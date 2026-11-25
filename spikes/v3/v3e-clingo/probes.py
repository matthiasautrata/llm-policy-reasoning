"""V3e probes (PLAN-v3-cycles §3), run from the repo root:  .venv/bin/python spikes/v3/v3e-clingo/probes.py
  stable   the plain (two-valued) encoding: count stable models for Y1-Y3; Y2 should have 2, Y3 none (odd loop)
  latency  base decide vs with_hypothesis(withhold) on Q10 and Q38-shaped goals: ground and solve split
  explain  what xclingo / clingexplaid give on the same program
Writes results/probes.json.
"""
import json, os, pathlib, statistics, sys, time
os.environ.setdefault("V3E_ENCODING", "doubled")   # plain_rule_body rewrites the doubled per-rule text
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import host  # noqa: E402
from host import asp, clingo, sql, Session, View, World, Ctx, read_edn  # noqa: E402

SH = HERE.parent / "shared"
CFG = {"backend": "duckdb", "duckdb": "spikes/v3/shared/slice.duckdb", "fetch_limit": 10000}
D = "2026-07-15"


def session():
    sql.configure(json.dumps(CFG), os.getcwd())
    S = Session()
    for f in ("slice.edn", "extension.edn", "cycles.edn"):
        S.load_file(SH / f)
    return S


def demand(S, G):
    A = G[1] if G[0] == "neg" else G
    bp = asp.bound_positions(A[0], S.meta.modes)
    return f"dm({asp.pn(A[0])},{asp.tup(asp.term(A[1 + i]) for i in bp)})."


def stable(S, G, limit=10):
    """stable models of the plain encoding restricted to G's demand; returns [def atoms per model] (G's pred only)"""
    sql.begin_op()
    texts = [asp.plain_rule_body(t) for t in S.store.text.values()]
    prog = "\n".join([asp.PLAIN_META, S.meta.func_text, *texts, f"asof({asp.q(D)}).", demand(S, G),
                      "active(X) :- kind(X,_)."])
    ctl = clingo.Control([str(limit), "--warn=none"])
    ctl.add("base", [], prog.replace("[free]", ""))
    ctl.ground([("base", [])], context=Ctx(S.meta))
    ms = []
    ctl.solve(on_model=lambda m: ms.append(sorted(str(s) for s in m.symbols(shown=True)
                                                 if str(s.arguments[0]).lstrip("neg(").startswith(G[0]))))
    sql.take_log()
    return ms


def mus_probe(S, G):
    """clingexplaid: the plain encoding of G with active/1 as free externals, all assumed true -> a minimal
    unsatisfiable subset of rule ids (for an odd loop, the loop's members)"""
    from clingexplaid.unsat.computer import SubsetComputer
    sql.begin_op()
    texts = [asp.plain_rule_body(t) for t in S.store.text.values()]
    prog = "\n".join([asp.PLAIN_META, S.meta.func_text, *texts, f"asof({asp.q(D)}).", demand(S, G)])
    ctl = clingo.Control(["--warn=none"])
    ctl.add("base", [], prog)
    ctl.ground([("base", [])], context=Ctx(S.meta))
    ids = list(S.store.rules) + list(S.store.claims)
    sc = SubsetComputer(ctl, [(clingo.Function("active", [clingo.String(i)]), True) for i in ids])
    t = time.time()
    m = sc.mus()
    sql.take_log()
    return {"type": type(m).__name__, "ids": sorted((a[0] if isinstance(a, tuple) else a.symbol).arguments[0].string for a in m), "ms": round((time.time() - t) * 1000, 1)}


def latency(S, G, withhold, n=30):
    sql.begin_op()
    base, hyp = [], []
    for _ in range(n):
        for lst, view in ((base, S.store), (hyp, None)):
            if view is None:
                view = View(S.store); view.withheld |= set(withhold)
            sql.begin_op()
            t = time.time()
            W = World(view, D, [G])
            W.evaluate(G)
            lst.append({"total": (time.time() - t) * 1000, **W.timing})
            sql.take_log()
    agg = lambda L, kk: round(statistics.median(x[kk] for x in L), 2)
    return {kk: {"base": agg(base, kk), "hypothesis": agg(hyp, kk)} for kk in ("total", "ground_ms", "solve_ms")}


def explain_probe():
    out = {}
    try:
        import xclingo, importlib.metadata as md
        out["xclingo"] = {"version": md.version("xclingo")}
        from xclingo import XclingoControl
        x = XclingoControl(["0"])
        x.add("base", [], "%!trace_rule {\"% is preferred\", X}\npreferred(X) :- approved(X), not suspended(X).\n"
                         "approved(dyne).\n%!trace {\"% approved\",X} approved(X).\n%!show_trace preferred(X).\n")
        x.ground([("base", [])])
        out["xclingo"]["toy"] = [str(e) for m in x.solve() for e in m.explain_model()][:3]
    except Exception as e:  # noqa: BLE001
        out.setdefault("xclingo", {})["error"] = f"{type(e).__name__}: {e}"
    try:
        import clingexplaid, importlib.metadata as md
        out["clingexplaid"] = {"version": md.version("clingexplaid"),
                               "gives": "MUS/MSS/MCS over assumptions, unsat constraints: explains why a program has no model, "
                                        "not why an atom holds (see mus)"}
    except Exception as e:  # noqa: BLE001
        out.setdefault("clingexplaid", {})["error"] = f"{type(e).__name__}: {e}"
    return out


def main():
    S = session()
    res = {"clingo": clingo.__version__, "stable": {}, "latency": {}}
    for name, G in (("Y1 blacklisted fern", ["blacklisted", "fern"]), ("Y2 preferred dyne", ["preferred", "dyne"]),
                    ("Y2 control preferred acme", ["preferred", "acme"]), ("Y3 trusted edge", ["trusted", "edge"])):
        ms = stable(S, G)
        res["stable"][name] = {"models": len(ms), "def_atoms": ms}
        print(f"stable  {name:28} {len(ms)} model(s) {ms}")
    for name, G in (("Y3 trusted edge", ["trusted", "edge"]), ("Y2 preferred dyne", ["preferred", "dyne"])):
        res.setdefault("mus", {})[name] = r = mus_probe(S, G)
        print(f"mus     {name:28} {r}")
    for name, G, wh in (("Q10 cost_centre_of e077", ["cost_centre_of", "e077", "?c"], ["R313"]),
                        ("Q38 preferred dyne", ["preferred", "dyne"], ["RY23"])):
        Gg = G if host.ground(G) else ["cost_centre_of", "e077", "cc0077"]
        res["latency"][name] = latency(S, Gg, wh)
        print(f"latency {name:28} {res['latency'][name]}")
    res["explain"] = explain_probe()
    print("explain", json.dumps(res["explain"])[:600])
    (HERE / "results" / "probes.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
