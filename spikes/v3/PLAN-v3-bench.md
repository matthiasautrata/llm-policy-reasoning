# v3 benchmark — build and pilot

Plan for Claude Code, 2026-11-25 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. Design (normative for this plan): the Tolaria note `warrant-layer/benchmark-design.md`; its content relevant here is restated below. **API spend: $10 hard cap for everything in v3, pilot included.** The full run is not part of this plan.

## 0 Housekeeping

- Harvest `PLAN-v3-sqlform.md` into `HISTORY.md` (one entry) and delete it.
- RESULTS residual: `flush()` still batches as `UNION ALL` when more than one filter column varies (the memory blow-up pattern). The generator (§2) must not produce such shapes silently: report any it would.
- PROGRESS question 1 is answered: Postgres is uninstalled (Matthias, 2026-11-25); the untracked `results/*.jsonl` copies are deleted. Remove `__pycache__` directories if deletion is permitted; otherwise leave them.

## 1 Layout

New top-level `bench/` for the benchmark; the engine stays in `spikes/v3/` and is called through its CLI (`CONTRACT.md`). Reuse from v2's `harness/`: `openrouter.py` (client, cost per call), the runner's budget tracking, and the scoring scaffold. New: task format, arms, generator, renderer, judge.

## 2 Rule and claim generator (the curve's x-axis)

- `bench/gen.py` produces rule bases at **N = 25, 50, 100, 200** (rules plus claims) as supersets of the slice, from **families** with realistic interaction: dated limit versions, exceptions and exceptions to exceptions, owner disputes with and without superiority, claims with required and supporting sub-claims, later-wins within one asserter, distractor rules irrelevant to the tasks.
- Knobs as parameters: N, interaction density (exceptions, precedence, conflicts per 100 rules), distractor share. Seeded and reproducible.
- **Oracle stays independent.** `reference.py` re-implements rules by hand, so it cannot read generated rules. Implement each *family* once in `reference.py`, by hand and parameterised from its documented meaning, never by interpreting the generated EDN. Keys for every generated base come from there.
- Every generated base passes the integrity gate; the generator rejects its own output otherwise.
- The schema and data stay at slice size (decided): only rules and claims grow.

## 3 Material for G, generated from the same source

- `bench/render_md.py` renders each rule base as the best markdown a careful Genie or Cortex user would write: structured as Databricks recommends (focused sections, definitions, rules with owners and dates, examples), from the rules' `:doc` texts, owners, validity, superiority, and the claims with asserters and validity. Plus schema docs and a few example SQL queries.
- **Completeness check:** every rule and claim id of the base appears in its markdown; nothing T knows is withheld from G.
- **G+** adds trusted functions (parameterised SQL) for the five most frequent manager questions, generated from the rules and checked against the oracle. Other questions fall back to G.

## 4 Tasks

- **Analyst:** A1, A2, A3 from the design note, each a scripted session of four turns, with gold reasons (id, text, rules or claims, turn). Store as data under `bench/tasks/`. Where a design component has a checkable value, record the expected value from `reference.py` so its SQL can be checked mechanically.
- **Manager:** the slice questions rephrased as a manager would ask, department scope, under `bench/questions/`.
- **R311 threshold (decided by Matthias, 2026-11-25):** software requests are auto-approved under **1,000**, not 10,000. Change R311 (`:doc`, body) and the hand-written rule in `reference.py` before §2; regenerate keys and list every changed key with its reason; gate as usual. A2 GR3 already says 1,000.

## 5 Arms and runs

- **G:** markdown plus schema docs plus examples in the prompt; read-only `sql` tool.
- **G+:** G plus the trusted functions.
- **T:** tools `resolve_term`, `describe`, `decide`, `why`, `why_not`, read-only `sql`, through the V3a CLI. Every tool call is logged where the tool runs, never inferred from model output.
- Models: DeepSeek and GLM (the v2 models via OpenRouter). Judge: Claude Sonnet via OpenRouter, a family not under test.
- Every call records model, provider, tokens, cost and time (as v2).

## 6 Scoring

