% Procurement world, layer L2: base relations, terms, definitions and open questions. Dates are integers YYYYMMDD.

:- discontiguous relation/1, column/4, key/2, fk/3.
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
relation(today).
column(today, date, 1, date).
key(today, date).
relation(role_limit_version).
column(role_limit_version, role, 1, enum).
column(role_limit_version, limit, 2, int).
column(role_limit_version, valid_from, 3, date).
column(role_limit_version, valid_to, 4, date).
key(role_limit_version, role).
relation(vendor_status).
column(vendor_status, vendor, 1, id).
column(vendor_status, status, 2, enum).
column(vendor_status, valid_from, 3, date).
column(vendor_status, valid_to, 4, date).
key(vendor_status, vendor).
fk(vendor_status, vendor, vendor).
relation(assignment).
column(assignment, emp, 1, id).
column(assignment, cc, 2, id).
column(assignment, source, 3, enum).
column(assignment, effective, 4, date).
key(assignment, emp).
fk(assignment, emp, emp).
fk(assignment, cc, cc).
relation(exemption).
column(exemption, exemption, 1, id).
column(exemption, category, 2, enum).
column(exemption, granted, 3, date).
key(exemption, exemption).
relation(exemption_withdrawn).
column(exemption_withdrawn, exemption, 1, id).
column(exemption_withdrawn, date, 2, date).
key(exemption_withdrawn, exemption).
fk(exemption_withdrawn, exemption, exemption).

% cc(Cc): A cost centre.
:- dynamic cc/1.
cc(company).
cc(cc1).
cc(cc1_1).
cc(cc1_1_1).
cc(cc1_1_1_1).
cc(cc1_1_1_2).
cc(cc1_1_1_3).
cc(cc1_1_2).
cc(cc1_1_2_1).
cc(cc1_1_2_2).
cc(cc1_1_2_3).
cc(cc1_1_3).
cc(cc1_1_3_1).
cc(cc1_1_3_2).
cc(cc1_1_3_3).
cc(cc1_2).
cc(cc1_2_1).
cc(cc1_2_1_1).
cc(cc1_2_1_2).
cc(cc1_2_1_3).
cc(cc1_2_2).
cc(cc1_2_2_1).
cc(cc1_2_2_2).
cc(cc1_2_2_3).
cc(cc1_2_3).
cc(cc1_2_3_1).
cc(cc1_2_3_2).
cc(cc1_2_3_3).
cc(cc1_3).
cc(cc1_3_1).
cc(cc1_3_1_1).
cc(cc1_3_1_2).
cc(cc1_3_1_3).
cc(cc1_3_2).
cc(cc1_3_2_1).
cc(cc1_3_2_2).
cc(cc1_3_2_3).
cc(cc1_3_3).
cc(cc1_3_3_1).
cc(cc1_3_3_2).
cc(cc1_3_3_3).
cc(cc2).
cc(cc2_1).
cc(cc2_1_1).
cc(cc2_1_1_1).
cc(cc2_1_1_2).
cc(cc2_1_1_3).
cc(cc2_1_2).
cc(cc2_1_2_1).
cc(cc2_1_2_2).
cc(cc2_1_2_3).
cc(cc2_1_3).
cc(cc2_1_3_1).
cc(cc2_1_3_2).
cc(cc2_1_3_3).
cc(cc2_2).
cc(cc2_2_1).
cc(cc2_2_1_1).
cc(cc2_2_1_2).
cc(cc2_2_1_3).
cc(cc2_2_2).
cc(cc2_2_2_1).
cc(cc2_2_2_2).
cc(cc2_2_2_3).
cc(cc2_2_3).
cc(cc2_2_3_1).
cc(cc2_2_3_2).
cc(cc2_2_3_3).
cc(cc2_3).
cc(cc2_3_1).
cc(cc2_3_1_1).
cc(cc2_3_1_2).
cc(cc2_3_1_3).
cc(cc2_3_2).
cc(cc2_3_2_1).
cc(cc2_3_2_2).
cc(cc2_3_2_3).
cc(cc2_3_3).
cc(cc2_3_3_1).
cc(cc2_3_3_2).
cc(cc2_3_3_3).
cc(cc3).
cc(cc3_1).
cc(cc3_1_1).
cc(cc3_1_1_1).
cc(cc3_1_1_2).
cc(cc3_1_1_3).
cc(cc3_1_2).
cc(cc3_1_2_1).
cc(cc3_1_2_2).
cc(cc3_1_2_3).
cc(cc3_1_3).
cc(cc3_1_3_1).
cc(cc3_1_3_2).
cc(cc3_1_3_3).
cc(cc3_2).
cc(cc3_2_1).
cc(cc3_2_1_1).
cc(cc3_2_1_2).
cc(cc3_2_1_3).
cc(cc3_2_2).
cc(cc3_2_2_1).
cc(cc3_2_2_2).
cc(cc3_2_2_3).
cc(cc3_2_3).
cc(cc3_2_3_1).
cc(cc3_2_3_2).
cc(cc3_2_3_3).
cc(cc3_3).
cc(cc3_3_1).
cc(cc3_3_1_1).
cc(cc3_3_1_2).
cc(cc3_3_1_3).
cc(cc3_3_2).
cc(cc3_3_2_1).
cc(cc3_3_2_2).
cc(cc3_3_2_3).
cc(cc3_3_3).
cc(cc3_3_3_1).
cc(cc3_3_3_2).
cc(cc3_3_3_3).

% cc_parent(Cc, Parent): The parent of a cost centre. The root cost centre has no row.
:- dynamic cc_parent/2.
cc_parent(cc1, company).
cc_parent(cc1_1, cc1).
cc_parent(cc1_1_1, cc1_1).
cc_parent(cc1_1_1_1, cc1_1_1).
cc_parent(cc1_1_1_2, cc1_1_1).
cc_parent(cc1_1_1_3, cc1_1_1).
cc_parent(cc1_1_2, cc1_1).
cc_parent(cc1_1_2_1, cc1_1_2).
cc_parent(cc1_1_2_2, cc1_1_2).
cc_parent(cc1_1_2_3, cc1_1_2).
cc_parent(cc1_1_3, cc1_1).
cc_parent(cc1_1_3_1, cc1_1_3).
cc_parent(cc1_1_3_2, cc1_1_3).
cc_parent(cc1_1_3_3, cc1_1_3).
cc_parent(cc1_2, cc1).
cc_parent(cc1_2_1, cc1_2).
cc_parent(cc1_2_1_1, cc1_2_1).
cc_parent(cc1_2_1_2, cc1_2_1).
cc_parent(cc1_2_1_3, cc1_2_1).
cc_parent(cc1_2_2, cc1_2).
cc_parent(cc1_2_2_1, cc1_2_2).
cc_parent(cc1_2_2_2, cc1_2_2).
cc_parent(cc1_2_2_3, cc1_2_2).
cc_parent(cc1_2_3, cc1_2).
cc_parent(cc1_2_3_1, cc1_2_3).
cc_parent(cc1_2_3_2, cc1_2_3).
cc_parent(cc1_2_3_3, cc1_2_3).
cc_parent(cc1_3, cc1).
cc_parent(cc1_3_1, cc1_3).
cc_parent(cc1_3_1_1, cc1_3_1).
cc_parent(cc1_3_1_2, cc1_3_1).
cc_parent(cc1_3_1_3, cc1_3_1).
cc_parent(cc1_3_2, cc1_3).
cc_parent(cc1_3_2_1, cc1_3_2).
cc_parent(cc1_3_2_2, cc1_3_2).
cc_parent(cc1_3_2_3, cc1_3_2).
cc_parent(cc1_3_3, cc1_3).
cc_parent(cc1_3_3_1, cc1_3_3).
cc_parent(cc1_3_3_2, cc1_3_3).
cc_parent(cc1_3_3_3, cc1_3_3).
cc_parent(cc2, company).
cc_parent(cc2_1, cc2).
cc_parent(cc2_1_1, cc2_1).
cc_parent(cc2_1_1_1, cc2_1_1).
cc_parent(cc2_1_1_2, cc2_1_1).
cc_parent(cc2_1_1_3, cc2_1_1).
cc_parent(cc2_1_2, cc2_1).
cc_parent(cc2_1_2_1, cc2_1_2).
cc_parent(cc2_1_2_2, cc2_1_2).
cc_parent(cc2_1_2_3, cc2_1_2).
cc_parent(cc2_1_3, cc2_1).
cc_parent(cc2_1_3_1, cc2_1_3).
cc_parent(cc2_1_3_2, cc2_1_3).
cc_parent(cc2_1_3_3, cc2_1_3).
cc_parent(cc2_2, cc2).
cc_parent(cc2_2_1, cc2_2).
cc_parent(cc2_2_1_1, cc2_2_1).
cc_parent(cc2_2_1_2, cc2_2_1).
cc_parent(cc2_2_1_3, cc2_2_1).
cc_parent(cc2_2_2, cc2_2).
cc_parent(cc2_2_2_1, cc2_2_2).
cc_parent(cc2_2_2_2, cc2_2_2).
cc_parent(cc2_2_2_3, cc2_2_2).
cc_parent(cc2_2_3, cc2_2).
cc_parent(cc2_2_3_1, cc2_2_3).
cc_parent(cc2_2_3_2, cc2_2_3).
cc_parent(cc2_2_3_3, cc2_2_3).
cc_parent(cc2_3, cc2).
cc_parent(cc2_3_1, cc2_3).
cc_parent(cc2_3_1_1, cc2_3_1).
cc_parent(cc2_3_1_2, cc2_3_1).
cc_parent(cc2_3_1_3, cc2_3_1).
cc_parent(cc2_3_2, cc2_3).
cc_parent(cc2_3_2_1, cc2_3_2).
cc_parent(cc2_3_2_2, cc2_3_2).
cc_parent(cc2_3_2_3, cc2_3_2).
cc_parent(cc2_3_3, cc2_3).
cc_parent(cc2_3_3_1, cc2_3_3).
cc_parent(cc2_3_3_2, cc2_3_3).
cc_parent(cc2_3_3_3, cc2_3_3).
cc_parent(cc3, company).
cc_parent(cc3_1, cc3).
cc_parent(cc3_1_1, cc3_1).
cc_parent(cc3_1_1_1, cc3_1_1).
cc_parent(cc3_1_1_2, cc3_1_1).
cc_parent(cc3_1_1_3, cc3_1_1).
cc_parent(cc3_1_2, cc3_1).
cc_parent(cc3_1_2_1, cc3_1_2).
cc_parent(cc3_1_2_2, cc3_1_2).
cc_parent(cc3_1_2_3, cc3_1_2).
cc_parent(cc3_1_3, cc3_1).
cc_parent(cc3_1_3_1, cc3_1_3).
cc_parent(cc3_1_3_2, cc3_1_3).
cc_parent(cc3_1_3_3, cc3_1_3).
cc_parent(cc3_2, cc3).
cc_parent(cc3_2_1, cc3_2).
cc_parent(cc3_2_1_1, cc3_2_1).
cc_parent(cc3_2_1_2, cc3_2_1).
cc_parent(cc3_2_1_3, cc3_2_1).
cc_parent(cc3_2_2, cc3_2).
cc_parent(cc3_2_2_1, cc3_2_2).
cc_parent(cc3_2_2_2, cc3_2_2).
cc_parent(cc3_2_2_3, cc3_2_2).
cc_parent(cc3_2_3, cc3_2).
cc_parent(cc3_2_3_1, cc3_2_3).
cc_parent(cc3_2_3_2, cc3_2_3).
cc_parent(cc3_2_3_3, cc3_2_3).
cc_parent(cc3_3, cc3).
cc_parent(cc3_3_1, cc3_3).
cc_parent(cc3_3_1_1, cc3_3_1).
cc_parent(cc3_3_1_2, cc3_3_1).
cc_parent(cc3_3_1_3, cc3_3_1).
cc_parent(cc3_3_2, cc3_3).
cc_parent(cc3_3_2_1, cc3_3_2).
cc_parent(cc3_3_2_2, cc3_3_2).
cc_parent(cc3_3_2_3, cc3_3_2).
cc_parent(cc3_3_3, cc3_3).
cc_parent(cc3_3_3_1, cc3_3_3).
cc_parent(cc3_3_3_2, cc3_3_3).
cc_parent(cc3_3_3_3, cc3_3_3).

