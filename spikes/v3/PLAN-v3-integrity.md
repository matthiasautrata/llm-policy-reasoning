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

**2026-11-25 — Phase 1 done (slice migration).** Keys regenerated: identical to the pre-migration keys except the new Q25 in `base` and `extended` (§1.4 asks for it, so the gate reads "identical plus the regression questions"). All five spikes GREEN 1–7 (V3a in both `wfs` and `memo` modes); negatives 15/15 in every spike.

- **Supports and the qualifier (§1.1).** The plan says `supports` members "never change a status". The pre-migration engines give a parent with a failing supporting sub-claim `holds_with_qualifier` (CONTRACT.md), and keys Q07/Q14 depend on it. Kept that: a failing `supports` member adds a qualifier and never rebuts. "Never change a status" is read as "never rebut". Changing it would break the byte-identical gate.
- **Output contract unchanged.** The `claims` op still returns nested `subclaims` with `role` `"required"` / `"supporting"`, built from the links: `depends_on` first, then `supports`, in list order. Only storage is flat. The top-level list (and `describe`) holds the claims that no *active* claim links to. One consequence: withholding a parent (hypothesis) now lists its members at top level, where before they vanished with it. No question exercises this. Documented in CONTRACT.md.
- **Asserter inheritance gone.** Each lifted claim carries its own `asserted_by`/`asserted_at`/`valid_*` (copied from the old sub-claim, not the parent). In V3b each claim is now its own transaction, so the inherited-asserter bug cannot occur. V3b's `probe.clj` queries still use `:claim/parent` and are stale; they are left as a record of the old probe and are not run by accept.
- **`recorded_at` fixtures (§1.2).** `2026-09-14` on every rule and claim in `slice.edn`, `2026-09-15` in `extension.edn` and `cycles.edn`. Required on rules and claims in every model (LinkML, Malli, the V3c validator, V3d's closed maps). The "no rule body mentions `recorded_at`" check lives in the shared `model_check.shape_errors`, which every spike's accept run goes through.
- **Additivity choices (§1.3).** `measure:booked_total` and `measure:pending_exposure` are `:semi-additive` with `:unsafe_dims [:cost_centre]`: they sum over a cost-centre hierarchy, so adding parent and child double-counts. `measure:headroom` is `:non-additive` (a difference against a limit). In LinkML the requirement is a Concept rule (precondition `kind == measure`), because the `concepts` range admits plain Concept.
- **Integer casts (§1.4).** The only `SUM … AS INTEGER` was in `measure:booked_total`; it is now `BIGINT`. Its root value, 153,646,000, fits in INT32, so no key value changed. Q25 (root booked total) was added anyway, as the plan asks. A `COUNT` cast to INTEGER was left alone: a count cannot reach 2^31 on this slice and is not a SUM.
- **Negatives (§1.5).** Old #9 ("sub-claim role not required/supporting") cannot be stated in the flat shape, so it is re-expressed as "`depends_on` member not a claim id" (`[:R101]`). New: #13 nested `:subclaims`, #14 measure without `:additivity`, #15 dangling `depends_on` id (`:C9.9`). #10's added superiority rule now carries `recorded_at`, so it is still rejected for the unknown owner alone. LinkML 1.12.1 has no reference-integrity check, so #15 passes `linkml-validate` and the JSON Schema and is caught only by the shared check. `negatives.md` has a new "shared check" column: LinkML 14/15, JSON Schema 14/15, shared 4/15, rejected by at least one layer 15/15. The Malli (V3b), V3c and V3d validators reject all 15 by themselves, each with its own link-resolve check.

**2026-11-25 — Phase 2 done (integrity checks, fixtures, re-entry guard).** All five spikes GREEN on checks 1–8 (V3a in both `wfs` and `memo` modes). Negatives are still 15/15 in every spike. The guard probe gives `defeat-cycle` on Y2 and Y3 in every memo evaluator, with each op under 35 ms: V3a memo 2/2, V3b 2/2, V3c 2/2, V3d 2/2. Keys for every question still run are identical to the phase-1 keys. The only additions are new questions (below).

- **One gate, five callers.** The checks live in `shared/model_check.py`. `shared/integrity.py` builds the rule base an engine would hold (the first load path plus further load paths plus added EDN texts, minus withheld ids) and runs them over it. V3a and V3e import it. V3b (`gate.clj`, `clojure.java.shell`), V3c (`gate.ex`, `System.cmd` with a temp-file stdin) and V3d (`Gate.flix`, `ProcessBuilder` with temp-file redirects) run it as a subprocess. A check takes about 13 ms; a call takes about 60 ms with Python start-up. A hypothesis that removes a violation is admitted, because the check sees only the hypothetical rule base.
- **The gate runs before each engine's own schema validation.** That way a fixture is rejected for its integrity violation and not for some engine-specific schema error, and the rejection is identical across engines.
- **Rejection format.** A rejected load gives `{"error": {"op": "load", "violations": [...]}, "results": []}`. A rejected `add` or `with_hypothesis` gives that op's result as `{"error": {"op", "violations"}}`, and the state is unchanged. Violations are `{violation, members, message}`. For `defeat-cycle` the members are **rule ids**, the ones `model_check --cycles` reported (`RY23`/`RY24`; `RY31`/`RY32`). The guard's members are different: they are goals, because at run time the evaluator knows goals, not the static rules. See CONTRACT.md.
- **`INTEGRITY_GATE=off`** admits everything. Only `cycles_probe.py` sets it, to reach the re-entry guard.
- **IR-001b combination.** Explicit `:superior-to` comes first, then the authority order (`{:pred :order}`), then strict over non-strict, then `later`. `later` applies only between claims of one asserter, and equal `asserted_at` gives nothing. The first criterion that orders a pair in either direction decides it. The relation is built over rivals (records concluding the same predicate) plus explicit edges. Any strongly connected component or self-loop is a `superiority-cycle`. The asserter order is also checked per predicate: two superiority rules for one predicate must not rank two asserters both ways. The authority fixture reports R313 plus RS3 plus the claims in the cycle, so its manifest entry checks inclusion, not exact members.
- **IR-002 artifact.** A predicate `p` (term `term:p`) is defined by artifacts. The *binding artifact* is the concept named `p`, together with its `:derived-by` rule and any `:definition` rule of the term's owner whose body is a single fetch of that concept; such a rule only exposes the binding as a predicate (R104 for `booked_total`). There is one *rule artifact* per owner: the remaining `:class :definition` rules with head `p`. Two or more artifacts is a `duplicate-definition`. The slice passes. The fixture adds a second-owner definition of `booked_total` (RD1).
- **IR-003 holds by construction.** No slice record orders rivals other than through superiority, and `:defeater` is an undercut, which is allowed. The check rejects any record that carries an ordering key (`priority`, `weight`, `rank`, `salience`, `overrides`, `precedence`, `preference`, `order_by`). The fixture adds `:priority` (RP1).
- **IR-004 is derived at test time.** `accept.py` copies the slice with `:additivity` removed from `measure:booked_total` into a tempdir. No second slice is committed.
- **IR-005.** The completeness claim is C10, finance asserting `[:complete "booked_total"]`. R104 (a fetch of a measure) names `:completeness [:C10]`. R304 and R310 (`:not`) are `:closed_over :known_facts`. Completeness is checked only for existence: each named id must be an active claim on predicate `complete`. Scope matching (the claim's period against the query's as-of) is not checked; that would need a scope language the slice does not have. **Qualifier rule:** `decide` returns `"total over known facts in declared scope"` when the status is ANSWER, the value is not false, null or `[]`, and the why tree uses a `:closed_over` rule. Otherwise it returns null. A negative answer from NAF carries no qualifier, because there is no positive totality claim to qualify. New questions: Q26 (`booked_total cc0009`, the completeness branch, qualifier null) and Q27 (`approved r000005`, through R304/R310, qualifier set). Both have `:check_qualifier true`, and only such questions compare the field, so older keys are unchanged.
- **The cycles split.** `cycles-acyclic.edn` is loaded only in check 7, not in checks 1–6, so the base keys and the bench stay as they were. Y2 and Y3 move to `fixtures/integrity/`. The question mapping:
  - Q30, Q32, Q34, Q35 and Q37 are kept on the acyclic state, and their keys are equal to the old cycles keys.
  - Q31 (Y2 dyne) and Q33 (Y3) become the load-rejection fixtures.
  - Q36 (Y5b, a supporter depending on a *cycle* literal) is retired: on Y1's dispute it would be the same as Q35.
  - Q38 and Q39 (Y6) become check 7's hypothesis tests. Adding RY24, and adding the Y3 file as a hypothesis, are each rejected with exact members. The probe [Q32, Q43] answers the same before and after, and matches the keys.
  - New: Q40 (Y5d, `[:not]` of the contested literal, true, qualifier set), Q41 and Q42 (Y5e), and Q43 (Y2 rebuilt without the loop, CONFLICT [[RY21],[RY23]]).
- **Y5e approximated.** "A measure over a set containing the contested literal" is not expressible: the rule language aggregates table rows through concept bindings, not sets of derived literals. RY56 fetches the measure over a binding that is itself contested: `home_budget e077` reads `booked_total` of e077's cost centre, and on 15 July `cost_centre_of e077` is the Q04 dispute. Q42 (R313 active) gives ANSWER [699000]. Q41 (R313 withheld) gives ANSWER [] with an empty why, because the body never binds under pre-propagation semantics. That changes in phase 3.
- **An empty value has no why tree.** `accept.py` no longer requires a why tree when the key value is `[]` (Q41).
- **Capabilities.** Every `capabilities.json` is `reject` (V3a in both modes, V3e). `model_check.py --cycles` (now over cycles-acyclic) and `--fixture` remain as diagnostics, with the default flag `report`.
- **The re-entry guard applies only to the memo evaluators.** V3a memo uses `nb_setval` for the path and V3b/V3c/V3d carry a `path` in the evaluation context. The guard throws a tagged error, and the op handler turns it into the violation format. V3a wfs and V3e answer the loops natively when the gate is bypassed. Both give CONFLICT on both loops: Y2 [[RY21],[RY23]], Y3 [[CY3],[RY32]] (`results/guard-probe*.txt`). They therefore have no guard, and the "end in a named error" criterion is read as applying to the memo evaluators, as §3.2 lists them.
- **Results files.** `results/accept*.txt` and `results/guard-probe*` are new or refreshed. The `cycles-probe*` files are the PLAN-v3-cycles runs, which RESULTS cites, and are left as they were. `cycles_probe.py` now runs the guard probe.

**2026-11-25 — Phase 3 done (ambiguity propagation, §4).** `reference.py` implements `shared/SEMANTICS.md` and the keys are regenerated. Q01–Q27 are byte-identical. Q35, Q37, Q40 and Q41 change from ANSWER to CONFLICT; Q30, Q32, Q34, Q42 and Q43 keep their keys (`results/key-diff-propagation.md`). All five engines were ported in the plan order (V3a memo, V3b, V3e plain, V3c, V3d), each in one session, and each is GREEN on checks 1–8 under propagation, plus `--mutation` OK, `isolation.py` PASS on DuckDB and Postgres, and negatives 15/15. No engine had to be stopped.

- **`results/` at the spike root.** §4.3 names `results/key-diff-propagation.md` and no directory. It is put in `spikes/v3/results/`, beside the plan, because it describes the shared keys and no single engine.
- **Root vs downstream.** A contested literal is a *root* when a proven-bodied supporter meets a proven-bodied unbeaten attacker; that is the old "blocked" case, and it keeps its CONFLICT shape: the side proofs as `why`, sides from its own members. Every other contested literal is *downstream*. Its CONFLICT `why` holds one `contested` node per contested ground instance, and its sides are the deduplicated, sorted union of the sides of every root reached through contested body literals. An open goal with any contested candidate instance is CONFLICT as a whole. The plan's node `{type, goal, via, roots}` gains a `rules` field: the ids of the live supporters and unbeaten attackers along the way. Without it `check_why.py` cannot tie the node to rules, and the core-id check would fail. CONTRACT.md has the node.
- **Team-form refutation.** §4.1 says "some live attacker with a proven body beats every live supporter". The reference and every engine use DL's −σ team form: *every* live supporter is beaten by *some* superior attacker with a proven body. The defeater reported is the smallest such id. This is a strict superset of the plan's reading. No key changes, because no literal of the slice has two live supporters facing different superior attackers.
- **Claims.** A claim whose own assertion is downstream-contested has standing `contested`, with sides from the root(s). A `depends_on` member that is contested makes the parent `contested` (with `via` the member); before, it made it `rebutted`. A contested `supports` member still only qualifies.
- **`[:not L]` inside a body.** When L is contested, the literal is contested and the body solution keeps a placeholder `{type: "contested_lit", goal}` in place of a proof. why-not shows the same placeholder.
- **Blocking kept behind flags, not deleted.** `reference.py --semantics blocking` and `accept.py --semantics blocking` reproduce the phase-2 keys for check 7. V3a's default mode is now `memo` (propagation); `wfs` is the retired blocking mode (`results/accept-wfs-blocking.txt`, GREEN against the blocking keys). V3e's default is `V3E_ENCODING=plain`, one two-valued model with explicit status atoms; `doubled` is the retired blocking encoding (`results/accept-doubled-blocking.txt`, GREEN). `probes.py` pins `doubled`, since its rewrites act on that text.
- **V3e plain on cycles.** The plain encoding raises an EngineError when a solve does not give exactly one model. On the gate-bypassed Y2 and Y3 loops it *does* give exactly one model, and that model answers CONFLICT with sides null (`results/guard-probe-plain.*`, "guarded 0 of 2"). So the plain encoding answers loops instead of naming them, and the sides are empty. With the gate on, loops never reach it. The phase-2 guard files (doubled) stay as they were.
- **Guard probe refreshed.** In V3b, V3c and V3d `results/guard-probe.txt` / `guard-probe-duckdb.json` were overwritten by the propagation run. They still say guarded 2 of 2; each op takes under 50 ms (V3b 48 ms on Y2 is the slowest). Only the timings differ from phase 2. V3a memo's `guard-probe-memo.*` is refreshed the same way.
- **Latency.** Before = ef6ec40, built in a detached worktree; after = this commit. The table is `bench.py`, decide_ms p50 / p95. SQL per decide is unchanged in every engine (V3a–V3d 11.17, V3e 21.86), because propagation adds no fetches. The before/after differences (−4 % to +10 % on p50) are of the size these benches drift between runs. No systematic cost of propagation is visible on the slice; it adds no queries, and the slice has almost no contested literals to follow.

  | engine | DuckDB before | DuckDB after | Postgres before | Postgres after |
  |---|---|---|---|---|
  | V3a memo | 4.34 / 9.38 | 4.58 / 10.18 | 7.72 / 21.94 | 8.59 / 23.37 |
  | V3b | 6.19 / 13.37 | 6.11 / 13.97 | ≈4.70 (median) | ≈5.42 (median) |
  | V3c | 5.97 / 13.21 | 5.78 / 13.41 | 11.63 / 31.32 | 12.81 / 31.81 |
  | V3d | 6.89 / 14.64 | 6.89 / 15.06 | 4.86 / 12.96 | 5.10 / 14.25 |
  | V3e plain | 15.59 / 17.13 | 15.96 / 18.77 | 14.01 / 16.29 | 13.72 / 16.13 |

- **Effort (code lines, `git diff --numstat`, added / removed).** shared: `reference.py` +192/−8, `check_why.py` +45/−3, `accept.py` +12/−2. V3a: `defeasible.pl` +138/−14, `ops.pl` +31/−4, `host.py` +2/−2. V3b: `engine.clj` +101/−8, `ops.clj` +41/−10. V3c: `engine.ex` +138/−7, `ops.ex` +66/−10, `why.ex` +5/−2; the blocking-era `supporters`/`attackers`/`classify` were left in place, unused. V3d: `Engine.flix` +145/−34, `Ops.flix` +43/−9; the old functions were removed, because `Sup` gained fields. V3e: `asp.py` +60/−4, `host.py` +126/−7, `probes.py` +1. In every engine the new evaluator is a three-valued twin of `lit`/`body`/`apply_rule` plus a team-defeat `classify`, and the ops gain a BFS (`contested_why`) for the why node. V3d compiled and went green on its second build; the only error was a tuple pattern in a lambda.
- **Baseline worktree.** The "before" benches ran from a `git worktree` at ef6ec40 in the scratchpad. The untracked build inputs were linked or copied in: `.venv` and `shared/slice.duckdb` as symlinks, V3c's `_build`/`deps`, and V3d's `lib/`. The worktree is removed after this commit.
