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
- Does `why/2` scale to L-size worlds within the per-call time limit? (Answered in M5: yes, L-s1 builds and checks 10857 trees in 1.65 s.)
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

**2026-11-22 · M1**
- M1 test passes: `make verify` regenerates `worlds/` and requires it to match byte for byte. Then, for 3 sizes × 3 seeds, `verify/reference.py` must reproduce every key `engine/keys.pl` computed: 9 worlds × 48 questions × 4 layers × 2 fork configurations = 3456 keys. Mutating two comparisons in the reference makes it fail, so the test can fail. Key statuses over all worlds:
  - decided config: 991 ANSWER, 648 UNDERDETERMINED, 17 CONFLICT, 72 OUT_OF_SCOPE;
  - open config: 214 of those ANSWERs become AMBIGUOUS.
- Scope: the full rule base, L0–L3 (38 rule records), is written and keyed now, so the keys for M3–M5 already exist and are checked. Only L0 is rendered (text.md, structured.yaml, formal.pl). The L1–L3 projections come with their milestones.
- `why/2` is deferred to M5, as the milestone table says (§4.2 lists it under the engine). There is no Soufflé cross-check, which §4.3 marked optional.
- Negation is `\+`, not `tnot/1`. The rule base is stratified, and `keys.pl` halts if it is not, so well-founded semantics adds nothing. `\+` also keeps clauses portable to the plain Datalog/Python reading. Only recursive predicates are tabled: `cc_anc/2` and `chain/2`.
- Programs are built per (layer, fork readings) into a fresh module. Only relations and predicates of layer ≤ L are declared, so a call above the layer is an existence error rather than a silent `false`. `ask` reports this as "headroom/2 is not defined at layer 0".
- Rule records live in `rules/rules.yaml`: id, head, layer, class, conservative, owner, fork, table, english, prolog. The engine reads them at runtime; there is no build step.
  - Forks are data: id, layer, owner, question, readings, decided. A forked rule carries `fork: {id, reading}`.
  - The v1 forks keep their names: c1 committed spend, c2 governing date, c3 department, c4 cap scope.
  - C5, deny vs auto-approve, has no rule by design. It is a `conflict:` goal in the question bank, keyed CONFLICT.
- Two key configurations per question and layer:
  - `decided`: every fork takes its decided reading, which is what the material states once a fork is written down.
  - `open`: every fork the question depends on at that layer is live. Readings that disagree give AMBIGUOUS, with the value under each reading.
  - Q25 (which cost centre on a date) is CONFLICT at L2, where hr and finance disagree. At L3 it is resolved by R313 (finance governs). A resolve goal applies only from its own layer upwards.
