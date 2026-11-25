"""Spike v3 performance (latency and SQL statements per op), the same session for any CLI.

  .venv/bin/python spikes/v3/shared/bench.py --cli spikes/v3/v3a-prolog/cli [--n 200]

decide: N `approved` decisions on seeded random requests of the 100k (each a full defeasible
evaluation: approver chain, cap check over ancestors, vendor check, denial, incompatibility), then the
23 questions; p50/p95 from each op's own `ms`, overall and after the first 20 ops (warm).
cold start: wall time of a session that loads slice.edn and runs nothing. memory: max RSS of the bench
session (/usr/bin/time -l, macOS).
"""
import argparse, json, random, re, shlex, statistics, subprocess, sys, time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from accept import CFG, ROOT, SLICE, load, op_for  # noqa: E402


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def run(cli, script):
    t = time.time()
    p = subprocess.run(["/usr/bin/time", "-l", *shlex.split(cli)], input=json.dumps(script),
                       capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        raise SystemExit(p.stderr[-3000:])
    rss = int(re.search(r"(\d+)\s+maximum resident set size", p.stderr).group(1))
    return json.loads(p.stdout), time.time() - t, rss


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--cli", required=True)
    a.add_argument("--n", type=int, default=200)
    a = a.parse_args()
    cfg = CFG
    rng = random.Random(7)
    reqs = [f"r{rng.randrange(1, 100001):06d}" for _ in range(a.n)]
    _, _, Q = load()
    ops = [{"op": "decide", "goal": f'[:approved "{r}"]'} for r in reqs] + [op_for(q) for q in Q]

    _, cold, rss0 = run(a.cli, {"config": cfg, "load": [SLICE], "ops": []})
    out, wall, rss = run(a.cli, {"config": cfg, "load": [SLICE], "ops": ops})
    res = out["results"]
    ms = [r["ms"] for r in res[:a.n]]
    errs = [r for r in res if r.get("status") == "ERROR"]
    vals = [r.get("value") for r in res[:a.n]]
    report = {
        "cli": a.cli, "n": a.n, "errors": len(errs),
        "approved_true": sum(1 for v in vals if v is True),
        "decide_ms": {"p50": pct(ms, .5), "p95": pct(ms, .95), "max": max(ms), "mean": statistics.mean(ms)},
        "decide_ms_warm": {"p50": pct(ms[20:], .5), "p95": pct(ms[20:], .95)},
        "questions_ms": {"p50": pct([r["ms"] for r in res[a.n:]], .5), "p95": pct([r["ms"] for r in res[a.n:]], .95)},
        "sql_per_decide": statistics.mean(len(r["sql_log"]) for r in res[:a.n]),
        "load_ms": out.get("load_ms"), "cold_start_s": round(cold, 2), "session_wall_s": round(wall, 2),
        "max_rss_mb": {"load_only": round(rss0 / 2**20), "bench": round(rss / 2**20)},
    }
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
