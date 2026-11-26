# Spike v3 results: System A and the benchmark

This file covers the current state only. `HISTORY.md` covers how the spike got here: five platforms, the exploratory runs, reversed findings and platform lessons. Its intro names the tags that hold everything removed.

System A was measured on 2026-11-25 on Apple Silicon (macOS), with SWI-Prolog 11.0.1, janus-swi 1.5.3, duckdb (Python) 2.0.1 and LinkML 1.12.1. The benchmark was run on 2026-11-26. DuckDB is the only backend. Postgres 18 gave identical answers and was retired on 2026-11-25 (HISTORY phase 1). The raw engine outputs are in `v3a-prolog/results/` and the benchmark records in `bench/results/`. Run these from the repo root:

```
.venv/bin/python spikes/v3/shared/reference.py                                   # keys.json (oracle)
.venv/bin/python spikes/v3/shared/accept.py    --cli spikes/v3/v3a-prolog/cli    # checks 1, 3-8; add --mutation
.venv/bin/python spikes/v3/shared/isolation.py --cli spikes/v3/v3a-prolog/cli
.venv/bin/python spikes/v3/shared/bench.py     --cli spikes/v3/v3a-prolog/cli
.venv/bin/python spikes/v3/shared/cycles_probe.py --cli spikes/v3/v3a-prolog/cli # re-entry guard, gate off
.venv/bin/python spikes/v3/shared/hyp_latency.py  --cli spikes/v3/v3a-prolog/cli
.venv/bin/python spikes/v3/v3a-prolog/linkml/build.py                            # LinkML model, negatives
```

`bench/README.md` gives the commands that regenerate the benchmark items and keys and that reproduce every run and table below.

# System A

## What it is

- **Shape.**
  - Rules and claims are data. They are authored once in EDN (`shared/slice.edn`, `extension.edn`, `cycles-acyclic.edn`) and interpreted at runtime by a top-down defeasible engine.
  - Detail data stays in DuckDB. The engine reaches it only through `fetch(concept, filters)`. The bindings from concept to SQL live in the slice, and no table is ever loaded.
- **Contract** (`shared/CONTRACT.md`). A session is a JSON-lines CLI.
  - Ops: `decide`, `claims`, `why`, `why_not`, `add`, `with_hypothesis` and `resolve_term`, plus the design ops `rules` and `summary`.
  - Answers: `ANSWER`, `CONFLICT` with sides, `UNDERDETERMINED` or `OUT_OF_SCOPE`. Each comes with a why tree and owners.
- **Semantics** (`shared/SEMANTICS.md`). The logic is defeasible, with team defeat and ambiguity propagation. A literal is proven, refuted or contested, and anything downstream of a contested conclusion is contested.
  - Superiority is ordered: explicit, then strict, then authority, then later `asserted_at`.
  - Functional predicates make rivals. Claims are defeasible facts, gated by valid time.
  - `[:agg :sum|:count ?x [body] ?out]` aggregates over the proven solutions of a derived conjunction. Any contested member contests the aggregate.
  - Every `decide` ANSWER carries a `qualifier`.
    - It is `"total over known facts in declared scope"` when the answer rests on absence, and null otherwise.
    - An answer rests on absence when its proof uses a `:closed_over` rule, or when a ground `false` has no live supporter or is defeated through such a rule.
    - Coverage is derived. A name is covered by an in-force `[:complete "N"]` claim, or when no claim feeds it and everything that concludes or attacks it is covered.
- **Oracle.** `shared/reference.py` re-implements the semantics independently of the engine and writes `keys.json`.
  - `check_why.py` re-derives every why tree and re-runs the SQL of each node.
  - The mutation test guards the checker itself: check 1 must fail on mutated keys.
- **Integrity gate** (`shared/model_check.py` through `shared/integrity.py`, IR-001a … IR-007).
  - It is one shared Python implementation, imported by V3a. It runs at load, before every `add`, and inside `with_hypothesis` against the hypothetical rule base.
  - A violation rejects the change and leaves the state as it was.
  - Cycles are rejected, never answered. With the gate off, a re-entry guard in the evaluator still catches them.
  - One check of slice, extension and acyclic takes about 12.6 ms.

| Id | Violation | Fixture (`shared/fixtures/integrity/`) |
|---|---|---|
| IR-001a | `defeat-cycle` (negative dependency cycle) | `y2-even-loop.edn` (RY23 RY24), `y3-odd-loop.edn` (RY31 RY32) |
| IR-001b | `superiority-cycle` | `ir001b-explicit.edn`, `ir001b-authority.edn` |
| IR-002 | `duplicate-definition` | `ir002-duplicate-definition.edn` |
| IR-003 | `rebuttal-without-preference` (an ordering key) | `ir003-ordering-key.edn` |
| IR-004 | `missing-additivity` on a measure | derived: slice without `:additivity` |
| IR-005 | `negative-without-completeness` | `ir005-no-completeness.edn` |
| IR-006 | `unbound-call` (moded safety, `modes.edn`) | `ir006-unbound-call.edn` |
| IR-007 | `unsafe-aggregation` (a `:sum` of a `:semi-additive` measure across a parameter bound inside the aggregate) | `ir007-unsafe-aggregation.edn` (RA1) |

## The engine: V3a (`v3a-prolog/`)

V3a is SWI-Prolog hosted from Python through janus. It has one evaluation mode: recursion with a memo of statuses keyed by state token. Why trees are rebuilt on demand.

