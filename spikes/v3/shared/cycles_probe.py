"""Re-entry guard probe (PLAN-v3-integrity §3.2): what an engine does with a negative cycle when the
integrity gate is bypassed.

  python spikes/v3/shared/cycles_probe.py --cli spikes/v3/v3a-prolog/cli [--timeout 30] [--out f.json]

For each loop fixture (Y2 even loop, Y3 odd loop under fixtures/integrity/) loads slice + extension +
fixture with INTEGRITY_GATE=off, so the load is admitted, and asks the goal on the loop. A memo
evaluator must end in a named `defeat-cycle` error (the re-entry guard: the result's error names the
goal path) in under 1 s (the op's own ms; wall time includes process start). Without the guard the outcome
was a stack overflow or a timeout.
Prints one line per probe: outcome (guard | answer | crash | timeout), seconds, detail.
"""
import argparse, json, os, pathlib, shlex, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from accept import CFG, SLICE, EXT, FIX, ROOT, answer_fields  # noqa: E402

PROBES = [("Y2", "y2-even-loop.edn", '[:preferred "dyne"]'),
          ("Y3", "y3-odd-loop.edn", '[:trusted "edge"]')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True)
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("--out")
    a = ap.parse_args()
    env = dict(os.environ, INTEGRITY_GATE="off")
    rows = []
    for name, fix, goal in PROBES:
        script = {"config": CFG, "load": [SLICE, EXT, f"{FIX}/{fix}"], "ops": [{"op": "decide", "goal": goal}]}
        t, r = time.time(), {}
        try:
            p = subprocess.run(shlex.split(a.cli), input=json.dumps(script), capture_output=True, text=True,
                               cwd=ROOT, timeout=a.timeout, env=env)
            if p.returncode != 0:
                outcome, got = "crash", (p.stderr.strip().splitlines() or ["?"])[-1][:160]
            else:
                out = json.loads(p.stdout)
                r = (out.get("results") or [{"error": out.get("error")}])[0]
                if "error" in r:
                    outcome = "guard" if "defeat-cycle" in json.dumps(r["error"]) else "error"
                    got = r["error"]
                else:
                    outcome, got = "answer", answer_fields({"kind": "decide"}, r)
        except subprocess.TimeoutExpired:
            outcome, got = "timeout", f">{a.timeout:.0f}s"
        s = time.time() - t
        op_ms = r.get("ms") if outcome in ("guard", "answer", "error") else None
        rows.append(dict(probe=name, goal=goal, outcome=outcome, got=got, s=round(s, 2), op_ms=op_ms,
                         under_1s=(op_ms if op_ms is not None else s * 1000) < 1000))
        print(f"{name} {goal:22} {outcome:8} {s:5.2f}s wall, op {op_ms} ms  {json.dumps(got, default=str)[:220]}", flush=True)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(rows, indent=1, default=str))
    print("guarded", sum(r["outcome"] == "guard" for r in rows), "of", len(rows),
          "| under 1 s", sum(r["under_1s"] for r in rows))


if __name__ == "__main__":
    main()