% org_unit(Cc, Unit): The organisational unit a cost centre belongs to.
:- dynamic org_unit/2.
org_unit(company, leadership).
org_unit(cc1, leadership).
org_unit(cc1_1, leadership).
org_unit(cc1_1_1, leadership).
org_unit(cc1_1_1_1, support).
org_unit(cc1_1_1_2, delivery).
org_unit(cc1_1_1_3, support).
org_unit(cc1_1_2, leadership).
org_unit(cc1_1_2_1, delivery).
org_unit(cc1_1_2_2, support).
org_unit(cc1_1_2_3, support).
org_unit(cc1_1_3, leadership).
org_unit(cc1_1_3_1, delivery).
org_unit(cc1_1_3_2, support).
org_unit(cc1_1_3_3, support).
org_unit(cc1_2, leadership).
org_unit(cc1_2_1, leadership).
org_unit(cc1_2_1_1, support).
org_unit(cc1_2_1_2, support).
org_unit(cc1_2_1_3, delivery).
org_unit(cc1_2_2, leadership).
org_unit(cc1_2_2_1, support).
org_unit(cc1_2_2_2, support).
org_unit(cc1_2_2_3, support).
org_unit(cc1_2_3, leadership).
org_unit(cc1_2_3_1, support).
org_unit(cc1_2_3_2, support).
org_unit(cc1_2_3_3, delivery).
org_unit(cc1_3, leadership).
org_unit(cc1_3_1, leadership).
org_unit(cc1_3_1_1, delivery).
org_unit(cc1_3_1_2, delivery).
org_unit(cc1_3_1_3, support).
org_unit(cc1_3_2, leadership).
org_unit(cc1_3_2_1, delivery).
org_unit(cc1_3_2_2, support).
org_unit(cc1_3_2_3, support).
org_unit(cc1_3_3, leadership).
org_unit(cc1_3_3_1, delivery).
org_unit(cc1_3_3_2, support).
org_unit(cc1_3_3_3, support).
org_unit(cc2, leadership).
org_unit(cc2_1, leadership).
org_unit(cc2_1_1, leadership).
org_unit(cc2_1_1_1, support).
org_unit(cc2_1_1_2, delivery).
org_unit(cc2_1_1_3, support).
org_unit(cc2_1_2, leadership).
org_unit(cc2_1_2_1, delivery).
org_unit(cc2_1_2_2, delivery).
org_unit(cc2_1_2_3, delivery).
org_unit(cc2_1_3, leadership).
org_unit(cc2_1_3_1, support).
org_unit(cc2_1_3_2, support).
org_unit(cc2_1_3_3, support).
org_unit(cc2_2, leadership).
org_unit(cc2_2_1, leadership).
org_unit(cc2_2_1_1, support).
org_unit(cc2_2_1_2, delivery).
org_unit(cc2_2_1_3, support).
org_unit(cc2_2_2, leadership).
org_unit(cc2_2_2_1, delivery).
org_unit(cc2_2_2_2, delivery).
org_unit(cc2_2_2_3, delivery).
org_unit(cc2_2_3, leadership).
org_unit(cc2_2_3_1, support).
org_unit(cc2_2_3_2, support).
org_unit(cc2_2_3_3, support).
org_unit(cc2_3, leadership).
org_unit(cc2_3_1, leadership).
org_unit(cc2_3_1_1, support).
org_unit(cc2_3_1_2, delivery).
org_unit(cc2_3_1_3, delivery).
org_unit(cc2_3_2, leadership).
org_unit(cc2_3_2_1, support).
org_unit(cc2_3_2_2, support).
org_unit(cc2_3_2_3, support).
org_unit(cc2_3_3, leadership).
org_unit(cc2_3_3_1, delivery).
org_unit(cc2_3_3_2, support).
org_unit(cc2_3_3_3, delivery).
org_unit(cc3, leadership).
org_unit(cc3_1, leadership).
org_unit(cc3_1_1, leadership).
org_unit(cc3_1_1_1, support).
org_unit(cc3_1_1_2, support).
org_unit(cc3_1_1_3, delivery).
org_unit(cc3_1_2, leadership).
org_unit(cc3_1_2_1, support).
org_unit(cc3_1_2_2, support).
org_unit(cc3_1_2_3, support).
org_unit(cc3_1_3, leadership).
org_unit(cc3_1_3_1, support).
org_unit(cc3_1_3_2, delivery).
org_unit(cc3_1_3_3, support).
org_unit(cc3_2, leadership).
org_unit(cc3_2_1, leadership).
org_unit(cc3_2_1_1, delivery).
org_unit(cc3_2_1_2, support).
org_unit(cc3_2_1_3, support).
org_unit(cc3_2_2, leadership).
org_unit(cc3_2_2_1, delivery).
org_unit(cc3_2_2_2, support).
org_unit(cc3_2_2_3, support).
org_unit(cc3_2_3, leadership).
org_unit(cc3_2_3_1, delivery).
org_unit(cc3_2_3_2, support).
org_unit(cc3_2_3_3, delivery).
org_unit(cc3_3, leadership).
org_unit(cc3_3_1, leadership).
org_unit(cc3_3_1_1, support).
org_unit(cc3_3_1_2, support).
org_unit(cc3_3_1_3, support).
org_unit(cc3_3_2, leadership).
org_unit(cc3_3_2_1, support).
org_unit(cc3_3_2_2, delivery).
org_unit(cc3_3_2_3, delivery).
org_unit(cc3_3_3, leadership).
org_unit(cc3_3_3_1, delivery).
org_unit(cc3_3_3_2, delivery).
org_unit(cc3_3_3_3, delivery).

% emp(Emp, Role, Cc): An employee, their role, and their current cost centre as finance records it.
:- dynamic emp/3.
emp(e000, vp, company).
emp(e001, director, cc1).
emp(e002, senior_manager, cc1_1).
emp(e003, senior_manager, cc1_1_1).
emp(e004, manager, cc1_1_1_1).
emp(e005, manager, cc1_1_1_2).
emp(e006, manager, cc1_1_1_3).
emp(e007, senior_manager, cc1_1_2).
emp(e008, manager, cc1_1_2_1).
emp(e009, manager, cc1_1_2_2).
emp(e010, manager, cc1_1_2_3).
emp(e011, senior_manager, cc1_1_3).
emp(e012, manager, cc1_1_3_1).
emp(e013, manager, cc1_1_3_2).
emp(e014, manager, cc1_1_3_3).
emp(e015, senior_manager, cc1_2).
emp(e016, senior_manager, cc1_2_1).
emp(e017, manager, cc1_2_1_1).
emp(e018, manager, cc1_2_1_2).
emp(e019, manager, cc1_2_1_3).
emp(e020, senior_manager, cc1_2_2).
emp(e021, manager, cc1_2_2_1).
emp(e022, manager, cc1_2_2_2).
emp(e023, manager, cc1_2_2_3).
emp(e024, senior_manager, cc1_2_3).
emp(e025, manager, cc1_2_3_1).
emp(e026, manager, cc1_2_3_2).
emp(e027, manager, cc1_2_3_3).
emp(e028, senior_manager, cc1_3).
emp(e029, senior_manager, cc1_3_1).
emp(e030, manager, cc1_3_1_1).
emp(e031, manager, cc1_3_1_2).
emp(e032, manager, cc1_3_1_3).
emp(e033, senior_manager, cc1_3_2).
emp(e034, manager, cc1_3_2_1).
emp(e035, manager, cc1_3_2_2).
emp(e036, manager, cc1_3_2_3).
emp(e037, senior_manager, cc1_3_3).
emp(e038, manager, cc1_3_3_1).
emp(e039, manager, cc1_3_3_2).
emp(e040, manager, cc1_3_3_3).
emp(e041, director, cc2).
emp(e042, senior_manager, cc2_1).
emp(e043, senior_manager, cc2_1_1).
emp(e044, manager, cc2_1_1_1).
emp(e045, manager, cc2_1_1_2).
emp(e046, manager, cc2_1_1_3).
emp(e047, senior_manager, cc2_1_2).
emp(e048, manager, cc2_1_2_1).
emp(e049, manager, cc2_1_2_2).
emp(e050, manager, cc2_1_2_3).
emp(e051, senior_manager, cc2_1_3).
emp(e052, manager, cc2_1_3_1).
emp(e053, manager, cc2_1_3_2).
emp(e054, manager, cc2_1_3_3).
emp(e055, senior_manager, cc2_2).
emp(e056, senior_manager, cc2_2_1).
emp(e057, manager, cc2_2_1_1).
emp(e058, manager, cc2_2_1_2).
emp(e059, manager, cc2_2_1_3).
emp(e060, senior_manager, cc2_2_2).
emp(e061, manager, cc2_2_2_1).
emp(e062, manager, cc2_2_2_2).
emp(e063, manager, cc2_2_2_3).
emp(e064, senior_manager, cc2_2_3).
emp(e065, manager, cc2_2_3_1).
emp(e066, manager, cc2_2_3_2).
emp(e067, manager, cc2_2_3_3).
emp(e068, senior_manager, cc2_3).
emp(e069, senior_manager, cc2_3_1).
emp(e070, manager, cc2_3_1_1).
emp(e071, manager, cc2_3_1_2).
emp(e072, manager, cc2_3_1_3).
emp(e073, senior_manager, cc2_3_2).
emp(e074, manager, cc2_3_2_1).
emp(e075, manager, cc2_3_2_2).
emp(e076, manager, cc2_3_2_3).
emp(e077, senior_manager, cc2_3_3).
emp(e078, manager, cc2_3_3_1).
emp(e079, manager, cc2_3_3_2).
emp(e080, manager, cc2_3_3_3).
emp(e081, director, cc3).
emp(e082, senior_manager, cc3_1).
emp(e083, senior_manager, cc3_1_1).
emp(e084, manager, cc3_1_1_1).
emp(e085, manager, cc3_1_1_2).
emp(e086, manager, cc3_1_1_3).
emp(e087, senior_manager, cc3_1_2).
emp(e088, manager, cc3_1_2_1).
emp(e089, manager, cc3_1_2_2).
emp(e090, manager, cc3_1_2_3).
emp(e091, senior_manager, cc3_1_3).
emp(e092, manager, cc3_1_3_1).
emp(e093, manager, cc3_1_3_2).
emp(e094, manager, cc3_1_3_3).
emp(e095, senior_manager, cc3_2).
emp(e096, senior_manager, cc3_2_1).
emp(e097, manager, cc3_2_1_1).
emp(e098, manager, cc3_2_1_2).
emp(e099, manager, cc3_2_1_3).
emp(e100, senior_manager, cc3_2_2).
emp(e101, manager, cc3_2_2_1).
emp(e102, manager, cc3_2_2_2).
emp(e103, manager, cc3_2_2_3).
emp(e104, senior_manager, cc3_2_3).
emp(e105, manager, cc3_2_3_1).
emp(e106, manager, cc3_2_3_2).
emp(e107, manager, cc3_2_3_3).
emp(e108, senior_manager, cc3_3).
emp(e109, senior_manager, cc3_3_1).
emp(e110, manager, cc3_3_1_1).
emp(e111, manager, cc3_3_1_2).
emp(e112, manager, cc3_3_1_3).
emp(e113, senior_manager, cc3_3_2).
emp(e114, manager, cc3_3_2_1).
emp(e115, manager, cc3_3_2_2).
emp(e116, manager, cc3_3_2_3).
emp(e117, senior_manager, cc3_3_3).
emp(e118, manager, cc3_3_3_1).
emp(e119, manager, cc3_3_3_2).
emp(e120, manager, cc3_3_3_3).
emp(e121, analyst, cc1_1_1_1).
emp(e122, analyst, cc1_1_1_1).
emp(e123, analyst, cc1_1_1_2).
emp(e124, analyst, cc1_1_1_2).
emp(e125, analyst, cc1_1_1_3).
emp(e126, analyst, cc3_3_3_3).
emp(e127, analyst, cc1_1_2_1).
emp(e128, analyst, cc1_1_2_1).
emp(e129, analyst, cc1_1_2_2).
emp(e130, analyst, cc1_1_2_2).
emp(e131, analyst, cc1_1_2_3).
emp(e132, analyst, cc1_1_2_3).
emp(e133, analyst, cc1_1_3_1).
emp(e134, analyst, cc1_1_3_1).
emp(e135, analyst, cc1_1_3_2).
emp(e136, analyst, cc1_1_3_2).
emp(e137, analyst, cc1_1_3_3).
emp(e138, analyst, cc1_1_3_3).
emp(e139, analyst, cc1_2_1_1).
emp(e140, analyst, cc1_2_1_1).
emp(e141, analyst, cc1_2_1_2).
emp(e142, analyst, cc1_2_1_2).
emp(e143, analyst, cc1_2_1_3).
emp(e144, analyst, cc1_2_1_3).
emp(e145, analyst, cc1_2_2_1).
emp(e146, analyst, cc1_2_2_1).
emp(e147, analyst, cc1_2_2_2).
emp(e148, analyst, cc1_2_2_2).
emp(e149, analyst, cc1_2_2_3).
emp(e150, analyst, cc1_2_2_3).
emp(e151, analyst, cc1_2_3_1).
emp(e152, analyst, cc1_2_3_1).
emp(e153, analyst, cc1_2_3_2).
emp(e154, analyst, cc1_2_3_2).
emp(e155, analyst, cc1_2_3_3).
emp(e156, analyst, cc1_2_3_3).
emp(e157, analyst, cc1_3_1_1).
emp(e158, analyst, cc1_3_1_1).
emp(e159, analyst, cc1_3_1_2).
emp(e160, analyst, cc1_3_1_2).
emp(e161, analyst, cc1_3_1_3).
emp(e162, analyst, cc1_3_1_3).
emp(e163, analyst, cc1_3_2_1).
emp(e164, analyst, cc1_3_2_1).
emp(e165, analyst, cc1_3_2_2).
emp(e166, analyst, cc1_3_2_2).
emp(e167, analyst, cc1_3_2_3).
emp(e168, analyst, cc1_3_2_3).
emp(e169, analyst, cc1_3_3_1).
emp(e170, analyst, cc1_3_3_1).
emp(e171, analyst, cc1_3_3_2).
emp(e172, analyst, cc1_3_3_2).
emp(e173, analyst, cc3_2_1_2).
emp(e174, analyst, cc1_3_3_3).
emp(e175, analyst, cc2_1_1_1).
emp(e176, analyst, cc2_1_1_1).
emp(e177, analyst, cc2_1_1_2).
emp(e178, analyst, cc2_1_1_2).
emp(e179, analyst, cc2_1_1_3).
emp(e180, analyst, cc2_1_1_3).
emp(e181, analyst, cc2_1_2_1).
emp(e182, analyst, cc2_1_2_1).
emp(e183, analyst, cc2_1_2_2).
emp(e184, analyst, cc2_1_2_2).
emp(e185, analyst, cc2_1_2_3).
emp(e186, analyst, cc2_1_2_3).
emp(e187, analyst, cc2_1_3_1).
emp(e188, analyst, cc2_1_3_1).
emp(e189, analyst, cc2_1_3_2).
emp(e190, analyst, cc2_1_3_2).
emp(e191, analyst, cc2_1_3_3).
emp(e192, analyst, cc2_1_3_3).
emp(e193, analyst, cc3_2_3_2).
emp(e194, analyst, cc2_2_1_1).
emp(e195, analyst, cc2_2_1_2).
emp(e196, analyst, cc2_2_1_2).
emp(e197, analyst, cc2_2_1_3).
emp(e198, analyst, cc1_3_2_2).
emp(e199, analyst, cc2_2_2_1).
emp(e200, analyst, cc2_2_2_1).
emp(e201, analyst, cc2_2_2_2).
emp(e202, analyst, cc2_2_2_2).
emp(e203, analyst, cc2_2_2_3).
emp(e204, analyst, cc2_2_2_3).
emp(e205, analyst, cc2_2_3_1).
emp(e206, analyst, cc2_2_3_1).
emp(e207, analyst, cc2_2_3_2).
emp(e208, analyst, cc2_2_3_2).
emp(e209, analyst, cc2_2_3_3).
emp(e210, analyst, cc2_2_3_3).
emp(e211, analyst, cc2_3_1_1).
emp(e212, analyst, cc2_3_1_1).
emp(e213, analyst, cc2_1_3_1).
emp(e214, analyst, cc2_3_1_2).
emp(e215, analyst, cc2_3_1_3).
emp(e216, analyst, cc2_3_1_3).
emp(e217, analyst, cc2_3_2_1).
emp(e218, analyst, cc2_3_2_1).
emp(e219, analyst, cc2_3_2_2).
emp(e220, analyst, cc2_3_2_2).
emp(e221, analyst, cc2_3_2_3).
emp(e222, analyst, cc2_3_2_3).
emp(e223, analyst, cc2_3_3_1).
emp(e224, analyst, cc2_3_3_1).
emp(e225, analyst, cc2_3_3_2).
emp(e226, analyst, cc2_3_3_2).
emp(e227, analyst, cc2_3_3_3).
emp(e228, analyst, cc2_3_3_3).
emp(e229, analyst, cc2_3_2_3).
emp(e230, analyst, cc3_1_1_1).
emp(e231, analyst, cc3_1_1_2).
emp(e232, analyst, cc3_1_1_2).
emp(e233, analyst, cc3_1_1_3).
emp(e234, analyst, cc3_1_1_3).
emp(e235, analyst, cc3_1_2_1).
emp(e236, analyst, cc3_1_2_1).
emp(e237, analyst, cc3_1_2_2).
emp(e238, analyst, cc3_1_2_2).
emp(e239, analyst, cc3_1_2_3).
emp(e240, analyst, cc3_1_2_3).
emp(e241, analyst, cc3_1_3_1).
emp(e242, analyst, cc3_1_3_1).
emp(e243, analyst, cc3_1_3_2).
emp(e244, analyst, cc3_1_3_2).
emp(e245, analyst, cc3_1_3_3).
emp(e246, analyst, cc3_1_3_3).
emp(e247, analyst, cc3_2_1_1).
emp(e248, analyst, cc3_2_1_1).
emp(e249, analyst, cc3_2_1_2).
emp(e250, analyst, cc3_2_1_2).
emp(e251, analyst, cc3_2_1_3).
emp(e252, analyst, cc3_2_1_3).
emp(e253, analyst, cc3_2_2_1).
emp(e254, analyst, cc3_2_2_1).
emp(e255, analyst, cc3_2_2_2).
emp(e256, analyst, cc3_2_2_2).
emp(e257, analyst, cc3_2_2_3).
emp(e258, analyst, cc3_2_2_3).
emp(e259, analyst, cc3_2_3_1).
emp(e260, analyst, cc3_2_3_1).
emp(e261, analyst, cc3_2_3_2).
emp(e262, analyst, cc3_2_3_2).
emp(e263, analyst, cc3_2_3_3).
emp(e264, analyst, cc3_2_3_3).
emp(e265, analyst, cc3_2_2_3).
emp(e266, analyst, cc3_3_1_1).
emp(e267, analyst, cc3_3_1_2).
emp(e268, analyst, cc3_3_1_2).
emp(e269, analyst, cc3_3_1_3).
emp(e270, analyst, cc3_3_1_3).
emp(e271, analyst, cc3_3_2_1).
emp(e272, analyst, cc3_3_2_1).
emp(e273, analyst, cc3_3_2_2).
emp(e274, analyst, cc3_3_2_2).
emp(e275, analyst, cc3_3_2_3).
emp(e276, analyst, cc3_3_2_3).
emp(e277, analyst, cc3_3_3_1).
emp(e278, analyst, cc3_3_3_1).
emp(e279, analyst, cc3_3_3_2).
emp(e280, analyst, cc3_3_3_2).
emp(e281, analyst, cc3_3_3_3).
emp(e282, analyst, cc3_3_3_3).

