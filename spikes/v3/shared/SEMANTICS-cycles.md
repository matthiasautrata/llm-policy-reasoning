# Semantics for defeat cycles (PLAN-v3-cycles §1.2)

Target: **well-founded defeasible semantics with ambiguity blocking**. It is fixed here before keying, and `reference.py` (`Cyc`) implements it independently of every spike.

## Definition

Ground the theory: rules, defeaters, claims in force on `as_of`, and superiority (explicit `:superior-to`, authority rules `:pred`/`:order`, later `asserted_at` for the same asserter, strict over non-strict). Then read it as the normal logic program below, a ground form of the Antoniou–Billington–Governatori–Maher metaprogram (TPLP 2006, clauses c4–c6), and take its **well-founded model** (alternating fixpoint). Here `~L` is the complement of L; a claim is a rule with an empty body; `body(r)` holds when every body literal is `def`, builtins and fetches being facts.

```
def(L)            :- r supports L, r is not a defeater, body(r), not overruled(r, L).
overruled(r, L)   :- s attacks L (head ~L, or a functional rival), body(s), not beaten(s, L).
beaten(s, L)      :- t supports L, t > s, body(t).
```

Each literal then has a value: **true**, **false**, or **undefined**.

**Ambiguity blocking** comes from the three-valued reading of `body(s)` inside `overruled`. An attacker is discarded only when its body is **false**. An attacker whose body is undefined keeps `overruled` undefined, so the literal it attacks is undefined too. The undefined attacker "still counts", as in Maier's Def. 3. An ambiguous literal that the theory determines, such as a direct rebut with no priority, is false on both sides. It therefore cannot attack anything downstream (Y5c).

## Mapping to statuses

| WFS value of goal L | Status | Sides |
|---|---|---|
| true | ANSWER (value true) | none |
| undefined | CONFLICT | `[[live supporters], [live unbeaten attackers]]`, where *live* means the body is not false. If either list is empty, as when L only depends on something undefined (Y5b), the sides are those of the first undefined body literal of the first undefined supporter, taken recursively. |
| false, with an applicable supporter (body true) and a live unbeaten attacker | CONFLICT (blocked, as the existing slice semantics already do for C3/C4) | `[[applicable supporters], [live unbeaten attackers]]` |
| false, otherwise | ANSWER (value false) | none |

The why tree for an undefined goal has a node `{type: "undefined", goal, literals, members}`:
- `literals`: the undefined ground literals reachable from the goal through body and attack edges;
- `members`: the ids of every rule or claim that supports or attacks one of those literals and has a live body.

`check_why.py` compares both lists to the reference.

## Decisions

- **Y5: blocking, not propagating.** Consider a literal whose only supporter depends on a *blocked* literal (Y5a), or whose attacker does (Y5c). The blocked literal is false, so the downstream rule fails (Y5a gives ANSWER false) or the attacker is discarded (Y5c gives ANSWER true). Under ambiguity propagation, Y5c would be CONFLICT. Y5c is the question that tells the two apart.
- A literal that depends positively on a literal **undefined by a cycle** (Y5b) is undefined, and so CONFLICT. This is not ambiguity propagation in the DL sense. It is plain WFS: failure by looping cannot be decided, so neither can anything built on it. The existing slice semantics never met this case.
- Y1 is **not** undefined: DL derives −∂ for both sides, which is the existing "blocked" CONFLICT. Undefined values arise only from real dependency cycles: Y2, which is even, and Y3, which is odd. Y3 gets the same mapping as Y2.
- **WFS (failure by looping) over Kunen.** With Kunen semantics, `p ⇒ p` leaves p undecided. With WFS it is false. The slice has no positive loops, so this choice does not change any key. It is recorded so that the engines agree on it.

## Literature: confirmed vs assumed

**Confirmed** (read in the source):
- Antoniou, Billington, Governatori, Maher, *Embedding defeasible logic into logic programs*, TPLP 6(6), 2006 (arXiv cs/0511055):
  - The c4–c6 metaprogram, which the program above follows.
  - DL coincides with the Kunen semantics of the metaprogram. It coincides with the sceptical stable semantics only for decisive (acyclic) theories.
  - An undecided literal implies a cycle in the dependency graph. The cycle problem "prevents Defeasible Logic to be characterised by well-founded semantics", and Maher & Governatori (1999) give a modified DL that uses WFS.
- Maier, *Well-founded semantics for defeasible logic* (arXiv 1106.1957):
  - Both NDL (ambiguity blocking) and ADL (ambiguity propagating) include failure by looping.
  - ADL corresponds to the WFS of the *direct* translation; NDL does not. In Maier's words, "NDL blocks ambiguity while both ADL and the WFS propagate it".
  - So blocking has to be encoded through the metaprogram, as above. A direct translation of rules to `not ~L` would propagate.

**Assumed** (not verified):
- That the program above coincides with Maher & Governatori's WFDL (AAAI-99) on Y1–Y6. The AAAI PDF could not be read, so their exact metaprogram was not compared.
- Team defeat with authority and `later` superiority, and functional rivals as attackers. These extend the published metaprograms in the way the slice already did. No published result covers them.
- Claims as empty-body defeasible rules gated by valid time. This is a modelling choice of this spike, not literature.

## Answer sets (V3e)

The same program read under stable models gives:
- Y2 (an even loop): two answer sets. Cautious reasoning yields neither literal; brave reasoning yields both, which gives the sides.
- Y3 (an odd loop): no answer set, so a naive encoding makes the whole program inconsistent.

V3e has to handle Y3 apart from this mapping. Its Decisions entry records how.
