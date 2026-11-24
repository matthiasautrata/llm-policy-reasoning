# Spike v3 — System A for the warrant: V3a (LinkML · Prolog · DuckDB) vs V3b (EDN · Clojure · Datahike · DuckDB)

Plan for Claude Code. Written 2026-11-24 from a design session with Matthias. Same procedure as v2's `REWORK.md`: follow it, deviate where the code shows a better way, log every deviation with its reason under **Decisions** at the end.

## 0 Ground rules

- Work on a branch `spike/v3`. Do not push. Do not touch v2 code outside `spikes/v3/` except to import from it read-only.
- No LLM calls in this spike. Budget: $0 API spend.
- Ask Matthias before installing system-level software (brew, Docker images, JDKs). Language-level deps (pip into the repo `.venv`, Clojure `deps.edn`) are fine.
- Timebox: V3a ≈ 2 working sessions, V3b ≈ 3. If a spike is not green on the acceptance test (§6) at the end of its timebox, stop, record what is missing and why, and do not extend without asking.
- Every claim about a library's API (Datahike branching, Scriptum/Proximum, SWI janus, LinkML generators) must be checked against current docs before use; record versions.

## 1 Purpose

v3 will test whether rules held as tools and computed deterministically beat free-text rules in the prompt (the Genie pattern), as rules grow and interact. Its thesis does not depend on which deterministic engine computes the rules. This spike decides **System A** — the store and evaluator for vocabulary, semantic-layer metadata, claims and rules — for the v3 build and for a possible path to a system at work.

Two candidates, one identical acceptance test, criteria fixed in advance (§7):

- **V3a** — LinkML (structure) · SWI-Prolog (evaluator, shell) · DuckDB/Postgres (detail data) · Python host.
- **V3b** — EDN + Malli (structure and rules, one notation) · Clojure evaluator · Datahike (claims, vocabulary, history, branching) · DuckDB/Postgres (detail data) · JVM.

Out of scope: the v3 arms (G, G+, T), any agent or prompt, scale beyond §4.

## 2 Architecture constraint (both spikes)

**System A holds no detail data.** Detail data stays relational. System A reaches it only through one interface:

```
fetch(concept, filters) -> rows
```

- `concept` is a semantic-layer entry (measure or dimension) bound to physical tables and columns; the binding yields a SQL template.
- Two backends must work with **only a config change**: DuckDB (file) and Postgres (local). This stands in for Databricks / Snowflake.
- Dialect differences (date functions, recursive CTE syntax if any) live in the binding layer, never in rules.
- Rules never contain SQL. Rules reference concepts; concepts resolve to SQL.

## 3 Shared assets (`spikes/v3/shared/`) — build first

### 3.1 Canonical slice: `slice.edn`

One file, authored once, in EDN. It is the input to both spikes (V3a loads it through an EDN reader; V3b natively). Contents:

**Assets** (anything significant a claim can attach to), stable ids with prefixes:
`table:req`, `table:emp`, `table:cc`, `table:assignment`, `table:role_limit_version`, `table:vendor_status`, `col:req/amount`, `measure:booked_total`, `term:booked_total`, `term:committed_spend`, `term:department`, …

**Physical model** (doc per table/column), **semantic layer** (measures: `booked_total`, `headroom`, `pending_exposure`; dimensions: `cost_centre`, `org_unit`), **vocabulary** (terms with contrastive definitions — "X as opposed to Y, differing in Z" — code lists for `category`, `vendor_status`, `role`; a two-level taxonomy for `category`).

**Rules** (about 12, reusing v2 R-ids where they exist; procurement domain):

