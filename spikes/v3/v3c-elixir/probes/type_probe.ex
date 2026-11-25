# What Elixir 1.20's type checker reports (PLAN-v3cd §1.2.5). Each function plants one bug; the first
# four reproduce in shape runtime errors hit while building V3c (BadMapError, KeyError, child spec, KeyError).
# Compile against the prod beams, nothing is loaded or run:
#   elixirc -o <tmpdir> -pa _build/prod/lib/v3c/ebin probes/type_probe.ex
defmodule TypeProbe do
  # T1 (hit at runtime: BadMapError) a function's tuple result used as a struct
  def t1(st, recs), do: V3c.Store.add_records(st, recs, :ext).recs

  # T2 (hit at runtime: KeyError) atom key on a string-keyed row map from SQL
  def t2, do: V3c.SQL.fetch(:ancestors_or_self, [{"cc", "cc0001"}]).rows |> Enum.map(& &1.anc)

  # T3 (hit at runtime: app start failed) a {module, fun, opts} tuple as a child spec
  def t3, do: Supervisor.start_link([{Agent, &V3c.Store.new/0, [name: X]}], strategy: :one_for_one)

  # T4 (hit at runtime: KeyError :id) a required struct-less map field
  def t4(r), do: r.id

  # T5 unknown struct field
  def t5, do: V3c.Store.new().records

  # T6 a struct passed to a string function
  def t6, do: String.upcase(V3c.Store.new())

  # T7 binary concatenation on an atom result
  def t7, do: V3c.SQL.conn_name(1) <> "x"

  # T8 a clause on a result shape the callee never returns ({:proven, sups, sn} is a 3-tuple)
  def t8(ctx, l) do
    case V3c.Engine.evaluate(ctx, l) do
      {:proven, sups} -> sups
      _ -> nil
    end
  end

  # T9 arithmetic on a string literal
  def t9(x), do: x + "1"

  # T10 wrong arity to a local module function
  def t10, do: V3c.Engine.ground?(1, 2)
end
