"""Score arm records (PLAN-v3-bench §6): manager answers against the keys, analyst sessions by checks and judge.

  .venv/bin/python bench/score.py bench/results/b1.jsonl [--report bench/results/b1.md]
  .venv/bin/python bench/score.py bench/results/b1.jsonl --judge --budget 2.00   # submit the Batch; again to collect
  .venv/bin/python bench/score.py bench/results/b1.jsonl --export bench/grading     # 10 sessions for hand grading

Manager (mechanical), per question: status; value for ANSWER (lists as sets, a one-element list as its element);
sides for CONFLICT, strict (the same set of id sets) and tolerant (each key side inside its own reported side, no
reported side holding ids of two key sides: extra ids allowed, sides not merged or swapped); qualifier (the
"qualified" flag against the key's qualifier, which every decide key states, null when none); for a claim, standing
and defeater; for a term, its status and candidates. correct = status, value, strict sides and qualifier
(benchmark-design §2; PLAN-v3-bench-full §3b′); "tolerant" is the same with tolerant sides.
Analyst: each check is searched for mechanically when its value is a number or an id: "reported" (in that turn's
reply), "naive" (only the known wrong value is), "computed" (only in that turn's tool results), "absent". Gold
reasons are graded by the judge (bench/judge_rubric.md; an OpenAI model via the Batch API, a family not under test) as covered / missed / wrong; the
mechanical checks are also graded by it, which gives a mechanical-vs-judge agreement for free. Rule ids cited
per gold reason are counted mechanically.
Further measures: cross-question consistency (pairs of manager questions whose answers must agree whatever they
are), silent interpretation (an undefined or ambiguous term answered as decided), inlining (T's own SQL over the
tables the rules govern), cost and tokens per correct answer / covered reason.
Judge agreement: bench/grading/grades.json, once Matthias fills it, against the judge's grades; and the judge
against itself when a second judging exists (--judge --judge-out <grades>.2.jsonl, PLAN-v3-bench-full §3b).
Cells are reported per item set: core (the slice's, at every N), family (F*, on the generated families, with a
table by k) and A4 (PLAN-v3-bench-full §3b).
"""
import argparse, collections, json, pathlib, re, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "bench")]
import run as B                                   # noqa: E402
from harness import openai_batch                  # noqa: E402
from harness.read import _last_json               # noqa: E402

RUBRIC = ROOT / "bench/judge_rubric.md"
IDS = re.compile(r"(?<![\w.])((?:R|G|C|H)\d+(?:\.\d+)*)(?![\w])")
# pairs of manager questions whose answers must agree, whatever the answers are
CONSISTENT = [("M01", "M02", "headroom = cap - booked total (cc0009)"),
              ("M08", "M50", "purchase order follows approval (r000001)"),
              ("M09", "M51", "purchase order follows approval (r000005)"),
              ("M03", "M05", "r000004 (10 July) is governed by July's manager limit")]
CAP_CC0009 = 5572000          # cc.cap of cc0009 (DuckDB); headroom 1,857,000 + booked 3,715,000
GOVERNED = re.compile(r"role_limit_version|vendor_status|\bcap\b|booked|violation|WITH\s+RECURSIVE", re.I)


# ---------------------------------------------------------------- manager

def norm(v):
    if isinstance(v, list):
        s = sorted({json.dumps(norm(x)) for x in v})
        return json.loads(s[0]) if len(s) == 1 else s
    if isinstance(v, bool) or v is None:
        return v
    if isinstance(v, (int, float)):
        return int(v) if float(v).is_integer() else v
    t = str(v).strip().lower()
    if t in ("true", "yes"): return True
    if t in ("false", "no"): return False
    n = re.sub(r"[,_\s'’€$]", "", t)
    return int(n) if re.fullmatch(r"-?\d+", n) else t


