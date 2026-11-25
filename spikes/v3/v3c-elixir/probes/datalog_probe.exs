# ex_datalog 0.5.0 probe (PLAN-v3cd §1.2.1). Run from v3c-elixir/:  MIX_ENV=prod mix run probes/datalog_probe.exs
#
#  A  the strict recursive part (ancestors_or_self, reporting_chain) as ex_datalog rules over edges
#     fetched through SQL, compared with the slice's recursive CTEs, timed (semi-naive vs magic sets)
#  B  Explain derivation trees for one fact, mapped to the contract's why-node shape
#  C  a BEAM callback as the fetch hook
#  D  the defeasible layer as an ex_datalog meta-program
alias ExDatalog.{Program, Knowledge, Explain, Callback, Term}

root = Path.expand("../../..", File.cwd!())
cfg = %{"backend" => "duckdb", "duckdb" => "spikes/v3/shared/slice.duckdb", "fetch_limit" => 100_000}
:ok = V3c.SQL.configure(cfg, root)
slice = V3c.EDN.read!(File.read!(Path.join(root, "spikes/v3/shared/slice.edn")))
for c <- slice.concepts, c[:sql], do: V3c.SQL.register(c.name, c.sql, c[:params] || [])

q = fn sql ->
  {:ok, r} = Adbc.Connection.query(V3c.SQL.conn_name(1), sql, [])
  Enum.flat_map(r.data, fn cols -> cols |> Enum.map(&Adbc.Column.to_list/1) |> Enum.zip() |> Enum.map(&Tuple.to_list/1) end)
end

time = fn f -> {us, v} = :timer.tc(f); {Float.round(us / 1000, 2), v} end

# ---------------------------------------------------------------- A: closure over fetched edges
{fetch_ms, {cc, emp}} = time.(fn -> {q.("SELECT id, parent FROM cc"), q.("SELECT id, manager, role FROM emp")} end)
IO.puts("A. fetched #{length(cc)} cc rows, #{length(emp)} emp rows in #{fetch_ms} ms (whole edge tables: bypasses fetch/fetch_limit)")

base =
  Program.new()
  |> Program.add_relation("cc", [:string, :any])
  |> Program.add_relation("emp", [:string, :any, :string])
  |> Program.add_relation("anc", [:string, :string, :integer])
  |> Program.add_relation("chain", [:string, :string, :integer])
  |> Program.add_facts(for [i, p] <- cc, do: {"cc", [i, p]})
  |> Program.add_facts(for [i, m, r] <- emp, do: {"emp", [i, m, r]})
# anc(C, A, D): A is C's ancestor-or-self at depth D (the CTE's depth column)
anc_rules = fn p -> p
  |> Program.add_rule({"anc", [:C, :C, 0]}, [{:positive, {"cc", [:C, :_]}}])
  |> Program.add_rule({"anc", [:C, :A, :D]}, [{:positive, {"anc", [:C, :X, :D0]}}, {:positive, {"cc", [:X, :A]}}], [{:neq, :A, nil}, {:add, :D0, 1, :D}])
end
# chain(E, M, D): M approves for E at depth D (manager, manager's manager, ...)
chain_rules = fn p -> p
  |> Program.add_rule({"chain", [:E, :M, 1]}, [{:positive, {"emp", [:E, :M, :_]}}], [{:neq, :M, nil}])
  |> Program.add_rule({"chain", [:E, :M2, :D]}, [{:positive, {"chain", [:E, :M, :D0]}}, {:positive, {"emp", [:M, :M2, :_]}}], [{:neq, :M2, nil}, {:add, :D0, 1, :D}])
end
prog = base |> anc_rules.() |> chain_rules.()

# The default timeout_ms (30 s per stratum) TRUNCATES silently unless stats.termination is checked:
# a first run of this probe compared a :timeout result with the CTEs and found it short by one level.
mat = fn p, rel, opts ->
  {ms, {:ok, k}} = time.(fn -> ExDatalog.materialize(p, Keyword.merge([timeout_ms: 600_000], opts)) end)
  {ms, k, k.stats.termination, k.stats.iterations, MapSet.size(Knowledge.get(k, rel))}
