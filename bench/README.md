# v3 benchmark (PLAN-v3-bench)

Built 2026-11-25 on branch spike/v3. The design is in `notes/warrant-layer/benchmark-design.md`; the build plan is HISTORY phase 10 (`PLAN-v3-bench.md` at tag `spike-v3-bench`), hardening and the pilot HISTORY phase 11 (`PLAN-v3-bench-run.md` at tag `spike-v3-bench-run`), the full runs HISTORY phases 12–21 (`PLAN-v3-bench-full.md` at tag `spike-v3-benchmark`). Results: `spikes/v3/RESULTS.md`. The engine is reached only through `spikes/v3/v3a-prolog/cli`.

From the repo root:

```
.venv/bin/python bench/gen.py                                        # bases/N{025,050,100,200}.{edn,params,questions}
.venv/bin/python spikes/v3/shared/reference.py --bench bench/bases/N050 bench/bases/N100 bench/bases/N200   # *.keys.json
.venv/bin/python bench/check_bases.py                                # gate, base keys, slice keys on every base; task keys equal regenerated keys
.venv/bin/python bench/render_md.py                                  # material/N*.md for arm G, completeness check
.venv/bin/python bench/gplus.py                                      # G+ trusted functions against the oracle
.venv/bin/python bench/gen_items.py                                  # questions/family.json, tasks/A4.json (§3b)
.venv/bin/python spikes/v3/shared/reference.py --tasks bench/tasks/A1.json bench/tasks/A2.json bench/tasks/A3.json bench/tasks/A4.json   # tasks/A*.keys.json
```

## Bases (§2)

