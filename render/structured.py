"""Structured projection: YAML, one entry per relation with its schema and rows."""
import yaml
from render.common import relations


class _Flow(list):
    pass


yaml.SafeDumper.add_representer(_Flow, lambda d, v: d.represent_sequence("tag:yaml.org,2002:seq", v, flow_style=True))


def render(w, k):
    doc = {"layer": f"L{k}", "dates": "YYYY-MM-DD", "relations": []}
    for r in relations(k):
        e = {"name": r["name"], "doc": r["doc"],
             "columns": [{"name": c, "type": t} for c, t in r["columns"]], "key": _Flow(r["key"])}
        if r.get("fks"):
            e["references"] = dict(r["fks"])
        e["rows"] = [_Flow(row) for row in w["relations"][r["name"]]]
        doc["relations"].append(e)
    return yaml.safe_dump(doc, sort_keys=False, width=200, allow_unicode=True)
