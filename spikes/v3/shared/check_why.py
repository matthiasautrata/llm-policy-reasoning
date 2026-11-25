"""Independent re-verification of System A why trees (CONTRACT.md), for both spikes.

Does not share code with either evaluator. Given the active rule/claim set, the evaluation date and a
backend connection, it re-checks every node:

  rule        id is active; head unifies with goal; children align with the body literals in order
              (derived literal -> rule/claim node whose goal unifies; fetch -> fetch node; [:not L] ->
              absent node; builtin -> fact node, re-evaluated); trailing children are superior /
              defeated_by nodes, themselves verified
  claim       id is active; goal is its assertion; in force on as_of
  fetch       SQL re-run on the backend: same row count, the bound row is among the rows, and the row
              agrees with the literal's filters
  superior    re-derived from the slice: explicit :superior-to, authority (R313), later asserted_at,
              strict over non-strict
  absent      structural (children, if any, verified as why-not material)
  undefined   (defeat cycles) goal, literals, members: the goal and its literals must be undefined in the
              reference's well-founded model (`undefined` = the key's {literals, members}); the node for
              the question's goal must list exactly the reference's component, nested ones a subset;
              members must be active ids
  contested   (ambiguity propagation, SEMANTICS.md) goal, via, rules, roots: the goal must be a
              downstream-contested ground literal of the reference (`contested` = the key's map
              json(goal) -> {via, rules, roots}); via (literals), rules (ids) and the roots' {goal, sides}
              must equal the reference's exactly; rules must be active ids; each root is a conflict node
  conflict    goal, sides, children: the side members' proofs (rule / claim nodes), each verified; every
              side id must have a child node

Usage as a library: Checker(slice_plain, active_rules, active_claims, as_of, runsql).check(nodes)
returns a list of error strings (empty = verified).
"""
import operator

CMP = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "=": operator.eq}
ARITH = {"+": operator.add, "-": operator.sub}


def is_var(x):
    return isinstance(x, str) and x.startswith("?")


def walk(t, s):
    while is_var(t) and t in s:
        t = s[t]
    return t


def subst(t, s):
    t = walk(t, s)
    if isinstance(t, list):
        return [subst(x, s) for x in t]
    if isinstance(t, dict):
        return {k: subst(v, s) for k, v in t.items()}
    return t


def unify(a, b, s):
    """a: pattern (may hold ?vars); b: ground JSON value. -> extended s or None."""
    if s is None:
        return None
    a = walk(a, s)
    if is_var(a):
        return {**s, a: b}
    if isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            return None
        for x, y in zip(a, b):
            s = unify(x, y, s)
            if s is None:
                return None
        return s
    if isinstance(a, bool) or isinstance(b, bool):
        return s if a is b else None
    return s if a == b else None


def ground(t):
    if is_var(t):
        return False
    if isinstance(t, list):
        return all(ground(x) for x in t)
    return True


def ev(t, s):
    t = walk(t, s)
    if isinstance(t, list) and t and t[0] in ARITH:
        return ARITH[t[0]](ev(t[1], s), ev(t[2], s))
    if is_var(t):
        raise ValueError(f"unbound {t}")
    return t


def norm(v):
    """Backend values -> comparable JSON values."""
    if hasattr(v, "isoformat"):
        return v.isoformat()[:10]
    if hasattr(v, "is_integer") and not isinstance(v, bool) and float(v).is_integer():
        return int(v)
    return v


def node_ids(nodes, out=None):
    """All rule / claim ids an explanation mentions (for the core check)."""
    out = set() if out is None else out
    for n in nodes or []:
        t = n.get("type")
        if t in ("rule", "claim", "defeated_by") and n.get("id"):
            out.add(n["id"])
        if t == "defeated_by" and n.get("target"):
            out.add(n["target"])
        if t == "undefined":
            out |= set(n.get("members") or [])
        if t == "contested":
            out |= set(n.get("rules") or [])
            node_ids(n.get("roots"), out)
        if t == "conflict":
            out |= {i for sd in n.get("sides") or [] for i in sd}
        if t == "superior":
            out |= {n["winner"], n["loser"]}
            if n.get("source", "").startswith("authority:"):
                out.add(n["source"].split(":", 1)[1])
        node_ids(n.get("children"), out)
        if n.get("failed"):
            node_ids([n["failed"]], out)
    return out


