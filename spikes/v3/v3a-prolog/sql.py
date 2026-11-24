"""V3a SQL boundary: concept bindings -> SQL, executed on DuckDB or Postgres.

Prolog registers each concept of the slice (name, SQL template, params) at load time and calls
fetch(concept, filters_json) through janus. Everything dialect-specific lives here:
  - parameter style: DuckDB `?`, psycopg `%s`
  - @iso(x) macro: DuckDB strftime(x, '%Y-%m-%d'), Postgres to_char(x, 'YYYY-MM-DD')
  - $name required parameters -> bound placeholders; other filters wrap the template as
    SELECT * FROM (<sql>) t WHERE t."col" = ? ... LIMIT fetch_limit + 1
Rows come back as JSON (dates already ISO strings via @iso). A per-op cache avoids re-issuing the same
statement inside one op; the per-op log is what the CLI reports as sql_log.
"""
import json, re

_cfg, _con, _concepts, _cache, _log = {}, None, {}, {}, []


def configure(cfg_json, root):
    global _cfg, _con
    _cfg = json.loads(cfg_json)
    if _con is not None:
        _con.close()
    if _cfg["backend"] == "duckdb":
        import duckdb
        _con = duckdb.connect(str(root) + "/" + _cfg["duckdb"], read_only=True)
    elif _cfg["backend"] == "postgres":
        import psycopg
        _con = psycopg.connect(_cfg["postgres"], autocommit=True)
    else:
        raise ValueError(_cfg["backend"])
    return True


def register(name, sql, params):
    _concepts[name] = (sql, list(params))
    return True


def _dialect(sql):
    if _cfg["backend"] == "duckdb":
        return re.sub(r"@iso\(([^)]*)\)", r"strftime(\1, '%Y-%m-%d')", sql), "?"
    return re.sub(r"@iso\(([^)]*)\)", r"to_char(\1, 'YYYY-MM-DD')", sql).replace("%", "%%"), "%s"


def build(concept, filters):
    tmpl, req = _concepts[concept]
    sql, ph = _dialect(tmpl)
    params = []
    def sub(m):
        params.append(filters[m.group(1)])
        return ph
    missing = [p for p in req if p not in filters]
    if missing:
        raise ValueError(f"fetch {concept}: required parameter(s) {missing} unbound")
    sql = re.sub(r"\$([a-z_]+)", sub, sql)
    rest = [(c, v) for c, v in filters.items() if c not in req]
    if rest:
        sql = f"SELECT * FROM ({sql}) t WHERE " + " AND ".join(f't."{c}" = {ph}' for c, _ in rest)
        params += [v for _, v in rest]
    limit = int(_cfg.get("fetch_limit", 10000))
    return f"{sql} LIMIT {limit + 1}", params, limit


def _val(v):
    if hasattr(v, "isoformat"):
        return v.isoformat()[:10]
    return v


def fetch(concept, filters_json):
    filters = json.loads(filters_json)
    key = (concept, json.dumps(filters, sort_keys=True))
    if key in _cache:
        return _cache[key]
    sql, params, limit = build(concept, filters)
    if _cfg["backend"] == "duckdb":
        cur = _con.execute(sql, params)
    else:
        cur = _con.cursor(); cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    rows = [{c: _val(v) for c, v in zip(cols, r)} for r in cur.fetchall()]
    truncated = len(rows) > limit
    rows = rows[:limit]
    _log.append({"concept": concept, "sql": sql, "params": params, "rows": len(rows)})
    out = json.dumps({"rows": rows, "sql": sql, "params": params, "truncated": truncated})
    _cache[key] = out
    return out


def begin_op():
    _cache.clear(); _log.clear()
    return True


def take_log():
    return json.dumps(_log)
