"""V3e host (PLAN-v3-cycles §3): Python + clingo. Rules are data: EDN records are translated to ASP text when
they are loaded or added (asp.py); every op grounds and solves its own clingo Control.

Per op (World):
  program  = asp.META + functional rivals + the texts of the visible records + asof/1 + goal demand dm/2
  ground   with a context whose @fetch(C, Filters) calls the SQL boundary (V3a's sql.py) for each demanded
           filter set, so only demanded rows are fetched (top-down demand by a magic-set rewrite)
  solve    twice on the same Control, under assumptions active(Id) = not withheld:
             enum_mode cautious -> t_* atoms true in every partial stable model = WFS true
             enum_mode brave    -> p_* atoms in some partial stable model     = WFS not false
  read     the ground skeleton (h/3, ih/2: every head instance with its bindings) from symbolic_atoms
The host then builds statuses and why trees from those truth values, a Python port of V3a's wfs-mode
evaluate/classify/sides (defeasible.pl), decide/claims ops (ops.pl) and explain_not (why.pl).

Hypotheses: withheld ids are assumptions (#external active/1 set false), added records are local to the
op's Control. Every op has its own Control, so concurrent hypotheses need no lock (shared/isolation.py).
"""
import json, os, pathlib, sys, threading, time
from decimal import Decimal

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "v3a-prolog"))
sys.path.insert(0, str(HERE.parent / "shared"))
import clingo  # noqa: E402
from clingo import Function, Number, String  # noqa: E402
import edn_format  # noqa: E402
import sql  # noqa: E402  (V3a's SQL boundary, reused unchanged)
from reference import plain  # noqa: E402  (EDN -> plain Python: keywords to names, #inst to ISO dates)
import asp  # noqa: E402

CMP = ("<", "<=", ">", ">=", "=")
BUILTIN = CMP + ("is", "as_of")


class EngineError(Exception):
    pass


# ------------------------------------------------------------------ terms

def is_var(x):
    return isinstance(x, str) and x.startswith("?")


def same(a, b):
    return isinstance(a, bool) == isinstance(b, bool) and (a is None) == (b is None) and a == b


def walk(t, s):
    while is_var(t) and t in s:
        t = s[t]
    return t


def subst(t, s):
    t = walk(t, s)
    if isinstance(t, list): return [subst(x, s) for x in t]
    if isinstance(t, dict): return {k: subst(v, s) for k, v in t.items()}
    return t


def unify(a, b, s):
    if s is None: return None
    a, b = walk(a, s), walk(b, s)
    if is_var(a):
        return s if a == b else {**s, a: b}
    if is_var(b):
        return {**s, b: a}
    if isinstance(a, list) or isinstance(b, list):
        if not (isinstance(a, list) and isinstance(b, list)) or len(a) != len(b): return None
        for x, y in zip(a, b):
            s = unify(x, y, s)
            if s is None: return None
        return s
    return s if same(a, b) else None


def ground(t):
    if is_var(t): return False
    if isinstance(t, list): return all(ground(x) for x in t)
    if isinstance(t, dict): return all(ground(x) for x in t.values())
    return True


def term_vars(t, out=None):
    out = [] if out is None else out
    if is_var(t):
        if t not in out: out.append(t)
    elif isinstance(t, list):
        for x in t: term_vars(x, out)
    elif isinstance(t, dict):
        for k in sorted(t): term_vars(t[k], out)
    return out


def rename(t, sfx):
    if is_var(t): return t + sfx
    if isinstance(t, list): return [rename(x, sfx) for x in t]
    if isinstance(t, dict): return {k: rename(v, sfx) for k, v in t.items()}
    return t


def json_safe(t):
    """unbound variables -> "?_N" (numbered in order of appearance, as V3a's numbervars)"""
    m = {v: f"?_{i}" for i, v in enumerate(term_vars(t))}
    return subst(t, m)


def okey(x):
    """SWI standard order (numbers < atoms < strings < compound) for the plain forms used here"""
    if isinstance(x, bool) or x is None: return (1, "null" if x is None else str(x).lower())
    if isinstance(x, (int, float)): return (0, x)
    if isinstance(x, str): return (3, x)
    if isinstance(x, list):
        return (4, [(2, x[0]) if i == 0 and isinstance(x[0], str) else okey(y) for i, y in enumerate(x)])
    return (5, str(x))


def ev(t):
    if isinstance(t, list) and t and t[0] in ("+", "-"):
        a, b = ev(t[1]), ev(t[2])
        return a + b if t[0] == "+" else a - b
    if is_var(t): raise EngineError(f"unbound {t} in arithmetic")
    return t


def cmp_holds(op, a, b):
    x, y = ev(a), ev(b)
    if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool) and not isinstance(y, bool):
        return {"<": x < y, "<=": x <= y, ">": x > y, ">=": x >= y, "=": x == y}[op]
    kx, ky = okey(x), okey(y)
    return {"<": kx < ky, "<=": kx <= ky, ">": kx > ky, ">=": kx >= ky, "=": kx == ky}[op]


def pred_of(L):
    return L[1][0] if L[0] == "neg" else L[0]


def k(L):
    return json.dumps(L)


