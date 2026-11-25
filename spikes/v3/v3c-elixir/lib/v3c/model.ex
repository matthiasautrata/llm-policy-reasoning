defmodule V3c.Model do
  @moduledoc """
  V3c model: a hand-written validator for the slice and its runtime extensions, over the EDN the engine
  loads (rule heads and bodies included). It mirrors V3b's Malli schema clause for clause.

  Why hand-written: the rule language is positional (`[:fetch :c {..} {..}]`, `[:< a b]`), recursive
  (`[:not lit]`, `[:+ a b]`) and closed. Peri and NimbleOptions validate maps and keyword lists, not
  positional grammars; Ecto embedded schemas want structs and casting. Pattern matching over the data is
  what Elixir does natively, and every clause is a function head.

  `errors(x)` returns `[{path, message}]`, empty when `x` conforms. A map is a slice; a list is an extension.
  """

  @owners ~w(finance hr procurement compliance risk controller)a
  @classes ~w(definition material_inference exception entitlement superiority incompatibility)a
  @cmp ~w(< <= > >= =)a
  @reserved [:fetch, :not, :neg, :is, :as_of | @cmp]

  def errors(x) when is_map(x), do: slice(x, [])
  def errors(x) when is_list(x), do: each(x, [], &record/2)
  def errors(_), do: [{[], "a slice (map) or an extension (vector)"}]

  def validate!(label, x) do
    case errors(x) do
      [] -> :ok
      es -> raise ArgumentError, "#{label}: " <> Enum.map_join(Enum.take(es, 5), "; ", fn {p, m} -> "#{inspect(p)} #{m}" end)
    end
  end

  # ---------------------------------------------------------------- combinators

  defp each(xs, p, f) when is_list(xs), do: xs |> Enum.with_index() |> Enum.flat_map(fn {x, i} -> f.(x, p ++ [i]) end)
  defp each(_, p, _), do: [{p, "a vector"}]

  defp check(true, _p, _m), do: []
  defp check(_, p, m), do: [{p, m}]

  # a closed map: required keys, optional keys, one predicate per key
  defp closed(m, p, req, opt) when is_map(m) do
    allowed = Map.merge(req, opt)
    missing = for {k, _} <- req, not Map.has_key?(m, k), do: {p ++ [k], "missing required key"}
    extra = for {k, _} <- m, not Map.has_key?(allowed, k), do: {p ++ [k], "disallowed key"}
    bad = for {k, v} <- m, f = allowed[k], e <- f.(v, p ++ [k]), do: e
    missing ++ extra ++ bad
  end

  defp closed(_, p, _, _), do: [{p, "a map"}]

  defp is(pred, msg), do: fn v, p -> check(pred.(v), p, msg) end
  defp vec_of(f), do: fn v, p -> each(v, p, f) end
  defp re(r), do: is(&(is_binary(&1) and Regex.match?(r, &1)), "should match #{inspect(r.source)}")
  defp enum(xs), do: is(&(&1 in xs), "should be one of #{inspect(xs)}")
  defp maybe(f), do: fn v, p -> if is_nil(v), do: [], else: f.(v, p) end

  @date ~r/^\d{4}-\d{2}-\d{2}$/
  defp date, do: re(@date)
  defp str, do: is(&is_binary/1, "a string")
  defp kw, do: is(&(is_atom(&1) and not is_boolean(&1) and not is_nil(&1)), "a keyword")
  defp owner, do: enum(@owners)

  # ---------------------------------------------------------------- the rule language

  def lvar?({:var, "?" <> _}), do: true
  def lvar?(_), do: false

  defp term(t, p) do
    cond do
      lvar?(t) or is_binary(t) or is_integer(t) or is_boolean(t) -> []
      is_list(t) -> expr(t, p)
      true -> [{p, "a term: ?variable, string, integer, boolean or [:+|:- a b]"}]
    end
  end

  defp expr([op, a, b], p) when op in [:+, :-], do: term(a, p ++ [1]) ++ term(b, p ++ [2])
  defp expr(_, p), do: [{p, "an expression [:+|:- a b]"}]

  defp keyword?(x), do: is_atom(x) and not is_boolean(x) and not is_nil(x)

  def literal([:fetch, c, f, o], p) do
    check(keyword?(c), p ++ [1], "a concept keyword") ++
      if(is_map(f), do: Enum.flat_map(f, fn {k, v} -> check(keyword?(k), p ++ [2], "keyword keys") ++ term(v, p ++ [2, k]) end),
        else: [{p ++ [2], "filters: a map"}]) ++
      if(is_map(o), do: Enum.flat_map(o, fn {k, v} -> check(keyword?(k) and lvar?(v), p ++ [3, k], "outputs: {:col ?var}") end),
        else: [{p ++ [3], "outputs: a map"}])
  end

  def literal([op, l], p) when op in [:not, :neg], do: nested(l, p ++ [1])
  def literal([op, a, b], p) when op in @cmp, do: term(a, p ++ [1]) ++ term(b, p ++ [2])
  def literal([:is, x, e], p), do: check(lvar?(x), p ++ [1], "a ?variable") ++ (if is_list(e), do: expr(e, p ++ [2]), else: [{p ++ [2], "an expression"}])
  def literal([:as_of, x], p), do: term(x, p ++ [1])
  def literal([op | _], p) when op in @reserved, do: [{p, "#{inspect(op)}: wrong arity or shape"}]
  def literal([pred | args], p) when is_atom(pred) and not is_boolean(pred) and not is_nil(pred),
    do: args |> Enum.with_index(1) |> Enum.flat_map(fn {a, i} -> term(a, p ++ [i]) end)

  def literal(_, p), do: [{p, "a literal [:pred arg ...]"}]

  defp nested(l, p) when is_list(l), do: literal(l, p)
  defp nested(_, p), do: [{p, "a literal (vector)"}]

  defp lit, do: &nested/2

  # ---------------------------------------------------------------- records

  defp rule_common, do: %{id: kw(), owner: owner(), doc: str(), class: enum(@classes), recorded_at: date()}

  defp rule(%{kind: :superiority} = r, p),
    do: closed(r, p, Map.merge(rule_common(), %{kind: fn _, _ -> [] end, pred: kw(), order: vec_of(owner())}), %{superior_to() => vec_of(kw())})

  defp rule(r, p) when is_map(r),
    do:
      closed(r, p, Map.merge(rule_common(), %{kind: enum(~w(strict defeasible defeater incompatible)a), head: lit(), body: vec_of(lit())}),
        %{superior_to() => vec_of(kw())})

  defp rule(_, p), do: [{p, "a rule (map)"}]

  defp superior_to, do: :"superior-to"

  defp claim_core,
    do: %{id: kw(), assertion: lit(), asserted_by: owner(), asserted_at: date(), valid_from: date(), recorded_at: date()}

  defp claim_opt,
    do: %{valid_to: maybe(date()), backing: str(), qualifier: enum(["certainly", "presumably"]), warrant: kw()}

  # Flat claims (PLAN-v3-integrity §1.1): a parent names its members by id; links_resolve/2 checks the ids.
  defp claim_id, do: is(&(is_atom(&1) and Regex.match?(~r/^C[0-9]+(\.[0-9]+)?$/, Atom.to_string(&1))), "a claim id")

  defp claim(c, p),
    do:
      closed(c, p, Map.put(claim_core(), :about, re(~r/^[a-z]+:[A-Za-z0-9_\/]+$/)),
        Map.merge(claim_opt(), %{depends_on: vec_of(claim_id()), supports: vec_of(claim_id())}))

  defp links_resolve(s, p) do
    cs = if is_map(s) and is_list(s[:claims]), do: Enum.filter(s.claims, &is_map/1), else: []
    ids = MapSet.new(cs, &Map.get(&1, :id))
    for c <- cs, k <- [:depends_on, :supports], l = Map.get(c, k), is_list(l), x <- l, not MapSet.member?(ids, x),
      do: {p ++ [:claims, Map.get(c, :id), k], "names unknown claim #{inspect(x)}"}
  end

  defp record(%{kind: _} = r, p), do: rule(r, p)
  defp record(%{assertion: _} = c, p), do: claim(c, p)
  defp record(_, p), do: [{p, "a rule or claim record"}]

  # ---------------------------------------------------------------- the slice

  defp column(c, p),
    do: closed(c, p, %{id: re(~r/^col:[a-z_]+\/[a-z_]+$/), name: str(), type: enum(~w(id int enum bool date)a), doc: str()}, %{})

  defp table(t, p),
    do: closed(t, p, %{id: re(~r/^table:[a-z_]+$/), name: str(), doc: str(), columns: vec_of(&column/2)}, %{})

  defp concept(c, p) do
    closed(c, p, %{id: re(~r/^(measure|dim|entity|hier):[a-z_]+$/), name: kw(), kind: enum(~w(entity dimension hierarchy measure)a),
        tables: vec_of(re(~r/^table:/)), doc: str()},
      %{columns: vec_of(kw()), params: vec_of(kw()), sql: str(), "derived-by": kw(),
        additivity: enum(~w(additive semi-additive non-additive unknown)a), unsafe_dims: vec_of(kw())}) ++
      check(not is_map(c) or Map.has_key?(c, :sql) or Map.has_key?(c, :"derived-by"), p, "a concept has :sql or :derived-by") ++
      check(not is_map(c) or c[:kind] != :measure or Map.has_key?(c, :additivity), p, "a measure declares :additivity") ++
      check(not is_map(c) or c[:additivity] != :"semi-additive" or c[:unsafe_dims] not in [nil, []], p,
        "a semi-additive measure names its :unsafe_dims")
  end

  defp term_rec(t, p),
    do:
      closed(t, p, %{id: re(~r/^term:[a-z_]+$/), label: str(), synonyms: vec_of(str()), owner: owner(), definition: str()},
        %{concept: re(~r/^(measure|dim|entity|hier):/), see: vec_of(re(~r/^term:/))})

  defp asset(a, p), do: closed(a, p, %{id: str(), kind: enum([:vendor, :employee]), doc: str()}, %{})

  defp open_map(m, p, req) when is_map(m), do: Enum.flat_map(req, fn {k, f} -> if Map.has_key?(m, k), do: f.(m[k], p ++ [k]), else: [{p ++ [k], "missing required key"}] end)
  defp open_map(_, p, _), do: [{p, "a map"}]

  defp slice(s, p) do
    closed(s, p,
      %{
        "slice/version": is(&is_integer/1, "an integer"),
        today: date(),
        assets: vec_of(&asset/2),
        tables: vec_of(&table/2),
        concepts: vec_of(&concept/2),
        terms: vec_of(&term_rec/2),
        "code-lists": vec_of(&open_map(&1, &2, %{id: re(~r/^codes:/), values: vec_of(str())})),
        taxonomies:
          vec_of(&open_map(&1, &2, %{id: str(), "code-list": str(),
              tree: fn m, q -> if is_map(m), do: Enum.flat_map(m, fn {k, v} -> str().(k, q) ++ vec_of(str()).(v, q ++ [k]) end), else: [{q, "a map"}] end})),
        functional: fn m, q -> if is_map(m), do: Enum.flat_map(m, fn {k, v} -> kw().(k, q) ++ check(is_integer(v) and v > 0, q ++ [k], "a positive integer") end), else: [{q, "a map"}] end,
        rules: vec_of(&rule/2),
        claims: vec_of(&claim/2)
      }, %{}) ++ links_resolve(s, p)
  end

  # ---------------------------------------------------------------- negative tests (the same 15 as V3a and V3b)

  defp upd(s, path, f), do: update_in(s, Enum.map(path, &acc/1), f)
  defp acc(i) when is_integer(i), do: Access.at(i)
  defp acc(k), do: Access.key(k)

  def negatives do
    [
      {"concept with neither :sql nor :derived-by", &upd(&1, [:concepts, 0], fn c -> Map.drop(c, [:sql, :"derived-by"]) end)},
      {"unknown owner on a rule", &upd(&1, [:rules, 0, :owner], fn _ -> :marketing end)},
      {"rule variable without ?", &upd(&1, [:rules, 0, :head], fn h -> List.replace_at(h, 1, {:sym, "cc"}) end)},
      {"fetch filters not a map", &upd(&1, [:rules, 0, :body, 0], fn l -> List.replace_at(l, 2, ["cc", {:var, "?c"}]) end)},
      {"unknown arithmetic op in :is", &upd(&1, [:rules, 1, :body], fn b -> b ++ [[:is, {:var, "?x"}, [:*, 2, 3]]] end)},
      {"comparison with three arguments", &upd(&1, [:rules, 1, :body], fn b -> b ++ [[:<, {:var, "?x"}, 1, 2]] end)},
      {"bad date in a claim", &upd(&1, [:claims, 0, :asserted_at], fn _ -> "2026-3-1" end)},
      {"unknown key on a claim (closed map)", &upd(&1, [:claims, 0], fn c -> Map.put(c, :confidence, 0.9) end)},
      {"depends_on member not a claim id", &upd(&1, [:claims, 0], fn c -> Map.put(c, :depends_on, [:R101]) end)},
      {"superiority order with unknown owner",
       &upd(&1, [:rules], fn rs -> rs ++ [%{id: :R999, kind: :superiority, owner: :controller, class: :superiority, doc: "x", pred: :p, order: [:hr, :sales], recorded_at: hd(rs)[:recorded_at]}] end)},
      {"rule kind unknown", &upd(&1, [:rules, 0, :kind], fn _ -> :presumption end)},
      {"negated literal wrapping a non-literal", &upd(&1, [:rules, 0, :head], fn _ -> [:neg, "x"] end)},
      # PLAN-v3-integrity §1.5
      {"nested :subclaims (claims are flat)", fn s -> upd(s, [:claims, 0], &Map.put(&1, :subclaims, [Enum.at(s.claims, 1)])) end},
      {"measure without :additivity",
       &upd(&1, [:concepts], fn cs -> Enum.map(cs, fn c -> if c.kind == :measure, do: Map.delete(c, :additivity), else: c end) end)},
      {"dangling depends_on id", &upd(&1, [:claims, 0, :depends_on], fn l -> l ++ [:"C9.9"] end)}
    ]
  end
end
