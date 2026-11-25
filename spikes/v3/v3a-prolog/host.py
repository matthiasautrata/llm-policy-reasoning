"""V3a host: Python embeds SWI-Prolog via janus_swi; Prolog calls back into sql.py for every fetch."""
import json, os, pathlib, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import janus_swi as janus  # noqa: E402
import sql  # noqa: E402,F401  (imported so Prolog's py_call(sql:...) finds the same module)


def main():
    script = json.load(sys.stdin)
    root = os.getcwd()
    t0 = time.time()
    janus.consult(str(HERE / "ops.pl"))
    sql.configure(json.dumps(script["config"]), root)
    if "hypothesis" in script["config"]:   # "snapshot" (default) | "assert" (original, not isolated)
        janus.query_once("ops:set_hyp_mode(M)", {"M": script["config"]["hypothesis"]})
    # evaluation mode: ENGINE_MODE (accept.py --mode) or config "eval": wfs (default) | memo;
    # table policy: config "tables": op (default: abolish at every op) | session (keep; keyed by state, as_of)
    mode = script["config"].get("eval") or os.environ.get("ENGINE_MODE") or "wfs"
    janus.query_once("defeasible:set_eval_mode(M)", {"M": mode})
    janus.query_once("defeasible:set_table_policy(M)", {"M": script["config"].get("tables") or os.environ.get("V3A_TABLES") or "op"})
    janus.query_once("ops:load_files_json(J)", {"J": json.dumps(script.get("load", []))})
    load_ms = (time.time() - t0) * 1000
    results = []
    for op in script.get("ops", []):
        r = janus.query_once("ops:run_op(J, Out)", {"J": json.dumps(op)})
        results.append(json.loads(r["Out"]))
    out = {"results": results, "load_ms": load_ms}
    if "concurrent" in script:   # test mode: each op list in its own Prolog thread (shared/isolation.py)
        out["concurrent"] = json.loads(janus.query_once("ops:run_concurrent(J, Out)",
                                                        {"J": json.dumps(script["concurrent"])})["Out"])
    if "after" in script:        # ops run on the main thread after the concurrent lists have joined
        out["after"] = [json.loads(janus.query_once("ops:run_op(J, Out)", {"J": json.dumps(op)})["Out"])
                        for op in script["after"]]
    if script.get("memo_test"):
        out["memo_test"] = janus.query_once("ops:memo_test(Out)")["Out"]
    if script.get("table_test"):
        out["table_test"] = janus.query_once("ops:table_test(Out)")["Out"]
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