# ------------------------------------------------------------------ Symbols <-> plain

def num(v):
    if not -2**31 <= v < 2**31:
        raise EngineError(f"integer {v} does not fit clingo's 32-bit range")
    return Number(v)


def to_sym(x):
    if isinstance(x, bool): return Function("true" if x else "false")
    if x is None: return Function("null")
    if isinstance(x, int): return num(x)
    if isinstance(x, Decimal) and x == int(x): return num(int(x))
    if isinstance(x, float) and x.is_integer(): return num(int(x))
    if isinstance(x, str): return String(x)
    raise EngineError(f"cannot represent {x!r} in ASP")


def lit_sym(L):
    if L[0] == "neg": return Function("neg", [lit_sym(L[1])])
    return Function(L[0], [to_sym(a) for a in L[1:]])


def from_sym(s):
    t = s.type
    if t == clingo.SymbolType.Number: return s.number
    if t == clingo.SymbolType.String: return s.string
    if t == clingo.SymbolType.Function and not s.arguments:
        return {"true": True, "false": False, "null": None}.get(s.name, s.name)
    if t == clingo.SymbolType.Function and s.name == "":
        return [from_sym(a) for a in s.arguments]
    raise EngineError(f"unexpected symbol {s}")


def lit_py(s):
    if s.name == "neg": return ["neg", lit_py(s.arguments[0])]
    return [s.name] + [from_sym(a) for a in s.arguments]


# ------------------------------------------------------------------ store

def read_edn(text):
    return plain(edn_format.loads(text))


class View:
    """The visible rule / claim set: the session store, or a hypothesis's copy of it."""

    def __init__(self, parent=None):
        self.rules = dict(parent.rules) if parent else {}
        self.claims = dict(parent.claims) if parent else {}       # sub-claims flattened (parent, about)
        self.text = dict(parent.text) if parent else {}
        self.withheld = set(parent.withheld) if parent else set()
        self.meta = parent.meta if parent else None
        self._order = None

    def add(self, recs):
        ids = []
        for r in recs:
            ids.append(r["id"])
            if "assertion" in r:
                self._claim(r, None, r["about"])
            else:
                self.text[r["id"]] = asp.translate_rule(r, self.meta.modes, self.meta.concept_cols)
                self.rules[r["id"]] = r
        self._order = None
        return ids

    def _claim(self, c, parent, about):
        c = dict(c, parent=parent, about=about, role=c.get("role"))
        self.text[c["id"]] = asp.translate_claim(c)
        self.claims[c["id"]] = c
        for s in c.get("subclaims") or []:
            self._claim(s, c["id"], about)

    def active(self, i):
        return i not in self.withheld

    def order(self, i):
        if self._order is None:
            self._order = {x: n for n, x in enumerate(list(self.rules) + list(self.claims))}
        return self._order.get(i, 1 << 30)

    def kind(self, i):
        return "claim" if i in self.claims else self.rules[i]["kind"]

    def in_force(self, c, d):
        return c["valid_from"] <= d and (c.get("valid_to") is None or d <= c["valid_to"])

    def sup(self, w, l):
        """first source of w > l: explicit, strict, authority:<rule>, later (V3a sup/3 clause order)"""
        R, C = self.rules, self.claims
        if w in R and l in (R[w].get("superior-to") or []): return "explicit"
        if w in R and R[w]["kind"] == "strict" and not (l in R and R[l]["kind"] == "strict"): return "strict"
        if w in C and l in C:
            a, b = C[w], C[l]
            if a["asserted_by"] != b["asserted_by"] and pred_of(a["assertion"]) == pred_of(b["assertion"]):
                for sid, r in R.items():
                    if r["kind"] == "superiority" and self.active(sid) and r["pred"] == pred_of(a["assertion"]):
                        o = r.get("order") or []
                        if a["asserted_by"] in o and b["asserted_by"] in o and o.index(a["asserted_by"]) < o.index(b["asserted_by"]):
                            return f"authority:{sid}"
            if a["asserted_by"] == b["asserted_by"] and a["asserted_at"] > b["asserted_at"]: return "later"
        return None


class Meta:
    def __init__(self):
        self.slice, self.today, self.functional = None, None, {}
        self.concepts, self.concept_cols, self.terms, self.assets = [], {}, [], []
        self.modes = {p: (m if isinstance(m, list) else [m])
                      for p, m in read_edn((HERE.parent / "shared" / "modes.edn").read_text()).items()}
        self.func_text = ""


class Session:
    def __init__(self):
        self.meta = Meta()
        self.store = View()
        self.store.meta = self.meta

    def load_file(self, path):
        t = read_edn(pathlib.Path(path).read_text())
        if isinstance(t, dict):
            M = self.meta
            M.slice, M.today, M.functional = t, t["today"], dict(t.get("functional") or {})
            M.func_text = asp.functional_rules(M.functional)
            for c in t.get("concepts") or []:
                M.concepts.append(c)
                M.concept_cols[c["name"]] = list(c.get("columns") or [])
                if c.get("sql"):
                    sql.register(c["name"], c["sql"], list(c.get("params") or []))
            M.terms, M.assets = list(t.get("terms") or []), list(t.get("assets") or [])
            self.store.add(list(t.get("rules") or []) + list(t.get("claims") or []))
        else:
            self.store.add(t)


