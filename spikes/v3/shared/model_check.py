"""Shared model check over the rule base (PLAN-v3-cycles §1.4, amendment A2). Engine-independent.

  python spikes/v3/shared/model_check.py [--cycles] [--engine v3a-prolog] [--mode wfs]

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
3 Strictness comes from the engine: capabilities.json in the spike directory {"cycles": "reject" | "report"}
  (with --mode, {"modes": {mode: flag}}). With "reject", a rule base that has a negative cycle fails.
  Moded errors fail on every engine.

Library: check(S, rules, claims, questions, cycles_flag) -> dict(cycles=[...], modes={...}, errors=[...], ok=bool)
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


def check(S, rules, claims, questions, cycles_flag="report", declared=None):
    errors = []
    cyc = negative_cycles(rules, claims, S.get("functional") or {})
    if cyc and cycles_flag == "reject":
        errors.append(f"negative cycle(s) rejected (engine flag cycles: reject): {[c['predicates'] for c in cyc]}")
    M = Modes(S, rules, claims)
    modes = M.infer()
    for p, ms in modes.items():
        if not ms:
            errors.append(f"{p}: no safe calling mode at all")
    declared = declared if declared is not None else {}
    for p in sorted(set(modes) | set(declared)):
        if p not in modes and p not in M.arity: continue          # declared for a predicate not in this rule base
        if sorted(declared.get(p, [])) != modes.get(p, []):
            errors.append(f"{p}: declared modes {declared.get(p)} != inferred {modes.get(p)}")
    for p, n in (S.get("functional") or {}).items():
        if p in modes and not any(set(i for i, ch in enumerate(m) if ch == "+") <= set(range(n)) for m in modes[p]):
            errors.append(f"functional {p}: every mode binds the value position (key {n})")
    for r in M.rules:                                # every call site: the rule must be safe in some mode
        if r.get("kind") in ("incompatible",): continue
        p = atom(r["head"])[0]
        if not any(M.simulate(r, m)[0] for m in M.safe.get(p, ())):
            errors.append(f"{r['id']}: unsafe in every mode: {M.simulate(r, frozenset(range(M.arity[p])))[1]}")
    for q in questions:
        g = q.get("goal")
        if not g: continue
        p, a, _ = atom(g)
        bp = frozenset(i for i, x in enumerate(a) if not vars_of(x))
        if not M.is_safe(p, bp):
            errors.append(f"{q['id']}: goal {p} called with bound {sorted(bp)}, modes {modes.get(p)}")
    return dict(cycles=cyc, modes=modes, errors=errors, ok=not errors)


def declared_modes():
    d = plain(E.loads((HERE / "modes.edn").read_text()))
    return {p: (v if isinstance(v, list) else [v]) for p, v in d.items()}


def engine_flag(engine, mode=None):
    cap = json.loads((HERE.parent / engine / "capabilities.json").read_text())
    return cap["modes"][mode]["cycles"] if mode else cap["cycles"]


def rule_base(cycles=True):
    S, X, Q, Y, QC = load(cycles=True)
    recs = X + (Y if cycles else [])
    rules = list(S["rules"]) + [x for x in recs if "head" in x or "pred" in x]
    claims = list(S["claims"]) + [x for x in recs if "assertion" in x]
    for c in list(claims):
        claims += [dict(s, about=c["about"]) for s in c.get("subclaims") or []]
    return S, rules, claims, Q + (QC if cycles else [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", action="store_true", help="include cycles.edn")
    ap.add_argument("--engine", help="spike directory with capabilities.json")
    ap.add_argument("--mode", help="engine mode (capabilities.json modes)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    flag = engine_flag(a.engine, a.mode) if a.engine else "report"
    S, rules, claims, Q = rule_base(a.cycles)
    res = check(S, rules, claims, Q, flag, declared_modes())
    if a.json:
        print(json.dumps(res, indent=1)); return 0 if res["ok"] else 1
    print(f"rule base: slice + extension{' + cycles' if a.cycles else ''}; engine {a.engine or '-'} {a.mode or ''} cycles: {flag}")
    print(f"negative cycles: {len(res['cycles'])}")
    for c in res["cycles"]:
        print("  ", c["predicates"], "rules", c["rules"]); [print("     ", e) for e in c["negative_edges"]]
    print("modes:", ", ".join(f"{p} {'|'.join(m)}" for p, m in res["modes"].items()))
    print("errors:", len(res["errors"])); [print("  ", e) for e in res["errors"]]
    print("OK" if res["ok"] else "REJECTED")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
