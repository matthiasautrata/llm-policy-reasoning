% Procurement world, layer L1: base relations, terms, definitions and decisions. Dates are integers YYYYMMDD.

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

% Terms: concept(Term, Binding, Meaning) -- what the terms used by the definitions refer to.
:- discontiguous concept/3, rule/6, doc/2, cc_anc/2, in_subtree/2, chain/2, booked_total/2, pending_total/2, committed/2, headroom/2, over_cap/1, cap_scope/2, exposure/3, cap_breach/1, big_capital/1, dept/2, headcount/2.
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
fork(c3, hr, 'department', 'Is an employee\'s department their cost centre or their cost centre\'s organisational unit?', [cost_centre, org_unit]).
fork(c4, controller, 'cap scope', 'Does a request\'s cap check cover only the requester\'s cost centre, or also every ancestor of it?', [with_ancestors, own_only]).
fork(c6, controller, 'booked total', 'Does the booked total of a cost centre include what is booked on its descendants, or only what is booked directly on it?', [with_descendants, direct_only]).
% Decisions: decided(Fork, Reading). The definitions below follow them; reading/2 is what a rule consults.
decided(c1, booked_only).
decided(c3, cost_centre).
decided(c4, with_ancestors).
decided(c6, with_descendants).
reading(c1, booked_only).
reading(c3, cost_centre).
reading(c4, with_ancestors).
reading(c6, with_descendants).

% Definitions: rule(Id, Head, Layer, Class, Conservative, Owner); doc(Head, Meaning); then the clauses.
% Owner none: no one could reasonably read the rule differently.
doc(cc_anc/2, 'cc_anc(C, A): A is an ancestor of cost centre C (parent, parent\'s parent, ...).').
doc(in_subtree/2, 'in_subtree(C, Root): C is Root or a descendant of Root.').
doc(chain/2, 'chain(E, M): M is in E\'s reporting chain (manager, manager\'s manager, ...).').
doc(booked_total/2, 'booked_total(C, T): T is the booked amount of C and all its descendants.').
doc(pending_total/2, 'pending_total(C, P): P is the amount of pending requests raised in C or its descendants.').
doc(committed/2, 'committed(C, T): T is the committed spend of cost centre C.').
doc(headroom/2, 'headroom(C, H): H is C\'s cap minus its committed spend.').
doc(over_cap/1, 'over_cap(C): C\'s committed spend exceeds its cap.').
doc(cap_scope/2, 'cap_scope(R, C): cost centre C\'s cap applies to request R.').
doc(exposure/3, 'exposure(R, C, X): X is what C would have committed if R were approved.').
doc(cap_breach/1, 'cap_breach(R): approving R would exceed the cap of a cost centre in its cap scope.').
doc(big_capital/1, 'big_capital(R): R is a capital request over 50000.').
doc(dept/2, 'dept(E, D): D is employee E\'s department.').
doc(headcount/2, 'headcount(D, N): N employees belong to department D.').
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

% R104: The booked total of a cost centre is the sum of the booked amounts of every cost centre in its subtree (zero where nothing is booked).
rule('R104', booked_total/2, 1, definitional, true, controller).
booked_total(C, T) :- cc(C), aggregate_all(sum(B), (in_subtree(D, C), booked(D, B)), T).

% R105: The pending total of a cost centre is the sum of the amounts of pending requests whose requester's cost centre lies in its subtree.
rule('R105', pending_total/2, 1, definitional, true, none).
pending_total(C, P) :- cc(C), aggregate_all(sum(A), (req(_, E, A, _, _, _, pending), emp(E, _, D), in_subtree(D, C)), P).

% R106: The committed spend of a cost centre is its booked total. Pending requests do not count.
rule('R106', committed/2, 1, definitional, true, controller).
committed(C, T) :- booked_total(C, T).

% R107: The headroom of a cost centre is its cap minus its committed spend.
rule('R107', headroom/2, 1, definitional, true, none).
headroom(C, H) :- cap(C, K), committed(C, T), H is K - T.

% R108: A cost centre is over cap if its committed spend exceeds its cap.
rule('R108', over_cap/1, 1, definitional, true, none).
over_cap(C) :- cap(C, K), committed(C, T), T > K.

% R109: A request's cap scope is its requester's cost centre and every ancestor of that cost centre.
rule('R109', cap_scope/2, 1, definitional, true, controller).
cap_scope(R, C) :- req(R, E, _, _, _, _, _), emp(E, _, C).
cap_scope(R, A) :- req(R, E, _, _, _, _, _), emp(E, _, C), cc_anc(C, A).

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

% R113: An employee's department is their cost centre.
rule('R113', dept/2, 1, definitional, true, hr).
dept(E, D) :- emp(E, _, D).

% R114: The headcount of a department is the number of employees whose department it is.
rule('R114', headcount/2, 1, definitional, true, none).
headcount(D, N) :- setof(X, E^dept(E, X), Ds), member(D, Ds), aggregate_all(count, dept(_, D), N).
