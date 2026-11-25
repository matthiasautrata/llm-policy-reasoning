# Spike v3 addendum — integrity at load time, ambiguity propagation, slice migration

Plan for Claude Code, 2026-11-25 (Matthias). Continue on branch `spike/v3`. Do not push. No API spend. Ask before installing system software. Log deviations under **Decisions** at the end, as before.

## 0 Why

Two decisions taken after `PLAN-v3-cycles.md` reverse its premise and change the semantics:

1. **Defeat cycles are rejected at load time, not answered.** The Warrant-Layer prefers a working engine to academic completeness; cyclic defeat is an exotic corner of day-to-day policy. Integrity rules are checked at load time and on every change to the rule base, hypotheses included. The ledger is the Tolaria note `warrant-layer/integrity-rules.md` (IR-001 … IR-006 below).
2. **Ambiguity propagation replaces ambiguity blocking.** Everything downstream of a contested conclusion is contested. Blocking (SEMANTICS-cycles.md, Y5 decision) returns confident answers across an unresolved conflict (Q35 false, Q37 true); that is the silent incompleteness the Warrant-Layer exists to refuse.

Also, from the same discussion: claims are **flat** with links; claims carry **three time axes**; every measure declares **additivity**.

RESULTS "Defeat cycles" stays as written. Its conclusion ("only WFS or stable-model engines provide the needed semantics") rests on the reversed premise; §6 records that.

Work in three phases, each its own commits, so diffs stay attributable:

| Phase | Changes | Keys |
|---|---|---|
| 1 Migration (§1) | slice shape only | **byte-identical**; any diff is a bug |
| 2 Integrity (§2, §3) | load-time checks, fixtures, re-entry guard | byte-identical for every question still run |
| 3 Propagation (§4) | semantics | changed keys listed and each explained (§4.3) |

## 1 Phase 1 — slice migration (`shared/`)

1. **Flat claims.** Lift every `:subclaims` entry to a top-level claim with its own id. Replace nesting by links on the former parent: `:depends_on [ids]` for `:required`, `:supports [ids]` for `:supporting`. Semantics unchanged: a parent holds only if every `depends_on` member holds; `supports` members never change a status and appear in `why` only. Each lifted claim keeps its own `asserted_by`, `asserted_at`, `valid_from`, `valid_to` (no inheritance from the parent: the V3b inherited-asserter bug must be unrepresentable).
2. **Three time axes.** Every rule and claim gets `:recorded_at` (when the system recorded it; append-only) next to `:asserted_at` (when the asserter said it) and `:valid_from`/`:valid_to` (when it applies). In the slice, `recorded_at` is a fixture value so keys stay reproducible. Add a model check: no rule body may reference `recorded_at`; it is audit and replay only.
3. **Additivity.** Every `:kind :measure` concept declares `:additivity` ∈ `:additive`, `:semi-additive` (with `:unsafe_dims [...]`), `:non-additive`, `:unknown`. No default.
4. **Integer casts.** Every `SUM` cast to `INTEGER` (at least `measure:booked_total`; search for others) becomes `BIGINT`, the A1 fix applied everywhere. Add one regression question per fixed measure that reaches its root, as Q24 does.
5. Update `reference.py`, the V3a LinkML model, V3b's Malli schema and the shared validator to the new shape. The 12 existing negatives still pass; add negatives for: a nested `:subclaims` (now invalid), a measure without `:additivity`, a dangling `depends_on` id.

Gate: regenerate keys; they must be byte-identical to the pre-migration keys. All five spikes still green on 1–6 for the questions in force before `cycles.edn`.

## 2 Phase 2 — integrity checks (`shared/model_check.py`)

One implementation in Python over the slice, as A2 asked. Every check has a named violation, lists the offending ids, and has at least one negative fixture under `shared/fixtures/integrity/` that must be rejected. Checks run:
- at load,
- on every rule or claim change,
- inside `with_hypothesis`, against the hypothetical rule base (a hypothesis that would create a violation is rejected; one that removes a violation is allowed).

