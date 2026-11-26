/*  EDN reader (DCG) for the subset spike v3 uses.

    EDN               Prolog
    [a b] (a b)       list
    {k v ...}         map([K-V, ...])
    #{a b}            set([...])
    :kw  :C1.1  :<    atom kw, 'C1.1', <
    "s"               string
    12  -3  1.5       number
    true false nil    true, false, null
    sym  ?x           sym(sym), sym('?x')   (edn_vars/2 turns ?x into Prolog variables)
    #inst "2026-..."  string "2026-09-15" (date part)
    ; comment , whitespace
*/
:- module(edn, [edn_read_file/2, edn_parse/2, edn_vars/2, edn_vars/4, mget/3, mget/4]).
:- use_module(library(dcg/basics)).

edn_read_file(File, T) :-
    read_file_to_codes(File, Cs, [encoding(utf8)]),
    (   phrase((ws, value(T), ws), Cs) -> true
    ;   throw(error(edn_syntax(File), _)) ).

edn_parse(Text, T) :-
    string_codes(Text, Cs),
    (   phrase((ws, value(T), ws), Cs) -> true
    ;   throw(error(edn_syntax(Text), _)) ).

ws --> [C], { code_type(C, space) ; C =:= 0', }, !, ws.
ws --> ";", string_without("\n", _), !, ws.
ws --> [].

value(L)          --> "[", !, ws, items(L), "]".
value(L)          --> "(", !, ws, items(L), ")".
value(set(L))     --> "#{", !, ws, items(L), "}".
value(map(Ps))    --> "{", !, ws, pairs(Ps), "}".
value(D)          --> "#inst", !, ws, str(S), { sub_string(S, 0, 10, _, D) }.
value(S)          --> str(S), !.
value(K)          --> ":", !, name_codes(Cs), { Cs \== [], atom_codes(K, Cs) }.
value(N)          --> number(N), !.
value(T)          --> name_codes(Cs), { Cs \== [], atom_codes(A, Cs), sym_value(A, T) }.

sym_value(true, true) :- !.
sym_value(false, false) :- !.
sym_value(nil, null) :- !.
sym_value(A, sym(A)).

items([V|Vs]) --> value(V), !, ws, items(Vs).
items([])     --> [].

pairs([K-V|Ps]) --> value(K), !, ws, value(V), ws, pairs(Ps).
pairs([])       --> [].

str(S) --> "\"", chars(Cs), "\"", { string_codes(S, Cs) }.
chars([C|Cs]) --> "\\", [E], !, { esc(E, C) }, chars(Cs).
chars([C|Cs]) --> [C], { C \== 0'" }, !, chars(Cs).
chars([])     --> [].
esc(0'n, 0'\n). esc(0't, 0'\t). esc(0'", 0'"). esc(0'\\, 0'\\).

name_codes([C|Cs]) --> [C], { name_char(C) }, !, name_codes(Cs).
name_codes([])     --> [].
name_char(C) :- code_type(C, alnum), !.
name_char(C) :- memberchk(C, `_-.*+!?<>=/$%&'`).

%!  edn_vars(+T0, -T) is det.
%   Replace sym('?x') by Prolog variables, one per distinct name.
edn_vars(T0, T) :- edn_vars(T0, T, [], _).
edn_vars(V, V, A, A) :- var(V), !.
edn_vars(sym(N), V, A0, A) :- sub_atom(N, 0, 1, _, ?), !,
    (   memberchk(N-V0, A0) -> V = V0, A = A0 ; A = [N-V|A0] ).
edn_vars(T0, T, A0, A) :- compound(T0), !,
    T0 =.. [F|As0], foldl_vars(As0, As, A0, A), T =.. [F|As].
edn_vars(T, T, A, A).
foldl_vars([], [], A, A).
foldl_vars([X|Xs], [Y|Ys], A0, A) :- edn_vars(X, Y, A0, A1), foldl_vars(Xs, Ys, A1, A).

%!  mget(+Key, +Map, -Value) is semidet.   mget/4 with a default.
mget(K, map(Ps), V) :- memberchk(K-V, Ps).
mget(K, M, V, D) :- ( mget(K, M, V0), V0 \== null -> V = V0 ; V = D ).
