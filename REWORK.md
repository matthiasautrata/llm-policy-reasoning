# REWORK — llm-policy-reasoning v2

Plan and instructions for the v2 rewrite. Written 2026-11-22 from a design session; executor: Claude Code in this repo. Deviate where the code shows a better way, but log each deviation with its reason in the "Decisions" section at the end.

## 1 Aim

v1 (`PAPER.md`, "Rules in Context") asked whether *notation* matters and when an *engine* is needed. It found that written decisions matter, not notation, and that the engine earns its place at scale. It left one thing unmeasured: translation from question to formal query, where interpretation enters (v1 §7, "Construct").

v2 asks: **which layer of meaning does a question need, and in which representation and mode does a model use it reliably?** It is the experimental arm of the warrant-layer project (notes: `warrant-layer/question-compilation.md`).

## 2 Design: layers × representations × modes

### 2.1 Layers (cumulative)

| Layer | Adds | Unlocks | Typical failure without it |
| --- | --- | --- | --- |
| L0 schema | tables, columns, types, keys, foreign keys | structure questions, plain joins | join-path forks, guessed column meaning |
| L1 ontology | concepts, contrastive definitions, concept → column bindings, conservative definitions | "what does X mean", term-grounded facts | silent coercion, synonym drift |
| L2 context | asserted claims with scope and provenance: as-of, source, rule versions, status, disagreement | "according to whom", "as of when", "is it disputed" | answering from a stale or contested claim |
| L3 warrant | owned rules that are non-conservative, defeasible or deontic: approval, exceptions, denial, precedence | "may I", "is it approved", "why" | fluent answer without justification |

