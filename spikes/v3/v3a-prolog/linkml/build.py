"""V3a model build: EDN -> LinkML instances, validate, docs, DDL comparison.

  .venv/bin/python spikes/v3/v3a-prolog/linkml/build.py

Steps
  1 edn2yaml: shared/slice.edn + extension.edn -> slice.instance.yaml
  2 linkml-validate the schema against the metamodel, the instances against the schema
  3 rule heads/bodies/assertions are EDN strings LinkML cannot see into: parse each with the V3a EDN reader
  4 gen-doc: schema docs -> docs/schema/; instance docs (the G arm's material) -> docs/slice.md
  5 physical model -> physical.yaml (one class per table) -> gen-sqlddl (postgresql) -> physical.sql;
    compare columns and types with shared/gen.py's DDL -> ddl_compare.md
"""
import pathlib, re, subprocess, sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BIN = ROOT / ".venv" / "bin"
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "shared"))
import edn2yaml  # noqa: E402


def sh(*args, **kw):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True, cwd=HERE, **kw)
    if p.returncode:
        raise SystemExit(f"{args[0]} failed:\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}")
    return p.stdout


def edn_check(doc):
    """Every EDN string must parse with edn.pl (the reader V3a loads rules with)."""
    import janus_swi as janus
    janus.consult(str(HERE.parent / "edn.pl"))
    texts = [(r["id"], k, r[k]) for r in doc["rules"] for k in ("head", "body") if k in r]
    for c in doc["claims"]:
        texts.append((c["id"], "assertion", c["assertion"]))
        texts += [(s["id"], "assertion", s["assertion"]) for s in c.get("subclaims") or []]
    bad = [t for t in texts if not janus.query_once("catch(edn:edn_parse(S, _), _, fail)", {"S": t[2]})["truth"]]
    return len(texts), bad


SQLTYPE = {"id": "string", "enum": "string", "int": "integer", "bool": "boolean", "date": "date"}


def physical_schema(doc, keys=None):
    """keys (pass B): {table: {column: (type, not_null, pk)}} from gen.py, mapped onto LinkML
    required / identifier (single-column key) / unique_keys (composite key)."""
    classes = {}
    for t in doc["tables"]:
        cls = {"description": t["doc"], "attributes": {}}
        k = (keys or {}).get(t["name"], {})
        pks = [c for c, v in k.items() if v[2]]
        for c in t["columns"]:
            a = {"range": SQLTYPE[c["column_type"]], "description": c["doc"]}
            if c["name"] in k and k[c["name"]][1]: a["required"] = True
            if len(pks) == 1 and c["name"] == pks[0]: a["identifier"] = True
            cls["attributes"][c["name"]] = a
        if len(pks) > 1: cls["unique_keys"] = {f"{t['name']}_pk": {"unique_key_slots": pks}}
        classes[t["name"]] = cls
    return {"id": "https://example.org/llm-policy-reasoning/spike-v3/physical", "name": "physical",
            "prefixes": {"linkml": "https://w3id.org/linkml/"}, "imports": ["linkml:types"],
            "default_range": "string", "classes": classes}


def parse_ddl(sql):
    """CREATE TABLE blocks -> {table: {column: (type, not_null, pk)}}"""
    out = {}
    for m in re.finditer(r'CREATE TABLE "?(\w+)"? \((.*?)\n\);', sql, re.S):
        cols = {}
        body = m.group(2)
        pk = re.search(r"PRIMARY KEY \(([^)]*)\)", body)
        pks = {c.strip().strip('"') for c in pk.group(1).split(",")} if pk else set()
        for line in body.split(",\n"):
            line = line.strip()
            cm = re.match(r'"?(\w+)"?\s+([A-Z]+)(.*)', line)
            if cm and not line.startswith(("PRIMARY", "FOREIGN", "UNIQUE")):
                cols[cm.group(1)] = (cm.group(2), "NOT NULL" in cm.group(3) or "PRIMARY KEY" in cm.group(3),
                                     cm.group(1) in pks or "PRIMARY KEY" in cm.group(3))
        out[m.group(1)] = cols
    return out


