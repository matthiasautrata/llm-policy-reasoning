///
/// V3d evaluator: the same defeasible logic as V3a defeasible.pl, V3b engine.clj, V3c engine.ex, over the
/// typed model (Model.Term / Goal / Lit) — an own evaluator (PLAN-v3cd Q1 route (iii)); see probes/ for
/// how far Flix's native Datalog carries the rules.
///
/// Search is continuation-passing with early stop: a body calls k(s, nodes) per solution; k returns true
/// to stop (V3b lazy seqs, V3c Streams). Everything the engine needs from outside (concept rows, the
/// per-op memo, fresh names, failure) is the effect Eval; Sql.withEval handles it per op.
///
/// evaluate decides a ground goal:
///   Proven(sups, supNodes)        every applicable attacker is beaten by some applicable supporter
///   Defeated(att, sups, nodes)    an unbeaten attacker is superior to every supporter
///   Blocked(sups, unbeaten)       ambiguity blocking
///   NoneEv(atts)                  no applicable supporter
///
pub mod Engine {

    use Model.{Value, ArOp, Term, Goal, CmpOp, Lit, Kind, Owner, Rule, Claim, Form}
    use Model.Value.{VStr, VInt, VBool, VNull}
    use Model.Term.{Var, Val, Ar}
    use Model.Goal.{Pos, Neg}
    use Util.Json.Json
    use Util.Json.Json.{JArray, JBool, JNull, JNumber, JObject, JString}

    // ------------------------------------------------------------------ types

    pub type alias Subst = Map[String, Term]

    pub type alias Row = Map[String, Value]

    pub type alias FetchOut = {rows = List[Row], sql = String, params = List[Value], truncated = Bool}

    pub enum Node {
        /// id, goal, children, failed (why-not only)
        case NRule(String, Goal, List[Node], Option[Node])
        /// id, goal, asserted_by, asserted_at, children
        case NClaim(String, Goal, Owner, String, List[Node])
        /// concept, filters, row count, row, sql, params, truncated
        case NFetch(String, List[(String, Value)], Int32, Option[Row], String, List[Value], Bool)
        /// goal, holds (Some(false) when a builtin failed)
        case NFact(Json, Option[Bool])
        /// goal, children
        case NAbsent(Json, Option[List[Node]])
        /// attacker id, target id, children, blocked
        case NDefeated(String, String, List[Node], Bool)
        /// winner, loser, source
        case NSuperior(String, String, String)
    }

    pub type alias Sup = {id = String, proof = Node}

    pub enum Ev {
        case Proven(List[Sup], List[Node])
        case Defeated(Sup, List[Sup], List[Node])
        case Blocked(List[Sup], List[Sup])
        case NoneEv(List[Sup])
    }

    /// what the evaluator asks of the world
    pub eff Eval {
        def fetch(concept: String, filters: List[(String, Value)]): FetchOut
        def memoGet(key: (String, Goal)): Option[Ev]
        def memoPut(key: (String, Goal), ev: Ev): Unit
        def fresh(): Int64
        def fail(msg: String): Void
    }

    /// a logic rule as the engine reads it
    pub type alias LR = {id = String, kind = Kind, head = Goal, body = List[Lit]}

    pub type alias Ctx = {d = String, logic = List[LR], claims = List[Claim], ruleBy = Map[String, Rule],
                          claimBy = Map[String, Claim], functional = Map[String, Int32],
                          orders = List[(String, String, List[Owner])], path = List[(String, Goal)]}

