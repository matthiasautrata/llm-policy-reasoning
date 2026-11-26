"""Independent reference for spike v3: the rules' :doc texts and the slice semantics re-implemented by hand in
plain Python over the detail data, without any rule interpreter, the concept bindings, or the spikes.

  python spikes/v3/shared/reference.py               # -> shared/keys.json
  python spikes/v3/shared/reference.py --mutate      # flipped comparisons -> stdout (mutation test)
  python spikes/v3/shared/reference.py --bench bench/bases/N050 ...   # benchmark family keys -> N050.keys.json
  python spikes/v3/shared/reference.py --tasks bench/tasks/A1.json ... # analyst task components -> A1.keys.json

Reads slice.edn only for constants a reader of the docs would also read (today, claims, terms,
functional predicates); every rule is a Python function below. Data: a full load of DuckDB (the
reference is not System A and may hold the rows).

Key shape per question:
  decide        {status, value, sides, core, qualifier}        sides: sorted list of sorted id lists, or null
  why_not       {status, value, failed, core, qualifier}   failed: literals that must be shown as failed
  claim         {standing, defeater, qualifier, core}
  resolve_term  {status, candidates}
  fetch         {value, row_count, core}             (Q24, Q25: the integer-cast regressions, pending exposure and booked total of the root)
Dispute questions (:state :acyclic, keys["acyclic"]) use the class Prop: the hand-grounded theory of
cycles-acyclic.edn under ambiguity propagation (SEMANTICS.md). Every decide key adds qualifier
("total over known facts in declared scope" when the answer rests on absence: SEMANTICS.md, Qualifier).
`core` lists the rule / claim ids an explanation must contain.
"""
import argparse, datetime, json, pathlib, re, sys
import edn_format as E  # duckdb is imported where the reference reads data (integrity.py needs only the reader)

HERE = pathlib.Path(__file__).resolve().parent
K = E.Keyword


def kw(x):
    return x.name if isinstance(x, E.Keyword) else x


def iso(x):
    return x.isoformat()[:10] if isinstance(x, (datetime.date, datetime.datetime)) else x


def plain(x):
    """EDN value -> plain Python (keywords to names, #inst to ISO dates)."""
    if isinstance(x, E.Keyword): return x.name
    if isinstance(x, (datetime.date, datetime.datetime)): return iso(x)
    if hasattr(x, "items"): return {plain(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, frozenset, set)) or type(x).__name__ == "ImmutableList": return [plain(v) for v in x]
    if isinstance(x, E.Symbol): return "?" + x.name.lstrip("?") if x.name.startswith("?") else x.name
    return x


