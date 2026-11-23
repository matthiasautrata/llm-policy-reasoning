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
cc(cc1_1_2).
cc(cc1_1_3).
cc(cc1_2).
cc(cc1_2_1).
cc(cc1_2_2).
cc(cc1_2_3).
cc(cc1_3).
cc(cc1_3_1).
cc(cc1_3_2).
cc(cc1_3_3).
cc(cc2).
cc(cc2_1).
cc(cc2_1_1).
cc(cc2_1_2).
cc(cc2_1_3).
cc(cc2_2).
cc(cc2_2_1).
cc(cc2_2_2).
cc(cc2_2_3).
cc(cc2_3).
cc(cc2_3_1).
cc(cc2_3_2).
cc(cc2_3_3).
cc(cc3).
cc(cc3_1).
cc(cc3_1_1).
cc(cc3_1_2).
cc(cc3_1_3).
cc(cc3_2).
cc(cc3_2_1).
cc(cc3_2_2).
cc(cc3_2_3).
cc(cc3_3).
cc(cc3_3_1).
cc(cc3_3_2).
cc(cc3_3_3).

% cc_parent(Cc, Parent): The parent of a cost centre. The root cost centre has no row.
:- dynamic cc_parent/2.
cc_parent(cc1, company).
cc_parent(cc1_1, cc1).
cc_parent(cc1_1_1, cc1_1).
cc_parent(cc1_1_2, cc1_1).
cc_parent(cc1_1_3, cc1_1).
cc_parent(cc1_2, cc1).
cc_parent(cc1_2_1, cc1_2).
cc_parent(cc1_2_2, cc1_2).
cc_parent(cc1_2_3, cc1_2).
cc_parent(cc1_3, cc1).
cc_parent(cc1_3_1, cc1_3).
cc_parent(cc1_3_2, cc1_3).
cc_parent(cc1_3_3, cc1_3).
cc_parent(cc2, company).
cc_parent(cc2_1, cc2).
cc_parent(cc2_1_1, cc2_1).
cc_parent(cc2_1_2, cc2_1).
cc_parent(cc2_1_3, cc2_1).
cc_parent(cc2_2, cc2).
cc_parent(cc2_2_1, cc2_2).
cc_parent(cc2_2_2, cc2_2).
cc_parent(cc2_2_3, cc2_2).
cc_parent(cc2_3, cc2).
cc_parent(cc2_3_1, cc2_3).
cc_parent(cc2_3_2, cc2_3).
cc_parent(cc2_3_3, cc2_3).
cc_parent(cc3, company).
cc_parent(cc3_1, cc3).
cc_parent(cc3_1_1, cc3_1).
cc_parent(cc3_1_2, cc3_1).
cc_parent(cc3_1_3, cc3_1).
cc_parent(cc3_2, cc3).
cc_parent(cc3_2_1, cc3_2).
cc_parent(cc3_2_2, cc3_2).
cc_parent(cc3_2_3, cc3_2).
cc_parent(cc3_3, cc3).
cc_parent(cc3_3_1, cc3_3).
cc_parent(cc3_3_2, cc3_3).
cc_parent(cc3_3_3, cc3_3).

% org_unit(Cc, Unit): The organisational unit a cost centre belongs to.
:- dynamic org_unit/2.
org_unit(company, leadership).
org_unit(cc1, leadership).
org_unit(cc1_1, leadership).
org_unit(cc1_1_1, delivery).
org_unit(cc1_1_2, support).
org_unit(cc1_1_3, support).
org_unit(cc1_2, leadership).
org_unit(cc1_2_1, delivery).
org_unit(cc1_2_2, delivery).
org_unit(cc1_2_3, delivery).
org_unit(cc1_3, leadership).
org_unit(cc1_3_1, delivery).
org_unit(cc1_3_2, support).
org_unit(cc1_3_3, support).
org_unit(cc2, leadership).
org_unit(cc2_1, leadership).
org_unit(cc2_1_1, delivery).
org_unit(cc2_1_2, delivery).
org_unit(cc2_1_3, delivery).
org_unit(cc2_2, leadership).
org_unit(cc2_2_1, delivery).
org_unit(cc2_2_2, support).
org_unit(cc2_2_3, delivery).
org_unit(cc2_3, leadership).
org_unit(cc2_3_1, delivery).
org_unit(cc2_3_2, support).
org_unit(cc2_3_3, support).
org_unit(cc3, leadership).
org_unit(cc3_1, leadership).
org_unit(cc3_1_1, delivery).
org_unit(cc3_1_2, support).
org_unit(cc3_1_3, support).
org_unit(cc3_2, leadership).
org_unit(cc3_2_1, delivery).
org_unit(cc3_2_2, support).
org_unit(cc3_2_3, support).
org_unit(cc3_3, leadership).
org_unit(cc3_3_1, support).
org_unit(cc3_3_2, delivery).
org_unit(cc3_3_3, support).

