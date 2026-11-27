# v3 addendum — gpt-6.2-sol at effort max

Plan for Claude Code, 2026-11-26 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. Arms frozen. Push approved for this plan's commits; no merge.

**Why:** OpenAI lists low, medium, high, xhigh and max for gpt-6.2-sol (model catalog, read 2026-11-26). RESULTS states the closure result "up to effort high". Close the gap at the top setting.

1. **Run:** gpt-6.2-sol, reasoning effort **max**, family questions F01–F16, N 200, arms G, G-q and T, 3 repetitions, OpenAI credits, 2 workers. Same items, scoring (mechanical, no judge) and reporting as §3f.
2. **Budget:** estimate first from a check cell at max (reasoning tokens may rise sharply); cap at the remaining OpenAI credit minus $2 (about $11). If the estimate exceeds the cap, drop T first (it is 48 of 48 at medium and high), then reduce to 2 repetitions; never drop G or G-q. Stop before any call if even that does not fit.
3. **Expected outcomes, recorded in HISTORY before the run:** if G and G-q at max still qualify absence near 0, closure without an engine fails at this model's maximum effort, and RESULTS drops the "up to effort high" qualification; if they qualify it near T, closure depends on maximum reasoning effort, and RESULTS reports it with its cost per correct answer beside T's.
4. **Report** beside §3f (medium, high, max): correct, qualifier, absence, contested sides, by k, reasoning tokens per cell, cost. Update RESULTS and HISTORY (one phase), commit, push `spike/v3`. Delete this plan after harvesting it.

STOP: report.

## Decisions

(Executor: append dated entries — what was decided, why.)
- 2026-11-26 — `run.py --reasoning` gains `xhigh` and `max` (the values OpenAI's catalog lists); a runner flag, not an arm change. Output `bench/results/b3g.jsonl`. The check cell (F01, G, rep 0) is written to the same file, so the run resumes past it and its cost counts against the cap.
- 2026-11-26 — Cap $11.2: the $13.2 of OpenAI credit HISTORY phase 21 records as remaining, less $2. The estimate scales b3f's measured cost per arm (same model, items and arms, effort high) by the check cell's cost ratio at max against the same cell at high, because b3c's DeepSeek tokens say nothing about reasoning at max.
