defmodule V3c.Ops do
  @moduledoc """
  V3c System A surface (CONTRACT.md): decide, why_not, claims, resolve_term, describe, fetch, add,
  with_hypothesis (+ the test op sleep). Each op runs against one store value: main's (taken from the
  `V3c.State` agent when the op starts) or a hypothesis's (passed down explicitly).
  """
  alias V3c.{Why, SQL, Store, EDN, Model, Gate}
  alias V3c.Engine, as: E

  defp ctx(op, db) do
    ix = Store.index(db)
    %{ix: ix, d: op["as_of"] || ix.today, memo: {:memo, make_ref()}, db: db}
  end

  # ---------------------------------------------------------------- decide

  defp known_pred?(ix, p),
    do: Enum.any?(ix.rules, &(is_list(&1[:head]) and E.pred_of(&1.head) == p)) or Enum.any?(ix.claims, &(E.pred_of(&1.assertion) == p))

  defp scope(ix, p), do: if(Enum.any?(ix.terms, &(&1.id == "term:" <> Atom.to_string(p))), do: "UNDERDETERMINED", else: "OUT_OF_SCOPE")

  defp sub_nodes(x) when is_map(x) do
    ids = if x[:type] == "contested", do: Enum.map(x.rules, &%{id: &1}), else: []
    [x | ids] ++ Enum.flat_map([x[:children], x[:failed], x[:roots]], &sub_nodes/1)
  end

  defp sub_nodes(x) when is_list(x), do: Enum.flat_map(x, &sub_nodes/1)
  defp sub_nodes(_), do: []

  defp answer(c, st, v, sides, why) do
    owners = for(n <- sub_nodes(why), r = n[:id] && E.rule_by_id(c, n[:id]), r, do: Atom.to_string(r.owner)) |> Enum.uniq() |> Enum.sort()
    # IR-005: proven through a rule marked :closed_over :known_facts -> total only over the known facts
    closed = st == "ANSWER" and v not in [false, nil, []] and
               Enum.any?(sub_nodes(why), fn n -> r = n[:id] && E.rule_by_id(c, n[:id]); r && r[:closed_over] == :known_facts end)
    %{status: st, value: v, sides: sides, why: why, owners: owners, qualifier: if(closed, do: "total over known facts in declared scope")}
  end

  defp team_proofs(sups, sn), do: for(s <- sups, do: Map.update!(s.proof, :children, &(&1 ++ Enum.filter(sn, fn n -> n.winner == s.id end))))

  # Erlang's list order is V3b's lexi (element-wise, then length)
  defp sides(id_lists), do: id_lists |> Enum.uniq() |> Enum.sort()

  defp incompatible(c, g) do
    Enum.find_value(Enum.filter(c.ix.rules, &(&1.kind == :incompatible)), fn r ->
      case Enum.at(E.apply_rule(c, %{r | kind: :strict}, g), 0) do
        {_, p} -> {r.id, %{p | goal: [:neg, g]}}
        nil -> nil
      end
    end)
  end

  @doc """
  PLAN-v3-integrity §4: {sides, contested node} of a downstream-contested ground g. Follows contested body
  literals to the root conflicts (SEMANTICS.md, why tree).
  """
  def contested_why(c, g), do: cw(c, g, [g], MapSet.new(), [], [], %{})

  defp cw(_c, g, [], _seen, via, rules, roots) do
    rs = E.sort_terms(Map.keys(roots))
    {sides(Enum.flat_map(rs, &roots[&1].sides)),
     %{type: "contested", goal: g, via: E.sort_terms(via), rules: rules |> Enum.uniq() |> Enum.sort(), roots: Enum.map(rs, &roots[&1])}}
  end

  defp cw(c, g, [x | more], seen, via, rules, roots) do
    if MapSet.member?(seen, x) do
      cw(c, g, more, seen, via, rules, roots)
    else
      seen = MapSet.put(seen, x)

      case E.evaluate(c, x) do
        {:blocked, a, b} ->
          node = %{type: "conflict", goal: x, sides: sides([E.ids_of(a), E.ids_of(b)]), children: Enum.map(a, & &1.proof) ++ Enum.map(b, & &1.proof)}
          cw(c, g, more, seen, via, rules, Map.put(roots, x, node))

        {:contested, rs, vs} -> cw(c, g, more ++ vs, seen, via ++ vs, rules ++ rs, roots)
        _ -> cw(c, g, more, seen, via, rules, roots)
      end
    end
  end

  defp decide_ground(c, g) do
    case E.evaluate(c, g) do
      {:proven, sups, sn} ->
        why = team_proofs(sups, sn)

        case incompatible(c, g) do
          {iid, inode} -> answer(c, "CONFLICT", nil, sides([E.ids_of(sups), [iid]]), why ++ [inode])
          nil -> answer(c, "ANSWER", true, nil, why)
        end

      {:blocked, sups, un} ->
        answer(c, "CONFLICT", nil, sides([E.ids_of(sups), E.ids_of(un)]), Enum.map(sups, & &1.proof) ++ Enum.map(un, & &1.proof))

      {:contested, _, _} ->
        {sd, node} = contested_why(c, g)
        answer(c, "CONFLICT", nil, sd, [node])

      _ ->
        answer(c, "ANSWER", false, nil, [Why.explain_not(c, g)])
    end
  end

  defp vars_of(t) when is_list(t), do: t |> Enum.flat_map(&vars_of/1) |> Enum.uniq()
  defp vars_of(t), do: if(E.lvar?(t), do: [t], else: [])

  defp sups_of({st, sups, _}) when st in [:proven, :blocked], do: sups
  defp sups_of({:defeated, _, sups, _}), do: sups
  defp sups_of(_), do: []

  defp decide_open(c, g) do
    vs = vars_of(g)

    value = fn inst ->
      s = E.unify(g, inst, %{})
      case Enum.map(vs, &E.subst(&1, s)) do
        [x] -> x
        xs -> xs
      end
    end

    cands = E.candidates3(c, g) |> Enum.filter(&E.ground?/1) |> E.sort_terms()
    ges = for gi <- cands, do: {gi, E.evaluate(c, gi)}
    won = Enum.filter(ges, fn {_, ev} -> elem(ev, 0) == :proven end)
    cont = Enum.filter(ges, fn {_, ev} -> E.value3(ev) == :contested end)

    cond do
      # propagation: any contested instance contests the goal
      cont != [] ->
        parts =
          for {gi, ev} <- cont do
            case ev do
              {:blocked, a, b} -> {sides([E.ids_of(a), E.ids_of(b)]), Enum.map(a, & &1.proof) ++ Enum.map(b, & &1.proof)}
              _ -> (fn {sd, n} -> {sd, [n]} end).(contested_why(c, gi))
            end
          end

        answer(c, "CONFLICT", nil, sides(Enum.flat_map(parts, &elem(&1, 0))), Enum.flat_map(parts, &elem(&1, 1)))

      c.ix.functional[E.pred_of(g)] ->
      cond do
        length(won) == 1 ->
          [{gi, {_, sups, sn}}] = won
          answer(c, "ANSWER", value.(gi), nil, team_proofs(sups, sn))

        won == [] and ges != [] ->
          answer(c, "CONFLICT", nil,
            sides(for({_, ev} <- ges, ss = sups_of(ev), ss != [], do: E.ids_of(ss))),
            for({_, ev} <- ges, s <- sups_of(ev), do: s.proof))

        won == [] ->
          answer(c, "ANSWER", nil, nil, [Why.explain_not(c, g)])

        true ->
          %{answer(c, "CONFLICT", nil, nil, []) | value: Enum.map(won, fn {gi, _} -> value.(gi) end)}
      end

      true ->
      vws = for {gi, {_, sups, sn}} <- won, do: {value.(gi), team_proofs(sups, sn)}
      answer(c, "ANSWER", E.sort_terms(Enum.map(vws, &elem(&1, 0))), nil, Enum.flat_map(vws, &elem(&1, 1)))
    end
  end

  def decide(c, g) do
    p = E.pred_of(g)

    cond do
      not known_pred?(c.ix, p) -> %{status: scope(c.ix, p), value: nil, sides: nil, why: [], owners: [], qualifier: nil}
      E.ground?(g) -> decide_ground(c, g)
      true -> decide_open(c, g)
    end
  end

  def why_not(c, g) do
    case E.ground?(g) && E.evaluate(c, g) do
      {:proven, sups, sn} -> %{status: "ANSWER", value: true, why: team_proofs(sups, sn), why_not: []}
      _ -> %{status: "ANSWER", value: false, why_not: [Why.explain_not(c, g)]}
    end
  end

  # ---------------------------------------------------------------- claims

  defp failing?(s), do: s.standing not in ["holds", "holds_with_qualifier"]

  defp st(standing, defeater \\ nil, q \\ [], sides \\ nil), do: %{standing: standing, defeater: defeater, qualifier: q, sides: sides}

  defp own_standing({st, _, _}) when st in [:proven], do: st("holds")
  defp own_standing({:none, _}), do: st("holds")
  defp own_standing({:defeated, a, _, _}), do: st("rebutted", a.id)
  defp own_standing({:blocked, sups, un}), do: st("contested", nil, [], sides([E.ids_of(sups), E.ids_of(un)]))

  defp sub_standing(subs) do
    case Enum.find(subs, &(&1.role == "required" and failing?(&1))) do
      nil ->
        case for(s <- subs, s.role == "supporting" and failing?(s), do: s.id) |> Enum.sort() do
          [] -> st("holds")
          q -> st("holds_with_qualifier", nil, q)
        end

      # propagation: a contested required member contests the parent
      %{standing: "contested"} = s ->
        Map.put(st("contested", nil, [], s.sides), :via, s.id)

      s ->
        Map.put(st("rebutted", s.defeater), :via, s.id)
    end
  end

  def standing(c, cl) do
    subs = for sid <- cl.members, s = c.ix.claim[sid], do: standing(c, s)

    st =
      if E.in_force?(cl, c.d) do
        st0 =
          case E.evaluate(c, cl.assertion) do
            {:contested, _, _} -> st("contested", nil, [], elem(contested_why(c, cl.assertion), 0))
            ev -> own_standing(ev)
          end

        if st0.standing == "holds", do: sub_standing(subs), else: st0
      else
        st("not_in_force")
      end

    %{id: cl.id, about: cl.about, assertion: cl.assertion, asserted_by: cl.asserted_by, asserted_at: cl.asserted_at,
      valid_from: cl.valid_from, valid_to: cl[:valid_to], backing: cl[:backing], modal: cl[:qualifier],
      role: cl[:role]}
    |> Map.merge(st)
    |> Map.put(:subclaims, subs)
  end

  # ---------------------------------------------------------------- vocabulary, metadata

  def resolve_term(c, text) do
    ids =
      Store.terms_matching(c.db, Store.norm(text))
      |> Enum.flat_map(&(case Store.term_see(c.db, &1) do [] -> [&1]; see -> see end))
      |> Enum.uniq()
      |> Enum.sort()

    byid = Map.new(c.ix.terms, &{&1.id, &1})

    %{text: text, status: (case length(ids) do 0 -> "none"; 1 -> "concept"; _ -> "several" end),
      candidates: for(id <- ids, t = byid[id], do: %{term: id, definition: t.definition, owner: Atom.to_string(t.owner)})}
  end

  def describe(c, a) do
    find = fn k -> Enum.find(Map.fetch!(c.ix, k), &(&1.id == a)) end

    {k, doc, b} =
      cond do
        x = find.(:assets) -> {Atom.to_string(x.kind), x.doc, nil}
        x = find.(:terms) -> {"term", x.definition, x[:concept]}
        x = find.(:concepts) ->
          {Atom.to_string(x.kind), x.doc,
           %{concept: Atom.to_string(x.name), tables: x[:tables] || [], params: Enum.map(x[:params] || [], &Atom.to_string/1), sql: x[:sql]}}
        x = find.(:tables) -> {"table", x.doc, nil}
        x = find.(:columns) -> {"column", x.doc, nil}
        true -> {nil, nil, nil}
      end

    %{status: if(k, do: "ANSWER", else: "OUT_OF_SCOPE"), asset: a, kind: k, doc: doc, bindings: b, claims: Store.claims_about(c.db, a)}
  end

  # ---------------------------------------------------------------- dispatch

  defp read_recs(text) do
    recs = EDN.read!(text)
    Model.validate!("records", recs)
    recs
  end

  defp with_hypothesis(op, db) do
    ts = Gate.texts() ++ if(op["add"], do: [op["add"]], else: [])
    w = op["withhold"] || []
    ws = Gate.withheld() ++ w

    Gate.check("with_hypothesis", ts, ws) ||
      (
        recs = if op["add"], do: read_recs(op["add"]), else: []
        {db2, ids} = Store.hypothesis(db, w, recs)
        %{results: Gate.within(ts, ws, fn -> Enum.map(op["ops"], &run_op(&1, db2)) end), added: ids, withheld: w}
      )
  end

  defp lit_edn(l) when is_list(l), do: "[" <> Enum.map_join(l, " ", &lit_edn/1) <> "]"
  defp lit_edn(a) when is_atom(a), do: ":" <> Atom.to_string(a)
  defp lit_edn(x), do: inspect(x)

  defp do_op(op, db) do
    case op["op"] do
      "decide" -> decide(ctx(op, db), EDN.read!(op["goal"]))
      "why_not" -> why_not(ctx(op, db), EDN.read!(op["goal"]))
      "claims" ->
        c = ctx(op, db)
        %{asset: op["asset"], claims: for(cl <- c.ix.claims, cl.about == op["asset"], is_nil(cl.parent), do: standing(c, cl))}
      "resolve_term" -> resolve_term(ctx(op, db), op["text"])
      "describe" -> describe(ctx(op, db), op["asset"])
      "fetch" ->
        %{rows: rows, sql: sql, params: params, truncated: tr} =
          SQL.fetch(String.to_existing_atom(op["concept"]), Enum.sort(op["filters"] || %{}))
        %{concept: op["concept"], filters: op["filters"], rows: rows, sql: sql, params: params, row_count: length(rows), truncated: tr}
      "add" ->
        ts = Gate.texts() ++ [op["edn"]]

        Gate.check("add", ts, Gate.withheld()) ||
          (
            recs = read_recs(op["edn"])
            r = %{added: Agent.get_and_update(V3c.State, fn st -> {st2, ids} = Store.add_records(st, recs, :ext); {ids, st2} end)}
            Gate.commit_add(ts)
            r
          )
      "with_hypothesis" -> with_hypothesis(op, db)
      "sleep" ->
        t0 = System.system_time(:millisecond)
        Process.sleep(op["ms"])
        %{t0: t0, t1: System.system_time(:millisecond)}
      other -> raise ArgumentError, "unknown op #{other}"
    end
  end

  defp short(e), do: e.__struct__ |> Module.split() |> List.last()

  def run_op(op, db \\ nil) do
    SQL.begin_op()
    t0 = System.monotonic_time(:microsecond)
    db = db || Agent.get(V3c.State, & &1)

    r =
      try do
        do_op(op, db)
      rescue
        e -> %{status: "ERROR", error: "#{short(e)}: #{Exception.message(e)}"}
      catch
        :exit, reason -> %{status: "ERROR", error: "exit: #{inspect(reason, limit: 5)}"}
        # the re-entry guard, in the integrity gate's format
        {:defeat_cycle, p} ->
          ms = Enum.map(p, &lit_edn/1)
          %{status: "ERROR", error: %{op: op["op"], violations: [%{violation: "defeat-cycle", members: ms, path: p, message: "re-entered " <> hd(ms)}]}}
      after
        for {{:memo, _} = k, _} <- Process.get(), do: Process.delete(k)
      end

    ms = (System.monotonic_time(:microsecond) - t0) / 1000
    Map.merge(r, %{ms: ms, sql_log: if(op["op"] == "with_hypothesis", do: [], else: SQL.take_log())})
  end

  @doc "Test mode (shared/isolation.py): each op list in its own process; results stamped with :t_start/:t_end (epoch ms)."
  def run_concurrent(lists) do
    timed = fn op ->
      a = System.system_time(:millisecond)
      r = run_op(op)
      Map.merge(r, %{t_start: a, t_end: System.system_time(:millisecond)})
    end

    lists |> Enum.map(fn ops -> Task.async(fn -> Enum.map(ops, timed) end) end) |> Task.await_many(:infinity)
  end
end
