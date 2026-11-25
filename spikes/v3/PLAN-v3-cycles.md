# Spike v3 addendum — defeat cycles: V3a with tabling/WFS, and V3e (Clingo)

Plan for Claude Code, 2026-11-25 (Matthias). Continue on branch `spike/v3`. Do not push. No API spend. Log deviations under **Decisions** at the end, as before. Timebox: shared + V3a one session, V3e one to two sessions.

## 0 Why

All four spikes (V3a–V3d) run an own defeasible evaluator, and the slice contains **no negative cycles**. RESULTS "V3c and V3d" concludes that the defeasible layer is native on no platform, because team defeat over derived conclusions is a negative cycle and every Datalog engine tried stops at stratified negation. Two engines were not tried for this:

- **SWI-Prolog with tabling and well-founded semantics** (`tnot/1`): a mutual defeat becomes *undefined*, which under ambiguity blocking is CONFLICT.
- **Clingo** (answer set semantics): negation through cycles is native; cautious consequence gives what holds in all answer sets; `#external` / solve assumptions give hypotheses natively.

This addendum adds cycle questions to the slice and tests both. It can change the main finding.

## 1 Shared (`spikes/v3/shared/`) — first

### 1.1 Slice extension: `cycles.edn`

Loaded on top of `slice.edn` (like `extension.edn`). Plant, each with its own question in `questions.edn` (ids Q30+):

