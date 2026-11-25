defmodule V3c.Engine do
  @moduledoc """
  V3c evaluator: the same defeasible logic as V3a's defeasible.pl and V3b's engine.clj, over EDN data as
  Elixir data.

  Literals are lists `[:pred arg ...]`; `[:neg l]` is the complement; variables are `{:var, "?x"}`. A body
  is evaluated left to right as a lazy Stream of substitutions (V3b: lazy seqs). `evaluate` decides a
  ground literal with ambiguity propagation (shared/SEMANTICS.md, PLAN-v3-integrity §4): proven, refuted
  or contested.
    {:proven, sups, sup_nodes}  a proven-bodied supporter; every live attacker beaten (team defeat)    proven
    {:defeated, att, sups, dn}  every live supporter beaten by a superior proven-bodied attacker;
                                att the smallest such id                                                refuted
    {:none, atts}               no live supporter                                                       refuted
    {:blocked, sups, unbeaten}  root: proven-bodied supporters meet proven-bodied unbeaten attackers    contested
    {:contested, rules, via}    downstream: only through contested body literals via                 contested
  Live = body not refuted (body3: solutions with v :proven | :contested).
  Supporters: strict/defeasible rules whose body holds, in-force claims. Attackers: the same for the
  complement and, for functional predicates, the same key with another value; defeaters attack only.
  Superiority: explicit :superior-to, strict over non-strict, asserter authority (a :superiority rule
  scoped to its :pred), later asserted_at for the same asserter.

  ctx: %{ix: store index, d: as-of date, memo: ref}. The memo is per op, in the op's process dictionary
  under its ref (V3b: an atom in the ctx).
  """
  alias V3c.SQL

  @type term_ :: {:var, String.t()} | String.t() | integer | float | boolean | atom | [term_] | map
  @type subst :: %{optional({:var, String.t()}) => term_}

  # ---------------------------------------------------------------- terms

  defguard is_lvar(x) when is_tuple(x) and tuple_size(x) == 2 and elem(x, 0) == :var

  def lvar?(x), do: is_lvar(x)

  def walk(t, s) when is_lvar(t) do
    case s do
      %{^t => v} -> walk(v, s)
      _ -> t
    end
  end

  def walk(t, _), do: t

  @spec unify(term_, term_, subst | nil) :: subst | nil
  def unify(_, _, nil), do: nil

  def unify(a, b, s) do
    a = walk(a, s)
    b = walk(b, s)

    cond do
      is_lvar(a) -> if a == b, do: s, else: Map.put(s, a, b)
      is_lvar(b) -> Map.put(s, b, a)
      is_list(a) and is_list(b) -> if length(a) == length(b), do: unify_all(a, b, s)
      is_map(a) and is_map(b) -> if a == b, do: s
      is_boolean(a) or is_boolean(b) -> if a === b, do: s
      is_number(a) and is_number(b) -> if a == b, do: s
      a === b -> s
      true -> nil
    end
  end

  defp unify_all([], [], s), do: s
  defp unify_all([x | xs], [y | ys], s), do: (case unify(x, y, s) do nil -> nil; s -> unify_all(xs, ys, s) end)

  def subst(t, s) do
    case walk(t, s) do
      l when is_list(l) -> Enum.map(l, &subst(&1, s))
      m when is_map(m) and not is_struct(m) -> Map.new(m, fn {k, v} -> {k, subst(v, s)} end)
      x -> x
    end
  end

  def ground?(t) when is_lvar(t), do: false
  def ground?(t) when is_list(t), do: Enum.all?(t, &ground?/1)
  def ground?(t) when is_map(t) and not is_struct(t), do: Enum.all?(Map.values(t), &ground?/1)
  def ground?(_), do: true

  @doc "Fresh variables for one use of a rule."
  def rename(t), do: rename(t, "#" <> Integer.to_string(System.unique_integer([:positive, :monotonic])))
  defp rename({:var, n}, sfx), do: {:var, n <> sfx}
  defp rename(l, sfx) when is_list(l), do: Enum.map(l, &rename(&1, sfx))
  defp rename(m, sfx) when is_map(m) and not is_struct(m), do: Map.new(m, fn {k, v} -> {k, rename(v, sfx)} end)
  defp rename(x, _), do: x

  defp rank(x) when is_lvar(x), do: 0
  defp rank(x) when is_number(x), do: 1
  defp rank(x) when is_atom(x), do: 2
  defp rank(x) when is_binary(x), do: 3
  defp rank(_), do: 4

  # Clojure's (str x) for keywords, booleans and nil, which V3b's order compares
  defp astr(nil), do: ""
  defp astr(b) when is_boolean(b), do: Atom.to_string(b)
  defp astr(a), do: ":" <> Atom.to_string(a)

  defp cmp(a, b) when a < b, do: -1
  defp cmp(a, b) when a > b, do: 1
  defp cmp(_, _), do: 0

  @doc "A standard order of terms (variables < numbers < atoms < strings < lists), lexicographic on lists."
  def tcmp(a, b) do
    {ra, rb} = {rank(a), rank(b)}

    cond do
      ra != rb -> cmp(ra, rb)
      is_list(a) -> Enum.zip_with(a, b, &tcmp/2) |> Enum.find(0, &(&1 != 0)) |> then(&if(&1 == 0, do: cmp(length(a), length(b)), else: &1))
      ra == 2 -> cmp(astr(a), astr(b))
      ra == 0 -> cmp(elem(a, 1), elem(b, 1))
      true -> cmp(a, b)
    end
  end

  def sort_terms(xs), do: xs |> Enum.uniq() |> Enum.sort(&(tcmp(&1, &2) <= 0))

  def pred_of([:neg, l]), do: pred_of(l)
  def pred_of([p | _]), do: p

  # ---------------------------------------------------------------- store access

  def in_force?(%{valid_from: f} = c, d), do: f <= d and (is_nil(c[:valid_to]) or d <= c.valid_to)

  defp rules_of(ctx, kinds), do: Enum.filter(ctx.ix.rules, &(&1.kind in kinds))
  def rule_by_id(ctx, id), do: ctx.ix.rule[id]
  def claim_by_id(ctx, id), do: ctx.ix.claim[id]

  @derivers [:strict, :defeasible]
  @attacking [:strict, :defeasible, :defeater]

  def claim_proof(c, goal),
    do: %{type: "claim", id: c.id, goal: goal, asserted_by: c.asserted_by, asserted_at: c.asserted_at, children: []}

  # ---------------------------------------------------------------- bodies

  # a stream whose construction is deferred until it is consumed (V3b's lazy seqs start no work on creation)
  defp defer(f), do: Stream.flat_map([nil], fn _ -> f.() end)

  defp ev(t, s) do
    case walk(t, s) do
      [op, a, b] when op in [:+, :-] ->
        {x, y} = {ev(a, s), ev(b, s)}
        if op == :+, do: x + y, else: x - y

      v when is_lvar(v) ->
        raise ArgumentError, "unbound #{elem(v, 1)}"

      v ->
        v
    end
  end

  def cmp_holds?(op, a, b) do
    {x, y} = {ev(a, %{}), ev(b, %{})}
    c = if is_number(x) and is_number(y), do: cmp(x * 1.0, y * 1.0), else: tcmp(x, y)

    case op do
      :< -> c < 0
      :<= -> c <= 0
      :> -> c > 0
      :>= -> c >= 0
      := -> c == 0
    end
  end

  @doc "Concept lookup with ground filters -> {rows, node info, filters [{string, value}]}."
  def fetch_rows(c, f) do
    unless ground?(f), do: raise(ArgumentError, "fetch #{c}: filters not ground: #{inspect(f)}")
    fs = for {k, v} <- f, do: {Atom.to_string(k), v}
    %{rows: rows, sql: sql, params: params, truncated: tr} = SQL.fetch(c, fs)
    {rows, %{sql: sql, params: params, truncated: tr}, fs}
  end

  @doc "One body literal under substitution s -> stream of {s', node}."
  def lit(ctx, [op | args] = l, s) do
    case op do
      :fetch ->
        [c, f, o] = args
        {rows, info, fs} = fetch_rows(c, subst(f, s))
        n = length(rows)

        Stream.flat_map(rows, fn row ->
          s2 =
            Enum.reduce_while(o, s, fn {col, t}, s ->
              case Map.fetch(row, Atom.to_string(col)) do
                {:ok, v} -> (case unify(t, v, s) do nil -> {:halt, nil}; s -> {:cont, s} end)
                :error -> {:halt, nil}
              end
            end)

          if s2, do: [{s2, Map.merge(info, %{type: "fetch", concept: Atom.to_string(c), filters: Map.new(fs), rows: n, row: row})}], else: []
        end)

      :not ->
        g = subst(hd(args), s)
        # a contested g is not absent
        absent = if ground?(g), do: value3(evaluate(ctx, g)) == :refuted, else: Enum.empty?(prove(ctx, g))
        if absent, do: [{s, %{type: "absent", goal: g}}], else: []

      :as_of ->
        case unify(hd(args), ctx.d, s) do
          nil -> []
          s2 -> [{s2, %{type: "fact", goal: [:as_of, ctx.d]}}]
        end

      :is ->
        [x, e] = args
        v = ev(e, s)

        case unify(x, v, s) do
          nil -> []
          s2 -> [{s2, %{type: "fact", goal: [:is, v, subst(e, s)]}}]
        end

      op when op in [:<, :<=, :>, :>=, :=] ->
        [a, b] = Enum.map(args, &subst(&1, s))
        if cmp_holds?(op, a, b), do: [{s, %{type: "fact", goal: [op, a, b]}}], else: []

      _derived ->
        g = subst(l, s)

        prove(ctx, g)
        |> Stream.flat_map(fn {inst, p} ->
          case unify(l, inst, s) do
            nil -> []
            s2 -> [{s2, p}]
          end
        end)
    end
  end

  @doc "-> stream of {s, kids}"
  def body(_ctx, [], s), do: [{s, []}]

  def body(ctx, [l | ls], s) do
    defer(fn ->
      lit(ctx, l, s)
      |> Stream.flat_map(fn {s1, k} -> Stream.map(body(ctx, ls, s1), fn {s2, ks} -> {s2, [k | ks]} end) end)
    end)
  end

  @doc "Rule r concluding goal l: stream of {s, proof node} (goal instantiated by the body)."
  def apply_rule(ctx, r, l) do
    [head, bd] = rename([r.head, r.body])

    case unify(head, l, %{}) do
      nil -> []
      s -> Stream.map(body(ctx, bd, s), fn {s2, kids} -> {s2, %{type: "rule", id: r.id, goal: subst(l, s2), children: kids}} end)
    end
  end

  defp first(stream), do: Enum.at(stream, 0)

  # ---------------------------------------------------------------- evaluation

  defp candidates(ctx, l) do
    Enum.flat_map(rules_of(ctx, @derivers), fn r -> Enum.map(apply_rule(ctx, r, l), fn {s, _} -> subst(l, s) end) end) ++
      for c <- ctx.ix.claims, in_force?(c, ctx.d), s = unify(l, c.assertion, %{}), s != nil, do: subst(l, s)
  end

  @doc "l defeasibly provable: stream of {ground instance, proof}."
  def prove(ctx, l) do
    proof = fn g ->
      case evaluate(ctx, g) do
        {:proven, [s1 | _], sn} -> [{g, Map.update!(s1.proof, :children, &(&1 ++ sn))}]
        _ -> []
      end
    end

    if ground?(l),
      do: defer(fn -> proof.(l) end),
      else: defer(fn -> candidates(ctx, l) |> Enum.filter(&ground?/1) |> sort_terms() end) |> Stream.flat_map(proof)
  end

  def supporters(ctx, l) do
    for(r <- rules_of(ctx, @derivers), {_, p} = first(apply_rule(ctx, r, l)) || {nil, nil}, p != nil, do: %{id: r.id, kind: r.kind, proof: p}) ++
      for c <- ctx.ix.claims, c.assertion == l, in_force?(c, ctx.d), do: %{id: c.id, kind: :claim, proof: claim_proof(c, l)}
  end

  @doc "{head, diff}: diff nil, or {v, v2} for a functional rival with the key fixed and value v2 /= v."
  def rivals(_ctx, [:neg, l]), do: [{l, nil}]

  def rivals(ctx, [p | args] = l) do
    n = ctx.ix.functional[p]
    base = [{[:neg, l], nil}]

    if n && length(args) == n + 1 do
      v2 = {:var, "?rival#" <> Integer.to_string(System.unique_integer([:positive, :monotonic]))}
      base ++ [{[p | Enum.take(args, n)] ++ [v2], {List.last(args), v2}}]
    else
      base
    end
  end

  defp differs?(nil, _), do: true
  defp differs?({v, v2}, s), do: v !== subst(v2, s)

  def attackers(ctx, l) do
    atts =
      for {h, diff} <- rivals(ctx, l) do
        for(r <- rules_of(ctx, @attacking),
            {s, p} = first(Stream.filter(apply_rule(ctx, r, h), fn {s, _} -> differs?(diff, s) end)) || {nil, nil},
            p != nil,
            do: %{id: r.id, kind: r.kind, head: subst(h, s), proof: p}) ++
          for c <- ctx.ix.claims, in_force?(c, ctx.d), s = unify(h, c.assertion, %{}), s != nil, differs?(diff, s),
              do: %{id: c.id, kind: :claim, head: c.assertion, proof: claim_proof(c, c.assertion)}
      end

    atts |> List.flatten() |> Enum.uniq_by(& &1.id)
  end

  @doc "Sources by which w is superior to l, in order: explicit, strict, authority:<id>, later."
  def sup(ctx, w, l) do
    {rw, rl, cw, cl} = {rule_by_id(ctx, w), rule_by_id(ctx, l), claim_by_id(ctx, w), claim_by_id(ctx, l)}

    if(rw && MapSet.member?(rw.superior_to, l), do: ["explicit"], else: []) ++
      if(rw && rw.kind == :strict && !(rl && rl.kind == :strict), do: ["strict"], else: []) ++
      if(cw && cl && cw.asserted_by != cl.asserted_by && pred_of(cw.assertion) == pred_of(cl.assertion),
        do:
          for(r <- rules_of(ctx, [:superiority]), r.pred == pred_of(cw.assertion),
              iw = Enum.find_index(r.order, &(&1 == cw.asserted_by)),
              il = Enum.find_index(r.order, &(&1 == cl.asserted_by)),
              iw != nil and il != nil and iw < il,
              do: "authority:" <> r.id),
        else: []) ++
      if(cw && cl && cw.asserted_by == cl.asserted_by && cw.asserted_at > cl.asserted_at, do: ["later"], else: [])
  end

  defp sup1(ctx, w, l), do: List.first(sup(ctx, w, l))

  def classify(_ctx, [], atts), do: {:none, atts}

  def classify(ctx, sups, atts) do
    beater = fn a -> Enum.find(sups, &sup1(ctx, &1.id, a.id)) end
    {beaten, unbeaten} = Enum.split_with(atts, &beater.(&1))
    sn = for a <- beaten, s = beater.(a), do: %{type: "superior", winner: s.id, loser: a.id, source: sup1(ctx, s.id, a.id)}

    cond do
      unbeaten == [] ->
        {:proven, sups, sn}

      a = Enum.find(unbeaten, fn a -> Enum.all?(sups, &sup1(ctx, a.id, &1.id)) end) ->
        {:defeated, a, sups, for(s <- sups, do: %{type: "superior", winner: a.id, loser: s.id, source: sup1(ctx, a.id, s.id)})}

      true ->
        {:blocked, sups, unbeaten}
    end
  end

  # ---------------------------------------------------------------- ambiguity propagation

  def value3({:proven, _, _}), do: :proven
  def value3({:defeated, _, _, _}), do: :refuted
  def value3({:none, _}), do: :refuted
  def value3({st, _, _}) when st in [:blocked, :contested], do: :contested

  @nonderived [:fetch, :not, :as_of, :is, :<, :<=, :>, :>=, :=]

  @doc "One body literal -> stream of {s, node, v, cl}; v :proven | :contested, cl the contested literals ([:not g] as g). Refuted solutions are dropped."
  def lit3(ctx, [op | args] = l, s) do
    cond do
      op == :not and ground?(subst(hd(args), s)) ->
        g = subst(hd(args), s)

        case value3(evaluate(ctx, g)) do
          :refuted -> [{s, %{type: "absent", goal: g}, :proven, []}]
          :contested -> [{s, %{type: "contested_lit", goal: g}, :contested, [g]}]
          :proven -> []
        end

      op in @nonderived ->
        Stream.map(lit(ctx, l, s), fn {s2, n} -> {s2, n, :proven, []} end)

      true ->
        g = subst(l, s)

        defer(fn ->
          gs = if ground?(g), do: [g], else: candidates3(ctx, g) |> Enum.filter(&ground?/1) |> sort_terms()

          Stream.flat_map(gs, fn gi ->
            ev = evaluate(ctx, gi)
            v = value3(ev)
            s2 = unify(l, gi, s)

            cond do
              s2 == nil or v == :refuted -> []
              v == :proven -> [{s2, Map.update!(hd(elem(ev, 1)).proof, :children, &(&1 ++ elem(ev, 2))), :proven, []}]
              true -> [{s2, %{type: "contested_lit", goal: gi}, :contested, [gi]}]
            end
          end)
        end)
    end
  end

  def body3(_ctx, [], s), do: [{s, [], :proven, []}]

  def body3(ctx, [l | ls], s) do
    defer(fn ->
      lit3(ctx, l, s)
      |> Stream.flat_map(fn {s1, k, v1, c1} ->
        Stream.map(body3(ctx, ls, s1), fn {s2, ks, v2, c2} ->
          {s2, [k | ks], if(v1 == :proven and v2 == :proven, do: :proven, else: :contested), c1 ++ c2}
        end)
      end)
    end)
  end

  defp apply_rule3(ctx, r, l) do
    [head, bd] = rename([r.head, r.body])

    case unify(head, l, %{}) do
      nil -> []
      s -> Stream.map(body3(ctx, bd, s), fn {s2, kids, v, cl} -> {s2, %{type: "rule", id: r.id, goal: subst(l, s2), children: kids}, v, cl} end)
    end
  end

  # the first proven solution, else the first (contested) one
  defp best(sols), do: Enum.find(sols, &(elem(&1, 2) == :proven)) || Enum.at(sols, 0)

  @doc "Instances of l with a live supporter."
  def candidates3(ctx, l) do
    Enum.flat_map(rules_of(ctx, @derivers), fn r -> Enum.map(apply_rule3(ctx, r, l), fn {s, _, _, _} -> subst(l, s) end) end) ++
      for c <- ctx.ix.claims, in_force?(c, ctx.d), s = unify(l, c.assertion, %{}), s != nil, do: subst(l, s)
  end

  defp supporters3(ctx, l) do
    for(r <- rules_of(ctx, @derivers), {_, p, v, cl} = best(apply_rule3(ctx, r, l)) || {nil, nil, nil, nil}, p != nil,
        do: %{id: r.id, kind: r.kind, proof: p, v: v, cl: cl}) ++
      for c <- ctx.ix.claims, c.assertion == l, in_force?(c, ctx.d), do: %{id: c.id, kind: :claim, proof: claim_proof(c, l), v: :proven, cl: []}
  end

  defp attackers3(ctx, l) do
    atts =
      for {h, diff} <- rivals(ctx, l) do
        for(r <- rules_of(ctx, @attacking),
            {s, p, v, cl} = best(Stream.filter(apply_rule3(ctx, r, h), fn {s, _, _, _} -> differs?(diff, s) end)) || {nil, nil, nil, nil},
            p != nil,
            do: %{id: r.id, kind: r.kind, head: subst(h, s), proof: p, v: v, cl: cl}) ++
          for c <- ctx.ix.claims, in_force?(c, ctx.d), s = unify(h, c.assertion, %{}), s != nil, differs?(diff, s),
              do: %{id: c.id, kind: :claim, head: c.assertion, proof: claim_proof(c, c.assertion), v: :proven, cl: []}
      end

    atts |> List.flatten() |> Enum.uniq_by(& &1.id)
  end

  def classify3(_ctx, [], atts), do: {:none, atts}

  def classify3(ctx, sups, atts) do
    pv? = &(&1.v == :proven)
    beats = fn xs, loser -> Enum.find_value(xs, fn x -> if pv?.(x), do: (case sup1(ctx, x.id, loser.id) do nil -> nil; src -> {x, src} end) end) end

    if Enum.all?(sups, &beats.(atts, &1)) do
      # -sigma, team form
      w = for(t <- sups, a <- atts, pv?.(a), sup1(ctx, a.id, t.id), do: a.id) |> Enum.uniq() |> Enum.sort() |> hd()
      dn = for t <- sups, {x, src} = beats.(atts, t), do: %{type: "superior", winner: x.id, loser: t.id, source: src}
      {:defeated, Enum.find(atts, &(&1.id == w)), sups, dn}
    else
      sp = Enum.filter(sups, pv?)
      un = Enum.reject(atts, &beats.(sups, &1))
      ap = Enum.filter(un, pv?)

      cond do
        sp != [] and un == [] ->
          {:proven, sp, for(a <- atts, {x, src} = beats.(sups, a), do: %{type: "superior", winner: x.id, loser: a.id, source: src})}

        sp != [] and ap != [] ->
          {:blocked, sp, ap}

        true ->
          {:contested, ids_of(sups ++ un), sort_terms(Enum.flat_map(sups ++ un, & &1.cl))}
      end
    end
  end

  @doc """
  Memoised per op. Re-entry guard (PLAN-v3-integrity §3.2): ctx carries the path of literals being
  evaluated; meeting one again is a dependency cycle the integrity gate did not stop
  (INTEGRITY_GATE=off). Throws {:defeat_cycle, goal_path}, a backstop, not a semantics.
  """
  def evaluate(ctx, l) do
    k = {ctx.d, l}
    memo = Process.get(ctx.memo, %{})

    case memo do
      %{^k => r} ->
        r

      _ ->
        path = Map.get(ctx, :path, [])
        if i = Enum.find_index(path, &(&1 == k)), do: throw({:defeat_cycle, Enum.map(Enum.drop(path, i), &elem(&1, 1)) ++ [l]})
        ctx = Map.put(ctx, :path, path ++ [k])
        r = classify3(ctx, supporters3(ctx, l), attackers3(ctx, l))
        Process.put(ctx.memo, Map.put(Process.get(ctx.memo, %{}), k, r))
        r
    end
  end

  def ids_of(xs), do: xs |> Enum.map(& &1.id) |> Enum.uniq() |> Enum.sort()
end
