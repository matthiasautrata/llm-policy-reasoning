/*  V3a evaluator: defeasible logic (Nute / Governatori style) over EDN rules and Toulmin claims.

    Store (dynamic, asserted from slice.edn / extension.edn / add / with_hypothesis):
      rule(Id, Kind, Head, Body, Meta)        Kind: strict | defeasible | defeater | superiority | incompatible
      claim(Id, Assertion, By, At, From, To, About, Parent, Role, Meta)   sub-claims: Parent \== null
      functional(Pred, KeyArity)  concept(Name, Map)  term(Id, Map)  today(Date)  withheld(Id)

    Literals are lists [Pred|Args]; [neg, L] is the complement. evaluate/3 decides a ground literal:
      proven(Sups, SupNodes)   every applicable attacker is beaten by some applicable supporter (team defeat)
      defeated(A, Sups, SupNodes)  an unbeaten attacker A is superior to every supporter
      blocked(Sups, Unbeaten)  ambiguity blocking: attackers unbeaten, none superior to all supporters
      none(Atts)               no applicable supporter
    Supporters: active strict/defeasible rules whose body is provable, in-force claims. Attackers: the same
    for the complement and, for functional predicates, for the same key with another value; defeaters
    attack only. Superiority: explicit :superior-to, strict over non-strict, asserter authority (a
    :superiority rule, scoped to its :pred), later asserted_at for the same asserter.
    Memoised per op (memo/3), cleared whenever the rule/claim set changes.
*/
:- module(defeasible, [load_file/1, add_records/3, retract_source/1, evaluate/3, prove/3, body/3, lit/3,
                       supporters/3, attackers/3, sup/3, in_force/3, active/1, clear_memo/0, pred_of/2,
                       fetch_rows/5, cmp_lit/1, ev/2, ids_of/2,
                       rule/5, claim/10, functional/2, concept/2, term/2, today/1, withheld/1, slice/1, asset/2, src/2]).
:- use_module(edn).
:- use_module(library(janus)).
:- use_module(library(json)).

:- dynamic rule/5, claim/10, functional/2, concept/2, term/2, today/1, withheld/1, memo/3, slice/1, asset/2, src/2.

% ------------------------------------------------------------------ loading

load_file(File) :-
    edn_read_file(File, T),
    (   T = map(_) -> load_slice(T)
    ;   is_list(T) -> add_records(T, ext, _) ).

load_slice(M) :-
    assertz(slice(M)),
    mget(today, M, D), assertz(today(D)),
    mget(functional, M, map(Fs)), forall(member(P-N, Fs), assertz(functional(P, N))),
    mget(concepts, M, Cs),
    forall(member(C, Cs), ( mget(name, C, N), assertz(concept(N, C)),
                            (   mget(sql, C, Sql) -> mget(params, C, Ps, []),
                                py_call(sql:register(N, Sql, Ps), _)
                            ;   true ) )),
    mget(terms, M, Ts), forall(member(T, Ts), ( mget(id, T, Id), assertz(term(Id, T)) )),
    mget(assets, M, As, []), forall(member(A, As), ( mget(id, A, Id), assertz(asset(Id, A)) )),
    mget(rules, M, Rs), mget(claims, M, Cl),
    append(Rs, Cl, Recs), add_records(Recs, base, _).

%!  add_records(+Maps, +Source, -Ids)
add_records(Recs, Src, Ids) :-
    foldl(add_record(Src), Recs, [], Ids0), reverse(Ids0, Ids), clear_memo.

add_record(Src, M, Ids0, [Id|Ids0]) :-
    mget(id, M, Id),
    (   mget(assertion, M, _) -> add_claim(M, null, Src)
    ;   edn_vars(M, MV), mget(kind, MV, K), mget(head, MV, H, none), mget(body, MV, B, []),
        assertz(rule(Id, K, H, B, MV)), assertz(src(Id, Src)) ).

add_claim(M, Parent, Src) :-
    mget(id, M, Id), mget(assertion, M, A), mget(asserted_by, M, By), mget(asserted_at, M, At),
    mget(valid_from, M, F), mget(valid_to, M, T, null), mget(role, M, Role, null),
    (   Parent == null -> mget(about, M, About) ; claim(Parent, _, _, _, _, _, About, _, _, _) ),
    assertz(claim(Id, A, By, At, F, T, About, Parent, Role, M)), assertz(src(Id, Src)),
    mget(subclaims, M, Subs, []),
    forall(member(S, Subs), add_claim(S, Id, Src)).

retract_source(Src) :-
    forall(src(Id, Src), ( retractall(rule(Id, _, _, _, _)), retractall(claim(Id, _, _, _, _, _, _, _, _, _)) )),
    retractall(src(_, Src)), clear_memo.

