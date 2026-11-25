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
| `defeasible.pl`: store, three-valued `eval3`/`classify3`/`body3`, superiority, re-entry guard | 317 |
| `ops.pl`: the contract ops, `contested_why`, hypotheses | 290 |
| `why.pl`: why / why_not trees | 63 |
| `edn.pl`: EDN reader (DCG) | 78 |
| `sql.py`: the `fetch` boundary (duckdb), per-thread cache | 97 |
| `host.py` + `cli`: janus host, gate calls | 72 + 4 |
| `linkml/`: `slice.yaml` schema, `edn2yaml.py`, `build.py` (docs, DDL comparison, negatives) | |

## §7 rows

| Criterion | V3a |
|---|---|
| Correctness | `accept.py` GREEN on checks 1 and 3–8 (`results/accept.txt`; check 2, the backend swap, is retired). `--mutation` fails check 1, as it must (`results/mutation.txt`). |
| Defeasible semantics | All built in `defeasible.pl`: team defeat, superiority, functional rivals, R314 incompatibility, and propagation with a `contested` why node. |
| Explanations | Complete against the keys. `check_why.py` re-verifies every tree, including `contested` nodes (`via`, `rules`, roots). |
| As-of / provenance | Valid time from claim attributes (`valid_from`/`valid_to`). Assertion provenance from `asserted_by`/`asserted_at`/`recorded_at`. No transaction-time axis. |
| Adoption gate | `snapshot/1`: changes are invisible to other threads and always discarded. `isolation.py` PASS (`results/isolation-duckdb.txt`). |
| Integrity | Check 8 PASS: 9 fixtures plus the `add` and hypothesis cases, with the exact member sets above. Re-entry guard with the gate off: 2 of 2 loops named as `defeat-cycle` with their goal path, 0.8–2.2 ms (`results/guard-probe.*`). |
| Model / validation | LinkML 1.12.1 with structured rule bodies; 81/81 literals round-trip to EDN. The 15 negatives are 15/15 rejected by some layer: linkml-validate 14/15, JSON Schema 14/15, shared shape check 4/15 (`linkml/negatives.md`, `results/negatives.txt`). |
| SQL boundary | Prolog → Python (janus) → duckdb. 11.17 statements per `approved` decision. The exhaustive set question (check 5) uses 551 bounded statements and at most 425 rows. |
| Footprint (information) | SWI-Prolog 11.0.1 (brew) plus `.venv`, 273 MB (LinkML dominates). |

**Latency** (`bench.py`: 200 `approved` decisions on seeded random requests, then the questions; the per-op `ms` from the CLI's own clock; 49/200 approved, 0 errors):

| | DuckDB |
|---|---|
| decide p50 / p95 / max (ms) | 4.57 / 10.12 / 15.6 |
| questions p50 / p95 (ms) | 0.67 / 10.7 |
| load (ms), cold start (s) | 58, 0.13 |
| max RSS, loaded / bench (MB) | 63 / 135 |

**Hypotheses** (`hyp_latency.py`, n = 30; p50 / p95 ms of the base `decide` and of the whole `with_hypothesis` op, which includes the gate):

| | base | hypothesis |
|---|---|---|
| Q10 (withhold R313): ANSWER → CONFLICT | 0.13 / 0.14 | 0.16 / 0.18 |
| Q38 (withhold RY23): CONFLICT → ANSWER | 0.58 / 0.79 | 0.35 / 0.39 |

Bench runs drift by about ±10 % on p50, so differences smaller than that are noise.

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
2. **Aggregation over derived literals is unspecified.**
   - Measures aggregate fetched rows only.
   - A measure over a contested binding (Y5e, Q41) is contested as a whole, which is an approximation.
   - The semantics of `sum`/`count` over derived, possibly contested, literals is not yet written.
3. **The qualifier is attached to positive answers only.** `"total over known facts in declared scope"` is attached when the value is not `false`, `null` or `[]`. A negative `ANSWER` that rests on absence carries no qualifier, although it rests on the same closed-world assumption.
4. **The three v3 preconditions** (Tolaria note `v3-next-decisions`): questions downstream of real conflicts (the slice has almost none, so propagation's cost on a dispute-heavy base is unmeasured); aggregation over derived literals (2); the qualifier on answers resting on absence (3).
5. **Rule classes are not deontic** (PROGRESS question 10). `:class` records a rule's inferential role, not whether it grants a permission, obligation or prohibition.
6. **Not done:** search for `resolve_term` (Lucene, HNSW). Plain matching over normalised terms and synonyms passes check 6.

## Fallback

If SWI-Prolog is refused at JPMC, the fallback is a separate Python engine written from `SEMANTICS.md` against `CONTRACT.md`. It must stay distinct from `reference.py`, which remains the oracle. It is documented only, not built. Everything else stays as it is: the gate, the oracle, `accept.py`, `check_why.py`, the fixtures and the DuckDB backend. The engine is the only part that would be replaced.