| Part | Lines |
|---|---|
| `defeasible.pl`: store, three-valued `eval3`/`classify3`/`body3`, aggregates, superiority, re-entry guard | 362 |
| `ops.pl`: the contract ops, `contested_why`, the absence qualifier, hypotheses | 301 |
| `why.pl`: why / why_not trees | 63 |
| `edn.pl`: EDN reader (DCG) | 78 |
| `sql.py`: the `fetch` boundary (duckdb), per-thread cache | 97 |
| `host.py` + `cli`: janus host, gate calls | 72 + 4 |
| `linkml/`: `slice.yaml` schema, `edn2yaml.py`, `build.py` (docs, DDL comparison, negatives) | |

| Criterion | V3a |
|---|---|
| Correctness | `accept.py` is GREEN on checks 1 and 3–8 (`results/accept.txt`). Check 2, the backend swap, is retired. `--mutation` fails check 1, as it must (`results/mutation.txt`). |
| Defeasible semantics | Built in `defeasible.pl`: team defeat, superiority, functional rivals, R314 incompatibility (an attacker of `approved`), aggregates over derived literals, and propagation with a `contested` why node. |
| Explanations | Complete against the keys. `check_why.py` re-verifies every tree, including `contested` nodes (`via`, `rules`, roots) and aggregate nodes (each member re-proved, the total recomputed). |
| As-of / provenance | Valid time comes from claim attributes (`valid_from`/`valid_to`). Assertion provenance comes from `asserted_by`/`asserted_at`/`recorded_at`. There is no transaction-time axis. |
| Adoption gate | `snapshot/1`: changes are invisible to other threads and always discarded. `isolation.py` PASS (`results/isolation-duckdb.txt`). |
| Integrity | Check 8 PASS: 9 fixtures, plus the `add` and hypothesis cases, with the member sets above. With the gate off, the re-entry guard names 2 of 2 loops as `defeat-cycle` with their goal path, in 0.8–2.2 ms (`results/guard-probe.*`). |
| Model / validation | LinkML 1.12.1, with structured rule bodies including the `Aggregate` literal. 90/90 literals round-trip to EDN. All 15 negatives are rejected by some layer: linkml-validate 14/15, JSON Schema 14/15, the shared shape check 4/15 (`linkml/negatives.md`, `results/negatives.txt`). |
| SQL boundary | Prolog → Python (janus) → duckdb. 11.92 statements per `approved` decision. The exhaustive set question (check 5) uses 551 bounded statements and at most 425 rows. |
| Footprint (information) | SWI-Prolog 11.0.1 (brew) plus `.venv`, 273 MB (LinkML dominates). |

**Latency** (`bench.py`).
- Setup: 200 `approved` decisions on seeded random requests, then the questions. The per-op `ms` is the CLI's own clock.
- Outcome: 49/200 approved, 0 errors.

| | DuckDB |
|---|---|
| decide p50 / p95 / max (ms) | 4.89 / 10.13 / 15.5 |
| questions p50 / p95 (ms) | 1.23 / 1148 (Q46, the contested aggregate over cc0105) |
| load (ms), cold start (s) | 62, 0.13 |
| max RSS, loaded / bench (MB) | 63 / 162 |

**Hypotheses** (`hyp_latency.py`, n = 30). The table gives p50 / p95 in ms, for the base `decide` and for the whole `with_hypothesis` op, which includes the gate.

| | base | hypothesis |
|---|---|---|
| Q10 (withhold R313): ANSWER → CONFLICT | 0.14 / 0.15 | 0.17 / 0.20 |
| Q38 (withhold RY23): CONFLICT → ANSWER | 0.58 / 0.83 | 0.37 / 0.40 |

Bench runs drift by about ±10 % on p50, so smaller differences are noise.

## What the slice exercises (HISTORY phases 7–9)

- **Aggregates.**
  - Questions:
    - Q44 (cc0058) is an ANSWER of 1512000.
    - Q45 asks for a count over leaf cc0290.
    - Q46 (cc0105) is a CONFLICT `[[R312],[R314]]` through r000001.
  - R120 and R121 are `:closed_over :known_facts`, as IR-005 requires.
  - The body is evaluated set-at-a-time in rounds against the per-op cache (`CONTRACT.md`, Aggregates). Each round fetches its misses as one paged statement per concept and filter shape, so no statement returns more than `fetch_limit` rows.
- **IR-007.** The gate rejects a `:sum` of a `:semi-additive` measure across one of its parameters. This covers a direct fetch of the measure and a predicate that carries it, as R104 carries `booked_total`.
  - No slice rule is rejected.
  - RA1 sums `booked_total` over a chain of ancestors.
- **The absence qualifier** is held by every `decide` key.
  - Only `booked_total` is covered (C10).
  - Q53–Q55 move the qualifier with completeness claims declared inside `with_hypothesis`:
    - Q53, the base: CLOSED;
    - Q54, with every name `cap_breach` reads declared complete: `null`;
    - Q55, the same without `cost_centre`: CLOSED.
- **Downstream of real conflicts.**
  - R315 `home_headroom` (Q48, Q49) derives from the claim conflict C3/C4.
  - R316 `po_issued` (Q50–Q52) derives from `approved`, which is contested by R312/R314.
  - V3a matched every key without an engine change.

**Large aggregates.** The workload is `[:approved_total C ?v]` at 10⁵ requests. Each centre ran in its own in-process session, in SWI's default 1 GB stack.

