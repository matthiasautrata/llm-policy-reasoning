# v3 benchmark (PLAN-v3-bench)

Built 2026-11-25 on branch spike/v3. The design is in `spikes/v3/PLAN-v3-bench.md` and `notes/warrant-layer/benchmark-design.md`. The engine is reached only through `spikes/v3/v3a-prolog/cli`.

From the repo root:

```
.venv/bin/python bench/gen.py                                        # bases/N{025,050,100,200}.{edn,params,questions}
.venv/bin/python spikes/v3/shared/reference.py --bench bench/bases/N050 bench/bases/N100 bench/bases/N200   # *.keys.json
.venv/bin/python bench/check_bases.py                                # gate, base keys, slice keys on every base
```

## Bases (§2)

| N | rules | claims | interactions | per 100 rules | distractor share | base questions |
|---|---|---|---|---|---|---|
| 25 | 25 | 14 | 4 | 16 | – | – (the slice's 37) |
| 50 | 50 | 30 | 10 | 20 | 0.36 | 45 |
| 100 | 100 | 56 | 20 | 20 | 0.31 | 122 |
| 200 | 200 | 115 | 40 | 20 | 0.30 | 277 |

These figures use seed 1, density 20 and distractor share 0.3. The families are described in `gen.py`'s docstring, and each instance's parameters are in `N*.params.json`. The oracle reads those parameters and never the EDN. Each base passes the integrity gate. Its base questions and the 37 slice questions match their keys through the CLI, including accept.py's proof checks. A changed key fails, as it should. Generation is deterministic.

The `UNION ALL` fetch shape occurs only in the slice (R112 and R311 on `request.category`). Generated rules add none.
