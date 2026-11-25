# Spike v3 addendum — V3a fixes before the comparison is settled

Plan for Claude Code, 2026-11-24 (Matthias). Continue on branch `spike/v3`. Do not push. No API spend. Timebox: one session. Log deviations under **Decisions** at the end, as in `PLAN.md`.

## Why

`RESULTS.md` recommends V3b's shape on two deciding facts. Both are partly artifacts of how V3a was built, not of its stack:

1. **"V3a's adoption gate has no isolation."** V3a mutates the global store with assert/retract under `setup_call_cleanup` (`ops.pl` `with_hypothesis`). SWI-Prolog has transactions and snapshots (`transaction/1`, `snapshot/1`), which may give isolated hypotheses natively. Not tried.
2. **"LinkML cannot see inside rule bodies."** PLAN §5.1 told V3a to keep rule heads and bodies as EDN *strings* in a `body` slot. That compares rules-as-strings with rules-as-structured-data, not LinkML with Malli. LinkML can model bodies as nested classes. Not tried.

Fix both, re-measure the affected criteria, and update `RESULTS.md`. The goal is a fair comparison, not a V3a win.

## F1 — Isolated hypotheses in V3a

1. Read the SWI-Prolog 11 docs for `transaction/1`, `snapshot/1` and their isolation guarantees (visibility to other threads, interaction with tabling and with `retract` on clauses visible before the transaction). Record the version and what the docs say.
2. Replace the assert/retract mechanism in `with_hypothesis` with `snapshot/1` (or `transaction/1` + rollback, whichever the docs show is correct for "evaluate, then discard").
3. **Memo:** the per-op memo (`memo/3`) is global. Inside a hypothesis it must start empty or be keyed by state; base-state memo entries must never be used under a hypothesis and vice versa. Make that explicit and test it.
4. **Concurrency test** (new, for both spikes, add to `shared/accept.py` as check 4b or a separate `shared/isolation.py`):
   - thread/process A runs `with_hypothesis` (withhold R313) on the e077 question, with an artificial delay inside the hypothesis;
   - B asks the same question against the base state during A's delay;
   - pass iff A sees CONFLICT and B sees the base answer, and the base is unchanged afterwards.
   - For V3a, run A and B as Prolog threads in one process (the CLI may need a `--threads` test mode). For V3b run the same test against `d/with` and against the branch mode.
5. Measure the hypothesis latency (p50/p95 over 50 runs) for the new V3a mechanism; compare with the old 0.1 ms and with V3b's `d/with` (2.7 ms) and branch (103 ms).
6. Optional, only if time remains: a purer variant that passes the state as a value through the evaluator (no dynamic database for hypotheses). Record only effort and size; do not replace F1.2 with it.

## F2 — Structured rule bodies in the LinkML model

1. Extend `linkml/slice.yaml` so heads, bodies and claim assertions are **structured**:
   - classes for the body language as `slice.edn` uses it: `Literal` (predicate + args), `Negation`, `Fetch` (concept + filter map), `Comparison`, `Arithmetic` / `Expr`, `Term` (variable | constant | keyword);
   - discriminated unions via `designates_type` or `any_of` ranges, whichever current LinkML validates correctly; record which works;
   - variable naming constraint (pattern), expression arity, filter-map shape — mirror what Malli checks in `v3b-clojure/src/.../model.clj`.
2. Change `edn2yaml.py` to emit structured YAML for heads/bodies/assertions instead of strings. Keep `edn.pl` as the engine's reader; the LinkML instance is the validated model.
3. **Class rule** "a concept has `sql` or `derived_by`": find out why linkml-validate 1.12.1 did not enforce it (validator plugin, JSON Schema `if/then` generation, `rules` support). Try: current linkml-validate, the generated JSON Schema with `jsonschema` directly, and LinkML's `any_of` on slots instead of `rules`. Record what enforces it.
4. Port V3b's **12 negative tests** to V3a (same malformed records). Pass iff LinkML (or its generated JSON Schema) rejects 12/12. Record error message quality next to Malli's.
5. Regenerate docs (`gen-doc`, instance docs) and DDL; confirm `docs/slice.md` still matches V3b's.
6. Record sizes: schema lines before/after, instance YAML lines.

## F3 — Re-measure and update RESULTS.md

1. Re-run `accept.py` (checks 1–6 plus the new isolation check) and `bench.py` for both spikes on DuckDB and Postgres. Both must stay green.
2. Do not rewrite the existing sections. Add a section **"After the V3a fixes"** with:
   - the rows of the §7 table that changed (adoption gate, model/validation, authoring size, effort, any performance change), old vs new;
   - what SWI transactions/snapshots do and do not guarantee;
   - what LinkML can and cannot express or enforce for rule bodies.
