"""OWL + SHACL-AF version of the scaling policy (same rules as rules.dl), plus its engine.

emit(w, level, out)  writes schema+rules+data Turtle, runs pySHACL once to materialise the
inferred graph (inferred.nt, engine time recorded), and writes the ./sparql query tool.
"""
import json, pathlib, time

PFX = """@prefix ex:   <http://example.org/proc#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
"""

SCHEMA = """
# ---------- schema (OWL) ----------
ex:CostCentre a owl:Class .  ex:Employee a owl:Class .  ex:Role a owl:Class .
ex:Vendor a owl:Class .      ex:Request a owl:Class .
ex:parent      a owl:ObjectProperty , owl:FunctionalProperty ; rdfs:domain ex:CostCentre ; rdfs:range ex:CostCentre .
ex:booked      a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:domain ex:CostCentre ; rdfs:range xsd:integer .
ex:cap         a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:domain ex:CostCentre ; rdfs:range xsd:integer .
ex:role        a owl:ObjectProperty , owl:FunctionalProperty ; rdfs:domain ex:Employee ; rdfs:range ex:Role .
ex:costCentre  a owl:ObjectProperty , owl:FunctionalProperty ; rdfs:domain ex:Employee ; rdfs:range ex:CostCentre .
ex:reportsTo   a owl:ObjectProperty , owl:FunctionalProperty ; rdfs:domain ex:Employee ; rdfs:range ex:Employee .
ex:limit       a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:domain ex:Role ; rdfs:range xsd:integer .
ex:status      a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:domain ex:Vendor ; rdfs:range xsd:string .
ex:requester   a owl:ObjectProperty , owl:FunctionalProperty ; rdfs:domain ex:Request ; rdfs:range ex:Employee .
ex:amount      a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:domain ex:Request ; rdfs:range xsd:integer .
ex:category    a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:domain ex:Request ; rdfs:range xsd:string .
ex:vendor      a owl:ObjectProperty , owl:FunctionalProperty ; rdfs:domain ex:Request ; rdfs:range ex:Vendor .
ex:violation   a owl:DatatypeProperty ; rdfs:domain ex:Employee ; rdfs:range xsd:boolean .   #L2
ex:emergency   a owl:DatatypeProperty ; rdfs:domain ex:Request ; rdfs:range xsd:boolean .    #L2
# derived by the SHACL rules below; boolean flags are asserted only when true
ex:ancestor a owl:ObjectProperty , owl:TransitiveProperty .  ex:parent rdfs:subPropertyOf ex:ancestor .
ex:inChainOf a owl:ObjectProperty , owl:TransitiveProperty .  ex:reportsTo rdfs:subPropertyOf ex:inChainOf .
ex:bookedTotal a owl:DatatypeProperty .  ex:headroom a owl:DatatypeProperty .  ex:overCap a owl:DatatypeProperty .
ex:charges a owl:ObjectProperty .  ex:capBreach a owl:DatatypeProperty .  ex:hasApprover a owl:DatatypeProperty .
ex:bigCapital a owl:DatatypeProperty .   #L2
ex:vendorOk a owl:DatatypeProperty .  ex:eligible a owl:DatatypeProperty .
ex:denied a owl:DatatypeProperty .       #L2
ex:approved a owl:DatatypeProperty .
"""

# (shape target class, sh:order, CONSTRUCT body, level-2 only?)
RULES = [
    ("CostCentre", 1, "{ $this ex:ancestor ?a } WHERE { $this ex:parent+ ?a }", False),
    ("Employee", 1, "{ $this ex:inChainOf ?m } WHERE { $this ex:reportsTo+ ?m }", False),
    ("Request", 1, '{ $this ex:bigCapital true } WHERE { $this ex:category "capital" ; ex:amount ?a . FILTER(?a > 50000) }', True),
    ("Request", 1, '{ $this ex:vendorOk true } WHERE { $this ex:vendor/ex:status "approved" }', False),
    ("Request", 1, "{ $this ex:denied true } WHERE { $this ex:requester/ex:violation true }", True),
    ("CostCentre", 2, "{ $this ex:bookedTotal ?t } WHERE { { SELECT $this (SUM(?b) AS ?t) WHERE {\n"
                      "      ?d ex:parent* $this . OPTIONAL { ?d ex:booked ?b0 } BIND(COALESCE(?b0, 0) AS ?b) } GROUP BY $this } }", False),
    ("Request", 2, "{ $this ex:charges ?c } WHERE { $this ex:requester/ex:costCentre/ex:parent* ?c }", False),
    ("Request", 2, "{ $this ex:hasApprover true } WHERE { $this ex:requester/ex:inChainOf ?m ; ex:amount ?a .\n"
                   "      ?m ex:role/ex:limit ?l . FILTER(?l >= ?a) }", False),
    ("Request", 2, '{ $this ex:vendorOk true } WHERE { $this ex:emergency true ; ex:vendor/ex:status "suspended" .\n'
                   "      FILTER NOT EXISTS { $this ex:bigCapital true } }", True),
    ("CostCentre", 3, "{ $this ex:headroom ?h } WHERE { $this ex:bookedTotal ?t ; ex:cap ?k . BIND(?k - ?t AS ?h) }", False),
    ("CostCentre", 3, "{ $this ex:overCap true } WHERE { $this ex:bookedTotal ?t ; ex:cap ?k . FILTER(?t > ?k) }", False),
    ("Request", 3, "{ $this ex:capBreach true } WHERE { $this ex:charges ?c ; ex:amount ?a .\n"
                   "      ?c ex:bookedTotal ?t ; ex:cap ?k . FILTER(?t + ?a > ?k) }", False),
    ("Request", 4, "{ $this ex:eligible true } WHERE { $this ex:hasApprover true ; ex:vendorOk true .\n"
                   "      FILTER NOT EXISTS { $this ex:capBreach true } }", False),
    ("Request", 5, "{ $this ex:approved true } WHERE { $this ex:eligible true . FILTER NOT EXISTS { $this ex:denied true } }", False),
]


