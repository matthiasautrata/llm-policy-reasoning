/*  V3a evaluator: defeasible logic (Nute / Governatori style) over EDN rules and Toulmin claims.

    Store (dynamic, asserted from slice.edn / extension.edn / add / with_hypothesis):
      rule(Id, Kind, Head, Body, Meta)        Kind: strict | defeasible | defeater | superiority | incompatible
      claim(Id, Assertion, By, At, From, To, About, null, null, Meta)   flat; links: claim_link/3
      functional(Pred, KeyArity)  concept(Name, Map)  term(Id, Map)  today(Date)  withheld(Id)

    Literals are lists [Pred|Args]; [neg, L] is the complement. evaluate/3 decides a ground literal
    (memo mode: ambiguity propagation, shared/SEMANTICS.md; each literal proven, refuted or contested):
      proven(Sups, SupNodes)   a proven-bodied supporter, every live attacker beaten by a superior
                               proven-bodied supporter (team defeat)                     -- proven
      defeated(A, Sups, DN)    every live supporter beaten by a superior proven-bodied attacker; A the
                               smallest such attacker id                                 -- refuted
      none(Atts)               no live supporter                                         -- refuted
      blocked(Sups, Unbeaten)  a root conflict: proven-bodied supporters meet proven-bodied unbeaten
                               attackers                                                 -- contested
      contested(Rules, Via)    downstream: contested only through contested body literals Via of the
                               live supporters / live unbeaten attackers Rules           -- contested
    Live = body not refuted (body3/5 gives proven or contested solutions).
    Supporters: active strict/defeasible rules whose body is provable, in-force claims. Attackers: the same
    for the complement and, for functional predicates, for the same key with another value; defeaters
    attack only. Superiority: explicit :superior-to, strict over non-strict, asserter authority (a
    :superiority rule, scoped to its :pred), later asserted_at for the same asserter.
    Memoised per op and state (memo/5), cleared whenever the rule/claim set changes.

    evaluate/3 recurses through the live supporters/attackers (eval3/3). A dependency cycle the integrity
    gate missed (INTEGRITY_GATE=off) hits the re-entry guard.
*/
:- module(defeasible, [eval3/3, body3/5, candidate3/2, value3/2, contested_info/5, load_file/1, add_records/3, retract_source/1, evaluate/3, prove/3, body/3, lit/3,
                       sup/3, in_force/3, active/1, clear_memo/0, pred_of/2,
                       state_token/1, with_state/2, memo/5, clear_fetched/0,
                       fetch_rows/5, cmp_lit/1, ev/2, ids_of/2, derived_lit/1,
                       rule/5, claim/10, claim_link/3, top_claim/2, functional/2, concept/2, term/2, today/1, withheld/1, slice/1, asset/2, src/2]).
:- use_module(edn).
:- thread_local fetched/4, needed/1.
:- use_module(library(janus)).
:- use_module(library(json)).

:- dynamic rule/5, rule_at/2, claim/10, claim_link/3, top_claim/2, functional/2, concept/2, term/2, today/1, withheld/1, memo/5, slice/1, asset/2, src/2.

%   Memo entries are keyed by a state token: `base`, or hyp(N) inside the N-th hypothesis. The token is a
%   global variable, which SWI keeps per thread. Under snapshot/1, entries asserted inside the hypothesis are
%   discarded with it; entries the base asserted before the snapshot stay visible inside it, and the key keeps
%   them from being used there (tested by ops:memo_test/1).

:- meta_predicate with_state(+, 0).
state_token(S) :- ( nb_current(v3a_state, S0) -> S = S0 ; S = base ).
with_state(S, G) :- state_token(Old), setup_call_cleanup(nb_setval(v3a_state, S), G, nb_setval(v3a_state, Old)).

% ------------------------------------------------------------------ loading

load_file(File) :-
    edn_read_file(File, T),
    (   T = map(_) -> load_slice(T)
    ;   is_list(T) -> add_records(T, ext, _) ).