class Ref:
    def __init__(self, slice_, extended, mutate=False):
        self.S, self.ext, self.mut = slice_, extended, mutate
        self.today = slice_["today"]
        import duckdb
        con = duckdb.connect(str(HERE / "slice.duckdb"), read_only=True)
        q = lambda s: con.execute(s).fetchall()
        self.cc = {r[0]: dict(parent=r[1], booked=r[2], cap=r[3]) for r in q("SELECT id, parent, booked, cap FROM cc")}
        self.kids = {}
        for c, d in self.cc.items():
            self.kids.setdefault(d["parent"], []).append(c)
        self.emp = {r[0]: dict(role=r[1], cc=r[2], manager=r[3], violation=r[4]) for r in q("SELECT id, role, cc, manager, violation FROM emp")}
        self.req = {r[0]: dict(requester=r[1], amount=r[2], category=r[3], vendor=r[4], date=iso(r[5]), status=r[6], emergency=r[7])
                    for r in q("SELECT * FROM req")}
        self.limits = [(r[0], r[1], iso(r[2]), iso(r[3])) for r in q('SELECT role, "limit", valid_from, valid_to FROM role_limit_version')]
        self.vstat = [(r[0], r[1], iso(r[2]), iso(r[3])) for r in q("SELECT * FROM vendor_status")]
        self._bt = {}
        claims = list(slice_["claims"]) + ([x for x in extended if x["id"].startswith("C")] if extended else [])
        self.claims = {}
        for c in claims:
            self.claims[c["id"]] = c
        self.has_R307 = any(x["id"] == "R307" for x in extended)

    # ---- R104 / R105: booked total over the subtree; headroom
    def subtree(self, x):
        out, st = [], [x]
        while st:
            c = st.pop(); out.append(c); st += self.kids.get(c, [])
        return out

    def booked_total(self, c):
        if c not in self._bt:
            self._bt[c] = sum(self.cc[d]["booked"] for d in self.subtree(c))
        return self._bt[c]

    def headroom(self, c):
        return self.cc[c]["cap"] - self.booked_total(c)

    def anc_self(self, c):
        out = [c]
        while self.cc[c]["parent"]:
            c = self.cc[c]["parent"]; out.append(c)
        return out

    # ---- R106 cap breach; R110 breaching requests in a subtree
    def cap_breach(self, r):
        q = self.req[r]
        gt = (lambda a, b: a < b) if self.mut else (lambda a, b: a > b)          # mutation 1
        return any(gt(self.booked_total(c) + q["amount"], self.cc[c]["cap"]) for c in self.anc_self(self.emp[q["requester"]]["cc"]))

    def breach_in(self, x):
        sub = set(self.subtree(x))
        return sorted(r for r, q in self.req.items() if q["status"] == "pending" and self.emp[q["requester"]]["cc"] in sub and self.cap_breach(r))

    # ---- R202 / R201 / R203 dated limits
    def limit_on(self, role, d):
        return next((l for ro, l, f, t in self.limits if ro == role and f <= d <= t), None)

    def chain(self, e):
        out = []
        while self.emp[e]["manager"]:
            e = self.emp[e]["manager"]; out.append(e)
        return out

    # ---- R204 vendor status on the request date; R305 / R306 / R307 vendor check
    def vendor_status_for(self, r):
        q = self.req[r]
        return next((s for v, s, f, t in self.vstat if v == q["vendor"] and f <= q["date"] <= t), None)

    def big_capital(self, r):
        q = self.req[r]
        return q["category"] == "capital" and q["amount"] > 50000

    def vendor_cleared(self, r):
        """-> (value, supporting rule, defeater)"""
        q, s = self.req[r], self.vendor_status_for(r)
        if s == "approved":
            return True, "R305", None
        if q["emergency"] and s == "suspended":
            if self.has_R307 and self.big_capital(r):        # defeater R307, superior to R306
                return False, None, "R307"
            return True, "R306", None
        return False, None, None

    def has_approver(self, r):
        q = self.req[r]
        return any((self.limit_on(self.emp[a]["role"], q["date"]) or -1) >= q["amount"] for a in self.chain(q["requester"]))

    def denied(self, r):
        return self.emp[self.req[r]["requester"]]["violation"]

    def auto_approved(self, r):
        q = self.req[r]
        lt = (lambda a, b: a > b) if self.mut else (lambda a, b: a < b)          # mutation 2
        return q["category"] == "software" and lt(q["amount"], 10000)

    def eligible(self, r):
        return self.has_approver(r) and not self.cap_breach(r) and self.vendor_cleared(r)[0]

    def approved(self, r):
        """-> (status, value, sides): R310, R312; R314 makes approved+denied a CONFLICT."""
        sup = (["R310"] if self.eligible(r) and not self.denied(r) else []) + (["R312"] if self.auto_approved(r) else [])
        if sup and self.denied(r):
            return "CONFLICT", None, sorted([sorted(sup), ["R314"]])
        return "ANSWER", bool(sup), None

    # ---- R120 / R121: aggregate over the pending requests of a subtree whose approval is proven
    def approved_agg(self, x, op):
        """-> (status, value, sides, contested, count): members = approved proven (count of them); any contested
        member contests the aggregate (sides = the members' root sides); the contested instance binds the proven part."""
        sub = set(self.subtree(x))
        reqs = sorted(r for r, q in self.req.items() if q["status"] == "pending" and self.emp[q["requester"]]["cc"] in sub)
        val = lambda rs: sum(self.req[r]["amount"] for r in rs) if op == "sum" else len(rs)
        res = {r: self.approved(r) for r in reqs}
        mem = [r for r in reqs if res[r][0] == "ANSWER" and res[r][1]]
        cont = [r for r in reqs if res[r][0] == "CONFLICT"]
        if not cont:
            return "ANSWER", val(mem), None, None, len(mem)
        sides = sorted({json.dumps(sd) for r in cont for sd in res[r][2]})
        return "CONFLICT", val(mem), [json.loads(sd) for sd in sides], {
            "via": [["approved", r] for r in cont], "roots": [dict(goal=["approved", r], sides=res[r][2]) for r in cont]}, len(mem)

    # ---- claims: defeasible facts with superiority (explicit, R313 authority, later same asserter)
    def in_force(self, c, d):
        return iso(c["valid_from"]) <= d and (c.get("valid_to") is None or d <= iso(c["valid_to"]))

    def sup(self, a, b, r313=True):
        A, B = self.claims[a], self.claims[b]
        lit = plain(A["assertion"]); pred = lit[1][0] if lit[0] == "neg" else lit[0]
        order = ["finance", "hr"]
        if r313 and pred == "cost_centre_of" and kw(A["asserted_by"]) in order and kw(B["asserted_by"]) in order \
                and A["asserted_by"] != B["asserted_by"]:
            return order.index(kw(A["asserted_by"])) < order.index(kw(B["asserted_by"]))
        return A["asserted_by"] == B["asserted_by"] and iso(A["asserted_at"]) > iso(B["asserted_at"])

    def competes(self, l1, l2):
        if l1[0] == "neg" or l2[0] == "neg":
            return (l1[0] == "neg") != (l2[0] == "neg") and (l1[1] if l1[0] == "neg" else l1) == (l2[1] if l2[0] == "neg" else l2)
        return l1[0] == l2[0] == "cost_centre_of" and l1[1] == l2[1] and l1[2] != l2[2]

    def literal(self, lit, d, r313=True):
        """Team defeat over in-force claims (no rule bodies, so blocking and propagation coincide). -> (status, supporters, blockers)
        status: proven | rebutted (a blocker is superior to every supporter) | contested | none"""
        live = [i for i, c in self.claims.items() if self.in_force(c, d)]
        S = [i for i in live if plain(self.claims[i]["assertion"]) == lit]
        A = [i for i in live if self.competes(plain(self.claims[i]["assertion"]), lit)]
        if not S:
            return "none", [], A
        blockers = [a for a in A if not any(self.sup(s, a, r313) for s in S)]
        if not blockers:
            return "proven", S, []
        if all(any(self.sup(a, s, r313) for a in blockers) for s in S):   # team: each supporter beaten by some blocker
            return "rebutted", S, blockers
        return "contested", S, blockers

    def cost_centre_of(self, e, d, r313=True):
        vals = sorted({plain(c["assertion"])[2] for c in self.claims.values()
                       if plain(c["assertion"])[:2] == ["cost_centre_of", e] and self.in_force(c, d)})
        res = {v: self.literal(["cost_centre_of", e, v], d, r313) for v in vals}
        won = [v for v, (st, _, _) in res.items() if st == "proven"]
        if won:
            return "ANSWER", won[0], None, res[won[0]][1]
        sides = sorted(sorted(s) for v, (st, s, _) in res.items() if s)
        return "CONFLICT", None, sides, [i for s in sides for i in s]

    def standing(self, cid, d):
        c = self.claims[cid]
        st, S, B = self.literal(plain(c["assertion"]), d)
        if not self.in_force(c, d):
            return dict(standing="not_in_force", defeater=None, qualifier=[], core=[cid])
        if st == "rebutted":
            dft = sorted(a for a in B if any(self.sup(a, s) for s in S))[0]
            return dict(standing="rebutted", defeater=dft, qualifier=[], core=[cid, dft])
        if st == "contested":
            return dict(standing="contested", defeater=None, qualifier=[], core=[cid] + B)
        qual, core = [], [cid]
        links = [(m, "required") for m in c.get("depends_on") or []] + [(m, "supporting") for m in c.get("supports") or []]
        for sid, role in links:
            r = self.standing(sid, d)
            if r["standing"] in ("holds", "holds_with_qualifier"):
                continue
            if role == "required" and r["standing"] == "contested":   # propagation (SEMANTICS.md): a contested member contests the parent
                return dict(standing="contested", defeater=None, qualifier=[], core=[cid] + r["core"])
            if role == "required":
                return dict(standing="rebutted", defeater=r["defeater"], qualifier=[], core=[cid, sid] + ([r["defeater"]] if r["defeater"] else []))
            qual.append(sid); core += [sid] + ([r["defeater"]] if r["defeater"] else [])
        return dict(standing="holds_with_qualifier" if qual else "holds", defeater=None, qualifier=sorted(qual), core=core)

    # ---- vocabulary
    def resolve_term(self, text):
        norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("_", " "))).strip()
        t = norm(text)
        hits = [x for x in self.S["terms"] if t == norm(x["label"]) or t in [norm(s) for s in x.get("synonyms") or []]]
        cands = sorted({c for x in hits for c in (plain(x["see"]) if x.get("see") else [x["id"]])})
        return dict(status="none" if not cands else "concept" if len(cands) == 1 else "several", candidates=cands)


CLOSED = "total over known facts in declared scope"


def answer(R, q):
    """The key for question q (plain dict) in reference R; every decide and why_not key states the qualifier
    (None when there is none: a missing field must never be read as not qualified, PLAN-v3-bench-full §3b′)."""
    k = answer1(R, q)
    if q["kind"] in ("decide", "why_not"):
        k["qualifier"] = qualifier(R, q, k)
    return k


