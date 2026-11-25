///
/// V3d System A surface (CONTRACT.md): decide, why_not, claims, resolve_term, describe, fetch, add,
/// with_hypothesis (+ the test op sleep). Each op runs against one store value: main's (read from the
/// session Ref when the op starts) or a hypothesis's (passed down explicitly). Same semantics as V3c ops.ex.
///
pub mod Ops {
    import java.lang.{System => JSys}
    import java.lang.{Thread => JThread}
    import java.sql.{Connection => JConn}

    use Model.{Value, Term, Goal, Kind, Claim, Role, Form}
    use Model.Value.{VStr, VInt, VBool, VNull}
    use Model.Term.{Var, Val}
    use Model.Goal.{Pos, Neg}
    use Engine.{Ctx, Ev, Node, Sup, LR, obj, jarr, jint, goalJson, termJson, nodeJson, valueJson, idsOf}
    use Store.Store
    use Util.Json.Json
    use Util.Json.Json.{JArray, JBool, JNull, JNumber, JObject, JString}

    // ------------------------------------------------------------------ JSON helpers

    pub def get(k: String, j: Json): Option[Json] = match j {
        case JObject(m) => Map.get(k, m)
        case _ => None
    }

    pub def getStr(k: String, j: Json): Option[String] = match get(k, j) {
        case Some(JString(s)) => Some(s)
        case _ => None
    }

    pub def getList(k: String, j: Json): List[Json] = match get(k, j) {
        case Some(JArray(v)) => Vector.toList(v)
        case _ => Nil
    }

    def jstr(s: String): Json = JString(s)

    def jopt(o: Option[String]): Json = match o { case Some(s) => JString(s) case None => JNull }

    def jstrs(xs: List[String]): Json = jarr(List.map(jstr, xs))

    pub def jfloat(x: Float64): Json = match BigDecimal.fromString(Float64.toString(x)) {
        case Some(b) => JNumber(b)
        case None => JNull
    }

    pub def merge(j: Json, kvs: List[(String, Json)]): Json = match j {
        case JObject(m) => JObject(List.foldLeft((acc, kv) -> Map.insert(fst(kv), snd(kv), acc), m, kvs))
        case _ => j
    }

    def jsonValue(j: Json): Value = match j {
        case JString(s) => VStr(s)
        case JBool(b) => VBool(b)
        case JNumber(n) => match BigDecimal.tryToInt64(n) { case Some(i) => VInt(i) case None => VStr(BigDecimal.toPlainString(n)) }
        case _ => VNull
    }

    // ------------------------------------------------------------------ env

    pub type alias Env = {cfg = Sql.Cfg, conn = JConn}

