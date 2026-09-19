"""Scaling-test generator.

  python scaling/gen.py --depth 3 --branch 3 --analysts 3 --level 2 --seed 1 --out scaling/worlds/M-L2-s1

A world = a cost-centre tree of the given depth/branching, one manager per centre, analysts in
the leaves, requests, vendors, budgets. --level 0 = monotone policy with one negation (cap breach);
--level 2 = adds an exception (emergency vendor waiver), an exception to it (big capital), and a
deny rule that overrides approval. The same policy is emitted as Datalog and as English; questions
and keys come from Soufflé. Writes: facts.dl, program.dl, prompt-{text,datalog,tool}.txt,
questions.json, answers.json, ask (tool-arm oracle).
"""
import argparse, json, pathlib, random, re, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

HERE = pathlib.Path(__file__).resolve().parent
LIMIT = {"vp": 500000, "director": 100000, "senior_manager": 50000, "manager": 25000, "analyst": 5000}
AMOUNTS = [4000, 9000, 12000, 20000, 30000, 45000, 60000, 90000, 120000]
CATS = ["software", "hardware", "services", "capital"]
VENDORS = {"acme": "approved", "bolt": "suspended", "cog": "approved", "dyne": "suspended", "edge": "approved"}

POLICY = {0: """\
POLICY

1. Cost centres form a tree. The ancestors of a cost centre are its parent, its parent's parent, and so on.
2. An employee's reporting chain is their manager, their manager's manager, and so on. It does not include the employee.
3. The booked total of a cost centre is its own booked amount (zero if none) plus the booked amounts of all its descendants. Requests never count towards booked totals.
4. The headroom of a cost centre is its cap minus its booked total. A cost centre is over cap if its booked total exceeds its cap.
5. A request charges its requester's cost centre and every ancestor of that cost centre. A request breaches a cap if, for any cost centre it charges, that centre's booked total plus the request amount exceeds that centre's cap.
6. A request has an approver if someone in the requester's reporting chain has a role limit at least equal to the request amount.
7. A request passes the vendor check if its vendor's status is approved.
8. A request is approved if and only if it has an approver, breaches no cap, and passes the vendor check.
""", 2: None}
POLICY[2] = POLICY[0].replace(
    "7. A request passes the vendor check if its vendor's status is approved.\n",
    "7. A request passes the vendor check if its vendor's status is approved.\n"
    "7a. Exception to 7: an emergency request also passes the vendor check when its vendor is suspended.\n"
    "7b. Exception to 7a: 7a does not apply to a capital request whose amount is over 50000.\n").replace(
    "8. A request is approved if and only if it has an approver, breaches no cap, and passes the vendor check.\n",
    "8. A request is approved if and only if it has an approver, breaches no cap, passes the vendor check, and is not denied.\n"
    "9. A request is denied if its requester has a recorded policy violation. Denial overrides everything else: a denied request is never approved.\n")

FORMAT = """\
OUTPUT FORMAT -- reply with one JSON object and nothing else. Keys are the question ids.
Values: yes/no -> true or false; number -> integer; list -> JSON array of ids (order irrelevant, [] if none).
"""


