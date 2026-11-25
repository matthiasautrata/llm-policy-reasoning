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
- [x] Benchmark preconditions (2026-11-25, `PLAN-v3-preconditions.md` §2; RESULTS "Benchmark preconditions"):
  - §2.1 `[:agg :sum|:count ..]`, R120/R121, Q44–Q46; fetch volume measured, push-down proposed;
  - §2.2 the absence qualifier on every `decide` key, Q47;
  - §2.3 R315/R316 downstream of C3/C4 and R312/R314, Q48–Q52.
  - Gate: GREEN 1, 3–8 (36 base questions); `--mutation` fails check 1; isolation PASS; negatives 15/15 (90 literals round-trip); guard probe 2/2; bench 0 errors, 11.92 SQL per decide.
- [x] PROGRESS 11–15 (2026-11-25; Decisions in `PLAN-v3-preconditions.md`): IR-007 with fixture RA1; derived coverage (IR-005 amended), Q53–Q55; Q26/Q27 removed; the aggregate push-down, measured to the root (693 statements, 207 s, 12.1 GB; RESULTS "Fetch volume").
  - Gate: keys changed only by Q26/Q27 removed and Q53–Q55 added; GREEN 1, 3–8 (37 base questions); `--mutation` fails check 1; isolation PASS; negatives unchanged; guard probe 2/2; bench 0 errors.
- [ ] Harvest `PLAN-v3-preconditions.md` into HISTORY and remove it, once Matthias has reviewed its Decisions.

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
11. ~~Integrity candidate~~: answered 2026-11-25. Accepted as IR-007 `unsafe-aggregation`, with the negative fixture RA1 (`fixtures/integrity/ir007-unsafe-aggregation.edn`).
12. ~~IR-005 extended to absence~~: answered 2026-11-25. It is an amendment to IR-005, and the code citations stay.
13. ~~Duplicate questions Q26/Q27~~: answered 2026-11-25. Removed: Q01 and Q09 key the same goals and qualifiers, so neither adds a branch.
14. ~~`cap_breach` and C10~~: answered 2026-11-25. Completeness is derived: a predicate is covered only if every predicate and concept it reads, attackers included, is covered. C10 does not cover `cap_breach`. Q53–Q55 probe it (`SEMANTICS.md`, Qualifier).
15. ~~Aggregate push-down~~: answered 2026-11-25. It is built (set-at-a-time rounds, batched and paged fetches) and measured at the root (RESULTS, "Fetch volume").

