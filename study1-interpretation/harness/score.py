"""Score model replies against keys/keys.json.

Input: JSONL records {"prompt": "p07", "model": "...", "run": "...", "text": "<final reply>"}.
Output: per-scenario CSV + a summary table on stdout.

  python harness/score.py results/runs.jsonl [--csv results/scored.csv]
"""
import csv, json, pathlib, re, sys
from collections import defaultdict

root = pathlib.Path(__file__).resolve().parents[1]
KEYS = json.loads((root / "keys/keys.json").read_text())["keys"]
MANIFEST = json.loads((root / "prompts/manifest.json").read_text())


def parse(text):
    """SCENARIO blocks -> {id: (status, answer)}."""
    out = {}
    for block in re.split(r"SCENARIO:\s*", text or "")[1:]:
        sid = re.match(r"\**\s*(S\d+)", block)
        st = re.search(r"STATUS:\s*\**\s*([A-Z]+)", block)
        an = re.search(r"ANSWER:\s*(.*)", block)
        if sid:
            out[sid[1]] = (st[1] if st else "?", an[1].strip() if an else "")
    return out


def grade(key, got):
    """-> (outcome, correct). outcome in ok | wrong-value | overreach | overcaution | wrong-status | missing."""
    if got is None:
        return "missing", False
    st, ans = got
    if st != key["status"]:
        if key["status"] in ("AMBIGUOUS", "CONFLICT") and st == "ANSWER":
            return "overreach", False
        if key["status"] == "ANSWER" and st in ("AMBIGUOUS", "CONFLICT"):
            return "overcaution", False
        return "wrong-status", False
    if st == "ANSWER":
        a = ans.lower()
        ok = all(re.search(p, a) for p in key.get("all", [])) and not any(re.search(p, a) for p in key.get("none", []))
        return ("ok", True) if ok else ("wrong-value", False)
    return "ok", True


def score(records):
    rows = []
    for r in records:
        keys, got = KEYS[r["prompt"]], parse(r["text"])
        for sid, key in keys.items():
            if key["status"] == "EXCLUDED":
                continue
            outcome, ok = grade(key, got.get(sid))
            g = got.get(sid, ("", ""))
            rows.append(dict(prompt=r["prompt"], arm=arm(r["prompt"]), model=r["model"], run=r["run"],
                             scenario=sid, expected=key["status"], status=g[0], answer=g[1][:120],
                             outcome=outcome, correct=int(ok)))
    return rows


def arm(p):
    m = MANIFEST.get(p) or {"phase": "B", "arm": "owl+shacl (new)"}
    return f'{m["phase"]}:{m["arm"]}'


def summary(rows):
    agg = defaultdict(lambda: defaultdict(int))
    for r in rows:
        a = agg[(r["arm"], r["model"])]
        a["n"] += 1; a["correct"] += r["correct"]; a[r["outcome"]] += 1
    runs = defaultdict(set)
    for r in rows:
        runs[(r["arm"], r["model"])].add(r["run"])
    cols = ["overreach", "overcaution", "wrong-value", "wrong-status", "missing"]
    print(f'{"arm":34} {"model":28} runs  score   ' + " ".join(f"{c[:11]:>11}" for c in cols))
    for (a, m), v in sorted(agg.items()):
        print(f'{a:34} {m.split("/")[-1][:28]:28} {len(runs[(a, m)]):>4}  {v["correct"]:>3}/{v["n"]:<3} ' + " ".join(f"{v[c]:>11}" for c in cols))


if __name__ == "__main__":
    src = pathlib.Path(sys.argv[1])
    rows = score([json.loads(l) for l in src.read_text().splitlines() if l.strip()])
    out = pathlib.Path(sys.argv[sys.argv.index("--csv") + 1]) if "--csv" in sys.argv else src.with_suffix(".scored.csv")
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary(rows)
    print(f"\n{len(rows)} graded answers -> {out}")
