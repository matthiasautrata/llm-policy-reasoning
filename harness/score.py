"""Score run records against the keys and write a Markdown report.

  python harness/score.py results/m2-read-L0.jsonl[.gz] [--report results/m2-read-L0.md]
      [--worlds S-s1 M-s1] [--templates Q01 Q11] [--max-rep 1]   (restrict to common cells across runs)

Per record (the key is the world's key at the record's layer and config, decided or open):
  status_ok   the model's status equals the key's
  correct     status_ok, and for an ANSWER key the value matches exactly (sets also get F1)
  overreach   the key is UNDERDETERMINED and the model gave a value (ANSWER or AMBIGUOUS)
  abstain_ok  lenient: key and model are both abstentions (UNDERDETERMINED or OUT_OF_SCOPE)
  false_abst  the key is ANSWER and the model abstained
  readings_ok for an AMBIGUOUS key met with AMBIGUOUS: the model's distinct reading values equal the
              key's (reading names are free text, so only the values are compared); correct requires it
  lucky       an overreaching ANSWER whose value equals the decided key at the question's min_layer
              (the model guessed the definition the next layer supplies)
  noticed     rough keyword heuristic: the reply or the reasoning trace says something is ambiguous,
              undefined or missing (STRICT list; WIDE adds assum-, interpret-, "could mean", "not given",
              "doesn't say"). Reported for overreaching ANSWERs ("noticed but answered") next to the same
              rate on ANSWER keys answered correctly, the control. JSON keys are blanked before matching.
  assumed     assume prompt only: the reply's assumptions list is non-empty
Replies are re-parsed from the raw content, so parser fixes apply to old records.
Unparsed replies count as wrong (status "PARSE"); API errors are left out and counted.
Checks before scoring that every question whose min_layer exceeds the layer is keyed UNDERDETERMINED.
"""
import argparse, collections, gzip, json, pathlib, re, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from harness.read import norm_value, parse      # noqa: E402

ABST = {"UNDERDETERMINED", "OUT_OF_SCOPE"}
ORDER = ["ANSWER", "AMBIGUOUS", "CONFLICT", "UNDERDETERMINED", "OUT_OF_SCOPE", "PARSE"]
STRICT = r"ambigu|not defined|undefined|no definition|not specified|unspecified|unclear|does(?: not|n't) define|no rule"
NOTICE = {"strict": re.compile(STRICT, re.I),
          "wide": re.compile(STRICT + r"|assum|interpret|could mean|missing|not stated|not given|does(?: not|n't) (?:say|specify)", re.I)}
JSON_KEYS = re.compile(r'"(?:missing|assumptions)"\s*:|\bmissing(?: field)?\s*[:=]?\s*null\b', re.I)


def noticed(text, kind):
    return bool(NOTICE[kind].search(JSON_KEYS.sub(" ", text or "")))


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
    s["readings_ok"] = None
    if ks == "AMBIGUOUS" and ms == "AMBIGUOUS":
        kv = sorted({json.dumps(norm_value(v, r["type"])) for v in key["readings"].values()})
        s["readings_ok"] = p.get("reading_values") == kv
    s["correct"] = s["status_ok"] and (ks != "ANSWER" or bool(s["value_ok"])) and (ks != "AMBIGUOUS" or bool(s["readings_ok"]))
    s["config"] = r.get("cfg", "decided")
    s["prompt"] = r.get("prompt", "base")
    s["noticed_reply"] = noticed(r["content"], "strict")
    for kind in NOTICE:
        s[f"noticed_{kind}"] = noticed(r["content"] + "\n" + (r.get("reasoning") or ""), kind)
    s["assumptions"] = p.get("assumptions")         # None: field absent (base prompt, or not given)
    s["assumed"] = bool(s["assumptions"])
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
    amb = [s for s in group if s["key"] == "AMBIGUOUS"]
    return [n, pct(sum(s["correct"] for s in group), n),
            pct(sum(s["correct"] for s in ans), len(ans)),
            pct(sum(s["status_ok"] for s in amb), len(amb)),
            pct(sum(bool(s["readings_ok"]) for s in amb), len(amb)),
            pct(sum(s["overreach"] for s in und), len(und)),
            pct(sum(bool(s["lucky"]) for s in und), sum(s["lucky"] is not None for s in und)),
            pct(sum(s["abstain_ok"] for s in und + oos), len(und + oos)),
            pct(sum(s["status_ok"] for s in oos), len(oos)),
            pct(sum(s["false_abst"] for s in ans), len(ans)),
            sum(s["got"] == "PARSE" for s in group)]


