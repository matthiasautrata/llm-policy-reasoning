"""Harness self-test, no API calls (PLAN-v3-bench §8, PLAN-v3-bench-run §1, §2). Green before every paid step.

  .venv/bin/python bench/selftest.py

1. Budget stop: a fake client charging $0.01 per call under a $0.03 cap stops, exits 1, records error "budget",
   and spends no more than the cap.
2. Concurrency: 8 workers of fake calls under a $0.05 cap never spend more than the cap.
3. Faults, each recorded with its cost and without losing the record: a client that raises (type, message and
   traceback recorded, the failed call's reservation counted); a tool call without "function"; tool arguments
   that are not JSON (returned to the model, the session goes on); a reply without "tool_calls" (taken as final);
   a reply reporting far fewer prompt tokens than were sent ("truncated").
4. Keys: .env is git-ignored; the loader refuses a file git does not ignore or others can read, loads the
   values, and leaves variables already set alone.
5. Endpoints: the OpenRouter body is v2's; OpenAI's has no OpenRouter fields; a Batch output line parses into the
   same record fields at half price.
6. Scoring: the key stub scores every manager question, mechanical check and consistency pair as correct; the
   abstaining stub does not. The stub judge writes parseable grades and the export runs.
"""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable
sys.path[:0] = [str(ROOT), str(ROOT / "bench")]


def run(*a):
    return subprocess.run([PY, *a], cwd=ROOT, capture_output=True, text=True)


def cells(d, name, model, items, budget, workers=1, arms=("G",)):
    out = d / f"{name}.jsonl"
    p = run("bench/run.py", "--models", model, "--n", "25", "--arms", *arms, "--items", *items, "--workers", str(workers),
            "--out", str(out), "--budget", str(budget))
    return p, [json.loads(l) for l in out.read_text().splitlines()] if out.exists() else []


def main():
    d = pathlib.Path(tempfile.mkdtemp())
    M6 = ["M01", "M02", "M03", "M04", "M05", "M06"]

    p, recs = cells(d, "stop", "fake:0.01", M6, 0.03)
    spent = sum(r["cost"] for r in recs)
    assert p.returncode == 1, p.stdout + p.stderr
    assert any(r["error"] == "budget" for r in recs) and spent <= 0.03 + 1e-9, (len(recs), spent)
    print(f"budget stop: ok ({len(recs)} cells written, ${spent:.4f} spent, exit 1)")

    many = [f"M{i:02d}" for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)]
    p, recs = cells(d, "conc", "fake:0.01", many, 0.05, workers=8, arms=("G", "G+", "T"))
    spent = sum(r["cost"] for r in recs)
    assert p.returncode == 1 and spent <= 0.05 + 1e-9, (spent, p.stdout[-500:])
    print(f"concurrency: ok (8 workers, {len(recs)} cells, ${spent:.4f} spent under $0.05)")

    p, (r,) = cells(d, "raise", "fake:0.01:raise", ["M01"], 1)
    assert r["error"].startswith("ValueError: fake client failure") and r["error_type"] == "ValueError"
    assert "Traceback" in r["traceback"] and r["cost"] == 0.02 and r["calls"][-1]["cost_estimated"], r
    p, (r,) = cells(d, "nofunc", "fake:0.01:nofunc", ["M01"], 1)
    assert r["error"].startswith("KeyError") and r["cost"] == 0.01 and r["traceback"], r
    p, (r,) = cells(d, "badargs", "fake:0.01:badargs", ["M01"], 1)
    assert r["error"] is None and r["tools"][0]["error"].startswith("JSONDecodeError") and r["answer"], r
    p, (r,) = cells(d, "notools", "fake:0.01:notools", ["M01"], 1)
    assert r["error"] is None and r["answer"], r
    p, (r,) = cells(d, "trunc", "fake:0.01:trunc", ["M01"], 1)
    assert r["error"].startswith("truncated") and r["cost"] == 0.01, r
    print("faults: ok (raise, nofunc, badargs, notools, trunc recorded with their cost)")

    from harness import openrouter as o, openai_batch as ob
    import os
    assert subprocess.run(["git", "check-ignore", "-q", o.ENV_FILE], cwd=ROOT).returncode == 0, ".env not git-ignored"
    env = ROOT / "results" / "selftest-env.jsonl"          # a path git ignores (results/*.jsonl)
    try:
        env.write_text("# c\nSELFTEST_A=one\nSELFTEST_B='two'\nSELFTEST_C=\n")
        env.chmod(0o644)
        try:
            o.load_env(str(env)); raise AssertionError("loaded a group-readable file")
        except o.CallError as e:
            assert "chmod 600" in str(e) and "one" not in str(e)
        env.chmod(0o600)
        os.environ["SELFTEST_B"] = "set"
        o.load_env(str(env))
        assert (os.environ["SELFTEST_A"], os.environ["SELFTEST_B"], "SELFTEST_C" in os.environ) == ("one", "set", False)
        loose = pathlib.Path(tempfile.mkdtemp()) / ".env"
        loose.write_text("X=1\n"); loose.chmod(0o600)
        try:
            o.load_env(str(loose)); raise AssertionError("loaded a file git does not ignore")
        except o.CallError as e:
            assert "not git-ignored" in str(e)
    finally:
        env.unlink(missing_ok=True)
    print("keys: ok (.env ignored; unignored or readable files refused; environment wins)")
    msgs = [{"role": "user", "content": "x"}]
    assert o.body("m", msgs, temperature=1.0, max_tokens=10, provider={"q": 1}) == {
        "model": "m", "messages": msgs, "temperature": 1.0, "max_tokens": 10, "usage": {"include": True}, "provider": {"q": 1}}
    b = o.body("gpt-6.2-sol", msgs, temperature=None, max_tokens=10, provider={"q": 1}, endpoint="openai")
    assert b == {"model": "gpt-6.2-sol", "messages": msgs, "max_completion_tokens": 10}, b
    line = {"custom_id": "j0000", "response": {"status_code": 200, "body": {
        "model": "gpt-6.2-sol-2026-10-01", "choices": [{"message": {"role": "assistant", "content": '{"status":"graded"}'},
                                                       "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1000000, "completion_tokens": 100000, "prompt_tokens_details": {"cached_tokens": 0}}}}}
    res = ob.parse_line(line)["j0000"]
    assert abs(res["cost"] - (2.0 + 1.0) / 2) < 1e-9 and res["provider"] == "openai", res
    assert "error" in ob.parse_line({"custom_id": "j1", "response": {"status_code": 400, "body": {"error": "bad"}}})["j1"]
    print("endpoints: ok (OpenRouter body unchanged, OpenAI body, Batch line at half price)")

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
        assert not any(r["kind"] == "analyst" and r["arm"] == "G+" for r in recs)
        print(f"scoring {model}: manager {sum(m)}/{len(m)}, checks {k.count('reported')}/{len(k)}: ok")
    out = d / "key.jsonl"
    p = run("bench/score.py", str(out), "--judge", "--judge-model", "stub:judge")
    assert p.returncode == 0 and "Mechanical checks vs judge" in p.stdout, p.stdout + p.stderr
    p = run("bench/score.py", str(out), "--export", str(d / "grading"))
    assert p.returncode == 0 and len(list((d / "grading").glob("S*.md"))) == 10, p.stdout + p.stderr
    print("judge (stub) and export: ok")


if __name__ == "__main__":
    main()