    pub def ctx(d: String, rules: List[Rule], claims: List[Claim], functional: Map[String, Int32]): Ctx =
        {d = d,
         logic = List.filterMap(r -> match r#form {
             case Form.Logic(k, h, b) => Some({id = r#id, kind = k, head = h, body = b})
             case _ => None
         }, rules),
         claims = claims,
         ruleBy = List.toMap(List.map(r -> (r#id, r), rules)),
         claimBy = List.toMap(List.map(c -> (c#id, c), claims)),
         functional = functional,
         orders = List.filterMap(r -> match r#form {
             case Form.Order(p, os) => Some((r#id, p, os))
             case _ => None
         }, rules),
         path = Nil}

    // ------------------------------------------------------------------ terms

    pub def walk(t: Term, s: Subst): Term = match t {
        case Var(n) => match Map.get(n, s) {
            case Some(v) => walk(v, s)
            case None => t
        }
        case _ => t
    }

    pub def unify(a0: Term, b0: Term, s: Subst): Option[Subst] =
        let a = walk(a0, s);
        let b = walk(b0, s);
        match (a, b) {
            case (Var(x), Var(y)) if x == y => Some(s)
            case (Var(x), _) => Some(Map.insert(x, b, s))
            case (_, Var(y)) => Some(Map.insert(y, a, s))
            case (Ar(o1, x1, y1), Ar(o2, x2, y2)) if o1 == o2 => unify(x1, x2, s) |> Option.flatMap(unify(y1, y2))
            case (Val(x), Val(y)) => if (x == y) Some(s) else None
            case _ => None
        }

    def unifyAll(xs: List[Term], ys: List[Term], s: Subst): Option[Subst] = match (xs, ys) {
        case (Nil, Nil) => Some(s)
        case (x :: xr, y :: yr) => unify(x, y, s) |> Option.flatMap(unifyAll(xr, yr))
        case _ => None
    }

    pub def unifyG(a: Goal, b: Goal, s: Subst): Option[Subst] = match (a, b) {
        case (Pos(p, xs), Pos(q, ys)) if p == q => unifyAll(xs, ys, s)
        case (Neg(x), Neg(y)) => unifyG(x, y, s)
        case _ => None
    }

    pub def substT(t: Term, s: Subst): Term = match walk(t, s) {
        case Ar(o, a, b) => Ar(o, substT(a, s), substT(b, s))
        case x => x
    }

    pub def substG(g: Goal, s: Subst): Goal = match g {
        case Pos(p, ts) => Pos(p, List.map(t -> substT(t, s), ts))
        case Neg(h) => Neg(substG(h, s))
    }

    pub def groundT(t: Term): Bool = match t {
        case Var(_) => false
        case Val(_) => true
        case Ar(_, a, b) => groundT(a) and groundT(b)
    }

    pub def groundG(g: Goal): Bool = match g {
        case Pos(_, ts) => List.forAll(groundT, ts)
        case Neg(h) => groundG(h)
    }

    def renT(sfx: String, t: Term): Term = match t {
        case Var(n) => Var(n + sfx)
        case Ar(o, a, b) => Ar(o, renT(sfx, a), renT(sfx, b))
        case x => x
    }

    def renG(sfx: String, g: Goal): Goal = match g {
        case Pos(p, ts) => Pos(p, List.map(renT(sfx), ts))
        case Neg(h) => Neg(renG(sfx, h))
    }

    def renL(sfx: String, l: Lit): Lit = match l {
        case Lit.Derived(g) => Lit.Derived(renG(sfx, g))
        case Lit.Fetch(c, fs, os) => Lit.Fetch(c, List.map(match (k, t) -> (k, renT(sfx, t)), fs), List.map(match (k, v) -> (k, v + sfx), os))
        case Lit.Not(g) => Lit.Not(renG(sfx, g))
        case Lit.Cmp(o, a, b) => Lit.Cmp(o, renT(sfx, a), renT(sfx, b))
        case Lit.Is(x, o, a, b) => Lit.Is(x + sfx, o, renT(sfx, a), renT(sfx, b))
        case Lit.AsOf(t) => Lit.AsOf(renT(sfx, t))
    }

    /// fresh variables for one use of a rule
    def rename(r: LR): (Goal, List[Lit]) \ Eval =
        let sfx = "#${Eval.fresh()}";
        (renG(sfx, r#head), List.map(renL(sfx), r#body))

    // the standard order of V3b/V3c: variables < numbers < atoms (booleans, nil) < strings < lists
    def rank(t: Term): Int32 = match t {
        case Var(_) => 0
        case Val(VInt(_)) => 1
        case Val(VBool(_)) => 2
        case Val(VNull) => 2
        case Val(VStr(_)) => 3
        case Ar(_, _, _) => 4
    }

    def atomStr(t: Term): String = match t {
        case Val(VBool(b)) => if (b) "true" else "false"
        case _ => ""
    }

    def opStr(o: ArOp): String = match o {
        case ArOp.Plus => "+"
        case ArOp.Minus => "-"
    }

    def cmpI(a: a, b: a): Int32 with Order[a] = match Order.compare(a, b) {
        case Comparison.LessThan => -1
        case Comparison.EqualTo => 0
        case Comparison.GreaterThan => 1
    }

    pub def tcmp(a: Term, b: Term): Int32 =
        let (ra, rb) = (rank(a), rank(b));
        if (ra != rb) cmpI(ra, rb)
        else match (a, b) {
            case (Var(x), Var(y)) => cmpI(x, y)
            case (Val(VInt(x)), Val(VInt(y))) => cmpI(x, y)
            case (Val(VStr(x)), Val(VStr(y))) => cmpI(x, y)
            case (Ar(o1, x1, y1), Ar(o2, x2, y2)) =>
                let c = cmpI(":" + opStr(o1), ":" + opStr(o2));
                if (c != 0) c else lcmp(x1 :: y1 :: Nil, x2 :: y2 :: Nil)
            case _ => cmpI(atomStr(a), atomStr(b))
        }

    pub def lcmp(xs: List[Term], ys: List[Term]): Int32 = match (xs, ys) {
        case (Nil, Nil) => 0
        case (Nil, _) => -1
        case (_, Nil) => 1
        case (x :: xr, y :: yr) => let c = tcmp(x, y); if (c != 0) c else lcmp(xr, yr)
    }

    pub def gcmp(a: Goal, b: Goal): Int32 = match (a, b) {
        case (Pos(p, xs), Pos(q, ys)) => let c = cmpI(":" + p, ":" + q); if (c != 0) c else lcmp(xs, ys)
        case (Neg(x), Neg(y)) => gcmp(x, y)
        case (Pos(p, _), Neg(_)) => cmpI(":" + p, ":neg")
        case (Neg(_), Pos(q, _)) => cmpI(":neg", ":" + q)
    }

    def toCmp(i: Int32): Comparison = if (i < 0) Comparison.LessThan else if (i > 0) Comparison.GreaterThan else Comparison.EqualTo

    pub def sortGoals(gs: List[Goal]): List[Goal] = List.sortWith((x, y) -> toCmp(gcmp(x, y)), List.distinct(gs))

    pub def sortValues(vs: List[List[Term]]): List[List[Term]] = List.sortWith((x, y) -> toCmp(lcmp(x, y)), List.distinct(vs))

    pub def predOf(g: Goal): String = Model.predOf(g)

    // ------------------------------------------------------------------ JSON of terms and nodes

    pub def jint(i: Int64): Json = JNumber(Int64.toBigDecimal(i))

    pub def valueJson(v: Value): Json = match v {
        case VStr(s) => JString(s)
        case VInt(i) => jint(i)
        case VBool(b) => JBool(b)
        case VNull => JNull
    }

    def stripVar(n: String): String = match String.indexOf(substr = "#", n) {
        case Some(i) => String.slice(start = 0, end = i, n)
        case None => n
    }

    pub def jarr(xs: List[Json]): Json = JArray(List.toVector(xs))

    pub def obj(kvs: List[(String, Json)]): Json = JObject(List.toMap(kvs))

    pub def termJson(t: Term): Json = match t {
        case Var(n) => JString(stripVar(n))
        case Val(v) => valueJson(v)
        case Ar(o, a, b) => jarr(JString(opStr(o)) :: termJson(a) :: termJson(b) :: Nil)
    }

    pub def goalJson(g: Goal): Json = match g {
        case Pos(p, ts) => jarr(JString(p) :: List.map(termJson, ts))
        case Neg(h) => jarr(JString("neg") :: goalJson(h) :: Nil)
    }

    pub def rowJson(r: Row): Json = JObject(Map.map(valueJson, r))

    def cmpName(o: CmpOp): String = match o {
        case CmpOp.Lt => "<"
        case CmpOp.Le => "<="
        case CmpOp.Gt => ">"
        case CmpOp.Ge => ">="
        case CmpOp.Equ => "="
    }

    pub def ownerName(o: Owner): String = match o {
        case Owner.Finance => "finance"
        case Owner.Hr => "hr"
        case Owner.Procurement => "procurement"
        case Owner.Compliance => "compliance"
        case Owner.Risk => "risk"
        case Owner.Controller => "controller"
    }

    def litJson(l: Lit): Json = match l {
        case Lit.Cmp(o, a, b) => jarr(JString(cmpName(o)) :: termJson(a) :: termJson(b) :: Nil)
        case Lit.Is(x, o, a, b) => jarr(JString("is") :: JString(stripVar(x)) :: termJson(Ar(o, a, b)) :: Nil)
        case Lit.AsOf(t) => jarr(JString("as_of") :: termJson(t) :: Nil)
        case Lit.Derived(g) => goalJson(g)
        case Lit.Not(g) => jarr(JString("not") :: goalJson(g) :: Nil)
        case Lit.Fetch(c, _, _) => jarr(JString("fetch") :: JString(c) :: Nil)
    }

    pub def nodeJson(n: Node): Json = match n {
        case Node.NRule(id, g, ks, f) =>
            obj(("type", JString("rule")) :: ("id", JString(id)) :: ("goal", goalJson(g)) :: ("children", jarr(List.map(nodeJson, ks))) ::
                (match f { case Some(x) => ("failed", nodeJson(x)) :: Nil case None => Nil }))
        case Node.NClaim(id, g, by, at, ks) =>
            obj(("type", JString("claim")) :: ("id", JString(id)) :: ("goal", goalJson(g)) :: ("asserted_by", JString(ownerName(by))) ::
                ("asserted_at", JString(at)) :: ("children", jarr(List.map(nodeJson, ks))) :: Nil)
        case Node.NFetch(c, fs, n0, row, sql, ps, tr) =>
            obj(("type", JString("fetch")) :: ("concept", JString(c)) :: ("filters", JObject(List.toMap(List.map(match (k, v) -> (k, valueJson(v)), fs)))) ::
                ("rows", JNumber(Int32.toBigDecimal(n0))) :: ("row", match row { case Some(r) => rowJson(r) case None => JNull }) ::
                ("sql", JString(sql)) :: ("params", jarr(List.map(valueJson, ps))) :: ("truncated", JBool(tr)) :: Nil)
        case Node.NFact(g, h) =>
            obj(("type", JString("fact")) :: ("goal", g) :: (match h { case Some(b) => ("holds", JBool(b)) :: Nil case None => Nil }))
        case Node.NAbsent(g, ks) =>
            obj(("type", JString("absent")) :: ("goal", g) :: (match ks { case Some(xs) => ("children", jarr(List.map(nodeJson, xs))) :: Nil case None => Nil }))
        case Node.NDefeated(id, t, ks, bl) =>
            obj(("type", JString("defeated_by")) :: ("id", JString(id)) :: ("target", JString(t)) :: ("children", jarr(List.map(nodeJson, ks))) ::
                (if (bl) ("blocked", JBool(true)) :: Nil else Nil))
        case Node.NSuperior(w, l, src) =>
            obj(("type", JString("superior")) :: ("winner", JString(w)) :: ("loser", JString(l)) :: ("source", JString(src)) :: Nil)
    }

    // ------------------------------------------------------------------ store access

    pub def inForce(c: Claim, d: String): Bool =
        c#validFrom <= d and (match c#validTo { case None => true case Some(t) => d <= t })

    def logicOf(c: Ctx, ks: List[Kind]): List[LR] = List.filter(r -> List.memberOf(r#kind, ks), c#logic)

    pub def derivers(): List[Kind] = Kind.Strict :: Kind.Defeasible :: Nil

    def attacking(): List[Kind] = Kind.Strict :: Kind.Defeasible :: Kind.Defeater :: Nil

    pub def claimProof(c: Claim, g: Goal): Node = Node.NClaim(c#id, g, c#assertedBy, c#assertedAt, Nil)

    pub def withChildren(n: Node, extra: List[Node]): Node = match n {
        case Node.NRule(id, g, ks, f) => Node.NRule(id, g, ks ++ extra, f)
        case Node.NClaim(id, g, by, at, ks) => Node.NClaim(id, g, by, at, ks ++ extra)
        case _ => n
    }

    // ------------------------------------------------------------------ bodies

    def evT(t0: Term, s: Subst): Value \ Eval = match walk(t0, s) {
        case Ar(o, a, b) => match (evT(a, s), evT(b, s)) {
            case (VInt(x), VInt(y)) => VInt(if (o == ArOp.Plus) x + y else x - y)
            case (x, y) => Eval.fail("ArgumentError: arithmetic on ${x}, ${y}")
        }
        case Var(n) => Eval.fail("ArgumentError: unbound ${stripVar(n)}")
        case Val(v) => v
    }

    pub def cmpHolds(o: CmpOp, a: Term, b: Term): Bool \ Eval =
        let (x, y) = (evT(a, Map.empty()), evT(b, Map.empty()));
        let c = match (x, y) {
            case (VInt(i), VInt(j)) => cmpI(i, j)
            case _ => tcmp(Val(x), Val(y))
        };
        match o {
            case CmpOp.Lt => c < 0
            case CmpOp.Le => c <= 0
            case CmpOp.Gt => c > 0
            case CmpOp.Ge => c >= 0
            case CmpOp.Equ => c == 0
        }

    /// a concept lookup with ground filters -> rows and the node for them (row filled in per row)
    pub def fetchRows(cn: String, fs: List[(String, Term)]): (List[Row], Option[Row] -> Node) \ Eval =
        let vs = List.map(match (k, t) -> if (groundT(t)) (k, evT(t, Map.empty())) else Eval.fail("ArgumentError: fetch ${cn}: filters not ground"), fs)
                 |> List.sortBy(fst);
        let out = Eval.fetch(cn, vs);
        let n = List.length(out#rows);
        (out#rows, row -> Node.NFetch(cn, vs, n, row, out#sql, out#params, out#truncated))

    def bindRow(row: Row, os: List[(String, String)], s: Subst): Option[Subst] = match os {
        case Nil => Some(s)
        case (col, v) :: rest => match Map.get(col, row) {
            case Some(x) => unify(Var(v), Val(x), s) |> Option.flatMap(bindRow(row, rest))
            case None => None
        }
    }

    def eachRow(rows: List[Row], os: List[(String, String)], s: Subst, mk: Option[Row] -> Node, k: (Subst, Node) -> Bool \ ef): Bool \ ef =
        match rows {
            case Nil => false
            case row :: rest => match bindRow(row, os, s) {
                case Some(s2) => if (k(s2, mk(Some(row)))) true else eachRow(rest, os, s, mk, k)
                case None => eachRow(rest, os, s, mk, k)
            }
        }

    /// one body literal under s: k(s', node) per solution, until k says stop
    pub def lit(c: Ctx, l: Lit, s: Subst, k: (Subst, Node) -> Bool \ ef): Bool \ ef + Eval = match l {
        case Lit.Fetch(cn, fs, os) =>
            let (rows, mk) = fetchRows(cn, List.map(match (f, t) -> (f, substT(t, s)), fs));
            eachRow(rows, os, s, mk, k)
        case Lit.Not(g) =>
            let g1 = substG(g, s);
            if (provable(c, g1)) false else k(s, Node.NAbsent(goalJson(g1), None))
        case Lit.AsOf(t) => match unify(t, Val(VStr(c#d)), s) {
            case Some(s2) => k(s2, Node.NFact(jarr(JString("as_of") :: JString(c#d) :: Nil), None))
            case None => false
        }
        case Lit.Is(x, o, a, b) =>
            let v = evT(Ar(o, a, b), s);
            match unify(Var(x), Val(v), s) {
                case Some(s2) => k(s2, Node.NFact(jarr(JString("is") :: valueJson(v) :: termJson(substT(Ar(o, a, b), s)) :: Nil), None))
                case None => false
            }
        case Lit.Cmp(o, a, b) =>
            let (x, y) = (substT(a, s), substT(b, s));
            if (cmpHolds(o, x, y)) k(s, Node.NFact(litJson(Lit.Cmp(o, x, y)), None)) else false
        case Lit.Derived(g) =>
            prove(c, substG(g, s), (inst, p) -> match unifyG(g, inst, s) {
                case Some(s2) => k(s2, p)
                case None => false
            })
    }

    pub def body(c: Ctx, ls: List[Lit], s: Subst, k: (Subst, List[Node]) -> Bool \ ef): Bool \ ef + Eval = match ls {
        case Nil => k(s, Nil)
        case l :: rest => lit(c, l, s, (s1, n) -> body(c, rest, s1, (s2, ns) -> k(s2, n :: ns)))
    }

    /// rule r concluding goal g: k(s, proof node) per solution
    pub def applyRule(c: Ctx, r: LR, g: Goal, k: (Subst, Node) -> Bool \ ef): Bool \ ef + Eval =
        let (h, b) = rename(r);
        match unifyG(h, g, Map.empty()) {
            case Some(s) => body(c, b, s, (s2, kids) -> k(s2, Node.NRule(r#id, substG(g, s2), kids, None)))
            case None => false
        }

    /// the first solution of applyRule satisfying p
    pub def firstRule(c: Ctx, r: LR, g: Goal, p: Subst -> Bool): Option[(Subst, Node)] \ Eval = region rc {
        let out = Ref.fresh(rc, None);
        discard applyRule(c, r, g, (s, n) -> if (p(s)) { Ref.put(Some((s, n)), out); true } else false);
        Ref.get(out)
    }

    /// all solutions of applyRule, as proof nodes
    pub def allRule(c: Ctx, r: LR, g: Goal): List[(Subst, Node)] \ Eval = region rc {
        let out = Ref.fresh(rc, Nil);
        discard applyRule(c, r, g, (s, n) -> { Ref.put((s, n) :: Ref.get(out), out); false });
        List.reverse(Ref.get(out))
    }

    // ------------------------------------------------------------------ evaluation

    def candidates(c: Ctx, l: Goal): List[Goal] \ Eval =
        List.flatMap(r -> List.map(match (s, _) -> substG(l, s), allRule(c, r, l)), logicOf(c, derivers())) ++
        List.filterMap(cl -> if (inForce(cl, c#d)) unifyG(l, cl#assertion, Map.empty()) |> Option.map(substG(l)) else None, c#claims)

    def proofOf(c: Ctx, g: Goal): Option[Node] \ Eval = match evaluate(c, g) {
        case Ev.Proven(s1 :: _, sn) => Some(withChildren(s1#proof, sn))
        case _ => None
    }

    def eachProof(c: Ctx, gs: List[Goal], k: (Goal, Node) -> Bool \ ef): Bool \ ef + Eval = match gs {
        case Nil => false
        case g :: rest => match proofOf(c, g) {
            case Some(p) => if (k(g, p)) true else eachProof(c, rest, k)
            case None => eachProof(c, rest, k)
        }
    }

    /// l defeasibly provable: k(ground instance, proof) per instance, until k says stop
    pub def prove(c: Ctx, l: Goal, k: (Goal, Node) -> Bool \ ef): Bool \ ef + Eval =
        if (groundG(l)) eachProof(c, l :: Nil, k)
        else eachProof(c, sortGoals(List.filter(groundG, candidates(c, l))), k)

    pub def provable(c: Ctx, l: Goal): Bool \ Eval = prove(c, l, (_, _) -> true)

    pub def firstProof(c: Ctx, l: Goal): Option[(Goal, Node)] \ Eval = region rc {
        let out = Ref.fresh(rc, None);
        discard prove(c, l, (g, p) -> { Ref.put(Some((g, p)), out); true });
        Ref.get(out)
    }

    def supporters(c: Ctx, l: Goal): List[Sup] \ Eval =
        List.filterMap(r -> firstRule(c, r, l, _ -> true) |> Option.map(match (_, p) -> {id = r#id, proof = p}), logicOf(c, derivers())) ++
        List.filterMap(cl -> if (cl#assertion == l and inForce(cl, c#d)) Some({id = cl#id, proof = claimProof(cl, l)}) else None, c#claims)

    /// (head, diff): diff None, or (v, v2) for a functional rival with the key fixed and value v2 /= v
    def rivals(c: Ctx, l: Goal): List[(Goal, Option[(Term, Term)])] \ Eval = match l {
        case Neg(h) => (h, None) :: Nil
        case Pos(p, args) =>
            let base = (Neg(l), None) :: Nil;
            match Map.get(p, c#functional) {
                case Some(n) if List.length(args) == n + 1 =>
                    let v2 = Var("?rival#${Eval.fresh()}");
                    base ++ ((Pos(p, List.take(n, args) ++ (v2 :: Nil)), List.last(args) |> Option.map(v -> (v, v2))) :: Nil)
                case _ => base
            }
    }

    def differs(diff: Option[(Term, Term)], s: Subst): Bool = match diff {
        case None => true
        case Some((v, v2)) => v != substT(v2, s)
    }

    def attackers(c: Ctx, l: Goal): List[Sup] \ Eval =
        let atts = List.flatMap(match (h, diff) ->
            List.filterMap(r -> firstRule(c, r, h, differs(diff)) |> Option.map(match (_, p) -> {id = r#id, proof = p}), logicOf(c, attacking())) ++
            List.filterMap(cl -> if (inForce(cl, c#d)) match unifyG(h, cl#assertion, Map.empty()) {
                    case Some(s) if differs(diff, s) => Some({id = cl#id, proof = claimProof(cl, cl#assertion)})
                    case _ => None
                } else None, c#claims), rivals(c, l));
        uniqById(atts, Set.empty(), Nil)

    def uniqById(xs: List[Sup], seen: Set[String], acc: List[Sup]): List[Sup] = match xs {
        case Nil => List.reverse(acc)
        case x :: rest => if (Set.memberOf(x#id, seen)) uniqById(rest, seen, acc) else uniqById(rest, Set.insert(x#id, seen), x :: acc)
    }

    def kindOf(r: Rule): Option[Kind] = match r#form {
        case Form.Logic(k, _, _) => Some(k)
        case _ => None
    }

    /// sources by which w is superior to l, in order: explicit, strict, authority:<id>, later
    pub def sup(c: Ctx, w: String, l: String): List[String] =
        let (rw, rl, cw, cl) = (Map.get(w, c#ruleBy), Map.get(l, c#ruleBy), Map.get(w, c#claimBy), Map.get(l, c#claimBy));
        let explicit = match rw { case Some(r) if List.memberOf(l, r#superiorTo) => "explicit" :: Nil case _ => Nil };
        let strict = match rw {
            case Some(r) if kindOf(r) == Some(Kind.Strict) and not (Option.flatMap(kindOf, rl) == Some(Kind.Strict)) => "strict" :: Nil
            case _ => Nil
        };
        let (authority, later) = match (cw, cl) {
            case (Some(a), Some(b)) =>
                let p = predOf(a#assertion);
                let au = if (a#assertedBy != b#assertedBy and p == predOf(b#assertion))
                    List.filterMap(match (id, q, ord) ->
                        if (q != p) None
                        else match (List.indexOf(a#assertedBy, ord), List.indexOf(b#assertedBy, ord)) {
                            case (Some(iw), Some(il)) if iw < il => Some("authority:" + id)
                            case _ => None
                        }, c#orders)
                    else Nil;
                (au, if (a#assertedBy == b#assertedBy and a#assertedAt > b#assertedAt) "later" :: Nil else Nil)
            case _ => (Nil, Nil)
        };
        explicit ++ strict ++ authority ++ later

    def sup1(c: Ctx, w: String, l: String): Option[String] = List.head(sup(c, w, l))

    def classify(c: Ctx, sups: List[Sup], atts: List[Sup]): Ev =
        if (List.isEmpty(sups)) Ev.NoneEv(atts)
        else {
            let beater = a -> List.find(s -> Option.nonEmpty(sup1(c, s#id, a#id)), sups);
            let (beaten, unbeaten) = List.partition(a -> Option.nonEmpty(beater(a)), atts);
            let sn = List.filterMap(a -> beater(a) |> Option.map(s ->
                Node.NSuperior(s#id, a#id, Option.getWithDefault("", sup1(c, s#id, a#id)))), beaten);
            if (List.isEmpty(unbeaten)) Ev.Proven(sups, sn)
            else match List.find(a -> List.forAll(s -> Option.nonEmpty(sup1(c, a#id, s#id)), sups), unbeaten) {
                case Some(a) => Ev.Defeated(a, sups, List.map(s -> Node.NSuperior(a#id, s#id, Option.getWithDefault("", sup1(c, a#id, s#id))), sups))
                case None => Ev.Blocked(sups, unbeaten)
            }
        }

    /// Memoised per op. Re-entry guard (PLAN-v3-integrity §3.2): the ctx carries the path of goals being
    /// evaluated; meeting one again is a dependency cycle the integrity gate did not stop
    /// (INTEGRITY_GATE=off). Fails with cycleTag + the violation JSON, a backstop, not a semantics.
    pub def evaluate(c0: Ctx, l: Goal): Ev \ Eval =
        let key = (c0#d, l);
        match Eval.memoGet(key) {
            case Some(r) => r
            case None =>
                match List.indexOf(key, c0#path) {
                    case Some(i) => { let gs = List.map(snd, List.drop(i, c0#path)) ++ (l :: Nil); discard Eval.fail(cycleTag() + Util.Json.toCompactString(cycleJson(gs))) }
                    case None => ()
                };
                let c = {path = c0#path ++ (key :: Nil) | c0};
                let r = classify(c, supporters(c, l), attackers(c, l));
                Eval.memoPut(key, r);
                r
        }

    pub def cycleTag(): String = "\u0001defeat-cycle\u0001"

    def termEdn(t: Term): String = match t {
        case Val(VStr(s)) => "\"${s}\""
        case Val(VInt(i)) => "${i}"
        case Val(VBool(b)) => "${b}"
        case Val(VNull) => "nil"
        case Var(n) => n
        case other => "${other}"
    }

    pub def goalEdn(g: Goal): String = match g {
        case Pos(p, ts) => "[" + String.intercalate(" ", (":" + p) :: List.map(termEdn, ts)) + "]"
        case Neg(h) => "[:neg ${goalEdn(h)}]"
    }

    def cycleJson(gs: List[Goal]): Json =
        let ms = List.map(goalEdn, gs);
        obj(("violation", JString("defeat-cycle")) :: ("members", jarr(List.map(JString, ms))) ::
            ("path", jarr(List.map(goalJson, gs))) :: ("message", JString("re-entered " + Option.getWithDefault("", List.head(ms)))) :: Nil)

    pub def idsOf(xs: List[Sup]): List[String] = List.sort(List.distinct(List.map(x -> x#id, xs)))

    // ------------------------------------------------------------------ why not (V3a why.pl, V3b why.clj, V3c why.ex)

    pub def defeatNode(c: Ctx, id: String, ev: Ev): Option[Node] = match ev {
        case Ev.Defeated(a, _, _) =>
            let sn = match sup(c, a#id, id) { case src :: _ => Node.NSuperior(a#id, id, src) :: Nil case Nil => Nil };
            Some(Node.NDefeated(a#id, id, a#proof :: sn, false))
        case Ev.Blocked(_, a :: _) => Some(Node.NDefeated(a#id, id, a#proof :: Nil, true))
        case _ => None
    }

    def failedLit(c: Ctx, l: Lit, s: Subst): Node \ Eval = match l {
        case Lit.Fetch(cn, fs, _) =>
            let f2 = List.map(match (f, t) -> (f, substT(t, s)), fs);
            if (List.forAll(match (_, t) -> groundT(t), f2)) {
                let (_, mk) = fetchRows(cn, f2);
                mk(None)
            } else Node.NAbsent(litJson(l), None)
        case Lit.Not(g) =>
            let g1 = substG(g, s);
            let kids = match firstProof(c, g1) { case Some((_, p)) => p :: Nil case None => Nil };
            Node.NAbsent(jarr(JString("not") :: goalJson(g1) :: Nil), Some(kids))
        case Lit.Derived(g) => explainNot(c, substG(g, s))
        case Lit.Cmp(o, a, b) => Node.NFact(litJson(Lit.Cmp(o, substT(a, s), substT(b, s))), Some(false))
        case Lit.Is(x, o, a, b) => Node.NFact(jarr(JString("is") :: termJson(substT(Var(x), s)) :: termJson(substT(Ar(o, a, b), s)) :: Nil), Some(false))
        case Lit.AsOf(t) => Node.NFact(jarr(JString("as_of") :: termJson(substT(t, s)) :: Nil), Some(false))
    }

    def firstLit(c: Ctx, l: Lit, s: Subst): Option[(Subst, Node)] \ Eval = region rc {
        let out = Ref.fresh(rc, None);
        discard lit(c, l, s, (s2, n) -> { Ref.put(Some((s2, n)), out); true });
        Ref.get(out)
    }

    /// first solution of each literal in turn -> (s, done, failed node)
    def walkBody(c: Ctx, ls: List[Lit], s: Subst, done: List[Node]): (Subst, List[Node], Option[Node]) \ Eval = match ls {
        case Nil => (s, List.reverse(done), None)
        case l :: rest => match firstLit(c, l, s) {
            case Some((s2, k)) => walkBody(c, rest, s2, k :: done)
            case None => (s, List.reverse(done), Some(failedLit(c, l, s)))
        }
    }

    def explainRule(c: Ctx, r: LR, g: Goal, ev: Ev): Option[Node] \ Eval =
        let (h, b) = rename(r);
        match unifyG(h, g, Map.empty()) {
            case None => None
            case Some(s) =>
                let (s2, done, failed) = walkBody(c, b, s, Nil);
                let f = match failed { case Some(x) => Some(x) case None => defeatNode(c, r#id, ev) };
                Some(Node.NRule(r#id, substG(g, s2), done, f))
        }

    pub def explainNot(c: Ctx, g: Goal): Node \ Eval =
        let ground = groundG(g);
        let ev = if (ground) evaluate(c, g) else Ev.NoneEv(Nil);
        let rs = List.filterMap(r -> explainRule(c, r, g, ev), logicOf(c, derivers()));
        let defeated = match ev { case Ev.Proven(_, _) => false case Ev.NoneEv(_) => false case _ => true };
        let cs = if (ground and defeated)
            List.filterMap(cl -> if (cl#assertion == g and inForce(cl, c#d))
                    defeatNode(c, cl#id, ev) |> Option.map(dn -> Node.NClaim(cl#id, g, cl#assertedBy, cl#assertedAt, dn :: Nil))
                else None, c#claims)
            else Nil;
        Node.NAbsent(goalJson(g), Some(rs ++ cs))
}
