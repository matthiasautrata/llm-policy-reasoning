"""Score run records against the keys and write a Markdown report.

  python harness/score.py results/m2-read-L0.jsonl[.gz] [--report results/m2-read-L0.md]

Per record (the key is the world's decided key at the record's layer):
  status_ok   the model's status equals the key's
  correct     status_ok, and for an ANSWER key the value matches exactly (sets also get F1)
  overreach   the key is UNDERDETERMINED and the model gave a value (ANSWER or AMBIGUOUS)
  abstain_ok  lenient: key and model are both abstentions (UNDERDETERMINED or OUT_OF_SCOPE)
  false_abst  the key is ANSWER and the model abstained
  lucky       an overreaching ANSWER whose value equals the decided key at the question's min_layer
              (the model guessed the definition the next layer supplies)
Replies are re-parsed from the raw content, so parser fixes apply to old records.
Unparsed replies count as wrong (status "PARSE"); API errors are left out and counted.
Checks before scoring that every question whose min_layer exceeds the layer is keyed UNDERDETERMINED.
"""
import argparse, collections, gzip, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from harness.read import norm_value, parse      # noqa: E402

ABST = {"UNDERDETERMINED", "OUT_OF_SCOPE"}
ORDER = ["ANSWER", "AMBIGUOUS", "CONFLICT", "UNDERDETERMINED", "OUT_OF_SCOPE", "PARSE"]


