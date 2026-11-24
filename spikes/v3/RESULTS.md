# Spike v3 results: System A in two architectures

V3a: LinkML · SWI-Prolog · DuckDB/Postgres (`v3a-prolog/`).
V3b: EDN/Malli · Clojure · Datahike · DuckDB/Postgres (`v3b-clojure/`).

Both implement the same contract (`shared/CONTRACT.md`) over the same slice (`shared/slice.edn`). Both run against the same 100k-request world. Everything below can be reproduced from the repo root:

```
.venv/bin/python spikes/v3/shared/accept.py --cli spikes/v3/v3a-prolog/cli      # and v3b-clojure/cli; add --mutation
.venv/bin/python spikes/v3/shared/bench.py  --cli spikes/v3/v3a-prolog/cli      # --backend postgres
.venv/bin/python spikes/v3/v3a-prolog/linkml/build.py                           # V3a model
(cd spikes/v3/v3b-clojure && clojure -M:model && clojure -M:probe)              # V3b model, Datahike probes
```

Measured on 2026-11-24 (Apple Silicon, macOS). Per PLAN Decisions 2026-11-24, this is an exploration, not a selection. Expressiveness and insight weigh most, and footprint is information only.

## What we learned about the architecture

These points hold whichever spike is preferred.

1. **The `fetch(concept, filters)` boundary is the stable part of System A.**
   - Both engines issue exactly the same number of SQL statements: 11.17 per `approved` decision on 200 random requests.
   - Both reach the same answers (49/200 approved).
   - Neither engine ever loads a table: the exhaustive set question used 551 bounded statements and at most 425 rows.
   - Switching from DuckDB to Postgres was a config change in both.
   - The concept → SQL bindings live in the slice, so an engine never needs to know which backend it is talking to.

2. **The defeasible layer is small, and neither platform provides it natively.**
   - Team defeat, ambiguity blocking, superiority (explicit, strict, authority, later), functional rivals and R314 incompatibility take about 150–200 lines in either language.
   - Prolog contributes unification and backtracking for rule bodies. Clojure needed 57 lines to rebuild these (unify, walk, rename, a Prolog-like standard order).
   - Clojure contributes an EDN reader. Prolog needed a 78-line DCG for it.
   - Datalog rules (`%`) did not fit. The defeasible layer reasons over proof results (which supporters beat which attackers), not over facts.
   - The design decision that matters is "rules are data interpreted at runtime". The platform choice matters much less.

3. **Time has two axes, and only one of them belongs to the store.**
   - **Valid time** is when a claim is in force: `valid_from`/`valid_to`. It is domain data and must be modelled explicitly as attributes. Both spikes answer every as-of question this way.
   - **Transaction time** is when the system learned something. Datahike provides it for free, and the probe shows it is a real second axis:
     - On 2026-08-02, C5 (valid from 08-01, asserted 08-05) was already true but not yet known.
     - `d/as-of` on a transaction id reproduces the pre-extension state: C1 "holds" before the extension, "rebutted" after.
   - Using transaction time as assertion time breaks in three places:
     1. Rules and vocabulary are transacted at load time, so a tx-time view of 2026-07-15 contains **0 rules**.
     2. A sub-claim shares its parent's transaction, so tx-meta names the parent's asserter. Finance's C1.3 and C2.3 show up as procurement.
     3. Backdated `txInstant`s arrive out of order. Datahike accepts this and filters each datom by its own instant, which works, but nothing enforces it.
   - Conclusion: `asserted_by`/`asserted_at` are **semantic**, because superiority by authority and "later wins" read them. They belong in attributes. Transaction time is an audit axis: what did we know when we decided.

4. **An adoption gate is "evaluate against a value".**
   - V3a mutates its global store under `setup_call_cleanup`: it asserts `withheld/1` and the hypothetical records, runs, then retracts. This is very cheap (0.1 ms) and correct for a single-threaded CLI. Isolation depends on cleanup discipline: a concurrent op would see the hypothesis.
   - V3b evaluates against an immutable db value, so isolation holds by construction:
     - `d/with` costs about 2.7 ms.
     - A Datahike branch costs about 103 ms (185 ms when it adds the extension). It is an *experimental* namespace.
   - Branches are the right tool for a long-lived proposal that someone reviews and later merges. Values are the right tool for what-ifs.

5. **Explanations are a data contract, and independent re-verification was the main correctness tool.**
   - The tree shape (rule / claim / fetch / fact / absent / defeated_by / superior) carried both spikes. `check_why.py` re-derives every tree, including re-running node SQL.
   - The acceptance run built on it, guarded by the mutation test (check 1 must fail on mutated keys), surfaced V3a's three engine bugs. V3b's port then went green on the first full run.
   - Malli made the shape itself checkable: all 350 why roots of a run conform. The schema is exported as `docs/why-node.schema.json` for other consumers, for example the LLM arm.

6. **A model that cannot see inside rule bodies misses the important part.**
   - LinkML holds the envelope: ids, owners, dates, enums. The heads, bodies and assertions are opaque strings to it; `build.py` had to parse all 53 with `edn.pl` separately.
   - linkml-validate 1.12.1 also did not enforce the declared rule "a concept has `sql` or `derived_by`".
   - Malli validates rule bodies structurally: literal kinds, variable naming, fetch filter maps, expression arity. It enforced the class rule and rejected 12/12 negative tests.
   - In return, LinkML provides schema docs and DDL generators (`gen-doc`, `gen-sqlddl`) that Malli lacks. Malli's error messages for a bad literal inside an `:orn` list every alternative and are noisy.
   - Both instance-doc generators were hand-written and produce identical `docs/slice.md` files.

