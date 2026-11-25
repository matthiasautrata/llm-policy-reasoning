"""V3e translator: EDN rules and claims (plain form) -> ASP text, at load time (PLAN-v3-cycles §3.1).

Each record is translated once when it is loaded or added; an op's program is META + the texts of the
records it can see + a few per-op facts (asof/1, dm/2 goal demand). Nothing is written to the source tree.

Two layers per rule r with head literal p(..) (or [:neg p(..)]):

1 Grounding skeleton (positive, so gringo computes it as facts while grounding):
    h(inst("r", (V1..Vn)), pos|neg, p(..)) :- dm(p, (bound head args)), <positive body>.
  inst/2 carries every rule variable (first-appearance order), so the host can rebuild bindings for the
  why tree. The positive body has derived literals as pos(L), fetches as frow(concept, Filters, Row),
  builtins as ASP comparisons/assignments, [:as_of ?d] as asof(V_d); [:not L] is left out (over-
  approximation; its truth enters in layer 2).
  Demand (a magic-set rewrite driven by modes.edn): for body position i, a rule deriving the demand of
  literal i from the guard and the positive prefix before i:
    fetch           need(concept, Filters) :- guard, prefix.
    derived / not   dm(q, (args at q's "+" positions)) :- guard, prefix.
  The meta rule frow(C, F, R) :- need(C, F), R = @fetch(C, F) calls the host's SQL boundary during
  grounding for each demanded filter set, so only demanded rows are ever fetched (check 5).
  Demand is keyed by predicate, regardless of sign, so attackers ([:neg p]) and functional rivals of a
  demanded literal are grounded too.

2 Truth (Tr_p of the SEMANTICS-cycles.md metaprogram; Janhunen et al. 2006): every normal rule
  a :- B+, not B- becomes   t_a :- t_B+, not p_B-.   p_a :- p_B+, not t_B-.   :- t_a, not p_a.
  The stable models of the doubled program are the partial stable models of the original; the
  well-founded model is the knowledge-least of them, so WFS true = t_X in the cautious consequences, and
  WFS non-false = p_X in the brave consequences. Per rule only the body rule is emitted here
  (t_body / p_body); def / ovr / beat are generic (META).

2' Status (default, PLAN-v3-integrity §4; encoding "plain", ENCODING below): the base is acyclic (integrity gate),
  so a plain two-valued, stratified program with explicit status atoms computes ambiguity propagation
  (SEMANTICS.md) in its single stable model. Per rule:
    bref(I) :- hd, ref(X).            for a derived body literal X        (a refuted literal refutes the body)
    bref(I) :- hd, pro(X).            for [:not X]
    bpro(I) :- hd, active(r), pro(X1), .., ref(N1), ..                    (every literal proven)
    lit_(X) :- hd.                    X gets a status even without a supporter (refuted, vacuously)
  PROP_META derives live/beaten/pro/ref/con from those (team defeat). The doubled encoding (2) is retired
  behind V3E_ENCODING=doubled (ambiguity blocking; accept.py --semantics blocking).

Terms: ?x -> V_x; strings stay strings; true/false/null constants; integers (32-bit in clingo); rule
and claim ids are strings; predicates are function symbols; [:neg L] -> neg(L).
"""
import json, os, re

ENCODING = os.environ.get("V3E_ENCODING", "plain")   # plain (propagation, default) | doubled (retired, WFS blocking)
if ENCODING not in ("plain", "doubled"):
    raise ValueError(f"V3E_ENCODING={ENCODING!r}: plain | doubled")

CMP = {"<": "<", "<=": "<=", ">": ">", ">=": ">=", "=": "="}
IDENT = re.compile(r"^[a-z][A-Za-z0-9_]*$")


class TranslateError(ValueError):
    pass


def is_var(x):
    return isinstance(x, str) and x.startswith("?")


def var(x):
    return "V_" + re.sub(r"[^A-Za-z0-9_]", "_", x[1:])


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def pn(p):
    if not isinstance(p, str) or not IDENT.match(p):
        raise TranslateError(f"predicate name {p!r} is not an ASP identifier")
    return p


def term(x):
    if is_var(x): return var(x)
    if isinstance(x, bool): return "true" if x else "false"
    if x is None: return "null"
    if isinstance(x, int):
        if not -2**31 <= x < 2**31: raise TranslateError(f"integer {x} does not fit clingo's 32-bit range")
        return str(x)
    if isinstance(x, float) and x.is_integer(): return term(int(x))
    if isinstance(x, str): return q(x)
    raise TranslateError(f"cannot translate term {x!r}")


def expr(x):
    if isinstance(x, list) and x and x[0] in ("+", "-"):
        return f"({expr(x[1])}{x[0]}{expr(x[2])})"
    return term(x)