def sides(x):
    return {frozenset(str(i).strip() for i in s) for s in x} if isinstance(x, list) and all(isinstance(s, list) for s in x) else None


def sides_tolerant(got, want):
    """each key side inside one reported side, a different one per key side, no reported side holding ids of two key sides"""
    g, w = sides(got), sides(want)
    if g is None or w is None:
        return g == w
    home = {}
    for s in w:
        hit = [x for x in g if s <= x]
        if len(hit) != 1 or hit[0] in home.values():
            return False
        home[s] = hit[0]
    return all(not (home[s] & o) for s in w for o in w if o != s)


def score_manager(rec):
    key, a = B.manager_key(B.item(rec["item"], rec["n"])), rec.get("answer") or {}
    o = {"parsed": bool(a)}
    if "standing" in key:
        o.update(type="claim", status_ok=a.get("standing") == key["standing"],
                 value_ok=(a.get("defeater") or None) == key["defeater"])
        o["correct"] = o["tolerant"] = o["status_ok"] and o["value_ok"]
    elif "candidates" in key:
        want = {c.split(":", 1)[1].replace("_", " ") for c in key["candidates"]}
        got = {str(c).strip().lower().replace("_", " ") for c in a.get("candidates") or []}
        o.update(type="term", status_ok=a.get("term") == key["status"], value_ok=got == want)
        o["correct"] = o["tolerant"] = o["status_ok"] and o["value_ok"]
    else:
        if "qualifier" not in key:           # a missing field is never read as "not qualified" (§3b′)
            raise KeyError(f"key of {rec['item']} at N {rec['n']} states no qualifier")
        st = str(a.get("status", "")).upper()
        con = key["status"] == "CONFLICT"
        o.update(type="decide", status_ok=st == key["status"],
                 value_ok=key["status"] != "ANSWER" or norm(a.get("value")) == norm(key.get("value")),
                 sides_ok=not con or sides(a.get("sides")) == sides(key["sides"]),
                 sides_tol=not con or sides_tolerant(a.get("sides"), key["sides"]),
                 qualifier_ok=bool(a.get("qualified")) == (key["qualifier"] is not None))
        o["correct"] = o["status_ok"] and o["value_ok"] and o["sides_ok"] and o["qualifier_ok"]
        o["tolerant"] = o["status_ok"] and o["value_ok"] and o["sides_tol"] and o["qualifier_ok"]
        o["silent"] = key["status"] in ("UNDERDETERMINED",) and st == "ANSWER"
    if o["type"] == "term":
        o["silent"] = key["status"] == "several" and a.get("term") == "concept"
    return o


def consistency(recs):
    """per (arm, model, N): how many CONSISTENT pairs agree"""
    by = collections.defaultdict(dict)
    for r in recs:
        if r["kind"] == "manager" and not r["error"]:
            by[(arm(r), r["model"], r["n"], r["rep"])][r["item"]] = r.get("answer") or {}
    out = collections.defaultdict(lambda: [0, 0])
    for k, ans in by.items():
        for x, y, _ in CONSISTENT:
            if x in ans and y in ans:
                a, b = ans[x], ans[y]
                if x == "M01":
                    ok = norm(b.get("value")) == (CAP_CC0009 - norm(a.get("value")) if isinstance(norm(a.get("value")), int) else None)
                else:
                    ok = (str(a.get("status")).upper(), norm(a.get("value"))) == (str(b.get("status")).upper(), norm(b.get("value")))
                out[k[:3]][0] += ok
                out[k[:3]][1] += 1
    return out


# ---------------------------------------------------------------- analyst, mechanical