def qualifier(R, q, k):
    """SEMANTICS.md, Qualifier (IR-005, amended 2026-11-25): CLOSED when the ANSWER rests on absence and the
    absence is not covered (derived coverage, coverage() below)."""
    if k["status"] != "ANSWER":
        return None
    h = q.get("hypothesis") or {}
    cov = Coverage(R, q.get("as_of") or R.today, h.get("withhold") or (), plain(list(E.loads(h["add"]))) if h.get("add") else [])
    closed = {kw(r["id"]) for r in R.S["rules"] if kw(r.get("closed_over")) == "known_facts"}
    open_closed = {i for i in closed if not cov.rule(i)}
    g = q["goal"]
    if k["value"] not in (False, None, []):
        return CLOSED if set(k["core"]) & open_closed else None
    return None if cov.pred(g[0]) else CLOSED if absent(R, g, k["value"], open_closed) else None


# Coverage (SEMANTICS.md, Qualifier), read from the rule docs, not from the rule bodies: per predicate, the rules
# that conclude or attack it, and what each one reads: ("f", concept) a fetch, ("p", predicate) a derived
# literal or the [:not] of one. Builtins and as_of are always covered and are left out.
F, P = (lambda c: ("f", c)), (lambda c: ("p", c))
DEPS = {
    "booked_total": {"R104": [F("booked_total")]},
    "headroom": {"R105": [P("booked_total"), F("cost_centre")]},
    "cap_breach": {"R106": [F("request"), F("employee"), F("ancestors_or_self"), P("booked_total"), F("cost_centre")]},
    "breach_in": {"R110": [F("request_in_subtree"), P("cap_breach")]},
    "approved_total": {"R120": [F("request_in_subtree"), P("approved")]},
    "approved_count": {"R121": [F("request_in_subtree"), P("approved")]},
    "big_capital": {"R112": [F("request")]},
    "role_limit": {"R201": [P("limit_on")]},
    "limit_on": {"R202": [F("role_limit_version")]},
    "governing_limit": {"R203": [F("request"), P("limit_on")]},
    "vendor_status_for": {"R204": [F("request"), F("vendor_status")]},
    "has_approver": {"R301": [F("request"), F("reporting_chain"), P("governing_limit")]},
    "cap_ok": {"R304": [P("cap_breach")]},
    "vendor_cleared": {"R305": [P("vendor_status_for")], "R306": [F("request"), P("vendor_status_for")],
                       "R307": [F("request"), P("vendor_status_for"), P("big_capital")]},     # R307: extension defeater
    "eligible": {"R308": [P("has_approver"), P("cap_ok"), P("vendor_cleared")]},
    "denied": {"R309": [F("request"), F("employee")]},
    "approved": {"R310": [P("eligible"), P("denied")], "R312": [P("auto_approved")], "R314": [P("denied")]},
    "auto_approved": {"R311": [F("request")]},
    "home_headroom": {"R315": [P("cost_centre_of"), P("headroom")]},
    "po_issued": {"R316": [P("approved")]},
}
RULE_DEPS = {i: ds for rs in DEPS.values() for i, ds in rs.items()}


class Coverage:
    """A name is covered by an in-force [:complete "N"] claim, or (a predicate) when no claim asserts it or its
    complement and every present, unwithheld rule that concludes or attacks it reads only covered names."""
    def __init__(self, R, d, withhold, added):
        self.R, self.withhold = R, set(withhold)
        claims = [c for c in list(R.claims.values()) + [x for x in added if "assertion" in x] if c["id"] not in self.withhold]
        self.complete = {plain(c["assertion"])[1] for c in claims
                         if plain(c["assertion"])[0] == "complete" and R.in_force(c, d)}
        self.fed = {(a[1][0] if a[0] == "neg" else a[0]) for a in (plain(c["assertion"]) for c in claims)}

    def rules(self, p):
        return {i: ds for i, ds in DEPS.get(p, {}).items() if i not in self.withhold and (i != "R307" or self.R.has_R307)}

    def pred(self, p, path=()):
        if p in self.complete: return True
        if p in path: return True                      # positive recursion adds no gap (none in the slice)
        rs = self.rules(p)
        return bool(rs) and p not in self.fed and all(self.deps(ds, path + (p,)) for ds in rs.values())

    def deps(self, ds, path=()):
        return all(n in self.complete if t == "f" else self.pred(n, path) for t, n in ds)

    def rule(self, rid):
        return self.deps(RULE_DEPS[rid])


def absent(R, g, v, closed):
    """A negative value rests on absence: open null/[] always; a ground false when no supporter was live,
    or when the defeater that refutes it is an uncovered :closed_over rule. Reasoned per predicate from the rule docs."""
    if v is not False:
        return True                                    # open: no binding is known
    p = g[0]
    if p == "approved":                                # R310 needs [:not denied], so R314 never meets a live R310,
        return True                                    # and a live R312 gives true or CONFLICT: false is none
    if p in ("denied", "cap_breach"):                  # R309 / R106 is the only supporter; nothing attacks it
        return True
    if p == "po_issued":                               # R316 is the only supporter; false means approved is refuted
        return True
    if p == "vendor_cleared":                          # none: neither R305 nor R306 live; else defeated by R307
        _, _, dft = R.vendor_cleared(g[1])
        return dft is None or dft in closed
    raise AssertionError(f"absence of a false {p} not reasoned in the reference")


def summary(R, q):
    """summary op (PLAN-v3-bench-full §2): the status of each instance of [p ?r] over a request domain, from the same
    per-request functions as the decide keys. Domains: a list of ids, or the pending requests of a subtree."""
    p, (var,) = q["goal"][0], [x for x in q["goal"][1:] if isinstance(x, str) and x.startswith("?")]
    dom = q["filters"][var]
    if isinstance(dom, list):
        rs = sorted(dom)
    else:
        assert dom["concept"] == "request_in_subtree" and dom["filters"].get("status") == "pending", dom
        rs = _pending(R, dom["filters"]["root"])
    def status(r):                                 # -> (proven | refuted | contested, root or None)
        if p in ("approved", "po_issued"):         # R316: po_issued follows approved, contested through it
            st, v, sides = R.approved(r)
            return ("contested", (["approved", r], sides)) if st == "CONFLICT" else ("proven" if v else "refuted", None)
        v = {"vendor_cleared": lambda r: R.vendor_cleared(r)[0], "cap_breach": R.cap_breach, "denied": R.denied}[p](r)
        return ("proven" if v else "refuted"), None
    res = {r: status(r) for r in rs}
    roots = {}
    for st, root in res.values():
        if root: roots[json.dumps(root)] = roots.get(json.dumps(root), 0) + 1
    rl = sorted(({"goal": json.loads(g)[0], "sides": json.loads(g)[1], "instances": n} for g, n in roots.items()),
                key=lambda x: (-x["instances"], json.dumps(x["goal"])))
    by = {s: [r for r in rs if res[r][0] == s] for s in ("proven", "refuted", "contested")}
    return dict(status="ANSWER", instances=len(rs), counts={s: len(v) for s, v in by.items()},
                contested_roots=rl[:20], contested_roots_total=len(rl), sample={s: v[:10] for s, v in by.items()})


