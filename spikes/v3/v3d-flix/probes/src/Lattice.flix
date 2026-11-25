// Q2: claim standing as a lattice-valued predicate.
// Chain Bot < Rebutted < Qualified < Holds. A conclusion's standing is the meet of its premises' standings
// (weakest link); alternative derivations are joined by the solver (best support wins). Rebuttal lowers a
// standing, which is not monotone: it goes through stratified negation (`not Attacked(c)`), not the lattice.
mod Lattice {

    pub enum Standing with Eq, Order, ToString { case Bot, case Rebutted, case Qualified, case Holds }

    def rank(s: Standing): Int32 = match s {
        case Standing.Bot => 0
        case Standing.Rebutted => 1
        case Standing.Qualified => 2
        case Standing.Holds => 3
    }

    instance PartialOrder[Standing] { pub def lessEqual(x: Standing, y: Standing): Bool = rank(x) <= rank(y) }
    instance LowerBound[Standing] { pub def minValue(): Standing = Standing.Bot }
    instance JoinLattice[Standing] { pub def leastUpperBound(x: Standing, y: Standing): Standing = if (rank(x) >= rank(y)) x else y }
    instance MeetLattice[Standing] { pub def greatestLowerBound(x: Standing, y: Standing): Standing = if (rank(x) <= rank(y)) x else y }

    pub def meet(x: Standing, y: Standing): Standing = MeetLattice.greatestLowerBound(x, y)

    /// Claims (as asserted), premises of conclusions (two-premise rules; one-premise rules repeat the premise),
    /// attacks (an attacker that itself holds rebuts its target). All of it runtime data.
    pub def probe(): Unit \ IO = {
        let asserted = (("c_hr_cc0078", Standing.Holds) :: ("c_fin_cc0077", Standing.Qualified) :: ("c_doc_role", Standing.Holds) ::
                        ("c_old_role", Standing.Holds) :: ("c_audit", Standing.Holds) :: Nil);
        let rules = ("limit_ok", "c_doc_role", "c_hr_cc0078") :: ("limit_ok", "c_old_role", "c_fin_cc0077") ::
                    ("route_cc", "c_fin_cc0077", "c_fin_cc0077") :: ("approve", "limit_ok", "route_cc") :: Nil;
        let attacks = ("c_audit", "c_old_role") :: Nil;
        let db = inject asserted, rules, attacks into AssertedL/2, Rule/3, Attacks/2;
        let p = #{
            Asserted(c; s) :- AssertedL(c, s).
            Attacked(c) :- Attacks(a, c), Asserted(a; s), if (s == Standing.Holds).
            Eff(c; s) :- Asserted(c; s), not Attacked(c).
            Eff(c; Standing.Rebutted) :- Attacked(c).
            Eff(g; meet(a, b)) :- Rule(g, p1, p2), Eff(p1; a), Eff(p2; b).
        };
        let m = solve db <+> p;
        let effs: Vector[(String, Standing)] = query m select (c, s) from Eff(c; s);
        Vector.forEach(match (c, s) -> println("  Eff(${c}; ${s})"), effs);
        // the same program, attacks removed: only c_old_role changes (Holds); limit_ok is Holds via c_doc_role in both runs
        let db2 = inject asserted, rules into AssertedL/2, Rule/3;
        let effs2: Vector[(String, Standing)] = query db2, p select (c, s) from Eff(c; s);
        println("  without the attack:");
        Vector.forEach(match (c, s) -> println("  Eff(${c}; ${s})"), effs2)
    }
}
