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
org_unit(cc1_1_1, support).
org_unit(cc1_1_2, delivery).
org_unit(cc1_1_3, delivery).
org_unit(cc1_2, leadership).
org_unit(cc1_2_1, support).
org_unit(cc1_2_2, delivery).
org_unit(cc1_2_3, support).
org_unit(cc1_3, leadership).
org_unit(cc1_3_1, support).
org_unit(cc1_3_2, support).
org_unit(cc1_3_3, delivery).
org_unit(cc2, leadership).
org_unit(cc2_1, leadership).
org_unit(cc2_1_1, support).
org_unit(cc2_1_2, delivery).
org_unit(cc2_1_3, delivery).
org_unit(cc2_2, leadership).
org_unit(cc2_2_1, support).
org_unit(cc2_2_2, delivery).
org_unit(cc2_2_3, support).
org_unit(cc2_3, leadership).
org_unit(cc2_3_1, support).
org_unit(cc2_3_2, delivery).
org_unit(cc2_3_3, delivery).
org_unit(cc3, leadership).
org_unit(cc3_1, leadership).
org_unit(cc3_1_1, delivery).
org_unit(cc3_1_2, support).
org_unit(cc3_1_3, support).
org_unit(cc3_2, leadership).
org_unit(cc3_2_1, support).
org_unit(cc3_2_2, support).
org_unit(cc3_2_3, delivery).
org_unit(cc3_3, leadership).
org_unit(cc3_3_1, delivery).
org_unit(cc3_3_2, delivery).
org_unit(cc3_3_3, support).

