"""Shared model check over the rule base (PLAN-v3-cycles §1.4, amendment A2). Engine-independent.

  python spikes/v3/shared/model_check.py [--cycles] [--fixture f.edn] [--json]

1 Cycle report: the predicate dependency graph, with signed edges
    body literal -> head                    +
    [:not L] -> head                        -
    attacker body -> attacked predicate     -   (the head's complement has supporters: a rule or a claim for
                                                 P against one for [:neg P]; or rival rules of a functional P)
    incompatible body -> head               -   (R314: denied -> approved)
  Every strongly connected component that holds a "-" edge is a negative cycle. It is listed with its
  predicates and the rule ids that make its edges.
2 Moded safety (RESULTS lesson 3): for each predicate, infer the minimal sets of argument positions a
  caller must bind. A position counts as bound when it is a constant or a bound variable. Evaluation is
  left to right:
    fetch filters must be bound, and so must the concept's required params; the outputs then bind
    comparisons and [:not L] need every variable bound
    [:is V E] needs E bound and binds V
    [:as_of ?d] binds ?d
    a derived literal needs a safe pattern of its callee and binds all its arguments
    every head variable must be bound at the end.
  The check then compares the inferred modes with the declarations in modes.edn, checks every call site
  in the rules and every question goal, and checks that each functional predicate has a mode within its
  key positions.
3 A rule base with a negative cycle fails (IR-001a): cycles are rejected, never answered. So do moded errors.
  The command line prints the cycle report as a diagnostic, then the verdict.

Library: check(S, rules, claims, questions) -> dict(cycles=[...], modes={...}, errors=[...], ok=bool)
"""
import argparse, itertools, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reference import load, plain  # noqa: E402  (EDN reader only)
import edn_format as E  # noqa: E402

BUILTIN = {"<", "<=", ">", ">=", "=", "is", "as_of"}


def is_var(x):
    return isinstance(x, str) and x.startswith("?")


def vars_of(t):
    if is_var(t): return {t}
    if isinstance(t, list): return set().union(*[vars_of(x) for x in t]) if t else set()
    if isinstance(t, dict): return set().union(*[vars_of(x) for x in t.values()]) if t else set()
    return set()


def atom(L):
    """head or body literal -> (pred, args, sign)"""
    if L[0] == "neg": return L[1][0], L[1][1:], "-"
    return L[0], L[1:], "+"


def derived_body(r):
    """-> [(literal, negated)] for the derived (non-builtin, non-fetch) body literals"""
    out = []
    for b in r.get("body") or []:
        if b[0] == "not": out.append((b[1], True))
        elif b[0] not in BUILTIN and b[0] != "fetch": out.append((b, False))
    return out


# ------------------------------------------------------------------ 1 cycles
def dependency_graph(rules, claims, functional):
    """-> {(from, to): {sign: set(rule ids)}}"""
    E_ = {}
    def edge(a, b, sign, rid):
        E_.setdefault((a, b), {}).setdefault(sign, set()).add(rid)
    by_pred = {}
    for r in rules:
        if r.get("kind") == "superiority": continue
        p, _, s = atom(r["head"])
        by_pred.setdefault(p, {"+": [], "-": []})[s].append(r)
    for c in claims:
        p, _, s = atom(c["assertion"])
        by_pred.setdefault(p, {"+": [], "-": []})[s].append({"id": c["id"], "body": []})
    for r in rules:
        k = r.get("kind")
        if k == "superiority": continue
        p, _, s = atom(r["head"])
        other = "-" if s == "+" else "+"
        contested = bool(by_pred[p][other]) or (p in functional and len(by_pred[p]["+"]) > 1)
        for L, negated in derived_body(r):
            q = atom(L)[0]
            if k == "incompatible":
                edge(q, p, "-", r["id"]); continue
            edge(q, p, "-" if negated else "+", r["id"])
            if contested:
                edge(q, p, "-", r["id"])
    return E_


def sccs(nodes, succ):
    idx, low, st, on, out, n = {}, {}, [], set(), [], [0]
    def visit(v):
        idx[v] = low[v] = n[0]; n[0] += 1; st.append(v); on.add(v)
        for w in succ.get(v, ()):
            if w not in idx:
                visit(w); low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            c = set()
            while True:
                w = st.pop(); on.discard(w); c.add(w)
                if w == v: break
            out.append(c)
    for v in sorted(nodes):
        if v not in idx: visit(v)
    return out


