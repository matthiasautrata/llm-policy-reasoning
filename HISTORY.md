# llm-policy-reasoning history

One line per chapter. The detail lives in each chapter's own record, named at the end of its entry.

## v1 — Rules in Context (2026-09-18..2026-11-22; tag `v1`, 0818ce3..24973ef)

Does notation matter, and when is an engine needed? Written decisions mattered, notation did not; the engine earned its place at scale. Record: `paper/v1/`, the studies at tag `v1` (`make verify-v1`).

## v2 — Layers of Meaning (2026-11-22..23; c9e8ab3..b228dca)

Which layer (L0–L3) does a question need, in which representation and mode? H1 and H5 confirmed, H2 qualified, H3 wins on contradiction, H4 falsified; $8.11 for 8,878 records. Record: `paper/v2/`, `REWORK.md` (plan and Decisions, M0–M7), `results/`.

## v3 spike — System A (2026-11-24..; fcd9480..; tags `spike-v3-five-platforms`, `spike-v3-housekeeping`)

Rules and claims as data, a defeasible engine over bounded SQL fetch; five platforms explored, Python + Prolog chosen. Record: `spikes/v3/HISTORY.md`.

## Repo inventory (2026-11-25; tag `spike-v3-housekeeping`)

Every top-level entry was checked for a current claim that cites it (`INVENTORY.md` at the tag; approved by Matthias, executed by `spikes/v3/PLAN-v3-preconditions.md` §1).
- Kept: the papers, the v2 code (`make verify` needs all of it; `spikes/v3/shared/gen.py` imports `world.domain`), `worlds/`, and all of `results/`.
- `results/m6-compile-L3-preR314` is superseded and unscored but kept: its 142 records are part of the paper's 8,878 and its cost.
- `REWORK.md` stays until the paper is consolidated, because paper v2 cites its Decisions for costs.
- Updated: README (v2 finished, spike v3), `requirements.txt` (the spike's dependencies).
