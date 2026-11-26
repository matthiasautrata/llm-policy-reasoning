# v3 benchmark — fixes from the pilot, T's design tools, model selection, re-pilot, full run

Plan for Claude Code, 2026-11-26 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. First, harvest `PLAN-v3-bench-run.md` into `HISTORY.md` (one entry, with the pilot table) and delete it. **STOP after each marked step.** OpenRouter remaining: $9.33 (hard cap). OpenAI judge: from Matthias's credits.

## 1 Fixes from the pilot (no calls)

1. Reservation price per model: the highest fp8 price in the model's endpoints list, dated.
2. `RESERVE_CHARS` 2.5.
3. Calibrate `EST` from the pilot's actual tokens and calls per cell (analyst estimate was about 5× too low).
4. **Final answer at the call limit (the largest defect found).** In the pilot every turn that hit the limit ended with an empty reply: 21 turns, all with 0 characters (one with 146). That includes turn 1, the main design turn, in 8 of the 12 analyst sessions, on both arms, so the pilot's analyst grades mostly reflect turns 2–4. Fix, the same for every arm: when a turn reaches its limit, make one more call with tools disabled (`tool_choice: none`) and the instruction to answer now from what was found, saying what was not checked. Record that the turn was closed this way (`forced_final: true`). Self-test: a fake client that always calls tools must still end each turn with a non-empty reply.
5. Self-test green.
6. The pilot's hand-grading export is withdrawn (its sessions are crippled by fix 4); a new export comes from batch 1.

## 2 T's design tools (approved by Matthias 2026-11-26: learning from the pilot and restarting where needed is part of the method)

### 2.1 Why

Pilot (DeepSeek, one repetition, so a signal, not a result): T led on manager questions (7/10, 8/10 against G 5/10, 6/10) but not on analyst tasks (gold reasons covered: G 28 and 24, T 26 and 20 at N 25 and 200). Where T lost:
- **A2 at N 200:** T made 238 `decide` calls, hit the call limit in turns 1 and 3, and missed seven reasons. It evaluated instance by instance.
- **A1 GR6, GR10:** wrong at both N: the vendor exceptions and the mid-year transfer, which a design must see as *rules*, not as answers.

T's tools only *evaluate* (`decide`, `why`, `why_not`, `describe`, `resolve_term`). A design partner must also *navigate the rules*: which rules govern a term, how they interact, where they conflict. G reads every rule as text; T has no way to list them. Meanwhile G degraded at N 200 on A1 (eight reasons missed or wrong), as the thesis predicts.

### 2.2 Proposal

Two engine ops (`CONTRACT.md`, V3a, `reference.py` where it computes results), exposed as T tools:
- **`rules`** `{about: term | predicate | asset}` → the rules and claims that conclude, attack or read it, each with `doc`, owner, kind, class, validity, superiority edges, dependencies, and the conflicts the engine knows of (root conflicts touching it). Structure from the loaded rule base, no evaluation.
- **`summary`** `{goal: open goal, filters?, as_of?}` → status counts over the goal's instances (proven / refuted / contested), the contested roots, and a bounded sample of ids per status. One call instead of hundreds of `decide`s.

Tool descriptions say what each is for (design: `rules`, `summary`; answers: `decide`, `why`). No other change to T's prompt.

### 2.3 Fairness note (record in RESULTS and HISTORY)

This change is made after the pilot. It is legitimate only because it addresses a capability gap any real deployment has (navigating the rule base), not the gold reasons, and because it is frozen before the full run. Report both T versions; "evaluation-only tools are not enough for design work" is itself a finding.

### 2.4 Call limit

Keep the same limit for every arm (decided: one bound for all). Report cells that hit it as their own outcome, by arm.

STOP: report the ops, the tool descriptions, and the gate.

## 3 DeepSeek full run, in two batches (priority; decided 2026-11-26)

The benchmark runs on DeepSeek first; other models come after (§4). The re-pilot is folded into the full run, so nothing is paid twice:

- **Batch 1:** DeepSeek, N = 25 and 200, repetition 1, all arms (G+ on the analyst tasks too), all 31 manager questions and A1–A3. Judge at medium. STOP: report, compare with the pilot (T with and without the design tools), and recompute the rest. If batch 1 shows a defect that invalidates cells, fix it, mark those cells for re-run, and say so; otherwise continue.
- **Amendment after batch 1 (Matthias, 2026-11-26): do §3a and §3b before batch 2.**