- **Manager:** status, value, sides, qualifier against the keys (mechanical).
- **Analyst:** per gold reason *covered / missed / wrong*. Mechanical where possible: SQL of a component run and compared with the oracle value; cited rule or claim ids. Otherwise the judge, with a fixed rubric (text in the repo). Export 10 sessions, stratified by arm and N, to `bench/grading/` for Matthias to grade by hand; report judge agreement.
- **Both:** cross-question consistency, silent interpretation (undecided term answered as decided), inlining (T re-implementing a governed rule in its own SQL), cost and tokens per correct answer.

## 7 Pilot (only spend in this plan)

- N = 25 and N = 200, one repetition, both models, all three arms, all three analyst tasks and the manager questions; judge on the analyst sessions.
- Before any call: estimate tokens and cost per cell from prompt sizes (G grows with N) and print the estimate for the full design (N 25–200, repetitions to be proposed). If the pilot itself would exceed $3, stop and report instead.
- After the pilot: actual cost per cell, the projected full-run cost, and a proposal for the full run (repetitions, which cells) that fits the remaining budget. **Stop there; Matthias decides the full run.**

## 8 Gate

The `CLAUDE.md` gate for anything touching `spikes/v3/`, plus: generator determinism (same seed, same bases), oracle keys for every generated base, completeness check of the markdown, the harness stops at the budget cap (tested with a tiny cap and a fake client).

## Decisions

(Executor: append dated entries — what was decided, why.)

- 2026-11-25, §0: `PLAN-v3-sqlform.md` is HISTORY phase 9, tag `spike-v3-sqlform` (73e4014). The `UNION ALL` shape is RESULTS residual 6. PROGRESS question 1 is removed as answered: Postgres is uninstalled (checked: `brew list postgresql@18` fails), no `results/*.jsonl` copies remain, and every `__pycache__` outside `.venv` is deleted.
- 2026-11-25, §4, R311 threshold (Matthias, after the executor raised it): kept at **10,000**. At 1,000 no request in the data would qualify (the smallest amount is 3,000, v2 `AMOUNTS`), so R311/R312 would never fire and the slice's one auto-approval conflict (r000001, R312 vs R314) would vanish, leaving A1 GR8 and A2 GR6 nothing to show. A2 GR3 is stated at 10,000 in the task data instead. No key changes.
- 2026-11-25, §2, meaning of N (Matthias): **rules only**. N = 25 is the slice's 24 rules plus R307 from `extension.edn`; N = 50/100/200 add 25/75/175 generated rules. Claims grow in proportion (14 per 25 rules, as in the core) and are reported, not counted.
- 2026-11-25, §2, slice predicates (Matthias): **read, never conclude**. Generated families have their own predicates and may read slice predicates (`programme_cleared` reads `vendor_cleared`). Every slice key therefore holds at every N, and `check_bases.py` checks this: the 37 slice questions on each base against `keys.json` (extended).
- 2026-11-25, §2, vocabulary: one fixed predicate per family, with the instance code first (`[:programme_limit_ok "P03" ?r]`), so `modes.edn` gains one fixed section (`"-+"`, as inferred) and not one entry per instance. All limit versions are defined by one owner (procurement), since IR-002 rejects a `:definition` predicate defined by two owners. Disputes use a defeasible rule against a defeater, not two definitions.
- 2026-11-25, §2, base files: `bench/bases/N*.edn` is the slice map's text with the generated assets, terms, rules and claims spliced in before each closing bracket, so the comments survive; `extension.edn` is loaded beside it. The generated files are committed: they are the task data the arms read, and they are reproducible from the seed (checked byte for byte).
- 2026-11-25, §2, fetch shapes: generated rules filter fetches on the key only and compare constants in the body, so they add no `UNION ALL` shape. The report (`gen.py` output, `params.json` `report.union_all`) finds one shape at every N, the slice's own: `request` on `category` with `capital` and `software` (R112, R311), reached from `approved` and the predicates built on it. Generated rules use no aggregate, no `:not` and no measure fetch, so IR-005 never applies to them.
- 2026-11-25, §2, density: "interactions per 100 rules" counts exceptions, counter-exceptions, owner disputes and authority superiority rules over the whole base, including the core's 4 (R306, R307, R313, R314). The default 20 gives 10/20/40 at N = 50/100/200. A third of the disputes have no superiority (CONFLICT), a third favour each side.
