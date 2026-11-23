"""M1 test: the engine and the independent reference agree on every key.

  python verify/check.py                 # all of worlds/; exits 1 on any mismatch
  python verify/check.py worlds/S-s1     # some worlds (skips the regeneration check)

All worlds:
  fresh      world/gen.py regenerates worlds/ byte for byte (the committed worlds are its output)
Per world:
  engine     keys.pl re-run on questions.json reproduces keys.json (generation is deterministic)
  reference  verify/reference.py gives the same status and value as keys.json, decided and open
  meta       the engine's derived min_layer and forks equal the bank's declarations
  L0 = L2    the current values L0 shows agree with what L2's history says on today
  rows       every rendered representation of every layer holds exactly the world's rows of each
             relation it shows, none dropped, merged or added (so both sides of a disagreement
             survive ingestion: hr's and finance's assignment records alike)
  formal     each rendered formal.pl with rules (L1-L3, decided and open), loaded on its own in
             SWI-Prolog, reproduces the keys of its layer: decided ANSWER keys as they are; open keys
             under every combination of the question's open forks, asserted as reading/2 facts; a
             question keyed UNDERDETERMINED raises an existence error (its predicates are absent); and
             for a question keyed CONFLICT its conflict goal holds and, for a sym or int goal,
             the goal's values are exactly the key's sides (both survive ingestion); where a resolve
             rule settles a conflict (Q25 at L3, R313), the resolve goal gives the ANSWER key
  why        verify/why.pl: the why/2 tree of every true instance of every derived predicate (L3,
             decided and every reading combination; up to 200 instances per predicate and readings)
             re-verifies with check_why/3, and a corrupted tree is rejected; the why keys
             (keys.json "why", re-checked by keys.pl) name rules of the question's layer
All worlds, after the per-world checks:
  as-of      each dated template (Q21-Q23, Q26) has instances whose key differs from what the
             current (today) value would give, so answering from L0's current values is caught
"""
import filecmp, itertools, json, pathlib, re, subprocess, sys, tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from questions.sample import engine_keys     # noqa: E402
from verify import reference                 # noqa: E402
from render.common import FORKS, RULES, material_dir, relations   # noqa: E402

FORMAL = [(1, "decided"), (1, "open"), (2, "decided"), (2, "open"), (3, "decided"), (3, "open")]   # formal.pl files that must reproduce the keys
MATERIAL = [(0, "decided")] + FORMAL                                  # every rendered material directory


def formal(d, qs, keys):
    """Mismatches between the rendered formal projections and the keys (see the module docstring)."""
    errs = []
    for L, cfg in FORMAL:
        jobs, want = [], []
        for q in qs:
            e, m = keys[cfg][q["id"]][f"L{L}"], keys["meta"][q["id"]]
            if e["status"] == "OUT_OF_SCOPE":
                continue
            live = [f for f in m["forks"] if FORKS[f]["layer"] <= L] if cfg == "open" else []
            for combo in itertools.product(*(FORKS[f]["readings"] for f in live)):
                rs = [[f, r] for f, r in zip(live, combo)]
                if e["status"] == "CONFLICT":     # every reading conflicts alike, else the key would be AMBIGUOUS
                    jobs.append({"id": q["id"], "type": "bool", "goal": q["conflict"], "readings": rs})
                    want.append(("value", True))
                    if q["type"] not in ("bool", "set"):
                        jobs.append({"id": q["id"], "type": "set", "goal": q["goal"], "readings": rs})
                        want.append(("value", e["sides"]))
                    continue
                if e["status"] == "ANSWER":
                    exp = ("value", e["value"])
                elif e["status"] == "AMBIGUOUS":
                    v = e["readings"][",".join(f"{f}={r}" for f, r in rs)]
                    exp = ("value", v)
                else:
                    exp = ("error", "existence_error")
                goal = q["goal"]
                if q.get("resolve"):              # an ANSWER despite the conflict goal: the resolve rule settles it
                    goal = f"(({q['conflict']}) -> ({q['resolve']}) ; ({q['goal']}))"
                jobs.append({"id": q["id"], "type": q["type"], "goal": goal, "readings": rs})
                want.append(exp)
        with tempfile.TemporaryDirectory() as tmp:
            jf, of = pathlib.Path(tmp, "jobs.json"), pathlib.Path(tmp, "out.json")
            jf.write_text(json.dumps(jobs))
            subprocess.run(["swipl", str(ROOT / "verify/formal.pl"), str(jf), str(of),
                            str(d / material_dir(L, cfg) / "formal.pl")], check=True)
            got = json.loads(of.read_text())
        for j, (kind, exp), g in zip(jobs, want, got):
            tag = f"formal {material_dir(L, cfg)} {j['id']} {j['readings'] or ''}"
            if kind == "value" and g.get("value", g.get("error")) != exp:
                errs.append(f"{tag}: formal.pl gives {g.get('value', g.get('error'))}, key {exp}")
            if kind == "error" and exp not in (g.get("error") or ""):
                errs.append(f"{tag}: keyed UNDERDETERMINED but formal.pl gives {g.get('value')}")
    return errs