# ------------------------------------------------------------------ fetch during grounding

def fetch_json(concept, filters):
    return json.loads(sql.fetch(concept, json.dumps(dict(sorted(filters.items())))))


class Ctx:
    def __init__(self, meta):
        self.meta = meta

    def fetch(self, c, f):
        concept = c.string
        filters = {p.arguments[0].string: from_sym(p.arguments[1]) for p in f.arguments}
        cols = self.meta.concept_cols[concept]
        res = fetch_json(concept, filters)
        return [Function("", [to_sym(r.get(col)) for col in cols]) for r in res["rows"]]


# ------------------------------------------------------------------ one op's world

class World:
    def __init__(self, view, as_of, goals=()):
        self.V, self.D, self.M = view, as_of, view.meta
        demand = []
        for g in goals:
            A = g[1] if g[0] == "neg" else g
            bp = asp.bound_positions(A[0], self.M.modes)
            args = [A[1 + i] for i in bp if 1 + i < len(A)]
            if not ground(args):
                raise EngineError(f"goal {g} leaves a position its mode binds ({A[0]} {self.M.modes.get(A[0])}) unbound")
            demand.append(f"dm({asp.pn(A[0])},{asp.tup(asp.term(a) for a in args)}).")
        prog = "\n".join([asp.META, self.M.func_text, *view.text.values(), f"asof({asp.q(as_of)}).", *demand])
        t0 = time.time()
        ctl = clingo.Control(["0", "--warn=none"])
        ctl.add("base", [], prog)
        ctl.ground([("base", [])], context=Ctx(self.M))
        t1 = time.time()
        ids = list(view.rules) + list(view.claims)
        assumptions = [(Function("active", [String(i)]), view.active(i)) for i in ids]
        self.C, self.B = self._solve(ctl, "cautious", assumptions), self._solve(ctl, "brave", assumptions)
        t2 = time.time()
        self.timing = {"ground_ms": (t1 - t0) * 1000, "solve_ms": (t2 - t1) * 1000}
        # ground skeleton: every head instance (rules and in-force claims), and R314-style incompatibilities
        self.heads, self.inst, self.ih, self.func = {}, {}, {}, {}
        for a in ctl.symbolic_atoms.by_signature("h", 3):
            I, S, A = a.symbol.arguments
            L = lit_py(A) if S.name == "pos" else ["neg", lit_py(A)]
            rid = I.arguments[0].string
            vals = [from_sym(x) for x in I.arguments[1].arguments]
            self.inst[I] = (rid, vals, L)
            self.heads.setdefault(k(L), []).append(I)
            if S.name == "pos" and L[0] in self.M.functional:
                n = self.M.functional[L[0]]
                if len(L) - 1 == n + 1:
                    self.func.setdefault(k(L[:1 + n]), {})[k(L)] = L
        for a in ctl.symbolic_atoms.by_signature("ih", 2):
            I, A = a.symbol.arguments
            rid = I.arguments[0].string
            self.inst[I] = (rid, [from_sym(x) for x in I.arguments[1].arguments], lit_py(A))
            self.ih.setdefault(k(lit_py(A)), []).append(I)
        for v in self.heads.values(): v.sort()
        self.memo, self.stack, self.ex_stack = {}, [], []

    @staticmethod
    def _solve(ctl, mode, assumptions):
        ctl.configuration.solve.enum_mode = mode
        last = []
        def on_model(m):
            last[:] = m.symbols(shown=True)
        r = ctl.solve(assumptions=assumptions, on_model=on_model)
        if not r.satisfiable:
            raise EngineError(f"no partial stable model ({mode})")
        return set(last)

    # ---- truth values
    def wval(self, L):
        s = lit_sym(L)
        if Function("t_def", [s]) in self.C: return "true"
        if Function("p_def", [s]) in self.B: return "undefined"
        return "false"

    def bval(self, I):
        if Function("t_body", [I]) in self.C: return "true"
        if Function("p_body", [I]) in self.B: return "undefined"
        return "false"

    def beat_true(self, L, aid):
        s = lit_sym(L)
        return any(x.name == "t_beat" and x.arguments[1] == s and x.arguments[0].arguments[0].string == aid
                   for x in self.C)

    def binding(self, I):
        rid, vals, _ = self.inst[I]
        return dict(zip(asp.rule_vars(self.V.rules[rid]), vals)) if rid in self.V.rules else {}

    def rivals(self, L):
        if L[0] == "neg": return [L[1]]
        out = [["neg", L]]
        n = self.M.functional.get(L[0])
        if n is not None and len(L) - 1 == n + 1:
            out += [R for kk, R in sorted(self.func.get(k(L[:1 + n]), {}).items()) if not same(R[-1], L[-1])]
        return out

    def by_id(self, insts, kinds):
        """[(rid, [instances])] grouped per id, in store order; only active ids of the given kinds"""
        g = {}
        for I in insts:
            rid = self.inst[I][0]
            if self.V.active(rid) and self.V.kind(rid) in kinds:
                g.setdefault(rid, []).append(I)
        return sorted(g.items(), key=lambda x: self.V.order(x[0]))

    # ---- proofs
    def claim_node(self, cid, L, children=()):
        c = self.V.claims[cid]
        return {"type": "claim", "id": cid, "goal": L, "asserted_by": c["asserted_by"], "asserted_at": c["asserted_at"],
                "children": list(children)}

    def body_nodes(self, rule, b):
        kids = []
        for lit in rule.get("body") or []:
            op = lit[0]
            if op == "fetch":
                F = {c: subst(v, b) for c, v in sorted((lit[2] or {}).items())}
                res = fetch_json(lit[1], F)
                outs = {c: subst(t, b) for c, t in (lit[3] or {}).items()}
                row = next((r for r in res["rows"] if all(c in r and same(r[c], v) for c, v in outs.items())), None)
                if row is None: raise EngineError(f"no row of {lit[1]} {F} matches {outs}")
                kids.append({"sql": res["sql"], "params": res["params"], "truncated": res["truncated"], "type": "fetch",
                             "concept": lit[1], "filters": F, "rows": len(res["rows"]), "row": row})
            elif op == "not":
                kids.append({"type": "absent", "goal": subst(lit[1], b)})
            elif op == "as_of":
                kids.append({"type": "fact", "goal": ["as_of", self.D]})
            elif op == "is":
                kids.append({"type": "fact", "goal": ["is", subst(lit[1], b), subst(lit[2], b)]})
            elif op in CMP:
                kids.append({"type": "fact", "goal": [op, subst(lit[1], b), subst(lit[2], b)]})
            else:
                p = self.prove_ground(subst(lit, b))
                if p is None: raise EngineError(f"body literal {subst(lit, b)} of a true instance is not provable")
                kids.append(p)
        return kids

    def rule_proof(self, I):
        rid, _, L = self.inst[I]
        if self.V.kind(rid) == "claim":
            return self.claim_node(rid, L)
        return {"type": "rule", "id": rid, "goal": L, "children": self.body_nodes(self.V.rules[rid], self.binding(I))}

    def prove_ground(self, L):
        if self.wval(L) != "true": return None
        if k(L) in self.stack: return {"type": "ref", "goal": L}
        E = self.evaluate(L)
        if E[0] != "proven": return None
        sups, supn = E[1], E[2]
        p = dict(sups[0][2]); p["children"] = p["children"] + supn
        return p

    def prove_first(self, L, s):
        """first proof of pattern L (with bindings s): (proof, s2) or None"""
        G = subst(L, s)
        if ground(G):
            p = self.prove_ground(G)
            return (p, s) if p is not None else None
        cands = {}
        for kk, insts in self.heads.items():
            H = json.loads(kk)
            if unify(G, H, {}) is None: continue
            for rid, Is in self.by_id(insts, ("strict", "defeasible", "claim")):
                if any(self.bval(I) == "true" for I in Is): cands[kk] = H
        for H in sorted(cands.values(), key=okey):
            p = self.prove_ground(H)
            if p is not None:
                return p, unify(G, H, s)
        return None

    # ---- evaluation (V3a wfs_eval)
    def supporters(self, L):
        out = []
        for rid, Is in self.by_id(self.heads.get(k(L), []), ("strict", "defeasible", "claim")):
            I = next((I for I in Is if self.bval(I) == "true"), None)
            if I is not None:
                out.append((rid, self.V.kind(rid), self.rule_proof(I)))
        return out

    def attackers(self, L):
        out, seen = [], set()
        for H in self.rivals(L):
            for rid, Is in self.by_id(self.heads.get(k(H), []), ("strict", "defeasible", "defeater", "claim")):
                I = next((I for I in Is if self.bval(I) == "true"), None)
                if I is not None and rid not in seen:
                    seen.add(rid); out.append((rid, self.V.kind(rid), H, self.rule_proof(I)))
        return out

    def groups(self, L, role):
        """V3a inst/8: [(rid, kind, head, val, ulits)] for supporters (sup) / attackers (att) with a live body"""
        heads = [L] if role == "sup" else self.rivals(L)
        kinds = ("strict", "defeasible", "claim") if role == "sup" else ("strict", "defeasible", "defeater", "claim")
        g = {}
        for H in heads:
            for rid, Is in self.by_id(self.heads.get(k(H), []), kinds):
                g.setdefault(rid, []).extend(Is)
        out = []
        for rid in sorted(g, key=self.V.order):
            Is = sorted(g[rid])
            live = [I for I in Is if self.bval(I) != "false"]
            if not live: continue
            if any(self.bval(I) == "true" for I in live):
                tI = next(I for I in live if self.bval(I) == "true")
                out.append((rid, self.V.kind(rid), self.inst[tI][2], "true", []))
            else:
                out.append((rid, self.V.kind(rid), self.inst[live[0]][2], "undefined", self.undefined_lits(live[0])))
        return out

    def undefined_lits(self, I):
        rid = self.inst[I][0]
        if rid not in self.V.rules: return []
        b, out = self.binding(I), []
        for lit in self.V.rules[rid].get("body") or []:
            if lit[0] == "fetch" or lit[0] in BUILTIN: continue
            X = subst(lit[1] if lit[0] == "not" else lit, b)
            if self.wval(X) == "undefined": out.append(X)
        return out

    def evaluate(self, L):
        key = k(L)
        if key in self.memo: return self.memo[key]
        if not ground(L): raise EngineError(f"evaluate of a non-ground literal {L}")
        v = self.wval(L)
        self.stack.append(key)
        try:
            if v == "undefined":
                R = ("undefined", self.sides(L), self.undefined_node(L))
            else:
                sups, a1 = self.supporters(L), self.attackers(L)
                ids1 = {a[0] for a in a1}
                a2 = []
                for rid, kind, H, val, ul in self.groups(L, "att"):
                    if val == "undefined" and ul and rid not in ids1:
                        a2.append((rid, kind, H, {"type": "rule", "id": rid, "goal": H, "children": [self.undefined_node(ul[0])]}))
                        ids1.add(rid)
                R = self.classify(sups, a1 + a2)
                if not ((v == "true" and R[0] == "proven") or (v == "false" and R[0] != "proven")):
                    raise EngineError(f"wfs_inconsistent({L}, {v}, {R[0]})")
        finally:
            self.stack.pop()
        self.memo[key] = R
        return R

    def classify(self, sups, atts):
        if not sups: return ("none", atts)
        beaten = [a for a in atts if any(self.V.sup(s[0], a[0]) for s in sups)]
        unbeaten = [a for a in atts if a not in beaten]
        supn = []
        for a in beaten:
            s = next(s for s in sups if self.V.sup(s[0], a[0]))
            supn.append({"type": "superior", "winner": s[0], "loser": a[0], "source": self.V.sup(s[0], a[0])})
        if not unbeaten: return ("proven", sups, supn)
        for a in unbeaten:
            if all(self.V.sup(a[0], s[0]) for s in sups):
                dn = [{"type": "superior", "winner": a[0], "loser": s[0], "source": self.V.sup(a[0], s[0])} for s in sups]
                return ("defeated", a, sups, dn)
        return ("blocked", sups, unbeaten)

    def sides(self, L, seen=()):
        sg = self.groups(L, "sup")
        Ss = sorted({g[0] for g in sg})
        As = sorted({g[0] for g in self.groups(L, "att") if not self.beat_true(L, g[0])})
        if Ss and As: return sorted([Ss, As])
        pairs = sorted(((g[0], g[4][0]) for g in sg if g[3] == "undefined" and g[4]), key=lambda p: (p[0], okey(p[1])))
        if pairs and k(pairs[0][1]) not in seen:
            return self.sides(pairs[0][1], seen + (k(L),))
        return None

    def undefined_node(self, L):
        seen, q = [], [L]
        while q:
            X = q.pop(0)
            if any(k(X) == k(Y) for Y in seen): continue
            seen.append(X)
            for g in self.groups(X, "sup") + self.groups(X, "att"):
                if g[3] == "undefined": q += g[4]
        lits = sorted(seen, key=okey)
        mems = sorted({g[0] for X in lits for g in self.groups(X, "sup") + self.groups(X, "att")})
        return {"type": "undefined", "goal": L, "literals": lits, "members": mems, "children": []}

    def incompatible(self, G):
        cands = sorted(self.ih.get(k(G), []), key=lambda I: (self.V.order(self.inst[I][0]), I))
        for I in cands:
            rid = self.inst[I][0]
            if self.V.active(rid) and self.bval(I) == "true":
                return rid, {"type": "rule", "id": rid, "goal": ["neg", G],
                             "children": self.body_nodes(self.V.rules[rid], self.binding(I))}
        return None

    # ---- why-not (V3a why.pl)
    def explain_not(self, G):
        GJ = json_safe(G)
        if k(GJ) in self.ex_stack:
            return {"type": "absent", "goal": GJ, "children": []}
        self.ex_stack.append(k(GJ))
        try:
            E = self.evaluate(G) if ground(G) else ("none", [])
            Rs = []
            for rid, r in self.V.rules.items():
                if r["kind"] in ("strict", "defeasible") and self.V.active(rid) and unify(rename(r["head"], "#"), G, {}) is not None:
                    n = self.explain_rule(rid, G, E)
                    if n is not None: Rs.append(n)
            Cl = []
            if ground(G) and E[0] not in ("proven", "none"):
                for cid, c in self.V.claims.items():
                    if c["assertion"] == G and self.V.active(cid) and self.V.in_force(c, self.D):
                        dn = self.defeat_node(cid, E)
                        if dn is not None: Cl.append(self.claim_node(cid, G, [dn]))
            return {"type": "absent", "goal": GJ, "children": Rs + Cl}
        finally:
            self.ex_stack.pop()

    def explain_rule(self, rid, G, E):
        r = rename(self.V.rules[rid], "#")
        s = unify(r["head"], G, {})
        done, failed = [], None
        for lit in r.get("body") or []:
            res = self.lit_first(lit, s)
            if res is None:
                failed = self.failed_lit(lit, s)
                if failed is None: return None
                break
            node, s = res
            done.append(node)
        else:
            failed = self.defeat_node(rid, E)
        return {"type": "rule", "id": rid, "goal": json_safe(subst(G, s)), "children": done, "failed": failed}

    def lit_first(self, lit, s):
        op = lit[0]
        if op == "fetch":
            F = {c: subst(v, s) for c, v in sorted((lit[2] or {}).items())}
            if not ground(F): raise EngineError(f"fetch_unbound({lit[1]}, {F})")
            res = fetch_json(lit[1], F)
            for row in res["rows"]:
                s2 = s
                for c, t in (lit[3] or {}).items():
                    s2 = unify(t, row[c], s2) if c in row else None
                if s2 is not None:
                    return {"sql": res["sql"], "params": res["params"], "truncated": res["truncated"], "type": "fetch",
                            "concept": lit[1], "filters": F, "rows": len(res["rows"]), "row": row}, s2
            return None
        if op == "not":
            L = subst(lit[1], s)
            return ({"type": "absent", "goal": L}, s) if self.wval(L) == "false" else None
        if op == "as_of":
            s2 = unify(lit[1], self.D, s)
            return ({"type": "fact", "goal": ["as_of", self.D]}, s2) if s2 is not None else None
        if op == "is":
            E = subst(lit[2], s)
            s2 = unify(lit[1], ev(E), s)
            return ({"type": "fact", "goal": ["is", ev(E), E]}, s2) if s2 is not None else None
        if op in CMP:
            a, b = subst(lit[1], s), subst(lit[2], s)
            return ({"type": "fact", "goal": [op, a, b]}, s) if cmp_holds(op, a, b) else None
        return self.prove_first(lit, s)

    def failed_lit(self, lit, s):
        op = lit[0]
        if op == "fetch":
            F = {c: subst(v, s) for c, v in sorted((lit[2] or {}).items())}
            if not ground(F): return {"type": "absent", "goal": json_safe(["fetch", lit[1]])}
            res = fetch_json(lit[1], F)
            return {"sql": res["sql"], "params": res["params"], "truncated": res["truncated"], "type": "fetch",
                    "concept": lit[1], "filters": F, "rows": len(res["rows"]), "row": None}
        if op == "not":
            L = subst(lit[1], s)
            p = self.prove_first(L, {})
            return {"type": "absent", "goal": ["not", json_safe(L)], "children": [p[0]]} if p else None
        if op in BUILTIN:
            return {"type": "fact", "goal": json_safe(subst(lit, s)), "holds": False}
        return self.explain_not(subst(lit, s))

    def defeat_node(self, rid, E):
        if E[0] == "defeated":
            a = E[1]
            src = self.V.sup(a[0], rid)
            sn = [{"type": "superior", "winner": a[0], "loser": rid, "source": src}] if src else []
            return {"type": "defeated_by", "id": a[0], "target": rid, "children": [a[3]] + sn}
        if E[0] == "blocked":
            a = E[2][0]
            return {"type": "defeated_by", "id": a[0], "target": rid, "children": [a[3]], "blocked": True}
        return None


