"""Instantiate the question bank for one world.

For each template, draw up to N_CAND distinct parameter sets, key them all with the engine, then keep
two whose keys differ (decided value at L3 and open-config status at L3) where the candidates allow it.
Instance ids are <template>-1, <template>-2.
"""
import json, pathlib, random, subprocess, tempfile
from datetime import date, timedelta
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANK = yaml.safe_load((ROOT / "questions/bank.yaml").read_text())["templates"]
SCHEMA = yaml.safe_load((ROOT / "world/schema.yaml").read_text())["relations"]
N_CAND, N_KEEP = 6, 2
TODAY = date(2026, 9, 15)
REQ_FROM = date(2026, 6, 1)


class Pools:
    def __init__(self, w):
        R = w["relations"]
        self.cc = [c for (c,) in R["cc"]]
        par = {c: p for c, p in R["cc_parent"]}
        self.internal = sorted({p for p in par.values() if p in par})        # non-root, non-leaf
        self.internal = self.internal or sorted(set(par.values()))
        self.leaf = [c for c in self.cc if c not in par.values()]
        self.emp = {e: (r, c) for e, r, c in R["emp"]}
        self.mgr = dict(R["reports"])
        self.managers = sorted(set(self.mgr.values()))
        self.analysts = [e for e, (r, _) in self.emp.items() if r == "analyst"]
        self.req = {r[0]: r for r in R["req"]}
        viol = {e for (e,) in R["violation"]}
        emerg = {r for (r,) in R["emergency"]}
        self.req_hot = [r for r, (_, e, a, cat, v, d, st) in self.req.items()
                        if e in viol or r in emerg or cat == "capital" or 25000 < a <= 40000
                        or v in ("bolt", "dyne", "fern") or (cat == "software" and a < 10000)]
        self.vendors = [v for (v, _) in R["vendor"]]
        periods = {}
        for v, *_ in R["vendor_status"]:
            periods[v] = periods.get(v, 0) + 1
        self.changing = [v for v, n in periods.items() if n > 1]
        hr = {}
        for e, c, src, eff in R["assignment"]:
            if src == "hr" and eff > "2026-01-01":
                hr[e] = eff
        fin = {e: eff for e, c, src, eff in R["assignment"] if src == "finance" and eff > "2026-01-01"}
        self.moved = {e: (hr[e], fin.get(e)) for e in sorted(hr)}
        self.rels = sorted({t for r in SCHEMA for t in (r.get("fks") or {}).values()})

    def chain(self, e):
        out = []
        while e in self.mgr:
            e = self.mgr[e]; out.append(e)
        return out


def _rand_date(rnd, lo, hi):
    return lo + timedelta(days=rnd.randrange((hi - lo).days + 1))


def draw(kind, P, rnd, bound):
    """One value for a sampler kind; returns (text value, goal value)."""
    pick = lambda xs: rnd.choice(xs)
    if kind == "referenced_relation": v = pick(P.rels)
    elif kind == "manager": v = pick(P.managers)
    elif kind == "leaf_cc": v = pick(P.leaf)
    elif kind == "cc": v = pick(P.cc)
    elif kind == "internal_cc": v = pick(P.internal)
    elif kind == "vendor": v = pick(P.vendors)
    elif kind == "changing_vendor": v = pick(P.changing if rnd.random() < 0.75 else P.vendors)
    elif kind == "req": v = pick(P.req_hot if P.req_hot and rnd.random() < 0.6 else list(P.req))
    elif kind == "analyst": v = pick(P.analysts)
    elif kind == "chain_member":
        ch = P.chain(P.req[bound["r"][0]][1])
        v = pick(ch) if ch and rnd.random() < 0.85 else pick(list(P.emp))
    elif kind == "moved": v = pick(list(P.moved))
    elif kind == "source": v = pick(["hr", "finance"])
    elif kind in ("date", "move_date"):
        if kind == "move_date":
            d1, d2 = P.moved[bound["e"][0]]
            lo = date.fromisoformat(d1) - timedelta(days=10)
            hi = min(TODAY, (date.fromisoformat(d2) if d2 else TODAY) + timedelta(days=10))
        else:
            lo, hi = REQ_FROM, TODAY
        d = _rand_date(rnd, lo, hi)
        return d.isoformat(), d.strftime("%Y%m%d")
    else:
        raise ValueError(kind)
    return v, v


