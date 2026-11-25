"""Spike v3 isolation test for with_hypothesis (PLAN-v3a-fix F1.4), the same session for any CLI.

  .venv/bin/python spikes/v3/shared/isolation.py --cli spikes/v3/v3a-prolog/cli [--hypothesis snapshot]

Two op lists run concurrently in one process (CLI script key "concurrent"; V3a: Prolog threads):
  A: with_hypothesis(withhold R313) [sleep DELAY, decide cost_centre_of e077 as of 2026-07-15]
  B: sleep DELAY/4, decide cost_centre_of e077 as of 2026-07-15        (on the base state)
then "after": the same decide on the main thread.
Pass iff A's decide is CONFLICT, B's decide is ANSWER cc0077 and ran while A's hypothesis was active (B's decide
started after A's sleep began and ended before A's sleep ended), and the base answer afterwards is cc0077.
Exit status 0 on pass, 1 on fail.
"""
import argparse, json, shlex, subprocess, sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from accept import CFG, ROOT, SLICE  # noqa: E402

Q = {"op": "decide", "goal": '[:cost_centre_of "e077" ?c]', "as_of": "2026-07-15"}


def script(cfg, delay):
    return {"config": cfg, "load": [SLICE], "ops": [],
            "concurrent": [[{"op": "with_hypothesis", "withhold": ["R313"],
                             "ops": [{"op": "sleep", "ms": delay}, Q]}],
                           [{"op": "sleep", "ms": delay // 4}, Q]],
            "after": [Q]}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--cli", required=True)
    a.add_argument("--hypothesis", help="CLI hypothesis mode (V3a: snapshot|assert)")
    a.add_argument("--delay", type=int, default=1000)
    a = a.parse_args()
    cfg = dict(CFG)
    if a.hypothesis:
        cfg["hypothesis"] = a.hypothesis
    p = subprocess.run(shlex.split(a.cli), input=json.dumps(script(cfg, a.delay)), capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        raise SystemExit(p.stderr[-3000:])
    out = json.loads(p.stdout)
    (hyp,), (bsleep, bq) = out["concurrent"]
    asleep, aq = hyp["results"]
    after = out["after"][0]
    checks = {
        "A sees CONFLICT": aq.get("status") == "CONFLICT",
        "B sees base answer cc0077": (bq.get("status"), bq.get("value")) == ("ANSWER", "cc0077"),
        "B's decide ran during A's hypothesis": asleep["t0"] < bq["t_start"] and bq["t_end"] < asleep["t1"],
        "base unchanged afterwards": (after.get("status"), after.get("value")) == ("ANSWER", "cc0077"),
    }
    print(f"isolation  cli={a.cli}  hypothesis={a.hypothesis or 'default'}")
    print(f"  A: {aq.get('status')} {aq.get('value')}   B: {bq.get('status')} {bq.get('value')}"
          f" (decide {bq['t_start'] - asleep['t0']:.0f}..{bq['t_end'] - asleep['t0']:.0f} ms into A's"
          f" {asleep['t1'] - asleep['t0']:.0f} ms sleep)   after: {after.get('status')} {after.get('value')}")
    for k, v in checks.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    ok = all(checks.values())
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
