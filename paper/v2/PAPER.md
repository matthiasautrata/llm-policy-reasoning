# Layers of Meaning: Which Layer Does a Question Need, and How Should a Model Use It?

**Schema, ontology, context and warrant layers in text, YAML and Prolog, read in context or compiled to engine plans**

Matthias · Technical report · November 2026

## Abstract

v1 of this study found that, for policy questions, written interpretation decisions matter more than notation, and that a deterministic engine earns its place at scale. It left translation unmeasured, and with it the question of *what material a question needs*. v2 splits the material of a synthetic procurement organisation into four cumulative layers: schema (L0), ontology (L1), context (L2) and warrant (L3). Each layer is rendered in three representations: Markdown, YAML and Prolog. Machine-checked keys give every question a minimum layer, below which the correct answer is UNDERDETERMINED. A flash-tier model (DeepSeek V4.1 Flash) answered 8,198 calls, either in read mode (material in context) or in compile mode (it writes Prolog plans that an engine validates and runs). We test five hypotheses:

- **The layer step (H1) is confirmed.** On questions that need L1, accuracy goes from 39% (170/432) with L0 alone to 99% (501/504) with L1. Below the needed layer, every error is overreach, and most overreach guesses the definition that a later layer will give.
- **Representation (H2) matters less than layer presence.** With the right layer present, ANSWER keys are 99–100% correct in every representation. Representation moves the abstention boundary, and at about 1.5k facts it shows in cost and time but not in accuracy.
- **Compile mode (H3) wins on contradiction.** It reaches 29/30 on rule-level CONFLICT keys, against 5/24 for read. It ties read at L size, and its errors move into the plan's shape. But it *raises* overreach when the needed layer is absent.
- **The criterion (H4) is falsified as stated.** Read failures do not concentrate on defeasible or deontic rules (286/288 correct). They concentrate on contradictions, both in the data and between rules.
- **Small model plus engine (H5) is confirmed.** DeepSeek in compile mode matches a larger model (GLM-5.3) in read mode where the material is consistent (82/84 each), and beats it on the rule-level contradiction (29/30 vs 9/20). It costs 2–3.5× less per call. GLM resolves half of the contradictions silently.

The whole programme cost $8.11.

## 1 Introduction

A question to a policy system carries an unstated requirement: what must be on the table before it can be answered. "Which cost centre does e077 belong to?" needs only the tables. "What is the booked total of cc2?" needs a definition: does the total include descendants? "Which cost centre did e077 belong to on 2026-03-05, according to finance?" needs dated, sourced claims. "May m approve request r?" needs owned rules that license conclusions the facts do not contain.

v1 [11] asked whether notation matters and when an engine is needed. v2 asks **which layer of meaning a question needs, and in which representation and mode a model uses it reliably.** The design makes the layers explicit, keys each question at each layer, and measures what a model does when the layer it needs is present and when it is absent.

Five hypotheses were fixed before the runs (§3 of `REWORK.md`):

**H1 Layer step.** Accuracy on questions with minimum layer k jumps when layer k is present. Below k, overreach (an answer instead of UNDERDETERMINED) is the dominant error.

**H2 Representation.** In read mode, representation matters less than layer presence at small scale. At scale it re-enters through length.

**H3 Mode.** Compile is at least as good as read at scale and on L3. Errors move to translation, where they can be measured.

**H4 Criterion.** Read-mode failures concentrate on rules that are non-conservative, defeasible or deontic (L3), not on conservative ones.

**H5 Small + engine.** A small model in compile mode matches or beats a large model in read mode.

**Contributions.**
(i) A layered benchmark. Its keys are computed by a SWI-Prolog engine and cross-checked by an independent Python reference: 3,600 keys (9 worlds × 50 questions × 4 layers × 2 configurations), with proof trees that re-verify.
(ii) Evidence for a layer step and for overreach as the error below the step, with counts for each layer.
(iii) A characterisation of compile mode. It closes rule-level contradictions that read mode cannot, it does not reduce overreach, and its errors are in the plan's shape.
(iv) A refinement of the conservative/non-conservative criterion. The hard case is contradiction, not defeasibility.

