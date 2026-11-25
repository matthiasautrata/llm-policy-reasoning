# Spike v3 addendum — memory and aggregate cost: attribute, fix, re-measure, then decide

Plan for Claude Code, 2026-11-25 (Matthias). Branch `spike/v3`. Standing rules: `CLAUDE.md`. First, harvest `PLAN-v3-preconditions.md` into `HISTORY.md` (one entry; Matthias has reviewed its Decisions) and delete it.

## 0 Why

`[:approved_total "cc0000" ?v]` (90 028 pending members) takes 207 s and peaks at 12.1 GB RSS with about 925 000 memo entries; the bench peak rose from 153 to 656 MB, unattributed. About ten memoised literals per member is what the rules justify. About 13 KB per entry is not. Hypotheses from reading `defeasible.pl`, to be confirmed or refuted by §1:

1. **Memo entries store full proof trees.** `evaluate/3` memoises `proven(Sups, …)` with the proof dicts; `assertz` copies the term, so subproofs shared across members (the same cap check, vendor status, role limit) are duplicated per member and again per ancestor entry.
2. **Every lookup copies them back.** `memo_get` copies the stored term to the stack; `findall` copies solutions again; the aggregate does both over every member, every round.
3. **Explanations are built for every member and then discarded.** `agg3` keeps `members:[_{value, children:Kids}]` for all members and memoises it; the response's why tree is 0.4 MB.

Memory is an engineering defect. Latency (about 2.3 ms per member) is partly the same defect and partly the evaluation strategy (top-down, member at a time). Fix the defect first, then measure, then decide the strategy (§5).

## 1 Attribute (before any fix)

On cc0018 (L2), cc0002 (L1) and cc0000 (root), one session each:
- memo entries by key kind (`literal`, `missed(_, _)`, `agg(_)`) and by predicate; `term_size/2` of the stored results, total and per kind;
- `statistics/2`: clause-store memory (`memory`/`program`), global and trail stack peaks, GC time;
- peak RSS; share of time in fetch, evaluation, memo copy (profile).

Write the numbers into RESULTS (a short table) and say which of hypotheses 1–3 they confirm. Attribute the bench's 153 → 656 MB the same way.

## 2 Fix A: memoise statuses, build proofs on demand

- The memo holds only what evaluation needs: status (proven / refuted / contested), value, and the ids and ground instances of live supporters, beaten and unbeaten attackers, contested body literals. No proof dicts.
- Why trees are rebuilt from those ids, only for what the answer reports: the goal; for an aggregate, every contested member in full, and proven members as a bounded sample (default 20, configurable) with the member count. Specify the aggregate node change in `CONTRACT.md` and `SEMANTICS.md`; `check_why.py` verifies every reported member and the count.
- Semantics unchanged. Gate: keys byte-identical except the aggregate node shape; list those diffs.

## 3 Fix B: index rules

Rule lookup by id (`live_sup` / `live_att` scanning `rule/5`) is 17 % of the profile at cc0002. Index rules by head predicate (and by id) so lookups are not linear scans. Gate unchanged.

## 4 Re-measure

The §2.1 fetch-volume table again, L4 to root, with added columns: peak RSS, memo entries, bytes per entry, GC time. Bench and hypothesis latency again. If the root no longer needs an 8 GB stack, restore the default `stack_limit` and record it.

## 5 Strategy for large aggregates: proposal only, Matthias decides after §4

For information, a reasonable "good enough" for the benchmark: root under about 10 s and under 1 GB. Write a one-page proposal in RESULTS with an estimate for the option the numbers point to:

1. **Stop here.** If §4 meets the bar.
2. **Compile aggregate bodies to SQL (hybrid).** Precedent: at work, Datalog → Logica → Postgres was compiled-only by design, and that is what made it modular, composable and portable. Here:
   - SQL generated from the rules, never hand-edited; the rules stay the only definition (IR-002).
   - Acyclic rule bases are stratified, so: layered views or functions; `NOT EXISTS` for negation; native aggregates; a status column for the three values; anti-joins for team defeat; `as_of` and withheld rule ids as parameters; supporter and attacker ids as columns for explanations.
   - Portable SQL, with dialects by a transpiler (e.g. SQLGlot): DuckDB locally; Postgres, Snowflake and Iceberg engines as targets, because transactional data must stay there.
   - Prolog keeps single-literal questions, explanations from the id columns, and hypotheses that add rules.
   - The compiled path must reproduce `reference.py`'s keys under the same gate.
   - First target: the body of `approved_total` (`approved` over a subtree).
