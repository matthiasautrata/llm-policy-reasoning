"""V3a SQL boundary: concept bindings -> SQL, executed on DuckDB (read-only).

Prolog registers each concept of the slice (name, SQL template, params) at load time and calls
fetch(concept, filters_json) through janus. Everything dialect-specific lives here:
  - @iso(x) macro: strftime(x, '%Y-%m-%d')
  - $name required parameters -> bound placeholders; other filters wrap the template as
    SELECT * FROM (<sql>) t WHERE t."col" = ? ... LIMIT fetch_limit + 1
Rows come back as JSON (dates already ISO strings via @iso). A per-op cache avoids re-issuing the same
statement inside one op; the per-op log is what the CLI reports as sql_log. Cache and log are per thread
(threading.local; each Prolog thread that py_calls gets its own Python thread state), and statements are
serialised on the one connection, so concurrent Prolog threads (the isolation test) do not mix their logs.
"""
import json, re, threading

_cfg, _con, _concepts = {}, None, {}
_tl, _lock = threading.local(), threading.Lock()


def _state():
    if not hasattr(_tl, "cache"):
        _tl.cache, _tl.log = {}, []
    return _tl


def configure(cfg_json, root):
    global _cfg, _con
    _cfg = json.loads(cfg_json)
    if _con is not None:
        _con.close()
    if _cfg.get("backend", "duckdb") != "duckdb":
        raise ValueError(f"backend {_cfg['backend']}: DuckDB only")
    import duckdb
    _con = duckdb.connect(str(root) + "/" + _cfg["duckdb"], read_only=True)
    return True


def register(name, sql, params):
    _concepts[name] = (sql, list(params))
    return True


def _dialect(sql):
    return re.sub(r"@iso\(([^)]*)\)", r"strftime(\1, '%Y-%m-%d')", sql), "?"


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
    st = _state()
    key = (concept, json.dumps(filters, sort_keys=True))
    if key in st.cache:
        return st.cache[key]
    sql, params, limit = build(concept, filters)
    with _lock:
        cur = _con.execute(sql, params)
        cols = [d[0] for d in cur.description]
        raw = cur.fetchall()
    rows = [{c: _val(v) for c, v in zip(cols, r)} for r in raw]
    truncated = len(rows) > limit
    rows = rows[:limit]
    st.log.append({"concept": concept, "sql": sql, "params": params, "rows": len(rows)})
    out = json.dumps({"rows": rows, "sql": sql, "params": params, "truncated": truncated})
    st.cache[key] = out
    return out


def begin_op():
    st = _state(); st.cache.clear(); st.log.clear()
    return True


def take_log():
    return json.dumps(_state().log)
