/*  core.pl -- the v2 engine.

    Reads world/schema.yaml (base relations) and rules/rules.yaml (rule records) at runtime,
    reads a world's facts.pl, and builds one program per (layer, fork readings) into a fresh
    module: base facts of layer =< L, schema facts of layer =< L, reading/2 facts, and the
    clauses of rules of layer =< L whose fork reading (if any) is the chosen one.
    Only relations and derived predicates of layer =< L are declared (dynamic, or tabled for
    records with table: true), so calling a predicate of a higher layer is an existence error,
    not a silent failure: a model asking at L0 for headroom/2 learns it is not defined there.
    Negation is \+ : the rule base is stratified (checked by the M1 tests, not assumed).
    Exclusions (M6): a rule with head excluded/1 states that an atom must not hold. program_x/3 builds
    the exclusion-enforced program: every predicate P that an excluded/1 clause of layer =< L names
    gets its clauses under a raw name and the wrapper P(Xs) :- raw(Xs), \+ excluded(P(Xs)). Where the
    plain program and the enforced one give different values, the rule base derives both G and
    excluded(G): it contradicts itself, and the keys (and compile mode) report CONFLICT with both values.
*/
:- module(core, [ load_meta/1, load_world/1, program/3, program_for/3, program_x/3,
                  excl_target/2, excl_relevant/2, contradicted/3,
                  rule_rec/9, fork_rec/4, rel_rec/5, rel_doc_from/3, rel_layer/2, pred_layer/2, pred_doc/3,
                  goal_preds/2, closure/2, goal_meta/3, decided_readings/1, all_fork_ids/1,
                  unknown_call/1, stratified/1, known/1, schema_pred/1, meta_root/1 ]).
:- use_module(library(yaml)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(occurs)).

:- dynamic rule_rec/9, fork_rec/4, rel_rec/5, rel_doc_from/3, doc_rec/2, wfact/1, prog_cache/3, meta_root/1.

%% load_meta(+Root) -- read schema.yaml and rules.yaml under the repository root.
load_meta(Root) :-
    retractall(rule_rec(_,_,_,_,_,_,_,_,_)), retractall(fork_rec(_,_,_,_)),
    retractall(rel_rec(_,_,_,_,_)), retractall(rel_doc_from(_,_,_)), retractall(doc_rec(_,_)), retractall(meta_root(_)),
    assertz(meta_root(Root)),
    directory_file_path(Root, 'world/schema.yaml', SF), yaml_read(SF, S),
    forall(member(R, S.relations), add_rel(R)),
    directory_file_path(Root, 'rules/rules.yaml', RF), yaml_read(RF, Y),
    forall(member(F, Y.forks), ( atom_string(I, F.id), atom_string(D, F.decided), maplist(atom_string, Rs, F.readings),
                                 assertz(fork_rec(I, F.layer, D, Rs)) )),
    dict_pairs(Y.docs, _, DocPairs),
    forall(member(K-V, DocPairs), (term_string(PI, K), assertz(doc_rec(PI, V)))),
    forall(member(R, Y.rules), add_rule(R)).

add_rel(R) :-
    atom_string(Name, R.name),
    maplist([[C,T], C2-T2]>>(atom_string(C2, C), atom_string(T2, T)), R.columns, Cols),
    ( get_dict(fks, R, Fk) -> dict_pairs(Fk, _, FkPairs0),
        maplist([C-T, C-T2]>>atom_string(T2, T), FkPairs0, FkPairs) ; FkPairs = [] ),
    assertz(rel_rec(Name, R.layer, Cols, FkPairs, R.doc)),
    ( get_dict(doc_from, R, DF) -> dict_pairs(DF, _, DFs),
        forall(member(K-D, DFs), ( ( integer(K) -> KL = K ; atom_number(K, KL) ), assertz(rel_doc_from(Name, KL, D)) )) ; true ).

add_rule(R) :-
    atom_string(Id, R.id), term_string(Head, R.head),
    ( get_dict(fork, R, F), F \== null -> atom_string(FI, F.id), atom_string(FR, F.reading), Fork = FI-FR
    ; Fork = none ),
    ( get_dict(table, R, true) -> Tab = true ; Tab = false ),
    ( R.owner == null -> Owner = none ; atom_string(Owner, R.owner) ),
    read_clauses(R.prolog, Clauses),
    atom_string(Class, R.class),
    assertz(rule_rec(Id, Head, R.layer, Class, R.conservative, Owner, Fork, Tab, Clauses)).

