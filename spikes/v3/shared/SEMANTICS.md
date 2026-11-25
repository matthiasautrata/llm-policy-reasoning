# Semantics: ambiguity propagation over an acyclic rule base (PLAN-v3-integrity §4.1)

This replaces the Y5 decision of `SEMANTICS-cycles.md`, which was ambiguity blocking. Everything downstream of a contested conclusion is now contested. `reference.py` (`Prop`, `answer_acyclic`) implements this independently of every spike.

Under the old semantics, available behind `reference.py --semantics blocking`, the retired engine modes (V3a `wfs`, V3e doubled encoding) keep their old keys.

## Precondition

The rule base is acyclic: the integrity gate rejects a defeat cycle at load, on `add`, and inside `with_hypothesis` (IR-001a). Superiority is a strict partial order (IR-001b). Evaluation is therefore stratified, and bottom-up and top-down evaluation give the same values.

## Values

Ground the theory as before:
- rules and defeaters;
- claims in force on `as_of`;
- superiority: explicit `:superior-to`, then authority rules `:pred`/`:order` (R313, RY4), then later `asserted_at` for the same asserter (claims only), then strict over non-strict.

A **claim** is a rule with an empty body. `depends_on` adds its member claims to that body; `supports` adds nothing.

For a literal L:
- its **supporters** are the non-defeater rules and claims with head L;
- its **attackers** are the rules, defeaters and claims with head ~L, plus, for a functional predicate (`cost_centre_of`), the claims of another value for the same key.

Each literal is **proven**, **refuted** or **contested**.

**Bodies and builtins**
- A body (conjunction) is refuted if any literal in it is refuted, proven if all are proven, and contested otherwise.
- Fetches, builtins and `as_of` are proven or refuted (facts).
- A comparison or arithmetic literal over a contested binding is contested: the binding comes from a contested literal earlier in the body, so the body is contested already.
- `[:not L]` is proven if L is refuted, refuted if L is proven, and contested if L is contested.

**Live and beaten**
- A supporter or attacker is **live** if its body is not refuted.
- A live attacker a of L is **beaten** if some live supporter t of L with **t > a** has a **proven** body. This is team defeat: different attackers may be beaten by different supporters. A superior supporter with a contested body does not beat, so the conflict stays open.

**L itself**
- **Refuted** if every live supporter t is beaten by some live attacker a > t with a proven body. This holds vacuously when no supporter is live.
- **Proven** if some live supporter has a proven body and every live attacker is beaten.
- **Contested** otherwise. That covers two cases:
  - a proven-bodied supporter meeting a live unbeaten attacker: the old "blocked" CONFLICT (C3/C4, R312/R314, Y1, RY21/RY23);
  - every live supporter, or the unbeaten attacker, resting on a contested body literal: downstream propagation (Y5a, Y5c, Y5d, Y5e).

**Measures and strict rules**
- A **measure** over a set with a contested member is contested. In the slice's rule language a measure is a fetch keyed by a binding, so a fetch whose key comes from a contested literal is contested (RY56, Y5e).
- An open goal (`[:home_budget "e077" ?v]`) is contested if any of its candidate instances is contested. Otherwise its value is the set of proven instances.
- **Strict** rules propagate the same way. The slice has no strict rule whose body can be contested.

## Mapping to statuses

| Value of the goal | Status | Sides |
|---|---|---|
| proven | ANSWER (true, or the value) | none |
| refuted | ANSWER false (or `[]` for an open goal), as before | none |
| contested at a **root** (a proven-bodied live supporter meets a proven-bodied live unbeaten attacker) | CONFLICT | `[[those supporters], [those attackers]]`, unchanged from the earlier slice semantics |
| contested **downstream** | CONFLICT | the sides of every root conflict reached by following contested body literals, deduplicated and sorted |

`UNDERDETERMINED` and `OUT_OF_SCOPE` are unchanged.

## Why tree for a downstream CONFLICT

The why tree has one node per contested ground instance of the goal:

```
{type: "contested", goal, via: [literals], rules: [ids], roots: [conflict nodes]}
{type: "conflict",  goal, sides, children: [proof nodes of the side members]}
```