| Id | Content | Exercises |
|---|---|---|
| R104 | booked total rolls up over the subtree | semantic-layer measure, recursion |
| R105 | headroom = cap − booked total | arithmetic over a measure |
| R106 | cap breach: booked total + amount > cap on any charged centre | ancestors |
| R203 | approval limit governed by the request date (dated `role_limit_version`) | as-of |
| R301 | has approver: someone in the chain with limit ≥ amount | recursion + as-of |
| R305 | vendor check: vendor approved | base rule |
| R306 | exception: emergency passes a suspended vendor | defeasible |
| R307 | exception to the exception: not for capital > 50,000 | defeater of R306 |
| R310 | approved if eligible and not denied | |
| R311/R312 | software < 10,000 auto-approved; auto-approved ⇒ approved | second sufficient condition |
| R314 | incompatibility: a denied request is never approved | rule-level CONFLICT, engine-detected |
| R313 | where HR and finance claims disagree on a cost centre, finance prevails | superiority by asserter |

**Claims** (Toulmin): each claim has
`id, about (asset id), assertion, asserted_by, asserted_at, valid_from, valid_to, warrant (rule id, optional), backing (source), qualifier, subclaims`.
One level of nesting. Each sub-claim has the same fields plus `role: required | supporting`.

Semantics of a parent claim (**confirm with Matthias before building; default below**):
- holds iff it is not defeated and every `required` sub-claim stands;
- if some `supporting` sub-claims are defeated it **holds with qualifier**, listing them;
- if a `required` sub-claim is defeated it is **rebutted**, naming the defeater.

Planted claims:
- C1 "vendor bolt is fit for use" (procurement), sub-claims: due diligence passed (compliance, required), not sanctioned (risk, required, valid to 2026-12-31), price benchmark within 5% (finance, supporting). A later risk claim "bolt sanctioned from 2026-06-01" defeats the sanctions sub-claim for dates ≥ 2026-06-01 → C1 rebutted from that date, holds before.
- C2 "vendor cog fit for use" with a defeated *supporting* sub-claim → holds with qualifier.
- C3/C4 HR vs finance claims on employee e077's cost centre on overlapping dates → resolved by R313 (superiority), CONFLICT if R313 is withheld.
- One claim superseded by a later claim from the same asserter (later supersedes earlier).

### 3.2 Defeasible semantics (both spikes implement the same)

Defeasible logic in the Nute / Governatori style:
- strict rules, defeasible rules, defeaters; superiority relation.
- Superiority sources, in this order: explicit `superior` facts (e.g. R307 > R306); asserter authority order (`finance > hr`); for the same asserter, later `asserted_at` supersedes earlier.
- **Ambiguity blocking:** two applicable rules with complementary conclusions and no superiority → neither is concluded; status **CONFLICT** with both sides. This matches v2's statuses.
- Incompatibility (R314) is declared, not inferred: `excluded(approved(R)) ← denied(R)`; a goal derived and excluded is CONFLICT, as v2's M/M− check.
- Statuses returned: `ANSWER`, `CONFLICT` (with sides), `UNDERDETERMINED` (a needed concept or rule absent), `OUT_OF_SCOPE` (term resolves to none).

### 3.3 Reference and keys: `reference.py`

Independent plain-Python implementation of §3.1 + §3.2 over the generated data (pattern: v2 `verify/reference.py`). Produces `keys.json`: per question, expected status, value, sides, and the **core** rule/claim ids of the explanation. Both spikes must reproduce every key. A mutation test (flip two comparisons) must make the check fail.

### 3.4 Data: `gen.py`

- Reuse v2 `world/` generator logic for the tree, employees, vendors.
- Scale: about 2,000 cost centres, 20,000 employees, 100,000 requests, assignments with HR/finance divergence, dated role limits and vendor status.
- Load identically into `slice.duckdb` and a local Postgres database `spike_v3`. A check script compares row counts and checksums per table.

### 3.5 Questions: `questions.edn`