def negative_cycles(rules, claims, functional):
    G = dependency_graph(rules, claims, functional)
    nodes = {a for a, _ in G} | {b for _, b in G}
    succ = {}
    for a, b in G: succ.setdefault(a, set()).add(b)
    out = []
    for c in sccs(nodes, succ):
        inner = {(a, b): s for (a, b), s in G.items() if a in c and b in c}
        if not inner: continue
        neg_edges = [(a, b, sorted(s["-"])) for (a, b), s in inner.items() if "-" in s]
        if neg_edges:
            out.append(dict(predicates=sorted(c), rules=sorted({i for s in inner.values() for ids in s.values() for i in ids}),
                            negative_edges=sorted([f"{a} -[{','.join(ids)}]-> {b}" for a, b, ids in neg_edges])))
    return out


# ------------------------------------------------------------------ 2 moded safety
class Modes:
    def __init__(self, S, rules, claims):
        self.concepts = {c["name"]: c for c in S["concepts"]}
        self.rules = [r for r in rules if r.get("kind") != "superiority"]
        self.arity = {}
        for r in self.rules:
            p, a, _ = atom(r["head"]); self.arity[p] = len(a)
        self.factual = {atom(c["assertion"])[0] for c in claims}
        for c in claims:
            p, a, _ = atom(c["assertion"]); self.arity.setdefault(p, len(a))
        self.safe = {}            # pred -> set of frozenset(bound positions) known safe
        self.errors = []

    def is_safe(self, p, bound):
        if p not in {atom(r["head"])[0] for r in self.rules}:
            return True                               # claims only, or no rules: facts / plain failure
        return any(m <= bound for m in self.safe.get(p, ()))   # safe sets are upward closed

    def simulate(self, r, bound_pos, report=None):
        """bound head positions -> (ok, first problem)"""
        _, args, _ = atom(r["head"])
        B = set()
        for i in bound_pos:
            B |= vars_of(args[i])
        def need(vs, what):
            miss = sorted(v for v in vs if v not in B)
            return None if not miss else f"{what}: unbound {', '.join(miss)}"
        for b in r.get("body") or []:
            op, prob = b[0], None
            if op == "fetch":
                c = self.concepts.get(b[1])
                prob = need(vars_of(b[2]), f"fetch {b[1]} filters")
                if not prob and c:
                    gone = [p for p in c.get("params") or [] if p not in b[2]]
                    prob = f"fetch {b[1]}: required param {gone} missing" if gone else None
                B |= vars_of(b[3]) if len(b) > 3 else set()
            elif op == "as_of":
                B |= vars_of(b[1])
            elif op == "is":
                prob = need(vars_of(b[2]), "is"); B |= vars_of(b[1])
            elif op in BUILTIN:
                prob = need(vars_of(b[1:]), op)
            elif op == "not":
                q, qa, _ = atom(b[1])
                prob = need(vars_of(qa), f"not {q}")
                if not prob and not self.is_safe(q, frozenset(range(len(qa)))):
                    prob = f"not {q}: callee unsafe even fully bound"
            else:
                q, qa, _ = atom(b)
                bp = frozenset(i for i, x in enumerate(qa) if not vars_of(x) - B)
                if not self.is_safe(q, bp):
                    prob = f"call {q}/{len(qa)} with bound positions {sorted(bp)}: no safe mode"
                B |= vars_of(qa)
            if prob:
                return False, prob
        miss = sorted(vars_of(args) - B)
        return (False, f"head variables {miss} unbound at the end") if miss else (True, None)

    def infer(self):
        """Greatest fixpoint: start with every pattern safe, drop patterns under which some rule of the
        predicate is unsafe, until stable. Mutual recursion (a defeat cycle) is then safe when each call
        in the cycle is bound; a least fixpoint could never type it."""
        preds = sorted({atom(r["head"])[0] for r in self.rules})
        allp = lambda n: {frozenset(c) for k in range(n + 1) for c in itertools.combinations(range(n), k)}
        self.safe = {p: allp(self.arity[p]) for p in preds}
        changed = True
        while changed:
            changed = False
            for p in preds:
                keep = {bp for bp in self.safe[p]
                        if all(self.simulate(r, bp)[0] for r in self.rules if atom(r["head"])[0] == p)}
                if keep != self.safe[p]:
                    self.safe[p], changed = keep, True
        for p in preds:
            ms = self.safe[p]
            self.safe[p] = {m for m in ms if not any(o < m for o in ms)}
        return {p: sorted(mode_str(m, self.arity[p]) for m in self.safe[p]) for p in preds}


def mode_str(m, n):
    return "".join("+" if i in m else "-" for i in range(n))


ADDITIVITY = {"additive", "semi-additive", "non-additive", "unknown"}