| Id | Check | Violation | Notes |
|---|---|---|---|
| IR-001a | No negative dependency cycle through `:not`, defeat (attack edges) or incompatibility | `defeat-cycle`, with members | Exists (`--cycles`); switch to reject. |
| IR-001b | Superiority is a strict partial order. Explicit `:superior-to`, the authority order (R313-style `:pred`/`:order`) and strict-over-non-strict combine lexicographically in that order; `later` by `asserted_at` applies only between claims of the same asserter, and equal `asserted_at` gives no superiority | `superiority-cycle`, with members | New. `model_check.py` currently skips superiority rules. |
| IR-002 | One definition per term: a vocabulary term is defined by exactly one artifact (one concept binding, or rules of class `:definition` under one owner), never both, never two | `duplicate-definition` | New. Define "artifact" precisely in the code's docstring and record it under Decisions. |
| IR-003 | A rebuttal becomes a defeat only through superiority; nothing else orders rivals | `rebuttal-without-preference` | Probably holds by construction in the slice (defeat only via superiority; `:defeater` is an undercut, allowed). Verify, record, and add a fixture that tries a second ordering mechanism. |
| IR-004 | Every measure declares additivity | `missing-additivity` | From phase 1. |
| IR-005 | A rule that uses `:not`, or a fetch of a `:measure`, either references a completeness claim for its scope (`:completeness [claim ids]`) or is marked `:closed_over :known_facts`; in the latter case `decide` sets `qualifier` to `"total over known facts in declared scope"` | `negative-without-completeness` | New. Add one completeness claim to the slice (e.g. the vendor-status register complete for 2026, asserted by procurement) and one question per branch. |
| IR-006 | Bound variables: the variables a caller must bind are declared (`modes.edn`) and every call site binds them | `unbound-call` | Exists; keep as reject. |

Retire the `cycles: report` capability for the accept run: every engine runs `reject`. Keep `--cycles` reporting as a diagnostic.

## 3 Phase 2 — fixtures, tests, re-entry guard

1. **Split `cycles.edn`.**
   - `cycles-acyclic.edn` (loaded in the normal run): Y1 (direct rebut, a dispute), Y4 (rivals ordered by superiority), the Y2 control (acme, Q32) rebuilt without the cycle, and new Y5 variants built on **Y1's dispute** instead of on a cycle: Y5a (supporter depends on the contested literal), Y5c (attacker depends on it), Y5d (`:not` of it), Y5e (a measure over a set containing it).
   - `fixtures/integrity/` (load-rejection tests): Y2 (even loop) and Y3 (odd loop). Expected: load rejected with `defeat-cycle` and exactly the members `model_check.py --cycles` reports today (`RY23`/`RY24`; `RY31`/`RY32` with `CY3`).
   - Y6 becomes two hypothesis tests on the acyclic base: a hypothesis that **adds** the rule closing the loop is rejected with `defeat-cycle`; the base answers unchanged afterwards.
2. **Re-entry guard.** In every memo evaluator (V3a memo, V3b, V3c, V3d), mark a goal in progress on entry; re-entry raises `defeat-cycle` naming the goal path. `cycles_probe.py` (model check bypassed) must now end in that named error in under 1 s on Y2 and Y3, on every engine, instead of a stack overflow or timeout. This is a backstop, not the semantics.
3. Q30–Q39 are renumbered or retired as needed; record the mapping. `accept.py` gains check 8: every fixture under `fixtures/integrity/` is rejected with its named violation.

Gate: keys for every question still run are byte-identical (propagation is not in yet).

## 4 Phase 3 — ambiguity propagation

### 4.1 Semantics (`shared/SEMANTICS.md`, replacing the Y5 part of SEMANTICS-cycles.md)

The rule base is acyclic (IR-001a), so evaluation is three-valued and stratified: each literal is **proven**, **refuted** or **contested**, computed bottom-up or top-down with the same result.

