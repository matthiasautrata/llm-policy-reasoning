"""Items on the generated families (PLAN-v3-bench-full §3b, §3b′): manager questions stratified by k, and the design
task A4 whose items are the same requests at every N.

  .venv/bin/python bench/gen_items.py      # bench/questions/family.json, bench/tasks/A4.json
  .venv/bin/python spikes/v3/shared/reference.py --tasks bench/tasks/A4.json     # A4.keys.json, per N

Both are written per N under "by_n"; an id names the same slot at every N. Nothing here is a key: family
questions are base questions (bench/bases/N*.questions.json), keyed by bench/bases/N*.keys.json under "base";
A4's checks are keyed by reference.py. The family oracle (reference.bench_ref) picks worked examples by the
outcome the turn is about, never by how an arm answered.

family.json (§3b′): 16 questions per N, 4 per k stratum (k = len(core), the rules and claims on the key's proof
path: 1, 2-3, 4-5, 6+), within a stratum one per outcome (CONFLICT, true, false by absence, false by defeat)
where it has one. A stratum short of instances at an N is filled from the nearest lower one and recorded.
Each question records k and d, the dispute count: the capitalisation disputes with a rule on the key's path.
A4 (§3b′): P01 is seeded apart (gen.py), so its programme, clearance and the requests asked about are the same
at every N; what grows with N is the disputes over P01's category and the chain U01..Um under P01. Requests
for turns 3 and 4 are picked by their outcome at the largest N and asked at every N.
"""
import datetime, json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "spikes/v3/shared"))
import reference  # noqa: E402

BASES, NS = ROOT / "bench/bases", [50, 100, 200]
STRATA = [(1, 1), (2, 3), (4, 5), (6, 99)]
PER = 4
FAMILY_GOALS = ("programme_limit_ok", "programme_cleared", "capitalised")
# How a reply states a decide check's answer in prose (PLAN-v3-bench-full §3e.1), by predicate: [regex, polarity]
# pairs tried in order, a matched span consumed before the next pair, so a negated phrase is read before its word.
SAYS = {
    "limit_ok": [[r"\bnot\s+(?:\w+\s+)?within\b|\bexceed|\bbreach|\boutside\b|\babove\b|(?<!prevails )(?<!prevail )\bover\b|\d\s*>\s*\d", "false"],
                 [r"\bwithin\b|\binside\b|\d\s*(?:≤|<=)\s*\d", "true"]],
    "cleared": [[r"\bnot\s+(?:be\s+)?(?:\w+-)?(?:cleared|clearable|chargeable)\b|\buncleared\b|\bblocked\b", "false"],
                [r"\bcleared\b|\bchargeable\b", "true"]],
    "capitalised": [[r"\bnot\s+(?:be\s+)?capitali[sz](?:ed|able)\b", "false"], [r"\bnot\s+expensed\b", "true"],
                    [r"\bcapitali[sz](?:ed|e)\b", "true"], [r"\bexpensed\b", "false"]],
}


def says(pred):
    return SAYS[next(k for k in SAYS if pred.endswith(k))]


def day(d):
    x = datetime.date.fromisoformat(d)
    return f"{x.day} {x.strftime('%B')} {x.year}"


def money(a):
    return f"{a:,}"


def load(n):
    st = BASES / f"N{n:03d}"
    rd = lambda s: json.loads(st.with_suffix(s).read_text()) if s != ".keys.json" else json.loads((BASES / f"N{n:03d}.keys.json").read_text())
    return rd(".params.json"), rd(".questions.json"), rd(".keys.json"), reference.bench_ref(st)


def outcome(k):
    if "status" not in k: return "claim"
    if k["status"] == "CONFLICT": return "contested"
    return "true" if k["value"] else "false (absence)" if k["qualifier"] else "false (defeat)"


def disputes_on(k, P):
    ids = set(k.get("core") or [])
    return sum(1 for d in P["disputes"] if {d["for"]["id"], d["against"]["id"]} & ids)


