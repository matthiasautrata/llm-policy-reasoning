# Spike v3 addendum — one SQL form per concept; scope recorded

Plan for Claude Code, 2026-11-25 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. First, harvest `PLAN-v3-memory.md` into `HISTORY.md` (one entry) and delete it.

## 0 Scope (decided by Matthias, 2026-11-25)

The system answers questions **about** the data: structure, meaning, classifications, relationships, claims, warrants, and how to query it (SQL help). It is not the execution path for big-data queries; users keep Genie, Cortex and plain SQL for that. Therefore:
- Large aggregates at the root (110 s, 4.6 GB) are a documented residual, not a blocker. No probe query, no SQL generator as an execution path in this plan.
- Compiling rules to SQL may return later as an **answer** ("here is the SQL that implements the rule, and the rules it rests on"), to be decided in the benchmark design.

Record this scope in RESULTS (Strategy for large aggregates: decision) and in PROGRESS.

## 1 One SQL form per concept

`:batch_sql` is a second, hand-written SQL text for `reporting_chain`: two definitions that must agree (IR-002 risk).
- Make the **set form the only form**: a concept with a required parameter takes a set (`IN ($p)`), and a single key is a set of one. Remove `:batch_sql` from the slice, the LinkML model, `sql.py` and `CONTRACT.md`.
- Apply to every concept with a required parameter, not only `reporting_chain`, if the set form is natural for it; record each choice. Where a concept cannot take a set naturally, leave the single form and record why.
- `flush()` uses the one form for both single and batched fetches.
- Gate: keys byte-identical; bench and the L2 memory figure (cc0018 peak ≈ 0.49 GB) not worse beyond noise; check 5 (bounded fetch) holds.

## 2 RESULTS and PROGRESS

RESULTS: current state; the scope decision; the root as residual with its numbers. PROGRESS: status; open questions only.

## Decisions

(Executor: append dated entries — what was decided, why.)
