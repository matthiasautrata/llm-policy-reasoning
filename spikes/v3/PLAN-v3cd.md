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
