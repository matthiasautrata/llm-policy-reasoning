# llm-policy-reasoning

Which layer of meaning does a question about a rule-based policy need, and in which representation and mode does a language model use it reliably?

v2 is under construction; the plan, hypotheses and milestones are in [`REWORK.md`](REWORK.md).
It crosses four cumulative layers (L0 schema, L1 ontology, L2 context, L3 warrant) with three representations (text, structured, formal) and two modes (*read*: the model answers from the material; *compile*: the model writes a Prolog goal that an engine executes), on a synthetic procurement-approval policy whose answer keys are computed by SWI-Prolog and checked by an independent Python implementation.

## v1

v1, "Rules in Context", asked whether notation matters and when an engine is needed. Written decisions mattered, notation did not; the engine earned its place at scale.
Paper: [`paper/v1/PAPER.md`](paper/v1/PAPER.md) · PDF: [`paper/v1/whitepaper.pdf`](paper/v1/whitepaper.pdf).
Its studies, transcripts and results are at git tag `v1` (see [`paper/v1/README.md`](paper/v1/README.md)).

## Layout

```
REWORK.md     v2 plan and decision log
world/        world generator and domain model
rules/        rules.yaml: rule records (id, layer, class, conservative, owner, english, prolog)
render/       projections per representation × layer (text, structured, prolog)
engine/       SWI-Prolog engine, why/2, capability registry, ./ask
verify/       independent Python reference; engine == reference check
questions/    question bank (kind, min_layer, forks, type) → per-world questions and keys
harness/      model runs, compile-mode IM validation, scoring
worlds/       generated worlds used in runs (committed)
results/      run records
paper/        v2 paper sources; paper/v1/ holds the frozen v1 report
```

## Prerequisites

- Python ≥ 3.10 (`pip install -r requirements.txt`, ideally into `.venv/`; the Makefile uses `.venv/bin/python` when present)
- [SWI-Prolog](https://www.swi-prolog.org) 9+ on `PATH` (developed on 11.0)
- For `make verify-v1` only: [Soufflé](https://souffle-lang.github.io) 2.4+ on `PATH`, and `pip install pyshacl rdflib`

```
make worlds       # regenerate worlds/ (sizes S M L × seeds 1 2 3): relations, L0 projections, questions, keys
make verify       # worlds/ is fresh, and the Python reference reproduces every engine key
make verify-v1    # check the frozen v1 tree (tag v1) still verifies
```

The engine can be queried directly; this is the tool the compile mode will give a model:

```
engine/ask --world worlds/S-s1 --layer 1 'headroom(cc1, V)'
engine/ask --world worlds/S-s1 --layer 1 --reading c1=with_pending 'headroom(cc1, V)'
engine/ask --capabilities --layer 2        # predicates available at a layer, with their meaning
```

It prints one line of bindings per solution (or `true` / `false`). It exits 2 on an error, for example a predicate that is not defined at the requested layer. Every call is logged as JSONL to `$ASK_LOG` or `WORLD/ask.log.jsonl`.

### Model runs

Read mode puts one layer's material in context and asks one question per call. The model ends its reply with a JSON object holding a status (`ANSWER`, `AMBIGUOUS`, `CONFLICT`, `UNDERDETERMINED`, `OUT_OF_SCOPE`) and a value. Calls go through [OpenRouter](https://openrouter.ai), with the key read from `OPENROUTER_API_KEY`.

```
python harness/run.py --layer 0 --worlds S-s1 M-s1 --n 3 --model deepseek/deepseek-v4.1-flash \
    --reasoning-effort medium --out results/run.jsonl --budget 1.00
python harness/run.py --layer 0 --worlds S-s1 --model stub:key --out /tmp/stub.jsonl   # no calls; scores 100%
python harness/score.py results/run.jsonl --report results/run.md
```

How a run behaves:
- It appends one record per call: world, layer, representation, model and serving provider, question, raw reply and reasoning, parsed answer, tokens, cost, seconds.
- It is resumable. Cells that are already done are skipped.
- `--budget` caps the summed cost of the file.
- Providers are restricted to fp8 and sorted by price, unless `--quantization any` is given.
- Plain `results/*.jsonl` files are working copies and are ignored by git. The committed copy is `gzip -9`, and `score.py` reads it directly.
