# Spike v3 results: System A on Python + Prolog

Current state only. `HISTORY.md` covers how the spike got here: five platforms, reversed findings, platform lessons. The tag `spike-v3-five-platforms` holds everything that was removed.

Measured 2026-11-25 on Apple Silicon (macOS). Versions: SWI-Prolog 11.0.1, janus-swi 1.5.3, duckdb (Python) 2.0.1, LinkML 1.12.1. DuckDB is the only backend: Postgres 18 gave identical answers and was retired on 2026-11-25 (`HISTORY.md`, phase 1). The raw outputs are in `v3a-prolog/results/`. From the repo root:

```
.venv/bin/python spikes/v3/shared/reference.py                                   # keys.json (oracle)
.venv/bin/python spikes/v3/shared/accept.py    --cli spikes/v3/v3a-prolog/cli    # checks 1, 3-8; add --mutation
.venv/bin/python spikes/v3/shared/isolation.py --cli spikes/v3/v3a-prolog/cli
.venv/bin/python spikes/v3/shared/bench.py     --cli spikes/v3/v3a-prolog/cli
.venv/bin/python spikes/v3/shared/cycles_probe.py --cli spikes/v3/v3a-prolog/cli # re-entry guard, gate off
.venv/bin/python spikes/v3/shared/hyp_latency.py  --cli spikes/v3/v3a-prolog/cli
.venv/bin/python spikes/v3/v3a-prolog/linkml/build.py                            # LinkML model, negatives
```

## What System A is

- **Shape.**
  - Rules and claims are data, authored once in EDN (`shared/slice.edn`, `extension.edn`, `cycles-acyclic.edn`) and interpreted at runtime by a top-down defeasible engine.
  - Detail data stays in DuckDB. The engine reaches it only through `fetch(concept, filters)`, whose concept → SQL bindings live in the slice. No table is ever loaded.
- **Contract** (`shared/CONTRACT.md`): a JSON-lines CLI session.
  - Ops: `decide`, `claims`, `why`, `why_not`, `add`, `with_hypothesis` and `resolve_term`.
  - Answers: `ANSWER`, `CONFLICT` with sides, `UNDERDETERMINED` or `OUT_OF_SCOPE`, each with a why tree and owners.
- **Semantics** (`shared/SEMANTICS.md`): defeasible logic with team defeat and ambiguity propagation. A literal is proven, refuted or contested, and anything downstream of a contested conclusion is contested.
  - Superiority is ordered explicit → strict → authority → later `asserted_at`.
  - Functional predicates make rivals. Claims are defeasible facts gated by valid time.
  - `[:agg :sum|:count ?x [body] ?out]` aggregates over the solutions of a derived conjunction (below).
  - Every `decide` ANSWER carries a `qualifier`: `"total over known facts in declared scope"` when the answer rests on absence, else null (below).
- **Oracle.** `shared/reference.py` re-implements the semantics independently of the engine and writes `keys.json`. `check_why.py` re-derives every why tree, re-running node SQL. The mutation test (check 1 must fail on mutated keys) guards the checker itself.
- **Integrity gate** (`shared/model_check.py` through `shared/integrity.py`, IR-001a … IR-007).
  - One shared Python implementation, imported by V3a and run at load, before every `add`, and inside `with_hypothesis` against the hypothetical rule base. A violation rejects the change and leaves the state as it was.
  - Cycles are rejected, never answered. A re-entry guard in the evaluator backs this up when the gate is off.
  - One check of slice + extension + acyclic takes about 12.6 ms.

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

SWI-Prolog hosted from Python through janus. It has one evaluation mode: recursion with a memo keyed by state token.

| Part | Lines |
|---|---|
| `defeasible.pl`: store, three-valued `eval3`/`classify3`/`body3`, aggregates, superiority, re-entry guard | 362 |
| `ops.pl`: the contract ops, `contested_why`, the absence qualifier, hypotheses | 301 |
| `why.pl`: why / why_not trees | 63 |
| `edn.pl`: EDN reader (DCG) | 78 |
| `sql.py`: the `fetch` boundary (duckdb), per-thread cache | 97 |
| `host.py` + `cli`: janus host, gate calls | 72 + 4 |
| `linkml/`: `slice.yaml` schema, `edn2yaml.py`, `build.py` (docs, DDL comparison, negatives) | |

## §7 rows

| Criterion | V3a |
|---|---|
| Correctness | `accept.py` GREEN on checks 1 and 3–8 (`results/accept.txt`; check 2, the backend swap, is retired). `--mutation` fails check 1, as it must (`results/mutation.txt`). |
| Defeasible semantics | All built in `defeasible.pl`: team defeat, superiority, functional rivals, R314 incompatibility (an attacker of `approved`), aggregates over derived literals, and propagation with a `contested` why node. |
| Explanations | Complete against the keys. `check_why.py` re-verifies every tree, including `contested` nodes (`via`, `rules`, roots) and aggregate nodes (each member re-proved, the total recomputed). |
| As-of / provenance | Valid time from claim attributes (`valid_from`/`valid_to`). Assertion provenance from `asserted_by`/`asserted_at`/`recorded_at`. No transaction-time axis. |
| Adoption gate | `snapshot/1`: changes are invisible to other threads and always discarded. `isolation.py` PASS (`results/isolation-duckdb.txt`). |
| Integrity | Check 8 PASS: 9 fixtures plus the `add` and hypothesis cases, with the exact member sets above. Re-entry guard with the gate off: 2 of 2 loops named as `defeat-cycle` with their goal path, 0.8–2.2 ms (`results/guard-probe.*`). |
| Model / validation | LinkML 1.12.1 with structured rule bodies, including the `Aggregate` literal; 90/90 literals round-trip to EDN. The 15 negatives are 15/15 rejected by some layer: linkml-validate 14/15, JSON Schema 14/15, shared shape check 4/15 (`linkml/negatives.md`, `results/negatives.txt`). |
| SQL boundary | Prolog → Python (janus) → duckdb. 11.92 statements per `approved` decision (11.17 before R314 became an attacker inside `eval3`). The exhaustive set question (check 5) uses 551 bounded statements and at most 425 rows. |
| Footprint (information) | SWI-Prolog 11.0.1 (brew) plus `.venv`, 273 MB (LinkML dominates). |

