# System A contract (both spikes)

PLAN §4 made concrete. Each spike ships a CLI that reads one **session script** (JSON) on stdin and
writes one JSON object to stdout. A session is one process: `add` and `with_hypothesis` act on the
running state, so runtime extension is tested without restart.

## Session script

```json
{"config": {"backend": "duckdb" | "postgres",
            "duckdb": "spikes/v3/shared/slice.duckdb",
            "postgres": "dbname=spike_v3",
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

Claim standing: `holds`, `holds_with_qualifier` (qualifier lists the defeated *supporting* sub-claims),
`rebutted` (defeater names the winning claim, possibly via a required sub-claim), `contested`
(no superiority either way; sides), `not_in_force`.

Claims are stored flat and linked by id (PLAN-v3-integrity §1.1). In the `claims` output, a claim's
`subclaims` are its active linked members: `:depends_on` members first (`role` `"required"`), then
`:supports` members (`role` `"supporting"`). The top-level list (and `describe`) holds the claims about the
asset that no active claim links to; withholding a parent therefore lists its members at top level.

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

why-not trees: an `absent` node for the goal whose children are, per candidate rule, a `rule` node
with `failed`: the first body literal that did not hold (an `absent` node, recursively explained for
derived literals, or a `fetch` node with 0 rows), or a `defeated_by` node.

`shared/check_why.py` re-verifies trees independently of both evaluators: rule ids exist in the active
rule set, heads and bodies unify with the children's goals, fetch SQL is re-run and must return the
bound row, builtins are re-evaluated, claims are in force, superiority is re-derived from the slice.