def answer1(R, q):
    k, g, d = q["kind"], q.get("goal"), q.get("as_of") or R.today
    A = lambda v, core: dict(status="ANSWER", value=v, sides=None, core=core)
    if k == "fetch":
        assert q["concept"] in ("pending_exposure", "booked_total")
        if q["concept"] == "booked_total":
            return dict(value=R.booked_total(q["filters"]["cc"]), row_count=1, core=[])
        sub = set(R.subtree(q["filters"]["cc"]))
        v = sum(x["amount"] for x in R.req.values() if x["status"] == "pending" and R.emp[x["requester"]]["cc"] in sub)
        return dict(value=v, row_count=1, core=[])
    if k == "resolve_term":
        return R.resolve_term(q["text"])
    if k == "claim":
        return R.standing(q["claim"], d)
    if k == "summary":
        return summary(R, q)
    p = g[0]
    if k == "why_not":
        assert p == "approved"
        r = g[1]; st, v, _ = R.approved(r); assert st == "ANSWER" and v is False
        failed, core = [], ["R310", "R312"]
        if not R.has_approver(r): failed.append(["has_approver", r])
        if R.cap_breach(r): failed.append(["cap_ok", r])
        vc, _, dft = R.vendor_cleared(r)
        if not vc:
            failed.append(["vendor_cleared", r]); core += ["R305", "R306"] + ([dft] if dft else [])
        if failed: failed.insert(0, ["eligible", r]); core.append("R308")
        if R.denied(r): failed.append(["denied", r])      # shown as the NAF condition that failed
        if not R.auto_approved(r): failed.append(["auto_approved", r]); core.append("R311")
        return dict(status="ANSWER", value=False, failed=failed, core=sorted(set(core)))
    if p == "booked_total": return A(R.booked_total(g[1]), ["R104"])     # R104 names completeness C10
    if p == "headroom": return A(R.headroom(g[1]), ["R105", "R104"])
    if p == "role_limit": return A(R.limit_on(g[1], d), ["R201", "R202"])
    if p == "governing_limit": return A(R.limit_on(g[2], R.req[g[1]]["date"]), ["R203", "R202"])
    if p == "vendor_cleared":
        v, s, dft = R.vendor_cleared(g[1])
        return A(v, [s, "R204"] if s else [dft] if dft else ["R305", "R306"])
    if p == "approved":
        st, v, sides = R.approved(g[1])
        if st == "CONFLICT": return dict(status=st, value=None, sides=sides, core=sorted({i for s in sides for i in s}))
        return A(v, ["R310", "R308", "R301", "R304", "R305"] if v else ["R310", "R312"])
    if p == "cost_centre_of":
        r313 = "R313" not in ((q.get("hypothesis") or {}).get("withhold") or [])
        st, v, sides, core = R.cost_centre_of(g[1], d, r313)
        core = sorted(set(core + (["R313"] if r313 and st == "ANSWER" and d < "2026-08-01" else [])))
        return dict(status=st, value=v, sides=sides, core=core)
    if p == "home_headroom":                           # R315: open goal, one instance per claimed cost centre
        r313 = "R313" not in ((q.get("hypothesis") or {}).get("withhold") or [])
        st, v, sides, core = R.cost_centre_of(g[1], d, r313)
        if st == "ANSWER": return A([R.headroom(v)], ["R315", "R105"])
        cont = {}
        for c in sorted({plain(x["assertion"])[2] for x in R.claims.values()
                         if plain(x["assertion"])[:2] == ["cost_centre_of", g[1]] and R.in_force(x, d)}):
            L = ["cost_centre_of", g[1], c]
            assert R.literal(L, d, r313)[0] == "contested"
            cont[json.dumps(["home_headroom", g[1], R.headroom(c)])] = dict(
                via=[L], rules=["R315"], roots=[dict(goal=L, sides=sides)])
        return dict(status=st, value=None, sides=sides, core=sorted(set(core) | {"R315"}), contested=cont)
    if p == "po_issued":                               # R316: downstream of approved
        st, v, sides = R.approved(g[1])
        if st == "ANSWER": return A(v, ["R316", "R310", "R308", "R304"] if v else ["R316"])
        return dict(status=st, value=None, sides=sides, core=sorted({"R316"} | {i for sd in sides for i in sd}),
                    contested={json.dumps(["po_issued", g[1]]): dict(
                        via=[["approved", g[1]]], rules=["R316"], roots=[dict(goal=["approved", g[1]], sides=sides)])})
    if p == "breach_in": return A(R.breach_in(g[1]), ["R110", "R106"])
    if p == "denied": return A(R.denied(g[1]), ["R309"])
    if p == "cap_breach": return A(R.cap_breach(g[1]), ["R106"])
    if p in ("approved_total", "approved_count"):
        rid = {"approved_total": "R120", "approved_count": "R121"}[p]
        st, v, sides, c, n = R.approved_agg(g[1], "sum" if p == "approved_total" else "count")
        if st == "ANSWER": return dict(A(v, [rid]), agg_count=n)   # the aggregate node's count (HISTORY phase 8)
        return dict(status=st, value=None, sides=sides, core=sorted({rid} | {i for sd in sides for i in sd}),
                    contested={json.dumps([p, g[1], v]): dict(via=c["via"], rules=[rid], roots=c["roots"])})
    terms = {x["id"] for x in R.S["terms"]}
    if f"term:{p}" in terms: return dict(status="UNDERDETERMINED", value=None, sides=None, core=[])
    return dict(status="OUT_OF_SCOPE", value=None, sides=None, core=[])


# ---------------------------------------------------------------------------- disputes (cycles-acyclic.edn)
def neg(L):
    return L[1] if L[0] == "neg" else ["neg", L]


# ---------------------------------------------------------------------------- ambiguity propagation
PROVEN, REFUTED, CONTESTED = "proven", "refuted", "contested"
AUTH = {"watchlisted": ("RY4", ["risk", "compliance"]), "cost_centre_of": ("R313", ["finance", "hr"])}


def pos(b):
    """A body literal's derived literal: [:not L] -> L."""
    return b[1] if b[0] == "not" else b


