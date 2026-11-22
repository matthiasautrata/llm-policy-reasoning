"""Text projection: Markdown, one section and one table per relation."""
from render.common import relations


def render(w, k):
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
    return "\n".join(out)