load_slice(M) :-
    assertz(slice(M)),
    mget(today, M, D), assertz(today(D)),
    mget(functional, M, map(Fs)), forall(member(P-N, Fs), assertz(functional(P, N))),
    mget(concepts, M, Cs),
    forall(member(C, Cs), ( mget(name, C, N), assertz(concept(N, C)),
                            (   mget(sql, C, Sql) -> mget(params, C, Ps, []), mget(batch_sql, C, BSql, @(none)),
                                py_call(sql:register(N, Sql, Ps, BSql), _)
                            ;   true ) )),
    mget(terms, M, Ts), forall(member(T, Ts), ( mget(id, T, Id), assertz(term(Id, T)) )),
    mget(assets, M, As, []), forall(member(A, As), ( mget(id, A, Id), assertz(asset(Id, A)) )),
    mget(rules, M, Rs), mget(claims, M, Cl),
    append(Rs, Cl, Recs), add_records(Recs, base, _).

%!  add_records(+Maps, +Source, -Ids)
add_records(Recs, Src, Ids) :-
    foldl(add_record(Src), Recs, [], Ids0), reverse(Ids0, Ids), clear_memo.

add_record(Src, M, Ids0, [Id|Ids0]) :-
    mget(id, M, Id),
    (   mget(assertion, M, _) -> add_claim(M, Src)
    ;   edn_vars(M, MV), mget(kind, MV, K), mget(head, MV, H, none), mget(body, MV, B, []),
        assertz(rule(Id, K, H, B, MV)), assertz(src(Id, Src)),
        ( head_key(H, HK) -> assertz(rule_at(HK, Id)) ; true ) ).

%   rule_at(Key, Id) indexes rules by head (Key: the predicate, neg(P) for a complement), in load order, so a
%   lookup by head is not a scan of every rule. head_rule/2 falls back to the scan for a head with no key.
head_key(H, K) :- nonvar(H), H = [P|T], atom(P),
    (   P == neg -> T = [X], nonvar(X), X = [Q|_], atom(Q), K = neg(Q) ; K = P ).
head_rule(H, Id) :- ( head_key(H, K) -> rule_at(K, Id) ; rule(Id, _, _, _, _) ).

%   Claims are flat (PLAN-v3-integrity §1): a claim links its members by id, :depends_on (role required)
%   and :supports (role supporting). The Parent and Role arguments of claim/10 stay null; claim_link/3
%   gives the links and top_claim/2 the claims no active claim links to.
add_claim(M, Src) :-
    mget(id, M, Id), mget(assertion, M, A), mget(asserted_by, M, By), mget(asserted_at, M, At),
    mget(valid_from, M, F), mget(valid_to, M, T, null), mget(about, M, About),
    assertz(claim(Id, A, By, At, F, T, About, null, null, M)), assertz(src(Id, Src)).

claim_link(P, C, Role) :-
    claim(P, _, _, _, _, _, _, _, _, M),
    (   mget(depends_on, M, L, []), Role = required ; mget(supports, M, L, []), Role = supporting ),
    member(C, L).

linked(C) :- claim_link(P, C, _), active(P), !.          % a withheld parent no longer hides its members
top_claim(Id, About) :- claim(Id, _, _, _, _, _, About, _, _, _), \+ linked(Id).

retract_source(Src) :-
    forall(src(Id, Src), ( retractall(rule(Id, _, _, _, _)), retractall(rule_at(_, Id)), retractall(claim(Id, _, _, _, _, _, _, _, _, _)) )),
    retractall(src(_, Src)), clear_memo.

%   clear_memo runs at the start of every op.
clear_memo :- retractall(memo(_, _, _, _, _)).

%   memo(Hash, State, AsOf, Key, Result): Hash = variant_hash(Key) gives first-argument indexing (Key is a
%   list or an agg/3 term with variables, which SWI does not index on).
memo_get(S, D, K, R) :- variant_hash(K, H), memo(H, S, D, K0, R0), K0 =@= K, !, R = R0.
memo_put(S, D, K, R) :- variant_hash(K, H), assertz(memo(H, S, D, K, R)).

active(Id) :- \+ withheld(Id).

% ------------------------------------------------------------------ evaluation

%!  prove(?L, +AsOf, -Proof) is nondet.   L defeasibly provable (+∂); binds L to each proven instance.
prove(L, D, P) :- ground(L), !,
    evaluate(L, D, proven(Sups, SupN)), Sups = [s(_, _, P0)|_], with_children(P0, SupN, P).
