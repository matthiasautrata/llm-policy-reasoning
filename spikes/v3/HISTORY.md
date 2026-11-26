# Spike v3 history

How spike v3 (System A: rules and claims as data, a defeasible engine, a bounded SQL `fetch`) got to its current state. `RESULTS.md` describes the current state only, and this file holds what came before it.

**Everything removed is reachable from the git tag `spike-v3-five-platforms`** (commit 006b2dd). That includes the five spikes, the executed plans, `SEMANTICS-cycles.md`, `cycles.edn` and every results file of a dropped engine or retired mode. For example, `git show spike-v3-five-platforms:spikes/v3/RESULTS.md` gives the full results as they stood. All dates are 2026.

## Phases

### 1 Initial: V3a vs V3b (2026-11-24; fcd9480..8828f1b)

**Question.** Should System A be LinkML · SWI-Prolog · DuckDB (V3a) or EDN/Malli · Clojure · Datahike (V3b), with the same contract (`shared/CONTRACT.md`), slice and 100k-request world, judged by the acceptance checks 1–6?

**What was built.**
- Shared: the world generator, `slice.edn`, questions, `reference.py` keys, `check_why.py`, `accept.py` (with a mutation test) and `bench.py`.
- Both engines, both green on checks 1–6, and the LinkML and Malli models.

**Decisions and why.**
- Rules are authored once in EDN, so that differences are engine differences.
- Python hosts Prolog through janus, because Prolog-side `py_call` bound to the system Python.
- The defeasible semantics: functional predicates as rivals, claims as defeasible facts with asserter authority, and superiority ordered explicit → strict → authority → later.
- §7 weights expressiveness and insight. Footprint is information only. "This is an exploration, not a selection."

**Findings that still hold.**
- The `fetch` boundary is the stable part: 11.17 SQL statements per decide, no table ever loaded, and a backend swap is a config change.
- Backend independence: DuckDB and Postgres 18 gave the same answers and explanations, SQL text aside (check 2), in every later phase too. That settled it, so Postgres and check 2 were retired on 2026-11-25 (phase 7; the last Postgres outputs are at tag `spike-v3-housekeeping`).
- The defeasible layer is small, about 150–200 lines, and is built, not native.
- "Rules are data, interpreted at runtime" matters more than the platform.
- Valid time and assertion provenance (`asserted_by`/`asserted_at`) are semantic attributes. Transaction time is only an audit axis.
- Re-verifying the explanations (`check_why.py`, guarded by the mutation test) was the main correctness tool.

**Reversed.** The recommendation rested on two deciding facts: V3b's hypotheses as values (V3a not isolated), and Malli seeing rule bodies (LinkML treating them as strings). Both were reversed by phase 2.

### 2 V3a fixes (2026-11-24; 930c50d..33ac69b)

**Question.** Can V3a close both gaps?

**What was built.**
- F1: `snapshot/1` hypotheses with a memo keyed by state, and `shared/isolation.py` (a concurrent op must not see an open hypothesis).
- F2: structured rule bodies in LinkML, with 12/12 negatives rejected.

**Decisions and why.**
- F1.6, threading the state as a value through the Prolog evaluator, was skipped to keep the timebox for F2.

**Findings that still hold.**
- `snapshot/1` isolates the dynamic database at 0.11 ms. Anything outside it is a discipline: memo keys, global variables, the Python-side cache.
- LinkML 1.12.1 validates a *converted copy*, so the converter is part of the trust chain.
- Two of its schema rules were silent no-ops (`rules` without `preconditions`; `any_of` not inherited through `is_a`), and only negative tests exposed them.
- An earlier Postgres latency difference was run-to-run variation.

**Reversed.** "Carry forward V3b's shape because of two facts" became "the shape can be built in either stack; the stack is open".

### 3 V3c Elixir and V3d Flix (2026-11-24; edf25eb..d51f3ca)

**Question.** Do the BEAM or Flix's Datalog, lattices and types change the picture?

**What was built.** Both engines are green on checks 1–6. Each needed its own evaluator, ported from V3b. There were probes of ex_datalog, supervision, throughput, hot reload, the Flix `Fixpoint3` path, lattices, and planted type defects.

**Decisions and why.**
- Own evaluators were written, because no Datalog engine accepts the defeasible meta-program: it needs non-stratified negation.
- adbc's DuckDB was pinned by URL, to read the slice file.

**Findings that still hold.**
- The defeasible layer is not native Datalog on any platform.
- Top-down with bounded fetch is part of the shape. Bottom-up materialised 782k facts and hit SQL that no question asks.
- Rules as data lose the compiler's checks, so the model must take them over. This led to the shared model check.
- The INT32 overflow in `pending_exposure` was found here; it was fixed in phase 4 (A1).

