/*  V3a System A surface (CONTRACT.md): run_op(+OpJSON, -ResultJSON).
    decide, why_not, claims, resolve_term, describe, fetch, rules, summary, add, with_hypothesis.
*/
:- module(ops, [run_op/2, load_files_json/1, set_hyp_mode/1, run_concurrent/2, memo_test/1]).
:- use_module(edn).
:- use_module(defeasible).
:- use_module(why).
:- use_module(library(janus)).
:- discontiguous do_op/3.
:- use_module(library(json)).

load_files_json(J) :-
    atom_json_term(J, Fs, [value_string_as(string)]),
    forall(member(F, Fs), load_file(F)).

run_op(J, Out) :-
    atom_json_dict(J, Op, [value_string_as(string)]),
    op_result(Op, R),
    with_output_to(string(Out), json_write_dict(current_output, R, [width(0)])).

op_result(Op, R) :-
    py_call(sql:begin_op(), _), clear_fetched, clear_memo,
    get_time(T0),
    catch(do_op(Op.op, Op, R0), E, op_error(Op.op, E, R0)),
    get_time(T1), Ms is (T1 - T0) * 1000,
    py_call(sql:take_log(), LogJ), atom_json_dict(LogJ, Log, [value_string_as(string)]),
    ( Op.op == "with_hypothesis" -> L = [] ; L = Log ),
    R = R0.put(_{ms:Ms, sql_log:L}).

%   The re-entry guard (defeasible:evaluate/3, memo mode) throws defeat_cycle(Path): reported in the
%   integrity gate's format, members = the goals on the cycle, outermost first.
op_error(Op, defeat_cycle(Path), _{status:"ERROR", error:_{op:Op, violations:[V]}}) :- !,
    maplist([G, S]>>format(string(S), "~w", [G]), Path, Ms),
    atomic_list_concat(Ms, ' -> ', Msg0), format(string(Msg), "re-entered ~w (goal path ~w)", [Path, Msg0]),
    V = _{violation:"defeat-cycle", members:Ms, path:Path, message:Msg}.
op_error(_, E, _{status:"ERROR", error:S}) :- message_to_codes(E, S).

message_to_codes(E, S) :- message_to_codes(E, [], Cs), !, string_codes(S, Cs).
message_to_codes(E, S) :- format(string(S), "~q", [E]).
message_to_codes(E, _, Cs) :- '$messages':translate_message(E, Ls, []), with_output_to(codes(Cs), print_message_lines(current_output, '', Ls)).

as_of(Op, D) :- ( get_dict(as_of, Op, D0) -> atom_string(D0, D) ; today(D) ).

% ------------------------------------------------------------------ decide

do_op("decide", Op, R) :- !, as_of(Op, D), edn_parse(Op.goal, G0), edn_vars(G0, G), decide(G, D, R).
do_op("why_not", Op, R) :- !, as_of(Op, D), edn_parse(Op.goal, G0), edn_vars(G0, G), why_not(G, D, R).

decide(G, D, R) :-
    pred_of(G, P),
    (   \+ known_pred(P) -> scope(P, St), R = _{status:St, value:null, sides:null, why:[], owners:[], qualifier:null}
    ;   ground(G) -> decide_ground(G, D, R)
    ;   decide_open(G, D, R) ).

known_pred(P) :- rule(Id, _, H, _, _), active(Id), H \== none, pred_of(H, P), !.
known_pred(P) :- claim(Id, A, _, _, _, _, _, _, _, _), active(Id), pred_of(A, P), !.

scope(P, St) :- format(string(T), "term:~w", [P]), ( term(T, _) -> St = "UNDERDETERMINED" ; St = "OUT_OF_SCOPE" ).

decide_ground(G, D, R) :-
    evaluate(G, D, E),
    (   E = proven(Sups, SupN)
    ->  team_proofs(Sups, SupN, Why), answer("ANSWER", true, null, Why, D, R)
    ;   E = blocked(Sups, Un)
    ->  ids_of(Sups, A), ids_of(Un, B), sort([A, B], Sides),
        maplist([s(_, _, P), P]>>true, Sups, W1), maplist([a(_, _, _, P), P]>>true, Un, W2), append(W1, W2, Why),
        answer("CONFLICT", null, Sides, Why, D, R)
    ;   E = contested(_, _)                            % downstream of a root conflict
    ->  contested_why(G, D, Sides, Node), answer("CONFLICT", null, Sides, [Node], D, R)
    ;   explain_not(G, D, N), absence(G, D, E, Abs), answer("ANSWER", false, null, [N], Abs, D, R) ).

%!  absence(+G, +D, +E, -Abs)  SEMANTICS.md, Qualifier: a refuted ground G rests on absence when no supporter
%   was live, or when the winning attacker's proof uses a :closed_over rule; an open G with no binding
%   always (E = open). Not when an in-force [:complete "P"] claim covers G's predicate.
absence(G, D, _, false) :- pred_of(G, P), covered(P, D), !.
absence(_, _, none(_), true) :- !.
absence(_, _, open, true) :- !.
absence(_, D, defeated(a(_, _, _, Pf), _, _), true) :- why_ids([Pf], Ids), uses_uncovered_closed(Ids, D), !.
absence(_, _, _, false).

