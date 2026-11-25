# BEAM probes (PLAN-v3cd §1.2.4). Run from v3c-elixir/:
#   MIX_ENV=prod mix run probes/beam_probes.exs [duckdb|postgres] [all|super|par|reload]
# Writes results/beam-<backend>.json.
#
#  super   kill the SQL connection process mid-decide-loop: what the in-flight op returns, when the
#          supervisor (rest_for_one under V3c.SQL.Sup) has it back, whether later ops are correct
#  par     the bench's 200 seeded decides: 1 process on 1 connection vs 8 processes on 8 connections
#  reload  recompile and load V3c.Engine (modified) while 8 processes run decides: dropped requests?
[backend, which] =
  case System.argv() do
    [b, w] -> [b, w]
    [b] -> [b, "all"]
    [] -> ["duckdb", "all"]
  end

root = Path.expand("../../..", File.cwd!())
cfg = %{"backend" => backend, "fetch_limit" => 10_000, "duckdb" => "spikes/v3/shared/slice.duckdb",
        "postgres" => System.get_env("SPIKE_V3_PG", "dbname=spike_v3")}

# the bench's request ids: Python random.Random(7).randrange(1, 100001), reproduced by a python call
reqs =
  System.cmd("python3", ["-c", "import random; r = random.Random(7); print(' '.join(f'r{r.randrange(1, 100001):06d}' for _ in range(200)))"])
  |> elem(0) |> String.split()

setup = fn pool ->
  :ok = V3c.SQL.configure(cfg, root, pool: pool)
  V3c.CLI.load(["spikes/v3/shared/slice.edn"], root)
end

decide = fn r -> V3c.Ops.run_op(%{"op" => "decide", "goal" => ~s([:approved "#{r}"])}) end
pct = fn xs, p -> xs = Enum.sort(xs); Enum.at(xs, min(length(xs) - 1, trunc(p * length(xs)))) end
now = fn -> System.monotonic_time(:microsecond) / 1000 end
out = %{backend: backend}

# reference answers, sequential, one connection
setup.(1)
ref = Map.new(reqs, fn r -> {r, decide.(r).value} end)
IO.puts("#{backend}: reference: #{Enum.count(ref, fn {_, v} -> v == true end)}/200 approved")

# ------------------------------------------------------------------ super
out =
  if which in ["all", "super"] do
    setup.(1)
    parent = self()
    loop = Task.async(fn ->
      for {r, i} <- Enum.with_index(reqs) do
        if i == 50, do: send(parent, :go)
        if i == 50, do: receive(do: (:killed -> :ok))
        t = now.()
        res = decide.(r)
        {i, r, res.status, res[:value], res[:error], t, now.()}
      end
    end)
    receive do: (:go -> :ok)
    victim = Process.whereis(V3c.SQL.conn_name(1))
    killer = Task.async(fn ->
      # kill once the op that starts next has been running ~1 ms (it is in or near a SQL call)
      Process.sleep(1)
      t = now.()
      Process.exit(victim, :kill)
      t
    end)
    send(loop.pid, :killed)
    t_kill = Task.await(killer)
    # when is a connection registered again?
    t_back = Stream.repeatedly(fn -> Process.sleep(0); Process.whereis(V3c.SQL.conn_name(1)) end)
             |> Enum.find(&(&1 && &1 != victim)) && now.()
    rows = Task.await(loop, :infinity)
    errs = for {i, r, "ERROR", _, e, _, _} <- rows, do: %{i: i, req: r, error: String.slice(e, 0, 160)}
    wrong = for {i, r, st, v, _, _, _} <- rows, st != "ERROR", v != ref[r], do: %{i: i, req: r}
    after_ok = rows |> Enum.drop_while(fn {_, _, st, _, _, _, _} -> st != "ERROR" end) |> Enum.drop(1)
               |> Enum.all?(fn {_, r, st, v, _, _, _} -> st != "ERROR" and v == ref[r] end)
    s = %{errors: errs, wrong_answers: length(wrong), restart_ms: Float.round(t_back - t_kill, 2),
          ops_after_first_error_all_correct: after_ok, sql_sup_children: :supervisor.count_children(V3c.SQL.Sup)}
    IO.puts("super: #{inspect(s, limit: :infinity)}")
    Map.put(out, :supervision, Map.update!(s, :sql_sup_children, &Map.new/1))
  else
    out
  end

