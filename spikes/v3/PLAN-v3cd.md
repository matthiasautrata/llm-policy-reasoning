# Spike v3 addendum — V3c (Elixir · ex_datalog) and V3d (Flix)

Plan for Claude Code, 2026-11-24 (Matthias). Continue on branch `spike/v3`. Do not push. No API spend. Log deviations under **Decisions** at the end, as before.

## 0 Why, and ground rules

V3a (Prolog) and V3b (Clojure/Datahike) settled the **shape** of System A (rules and claims as data, a schema that sees rule bodies, isolated hypotheses, valid time as attributes, `fetch` as the only path to detail data). They did not settle the platform. This addendum adds two platforms that differ from both in kind:

- **V3c — Elixir on the BEAM**: processes, supervision, hot code reload, LiveView; set-theoretic gradual types (still arriving). Logic via `ex_datalog` or an own evaluator.
- **V3d — Flix on the JVM**: algebraic data types, an effect system, Datalog as first-class typed values with lattice semantics.

This is an exploration (PLAN Decisions 2026-11-24): expressiveness and insight weigh most; footprint is information only.

Ground rules as before:
- Same slice (`shared/slice.edn`), same contract (`shared/CONTRACT.md`), same checks: `accept.py` (1–6, `--mutation`), `isolation.py`, `bench.py` on DuckDB **and** Postgres, `check_why.py`.
- Same 12 negative model tests as V3a/V3b (`v3b-clojure/src/v3b/model.clj` `negatives`, `v3a-prolog/linkml/negatives.md`): pass iff 12/12 rejected.
- Rules are data loaded at runtime. No code generation from the slice, no recompilation when a rule or claim changes (check 3). If a platform forces this, stop and record it; do not work around it silently.
- Ask Matthias before installing system software (Erlang/OTP + Elixir, a JDK if needed, the Flix compiler). Language-level deps (mix, Flix packages, jars) are fine.
- Every library claim checked against current docs; record versions.
- Timebox: V3c 3 sessions, V3d 3 sessions. Not green at the end: stop, record what is missing and why.
- Order: V3c, then V3d.

## 1 V3c — Elixir · ex_datalog · DuckDB/Postgres (`spikes/v3/v3c-elixir/`)

### 1.1 Stack (verify each)

- Elixir ≥ 1.19 / OTP ≥ 28 (record versions; note the state of set-theoretic type checking in that release).
- **ex_datalog** (`thanos/ex_datalog`, MIT). Pin an exact version (0.5.x at the time of writing). It is young and pre-1.0 with API churn: read its changelog and migration guides first, and record which features are experimental (magic sets).
- **SQL boundary**: prefer `adbc` (elixir-explorer; drivers for DuckDB, PostgreSQL, Snowflake) for both backends. Fallbacks: `duckdbex` (NIF) for DuckDB, `Postgrex` for Postgres. Record which was used and why. The concept → SQL bindings come from the slice, as in V3a/V3b.
- **EDN reader**: try an existing hex package first (record name, version, maintenance); otherwise write a reader for the subset with NimbleParsec. Record lines.
- **Model validation**: choose the most idiomatic option (structs + a validation library, e.g. Peri, NimbleOptions or Ecto embedded schemas; or a hand-written validator over the EDN data). It must see inside rule bodies like Malli and the structured LinkML model. Record the choice and why.

### 1.2 Key questions V3c must answer

1. **What does ex_datalog carry?** The defeasible layer (team defeat, ambiguity blocking, superiority, functional rivals, R314 incompatibility) reasons over proof results, which did not fit Datahike's Datalog rules. Try first:
   - ex_datalog for the strict, recursive part (ancestors, reporting chain) over facts fetched through `fetch`, with BEAM callback predicates as the fetch hook;
   - its `Explain` derivation trees as the source of `why` nodes.
   Then decide whether the defeasible layer can be expressed in ex_datalog (stratified negation only, no well-founded semantics) or must be an Elixir interpreter over its results, as in V3b. If ex_datalog gets in the way, an own evaluator in Elixir is a valid outcome; record exactly where it got in the way.
