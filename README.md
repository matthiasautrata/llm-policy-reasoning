# llm-policy-reasoning

When should a language model evaluate a rule-based policy itself, and when should it hand the job to an engine?
This repository holds two studies on a synthetic procurement-approval policy. The policy is written in three forms, English, Datalog and OWL + SHACL-AF, and every answer key is checked by a machine.

**Paper:** [`PAPER.md`](PAPER.md) · typeset PDF: [`paper/whitepaper.pdf`](paper/whitepaper.pdf)

## Findings in brief

1. **Written decisions matter more than the notation.** When the interpretation decisions were written down, 449 of the 453 answered questions were correct in English, Datalog and OWL + SHACL-AF alike. When they were missing, models silently picked one reading in 15 of 87 answers.
2. **A model evaluating the rules itself runs into cost first, then errors.** As the world grew from 76 to 1,336 facts, the reading runs slowed sharply, and their first errors were omissions from set-valued and count answers. At 1,336 facts, two of Sonnet's three reading runs exhausted their output budget without answering.
3. **Behind an engine, results stay flat.** Querying Soufflé or a graph materialised by pySHACL gave 9 of 9 answers at every size, in 12–56 s per run.

## Layout

```
PAPER.md                      the white paper (GitHub-rendered); paper/ holds the PDF, figures and build scripts
study1-interpretation/        Study 1: ambiguity and notation (fixed small/large worlds)
  prompts/                    18 original prompts (verbatim, recovered) + x01 (OWL+SHACL); manifest.json
  keys/keys.json              expected STATUS per scenario + answer regexes
  oracle/small|large/         the Datalog arms in Soufflé syntax + one query per scenario
  oracle/check_ontology.py    the OWL+SHACL arm under pySHACL == Soufflé, relation by relation
  arms/large-owl-shacl/       schema, rules, data; build_prompt.py -> prompts/x01
  harness/                    run.py (any model via litellm; serves ASK: queries from Soufflé), score.py, import_hermes.py
  transcripts/                the 50 original agent sessions of 2026-08-31 (metadata trimmed)
  results/                    run records (*.jsonl) and graded answers (*.scored.csv)
study2-scaling/               Study 2: size and overrides (generated worlds)
  gen.py, rules.dl, shacl_arm.py   world generator; policy as Datalog, English and OWL+SHACL-AF
  verify.py                   independent Python evaluation of the English rules == Soufflé keys
  check_shacl.py              pySHACL-derived relations == Soufflé, tuple for tuple
  score.py                    grading (exact match; F1 for sets)
  worlds/{S,M,L}-L{0,2}/      the exact worlds, prompts, keys and query tools used in the runs
  results/                    run records, graded answers, wall time and token cost
history/2026-08-31-agent-datalog/  Datalog programs and outputs that the Aug 31 agent wrote during its runs
```

## Reproduce

Requirements: Python ≥ 3.10, [Soufflé](https://souffle-lang.github.io) 2.4+ on `PATH`, and pandoc + XeLaTeX (only for rebuilding the PDF).

```
pip install -r requirements.txt
make verify      # recompute every key; check English == Datalog == OWL+SHACL
make score       # re-grade all recorded runs
make figures     # regenerate paper/fig-*.png from the result files
make paper       # rebuild paper/whitepaper.pdf
```

Running new models:

```
# Study 1 (any litellm model id; oracle arms are served automatically)
python study1-interpretation/harness/run.py --models anthropic/<model> openrouter/<vendor>/<model> --reps 3 \
       --out study1-interpretation/results/runs.jsonl
python study1-interpretation/harness/score.py study1-interpretation/results/runs.jsonl

# Study 2: generate a new world, then hand prompt-*.txt to a model (tool arms: ./ask, ./sparql in the world folder)
python study2-scaling/gen.py --depth 4 --branch 3 --analysts 2 --level 2 --seed 2 --out study2-scaling/worlds/L-L2-s2
```

## Caveats

- Study 2 ran once per cell, with one seed per world.
- The Claude runs used Claude Code subagents, so model versions, temperature and reasoning budgets were not controlled.
- The `AMBIGUOUS` keys in Study 1 are judgements. The numeric and yes/no keys are machine-checked.

See §7 of the paper for the full list.