- A body (conjunction) is refuted if any literal in it is refuted, proven if all are proven, otherwise contested.
- `[:not L]` is proven if L is refuted, refuted if L is proven, contested if L is contested.
- A supporter or attacker is **live** if its body is not refuted.
- An attacker is **beaten** if some supporter of the other side that is superior to it has a **proven** body (team defeat). A superior supporter with a contested body does not beat; the conflict stays open.
- L is **proven** if some live supporter has a proven body and every live attacker is beaten.
- L is **refuted** if no supporter is live, or some live attacker with a proven body beats every live supporter.
- Otherwise L is **contested**. This includes: a live supporter and a live unbeaten attacker (the existing "blocked" CONFLICT), and any L whose only live supporters have contested bodies (downstream propagation).
- Comparisons and arithmetic over a contested binding are contested. A measure whose input set contains a contested member is contested. Strict rules propagate the same way.
- Claims: a claim is a rule with an empty body gated by valid time; `depends_on` adds its members to the body.

Mapping to statuses: proven → ANSWER (true or value); refuted → ANSWER false / absent, as today; contested → CONFLICT. `UNDERDETERMINED` is unchanged.

**Sides for downstream CONFLICT:** the sides of the root conflict(s) the goal depends on, found by following contested body literals; if several roots, all of them, in a stable order. The why tree gets a node `{type: "contested", goal, via: [literals], roots: [conflict nodes]}`; `check_why.py` re-verifies `via` and `roots` against the reference.

State which published semantics this matches (Antoniou et al., ambiguity propagating DL, ∂ with support δ) and what is extended (team defeat with authority and `later`, functional rivals, measures). Record confirmed vs assumed, as before.

### 4.2 Implementation

1. `reference.py`: implement §4.1 independently of every spike. Regenerate keys.
2. Port to the engines in this order, one session each: **V3a** (memo mode; WFS mode retired behind a flag, not ported), **V3b**, **V3e** (plain two-valued encoding with explicit status atoms; the doubled encoding retired behind a flag), **V3c**, **V3d**. Not green at the end of its session: stop that engine, record what is missing and an estimate, move on.
3. Each engine: `accept.py` 1–8, `--mutation`, `isolation.py`, `bench.py` on DuckDB and Postgres, negatives.

### 4.3 Key changes

Produce `results/key-diff-propagation.md`: every question whose key changes, old → new, and the reason in one line (which root conflict it now depends on). Expected: Y5a (was ANSWER false under blocking) and Y5c (was ANSWER true) become CONFLICT; any existing question whose derivation passes through the C3/C4 conflicts may change too. An unexplained change is a bug in the reference or the engine, not a finding.

## 5 Rule classes (report only, no change)

The slice's `:class` vocabulary (`definition`, `material_inference`, `exception`, `entitlement`, `incompatibility`, `superiority`) is inferentialist and is not to be replaced by another vocabulary in this addendum. Report, per class: the rules using it, and for `entitlement` whether each rule is a policy permission ("may approve") or an entitlement in the inferential sense. This feeds a later decision on how deontic rules enter as their own kind. Put the report in RESULTS §6 and a question in PROGRESS.

## 6 RESULTS.md

Do not rewrite earlier sections. Add **"Integrity at load time and ambiguity propagation"**:
- a note at the top that "Defeat cycles" answered a question since reversed (cycles are rejected, not answered), and what remains valid from it (the memo crash analysis, the cycle detection, the unsat-core observation);
- the integrity checks: one row per IR with fixture, violation and result per engine;
- re-entry guard results from `cycles_probe.py`;
- propagation: the key diff summary, per-engine effort (lines changed, session count), latency before/after;
- the §5 class report;
- lesson 1 revisited again: with an acyclic rule base, which engines are native for the three-valued propagation and which needed it built;
- the platform revisit in the A3 order (semantics, guarantees, operation, footprint), noting that semantics may no longer separate the platforms.

## Decisions

(Executor: append dated entries — what was decided, why.)