end
full = System.get_env("FULL") == "1"   # the full chain materialisations take ~90 s; FULL=1 runs them
if full do
  {t30, _, term30, _, n30} = mat.(base |> chain_rules.(), "chain", timeout_ms: 30_000)
  IO.puts("   chain with the default 30 s timeout: #{t30} ms, termination #{term30}, #{n30} facts")
end

{anc_ms, ka, anc_term, anc_it, _} = mat.(base |> anc_rules.(), "anc", [])
{anc_x_ms, _, _, _, _} = mat.(base |> anc_rules.(), "anc", explain: true)
{ch_ms, kc, ch_term, ch_it, _} = if full, do: mat.(base |> chain_rules.(), "chain", []), else: {0, nil, :skipped, 0, 0}
anc = Knowledge.get(ka, "anc")
chain = if full, do: Knowledge.get(kc, "chain"), else: nil
IO.puts("   anc: #{MapSet.size(anc)} facts, #{anc_ms} ms (explain: #{anc_x_ms} ms), #{anc_it} iterations, #{anc_term}")
if full, do: IO.puts("   chain: #{MapSet.size(chain)} facts, #{ch_ms} ms, #{ch_it} iterations, #{ch_term}")

# compare with all-pairs versions of the slice's recursive CTEs (one statement each)
{cte_ms, {anc_sql, chain_sql}} =
  time.(fn ->
    {q.("WITH RECURSIVE a(cc, anc, depth) AS (SELECT id, id, 0 FROM cc UNION ALL SELECT a.cc, c.parent, a.depth + 1 FROM a JOIN cc c ON c.id = a.anc WHERE c.parent IS NOT NULL) SELECT cc, anc, depth FROM a")
     |> MapSet.new(&List.to_tuple/1),
     q.("WITH RECURSIVE ch(emp, approver, depth) AS (SELECT id, manager, 1 FROM emp WHERE manager IS NOT NULL UNION ALL SELECT ch.emp, e.manager, ch.depth + 1 FROM ch JOIN emp e ON e.id = ch.approver WHERE e.manager IS NOT NULL) SELECT emp, approver, depth FROM ch")
     |> MapSet.new(&List.to_tuple/1)}
  end)
IO.puts("   all-pairs CTEs (2 statements): #{cte_ms} ms; #{MapSet.size(anc_sql)} anc, #{MapSet.size(chain_sql)} chain rows")
IO.puts("   anc == CTE: #{anc == anc_sql}   chain == CTE: #{if full, do: chain == chain_sql, else: :skipped}")
# spot check against the slice's own per-key concept
spot = V3c.SQL.fetch(:ancestors_or_self, [{"cc", "cc0077"}]).rows |> MapSet.new(&{&1["cc"], &1["anc"], &1["depth"]})
IO.puts("   slice concept ancestors_or_self(cc0077) subset of anc: #{MapSet.subset?(spot, anc)}")

# magic sets for one goal: positive program, ground bound position
g = "cc0077"
{ms_ms, ms_res} = time.(fn -> ExDatalog.materialize(base |> anc_rules.(), strategy: :magic_sets, goal: {"anc", [g, :_, :_]}, timeout_ms: 600_000) end)
ms_ok = case ms_res do
  {:ok, km} ->
    got = Knowledge.get(km, "anc") |> Enum.filter(&(elem(&1, 0) == g)) |> MapSet.new()
    want = anc |> Enum.filter(&(elem(&1, 0) == g)) |> MapSet.new()
    "#{got == want} (#{MapSet.size(Knowledge.get(km, "anc"))} anc facts returned, termination #{km.stats.termination})"
  {:error, e} -> "error #{inspect(e)}"