**Reversed.** "Pick by secondary property (V3c, V3d, V3b, V3a)" was set aside for an ordered revisit (PLAN-v3-cycles A3), and then settled by the platform decision.

### 4 Defeat cycles: V3a WFS and V3e Clingo (2026-11-25; 48e1af1..5fc38c0)

**Question.** Can engines *answer* cyclic defeat (Y1–Y6, Q30–Q39) under WFS with ambiguity blocking (`SEMANTICS-cycles.md`)?

**What was built.**
- Shared: `cycles.edn`, `reference.py` `Cyc` (an alternating fixpoint), the `BIGINT` fix, and `model_check.py` with cycle and bound-variable checks plus a `cycles: reject | report` flag.
- V3a WFS: SWI tabling with `tnot`.
- V3e: clingo 5.8.0 with a doubled encoding, so that cautious and brave consequences give WFS, and a magic-set demand rewrite.

**Decisions and why.**
- A1: fix the SQL at the binding.
- A2: static checks once, in shared Python.
- A3: revisit the platforms in the order semantics → guarantees → operation → footprint.
- Y5 was decided as ambiguity *blocking*.

**Findings that still hold.**
- Memo evaluators crash on a real cycle: nothing marks a goal as in progress (StackOverflowError, stack limit, or timeout). This is why the re-entry guard exists.
- Cycle detection in the model check (now IR-001a).
- An ASP unsat core (clingexplaid MUS) names the odd loop's members in 0.2 ms.
- The plain two-valued ASP reading is not WFS: Y3 has no model.
- DL equals the Kunen semantics of its metaprogram, not WFS (Maier, confirmed in the sources).

**Reversed by phase 5.**
- Cycles are now *rejected at load* (IR-001a), not answered, so the WFS and ASP capability is no longer asked for.
- Blocking was replaced by propagation: Q35, Q37, Q40 and Q41 now give CONFLICT.
- "Semantics separates the platforms" no longer holds.

### 5 Integrity and propagation (2026-11-25; ccd9846..887b042)

**Question.** Make the rule base safe at load time, and propagate ambiguity downstream.

**What was built.**
- Phase 1: flat claims, `recorded_at`, additivity on every measure, Q25, and 15 negatives.
- Phase 2: one gate, IR-001a…IR-006 (`model_check.py` through `integrity.py`), run at load, `add` and `with_hypothesis` in all five spikes, with fixtures under `fixtures/integrity/`, check 8, and a re-entry guard in the memo evaluators.
- Phase 3: `SEMANTICS.md` (proven, refuted, contested; team-form refutation) in `reference.py` and in all five engines, one session each, all GREEN 1–8.

**Decisions and why.**
- Cycles are rejected, because the Warrant-Layer prefers a working engine to completeness and cyclic defeat is exotic in day-to-day policy.
- Rejections are identical across engines, because the gate runs before engine-specific validation.
- IR-002 "artifact" was defined precisely.
- IR-003 holds by construction in the slice. Its check rejects ordering keys.
- IR-005 checks that a completeness claim exists, not its scope. The qualifier applies to positive answers only.
- The why node gained a `rules` field, needed to tie it to rule ids.
- Y5e was approximated by a measure over a contested binding.

**Findings that still hold.**
- Q01–Q27 are byte-identical under propagation. Only the synthetic Y-questions moved.
- Propagation costs no measurable latency and adds no fetches.
- No engine is native for three-valued propagation; each needed a three-valued twin of `lit`/`body`/`classify`, about 140–210 lines.
- The rule-class report: `:class` records inferential role, not deontic status (PROGRESS question on deontic rules).

### 6 Pruning to Python + Prolog (2026-11-25; 006b2dd..86924f8, tag `spike-v3-housekeeping`)

**Question.** Keep only what the decided platform needs.

**What was done.**
- Tagged `spike-v3-five-platforms`.
- Deleted V3b–V3e, V3a's WFS mode, the blocking semantics, `cycles.edn`, `SEMANTICS-cycles.md` and the executed plans.
- Rewrote RESULTS and PROGRESS to the current state, and wrote the repo-wide `INVENTORY.md`, which is now summarised in the root `HISTORY.md`.
- `PLAN-v3-housekeeping.md` (at the tag) lists each removal with its line counts, for example defeasible.pl −185/+12 and reference.py −167/+10.

**Findings.**
- Keys were byte-identical before and after the pruning, and every check of the gate passed on both backends.
- One defect was introduced and caught by the gate: a stray `}` in `model_check.py`'s f-string, left by removing the engine flag.
- Kept because current claims cite them: `gen.py`, `hyp_latency.py` and the LinkML artefacts.