def f1(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return 1.0
    tp = len(a & b)
    return 0.0 if not tp else 2 * tp / (len(a) + len(b))


def score(r, key, meta, later):
    p = r["parsed"] = parse(r["content"], r["type"])
    ms = p["status"] or "PARSE"
    ks = key["status"]
    s = {"key": ks, "got": ms, "status_ok": ms == ks, "min_layer": meta["min_layer"]}
    s["overreach"] = ks == "UNDERDETERMINED" and ms in ("ANSWER", "AMBIGUOUS")
    s["abstain_ok"] = ks in ABST and ms in ABST
    s["false_abst"] = ks == "ANSWER" and ms in ABST
    s["value_ok"] = None
    s["f1"] = None
    if ks == "ANSWER" and ms == "ANSWER":
        kv = norm_value(key["value"], r["type"])
        s["value_ok"] = p["value"] == kv
        if r["type"] == "set":
            s["f1"] = f1(p["value"] or [], kv)
    s["alias"] = p["alias"]
    s["lucky"] = None
    if s["overreach"] and ms == "ANSWER" and later and later["status"] == "ANSWER":
        s["lucky"] = p["value"] == norm_value(later["value"], r["type"])
    s["correct"] = s["status_ok"] and (ks != "ANSWER" or bool(s["value_ok"]))
    return s


def pct(n, d):
    return "–" if not d else f"{100 * n / d:.0f}% ({n}/{d})"


def table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    return "\n".join(out)


def summary(group):
    n = len(group)
    und = [s for s in group if s["key"] == "UNDERDETERMINED"]
    ans = [s for s in group if s["key"] == "ANSWER"]
    oos = [s for s in group if s["key"] == "OUT_OF_SCOPE"]
    return [n, pct(sum(s["correct"] for s in group), n),
            pct(sum(s["correct"] for s in ans), len(ans)),
            pct(sum(s["overreach"] for s in und), len(und)),
            pct(sum(bool(s["lucky"]) for s in und), sum(s["lucky"] is not None for s in und)),
            pct(sum(s["abstain_ok"] for s in und + oos), len(und + oos)),
            pct(sum(s["status_ok"] for s in oos), len(oos)),
            pct(sum(s["false_abst"] for s in ans), len(ans)),
            sum(s["got"] == "PARSE" for s in group)]


HEAD = ["n", "correct", "correct on ANSWER keys", "overreach", "overreach = later key", "abstained (lenient)", "OUT_OF_SCOPE exact",
        "false abstention", "unparsed"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--report")
    a = ap.parse_args()

    recs = [json.loads(l) for f in a.runs
            for l in (gzip.open(f, "rt") if f.endswith(".gz") else open(f)).read().splitlines()]
    errors = [r for r in recs if r.get("error")]
    recs = [r for r in recs if not r.get("error")]

    keys, scored = {}, []
    for r in recs:
        w = r["world"]
        if w not in keys:
            k = json.loads((ROOT / "worlds" / w / "keys.json").read_text())
            for qid, m in k["meta"].items():
                for L in range(4):
                    e = k["decided"][qid][f"L{L}"]
                    if m["min_layer"] is not None and L < m["min_layer"] and e["status"] != "UNDERDETERMINED":
                        raise SystemExit(f"{w} {qid} L{L}: below min_layer {m['min_layer']} but keyed {e['status']}")
            keys[w] = k
        k = keys[w]
        m = k["meta"][r["qid"]]
        later = k["decided"][r["qid"]][f"L{m['min_layer']}"] if m["min_layer"] is not None else None
        s = score(r, k["decided"][r["qid"]][f"L{r['layer']}"], m, later)
        scored.append((r, s))

    def by(f):
        g = collections.defaultdict(list)
        for r, s in scored:
            g[f(r, s)].append(s)
        return sorted(g.items(), key=lambda kv: str(kv[0]))

    L = []
    models = sorted({r["model"] for r, _ in scored})
    layers = sorted({r["layer"] for r, _ in scored})
    L.append(f"# Read mode: {', '.join(models)} at layer(s) {', '.join(map(str, layers))}\n")
    cost = sum(r.get("cost") or 0 for r in recs)
    secs = [r.get("seconds") or 0 for r in recs]
    toks = lambda f: sum(r.get(f) or 0 for r in recs)
    L.append(f"{len(recs)} scored records, {len(errors)} API errors left out. Cost ${cost:.4f}; "
             f"prompt tokens {toks('prompt_tokens'):,}, completion tokens {toks('completion_tokens'):,} "
             f"(reasoning {toks('reasoning_tokens'):,}); mean {sum(secs) / max(1, len(secs)):.1f} s per call.")
    prov = collections.Counter(r.get("provider") for r in recs)
    L.append("Providers: " + ", ".join(f"{p} {n}" for p, n in prov.most_common()) + ".")
    L.append(f"Status spelled with an accepted alias (UNDETERMINED): {sum(s['alias'] for _, s in scored)}.")
    fins = collections.Counter(r.get("finish_reason") for r in recs)
    L.append("Finish reasons: " + ", ".join(f"{p} {n}" for p, n in fins.most_common()) + ".\n")
    L.append("Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) "
             "and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met "
             "with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals "
             "the decided key once the question's layer is present.\n")

    for title, f in [("By model and representation", lambda r, s: (r["model"], r["repr"])),
                     ("By model and key's min_layer", lambda r, s: (r["model"], s["min_layer"])),
                     ("By model and world", lambda r, s: (r["model"], r["world"]))]:
        L.append(f"## {title}\n")
        L.append(table([[*kk, *summary(g)] for kk, g in by(f)], ["model", title.split(" and ")[-1], *HEAD]))
        L.append("")

    L.append("## Status confusion (rows: key, columns: model)\n")
    for m in models:
        c = collections.Counter((s["key"], s["got"]) for r, s in scored if r["model"] == m)
        ks = [x for x in ORDER if any(kk == x for kk, _ in c)]
        L.append(f"**{m}**\n")
        L.append(table([[k, *(c[(k, g)] for g in ORDER)] for k in ks], ["key \\ model", *ORDER]))
        L.append("")

    L.append("## By template\n")
    rows = []
    for (m, t), g in by(lambda r, s: (r["model"], r["template"])):
        got = collections.Counter(s["got"] for s in g)
        rows.append([m, t, g[0]["key"], g[0]["min_layer"], pct(sum(s["correct"] for s in g), len(g)),
                     ", ".join(f"{k} {n}" for k, n in got.most_common())])
    L.append(table(rows, ["model", "template", "key", "min_layer", "correct", "model statuses"]))
    L.append("")

    L.append("## Stability across repetitions\n")
    rows = []
    cells = collections.defaultdict(list)
    for r, s in scored:
        cells[(r["model"], r["repr"], r["world"], r["qid"])].append(s["got"])
    for (m, rep), _ in by(lambda r, s: (r["model"], r["repr"])):
        cs = [v for kk, v in cells.items() if kk[:2] == (m, rep) and len(v) > 1]
        rows.append([m, rep, len(cs), pct(sum(len(set(v)) == 1 for v in cs), len(cs))])
    L.append(table(rows, ["model", "repr", "question cells with ≥2 reps", "same status every rep"]))
    L.append("")

    text = "\n".join(L)
    if a.report:
        pathlib.Path(a.report).write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