- **`via`**: every contested literal reached from `goal` through contested body literals of live supporters and live unbeaten attackers, roots included. `[:not L]` is listed as L, and a `depends_on` member as its assertion.
- **`rules`**: the ids of the live supporters and live unbeaten attackers of `goal` and of every non-root `via` literal.
- **`roots`**: one `conflict` node per root literal, sorted by goal.

A root CONFLICT keeps its current why tree, the list of side proofs.

`check_why.py` compares `via`, `rules` and each root's `{goal, sides}` with the reference exactly, and verifies the children of every conflict node as ordinary proofs.

Claims follow the same rule. A claim whose `depends_on` member is contested has standing `contested`; before, that would have been `rebutted` without a defeater. A `supports` member still only adds a qualifier. No slice claim reaches that case, because C1.2 is beaten by the later C6, so keys do not change there.

## Which published semantics this is

This is the **ambiguity-propagating defeasible logic with team defeat**, with the tags +δ/−δ (propagating provability) and +σ/−σ (support).

The definitions were read in Maher, *Relative Expressiveness of Defeasible Logics II*, arXiv 2102.10532, Appendix B. Billington et al. (2010) is cited there as the origin of the framework.

| Here | DL tag |
|---|---|
| proven | +δ |
| refuted | −σ |
| contested | +σ and −δ |
| live (body not refuted) | the body has no −σ literal, the escape clause (2c-i) of +δ |
| beaten | beaten by some t ∈ R_sd[q] with t > s and a +δ body, clause (2c-ii) of +δ |
| refuted (each live supporter beaten by some superior attacker with a proven body) | −σ (2): each r fails on a −σ body literal or meets some s > r with a +δ body |

### Confirmed (read in the source)

- The +δ, −δ, +σ and −σ inference conditions, read in Maher 2021, Appendix B:
  - **+δq**: some strict or defeasible rule for q has a +δ body; −Δ~q holds; and every rule s for ~q either has a −σ body literal or is beaten by some rule t for q with t > s and a +δ body.
  - **−σq**: every rule r for q either has a −σ body literal, or meets some s for ~q with a +δ body and s > r.
- Team defeat is the ∀s / ∃t shape. The starred variants δ*, σ* drop it.
- The inclusion chain +Δ ⊆ +δ* ⊆ +δ ⊆ +∂ ⊆ +σ ⊆ +σ* is stated in Maher 2021 and attributed to Billington, Antoniou, Governatori and Maher, *An inclusion theorem for defeasible logics*, ACM TOCL 12(1), 2010.
- From SEMANTICS-cycles.md (Maier, arXiv 1106.1957): ambiguity propagation is what the WFS of the direct translation already gives. Ambiguity blocking needed the metaprogram.

### Assumed (not verified against the sources)

- **Who introduced δ/σ.** The fetched text does not say. Candidates are Antoniou, Billington, Governatori and Maher, *A flexible framework for defeasible logics*, AAAI 2000, and Maier & Nute, JELIA 2006. Neither was read.
- **Defeaters.** Defeaters count as attackers (R[~q]) but never as supporters (R_sd[q]), as in standard DL.
- **Extensions this spike adds beyond the published logics.** No published result covers them:
  - superiority built from authority rules and `later` asserted_at;
  - functional rivals as attackers;
  - claims as empty-body rules gated by valid time, with `depends_on` as body literals;
  - measures and open goals being contested when any instance is.
- **The three-way mapping onto CONFLICT.** Contested = +σ −δ. The −Δ~q clause has no work to do: there are no strict conflicts.

## Literature

- Maher, M. J. *Relative Expressiveness of Defeasible Logics II*. arXiv:2102.10532. Appendix B was read.
- Billington, D., Antoniou, G., Governatori, G., Maher, M. J. *An inclusion theorem for defeasible logics*. ACM TOCL 12(1), 2010. Cited via Maher 2021; not read.
- Antoniou, G., Billington, D., Governatori, G., Maher, M. J. *A flexible framework for defeasible logics*. AAAI 2000. Not read.
- Governatori, Maher, Antoniou, Billington. *Argumentation semantics for defeasible logic*. J. Logic Computat. 14(5), 2004. Not read; this is where the abstract places argumentation semantics for both the propagating and the blocking variant.