class Prop:
    """Ambiguity propagation (SEMANTICS.md) over the acyclic dispute theory of cycles-acyclic.edn plus
    the slice's claims, grounded by hand. A ground rule: (id, kind, head, body literals). Bodies list
    only derived literals and [:not L]; fetches, builtins and as_of are decided here in Python.
    Each literal is proven, refuted or contested; memoised top-down (the theory is acyclic)."""

    def __init__(self, R, d, withhold=()):
        self.R, self.d = R, d
        present = {y["id"] for y in R.cyc_recs}
        V = sorted({v for v, *_ in R.vstat})
        ok = lambda v: any(x == v and s == "approved" and f <= d <= t for x, s, f, t in R.vstat)
        sus = lambda v: any(x == v and s == "suspended" for x, s, *_ in R.vstat)
        rules = []
        for v in V:
            rules += [("RY21", "defeasible", ["preferred", v], [], ok(v)),
                      ("RY22", "defeasible", ["under_review", v], [], sus(v)),
                      ("RY23", "defeater", ["neg", ["preferred", v]], [["under_review", v]], True),
                      ("RY51", "defeasible", ["flagged", v], [["blacklisted", v]], True),
                      ("RY53", "defeasible", ["cleared_for_tender", v], [["onboarded", v]], True),
                      ("RY54", "defeater", ["neg", ["cleared_for_tender", v]], [["blacklisted", v]], True),
                      ("RY55", "defeasible", ["screening_clear", v], [["not", ["blacklisted", v]]], True)]
        claims = list(R.cyc_claims) + list(R.claims.values())
        self.claims = {c["id"]: c for c in claims}
        for c in claims:
            rules.append((c["id"], "claim", plain(c["assertion"]), [["claim_dep", m] for m in c.get("depends_on") or []],
                          R.in_force(c, d)))
        # RY56: home_budget(e, v) :- cost_centre_of(e, c), fetch booked_total(c) = v; one instance per claimed (e, c)
        for e, c in sorted({tuple(plain(x["assertion"])[1:]) for x in claims if plain(x["assertion"])[0] == "cost_centre_of"}):
            rules.append(("RY56", "defeasible", ["home_budget", e, R.booked_total(c)], [["cost_centre_of", e, c]], True))
        self.rules = [r[:4] for r in rules if r[4] and r[0] not in withhold and (r[0] in present or r[0] in R.claims)]
        self.auth = {p: o for p, (rid, o) in AUTH.items() if rid not in withhold and (rid in present or rid == "R313")}
        self.memo = {}

    # ---- structure
    def sup(self, t, s):
        """t > s: authority (RY4, R313) or later asserted_at by the same asserter, between claims only."""
        if t[1] != "claim" or s[1] != "claim": return False
        A, B = self.claims[t[0]], self.claims[s[0]]
        pred = t[2][1][0] if t[2][0] == "neg" else t[2][0]
        o = self.auth.get(pred)
        a, b = kw(A["asserted_by"]), kw(B["asserted_by"])
        if o and a in o and b in o and a != b:
            return o.index(a) < o.index(b)
        return a == b and iso(A["asserted_at"]) > iso(B["asserted_at"])

    def supporters(self, L):
        return [r for r in self.rules if r[2] == L and r[1] != "defeater"]

    def attackers(self, L):
        """Head ~L, or a functional rival (cost_centre_of with the same employee, another cost centre)."""
        rival = lambda h: L[0] == h[0] == "cost_centre_of" and L[1] == h[1] and L[2] != h[2]
        return [r for r in self.rules if r[2] == neg(L) or rival(r[2])]

    # ---- values
    def val(self, b):
        if b[0] == "not":
            return {PROVEN: REFUTED, REFUTED: PROVEN, CONTESTED: CONTESTED}[self.val(b[1])]
        if b[0] == "claim_dep":                       # depends_on: the member claim holds
            c = next(r for r in self.rules if r[0] == b[1]) if any(r[0] == b[1] for r in self.rules) else None
            return self.val(c[2]) if c else REFUTED
        k = json.dumps(b)
        if k not in self.memo:
            self.memo[k] = None                       # acyclic: never re-entered
            self.memo[k] = self.compute(b)
        assert self.memo[k] is not None, f"re-entered {b}"
        return self.memo[k]

    def body(self, r):
        vs = [self.val(b) for b in r[3]]
        return REFUTED if REFUTED in vs else PROVEN if all(v == PROVEN for v in vs) else CONTESTED

    def live(self, r):
        return self.body(r) != REFUTED

    def beaten(self, a, L):
        return any(self.sup(t, a) and self.body(t) == PROVEN for t in self.supporters(L) if self.live(t))

    def compute(self, L):
        S = [r for r in self.supporters(L) if self.live(r)]
        A = [a for a in self.attackers(L) if self.live(a)]
        if all(any(self.body(a) == PROVEN and self.sup(a, t) for a in A) for t in S):   # -sigma; vacuous if no S
            return REFUTED
        if any(self.body(t) == PROVEN for t in S) and all(self.beaten(a, L) for a in A):
            return PROVEN
        return CONTESTED

    # ---- explanation of a contested literal
    def explain(self, L):
        """-> ("root", sides) when a proven-bodied supporter meets a proven-bodied unbeaten attacker;
        else ("via", rules, contested body literals) over the live supporters and live unbeaten attackers."""
        S = [r for r in self.supporters(L) if self.live(r)]
        A = [a for a in self.attackers(L) if self.live(a) and not self.beaten(a, L)]
        Sp, Ap = [r for r in S if self.body(r) == PROVEN], [a for a in A if self.body(a) == PROVEN]
        if Sp and Ap:
            return "root", sorted([sorted({r[0] for r in Sp}), sorted({a[0] for a in Ap})])
        via = [pos(b) for r in S + A for b in r[3] if b[0] != "claim_dep" and self.val(b) == CONTESTED]
        via += [self.rule_of(b[1])[2] for r in S + A for b in r[3] if b[0] == "claim_dep" and self.val(b) == CONTESTED]
        return "via", sorted({r[0] for r in S + A}), via

    def rule_of(self, rid):
        return next(r for r in self.rules if r[0] == rid)

    def contested(self, G):
        """-> {via, rules, roots: [{goal, sides}]} for a downstream-contested G, or None when G is itself a root."""
        if self.explain(G)[0] == "root":
            return None
        via, rules, roots, seen, st = {}, set(), {}, set(), [G]
        while st:
            x = st.pop(); k = json.dumps(x)
            if k in seen: continue
            seen.add(k)
            e = self.explain(x)
            if e[0] == "root":
                roots[k] = dict(goal=x, sides=e[1])
            else:
                rules |= set(e[1])
                for b in e[2]:
                    via[json.dumps(b)] = b; st.append(b)
        return dict(via=[via[k] for k in sorted(via)], rules=sorted(rules), roots=[roots[k] for k in sorted(roots)])

    def answer(self, G):
        v = self.val(G)
        if v == PROVEN:
            win = sorted({r[0] for r in self.supporters(G) if self.body(r) == PROVEN})
            A = [a for a in self.attackers(G) if self.live(a)]
            src = AUTH.get(G[1][0] if G[0] == "neg" else G[0])
            src = [src[0]] if src and A and self.auth.get(G[0]) and any(
                a[1] == "claim" and kw(self.claims[a[0]]["asserted_by"]) in self.auth[G[0]] for a in A) else []
            return dict(status="ANSWER", value=True, sides=None, core=sorted(win + src))
        if v == REFUTED:
            return dict(status="ANSWER", value=False, sides=None, core=sorted({r[0] for r in self.supporters(G)}))
        return self.conflict({json.dumps(G): G})

    def conflict(self, inst):
        """CONFLICT key for contested ground instances {json: goal}: root sides, or the roots' sides."""
        sides, core, cmap = [], set(), {}
        for k in sorted(inst):
            G = inst[k]; c = self.contested(G)
            if c is None:
                sd = self.explain(G)[1]
            else:
                cmap[k] = c; core |= set(c["rules"])
                sd = [s for r in c["roots"] for s in r["sides"]]
            for s in sd:
                core |= set(s)
                if s not in sides: sides.append(s)
        k = dict(status="CONFLICT", value=None, sides=sorted(sides), core=sorted(core))
        if cmap: k["contested"] = cmap
        return k