% emp(Emp, Role, Cc): An employee, their role, and their current cost centre as finance records it.
:- dynamic emp/3.
emp(e000, vp, company).
emp(e001, director, cc1).
emp(e002, senior_manager, cc1_1).
emp(e003, manager, cc1_1_1).
emp(e004, manager, cc1_1_2).
emp(e005, manager, cc1_1_3).
emp(e006, senior_manager, cc1_2).
emp(e007, manager, cc1_2_1).
emp(e008, manager, cc1_2_2).
emp(e009, manager, cc1_2_3).
emp(e010, senior_manager, cc1_3).
emp(e011, manager, cc1_3_1).
emp(e012, manager, cc1_3_2).
emp(e013, manager, cc1_3_3).
emp(e014, director, cc2).
emp(e015, senior_manager, cc2_1).
emp(e016, manager, cc2_1_1).
emp(e017, manager, cc2_1_2).
emp(e018, manager, cc2_1_3).
emp(e019, senior_manager, cc2_2).
emp(e020, manager, cc2_2_1).
emp(e021, manager, cc2_2_2).
emp(e022, manager, cc2_2_3).
emp(e023, senior_manager, cc2_3).
emp(e024, manager, cc2_3_1).
emp(e025, manager, cc2_3_2).
emp(e026, manager, cc2_3_3).
emp(e027, director, cc3).
emp(e028, senior_manager, cc3_1).
emp(e029, manager, cc3_1_1).
emp(e030, manager, cc3_1_2).
emp(e031, manager, cc3_1_3).
emp(e032, senior_manager, cc3_2).
emp(e033, manager, cc3_2_1).
emp(e034, manager, cc3_2_2).
emp(e035, manager, cc3_2_3).
emp(e036, senior_manager, cc3_3).
emp(e037, manager, cc3_3_1).
emp(e038, manager, cc3_3_2).
emp(e039, manager, cc3_3_3).
emp(e040, analyst, cc1_1_1).
emp(e041, analyst, cc1_1_1).
emp(e042, analyst, cc1_1_1).
emp(e043, analyst, cc1_2_1).
emp(e044, analyst, cc1_1_2).
emp(e045, analyst, cc1_1_2).
emp(e046, analyst, cc1_1_3).
emp(e047, analyst, cc1_1_3).
emp(e048, analyst, cc1_1_3).
emp(e049, analyst, cc1_2_1).
emp(e050, analyst, cc1_2_1).
emp(e051, analyst, cc1_2_1).
emp(e052, analyst, cc1_2_2).
emp(e053, analyst, cc1_2_2).
emp(e054, analyst, cc1_2_2).
emp(e055, analyst, cc1_2_3).
emp(e056, analyst, cc1_2_3).
emp(e057, analyst, cc1_2_3).
emp(e058, analyst, cc1_3_1).
emp(e059, analyst, cc1_3_1).
emp(e060, analyst, cc1_3_1).
emp(e061, analyst, cc1_3_2).
emp(e062, analyst, cc1_3_2).
emp(e063, analyst, cc1_3_2).
emp(e064, analyst, cc1_3_3).
emp(e065, analyst, cc1_3_3).
emp(e066, analyst, cc1_3_3).
emp(e067, analyst, cc2_1_1).
emp(e068, analyst, cc2_1_1).
emp(e069, analyst, cc2_1_1).
emp(e070, analyst, cc2_1_2).
emp(e071, analyst, cc2_1_2).
emp(e072, analyst, cc2_1_2).
emp(e073, analyst, cc2_1_3).
emp(e074, analyst, cc3_1_1).
emp(e075, analyst, cc2_1_3).
emp(e076, analyst, cc2_2_1).
emp(e077, analyst, cc3_1_3).
emp(e078, analyst, cc2_2_1).
emp(e079, analyst, cc2_2_2).
emp(e080, analyst, cc2_2_2).
emp(e081, analyst, cc2_2_2).
emp(e082, analyst, cc2_2_3).
emp(e083, analyst, cc2_2_3).
emp(e084, analyst, cc2_2_3).
emp(e085, analyst, cc2_3_1).
emp(e086, analyst, cc2_3_1).
emp(e087, analyst, cc2_3_1).
emp(e088, analyst, cc2_3_2).
emp(e089, analyst, cc2_3_2).
emp(e090, analyst, cc2_3_2).
emp(e091, analyst, cc2_3_3).
emp(e092, analyst, cc2_3_3).
emp(e093, analyst, cc2_3_3).
emp(e094, analyst, cc3_1_1).
emp(e095, analyst, cc3_1_1).
emp(e096, analyst, cc3_1_1).
emp(e097, analyst, cc3_1_2).
emp(e098, analyst, cc3_1_2).
emp(e099, analyst, cc2_1_3).
emp(e100, analyst, cc3_1_3).
emp(e101, analyst, cc3_1_3).
emp(e102, analyst, cc3_1_3).
emp(e103, analyst, cc3_2_1).
emp(e104, analyst, cc3_2_1).
emp(e105, analyst, cc3_2_1).
emp(e106, analyst, cc3_2_2).
emp(e107, analyst, cc3_2_2).
emp(e108, analyst, cc3_2_2).
emp(e109, analyst, cc3_2_3).
emp(e110, analyst, cc3_1_1).
emp(e111, analyst, cc3_2_3).
emp(e112, analyst, cc3_3_1).
emp(e113, analyst, cc3_3_1).
emp(e114, analyst, cc3_3_1).
emp(e115, analyst, cc3_3_2).
emp(e116, analyst, cc3_3_2).
emp(e117, analyst, cc3_3_2).
emp(e118, analyst, cc3_3_3).
emp(e119, analyst, cc3_3_3).
emp(e120, analyst, cc3_3_3).

