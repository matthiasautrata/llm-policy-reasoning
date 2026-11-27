# llm-policy-reasoning

When a language model answers questions that depend on business rules, does it matter how the rules are written,
and does it matter who applies them: the model, reading them, or an engine it calls?

Three studies on synthetic procurement policies with machine-checked answer keys. Short answer: notation is
secondary; evaluation is not. Models reading the rules get the values right and lose the standing of their answers
(a "no" that rests only on missing data, the sides of a conflict between owners); models calling an engine that
evaluates the same rules keep it, at lower model cost.

## Papers

- **White paper:** [*Beyond Context Graphs and Layers: The Warrant Dimension for Data Agents*](paper/v3/whitepaper/WHITEPAPER.md).
- **Companion (arXiv preprint, LaTeX):** *AI-Ready Data: Syntax, Ontology and Computed Warrants Compared*,
  [`paper/v3/companion/`](paper/v3/companion/) (`make -C paper/v3/companion`). It consolidates the three studies.
- Earlier reports: v1 [`paper/v1/PAPER.md`](paper/v1/PAPER.md), v2 [`paper/v2/PAPER.md`](paper/v2/PAPER.md).

How the papers are built, reviewed and kept free of internal names: [`paper/v3/README.md`](paper/v3/README.md).

## The three studies

- **v3, warrants evaluated** (`spikes/v3/`, `bench/`). System A keeps rules and claims as data, checks them at load
  time and evaluates them as defeasible logic in SWI-Prolog (via janus) over bounded SQL on DuckDB. A benchmark
  compares models reading the rules as a document with models calling the engine, across three models and up to
  200 rules. Current state: [`spikes/v3/RESULTS.md`](spikes/v3/RESULTS.md); how to rebuild and rescore:
  [`bench/README.md`](bench/README.md); how the spike got here: [`spikes/v3/HISTORY.md`](spikes/v3/HISTORY.md).
- **v2, "Layers of Meaning"**: four cumulative layers (L0 schema, L1 ontology, L2 context, L3 warrant) × three
  representations (text, structured, formal) × two modes (*read*: the model answers from the material; *compile*:
  the model writes a Prolog goal that an engine executes). Plan and decision log: [`REWORK.md`](REWORK.md).
- **v1, "Rules in Context"**: English, Datalog and OWL + SHACL-AF, with and without written interpretation
  decisions, and at growing scale. Frozen at git tag `v1` (see [`paper/v1/README.md`](paper/v1/README.md)).

The repository's history, one line per phase with tags and commit ranges: [`HISTORY.md`](HISTORY.md).

## Layout

```
HISTORY.md    v1, v2, v3: one line each, with tags and commit ranges
REWORK.md     v2 plan and decision log
world/        world generator and domain model
rules/        rules.yaml: rule records (id, layer, class, conservative, owner, english, prolog)
render/       projections per representation × layer (text, structured, prolog)
engine/       SWI-Prolog engine, why/2, capability registry, ./ask
verify/       independent Python reference; engine == reference check
questions/    question bank (kind, min_layer, forks, type) → per-world questions and keys
harness/      v2 model runs, compile-mode IM validation, scoring; the shared chat client
worlds/       generated worlds used in runs (committed)
results/      v2 run records
paper/        v1 and v2 reports; paper/v3/ the white paper, the companion and the review tooling
spikes/v3/    System A (engine, oracle, integrity gate, acceptance tests)
bench/        v3 benchmark: rule-base generator, items, set-ups, runs, scoring, committed run records
```

## Prerequisites

- Python ≥ 3.10 (`pip install -r requirements.txt`, ideally into `.venv/`; the Makefile uses `.venv/bin/python` when present)
- [SWI-Prolog](https://www.swi-prolog.org) 9+ on `PATH` (developed on 11.0)
- For `spikes/v3` only: the packages marked spike v3 in `requirements.txt`
- For `make verify-v1` only: [Soufflé](https://souffle-lang.github.io) 2.4+ on `PATH`, and `pip install pyshacl rdflib`

```
make worlds       # v2: regenerate worlds/ (sizes S M L × seeds 1 2 3): relations, projections, questions, keys
make verify       # worlds/ is fresh, the Python reference reproduces every engine key, and the rendered
                  # L1 formal.pl (decided and open) reproduces the L1 keys on its own
make verify-v1    # check the frozen v1 tree (tag v1) still verifies
```

The v2 engine can be queried directly; this is the tool compile mode gives a model:

```
engine/ask --world worlds/S-s1 --layer 1 'headroom(cc1, V)'
engine/ask --world worlds/S-s1 --layer 1 --reading c1=with_pending 'headroom(cc1, V)'
engine/ask --capabilities --layer 2        # predicates available at a layer, with their meaning
```

It prints one line of bindings per solution (or `true` / `false`). It exits 2 on an error, for example a predicate that is not defined at the requested layer. Every call is logged as JSONL to `$ASK_LOG` or `WORLD/ask.log.jsonl`.

### Model runs (v2)

Read mode puts one layer's material in context and asks one question per call. The model ends its reply with a JSON object holding a status (`ANSWER`, `AMBIGUOUS`, `CONFLICT`, `UNDERDETERMINED`, `OUT_OF_SCOPE`) and a value. Calls go through [OpenRouter](https://openrouter.ai), with the key read from `OPENROUTER_API_KEY`.

```
python harness/run.py --layer 0 --worlds S-s1 M-s1 --n 3 --model deepseek/deepseek-v4.1-flash \
    --reasoning-effort medium --out results/run.jsonl --budget 1.00
python harness/run.py --layer 0 --worlds S-s1 --model stub:key --out /tmp/stub.jsonl   # no calls; scores 100%
python harness/score.py results/run.jsonl --report results/run.md
python harness/run.py --layer 1 --config open ...      # L1 with its forks undecided (keys from keys.json "open")
python harness/run.py --layer 0 --prompt assume ...    # JSON also carries a required assumptions list
python harness/score.py results/a.jsonl results/b.jsonl --worlds S-s1 M-s1 --max-rep 1   # common cells only
```

Each world directory holds the material per layer and configuration: `L0/`, `L1/` (decided: forked rules in their
decided reading, decisions stated) and `L1-open/` (every reading of each fork, nothing decided), each with
`text.md`, `structured.yaml` and `formal.pl`.

How a run behaves:
- It appends one record per call: world, layer, representation, model and serving provider, question, raw reply and reasoning, parsed answer, tokens, cost, seconds.
- It is resumable. Cells that are already done are skipped.
- `--budget` caps the summed cost of the file.
- Providers are restricted to fp8 and sorted by price, unless `--quantization any` is given. `--only-provider NAME`
  restricts serving to the named providers (cheapest first, falling back within the list); failed calls are
  recorded as errors and retried on resume.
- Plain `results/*.jsonl` files are working copies and are ignored by git. The committed copy is `gzip -9`, and `score.py` reads it directly.
