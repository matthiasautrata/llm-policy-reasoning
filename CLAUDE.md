# llm-policy-reasoning — standing rules

Applies to every session and every plan. A plan states only what is specific to it; where a plan and this file conflict, the plan wins for that plan, and the conflict is logged in its Decisions.

## Working

- An explicit instruction is action; a question is discussion. Present options with trade-offs before building anything non-trivial; flag assumptions.
- Minimal and precise: derive rather than declare, unify duplicates, no filler. Fix at the source of truth (slice, spec, generator) and regenerate; never hand-edit generated files.
- Plans live in `spikes/v3/PLAN-*.md` while being executed. Each has a **Decisions** section: append dated entries (what, why) for every deviation or choice the plan left open.
- Dates ISO 8601. Record library and tool versions when a result depends on them.

## Git and spend

- Commit per phase or logical step, message `area: summary`. Stage explicit paths.
- Never push unless asked. No API spend unless the plan sets a budget.
- Ask before installing system software; language-level dependencies are fine.

## Housekeeping

- A file stays only if a current claim cites it. Superseded material is summarised in a `HISTORY.md` (question, decisions and why, findings kept, findings reversed and by what, commit range), then deleted.
- Tag before deleting, so that every removed file is reachable; HISTORY names the tag.
- One living doc per topic, describing the current state only. Reversed findings belong in HISTORY, not in RESULTS. An executed plan is harvested into HISTORY and removed.
- Docs change in the same commit as the code they describe.

## The v3 system (spikes/v3)

- Platform: Python + Prolog. Engine: SWI-Prolog via janus (`v3a-prolog`). Oracle: `shared/reference.py`, independent of the engine; never make it the engine. Fallback if SWI is refused: a separate Python engine written from the spec.
- Spec: `shared/SEMANTICS.md` (three-valued, ambiguity propagation: anything downstream of a contested conclusion is contested). Contract: `shared/CONTRACT.md`. Data rules: rules and claims are data loaded at runtime; detail data stays in DuckDB/Postgres and is reached only through `fetch`.
- Integrity checks run at load, `add` and `with_hypothesis`, in one shared Python gate (`shared/model_check.py`, `shared/integrity.py`). Cycles are rejected, never answered. The ledger of checks (IR-nnn) is kept by Matthias outside the repo; a new or changed check is proposed to him, and its id is cited in code and fixtures.
- Keys (`shared/keys.json`) come only from `reference.py`. A changed key is either listed with its reason in the plan's results or it is a bug.

## Gate for every change to spikes/v3

Run from the repo root with `.venv/bin/python`:

- `spikes/v3/shared/reference.py`, then `git diff --stat spikes/v3/shared/keys.json` (no unexplained change)
- `spikes/v3/shared/accept.py --cli spikes/v3/v3a-prolog/cli` (all checks), and again with `--mutation` (must fail check 1)
- `spikes/v3/shared/isolation.py --cli spikes/v3/v3a-prolog/cli` on DuckDB and Postgres
- the negatives (LinkML model) and the guard probe, as their scripts document

v1 and v2 (outside `spikes/`): `make verify`; `make verify-v1` for the frozen v1 tree.
