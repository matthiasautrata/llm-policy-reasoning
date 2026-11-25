"""V3a host: Python embeds SWI-Prolog via janus_swi; Prolog calls back into sql.py for every fetch."""
import json, os, pathlib, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import janus_swi as janus  # noqa: E402
import sql  # noqa: E402,F401  (imported so Prolog's py_call(sql:...) finds the same module)
sys.path.insert(0, str(HERE.parent / "shared"))
import integrity  # noqa: E402  (the shared integrity gate, PLAN-v3-integrity §2)


class Gate:
    """Integrity gate around the Prolog session: the load, every `add`, every `with_hypothesis` are
    checked against the rule base they would produce before Prolog sees them. A rejected op returns
    {"error": {"op", "violations"}} and leaves the state unchanged."""
    def __init__(self, load):
        self.load, self.added = load, []

    def check(self, op):
        if op.get("op") == "add":
            v = integrity.gate(self.load, self.added + [op.get("edn") or "[]"])
        elif op.get("op") == "with_hypothesis":
            v = integrity.gate(self.load, self.added + ([op["add"]] if op.get("add") else []), op.get("withhold") or [])
        else:
            return None
        return {"error": {"op": op["op"], "violations": v}, "ms": 0, "sql_log": []} if v else None

    def done(self, op, result):
        if op.get("op") == "add" and "error" not in result:
            self.added.append(op.get("edn") or "[]")


def main():
    script = json.load(sys.stdin)
    root = os.getcwd()
    t0 = time.time()
    gate = Gate(script.get("load", []))
    v = integrity.gate(gate.load)
    if v:   # load rejected before the engine reads anything (the gate runs before LinkML / Prolog parsing)
        json.dump({"error": {"op": "load", "violations": v}, "results": [], "load_ms": (time.time() - t0) * 1000}, sys.stdout)
        return
    janus.consult(str(HERE / "ops.pl"))
    sql.configure(json.dumps(script["config"]), root)
    if "hypothesis" in script["config"]:   # "snapshot" (default) | "assert" (original, not isolated)
        janus.query_once("ops:set_hyp_mode(M)", {"M": script["config"]["hypothesis"]})
    janus.query_once("ops:load_files_json(J)", {"J": json.dumps(script.get("load", []))})
    load_ms = (time.time() - t0) * 1000
    results = []
    for op in script.get("ops", []):
        t = time.time()
        rej = gate.check(op)
        if rej:
            rej["ms"] = (time.time() - t) * 1000
            results.append(rej)
            continue
        r = json.loads(janus.query_once("ops:run_op(J, Out)", {"J": json.dumps(op)})["Out"])
        gate.done(op, r)
        results.append(r)
    out = {"results": results, "load_ms": load_ms}
    if "concurrent" in script:   # test mode: each op list in its own Prolog thread (shared/isolation.py)
        out["concurrent"] = json.loads(janus.query_once("ops:run_concurrent(J, Out)",
                                                        {"J": json.dumps(script["concurrent"])})["Out"])
    if "after" in script:        # ops run on the main thread after the concurrent lists have joined
        out["after"] = [json.loads(janus.query_once("ops:run_op(J, Out)", {"J": json.dumps(op)})["Out"])
                        for op in script["after"]]
    if script.get("memo_test"):
        out["memo_test"] = janus.query_once("ops:memo_test(Out)")["Out"]
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
