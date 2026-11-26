"""Items on the generated families (PLAN-v3-bench-full §3b): the questions and the task whose difficulty can grow with N.

  .venv/bin/python bench/gen_items.py      # bench/questions/family.json, bench/tasks/A4.json
  .venv/bin/python spikes/v3/shared/reference.py --tasks bench/tasks/A4.json     # A4.keys.json, per N

Both are written per N >= 50 (N 25 has no generated families) under "by_n"; an item id names the same slot at
every N, and each N fills it from its own base. Nothing here is a key: family questions are base questions
(bench/bases/N*.questions.json), keyed by bench/bases/N*.keys.json under "base"; A4's checks are keyed by
reference.py. The family oracle (reference.bench_ref) is used only to pick worked examples whose outcome is
the one the turn is about (a request the exception, not the vendor check, decides).

family.json: 12 questions per N, 2 per pattern; a pattern short of instances at an N is filled from plain
clearance and recorded as such. k = rules and claims on the key's proof path (len(core)).
A4: one programme, P01, present at every N; its content differs per N (gen.py seeds per N).
"""
import datetime, json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "spikes/v3/shared"))
import reference  # noqa: E402

BASES, NS = ROOT / "bench/bases", [50, 100, 200]
PATTERNS = [("limit", "dated limit version"), ("limit", "dated limit version"),
            ("exception", "exception"), ("exception", "exception"),
            ("counter", "counter-exception"), ("counter", "counter-exception"),
            ("dispute", "owner dispute without superiority"), ("dispute", "owner dispute without superiority"),
            ("dispute_sup", "owner dispute with superiority"), ("dispute_sup", "owner dispute with superiority"),
            ("claim", "claim tree"), ("claim", "claim tree")]


def day(d):
    x = datetime.date.fromisoformat(d)
    return f"{x.day} {x.strftime('%B')} {x.year}"


def money(a):
    return f"{a:,}"


def load(n):
    st = BASES / f"N{n:03d}"
    rd = lambda s: json.loads(st.with_suffix(s).read_text()) if s != ".keys.json" else json.loads((BASES / f"N{n:03d}.keys.json").read_text())
    return rd(".params.json"), rd(".questions.json"), rd(".keys.json"), reference.bench_ref(st)


def pattern(q, k, P, R):
    if q["kind"] == "claim":
        return "claim" if q["claim"] in {t["top"]["id"] for t in P["claim_trees"]} else None
    g, code = q["goal"][0], q["goal"][1]
    if g == "programme_limit_ok":
        return "limit"
    if g == "programme_cleared":
        c = R.prog[code]["clearance"]
        if c["exception"] and c["exception"]["id"] in k["core"]: return "exception"
        if c["counter"] and c["counter"]["id"] in k["core"] and k["value"] is True: return "counter"
        return "clearance"
    if g == "capitalised":
        return "dispute_sup" if R.disp[code]["superior"] else "dispute"
    return None


def text(q, R):
    if q["kind"] == "claim":
        t = next(t for t in R.B["claim_trees"] if t["top"]["id"] == q["claim"])
        v = q["asset"].split(":")[1]
        return (f"Was vendor {v} a qualified supplier under supplier list {t['code']} on {day(q['as_of'])}?" if q.get("as_of")
                else f"Is vendor {v} a qualified supplier under supplier list {t['code']}?")
    g, code, r = q["goal"]
    if g == "capitalised":
        return f"Under capitalisation policy {code}, is my request {r} capitalised, or expensed?"
    name = R.prog[code]["name"]
    if g == "programme_limit_ok":
        return f"Is my request {r} within the limit of the {name} programme ({code})?"
    return f"Can request {r} be charged to the {name} programme ({code}), i.e. is it cleared under it?"