3. **Bottom-up in Prolog for aggregate bodies.** Compute the body predicate for all members once per op and state, then aggregate. Only if 2 is blocked.

Name the deciding numbers. Do not build 2 or 3 in this plan.

## Decisions

(Executor: append dated entries — what was decided, why.)

- 2026-11-25, §1: measured with scratch probes (memo grouped by key kind, predicate and status with `term_size/2`; `statistics/2`; RSS per SQL statement), not with code added to the engine. The root's memo figures come from a run with the §3 index in place: indexing does not change memo contents, but it does change the timing (139 s against 207 s).
- 2026-11-25, §1: hypotheses 1–3 hold, but the largest memory cost is DuckDB executing `flush()`'s UNION ALL batches of the recursive `reporting_chain` CTE (about 4 MB per copy). The memo is about 1.8 GB of the root's 12.7 GB. Fix A alone cannot meet the §5 bar. The choice of SQL remedy is put to Matthias before §2 (RESULTS, Memory attribution).
- 2026-11-25, §3, done before §2: the index is independent of Fix A and cheap to verify on its own. Rules are indexed by head predicate (`rule_at/2`, keyed `neg(P)` for a complement), with a scan as the fallback for a head that has no key. Lookup by id already used first-argument indexing on `rule/5`. Gate GREEN, keys unchanged. Root: 207 674 → 139 139 ms. Bench peak 671 MB (was 656).
- 2026-11-25, SQL remedy (Matthias's choice, after §1): `:batch_sql`, an optional set form of a concept's SQL for its one required parameter, written `IN ($p)`. It is data in slice.edn and a slot in the LinkML model; `sql.register` rejects a malformed one. `flush()` uses it when that parameter is the filter that varies. No new gate check: `check_why` re-runs each reported key's single-key statement, and a probe with a wrong set form failed check 1. A static check (the set form has the same output columns, and its parameter is among them) could be proposed as a new IR. L2: +2089 MB → +3 MB on the statement; bench 671 → 241 MB. The root still peaks at 12.1 GB, so §2 is re-attributed there. Re-measured: the root's SQL growth is 616 MB (was 5.2 GB); its largest statement adds 188 MB.
- 2026-11-25, §2: the memo holds `status/3` results whose eterms carry `-` for the proof; supporter and attacker ids, their ground heads, superiority nodes, contested literals and aggregate value/count are kept. Evaluation runs with proofs off (`with_proofs/2`, a global variable), so body literals give `-` and no proof dict is built. `evaluate/3` rebuilds the proofs of one result on demand (`hydrate/4`): a claim from `claim/10`, a rule eterm by re-running `best_sol/7`, which is deterministic and so finds the solution evaluation found. `prove/3` rebuilds only the first supporter, as before; `decide_open` takes statuses for every candidate and rebuilds only the instances it reports. Why trees are unchanged except the aggregate node.
- 2026-11-25, §2, aggregate node: `count` (the proven members) and `members`, the first `agg_sample` (default 20) in binding order, rebuilt from their stored bindings. `agg_sample` is a CLI config key, held in a Prolog flag so that threads see it. "Every contested member in full" is met by the `contested` node, not the aggregate node: a contested aggregate never gives an aggregate node, and its `via` and `roots` already list every contested member with its side proofs. `check_why` verifies every shown member, `count` ≥ members, `count` against the key, the recomputed value when all members are shown, and a `:count` value equal to `count`; a `:sum` value under sampling rests on the key's value.
- 2026-11-25, §2, key diff: `agg_count` added to Q44 (99) and Q45 (9) in `base` and `changed`, from `reference.py`'s member list; no other key changed. Probes: a sample of 200 (every member shown, value recomputed) passes check 1; a count one too high fails check 1 on Q44.