def text(q, R):
    if q["kind"] == "claim":
        t = next(t for t in R.B["claim_trees"] if t["top"]["id"] == q["claim"])
        v = q["asset"].split(":")[1]
        return (f"Was vendor {v} a qualified supplier under supplier list {t['code']} on {day(q['as_of'])}?" if q.get("as_of")
                else f"Is vendor {v} a qualified supplier under supplier list {t['code']}?")
    g, r = q["goal"][0], q["goal"][-1]
    if g == "capitalised":
        return f"Is my {q['goal'][1]} request {r} capitalised, or expensed?"
    if g.startswith("u") and g.endswith("_cleared"):
        u = "U" + g[1:3]
        return f"Can request {r} be charged to sub-programme {u} of the {R.prog['P01']['name']} programme (P01), i.e. is it cleared under {u}?"
    code = q["goal"][1]; name = R.prog[code]["name"]
    if g == "programme_limit_ok":
        return f"Is my request {r} within the limit of the {name} programme ({code})?"
    return f"Can request {r} be charged to the {name} programme ({code}), i.e. is it cleared under it?"


def family(n):
    P, Q, K, R = load(n)
    rnd = random.Random(f"family:{n}")
    ok = lambda q: q["kind"] == "claim" and q["claim"] in {t["top"]["id"] for t in P["claim_trees"]} or q["kind"] == "decide" and (
        q["goal"][0] in FAMILY_GOALS or q["goal"][0].startswith("u") and q["goal"][0].endswith("_cleared"))
    Q = [q for q in Q if ok(q)]
    kk = lambda q: len(K[q["id"]].get("core") or [])
    used, out = set(), []
    for s, (lo, hi) in enumerate(STRATA):
        for j in range(PER):
            got, src = None, None
            for t, (a, b) in reversed(list(enumerate(STRATA[:s + 1]))):    # this stratum, then the nearest lower
                pool = [q for q in Q if q["id"] not in used and a <= kk(q) <= b]
                if not pool: continue
                have = {x["outcome"] for x in out if x["_s"] == s}
                fresh = [q for q in pool if outcome(K[q["id"]]) not in have]
                got, src = rnd.choice(sorted(fresh or pool, key=lambda q: q["id"])), t
                break
            if got is None: continue
            used.add(got["id"])
            k = K[got["id"]]
            out.append(dict(_s=s, _q=got, slot=f"F{len(out) + 1:02d}",
                            stratum=f"k {lo}" + (f"-{hi}" if hi != lo and hi < 99 else "+" if hi == 99 else "")
                            + ("" if src == s else f" (filled from k {STRATA[src][0]}" + (f"-{STRATA[src][1]})" if STRATA[src][1] != STRATA[src][0] else ")")),
                            outcome=outcome(k), base=got["id"], k=kk(got), d=disputes_on(k, P), text=text(got, R)))
    return [{x: v for x, v in o.items() if not x.startswith("_")} for o in out]


def pick(rows, want):
    """the first request (sorted) for which want(r) holds"""
    return next(r for r in sorted(rows) if want(r))


