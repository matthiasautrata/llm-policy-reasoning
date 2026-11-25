# Spike v3 progress (branch spike/v3)

Updated as work proceeds; newest first.

## Status

- [x] PLAN-v3cd V3d, Flix 0.80.0 (2026-11-24, committed locally, not pushed). Results:
  - GREEN 1–6, mutation fails as required; isolation PASS and bench on DuckDB and Postgres; 12/12 negatives.
  - It runs an own evaluator. Probes for runtime rules as Flix Datalog: 16/19 slice rules reach the solver via the `Fixpoint3` AST, but that path has no negative-cycle check, is bottom-up only, and needs a demand domain. The reified meta-program is about 45× slower. Codegen would cost 9.6 s per rule change.
  - The lattice works for standing, not for defeat. 9/10 planted type defects are caught (V3c: 4/10). 8 threads give 3.4× throughput.
  - RESULTS.md has a new section, "V3c and V3d": the §7 table in four columns, answers to §1.2 and §2.2, architecture additions, and the four-platform revisit.
- [x] PLAN-v3cd V3c, Elixir 1.20.5 / OTP 29.1.2 (2026-11-24, committed locally). Results:
  - GREEN 1–6, mutation, isolation and bench on both backends; 12/12 negatives.
  - It runs an own evaluator, because ex_datalog rejects the defeasible meta-program.
  - Probes: supervision, 1 vs 8 processes, hot reload, types.
- [x] PLAN-v3a-fix (2026-11-24, committed locally, not pushed): F1 V3a hypotheses via `snapshot/1` with a state-keyed memo, and `shared/isolation.py` (V3a snapshot PASS, old assert mode FAIL, V3b branch and with PASS, DuckDB and Postgres); F2 LinkML rule bodies structured, 12/12 negatives, class rule now enforced (two LinkML pitfalls found); F3 both spikes still GREEN 1–6 with mutation failing as required, benches rerun. RESULTS.md has a new section "After the V3a fixes": neither deciding fact of the original Recommendation still holds
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
4. ~~V3b's `d/with` mode is untested by `accept.py`~~: now covered by `shared/isolation.py --hypothesis with`.
5. With both deciding facts gone, RESULTS ends in "carry forward the shape; the stack is open". Is a tie-break wanted (for example, trying F1.6, state-as-value in Prolog), or is the trade-off list enough?
6. V3d found that the slice's `pending_exposure` SQL (`CAST(SUM(...) AS INTEGER)`) overflows when it is evaluated for the root centre. No question asks that, so the top-down engines never hit it. Should the shared slice be fixed (`BIGINT`)?
7. RESULTS architecture point 3: rules as data lose the compiler's stratification and range-restriction checks, and no model checks them. Should a moded safety check and a stratification check go into the model validators as a follow-up?
8. The four-platform revisit ends with "the stack is open; pick by secondary property": resilience and concurrency (V3c), static guarantees (V3d), audit time (V3b), footprint (V3a). Is that the framing you want, or is a next spike wanted to combine two, such as the shape in Flix with typed rows per concept?