2. **Isolation.** Pass the state as an immutable value (the idiom), and/or run a hypothesis in its own process. Run `isolation.py`; measure hypothesis latency (p50/p95 over 50 runs) against V3a `snapshot/1` (0.11 ms), V3b `d/with` (2.7 ms) and branch (103 ms).
3. **Runtime extension.** Check 3 (a claim and a rule added at runtime) without restart.
4. **BEAM side benefits, probed, not built out** (record effort and outcome, each a short probe):
   - a supervision tree for System A (store, SQL pool, evaluator) and what happens when the SQL connection process is killed mid-decide;
   - concurrency: `bench.py` decisions run concurrently (e.g. 8 parallel) against both backends; throughput and p95;
   - hot code reload: change the evaluator module (e.g. a log line) while a decide loop runs, without dropping requests;
   - optional, only if time remains: a minimal LiveView page that shows a `decide` result and its `why` tree. Effort only; no styling.
5. **Types.** What does Elixir's type checking catch in this code base today (run the compiler with its type warnings; record findings), compared with Flix in V3d?

## 2 V3d — Flix · DuckDB/Postgres (`spikes/v3/v3d-flix/`)

### 2.1 Stack (verify each)

- Flix compiler (record version; Flix requires a recent JDK — use the JDK already installed for V3b if it fits).
- **SQL boundary**: JDBC through Java interop (DuckDB JDBC, PostgreSQL JDBC — the drivers V3b uses), behind Flix's effect system (record how IO/effects are typed at the boundary).
- **EDN reader**: Java interop to an existing EDN reader (e.g. edn-java, or Clojure's EDN reader jar), or a parser in Flix. Record the choice and lines.
- **Model**: algebraic data types for terms, literals, rules, claims. Validation = parsing EDN into the ADTs plus checks the type system cannot express. The 12 negatives must be rejected at that boundary; record which are caught by the types themselves and which needed explicit checks.

### 2.2 Key questions V3d must answer

1. **Can rules loaded from data at runtime become Flix Datalog values?** Flix supports first-class Datalog constraints constructed and composed at run time, but its predicate symbols and their types are fixed at compile time. Try, in this order, and record what works:
   - **(i) fixed predicate vocabulary**: the slice's predicates are known; build Datalog constraint values from parsed EDN rules at runtime over those typed predicates;
   - **(ii) reified encoding**: generic relations (e.g. a predicate name plus a vector of values) with rules as data and a fixed meta-program in Flix Datalog;
   - **(iii) own evaluator in Flix** over ADTs, using Flix Datalog only where it fits (e.g. recursion over fetched facts), as V3b and V3c did;
   - **(iv) generating Flix source from the slice and compiling** — record the cost only; it violates "no compile on rule change" and is not an acceptable final answer.
2. **Lattice semantics.** Probe whether claim standing (`holds` > `holds with qualifier` > `rebutted`, or a qualifier set) or derived confidence can be expressed as a lattice-valued predicate, so that standing propagates through derivation natively. A short probe with a written result; not required for green.
3. **Isolation.** Datalog values are immutable; a hypothesis is a different value. Run `isolation.py`; measure latency as in §1.2.2.
4. **Explanations.** How much of `why` / `why_not` comes from Flix (provenance, if any) and how much is built? Trees must pass `check_why.py`.
5. **Types and effects.** What did the type and effect system catch during development (record concrete defects caught at compile time), and what did it cost in ceremony?

## 3 RESULTS.md

Do not rewrite earlier sections. Add **"V3c and V3d"** with:
- the §7 table extended to four columns (V3a/V3b values from "After the V3a fixes"), plus rows for: concurrency throughput, supervision/failure behaviour (V3c), lattice probe (V3d), what the type system caught (V3c, V3d), and whether rules-as-data reached the native Datalog (V3c, V3d);
- answers to the key questions of §1.2 and §2.2, each with evidence;
- additions to "What we learned about the architecture", if any, independent of which platform is preferred;
- a short revisit of the recommendation across four platforms. Readability remains Matthias's call.

## 4 Layout

```
spikes/v3/
  PLAN-v3cd.md     this file
  v3c-elixir/      mix project, cli
  v3d-flix/        flix project, cli
```

Both CLIs speak the same JSON contract and support the test-only `sleep` op and `concurrent` / `after` script keys used by `isolation.py`.

## Decisions

(Executor: append dated entries — what was decided, why.)

**2026-11-24 · Installs (approved by Matthias).** `brew install erlang elixir flix` → Erlang/OTP 29.1.2, Elixir 1.20.5, Flix 0.80.0. The existing openjdk 27.0.1 is used for Flix and the JDBC drivers.

**2026-11-24 · V3c library versions (checked against hexdocs and the deps' sources).** ex_datalog 0.5.0, adbc 0.12.1, nimble_parsec 1.4.2, jason 1.4.5. adbc 0.12.1 pins DuckDB 1.5.1, which cannot read `slice.duckdb` (written by DuckDB 2.0.1), so `config.exs` pins DuckDB 2.0.1 through the driver's tar.gz URL. Postgres goes through the ADBC postgres driver: `$n` placeholders, and numerics come back as strings or Decimal, which `V3c.SQL` normalises.

**2026-11-24 · V3c EDN reader and validation.** `eden` was not used: its last release is 2.1.0 from 2020-10-31 (hex), and the slice needs only a small EDN subset (keywords, symbols as logic variables, vectors, maps, sets, strings, numbers). The reader is a NimbleParsec grammar (`V3c.EDN`). The record schema is a hand-written validator (`V3c.Model`) because no Elixir library maps onto the LinkML model. The same 12 negatives are rejected. As in V3b, `add` and `with_hypothesis` validate their records too.

**2026-11-24 · V3c evaluator: own, not ex_datalog.** System A's defeasible evaluator is a port of V3b's `engine.clj`. Facts are fetched on demand, there is a per-op memo, and there are why trees. The evaluator runs over the immutable `%V3c.Store{}`. The per-op memo and the SQL cache live in the process dictionary of the process running the op. That gives isolation by construction, since each op is its own process in concurrent mode. ex_datalog is evaluated as a probe (`probes/datalog_probe.exs`) and not as the engine, because:
- its stratifier rejects the defeasible meta-program;
- its relations are fixed-arity, which forces rule bodies to be reified;
- it materialises bottom-up over fetched relations, whereas check 5 wants bounded per-goal fetches.

See RESULTS "V3c and V3d" for the numbers.

**2026-11-24 · V3c Postgres latency is noisy.** Four runs of bench.py on Postgres gave decide p50/p95 of 15.5/37.7, 7.9/19.6, 15.0/36.1 and 15.0/36.6 ms. All four had 0 errors, 49/200 approved and 11.17 statements per decide. The committed `bench-postgres.json` is the first run. In-process, after a warm-up pass over the same 200 requests, one process on one connection gives p50/p95 of 4.9/12.7 ms (`beam-postgres.json`). V3b measured 5.2/17.3 ms. The statement count is identical, so the spread lies in Postgres-side and driver-side warm state, not in the evaluator. Not investigated further; this is footprint information only.

**2026-11-24 · V3c probes, and what they changed.**
- **ex_datalog** (`results/datalog-probe.txt`). Its default `timeout_ms` is 30 s per stratum, and a timeout returns `{:ok, knowledge}` with `stats.termination: :timeout`. The probe's first run compared such a truncated result with the CTEs. It now checks the termination field and passes `timeout_ms: 600_000`.
- **Explain** is probed on a 5-edge graph. On the full ancestor relation it ran out of memory (12.7 GB RSS, process killed), because provenance stores no bindings.
- **LiveView** was skipped. It is optional in §1.2, the timebox went to the probes above, and the contract needs no UI.
- **Hot reload** uses `Code.compile_string/2` on a modified `engine.ex`, loaded twice, so the second load purges version 1 while the 8 workers run. A release upgrade (appup or relup) was not tried.

**2026-11-24 · V3d stack (versions checked against the Flix 0.80.0 docs and stdlib source, and Maven Central).** Flix 0.80.0 on openjdk 27.0.1; DuckDB JDBC 2.0.1.0 and PostgreSQL JDBC 42.7.15 as `mvn-dependencies` in `flix.toml`. The driver is instantiated directly (`new DuckDBDriver()`, `new org.postgresql.Driver()`) instead of going through `DriverManager`. That makes one plain constructor call per backend and does not depend on ServiceLoader registration in the fat jar; `DriverManager` was not tried. Postgres needs `stringtype=unspecified` so that string parameters bind against date and numeric columns. All JDBC calls are typed `\ IO`, and the boundary is `Sql.flix`. The evaluator does no IO itself: it performs a user-defined `Eval` effect (fetch, memo, fresh names, failure), which `Sql.withEval` handles for one op. Model, Store and Edn are pure. The CLI and the probes run with `-Xss512m`, a large main-thread stack for the deeply recursive evaluator and solver. It was set as a precaution; a run at the default stack size was not measured.

**2026-11-24 · V3d EDN reader: hand-written in Flix (181 lines).** There is no Flix EDN library. Java interop to edn-java 0.7.1 or to Clojure's reader was rejected: both hand back `java.util` collections, which would need converting into Flix values anyway. A parser straight into a Flix `Edn` ADT avoids that conversion and stays typed.

**2026-11-24 · V3d model and the 12 negatives (`results/negatives.txt`, `-Dprobe=negatives`).** The model is a set of ADTs for terms, literals, rule forms, claims and concepts. The parser targets these ADTs ("parse, don't validate"), and 12/12 negatives are rejected with a path and a message. 10 of them fall out of the parse: no value of the ADTs can represent them (owner and role enums, rule kind, arity and shape of literals, `?` variables, `[:neg <literal>]`, fetch filters as a map, `:is` operators, superiority owners, and a concept's `Source` as `Sql | Derived`). 2 need checks the types cannot express: the ISO date regex and closed maps (unknown keys). `Not` was narrowed to wrap a goal literal only. Validation stops at the first error, unlike Malli, which collects them all. `add` and `with_hypothesis` validate through the same parser.

**2026-11-24 · V3d evaluator: own (route iii), Flix Datalog in the probes only.** System A's evaluator (`Engine.flix`, 624 lines with the why/why_not trees) is a port of V3b/V3c. It runs over the immutable Store record, with on-demand fetches and a per-op memo. Flix Datalog is not used in System A. The probes for routes (i), (ii) and (iv), and the reasons, are in the next entries and in RESULTS "V3c and V3d".

**2026-11-24 · V3d Flix pitfalls (cost of the ceremony, recorded).**
- Keywords that collide with ordinary names: `query`, `force`, `run`, `eff`, `inject`, `pquery`, `psolve`, `solve`.
- Java varargs calls need an explicit array. A fully qualified Java type does not parse in a signature, so each one needs an `import ... => Alias`.
- `main` has the effect signature `IO + Chan + NonDet` once it spawns threads.
- `spawn` admits only `IO + Chan + NonDet`. A thread cannot touch the parent region's `Ref`, which the compiler rejects (E6469). So each `concurrent` thread gets its own `Ref` holding the store value as it was at the spawn. That gives isolation by construction, and the compiler enforces it.
- Datalog solving is pure, so the optimiser may move it past a clock read. Timings need an IO call that uses the result (`pin`).
- `/dev/stdin` is read with `Files.readString`.
- The probes are a separate Flix project, `probes/`. Its `src/` symlinks System A's sources, so the probes see the real modules without a package build.

**2026-11-24 · V3d Q1 probes (`results/probe-*.txt`).**
- **(ii) reified encoding** (`Reified.flix`): rules as data plus a fixed meta-program over generic `Fact(pred, args)` relations. The ancestor closure gives the same 9497 facts as the typed program, but takes 8.6 s with facts keyed by predicate (67 s unkeyed), against 0.2 s for the typed program, about 45×.
- **(i) runtime-built programs** (`Translate.flix`): the slice's rules are translated into Flix's `Fixpoint3` AST, which user code can reach (it is what the solver runs; the documented user API is the compile-time `#{}` syntax), and solved by `Fixpoint3.Solver.runSolver`. This is the only way a Datalog program can come from data, since the `#{}` syntax is compile-time. 16 of 19 logic rules translate. The 3 that do not:
  - R106: a comparison over an arithmetic term;
  - R202 and R304: not range-restricted, with a variable bound only by the caller (goal-directed).

  Findings:
  - `BodyPredicate.Functional` takes outputs *before* inputs. Both are `Vector[VarSym]`, so swapping them type-checks and only crashes inside the solver (`getOrCrash`).
  - **The runtime path has no negative-cycle check.** `p :- q, not r. r :- q, not p.` built at runtime "solves" and derives both p and r, which is unsound. The same program as a typed `#{}` value is rejected at compile time with E5914 (`results/neg-cycle-typed.txt`).
  - The runtime path also assumes range restriction; the translator checks it.
  - Bottom-up needs a demand domain: a parameterised concept must be materialised for every binding, and the domain (all cc ids, the distinct requesters) was chosen by hand. That materialised 782,603 fetch facts in about 38 s.
  - Materialising `pending_exposure` for every centre, root included, overflows the slice SQL's `CAST(SUM(...) AS INTEGER)` (3,830,473,000). This is a latent bug in the slice's SQL, reachable only bottom-up. It was left as found, because the slice is shared and the top-down engines never ask for the root.
- **(iv) codegen, cost only:** `flix check` takes 2.7–2.9 s and `build-fatjar` 9.6 s, plus a 1.7 s JVM cold start, and the in-process state is lost. Not pursued.

**2026-11-24 · V3d type probe (`probes/types/`, `results/type-probe.txt`).** The V3c planted defects T01–T10 were re-planted as Flix analogs, each checked alone against System A's sources. 9/10 were caught at compile time (V3c with Elixir 1.20: 4/10). The miss is T02, a misspelt key on a SQL row, because rows are `Map[String, Value]`. T03 (a bad child spec in V3c) has no Flix analog, since there is no supervisor; the defect planted instead is a spawned thread touching the parent's `Ref`, which is caught. Two extras with no V3c analog are both caught: an IO effect leaking from a function declared pure (E8752), and a non-exhaustive match on a literal form (E5952).

**2026-11-24 · V3d throughput probe added (`probes/par.py`, `results/par-*.json`).** The plan's concurrency row needs a V3d number. The probe runs the bench's 200 seeded decides through the CLI's `concurrent` key on 1 thread and on 8 threads, each thread on its own JDBC connection, after a sequential warm-up of the same 200 for the JIT. The answers are identical between 1 and 8 threads, and there are 0 errors.

**2026-11-24 · V3d hypothesis latency is higher than V3c's** (`results/hyp-latency-*.json`). Q11 (withhold R313, then decide) has p50/p95 of 0.49/1.40 ms on DuckDB, against V3c's 0.19/0.33. A plain decide on the same request is 0.21/0.34 against 0.13/0.15. Deriving the hypothesis store itself is 0.016 ms, so the difference lies in the evaluator, not in the hypothesis mechanism. Not investigated: this is footprint only.