def answer_acyclic(R, q):
    k = answer_acyclic1(R, q)
    if k["status"] != "ANSWER":
        k["qualifier"] = None
    elif k["value"] in (False, None, []):              # open [] (no RY56 instance proven): absence; false: not reasoned
        assert k["value"] == [], "a false in the acyclic theory: absence not reasoned in the reference"
        k["qualifier"] = CLOSED
    else:                                              # RY55 is the one :closed_over rule of the theory
        k["qualifier"] = CLOSED if "RY55" in k["core"] else None
    return k


def answer_acyclic1(R, q):
    w = tuple((q.get("hypothesis") or {}).get("withhold") or ())
    d, g = q.get("as_of") or R.today, q["goal"]
    P = Prop(R, d, w)
    if g[0] == "home_budget":                          # open goal [:home_budget e ?v]: one RY56 instance per claimed cc
        inst = {json.dumps(r[2]): r[2] for r in P.rules if r[0] == "RY56" and r[2][1] == g[1]}
        vals = {k: P.val(G) for k, G in inst.items()}
        if CONTESTED in vals.values():                 # a measure over a contested binding is contested
            return P.conflict({k: inst[k] for k, v in vals.items() if v == CONTESTED})
        won = sorted(inst[k][2] for k, v in vals.items() if v == PROVEN)
        return dict(status="ANSWER", value=won, sides=None, core=["RY56"] if won else [])
    return P.answer(g)


def load(cycles=False):
    """-> slice, extension, questions (base / extended list; with cycles=True also the records of
    cycles-acyclic.edn and the :state :acyclic questions)."""
    S = plain(E.loads((HERE / "slice.edn").read_text()))
    X = plain(list(E.loads((HERE / "extension.edn").read_text())))
    QA = plain(list(E.loads((HERE / "questions.edn").read_text())))
    Q = [q for q in QA if q.get("state") != "acyclic"]
    if not cycles:
        return S, X, Q
    Y = plain(list(E.loads((HERE / "cycles-acyclic.edn").read_text())))
    return S, X, Q, Y, [q for q in QA if q.get("state") == "acyclic"]


def keys(mutate=False):
    S, X, Q, Y, QC = load(cycles=True)
    out = {}
    for state, ext in (("base", []), ("extended", X)):
        R = Ref(S, ext, mutate)
        out[state] = {q["id"]: answer(R, q) for q in Q}
    out["changed"] = sorted(i for i in out["base"] if out["base"][i] != out["extended"][i])
    R = Ref(S, X, mutate)
    R.cyc_claims, R.cyc_recs = [y for y in Y if "assertion" in y], Y
    out["acyclic"] = {q["id"]: answer_acyclic(R, q) for q in QC}
    return out


# ---------------------------------------------------------------------------- benchmark families (PLAN-v3-bench §2)
# Hand-written from the documented meaning of each family: the parameters in bench/bases/N*.params.json, which
# bench/gen.py writes beside the rule docs; never from the EDN. The slice reference answers the slice predicates the
# families read (vendor_cleared). Generated predicates are never covered (the request concept is not complete), so a
# false is CLOSED exactly when no supporter of the instance was live (SEMANTICS.md, Qualifier).
class Bench(Ref):
    def __init__(self, S, X, params, claims):
        super().__init__(S, X)
        self.B = params
        for c in claims:
            self.claims[c["id"]] = c
        import duckdb
        con = duckdb.connect(str(HERE / "slice.duckdb"), read_only=True)
        self.unit = dict(con.execute("SELECT id, org_unit FROM cc").fetchall())
        self.prog = {p["code"]: p for p in params["programmes"]}
        self.disp = {d["code"]: d for d in params["disputes"]}
        self.dist = {d["code"]: d for d in params["distractor_rules"]}

    def sup(self, a, b, r313=True):                    # one authority order per predicate (the export licence rule)
        o = self.B.get("superiority")
        A, Bc = self.claims[a], self.claims[b]
        lit = plain(A["assertion"]); pred = lit[1][0] if lit[0] == "neg" else lit[0]
        x, y = kw(A["asserted_by"]), kw(Bc["asserted_by"])
        if o and pred == o["pred"] and x != y and x in o["order"] and y in o["order"]:
            return o["order"].index(x) < o["order"].index(y)
        return super().sup(a, b, r313)

    def limit_ok(self, P, r):
        """-> the version that admits r, or None"""
        p, q = self.prog[P], self.req[r]
        return next((v["id"] for v in p["versions"] if q["category"] == p["category"]
                     and v["valid_from"] <= q["date"] <= v["valid_to"] and q["amount"] <= v["limit"]), None)

    def decide(self, g):
        p, A = g[0], lambda v, core, qual=None: dict(status="ANSWER", value=v, sides=None, core=core, qualifier=qual)
        if p in REQUEST_GOALS or p.startswith("u") and p.endswith("_cleared"):
            return BenchProp(self, g[-1]).answer(g)
        if p in ("perk", "centre_tag"):
            d = self.dist[g[1]]
            hit = self.emp[g[2]]["role"] == d["role"] if p == "perk" else self.unit[g[2]] == d["org_unit"]
            return A(True, [d["id"]]) if hit else A(False, [d["id"]], CLOSED)
        st, S_, B_ = self.literal(g, self.today)               # claims-only predicates
        if st == "proven": return A(True, S_)
        if st == "rebutted": return A(False, B_)
        if st == "contested": return dict(status="CONFLICT", value=None, sides=sorted([sorted(S_), sorted(B_)]), core=S_ + B_, qualifier=None)
        return A(False, [], CLOSED)

    def answer(self, q):
        if q["kind"] == "claim":
            return self.standing(q["claim"], q.get("as_of") or self.today)
        return self.decide(q["goal"])


REQUEST_GOALS = ("programme_limit_ok", "programme_cleared", "capitalised")