def mentions(t, name):
    if t == name: return True
    if isinstance(t, (list, tuple)): return any(mentions(x, name) for x in t)
    if isinstance(t, dict): return any(k == name or mentions(v, name) for k, v in t.items())
    return False


def shape_errors(S, rules, claims, additivity=True):
    """PLAN-v3-integrity §1: flat claims, linked by ids; additivity on every measure; recorded_at is
    provenance only (no rule body reads it)."""
    errors = []
    ids = {c.get("id") for c in claims}
    for c in claims:
        if "subclaims" in c:
            errors.append(f"{c.get('id')}: nested :subclaims (claims are flat; link with :depends_on / :supports)")
        for k in ("depends_on", "supports"):
            v = c.get(k)
            if v is None: continue
            if not isinstance(v, list):
                errors.append(f"{c.get('id')}: :{k} must be a vector of claim ids"); continue
            for m in v:
                if m not in ids: errors.append(f"{c.get('id')}: :{k} names unknown claim {m}")
    for r in rules:
        if mentions(r.get("body") or [], "recorded_at"):
            errors.append(f"{r.get('id')}: rule body references recorded_at (provenance, not evidence)")
    for c in S.get("concepts") or []:
        if c.get("kind") != "measure" or not additivity: continue
        a = c.get("additivity")
        if a not in ADDITIVITY:
            errors.append(f"{c['id']}: :additivity missing or not one of {sorted(ADDITIVITY)}: {a}")
        elif a == "semi-additive" and not c.get("unsafe_dims"):
            errors.append(f"{c['id']}: :semi-additive without :unsafe_dims")
    return errors


# ------------------------------------------------------------------ 3 integrity (PLAN-v3-integrity §2)
ORDERING_KEYS = {"priority", "weight", "rank", "salience", "overrides", "precedence", "preference", "order_by"}


def V(violation, members, message):
    return dict(violation=violation, members=sorted({str(m) for m in members}), message=message)


def pred_of(x):
    """rule head / claim assertion predicate (complement stripped)"""
    L = x.get("head") or x.get("assertion")
    return atom(L)[0] if L else None


def superiority_cycles(rules, claims):
    """IR-001b. Superiority between rivals (records whose conclusions share a predicate) and along
    explicit :superior-to edges, combined lexicographically:
      1 explicit :superior-to (either direction decides the pair)
      2 authority: a superiority rule {:pred p :order [a b ...]} ranks claims on p by asserter
      3 strict over non-strict (rules)
      4 later asserted_at, only between claims of the same asserter; equal asserted_at: none.
    The relation must be a strict partial order: any strongly connected component (or a self-loop)
    of the combined relation is a violation. Also checked on its own: the asserter order per predicate
    (several superiority rules for one predicate must not order two asserters both ways)."""
    out = []
    items = {x["id"]: x for x in [r for r in rules if r.get("kind") != "superiority"] + list(claims)}
    auth, auth_src = {}, {}
    for r in rules:
        if r.get("kind") != "superiority": continue
        o = r.get("order") or []
        for i, a in enumerate(o):
            for b in o[i + 1:]:
                auth.setdefault(r.get("pred"), set()).add((a, b))
                auth_src.setdefault((r.get("pred"), a, b), set()).add(r["id"])
    for p, rel in auth.items():                       # asserter order per predicate
        nodes = {a for e in rel for a in e}
        succ = {}
        for a, b in rel: succ.setdefault(a, set()).add(b)
        for c in sccs(nodes, succ):
            if len(c) > 1:
                src = {i for (q, a, b), ids in auth_src.items() if q == p and a in c and b in c for i in ids}
                out.append(V("superiority-cycle", src, f"authority order on {p} ranks {sorted(c)} both ways ({sorted(src)})"))
    def explicit(a, b): return b in (items[a].get("superior-to") or [])
    def authority(a, b):
        A, B = items[a], items[b]
        if "assertion" not in A or "assertion" not in B: return False
        return (A.get("asserted_by"), B.get("asserted_by")) in auth.get(pred_of(A), ())
    def strict(a, b): return items[a].get("kind") == "strict" and items[b].get("kind") not in ("strict", None)
    def later(a, b):
        A, B = items[a], items[b]
        return ("assertion" in A and "assertion" in B and A.get("asserted_by") == B.get("asserted_by")
                and str(A.get("asserted_at")) > str(B.get("asserted_at")))
    def sup(a, b):
        for f in (explicit, authority, strict, later):
            if f(a, b) or f(b, a): return f(a, b)
        return False
    by_pred = {}
    for i, x in items.items(): by_pred.setdefault(pred_of(x), []).append(i)
    pairs = {(a, b) for ids in by_pred.values() for a in ids for b in ids if a != b}
    pairs |= {(a, b) for a in items for b in (items[a].get("superior-to") or []) if b in items}
    succ = {}
    for a, b in pairs:
        if sup(a, b): succ.setdefault(a, set()).add(b)
    for a in items:
        if explicit(a, a):
            out.append(V("superiority-cycle", [a], f"{a} is declared superior to itself"))
    for c in sccs(set(items), succ):
        if len(c) > 1:
            src = {i for (q, a, b), ids in auth_src.items() for i in ids
                   if any(pred_of(items[m]) == q and items[m].get("asserted_by") in (a, b) for m in c)}
            out.append(V("superiority-cycle", c | src, f"superiority is not a strict partial order over {sorted(c)}"))
    return out


