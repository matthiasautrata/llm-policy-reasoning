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
- The root (90 028 pending) now runs in SWI's default 1 GB stack: 110 s and 4.6 GB peak RSS (Memory after the fixes). Its response is 13.8 MB, of which the why tree is 0.4 MB.

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

- **The largest single cost is DuckDB, not the memo.** `reporting_chain` has a required parameter (`$emp`), so `flush()` batches it as a UNION ALL of single-key recursive CTEs, and each copy costs about 4 MB to plan and run. One 500-copy statement adds 2.1 GB at L2; the root's five largest add 2.0, 0.8, 0.5, 0.4 and 0.3 GB. In isolation (500 employees, 2 201 rows), the UNION ALL adds 2 112 MB in chunks of 500, 805 MB in chunks of 100 and 255 MB in chunks of 25. A recursive CTE that carries the key through the recursion (`WHERE id IN (…)`) adds 10 MB for the same rows. The single-key form does not carry `$emp` through its recursion, so `flush()` cannot derive the set form from it. The set form is therefore declared as data: `reporting_chain` carries a `:batch_sql` (`CONTRACT.md`, Aggregates). With it, the L2 statement adds 3 MB, cc0018 peaks at 0.49 GB and the bench at 241 MB, with the same statements and keys. The root still peaks at 12.1 GB, so its peak is not the SQL growth.
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

With `:batch_sql`, the rule index and the status-only memo (proofs rebuilt on demand, aggregate nodes sampled; `CONTRACT.md`, Why trees). One in-process session per centre, `[:approved_total C ?v]`, default 1 GB stack. Memo bytes are `term_size/2` cells × 8.

| Centre (level) | Result | statements | ms | peak RSS | memo entries | bytes / entry | GC |
|---|---|---|---|---|---|---|---|
| cc0290 (L4) | ANSWER | 12 | 80 | 103 MB | 590 | 60 | 2 ms |
| cc0681 (L4) | CONFLICT | 12 | 96 | 104 MB | 722 | 64 | 2 ms |
| cc0058 (L3) | ANSWER | 12 | 417 | 135 MB | 3 566 | 59 | 7 ms |
| cc0105 (L3) | CONFLICT | 12 | 514 | 134 MB | 4 619 | 58 | 9 ms |
| cc0018 (L2) | CONFLICT | 24 | 2 634 | 283 MB | 22 962 | 58 | 48 ms |
| cc0002 (L1) | CONFLICT | 95 | 13 179 | 1 033 MB | 115 348 | 58 | 259 ms |
| cc0000 (root) | CONFLICT | 693 | 109 768 | 4 634 MB | 924 846 | 58 | 2.2 s |

- **Memo:** about 58 bytes per entry, against about 1 900 before (root: 54 MB against 1 768 MB). The entry count is unchanged: the memo still holds a status for every literal the members reach, about 10 per member.
- **Root:** 12.7 GB → 4.6 GB, 139 → 110 s; the global stack in use 1 641 → 249 MB; GC reclaims 13.9 GB in 2.2 s (was 21.1 GB, 3.3 s). The 8 GB `stack_limit` is no longer needed. Accounted at the peak: memo 54 MB, global stack 249 MB, fetch caches 330 MB (Prolog 210, Python 120), DuckDB 672 MB. The remaining 3 GB or so is not attributed by these probes; the likely candidates are the transient findall copies of the 90 028 solutions per round and allocator retention after GC.
- **Time is linear in the members:** about 1.2 ms per pending member at every level from L2 up (1.18 at cc0018, 1.18 at cc0002, 1.22 at the root).
- **Bench:** session peak 241 → 175 MB (was 153 before aggregates), p50 and p95 unchanged within noise; hypothesis latency unchanged (Q10 and Q38).

## Strategy for large aggregates: proposal (`PLAN-v3-memory.md` §5, for Matthias to decide)

The bar, for information: the root under about 10 s and under 1 GB.