%!  covered(+N, +D)  SEMANTICS.md, Qualifier (IR-005, amended 2026-11-25): N (a predicate or a fetch
%   concept) is covered when an in-force [:complete "N"] claim names it, or when N is a predicate no active
%   claim asserts, some active rule concludes or attacks it, and every such rule's body is covered. A
%   predicate met again on the path counts as covered.
covered(N, D) :- covered(N, D, []).
covered(N, D, _) :- complete(N, D), !.
covered(P, _, Path) :- memberchk(P, Path), !.
covered(P, D, Path) :-
    \+ ( claim(Id, A, _, _, _, _, _, _, _, _), active(Id), pred_of(A, P) ),
    findall(B, ( rule(Id, K, H, B, _), K \== superiority, active(Id), H \== none, pred_of(H, P) ), Bs),
    Bs \== [],
    forall(member(B, Bs), body_covered(B, D, [P|Path])).

complete(N, D) :-
    claim(Id, [complete, S], _, _, F, T, _, _, _, _), active(Id), in_force(F, T, D), atom_string(N, S), !.

body_covered(B, D, Path) :- forall(member(L, B), lit_covered(L, D, Path)).
lit_covered([fetch, C|_], D, _) :- !, complete(C, D).
lit_covered([not, L], D, Path) :- !, lit_covered(L, D, Path).
lit_covered([agg, _, _, B, _], D, Path) :- !, body_covered(B, D, Path).
lit_covered(L, D, Path) :- derived_lit(L), !, pred_of(L, P), covered(P, D, Path).
lit_covered(_, _, _).

%   A rule is covered when its body is.
rule_covered(Id, D) :- rule(Id, _, _, B, _), body_covered(B, D, []).

uses_uncovered_closed(Ids, D) :-
    member(Id, Ids), rule(Id, _, _, _, M), mget(closed_over, M, known_facts), \+ rule_covered(Id, D), !.

%!  contested_why(+G, +D, -Sides, -Node)  PLAN-v3-integrity §4: the contested node of a downstream G
contested_why(G, D, Sides, _{type:contested, goal:G, via:Via, rules:Rules, roots:RNs}) :-
    contested_info(G, D, Via, Rules, Roots),
    maplist([X-Sd-Ps, _{type:conflict, goal:X, sides:Sd, children:Ps}]>>true, Roots, RNs),
    findall(S, ( member(_-Sd-_, Roots), member(S, Sd) ), S0), sort(S0, Sides).

%   One contested instance of an open goal: its sides and why nodes (a root: the side proofs).
inst_conflict(_, _, blocked(Sp, Ap), Sides, Why) :- !,
    ids_of(Sp, A), ids_of(Ap, B), sort([A, B], Sides),
    maplist([s(_, _, P), P]>>true, Sp, W1), maplist([a(_, _, _, P), P]>>true, Ap, W2), append(W1, W2, Why).
inst_conflict(G, D, contested(_, _), Sides, [Node]) :- contested_why(G, D, Sides, Node).

team_proofs(Sups, SupN, Why) :-
    maplist(team_proof(SupN), Sups, Why).
team_proof(SupN, s(Id, _, P0), P) :-
    include(winner_is(Id), SupN, Mine), get_dict(children, P0, C0), append(C0, Mine, C), put_dict(children, P0, C, P).
winner_is(Id, N) :- get_dict(winner, N, Id).

decide_open(G, D, R) :-
    term_variables(G, Vs),
    candidates(G, D, Gs),
    findall(G-E, ( member(G, Gs), status(G, D, E) ), GEs0),     % statuses; proofs only for what is reported
    include([_-E]>>(E = proven(_, _)), GEs0, Won0), maplist(hydrate_pair(D), Won0, Won),
    include([_-E]>>value3(E, contested), GEs0, Cont0), maplist(hydrate_pair(D), Cont0, Cont),
    pred_of(G, P),
    (   Cont \== []                                    % propagation: any contested instance contests the goal
    ->  findall(Sd-W, ( member(Gi-Ei, Cont), inst_conflict(Gi, D, Ei, Sd, W) ), SWs),
        pairs_keys_values(SWs, Sds, Ws), append(Sds, S0), sort(S0, Sides), append(Ws, Why),
        answer("CONFLICT", null, Sides, Why, D, R)
    ;   functional(P, _)
    ->  (   Won = [G1-proven(S, SN)] -> G = G1, value_of(Vs, V), team_proofs(S, SN, Why), answer("ANSWER", V, null, Why, D, R)
        ;   Won = [], GEs0 \== []
        ->  maplist(hydrate_pair(D), GEs0, GEs),
            findall(Ids, ( member(_-E, GEs), sups_of(E, Ss), Ss \== [], ids_of(Ss, Ids) ), Sides0), sort(Sides0, Sides),
            findall(Pf, ( member(_-E, GEs), sups_of(E, Ss), member(s(_, _, Pf), Ss) ), Why),
            answer("CONFLICT", null, Sides, Why, D, R)
        ;   Won = [] -> explain_not(G, D, N), absence(G, D, open, Abs), answer("ANSWER", null, null, [N], Abs, D, R)
        ;   findall(V, ( member(G-_, Won), value_of(Vs, V) ), Vals),
            answer("CONFLICT", null, null, [], D, R0), R = R0.put(value, Vals) )
    ;   findall(V-Why1, ( member(G-proven(S, SN), Won), value_of(Vs, V), team_proofs(S, SN, Why1) ), VWs),
        pairs_keys_values(VWs, Vals0, Whys), sort(Vals0, Vals), append(Whys, Why),
        ( Vals == [] -> absence(G, D, open, Abs) ; Abs = false ),
        answer("ANSWER", Vals, null, Why, Abs, D, R) ).