clear_memo :- retractall(memo(_, _, _)).

active(Id) :- \+ withheld(Id).

% ------------------------------------------------------------------ evaluation

%!  prove(?L, +AsOf, -Proof) is nondet.   L defeasibly provable (+∂); binds L to each proven instance.
prove(L, D, P) :- ground(L), !,
    evaluate(L, D, proven(Sups, SupN)), Sups = [s(_, _, P0)|_], with_children(P0, SupN, P).
prove(L, D, P) :-
    findall(L, candidate(L, D), Ls0), sort(Ls0, Ls),
    member(L, Ls), ground(L),
    evaluate(L, D, proven(Sups, SupN)), Sups = [s(_, _, P0)|_], with_children(P0, SupN, P).

candidate(L, D) :-
    (   rule(Id, K, L, B, _), memberchk(K, [strict, defeasible]), active(Id), body(B, D, _)
    ;   claim(Id, L, _, _, F, T, _, _, _, _), active(Id), in_force(F, T, D) ).

with_children(P0, Extra, P) :- get_dict(children, P0, Cs0), append(Cs0, Extra, Cs), put_dict(children, P0, Cs, P).

evaluate(L, D, R) :- memo(D, L, R0), !, R = R0.
evaluate(L, D, R) :-
    supporters(L, D, Sups), attackers(L, D, Atts),
    classify(Sups, Atts, R0),          % R0 fresh: callers pass patterns like proven(_, _)
    assertz(memo(D, L, R0)), R = R0.

%!  supporters(+L, +D, -Sups)  [s(Id, Kind, Proof)]: one proof per applicable rule / in-force claim
supporters(L, D, Sups) :-
    findall(s(Id, K, P),
            (   rule(Id, K, L0, _, _), memberchk(K, [strict, defeasible]), active(Id), L0 = L,
                once(apply_rule(Id, L, D, P))
            ;   claim(Id, L, By, At, F, T, _, _, _, _), active(Id), in_force(F, T, D),
                K = claim, P = _{type:claim, id:Id, goal:L, asserted_by:By, asserted_at:At, children:[]} ),
            Sups).

apply_rule(Id, L, D, _{type:rule, id:Id, goal:L, children:Kids}) :-
    rule(Id, _, L, B, _), body(B, D, Kids).

%!  attackers(+L, +D, -Atts)  [a(Id, Kind, Head, Proof)]
attackers(L, D, Atts) :-
    findall(a(Id, K, H, P), ( rival(L, H, Diff), attacker(H, Diff, D, Id, K, P) ), Atts0),
    dedup_ids(Atts0, Atts).

rival([neg, X], X, true) :- !.
rival(L, [neg, L], true).
rival([P|Args], [P|Rival], diff(V, V2)) :-
    functional(P, N), length(Args, Len), Len =:= N + 1,
    length(Key, N), append(Key, [V], Args), append(Key, [V2], Rival).

attacker(H, Diff, D, Id, K, P) :-
    rule(Id, K, H0, _, _), memberchk(K, [strict, defeasible, defeater]), active(Id), copy_term(H-Diff, H1-Diff1),
    H0 = H1,
    once(( apply_rule(Id, H1, D, P), differs(Diff1) )).
attacker(H, Diff, D, Id, claim, P) :-
    copy_term(H-Diff, H1-Diff1),
    claim(Id, H1, By, At, F, T, _, _, _, _), active(Id), in_force(F, T, D), differs(Diff1),
    P = _{type:claim, id:Id, goal:H1, asserted_by:By, asserted_at:At, children:[]}.

differs(true).
differs(diff(V, V2)) :- V \== V2.

dedup_ids([], []).
dedup_ids([A|As], [A|Bs]) :- arg(1, A, Id), exclude([X]>>arg(1, X, Id), As, Rest), dedup_ids(Rest, Bs).

classify([], Atts, none(Atts)) :- !.
classify(Sups, Atts, R) :-
    partition([A]>>( arg(1, A, AId), member(s(SId, _, _), Sups), sup(SId, AId, _) ), Atts, Beaten, Unbeaten),
    findall(_{type:superior, winner:SId, loser:AId, source:Src},
            ( member(A, Beaten), arg(1, A, AId), once(( member(s(SId, _, _), Sups), sup(SId, AId, Src) )) ),
            SupN),
    (   Unbeaten == [] -> R = proven(Sups, SupN)
    ;   member(A, Unbeaten), arg(1, A, AId), forall(member(s(SId, _, _), Sups), sup(AId, SId, _)) ->
        findall(_{type:superior, winner:AId, loser:SId, source:Src},
                ( member(s(SId, _, _), Sups), once(sup(AId, SId, Src)) ), DN),
        R = defeated(A, Sups, DN)
    ;   R = blocked(Sups, Unbeaten) ).

