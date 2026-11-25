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

## V3c and V3d

Added 2026-11-24 after `PLAN-v3cd.md`: V3c is Elixir 1.20.5 on OTP 29.1.2, V3d is Flix 0.80.0 on JDK 27.0.1. Versions, deviations and pitfalls are in that plan's Decisions. The sections above are left as written. Raw outputs are in `v3c-elixir/results/` and `v3d-flix/results/`.

**Re-run.**

| Run | V3c | V3d |
|---|---|---|
| `accept.py` (DuckDB, check 2 on Postgres; check 1 runs `check_why`) | GREEN 1–6 | GREEN 1–6 |
| `accept.py --mutation` | fails, as it must | fails, as it must |
| `isolation.py`, both backends | PASS | PASS |
| `bench.py`, both backends | 0 errors, 49/200 approved, 11.17 statements per decide | same |
| 12 negatives | 12/12 rejected | 12/12 rejected (`results/negatives.txt`) |

Both use an **own defeasible evaluator**, ported from V3b, over an immutable store value with on-demand fetches. Neither runs System A on its platform's Datalog. The Datalog engines were probed instead; the answers to Q1 below say why.

### §7 criteria, four platforms

V3a and V3b values are from "After the V3a fixes" where that section changed them, and from the first table otherwise.

| Criterion | V3a (LinkML · Prolog) | V3b (Malli · Clojure · Datahike) | V3c (Elixir · ex_datalog probe) | V3d (Flix) |
|---|---|---|---|---|
| Correctness | Green 1–6; mutation fails | Green 1–6; mutation fails | Green 1–6; mutation fails. Ported V3b's settled semantics | Green 1–6; mutation fails. Ported V3b's settled semantics |
| Effort | Session 1 | Session 2 | Within its timebox (3 sessions) | Within its timebox (3 sessions); most of it went to the Datalog probes |
| Defeasible semantics | All built (`defeasible.pl`) | All built (`engine.clj`) | All built (`engine.ex`). ex_datalog rejects the defeasible meta-program (`:unstratified_negation`) | All built (`Engine.flix`). Flix Datalog does stratified negation only; team defeat over derived conclusions would be a negative cycle |
| Explanations | Built; `why.pl` 63 lines | Built; `why.clj` 64 | Built; `why.ex` 92. `Explain` gives 82,195 nodes for a 3-step proof on a 5-edge graph, and runs out of memory (12.7 GB) on the full ancestor relation | Built, inside `Engine.flix`. `pquery` returns the leaf input facts of one derivation (3 facts, 0.1 s), not a tree |
| Model / validation | 12/12 (linkml-validate on a converted copy) | 12/12 (Malli) | 12/12, hand-written validator over the EDN data | 12/12: 10 by parsing into ADTs, 2 by explicit checks (date regex, closed maps) |
| Adoption gate / hypothesis, p50/p95 (DuckDB) | `snapshot/1` 0.11/0.12 ms | `d/with` 2.7 ms; branch 103 ms | Store value: Q11 0.19/0.33 ms; deriving the store alone 0.05 ms | Store value: Q11 0.49/1.40 ms; deriving the store alone 0.016 ms |
| Isolation, kind | Primitive plus memo-key discipline | By construction (the db value is an argument) | By construction (a value; each concurrent op is its own process, and the per-op memo lives in that process) | By construction, **compiler-enforced**: a spawned thread cannot touch the parent region's `Ref` (E6469), so each thread gets its own copy of the store value |
| SQL boundary | janus → Python | JDBC | ADBC 0.12.1, with DuckDB 2.0.1 pinned by URL | JDBC through interop, typed `\ IO`. The evaluator performs a user-defined `Eval` effect, handled per op |
| Performance (DuckDB) | 4.4/9.3 ms; cold 0.12 s; RSS 60/126 MB | 6.0/13.1 ms; cold 2.4 s; RSS 367/645 MB | 5.5/12.0 ms; cold 0.30 s; RSS 121/239 MB | 6.3/13.8 ms; cold 1.7 s (load 713 ms); RSS 92/333 MB |
| Performance (Postgres) | 8.5/21.7 ms | 5.2/17.3 ms | 15.5/37.7 ms in bench.py (noisy: 7.9–15.5 p50 over 4 runs); 4.9/12.7 in-process, warm | 5.1/15.5 ms; cold 0.15 s; RSS 69/384 MB |
| **Concurrency throughput**: the bench's 200 decides, 1 → 8 workers (decides/s, p95 at 8) | not measured (statements serialised on one connection) | not measured (same) | DuckDB 140 → 288 (2.1×), p95 45 ms; Postgres 86 → 505 (5.9×), p95 31 ms. 8 processes, 8 connections | DuckDB 135 → 459 (3.4×), p95 32 ms; Postgres 321 → 1081 (3.4×), p95 15 ms. 8 threads, 8 connections. Same answers, 0 errors |
| **Supervision / failure** | — | — | SQL connection killed mid-loop: restarted in 0.04–0.46 ms. On Postgres one op got an error (the call in flight); 0 wrong answers. Hot reload of the evaluator under 8 workers: 0 errors over 531 / 1061 requests | No supervisor. A failure is a value (`Result`); a thread that dies is not restarted. Not probed |
| **Lattice** | — | — | — (ex_datalog has no lattices) | Standing as a lattice-valued predicate works natively: meet over premises, the solver joins alternative derivations. Rebuttal lowers a standing, which is not monotone, so it needs stratified negation, not the lattice |
| **Types caught** (planted defects T01–T10) | — | — | 4/10 (T1, T6, T9, plus T10 from the undefined-function check, not the type system) | 9/10. The miss: a misspelt key on a `Map[String, Value]` SQL row. Also caught: an IO effect leak from a pure function, and a non-exhaustive match on a literal form |
| **Rules as data → native Datalog** | (not tried; Prolog clauses are data) | No: Datahike rules did not fit the defeasible layer | No. Strict closures only, as a probe: anc 0.57 s, chain 56 s vs CTE 37 ms. Magic sets 39–42 ms. Callbacks return one value per binding, and their SQL runs in other processes, outside the op's log | Partly. 16/19 logic rules become runtime `Fixpoint3` AST values and solve over materialised SQL facts, but without the frontend's checks (stratification, range restriction), bottom-up only, and not the defeasible semantics. The reified meta-program route is about 45× slower than typed predicates |
| Footprint (information) | `.venv` 250 MB + SWI-Prolog | 75 jars, 106 MB + JDK | Erlang/OTP + Elixir (brew); deps compiled under `_build` | Fat jar 84.5 MB; `lib/` 79 MB; Flix 38 MB + JDK 374 MB |

