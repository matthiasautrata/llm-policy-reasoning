"""Independent check: evaluate the ENGLISH policy (numbered rules in gen.POLICY) in plain Python,
straight from facts.dl, and compare every question's answer with the Soufflé-derived key.

  python scaling/verify.py scaling/worlds/*
"""
import json, pathlib, re, sys

def load(world):
    F = {}
    for m in re.finditer(r'^(\w+)\((.*)\)\.$', (world / "program.dl").read_text(), re.M):
        F.setdefault(m[1], []).append([int(a) if a.isdigit() else a.strip('"') for a in re.findall(r'"[^"]*"|\d+', m[2])])
    return F

def evaluate(F, level):
    parent = {c: p for c, p in F.get("cc_parent", [])}
    anc = lambda c: [] if c not in parent else [parent[c]] + anc(parent[c])            # rule 1
    mgr = {e: m for e, m in F.get("reports", [])}
    chain = lambda e: [] if e not in mgr else [mgr[e]] + chain(mgr[e])                 # rule 2
    booked = {c: b for c, b in F.get("booked", [])}
    cap = {c: k for c, k in F["cap"]}
    ccs = [c for (c,) in F["cc"]]
    total = {c: booked.get(c, 0) + sum(booked.get(d, 0) for d in ccs if c in anc(d)) for c in ccs}   # rule 3
    headroom = {c: cap[c] - total[c] for c in ccs}                                      # rule 4
    over = {c for c in ccs if total[c] > cap[c]}
    emp = {e: (r, c) for e, r, c in F["emp"]}
    limit = {r: l for r, l in F["role_limit"]}
    vstat = {v: s for v, s in F["vendor"]}
    viol = {e for (e,) in F.get("violation", [])}
    emerg = {r for (r,) in F.get("emergency", [])}
    out = {}
    for r, e, a, cat, v in F["req"]:
        charged = [emp[e][1]] + anc(emp[e][1])                                          # rule 5
        breach = any(total[c] + a > cap[c] for c in charged)
        has_appr = any(limit[emp[m][0]] >= a for m in chain(e))                         # rule 6
        vok = vstat[v] == "approved"                                                    # rule 7
        if level and not vok and vstat[v] == "suspended" and r in emerg and not (cat == "capital" and a > 50000):
            vok = True                                                                  # rules 7a, 7b
        denied = level and e in viol                                                    # rule 9
        out[r] = dict(charged=charged, breach=breach, vok=vok, approved=has_appr and not breach and vok and not denied)
    return dict(out=out, headroom=headroom, over=over, chain=chain, emp=emp)

def answer(q, E):
    t, R = q["text"], E["out"]
    ids = re.findall(r"\b(r\d{3}|e\d{3}|company|cc[\d_]+)\b", t)
    if t.startswith("Is request") and t.endswith("approved?"): return R[ids[0]]["approved"]
    if t.startswith("What is the headroom"): return E["headroom"][ids[0]]
    if t.startswith("How many employees have"): return sum(ids[0] in E["chain"](e) for e in E["emp"])
    if t.startswith("Which requests that charge"): return sorted(r for r, x in R.items() if x["approved"] and ids[0] in x["charged"])
    if t == "Which requests breach a cap?": return sorted(r for r, x in R.items() if x["breach"])
    if t == "Which cost centres are over cap?": return sorted(E["over"])
    if t.startswith("Does request"): return R[ids[0]]["vok"]
    if t.startswith("How many requests are approved"): return sum(x["approved"] for x in R.values())
    raise ValueError(t)

bad = 0
for w in map(pathlib.Path, sys.argv[1:]):
    meta = json.loads((w / "world.json").read_text())
    E = evaluate(load(w), meta["level"])
    key = json.loads((w / "answers.json").read_text())
    for q in json.loads((w / "questions.json").read_text()):
        got = answer(q, E)
        if got != key[q["id"]]:
            bad += 1; print("MISMATCH", w.name, q["id"], got, key[q["id"]])
    print(w.name, "ok" if not bad else "")
sys.exit(bool(bad))
