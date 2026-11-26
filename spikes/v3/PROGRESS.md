# Spike v3 progress (branch spike/v3)

Newest first. `HISTORY.md` holds the earlier phases. `RESULTS.md` describes the current state.

## Status

- [x] Pruning to Python + Prolog (2026-11-25; HISTORY phase 6, tag `spike-v3-housekeeping`).
- [x] Inventory executed, Postgres retired, benchmark preconditions, PROGRESS 11–15 (2026-11-25; HISTORY phase 7, tag `spike-v3-preconditions`).
- [x] Memory and aggregate cost (2026-11-25; HISTORY phase 8, tag `spike-v3-memory`).
- [x] One SQL form per concept; scope: the system answers questions about the data, the root aggregate is a documented residual (2026-11-25; HISTORY phase 9, tag `spike-v3-sqlform`).
- [x] Benchmark build; pilot estimate over $3, not run (2026-11-25; HISTORY phase 10, tag `spike-v3-bench`).
- [ ] Benchmark hardening, endpoints, smoke tests, pilot (`PLAN-v3-bench-run.md`).

## Questions for Matthias

Open questions only; answered ones are in `HISTORY.md` with their phase.

10. Rule classes and deontic rules (RESULTS, residual 5). The `:class` labels record a rule's inferential role, not whether it grants a permission.
    - R311 (`auto_approved`, "without further checks") is a policy permission. R312 (`auto_approved` → `approved`) is an inferential entitlement.
    - R301 was "may approve" (`entitlement`) in `rules/rules.yaml` and became the `material_inference` `has_approver` in the slice.
    - Should deontic rules enter as their own kind, either a `:modality` (permission / obligation / prohibition) beside `:class` or a separate record type issued by an authority? Should R301 go back to a permission?
    - **Open, deferred** with the vocabulary work.
