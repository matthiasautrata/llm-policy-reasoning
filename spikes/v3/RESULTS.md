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

## After the V3a fixes

Added 2026-11-24 after `PLAN-v3a-fix.md` (F1 isolated hypotheses, F2 structured rule bodies in LinkML; the details are in that plan's Decisions). The sections above are left as written. Where they disagree with this section, this section is current.

**Re-run.**

| Run | V3a | V3b |
|---|---|---|
| `accept.py` (DuckDB and Postgres, check 2) | GREEN 1–6 | GREEN 1–6 |
| `accept.py --mutation` | fails, as it must | fails, as it must |
| `shared/isolation.py`, both backends | PASS with `snapshot`; FAIL with the old `assert` mode, kept as a control | PASS with `branch` and with `with` |
| `bench.py`, both backends | 0 errors, 49/200 approved, 11.17 statements per decide | same |

**Isolation test.** A concurrent op B decides on the base while op A's hypothesis is open, and B must not see the hypothesis. This also covers V3b's `d/with` mode, which `accept.py` does not reach (PROGRESS question 4).

### Changed §7 rows, old → new

| Criterion | V3a old | V3a new | V3b old | V3b new |
|---|---|---|---|---|
| Adoption gate | assert/retract under `setup_call_cleanup`; 0.1 ms; no isolation | `snapshot/1` with a memo keyed by state. p50/p95: 0.11/0.12 ms; 0.23/0.26 ms with the extension added. Concurrent test PASS on both backends | `d/with` 2.7 ms; branch 103 ms; isolated by construction (untested) | Unchanged, now tested: PASS in both modes, both backends |
| Model / validation | Envelope only; 53 heads/bodies/assertions opaque strings; the class rule not enforced | Bodies structured (literal and term classes). **12/12 negatives rejected** by linkml-validate and by `jsonschema` on the generated schema. Round trip structure → EDN → `edn.pl` 80/80 | 12/12 (Malli) | Unchanged |
| Performance (DuckDB) | decide p50/p95 4.3/9.2 ms; cold start 0.13 s; RSS 60/128 MB | 4.4/9.3 ms; 0.12 s; 60/126 MB (unchanged) | 5.9/13.0 ms; 2.4 s; RSS 374/644 MB | 6.0/13.1 ms; 2.4 s; 367/645 MB (unchanged) |
| Performance (Postgres) | decide p50/p95 12.6/29.9 ms | 8.5/21.7 ms (repeats 7.7–7.9 / 18.7–19.0). The pre-fix commit `8828f1b`, measured today, gives 8.6/21.4, so the old figure was run-to-run variation, not an effect of F1 | 4.5/17.0 ms | 5.2/17.3 ms |
| Authoring (size only) | LinkML schema 199 lines; instance YAML 760 | Schema 292; instance YAML **1331** (`slice.edn` is 318) | Malli schemas about 80 lines | Unchanged |
| Lines: model / validation | `edn2yaml.py` 61 + `build.py` 203 + `slice.yaml` 199 | 158 + 278 + 292 | `model.clj` 195 | Unchanged |
| Lines: surface / SQL / glue | `defeasible.pl` 209, `ops.pl` 207, `sql.py` 95, `host.py` 26 | 219, 253, 107, 37 | `ops.clj` 186, `sql.clj` 91, `cli.clj` 47 | 194, 95, 49 |

`shared/isolation.py` (64 lines) is new and shared. Both spikes gained a test-only `sleep` op and the `concurrent`/`after` script keys. In both, the SQL per-op cache and log became thread-local and statements are serialised on the one connection.

### What SWI-Prolog snapshots do and do not guarantee

**Guaranteed** by `snapshot/1` in SWI-Prolog 11.0.0 (manual §4.14.1.3):
- The goal sees the dynamic database as of the snapshot's start, plus its own changes.
- No other thread ever sees those changes.
- The changes are always discarded: on success, failure and exception alike.
- Isolation costs nothing measurable here: 0.11 ms, the same as the old assert/retract.

**Not covered:**
1. **Anything that is not the dynamic database.**
   - Global variables (`nb_setval`) and flags (`flag/3`) are not rolled back.
   - Static code and files loaded inside the goal become global.
   - Side effects through `py_call` happen. Here they are read-only SQL, and the Python-side cache had to be made thread-local by hand.
   - Shared tabling should not be combined with transactions. V3a uses no tabling.
2. **State visible from before the snapshot.**
   - Facts the base asserted before the snapshot, such as the memo, are visible inside it.
   - V3a therefore had to key the memo by a state token. Without the key, the hypothesis reuses base results; `memo_test`'s control case shows this.
   - This obligation falls on every cache the evaluator adds. It is a discipline, not a property of the construct.
3. **Concurrent writers.** Commits are atomic, but consistency between writers needs a mutex or `transaction/3` constraints. Hypotheses never commit, so this does not arise yet.

**Compared with V3b:** V3b's isolation covers everything the evaluator reads, because the db value is passed as an argument. V3a's covers the dynamic database, plus whatever the evaluator's authors key correctly. Both are now isolated and tested. The kinds of guarantee differ.

### What LinkML can and cannot express or enforce (1.12.1)

**Can (as used here):**
- polymorphic rule literals and terms via `designates_type` on an abstract parent, with closed classes;
- variable naming via `pattern`;
- arity via named slots, with surplus positions rejected by the closed class;
- operator sets via enums;
- fetch filter and output maps via keyed, inlined classes; the compact `{column: value}` form is accepted;
- "sql or derived_by" via a class-level `any_of` of `slot_conditions`;
- from the same schema, gen-doc, gen-sqlddl and JSON Schema. Malli has no doc or DDL generators.

**Cannot, or only with friction:**
- **No positional notation.** EDN vectors such as `[:< ?x 1]` have to be converted into objects.
  - The converter (158 lines) is part of the trust chain: LinkML validates a *converted copy*, while the engine still runs `slice.edn` through `edn.pl`. The round-trip check guards that gap; Malli validates the values the engine runs.
  - The YAML is 1331 lines against 318 in `slice.edn`.
- **Two silent no-ops found** (F2.3):
  - A `rules` entry without `preconditions` becomes a JSON Schema `then` with no `if`, which is ignored.
  - A class-level `any_of` is not inherited through `is_a`, while ranges admit descendants. A concept with neither key validated as a `Measure` until the condition was repeated on each subclass.
  - In both cases the schema validated cleanly and the rule simply did not apply. Only a negative test exposed them.
- **No custom error messages.** `slot_conditions` has no message slot. See below.

**Error messages** (all 12 in `v3a-prolog/linkml/negatives.md`, compared with Malli in the F2.4 Decision):
- Enum, pattern, date and closed-class errors: good in both.
- Errors inside a polymorphic literal: linkml-validate is *more* specific than Malli. It names the deepest failing slot (`… in /rules/0/head/args/0/name`), where Malli lists every `:orn` alternative first.
- Arity and wrong-kind errors: vague in both. LinkML says "not valid under any of the given schemas"; Malli says "input remaining".
- The class rule: only Malli carries a readable message.

Neither model checks rule semantics, such as variable safety or a `derived_by` that names an existing rule. Neither was tested for it.

### Recommendation, revisited

**Neither of the two deciding facts above still holds as stated.**
1. *"Hypotheses as values are isolated by construction at about 3 ms; V3a is correct only because nothing runs concurrently."*
   - V3a now isolates hypotheses with `snapshot/1` at 0.11 ms, and it passes the same concurrent test as V3b on both backends.
   - What remains is the kind of guarantee, described above, not whether there is one.
2. *"The model has to see the rules; LinkML treated the bodies as strings and let the class rule through."*
   - LinkML now sees the bodies and rejects 12/12, the same as Malli.
   - What remains:
     - it validates a converted copy through a converter that must track the rule language;
     - it took two non-obvious schema fixes, which a negative test was needed to find.

**So the spike no longer measures a fact that forces the shape choice.** The shape elements recommended above can be built in either stack, and both spikes now have them:
- rules and claims as data;
- a schema that sees rule bodies;
- isolated hypotheses;
- valid time and assertion provenance as attributes.

**What still separates the two shapes:**
- **Notation.**
  - V3b uses one notation, EDN, for slice, rules, schema and validation, applied to the values the engine runs.
  - V3a has two: EDN, authored and run, and LinkML/YAML for model, docs and DDL, at about 4× the lines.
- **State as a value.**
  - In Clojure it is the idiom: every reader gets isolation for free.
  - In Prolog it is an opt-in primitive, plus discipline for everything outside the dynamic database, such as memo keys, global variables and the Python side.
  - F1.6 (threading state as a value through the Prolog evaluator) was not attempted. Estimate: most of `defeasible.pl` and `why.pl` would change.
- **Transaction time.** Only Datahike offers the "known when" audit axis (§3).
- **Generators.** LinkML's gen-doc, DDL and JSON Schema come with the schema. Malli gives only JSON Schema.
- **Footprint and latency (information only).**
  - V3a is lighter: 0.12 s cold start versus 2.4 s, and about 60–130 MB RSS versus 370–645 MB.
  - V3a is faster on DuckDB: 4.4 ms p50 versus 6.0 ms.
  - On Postgres the gap is smaller than first reported: V3a 8.5 ms p50 versus V3b 5.2 ms.

**Carry forward the shape; the stack is open.** The remaining differences are qualitative trade-offs. On one side: one notation and isolation by construction. On the other: generators, a smaller footprint and isolation by primitive plus discipline. Readability of the two notations is Matthias's call.