def family(n):
    P, Q, K, R = load(n)
    rnd = random.Random(f"family:{n}")
    pool = {}
    for q in Q:
        p = pattern(q, K[q["id"]], P, R)
        if p: pool.setdefault(p, []).append(q)
    mid = lambda q: (lambda d, a: d["for"]["min"] <= a < d["against"]["below"])(R.disp[q["goal"][1]], R.req[q["goal"][2]]["amount"])
    prefer = {   # the first of a pattern's two slots takes the instance that shows the pattern
        "limit": [lambda q: K[q["id"]]["value"] is True, lambda q: K[q["id"]]["value"] is False],
        "dispute": [lambda q: K[q["id"]]["status"] == "CONFLICT", lambda q: K[q["id"]]["status"] == "ANSWER"],
        "dispute_sup": [mid, lambda q: True],
        "claim": [lambda q: len(K[q["id"]]["core"]) > 1 and not q.get("as_of"), lambda q: bool(q.get("as_of"))],
    }
    used, out, seen = set(), [], {}
    for i, (p, label) in enumerate(PATTERNS):
        j = seen.get(p, 0); seen[p] = j + 1
        cands = [q for q in pool.get(p, []) if q["id"] not in used]
        f = prefer.get(p, [lambda q: True] * 2)[j]
        cands = [q for q in cands if f(q)] or cands
        got = p
        if not cands:
            cands, got = [q for q in pool["clearance"] if q["id"] not in used], "clearance"
        q = rnd.choice(cands)
        used.add(q["id"])
        out.append(dict(slot=f"F{i + 1:02d}", pattern=label if got == p else f"plain clearance (no {label} instance left)",
                        base=q["id"], k=len(K[q["id"]]["core"]), text=text(q, R)))
    return out


def pick(R, rows, want):
    """the first request (sorted) for which want(r) holds"""
    return next(r for r in sorted(rows) if want(r))


