# Spike v3 addendum — pruning to Python + Prolog, history, cleanup

Plan for Claude Code, 2026-11-25 (Matthias). Continue on branch `spike/v3`. Do not push. No API spend. Log deviations under **Decisions** at the end.

## 0 Why, and the rule

Platform decision (2026-11-25): **Python + Prolog**.
- Engine: SWI-Prolog via janus (V3a, memo mode, propagation).
- Oracle: `shared/reference.py` stays independent of the engine. It is never promoted to engine (the engine would then check itself).
- Integrity gate: shared Python (`model_check.py`, `integrity.py`).
- Fallback, documented only: a separate Python engine written from `SEMANTICS.md`, if SWI is refused at JPMC.
- Dropped: V3b (Clojure), V3c (Elixir), V3d (Flix), V3e (Clingo). Blocking semantics is retired.

Standing rules are in the repo's `CLAUDE.md` (new, 2026-11-25); commit it in step 1. Housekeeping rule: **a file stays only if a current claim cites it.** Everything else becomes history: summarised in `HISTORY.md`, kept recoverable through a git tag, then deleted. One living doc per topic; executed plans collapse into HISTORY.

## 1 Tag first

Commit any pending change (PROGRESS.md has one). Then tag the current state: `spike-v3-five-platforms`. Every deleted file must be reachable from this tag; HISTORY points to it.

## 2 `spikes/v3/HISTORY.md`

Harvest, before deleting anything: every PLAN's **Decisions**, every RESULTS section, PROGRESS, `SEMANTICS-cycles.md`. Target: two to three pages, prose plus small tables. Per phase (initial V3a/V3b, V3a fixes, V3c/V3d, cycles, integrity, pruning):
- the question it asked;
- what was built (one line);
- decisions and why;
- findings that still hold;
- findings later reversed, and by what (first example: defeat cycles answered by WFS/ASP, then rejected at load by IR-001a);
- the commit range.

Then **platform lessons**, one short paragraph each, kept even though the platform is dropped:
- V3b: database transaction time is not assertion time (bitemporal lesson); `d/with` hypotheses as values.
- V3c: supervision and 8-process throughput; `ex_datalog` cannot run the defeasible meta-program.
- V3d: compiler catches 9/10 planted type defects, but not in rules loaded at runtime; Fixpoint path lacks a negative-cycle check.
- V3e: an ASP unsat core names cycle members for free; xclingo 2.0b24 broken under clingo 5.8.0; per-op grounding dominates latency; demand needs a magic-set rewrite.
- All: "rules are data, interpreted at runtime" mattered more than the platform; independent re-verification of proof trees was the main correctness tool.

Close with the decision and its rationale (§0), and the fallback.

## 3 Delete

After HISTORY is committed:
- `v3b-clojure/`, `v3c-elixir/`, `v3d-flix/`, `v3e-clingo/`.
- V3a's WFS mode (tabled `wdef`/`wovr`/`wbeat`, `ENGINE_MODE`, table keying); memo is the only mode. Remove the switch, not just the default.
- `reference.py --semantics blocking`, `accept.py --semantics blocking`, the `Cyc` class if nothing else uses it.
- `cycles.edn` (superseded by `cycles-acyclic.edn` and `fixtures/integrity/`), `SEMANTICS-cycles.md` (in HISTORY; `SEMANTICS.md` is the spec).
- Executed plans: `PLAN.md`, `PLAN-v3a-fix.md`, `PLAN-v3cd.md`, `PLAN-v3-cycles.md`, `PLAN-v3-integrity.md`. This plan is deleted by the next one.
- Results files of deleted engines and of retired modes. Keep `results/key-diff-propagation.md` only if RESULTS cites it.
- `capabilities.json` and the `cycles: reject | report` flag, if only one engine remains: reject is the only behaviour. Keep `model_check.py --cycles` as a diagnostic.
- Anything else under `spikes/v3/` that no current file cites. List each removal in Decisions.

