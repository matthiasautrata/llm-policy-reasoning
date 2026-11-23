/*  why.pl -- justifications: the proof tree of a goal that holds, and a check that re-verifies it.

    why(+Layer, +Readings, +Goal, -Tree)
        Goal is answered with the tabled program (core:program/3); a true instance is then justified
        by a meta-interpreter over the same rule records (layer =< Layer, forked clauses only in the
        chosen readings). Nodes:
          rule(Id, G, Body)      G holds by a clause of rule Id; Body = the trees of its literals, in order
          fact(G)                a base fact, a schema fact or a reading/2 fact of the program
          builtin(G)             a comparison or arithmetic step
          absent(G)              \+ G holds: G has no proof (closed world); not expanded further
          lemma(G)               an aggregate (aggregate_all, setof, findall, forall, member), or a
                                 subgoal below the depth bound: re-run as a whole, not expanded
          ite(C, then(TC, TT))   (C -> T ; E) took the then branch: TC proves C, TT proves T
          ite(C, else(TE))       ... took the else branch: C fails, TE proves E
        Fails if Goal has no solution. A non-ground Goal is justified for its first solution.
    check_why(+Layer, +Readings, +Tree)
        Re-verifies a tree without the meta-interpreter: every rule node is an instance of a clause of
        its rule (allowed at Layer under Readings) whose body literals match the children in order;
        fact leaves are looked up in the world's facts (not the program), builtins re-evaluated,
        absent and lemma leaves re-run against the program.
    why_rules(+Layer, +Readings, +Tree, -Core, -Support)
        Core: the rule ids of the tree's rule nodes. Support: the further rules a reader consults
        through the absent and lemma leaves (the rules of their predicates' dependency closure),
        e.g. R309 for absent(denied(r)). An explanation must name Core and may name Support.
    tree_dict(+Tree, -Dict): the JSON form ({rule, goal, body} | {fact} | {builtin} | {absent} |
        {lemma} | {ite, branch, body}); goals as strings.
*/
:- module(why, [why/4, check_why/3, why_rules/5, tree_dict/2, full_readings/2]).
:- use_module(core).
:- use_module(library(apply)).
:- use_module(library(lists)).

max_depth(200).

%% full_readings(+Readings0, -Readings): one Fork-Reading pair per fork, as core:program/3 makes them.
full_readings(Rs0, Rs) :-
    decided_readings(Dec),
    findall(I-R, ( member(I-D, Dec), ( memberchk(I-R0, Rs0) -> R = R0 ; R = D ) ), Rs).

why(Layer, Rs0, G, Tree) :-
    full_readings(Rs0, Rs), program(Layer, Rs, M),
    C = ctx(Layer, Rs, M),
    once(( M:G, lit(G, C, 0, Tree) )).

%% lit(+Literal, +Ctx, +Depth, -Tree): Literal holds (it is called first), and Tree justifies it.
lit(G, ctx(_, _, M), _, lemma(G)) :- lemma_goal(G), !, M:G.
lit(G, ctx(_, _, M), _, fact(G)) :- base(G), !, M:G.
lit(G, _, _, builtin(G)) :- builtin(G), !, call(G).
lit(G, C, D, T) :-
    C = ctx(_, _, M),
    M:G,
    max_depth(Max),
    (   D >= Max -> T = lemma(G)
    ;   D1 is D + 1, once(( clause_of(C, Id, G, B), body(B, C, D1, Ts) )), T = rule(Id, G, Ts) ).

%% body(+Body, +Ctx, +Depth, -Trees)
body(true, _, _, []) :- !.
body((A, B), C, D, Ts) :- !, body(A, C, D, Ta), body(B, C, D, Tb), append(Ta, Tb, Ts).
body((If -> Then ; Else), C, D, [ite(If, Br)]) :- !,
    C = ctx(_, _, M),
    (   once(M:If)
    ->  body(If, C, D, TC), body(Then, C, D, TT), Br = then(TC, TT)
    ;   body(Else, C, D, TE), Br = else(TE) ).
body(\+ A, ctx(_, _, M), _, [absent(A)]) :- !, \+ M:A.
body(G, C, D, [T]) :- lit(G, C, D, T).

%% clause_of(+Ctx, -Id, ?Head, -Body): a clause of a rule allowed at the context's layer and readings.
clause_of(ctx(Layer, Rs, _), Id, H, B) :-
    functor(H, N, A),
    rule_rec(Id, N/A, L, _, _, _, Fork, _, Cs), L =< Layer,
    ( Fork == none -> true ; memberchk(Fork, Rs) ),
    member(Cl0, Cs), copy_term(Cl0, Cl),
    ( Cl = (H0 :- B) -> true ; H0 = Cl, B = true ),
    H = H0.

