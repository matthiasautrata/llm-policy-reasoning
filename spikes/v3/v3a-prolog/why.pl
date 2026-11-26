/*  V3a explanations: why-not trees and JSON-safe goals (CONTRACT.md "Why trees").

    explain_not(+Goal, +AsOf, -Node): an `absent` node for Goal whose children are, per candidate rule,
    a `rule` node with the body literals that held (`children`) and `failed`: the first literal that did
    not (recursively explained for derived literals, a 0-row fetch, a false builtin, a NAF literal whose
    goal is provable), or, when the body held, the `defeated_by` node of the attacker that won (or blocked).
    A live supporter of a goal refuted by defeat (its body contested, not refuted) also gets the `defeated_by`
    node: the defeat decided the goal, not the body (a contested literal is not absent).
    In-force claims asserting Goal that were defeated appear as `claim` nodes with a `defeated_by` child.
    Bodies are followed along their first solution (a documented simplification).
*/
:- module(why, [explain_not/3, json_safe/2]).
:- use_module(defeasible).
:- use_module(edn).

explain_not(G, D, _{type:absent, goal:GJ, children:Cs}) :-
    json_safe(G, GJ),
    ( ground(G) -> evaluate(G, D, E) ; E = none([]) ),
    findall(N, ( rule(Id, K, H, _, _), memberchk(K, [strict, defeasible]), active(Id),
                 \+ \+ H = G, explain_rule(Id, G, D, E, N) ), Rs),
    findall(N, ( ground(G), claim_node(G, D, E, N) ), Cl),
    append(Rs, Cl, Cs).

explain_rule(Id, G0, D, E, _{type:rule, id:Id, goal:GJ, children:Kids, failed:F}) :-
    copy_term(G0, G),
    rule(Id, _, G, B, _),
    walk(B, D, [], R),
    (   R = ok(Done) -> reverse(Done, Kids), defeat_node(Id, E, F)
    ;   R = failed(Done, F0), E = defeated(_, Ss, _), memberchk(s(Id, _, _), Ss)
    ->  reverse(Done, Kids), defeat_node(Id, E, F)
    ;   R = failed(Done, F0), reverse(Done, Kids), F = F0 ),
    json_safe(G, GJ).

walk([], _, Done, ok(Done)).
walk([L|Ls], D, Done, R) :-
    (   lit(L, D, K) -> walk(Ls, D, [K|Done], R)
    ;   failed_lit(L, D, F), R = failed(Done, F) ).

failed_lit([fetch, C, map(F), map(_)], _, Node) :- !,
    (   forall(member(_-V, F), ground(V))
    ->  fetch_rows(C, F, Rows, Info, FD), length(Rows, N),
        Node = Info.put(_{type:fetch, concept:C, filters:FD, rows:N, row:null})
    ;   json_safe([fetch, C], J), Node = _{type:absent, goal:J} ).
failed_lit([not, L], D, _{type:absent, goal:[not, LJ], children:[P]}) :- !,
    once(prove(L, D, P)), json_safe(L, LJ).
failed_lit([Op|As], _, _{type:fact, goal:J, holds:false}) :-
    memberchk(Op, [<, <=, >, >=, =, is, as_of]), !, json_safe([Op|As], J).
failed_lit(L, D, N) :- explain_not(L, D, N).

% the body held: say who defeated or blocked the conclusion
defeat_node(Id, defeated(a(AId, _, _, AP), _, _), _{type:defeated_by, id:AId, target:Id, children:[AP|Sn]}) :- !,
    findall(_{type:superior, winner:AId, loser:Id, source:S}, once(sup(AId, Id, S)), Sn).
defeat_node(Id, blocked(_, [a(AId, _, _, AP)|_]), _{type:defeated_by, id:AId, target:Id, children:[AP], blocked:true}) :- !.
defeat_node(_, _, null).

claim_node(G, D, E, N) :-
    E \= proven(_, _), E \= none(_),
    claim(Id, G, By, At, F, T, _, _, _, _), active(Id), in_force(F, T, D),
    defeat_node(Id, E, DN), DN \== null,
    N = _{type:claim, id:Id, goal:G, asserted_by:By, asserted_at:At, children:[DN]}.

%!  json_safe(+T0, -T): unbound variables become "?_N" strings so any goal can be written as JSON.
json_safe(T0, T) :- copy_term(T0, T1), numbervars(T1, 0, _), js(T1, T).
js('$VAR'(N), S) :- !, format(string(S), "?_~w", [N]).
js(L, J) :- is_list(L), !, maplist(js, L, J).
js(map(Ps), D) :- !, maplist([K-V, K-W]>>js(V, W), Ps, Qs), dict_pairs(D, _, Qs).
js(X, X).