def tup(xs):
    xs = list(xs)
    return "()" if not xs else "(" + ",".join(xs) + ("," if len(xs) == 1 else "") + ")"


def atom(A):
    """[p, a1..] -> p(a1,..) (no args: p)"""
    return pn(A[0]) + (("(" + ",".join(term(a) for a in A[1:]) + ")") if len(A) > 1 else "")


def lit(L):
    return f"neg({atom(L[1])})" if L[0] == "neg" else atom(L)


def base_atom(L):
    return L[1] if L[0] == "neg" else L


def bound_positions(p, modes):
    """argument indices bound in every declared mode of p ("+"); none if p has no mode (claims-only)."""
    ms = modes.get(p) or []
    if not ms: return []
    n = min(len(m) for m in ms)
    return [i for i in range(n) if all(m[i] == "+" for m in ms)]


def dm(L, modes):
    A = base_atom(L)
    return f"dm({pn(A[0])},{tup(term(A[1 + i]) for i in bound_positions(A[0], modes) if 1 + i < len(A))})"


def vars_in(x, out):
    if is_var(x):
        if x not in out: out.append(x)
    elif isinstance(x, list):
        for y in x: vars_in(y, out)
    elif isinstance(x, dict):
        for k in sorted(x): vars_in(x[k], out)
    return out


def rule_vars(r):
    """every variable of the rule, head first, then body, in first-appearance order"""
    out = []
    vars_in(r.get("head"), out)
    for b in r.get("body") or []:
        if b[0] == "fetch":
            vars_in(b[2] or {}, out); vars_in(b[3] or {}, out)
        else:
            vars_in(b, out)
    return out


def filters_term(F):
    return tup(f"({q(c)},{term(F[c])})" for c in sorted(F))


def fetch_atoms(b, concepts):
    c, F, O = b[1], b[2] or {}, b[3] or {}
    cols = concepts.get(c)
    if cols is None:
        raise TranslateError(f"fetch of unknown concept {c}")
    for k in O:
        if k not in cols: raise TranslateError(f"concept {c} has no column {k}")
    row = tup(term(O[k]) if k in O else "_" for k in cols)
    return f"need({q(c)},{filters_term(F)})", f"frow({q(c)},{filters_term(F)},{row})"


def is_builtin(b):
    return b[0] in CMP or b[0] in ("is", "as_of")


def builtin(b):
    if b[0] == "as_of": return f"asof({term(b[1])})"
    if b[0] == "is": return f"{term(b[1])}={expr(b[2])}"
    return f"{expr(b[1])}{CMP[b[0]]}{expr(b[2])}"


def translate_rule(r, modes, concepts):
    rid, kind = r["id"], r["kind"]
    out = [f"% {rid} ({kind})", f"kind({q(rid)},{kind}).", f"#external active({q(rid)}). [free]"]
    for w in r.get("superior-to") or []:
        out.append(f"superior_to({q(rid)},{q(w)}).")
    if kind == "superiority":
        for i, by in enumerate(r.get("order") or []):
            out.append(f"order({q(rid)},{pn(r['pred'])},{term(by)},{i}).")
        return "\n".join(out) + "\n"
    H, B = r["head"], r.get("body") or []
    A = base_atom(H)
    sign = "neg" if H[0] == "neg" else "pos"
    guard = dm(H, modes)
    I = f"inst({q(rid)},{tup(var(v) for v in rule_vars(r))})"
    pos, tb, pb, st, refs, lits = [], [], [], [], [], []
    for b in B:
        prefix = ", ".join([guard] + pos)
        if b[0] == "fetch":
            need, fr = fetch_atoms(b, concepts)
            out.append(f"{need} :- {prefix}.")
            pos.append(fr)
        elif b[0] == "not":
            out.append(f"{dm(b[1], modes)} :- {prefix}.")
            tb.append(f"not p_def({lit(b[1])})"); pb.append(f"not t_def({lit(b[1])})")
            st.append(f"ref({lit(b[1])})"); refs.append(f"pro({lit(b[1])})"); lits.append(lit(b[1]))
        elif is_builtin(b):
            pos.append(builtin(b))
        else:
            out.append(f"{dm(b, modes)} :- {prefix}.")
            pos.append(f"pos({lit(b)})")
            tb.append(f"t_def({lit(b)})"); pb.append(f"p_def({lit(b)})")
            st.append(f"pro({lit(b)})"); refs.append(f"ref({lit(b)})"); lits.append(lit(b))
    hd = f"ih({I},{atom(A)})" if kind == "incompatible" else f"h({I},{sign},{atom(A)})"
    out.append(f"{hd} :- {', '.join([guard] + pos)}.")
    if ENCODING == "doubled":
        for t, xs in (("t_body", tb), ("p_body", pb)):
            out.append(f"{t}({I}) :- {', '.join([hd, f'active({q(rid)})'] + xs)}.")
    else:
        out.append(f"bpro({I}) :- {', '.join([hd, f'active({q(rid)})'] + st)}.")
        out += [f"bref({I}) :- {hd}, {x}." for x in refs]
        out += [f"lit_({x}) :- {hd}." for x in dict.fromkeys(lits)]
    return "\n".join(out) + "\n"