**Boundary L1/L2 vs L3** (the criterion under test, not an axiom):
- Classification, joining, filtering and eliminable definitions are *conservative*: they rearrange what is asserted. They live in L0–L2 and need no inferential warrant; their warrant is *testimonial* (provenance), carried in L2.
- A rule is L3 if it is non-conservative (licenses conclusions not contained in the facts), defeasible (has exceptions), or deontic (may / must / must not). Its warrant is *inferential*: the derivation.
- Ownership is orthogonal: a contested definition ("active = traded within 90 days"; v1's C1 "committed spend") is conservative but owned. Test: if two SMEs could reasonably disagree, the rule carries an owner, whatever its layer.
- Every rule record carries `layer`, `class`, `conservative: bool`, `owner`. Hypothesis H4 tests whether reading fails first on L3 rules.

**Naming clash:** v1 uses `L0`/`L2` for *override levels* (study2 worlds `S-L2` etc.). In v2, `L0`–`L3` are layers only; override depth becomes a world parameter `overrides: 0|1|2`.

### 2.2 Representations (one source, three projections)

| Column | Form |
| --- | --- |
| text | Markdown: data dictionary, glossary, handbook prose |
| structured | YAML/JSON: dbt-style schema, flat concept list, typed n-ary claim records (`id, frame, roles, scope, evidence, warrant, status`), rule records |
| formal | SWI-Prolog: facts, tabled rules, rule metadata as facts |

All three are *generated* from one world model plus one rule file. Never hand-maintain two projections. Where English rule text cannot be generated from the clause, keep English and clause in the same rule record and let the independent verifier (§4.3) prove them equivalent.

No RDF/OWL column in v2. v1 already showed plain OWL cannot state decisions and that OWL + SHACL behaves like the others behind an engine.

### 2.3 Modes

- **read**: representation in context; the model answers directly (repeats v1 conditions per layer).
- **compile**: the model writes a plan (an intermediate model, IM) that the engine executes. In v2 the IM is a Prolog goal over declared predicates (data == program). Static checks before execution: predicates exist in the capability registry, arities match, no side-effecting builtins, variables safe. Ambiguity by execution: request k = 3 candidate IMs; if their answers agree, answer; if they differ, the correct output is `AMBIGUOUS` with the differing readings.
- compile is meaningful for formal, partly for structured (plan over declared relations), not for text. That asymmetry is reported, not hidden.

### 2.4 Answer statuses (keys are per question × layer)

`ANSWER` · `AMBIGUOUS` (readings differ) · `CONFLICT` (rules collide without precedence) · `UNDERDETERMINED` (the layers present do not settle it; name what is missing) · `OUT_OF_SCOPE` (no adequate term: abstention).

A question with minimum layer k has key `UNDERDETERMINED` below k. This makes overreach measurable at every rung, as v1 did for missing decisions.

### 2.5 Question kinds

fact · explain · structure · permission · fitness. Each question records `kind`, `min_layer`, `forks` (named interpretation forks it touches), `type` (bool, int, set, status, justification).

"explain" answers are graded structurally: the model must cite rule ids and fact ids; grade set-F1 against the engine's proof (rule ids used), plus the status.

## 3 Hypotheses

- **H1 Layer step.** Accuracy on questions with `min_layer = k` jumps when layer k is present; below k, overreach (answer instead of `UNDERDETERMINED`) is the dominant error.
- **H2 Representation.** Within a layer, in read mode, representation matters less than layer presence at small scale (extends v1 A1); at scale it re-enters through length.
- **H3 Mode.** compile ≥ read at scale and on L3; errors move to translation and are measurable there (v1's open item).
- **H4 Criterion.** Read-mode failures concentrate on non-conservative / defeasible / deontic rules (L3), not on conservative ones.
- **H5 Small + engine.** A small model in compile mode matches or beats a large model in read mode.

Each hypothesis needs a test that can fail. If H1 fails (no step), the layer is decoration.

## 4 Build

### 4.1 Domain

Keep the procurement domain. It already spans the layers:
- L0: `cc`, `cc_parent`, `emp`, `reports`, `req`, `vendor`, `booked`, `cap`, `role_limit`, `org_unit`.
- L1: ancestors, reporting chain, booked total, headroom, charges; v1 forks C1 (committed spend: booked only?), C3 (department = cost centre or org unit?), C4 (caps on ancestors?) are L1 definitional decisions.
- L2: dated rule versions and vendor status periods, `today`, withdrawn exemptions (v1 C2); add two sources that disagree (HR vs finance on an employee's cost centre) and claim status.
- L3: approver eligibility, vendor check with exception and exception-to-exception, deny overriding approval, deny vs auto-approve without precedence (v1 C5 → `CONFLICT`).

Harvest `study1-interpretation/oracle/large/*.dl` (dated periods, org units, exemptions) and `study2-scaling/gen.py` (tree generator, sizes, sampling of questions) into one generator.

### 4.2 Engine (SWI-Prolog)

- SWI-Prolog 9.x, `:- table` on recursive predicates (termination for the Datalog fragment), `tnot/1` for negation under well-founded semantics, `aggregate_all/3` for sums and counts.
- Rules loaded at runtime (`consult` / `assertz`); no compile or deploy step. Rule metadata as facts: `rule(Id, Head, Layer, Class, Conservative, Owner)`.
- `why/2`: a meta-interpreter returning the proof tree for a ground goal. Risk: tabling and meta-interpretation interact badly. Plan: compute answers with the tabled program; justify a ground answer with a depth-bounded meta-interpreter that treats tabled subgoals as lemmas; record negated subgoals as `absent(G)` (closed world). Verify that every `why` tree checks by re-running its leaves.
- `ask` CLI with the v1 interface (`./ask 'approved(R)'`), backed by `swipl`. Log every call at the tool boundary (v1 finding: tool use cannot be read off a transcript).
- Capability registry: `capability(Pred/Arity, Layer, Doc)`; the compile-mode validator and the prompts both read it.

### 4.3 Keys and checks

- Keys computed by the Prolog engine.
- Independent check: a plain-Python reference implementation of the rule records' English (harvest `study2-scaling/verify.py`) must reproduce every key. Optional second check: emit the Datalog fragment (L0–L2 plus stratified L3) for Soufflé and compare relation by relation; keep only if cheap.
- `make verify` fails on any disagreement.

### 4.4 Harness

- Harvest `study1-interpretation/harness/run.py` (litellm loop, oracle turns) and `study2-scaling/score.py` (exact + set-F1).
- Run through the API, not subagents: fixed model ids, temperature, reasoning budget, ≥ 3 reps per cell, exact token and wall-time accounting (all v1 threats).
- Models: one small and fuzzy (Haiku-class and/or a local 8–30B open model via litellm), one strong reference.
- Records: one JSONL per run with world, layer, representation, mode, model, question, raw output, parsed answer, status, tool calls, tokens, seconds.

### 4.5 Proposed layout

```
REWORK.md          this plan (delete or fold into README when done)
world/             gen.py (one generator), domain.py (entities, sizes, forks)
rules/             rules.yaml (rule records: id, layer, class, conservative, owner, english, prolog)
render/            text.py, structured.py, prolog.py  (projection per representation × layer)
engine/            core.pl, why.pl, capability.pl, ask
verify/            reference.py (independent Python), check.py
questions/         bank.yaml (templates: kind, min_layer, forks, type) → per-world questions + keys
harness/           run.py, compile.py (IM validation, k-candidate execution), score.py
worlds/            generated, committed (exact worlds used in runs)
results/
paper/             v2 paper sources
```

### 4.6 v1

- First, ask Matthias before committing the pending v1 edits (`PAPER.md`, `README.md`, figures, PDF are modified, uncommitted). Then tag the commit `v1`.
- Move the v1 paper to `paper/v1/` (PAPER.md, PDF, figures) so it stays citable; keep v1 studies reachable via the tag rather than duplicating them in `main`. Remove `history/`, `study1-interpretation/`, `study2-scaling/`, OWL/SHACL code from `main` once their useful parts are harvested.
- Requirements drop pyshacl / rdflib; add SWI-Prolog to the README prerequisites.

## 5 Milestones

Each ends with a test that can fail.

| # | Deliverable | Test |
| --- | --- | --- |
| M0 | v1 frozen and tagged; layout in place | `git checkout v1 && make verify` still passes |
| M1 | world model, rule records, Prolog engine, Python reference, L0 projections in 3 reps, question bank with per-layer keys | reference == engine on every key, 3 seeds × 3 sizes |
| M2 | read-mode runs at L0 | below-layer questions keyed `UNDERDETERMINED`; overreach rate reported |
| M3 | L1 added (definitions, bindings, C1/C3/C4 forks) | H1 step visible for `min_layer = 1` questions |
| M4 | L2 added (versions, sources, disagreement, C2) | a contradiction survives ingestion; as-of questions keyed correctly |
| M5 | L3 added (approval, exceptions, deny, C5), `why/2` | every `why` tree re-verifies; explain answers graded against it |
| M6 | compile mode, IM validator, k-candidate ambiguity | forks surfaced by divergent execution vs read-mode baseline |
| M7 | full matrix runs, paper v2 | H1–H5 each confirmed or falsified, with counts |

Cost control: do not run the full matrix before M6. Per milestone run only the new layer's questions, plus a fixed regression subset.

## 6 Open questions

- Is the rule classification (definitional, material inference, defeasible, incompatibility, entitlement, fitness, temporal) closed? Record any rule that fits no class.
- Can English rule text be generated from clauses for L1–L3, or must it stay co-located and verified?
- Does `why/2` scale to L-size worlds within the per-call time limit?
- Clojure later: the IM is plain data; re-hosting it in Clojure/EDN should need no change to the plan language. Check that nothing Prolog-specific leaks into the IM schema.

## Decisions

(Executor: append dated entries — what was decided, why.)

**2026-11-22 · M0**
- v1 frozen: Matthias approved committing the pending v1 edits (PAPER.md, README.md, figures, PDF) as `24973ef`, tagged annotated `v1`. REWORK.md kept out of that commit.
- M0 test passes: `make verify-v1` adds a temporary worktree at `v1`, runs its `make verify`, removes the worktree, and propagates the exit status (checked with a forced failure). Toolchain: Soufflé 2.5 (brew), pyshacl 0.40.2 / rdflib 7.6.0 in a gitignored `.venv/` on Python 3.14.
- SWI-Prolog is 11.0.0 (current brew bottle), not 9.x as §4.2 says. `table`, `tnot/1`, `aggregate_all/3` are unchanged; README states "9+ (developed on 11.0)".
- Deviation from §4.6 ordering: `history/`, `study1-interpretation/`, `study2-scaling/` and the OWL/SHACL code were removed from `main` in M0, not after harvest. Reason: the `v1` tag already keeps them byte-for-byte reachable (`git show v1:study2-scaling/gen.py`, or a worktree), so harvesting in M1 loses nothing, and `main` avoids a half-v1/half-v2 state where the Makefile and requirements disagree.
- `paper/v1/` holds PAPER.md, whitepaper.pdf and both figures. The only edit to PAPER.md is the figure paths (`paper/fig-*.png` → `fig-*.png`). v1's `paper/build.py` and `paper/figures.py` were not moved: they read study results that now live only at the tag, so they are rebuilt from there (`paper/v1/README.md`).
- Layout from §4.5 created as directories with `.gitkeep`; no `make verify` on `main` until M1 has something to check (a target that always passes would not be a test).
- requirements.txt: dropped pyshacl/rdflib, added pyyaml (rule and question files are YAML).
