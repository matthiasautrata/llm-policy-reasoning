"""Spike v3 acceptance test (PLAN §6), identical for both spikes.

  python spikes/v3/shared/accept.py --cli "spikes/v3/v3a-prolog/cli"
  python spikes/v3/shared/accept.py --cli "..." --mutation     # keys from reference.py --mutate must FAIL check 1

The CLI reads a session script (CONTRACT.md) on stdin and prints {"results": [...]}. Checks:
  1 every question matches keys.json (extended state): status, value, sides / standing, defeater,
    qualifier / candidates; core ids within the explanation; every why tree re-verifies (check_why.py)
  2 backend swap: Postgres gives the same answers and explanations (SQL text aside) with only the config changed
  3 runtime extension: base state answers base keys; `add` extension.edn in the same process; answers
    then match extended keys and exactly keys["changed"] differ
  4 with_hypothesis withholding R313: Q10 is CONFLICT inside, ANSWER before and after, state unchanged
  5 Q17 answered through fetch, bounded: every statement <= fetch_limit rows, total rows far below a
    full load, SQL logged
  6 resolve_term probes match
  7 defeat cycles (--only 7; PLAN-v3-cycles): load slice + extension + cycles.edn. The engine's flag
    (capabilities.json, via model_check.py) decides: "report" -> every question must still match its
    extended key (cycles.edn changes nothing else), and Q30-Q39 must match keys["cycles"], undefined
    nodes re-verified; "reject" -> the shared model check must reject the rule base (and that is the pass)
  Before the checks, model_check.py runs over the loaded rule base (moded safety on every engine).
"""
import argparse, copy, json, os, pathlib, shlex, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from reference import load, keys as ref_keys  # noqa: E402  (slice reader + key generator, not an evaluator)
from check_why import Checker, node_ids, goals_in  # noqa: E402

SLICE, EXT, CYC = "spikes/v3/shared/slice.edn", "spikes/v3/shared/extension.edn", "spikes/v3/shared/cycles.edn"
FETCH_LIMIT = 10000
CFG = {"duckdb": {"backend": "duckdb", "duckdb": "spikes/v3/shared/slice.duckdb", "fetch_limit": FETCH_LIMIT},
       "postgres": {"backend": "postgres", "postgres": os.environ.get("SPIKE_V3_PG", "dbname=spike_v3"), "fetch_limit": FETCH_LIMIT}}


def edn(x):
    """plain goal -> EDN text (first element of a list is a keyword)."""
    if isinstance(x, list):
        return "[" + " ".join([":" + x[0]] + [edn(v) for v in x[1:]]) + "]" if x and isinstance(x[0], str) and not x[0].startswith("?") \
            else "[" + " ".join(edn(v) for v in x) + "]"
    if isinstance(x, bool): return "true" if x else "false"
    if isinstance(x, str): return x if x.startswith("?") else json.dumps(x)
    return str(x)


def op_for(q):
    k = q["kind"]
    if k == "fetch":
        return {"op": "fetch", "concept": q["concept"], "filters": q["filters"]}
    if k == "resolve_term":
        return {"op": "resolve_term", "text": q["text"]}
    if k == "claim":
        return {"op": "claims", "asset": q["asset"], **({"as_of": q["as_of"]} if q.get("as_of") else {})}
    o = {"op": "decide" if k == "decide" else "why_not", "goal": edn(q["goal"]), **({"as_of": q["as_of"]} if q.get("as_of") else {})}
    if q.get("hypothesis"):
        h = q["hypothesis"]
        return {"op": "with_hypothesis", "withhold": h.get("withhold") or [], **({"add": h["add"]} if h.get("add") else {}), "ops": [o]}
    return o


def unwrap(q, r):
    """The result that answers q (inside a hypothesis; the claim of a claims listing)."""
    if q.get("hypothesis"):
        r = r["results"][0]
    if q["kind"] == "claim":
        c = next((c for c in r.get("claims") or [] if c["id"] == q["claim"]), None)
        return c or {"error": f"claim {q['claim']} not listed"}
    return r