def patterns(v):
    """regexes for a checkable value; None if the value is not a number or an id"""
    if isinstance(v, dict):
        v = v.get("value")
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        d = str(abs(v))
        groups = [d[max(0, i - 3):i] for i in range(len(d), 0, -3)][::-1]
        sep = r"[,\s.'’ ]?"
        p = [r"(?<![\d.,])" + sep.join(groups) + r"(?![\d]|[.,]\d)"]
        if v % 1000 == 0 and v >= 1000:
            p.append(rf"(?<![\d.,]){v // 1000}\s?[kK]\b")
        return [re.compile(x) for x in p]
    if isinstance(v, str) and re.fullmatch(r"[a-z]{1,3}\d{3,}", v):
        return [re.compile(rf"\b{v}\b")]
    return None


CONTESTED = re.compile(r"contest|conflict|disputed", re.I)


def contested(v):
    return isinstance(v, dict) and v.get("status") == "CONFLICT"


def found(pats, text):
    return bool(pats) and any(p.search(text) for p in pats)


def score_checks(rec):
    task, keys = B.item(rec["item"], rec["n"]), B.task_keys(rec["item"], rec["n"])
    text = {t["turn"]: t["content"] for t in rec["turns"]}
    tools = collections.defaultdict(str)
    for t in rec["tools"]:
        tools[t["turn"]] += t["result"] + "\n"
    out = {}
    for c in task["checks"]:
        k = keys[c["id"]]
        pe, pn = patterns(k["value"]), patterns(k["naive"]) if "naive" in k else None
        if pe is None:
            out[c["id"]] = "judge"
            continue
        s = text.get(c["turn"], "")
        got = found(pe, s)
        if got and contested(k["value"]):     # a contested value counts only on a line that says so (rubric)
            got = any(found(pe, line) and CONTESTED.search(line) for line in s.splitlines())
            if not got:
                out[c["id"]] = "naive"         # given as a plain figure: the rubric's "contested result as yes or no"
                continue
        out[c["id"]] = ("reported" if got else "naive" if found(pn, s) else
                        "computed" if found(pe, tools[c["turn"]]) else "absent")
    return out


def cited(rec):
    """per gold reason: its refs (rules and claims) cited in any reply up to its last turn"""
    task = B.item(rec["item"], rec["n"])
    out = {}
    for g in task["gold"]:
        refs = {r for r in g["refs"] if IDS.fullmatch(r)}
        said = set(IDS.findall(" ".join(t["content"] for t in rec["turns"] if t["turn"] <= max(g["turns"]))))
        out[g["id"]] = (len(refs & said), len(refs))
    return out


def inlining(rec):
    qs = [t for t in rec["tools"] if t["name"] == "sql"]
    gov = [t for t in qs if GOVERNED.search(json.dumps(t["args"]))]
    return len(gov), len(qs)


# ---------------------------------------------------------------- judge

def judge_messages(rec):
    task, keys = B.item(rec["item"], rec["n"]), B.task_keys(rec["item"], rec["n"])
    parts = ["# Task\n"]
    for t in task["turns"]:
        parts.append(f"Turn {t['n']}: {t['text']} {t['example']}")
    parts.append("\n# Gold reasons\n")
    parts += [f"- {g['id']} (turns {', '.join(map(str, g['turns']))}; refs {', '.join(g['refs'])}): {g['text']}" for g in task["gold"]]
    parts.append("\n# Checks\n")
    for c in task["checks"]:
        k = keys[c["id"]]
        parts.append(f"- {c['id']} (turn {c['turn']}): {c['component']}: expected {json.dumps(k['value'])}"
                     + (f"; naive (wrong) {json.dumps(k['naive'])}" if "naive" in k else ""))
    parts.append("\n# The assistant's replies\n")
    for t in rec["turns"]:
        c = t["content"]
        parts.append(f"## Turn {t['turn']}\n\n" + (c if len(c) <= 16000 else c[:16000] + "\n[reply truncated]"))
    return [{"role": "system", "content": RUBRIC.read_text()}, {"role": "user", "content": "\n".join(parts)}]


