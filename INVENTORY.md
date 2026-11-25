# Repo inventory (proposal, 2026-11-25)

Written for `spikes/v3/PLAN-v3-housekeeping.md` §5. **This is a proposal only. Nothing is removed until Matthias decides**, and the paper consolidation depends on the outcome.

The rule applied is the one in `CLAUDE.md`: a file stays only if a current claim cites it. Superseded material is summarised in a `HISTORY.md`, tagged, then deleted.

Proposals:
- **keep**: cited by a current claim or needed to reproduce one.
- **history**: summarise in the root `HISTORY.md`, reachable through a tag, then delete.
- **delete**: no claim depends on it.

"Cites" means the path or file stem appears in a tracked file outside the entry itself (`rg`). The gate commands named are those in `CLAUDE.md`.

## Top level

| Entry | Who cites it | Proposal |
|---|---|---|
| `README.md` | (entry point) | **keep, update.** It still says "v2 is under construction". v2 is finished (paper v2, M7), and spike v3 is not mentioned. |
| `CLAUDE.md` | (standing rules) | keep |
| `Makefile` | README; `CLAUDE.md` (`make verify`, `make verify-v1`) | keep |
| `requirements.txt` | README, REWORK | **keep, update.** It lists only v2's deps (pyyaml, litellm, matplotlib). Spike v3's deps (duckdb, psycopg, janus-swi, linkml, edn_format) are installed in `.venv` but not recorded. The leftover V3e packages (clingo and others) are still in `.venv`. |
| `REWORK.md` (584 lines) | README, Makefile comment, `paper/v2/PAPER.md` (§3 hypotheses; costs "listed in REWORK.md, Decisions"), `paper/v2/README.md` | **history, after the paper consolidation.** It is v2's executed plan and decision log: by the housekeeping rule, an executed plan collapses into HISTORY. The paper still points into its Decisions for costs and derivations, though. Either the consolidated paper carries those numbers, or it cites the tag. Until then, keep. |

## Paper

| Entry | Who cites it | Proposal |
|---|---|---|
| `paper/v1/` (PAPER.md, whitepaper.pdf, 2 figures, README) | README, REWORK §1, paper v2 [11] | **keep.** It is a frozen report. Its studies live at tag `v1`, and `make verify-v1` checks them. |
| `paper/v2/` (PAPER.md, README) | REWORK (M7) | **keep.** It is the current paper, and the consolidation target. |

## v2 code (`make verify` depends on all of it)

| Entry | Who cites it | Proposal |
|---|---|---|
| `world/` (gen.py, domain.py, schema.yaml) | Makefile `worlds`, `verify/check.py`, `render/common.py`, `engine/core.pl`, `questions/sample.py`; **`spikes/v3/shared/gen.py` imports `world.domain`** | **keep.** It is the generator of v2, and spike v3's world depends on it. (Not in the plan's list, but cited.) |
| `rules/rules.yaml` | engine, render, verify, `harness/score.py`, `world/domain.py`; spike v3 PROGRESS question 10 (R301 "may approve") | **keep.** It is the source of truth for the v2 rule records. |
| `render/` | `world/gen.py`, `verify/check.py`, `engine/capability.pl` | keep |
| `engine/` (`ask`, *.pl) | harness, verify, questions, `world/gen.py`; README (`engine/ask`) | keep |
| `verify/` | Makefile `verify`, `questions/bank.yaml` | keep (the M1 test) |
| `questions/` (bank.yaml, sample.py) | `world/gen.py`, `verify`, `harness/score.py` | keep |
| `harness/` (run, read, compile, score, openrouter) | README, paper v2 §reproducibility (`harness/score.py`), paper v2 README | keep: it rescores every committed run |
| `worlds/` (9 worlds, 227 files, 8.8 MB) | README, `verify/check.py` (freshness), `world/gen.py`; the inputs of every run in `results/` | keep: `make verify` checks they are what the generator produces |

## `results/`

There are 69 files on disk: 45 tracked (20 Markdown reports, 24 `*.jsonl.gz` raw records, `.gitkeep`), plus 24 plain `*.jsonl` working copies that git ignores (`.gitignore`, README). Paper v2 §reproducibility cites the whole set: "every raw record (`results/*.jsonl.gz`) and the scored reports (`results/*.md`)". Its README adds: "Every number in it comes from a scored report."

| Files | Who cites them | Proposal |
|---|---|---|
| The 20 `*.md` reports | paper v2 (as a set); REWORK by name for m2, m2a-assume, m2a-models, m3, m4 (×2), m5 (read, explain), m6 compile L0/L2-open, `m6-{read,compile}-L3-c5-{decided,open}`, `m6-{read,compile}-L3-size-*`, m7-glm | **keep.** `m5-read-L3-open` and `m7-read-decided-L0-L3` are not cited by name. The second is the pooled DeepSeek read report behind H1/H2 (4,728 records). Have the consolidated paper cite both. |
| The `*.jsonl.gz` behind a report | paper v2 (as a set) | **keep.** Without them no report can be rescored. |
| `m2a-read-L0-{deepseek,glm-5.3,qwen3.8-flash}.jsonl.gz` | none by name; inputs of `m2a-models-L0.md` (REWORK line 279) | keep |
| `m2a-pilot-L0-glm-5.3-medium.jsonl.gz` | REWORK line 283 ("kept in `m2a-pilot-…-medium.jsonl`", the evidence for effort high) | keep, or **history** if REWORK goes to history |
| `m6-compile-L3-preR314-deepseek-v4.1-flash.jsonl.gz` | REWORK line 561 ("set aside … superseded by the fix and not scored") | **keep.** It is superseded and unscored, but its 142 records are part of paper v2's total: the 24 `.gz` files sum to exactly 8,878, and the cost of $8.11 counts them as well. To remove it, the consolidated paper must first restate the total, or say that the run is held at a tag. |
| plain `*.jsonl` (24, untracked) | `.gitignore` (working copies) | **delete** locally. They duplicate the `.gz` files, and `score.py` reads the `.gz` directly. |

## `spikes/`

| Entry | Who cites it | Proposal |
|---|---|---|
| `spikes/v3/` | its own RESULTS, PROGRESS, HISTORY | **keep.** It was pruned by `PLAN-v3-housekeeping.md`, and the tag `spike-v3-five-platforms` holds the rest. |

## Skeleton for a root `HISTORY.md`

One HISTORY per repo, superseding nothing yet. `spikes/v3/HISTORY.md` either stays as the detailed chapter or folds into it.

```
# llm-policy-reasoning history

## v1 — Rules in Context (2026-09; tag v1, 0818ce3..24973ef)
Does notation matter, and when is an engine needed? Written decisions mattered, notation did not; the engine earned its place at scale.

## v2 — Layers of Meaning (2026-11-22..23; c9e8ab3..b228dca, REWORK.md M0–M7)
Which layer (L0–L3) does a question need, in which representation and mode? H1 and H5 confirmed, H2 qualified, H3 wins on contradiction, H4 falsified; $8.11.

## v3 spike — System A (2026-11-24..25; fcd9480.., tag spike-v3-five-platforms)
Rules and claims as data, a defeasible engine over bounded SQL fetch; five platforms explored, Python + Prolog chosen (spikes/v3/HISTORY.md).
```
