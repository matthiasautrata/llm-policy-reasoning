% Procurement world, layer L0: base relations. Dates are integers YYYYMMDD.

% Schema: relation(Name). column(Relation, Column, Position, Type). key(Relation, FirstKeyColumn). fk(Relation, Column, ReferencedRelation).
relation(cc).
column(cc, cc, 1, id).
key(cc, cc).
relation(cc_parent).
column(cc_parent, cc, 1, id).
column(cc_parent, parent, 2, id).
key(cc_parent, cc).
fk(cc_parent, cc, cc).
fk(cc_parent, parent, cc).
relation(org_unit).
column(org_unit, cc, 1, id).
column(org_unit, unit, 2, enum).
key(org_unit, cc).
fk(org_unit, cc, cc).
relation(emp).
column(emp, emp, 1, id).
column(emp, role, 2, enum).
column(emp, cc, 3, id).
key(emp, emp).
fk(emp, cc, cc).
relation(reports).
column(reports, emp, 1, id).
column(reports, manager, 2, id).
key(reports, emp).
fk(reports, emp, emp).
fk(reports, manager, emp).
relation(role_limit).
column(role_limit, role, 1, enum).
column(role_limit, limit, 2, int).
key(role_limit, role).
relation(vendor).
column(vendor, vendor, 1, id).
column(vendor, status, 2, enum).
key(vendor, vendor).
relation(req).
column(req, req, 1, id).
column(req, requester, 2, id).
column(req, amount, 3, int).
column(req, category, 4, enum).
column(req, vendor, 5, id).
column(req, date, 6, date).
column(req, status, 7, enum).
key(req, req).
fk(req, requester, emp).
fk(req, vendor, vendor).
relation(emergency).
column(emergency, req, 1, id).
key(emergency, req).
fk(emergency, req, req).
relation(violation).
column(violation, emp, 1, id).
key(violation, emp).
fk(violation, emp, emp).
relation(booked).
column(booked, cc, 1, id).
column(booked, amount, 2, int).
key(booked, cc).
fk(booked, cc, cc).
relation(cap).
column(cap, cc, 1, id).
column(cap, amount, 2, int).
key(cap, cc).
fk(cap, cc, cc).

% cc(Cc): A cost centre.
:- dynamic cc/1.
cc(company).
cc(cc1).
cc(cc1_1).
cc(cc1_2).
cc(cc2).
cc(cc2_1).
cc(cc2_2).

% cc_parent(Cc, Parent): The parent of a cost centre. The root cost centre has no row.
:- dynamic cc_parent/2.
cc_parent(cc1, company).
cc_parent(cc1_1, cc1).
cc_parent(cc1_2, cc1).
cc_parent(cc2, company).
cc_parent(cc2_1, cc2).
cc_parent(cc2_2, cc2).

% org_unit(Cc, Unit): The organisational unit a cost centre belongs to.
:- dynamic org_unit/2.
org_unit(company, leadership).
org_unit(cc1, leadership).
org_unit(cc1_1, support).
org_unit(cc1_2, delivery).
org_unit(cc2, leadership).
org_unit(cc2_1, delivery).
org_unit(cc2_2, support).

% emp(Emp, Role, Cc): An employee, their role, and their cost centre in the finance system of record.
:- dynamic emp/3.
emp(e000, vp, company).
emp(e001, director, cc1).
emp(e002, manager, cc1_1).
emp(e003, manager, cc1_2).
emp(e004, director, cc2).
emp(e005, manager, cc2_1).
emp(e006, manager, cc2_2).
emp(e007, analyst, cc1_1).
emp(e008, analyst, cc1_2).
emp(e009, analyst, cc1_2).
emp(e010, analyst, cc1_2).
emp(e011, analyst, cc2_1).
emp(e012, analyst, cc2_1).
emp(e013, analyst, cc2_2).
emp(e014, analyst, cc2_2).

% reports(Emp, Manager): An employee's direct manager.
:- dynamic reports/2.
reports(e001, e000).
reports(e002, e001).
reports(e003, e001).
reports(e004, e000).
reports(e005, e004).
reports(e006, e004).
reports(e007, e002).
reports(e008, e003).
reports(e009, e003).
reports(e010, e003).
reports(e011, e005).
reports(e012, e005).
reports(e013, e006).
reports(e014, e006).

% role_limit(Role, Limit): The approval limit currently attached to a role.
:- dynamic role_limit/2.
role_limit(analyst, 5000).
role_limit(manager, 40000).
role_limit(senior_manager, 50000).
role_limit(director, 100000).
role_limit(vp, 500000).

% vendor(Vendor, Status): A vendor and its current status (approved or suspended).
:- dynamic vendor/2.
vendor(acme, approved).
vendor(bolt, suspended).
vendor(cog, approved).
vendor(dyne, approved).
vendor(edge, approved).
vendor(fern, suspended).

% req(Req, Requester, Amount, Category, Vendor, Date, Status): A purchase request, raised on the given date; status is pending or cancelled.
:- dynamic req/7.
req(r001, e008, 20000, hardware, fern, 20260708, pending).
req(r002, e006, 12000, services, cog, 20260803, pending).
req(r003, e004, 45000, hardware, acme, 20260827, pending).
req(r004, e014, 12000, hardware, fern, 20260712, pending).
req(r005, e014, 38000, services, acme, 20260609, pending).
req(r006, e003, 120000, hardware, bolt, 20260808, pending).
req(r007, e009, 60000, software, dyne, 20260825, pending).
req(r008, e010, 8000, software, acme, 20260826, pending).
req(r009, e009, 38000, services, fern, 20260731, pending).
req(r010, e014, 60000, capital, cog, 20260625, pending).
req(r011, e013, 3000, software, fern, 20260619, pending).
req(r012, e009, 45000, capital, cog, 20260818, pending).
req(r013, e014, 120000, services, cog, 20260901, pending).
req(r014, e004, 90000, hardware, bolt, 20260722, pending).
req(r015, e009, 20000, software, fern, 20260627, cancelled).
req(r016, e009, 20000, hardware, bolt, 20260601, pending).
req(r017, e007, 38000, software, fern, 20260825, pending).
req(r018, e013, 90000, capital, fern, 20260829, pending).

% emergency(Req): A request flagged as an emergency.
:- dynamic emergency/1.
emergency(r002).
emergency(r004).
emergency(r011).
emergency(r015).
emergency(r018).

% violation(Emp): An employee with a recorded policy violation.
:- dynamic violation/1.
violation(e010).

% booked(Cc, Amount): Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
:- dynamic booked/2.
booked(cc1_1, 112000).
booked(cc1_2, 83000).
booked(cc2_1, 93000).
booked(cc2_2, 43000).

% cap(Cc, Amount): The spending cap of a cost centre this quarter.
:- dynamic cap/2.
cap(company, 397000).
cap(cc1, 292000).
cap(cc1_1, 134000).
cap(cc1_2, 116000).
cap(cc2, 156000).
cap(cc2_1, 95000).
cap(cc2_2, 47000).
