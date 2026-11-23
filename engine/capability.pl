/*  capability.pl -- the capability registry: what a model may call at each layer.

    capability(Pred/Arity, Layer, Doc): Pred/Arity exists from Layer on, meaning Doc.
    Read by the compile-mode validator and by the prompts (M6); `engine/ask --capabilities` lists it.
*/
:- module(capability, [capability/3, capabilities/2]).
:- use_module(core).

capability(PI, L, Doc) :- pred_doc(PI, L, Doc).
capability(relation/1, 0, "relation(R): R is a relation of the schema.").
capability(column/4, 0, "column(R, C, P, T): relation R has column C at position P with type T.").
capability(key/2, 0, "key(R, C): C is the first key column of relation R.").
capability(fk/3, 0, "fk(R, C, T): column C of relation R refers to relation T.").
capability(reading/2, 1, "reading(Fork, Reading): the reading chosen for an interpretation fork.").

%% capabilities(+Layer, -List): c(PI, FromLayer, Doc) for everything available at Layer, sorted by layer.
%% A relation's doc is the one its material shows at Layer (schema.yaml doc_from), as render/common.py does.
capabilities(Layer, List) :-
    findall(L-c(PI, L, Doc), ( capability(PI, L, Doc0), L =< Layer, doc_at(PI, Layer, Doc0, Doc) ), Ps),
    keysort(Ps, S), pairs_values(S, List).

doc_at(N/_, Layer, Doc0, Doc) :-
    ( aggregate_all(max(K, D), ( rel_doc_from(N, K, D), K =< Layer ), max(_, D1)) -> Doc = D1 ; Doc = Doc0 ).