About 15, each with a key from §3.3. Must include:
- value questions over a measure (booked total, headroom of a subtree);
- an as-of question (approval limit on the request date vs today);
- vendor check under exception and exception-to-exception;
- approval with R314 conflict (expected CONFLICT, sides);
- e077's cost centre on a date (R313 resolves; also asked with R313 withheld → CONFLICT);
- C1 on a date before and after 2026-06-01 (holds / rebutted, with defeater);
- C2 (holds with qualifier);
- one **why-not** (request not approved: which condition failed or which defeater won);
- one exhaustive set question (all breaching requests in a subtree) — must be answered via `fetch`, not by loading all rows;
- three `resolve_term` probes: one concept, one none ("travel budget"), one several ("department": cost centre vs org unit).

## 4 System A surface (both spikes, same contract)

A function API plus a CLI that prints JSON. No HTTP/MCP needed in the spike.

| Call | Returns |
|---|---|
| `resolve_term(text)` | `{status: concept|none|several, candidates:[{term, definition, owner}]}` |
| `describe(asset_id)` | docs, bindings, claims attached |
| `fetch(concept, filters)` | rows (+ SQL issued, row count, truncation flag) |
| `decide(goal, as_of?)` | `{status, value, sides?, why, owner(s), qualifier?}` |
| `why_not(goal, as_of?)` | failed conditions or winning defeater |
| `claims(asset_id, as_of?)` | claims with their current standing |
| `with_hypothesis(extra_rules_or_claims, thunk)` | evaluate under a temporary rule/claim set, then discard (adoption gate / what-if) |

`why` is a proof tree in a common JSON shape (both spikes): nodes `rule`, `claim`, `fact`, `fetch` (SQL + row count), `absent`, `defeated_by`, `superior`. A checker re-verifies every tree independently of the evaluator (as v2 `check_why/3`).

## 5 Spike specifics

### 5.1 V3a — LinkML · Prolog · DuckDB/Postgres (`spikes/v3/v3a-prolog/`)

- **Model:** a LinkML schema for Asset, Table, Column, Measure, Dimension, Term, CodeList, Rule (envelope: id, owner, class, conservative, layer, body), Claim, SubClaim. Rule bodies are EDN strings in a `body` slot. Convert `slice.edn` → JSON/YAML instances and validate them with LinkML. Generate Markdown docs from the schema + instances (this will be the G arm's material in v3) and DDL for DuckDB/Postgres (compare with the generator's DDL; record mismatches).
- **EDN reader:** a DCG for the EDN subset used (lists, vectors, maps, sets, keywords, symbols, strings, integers, decimals, `#inst`). Rule bodies become Prolog terms.
- **Evaluator:** SWI-Prolog (installed: 11.0). Defeasible theory → clauses by a translation in the DR-Prolog style; tabling; well-founded semantics (`tnot/1`) where mutual defeat can loop. Reuse v2 `engine/why.pl` ideas for proofs; extend with `defeated_by`, `superior`, claims.
- **SQL boundary:** Prolog calls Python through SWI's janus (`py_call/2`); Python executes SQL via `duckdb` / `psycopg`. Concept → SQL binding table in Python or Prolog (choose one, record why).
- **Hypotheses:** `with_hypothesis` via a temporary module or `assert`/`retract` in a transaction; regression = the questions of §3.5.

### 5.2 V3b — EDN · Clojure · Datahike · DuckDB/Postgres (`spikes/v3/v3b-clojure/`)

- **Model:** Malli schemas in EDN for the same record kinds; validate `slice.edn` directly. Generate the same Markdown docs (write the generator). JSON Schema from Malli for the common `why` shape.
- **Store:** Datahike (file backend; record the version). Claims, assets, vocabulary, rules as entities. Who-said-it/when: map `asserted_by`/`asserted_at` to transaction metadata **and** to attributes; record which works better for as-of queries and why. Use `as-of` / history for C1 before/after.
- **Branching:** use Datahike's versioning / branching API for `with_hypothesis` (verify the API in current docs; if experimental, say so). Compare with a plain in-memory database copy.
- **Search:** `resolve_term` first with plain Datalog string matching over terms and synonyms; then try Scriptum (Lucene) for full-text. HNSW (Proximum) only if time remains; not required for green.
- **Evaluator:** in Clojure over Datahike query results. Rules are EDN data interpreted at runtime (no codegen, no restart). Datahike rules (`%`) may be used for recursion where they fit; the defeasible layer (superiority, ambiguity blocking, incompatibility) is the Clojure interpreter's job. Proof trees in the common shape.
- **SQL boundary:** `next.jdbc` with the DuckDB JDBC driver and the Postgres driver; same concept bindings (read from `slice.edn`).
- **Dev loop:** REPL-driven; a `bb`/CLI entry point prints JSON for the shared checker.

