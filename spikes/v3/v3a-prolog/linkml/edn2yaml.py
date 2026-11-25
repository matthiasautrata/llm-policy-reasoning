"""slice.edn (+ extension.edn) -> LinkML instance YAML (slice.instance.yaml), for linkml-validate and gen-doc.

Field names map to snake_case slots. Rule heads, bodies and claim assertions become structured objects
(PLAN-v3a-fix F2): each literal and term is an object whose `type` names its LinkML class (designates_type):
  literal  Derived{pred, args}  Fetch{concept, filters, outputs}  Not{literal}  Neg{literal}
           Comparison{op, left, right}  Is{var, expr}  AsOf{date}
  term     Var{name}  Str{value}  Int{value}  Bool{value}  Expr{op, left, right}
The mapping is faithful, not validating: positions beyond a form's arity go to `extra`, a non-map filter
or output becomes a list, a keyword where a term belongs becomes Keyword{name}. The schema rejects those;
this converter never repairs or drops anything. to_edn() renders the structure back to EDN text (instance
docs, and the round-trip check in build.py). Run: .venv/bin/python spikes/v3/v3a-prolog/linkml/edn2yaml.py
"""
import datetime, json, pathlib
import edn_format as E, yaml

HERE = pathlib.Path(__file__).resolve().parent
SHARED = HERE.parents[1] / "shared"
RENAME = {"code-lists": "code_lists", "derived-by": "derived_by", "superior-to": "superior_to", "class": "rule_class",
          "code-list": "code_list", "type": "column_type"}
CMP = {"<", "<=", ">", ">=", "="}


def name(k):
    return k.name if isinstance(k, (E.Keyword, E.Symbol)) else str(k)


def iso(x):
    return x.isoformat()[:10] if isinstance(x, (datetime.date, datetime.datetime)) else x


def thaw(x):
    """edn_format's immutable values -> plain dict/list (Keyword, Symbol, dates kept), so tests can mutate them."""
    if hasattr(x, "items"): return {k: thaw(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)) or type(x).__name__ == "ImmutableList": return [thaw(v) for v in x]
    return x


def read(path):
    return thaw(E.loads(path.read_text()))


# ------------------------------------------------------------------ rule language -> structure

def term(x):
    if isinstance(x, E.Symbol): return {"type": "Var", "name": x.name}
    if isinstance(x, bool): return {"type": "Bool", "value": x}
    if isinstance(x, int): return {"type": "Int", "value": x}
    if isinstance(x, str): return {"type": "Str", "value": x}
    if isinstance(x, E.Keyword): return {"type": "Keyword", "name": x.name}
    if isinstance(x, list) and x and isinstance(x[0], E.Keyword):
        return positional("Expr", {"op": x[0].name}, ["left", "right"], [term(v) for v in x[1:]])
    return x


def positional(t, out, slots, vals):
    out = {"type": t, **out}
    for s, v in zip(slots, vals): out[s] = v
    if len(vals) > len(slots): out["extra"] = vals[len(slots):]
    return out


def mapping(m, val):
    return {name(k): val(v) for k, v in m.items()} if isinstance(m, dict) else [val(v) for v in m] if isinstance(m, list) else m


def literal(x):
    if not (isinstance(x, list) and x and isinstance(x[0], E.Keyword)):
        return term(x)                                        # not a literal: the schema rejects it where a literal belongs
    k, rest = x[0].name, x[1:]
    if k == "fetch":
        vals = [name(v) for v in rest[:1]] + [mapping(m, term) for m in rest[1:3]] + [term(v) for v in rest[3:]]
        return positional("Fetch", {}, ["concept", "filters", "outputs"], vals)
    if k in ("not", "neg"):
        return positional(k.capitalize(), {}, ["literal"], [literal(v) for v in rest])
    if k in CMP:
        return positional("Comparison", {"op": k}, ["left", "right"], [term(v) for v in rest])
    if k == "is":
        return positional("Is", {}, ["var", "expr"], [term(v) for v in rest])
    if k == "as_of":
        return positional("AsOf", {}, ["date"], [term(v) for v in rest])
    return {"type": "Derived", "pred": k, "args": [term(v) for v in rest]}


def outputs_as_names(lit):
    """Fetch outputs are variables: emit the variable name (compact dict form, Output{column, var})."""
    if isinstance(lit, dict) and lit.get("type") == "Fetch" and isinstance(lit.get("outputs"), dict):
        lit["outputs"] = {c: (v["name"] if isinstance(v, dict) and v.get("type") == "Var" else v) for c, v in lit["outputs"].items()}
    for k in ("literal",):
        if isinstance(lit, dict) and k in lit: outputs_as_names(lit[k])
    return lit


def lit(x):
    return outputs_as_names(literal(x))


# ------------------------------------------------------------------ structure -> EDN text

def to_edn(s):
    if not isinstance(s, dict): return E.dumps(s)
    t = s["type"]
    def ts(*xs): return " ".join(to_edn(x) for x in xs)
    if t == "Var": return s["name"]
    if t in ("Str", "Int", "Bool"): return E.dumps(s["value"])
    if t == "Expr": return f"[:{s['op']} {ts(s['left'], s['right'])}]"
    if t == "Derived": return "[" + " ".join([":" + s["pred"]] + [to_edn(a) for a in s["args"]]) + "]"
    if t in ("Not", "Neg"): return f"[:{t.lower()} {to_edn(s['literal'])}]"
    if t == "Comparison": return f"[:{s['op']} {ts(s['left'], s['right'])}]"
    if t == "Is": return f"[:is {ts(s['var'], s['expr'])}]"
    if t == "AsOf": return f"[:as_of {to_edn(s['date'])}]"
    if t == "Fetch":
        f = " ".join(f":{c} {to_edn(v)}" for c, v in s["filters"].items())
        o = " ".join(f":{c} {v}" for c, v in s["outputs"].items())
        return f"[:fetch :{s['concept']} {{{f}}} {{{o}}}]"
    raise ValueError(t)


# ------------------------------------------------------------------ records

def plain(x):
    if isinstance(x, (E.Keyword, E.Symbol)): return x.name
    if isinstance(x, (datetime.date, datetime.datetime)): return iso(x)
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            k = name(k)
            if k in ("head", "assertion"): out[k] = lit(v)
            elif k == "body": out[k] = [lit(l) for l in v] if isinstance(v, list) else plain(v)
            elif v is not None: out[RENAME.get(k, k)] = plain(v)
        return out
    if isinstance(x, list): return [plain(v) for v in x]
    return x


def convert(S=None, X=None):
    S = read(SHARED / "slice.edn") if S is None else S
    X = read(SHARED / "extension.edn") if X is None else X
    out = plain(S)
    out["version"] = out.pop("slice/version")
    for c in out["concepts"]:
        c["concept_name"] = c.pop("name")
        if "columns" in c: c["columns_out"] = c.pop("columns")
    for t in out["taxonomies"]:
        t["groups"] = [{"group": g, "members": m} for g, m in t.pop("tree").items()]
    out["functional"] = [{"pred": p, "key_arity": n} for p, n in out["functional"].items()]
    for x in X:
        (out["rules"] if "kind" in plain(x) else out["claims"]).append(plain(x))
    return out


def dump(doc):
    return yaml.safe_dump(json.loads(json.dumps(doc)), sort_keys=False, allow_unicode=True, width=120)


if __name__ == "__main__":
    p = HERE / "slice.instance.yaml"
    p.write_text("# generated by edn2yaml.py from shared/slice.edn + shared/extension.edn; do not edit\n" + dump(convert()))
    print(p, sum(1 for _ in p.open()), "lines")
