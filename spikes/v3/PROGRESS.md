# Spike v3 progress (branch spike/v3)

Updated as work proceeds; newest first.

## Status

- [x] Shared world: `shared/gen.py` (1969 cc, 20k emp, 100k req; DuckDB and Postgres 18 identical, `--check`)
- [x] `shared/slice.edn`, `extension.edn`, `questions.edn` (Q01–Q23), `reference.py` → `keys.json` (extension changes Q07, Q14)
- [x] `shared/CONTRACT.md`: CLI session script, ops, why-tree shape
- [x] `shared/check_why.py`, `shared/accept.py` (mutation test: check 1 fails on mutated keys, as it must)
- [x] V3a engine GREEN on checks 1–6 (2026-11-24, session 1). Bugs on the way: forall/2 not binding fetch outputs; dict `.key` inside yall lambdas expands too early; evaluate/3 called with a bound result skipped classify's cut and "proved" goals with no supporter
- [x] V3a LinkML model (`v3a-prolog/linkml/`, one command: `.venv/bin/python spikes/v3/v3a-prolog/linkml/build.py`): schema `slice.yaml` and the converted slice validate; the 53 EDN rule/claim strings parse; docs via gen-doc (`docs/schema/`) plus instance docs `docs/slice.md` (G-arm material); DDL via gen-sqlddl compared with gen.py in `ddl_compare.md` (no keys in the slice model → 29/31 columns differ; with keys added only the composite PKs differ, they come out as UNIQUE; no indexes). The concept "sql or derived_by" rule is not enforced by linkml-validate
- [x] V3b engine GREEN on checks 1–6 on the first full run (2026-11-24, session 2); mutation test fails as required. Defects on the way were in glue, not semantics: Malli recursive schemas (need `[:ref]`, and `[:schema [:ref]]` inside seqex), data.json pushback overflow on stdin, environ printing a JAVA_HOME warning on stdout
- [x] V3b model (`clojure -M:model`): slice + extension validate natively (rule bodies included); 12/12 negative tests rejected, including the concept sql-or-derived rule LinkML did not enforce; `docs/slice.md` identical to V3a's below the header; `docs/why-node.schema.json` from Malli; all 350 why roots of a check-1 run conform
- [x] V3b probes (`clojure -M:probe`): who-said-it attributes vs tx-meta, as-of on tx vs valid time, C1 history via `d/as-of`, hypothesis branch vs `d/with`
- [x] `shared/bench.py`: decide p50/p95, cold start, max RSS for any CLI
- [x] RESULTS.md: "What we learned about the architecture", §7 table, LOC, performance (DuckDB + Postgres), recommendation (V3b's architecture shape; engine either). Readability left to you

## Questions for Matthias

(Decisions taken without you are logged in PLAN.md → Decisions; these are the ones worth a look.)

1. Tooling: Postgres 18 via `brew services` (socket /tmp:5432, db `spike_v3`); clojure + babashka via brew; Python deps via uv into `.venv`. OK to keep the brew service running?
2. RESULTS recommends V3b's *shape* (rules as data + schema into bodies + immutable state, hypotheses as values), not its engine. Does that framing match what you wanted from an exploration, or do you want a stack-level pick?
3. Optional search (Scriptum/Lucene, HNSW) was skipped: plain Datalog matching passes check 6. Worth a follow-up?
4. V3b's `d/with` hypothesis mode is verified by probe/timing, not by `accept.py` (which has no config switch for it). Add one?
