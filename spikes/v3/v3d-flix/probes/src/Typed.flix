// Q1 (iii, where Flix Datalog fits) + Q4 (provenance) + Q2 (lattice): Flix Datalog with predicates
// fixed in source, facts injected at runtime from SQL rows.
mod Typed {
    import java.sql.{Connection => JConn}
    import java.lang.{System => JSys}

    def ms(t0: Int64): Float64 \ IO = Int64.toFloat64(JSys.nanoTime() - t0) / 1000000.0

    /// Datalog solving is pure, so the optimiser may move it past a clock read; an IO call that uses the result pins it.
    def pin(n: Int32): Unit \ IO = JSys.out.print(if (n < 0) "!" else "")

    def pairs(conn: JConn, sql: String): List[(String, String)] \ IO =
        match Sql.runQuery(conn, sql, Nil) {
            case Ok(rows) => List.filterMap(r -> match (Map.get("a", r), Map.get("b", r)) {
                case (Some(Model.Value.VStr(a)), Some(Model.Value.VStr(b))) => Some((a, b))
                case _ => None
            }, rows)
            case Err(e) => { JSys.err.println(e); Nil }
        }

    def count(conn: JConn, sql: String): Int64 \ IO = match Sql.runQuery(conn, sql, Nil) {
        case Ok(r :: _) => match Map.get("n", r) { case Some(Model.Value.VInt(n)) => n case _ => -1i64 }
        case _ => -1i64
    }

    /// Transitive closure over runtime rows: ancestors_or_self over cc.parent, reporting chain over emp.manager.
    pub def closure(conn: JConn): Unit \ IO = {
        let t0 = JSys.nanoTime();
        let cc = pairs(conn, "SELECT id AS a, parent AS b FROM cc WHERE parent IS NOT NULL");
        let ids = pairs(conn, "SELECT id AS a, id AS b FROM cc") |> List.map(fst);
        let tf = ms(t0);
        let t1 = JSys.nanoTime();
        let db = inject ids, cc into Node/1, Parent/2;
        let r = #{
            Anc(x, x) :- Node(x).
            Anc(x, z) :- Anc(x, y), Parent(y, z).
        };
        let anc: Vector[(String, String)] = query db, r select (x, y) from Anc(x, y);
        pin(Vector.length(anc));
        let ta = ms(t1);
        let sqlN = count(conn, "WITH RECURSIVE up(cc, id, parent) AS (SELECT id, id, parent FROM cc UNION ALL SELECT u.cc, c.id, c.parent FROM cc c JOIN up u ON c.id = u.parent) SELECT count(*) AS n FROM up");
        println("anc: ${Vector.length(anc)} facts (SQL CTE ${sqlN}) in ${ta} ms; fetch ${List.length(cc)} edges ${tf} ms");

        let emp = pairs(conn, "SELECT id AS a, manager AS b FROM emp WHERE manager IS NOT NULL");
        let t2 = JSys.nanoTime();
        let db2 = inject emp into Mgr/2;
        let r2 = #{
            Chain(x, m) :- Mgr(x, m).
            Chain(x, m) :- Chain(x, y), Mgr(y, m).
        };
        let ch: Vector[(String, String)] = query db2, r2 select (x, m) from Chain(x, m);
        pin(Vector.length(ch));
        let tc = ms(t2);
        let t3 = JSys.nanoTime();
        let sqlC = count(conn, "WITH RECURSIVE ch(id, approver) AS (SELECT id, manager FROM emp WHERE manager IS NOT NULL UNION ALL SELECT ch.id, e.manager FROM emp e JOIN ch ON e.id = ch.approver WHERE e.manager IS NOT NULL) SELECT count(*) AS n FROM ch");
        pin(if (sqlC < 0i64) -1 else 0);
        println("chain: ${Vector.length(ch)} facts (SQL CTE ${sqlC}, ${ms(t3)} ms) in ${tc} ms over ${List.length(emp)} edges");

        // one goal, top-down, as System A asks it: the chain of e077 only (a query on the full closure)
        let t4 = JSys.nanoTime();
        let one: Vector[String] = query db2, r2 select m from Chain("e077", m);
        pin(Vector.length(one));
        println("chain of e077: ${one} (${ms(t4)} ms, full closure recomputed)")
    }

    pub def reified(conn: JConn): Unit \ IO = {
        let cc = pairs(conn, "SELECT id AS a, parent AS b FROM cc WHERE parent IS NOT NULL");
        let ids = pairs(conn, "SELECT id AS a, id AS b FROM cc") |> List.map(fst);
        Reified.probe(cc, ids)
    }

    /// Q4: provenance of one derived fact (`pquery`).
    pub def provenance(conn: JConn): Unit \ IO = {
        let cc = pairs(conn, "SELECT id AS a, parent AS b FROM cc WHERE parent IS NOT NULL");
        let ids = pairs(conn, "SELECT id AS a, id AS b FROM cc") |> List.map(fst);
        let db = inject ids, cc into Node/1, Parent/2;
        let r = #{
            Anc(x, x) :- Node(x).
            Anc(x, z) :- Anc(x, y), Parent(y, z).
        };
        let t0 = JSys.nanoTime();
        let p = pquery db, r select Anc("cc0077", "cc0001") with {Parent, Node};
        pin(Vector.length(p));
        println("pquery Anc(cc0077, cc0001) with {Parent, Node}: ${ms(t0)} ms");
        Vector.forEach(x -> println(ematch x {
            case Node(a) => "  Node(${a})"
            case Parent(a, b) => "  Parent(${a}, ${b})"
        }), p)
    }
}
