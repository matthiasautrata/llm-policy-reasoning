"""Formal projection: SWI-Prolog facts. Relations are declared dynamic (an empty relation is a fact
too: nothing holds); the schema itself is stated as relation/1, column/4, key/2 and fk/3 facts."""
from render.common import relations, date_int


def _val(v, t):
    if t == "date":
        return str(date_int(v))
    if t == "int":
        return str(v)
    return v if v.replace("_", "").isalnum() and v[0].islower() else "'" + v.replace("'", "\\'") + "'"


def _facts(w, r):
    types = [t for _, t in r["columns"]]
    return [f"{r['name']}({', '.join(_val(v, t) for v, t in zip(row, types))})." for row in w["relations"][r["name"]]]


def facts(w, k):
    """All base facts of layers <= k, as read by the engine (no comments, no schema facts)."""
    return "".join(l + "\n" for r in relations(k) for l in _facts(w, r))


def render(w, k):
    out = [f"% Procurement world, layer L{k}: base relations. Dates are integers YYYYMMDD.", ""]
    out.append("% Schema: relation(Name). column(Relation, Column, Position, Type). key(Relation, FirstKeyColumn). fk(Relation, Column, ReferencedRelation).")
    for r in relations(k):
        out.append(f"relation({r['name']}).")
        out += [f"column({r['name']}, {c}, {i}, {t})." for i, (c, t) in enumerate(r["columns"], 1)]
        out.append(f"key({r['name']}, {r['columns'][0][0]}).")
        out += [f"fk({r['name']}, {c}, {ref})." for c, ref in (r.get("fks") or {}).items()]
    for r in relations(k):
        args = ", ".join(c.capitalize() for c, _ in r["columns"])
        out += ["", f"% {r['name']}({args}): {r['doc']}", f":- dynamic {r['name']}/{len(r['columns'])}."]
        out += _facts(w, r)
    return "\n".join(out) + "\n"