3. Revisit the **Recommendation**. If its two deciding facts no longer hold, say so plainly and state what still separates the two shapes (for example: one notation for structure and rules; immutable values as the idiom; the transaction-time axis; generators). Keep "readability is Matthias's call".

## Decisions

(Executor: append dated entries — what was decided, why.)

**2026-11-24 · F1.1 SWI docs (SWI-Prolog 11.0.0, manual §4.14.1.3 "Transactions", local copy `lib/swipl/doc/Manual/db.html`).**
- `transaction/1` runs the goal as once/1. The goal sees the dynamic database as of the transaction start plus its own changes. Other threads see none of those changes until commit, and the commit is atomic. Failure or an exception discards them. A committed retract of a clause that existed before the transaction makes it globally invisible; retracting the same clause in several transactions is a no-op on the second commit.
- `snapshot/1` is the same, but always discards local changes. The manual calls it the tool for "what if" reasoning.
- They cover only the dynamic database. Static code is shared, and source files loaded inside (for example by autoloading) are globally visible at once.
- Global variables (`nb_setval`) and flags (`flag/3`) are not database and are not rolled back. Global variables are per thread.
- SQL side effects through `py_call` are not rolled back either. They are read-only here.
- Limits: 2^32−1 changes per transaction. Tabling is handled only for local (thread-private) tables, and shared tables should not be combined with transactions (V3a uses no tabling).
- Transactions on their own do not guarantee consistency between concurrent writers: use a mutex or `transaction/3` constraints.
- Decision: use `snapshot/1`. A hypothesis must always be discarded, and "transaction + forced failure" would be the same thing, written less clearly.

**2026-11-24 · F1.2/F1.3 implemented.**
- `with_hypothesis` runs the withholds, the added records and the nested ops inside `snapshot/1`.
- The old assert/retract mechanism is kept behind config `"hypothesis": "assert"`, so the isolation test can show that it fails.
- The memo is now `memo(State, Goal-date, Literal, Result)`. State is a per-thread global variable: `base`, or `hyp(N)` inside a hypothesis. This was needed even with snapshots: memo facts the base asserted before the snapshot are visible inside it.
- `memo_test` (CLI script key `"memo_test": true`):
  - base entries exist (2) but are not used inside the hypothesis, which gives CONFLICT;
  - no `hyp(_)` entries remain afterwards, and the base answer is unchanged;
  - control: the same snapshot under the `base` token reuses the base entry and answers cc0077, which is the leak the key prevents.
- `sql.py`'s per-op cache and log are now thread-local, and statements are serialised on the one connection. V3b's `sql.clj` got the same change (ThreadLocal, `locking`), because both have one shared connection and log.
- Pitfall, again: dict functional notation inside a yall lambda expands outside the lambda. This is the same bug class as session 1. It needed a named helper (`timed_op/2`).

**2026-11-24 · F1.4 isolation test.**
- Written as a separate `shared/isolation.py`, not as check 4b, because it needs a test-only CLI surface. Both CLIs gained:
  - a `sleep` op that returns wall-clock t0/t1;
  - a script key `"concurrent": [[ops], [ops]]`, run as Prolog threads in V3a and as futures in V3b, with each result stamped with t_start/t_end;
  - a script key `"after": [ops]`.
- The test passes iff:
  - A (with_hypothesis withhold R313: sleep 1000 ms, then decide) gives CONFLICT;
  - B (sleep 250 ms, then decide on the base) gives cc0077;
  - B's decide lies inside A's sleep;
  - `after` gives cc0077.
- Results: V3a snapshot PASS, V3a assert **FAIL** (B sees CONFLICT), V3b branch PASS, V3b with PASS.

**2026-11-24 · F1.5 latency** (Q11 withhold, 50 runs, DuckDB, the op's own `ms`):
- V3a snapshot: p50 0.11 / p95 0.12 ms; with the extension added: 0.23 / 0.26 ms.
- The old assert mode measures the same (0.11 / 0.13).
- So isolation costs nothing measurable in V3a. Compare V3b `d/with` 2.7 ms and branch 103 ms.

**2026-11-24 · F1.6 skipped.** Passing the state as a value through the evaluator would mean threading a state argument through `defeasible.pl` and `why.pl` in place of the dynamic predicates. Not attempted, to leave the timebox for F2. A rough estimate, not a measurement: most of the 209 + 63 lines would change, because every `rule/5` and `claim/10` lookup becomes a lookup in an assoc or dict.
