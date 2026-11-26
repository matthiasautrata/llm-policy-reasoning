# Judge rubric (PLAN-v3-bench §6)

You grade one analyst session: an assistant's designs for a dashboard, over four scripted turns. You get the turns,
the gold reasons, the checks with their expected values, and the assistant's reply to each turn. Grade only what
the replies say. Do not reward length, confidence or style.

## Gold reasons

A gold reason is a distinction the design must make. Grade each one:

- **covered**: the design states the distinction, or applies it visibly (in a component, its SQL or its caveats),
  and applies it correctly. Rule ids alone are not enough; the design must act on the distinction.
- **wrong**: the design addresses the distinction but gets it wrong. Examples: sums headroom across centres; adds a
  parent's and a child's booked totals; picks one reading of an undefined term without saying so; reports a
  contested result as yes or as no; uses today's limit for a past date.
- **missed**: the design does not address the distinction in any turn listed for it.

The reason's turns are where it is expected. Credit a reason covered in a later turn too, but not a reason the
design states once and contradicts later: that is wrong.

## Checks

A check is one figure or finding for the worked example. Grade each one:

- **reported**: the reply for that turn gives the expected value (any formatting; for a contested result, it says
  contested and gives the proven part where one is expected).
- **wrong**: the reply gives a different value, including the naive value where one is listed.
- **absent**: the reply gives no value for it.

## Output

Reply with one JSON object only, no prose:

```json
{"status": "graded",
 "reasons": [{"id": "GR1", "grade": "covered", "evidence": "a quote of at most 25 words, or empty"}],
 "checks": [{"id": "A1.K1", "grade": "reported"}]}
```

Every gold reason and every check appears exactly once.