### 7 Benchmark preconditions (2026-11-25; 105c967..fc5e834, tag `spike-v3-preconditions`)

**Question.** Finish the cleanup to DuckDB only, then make the slice express and exercise what the benchmark needs: aggregation over derived literals, a qualifier on answers that rest on absence, and questions downstream of real conflicts. `PLAN-v3-preconditions.md` (at the tag) holds every Decision.

**Decisions and why.**
- Postgres and check 2 retired, since backend independence was shown (phase 1). Check numbers are kept, not renumbered, because the docs cite them. The V3e packages and psycopg left `.venv`.
- `[:agg :sum|:count ?x [L1 .. Ln] ?out]` over proven members; any contested member contests the aggregate, and the total over the proven ones appears only in the contested node. R314 became an attacker of `approved` inside the evaluator so that a member can be contested by it (11.17 → 11.92 SQL per decide).
- Every `decide` key holds the qualifier; `:check_qualifier` retired, because a per-question flag left most negatives unchecked.
- Coverage is derived (PROGRESS 14, IR-005 amended): a predicate is covered by an in-force `[:complete "N"]` claim, or when no claim asserts it and every rule that concludes or attacks it reads only covered names. Claims are not assumed complete. Recursion counts as covered. C10 does not cover `cap_breach`.
- IR-007 `unsafe-aggregation` (PROGRESS 11) treats every parameter of a semi-additive measure as unsafe, since the slice maps none to a dimension. Fixture RA1.
- The aggregate push-down (PROGRESS 15) as rounds over the per-op cache, not as SQL compilation, so the rules stay data run by the one evaluator. Fetches inside an aggregate are paged. The cost fixes needed: a round-scoped memo for misses, a Prolog copy of the fetch cache, `variant_hash` keys, a `keysort` grouping. The CLI config gained an optional `stack_limit`.

**Findings kept.**
- R315/R316 put five base questions downstream of C3/C4 and R312/R314. V3a needed no change: propagation already handled them.
- The push-down bounds statements: 693 at the root against about 260 000 one member at a time; no statement exceeds `fetch_limit`.
- The cost moved into the evaluator: the root takes 208 s and peaks at 12.1 GB (about 925 000 memo entries). This is the open question of `PLAN-v3-memory.md`.

**Findings reversed.**
- "A truncated fetch inside an aggregate is an ERROR" and "L1 and the root exceed `fetch_limit`": reversed by paging (fc5e834).
- "Fetch volume is linear in the members, about 2.9 statements each": reversed by the push-down. Latency is still linear.
- "Completeness covers by predicate name only" (§2.2): replaced by derived coverage (ae7d906).
- Q26/Q27 retired: they duplicated Q01/Q09.

### 8 Memory and aggregate cost (2026-11-25; 11b425e..2f60623, tag `spike-v3-memory`)

**Question.** Why does the root aggregate (`[:approved_total "cc0000" ?v]`, 90 028 members) take 207 s and peak at 12.7 GB, and what is the strategy for large aggregates? `PLAN-v3-memory.md` (at the tag) holds every Decision.

**Decisions and why.**
- Attribution by scratch probes, not engine code. The three memo hypotheses held (proof trees stored per entry, copied back per lookup, built for every member), but the largest cost was DuckDB running `flush()`'s UNION ALL batches of the recursive `reporting_chain` CTE.
- SQL remedy (Matthias): `:batch_sql`, a set form of a concept's SQL for its one required parameter. L2 statement +2089 → +3 MB.
- Rules indexed by head predicate (`rule_at/2`): root 207 → 139 s.
- Fix A: the memo holds statuses only; why trees are rebuilt on demand by re-running the deterministic `best_sol/7` (`hydrate/4`). The aggregate node gained `count` and shows a sample of `agg_sample` (default 20) members; contested members are reported by the `contested` node. Keys: `agg_count` added to Q44 and Q45, nothing else changed.

**Findings kept.**
- Root after the fixes: 110 s and 4.6 GB in SWI's default 1 GB stack; memo 54 MB (was 1.8 GB), about 58 bytes per entry; bench peak 175 MB.
- About 1.2 ms per pending member from L2 up; the evaluator is about 94 % of the root's time (SQL 7.3 of 132 s). About 3 GB of the root's peak is unattributed.

**Findings reversed.**
- "The memo is the cost": reversed by attribution (DuckDB batches first, then the memo, both fixed).
- The §5 proposal (compile aggregate bodies to SQL as an execution path) was not adopted: Matthias scoped the system to questions about the data, and the root became a documented residual (`PLAN-v3-sqlform.md`).

