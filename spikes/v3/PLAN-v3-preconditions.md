# Spike v3 addendum — inventory cleanup, DuckDB only, preconditions for the benchmark

Plan for Claude Code, 2026-11-25 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. This plan replaces `PLAN-v3-housekeeping.md`: harvest its Decisions into `spikes/v3/HISTORY.md` (one short entry), then delete it.

## 1 Housekeeping (approved by Matthias)

1. **Execute `INVENTORY.md`** as proposed. Write the root `HISTORY.md` from its skeleton (v1, v2, v3 spike; `spikes/v3/HISTORY.md` stays as the detailed chapter). `REWORK.md` stays until the paper is consolidated, as proposed. Then remove `INVENTORY.md` (summarised in the root HISTORY).
2. **Postgres retired.** Backend independence is shown (HISTORY: identical answers on DuckDB and Postgres 18). From now on DuckDB only:
   - `accept.py` check 2 (backend swap) is retired; `isolation.py` and `bench.py` run on DuckDB only; remove the Postgres config paths and `psycopg` use.
   - Update `CLAUDE.md` (gate, data rules) and `CONTRACT.md` accordingly.
   - Stop the service: `brew services stop postgresql@18` (or the installed formula name). Do not uninstall; tell Matthias the command to remove it if he wants.
3. **`.venv`:** remove `clingo`, `xclingo`, `clingexplaid` and any other package only V3e used. Check nothing remaining imports them.

Gate (`CLAUDE.md`, now DuckDB only): keys byte-identical, all remaining checks green.

## 2 Preconditions for the benchmark

The real v3 benchmark needs three things the slice cannot yet express or exercise. Spec first (`SEMANTICS.md`, `CONTRACT.md`), then `reference.py` (independent), then V3a. Each its own commit; each changed key listed with its reason.

### 2.1 Aggregation over derived literals

Today measures sum table rows through SQL bindings only; "the total of approved requests", where approval is derived, cannot be stated.
- Add a body form for aggregation over the solutions of a derived conjunction, e.g. `[:agg :sum ?amount [goal ...] ?out]` (also `:count`; others only if needed). Choose the exact syntax; record it.
- Semantics (propagation): members are the solutions whose conjunction is proven; refuted solutions are excluded; if any candidate solution is contested, the aggregate is contested, with the roots of the contested members as sides. Empty set gives 0 for `:sum`/`:count`.
- An aggregate is an aggregation for IR-005: it needs `:completeness` or `:closed_over :known_facts`.
- Bounded fetch must still hold (check 5). If aggregating over derived literals forces fetching too many rows at 10⁵ requests, record the numbers; do not hide it. Propose (do not implement) a push-down if needed.
- Questions: the total of *approved* requests in a cost-centre subtree, (a) where every member's approval is proven, (b) where one member's approval is contested (e.g. through the R314 approved/denied incompatibility), expected CONFLICT. Do not define `term:committed_spend`: it is the slice's deliberately undecided term.
- Integrity candidate, propose only (Matthias keeps the ledger): aggregating a `:semi-additive` measure across one of its `:unsafe_dims` is rejected.

### 2.2 Qualifier on answers that rest on absence

IR-005 currently qualifies positive answers only. A negative answer from failure to prove ("no approved request exists") is the closed-world case the qualifier exists for.
- `decide` sets `qualifier: "total over known facts in declared scope"` whenever the answer depends on absence: a `:not` that succeeded, or an ANSWER false because no supporter was live, unless a completeness claim covers the predicate. Positive answers keep the existing rule.
- Specify it in `SEMANTICS.md`; list every key whose qualifier changes, with the reason.

### 2.3 Questions downstream of real conflicts

