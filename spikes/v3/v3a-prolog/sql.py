"""V3a SQL boundary: concept bindings -> SQL, executed on DuckDB (read-only).

Prolog registers each concept of the slice (name, SQL template, params) at load time and calls
fetch(concept, filters_json) through janus. Everything dialect-specific lives here:
  - @iso(x) macro: strftime(x, '%Y-%m-%d')
  - $name required parameters -> bound placeholders; other filters wrap the template as
    SELECT * FROM (<sql>) t WHERE t."col" = ? ... LIMIT fetch_limit + 1
Rows come back as JSON (dates already ISO strings via @iso). A per-op cache avoids re-issuing the same
statement inside one op. Inside an aggregate (CONTRACT.md, Aggregates) Prolog calls need(): a cached,
untruncated entry is returned, otherwise the (concept, filters) is recorded and "" returned; flush() then
fetches every recorded need set-at-a-time: one statement per concept and filter shape (an IN list when one
column filter varies, else a UNION ALL of the single-key statements tagged __b), paged with
ORDER BY ALL LIMIT fetch_limit OFFSET k, chunked at CHUNK keys. Each key's cache entry carries its
single-key statement without LIMIT, which check_why re-runs. The per-op log is what the CLI reports as
sql_log. Cache, needs and log are per thread (threading.local; each Prolog thread that py_calls gets its
own Python thread state), and statements are serialised on the one connection, so concurrent Prolog
threads (the isolation test) do not mix their logs.
"""
import json, re, threading

_cfg, _con, _concepts = {}, None, {}
_tl, _lock = threading.local(), threading.Lock()


CHUNK = 500


def _state():
    if not hasattr(_tl, "cache"):
        _tl.cache, _tl.log, _tl.needs = {}, [], {}
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


def single(concept, filters):
    """The single-key statement and params, without LIMIT."""
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
    return sql, params


def _limit():
    return int(_cfg.get("fetch_limit", 10000))


def build(concept, filters):
    sql, params = single(concept, filters)
    return f"{sql} LIMIT {_limit() + 1}", params, _limit()


def _val(v):
    if hasattr(v, "isoformat"):
        return v.isoformat()[:10]
    return v


def _run(sql, params):
    with _lock:
        cur = _con.execute(sql, params)
        cols = [d[0] for d in cur.description]
        raw = cur.fetchall()
    return [{c: _val(v) for c, v in zip(cols, r)} for r in raw]


def _key(concept, filters):
    return (concept, json.dumps(filters, sort_keys=True))


def fetch(concept, filters_json):
    filters = json.loads(filters_json)
    st = _state()
    key = _key(concept, filters)
    if key in st.cache:
        return st.cache[key][1]
    sql, params, limit = build(concept, filters)
    rows = _run(sql, params)
    truncated = len(rows) > limit
    rows = rows[:limit]
    st.log.append({"concept": concept, "sql": sql, "params": params, "rows": len(rows)})
    out = json.dumps({"rows": rows, "sql": sql, "params": params, "truncated": truncated})
    st.cache[key] = (truncated, out)
    return out


def need(concept, filters_json):
    """Inside an aggregate: the cached untruncated entry, else record the need and return ""."""
    filters = json.loads(filters_json)
    st = _state()
    key = _key(concept, filters)
    hit = st.cache.get(key)
    if hit is not None and not hit[0]:
        return hit[1]
    st.needs[key] = filters
    return ""


def _paged(concept, sql, params):
    """Every row of sql, ORDER BY ALL LIMIT fetch_limit OFFSET k; each page is one logged statement."""
    st, lim, k, rows = _state(), _limit(), 0, []
    while True:
        q = f"SELECT * FROM ({sql}) p ORDER BY ALL LIMIT {lim} OFFSET {k}"
        page = _run(q, params)
        st.log.append({"concept": concept, "sql": q, "params": params, "rows": len(page)})
        rows += page
        if len(page) < lim:
            return rows
        k += lim


def flush():
    """Fetch every recorded need, batched per concept and filter shape. Returns the number of keys."""
    st = _state()
    needs, st.needs = st.needs, {}
    groups = {}
    for (concept, _), f in needs.items():
        groups.setdefault((concept, tuple(sorted(f))), []).append(f)
    for (concept, cols), fs in groups.items():
        req = _concepts[concept][1]
        vary = [c for c in cols if len({json.dumps(f[c]) for f in fs}) > 1]
        for i in range(0, len(fs), CHUNK):
            chunk = fs[i:i + CHUNK]
            if len(chunk) > 1 and len(vary) == 1 and vary[0] not in req:
                c = vary[0]
                base = {k: v for k, v in chunk[0].items() if k != c}
                sql, params = single(concept, base)
                sql = f'SELECT * FROM ({sql}) b WHERE b."{c}" IN ({", ".join("?" * len(chunk))})'
                rows = _paged(concept, sql, params + [f[c] for f in chunk])
                split = {}
                for r in rows:
                    split.setdefault(json.dumps(r[c]), []).append(r)
                per = [split.get(json.dumps(f[c]), []) for f in chunk]
            else:
                parts, params = [], []
                for b, f in enumerate(chunk):
                    s1, p1 = single(concept, f)
                    parts.append(f"SELECT {b} AS __b, s{b}.* FROM ({s1}) s{b}")
                    params += p1
                rows = _paged(concept, " UNION ALL ".join(parts), params)
                per = [[] for _ in chunk]
                for r in rows:
                    per[r.pop("__b")].append(r)
            for f, rs in zip(chunk, per):
                s1, p1 = single(concept, f)
                st.cache[_key(concept, f)] = (False, json.dumps(
                    {"rows": rs, "sql": s1, "params": p1, "truncated": False}))
    return len(needs)


def begin_op():
    st = _state(); st.cache.clear(); st.log.clear(); st.needs.clear()
    return True


def take_log():
    return json.dumps(_state().log)
