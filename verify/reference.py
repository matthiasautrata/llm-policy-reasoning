"""Independent reference: the rules' English (rules/rules.yaml `english`) re-implemented in plain
Python over world.json, without the engine, the Prolog clauses, or the engine's dependency analysis.

Gating uses the question bank's *declared* min_layer and forks; the engine derives both itself, and
verify/check.py compares the two. Keys have the same shape as engine/keys.pl's.
"""
import itertools, pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANK = {t["id"]: t for t in yaml.safe_load((ROOT / "questions/bank.yaml").read_text())["templates"]}
_RULES = yaml.safe_load((ROOT / "rules/rules.yaml").read_text())
FORKS = {f["id"]: f for f in _RULES["forks"]}
SCHEMA = yaml.safe_load((ROOT / "world/schema.yaml").read_text())["relations"]
LAYERS = range(4)


class World:
    """The policy at layer k under fork readings rd, evaluated from the English rule texts."""

    def __init__(self, w, k, rd):
        R = w["relations"]
        self.k, self.rd, self.R = k, rd, R
        self.cc = [c for (c,) in R["cc"]]
        self.parent = dict(R["cc_parent"])
        self.unit = dict(R["org_unit"])
        self.emp = {e: (r, c) for e, r, c in R["emp"]}
        self.mgr = dict(R["reports"])
        self.req = {r[0]: r for r in R["req"]}
        self.emerg = {r for (r,) in R["emergency"]}
        self.viol = {e for (e,) in R["violation"]}
        self.booked = dict(R["booked"])
        self.cap = dict(R["cap"])
        self.today = R["today"][0][0]

    # L1 -- "The ancestors of a cost centre are its parent, its parent's parent, and so on."
    def anc(self, c):
        out = []
        while c in self.parent:
            c = self.parent[c]; out.append(c)
        return out

    def subtree(self, x):            # x itself and its descendants
        return {c for c in self.cc if c == x or x in self.anc(c)}

    def chain(self, e):              # manager, manager's manager, ...; not the employee
        out = []
        while e in self.mgr:
            e = self.mgr[e]; out.append(e)
        return out

    def booked_total(self, c):       # fork c6
        if self.rd["c6"] == "direct_only":
            return self.booked.get(c, 0)
        return sum(self.booked.get(d, 0) for d in self.subtree(c))

    def pending_total(self, c):
        sub = self.subtree(c)
        return sum(a for _, e, a, _, _, _, st in self.req.values() if st == "pending" and self.emp[e][1] in sub)

    def committed(self, c):          # fork c1
        return self.booked_total(c) + (self.pending_total(c) if self.rd["c1"] == "with_pending" else 0)

    def headroom(self, c):
        return self.cap[c] - self.committed(c)

    def over_cap(self, c):
        return self.committed(c) > self.cap[c]

    def cap_scope(self, r):          # fork c4
        own = self.emp[self.req[r][1]][1]
        return [own] + (self.anc(own) if self.rd["c4"] == "with_ancestors" else [])

    def cap_breach(self, r):
        _, _, a, _, _, _, st = self.req[r]
        for c in self.cap_scope(r):
            # committed spend plus the amount, not counting r twice when committed already includes it
            x = self.committed(c) + (0 if self.rd["c1"] == "with_pending" and st == "pending" else a)
            if x > self.cap[c]:
                return True
        return False

    def big_capital(self, r):
        return self.req[r][3] == "capital" and self.req[r][2] > 50000

    def dept(self, e):               # fork c3
        c = self.emp[e][1]
        return c if self.rd["c3"] == "cost_centre" else self.unit[c]

    def headcount(self, d):
        return sum(self.dept(e) == d for e in self.emp)

    # L2 -- dated rules
    def governing_date(self, r):     # fork c2
        return self.req[r][5] if self.rd["c2"] == "request_date" else self.today

    def limit_on(self, role, d):
        return [l for ro, l, f, t in self.R["role_limit_version"] if ro == role and f <= d <= t]

    def vendor_status_on(self, v, d):
        return [s for vv, s, f, t in self.R["vendor_status"] if vv == v and f <= d <= t]

    def vendor_approved(self, r):
        return "approved" in self.vendor_status_on(self.req[r][4], self.governing_date(r))

    def cc_on(self, e, src, d):      # the latest record of src effective on or before d
        recs = [(eff, c) for ee, c, s, eff in self.R["assignment"] if ee == e and s == src and eff <= d]
        if not recs:
            return set()
        latest = max(eff for eff, _ in recs)
        return {c for eff, c in recs if eff == latest}

    def disputed_on(self, e, d):
        return any(a != b for a in self.cc_on(e, "hr", d) for b in self.cc_on(e, "finance", d))

    def exemption_in_force(self, cat, d):
        wd = {}
        for x, w in self.R["exemption_withdrawn"]:
            wd.setdefault(x, []).append(w)
        return any(c == cat and g <= d and not any(w <= d for w in wd.get(x, [])) for x, c, g in self.R["exemption"])

    # L3 -- warrant
    def approver(self, r, m):
        _, e, a, *_ = self.req[r]
        return m in self.chain(e) and any(l >= a for l in self.limit_on(self.emp[m][0], self.governing_date(r)))

    def has_approver(self, r):
        return any(self.approver(r, m) for m in self.chain(self.req[r][1]))

    def exempt(self, r):
        return self.exemption_in_force(self.req[r][3], self.governing_date(r))

    def cap_ok(self, r):
        return not self.cap_breach(r) or self.exempt(r)

    def waiver(self, r):
        return r in self.emerg and "suspended" in self.vendor_status_on(self.req[r][4], self.governing_date(r))

    def waiver_blocked(self, r):
        return self.waiver(r) and self.big_capital(r)

    def vendor_cleared(self, r):
        return self.vendor_approved(r) or (self.waiver(r) and not self.waiver_blocked(r))

    def eligible(self, r):
        return self.has_approver(r) and self.cap_ok(r) and self.vendor_cleared(r)

    def denied(self, r):
        return self.req[r][1] in self.viol

    def auto_approved(self, r):
        return self.req[r][3] == "software" and self.req[r][2] < 10000

    def approved(self, r):
        return (self.eligible(r) and not self.denied(r)) or self.auto_approved(r)

    def in_sub_reqs(self, c):
        sub = self.subtree(c)
        return [r for r, (_, e, *_) in self.req.items() if self.emp[e][1] in sub]


