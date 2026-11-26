# v3 benchmark (PLAN-v3-bench)

Built 2026-11-25 on branch spike/v3. The design is in `notes/warrant-layer/benchmark-design.md`; the build plan is HISTORY phase 10 (`PLAN-v3-bench.md` at tag `spike-v3-bench`), hardening and the pilot HISTORY phase 11 (`PLAN-v3-bench-run.md` at tag `spike-v3-bench-run`), the current plan `spikes/v3/PLAN-v3-bench-full.md`. The engine is reached only through `spikes/v3/v3a-prolog/cli`.

From the repo root:

```
.venv/bin/python bench/gen.py                                        # bases/N{025,050,100,200}.{edn,params,questions}
.venv/bin/python spikes/v3/shared/reference.py --bench bench/bases/N050 bench/bases/N100 bench/bases/N200   # *.keys.json
.venv/bin/python bench/check_bases.py                                # gate, base keys, slice keys on every base
.venv/bin/python bench/render_md.py                                  # material/N*.md for arm G, completeness check
.venv/bin/python bench/gplus.py                                      # G+ trusted functions against the oracle
.venv/bin/python spikes/v3/shared/reference.py --tasks bench/tasks/A1.json bench/tasks/A2.json bench/tasks/A3.json   # tasks/A*.keys.json
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

`questions/manager.json` holds the slice questions rephrased as a manager would ask, with department scope. It has 31 questions. The keys stay in `spikes/v3/shared/keys.json` (extended), under the slice id. The file lists the six excluded questions and why: four hypothesis questions and two root-level totals.

## Arms, scoring and pilot (§5–§8)

```
.venv/bin/python bench/run.py --models deepseek/deepseek-v4.1-flash --n 25 200 --estimate                  # cost estimate, no calls
.venv/bin/python bench/run.py --models deepseek/deepseek-v4.1-flash --n 25 200 --out bench/results/b1.jsonl --budget 3   # refuses if the estimate exceeds what is left
.venv/bin/python bench/score.py bench/results/b1.jsonl --judge --budget 2              # submits an OpenAI Batch; rerun to collect (exit 3 while pending)
.venv/bin/python bench/score.py bench/results/b1.jsonl --export bench/grading          # 10 sessions for hand grading
.venv/bin/python bench/selftest.py                                                     # budget, faults, endpoints, scoring; no calls
```

`run.py` runs the arms G, G+ and T (analyst tasks: G and T by default, `--analyst-arms`). T's tools are `resolve_term`, `describe`, `decide`, `why`, `why_not`, and the design tools `rules` and `summary` (PLAN-v3-bench-full §2, added after the pilot; records carry `config.t_tools`, and `score.py` reports records without them as `T-eval`). T's system prompt is unchanged from the pilot. A model is an OpenRouter id, `openai@<id>` or `ollama@<tag>` (`--context`, default 65536, recorded); `harness/openrouter.py` serves all three endpoints, keys from `OPENROUTER_API_KEY` and `OPENAI_API_KEY`, set in the environment or in the git-ignored `.env` at the repo root (format in `.env.example`, mode 600; the environment wins; `run.py` and `score.py` refuse a `.env` that git does not ignore before doing anything else), never logged. Cost is OpenRouter's charged cost, OpenAI's from tokens and `OPENAI_PRICE` (checked 2026-11-26), Ollama's 0.

Each cell is one resumable JSONL record holding every call (model, provider, tokens, cost, time) and every tool call as executed. Prices are fetched at start from OpenRouter's public endpoints list and recorded in the config: per field, the highest over the endpoints the quantization filter (default fp8) admits is the reserve price, the lowest the typical one. Before each call the budget reserves the call's maximum cost (the prompt at 2.5 characters per token plus `max_tokens`, at the reserve price) and settles it with the actual cost after, so concurrent workers never exceed `--budget`. A live run first estimates its cells from the pilot's tokens and calls per cell (at the typical price times the pilot's charged-to-typical ratio, plus one forced call per turn the pilot ended at the limit) and refuses before any call if the estimate exceeds what is left of the budget. A turn that reaches the call limit (8 manager, 12 analyst calls with tools) ends with one more call with tools forbidden (`tool_choice: none`) asking for the answer from what was found (`forced_final`). `score.py` reports the cells and turns that reached it, by arm, as their own outcome. Every exception is recorded with its type, message, traceback and the cost already spent; a call that fails keeps its reservation as its cost. A reply whose reported prompt tokens are fewer than one per 8 characters sent, or (Ollama) that fills 98 % of the context, fails the cell with `truncated`.

The judge is `openai@gpt-6.2-sol` through the OpenAI Batch API (`harness/openai_batch.py`, half price), with its own budget (the OpenAI credits); `stub:key`, `stub:tool`, `stub:abstain`, `stub:judge` and `fake:<usd>[:raise|badargs|nofunc|notools|trunc]` stand in for models in tests. `score.py` scores the manager answers against the keys and the analyst checks mechanically. It grades gold reasons with the judge (`judge_rubric.md`) and reports consistency, silent interpretation, inlining and cost per correct answer.

A contested check counts as reported only on a line that also says contested (or conflict, disputed); a plain figure counts as the naive answer. `--judge-reasoning` (default medium, HISTORY phase 11) sets the judge's `reasoning_effort`; grades go to `<results>.judge-<effort>.jsonl` (low: `<results>.judge.jsonl`), so levels can be compared on the same sessions. Results in `bench/results/` are committed gzipped (`gzip -k -9`; `gunzip -k` before scoring); the plain JSONL and the batch state stay local.

Pilot (HISTORY phase 11): DeepSeek, A1–A3 and ten manager questions, N = 25 and 200, 72 cells, run 2026-11-26 for $0.60 (`results/pilot*.jsonl.gz`); its analyst grades are withdrawn (empty replies at the call limit).
