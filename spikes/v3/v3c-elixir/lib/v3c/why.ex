defmodule V3c.Why do
  @moduledoc """
  V3c explanations (CONTRACT.md 'Why trees'), the same walk as V3a's why.pl and V3b's why.clj.

  explain_not: an absent node for the goal whose children are, per candidate rule, a rule node with the
  body literals that held and `failed`: the first literal that did not (recursively explained for derived
  literals, a 0-row fetch, a false builtin, a NAF literal whose goal is provable) or, when the body held,
  the defeated_by node of the attacker that won (or blocked). In-force claims asserting the goal that were
  defeated appear as claim nodes with a defeated_by child. Bodies are followed along their first solution.
  """
  alias V3c.Engine, as: E

  def defeat_node(ctx, id, {:defeated, a, _, _}) do
    sup = case E.sup(ctx, a.id, id) do
      [src | _] -> [%{type: "superior", winner: a.id, loser: id, source: src}]
      [] -> []
    end

    %{type: "defeated_by", id: a.id, target: id, children: [a.proof | sup]}
  end

  def defeat_node(_ctx, id, {:blocked, _, [a | _]}),
    do: %{type: "defeated_by", id: a.id, target: id, children: [a.proof], blocked: true}

  def defeat_node(_, _, _), do: nil

  @builtins [:<, :<=, :>, :>=, :=, :is, :as_of]

  defp failed_lit(ctx, [op | args] = l, s) do
    cond do
      op == :fetch ->
        [c, f | _] = args
        f2 = E.subst(f, s)

        if E.ground?(f2) do
          {rows, info, fs} = E.fetch_rows(c, f2)
          Map.merge(info, %{type: "fetch", concept: Atom.to_string(c), filters: Map.new(fs), rows: length(rows), row: nil})
        else
          %{type: "absent", goal: [:fetch, c]}
        end

      op == :not ->
        g = E.subst(hd(args), s)
        case Enum.at(E.prove(ctx, g), 0) do
          {_, p} -> %{type: "absent", goal: [:not, g], children: [p]}
          # propagation: [:not g] fails on a contested g too
          nil -> %{type: "contested_lit", goal: g}
        end

      op in @builtins ->
        %{type: "fact", goal: E.subst(l, s), holds: false}

      true ->
        explain_not(ctx, E.subst(l, s))
    end
  end

  # first solution of each literal in turn -> {s, done, failed node | nil}
  defp walk_body(_ctx, [], s, done), do: {s, Enum.reverse(done), nil}

  defp walk_body(ctx, [l | ls], s, done) do
    case Enum.at(E.lit(ctx, l, s), 0) do
      {s2, k} -> walk_body(ctx, ls, s2, [k | done])
      nil -> {s, Enum.reverse(done), failed_lit(ctx, l, s)}
    end
  end

  defp explain_rule(ctx, r, g, ev) do
    [head, bd] = E.rename([r.head, r.body])

    case E.unify(head, g, %{}) do
      nil ->
        nil

      s ->
        {s2, done, failed} = walk_body(ctx, bd, s, [])
        %{type: "rule", id: r.id, goal: E.subst(g, s2), children: done, failed: failed || defeat_node(ctx, r.id, ev)}
    end
  end

  def explain_not(ctx, g) do
    ev = if E.ground?(g), do: E.evaluate(ctx, g), else: {:none, []}
    rs = for r <- ctx.ix.rules, r.kind in [:strict, :defeasible], n = explain_rule(ctx, r, g, ev), n != nil, do: n

    cs =
      if E.ground?(g) and elem(ev, 0) not in [:proven, :none] do
        for c <- ctx.ix.claims, c.assertion == g, E.in_force?(c, ctx.d), dn = defeat_node(ctx, c.id, ev), dn != nil,
            do: %{E.claim_proof(c, g) | children: [dn]}
      else
        []
      end

    %{type: "absent", goal: g, children: rs ++ cs}
  end
end
