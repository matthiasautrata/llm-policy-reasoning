/*  compile.pl -- compile mode: validate and execute the plans (intermediate models) of one reply.

    swipl engine/compile.pl < REQUEST_JSON  > RESULT_JSON

    REQUEST  {"world": DIR, "layer": L, "config": "decided"|"open", "type": "bool"|"int"|"sym"|"set",
              "plans": [{"readings": {"c1": "booked_only", ...}, "goal": "<Prolog goal text>"}, ...]}
    A plan is plain data: the readings it adopts and a goal over the material's predicates. For an int, sym
    or set question the goal binds V to the answer; for a bool question the answer is whether it holds.

    Static checks per plan (before anything runs):
      syntax      the goal parses as one Prolog term
      calls       every called predicate is a capability at layer =< L with that arity (engine/capability.pl),
                  or a whitelisted side-effect-free built-in; no variable goals, no module qualification
      variables   for int, sym and set: V occurs in the goal outside negation
      readings    each fork named exists at layer =< L and the reading is one of its readings; in the
                  decided configuration the reading must be the decided one
    Execution: in the open configuration, every fork of layer =< L in the goal's dependency closure that the
    plan does not fix is expanded over all its readings (engine-side divergence); in the decided
    configuration nothing is expanded. Each run has a 10 s limit and at most 1000 solutions. Values as in
    keys.pl: bool true|false; int and sym the single V ("none" if there is none, an error if several);
    set the sorted distinct V.
    Integrity (M6): where an exclusion (excluded/1, R314) bears on the goal, each run is repeated in the
    exclusion-enforced program (core:program_x/3); different values mean the rule base derives G and
    excluded(G), and the run's value is "CONFLICT" (sides [enforced, plain], detail: the atoms).
    Aggregate over every run of every valid plan: one distinct value -> ANSWER, every run "CONFLICT" ->
    CONFLICT (engine_conflict: detected by the engine, not declared by the model), several -> AMBIGUOUS
    (readings: "plan N: c1=..,c6=.." -> value or "CONFLICT"), no run -> null. Each plan also reports
    constructs: the aggregation and arithmetic built-ins its goal uses (flagged, not rejected). Error messages never mention layers: a
    predicate above L is "not a predicate of the material", as one no layer defines.

    RESULT   {"status", "value", "readings", "errors": [msg], "plans": [{"index", "goal", "error",
              "fixed": {fork: reading}, "expanded": [fork], "runs": [{"readings": {..}, "value"|"error"}]}]}
*/
:- use_module(core).
:- use_module(capability).
:- if(exists_source(library(json))).
:- use_module(library(json)).
:- else.
:- use_module(library(http/json)).
:- endif.
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(time)).

:- initialization(main, main).
:- prolog_load_context(directory, D), file_directory_name(D, Root), assertz(root(Root)).
:- dynamic root/1.

time_limit(10).
max_solutions(1000).

main :-
    root(Root), load_meta(Root),
    json_read_dict(user_input, Q, [value_string_as(string)]),
    atom_string(W, Q.world), load_world(W),
    atom_string(Cfg, Q.config), atom_string(Type, Q.type),
    numlist_from(1, Q.plans, Ix),
    maplist(plan(Q.layer, Cfg, Type), Ix, Q.plans, Ps),
    aggregate(Ps, Out0),
    findall(M, ( member(P, Ps), P.error \== null, format(string(M), "plan ~d: ~s", [P.index, P.error]) ), E1),
    findall(M, ( member(P, Ps), member(R, P.runs), get_dict(error, R, Er),
                 run_label(P.index, R.readings, Lb), format(string(M), "~s: ~s", [Lb, Er]) ), E2),
    append(E1, E2, Errs),
    json_write_dict(user_output, Out0.put(_{errors:Errs, plans:Ps}), [width(0)]), nl.

numlist_from(_, [], []) :- !.
numlist_from(N, [_|T], [N|R]) :- N1 is N + 1, numlist_from(N1, T, R).