% emp(Emp, Role, Cc): An employee, their role, and their cost centre in the finance system of record.
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
emp(e043, analyst, cc1_1_2).
emp(e044, analyst, cc2_1_1).
emp(e045, analyst, cc1_1_2).
emp(e046, analyst, cc1_1_3).
emp(e047, analyst, cc1_1_3).
emp(e048, analyst, cc1_1_3).
emp(e049, analyst, cc1_2_1).
emp(e050, analyst, cc1_2_1).
emp(e051, analyst, cc1_2_1).
emp(e052, analyst, cc1_2_2).
emp(e053, analyst, cc1_2_2).
emp(e054, analyst, cc2_2_2).
emp(e055, analyst, cc1_2_3).
emp(e056, analyst, cc1_2_3).
emp(e057, analyst, cc1_2_3).
emp(e058, analyst, cc1_3_1).
emp(e059, analyst, cc1_3_1).
emp(e060, analyst, cc1_3_1).
emp(e061, analyst, cc1_3_2).
emp(e062, analyst, cc1_3_2).
emp(e063, analyst, cc1_2_3).
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
emp(e074, analyst, cc2_1_3).
emp(e075, analyst, cc2_1_3).
emp(e076, analyst, cc2_2_1).
emp(e077, analyst, cc2_2_1).
emp(e078, analyst, cc2_2_1).
emp(e079, analyst, cc2_2_2).
emp(e080, analyst, cc2_2_2).
emp(e081, analyst, cc2_2_2).
emp(e082, analyst, cc2_2_3).
emp(e083, analyst, cc2_2_3).
emp(e084, analyst, cc2_2_3).
emp(e085, analyst, cc2_3_1).
emp(e086, analyst, cc2_3_1).
emp(e087, analyst, cc2_1_1).
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
emp(e099, analyst, cc3_1_2).
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
emp(e110, analyst, cc3_2_3).
emp(e111, analyst, cc3_1_2).
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
reports(e043, e004).
reports(e044, e016).
reports(e045, e004).
reports(e046, e005).
reports(e047, e005).
reports(e048, e005).
reports(e049, e007).
reports(e050, e007).
reports(e051, e007).
reports(e052, e008).
reports(e053, e008).
reports(e054, e021).
reports(e055, e009).
reports(e056, e009).
reports(e057, e009).
reports(e058, e011).
reports(e059, e011).
reports(e060, e011).
reports(e061, e012).
reports(e062, e012).
reports(e063, e009).
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
reports(e074, e018).
reports(e075, e018).
reports(e076, e020).
reports(e077, e020).
reports(e078, e020).
reports(e079, e021).
reports(e080, e021).
reports(e081, e021).
reports(e082, e022).
reports(e083, e022).
reports(e084, e022).
reports(e085, e024).
reports(e086, e024).
reports(e087, e016).
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
reports(e099, e030).
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
reports(e110, e035).
reports(e111, e030).
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
req(r001, e040, 38000, services, acme, 20260716, pending).
req(r002, e115, 38000, services, acme, 20260714, pending).
req(r003, e114, 30000, software, edge, 20260705, pending).
req(r004, e050, 60000, hardware, acme, 20260904, cancelled).
req(r005, e055, 90000, hardware, edge, 20260623, pending).
req(r006, e046, 120000, services, dyne, 20260612, pending).
req(r007, e040, 120000, software, cog, 20260825, pending).
req(r008, e006, 45000, hardware, dyne, 20260622, pending).
req(r009, e083, 38000, hardware, acme, 20260815, pending).
req(r010, e064, 3000, hardware, acme, 20260816, pending).
req(r011, e029, 90000, hardware, fern, 20260718, pending).
req(r012, e063, 45000, hardware, bolt, 20260903, pending).
req(r013, e032, 120000, software, fern, 20260907, pending).
req(r014, e046, 38000, software, dyne, 20260706, pending).
req(r015, e052, 20000, services, edge, 20260717, pending).
req(r016, e072, 120000, services, acme, 20260709, pending).
req(r017, e038, 38000, software, dyne, 20260824, pending).
req(r018, e077, 38000, hardware, bolt, 20260708, pending).
req(r019, e070, 20000, hardware, bolt, 20260730, pending).
req(r020, e039, 12000, capital, fern, 20260914, pending).
req(r021, e100, 8000, capital, fern, 20260724, pending).
req(r022, e077, 120000, hardware, fern, 20260808, pending).
req(r023, e042, 3000, hardware, edge, 20260807, pending).
req(r024, e021, 8000, hardware, bolt, 20260708, pending).
req(r025, e105, 8000, hardware, edge, 20260725, cancelled).
req(r026, e064, 120000, capital, fern, 20260604, pending).
req(r027, e041, 45000, software, dyne, 20260907, pending).
req(r028, e093, 3000, capital, dyne, 20260806, pending).
req(r029, e011, 60000, services, dyne, 20260905, cancelled).
req(r030, e051, 45000, hardware, edge, 20260630, pending).
req(r031, e045, 20000, software, dyne, 20260822, cancelled).
req(r032, e065, 90000, services, dyne, 20260605, pending).
req(r033, e018, 45000, services, acme, 20260814, pending).
req(r034, e088, 12000, services, dyne, 20260622, cancelled).
req(r035, e093, 12000, software, cog, 20260712, pending).
req(r036, e045, 30000, software, fern, 20260731, pending).
req(r037, e079, 120000, capital, fern, 20260629, pending).
req(r038, e022, 12000, capital, bolt, 20260819, pending).
req(r039, e060, 12000, software, cog, 20260703, pending).
req(r040, e047, 12000, software, edge, 20260905, pending).
req(r041, e086, 8000, services, cog, 20260606, pending).
req(r042, e069, 12000, hardware, cog, 20260818, pending).
req(r043, e001, 12000, capital, bolt, 20260910, pending).
req(r044, e048, 20000, capital, bolt, 20260906, pending).
req(r045, e019, 3000, services, dyne, 20260906, pending).
req(r046, e066, 20000, hardware, fern, 20260815, pending).
req(r047, e052, 30000, capital, bolt, 20260715, pending).
req(r048, e021, 12000, hardware, bolt, 20260914, pending).
req(r049, e119, 90000, capital, fern, 20260912, pending).
req(r050, e045, 90000, hardware, edge, 20260829, pending).
req(r051, e013, 45000, hardware, acme, 20260704, pending).
req(r052, e097, 12000, software, bolt, 20260904, pending).
req(r053, e025, 30000, hardware, acme, 20260708, cancelled).
req(r054, e119, 12000, software, bolt, 20260831, cancelled).
req(r055, e071, 45000, services, cog, 20260815, pending).
req(r056, e104, 45000, capital, dyne, 20260627, pending).
req(r057, e117, 120000, services, dyne, 20260610, pending).
req(r058, e013, 60000, software, cog, 20260625, pending).
req(r059, e051, 120000, hardware, bolt, 20260827, pending).
req(r060, e027, 90000, hardware, fern, 20260627, pending).
req(r061, e097, 20000, services, cog, 20260603, pending).
req(r062, e115, 8000, software, acme, 20260604, pending).
req(r063, e044, 3000, software, fern, 20260624, pending).
req(r064, e055, 90000, capital, fern, 20260913, cancelled).
req(r065, e070, 60000, services, cog, 20260829, pending).
req(r066, e048, 90000, hardware, edge, 20260808, pending).
req(r067, e110, 90000, capital, cog, 20260827, pending).
req(r068, e120, 90000, capital, dyne, 20260715, pending).
req(r069, e117, 20000, hardware, edge, 20260716, pending).
req(r070, e020, 20000, software, bolt, 20260817, pending).
req(r071, e065, 12000, services, acme, 20260716, pending).
req(r072, e107, 12000, software, cog, 20260813, pending).
req(r073, e106, 30000, services, edge, 20260730, pending).
req(r074, e106, 30000, hardware, edge, 20260807, cancelled).
req(r075, e119, 30000, services, bolt, 20260801, pending).
req(r076, e099, 120000, services, fern, 20260905, pending).
req(r077, e105, 60000, software, dyne, 20260602, pending).
req(r078, e045, 12000, services, cog, 20260611, pending).
req(r079, e011, 20000, hardware, acme, 20260607, pending).
req(r080, e053, 60000, capital, cog, 20260618, pending).
req(r081, e012, 120000, services, fern, 20260822, pending).
req(r082, e013, 30000, hardware, bolt, 20260706, pending).
req(r083, e095, 20000, services, bolt, 20260716, pending).
req(r084, e031, 8000, software, fern, 20260715, pending).
req(r085, e061, 90000, services, dyne, 20260719, pending).
req(r086, e116, 38000, software, dyne, 20260726, pending).
req(r087, e056, 60000, hardware, dyne, 20260613, pending).
req(r088, e030, 30000, hardware, cog, 20260913, pending).
req(r089, e019, 60000, capital, acme, 20260629, pending).
req(r090, e096, 3000, software, cog, 20260915, pending).
req(r091, e087, 20000, services, acme, 20260707, pending).
req(r092, e033, 38000, services, dyne, 20260709, pending).
req(r093, e114, 60000, software, edge, 20260725, pending).
req(r094, e077, 60000, software, bolt, 20260810, pending).
req(r095, e089, 30000, software, fern, 20260605, pending).
req(r096, e078, 90000, hardware, dyne, 20260818, pending).
req(r097, e093, 20000, services, acme, 20260911, pending).
req(r098, e082, 20000, services, fern, 20260711, pending).
req(r099, e026, 3000, hardware, fern, 20260816, pending).
req(r100, e050, 12000, hardware, cog, 20260818, pending).
req(r101, e084, 12000, hardware, fern, 20260901, pending).
req(r102, e057, 20000, capital, cog, 20260904, pending).

