# Spike v3 progress (branch spike/v3)

Newest first. `HISTORY.md` holds the earlier phases. `RESULTS.md` describes the current state.

## Status

- [x] Pruning to Python + Prolog (2026-11-25; HISTORY phase 6, tag `spike-v3-housekeeping`).
- [x] Inventory executed, Postgres retired, benchmark preconditions, PROGRESS 11–15 (2026-11-25; HISTORY phase 7, tag `spike-v3-preconditions`).
- [x] Memory and aggregate cost (2026-11-25; HISTORY phase 8, tag `spike-v3-memory`).
- [ ] One SQL form per concept (`PLAN-v3-sqlform.md`). Scope decided: the system answers questions about the data, not big-data queries, so the root aggregate is a documented residual (RESULTS, Strategy for large aggregates: decision).

## Questions for Matthias

Open questions only; answered ones are in `HISTORY.md` with their phase.

1. **By hand (tooling).** Postgres is stopped, not uninstalled: to remove it, run `brew uninstall postgresql@18`, then delete `/opt/homebrew/var/postgresql@18`. The session's permission check refused deleting the untracked local copies `results/*.jsonl`, which are byte-identical to the `.gz` files, and the untracked `__pycache__` directories. To delete them, run `rm results/*.jsonl; find . -path ./.venv -prune -o -name __pycache__ -type d -exec rm -rf {} +`.
10. Rule classes and deontic rules (RESULTS, residual 5). The `:class` labels record a rule's inferential role, not whether it grants a permission.
    - R311 (`auto_approved`, "without further checks") is a policy permission. R312 (`auto_approved` → `approved`) is an inferential entitlement.
    - R301 was "may approve" (`entitlement`) in `rules/rules.yaml` and became the `material_inference` `has_approver` in the slice.
    - Should deontic rules enter as their own kind, either a `:modality` (permission / obligation / prohibition) beside `:class` or a separate record type issued by an authority? Should R301 go back to a permission?
    - **Open, deferred** with the vocabulary work.
