"""SHACL arm == Datalog arm: every derived relation, tuple for tuple, per world.
  python scaling/check_shacl.py scaling/worlds/*"""
import pathlib, subprocess, sys, tempfile
from rdflib import Graph
P = {"cc_anc": "?x ex:ancestor ?y", "chain": "?x ex:inChainOf ?y", "booked_total": "?x ex:bookedTotal ?y",
     "headroom": "?x ex:headroom ?y", "over_cap": "?x ex:overCap true", "charges": "?x ex:charges ?y",
     "cap_breach": "?x ex:capBreach true", "has_approver": "?x ex:hasApprover true", "vendor_ok": "?x ex:vendorOk true",
     "eligible": "?x ex:eligible true", "denied": "?x ex:denied true", "approved": "?x ex:approved true"}
bad = 0
for w in map(pathlib.Path, sys.argv[1:]):
    g = Graph().parse(w / "inferred.nt", format="nt")
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, "p.dl").write_text((w / "program.dl").read_text() + "".join(f".output {r}\n" for r in P))
        subprocess.run(["souffle", "-w", "-D", d, f"{d}/p.dl"], check=True, capture_output=True)
        S = {r: {tuple(l.split("\t")) for l in pathlib.Path(d, f"{r}.csv").read_text().splitlines() if l} for r in P}
    loc = lambda v: str(v).split("#")[-1]
    diffs = []
    for r, pat in P.items():
        vars_ = "?x ?y" if "?y" in pat else "?x"
        Q = {tuple(loc(v) for v in row) for row in g.query(f"PREFIX ex: <http://example.org/proc#> SELECT {vars_} {{ {pat} }}")}
        if Q != S[r]: diffs.append((r, len(S[r] - Q), len(Q - S[r])))
    bad += bool(diffs)
    print(f"{w.name:10} {'OK' if not diffs else 'MISMATCH ' + str(diffs)}  ({sum(len(v) for v in S.values())} tuples)")
sys.exit(bool(bad))
