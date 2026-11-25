# Spike v3 progress (branch spike/v3)

Newest first. `HISTORY.md` holds the earlier phases. `RESULTS.md` describes the current state.

## Status

- [x] Pruning to Python + Prolog (2026-11-25, `PLAN-v3-housekeeping.md` at tag `spike-v3-housekeeping`):
  - tagged `spike-v3-five-platforms`, then deleted V3b–V3e, V3a's WFS mode, the blocking semantics, `cycles.edn`, `SEMANTICS-cycles.md` and the executed plans (each removal is listed in the plan's Decisions);
  - wrote `HISTORY.md`;
  - rewrote RESULTS to the current state.
  - Gate: keys byte-identical; V3a GREEN 1–8; `--mutation` fails check 1; isolation PASS on DuckDB and Postgres; negatives 15/15; bench on both backends; guard probe 2/2 (`v3a-prolog/results/`).
- [x] Repo-wide inventory (2026-11-25): approved and executed (`PLAN-v3-preconditions.md` §1.1); summarised in the root `HISTORY.md`.
- [x] Postgres retired, `.venv` cleaned (2026-11-25, `PLAN-v3-preconditions.md` §1.2–1.3). Gate on DuckDB: keys byte-identical; GREEN 1, 3–8; `--mutation` fails check 1; isolation PASS; negatives 15/15; bench 0 errors; guard probe 2/2.
- [ ] Benchmark preconditions (`PLAN-v3-preconditions.md` §2): aggregation over derived literals, the qualifier on answers resting on absence, questions downstream of real conflicts.

## Questions for Matthias

1. ~~Tooling: Postgres via brew services; the leftover V3e packages in `.venv`~~: answered 2026-11-25 by `PLAN-v3-preconditions.md` §1.2–1.3. The service is stopped, not uninstalled; to remove it, run `brew uninstall postgresql@18`, then delete `/opt/homebrew/var/postgresql@18`. The V3e packages and psycopg are gone from `.venv`.
   - Still to do by hand: the session's permission check refused deleting the untracked local copies `results/*.jsonl`, which are byte-identical to the `.gz` files, and the untracked `__pycache__` directories. To delete them, run `rm results/*.jsonl; find . -path ./.venv -prune -o -name __pycache__ -type d -exec rm -rf {} +`.
2. ~~Framing of the recommendation (shape vs stack)~~: answered 2026-11-25 by the platform decision, Python + Prolog (`HISTORY.md`, Decision).
3. ~~Optional search (Scriptum/Lucene, HNSW) for `resolve_term`~~: folded into the platform decision 2026-11-25. Not part of v3; listed under RESULTS "Not done".
5. ~~Tie-break between the stacks~~: answered 2026-11-25 by the platform decision.
10. Rule classes and deontic rules (RESULTS, residual 5). The `:class` labels record a rule's inferential role, not whether it grants a permission.
    - R311 (`auto_approved`, "without further checks") is a policy permission. R312 (`auto_approved` → `approved`) is an inferential entitlement.
    - R301 was "may approve" (`entitlement`) in `rules/rules.yaml` and became the `material_inference` `has_approver` in the slice.
    - Should deontic rules enter as their own kind, either a `:modality` (permission / obligation / prohibition) beside `:class` or a separate record type issued by an authority? Should R301 go back to a permission?
    - **Open, deferred** with the vocabulary work.
