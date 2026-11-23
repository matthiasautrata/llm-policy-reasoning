"""Shared helpers for the projections: which relations, rules, forks and concepts a layer shows.

Configurations (cfg):
  decided  forked rules appear only in their decided reading, and the decisions are stated
  open     forked rules appear with every reading, marked undecided (no decision is stated)
"""
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = yaml.safe_load((ROOT / "world/schema.yaml").read_text())["relations"]
RULES = yaml.safe_load((ROOT / "rules/rules.yaml").read_text())
FORKS = {f["id"]: f for f in RULES["forks"]}
CONFIGS = ("decided", "open")


def relations(k):
    """Schema records of the relations shown at layer k (layers are cumulative)."""
    return [r for r in SCHEMA if r["layer"] <= k]


def forks(k):
    return [f for f in RULES["forks"] if f["layer"] <= k]


def concepts(k):
    return RULES["concepts"] if k >= 1 else []


def items(k, cfg):
    """The rule records of layers 1..k in file order, as ('rule', rec) and ('fork', fork, [recs]).
    decided: a forked rule appears as its decided reading only. open: the records of one fork are
    grouped at the position of the first one, one per reading."""
    out, seen = [], set()
    for r in RULES["rules"]:
        if r["layer"] > k:
            continue
        f = r.get("fork")
        if not f:
            out.append(("rule", r))
        elif cfg == "decided":
            if f["reading"] == FORKS[f["id"]]["decided"]:
                out.append(("rule", r))
        elif f["id"] not in seen:
            seen.add(f["id"])
            recs = [x for x in RULES["rules"] if (x.get("fork") or {}).get("id") == f["id"]]
            out.append(("fork", FORKS[f["id"]], sorted(recs, key=lambda x: FORKS[f["id"]]["readings"].index(x["fork"]["reading"]))))
    return out


def material_dir(k, cfg):
    return f"L{k}" if cfg == "decided" or k == 0 else f"L{k}-open"


def date_int(s):
    return int(s.replace("-", ""))