% reports(Emp, Manager): An employee's direct manager.
:- dynamic reports/2.
reports(e001, e000).
reports(e002, e001).
reports(e003, e002).
reports(e004, e003).
reports(e005, e003).
reports(e006, e003).
reports(e007, e002).
reports(e008, e007).
reports(e009, e007).
reports(e010, e007).
reports(e011, e002).
reports(e012, e011).
reports(e013, e011).
reports(e014, e011).
reports(e015, e001).
reports(e016, e015).
reports(e017, e016).
reports(e018, e016).
reports(e019, e016).
reports(e020, e015).
reports(e021, e020).
reports(e022, e020).
reports(e023, e020).
reports(e024, e015).
reports(e025, e024).
reports(e026, e024).
reports(e027, e024).
reports(e028, e001).
reports(e029, e028).
reports(e030, e029).
reports(e031, e029).
reports(e032, e029).
reports(e033, e028).
reports(e034, e033).
reports(e035, e033).
reports(e036, e033).
reports(e037, e028).
reports(e038, e037).
reports(e039, e037).
reports(e040, e037).
reports(e041, e000).
reports(e042, e041).
reports(e043, e042).
reports(e044, e043).
reports(e045, e043).
reports(e046, e043).
reports(e047, e042).
reports(e048, e047).
reports(e049, e047).
reports(e050, e047).
reports(e051, e042).
reports(e052, e051).
reports(e053, e051).
reports(e054, e051).
reports(e055, e041).
reports(e056, e055).
reports(e057, e056).
reports(e058, e056).
reports(e059, e056).
reports(e060, e055).
reports(e061, e060).
reports(e062, e060).
reports(e063, e060).
reports(e064, e055).
reports(e065, e064).
reports(e066, e064).
reports(e067, e064).
reports(e068, e041).
reports(e069, e068).
reports(e070, e069).
reports(e071, e069).
reports(e072, e069).
reports(e073, e068).
reports(e074, e073).
reports(e075, e073).
reports(e076, e073).
reports(e077, e068).
reports(e078, e077).
reports(e079, e077).
reports(e080, e077).
reports(e081, e000).
reports(e082, e081).
reports(e083, e082).
reports(e084, e083).
reports(e085, e083).
reports(e086, e083).
reports(e087, e082).
reports(e088, e087).
reports(e089, e087).
reports(e090, e087).
reports(e091, e082).
reports(e092, e091).
reports(e093, e091).
reports(e094, e091).
reports(e095, e081).
reports(e096, e095).
reports(e097, e096).
reports(e098, e096).
reports(e099, e096).
reports(e100, e095).
reports(e101, e100).
reports(e102, e100).
reports(e103, e100).
reports(e104, e095).
reports(e105, e104).
reports(e106, e104).
reports(e107, e104).
reports(e108, e081).
reports(e109, e108).
reports(e110, e109).
reports(e111, e109).
reports(e112, e109).
reports(e113, e108).
reports(e114, e113).
reports(e115, e113).
reports(e116, e113).
reports(e117, e108).
reports(e118, e117).
reports(e119, e117).
reports(e120, e117).
reports(e121, e004).
reports(e122, e004).
reports(e123, e005).
reports(e124, e005).
reports(e125, e006).
reports(e126, e120).
reports(e127, e008).
reports(e128, e008).
reports(e129, e009).
reports(e130, e009).
reports(e131, e010).
reports(e132, e010).
reports(e133, e012).
reports(e134, e012).
reports(e135, e013).
reports(e136, e013).
reports(e137, e014).
reports(e138, e014).
reports(e139, e017).
reports(e140, e017).
reports(e141, e018).
reports(e142, e018).
reports(e143, e019).
reports(e144, e019).
reports(e145, e021).
reports(e146, e021).
reports(e147, e022).
reports(e148, e022).
reports(e149, e023).
reports(e150, e023).
reports(e151, e025).
reports(e152, e025).
reports(e153, e026).
reports(e154, e026).
reports(e155, e027).
reports(e156, e027).
reports(e157, e030).
reports(e158, e030).
reports(e159, e031).
reports(e160, e031).
reports(e161, e032).
reports(e162, e032).
reports(e163, e034).
reports(e164, e034).
reports(e165, e035).
reports(e166, e035).
reports(e167, e036).
reports(e168, e036).
reports(e169, e038).
reports(e170, e038).
reports(e171, e039).
reports(e172, e039).
reports(e173, e098).
reports(e174, e040).
reports(e175, e044).
reports(e176, e044).
reports(e177, e045).
reports(e178, e045).
reports(e179, e046).
reports(e180, e046).
reports(e181, e048).
reports(e182, e048).
reports(e183, e049).
reports(e184, e049).
reports(e185, e050).
reports(e186, e050).
reports(e187, e052).
reports(e188, e052).
reports(e189, e053).
reports(e190, e053).
reports(e191, e054).
reports(e192, e054).
reports(e193, e106).
reports(e194, e057).
reports(e195, e058).
reports(e196, e058).
reports(e197, e059).
reports(e198, e035).
reports(e199, e061).
reports(e200, e061).
reports(e201, e062).
reports(e202, e062).
reports(e203, e063).
reports(e204, e063).
reports(e205, e065).
reports(e206, e065).
reports(e207, e066).
reports(e208, e066).
reports(e209, e067).
reports(e210, e067).
reports(e211, e070).
reports(e212, e070).
reports(e213, e052).
reports(e214, e071).
reports(e215, e072).
reports(e216, e072).
reports(e217, e074).
reports(e218, e074).
reports(e219, e075).
reports(e220, e075).
reports(e221, e076).
reports(e222, e076).
reports(e223, e078).
reports(e224, e078).
reports(e225, e079).
reports(e226, e079).
reports(e227, e080).
reports(e228, e080).
reports(e229, e076).
reports(e230, e084).
reports(e231, e085).
reports(e232, e085).
reports(e233, e086).
reports(e234, e086).
reports(e235, e088).
reports(e236, e088).
reports(e237, e089).
reports(e238, e089).
reports(e239, e090).
reports(e240, e090).
reports(e241, e092).
reports(e242, e092).
reports(e243, e093).
reports(e244, e093).
reports(e245, e094).
reports(e246, e094).
reports(e247, e097).
reports(e248, e097).
reports(e249, e098).
reports(e250, e098).
reports(e251, e099).
reports(e252, e099).
reports(e253, e101).
reports(e254, e101).
reports(e255, e102).
reports(e256, e102).
reports(e257, e103).
reports(e258, e103).
reports(e259, e105).
reports(e260, e105).
reports(e261, e106).
reports(e262, e106).
reports(e263, e107).
reports(e264, e107).
reports(e265, e103).
reports(e266, e110).
reports(e267, e111).
reports(e268, e111).
reports(e269, e112).
reports(e270, e112).
reports(e271, e114).
reports(e272, e114).
reports(e273, e115).
reports(e274, e115).
reports(e275, e116).
reports(e276, e116).
reports(e277, e118).
reports(e278, e118).
reports(e279, e119).
reports(e280, e119).
reports(e281, e120).
reports(e282, e120).

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
req(r001, e090, 8000, services, acme, 20260603, pending).
req(r002, e105, 20000, software, cog, 20260802, pending).
req(r003, e028, 20000, software, dyne, 20260910, pending).
req(r004, e253, 12000, capital, cog, 20260914, pending).
req(r005, e035, 90000, hardware, dyne, 20260905, pending).
req(r006, e118, 45000, hardware, bolt, 20260605, pending).
req(r007, e038, 90000, software, edge, 20260609, pending).
req(r008, e040, 20000, capital, cog, 20260913, cancelled).
req(r009, e145, 12000, capital, bolt, 20260712, pending).
req(r010, e264, 60000, hardware, cog, 20260908, pending).
req(r011, e136, 120000, services, bolt, 20260825, pending).
req(r012, e179, 12000, hardware, dyne, 20260915, pending).
req(r013, e214, 3000, capital, edge, 20260820, pending).
req(r014, e233, 12000, services, cog, 20260628, pending).
req(r015, e019, 30000, capital, dyne, 20260913, pending).
req(r016, e204, 90000, software, cog, 20260707, pending).
req(r017, e143, 45000, services, acme, 20260728, pending).
req(r018, e054, 8000, software, acme, 20260614, pending).
req(r019, e216, 30000, services, fern, 20260731, pending).
req(r020, e250, 90000, hardware, bolt, 20260617, pending).
req(r021, e264, 38000, software, bolt, 20260727, pending).
req(r022, e068, 38000, capital, dyne, 20260906, pending).
req(r023, e026, 38000, capital, dyne, 20260810, pending).
req(r024, e147, 38000, software, bolt, 20260901, pending).
req(r025, e125, 38000, hardware, fern, 20260903, pending).
req(r026, e254, 12000, hardware, fern, 20260618, pending).
req(r027, e169, 3000, software, fern, 20260723, pending).
req(r028, e117, 20000, software, bolt, 20260711, pending).
req(r029, e201, 12000, services, edge, 20260721, pending).
req(r030, e080, 45000, capital, edge, 20260812, pending).
req(r031, e192, 38000, services, edge, 20260720, pending).
req(r032, e097, 12000, software, edge, 20260815, pending).
req(r033, e249, 30000, hardware, acme, 20260830, pending).
req(r034, e160, 45000, hardware, acme, 20260609, pending).
req(r035, e051, 30000, services, fern, 20260802, pending).
req(r036, e091, 8000, services, fern, 20260817, pending).
req(r037, e279, 8000, services, fern, 20260720, pending).
req(r038, e096, 20000, hardware, dyne, 20260825, pending).
req(r039, e055, 12000, hardware, cog, 20260914, pending).
req(r040, e044, 20000, software, cog, 20260626, pending).
req(r041, e081, 90000, capital, bolt, 20260817, pending).
req(r042, e176, 12000, capital, fern, 20260712, pending).
req(r043, e107, 20000, services, fern, 20260831, pending).
req(r044, e203, 120000, capital, acme, 20260822, pending).
req(r045, e183, 20000, hardware, cog, 20260624, pending).
req(r046, e264, 30000, capital, cog, 20260622, pending).
req(r047, e201, 8000, hardware, edge, 20260711, cancelled).
req(r048, e151, 20000, hardware, dyne, 20260609, pending).
req(r049, e269, 3000, hardware, fern, 20260813, pending).
req(r050, e110, 60000, capital, fern, 20260822, pending).
req(r051, e100, 45000, software, cog, 20260627, pending).
req(r052, e211, 20000, hardware, dyne, 20260820, pending).
req(r053, e007, 12000, hardware, acme, 20260722, pending).
req(r054, e203, 60000, software, cog, 20260910, pending).
req(r055, e198, 12000, services, edge, 20260704, pending).
req(r056, e108, 3000, software, cog, 20260723, pending).
req(r057, e097, 30000, services, acme, 20260706, pending).
req(r058, e116, 120000, hardware, acme, 20260601, pending).
req(r059, e168, 8000, software, dyne, 20260719, pending).
req(r060, e076, 8000, services, dyne, 20260828, pending).
req(r061, e282, 60000, services, acme, 20260804, cancelled).
req(r062, e007, 90000, software, dyne, 20260828, pending).
req(r063, e269, 120000, services, edge, 20260713, pending).
req(r064, e118, 38000, services, dyne, 20260619, pending).
req(r065, e234, 120000, services, dyne, 20260617, pending).
req(r066, e032, 120000, software, fern, 20260719, pending).
req(r067, e055, 120000, capital, cog, 20260830, pending).
req(r068, e035, 60000, hardware, cog, 20260722, pending).
req(r069, e117, 60000, services, bolt, 20260709, pending).
req(r070, e087, 120000, hardware, acme, 20260620, pending).
req(r071, e133, 12000, capital, cog, 20260709, cancelled).
req(r072, e033, 38000, services, acme, 20260710, pending).
req(r073, e013, 120000, services, bolt, 20260620, pending).
req(r074, e081, 20000, hardware, edge, 20260628, pending).
req(r075, e254, 60000, hardware, acme, 20260614, pending).
req(r076, e150, 20000, services, cog, 20260830, pending).
req(r077, e230, 8000, capital, dyne, 20260606, pending).
req(r078, e164, 3000, software, cog, 20260720, pending).
req(r079, e040, 8000, software, bolt, 20260825, pending).
req(r080, e070, 3000, hardware, edge, 20260718, pending).
req(r081, e072, 38000, services, acme, 20260810, pending).
req(r082, e128, 3000, hardware, acme, 20260706, pending).
req(r083, e132, 60000, hardware, acme, 20260822, pending).
req(r084, e264, 60000, software, dyne, 20260905, pending).
req(r085, e192, 38000, services, acme, 20260726, pending).
req(r086, e273, 20000, software, cog, 20260728, pending).
req(r087, e003, 12000, services, edge, 20260908, pending).
req(r088, e270, 60000, capital, acme, 20260831, pending).
req(r089, e271, 90000, hardware, edge, 20260626, pending).
req(r090, e115, 120000, software, fern, 20260715, pending).
req(r091, e046, 120000, services, bolt, 20260822, pending).
req(r092, e120, 3000, hardware, fern, 20260810, pending).
req(r093, e182, 90000, software, edge, 20260912, pending).
req(r094, e142, 12000, capital, cog, 20260908, pending).
req(r095, e258, 60000, software, acme, 20260713, pending).
req(r096, e219, 120000, software, edge, 20260914, pending).
req(r097, e120, 38000, software, fern, 20260820, pending).
req(r098, e204, 120000, services, acme, 20260602, pending).
req(r099, e139, 45000, hardware, edge, 20260816, pending).
req(r100, e244, 20000, software, edge, 20260622, pending).
req(r101, e047, 20000, hardware, edge, 20260805, pending).
req(r102, e198, 38000, software, cog, 20260723, pending).
req(r103, e016, 12000, capital, dyne, 20260804, pending).
req(r104, e154, 3000, software, acme, 20260606, pending).
req(r105, e221, 20000, software, dyne, 20260624, pending).
req(r106, e105, 30000, capital, edge, 20260601, pending).
req(r107, e032, 60000, capital, acme, 20260804, pending).
req(r108, e279, 38000, hardware, edge, 20260821, cancelled).
req(r109, e230, 38000, hardware, dyne, 20260802, pending).
req(r110, e259, 38000, software, edge, 20260804, pending).
req(r111, e091, 12000, services, cog, 20260727, pending).
req(r112, e003, 60000, hardware, bolt, 20260606, pending).
req(r113, e174, 90000, software, edge, 20260607, pending).
req(r114, e263, 90000, services, edge, 20260801, pending).
req(r115, e161, 90000, software, acme, 20260809, pending).
req(r116, e240, 38000, capital, edge, 20260613, pending).
req(r117, e240, 45000, services, edge, 20260619, pending).
req(r118, e029, 38000, software, dyne, 20260810, pending).
req(r119, e270, 120000, hardware, acme, 20260830, pending).
req(r120, e278, 38000, services, acme, 20260614, pending).
req(r121, e113, 3000, software, bolt, 20260625, pending).
req(r122, e209, 12000, software, fern, 20260620, pending).
req(r123, e127, 20000, hardware, edge, 20260607, pending).
req(r124, e184, 90000, hardware, edge, 20260718, pending).
req(r125, e173, 30000, software, fern, 20260713, pending).
req(r126, e222, 60000, capital, bolt, 20260807, pending).
req(r127, e040, 38000, services, acme, 20260710, pending).
req(r128, e071, 12000, capital, bolt, 20260730, pending).
req(r129, e111, 8000, capital, bolt, 20260902, pending).
req(r130, e222, 90000, hardware, acme, 20260706, cancelled).
req(r131, e097, 12000, software, acme, 20260826, pending).
req(r132, e052, 30000, capital, dyne, 20260901, pending).
req(r133, e267, 90000, services, fern, 20260616, pending).
req(r134, e084, 3000, services, dyne, 20260913, pending).
req(r135, e199, 12000, hardware, bolt, 20260809, pending).
req(r136, e118, 20000, hardware, cog, 20260907, pending).
req(r137, e075, 90000, capital, fern, 20260618, pending).
req(r138, e038, 20000, services, bolt, 20260609, pending).
req(r139, e061, 90000, software, dyne, 20260623, pending).
req(r140, e191, 90000, capital, fern, 20260710, pending).
req(r141, e206, 120000, software, cog, 20260705, cancelled).
req(r142, e163, 60000, hardware, fern, 20260827, cancelled).
req(r143, e271, 30000, services, cog, 20260718, pending).
req(r144, e049, 60000, capital, dyne, 20260723, pending).
req(r145, e197, 8000, capital, edge, 20260831, pending).
req(r146, e072, 60000, hardware, edge, 20260712, pending).
req(r147, e144, 60000, software, edge, 20260802, pending).
req(r148, e278, 8000, capital, edge, 20260710, pending).
req(r149, e076, 20000, capital, bolt, 20260707, pending).
req(r150, e100, 45000, services, bolt, 20260710, cancelled).
req(r151, e230, 20000, hardware, bolt, 20260610, pending).
req(r152, e005, 8000, hardware, dyne, 20260614, pending).
req(r153, e122, 90000, capital, bolt, 20260625, pending).
req(r154, e138, 20000, capital, acme, 20260609, pending).
req(r155, e200, 12000, hardware, bolt, 20260908, pending).
req(r156, e044, 20000, capital, cog, 20260705, pending).
req(r157, e188, 60000, hardware, fern, 20260807, pending).
req(r158, e100, 90000, hardware, fern, 20260719, pending).
req(r159, e229, 3000, services, acme, 20260612, pending).
req(r160, e046, 3000, software, acme, 20260615, pending).
req(r161, e222, 20000, hardware, bolt, 20260617, pending).
req(r162, e077, 90000, capital, cog, 20260710, pending).
req(r163, e207, 3000, capital, bolt, 20260705, pending).
req(r164, e127, 38000, hardware, cog, 20260814, pending).
req(r165, e268, 120000, software, edge, 20260623, pending).
req(r166, e086, 20000, capital, cog, 20260907, pending).
req(r167, e135, 45000, hardware, bolt, 20260710, pending).
req(r168, e271, 8000, services, edge, 20260629, pending).
req(r169, e184, 45000, software, bolt, 20260713, pending).
req(r170, e169, 38000, software, fern, 20260824, pending).
req(r171, e273, 45000, capital, edge, 20260727, pending).
req(r172, e259, 45000, hardware, dyne, 20260826, cancelled).
req(r173, e237, 60000, hardware, fern, 20260724, pending).
req(r174, e181, 38000, services, cog, 20260707, pending).
req(r175, e162, 45000, software, acme, 20260708, pending).
req(r176, e260, 3000, services, bolt, 20260901, pending).
req(r177, e169, 20000, hardware, cog, 20260804, pending).
req(r178, e209, 90000, software, edge, 20260914, pending).
req(r179, e084, 20000, services, fern, 20260726, pending).
req(r180, e035, 12000, services, acme, 20260913, pending).
req(r181, e163, 60000, hardware, fern, 20260716, pending).
req(r182, e155, 90000, capital, bolt, 20260604, pending).
req(r183, e026, 60000, hardware, edge, 20260915, pending).
req(r184, e094, 30000, software, dyne, 20260904, pending).
req(r185, e127, 45000, software, dyne, 20260903, pending).
req(r186, e196, 3000, hardware, acme, 20260907, pending).
req(r187, e271, 45000, services, bolt, 20260831, pending).
req(r188, e147, 45000, services, fern, 20260610, cancelled).
req(r189, e132, 90000, hardware, dyne, 20260709, pending).
req(r190, e248, 90000, capital, edge, 20260804, pending).
req(r191, e014, 38000, software, cog, 20260625, pending).
req(r192, e119, 90000, capital, fern, 20260606, pending).
req(r193, e084, 3000, capital, dyne, 20260627, pending).
req(r194, e263, 12000, hardware, cog, 20260814, pending).
req(r195, e072, 120000, hardware, bolt, 20260723, pending).
req(r196, e250, 45000, software, edge, 20260827, pending).
req(r197, e250, 30000, capital, fern, 20260719, pending).
req(r198, e209, 60000, capital, dyne, 20260818, pending).
req(r199, e085, 8000, software, edge, 20260815, pending).
req(r200, e239, 90000, hardware, dyne, 20260805, pending).
req(r201, e223, 38000, hardware, dyne, 20260820, pending).
req(r202, e044, 30000, software, dyne, 20260621, pending).
req(r203, e109, 3000, software, dyne, 20260610, pending).
req(r204, e248, 90000, software, bolt, 20260811, pending).
req(r205, e075, 12000, capital, bolt, 20260622, pending).
req(r206, e252, 38000, capital, dyne, 20260804, pending).
req(r207, e109, 60000, services, acme, 20260828, pending).
req(r208, e126, 20000, capital, fern, 20260618, pending).
req(r209, e028, 90000, software, edge, 20260812, pending).
req(r210, e229, 45000, software, dyne, 20260618, pending).
req(r211, e148, 3000, services, fern, 20260704, pending).
req(r212, e273, 45000, services, cog, 20260805, pending).
req(r213, e009, 12000, services, edge, 20260818, pending).
req(r214, e001, 45000, capital, edge, 20260616, pending).
req(r215, e276, 60000, capital, cog, 20260712, pending).
req(r216, e019, 12000, hardware, acme, 20260822, pending).
req(r217, e271, 8000, capital, dyne, 20260722, pending).
req(r218, e057, 30000, software, acme, 20260828, pending).
req(r219, e273, 8000, services, bolt, 20260911, pending).
req(r220, e190, 60000, software, edge, 20260605, pending).
req(r221, e187, 90000, capital, fern, 20260614, pending).
req(r222, e217, 60000, services, acme, 20260718, pending).
req(r223, e255, 30000, services, edge, 20260807, pending).
req(r224, e137, 3000, services, bolt, 20260811, pending).
req(r225, e281, 90000, software, dyne, 20260627, pending).
req(r226, e223, 3000, services, edge, 20260809, pending).
req(r227, e006, 8000, capital, cog, 20260714, pending).
req(r228, e166, 12000, capital, bolt, 20260610, cancelled).
req(r229, e168, 12000, hardware, fern, 20260611, pending).
req(r230, e069, 3000, services, fern, 20260603, pending).
req(r231, e117, 3000, software, dyne, 20260707, pending).
req(r232, e186, 60000, hardware, dyne, 20260909, cancelled).

