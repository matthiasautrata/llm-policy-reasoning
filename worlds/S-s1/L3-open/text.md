# Procurement records (L3)

Each table below is one kind of record. Dates are YYYY-MM-DD.

## cc

A cost centre.
Identified by: cc.

| cc |
|---|
| company |
| cc1 |
| cc1_1 |
| cc1_2 |
| cc2 |
| cc2_1 |
| cc2_2 |

## cc_parent

The parent of a cost centre. The root cost centre has no row.
Identified by: cc. References: `cc` refers to `cc`; `parent` refers to `cc`.

| cc | parent |
|---|---|
| cc1 | company |
| cc1_1 | cc1 |
| cc1_2 | cc1 |
| cc2 | company |
| cc2_1 | cc2 |
| cc2_2 | cc2 |

## org_unit

The organisational unit a cost centre belongs to.
Identified by: cc. References: `cc` refers to `cc`.

| cc | unit |
|---|---|
| company | leadership |
| cc1 | leadership |
| cc1_1 | delivery |
| cc1_2 | support |
| cc2 | leadership |
| cc2_1 | support |
| cc2_2 | delivery |

## emp

An employee, their role, and their current cost centre as finance records it.
Identified by: emp. References: `cc` refers to `cc`.

| emp | role | cc |
|---|---|---|
| e000 | vp | company |
| e001 | director | cc1 |
| e002 | manager | cc1_1 |
| e003 | manager | cc1_2 |
| e004 | director | cc2 |
| e005 | manager | cc2_1 |
| e006 | manager | cc2_2 |
| e007 | analyst | cc1_1 |
| e008 | analyst | cc1_1 |
| e009 | analyst | cc1_2 |
| e010 | analyst | cc1_2 |
| e011 | analyst | cc2_2 |
| e012 | analyst | cc2_1 |
| e013 | analyst | cc2_2 |
| e014 | analyst | cc2_2 |

## reports

An employee's direct manager.
Identified by: emp. References: `emp` refers to `emp`; `manager` refers to `emp`.

| emp | manager |
|---|---|
| e001 | e000 |
| e002 | e001 |
| e003 | e001 |
| e004 | e000 |
| e005 | e004 |
| e006 | e004 |
| e007 | e002 |
| e008 | e002 |
| e009 | e003 |
| e010 | e003 |
| e011 | e006 |
| e012 | e005 |
| e013 | e006 |
| e014 | e006 |

## role_limit

The approval limit currently attached to a role.
Identified by: role.

| role | limit |
|---|---|
| analyst | 5000 |
| manager | 40000 |
| senior_manager | 50000 |
| director | 100000 |
| vp | 500000 |

## vendor

A vendor and its current status (approved or suspended).
Identified by: vendor.

| vendor | status |
|---|---|
| acme | approved |
| bolt | suspended |
| cog | approved |
| dyne | approved |
| edge | approved |
| fern | suspended |

## req

A purchase request, raised on the given date; status is pending or cancelled.
Identified by: req. References: `requester` refers to `emp`; `vendor` refers to `vendor`.

| req | requester | amount | category | vendor | date | status |
|---|---|---|---|---|---|---|
| r001 | e011 | 3000 | hardware | cog | 2026-07-23 | pending |
| r002 | e008 | 90000 | capital | fern | 2026-06-22 | pending |
| r003 | e008 | 8000 | software | fern | 2026-08-08 | pending |
| r004 | e005 | 90000 | services | bolt | 2026-07-05 | pending |
| r005 | e010 | 120000 | hardware | dyne | 2026-06-28 | cancelled |
| r006 | e011 | 38000 | services | cog | 2026-09-10 | pending |
| r007 | e011 | 60000 | capital | cog | 2026-06-17 | pending |
| r008 | e004 | 12000 | software | cog | 2026-08-26 | pending |
| r009 | e009 | 60000 | capital | cog | 2026-08-01 | pending |
| r010 | e007 | 120000 | services | edge | 2026-06-15 | cancelled |
| r011 | e008 | 8000 | software | acme | 2026-09-12 | pending |
| r012 | e008 | 20000 | software | fern | 2026-07-04 | pending |
| r013 | e014 | 38000 | services | edge | 2026-08-14 | pending |
| r014 | e008 | 20000 | hardware | bolt | 2026-06-23 | pending |
| r015 | e011 | 12000 | hardware | fern | 2026-06-14 | pending |
| r016 | e002 | 90000 | hardware | bolt | 2026-07-02 | pending |
| r017 | e001 | 3000 | software | acme | 2026-08-27 | cancelled |
| r018 | e013 | 38000 | services | acme | 2026-06-19 | pending |

## emergency

A request flagged as an emergency.
Identified by: req. References: `req` refers to `req`.

| req |
|---|
| r002 |
| r004 |
| r015 |

## violation

An employee with a recorded policy violation.
Identified by: emp. References: `emp` refers to `emp`.

| emp |
|---|
| e008 |