## 2 Related work

*Reasoning over rules in language.* RuleTaker [1] and ProofWriter [2] showed that transformers can emulate deduction over natural-language rules. Dziri et al. [3] show that errors compound over the number of reasoning steps. BoardgameQA [4] studies contradictory information with preferences, the analogue of our C5 contradiction without precedence.

*Long context.* Usable context is shorter than nominal context [5, 6], and much shorter when question and evidence share no literal cue [7]. We test this at 0.16k–1.5k facts.

*Solver-augmented models.* Logic-LM [9] and LINC [10] have the model translate the problem into a formal language and delegate inference to a solver. Our compile mode does the same with the rules given and the plan language fixed, so that translation errors can be counted separately. v1 used Soufflé [8]; v2 uses SWI-Prolog with tabling.

## 3 Materials

**Worlds.** One generator produces 9 worlds: sizes S, M and L × 3 seeds. Every world contains cost centres in a tree, employees, a reporting chain, requests, vendors, bookings, caps, role limits and org units. Measured as base facts (L0 formal, schema included), S-s1 has 156, M-s1 642 and L-s1 1,543. The runs use S-s1–3 and M-s1, plus L-s1 for the size curve.

**Layers.** The layers are cumulative, and each adds what the next kind of question needs:

| Layer | Adds | Example rule classes |
|---|---|---|
| L0 schema | tables, columns, types, keys | — |
| L1 ontology | concepts and definitions (ancestors, booked total, headroom), forks c1, c3, c4, c6 | definitional |
| L2 context | dated rule versions, vendor status periods, `today`, two disagreeing sources (HR vs finance), fork c2 | temporal, fitness |
| L3 warrant | approver eligibility, vendor check with exception and exception-to-exception, denial, auto-approval, precedence of finance (R313), incompatibility (R314) | entitlement, defeasible, material inference, incompatibility |

There are 38 rule records. Each carries layer, class, a `conservative` flag, an owner, English text and a Prolog clause.

**Representations.** All three are generated from one source: text (Markdown tables plus handbook prose), structured (YAML relations, concepts and rule records) and formal (a Prolog program with rule metadata as facts).

**Configurations.**
- *Decided* states one reading for every fork.
- *Open* lists every reading of every fork and decides none. Its keys are AMBIGUOUS wherever the readings differ.

**Statuses.** ANSWER, AMBIGUOUS, CONFLICT (the material contradicts itself and nothing gives precedence), UNDERDETERMINED (the layers present do not settle it) and OUT_OF_SCOPE.

**Questions.** There are 25 templates × 2 instances = 50 questions per world. Each has a kind (fact, structure, permission, fitness, explain), a type (bool, int, sym, set) and a minimum layer:
- min_layer 0: Q01–Q05, Q91 (controls);
- min_layer 1: Q11–Q17;
- min_layer 2: Q21–Q26;
- min_layer 3: Q31–Q36.

Every question has a key at every layer. Below its minimum layer the key is UNDERDETERMINED.

**Two planted contradictions.**
- *Q25* (which cost centre an employee belonged to on a date) is CONFLICT at L2 wherever HR and finance disagree: 45 of 72 instances in the run worlds. At L3, R313 resolves it in favour of finance.
- *C5* is a rule-level contradiction: a denied request that also qualifies for auto-approval. It is CONFLICT at L3 on Q33 ("is request r approved?") and Q34 (approved requests in a subtree). It is real by construction because of R314, `excluded(approved(R)) :- denied(R)`. The engine detects it by comparing the program with its exclusion-enforced variant M−: if a goal's value differs, the rule base derives both G and excluded(G).

**Keys and checks.**
- Keys are computed by the Prolog engine, which tables recursive predicates and uses `tnot/1` for negation.
- A plain-Python reference reproduces every key: 3,600 keys, decided and open, at all layers.
- A formal check runs plain Prolog on each rendered `formal.pl`.
- For L3 "why" questions, a meta-interpreter returns a proof tree and every tree re-verifies by re-running its leaves: 1,785 trees (S-s1), 6,234 (M-s1) and 10,857 (L-s1), with 0 failures.
- `make verify` fails on any disagreement.

