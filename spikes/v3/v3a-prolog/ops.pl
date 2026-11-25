/*  V3a System A surface (CONTRACT.md): run_op(+OpJSON, -ResultJSON).
    decide, why_not, claims, resolve_term, describe, fetch, add, with_hypothesis.
*/
:- module(ops, [run_op/2, load_files_json/1, set_hyp_mode/1, run_concurrent/2, memo_test/1, table_test/1]).
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
    py_call(sql:begin_op(), _), clear_memo,
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
    ->  team_proofs(Sups, SupN, Why),
        (   incompatible(G, D, IId, INode)
        ->  ids_of(Sups, SIds), sort([SIds, [IId]], Sides), append(Why, [INode], W2),
            answer("CONFLICT", null, Sides, W2, R)
        ;   answer("ANSWER", true, null, Why, R) )
    ;   E = blocked(Sups, Un)
    ->  ids_of(Sups, A), ids_of(Un, B), sort([A, B], Sides),
        maplist([s(_, _, P), P]>>true, Sups, W1), maplist([a(_, _, _, P), P]>>true, Un, W2), append(W1, W2, Why),
        answer("CONFLICT", null, Sides, Why, R)
    ;   E = undefined(Sides, UNode)                    % wfs mode: undefined by a negative cycle
    ->  answer("CONFLICT", null, Sides, [UNode], R)
    ;   explain_not(G, D, N), answer("ANSWER", false, null, [N], R) ).

% R314-style declared incompatibility: the goal is proven and the incompatible body is provable
incompatible(G, D, Id, _{type:rule, id:Id, goal:[neg, G], children:Kids}) :-
    rule(Id, incompatible, H, B, _), active(Id), H = G, once(body(B, D, Kids)).

team_proofs(Sups, SupN, Why) :-
    maplist(team_proof(SupN), Sups, Why).
team_proof(SupN, s(Id, _, P0), P) :-
    include(winner_is(Id), SupN, Mine), get_dict(children, P0, C0), append(C0, Mine, C), put_dict(children, P0, C, P).
winner_is(Id, N) :- get_dict(winner, N, Id).

decide_open(G, D, R) :-
    term_variables(G, Vs),
    findall(G, candidate_instance(G, D), Gs0), sort(Gs0, Gs),
    findall(G-E, ( member(G, Gs), evaluate(G, D, E) ), GEs),
    include([_-E]>>(E = proven(_, _)), GEs, Won),
    pred_of(G, P),
    (   functional(P, _)
    ->  (   Won = [G1-proven(S, SN)] -> G = G1, value_of(Vs, V), team_proofs(S, SN, Why), answer("ANSWER", V, null, Why, R)
        ;   Won = [], GEs \== []
        ->  findall(Ids, ( member(_-E, GEs), sups_of(E, Ss), Ss \== [], ids_of(Ss, Ids) ), Sides0), sort(Sides0, Sides),
            findall(Pf, ( member(_-E, GEs), sups_of(E, Ss), member(s(_, _, Pf), Ss) ), Why),
            answer("CONFLICT", null, Sides, Why, R)
        ;   Won = [] -> explain_not(G, D, N), answer("ANSWER", null, null, [N], R)
        ;   findall(V, ( member(G-_, Won), value_of(Vs, V) ), Vals),
            answer("CONFLICT", null, null, [], R0), R = R0.put(value, Vals) )
    ;   findall(V-Why1, ( member(G-proven(S, SN), Won), value_of(Vs, V), team_proofs(S, SN, Why1) ), VWs),
        pairs_keys_values(VWs, Vals0, Whys), sort(Vals0, Vals), append(Whys, Why),
        answer("ANSWER", Vals, null, Why, R) ).

candidate_instance(G, D) :-
    (   rule(Id, K, G, B, _), memberchk(K, [strict, defeasible]), active(Id), body(B, D, _)
    ;   claim(Id, G, _, _, F, T, _, _, _, _), active(Id), in_force(F, T, D) ),
    ground(G).

sups_of(proven(S, _), S).
sups_of(defeated(_, S, _), S).
sups_of(blocked(S, _), S).
sups_of(none(_), []).
sups_of(undefined(_, _), []).

value_of([V], V) :- !.
value_of(Vs, Vs).

answer(St, V, Sides, Why, _{status:St, value:V, sides:Sides, why:Why, owners:Os, qualifier:Q}) :-
    why_ids(Why, Ids), findall(O, ( member(Id, Ids), rule(Id, _, _, _, M), mget(owner, M, O) ), Os0), sort(Os0, Os),
    qualifier(St, V, Ids, Q).

%   IR-005: an answer proven through a rule marked :closed_over :known_facts is total only over the known
%   facts (its :not / measure reads every fact there is, with no completeness claim behind it).
qualifier("ANSWER", V, Ids, "total over known facts in declared scope") :-
    V \== false, V \== null, V \== [],
    member(Id, Ids), rule(Id, _, _, _, M), mget(closed_over, M, known_facts), !.