# ------------------------------------------------------------------ ops (V3a ops.pl)

def why_ids(why):
    out = set()
    def go(x):
        if isinstance(x, list):
            for y in x: go(y)
        elif isinstance(x, dict):
            if "id" in x: out.add(x["id"])
            if x.get("type") == "undefined": out.update(x.get("members") or [])
            for kk in ("children", "failed"):
                if kk in x: go(x[kk])
    go(why)
    return sorted(out)


class Ops:
    def __init__(self, session):
        self.S = session

    def answer(self, view, st, val, sides, why):
        owners = sorted({view.rules[i]["owner"] for i in why_ids(why) if i in view.rules and view.rules[i].get("owner")})
        return {"status": st, "value": val, "sides": sides, "why": why, "owners": owners, "qualifier": None}

    def as_of(self, op):
        return op.get("as_of") or self.S.meta.today

    def known_pred(self, view, p):
        return any(view.active(i) and r.get("head") and pred_of(r["head"]) == p for i, r in view.rules.items()) or \
            any(view.active(i) and pred_of(c["assertion"]) == p for i, c in view.claims.items())

    def scope(self, p):
        return "UNDERDETERMINED" if any(t["id"] == f"term:{p}" for t in self.S.meta.terms) else "OUT_OF_SCOPE"

    def run(self, op, view):
        sql.begin_op()
        t0 = time.time()
        try:
            r = getattr(self, "op_" + op["op"])(op, view)
        except Exception as e:  # noqa: BLE001  (reported per op, as V3a does)
            r = {"status": "ERROR", "error": f"{type(e).__name__}: {e}"}
        r["ms"] = (time.time() - t0) * 1000
        log = json.loads(sql.take_log())
        r["sql_log"] = [] if op["op"] == "with_hypothesis" else log
        return r

    # ---- decide / why_not
    def op_decide(self, op, view):
        G = read_edn(op["goal"])
        D = self.as_of(op)
        p = pred_of(G)
        if not self.known_pred(view, p):
            return {"status": self.scope(p), "value": None, "sides": None, "why": [], "owners": [], "qualifier": None}
        W = World(view, D, [G])
        r = self.decide_ground(W, G) if ground(G) else self.decide_open(W, G)
        if os.environ.get("V3E_TIMING"): r["engine"] = W.timing   # latency probe only (not in the contract)
        return r

    def team_proofs(self, sups, supn):
        out = []
        for sid, _, p in sups:
            p = dict(p); p["children"] = p["children"] + [n for n in supn if n["winner"] == sid]
            out.append(p)
        return out

    def decide_ground(self, W, G):
        E = W.evaluate(G)
        if E[0] == "proven":
            why = self.team_proofs(E[1], E[2])
            inc = W.incompatible(G)
            if inc:
                sides = sorted([sorted({s[0] for s in E[1]}), [inc[0]]])
                return self.answer(W.V, "CONFLICT", None, sides, why + [inc[1]])
            return self.answer(W.V, "ANSWER", True, None, why)
        if E[0] == "blocked":
            sides = sorted([sorted({s[0] for s in E[1]}), sorted({a[0] for a in E[2]})])
            return self.answer(W.V, "CONFLICT", None, sides, [s[2] for s in E[1]] + [a[3] for a in E[2]])
        if E[0] == "undefined":
            return self.answer(W.V, "CONFLICT", None, E[1], [E[2]])
        return self.answer(W.V, "ANSWER", False, None, [W.explain_not(G)])

    def candidates(self, W, G):
        out = {}
        for kk, insts in W.heads.items():
            H = json.loads(kk)
            if unify(G, H, {}) is None: continue
            for rid, Is in W.by_id(insts, ("strict", "defeasible", "claim")):
                if any(W.bval(I) == "true" for I in Is): out[kk] = H
        return sorted(out.values(), key=okey)

    def decide_open(self, W, G):
        Vs = term_vars(G)
        val = lambda H: (lambda s: subst(Vs[0], s) if len(Vs) == 1 else subst(Vs, s))(unify(G, H, {}))
        GEs = [(H, W.evaluate(H)) for H in self.candidates(W, G)]
        won = [(H, E) for H, E in GEs if E[0] == "proven"]
        sups_of = lambda E: E[1] if E[0] == "proven" else (E[2] if E[0] == "defeated" else (E[1] if E[0] == "blocked" else []))
        if pred_of(G) in self.S.meta.functional:
            if len(won) == 1:
                H, E = won[0]
                return self.answer(W.V, "ANSWER", val(H), None, self.team_proofs(E[1], E[2]))
            if not won and GEs:
                sides = sorted({json.dumps(sorted({s[0] for s in sups_of(E)})) for _, E in GEs if sups_of(E)})
                why = [s[2] for _, E in GEs for s in sups_of(E)]
                return self.answer(W.V, "CONFLICT", None, [json.loads(x) for x in sides], why)
            if not won:
                return self.answer(W.V, "ANSWER", None, None, [W.explain_not(G)])
            r = self.answer(W.V, "CONFLICT", None, None, [])
            r["value"] = [val(H) for H, _ in won]
            return r
        vals, why = [], []
        for H, E in won:
            vals.append(val(H)); why += self.team_proofs(E[1], E[2])
        uniq = {k(v): v for v in vals}
        return self.answer(W.V, "ANSWER", sorted(uniq.values(), key=okey), None, why)

    def op_why_not(self, op, view):
        G = read_edn(op["goal"])
        W = World(view, self.as_of(op), [G])
        if ground(G):
            E = W.evaluate(G)
            if E[0] == "proven":
                return {"status": "ANSWER", "value": True, "why": self.team_proofs(E[1], E[2]), "why_not": []}
        return {"status": "ANSWER", "value": False, "why_not": [W.explain_not(G)]}

    # ---- claims
    def op_claims(self, op, view):
        A, D = op["asset"], self.as_of(op)
        top = [i for i, c in view.claims.items() if c["about"] == A and c["parent"] is None and view.active(i)]
        goals = [c["assertion"] for c in view.claims.values() if c["about"] == A]
        W = World(view, D, goals) if top else None
        return {"asset": A, "claims": [self.standing(W, i) for i in top]}

    def standing(self, W, cid):
        V = W.V
        c = V.claims[cid]
        base = {"id": cid, "about": c["about"], "assertion": c["assertion"], "asserted_by": c["asserted_by"],
                "asserted_at": c["asserted_at"], "valid_from": c["valid_from"], "valid_to": c.get("valid_to"),
                "backing": c.get("backing"), "modal": c.get("qualifier"), "role": c.get("role")}
        subs = [self.standing(W, i) for i, s in V.claims.items() if s["parent"] == cid and V.active(i)]
        if not V.in_force(c, W.D):
            st = {"standing": "not_in_force", "defeater": None, "qualifier": [], "sides": None}
        else:
            st = self.own_standing(W.evaluate(c["assertion"]))
            if st["standing"] == "holds":
                st = self.sub_standing(subs)
        return {**base, **st, "subclaims": subs}

    @staticmethod
    def own_standing(E):
        if E[0] in ("proven", "none"):
            return {"standing": "holds", "defeater": None, "qualifier": [], "sides": None}
        if E[0] == "defeated":
            return {"standing": "rebutted", "defeater": E[1][0], "qualifier": [], "sides": None}
        if E[0] == "blocked":
            return {"standing": "contested", "defeater": None, "qualifier": [],
                    "sides": sorted([sorted({s[0] for s in E[1]}), sorted({a[0] for a in E[2]})])}
        return {"standing": "contested", "defeater": None, "qualifier": [], "sides": E[1]}

    @staticmethod
    def sub_standing(subs):
        failing = lambda s: s["standing"] not in ("holds", "holds_with_qualifier")
        for s in subs:
            if s["role"] == "required" and failing(s):
                return {"standing": "rebutted", "defeater": s["defeater"], "qualifier": [], "sides": None, "via": s["id"]}
        q = sorted({s["id"] for s in subs if s["role"] == "supporting" and failing(s)})
        if not q:
            return {"standing": "holds", "defeater": None, "qualifier": [], "sides": None}
        return {"standing": "holds_with_qualifier", "defeater": None, "qualifier": q, "sides": None}

    # ---- vocabulary, metadata, fetch
    @staticmethod
    def norm(s):
        return " ".join("".join(ch if ch.isalnum() else " " for ch in s.lower()).split())

    def op_resolve_term(self, op, view):
        n = self.norm(op["text"])
        T = {t["id"]: t for t in self.S.meta.terms}
        ids = set()
        for t in self.S.meta.terms:
            if self.norm(t.get("label", "")) == n or any(self.norm(x) == n for x in t.get("synonyms") or []):
                ids |= set(t["see"]) if t.get("see") else {t["id"]}
        ids = sorted(ids)
        cs = [{"term": i, "definition": T[i]["definition"], "owner": T[i]["owner"]} for i in ids if i in T]
        st = "none" if not ids else ("concept" if len(ids) == 1 else "several")
        return {"text": op["text"], "status": st, "candidates": cs}

    def op_describe(self, op, view):
        A, M = op["asset"], self.S.meta
        cs = [i for i, c in view.claims.items() if c["about"] == A and c["parent"] is None]
        meta = None
        for a in M.assets:
            if a["id"] == A: meta = (a.get("kind"), a.get("doc"), None); break
        if meta is None:
            for t in M.terms:
                if t["id"] == A: meta = ("term", t.get("definition"), t.get("concept")); break
        if meta is None:
            for c in M.concepts:
                if c.get("id") == A:
                    meta = (c.get("kind"), c.get("doc"), {"concept": c["name"], "tables": c.get("tables") or [],
                                                          "params": c.get("params") or [], "sql": c.get("sql")}); break
        if meta is None:
            for t in M.slice.get("tables") or []:
                if t["id"] == A: meta = ("table", t.get("doc"), None); break
                for col in t.get("columns") or []:
                    if col["id"] == A: meta = ("column", col.get("doc"), None); break
                if meta: break
        st = "ANSWER" if meta else "OUT_OF_SCOPE"
        kd, doc, b = meta or (None, None, None)
        return {"status": st, "asset": A, "kind": kd, "doc": doc, "bindings": b, "claims": cs}

    def op_fetch(self, op, view):
        res = fetch_json(op["concept"], op["filters"])
        return {"concept": op["concept"], "filters": op["filters"], "rows": res["rows"], "sql": res["sql"],
                "params": res["params"], "row_count": len(res["rows"]), "truncated": res["truncated"]}

    # ---- extension, hypotheses
    def op_add(self, op, view):
        recs = read_edn(op["edn"])
        return {"added": view.add(recs if isinstance(recs, list) else [recs])}

    def op_with_hypothesis(self, op, view):
        h = View(view)
        h.withheld |= set(op.get("withhold") or [])
        ids = []
        if op.get("add"):
            recs = read_edn(op["add"])
            ids = h.add(recs if isinstance(recs, list) else [recs])
        return {"results": [self.run(o, h) for o in op["ops"]], "added": ids, "withheld": list(op.get("withhold") or [])}

    def op_sleep(self, op, view):
        t0 = time.time() * 1000
        time.sleep(op["ms"] / 1000)
        return {"t0": t0, "t1": time.time() * 1000}


def main():
    script = json.load(sys.stdin)
    t0 = time.time()
    sql.configure(json.dumps(script["config"]), os.getcwd())
    S = Session()
    for f in script.get("load", []):
        S.load_file(f)
    O = Ops(S)
    load_ms = (time.time() - t0) * 1000
    out = {"results": [O.run(op, S.store) for op in script.get("ops", [])], "load_ms": load_ms}
    if "concurrent" in script:   # test mode (shared/isolation.py): each op list in its own thread
        res = [None] * len(script["concurrent"])
        def go(n, ops):
            rs = []
            for o in ops:
                a = time.time() * 1000
                r = O.run(o, S.store)
                r["t_start"], r["t_end"] = a, time.time() * 1000
                rs.append(r)
            res[n] = rs
        ts = [threading.Thread(target=go, args=(n, ops)) for n, ops in enumerate(script["concurrent"])]
        for t in ts: t.start()
        for t in ts: t.join()
        out["concurrent"] = res
    if "after" in script:
        out["after"] = [O.run(op, S.store) for op in script["after"]]
    json.dump(out, sys.stdout, default=str)


if __name__ == "__main__":
    main()