## 4 Method

**Read mode.** The system prompt holds the layer's material and the five statuses. It never mentions layers: a model at L0 is not told that more material exists, only not to answer beyond what it was given. The reply ends in one JSON line with status, value, readings and missing. Two variants add a required list:
- `assume` asks for the assumptions the reply depends on;
- `explain` asks for the ids of the rules applied, graded against the proof tree.

**Compile mode.** The model returns at most 3 plans, each `{readings, goal}`, where the goal is a Prolog goal over the layer's declared predicates and a whitelist of built-ins. The engine then:
1. validates each plan statically (predicates exist at this layer, no side effects, bounded execution);
2. runs it, expanding any open forks the plan leaves unfixed;
3. aggregates: one distinct value gives ANSWER, several give AMBIGUOUS;
4. checks for contradiction in M− (engine-detected CONFLICT).

Errors get one repair turn. A reply whose plans never run is scored as a parse failure. Compile is offered for formal and structured only, since text has no declared predicates.

**Models and settings.**
- *Main model:* DeepSeek V4.1 Flash (`deepseek/deepseek-v4.1-flash`) through OpenRouter, fp8, sorted by price. It was served by Baidu, DeepInfra and InferenceNet; the provider is recorded per call.
- *Comparison models:* GLM-5.3 (`z-ai/glm-5.3`, Novita, fp8, effort high), and Qwen3.8 Flash (`qwen/qwen3.8-flash`, Alibaba, effort medium) in an L0 model comparison.
- *Settings:* temperature 1.0, DeepSeek reasoning effort medium, max_tokens 16,000.

**Scoring.**
- *Correct* means the status is right, plus the value for ANSWER keys and the reading values for AMBIGUOUS keys.
- *Overreach* is an ANSWER on an UNDERDETERMINED key.
- *Lucky* means an overreaching value that equals the key at the question's minimum layer: the model guessed the later definition.
- *Lenient abstention* accepts UNDERDETERMINED and OUT_OF_SCOPE for each other.

**Scope.** Each milestone ran the new layer's questions plus a fixed regression subset of 19 templates (Q01–Q05, Q11–Q17, Q21–Q26, Q91), at n = 1–3. Under a $10 cap, the paper reports these subsets, not a full worlds × layers × representations × modes × reps matrix (§7).

## 5 Results

### 5.1 H1: the layer step

The table pools the decided read runs (base prompt, DeepSeek). Rows are grouped by the key's minimum layer; columns give the layer shown.

| min_layer | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| 1 | **39%** (170/432) | **99%** (501/504) | — | — |
| 2 | 53% | **50%** (72/144) | **90%** (387/432) | 100% |
| 3 | 85% | 58% | **69%** | **90%** (390/432) |

Overreach on keys below their layer, with the lucky share in parentheses:

| min_layer | at L0 | at L1 | at L2 |
|---|---|---|---|
| 1 | 60% (65% lucky) | — | — |
| 2 | 19% (92%) | 50% (100%) | — |
| 3 | 14% (68%) | 20% (83%) | 26% (68%) |

- **The step is large for k = 1 and k = 2.** On min_layer 1 keys, L0 → L1 is 39% → 99%. By representation, the L0 rates are 49% formal, 40% structured and 31% text; all reach 99–100% at L1. On min_layer 2 keys, L1 → L2 is 50% → 90%.
- **Below the step, every error is overreach.** In M2, every wrong status on an UNDERDETERMINED key was ANSWER or OUT_OF_SCOPE. Under lenient abstention, which accepts OUT_OF_SCOPE, every remaining error is an ANSWER.
- **Most overreach is lucky.** The model fills the missing definition with the reading the next layer will state, which is also the usual business reading. An extreme case: at L1, all 72 Q22 answers (the applicable approval limit) are overreach, and every one equals the L2 key, because the L1 guess and the L2 definition give the same number. Accuracy on such questions cannot tell understanding from a good guess. Only the status can.
- **For k = 3 the step depends on the representation.** At L2, min_layer 3 keys score 42% in text (28 ANSWERs), 83% in structured and 98% in formal. Formal already abstains at L2, so it has no step to show. L3 then lowers every representation to about 90–91%, because the C5 conflicts sit there (§5.3).
- **Partial material raises overreach.** For min_layer 3 questions it grows from 14% (L0) to 20% (L1) and 26% (L2). In text at L2, Q31 ("may m approve r?") is answered 23 of 24 times. The more relevant-looking material there is, the more often the model assembles an answer from it.