%% plan(+Layer, +Cfg, +Type, +Index, +PlanDict, -ResultDict)
plan(Layer, Cfg, Type, I, P, R) :-
    ( get_dict(goal, P, Text0) -> true ; Text0 = "" ),
    ( string(Text0) -> Text = Text0 ; format(string(Text), "~w", [Text0]) ),
    R0 = _{index:I, goal:Text, error:null, fixed:_{}, expanded:[], runs:[], constructs:[]},
    catch(( validate(Layer, Cfg, Type, P, Text, G, V, Fixed), Res = ok ), compile_error(Msg), Res = error(Msg)),
    (   Res == ok
    ->  expand(Layer, Cfg, G, Fixed, Exp),
        findall(Rs, ( combos(Exp, C), append(Fixed, C, Rs) ), Combos),
        maplist(run(Layer, Type, G, V), Combos, Runs),
        pairs_dict(Fixed, FD), constructs(G, Cn),
        R = R0.put(_{fixed:FD, expanded:Exp, runs:Runs, constructs:Cn})
    ;   Res = error(Msg1), R = R0.put(error, Msg1) ).

fail_with(Fmt, Args) :- format(string(M), Fmt, Args), throw(compile_error(M)).

%% ---------- static checks ----------
validate(Layer, Cfg, Type, P, Text, G, V, Fixed) :-
    ( Text == "" -> fail_with("the plan has no goal", []) ; true ),
    catch(term_string(G, Text, [variable_names(Bs)]), E,
          ( message_line(E, M0), fail_with("the goal does not parse (~s)", [M0]) )),
    ( var(G) -> fail_with("the goal is a bare variable", []) ; true ),
    calls_ok(Layer, G),
    ( memberchk('V'=V, Bs) -> true ; true ),
    (   Type == bool -> true
    ;   var(V), strip_neg(G, Pos), term_variables(Pos, PV), member(X, PV), X == V -> true
    ;   what(Type, What), fail_with("the question asks for ~w, so the goal must bind V to the answer (V must occur outside negation)", [What]) ),
    ( get_dict(readings, P, RD), is_dict(RD) -> dict_pairs(RD, _, RP) ; RP = [] ),
    maplist(reading_ok(Layer, Cfg), RP, Fixed0), sort(Fixed0, Fixed).

calls_ok(_, G) :- var(G), !, fail_with("a goal may not be a variable", []).
calls_ok(_, _:_) :- !, fail_with("module-qualified goals are not allowed", []).
calls_ok(L, G) :- control(G, Subs), !, maplist(calls_ok(L), Subs).
calls_ok(L, G) :-
    ( callable(G) -> true ; fail_with("~q is not a goal", [G]) ),
    functor(G, N, A),
    (   capability(N/A, L0, _), L0 =< L -> true
    ;   allowed(N/A) -> true
    ;   ( known(N/A) ; capability(N/A, _, _) ; \+ predicate_property(system:G, built_in) )
    ->  (   findall(N/A1, ( capability(N/A1, L1, _), L1 =< L ), Others), Others = [_|_]
        ->  fail_with("~q is not a predicate of the material (it has ~q)", [N/A, Others])
        ;   fail_with("~q is not a predicate of the material", [N/A]) )
    ;   fail_with("~q is not allowed in a plan (only the material's predicates and the listed built-ins)", [N/A]) ).

%% control(+G, -SubGoals): control constructs and the goal arguments of aggregates.
control((A, B), [A, B]).
control((A ; B), [A, B]).
control((A -> B), [A, B]).
control(\+ A, [A]).
control(once(A), [A]).
control(forall(A, B), [A, B]).
control(aggregate_all(_, A, _), [A]).
control(findall(_, A, _), [A]).
control(setof(_, A, _), [A1]) :- strip_hat(A, A1).
control(bagof(_, A, _), [A1]) :- strip_hat(A, A1).
strip_hat(A, A) :- var(A), !.
strip_hat(_^A, B) :- !, strip_hat(A, B).
strip_hat(A, A).

