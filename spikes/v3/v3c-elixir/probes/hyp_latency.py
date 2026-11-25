"""Hypothesis latency, 50 runs per variant, the op's own `ms` (as PLAN-v3a-fix F1.5). Usage: hyp_latency.py CLI [backend]"""
import json, statistics, subprocess, sys
sys.path.insert(0, "spikes/v3/shared")
import accept as A
cli, backend = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "duckdb")
ext = open(A.EXT).read()
goal = {"op": "decide", "goal": '[:cost_centre_of "e077" ?c]', "as_of": "2026-07-15"}
variants = {
    "Q11 withhold R313 + decide": {"op": "with_hypothesis", "withhold": ["R313"], "ops": [goal]},
    "withhold R313, no ops": {"op": "with_hypothesis", "withhold": ["R313"], "ops": []},
    "add extension.edn + decide": {"op": "with_hypothesis", "add": ext, "ops": [goal]},
    "plain decide (no hypothesis)": goal,
}
ops = [v for v in variants.values() for _ in range(50)]
out = json.loads(subprocess.run([cli], input=json.dumps({"config": A.CFG[backend], "load": [A.SLICE], "ops": ops}),
                                capture_output=True, text=True, check=True).stdout)["results"]
res = {}
for i, name in enumerate(variants):
    ms = sorted(r["ms"] for r in out[i * 50:(i + 1) * 50])
    res[name] = {"p50": round(statistics.median(ms), 3), "p95": round(ms[int(0.95 * 50) - 1], 3)}
print(json.dumps({"backend": backend, "runs": 50, **res}, indent=1))