**Verdict: H1 confirmed for k = 1 and k = 2. For k = 3 it is confirmed in text and structured, and not visible in formal.** Below the step, overreach is the only error.

*The error is noticed in the trace, not in the reply.* An overreaching ANSWER whose reasoning matches a keyword list of ambiguity and missing-definition terms is counted as noticed but answered. That covers 89% of the 401 M2 overreaches, against an 11% control rate. The visible reply flags it in 2/401. This calibration is model-specific: GLM-5.3 scores 35–47% (control 0–4%), and Qwen's traces use the keywords everywhere (control 43–57%). So "noticed but answered" is a DeepSeek finding.

*Asking for assumptions does not produce abstention.* With a required `assumptions` list, overreach on min_layer 1 keys falls only from 67% to 59%, and 93–96% of overreaching ANSWERs list the assumption they made: for example, "'booked total' is read as the amount booked directly on the cost centre". Overreach becomes stated assumption rather than abstention.

*A stronger model overreaches more.* On 11 templates at L0, overreach on min_layer 1 keys is 96% for GLM-5.3, 74% for DeepSeek and 69% for Qwen. Their accuracy on ANSWER keys is 96–99%.

### 5.2 H2: representation

Correct, pooled decided read:

| Layer | formal | structured | text |
|---|---|---|---|
| L0 | 71% | 70% | 66% |
| L1 | 89% | 91% | 87% |
| L2 | 92% | 91% | 85% |
| L3 | 95% | 95% | 95% |

- **ANSWER keys are 99–100% correct in every cell.** Representation does not affect whether the model reads a settled answer correctly.
- **Representation moves the abstention boundary.**
  - Text overreaches most: at L0 on min_layer 1 keys, 35% text, 30% structured and 28% formal.
  - The wording of the material changes which status the model picks. In the L1-open formal material, a comment saying that "nothing that depends on an open question is derived" gave 16% correct. Rewording it to say that the readings are alternatives the material allows gave 87%.
  - At L2, Q25 data conflicts were filed as AMBIGUOUS with both sides (35/45) rather than as CONFLICT, in every representation. Only AMBIGUOUS has a slot in the answer format for two values. These are status-boundary effects, not reading errors.
- **Size: little effect at 1.5k facts.** Read L3 decided on the 19-template subset, per world:

| World | facts | correct | prompt tok | reasoning tok | mean s | cost per call |
|---|---|---|---|---|---|---|
| S-s1 | 156 | 100% | 4.5–8.0k | 620–885 | 5.9–7.9 | $0.00049–0.00063 |
| M-s1 | 642 | 95–97% | 15–19k | 857–1,001 | 6.7–7.3 | $0.00072–0.00080 |
| L-s1 | 1,543 | 97–100% | 36–42k | 1,250–1,830 | 9.2–13.8 | $0.00122–0.00163 |

At L-s1, formal (38k tokens) scores 100% at 9.2 s per call, structured (42k) 97% at 13.8 s, and text (36k) 97% at 11.7 s. From S to L, about 10× the facts, reasoning grows about 2× and time about 1.6×, with no truncation. v1's Sonnet runs took 24× the time for 17× the facts.

**Verdict: H2 confirmed at small scale. "Re-enters through length" is only weakly supported:** the longest representation is the slowest and costliest, but accuracy does not change at 1.5k facts. The size test stops at about v1's L world (1,336 facts); larger worlds were not run.