read_clauses(Text, Clauses) :-
    setup_call_cleanup(open_string(Text, S), read_all(S, Clauses), close(S)).
read_all(S, Cs) :-
    read_term(S, T, []),
    ( T == end_of_file -> Cs = [] ; Cs = [T|Rest], read_all(S, Rest) ).

rel_layer(Name/Ar, L) :- rel_rec(Name, L, Cols, _, _), length(Cols, Ar).
rel_layer(SchemaPI, 0) :- schema_pred(SchemaPI).
schema_pred(relation/1). schema_pred(column/4). schema_pred(fk/3). schema_pred(key/2).

%% pred_layer(?PI, ?Layer): layer of a base relation or derived predicate (min over its rules).
pred_layer(PI, L) :- rel_layer(PI, L).
pred_layer(PI, L) :- \+ rel_layer(PI, _), setof(L0, A^B^C^D^E^F^G^rule_rec(A, PI, L0, B, C, D, E, F, G), [L|_]).

pred_doc(PI, L, Doc) :- rel_rec(N, L, Cols, _, Doc), length(Cols, Ar), PI = N/Ar.
pred_doc(PI, L, Doc) :- doc_rec(PI, Doc), pred_layer(PI, L).

derived(PI) :- rule_rec(_, PI, _, _, _, _, _, _, _), !.
known(PI) :- ( rel_layer(PI, _) ; derived(PI) ; PI == reading/2 ), !.

all_fork_ids(Ids) :- findall(I, fork_rec(I, _, _, _), Ids).
decided_readings(Rs) :- findall(I-D, fork_rec(I, _, D, _), Rs).

%% load_world(+Dir) -- read Dir/facts.pl (the formal projection of all base relations).
load_world(Dir) :-
    retractall(wfact(_)), retractall(prog_cache(_,_,_)),
    directory_file_path(Dir, 'facts.pl', F),
    setup_call_cleanup(open(F, read, S), read_facts(S), close(S)).
read_facts(S) :-
    read_term(S, T, []),
    ( T == end_of_file -> true
    ; ( T = (:- _) -> true ; assertz(wfact(T)) ), read_facts(S) ).

%% program(+Layer, +Readings, -Module): the program for Layer under Readings (Fork-Reading pairs,
%% one per fork; missing forks take their decided reading). Cached per world.
program(Layer, Readings0, M) :-
    decided_readings(Dec),
    findall(I-R, (member(I-D, Dec), ( memberchk(I-R0, Readings0) -> R = R0 ; R = D )), Readings),
    ( prog_cache(Layer, Readings, M) -> true
    ; gensym(prog_, M), build(Layer, Readings, M), assertz(prog_cache(Layer, Readings, M)) ).

program_for(Layer, Readings, M) :- program(Layer, Readings, M).

%% program_x(+Layer, +Readings, -Module): the exclusion-enforced program (see the header). With no
%% exclusion at layer =< Layer it is the plain program itself.
program_x(Layer, Readings0, M) :-
    (   \+ excl_target(_, Layer) -> program(Layer, Readings0, M)
    ;   decided_readings(Dec),
        findall(I-R, (member(I-D, Dec), ( memberchk(I-R0, Readings0) -> R = R0 ; R = D )), Readings),
        (   prog_cache(x(Layer), Readings, M) -> true
        ;   gensym(progx_, M), build(Layer, Readings, M, enforce), assertz(prog_cache(x(Layer), Readings, M)) ) ).

%% excl_target(?PI, +Layer): an excluded/1 clause of a rule of layer =< Layer names an atom of PI.
excl_target(PI, Layer) :-
    rule_rec(_, excluded/1, L, _, _, _, _, _, Cs), L =< Layer, member(C, Cs),
    ( C = (H :- _) -> true ; H = C ), H = excluded(T), callable(T), functor(T, N, A), PI = N/A.

%% excl_relevant(+Layer, +Goals): the dependency closure of Goals contains a predicate an exclusion
%% of layer =< Layer names, so the plain and the enforced program may differ on Goals.
excl_relevant(Layer, Goals) :-
    foldl([G, A0, A]>>(goal_preds(G, P), append(A0, P, A)), Goals, [], P0),
    closure(P0, Cl), member(PI, Cl), excl_target(PI, Layer), !.

%% contradicted(+Module, +Layer, -Atoms): the atoms G the plain program derives together with excluded(G).
contradicted(M, Layer, Atoms) :-
    findall(G, ( excl_target(N/A, Layer), functor(G, N, A), M:excluded(G), once(M:G) ), As0), sort(As0, Atoms).

raw_name(N, R) :- atom_concat(N, '$raw', R).