prove(L, D, P) :-
    findall(L, candidate3(L, D), Ls0), sort(Ls0, Ls),
    member(L, Ls), ground(L),
    evaluate(L, D, proven(Sups, SupN)), Sups = [s(_, _, P0)|_], with_children(P0, SupN, P).

with_children(P0, Extra, P) :- get_dict(children, P0, Cs0), append(Cs0, Extra, Cs), put_dict(children, P0, Cs, P).

evaluate(L, D, R) :- state_token(S), memo_get(S, D, L, R0), !, R = R0.
evaluate(L, D, R) :- round(Rd), state_token(S), memo_get(S, D, missed(Rd, L), R0), !, miss, R = R0.
evaluate(L, D, R) :-
    guard_path(P),
    (   append(Pre, [D-L|_], P) -> append(Pre, [D-L], Seg), cycle_goals(Seg, Path), throw(defeat_cycle(Path)) ; true ),
    misses(M0),
    setup_call_cleanup(nb_setval(v3a_guard, [D-L|P]),
                       once(eval3(L, D, R0)),          % R0 fresh: callers pass patterns like proven(_, _)
                       nb_setval(v3a_guard, P)),
    state_token(S), memo_unless_missed(M0, S, D, L, R0), R = R0.

%   Collect mode (CONTRACT.md, Aggregates): a fetch inside an aggregate that misses the cache counts a
%   miss and fails. A result computed while a miss happened is memoised for the current round only, as
%   missed(Round, L), and replaying it counts a miss again; the next round recomputes it.
misses(M) :- ( nb_current(v3a_miss, M0), integer(M0) -> M = M0 ; M = 0 ).
miss :- misses(M), M1 is M + 1, nb_setval(v3a_miss, M1).
round(Rd) :- nb_current(v3a_round, Rd), integer(Rd).
memo_unless_missed(M0, S, D, L, R0) :-
    (   misses(M0) -> memo_put(S, D, L, R0)
    ;   round(Rd) -> memo_put(S, D, missed(Rd, L), R0)
    ;   true ).

%   Re-entry guard (PLAN-v3-integrity §3.2): a literal whose evaluation is in progress (same
%   as_of) is being evaluated again, i.e. the rule base has a dependency cycle the integrity gate did not
%   stop (INTEGRITY_GATE=off). A backstop, not a semantics: throws defeat_cycle(GoalPath).
guard_path(P) :- ( nb_current(v3a_guard, P0), P0 \== [] -> P = P0 ; P = [] ).
cycle_goals(Seg, Path) :-          % Seg: the guard stack (innermost first) down to the first entry of the goal
    reverse(Seg, Outer), maplist([_-G, G]>>true, Outer, Path0), Path0 = [G0|_], append(Path0, [G0], Path).

rival([neg, X], X, true) :- !.
rival(L, [neg, L], true).
rival([P|Args], [P|Rival], diff(V, V2)) :-
    functional(P, N), length(Args, Len), Len =:= N + 1,
    length(Key, N), append(Key, [V], Args), append(Key, [V2], Rival).

differs(true).
differs(diff(V, V2)) :- V \== V2.

%!  sup(+Winner, +Loser, -Source) is nondet.
sup(W, L, explicit) :- rule(W, _, _, _, M), mget('superior-to', M, Ls), memberchk(L, Ls).
sup(W, L, strict) :- rule(W, strict, _, _, _), \+ rule(L, strict, _, _, _).
sup(W, L, Src) :-
    claim(W, AW, ByW, _, _, _, _, _, _, _), claim(L, AL, ByL, _, _, _, _, _, _, _), ByW \== ByL,
    pred_of(AW, P), pred_of(AL, P),
    rule(SId, superiority, _, _, M), active(SId), mget(pred, M, P), mget(order, M, O),
    nth0(IW, O, ByW), nth0(IL, O, ByL), IW < IL,
    format(atom(Src), 'authority:~w', [SId]).
sup(W, L, later) :-
    claim(W, _, By, AtW, _, _, _, _, _, _), claim(L, _, By, AtL, _, _, _, _, _, _), AtW @> AtL.

pred_of([neg, X], P) :- !, pred_of(X, P).
pred_of([P|_], P).

in_force(F, T, D) :- F @=< D, ( T == null -> true ; D @=< T ).