def build(depth, branch, analysts, level, seed, req_ratio=0.8):
    rnd = random.Random(seed)
    cc, parent, lvl = [], {}, {}
    def mk(c, p, l):
        cc.append(c); lvl[c] = l
        if p: parent[c] = p
        if l < depth:
            for i in range(branch):
                mk(f"{c}_{i + 1}" if p else f"cc{i + 1}", c, l + 1)
    mk("company", None, 0)
    emps, reports, mgr = [], {}, {}
    n = 0
    for c in cc:
        role = "vp" if lvl[c] == 0 else "director" if lvl[c] == 1 else "manager" if lvl[c] == depth else "senior_manager"
        e = f"e{n:03d}"; n += 1; emps.append((e, role, c)); mgr[c] = e
        if c in parent: reports[e] = mgr[parent[c]]
    for c in cc:
        if lvl[c] == depth:
            for _ in range(analysts):
                e = f"e{n:03d}"; n += 1; emps.append((e, "analyst", c)); reports[e] = mgr[c]
    # budgets: leaves book 40k-140k, some internal centres book a little; caps set around the booked total
    booked = {c: rnd.randrange(40, 141) * 1000 for c in cc if lvl[c] == depth}
    for c in cc:
        if lvl[c] < depth and rnd.random() < 0.3:
            booked[c] = rnd.randrange(5, 40) * 1000
    total = {}
    for c in reversed(cc):
        total[c] = booked.get(c, 0) + sum(total[k] for k in cc if parent.get(k) == c)
    factors = lambda c: [1.2, 1.4] if lvl[c] == 0 else [1.05, 1.15, 1.3, 1.5] if lvl[c] < depth else [0.97, 1.03, 1.1, 1.2, 1.4, 1.6]
    cap = {c: int(total[c] * rnd.choice(factors(c)) // 1000 * 1000) for c in cc}
    staff = [e for e in emps if e[1] != "vp"]
    reqs = []
    for i in range(max(8, int(len(emps) * req_ratio))):
        e = rnd.choice(staff)[0]
        reqs.append((f"r{i + 1:03d}", e, rnd.choice(AMOUNTS), rnd.choice(CATS), rnd.choice(list(VENDORS))))
    violation = sorted(rnd.sample([e[0] for e in staff], max(1, len(staff) // 10))) if level else []
    emergency = sorted(r[0] for r in reqs if rnd.random() < 0.25) if level else []
    return dict(cc=cc, parent=parent, lvl=lvl, emps=emps, reports=reports, booked=booked, cap=cap,
                reqs=reqs, violation=violation, emergency=emergency, level=level, depth=depth)


def facts_dl(w):
    L = [f'cc("{c}").' for c in w["cc"]] + [f'cc_parent("{c}","{p}").' for c, p in w["parent"].items()]
    L += [f'emp("{e}","{r}","{c}").' for e, r, c in w["emps"]] + [f'reports("{e}","{m}").' for e, m in w["reports"].items()]
    L += [f'role_limit("{r}",{l}).' for r, l in LIMIT.items()] + [f'vendor("{v}","{s}").' for v, s in VENDORS.items()]
    L += [f'req("{r}","{e}",{a},"{k}","{v}").' for r, e, a, k, v in w["reqs"]]
    L += [f'booked("{c}",{b}).' for c, b in w["booked"].items()] + [f'cap("{c}",{k}).' for c, k in w["cap"].items()]
    L += [f'violation("{e}").' for e in w["violation"]] + [f'emergency("{r}").' for r in w["emergency"]]
    return "\n".join(L) + "\n"


def facts_text(w):
    L = ["DATA", "", "Cost centres (id: parent; booked; cap):"]
    L += [f"  {c}: {w['parent'].get(c, '-')}; booked {w['booked'].get(c, 0)}; cap {w['cap'][c]}" for c in w["cc"]]
    L += ["", "Employees (id: role; cost centre; manager):"]
    L += [f"  {e}: {r}; {c}; {w['reports'].get(e, '-')}" for e, r, c in w["emps"]]
    L += ["", "Role limits: " + "; ".join(f"{r} {l}" for r, l in LIMIT.items())]
    L += ["Vendor status: " + "; ".join(f"{v} {s}" for v, s in VENDORS.items())]
    L += ["", "Requests (id: requester; amount; category; vendor):"]
    L += [f"  {r}: {e}; {a}; {k}; {v}" for r, e, a, k, v in w["reqs"]]
    if w["level"]:
        L += ["", "Employees with a recorded policy violation: " + ", ".join(w["violation"]),
              "Emergency requests: " + ", ".join(w["emergency"])]
    return "\n".join(L) + "\n"


def rules_dl(level):
    src = (HERE / "rules.dl").read_text().splitlines()
    return "\n".join(l.split("//L2")[0].rstrip() for l in src if level == 2 or "//L2" not in l) + "\n"


def souffle(program, rels):
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, "p.dl").write_text(program + "".join(f".output {r}\n" for r in rels))
        subprocess.run(["souffle", "-w", "-D", d, f"{d}/p.dl"], check=True, capture_output=True)
        return {r: [l.split("\t") for l in pathlib.Path(d, f"{r}.csv").read_text().splitlines() if l] for r in rels}


def questions(w, D, seed):
    rnd = random.Random(seed + 1000)
    approved = {r for (r,) in D["approved"]}
    breach = {r for (r,) in D["cap_breach"]}
    vendor_ok = {r for (r,) in D["vendor_ok"]}
    charges = {}
    for r, c in D["charges"]:
        charges.setdefault(r, set()).add(c)
    own = {e: c for e, _, c in w["emps"]}
    req = {r[0]: r for r in w["reqs"]}
    depth_of = lambda r: w["lvl"][own[req[r][1]]]
    # Q1: an approved request, deepest requester
    yes = sorted(approved, key=lambda r: (-depth_of(r), r))
    # Q2: a non-approved request whose ONLY failure is an ancestor-level cap breach (own centre fine),
    #     else one failing via the exception-to-exception, else any
    def own_ok(r):
        c, a = own[req[r][1]], req[r][2]
        return dict(D["booked_total_kv"])[c] + a <= w["cap"][c]
    no = [r for r in req if r not in approved and r in breach and own_ok(r) and r in vendor_ok
          and not (w["level"] and req[r][1] in w["violation"])]
    no = no or [r for r in req if r not in approved]
    # directors / level-1 centres
    lvl1 = [c for c in w["cc"] if w["lvl"][c] == 1]
    x = rnd.choice(lvl1)
    mgr_x = next(e for e, r, c in w["emps"] if c == x and r == "director")
    chain_cnt = sum(1 for e, m in D["chain"] if m == mgr_x)
    susp = [r for r in req if VENDORS[req[r][4]] == "suspended"]
    if w["level"]:
        em = [r for r in susp if r in w["emergency"]]
        want = rnd.random() < 0.5
        cand = [r for r in em if (r in vendor_ok) == want] or em or susp
    else:
        want = rnd.random() < 0.5
        cand = [r for r in req if (r in vendor_ok) == want]
    q8 = rnd.choice(cand)
    Q = [
        ("Q1", "bool", f"Is request {yes[0]} approved?", True, "approved-yes"),
        ("Q2", "bool", f"Is request {no[0]} approved?", False, "approved-no"),
        ("Q3", "int", f"What is the headroom of cost centre {x}?", int(dict(D['headroom_kv'])[x]), "aggregate"),
        ("Q4", "int", f"How many employees have {mgr_x} in their reporting chain?", chain_cnt, "count-chain"),
        ("Q5", "set", f"Which requests that charge cost centre {x} are approved?",
         sorted(r for r in approved if x in charges.get(r, ())), "set-subtree"),
        ("Q6", "set", "Which requests breach a cap?", sorted(breach), "set-all"),
        ("Q7", "set", "Which cost centres are over cap?", sorted(c for (c,) in D["over_cap"]), "set-all"),
        ("Q8", "bool", f"Does request {q8} pass the vendor check?", q8 in vendor_ok, "override" if w["level"] else "lookup"),
        ("Q9", "int", "How many requests are approved in total?", len(approved), "count-all"),
    ]
    return [dict(id=i, type=t, text=s, kind=k) for i, t, s, _, k in Q], {i: a for i, t, s, a, k in Q}


def main():
    ap = argparse.ArgumentParser()
    for a, d in [("depth", 2), ("branch", 2), ("analysts", 2), ("level", 0), ("seed", 1)]:
        ap.add_argument(f"--{a}", type=int, default=d)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    w = build(a.depth, a.branch, a.analysts, a.level, a.seed)
    rules, facts = rules_dl(a.level), facts_dl(w)
    D = souffle(rules + facts, ["approved", "cap_breach", "vendor_ok", "charges", "chain", "over_cap", "headroom", "booked_total"])
    D["headroom_kv"] = [(c, h) for c, h in D["headroom"]]
    D["booked_total_kv"] = [(c, int(t)) for c, t in D["booked_total"]]
    qs, ans = questions(w, D, a.seed)
    qtext = "QUESTIONS\n\n" + "\n".join(f"{q['id']}. {q['text']}" for q in qs) + "\n\n"
    head = "You are answering questions about a procurement approval policy.\nRead the material, then answer the questions at the end. Treat the material as complete.\n\n"
    dl_block = "RULES AND FACTS -- the policy as a Datalog program (Souffle syntax)\n\n" + rules + "\n" + facts + "\n"
    (out / "prompt-text.txt").write_text(head + POLICY[a.level] + "\n" + facts_text(w) + "\n" + qtext + FORMAT)
    (out / "prompt-datalog.txt").write_text(head + dl_block + qtext + FORMAT)
    (out / "prompt-tool.txt").write_text(head + dl_block + qtext + FORMAT +
        "\nA Datalog engine holding exactly this program is available. Query it from the shell with\n"
        "  ./ask 'approved(R)'      or   ./ask 'headroom(\"cc1\", H)'\n"
        "(capitalised words are variables; any relation above may be queried). Use it as much as you like.\n")
    (out / "program.dl").write_text(rules + facts)
    import shacl_arm
    engine_s, _ = shacl_arm.emit(w, a.level, out, LIMIT, VENDORS, head, qtext, FORMAT)
    (out / "questions.json").write_text(json.dumps(qs, indent=1))
    (out / "answers.json").write_text(json.dumps(ans, indent=1))
    (out / "world.json").write_text(json.dumps(dict(depth=a.depth, branch=a.branch, analysts=a.analysts, level=a.level,
        seed=a.seed, cost_centres=len(w["cc"]), employees=len(w["emps"]), requests=len(w["reqs"]),
        facts=facts.count("\n"), prompt_chars={k: len((out / f"prompt-{k}.txt").read_text()) for k in ["text", "datalog", "tool", "shacl", "shacl-tool"]},
        shacl_engine_seconds=engine_s)))
    ask = out / "ask"
    ask.write_text(ASK_SH); ask.chmod(0o755)
    print(out, json.loads((out / "world.json").read_text()))


ASK_SH = r'''#!/usr/bin/env python3
"""./ask 'pred(args)' -- answer a query over program.dl with Souffle."""
import pathlib, re, subprocess, sys, tempfile
prog = (pathlib.Path(__file__).resolve().parent / "program.dl").read_text()
q = " ".join(sys.argv[1:]).strip().rstrip(".")
m = re.fullmatch(r"(\w+)\((.*)\)", q)
decl = dict((d[1], [t.split(":")[1].strip() for t in d[2].split(",")]) for d in re.finditer(r"\.decl\s+(\w+)\(([^)]*)\)", prog))
if not m or m[1] not in decl: sys.exit(f"error: unknown query {q!r}; relations: {', '.join(sorted(decl))}")
args = [a.strip() for a in m[2].split(",")] if m[2].strip() else []
if len(args) != len(decl[m[1]]): sys.exit(f"error: {m[1]} takes {len(decl[m[1]])} arguments")
vs, terms = [], []
for a, t in zip(args, decl[m[1]]):
    if a == "_" or a[:1].isupper():
        if a != "_" and a not in [v for v, _ in vs]: vs.append((a, t))
        terms.append(a)
    else:
        a = a.strip("'\"")
        terms.append(a if t == "number" else f'"{a}"')
head = ", ".join(f"{v}:{t}" for v, t in vs) or "ok:number"
rule = f"q({', '.join(v for v, _ in vs) or '1'}) :- {m[1]}({', '.join(terms)})."
with tempfile.TemporaryDirectory() as d:
    pathlib.Path(d, "q.dl").write_text(prog + f"\n.decl q({head})\n.output q\n{rule}\n")
    r = subprocess.run(["souffle", "-w", "-D", d, f"{d}/q.dl"], capture_output=True, text=True)
    if r.returncode: sys.exit("error: " + r.stderr.strip())
    rows = [l for l in pathlib.Path(d, "q.csv").read_text().splitlines() if l]
print(("true" if rows else "false") if not vs else "\n".join(rows) if rows else "(no rows)")
'''

if __name__ == "__main__":
    main()