% emergency(Req): A request flagged as an emergency.
:- dynamic emergency/1.
emergency(r002).
emergency(r007).
emergency(r016).
emergency(r024).
emergency(r025).
emergency(r026).
emergency(r034).
emergency(r048).
emergency(r051).
emergency(r054).
emergency(r058).
emergency(r065).
emergency(r078).
emergency(r093).
emergency(r096).
emergency(r100).
emergency(r110).
emergency(r112).
emergency(r126).
emergency(r130).
emergency(r132).
emergency(r142).
emergency(r148).
emergency(r151).
emergency(r152).
emergency(r155).
emergency(r157).
emergency(r167).
emergency(r168).
emergency(r176).
emergency(r182).
emergency(r183).
emergency(r184).
emergency(r185).
emergency(r188).
emergency(r201).
emergency(r204).
emergency(r208).
emergency(r209).
emergency(r212).
emergency(r216).
emergency(r219).
emergency(r221).
emergency(r227).
emergency(r230).
emergency(r231).

% violation(Emp): An employee with a recorded policy violation.
:- dynamic violation/1.
violation(e015).
violation(e033).
violation(e035).
violation(e042).
violation(e054).
violation(e065).
violation(e070).
violation(e073).
violation(e078).
violation(e109).
violation(e118).
violation(e157).
violation(e169).
violation(e177).
violation(e180).
violation(e187).
violation(e188).
violation(e191).
violation(e201).
violation(e212).
violation(e218).
violation(e220).
violation(e225).
violation(e227).
violation(e250).
violation(e253).
violation(e279).
violation(e280).

% booked(Cc, Amount): Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
:- dynamic booked/2.
booked(cc1_1_1_1, 78000).
booked(cc1_1_1_2, 72000).
booked(cc1_1_1_3, 114000).
booked(cc1_1_2_1, 121000).
booked(cc1_1_2_2, 63000).
booked(cc1_1_2_3, 80000).
booked(cc1_1_3_1, 132000).
booked(cc1_1_3_2, 95000).
booked(cc1_1_3_3, 77000).
booked(cc1_2_1_1, 66000).
booked(cc1_2_1_2, 57000).
booked(cc1_2_1_3, 83000).
booked(cc1_2_2_1, 50000).
booked(cc1_2_2_2, 84000).
booked(cc1_2_2_3, 92000).
booked(cc1_2_3_1, 54000).
booked(cc1_2_3_2, 114000).
booked(cc1_2_3_3, 47000).
booked(cc1_3_1_1, 42000).
booked(cc1_3_1_2, 54000).
booked(cc1_3_1_3, 62000).
booked(cc1_3_2_1, 98000).
booked(cc1_3_2_2, 47000).
booked(cc1_3_2_3, 54000).
booked(cc1_3_3_1, 41000).
booked(cc1_3_3_2, 136000).
booked(cc1_3_3_3, 102000).
booked(cc2_1_1_1, 128000).
booked(cc2_1_1_2, 124000).
booked(cc2_1_1_3, 94000).
booked(cc2_1_2_1, 109000).
booked(cc2_1_2_2, 106000).
booked(cc2_1_2_3, 46000).
booked(cc2_1_3_1, 129000).
booked(cc2_1_3_2, 70000).
booked(cc2_1_3_3, 124000).
booked(cc2_2_1_1, 110000).
booked(cc2_2_1_2, 63000).
booked(cc2_2_1_3, 88000).
booked(cc2_2_2_1, 42000).
booked(cc2_2_2_2, 40000).
booked(cc2_2_2_3, 78000).
booked(cc2_2_3_1, 40000).
booked(cc2_2_3_2, 62000).
booked(cc2_2_3_3, 49000).
booked(cc2_3_1_1, 75000).
booked(cc2_3_1_2, 76000).
booked(cc2_3_1_3, 66000).
booked(cc2_3_2_1, 64000).
booked(cc2_3_2_2, 51000).
booked(cc2_3_2_3, 90000).
booked(cc2_3_3_1, 106000).
booked(cc2_3_3_2, 126000).
booked(cc2_3_3_3, 75000).
booked(cc3_1_1_1, 66000).
booked(cc3_1_1_2, 93000).
booked(cc3_1_1_3, 58000).
booked(cc3_1_2_1, 67000).
booked(cc3_1_2_2, 46000).
booked(cc3_1_2_3, 126000).
booked(cc3_1_3_1, 81000).
booked(cc3_1_3_2, 65000).
booked(cc3_1_3_3, 77000).
booked(cc3_2_1_1, 105000).
booked(cc3_2_1_2, 105000).
booked(cc3_2_1_3, 63000).
booked(cc3_2_2_1, 134000).
booked(cc3_2_2_2, 118000).
booked(cc3_2_2_3, 44000).
booked(cc3_2_3_1, 120000).
booked(cc3_2_3_2, 71000).
booked(cc3_2_3_3, 109000).
booked(cc3_3_1_1, 111000).
booked(cc3_3_1_2, 70000).
booked(cc3_3_1_3, 101000).
booked(cc3_3_2_1, 41000).
booked(cc3_3_2_2, 139000).
booked(cc3_3_2_3, 113000).
booked(cc3_3_3_1, 60000).
booked(cc3_3_3_2, 83000).
booked(cc3_3_3_3, 110000).
booked(cc2, 10000).
booked(cc2_1_2, 35000).
booked(cc2_3_2, 16000).
booked(cc3_2, 36000).
booked(cc3_3, 31000).
booked(cc3_3_1, 17000).