% ------------------------------------------------------------------ ambiguity propagation

%!  eval3(+L, +D, -R)  SEMANTICS.md over the live supporters / attackers of ground L.
%   Entries: s(Id, K, Proof)-V-CL and a(Id, K, Head, Proof)-V-CL; V proven | contested (body value), CL the
%   contested body literals ([:not X] as X).
eval3(L, D, R) :-
    findall(s(Id, K, P)-V-CL, live_sup(L, D, Id, K, P, V, CL), S),
    findall(a(Id, K, H, P)-V-CL, live_att(L, D, Id, K, H, P, V, CL), A0), dedup_e(A0, A),
    classify3(S, A, R).

live_sup(L, D, Id, K, _{type:rule, id:Id, goal:L, children:Kids}, V, CL) :-
    head_rule(L, Id), rule(Id, K, L0, _, _), memberchk(K, [strict, defeasible]), active(Id), \+ L0 \= L,
    best_sol(Id, L, D, true, V, Kids, CL).
live_sup(L, D, Id, claim, P, proven, []) :-
    claim(Id, L, By, At, F, T, _, _, _, _), active(Id), in_force(F, T, D),
    P = _{type:claim, id:Id, goal:L, asserted_by:By, asserted_at:At, children:[]}.

live_att(L, D, Id, K, H, _{type:rule, id:Id, goal:H, children:Kids}, V, CL) :-
    rival(L, H0, Diff0),
    head_rule(H0, Id), rule(Id, K, Hr, _, _), memberchk(K, [strict, defeasible, defeater]), active(Id),
    copy_term(H0-Diff0, H-Diff), \+ Hr \= H,
    best_sol(Id, H, D, differs(Diff), V, Kids, CL).
live_att(L, D, Id, incompatible, [neg, L], _{type:rule, id:Id, goal:[neg, L], children:Kids}, V, CL) :-
    head_rule(L, Id), rule(Id, incompatible, Hr, _, _), active(Id), \+ Hr \= L,    % R314: a declared incompatibility attacks its head
    best_sol(Id, L, D, true, V, Kids, CL).
live_att(L, D, Id, claim, H, P, proven, []) :-
    rival(L, H0, Diff0), copy_term(H0-Diff0, H-Diff),
    claim(Id, H, By, At, F, T, _, _, _, _), active(Id), in_force(F, T, D), differs(Diff),
    P = _{type:claim, id:Id, goal:H, asserted_by:By, asserted_at:At, children:[]}.

%   A proven body solution if there is one, else a contested one (binds H on the way).
best_sol(Id, H, D, Chk, V, Kids, CL) :-
    (   once(( rule(Id, _, H, B, _), body3(B, D, Kids, proven, CL), call(Chk) )) -> V = proven
    ;   once(( rule(Id, _, H, B, _), body3(B, D, Kids, contested, CL), call(Chk) )) -> V = contested ).

dedup_e([], []).
dedup_e([E|Es], [E|Fs]) :- eid(E, Id), exclude([X]>>eid(X, Id), Es, Rest), dedup_e(Rest, Fs).

eid(T-_-_, Id) :- arg(1, T, Id).
eterm(T-_-_, T).
eproven(_-proven-_).

beats_e(Es, Loser, W, Src) :- member(E, Es), eproven(E), eid(E, W), sup(W, Loser, Src).

classify3([], A, none(As)) :- !, maplist(eterm, A, As).
classify3(S, A, R) :-
    maplist(eterm, S, Ss),
    (   forall(member(T, S), ( eid(T, TId), beats_e(A, TId, _, _) ))       % -sigma, team form
    ->  findall(W, ( member(T, S), eid(T, TId), beats_e(A, TId, W, _) ), Ws), sort(Ws, [W1|_]),
        once(( member(AE, A), eid(AE, W1) )), eterm(AE, Def),
        findall(_{type:superior, winner:W, loser:TId, source:Src},
                ( member(T, S), eid(T, TId), once(beats_e(A, TId, W, Src)) ), DN),
        R = defeated(Def, Ss, DN)
    ;   include(eproven, S, Sp0), maplist(eterm, Sp0, Sp),
        partition([AE]>>( eid(AE, AId), beats_e(S, AId, _, _) ), A, _, Un),
        (   Sp \== [], Un == []
        ->  findall(_{type:superior, winner:W, loser:AId, source:Src},
                    ( member(AE, A), eid(AE, AId), once(beats_e(S, AId, W, Src)) ), SupN),
            R = proven(Sp, SupN)
        ;   include(eproven, Un, Ap0), Sp \== [], Ap0 \== []
        ->  maplist(eterm, Ap0, Ap), R = blocked(Sp, Ap)
        ;   append(S, Un, Live), maplist(eid, Live, Rs0), sort(Rs0, Rs),
            findall(X, ( member(_-_-CL, Live), member(X, CL) ), Vs0), sort(Vs0, Vs),
            R = contested(Rs, Vs) ) ).

