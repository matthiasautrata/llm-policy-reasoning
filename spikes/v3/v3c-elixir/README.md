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
| `probes/datalog_probe.exs` | ex_datalog 0.5.0: closures vs CTEs, magic sets, Explain, callbacks, the defeasible meta-program (`FULL=1` adds the ~90 s full reporting-chain runs) |
| `probes/beam_probes.exs` | `[duckdb\|postgres] [all\|super\|par\|reload]`: kill a SQL connection mid-loop, 1 vs 8 processes, hot code reload under load |
| `probes/hyp_latency.py` | hypothesis latency, 50 runs per variant |
| `probes/type_probe.ex` | planted bugs, compiled with `elixirc` to see what the 1.20 type checker reports |
| `results/` | raw outputs of the shared checks and the probes |
