# Spike v3 progress (branch spike/v3)

Updated as work proceeds; newest first.

## Status

- [x] Shared world: `shared/gen.py` (1969 cc, 20k emp, 100k req; DuckDB and Postgres 18 identical, `--check`)
- [x] `shared/slice.edn`, `extension.edn`, `questions.edn` (Q01–Q23), `reference.py` → `keys.json` (extension changes Q07, Q14)
- [x] `shared/CONTRACT.md`: CLI session script, ops, why-tree shape
- [ ] `shared/check_why.py`, `shared/accept.py`
- [ ] V3a (LinkML · SWI-Prolog · DuckDB/Postgres)
- [ ] V3b (EDN/Malli · Clojure · Datahike)
- [ ] RESULTS.md

## Questions for Matthias

(Decisions taken without you are logged in PLAN.md → Decisions; these are the ones worth a look.)

1. Tooling: Postgres 18 via `brew services` (socket /tmp:5432, db `spike_v3`); clojure + babashka via brew; Python deps via uv into `.venv`. OK to keep the brew service running?
