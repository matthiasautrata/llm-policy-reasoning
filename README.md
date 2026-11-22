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
make verify-v1    # check the frozen v1 tree (tag v1) still verifies
```
