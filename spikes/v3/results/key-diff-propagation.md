# Key diff: ambiguity blocking → ambiguity propagation (PLAN-v3-integrity §4.3)

`shared/keys.json` before phase 3 (ef6ec40, blocking; still `reference.py --semantics blocking`) against
after (propagation, `shared/SEMANTICS.md`). The base and extended states (Q01–Q27) are **byte-identical**:
no slice question derives anything from a contested literal (R314's conflict on `approved` and C3/C4's on
`cost_centre_of` feed no rule of the slice; C1 depends on C1.2, which is beaten by the later C6, not
contested). Only `:state :acyclic` questions change, and exactly the four built on Y1's dispute (Y5) or on
the R313-less C3/C4 dispute:

| Q | Goal | Old (blocking) | New (propagation) | Reason (root conflict) |
|---|---|---|---|---|
| Q35 (Y5a) | `[:flagged "fern"]` | ANSWER false, core RY51 | CONFLICT, sides `[[CY1a] [CY1b]]`, core CY1a CY1b RY51 | RY51's only body literal `blacklisted fern` is the contested root Y1 (CY1a vs CY1b, no superiority); blocking read it as false |
| Q37 (Y5c) | `[:cleared_for_tender "fern"]` | ANSWER true, core RY53 | CONFLICT, sides `[[CY1a] [CY1b]]`, core CY1a CY1b RY53 RY54 | the defeater RY54's body `blacklisted fern` is contested, so RY54 is live and unbeaten; blocking discarded it |
| Q40 (Y5d) | `[:screening_clear "fern"]` | ANSWER true, qualifier "total over known facts…" | CONFLICT, sides `[[CY1a] [CY1b]]`, core CY1a CY1b RY55, qualifier null | RY55's `[:not [:blacklisted "fern"]]` is contested because its argument is; blocking's NAF succeeded on the false literal |
| Q41 (Y5e) | `[:home_budget "e077" ?v]`, as of 2026-07-15, R313 withheld | ANSWER `[]` | CONFLICT, sides `[[C3] [C4]]`, core C3 C4 RY56 | both RY56 instances (699000 via cc0077, 774000 via cc0078) fetch the measure over a contested `cost_centre_of` (C3 hr vs C4 finance, unordered without R313); blocking gave the empty set |

Unchanged acyclic questions, as expected: Q30 (the root Y1 itself), Q32 (acme, no attacker), Q34 (RY4
resolves Y4), Q42 (R313 resolves C3/C4, so 699000 is proven and 774000 refuted), Q43 (RY21 against the
unordered defeater RY23, a root conflict).

The downstream CONFLICT keys also carry `contested`: per contested ground instance of the goal, `{via,
rules, roots}` (SEMANTICS.md), re-verified by `check_why.py` against the engines' `contested` nodes.

Refutation was moved to DL's team form (−σ: every live supporter beaten by *some* superior attacker with a
proven body) in both `Prop` and the slice's `Ref.literal`; no key changes (no literal of the slice has two
live supporters facing different superior attackers).