### 5.3 H3: compile vs read

| Comparison | read | compile |
|---|---|---|
| C5 CONFLICT keys, L3 decided (M-s1, S-s1–3, Q33/Q34) | 5/24 (8 side picked, 11 truncated) | **29/30** (9 engine-detected) |
| Size curve, all worlds (calls; errors) | 456; 8 wrong values | 304; 6 unrun plans, 0 wrong values |
| L-s1 formal / structured | 76/76, 74/76 | 72/76, 76/76 |
| L2 open, formal / structured | 93%, 96% | 88%, 95% |
| L0 overreach, formal | 22/48 | **33/44** |
| L0 overreach, structured | 28/108 | **45/114** |

- **On a rule-level contradiction, compile wins clearly.**
  - In read mode the C5 contradiction is often noticed but cannot be closed. Median reasoning on CONFLICT keys is 15.6k tokens, against 2.3k on ANSWER keys of the same run. In the open configuration every CONFLICT reply hit the 16k output cap. v1 found this failure mode with size; here it comes from self-contradiction.
  - Compile closes it at a median of 6.7k reasoning tokens. Most CONFLICTs the model declared itself; the rest the engine detected in plans that asked for approval directly. No compile reply picked a side.
- **At L size the modes tie.** Compile is flat in reasoning and time from S to L, as v1's engine arms were. Its cost per call follows its longer prompt (the predicate list), so at L it costs about the same as read.
- **The errors move into translation, and they are errors of shape.**
  - Every compile error in the size runs is a plan that never ran; no plan that ran gave a wrong value. Read's errors are wrong values: for example, an employee's earlier cost centre read from the assignment history (Q03, Q15).
  - Of the 62 first-pass errors in L2-open compile, 30 were "V not bound" (a value question whose goal binds nothing), 28 were a list given as one value, 3 were too many plans and 1 had no JSON. That is 58/62 in the plan's shape, not its logic.
- **Compile raises overreach when the layer is absent.** At L0 the model does not call the undefined predicate, which validation would catch: only 1% of first replies were blocked. It writes the missing concept out of base relations instead: `( booked(C, V) -> true ; V = 0 )` for a booked total, `emp(E, Role, _), role_limit(Role, V)` for an approval limit. The repair turn makes this worse, because an error is "fixed" by inlining more. As in read mode, 67% (formal) and 78% (structured) of the inlined values equal the later key. A static flag on aggregation and arithmetic built-ins catches 39–47% of inlined plans, and it also fires on 20% of legitimate ones.
- **Divergent execution surfaced no fork the model had not already split on itself** (0% engine-only, L2 open).

**Verdict: H3 confirmed on L3 contradiction (29/30 vs 5/24) and on errors moving to translation (all compile errors are in plan shape). At scale it is a tie, not a win. It is refuted for abstention:** compile raises overreach at L0 (formal 33/44 vs 22/48).

### 5.4 H4: where read mode fails

Read errors at or above the question's minimum layer (DeepSeek, decided):

| Layer shown | n | errors | of which on CONFLICT keys |
|---|---|---|---|
| L0 | 360 | 3 | 0 |
| L1 | 864 | 6 | 0 |
| L2 | 720 | 52 | 45 (Q25: 35 AMBIGUOUS with both sides, 10 UNDERDETERMINED) |
| L3 | 864 | 45 | 40 (Q33/Q34 C5: 36 ANSWER, 4 parse) |

- **85 of 106 errors are on CONFLICT keys.** On the L3 templates whose keys follow from the defeasible and deontic rules, read mode is nearly perfect: Q31 permission 72/72, Q32 vendor check with exception and exception-to-exception 72/72, Q35 denial 72/72, Q36 cap check 70/72. That is 286/288. Q33 scores 64/72 and Q34 40/72, and their misses are the C5 conflicts.
- **The concentration replicates in a second model family.** On the C5 cells, GLM-5.3 misses 11 of 20 CONFLICT keys and 1 of 44 other keys of the same templates (§5.5).
- **The two contradictions behave differently.** The data conflict, Q25, was always noticed: no reply picked a side, and the miss is the status label. The rule conflict, C5 before R314, was resolved silently:
  - *By the reader:* R312 "an automatically approved request is approved" was read as a second sufficient condition, and R310's "denial overrides eligibility" as scoped to eligibility.
  - *By the formalism:* formal gave 15/15 ANSWER, because two clauses for `approved/1` are a union under program semantics. A formal rule set resolves an unstated precedence by construction. It needs an explicit incompatibility (R314) for the contradiction to exist at all.
