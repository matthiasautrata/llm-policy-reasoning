defmodule V3c.CLI do
  @moduledoc """
  V3c CLI (CONTRACT.md): session script (JSON) on stdin -> {"results": [...], "load_ms": n} on stdout.
  Paths in `load` are relative to V3C_ROOT (the repo root). Optional config key "pool": SQL connections.
  """
  alias V3c.{EDN, Model, Ops, SQL, Store}

  @doc "Keywords -> names; logic variables -> their source name (\"?r\"); sets -> lists."
  def jsonable(x) do
    case x do
      nil -> nil
      b when is_boolean(b) -> b
      a when is_atom(a) -> a |> Atom.to_string() |> String.split("/") |> List.last()
      {:var, n} -> n |> String.split("#") |> hd()
      {:sym, s} -> s
      %MapSet{} = s -> s |> MapSet.to_list() |> Enum.map(&jsonable/1)
      m when is_map(m) -> Map.new(m, fn {k, v} -> {jsonable(k), jsonable(v)} end)
      l when is_list(l) -> Enum.map(l, &jsonable/1)
      t when is_tuple(t) -> inspect(t)
      v -> v
    end
  end

  def load(files, root) do
    Agent.update(V3c.State, fn _ -> Store.new() end)

    for f <- files do
      x = EDN.read!(File.read!(Path.join(root, f)))
      Model.validate!(f, x)

      if is_map(x) do
        for c <- x.concepts, c[:sql], do: SQL.register(c.name, c.sql, c[:params] || [])
        Agent.update(V3c.State, &Store.load_slice(&1, x))
      else
        Agent.update(V3c.State, fn st -> elem(Store.add_records(st, x, :ext), 0) end)
      end
    end

    :ok
  end

  def run(script) do
    root = System.get_env("V3C_ROOT") || File.cwd!()
    cfg = script["config"]
    t0 = System.monotonic_time(:microsecond)
    :ok = SQL.configure(cfg, root, pool: cfg["pool"] || 1)
    load(script["load"] || [], root)
    load_ms = (System.monotonic_time(:microsecond) - t0) / 1000
    out = %{results: Enum.map(script["ops"] || [], &Ops.run_op/1), load_ms: load_ms}
    out = if script["concurrent"], do: Map.put(out, :concurrent, Ops.run_concurrent(script["concurrent"])), else: out
    if script["after"], do: Map.put(out, :after, Enum.map(script["after"], &Ops.run_op/1)), else: out
  end

  def main do
    script = IO.read(:stdio, :eof) |> Jason.decode!()
    IO.write(Jason.encode!(jsonable(run(script))))
  end
end
