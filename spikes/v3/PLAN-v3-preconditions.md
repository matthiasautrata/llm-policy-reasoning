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

