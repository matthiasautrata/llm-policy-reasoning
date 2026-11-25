# System A contract

The engine (V3a, `v3a-prolog/cli`) ships a CLI that reads one **session script** (JSON) on stdin and
writes one JSON object to stdout. A session is one process: `add` and `with_hypothesis` act on the
running state, so runtime extension is tested without restart.

## Session script

```json
{"config": {"backend": "duckdb",
            "duckdb": "spikes/v3/shared/slice.duckdb",
            "fetch_limit": 10000},
 "load": ["spikes/v3/shared/slice.edn", "spikes/v3/shared/extension.edn"],
 "ops": [ <op>, ... ]}
```

Output: `{"results": [<result>, ...], "load_ms": <number>}`. Every result carries `"ms"` (wall time of
the op) and `"sql_log"`: the SQL statements the op issued, each `{"concept", "sql", "params", "rows"}`.

## Ops

| op | fields | result |
|---|---|---|
| `resolve_term` | `text` | `{status: concept\|none\|several, candidates: [{term, definition, owner}]}` |
| `describe` | `asset` | `{asset, kind, doc, bindings, claims: [claim ids]}` |
| `fetch` | `concept`, `filters` (object) | `{rows: [object], sql, params, row_count, truncated}` |
| `decide` | `goal` (EDN text), `as_of`? | `{status, value, sides, why: [node], owners: [..], qualifier}` |
| `why_not` | `goal`, `as_of`? | `{status, value, why_not: [node]}` |
| `claims` | `asset`, `as_of`? | `{claims: [{id, standing, defeater, qualifier, sides, subclaims: [...]}]}` |
| `add` | `edn` (EDN text: a vector of rule / claim records) | `{added: [ids]}` |
| `with_hypothesis` | `add`? (EDN text), `withhold`? ([ids]), `ops` | `{results: [<result>, ...]}`; state afterwards is unchanged |

`as_of` defaults to the slice's `:today`. Statuses: `ANSWER`, `CONFLICT`, `UNDERDETERMINED`
(the predicate is a known term with no rule or claim), `OUT_OF_SCOPE` (the predicate resolves to no term).

`value`: `true`/`false` for a ground goal; for a goal with one variable, the value of a functional
predicate (slice `:functional`) or the sorted list of all values otherwise. `sides`: for CONFLICT, the
ids of the applicable rules/claims on each side, as a sorted list of sorted lists.

`qualifier` (decide, IR-005): `"total over known facts in declared scope"` when the status is `ANSWER`,
the value is not `false`, `null` or `[]`, and the why tree uses a rule marked `:closed_over :known_facts`
(the answer rests on NAF over the known facts); otherwise `null`. An `ANSWER` whose value is `[]` (no
binding) has an empty `why`.

Claim standing: `holds`, `holds_with_qualifier` (qualifier lists the defeated *supporting* sub-claims),
`rebutted` (defeater names the winning claim, possibly via a required sub-claim), `contested`
(no superiority either way; sides), `not_in_force`.

Claims are stored flat and linked by id (PLAN-v3-integrity §1.1). In the `claims` output, a claim's
`subclaims` are its active linked members: `:depends_on` members first (`role` `"required"`), then
`:supports` members (`role` `"supporting"`). The top-level list (and `describe`) holds the claims about the
asset that no active claim links to; withholding a parent therefore lists its members at top level.

## Integrity gate and errors (PLAN-v3-integrity §2–§3)

The engine runs the shared gate `shared/integrity.py` (stdin `{"load": [paths], "added": [EDN texts],
"withhold": [ids]}` → `{"ok", "violations", "ms"}`) on the rule base an op would produce, **before** its
own schema validation and before the store sees anything: at load, on every `add`, on every
`with_hypothesis` (its `add` and `withhold` on top of the running state). A violation is
`{"violation": <IR name>, "members": [ids], "message"}`; for `defeat-cycle` the members are rule ids.

- Load rejected: the output is `{"error": {"op": "load", "violations": [...]}, "results": []}`.
- `add` / `with_hypothesis` rejected: that op's result is `{"error": {"op", "violations"}}` (plus `ms`);
  the state is unchanged and later ops run as if it had not been sent.