def a4(n):
    P, _, _, R = load(n)
    p = P["programmes"][0]
    code, name, cat, vs, c = p["code"], p["name"], p["category"], p["versions"], p["clearance"]
    ven = c["exception"]["vendor"]
    req = R.req
    of = lambda v: [r for r, q in req.items() if q["category"] == cat and v["valid_from"] <= q["date"] <= v["valid_to"]]
    lim0 = vs[0]["limit"]
    r1 = pick(R, of(vs[0]), lambda r: req[r]["amount"] <= lim0)
    last = vs[-1]
    # a later request that the first version's limit would judge differently (if the limits differ)
    r2 = pick(R, of(last), lambda r: (lim0 < req[r]["amount"] <= last["limit"]) if last["limit"] > lim0
              else (last["limit"] < req[r]["amount"] <= lim0) if last["limit"] < lim0 else True)
    vreq = [r for r, q in req.items() if q["category"] == cat and q["vendor"] == ven]
    r3 = pick(R, vreq, lambda r: not req[r]["emergency"] and R.limit_ok(code, r) and R.vendor_cleared(r)[0])
    r4 = pick(R, vreq, lambda r: req[r]["emergency"] and R.limit_ok(code, r) and not R.vendor_cleared(r)[0]) if any(
        req[r]["emergency"] and R.limit_ok(code, r) and not R.vendor_cleared(r)[0] for r in vreq) else \
        pick(R, vreq, lambda r: req[r]["emergency"] and R.limit_ok(code, r))
    K1, K2 = R.disp["K01"], R.disp["K02"]
    band = lambda d: lambda r: req[r]["category"] == d["category"] and d["for"]["min"] <= req[r]["amount"] < d["against"]["below"]
    r5, r6 = pick(R, req, band(K1)), pick(R, req, band(K2))
    trees = [t for t in P["claim_trees"] if t["vendor"] == ven]
    cds = [x for x in P["claim_disputes"] if x["vendor"] == ven]
    cats = sorted({d["category"] for d in P["disputes"]})
    excw, ctrw = c["exception"]["id"], c["counter"]["id"]
    vlist = "; ".join(f"{v['id']} from {day(v['valid_from'])} to {day(v['valid_to'])}, limit {money(v['limit'])}" for v in vs)
    who = lambda d: (d["for"]["owner"] if d["superior"] == "for" else d["against"]["owner"])

    turns = [
        dict(n=1, text=f"Build a programme view for the {name} programme ({code}): for a request, which programme limit "
                       f"applies, and is the request within it?",
             example=f"As a worked example, take requests {r1} and {r2}: give the limit that governs each and whether it is within it."),
        dict(n=2, text=f"Extend the view to clearance: which requests can be charged to the {name} programme?",
             example=f"Give the clearance of requests {r3} and {r4}, both from vendor {ven}, and how many {cat} requests "
                     f"from {ven} are cleared under {code} in all."),
        dict(n=3, text="Add capitalisation: is a request capitalised or expensed, and who decides?",
             example=f"Give the outcome for request {r5} under policy K01 and for request {r6} under policy K02, and say "
                     f"whether either policy applies to {code}'s requests."),
        dict(n=4, text=f"Vendor {ven} matters to this programme. Is it a qualified supplier, and what else is claimed about it?",
             example="Name the claims involved, their asserters and their standing today"
                     + (" and before any later claim." if any(t["later"] for t in trees) else ".")),
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
        dict(id="GR6", text=f"K01: {K1['for']['owner']} capitalises {K1['category']} requests from {money(K1['for']['min'])}, "
                            f"{K1['against']['owner']} expenses them under {money(K1['against']['below'])}; no superiority is "
                            f"stated, so {r5} is contested (both sides, with their rules), not a yes or no",
             refs=[K1["for"]["id"], K1["against"]["id"]], turns=[3]),
        dict(id="GR7", text=f"K02: the same kind of disagreement, but {who(K2)}'s rule is stated to prevail, so {r6} is "
                            f"{'capitalised' if K2['superior'] == 'for' else 'expensed'}",
             refs=[K2["for"]["id"], K2["against"]["id"]], turns=[3]),
        dict(id="GR8", text=f"The capitalisation policies cover {', '.join(cats)} requests"
                            + (f"; none covers {cat}, so they do not touch {code}'s requests" if cat not in cats
                               else f"; those on {cat} also cover {code}'s requests"),
             refs=[d["for"]["id"] for d in P["disputes"] if d["code"] in ("K01", "K02")], turns=[3]),
    ]
    checks = [
        dict(id="A4.K1", gr=["GR1"], turn=1, component=f"limit governing {r1}", call=["programme_limit", code, r1]),
        dict(id="A4.K2", gr=["GR1"], turn=1, component=f"limit governing {r2}", call=["programme_limit", code, r2],
             **({"naive": ["programme_limit_first", code]} if last["limit"] != lim0 else {})),
        dict(id="A4.K3", gr=["GR1"], turn=1, component=f"{r2} within the {code} limit", call=["decide", "programme_limit_ok", code, r2]),
        dict(id="A4.K4", gr=["GR3", "GR4"], turn=2, component=f"clearance of {r3} under {code}", call=["decide", "programme_cleared", code, r3]),
        dict(id="A4.K5", gr=["GR5"], turn=2, component=f"clearance of {r4} under {code}", call=["decide", "programme_cleared", code, r4]),
        dict(id="A4.K6", gr=["GR4", "GR5"], turn=2, component=f"{cat} requests from {ven} cleared under {code}",
             call=["cleared_count", code, ven], naive=["cleared_count_no_exception", code, ven]),
        dict(id="A4.K7", gr=["GR6"], turn=3, component=f"{r5} capitalised under K01", call=["decide", "capitalised", "K01", r5]),
        dict(id="A4.K8", gr=["GR7"], turn=3, component=f"{r6} capitalised under K02", call=["decide", "capitalised", "K02", r6]),
    ]
    g = 9
    if trees:
        gold.append(dict(id=f"GR{g}", text=f"Qualification of {ven} (procurement's claim per supplier list) rests on required "
                                            f"insurance and quality claims and a supporting delivery claim, each with its own asserter",
                         refs=[x for t in trees for x in [t["top"]["id"]] + [m["id"] for m in t["members"]]], turns=[4]))
        g += 1
    for t in trees:
        checks.append(dict(id=f"A4.K{len(checks) + 1}", gr=[f"GR{g - 1}"], turn=4, component=f"{ven} qualified under {t['code']} today",
                           call=["claim_standing", t["top"]["id"]]))
        if t["later"]:
            L = t["later"]
            role = next(m["role"] for m in t["members"] if m["id"] == L["target"])
            gold.append(dict(id=f"GR{g}", text=f"{t['code']}: the later claim {L['id']} (same asserter, from {day(L['valid_from'])}) "
                                               f"negates {L['target']}, a {role} sub-claim, and supersedes it: qualification is "
                                               f"{'rebutted' if role == 'required' else 'only qualified'} from that date",
                             refs=[L["id"], L["target"]], turns=[4]))
            g += 1
            checks.append(dict(id=f"A4.K{len(checks) + 1}", gr=[f"GR{g - 1}"], turn=4,
                               component=f"{ven} qualified under {t['code']} the day before {L['id']}",
                               call=["claim_standing", t["top"]["id"]],
                               as_of=(datetime.date.fromisoformat(L["valid_from"]) - datetime.timedelta(days=1)).isoformat()))
    for x in cds:
        sup = x["superiority"]
        gold.append(dict(id=f"GR{g}", text=f"{x['code']}: {x['yes']['asserter']} and {x['no']['asserter']} disagree on {x['pred']} for {ven}; "
                                           + ("legal prevails by the stated authority rule" if sup else "no superiority is stated, so it stays contested"),
                         refs=[x["yes"]["id"], x["no"]["id"]], turns=[4]))
        g += 1
        checks.append(dict(id=f"A4.K{len(checks) + 1}", gr=[f"GR{g - 1}"], turn=4, component=f"{x['pred']} for {ven} ({x['code']})",
                           call=["decide", x["pred"], x["code"], ven]))
    if not trees and not cds:
        gold.append(dict(id=f"GR{g}", text=f"No claim in the base is about {ven}: say so rather than infer qualification", refs=[], turns=[4]))
    return dict(turns=turns, gold=gold, checks=checks)


