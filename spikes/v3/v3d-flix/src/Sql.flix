///
/// V3d SQL boundary: concept bindings (from slice.edn) -> SQL, executed through JDBC (Java interop) on
/// DuckDB (duckdb_jdbc 2.0.1.0) or Postgres (pgjdbc 42.7.15).
///
/// Same binding layer as V3a sql.py, V3b sql.clj, V3c sql.ex:
///   - `$name` required parameters -> `?`; other filters wrap the template as
///     `SELECT * FROM (<sql>) t WHERE t."col" = ? ... LIMIT fetch_limit + 1`
///   - `@iso(x)`: DuckDB `strftime(x, '%Y-%m-%d')`, Postgres `to_char(x, 'YYYY-MM-DD')`
/// JDBC takes `?` on both backends. The SQL reported for Postgres uses `%s` (and doubles `%`) so the
/// shared checker can re-run it with psycopg.
///
/// `withEval` handles the engine's Eval effect for one op: fetch (cached per op, logged), the memo,
/// fresh names, failure. The JDBC connection is passed in; each thread opens its own.
///
pub mod Sql {
    import java.sql.{Connection => JConn}
    import java.sql.ResultSet
    import java.sql.PreparedStatement
    import java.sql.SQLException
    import java.util.Properties
    import java.lang.{System => JSys}
    import java.lang.{Exception => JExn}
    import org.duckdb.DuckDBDriver
    import org.postgresql.{Driver => PgDriver}

    use Model.Value
    use Model.Value.{VStr, VInt, VBool, VNull}
    use Engine.{Ev, FetchOut, Row}
    use Model.Goal
    use Util.Json.Json
    use Util.Json.Json.{JString, JNumber}

    pub type alias Cfg = {backend = String, duckdb = String, postgres = String, limit = Int32,
                          concepts = Map[String, (String, List[String])]}