| Centre (level) | Result | statements | ms | peak RSS |
|---|---|---|---|---|
| cc0290 (L4) | ANSWER 32000 | 12 | 84 | 96 MB |
| cc0681 (L4) | CONFLICT | 12 | 97 | 97 MB |
| cc0058 (L3) | ANSWER 1512000 | 12 | 420 | 109 MB |
| cc0105 (L3) | CONFLICT | 12 | 521 | 111 MB |
| cc0018 (L2, 2 224 pending) | CONFLICT | 24 | 2 669 | 173 MB |
| cc0002 (L1, 11 213 pending) | CONFLICT | 95 | 13 184 | 419 MB |
| cc0000 (root, 90 028 pending) | CONFLICT | 693 | 107 566 | 2 781 MB |

- **Statements.** The count is O(concepts × rounds × pages): 693 at the root, against about 260 000 if members were fetched one at a time.
- **Time** is linear in the members, at about 1.2 ms per pending member from L2 up. The evaluator takes about 94 % of the root's time (SQL is 7.3 of 132 s).
- **Memo.** About 58 bytes per entry, about 10 entries per member.
- **Fixes behind these numbers.**
  - One SQL form per concept, `IN ($p)`, with a single key as a set of one.
  - Rules indexed by head predicate.
  - A memo that holds statuses only.
  - The attribution that motivated them is in HISTORY phase 8. The full table is in RESULTS at tag `spike-v3-benchmark`.
- **Scope decision** (Matthias, 2026-11-25).
  - The system answers questions *about* the data: structure, meaning, classifications, relationships, claims, warrants, and SQL help. It is not the execution path for big-data queries.
  - The root aggregate is therefore a documented residual (residual 2), not a blocker. It misses the "good enough" bar of about 10 s and 1 GB. Only taking the per-member evaluator out of the loop would meet that bar.

# The benchmark

## Design

**Question.** Does a model answer and design policy questions better with the engine as a tool than with the same rules as text?

The design note is `notes/warrant-layer/benchmark-design.md`. The build and the reproduction commands are in `bench/README.md`. Each run is named by the plan section that ran it (§3b′ … §3f). The plan is at tag `spike-v3-benchmark` (`PLAN-v3-bench-full.md`), and HISTORY phases 17–21 record each run with its commits.

**Bases** (`bench/gen.py`). One generator produces synthetic rule bases of N = 50, 100 and 200 rules over the slice's purchasing domain. It seeds families of interacting rules: dated limits, exceptions and counter-exceptions, capitalisation ranges disputed between owners, with or without superiority, and sub-programme chains. Each base passes the integrity gate. Its keys come from `reference.py`, which reads the generator's parameters, never the EDN.

**Arms.** Every arm has the data model and `sql` over the same DuckDB data. All arms share one task instruction, which defines `qualified`, and the same call limit: 8 calls with tools per manager turn and 12 per analyst turn. A turn at the limit gets one forced final answer, and `score.py` reports those turns as their own outcome.

| arm | adds | role |
|---|---|---|
| F | nothing: no rules | floor: what the material contributes |
| G | the rules and claims as markdown (`bench/material/N*.md`, rendered from rule docs, every id present) | rules as text |
| G+ | G plus five trusted functions over the slice rules (`bench/gplus.py`) | the usual deployment |
| G-q, G+-q | G or G+ plus one sentence: "For every no, say whether it rests only on not finding something in the data." | control: asking for the qualifier |
| G-tools | G's material without its rules and claims, which it looks up with T's `rules` tool (no evaluation) | control: rule navigation without the evaluator |
| T | the engine's tools: `resolve_term`, `describe`, `decide`, `why`, `why_not`, and the design tools `rules` and `summary` | rules as an engine |

**Items.**
- **Family questions** (`bench/questions/family.json`): F01–F16 per N, as manager questions. They are sampled from the base's questions and stratified by k, the rules and claims on the key's proof path (1, 2–3, 4–5, 6+), four per stratum. Within a stratum there is one question per outcome where possible:
  - true;
  - false by absence, which needs the qualifier;
  - false by defeat;
  - contested, which needs the sides;
  - a claim.
- **A4** (`bench/tasks/A4.json`) is a four-turn analyst design task on programme P01. Its gold reasons are derived from the generator's parameters, and its checks have per-N keys (`A4.keys.json`). It asks about the same nine requests at every N, while N adds disputes over P01's category and sub-programme levels.
- **Strata.** Each family item also records d, the capitalisation disputes with a rule on its path. The strata differ by N (family items, of 16):

| N | k 1 / 2–3 / 4–5 / 6+ | d 0 / 1 / 2–3 / 4+ |
|---|---|---|
| 50 | 4 / 10 / 2 / 0 | 11 / 5 / 0 / 0 |
| 100 | 4 / 4 / 5 / 3 | 10 / 0 / 6 / 0 |
| 200 | 4 / 4 / 4 / 4 | 9 / 0 / 0 / 7 |

  d 1 occurs only at N 50, and d 4+ only at N 200. A comparison across N therefore compares item sets as well as N.

**Models.** The judge model and the arms are fixed across models:
- DeepSeek v4.1 Flash (`deepseek/deepseek-v4.1-flash`, OpenRouter, providers admitted by the fp8 quantization filter);
- GLM 5.3 (`z-ai/glm-5.3`, OpenRouter);
- gpt-6.2-sol (`openai@gpt-6.2-sol`, OpenAI Responses API), at reasoning effort medium and high.

**Scoring.** Grades come from oracle keys wherever keys decide. The LLM judge is used only where no key does.
- **Manager answers.** A manager answer is correct when status, value, sides and qualifier all match the key. Every key states its qualifier, null when none applies. Sides are scored two ways:
  - strict: the same id sets;
  - tolerant: each key side falls inside exactly one reported side, with extra ids allowed.
