# Procurement slice: model, vocabulary, rules, claims

Evaluation date: 2026-09-15. Generated from `shared/slice.edn` by `v3a-prolog/linkml/build.py`.

## Tables

### cc (`table:cc`)

A cost centre: a node of the budget tree, with its spending cap and the spend booked directly on it this quarter.

| column | type | meaning |
|---|---|---|
| id | id | Cost centre id. |
| parent | id | Parent cost centre; empty for the root. |
| level | int | Depth in the tree; the root is 0. |
| org_unit | enum | Organisational unit the centre belongs to. |
| booked | int | Spend booked directly on this centre (not its descendants). |
| cap | int | Spending cap of the centre this quarter. |

### emp (`table:emp`)

An employee, their role, their cost centre as finance records it, and their direct manager.

| column | type | meaning |
|---|---|---|
| id | id | Employee id. |
| role | enum | Role; governs the approval limit. |
| cc | id | Current cost centre in the finance system. |
| manager | id | Direct manager; empty for the vp. |
| violation | bool | The employee has a recorded policy violation. |

### req (`table:req`)

A purchase request, raised on a date by an employee, for an amount, category and vendor.

| column | type | meaning |
|---|---|---|
| id | id | Request id. |
| requester | id | Employee who raised the request. |
| amount | int | Amount requested. |
| category | enum | Spend category (code list codes:category). |
| vendor | id | Vendor the purchase is from. |
| date | date | Date the request was raised; governs dated rules (R203). |
| status | enum | pending or cancelled. |
| emergency | bool | Flagged as an emergency. |

### assignment (`table:assignment`)

A source's record (hr or finance) that an employee belongs to a cost centre from the effective date on.

| column | type | meaning |
|---|---|---|
| emp | id | Employee. |
| cc | id | Cost centre. |
| source | enum | hr or finance. |
| effective | date | Effective from. |

### role_limit_version (`table:role_limit_version`)

A dated version of a role's approval limit, valid from and to the given dates inclusive.

| column | type | meaning |
|---|---|---|
| role | enum | Role. |
| limit | int | Approval limit. |
| valid_from | date | First day valid. |
| valid_to | date | Last day valid. |

### vendor_status (`table:vendor_status`)

A vendor's status during a period, from and to the given dates inclusive.

| column | type | meaning |
|---|---|---|
| vendor | id | Vendor. |
| status | enum | approved or suspended. |
| valid_from | date | First day. |
| valid_to | date | Last day. |

## Semantic layer

| concept | kind | parameters | columns | meaning |
|---|---|---|---|---|
| request | entity | — | id, requester, amount, category, vendor, date, status, emergency | Purchase requests. |
| employee | entity | — | id, role, cc, manager, violation | Employees. |
| cost_centre | dimension | — | id, parent, level, org_unit, booked, cap | The cost centre dimension: the budget tree, its caps and direct bookings. |
| org_unit | dimension | — | id, centres | The organisational-unit dimension: a grouping of cost centres, not a tree. |
| ancestors_or_self | hierarchy | cc | cc, anc, depth | A cost centre and every ancestor up to the root (the centres a request is charged against). |
| subtree | hierarchy | root | root, id | A cost centre and all its descendants. |
| reporting_chain | hierarchy | emp | emp, approver, role, depth | An employee's manager, the manager's manager, and so on; not the employee. |
| request_in_subtree | entity | root | root, id, requester, cc, amount, status | Requests whose requester's cost centre lies in the subtree of a root. |
| role_limit_version | entity | — | role, limit, valid_from, valid_to | Dated approval-limit versions per role. |
| vendor_status | entity | — | vendor, status, valid_from, valid_to | Dated vendor status periods. |
| assignment | entity | — | emp, cc, source, effective | hr and finance cost-centre assignment records. |
| booked_total | measure | cc | cc, value | Sum of the spend booked directly on every cost centre in the subtree of a centre (zero where nothing is booked). |
| pending_exposure | measure | cc | cc, value | Sum of the amounts of pending requests whose requester's cost centre lies in the subtree of a centre. |
| headroom | measure | — | — | Cap minus booked total. Computed by rule R105 over measure:booked_total; no SQL of its own. |