- **Below the layer the gradient runs the other way.** Overreach is highest on the conservative L1 concepts (60% at L0), against 19% and 14% for min_layer 2 and 3 keys at L0. A conservative definition is easy to guess, and the guess is usually the stated one (65% lucky).
- **Explanation does not single out L3.** With the `explain` prompt, all 306 answers are correct, and core recall of the proof's rules is 0.97 in each representation. By class: L1 definitional 94%, L2 temporal 91%, L2 fitness 100%, L3 definitional 67% (18/27), material inference 75%, defeasible 88%, entitlement 88%, incompatibility 100%. The misses lie along the long chains, not on one class.

**Verdict: H4 falsified as stated.** Read mode does not fail first on non-conservative, defeasible or deontic rules: 286/288 on the L3 templates without conflicts. It fails on contradiction, both in the data (Q25) and between rules (C5). Below the needed layer, it overreaches most on conservative concepts. The criterion that predicts difficulty is *whether the material is consistent*, not whether a rule is conservative.

### 5.5 H5: small model + engine vs larger model reading

Same 84 cells: M-s1, L3 decided, the 19-template subset plus Q33/Q34, formal and structured, rep 0.

| Arm | correct | formal | structured | cost per call | mean s |
|---|---|---|---|---|---|
| GLM-5.3, read | **82/84** | 40/42 | 42/42 | $0.0036–0.0048 | 7.5–9.5 |
| DeepSeek V4.1 Flash, compile | **82/84** | 40/42 | 42/42 | $0.0014–0.0017 | 13–20 |
| DeepSeek V4.1 Flash, read | 79/84 | | | | |

- GLM's two errors are the same Q03/Q15 history misreadings that DeepSeek makes in read mode; the keys were rechecked against the material. One of DeepSeek compile's errors is a plan-shape error (`V = []` for a set). DeepSeek read lost the two Q34 CONFLICT cells to truncation.
- On these 84 cells GLM's median reasoning was about 100 tokens. Its two CONFLICT cells were both correct, at 7–14k tokens (86–174 s, $0.018–0.032 each).

The 84 cells hold only 2 CONFLICT keys, so GLM was also run on all C5 cells: Q33/Q34 on M-s1 and S-s1–3, formal and structured, n = 2, the same cells as DeepSeek's C5 runs (§5.3).

| Arm (C5 cells) | CONFLICT keys | formal | structured | other keys | median reasoning on CONFLICT | cost per call, CONFLICT / other |
|---|---|---|---|---|---|---|
| GLM-5.3, read (n = 2) | **9/20** | 6/10 | 3/10 | 43/44 | 4.7k tok, 64 s | $0.0140 / $0.0058 |
| DeepSeek, compile (n = 3) | **29/30** | 15/15 | 14/15 | 61/66 | 6.7k tok, 55 s | $0.0039 / $0.0027 |
| DeepSeek, read (n = 3, cap-stopped) | 5/15 | 3/6 | 2/9 | 43/47 | 15.8k tok, 86 s | $0.0092 / $0.0033 |

- **The larger model resolves the contradiction silently instead of truncating.** GLM answers 10 of the 20 CONFLICT cells with a value. 8 of the 10 take the side on which denial wins, the value of the exclusion-enforced program M−, as if R314 had precedence. The other 2 match neither side. Only 1 of 20 hit the output cap, against 7 of 15 for DeepSeek read. DeepSeek read fails by reasoning until it is cut off; GLM fails by picking the plausible business reading, as at L0 (§5.1).
- DeepSeek compile's misses on the other keys are unrun plans (4) and one engine-side CONFLICT on an ANSWER key. GLM's one miss is a formal misreading.
- Over all its reps on these M-s1 cells (100 records), DeepSeek compile scores 96/100.

