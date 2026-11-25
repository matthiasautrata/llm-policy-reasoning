// Q1 (i) at the level Flix compiles `#{...}` to: the slice's rules (Model ADTs parsed from EDN at runtime)
// translated into Fixpoint3.Ast constraints and handed to Fixpoint3.Solver. No Flix source is generated.
// Reports which literal forms translate, and what the stratifier says about
//   (a) the rules read as plain Horn clauses (kinds ignored), and
//   (b) the standard defeasible encoding  p :- body, not ~p.   ~p :- body', not p.
mod Translate {
    import java.lang.{System => JSys}
    import java.lang.{Throwable => JExn}
    import java.sql.{Connection => JConn}
    use Fixpoint3.Boxed
    use Fixpoint3.Boxable.{box, unbox}
    use Fixpoint3.Ast.Shared.PredSym
    use Fixpoint3.Ast.Shared.Denotation.Relational
    use Fixpoint3.Ast.Datalog.{Datalog, Constraint, HeadPredicate, BodyPredicate, HeadTerm, BodyTerm, VarSym, Polarity, Fixity}
    use Fixpoint3.Ast.Datalog.Datalog.{Datalog => Prog}
    use Model.{Goal, Term, Lit, CmpOp, ArOp, Value, Kind, Rule}
    use Model.Form.Logic

    /// the id is a placeholder: runSolver renumbers predicate symbols itself (RenamePredSyms)
    def sym(n: String): PredSym = PredSym.PredSym(n, Int32.toInt64(Hash.hash(n)))

    def tvars(t: Term): List[String] = match t {
        case Term.Var(v) => v :: Nil
        case Term.Ar(_, a, b) => tvars(a) ++ tvars(b)
        case _ => Nil
    }

    /// range restriction, which the `#{...}` frontend enforces and the AST solver assumes:
    /// every variable in the head, a negated literal, a comparison or an arithmetic input is bound
    /// by a positive literal or an `is`/`as_of` output. Returns the unbound variables.
    def unbound(head: Goal, body: List[Lit]): List[String] = {
        let bound = List.flatMap(l -> match l {
            case Lit.Derived(g) => List.flatMap(tvars, argsOf(g))
            case Lit.Fetch(_, fs, outs) => List.flatMap(match (_, t) -> tvars(t), fs) ++ List.map(snd, outs)
            case Lit.Is(x, _, _, _) => x :: Nil
            case Lit.AsOf(t) => tvars(t)
            case _ => Nil
        }, body) |> List.toSet;
        let used = List.flatMap(tvars, argsOf(head)) ++ List.flatMap(l -> match l {
            case Lit.Not(g) => List.flatMap(tvars, argsOf(g))
            case Lit.Cmp(_, a, b) => tvars(a) ++ tvars(b)
            case Lit.Is(_, _, a, b) => tvars(a) ++ tvars(b)
            case _ => Nil
        }, body);
        List.filter(v -> not Set.memberOf(v, bound), used) |> List.distinct
    }

    def predName(g: Goal): String = match g {
        case Goal.Pos(p, _) => p
        case Goal.Neg(h) => "~" + predName(h)
    }
    def argsOf(g: Goal): List[Term] = match g {
        case Goal.Pos(_, a) => a
        case Goal.Neg(h) => argsOf(h)
    }
    def complement(g: Goal): Goal = match g {
        case Goal.Neg(h) => h
        case _ => Goal.Neg(g)
    }

    def bodyTerm(t: Term): Result[String, BodyTerm] = match t {
        case Term.Var(v) => Ok(BodyTerm.Var(VarSym.VarSym(v)))
        case Term.Val(x) => Ok(BodyTerm.Lit(box(x)))
        case Term.Ar(_, _, _) => Err("arithmetic term in an atom")
    }
    def headTerm(t: Term): Result[String, HeadTerm] = match t {
        case Term.Var(v) => Ok(HeadTerm.Var(VarSym.VarSym(v)))
        case Term.Val(x) => Ok(HeadTerm.Lit(box(x)))
        case Term.Ar(_, _, _) => Err("arithmetic term in a head")
    }

    def atom(pol: Polarity, g: Goal): Result[String, BodyPredicate] =
        Result.traverse(bodyTerm, argsOf(g)) |> Result.map(ts -> BodyPredicate.BodyAtom(sym(predName(g)), Relational, pol, Fixity.Loose, List.toVector(ts)))