def _single(xs):
    xs = sorted(set(xs))
    if len(xs) > 1:
        raise ValueError(f"not single: {xs}")
    return xs[0] if xs else "none"


def _schema_refs(rel, k):
    return sorted({r["name"] for r in SCHEMA if r["layer"] <= k for t in (r.get("fks") or {}).values() if t == rel})


# template -> (value(W, p, k), conflict(W, p) or None, resolve: (layer, value(W, p)) or None)
EVAL = {
    "Q01": (lambda W, p, k: _schema_refs(p["rel"], k), None, None),
    "Q02": (lambda W, p, k: sorted(e for e, m in W.mgr.items() if m == p["m"]), None, None),
    "Q03": (lambda W, p, k: sum(1 for _, e, *_, st in W.req.values() if st == "pending" and W.emp[e][1] == p["c"]), None, None),
    "Q04": (lambda W, p, k: W.booked.get(p["c"], 0), None, None),
    "Q05": (lambda W, p, k: _single(s for v, s in W.R["vendor"] if v == p["v"]), None, None),
    "Q11": (lambda W, p, k: W.booked_total(p["c"]), None, None),
    "Q17": (lambda W, p, k: W.booked_total(p["c"]), None, None),      # paraphrase of Q11
    "Q12": (lambda W, p, k: W.headroom(p["c"]), None, None),
    "Q13": (lambda W, p, k: sorted(c for c in W.subtree(p["c"]) if W.over_cap(c)), None, None),
    "Q14": (lambda W, p, k: W.cap_breach(p["r"]), None, None),
    "Q15": (lambda W, p, k: W.headcount(W.dept(p["e"])), None, None),
    "Q16": (lambda W, p, k: sum(p["m"] in W.chain(e) for e in W.emp), None, None),
    "Q21": (lambda W, p, k: "approved" in W.vendor_status_on(p["v"], p["d"]), None, None),
    "Q22": (lambda W, p, k: _single(W.limit_on(W.emp[p["m"]][0], W.governing_date(p["r"]))), None, None),
    "Q23": (lambda W, p, k: _single(W.cc_on(p["e"], p["src"], p["d"])), None, None),
    "Q24": (lambda W, p, k: W.disputed_on(p["e"], p["d"]), None, None),
    "Q25": (lambda W, p, k: _single(W.cc_on(p["e"], "hr", p["d"]) | W.cc_on(p["e"], "finance", p["d"])),
            lambda W, p: W.disputed_on(p["e"], p["d"]),
            (3, lambda W, p: _single(W.cc_on(p["e"], "finance", p["d"])))),     # R313: finance governs
    "Q26": (lambda W, p, k: W.exemption_in_force("capital", p["d"]), None, None),
    "Q31": (lambda W, p, k: W.approver(p["r"], p["m"]), None, None),
    "Q32": (lambda W, p, k: W.vendor_cleared(p["r"]), None, None),
    "Q33": (lambda W, p, k: W.approved(p["r"]), lambda W, p: W.denied(p["r"]) and W.auto_approved(p["r"]), None),
    "Q34": (lambda W, p, k: sorted(r for r in W.in_sub_reqs(p["c"]) if W.approved(r)),
            lambda W, p: any(W.denied(r) and W.auto_approved(r) for r in W.in_sub_reqs(p["c"])), None),
    "Q35": (lambda W, p, k: W.denied(p["r"]), None, None),
    "Q36": (lambda W, p, k: W.cap_ok(p["r"]), None, None),
}


