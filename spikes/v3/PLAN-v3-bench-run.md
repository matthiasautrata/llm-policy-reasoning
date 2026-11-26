# v3 benchmark — hardening, endpoints, smoke tests, pilot

Plan for Claude Code, 2026-11-26 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. First, harvest `PLAN-v3-bench.md` into `HISTORY.md` (one entry) and delete it.

**Stop after each step marked STOP** and report to Matthias; do not continue without his go. The aim is to never pay twice for a bug.

## 0 Budget and roles (decided 2026-11-26)

- **Tested models:** DeepSeek and GLM via OpenRouter; OpenRouter spend **$10 hard cap** for v3.
- **Judge:** an OpenAI model via the OpenAI **Batch API** (offline, half price), paid from Matthias's OpenAI credits (about $18). OpenAI is not a tested family, so no model grades itself. Sonnet is no longer the judge.
- **Local model** (Ollama) for plumbing tests and as a separately labelled extra column; never mixed into the paid results.
- Key handling: `OPENROUTER_API_KEY`, `OPENAI_API_KEY` from the environment, never logged.

## 1 Code fixes (no calls)

1. `session()` catches **every** exception: record type, message and traceback in the cell, count the cost already spent, write the record. An unexpected error must never lose a record or its cost.
2. **Hard cap means hard:** before each call, reserve an estimated maximum cost (prompt tokens known, max completion tokens) under the lock; settle with the actual cost after. Concurrency cannot overshoot the cap.
3. Self-test extended: an exception inside a session (fake client raising, malformed tool call, reply without `tool_calls`) is recorded with its cost; concurrent fake calls under a tiny cap never exceed it.

## 2 Endpoints and truncation (no calls)

1. **Endpoint option** in `harness/openrouter.py` (or a sibling client with the same return shape): `openrouter`, `openai`, `ollama` (OpenAI-compatible, `http://localhost:11434/v1`). Tools, messages and records identical across endpoints. `make verify` still passes (v2 records unaffected).
2. **Cost:** OpenRouter's charged cost as now; OpenAI from tokens times a price table; Ollama $0. The OpenAI price table is checked against OpenAI's official pricing page at build time, with the date recorded. Do not use models OpenAI is retiring (GPT-5, GPT-5 mini, GPT-5 nano, o3 shut down 2026-12-11).
3. **Truncation check on every call:** if the endpoint reports fewer prompt tokens than were sent (beyond a small tolerance for tokenizer differences), the cell fails loudly with `truncated`. For Ollama, set the context explicitly (e.g. 64k) and record it; verify the model plus that context fits in 32 GB before running.
4. **Key file:** a git-ignored `.env` at the repo root (add `.env` to `.gitignore` first, and check `git check-ignore .env` before anything else), lines `OPENROUTER_API_KEY=…` and `OPENAI_API_KEY=…`, permissions 600. A small loader in the client (no new dependency) reads it; variables already set in the environment win. Commit a `.env.example` with empty values. Never print, log or record a key, and never read the file's contents into a tool result or report. Matthias fills in the values himself.
5. **Model ids checked** before any paid run: one minimal call per model id (DeepSeek, GLM, the chosen OpenAI judge) confirms it exists and accepts tools (cost: a fraction of a cent). Record served model and provider.

STOP: report the fixes, the self-test, and the proposed OpenAI judge model with its verified price.

## 3 Local smoke test ($0)

- Ollama, one model that tool-calls reliably and fits 32 GB with a 64k context: try `gpt-oss:20b` first (large context headroom), else `gemma4:26b`. Record the tag and context.
- Cells: M01 and A1 (all four turns), N = 25, arms G, G+, T. Stub judge.
- Check by hand, one record per arm: tool calls and results round-trip; T's engine calls work; the `sql` tool works; the manager answer's JSON parses; records are complete; `score.py` and `--export` run end to end; no truncation.
- Results are plumbing only: never scored as findings.

STOP: report, with one record per arm summarised.

## 4 Paid smoke test (about $0.10–0.20 OpenRouter, cents OpenAI)

- The same cells on DeepSeek; one OpenAI Batch judge job on the three A1 sessions.
- Check: recorded costs match OpenRouter's, prompt caching visible (`cached_tokens`), the batch submit-and-collect works, judge output parses against the rubric.