end
IO.puts("   magic sets, goal anc(#{g}, _, _): #{ms_ms} ms, same answer: #{ms_ok}")
e0 = "e10523"
{ms2_ms, ms2} = time.(fn -> ExDatalog.materialize(base |> chain_rules.(), strategy: :magic_sets, goal: {"chain", [e0, :_, :_]}, timeout_ms: 600_000) end)
case ms2 do
  {:ok, km} -> IO.puts("   magic sets, goal chain(#{e0}, _, _): #{ms2_ms} ms, #{MapSet.size(Knowledge.get(km, "chain"))} facts, equal to CTE: #{MapSet.new(Knowledge.get(km, "chain")) == (chain_sql |> Enum.filter(&(elem(&1, 0) == e0)) |> MapSet.new())}")
  {:error, e} -> IO.puts("   magic sets chain: error #{inspect(e)}")
end

# ---------------------------------------------------------------- B: Explain
# Explain.explain/3 on the full anc relation (9497 facts) did not return: 12.7 GB RSS after ~2 min, killed.
# Cause (explain.ex, expand_body_relation/4): provenance stores only the rule id per fact, not the bindings,
# so each positive body atom's children are ALL tuples of that body relation, each expanded recursively.
# Demonstrated on a 4-node chain plus one unrelated edge:
#   cc: x3 -> x2 -> x1 -> x0 (root), y1 -> x0
small = for {i, p} <- [{"x0", nil}, {"x1", "x0"}, {"x2", "x1"}, {"x3", "x2"}, {"y1", "x0"}], do: {"cc", [i, p]}
ps = Program.new() |> Program.add_relation("cc", [:string, :any]) |> Program.add_relation("anc", [:string, :string, :integer])
     |> Program.add_facts(small) |> anc_rules.()
{:ok, kx} = ExDatalog.materialize(ps, explain: true)
deep = {"x2", "x0", 2}
{:ok, tree} = Explain.explain(kx, "anc", deep)
count = fn count, t -> case t do :base_fact -> 1; %Explain.Node{children: ch} -> 1 + Enum.sum(Enum.map(ch, &count.(count, &1))) end end
facts = fn facts, t -> case t do :base_fact -> []; %Explain.Node{fact: f, children: ch} -> [f | Enum.flat_map(ch, &facts.(facts, &1))] end end
top = Enum.map(tree.children, fn :base_fact -> :base_fact; n -> n.fact end)
IO.puts("B. Explain anc#{inspect(deep)} on the 5-edge graph: rule #{tree.rule_id}, #{length(tree.children)} direct children, #{count.(count, tree)} nodes in all")
IO.puts("   direct children: #{inspect(top)}")
IO.puts("   derived facts named anywhere in the tree: #{facts.(facts, tree) |> Enum.uniq() |> length()} of #{MapSet.size(Knowledge.get(kx, "anc"))} anc facts (incl. unrelated y1 ones: #{facts.(facts, tree) |> Enum.any?(&(elem(&1, 0) == "y1"))})")
IO.puts("   a correct proof needs 3 rule nodes: anc(x2,x0,2) <- anc(x2,x1,1) + cc(x1,x0); anc(x2,x1,1) <- anc(x2,x2,0) + cc(x2,x1); anc(x2,x2,0) <- cc(x2,x1)")

# ---------------------------------------------------------------- C: a callback as the fetch hook
defmodule Probe.Fetch do
  # a value callback: one SQL statement per binding, returns ONE value (the rows as a list)
  def ancestors(c), do: V3c.SQL.fetch(:ancestors_or_self, [{"cc", c}]).rows |> Enum.map(& &1["anc"])
  def is_ancestor(c, a), do: a in ancestors(c)
end