Lines (total, incl. blanks and comments):

| Part | V3c | V3d |
|---|---|---|
| EDN reader | `edn.ex` 102 (NimbleParsec) | `Edn.flix` 181 (hand-written) |
| Model / validation | `model.ex` 200 | `Model.flix` 496 (ADTs and parser; the types *are* the model) |
| Evaluator + why | `engine.ex` 360 + `why.ex` 92 | `Engine.flix` 624 |
| Store | `store.ex` 94 | `Store.flix` 47 |
| Ops / SQL / glue | 277 / 138 / 67 | 357 / 174 / 107 |
| Total | 1330 | 1986 |

Latency is the CLI's own per-op `ms`, as before. V3d's Postgres cold start is shorter than its DuckDB one because loading DuckDB's native library dominates. The 1-thread rows of the throughput probe run after a warm-up pass; that is why V3d Postgres reaches 2.1 ms p50 there, against 5.1 in `bench.py`.

### V3c: answers to PLAN-v3cd §1.2

1. **What does ex_datalog carry?** Only the strict recursive part, and only as a probe.
   - The ancestor closure is correct (9497 facts, equal to the CTE) but takes 0.57 s, and the reporting chain takes 56 s. The two all-pairs CTEs take 37 ms together.
   - Magic sets answer one goal in 39–42 ms, the same answer as the CTE.
   - The default 30 s timeout returns `{:ok, …}` with 79,652 of 97,683 facts. Truncation is visible only in `stats.termination`.
   - BEAM callbacks as the `fetch` hook return one value per binding, so a multi-row fetch comes back as a list term, not as joinable rows. Their SQL runs in separate processes, invisible to the op's log and cache, which check 5 needs.
   - `Explain` is not a usable source for `why`. It names every derived fact rather than one proof: 82,195 nodes for a 3-step proof. It runs out of memory on the full relation.
   - The defeasible meta-program is rejected as unstratified.
   
   So it is an own evaluator in Elixir, as in V3b (`engine.ex` 360 + `why.ex` 92).
2. **Isolation.** The state is one immutable `%Store{}`, and each concurrent op is its own process. `isolation.py` passes on both backends. Hypothesis p50/p95 on DuckDB: Q11 0.19/0.33 ms; with the extension added, 0.21/0.29 ms. That is between V3a's `snapshot/1` (0.11) and V3b's `d/with` (2.7).
3. **Runtime extension.** Check 3 passes: a claim and a rule are added at runtime with no restart, and Q07 and Q14 change.
4. **BEAM side benefits.**
   - Supervision: killing the SQL connection process mid-loop restarts it in under 0.5 ms, with 0 wrong answers. At most the op in flight gets an error.
   - Concurrency: 8 processes give 2.1× on DuckDB and 5.9× on Postgres.
   - Hot reload: the evaluator module, loaded twice under 8 workers, gave 0 errors and 0 wrong answers, and all three versions served requests.
   - Each of these was a short probe (`probes/beam_probes.exs`) against System A's existing supervision tree: a top supervisor, plus a `rest_for_one` supervisor per SQL connection.
   - LiveView was skipped (optional).
5. **Types.** Elixir 1.20's checker reported 3 of 10 planted defects, plus 1 from the undefined-function check. Not reported: a string key used as an atom on a SQL row (T2), a bad child spec (T3), a missing map field (T4), an unknown struct field (T5), concatenation on an atom (T7), and a clause on a result shape the callee never returns (T8). V3d's Flix caught 9/10 of the same.

### V3d: answers to PLAN-v3cd §2.2