- **Analyst checks.** A check is read from the session's text by subject-scoped readers (`bench/score.py`). A number counts only in a block or under a heading that names the check's subject. A decide verdict counts only if its block cites a rule of the oracle's core, or, for a key resting on absence, says so.
- **Gold reasons.** Each reason is decided by the checks that name it (`decided_by`):
  - covered when every check is reported correctly;
  - wrong when one gives the naive value, a plain value for a contested key, or the other value;
  - missed otherwise.
- **Where the judge grades instead.** The judge (`gpt-6.2-sol`, OpenAI Batch, effort medium, `bench/judge_rubric.md`) judges each session twice. It grades three kinds of reason, labelled per task and N in the report:
  - reasons with no keys;
  - reasons whose keys no reader reads;
  - reasons that say something is contested at an N where no key is.
  - Unclear readings also fall back to the judge's first judging.
- **Unconfirmed numbers.** A numeric grade that the judge contradicts counts as unconfirmed.

**Confirmatory runs.** Each confirmatory run had its expected outcomes recorded in the plan before it ran. Each replication repeats a confirmatory design on new N or a new model. All runs use 3 repetitions and frozen arms.

| run | items | arms (manager; analyst) | model, N | status | records |
|---|---|---|---|---|---|
| §3b′ | F01–F16, A4 | G, G+, T, F; G, T, F | DeepSeek; 50, 200 | confirmatory | `b3c` |
| §3c.2 | F01–F16 | G-q, G+-q | DeepSeek; 200 | confirmatory | `b3d-q` |
| §3d.2 | F01–F16, A4 | G-tools; G-tools | DeepSeek; 200 | confirmatory | `b3d-gtools` |
| §3c.3 | F01–F16, A4 | G, G+, T, F; G, T, F | DeepSeek; 100 | replication | `b3d-n100` |
| §3c.4, §3d.1 | F01–F16; A4 | G, G+, T; G, G+, T | GLM 5.3; 200 | replication | `b3d-glm`, `b3d-glm-a4` |
| §3e.2 | F01–F16 | G, G-q, T | gpt-6.2-sol, effort medium; 200 | confirmatory | `b3e` |
| §3f | F01–F16 | G, G-q, T | gpt-6.2-sol, effort high; 200 | confirmatory | `b3f` |

Each run's files are in `bench/results/`: `<records>.jsonl.gz` holds the cells, and `.judge-medium.jsonl.gz` and `.2.jsonl.gz` hold the grades. For §3b′ the grades are `b3c.rejudge-medium*`. In the tables, a refused or truncated record that was re-run counts in cost only.

**Exploratory runs.** The pilot, batch 1 (§3, §3a) and §3b ran one repetition each, on the slice's manager questions M01–M31, A1–A3, and an older generator whose programmes did not interact (k ≤ 3). They shaped the arms and the scoring, and their tables are in HISTORY phases 11, 14 and 16. No result below rests on them.

## Family questions: DeepSeek, N 50 and 200 (§3b′)

48 cells per arm and N (16 items × 3). "Correct" gives strict; tolerant sides.

| arm | N | correct | status | qualifier | contested sides strict / tolerant (of 9) | by k: 1 / 2–3 / 4–5 / 6+ |
|---|---|---|---|---|---|---|
| F | 50 | 0; 0 | 6 | 24/39 | 0 / 0 | 0/12, 0/30, 0/6, – |
| F | 200 | 6; 6 | 12 | 27/42 | 0 / 0 | 0/12, 0/12, 3/12, 3/12 |
| G | 50 | 33; 33 | 44 | 27/39 | 6 / 6 | 9/12, 18/30, 6/6, – |
| G | 200 | 25; 26 | 46 | 27/42 | 2 / 3 | 9/12, 6/12, 7/12, 3/12 |
| G+ | 50 | 30; 30 | 42 | 27/39 | 3 / 3 | 9/12, 15/30, 6/6, – |
| G+ | 200 | 27; 28 | 46 | 27/42 | 3 / 4 | 9/12, 6/12, 9/12, 3/12 |
| T | 50 | 43; 43 | 48 | 35/39 | 9 / 9 | 10/12, 27/30, 6/6, – |
| T | 200 | 46; 46 | 48 | 40/42 | 9 / 9 | 11/12, 11/12, 12/12, 12/12 |

Correct by the key's outcome, at N 50 / N 200. The totals are 15/15 true, 12/15 false by absence, 3/3 false by defeat, 9/9 contested and 9/6 claims.

| arm | true | false (absence) | false (defeat) | contested | claim |
|---|---|---|---|---|---|
| G | 15 / 14 | 0 / 0 | 3 / 3 | 6 / 2 | 9 / 6 |
| G+ | 15 / 15 | 0 / 0 | 3 / 3 | 3 / 3 | 9 / 6 |
| T | 14 / 15 | 8 / 13 | 3 / 3 | 9 / 9 | 9 / 6 |
| F | 0 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

