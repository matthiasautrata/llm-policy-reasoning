"""Harness self-test, no API calls (PLAN-v3-bench §8).

  .venv/bin/python bench/selftest.py

1. Budget stop: a fake client charging $0.01 per call under a $0.03 cap must stop, exit 1 and record error "budget",
   with no more than the cap spent.
2. Scoring: the key stub (answers are the keys) must score every manager question, every mechanical check and every
   consistency pair as correct; the abstaining stub must not.
"""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable


def run(*a):
    return subprocess.run([PY, *a], cwd=ROOT, capture_output=True, text=True)


def main():
    d = pathlib.Path(tempfile.mkdtemp())
    p = run("bench/run.py", "--models", "fake:0.01", "--n", "25", "--arms", "G", "--items", "M01", "M02", "M03", "M04",
            "M05", "M06", "--workers", "1", "--out", str(d / "fake.jsonl"), "--budget", "0.03")
    recs = [json.loads(l) for l in (d / "fake.jsonl").read_text().splitlines()]
    spent = sum(r["cost"] for r in recs)
    assert p.returncode == 1, p.stdout + p.stderr
    assert any(r["error"] == "budget" for r in recs) and len(recs) < 6 and spent <= 0.03 + 1e-9, (len(recs), spent)
    print(f"budget stop: ok ({len(recs)} cells written, ${spent:.4f} spent, exit 1)")

    sys.path[:0] = [str(ROOT / "bench")]
    import score as S
    for model, want in (("stub:key", True), ("stub:abstain", False)):
        out = d / f"{model.split(':')[1]}.jsonl"
        p = run("bench/run.py", "--models", model, "--n", "25", "200", "--out", str(out), "--budget", "1")
        assert p.returncode == 0, p.stdout + p.stderr
        recs = S.load(out)
        m = [S.score_manager(r)["correct"] for r in recs if r["kind"] == "manager"]
        k = [v for r in recs if r["kind"] == "analyst" for v in S.score_checks(r).values() if v != "judge"]
        c = list(S.consistency(recs).values())
        full = all(m) and all(v == "reported" for v in k) and all(ok == n for ok, n in c)
        assert full == want, (model, sum(m), len(m), k.count("reported"), len(k), c)
        print(f"scoring {model}: manager {sum(m)}/{len(m)}, checks {k.count('reported')}/{len(k)}: ok")


if __name__ == "__main__":
    main()