%!  value3(+E, -V)  proven | refuted | contested
value3(proven(_, _), proven).
value3(defeated(_, _, _), refuted).
value3(none(_), refuted).
value3(blocked(_, _), contested).
value3(contested(_, _), contested).

%!  body3(+B, +D, -Kids, ?V, -CL) is nondet.  A live solution of body B: V proven | contested.
body3([], _, [], proven, []).
body3([L|Ls], D, [K|Ks], V, CL) :-
    lit3(L, D, K, V1, C1), body3(Ls, D, Ks, V2, C2),
    ( V1 == proven, V2 == proven -> V = proven ; V = contested ), append(C1, C2, CL).

lit3([not, X], D, N, V, CL) :- ground(X), !,
    evaluate(X, D, E), value3(E, V0),
    (   V0 == refuted -> V = proven, CL = [], N = _{type:absent, goal:X}
    ;   V0 == contested -> V = contested, CL = [X], N = _{type:contested_lit, goal:X} ).
lit3([agg, Op, X, B, Out], D, N, V, CL) :- !,
    agg3(Op, X, B, D, Val, N, V, CL), Out = Val.
lit3(L, D, N, V, CL) :- derived_lit(L), !,
    (   ground(L) -> Ls = [L] ; findall(L, candidate3(L, D), Ls0), sort(Ls0, Ls) ),
    member(L, Ls), evaluate(L, D, E), value3(E, V0),
    (   V0 == proven -> V = proven, CL = [], once(prove(L, D, N))
    ;   V0 == contested -> V = contested, CL = [L], N = _{type:contested_lit, goal:L} ).
lit3(L, D, N, proven, []) :- lit(L, D, N).

derived_lit([P|_]) :- \+ memberchk(P, [fetch, not, as_of, is, <, <=, >, >=, =, agg]).

%!  agg3(+Op, ?X, +B, +D, -Val, -Node, -V, -CL)  SEMANTICS.md, Aggregates: members are the proven solutions
%   (distinct bindings of B's local variables); any contested solution contests the literal (CL: the
%   contested literals of those solutions), and Val is then the aggregate over the proven members only.
%   Memoised per op and state like evaluate/3. B is evaluated set-at-a-time in rounds (CONTRACT.md,
%   Aggregates): the outermost aggregate repeats the findall, flushing the recorded fetch needs as batches
%   after each round with a miss, until a round has none; a nested one runs once inside the outer round.
agg3(Op, X, B, D, Val, N, V, CL) :-
    copy_term(agg(Op, X, B), K), state_token(S),
    (   memo_get(S, D, agg(K), R0) -> true
    ;   round(Rd), memo_get(S, D, missed(Rd, agg(K)), R0) -> miss
    ;   term_variables(B, Loc),
        agg_depth(Depth), Depth1 is Depth + 1, misses(M0),
        setup_call_cleanup(nb_setval(v3a_agg, Depth1),
                           agg_rounds(Depth, Loc-X-V1-Kids-C1, body3(B, D, Kids, V1, C1), Sols0),
                           nb_setval(v3a_agg, Depth)),
        agg_group(Sols0, Mem, Cont),
        maplist([_-Xi-_-_-_, Xi]>>true, Mem, Xs),
        (   Op == sum -> sum_list(Xs, Val0) ; length(Xs, Val0) ),
        maplist([_-Xi-_-Ki-_, _{value:Xi, children:Ki}]>>true, Mem, MNs),
        findall(Y, ( member(_-_-_-_-C1, Cont), member(Y, C1) ), CL0), sort(CL0, CL1),
        ( Cont == [] -> V0 = proven ; V0 = contested ),
        R0 = r(Val0, _{type:aggregate, op:Op, value:Val0, members:MNs}, V0, CL1),
        memo_unless_missed(M0, S, D, agg(K), R0) ),
    R0 = r(Val, N, V, CL).