def gen_ddl():
    from gen import DDL
    out = {}
    for t, body in DDL.items():
        cols, pks = {}, set()
        pk = re.search(r"PRIMARY KEY \(([^)]*)\)", body)
        if pk: pks = {c.strip() for c in pk.group(1).split(",")}
        for part in re.split(r",\s*(?![^()]*\))", body):
            part = part.strip()
            if part.startswith("PRIMARY KEY"): continue
            cm = re.match(r'"?(\w+)"?\s+([A-Z]+)(.*)', part)
            cols[cm.group(1)] = (cm.group(2), "NOT NULL" in cm.group(3) or "PRIMARY KEY" in cm.group(3),
                                 cm.group(1) in pks or "PRIMARY KEY" in cm.group(3))
        out[t] = cols
    return out


NORM = {"TEXT": "VARCHAR", "VARCHAR": "VARCHAR", "INTEGER": "INTEGER", "BOOLEAN": "BOOLEAN", "DATE": "DATE"}


def compare(lm, g):
    rows, mism = [], 0
    for t in g:
        for c, (ty, nn, pk) in g[t].items():
            l = lm.get(t, {}).get(c)
            if l is None:
                rows.append(f"| {t}.{c} | {ty} {'NOT NULL' if nn else ''}{' PK' if pk else ''} | (missing) | column |"); mism += 1; continue
            diffs = []
            if NORM.get(l[0], l[0]) != NORM.get(ty, ty): diffs.append(f"type {l[0]} vs {ty}")
            if l[1] != nn: diffs.append("nullability")
            if l[2] != pk: diffs.append("primary key")
            if diffs:
                mism += 1
                rows.append(f"| {t}.{c} | {ty}{' NOT NULL' if nn else ''}{' PK' if pk else ''} | {l[0]}{' NOT NULL' if l[1] else ''}{' PK' if l[2] else ''} | {', '.join(diffs)} |")
    for t in lm:
        for c in lm[t]:
            if c not in g.get(t, {}):
                rows.append(f"| {t}.{c} | (absent) | {lm[t][c][0]} | extra column |"); mism += 1
    return rows, mism, sum(len(v) for v in g.values())


def md_escape(s):
    return str(s).replace("|", "\\|")


def instance_docs(doc):
    L = ["# Procurement slice: model, vocabulary, rules, claims", "",
         f"Evaluation date: {doc['today']}. Generated from `shared/slice.edn` by `v3a-prolog/linkml/build.py`.", ""]
    L += ["## Tables", ""]
    for t in doc["tables"]:
        L += [f"### {t['name']} (`{t['id']}`)", "", t["doc"], "", "| column | type | meaning |", "|---|---|---|"]
        L += [f"| {c['name']} | {c['column_type']} | {md_escape(c['doc'])} |" for c in t["columns"]]
        L += [""]
    L += ["## Semantic layer", "", "| concept | kind | parameters | columns | meaning |", "|---|---|---|---|---|"]
    for c in doc["concepts"]:
        L.append(f"| {c['concept_name']} | {c['kind']} | {', '.join(c.get('params') or []) or '—'} | "
                 f"{', '.join(c.get('columns_out') or []) or '—'} | {md_escape(c['doc'])} |")
    L += ["", "## Vocabulary", ""]
    for t in doc["terms"]:
        syn = f" (also: {', '.join(t['synonyms'])})" if t.get("synonyms") else ""
        see = f" See {', '.join(t['see'])}." if t.get("see") else ""
        L += [f"- **{t['label']}**{syn} — {t['definition']}{see} *Owner: {t['owner']}.*"]
    L += ["", "## Code lists", ""] + [f"- `{c['id']}`: {', '.join(c['values'])}" for c in doc["code_lists"]]
    L += ["", "## Rules", "", "| id | kind | owner | rule |", "|---|---|---|---|"]
    for r in doc["rules"]:
        extra = f" Prevails over {', '.join(r['superior_to'])}." if r.get("superior_to") else ""
        L.append(f"| {r['id']} | {r['kind']} | {r['owner']} | {md_escape(r['doc'])}{extra} |")
    L += ["", "## Claims", ""]
    for c in doc["claims"]:
        to = c.get("valid_to") or "open"
        L += [f"- **{c['id']}** about `{c['about']}`: `{c['assertion']}` — {c['asserted_by']}, {c['asserted_at']}, "
              f"in force {c['valid_from']}–{to}; {c.get('qualifier', '')}; backing: {c.get('backing', '')}"]
        for s in c.get("subclaims") or []:
            L += [f"  - {s['id']} ({s['role']}): `{s['assertion']}` — {s['asserted_by']}, {s['asserted_at']}, "
                  f"in force {s['valid_from']}–{s.get('valid_to') or 'open'}"]
    return "\n".join(L) + "\n"