class BenchProp(Prop):
    """Ambiguity propagation over the request-level families of a generated base (programme limits and clearance,
    capitalisation disputes, P01's sub-programme chain), grounded by hand for one request r from params.json,
    never from the EDN. A ground rule is kept when its fact conditions hold; superiority is params["superior"].
    vendor_cleared is the slice's (Ref.vendor_cleared), entered as its deciding rule."""

    def __init__(self, B, r):
        self.R, self.d, self.claims, self.auth, self.memo = B, B.today, {}, {}, {}
        q, P = B.req[r], B.B
        em, amt, cat = q["emergency"], q["amount"], q["category"]
        rules = []                                                   # (id, kind, head, body, facts hold)
        ok, s, x = B.vendor_cleared(r)
        if ok: rules.append((s, "defeasible", ["vendor_cleared", r], [], True))
        if x: rules.append((x, "defeater", ["neg", ["vendor_cleared", r]], [], True))
        for p in P["programmes"]:
            c, lim, cl = p["code"], ["programme_limit_ok", p["code"], r], ["programme_cleared", p["code"], r]
            for v in p["versions"]:
                rules.append((v["id"], "defeasible", lim, [], cat == p["category"] and v["valid_from"] <= q["date"] <= v["valid_to"]
                              and amt <= v["limit"]))
            k = p["clearance"]
            if not k: continue
            rules.append((k["base"], "defeasible", cl, [lim, ["vendor_cleared", r]], True))
            if k["exception"]:
                ev = q["vendor"] == k["exception"]["vendor"]
                rules.append((k["exception"]["id"], "defeater", ["neg", cl], [], ev))
                if k["counter"]:
                    rules.append((k["counter"]["id"], "defeasible", cl, [lim], ev and em))
        for d in P["disputes"]:
            h, here = ["capitalised", d["category"], r], cat == d["category"]
            rules += [(d["for"]["id"], "defeasible", h, [], here and amt >= d["for"]["min"]),
                      (d["against"]["id"], "defeater", ["neg", h], [], here and amt < d["against"]["below"])]
        head = lambda c: ["programme_cleared", "P01", r] if c == "P01" else [f"u{c[1:]}_cleared", r]
        for L in P.get("chain", []):
            h = head(L["code"])
            rules.append((L["base"]["id"], "defeasible", h, [head(L["parent"])]
                          + ([["capitalised", B.prog["P01"]["category"], r]] if L["base"]["capitalised"] else []), True))
            if L["exception"]:
                rules += [(L["exception"]["id"], "defeater", ["neg", h], [], em),
                          (L["counter"]["id"], "defeasible", h, [head("P01")], em and amt <= L["counter"]["max"])]
        self.all = [x[:4] for x in rules]
        self.rules = [x[:4] for x in rules if x[4]]
        self.over = {tuple(x) for x in P["superior"]}

    def sup(self, t, s):
        return (t[0], s[0]) in self.over

    def path(self, L):
        """the rules that prove L: its proven supporters no proven-bodied live attacker overrules, and their body's paths"""
        A = [a for a in self.attackers(L) if self.live(a) and self.body(a) == PROVEN]
        out = []
        for t in self.supporters(L):
            if self.body(t) == PROVEN and not any(self.sup(a, t) for a in A):
                out += [t[0]] + [i for b in t[3] if b[0] != "not" for i in self.path(b)]
        return list(dict.fromkeys(out))

    def answer(self, G):
        v = self.val(G)
        if v == PROVEN:
            return dict(status="ANSWER", value=True, sides=None, core=sorted(set(self.path(G))), qualifier=None)
        if v == REFUTED:
            S = [t for t in self.supporters(G) if self.live(t)]
            if not S:                                                # nothing supports G: closed over the known facts
                return dict(status="ANSWER", value=False, sides=None, qualifier=CLOSED,
                            core=sorted({x[0] for x in self.all if x[2] == G and x[1] != "defeater"}))
            A = [a for a in self.attackers(G) if self.live(a) and self.body(a) == PROVEN and any(self.sup(a, t) for t in S)]
            return dict(status="ANSWER", value=False, sides=None, core=sorted({a[0] for a in A}), qualifier=None)
        k = self.conflict({json.dumps(G): G}); k["qualifier"] = None
        return k


def bench_ref(stem):
    """the family oracle for one base: bench/bases/N*.params.json + the base's claims"""
    stem = pathlib.Path(stem)
    S, X, _ = load()
    base = plain(E.loads(stem.with_suffix(".edn").read_text()))
    ours = {c["id"] for c in S["claims"]}
    return Bench(S, X, json.loads(stem.with_suffix(".params.json").read_text()), [c for c in base["claims"] if c["id"] not in ours])


def bench_keys(stem):
    """bench/bases/N*.{params,questions}.json + the base's claims -> keys per question"""
    R = bench_ref(stem)
    return {q["id"]: R.answer(q) for q in json.loads(pathlib.Path(stem).with_suffix(".questions.json").read_text())}


# ---------------------------------------------------------------------------- analyst task components (PLAN-v3-bench §4)
# The checkable values of a task's worked example (bench/tasks/A*.json "checks"), from the same hand-written functions
# as the question keys. Requests count for their requester's centre in the emp table, as in R120 (approved_agg).
# A "naive" entry is the value a known wrong design produces, so the scorer can tell wrong from missed.
def _pending(R, c, until=None):
    sub = set(R.subtree(c))
    return sorted(r for r, q in R.req.items() if q["status"] == "pending" and R.emp[q["requester"]]["cc"] in sub
                  and (until is None or q["date"] <= until))


def _outcomes(R, c):
    rs = _pending(R, c)
    res = {r: R.approved(r) for r in rs}
    cnt = lambda st, v=None: sum(1 for x in res.values() if x[0] == st and (v is None or x[1] is v))
    return dict(pending=len(rs), approved=cnt("ANSWER", True), not_approved=cnt("ANSWER", False), contested=cnt("CONFLICT"),
                auto_approved=sum(1 for r in rs if res[r][0] == "ANSWER" and R.auto_approved(r)))


def _reasons(R, c):
    """reasons per pending request not approved (proven false): several may apply to one request (GR4)"""
    no = [r for r in _pending(R, c) if R.approved(r) == ("ANSWER", False, None)]
    why = {r: [k for k, hit in (("no_approver", not R.has_approver(r)), ("cap_breach", R.cap_breach(r)),
                                ("vendor_not_cleared", not R.vendor_cleared(r)[0]), ("denied", R.denied(r))) if hit] for r in no}
    out = {k: sum(k in v for v in why.values()) for k in ("no_approver", "cap_breach", "vendor_not_cleared", "denied")}
    return dict(not_approved=len(no), **out, several_reasons=sum(len(v) > 1 for v in why.values()))


def _known(R, d):
    """the claims asserted on or before d (what was known at d), on a copy of R"""
    import copy
    K = copy.copy(R)
    K.claims = {i: c for i, c in R.claims.items() if iso(c["asserted_at"]) <= d}
    return K