# ------------------------------------------------------------------ par
run_par = fn n ->
  setup.(n)
  chunks = reqs |> Enum.with_index() |> Enum.group_by(fn {_, i} -> rem(i, n) end, &elem(&1, 0)) |> Map.values()
  # warm-up pass (JIT-less BEAM: warms the SQL side and the persistent terms)
  Enum.each(Enum.take(reqs, 20), decide)
  t0 = now.()
  res = chunks |> Enum.map(fn rs -> Task.async(fn -> Enum.map(rs, &{&1, decide.(&1)}) end) end) |> Task.await_many(:infinity) |> Enum.concat()
  wall = now.() - t0
  ms = Enum.map(res, fn {_, x} -> x.ms end)
  %{procs: n, wall_ms: Float.round(wall, 1), decides_per_s: Float.round(200 / wall * 1000, 1),
    p50: pct.(ms, 0.5), p95: pct.(ms, 0.95), errors: Enum.count(res, fn {_, x} -> x.status == "ERROR" end),
    same_answers: Enum.all?(res, fn {r, x} -> x.value == ref[r] end)}
end

out =
  if which in ["all", "par"] do
    p = [run_par.(1), run_par.(8)]
    IO.puts("par: #{inspect(p)}")
    Map.put(out, :parallel, p ++ [%{schedulers: System.schedulers_online()}])
  else
    out
  end

# ------------------------------------------------------------------ reload
out =
  if which in ["all", "reload"] do
    setup.(8)
    src = File.read!("lib/v3c/engine.ex")
    v2 = String.replace(src, ~r/defmodule V3c.Engine do\n/, "defmodule V3c.Engine do\n  def __probe_version__, do: 2\n", global: false)
    v3 = String.replace(v2, "def __probe_version__, do: 2", "def __probe_version__, do: 3")
    stop = :atomics.new(1, [])
    workers = for w <- 1..8 do
      Task.async(fn ->
        Stream.iterate(0, &(&1 + 1))
        |> Enum.reduce_while([], fn i, acc ->
          if :atomics.get(stop, 1) == 1 do
            {:halt, acc}
          else
            r = Enum.at(reqs, rem(i * 8 + w, 200))
            x = decide.(r)
            v = try do: V3c.Engine.__probe_version__(), rescue: (_ -> 1)
            {:cont, [{r, x.status, x.value, v} | acc]}
          end
        end)
      end)
    end
    Process.sleep(300)
    {load2_us, _} = :timer.tc(fn -> Code.compile_string(v2, "lib/v3c/engine.ex") end)
    Process.sleep(300)
    # a second load purges the oldest version: any process still executing v1 code would be killed
    {load3_us, _} = :timer.tc(fn -> Code.compile_string(v3, "lib/v3c/engine.ex") end)
    Process.sleep(300)
    :atomics.put(stop, 1, 1)
    rows = workers |> Task.await_many(:infinity) |> Enum.concat()
    s = %{requests: length(rows), errors: Enum.count(rows, &(elem(&1, 1) == "ERROR")),
          wrong_answers: Enum.count(rows, fn {r, st, v, _} -> st != "ERROR" and v != ref[r] end),
          by_version: rows |> Enum.frequencies_by(&elem(&1, 3)),
          load_ms: [Float.round(load2_us / 1000, 1), Float.round(load3_us / 1000, 1)],
          workers_alive_to_end: length(workers)}
    IO.puts("reload: #{inspect(s)}")
    Map.put(out, :hot_reload, s)
  else
    out
  end

File.write!("results/beam-#{backend}#{if which == "all", do: "", else: "-" <> which}.json", Jason.encode!(V3c.CLI.jsonable(out), pretty: true))