agg_rounds(Depth, T, G, Sols) :-
    (   Depth =:= 0
    ->  setup_call_cleanup(true, agg_round(T, G, Sols),
                           ( nb_setval(v3a_round, none), retractall(memo(_, _, _, missed(_, _), _)) ))
    ;   findall(T, G, Sols) ).

agg_round(T, G, Sols) :-
    flag(v3a_round, Rd, Rd + 1), nb_setval(v3a_round, Rd),
    misses(M0), findall(T, G, Sols0),
    (   misses(M0) -> Sols = Sols0
    ;   nb_setval(v3a_miss, M0), retractall(memo(_, _, _, missed(Rd, _), _)),
        retractall(needed(_)), py_call(sql:flush(), _), agg_round(T, G, Sols) ).

agg_depth(V) :- ( nb_current(v3a_agg, V0), integer(V0) -> V = V0 ; V = 0 ).

%   One entry per distinct binding, in binding order: the first proven solution under it, else the first
%   contested one. Grouped by keysort (stable), not by list search: the root has ~90k members.
agg_group(Sols, Mem, Cont) :-
    numbered(Sols, 0, Ns), keysort(Ns, Sorted), group_pairs_by_key(Sorted, Groups),
    maplist(pick_sol, Groups, Picked0), keysort(Picked0, Picked), pairs_values(Picked, Best),
    partition([_-_-V-_-_]>>(V == proven), Best, Mem, Cont).

numbered([], _, []).
numbered([E|Es], I, [Loc-(I-E)|Ns]) :- E = Loc-_-_-_-_, I1 is I + 1, numbered(Es, I1, Ns).

pick_sol(_-IEs, P) :-
    (   member(P, IEs), P = _-(_-_-proven-_-_) -> true ; IEs = [P|_] ).

%!  candidate3(?L, +D)  a ground instance of L with a live supporter
candidate3(L, D) :-
    (   head_rule(L, Id), rule(Id, K, L, B, _), memberchk(K, [strict, defeasible]), active(Id), body3(B, D, _, _, _)
    ;   claim(Id, L, _, _, F, T, _, _, _, _), active(Id), in_force(F, T, D) ),
    ground(L).

%!  contested_info(+G, +D, -Via, -Rules, -Roots)  for a downstream-contested G (SEMANTICS.md, why tree):
%   Via every contested literal reached through contested body literals, Rules the live supporters /
%   unbeaten attackers of G and the non-root Via literals, Roots [Goal-Sides-SideProofs] per root.
contested_info(G, D, Via, Rules, Roots) :-
    cwalk([G], D, [], [], [], [], V0, Ru0, Ro0),
    sort(V0, Via), sort(Ru0, Rules), sort(Ro0, Roots).

cwalk([], _, _, V, Ru, Ro, V, Ru, Ro).
cwalk([X|Xs], D, Seen, V0, Ru0, Ro0, V, Ru, Ro) :-
    (   memberchk(X, Seen) -> cwalk(Xs, D, Seen, V0, Ru0, Ro0, V, Ru, Ro)
    ;   evaluate(X, D, E),
        (   E = blocked(Sp, Ap)
        ->  ids_of(Sp, I1), ids_of(Ap, I2), sort([I1, I2], Sides),
            maplist([s(_, _, P), P]>>true, Sp, P1), maplist([a(_, _, _, P), P]>>true, Ap, P2), append(P1, P2, Ps),
            cwalk(Xs, D, [X|Seen], V0, Ru0, [X-Sides-Ps|Ro0], V, Ru, Ro)
        ;   E = contested(Rs, Vs)
        ->  append(Rs, Ru0, Ru1), append(Vs, V0, V1), append(Xs, Vs, Q),
            cwalk(Q, D, [X|Seen], V1, Ru1, Ro0, V, Ru, Ro)
        ;   cwalk(Xs, D, [X|Seen], V0, Ru0, Ro0, V, Ru, Ro) ) ).

