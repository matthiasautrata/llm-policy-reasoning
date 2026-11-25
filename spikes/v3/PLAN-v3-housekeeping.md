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
