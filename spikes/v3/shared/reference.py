"""Independent reference for spike v3: the rules' :doc texts and PLAN §3.2 re-implemented by hand in
plain Python over the detail data, without any rule interpreter, the concept bindings, or the spikes.

  python spikes/v3/shared/reference.py               # -> shared/keys.json
  python spikes/v3/shared/reference.py --mutate      # flipped comparisons -> stdout (mutation test)

Reads slice.edn only for constants a reader of the docs would also read (today, claims, terms,
functional predicates); every rule is a Python function below. Data: a full load of DuckDB (the
reference is not System A and may hold the rows).

Key shape per question:
  decide        {status, value, sides, core}          sides: sorted list of sorted id lists, or null
  why_not       {status, value, failed, core}         failed: literals that must be shown as failed
  claim         {standing, defeater, qualifier, core}
  resolve_term  {status, candidates}
`core` lists the rule / claim ids an explanation must contain.
"""
import argparse, datetime, json, pathlib, re, sys
import duckdb, edn_format as E

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
            for s in c.get("subclaims") or []:
                self.claims[s["id"]] = dict(s, parent=c["id"], about=c["about"])
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
        """Team defeat with ambiguity blocking over in-force claims. -> (status, supporters, blockers)
        status: proven | rebutted (a blocker is superior to every supporter) | contested | none"""
        live = [i for i, c in self.claims.items() if self.in_force(c, d)]
        S = [i for i in live if plain(self.claims[i]["assertion"]) == lit]
        A = [i for i in live if self.competes(plain(self.claims[i]["assertion"]), lit)]
        if not S:
            return "none", [], A
        blockers = [a for a in A if not any(self.sup(s, a, r313) for s in S)]
        if not blockers:
            return "proven", S, []
        if any(all(self.sup(a, s, r313) for s in S) for a in blockers):
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
            dft = sorted(a for a in B if all(self.sup(a, s) for s in S))[0]
            return dict(standing="rebutted", defeater=dft, qualifier=[], core=[cid, dft])
        if st == "contested":
            return dict(standing="contested", defeater=None, qualifier=[], core=[cid] + B)
        qual, core = [], [cid]
        for s in c.get("subclaims") or []:
            r = self.standing(s["id"], d)
            if r["standing"] in ("holds", "holds_with_qualifier"):
                continue
            if kw(s["role"]) == "required":
                return dict(standing="rebutted", defeater=r["defeater"], qualifier=[], core=[cid, s["id"]] + ([r["defeater"]] if r["defeater"] else []))
            qual.append(s["id"]); core += [s["id"]] + ([r["defeater"]] if r["defeater"] else [])
        return dict(standing="holds_with_qualifier" if qual else "holds", defeater=None, qualifier=sorted(qual), core=core)

    # ---- vocabulary
    def resolve_term(self, text):
        norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("_", " "))).strip()
        t = norm(text)
        hits = [x for x in self.S["terms"] if t == norm(x["label"]) or t in [norm(s) for s in x.get("synonyms") or []]]
        cands = sorted({c for x in hits for c in (plain(x["see"]) if x.get("see") else [x["id"]])})
        return dict(status="none" if not cands else "concept" if len(cands) == 1 else "several", candidates=cands)


def answer(R, q):
    """The key for question q (plain dict) in reference R."""
    k, g, d = q["kind"], q.get("goal"), q.get("as_of") or R.today
    A = lambda v, core: dict(status="ANSWER", value=v, sides=None, core=core)
    if k == "resolve_term":
        return R.resolve_term(q["text"])
    if k == "claim":
        return R.standing(q["claim"], d)
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
    if p == "booked_total": return A(R.booked_total(g[1]), ["R104"])
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
    if p == "breach_in": return A(R.breach_in(g[1]), ["R110", "R106"])
    terms = {x["id"] for x in R.S["terms"]}
    if f"term:{p}" in terms: return dict(status="UNDERDETERMINED", value=None, sides=None, core=[])
    return dict(status="OUT_OF_SCOPE", value=None, sides=None, core=[])


def load():
    S = plain(E.loads((HERE / "slice.edn").read_text()))
    X = plain(list(E.loads((HERE / "extension.edn").read_text())))
    Q = plain(list(E.loads((HERE / "questions.edn").read_text())))
    return S, X, Q


def keys(mutate=False):
    S, X, Q = load()
    out = {}
    for state, ext in (("base", []), ("extended", X)):
        R = Ref(S, ext, mutate)
        out[state] = {q["id"]: answer(R, q) for q in Q}
    out["changed"] = sorted(i for i in out["base"] if out["base"][i] != out["extended"][i])
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mutate", action="store_true"); a = ap.parse_args()
    k = keys(a.mutate)
    if a.mutate:
        json.dump(k, sys.stdout, indent=1, sort_keys=True)
    else:
        (HERE / "keys.json").write_text(json.dumps(k, indent=1, sort_keys=True) + "\n")
        for i, v in k["extended"].items():
            print(i, {x: (y if not isinstance(y, list) or len(y) < 8 else f"[{len(y)} items]") for x, y in v.items()})
        print("changed by the extension:", k["changed"])