Propagation changed no base question, because no base rule derives anything from a contested literal. Add rules and at least three base-state questions whose derivation passes through a real root conflict of the slice (C3/C4 on `cost_centre_of` where R313 is not in force, R314's approved/denied conflict, or a new owned dispute that is plausible in procurement). Expected: CONFLICT with the root's sides, or ANSWER where superiority resolves it. They become part of checks 1–3.

## 3 RESULTS and PROGRESS

RESULTS: current state only; add the aggregation form, the absence qualifier, the new questions, fetch volume for 2.1, and the integrity candidate. PROGRESS: status, and questions for Matthias.

## Decisions

(Executor: append dated entries — what was decided, why.)

- **2026-11-25 §1.1 tag.** The tag `spike-v3-housekeeping` is at 86924f8, the last commit that holds `INVENTORY.md` and `PLAN-v3-housekeeping.md`; the root HISTORY and `spikes/v3/HISTORY.md` name it.
- **2026-11-25 §1.1 harvest.** The housekeeping plan's Decisions went into `spikes/v3/HISTORY.md` phase 6 (commit range, line counts by pointer to the tag, the f-string defect, what was kept). The root `HISTORY.md` adds a "Repo inventory" entry in place of `INVENTORY.md`.
- **2026-11-25 §1.1 inventory.**
  - README: the "under construction" line now points to the finished v2 paper, and the README introduces the v3 spike, `HISTORY.md` and `spikes/v3/`.
  - `requirements.txt` gains the spike's four packages with the versions it was developed on.
  - Not done: deleting the 24 untracked plain `results/*.jsonl` copies and the untracked `__pycache__` directories. I checked that each copy is byte-identical to its `.gz`, but the session's permission check refused the `rm`. They are untracked, so the repo is unaffected; the command is in PROGRESS.
- **2026-11-25 §1.2 Postgres retired.**
  - Removed: the Postgres paths in `accept.py` (check 2, `CFG["postgres"]`, `Env`'s psycopg branch), `sql.py` (connection, `%s` parameters, `to_char`), `gen.py` (`load_pg`, the cross-backend `--check`, which now prints the DuckDB counts and fingerprints), and the `--backend` options of `bench.py`, `isolation.py`, `hyp_latency.py` and `cycles_probe.py`. `CFG` is now a single DuckDB config.
  - Check numbers stay as they were: check 2 is marked retired rather than renumbered, because RESULTS, HISTORY and the PLAN texts cite the checks by number. `--only` defaults to `1345678`.
  - The config keeps `"backend": "duckdb"` (CONTRACT); `sql.py` rejects any other value.
  - Kept: the `@iso()` macro in the slice SQL. It still separates the slice from the dialect, at no cost.
  - Kept: `build.py`'s `gen-sqlddl --dialect postgresql`. That is LinkML's DDL output for the comparison with `gen.py`, not a backend, and LinkML has no DuckDB dialect.
  - Deleted: `results/{bench,hyp-latency}-postgres.json` and `isolation-postgres.txt` (at tag `spike-v3-housekeeping`). HISTORY phase 1 records the backend independence.
  - `brew services stop postgresql@18` was run. The command to remove it completely is in PROGRESS.
- **2026-11-25 §1.3 `.venv`.**
  - Uninstalled with `uv pip uninstall`: clingo 5.8.0, clingexplaid 1.5.1, clorm 1.6.3, xclingo 2.0b24, musclingo 0.1.2, clingraph 1.2.6, and their only dependents' dependencies cffi 2.1.1, pycparser 3.12 and bidict 0.24.1 (each checked with `pip show`: required by nothing else). I also uninstalled psycopg and psycopg-binary 3.3.9 (§1.2).
  - Kept: graphviz (LinkML needs it); jinja2, jsonschema and networkx (dependencies of LinkML as well).
  - `pip check` is clean, and no tracked Python file outside `.venv` imports any removed package.
- **2026-11-25 §1 gate (DuckDB).**
  - `keys.json` is byte-identical.
  - `accept.py` is GREEN on checks 1 and 3–8, and `--mutation` fails check 1 (Q27, R312).
  - `isolation.py` PASS; negatives 15/15; guard probe 2/2.
  - bench: 0 errors, 11.17 SQL per decide, p50 4.57 ms.
- **2026-11-25 §2.1 syntax.** `[:agg Op ?x [L1 .. Ln] ?out]` with Op `:sum` or `:count`: the plan's example form, with the body as a list so that it is a conjunction. No other op was needed. LinkML gains an `Aggregate` literal class and an `AggregateOp` enum.
- **2026-11-25 §2.1 R314 inside `eval3`.** R314 used to be checked after the fact. To make an aggregate member contested by it, R314 became an attacker of `approved` in `eval3` (for `approved` only, since it is the only `:incompatible` rule). This cost 11.17 → 11.92 SQL per decide.
- **2026-11-25 §2.1 rules.** R120 `approved_total` and R121 `approved_count`, `recorded_at` 2026-09-14 like the rest of the slice, `:closed_over :known_facts`. Their key core is the aggregate rule only ([R120]), since the members' proofs vary.
- **2026-11-25 §2.1 the proven part.** A contested aggregate still binds ?out to the total over the proven members. That value appears only in the `contested` node's goal (Q46: 1526000), never as an answer.
- **2026-11-25 §2.1 truncation.** A truncated fetch inside the aggregate body is an ERROR, scoped to fetches made while the body is evaluated. Edge case: a memo hit from an earlier truncated fetch outside the aggregate would not be seen as truncated. No question reaches it.
- **2026-11-25 §2.1 qualifier ids.** The set of closed rules is derived from `:closed_over` in the slice, not listed in the reference.
- **2026-11-25 §2.1 limitation kept.** A builtin after a contested binding is evaluated on the bound value (`SEMANTICS.md`, Known limitation); no slice body has one, so it is documented, not fixed.
- **2026-11-25 §2.1 `excluded` dropped.** CONTRACT's aggregate node does not list the refuted bindings: `check_why.py` recomputes the total from the members, which is enough to verify it.
- **2026-11-25 §2.1 fetch volume.** Measured at L4–L0 (RESULTS). It is linear in the members, and L1/L0 exceed `fetch_limit`. The push-down is proposed in RESULTS, not built.
- **2026-11-25 §2.2 every key holds the qualifier.** Every `decide` key now holds `qualifier`, null or the string, and `:check_qualifier` is retired. A per-question flag would have left most negative answers unchecked.
- **2026-11-25 §2.2 false by defeat.** It is qualified only when the winning attacker's proof uses a `:closed_over` rule, and V3a inspects the proof of the smallest winning attacker only. In the slice the defeater R307 is not `:closed_over`, so Q07ext stays null.
- **2026-11-25 §2.2 open answers.** An open `null` or `[]` is always qualified: no binding is known.
- **2026-11-25 §2.2 the exception.** Completeness covers by predicate name: an in-force `[:complete "P"]` claim on the goal's predicate. No slice question reaches it (C10 names `booked_total`, which is never absent); a probe claim confirmed it in V3a, and the probe was not committed.
- **2026-11-25 §2.2 keys changed.** Q09 → CLOSED (R310/R304 were already closed, but the key was not checked); Q18 → CLOSED (false, no live supporter); Q47 added (`denied r000005`). Every other `decide` key gained `qualifier: null`.
- **2026-11-25 §2.3 rules.** R315 `home_headroom` (finance, from `cost_centre_of` and `headroom`), the base-slice counterpart of RY56; R316 `po_issued` (procurement, from `approved`). Both are defeasible, with no `:functional` declaration (like RY56, so the contested instances do not rival each other). `home_headroom` has mode `--`, because `cost_centre_of` is claims-only and so enumerable; the model check inferred it and rejected `+-`.
- **2026-11-25 §2.3 questions.** Q48 (CONFLICT through C3/C4, R313 withheld), Q49 (ANSWER, resolved by R313), Q50 (CONFLICT through R312/R314). The controls are Q51 (true, qualified) and Q52 (false, R316 not live, qualified). No existing key changed. V3a needed no change.