allowed(PI) :- memberchk(PI, [
    true/0, fail/0, false/0,
    (=)/2, (\=)/2, (==)/2, (\==)/2, (@<)/2, (@>)/2, (@=<)/2, (@>=)/2, compare/3,
    (<)/2, (>)/2, (=<)/2, (>=)/2, (=:=)/2, (=\=)/2, (is)/2, between/3, succ/2, plus/3,
    atom/1, number/1, integer/1, atomic/1, var/1, nonvar/1, ground/1, is_list/1,
    member/2, memberchk/2, length/2, append/3, nth0/3, nth1/3, last/2, msort/2, sort/2, sort/4,
    list_to_set/2, sum_list/2, sumlist/2, max_list/2, min_list/2, max_member/2, min_member/2,
    subtract/3, intersection/3, union/3 ]).

%% strip_neg(+G, -Pos): G with its negated parts removed (\+ A, and the condition-only parts of forall).
strip_neg(G, G) :- var(G), !.
strip_neg(\+ _, true) :- !.
strip_neg(forall(_, _), true) :- !.
strip_neg((A, B), (A1, B1)) :- !, strip_neg(A, A1), strip_neg(B, B1).
strip_neg((A ; B), (A1 ; B1)) :- !, strip_neg(A, A1), strip_neg(B, B1).
strip_neg((A -> B), (A1 -> B1)) :- !, strip_neg(A, A1), strip_neg(B, B1).
strip_neg(G, G).

reading_ok(Layer, Cfg, F0-R0, F-R) :-
    to_atom(F0, F), to_atom(R0, R),
    (   fork_rec(F, FL, Dec, Rds), FL =< Layer -> true
    ;   fail_with("~w is not a question of interpretation of the material", [F]) ),
    ( memberchk(R, Rds) -> true ; fail_with("~w is not a reading of ~w (its readings: ~w)", [R, F, Rds]) ),
    ( Cfg == decided, R \== Dec -> fail_with("~w is decided as ~w in the material, not ~w", [F, Dec, R]) ; true ).
to_atom(X, A) :- ( atom(X) -> A = X ; string(X) -> atom_string(A, X) ; format(atom(A), "~w", [X]) ).

%% ---------- execution ----------
expand(_, decided, _, _, []) :- !.
expand(Layer, open, G, Fixed, Exp) :-
    goal_meta([G], _, Fs0),
    findall(F, ( sub_term(T, G), compound(T), T = reading(F0, _), atom(F0), F = F0 ), Fs1),
    append(Fs0, Fs1, Fs2), sort(Fs2, Fs),
    findall(F, ( member(F, Fs), fork_rec(F, FL, _, _), FL =< Layer, \+ memberchk(F-_, Fixed) ), Exp).

combos([], []).
combos([F|Fs], [F-R|Rs]) :- fork_rec(F, _, _, Rds), member(R, Rds), combos(Fs, Rs).

run(Layer, Type, G0, V0, Rs, Out) :-
    pairs_dict(Rs, RD),
    program(Layer, Rs, M),
    run_in(M, Type, G0, V0, Res),
    (   Res = value(X1), excl_relevant(Layer, [G0])          % integrity: the exclusion-enforced program too
    ->  program_x(Layer, Rs, MX), run_in(MX, Type, G0, V0, ResX),
        (   ResX = value(X1) -> Out = _{readings:RD, value:X1}
        ;   ResX = value(XX) -> contradicted(M, Layer, As), format(string(D), "derived and excluded: ~q", [As]),
            Out = _{readings:RD, value:"CONFLICT", sides:[XX, X1], detail:D}
        ;   ResX = error(MsgX), Out = _{readings:RD, error:MsgX} )
    ;   Res = value(X1) -> Out = _{readings:RD, value:X1}
    ;   Res = error(Msg1), Out = _{readings:RD, error:Msg1} ).

run_in(M, Type, G0, V0, Res) :-
    copy_term(G0-V0, G-V), time_limit(T),
    catch(( call_with_time_limit(T, value(Type, M, G, V, X)), Res = value(X) ), E, ( message_line(E, Msg), Res = error(Msg) )).

