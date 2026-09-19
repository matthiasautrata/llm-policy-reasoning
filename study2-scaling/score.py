"""Score scaling runs: exact match per question, plus F1 for set answers.
  python scaling/score.py results/scaling-pilot-*.jsonl"""
import json, pathlib, sys
from collections import defaultdict
root = pathlib.Path(__file__).resolve().parent
rows = []
for f in sys.argv[1:]:
    for l in open(f):
        r = json.loads(l)
        key = json.loads((root / "worlds" / r["world"] / "answers.json").read_text())
        qs = {q["id"]: q for q in json.loads((root / "worlds" / r["world"] / "questions.json").read_text())}
        for q, k in key.items():
            g = r["answer"].get(q)
            if isinstance(k, list):
                G, K = set(g or []), set(k)
                p = len(G & K) / len(G) if G else float(not K); rc = len(G & K) / len(K) if K else float(not G)
                f1 = 2 * p * rc / (p + rc) if p + rc else 0.0
            else:
                f1 = float(g == k)
            rows.append(dict(world=r["world"], size=r["world"][0], level=r["world"][2:], arm=r["arm"], model=r["model"],
                             q=q, kind=qs[q]["kind"], type=qs[q]["type"], exact=int(g == k if not isinstance(k, list) else set(g or []) == set(k)), f1=round(f1, 3)))
def table(by):
    agg = defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        a = agg[tuple(r[b] for b in by)]; a[0] += 1; a[1] += r["exact"]; a[2] += r["f1"]
    print("  ".join(f"{b:>8}" for b in by), "  exact   meanF1")
    for k, (n, e, f) in sorted(agg.items()):
        print("  ".join(f"{x:>8}" for x in k), f"  {e:>2}/{n:<3} {f / n:6.2f}")
    print()
if __name__ == "__main__":
    table(["model", "arm"]); table(["size", "level", "arm"]); table(["type", "size", "arm"])
    out = pathlib.Path(sys.argv[1]).with_suffix(".scored.jsonl")
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