qualifier(_, _, _, null).

why_ids(Why, Ids) :- findall(Id, ( sub_node(Why, N), is_dict(N), get_dict(id, N, Id) ), Ids0), sort(Ids0, Ids).
sub_node(X, X).
sub_node(X, N) :- is_dict(X), get_dict(K, X, C), memberchk(K, [children, failed]), sub_node(C, N).
sub_node(X, _{id:Id}) :- is_dict(X), get_dict(type, X, undefined), get_dict(members, X, Ms), member(Id, Ms).
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
    ;   evaluate(A, D, E), own_standing(E, St0),
        (   St0.standing == "holds" -> sub_standing(Subs, St) ; St = St0 ) ),
    R = Base.put(St).put(subclaims, Subs).

failing(S) :- get_dict(standing, S, X), \+ memberchk(X, ["holds", "holds_with_qualifier"]).

own_standing(proven(_, _), _{standing:"holds", defeater:null, qualifier:[], sides:null}).
own_standing(defeated(a(AId, _, _, _), _, _), _{standing:"rebutted", defeater:AId, qualifier:[], sides:null}).
own_standing(blocked(S, U), _{standing:"contested", defeater:null, qualifier:[], sides:Sides}) :-
    ids_of(S, A), ids_of(U, B), sort([A, B], Sides).
own_standing(none(_), _{standing:"holds", defeater:null, qualifier:[], sides:null}).
own_standing(undefined(Sides, _), _{standing:"contested", defeater:null, qualifier:[], sides:Sides}).

sub_standing(Subs, St) :-
    (   member(S, Subs), get_dict(role, S, required), failing(S)
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
                             maplist([O, R]>>op_result(O, R), Ops, Rs) ))),
    drop_state_tables(S).
hypothesis(assert, S, W, Recs, Ops, Ids, Rs) :-
    setup_call_cleanup(
        ( forall(member(I, W), assertz(withheld(I))), add_records(Recs, hyp, Ids) ),
        with_state(S, maplist([O, R]>>op_result(O, R), Ops, Rs)),
        ( forall(member(I, W), retract(withheld(I))), retract_source(hyp) )), drop_state_tables(S).

%   Tables computed under a hypothesis's token are dead once it exits (the token is never reused).
drop_state_tables(S) :- abolish_table_subgoals(defeasible:wdef(S, _, _)),
    abolish_table_subgoals(defeasible:wovr(S, _, _)), abolish_table_subgoals(defeasible:wbeat(S, _, _, _)).

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
    aggregate_all(count, memo(base, _, _, _), NBase),
    snapshot(with_state(hyp(t), ( assertz(withheld('R313')), do_op("decide", G, H) ))),
    snapshot(( assertz(withheld('R313')), do_op("decide", G, Leak) )),     % control: token stays base
    do_op("decide", G, B2),
    aggregate_all(count, memo(hyp(_), _, _, _), NHyp),
    Out = _{base_before:B1.status-B1.value, base_memo_entries:NBase, hypothesis:H.status, control_same_token:Leak.status,
            base_after:B2.status-B2.value, hyp_entries_left:NHyp}.
%!  table_test(-Out)  wfs mode, table policy session: tables computed in the base must not answer inside a
%   hypothesis, and tables of either must not answer for another as_of. Control: the same hypothesis run under
%   the `base` token picks up the base table (the leak the state argument prevents).
table_test(Out) :-
    set_table_policy(session), clear_tables,
    G = _{op:"decide", goal:"[:preferred \"dyne\"]"},
    Old = G.put(as_of, "2026-01-15"),
    do_op("decide", G, B1), do_op("decide", Old, O1),
    aggregate_all(count, ( current_table(defeasible:V, _), subsumes_term(wdef(base, _, _), V) ), NBase),
    snapshot(with_state(hyp(t), ( assertz(withheld('RY23')), do_op("decide", G, H), do_op("decide", Old, HO) ))),
    drop_state_tables(hyp(t)),
    snapshot(( assertz(withheld('RY23')), retractall(defeasible:memo(_, _, _, _)),  % control: token stays base;
               do_op("decide", G, Leak) )),                                       % memo emptied, so only tables answer
    do_op("decide", G, B2), do_op("decide", Old, O2),
    aggregate_all(count, ( current_table(defeasible:V, _), subsumes_term(wdef(hyp(_), _, _), V) ), NHyp),
    set_table_policy(op),
    Out = _{base_before:B1.status-B1.value, old_before:O1.status-O1.value, base_tables:NBase,
            hypothesis:H.status-H.value, hypothesis_old:HO.status-HO.value, control_same_token:Leak.status-Leak.value,
            base_after:B2.status-B2.value, old_after:O2.status-O2.value, hyp_tables_left:NHyp}.
do_op(Name, _, _) :- throw(error(unknown_op(Name), _)).