% cap(Cc, Amount): The spending cap of a cost centre this quarter.
:- dynamic cap/2.
cap(company, 8240000).
cap(cc1, 2220000).
cap(cc1_1, 1081000).
cap(cc1_1_1, 277000).
cap(cc1_1_1_1, 75000).
cap(cc1_1_1_2, 115000).
cap(cc1_1_1_3, 136000).
cap(cc1_1_2, 343000).
cap(cc1_1_2_1, 133000).
cap(cc1_1_2_2, 61000).
cap(cc1_1_2_3, 112000).
cap(cc1_1_3, 319000).
cap(cc1_1_3_1, 211000).
cap(cc1_1_3_2, 97000).
cap(cc1_1_3_3, 92000).
cap(cc1_2, 679000).
cap(cc1_2_1, 267000).
cap(cc1_2_1_1, 64000).
cap(cc1_2_1_2, 55000).
cap(cc1_2_1_3, 80000).
cap(cc1_2_2, 259000).
cap(cc1_2_2_1, 80000).
cap(cc1_2_2_2, 134000).
cap(cc1_2_2_3, 128000).
cap(cc1_2_3, 247000).
cap(cc1_2_3_1, 52000).
cap(cc1_2_3_2, 125000).
cap(cc1_2_3_3, 45000).
cap(cc1_3, 731000).
cap(cc1_3_1, 205000).
cap(cc1_3_1_1, 40000).
cap(cc1_3_1_2, 64000).
cap(cc1_3_1_3, 68000).
cap(cc1_3_2, 208000).
cap(cc1_3_2_1, 137000).
cap(cc1_3_2_2, 75000).
cap(cc1_3_2_3, 52000).
cap(cc1_3_3, 418000).
cap(cc1_3_3_1, 39000).
cap(cc1_3_3_2, 217000).
cap(cc1_3_3_3, 163000).
cap(cc2, 3438000).
cap(cc2_1, 1447000).
cap(cc2_1_1, 449000).
cap(cc2_1_1_1, 179000).
cap(cc2_1_1_2, 148000).
cap(cc2_1_1_3, 91000).
cap(cc2_1_2, 444000).
cap(cc2_1_2_1, 105000).
cap(cc2_1_2_2, 148000).
cap(cc2_1_2_3, 64000).
cap(cc2_1_3, 419000).
cap(cc2_1_3_1, 141000).
cap(cc2_1_3_2, 67000).
cap(cc2_1_3_3, 173000).
cap(cc2_2, 600000).
cap(cc2_2_1, 391000).
cap(cc2_2_1_1, 106000).
cap(cc2_2_1_2, 88000).
cap(cc2_2_1_3, 123000).
cap(cc2_2_2, 184000).
cap(cc2_2_2_1, 50000).
cap(cc2_2_2_2, 44000).
cap(cc2_2_2_3, 75000).
cap(cc2_2_3, 158000).
cap(cc2_2_3_1, 56000).
cap(cc2_2_3_2, 99000).
cap(cc2_2_3_3, 47000).
cap(cc2_3, 782000).
cap(cc2_3_1, 249000).
cap(cc2_3_1_1, 72000).
cap(cc2_3_1_2, 73000).
cap(cc2_3_1_3, 92000).
cap(cc2_3_2, 254000).
cap(cc2_3_2_1, 89000).
cap(cc2_3_2_2, 71000).
cap(cc2_3_2_3, 92000).
cap(cc2_3_3, 399000).
cap(cc2_3_3_1, 102000).
cap(cc2_3_3_2, 151000).
cap(cc2_3_3_3, 90000).
cap(cc3, 3198000).
cap(cc3_1, 712000).
cap(cc3_1_1, 282000).
cap(cc3_1_1_1, 64000).
cap(cc3_1_1_2, 90000).
cap(cc3_1_1_3, 92000).
cap(cc3_1_2, 358000).
cap(cc3_1_2_1, 107000).
cap(cc3_1_2_2, 47000).
cap(cc3_1_2_3, 201000).
cap(cc3_1_3, 234000).
cap(cc3_1_3_1, 97000).
cap(cc3_1_3_2, 104000).
cap(cc3_1_3_3, 84000).
cap(cc3_2, 1357000).
cap(cc3_2_1, 354000).
cap(cc3_2_1_1, 101000).
cap(cc3_2_1_2, 108000).
cap(cc3_2_1_3, 88000).
cap(cc3_2_2, 340000).
cap(cc3_2_2_1, 129000).
cap(cc3_2_2_2, 129000).
cap(cc3_2_2_3, 48000).
cap(cc3_2_3, 450000).
cap(cc3_2_3_1, 116000).
cap(cc3_2_3_2, 85000).
cap(cc3_2_3_3, 152000).
cap(cc3_3, 1314000).
cap(cc3_3_1, 388000).
cap(cc3_3_1_1, 114000).
cap(cc3_3_1_2, 72000).
cap(cc3_3_1_3, 111000).
cap(cc3_3_2, 439000).
cap(cc3_3_2_1, 42000).
cap(cc3_3_2_2, 194000).
cap(cc3_3_2_3, 124000).
cap(cc3_3_3, 265000).
cap(cc3_3_3_1, 66000).
cap(cc3_3_3_2, 116000).
cap(cc3_3_3_3, 176000).

% today(Date): The date on which the material was compiled.
:- dynamic today/1.
today(20260915).

% role_limit_version(Role, Limit, Valid_from, Valid_to): A dated version of a role's approval limit, valid from and to the given dates inclusive.
:- dynamic role_limit_version/4.
role_limit_version(analyst, 5000, 20260101, 20261231).
role_limit_version(manager, 25000, 20260101, 20260731).
role_limit_version(manager, 40000, 20260801, 20261231).
role_limit_version(senior_manager, 50000, 20260101, 20261231).
role_limit_version(director, 100000, 20260101, 20261231).
role_limit_version(vp, 500000, 20260101, 20261231).

% vendor_status(Vendor, Status, Valid_from, Valid_to): A vendor's status during a period, from and to the given dates inclusive.
:- dynamic vendor_status/4.
vendor_status(acme, approved, 20260101, 20261231).
vendor_status(bolt, approved, 20260101, 20260731).
vendor_status(bolt, suspended, 20260801, 20261231).
vendor_status(cog, approved, 20260101, 20261231).
vendor_status(dyne, suspended, 20260101, 20260630).
vendor_status(dyne, approved, 20260701, 20261231).
vendor_status(edge, approved, 20260101, 20261231).
vendor_status(fern, suspended, 20260101, 20261231).

