defmodule V3c.SQL do
  @moduledoc """
  V3c SQL boundary: concept bindings (from slice.edn) -> SQL, executed through ADBC on DuckDB or Postgres.

  Same binding layer as V3a's sql.py and V3b's sql.clj, so that differences are engine differences:
    - `$name` required parameters -> placeholders; other filters wrap the template as
      `SELECT * FROM (<sql>) t WHERE t."col" = ? ... LIMIT fetch_limit + 1`
    - `@iso(x)`: DuckDB `strftime(x, '%Y-%m-%d')`, Postgres `to_char(x, 'YYYY-MM-DD')`
  Placeholders are `?` (DuckDB) or `$1..$n` (Postgres ADBC). The SQL text reported for Postgres uses `%s`
  (and doubles `%`) so the shared checker can re-run it with psycopg.

  Processes: `configure/2` starts a supervisor under V3c.Sup holding the ADBC database and `pool` connection
  processes (default 1). Each connection is a GenServer, so statements on one connection are serialised by
  its mailbox. Cfg and concept bindings are in :persistent_term (read by every process, written at load).
  The per-op cache and log are in the calling process's dictionary: an op runs in one process, so concurrent
  ops (shared/isolation.py) never mix logs.
  """
  @cfg {__MODULE__, :cfg}
  @concepts {__MODULE__, :concepts}

  def configure(cfg, root, opts \\ []) do
    pool = Keyword.get(opts, :pool, 1)
    for {_, pid, _, _} <- DynamicSupervisor.which_children(V3c.Sup), do: DynamicSupervisor.terminate_child(V3c.Sup, pid)
    :persistent_term.put(@cfg, Map.merge(cfg, %{"pool" => pool}))
    :persistent_term.put(@concepts, %{})

    db =
      case cfg["backend"] do
        "duckdb" -> [driver: :duckdb, version: "2.0.1", path: Path.join(root, cfg["duckdb"]), access_mode: "READ_ONLY"]
        "postgres" -> [driver: :postgresql, uri: pg_uri(cfg["postgres"])]
      end

    children =
      [%{id: :db, start: {Adbc.Database, :start_link, [Keyword.put(db, :process_options, name: V3c.SQL.DB)]}}] ++
        for i <- 1..pool do
          %{id: {:conn, i}, start: {Adbc.Connection, :start_link, [[database: V3c.SQL.DB, process_options: [name: conn_name(i)]]]}}
        end

    spec = %{id: __MODULE__, type: :supervisor,
             start: {Supervisor, :start_link, [children, [strategy: :rest_for_one, name: V3c.SQL.Sup, max_restarts: 100, max_seconds: 1]]}}
    {:ok, _} = DynamicSupervisor.start_child(V3c.Sup, spec)
    :ok
  end

  def conn_name(i), do: :"Elixir.V3c.SQL.Conn#{i}"

  defp pg_uri(dsn) do
    kv = dsn |> String.split() |> Map.new(fn p -> List.to_tuple(String.split(p, "=", parts: 2)) end)
    user = kv["user"] || System.get_env("USER")
    "postgresql://#{user}@#{kv["host"] || "localhost"}:#{kv["port"] || "5432"}/#{kv["dbname"]}"
  end

  def cfg, do: :persistent_term.get(@cfg)

  def register(name, sql, params) do
    :persistent_term.put(@concepts, Map.put(:persistent_term.get(@concepts), name, {sql, Enum.map(params, &Atom.to_string/1)}))
  end

  defp dialect(sql) do
    rep = if cfg()["backend"] == "duckdb", do: "strftime(\\1, '%Y-%m-%d')", else: "to_char(\\1, 'YYYY-MM-DD')"
    Regex.replace(~r/@iso\(([^)]*)\)/, sql, rep)
  end

  @doc "concept (atom), filters [{string, value}] (ordered) -> {sql, params, limit}; placeholders `?`"
  def build(c, filters) do
    {tmpl, req} = Map.get(:persistent_term.get(@concepts), c) || raise ArgumentError, "unknown concept #{c}"
    fm = Map.new(filters)
    missing = Enum.reject(req, &Map.has_key?(fm, &1))
    if missing != [], do: raise(ArgumentError, "fetch #{c}: required parameter(s) #{inspect(missing)} unbound")

    {sql, ps} =
      Regex.split(~r/\$[a-z_]+/, dialect(tmpl), include_captures: true)
      |> Enum.map_reduce([], fn
        "$" <> p, acc -> {"?", [fm[p] | acc]}
        part, acc -> {part, acc}
      end)

    rest = Enum.reject(filters, fn {k, _} -> k in req end)
    sql = Enum.join(sql)
    sql = if rest == [], do: sql, else: "SELECT * FROM (#{sql}) t WHERE " <> Enum.map_join(rest, " AND ", fn {k, _} -> ~s(t."#{k}" = ?) end)
    limit = cfg()["fetch_limit"] || 10000
    {sql <> " LIMIT #{limit + 1}", Enum.reverse(ps) ++ Enum.map(rest, &elem(&1, 1)), limit}
  end

  defp reported(sql), do: if(cfg()["backend"] == "postgres", do: sql |> String.replace("%", "%%") |> String.replace("?", "%s"), else: sql)

  defp executed(sql) do
    if cfg()["backend"] == "postgres" do
      sql |> String.split("?") |> Enum.with_index() |> Enum.map_join(fn {s, 0} -> s; {s, i} -> "$#{i}" <> s end)
    else
      sql
    end
  end

  defp conn do
    case cfg()["pool"] do
      1 -> conn_name(1)
      n -> conn_name(:erlang.phash2(self(), n) + 1)
    end
  end

  defp rows(%Adbc.Result{data: batches}) do
    Enum.flat_map(batches, fn cols ->
      names = Enum.map(cols, & &1.field.name)
      cols |> Enum.map(&Adbc.Column.to_list/1) |> Enum.zip_with(&Map.new(Enum.zip(names, &1)))
    end)
    |> Enum.map(fn r -> Map.new(r, fn {k, v} -> {k, value(v)} end) end)
  end

  defp value(%Date{} = d), do: Date.to_iso8601(d)
  defp value(%Decimal{} = d), do: if(Decimal.integer?(d), do: Decimal.to_integer(d), else: Decimal.to_float(d))
  defp value(v), do: v

  @doc "-> %{rows: [%{string => value}], sql:, params:, truncated:}"
  def fetch(c, filters) do
    key = {c, filters}
    st = Process.get(__MODULE__, %{cache: %{}, log: []})

    case st.cache do
      %{^key => out} ->
        out

      _ ->
        {sql, params, limit} = build(c, filters)
        rows = case Adbc.Connection.query(conn(), executed(sql), params) do
          {:ok, r} -> rows(r)
          {:error, e} -> raise RuntimeError, "SQL #{c}: " <> Exception.message(e)
        end
        out = %{rows: Enum.take(rows, limit), sql: reported(sql), params: params, truncated: length(rows) > limit}
        Process.put(__MODULE__, %{st | cache: Map.put(st.cache, key, out),
          log: [%{concept: Atom.to_string(c), sql: out.sql, params: params, rows: length(out.rows)} | st.log]})
        out
    end
  end

  def begin_op, do: Process.put(__MODULE__, %{cache: %{}, log: []})
  def take_log, do: Enum.reverse(Process.get(__MODULE__, %{log: []}).log)
end