% reports(Emp, Manager): An employee's direct manager.
:- dynamic reports/2.
reports(e001, e000).
reports(e002, e001).
reports(e003, e002).
reports(e004, e002).
reports(e005, e002).
reports(e006, e001).
reports(e007, e006).
reports(e008, e006).
reports(e009, e006).
reports(e010, e001).
reports(e011, e010).
reports(e012, e010).
reports(e013, e010).
reports(e014, e000).
reports(e015, e014).
reports(e016, e015).
reports(e017, e015).
reports(e018, e015).
reports(e019, e014).
reports(e020, e019).
reports(e021, e019).
reports(e022, e019).
reports(e023, e014).
reports(e024, e023).
reports(e025, e023).
reports(e026, e023).
reports(e027, e000).
reports(e028, e027).
reports(e029, e028).
reports(e030, e028).
reports(e031, e028).
reports(e032, e027).
reports(e033, e032).
reports(e034, e032).
reports(e035, e032).
reports(e036, e027).
reports(e037, e036).
reports(e038, e036).
reports(e039, e036).
reports(e040, e003).
reports(e041, e003).
reports(e042, e003).
reports(e043, e007).
reports(e044, e004).
reports(e045, e004).
reports(e046, e005).
reports(e047, e005).
reports(e048, e005).
reports(e049, e007).
reports(e050, e007).
reports(e051, e007).
reports(e052, e008).
reports(e053, e008).
reports(e054, e008).
reports(e055, e009).
reports(e056, e009).
reports(e057, e009).
reports(e058, e011).
reports(e059, e011).
reports(e060, e011).
reports(e061, e012).
reports(e062, e012).
reports(e063, e012).
reports(e064, e013).
reports(e065, e013).
reports(e066, e013).
reports(e067, e016).
reports(e068, e016).
reports(e069, e016).
reports(e070, e017).
reports(e071, e017).
reports(e072, e017).
reports(e073, e018).
reports(e074, e029).
reports(e075, e018).
reports(e076, e020).
reports(e077, e031).
reports(e078, e020).
reports(e079, e021).
reports(e080, e021).
reports(e081, e021).
reports(e082, e022).
reports(e083, e022).
reports(e084, e022).
reports(e085, e024).
reports(e086, e024).
reports(e087, e024).
reports(e088, e025).
reports(e089, e025).
reports(e090, e025).
reports(e091, e026).
reports(e092, e026).
reports(e093, e026).
reports(e094, e029).
reports(e095, e029).
reports(e096, e029).
reports(e097, e030).
reports(e098, e030).
reports(e099, e018).
reports(e100, e031).
reports(e101, e031).
reports(e102, e031).
reports(e103, e033).
reports(e104, e033).
reports(e105, e033).
reports(e106, e034).
reports(e107, e034).
reports(e108, e034).
reports(e109, e035).
reports(e110, e029).
reports(e111, e035).
reports(e112, e037).
reports(e113, e037).
reports(e114, e037).
reports(e115, e038).
reports(e116, e038).
reports(e117, e038).
reports(e118, e039).
reports(e119, e039).
reports(e120, e039).

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
req(r001, e065, 90000, hardware, dyne, 20260915, cancelled).
req(r002, e067, 38000, services, acme, 20260722, pending).
req(r003, e095, 30000, capital, cog, 20260809, pending).
req(r004, e004, 120000, software, edge, 20260627, pending).
req(r005, e115, 8000, capital, fern, 20260603, pending).
req(r006, e043, 3000, services, edge, 20260615, pending).
req(r007, e043, 20000, software, bolt, 20260729, pending).
req(r008, e051, 30000, services, edge, 20260915, cancelled).
req(r009, e110, 60000, services, dyne, 20260725, pending).
req(r010, e094, 45000, hardware, bolt, 20260723, pending).
req(r011, e081, 90000, capital, fern, 20260626, pending).
req(r012, e032, 38000, capital, edge, 20260715, pending).
req(r013, e077, 3000, hardware, cog, 20260618, cancelled).
req(r014, e112, 38000, services, fern, 20260818, pending).
req(r015, e106, 12000, capital, fern, 20260827, pending).
req(r016, e081, 60000, capital, cog, 20260606, pending).
req(r017, e018, 3000, capital, dyne, 20260811, pending).
req(r018, e056, 12000, software, acme, 20260911, pending).
req(r019, e092, 8000, hardware, dyne, 20260610, pending).
req(r020, e069, 8000, services, cog, 20260822, pending).
req(r021, e012, 20000, services, fern, 20260615, cancelled).
req(r022, e021, 12000, hardware, dyne, 20260609, pending).
req(r023, e061, 20000, software, bolt, 20260824, pending).
req(r024, e107, 8000, software, acme, 20260824, pending).
req(r025, e094, 8000, services, fern, 20260906, pending).
req(r026, e046, 45000, software, bolt, 20260904, pending).
req(r027, e087, 60000, services, acme, 20260716, pending).
req(r028, e025, 3000, hardware, fern, 20260803, pending).
req(r029, e098, 20000, capital, dyne, 20260711, pending).
req(r030, e088, 20000, software, bolt, 20260730, pending).
req(r031, e018, 30000, software, fern, 20260906, pending).
req(r032, e067, 8000, capital, fern, 20260821, pending).
req(r033, e044, 8000, services, cog, 20260811, pending).
req(r034, e085, 120000, capital, acme, 20260912, pending).
req(r035, e088, 20000, capital, dyne, 20260830, pending).
req(r036, e072, 30000, services, edge, 20260903, pending).
req(r037, e058, 120000, services, acme, 20260827, pending).
req(r038, e086, 45000, hardware, dyne, 20260624, pending).
req(r039, e076, 12000, software, cog, 20260622, pending).
req(r040, e078, 45000, services, acme, 20260617, pending).
req(r041, e045, 45000, capital, dyne, 20260906, pending).
req(r042, e025, 8000, software, edge, 20260829, pending).
req(r043, e045, 120000, hardware, fern, 20260812, pending).
req(r044, e102, 90000, services, acme, 20260826, pending).
req(r045, e020, 90000, services, dyne, 20260711, pending).
req(r046, e007, 12000, software, fern, 20260810, pending).
req(r047, e033, 12000, services, fern, 20260620, pending).
req(r048, e018, 30000, services, acme, 20260901, pending).
req(r049, e012, 90000, software, dyne, 20260907, pending).
req(r050, e075, 38000, services, dyne, 20260718, pending).
req(r051, e072, 12000, software, acme, 20260709, pending).
req(r052, e089, 3000, software, acme, 20260626, cancelled).
req(r053, e105, 90000, software, edge, 20260616, pending).
req(r054, e048, 38000, software, acme, 20260718, cancelled).
req(r055, e095, 90000, software, bolt, 20260729, cancelled).
req(r056, e085, 38000, capital, fern, 20260609, pending).
req(r057, e104, 8000, capital, fern, 20260710, pending).
req(r058, e026, 3000, software, cog, 20260911, cancelled).
req(r059, e080, 12000, hardware, fern, 20260728, pending).
req(r060, e095, 120000, services, cog, 20260810, pending).
req(r061, e106, 120000, capital, fern, 20260828, pending).
req(r062, e075, 8000, services, edge, 20260908, pending).
req(r063, e032, 30000, services, bolt, 20260610, pending).
req(r064, e093, 12000, services, cog, 20260808, pending).
req(r065, e074, 38000, capital, cog, 20260823, pending).
req(r066, e082, 20000, hardware, bolt, 20260602, pending).
req(r067, e017, 12000, capital, cog, 20260825, pending).
req(r068, e024, 60000, software, dyne, 20260721, pending).
req(r069, e066, 45000, capital, acme, 20260620, cancelled).
req(r070, e028, 12000, hardware, cog, 20260826, pending).
req(r071, e057, 38000, services, acme, 20260624, pending).
req(r072, e040, 30000, hardware, fern, 20260715, pending).
req(r073, e077, 20000, services, edge, 20260805, pending).
req(r074, e109, 30000, capital, cog, 20260823, pending).
req(r075, e053, 60000, software, acme, 20260701, pending).
req(r076, e014, 38000, hardware, fern, 20260616, pending).
req(r077, e092, 120000, hardware, fern, 20260818, pending).
req(r078, e020, 12000, software, acme, 20260602, pending).
req(r079, e104, 30000, hardware, fern, 20260708, pending).
req(r080, e096, 30000, hardware, bolt, 20260611, pending).
req(r081, e014, 38000, capital, edge, 20260828, pending).
req(r082, e115, 60000, capital, edge, 20260707, pending).
req(r083, e099, 12000, capital, bolt, 20260915, cancelled).
req(r084, e032, 90000, hardware, bolt, 20260621, pending).
req(r085, e106, 20000, hardware, fern, 20260703, pending).
req(r086, e038, 45000, hardware, edge, 20260619, pending).
req(r087, e034, 45000, services, bolt, 20260826, pending).
req(r088, e012, 3000, capital, cog, 20260608, pending).
req(r089, e083, 30000, software, bolt, 20260621, pending).
req(r090, e086, 8000, software, acme, 20260710, pending).
req(r091, e083, 120000, services, fern, 20260724, pending).
req(r092, e060, 120000, hardware, bolt, 20260801, pending).
req(r093, e072, 30000, services, edge, 20260603, pending).
req(r094, e068, 8000, services, fern, 20260819, cancelled).
req(r095, e004, 12000, services, fern, 20260609, pending).
req(r096, e063, 30000, services, bolt, 20260601, pending).
req(r097, e117, 30000, services, dyne, 20260806, pending).
req(r098, e088, 60000, services, fern, 20260630, pending).
req(r099, e065, 45000, hardware, cog, 20260625, pending).
req(r100, e030, 90000, hardware, acme, 20260814, pending).
req(r101, e082, 20000, capital, dyne, 20260814, pending).
req(r102, e007, 45000, services, bolt, 20260816, pending).

