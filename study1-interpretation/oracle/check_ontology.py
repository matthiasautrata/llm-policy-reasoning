"""Execute the phase-B OWL+SHACL arm with pySHACL and check it against the Soufflé oracle:
every derived relation must be tuple-for-tuple identical."""
import pathlib, subprocess, sys, tempfile
from pyshacl import shacl_rules
from rdflib import Graph

root = pathlib.Path(__file__).resolve().parents[1]
arm, dl = root / "arms/large-owl-shacl", root / "oracle/large"
g = shacl_rules(Graph().parse(arm / "schema.ttl").parse(arm / "data.ttl"),
                shacl_graph=Graph().parse(arm / "rules.ttl"), advanced=True, iterate_rules=False)

def souffle(program):
    d = pathlib.Path(tempfile.mkdtemp()); (d / "p.dl").write_text(program)
    subprocess.run(["souffle", "-w", "-D", str(d), str(d / "p.dl")], check=True, capture_output=True)
    return lambda rel: {tuple(l.split("\t")) for l in (d / f"{rel}.csv").read_text().splitlines() if l}

def sparql(q):
    loc = lambda x: str(x).split("#")[-1]
    return {tuple(loc(v) for v in row) for row in g.query("PREFIX ex: <http://example.org/proc#>\n" + q)}

# relation-by-relation equivalence
pairs = {
    "cc_anc": "SELECT ?c ?a {?c ex:ancestorCostCentre ?a}", "booked_at": "SELECT ?c ?t {?c ex:bookedSpend ?t}",
    "headroom": "SELECT ?c ?h {?c ex:headroom ?h}", "over_committed": "SELECT ?c {?c ex:overCommitted true}",
    "charges": "SELECT ?r ?c {?r ex:charges ?c}", "cap_breach": "SELECT ?r ?c {?r ex:breachesCapOf ?c}",
    "vendor_ok": "SELECT ?r {?r ex:vendorCheckPassed true}", "chain": "SELECT ?e ?m {?e ex:inReportingChainOf ?m}",
    "approver": "SELECT ?r ?e {?r ex:eligibleApprover ?e}", "dept_headcount": "SELECT ?c ?n {?c ex:headcount ?n}",
    "dept_exposure": "SELECT ?c ?s {?c ex:pendingExposure ?s}", "escalation": "SELECT ?r {?r ex:requiresEscalation true}",
    "deny": "SELECT ?r {?r ex:denied true}", "auto_approve": "SELECT ?r {?r ex:autoApproved true}",
    "conflict": "SELECT ?r {?r ex:inConflict true}", "exempt": "SELECT ?r {?r ex:exempt true}",
}
rel = souffle((dl / "rules.dl").read_text() + (dl / "facts.dl").read_text() + "".join(f".output {r}\n" for r in pairs))
bad = {r: (len(rel(r) ^ sparql(q))) for r, q in pairs.items() if rel(r) != sparql(q)}
for r, q in pairs.items():
    print(f"{r:15} {len(rel(r)):4} tuples  {'OK' if r not in bad else 'MISMATCH'}")
print("OWL+SHACL arm == Datalog arm on all derived relations" if not bad else f"MISMATCH {bad}")
sys.exit(bool(bad))
