/*  keys.pl -- per-layer answer keys for question instances.

    swipl engine/keys.pl ROOT WORLD_DIR QUESTIONS_JSON OUT_JSON

    For each question and layer L0..L3, in two configurations:
      decided  every fork takes its decided reading (the material states the decisions)
      open     every fork the question depends on is left open (all readings are live)
    the key is one of
      OUT_OF_SCOPE     the goal calls a predicate no layer defines
      UNDERDETERMINED  L < min_layer (missing_layer = min_layer)
      ANSWER           value (bool | int | sym as string | set as sorted list)
      CONFLICT         the conflict goal holds and no resolve goal is available at L (detail)
      AMBIGUOUS        live readings give different results (readings: "c1=..,c4=.." -> value | "CONFLICT")
    min_layer and forks are derived here from the dependency closure of goal and conflict (meta).
*/
:- use_module(core).
:- if(exists_source(library(json))).
:- use_module(library(json)).
:- else.
:- use_module(library(http/json)).
:- endif.
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

:- initialization(main, main).

main :-
    current_prolog_flag(argv, [Root, World, QF, Out]),
    load_meta(Root),
    ( stratified(Bad) -> true ; Bad = [] ),
    ( Bad == [] -> true ; format(user_error, "rule base not stratified: ~q~n", [Bad]), halt(1) ),
    load_world(World),
    setup_call_cleanup(open(QF, read, S), json_read_dict(S, Qs, [value_string_as(string)]), close(S)),
    foldl(question_ctx, Qs, _{meta:_{}, decided:_{}, open:_{}}, Keys),
    setup_call_cleanup(open(Out, write, O), json_write_dict(O, Keys, [width(0)]), close(O)).

question_ctx(Q, K0, K) :-
    catch(question(Q, K0, K), E, ( get_dict(id, Q, Id), format(user_error, "question ~s: ", [Id]), throw(E) )).

question(Q, K0, K) :-
    atom_string(Id, Q.id),
    parse(Q, P),
    meta(P, Meta),
    findall(LK-E, ( between(0, 3, L), format(atom(LK), "L~d", [L]), key(decided, L, Meta, P, E) ), Dec),
    findall(LK-E, ( between(0, 3, L), format(atom(LK), "L~d", [L]), key(open, L, Meta, P, E) ), Open),
    dict_pairs(DD, _, Dec), dict_pairs(OD, _, Open),
    ( Meta = scope(ML, Fs) -> MD = _{min_layer:ML, forks:Fs} ; MD = _{min_layer:null, forks:[]} ),
    put_dict(Id, K0.meta, MD, Me), put_dict(Id, K0.decided, DD, De), put_dict(Id, K0.open, OD, Op),
    K = _{meta:Me, decided:De, open:Op}.

%% parse(+QuestionDict, -q(Type, Goal-V, Conflict, Resolve-RV))
parse(Q, q(Type, G-V, C, R-RV)) :-
    atom_string(Type, Q.type),
    goal_var(Q.goal, G, V),
    ( Q.get(conflict) = CS, string(CS) -> term_string(C, CS) ; C = none ),
    ( Q.get(resolve) = RS, string(RS) -> goal_var(RS, R, RV) ; R = none ).
goal_var(S, G, V) :- term_string(G, S, [variable_names(Bs)]), ( memberchk('V'=V, Bs) -> true ; true ).

%% meta(+Parsed, -scope(MinLayer, Forks) | out_of_scope)
meta(q(_, G-_, C, _), M) :-
    Gs = [G|Cs], ( C == none -> Cs = [] ; Cs = [C] ),
    ( member(X, Gs), unknown_call(X) -> M = out_of_scope
    ; goal_meta(Gs, ML, Fs), M = scope(ML, Fs) ).

key(_, _, out_of_scope, _, _{status:"OUT_OF_SCOPE"}) :- !.
key(_, L, scope(ML, _), _, _{status:"UNDERDETERMINED", missing_layer:ML}) :- L < ML, !.
key(Cfg, L, scope(_, Fs), P, E) :-
    live_forks(Cfg, L, Fs, Live),
    findall(Rs, readings(Live, Rs), Combos),
    findall(Rs-Res, ( member(Rs, Combos), eval(L, Rs, P, Res) ), Results),
    findall(Res, member(_-Res, Results), Rs0), sort(Rs0, Distinct),
    ( Distinct = [One] -> entry(One, E)
    ; findall(RK-RV, ( member(Rs-Res, Results), readings_key(Rs, RK), res_value(Res, RV) ), Pairs),
      dict_pairs(RD, _, Pairs), E = _{status:"AMBIGUOUS", readings:RD} ).

live_forks(decided, _, _, []).
live_forks(open, L, Fs, Live) :- findall(F, ( member(F, Fs), fork_rec(F, FL, _, _), FL =< L ), Live).

readings([], []).
readings([F|Fs], [F-R|Rs]) :- fork_rec(F, _, _, Rds), member(R, Rds), readings(Fs, Rs).

readings_key([], 'decided') :- !.
readings_key(Rs, K) :- maplist([F-R, S]>>format(string(S), "~w=~w", [F, R]), Rs, Ss),
    atomic_list_concat(Ss, ',', K).

entry(v(V), _{status:"ANSWER", value:V}).
entry(conflict(D), _{status:"CONFLICT", detail:D}).
res_value(v(V), V).
res_value(conflict(_), "CONFLICT").

%% eval(+Layer, +Readings, +Parsed, -v(Value) | conflict(Detail))
eval(L, Rs, P0, Res) :-
    copy_term(P0, q(Type, G-V, C, R-RV)),
    program(L, Rs, M),
    (   C \== none, once(M:C)
    ->  (   R \== none, goal_meta([R], RL, _), RL =< L
        ->  value(Type, M, R, RV, X), Res = v(X)
        ;   format(string(D), "~q", [C]), Res = conflict(D) )
    ;   value(Type, M, G, V, X), Res = v(X) ).

value(bool, M, G, _, B) :- !, ( once(M:G) -> B = true ; B = false ).
value(set, M, G, V, S) :- !, findall(V, M:G, L0), sort(L0, L1), maplist(to_json, L1, S).
value(_, M, G, V, X) :-
    findall(V, M:G, L0), sort(L0, L),
    ( L = [X0] -> to_json(X0, X)
    ; L == [] -> X = "none"
    ; throw(error(not_single(G, L), _)) ).
to_json(X, X) :- number(X), !.
to_json(X, S) :- atom_string(X, S).