build(Layer, Readings, M) :- build(Layer, Readings, M, plain).
build(Layer, Readings, M, Mode) :-
    (   Mode == enforce -> findall(PI, excl_target(PI, Layer), X0), sort(X0, Xs) ; Xs = [] ),
    findall(R/A, ( member(N/A, Xs), raw_name(N, R) ), Raws),
    findall(N/A, (rel_rec(N, L, Cols, _, _), L =< Layer, length(Cols, A)), Rels),
    findall(PI, (rule_rec(_, PI, _, _, _, _, _, _, _), pred_layer(PI, L), L =< Layer), Ds0), sort(Ds0, Ds),
    findall(PI, schema_pred(PI), Sch),
    append([Rels, Ds, Sch, [reading/2], Raws], Dyn0), sort(Dyn0, Dyn),
    findall(PI, (rule_rec(_, PI, L, _, _, _, _, true, _), L =< Layer), Tab1),
    findall(R/A, ( member(N/A, Tab1), memberchk(N/A, Xs), raw_name(N, R) ), Tab2),
    append(Tab1, Tab2, Tab0), sort(Tab0, Tab),
    subtract(Dyn, Tab, DynOnly),
    with_output_to(string(Text), (
        forall(member(PI, DynOnly), format(":- dynamic ~q.~n", [PI])),
        forall(member(PI, Tab), format(":- table ~q.~n", [PI])),
        forall(( member(PI, Ds) ; member(PI, Raws) ), format(":- discontiguous ~q.~n", [PI])),
        forall(( wfact(T), functor(T, N, A), rel_layer(N/A, L), L =< Layer ), format("~q.~n", [T])),
        forall(schema_fact(Layer, T), format("~q.~n", [T])),
        forall(member(I-R, Readings), format("~q.~n", [reading(I, R)])),
        forall(( rule_rec(_, _, L, _, _, _, Fork, _, Cs), L =< Layer,
                 ( Fork == none -> true ; memberchk(Fork, Readings) ),
                 member(C0, Cs), rename_head(Xs, C0, C) ),
               portray_clause(C)),
        forall(( member(N/A, Xs), raw_name(N, R), length(Args, A), W =.. [N|Args], Raw =.. [R|Args] ),
               portray_clause((W :- Raw, \+ excluded(W)))) )),
    setup_call_cleanup(open_string(Text, S), load_files(M:M, [stream(S), silent(true)]), close(S)).

rename_head([], C, C) :- !.
rename_head(Xs, (H :- B), (H1 :- B)) :- !, rename_atom(Xs, H, H1).
rename_head(Xs, H, H1) :- rename_atom(Xs, H, H1).
rename_atom(Xs, H, H1) :-
    functor(H, N, A), ( memberchk(N/A, Xs) -> raw_name(N, R), H =.. [N|Args], H1 =.. [R|Args] ; H1 = H ).

schema_fact(Layer, relation(N)) :- rel_rec(N, L, _, _, _), L =< Layer.
schema_fact(Layer, column(N, C, P, T)) :- rel_rec(N, L, Cols, _, _), L =< Layer, nth1(P, Cols, C-T).
schema_fact(Layer, fk(N, C, Ref)) :- rel_rec(N, L, _, Fks, _), L =< Layer, member(C-Ref, Fks).
schema_fact(Layer, key(N, C)) :- rel_rec(N, L, Cols, _, _), L =< Layer, Cols = [C-_|_].

%% goal_preds(+Goal, -PIs): user predicates (relations, derived, reading/2) called by Goal.
goal_preds(G, PIs) :- phrase(calls(G), PIs0), sort(PIs0, PIs).

calls(V) --> { var(V) }, !.
calls((A, B)) --> !, calls(A), calls(B).
calls((A ; B)) --> !, calls(A), calls(B).
calls((A -> B)) --> !, calls(A), calls(B).
calls(\+ A) --> !, calls(A).
calls(_^A) --> !, calls(A).
calls(once(A)) --> !, calls(A).
calls(forall(A, B)) --> !, calls(A), calls(B).
calls(aggregate_all(_, A, _)) --> !, calls(A).
calls(findall(_, A, _)) --> !, calls(A).
calls(setof(_, A, _)) --> !, calls(A).
calls(bagof(_, A, _)) --> !, calls(A).
calls(G) --> { callable(G), functor(G, N, A), known(N/A) }, !, [N/A].
calls(_) --> [].

