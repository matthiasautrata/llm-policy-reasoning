# V3e — Python 3.14 · clingo 5.8.0 · DuckDB / Postgres (V3a's `sql.py`)

System A over the shared slice and contract, plus the defeat-cycle extension (`../shared/cycles.edn`,
`../shared/SEMANTICS-cycles.md`). Plan: `../PLAN-v3-cycles.md` §3. Results: `../RESULTS.md`
("Defeat cycles: V3a with WFS, V3e Clingo").

    .venv/bin/python spikes/v3/shared/accept.py --cli spikes/v3/v3e-clingo/cli        # from the repo root
    .venv/bin/python spikes/v3/shared/cycles_probe.py --cli spikes/v3/v3e-clingo/cli
    .venv/bin/python spikes/v3/v3e-clingo/probes.py                                     # stable / mus / latency / explain
    .venv/bin/python spikes/v3/v3e-clingo/negatives.py

| File | What |
|---|---|
| `asp.py` | load-time EDN → ASP translator (one text per rule or claim) and the fixed metaprogram `META`: demand (`dm`/`need`, a magic-set rewrite keyed by `shared/modes.edn`), `@fetch` during grounding, supports/attacks, superiority (explicit, strict, authority, later), and the defeasible layer doubled for partial stable models; `PLAIN_META` is the undoubled two-valued encoding used by the probes |
| `host.py` | store (records + their ASP texts), one clingo `Control` per op (ground with the SQL context, solve cautious and brave under `active/1` assumptions), statuses and why trees from the truth values (a port of V3a's wfs-mode `defeasible.pl` / `ops.pl` / `why.pl`), the contract's ops, `concurrent` / `after` |
| `cli` | `exec .venv/bin/python host.py` |
| `capabilities.json` | `{"cycles": "report"}`: the model check reports negative cycles rather than rejecting them |
| `probes.py` | plain stable models for Y1–Y3; clingexplaid MUS for Y3; base vs hypothesis latency (ground/solve split); xclingo trial |
| `negatives.py` | the 15 negatives, by V3a's LinkML model plus the shared `model_check.shape_errors` (`v3a-prolog/linkml/build.py` `negatives`) |
| `results/` | `accept.txt`, `bench-{duckdb,postgres}.json`, `cycles-probe-{duckdb,postgres}.json`, `probes.json`, `negatives.txt`, `mutation.txt`, `isolation-{duckdb,postgres}.txt` |

## How a decide runs

1. Program = `META` + the functional-rival rules + the texts of the visible records + `asof("D")` + `dm(pred, (bound args))` for the goal.
2. Ground with a context object: `frow(C,F,R) :- need(C,F), R = @fetch(C,F)` calls V3a's `sql.fetch` for each demanded filter set while grounding recurses, so only demanded rows are fetched (check 5).
3. Solve the same Control twice under assumptions `active(Id)` (false for withheld ids): `enum_mode=cautious` gives the atoms true in every partial stable model (`t_*`, WFS true), and `enum_mode=brave` gives the atoms in some partial stable model (`p_*`, WFS not false). This is the Tr_p doubling of Janhunen et al. 2006: the well-founded model is the knowledge-least partial stable model.
4. The host reads the ground skeleton (`h/3`, `ih/2`) and builds V3a's status (proven / defeated / blocked / undefined / none) and why tree from the three-valued answer.

The truth values come from clingo. The trees come from the host.