    def cmpFn(op: CmpOp): Value -> Value -> Bool = match op {
        case CmpOp.Lt => (a, b) -> a < b
        case CmpOp.Le => (a, b) -> a <= b
        case CmpOp.Gt => (a, b) -> a > b
        case CmpOp.Ge => (a, b) -> a >= b
        case CmpOp.Equ => (a, b) -> a == b
    }
    def arFn(op: ArOp): Value -> Value -> Value = match op {
        case ArOp.Plus => (a, b) -> match (a, b) { case (Value.VInt(x), Value.VInt(y)) => Value.VInt(x + y) case _ => Value.VNull }
        case ArOp.Minus => (a, b) -> match (a, b) { case (Value.VInt(x), Value.VInt(y)) => Value.VInt(x - y) case _ => Value.VNull }
    }
    def ub(b: Boxed): Value = unbox(b)

    /// a comparison: both sides variables -> Guard2; one side a constant -> Guard1 closing over it
    def guard(op: CmpOp, a: Term, b: Term): Result[String, BodyPredicate] = {
        let f = cmpFn(op);
        match (a, b) {
            case (Term.Var(x), Term.Var(y)) => Ok(BodyPredicate.Guard2((p, q) -> f(ub(p), ub(q)), VarSym.VarSym(x), VarSym.VarSym(y)))
            case (Term.Var(x), Term.Val(c)) => Ok(BodyPredicate.Guard1(p -> f(ub(p), c), VarSym.VarSym(x)))
            case (Term.Val(c), Term.Var(y)) => Ok(BodyPredicate.Guard1(q -> f(c, ub(q)), VarSym.VarSym(y)))
            case _ => Err("comparison over an arithmetic term")
        }
    }