**Verdict: H5 confirmed.** The small model with the engine matches the larger model where the material is consistent (82/84 vs 82/84; other C5-template keys 61/66 vs 43/44). It beats the larger model on the rule-level contradiction (29/30 vs 9/20), at 2–3.5× lower cost per call. Neither arm is better at abstaining: at L0, where the needed layer is missing, GLM overreached more than DeepSeek in read mode (96% vs 74%), and DeepSeek compile overreaches more than DeepSeek read (§5.3).

### 5.6 Summary

| Hypothesis | Verdict | Key counts |
|---|---|---|
| H1 layer step | confirmed (k = 1, 2); for k = 3 in text and structured only | 170/432 → 501/504; 72/144 → 387/432; below the step every error is overreach, 65–100% lucky |
| H2 representation | confirmed at small scale; length effect only in cost and time | ANSWER keys 99–100% in all representations; L-s1 97–100% |
| H3 mode | confirmed on contradiction and on error location; tie at scale; refuted for abstention | C5 29/30 vs 5/24; size: 0 wrong values in compile; L0 overreach 33/44 vs 22/48 |
| H4 criterion | falsified; refined to contradiction | 85/106 read errors on CONFLICT keys; L3 non-conflict templates 286/288 |
| H5 small + engine | confirmed: matches on consistent material, beats on contradiction | 82/84 vs 82/84; C5 CONFLICT 29/30 vs 9/20; 2–3.5× lower cost per call |

## 6 Discussion

**Layers are not decoration, but a missing layer is invisible to the model.** The step in H1 is the clearest result. So is its counterpart: without the layer, the model rarely abstains. It fills the gap with the most usual definition, and usually guesses right. Accuracy on such questions overstates understanding; the status is the informative signal. Neither asking for assumptions nor giving a stronger model fixes this. An organisation that wants abstention has to supply the layer, or check at the system level that a definition was supplied.

**Compile mode is not an abstention mechanism.** One might hope that an engine that refuses unknown predicates would turn overreach into UNDERDETERMINED. It does not, because the model writes the missing concept out of base relations. Overreach is semantic, not syntactic. A validator could only catch it if the plan had to name the concept it computes, so that the concept could be checked against the layer's capabilities. That argues for a **typed plan schema**: a data AST that names the concept and declares its output kind (scalar, set or bool). It would also remove the 58/62 shape errors. It was not built in v2.

**Contradiction is the hard case for reading, and the engine's strongest case.** v1 located the engine's advantage in size. v2 finds that at 1.5k facts size costs time but not accuracy. A self-contradiction, by contrast, produces long reasoning and truncation in read mode (DeepSeek), or a silently chosen side (GLM-5.3, 10/20 answered, 8 of them with denial winning). Compile mode turns contradiction into a mechanical comparison (M vs M−), which the model does not need to carry out. The rule-level result also has a design consequence: in a formal rule base, an unstated precedence between two sufficient conditions is resolved silently as a union. Contradiction must be declared (an incompatibility rule) before an engine can find it.

**The division of labour from v1 holds, with a refinement.** The model interprets and plans; the engine evaluates and checks consistency. But the model also decides whether the material suffices, and both modes do that badly.

## 7 Threats to validity