% emergency(Req): A request flagged as an emergency.
:- dynamic emergency/1.
emergency(r006).
emergency(r007).
emergency(r011).
emergency(r018).
emergency(r022).
emergency(r027).
emergency(r031).
emergency(r042).
emergency(r056).
emergency(r058).
emergency(r059).
emergency(r061).
emergency(r062).
emergency(r067).
emergency(r073).
emergency(r075).
emergency(r083).
emergency(r084).
emergency(r088).
emergency(r091).
emergency(r095).
emergency(r097).

% violation(Emp): An employee with a recorded policy violation.
:- dynamic violation/1.
violation(e006).
violation(e026).
violation(e028).
violation(e034).
violation(e043).
violation(e054).
violation(e062).
violation(e069).
violation(e070).
violation(e086).
violation(e097).
violation(e107).

% booked(Cc, Amount): Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
:- dynamic booked/2.
booked(cc1_1_1, 63000).
booked(cc1_1_2, 63000).
booked(cc1_1_3, 81000).
booked(cc1_2_1, 115000).
booked(cc1_2_2, 95000).
booked(cc1_2_3, 97000).
booked(cc1_3_1, 126000).
booked(cc1_3_2, 47000).
booked(cc1_3_3, 119000).
booked(cc2_1_1, 47000).
booked(cc2_1_2, 72000).
booked(cc2_1_3, 73000).
booked(cc2_2_1, 62000).
booked(cc2_2_2, 108000).
booked(cc2_2_3, 86000).
booked(cc2_3_1, 73000).
booked(cc2_3_2, 63000).
booked(cc2_3_3, 86000).
booked(cc3_1_1, 113000).
booked(cc3_1_2, 92000).
booked(cc3_1_3, 105000).
booked(cc3_2_1, 69000).
booked(cc3_2_2, 54000).
booked(cc3_2_3, 75000).
booked(cc3_3_1, 56000).
booked(cc3_3_2, 41000).
booked(cc3_3_3, 59000).
booked(company, 14000).
booked(cc2, 9000).
booked(cc2_2, 19000).
booked(cc3_2, 29000).
booked(cc3_3, 35000).

