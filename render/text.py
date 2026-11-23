"""Text projection: Markdown. One section and one table per relation; from L1 on, a glossary of terms,
the definitions (rule English with rule ids) and the decisions (decided) or open questions (open)."""
from render.common import relations, concepts, forks, items


def render(w, k, cfg="decided"):
    out = [f"# Procurement records (L{k})", "",
           "Each table below is one kind of record. Dates are YYYY-MM-DD.", ""]
    for r in relations(k):
        cols = [c for c, _ in r["columns"]]
        out += [f"## {r['name']}", "", r["doc"]]
        keys = ", ".join(r["key"])
        refs = "; ".join(f"`{c}` refers to `{t}`" for c, t in (r.get("fks") or {}).items())
        out += [f"Identified by: {keys}." + (f" References: {refs}." if refs else ""), ""]
        rows = w["relations"][r["name"]]
        if rows:
            out += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
            out += ["| " + " | ".join(str(v) for v in row) + " |" for row in rows]
        else:
            out.append("(no records)")
        out.append("")
    if k < 1:
        return "\n".join(out)

    out += ["# Terms", "", "What the terms used below refer to in the records.", ""]
    out += [f"- **{c['term']}** (`{c['binding']}`): {c['english']}" for c in concepts(k)]
    out += ["", "# Definitions", "", "Each definition has a rule id. A definition applies wherever its term is used.", ""]
    for it in items(k, cfg):
        if it[0] == "rule":
            out.append(f"- **{it[1]['id']}.** {it[1]['english']}")
        else:
            f, recs = it[1], it[2]
            out.append(f"- **Open question {f['id']}** (owner: {f['owner']}), on {f['term']}: {f['question']} "
                       f"This has not been decided. The readings are:")
            out += [f"  - {x['fork']['reading']} ({x['id']}): {x['english']}" for x in recs]
    if cfg == "decided":
        out += ["", "# Decisions", "", "Questions of interpretation, who decides them, and what was decided. "
                "The definitions above already follow these decisions.", ""]
        for f in forks(k):
            out.append(f"- **{f['id']}** (owner: {f['owner']}), on {f['term']}: {f['question']} Decided: {f['decided']}.")
    out.append("")
    return "\n".join(out)