- **One main model, several providers.** Almost all calls are DeepSeek V4.1 Flash. They were served by Baidu, DeepInfra and InferenceNet at fp8, and provider is recorded but not balanced. The size curve was re-run on one day, mostly on one provider (96%), to remove this confound there.
- **Small n and subsets.** Most cells are n = 1–3. Under the $10 cap the full matrix was not run. Each milestone ran its new questions plus the 19-template regression subset; compile mode at L0 covers M-s1 only, and the size curve covers one L world.
- **Runs stopped at caps.** Three of the four C5 runs and the L0 compile run stopped at their budget caps, so their cells are unbalanced: for example, read decided 98/144 cells, compile open 45/96.
- **H5 rests on one pair of models.** GLM-5.3 ran at n = 1 on the 84 subset cells and at n = 2 on the 64 C5 cells (20 of them CONFLICT keys). DeepSeek compile's C5 cells are n = 3 from M6, run on a different day.
- **Template choice.** The L0 model comparison used 11 templates chosen from DeepSeek's M2 overreach, which favours finding overreach for DeepSeek. GLM still overreached more.
- **Size.** L-s1 has 1,543 facts. Effects of length beyond that are untested.
- **Heuristics.** "Noticed but answered" is a keyword heuristic, with a per-model control rate.
- **Answer format.** The format creates status-boundary effects: Q25 was filed as AMBIGUOUS for want of a slot for two values. A `sides` field for CONFLICT would need a new baseline.
- **Construct.** The worlds are synthetic, the domain is one, and the questions come from templates. The layer boundaries follow the stated criterion (§3 of `REWORK.md`), which is itself what H4 tests.

## 8 Conclusions and future work

When a question needs a layer of meaning, providing that layer is what makes it answerable. Without it, a model answers anyway, usually with the right guess, in every representation and in both modes. Representation matters at the boundary of abstention, not in reading. Compile mode earns its place on contradiction and consistency, and it lets a flash-tier model match a larger one on consistent material, and beat it on contradiction, at 2–3.5× lower cost per call. It does not make a model abstain.

Next steps:
- a typed plan schema that names the computed concept and its output kind, so that overreach and shape errors can be checked before execution;
- a CONFLICT `sides` field in the answer format;
- the full matrix with a second model family at n ≥ 3;
- worlds well beyond 1.5k facts;
- a scoring category for "ANSWER with a stated assumption naming the missing definition".

## Reproducibility

The repository holds the generator, rule records, renderers, engine, Python reference, question bank, harness, every world used, every raw record (`results/*.jsonl.gz`) and the scored reports (`results/*.md`). `make verify` regenerates every world and checks every key against the reference. `harness/score.py <run>.jsonl --report <run>.md` rescores a run. Runs used OpenRouter at a total of $8.11 for 8,878 records: DeepSeek 8,198 records ($6.37), GLM-5.3 416 ($1.23) and Qwen3.8 Flash 264 ($0.51). The cost of each run is listed in `REWORK.md`, Decisions.

## References

[1] P. Clark, O. Tafjord, K. Richardson. Transformers as Soft Reasoners over Language. *IJCAI* 2020.

[2] O. Tafjord, B. Dalvi, P. Clark. ProofWriter: Generating Implications, Proofs, and Abductive Statements over Natural Language. *Findings of ACL-IJCNLP* 2021.

[3] N. Dziri et al. Faith and Fate: Limits of Transformers on Compositionality. *NeurIPS* 2023.

[4] M. Kazemi et al. BoardgameQA: A Dataset for Natural Language Reasoning with Contradictory Information. *NeurIPS Datasets and Benchmarks* 2023.

[5] N. F. Liu et al. Lost in the Middle: How Language Models Use Long Contexts. *TACL* 12, 2024.

[6] C.-P. Hsieh et al. RULER: What's the Real Context Size of Your Long-Context Language Models? *COLM* 2024.

[7] A. Modarressi et al. NoLiMa: Long-Context Evaluation Beyond Literal Matching. *ICML* 2025.

[8] H. Jordan, B. Scholz, P. Subotić. Soufflé: On Synthesis of Program Analyzers. *CAV* 2016.

[9] L. Pan, A. Albalak, X. Wang, W. Y. Wang. Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning. *Findings of EMNLP* 2023.

[10] T. X. Olausson et al. LINC: A Neurosymbolic Approach for Logical Reasoning by Combining Language Models with First-Order Logic Provers. *EMNLP* 2023.

[11] v1 of this report: *Rules in Context: When Should a Language Model Evaluate a Policy Itself?* Technical report, September 2026. `paper/v1/PAPER.md`, git tag `v1`.
