# Spike v3 progress (branch spike/v3)

Newest first. `HISTORY.md` holds the earlier phases. `RESULTS.md` describes the current state.

## Status

- [x] Pruning to Python + Prolog (2026-11-25, `PLAN-v3-housekeeping.md`):
  - tagged `spike-v3-five-platforms`, then deleted V3b–V3e, V3a's WFS mode, the blocking semantics, `cycles.edn`, `SEMANTICS-cycles.md` and the executed plans (each removal is listed in the plan's Decisions);
  - wrote `HISTORY.md`;
  - rewrote RESULTS to the current state.
  - Gate: keys byte-identical; V3a GREEN 1–8; `--mutation` fails check 1; isolation PASS on DuckDB and Postgres; negatives 15/15; bench on both backends; guard probe 2/2 (`v3a-prolog/results/`).
- [x] Repo-wide inventory (2026-11-25, `INVENTORY.md` at the repo root, a proposal with a root HISTORY skeleton). Awaiting Matthias: nothing outside `spikes/` is removed until he decides.

## Questions for Matthias

1. Tooling: Postgres 18 via `brew services` (socket /tmp:5432, db `spike_v3`). OK to keep the brew service running? The `.venv` still holds clingo and the other packages of the dropped V3e; remove them?
2. ~~Framing of the recommendation (shape vs stack)~~: answered 2026-11-25 by the platform decision, Python + Prolog (`HISTORY.md`, Decision).
3. ~~Optional search (Scriptum/Lucene, HNSW) for `resolve_term`~~: folded into the platform decision 2026-11-25. Not part of v3; listed under RESULTS "Not done".
5. ~~Tie-break between the stacks~~: answered 2026-11-25 by the platform decision.
10. Rule classes and deontic rules (RESULTS, residual 5). The `:class` labels record a rule's inferential role, not whether it grants a permission.
    - R311 (`auto_approved`, "without further checks") is a policy permission. R312 (`auto_approved` → `approved`) is an inferential entitlement.
    - R301 was "may approve" (`entitlement`) in `rules/rules.yaml` and became the `material_inference` `has_approver` in the slice.
    - Should deontic rules enter as their own kind, either a `:modality` (permission / obligation / prohibition) beside `:class` or a separate record type issued by an authority? Should R301 go back to a permission?
    - **Open, deferred** with the vocabulary work.
