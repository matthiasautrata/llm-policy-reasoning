"""Ask each cycle question (Q30-Q39) in its own session, with a timeout (PLAN-v3-cycles §4).

  python spikes/v3/shared/cycles_probe.py --cli spikes/v3/v3b-clojure/cli [--timeout 30] [--out f.json] [--backend postgres]

Loads slice + extension + cycles.edn, as check 7 does, but bypasses the model check: the point is
to see what the engine itself does with a negative cycle (answer, wrong answer, error, loop).
Prints one line per question: outcome vs keys["cycles"].
"""
import argparse, json, pathlib, shlex, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reference import load  # noqa: E402
from accept import CFG, SLICE, EXT, CYC, ROOT, op_for, unwrap, answer_fields  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True)
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("--out")
    ap.add_argument("--backend", default="duckdb")
    a = ap.parse_args()
    _, _, _, _, QC = load(cycles=True)
    K = json.loads((HERE / "keys.json").read_text())["cycles"]
    rows = []
    for q in QC:
        script = {"config": CFG[a.backend], "load": [SLICE, EXT, CYC], "ops": [op_for(q)]}
        t = time.time()
        try:
            p = subprocess.run(shlex.split(a.cli), input=json.dumps(script), capture_output=True, text=True,
                               cwd=ROOT, timeout=a.timeout)
            if p.returncode != 0:
                outcome, got = "crash", (p.stderr.strip().splitlines() or ["?"])[-1][:160]
            else:
                r = unwrap(q, json.loads(p.stdout)["results"][0])
                if "error" in r:
                    outcome, got = "error", str(r["error"])[:160]
                else:
                    f = answer_fields(q, r)
                    want = {k: K[q["id"]].get(k) for k in f}
                    outcome, got = ("match" if f == want else "wrong"), f
        except subprocess.TimeoutExpired:
            outcome, got = "timeout", f">{a.timeout:.0f}s"
        rows.append(dict(id=q["id"], outcome=outcome, got=got, want={k: K[q["id"]].get(k) for k in ("status", "value", "sides")},
                         s=round(time.time() - t, 1)))
        print(f"{q['id']} {outcome:8} {time.time() - t:5.1f}s  got {got}  want {rows[-1]['want']}", flush=True)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(rows, indent=1, default=str))
    print("matched", sum(r["outcome"] == "match" for r in rows), "of", len(rows))


if __name__ == "__main__":
    main()