## booked

Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| cc1_1 | 47000 |
| cc1_2 | 137000 |
| cc2_1 | 75000 |
| cc2_2 | 101000 |

## cap

The spending cap of a cost centre this quarter.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| company | 432000 |
| cc1 | 211000 |
| cc1_1 | 56000 |
| cc1_2 | 219000 |
| cc2 | 264000 |
| cc2_1 | 72000 |
| cc2_2 | 104000 |

## today

The date on which the material was compiled.
Identified by: date.

| date |
|---|
| 2026-09-15 |

## role_limit_version

A dated version of a role's approval limit, valid from and to the given dates inclusive.
Identified by: role, valid_from.

| role | limit | valid_from | valid_to |
|---|---|---|---|
| analyst | 5000 | 2026-01-01 | 2026-12-31 |
| manager | 25000 | 2026-01-01 | 2026-07-31 |
| manager | 40000 | 2026-08-01 | 2026-12-31 |
| senior_manager | 50000 | 2026-01-01 | 2026-12-31 |
| director | 100000 | 2026-01-01 | 2026-12-31 |
| vp | 500000 | 2026-01-01 | 2026-12-31 |

## vendor_status

A vendor's status during a period, from and to the given dates inclusive.
Identified by: vendor, valid_from. References: `vendor` refers to `vendor`.

| vendor | status | valid_from | valid_to |
|---|---|---|---|
| acme | approved | 2026-01-01 | 2026-12-31 |
| bolt | approved | 2026-01-01 | 2026-07-31 |
| bolt | suspended | 2026-08-01 | 2026-12-31 |
| cog | approved | 2026-01-01 | 2026-12-31 |
| dyne | suspended | 2026-01-01 | 2026-06-30 |
| dyne | approved | 2026-07-01 | 2026-12-31 |
| edge | approved | 2026-01-01 | 2026-12-31 |
| fern | suspended | 2026-01-01 | 2026-12-31 |

## assignment

A source's record (hr or finance) that an employee belongs to a cost centre from the effective date on.
Identified by: emp, source, effective. References: `emp` refers to `emp`; `cc` refers to `cc`.

| emp | cc | source | effective |
|---|---|---|---|
| e000 | company | finance | 2026-01-01 |
| e000 | company | hr | 2026-01-01 |
| e001 | cc1 | finance | 2026-01-01 |
| e001 | cc1 | hr | 2026-01-01 |
| e002 | cc1_1 | finance | 2026-01-01 |
| e002 | cc1_1 | hr | 2026-01-01 |
| e003 | cc1_2 | finance | 2026-01-01 |
| e003 | cc1_2 | hr | 2026-01-01 |
| e004 | cc2 | finance | 2026-01-01 |
| e004 | cc2 | hr | 2026-01-01 |
| e005 | cc2_1 | finance | 2026-01-01 |
| e005 | cc2_1 | hr | 2026-01-01 |
| e006 | cc2_2 | finance | 2026-01-01 |
| e006 | cc2_2 | hr | 2026-01-01 |
| e007 | cc1_1 | finance | 2026-01-01 |
| e007 | cc1_1 | hr | 2026-01-01 |
| e008 | cc1_1 | finance | 2026-01-01 |
| e008 | cc1_1 | hr | 2026-01-01 |
| e009 | cc1_2 | finance | 2026-01-01 |
| e009 | cc1_2 | hr | 2026-01-01 |
| e010 | cc1_2 | finance | 2026-01-01 |
| e010 | cc1_2 | hr | 2026-01-01 |
| e011 | cc2_1 | finance | 2026-01-01 |
| e011 | cc2_2 | finance | 2026-07-18 |
| e011 | cc2_1 | hr | 2026-01-01 |
| e011 | cc2_2 | hr | 2026-06-19 |
| e012 | cc2_1 | finance | 2026-01-01 |
| e012 | cc2_1 | hr | 2026-01-01 |
| e013 | cc2_2 | finance | 2026-01-01 |
| e013 | cc2_2 | hr | 2026-01-01 |
| e013 | cc1_1 | hr | 2026-09-02 |
| e014 | cc2_2 | finance | 2026-01-01 |
| e014 | cc2_2 | hr | 2026-01-01 |

## exemption

An exemption from the cap check for one request category, granted on a date.
Identified by: exemption.

| exemption | category | granted |
|---|---|---|
| capex | capital | 2026-01-01 |

## exemption_withdrawn

The date an exemption was withdrawn; it no longer applies from that date on.
Identified by: exemption. References: `exemption` refers to `exemption`.

| exemption | date |
|---|---|
| capex | 2026-08-10 |

# Terms

What the terms used below refer to in the records.