STOP: report actual cost per cell and per judge session; recompute the pilot estimate from these actuals.

## 5 Pilot

- DeepSeek only; A1–A3 and the ten manager questions M01 M03 M08 M13 M16 M17 M19 M21 M46 M50; N = 25 and 200; arms G and T for the analyst tasks, G, G+ and T for the manager questions (G+ left out of the analyst tasks in the pilot only, to save cost; it returns for the full run, at least at N = 25 and 200, because without it the baseline is a straw man: Databricks itself recommends trusted assets).
- Judge: OpenAI Batch on the analyst sessions.
- Export 10 sessions for Matthias's hand grading.

STOP: report pilot results, actual costs, and a proposal for the full run (repetitions; G+ on analyst tasks, at least at N = 25 and 200; whether GLM runs all N or a subset; local model column) within the remaining OpenRouter budget.

## Gate

The `CLAUDE.md` gate for anything touching `spikes/v3/`; `bench/selftest.py` green before every paid step; `make verify` green after client changes.

## Decisions

(Executor: append dated entries — what was decided, why.)

- 2026-11-26 — PLAN-v3-bench harvested into HISTORY phase 10 under tag `spike-v3-bench`, then removed (standing rule).
- 2026-11-26 — §1.2 hard cap as reserve and settle: the reservation is the call's maximum cost, the prompt at 3 characters per token (an over-estimate for English and JSON) plus `max_tokens` of completion, at list price without caching. A model without a known price is refused rather than run unbounded.
- 2026-11-26 — §1.1 a call that raises keeps its reservation as its cost (`cost_estimated`): a failed paid call may still be charged, and the conservative figure keeps the cap hard.
- 2026-11-26 — §2.3 truncation: fails when the reported prompt tokens are fewer than one per 8 characters sent (no tokenizer gives that, so input was dropped), or, for Ollama, when prompt plus completion reach 98 % of the context. `finish_reason` "length" is not a failure: it is recorded, and the cell's answer is scored as given.
- 2026-11-26 — §2.1 endpoint chosen by the model name (`openai@`, `ollama@`, otherwise OpenRouter), so one run can mix them and each record names its endpoint; OpenRouter's request body is unchanged (selftest asserts it, `make verify` green).
- 2026-11-26 — the judge has its own budget (`score.py --budget`, default $2), since it is paid from the OpenAI credits, not the $10 OpenRouter cap.
- 2026-11-26 — §2.2 judge proposed: `gpt-6.2-sol`, Batch $1 / $0.05 / $5 per 1M input / cached / output (Standard $2 / $0.10 / $10), checked 2026-11-26 on developers.openai.com/api/docs/pricing; alternative `gpt-6.1-terra` at half that. The retired models are absent from the price table, so they cannot be run.
- 2026-11-26 — `--pilot` now means §5 (DeepSeek, A1–A3 and the ten manager questions, N 25 and 200, analyst arms G and T); `--pilot-cap` removed, `--budget` is the cap and the pilot refuses to start when its estimate exceeds it.
- 2026-11-26 — §2.4 model ids, one minimal call with one tool each (total $0.0006 OpenRouter). With the run's routing (fp8, sort by price): `deepseek/deepseek-v4.1-flash` served as itself by InferenceNet, `z-ai/glm-5.3` by Novita; both returned a well-formed tool call (finish_reason `tool_calls`). Without the quantization filter, Cloudflare and Friendli served them. The providers vary from call to call, and every call records its provider. The OpenAI judge id is not checked yet because `OPENAI_API_KEY` is not set.
- 2026-11-26 — §2.4 key file (plan step added by Matthias; the model-id check became §2.5, and the entry above that says §2.4 means it). `.env` added to `.gitignore` first, then `git check-ignore` confirmed. `openrouter.load_env()` reads only KEY=VALUE lines, skips empty values and comments, and lets variables already set in the environment win. It refuses a file that git does not ignore or that group or others can read, and no error message includes a value. `run.py` and `score.py` call it first, and `chat()` and the Batch client call it before every keyed request. `.env.example` is committed. Matthias had already created `.env` (mode 644). I tightened it to 600 without reading it; a check of which names are set printed only set or empty.
