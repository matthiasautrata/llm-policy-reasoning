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
org_unit(cc1_2, support).
org_unit(cc2, leadership).
org_unit(cc2_1, support).
org_unit(cc2_2, delivery).

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
emp(e008, analyst, cc1_1).
emp(e009, analyst, cc1_2).
emp(e010, analyst, cc1_2).
emp(e011, analyst, cc2_1).
emp(e012, analyst, cc2_2).
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
reports(e008, e002).
reports(e009, e003).
reports(e010, e003).
reports(e011, e005).
reports(e012, e006).
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
req(r001, e013, 38000, hardware, cog, 20260617, pending).
req(r002, e008, 8000, software, edge, 20260724, cancelled).
req(r003, e010, 38000, services, acme, 20260617, pending).
req(r004, e011, 60000, capital, cog, 20260624, pending).
req(r005, e002, 12000, software, dyne, 20260907, pending).
req(r006, e005, 12000, software, bolt, 20260818, pending).
req(r007, e009, 8000, software, acme, 20260620, pending).
req(r008, e011, 12000, hardware, fern, 20260612, pending).
req(r009, e005, 3000, hardware, fern, 20260727, pending).
req(r010, e014, 90000, capital, fern, 20260719, pending).
req(r011, e003, 3000, capital, fern, 20260604, pending).
req(r012, e009, 120000, software, dyne, 20260831, pending).
req(r013, e007, 60000, hardware, fern, 20260906, pending).
req(r014, e011, 30000, software, dyne, 20260712, pending).
req(r015, e011, 20000, hardware, bolt, 20260730, pending).
req(r016, e014, 90000, capital, cog, 20260829, pending).
req(r017, e003, 45000, software, bolt, 20260610, pending).
req(r018, e007, 30000, software, edge, 20260820, pending).

% emergency(Req): A request flagged as an emergency.
:- dynamic emergency/1.
emergency(r008).
emergency(r010).
emergency(r017).

% violation(Emp): An employee with a recorded policy violation.
:- dynamic violation/1.
violation(e009).

% booked(Cc, Amount): Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
:- dynamic booked/2.
booked(cc1_1, 122000).
booked(cc1_2, 120000).
booked(cc2_1, 98000).
booked(cc2_2, 110000).

% cap(Cc, Amount): The spending cap of a cost centre this quarter.
:- dynamic cap/2.
cap(company, 630000).
cap(cc1, 254000).
cap(cc1_1, 134000).
cap(cc1_2, 132000).
cap(cc2, 312000).
cap(cc2_1, 95000).
cap(cc2_2, 132000).