- **Closure.** G and G+ never qualify a "no" that rests on absence: 0 of 27 at both N. In 25 of the 27 misses the value is right and only the qualifier is missing. T qualifies 21 of 27.
- **Contested sides.** G's sides degrade as disputes accumulate: strict 6 of 9 at N 50 (one dispute) and 2 of 9 at N 200 (d 4–7). T has all 18.
- **Values.** G's status is right in 90 of 96, its value wrong on 1 of 30 true keys, and every rule arm gets false by defeat in 6 of 6.
- **k.** G falls from 9/12 at k 1 to 3/12 at k 6+ at N 200. The fall is closure, not wrong values: the k ≥ 6 slots at N 200 are contested or absence keys.
- **F** answers 6 of 96, all of them "true" keys at N 200 that it answered "yes" without the rules.
- **G+** is not better than G. None of its five functions reaches the families, so on these items it is G with unused tools.
- **Cost.** Per correct family answer at N 200, T costs $0.0013 and G $0.0017. F reaches the call limit in 33 of 96 manager cells, T in 3 and G in none.

## A4: DeepSeek, N 50 and 200 (§3b′)

Gold reasons covered / missed / wrong, over 3 sessions: 9 reasons per session at N 50, 10 at N 200. The judge's first judging alone is in brackets.

| arm | N 50 (of 27) | N 200 (of 30) | numeric checks reported, judge-confirmed (of 15), N 50 and 200 |
|---|---|---|---|
| F | 0 / 11 / 16 (0 / 3 / 24) | 0 / 15 / 15 (0 / 5 / 25) | 0 and 0 |
| G | 14 / 0 / 13 (14 / 0 / 13) | 23 / 2 / 5 (25 / 0 / 5) | 13 and 15 |
| T | 25 / 0 / 2 (25 / 0 / 2) | 28 / 0 / 2 (25 / 0 / 5) | 15 and 15 |

- **GR7** (precedence, and contested where no superior rule holds) is graded from keys.
  - At N 200, T reports r000059 as contested with both sides in 3 of 3 sessions. G does so in 1, gives a plain value in 1, and is unclear in 1.
  - At N 50 no key tests GR7, because r000059 (8,000) is in no capitalise range there.
