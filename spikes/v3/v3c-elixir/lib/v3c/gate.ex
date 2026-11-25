defmodule V3c.Gate do
  @moduledoc """
  The shared integrity gate (PLAN-v3-integrity §2), run as a subprocess: shared/integrity.py reads
  {load, added, withhold} on stdin and prints {ok, violations, ms}. One implementation for every engine.
  Session state (load paths, EDN texts added since) lives in the `V3c.GateState` agent; inside a
  hypothesis the texts and withheld ids are rebound in the process dictionary (hypotheses run inline).
  """

  def start(root, load) do
    st = %{root: root, load: load, added: []}
    case Agent.start(fn -> st end, name: V3c.GateState) do
      {:ok, _} -> :ok
      {:error, {:already_started, _}} -> Agent.update(V3c.GateState, fn _ -> st end)
    end
  end

  @doc "-> [] (admissible) or the violation maps."
  def violations(root, load, added, withhold) do
    req = Jason.encode!(%{load: load, added: added, withhold: withhold})
    f = Path.join(System.tmp_dir!(), "v3c-gate-#{System.unique_integer([:positive])}.json")
    File.write!(f, req)
    py = Path.join(root, ".venv/bin/python")
    gate = Path.join(root, "spikes/v3/shared/integrity.py")

    try do
      case System.cmd("sh", ["-c", "exec \"$0\" \"$1\" < \"$2\"", py, gate, f], cd: root, stderr_to_stdout: false) do
        {out, 0} -> Jason.decode!(out)["violations"]
        {out, n} -> [%{"violation" => "malformed-record", "members" => [], "message" => "integrity gate failed (#{n}): #{out}"}]
      end
    after
      File.rm(f)
    end
  end

  defp hyp, do: Process.get(:v3c_hyp)
  def texts, do: (case hyp() do {t, _} -> t; nil -> Agent.get(V3c.GateState, & &1.added) end)
  def withheld, do: (case hyp() do {_, w} -> w; nil -> [] end)

  @doc "nil when admissible, else the op's error result (state unchanged)."
  def check(op, added, withhold) do
    %{root: r, load: l} = Agent.get(V3c.GateState, & &1)
    case violations(r, l, added, withhold) do
      [] -> nil
      v -> %{error: %{op: op, violations: v}}
    end
  end

  def commit_add(texts), do: if(hyp() == nil, do: Agent.update(V3c.GateState, &%{&1 | added: texts}))

  @doc "Runs f with the hypothesis's texts and withheld ids bound."
  def within(texts, withheld, f) do
    old = Process.get(:v3c_hyp)
    Process.put(:v3c_hyp, {texts, withheld})
    try do
      f.()
    after
      if old, do: Process.put(:v3c_hyp, old), else: Process.delete(:v3c_hyp)
    end
  end
end