1. **Can runtime rules become Flix Datalog values?**
   - **(i) A fixed predicate vocabulary with typed `#{}` programs** does not reach rules loaded at runtime. The predicate symbols and their types live in source, and a typed program can only be composed (`<+>`) from fragments that already exist there. It works well where the *rules* are fixed and only *facts* come from SQL:
     - typed closures over SQL rows: ancestors 9497 facts in 0.2 s, chain 97,683 in 0.6 s;
     - but a single goal recomputes the whole closure (0.33 s for one employee's chain).
   - **Runtime programs through the `Fixpoint3` AST** (`Translate.flix`) are the way rules-as-data reach the solver. 16 of 19 logic rules translate; R106 (a comparison over an arithmetic term), R202 and R304 (not range-restricted, bound only by the caller) do not. What this path gives up:
     - **No negative-cycle check.** A cycle built at runtime "solves" and derives both sides, which is unsound. The same program as typed source is rejected at compile time (E5914).
     - No range-restriction check, and an output/input argument order that only the solver notices.
     - **Bottom-up only.** It needs a hand-chosen demand domain for parameterised concepts: 782,603 fetch facts materialised in 38 s. It also surfaced an INT32 overflow in the slice's own `pending_exposure` SQL, which no top-down engine ever reaches. Check 5's bounded fetch is lost.
     - Its readings are Horn and a stratified approximation, not team defeat.
   - **(ii) The reified encoding** works: the same 9497 facts, but 8.6 s, about 45× the typed program. The defeasible meta-program would need non-stratified negation as well.
   - **(iii) An own evaluator** is what System A runs. Flix Datalog would fit the strict closures, which the SQL CTEs already do in milliseconds.
   - **(iv) Codegen** costs 2.7–2.9 s for `check`, 9.6 s for a fat jar, a 1.7 s cold start, and the loss of in-process state on every rule change.
2. **Lattice.** Yes, for propagation. `Eff(g; meet(a, b))` gives a conclusion the weakest standing of its premises, and the solver joins alternative derivations to the best one (`probe-lattice.txt`). Defeat is not monotone, so it cannot be a lattice operation; it needs stratified negation. Team defeat over *derived* conclusions is then a negative cycle. So the lattice can carry "how well supported", and defeat stays in the evaluator.
3. **Isolation.** A hypothesis is a derived `Store` value. `isolation.py` passes on both backends. The compiler enforces that no thread shares the parent's mutable `Ref`. Q11 p50/p95 is 0.49/1.40 ms; deriving the hypothesis store is 0.016 ms. The rest is a slower evaluator than V3c's on this path (plain decide 0.21 vs 0.13 ms).
4. **Explanations.** All built. `pquery` gives the input facts that support one derived fact (Node, two Parent edges for `Anc(cc0077, cc0001)`, 0.1 s), but not the rule steps or why-not. It also answers only for typed programs. `why` and `why_not` come from the own evaluator and pass `check_why`.
5. **Types and effects.**
   - Caught: 9/10 planted defects plus 2 extras: an effect leak, and a non-exhaustive match over literal forms.
   - Most caught by the compiler during development: record shapes, `Result` vs `Option`, effect rows around `spawn`. The one real hole is the SQL row, a `Map[String, Value]`.
   - The ceremony cost:
     - name collisions with Datalog keywords;
     - imports with aliases for every Java type;
     - explicit arrays for varargs;
     - an effect signature on `main`;
     - `pin` around timings;
     - a Model about 2.5× V3c's lines, because the ADTs and their parser are the validator.

### What we learned about the architecture (additions)

1. **The defeasible layer is not native Datalog on any of the four platforms.** Datahike rules, ex_datalog and Flix Datalog all stop at stratified negation, and team defeat over derived conclusions is a negative cycle. All four run the same own top-down evaluator. What the Datalog engines do well (recursive closures over fetched rows), SQL CTEs already do in milliseconds.
2. **Top-down with a bounded fetch is part of the shape, not an engine detail.** The bottom-up path had to materialise 782k facts over a hand-chosen domain, and it reached SQL (`pending_exposure` at the root) that no question asks. Rules like R202 and R304 are legitimate only because a caller binds their variables. Check 5 measures exactly that property.
3. **Rules as data lose the compiler's rule checks, so the model must take them over.** The static checks the typed Flix path gives for free (stratification, range restriction) are gone on the runtime path. The model validators, V3a–V3d alike, do not check them either. A moded safety check (which variables the caller binds) and a stratification check belong in the model.
4. **Isolation by construction has three forms now:**
   - a value passed as an argument (V3b, V3c, V3d);
   - a process per op (V3c);
   - a compiler that refuses shared mutable state across threads (V3d).
   
   Only the Prolog primitive needs a discipline.
5. **The SQL boundary is where static guarantees stop.** It is Flix's one type miss, V3c's callbacks lose the op's log there, and DuckDB's INT128 sums meet an INT32 cast there. Typed rows per concept, generated from the concept's `columns`, would close the Flix gap without codegen of rules.
6. **Lattice-valued standing is a separate axis from defeat.** Support strength can propagate monotonically through derivations; defeat cannot. If qualified or partial standing matters, it fits a lattice, and the evaluator keeps defeat.

### Recommendation across four platforms

The shape stands: rules and claims as data, a model that sees rule bodies, isolated hypotheses as values, a top-down evaluator with bounded fetch. All four platforms carry it, and all four needed an own evaluator. What each adds or costs (no ranking):
- **V3a, Prolog:** the shortest evaluator, the lightest footprint and the fastest on DuckDB. Isolation is a primitive plus discipline, and LinkML validates a converted copy.
- **V3b, Clojure/Datahike:** one notation throughout, isolation by construction, and transaction time as an audit axis. The heaviest footprint.
- **V3c, Elixir:** isolation by value and by process, plus what the BEAM gives for free: supervision with sub-millisecond restarts, 2–6× throughput at 8 workers, and hot reload under load. The type checker is still weak (3–4/10). ex_datalog is young and carries nothing of System A.
- **V3d, Flix:** the strongest static checks (9/10, effects, exhaustiveness) and compiler-enforced isolation. A native lattice, if graded standing is wanted. Its first-class Datalog does not reach rules loaded at runtime without dropping to an unchecked AST. The costs are ceremony and the largest code base (1986 lines).

The stack remains open. The new information is about which secondary property is wanted:
- operational resilience and concurrency (V3c);
- static guarantees (V3d);
- audit time (V3b);
- minimal footprint (V3a).

Readability of the four notations is Matthias's call.

## Defeat cycles: V3a with WFS, V3e Clingo

Added 2026-11-25 after `PLAN-v3-cycles.md`. V3e is Python 3.14 with clingo 5.8.0. V3a gains a WFS mode (SWI tabling with `tnot/1`) and keeps its memo mode as the control. V3b–V3d ran unchanged. The sections above are left as written. The semantics is in `shared/SEMANTICS-cycles.md`, versions and deviations are in that plan's Decisions, and raw outputs are in each spike's `results/`.

**Shared work.**
- `cycles.edn` adds Y1–Y6 as Q30–Q39. `reference.py` (`Cyc`, an alternating fixpoint) keys them.
- The A1 fix (`pending_exposure` cast to `BIGINT`) left every existing key byte-identical. The new Q24 reaches the root.
- `model_check.py --cycles` finds two negative cycles: `exempt_from_audit ↔ trusted` (RY31, RY32: Y3, odd) and `preferred ↔ under_review` (RY23, RY24: Y2, even). The bound-variable check finds 0 errors. Modes are inferred as a greatest fixpoint, so mutually recursive predicates can be typed.

### Y1–Y6, five spikes

Each question runs in its own session, with the model check bypassed (`cycles_probe.py`, DuckDB, 60 s timeout). ✓ = matches the WFS key.

| Q | Pattern | Key | V3a WFS | V3e | V3a memo | V3b | V3c | V3d |
|---|---|---|---|---|---|---|---|---|
| Q30 | Y1 direct rebut | CONFLICT CY1a / CY1b | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Q31 | Y2 even loop, derived | CONFLICT RY21 / RY23 | ✓ | ✓ | stack limit | StackOverflowError | timeout | timeout |
| Q32 | Y2 control (acme) | ANSWER true | ✓ | ✓ | stack limit | StackOverflowError | timeout | timeout |
| Q33 | Y3 odd loop | CONFLICT CY3 / RY32 | ✓ | ✓ | stack limit | StackOverflowError | timeout | timeout |
| Q34 | Y4 cycle broken by superiority | ANSWER true | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Q35 | Y5a downstream of blocked | ANSWER false | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Q36 | Y5b downstream of undefined | CONFLICT RY21 / RY23 | ✓ | ✓ | stack limit | StackOverflowError | timeout | timeout |
| Q37 | Y5c attacker's body blocked | ANSWER true | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Q38 | Y6 hypothesis withholds RY23 | ANSWER true | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Q39 | Y6 base after the hypothesis | CONFLICT RY21 / RY23 | ✓ | ✓ | stack limit | StackOverflowError | timeout | timeout |
| | **matched** | | **10/10** | **10/10** | 5/10 | 5/10 | 5/10 | 5/10 |
| | check 7 | | PASS (report) | PASS (report) | — | PASS (reject) | PASS (reject) | PASS (reject) |

The memo evaluators fail on the same five questions, and for the same reason. The memo is written only after `evaluate` returns, and nothing marks a goal as in progress. A real dependency cycle therefore re-enters `evaluate → attackers → prove → evaluate` without bound. The JVM throws StackOverflowError (V3b, at `engine/rename`), SWI hits its 1 GB stack limit (V3a memo), and the BEAM process recurses until the 60 s timeout (V3c; its memory was not sampled). V3d runs its CLI with `-Xss512m`, which probably lets the recursion run past the 60 s timeout before the stack overflows (not checked with a longer timeout).

Q32 fails as well, although acme is never suspended. The attacker's body has to be evaluated before it can be found false, and that evaluation runs into the cycle. Q38 passes everywhere because the hypothesis withholds RY23 and so cuts the cycle. Y1 passes everywhere because a direct rebut between claims is not a dependency cycle: it is the "blocked" CONFLICT the slice already had.

Under A2 the reject engines are still correct as deployed: check 7 passes because the shared model check refuses a rule base with a negative cycle. What they lack is a way to *answer* one.

**What V3b–V3d would need.** Port the alternating fixpoint (V3a's `wdef`/`wovr`/`wbeat`, or the host side of V3e) over the ground instances an op demands, plus the `undefined` why node and the sides rule from SEMANTICS-cycles.md. The specs and the tests already exist: `reference.py` `Cyc`, `check_why.py`, Q30–Q39. Estimate: 150–250 lines of evaluator and about 80 for why/sides per spike, about one session each. A cheaper stopgap, an in-progress marker that answers "undefined" on re-entry, stops the loop. It is not WFS, though: it can call a literal undefined that the alternating fixpoint would make false (as for Q32), so it would have to be checked against the keys and probably would not pass.

### Native vs built

| | V3a WFS (SWI-Prolog 11.0.1 tabling) | V3e (clingo 5.8.0) |
|---|---|---|
| Three-valued truth of the defeasible layer | **Native.** Tabled `wdef/3`, `wovr/3`, `wbeat/4` with `tnot/1`. SLG resolution gives the well-founded model, and `call_delays/2` reads the undefined residue | **Native, by encoding.** The defeasible layer is doubled (`t_*` / `p_*`, the Tr_p of Janhunen et al. 2006), and two solves on one Control give cautious `t_*` = WFS true and brave `p_*` = WFS not false |
| Superiority (explicit, strict, authority, later) | In the metaprogram (Prolog) | In the metaprogram (ASP) |
| Fetch demand (check 5) | Native: SLG calls `fetch` left to right, only for goals it reaches; 11.2 statements per decide | **Built:** a magic-set rewrite (`dm`/`need`) in the translator, keyed by `shared/modes.edn`. `@fetch` during grounding is only the SQL boundary. Bounded, but broader: 21.9 statements per decide, because every body of every demanded rule is demanded, attackers included |
| Statuses (proven / defeated / blocked / undefined) and CONFLICT sides | Built: `defeasible.pl` classifies over the three values | Built: the host, a Python port of V3a's classify / sides |
| `why` / `why_not`, including the `undefined` node | Built: `why.pl` over the tabled values | Built in the host from the ground skeleton (`h/3`, `ih/2`). xclingo 2.0b24 fails on its own README example; clingexplaid 1.5.1 explains unsatisfiability, not derivations |
| Hypotheses | `snapshot/1`; tables keyed by a state token and as_of, abolished per op | `#external active(Id). [free]` plus `solve(assumptions=…)`, one Control per op |
| Lines | `defeasible.pl` 347, `ops.pl` 282, `why.pl` 63 | `asp.py` 294 (translator and metaprogram), `host.py` 939 (store, Control, statuses, trees, ops) |

So the **truth values** of team defeat over derived conclusions, cycles included, are native on both. Everything that turns truth values into the contract's answers is still built: statuses, sides and trees. On V3e the fetch demand is built too, which comes for free with SLG.

One insight came from tooling built for something else. clingexplaid's MUS over the plain (undoubled) encoding names the odd loop exactly: `{CY3, RY31, RY32}` in 0.2 ms, the same set as V3a's `undefined.members`. An ASP solver's unsat core is therefore a cheap detector for odd loops.

### Semantics: confirmed, assumed, divergence

- **Confirmed in the source** (SEMANTICS-cycles.md):
  - the ABGM metaprogram (TPLP 2006) that the encoding follows;
  - that DL equals the Kunen semantics of that metaprogram, not WFS, and that undecided literals imply cycles;
  - Maier: NDL (blocking) differs from the WFS of the *direct* translation, so blocking has to be encoded in the metaprogram.
- **Assumed:**
  - equivalence with Maher & Governatori's WFDL (the AAAI-99 PDF could not be read);
  - team defeat with authority and `later` superiority, and functional rivals as attackers;
  - claims as valid-time-gated empty-body rules.
- **Y5 decided:** blocking (Q35 false, Q37 true). Downstream of an undefined literal is undefined (Q36). Q37 is the question that separates blocking from propagation.
- **WFS vs answer sets:** no divergence on Y1–Y6 once the encoding is doubled, since partial stable models include the well-founded one. The plain two-valued encoding does diverge (`probes.py`):
  - Y1: one model, with neither side;
  - Y2: two models (`{}` and `{preferred(dyne)}`), so cautious reasoning drops `preferred(dyne)` and brave reasoning gives the sides;
  - Y3: **no** model, so the whole program is inconsistent and every question would fail, not only Q33.
  
  "Answer statuses from cautious consequences" therefore holds only over the doubled program. Over the plain one it holds for even loops and breaks on odd ones.

### §7 rows, V3a WFS and V3e

| Criterion | V3a WFS | V3e (Clingo) |
|---|---|---|
| Correctness | Green 1–7 (Q30–Q39 10/10 on both backends); mutation fails; isolation PASS on both | Green 1–7 (10/10 on both backends); mutation fails; isolation PASS on both; negatives 12/12 by V3a's LinkML model |
| Effort | Within §2 (one session): the metaprogram, the tables keyed by state and date, `call_delays` for undefined | Within §3 (one session). Most of it went to the doubled encoding, the demand rewrite, and porting the trees |
| Explanations | Built (`why.pl` 63), plus the `undefined` node; passes `check_why` | Built in the host. Tooling: xclingo broken, clingexplaid MUS only (see above) |
| Hypotheses, CLI p50 (DuckDB; Postgres similar), base / with_hypothesis | Q10 0.17 / 0.19 ms; Q38 0.76 / 0.38 ms | Q10 6.66 / 6.60 ms; Q38 8.42 / 7.78 ms. A hypothesis costs nothing extra: each op grounds anyway |
| Latency, decide p50/p95 | DuckDB 4.9/9.4 ms (memo 4.4/9.2); Postgres 10.0/22.2 (memo 10.3/27.3); RSS 60/127 MB | DuckDB 14.2/14.9 ms; Postgres 11.9/14.4; cold 0.11–0.15 s; RSS 55–61/82–125 MB. In-process: about 5 ms grounding and 0.4–0.5 ms for both solves |
| Bounded fetch (check 5) | Holds; 11.2 statements per decide, same as memo | Holds (Q17: 551 statements, 1006 rows, max 425); 21.9 per decide |

### Lesson 1, revisited

Lesson 1 in "V3c and V3d" said: *the defeasible layer is not native Datalog on any of the four platforms*. That still holds for **Datalog**: Datahike, ex_datalog and Flix stop at stratified negation. It no longer holds for **logic programming**. Two engines carry defeat over derived conclusions, cycles included, as native semantics, with no evaluator written for the truth values:
- SWI's tabling under WFS, which is top-down and keeps bounded fetch for free;
- clingo's partial stable models, which are bottom-up per op and need a demand rewrite to keep fetch bounded.

The lesson therefore splits:
1. **Semantics needs non-stratified negation, and only WFS or stable-model engines provide it.** A cyclic defeat graph is a legitimate policy state: two departments, each with a rule that defeats the other's conclusion. A stratified engine has to reject it (A2's `reject`), and a memo evaluator crashes on it.
2. **The answer layer is built on every platform.** Statuses, CONFLICT sides and why trees, including the new `undefined` node, are built in V3a and V3e as well. Explanation tooling for ASP does not reach derivation trees today.
3. **Top-down demand is native only with SLG.** V3e regains bounded fetch with a magic-set rewrite and pays for it in grounding, roughly 3× V3a's decide latency.

### What each platform makes natural, and what it taught us (A3 order)

This is not a choice. Choosing happens later, for v3's T arm.

**1. Semantics: is the defeasible core native or built?**
- *V3a WFS:* native truth values with WFS, top-down, with demand for free. Taught: tables must be keyed by state and date and abolished per op, or answers leak across hypotheses (`table-test.json`). The memo mode is the clearest picture of why cycles need tabling.
- *V3e Clingo:* native truth values through the doubled encoding. Taught: the plain stable-model reading is *not* the intended semantics (Y3 has no model). The doubling is the step that makes ASP agree with WFS. The unsat core is a cycle detector for free.
- *V3b, V3c, V3d:* built and acyclic only. All three loop on a cycle, and the shared model check (A2) keeps them correct by rejecting such a rule base. Getting to WFS is a port of about one session each, with the reference and keys as its spec.

**2. Guarantees: isolation, static checks, explanations.**
- Isolation: by value and by construction in V3b–V3d. V3e has a Control per op and no shared mutable state. V3a has a primitive plus discipline, now with table keys as a second discipline.
- Static checks: the shared model check (cycles, bound variables) now covers every engine, and only its strictness differs. Flix's compiler checks remain the strongest per platform, but they do not reach runtime rules (see "V3c and V3d").
- Explanations: built everywhere, and complete in the contract's sense on all five (`check_why`). Only the native engines can explain a cycle (the `undefined` node), because only they can answer one.

**3. Operation: resilience, concurrency, audit time.** Unchanged by this addendum: V3c for supervision and throughput, V3b for transaction time. V3e adds per-op Controls that parallelise with no lock. Its latency is dominated by grounding (≈5 ms), not solving, so the cost grows with the demanded program, not with the cycles.

**4. Footprint (information only).** V3e: clingo 5.8.0 from a pip wheel in the shared `.venv` (273 MB in total, up from 250), plus V3a's `sql.py`; RSS about 60 MB. V3a's footprint is unchanged by tabling.

**What changed from the earlier recommendation.** That one compared platforms on secondary properties, assuming the core was equal. It is not: on cycles, V3a WFS and V3e answer, and V3b–V3d need a rule base without cycles or a ported fixpoint. Readability of the notations remains Matthias's call.

## Integrity at load time and ambiguity propagation

Added 2026-11-25 after `PLAN-v3-integrity.md` (phases f98651d, ef6ec40, a6cb024). The sections above are left as written. Deviations and versions are in that plan's Decisions; the semantics is `shared/SEMANTICS.md`; raw outputs are in each spike's `results/` and in `results/key-diff-propagation.md`.

**A note on "Defeat cycles".** That section answered a question that has since been reversed: cycles are now **rejected at load** (IR-001a), not answered. Its WFS-vs-memo table and its native-vs-built comparison describe a capability the accept run no longer asks for, and its "Y5 decided: blocking" is replaced by propagation (below). What remains valid from it:
- the memo crash analysis (no in-progress mark, so a cycle re-enters `evaluate` without bound). It is now the reason for the re-entry guard;
- the cycle detection in `model_check.py`, now the IR-001a gate in every engine;
- the unsat-core observation (clingexplaid's MUS names the odd loop), still a cheap second detector;
- the plain-vs-doubled finding for ASP, which matters again because V3e's default is now plain (see the guard results).

### Integrity checks (check 8)

One implementation, `shared/model_check.py`, reached through `shared/integrity.py` by every engine: imported by V3a and V3e, a subprocess for V3b, V3c and V3d. It runs at load, on `add`, and inside `with_hypothesis` against the hypothetical rule base. Fixtures are in `shared/fixtures/integrity/` (`manifest.edn`).

| Id | Fixture | Violation, members | V3a | V3b | V3c | V3d | V3e |
|---|---|---|---|---|---|---|---|
| IR-001a | `y2-even-loop.edn` | `defeat-cycle` RY23 RY24 (exact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-001a | `y3-odd-loop.edn` | `defeat-cycle` RY31 RY32 (exact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-001b | `ir001b-explicit.edn` | `superiority-cycle` RS1 RS2 (exact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-001b | `ir001b-authority.edn` | `superiority-cycle` ⊇ R313 RS3 | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-002 | `ir002-duplicate-definition.edn` | `duplicate-definition` R104 RD1 measure:booked_total (exact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-003 | `ir003-ordering-key.edn` | `rebuttal-without-preference` RP1 (exact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-004 | derived: slice without `:additivity` on `measure:booked_total` | `missing-additivity` measure:booked_total (exact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-005 | `ir005-no-completeness.edn` | `negative-without-completeness` RN1 (exact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| IR-006 | `ir006-unbound-call.edn` | `unbound-call` ⊇ RU1 | ✓ | ✓ | ✓ | ✓ | ✓ |
| | hypothesis tests (former Q38/Q39): adding RY24, adding the Y3 file | `defeat-cycle`, exact; base unchanged after | ✓ | ✓ | ✓ | ✓ | ✓ |
| | **check 8 / accept** | | PASS, GREEN 1–8 | PASS, GREEN 1–8 | PASS, GREEN 1–8 | PASS, GREEN 1–8 | PASS, GREEN 1–8 |

The rejection is byte-identical across engines because the gate runs before each engine's own schema validation. Of the seven checks, only IR-001a and IR-006 existed before. IR-003 holds by construction in the slice, so its check is a guard against a second ordering mechanism (an ordering key) being added. IR-005 checks that a completeness claim exists, not that its scope matches the query; the slice has no scope language. A check costs about 13 ms, or about 60 ms per call with Python start-up for the subprocess engines.

### Re-entry guard (`cycles_probe.py`, gate bypassed, DuckDB)

| Engine | Y2 even loop | Y3 odd loop | Result |
|---|---|---|---|
| V3a memo | `defeat-cycle`, goal path preferred → under_review → preferred, 2.3 ms | `defeat-cycle`, trusted → exempt_from_audit → trusted, 0.7 ms | guarded 2 of 2 |
| V3b | same path, 48 ms | same path, 17 ms | guarded 2 of 2 |
| V3c | 6.3 ms | 2.0 ms | guarded 2 of 2 |
| V3d | 34 ms | 18 ms | guarded 2 of 2 |
| V3a wfs (retired) | CONFLICT [[RY21],[RY23]] | CONFLICT [[CY3],[RY32]] | answers natively, no guard needed |
| V3e doubled (retired) | CONFLICT [[RY21],[RY23]] | CONFLICT [[CY3],[RY32]] | answers natively, no guard needed |
| V3e plain (default) | CONFLICT, sides null | CONFLICT, sides null | guarded 0 of 2: one model, answers without naming the loop |

Every probe ends in under 1 s, where before the memo engines crashed or timed out at 60 s. The guard's members are goals, not rule ids: at run time the evaluator sees goals. V3e plain is the one gap. Its single-model check does not fire on these loops, so with the gate off it gives a CONFLICT with no sides. With the gate on, which is the deployed setting, loops never reach it.

### Propagation

**Key diff** (`results/key-diff-propagation.md`). Q01–Q27 are byte-identical: no slice question derives anything from a contested literal. Four acyclic questions change, each explained by its root conflict:
- Q35 (Y5a), Q37 (Y5c) and Q40 (Y5d) go from ANSWER to CONFLICT with sides [[CY1a],[CY1b]] (Y1's dispute). Q37 is the question that separates the semantics: under blocking the defeater RY54 was discarded, under propagation it is live and unbeaten.
- Q41 (Y5e) goes from ANSWER [] to CONFLICT [[C3],[C4]]: the measure is fetched over the contested `cost_centre_of` with R313 withheld.
- Q30, Q32, Q34, Q42 and Q43 are unchanged.

Refutation moved to DL's team form (−σ) with no key change. Downstream CONFLICTs carry a `contested` why node `{goal, via, rules, roots}`, which `check_why.py` re-verifies against the reference.

**Effort.** One session per engine, every engine GREEN 1–8 at the end of its session, with mutation, isolation (DuckDB and Postgres) and negatives 15/15. Lines added / removed (`git diff --numstat`):

| | Files | + / − |
|---|---|---|
| shared | `reference.py`, `check_why.py`, `accept.py` | +249 / −13 |
| V3a | `defeasible.pl`, `ops.pl`, `host.py` | +171 / −20 |
| V3b | `engine.clj`, `ops.clj` | +142 / −18 |
| V3c | `engine.ex`, `ops.ex`, `why.ex` | +209 / −19 |
| V3d | `Engine.flix`, `Ops.flix` | +188 / −43 |
| V3e | `asp.py`, `host.py`, `probes.py` | +187 / −11 |

The shape of the change was the same everywhere: a three-valued twin of `lit` / `body` / `apply_rule`, a team-defeat `classify`, and a breadth-first walk (`contested_why`) for the why node. V3e put the three values into the program as status atoms (`PROP_META`) and kept the tree-building in the host.

**Latency**, `bench.py` decide_ms p50 / p95, before (ef6ec40, blocking) → after (propagation):

| Engine | DuckDB before | DuckDB after | Postgres before | Postgres after |
|---|---|---|---|---|
| V3a (memo) | 4.34 / 9.38 | 4.58 / 10.18 | 7.72 / 21.94 | 8.59 / 23.37 |
| V3b | 6.19 / 13.37 | 6.11 / 13.97 | ≈4.70 (p50) | ≈5.42 (p50) |
| V3c | 5.97 / 13.21 | 5.78 / 13.41 | 11.63 / 31.32 | 12.81 / 31.81 |
| V3d | 6.89 / 14.64 | 6.89 / 15.06 | 4.86 / 12.96 | 5.10 / 14.25 |
| V3e (plain after, doubled before) | 15.59 / 17.13 | 15.96 / 18.77 | 14.01 / 16.29 | 13.72 / 16.13 |

SQL statements per decide are unchanged (V3a–V3d 11.17, V3e 21.86): propagation adds no fetches. The differences (−4 % to +10 % on p50) are the size of the drift between bench runs, so no systematic cost is visible. The slice has almost no contested literals to follow, so this says little about a rule base full of disputes.

### Rule classes (§5, report only)

The slice's `:class` vocabulary, per class, over `slice.edn`, `extension.edn`, `cycles-acyclic.edn` and the integrity fixtures:

| Class | Rules |
|---|---|
| `definition` | R104 `booked_total`, R105 `headroom`, R110 `breach_in`, R112 `big_capital` (finance); R201 `role_limit`, R202 `limit_on`, R203 `governing_limit`, R204 `vendor_status_for` (procurement). All strict |
| `material_inference` | R106 `cap_breach`, R301 `has_approver`, R304 `cap_ok`, R305 `vendor_cleared`, R308 `eligible`, R309 `denied` (compliance), R310 `approved`; cycles-acyclic RY21, RY22, RY51, RY53, RY55, RY56 |
| `exception` | R306 (`vendor_cleared` for an emergency despite a suspended vendor); R307 (extension, a defeater on `neg vendor_cleared` for big capital); RY23, RY54 (defeaters) |
| `entitlement` | R311 `auto_approved`, R312 `approved` ← `auto_approved`; fixture RY31 `exempt_from_audit` ← `trusted` (Y3 file) |
| `incompatibility` | R314 (a denied request is never approved) |
| `superiority` | R313 (controller: finance over hr on `cost_centre_of`); RY4 |

**The entitlement rules:**
- **R311 is a policy permission.** Its doc says the request is "approved automatically, without further checks": an authority grants a status to a class of requests. It is a permission in the "may approve" sense, issued by procurement, and has nothing inferential about it.
- **R312 is an entitlement in the inferential sense.** "An automatically approved request is approved" licenses a defeasible step from one status to another. It commits to nothing new. It is defeasible because R314 can block it.
- **RY31 is a policy permission**, in the form of an exemption: "a trusted vendor is exempt from audit". It appears only in the rejected Y3 fixture.

**What the labels do not track:**
- **The original R301 was a permission.** `rules/rules.yaml` has `approver/2` as `class: entitlement` with "Someone **may approve** a request if …", and `worlds/S-s1/L3*/formal.pl` agrees. In the slice it became `has_approver`, a `material_inference`, so the permission was rewritten as a fact about the reporting chain.
- **Deontic status is spread over three classes.** R310 concludes `approved`, a deontic status, under `material_inference`, R312 concludes it under `entitlement`, and R314 forbids it under `incompatibility`. The class records the rule's inferential role, not whether its conclusion is a permission, obligation or prohibition.
- **The two vocabularies have drifted.** `rules.yaml` uses definitional | temporal | fitness | material_inference | defeasible | incompatibility | entitlement, and the slice uses six of its own. The inferentialist classes are used consistently within the slice; the deontic reading has no home in either.

The question this raises is in PROGRESS.

### Lesson 1, revisited again

With the rule base acyclic by IR-001a, propagation is stratified and three-valued. **No engine has it natively; every engine built it.**
- **The memo engines (V3a memo, V3b, V3c, V3d)** needed a three-valued twin of `lit` / `body` / `classify`, about 140–210 lines each, plus the guard as a backstop. Their native layer, plain recursion with a memo, carries two values.
- **V3e plain** encodes the three values as explicit status atoms (`PROP_META`: live, beaten, pro, ref, con) in one stratified two-valued model. The solver computes them, but the encoding is ours: the answer-set semantics gives two values, and "contested" is a derived atom, not a truth value.
- **V3a WFS was native only for blocking.** Its third value, undefined, arises only from loops. On an acyclic base the well-founded model is total, so it cannot carry a dispute downstream; it gave the blocking answers on Y5 (Q35 false, Q37 true) and was retired, not ported. ASP's doubled encoding is in the same position.

So the split in "Defeat cycles" lesson 1 changes again:
1. **The semantics no longer needs non-stratified negation.** IR-001a removed the case that only WFS and stable-model engines could answer. What remains is a stratified three-valued evaluation that any of the five platforms computes with about one session of work.
2. **The answer layer is still built everywhere**: statuses, sides, why trees, now with a `contested` node.
3. **Demand remains the one native difference**: top-down engines fetch only what a goal reaches; V3e keeps its magic-set rewrite and its roughly 2× SQL per decide.

### What each platform makes natural, again (A3 order)

This is not a choice. **Semantics may no longer separate the platforms**: with cycles rejected at load and propagation built the same way in all five, every engine computes the same keys from the same spec.

**1. Semantics.**
- *V3a:* memo mode is now the default, and WFS tabling is retired. What SWI made natural, answering cycles, is not asked for. Top-down demand is still free.
- *V3b, V3c, V3d:* the gap from "Defeat cycles" is closed by IR-001a and the guard, not by porting WFS. Each now gives the same answers as V3a.
- *V3e:* plain encoding, a single model with status atoms. It is natural for "compute every status at once", and it needs the host for trees and the demand rewrite for bounded fetch. Its one weak spot is gate-off behaviour on loops (CONFLICT with no sides).

**2. Guarantees.** Integrity is now one shared gate, so static checks no longer separate the platforms either. The engine-native layers still add something: Malli (V3b), the V3c validator and V3d's closed maps reject all 15 negatives by themselves, and Flix's compiler checks the evaluator code, not the runtime rules. Isolation is unchanged (by value in V3b–V3d, a Control per op in V3e, snapshot discipline in V3a). Explanations are built and complete on all five, now with the `contested` node.

**3. Operation.** Unchanged: V3c for supervision and throughput, V3b for transaction time, V3e for lock-free per-op Controls. The gate adds a subprocess call (about 60 ms) to load, `add` and `with_hypothesis` in V3b–V3d but not to `decide`; V3a and V3e import it in-process. An in-process port of the gate would be needed if rule changes became frequent.

**4. Footprint (information only).** Unchanged by this addendum. The shared gate is Python, so every engine now depends on the `.venv`.

**What changed.** The cycles addendum found a semantic difference between the platforms; this addendum removes it by policy (reject cycles) and by spec (propagation from `reference.py`). The choice for v3's T arm therefore rests on guarantees, operation and readability, as before "Defeat cycles", with one new item: whether the integrity gate should stay shared Python or become native to the chosen platform.