def why(d, keys):
    """verify/why.pl over the world, and the why keys' rules against the rule records."""
    p = subprocess.run(["swipl", str(ROOT / "verify/why.pl"), str(ROOT), str(d), "3"], capture_output=True, text=True)
    errs = [] if p.returncode == 0 else [f"why: {p.stdout.strip()} {p.stderr.strip()}"]
    ids = {r["id"] for r in RULES["rules"]}
    for q, e in keys.get("why", {}).items():
        if keys["decided"][q]["L3"] != {"status": "ANSWER", "value": True}:
            errs.append(f"why {q}: a why key on a question not keyed true at L3")
        if not e["core"] or not set(e["core"] + e["support"]) <= ids or set(e["core"]) & set(e["support"]):
            errs.append(f"why {q}: core {e['core']} / support {e['support']} malformed")
    return errs


def _norm(v):
    v = str(v).strip().strip("'")
    return v.replace("-", "") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) else v


def rows(d, w):
    """Relations whose rendered rows differ from world.json, per material directory and representation."""
    errs = []
    for L, cfg in MATERIAL:
        m = d / material_dir(L, cfg)
        text, pl = (m / "text.md").read_text(), (m / "formal.pl").read_text()
        ys = {r["name"]: r["rows"] for r in yaml.safe_load((m / "structured.yaml").read_text())["relations"]}
        for r in relations(L):
            n = r["name"]
            want = sorted(tuple(map(_norm, x)) for x in w["relations"][n])
            sec = re.search(rf"^## {n}\n(.*?)(?=^#|\Z)", text, re.M | re.S)
            lines = [x for x in (sec.group(1) if sec else "").splitlines() if x.startswith("|")][2:]
            got = {"text": sorted(tuple(_norm(c) for c in x.strip("|").split("|")) for x in lines),
                   "structured": sorted(tuple(map(_norm, x)) for x in ys.get(n, [])),
                   "formal": sorted(tuple(_norm(c) for c in a.split(", "))
                                    for a in re.findall(rf"^{n}\((.*)\)\.$", pl, re.M))}
            for rep, g in got.items():
                if g != want:
                    errs.append(f"rows {material_dir(L, cfg)} {rep} {n}: {len(g)} rows, world has {len(want)}"
                                f"{'' if len(g) != len(want) else ' (contents differ)'}")
    return errs


DATED = ("Q21", "Q22", "Q23", "Q26")


def as_of(d, w, qs, keys):
    """Per dated template: (instances, instances whose L2 key differs from the answer as of today)."""
    R, out = w["relations"], {}
    today = R["today"][0][0]
    W = reference.World(w, 2, {f: x["decided"] for f, x in reference.FORKS.items()})
    for q in qs:
        if q["template"] not in DATED:
            continue
        e, p = keys["decided"][q["id"]]["L2"], q["params"]
        if q["template"] == "Q21":
            now = any(v == p["v"] and s == "approved" and f <= today <= t for v, s, f, t in R["vendor_status"])
        elif q["template"] == "Q22":
            role = next(r for x, r, _ in R["emp"] if x == p["m"])
            now = next(l for r, l in R["role_limit"] if r == role)
        elif q["template"] == "Q23":
            now = next(iter(W.cc_on(p["e"], p["src"], today)))
        else:
            now = any(c == "capital" and g <= today for x, c, g in R["exemption"]) and \
                  not any(t <= today for x, t in R["exemption_withdrawn"])
        n, k = out.get(q["template"], (0, 0))
        out[q["template"]] = (n + 1, k + (e.get("value") != now))
    return out


