"""Formal projection: SWI-Prolog facts. Relations are declared dynamic (an empty relation is a fact
too: nothing holds); the schema itself is stated as relation/1, column/4, key/2 and fk/3 facts.
From L1 on: concept/3 bindings, fork/5 questions, the decisions as decided/2 and reading/2 facts
(decided) or undecided/1 facts with every reading's clauses guarded by reading/2, stated as alternatives (open), rule/6
records, doc/2 meanings, and the clauses themselves, each rule preceded by its id and English.
The file loads on its own: the derived predicates answer the questions the layer can answer."""
from render.common import relations, concepts, forks, items, date_int, RULES


def _val(v, t):
    if t == "date":
        return str(date_int(v))
    if t == "int":
        return str(v)
    return v if v.replace("_", "").isalnum() and v[0].islower() else "'" + v.replace("'", "\\'") + "'"


def _q(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _facts(w, r):
    types = [t for _, t in r["columns"]]
    return [f"{r['name']}({', '.join(_val(v, t) for v, t in zip(row, types))})." for row in w["relations"][r["name"]]]


def facts(w, k):
    """All base facts of layers <= k, as read by the engine (no comments, no schema facts)."""
    return "".join(l + "\n" for r in relations(k) for l in _facts(w, r))


def _guard(text, fork, reading):
    """Insert reading(Fork, Reading) as the first goal of every clause of a rule."""
    out = []
    for line in text.rstrip("\n").split("\n"):
        if line and not line[0].isspace():
            assert " :- " in line, f"forked clause without a body: {line}"
            line = line.replace(" :- ", f" :- reading({fork}, {reading}), ", 1)
        out.append(line)
    return "\n".join(out)


def _rule(r, guard=None):
    owner = r["owner"] or "none"
    out = [f"% {r['id']}: {r['english']}",
           f"rule({_q(r['id'])}, {r['head']}, {r['layer']}, {r['class']}, {str(r['conservative']).lower()}, {owner})."]
    body = r["prolog"].rstrip("\n")
    out.append(_guard(body, *guard) if guard else body)
    return out


def render(w, k, cfg="decided"):
    out = [f"% Procurement world, layer L{k}: base relations" + (", terms, definitions and " +
           ("decisions" if cfg == "decided" else "open questions") if k >= 1 else "") +
           ". Dates are integers YYYYMMDD.", ""]
    if k >= 1:   # L0 stays byte-identical to the material of the M2 run
        out.append(":- discontiguous relation/1, column/4, key/2, fk/3.")
    out.append("% Schema: relation(Name). column(Relation, Column, Position, Type). key(Relation, FirstKeyColumn). fk(Relation, Column, ReferencedRelation).")
    for r in relations(k):
        out.append(f"relation({r['name']}).")
        out += [f"column({r['name']}, {c}, {i}, {t})." for i, (c, t) in enumerate(r["columns"], 1)]
        out.append(f"key({r['name']}, {r['columns'][0][0]}).")
        out += [f"fk({r['name']}, {c}, {ref})." for c, ref in (r.get("fks") or {}).items()]
    for r in relations(k):
        args = ", ".join(c.capitalize() for c, _ in r["columns"])
        out += ["", f"% {r['name']}({args}): {r['doc']}", f":- dynamic {r['name']}/{len(r['columns'])}."]
        out += _facts(w, r)
    if k < 1:
        return "\n".join(out) + "\n"

    its = items(k, cfg)
    recs = [it[1] for it in its if it[0] == "rule"] + [x for it in its if it[0] == "fork" for x in it[2]]
    heads = list(dict.fromkeys(r["head"] for r in recs))
    out += ["", "% Terms: concept(Term, Binding, Meaning) -- what the terms used by the definitions refer to.",
            f":- discontiguous {', '.join(['concept/3', 'rule/6', 'doc/2'] + heads)}."]
    out += [f"concept({_q(c['term'])}, {_q(c['binding'])}, {_q(c['english'])})." for c in concepts(k)]
    out += ["", "% Questions of interpretation: fork(Id, Owner, Term, Question, Readings).",
            ":- dynamic reading/2."]
    for f in forks(k):
        out.append(f"fork({f['id']}, {f['owner']}, {_q(f['term'])}, {_q(f['question'])}, [{', '.join(f['readings'])}]).")
    if cfg == "decided":
        out.append("% Decisions: decided(Fork, Reading). The definitions below follow them; reading/2 is what a rule consults.")
        out += [f"decided({f['id']}, {f['decided']})." for f in forks(k)]
        out += [f"reading({f['id']}, {f['decided']})." for f in forks(k)]
    else:
        out.append("% Open questions: undecided(Fork). The material does not choose between a fork's readings; each "
                   "is an alternative it allows. Each reading's clauses below are guarded by reading(Fork, Reading), "
                   "and no reading/2 fact is given: to evaluate a predicate under a reading, assume reading(Fork, Reading).")
        out += [f"undecided({f['id']})." for f in forks(k)]
    out += ["", "% Definitions: rule(Id, Head, Layer, Class, Conservative, Owner); doc(Head, Meaning); then the clauses.",
            "% Owner none: no one could reasonably read the rule differently."]
    out += [f"doc({h}, {_q(RULES['docs'][h])})." for h in heads]
    tabled = sorted({r["head"] for r in recs if r.get("table")})
    if tabled:
        out.append(f":- table {', '.join(tabled)}.")
    for it in its:
        out.append("")
        if it[0] == "rule":
            out += _rule(it[1])
        else:
            f = it[1]
            out.append(f"% Open question {f['id']} (owner: {f['owner']}), on {f['term']}: {f['question']} Not decided; the readings below are alternatives, one rule per reading.")
            for x in it[2]:
                out += _rule(x, guard=(f["id"], x["fork"]["reading"]))
    return "\n".join(out) + "\n"
