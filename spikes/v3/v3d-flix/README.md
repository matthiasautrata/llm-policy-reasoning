# V3d — Flix 0.80.0 · JDBC (DuckDB / Postgres)

System A over the shared slice (`../shared/slice.edn`) and contract (`../shared/CONTRACT.md`).
Plan: `../PLAN-v3cd.md`. Results: `../RESULTS.md` ("V3c and V3d").

    ./fx build-fatjar                                                      # in this directory; ./fx fetches the JDBC jars into lib/
    .venv/bin/python spikes/v3/shared/accept.py --cli spikes/v3/v3d-flix/cli    # from the repo root

Probes (a separate Flix project in `probes/`; its `src/` symlinks System A's sources):

    (cd spikes/v3/v3d-flix/probes && ./fx build-fatjar)
    java -Xss512m --enable-native-access=ALL-UNNAMED -Dprobe=<typed|reified|translate|lattice|all> \
         -jar spikes/v3/v3d-flix/probes/artifact/probes.jar                # from the repo root

| File | What |
|---|---|
| `src/Edn.flix` | EDN reader for the slice subset, hand-written |
| `src/Model.flix` | ADTs for terms, literals, rules, claims, concepts; EDN → ADT parse plus explicit checks; the 15 negatives |
| `src/Store.flix` | the state as one immutable record; hypotheses are derived values |
| `src/Engine.flix` | defeasible evaluator (port of V3b `engine.clj` / V3c `engine.ex`) and why / why_not trees |
| `src/Ops.flix` | the contract's ops |
| `src/Sql.flix` | concept bindings → SQL through JDBC (`\ IO`) |
| `src/Main.flix`, `cli` | JSON CLI, `concurrent` / `after` keys (a thread per op list, a connection per thread) |
| `probes/src/Typed.flix` | Q1 (iii)/Q4: Flix Datalog closures over SQL rows vs CTEs, `pquery` provenance |
| `probes/src/Reified.flix` | Q1 (ii): rules as data, a fixed meta-program in Flix Datalog |
| `probes/src/Translate.flix` | Q1 (i): slice rules → runtime `Fixpoint3` AST values, solved over materialised SQL facts |
| `probes/src/Lattice.flix` | Q2: claim standing as a lattice-valued predicate |
| `probes/neg/Cycle.flix` | the same negative cycle written as a typed `#{}` program (rejected at compile time) |
| `probes/types/` | planted defects T01–T10 (V3c analogs) plus E1, E2; `run.sh <scratch dir>` checks each alone |
| `probes/hyp_latency.py` | hypothesis latency, 50 runs per variant |
| `probes/par.py` | the bench's 200 decides, 1 vs 8 threads |
| `results/` | raw outputs of the shared checks and the probes |