def definition_artifacts(S, rules):
    """IR-002. The artifacts that define a predicate (= a vocabulary term's name, term:<name>):
      the binding artifact: the concept named <name> (a semantic-layer binding), together with its
        :derived-by rule and any :definition rule of the term's owner whose body is a single fetch of
        that concept (such a rule only exposes the binding as a predicate);
      a rule artifact per owner: the remaining :class :definition rules with head predicate <name>,
        grouped by :owner.
    -> {predicate: [(artifact label, [ids])]}. A predicate defined by two or more artifacts violates IR-002."""
    concepts = {kw(c["name"]): c for c in S.get("concepts") or []}
    owner = {t["id"].split(":", 1)[1]: kw(t.get("owner")) for t in S.get("terms") or []}
    arts = {}
    for p, c in concepts.items():
        if c.get("kind") in ("measure", "dimension", "entity") and f"{p}" in owner:
            arts.setdefault(p, {})["binding"] = {c["id"]} | ({kw(c["derived-by"])} if c.get("derived-by") else set())
    for r in rules:
        if r.get("class") != "definition" or "head" not in r: continue
        p, _, _ = atom(r["head"])
        b = r.get("body") or []
        exposes = (len(b) == 1 and b[0][0] == "fetch" and b[0][1] == p and kw(r.get("owner")) == owner.get(p))
        if p in arts and "binding" in arts[p] and (r["id"] in arts[p]["binding"] or exposes):
            arts[p]["binding"].add(r["id"]); continue
        arts.setdefault(p, {}).setdefault(f"rules:{kw(r.get('owner'))}", set()).add(r["id"])
    return {p: sorted((k, sorted(v)) for k, v in a.items()) for p, a in arts.items()}


def kw(x):
    return x[1:] if isinstance(x, str) and x.startswith(":") else x


def integrity_violations(S, rules, claims):
    """IR-001a .. IR-005 over the active rule base (IR-006 is the moded check in check())."""
    out = []
    cyc = negative_cycles(rules, claims, S.get("functional") or {})
    for c in cyc:
        out.append(V("defeat-cycle", c["rules"], f"negative dependency cycle over {c['predicates']}: {c['negative_edges']}"))
    out += superiority_cycles(rules, claims)
    for p, arts in definition_artifacts(S, rules).items():
        if len(arts) > 1:
            out.append(V("duplicate-definition", [i for _, ids in arts for i in ids],
                         f"{p} is defined by {len(arts)} artifacts: {arts}"))
    for x in list(rules) + list(claims):
        bad = sorted(ORDERING_KEYS & set(x))
        if bad:
            out.append(V("rebuttal-without-preference", [x["id"]],
                         f"{x['id']}: {bad} would order rivals outside superiority"))
    measures = {kw(c["name"]) for c in S.get("concepts") or [] if c.get("kind") == "measure"}
    for c in S.get("concepts") or []:
        if c.get("kind") != "measure": continue
        a = c.get("additivity")
        if a not in ADDITIVITY:
            out.append(V("missing-additivity", [c["id"]], f"{c['id']}: :additivity missing or not one of {sorted(ADDITIVITY)}: {a}"))
        elif a == "semi-additive" and not c.get("unsafe_dims"):
            out.append(V("missing-additivity", [c["id"]], f"{c['id']}: :semi-additive without :unsafe_dims"))
    cl = {c["id"]: c for c in claims}
    for r in rules:
        body = r.get("body") or []
        uses = [f"not {atom(b[1])[0]}" for b in body if b[0] == "not"] + \
               [f"fetch of measure {b[1]}" for b in body if b[0] == "fetch" and b[1] in measures]
        if not uses: continue
        comp, closed = r.get("completeness"), r.get("closed_over")
        if closed == "known_facts" and not comp: continue
        if comp and not closed and isinstance(comp, list):
            bad = [i for i in comp if i not in cl or pred_of(cl[i]) != "complete"]
            if not bad: continue
            out.append(V("negative-without-completeness", [r["id"]] + bad,
                         f"{r['id']}: :completeness {bad} is not an active [:complete ...] claim"))
            continue
        out.append(V("negative-without-completeness", [r["id"]],
                     f"{r['id']} uses {uses} without :completeness [claim ids] or :closed_over :known_facts"))
    for e in shape_errors(S, rules, claims, additivity=False):
        out.append(V("malformed-record", [e.split(":", 1)[0]], e))
    return out


