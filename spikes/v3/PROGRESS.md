# Spike v3 progress (branch spike/v3)

`RESULTS.md` describes the current state. `HISTORY.md` holds every phase so far (1–22) and names the tags.

## Status

- [x] System A, the benchmark and its confirmatory runs, wrapped up (2026-11-26; HISTORY phases 1–22, last tag `spike-v3-wrapup`). No plan is open.

## Questions for Matthias

This section lists open questions only. Answered ones are in `HISTORY.md` with their phase.

10. Rule classes and deontic rules (RESULTS, residual 5). The `:class` labels record a rule's inferential role, not whether it grants a permission.
    - R311 (`auto_approved`, "without further checks") is a policy permission. R312 (`auto_approved` → `approved`) is an inferential entitlement.
    - R301 was "may approve" (`entitlement`) in `rules/rules.yaml` and became the `material_inference` `has_approver` in the slice.
    - Should deontic rules enter as their own kind? Either a `:modality` (permission / obligation / prohibition) beside `:class`, or a separate record type issued by an authority.
    - Should R301 go back to a permission?
    - **Open, deferred** with the vocabulary work.
