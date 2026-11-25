"""V3d throughput: the bench's 200 seeded decides, 1 thread vs 8 threads (`concurrent`, each thread
on its own JDBC connection), after a sequential warm-up of the same 200 in `ops` (JIT). Wall = max
t_end - min t_start. Analog of V3c beam_probes.exs `par`.

  .venv/bin/python spikes/v3/v3d-flix/probes/par.py --backend duckdb
"""
import argparse, json, random, subprocess, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "shared"))
from accept import CFG, ROOT, SLICE  # noqa: E402
from bench import pct  # noqa: E402

CLI = str(pathlib.Path(__file__).parents[1] / "cli")


def session(cfg, warm, lists):
    p = subprocess.run([CLI], input=json.dumps({"config": cfg, "load": [SLICE], "ops": warm, "concurrent": lists}),
                       capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        raise SystemExit(p.stderr[-3000:])
    return json.loads(p.stdout)["concurrent"]


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--backend", default="duckdb")
    a = a.parse_args()
    rng = random.Random(7)
    reqs = [f"r{rng.randrange(1, 100001):06d}" for _ in range(200)]
    ops = [{"op": "decide", "goal": f'[:approved "{r}"]'} for r in reqs]
    out, answers = [], {}
    for n in (1, 8):
        lists = [ops[i::n] for i in range(n)]
        res = session(CFG[a.backend], ops, lists)
        flat = [r for l in res for r in l]
        errs = sum(1 for r in flat if r.get("status") == "ERROR")
        wall = max(r["t_end"] for r in flat) - min(r["t_start"] for r in flat)
        vals = {o["goal"]: r.get("value") for l, rl in zip(lists, res) for o, r in zip(l, rl)}
        answers[n] = vals
        ms = [r["ms"] for r in flat]
        out.append({"threads": n, "wall_ms": wall, "decides_per_s": round(200 / wall * 1000, 1), "errors": errs,
                    "p50": pct(ms, .5), "p95": pct(ms, .95)})
    out.append({"same_answers": answers[1] == answers[8]})
    print(json.dumps({"backend": a.backend, "parallel": out}, indent=1))


if __name__ == "__main__":
    main()
