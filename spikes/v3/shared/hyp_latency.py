"""Hypothesis latency through the CLI contract, for any engine (PLAN-v3-cycles §3 "measure hypothesis latency").
  python spikes/v3/shared/hyp_latency.py --cli spikes/v3/v3e-clingo/cli [--backend duckdb] [--n 30]
For Q10 (withhold R313) and Q38 (withhold RY23): p50/p95 of the base decide's `ms` and of the whole
with_hypothesis op's `ms` (n each, one session, slice + extension + cycles)."""
import argparse, json, shlex, statistics, subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from accept import CFG, SLICE, EXT, CYC, ROOT  # noqa: E402

CASES = {"Q10": ('[:cost_centre_of "e077" ?c]', ["R313"]), "Q38": ('[:preferred "dyne"]', ["RY23"])}
ap = argparse.ArgumentParser(); ap.add_argument("--cli", required=True); ap.add_argument("--backend", default="duckdb")
ap.add_argument("--n", type=int, default=30); a = ap.parse_args()
ops = []
for q, (g, wh) in CASES.items():
    d = {"op": "decide", "goal": g, "as_of": "2026-07-15"}
    ops += [d] * a.n + [{"op": "with_hypothesis", "withhold": wh, "ops": [d]}] * a.n
p = subprocess.run(shlex.split(a.cli), input=json.dumps({"config": CFG[a.backend], "load": [SLICE, EXT, CYC], "ops": ops}),
                   capture_output=True, text=True, cwd=ROOT)
R = json.loads(p.stdout)["results"]
pc = lambda xs: {"p50": round(statistics.median(xs), 2), "p95": round(sorted(xs)[int(0.95 * len(xs)) - 1], 2)}
out, i = {"cli": a.cli, "backend": a.backend, "n": a.n}, 0
for q in CASES:
    base, hyp = R[i:i + a.n], R[i + a.n:i + 2 * a.n]; i += 2 * a.n
    out[q] = {"base": pc([r["ms"] for r in base]), "hypothesis": pc([r["ms"] for r in hyp]),
              "answers": [base[0].get("status"), hyp[0]["results"][0].get("status")]}
print(json.dumps(out))