hydrate_pair(D, G-E0, G-E) :- hydrate(G, D, E0, E).

sups_of(proven(S, _), S).
sups_of(defeated(_, S, _), S).
sups_of(blocked(S, _), S).
sups_of(none(_), []).

value_of([V], V) :- !.
value_of(Vs, Vs).

answer(St, V, Sides, Why, D, R) :- answer(St, V, Sides, Why, false, D, R).
answer(St, V, Sides, Why, Abs, D, _{status:St, value:V, sides:Sides, why:Why, owners:Os, qualifier:Q}) :-
    why_ids(Why, Ids), findall(O, ( member(Id, Ids), rule(Id, _, _, _, M), mget(owner, M, O) ), Os0), sort(Os0, Os),
    qualifier(St, V, Ids, Abs, D, Q).

%   IR-005 (SEMANTICS.md, Qualifier): a positive answer proven through a rule marked :closed_over
%   :known_facts is total only over the known facts (its :not / aggregate / measure reads every fact there
%   is, with no completeness claim behind it); a negative answer when it rests on absence (absence/4).
qualifier("ANSWER", V, Ids, Abs, D, Q) :-
    (   memberchk(V, [false, null, []]) -> Abs == true ; uses_uncovered_closed(Ids, D) ), !,
    Q = "total over known facts in declared scope".
qualifier(_, _, _, _, _, null).

why_ids(Why, Ids) :- findall(Id, ( sub_node(Why, N), is_dict(N), get_dict(id, N, Id) ), Ids0), sort(Ids0, Ids).
sub_node(X, X).
sub_node(X, N) :- is_dict(X), get_dict(K, X, C), memberchk(K, [children, failed, roots, members]), sub_node(C, N).
sub_node(X, _{id:Id}) :- is_dict(X), get_dict(type, X, contested), get_dict(rules, X, Ms), member(Id, Ms).
sub_node(L, N) :- is_list(L), member(X, L), sub_node(X, N).

why_not(G, D, R) :-
    (   ground(G), evaluate(G, D, proven(S, SN))
    ->  team_proofs(S, SN, Why), R = _{status:"ANSWER", value:true, why:Why, why_not:[]}
    ;   explain_not(G, D, N), R = _{status:"ANSWER", value:false, why_not:[N]} ).

% ------------------------------------------------------------------ claims

do_op("claims", Op, _{asset:A, claims:Cs}) :- !,
    as_of(Op, D), A = Op.asset,
    findall(C, ( top_claim(Id, A), active(Id), standing(Id, D, null, C) ), Cs).

%!  standing(+Id, +D, +Role, -Dict): holds | holds_with_qualifier | rebutted | contested | not_in_force
standing(Id, D, Role, R) :-
    claim(Id, A, By, At, F, T, About, _, _, M),
    mget(backing, M, Bk, null), mget(qualifier, M, Modal, null),
    Base = _{id:Id, about:About, assertion:A, asserted_by:By, asserted_at:At, valid_from:F, valid_to:T,
             backing:Bk, modal:Modal, role:Role},
    findall(S, ( claim_link(Id, SId, SR), active(SId), standing(SId, D, SR, S) ), Subs),
    (   \+ in_force(F, T, D) -> St = _{standing:"not_in_force", defeater:null, qualifier:[], sides:null}
    ;   evaluate(A, D, E),
        (   E = contested(_, _) -> contested_why(A, D, Sides, _),
            St0 = _{standing:"contested", defeater:null, qualifier:[], sides:Sides}
        ;   own_standing(E, St0) ),
        (   St0.standing == "holds" -> sub_standing(Subs, St) ; St = St0 ) ),
    R = Base.put(St).put(subclaims, Subs).

failing(S) :- get_dict(standing, S, X), \+ memberchk(X, ["holds", "holds_with_qualifier"]).

