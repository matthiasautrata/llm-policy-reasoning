"""Markdown for arm G, rendered from the same rule base the engine loads (PLAN-v3-bench §3).

  .venv/bin/python bench/render_md.py              # bench/material/N{025,050,100,200}.md, then the completeness check

The material follows Databricks' guidance for Genie spaces: focused sections, the data model with column docs,
a glossary of business terms with owners, the rules in plain language with owner, kind, validity and precedence,
the claims with asserter, validity and links, and example SQL. Rules are rendered from their :doc texts and
metadata, never from their bodies; the example SQL is the semantic layer's own bindings (the concepts the engine
fetches through), with parameters filled in. Completeness: every rule and claim id of the base appears
in its markdown, so nothing T can reach is withheld from G.
"""
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "spikes/v3/shared"))
import integrity  # noqa: E402

BASES, OUT = ROOT / "bench/bases", ROOT / "bench/material"
EXT = "spikes/v3/shared/extension.edn"
EXAMPLE_ARGS = {"cc": "'cc0001'", "root": "'cc0001'", "emp": "'e077'"}

KIND = {"strict": "strict (always holds when its conditions hold; cannot be overridden)",
        "defeasible": "defeasible (holds unless a rule that prevails over it says otherwise)",
        "defeater": "defeater (only blocks a conclusion; never establishes one)",
        "superiority": "precedence between asserters",
        "incompatible": "incompatibility (two conclusions that cannot both hold)"}

COMBINE = """\
## 3 How the rules combine

Read this before using any rule. The rules below are the policy. Where the rules and the data seem to disagree, the rules win.

- **Strict** rules always hold when their conditions hold. **Defeasible** rules hold unless a rule that *prevails over* them says otherwise. **Defeaters** block a conclusion and never establish one.
- A rule **prevails over** another only where this is stated ("Prevails over …", or a precedence rule naming the asserters). A conclusion holds when a rule supporting it applies and every rule against it that applies is overridden by a prevailing supporter.
- If rules for and against a conclusion both apply and neither prevails, the conclusion is **contested**. Report it as contested, with both sides. Do not pick one, and do not count it as true or as false. Anything that depends on a contested conclusion is contested as well.
- An **incompatibility** says two conclusions never both hold. If both are derived, the result is contested.
- **Dated rules and data:** a version or status applies on the date it is valid. For a request, that is the request date, unless the rule says otherwise. A view "as it stood at" a date evaluates every dated rule, status and claim at that date.
- **Claims** are statements by an asserter about an asset, each valid from–to.
  - A later claim by the **same** asserter supersedes an earlier conflicting one.
  - Claims by **different** asserters that conflict stay contested, unless a precedence rule orders the asserters.
  - A claim that *depends on* sub-claims fails if a required sub-claim fails. If a *supporting* sub-claim fails, the claim still holds but is qualified.
  - A claim outside its validity window does not hold.
- **Absence:** a "no" that rests only on not finding something in the data is a no *over the known facts*. Say so, unless a completeness claim covers the data. Booked totals are declared complete (claim C10).
- **Terms** without a definition are undecided: ask, or show each reading. Do not choose one silently.
- Today is {today}.
"""


def words(lit):
    if lit and lit[0] == "neg":
        return "NOT " + words(lit[1])
    return f"{lit[0]}({', '.join(map(str, lit[1:]))})"


def pred(r):
    h = r.get("head")
    if h is None:
        return r.get("pred")
    return h[1][0] if h[0] == "neg" else h[0]


def example_sql(c):
    s = re.sub(r"@iso\(([^)]*)\) AS \1\b", r"\1", c["sql"])
    for p in c.get("params") or []:
        s = s.replace(f"${p}", EXAMPLE_ARGS[p])
    return s