**Where §4 leaves it.** The root takes 110 s and 4.6 GB: 11× over on time and 4.6× over on memory. L1 (11 213 members, 13 s, 1.0 GB) is already just over the bar. Option 1, stop, does not meet it.

**The deciding numbers.**
- *Per-member cost:* 1.2 ms. The bar needs 0.11 ms, about 11× less, at 90 028 members.
- *Where the time goes:* SQL is about 6 % at the root (7.3 of 132 s over 693 statements, measured before §2; 2.4 of 24.9 s at cc0002). About 94 % is the evaluator: about 10 memoised literals per member, each classified for supporters, attackers and superiority.
- *Memory:* the memo is no longer the cost (54 MB). What remains scales with members times literals: the fetch caches, the per-round solution lists and the GC churn (13.9 GB reclaimed).

**Options.**
- **2. Compile aggregate bodies to SQL (hybrid).** This is the option the numbers point to: it is the only one that takes the per-member evaluator out of the loop.
  - The body of `approved_total` is the approval chain R304–R316 over a subtree. As one generated statement, it is a few joins and anti-joins over 10⁵ requests. Its parts are `reporting_chain` (whose set form already runs 1 000 employees in 0.15 s), limits, the vendor status and a status column for the three values.
  - Estimate: well under 10 s and under 1 GB at the root. DuckDB already reads everything the root needs in 7.3 s of SQL across 693 paged statements, and one set-based statement would not materialise the members in Prolog.
  - What it costs: a generator from the rules to SQL for the stratified fragment these bodies use (negation, team defeat, superiority as anti-joins, `as_of` and withheld ids as parameters). Dialects would come through SQLGlot. Explanations would come from supporter and attacker id columns that Prolog rehydrates, as `hydrate/4` already does from ids. The compiled path must reproduce `reference.py`'s keys under the same gate, so every slice body under an aggregate needs the full semantics, including the contested value.
  - Effort: the largest of the three. The risk is in claims (R313 authority, later-same-asserter) and in propagating contested values in SQL.
- **3. Bottom-up in Prolog.** Compute the body predicate for all members once per op and state, then aggregate. It removes the top-down overhead (guard, memo lookups, per-literal `findall`), but each member still needs its own defeasible classification.
  - Estimate: 2–4× from avoiding repeated lookups, which leaves the root at roughly 30–55 s. It does not reach the bar unless the classification itself becomes set-at-a-time, and at that point it is option 2 written in Prolog.

**Recommendation.** Option 2, first target `approved_total`. Before building the generator, first measure one hand-written probe query (scratch only, not in the repo, never an engine path) against the root's member set. That probe confirms the "well under 10 s" estimate, and the estimate is the number this choice rests on.

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
2. **Aggregate latency and memory at the root.** After the memory fixes, 110 s and 4.6 GB for 90 028 members, in the default stack; time is linear at about 1.2 ms per member (Memory after the fixes). The remedy is for Matthias to choose (Strategy for large aggregates).
3. **A builtin after a contested binding hides the contest** if it refutes the solution (`SEMANTICS.md`, Known limitation). No slice body has one.
4. **Propagation's cost on a dispute-heavy base is unmeasured.** The slice now has five questions downstream of two root conflicts (C3/C4, R312/R314), not a dispute-heavy base.
5. **Rule classes are not deontic** (PROGRESS question 10). `:class` records a rule's inferential role, not whether it grants a permission, obligation or prohibition.
6. **Not done:** search for `resolve_term` (Lucene, HNSW). Plain matching over normalised terms and synonyms passes check 6.

## Fallback

If SWI-Prolog is refused at JPMC, the fallback is a separate Python engine written from `SEMANTICS.md` against `CONTRACT.md`. It must stay distinct from `reference.py`, which remains the oracle. It is documented only, not built. Everything else stays as it is: the gate, the oracle, `accept.py`, `check_why.py`, the fixtures and the DuckDB backend. The engine is the only part that would be replaced.