    pub def connect(cfg: Cfg): Result[String, JConn] \ IO = try {
        if (cfg#backend == "duckdb") {
            let p = new Properties();
            discard p.setProperty("duckdb.read_only", "true");
            Ok((new DuckDBDriver()).connect("jdbc:duckdb:${cfg#duckdb}", p))
        } else {
            let kv = String.words(cfg#postgres) |> List.filterMap(w -> match String.split(regex = "=", w) {
                case k :: v :: _ => Some((k, v))
                case _ => None
            }) |> List.toMap;
            let user = Map.getWithDefault("user", JSys.getenv("USER"), kv);
            let url = "jdbc:postgresql://${Map.getWithDefault("host", "localhost", kv)}:${Map.getWithDefault("port", "5432", kv)}/${Map.getWithDefault("dbname", "", kv)}";
            let p = new Properties();
            discard p.setProperty("user", user);
            // untyped string parameters, so `date_col <= ?` works with a 'YYYY-MM-DD' string (as ADBC/psycopg)
            discard p.setProperty("stringtype", "unspecified");
            Ok((new PgDriver()).connect(url, p))
        }
    } catch {
        case e: JExn => Err("connect ${cfg#backend}: ${e.getMessage()}")
    }

    def dialect(cfg: Cfg, sql: String): String =
        let rep = if (cfg#backend == "duckdb") "strftime($1, '%Y-%m-%d')" else "to_char($1, 'YYYY-MM-DD')";
        sql.replaceAll("@iso\\(([^)]*)\\)", rep)

    def isParamChar(c: Char): Bool = (c >= 'a' and c <= 'z') or c == '_'

    /// `$name` -> `?`, collecting the names in order
    def params(s: String, i: Int32, n: Int32, out: List[String], names: List[String]): (String, List[String]) =
        if (i >= n) (String.flatten(List.reverse(out)), List.reverse(names))
        else if (String.charAt(i, s) == '$' and i + 1 < n and isParamChar(String.charAt(i + 1, s))) {
            let j = scanName(s, i + 1, n);
            params(s, j, n, "?" :: out, String.slice(start = i + 1, end = j, s) :: names)
        } else params(s, i + 1, n, Char.toString(String.charAt(i, s)) :: out, names)

    def scanName(s: String, i: Int32, n: Int32): Int32 = if (i < n and isParamChar(String.charAt(i, s))) scanName(s, i + 1, n) else i

    /// concept, filters (sorted by key) -> (sql with `?`, params)
    pub def build(cfg: Cfg, cn: String, fs: List[(String, Value)]): Result[String, (String, List[Value])] =
        match Map.get(cn, cfg#concepts) {
            case None => Err("ArgumentError: unknown concept ${cn}")
            case Some((tmpl, req)) =>
                let fm = List.toMap(fs);
                let missing = List.filter(p -> not Map.memberOf(p, fm), req);
                if (not List.isEmpty(missing)) Err("ArgumentError: fetch ${cn}: required parameter(s) ${missing} unbound")
                else {
                    let t = dialect(cfg, tmpl);
                    let (sql0, names) = params(t, 0, String.length(t), Nil, Nil);
                    let ps = List.filterMap(p -> Map.get(p, fm), names);
                    let rest = List.filter(match (k, _) -> not List.memberOf(k, req), fs);
                    let sql1 = if (List.isEmpty(rest)) sql0
                        else "SELECT * FROM (${sql0}) t WHERE " + String.intercalate(" AND ", List.map(match (k, _) -> "t.\"${k}\" = ?", rest));
                    Ok(("${sql1} LIMIT ${cfg#limit + 1}", ps ++ List.map(snd, rest)))
                }
        }

    def reported(cfg: Cfg, sql: String): String =
        if (cfg#backend == "postgres") String.replace(src = "?", dst = "%s", String.replace(src = "%", dst = "%%", sql)) else sql

    def readRows(rs: ResultSet, n: Int32, names: List[String], types: List[(Int32, Int32)], acc: List[Row]): List[Row] \ IO =
        if (not rs.next()) List.reverse(acc)
        else {
            let row = List.zip(names, List.zip(List.range(1, n + 1), types)) |> List.map(match (name, (i, (ty, sc))) -> {
                let v = if (ty == -5 or ty == 4 or ty == 5 or ty == -6) { let x = rs.getLong(i); if (rs.wasNull()) VNull else VInt(x) }
                    else if (ty == 16 or ty == -7) { let x = rs.getBoolean(i); if (rs.wasNull()) VNull else VBool(x) }
                    else if ((ty == 2 or ty == 3) and sc == 0) { let x = rs.getLong(i); if (rs.wasNull()) VNull else VInt(x) }
                    else { let x = rs.getString(i); if (rs.wasNull()) VNull else VStr(x) };
                (name, v)
            }) |> List.toMap;
            readRows(rs, n, names, types, row :: acc)
        }

    def setParams(ps: PreparedStatement, xs: List[Value], i: Int32): Unit \ IO = match xs {
        case Nil => ()
        case x :: rest =>
            match x {
                case VStr(s) => ps.setString(i, s)
                case VInt(v) => ps.setLong(i, v)
                case VBool(b) => ps.setBoolean(i, b)
                case VNull => ps.setNull(i, 0)
            };
            setParams(ps, rest, i + 1)
    }

    pub def runQuery(conn: JConn, sql: String, ps: List[Value]): Result[String, List[Row]] \ IO = try {
        let st = conn.prepareStatement(sql);
        setParams(st, ps, 1);
        let rs = st.executeQuery();
        let md = rs.getMetaData();
        let n = md.getColumnCount();
        let names = List.map(i -> md.getColumnLabel(i), List.range(1, n + 1));
        let types = List.map(i -> (md.getColumnType(i), md.getScale(i)), List.range(1, n + 1));
        let rows = readRows(rs, n, names, types, Nil);
        rs.close();
        st.close();
        Ok(rows)
    } catch {
        case e: SQLException => Err("RuntimeError: SQL: ${e.getMessage()}")
    }

    pub def fetch(cfg: Cfg, conn: JConn, cn: String, fs: List[(String, Value)]): Result[String, FetchOut] \ IO =
        match build(cfg, cn, fs) {
            case Err(e) => Err(e)
            case Ok((sql, ps)) => match runQuery(conn, sql, ps) {
                case Err(e) => Err("${e} (${cn})")
                case Ok(rows) =>
                    Ok({rows = List.take(cfg#limit, rows), sql = reported(cfg, sql), params = ps, truncated = List.length(rows) > cfg#limit})
            }
        }

    /// Handle Eval for one op: -> (result or error, SQL log entries)
    pub def withEval(cfg: Cfg, conn: JConn, f: Unit -> a \ Engine.Eval): (Result[String, a], List[Json]) \ IO = region rc {
        let memo: Ref[Map[(String, Goal), Ev], rc] = Ref.fresh(rc, Map.empty());
        let cache: Ref[Map[(String, List[(String, Value)]), FetchOut], rc] = Ref.fresh(rc, Map.empty());
        let log = Ref.fresh(rc, Nil);
        let counter = Ref.fresh(rc, 0i64);
        let r = run { Ok(f()) } with handler Engine.Eval {
            def fetch(cn, fs, k) = match Map.get((cn, fs), Ref.get(cache)) {
                case Some(o) => k(o)
                case None => match fetch(cfg, conn, cn, fs) {
                    case Ok(o) =>
                        Ref.put(Map.insert((cn, fs), o, Ref.get(cache)), cache);
                        let e = Engine.obj(("concept", JString(cn)) :: ("sql", JString(o#sql)) ::
                                           ("params", Engine.jarr(List.map(Engine.valueJson, o#params))) ::
                                           ("rows", Engine.jint(Int32.toInt64(List.length(o#rows)))) :: Nil);
                        Ref.put(e :: Ref.get(log), log);
                        k(o)
                    case Err(m) => Err(m)
                }
            }
            def memoGet(key, k) = k(Map.get(key, Ref.get(memo)))
            def memoPut(key, ev, k) = { Ref.put(Map.insert(key, ev, Ref.get(memo)), memo); k() }
            def fresh(k) = { let i = Ref.get(counter) + 1i64; Ref.put(i, counter); k(i) }
            def fail(m, _k) = Err(m)
        };
        (r, List.reverse(Ref.get(log)))
    }
}