%!  sup(+Winner, +Loser, -Source) is nondet.
sup(W, L, explicit) :- rule(W, _, _, _, M), mget('superior-to', M, Ls), memberchk(L, Ls).
sup(W, L, strict) :- rule(W, strict, _, _, _), \+ rule(L, strict, _, _, _).
sup(W, L, Src) :-
    claim(W, AW, ByW, _, _, _, _, _, _, _), claim(L, AL, ByL, _, _, _, _, _, _, _), ByW \== ByL,
    pred_of(AW, P), pred_of(AL, P),
    rule(SId, superiority, _, _, M), active(SId), mget(pred, M, P), mget(order, M, O),
    nth0(IW, O, ByW), nth0(IL, O, ByL), IW < IL,
    format(atom(Src), 'authority:~w', [SId]).
sup(W, L, later) :-
    claim(W, _, By, AtW, _, _, _, _, _, _), claim(L, _, By, AtL, _, _, _, _, _, _), AtW @> AtL.

pred_of([neg, X], P) :- !, pred_of(X, P).
pred_of([P|_], P).

in_force(F, T, D) :- F @=< D, ( T == null -> true ; D @=< T ).

% ------------------------------------------------------------------ rule bodies

body([], _, []).
body([L|Ls], D, [K|Ks]) :- lit(L, D, K), body(Ls, D, Ks).

lit([fetch, C, map(F), map(O)], _, Node) :- !,
    fetch_rows(C, F, Rows, Info, Filters),
    length(Rows, N),
    member(Row, Rows),
    maplist([Col-V]>>get_dict(Col, Row, V), O),
    Node = Info.put(_{type:fetch, concept:C, filters:Filters, rows:N, row:Row}).
lit([not, L], D, _{type:absent, goal:L}) :- !, \+ prove(L, D, _).
lit([as_of, X], D, _{type:fact, goal:[as_of, D]}) :- !, X = D.
lit([is, X, E], _, _{type:fact, goal:[is, V, E1]}) :- !, ev(E, V), X = V, inst(E, E1).
lit([Op, A, B], _, _{type:fact, goal:[Op, A1, B1]}) :- cmp_op(Op), !, inst(A, A1), inst(B, B1), cmp_lit([Op, A1, B1]).
lit(L, D, P) :- prove(L, D, P).

cmp_op(Op) :- memberchk(Op, [<, <=, >, >=, =]).
inst(X, X).   % arguments are bound by the time a builtin runs (left-to-right bodies)

cmp_lit([Op, A, B]) :-
    ev(A, X), ev(B, Y),
    (   number(X), number(Y) -> num_cmp(Op, X, Y)
    ;   compare(O, X, Y), ord_ok(Op, O) ).
num_cmp(<, X, Y) :- X < Y.   num_cmp(<=, X, Y) :- X =< Y.  num_cmp(>, X, Y) :- X > Y.
num_cmp(>=, X, Y) :- X >= Y. num_cmp(=, X, Y) :- X =:= Y.
ord_ok(<, <). ord_ok(<=, <). ord_ok(<=, =). ord_ok(>, >). ord_ok(>=, >). ord_ok(>=, =). ord_ok(=, =).

ev(X, X) :- ( number(X) ; string(X) ; atom(X) ), !.
ev([+, A, B], V) :- !, ev(A, X), ev(B, Y), V is X + Y.
ev([-, A, B], V) :- !, ev(A, X), ev(B, Y), V is X - Y.

%!  fetch_rows(+Concept, +FilterPairs, -Rows, -Info, -FilterDict)
%   Calls the SQL boundary (sql.py) with ground filters; Info carries sql and params for the why tree.
fetch_rows(C, F, Rows, _{sql:Sql, params:Ps, truncated:Tr}, FD) :-
    (   forall(member(_-V, F), ground(V)) -> true
    ;   throw(error(fetch_unbound(C, F), _)) ),
    dict_pairs(FD, _, F),
    with_output_to(string(J), json_write_dict(current_output, FD, [width(0)])),
    py_call(sql:fetch(C, J), Out),
    atom_json_dict(Out, R, [value_string_as(string)]),
    Rows = R.rows, Sql = R.sql, Ps = R.params, Tr = R.truncated.

ids_of(Xs, Ids) :- maplist([X, Id]>>arg(1, X, Id), Xs, Ids0), sort(Ids0, Ids).