| Id | Pattern | Expected |
|---|---|---|
| Y1 | Two claims rebut each other directly, no superiority (two asserters of equal authority on one vendor's status) | CONFLICT, sides = both claims |
| Y2 | Team defeat over **derived** conclusions: conclusion P is attacked by defeasible conclusion Q, and Q is attacked by a rule whose body depends on P | CONFLICT, sides from the cycle |
| Y3 | Odd loop: a claim indirectly defeats itself (through one intermediate) | CONFLICT (undefined), sides from the loop |
| Y4 | A cycle that superiority breaks (same as Y1 plus `superior`) | ANSWER, the superior side |
| Y5 | A conclusion that *depends on* an undefined one (downstream of Y1) | under ambiguity blocking: per §1.2 — decide and key it |
| Y6 | A cycle under a hypothesis: withholding one rule of Y2 breaks the cycle | inside `with_hypothesis`: ANSWER; base unchanged |

### 1.2 Semantics: specify before keying

Write `shared/SEMANTICS-cycles.md` (one page): the target is **well-founded defeasible semantics with ambiguity blocking**, mapped to statuses as true → ANSWER, false → not derived (ANSWER false / absent), undefined → CONFLICT with sides = the members of the undefined component that bear on the goal. State explicitly:
- what Y5 returns (blocking: the downstream conclusion is not derived, so its own rule fails, giving ANSWER false — or does undefinedness propagate? Ambiguity *blocking* vs *propagating* differ exactly here). Choose blocking unless the literature check below shows our existing semantics already behave otherwise; record the choice;
- check against the literature that the chosen WFS mapping matches ambiguity-blocking defeasible logic (Maher, Governatori and colleagues on defeasible logic vs Kunen / well-founded semantics of translated programs). Record what was confirmed and what was only assumed.

### 1.3 Reference and keys

Extend `reference.py` with an independent implementation of §1.2 (alternating fixpoint over the ground defeat graph is enough at this size). Regenerate `keys.json` for Q30+. Mutation test still fails as required. Existing keys must not change.

### 1.4 Model check

Add to the shared checks a **cycle report** over the rule base: list every negative cycle (through `not`, defeat, incompatibility) with its members. With WFS / ASP a cycle is allowed, so this reports, it does not reject. Also add the **moded safety** check from RESULTS lesson 3: for each rule, the variables a caller must bind (R202, R304 style) are declared, and every call site binds them. Implement once in Python over `slice.edn` (+ `cycles.edn`).

## 2 V3a — tabling and WFS (`spikes/v3/v3a-prolog/`)

1. Replace the per-op memo (`memo/4`) with SWI tabling on the defeasible predicates; use `tnot/1` for defeat and incompatibility checks. Keep the memo version behind a config switch as a control.
2. Read three-valued results: true, false, undefined. For undefined, get the residual program (`call_delays/2` or the documented equivalent in SWI 11) and derive the CONFLICT sides and a `why` node for the cycle (new node kind `undefined` with the cycle members; extend `check_why.py` to re-verify it against the reference's undefined component).
3. **Interactions to resolve and record:**
   - tabling inside `snapshot/1`: per the SWI docs, transactions handle only thread-local tables. Use thread-local tables, or abolish the relevant tables inside the snapshot; `isolation.py` must still pass;
   - tabling vs fetched data and `as_of`: tabled answers must not leak across dates or hypotheses. Use incremental tabling over the dynamic facts, or key tables by state/date; show with a test that Q-as-of questions still pass after a hypothesis;
   - tabled goals calling `py_call` (fetch): record whether results are reused correctly within an op and invalidated across ops.
4. Re-run `accept.py` (1–6 + Q30+), `--mutation`, `isolation.py`, `bench.py` on both backends. Record the latency cost of tabling versus the memo.

## 3 V3e — Clingo (`spikes/v3/v3e-clingo/`)

### 3.1 Stack

- clingo Python package (record version), Python host reusing V3a's `sql.py` boundary (or a copy), same CLI contract and JSON.
- Rules from `slice.edn` (+ `cycles.edn`) translated **at load time** into ASP text by a translator in the host (this is a load step like `consult`, not code generation into the source tree; rule changes at runtime = re-translate and re-ground the affected program part, no restart).

### 3.2 Design

- **Fetch:** top-down demand in the host. For a question, determine the concepts and bindings the goal needs (from rule bodies and the moded-safety declarations), fetch them through `fetch` with bounded SQL, and add them as facts. Then ground a small program for that question. Record how the demand analysis is done and whether check 5 (bounded fetch) holds. Script functions during grounding (`@fetch(...)`) may be probed, but they do not give top-down demand by themselves.
- **Defeasible encoding:** strict, defeasible, defeaters, superiority, ambiguity blocking, incompatibility (R314), claims and sub-claims (required/supporting) in ASP. Answer statuses from **cautious consequences** (and brave, for sides). Verify the encoding against §1.2 on Y1–Y6; record any divergence between ASP stable-model semantics and the WFS keys (odd loops Y3 have no stable model in naive encodings — handle and record how).
- **Hypotheses:** `#external` atoms for withheld rules and claims, and `solve(assumptions=…)`, in a multi-shot control object. `isolation.py` must pass (separate control objects per concurrent op, or a lock — record which and why). Measure hypothesis latency as before.
- **Explanations:** `why` / `why_not` in the common tree shape. Try existing tooling first (xclingo, clingo-explaid or current equivalents; record versions and what they give), else track justifications in the encoding (rule-applied atoms) and build the tree in the host. Trees must pass `check_why.py`.
- **As-of / provenance:** valid time and assertion attributes as facts, as in the other spikes.

### 3.3 Checks

`accept.py` (1–6 + Q30+), `--mutation`, `isolation.py`, `bench.py` on DuckDB and Postgres, 12 negatives (model validation: reuse V3a's LinkML model or the shared Python validator; record which).

## 4 Other spikes

Run V3b, V3c, V3d against Q30+ unchanged and **record** the outcome (they are expected to fail or loop on cycles). Do not fix them in this addendum; note what each would need (e.g. an alternating-fixpoint pass) and an estimate.

## 5 RESULTS.md

Do not rewrite earlier sections. Add **"Defeat cycles: V3a with WFS, V3e Clingo"**:
- Y1–Y6 outcomes for all five spikes (table);
- whether the defeasible core is native in V3a-WFS and V3e, and what still had to be built (explanations, fetch demand, sides);
- the semantics confirmed vs assumed (§1.2), and any divergence between WFS and answer-set results;
- §7 rows for V3e plus V3a-WFS (correctness, effort, explanations, hypotheses, latency, bounded fetch);
- a revisit of lesson 1 in "V3c and V3d" ("the defeasible layer is not native Datalog on any platform") and of the recommendation.

## Amendments 2026-11-25 (Matthias's answers to PROGRESS questions 6–8)

These bind the executor like the sections they amend.

**A1 (§1, from Q6): fix `pending_exposure` as part of the shared work.** It is a real bug in the shared slice: an INT32 cast on DuckDB's INT128 sum. Top-down evaluation never asks for the root, so no question hit it; Flix's bottom-up path found it.
- Fix it in the concept → SQL binding (`measure:pending_exposure` in `slice.edn`), not in the rules. Cast to `BIGINT` or `DECIMAL`.
- Check both backends: Postgres sums integers to `BIGINT`, DuckDB to `INT128`.
- Regenerate the keys. Existing keys must not change; that unchanged diff is itself the evidence that the bug was unreachable top-down.
- Add one regression question that does reach the root, so the bug cannot silently return.

**A2 (§1.4, from Q7): one shared model check, with strictness set by the engine.** Stratification and bound variables are properties of the rule base, not of a platform. Implement them once in Python over `slice.edn` (+ `cycles.edn`), not per spike.
- Each engine declares a capability flag `cycles: reject | report`, which the shared check reads.
  - `report`: V3a with WFS and V3e with answer sets. Cycles are allowed and listed with their members.
  - `reject`: the V3b–V3d evaluators and V3a's memo mode. A rule base with a negative cycle is rejected.
- The bound-variable check applies to every engine. It covers which variables a caller must bind (R202, R304 style) and whether every call site binds them.

**A3 (§5, from Q8): the revisit is not "pick by secondary property".** That frame presumes the core is equal, and this addendum may change that: if WFS tabling or Clingo makes defeat native, the platforms differ in their primary property.
- After the cycles results, order the revisit by how much each property bears on the warrant:
  1. Semantics: is the defeasible core native or built?
  2. Guarantees: the kind of isolation, which static checks, how complete the explanations are.
  3. Operation: resilience and concurrency, the audit time axis.
  4. Footprint: information only.
- Phrase it as "what each platform makes natural, and what it taught us", not as a choice. Choosing happens later, for v3's T arm.

## Decisions

(Executor: append dated entries — what was decided, why.)

**2026-11-25 — §1 shared**
- *A1:* `measure:pending_exposure` is cast to `BIGINT` in `slice.edn`. Q24 is the regression and asks for the root, `cc0000`. After the keys were regenerated, every existing key is byte-identical. That confirms the bug was unreachable top-down.
- *LinkML docs (`v3a-prolog/linkml/docs/`) were not regenerated for `cycles.edn`.* The cycles extension adds no new record shapes, and V3e calls `build.negatives` directly, so `build.main()`, which rewrites the docs, was not run.
- *Model check modes are a greatest fixpoint* (`model_check.py` `infer`). A least fixpoint cannot type mutually recursive predicates: every pattern of a defeat cycle would stay unsafe. Starting from "all safe" and removing unsafe patterns accepts a cycle whose calls are all bound.
- *Check 7 by capability:*
  - `report` engines must answer Q30–Q39 against the WFS keys;
  - `reject` engines pass check 7 when the model check rejects the cyclic rule base;
  - what the engine itself does on cycles is measured separately by `cycles_probe.py`, which bypasses the model check.
- *Y5 choices (SEMANTICS-cycles.md):* a literal downstream of a blocked conclusion is false (Q35); one downstream of an undefined conclusion is undefined and reports the cycle's sides (Q36); an attacker whose body is blocked does not attack (Q37). These follow from the metaprogram's WFS and were not chosen separately.
- *RY-rule owners:* the defeaters in the cycles are owned by `compliance`, so the owner checks see a real owner and the existing owner enum stays closed.

**2026-11-25 — §2 V3a WFS**
- *Truth values come from a tabled metaprogram* (`wdef/3`, `wovr/3`, `wbeat/4` with `tnot/1`). The existing classify, sides and why code works over those values. Undefined literals are read with `call_delays/2`. The memo engine is kept as `ENGINE_MODE=memo` (control).
- *Tables are keyed by a state token (`base`, `hyp(N)`) and the as_of date, and are abolished on every rule/claim change and, under the default policy `op`, at the start of every op.* `results/table-test.json` is the control: it shows the leak the key prevents. Isolation passes on both backends. No thread-local tables were needed: the token keeps hypotheses apart, and each op starts clean.
- *Fetch from tabled goals:* `py_call` results are cached per op in `sql.py`, not in the tables. Within an op they are reused through the per-op cache. Across ops the cache is reset, so nothing is reused stale.
- *Cost:* DuckDB decide p50 4.4 → 4.9 ms, p95 9.2 → 9.4 ms; Postgres p50 10.3 → 10.0 ms (noise). SQL per decide is unchanged (11.2).

**2026-11-25 — §3 V3e Clingo**
- *clingo 5.8.0, not 5.8.3.* Installing xclingo 2.0b24 downgraded clingo, because it pins `clingo==5.8`. Every V3e result is on 5.8.0. Other versions: clingexplaid 1.5.1, edn_format 0.8.0, Python 3.14.
- *WFS from answer sets by the Tr_p doubling (Janhunen, Niemelä, Seipel, Simons, You, TOCL 2006).* The defeasible layer is written twice: as `t_*` (true) and `p_*` (possible).
  - Each `not` in a `t_*` rule reads `p_*`, and each `not` in a `p_*` rule reads `t_*`.
  - The well-founded model is the knowledge-least partial stable model, so cautious consequences of `t_*` are the WFS-true atoms and brave consequences of `p_*` are the WFS-non-false atoms.
  - Two solves run on one Control, with `enum_mode` cautious and then brave.
  - This handles Y3 (the odd loop): the plain encoding has no stable model there (`probes.py`: Y3 0 models, Y2 2 models, Y1 1), but the doubled program always has partial stable models.
  - No WFS/ASP divergence remains on Y1–Y6: all ten Q30–Q39 match the WFS keys.
- *`#external active(Id). [free]`, all assumed in every solve.* Externals default to false, and without `[free]` the first solve was UNSAT. Each solve passes `active(Id)` as true for visible ids and false for withheld ones.
- *32-bit integers:* clingo integers are 32-bit. The host raises a named error for an out-of-range value instead of letting it wrap. No slice value is out of range.
- *One Control per op, no lock.* Re-grounding is needed for each op anyway (the next point). A Control is not shared between threads, so concurrent hypotheses need no lock and `isolation.py` passes. This departs from §3.2, which asks for one multi-shot Control. Hypotheses still use `#external` plus assumptions as §3.2 asks, but within the op's own Control.
- *Per-op grounding, not incremental.* In multi-shot clingo, rules already grounded in `base` are not re-grounded for new demand atoms added in later program parts. Per-op demand therefore needs a fresh ground, about 5 ms here: 85% of a decide is grounding and 0.4–0.5 ms is the two solves.
- *Demand as a magic-set rewrite in the translation, fetch during grounding.*
  - The translator emits, per rule, demand propagation `dm(P, BoundArgs)` → `need(Concept, Filters)` for its body, keyed by the bound positions in `shared/modes.edn` (the positions bound in every declared mode).
  - `frow(C,F,R) :- need(C,F), R = @fetch(C,F)` calls V3a's `sql.fetch` during grounding.
  - §3.2 says `@fetch` alone does not give demand; the dm/need rewrite does, and `@fetch` is only the boundary.
  - Check 5 holds (Q17: 551 statements, 1006 rows, max 425). The demand is broader than SLG's: 21.9 SQL statements per decide vs V3a's 11.2, because the rewrite demands every body of every rule whose head is demanded, attackers included, without SLG's left-to-right early failure.
- *The trees come from the host.*
  - xclingo 2.0b24 fails on its own README example under clingo 5.8.0 / Python 3.14: the explainer program it generates does not parse.
  - clingexplaid 1.5.1 explains unsatisfiability (MUS, MSS, MCS over assumptions), not derivations. Over `active/1` assumptions on the plain encoding it returns exactly the odd loop for Y3 (`{CY3, RY31, RY32}`, 0.2 ms), the same set as V3a's `undefined.members`. It is recorded as a probe and not used in the tree.
  - `host.py` builds why/why_not from the three truth values and the ground skeleton (`h/3`, `ih/2`). It is a port of V3a's wfs-mode classify/sides/explain_not, and all trees pass `check_why.py`.
- *Negatives by V3a's LinkML model:* `negatives.py` calls `v3a-prolog/linkml/build.py` `negatives(S, X)`, and 12/12 are rejected by both linkml-validate and the generated JSON Schema. This was chosen over the shared Python validator because it is the one model that already sees rule bodies, and V3e adds no record shapes.
- *`hyp_latency.py` (shared) was added,* so both report engines' hypothesis latency is measured through the same CLI path.

**2026-11-25 — §4 other spikes**
- V3b, V3c and V3d were run unchanged: `cycles_probe.py` plus check 7. No fixes, as §4 says. Outcomes and estimates are in RESULTS "Defeat cycles".
- Each scores 5/10. All three fail on Q31, Q32, Q33, Q36 and Q39, the questions whose evaluation enters a real cycle:
  - V3b: StackOverflowError at `engine/rename`;
  - V3c: 60 s timeout;
  - V3d: 60 s timeout, under `-Xss512m`.
- Check 7 passes on all three by `reject`.
- Probe timeout of 60 s per question, DuckDB only: all three fail in the evaluator before any backend-specific step, so Postgres would add nothing. Logs are in `results/cycles-probe.txt` and `results/cycles-probe-duckdb.json` in each spike.