def candidates(t, P, rnd):
    seen, out = set(), []
    for _ in range(N_CAND * 5):
        b = {}
        for name, kind in (t.get("params") or {}).items():
            b[name] = draw(kind, P, rnd, b)
        key = tuple(sorted((k, v[0]) for k, v in b.items()))
        if key in seen:
            continue
        seen.add(key)
        fill = lambda s, i: None if s is None else s.format(**{k: v[i] for k, v in b.items()})
        out.append(dict(template=t["id"], kind=t["kind"], type=t["type"], text=fill(t["text"], 0),
                        goal=fill(t["goal"], 1), conflict=fill(t.get("conflict"), 1), resolve=fill(t.get("resolve"), 1),
                        params={k: v[0] for k, v in b.items()}))
        if len(out) == N_CAND:
            break
    return out


def engine_keys(world_dir, qs):
    with tempfile.TemporaryDirectory() as tmp:
        qf, kf = pathlib.Path(tmp, "q.json"), pathlib.Path(tmp, "k.json")
        qf.write_text(json.dumps(qs))
        subprocess.run(["swipl", str(ROOT / "engine/keys.pl"), str(ROOT), str(world_dir), str(qf), str(kf)], check=True)
        return json.loads(kf.read_text())


def make(world_dir, w, seed):
    rnd = random.Random(seed + 7000)
    P = Pools(w)
    cands = []
    for t in BANK:
        if t.get("paraphrase_of"):      # no draws: the sampling of every other template is unchanged
            continue
        for i, q in enumerate(candidates(t, P, rnd)):
            q["id"] = f"{t['id']}-c{i + 1}"
            cands.append(q)
    K = engine_keys(world_dir, cands)
    sig = lambda q: json.dumps([K["decided"][q["id"]]["L3"], K["open"][q["id"]]["L3"]["status"]], sort_keys=True)
    qs, keys = [], {"meta": {}, "decided": {}, "open": {}}
    para = []
    for t in BANK:
        if t.get("paraphrase_of"):
            para.append(t)
            continue
        cs = [q for q in cands if q["template"] == t["id"]]
        groups = {}
        for q in cs:
            groups.setdefault(sig(q), []).append(q)
        order = sorted(groups)
        rnd.shuffle(order)
        chosen = [groups[g][0] for g in order[:N_KEEP]]
        rest = [q for q in cs if q not in chosen]
        chosen += rest[:N_KEEP - len(chosen)]
        for i, q in enumerate(sorted(chosen, key=lambda q: q["id"])):
            new = f"{t['id']}-{i + 1}"
            for part in keys:
                keys[part][new] = K[part][q["id"]]
            qs.append(dict(q, id=new))
    if para:
        pq = []
        for t in para:
            for q in [q for q in qs if q["template"] == t["paraphrase_of"]]:
                fill = lambda s, i: None if s is None else s.format(**{k: q["params"][k] if i == 0 else goal_val(q, k) for k in q["params"]})
                pq.append(dict(template=t["id"], kind=t["kind"], type=t["type"], text=fill(t["text"], 0),
                               goal=fill(t["goal"], 1), conflict=fill(t.get("conflict"), 1), resolve=fill(t.get("resolve"), 1),
                               params=dict(q["params"]), id=f"{t['id']}-{q['id'].rsplit('-', 1)[1]}"))
        PK = engine_keys(world_dir, pq)
        for q in pq:
            for part in keys:
                keys[part][q["id"]] = PK[part][q["id"]]
        qs += pq
    return qs, keys


def goal_val(q, k):
    """A parameter's goal form: ISO dates become YYYYMMDD, everything else is the same."""
    v = q["params"][k]
    return v.replace("-", "") if len(v) == 10 and v[4] == "-" and v[7] == "-" else v
