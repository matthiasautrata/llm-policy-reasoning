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
    janus.query_once("ops:load_files_json(J)", {"J": json.dumps(script.get("load", []))})
    load_ms = (time.time() - t0) * 1000
    results = []
    for op in script.get("ops", []):
        r = janus.query_once("ops:run_op(J, Out)", {"J": json.dumps(op)})
        results.append(json.loads(r["Out"]))
    json.dump({"results": results, "load_ms": load_ms}, sys.stdout)


if __name__ == "__main__":
    main()
