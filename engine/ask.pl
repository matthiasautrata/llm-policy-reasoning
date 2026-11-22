/*  ask.pl -- the tool boundary: run one goal against a world at a layer, and log the call.

    engine/ask [--world DIR] [--layer N] [--reading FORK=READING]... GOAL
    engine/ask [--layer N] --capabilities
    Defaults: ASK_WORLD, ASK_LAYER (else 3); forks not given take their decided reading.
    Prints one line per solution with the bindings of the goal's named variables ("true" if none),
    or "false". Every call is appended as one JSON line to ASK_LOG (else WORLD/ask.log.jsonl).
*/
:- use_module(core).
:- use_module(capability).
:- if(exists_source(library(json))).
:- use_module(library(json)).
:- else.
:- use_module(library(http/json)).
:- endif.
:- use_module(library(main)).

:- initialization(main, main).
:- prolog_load_context(directory, D), file_directory_name(D, Root), assertz(root(Root)).
:- dynamic root/1.

max_solutions(1000).

main(Argv) :-
    root(Root), load_meta(Root),
    opts(Argv, _{world:none, layer:none, readings:[], caps:false}, O, Rest),
    ( O.layer \== none -> Layer = O.layer ; getenv('ASK_LAYER', LS) -> atom_number(LS, Layer) ; Layer = 3 ),
    (   O.caps == true
    ->  capabilities(Layer, Cs), forall(member(c(PI, L, Doc), Cs), format("L~d  ~q  ~s~n", [L, PI, Doc]))
    ;   ( O.world \== none -> W = O.world ; getenv('ASK_WORLD', W) -> true ; die("no world: --world DIR or ASK_WORLD") ),
        atomic_list_concat(Rest, ' ', GoalText),
        ( GoalText == '' -> die("no goal") ; true ),
        load_world(W),
        get_time(T0),
        catch(run(Layer, O.readings, GoalText, Lines, Status), E,
              ( error_message(E, Layer, Msg), Lines = [Msg], Status = error(Msg) )),
        get_time(T1),
        forall(member(Ln, Lines), format("~s~n", [Ln])),
        Secs is T1 - T0,
        log_call(W, Layer, O.readings, GoalText, Status, Secs),
        ( Status = error(_) -> halt(2) ; true )
    ).

error_message(error(unknown_predicate(_), _), _, "error: the goal calls a predicate that no layer defines") :- !.
error_message(error(existence_error(procedure, PI), _), L, Msg) :- !,
    unqualified(PI, P), format(string(Msg), "error: ~q is not defined at layer ~d", [P, L]).
error_message(error(syntax_error(S), _), _, Msg) :- !, format(string(Msg), "error: syntax error (~w)", [S]).
error_message(E, _, Msg) :-                     % anything else: SWI's own message text, one line
    catch(( message_to_codes(E, Cs), normalize_space(string(S), Cs) ), _, fail), !,
    string_concat("error: ", S, Msg).
error_message(E, _, Msg) :- format(string(Msg), "error: ~q", [E]).
unqualified(_:PI, PI) :- !.
unqualified(PI, PI).
message_to_codes(E, Cs) :- '$messages':translate_message(E, Lines, []),
    with_output_to(string(Cs), print_message_lines(current_output, '', Lines)).

opts([], O, O, []).
opts(['--world', W|T], O0, O, R) :- !, opts(T, O0.put(world, W), O, R).
opts(['--layer', L|T], O0, O, R) :- !, atom_number(L, N), opts(T, O0.put(layer, N), O, R).
opts(['--reading', FR|T], O0, O, R) :- !, atomic_list_concat([F, Rd], '=', FR),
    opts(T, O0.put(readings, [F-Rd|O0.readings]), O, R).
opts(['--capabilities'|T], O0, O, R) :- !, opts(T, O0.put(caps, true), O, R).
opts([A|T], O0, O, [A|R]) :- opts(T, O0, O, R).

run(Layer, Readings, Text, Lines, Status) :-
    term_string(G, Text, [variable_names(Bs)]),
    ( unknown_call(G) -> throw(error(unknown_predicate(G), _)) ; true ),
    program(Layer, Readings, M), max_solutions(Max),
    findall(Line, limit(Max, (M:G, bindings_line(Bs, Line))), Lines0),
    ( Lines0 == [] -> Lines = ["false"], Status = false
    ; sort(Lines0, Lines), length(Lines, N), Status = solutions(N) ).

bindings_line([], "true") :- !.
bindings_line(Bs, Line) :-
    exclude([N=_]>>sub_atom(N, 0, _, _, '_'), Bs, Named),
    ( Named == [] -> Line = "true"
    ; maplist([N=V, S]>>format(string(S), "~w = ~q", [N, V]), Named, Ss), atomic_list_concat(Ss, ', ', A), atom_string(A, Line) ).

log_call(W, Layer, Readings, Goal, Status, Secs) :-
    ( getenv('ASK_LOG', LF) -> true ; directory_file_path(W, 'ask.log.jsonl', LF) ),
    get_time(Now), format_time(string(TS), "%FT%T%:z", Now),
    maplist([F-R, S]>>format(string(S), "~w=~w", [F, R]), Readings, RS),
    ( Status = solutions(N) -> St = "ok" ; Status == false -> St = "false", N = 0 ; St = "error", N = 0 ),
    D = _{ts:TS, world:W, layer:Layer, readings:RS, goal:Goal, status:St, solutions:N, seconds:Secs},
    setup_call_cleanup(open(LF, append, S), (json_write_dict(S, D, [width(0)]), nl(S)), close(S)).

die(Msg) :- format(user_error, "ask: ~s~n", [Msg]), halt(1).