- **GR2** (outside P01's category the limit answer is false, not unknown) is judge-only. G is wrong in 10 of 12 gradings and T in 3 of 12.
- **Numeric checks.** G and T report them, including the chain counts (N 200: 2,050 cleared and 3,692 contested under U04), and neither gives the naive value. F reports none once the judge's confirmation is required. Its 8,000 is r000228's amount, which equals the limit, and its 0 is a row count.

## Controls

**The qualifier sentence (§3c.2).** DeepSeek, N 200, family questions, of 48.

| arm | correct; tolerant | qualifier (of 42) | contested sides strict / tolerant (of 9) | false by absence (of 15) | by k: 1 / 2–3 / 4–5 / 6+ |
|---|---|---|---|---|---|
| G (§3b′) | 25; 26 | 27 | 2 / 3 | 0 | 9, 6, 7, 3 |
| G-q | 26; 28 | 27 | 4 / 6 | 0 | 9, 6, 8, 3 |
| G+ (§3b′) | 27; 28 | 27 | 3 / 4 | 0 | 9, 6, 9, 3 |
| G+-q | 26; 28 | 27 | 2 / 4 | 0 | 9, 6, 8, 3 |
| T (§3b′) | 46; 46 | 40 | 9 / 9 | 13 | 11, 11, 12, 12 |

- Asking for the qualifier changes nothing: 0 of 15 for both variants.
- The model reads the sentence narrowly. It calls a "no" absence-based only when a record is missing. A "no" from a rule over known facts it calls plain: in F01, G-q writes "This is not an absence-based conclusion".
- The spec qualifies every such "no". The gap is in applying the semantics, not in the wording of the request.

**Rules as a lookup tool (§3d.2).** DeepSeek, N 200.

| arm | correct; tolerant | qualifier (of 42) | sides strict (of 9) | by k: 1 / 2–3 / 4–5 / 6+ | true / absence / contested | A4 covered / missed / wrong (of 30), keys where they decide (judge) |
|---|---|---|---|---|---|---|
| G (§3b′) | 25; 26 | 27 | 2 | 9, 6, 7, 3 | 14, 0, 2 | 23 / 2 / 5 (25 / 0 / 5) |
| G-tools | 27; 29 | 27 | 3 | 9, 6, 9, 3 | 15, 0, 3 | 27 / 2 / 1 (25 / 0 / 5) |
| T (§3b′) | 46; 46 | 40 | 9 | 11, 11, 12, 12 | 15, 13, 9 | 28 / 0 / 2 (25 / 0 / 5) |

- **Family answers.** G-tools scores with G, not with T. Navigating the rule base is not what T gains. What T gains is exact evaluation.
- **A4.** G-tools is close to T. Each of its analyst sessions applies the looked-up rules to two or three named requests, and the lookup suffices for that.
  - It reports r000059 as contested with both sides in 3 of 3 sessions, citing the stated precedence ("G020 beats G017").
  - It reports 15 of 15 numeric checks.

**The arms themselves.**
- T's A4 sessions did not re-derive rules in SQL. Every SQL query flagged as inlining reads a governed table. T made 27–40 calls to `rules`, `decide` and `why` per session, and at most 9 SQL calls.
- Of T's 5 analyst turns at the limit, 4 used `summary`.

## Replications

**N 100 (§3c.3).** DeepSeek, all arms. A4 is graded with keys where they decide; the judge's first judging is in brackets.

| arm | correct; tolerant | qualifier (of 42) | sides strict (of 6) | by k: 1 / 2–3 / 4–5 / 6+ | A4 covered / missed / wrong (of 30) | manager cells at the limit |
|---|---|---|---|---|---|---|
| F | 3; 3 | 34 | 0 | 0, 3, 0, 0 | 0 / 16 / 14 (0 / 11 / 19) | 24 |
| G | 40; 41 | 36 | 5 | 9, 8, 14, 9 | 21 / 0 / 9 (20 / 0 / 10) | 0 |
| G+ | 39; 40 | 36 | 4 | 8, 7, 15, 9 | – | 0 |
| T | 47; 47 | 42 | 6 | 11, 12, 15, 9 | 25 / 3 / 2 (26 / 2 / 2) | 1 |

- G scores higher here than at N 50 or 200 because of the item mix, not N. N 100 has 2 absence items (6 cells) against 5 at N 200, and its disputes reach d 2–3, not d 4+.
- The absence result holds: G is 0 of 6, T 6 of 6.
- On contested keys G is 5 of 6 and T 6 of 6. On true keys G is 26 of 27.
- No capitalisation key is contested at N 100, so the judge grades GR7 and GR8.

**A second model (§3c.4, §3d.1).** GLM 5.3, N 200.

| arm | correct; tolerant | qualifier (of 42) | sides strict (of 9) | by k: 1 / 2–3 / 4–5 / 6+ | true / absence / contested (of 15 / 15 / 9) | A4 covered / missed / wrong (of 30), keys where they decide (judge) | $ per correct |
|---|---|---|---|---|---|---|---|
| G | 25; 27 | 27 | 3 | 9, 6, 8, 2 | 13, 0, 3 | 16 / 6 / 8 (17 / 0 / 13) | 0.026 |
| G+ | 21; 23 | 27 | 2 | 9, 6, 6, 0 | 10, 0, 2 | 23 / 5 / 2 (23 / 0 / 7) | 0.032 |
| T | 40; 40 | 42 | 9 | 11, 12, 8, 9 | 12, 11, 9 | 29 / 1 / 0 (28 / 1 / 1) | 0.012 |

- **The pattern is DeepSeek's.** G and G+ never qualify absence and lose contested sides. T qualifies every key and has every contested side.
- **GLM's T** is weaker than DeepSeek's on true keys (12 of 15) and at k 4–5.
- **A4.**
  - T covers GR7 in 3 of 3 sessions, G+ in 2 and G in 1.
  - Numeric checks reported, judge-confirmed: T 15, G 11, G+ 11 (of 15).
  - Unlike with DeepSeek, G+ does better than G here, though none of its functions reaches the families.
- **Cost.** Per correct family answer, GLM costs about 9× DeepSeek for T and 15× for G. T is the cheapest arm with either model.

## A stronger model: gpt-6.2-sol at effort medium and high (§3e.2, §3f)

- **Model.** gpt-6.2-sol on OpenAI's API. It was the strongest model on OpenAI's pricing page (read 2026-11-26) whose estimate fit the budget, and it is not deprecated.
- **Serving.** Every call was served as `gpt-6.2-sol` at the effort requested and echoed. Calls with tools go through the Responses API, statelessly, with the encrypted reasoning sent back between tool calls (`harness/openrouter.py`), because Chat Completions refuses function tools with reasoning effort for this model.
- **Scoring.** Mechanical, with no judge. gpt-6.2-sol is also the judge's model, but no judge grade enters these results.
- **Effort levels.** The model also accepts xhigh and max (OpenAI's model catalog, read 2026-11-26). The runner offers low, medium and high, so the claim holds *up to effort high*.

| effort | arm | correct; tolerant | qualifier (of 42) | absence qualified (of 15) | sides strict / tolerant (of 9) | true / defeat (of 15 / 3) | by k: 1 / 2–3 / 4–5 / 6+ | reasoning / completion tokens per cell | cost | $ per correct |
|---|---|---|---|---|---|---|---|---|---|---|
| medium | G | 26; 27 | 27 | 0 | 2 / 3 | 15 / 3 | 9, 6, 8, 3 | 28 / 282 | $0.43 | 0.017 |
| medium | G-q | 25; 25 | 27 | 0 | 1 / 1 | 15 / 3 | 9, 6, 7, 3 | 21 / 277 | $0.45 | 0.017 |
| medium | T | 48; 48 | 42 | 15 | 9 / 9 | 15 / 3 | 12, 12, 12, 12 | 10 / 255 | $0.36 | 0.008 |
| high | G | 26; 26 | 27 | 0 | 2 / 2 | 15 / 3 | 9, 6, 8, 3 | 110 / 377 | $0.49 | 0.019 |
| high | G-q | 25; 28 | 27 | 0 | 1 / 4 | 15 / 3 | 9, 6, 7, 3 | 105 / 378 | $0.48 | 0.019 |
| high | T | 48; 48 | 42 | 15 | 9 / 9 | 15 / 3 | 12, 12, 12, 12 | 60 / 349 | $0.54 | 0.011 |

For comparison, DeepSeek at N 200 (§3b′, §3c.2):
- G 25; 26, absence 0 of 15;
- G-q 26; 28, absence 0 of 15;
- T 46; 46, absence 13 of 15.

- **The closure result holds for the stronger model at both efforts.** G and G-q qualify absence in 0 of 15, with the value right in 15 of 15. T qualifies all 15 and is right on all 48 cells.
- **Values are not the gap.** G and G-q are right on every true, false-by-defeat and claim key. They lose on qualifiers and contested sides.
- **More effort buys reasoning, not closure.** Reasoning tokens rose about 4× for G and 6× for T, but stay small (60–110 per cell). The strict counts are identical to medium's.
- **Cost.** T costs the most per cell at high ($0.011 against G's $0.010), because it makes more calls and caches less (76 % of prompt tokens against 99 %). It still costs the least per correct answer.
- **Refusals.** At medium, nine cells were stopped by OpenAI's rate limit at 6 workers and re-run at 2. Refused calls cost nothing.

## Judge validity: keys against the judge (§3e.1)

The table compares keys against the judge, per reason, over both judgings, by arm. A pair is one keys grade against one judging.

| run | arm | pairs | agree |
|---|---|---|---|
| batch 1 (A1, A2; exploratory) | G / G+ / T | 56 / 56 / 56 | 0.59 / 0.89 / 0.68 |
| §3b′ (A4, N 50, 200) | F / G / T | 78 / 64 / 54 | 0.47 / 0.88 / 0.91 |
| N 100 | F / G / T | 24 / 34 / 26 | 0.58 / 0.94 / 0.92 |
| G-tools | G-tools | 36 | 0.69 |
| GLM | G / G+ / T | 52 / 44 / 40 | 0.67 / 0.64 / 0.95 |

The judge agrees with itself on 0.90–0.97 of reasons per run (kappa 0.67–0.93). I read every disagreement with the keys. They fall into four kinds:
1. **Right answer, rejected explanation.** The keys credit it and the judge does not. GLM's G and G+ report the contest with its sides but say that "across policies nothing prevails", which is false.
2. **The judge misreads a correct explanation.** DeepSeek's G (one session) and T (two), and G-tools (three), write that G020 defeats G017. That is the stated precedence and the oracle's sides, and the judge grades it wrong.
3. **Stated in words without the key's value.** The judge credits it and the keys do not: a rule restated without its number, or a contest given without all its sides. This is definitional. The keys ask for the answer, the judge for the reason.
4. **Reader limits.** Here the keys under-call.
   - A wrong count other than the naive one reads as not reported. GLM G's "0 undecided" against 3,692 is graded missed, not wrong.
   - A rule stated only in general reads as absent.
   - Unclear readings fall back to the judge.

**Finding.** The judge is reliable, but it does not measure what the keys measure.
- **What each grades.** On a mapped reason the judge grades the stated rule. The keys grade the answers the rule produces.
- **Where they agree.** Where the arm has the rules and explains them (DeepSeek G and T on A4), the two agree on 0.88–0.94 of pairs, and most remaining differences are judge errors of kind 2.
- **Where they part.** Where answers and explanations come apart (F, GLM's G and G+), agreement falls to 0.47–0.68.
- **Consequence.** Neither instrument alone grades "the reason is covered". The comparison on answers (keys) keeps T ahead of G at N 200 for both models: DeepSeek 28 against 23 covered, GLM 29 against 16.

**F's covered grades, read by hand.** All of F's keyed covered grades in A4 were coincidences, and two reader rules now exclude them:
- A table row answers for its own id. K6's 524 was read from a row headed by cc0008.
- A verdict needs a rule of the oracle's core in its block. F's "not cleared" for r000027 rests on cancellation, not G005.

After these two rules, F covers no reason by keys at any N.

**$ per covered reason** is the session cost over the covered reasons, split by who graded them (keyed; judge-graded).
- A4 at N 200, DeepSeek: G 0.0030; 0.0057, T 0.0023; 0.0083, G-tools 0.0034; 0.0050.
- A4 at N 200, GLM: G 0.0280; –, G+ 0.0221; 0.0625, T 0.0228; 0.0507.
- The halves are not comparable across arms, because which reasons the keys decide depends on N and on the reading.

## Main result

Across three models (DeepSeek v4.1 Flash, GLM 5.3, gpt-6.2-sol up to effort high) and three N, the rule arms do not differ on values. They differ on closure:
- **Absence.** A "no" that rests on absence is qualified by T in:
  - 13 of 15 (DeepSeek, N 200);
  - 6 of 6 (DeepSeek, N 100);
  - 11 of 15 (GLM);
  - 15 of 15 (gpt-6.2-sol, at medium and at high).

  G, G+, G-q, G+-q and G-tools qualify it in 0 of every count.
- **Contested sides.** They are complete for T on every contested key and every model. For G they degrade as disputes accumulate.

**Controls.**
- Asking for the qualifier does not produce it (G-q, two models, two efforts).
- Rule lookup without the evaluator does not close the gap (G-tools).
- F answers almost nothing without the rules, which shows what the material contributes.

**Cost.** T is the cheapest arm per correct family answer at N 50 and 200 with every model (DeepSeek $0.0013, GLM $0.012, gpt-6.2-sol $0.008–0.011 at N 200). At N 100, G and G+ are cheaper than T, at $0.0007 against $0.0009.

| run | cells | arms $ | judge $ |
|---|---|---|---|
| §3b′ (`b3c`) | 403 | 0.673 | 0.854 (0.340 first judging, superseded by the §3c.1 re-judging, 0.514) |
| §3c.2 (`b3d-q`) | 100 | 0.092 | – |
| §3c.3 (`b3d-n100`) | 201 | 0.327 | 0.167 |
| §3c.4 (`b3d-glm`) | 147 | 1.824 | – |
| §3d.1 (`b3d-glm-a4`) | 9 | 1.280 | 0.130 |
| §3d.2 (`b3d-gtools`) | 51 | 0.148 | 0.068 |
| §3e.2 (`b3e`) | 153 | 1.245 | – |
| §3f (`b3f`) | 144 | 1.506 | – |
| confirmatory runs | 1 208 | 7.095 | 1.219 |

- **Exploratory runs.** The pilot ($0.598, judge $0.242), batch 1 ($0.585 with its re-runs, judge $0.859), §3b ($0.110, judge $0.108) and the smoke tests ($0.072, judge $0.022) add $1.37 for arms and $1.23 for the judge.
- **Cell counts.** They include refused and truncated records that were re-run.

**Changes made after seeing results.** Each change is listed with its reason. HISTORY phases 12–21 hold the details.
1. **Forced final answer.** A turn at the call limit gets one last call with tools forbidden, so it is scored rather than left empty.
2. **T's design tools `rules` and `summary`.** Evaluation-only tools could not navigate the rule base, a gap any deployment has. They were added after the pilot and frozen before every run above. The pilot's T is reported as `T-eval`.
3. **Id resolution in `rules`, `describe` and `claims`.** T had asked for records by id and got OUT_OF_SCOPE.
4. **Gold-reason rewrites.**
   - A1 GR2, A2 GR9 and GR12 were unsatisfiable: they asked for a dated approver chain the data cannot give.
   - A4 GR6 was reworded for one dispute at N 50.
5. **Scoring fixes.**
   - The qualifier is part of correct.
   - Sides are scored strict and tolerant.
   - Numeric checks name a subject and need the judge's confirmation.
   - Superseded failed records count in cost only.
   - Gold reasons are graded from keys where keys decide.
   - A keyed verdict needs its core in its block, and a table row answers for its own id.
6. **The generator.** Interactions now grow with N, after §3b found the programmes independent. §3b is exploratory for this reason.

## Limitations

- **One generator, one domain.** Every confirmatory comparison uses `bench/gen.py`'s families over the slice's purchasing domain.
- **Synthetic data.** The bases, the requests and their outcomes are generated. Nothing is drawn from a real rule base or a real ledger.
- **Strata differ by N.** k and d are filled differently at each N (Design), so differences across N are partly differences of item mix.
- **Reader limits.** Keys read answers, not explanations.
  - A wrong count other than the naive one reads as not reported.
  - A rule stated only in general reads as absent.
  - Unclear readings fall back to the judge.
- **Judge-only reasons.** Some reasons have no keys, unread keys, or nothing contested to test at that N. They rest on the judge alone.
  - The judge is one model, which agrees with itself but agrees with the keys on only 0.47–0.95 of grades.
  - It has not been checked against hand grading. No hand grades exist.
- **Effort.** gpt-6.2-sol was tested at effort medium and high. The levels above high that it accepts (xhigh, max) were not run, so the result holds up to effort high.
- **Models.** Three models, with three repetitions each. OpenRouter routes a model to any admitted provider, and the provider is recorded per call.

# Built vs native

- **Native in SWI-Prolog:**
  - unification and backtracking for rule bodies;
  - top-down demand: `fetch` is called left to right, only for goals the question reaches;
  - `snapshot/1` isolation of the dynamic database.
- **Built:**
  - the whole defeasible layer, including the three values (no platform tried had propagation natively);
  - statuses, sides and why trees;
  - the EDN reader;
  - the memo, keyed by state;
  - the re-entry guard.
- **Kept outside the engine on purpose:** the integrity gate and the oracle, both in Python, so that the engine is checked by code it does not share.
- **What `snapshot/1` does not cover** (SWI manual §4.14.1.3):
  - global variables and flags;
  - code loaded inside the goal;
  - side effects through `py_call` (read-only SQL here; the Python cache is made thread-local by hand);
  - anything visible from before the snapshot.

  That last gap is why the memo is keyed by state. Every cache added to the evaluator carries the same obligation: isolation is a discipline here, not a property of the construct.
- **What LinkML does not cover:**
  - It validates a *converted copy*. `edn2yaml.py` is part of the trust chain, and the round-trip check guards it.
  - Two of its schema rules were silent no-ops until negative tests exposed them: `rules` without `preconditions`, and `any_of` not inherited through `is_a`.
  - Neither LinkML nor JSON Schema checks rule semantics. That is the integrity gate's job.

# Known residuals

1. **IR-005 checks existence, not scope.** It requires a completeness claim (`:closed_over :known_facts`) for a rule that rests on negation as failure. It does not check that the claim's scope covers the query, and the slice has no scope language.
2. **Aggregate latency and memory at the root.** These are out of scope by decision (Large aggregates). The root takes 108 s and 2.8 GB for 90 028 members in the default stack, and time is linear at about 1.2 ms per member.
3. **A builtin after a contested binding hides the contest** if it refutes the solution (`SEMANTICS.md`, Known limitation). No slice body has one.
4. **Propagation's cost on a dispute-heavy base is unmeasured.** The slice has five questions downstream of two root conflicts (C3/C4, R312/R314), which does not make it a dispute-heavy base.
5. **Rule classes are not deontic** (PROGRESS question 10). `:class` records a rule's inferential role, not whether it grants a permission, obligation or prohibition.
6. **`flush()` batches as `UNION ALL` when more than one filter column varies.** This is the shape behind the earlier memory blow-up (HISTORY phase 8). No slice rule produces it on a hot path, and the bench generator reports any base that would (HISTORY phase 10).
7. **Not done:** search for `resolve_term` (Lucene, HNSW). Plain matching over normalised terms and synonyms passes check 6.

# Fallback

If SWI-Prolog is refused at JPMC, the fallback is a separate Python engine written from `SEMANTICS.md` against `CONTRACT.md`.
- It must stay distinct from `reference.py`, which remains the oracle.
- It is documented only, not built.
- Everything else stays as it is: the gate, the oracle, `accept.py`, `check_why.py`, the fixtures and the DuckDB backend. The engine is the only part that would be replaced.