def check(S, rules, claims, questions, declared=None):
    """-> dict(cycles, modes, violations: [{violation, members, message}], errors: [messages], ok)."""
    viol = integrity_violations(S, rules, claims)
    cyc = negative_cycles(rules, claims, S.get("functional") or {})
    unbound = []
    M = Modes(S, rules, claims)
    modes = M.infer()
    for p, ms in modes.items():
        if not ms:
            unbound.append(([p], f"{p}: no safe calling mode at all"))
    declared = declared if declared is not None else {}
    for p in sorted(set(modes) | set(declared)):
        if p not in modes and p not in M.arity: continue          # declared for a predicate not in this rule base
        if sorted(declared.get(p, [])) != modes.get(p, []):
            unbound.append(([p], f"{p}: declared modes {declared.get(p)} != inferred {modes.get(p)}"))
    for p, n in (S.get("functional") or {}).items():
        if p in modes and not any(set(i for i, ch in enumerate(m) if ch == "+") <= set(range(n)) for m in modes[p]):
            unbound.append(([p], f"functional {p}: every mode binds the value position (key {n})"))
    for r in M.rules:                                # every call site: the rule must be safe in some mode
        if r.get("kind") in ("incompatible",): continue
        p = atom(r["head"])[0]
        if not any(M.simulate(r, m)[0] for m in M.safe.get(p, ())):
            unbound.append(([r["id"]], f"{r['id']}: unsafe in every mode: {M.simulate(r, frozenset(range(M.arity[p])))[1]}"))
    for q in questions:
        g = q.get("goal")
        if not g: continue
        p, a, _ = atom(g)
        bp = frozenset(i for i, x in enumerate(a) if not vars_of(x))
        if not M.is_safe(p, bp):
            unbound.append(([q["id"]], f"{q['id']}: goal {p} called with bound {sorted(bp)}, modes {modes.get(p)}"))
    viol += [V("unbound-call", m, msg) for m, msg in unbound]
    errors = [f"{v['violation']}: {v['message']}" for v in viol]
    return dict(cycles=cyc, modes=modes, violations=viol, errors=errors, ok=not viol)


def declared_modes():
    d = plain(E.loads((HERE / "modes.edn").read_text()))
    return {p: (v if isinstance(v, list) else [v]) for p, v in d.items()}


def rule_base(cycles=True, extra=()):
    """slice + extension (+ cycles-acyclic.edn with cycles) + the records of each extra EDN file."""
    S, X, Q, Y, QC = load(cycles=True)
    recs = X + (Y if cycles else [])
    for f in extra:
        recs = recs + plain(list(E.loads(pathlib.Path(f).read_text())))
    rules = list(S["rules"]) + [x for x in recs if "head" in x or "pred" in x]
    claims = list(S["claims"]) + [x for x in recs if "assertion" in x]
    return S, rules, claims, Q + (QC if cycles else [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", action="store_true", help="include cycles-acyclic.edn")
    ap.add_argument("--fixture", action="append", default=[], help="add the records of this EDN file (e.g. fixtures/integrity/y2-even-loop.edn)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    S, rules, claims, Q = rule_base(a.cycles, a.fixture)
    res = check(S, rules, claims, Q, declared_modes())
    if a.json:
        print(json.dumps(res, indent=1)); return 0 if res["ok"] else 1
    print(f"rule base: slice + extension{' + cycles-acyclic' if a.cycles else ''}{''.join(' + ' + f for f in a.fixture)}")
    print(f"negative cycles: {len(res['cycles'])}")
    for c in res["cycles"]:
        print("  ", c["predicates"], "rules", c["rules"]); [print("     ", e) for e in c["negative_edges"]]
    print("modes:", ", ".join(f"{p} {'|'.join(m)}" for p, m in res["modes"].items()))
    print("errors:", len(res["errors"])); [print("  ", e) for e in res["errors"]]
    print("OK" if res["ok"] else "REJECTED")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
