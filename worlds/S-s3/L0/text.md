# Procurement records (L0)

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
| cc1_1 | support |
| cc1_2 | delivery |
| cc2 | leadership |
| cc2_1 | delivery |
| cc2_2 | support |

## emp

An employee, their role, and their cost centre in the finance system of record.
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
| e008 | analyst | cc1_2 |
| e009 | analyst | cc1_2 |
| e010 | analyst | cc1_2 |
| e011 | analyst | cc2_1 |
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
| e008 | e003 |
| e009 | e003 |
| e010 | e003 |
| e011 | e005 |
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
| r001 | e008 | 20000 | hardware | fern | 2026-07-08 | pending |
| r002 | e006 | 12000 | services | cog | 2026-08-03 | pending |
| r003 | e004 | 45000 | hardware | acme | 2026-08-27 | pending |
| r004 | e014 | 12000 | hardware | fern | 2026-07-12 | pending |
| r005 | e014 | 38000 | services | acme | 2026-06-09 | pending |
| r006 | e003 | 120000 | hardware | bolt | 2026-08-08 | pending |
| r007 | e009 | 60000 | software | dyne | 2026-08-25 | pending |
| r008 | e010 | 8000 | software | acme | 2026-08-26 | pending |
| r009 | e009 | 38000 | services | fern | 2026-07-31 | pending |
| r010 | e014 | 60000 | capital | cog | 2026-06-25 | pending |
| r011 | e013 | 3000 | software | fern | 2026-06-19 | pending |
| r012 | e009 | 45000 | capital | cog | 2026-08-18 | pending |
| r013 | e014 | 120000 | services | cog | 2026-09-01 | pending |
| r014 | e004 | 90000 | hardware | bolt | 2026-07-22 | pending |
| r015 | e009 | 20000 | software | fern | 2026-06-27 | cancelled |
| r016 | e009 | 20000 | hardware | bolt | 2026-06-01 | pending |
| r017 | e007 | 38000 | software | fern | 2026-08-25 | pending |
| r018 | e013 | 90000 | capital | fern | 2026-08-29 | pending |

## emergency

A request flagged as an emergency.
Identified by: req. References: `req` refers to `req`.

| req |
|---|
| r002 |
| r004 |
| r011 |
| r015 |
| r018 |

## violation

An employee with a recorded policy violation.
Identified by: emp. References: `emp` refers to `emp`.

| emp |
|---|
| e010 |

## booked

Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| cc1_1 | 112000 |
| cc1_2 | 83000 |
| cc2_1 | 93000 |
| cc2_2 | 43000 |

## cap

The spending cap of a cost centre this quarter.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| company | 397000 |
| cc1 | 292000 |
| cc1_1 | 134000 |
| cc1_2 | 116000 |
| cc2 | 156000 |
| cc2_1 | 95000 |
| cc2_2 | 47000 |