cb =
  Program.new()
  |> Program.add_relation("goal_cc", [:string])
  |> Program.add_relation("ancs", [:string, :any])
  |> Program.add_relation("under_root", [:string])
  |> Program.add_fact("goal_cc", [g])
  |> Program.add_rule(%ExDatalog.Rule{
       head: ExDatalog.Atom.new("ancs", [Term.var("C"), Term.var("L")]),
       body: [{:positive, ExDatalog.Atom.new("goal_cc", [Term.var("C")])}, {:callback, Callback.new(Probe.Fetch, :ancestors, [Term.var("C")], Term.var("L"))}]})
  |> Program.add_rule(%ExDatalog.Rule{
       head: ExDatalog.Atom.new("under_root", [Term.var("C")]),
       body: [{:positive, ExDatalog.Atom.new("goal_cc", [Term.var("C")])}, {:callback, Callback.new(Probe.Fetch, :is_ancestor, [Term.var("C"), Term.const("cc0001")])}]})

V3c.SQL.begin_op()
case ExDatalog.materialize(cb) do
  {:ok, kc} ->
    IO.puts("C. callback fetch: ancs = #{inspect(Knowledge.get(kc, "ancs"))}; under_root = #{inspect(Knowledge.get(kc, "under_root"))}")
    IO.puts("   SQL log entries in the calling process: #{length(V3c.SQL.take_log())} (the callbacks ran in spawn_monitor'ed processes: their SQL is invisible to the op's log and cache)")
    IO.puts("   a callback returns ONE value per binding: a multi-row fetch comes back as a list term, not as rows the rule can join on")
  {:error, e} -> IO.puts("C. callback program rejected: #{inspect(e)}")
end

# ---------------------------------------------------------------- D: the defeasible layer as a meta-program
# Reified: rule(R, Head), body(R, Lit) (bodies are lists of literals, so one fact per literal), attacks(R, L)
#   proven(L)    :- rule(R, L), applicable(R), not undefeated_attack(L)
#   applicable(R):- rule(R, _), not unmet(R)
#   unmet(R)     :- body(R, Lit), not proven(Lit)
#   undefeated_attack(L) :- attacks(A, L), applicable(A), not beaten(A, L)
# proven -> unmet -> applicable -> proven passes through `not` twice: a negative edge inside a cycle.
meta =
  Program.new()
  |> Program.add_relation("rule", [:atom, :atom])
  |> Program.add_relation("body", [:atom, :atom])
  |> Program.add_relation("attacks", [:atom, :atom])
  |> Program.add_relation("beaten", [:atom, :atom])
  |> Program.add_relation("fact", [:atom])
  |> Program.add_relation("proven", [:atom])
  |> Program.add_relation("applicable", [:atom])
  |> Program.add_relation("unmet", [:atom])
  |> Program.add_relation("undefeated_attack", [:atom])
  |> Program.add_facts([{"rule", [:r306, :vendor_cleared]}, {"body", [:r306, :approved_vendor]}, {"fact", [:approved_vendor]},
                        {"attacks", [:r307, :vendor_cleared]}, {"rule", [:r307, :neg_vendor_cleared]}, {"body", [:r307, :sanctioned]}])
  |> Program.add_rule({"proven", [:L]}, [{:positive, {"fact", [:L]}}])
  |> Program.add_rule({"proven", [:L]}, [{:positive, {"rule", [:R, :L]}}, {:positive, {"applicable", [:R]}}, {:negative, {"undefeated_attack", [:L]}}])
  |> Program.add_rule({"applicable", [:R]}, [{:positive, {"rule", [:R, :_]}}, {:negative, {"unmet", [:R]}}])
  |> Program.add_rule({"unmet", [:R]}, [{:positive, {"body", [:R, :Lit]}}, {:negative, {"proven", [:Lit]}}])
  |> Program.add_rule({"undefeated_attack", [:L]}, [{:positive, {"attacks", [:A, :L]}}, {:positive, {"applicable", [:A]}}, {:negative, {"beaten", [:A, :L]}}])

case ExDatalog.materialize(meta) do
  {:ok, km} -> IO.puts("D. meta-program accepted: proven = #{inspect(Knowledge.get(km, "proven"))}")
  {:error, e} -> IO.puts("D. meta-program rejected: #{inspect(e, limit: 8, printable_limit: 400)}")
end