## Vocabulary

- **booked total** (also: total booked, booked spend) — The booked total of a cost centre, as opposed to its booked amount, differs in counting the bookings of every descendant centre, not only those made directly on it. *Owner: finance.*
- **booked amount** (also: direct booking) — The booked amount of a cost centre, as opposed to its booked total, is only what is booked directly on that centre. *Owner: finance.*
- **committed spend** (also: commitments) — Committed spend, as opposed to booked total, differs in whether pending requests count. Finance has not decided which; no rule defines it. *Owner: finance.*
- **headroom** (also: remaining budget) — Headroom, as opposed to cap, is what remains of the cap after the booked total (R105). *Owner: finance.*
- **pending exposure** (also: pending total) — Pending exposure, as opposed to booked total, sums requests not yet booked (pending, not cancelled). *Owner: finance.*
- **cost centre** (also: cc, budget centre) — A cost centre, as opposed to an org unit, is a node of the budget tree: caps and bookings roll up along it. *Owner: finance.*
- **org unit** (also: organisational unit, unit) — An org unit, as opposed to a cost centre, is a flat grouping of centres (delivery, support, leadership); nothing rolls up along it. *Owner: hr.*
- **department** — Used in practice for both a cost centre and an org unit; resolve to one of them before use. See term:cost_centre, term:org_unit. *Owner: hr.*
- **approval limit** (also: signing limit) — A role's approval limit, as opposed to a cap, bounds a single request an approver may sign, not a centre's spend; dated (R202, R203). *Owner: procurement.*
- **vendor status** — A vendor's status, as opposed to its fitness claims, is the dated register entry (approved or suspended). *Owner: procurement.*
- **purchase request** (also: request, requisition) — A purchase request, as opposed to a booking, is spend not yet committed. *Owner: procurement.*

## Code lists

- `codes:category`: software, hardware, services, capital
- `codes:vendor_status`: approved, suspended
- `codes:role`: analyst, manager, senior_manager, director, vp
- `codes:request_status`: pending, cancelled
- `codes:source`: hr, finance

## Rules

