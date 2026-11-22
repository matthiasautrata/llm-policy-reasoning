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
"""
import filecmp, json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from questions.sample import engine_keys     # noqa: E402
from verify import reference                 # noqa: E402


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
    bad = 0
    if not sys.argv[1:]:
        stale = fresh()
        print(f"fresh: worlds/ {'matches' if not stale else 'differs from'} world/gen.py output")
        for f in stale[:20]:
            print("  " + f + "   (run make worlds)")
        bad += bool(stale)
    for d in dirs:
        errs = check(d)
        n = len(json.loads((d / "questions.json").read_text()))
        print(f"{d.name}: {n} questions x 4 layers x 2 configs, {'ok' if not errs else f'{len(errs)} mismatches'}")
        for e in errs[:20]:
            print("  " + e)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