- **requester** (`req.requester`): The requester of a request is the employee who raised it.
- **requester's cost centre** (`emp.cc`): A requester's cost centre is the cost centre recorded for them in emp.
- **pending request** (`req.status = pending`): A pending request is one whose status is pending. Cancelled requests are neither pending nor booked.
- **booked amount** (`booked.amount`): The booked amount of a cost centre is what is booked directly on it. Its booked total is defined separately (R104).
- **cap** (`cap.amount`): The cap of a cost centre bounds its committed spend (R106).
- **manager** (`reports.manager`): An employee's manager is their direct manager only. Their reporting chain (R103) goes further up.
- **organisational unit** (`org_unit.unit`): The organisational unit of a cost centre is a grouping of cost centres. An employee's department is defined separately (R113).

# Definitions

Each definition has a rule id. A definition applies wherever its term is used.

- **R101.** The ancestors of a cost centre are its parent, its parent's parent, and so on.
- **R102.** A cost centre lies in the subtree of a cost centre X if it is X or one of X's descendants.
- **R103.** An employee's reporting chain is their manager, their manager's manager, and so on. It does not include the employee.
- **Open question c6** (owner: controller), on booked total: Does the booked total of a cost centre include what is booked on its descendants, or only what is booked directly on it? This has not been decided. The readings are:
  - with_descendants (R104): The booked total of a cost centre is the sum of the booked amounts of every cost centre in its subtree (zero where nothing is booked).
  - direct_only (R104b): The booked total of a cost centre is its own booked amount, not counting its descendants (zero where nothing is booked).
- **R105.** The pending total of a cost centre is the sum of the amounts of pending requests whose requester's cost centre lies in its subtree.
- **Open question c1** (owner: controller), on committed spend: Does the committed spend of a cost centre include pending requests? This has not been decided. The readings are:
  - booked_only (R106): The committed spend of a cost centre is its booked total. Pending requests do not count.
  - with_pending (R106b): The committed spend of a cost centre is its booked total plus its pending total.
- **R107.** The headroom of a cost centre is its cap minus its committed spend.
- **R108.** A cost centre is over cap if its committed spend exceeds its cap.
- **Open question c4** (owner: controller), on cap scope: Does a request's cap check cover only the requester's cost centre, or also every ancestor of it? This has not been decided. The readings are:
  - with_ancestors (R109): A request's cap scope is its requester's cost centre and every ancestor of that cost centre.
  - own_only (R109b): A request's cap scope is its requester's cost centre only.
- **R110.** A request's exposure at a cost centre in its cap scope is that centre's committed spend plus the request amount, not counting the request itself twice if committed spend already includes it.
- **R111.** A request breaches a cap if its exposure at some cost centre in its cap scope exceeds that centre's cap.
- **R112.** A big capital request is a capital request whose amount is over 50000.
- **Open question c3** (owner: hr), on department: Is an employee's department their cost centre or their cost centre's organisational unit? This has not been decided. The readings are:
  - cost_centre (R113): An employee's department is their cost centre.
  - org_unit (R113b): An employee's department is the organisational unit of their cost centre.
- **R114.** The headcount of a department is the number of employees whose department it is.
- **Open question c2** (owner: procurement), on governing date: Which date governs a request's dated rules (approval limits, vendor status, exemptions), the request date or today? This has not been decided. The readings are:
  - request_date (R201): A request's dated rules (approval limits, vendor status, exemptions) are read as of the date the request was raised.
  - today (R201b): A request's dated rules (approval limits, vendor status, exemptions) are read as of today.
- **R202.** A role's approval limit on a date is the limit of the version valid on that date.
- **R203.** A vendor's status on a date is the status of the period that contains that date.
- **R204.** A request's vendor is approved for it if the vendor's status on the request's governing date is approved.
- **R205.** According to a source, an employee belongs on a date to the cost centre of that source's latest assignment record effective on or before that date.
- **R206.** An employee's cost centre is disputed on a date if hr and finance place them in different cost centres on that date.
- **R207.** An exemption is in force on a date if it was granted on or before that date and not withdrawn on or before that date.
- **R301.** Someone may approve a request if they are in the requester's reporting chain and their role's approval limit on the request's governing date is at least the request amount.
- **R302.** A request has an approver if someone may approve it.
- **R303.** Exception to the cap check: a request is exempt from it if an exemption for its category is in force on its governing date.
- **R304.** A request passes the cap check if it breaches no cap or is exempt from the cap check.
- **R305.** A request passes the vendor check if its vendor is approved for it, or if the emergency waiver applies to it.
- **R306.** Exception to the vendor check: an emergency request whose vendor is suspended on its governing date is waived through the vendor check.
- **R307.** Exception to the emergency waiver: the waiver does not apply to a big capital request.
- **R308.** A request is eligible if it has an approver, passes the cap check and passes the vendor check.
- **R309.** A request is denied if its requester has a recorded policy violation.
- **R310.** A request is approved if it is eligible and not denied. Denial overrides eligibility.
- **R311.** A software request under 10000 is approved automatically, without further checks.
- **R312.** An automatically approved request is approved.
- **R313.** Where hr and finance disagree about an employee's cost centre, finance governs.
