"""V3e model validation = V3a's LinkML model, reused (PLAN-v3-cycles §3): the 12 negatives of
v3a-prolog/linkml/build.py `negatives(S, X)`, called directly (build.main() would regenerate the docs).
Run from the repo root: .venv/bin/python spikes/v3/v3e-clingo/negatives.py > spikes/v3/v3e-clingo/results/negatives.txt"""
import pathlib, sys
L = pathlib.Path(__file__).resolve().parent.parent / "v3a-prolog" / "linkml"
sys.path.insert(0, str(L))
import build, edn2yaml  # noqa: E402

S, X = edn2yaml.read(edn2yaml.SHARED / "slice.edn"), edn2yaml.read(edn2yaml.SHARED / "extension.edn")
out = build.negatives(S, X)
n = 0
for label, lm, jm in out:
    ok = bool(lm) and bool(jm)
    n += ok
    print(f"  {'rejected' if ok else 'ACCEPTED'}  {label}: linkml: {(lm or ['-'])[0][:110]} | json-schema: {(jm or ['-'])[0][:80]}")
print(f"negatives rejected (LinkML validator and JSON Schema both): {n}/{len(out)}")
