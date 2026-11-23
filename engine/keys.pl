/*  keys.pl -- per-layer answer keys for question instances.

    swipl engine/keys.pl ROOT WORLD_DIR QUESTIONS_JSON OUT_JSON

    For each question and layer L0..L3, in two configurations:
      decided  every fork takes its decided reading (the material states the decisions)
      open     every fork the question depends on is left open (all readings are live)
    the key is one of
      OUT_OF_SCOPE     the goal calls a predicate no layer defines
      UNDERDETERMINED  L < min_layer (missing_layer = min_layer)
      ANSWER           value (bool | int | sym as string | set as sorted list)
      CONFLICT         the rule base contradicts itself on the goal (it derives G and excluded(G): the plain
                       and the exclusion-enforced program differ; sides [enforced value, plain value]), or the
                       bank's conflict goal holds (data conflicts; sides: the distinct values the material
                       supports, for sym and int goals; both, for bool); in either case only if no resolve
                       goal is available at L
      AMBIGUOUS        live readings give different results (readings: "c1=..,c4=.." -> value | "CONFLICT")
    min_layer and forks are derived here from the dependency closure of goal and conflict (meta).
    why: for each bool question whose L3 decided key is true, the why/4 tree of its goal (checked with
    check_why/3), its core rules and support rules (engine/why.pl); explain answers are graded on them.
*/
:- use_module(core).
:- use_module(why).
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
    foldl(question_ctx, Qs, _{meta:_{}, decided:_{}, open:_{}, why:_{}}, Keys),
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
    ( why_entry(P, DD.'L3', W) -> put_dict(Id, K0.why, W, Wh) ; Wh = K0.why ),
    K = _{meta:Me, decided:De, open:Op, why:Wh}.

%% why_entry(+Parsed, +L3DecidedKey, -Entry): for a bool question keyed true at L3 (decided), the
%% justification an explanation is graded against: the proof tree (re-verified here) and its rules.
why_entry(q(bool, G-_, _, _), _{status:"ANSWER", value:true}, _{tree:TD, core:Core, support:Sup}) :-
    why(3, [], G, T),
    ( check_why(3, [], T) -> true ; throw(error(why_does_not_verify(G), _)) ),
    why_rules(3, [], T, Core, Sup), tree_dict(T, TD).

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
    findall(X, ( member(Res, Distinct), res_value(Res, X) ), Xs0), sort(Xs0, Xs),
    (   Distinct = [One] -> entry(One, E)
    ;   Xs == ["CONFLICT"]                 % every reading conflicts, on sides that vary: CONFLICT, no sides
    ->  Distinct = [conflict(D, _)|_], entry(conflict(D, none), E)
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
entry(conflict(D, none), _{status:"CONFLICT", detail:D}) :- !.
entry(conflict(D, S), _{status:"CONFLICT", detail:D, sides:S}).
res_value(v(V), V).
res_value(conflict(_, _), "CONFLICT").

%% eval(+Layer, +Readings, +Parsed, -v(Value) | conflict(Detail, Sides))
%% A conflict is detected (the plain and the exclusion-enforced program give different values: the rule
%% base derives G and excluded(G); sides [enforced value, plain value]) or declared (the bank's conflict
%% goal holds: data conflicts such as Q25). Where an exclusion bears on the goal, the declaration must
%% agree with the detection: the bank and the engine are checked against each other, not trusted.
eval(L, Rs, P0, Res) :-
    copy_term(P0, q(Type, G-V, C, R-RV)),
    program(L, Rs, M),
    (   excl_relevant(L, [G]) -> value(Type, M, G, V, X), program_x(L, Rs, MX), value(Type, MX, G, V, XX),
        ( X \== XX -> Det = true ; Det = false ), Rel = true
    ;   Det = false, Rel = false ),
    ( C \== none, once(M:C) -> Dec = true ; Dec = false ),
    ( Rel == true, C \== none, Det \== Dec -> throw(error(conflict_declaration_mismatch(G, detected(Det), declared(Dec)), _)) ; true ),
    (   ( Det == true ; Dec == true )
    ->  (   R \== none, goal_meta([R], RL, _), RL =< L
        ->  value(Type, M, R, RV, Y), Res = v(Y)
        ;   Det == true
        ->  contradicted(M, L, As0), relevant_atoms(As0, G, X, XX, As),
            format(string(D), "derived and excluded: ~q", [As]), Res = conflict(D, [XX, X])
        ;   format(string(D), "~q", [C]), sides(Type, M, G, V, S), Res = conflict(D, S) )
    ;   ( var(X) -> value(Type, M, G, V, X) ; true ), Res = v(X) ).

%% relevant_atoms: the contradicted atoms that mention the goal's constants or the values that differ.
relevant_atoms(As0, G, X, XX, As) :-
    term_to_list(X, L1), term_to_list(XX, L2), union(L1, L2, U), intersection(L1, L2, I), subtract(U, I, Diff),
    findall(A, ( member(A, As0), A =.. [_|Args], member(Arg, Args), atomic(Arg),
                 ( atom_string(Arg, S), memberchk(S, Diff) ; sub_term(T, G), T == Arg ) ), As1),
    sort(As1, As).
term_to_list(X, L) :- ( is_list(X) -> L = X ; L = [X] ).

sides(bool, _, _, _, [false, true]) :- !.
sides(set, _, _, _, none) :- !.
sides(_, M, G, V, S) :- value(set, M, G, V, S).

value(bool, M, G, _, B) :- !, ( once(M:G) -> B = true ; B = false ).
value(set, M, G, V, S) :- !, findall(V, M:G, L0), sort(L0, L1), maplist(to_json, L1, S).
value(_, M, G, V, X) :-
    findall(V, M:G, L0), sort(L0, L),
    ( L = [X0] -> to_json(X0, X)
    ; L == [] -> X = "none"
    ; throw(error(not_single(G, L), _)) ).
to_json(X, X) :- number(X), !.
to_json(X, S) :- atom_string(X, S).