# template -> the distinct values the material supports when the conflict holds (sym/int goals);
# bool goals have both sides, set goals none.
SIDES = {"Q25": lambda W, p: sorted(W.cc_on(p["e"], "hr", p["d"]) | W.cc_on(p["e"], "finance", p["d"]))}


def _eval(w, k, rd, t, p):
    """('v', value) or ('c', sides) for one layer and one full set of readings."""
    val, conflict, resolve = EVAL[t]
    W = World(w, k, rd)
    if conflict and conflict(W, p):
        if resolve and resolve[0] <= k:
            return ("v", resolve[1](W, p))
        typ = BANK[t]["type"]
        return ("c", [False, True] if typ == "bool" else None if typ == "set" else SIDES[t](W, p))
    return ("v", val(W, p, k))


def keys(w, questions):
    out = {"decided": {}, "open": {}}
    dec = {f: x["decided"] for f, x in FORKS.items()}
    for q in questions:
        t = BANK[q["template"]]
        p = {n: q["params"][n] for n in (t.get("params") or {})}
        for cfg in out:
            ks = {}
            for k in LAYERS:
                L = f"L{k}"
                if t["min_layer"] is None:
                    ks[L] = {"status": "OUT_OF_SCOPE"}; continue
                if k < t["min_layer"]:
                    ks[L] = {"status": "UNDERDETERMINED", "missing_layer": t["min_layer"]}; continue
                live = [] if cfg == "decided" else sorted(f for f in t["forks"] if FORKS[f]["layer"] <= k)
                res = {}
                for combo in itertools.product(*(FORKS[f]["readings"] for f in live)):
                    rd = dict(dec, **dict(zip(live, combo)))
                    res[",".join(f"{f}={r}" for f, r in zip(live, combo)) or "decided"] = _eval(w, k, rd, q["template"], p)
                distinct = {repr(v) for v in res.values()}
                if len(distinct) == 1:
                    v = next(iter(res.values()))
                    ks[L] = {"status": "ANSWER", "value": v[1]} if v[0] == "v" else \
                        {"status": "CONFLICT", **({"sides": v[1]} if v[1] is not None else {})}
                else:
                    ks[L] = {"status": "AMBIGUOUS", "readings": {rk: (v[1] if v[0] == "v" else "CONFLICT") for rk, v in res.items()}}
            out[cfg][q["id"]] = ks
    return out