## 3a Fixes from batch 1 (cents)

Batch 1 findings: G covers 30/34 gold reasons at both N, so the rule count does not bite; two gold reasons are graded wrong for every arm at every N; T could not open claim C10 by id.

1. **Gold reasons** (task data and the Tolaria design note `warrant-layer/benchmark-design.md` together):
   - A2 GR9 and GR12 ask for the reporting chain as of the request date, which the data cannot give (reporting lines are not dated). Rewrite both as caveats: the design must state that the approver chain reflects the current org chart, and keep limits and vendor status as of the request date.
   - A1 GR2: from "never sum headroom across centres" to "headroom is not additive into a budget: a sum over centres is bounded by their ancestors' caps, and over overlapping subtrees it double-counts".
   - Check every other reason that no arm covers at any N in batch 1 the same way: is it satisfiable from the data and tools? List the result.
2. **T tool gap:** `describe` and `rules` accept a rule or claim id (claims by id, with standing at `as_of`). Give `domain_truncated` a readable message. Engine and contract change, gate as usual.
3. **Re-judge** batch 1 with the rewritten reasons (judge only, no new arm calls). Re-run T's analyst cells at N 25 and 200 only if fix 2 can change them (T asked for a claim by id in that cell); list which.

STOP: report the re-judged table and which cells were re-run.

## 3b Make the rule count bite (about $1)

Batch 1 tests only the core slice: no question or task needs a generated rule, so growth in N is distraction only. The hypothesis is about rules that interact and must be honoured (k × interaction).

1. **Manager questions on the generated families,** for each N ≥ 50: a fixed number per N (propose 12), sampled from `bases/N*.questions.json` stratified by pattern (dated limit version, exception, counter-exception, owner dispute with and without superiority, claim tree), phrased as a manager would ask. Record k (rules and claims on the proof path) per question. Keys from the existing family oracle.
2. **Analyst task A4** on one generated programme present at every N ≥ 50: dated limit versions, the clearance exception and counter-exception, an owner dispute, claims about it. Gold reasons derived from the family's structure, with mechanical checks wherever the oracle gives a value. If the generator makes programmes independent of each other, so that a programme's interactions do not grow with N, say so and propose how density can reach the task programme (more disputes, superiority and exceptions touching it as N grows); do not change the bases without Matthias's go.
3. N 25 has no generated families: the family questions and A4 start at N 50. The core-slice questions stay at every N as the baseline.
4. Run the new items at N 50 and 200 first, DeepSeek, all arms, repetition 1.

STOP: report whether accuracy or gold coverage now moves with N or k, by arm.

## 3c Batch 2

- **Batch 2** (after §3a and §3b, with the new items included): N = 50 and 100 (repetition 1), then repetition 2 at all N, resumable, within the cap minus a reserve for §4.

STOP after batch 2: results, cost, and the reassessment.

## 4 Later: other models

After the DeepSeek run, Matthias decides on a second family. Candidates: GLM, Ling Flash 3.1, Hy4 Flash. Selection by OpenRouter's Models and Benchmarks APIs, re-ranked by our cost per cell against the agentic index, then one A1 session per candidate on G and T at N = 25. Local column (gpt-oss:20b) likewise later: manager questions at all N; analyst tasks only at N = 25, or at 128k context if it fits in memory.

## Decisions