def main():
    fam = {n: family(n) for n in NS}
    qs = []
    for i in range(len(PATTERNS)):
        slot = fam[NS[0]][i]["slot"]
        qs.append(dict(id=slot, scope=None, by_n={str(n): {k: v for k, v in fam[n][i].items() if k != "slot"} for n in NS}))
    doc = {"source": "GENERATED by bench/gen_items.py from bench/bases/N*.questions.json; do not edit (PLAN-v3-bench-full §3b)",
           "keys": "bench/bases/N*.keys.json under the base question id; never copied here",
           "patterns": [lbl for _, lbl in PATTERNS], "questions": qs}
    (ROOT / "bench/questions/family.json").write_text(json.dumps(doc, indent=1) + "\n")
    task = {"id": "A4", "title": "programme view on the generated families",
            "source": "GENERATED by bench/gen_items.py from bench/bases/N*.params.json; do not edit (PLAN-v3-bench-full §3b)",
            "output": "Per turn, a design: the components, the rules and claims each rests on, the SQL or lookup per component, and caveats.",
            "by_n": {str(n): a4(n) for n in NS}}
    (ROOT / "bench/tasks/A4.json").write_text(json.dumps(task, indent=1) + "\n")
    for n in NS:
        print(f"N{n}: family", [(q["pattern"][:12], q["base"], q["k"]) for q in fam[n]])
        t = task["by_n"][str(n)]
        print(f"N{n}: A4 {len(t['gold'])} gold, {len(t['checks'])} checks")


if __name__ == "__main__":
    main()