HEAD = ["n", "correct", "correct on ANSWER keys", "AMBIGUOUS seen", "AMBIGUOUS readings right", "overreach", "overreach = later key", "abstained (lenient)", "OUT_OF_SCOPE exact",
        "false abstention", "unparsed"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--report")
    ap.add_argument("--worlds", nargs="*")
    ap.add_argument("--templates", nargs="*")
    ap.add_argument("--max-rep", type=int, help="keep repetitions 0..MAX_REP only")
    a = ap.parse_args()

    recs = [json.loads(l) for f in a.runs
            for l in (gzip.open(f, "rt") if f.endswith(".gz") else open(f)).read().splitlines()]
    errors = [r for r in recs if r.get("error")]
    recs = [r for r in recs if not r.get("error")]
    keep = lambda r: ((not a.worlds or r["world"] in a.worlds) and (not a.templates or r["template"] in a.templates)
                      and (a.max_rep is None or r["rep"] <= a.max_rep))
    recs, errors = [r for r in recs if keep(r)], [r for r in errors if keep(r)]

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
        s = score(r, k[r.get("cfg", "decided")][r["qid"]][f"L{r['layer']}"], m, later)
        s["side"] = None
        ke = k[r.get("cfg", "decided")][r["qid"]][f"L{r['layer']}"]
        if s["key"] == "CONFLICT" and s["got"] == "AMBIGUOUS" and ke.get("sides") is not None:
            s["side"] = "both" if r["parsed"].get("reading_values") == sorted(
                {json.dumps(norm_value(v, r["type"])) for v in ke["sides"]}) else "ambiguous-other"
        if s["key"] == "CONFLICT" and s["got"] == "ANSWER":
            top = k["decided"][r["qid"]]["L3"]
            s["side"] = "resolved" if top["status"] == "ANSWER" and r["parsed"]["value"] == norm_value(top["value"], r["type"]) else "other"
        scored.append((r, s))
    scored_s = {id(r): s for r, s in scored}

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

    lc = lambda r, s: (r["model"], f"L{r['layer']}", s["config"], s["prompt"])
    LC = ["model", "layer", "config", "prompt"]
    for title, f in [("By representation", lambda r, s: (*lc(r, s), r["repr"])),
                     ("By key's min_layer", lambda r, s: (*lc(r, s), s["min_layer"])),
                     ("By world", lambda r, s: (*lc(r, s), r["world"]))]:
        L.append(f"## {title}\n")
        L.append(table([[*kk, *summary(g)] for kk, g in by(f)], [*LC, title.split(" ")[-1], *HEAD]))
        L.append("")

    L.append("## Noticed but answered\n")
    L.append("Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning "
             "trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and "
             "wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered "
             "correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty "
             "assumptions list, on overreaches and on the control; absent = the list was left out.\n")
    rows = []
    for kk, g in by(lambda r, s: (*lc(r, s), r["repr"])):
        ov = [s for s in g if s["overreach"] and s["got"] == "ANSWER"]
        ctl = [s for s in g if s["key"] == "ANSWER" and s["correct"]]
        row = [*kk, len(ov)]
        for kind in ("strict", "wide", "reply"):
            f = "noticed_reply" if kind == "reply" else f"noticed_{kind}"
            row += [pct(sum(s[f] for s in ov), len(ov)), pct(sum(s[f] for s in ctl), len(ctl))]
        if kk[3] == "base":
            row += ["–", "–", "–"]
        else:
            row += [pct(sum(s["assumed"] for s in ov), len(ov)), pct(sum(s["assumed"] for s in ctl), len(ctl)),
                    sum(s["assumptions"] is None for s in g)]
        rows.append(row)
    L.append(table(rows, [*LC, "repr", "overreaching ANSWERs", "noticed (strict)", "control (strict)",
                          "noticed (wide)", "control (wide)", "in reply", "control (reply)",
                          "assumptions stated", "control (assumptions)", "assumptions absent"]))
    L.append("")

    # H1: the definitions a question needs turn overreach at the layer below into answers at its own layer.
    steps = sorted({(r["layer"], s["config"]) for r, s in scored if s["prompt"] == "base"})
    for ml in sorted({s["min_layer"] for _, s in scored if s["min_layer"]}):
        if not any(l == ml for l, _ in steps) or not any(l < ml for l, _ in steps):
            continue
        L.append(f"## Step at layer {ml}: questions with min_layer {ml}, by layer shown\n")
        L.append("Correct at each layer (below min_layer the key is UNDERDETERMINED, so correct means abstaining; "
                 "lenient: OUT_OF_SCOPE counts as abstaining), and the status mix.\n")
        rows = []
        for (m, rep), _ in by(lambda r, s: (r["model"], r["repr"])):
            for l, c in steps:
                g = [s for r, s in scored if r["model"] == m and r["repr"] == rep and r["layer"] == l
                     and s["config"] == c and s["prompt"] == "base" and s["min_layer"] == ml]
                if not g:
                    continue
                ok = sum(s["correct"] or (s["key"] == "UNDERDETERMINED" and s["abstain_ok"]) for s in g)
                got = collections.Counter(s["got"] for s in g)
                rows.append([m, rep, f"L{l}", c, len(g), pct(ok, len(g)),
                             ", ".join(f"{k} {n}" for k, n in got.most_common())])
        L.append(table(rows, ["model", "repr", "layer", "config", "n", "correct (lenient)", "model statuses"]))
        L.append("(base prompt only.)")
        L.append("")

    para = {t["id"]: t["paraphrase_of"] for t in yaml.safe_load((ROOT / "questions/bank.yaml").read_text())["templates"]
            if t.get("paraphrase_of")}
    tmpls = {r["template"] for r, _ in scored}
    if any(t in tmpls and src in tmpls for t, src in para.items()):
        L.append("## Paraphrases: same instances, one wording changed\n")
        L.append("A paraphrase template asks the instances of its source template with different wording. "
                 "Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer "
                 "(for Q11/Q17 at L0: the roll-up reading).\n")
        rows = []
        for t, src in sorted(para.items()):
            for kk, g in by(lambda r, s: (*lc(r, s), r["template"])):
                if kk[-1] not in (src, t):
                    continue
                und = [s for s in g if s["key"] == "UNDERDETERMINED"]
                got = collections.Counter(s["got"] for s in g)
                rows.append([*kk, len(g), pct(sum(s["correct"] for s in g), len(g)),
                             pct(sum(bool(s["lucky"]) for s in und), sum(s["lucky"] is not None for s in und)),
                             ", ".join(f"{k} {n}" for k, n in got.most_common())])
        L.append(table(rows, [*LC, "template", "n", "correct", "overreach = later key", "model statuses"]))
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
    for (*kk, t), g in by(lambda r, s: (*lc(r, s), r["template"])):
        got = collections.Counter(s["got"] for s in g)
        kst = collections.Counter(s["key"] for s in g)
        rows.append([*kk, t, ", ".join(f"{k} {n}" for k, n in kst.most_common()), g[0]["min_layer"],
                     pct(sum(s["correct"] for s in g), len(g)), ", ".join(f"{k} {n}" for k, n in got.most_common())])
    L.append(table(rows, [*LC, "template", "keys", "min_layer", "correct", "model statuses"]))
    L.append("")

    if any(s["key"] == "CONFLICT" for _, s in scored):
        L.append("## CONFLICT keys\n")
        L.append("Keys where the material holds both sides of a disagreement and nothing at the layer says which "
                 "prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides "
                 "(the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. "
                 "An ANSWER picks a side: resolved = the value the next layer's resolution rule gives "
                 "(L3 decided key), other = any other value.\n")
        rows = []
        for kk, g in by(lambda r, s: (*lc(r, s), r["repr"])):
            g = [s for s in g if s["key"] == "CONFLICT"]
            if g:
                got = collections.Counter(s["got"] for s in g)
                rows.append([*kk, len(g), pct(got["CONFLICT"], len(g)), pct(sum(s["side"] == "both" for s in g), len(g)),
                             pct(len(g) - got["ANSWER"], len(g)), sum(s["side"] == "resolved" for s in g),
                             sum(s["side"] == "other" for s in g), ", ".join(f"{k} {n}" for k, n in got.most_common())])
        L.append(table(rows, [*LC, "repr", "n", "CONFLICT", "AMBIGUOUS = both sides", "no side picked",
                              "ANSWER = resolved", "ANSWER = other", "model statuses"]))
        L.append("")

    ex = [(r, s) for r, s in scored if "rules" in (r.get("parsed") or {}) and r["qid"] in keys[r["world"]].get("why", {})]
    if ex:
        L.append("## Explanations (explain prompt, graded against the why/2 tree)\n")
        L.append("Only replies whose key and answer are both ANSWER true (why/2 justifies true answers only). "
                 "Core: the rules of the tree's rule nodes; an explanation must name them. Support: the rules behind "
                 "the tree's closed-world negations, aggregates and if-then-else conditions; an explanation may name "
                 "them. Ids are compared without a reading suffix (R104b = R104). Recall = share of core named; "
                 "precision = share of named rules that are in core or support; exact = recall 1 and nothing outside "
                 "core and support.\n")
        bare = lambda i: re.sub(r"[a-z]$", "", i)
        rec = []
        for r, s in ex:
            w = keys[r["world"]]["why"][r["qid"]]
            got = {bare(i) for i in r["parsed"]["rules"]}
            core, ok = set(w["core"]), set(w["core"]) | set(w["support"])
            sc = dict(correct=s["key"] == "ANSWER" and r["parsed"].get("status") == "ANSWER" and r["parsed"].get("value") is True,
                      recall=len(got & core) / len(core), prec=len(got & ok) / len(got) if got else None,
                      n=len(got), core=core, got=got)
            sc["full"] = sc["recall"] == 1
            sc["clean"] = got <= ok
            rec.append((r, sc))
        rows = []
        g = collections.defaultdict(list)
        for r, sc in rec:
            g[(*lc(r, scored_s[id(r)]), r["repr"])].append(sc)
        for kk, v in sorted(g.items(), key=lambda kv: str(kv[0])):
            c = [x for x in v if x["correct"]]
            ps = [x["prec"] for x in c if x["prec"] is not None]
            mean = lambda xs: f"{sum(xs) / len(xs):.2f}" if xs else "-"
            rows.append([*kk, len(v), len(c), mean([x["recall"] for x in c]), pct(sum(x["full"] for x in c), len(c)),
                         mean(ps), pct(sum(x["clean"] for x in c), len(c)), pct(sum(x["full"] and x["clean"] for x in c), len(c)),
                         sum(x["n"] == 0 for x in c), mean([x["n"] for x in c])])
        L.append(table(rows, [*LC, "repr", "n", "ANSWER true", "core recall", "full recall", "precision",
                              "nothing outside", "exact", "empty list", "mean ids named"]))
        L.append("")
        rr = {x["id"]: x for x in yaml.safe_load((ROOT / "rules/rules.yaml").read_text())["rules"]}
        cls = collections.defaultdict(lambda: [0, 0])
        for r, sc in rec:
            if sc["correct"]:
                for i in sc["core"]:
                    k2 = (rr[i]["layer"], rr[i]["class"], rr[i]["conservative"])
                    cls[k2][0] += 1; cls[k2][1] += i in sc["got"]
        L.append("Core recall per rule class (correct replies, all representations): a needed rule of the class, named or not. "
                 "H4 predicts conservative rules (rearranging what is asserted) are left unnamed more often.\n")
        L.append(table([[*k2, n, pct(h, n)] for k2, (n, h) in sorted(cls.items(), key=lambda kv: str(kv[0]))],
                       ["layer", "class", "conservative", "needed", "named"]))
        L.append("")
        miss = collections.Counter(i for _, sc in rec if sc["correct"] for i in sc["core"] - sc["got"])
        extra = collections.Counter(i for r, sc in rec if sc["correct"]
                                    for i in sc["got"] - sc["core"] - set(keys[r["world"]]["why"][r["qid"]]["support"]))
        L.append("Most often missed core rules: " + (", ".join(f"{i} {n}" for i, n in miss.most_common(10)) or "none") + ".")
        L.append("Most often named outside core and support: " + (", ".join(f"{i} {n}" for i, n in extra.most_common(10)) or "none") + ".\n")

    L.append("## Stability across repetitions\n")
    rows = []
    cells = collections.defaultdict(list)
    for r, s in scored:
        cells[(*lc(r, s), r["repr"], r["world"], r["qid"])].append(s["got"])
    for kk0, _ in by(lambda r, s: (*lc(r, s), r["repr"])):
        cs = [v for kk, v in cells.items() if kk[:len(kk0)] == kk0 and len(v) > 1]
        rows.append([*kk0, len(cs), pct(sum(len(set(v)) == 1 for v in cs), len(cs))])
    L.append(table(rows, [*LC, "repr", "question cells with ≥2 reps", "same status every rep"]))
    L.append("")

    text = "\n".join(L)
    if a.report:
        pathlib.Path(a.report).write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