%% constructs(+Goal, -Names): aggregation and arithmetic the plan computes itself. Reported, not rejected:
%% a count can be legitimate, but at a layer that lacks the concept it marks an inlined definition.
constructs(G, Ns) :-
    findall(N, ( sub_term(T, G), compound(T), functor(T, N, A), memberchk(N/A, [aggregate_all/3, aggregate_all/4,
                 findall/3, setof/3, bagof/3, sum_list/2, sumlist/2, max_list/2, min_list/2, max_member/2,
                 min_member/2, length/2, is/2, succ/2, plus/3]) ), Ns0), sort(Ns0, Ns).

value(bool, M, G, _, B) :- !, ( once(M:G) -> B = true ; B = false ).
value(set, M, G, V, S) :- !, max_solutions(N),
    findall(V, limit(N, M:G), L0), sort(L0, L1), maplist(to_json, L1, S).
value(Type, M, G, V, X) :- max_solutions(N),
    findall(V, limit(N, M:G), L0), sort(L0, L),
    (   L = [X0] -> to_json(X0, X), ( Type == int, \+ integer(X0) -> throw(not_integer(X0)) ; true )
    ;   L == [] -> X = "none"
    ;   throw(several(L)) ).

to_json(X, X) :- number(X), !.
to_json(X, S) :- atom(X), !, atom_string(X, S).
to_json(X, _) :- throw(not_a_value(X)).

message_line(several(L), M) :- !, length(L, N), ( N > 5 -> length(H, 5), append(H, _, L), Sfx = ", ..." ; H = L, Sfx = "" ),
    format(string(M), "the goal gives ~d different values for V (~q~s); this question needs exactly one", [N, H, Sfx]).
message_line(not_integer(X), M) :- !, format(string(M), "V = ~q is not an integer", [X]).
message_line(not_a_value(X), M) :- !, format(string(M), "V = ~q is not an identifier or a number", [X]).
message_line(time_limit_exceeded, "the goal did not finish within the time limit") :- !.
message_line(error(existence_error(procedure, PI), _), M) :- !,
    ( PI = _:P -> true ; P = PI ), format(string(M), "~q is not a predicate of the material", [P]).
message_line(error(syntax_error(S), _), M) :- !, format(string(M), "syntax error: ~w", [S]).
message_line(E, M) :-
    catch(( '$messages':translate_message(E, Ls, []),
            with_output_to(string(S0), print_message_lines(current_output, '', Ls)),
            normalize_space(string(M), S0) ), _, fail), !.
message_line(E, M) :- format(string(M), "~q", [E]).

%% ---------- aggregate ----------
aggregate(Ps, Out) :-
    findall(Lb-X, ( member(P, Ps), member(R, P.runs), get_dict(value, R, X), run_label(P.index, R.readings, Lb) ), Vs),
    findall(X, member(_-X, Vs), Xs0), sort(Xs0, Xs),
    (   Xs == [] -> Out = _{status:null, value:null, readings:null}
    ;   Xs == ["CONFLICT"]                                   % every run contradicts itself
    ->  findall(S, ( member(P, Ps), member(R, P.runs), get_dict(sides, R, S) ), Ss0), sort(Ss0, Ss),
        ( Ss = [S1] -> Sd = S1 ; Sd = null ),
        Out = _{status:"CONFLICT", value:null, readings:null, sides:Sd, engine_conflict:true}
    ;   Xs = [X] -> Out = _{status:"ANSWER", value:X, readings:null}
    ;   findall(K-X, ( member(Lb-X, Vs), atom_string(K, Lb) ), KV0),
        sort(1, @<, KV0, KV), dict_pairs(RD, _, KV),
        Out = _{status:"AMBIGUOUS", value:null, readings:RD} ).

run_label(I, RD, Lb) :-
    dict_pairs(RD, _, Ps),
    ( Ps == [] -> format(string(Lb), "plan ~d", [I])
    ; maplist([F-R, S]>>format(string(S), "~w=~w", [F, R]), Ps, Ss), atomic_list_concat(Ss, ',', A),
      format(string(Lb), "plan ~d: ~w", [I, A]) ).

pairs_dict(Ps, D) :- dict_pairs(D, _, Ps).
what(int, "a number").
what(sym, "a single value").
what(set, "a list").
