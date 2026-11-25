defmodule V3c.Store do
  @moduledoc """
  V3c store: the state is one immutable value, `%V3c.Store{}`. It holds every slice record (rules, claims,
  terms, concepts, tables, columns, assets) in authoring order, each with its source (base | ext | hyp), and
  the index the engine reads, rebuilt whenever records change.

  The running session's state is held by one process (an Agent, `V3c.State`): `add` replaces the value in
  it. A hypothesis never touches that process: `hypothesis/3` derives a new value (records withheld,
  records added) and the nested ops read that value; the main value is untouched by construction, and
  concurrent readers keep the value they took.
  """
  defstruct recs: [], seq: 0, ix: nil

  @type t :: %__MODULE__{recs: [{non_neg_integer, atom, map, atom}], seq: non_neg_integer, ix: map | nil}

  def rid(x) when is_atom(x), do: Atom.to_string(x)
  def rid(x), do: to_string(x)

  def pred_of([:neg, l]), do: pred_of(l)
  def pred_of([p | _]), do: p

  @doc "resolve_term normalisation: lowercase, non-alphanumerics to spaces, collapse."
  def norm(s), do: s |> String.downcase() |> String.replace(~r/[^\p{L}\p{N}]/u, " ") |> String.split() |> Enum.join(" ")

  def new, do: %__MODULE__{} |> reindex()

  defp put(st, type, rec, src), do: %{st | seq: st.seq + 1, recs: [{st.seq + 1, type, rec, src} | st.recs]}

  # Claims are flat (PLAN-v3-integrity §1.1): one record per claim, its own asserter, times and :about.
  # The links (:depends_on, :supports) stay on the record; reindex derives parent, role and members.
  defp claim_rec(st, m, src), do: put(st, :claim, Map.put(m, :id, rid(m.id)), src)

  @doc "Rule and claim records -> {state, ids in the order given}. Rules first, then claims (as V3b)."
  def add_records(st, recs, src) do
    {claims, rules} = Enum.split_with(recs, &Map.has_key?(&1, :assertion))
    st = Enum.reduce(rules, st, &put(&2, :rule, &1, src))
    st = Enum.reduce(claims, st, &claim_rec(&2, &1, src))
    {reindex(st), Enum.map(recs, &rid(&1.id))}
  end

  def load_slice(st, s) do
    st = put(st, :slice, Map.take(s, [:today, :functional, :"code-lists", :taxonomies]), :base)
    st = Enum.reduce(s.assets, st, &put(&2, :asset, &1, :base))
    st = Enum.reduce(s.tables, st, &put(&2, :table, Map.delete(&1, :columns), :base))
    st = Enum.reduce(for(t <- s.tables, c <- t.columns, do: c), st, &put(&2, :column, &1, :base))
    st = Enum.reduce(s.concepts, st, &put(&2, :concept, &1, :base))

    st =
      Enum.reduce(s.terms, st, fn t, st ->
        put(st, :term, Map.put(t, :keys, Enum.uniq(Enum.map([t.label | t.synonyms], &norm/1))), :base)
      end)

    st |> add_records(s.rules ++ s.claims, :base) |> elem(0)
  end

  @doc "Withhold record ids (each record alone, as Datahike's retractEntity), then add records as :hyp."
  def hypothesis(st, withhold, recs) do
    w = MapSet.new(withhold)
    st = reindex(%{st | recs: Enum.reject(st.recs, fn {_, _, r, _} -> MapSet.member?(w, rid(Map.get(r, :id, ""))) end)})
    add_records(st, recs, :hyp)
  end

  # ---------------------------------------------------------------- index (what the engine reads)

  defp reindex(st) do
    by = st.recs |> Enum.reverse() |> Enum.group_by(&elem(&1, 1), &elem(&1, 2))
    slice = List.first(Map.get(by, :slice, [])) || %{}

    rules =
      for m <- Map.get(by, :rule, []) do
        m |> Map.put(:id, rid(m.id)) |> Map.put(:superior_to, MapSet.new(Map.get(m, :"superior-to", []), &rid/1))
      end

    cl = Map.get(by, :claim, [])
    links =
      for m <- cl, {k, role} <- [depends_on: "required", supports: "supporting"], x <- Map.get(m, k, []), into: %{},
        do: {rid(x), {m.id, role}}

    claims =
      for m <- cl do
        {parent, role} = Map.get(links, m.id, {nil, nil})
        members = Enum.map(Map.get(m, :depends_on, []) ++ Map.get(m, :supports, []), &rid/1)
        Map.merge(%{valid_to: nil}, m) |> Map.merge(%{parent: parent, role: role, members: members})
      end

    %{st | ix: %{
      today: slice[:today], functional: slice[:functional] || %{},
      rules: rules, claims: claims,
      rule: Map.new(rules, &{&1.id, &1}), claim: Map.new(claims, &{&1.id, &1}),
      concepts: Map.get(by, :concept, []), terms: Map.get(by, :term, []), assets: Map.get(by, :asset, []),
      tables: Map.get(by, :table, []), columns: Map.get(by, :column, [])
    }}
  end

  def index(%__MODULE__{ix: ix}), do: ix

  # ---------------------------------------------------------------- queries the ops ask the store directly

  def terms_matching(st, key), do: for(t <- st.ix.terms, key in t.keys, do: t.id)
  def term_see(st, id), do: Enum.find_value(st.ix.terms, [], &(&1.id == id && Map.get(&1, :see, [])))
  def claims_about(st, asset), do: for(c <- st.ix.claims, c.about == asset, is_nil(c.parent), do: c.id)
end
