defmodule V3c.EDN do
  @moduledoc """
  EDN reader (NimbleParsec). eden 2.1.0, the only EDN package on hex, rejects symbols that start with `?`
  (the rule language's variables) and returns vectors as `Array` structs, so the spike reads EDN itself.

  Mapping (the same choices as V3b's `read-edn`):
    keyword `:a` / `:ns/a` -> atom `:a` / `:"ns/a"`   symbol `?x` -> `{:var, "?x"}`, other symbols `{:sym, "x"}`
    vector and list -> list    map -> map    set -> MapSet    `#inst "2026-01-01"` -> the string
    nil / true / false, integers, floats, strings (with escapes); `;` comments, commas, `#_` discard.
  Keywords become atoms: atoms are never garbage-collected, so goals typed by users grow the atom table.
  """
  import NimbleParsec

  ws = ascii_char([?\s, ?\t, ?\n, ?\r, ?,]) |> times(min: 1) |> ignore()
  comment = string(";") |> repeat(ascii_char(not: ?\n)) |> ignore()
  discard = string("#_") |> ignore() |> optional(parsec(:skip)) |> parsec(:form) |> ignore()
  defcombinatorp(:skip, repeat(choice([ws, comment, discard])))

  sym_start = utf8_char([?a..?z, ?A..?Z, ?*, ?+, ?!, ?-, ?_, ??, ?<, ?>, ?=, ?/, ?., ?&, ?%, ?$])
  sym_rest = utf8_char([?a..?z, ?A..?Z, ?0..?9, ?*, ?+, ?!, ?-, ?_, ??, ?<, ?>, ?=, ?/, ?., ?&, ?%, ?$, ?:, ?#, ?'])
  name = sym_start |> repeat(sym_rest) |> reduce({List, :to_string, []})

  number =
    optional(ascii_char([?-, ?+]))
    |> ascii_string([?0..?9], min: 1)
    |> optional(string(".") |> ascii_string([?0..?9], min: 1))
    |> optional(ascii_char([?e, ?E]) |> optional(ascii_char([?-, ?+])) |> ascii_string([?0..?9], min: 1))
    |> lookahead_not(sym_rest)
    |> reduce(:number)

  escape =
    ignore(string("\\"))
    |> choice([
      string("n") |> replace(?\n),
      string("t") |> replace(?\t),
      string("r") |> replace(?\r),
      string("\"") |> replace(?"),
      string("\\") |> replace(?\\),
      ignore(string("u")) |> ascii_string([?0..?9, ?a..?f, ?A..?F], 4) |> map({String, :to_integer, [16]})
    ])

  str =
    ignore(string("\""))
    |> repeat(choice([escape, utf8_char(not: ?", not: ?\\)]))
    |> ignore(string("\""))
    |> reduce({List, :to_string, []})

  keyword = ignore(string(":")) |> concat(name) |> map({String, :to_atom, []})
  symbol = name |> map(:symbol)

  seq = fn open, close, tag ->
    ignore(string(open))
    |> parsec(:skip)
    |> repeat(parsec(:form) |> parsec(:skip))
    |> ignore(string(close))
    |> tag(tag)
  end

  inst = ignore(string("#inst")) |> parsec(:skip) |> concat(str)

  defcombinatorp(
    :form,
    choice([
      number,
      str,
      keyword,
      inst,
      seq.(~S(#{), "}", :set),
      seq.("[", "]", :vec),
      seq.("(", ")", :vec),
      seq.("{", "}", :map),
      symbol
    ])
    |> map(:build)
  )

  defparsecp(:document, parsec(:skip) |> parsec(:form) |> parsec(:skip) |> eos())

  defp number(parts) do
    s = Enum.map_join(parts, fn c when is_integer(c) -> <<c>>; b -> b end)
    if String.contains?(s, [".", "e", "E"]), do: elem(Float.parse(s), 0), else: String.to_integer(s)
  end

  defp symbol("nil"), do: nil
  defp symbol("true"), do: true
  defp symbol("false"), do: false
  defp symbol("?" <> _ = s), do: {:var, s}
  defp symbol(s), do: {:sym, s}

  defp build({:vec, xs}), do: xs
  defp build({:set, xs}), do: MapSet.new(xs)
  defp build({:map, xs}), do: xs |> Enum.chunk_every(2) |> Map.new(fn [k, v] -> {k, v} end)
  defp build(x), do: x

  @doc "EDN text -> data; raises ArgumentError on a syntax error."
  def read!(text) do
    case document(text) do
      {:ok, [x], _, _, _, _} -> x
      {:error, msg, rest, _, {line, _}, _} -> raise ArgumentError, "EDN line #{line}: #{msg} near #{inspect(String.slice(rest, 0, 30))}"
    end
  end
end