% assignment(Emp, Cc, Source, Effective): A source's record (hr or finance) that an employee belongs to a cost centre from the effective date on.
:- dynamic assignment/4.
assignment(e000, company, finance, 20260101).
assignment(e000, company, hr, 20260101).
assignment(e001, cc1, finance, 20260101).
assignment(e001, cc1, hr, 20260101).
assignment(e002, cc1_1, finance, 20260101).
assignment(e002, cc1_1, hr, 20260101).
assignment(e003, cc1_1_1, finance, 20260101).
assignment(e003, cc1_1_1, hr, 20260101).
assignment(e004, cc1_1_1_1, finance, 20260101).
assignment(e004, cc1_1_1_1, hr, 20260101).
assignment(e005, cc1_1_1_2, finance, 20260101).
assignment(e005, cc1_1_1_2, hr, 20260101).
assignment(e006, cc1_1_1_3, finance, 20260101).
assignment(e006, cc1_1_1_3, hr, 20260101).
assignment(e007, cc1_1_2, finance, 20260101).
assignment(e007, cc1_1_2, hr, 20260101).
assignment(e008, cc1_1_2_1, finance, 20260101).
assignment(e008, cc1_1_2_1, hr, 20260101).
assignment(e009, cc1_1_2_2, finance, 20260101).
assignment(e009, cc1_1_2_2, hr, 20260101).
assignment(e010, cc1_1_2_3, finance, 20260101).
assignment(e010, cc1_1_2_3, hr, 20260101).
assignment(e011, cc1_1_3, finance, 20260101).
assignment(e011, cc1_1_3, hr, 20260101).
assignment(e012, cc1_1_3_1, finance, 20260101).
assignment(e012, cc1_1_3_1, hr, 20260101).
assignment(e013, cc1_1_3_2, finance, 20260101).
assignment(e013, cc1_1_3_2, hr, 20260101).
assignment(e014, cc1_1_3_3, finance, 20260101).
assignment(e014, cc1_1_3_3, hr, 20260101).
assignment(e015, cc1_2, finance, 20260101).
assignment(e015, cc1_2, hr, 20260101).
assignment(e016, cc1_2_1, finance, 20260101).
assignment(e016, cc1_2_1, hr, 20260101).
assignment(e017, cc1_2_1_1, finance, 20260101).
assignment(e017, cc1_2_1_1, hr, 20260101).
assignment(e018, cc1_2_1_2, finance, 20260101).
assignment(e018, cc1_2_1_2, hr, 20260101).
assignment(e019, cc1_2_1_3, finance, 20260101).
assignment(e019, cc1_2_1_3, hr, 20260101).
assignment(e020, cc1_2_2, finance, 20260101).
assignment(e020, cc1_2_2, hr, 20260101).
assignment(e021, cc1_2_2_1, finance, 20260101).
assignment(e021, cc1_2_2_1, hr, 20260101).
assignment(e022, cc1_2_2_2, finance, 20260101).
assignment(e022, cc1_2_2_2, hr, 20260101).
assignment(e023, cc1_2_2_3, finance, 20260101).
assignment(e023, cc1_2_2_3, hr, 20260101).
assignment(e024, cc1_2_3, finance, 20260101).
assignment(e024, cc1_2_3, hr, 20260101).
assignment(e025, cc1_2_3_1, finance, 20260101).
assignment(e025, cc1_2_3_1, hr, 20260101).
assignment(e026, cc1_2_3_2, finance, 20260101).
assignment(e026, cc1_2_3_2, hr, 20260101).
assignment(e027, cc1_2_3_3, finance, 20260101).
assignment(e027, cc1_2_3_3, hr, 20260101).
assignment(e028, cc1_3, finance, 20260101).
assignment(e028, cc1_3, hr, 20260101).
assignment(e029, cc1_3_1, finance, 20260101).
assignment(e029, cc1_3_1, hr, 20260101).
assignment(e030, cc1_3_1_1, finance, 20260101).
assignment(e030, cc1_3_1_1, hr, 20260101).
assignment(e031, cc1_3_1_2, finance, 20260101).
assignment(e031, cc1_3_1_2, hr, 20260101).
assignment(e032, cc1_3_1_3, finance, 20260101).
assignment(e032, cc1_3_1_3, hr, 20260101).
assignment(e033, cc1_3_2, finance, 20260101).
assignment(e033, cc1_3_2, hr, 20260101).
assignment(e034, cc1_3_2_1, finance, 20260101).
assignment(e034, cc1_3_2_1, hr, 20260101).
assignment(e035, cc1_3_2_2, finance, 20260101).
assignment(e035, cc1_3_2_2, hr, 20260101).
assignment(e036, cc1_3_2_3, finance, 20260101).
assignment(e036, cc1_3_2_3, hr, 20260101).
assignment(e037, cc1_3_3, finance, 20260101).
assignment(e037, cc1_3_3, hr, 20260101).
assignment(e038, cc1_3_3_1, finance, 20260101).
assignment(e038, cc1_3_3_1, hr, 20260101).
assignment(e039, cc1_3_3_2, finance, 20260101).
assignment(e039, cc1_3_3_2, hr, 20260101).
assignment(e040, cc1_3_3_3, finance, 20260101).
assignment(e040, cc1_3_3_3, hr, 20260101).
assignment(e041, cc2, finance, 20260101).
assignment(e041, cc2, hr, 20260101).
assignment(e042, cc2_1, finance, 20260101).
assignment(e042, cc2_1, hr, 20260101).
assignment(e043, cc2_1_1, finance, 20260101).
assignment(e043, cc2_1_1, hr, 20260101).
assignment(e044, cc2_1_1_1, finance, 20260101).
assignment(e044, cc2_1_1_1, hr, 20260101).
assignment(e045, cc2_1_1_2, finance, 20260101).
assignment(e045, cc2_1_1_2, hr, 20260101).
assignment(e046, cc2_1_1_3, finance, 20260101).
assignment(e046, cc2_1_1_3, hr, 20260101).
assignment(e047, cc2_1_2, finance, 20260101).
assignment(e047, cc2_1_2, hr, 20260101).
assignment(e048, cc2_1_2_1, finance, 20260101).
assignment(e048, cc2_1_2_1, hr, 20260101).
assignment(e049, cc2_1_2_2, finance, 20260101).
assignment(e049, cc2_1_2_2, hr, 20260101).
assignment(e050, cc2_1_2_3, finance, 20260101).
assignment(e050, cc2_1_2_3, hr, 20260101).
assignment(e051, cc2_1_3, finance, 20260101).
assignment(e051, cc2_1_3, hr, 20260101).
assignment(e052, cc2_1_3_1, finance, 20260101).
assignment(e052, cc2_1_3_1, hr, 20260101).
assignment(e053, cc2_1_3_2, finance, 20260101).
assignment(e053, cc2_1_3_2, hr, 20260101).
assignment(e054, cc2_1_3_3, finance, 20260101).
assignment(e054, cc2_1_3_3, hr, 20260101).
assignment(e055, cc2_2, finance, 20260101).
assignment(e055, cc2_2, hr, 20260101).
assignment(e056, cc2_2_1, finance, 20260101).
assignment(e056, cc2_2_1, hr, 20260101).
assignment(e057, cc2_2_1_1, finance, 20260101).
assignment(e057, cc2_2_1_1, hr, 20260101).
assignment(e058, cc2_2_1_2, finance, 20260101).
assignment(e058, cc2_2_1_2, hr, 20260101).
assignment(e059, cc2_2_1_3, finance, 20260101).
assignment(e059, cc2_2_1_3, hr, 20260101).
assignment(e060, cc2_2_2, finance, 20260101).
assignment(e060, cc2_2_2, hr, 20260101).
assignment(e061, cc2_2_2_1, finance, 20260101).
assignment(e061, cc2_2_2_1, hr, 20260101).
assignment(e062, cc2_2_2_2, finance, 20260101).
assignment(e062, cc2_2_2_2, hr, 20260101).
assignment(e063, cc2_2_2_3, finance, 20260101).
assignment(e063, cc2_2_2_3, hr, 20260101).
assignment(e064, cc2_2_3, finance, 20260101).
assignment(e064, cc2_2_3, hr, 20260101).
assignment(e065, cc2_2_3_1, finance, 20260101).
assignment(e065, cc2_2_3_1, hr, 20260101).
assignment(e066, cc2_2_3_2, finance, 20260101).
assignment(e066, cc2_2_3_2, hr, 20260101).
assignment(e067, cc2_2_3_3, finance, 20260101).
assignment(e067, cc2_2_3_3, hr, 20260101).
assignment(e068, cc2_3, finance, 20260101).
assignment(e068, cc2_3, hr, 20260101).
assignment(e069, cc2_3_1, finance, 20260101).
assignment(e069, cc2_3_1, hr, 20260101).
assignment(e070, cc2_3_1_1, finance, 20260101).
assignment(e070, cc2_3_1_1, hr, 20260101).
assignment(e071, cc2_3_1_2, finance, 20260101).
assignment(e071, cc2_3_1_2, hr, 20260101).
assignment(e072, cc2_3_1_3, finance, 20260101).
assignment(e072, cc2_3_1_3, hr, 20260101).
assignment(e073, cc2_3_2, finance, 20260101).
assignment(e073, cc2_3_2, hr, 20260101).
assignment(e074, cc2_3_2_1, finance, 20260101).
assignment(e074, cc2_3_2_1, hr, 20260101).
assignment(e075, cc2_3_2_2, finance, 20260101).
assignment(e075, cc2_3_2_2, hr, 20260101).
assignment(e076, cc2_3_2_3, finance, 20260101).
assignment(e076, cc2_3_2_3, hr, 20260101).
assignment(e077, cc2_3_3, finance, 20260101).
assignment(e077, cc2_3_3, hr, 20260101).
assignment(e078, cc2_3_3_1, finance, 20260101).
assignment(e078, cc2_3_3_1, hr, 20260101).
assignment(e079, cc2_3_3_2, finance, 20260101).
assignment(e079, cc2_3_3_2, hr, 20260101).
assignment(e080, cc2_3_3_3, finance, 20260101).
assignment(e080, cc2_3_3_3, hr, 20260101).
assignment(e081, cc3, finance, 20260101).
assignment(e081, cc3, hr, 20260101).
assignment(e082, cc3_1, finance, 20260101).
assignment(e082, cc3_1, hr, 20260101).
assignment(e083, cc3_1_1, finance, 20260101).
assignment(e083, cc3_1_1, hr, 20260101).
assignment(e084, cc3_1_1_1, finance, 20260101).
assignment(e084, cc3_1_1_1, hr, 20260101).
assignment(e085, cc3_1_1_2, finance, 20260101).
assignment(e085, cc3_1_1_2, hr, 20260101).
assignment(e086, cc3_1_1_3, finance, 20260101).
assignment(e086, cc3_1_1_3, hr, 20260101).
assignment(e087, cc3_1_2, finance, 20260101).
assignment(e087, cc3_1_2, hr, 20260101).
assignment(e088, cc3_1_2_1, finance, 20260101).
assignment(e088, cc3_1_2_1, hr, 20260101).
assignment(e089, cc3_1_2_2, finance, 20260101).
assignment(e089, cc3_1_2_2, hr, 20260101).
assignment(e090, cc3_1_2_3, finance, 20260101).
assignment(e090, cc3_1_2_3, hr, 20260101).
assignment(e091, cc3_1_3, finance, 20260101).
assignment(e091, cc3_1_3, hr, 20260101).
assignment(e092, cc3_1_3_1, finance, 20260101).
assignment(e092, cc3_1_3_1, hr, 20260101).
assignment(e093, cc3_1_3_2, finance, 20260101).
assignment(e093, cc3_1_3_2, hr, 20260101).
assignment(e094, cc3_1_3_3, finance, 20260101).
assignment(e094, cc3_1_3_3, hr, 20260101).
assignment(e095, cc3_2, finance, 20260101).
assignment(e095, cc3_2, hr, 20260101).
assignment(e096, cc3_2_1, finance, 20260101).
assignment(e096, cc3_2_1, hr, 20260101).
assignment(e097, cc3_2_1_1, finance, 20260101).
assignment(e097, cc3_2_1_1, hr, 20260101).
assignment(e098, cc3_2_1_2, finance, 20260101).
assignment(e098, cc3_2_1_2, hr, 20260101).
assignment(e099, cc3_2_1_3, finance, 20260101).
assignment(e099, cc3_2_1_3, hr, 20260101).
assignment(e100, cc3_2_2, finance, 20260101).
assignment(e100, cc3_2_2, hr, 20260101).
assignment(e101, cc3_2_2_1, finance, 20260101).
assignment(e101, cc3_2_2_1, hr, 20260101).
assignment(e102, cc3_2_2_2, finance, 20260101).
assignment(e102, cc3_2_2_2, hr, 20260101).
assignment(e103, cc3_2_2_3, finance, 20260101).
assignment(e103, cc3_2_2_3, hr, 20260101).
assignment(e104, cc3_2_3, finance, 20260101).
assignment(e104, cc3_2_3, hr, 20260101).
assignment(e105, cc3_2_3_1, finance, 20260101).
assignment(e105, cc3_2_3_1, hr, 20260101).
assignment(e106, cc3_2_3_2, finance, 20260101).
assignment(e106, cc3_2_3_2, hr, 20260101).
assignment(e107, cc3_2_3_3, finance, 20260101).
assignment(e107, cc3_2_3_3, hr, 20260101).
assignment(e108, cc3_3, finance, 20260101).
assignment(e108, cc3_3, hr, 20260101).
assignment(e109, cc3_3_1, finance, 20260101).
assignment(e109, cc3_3_1, hr, 20260101).
assignment(e110, cc3_3_1_1, finance, 20260101).
assignment(e110, cc3_3_1_1, hr, 20260101).
assignment(e111, cc3_3_1_2, finance, 20260101).
assignment(e111, cc3_3_1_2, hr, 20260101).
assignment(e112, cc3_3_1_3, finance, 20260101).
assignment(e112, cc3_3_1_3, hr, 20260101).
assignment(e113, cc3_3_2, finance, 20260101).
assignment(e113, cc3_3_2, hr, 20260101).
assignment(e114, cc3_3_2_1, finance, 20260101).
assignment(e114, cc3_3_2_1, hr, 20260101).
assignment(e115, cc3_3_2_2, finance, 20260101).
assignment(e115, cc3_3_2_2, hr, 20260101).
assignment(e116, cc3_3_2_3, finance, 20260101).
assignment(e116, cc3_3_2_3, hr, 20260101).
assignment(e117, cc3_3_3, finance, 20260101).
assignment(e117, cc3_3_3, hr, 20260101).
assignment(e118, cc3_3_3_1, finance, 20260101).
assignment(e118, cc3_3_3_1, hr, 20260101).
assignment(e119, cc3_3_3_2, finance, 20260101).
assignment(e119, cc3_3_3_2, hr, 20260101).
assignment(e120, cc3_3_3_3, finance, 20260101).
assignment(e120, cc3_3_3_3, hr, 20260101).
assignment(e121, cc1_1_1_1, finance, 20260101).
assignment(e121, cc1_1_1_1, hr, 20260101).
assignment(e122, cc1_1_1_1, finance, 20260101).
assignment(e122, cc1_1_1_1, hr, 20260101).
assignment(e123, cc1_1_1_2, finance, 20260101).
assignment(e123, cc1_1_1_2, hr, 20260101).
assignment(e124, cc1_1_1_2, finance, 20260101).
assignment(e124, cc1_1_1_2, hr, 20260101).
assignment(e125, cc1_1_1_3, finance, 20260101).
assignment(e125, cc1_1_1_3, hr, 20260101).
assignment(e126, cc1_1_1_3, finance, 20260101).
assignment(e126, cc3_3_3_3, finance, 20260808).
assignment(e126, cc1_1_1_3, hr, 20260101).
assignment(e126, cc3_3_3_3, hr, 20260702).
assignment(e127, cc1_1_2_1, finance, 20260101).
assignment(e127, cc1_1_2_1, hr, 20260101).
assignment(e128, cc1_1_2_1, finance, 20260101).
assignment(e128, cc1_1_2_1, hr, 20260101).
assignment(e129, cc1_1_2_2, finance, 20260101).
assignment(e129, cc1_1_2_2, hr, 20260101).
assignment(e130, cc1_1_2_2, finance, 20260101).
assignment(e130, cc1_1_2_2, hr, 20260101).
assignment(e131, cc1_1_2_3, finance, 20260101).
assignment(e131, cc1_1_2_3, hr, 20260101).
assignment(e132, cc1_1_2_3, finance, 20260101).
assignment(e132, cc1_1_2_3, hr, 20260101).
assignment(e133, cc1_1_3_1, finance, 20260101).
assignment(e133, cc1_1_3_1, hr, 20260101).
assignment(e134, cc1_1_3_1, finance, 20260101).
assignment(e134, cc1_1_3_1, hr, 20260101).
assignment(e135, cc1_1_3_2, finance, 20260101).
assignment(e135, cc1_1_3_2, hr, 20260101).
assignment(e136, cc1_1_3_2, finance, 20260101).
assignment(e136, cc1_1_3_2, hr, 20260101).
assignment(e137, cc1_1_3_3, finance, 20260101).
assignment(e137, cc1_1_3_3, hr, 20260101).
assignment(e138, cc1_1_3_3, finance, 20260101).
assignment(e138, cc1_1_3_3, hr, 20260101).
assignment(e139, cc1_2_1_1, finance, 20260101).
assignment(e139, cc1_2_1_1, hr, 20260101).
assignment(e140, cc1_2_1_1, finance, 20260101).
assignment(e140, cc1_2_1_1, hr, 20260101).
assignment(e141, cc1_2_1_2, finance, 20260101).
assignment(e141, cc1_2_1_2, hr, 20260101).
assignment(e142, cc1_2_1_2, finance, 20260101).
assignment(e142, cc1_2_1_2, hr, 20260101).
assignment(e143, cc1_2_1_3, finance, 20260101).
assignment(e143, cc1_2_1_3, hr, 20260101).
assignment(e144, cc1_2_1_3, finance, 20260101).
assignment(e144, cc1_2_1_3, hr, 20260101).
assignment(e145, cc1_2_2_1, finance, 20260101).
assignment(e145, cc1_2_2_1, hr, 20260101).
assignment(e146, cc1_2_2_1, finance, 20260101).
assignment(e146, cc1_2_2_1, hr, 20260101).
assignment(e147, cc1_2_2_2, finance, 20260101).
assignment(e147, cc1_2_2_2, hr, 20260101).
assignment(e148, cc1_2_2_2, finance, 20260101).
assignment(e148, cc1_2_2_2, hr, 20260101).
assignment(e149, cc1_2_2_3, finance, 20260101).
assignment(e149, cc1_2_2_3, hr, 20260101).
assignment(e150, cc1_2_2_3, finance, 20260101).
assignment(e150, cc1_2_2_3, hr, 20260101).
assignment(e151, cc1_2_3_1, finance, 20260101).
assignment(e151, cc1_2_3_1, hr, 20260101).
assignment(e152, cc1_2_3_1, finance, 20260101).
assignment(e152, cc1_2_3_1, hr, 20260101).
assignment(e153, cc1_2_3_2, finance, 20260101).
assignment(e153, cc1_2_3_2, hr, 20260101).
assignment(e154, cc1_2_3_2, finance, 20260101).
assignment(e154, cc1_2_3_2, hr, 20260101).
assignment(e155, cc1_2_3_3, finance, 20260101).
assignment(e155, cc1_2_3_3, hr, 20260101).
assignment(e155, cc1_1_3_1, hr, 20260825).
assignment(e156, cc1_2_3_3, finance, 20260101).
assignment(e156, cc1_2_3_3, hr, 20260101).
assignment(e156, cc2_1_2_1, hr, 20260809).
assignment(e157, cc1_3_1_1, finance, 20260101).
assignment(e157, cc1_3_1_1, hr, 20260101).
assignment(e158, cc1_3_1_1, finance, 20260101).
assignment(e158, cc1_3_1_1, hr, 20260101).
assignment(e159, cc1_3_1_2, finance, 20260101).
assignment(e159, cc1_3_1_2, hr, 20260101).
assignment(e160, cc1_3_1_2, finance, 20260101).
assignment(e160, cc1_3_1_2, hr, 20260101).
assignment(e161, cc1_3_1_3, finance, 20260101).
assignment(e161, cc1_3_1_3, hr, 20260101).
assignment(e162, cc1_3_1_3, finance, 20260101).
assignment(e162, cc1_3_1_3, hr, 20260101).
assignment(e163, cc1_3_2_1, finance, 20260101).
assignment(e163, cc1_3_2_1, hr, 20260101).
assignment(e164, cc1_3_2_1, finance, 20260101).
assignment(e164, cc1_3_2_1, hr, 20260101).
assignment(e165, cc1_3_2_2, finance, 20260101).
assignment(e165, cc1_3_2_2, hr, 20260101).
assignment(e166, cc1_3_2_2, finance, 20260101).
assignment(e166, cc1_3_2_2, hr, 20260101).
assignment(e167, cc1_3_2_3, finance, 20260101).
assignment(e167, cc1_3_2_3, hr, 20260101).
assignment(e168, cc1_3_2_3, finance, 20260101).
assignment(e168, cc1_3_2_3, hr, 20260101).
assignment(e169, cc1_3_3_1, finance, 20260101).
assignment(e169, cc1_3_3_1, hr, 20260101).
assignment(e170, cc1_3_3_1, finance, 20260101).
assignment(e170, cc1_3_3_1, hr, 20260101).
assignment(e171, cc1_3_3_2, finance, 20260101).
assignment(e171, cc1_3_3_2, hr, 20260101).
assignment(e172, cc1_3_3_2, finance, 20260101).
assignment(e172, cc1_3_3_2, hr, 20260101).
assignment(e173, cc1_3_3_3, finance, 20260101).
assignment(e173, cc3_2_1_2, finance, 20260701).
assignment(e173, cc1_3_3_3, hr, 20260101).
assignment(e173, cc3_2_1_2, hr, 20260617).
assignment(e174, cc1_3_3_3, finance, 20260101).
assignment(e174, cc1_3_3_3, hr, 20260101).
assignment(e175, cc2_1_1_1, finance, 20260101).
assignment(e175, cc2_1_1_1, hr, 20260101).
assignment(e176, cc2_1_1_1, finance, 20260101).
assignment(e176, cc2_1_1_1, hr, 20260101).
assignment(e177, cc2_1_1_2, finance, 20260101).
assignment(e177, cc2_1_1_2, hr, 20260101).
assignment(e178, cc2_1_1_2, finance, 20260101).
assignment(e178, cc2_1_1_2, hr, 20260101).
assignment(e179, cc2_1_1_3, finance, 20260101).
assignment(e179, cc2_1_1_3, hr, 20260101).
assignment(e180, cc2_1_1_3, finance, 20260101).
assignment(e180, cc2_1_1_3, hr, 20260101).
assignment(e181, cc2_1_2_1, finance, 20260101).
assignment(e181, cc2_1_2_1, hr, 20260101).
assignment(e182, cc2_1_2_1, finance, 20260101).
assignment(e182, cc2_1_2_1, hr, 20260101).
assignment(e183, cc2_1_2_2, finance, 20260101).
assignment(e183, cc2_1_2_2, hr, 20260101).
assignment(e184, cc2_1_2_2, finance, 20260101).
assignment(e184, cc2_1_2_2, hr, 20260101).
assignment(e185, cc2_1_2_3, finance, 20260101).
assignment(e185, cc2_1_2_3, hr, 20260101).
assignment(e186, cc2_1_2_3, finance, 20260101).
assignment(e186, cc2_1_2_3, hr, 20260101).
assignment(e187, cc2_1_3_1, finance, 20260101).
assignment(e187, cc2_1_3_1, hr, 20260101).
assignment(e188, cc2_1_3_1, finance, 20260101).
assignment(e188, cc2_1_3_1, hr, 20260101).
assignment(e189, cc2_1_3_2, finance, 20260101).
assignment(e189, cc2_1_3_2, hr, 20260101).
assignment(e190, cc2_1_3_2, finance, 20260101).
assignment(e190, cc2_1_3_2, hr, 20260101).
assignment(e191, cc2_1_3_3, finance, 20260101).
assignment(e191, cc2_1_3_3, hr, 20260101).
assignment(e192, cc2_1_3_3, finance, 20260101).
assignment(e192, cc2_1_3_3, hr, 20260101).
assignment(e193, cc2_2_1_1, finance, 20260101).
assignment(e193, cc3_2_3_2, finance, 20260902).
assignment(e193, cc2_2_1_1, hr, 20260101).
assignment(e193, cc3_2_3_2, hr, 20260727).
assignment(e194, cc2_2_1_1, finance, 20260101).
assignment(e194, cc2_2_1_1, hr, 20260101).
assignment(e195, cc2_2_1_2, finance, 20260101).
assignment(e195, cc2_2_1_2, hr, 20260101).
assignment(e196, cc2_2_1_2, finance, 20260101).
assignment(e196, cc2_2_1_2, hr, 20260101).
assignment(e197, cc2_2_1_3, finance, 20260101).
assignment(e197, cc2_2_1_3, hr, 20260101).
assignment(e198, cc2_2_1_3, finance, 20260101).
assignment(e198, cc1_3_2_2, finance, 20260714).
assignment(e198, cc2_2_1_3, hr, 20260101).
assignment(e198, cc1_3_2_2, hr, 20260628).
assignment(e199, cc2_2_2_1, finance, 20260101).
assignment(e199, cc2_2_2_1, hr, 20260101).
assignment(e200, cc2_2_2_1, finance, 20260101).
assignment(e200, cc2_2_2_1, hr, 20260101).
assignment(e201, cc2_2_2_2, finance, 20260101).
assignment(e201, cc2_2_2_2, hr, 20260101).
assignment(e202, cc2_2_2_2, finance, 20260101).
assignment(e202, cc2_2_2_2, hr, 20260101).
assignment(e203, cc2_2_2_3, finance, 20260101).
assignment(e203, cc2_2_2_3, hr, 20260101).
assignment(e204, cc2_2_2_3, finance, 20260101).
assignment(e204, cc2_2_2_3, hr, 20260101).
assignment(e205, cc2_2_3_1, finance, 20260101).
assignment(e205, cc2_2_3_1, hr, 20260101).
assignment(e206, cc2_2_3_1, finance, 20260101).
assignment(e206, cc2_2_3_1, hr, 20260101).
assignment(e207, cc2_2_3_2, finance, 20260101).
assignment(e207, cc2_2_3_2, hr, 20260101).
assignment(e208, cc2_2_3_2, finance, 20260101).
assignment(e208, cc2_2_3_2, hr, 20260101).
assignment(e209, cc2_2_3_3, finance, 20260101).
assignment(e209, cc2_2_3_3, hr, 20260101).
assignment(e210, cc2_2_3_3, finance, 20260101).
assignment(e210, cc2_2_3_3, hr, 20260101).
assignment(e211, cc2_3_1_1, finance, 20260101).
assignment(e211, cc2_3_1_1, hr, 20260101).
assignment(e212, cc2_3_1_1, finance, 20260101).
assignment(e212, cc2_3_1_1, hr, 20260101).
assignment(e213, cc2_3_1_2, finance, 20260101).
assignment(e213, cc2_1_3_1, finance, 20260903).
assignment(e213, cc2_3_1_2, hr, 20260101).
assignment(e213, cc2_1_3_1, hr, 20260818).
assignment(e214, cc2_3_1_2, finance, 20260101).
assignment(e214, cc2_3_1_2, hr, 20260101).
assignment(e215, cc2_3_1_3, finance, 20260101).
assignment(e215, cc2_3_1_3, hr, 20260101).
assignment(e216, cc2_3_1_3, finance, 20260101).
assignment(e216, cc2_3_1_3, hr, 20260101).
assignment(e217, cc2_3_2_1, finance, 20260101).
assignment(e217, cc2_3_2_1, hr, 20260101).
assignment(e218, cc2_3_2_1, finance, 20260101).
assignment(e218, cc2_3_2_1, hr, 20260101).
assignment(e219, cc2_3_2_2, finance, 20260101).
assignment(e219, cc2_3_2_2, hr, 20260101).
assignment(e220, cc2_3_2_2, finance, 20260101).
assignment(e220, cc2_3_2_2, hr, 20260101).
assignment(e221, cc2_3_2_3, finance, 20260101).
assignment(e221, cc2_3_2_3, hr, 20260101).
assignment(e222, cc2_3_2_3, finance, 20260101).
assignment(e222, cc2_3_2_3, hr, 20260101).
assignment(e223, cc2_3_3_1, finance, 20260101).
assignment(e223, cc2_3_3_1, hr, 20260101).
assignment(e224, cc2_3_3_1, finance, 20260101).
assignment(e224, cc2_3_3_1, hr, 20260101).
assignment(e225, cc2_3_3_2, finance, 20260101).
assignment(e225, cc2_3_3_2, hr, 20260101).
assignment(e226, cc2_3_3_2, finance, 20260101).
assignment(e226, cc2_3_3_2, hr, 20260101).
assignment(e227, cc2_3_3_3, finance, 20260101).
assignment(e227, cc2_3_3_3, hr, 20260101).
assignment(e228, cc2_3_3_3, finance, 20260101).
assignment(e228, cc2_3_3_3, hr, 20260101).
assignment(e229, cc3_1_1_1, finance, 20260101).
assignment(e229, cc2_3_2_3, finance, 20260903).
assignment(e229, cc3_1_1_1, hr, 20260101).
assignment(e229, cc2_3_2_3, hr, 20260801).
assignment(e230, cc3_1_1_1, finance, 20260101).
assignment(e230, cc3_1_1_1, hr, 20260101).
assignment(e231, cc3_1_1_2, finance, 20260101).
assignment(e231, cc3_1_1_2, hr, 20260101).
assignment(e232, cc3_1_1_2, finance, 20260101).
assignment(e232, cc3_1_1_2, hr, 20260101).
assignment(e233, cc3_1_1_3, finance, 20260101).
assignment(e233, cc3_1_1_3, hr, 20260101).
assignment(e234, cc3_1_1_3, finance, 20260101).
assignment(e234, cc3_1_1_3, hr, 20260101).
assignment(e235, cc3_1_2_1, finance, 20260101).
assignment(e235, cc3_1_2_1, hr, 20260101).
assignment(e236, cc3_1_2_1, finance, 20260101).
assignment(e236, cc3_1_2_1, hr, 20260101).
assignment(e237, cc3_1_2_2, finance, 20260101).
assignment(e237, cc3_1_2_2, hr, 20260101).
assignment(e238, cc3_1_2_2, finance, 20260101).
assignment(e238, cc3_1_2_2, hr, 20260101).
assignment(e239, cc3_1_2_3, finance, 20260101).
assignment(e239, cc3_1_2_3, hr, 20260101).
assignment(e240, cc3_1_2_3, finance, 20260101).
assignment(e240, cc3_1_2_3, hr, 20260101).
assignment(e241, cc3_1_3_1, finance, 20260101).
assignment(e241, cc3_1_3_1, hr, 20260101).
assignment(e242, cc3_1_3_1, finance, 20260101).
assignment(e242, cc3_1_3_1, hr, 20260101).
assignment(e243, cc3_1_3_2, finance, 20260101).
assignment(e243, cc3_1_3_2, hr, 20260101).
assignment(e244, cc3_1_3_2, finance, 20260101).
assignment(e244, cc3_1_3_2, hr, 20260101).
assignment(e245, cc3_1_3_3, finance, 20260101).
assignment(e245, cc3_1_3_3, hr, 20260101).
assignment(e246, cc3_1_3_3, finance, 20260101).
assignment(e246, cc3_1_3_3, hr, 20260101).
assignment(e247, cc3_2_1_1, finance, 20260101).
assignment(e247, cc3_2_1_1, hr, 20260101).
assignment(e248, cc3_2_1_1, finance, 20260101).
assignment(e248, cc3_2_1_1, hr, 20260101).
assignment(e249, cc3_2_1_2, finance, 20260101).
assignment(e249, cc3_2_1_2, hr, 20260101).
assignment(e250, cc3_2_1_2, finance, 20260101).
assignment(e250, cc3_2_1_2, hr, 20260101).
assignment(e251, cc3_2_1_3, finance, 20260101).
assignment(e251, cc3_2_1_3, hr, 20260101).
assignment(e251, cc3_2_3_2, hr, 20260809).
assignment(e252, cc3_2_1_3, finance, 20260101).
assignment(e252, cc3_2_1_3, hr, 20260101).
assignment(e252, cc3_2_3_2, hr, 20260623).
assignment(e253, cc3_2_2_1, finance, 20260101).
assignment(e253, cc3_2_2_1, hr, 20260101).
assignment(e254, cc3_2_2_1, finance, 20260101).
assignment(e254, cc3_2_2_1, hr, 20260101).
assignment(e255, cc3_2_2_2, finance, 20260101).
assignment(e255, cc3_2_2_2, hr, 20260101).
assignment(e255, cc2_3_1_3, hr, 20260705).
assignment(e256, cc3_2_2_2, finance, 20260101).
assignment(e256, cc3_2_2_2, hr, 20260101).
assignment(e257, cc3_2_2_3, finance, 20260101).
assignment(e257, cc3_2_2_3, hr, 20260101).
assignment(e258, cc3_2_2_3, finance, 20260101).
assignment(e258, cc3_2_2_3, hr, 20260101).
assignment(e259, cc3_2_3_1, finance, 20260101).
assignment(e259, cc3_2_3_1, hr, 20260101).
assignment(e260, cc3_2_3_1, finance, 20260101).
assignment(e260, cc3_2_3_1, hr, 20260101).
assignment(e261, cc3_2_3_2, finance, 20260101).
assignment(e261, cc3_2_3_2, hr, 20260101).
assignment(e262, cc3_2_3_2, finance, 20260101).
assignment(e262, cc3_2_3_2, hr, 20260101).
assignment(e263, cc3_2_3_3, finance, 20260101).
assignment(e263, cc3_2_3_3, hr, 20260101).
assignment(e264, cc3_2_3_3, finance, 20260101).
assignment(e264, cc3_2_3_3, hr, 20260101).
assignment(e265, cc3_3_1_1, finance, 20260101).
assignment(e265, cc3_2_2_3, finance, 20260807).
assignment(e265, cc3_3_1_1, hr, 20260101).
assignment(e265, cc3_2_2_3, hr, 20260704).
assignment(e266, cc3_3_1_1, finance, 20260101).
assignment(e266, cc3_3_1_1, hr, 20260101).
assignment(e267, cc3_3_1_2, finance, 20260101).
assignment(e267, cc3_3_1_2, hr, 20260101).
assignment(e268, cc3_3_1_2, finance, 20260101).
assignment(e268, cc3_3_1_2, hr, 20260101).
assignment(e269, cc3_3_1_3, finance, 20260101).
assignment(e269, cc3_3_1_3, hr, 20260101).
assignment(e270, cc3_3_1_3, finance, 20260101).
assignment(e270, cc3_3_1_3, hr, 20260101).
assignment(e271, cc3_3_2_1, finance, 20260101).
assignment(e271, cc3_3_2_1, hr, 20260101).
assignment(e271, cc3_2_2_1, hr, 20260731).
assignment(e272, cc3_3_2_1, finance, 20260101).
assignment(e272, cc3_3_2_1, hr, 20260101).
assignment(e273, cc3_3_2_2, finance, 20260101).
assignment(e273, cc3_3_2_2, hr, 20260101).
assignment(e274, cc3_3_2_2, finance, 20260101).
assignment(e274, cc3_3_2_2, hr, 20260101).
assignment(e275, cc3_3_2_3, finance, 20260101).
assignment(e275, cc3_3_2_3, hr, 20260101).
assignment(e276, cc3_3_2_3, finance, 20260101).
assignment(e276, cc3_3_2_3, hr, 20260101).
assignment(e277, cc3_3_3_1, finance, 20260101).
assignment(e277, cc3_3_3_1, hr, 20260101).
assignment(e278, cc3_3_3_1, finance, 20260101).
assignment(e278, cc3_3_3_1, hr, 20260101).
assignment(e279, cc3_3_3_2, finance, 20260101).
assignment(e279, cc3_3_3_2, hr, 20260101).
assignment(e280, cc3_3_3_2, finance, 20260101).
assignment(e280, cc3_3_3_2, hr, 20260101).
assignment(e281, cc3_3_3_3, finance, 20260101).
assignment(e281, cc3_3_3_3, hr, 20260101).
assignment(e282, cc3_3_3_3, finance, 20260101).
assignment(e282, cc3_3_3_3, hr, 20260101).

