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

% emp(Emp, Role, Cc): An employee, their role, and their current cost centre as finance records it.
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
assignment(e003, cc1_2, finance, 20260101).
assignment(e003, cc1_2, hr, 20260101).
assignment(e004, cc2, finance, 20260101).
assignment(e004, cc2, hr, 20260101).
assignment(e005, cc2_1, finance, 20260101).
assignment(e005, cc2_1, hr, 20260101).
assignment(e006, cc2_2, finance, 20260101).
assignment(e006, cc2_2, hr, 20260101).
assignment(e007, cc1_1, finance, 20260101).
assignment(e007, cc1_1, hr, 20260101).
assignment(e008, cc1_1, finance, 20260101).
assignment(e008, cc1_2, finance, 20260907).
assignment(e008, cc1_1, hr, 20260101).
assignment(e008, cc1_2, hr, 20260805).
assignment(e009, cc1_2, finance, 20260101).
assignment(e009, cc1_2, hr, 20260101).
assignment(e010, cc1_2, finance, 20260101).
assignment(e010, cc1_2, hr, 20260101).
assignment(e011, cc2_1, finance, 20260101).
assignment(e011, cc2_1, hr, 20260101).
assignment(e011, cc1_1, hr, 20260826).
assignment(e012, cc2_1, finance, 20260101).
assignment(e012, cc2_1, hr, 20260101).
assignment(e013, cc2_2, finance, 20260101).
assignment(e013, cc2_2, hr, 20260101).
assignment(e014, cc2_2, finance, 20260101).
assignment(e014, cc2_2, hr, 20260101).

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