def rules_ttl(level):
    out = ["\n# ---------- rules (SHACL-AF). sh:order stratifies: a rule reads only properties derived at a lower order ----------",
           'ex:prefixes a owl:Ontology ; sh:declare [ sh:prefix "ex" ; sh:namespace "http://example.org/proc#"^^xsd:anyURI ] .']
    for cls in ["CostCentre", "Employee", "Request"]:
        rs = [r for r in RULES if r[0] == cls and (level == 2 or not r[3])]
        body = " ;\n".join(f'  sh:rule [ a sh:SPARQLRule ; sh:order {o} ; sh:prefixes ex:prefixes ;\n    sh:construct """CONSTRUCT {c}""" ]'
                           for _, o, c, _ in rs)
        out.append(f"ex:{cls}Rules a sh:NodeShape ; sh:targetClass ex:{cls} ;\n{body} .")
    return "\n".join(out) + "\n"


def schema_ttl(level):
    return "\n".join(l.split("#L2")[0].rstrip() for l in SCHEMA.splitlines() if level == 2 or "#L2" not in l) + "\n"


def data_ttl(w, limits, vendors):
    L = ["\n# ---------- data ----------"]
    for c in w["cc"]:
        L.append(f"ex:{c} a ex:CostCentre" + (f" ; ex:parent ex:{w['parent'][c]}" if c in w["parent"] else "")
                 + (f" ; ex:booked {w['booked'][c]}" if c in w["booked"] else "") + f" ; ex:cap {w['cap'][c]} .")
    L += [f"ex:{r} a ex:Role ; ex:limit {l} ." for r, l in limits.items()]
    L += [f'ex:{v} a ex:Vendor ; ex:status "{s}" .' for v, s in vendors.items()]
    viol = set(w["violation"])
    for e, r, c in w["emps"]:
        L.append(f"ex:{e} a ex:Employee ; ex:role ex:{r} ; ex:costCentre ex:{c}"
                 + (f" ; ex:reportsTo ex:{w['reports'][e]}" if e in w["reports"] else "")
                 + (" ; ex:violation true" if e in viol else "") + " .")
    em = set(w["emergency"])
    for r, e, a, k, v in w["reqs"]:
        L.append(f'ex:{r} a ex:Request ; ex:requester ex:{e} ; ex:amount {a} ; ex:category "{k}" ; ex:vendor ex:{v}'
                 + (" ; ex:emergency true" if r in em else "") + " .")
    return "\n".join(L) + "\n"


def emit(w, level, out, limits, vendors, head, qtext, fmt):
    from pyshacl import shacl_rules
    from rdflib import Graph
    schema, rules, data = PFX + schema_ttl(level), PFX + rules_ttl(level), PFX + data_ttl(w, limits, vendors)
    (out / "shacl-schema.ttl").write_text(schema); (out / "shacl-rules.ttl").write_text(rules); (out / "shacl-data.ttl").write_text(data)
    t0 = time.time()
    g = shacl_rules(Graph().parse(data=schema, format="turtle").parse(data=data, format="turtle"),
                    shacl_graph=Graph().parse(data=rules, format="turtle"), advanced=True, iterate_rules=False)
    engine_s = round(time.time() - t0, 2)
    g.serialize(out / "inferred.nt", format="nt")
    block = ("RULES AND FACTS -- the policy as an OWL ontology with SHACL-AF rules and Turtle data\n\n"
             + PFX + schema_ttl(level) + rules_ttl(level) + data_ttl(w, limits, vendors) + "\n")
    (out / "prompt-shacl.txt").write_text(head + block + qtext + fmt)
    (out / "prompt-shacl-tool.txt").write_text(head + block + qtext + fmt +
        "\nA SPARQL endpoint holding this data with every SHACL rule already applied is available. Query it from the shell with\n"
        "  ./sparql 'SELECT ?r WHERE { ?r ex:approved true }'     (the ex: prefix is predefined)\n"
        "Use it as much as you like.\n")
    tool = out / "sparql"
    tool.write_text(SPARQL_SH); tool.chmod(0o755)
    return engine_s, len(block)


SPARQL_SH = r'''#!/usr/bin/env python3
"""./sparql 'SELECT ... WHERE { ... }' -- query the SHACL-inferred graph (inferred.nt)."""
import pathlib, sys
from rdflib import Graph
g = Graph().parse(pathlib.Path(__file__).resolve().parent / "inferred.nt", format="nt")
q = "PREFIX ex: <http://example.org/proc#>\n" + " ".join(sys.argv[1:])
try:
    res = g.query(q)
except Exception as e:
    sys.exit(f"error: {e}")
if res.type == "ASK":
    print("true" if res.askAnswer else "false")
else:
    rows = [" ".join(str(v).split("#")[-1] if v is not None else "-" for v in row) for row in res]
    print("\n".join(rows) if rows else "(no rows)")
'''