% emergency(Req): A request flagged as an emergency.
:- dynamic emergency/1.
emergency(r006).
emergency(r010).
emergency(r011).
emergency(r016).
emergency(r020).
emergency(r026).
emergency(r030).
emergency(r036).
emergency(r037).
emergency(r044).
emergency(r048).
emergency(r049).
emergency(r060).
emergency(r061).
emergency(r063).
emergency(r066).
emergency(r067).
emergency(r068).
emergency(r075).
emergency(r084).
emergency(r085).
emergency(r087).
emergency(r093).
emergency(r097).
emergency(r098).
emergency(r101).

% violation(Emp): An employee with a recorded policy violation.
:- dynamic violation/1.
violation(e013).
violation(e014).
violation(e047).
violation(e063).
violation(e076).
violation(e081).
violation(e088).
violation(e101).
violation(e107).
violation(e113).
violation(e115).
violation(e118).

% booked(Cc, Amount): Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
:- dynamic booked/2.
booked(cc1_1_1, 100000).
booked(cc1_1_2, 139000).
booked(cc1_1_3, 47000).
booked(cc1_2_1, 105000).
booked(cc1_2_2, 45000).
booked(cc1_2_3, 119000).
booked(cc1_3_1, 125000).
booked(cc1_3_2, 44000).
booked(cc1_3_3, 98000).
booked(cc2_1_1, 120000).
booked(cc2_1_2, 125000).
booked(cc2_1_3, 46000).
booked(cc2_2_1, 54000).
booked(cc2_2_2, 68000).
booked(cc2_2_3, 111000).
booked(cc2_3_1, 124000).
booked(cc2_3_2, 76000).
booked(cc2_3_3, 99000).
booked(cc3_1_1, 67000).
booked(cc3_1_2, 71000).
booked(cc3_1_3, 87000).
booked(cc3_2_1, 42000).
booked(cc3_2_2, 106000).
booked(cc3_2_3, 63000).
booked(cc3_3_1, 91000).
booked(cc3_3_2, 95000).
booked(cc3_3_3, 119000).
booked(cc2_3, 38000).
booked(cc3_2, 22000).

% cap(Cc, Amount): The spending cap of a cost centre this quarter.
:- dynamic cap/2.
cap(company, 2935000).
cap(cc1, 863000).
cap(cc1_1, 429000).
cap(cc1_1_1, 97000).
cap(cc1_1_2, 166000).
cap(cc1_1_3, 45000).
cap(cc1_2, 309000).
cap(cc1_2_1, 147000).
cap(cc1_2_2, 62000).
cap(cc1_2_3, 166000).
cap(cc1_3, 307000).
cap(cc1_3_1, 128000).
cap(cc1_3_2, 70000).
cap(cc1_3_3, 100000).
cap(cc2, 1291000).
cap(cc2_1, 436000).
cap(cc2_1_1, 168000).
cap(cc2_1_2, 128000).
cap(cc2_1_3, 64000).
cap(cc2_2, 302000).
cap(cc2_2_1, 52000).
cap(cc2_2_2, 65000).
cap(cc2_2_3, 177000).
cap(cc2_3, 505000).
cap(cc2_3_1, 198000).
cap(cc2_3_2, 78000).
cap(cc2_3_3, 101000).
cap(cc3, 1144000).
cap(cc3_1, 292000).
cap(cc3_1_1, 69000).
cap(cc3_1_2, 113000).
cap(cc3_1_3, 84000).
cap(cc3_2, 302000).
cap(cc3_2_1, 43000).
cap(cc3_2_2, 109000).
cap(cc3_2_3, 88000).
cap(cc3_3, 396000).
cap(cc3_3_1, 127000).
cap(cc3_3_2, 114000).
cap(cc3_3_3, 122000).