Keep: both backends (DuckDB, Postgres), `isolation.py`, `bench.py`, `check_why.py`, the guard probe for V3a memo, the LinkML model (V3a's negatives use it).

## 4 Rewrite the living docs

- **`RESULTS.md`**: current state only, at most about 150 lines. What System A is (shape, contract, semantics, integrity gate), V3a's §7 rows, latency, what is built vs native, known residuals (IR-005 scope; aggregation over derived literals; qualifier on negative answers; the three v3 preconditions in the Tolaria note `v3-next-decisions`), the fallback. No reversed findings: those live in HISTORY.
- **`PROGRESS.md`**: reset. Status of the current state, and only questions still open (2, 3, 5 fold into the platform decision: mark answered; 10 stays open, deferred with the vocabulary work).
- **`shared/CONTRACT.md`**, **`SEMANTICS.md`**, `README` files: remove references to deleted engines and modes.

Gate: `reference.py` keys byte-identical to before this plan. V3a GREEN on `accept.py` 1–8, `--mutation`, `isolation.py`, negatives 15/15, `bench.py` on DuckDB and Postgres; guard probe still 2/2.

## 5 Repo-wide inventory (proposal only, no deletion)

v1 and v2 material outside `spikes/` (`results/` with 68 files, `REWORK.md`, `paper/v1`, `paper/v2`, `worlds/`, `rules/`, `harness/`, `engine/`, `render/`, `verify/`, `questions/`). Write `INVENTORY.md` at the repo root: per file or directory, who cites it (paper v2 section, README, a script), and a proposal: keep, history, delete. Also a skeleton for a root `HISTORY.md` (v1, v2, v3 spike), headings and one line each. Matthias decides before anything is removed; the paper consolidation depends on it.

## Decisions

(Executor: append dated entries — what was decided, why.)

- **2026-11-25 §3 removals.** Every one is reachable from the tag `spike-v3-five-platforms`.
  - Engines: `v3b-clojure/`, `v3c-elixir/`, `v3d-flix/`, `v3e-clingo/` (`git rm`). Their untracked build output (about 850 MB: Clojure classes and `.cpcache`, Elixir `_build`/`deps`, the Flix jar and lib cache) was deleted from disk too. The three `v3b-clojure` lines were dropped from `.gitignore`.
  - V3a WFS mode, switch included:
    - `defeasible.pl` −185/+12: the `eval_mode`/`table_policy` flags and setters, `clear_tables`, the tabled `wdef`/`wovr`/`wbeat` section, the wfs clauses of `prove`/`evaluate`/`lit`, and the two-valued `supporters`/`attackers`/`classify`/`candidate`, which were now unused;
    - `ops.pl` −41/+6: the `undefined` branches, `candidate_instance`, `drop_state_tables` and `table_test`;
    - `host.py` −7: `ENGINE_MODE`, `V3A_TABLES` and the `table_test` output.
  - Blocking: `reference.py --semantics blocking`, the classes `Cyc` and `answer_acyclic_blocking` (−167/+10), and `accept.py --semantics` and `--mode` (−17/+4).
  - `shared/cycles.edn` and `shared/SEMANTICS-cycles.md`.
  - The executed plans: `PLAN.md`, `PLAN-v3a-fix.md`, `PLAN-v3cd.md`, `PLAN-v3-cycles.md` and `PLAN-v3-integrity.md`.
  - `results/key-diff-propagation.md`. The new RESULTS does not cite it, because the key diff is a change against the retired semantics, which is history; HISTORY phase 5 records it. `spikes/v3/results/` is gone with it.
  - `v3a-prolog/capabilities.json`, and the `cycles: reject | report` flag in `model_check.py`, including `--engine`/`--mode` and `engine_flag`. A negative cycle is now always an error. `--cycles` and `--fixture` stay as diagnostics, and the CLI still prints the cycle report before the verdict.
  - All 24 files under `v3a-prolog/results/`: mode-suffixed outputs of memo, wfs, blocking and propagation, plus `table-test.json`. They were regenerated by the gate under plain names (see below), not kept, because every old file described a mode or a point in time that no longer exists.
- **2026-11-25 kept, although they mention retired material.**
  - The `PLAN-v3-…` § citations in code and fixture comments (for example "PLAN-v3-integrity §3.2"). The plans are reachable through the tag, which HISTORY names. Rewriting the citations would lose the pointer to the decision.
  - `shared/gen.py`, which PROGRESS, REWORK and the Makefile cite.
  - `hyp_latency.py`, which RESULTS cites for hypothesis latency.
  - The LinkML artefacts (`ddl_compare.md`, `physical*`, `slice.instance.yaml`, `docs/`), which `build.py` generates or cites.
  - Mentions of V3b's Malli negatives in `build.py` and in the generated `negatives.md`, reworded to "first written for V3b's Malli model" as provenance.
  - The comments in `cycles-acyclic.edn` and the two loop fixtures now say "cycles.edn, tag spike-v3-five-platforms".
- **2026-11-25 `prove/3` on a non-ground goal now enumerates `candidate3`**, not the removed two-valued `candidate`. `prove` keeps only proven instances, so the result is the same. The gate confirms it: keys are byte-identical and checks 1–8 pass.
- **2026-11-25 SEMANTICS.md** now cites Maier arXiv 1106.1957 directly, not through `SEMANTICS-cycles.md`. Its blocking paragraph is replaced by a pointer to HISTORY.
- **2026-11-25 Gate**, from the repo root, with outputs in `v3a-prolog/results/`:
  - `reference.py`: `keys.json` matches `keys-before-housekeeping.json` byte for byte (`cmp`).
  - `accept.txt`: GREEN 1–8.
  - `mutation.txt`: check 1 FAIL, mutation test OK.
  - `isolation-{duckdb,postgres}.txt`: PASS.
  - `negatives.txt`: 15/15 (`build.py`).
  - `bench-{duckdb,postgres}.json`: 0 errors, 11.17 SQL per decide.
  - `guard-probe.{txt,json}`: 2 of 2.
  - `hyp-latency-{duckdb,postgres}.json`.

  One defect was introduced and caught here. Removing the engine flag left a stray `}` in `model_check.py`'s summary f-string, which made `accept.py` fail on import. It was fixed before the gate run that counts.
- **2026-11-25 Not removed:** `clingo` and the other V3e packages in `.venv`. The plan did not ask for it, so this is PROGRESS question 1.
- **2026-11-25 §5 inventory:** `INVENTORY.md` at the repo root, a proposal only; nothing outside `spikes/` was removed.
  - The root `HISTORY.md` skeleton is a section of `INVENTORY.md`, not a file of its own. A root HISTORY now would anticipate decisions Matthias has not made.
  - `world/` was added, although the plan's list omits it: `spikes/v3/shared/gen.py` imports `world.domain`.
  - "68 files" in `results/` are the files on disk other than `.gitkeep`: 44 tracked (20 reports, 24 `.jsonl.gz`) and 24 untracked plain `.jsonl` copies.
  - `m6-compile-L3-preR314` was first proposed for history, then changed to keep. The 24 `.gz` files sum to 8,878 records, which is paper v2's total, so that run is counted in the paper.