def a4(n, picks):
    P, _, _, R = load(n)
    p = P["programmes"][0]
    code, name, cat, vs, c = p["code"], p["name"], p["category"], p["versions"], p["clearance"]
    ven, req = c["exception"]["vendor"], R.req
    r1, r2, r3, r4, r5, r6, r7, r8, r9 = (picks[k] for k in ("r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9"))
    lim0, last = vs[0]["limit"], vs[-1]
    ds = [d for d in P["disputes"] if d["category"] == cat]
    chain, um = P["chain"], P["chain"][-1]
    excw, ctrw = c["exception"]["id"], c["counter"]["id"]
    vlist = "; ".join(f"{v['id']} from {day(v['valid_from'])} to {day(v['valid_to'])}, limit {money(v['limit'])}" for v in vs)
    sup = [(a, b) for a, b in P["superior"] if any(a in (d["for"]["id"], d["against"]["id"]) for d in ds)]
    side = {d[s]["id"]: (d["code"], s, d[s]["owner"]) for d in ds for s in ("for", "against")}
    pol = "; ".join(f"{d['code']}: {d['for']['owner']} capitalises from {money(d['for']['min'])} ({d['for']['id']}), "
                    f"{d['against']['owner']} expenses under {money(d['against']['below'])} ({d['against']['id']})" for d in ds)
    lv = lambda L: f"{L['code']} ({L['base']['id']}: cleared under {L['parent']}" + (f" and capitalised" if L["base"]["capitalised"] else "") + ")"
    turns = [
        dict(n=1, text=f"Build a programme view for the {name} programme ({code}): for a request, which programme limit "
                       f"applies, and is the request within it?",
             example=f"As a worked example, take requests {r1} and {r2}: give the limit that governs each and whether it is within it."),
        dict(n=2, text=f"Extend the view to clearance: which requests can be charged to the {name} programme?",
             example=f"Give the clearance of requests {r3} and {r4}, both from vendor {ven}, and how many {cat} requests "
                     f"from {ven} are cleared under {code} in all."),
        dict(n=3, text=f"Add capitalisation: is a {cat} request, such as one charged to {code}, capitalised or expensed, and who decides?",
             example=f"Give the outcome for requests {r5} and {r6}, with the policies and rules it rests on."),
        dict(n=4, text=f"{code} has sub-programmes, {', '.join(L['code'] for L in chain)}, each one level below the one before. "
                       f"Extend the view to the last of them, {um['code']}: which requests can be charged to it?",
             example=f"Give the clearance of requests {r7}, {r8} and {r9} under {um['code']}, and how many {cat} requests "
                     f"are cleared under {um['code']} in all, and how many are undecided."),
    ]
    gold = [
        dict(id="GR1", text=f"{code}'s limit has {len(vs)} dated versions ({vlist}); the version valid on the request date "
                            f"governs, so {r2} ({day(req[r2]['date'])}, {money(req[r2]['amount'])}) is judged against "
                            f"{money(last['limit'])}" + (f", not {money(lim0)}" if last["limit"] != lim0 else ""),
             refs=[v["id"] for v in vs], turns=[1]),
        dict(id="GR2", text=f"The limit applies to {cat} requests only; other categories are not within it (false, not unknown)",
             refs=[v["id"] for v in vs], turns=[1]),
        dict(id="GR3", text=f"Clearance ({c['base']}, {p['owner']}) needs both the programme limit and the vendor check",
             refs=[c["base"]], turns=[2]),
        dict(id="GR4", text=f"Exception {excw} ({c['exception']['owner']}): a request from {ven} is not cleared, whatever the "
                            f"vendor check says; it prevails over {c['base']}, so {r3} is not cleared",
             refs=[excw, c["base"]], turns=[2]),
        dict(id="GR5", text=f"Exception to the exception {ctrw}: an emergency request from {ven} within the limit is cleared even "
                            f"without the vendor check; it prevails over {excw}, so {r4} is cleared",
             refs=[ctrw, excw], turns=[2]),
        dict(id="GR6", text=(f"1 capitalisation policy covers {cat} requests ({pol}); its two rules both take part: a request "
                             f"in both ranges has a rule on each side, not one owner's answer") if len(ds) == 1 else
                            (f"{len(ds)} capitalisation policies cover {cat} requests ({pol}); they conclude the same thing, "
                             f"so every rule whose body holds for a request takes part, not one policy"),
             refs=[x for d in ds for x in (d["for"]["id"], d["against"]["id"])], turns=[3], contest=len(ds) == 1),
        dict(id="GR7", text=("Stated precedence: " + "; ".join(f"{a} ({side[a][0]} {side[a][1]}) prevails over {b}"
                                                                 + (f" ({side[b][0]} {side[b][1]})" if b in side else "") for a, b in sup)
                             if sup else "No precedence is stated between the capitalisation rules")
                            + "; a rule that expenses is set aside only by a superior rule that capitalises and holds (and the reverse), "
                              "and where no such rule holds the outcome is contested, with both sides and their rules, not a yes or no",
             refs=sorted({x for ab in sup for x in ab}), turns=[3], contest=True),
        dict(id="GR8", text=f"Sub-programme chain: " + ", ".join(lv(L) for L in chain) + f"; a request reaches {um['code']} only "
                            f"through every level, so a contested capitalisation makes the clearance contested from "
                            f"{next((L['code'] for L in chain if L['base']['capitalised']), um['code'])} down, not false",
             refs=[L["base"]["id"] for L in chain], turns=[4], contest=True),
    ]
    ex = [L for L in chain if L["exception"]]
    if ex:
        gold.append(dict(id="GR9", text="From " + ex[0]["code"] + " on, each level has an exception (emergency requests are not cleared) "
                         "and an exception to it (an emergency request up to a stated amount that is cleared under P01 is cleared, "
                         "whatever the level above says): " + "; ".join(f"{L['code']}: {L['exception']['id']} over {L['base']['id']}, "
                         f"{L['counter']['id']} up to {money(L['counter']['max'])} over {L['exception']['id']}" for L in ex),
                         refs=[x for L in ex for x in (L["exception"]["id"], L["counter"]["id"])], turns=[4]))
    gold.append(dict(id=f"GR{len(gold) + 1}", text=f"The count under {um['code']} separates cleared from contested requests; "
                     f"counting what is cleared under {code} (or under any level above) as cleared under {um['code']} is wrong",
                     refs=[um["base"]["id"]], turns=[4]))
    D = lambda *g: ["decide", *g]
    checks = [
        dict(id="A4.K1", subject=r1, gr=["GR1"], turn=1, component=f"limit governing {r1}", call=["programme_limit", code, r1]),
        dict(id="A4.K2", subject=r2, gr=["GR1"], turn=1, component=f"limit governing {r2}", call=["programme_limit", code, r2],
             **({"naive": ["programme_limit_first", code]} if last["limit"] != lim0 else {})),
        dict(id="A4.K3", subject=r2, gr=["GR1"], turn=1, component=f"{r2} within the {code} limit", call=D("programme_limit_ok", code, r2)),
        dict(id="A4.K4", subject=r3, gr=["GR3", "GR4"], turn=2, component=f"clearance of {r3} under {code}", call=D("programme_cleared", code, r3)),
        dict(id="A4.K5", subject=r4, gr=["GR5"], turn=2, component=f"clearance of {r4} under {code}", call=D("programme_cleared", code, r4)),
        dict(id="A4.K6", subject=ven, gr=["GR4", "GR5"], turn=2, component=f"{cat} requests from {ven} cleared under {code}",
             call=["cleared_count", code, ven], naive=["cleared_count_no_exception", code, ven]),
        dict(id="A4.K7", subject=r5, gr=["GR6", "GR7"], turn=3, component=f"{r5} capitalised", call=D("capitalised", cat, r5)),
        dict(id="A4.K8", subject=r6, gr=["GR6", "GR7"], turn=3, component=f"{r6} capitalised", call=D("capitalised", cat, r6)),
        dict(id="A4.K9", subject=r7, gr=["GR8"], turn=4, component=f"clearance of {r7} under {um['code']}", call=D(um["pred"], r7)),
        dict(id="A4.K10", subject=r8, gr=["GR8"], turn=4, component=f"clearance of {r8} under {um['code']}", call=D(um["pred"], r8)),
        dict(id="A4.K11", subject=r9, gr=["GR9" if ex else "GR8"], turn=4, component=f"clearance of {r9} under {um['code']}", call=D(um["pred"], r9)),
        dict(id="A4.K12", subject=um["code"], gr=[gold[-1]["id"]], turn=4, component=f"{cat} requests cleared under {um['code']}",
             call=["chain_count", um["pred"], "cleared"], naive=["chain_count", "programme_cleared", "cleared"]),
        dict(id="A4.K13", subject=um["code"], gr=[gold[-1]["id"]], turn=4, component=f"{cat} requests whose clearance under {um['code']} is contested",
             call=["chain_count", um["pred"], "contested"]),
    ]
    for c in checks:
        if c["call"][0] == "decide":
            c["says"] = says(c["call"][1])
    for g in gold:                 # the keys that decide each reason: every check graded under it (§3e.1); a reason that
        by = [c for c in checks if g["id"] in c["gr"]]     # something is contested is decided by them only where one is
        if not g.pop("contest", False) or any(c["call"][0] == "decide" and R.decide(c["call"][1:])["status"] == "CONFLICT" for c in by):
            g["decided_by"] = [c["id"] for c in by]
        else:                      # contested at this N; else a yes or no reported for them does not test the reason
            g["decided_by"], g["untested_by"] = [], [c["id"] for c in by]
    return dict(turns=turns, gold=gold, checks=checks)