lemma_goal(G) :- compound(G), functor(G, N, A),
    memberchk(N/A, [aggregate_all/3, setof/3, bagof/3, findall/3, forall/2, member/2, memberchk/2]).
base(G) :- callable(G), functor(G, N, A), ( N/A == reading/2 ; rel_layer(N/A, _) ), !.
builtin(G) :- callable(G), predicate_property(system:G, built_in).

%% ---------- check ----------
check_why(Layer, Rs0, Tree) :-
    full_readings(Rs0, Rs), program(Layer, Rs, M),
    chk(Tree, ctx(Layer, Rs, M)).

chk(rule(Id, G, Ts), C) :- !,
    ground(G),
    once(( clause_of(C, Id, G, B), walk(B, Ts, []) )),
    maplist([T]>>chk(T, C), Ts).
chk(fact(G), ctx(Layer, Rs, _)) :- !,
    (   G = reading(F, R) -> memberchk(F-R, Rs)
    ;   functor(G, N, A), rel_layer(N/A, L), L =< Layer,
        ( schema_pred(N/A) -> core:schema_fact(Layer, G) ; core:wfact(G) ) ).
chk(builtin(G), _) :- !, call(G).
chk(absent(G), ctx(_, _, M)) :- !, \+ M:G.
chk(lemma(G), ctx(_, _, M)) :- !, once(M:G).
chk(ite(_, then(TC, TT)), C) :- !, maplist([T]>>chk(T, C), TC), maplist([T]>>chk(T, C), TT).
chk(ite(If, else(TE)), C) :- !, C = ctx(_, _, M), \+ M:If, maplist([T]>>chk(T, C), TE).

%% walk(+Body, +Trees0, -Trees): the body's literals, instantiated, are the goals of the trees in order.
walk(true, Ts, Ts) :- !.
walk((A, B), T0, T) :- !, walk(A, T0, T1), walk(B, T1, T).
walk((If -> Then ; Else), [ite(If, Br)|T], T) :- !,
    (   Br = then(TC, TT) -> walk(If, TC, []), walk(Then, TT, [])
    ;   Br = else(TE), walk(Else, TE, []) ).
walk(\+ A, [absent(A)|T], T) :- !.
walk(G, [N|T], T) :- node_goal(N, G).

node_goal(rule(_, G, _), G).
node_goal(fact(G), G).
node_goal(builtin(G), G).
node_goal(lemma(G), G).

%% ---------- rules of a tree ----------
why_rules(Layer, Rs0, Tree, Core, Support) :-
    full_readings(Rs0, Rs),
    phrase(nodes(Tree), Ns),
    findall(Id, member(r(Id), Ns), C0), sort(C0, Core),
    findall(PI, ( member(open(G), Ns), core:goal_preds(G, PIs), member(PI, PIs) ), P0),
    closure(P0, Cl),
    findall(Id, ( member(PI, Cl), rule_rec(Id, PI, L, _, _, _, Fork, _, _), L =< Layer,
                  ( Fork == none -> true ; memberchk(Fork, Rs) ) ), S0),
    sort(S0, S1), subtract(S1, Core, Support).

nodes(rule(Id, _, Ts)) --> [r(Id)], nodes_list(Ts).
nodes(absent(G)) --> [open(G)].
nodes(lemma(G)) --> [open(G)].
nodes(ite(If, then(TC, TT))) --> [open(If)], nodes_list(TC), nodes_list(TT).
nodes(ite(If, else(TE))) --> [open(If)], nodes_list(TE).
nodes(fact(_)) --> [].
nodes(builtin(_)) --> [].
nodes_list([]) --> [].
nodes_list([T|Ts]) --> nodes(T), nodes_list(Ts).

%% ---------- JSON form ----------
tree_dict(rule(Id, G, Ts), _{rule:Id, goal:S, body:Ds}) :- !, gs(G, S), maplist(tree_dict, Ts, Ds).
tree_dict(ite(If, then(TC, TT)), _{ite:S, branch:then, body:Ds}) :- !, gs(If, S), append(TC, TT, Ts), maplist(tree_dict, Ts, Ds).
tree_dict(ite(If, else(TE)), _{ite:S, branch:else, body:Ds}) :- !, gs(If, S), maplist(tree_dict, TE, Ds).
tree_dict(T, D) :- T =.. [K, G], gs(G, S), dict_pairs(D, _, [K-S]).
gs(G, S) :- copy_term(G, G1), numbervars(G1, 0, _), format(string(S), "~W", [G1, [quoted(true), numbervars(true)]]).