## 6 Acceptance test (identical for both)

`spikes/v3/shared/accept.py` runs a spike's CLI and checks:

1. Every question in `questions.edn` matches `keys.json`: status, value, sides; `why` core ⊆ tree rules/claims; every tree re-verifies.
2. Backend swap: same results on DuckDB and Postgres with only a config change.
3. Runtime extension: adding one claim (the later sanctions claim) and one rule (R307) at runtime changes exactly the expected answers, without restart, compile or deploy.
4. `with_hypothesis`: withholding R313 turns the e077 question into CONFLICT inside the hypothesis and leaves the base state unchanged afterwards.
5. The exhaustive set question is answered through `fetch` with a bounded result (no full-table load into System A); the issued SQL is logged.
6. `resolve_term` probes give concept / none / several as keyed.

Green = all six pass.

## 7 Comparison criteria (fixed now; report in `spikes/v3/RESULTS.md`)

| Criterion | Measure |
|---|---|
| Correctness | acceptance test green; defects found on the way and where (model, evaluator, SQL boundary) |
| Effort | sessions to green; lines of code split into model, evaluator, explanation, SQL boundary, glue |
| Defeasible semantics | ambiguity blocking, superiority, incompatibility, parent/sub-claim standing: native, built, or workaround |
| Explanations | why and why-not completeness against keys; effort to build |
| As-of / provenance | how naturally who-said-it, when, and validity are queried |
| Adoption gate | `with_hypothesis` mechanism and its cost |
| SQL boundary | clarity of the concept → SQL layer; DuckDB → Postgres swap effort |
| Performance | p50/p95 per `decide` at 100k requests; cold start; memory |
| Authoring | the slice read in each spike's own notation (LinkML YAML vs EDN): Matthias judges readability; record size in lines |
| Footprint and transfer | runtime deps; what would be needed at work (JVM vs SWI/Python); maturity notes (versions, experimental features used) |

`RESULTS.md` ends with a recommendation and the one or two facts that decided it. No verdict on readability: that is Matthias's call.

## 8 Order of work

1. Shared: `slice.edn`, `reference.py` + `keys.json` (+ mutation test), `gen.py` → DuckDB + Postgres, `questions.edn`, `accept.py`, why-tree checker. Confirm the parent/sub-claim semantics (§3.1) with Matthias before writing the reference.
2. V3a to green (it also validates the shared slice and keys cheaply).
3. V3b to green.
4. `RESULTS.md`.

## 9 Layout

```
spikes/v3/
  PLAN.md            this file
  RESULTS.md         comparison and recommendation (end of spike)
  shared/            slice.edn, questions.edn, gen.py, reference.py, keys.json, accept.py, check_why.py
  v3a-prolog/        linkml/, edn.pl, defeasible.pl, why.pl, sql.py, cli
  v3b-clojure/       deps.edn, src/, resources/schemas.edn, cli
```

## Decisions

(Executor: append dated entries — what was decided, why.)

**2026-11-24 · Parent/sub-claim semantics confirmed** (Matthias, before execution). §3.1 default stands: a parent claim holds iff it is not defeated and every `required` sub-claim stands; defeated `supporting` sub-claims leave it holding with a qualifier that lists them; a defeated `required` sub-claim rebuts it, naming the defeater. No need to ask again in step 8.1.
