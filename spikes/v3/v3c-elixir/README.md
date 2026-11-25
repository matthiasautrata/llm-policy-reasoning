# V3c — Elixir · ex_datalog probe · ADBC (DuckDB / Postgres)

System A over the shared slice (`../shared/slice.edn`) and contract (`../shared/CONTRACT.md`).
Plan: `../PLAN-v3cd.md`. Results: `../RESULTS.md` ("V3c and V3d").

    MIX_ENV=prod mix deps.get && MIX_ENV=prod mix compile    # once; the DuckDB 2.0.1 driver downloads on first use
    .venv/bin/python spikes/v3/shared/accept.py --cli spikes/v3/v3c-elixir/cli    # from the repo root

| File | What |
|---|---|
| `lib/v3c/edn.ex` | EDN reader (NimbleParsec) |
| `lib/v3c/model.ex` | validator over the EDN data, rule bodies included; the 12 negatives |
| `lib/v3c/store.ex` | the state as one immutable value; hypotheses are derived values |
| `lib/v3c/engine.ex` | defeasible evaluator (port of V3b `engine.clj`) |
| `lib/v3c/why.ex` | why / why_not trees |
| `lib/v3c/ops.ex` | the contract's ops, `concurrent` mode |
| `lib/v3c/sql.ex` | concept bindings -> SQL through ADBC, supervised connections |
| `lib/v3c/cli.ex`, `cli` | JSON CLI |
| `probes/` | ex_datalog, supervision, concurrency, hot reload |
| `results/` | raw outputs of the shared checks |