| id | kind | owner | rule |
|---|---|---|---|
| R104 | strict | finance | The booked total of a cost centre rolls up over its subtree. |
| R105 | strict | finance | The headroom of a cost centre is its cap minus its booked total. |
| R106 | defeasible | finance | A request breaches a cap if its amount plus the booked total of some centre it is charged against (its requester's centre or an ancestor) exceeds that centre's cap. |
| R110 | strict | finance | The breaching requests in a subtree are the pending requests raised from it that breach a cap. |
| R120 | strict | finance | Approved total of a subtree: the sum of the amounts of its pending requests whose approval is proven. |
| R121 | strict | finance | Approved count of a subtree: the number of its pending requests whose approval is proven. |
| R112 | strict | finance | A big capital request is a capital request over 50,000. |
| R201 | strict | procurement | A role's approval limit, asked without a date, is the limit on the evaluation date. |
| R202 | strict | procurement | A role's approval limit on a date is that of the version valid on the date. |
| R203 | strict | procurement | The approval limit that governs a request is the one valid on the date the request was raised, not today's. |
| R204 | strict | procurement | A request's vendor status is the vendor's status on the request date. |
| R301 | defeasible | procurement | A request has an approver if someone in the requester's reporting chain has a governing limit of at least the amount. |
| R304 | defeasible | finance | A request passes the cap check if it breaches no cap. |
| R305 | defeasible | procurement | A request passes the vendor check if its vendor is approved on the request date. |
| R306 | defeasible | procurement | Exception: an emergency request passes the vendor check even though its vendor is suspended. |
| R308 | defeasible | procurement | A request is eligible if it has an approver, passes the cap check and passes the vendor check. |
| R309 | defeasible | compliance | A request is denied if its requester has a recorded policy violation. |
| R310 | defeasible | procurement | A request is approved if it is eligible and not denied. |
| R311 | defeasible | procurement | A software request under 10,000 is approved automatically, without further checks. |
| R312 | defeasible | procurement | An automatically approved request is approved (a second sufficient condition). |
| R313 | superiority | controller | Where hr and finance claims disagree on an employee's cost centre, finance prevails. |
| R314 | incompatible | procurement | A denied request is never approved. Declared, not inferred: deriving both is a CONFLICT. |
| R315 | defeasible | finance | An employee's home headroom is the headroom of the cost centre the employee is in. |
| R316 | defeasible | procurement | A purchase order is issued for every approved request. |
| R307 | defeater | procurement | Exception to the exception: the emergency waiver (R306) does not apply to a big capital request. Prevails over R306. |

## Claims

- **C1** about `vendor:bolt`: `[:fit_for_use "bolt"]` — procurement, 2026-03-01, in force 2026-01-01–2026-12-31; presumably; backing: Vendor onboarding file VO-17
- **C1.1** about `vendor:bolt`: `[:due_diligence_passed "bolt"]` — compliance, 2026-02-15, in force 2026-01-01–open; certainly; backing: KYC review 2026-02
- **C1.2** about `vendor:bolt`: `[:neg [:sanctioned "bolt"]]` — risk, 2026-02-20, in force 2026-01-01–2026-12-31; certainly; backing: Sanctions screening run S-0220
- **C1.3** about `vendor:bolt`: `[:price_within_benchmark "bolt"]` — finance, 2026-02-25, in force 2026-01-01–open; presumably; backing: Benchmark B-12: within 5%
- **C2** about `vendor:cog`: `[:fit_for_use "cog"]` — procurement, 2026-03-01, in force 2026-01-01–2026-12-31; presumably; backing: Vendor onboarding file VO-21
- **C2.1** about `vendor:cog`: `[:due_diligence_passed "cog"]` — compliance, 2026-02-15, in force 2026-01-01–open; certainly; backing: KYC review 2026-02
- **C2.2** about `vendor:cog`: `[:neg [:sanctioned "cog"]]` — risk, 2026-02-20, in force 2026-01-01–2026-12-31; certainly; backing: Sanctions screening run S-0220
- **C2.3** about `vendor:cog`: `[:price_within_benchmark "cog"]` — finance, 2026-02-25, in force 2026-01-01–open; presumably; backing: Benchmark B-12: within 5%
- **C7** about `vendor:cog`: `[:neg [:price_within_benchmark "cog"]]` — finance, 2026-05-10, in force 2026-05-10–open; certainly; backing: Benchmark B-19: 12% above
- **C3** about `emp:e077`: `[:cost_centre_of "e077" "cc0078"]` — hr, 2026-07-01, in force 2026-07-01–open; certainly; backing: HR transfer record T-311
- **C4** about `emp:e077`: `[:cost_centre_of "e077" "cc0077"]` — finance, 2026-01-02, in force 2026-01-01–open; certainly; backing: Finance master data load 2026-01
- **C5** about `emp:e077`: `[:cost_centre_of "e077" "cc0078"]` — finance, 2026-08-05, in force 2026-08-01–open; certainly; backing: Finance transfer posting FT-88 (supersedes the January load for e077)
- **C10** about `measure:booked_total`: `[:complete "booked_total"]` — finance, 2026-09-14, in force 2026-01-01–2026-12-31; certainly; backing: Ledger close 2026-09: every booking of 2026 to date is posted to table cc
- **C6** about `vendor:bolt`: `[:sanctioned "bolt"]` — risk, 2026-06-03, in force 2026-06-01–open; certainly; backing: Sanctions list update 2026-06 (supersedes screening S-0220 for bolt)