own_standing(proven(_, _), _{standing:"holds", defeater:null, qualifier:[], sides:null}).
own_standing(defeated(a(AId, _, _, _), _, _), _{standing:"rebutted", defeater:AId, qualifier:[], sides:null}).
own_standing(blocked(S, U), _{standing:"contested", defeater:null, qualifier:[], sides:Sides}) :-
    ids_of(S, A), ids_of(U, B), sort([A, B], Sides).
own_standing(none(_), _{standing:"holds", defeater:null, qualifier:[], sides:null}).

sub_standing(Subs, St) :-
    (   member(S, Subs), get_dict(role, S, required), failing(S), get_dict(standing, S, "contested")
    ->  get_dict(id, S, Via), get_dict(sides, S, Sd),    % propagation: a contested required member contests
        St = _{standing:"contested", defeater:null, qualifier:[], sides:Sd, via:Via}
    ;   member(S, Subs), get_dict(role, S, required), failing(S)
    ->  get_dict(defeater, S, Df), get_dict(id, S, Via),
        St = _{standing:"rebutted", defeater:Df, qualifier:[], sides:null, via:Via}
    ;   findall(SId, ( member(S, Subs), get_dict(role, S, supporting), failing(S), get_dict(id, S, SId) ), Q0), sort(Q0, Q),
        (   Q == [] -> St = _{standing:"holds", defeater:null, qualifier:[], sides:null}
        ;   St = _{standing:"holds_with_qualifier", defeater:null, qualifier:Q, sides:null} ) ).

% ------------------------------------------------------------------ vocabulary, metadata, fetch

do_op("resolve_term", Op, _{text:Op.text, status:St, candidates:Cs}) :- !,
    norm(Op.text, N),
    findall(Id, ( term(Id0, M), term_matches(N, M), ( mget(see, M, See) -> member(Id, See) ; Id = Id0 ) ), Ids0),
    sort(Ids0, Ids),
    findall(_{term:Id, definition:Df, owner:O}, ( member(Id, Ids), term(Id, M), mget(definition, M, Df), mget(owner, M, O) ), Cs),
    length(Ids, K), ( K =:= 0 -> St = "none" ; K =:= 1 -> St = "concept" ; St = "several" ).

term_matches(N, M) :- mget(label, M, L), norm(L, N), !.
term_matches(N, M) :- mget(synonyms, M, Ss), member(S, Ss), norm(S, N), !.