def main():
    doc = edn2yaml.convert()
    inst = HERE / "slice.instance.yaml"
    inst.write_text("# generated by edn2yaml.py from shared/slice.edn + shared/extension.edn; do not edit\n"
                    + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))
    print("1 instances:", sum(1 for _ in inst.open()), "lines")
    print("2 schema:", sh(BIN / "linkml-validate", "slice.yaml").strip(),
          "| instances:", sh(BIN / "linkml-validate", "-s", "slice.yaml", "-C", "Slice", inst.name).strip())
    n, bad = edn_check(doc)
    print(f"3 EDN strings: {n} parsed, {len(bad)} bad", bad or "")
    sh(BIN / "gen-doc", "slice.yaml", "-d", "docs/schema")
    (HERE / "docs").mkdir(exist_ok=True)
    (HERE / "docs" / "slice.md").write_text(instance_docs(doc))
    print("4 docs: docs/schema/ (gen-doc),", sum(1 for _ in (HERE / "docs" / "slice.md").open()), "lines docs/slice.md")
    g = gen_ddl()
    out = ["# DDL: LinkML (gen-sqlddl, postgresql) vs shared/gen.py", "",
           "Generated by `build.py`. Column names, order and types agree in both passes (VARCHAR/TEXT are the same "
           "type in Postgres and DuckDB); `\"limit\"` is quoted by both. Neither pass emits gen.py's three secondary "
           "indexes (emp_cc, req_requester, cc_parent): LinkML has no index construct. Both generated files load into Postgres 18 "
           "(`psql -f`, checked by hand on 2026-11-24).", ""]
    for tag, keys, note in [
        ("A", None, "Physical model as the slice records it: column types and docs only. Everything is nullable "
                    "and there are no keys."),
        ("B", g, "Same model, with gen.py's NOT NULL and primary keys written into it as LinkML `required`, "
                 "`identifier` (single-column key) and `unique_keys` (composite key).")]:
        f = f"physical{'' if tag == 'A' else '_keys'}"
        (HERE / f"{f}.yaml").write_text(yaml.safe_dump(physical_schema(doc, keys), sort_keys=False, width=120))
        ddl = sh(BIN / "gen-sqlddl", "--dialect", "postgresql", "--no-metadata", "--no-use-foreign-keys", f"{f}.yaml")
        (HERE / f"{f}.sql").write_text(ddl)
        rows, mism, total = compare(parse_ddl(ddl), g)
        uk = re.findall(r"UNIQUE \(([^)]*)\)", ddl)
        out += [f"## Pass {tag}: `{f}.yaml` -> `{f}.sql`", "", note, "",
                f"{total} generator columns, {mism} mismatches."
                + (f" Composite keys come out as UNIQUE ({'; '.join(uk)}), not PRIMARY KEY, and UNIQUE does not "
                   "imply NOT NULL." if uk else ""), ""]
        if rows: out += ["| column | gen.py | LinkML | difference |", "|---|---|---|---|"] + rows + [""]
        print(f"5{tag} DDL: {total} columns, {mism} mismatches")
    (HERE / "ddl_compare.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