def picks():
    """the requests A4 asks about, the same at every N: turns 1-2 from P01 alone (seeded apart, the same at every N),
    turns 3-4 by their outcome at the largest N"""
    P, _, _, R = load(NS[-1])
    p = P["programmes"][0]
    code, cat, vs, c = p["code"], p["category"], p["versions"], p["clearance"]
    ven, req = c["exception"]["vendor"], R.req
    of = lambda v: [r for r, q in req.items() if q["category"] == cat and v["valid_from"] <= q["date"] <= v["valid_to"]]
    lim0, last = vs[0]["limit"], vs[-1]
    r1 = pick(of(vs[0]), lambda r: req[r]["amount"] <= lim0)
    r2 = pick(of(last), lambda r: (lim0 < req[r]["amount"] <= last["limit"]) if last["limit"] > lim0
              else (last["limit"] < req[r]["amount"] <= lim0) if last["limit"] < lim0 else True)
    vreq = [r for r, q in req.items() if q["category"] == cat and q["vendor"] == ven]
    r3 = pick(vreq, lambda r: not req[r]["emergency"] and R.limit_ok(code, r) and R.vendor_cleared(r)[0])
    r4 = pick(vreq, lambda r: req[r]["emergency"] and R.limit_ok(code, r) and not R.vendor_cleared(r)[0]) if any(
        req[r]["emergency"] and R.limit_ok(code, r) and not R.vendor_cleared(r)[0] for r in vreq) else \
        pick(vreq, lambda r: req[r]["emergency"] and R.limit_ok(code, r))
    um = P["chain"][-1]
    st = lambda g: (lambda k: (k["status"], k["value"], len(k["core"])))(R.decide(g))
    mine = sorted(r for r, q in req.items() if q["category"] == cat and q["vendor"] != ven and r not in (r1, r2))
    cl = [r for r in mine if R.decide(["programme_cleared", code, r])["value"] is True]
    r5 = next(r for r in cl if st(["capitalised", cat, r])[0] == "CONFLICT")         # contested, within the programme
    r6 = next(r for r in mine if st(["capitalised", cat, r])[:2] == ("ANSWER", True))
    cl = [r for r in cl if r not in (r5, r6)]                                        # every turn-3/4 request distinct
    deep = [r for r in cl if not req[r]["emergency"] and st([um["pred"], r])[:2] == ("ANSWER", True)]
    r7 = max(deep, key=lambda r: (st([um["pred"], r])[2], r)) if deep else next(r for r in cl if st([um["pred"], r])[1] is True)
    cl = [r for r in cl if r != r7]
    r8 = next(r for r in cl if not req[r]["emergency"] and st([um["pred"], r])[0] == "CONFLICT")
    r9 = next((r for r in cl if req[r]["emergency"] and st([um["pred"], r])[:2] == ("ANSWER", True)), None) or \
        next(r for r in cl if req[r]["emergency"])
    return dict(r1=r1, r2=r2, r3=r3, r4=r4, r5=r5, r6=r6, r7=r7, r8=r8, r9=r9)