def render(stem):
    load = [str(stem.with_suffix(".edn")), EXT]
    S, rules, claims = integrity.rule_base(load)
    o = [f"# Procurement policy and data: instructions for the analytics assistant\n",
         f"This space answers questions about purchase requests, cost centres, approvals and vendors. It contains "
         f"{len(rules)} rules and {len(claims)} claims. The data is in DuckDB; use the `sql` tool (read-only). "
         f"Cite rule and claim ids (R…, G…, C…, H…) for every conclusion you draw from them.\n"]
    # 1 data model
    o.append("## 1 Data model\n")
    for t in S["tables"]:
        o.append(f"### Table `{t['name']}`\n\n{t['doc']}\n\n| column | type | meaning |\n|---|---|---|")
        o += [f"| `{c['name']}` | {c['type']} | {c['doc']} |" for c in t["columns"]]
        o.append("")
    o.append("### Code lists\n")
    o += [f"- `{c['id'].split(':')[1]}`: {', '.join(c['values'])}" for c in S["code-lists"]]
    for x in S.get("taxonomies") or []:
        o.append(f"- taxonomy of `{x['code-list'].split(':')[1]}`: " + "; ".join(f"{k} = {', '.join(v)}" for k, v in x["tree"].items()))
    o.append("")
    # 2 glossary
    o.append("## 2 Glossary\n\nBusiness terms, each with its owner. Use the term the owner defines; resolve ambiguous ones before use.\n")
    for t in S["terms"]:
        syn = f" (also: {', '.join(t['synonyms'])})" if t.get("synonyms") else ""
        see = f" See {', '.join(t['see'])}." if t.get("see") else ""
        o.append(f"- **{t['label']}**{syn}, owner {t['owner']}: {t['definition']}{see}")
    o.append("")
    o.append(COMBINE.format(today=S["today"]))
    # 4 rules, grouped by what they conclude
    o.append("## 4 Rules\n\nGrouped by what each rule concludes. Every rule has an id, an owner, a kind, and the date it was recorded.\n")
    groups = {}
    for r in rules:
        groups.setdefault(pred(r) or r["id"], []).append(r)
    for p, rs in groups.items():
        o.append(f"### `{p}`\n")
        for r in rs:
            meta = [f"owner {r['owner']}", KIND.get(r["kind"], r["kind"]), f"class {r.get('class')}"]
            if r.get("superior-to"):
                meta.append("prevails over " + ", ".join(r["superior-to"]))
            if r.get("order"):
                meta.append(f"on `{r['pred']}`: " + " over ".join(r["order"]))
            if r.get("closed_over"):
                meta.append("answers over known facts only")
            if r.get("completeness"):
                meta.append("complete by claim " + ", ".join(r["completeness"]))
            meta.append(f"recorded {r['recorded_at']}")
            o.append(f"- **{r['id']}**: {r['doc']}  \n  _{'; '.join(meta)}_")
        o.append("")
    # 5 claims, per asset
    o.append("## 5 Claims\n\nStatements by an asserter about an asset. Columns: when the claim was asserted, when it is valid, what it rests on.\n")
    by = {}
    for c in claims:
        by.setdefault(c.get("about") or "-", []).append(c)
    for a, cs in by.items():
        o.append(f"### {a}\n\n| id | statement | asserted by | asserted at | valid | backing | qualifier | links |\n|---|---|---|---|---|---|---|---|")
        for c in cs:
            links = "; ".join(x for x in (
                ("requires " + ", ".join(c["depends_on"])) if c.get("depends_on") else "",
                ("supported by " + ", ".join(c["supports"])) if c.get("supports") else "") if x)
            o.append(f"| {c['id']} | `{words(c['assertion'])}` | {c['asserted_by']} | {c['asserted_at']} | "
                     f"{c['valid_from']} to {c.get('valid_to') or 'open'} | {c.get('backing') or ''} | {c.get('qualifier') or ''} | {links} |")
        o.append("")
    # 6 example SQL
    o.append("## 6 Example queries\n\nThe semantic layer's definitions, written as SQL over the tables above. Parameters are shown with example values.\n")
    for c in S["concepts"]:
        if c.get("sql"):
            o.append(f"**{c['id']}**: {c.get('doc', '')}\n\n```sql\n{example_sql(c)}\n```\n")
    return "\n".join(o)


def ids(stem):
    _, rules, claims = integrity.rule_base([str(stem.with_suffix(".edn")), EXT])
    return [r["id"] for r in rules] + [c["id"] for c in claims]


def missing(stem, md):
    return [i for i in ids(stem) if not re.search(rf"(?<![\w.]){re.escape(i)}(?![\w]|\.\d)", md)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="*", default=[25, 50, 100, 200])
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    bad = 0
    for n in a.n:
        stem = BASES / f"N{n:03d}"
        md = render(stem)
        (OUT / f"N{n:03d}.md").write_text(md + "\n")
        m = missing(stem, md)
        bad += bool(m)
        print(f"N={n}: {len(md):,} chars, ~{len(md) // 4:,} tokens; ids {len(ids(stem)) - len(m)}/{len(ids(stem))}"
              + (f" MISSING {m}" if m else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