**Latency** (`bench.py`: 200 `approved` decisions on seeded random requests, then the questions; the per-op `ms` from the CLI's own clock; 49/200 approved, 0 errors):

| | DuckDB |
|---|---|
| decide p50 / p95 / max (ms) | 4.89 / 10.13 / 15.5 |
| questions p50 / p95 (ms) | 1.23 / 1148 (Q46, the contested aggregate over cc0105) |
| load (ms), cold start (s) | 62, 0.13 |
| max RSS, loaded / bench (MB) | 63 / 153 |

**Hypotheses** (`hyp_latency.py`, n = 30; p50 / p95 ms of the base `decide` and of the whole `with_hypothesis` op, which includes the gate):

| | base | hypothesis |
|---|---|---|
| Q10 (withhold R313): ANSWER → CONFLICT | 0.14 / 0.15 | 0.17 / 0.20 |
| Q38 (withhold RY23): CONFLICT → ANSWER | 0.58 / 0.83 | 0.37 / 0.40 |

Bench runs drift by about ±10 % on p50, so differences smaller than that are noise.

## Benchmark preconditions (HISTORY phase 7)

**Aggregation over derived literals** (`SEMANTICS.md`, Aggregates).
- Form: `[:agg Op ?x [L1 .. Ln] ?out]`, Op `:sum` or `:count`. R120 (`approved_total`) and R121 (`approved_count`) sum or count the pending requests of a subtree whose approval is proven.
- Members are the proven solutions; refuted ones are excluded; no members gives 0. Any contested solution contests the aggregate, and its roots become the CONFLICT's sides. Every fetch inside the body is read in full, in pages of at most `fetch_limit` rows, so the member set is never truncated.
- IR-005 applies: R120/R121 are `:closed_over :known_facts`; an aggregate without either is rejected (`negative-without-completeness`).
- Questions: Q44 (cc0058, ANSWER 1512000), Q45 (leaf cc0290, count), Q46 (cc0105, CONFLICT `[[R312],[R314]]` through r000001).

**Fetch volume.** The body is evaluated set-at-a-time in rounds (`CONTRACT.md`, Aggregates): each round proves every member against the per-op cache, and its misses are fetched together, one paged statement per concept and filter shape. Measured on `[:approved_total C ?v]` at 10⁵ requests, one session per row (before → after the push-down):

| Centre (level) | Result | statements | ms | rows | max rows |
|---|---|---|---|---|---|
| cc0290 (L4) | ANSWER 32000 | 170 → 12 | 139 → 149 | 231 | 64 |
| cc0681 (L4) | CONFLICT | 212 → 12 | 204 → 174 | 270 | 65 |
| cc0058 (L3) | ANSWER 1512000 | 1034 → 12 | 960 → 799 | 1323 | 341 |
| cc0105 (L3) | CONFLICT | 1290 → 12 | 1165 → 1085 | 1715 | 451 |
| cc0018 (L2) | CONFLICT | 6631 → 24 | 6665 → 5269 | 8830 | 2398 |
| cc0002 (L1) | CONFLICT | ERROR → 95 | 25 487 | 44 444 | 10000 |
| cc0000 (L0, root) | CONFLICT | ERROR → 693 | 207 674 | | 10000 |

- The statement count is now O(concepts × rounds × pages), not O(members): 693 at the root against about 260 000 projected one at a time. No statement returns more than `fetch_limit` rows (check 5 holds).
- Latency is still linear in the members, now about 1.2 ms per pending member (Memory after the fixes). The cost has moved from SQL into the evaluator. Rules are indexed by head predicate (`rule_at/2`), because rule lookup was 17 % of the cc0002 profile.
- The root (90 028 pending) runs in SWI's default 1 GB stack: 108 s and 2.8 GB peak RSS (Memory after the fixes). It is a documented residual, not a blocker (Strategy for large aggregates: decision). Its response is 13.8 MB, of which the why tree is 0.4 MB.

**IR-007 `unsafe-aggregation`** (`SEMANTICS.md`, Aggregates). The gate rejects a `:sum` of a `:semi-additive` measure across one of the measure's parameters. That covers both a direct fetch of the measure and a predicate that carries it, as R104 carries `booked_total`. Every parameter counts as unsafe, because the slice maps no parameter to a dimension. No slice rule is rejected. The fixture RA1 sums `booked_total` over a chain of ancestors.

**Absence qualifier** (`SEMANTICS.md`, Qualifier). The qualifier is set when:
- a positive answer's why tree uses a `:closed_over` rule (as before);
- a ground `false` had no live supporter, or was defeated by an attacker whose proof uses a `:closed_over` rule;
- an open answer is `null` or `[]`.

Coverage is derived (IR-005 amended 2026-11-25). A name is covered when an in-force `[:complete "N"]` claim names it, or when it is a predicate that no claim feeds and every rule that concludes or attacks it reads only covered names. Only uncovered rules and predicates qualify an answer. In the slice only `booked_total` is covered (C10), so no base key changes. Q53–Q55 ask whether r000005 breaches a cap (`false`, with no live supporter):
- Q53, base: CLOSED;
- Q54, with `request`, `employee`, `ancestors_or_self` and `cost_centre` declared complete inside `with_hypothesis`: `null`, because `cap_breach` is now covered;
- Q55, the same without `cost_centre`: CLOSED.

Every `decide` key holds the qualifier. Keys changed when the qualifier was introduced:
- Q09, now CLOSED, by R310 and R304;
- Q18, `false` with no live supporter;
- Q47, new (`denied r000005` `false`, R309 not live);
- Q52, new (`po_issued r000006` `false`).

Q07ext stays `null`: it is `false`, defeated by R307, which is not `:closed_over`. Q26 and Q27 were removed on 2026-11-25 because they duplicated Q01 and Q09 (PROGRESS 13). Removing them and adding Q53–Q55 changed no other key.

**Downstream of real conflicts.** Two rules derive from contested literals:
- R315 `home_headroom` (`cost_centre_of` then `headroom`): Q48 withholds R313 on 15 July and gives CONFLICT `[[C3],[C4]]`, with one contested instance per claimed cost centre; Q49 is the same without the hypothesis, an ANSWER `[34000]` because R313 lets finance's C4 win;
- R316 `po_issued` (from `approved`): Q50 (r000001) gives CONFLICT `[[R312],[R314]]`; the controls Q51 (r000005, true) and Q52 (r000006, false) are qualified.

V3a matched every key without an engine change. Q48–Q52 are in checks 1 and 3.

## Memory attribution (HISTORY phase 8)

The baseline that motivated the fixes below, measured before them. One session per centre, `[:approved_total C ?v]`, 8 GB stack. A cell is one `term_size/2` word (8 bytes). SQL growth is the RSS added while DuckDB ran statements.

| | cc0018 (L2) | cc0002 (L1) | cc0000 (root) |
|---|---|---|---|
| members (pending) | 2 224 | 11 213 | 90 028 |
| memo entries | 22 962 | 115 348 | 924 846 |
| memo stored terms | 43 MB | 222 MB | 1 768 MB |
| of which the aggregate entry | 3.8 MB | 21 MB | 164 MB |
| largest groups (proven) | has_approver 9.6 MB, cap_breach 6.6 MB | has_approver 48 MB, cap_breach 32 MB | has_approver 388 MB, cap_breach 256 MB, governing_limit 215 MB |
| global stack in use (allocated) | 47 MB (67) | 172 MB (537) | 1 641 MB (2 148) |
| GC: runs, reclaimed, time | 58, 0.5 GB, 0.09 s | 79, 2.7 GB, 0.5 s | 88, 21.1 GB, 3.3 s |
| fetch cache: Prolog `fetched/4`, Python | 5 MB, 3 MB | 26 MB, 15 MB | 210 MB, 120 MB |
| SQL growth | 2.1 GB | 4.0 GB | 5.2 GB |
| peak RSS | 2.4 GB | 5.7 GB | 12.7 GB |

- **The largest single cost is DuckDB, not the memo.** `reporting_chain` has a required parameter (`$emp`), so `flush()` batches it as a UNION ALL of single-key recursive CTEs, and each copy costs about 4 MB to plan and run. One 500-copy statement adds 2.1 GB at L2; the root's five largest add 2.0, 0.8, 0.5, 0.4 and 0.3 GB. In isolation (500 employees, 2 201 rows), the UNION ALL adds 2 112 MB in chunks of 500, 805 MB in chunks of 100 and 255 MB in chunks of 25. A recursive CTE that carries the key through the recursion (`WHERE id IN (…)`) adds 10 MB for the same rows. The single-key form does not carry `$emp` through its recursion, so `flush()` cannot derive the set form from it. Each concept therefore has one SQL form that carries the key, `IN ($p)`, with a single key as a set of one (`CONTRACT.md`, Aggregates). With it, the L2 statement adds 3 MB, with the same statements and keys. The root still peaked at 12.1 GB, so its peak was not only the SQL growth.
- **Hypothesis 1 is confirmed, but the memo is not the main cost.** Proven entries hold the cells: a `none` entry is 2 cells and a proven `has_approver` is about 540. The memo is about 1.8 GB of the root's 12.7 GB.
- **Hypothesis 2 is confirmed.** At cc0002, `copy_term`, `memo/5` and `variant_hash` take about 10 % of the time. The root's global stack holds 1.6 GB in use, and GC reclaims 21 GB over the run.
- **Hypothesis 3 is confirmed, and bounded.** The aggregate entry is 164 MB at the root, while the response's why tree is 0.4 MB.
- **Time** at cc0002 (pre-index profile):
  - rule lookup (`rule/5`): 17 %;
  - fetch (`fetch_rows`, inclusive): 17 %, of which SQL is 2.4 of 24.9 s;
  - memo copy: about 10 %;
  - GC: 1.6 %.
- **Bench, 153 → 656 MB:** Q44 (cc0058) runs a 70-copy `reporting_chain` batch (+297 MB), and Q46 (cc0105) runs a 92-copy batch (+394 MB). That accounts for the rise.

## Memory after the fixes (HISTORY phase 8)

With one SQL form per concept, the rule index and the status-only memo (proofs rebuilt on demand, aggregate nodes sampled; `CONTRACT.md`, Why trees). One in-process session per centre, `[:approved_total C ?v]`, default 1 GB stack. Memo bytes are `term_size/2` cells × 8.

| Centre (level) | Result | statements | ms | peak RSS | memo entries | bytes / entry | GC |
|---|---|---|---|---|---|---|---|
| cc0290 (L4) | ANSWER | 12 | 84 | 96 MB | 590 | 60 | 2 ms |
| cc0681 (L4) | CONFLICT | 12 | 97 | 97 MB | 722 | 64 | 2 ms |
| cc0058 (L3) | ANSWER | 12 | 420 | 109 MB | 3 566 | 59 | 8 ms |
| cc0105 (L3) | CONFLICT | 12 | 521 | 111 MB | 4 619 | 58 | 10 ms |
| cc0018 (L2) | CONFLICT | 24 | 2 669 | 173 MB | 22 962 | 58 | 49 ms |
| cc0002 (L1) | CONFLICT | 95 | 13 184 | 419 MB | 115 348 | 58 | 275 ms |
| cc0000 (root) | CONFLICT | 693 | 107 566 | 2 781 MB | 924 846 | 58 | 2.1 s |

- **Memo:** about 58 bytes per entry, against about 1 900 before (root: 54 MB against 1 768 MB). The entry count is unchanged: the memo still holds a status for every literal the members reach, about 10 per member.
- **Root:** 12.7 GB → 2.8 GB, 139 → 108 s; GC reclaims 14.0 GB in 2.1 s (was 21.1 GB, 3.3 s). The 8 GB `stack_limit` is no longer needed. The set form for every parametrised concept, not only `reporting_chain`, took the root from 4.6 to 2.8 GB, L1 from 1 033 to 419 MB and L2 from 283 to 173 MB: `subtree`, `ancestors_or_self` and `request_in_subtree` had still been batched as UNION ALLs of recursive CTEs. Through the CLI the root takes 116 s and 2.7 GB. Accounted at the peak: memo 54 MB, fetch caches 330 MB (Prolog 210, Python 120); DuckDB's share was not re-measured, and the rest is not attributed by these probes.
- **Time is linear in the members:** about 1.2 ms per pending member at every level from L2 up (1.18 at cc0018, 1.18 at cc0002, 1.22 at the root).
- **Bench:** session peak 175 → 162 MB with one SQL form (241 MB with `reporting_chain`'s set form alone, 153 before aggregates); p50 and p95 unchanged within noise; hypothesis latency unchanged (Q10 and Q38).

## Strategy for large aggregates: decision (Matthias, 2026-11-25)

**Scope.** The system answers questions *about* the data: structure, meaning, classifications, relationships, claims, warrants, and how to query it (SQL help). It is not the execution path for big-data queries; users keep Genie, Cortex and plain SQL for that.

- Large aggregates at the root are therefore a documented residual, not a blocker: 108 s and 2.8 GB for 90 028 members (Memory after the fixes), against the "good enough" bar of about 10 s and 1 GB. L1 (11 213 members) takes 13 s and 0.4 GB.
- What the numbers say: about 1.2 ms per pending member at every level from L2 up, and the evaluator is about 94 % of the time (SQL 7.3 of 132 s at the root). Only taking the per-member evaluator out of the loop would meet the bar.
- No probe query is run and no SQL generator is built as an execution path. Compiling rules to SQL may return later as an *answer* ("here is the SQL that implements the rule, and the rules it rests on"), to be decided in the benchmark design.

## Design ops for the benchmark (PLAN-v3-bench-full §2, 2026-11-26)

Two ops (`CONTRACT.md`, Design ops) are T's design tools:
- `rules` lists the rule base around a predicate, term, concept, asset or goal pattern, with no evaluation.
- `summary` gives the status counts of an open goal over a domain, its contested roots and a sample.

The reference keys `summary` (Q56–Q60, five new keys in `keys.json`, `changed` unchanged at Q07 Q14); `rules` is structural and is checked against the slice by `bench/selftest.py`, not keyed. At N 200, `summary` over the 425 pending requests of cc0049 takes about 0.8 s; `rules` on a predicate with 34 concluding rules is 12.8k characters, over the 12k tool-result cap, so it narrows to a goal pattern (`[:capitalised "K01" ?a]`, 0.8k).

**Fairness note.** This change is made after the pilot. It is legitimate only because it addresses a capability gap any real deployment has (navigating the rule base), not the gold reasons, and because it is frozen before the full run. Both T versions are reported: `T-eval` (the pilot's evaluation-only tools) and `T` (with `rules` and `summary`; records carry `config.t_tools`). "Evaluation-only tools are not enough for design work" is itself a finding.

The call limit is the same for every arm; `score.py` reports the cells and turns that reach it as their own outcome, by arm (pilot: 21 of 108 turns).

## Benchmark batch 1 (PLAN-v3-bench-full §3, §3a, 2026-11-26)

DeepSeek v4.1 Flash, N 25 and 200, repetition 1, arms G, G+ and T on all 31 manager questions and A1–A3, judge `gpt-6.2-sol` at medium. 204 cells, no errors, no empty replies. Results: `bench/results/b1.jsonl.gz`, grades `b1.judge-medium.jsonl.gz`. One repetition: a signal, not a result.

§3a revised three gold reasons after the first judging (A1 GR2, A2 GR9 and GR12; `bench/tasks/A1.json`, `A2.json`), added rule and claim ids to T's `rules` and `describe`, re-ran the four T cells that had asked for a record by id (A1 at N 25 and 200; M14 and M21 at N 200, M21 wrong before, right after) and re-judged all 18 analyst sessions. The superseded T cells and grades are in `b1.pre3a.jsonl.gz` and `b1.judge-medium.pre3a.jsonl.gz`. Cost: $0.536 for the batch (estimate $1.20), $0.048 for the re-runs; judge $0.295 and then $0.281 (estimate $0.20).

Manager correct is scored as §3b′ defines it: status, value, sides and qualifier, every decide key stating its qualifier. Sides are given strict (the same id sets) and tolerant (each key side inside its own reported side, extra ids allowed); 3 of the 31 keys are CONFLICT. "Without qualifier" is the score before §3b′, kept for comparison.

| arm | N | manager correct, strict; tolerant | without qualifier | qualifier (of 25 decide) | gold reasons covered / missed / wrong (A1–A3, 34) | before §3a | turns at the call limit (manager; analyst) |
|---|---|---|---|---|---|---|---|
| G | 25 | 21; 23 | 27 | 18 | 28 / 1 / 5 | 30 / 0 / 4 | 2/31; 2/12 |
| G | 200 | 19; 20 | 25 | 18 | 30 / 1 / 3 | 30 / 0 / 4 | 4/31; 2/12 |
| G+ | 25 | 22; 23 | 28 | 19 | 29 / 1 / 4 | 29 / 0 / 5 | 1/31; 2/12 |
| G+ | 200 | 23; 25 | 28 | 20 | 30 / 2 / 2 | 28 / 2 / 4 | 1/31; 2/12 |
| T | 25 | 29; 29 | 30 | 24 | 27 / 1 / 6 | 25 / 3 / 6 | 2/31; 2/12 |
| T | 200 | 28; 28 | 29 | 24 | 29 / 1 / 4 | 23 / 2 / 9 | 1/31; 2/12 |

Against the pilot (same model; the pilot's 10 manager questions, gold reasons judged at medium before §3a):

| arm | manager N 25 / 200 (of 10) | gold covered N 25 / 200 |
|---|---|---|
| G, pilot → batch 1 | 5 / 6 → 7 / 6 | 26 / 23 → 30 / 30 |
| T-eval (pilot) → T | 7 / 8 → 10 / 8 | 25 / 18 → 25 / 23 |

- The qualifier is where the arms differ on manager questions: G and G+ miss it in 5–7 of 25 (almost all under-qualified: a "no" or a total over the known facts given as plain), T in 1. Strict sides lose G and G+ every CONFLICT key at N 25 (0 of 3; tolerant 1–2), T none. Before §3b′ the qualifier was not part of correct, and M16's key (Q16, a why_not) stated none and was read as "not qualified"; it is qualified, and only T at N 200 says so.
- Judge noise: of the 162 grades whose session and reason text did not change, 7 flipped between the two judgings (4 %). Differences of one or two reasons per cell are within it.
- Every gold reason is now covered by some arm at some N. Before §3a, A2 GR9 and GR12 were wrong in all six cells: they asked for a historical approver chain, which the data cannot give (`emp.manager` is undated). Revised, they are covered in 3 and 2 cells.
- T's gap on analyst gold reasons closed: 27 and 29 against G's 28 and 30 (judge). Graded from keys where keys decide (§3e.1), T has 28 and 29, G 29 and 26. Half of it is the revised texts; the A1 re-run adds the rest (A1 at N 200: 7 by-id calls, all answered, where before 3 returned OUT_OF_SCOPE; GR2, GR5, GR7 and GR11 now covered, GR9 lost).
- The forced final answer (§1.4) changed G most: every turn at the limit now has a reply, and G's A1 at N 200 went from 7/13 to 13/13. The pilot's "G degrades at N 200" does not recur in batch 1.
- T uses the design tools (319 `rules`, 121 `summary` calls; none over the result cap). A2 at N 200: 12 `decide` calls instead of 238.
- Every arm reaches the analyst call limit in 2 of 12 turns; manager turns at the limit are mostly wrong for G (0/6 correct) and mostly right for G+ and T (4/5).

## Rule count on the generated families (PLAN-v3-bench-full §3b, 2026-11-26)

DeepSeek v4.1 Flash, N 50 and 200, repetition 1, arms G, G+ and T, on the family questions F01–F12 and the analyst task A4 (`bench/questions/family.json`, `bench/tasks/A4.json`, one variant per N). 78 cells, no failed cell, $0.110. Three cells were refused by the budget's worst-case reservations at 6 workers before any call; they were run on resume at 2 workers, and their refusal records stay in the file. Judge `gpt-6.2-sol` at medium, twice: $0.075 and $0.033 (score.py's judge line sums every grades file since §3b′). Results: `bench/results/b3b.jsonl.gz`, grades `b3b.judge-medium.jsonl.gz` and `.2.jsonl.gz`. One repetition: a signal, not a result.

Scored as in batch 1 (§3b′: qualifier in correct; strict and tolerant sides agree on every family question here).

| arm | N | family correct (of 12) | without qualifier | qualifier (of 10) | correct at k = 1 / 2 / 3 | A4 gold covered / missed / wrong | A4 numbers reported (of 3) |
|---|---|---|---|---|---|---|---|
| G | 50 | 8 | 11 | 7 | 7/7, 0/3, 1/2 | 8 / 0 / 1 (of 9) | 3 |
| G | 200 | 10 | 12 | 8 | 8/9, 1/2, 1/1 | 8 / 0 / 3 (of 11) | 3 |
| G+ | 50 | 9 | 12 | 7 | 7/7, 1/3, 1/2 | 8 / 0 / 1 | 3 |
| G+ | 200 | 10 | 12 | 8 | 8/9, 1/2, 1/1 | 8 / 0 / 3 | 3 |
| T | 50 | 11 | 12 | 9 | 7/7, 2/3, 2/2 | 8 / 0 / 1 | 3 |
| T | 200 | 12 | 12 | 10 | 9/9, 2/2, 1/1 | 11 / 0 / 0 | 3 |

- Manager accuracy does not move with N (k only reaches 3). With the qualifier, T is 23 of 24 and G and G+ 18 and 19; their misses are at k ≥ 2 (dated limit versions and clearance, unqualified "no"s). Without it, 71 of 72 were correct. k is only 1–3, because the generator keeps programmes independent (PLAN-v3-bench-full Decisions, §3b finding): what N adds is distraction, not interaction. Without the qualifier, G's only miss (F07 at N 50) answers an owner dispute without superiority as a plain yes or no rather than contested. The qualifier misses (G and G+ on F02, F04, F06 and F08) leave out the limit version or the conflict note while the answer is right; T misses one.
- A4 does not separate the arms at N 50 (8 of 9 each). At N 200, G and G+ each have 3 wrong reasons and T has none. By the judge, the reason that separates them is GR6 (§3b's task has no subject per check, so it is not graded from keys, §3e.1): under K01 (no superiority) a request is contested, and G and G+ answer "expensed" or "not capitalised" in 3 of 4 sessions, while T reports the conflict in both. GR2 (a request outside P01's category is outside the limit: false, not unknown) is wrong for G at both N and for G+ at N 200; they answer null or "not covered". All three numeric checks are reported in all six sessions; none gives the naive limit or the count without the exception. N 200's variant has two more reasons (on claims), so the comparison across N is not on the same items.
- The judge agrees with itself: 60 of 60 grades on §3b, kappa 1.00; 198 of 204 on batch 1's 18 sessions judged a second time, kappa 0.90 (second judging $0.283). Batch 1's two judgings give G 28 and 26 at N 25, and 30 and 28 at N 200, against 28 at both N in the table above; the other arms differ by at most one reason. Mechanical checks and the judge agree 24 of 24 on §3b.

## Interacting rules and the floor arm (PLAN-v3-bench-full §3b′, 2026-11-26)

DeepSeek v4.1 Flash, N 50 and 200, 3 repetitions on all items. Manager arms are G, G+, T and F, the floor (data model and `sql`, no rules); analyst arms are G, T and F. The items are the family questions F01–F16, stratified by k, and A4. A4 asks about the same nine requests at every N, while N adds disputes over P01's category (1 at N 50, 4 at N 200, with superiority across disputes) and sub-programme levels (2 and 4). The run has 402 cells and cost $0.674. One F cell failed the truncation check and was re-run on resume. The judge, `gpt-6.2-sol` at medium, graded A4 twice after GR6 was reworded for a single dispute (§3c.1; $0.514); it agrees with itself on 0.96 of 171 reasons (kappa 0.93). Results: `bench/results/b3c.jsonl.gz`, grades `b3c.rejudge-medium.jsonl.gz` and `.2.jsonl.gz`. The expected outcomes were recorded in the plan's Decisions before the run.

Family questions: 48 cells per arm and N (16 items × 3). Correct means status, value, sides and qualifier; tolerant sides are given after the `;`.

| arm | N | correct | status | qualifier | contested keys: sides strict / tolerant (of 9) | by k: 1 / 2–3 / 4–5 / 6+ |
|---|---|---|---|---|---|---|
| F | 50 | 0; 0 | 6 | 24/39 | 0 / 0 | 0/12, 0/30, 0/6, – |
| F | 200 | 6; 6 | 12 | 27/42 | 0 / 0 | 0/12, 0/12, 3/12, 3/12 |
| G | 50 | 33; 33 | 44 | 27/39 | 6 / 6 | 9/12, 18/30, 6/6, – |
| G | 200 | 25; 26 | 46 | 27/42 | 2 / 3 | 9/12, 6/12, 7/12, 3/12 |
| G+ | 50 | 30; 30 | 42 | 27/39 | 3 / 3 | 9/12, 15/30, 6/6, – |
| G+ | 200 | 27; 28 | 46 | 27/42 | 3 / 4 | 9/12, 6/12, 9/12, 3/12 |
| T | 50 | 43; 43 | 48 | 35/39 | 9 / 9 | 10/12, 27/30, 6/6, – |
| T | 200 | 46; 46 | 48 | 40/42 | 9 / 9 | 11/12, 11/12, 12/12, 12/12 |

By the key's outcome, correct, at N 50 / N 200. Each cell reads 15/15 for true, 12/15 for false by absence, 3/3 for false by defeat, 9/9 for contested, and 9/6 for claims:

| arm | true | false (absence) | false (defeat) | contested | claim |
|---|---|---|---|---|---|
| G | 15 / 14 | 0 / 0 | 3 / 3 | 6 / 2 | 9 / 6 |
| G+ | 15 / 15 | 0 / 0 | 3 / 3 | 3 / 3 | 9 / 6 |
| T | 14 / 15 | 8 / 13 | 3 / 3 | 9 / 9 | 9 / 6 |
| F | 0 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

- The expected outcomes hold. (b) T's difference is closure. G and G+ never qualify a "no" that rests on absence: 0 of 27 at both N, and in 25 of 27 misses the value is right and only the qualifier is missing. T qualifies 21 of 27. On contested keys, G's sides get worse with the dispute count: strict 6 of 9 at N 50 (one dispute), 2 of 9 at N 200 (d 4–7). T has all 18. (c) There is no accuracy difference on values: G's status is right in 90 of 96, its value wrong on 1 of 30 true keys, and false by defeat is 6 of 6 for every rule arm. (a) G does not stay flat by k (9/12 at k 1, 3/12 at k 6+ at N 200), but the fall is closure, not wrong values. The k ≥ 6 slots at N 200 are contested or absence keys, and G misses their sides and qualifiers. (d) F answers almost nothing: 6 of 96, all "true" keys at N 200, which it answered "yes" without the rules.
- G+ (trusted functions) is not better than G here: none of its functions covers the families.
- A4, gold reasons covered / missed / wrong, graded from keys where keys decide and by the first judging elsewhere (§3e.1); the judge alone in brackets (first judging); 9 reasons per session at N 50 and 10 at N 200, 3 sessions:

| arm | N 50 (of 27) | N 200 (of 30) | numeric checks reported, judge-confirmed (of 15) |
|---|---|---|---|
| F | 4 / 7 / 16 (0 / 3 / 24) | 5 / 10 / 15 (0 / 5 / 25) | 0 and 0 |
| G | 14 / 0 / 13 (14 / 0 / 13) | 23 / 2 / 5 (25 / 0 / 5) | 13 and 15 |
| T | 25 / 0 / 2 (25 / 0 / 2) | 28 / 0 / 2 (25 / 0 / 5) | 15 and 15 |

- GR7 (precedence, and contested where no superior rule holds), graded from keys (§3e.1). At N 200, T reports r000059 as contested with both sides in 3 of 3 sessions; G does so in 1, gives a plain value in 1, and is unclear in 1. The judge's "T too misreads which rule survives" does not hold: on reading, T's explanations match the stated precedence (G020 over G017), and the judge marked them wrong. At N 50, GR7 is not tested by keys: r000059 is not contested there (8,000 is in no capitalise range), and G's answers for both requests are right. The judge's "G wrong in 6 of 6" at N 50 is about G's general rule ("blocked by G010" for the band where both rules hold), not about any reported answer. Counts per reason are over both judgings. GR2 (outside P01's category the limit answer is false, not unknown) is wrong for G in 10 of 12 and for T in 3 of 12. At N 50, G gets GR8 (the chain) wrong in 4 of 6 by the judge and in 2 of 2 read by keys (1 unclear); at N 200 the judge covers it in 6 of 6, while by keys G gives the U04 contest without all its sides in 2 of 3 (missed). GR9 at N 50 is graded by the judge only (wrong in 4 of 6). GR6 (every policy's rules take part), reworded for one dispute at N 50: by the judge (untested by keys at N 50) T 4 of 6 and G 0 of 6; at N 200 by keys T 3 of 3, G 1 covered and 1 wrong (r000059 "not capitalised"), where the judge has G 6 of 6.
- G and T report the numeric checks, including the chain counts (N 200: 2,050 cleared and 3,692 contested under U04); none gives the naive value. A mechanical grade counts only in a block or under a heading that names the check's subject, and only where the judge's grade of that check agrees (§3c.1). Neither condition alone separates F: its 8,000 is r000228's amount, which equals the limit, and its 0 is a row count, both next to the subject. With the judge's confirmation, F reports none: the judge contradicts 12 of its 16 mechanical "reported" or "naive" grades, and the other 4 are naive limits. G at N 50 misses K13 once and once gives a K13 figure the judge does not credit. Mechanical and judge agree on 67 of 90 numeric grades; every difference but two is F's.
- Cost per correct family answer at N 200: T $0.0013, G $0.0017. Calls at the limit: F reaches it in 33 of 96 manager cells, T in 3, G in none.
- Three repetitions on fixed items make this the first confirmatory comparison. It still covers one model and one generator; the strata at N 50 stop at k 4.

## Variants, N 100 and a second model (PLAN-v3-bench-full §3c.2–4, §3d, 2026-11-26)

Same items, scoring and judge as §3b′ (family F01–F16 and A4, 3 repetitions, A4 judged twice). The arms were frozen before these runs. Results: `bench/results/b3d-q`, `b3d-n100`, `b3d-glm`, `b3d-gtools`, `b3d-glm-a4` (`.jsonl.gz`, grades `.judge-medium.jsonl.gz` and `.2.jsonl.gz`). Refused or truncated records that were re-run count in cost only, shown as (+n).

**The qualifier sentence (§3c.2, confirmatory; outcomes recorded before the run).** G-q and G+-q are G and G+ with one added sentence: "For every no, say whether it rests only on not finding something in the data." DeepSeek, N 200, family, of 48. Cost: $0.093.

| arm | correct; tolerant | qualifier (of 42) | contested sides strict / tolerant (of 9) | false by absence (of 15) | by k: 1 / 2–3 / 4–5 / 6+ |
|---|---|---|---|---|---|
| G (§3b′) | 25; 26 | 27 | 2 / 3 | 0 | 9, 6, 7, 3 |
| G-q | 26; 28 | 27 | 4 / 6 | 0 | 9, 6, 8, 3 |
| G+ (§3b′) | 27; 28 | 27 | 3 / 4 | 0 | 9, 6, 9, 3 |
| G+-q | 26; 28 | 27 | 2 / 4 | 0 | 9, 6, 8, 3 |
| T (§3b′) | 46; 46 | 40 | 9 / 9 | 13 | 11, 11, 12, 12 |

- The closure result stands: telling the model to qualify absence changes nothing. The plan's alternative ("the tags were nudged") does not apply.
- The sentence only restates the task's own definition of `qualified` (`bench/run.py`, task instructions). The model reads it narrowly. It calls a "no" absence-based only when a record is missing. A "no" from a rule over known facts it calls plain: in F01, G-q writes "This is not an absence-based conclusion". The spec qualifies every such "no" ("total over known facts in declared scope", SEMANTICS.md). The gap is in applying the semantics, not in the wording of the request.

**N 100 (§3c.3, replication).** DeepSeek, all arms. Family of 48. A4 has 3 sessions of 10 reasons; the first judging is given, the second in brackets. Cost: $0.327, judge $0.167. Self-agreement 0.96, kappa 0.93.

| arm | correct; tolerant | qualifier (of 42) | sides strict (of 6) | by k: 1 / 2–3 / 4–5 / 6+ | A4 covered / missed / wrong (of 30): keys where they decide (judge) | manager cells at the limit |
|---|---|---|---|---|---|---|
| F | 3; 3 | 34 | 0 | 0, 3, 0, 0 | 1 / 15 / 14 (0 / 11 / 19) | 24 |
| G | 40; 41 | 36 | 5 | 9, 8, 14, 9 | 21 / 0 / 9 (20 / 0 / 10) | 0 |
| G+ | 39; 40 | 36 | 4 | 8, 7, 15, 9 | – | 0 |
| T | 47; 47 | 42 | 6 | 11, 12, 15, 9 | 25 / 3 / 2 (26 / 2 / 2) | 1 |

- G scores higher at N 100 than at N 50 or 200. This is the item mix, not an effect of N. N 100 has 2 absence items (6 cells) against 5 at N 200, and its disputes reach d 2–3 rather than d 4+ (strata below).
- The absence result holds: G is 0 of 6 on false by absence, T 6 of 6. On contested keys G is 5 of 6, T 6 of 6. On true keys G is 26 of 27.
- A4: at N 100 no capitalisation key is contested, so GR7 and GR8 are not tested by keys and keep the judge's grades: G wrong on both in 6 of 6 gradings, T covering GR7 in 4 of 6 and GR8 in 1 of 6 (missed 3, wrong 2). With keys where they decide and the judge elsewhere (GR2, GR7, GR8, GR10), G and T cover 21 and 25 of 30, F 1 (judge alone: 20, 26, 0).
- Numeric checks reported, judge-confirmed: G 14, T 15, F 0 (of 15).

**A second model (§3c.4 and §3d.1, replication).** GLM 5.3, N 200, arms G, G+ and T. Family: 3 repetitions, $1.82. A4: 3 repetitions, $1.28, judge $0.130. Self-agreement 0.97, kappa 0.91.

| arm | correct; tolerant | qualifier (of 42) | sides strict (of 9) | by k: 1 / 2–3 / 4–5 / 6+ | true / absence / contested (of 15 / 15 / 9) | A4 covered / missed / wrong (of 30): keys where they decide (judge) | $ per correct |
|---|---|---|---|---|---|---|---|
| G | 25; 27 | 27 | 3 | 9, 6, 8, 2 | 13, 0, 3 | 16 / 6 / 8 (17 / 0 / 13) | 0.026 |
| G+ | 21; 23 | 27 | 2 | 9, 6, 6, 0 | 10, 0, 2 | 23 / 5 / 2 (23 / 0 / 7) | 0.032 |
| T | 40; 40 | 42 | 9 | 11, 12, 8, 9 | 12, 11, 9 | 29 / 1 / 0 (28 / 1 / 1) | 0.012 |

- The pattern is DeepSeek's. G and G+ never qualify absence and lose contested sides. T qualifies every key and has every contested side.
- GLM's T is weaker than DeepSeek's on true keys (12 of 15) and at k 4–5. In A4, by keys (§3e.1), T covers GR7 in 3 of 3 sessions, G+ in 2 (1 contested without all sides), G in 1 (1 missed, 1 wrong); the judge has G and G+ wrong in 6 of 6 gradings. G and G+ are wrong on GR2 in 6 and 4 of 6 (judge only). G is wrong on GR8 in 2 of 3 by keys; on GR10 (the count under U04) it misses in 3 of 3, where one session says "0 undecided": a wrong count other than the naive one reads as not reported, so keys under-count G's wrong reasons here. T misses GR2 in 3 (judge). Numeric checks reported, judge-confirmed: T 15, G 11, G+ 11 (of 15). Unlike DeepSeek, G+ does better than G here (23 against 16 covered; wrong 2 against 8), though none of its functions covers the families.
- Per correct family answer GLM costs about 9× DeepSeek for T ($0.012 against $0.0013) and 15× for G ($0.026 against $0.0017); T is the cheapest arm with either model.

**Rules as a lookup tool (§3d.2, confirmatory; outcomes recorded before the run).** G-tools has G's material without the rules and claims sections. It looks them up with T's `rules` tool, which evaluates nothing, and applies them itself with `sql`. DeepSeek, N 200. Cost: $0.148, judge $0.068. Self-agreement 0.90, kappa 0.67.

| arm | correct; tolerant | qualifier (of 42) | sides strict (of 9) | by k: 1 / 2–3 / 4–5 / 6+ | true / absence / contested | A4 covered / missed / wrong (of 30): keys where they decide (judge) |
|---|---|---|---|---|---|---|
| G (§3b′) | 25; 26 | 27 | 2 | 9, 6, 7, 3 | 14, 0, 2 | 23 / 2 / 5 (25 / 0 / 5) |
| G-tools | 27; 29 | 27 | 3 | 9, 6, 9, 3 | 15, 0, 3 | 27 / 2 / 1 (25 / 0 / 5) |
| T (§3b′) | 46; 46 | 40 | 9 | 11, 11, 12, 12 | 15, 13, 9 | 28 / 0 / 2 (25 / 0 / 5) |

- On family answers G-tools scores with G, not with T. Being able to navigate the rule base is not what T gains. What T gains is exact evaluation, so the engine is needed. On A4's reasons graded from keys, G-tools (27 / 2 / 1) is close to T (28 / 0 / 2), not to G (23 / 2 / 5): its one analyst session per turn applies the looked-up rules to two or three named requests, which the lookup suffices for.
- G-tools reports r000059 as contested with both sides in 3 of 3 sessions (GR7 by keys, §3e.1), where the judge has it wrong in 5 of 6 gradings. Its explanation ("G020 beats G017") is the stated precedence. It reports 15 of 15 numeric checks and cites all 102 of its refs. 3 of 48 manager cells reach the call limit.

**Strata by N (§3d.3).** Family items, of 16:

| N | k 1 / 2–3 / 4–5 / 6+ | d 0 / 1 / 2–3 / 4+ |
|---|---|---|
| 50 | 4 / 10 / 2 / 0 | 11 / 5 / 0 / 0 |
| 100 | 4 / 4 / 5 / 3 | 10 / 0 / 6 / 0 |
| 200 | 4 / 4 / 4 / 4 | 9 / 0 / 0 / 7 |

Each N fills different strata: d 1 occurs only at N 50, and d 4+ only at N 200. A comparison across N therefore compares item sets as well as N.

**Checks on the arms (§3d.3).**
- G+'s functions do not reach the families. `gplus.py` has five functions (request_status, approved_total, spend, role_limit, breaching_requests), all over the slice rules R1xx–R3xx. On the family items G+ is G with unused tools, as its scores show.
- T's A4 sessions (§3b′) did not re-derive rules in SQL. Every SQL query flagged as inlining reads a governed table (cap, vendor_status, emp violation). T made 27–40 calls to rules, decide and why per session, and at most 9 SQL calls. Of the 5 turns that reached the limit, 4 used `summary`. T was not enumerating in SQL in place of `summary`.

## Gold reasons graded from keys (PLAN-v3-bench-full §3e.1, 2026-11-26)

**Method.** A gold reason is decided by the checks whose `gr` names it (`decided_by` in the task data; generated for A4 by `bench/gen_items.py`, hand-written for A1–A3). It is graded from the session's answers for those checks:
- covered when every one is reported correctly;
- wrong when one is reported wrongly: the naive value, a plain value for a contested key, or the other value;
- missed otherwise, including a contested key reported without all its sides.

Numbers are read as before (subject-named, block-scoped). A decide check is read by a scoped prose reader (`bench/score.py`, `read_decide`). It reads only the subject's own line, table cell or section, using a per-check vocabulary (`says`, generated). Where the reader finds both values and no wrong one, the reason is unclear and keeps the judge's grade (counted as fallback). No judge call was made; the judge's grades stand beside the keys grades and are not used for them.

Some reasons stay with the judge, labelled per task and N in the report:
- no keys: caveats and labels (A1 GR6, GR11, GR12; A2 GR9–GR12; A3 GR3, GR6; A4 GR2);
- unread: keys no reader reads, i.e. claim standings, every A3 key, and counts under 10 (A2 GR1, GR5, GR6, GR8; A4 GR9 at N 50, GR10 at N 100);
- untested: reasons that say something is contested, where no key is contested at that N (A4 GR6 and GR7 at N 50; GR7 and GR8 at N 100). A4's requests are picked once, at N 200. At N 50, r000059 (8,000) is in no capitalise range, so a yes or no reported for it cannot show whether a session treats the both-ranges band as contested.

**Re-scored.** Every analyst run was re-scored: batch 1, §3b′ (b3c, with the re-judged grades), N 100, G-tools and GLM. §3b is not re-scored, because its task (the old generator) has no subject per check, and the tables above say so where they cite it.

Keys against the judge, per reason and both judgings, by arm. A pair is one keys grade against one judging:

| run | arm | pairs | agree |
|---|---|---|---|
| batch 1 (A1, A2) | G / G+ / T | 56 / 56 / 56 | 0.59 / 0.89 / 0.68 |
| §3b′ (A4, N 50, 200) | F / G / T | 82 / 64 / 54 | 0.50 / 0.88 / 0.91 |
| N 100 | F / G / T | 24 / 34 / 26 | 0.58 / 0.94 / 0.92 |
| G-tools | G-tools | 36 | 0.69 |
| GLM | G / G+ / T | 52 / 44 / 40 | 0.67 / 0.64 / 0.95 |

I read every disagreement. They fall into four kinds:
1. **Right answer, rejected explanation; keys credit it and the judge does not.** This covers all 18 of F's covered|wrong pairs in §3b′. F has no rules, gets K4, K5 and K11 right, and explains them with invented gates ("the emergency flag has no rule attached"). GLM's G and G+ give a per-policy view or say that "across policies nothing prevails" (false: G017 prevails over G016) and still report the contest with its sides. In A1, GR9 is credited because the snapshot cost centre coincides with the dated one for e077.
2. **The judge misreads a correct explanation.** DeepSeek G (one session) and T (two), and G-tools (three), write that G020 defeats G017 and that G021 survives. That is the stated precedence and the oracle's sides, and the judge grades it wrong.
3. **Stated in words without the key's value; the judge credits it and the keys do not.** Batch 1's missed|covered pairs are a rule restated without its number, and A4 GR8 is the U04 contest given without all its sides (partial, so missed). These are definitional: the keys ask for the answer, the judge for the reason.
4. **Reader limits; the keys under-call.** A wrong count other than the naive one reads as not reported: GLM G's "0 undecided" against 3,692 is graded missed, not wrong. A rule stated only in general, with no per-subject answer, reads as absent (GLM G, session 3: "capitalised iff amount ≥ 45,000"). Unclear readings fall back to the judge: K11 at N 200 in most rule-arm sessions, where "cleared" and "not cleared" are both said of r000092 at different levels.

**Validity finding.** The judge is reliable (self-agreement 0.90–0.97) but does not measure the same thing as the keys. On a mapped reason it grades the stated rule; the keys grade the answers the rule produces. Where the arm has the rules and explains them (DeepSeek G and T on A4), the two agree on 0.88–0.94 of pairs, and most remaining differences are judge errors of kind 2. Where answers and explanations come apart (F, GLM's G and G+, A1's coincident cost centre), agreement falls to 0.50–0.68. Neither instrument alone grades "the reason is covered". The arm comparison on answers (keys) keeps T ahead of G at N 200 for both models (DeepSeek 28 against 23 covered, GLM 29 against 16). The comparison on explanations (judge) is the one in which the GR7 claims were made. Those claims are replaced above.

## State of the benchmark (PLAN-v3-bench-full §3c.5, 2026-11-26)

| run | items | models, N | reps | status |
|---|---|---|---|---|
| pilot | M01–M10, A1–A3 | DeepSeek; 25, 200 | 1 | exploratory |
| batch 1 (§3, §3a) | M01–M31, A1–A3 | DeepSeek; 25, 200 | 1 | exploratory |
| §3b | F01–F12, A4 (old generator) | DeepSeek; 50, 200 | 1 | exploratory |
| §3b′ | F01–F16, A4 | DeepSeek; 50, 200 | 3 | confirmatory (outcomes recorded before) |
| §3c.2 G-q, G+-q | F01–F16 | DeepSeek; 200 | 3 | confirmatory (outcomes recorded before) |
| §3d.2 G-tools | F01–F16, A4 | DeepSeek; 200 | 3 | confirmatory (outcomes recorded before) |
| §3c.3 | F01–F16, A4 | DeepSeek; 100 | 3 | replication |
| §3c.4, §3d.1 | F01–F16; A4 | GLM 5.3; 200 | 3 | replication |

**Main result.** Across two models and three N, the rule arms do not differ on values. They differ on closure:
- a "no" that rests on absence is qualified by T in 13 of 15 (DeepSeek N 200), 6 of 6 (N 100) and 11 of 15 (GLM), and by G, G+, G-q, G+-q and G-tools in 0 of every count;
- contested sides are complete for T on every contested key, and degrade for G as disputes accumulate.

The two controls rule out the obvious explanations:
- asking for the qualifier does not produce it (G-q);
- giving G the rule lookup without the evaluator does not close the gap (G-tools).

F answers almost nothing without the rules, which shows what the material contributes.

**Changes made after seeing results**, each with its reason:
1. Forced final answer (§1.4). A turn at the call limit gets one last call with tools forbidden, so it is scored rather than left empty.
2. T's design tools `rules` and `summary` (§2). Evaluation-only tools could not navigate the rule base, a gap any deployment has. The pilot's T is reported as `T-eval`.
3. Id resolution in `rules`, `describe` and `claims` (§3a). T asked for records by id and got OUT_OF_SCOPE. Four cells were re-run.
4. Gold-reason rewrites:
   - A1 GR2, A2 GR9 and GR12 (§3a): unsatisfiable, since they asked for a dated approver chain the data cannot give;
   - A4 GR6 (§3c.1): worded for one dispute at N 50.
5. Scoring fixes:
   - the qualifier is part of correct, and every decide key states one (§3b′);
   - strict and tolerant sides (§3b′);
   - numeric checks name a subject and need the judge's confirmation (§3c.1; F's coincidental 8,000 and 0);
   - failed records superseded by a re-run count in cost only (§3d.3);
   - gold reasons graded from keys where keys decide them, the judge elsewhere and on unclear readings (§3e.1; the judge had graded explanations, which on GR7 it misread).
6. The generator (§3b′). Interactions now grow with N, after §3b found programmes independent. §3b is exploratory for this reason.

**Open:**
- every confirmatory comparison uses one generator;
- the judge is one model, not yet checked against hand grading (`bench/grading/grades.json`); against keys it agrees on 0.50–0.95 of reason grades by arm (§3e.1), and its errors on GR7 were found by reading;
- keys read answers, not explanations, and a wrong count other than the naive one reads as not reported (§3e.1).

## Built vs native

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
- **Kept outside the engine on purpose:** the integrity gate and the oracle, both Python, so that the engine is checked by code it does not share.
- **What `snapshot/1` does not cover** (SWI manual §4.14.1.3):
  - global variables and flags;
  - code loaded inside the goal;
  - side effects through `py_call`, which are read-only SQL here; the Python cache is thread-local by hand;
  - anything visible from before the snapshot.

  The memo is keyed by state for that last reason. Every cache added to the evaluator carries the same obligation: it is a discipline, not a property of the construct.
- **What LinkML does not cover:**
  - It validates a *converted copy*. `edn2yaml.py` is part of the trust chain, and the round-trip check guards it.
  - Two of its schema rules were silent no-ops until negative tests exposed them: `rules` without `preconditions`, and `any_of` not inherited through `is_a`.
  - Neither LinkML nor JSON Schema checks rule semantics. That is the integrity gate's job.

## Known residuals

1. **IR-005 checks existence, not scope.** It requires a completeness claim (`:closed_over :known_facts`) for a rule that rests on negation as failure, but it does not check that the claim's scope covers the query. The slice has no scope language.
2. **Aggregate latency and memory at the root**, out of scope by decision (Strategy for large aggregates: decision): 108 s and 2.8 GB for 90 028 members, in the default stack; time is linear at about 1.2 ms per member (Memory after the fixes).
3. **A builtin after a contested binding hides the contest** if it refutes the solution (`SEMANTICS.md`, Known limitation). No slice body has one.
4. **Propagation's cost on a dispute-heavy base is unmeasured.** The slice now has five questions downstream of two root conflicts (C3/C4, R312/R314), not a dispute-heavy base.
5. **Rule classes are not deontic** (PROGRESS question 10). `:class` records a rule's inferential role, not whether it grants a permission, obligation or prohibition.
6. **`flush()` batches as `UNION ALL` when more than one filter column varies**, the shape behind the earlier memory blow-up (HISTORY phase 8). No slice rule produces it on a hot path; the bench generator reports any base that would (HISTORY phase 10).
7. **Not done:** search for `resolve_term` (Lucene, HNSW). Plain matching over normalised terms and synonyms passes check 6.

## Fallback

If SWI-Prolog is refused at JPMC, the fallback is a separate Python engine written from `SEMANTICS.md` against `CONTRACT.md`. It must stay distinct from `reference.py`, which remains the oracle. It is documented only, not built. Everything else stays as it is: the gate, the oracle, `accept.py`, `check_why.py`, the fixtures and the DuckDB backend. The engine is the only part that would be replaced.
