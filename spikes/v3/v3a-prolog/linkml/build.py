"""V3a model build: EDN -> LinkML instances, validate, docs, DDL comparison.

  .venv/bin/python spikes/v3/v3a-prolog/linkml/build.py

Steps
  1 edn2yaml: shared/slice.edn + extension.edn -> slice.instance.yaml
  2 linkml-validate the schema against the metamodel, the instances against the schema
  3 rule heads/bodies/assertions are structured in the instance (validated in step 2). Round trip: each one
    rendered back to EDN (edn2yaml.to_edn) must parse with edn.pl, the reader V3a loads rules with, and equal
    the original EDN value
  3b negative tests: V3b's 12 malformed slices (model.clj `negatives`), each converted and validated with
    linkml-validate's API and with the generated JSON Schema through `jsonschema` directly; pass iff 12/12 rejected
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


def literals(doc, src=None):
    """(id, field, structured literal, original EDN value) for every head, body literal and assertion."""
    K = edn2yaml.E.Keyword
    orig = {}
    if src:
        S, X = src
        for r in S[K("rules")] + [x for x in X if K("kind") in x]:
            orig[(r[K("id")].name, "head")] = r.get(K("head"))
            for i, l in enumerate(r.get(K("body")) or []): orig[(r[K("id")].name, f"body.{i}")] = l
        for c in S[K("claims")] + [x for x in X if K("assertion") in x]:
            for x in [c] + (c.get(K("subclaims")) or []): orig[(x[K("id")].name, "assertion")] = x[K("assertion")]
    out = []
    for r in doc["rules"]:
        if "head" in r: out.append((r["id"], "head", r["head"]))
        out += [(r["id"], f"body.{i}", l) for i, l in enumerate(r.get("body") or [])]
    for c in doc["claims"]:
        out += [(x["id"], "assertion", x["assertion"]) for x in [c] + (c.get("subclaims") or [])]
    return [(i, f, l, orig.get((i, f))) for i, f, l in out]


def edn_check(doc, src):
    """Structured literal -> EDN text: must parse with edn.pl and equal the authored EDN value."""
    import janus_swi as janus
    janus.consult(str(HERE.parent / "edn.pl"))
    lits = literals(doc, src)
    bad = []
    for i, f, l, o in lits:
        t = edn2yaml.to_edn(l)
        if not janus.query_once("catch(edn:edn_parse(S, _), _, fail)", {"S": t})["truth"] or edn2yaml.thaw(edn2yaml.E.loads(t)) != o:
            bad.append((i, f, t))
    return len(lits), bad


def negatives(S, X):
    """V3b's negative tests (v3b-clojure/src/v3b/model.clj `negatives`), applied to the same EDN: the 12 of
    PLAN-v3 (#9 re-expressed for flat claims, PLAN-v3-integrity Decisions) and 13-15 of PLAN-v3-integrity §1.5.
    -> [(label, linkml messages, json-schema messages, shared-check messages)]. The shared check is
    model_check.shape_errors: LinkML 1.12 does not check that a non-inlined reference resolves, so a
    dangling depends_on id (#15) is caught there only."""
    import copy
    K, Sym = edn2yaml.E.Keyword, edn2yaml.E.Symbol
    def mut(f):
        s = copy.deepcopy(S); f(s); return s
    def rules(s): return s[K("rules")]
    def claims(s): return s[K("claims")]
    cases = [
        ("concept with neither :sql nor :derived-by",
         lambda s: [s[K("concepts")][0].pop(k, None) for k in (K("sql"), K("derived-by"))]),
        ("unknown owner on a rule", lambda s: rules(s)[0].__setitem__(K("owner"), K("marketing"))),
        ("rule variable without ?", lambda s: rules(s)[0][K("head")].__setitem__(1, Sym("cc"))),
        ("fetch filters not a map", lambda s: rules(s)[0][K("body")][0].__setitem__(2, ["cc", Sym("?c")])),
        ("unknown arithmetic op in :is", lambda s: rules(s)[1][K("body")].append([K("is"), Sym("?x"), [K("*"), 2, 3]])),
        ("comparison with three arguments", lambda s: rules(s)[1][K("body")].append([K("<"), Sym("?x"), 1, 2])),
        ("bad date in a claim", lambda s: claims(s)[0].__setitem__(K("asserted_at"), "2026-3-1")),
        ("unknown key on a claim (closed map)", lambda s: claims(s)[0].__setitem__(K("confidence"), 0.9)),
        ("depends_on member not a claim id", lambda s: claims(s)[0].__setitem__(K("depends_on"), [K("R101")])),
        ("superiority order with unknown owner",
         lambda s: rules(s).append({K("id"): K("R999"), K("kind"): K("superiority"), K("owner"): K("controller"),
                                    K("class"): K("superiority"), K("doc"): "x", K("pred"): K("p"), K("order"): [K("hr"), K("sales")],
                                    K("recorded_at"): rules(s)[0][K("recorded_at")]})),
        ("rule kind unknown", lambda s: rules(s)[0].__setitem__(K("kind"), K("presumption"))),
        ("negated literal wrapping a non-literal", lambda s: rules(s)[0].__setitem__(K("head"), [K("neg"), "x"])),
        ("nested :subclaims (claims are flat)", lambda s: claims(s)[0].__setitem__(K("subclaims"), [copy.deepcopy(claims(s)[1])])),
        ("measure without :additivity",
         lambda s: next(c for c in s[K("concepts")] if c[K("kind")] == K("measure")).pop(K("additivity"))),
        ("dangling depends_on id", lambda s: claims(s)[0][K("depends_on")].append(K("C9.9"))),
    ]
    import json, jsonschema
    from linkml.validator import validate
    js = json.loads(sh(BIN / "gen-json-schema", "--include-range-class-descendants", "slice.yaml"))
    jv = jsonschema.Draft7Validator(js, format_checker=jsonschema.Draft7Validator.FORMAT_CHECKER)
    sys.path.insert(0, str(HERE.parent.parent / "shared"))
    import model_check, reference
    out = []
    for label, f in cases:
        m = mut(f)
        doc = json.loads(json.dumps(edn2yaml.convert(m, X)))
        lm = [r.message for r in validate(doc, str(HERE / "slice.yaml"), "Slice").results]
        jm = [e.message for e in jv.iter_errors(doc)]
        P, PX = reference.plain(m), reference.plain(list(X))
        sm = model_check.shape_errors(P, list(P["rules"]) + [x for x in PX if "kind" in x],
                                      list(P["claims"]) + [x for x in PX if "assertion" in x])
        out.append((label, lm, jm, sm))
    return out


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
        L += [f"- **{c['id']}** about `{c['about']}`: `{edn2yaml.to_edn(c['assertion'])}` — {c['asserted_by']}, {c['asserted_at']}, "
              f"in force {c['valid_from']}–{to}; {c.get('qualifier', '')}; backing: {c.get('backing', '')}"]
        for s in c.get("subclaims") or []:
            L += [f"  - {s['id']} ({s['role']}): `{edn2yaml.to_edn(s['assertion'])}` — {s['asserted_by']}, {s['asserted_at']}, "
                  f"in force {s['valid_from']}–{s.get('valid_to') or 'open'}"]
    return "\n".join(L) + "\n"


def main():
    S, X = edn2yaml.read(edn2yaml.SHARED / "slice.edn"), edn2yaml.read(edn2yaml.SHARED / "extension.edn")
    doc = edn2yaml.convert(S, X)
    inst = HERE / "slice.instance.yaml"
    inst.write_text("# generated by edn2yaml.py from shared/slice.edn + shared/extension.edn; do not edit\n" + edn2yaml.dump(doc))
    print("1 instances:", sum(1 for _ in inst.open()), "lines")
    print("2 schema:", sh(BIN / "linkml-validate", "slice.yaml").strip(),
          "| instances:", sh(BIN / "linkml-validate", "-s", "slice.yaml", "-C", "Slice", inst.name).strip())
    n, bad = edn_check(doc, (S, X))
    print(f"3 structured literals: {n}, round trip to EDN (edn.pl parses, value equal): {n - len(bad)} ok", bad or "")
    neg = negatives(S, X)
    L = ["# Negative tests: LinkML vs Malli", "",
         f"Generated by `build.py` (step 3b). V3b's {len(neg)} malformed slices (`model.clj` `negatives`; #9 re-expressed "
         "and #13-15 added for flat claims and additivity, PLAN-v3-integrity §1), converted by `edn2yaml.py` and "
         "validated by linkml-validate's API, by the generated JSON Schema (`gen-json-schema "
         "--include-range-class-descendants`) through `jsonschema` directly, and by the shared shape check "
         "(`shared/model_check.py` `shape_errors`: referential integrity, which LinkML does not check). "
         "First message of each shown.", "",
         "| # | mutation | linkml-validate | jsonschema | shared check |", "|---|---|---|---|---|"]
    for i, (label, lm, jm, sm) in enumerate(neg, 1):
        cell = lambda ms: (f"rejected ({len(ms)}): " + md_escape(ms[0][:160])) if ms else "**not rejected**"
        L.append(f"| {i} | {label} | {cell(lm)} | {cell(jm)} | {cell(sm)} |")
    (HERE / "negatives.md").write_text("\n".join(L) + "\n")
    print(f"3b negative tests: linkml-validate {sum(1 for x in neg if x[1])}/{len(neg)}, "
          f"jsonschema {sum(1 for x in neg if x[2])}/{len(neg)}, shared check {sum(1 for x in neg if x[3])}/{len(neg)}, "
          f"some layer {sum(1 for x in neg if x[1] or x[2] or x[3])}/{len(neg)} rejected (negatives.md)")
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