% exemption(Exemption, Category, Granted): An exemption from the cap check for one request category, granted on a date.
:- dynamic exemption/3.
exemption(capex, capital, 20260101).

% exemption_withdrawn(Exemption, Date): The date an exemption was withdrawn; it no longer applies from that date on.
:- dynamic exemption_withdrawn/2.
exemption_withdrawn(capex, 20260810).

% Terms: concept(Term, Binding, Meaning) -- what the terms used by the definitions refer to.
:- discontiguous concept/3, rule/6, doc/2, cc_anc/2, in_subtree/2, chain/2, pending_total/2, headroom/2, over_cap/1, exposure/3, cap_breach/1, big_capital/1, headcount/2, limit_on/3, vendor_status_on/3, vendor_approved/1, cc_on/4, disputed_on/2, exemption_in_force/3, booked_total/2, committed/2, cap_scope/2, dept/2, governing_date/2.
concept('requester', 'req.requester', 'The requester of a request is the employee who raised it.').
concept('requester\'s cost centre', 'emp.cc', 'A requester\'s cost centre is the cost centre recorded for them in emp.').
concept('pending request', 'req.status = pending', 'A pending request is one whose status is pending. Cancelled requests are neither pending nor booked.').
concept('booked amount', 'booked.amount', 'The booked amount of a cost centre is what is booked directly on it. Its booked total is defined separately (R104).').
concept('cap', 'cap.amount', 'The cap of a cost centre bounds its committed spend (R106).').
concept('manager', 'reports.manager', 'An employee\'s manager is their direct manager only. Their reporting chain (R103) goes further up.').
concept('organisational unit', 'org_unit.unit', 'The organisational unit of a cost centre is a grouping of cost centres. An employee\'s department is defined separately (R113).').

