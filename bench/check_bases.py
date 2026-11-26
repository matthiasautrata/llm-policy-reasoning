"""Check the generated bases (PLAN-v3-bench §2, §8): per base, through the engine CLI

  1 the base passes the integrity gate (shared/integrity.py), its questions the mode check
  2 every base question matches its key (bench/bases/N*.keys.json, from reference.py --bench), with the proof checks of accept.py
  3 every slice question still matches keys.json (extended state): generated rules read slice predicates, never conclude them

  .venv/bin/python bench/check_bases.py [--cli spikes/v3/v3a-prolog/cli] [--n 50 200] [--skip-slice]
"""
import argparse, json, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "spikes/v3/shared"))
import accept as A  # noqa: E402
import integrity  # noqa: E402
import model_check as MC  # noqa: E402
import reference  # noqa: E402

BASES = ROOT / "bench/bases"


def check(stem, cli, slice_too=True):
    load = [str(stem.with_suffix(".edn").relative_to(ROOT)), A.EXT]
    fails = []
    v = integrity.gate(load)
    if v: fails.append(f"gate: {v[:3]}")
    S, rules, claims = integrity.rule_base(load)
    Q = json.loads(stem.with_suffix(".questions.json").read_text()) if stem.with_suffix(".questions.json").exists() else []
    mc = MC.check(S, rules, claims, Q, MC.declared_modes())
    if not mc["ok"]: fails.append(f"modes: {mc['errors'][:3]}")
    X = reference.load()[1]
    env = A.Env(S, X)
    jobs = []
    if Q:
        jobs.append(("base", Q, json.loads(stem.with_suffix(".keys.json").read_text())))
    if slice_too:
        _, _, SQ = reference.load()
        jobs.append(("slice", SQ, json.loads((ROOT / "spikes/v3/shared/keys.json").read_text())["extended"]))
    for label, qs, keys in jobs:
        t = time.time()
        out = A.run(cli, {"config": A.CFG, "load": load, "ops": [A.op_for(q) for q in qs]})
        bad = 0
        for q, r in zip(qs, out["results"]):
            errs = A.check_question(q, keys[q["id"]], A.unwrap(q, r), env, S["today"])
            if errs:
                bad += 1
                fails.append(f"{label} {q['id']} {q.get('goal') or q.get('claim')}: {'; '.join(errs)[:300]}")
        print(f"  {stem.name} {label}: {len(qs) - bad}/{len(qs)} match ({time.time() - t:.1f} s)")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", default="spikes/v3/v3a-prolog/cli")
    ap.add_argument("--n", type=int, nargs="*")
    ap.add_argument("--skip-slice", action="store_true")
    a = ap.parse_args()
    stems = sorted(BASES.glob("N*.edn")) if not a.n else [BASES / f"N{n:03d}.edn" for n in a.n]
    fails = []
    for s in stems:
        fails += check(s.with_suffix(""), a.cli, not a.skip_slice)
    for f in fails: print("FAIL", f)
    print("PASS" if not fails else f"{len(fails)} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