- `INTEGRITY_GATE=off` in the environment admits everything (used only by `cycles_probe.py`).

Re-entry guard: meeting a goal already on the evaluation
path is a dependency cycle the gate did not stop. The op ends with `{"status": "ERROR", "error": {"op",
"violations": [{"violation": "defeat-cycle", "members": [goal EDN, outermost first, ending with the
repeated goal], "path": [goals], "message"}]}}`.

## Why trees

Goals are JSON arrays, predicate first: `["approved", "r000005"]`; `["neg", [...]]` for a complement.

| node | fields | meaning |
|---|---|---|
| `rule` | `id`, `goal`, `children` | the rule concluded `goal`; children align with its body literals in order, then any `superior` nodes |
| `claim` | `id`, `goal`, `asserted_by`, `asserted_at`, `children` | an in-force claim asserts `goal`; children are `superior` nodes |
| `fetch` | `concept`, `filters`, `sql`, `params`, `rows`, `row` | a concept lookup; `row` is the row that bound the literal (absent when `rows` is 0) |
| `fact` | `goal` | a builtin that held: comparison, `is`, `as_of` |
| `absent` | `goal`, `children`? | `goal` is not provable (NAF success, or a failed condition in why-not) |
| `defeated_by` | `id`, `target`, `children` | rule/claim `id` defeated `target`; children: its own proof and a `superior` node |
| `superior` | `winner`, `loser`, `source` | `source`: `explicit`, `authority:R313`, `later`, `strict` |
| `contested` | `goal`, `via`, `rules`, `roots` | ambiguity propagation (`SEMANTICS.md`): `goal` (ground) is contested only because it rests on contested literals. `via`: every contested literal reached through the bodies of its live supporters and live unbeaten attackers, roots included (`[:not L]` as L); `rules`: the ids of those live supporters / attackers of `goal` and of each non-root `via` literal; `roots`: one `conflict` node per root, sorted by goal |
| `aggregate` | `op`, `value`, `members` | an `[:agg Op ?x [..] ?out]` body literal (`SEMANTICS.md`, Aggregates). `members`: one `{value, children}` per proven solution, in binding order. `value` is that solution's ?x, and `children` are the proofs of the conjunction's literals, as for a rule. `check_why.py` re-verifies every member and recomputes the aggregate |
| `conflict` | `goal`, `sides`, `children` | a root conflict: a proven-bodied supporter meets a proven-bodied unbeaten attacker; children are the proofs of the side members |

Downstream CONFLICT (PLAN-v3-integrity §4): `sides` are the deduplicated, sorted sides of every root the
goal depends on; `why` holds one `contested` node per contested ground instance of the goal (an open goal
whose candidate instances include a contested one is CONFLICT as a whole). A root CONFLICT keeps the list
of side proofs as its `why`. A claim whose `depends_on` member is contested is `contested`.

Aggregates: a contested aggregate gives the downstream CONFLICT above. Its contested node's `goal` binds ?out to the aggregate over the proven members only, and `via` lists the contested members' literals. A truncated fetch inside an aggregate's conjunction ends the op with `{"status": "ERROR", "error": {"op", "aggregate": <goal>, "truncated": <concept>, "message"}}`.

Declared incompatibility (R314): an `:incompatible` rule is an attacker of its head (`SEMANTICS.md`), so `approved` against `denied` is a root conflict. Its side proof is a `rule` node with goal `[neg, head]`.

why-not trees: an `absent` node for the goal whose children are, per candidate rule, a `rule` node
with `failed`: the first body literal that did not hold (an `absent` node, recursively explained for
derived literals, or a `fetch` node with 0 rows), or a `defeated_by` node.

`shared/check_why.py` re-verifies trees independently of both evaluators: rule ids exist in the active
rule set, heads and bodies unify with the children's goals, fetch SQL is re-run and must return the
bound row, builtins are re-evaluated, claims are in force, superiority is re-derived from the slice.