- min_layer and forks: the engine derives both from the dependency closure of goal ∪ conflict. The bank declares them too, and `check.py` requires the two to agree, so a template cannot silently need a higher layer than it claims. OUT_OF_SCOPE (Q91, `travel_budget/2`) is detected as a call to a predicate no layer defines.
- L0 shows *current* values (`role_limit`, `vendor`, `emp.cc`). L2 adds the history behind them: `role_limit_version`, `vendor_status`, and `assignment` with an hr and a finance source. `check.py` requires L0 to equal L2 evaluated on `today`. Keys are relative to each layer's material: Q01 (which relations refer to X) has a different answer at L0 and at L2, by design.
- Sources that disagree (§4.1): HR records a transfer on d1. Finance records it 7–40 days later, or not yet; every world has one move finance has not recorded by today. `emp/3` is finance's view as of today.
  - "Claim status" from §4.1 was not added. The hr/finance disagreement already gives L2 a contradiction that survives ingestion (M4's test), and a second mechanism would add rules without adding a question kind.
- Question value types are bool, int, set and **sym** (a single symbol, such as a status or a cost centre). sym was added because "which cost centre" and "which status" are neither sets nor counts.
- Each world plants six requests so that every rule interaction occurs at least once:
  - C5;
  - waiver blocked;
  - waiver applies;
  - the manager-limit change (c2);
  - the exemption withdrawn later (c2);
  - the vendor suspended later (c2).
  Request ids are shuffled afterwards, so position gives nothing away.
- Sampling: each template draws 6 candidate instances. Two are kept from different key signatures (L3 decided value + open status), so the two instances of a template do not trivially share an answer. 24 templates (including the out-of-scope Q91) × 2 = 48 questions per world.
- Python 3.14 / SWI-Prolog 11.0 details: `library(http/json)` moved to `library(json)` and is loaded conditionally. Derived predicates are declared `discontiguous`, because forked alternatives interleave.

**2026-11-22 · M2**

- **Test passes.**
  - Below-layer keying: every question whose min_layer exceeds the layer is keyed UNDERDETERMINED. `verify/check.py` checks this, and `harness/score.py` asserts it again before scoring.
  - The overreach rate is reported in `results/m2-read-L0-deepseek-v4.1-flash.md`.
- **The run.**
  - `deepseek/deepseek-v4.1-flash` in read mode at L0, on S-s1, S-s2, S-s3 and M-s1 × 3 representations × 48 questions × 3 repetitions: 1728 calls, no API errors.
  - Cost $0.34, plus $0.004 of probes.
  - Overall results:
    - ANSWER keys: 99% correct (357/360).
    - OUT_OF_SCOPE keys: 100% correct.
    - Overreach on UNDERDETERMINED keys: 31% (401/1296).
  - Overreach by the question's min_layer:
    - L1: 60%;
    - L2: 19%;
    - L3: 14%.

    This fits H1's "overreach is the dominant error below the layer": every wrong status on an UNDERDETERMINED key is an ANSWER or an OUT_OF_SCOPE.
  - Overreach by representation: text 35%, structured 30%, formal 28%.
  - Status stability across 3 repetitions is 72–83% of question cells.
- **Harness without litellm.** `harness/openrouter.py` is a standard-library client, so no new dependency. It sends no identifying headers and records the served model, provider, tokens, reasoning tokens, OpenRouter's billed cost and wall time per call. v1's oracle turns belong to compile mode and are deferred to M6.
- **Model and routing.**
  - The model id is pinned.
  - Providers are restricted to fp8 and sorted by price; 1724 calls went to Baidu and 4 to InferenceNet. The provider is recorded per call.
  - Temperature 1.0, as in v1. `reasoning.effort = medium` is set explicitly rather than left to the provider default. max_tokens is 16000, and every call ended with `stop`.
- **Read mode.**
  - One question per call. The layer's material goes in the system message, and the question plus the expected answer type go in the user message.
  - The model ends its reply with a JSON object `{status, value, readings, missing}`.
  - The prompt defines the five statuses and never mentions layers, so the model is not told that more material exists.
- **Scoring.**
  - `correct` means the status matches and, for ANSWER keys, the value matches exactly.
  - Overreach is an UNDERDETERMINED key met with ANSWER or AMBIGUOUS. It is the primary below-layer metric.
  - Abstention is scored leniently (UNDERDETERMINED and OUT_OF_SCOPE are interchangeable) and strictly (the exact status). At L0 the two can't be told apart from inside the material when the layer that introduces a notion also introduces its relation. Q26 (exemptions) and Q24 (hr/finance disagreement) are mostly answered OUT_OF_SCOPE for that reason, so the lenient score is the one to read.
  - The scorer re-parses the raw replies, so parser fixes apply to old records. `UNDETERMINED`, used in 44 replies, is accepted as an alias and counted in the report.
- **Open for M3/M4: overreach that matches the later key.** The report shows how often an overreaching ANSWER equals the decided key at the question's min_layer:
  - Q13, Q14, Q16, Q22 match in every case. The obvious reading coincides with the definition the next layer supplies, so the value can't tell a guess from knowing the definition.
  - Q11 ("booked total") almost never matches: the model reads it as direct spend, while L1 defines it over the subtree.

  When M3/M4 sampling chooses instances, it should prefer ones where the natural-language default and the later definition differ, so that a step at the layer shows in values and not only in statuses.
- **Results files.** `results/*.jsonl` are working files and are not committed. The gzip copy (1.7 MB, with reasoning text) and the Markdown report are committed.

**2026-11-22 · M2 addendum** (Matthias's five follow-ups to M2, done before the M3 runs)

- **Fork c6, booked total (item 4).**
  - Registered as `c6` (controller): `with_descendants` (R104, decided) / `direct_only` (new R104b). It is c6, not c5, because C5 is the deny/auto-approve CONFLICT.
  - The L1 concept for "booked amount" now says it is the direct amount and that the booked total is defined separately (R104).
  - The bank's `forks:` lists of Q11–Q14 now include c6; `check.py` requires them to match the derived closure.
  - Existing questions, instances and decided keys are unchanged. Only open keys moved: Q11–Q14 and Q33/Q34/Q36 become AMBIGUOUS where the two readings differ.
- **Q16 (reporting chain).** The default was accepted: R103 stays unowned. "Reporting chain" has one reasonable reading (transitive managers). The M2 overreach on Q16 matches the L1 key every time.
- **Paraphrase (item 5).**
  - Q17 asks Q11's goal as "What is the rolled-up booked spend of cost centre {c}?".
  - `paraphrase_of: Q11` reuses Q11's instances with no sampling, so neither the RNG stream nor any other question moves.
  - Result (DeepSeek, base prompt, S-s1–3 + M-s1, n=3):
    - Q11 is answered 72/72, with the roll-up value 1/72.
    - Q17 is UNDERDETERMINED 33/72 and answered 39/72, every answer the roll-up value.
  - The wording selects the reading, so c6 is a real fork and not a model quirk. Score.py has a "Paraphrases" section.
- **Noticed but answered (item 1).**
  - What it counts: an overreaching ANSWER whose content or reasoning trace matches an ambiguity/missing-definition keyword list. There are two lists:
    - strict: ambiguous, not defined, unspecified, no rule, …
    - wide: strict plus assume, interpret, missing, not stated, …
  - JSON keys (`"missing":`, `"assumptions":`) are blanked first. The control is the same rate on ANSWER keys answered correctly.
  - M2 data (DeepSeek, all 401 overreaches):
    - strict: 89% (355/401), control 11%;
    - wide: 96%, control 17%.
    - Per representation (strict / control): formal 92/13, structured 91/17, text 84/5.
  - The noticing is in the reasoning trace: the visible reply flags it in 2/401. The user's rough 352/401 is confirmed.
  - It is a keyword heuristic and calibrates differently per model (see Models below), so read it with its control.
- **Assume prompt (item 2).**
  - Added as `--prompt assume`: the same instructions plus a required `assumptions` list in the JSON. It is a field, not a sixth status, so status scoring stays comparable with the base prompt. The record carries `prompt`, and a cell key includes it.
  - Subset: S-s1–3, 11 templates (Q01 Q03 Q05 controls; Q11 Q13 Q14 Q15 Q16 Q17 at min_layer 1; Q22; Q31) × 3 representations × 3 reps.
  - Results, base → assume, on the same cells:
    - overreach on min_layer 1 fell from 67% to 59%;
    - min_layer 2 stayed at 100%;
    - min_layer 3 went from 48% to 46%.
  - 93–96% of overreaching ANSWERs list assumptions, and the assumptions name the chosen reading. For example: "'booked total' is read as the amount booked directly on the cost centre".
  - 15–39% of correct control answers also list assumptions. These are trivial schema readings ("pending means status 'pending'").
  - Per template, abstention rose:
    - Q15: 65 → 83%;
    - Q16: 9 → 20%;
    - Q17: 54 → 70%.
    - Q11, Q13 and Q22 are still answered almost always.
  - Conclusion: overreach turns into *stated* assumptions, not into abstention.
    - A later scoring option is "ANSWER + an assumption naming the missing definition" as a softer category than silent overreach.
    - Under assume, the wide keyword list is contaminated (control 87–94%, because the trace discusses the field), so use strict.
  - Report: `results/m2a-assume-L0-deepseek-v4.1-flash.md`.
- **Models (item 3).** Same 11 templates, base prompt, S-s1 + M-s1, reps 0–1 (264 calls per model). Report: `results/m2a-models-L0.md`.
  - **GLM-5.3** (`z-ai/glm-5.3`):
    - Configuration: `reasoning.effort = high`, Novita, fp8.
    - fp8 to keep quantization comparable with DeepSeek; fp4 providers were excluded.
    - Effort high because at medium it thinks adaptively and barely reasons (28–163 tokens in a 12-call pilot, kept in `m2a-pilot-…-medium.jsonl`).
  - **Qwen3.8-flash** (`qwen/qwen3.8-flash`): effort medium, Alibaba (the only provider; quantization not reported, so `--quantization any`).
  - Overreach on the min_layer 1 keys of these cells:

    | Model | Overreach | ANSWER keys correct |
    |---|---|---|
    | DeepSeek | 74% | 99% |
    | Qwen | 69% | 97% |
    | GLM | 96% | 96% |

    - min_layer 2 (Q22) is 100% for all three.
    - min_layer 3 (Q31): 42 / 17 / 25%.
  - The stronger model overreaches *more*. GLM answers Q14, Q16 and Q17 almost always, where DeepSeek and Qwen abstain on half of Q14. On Q15, GLM uses AMBIGUOUS (20/24) instead of UNDERDETERMINED.
  - The paraphrase effect replicates in every family. Q11 is read as direct spend (roll-up 1/22, 0/23). Every Q17 ANSWER is the roll-up value (18/18, 23/23).
  - Noticed (strict) per model:
    - DeepSeek 87–95%, control 0–29%.
    - Qwen 97–100%, but control 43–57%: its traces use the keywords throughout, so the heuristic barely separates.
    - GLM 35–47%, control 0–4%: it answers without discussing alternatives.
    So "noticed but answered" is a DeepSeek finding, not a general one.
  - Stability across 2 reps: DeepSeek 75–84%, Qwen 75–80%, GLM 86–95%.
  - Bias: the 11 templates were chosen from DeepSeek's M2 overreach, which favours finding overreach for DeepSeek. GLM is still higher.
- **Routing.**
  - The cheapest fp8 provider for DeepSeek (Baidu) returned HTTP 429 ("temporarily rate-limited upstream") on most calls at ≥3 workers. The fallback went to InferenceNet at 3× the output price.
  - Added `--only-provider P…`, which sets `provider.only`. `allow_fallbacks: false` is not used: with it, OpenRouter tries only the first provider in the list.
  - Failed calls are stored as error records and retried on resume.
  - The assume run was served by Baidu 562, DeepInfra 332 and InferenceNet 294. All are the same model at fp8; the provider is recorded per call.
- **Cost.**

  | Item | Cost |
  |---|---|
  | DeepSeek (Q17 + assume) | $0.646 |
  | GLM | $0.411 run + $0.014 pilot + about $0.016 provider probes |
  | Qwen | $0.509 |
  | Addendum total | about $1.60 |
  | Running total with M2 | about $1.94 of the $5 |

  The M-s1 assume cells begun in the first attempt (59 records) are kept but not used; the assume comparison is on the S worlds.

**2026-11-22 · M3**

- **Test passes: the H1 step is visible for min_layer 1 questions.**
  - Setup: DeepSeek, base prompt, decided config, S-s1–3 + M-s1 × 3 representations × 3 reps, on the same question instances at both layers.
  - Correct on min_layer 1 questions goes from 40% (203/504) at L0 to 99% (501/504) at L1:

    | Representation | L0 | L1 |
    |---|---|---|
    | formal | 49% | 99% |
    | structured | 41% | 99% |
    | text | 32% | 100% |

  - The step also shows in *values*:
    - At L0, Q11 is answered with the direct reading (roll-up value 1/72).
    - At L1, Q11 and Q17 are 72/72 correct under R104's roll-up.
  - Report: `results/m3-read-L1-deepseek-v4.1-flash.md`. Its L0 rows are the M2 and m2a base-prompt records on the same cells.
- **Run scope** (cost control, §5). This is not all 50 templates. It covers:
  - every min_layer 0 template (Q01–Q05) as the regression subset;
  - every min_layer 1 template (Q11–Q17);
  - Q21, Q22, Q31 and Q33 as above-layer probes;
  - Q91 (out of scope).
  - 17 templates × 2 instances × 4 worlds × 3 representations × 3 reps = 1224 calls (including a 24-call pilot).
  - The open config covers only the forked L1 templates Q11–Q15 and Q17: 432 calls.
- **Regression and above-layer.**
  - L0 questions stay at 99% at L1, and Q91 at 100%.
  - Above the layer, overreach persists: 50% on min_layer 2 at both layers, and 26% → 20% on min_layer 3.
    - Q22 (applicable approval limit) is ANSWER 72/72 at L0 and at L1, and equals the L2 key every time.
    - Q33 ("is request r approved?") moves from UNDERDETERMINED to OUT_OF_SCOPE (31/72) at L1. This is still abstention, so the strict-correct rate on min_layer 3 drops (74% → 58%) while overreach falls.
- **Open config (L1-open).**
  - Text and structured are 95–97% correct: AMBIGUOUS, with the value under each reading right.
  - Formal is 16%. On the 129 AMBIGUOUS keys, formal answers UNDERDETERMINED 111 times. Every one of the 111 names the open fork in `missing`, and some compute both values first.
  - Overreach (ANSWER on an AMBIGUOUS key) is low everywhere: text 5, structured 3, formal 2 of 129.
  - Reading: the formal projection states an open fork as an absent `reading/2` fact, with the comment "nothing that depends on an open question is derived". The model takes that literally, as a missing decision, which the status definitions also allow.
  - This is a representation effect on the AMBIGUOUS/UNDERDETERMINED boundary, not overreach.
  - The material was left as rendered for this run. An ablation is open: reword the formal comment to list the readings' values as alternatives; 144 calls, about $0.13. Alternatively, score "UNDERDETERMINED naming the open fork" as a lenient match for AMBIGUOUS.
- **L1 material.**
  - Concepts (`rules.yaml` `concepts:`) bind each term the definitions use to a column, with the contrast that keeps it apart from a neighbouring term. They are descriptive only: the engine does not read them.
  - Rules are rendered with their id and English in all three representations. Formal also carries the clauses and `rule/6`, `doc/2`, `concept/3` and `fork/5` facts.
  - Decided: the definitions follow the decisions, and a Decisions section states them.
  - Open: every fork *of the layer* is shown open, not only those a question depends on, so the material is the same for every question. Each fork lists its readings with their rule ids. In formal, each reading's clauses are guarded by `reading(Fork, Reading)`.
  - L0 material stays byte-identical to the M2 run. The L1 format note in the prompt is added only from L1 on (`RULES_NOTE`).
- **Formal check.**
  - `verify/formal.pl` loads each rendered L1 / L1-open `formal.pl` alone, asserts the job's readings, and must reproduce every L1 key.
  - In particular, a question keyed UNDERDETERMINED at L1 must not be derivable from the file.
  - `make verify` runs it for all 9 worlds.
- **Questions stay fixed across layers.** The same instances are asked at every layer, and only the key changes, so a step is a within-question comparison. Records carry `cfg` (decided/open), and the resume key includes it.
- **Cost.** L1 decided $0.311; L1 open $0.388 (about 3× per call: about 1670 completion tokens against 510, because both readings are worked out). M3 total about $0.70. Running total about $2.64 of $5, with about $2.36 left for M4–M6.

**2026-11-22 · Stronger models and the formal-open ablation** (decided with Matthias after M3)
- **Move on with DeepSeek through M6.** No separate formal-open ablation. Instead the renderer's open-config wording is fixed in M4 (readings stated as alternatives, not as a missing decision), and the next open-config run measures it.
- **No Claude 5.5 run.** Estimates were about $40 (Sonnet 5.5) / $80 (Opus 5.5) for a reduced matrix of about 3,400 calls and $380 / $750 for the full matrix; Matthias judged this out of range. M7 stays on DeepSeek within the $5 cap; any second model must be cheap and is discussed first.
- **Harness note, for any later model.** `run.py` always sends `temperature`; Claude 5.5 models reject it, so it would have to be made optional.

**2026-11-22 · M4**

- **Test passes.**
  - *A contradiction survives ingestion.* Q25 ("which cost centre did e belong to on d?") is keyed CONFLICT whenever HR and finance disagree on the date: 45 of 72 instances in the run worlds. The key now carries the two sides (`sides`, computed by the engine and, independently, by the Python reference).
  - `verify/check.py` has two new checks:
    - **rows**: every relation row of the world appears in all three representations of every material directory (L0, L1, L1-open, L2, L2-open), so the disagreeing `assignment` rows are not dropped by any renderer;
    - **formal CONFLICT**: the rendered `formal.pl` must derive the conflict, and both sides, under every reading combination.
  - Negative tests: deleting a disagreeing row from text.md, formal.pl or L2-open/formal.pl makes `make verify` fail.
  - *As-of questions are keyed correctly.* For Q21, Q22, Q23 and Q26 the check counts instances whose L2 key differs from the value as of `today`: 6, 2, 8 and 10 of 18. A full run fails if any template has none, so the dated keys can't silently collapse to "today".
- **L2 material.**
  - Relations: `today`, `role_limit_version`, `vendor_status`, `assignment` (per source, with an effective date), `exemption`, `exemption_withdrawn`. Rules R201–R207. Fork c2 (request date vs today for the owner's procurement rule), decided as request_date.
  - **Leak fix.** At L2 the `emp` column doc said "current cost centre", which next to two disagreeing sources reads as "finance is the system of record", and that is R313 (L3). From L2 on the doc is "as finance records it", via a new `doc_from` per-layer override in `schema.yaml`. L0 and L1 material stay byte-identical.
  - **Open wording** (the decision after M3). The L1-open / L2-open formal comment now says the readings are alternatives the material allows, and how to evaluate under one (assume `reading(Fork, Reading)`). It no longer says "nothing that depends on an open question is derived". This changes only `*/L1-open/formal.pl` among older material.
- **Run scope** (§5). DeepSeek, base prompt, S-s1–3 + M-s1, flags as in M3.
  - L2 decided: Q21–Q26, Q31, Q33 × 3 reps (576 calls), plus the regression subset Q01–Q05, Q11–Q17, Q91 × 1 rep (312).
  - L2 open: the forked templates Q11–Q15, Q17, Q22 × 1 rep (168), plus Q22 on M-s2 and M-s3 × 3 reps, so that c2 has differing readings (36).
  - Rewording: L1-open, formal only, Q11–Q15 and Q17 × 3 reps (144), on the same cells as M3.
- **Results, L2 decided** (`results/m4-read-L2-deepseek-v4.1-flash.md`).
  - New ANSWER keys: Q21–Q24 and Q26 are 100% (360/360), as-of instances included. On min_layer 2, correct on ANSWER keys is 387/387.
  - Regression: min_layer 0 98% (Q03 3/24 wrong; a count on M-s1 that was wrong at L0 too, not an L2 effect), min_layer 1 98%, Q91 100%.
  - **Q25 CONFLICT: 0/45 under strict scoring, yet no reply picked a side.**

    | Representation | No side picked | AMBIGUOUS with both sides |
    |---|---|---|
    | formal | 15/15 | 14/15 |
    | structured | 15/15 | 11/15 |
    | text | 15/15 | 10/15 |

    The rest are UNDERDETERMINED, naming the missing precedence. The 27 ANSWER instances of Q25, where the sources agree, are all right. The replies say "no rule says which source prevails" and still file it as AMBIGUOUS. The likely cause is the answer format: only AMBIGUOUS has a slot (`readings`) for two values. This is a status-boundary effect, like the formal-open one in M3. It is not overreach. For M6/M7: either give CONFLICT a `sides` field in the JSON line (a prompt change, so it needs a fresh baseline), or score "AMBIGUOUS = both sides" as a lenient CONFLICT. For now it is reported, not adopted.
  - **Above-layer overreach grows in text.** min_layer 3 overreach is 26% (37/144). Q31 ("may m approve r?") is ANSWER 23/24 in text at L2, against 16/24 at L1; structured 8/24, formal 1/24. The L2 limits and exemptions give enough to assemble an approval rule the material doesn't state. Q33: 5 ANSWERs, all text.
- **Results, L2 open.** Correct: formal 94%, structured 97%, text 97%; AMBIGUOUS readings right 92% / 96% / 96%. Q22 under c2: 18/18 AMBIGUOUS with the right values. Q17: 6/24 ANSWER (overreach on an open fork).
- **Results, rewording** (`results/m4-read-L1-open-reword-deepseek-v4.1-flash.md`, against the M3 formal-open cells).

  | L1-open formal | M3 | M4 |
  |---|---|---|
  | correct | 23/144 | 125/144 |
  | AMBIGUOUS key → AMBIGUOUS | 16/129 | 118/129 |
  | AMBIGUOUS key → UNDERDETERMINED | 111/129 | 0/129 |
  | AMBIGUOUS key → ANSWER (overreach) | 2/129 | 11/129 |

  The M3 formal-open gap was the wording, as suspected. With a reading stated as an alternative, formal comes close to text and structured (95–97%). Overreach rises somewhat. Mean completion tokens 1817 → 2168. Because M3's formal-open numbers measured the old wording, they are superseded for any comparison across representations.
- **Harness.** `score.py` gains a "CONFLICT keys" section (strict, both sides as AMBIGUOUS, no side picked, resolved by the L3 value, other ANSWER). `run.py`, `read.py` and the prompt are unchanged.
- **Cost.** L2 decided $0.410, L2 open $0.207, rewording $0.135: M4 $0.75. Running total $3.37 of $5 (summed over every results file), $1.63 left for M5–M6.

**2026-11-22 · M5**

- **Test passes.**
  - *Every `why` tree re-verifies.* `verify/why.pl` builds a tree for every derived predicate of layers 1–3, under the decided readings and under every reading combination of the forks it depends on, up to 200 instances per predicate (dated predicates get each world date for their date argument). `check_why/3` re-checks each tree without the meta-interpreter. Results: S-s1 1785 trees (max depth 6, 0.13 s), M-s1 6234 (depth 7, 0.54 s), L-s1 10857 (depth 9, 1.65 s), 0 failures. Negative test: replacing a fact leaf's argument makes the check reject the tree. `make verify` runs it for all 9 worlds; the whole verify takes 45 s.
  - *Explain answers are graded against it.* `keys.json` gains `why`: for each bool question whose L3 decided key is ANSWER true, the tree (as JSON), `core` and `support`. That is 78 instances over the 9 worlds, 34 in the run worlds. `engine/keys.pl` refuses to write a tree that does not re-verify. `check.py` checks that each why entry belongs to an ANSWER-true key, that core is non-empty, that core and support are disjoint, and that every id is a rule record.
  - Open question §6 ("does `why/2` scale to L-size worlds?"): yes. The worst case is a depth-9 tree; all 10857 L-s1 trees build and check in under 2 s.
- **why/2 design** (`engine/why.pl`, as §4.2 planned).
  - Answers come from the tabled program. A true instance is then justified by a meta-interpreter over the same rule records: layer ≤ L, and forked clauses only under the chosen readings.
  - Node kinds: `rule(Id, G, Body)`, `fact`, `builtin`, `absent(G)` (closed-world negation, not expanded), `lemma(G)` (aggregates, member, or below the depth bound of 200, which no tree reaches), and `ite` for if-then-else, recording the branch taken.
  - Limits:
    - Positive proofs only. There is no why-not for false answers, so explain grading covers ANSWER-true keys only.
    - A non-ground goal is justified for its first solution.
    - The rules behind `absent` and `lemma` leaves are not expanded. They form the *support* set: rules an explanation may name. *Core* is the rules of the rule nodes: rules an explanation must name. For example, `cap_ok(r)` has core [R304] and support of 8 rules (the cap chain behind `absent(cap_breach(..))`).
- **L3 material.**
  - Rules R301–R313 rendered in all three representations.
  - Relations `emergency` and `violation` (layer 0 base relations, shown from L3).
  - L3-open has all forks c1–c6 open; L3 itself adds no fork.
  - Older material is unchanged.
  - Formal check fix: Q25 has a conflict goal at L2 and is settled at L3 by R313 (`resolve: authoritative_cc_on`). The formal check now evaluates `(conflict -> resolve ; goal)` for such keys, the same combination the engine keys use.
- **Harness.**
  - Prompt variant `explain`: the JSON line gains a required `"rules": [...]` list of applied rule ids. The template slots are renamed `extra_note` / `extra_field`; the base and assume prompts render byte-identically (checked).
  - `parse()` normalises ids (case, whitespace; ids that are not rule ids go to `rules_unparsed`).
  - `run.py --only-why` keeps only questions with a why key.
  - `score.py` gains an "Explanations" section: core recall, full recall, precision against core ∪ support, "nothing outside", exact, and recall per rule class and conservative flag (for H4).
  - Stub check (`stub:key`, which answers the key and cites core) scores 100% everywhere.
- **Run scope.** DeepSeek, flags as in M3/M4, S-s1–3 and M-s1.
  - L3 decided base: Q31–Q36 × 3 reps (432 calls) plus the regression subset Q01–Q05, Q11–Q17, Q21–Q26, Q91 × 1 rep (456 calls). Q25 is in the subset to check R313.
  - Explain: the 34 why instances × 3 representations × 3 reps (306 calls).
  - L3 open: Q31, Q32, Q35 × 1 rep (72 calls).
- **Results, L3 decided** (`results/m5-read-L3-deepseek-v4.1-flash.md`).
  - Correct on ANSWER keys 99–100% in every representation. New ANSWER keys: Q31, Q32 and Q35 are 72/72; Q36 is 70/72 (two arithmetic slips along the cap chain).
  - Regression: min_layer 0 98% (Q03 3/24 again, as at L0–L2), min_layer 1 and 2 100%, Q91 100%.
  - Q25 at L3 is 24/24: R313 (finance governs) is applied in every representation, including the instances that were CONFLICT at L2.
  - **C5 (denial vs automatic approval) is not reported as a conflict.** Q33's 9 CONFLICT instances got 8 ANSWER true and 1 CONFLICT. Q34's 36 CONFLICT instances got 28 ANSWER, 4 CONFLICT and 4 unparsed (max_tokens on structured and text). 27 of the 28 sets include the denied, auto-approved request.

    | Representation | CONFLICT | No side picked | ANSWER |
    |---|---|---|---|
    | formal | 0/15 | 0/15 | 15/15 |
    | structured | 2/15 | 5/15 | 10/15 |
    | text | 3/15 | 4/15 | 11/15 |

    The model reads R312 ("an automatically approved request is approved") as a second sufficient condition. It reads R310's "denial overrides eligibility" as scoped to eligibility, and so unions the two. That is a defensible reading of the text, and it is exactly the silent resolution C5 was planted to expose. This is the opposite of Q25 at L2, where the disagreement was in the data and was always noticed. Here the conflict is between two rules, and formal (two clauses for `approved/1`) never notices it.
  - Stability: formal 100%, structured 96%, text 92% of cells give the same status in every rep.
- **Results, explain** (`results/m5-explain-L3-deepseek-v4.1-flash.md`). All 306 replies are ANSWER true and correct; no list is empty.

  | Representation | core recall | full recall | precision | nothing outside | exact |
  |---|---|---|---|---|---|
  | formal | 0.97 | 94% | 0.97 | 95% | 92% |
  | structured | 0.97 | 93% | 0.96 | 90% | 89% |
  | text | 0.97 | 95% | 0.94 | 80% | 79% |

  - Text replies more often cite rules that were checked and did not apply: R303 (exemption), R311/R312 (auto-approval), R313. The grading counts those as outside the proof. "Considered" and "applied" are not separated by the prompt. If M7 cares, the prompt should ask for applied rules only and say so more sharply, or grading could allow rules whose head is the negated or rejected alternative.
  - H4 (conservative rules go unnamed more often): **not supported at this scale.**
    - Recall by class: L1 definitional (conservative) 94%, L2 temporal (conservative) 91%, L3 definitional (conservative) 67% (18/27), L3 material inference 75%, defeasible 88%, entitlement 88%, incompatibility 100%.
    - The misses are spread over the long chains (R103, R201–R204, R301, R305, R308, R310, about 9–15 each). They are not concentrated on conservative rules.
    - n is small (34 instances, one model), so this is a pilot reading, not a result.
- **Results, L3 open.** 72/72 correct, including Q32's 6 AMBIGUOUS keys (c2: vendor status on the request date vs today), with the right reading values.
- **Cost.** L3 decided $0.461 (the Q31–Q36 run stopped at its $0.35 cap 8 calls short and was resumed), explain $0.131, L3 open $0.024: M5 $0.62. Running total $3.98 of $5, $1.02 left for M6.

### 2026-11-23 · M6

- **Budget raised from $5 to $8** (Matthias, 2026-11-23). M7 is to be paid from the same cap.
- **Budget raised from $8 to $10, final limit** (Matthias, 2026-11-23, after M6's C5 and L0 runs had spent $6.49). It covers (iii) and M7.
- **Doc fixes.**
  - c6 leak: the `booked_total/2` doc said "the booked amount of C and all its descendants", which states the c6 reading `with_descendants`. It now reads "the booked total of cost centre C". Its effect on the earlier runs was nil.
  - `engine/capability.pl` now gives each relation the doc its material shows at the layer (`schema.yaml doc_from`), the same doc `render/common.py` uses. The compile prompt's predicate list therefore matches the material.
- **Compile mode** (`harness/compile.py`, `engine/compile.pl`).
  - *The plan is the intermediate model (IM).* It is plain data: `{"readings": {fork: reading}, "goal": "<Prolog goal>"}`. The goal runs over the layer's predicates and a whitelist of built-ins (comparison, arithmetic, lists, `findall`/`setof`/`bagof`/`aggregate_all`, `forall`, `\+`, if-then-else). There is no assert, I/O, `call/N` or module prefix.
  - *Static validation before execution.* Every called predicate must be in the whitelist or in the layer's capabilities; a predicate of a higher layer is reported as "not a predicate of the material". Readings must name an open fork and one of its readings. Execution is capped in time and inferences.
  - *k candidates in one call.* The model gives at most 3 plans, one per reading it considers, in a single reply. The engine also expands the open forks that a plan leaves unfixed. One distinct value gives ANSWER and several give AMBIGUOUS. More than 3 plans is a repair error, never a silent truncation.
  - *One repair turn* for validation or execution errors. Records keep the first and final outcomes.
  - The predicate list is alphabetical, so no layer order is shown.
  - Compile is offered for formal and structured only. Text has no declared predicates, and that asymmetry is reported, not hidden.
  - *The plan's `constructs` field* lists the aggregation and arithmetic built-ins the plan uses. It is a flag, not a rejection.
  - Stubs: `stub:key` (plans the bank goal), `stub:repair` (calls a missing predicate first) and `stub:plan` (always plans the bank goal, so the engine does the detecting). Each scores as designed: `stub:key` 100%; `stub:plan` gives CONFLICT 100%, engine-detected 4/4 at L3 for Q33/Q34, and at L0 every UNDERDETERMINED key is blocked.
- **L2-open, compile vs read** (`results/m6-compile-L2-open-deepseek-v4.1-flash.md`). The model is at ceiling in both modes:
  - Correct: compile formal 88%, structured 95%; read 93% and 96%. On AMBIGUOUS keys compile gets the readings right in 84% and 93%.
  - *Forks surfaced by divergent execution only (engine-only): 0%.* Whenever the plans diverged, the model had already split on the fork itself.
  - On Q12 the model gave 3 plans where c1 × c4 has 4 readings. The 3-plan cap is smaller than a two-fork product. Engine expansion of unfixed forks covers this when the plan leaves a fork open, but not when it fixes both forks in each of its 3 plans.
  - **Paper note: raw Prolog goals are an awkward plan language.** Of 62 first-pass compile errors, 30 were "V not bound" (a value question whose goal never binds V) and 28 were a list given as one value (`findall` into V where one solution per member is wanted). Another 3 were too many plans and 1 had no JSON. That is 58 of 62 errors in the plan's *shape*, not its logic. This argues for a typed plan schema: a data AST with declared output kind (scalar / set / bool), validated before execution. Not implemented.
  - Because L2-open is at ceiling, the rest of M6 was retargeted on Matthias's note, in order: (i) L0 overreach under compile, (ii) C5 after the fix, read vs compile, (iii) one L-size world.
- **C5 fix (a): an explicit incompatibility rule.**
  - *Why.* Under program semantics `approved/1` is the union of R310 and R312, so formal's 15/15 ANSWER in M5 was the literal reading, not an error. The M5 result stays as a separate finding: a formal rule set resolves an unstated precedence by construction (a union of clauses), so the formalism overreaches where a reader would have to stop.
  - *Fix.* New rule R314, `excluded(approved(R)) :- denied(R).` ("A denied request is never approved"; class incompatibility, owner procurement, layer 3). Now the material genuinely contradicts itself on a denied, auto-approved request, and CONFLICT is the right key by construction.
  - *Mechanical detection.* For each predicate P named by an `excluded/1` head at layer ≤ L, `program_x/3` builds M−, which renames P to `'P$raw'` and adds the wrapper `P(Xs) :- 'P$raw'(Xs), \+ excluded(P(Xs))`. If a goal's value differs between M and M−, the rule base derives both G and excluded(G): a detected CONFLICT, with sides [M− value, M value]. The stratification check gains the negative edge P → excluded/1.
  - *Keys.* `engine/keys.pl` cross-checks detection against the declared conflict goal wherever an exclusion bears on the goal; a mismatch throws. Q25 (a data conflict) stays declared only.
    - Q34 decided CONFLICT keys gain sides (approved and not denied in the subtree; approved in the subtree), in L-s2, M-s1, M-s3 and S-s1–3. Their details now read "derived and excluded: [...]".
    - An open-config key whose readings are all CONFLICT but whose sides vary by reading is CONFLICT without sides, not AMBIGUOUS. The same rule is applied in `keys.pl` and `reference.py`.
    - `check.py` checks that plain Prolog on the rendered formal.pl gives the last side, the union.
    - No status changed. The why keys are unchanged.
  - *Compile.* Each run that an exclusion bears on is repeated in M−. A difference makes the run's value "CONFLICT" (with sides and detail). If every run is CONFLICT the status is CONFLICT with `engine_conflict: true`; if only some are, the result is AMBIGUOUS with "CONFLICT" among the reading values. score.py's CONFLICT table gains an "engine-detected" column.
- **Results, C5 after the fix** (DeepSeek; M-s1, S-s1–3; Q33/Q34; n=3; `results/m6-{read,compile}-L3-c5-{decided,open}-deepseek-v4.1-flash.md`). Three of the four runs stopped at their $0.40 caps: read decided 98/144, read open 70/144, compile open 45/96, compile decided complete (96/96). The results on CONFLICT keys:

  | Mode, config | Representation | CONFLICT | ANSWER (a side) | Truncated (no JSON) |
  |---|---|---|---|---|
  | read, decided | formal | 3/6 | 0 | 3 |
  | read, decided | structured | 2/9 | 3 | 4 |
  | read, decided | text | 0/9 | 5 | 4 |
  | read, open | all | 0/16 | 0 | 16 |
  | compile, decided | formal | 15/15 (3 engine-detected) | 0 | 0 |
  | compile, decided | structured | 14/15 (6 engine-detected) | 0 | 1 |
  | compile, open | formal / structured | 6/9 | 0 | 3 |

  - *Read mode does not get better with the rule stated: the model reasons until it is cut off.* On CONFLICT keys the median reasoning is 15.6k tokens (decided), against 8.3k for the same keys in M5 and 2.3k for the ANSWER keys of the same run. In the open configuration every CONFLICT reply hit the 16k output cap. The C5 contradiction is now noticed (formal 3 of the 3 replies that finished), but read mode often cannot close it. This is v1's failure mode, which there appeared with size (exhausting the output budget without answering), here appearing with self-contradiction.
  - *Compile mode closes it.* Decided: 29/30 CONFLICT, median reasoning 6.7k tokens. Most of these the model declared itself (first reply CONFLICT: formal 12/15); where it planned the approval goal instead, the engine detected the contradiction. No compile reply picked a side.
  - ANSWER keys of the same templates: read 71/74 and compile 61/66 correct. All misses are truncations or unrun plans; no compile ANSWER is wrong.
- **Results, L0 overreach under compile** (`results/m6-compile-L0-deepseek-v4.1-flash.md`; stopped for budget after 224 calls, M-s1 only: formal 74, structured 150). Compared on the same question × representation cells with the M2 read baseline:

  | Representation | read overreach (M2) | compile, first reply | compile, final |
  |---|---|---|---|
  | formal (16 questions) | 22/48 | 25/44 | 33/44 |
  | structured (38 questions) | 28/108 | 36/114 | 45/114 |

  - Outcomes of the final reply on UNDERDETERMINED keys: **blocked 1%** (1/158 first replies called a predicate the layer lacks), **inlined** formal 75%, structured 39%, **abstained** 25% and 59%.
  - **Compile does not turn overreach into UNDERDETERMINED. It raises overreach.** The model does not call the undefined predicate; it writes the missing concept out of base relations. Examples: Q14 (cap breach) goes from 0/6 to 6/6 in formal, Q17 (not in the M2 run) 6/6, Q31/Q32 from 0/6 to 3–4/6 in structured.
    - The repair turn adds to overreach: an error on the first plan is "fixed" by inlining more.
    - Of the inlined values, 67% (formal) and 78% (structured) equal the key at the layer that defines the concept. As in M2, most overreach guesses the later definition.
  - **The static check is insufficient.** The `constructs` flag catches 39% (formal) and 47% (structured) of inlined plans, and it also fires on 20% of ANSWER-key plans (the control).
    - Many inlined plans use no aggregate at all: `( booked(C, V) -> true ; V = 0 )` for a booked total (Q11), `emp(E, Role, _), role_limit(Role, V)` for an approval limit (Q22).
    - Overreach is semantic (a base relation standing in for a concept the layer does not define), not syntactic. A check would need the IM to name the concept it computes, as a typed plan schema could.
  - **Correction to an earlier note: plans can express recursion, by unrolling it.** Q14 plans unroll the ancestor chain to a fixed depth (`cc_parent(C0, P1), cc_parent(P1, P2), ...`).
- **Compile costs more per call than read.** L0: $0.0021 per call and 3.4k reasoning tokens, against $0.0002 and 0.8k in M2 read. L2-open: $0.0017 per call. The model works the answer out and then also writes the plan; the prompt's "do not compute the answer yourself" is not followed in the reasoning trace.
- **(iii) Size: read vs compile on S-s1, M-s1, L-s1** (`results/m6-{read,compile}-L3-size-*.md`).
  - *Setup.* L3 decided, the M5 regression subset (Q01–Q05, Q11–Q17, Q21–Q26, Q91; 38 questions per world, no conflict templates), all on the same day and mostly the same provider (InferenceNet, 96%). L-s1 n=2, S-s1 and M-s1 n=1. Base facts (L0 formal, schema included): S-s1 156, M-s1 642, L-s1 1543, so L-s1 is about the size of v1's L world (1336).
  - The first S/M read comparison used M5's records, which DeepInfra served. Per-call time and cost differ between providers, so S/M read was re-run on the same day.

  | World | Mode | correct | prompt tok | reasoning tok | mean s | p90 s | cost per call |
  |---|---|---|---|---|---|---|---|
  | S-s1 | read (3 repr) | 100% | 4.5–8.0k | 620–885 | 5.9–7.9 | 11–22 | $0.00049–0.00063 |
  | M-s1 | read | 95–97% | 15–19k | 857–1,001 | 6.7–7.3 | 15–18 | $0.00072–0.00080 |
  | L-s1 | read | 97–100% | 36–42k | 1,250–1,830 | 9.2–13.8 | 19–38 | $0.00122–0.00163 |
  | S-s1 | compile (2 repr) | 97–100% | 8.6–10k | 773–1,059 | 9.3–10.5 | 21–30 | $0.00059–0.00070 |
  | M-s1 | compile | 97–100% | 22–23k | 937–979 | 8.9–10.3 | 23–26 | $0.00091–0.00096 |
  | L-s1 | compile | 95–100% | 47–49k | 987–1,269 | 8.6–11.0 | 16–33 | $0.00125–0.00162 |

  - **v1's blow-up is not replicated at this size for this model and subset.** From S to L (10× the facts), read reasoning grows about 2× and mean time about 1.6×, with no truncation and accuracy flat. v1's Sonnet runs, by contrast, took 24× the time for 17× the facts and ran out of a 64k budget.
  - Compile is flat in reasoning and time from S to L, as v1's engine arms were.
  - In both modes cost per call follows prompt length. Compile's prompt is longer (the predicate list and plan instructions), so at L it costs about the same as read.
  - Caveats: the subset has no exhaustive set-valued conflict questions (Q33/Q34 were left out on cost); one model; read at n=1–2.
  - **In M6 the blow-up came from self-contradiction, not size.** It appeared on C5 after R314: median reasoning 15.6k tokens, and every open-config CONFLICT reply truncated at 16k. Read mode's cost risk is driven by what the material does to the reasoning (an unresolvable contradiction), more than by how much of it there is.
- **score.py** gains a "Cost by world and representation" table (prompt, reasoning and completion tokens, mean/p90/max seconds, cost, truncations), and the report title names the mode.
- **Cost.**
  - My estimates were 5× too low. I sized the runs from M5's mean cost, but Q33/Q34 after R314 and all compile calls reason far longer.
  - Spent in M6: L2-open compile $0.191; set-aside pre-R314 L3 compile $0.078 (`m6-compile-L3-preR314`, superseded by the fix and not scored); C5 read $0.917 and compile $0.832; L0 compile $0.479. M6 total about $2.50.
  - Size runs (iii): L-s1 read $0.33, S/M read $0.15, L-s1 compile $0.22, S/M compile $0.12; $0.82 in total.
  - Running total **$7.31 of $10**, $2.69 left for M7.
