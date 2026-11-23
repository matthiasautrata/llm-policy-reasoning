/*  why.pl (verify) -- every why tree re-verifies.

    swipl verify/why.pl ROOT WORLD_DIR LAYER [MAX_PER_PRED]

    For every derived predicate of layer =< LAYER, under the decided readings and under every
    combination of the readings of the forks the predicate depends on, takes up to MAX_PER_PRED
    (default 200) true instances of its most general goal, builds the why/4 tree of each and checks
    it with check_why/3. Also checks that a corrupted tree (one fact leaf replaced by a fact that is
    not in the world) is rejected. Prints one summary line; exits 1 on any failure.
*/
:- use_module('../engine/core').
:- use_module('../engine/why').
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(aggregate)).
:- initialization(main, main).

main :-
    current_prolog_flag(argv, [Root, World, LA | Rest]),
    atom_number(LA, Layer), ( Rest = [MA] -> atom_number(MA, Max) ; Max = 200 ),
    load_meta(Root), load_world(World),
    findall(PI, ( rule_rec(_, PI, _, _, _, _, _, _, _), pred_layer(PI, L), L =< Layer ), P0), sort(P0, PIs),
    get_time(T0),
    findall(R, ( member(PI, PIs), combo(PI, Layer, Rs), instance(PI, Layer, Rs, Max, R) ), Res),
    get_time(T1),
    aggregate_all(count, member(ok(_, _), Res), Ok),
    findall(B, ( member(B, Res), B \= ok(_, _) ), Bad),
    aggregate_all(max(D), member(ok(_, D), Res), MaxD0), ( MaxD0 == 0 -> MaxD = 0 ; MaxD = MaxD0 ),
    corrupt(Layer, Res, CBad),
    Secs is T1 - T0, length(Bad, NB),
    format("~w L~d: ~d trees re-verify (max depth ~w), ~d failures, corrupted tree rejected: ~w, ~2f s~n",
           [World, Layer, Ok, MaxD, NB, CBad, Secs]),
    forall(( member(B, Bad), nth1(I, Bad, B), I =< 10 ), format("  ~q~n", [B])),
    ( NB =:= 0, CBad == yes -> halt(0) ; halt(1) ).

%% the readings to try: decided, then every combination over the forks the predicate depends on
combo(_, _, []).
combo(N/A, Layer, Rs) :-
    functor(G, N, A), goal_meta([G], _, Fs),
    findall(F, ( member(F, Fs), fork_rec(F, FL, _, _), FL =< Layer ), Live), Live \== [],
    readings(Live, Rs), decided_readings(D), \+ forall(member(X, Rs), memberchk(X, D)).
readings([], []).
readings([F|Fs], [F-R|Rs]) :- fork_rec(F, _, _, Rds), member(R, Rds), readings(Fs, Rs).

instance(N/A, Layer, Rs, Max, R) :-
    functor(G, N, A),
    full_readings(Rs, Full), program(Layer, Full, M),
    goals(M, G, Max, Gs),
    member(G1, Gs),
    (   catch(why(Layer, Full, G1, T), E, (R = error(G1, E), fail))
    ->  ( catch(check_why(Layer, Full, T), E2, (R = check_error(G1, E2), fail)) -> depth(T, D), R = ok(t(G1, Full, Layer, T), D) ; var(R) -> R = rejected(G1, Full) ; true )
    ;   var(R) -> R = no_tree(G1, Full)
    ;   true ).

depth(rule(_, _, Ts), D) :- !, foldl([T, A0, A]>>(depth(T, X), A is max(A0, X)), Ts, 0, D0), D is D0 + 1.
depth(ite(_, then(A, B)), D) :- !, append(A, B, Ts), foldl([T, A0, A1]>>(depth(T, X), A1 is max(A0, X)), Ts, 0, D).
depth(ite(_, else(Ts)), D) :- !, foldl([T, A0, A1]>>(depth(T, X), A1 is max(A0, X)), Ts, 0, D).
depth(_, 0).

%% corrupt the first tree that has a world fact leaf: swap in a fact that is not in the world
corrupt(Layer, Res, yes) :-
    member(ok(t(_, Rs, Layer, T), _), Res), replace_fact(T, T2), !,
    \+ catch(check_why(Layer, Rs, T2), _, fail).
corrupt(_, _, no).
replace_fact(fact(G), fact(G2)) :- G \= reading(_, _), G =.. [N|Args], length(Args, Ar), \+ core:schema_pred(N/Ar), Args = [_|_],
    last(Args, X), ( integer(X) -> X2 is X + 999983 ; X2 = no_such_value ), append(Front, [X], Args), append(Front, [X2], Args2), G2 =.. [N|Args2], !.
replace_fact(rule(I, G, Ts), rule(I, G, Ts2)) :- select(T, Ts, T2, Ts2), replace_fact(T, T2), !.

%% true instances of G; a predicate whose last argument must be bound (a date) is tried on the world's dates
goals(M, G, Max, Gs) :-
    catch(( findall(G, limit(Max, M:G), Gs0), sort(Gs0, Gs) ), error(instantiation_error, _), fail), !.
goals(M, G, Max, Gs) :-
    findall(D, ( member(F, [req(_, _, _, _, _, D, _), today(D), assignment(_, _, _, D), exemption(_, _, D),
                            exemption_withdrawn(_, D), role_limit_version(_, _, D, _), vendor_status(_, _, D, _)]),
                 catch(M:F, _, fail) ), D0), sort(D0, Ds),
    G =.. L, last(L, Last),
    findall(G, limit(Max, ( member(Last, Ds), M:G )), Gs0), sort(Gs0, Gs).