(Executor: append dated entries — what was decided, why.)
- 2026-11-26 — `PLAN-v3-bench-run.md` harvested into HISTORY phase 11 under tag `spike-v3-bench-run` (at 3903015), then removed, together with the pilot's grading export (§1.6). Recounted from `pilot.jsonl`: of the 21 turns at the call limit, 20 ended empty and one with 144 characters (§1.4 says 146), and turn 1 hit the limit in 9 of 12 analyst sessions (§1.4 says 8). HISTORY uses the recount.
- 2026-11-26 — §1.4: the forced call goes after the turn's ROUNDS calls with tools, so a limited turn makes ROUNDS + 1 calls; its tool calls, if the model still makes any, are dropped. `tool_choice` is sent only when tools are, so a G turn without tools is unchanged. Whether OpenRouter's DeepSeek and GLM endpoints honour `none` is untested (no calls in §1); score.py counts a forced reply that is still empty as empty.
- 2026-11-26 — §1.1: prices come from the endpoints list at the start of every run, not a dated table: per field (prompt, completion, cache read) the highest over the endpoints the quantization filter admits reserves the budget, the lowest is the typical price. They are recorded in each record's `config.prices` with the fetch time. Fetched 2026-11-26: DeepSeek reserve 1.5e-6 / 6e-6 / 7.5e-8, typical 5.07e-8 / 2.028e-7 / 1.014e-9 (20 fp8 endpoints); GLM reserve 2.1e-6 / 6.6e-6 / 2.6e-7, typical 6e-7 / 1.9e-6 / 1e-7 (9). A fetch failure or a model without a priced endpoint stops the run.
- 2026-11-26 — §1.2: RESERVE_CHARS 2.5; the pilot's lowest characters per prompt token was 2.80 (median 3.47).
- 2026-11-26 — §1.3: the estimate reads `pilot.jsonl.gz` at run time rather than copying figures: per (kind, arm, N), mean calls and uncached, cached and completion tokens per cell, plus one forced call (of the cell's mean call size) per turn the pilot ended at the limit. G+ analyst uses G's; N 50 and 100 are linear between 25 and 200. Cost is those tokens at the typical price times 2.69, the pilot's charged cost over its tokens at DeepSeek's typical price (routing used Baidu and InferenceNet, not only the cheapest). Judge: the pilot's medium mean, $0.0110 per analyst session. Assumed, untested: GLM's tokens match DeepSeek's, and T's design tools (§2) do not change T's. `--pilot` and PILOT are gone; every live run estimates its own remaining cells and refuses before any call if the estimate exceeds what is left of `--budget`. Batch 1 as planned (DeepSeek, N 25 and 200, all arms, G+ on analyst tasks): $1.20 OpenRouter, $0.20 judge.
- 2026-11-26 — Judge default medium (Matthias: "Medium is the judge level for now"). The grades file is named by effort, low keeping the untagged name, so the pilot's files keep theirs.
- 2026-11-26 — §2 `rules`: conflicts are structural, a supporter and a rival attacker of the predicate (complement, functional rival with a different value, or incompatible) whose heads can meet and with no superiority either way; a listed conflict is live only where both bodies hold (R305 vs R307 never in the slice data). `decide` and `summary` find the instances. For an asset only the claims about it are listed (bolt at N 200: 99 items, 48k characters, with every claim on its predicates; 21 items, 8k, without). Rules that only read the target are `read_by: [{id, head}]` (the concept `request` at N 200: 47k characters as items, 6.8k so). A goal pattern narrows a predicate to the records whose literal unifies with it, since 34 or 35 concluding rules (capitalised, programme_cleared at N 200) exceed the 12k tool-result cap. Null and empty fields are omitted.
- 2026-11-26 — §2 `summary`: open goals over requests or employees cannot be enumerated (the request concept needs its id bound), so `filters` maps a variable to a domain: a list of values, or a concept with filters (column default `id`). The instances are the cartesian product of the domains; each is decided with the other variables open, and one with no candidate counts as refuted. Without a domain the op returns ERROR naming the concept, the keys and an example domain. Limits: 20,000 instances, a truncated domain fetch is an ERROR, 20 contested roots (with the total), sample 10 per status.
- 2026-11-26 — §2 reference: `reference.py` keys `summary` from its per-request functions (Q56–Q60: approved, po_issued, vendor_cleared over cc0049, cap_breach over cc0009, po_issued over a list); five new keys, `changed` still Q07 Q14 (cc0049 has no request R307 decides differently). `rules` computes no result to key: it is a projection of the loaded rule base, checked against the slice in `bench/selftest.py`. accept.py maps `:kind :summary` to the op and compares status, instances, counts, contested roots and sample; check 1 covers it, and check_bases on every base. The model check's question mode test (IR-006) treats a summary variable with a domain as bound; without that it reported Q56–Q60 as unbound calls. This is a scope note on an existing check, not a new one, to confirm with Matthias.
- 2026-11-26 — §2 T tools: `rules` and `summary` added after `why_not`; descriptions begin "For design:" (rules, summary) and "For answers:" (decide, why). T's system prompt is unchanged, including its sentence naming the five evaluation tools, read as the plan's "no other change to T's prompt". `summary`'s `filters` is a JSON object in the tool schema (a string is parsed too). §2.3: records carry `config.t_tools`; score.py reports pilot T records as `T-eval`. §2.4: score.py's call-limit table (cells and turns at the limit, manager correct among them) by arm, kind, model and N; on the pilot it gives 21 of 108 turns.
- 2026-11-26 — Matthias confirmed the IR-006 scope note (a summary variable with a domain counts as bound).
- 2026-11-26 — Live check of §1.4's `tool_choice: "none"` (Matthias: "yes, try"; $0.008). Five T sessions on M01 at N 25, each one normal call that made 1–3 tool calls, then FINAL_NOW with tools forbidden. DeepSeek v4.1 Flash (served by Baidu, 3 of 3) and GLM 5.3 (Novita, 2 of 2): no tool calls, finish `stop`, 468–879 characters, all giving the key total 3,715,000. Only those providers were tested; the fp8 filter can route to others.
- 2026-11-26 — §3 batch 1 run as planned into `bench/results/b1.jsonl` (`--budget 3`): 204 cells, no errors, $0.536 (estimate $1.20, so the calibration overestimates by about 2.2×); judge $0.295 at medium (estimate $0.20). One judge reply (G+ A1 N 200) was invalid JSON (`;` between strings) and was graded again by rerunning `--judge`. No defect invalidates a cell; nothing is marked for re-run. One cosmetic defect, not fixed (the tools are frozen): `summary` with a domain whose fetch is truncated returns ERROR with "Unknown error term: domain_truncated(request)" instead of a message (2 calls). Batch 2 goes into the same file (resumable; rep 2 adds cells). Its estimate is $3.66 + judge $0.60; scaled by batch 1's ratios, about $1.65 + $0.90.
- 2026-11-26 — §3a.1 gold reasons: A1 GR2, A2 GR9 and GR12 replaced with Matthias's texts (verbatim from the notes vault), `source` noting the revision. The other reasons checked against batch 1's six analyst cells (G, G+, T at N 25 and 200): every one is covered in at least one cell (e.g. A3 GR8, wrong for G and G+, covered by T), so none other is unsatisfiable and none was changed.
- 2026-11-26 — §3a.2: `rules`, `describe` and `claims` resolve an active rule or claim id (`R203`, `C10`). `rules` gives that record as the only item, the predicates it concludes, attacks or ranks (a claim: its assertion's), and the root conflicts it is a side of; `describe` adds the item as `record` (kind the rule's, or `claim`); `claims` gives that claim's standing on `as_of`. An id is tried last in `rules` and `describe`, so an asset, predicate or concept with the same text wins (none exists). `domain_truncated` now prints "the domain <concept> has more rows than the fetch limit …; narrow it with its filters … or give a list of values". No key changed (the ops are not keyed); gate green. T's `rules` and `describe` descriptions name the ids; `config.t_tools` is unchanged (same tool names), so the T version is told apart by `ts` (re-run cells after 2026-11-26T11:19).
- 2026-11-26 — §3a.3 re-run: T asked for a record by id in both analyst A1 cells (N 25: `rules C10`; N 200: `rules R203`, `rules C10`, `describe C10`; all OUT_OF_SCOPE before). Both were moved to `b1.pre3a.jsonl` and re-run into `b1.jsonl` ($0.047, `--also` so the budget counts both); the new cells make 3 and 7 by-id calls, all answered. No other analyst cell asked by id. Two manager cells did (M14 N 200: `rules C1`, `rules C6`; M21 N 200: `rules C10`), not re-run, as §3a limits re-runs to analyst cells. M14 is correct; M21 is wrong (status right, value wrong), so the id fix might change it.
- 2026-11-26 — §3a.3 re-judge: the old grades moved to `b1.judge-medium.pre3a.jsonl` (with their batch markers), and all 18 analyst sessions graded again into `b1.judge-medium.jsonl` ($0.281, no unparsed reply). The pre-§3a T cells and grades are kept, as RESULTS compares with them. 7 of the 162 grades whose session and text did not change flipped, the judge's run-to-run noise.