% ------------------------------------------------------------------ rule bodies

body([], _, []).
body([L|Ls], D, [K|Ks]) :- lit(L, D, K), body(Ls, D, Ks).

lit([fetch, C, map(F), map(O)], _, Node) :- !,
    fetch_rows(C, F, Rows, Info, Filters),
    length(Rows, N),
    member(Row, Rows),
    maplist([Col-V]>>get_dict(Col, Row, V), O),
    Node = Info.put(_{type:fetch, concept:C, filters:Filters, rows:N, row:Row}).
lit([not, L], D, _{type:absent, goal:L}) :- !,           % L refuted (a contested L is not absent)
    (   ground(L) -> evaluate(L, D, E), value3(E, refuted) ; \+ prove(L, D, _) ).
lit([as_of, X], D, _{type:fact, goal:[as_of, D]}) :- !, X = D.
lit([is, X, E], _, _{type:fact, goal:[is, V, E1]}) :- !, ev(E, V), X = V, inst(E, E1).
lit([Op, A, B], _, _{type:fact, goal:[Op, A1, B1]}) :- cmp_op(Op), !, inst(A, A1), inst(B, B1), cmp_lit([Op, A1, B1]).
lit([agg|T], D, N) :- !, lit3([agg|T], D, N, proven, _).
lit(L, D, P) :- prove(L, D, P).

cmp_op(Op) :- memberchk(Op, [<, <=, >, >=, =]).
inst(X, X).   % arguments are bound by the time a builtin runs (left-to-right bodies)

cmp_lit([Op, A, B]) :-
    ev(A, X), ev(B, Y),
    (   number(X), number(Y) -> num_cmp(Op, X, Y)
    ;   compare(O, X, Y), ord_ok(Op, O) ).
num_cmp(<, X, Y) :- X < Y.   num_cmp(<=, X, Y) :- X =< Y.  num_cmp(>, X, Y) :- X > Y.
num_cmp(>=, X, Y) :- X >= Y. num_cmp(=, X, Y) :- X =:= Y.
ord_ok(<, <). ord_ok(<=, <). ord_ok(<=, =). ord_ok(>, >). ord_ok(>=, >). ord_ok(>=, =). ord_ok(=, =).

ev(X, X) :- ( number(X) ; string(X) ; atom(X) ), !.
ev([+, A, B], V) :- !, ev(A, X), ev(B, Y), V is X + Y.
ev([-, A, B], V) :- !, ev(A, X), ev(B, Y), V is X - Y.

%!  fetch_rows(+Concept, +FilterPairs, -Rows, -Info, -FilterDict)
%   Calls the SQL boundary (sql.py) with ground filters; Info carries sql and params for the why tree.
fetch_rows(C, F, Rows, _{sql:Sql, params:Ps, truncated:Tr}, FD) :-
    (   forall(member(_-V, F), ground(V)) -> true
    ;   throw(error(fetch_unbound(C, F), _)) ),
    dict_pairs(FD, _, F),
    ( agg_depth(Dp), Dp > 0 -> Agg = true ; Agg = false ),
    variant_hash(C-FD, H),
    (   fetched(H, C, FD, R), ( Agg == false ; R.truncated == false ) -> true
    ;   with_output_to(string(J), json_write_dict(current_output, FD, [width(0)])),
        (   Agg == true                                % collect mode: a miss records the need and fails
        ->  ( needed(H) -> miss, fail ; true ),
            py_call(sql:need(C, J), Out), ( ( Out == '' ; Out == "" ) -> assertz(needed(H)), miss, fail ; true )
        ;   py_call(sql:fetch(C, J), Out) ),
        atom_json_dict(Out, R, [value_string_as(string)]),
        retractall(fetched(H, C, FD, _)), assertz(fetched(H, C, FD, R)) ),
    Rows = R.rows, Sql = R.sql, Ps = R.params, Tr = R.truncated.

%   The parsed per-op fetch cache (mirrors sql.py's, so a repeated literal does not cross janus again).
clear_fetched :- retractall(fetched(_, _, _, _)), retractall(needed(_)).

ids_of(Xs, Ids) :- maplist([X, Id]>>arg(1, X, Id), Xs, Ids0), sort(Ids0, Ids).