%% closure(+PIs, -Closure): PIs plus every predicate their rules call, transitively.
closure(PIs, Cl) :- closure_(PIs, [], Cl0), sort(Cl0, Cl).
closure_([], Acc, Acc).
closure_([P|Ps], Acc, Cl) :-
    ( memberchk(P, Acc) -> closure_(Ps, Acc, Cl)
    ; findall(Q, ( rule_rec(_, P, _, _, _, _, _, _, Cs), member(C, Cs), body(C, B), goal_preds(B, Qs), member(Q, Qs) ), New),
      append(New, Ps, Ps2), closure_(Ps2, [P|Acc], Cl) ).
body((_ :- B), B) :- !.
body(_, true).

%% goal_meta(+Goals, -MinLayer, -Forks): MinLayer = highest layer in the closure of Goals;
%% Forks = forks whose readings any rule in the closure belongs to, or that reading/2 names.
goal_meta(Goals, MinLayer, Forks) :-
    foldl([G, A0, A]>>(goal_preds(G, P), append(A0, P, A)), Goals, [], P0),
    closure(P0, Cl),
    findall(L, ( member(PI, Cl), PI \== reading/2, pred_layer(PI, L) ), Ls), max_list([0|Ls], MinLayer),
    findall(F, ( member(PI, Cl), rule_rec(_, PI, _, _, _, _, F-_, _, _) ), F1),
    findall(F, ( member(PI, Cl), rule_rec(_, PI, _, _, _, _, _, _, Cs), member(C, Cs), body(C, B),
                 sub_term(T, B), compound(T), T = reading(F0, _), atom(F0), F = F0 ), F2),
    append(F1, F2, F3), sort(F3, Forks).

%% unknown_call(+Goal): Goal calls something that is neither a relation, a derived predicate,
%% reading/2, nor a built-in -- the question is out of scope of every layer.
unknown_call(G) :- leaf(G, L), \+ known_or_builtin(L).
leaf(V, _) :- var(V), !, fail.
leaf((A, B), L) :- !, ( leaf(A, L) ; leaf(B, L) ).
leaf((A ; B), L) :- !, ( leaf(A, L) ; leaf(B, L) ).
leaf((A -> B), L) :- !, ( leaf(A, L) ; leaf(B, L) ).
leaf(\+ A, L) :- !, leaf(A, L).
leaf(_^A, L) :- !, leaf(A, L).
leaf(once(A), L) :- !, leaf(A, L).
leaf(forall(A, B), L) :- !, ( leaf(A, L) ; leaf(B, L) ).
leaf(aggregate_all(_, A, _), L) :- !, leaf(A, L).
leaf(findall(_, A, _), L) :- !, leaf(A, L).
leaf(setof(_, A, _), L) :- !, leaf(A, L).
leaf(bagof(_, A, _), L) :- !, leaf(A, L).
leaf(G, G).
known_or_builtin(G) :-
    callable(G), functor(G, N, A),
    (   known(N/A) -> true
    ;   predicate_property(system:G, built_in) -> true
    ;   memberchk(N/A, [member/2, memberchk/2, sum_list/2, max_list/2, min_list/2, length/2, nth1/3, msort/2]) ).

%% stratified(-Bad): Bad = P-Q pairs where P depends negatively on Q (\+ or an aggregate) and Q
%% depends back on P. The engine evaluates \+ by finite failure, which is sound only if Bad = [].
stratified(Bad) :-
    findall(P-Q, ( neg_edge(P, Q), closure([Q], Cl), memberchk(P, Cl) ), Bad0), sort(Bad0, Bad).
neg_edge(P, Q) :-
    rule_rec(_, P, _, _, _, _, _, _, Cs), member(C, Cs), body(C, B), neg_sub(B, A), goal_preds(A, Qs), member(Q, Qs).
neg_edge(P, excluded/1) :- excl_target(P, 99).     % the enforced program's wrapper negates excluded/1
neg_sub(V, _) :- var(V), !, fail.
neg_sub((X, Y), A) :- !, ( neg_sub(X, A) ; neg_sub(Y, A) ).
neg_sub((X ; Y), A) :- !, ( neg_sub(X, A) ; neg_sub(Y, A) ).
neg_sub((X -> Y), A) :- !, ( neg_sub(X, A) ; neg_sub(Y, A) ).
neg_sub(\+ X, X) :- !.
neg_sub(aggregate_all(_, X, _), X) :- !.
neg_sub(findall(_, X, _), X) :- !.
neg_sub(setof(_, X, _), X) :- !.
neg_sub(bagof(_, X, _), X) :- !.
neg_sub(forall(X, Y), (X, Y)) :- !.
