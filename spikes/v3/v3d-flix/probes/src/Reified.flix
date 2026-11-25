// Q1 (ii): a reified encoding. Rules are runtime data (Model.Goal values) in generic relations; one fixed
// meta-program in typed Flix Datalog evaluates them, unification as a functional predicate (Engine.unifyG).
mod Reified {
    import java.lang.{System => JSys}
    use Model.{Goal, Term, Value}
    use Model.Goal.Pos
    use Model.Term.{Var, Val}

    def ms(t0: Int64): Float64 \ IO = Int64.toFloat64(JSys.nanoTime() - t0) / 1000000.0
    def pin(n: Int32): Unit \ IO = JSys.out.print(if (n < 0) "!" else "")

    /// unify body literal `g` with fact `h` under `s`: zero or one extended substitution
    pub def step(g: Goal, h: Goal, s: Engine.Subst): Vector[Engine.Subst] = match Engine.unifyG(g, h, s) {
        case Some(s2) => Vector#{s2}
        case None => Vector#{}
    }

    pub def inst(g: Goal, s: Engine.Subst): Goal = Engine.substG(g, s)

    def str(x: String): Term = Val(Value.VStr(x))

    /// rules as data: (id, head, body goals)
    pub def meta(rules: List[(String, Goal, List[Goal])], facts: List[Goal]): Vector[Goal] = {
        let heads = List.map(match (r, h, _) -> (r, h), rules);
        let lens = List.map(match (r, _, b) -> (r, List.length(b)), rules);
        let lits = List.flatMap(match (r, _, b) -> List.mapWithIndex((i, g) -> (r, i, Model.predOf(g), g), b), rules);
        let keyed = List.map(g -> (Model.predOf(g), g), facts);
        let db = inject heads, lens, lits, keyed into Head/2, Len/2, BodyLit/4, Fact/2;
        let p = #{
            Holds(p, g) :- Fact(p, g).
            Partial(r, 0, Map.empty()) :- Len(r, _).
            Partial(r, i + 1, s2) :- Partial(r, i, s), BodyLit(r, i, p, g), Holds(p, h), let s2 = step(g, h, s).
            Holds(Model.predOf(g), inst(g, s)) :- Partial(r, n, s), Len(r, n), Head(r, g).
        };
        query db, p select g from Holds(_, g)
    }

    /// ancestors_or_self over cc.parent as two rules *as data*, solved by the meta-program
    pub def probe(edges: List[(String, String)], nodes: List[String]): Unit \ IO = {
        let rules = ("anc0", Pos("anc", Var("x") :: Var("x") :: Nil), Pos("node", Var("x") :: Nil) :: Nil) ::
                    ("anc1", Pos("anc", Var("x") :: Var("z") :: Nil),
                        Pos("anc", Var("x") :: Var("y") :: Nil) :: Pos("parent", Var("y") :: Var("z") :: Nil) :: Nil) :: Nil;
        let facts = List.map(n -> Pos("node", str(n) :: Nil), nodes) ++ List.map(match (a, b) -> Pos("parent", str(a) :: str(b) :: Nil), edges);
        let t0 = JSys.nanoTime();
        let out = meta(rules, facts);
        pin(Vector.length(out));
        let anc = Vector.filter(g -> Model.predOf(g) == "anc", out);
        println("reified anc: ${Vector.length(anc)} facts in ${ms(t0)} ms (rules as data, fixed meta-program, facts keyed by predicate)")
    }
}