% cap(Cc, Amount): The spending cap of a cost centre this quarter.
:- dynamic cap/2.
cap(company, 2695000).
cap(cc1, 926000).
cap(cc1_1, 238000).
cap(cc1_1_1, 100000).
cap(cc1_1_2, 61000).
cap(cc1_1_3, 78000).
cap(cc1_2, 399000).
cap(cc1_2_1, 184000).
cap(cc1_2_2, 133000).
cap(cc1_2_3, 94000).
cap(cc1_3, 306000).
cap(cc1_3_1, 176000).
cap(cc1_3_2, 48000).
cap(cc1_3_3, 115000).
cap(cc2, 732000).
cap(cc2_1, 220000).
cap(cc2_1_1, 75000).
cap(cc2_1_2, 86000).
cap(cc2_1_3, 116000).
cap(cc2_2, 288000).
cap(cc2_2_1, 63000).
cap(cc2_2_2, 151000).
cap(cc2_2_3, 83000).
cap(cc2_3, 255000).
cap(cc2_3_1, 102000).
cap(cc2_3_2, 61000).
cap(cc2_3_3, 103000).
cap(cc3, 946000).
cap(cc3_1, 465000).
cap(cc3_1_1, 158000).
cap(cc3_1_2, 128000).
cap(cc3_1_3, 101000).
cap(cc3_2, 340000).
cap(cc3_2_1, 110000).
cap(cc3_2_2, 55000).
cap(cc3_2_3, 90000).
cap(cc3_3, 219000).
cap(cc3_3_1, 78000).
cap(cc3_3_2, 65000).
cap(cc3_3_3, 82000).

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
assignment(e004, cc1_1_2, finance, 20260101).
assignment(e004, cc1_1_2, hr, 20260101).
assignment(e005, cc1_1_3, finance, 20260101).
assignment(e005, cc1_1_3, hr, 20260101).
assignment(e006, cc1_2, finance, 20260101).
assignment(e006, cc1_2, hr, 20260101).
assignment(e007, cc1_2_1, finance, 20260101).
assignment(e007, cc1_2_1, hr, 20260101).
assignment(e008, cc1_2_2, finance, 20260101).
assignment(e008, cc1_2_2, hr, 20260101).
assignment(e009, cc1_2_3, finance, 20260101).
assignment(e009, cc1_2_3, hr, 20260101).
assignment(e010, cc1_3, finance, 20260101).
assignment(e010, cc1_3, hr, 20260101).
assignment(e011, cc1_3_1, finance, 20260101).
assignment(e011, cc1_3_1, hr, 20260101).
assignment(e012, cc1_3_2, finance, 20260101).
assignment(e012, cc1_3_2, hr, 20260101).
assignment(e013, cc1_3_3, finance, 20260101).
assignment(e013, cc1_3_3, hr, 20260101).
assignment(e014, cc2, finance, 20260101).
assignment(e014, cc2, hr, 20260101).
assignment(e015, cc2_1, finance, 20260101).
assignment(e015, cc2_1, hr, 20260101).
assignment(e016, cc2_1_1, finance, 20260101).
assignment(e016, cc2_1_1, hr, 20260101).
assignment(e017, cc2_1_2, finance, 20260101).
assignment(e017, cc2_1_2, hr, 20260101).
assignment(e018, cc2_1_3, finance, 20260101).
assignment(e018, cc2_1_3, hr, 20260101).
assignment(e019, cc2_2, finance, 20260101).
assignment(e019, cc2_2, hr, 20260101).
assignment(e020, cc2_2_1, finance, 20260101).
assignment(e020, cc2_2_1, hr, 20260101).
assignment(e021, cc2_2_2, finance, 20260101).
assignment(e021, cc2_2_2, hr, 20260101).
assignment(e022, cc2_2_3, finance, 20260101).
assignment(e022, cc2_2_3, hr, 20260101).
assignment(e023, cc2_3, finance, 20260101).
assignment(e023, cc2_3, hr, 20260101).
assignment(e024, cc2_3_1, finance, 20260101).
assignment(e024, cc2_3_1, hr, 20260101).
assignment(e025, cc2_3_2, finance, 20260101).
assignment(e025, cc2_3_2, hr, 20260101).
assignment(e026, cc2_3_3, finance, 20260101).
assignment(e026, cc2_3_3, hr, 20260101).
assignment(e027, cc3, finance, 20260101).
assignment(e027, cc3, hr, 20260101).
assignment(e028, cc3_1, finance, 20260101).
assignment(e028, cc3_1, hr, 20260101).
assignment(e029, cc3_1_1, finance, 20260101).
assignment(e029, cc3_1_1, hr, 20260101).
assignment(e030, cc3_1_2, finance, 20260101).
assignment(e030, cc3_1_2, hr, 20260101).
assignment(e031, cc3_1_3, finance, 20260101).
assignment(e031, cc3_1_3, hr, 20260101).
assignment(e032, cc3_2, finance, 20260101).
assignment(e032, cc3_2, hr, 20260101).
assignment(e033, cc3_2_1, finance, 20260101).
assignment(e033, cc3_2_1, hr, 20260101).
assignment(e034, cc3_2_2, finance, 20260101).
assignment(e034, cc3_2_2, hr, 20260101).
assignment(e035, cc3_2_3, finance, 20260101).
assignment(e035, cc3_2_3, hr, 20260101).
assignment(e036, cc3_3, finance, 20260101).
assignment(e036, cc3_3, hr, 20260101).
assignment(e037, cc3_3_1, finance, 20260101).
assignment(e037, cc3_3_1, hr, 20260101).
assignment(e038, cc3_3_2, finance, 20260101).
assignment(e038, cc3_3_2, hr, 20260101).
assignment(e039, cc3_3_3, finance, 20260101).
assignment(e039, cc3_3_3, hr, 20260101).
assignment(e040, cc1_1_1, finance, 20260101).
assignment(e040, cc1_1_1, hr, 20260101).
assignment(e041, cc1_1_1, finance, 20260101).
assignment(e041, cc1_1_1, hr, 20260101).
assignment(e042, cc1_1_1, finance, 20260101).
assignment(e042, cc1_1_1, hr, 20260101).
assignment(e043, cc1_1_2, finance, 20260101).
assignment(e043, cc1_2_1, finance, 20260712).
assignment(e043, cc1_1_2, hr, 20260101).
assignment(e043, cc1_2_1, hr, 20260618).
assignment(e044, cc1_1_2, finance, 20260101).
assignment(e044, cc1_1_2, hr, 20260101).
assignment(e045, cc1_1_2, finance, 20260101).
assignment(e045, cc1_1_2, hr, 20260101).
assignment(e046, cc1_1_3, finance, 20260101).
assignment(e046, cc1_1_3, hr, 20260101).
assignment(e047, cc1_1_3, finance, 20260101).
assignment(e047, cc1_1_3, hr, 20260101).
assignment(e048, cc1_1_3, finance, 20260101).
assignment(e048, cc1_1_3, hr, 20260101).
assignment(e049, cc1_2_1, finance, 20260101).
assignment(e049, cc1_2_1, hr, 20260101).
assignment(e050, cc1_2_1, finance, 20260101).
assignment(e050, cc1_2_1, hr, 20260101).
assignment(e051, cc1_2_1, finance, 20260101).
assignment(e051, cc1_2_1, hr, 20260101).
assignment(e052, cc1_2_2, finance, 20260101).
assignment(e052, cc1_2_2, hr, 20260101).
assignment(e053, cc1_2_2, finance, 20260101).
assignment(e053, cc1_2_2, hr, 20260101).
assignment(e054, cc1_2_2, finance, 20260101).
assignment(e054, cc1_2_2, hr, 20260101).
assignment(e055, cc1_2_3, finance, 20260101).
assignment(e055, cc1_2_3, hr, 20260101).
assignment(e056, cc1_2_3, finance, 20260101).
assignment(e056, cc1_2_3, hr, 20260101).
assignment(e057, cc1_2_3, finance, 20260101).
assignment(e057, cc1_2_3, hr, 20260101).
assignment(e058, cc1_3_1, finance, 20260101).
assignment(e058, cc1_3_1, hr, 20260101).
assignment(e059, cc1_3_1, finance, 20260101).
assignment(e059, cc1_3_1, hr, 20260101).
assignment(e060, cc1_3_1, finance, 20260101).
assignment(e060, cc1_3_1, hr, 20260101).
assignment(e060, cc1_1_1, hr, 20260820).
assignment(e061, cc1_3_2, finance, 20260101).
assignment(e061, cc1_3_2, hr, 20260101).
assignment(e062, cc1_3_2, finance, 20260101).
assignment(e062, cc1_3_2, hr, 20260101).
assignment(e063, cc1_3_2, finance, 20260101).
assignment(e063, cc1_3_2, hr, 20260101).
assignment(e064, cc1_3_3, finance, 20260101).
assignment(e064, cc1_3_3, hr, 20260101).
assignment(e065, cc1_3_3, finance, 20260101).
assignment(e065, cc1_3_3, hr, 20260101).
assignment(e066, cc1_3_3, finance, 20260101).
assignment(e066, cc1_3_3, hr, 20260101).
assignment(e067, cc2_1_1, finance, 20260101).
assignment(e067, cc2_1_1, hr, 20260101).
assignment(e068, cc2_1_1, finance, 20260101).
assignment(e068, cc2_1_1, hr, 20260101).
assignment(e069, cc2_1_1, finance, 20260101).
assignment(e069, cc2_1_1, hr, 20260101).
assignment(e070, cc2_1_2, finance, 20260101).
assignment(e070, cc2_1_2, hr, 20260101).
assignment(e071, cc2_1_2, finance, 20260101).
assignment(e071, cc2_1_2, hr, 20260101).
assignment(e072, cc2_1_2, finance, 20260101).
assignment(e072, cc2_1_2, hr, 20260101).
assignment(e073, cc2_1_3, finance, 20260101).
assignment(e073, cc2_1_3, hr, 20260101).
assignment(e074, cc2_1_3, finance, 20260101).
assignment(e074, cc3_1_1, finance, 20260823).
assignment(e074, cc2_1_3, hr, 20260101).
assignment(e074, cc3_1_1, hr, 20260726).
assignment(e075, cc2_1_3, finance, 20260101).
assignment(e075, cc2_1_3, hr, 20260101).
assignment(e076, cc2_2_1, finance, 20260101).
assignment(e076, cc2_2_1, hr, 20260101).
assignment(e077, cc2_2_1, finance, 20260101).
assignment(e077, cc3_1_3, finance, 20260718).
assignment(e077, cc2_2_1, hr, 20260101).
assignment(e077, cc3_1_3, hr, 20260708).
assignment(e078, cc2_2_1, finance, 20260101).
assignment(e078, cc2_2_1, hr, 20260101).
assignment(e079, cc2_2_2, finance, 20260101).
assignment(e079, cc2_2_2, hr, 20260101).
assignment(e080, cc2_2_2, finance, 20260101).
assignment(e080, cc2_2_2, hr, 20260101).
assignment(e081, cc2_2_2, finance, 20260101).
assignment(e081, cc2_2_2, hr, 20260101).
assignment(e082, cc2_2_3, finance, 20260101).
assignment(e082, cc2_2_3, hr, 20260101).
assignment(e083, cc2_2_3, finance, 20260101).
assignment(e083, cc2_2_3, hr, 20260101).
assignment(e084, cc2_2_3, finance, 20260101).
assignment(e084, cc2_2_3, hr, 20260101).
assignment(e085, cc2_3_1, finance, 20260101).
assignment(e085, cc2_3_1, hr, 20260101).
assignment(e086, cc2_3_1, finance, 20260101).
assignment(e086, cc2_3_1, hr, 20260101).
assignment(e087, cc2_3_1, finance, 20260101).
assignment(e087, cc2_3_1, hr, 20260101).
assignment(e088, cc2_3_2, finance, 20260101).
assignment(e088, cc2_3_2, hr, 20260101).
assignment(e089, cc2_3_2, finance, 20260101).
assignment(e089, cc2_3_2, hr, 20260101).
assignment(e090, cc2_3_2, finance, 20260101).
assignment(e090, cc2_3_2, hr, 20260101).
assignment(e091, cc2_3_3, finance, 20260101).
assignment(e091, cc2_3_3, hr, 20260101).
assignment(e092, cc2_3_3, finance, 20260101).
assignment(e092, cc2_3_3, hr, 20260101).
assignment(e093, cc2_3_3, finance, 20260101).
assignment(e093, cc2_3_3, hr, 20260101).
assignment(e094, cc3_1_1, finance, 20260101).
assignment(e094, cc3_1_1, hr, 20260101).
assignment(e095, cc3_1_1, finance, 20260101).
assignment(e095, cc3_1_1, hr, 20260101).
assignment(e096, cc3_1_1, finance, 20260101).
assignment(e096, cc3_1_1, hr, 20260101).
assignment(e097, cc3_1_2, finance, 20260101).
assignment(e097, cc3_1_2, hr, 20260101).
assignment(e098, cc3_1_2, finance, 20260101).
assignment(e098, cc3_1_2, hr, 20260101).
assignment(e099, cc3_1_2, finance, 20260101).
assignment(e099, cc2_1_3, finance, 20260627).
assignment(e099, cc3_1_2, hr, 20260101).
assignment(e099, cc2_1_3, hr, 20260615).
assignment(e100, cc3_1_3, finance, 20260101).
assignment(e100, cc3_1_3, hr, 20260101).
assignment(e101, cc3_1_3, finance, 20260101).
assignment(e101, cc3_1_3, hr, 20260101).
assignment(e102, cc3_1_3, finance, 20260101).
assignment(e102, cc3_1_3, hr, 20260101).
assignment(e103, cc3_2_1, finance, 20260101).
assignment(e103, cc3_2_1, hr, 20260101).
assignment(e104, cc3_2_1, finance, 20260101).
assignment(e104, cc3_2_1, hr, 20260101).
assignment(e105, cc3_2_1, finance, 20260101).
assignment(e105, cc3_2_1, hr, 20260101).
assignment(e106, cc3_2_2, finance, 20260101).
assignment(e106, cc3_2_2, hr, 20260101).
assignment(e107, cc3_2_2, finance, 20260101).
assignment(e107, cc3_2_2, hr, 20260101).
assignment(e108, cc3_2_2, finance, 20260101).
assignment(e108, cc3_2_2, hr, 20260101).
assignment(e109, cc3_2_3, finance, 20260101).
assignment(e109, cc3_2_3, hr, 20260101).
assignment(e110, cc3_2_3, finance, 20260101).
assignment(e110, cc3_1_1, finance, 20260810).
assignment(e110, cc3_2_3, hr, 20260101).
assignment(e110, cc3_1_1, hr, 20260716).
assignment(e111, cc3_2_3, finance, 20260101).
assignment(e111, cc3_2_3, hr, 20260101).
assignment(e112, cc3_3_1, finance, 20260101).
assignment(e112, cc3_3_1, hr, 20260101).
assignment(e113, cc3_3_1, finance, 20260101).
assignment(e113, cc3_3_1, hr, 20260101).
assignment(e114, cc3_3_1, finance, 20260101).
assignment(e114, cc3_3_1, hr, 20260101).
assignment(e115, cc3_3_2, finance, 20260101).
assignment(e115, cc3_3_2, hr, 20260101).
assignment(e116, cc3_3_2, finance, 20260101).
assignment(e116, cc3_3_2, hr, 20260101).
assignment(e117, cc3_3_2, finance, 20260101).
assignment(e117, cc3_3_2, hr, 20260101).
assignment(e118, cc3_3_3, finance, 20260101).
assignment(e118, cc3_3_3, hr, 20260101).
assignment(e119, cc3_3_3, finance, 20260101).
assignment(e119, cc3_3_3, hr, 20260101).
assignment(e120, cc3_3_3, finance, 20260101).
assignment(e120, cc3_3_3, hr, 20260101).

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
doc(booked_total/2, 'booked_total(C, T): T is the booked total of cost centre C.').
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
