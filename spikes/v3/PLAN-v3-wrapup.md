# v3 wrap-up — housekeeping, cleanup, commit, push

Plan for Claude Code, 2026-11-26 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. No API spend. **Pushing is approved for this plan** (step 6); merging into `main` is not.

## 1 Harvest and tag

1. Harvest `PLAN-v3-bench-full.md` into `spikes/v3/HISTORY.md`: one phase per section actually run (fixes, design tools, batch 1, §3a, §3b, §3b′, §3c, §3d, §3e, §3f), each with question, decisions and why, findings kept, findings reversed and by what (e.g. "T misreads GR7" was a judge error, reversed by §3e.1), commit range. Keep the list of post-hoc changes with their reasons.
2. Tag the state before deleting: `spike-v3-benchmark`. Then delete `PLAN-v3-bench-full.md` and this plan's predecessor files if any remain.
3. Root `HISTORY.md`: bring the v3 entry up to date (System A spike, benchmark, main result in two lines, tags).

## 2 RESULTS to its final form

`spikes/v3/RESULTS.md` describes the current state only, for the paper to draw on:
- System A (shape, contract, semantics, integrity gate, engine), briefly.
- The benchmark: design (arms G, G+, G-q, G-tools, T, F; items; k and d strata; models; scoring by keys, judge only where no key decides), the confirmatory runs (§3b′, §3c.2–4, §3d, §3e.2, §3f) and their tables, the main result, the controls, cost, the judge-validity finding, limitations (one generator, one domain, synthetic data, strata differ by N, reader limits, judge-only reasons, effort "high" as tested, see 4.3).
- Exploratory runs (pilot, batch 1, §3b) only as a short paragraph pointing to HISTORY; their tables move to HISTORY.
- Known residuals and the fallback, as now.

## 3 Living docs and repository

1. `PROGRESS.md`: reset to the current state; only open questions remain (10, deontic rules, stays open).
2. `bench/README.md`: how to reproduce every confirmatory run (commands, models, endpoints, budget flags, judge, scoring), and how keys and items are regenerated.
3. `CLAUDE.md`: add the bench gate (selftest, check_bases, task-key equality, render completeness) and the rule "grade from oracle keys where keys decide; the LLM judge only where none does". Remove anything stale.
4. Remove files no current claim cites (the housekeeping rule): scratch logs, superseded result files not cited by RESULTS or HISTORY (keep every `.gz` a table cites), stale caches. List removals in HISTORY.
5. Check that nothing secret is tracked or about to be: `.env` ignored and untracked (`git check-ignore .env`), no API key patterns in the tree or the unpushed history (`sk-`, `sk-or-`, long bearer-like strings); stop and report if anything is found. Results may contain provider generation ids: fine; keys: not.
6. If the Ollama server is still running from the smoke tests, stop it.

## 4 Small checks

1. The full gate (`CLAUDE.md`, now including the bench gate) green; `make verify` green.
2. Every table in RESULTS reproduces from the committed `.gz` files with `bench/score.py` (no API calls); list the commands.
3. OpenAI's docs for gpt-6.2-sol: is any reasoning effort above `high` accepted? Record the answer (source and date). If yes, RESULTS phrases the claim as "up to effort high"; do not run it.

## 5 Commit

Atomic commits per step above, `area: summary`, explicit paths. Working tree clean afterwards.

## 6 Push

Push `spike/v3` to `origin` (it is 70+ commits ahead) and the tags (`git push origin spike/v3 --tags`, or the named tags). Do not merge into `main` and do not open a PR; report the push and the tag list. Merging is Matthias's decision.

STOP: report what was removed, the final RESULTS outline, the gate, the secrets check, the effort answer and the push.

## Decisions

(Executor: append dated entries — what was decided, why.)
- 2026-11-26 — §1: `spike-v3-benchmark` is an annotated tag at b3b6a35, the last commit with `PLAN-v3-bench-full.md`. HISTORY phases 12–21 follow the plan's sections; §3d is its own phase (19) because the arms were frozen before it, and §3e.1 (judge validity) and §3e.2–§3f (the stronger model) are separate phases (20, 21) because they answer different questions. The post-hoc change list closes phase 21. No predecessor plan remained (PLAN-v3-bench-run was removed in phase 11).
- 2026-11-26 — This plan is itself harvested at the end (HISTORY phase 22) and removed after a tag `spike-v3-wrapup`, by the rule "an executed plan is harvested into HISTORY and removed"; both tags are pushed.
