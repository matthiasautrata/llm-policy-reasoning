"""Integrity gate (PLAN-v3-integrity §2): model_check.py's checks over a rule base as an engine holds it.
One implementation, independent of the engine. V3a imports gate(); the CLI serves any other host:

  echo '{"load": [paths], "added": [edn texts], "withhold": [ids]}' | python spikes/v3/shared/integrity.py
  -> {"ok": bool, "violations": [{"violation", "members", "message"}], "ms": number}

The rule base is: the first load path (a slice map), every further load path and every added EDN text
(vectors of rule / claim records), in order, minus the withheld ids. Engines call it at load, before
each `add` (state = load + earlier adds + the new text) and inside `with_hypothesis` (state + the
hypothesis' add, minus its withhold). A violation rejects the change; the state stays as it was.
A hypothesis that removes a violation is allowed (the check runs on the hypothetical rule base only).

Violations: defeat-cycle (IR-001a), superiority-cycle (IR-001b), duplicate-definition (IR-002),
rebuttal-without-preference (IR-003), missing-additivity (IR-004), negative-without-completeness
(IR-005), unbound-call (IR-006), malformed-record (flat-claim shape, recorded_at in a body).
INTEGRITY_GATE=off in the environment disables the gate (cycles_probe.py: the re-entry guard test).
"""
import json, os, pathlib, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import edn_format as E  # noqa: E402
from reference import plain  # noqa: E402
import model_check as MC  # noqa: E402


def _read(p):
    q = pathlib.Path(p)
    if not q.is_absolute() and not q.exists():
        q = ROOT / p
    return q.read_text()


def rule_base(load, added=(), withhold=()):
    """-> S, rules, claims"""
    S = plain(E.loads(_read(load[0])))
    recs = []
    for p in load[1:]:
        recs += plain(list(E.loads(_read(p))))
    for t in added:
        recs += plain(list(E.loads(t)))
    w = set(withhold)
    rules = [r for r in list(S.get("rules") or []) + [x for x in recs if "head" in x or "pred" in x] if r.get("id") not in w]
    claims = [c for c in list(S.get("claims") or []) + [x for x in recs if "assertion" in x] if c.get("id") not in w]
    return S, rules, claims


def gate(load, added=(), withhold=()):
    """-> list of violations (empty: the rule base is admissible)"""
    if os.environ.get("INTEGRITY_GATE") == "off":
        return []
    try:
        S, rules, claims = rule_base(load, added, withhold)
        return MC.check(S, rules, claims, [], MC.declared_modes())["violations"]
    except Exception as e:                    # an unreadable rule base is rejected, not crashed on
        return [MC.V("malformed-record", [], f"{type(e).__name__}: {e}")]


def main():
    t = time.time()
    req = json.loads(sys.stdin.read())
    v = gate(req.get("load") or [], req.get("added") or [], req.get("withhold") or [])
    print(json.dumps({"ok": not v, "violations": v, "ms": round((time.time() - t) * 1000, 1)}))


if __name__ == "__main__":
    main()