def main():
    fam = {n: family(n) for n in NS}
    m = min(len(f) for f in fam.values())
    qs = [dict(id=fam[NS[0]][i]["slot"], scope=None, by_n={str(n): {k: v for k, v in fam[n][i].items() if k != "slot"} for n in NS})
          for i in range(m)]
    doc = {"source": "GENERATED by bench/gen_items.py from bench/bases/N*.questions.json; do not edit (PLAN-v3-bench-full §3b′)",
           "keys": "bench/bases/N*.keys.json under the base question id; never copied here",
           "strata": [f"k {a}" + (f"-{b}" if b != a and b < 99 else "+" if b == 99 else "") for a, b in STRATA], "questions": qs}
    (ROOT / "bench/questions/family.json").write_text(json.dumps(doc, indent=1) + "\n")
    pk = picks()
    task = {"id": "A4", "title": "programme view on the generated families",
            "source": "GENERATED by bench/gen_items.py from bench/bases/N*.params.json; do not edit (PLAN-v3-bench-full §3b′)",
            "output": "Per turn, a design: the components, the rules and claims each rests on, the SQL or lookup per component, and caveats.",
            "requests": pk, "by_n": {str(n): a4(n, pk) for n in NS}}
    (ROOT / "bench/tasks/A4.json").write_text(json.dumps(task, indent=1) + "\n")
    print("A4 requests", pk)
    for n in NS:
        print(f"N{n}: family", [(q["stratum"], q["outcome"], q["k"], q["d"]) for q in fam[n]])
        t = task["by_n"][str(n)]
        print(f"N{n}: A4 {len(t['gold'])} gold, {len(t['checks'])} checks")


if __name__ == "__main__":
    main()