TASK = {
    "booked_total": lambda R, a, d: R.booked_total(a[0]),
    "headroom": lambda R, a, d: R.headroom(a[0]),
    "headroom_sum": lambda R, a, d: sum(R.headroom(c) for c in a),                  # naive: headroom added across centres
    "pending_exposure": lambda R, a, d: sum(R.req[r]["amount"] for r in _pending(R, a[0])),
    "booked_plus_pending": lambda R, a, d: R.booked_total(a[0]) + sum(R.req[r]["amount"] for r in _pending(R, a[0])),
    "selection_booked_total": lambda R, a, d: sum(R.cc[x]["booked"] for x in set().union(*map(R.subtree, a))),
    "booked_total_sum": lambda R, a, d: sum(R.booked_total(c) for c in a),          # naive: totals added, subtrees overlap
    "breaching_requests": lambda R, a, d: len(R.breach_in(a[0])),
    "own_cap_breaching_requests": lambda R, a, d: sum(                              # naive: own centre's cap only
        1 for r in _pending(R, a[0]) if R.booked_total(R.emp[R.req[r]["requester"]]["cc"]) + R.req[r]["amount"]
        > R.cc[R.emp[R.req[r]["requester"]]["cc"]]["cap"]),
    "approved_total": lambda R, a, d: dict(zip(("status", "value"), R.approved_agg(a[0], "sum")[:2])),
    "request_outcomes": lambda R, a, d: _outcomes(R, a[0]),
    "not_approved_reasons": lambda R, a, d: _reasons(R, a[0]),
    "role_limit": lambda R, a, d: R.limit_on(a[0], d),
    "cost_centre_of": lambda R, a, d: dict(zip(("status", "value", "sides"), R.cost_centre_of(a[0], d)[:3])),
    "vendor_status": lambda R, a, d: next((s for v, s, f, t in R.vstat if v == a[0] and f <= d <= t), None),
    "claim_standing": lambda R, a, d: {k: v for k, v in R.standing(a[0], d).items() if k in ("standing", "defeater", "qualifier")},
    # on a generated base (Bench; a task with by_n, PLAN-v3-bench-full §3b)
    "decide": lambda R, a, d: {k: v for k, v in R.decide(list(a)).items() if k in ("status", "value", "sides")},
    "programme_limit": lambda R, a, d: next(v["limit"] for v in R.prog[a[0]]["versions"]
                                            if v["valid_from"] <= R.req[a[1]]["date"] <= v["valid_to"]),
    "programme_limit_first": lambda R, a, d: R.prog[a[0]]["versions"][0]["limit"],   # naive: one limit all year
    "cleared_count": lambda R, a, d: _cleared(R, a[0], a[1]),
    "cleared_count_no_exception": lambda R, a, d: _cleared(R, a[0], a[1], naive=True),  # naive: base rule only
    # P01's sub-programme chain (§3b′): requests of P01's category by their outcome under goal predicate a[0]
    "chain_count": lambda R, a, d: _chain(R)[a[0]][a[1]],
}


def _chain(R):
    """{predicate: {"cleared", "contested"}} over the requests of P01's category, for P01 and every chain level"""
    if not hasattr(R, "_chain_memo"):
        cat, preds = R.prog["P01"]["category"], ["programme_cleared"] + [L["pred"] for L in R.B["chain"]]
        out = {p: dict(cleared=0, contested=0) for p in preds}
        for r, q in R.req.items():
            if q["category"] != cat: continue
            X = BenchProp(R, r)
            for p in preds:
                v = X.val(["programme_cleared", "P01", r] if p == "programme_cleared" else [p, r])
                if v == PROVEN: out[p]["cleared"] += 1
                elif v == CONTESTED: out[p]["contested"] += 1
        R._chain_memo = out
    return R._chain_memo


def _cleared(R, P, ven, naive=False):
    """requests of the programme's category from vendor ven that are cleared under P (naive: by the base rule alone)"""
    p = R.prog[P]
    rs = [r for r, q in R.req.items() if q["category"] == p["category"] and q["vendor"] == ven]
    if naive:
        return sum(1 for r in rs if R.limit_ok(P, r) and R.vendor_cleared(r)[0])
    return sum(1 for r in rs if R.decide(["programme_cleared", P, r])["value"] is True)


def _check_keys(R, checks):
    out = {}
    for k in checks:
        RR = _known(R, k["known_at"]) if k.get("known_at") else R
        d = k.get("as_of") or k.get("known_at") or R.today
        v = TASK[k["call"][0]](RR, k["call"][1:], d)
        out[k["id"]] = dict(value=v[k["field"]] if k.get("field") else v)
        if k.get("naive"):
            out[k["id"]]["naive"] = TASK[k["naive"][0]](RR, k["naive"][1:], d)
    return out


def task_keys(path):
    """bench/tasks/A*.json -> {check id: {value, naive?}}, per N for a task with by_n (as_of: valid time, default today; known_at: only the claims
    asserted by then; field: one entry of a dict value; naive: the value of the named wrong design)"""
    task = json.loads(pathlib.Path(path).read_text())
    if "by_n" in task:                                  # one variant per generated base: {N: {check id: ...}}
        bases = HERE.parents[2] / "bench/bases"
        return {n: _check_keys(bench_ref(bases / f"N{int(n):03d}"), v["checks"]) for n, v in task["by_n"].items()}
    S, X, _ = load()
    return _check_keys(Ref(S, X), task["checks"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mutate", action="store_true")
    ap.add_argument("--bench", nargs="+", metavar="STEM", help="bench bases (e.g. bench/bases/N050) -> STEM.keys.json")
    ap.add_argument("--tasks", nargs="+", metavar="TASK", help="analyst tasks (bench/tasks/A1.json) -> A1.keys.json")
    a = ap.parse_args()
    if a.tasks:
        for t in a.tasks:
            k = task_keys(t)
            pathlib.Path(t).with_suffix(".keys.json").write_text(json.dumps(k, indent=1, sort_keys=True) + "\n")
            print(t, len(k), "keys")
        sys.exit(0)
    if a.bench:
        for st in a.bench:
            k = bench_keys(st)
            pathlib.Path(st + ".keys.json").write_text(json.dumps(k, indent=1, sort_keys=True) + "\n")
            print(st, len(k), "keys")
        sys.exit(0)
    k = keys(a.mutate)
    if a.mutate:
        json.dump(k, sys.stdout, indent=1, sort_keys=True)
    else:
        (HERE / "keys.json").write_text(json.dumps(k, indent=1, sort_keys=True) + "\n")
        for i, v in k["extended"].items():
            print(i, {x: (y if not isinstance(y, list) or len(y) < 8 else f"[{len(y)} items]") for x, y in v.items()})
        print("changed by the extension:", k["changed"])
        for i, v in k["acyclic"].items():
            print(i, v)