def run(cli, script):
    t = time.time()
    p = subprocess.run(shlex.split(cli), input=json.dumps(script), capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        raise SystemExit(f"CLI failed ({p.returncode}):\n{p.stderr[-4000:]}")
    out = json.loads(p.stdout)
    out["wall_s"] = time.time() - t
    return out


class Env:
    """Active rule / claim sets and a SQL runner for the checker."""
    def __init__(self, S, X, backend, extended=True, withhold=(), Y=()):
        rules = list(S["rules"]) + ([x for x in X if "head" in x or "pred" in x] if extended else []) \
            + [y for y in Y if "head" in y or "pred" in y]
        claims = list(S["claims"]) + ([x for x in X if "assertion" in x] if extended else []) + [y for y in Y if "assertion" in y]
        self.S = S
        self.rules = {r["id"]: r for r in rules if r["id"] not in withhold}
        self.claims = {}
        for c in claims:
            if c["id"] in withhold: continue
            self.claims[c["id"]] = c
        self.backend = backend
        self._con = None

    def runsql(self, sql, params):
        if self._con is None:
            if self.backend == "duckdb":
                import duckdb
                self._con = duckdb.connect(str(ROOT / CFG["duckdb"]["duckdb"]), read_only=True)
            else:
                import psycopg
                self._con = psycopg.connect(CFG["postgres"]["postgres"])
        if self.backend == "duckdb":
            cur = self._con.execute(sql, params)
        else:
            cur = self._con.cursor(); cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


def answer_fields(q, r):
    k = q["kind"]
    if k == "fetch":
        rows = r.get("rows") or []
        return {"value": rows[0].get("value") if rows else None, "row_count": r.get("row_count")}
    if k == "resolve_term":
        return {"status": r.get("status"), "candidates": sorted(c["term"] for c in r.get("candidates") or [])}
    if k == "claim":
        return {"standing": r.get("standing"), "defeater": r.get("defeater"), "qualifier": sorted(r.get("qualifier") or [])}
    v = r.get("value")
    return {"status": r.get("status"), "value": sorted(v) if isinstance(v, list) else v,
            "sides": sorted(sorted(s) for s in r["sides"]) if r.get("sides") else None}


def claim_ids(c):
    ids = {c.get("id"), c.get("defeater")} | set(c.get("qualifier") or [])
    for s in c.get("sides") or []: ids |= set(s)
    for s in c.get("subclaims") or []: ids |= claim_ids(s)
    return ids - {None}


def check_question(q, key, r, env, as_of_default):
    errs = []
    if "error" in r:
        return [r["error"]]
    got = answer_fields(q, r)
    want = {f: key.get(f) for f in got}
    if q["kind"] == "why_not":
        want["sides"], got["sides"] = None, None
    for f in got:
        w = sorted(want[f]) if isinstance(want[f], list) and f != "sides" else want[f]
        if got[f] != w:
            errs.append(f"{f}: got {str(got[f])[:200]}, want {str(w)[:200]}")
    as_of = q.get("as_of") or as_of_default
    if q["kind"] == "decide":
        ids = node_ids(r.get("why"))
        miss = set(key.get("core") or []) - ids
        if miss: errs.append(f"core ids missing from why: {sorted(miss)}")
        if key["status"] in ("ANSWER", "CONFLICT") and not r.get("why"):
            errs.append("no why tree")
        errs += Checker(env.S, env.rules, env.claims, as_of, env.runsql, key.get("undefined"), q.get("goal")).check(r.get("why"))
        if key.get("undefined") and not any(n.get("type") == "undefined" for n in walk_nodes(r.get("why"))):
            errs.append("undefined goal without an undefined node")
    elif q["kind"] == "why_not":
        t = r.get("why_not")
        miss = set(key.get("core") or []) - node_ids(t)
        if miss: errs.append(f"core ids missing from why_not: {sorted(miss)}")
        gs = goals_in(t)
        for f in key.get("failed") or []:
            if f not in gs: errs.append(f"failed literal {f} not shown")
        errs += Checker(env.S, env.rules, env.claims, as_of, env.runsql).check_why_not(t)
    elif q["kind"] == "claim":
        miss = set(key.get("core") or []) - claim_ids(r)
        if miss: errs.append(f"core ids missing from claim result: {sorted(miss)}")
    return errs


def walk_nodes(nodes):
    for n in nodes or []:
        yield n
        yield from walk_nodes(n.get("children"))


def strip(x):
    """Drop timing, SQL text and params (dialect-specific) for cross-backend comparison."""
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if k not in ("ms", "sql", "params", "sql_log", "load_ms", "wall_s")}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True)
    ap.add_argument("--mutation", action="store_true", help="check 1 against mutated keys; must fail")
    ap.add_argument("--only", default="1234567")
    ap.add_argument("--out", help="write the raw results here (JSON)")
    ap.add_argument("--mode", help="engine mode for capabilities.json (e.g. v3a: wfs | memo)")
    ap.add_argument("--timeout", type=float, default=120, help="check 7: seconds before a session counts as looping")
    a = ap.parse_args()
    S, X, Q, Y, QC = load(cycles=True)
    K = ref_keys(mutate=True) if a.mutation else json.loads((HERE / "keys.json").read_text())
    today = S["today"]
    ops = [op_for(q) for q in Q]
    report, raw, green = {}, {}, True

    import model_check as MC
    if a.mode:   # passed to the engine's CLI process (V3a host.py reads ENGINE_MODE)
        os.environ["ENGINE_MODE"] = a.mode
    engine = pathlib.Path(shlex.split(a.cli)[0]).parent.name
    try:
        flag = MC.engine_flag(engine, a.mode)
    except FileNotFoundError:
        flag = "reject"
    S0, r0, c0, q0 = MC.rule_base(cycles=False)
    mc = MC.check(S0, r0, c0, q0, flag, MC.declared_modes())
    print(f"model check (slice + extension, {engine} cycles: {flag}):", "OK" if mc["ok"] else mc["errors"])

    def verdict(n, errs, note=""):
        nonlocal green
        report[n] = {"pass": not errs, "errors": errs[:40], "note": note}
        green &= not errs
        print(f"check {n}: {'PASS' if not errs else 'FAIL'} {note}")
        for e in errs[:25]: print("   ", e)

    def ask_all(backend, extended):
        out = run(a.cli, {"config": CFG[backend], "load": [SLICE] + ([EXT] if extended else []), "ops": ops})
        return out, [unwrap(q, r) for q, r in zip(Q, out["results"])]

    def keyed(state, res, env, label):
        errs = []
        for q, r in zip(Q, res):
            env_q = Env(S, X, env.backend, extended=(state == "extended"),
                        withhold=tuple((q.get("hypothesis") or {}).get("withhold") or ())) if q.get("hypothesis") else env
            if q.get("hypothesis"): env_q._con = env._con
            errs += [f"{label} {q['id']}: {e}" for e in check_question(q, K[state][q["id"]], r, env_q, today)]
        return errs

    envd = Env(S, X, "duckdb")
    if "1" in a.only or "5" in a.only or "6" in a.only or "2" in a.only:
        outd, resd = ask_all("duckdb", True); raw["duckdb_extended"] = outd
    if "1" in a.only:
        verdict(1, keyed("extended", resd, envd, "duckdb"), f"({len(Q)} questions, {outd['wall_s']:.1f}s wall)")
        if a.mutation:
            print("mutation test:", "OK (check 1 failed as it must)" if not report[1]["pass"] else "BROKEN (mutated keys passed)")
            return 0 if not report[1]["pass"] else 1
    if "2" in a.only:
        outp, resp = run(a.cli, {"config": CFG["postgres"], "load": [SLICE, EXT], "ops": ops}), None
        raw["postgres_extended"] = outp
        resp = [unwrap(q, r) for q, r in zip(Q, outp["results"])]
        envp = Env(S, X, "postgres")
        errs = keyed("extended", resp, envp, "postgres")
        for q, rd, rp in zip(Q, resd, resp):
            if strip(rd) != strip(rp):
                errs.append(f"{q['id']}: DuckDB and Postgres results differ beyond SQL text")
        verdict(2, errs, f"({outp['wall_s']:.1f}s wall)")
    if "3" in a.only:
        ext_text = (ROOT / EXT).read_text()
        out = run(a.cli, {"config": CFG["duckdb"], "load": [SLICE], "ops": ops + [{"op": "add", "edn": ext_text}] + ops})
        raw["runtime_extension"] = out
        n = len(Q)
        base = [unwrap(q, r) for q, r in zip(Q, out["results"][:n])]
        added = out["results"][n]
        ext = [unwrap(q, r) for q, r in zip(Q, out["results"][n + 1:])]
        errs = keyed("base", base, Env(S, X, "duckdb", extended=False), "base")
        errs += keyed("extended", ext, envd, "after add")
        if sorted(added.get("added") or []) != ["C6", "R307"]:
            errs.append(f"add returned {added.get('added')}")
        changed = sorted(q["id"] for q, b, e in zip(Q, base, ext) if answer_fields(q, b) != answer_fields(q, e))
        if changed != K["changed"]:
            errs.append(f"changed {changed}, want {K['changed']}")
        verdict(3, errs, f"(changed {changed})")
    if "4" in a.only:
        q10 = next(q for q in Q if q["id"] == "Q10")
        o = op_for(q10)
        out = run(a.cli, {"config": CFG["duckdb"], "load": [SLICE, EXT],
                          "ops": [o, {"op": "with_hypothesis", "withhold": ["R313"], "ops": [o]}, o]})
        raw["hypothesis"] = out
        before, inside, after = out["results"][0], out["results"][1]["results"][0], out["results"][2]
        errs = []
        if inside.get("status") != "CONFLICT": errs.append(f"inside: {inside.get('status')}")
        if before.get("status") != "ANSWER" or before.get("value") != "cc0077": errs.append(f"before: {answer_fields(q10, before)}")
        if strip(before) != strip(after): errs.append("state changed by the hypothesis")
        verdict(4, errs, f"(inside {inside.get('status')} {inside.get('sides')}, after {after.get('value')})")
    if "5" in a.only:
        i = next(j for j, q in enumerate(Q) if q["id"] == "Q17")
        r = outd["results"][i]
        log = r.get("sql_log") or []
        errs = []
        if not log: errs.append("no SQL logged")
        if not any(e.get("concept") == "request_in_subtree" for e in log): errs.append("request_in_subtree not fetched")
        big = [e for e in log if e.get("rows", 0) > FETCH_LIMIT]
        if big: errs.append(f"{len(big)} statements over {FETCH_LIMIT} rows")
        total = sum(e.get("rows", 0) for e in log)
        if total >= 100000: errs.append(f"{total} rows fetched in all: a full load")
        verdict(5, errs, f"({len(log)} statements, {total} rows, max {max((e.get('rows', 0) for e in log), default=0)})")
    if "6" in a.only:
        errs = []
        for q, r in zip(Q, resd):
            if q["kind"] == "resolve_term":
                errs += [f"{q['id']}: {e}" for e in check_question(q, K["extended"][q["id"]], r, envd, today)]
        verdict(6, errs)
    if "7" in a.only:
        S1, r1, c1, q1 = MC.rule_base(cycles=True)
        mc7 = MC.check(S1, r1, c1, q1, flag, MC.declared_modes())
        cyc = [c["predicates"] for c in mc7["cycles"]]
        if flag == "reject":
            errs = [] if not mc7["ok"] and mc7["cycles"] else ["model check did not reject the cyclic rule base"]
            verdict(7, errs, f"(cycles: reject; model check rejects {cyc}; see cycles_probe.py for the engine's own behaviour)")
        else:
            errs = list(mc7["errors"])
            allq = Q + QC
            t0 = time.time()
            try:
                p = subprocess.run(shlex.split(a.cli), input=json.dumps({"config": CFG["duckdb"], "load": [SLICE, EXT, CYC],
                                   "ops": [op_for(q) for q in allq]}), capture_output=True, text=True, cwd=ROOT, timeout=a.timeout)
                out = json.loads(p.stdout) if p.returncode == 0 else {"results": [{"error": p.stderr[-500:]}] * len(allq)}
            except subprocess.TimeoutExpired:
                out = {"results": [{"error": f"timeout {a.timeout}s"}] * len(allq)}
            raw["cycles"] = out
            res = [unwrap(q, r) for q, r in zip(allq, out["results"])]
            envc = Env(S, X, "duckdb", Y=Y)
            for q, r in zip(allq, res):
                key = K["cycles"][q["id"]] if q.get("state") == "cycles" else K["extended"][q["id"]]
                envq = Env(S, X, "duckdb", Y=Y, withhold=tuple((q.get("hypothesis") or {}).get("withhold") or ())) if q.get("hypothesis") else envc
                errs += [f"cycles {q['id']}: {e}" for e in check_question(q, key, r, envq, today)]
            got = {q["id"]: answer_fields(q, r) for q, r in zip(QC, res[len(Q):])}
            verdict(7, errs, f"(cycles: report; negative cycles {cyc}; {time.time() - t0:.1f}s) "
                             + " ".join(f"{i}={g.get('status')}" for i, g in got.items()))
    print("GREEN" if green else "NOT GREEN", f"(checks {a.only})")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps({"report": report, "raw": raw}, indent=1, default=str))
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