    /// [:is ?x [op a b]] -> a functional predicate binding ?x. Functional(outputs, f, inputs): outputs first
    /// (both are Vector[VarSym], so a swap type-checks and only crashes inside the solver)
    def functional(x: String, op: ArOp, a: Term, b: Term): Result[String, BodyPredicate] = {
        let f = arFn(op);
        let out = Vector#{VarSym.VarSym(x)};
        match (a, b) {
            case (Term.Var(p), Term.Var(q)) => Ok(BodyPredicate.Functional(out,
                v -> Vector#{Vector#{box(f(ub(Vector.get(0, v)), ub(Vector.get(1, v))))}}, Vector#{VarSym.VarSym(p), VarSym.VarSym(q)}))
            case (Term.Var(p), Term.Val(c)) => Ok(BodyPredicate.Functional(out,
                v -> Vector#{Vector#{box(f(ub(Vector.get(0, v)), c))}}, Vector#{VarSym.VarSym(p)}))
            case (Term.Val(c), Term.Var(q)) => Ok(BodyPredicate.Functional(out,
                v -> Vector#{Vector#{box(f(c, ub(Vector.get(0, v))))}}, Vector#{VarSym.VarSym(q)}))
            case _ => Err("arithmetic over constants or nested terms")
        }
    }

    /// [:fetch c {col term} {col ?v}] -> c(...) over the concept's columns, in order; other columns wild
    def fetchAtom(cols: List[String], c: String, fs: List[(String, Term)], outs: List[(String, String)]): Result[String, BodyPredicate] = {
        let fm = List.toMap(fs);
        let om = List.toMap(outs);
        let ts = List.map(col -> match (Map.get(col, fm), Map.get(col, om)) {
            case (Some(t), _) => bodyTerm(t)
            case (None, Some(v)) => Ok(BodyTerm.Var(VarSym.VarSym(v)))
            case (None, None) => Ok(BodyTerm.Wild)
        }, cols);
        Result.sequence(ts) |> Result.map(xs -> BodyPredicate.BodyAtom(sym("fetch:" + c), Relational, Polarity.Positive, Fixity.Loose, List.toVector(xs)))
    }

    def lit(cols: Map[String, List[String]], asOf: Value, l: Lit): Result[String, BodyPredicate] = match l {
        case Lit.Derived(g) => atom(Polarity.Positive, g)
        case Lit.Not(g) => atom(Polarity.Negative, g)
        case Lit.Fetch(c, fs, outs) => fetchAtom(Map.getWithDefault(c, Nil, cols), c, fs, outs)
        case Lit.Cmp(op, a, b) => guard(op, a, b)
        case Lit.Is(x, op, a, b) => functional(x, op, a, b)
        case Lit.AsOf(Term.Var(v)) => Ok(BodyPredicate.Functional(Vector#{VarSym.VarSym(v)}, _ -> Vector#{Vector#{box(asOf)}}, Vector#{}))
        case Lit.AsOf(_) => Err("as_of over a non-variable")
    }

    def constraint(cols: Map[String, List[String]], asOf: Value, head: Goal, body: List[Lit], extra: List[BodyPredicate]): Result[String, Constraint] =
        match unbound(head, body) {
            case Nil => constraint0(cols, asOf, head, body, extra)
            case vs => Err("not range-restricted, unbound: ${vs}")
        }

    def constraint0(cols: Map[String, List[String]], asOf: Value, head: Goal, body: List[Lit], extra: List[BodyPredicate]): Result[String, Constraint] =
        Result.flatMap(hts -> Result.map(bs ->
            Constraint.Constraint(HeadPredicate.HeadAtom(sym(predName(head)), Relational, List.toVector(hts)), List.toVector(bs ++ extra)),
            Result.traverse(lit(cols, asOf), body)), Result.traverse(headTerm, argsOf(head)))

    def logic(r: Rule): Option[(Kind, Goal, List[Lit])] = match r#form {
        case Logic(k, h, b) => Some((k, h, b))
        case _ => None
    }

    def runP(name: String, cs: List[Constraint]): Unit \ IO = {
        let t0 = JSys.nanoTime();
        let r = try { let u: Vector[Unit] = Fixpoint3.Solver.facts0(sym("__none"), Fixpoint3.Solver.runSolver(Prog(Vector#{}, List.toVector(cs)))); Ok(Vector.length(u)) } catch {
            case e: JExn => Err(e.getMessage())
        };
        let t = Int64.toFloat64(JSys.nanoTime() - t0) / 1000000.0;
        match r {
            case Ok(_) => println("  ${name}: ${List.length(cs)} constraints, stratified, solved (no facts) in ${t} ms")
            case Err(m) => println("  ${name}: ${List.length(cs)} constraints, solver raised: ${String.takeLeft(400, m)}")
        }
    }

    def headPreds(cs: List[Constraint]): List[String] = List.map(c -> match c {
        case Constraint.Constraint(HeadPredicate.HeadAtom(PredSym.PredSym(n, _), _, _), _) => n
    }, cs) |> List.distinct

    /// fetch:<concept> facts from SQL. A concept with a required parameter is materialised per value of a
    /// demand domain chosen by hand (cc/root: every centre; emp: every requester): bottom-up needs it all up front.
    def materialise(conn: JConn, st: Store.Store): (List[Constraint], List[String]) \ IO = {
        let cfg = {backend = "duckdb", duckdb = "", postgres = "", limit = 1000000,
                   concepts = List.filterMap(c -> match c#source {
                        case Model.Source.Sql(q) => Some((c#name, (q, c#params))) case _ => None }, st#meta#concepts) |> List.toMap};
        let col1 = q -> match Sql.runQuery(conn, q, Nil) {
            case Ok(rows) => List.filterMap(r -> Map.get("a", r), rows)
            case Err(_) => Nil
        };
        let ccs = col1("SELECT id AS a FROM cc");
        let reqs = col1("SELECT DISTINCT requester AS a FROM req");
        let domain = pn -> if (pn == "emp") reqs else ccs;
        let per = List.flatMap(c -> match c#source {
            case Model.Source.Sql(_) =>
                let binds = match c#params {
                    case Nil => Nil :: Nil
                    case pn :: Nil => List.map(v -> (pn, v) :: Nil, domain(pn))
                    case _ => Nil
                };
                List.flatMap(b -> match Sql.build(cfg, c#name, b) |> Result.flatMap(match (q, ps) -> Sql.runQuery(conn, q, ps)) {
                    case Ok(rows) => List.map(r -> Ok(Constraint.Constraint(HeadPredicate.HeadAtom(sym("fetch:" + c#name), Relational,
                        List.toVector(List.map(col -> HeadTerm.Lit(box(Map.getWithDefault(col, Value.VNull, r))), c#columns))), Vector#{})), rows)
                    case Err(e) => Err("${c#name}: ${e}") :: Nil
                }, binds)
            case _ => Nil
        }, st#meta#concepts);
        (List.filterMap(Result.toOption, per), List.filterMap(x -> match x { case Err(e) => Some(e) case _ => None }, per) |> List.distinct)
    }

    def countOf(n: String, d: Datalog): Int32 = { let v: Vector[Value] = Fixpoint3.Solver.facts1(sym(n), d); Vector.length(v) }

    def runWith(name: String, facts: List[Constraint], cs: List[Constraint]): Unit \ IO = {
        let t0 = JSys.nanoTime();
        let r = try { let m = Fixpoint3.Solver.runSolver(Prog(List.toVector(facts), List.toVector(cs)));
                      let n = List.map(p -> (p, countOf(p, m)), headPreds(cs));
                      Ok(n) } catch { case e: JExn => Err(e.getMessage()) };
        // pin the pure solve before reading the clock
        match r { case Ok(n) => JSys.out.print(if (List.length(n) < 0) "!" else "") case _ => () };
        let t = Int64.toFloat64(JSys.nanoTime() - t0) / 1000000.0;
        match r {
            case Ok(n) => println("  ${name}: ${List.length(facts)} facts + ${List.length(cs)} rules solved in ${t} ms; derived: ${String.intercalate(" ", List.map(match (p, k) -> "${p}=${k}", n))}")
            case Err(m) => println("  ${name}: solver raised: ${String.takeLeft(300, m)}")
        }
    }

    /// p :- q, not r.  r :- q, not p.   built at runtime: is the negative cycle caught, and how
    def cycle(): Unit \ IO = {
        let x = VarSym.VarSym("x");
        let a = (n, pol) -> BodyPredicate.BodyAtom(sym(n), Relational, pol, Fixity.Loose, Vector#{BodyTerm.Var(x)});
        let h = n -> HeadPredicate.HeadAtom(sym(n), Relational, Vector#{HeadTerm.Var(x)});
        let q = Constraint.Constraint(HeadPredicate.HeadAtom(sym("q"), Relational, Vector#{HeadTerm.Lit(box(Value.VStr("a")))}), Vector#{});
        let cs = Constraint.Constraint(h("p"), Vector#{a("q", Polarity.Positive), a("r", Polarity.Negative)}) ::
                 Constraint.Constraint(h("r"), Vector#{a("q", Polarity.Positive), a("p", Polarity.Negative)}) :: Nil;
        runWith("negative cycle p/r (AST, runtime)", q :: Nil, cs)
    }

    pub def probe(conn: JConn, st: Store.Store): Unit \ IO = {
        let cols = List.toMap(List.map(c -> (c#name, c#columns), st#meta#concepts));
        let asOf = Value.VStr(st#meta#today);
        let rules = List.filterMap(r -> Option.map(x -> (r#id, x), logic(r)), st#rules);
        // (a) Horn reading
        let horn = List.map(match (id, (_, h, b)) -> (id, constraint(cols, asOf, h, b, Nil)), rules);
        let ok = List.filterMap(match (_, x) -> Result.toOption(x), horn);
        let bad = List.filterMap(match (id, x) -> match x { case Err(e) => Some("${id}: ${e}") case _ => None }, horn);
        println("translate: ${List.length(st#rules)} rules, ${List.length(rules)} logic rules, ${List.length(ok)} translated; untranslatable:");
        List.forEach(b -> println("    ${b}"), bad);
        let kinds = List.map(match (_, (k, _, b)) -> (k, List.map(l -> match l {
            case Lit.Derived(_) => "derived" case Lit.Not(_) => "not" case Lit.Fetch(_, _, _) => "fetch"
            case Lit.Cmp(_, _, _) => "cmp" case Lit.Is(_, _, _, _) => "is" case Lit.AsOf(_) => "as_of"
        }, b)), rules);
        let counts = List.foldLeft((m, k) -> Map.insertWith((a, b) -> a + b, k, 1, m), Map.empty(), List.flatMap(snd, kinds));
        println("  literal forms: ${counts}");
        runP("(a) Horn reading, kinds ignored", ok);
        // (b) defeasible encoding: each defeasible/defeater rule blocked by its complementary conclusion
        let defeasible = List.filterMap(match (id, (k, h, b)) -> if (k == Kind.Defeasible or k == Kind.Defeater) Some((id, h, b)) else None, rules);
        let enc = List.filterMap(match (_, h, b) -> {
            let c = complement(h);
            match atom(Polarity.Negative, c) {
                case Ok(blk) => Result.toOption(constraint(cols, asOf, h, b, blk :: Nil))
                case Err(_) => None
            }
        }, defeasible);
        let strict = List.filterMap(match (_, (k, h, b)) -> if (k == Kind.Strict) Result.toOption(constraint(cols, asOf, h, b, Nil)) else None, rules);
        runP("(b) defeasible encoding (p :- body, not ~p)", strict ++ enc);
        let t0 = JSys.nanoTime();
        let (facts, ferr) = materialise(conn, st);
        println("  materialised ${List.length(facts)} fetch facts in ${Int64.toFloat64(JSys.nanoTime() - t0) / 1000000.0} ms; errors: ${ferr}");
        runWith("(a) Horn reading over SQL facts", facts, ok);
        runWith("(b) defeasible encoding over SQL facts", facts, strict ++ enc);
        cycle()
    }
}