### 9 One SQL form per concept (2026-11-25; 8f97c23..73e4014, tag `spike-v3-sqlform`)

**Question.** Can each concept have a single SQL text for single and batched fetches, removing `:batch_sql` (a second text that must agree with the first, an IR-002 risk)? And what is the scope for large aggregates? `PLAN-v3-sqlform.md` (at the tag) holds every Decision.

**Decisions and why.**
- Scope (Matthias): the system answers questions about the data, not big-data queries. The root aggregate is a documented residual; no probe query and no SQL generator as an execution path. Compiling rules to SQL may return as an answer, to be decided in the benchmark design.
- One form: each required parameter `$p` is written `IN ($p)` and `p` is an output column, so a single key is a set of one. All six parametrised concepts took it naturally. `sql.register` rejects any other shape (engine-local, not an IR). `flush()` keeps a `UNION ALL` of single-key statements where more than one filter column varies.
- A nonexistent centre now gives no row for `booked_total` and `pending_exposure` (was one row of 0), as for the other concepts; no key asks about one.

**Findings kept.**
- Keys byte-identical. Root 4.6 → 2.8 GB and 110 → 108 s; L1 1.0 GB → 419 MB; L2 173 MB; bench peak 175 → 162 MB.

**Findings reversed.**
- PROGRESS question 17 (two SQL texts that must agree) withdrawn: one text remains.

## Platform lessons (platforms dropped, lessons kept)

- **V3b, Clojure · Datahike · Malli.**
  - Database transaction time is not assertion time. A tx-time view of 2026-07-15 held 0 rules, because rules were transacted at load. Sub-claims inherited the parent's asserter, and backdated instants arrive out of order. Assertion time must be an attribute, and tx time is an audit axis ("what did we know when we decided").
  - `d/with` gave hypotheses as immutable values at about 2.7 ms, isolated by construction. Datahike branches (about 103 ms, experimental) suit long-lived proposals.
  - Malli validated the values the engine runs, rule bodies included, with readable custom messages.
- **V3c, Elixir · OTP.**
  - Supervision restarted a killed SQL connection in under 0.5 ms with 0 wrong answers.
  - 8 processes gave 2.1× throughput on DuckDB and 5.9× on Postgres.
  - Hot reload under load gave 0 errors.
  - ex_datalog 0.5.0 rejects the defeasible meta-program (`:unstratified_negation`), truncates silently on timeout, and its `Explain` blows up (82,195 nodes for a 3-step proof).
  - The type checker caught 4/10 planted defects.
- **V3d, Flix 0.80.0.**
  - The compiler caught 9/10 planted type defects, plus effect leaks and non-exhaustive matches, but not in rules loaded at runtime. Its one miss is the untyped SQL row.
  - The runtime `Fixpoint3` path has no negative-cycle or range-restriction check: a runtime cycle "solves" unsoundly. It is also bottom-up only.
  - The lattice carries graded standing natively. Defeat is not monotone, so it stays in the evaluator.
  - Compiler-enforced thread isolation.
- **V3e, clingo 5.8.0.**
  - An unsat core names cycle members for free.
  - xclingo 2.0b24 fails on its own README example under clingo 5.8.0, and clingexplaid explains unsatisfiability, not derivations, so trees were built in the host.
  - Per-op grounding (about 5 ms) dominates latency, about 3× V3a.
  - Bounded fetch needs a magic-set demand rewrite: 21.9 statements per decide against 11.2.
  - The plain encoding is two-valued: three values need explicit status atoms. Equivalence with WFS needs the doubled encoding.
- **All platforms.**
  - "Rules are data, interpreted at runtime" mattered more than the platform. Every platform ended up running the same top-down evaluator over the same `fetch` boundary.
  - Independent re-verification of proof trees (`check_why.py`, guarded by the mutation test) was the main correctness tool. It surfaced V3a's three engine bugs and checked every port.

## Decision (2026-11-25, Matthias)

**Python + Prolog.**
- The engine is SWI-Prolog via janus (V3a, memo mode, propagation).
- `shared/reference.py` stays the independent oracle, and is never promoted to engine, because the engine would then check itself.
- The integrity gate stays shared Python.

**Rationale.**
- With cycles rejected and propagation specified, semantics no longer separates the platforms.
- V3a has the shortest evaluator, the lightest footprint and native top-down demand. Prolog's standing at JPMC has improved, because another team already uses it.
- Clingo costs a demand rewrite and about 3× latency.
- Clojure's JVM operation and Elixir's admissibility count against them, and Flix is too niche to staff.

**Fallback (documented, not built).** If SWI-Prolog is refused at JPMC, a separate Python engine written from `SEMANTICS.md`, distinct from `reference.py`.