def stub_judge(rec):
    """grades from the mechanical checks; every reason covered (tests only)"""
    mech = score_checks(rec)
    o = {"status": "graded", "reasons": [{"id": g["id"], "grade": "covered", "evidence": ""} for g in B.item(rec["item"], rec["n"])["gold"]],
         "checks": [{"id": k, "grade": {"reported": "reported", "naive": "wrong"}.get(v, "absent")} for k, v in mech.items()]}
    return {"content": json.dumps(o), "cost": 0.0, "model_served": "stub:judge", "provider": "stub",
            "prompt_tokens": 0, "completion_tokens": 0, "seconds": 0.0}


JUDGE_MAX_TOKENS = 16000     # a reasoning judge spends part of it before the JSON
JUDGE_REASONING = "medium"   # without reasoning_effort gpt-6.2-sol does not reason; low barely does (HISTORY 11;
                             # medium chosen by Matthias 2026-11-26)


def _write(out, rec):
    with pathlib.Path(out).open("a") as f:
        f.write(json.dumps(rec) + "\n")


def _judge_rec(of, model, res, reasoning=None):
    rec = {"of": of, "model": model, "reasoning_effort": reasoning, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if "error" in res:
        return dict(rec, error=res["error"], cost=0.0)
    rec.update({k: res.get(k) for k in ("model_served", "provider", "prompt_tokens", "completion_tokens",
                                        "reasoning_tokens", "cached_tokens", "cost", "seconds", "finish_reason")},
               content=res["content"], grades=_last_json(res["content"]), error=None)
    if not rec["grades"]:
        rec["error"] = "unparsed"
    return rec


def judge(recs, out, model, budget, reasoning=JUDGE_REASONING):
    """Grade the analyst sessions not yet graded. stub:judge grades at once; openai@<id> goes through the Batch
    API: the first call submits (reserving the batch's maximum cost against --budget, which counts the judge's
    files only: the judge is paid from OpenAI credits, not the OpenRouter cap), later calls collect.
    -> "done", "pending" or "budget"."""
    out, state = pathlib.Path(out), pathlib.Path(str(out) + ".batch.json")
    done = {r["of"] for r in map(json.loads, out.read_text().splitlines()) if not r.get("error")} if out.exists() else set()
    if state.exists():
        st = json.loads(state.read_text())
        b = openai_batch.status(st["id"])
        print(f"judge batch {st['id']}: {b['status']} {json.dumps(b.get('request_counts'))}")
        if b["status"] not in ("completed", "failed", "expired", "cancelled"):
            return "pending"
        got = openai_batch.results(b) if b["status"] in ("completed", "expired", "cancelled") else {}
        for cid, of in st["requests"].items():
            _write(out, _judge_rec(of, st["model"], got.get(cid, {"error": f"batch {b['status']}: no result"}), st.get("reasoning")))
        state.rename(str(state) + f".{st['id']}.done")
        return "done"
    todo = [r for r in recs if r["kind"] == "analyst" and not r["error"] and json.dumps(B.cell(r)) not in done]
    spent = B.spent_in(out)
    print(f"judge: {len(todo)} sessions to grade; judge spent ${spent:.4f} of ${budget:.2f}")
    if not todo:
        return "done"
    if model.startswith("stub:"):
        for r in todo:
            _write(out, _judge_rec(json.dumps(B.cell(r)), model, stub_judge(r)))
        return "done"
    e, m = B.endpoint_of(model)
    if e != "openai":
        raise SystemExit(f"the judge runs on the OpenAI Batch API (openai@<id>), not {model}")
    reqs = {f"j{i:04d}": r for i, r in enumerate(todo)}
    held = sum(B.max_cost(model, judge_messages(r), None, JUDGE_MAX_TOKENS) for r in reqs.values()) / 2
    if spent + held > budget:
        print(f"judge batch could cost up to ${held:.4f}; with ${spent:.4f} spent that exceeds ${budget:.2f}: not submitted")
        return "budget"
    b = openai_batch.submit(openai_batch.lines([(c, judge_messages(r)) for c, r in reqs.items()], m, JUDGE_MAX_TOKENS, reasoning))
    state.write_text(json.dumps({"id": b["id"], "model": model, "reasoning": reasoning, "held": held, "submitted": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                 "requests": {c: json.dumps(B.cell(r)) for c, r in reqs.items()}}, indent=1) + "\n")
    print(f"judge batch {b['id']} submitted: {len(reqs)} sessions, at most ${held:.4f}")
    return "pending"


def judged(path):
    g = {}
    if path and pathlib.Path(path).exists():
        for r in map(json.loads, pathlib.Path(path).read_text().splitlines()):
            if not r.get("error") and r.get("grades"):
                g[r["of"]] = r["grades"]
    return g


# ---------------------------------------------------------------- export for hand grading

def export(recs, outdir, k=10):
    """k analyst sessions, stratified by arm and N (round robin over the strata, then over models and tasks)"""
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    strata = collections.defaultdict(list)
    for r in sorted((r for r in recs if r["kind"] == "analyst" and not r["error"]), key=lambda r: (r["item"], r["model"], r["rep"])):
        strata[(r["arm"], r["n"])].append(r)
    for s in strata.values():      # alternate models and tasks within a stratum
        s.sort(key=lambda r: (r["rep"], (B.TASKS.index(r["item"]) + B.MODELS.index(r["model"]) if r["model"] in B.MODELS else 0) % 3, r["model"]))
    pick, i = [], 0
    keys = sorted(strata)
    while len(pick) < k and any(strata.values()):
        s = strata[keys[i % len(keys)]]
        if s:
            pick.append(s.pop(0))
        i += 1
    sheet = {}
    for j, r in enumerate(pick, 1):
        sid = f"S{j:02d}"
        task = B.item(r["item"], r["n"])
        md = [f"# {sid}: task {r['item']} ({task['title']})\n",
              "Graded blind: the arm, model and N are in `index.json`, not here.\n"]
        for t, rep in zip(task["turns"], r["turns"]):
            md.append(f"## Turn {t['n']}\n\n> {t['text']} {t['example']}\n\n{rep['content']}\n")
        md.append("## Gold reasons\n")
        md += [f"- **{g['id']}** (turns {', '.join(map(str, g['turns']))}): {g['text']}" for g in task["gold"]]
        (outdir / f"{sid}.md").write_text("\n".join(md) + "\n")
        sheet[sid] = {"cell": B.cell(r), "grades": {g["id"]: None for g in task["gold"]}}
    (outdir / "index.json").write_text(json.dumps({s: v["cell"] for s, v in sheet.items()}, indent=1) + "\n")
    g = outdir / "grades.json"
    if not g.exists():
        g.write_text(json.dumps({s: v["grades"] for s, v in sheet.items()}, indent=1) + "\n")
    print(f"exported {len(pick)} sessions to {outdir}")


def agreement(gradedir, jg):
    g = pathlib.Path(gradedir) / "grades.json"
    if not g.exists():
        return None
    human, idx = json.loads(g.read_text()), json.loads((pathlib.Path(gradedir) / "index.json").read_text())
    pairs = []
    for sid, grades in human.items():
        j = {x["id"]: x["grade"] for x in (jg.get(json.dumps(idx[sid])) or {}).get("reasons", [])}
        pairs += [(h, j.get(gid)) for gid, h in grades.items() if h]
    return kappa(pairs)


def self_agreement(jg, jg2):
    """two judgings of the same sessions: per gold reason, the same grade?"""
    pairs = []
    for of, g in jg.items():
        if of in jg2:
            b = {x["id"]: x["grade"] for x in jg2[of].get("reasons", [])}
            pairs += [(x["grade"], b.get(x["id"])) for x in g.get("reasons", [])]
    return kappa(pairs)


def kappa(pairs):
    if not pairs:
        return None
    po = sum(a == b for a, b in pairs) / len(pairs)
    cats = ["covered", "missed", "wrong"]
    pe = sum((sum(a == c for a, _ in pairs) / len(pairs)) * (sum(b == c for _, b in pairs) / len(pairs)) for c in cats)
    return {"n": len(pairs), "agreement": po, "kappa": (po - pe) / (1 - pe) if pe < 1 else 1.0}


# ---------------------------------------------------------------- report

def group(iid):
    """the item set: the slice's (core, at every N) or one on the generated families (§3b)"""
    return "family" if iid.startswith("F") else "A4" if iid == "A4" else "core"


def grades_files(results, *also):
    """every grades file of a results file (<stem>.judge*.jsonl beside it), and any given elsewhere"""
    fs = set(map(str, pathlib.Path(results).parent.glob(pathlib.Path(results).stem + ".judge*.jsonl"))) if results else set()
    return sorted(fs | {str(f) for f in also if f and pathlib.Path(f).exists()})


def report(recs, jpath, gradedir, jpath2=None, results=None):
    jg, jg2 = judged(jpath), judged(jpath2)
    L = []
    cells = collections.defaultdict(lambda: collections.Counter())
    for r in recs:
        k = (arm(r), r["model"], r["n"], group(r["item"]))
        c = cells[k]
        c["empty"] += sum(1 for x in r["turns"] if (x.get("forced_final") or not x.get("tool_limit"))   # pre-§1.4 records:
                          and not (x["content"] or "").strip())                                     # limit turns not final
        c["cost"] += r["cost"]; c["tokens"] += r["prompt_tokens"] + r["completion_tokens"]; c["seconds"] += r["seconds"]
        if r["error"]:
            c["errors"] += 1
            continue
        if r["kind"] == "manager":
            s = score_manager(r)
            c["m"] += 1; c["m_correct"] += s["correct"]; c["m_tol"] += s["tolerant"]; c["m_status"] += s["status_ok"]
            c["m_parsed"] += s["parsed"]
            c["m_silent"] += s.get("silent", False)
            if s["type"] == "decide":
                c["m_qual"] += s["qualifier_ok"]; c["m_qual_n"] += 1
                if B.manager_key(B.item(r["item"], r["n"]))["status"] == "CONFLICT":
                    c["m_con"] += 1; c["m_sides"] += s["sides_ok"]; c["m_sides_tol"] += s["sides_tol"]
            c["m_cost"] += r["cost"]
        else:
            c["a"] += 1; c["a_cost"] += r["cost"]
            for v in score_checks(r).values():
                c["k_" + v] += 1
            j = jg.get(json.dumps(B.cell(r)))
            for x in (j or {}).get("reasons", []):
                c["gr_" + x["grade"]] += 1
            for x in (jg2.get(json.dumps(B.cell(r))) or {}).get("reasons", []):
                c["gr2_" + x["grade"]] += 1
            c["a_judged"] += bool(j)
            for got, n in cited(r).values():
                c["cite"] += got; c["cite_n"] += n
            if r["arm"] == "T":
                g, n = inlining(r); c["inl"] += g; c["sql"] += n; c["inl_sessions"] += g > 0
    L.append("| arm | model | N | items | manager correct (strict; tolerant sides) | status | qualifier | sides strict / tolerant (CONFLICT keys) | silent | analyst checks reported / naive / computed / absent | gold covered / missed / wrong | refs cited | T inlining (sessions; SQL) | cost | $ per correct manager | $ per covered reason | empty replies | errors |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in sorted(cells):
        c = cells[k]
        per_m = f"{c['m_cost'] / c['m_correct']:.4f}" if c["m_correct"] else "–"
        per_a = f"{c['a_cost'] / c['gr_covered']:.4f}" if c["gr_covered"] else "–"
        inl = f"{c['inl_sessions']}; {c['inl']}/{c['sql']}" if k[0] == "T" else "–"
        g2 = f"; 2nd {c['gr2_covered']} / {c['gr2_missed']} / {c['gr2_wrong']}" if jg2 else ""
        L.append(f"| {k[0]} | {k[1].split('/')[-1]} | {k[2]} | {k[3]} | {c['m_correct']}/{c['m']}; {c['m_tol']} | {c['m_status']}/{c['m']} | "
                 f"{c['m_qual']}/{c['m_qual_n']} | {c['m_sides']} / {c['m_sides_tol']} of {c['m_con']} | {c['m_silent']} | {c['k_reported']} / {c['k_naive']} / {c['k_computed']} / {c['k_absent']} "
                 f"(judge {c['k_judge']}) | {c['gr_covered']} / {c['gr_missed']} / {c['gr_wrong']} ({c['a_judged']}/{c['a']} judged{g2}) | "
                 f"{c['cite']}/{c['cite_n']} | {inl} | {c['cost']:.4f} | {per_m} | {per_a} | {c['empty']} | {c['errors']} |")
    kt = k_table(recs)
    if kt:
        L.append("\n" + kt)
    L.append("\n" + limit_table(recs))
    L.append("\nConsistency (manager pairs that must agree): " + "; ".join(
        f"{a} {m.split('/')[-1]} N{n} {ok}/{tot}" for (a, m, n), (ok, tot) in sorted(consistency(recs).items())))
    # mechanical vs judge on the mechanically checkable checks
    agree = tot = 0
    for r in recs:
        j = jg.get(json.dumps(B.cell(r))) if r["kind"] == "analyst" else None
        if j:
            jc = {x["id"]: x["grade"] for x in j.get("checks", [])}
            for cid, v in score_checks(r).items():
                if v != "judge" and cid in jc:
                    tot += 1
                    agree += {"reported": "reported", "naive": "wrong"}.get(v, "absent") == jc[cid]
    if tot:
        L.append(f"\nMechanical checks vs judge: {agree}/{tot} agree.")
    sa = self_agreement(jg, jg2) if jg2 else None
    if sa:
        L.append(f"\nJudge vs itself (a second judging, {jpath2}): {sa['agreement']:.2f} agreement, kappa {sa['kappa']:.2f} "
                 f"over {sa['n']} reasons.")
    ag = agreement(gradedir, jg) if gradedir else None
    L.append(f"\nJudge vs hand grading: {ag['agreement']:.2f} agreement, kappa {ag['kappa']:.2f} over {ag['n']} reasons."
             if ag else "\nJudge vs hand grading: not graded yet (bench/grading/grades.json).")
    gf = grades_files(results, jpath, jpath2)
    L.append(f"\nTotal cost of the arms: ${sum(r['cost'] for r in recs):.4f} over {len(recs)} cells; judge "
             f"${sum(B.spent_in(f) for f in gf):.4f} (OpenAI Batch) over every grades file: "
             + (", ".join(f"{pathlib.Path(f).name} ${B.spent_in(f):.4f}" for f in gf) or "none") + ".")
    return "\n".join(L)


def arm(r):
    """T-eval: T before the design tools (the pilot; no rules / summary), reported apart (PLAN-v3-bench-full §2.3)."""
    return "T-eval" if r["arm"] == "T" and "rules" not in r.get("config", {}).get("t_tools", ()) else r["arm"]


def k_table(recs):
    """family questions (§3b): manager correct by k, the rules and claims on the key's proof path"""
    c = collections.defaultdict(lambda: [0, 0, 0])
    for r in recs:
        if r["kind"] == "manager" and not r["error"] and group(r["item"]) == "family":
            x = c[(arm(r), r["model"], r["n"], B.item(r["item"], r["n"])["k"])]
            s = score_manager(r); x[0] += s["correct"]; x[1] += 1; x[2] += s["tolerant"]
    if not c:
        return ""
    ks = sorted({k[3] for k in c})
    L = ["Family questions, manager correct by k (rules and claims on the proof path), strict; tolerant sides:", "",
         "| arm | model | N | " + " | ".join(f"k = {k}" for k in ks) + " |", "|---|---|---|" + "---|" * len(ks)]
    for a, m, n in sorted({k[:3] for k in c}):
        L.append(f"| {a} | {m.split('/')[-1]} | {n} | " + " | ".join(
            (lambda x: f"{x[0]}/{x[1]}; {x[2]}" if x[1] else "–")(c.get((a, m, n, k), [0, 0, 0])) for k in ks) + " |")
    return "\n".join(L)


def limit_table(recs):
    """PLAN-v3-bench-full §2.4: one call bound for every arm; the cells that reach it are their own outcome, by arm."""
    c = collections.defaultdict(collections.Counter)
    for r in recs:
        if r["error"]: continue
        x = c[(arm(r), r["kind"], r["model"], r["n"])]
        hit = [t for t in r["turns"] if t.get("tool_limit")]
        x["cells"] += 1; x["turns"] += len(r["turns"]); x["hit_turns"] += len(hit); x["hit_cells"] += bool(hit)
        if r["kind"] == "manager" and hit:
            x["hit_correct"] += score_manager(r)["correct"]
    L = ["Call limit (a turn closed by the forced final answer), by arm:", "",
         "| arm | kind | model | N | cells at the limit | turns at the limit | manager correct among them |", "|---|---|---|---|---|---|---|"]
    for k in sorted(c):
        x = c[k]
        L.append(f"| {k[0]} | {k[1]} | {k[2].split('/')[-1]} | {k[3]} | {x['hit_cells']}/{x['cells']} | {x['hit_turns']}/{x['turns']} | "
                 + (f"{x['hit_correct']}/{x['hit_cells']} |" if k[1] == "manager" else "– |"))
    return "\n".join(L)


def load(path):
    return [json.loads(l) for l in pathlib.Path(path).read_text().splitlines() if l.strip()]


def main():
    openai_batch.openrouter.load_env()                 # first: refuses a .env that git does not ignore
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--judge-model", default=B.JUDGE)
    ap.add_argument("--judge-out")
    ap.add_argument("--judge-second", help="a second judging of the same sessions, for the judge's agreement with itself "
                                           "(default <grades>.2.jsonl if it exists)")
    ap.add_argument("--judge-reasoning", default=JUDGE_REASONING, choices=["low", "medium", "high", "xhigh"],
                    help="reasoning_effort; grades go to <results>.judge-<effort>.jsonl (low: <results>.judge.jsonl, as the pilot)")
    ap.add_argument("--budget", type=float, default=2.0, help="USD cap on the judge's spend (OpenAI credits; its files only)")
    ap.add_argument("--export")
    ap.add_argument("--grading", default=str(ROOT / "bench/grading"))
    ap.add_argument("--report")
    a = ap.parse_args()
    recs = load(a.results)
    tag = "" if a.judge_reasoning == "low" else f"-{a.judge_reasoning}"
    jpath = a.judge_out or str(pathlib.Path(a.results).with_suffix(f".judge{tag}.jsonl"))
    if a.judge:
        r = judge(recs, jpath, a.judge_model, a.budget, a.judge_reasoning)
        if r != "done":
            sys.exit(1 if r == "budget" else 3)
    if a.export:
        export(recs, a.export)
        return
    j2 = a.judge_second or (str(pathlib.Path(jpath).with_suffix(".2.jsonl")) if pathlib.Path(jpath).with_suffix(".2.jsonl").exists() else None)
    txt = report(recs, jpath, a.grading, j2, a.results)
    print(txt)
    if a.report:
        pathlib.Path(a.report).write_text(txt + "\n")


if __name__ == "__main__":
    main()
