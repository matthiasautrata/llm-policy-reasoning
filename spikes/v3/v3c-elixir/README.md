# V3c — Elixir · ex_datalog probe · ADBC (DuckDB / Postgres)

System A over the shared slice (`../shared/slice.edn`) and contract (`../shared/CONTRACT.md`).
Plan: `../PLAN-v3cd.md`. Results: `../RESULTS.md` ("V3c and V3d").

    MIX_ENV=prod mix deps.get && MIX_ENV=prod mix compile    # once; the DuckDB 2.0.1 driver downloads on first use
    .venv/bin/python spikes/v3/shared/accept.py --cli spikes/v3/v3c-elixir/cli    # from the repo root

| File | What |
|---|---|
| `lib/v3c/edn.ex` | EDN reader (NimbleParsec) |
| `lib/v3c/model.ex` | validator over the EDN data, rule bodies included; the 15 negatives (PLAN-v3 12, #9 re-expressed, PLAN-v3-integrity §1.5 13-15) |
| `lib/v3c/store.ex` | the state as one immutable value; hypotheses are derived values |
| `lib/v3c/engine.ex` | defeasible evaluator (port of V3b `engine.clj`) with ambiguity propagation (`shared/SEMANTICS.md`: `lit3`/`body3`/`classify3`); the blocking-era `supporters`/`attackers`/`classify` remain, unused |
| `lib/v3c/why.ex` | why / why_not trees |
| `lib/v3c/ops.ex` | the contract's ops, `concurrent` mode |
| `lib/v3c/sql.ex` | concept bindings -> SQL through ADBC, supervised connections |
| `lib/v3c/cli.ex`, `cli` | JSON CLI; runs the integrity gate on the load before EDN validation |
| `lib/v3c/gate.ex` | the shared integrity gate (`shared/integrity.py`) as a subprocess, for load, `add`, `with_hypothesis` (PLAN-v3-integrity §2); the re-entry guard is in `engine.ex` `evaluate` |
| `probes/datalog_probe.exs` | ex_datalog 0.5.0: closures vs CTEs, magic sets, Explain, callbacks, the defeasible meta-program (`FULL=1` adds the ~90 s full reporting-chain runs) |
| `probes/beam_probes.exs` | `[duckdb\|postgres] [all\|super\|par\|reload]`: kill a SQL connection mid-loop, 1 vs 8 processes, hot code reload under load |
| `probes/hyp_latency.py` | hypothesis latency, 50 runs per variant |
| `probes/type_probe.ex` | planted bugs, compiled with `elixirc` to see what the 1.20 type checker reports |
| `results/` | raw outputs of the shared checks and the probes; `accept.txt` (checks 1–8, blocking, phase 2), `*-propagation*` (PLAN-v3-integrity §4: accept, mutation, isolation, negatives = `mix test`, bench), `guard-probe.txt` / `guard-probe-duckdb.json` (re-entry guard, `shared/cycles_probe.py`, refreshed under propagation); `cycles-probe*` are the PLAN-v3-cycles runs |