| N | rules | claims | interactions | per 100 rules | distractor share | base questions |
|---|---|---|---|---|---|---|
| 25 | 25 | 14 | 4 | 16 | – | – (the slice's 37) |
| 50 | 50 | 30 | 10 | 20 | 0.36 | 45 |
| 100 | 100 | 56 | 20 | 20 | 0.31 | 122 |
| 200 | 200 | 115 | 40 | 20 | 0.30 | 277 |

These figures use seed 1, density 20 and distractor share 0.3. The families are described in `gen.py`'s docstring, and each instance's parameters are in `N*.params.json`. The oracle reads those parameters and never the EDN. Each base passes the integrity gate. Its base questions and the 37 slice questions match their keys through the CLI, including accept.py's proof checks. A changed key fails, as it should. Generation is deterministic.

The `UNION ALL` fetch shape occurs only in the slice (R112 and R311 on `request.category`). Generated rules add none.

## Material for G and G+ (§3)

`material/N*.md` is rendered from each base's rule docs and metadata, never from rule bodies. Every rule and claim id of the base appears in it. Sizes are about 5.0k, 7.8k, 12.4k and 21.6k tokens at N = 25, 50, 100 and 200.

`gplus.py` holds G+'s five trusted functions:

| function | manager questions it answers | rules |
|---|---|---|
| `request_status` | 12 | R301–R316, R307 |
| `approved_total` | 3 | R120, R121, R314 |
| `spend` | 3 | R104, R105 |
| `role_limit` | 3 | R201–R203 |
| `breaching_requests` | 1 | R106, R110 |

Each function is checked against `reference.py` on every request (100,000), every centre for `spend`, 67 centres for the subtree functions, and every role at its boundary dates. Dropping R307 from the SQL gives 594 mismatches. The cost centre of an employee and vendor fitness rest on claims, which are not in the data, so no trusted function answers them.

## Tasks and questions (§4)

`tasks/A{1,2,3}.json` hold one analyst task each:

- four scripted turns;
- the gold reasons from the design note (13, 12 and 9);
- the checks, i.e. components with a checkable value for a worked example.

Every turn adds one sentence naming the example (cc0049, its parent cc0009, e077, bolt and cog), so that the figures a design reports can be compared mechanically. `tasks/A*.keys.json` holds the expected values. They come from `reference.py --tasks`, and a `naive` value is what a known wrong design gives:

- adding totals across a parent and its child;
- summing headroom;
- checking only the requester's own cap.

The values do not depend on N, because generated rules never conclude a slice predicate.

Since PLAN-v3-bench-full §3b, `gen_items.py` writes two item files on the generated families. Both hold one variant per N ≥ 50 under `by_n`, because N 25 has no generated families and gen.py seeds each N separately. An id names the same slot at every N:

- `questions/family.json` holds 16 manager questions per N (F01–F16), stratified by k (the rules and claims on the key's proof path: 1, 2–3, 4–5, 6+), four per stratum and one per outcome within it where possible (contested, true, false by absence, false by defeat, claim). They are sampled from `bases/N*.questions.json` and keyed by `bases/N*.keys.json` under their `base` id; each records k and d (capitalisation disputes with a rule on the path). A stratum short at an N is filled from the nearest lower one, and `stratum` says so (§3b′).
- `tasks/A4.json` is the main design task on programme P01, seeded apart from N (§3b′): the same nine requests (`requests`) at every N, picked by their outcome at N 200. Turns: dated limits, clearance with the exception and counter-exception, capitalisation under the disputes over P01's category (growing with N, with superiority across disputes), and clearance under the last sub-programme of P01's chain (deeper with N). Its gold reasons are derived from the parameters; its checks are keyed per N by `reference.py --tasks` (`A4.keys.json`), with naive values (one limit all year, clearance without the exception, the chain count taken as P01's).

`questions/manager.json` holds the slice questions rephrased as a manager would ask, with department scope. It has 31 questions. The keys stay in `spikes/v3/shared/keys.json` (extended), under the slice id. The file lists the six excluded questions and why: four hypothesis questions and two root-level totals.

## Arms, scoring and pilot (§5–§8)

```
.venv/bin/python bench/run.py --models deepseek/deepseek-v4.1-flash --n 25 200 --estimate                  # cost estimate, no calls
.venv/bin/python bench/run.py --models deepseek/deepseek-v4.1-flash --n 25 200 --out bench/results/b1.jsonl --budget 3   # refuses if the estimate exceeds what is left
.venv/bin/python bench/score.py bench/results/b1.jsonl --judge --budget 2              # submits an OpenAI Batch; rerun to collect (exit 3 while pending)
.venv/bin/python bench/score.py bench/results/b1.jsonl --export bench/grading          # 10 sessions for hand grading
.venv/bin/python bench/selftest.py                                                     # budget, faults, endpoints, scoring; no calls
```

`run.py` runs the arms G, G+, T and F, the floor (the data model and `sql`, no rules; §3b′) (analyst tasks: G and T by default, `--analyst-arms`). Variants run only when named: G-q and G+-q are G and G+ with one sentence more in the task instructions, "For every no, say whether it rests only on not finding something in the data." (§3c.2). G-tools is G's material without its rules and claims, which it looks up through T's `rules` tool, and `sql`, with no evaluating tool (§3d.2). T's tools are `resolve_term`, `describe`, `decide`, `why`, `why_not`, and the design tools `rules` and `summary` (PLAN-v3-bench-full §2, added after the pilot; `rules` and `describe` also take a rule or claim id since §3a; records carry `config.t_tools`, and `score.py` reports records without them as `T-eval`). T's system prompt is unchanged from the pilot. A model is an OpenRouter id, `openai@<id>` or `ollama@<tag>` (`--context`, default 65536, recorded); `harness/openrouter.py` serves all three endpoints, keys from `OPENROUTER_API_KEY` and `OPENAI_API_KEY`, set in the environment or in the git-ignored `.env` at the repo root (format in `.env.example`, mode 600; the environment wins; `run.py` and `score.py` refuse a `.env` that git does not ignore before doing anything else), never logged. Cost is OpenRouter's charged cost, OpenAI's from tokens and `OPENAI_PRICE` (checked 2026-11-26), Ollama's 0.

Each cell is one resumable JSONL record holding every call (model, provider, tokens, cost, time) and every tool call as executed. Prices are fetched at start from OpenRouter's public endpoints list and recorded in the config: per field, the highest over the endpoints the quantization filter (default fp8) admits is the reserve price, the lowest the typical one. Before each call the budget reserves the call's maximum cost (the prompt at 2.5 characters per token plus `max_tokens`, at the reserve price) and settles it with the actual cost after, so concurrent workers never exceed `--budget`. A live run first estimates its cells from the pilot's tokens and calls per cell (at the typical price times the pilot's charged-to-typical ratio, plus one forced call per turn the pilot ended at the limit) and refuses before any call if the estimate exceeds what is left of the budget. A turn that reaches the call limit (8 manager, 12 analyst calls with tools) ends with one more call with tools forbidden (`tool_choice: none`) asking for the answer from what was found (`forced_final`). `score.py` reports the cells and turns that reached it, by arm, as their own outcome. Every exception is recorded with its type, message, traceback and the cost already spent; a call that fails keeps its reservation as its cost. A reply whose reported prompt tokens are fewer than one per 8 characters sent, or (Ollama) that fills 98 % of the context, fails the cell with `truncated`. A failed cell is re-run on resume, and its record stays in the file; `score.py` counts a failed record that a later record of the same cell supersedes in the cost only, shown as `(+n)` beside the errors (§3d.3).

The judge is `openai@gpt-6.2-sol` through the OpenAI Batch API (`harness/openai_batch.py`, half price), with its own budget (the OpenAI credits); `stub:key`, `stub:tool`, `stub:abstain`, `stub:judge` and `fake:<usd>[:raise|badargs|nofunc|notools|trunc]` stand in for models in tests. `score.py` scores the manager answers against the keys and the analyst checks mechanically. It grades gold reasons with the judge (`judge_rubric.md`) and reports consistency, silent interpretation, inlining and cost per correct answer. Since §3b, `--judge-out <results>.judge-medium.2.jsonl` writes a second, independent judging of the same sessions; the report finds it beside the first (or takes `--judge-second`), shows both coverages and the judge's agreement with itself (share and Cohen's kappa over the reasons). Rows are split by item group (core, family, A4), and family questions are also tabled by k and by dispute count d. Since §3b′, a manager decide answer is correct when status, value, sides and qualifier match; every decide and why_not key states its qualifier (null when none), and a key without one is an error, never "not qualified". Sides are reported strict (the same id sets) and tolerant (each key side inside exactly one reported side, extra ids allowed, sides neither merged nor swapped). The judge-cost line sums every `<results>.judge*.jsonl`.

A contested check counts as reported only on a line that also says contested (or conflict, disputed, undecided); a plain figure counts as the naive answer. Since §3c.1, a check with a `subject` (A4's: its request, vendor or chain level) counts only in a block (a table, list or paragraph) or under a heading that names the subject, and a mechanical reported or naive grade that the judge's grade of the check contradicts is counted `unconfirmed`. `--judge-reasoning` (default medium, HISTORY phase 11) sets the judge's `reasoning_effort`; grades go to `<results>.judge-<effort>.jsonl` (low: `<results>.judge.jsonl`), so levels can be compared on the same sessions. Results in `bench/results/` are committed gzipped (`gzip -k -9`; `gunzip -k` before scoring); the plain JSONL and the batch state stay local.

Pilot (HISTORY phase 11): DeepSeek, A1–A3 and ten manager questions, N = 25 and 200, 72 cells, run 2026-11-26 for $0.60 (`results/pilot*.jsonl.gz`); its analyst grades are withdrawn (empty replies at the call limit).

## Reproducing the confirmatory runs (RESULTS, The benchmark)

**Generated inputs.** Regenerate the bases, keys and items with the commands at the top, then run the bench gate:
- `selftest.py`;
- `check_bases.py` (base keys, slice keys, and task keys equal to the regenerated ones);
- `render_md.py` (completeness).

Generation is deterministic. A regenerated key that differs from the committed one is a bug, unless a plan lists it with its reason.

**Runs.** Each command writes one record file. The run resumes: run it again and it skips the cells already done and re-runs failed ones. `--estimate` prints the cost and makes no call.
- **Budget.** `--budget` caps the summed cost of `--out` and `--also`, and the run refuses before any call if its estimate exceeds what is left.
- **Calibration.** §3e.2 and §3f calibrate their estimate on the DeepSeek run (`--calibrate`), max on §3f.
- **Workers.** §3e.2 ran at 6 workers and re-ran its rate-limited cells at 2. §3f and max ran at 2 workers.
- **GLM caps.** GLM was run one repetition at a time (`--reps 1`, then 2, then 3), with caps of $2.5, $3.2 and $3.8 at 2 workers. The A4 run's caps went up to $4.2.

Endpoints:
- DeepSeek and GLM run through OpenRouter (`OPENROUTER_API_KEY`), with the fp8 quantization filter.
- gpt-6.2-sol runs through OpenAI's Responses API (`openai@`, `OPENAI_API_KEY`).
- The temperature is 1.0 and `--max-tokens` is 16000 throughout.

```
F="F01 F02 F03 F04 F05 F06 F07 F08 F09 F10 F11 F12 F13 F14 F15 F16"
DS=deepseek/deepseek-v4.1-flash
# §3b′ (b3c): DeepSeek, N 50 and 200, all arms, family + A4
.venv/bin/python bench/run.py --models $DS --n 50 200 --arms G G+ T F --analyst-arms G T F --items ${=F} A4 --reps 3 --out bench/results/b3c.jsonl --budget 2 --workers 4
# §3c.2 (b3d-q): the qualifier sentence
.venv/bin/python bench/run.py --models $DS --n 200 --arms G-q G+-q --items ${=F} --reps 3 --out bench/results/b3d-q.jsonl --budget 1.5
# §3c.3 (b3d-n100): N 100
.venv/bin/python bench/run.py --models $DS --n 100 --arms G G+ T F --analyst-arms G T F --items ${=F} A4 --reps 3 --out bench/results/b3d-n100.jsonl --budget 2
# §3d.2 (b3d-gtools): rules as a lookup tool
.venv/bin/python bench/run.py --models $DS --n 200 --arms G-tools --analyst-arms G-tools --items ${=F} A4 --reps 3 --out bench/results/b3d-gtools.jsonl --budget 2
# §3c.4 (b3d-glm) and §3d.1 (b3d-glm-a4): GLM 5.3
.venv/bin/python bench/run.py --models z-ai/glm-5.3 --n 200 --arms G G+ T --items ${=F} --reps 3 --out bench/results/b3d-glm.jsonl --budget 3.8 --workers 2
.venv/bin/python bench/run.py --models z-ai/glm-5.3 --n 200 --analyst-arms G G+ T --items A4 --reps 3 --out bench/results/b3d-glm-a4.jsonl --budget 4.2 --workers 2
# §3e.2 (b3e), §3f (b3f) and max (b3g): gpt-6.2-sol at effort medium, high and max
.venv/bin/python bench/run.py --models openai@gpt-6.2-sol --reasoning medium --n 200 --arms G G-q T --items ${=F} --reps 3 --out bench/results/b3e.jsonl --budget 16 --calibrate bench/results/b3c.jsonl
.venv/bin/python bench/run.py --models openai@gpt-6.2-sol --reasoning high --n 200 --arms G G-q T --items ${=F} --reps 3 --out bench/results/b3f.jsonl --budget 12.75 --workers 2 --calibrate bench/results/b3c.jsonl
.venv/bin/python bench/run.py --models openai@gpt-6.2-sol --reasoning max --n 200 --arms G G-q T --items ${=F} --reps 3 --out bench/results/b3g.jsonl --budget 11.2 --workers 2 --calibrate bench/results/b3f.jsonl
```

(`${=F}` splits the list in zsh; in bash write `$F`.)

**Judge.** Analyst runs only: b3c, b3d-n100, b3d-gtools and b3d-glm-a4.
- The judge is `openai@gpt-6.2-sol` through the OpenAI Batch API, at effort medium (`judge_rubric.md`). Each session is judged twice, and the second judging is written beside the first.
- §3b′ uses its re-judging after §3c.1, `b3c.rejudge-medium*.jsonl`. The first judging, `b3c.judge-medium*`, is kept as the record of that change.
- Each call submits a batch. Rerun it to collect the grades: the exit code is 3 while the batch is pending.

```
.venv/bin/python bench/score.py bench/results/b3d-n100.jsonl --judge --budget 2
.venv/bin/python bench/score.py bench/results/b3d-n100.jsonl --judge --budget 2 --judge-out bench/results/b3d-n100.judge-medium.2.jsonl
.venv/bin/python bench/score.py bench/results/b3c.jsonl --judge --budget 2 --judge-out bench/results/b3c.rejudge-medium.jsonl     # and .rejudge-medium.2.jsonl
```

**Scoring** makes no API calls. Grades come from oracle keys where keys decide (`decided_by`). The judge's grades are used only where no key decides, and on unclear readings. Every RESULTS table of a run comes from that run's report.

Decompress the committed files first (`gunzip -k bench/results/*.gz`). Then score:

```
.venv/bin/python bench/score.py bench/results/b3c.jsonl --judge-out bench/results/b3c.rejudge-medium.jsonl   # §3b′: family, by key type, A4
.venv/bin/python bench/score.py bench/results/b3d-q.jsonl        # §3c.2
.venv/bin/python bench/score.py bench/results/b3d-n100.jsonl     # §3c.3
.venv/bin/python bench/score.py bench/results/b3d-gtools.jsonl   # §3d.2
.venv/bin/python bench/score.py bench/results/b3d-glm.jsonl      # §3c.4
.venv/bin/python bench/score.py bench/results/b3d-glm-a4.jsonl   # §3d.1
.venv/bin/python bench/score.py bench/results/b3e.jsonl          # §3e.2
.venv/bin/python bench/score.py bench/results/b3f.jsonl          # §3f
.venv/bin/python bench/score.py bench/results/b3g.jsonl          # max
```

Each report also gives:
- the k and d tables;
- the call-limit table;
- keys against the judge, by reason and arm;
- the judge's agreement with itself;
- the cost line.

The strata table is `gen_items.py`'s output (`stratum`, `k` and `d` in `questions/family.json`). The exploratory runs (pilot, b1, b3b, smoke) score the same way. Their tables are in `spikes/v3/HISTORY.md`.