% Questions of interpretation: fork(Id, Owner, Term, Question, Readings).
:- dynamic reading/2.
fork(c1, controller, 'committed spend', 'Does the committed spend of a cost centre include pending requests?', [booked_only, with_pending]).
fork(c2, procurement, 'governing date', 'Which date governs a request\'s dated rules (approval limits, vendor status, exemptions), the request date or today?', [request_date, today]).
fork(c3, hr, 'department', 'Is an employee\'s department their cost centre or their cost centre\'s organisational unit?', [cost_centre, org_unit]).
fork(c4, controller, 'cap scope', 'Does a request\'s cap check cover only the requester\'s cost centre, or also every ancestor of it?', [with_ancestors, own_only]).
fork(c6, controller, 'booked total', 'Does the booked total of a cost centre include what is booked on its descendants, or only what is booked directly on it?', [with_descendants, direct_only]).
% Open questions: undecided(Fork). The material does not choose between a fork's readings; each is an alternative it allows. Each reading's clauses below are guarded by reading(Fork, Reading), and no reading/2 fact is given: to evaluate a predicate under a reading, assume reading(Fork, Reading).
undecided(c1).
undecided(c2).
undecided(c3).
undecided(c4).
undecided(c6).

% Definitions: rule(Id, Head, Layer, Class, Conservative, Owner); doc(Head, Meaning); then the clauses.
% Owner none: no one could reasonably read the rule differently.
doc(cc_anc/2, 'cc_anc(C, A): A is an ancestor of cost centre C (parent, parent\'s parent, ...).').
doc(in_subtree/2, 'in_subtree(C, Root): C is Root or a descendant of Root.').
doc(chain/2, 'chain(E, M): M is in E\'s reporting chain (manager, manager\'s manager, ...).').
doc(pending_total/2, 'pending_total(C, P): P is the amount of pending requests raised in C or its descendants.').
doc(headroom/2, 'headroom(C, H): H is C\'s cap minus its committed spend.').
doc(over_cap/1, 'over_cap(C): C\'s committed spend exceeds its cap.').
doc(exposure/3, 'exposure(R, C, X): X is what C would have committed if R were approved.').
doc(cap_breach/1, 'cap_breach(R): approving R would exceed the cap of a cost centre in its cap scope.').
doc(big_capital/1, 'big_capital(R): R is a capital request over 50000.').
doc(headcount/2, 'headcount(D, N): N employees belong to department D.').
doc(limit_on/3, 'limit_on(Role, L, D): L is the approval limit of Role on date D.').
doc(vendor_status_on/3, 'vendor_status_on(V, S, D): vendor V has status S on date D.').
doc(vendor_approved/1, 'vendor_approved(R): R\'s vendor is approved on R\'s governing date.').
doc(cc_on/4, 'cc_on(E, C, Src, D): according to source Src, employee E belongs to C on date D.').
doc(disputed_on/2, 'disputed_on(E, D): hr and finance disagree about E\'s cost centre on date D.').
doc(exemption_in_force/3, 'exemption_in_force(X, Cat, D): exemption X for category Cat applies on date D.').
doc(booked_total/2, 'booked_total(C, T): T is the booked amount of C and all its descendants.').
doc(committed/2, 'committed(C, T): T is the committed spend of cost centre C.').
doc(cap_scope/2, 'cap_scope(R, C): cost centre C\'s cap applies to request R.').
doc(dept/2, 'dept(E, D): D is employee E\'s department.').
doc(governing_date/2, 'governing_date(R, D): D is the date that governs request R\'s dated rules.').
:- table cc_anc/2, chain/2.

% R101: The ancestors of a cost centre are its parent, its parent's parent, and so on.
rule('R101', cc_anc/2, 1, definitional, true, none).
cc_anc(C, A) :- cc_parent(C, A).
cc_anc(C, A) :- cc_parent(C, P), cc_anc(P, A).

% R102: A cost centre lies in the subtree of a cost centre X if it is X or one of X's descendants.
rule('R102', in_subtree/2, 1, definitional, true, none).
in_subtree(C, C) :- cc(C).
in_subtree(C, X) :- cc_anc(C, X).

% R103: An employee's reporting chain is their manager, their manager's manager, and so on. It does not include the employee.
rule('R103', chain/2, 1, definitional, true, none).
chain(E, M) :- reports(E, M).
chain(E, M) :- reports(E, X), chain(X, M).

% Open question c6 (owner: controller), on booked total: Does the booked total of a cost centre include what is booked on its descendants, or only what is booked directly on it? Not decided; the readings below are alternatives, one rule per reading.
% R104: The booked total of a cost centre is the sum of the booked amounts of every cost centre in its subtree (zero where nothing is booked).
rule('R104', booked_total/2, 1, definitional, true, controller).
booked_total(C, T) :- reading(c6, with_descendants), cc(C), aggregate_all(sum(B), (in_subtree(D, C), booked(D, B)), T).
% R104b: The booked total of a cost centre is its own booked amount, not counting its descendants (zero where nothing is booked).
rule('R104b', booked_total/2, 1, definitional, true, controller).
booked_total(C, T) :- reading(c6, direct_only), cc(C), aggregate_all(sum(B), booked(C, B), T).

% R105: The pending total of a cost centre is the sum of the amounts of pending requests whose requester's cost centre lies in its subtree.
rule('R105', pending_total/2, 1, definitional, true, none).
pending_total(C, P) :- cc(C), aggregate_all(sum(A), (req(_, E, A, _, _, _, pending), emp(E, _, D), in_subtree(D, C)), P).

% Open question c1 (owner: controller), on committed spend: Does the committed spend of a cost centre include pending requests? Not decided; the readings below are alternatives, one rule per reading.
% R106: The committed spend of a cost centre is its booked total. Pending requests do not count.
rule('R106', committed/2, 1, definitional, true, controller).
committed(C, T) :- reading(c1, booked_only), booked_total(C, T).
% R106b: The committed spend of a cost centre is its booked total plus its pending total.
rule('R106b', committed/2, 1, definitional, true, controller).
committed(C, T) :- reading(c1, with_pending), booked_total(C, B), pending_total(C, P), T is B + P.

% R107: The headroom of a cost centre is its cap minus its committed spend.
rule('R107', headroom/2, 1, definitional, true, none).
headroom(C, H) :- cap(C, K), committed(C, T), H is K - T.

% R108: A cost centre is over cap if its committed spend exceeds its cap.
rule('R108', over_cap/1, 1, definitional, true, none).
over_cap(C) :- cap(C, K), committed(C, T), T > K.

% Open question c4 (owner: controller), on cap scope: Does a request's cap check cover only the requester's cost centre, or also every ancestor of it? Not decided; the readings below are alternatives, one rule per reading.
% R109: A request's cap scope is its requester's cost centre and every ancestor of that cost centre.
rule('R109', cap_scope/2, 1, definitional, true, controller).
cap_scope(R, C) :- reading(c4, with_ancestors), req(R, E, _, _, _, _, _), emp(E, _, C).
cap_scope(R, A) :- reading(c4, with_ancestors), req(R, E, _, _, _, _, _), emp(E, _, C), cc_anc(C, A).
% R109b: A request's cap scope is its requester's cost centre only.
rule('R109b', cap_scope/2, 1, definitional, true, controller).
cap_scope(R, C) :- reading(c4, own_only), req(R, E, _, _, _, _, _), emp(E, _, C).

% R110: A request's exposure at a cost centre in its cap scope is that centre's committed spend plus the request amount, not counting the request itself twice if committed spend already includes it.
rule('R110', exposure/3, 1, definitional, true, none).
exposure(R, C, X) :- req(R, _, A, _, _, _, St), cap_scope(R, C), committed(C, T),
    ( reading(c1, with_pending), St == pending -> X is T ; X is T + A ).

% R111: A request breaches a cap if its exposure at some cost centre in its cap scope exceeds that centre's cap.
rule('R111', cap_breach/1, 1, definitional, true, none).
cap_breach(R) :- exposure(R, C, X), cap(C, K), X > K.

% R112: A big capital request is a capital request whose amount is over 50000.
rule('R112', big_capital/1, 1, definitional, true, none).
big_capital(R) :- req(R, _, A, capital, _, _, _), A > 50000.

% Open question c3 (owner: hr), on department: Is an employee's department their cost centre or their cost centre's organisational unit? Not decided; the readings below are alternatives, one rule per reading.
% R113: An employee's department is their cost centre.
rule('R113', dept/2, 1, definitional, true, hr).
dept(E, D) :- reading(c3, cost_centre), emp(E, _, D).
% R113b: An employee's department is the organisational unit of their cost centre.
rule('R113b', dept/2, 1, definitional, true, hr).
dept(E, D) :- reading(c3, org_unit), emp(E, _, C), org_unit(C, D).

% R114: The headcount of a department is the number of employees whose department it is.
rule('R114', headcount/2, 1, definitional, true, none).
headcount(D, N) :- setof(X, E^dept(E, X), Ds), member(D, Ds), aggregate_all(count, dept(_, D), N).

% Open question c2 (owner: procurement), on governing date: Which date governs a request's dated rules (approval limits, vendor status, exemptions), the request date or today? Not decided; the readings below are alternatives, one rule per reading.
% R201: A request's dated rules (approval limits, vendor status, exemptions) are read as of the date the request was raised.
rule('R201', governing_date/2, 2, temporal, true, procurement).
governing_date(R, D) :- reading(c2, request_date), req(R, _, _, _, _, D, _).
% R201b: A request's dated rules (approval limits, vendor status, exemptions) are read as of today.
rule('R201b', governing_date/2, 2, temporal, true, procurement).
governing_date(R, D) :- reading(c2, today), req(R, _, _, _, _, _, _), today(D).

% R202: A role's approval limit on a date is the limit of the version valid on that date.
rule('R202', limit_on/3, 2, temporal, true, none).
limit_on(Role, L, D) :- role_limit_version(Role, L, F, T), F =< D, D =< T.

% R203: A vendor's status on a date is the status of the period that contains that date.
rule('R203', vendor_status_on/3, 2, temporal, true, none).
vendor_status_on(V, S, D) :- vendor_status(V, S, F, T), F =< D, D =< T.

% R204: A request's vendor is approved for it if the vendor's status on the request's governing date is approved.
rule('R204', vendor_approved/1, 2, temporal, true, none).
vendor_approved(R) :- req(R, _, _, _, V, _, _), governing_date(R, D), vendor_status_on(V, approved, D).

% R205: According to a source, an employee belongs on a date to the cost centre of that source's latest assignment record effective on or before that date.
rule('R205', cc_on/4, 2, temporal, true, none).
cc_on(E, C, Src, D) :- assignment(E, C, Src, F), F =< D,
    \+ ( assignment(E, _, Src, F2), F2 =< D, F2 > F ).

% R206: An employee's cost centre is disputed on a date if hr and finance place them in different cost centres on that date.
rule('R206', disputed_on/2, 2, fitness, true, none).
disputed_on(E, D) :- cc_on(E, C1, hr, D), cc_on(E, C2, finance, D), C1 \== C2.

% R207: An exemption is in force on a date if it was granted on or before that date and not withdrawn on or before that date.
rule('R207', exemption_in_force/3, 2, temporal, true, none).
exemption_in_force(X, Cat, D) :- exemption(X, Cat, G), G =< D,
    \+ ( exemption_withdrawn(X, W), W =< D ).