def translate_claim(c):
    A = c["assertion"]
    sign = "neg" if A[0] == "neg" else "pos"
    cid = c["id"]
    return "\n".join([
        f"% {cid} (claim)", f"kind({q(cid)},claim).", f"#external active({q(cid)}). [free]",
        f"claimrec({q(cid)},{sign},{atom(base_atom(A))},{term(c['valid_from'])},{term(c.get('valid_to'))}).",
        f"cby({q(cid)},{term(c['asserted_by'])}). cat({q(cid)},{term(c['asserted_at'])}). cpred({q(cid)},{pn(base_atom(A)[0])}).",
    ]) + "\n"


def functional_rules(functional):
    """rivals of a functional predicate p (key arity k): same key, another value"""
    out = []
    for p, k in sorted(functional.items()):
        K = ",".join(f"K{i}" for i in range(k))
        a = lambda v: f"{pn(p)}({K + ',' if K else ''}{v})"
        out.append(f"attacks(J,{a('V1')}) :- h(J,pos,{a('V2')}), h(_,pos,{a('V1')}), V1!=V2.")
    return "\n".join(out) + "\n"


META = r"""
% ---- fetch: demanded filter sets are served by the host during grounding
frow(C,F,R) :- need(C,F), R = @fetch(C,F).
pos(A) :- h(_,pos,A).
pos(neg(A)) :- h(_,neg,A).

% ---- claims: in force on asof, body-less instances
inforce(C) :- claimrec(C,_,_,F,null), asof(D), F <= D.
inforce(C) :- claimrec(C,_,_,F,T), T != null, asof(D), F <= D, D <= T.
h(inst(C,()),S,A) :- claimrec(C,S,A,_,_), inforce(C).
t_body(inst(C,())) :- h(inst(C,()),_,_), kind(C,claim), active(C).
p_body(inst(C,())) :- h(inst(C,()),_,_), kind(C,claim), active(C).

% ---- supporters and attackers (defeaters attack only)
supports(I,A) :- h(I,pos,A), I = inst(R,_), not kind(R,defeater).
supports(I,neg(A)) :- h(I,neg,A), I = inst(R,_), not kind(R,defeater).
attacks(J,neg(A)) :- h(J,pos,A).
attacks(J,A) :- h(J,neg,A).

% ---- superiority: explicit, strict over non-strict, asserter authority (scoped to a predicate), later
sup(W,L,explicit) :- superior_to(W,L).
sup(W,L,strict) :- kind(W,strict), kind(L,K), K != strict.
sup(W,L,auth(S)) :- cpred(W,P), cpred(L,P), cby(W,BW), cby(L,BL), BW != BL,
                    order(S,P,BW,NW), order(S,P,BL,NL), NW < NL, active(S).
sup(W,L,later) :- cby(W,B), cby(L,B), cat(W,AW), cat(L,AL), AW > AL.

% ---- the metaprogram (SEMANTICS-cycles.md), doubled (Tr_p): t_ = true, p_ = possibly true
%   def(L)    :- supports(I,L), body(I), not ovr(L).
%   ovr(L)    :- attacks(J,L), body(J), not beat(J,L).
%   beat(J,L) :- attacks(J,L), supports(I,L), sup(rule(I), rule(J)), body(I).
t_def(L) :- supports(I,L), t_body(I), not p_ovr(L).
p_def(L) :- supports(I,L), p_body(I), not t_ovr(L).
t_ovr(L) :- attacks(J,L), t_body(J), not p_beat(J,L).
p_ovr(L) :- attacks(J,L), p_body(J), not t_beat(J,L).
t_beat(J,L) :- attacks(J,L), supports(I,L), I = inst(R,_), J = inst(Q,_), sup(R,Q,_), t_body(I).
p_beat(J,L) :- attacks(J,L), supports(I,L), I = inst(R,_), J = inst(Q,_), sup(R,Q,_), p_body(I).
:- t_def(L), not p_def(L).
:- t_ovr(L), not p_ovr(L).
:- t_beat(J,L), not p_beat(J,L).
:- t_body(I), not p_body(I).

#show t_def/1. #show p_def/1. #show t_body/1. #show p_body/1. #show t_beat/2. #show sup/3.
"""