norm(S, N) :-
    string_lower(S, L), string_codes(L, Cs0),
    maplist([C, D]>>( code_type(C, alnum) -> D = C ; D = 0'\s ), Cs0, Cs1),
    string_codes(S1, Cs1), split_string(S1, " ", " ", Ws0), exclude(==(""), Ws0, Ws),
    atomic_list_concat(Ws, ' ', A), atom_string(A, N).

do_op("describe", Op, R) :- !, describe(Op.asset, R).

describe(A, R) :-
    findall(C, top_claim(C, A), Cs),
    ( asset_meta(A, K, Doc, B) -> St = "ANSWER" ; K = null, Doc = null, B = null, St = "OUT_OF_SCOPE" ),
    R = _{status:St, asset:A, kind:K, doc:Doc, bindings:B, claims:Cs}.

asset_meta(A, K, Doc, null) :- asset(A, M), !, mget(kind, M, K), mget(doc, M, Doc).
asset_meta(A, term, Doc, B) :- term(A, M), !, mget(definition, M, Doc), mget(concept, M, B, null).
asset_meta(A, K, Doc, _{concept:N, tables:Tb, params:Ps, sql:Sql}) :-
    concept(_, M), mget(id, M, A), !,
    mget(kind, M, K), mget(doc, M, Doc), mget(name, M, N), mget(sql, M, Sql, null),
    mget(tables, M, Tb, []), mget(params, M, Ps, []).
asset_meta(A, table, Doc, null) :- slice(S), mget(tables, S, Ts), member(T, Ts), mget(id, T, A), !, mget(doc, T, Doc).
asset_meta(A, column, Doc, null) :-
    slice(S), mget(tables, S, Ts), member(T, Ts), mget(columns, T, Cols), member(M, Cols), mget(id, M, A), !,
    mget(doc, M, Doc).

do_op("fetch", Op, _{concept:C, filters:Op.filters, rows:Rows, sql:Sql, params:Ps, row_count:N, truncated:Tr}) :- !,
    atom_string(C, Op.concept), dict_pairs(Op.filters, _, F),
    fetch_rows(C, F, Rows, Info, _), length(Rows, N), Sql = Info.sql, Ps = Info.params, Tr = Info.truncated.

% ------------------------------------------------------------------ design: rules, summary (PLAN-v3-bench-full §2)

%!  rules: the active rules and claims that conclude, attack, read or rank what `about` names (a predicate, a
%   term, a concept, an asset, or a goal pattern that narrows a predicate to the records whose literal can meet
%   it), from the loaded rule base alone (no evaluation). Rules that only read it are listed as id and head. conflicts: the opposing
%   pairs (a supporter and an attacker of the same predicate whose heads can meet) with no superiority either
%   way; each is a root conflict wherever both bodies hold (decide / summary find the instances).
do_op("rules", Op, R) :- !,
    (   sub_string(Op.about, 0, _, _, "[")         % a goal pattern: only the records whose literal can meet it
    ->  edn_parse(Op.about, G0), edn_vars(G0, G, [], _), pred_of(G, P0),
        ( known_pred(P0) -> Ps = [P0] ; Ps = [] ), Cs = [], Cl = []
    ;   about(Op.about, Ps, Cs, Cl), G = _ ),
    (   Ps == [], Cs == [], Cl == []
    ->  (   nonvar(G) -> pred_of(G, P1), scope(P1, St)
        ;   sub_string(Op.about, 0, _, _, "term:") -> St = "UNDERDETERMINED" ; St = "OUT_OF_SCOPE" ),
        R = _{status:St, about:Op.about, predicates:[], concepts:[], rules:[], read_by:[], conflicts:[]}
    ;   findall(Id-Role, ( member(P, Ps), role(P, Id, Role), meets(G, Id, Role) ), IR1),
        findall(Id-reads, ( member(C, Cs), rule(Id, _, _, B, _), active(Id), body_lit(B, [fetch, C|_]) ), IR2),
        findall(Id-about, member(Id, Cl), IR3),
        append([IR1, IR2, IR3], IR4),
        (   Cl == [] -> IR0 = IR4                     % an asset: its own claims, not every claim on their predicates
        ;   exclude([Id-_]>>( claim(Id, _, _, _, _, _, _, _, _, _), \+ memberchk(Id, Cl) ), IR4, IR0) ),
        sort(IR0, IR), group_pairs_by_key(IR, Groups),
        partition([_-Rs]>>( Rs == [reads] ), Groups, RG, MG),     % rules that only read it: id and head
        maplist(item, MG, Items),
        findall(_{id:Id, head:Hd}, ( member(Id-_, RG), rule(Id, _, H, _, _), edn_text(H, Hd) ), RB),
        pairs_keys(IR, Kept),
        findall(_{predicate:P, sides:[[X], [Y]]}, ( member(P, Ps), unresolved(P, X, Y), memberchk(X, Kept), memberchk(Y, Kept) ), Cf),
        R = _{status:"ANSWER", about:Op.about, predicates:Ps, concepts:Cs, rules:Items, read_by:RB, conflicts:Cf} ).

%   about(+Text, -Preds, -Concepts, -Claims): a predicate or concept by name; a term by id (its predicate of the
%   same name, its bound concept); a concept by id; an asset by id (the claims about it and their predicates).
about(A, Ps, Cs, Cl) :-
    ( sub_string(A, 0, _, _, "term:") -> sub_string(A, 5, _, 0, N) ; N = A ),
    atom_string(P0, N),
    findall(P0, mentioned(P0), P1),
    findall(C, ( concept(C, M), ( C == P0 ; mget(id, M, A) ; term(A, TM), mget(concept, TM, CI), mget(id, M, CI) ) ), C1),
    findall(Id, ( claim(Id, _, _, _, _, _, A, _, _, _), active(Id) ), Cl0), sort(Cl0, Cl),
    findall(P, ( member(Id, Cl), claim(Id, As, _, _, _, _, _, _, _, _), pred_of(As, P) ), P2),
    append(P1, P2, Ps0), sort(Ps0, Ps), sort(C1, Cs).

mentioned(P) :- once(( rule(Id, _, H, B, M), active(Id),
                       ( H \== none, pred_of(H, P) ; body_lit(B, L), derived_lit(L), pred_of(L, P) ; mget(pred, M, P) )
                     ; claim(Id, A, _, _, _, _, _, _, _, _), active(Id), pred_of(A, P) )).

%   role(+P, -Id, -Role): concludes (a strict / defeasible rule or a claim with a positive P head), attacks (a
%   negative head, a defeater, an incompatibility declared on P), reads (P in the body), ranks (a superiority rule on P).
role(P, Id, Role) :-
    rule(Id, K, H, B, M), active(Id),
    (   K == superiority -> mget(pred, M, P), Role = ranks
    ;   H \== none, pred_of(H, P), head_role(K, H, Role)
    ;   body_lit(B, L), derived_lit(L), pred_of(L, P), Role = reads ).
role(P, Id, Role) :-
    claim(Id, A, _, _, _, _, _, _, _, _), active(Id), pred_of(A, P), ( A = [neg, _] -> Role = attacks ; Role = concludes ).

%   meets(?Pattern, +Id, +Role): the record's literal for that role unifies with the pattern (always, if unbound).
meets(G, _, _) :- var(G), !.
meets(_, _, ranks) :- !.
meets(G, Id, reads) :- !, rule(Id, _, _, B, _), body_lit(B, L), ( L = [neg, X] -> true ; X = L ), \+ X \= G, !.
meets(G, Id, _) :- ( rule(Id, _, H, _, _) ; claim(Id, H, _, _, _, _, _, _, _, _) ), !, ( H = [neg, X] -> true ; X = H ), \+ X \= G.

head_role(K, H, Role) :- ( H = [neg, _] ; memberchk(K, [defeater, incompatible]) ), !, Role = attacks.
head_role(_, _, concludes).

%   Every literal of a body, inside [:not] and aggregates too.
body_lit(B, L) :- member(X, B), ( X = [not, Y] -> body_lit([Y], L) ; X = [agg, _, _, B2, _] -> body_lit(B2, L) ; L = X ).

item(Id-Roles, I) :-
    (   rule(Id, K, H, B, M)
    ->  findall(Q, ( body_lit(B, L), derived_lit(L), pred_of(L, Q) ), Q0), sort(Q0, Qs),
        findall(C, body_lit(B, [fetch, C|_]), C0), sort(C0, Cs),
        ( H == none -> Hd = null ; edn_text(H, Hd) ),
        I0 = _{id:Id, kind:K, head:Hd, recorded_at:Rec, depends_on:_{predicates:Qs, concepts:Cs}},
        mget(recorded_at, M, Rec, null),
        ( K == superiority -> mget(pred, M, Pr), mget(order, M, O), I1 = I0.put(_{pred:Pr, order:O}) ; I1 = I0 ),
        foldl(meta_field(M), [completeness, closed_over], I1, I2)
    ;   claim(Id, A, By, At, F, T, About, _, _, M),
        edn_text(A, Hd), mget(depends_on, M, Dp, []), mget(supports, M, Su, []), mget(qualifier, M, Q, null),
        mget(backing, M, Bk, null),
        I2 = _{id:Id, kind:claim, head:Hd, about:About, asserted_by:By, asserted_at:At, valid_from:F, valid_to:T,
               recorded_at:Rec, backing:Bk, modal:Q, depends_on:_{claims:Dp}, supports:Su},
        mget(recorded_at, M, Rec, null) ),
    mget(owner, M, Ow, null), mget(class, M, Cl, null), mget(doc, M, Doc, null),
    findall(_{id:L, source:S}, ( opponent(Id, L), sup(Id, L, S) ), Sup0), sort(Sup0, Sup),
    findall(_{id:W, source:S}, ( opponent(Id, W), sup(W, Id, S) ), Inf0), sort(Inf0, Inf),
    I3 = I2.put(_{roles:Roles, owner:Ow, class:Cl, doc:Doc, superior_to:Sup, inferior_to:Inf}),
    compact(I3, I).

%   Fields that are null or empty are left out.
compact(D0, D) :-
    dict_pairs(D0, T, Ps0),
    findall(K-V, ( member(K-V0, Ps0), ( is_dict(V0) -> compact(V0, V), dict_pairs(V, _, [_|_]) ; V = V0 ), V \== null, V \== [] ), Ps),
    dict_pairs(D, T, Ps).

meta_field(M, K, I0, I) :- ( mget(K, M, V), V \== null -> I = I0.put(K, V) ; I = I0 ).

%   opposes(?X, ?Y, ?P): X supports a P head that Y's head can attack (complement, a functional rival, or an
%   incompatibility declared on that head).
opposes(X, Y, P) :-
    supporter(X, HX), pred_of(HX, P),
    (   rival(HX, R, Diff), attacker_head(Y, HY), \+ HY \= R, copy_term(R-Diff, HY-D2), may_differ(D2)
    ;   rule(Y, incompatible, HY, _, _), active(Y), \+ HY \= HX ),
    X \== Y.

supporter(Id, H) :- rule(Id, K, H, _, _), memberchk(K, [strict, defeasible]), active(Id).
supporter(Id, H) :- claim(Id, H, _, _, _, _, _, _, _, _), active(Id).
attacker_head(Id, H) :- rule(Id, K, H, _, _), memberchk(K, [strict, defeasible, defeater]), active(Id).
attacker_head(Id, H) :- claim(Id, H, _, _, _, _, _, _, _, _), active(Id).

may_differ(true).
may_differ(diff(V, V2)) :- \+ V == V2.

opponent(Id, O) :- ( opposes(Id, O, _) ; opposes(O, Id, _) ), Id \== O.

unresolved(P, X, Y) :-
    setof(A-B, ( opposes(X0, Y0, P), msort([X0, Y0], [A, B]) ), Pairs), member(X-Y, Pairs),
    \+ sup(X, Y, _), \+ sup(Y, X, _).

%   EDN text of a stored literal (variables printed ?a, ?b, ...).
edn_text(T, S) :- copy_term(T, T1), numbervars(T1, 0, _), with_output_to(string(S), wedn(T1)).
wedn('$VAR'(N)) :- !, C is 0'a + N mod 26, K is N // 26, ( K =:= 0 -> format("?~c", [C]) ; format("?~c~w", [C, K]) ).
wedn(L) :- is_list(L), !, write('['), wedn_seq(L), write(']').
wedn(map(Ps)) :- !, write('{'), foldl([K-V, Sep0, ' ']>>( write(Sep0), wedn(K), write(' '), wedn(V) ), Ps, '', _), write('}').
wedn(X) :- string(X), !, json_write(current_output, X).
wedn(X) :- atom(X), !, format(":~w", [X]).
wedn(X) :- write(X).
wedn_seq([]).
wedn_seq([X|Xs]) :- wedn(X), forall(member(Y, Xs), ( write(' '), wedn(Y) )).

%!  summary: the status of every instance of an open goal. filters gives a variable's domain, either a list of
%   values or {concept, filters, column} (a fetch; column defaults to id); the instances are the goal's ground
%   candidates under each binding of the domains (a binding with none is one refuted instance).
do_op("summary", Op, R) :- !,
    as_of(Op, D), edn_parse(Op.goal, G0), edn_vars(G0, G, [], Ns0), reverse(Ns0, Ns),
    ( get_dict(filters, Op, F), F \== null -> dict_pairs(F, _, Ds) ; Ds = [] ),
    ( get_dict(sample, Op, K) -> true ; K = 10 ),
    pred_of(G, P),
    (   \+ known_pred(P) -> scope(P, St), R = _{status:St, goal:Op.goal, as_of:D}
    ;   catch(summary(G, Ns, Ds, D, K, R0), error(fetch_unbound(C, Fs), _), unbound_error(C, Fs, Ns, R0)),
        R = R0.put(_{goal:Op.goal, as_of:D}) ).

unbound_error(C, Fs, Ns, _{status:"ERROR", error:Msg}) :-
    pairs_keys(Ns, Vs), atomic_list_concat(Vs, ', ', VT), pairs_keys(Fs, Ks),
    format(string(Msg), "the goal's instances cannot be enumerated: ~w needs ~w bound; give a domain in filters for one of ~w, e.g. {\"?r\": {\"concept\": \"request_in_subtree\", \"filters\": {\"root\": \"cc0049\", \"status\": \"pending\"}}}", [C, Ks, VT]).

summary_limit(20000).

summary(G, Ns, Ds, D, K, R) :-
    maplist(domain(Ns), Ds, DVs),
    foldl([_-Vs, N0, N]>>( length(Vs, L), N is N0 * L ), DVs, 1, Size), summary_limit(Max),
    (   Size > Max -> throw(error(summary_too_large(Size, Max), _)) ; true ),
    pairs_values(Ns, Vars),
    findall(Vars-V-G, ( bind(DVs), instance(G, D, V) ), Is),
    aggregate_all(count, member(_-proven-_, Is), NP), aggregate_all(count, member(_-refuted-_, Is), NR),
    aggregate_all(count, member(_-contested-_, Is), NC), length(Is, N),
    findall(Gr-S, ( member(_-contested-Gi, Is), inst_roots(Gi, D, Rts), member(Gr-S, Rts) ), RS0),
    msort(RS0, RS1), clumped(RS1, RC),
    findall(_{goal:Gr, sides:S, instances:C}, ( member((Gr-S)-C, RC) ), Roots0),
    sort(instances, @>=, Roots0, Roots1), length(Roots1, NRoots), take(20, Roots1, Roots),
    maplist([St, St-Smp]>>( findall(B, ( member(Vs-St-_, Is), binding_of(Ns, Vs, B) ), Bs0), sort(Bs0, Bs), take(K, Bs, Smp) ),
            [proven, refuted, contested], Samples),
    dict_pairs(Sample, _, Samples),
    R = _{status:"ANSWER", instances:N, counts:_{proven:NP, refuted:NR, contested:NC}, contested_roots:Roots,
          contested_roots_total:NRoots, sample:Sample}.

domain(Ns, Name-Spec, Var-Vals) :-
    (   memberchk(Name-Var, Ns) -> true ; throw(error(domain_error(goal_variable, Name), _)) ),
    (   is_list(Spec) -> Vals = Spec
    ;   atom_string(C, Spec.concept), ( get_dict(filters, Spec, FD) -> dict_pairs(FD, _, F) ; F = [] ),
        ( get_dict(column, Spec, Col0) -> atom_string(Col, Col0) ; Col = id ),
        fetch_rows(C, F, Rows, Info, _),
        (   Info.truncated == true -> throw(error(domain_truncated(C), _)) ; true ),
        findall(V, ( member(Row, Rows), get_dict(Col, Row, V) ), Vs0), sort(Vs0, Vals) ).

bind([]).
bind([V-Vals|DVs]) :- member(V, Vals), bind(DVs).

instance(G, D, V) :- ground(G), !, status(G, D, E), value3(E, V).
instance(G, D, V) :- candidates(G, D, Gs), ( Gs == [] -> V = refuted ; member(G, Gs), status(G, D, E), value3(E, V) ).

%   The root conflicts behind a contested instance, as Goal-Sides.
inst_roots(G, D, Rts) :-
    status(G, D, E),
    (   E = blocked(S, A) -> ids_of(S, I1), ids_of(A, I2), sort([I1, I2], Sd), Rts = [G-Sd]
    ;   contested_info(G, D, _, _, Ro), findall(X-Sd, member(X-Sd-_, Ro), Rts) ).

binding_of([_-_], [V], B) :- !, ( var(V) -> B = null ; B = V ).
binding_of(Ns, Vs, B) :- pairs_keys(Ns, Ks), maplist([X, Y]>>( var(X) -> Y = null ; Y = X ), Vs, Ys),
    pairs_keys_values(Ps, Ks, Ys), dict_pairs(B, _, Ps).

take(K, L, T) :- length(L, N), M is min(K, N), length(T, M), append(T, _, L).

% ------------------------------------------------------------------ extension, hypotheses

do_op("add", Op, _{added:Ids}) :- !, edn_parse(Op.edn, Recs), add_records(Recs, ext, Ids).

%   Hypotheses. mode snapshot (default): snapshot/1 (SWI >= 9): the hypothesis's withholds, added records and
%   memo entries are local to this thread and discarded on exit; other threads see the base state throughout.
%   mode assert: the original mechanism (assert/retract on the shared database under setup_call_cleanup), kept
%   so the isolation test can show it fails.
:- dynamic hyp_mode/1.
hyp_mode(snapshot).
set_hyp_mode(M) :- retractall(hyp_mode(_)), atom_string(A, M), assertz(hyp_mode(A)).

do_op("with_hypothesis", Op, _{results:Rs, added:Ids, withheld:W}) :- !,
    ( get_dict(withhold, Op, W0) -> maplist([S, A]>>atom_string(A, S), W0, W) ; W = [] ),
    ( get_dict(add, Op, E), E \== null -> edn_parse(E, Recs) ; Recs = [] ),
    hyp_mode(M), flag(v3a_hyp, N, N + 1),
    hypothesis(M, hyp(N), W, Recs, Op.ops, Ids, Rs).

hypothesis(snapshot, S, W, Recs, Ops, Ids, Rs) :-
    snapshot(with_state(S, ( forall(member(I, W), assertz(withheld(I))), add_records(Recs, hyp, Ids),
                             maplist([O, R]>>op_result(O, R), Ops, Rs) ))).
hypothesis(assert, S, W, Recs, Ops, Ids, Rs) :-
    setup_call_cleanup(
        ( forall(member(I, W), assertz(withheld(I))), add_records(Recs, hyp, Ids) ),
        with_state(S, maplist([O, R]>>op_result(O, R), Ops, Rs)),
        ( forall(member(I, W), retract(withheld(I))), retract_source(hyp) )).

%   Test-only op: sleep, reporting wall-clock start/end (epoch ms) so the isolation test can check overlap.
do_op("sleep", Op, _{t0:T0, t1:T1}) :- !,
    get_time(A), T0 is A * 1000, S is Op.ms / 1000, sleep(S), get_time(B), T1 is B * 1000.

%!  run_concurrent(+JsonListOfOpLists, -Out)  each op list in its own Prolog thread; results per list, each op
%   result stamped with wall-clock t_start/t_end (epoch ms).
run_concurrent(J, Out) :-
    atom_json_dict(J, Lists, [value_string_as(string)]),
    maplist([Ops, Id]>>thread_create(run_list(Ops), Id, []), Lists, Ids),
    maplist([Id, Rs]>>( thread_join(Id, St), ( St = exited(Rs) -> true ; format(string(E), "~q", [St]), Rs = [_{status:"ERROR", error:E}] ) ), Ids, Rss),
    with_output_to(string(Out), json_write_dict(current_output, Rss, [width(0)])).

run_list(Ops) :- maplist(timed_op, Ops, Rs), thread_exit(Rs).

timed_op(O, R) :-          % not a yall lambda: dict functional notation would expand outside it
    get_time(A), op_result(O, R0), get_time(B), Ta is A * 1000, Tb is B * 1000,
    R = R0.put(_{t_start:Ta, t_end:Tb}).

%!  memo_test(-Out)  base memo entries must not be used inside a hypothesis, and hypothesis entries must not
%   survive it. Control: the same hypothesis run under the `base` token reuses the base entry (the leak the key prevents).
memo_test(Out) :-
    G = _{op:"decide", goal:"[:cost_centre_of \"e077\" ?c]", as_of:"2026-07-15"},
    clear_memo,
    do_op("decide", G, B1),                                    % populates memo(base, ...)
    aggregate_all(count, memo(_, base, _, _, _), NBase),
    snapshot(with_state(hyp(t), ( assertz(withheld('R313')), do_op("decide", G, H) ))),
    snapshot(( assertz(withheld('R313')), do_op("decide", G, Leak) )),     % control: token stays base
    do_op("decide", G, B2),
    aggregate_all(count, memo(_, hyp(_), _, _, _), NHyp),
    Out = _{base_before:B1.status-B1.value, base_memo_entries:NBase, hypothesis:H.status, control_same_token:Leak.status,
            base_after:B2.status-B2.value, hyp_entries_left:NHyp}.
do_op(Name, _, _) :- throw(error(unknown_op(Name), _)).