def goals_in(nodes, out=None):
    out = [] if out is None else out
    for n in nodes or []:
        if "goal" in n:
            out.append(n["goal"])
        goals_in(n.get("children"), out)
        if n.get("failed"):
            goals_in([n["failed"]], out)
    return out


class Checker:
    def __init__(self, slice_, rules, claims, as_of, runsql, undefined=None, goal=None, contested=None):
        """slice_: plain slice; rules: {id: rule}; claims: {id: claim incl. sub-claims}; runsql(sql, params) -> [dict];
        undefined: the reference's undefined component {literals, members} for the question goal (cycles)"""
        self.S, self.rules, self.claims, self.as_of, self.runsql = slice_, rules, claims, as_of, runsql
        self.undef, self.goal, self.cont = undefined, goal, contested or {}
        self.errors, self._sql = [], {}

    def err(self, path, msg):
        self.errors.append(f"{path}: {msg}")

    def check(self, nodes, path="why"):
        for i, n in enumerate(nodes or []):
            self.node(n, f"{path}[{i}]")
        return self.errors

    def check_why_not(self, nodes, path="why_not"):
        for i, n in enumerate(nodes or []):
            self.wn(n, f"{path}[{i}]")
        return self.errors

    # ---------------------------------------------------------------- proofs
    def node(self, n, path):
        t = n.get("type")
        if t == "rule":
            self.rule(n, path)
        elif t == "claim":
            self.claim(n, path)
        elif t == "superior":
            self.superior(n, path)
        elif t == "defeated_by":
            if n.get("id") not in self.rules and n.get("id") not in self.claims:
                self.err(path, f"defeater {n.get('id')} not active")
            for j, k in enumerate(n.get("children") or []):
                self.node(k, f"{path}.{n.get('id')}[{j}]")
        elif t == "absent":
            pass
        elif t == "fetch":
            self.fetch(n, path, None, None)
        elif t == "fact":
            pass
        elif t == "undefined":
            self.undefined(n, path)
        elif t == "contested":
            self.contested(n, path)
        elif t == "conflict":
            self.conflict(n, path)
        else:
            self.err(path, f"unknown node type {t}")

    def undefined(self, n, path):
        if not self.undef:
            return self.err(path, f"undefined node for {n.get('goal')}, but the reference has no undefined component")
        key = lambda xs: sorted(map(repr, xs or []))
        ref_l, ref_m = key(self.undef["literals"]), sorted(self.undef["members"])
        lits, mem = key(n.get("literals")), sorted(n.get("members") or [])
        if repr(n.get("goal")) not in ref_l:
            self.err(path, f"goal {n.get('goal')} is not undefined in the reference")
        if n.get("goal") == self.goal:
            if lits != ref_l: self.err(path, f"undefined literals {n.get('literals')} != reference {self.undef['literals']}")
            if mem != ref_m: self.err(path, f"undefined members {mem} != reference {ref_m}")
        else:
            if not set(lits) <= set(ref_l): self.err(path, f"undefined literals {n.get('literals')} outside the reference component")
            if not set(mem) <= set(ref_m): self.err(path, f"undefined members {mem} outside the reference component")
        for m in mem:
            if m not in self.rules and m not in self.claims:
                self.err(path, f"member {m} not active")
        for j, k in enumerate(n.get("children") or []):
            self.node(k, f"{path}[{j}]")

    def contested(self, n, path):
        import json
        g = n.get("goal"); ref = self.cont.get(json.dumps(g))
        if ref is None:
            return self.err(path, f"contested node for {g}, which the reference does not contest downstream")
        J = lambda xs: sorted(json.dumps(x) for x in xs or [])
        if J(n.get("via")) != J(ref["via"]): self.err(path, f"contested via {n.get('via')} != reference {ref['via']}")
        if sorted(n.get("rules") or []) != ref["rules"]: self.err(path, f"contested rules {n.get('rules')} != reference {ref['rules']}")
        for m in n.get("rules") or []:
            if m not in self.rules and m not in self.claims:
                self.err(path, f"rule {m} not active")
        roots = n.get("roots") or []
        if any(r.get("type") != "conflict" for r in roots): self.err(path, "a root is not a conflict node")
        got = sorted(json.dumps([r.get("goal"), sorted(sorted(x) for x in r.get("sides") or [])]) for r in roots)
        want = sorted(json.dumps([r["goal"], r["sides"]]) for r in ref["roots"])
        if got != want: self.err(path, f"contested roots {got} != reference {want}")
        for j, r in enumerate(roots):
            self.node(r, f"{path}.roots[{j}]")

    def conflict(self, n, path):
        kids = n.get("children") or []
        have = node_ids(kids)
        for i in {i for sd in n.get("sides") or [] for i in sd} - have:
            self.err(path, f"conflict side {i} has no proof node")
        for j, k in enumerate(kids):
            self.node(k, f"{path}[{j}]")

    def rule(self, n, path):
        rid, goal = n.get("id"), n.get("goal")
        path = f"{path}<{rid}>"
        r = self.rules.get(rid)
        if r is None:
            return self.err(path, "rule not in the active set")
        head = r["head"]
        if r["kind"] == "incompatible":
            if not (isinstance(goal, list) and goal[:1] == ["neg"]):
                return self.err(path, "incompatibility node must conclude [neg, head]")
            s = unify(head, goal[1], {})
        else:
            s = unify(head, goal, {})
        if s is None:
            return self.err(path, f"head {head} does not unify with goal {goal}")
        body, kids = r.get("body") or [], n.get("children") or []
        if len(kids) < len(body):
            return self.err(path, f"{len(kids)} children for {len(body)} body literals")
        for j, (lit, k) in enumerate(zip(body, kids)):
            s = self.literal(lit, k, s, f"{path}[{j}]")
            if s is None:
                return
        for j, k in enumerate(kids[len(body):]):
            if k.get("type") not in ("superior", "defeated_by"):
                self.err(f"{path}[+{j}]", f"extra child of type {k.get('type')}")
            self.node(k, f"{path}[+{j}]")
        if not ground(subst(head, s)):
            self.err(path, "head not ground after the body")

    def literal(self, lit, k, s, path):
        op = lit[0]
        if op == "fetch":
            if k.get("type") != "fetch" or k.get("concept") != lit[1]:
                self.err(path, f"expected fetch {lit[1]}, got {k.get('type')} {k.get('concept')}")
                return None
            return self.fetch(k, path, lit, s)
        if op == "not":
            g = subst(lit[1], s)
            if k.get("type") != "absent" or not ground(g) or k.get("goal") != g:
                self.err(path, f"expected absent {g}, got {k.get('type')} {k.get('goal')}")
                return None
            return s
        if op in CMP or op in ("is", "as_of"):
            if k.get("type") != "fact":
                self.err(path, f"expected fact for {op}")
                return None
            try:
                if op == "as_of":
                    s2 = unify(lit[1], self.as_of, s)
                elif op == "is":
                    s2 = unify(lit[1], ev(lit[2], s), s)
                else:
                    s2 = s if CMP[op](ev(lit[1], s), ev(lit[2], s)) else None
            except (ValueError, TypeError) as e:
                self.err(path, f"builtin {lit}: {e}")
                return None
            if s2 is None:
                self.err(path, f"builtin {subst(lit, s)} does not hold")
                return None
            if k.get("goal") is not None and k["goal"] != subst(lit, s2):
                self.err(path, f"fact goal {k['goal']} != {subst(lit, s2)}")
            return s2
        # derived literal
        if k.get("type") not in ("rule", "claim", "undefined", "contested"):
            self.err(path, f"expected a proof of {subst(lit, s)}, got {k.get('type')}")
            return None
        s2 = unify(lit, k.get("goal"), s)
        if s2 is None:
            self.err(path, f"literal {subst(lit, s)} does not unify with child goal {k.get('goal')}")
            return None
        self.node(k, path)
        return s2

    def sql(self, sql, params):
        key = (sql, tuple(map(str, params)))
        if key not in self._sql:
            self._sql[key] = [{c: norm(v) for c, v in r.items()} for r in self.runsql(sql, params)]
        return self._sql[key]

    def fetch(self, k, path, lit, s):
        rows = self.sql(k["sql"], k.get("params") or [])
        if len(rows) != k.get("rows"):
            self.err(path, f"fetch {k.get('concept')}: {len(rows)} rows on re-run, node says {k.get('rows')}")
        row = k.get("row")
        if row is not None and {c: norm(v) for c, v in row.items()} not in rows:
            self.err(path, f"fetch {k.get('concept')}: bound row {row} not among the re-run rows")
        if lit is None:
            return s
        filt, outs = lit[2] or {}, lit[3] or {}
        for col, term in filt.items():
            v = subst(term, s)
            if not ground(v):
                self.err(path, f"filter {col} unbound")
                return None
            if (k.get("filters") or {}).get(col) != v:
                self.err(path, f"filter {col}={v} not in node filters {k.get('filters')}")
                return None
            if row is not None and col in row and norm(row[col]) != v:
                self.err(path, f"row {col}={row[col]} contradicts filter {v}")
                return None
        if row is None:
            if outs or k.get("rows"):
                self.err(path, "proof fetch without a bound row")
                return None
            return s
        for col, term in outs.items():
            if col not in row:
                self.err(path, f"row lacks output column {col}")
                return None
            s = unify(term, norm(row[col]), s)
            if s is None:
                self.err(path, f"output {col}={row[col]} does not unify with {term}")
                return None
        return s

    def claim(self, n, path):
        cid = n.get("id")
        path = f"{path}<{cid}>"
        c = self.claims.get(cid)
        if c is None:
            return self.err(path, "claim not active")
        if c["assertion"] != n.get("goal"):
            self.err(path, f"goal {n.get('goal')} is not the assertion {c['assertion']}")
        if not (c["valid_from"] <= self.as_of and (c.get("valid_to") is None or self.as_of <= c["valid_to"])):
            self.err(path, f"claim not in force on {self.as_of}")
        for j, k in enumerate(n.get("children") or []):
            self.node(k, f"{path}[{j}]")

    def superior(self, n, path):
        w, l, src = n.get("winner"), n.get("loser"), n.get("source", "")
        ok = False
        if src == "explicit":
            ok = l in (self.rules.get(w, {}).get("superior-to") or [])
        elif src == "strict":
            ok = self.rules.get(w, {}).get("kind") == "strict" and self.rules.get(l, {}).get("kind") != "strict"
        elif src == "later":
            A, B = self.claims.get(w), self.claims.get(l)
            ok = bool(A and B and A["asserted_by"] == B["asserted_by"] and A["asserted_at"] > B["asserted_at"])
        elif src.startswith("authority:"):
            sr = self.rules.get(src.split(":", 1)[1])
            A, B = self.claims.get(w), self.claims.get(l)
            if sr and sr.get("kind") == "superiority" and A and B:
                pred = lambda c: c["assertion"][1][0] if c["assertion"][0] == "neg" else c["assertion"][0]
                o = sr["order"]
                ok = (pred(A) == pred(B) == sr["pred"] and A["asserted_by"] in o and B["asserted_by"] in o
                      and o.index(A["asserted_by"]) < o.index(B["asserted_by"]))
        if not ok:
            self.err(path, f"superior {w} > {l} ({src}) not derivable from the active set")

    # ---------------------------------------------------------------- why-not (structural + 0-row fetches)
    def wn(self, n, path):
        t = n.get("type")
        if t == "rule":
            r = self.rules.get(n.get("id"))
            if r is None:
                return self.err(path, f"rule {n.get('id')} not active")
            if r["kind"] != "incompatible" and unify(r["head"], n.get("goal"), {}) is None:
                self.err(path, f"head of {n['id']} does not unify with {n.get('goal')}")
            if n.get("failed") is None and not n.get("children"):
                self.err(path, f"rule {n['id']} in a why-not without a failed literal or defeater")
        elif t == "fetch":
            if n.get("rows") == 0 and self.sql(n["sql"], n.get("params") or []):
                self.err(path, f"fetch {n.get('concept')} said 0 rows, re-run returns rows")
            return
        elif t in ("absent", "defeated_by"):
            pass
        elif t in ("claim", "superior", "fact"):
            return self.node(n, path)
        for j, k in enumerate(n.get("children") or []):
            self.wn(k, f"{path}[{j}]")
        if n.get("failed"):
            self.wn(n["failed"], f"{path}.failed")