# Ambiguity propagation with explicit status atoms (ENCODING "plain", the default; PLAN-v3-integrity §4.2).
# Stratified over an acyclic base: one stable model. pro = +delta, ref = -sigma, con = +sigma and -delta.
PROP_META = r"""
frow(C,F,R) :- need(C,F), R = @fetch(C,F).
pos(A) :- h(_,pos,A).
pos(neg(A)) :- h(_,neg,A).
inforce(C) :- claimrec(C,_,_,F,null), asof(D), F <= D.
inforce(C) :- claimrec(C,_,_,F,T), T != null, asof(D), F <= D, D <= T.
h(inst(C,()),S,A) :- claimrec(C,S,A,_,_), inforce(C).
bpro(inst(C,())) :- h(inst(C,()),_,_), kind(C,claim), active(C).
supports(I,A) :- h(I,pos,A), I = inst(R,_), not kind(R,defeater).
supports(I,neg(A)) :- h(I,neg,A), I = inst(R,_), not kind(R,defeater).
attacks(J,neg(A)) :- h(J,pos,A).
attacks(J,A) :- h(J,neg,A).
sup(W,L,explicit) :- superior_to(W,L).
sup(W,L,strict) :- kind(W,strict), kind(L,K), K != strict.
sup(W,L,auth(S)) :- cpred(W,P), cpred(L,P), cby(W,BW), cby(L,BL), BW != BL,
                    order(S,P,BW,NW), order(S,P,BL,NL), NW < NL, active(S).
sup(W,L,later) :- cby(W,B), cby(L,B), cat(W,AW), cat(L,AL), AW > AL.
% live: active and the body not refuted; bpro implies live
act(I) :- h(I,_,_), I = inst(R,_), active(R).
live(I) :- act(I), not bref(I).
lit_(L) :- supports(_,L).
lit_(L) :- attacks(_,L).
% team defeat: an attacker is beaten by a superior supporter with a proven body, and vice versa
beaten(J,L) :- attacks(J,L), live(J), supports(I,L), bpro(I), I = inst(R,_), J = inst(Q,_), sup(R,Q,_).
sbeaten(I,L) :- supports(I,L), live(I), attacks(J,L), bpro(J), I = inst(R,_), J = inst(Q,_), sup(Q,R,_).
lsu(L) :- supports(I,L), live(I), not sbeaten(I,L).
unb(L) :- attacks(J,L), live(J), not beaten(J,L).
ref(L) :- lit_(L), not lsu(L).
pro(L) :- supports(I,L), bpro(I), not unb(L), not ref(L).
con(L) :- lit_(L), not pro(L), not ref(L).
#show pro/1. #show con/1. #show bpro/1. #show live/1.
"""

# A plain (undoubled) encoding of the same metaprogram, for the stable-model probe (probe_stable.py):
# its stable models are the two-valued ones; Y2 has two, Y3 (an odd loop through `not`) none.
PLAIN_META = r"""
frow(C,F,R) :- need(C,F), R = @fetch(C,F).
pos(A) :- h(_,pos,A).
pos(neg(A)) :- h(_,neg,A).
inforce(C) :- claimrec(C,_,_,F,null), asof(D), F <= D.
inforce(C) :- claimrec(C,_,_,F,T), T != null, asof(D), F <= D, D <= T.
h(inst(C,()),S,A) :- claimrec(C,S,A,_,_), inforce(C).
body(inst(C,())) :- h(inst(C,()),_,_), kind(C,claim), active(C).
supports(I,A) :- h(I,pos,A), I = inst(R,_), not kind(R,defeater).
supports(I,neg(A)) :- h(I,neg,A), I = inst(R,_), not kind(R,defeater).
attacks(J,neg(A)) :- h(J,pos,A).
attacks(J,A) :- h(J,neg,A).
sup(W,L,explicit) :- superior_to(W,L).
sup(W,L,strict) :- kind(W,strict), kind(L,K), K != strict.
sup(W,L,auth(S)) :- cpred(W,P), cpred(L,P), cby(W,BW), cby(L,BL), BW != BL,
                    order(S,P,BW,NW), order(S,P,BL,NL), NW < NL, active(S).
sup(W,L,later) :- cby(W,B), cby(L,B), cat(W,AW), cat(L,AL), AW > AL.
def(L) :- supports(I,L), body(I), not ovr(L).
ovr(L) :- attacks(J,L), body(J), not beat(J,L).
beat(J,L) :- attacks(J,L), supports(I,L), I = inst(R,_), J = inst(Q,_), sup(R,Q,_), body(I).
#show def/1.
"""


def plain_rule_body(text):
    """the per-rule text for PLAIN_META: t_body rule -> body rule (t_def/p_def -> def), p_body dropped"""
    out = []
    for line in text.splitlines():
        if line.startswith("p_body("): continue
        if line.startswith("t_body("):
            line = "body(" + line[len("t_body("):]
            line = line.replace("t_def(", "def(").replace("not p_def(", "not def(")
        out.append(line)
    return "\n".join(out) + "\n"
