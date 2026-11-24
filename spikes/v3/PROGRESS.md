# Spike v3 progress (branch spike/v3)

Updated as work proceeds; newest first.

## Status

- [x] Shared world: `shared/gen.py` (1969 cc, 20k emp, 100k req; DuckDB and Postgres 18 identical, `--check`)
- [x] `shared/slice.edn`, `extension.edn`, `questions.edn` (Q01–Q23), `reference.py` → `keys.json` (extension changes Q07, Q14)
- [x] `shared/CONTRACT.md`: CLI session script, ops, why-tree shape
- [x] `shared/check_why.py`, `shared/accept.py` (mutation test: check 1 fails on mutated keys, as it must)
- [x] V3a engine GREEN on checks 1–6 (2026-11-24, session 1). Bugs on the way: forall/2 not binding fetch outputs; dict `.key` inside yall lambdas expands too early; evaluate/3 called with a bound result skipped classify's cut and "proved" goals with no supporter
- [x] V3a LinkML model (`v3a-prolog/linkml/`, one command: `.venv/bin/python spikes/v3/v3a-prolog/linkml/build.py`): schema `slice.yaml` and the converted slice validate; the 53 EDN rule/claim strings parse; docs via gen-doc (`docs/schema/`) plus instance docs `docs/slice.md` (G-arm material); DDL via gen-sqlddl compared with gen.py in `ddl_compare.md` (no keys in the slice model → 29/31 columns differ; with keys added only the composite PKs differ, they come out as UNIQUE; no indexes). The concept "sql or derived_by" rule is not enforced by linkml-validate
- [ ] V3b (EDN/Malli · Clojure · Datahike)
- [ ] RESULTS.md

## Questions for Matthias

(Decisions taken without you are logged in PLAN.md → Decisions; these are the ones worth a look.)

1. Tooling: Postgres 18 via `brew services` (socket /tmp:5432, db `spike_v3`); clojure + babashka via brew; Python deps via uv into `.venv`. OK to keep the brew service running?
