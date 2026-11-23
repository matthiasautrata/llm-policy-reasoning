"""Structured projection: YAML. One entry per relation with its schema and rows; from L1 on, a flat
concept list with bindings, rule records (id, defines, meaning, class, conservative, owner, rule), and
the decisions (decided) or open forks with one rule record per reading (open)."""
import yaml
from render.common import relations, concepts, forks, items, RULES


class _Flow(list):
    pass


yaml.SafeDumper.add_representer(_Flow, lambda d, v: d.represent_sequence("tag:yaml.org,2002:seq", v, flow_style=True))


def _rule(r):
    e = {"id": r["id"], "defines": r["head"], "meaning": RULES["docs"][r["head"]], "class": r["class"],
         "conservative": r["conservative"], "owner": r["owner"], "rule": r["english"]}
    if r.get("fork"):
        e["reading_of"] = r["fork"]["id"]
    return e


def render(w, k, cfg="decided"):
    doc = {"layer": f"L{k}", "dates": "YYYY-MM-DD", "relations": []}
    for r in relations(k):
        e = {"name": r["name"], "doc": r["doc"],
             "columns": [{"name": c, "type": t} for c, t in r["columns"]], "key": _Flow(r["key"])}
        if r.get("fks"):
            e["references"] = dict(r["fks"])
        e["rows"] = [_Flow(row) for row in w["relations"][r["name"]]]
        doc["relations"].append(e)
    if k >= 1:
        doc["concepts"] = [dict(c) for c in concepts(k)]
        doc["rules"] = []
        for it in items(k, cfg):
            if it[0] == "rule":
                doc["rules"].append(_rule(it[1]))
            else:
                f = it[1]
                doc["rules"].append({"open_question": f["id"], "term": f["term"], "owner": f["owner"],
                                     "question": f["question"], "decided": None,
                                     "readings": [dict(reading=x["fork"]["reading"], **_rule(x)) for x in it[2]]})
        if cfg == "decided":
            doc["decisions"] = [{"id": f["id"], "term": f["term"], "owner": f["owner"], "question": f["question"],
                                 "readings": _Flow(f["readings"]), "decided": f["decided"]} for f in forks(k)]
    return yaml.safe_dump(doc, sort_keys=False, width=200, allow_unicode=True)
