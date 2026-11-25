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
- **Integrity gate** (`shared/model_check.py` through `shared/integrity.py`, IR-001a … IR-006).
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

## Benchmark preconditions (`PLAN-v3-preconditions.md` §2)

**Aggregation over derived literals** (`SEMANTICS.md`, Aggregates).
- Form: `[:agg Op ?x [L1 .. Ln] ?out]`, Op `:sum` or `:count`. R120 (`approved_total`) and R121 (`approved_count`) sum or count the pending requests of a subtree whose approval is proven.
- Members are the proven solutions; refuted ones are excluded; no members gives 0. Any contested solution contests the aggregate, and its roots become the CONFLICT's sides. A truncated fetch inside the body is an ERROR, not a qualified total.
- IR-005 applies: R120/R121 are `:closed_over :known_facts`; an aggregate without either is rejected (`negative-without-completeness`).
- Questions: Q44 (cc0058, ANSWER 1512000), Q45 (leaf cc0290, count), Q46 (cc0105, CONFLICT `[[R312],[R314]]` through r000001).

**Fetch volume.** The inner body is evaluated one solution at a time: one `approved` proof per pending member. Measured on `[:approved_total C ?v]` at 10⁵ requests:

| Centre (level) | Result | ms | statements | rows | max rows |
|---|---|---|---|---|---|
| cc0290 (L4) | ANSWER 32000 | 139 | 170 | 214 | 53 |
| cc0681 (L4) | CONFLICT | 204 | 212 | 252 | 65 |
| cc0058 (L3) | ANSWER 1512000 | 960 | 1034 | 1265 | 337 |
| cc0105 (L3) | CONFLICT | 1165 | 1290 | 1618 | 439 |
| cc0018 (L2) | CONFLICT | 6665 | 6631 | 8406 | 2224 |
| cc0002 (L1), cc0000 (L0) | ERROR | | | 10000 | `request_in_subtree` truncated at `fetch_limit` |

Cost is linear, about 2.9 statements and 3 ms per pending member. Every statement stays bounded (check 5 holds), but the root (90 028 pending) would need about 260 000 statements and 270 s, and its member fetch exceeds `fetch_limit`.

*Push-down (proposed, not implemented):* evaluate the body set-at-a-time. Fetch the members once, then prove `approved` for all of them with one batched fetch per concept (an `IN` list or a join on the member query), so the statement count is O(number of concepts) rather than O(members). Strict conditions expressible in SQL (category, amount thresholds) go into the subtree query itself.

**Integrity candidate (proposed for the ledger, no id).** Aggregating a `:semi-additive` measure across one of its `:unsafe_dims` is rejected. No slice rule does this today, so nothing changes.

**Absence qualifier** (`SEMANTICS.md`, Qualifier). The qualifier is set when:
- a positive answer's why tree uses a `:closed_over` rule (as before);
- a ground `false` had no live supporter, or was defeated by an attacker whose proof uses a `:closed_over` rule;
- an open answer is `null` or `[]`.

An in-force `[:complete "P"]` claim on the goal's predicate removes it from a negative answer. Every `decide` key now holds the qualifier. Keys that changed: Q09 (now CLOSED, by R310/R304); Q18 (false with no live supporter); Q47 is new (`denied r000005` false, R309 not live); Q52 is new (`po_issued r000006` false). Q07ext (false, defeated by R307, which is not `:closed_over`) stays null. No question reaches the completeness exception; it was checked with a probe claim only.

**Downstream of real conflicts.** Two rules derive from contested literals:
- R315 `home_headroom` (`cost_centre_of` then `headroom`): Q48 withholds R313 on 15 July and gives CONFLICT `[[C3],[C4]]`, with one contested instance per claimed cost centre; Q49 is the same without the hypothesis, an ANSWER `[34000]` because R313 lets finance's C4 win;
- R316 `po_issued` (from `approved`): Q50 (r000001) gives CONFLICT `[[R312],[R314]]`; the controls Q51 (r000005, true) and Q52 (r000006, false) are qualified.

V3a matched every key without an engine change. Q48–Q52 are in checks 1 and 3.

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
2. **Aggregates are evaluated one member at a time.** The cost is linear in the members, and subtrees at L1 and above exceed `fetch_limit` (ERROR). The push-down above is not built.
3. **A builtin after a contested binding hides the contest** if it refutes the solution (`SEMANTICS.md`, Known limitation). No slice body has one.
4. **Propagation's cost on a dispute-heavy base is unmeasured.** The slice now has five questions downstream of two root conflicts (C3/C4, R312/R314), not a dispute-heavy base.
5. **Rule classes are not deontic** (PROGRESS question 10). `:class` records a rule's inferential role, not whether it grants a permission, obligation or prohibition.
6. **Not done:** search for `resolve_term` (Lucene, HNSW). Plain matching over normalised terms and synonyms passes check 6.

## Fallback

If SWI-Prolog is refused at JPMC, the fallback is a separate Python engine written from `SEMANTICS.md` against `CONTRACT.md`. It must stay distinct from `reference.py`, which remains the oracle. It is documented only, not built. Everything else stays as it is: the gate, the oracle, `accept.py`, `check_why.py`, the fixtures and the DuckDB backend. The engine is the only part that would be replaced.