## §7 criteria

| Criterion | V3a (LinkML · Prolog) | V3b (Malli · Clojure · Datahike) |
|---|---|---|
| Correctness | Green 1–6, mutation fails as required. 3 engine bugs on the way (forall/2 not binding fetch outputs; yall dict expansion; `evaluate/3` called with a bound result skipping a cut) | Green 1–6 on the first full run; mutation fails. Defects only in glue: Malli recursive schemas, data.json stdin pushback, environ printing on stdout. *Caveat:* V3b ported V3a's settled semantics |
| Effort | Green in session 1, plus the LinkML model | Green in session 2. Both within the timebox (2 and 3 sessions) |
| Defeasible semantics | All of it built (`defeasible.pl`). No tabling/`tnot` was needed: a per-op memo, no negative cycles in the slice | All of it built (`engine.clj`, a port). Datalog rules not used for it |
| Explanations | Complete against keys; `why.pl` 63 lines | Complete against keys; `why.clj` 64 lines. Trees also validate against a Malli schema exported as JSON Schema |
| As-of / provenance | Valid time from attributes; who-said-it from claim facts. No transaction-time axis | Valid time from attributes (same). Tx time via `d/as-of` adds "known when", with the pitfalls in §3 above |
| Adoption gate | assert / retract under `setup_call_cleanup`; 0.1 ms; no isolation | Immutable value. `d/with` 2.7 ms; branch 103 ms (experimental API) |
| SQL boundary | Prolog → Python (janus) → duckdb/psycopg; swap = config | JDBC in-process; swap = config. Postgres SQL is rewritten to psycopg style only for the checker |
| Performance (DuckDB) | decide p50 4.3 ms, p95 9.2 ms; cold start 0.13 s; max RSS 60 MB loaded, 128 MB bench | decide p50 5.9 ms, p95 13.0 ms; cold start 2.4 s AOT (7.5 s from source; Datahike load 1.3 s); RSS 374 / 644 MB |
| Performance (Postgres) | decide p50 12.6 ms, p95 29.9 ms | decide p50 4.5 ms, p95 17.0 ms |
| Authoring (size only) | `slice.edn` 318 lines, shared. LinkML schema 199 lines; converted instance YAML 760 lines | `slice.edn` 318 lines, read directly. Malli schemas about 80 lines in `model.clj` |
| Footprint (information) | `.venv` 104 packages, 250 MB (linkml dominates), plus SWI-Prolog 11.0.0 | 75 jars, 106 MB, plus JDK 27. Datahike versioning is experimental |

Lines of code. The table shows total lines, with code lines (no blanks or comments; Clojure docstrings count as code) in parentheses.

| Part | V3a | V3b |
|---|---|---|
| Model / validation | `edn2yaml.py` 61 + `build.py` 203 + `slice.yaml` 199 | `model.clj` 195 (170): schemas, why schema, docs, negatives |
| Evaluator | `defeasible.pl` 209 (154) + `edn.pl` 78 (58) | `engine.clj` 255 (209), including 57 lines of term machinery |
| Explanation | `why.pl` 63 (50) | `why.clj` 64 (57) |
| Ops / surface | `ops.pl` 207 (149) | `ops.clj` 186 (152) |
| Store | (Prolog dynamic facts, inside `defeasible.pl`) | `store.clj` 177 (145) |
| SQL boundary | `sql.py` 95 (77) | `sql.clj` 91 (81) |
| Glue | `host.py` 26 + `cli` 4 | `cli.clj` 47 + `cli` 8 + `deps.edn` 11 |
| Engine total (evaluator, why, ops, SQL, glue) | ≈ 680 | ≈ 830 (store included) |

Latency is the per-op `ms` from the CLI's own clock: 200 `approved` decisions on seeded random requests, then Q01–Q23. Warm figures (after 20 ops) differ by less than 0.5 ms in both. The question p95 in V3b (about 100 ms) is the branch-based hypothesis (Q11).

Not done: Scriptum (Lucene) and HNSW search for `resolve_term`. PLAN marks them optional, and plain Datalog matching over normalised terms and synonyms passes check 6. The V3b `d/with` hypothesis mode was checked by the probe and by the timing session (CONFLICT inside, base unchanged afterwards), not by `accept.py`, which runs the default (branch).

Readability of the two notations is Matthias's call. There is no verdict here.

## Recommendation

**Carry forward V3b's architecture shape:**
- rules and claims as EDN data
- a schema that validates inside rule bodies
- the state as an immutable value, with hypotheses evaluated against a derived value
- valid time and assertion provenance as attributes, with transaction time only as an audit axis

The engine can be either. The Prolog evaluator is shorter and faster, and could sit behind the same shape.

The two deciding facts:
1. **Hypotheses as values are isolated by construction at about 3 ms** (`d/with`). V3a's adoption gate is correct only because nothing runs concurrently with it.
2. **The model has to see the rules.** Malli checked every rule body and enforced the class rule. LinkML treated the 53 rule and claim bodies as strings and let the class rule through.

What would change this: if the adoption gate never needs isolation (single-user, batch), or if generated DDL and schema docs matter more than rule validation, V3a's lighter stack wins on every measured number except Postgres latency.
