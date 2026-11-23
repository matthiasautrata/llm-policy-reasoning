"""World generator (harvested from v1 study2-scaling/gen.py and study1 oracle/large).

  python world/gen.py                     # all sizes x seeds -> worlds/<size>-s<seed>/
  python world/gen.py --size M --seed 2

A world is a cost-centre tree (one manager per centre, analysts in the leaves), requests, vendors,
budgets, dated role limits and vendor periods, an exemption that is withdrawn, and hr/finance
assignment records that disagree for a while after a transfer. Writes per world:
  world.json      params + every base relation as rows (dates ISO)
  facts.pl        the formal projection of all base relations (dates YYYYMMDD)
  L0/             the L0 projections: text.md, structured.yaml, formal.pl
  questions.json  question instances sampled from questions/bank.yaml
  keys.json       per-layer answer keys computed by the engine (engine/keys.pl)
"""
import argparse, json, pathlib, random, sys
from datetime import timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from world.domain import *          # noqa: E402,F403

import yaml                         # noqa: E402

SCHEMA = yaml.safe_load((ROOT / "world/schema.yaml").read_text())["relations"]


def iso(d):
    return d.isoformat()


def build(size, seed):
    depth, branch, analysts = SIZES[size]
    rnd = random.Random(seed * 1000 + depth * 10 + branch)
    cc, parent, lvl = [], {}, {}

    def mk(c, p, l):
        cc.append(c); lvl[c] = l
        if p: parent[c] = p
        if l < depth:
            for i in range(branch):
                mk(f"{c}_{i + 1}" if p else f"cc{i + 1}", c, l + 1)
    mk("company", None, 0)
    leaves = [c for c in cc if lvl[c] == depth]
    unit = {c: (rnd.choice(LEAF_UNITS) if lvl[c] == depth else INTERNAL_UNIT) for c in cc}

    emps, mgr, n = [], {}, 0          # emps: [emp, role, initial cc]
    for c in cc:
        role = "vp" if lvl[c] == 0 else "director" if lvl[c] == 1 else "manager" if lvl[c] == depth else "senior_manager"
        e = f"e{n:03d}"; n += 1; emps.append([e, role, c]); mgr[c] = e
    for c in leaves:
        for _ in range(analysts):
            e = f"e{n:03d}"; n += 1; emps.append([e, "analyst", c])

    # transfers: hr records the move on d1; finance on d2 > d1, or not yet (d2 after today -> no record)
    analysts_ = [e for e in emps if e[1] == "analyst"]
    k = max(2, round(len(analysts_) * P_TRANSFER))
    assignment = [[e, c, src, iso(YEAR_START)] for e, _, c in emps for src in ("hr", "finance")]
    final_cc = {e: c for e, _, c in emps}
    for i, (e, _, c) in enumerate(sorted(rnd.sample(analysts_, k))):
        to = rnd.choice([l for l in leaves if l != c])
        if i == 1:                     # one move finance has not recorded yet
            d1, d2 = REQ_FROM + timedelta(days=rnd.randrange(80, 96)), None
        else:
            d1 = REQ_FROM + timedelta(days=rnd.randrange(10, 80))
            d2 = d1 + timedelta(days=rnd.randrange(7, 41))
            if i > 1 and rnd.random() < 0.3:
                d2 = None
            if d2 is not None and d2 > TODAY:
                d2 = None
        assignment.append([e, to, "hr", iso(d1)])
        if d2 is not None:
            assignment.append([e, to, "finance", iso(d2)]); final_cc[e] = to
    emp = [[e, r, final_cc[e]] for e, r, _ in emps]
    reports = [[e, mgr[parent[c]]] for e, r, c in emp if r != "analyst" and c in parent]
    reports += [[e, mgr[c]] for e, r, c in emp if r == "analyst"]
    reports.sort()

    # budgets (v1): leaves book 40k-140k, some internal centres book a little; caps around the booked total
    booked = {c: rnd.randrange(40, 141) * 1000 for c in leaves}
    for c in cc:
        if lvl[c] < depth and rnd.random() < 0.3:
            booked[c] = rnd.randrange(5, 40) * 1000
    total = {}
    for c in reversed(cc):
        total[c] = booked.get(c, 0) + sum(total[x] for x in cc if parent.get(x) == c)
    factors = lambda c: [1.2, 1.4] if lvl[c] == 0 else [1.05, 1.15, 1.3, 1.5] if lvl[c] < depth else [0.97, 1.03, 1.1, 1.2, 1.4, 1.6]
    cap = {c: int(total[c] * rnd.choice(factors(c)) // 1000 * 1000) for c in cc}

    staff = [e for e in emp if e[1] != "vp"]
    span = (TODAY - REQ_FROM).days
    req = []
    for i in range(max(8, int(len(emp) * REQ_RATIO))):
        e = rnd.choice(staff)[0]
        d = REQ_FROM + timedelta(days=rnd.randrange(span + 1))
        st = "cancelled" if rnd.random() < P_CANCELLED else "pending"
        req.append([f"r{i + 1:03d}", e, rnd.choice(AMOUNTS), rnd.choice(CATEGORIES), rnd.choice(list(VENDORS)), iso(d), st])
    violation = sorted(rnd.sample([e[0] for e in staff], max(1, round(len(staff) * P_VIOLATION))))
    emergency = {i for i in range(len(req)) if rnd.random() < P_EMERGENCY}
    # planted cases, so every world exercises each rule interaction at least once (ids are shuffled below)
    day = lambda lo, hi: iso(REQ_FROM + timedelta(days=rnd.randrange(lo, hi)))
    an = [e for e, r, _ in emp if r == "analyst"]
    plant = [
        ([rnd.choice(violation), 8000, "software", "acme", day(0, span + 1), "pending"], False),   # deny vs auto-approve (C5)
        ([rnd.choice(an), 90000, "capital", "fern", day(0, span + 1), "pending"], True),         # waiver blocked
        ([rnd.choice(an), 12000, "hardware", "fern", day(0, span + 1), "pending"], True),        # waiver applies
        ([rnd.choice(an), 38000, "services", "acme", day(0, 60), "pending"], False),             # limit change (c2)
        ([rnd.choice(an), 60000, "capital", "cog", day(0, 70), "pending"], False),               # exemption, later withdrawn (c2)
        ([rnd.choice(an), 20000, "hardware", "bolt", day(0, 60), "pending"], False),             # vendor suspended later (c2)
    ]
    for row, em in plant:
        if em:
            emergency.add(len(req))
        req.append([None] + row)
    order = list(range(len(req)))
    rnd.shuffle(order)
    req = [[f"r{n + 1:03d}"] + req[i][1:] for n, i in enumerate(order)]
    emergency = sorted(f"r{n + 1:03d}" for n, i in enumerate(order) if i in emergency)

    rel = {
        "cc": [[c] for c in cc],
        "cc_parent": [[c, p] for c, p in parent.items()],
        "org_unit": [[c, unit[c]] for c in cc],
        "emp": emp,
        "reports": reports,
        "role_limit": [[r, as_of(vs, TODAY)] for r, vs in ROLE_LIMITS.items()],
        "vendor": [[v, as_of(ps, TODAY)] for v, ps in VENDORS.items()],
        "req": req,
        "emergency": [[r] for r in emergency],
        "violation": [[e] for e in violation],
        "booked": [[c, b] for c, b in booked.items()],
        "cap": [[c, k] for c, k in cap.items()],
        "today": [[iso(TODAY)]],
        "role_limit_version": [[r, l, iso(f), iso(t)] for r, vs in ROLE_LIMITS.items() for l, f, t in vs],
        "vendor_status": [[v, s, iso(f), iso(t)] for v, ps in VENDORS.items() for s, f, t in ps],
        "assignment": sorted(assignment, key=lambda a: (a[0], a[2], a[3])),
        "exemption": [[x, cat, iso(g)] for x, (cat, g, _) in EXEMPTIONS.items()],
        "exemption_withdrawn": [[x, iso(w)] for x, (_, _, w) in EXEMPTIONS.items() if w],
    }
    assert set(rel) == {r["name"] for r in SCHEMA}, "schema and generator disagree on relations"
    params = dict(size=size, seed=seed, depth=depth, branch=branch, analysts=analysts, today=iso(TODAY),
                  counts={k: len(v) for k, v in rel.items()})
    return dict(params=params, relations=rel)


# (layer, config) of the material written per world; layers without rules have one config.
MATERIAL = [(0, "decided"), (1, "decided"), (1, "open")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", choices=list(SIZES)); ap.add_argument("--seed", type=int)
    ap.add_argument("--out", default=str(ROOT / "worlds"))
    a = ap.parse_args()
    from render import prolog, text, structured
    from render.common import material_dir
    from questions import sample
    for size in [a.size] if a.size else SIZES:
        for seed in [a.seed] if a.seed else SEEDS:
            w = build(size, seed)
            d = pathlib.Path(a.out) / f"{size}-s{seed}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "world.json").write_text(json.dumps(w, indent=1) + "\n")
            (d / "facts.pl").write_text(prolog.facts(w, 3))
            for k, cfg in MATERIAL:
                m = d / material_dir(k, cfg)
                m.mkdir(exist_ok=True)
                (m / "formal.pl").write_text(prolog.render(w, k, cfg))
                (m / "text.md").write_text(text.render(w, k, cfg))
                (m / "structured.yaml").write_text(structured.render(w, k, cfg))
            qs, keys = sample.make(d, w, seed)
            (d / "questions.json").write_text(json.dumps(qs, indent=1) + "\n")
            (d / "keys.json").write_text(json.dumps(keys, indent=1, sort_keys=True) + "\n")
            print(d.name, w["params"]["counts"]["emp"], "employees,", w["params"]["counts"]["req"], "requests,", len(qs), "questions")


if __name__ == "__main__":
    main()
