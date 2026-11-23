/*  formal.pl -- evaluate questions against a rendered formal projection, nothing else loaded.

    swipl verify/formal.pl JOBS_JSON OUT_JSON FORMAL_PL   (FORMAL_PL last: swipl loads leading .pl arguments)

    JOBS_JSON: [{"id": Id, "type": Type, "goal": Goal, "readings": [[Fork, Reading], ...]}, ...]
    Each job loads FORMAL_PL fresh into its own module, asserts the given reading/2 facts (for the
    open questions of an open projection) and evaluates the goal the way engine/keys.pl does.
    OUT_JSON: [{"id": Id, "readings": ..., "value": V} | {"id": ..., "error": Message}, ...]
*/
:- if(exists_source(library(json))).
:- use_module(library(json)).
:- else.
:- use_module(library(http/json)).
:- endif.
:- use_module(library(apply)).
:- use_module(library(lists)).

:- initialization(main, main).

main :-
    current_prolog_flag(argv, [JF, Out, F]),
    setup_call_cleanup(open(JF, read, S), json_read_dict(S, Jobs, [value_string_as(string)]), close(S)),
    read_file_to_string(F, Text, []),
    foldl(job(Text), Jobs, Res, 0, _),
    setup_call_cleanup(open(Out, write, O), json_write_dict(O, Res, [width(0)]), close(O)).

job(Text, J, R, N0, N) :-
    N is N0 + 1, format(atom(M), "f~d", [N]),
    setup_call_cleanup(open_string(Text, S), load_files(M:M, [stream(S), silent(true)]), close(S)),
    forall(member([Fk, Rd], J.readings), ( atom_string(A, Fk), atom_string(B, Rd), assertz(M:reading(A, B)) )),
    atom_string(Type, J.type),
    term_string(G, J.goal, [variable_names(Bs)]), ( memberchk('V'=V, Bs) -> true ; true ),
    catch(( value(Type, M, G, V, X), R = _{id:J.id, readings:J.readings, value:X} ),
          E, ( message_to_codes(E, C), R = _{id:J.id, readings:J.readings, error:C} )).

message_to_codes(E, S) :- format(string(S), "~q", [E]).

value(bool, M, G, _, B) :- !, ( once(M:G) -> B = true ; B = false ).
value(set, M, G, V, S) :- !, findall(V, M:G, L0), sort(L0, L1), maplist(to_json, L1, S).
value(_, M, G, V, X) :-
    findall(V, M:G, L0), sort(L0, L),
    ( L = [X0] -> to_json(X0, X)
    ; L == [] -> X = "none"
    ; throw(error(not_single(G, L), _)) ).
to_json(X, X) :- number(X), !.
to_json(X, S) :- atom_string(X, S).