    def ctxOf(op: Json, db: Store): Ctx =
        Engine.ctx(Option.getWithDefault(db#meta#today, getStr("as_of", op)), db#rules, db#claims, db#meta#functional)

    def parseGoal(text: String): Goal \ Engine.Eval = match Edn.read(text) {
        case Err(e) => Engine.Eval.fail("ArgumentError: ${e}")
        case Ok(e) => match Model.goal("goal", e) {
            case Ok(g) => g
            case Err(m) => Engine.Eval.fail("ArgumentError: ${m}")
        }
    }

    // ------------------------------------------------------------------ decide

    def headOf(r: LR): Goal = r#head

    def knownPred(c: Ctx, p: String): Bool =
        List.exists(r -> Engine.predOf(headOf(r)) == p, c#logic) or List.exists(cl -> Engine.predOf(cl#assertion) == p, c#claims)

    def scope(db: Store, p: String): String =
        if (List.exists(t -> t#id == "term:" + p, db#meta#terms)) "UNDERDETERMINED" else "OUT_OF_SCOPE"

    def subIds(n: Node): List[String] = match n {
        case Node.NRule(id, _, ks, f) => id :: List.flatMap(subIds, ks) ++ (match f { case Some(x) => subIds(x) case None => Nil })
        case Node.NClaim(_, _, _, _, ks) => List.flatMap(subIds, ks)
        case Node.NDefeated(id, _, ks, _) => id :: List.flatMap(subIds, ks)
        case Node.NAbsent(_, Some(ks)) => List.flatMap(subIds, ks)
        case _ => Nil
    }

    def answer(c: Ctx, st: String, v: Json, sides: Option[List[List[String]]], why: List[Node]): Json =
        let owners = List.flatMap(subIds, why) |> List.filterMap(id -> Map.get(id, c#ruleBy) |> Option.map(r -> Engine.ownerName(r#owner)))
                     |> List.distinct |> List.sort;
        obj(("status", jstr(st)) :: ("value", v) :: ("sides", sidesJson(sides)) :: ("why", jarr(List.map(nodeJson, why))) ::
            ("owners", jstrs(owners)) :: ("qualifier", JNull) :: Nil)

    def sidesJson(s: Option[List[List[String]]]): Json = match s {
        case Some(xs) => jarr(List.map(jstrs, xs))
        case None => JNull
    }

    def isWinner(id: String, n: Node): Bool = match n {
        case Node.NSuperior(w, _, _) => w == id
        case _ => false
    }

    def teamProofs(sups: List[Sup], sn: List[Node]): List[Node] =
        List.map(s -> Engine.withChildren(s#proof, List.filter(isWinner(s#id), sn)), sups)

    // Erlang's list order (V3b's lexi): element-wise, then length; String order is the same
    def sides(xs: List[List[String]]): Option[List[List[String]]] = Some(List.sort(List.distinct(xs)))

    def incompatible(c: Ctx, g: Goal): Option[(String, Node)] \ Engine.Eval =
        List.filter(r -> r#kind == Kind.Incompatible, c#logic) |> List.findMap(r ->
            Engine.firstRule(c, r, g, _ -> true) |> Option.map(match (_, p) -> match p {
                case Node.NRule(id, _, ks, f) => (r#id, Node.NRule(id, Neg(g), ks, f))
                case _ => (r#id, p)
            }))

    def decideGround(c: Ctx, g: Goal): Json \ Engine.Eval = match Engine.evaluate(c, g) {
        case Ev.Proven(sups, sn) =>
            let why = teamProofs(sups, sn);
            match incompatible(c, g) {
                case Some((iid, inode)) => answer(c, "CONFLICT", JNull, sides(idsOf(sups) :: (iid :: Nil) :: Nil), why ++ (inode :: Nil))
                case None => answer(c, "ANSWER", JBool(true), None, why)
            }
        case Ev.Blocked(sups, un) =>
            answer(c, "CONFLICT", JNull, sides(idsOf(sups) :: idsOf(un) :: Nil), List.map(s -> s#proof, sups) ++ List.map(s -> s#proof, un))
        case _ => answer(c, "ANSWER", JBool(false), None, Engine.explainNot(c, g) :: Nil)
    }

    def varsT(t: Term): List[String] = match t {
        case Var(n) => n :: Nil
        case Term.Ar(_, a, b) => varsT(a) ++ varsT(b)
        case _ => Nil
    }

    def varsG(g: Goal): List[String] = match g {
        case Pos(_, ts) => List.flatMap(varsT, ts)
        case Neg(h) => varsG(h)
    }

    def supsOf(ev: Ev): List[Sup] = match ev {
        case Ev.Proven(s, _) => s
        case Ev.Blocked(s, _) => s
        case Ev.Defeated(_, s, _) => s
        case _ => Nil
    }

    def valueJ(v: List[Term]): Json = match v {
        case x :: Nil => termJson(x)
        case xs => jarr(List.map(termJson, xs))
    }

    def decideOpen(c: Ctx, g: Goal): Json \ Engine.Eval =
        let vs = List.distinct(varsG(g));
        let value = inst -> match Engine.unifyG(g, inst, Map.empty()) {
            case Some(s) => List.map(v -> Engine.substT(Var(v), s), vs)
            case None => Nil
        };
        let fromRules = List.filter(r -> List.memberOf(r#kind, Engine.derivers()), c#logic)
            |> List.flatMap(r -> Engine.allRule(c, r, g) |> List.filterMap(match (_, p) -> match p {
                case Node.NRule(_, gi, _, _) => Some(gi)
                case _ => None
            }));
        let fromClaims = List.filterMap(cl -> if (Engine.inForce(cl, c#d)) Engine.unifyG(g, cl#assertion, Map.empty()) |> Option.map(Engine.substG(g)) else None, c#claims);
        let cands = Engine.sortGoals(List.filter(Engine.groundG, fromRules ++ fromClaims));
        let ges = List.map(gi -> (gi, Engine.evaluate(c, gi)), cands);
        let won = List.filter(match (_, ev) -> match ev { case Ev.Proven(_, _) => true case _ => false }, ges);
        if (Map.memberOf(Engine.predOf(g), c#functional)) {
            match won {
                case (gi, Ev.Proven(sups, sn)) :: Nil => answer(c, "ANSWER", valueJ(value(gi)), None, teamProofs(sups, sn))
                case Nil if not List.isEmpty(ges) =>
                    answer(c, "CONFLICT", JNull,
                        sides(List.filterMap(match (_, ev) -> match supsOf(ev) { case Nil => None case ss => Some(idsOf(ss)) }, ges)),
                        List.flatMap(match (_, ev) -> List.map(s -> s#proof, supsOf(ev)), ges))
                case Nil => answer(c, "ANSWER", JNull, None, Engine.explainNot(c, g) :: Nil)
                case _ => merge(answer(c, "CONFLICT", JNull, None, Nil), ("value", jarr(List.map(match (gi, _) -> valueJ(value(gi)), won))) :: Nil)
            }
        } else {
            let vws = List.map(match (gi, ev) -> match ev {
                case Ev.Proven(sups, sn) => (value(gi), teamProofs(sups, sn))
                case _ => (value(gi), Nil)
            }, won);
            answer(c, "ANSWER", jarr(List.map(valueJ, Engine.sortValues(List.map(fst, vws)))), None, List.flatMap(snd, vws))
        }

    def decide(db: Store, c: Ctx, g: Goal): Json \ Engine.Eval =
        let p = Engine.predOf(g);
        if (not knownPred(c, p))
            obj(("status", jstr(scope(db, p))) :: ("value", JNull) :: ("sides", JNull) :: ("why", jarr(Nil)) :: ("owners", jarr(Nil)) :: ("qualifier", JNull) :: Nil)
        else if (Engine.groundG(g)) decideGround(c, g)
        else decideOpen(c, g)

    def whyNot(c: Ctx, g: Goal): Json \ Engine.Eval =
        let ev = if (Engine.groundG(g)) Engine.evaluate(c, g) else Ev.NoneEv(Nil);
        match ev {
            case Ev.Proven(sups, sn) =>
                obj(("status", jstr("ANSWER")) :: ("value", JBool(true)) :: ("why", jarr(List.map(nodeJson, teamProofs(sups, sn)))) :: ("why_not", jarr(Nil)) :: Nil)
            case _ =>
                obj(("status", jstr("ANSWER")) :: ("value", JBool(false)) :: ("why_not", jarr(nodeJson(Engine.explainNot(c, g)) :: Nil)) :: Nil)
        }

    // ------------------------------------------------------------------ claims

    /// standing, defeater, qualifier, sides, via
    type alias St = {standing = String, defeater = Option[String], qualifier = List[String], sides = Option[List[List[String]]], via = Option[String]}

    def st(s: String): St = {standing = s, defeater = None, qualifier = Nil, sides = None, via = None}

    def failing(s: St): Bool = s#standing != "holds" and s#standing != "holds_with_qualifier"

    def ownStanding(ev: Ev): St = match ev {
        case Ev.Defeated(a, _, _) => {defeater = Some(a#id) | st("rebutted")}
        case Ev.Blocked(sups, un) => {sides = sides(idsOf(sups) :: idsOf(un) :: Nil) | st("contested")}
        case _ => st("holds")
    }

    def subStanding(subs: List[(Claim, St, Json)]): St =
        match List.find(match (cl, s, _) -> cl#role == Some(Role.Required) and failing(s), subs) {
            case Some((cl, s, _)) => {defeater = s#defeater, via = Some(cl#id) | st("rebutted")}
            case None =>
                match List.filterMap(match (cl, s, _) -> if (cl#role == Some(Role.Supporting) and failing(s)) Some(cl#id) else None, subs) |> List.sort {
                    case Nil => st("holds")
                    case q => {qualifier = q | st("holds_with_qualifier")}
                }
        }

    def roleName(r: Role): String = match r { case Role.Required => "required" case Role.Supporting => "supporting" }

    def standing(c: Ctx, cl: Claim): (Claim, St, Json) \ Engine.Eval =
        let subs = List.filter(s -> s#parent == Some(cl#id), c#claims) |> List.map(s -> standing(c, s));
        let s = if (Engine.inForce(cl, c#d)) {
            let s0 = ownStanding(Engine.evaluate(c, cl#assertion));
            if (s0#standing == "holds") subStanding(subs) else s0
        } else st("not_in_force");
        let j = obj(("id", jstr(cl#id)) :: ("about", jstr(cl#about)) :: ("assertion", goalJson(cl#assertion)) ::
                    ("asserted_by", jstr(Engine.ownerName(cl#assertedBy))) :: ("asserted_at", jstr(cl#assertedAt)) ::
                    ("valid_from", jstr(cl#validFrom)) :: ("valid_to", jopt(cl#validTo)) :: ("backing", jopt(cl#backing)) ::
                    ("modal", jopt(cl#modal)) :: ("role", jopt(Option.map(roleName, cl#role))) ::
                    ("standing", jstr(s#standing)) :: ("defeater", jopt(s#defeater)) :: ("qualifier", jstrs(s#qualifier)) ::
                    ("sides", sidesJson(s#sides)) :: ("subclaims", jarr(List.map(match (_, _, x) -> x, subs))) ::
                    (match s#via { case Some(v) => ("via", jstr(v)) :: Nil case None => Nil }));
        (cl, s, j)

    // ------------------------------------------------------------------ vocabulary, metadata

    def resolveTerm(db: Store, text: String): Json =
        let ids = Store.termsMatching(db, Store.norm(text))
            |> List.flatMap(id -> match List.find(t -> t#id == id, db#meta#terms) {
                case Some(t) if not List.isEmpty(t#see) => t#see
                case _ => id :: Nil
            }) |> List.distinct |> List.sort;
        let n = List.length(ids);
        obj(("text", jstr(text)) :: ("status", jstr(if (n == 0) "none" else if (n == 1) "concept" else "several")) ::
            ("candidates", jarr(List.filterMap(id -> List.find(t -> t#id == id, db#meta#terms) |> Option.map(t ->
                obj(("term", jstr(id)) :: ("definition", jstr(t#definition)) :: ("owner", jstr(Engine.ownerName(t#owner))) :: Nil)), ids))) :: Nil)

    def describe(db: Store, a: String): Json =
        let m = db#meta;
        let found = match List.find(x -> x#id == a, m#assets) {
            case Some(x) => Some((x#kind, x#doc, JNull))
            case None => match List.find(x -> x#id == a, m#terms) {
                case Some(x) => Some(("term", x#definition, jopt(x#concept)))
                case None => match List.find(x -> x#id == a, m#concepts) {
                    case Some(x) => Some((x#kind, x#doc, obj(("concept", jstr(x#name)) :: ("tables", jstrs(x#tables)) :: ("params", jstrs(x#params)) ::
                        ("sql", match x#source { case Model.Source.Sql(s) => jstr(s) case _ => JNull }) :: Nil)))
                    case None => match List.find(x -> x#id == a, m#tables) {
                        case Some(x) => Some(("table", x#doc, JNull))
                        case None => List.find(x -> x#id == a, m#columns) |> Option.map(x -> ("column", x#doc, JNull))
                    }
                }
            }
        };
        let (st0, k, d, b) = match found {
            case Some((k, d, b)) => ("ANSWER", jstr(k), jstr(d), b)
            case None => ("OUT_OF_SCOPE", JNull, JNull, JNull)
        };
        obj(("status", jstr(st0)) :: ("asset", jstr(a)) :: ("kind", k) :: ("doc", d) :: ("bindings", b) :: ("claims", jstrs(Store.claimsAbout(db, a))) :: Nil)

    // ------------------------------------------------------------------ dispatch

    def readRecs(text: String): Result[String, List[Model.Rec]] =
        Edn.read(text) |> Result.flatMap(Model.records) |> Result.mapErr(m -> "ArgumentError: ${m}")

    /// the ops that only read: run under the Eval handler
    def engineOp(env: Env, op: Json, db: Store, name: String): (Result[String, Json], List[Json]) \ IO =
        Sql.withEval(env#cfg, env#conn, () -> {
            let c = ctxOf(op, db);
            let goalText = () -> Option.getWithDefault("", getStr("goal", op));
            match name {
                case "decide" => decide(db, c, parseGoal(goalText()))
                case "why_not" => whyNot(c, parseGoal(goalText()))
                case "claims" =>
                    let a = Option.getWithDefault("", getStr("asset", op));
                    let cls = List.filter(cl -> cl#about == a and Option.isEmpty(cl#parent), c#claims);
                    obj(("asset", jstr(a)) :: ("claims", jarr(List.map(cl -> { let (_, _, j) = standing(c, cl); j }, cls))) :: Nil)
                case "fetch" =>
                    let cn = Option.getWithDefault("", getStr("concept", op));
                    let fs = match get("filters", op) { case Some(JObject(fm)) => Map.toList(fm) case _ => Nil };
                    let vs = List.map(match (k, v) -> (k, Val(jsonValue(v))), fs);
                    let (rows, mk) = Engine.fetchRows(cn, vs);
                    let tr = match mk(None) { case Node.NFetch(_, _, _, _, _, _, t) => t case _ => false };
                    let (sql, ps) = match mk(None) { case Node.NFetch(_, _, _, _, s, p, _) => (s, p) case _ => ("", Nil) };
                    obj(("concept", jstr(cn)) :: ("filters", Option.getWithDefault(JNull, get("filters", op))) ::
                        ("rows", jarr(List.map(Engine.rowJson, rows))) :: ("sql", jstr(sql)) :: ("params", jarr(List.map(valueJson, ps))) ::
                        ("row_count", jint(Int32.toInt64(List.length(rows)))) :: ("truncated", JBool(tr)) :: Nil)
                case other => Engine.Eval.fail("ArgumentError: unknown op ${other}")
            }
        })

    def doOp(env: Env, main: Ref[Store, r], op: Json, db: Store): (Result[String, Json], List[Json], Bool) \ IO + r =
        let name = Option.getWithDefault("", getStr("op", op));
        match name {
            case "resolve_term" => (Ok(resolveTerm(db, Option.getWithDefault("", getStr("text", op)))), Nil, false)
            case "describe" => (Ok(describe(db, Option.getWithDefault("", getStr("asset", op)))), Nil, false)
            case "add" => match readRecs(Option.getWithDefault("", getStr("edn", op))) {
                case Err(e) => (Err(e), Nil, false)
                case Ok(recs) =>
                    let (st2, ids) = Store.addRecords(Ref.get(main), recs);
                    Ref.put(st2, main);
                    (Ok(obj(("added", jstrs(ids)) :: Nil)), Nil, false)
            }
            case "with_hypothesis" =>
                let add = match getStr("add", op) { case Some(t) => readRecs(t) case None => Ok(Nil) };
                match add {
                    case Err(e) => (Err(e), Nil, true)
                    case Ok(recs) =>
                        let w = List.filterMap(j -> match j { case JString(s) => Some(s) case _ => None }, getList("withhold", op));
                        let (db2, ids) = Store.hypothesis(db, w, recs);
                        let rs = List.map(o -> runOpOn(env, main, o, Some(db2)), getList("ops", op));
                        (Ok(obj(("results", jarr(rs)) :: ("added", jstrs(ids)) :: ("withheld", jstrs(w)) :: Nil)), Nil, true)
                }
            case "sleep" =>
                let t0 = JSys.currentTimeMillis();
                let ms = match get("ms", op) { case Some(JNumber(n)) => Option.getWithDefault(0i64, BigDecimal.tryToInt64(n)) case _ => 0i64 };
                JThread.sleep(ms);
                (Ok(obj(("t0", jint(t0)) :: ("t1", jint(JSys.currentTimeMillis())) :: Nil)), Nil, false)
            case _ => let (r, log) = engineOp(env, op, db, name); (r, log, false)
        }

    /// one op -> its result, with ms and sql_log (errors -> {status: ERROR, error})
    pub def runOpOn(env: Env, main: Ref[Store, r], op: Json, db0: Option[Store]): Json \ IO + r =
        let t0 = JSys.nanoTime();
        let db = match db0 { case Some(d) => d case None => Ref.get(main) };
        let (res, log, hyp) = doOp(env, main, op, db);
        let ms = Int64.toFloat64(JSys.nanoTime() - t0) / 1000000.0;
        let r0 = match res {
            case Ok(j) => j
            case Err(e) => obj(("status", jstr("ERROR")) :: ("error", jstr(e)) :: Nil)
        };
        merge(r0, ("ms", jfloat(ms)) :: ("sql_log", jarr(if (hyp) Nil else log)) :: Nil)

    pub def runOp(env: Env, main: Ref[Store, r], op: Json): Json \ IO + r = runOpOn(env, main, op, None)
}