def strip(e):
    return {k: v for k, v in e.items() if k != "detail"}


def check(d):
    errs = []
    w = json.loads((d / "world.json").read_text())
    qs = json.loads((d / "questions.json").read_text())
    keys = json.loads((d / "keys.json").read_text())

    if engine_keys(d, qs) != keys:
        errs.append("engine: keys.pl does not reproduce keys.json")

    ref = reference.keys(w, qs)
    for cfg in ("decided", "open"):
        for q in qs:
            for L, e in keys[cfg][q["id"]].items():
                r = ref[cfg][q["id"]][L]
                if strip(e) != r:
                    errs.append(f"reference {cfg} {q['id']} {L}: engine {strip(e)} != reference {r}")

    for q in qs:
        t = reference.BANK[q["template"]]
        m = keys["meta"][q["id"]]
        decl = {"min_layer": t["min_layer"], "forks": sorted(t["forks"])}
        if {"min_layer": m["min_layer"], "forks": sorted(m["forks"])} != decl:
            errs.append(f"meta {q['id']}: engine {m} != bank {decl}")

    errs += rows(d, w)
    errs += formal(d, qs, keys)
    errs += why(d, keys)

    R = w["relations"]
    today = R["today"][0][0]
    rlv = {(r, l) for r, l, f, t in R["role_limit_version"] if f <= today <= t}
    if set(map(tuple, R["role_limit"])) != rlv:
        errs.append("L0=L2: role_limit is not role_limit_version on today")
    vs = {(v, s) for v, s, f, t in R["vendor_status"] if f <= today <= t}
    if set(map(tuple, R["vendor"])) != vs:
        errs.append("L0=L2: vendor is not vendor_status on today")
    W = reference.World(w, 2, {f: x["decided"] for f, x in reference.FORKS.items()})
    for e, _, c in R["emp"]:
        if W.cc_on(e, "finance", today) != {c}:
            errs.append(f"L0=L2: emp {e} cc {c} != finance cc_on today {W.cc_on(e, 'finance', today)}")
    return errs


def fresh():
    """Files that differ between worlds/ and a fresh generation (fresh files never share a stat
    signature with committed ones, so dircmp compares every file by content)."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, str(ROOT / "world/gen.py"), "--out", tmp], check=True, stdout=subprocess.DEVNULL)
        diff = []

        def walk(c, rel):
            diff.extend(f"{rel}{x}" for x in c.left_only + c.right_only + c.diff_files + c.funny_files)
            for n, sub in c.subdirs.items():
                walk(sub, f"{rel}{n}/")
        walk(filecmp.dircmp(tmp, ROOT / "worlds", ignore=["ask.log.jsonl", ".gitkeep"]), "")
        return diff


def main():
    dirs = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(d for d in (ROOT / "worlds").iterdir() if d.is_dir())
    bad, tot = 0, {}
    if not sys.argv[1:]:
        stale = fresh()
        print(f"fresh: worlds/ {'matches' if not stale else 'differs from'} world/gen.py output")
        for f in stale[:20]:
            print("  " + f + "   (run make worlds)")
        bad += bool(stale)
    for d in dirs:
        errs = check(d)
        n = len(json.loads((d / "questions.json").read_text()))
        print(f"{d.name}: {n} questions x 4 layers x 2 configs (+ rows, L1-L3 formal, why), {'ok' if not errs else f'{len(errs)} mismatches'}")
        for e in errs[:20]:
            print("  " + e)
        bad += bool(errs)
        for t, (n, k) in as_of(d, json.loads((d / "world.json").read_text()), json.loads((d / "questions.json").read_text()),
                               json.loads((d / "keys.json").read_text())).items():
            tot[t] = (tot.get(t, (0, 0))[0] + n, tot.get(t, (0, 0))[1] + k)
    print("as-of: instances whose L2 key differs from the answer as of today: " +
          ", ".join(f"{t} {k}/{n}" for t, (n, k) in sorted(tot.items())))
    if not sys.argv[1:] and any(k == 0 for n, k in tot.values()):
        print("  a dated template never differs from its current value"); bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
