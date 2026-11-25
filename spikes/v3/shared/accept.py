"""Spike v3 acceptance test (contract checks 1-8).

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
  7 disputes on an acyclic base (PLAN-v3-integrity §3): load slice + extension + cycles-acyclic.edn;
    every question matches its extended key and the :state :acyclic questions match keys["acyclic"]
    (why trees re-verified; a downstream CONFLICT has one contested node per contested instance,
    SEMANTICS.md). Y6: a with_hypothesis that adds the rule closing a loop (RY24 -> Y2;
    RY31/RY32/CY3 -> Y3) returns an error naming defeat-cycle and its members; Q32/Q43 are the same
    before and after
  8 integrity fixtures (fixtures/integrity/manifest.edn): each is loaded on top of slice + extension
    (or a derived slice); the load must be rejected with the named violation and members. Also: `add`
    of the Y2 closing rule is rejected and leaves the state unchanged
  Before the checks, model_check.py (integrity) runs over slice + extension + cycles-acyclic.edn.
"""
import argparse, copy, json, os, pathlib, shlex, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from reference import load, keys as ref_keys  # noqa: E402  (slice reader + key generator, not an evaluator)
from check_why import Checker, node_ids, goals_in  # noqa: E402

SLICE, EXT, CYC = "spikes/v3/shared/slice.edn", "spikes/v3/shared/extension.edn", "spikes/v3/shared/cycles-acyclic.edn"
FIX = "spikes/v3/shared/fixtures/integrity"
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
    out = {"status": r.get("status"), "value": sorted(v) if isinstance(v, list) else v,
           "sides": sorted(sorted(s) for s in r["sides"]) if r.get("sides") else None}
    if q.get("check_qualifier"):
        out["qualifier"] = r.get("qualifier")
    return out


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
        if key["status"] in ("ANSWER", "CONFLICT") and not r.get("why") and key.get("value") != []:   # [] : no instance, nothing to explain
            errs.append("no why tree")
        errs += Checker(env.S, env.rules, env.claims, as_of, env.runsql, key.get("undefined"), q.get("goal"),
                        key.get("contested")).check(r.get("why"))
        tops = {json.dumps(n.get("goal")) for n in r.get("why") or [] if n.get("type") == "contested"}
        for g in key.get("contested") or {}:     # propagation: every contested instance explained at the top
            if g not in tops: errs.append(f"contested goal {g} without a contested node")
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


def edn_records(text, ids):
    """EDN vector text holding only the records of `text` whose :id is in ids (top-level maps)."""
    import edn_format as E
    from reference import plain
    keep = [r for r in E.loads(text) if plain(r).get("id") in ids]
    return "[" + "\n".join(E.dumps(r) for r in keep) + "]"


def derive_slice(text, spec):
    """slice.edn text with spec applied: {drop-additivity: concept name} removes that concept's :additivity
    (and :unsafe_dims), keeping everything else verbatim."""
    import re
    name = spec["drop-additivity"]
    i = text.index(f':id "{name}"')
    j = text.index("\n", text.index(":additivity", i))
    seg = re.sub(r"\s*:additivity\s+:[\w-]+", "", text[i:j])
    seg = re.sub(r"\s*:unsafe_dims\s+\[[^\]]*\]", "", seg)
    return text[:i] + seg + text[j:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True)
    ap.add_argument("--mutation", action="store_true", help="check 1 against mutated keys; must fail")
    ap.add_argument("--only", default="12345678")
    ap.add_argument("--out", help="write the raw results here (JSON)")
    ap.add_argument("--timeout", type=float, default=120, help="checks 7, 8: seconds before a session counts as looping")
    a = ap.parse_args()
    S, X, Q, Y, QC = load(cycles=True)
    K = ref_keys(mutate=True) if a.mutation else json.loads((HERE / "keys.json").read_text())
    today = S["today"]
    ops = [op_for(q) for q in Q]
    report, raw, green = {}, {}, True

    import model_check as MC
    S0, r0, c0, q0 = MC.rule_base(cycles=True)
    mc = MC.check(S0, r0, c0, q0, MC.declared_modes())
    print("model check (slice + extension + acyclic):", "OK" if mc["ok"] else mc["errors"])

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
    def session(load, ops):
        """Run one session; a crash or timeout becomes one error result per op."""
        try:
            p = subprocess.run(shlex.split(a.cli), input=json.dumps({"config": CFG["duckdb"], "load": load, "ops": ops}),
                               capture_output=True, text=True, cwd=ROOT, timeout=a.timeout)
            if p.returncode == 0:
                return json.loads(p.stdout)
            return {"error": {"op": "crash", "violations": [], "stderr": p.stderr[-500:]}, "results": []}
        except subprocess.TimeoutExpired:
            return {"error": {"op": "timeout", "violations": []}, "results": []}

    def rejected(err, violation, members, exact):
        """errs for an error object that must name `violation` with `members`."""
        if not isinstance(err, dict):
            return [f"not rejected (got {str(err)[:160]})"]
        vs = [v for v in err.get("violations") or [] if v.get("violation") == violation]
        got = [set(v.get("members") or []) for v in vs]
        ok = [m for m in got if (m == set(members) if exact else set(members) <= m)]
        if ok:
            return []
        return [f"no {violation} with members {members}{' exactly' if exact else ''}: got "
                + str([(v.get("violation"), v.get("members")) for v in err.get("violations") or []])[:300]]

    if "7" in a.only:
        allq = Q + QC
        q32, q43 = (next(q for q in QC if q["id"] == i) for i in ("Q32", "Q43"))
        probe = [op_for(q32), op_for(q43)]
        y2 = (ROOT / FIX / "y2-even-loop.edn").read_text()
        y3 = (ROOT / FIX / "y3-odd-loop.edn").read_text()
        ry24 = edn_records(y2, {"RY24"})
        t0 = time.time()
        out = session([SLICE, EXT, CYC], [op_for(q) for q in allq] + probe
                      + [{"op": "with_hypothesis", "add": ry24, "ops": probe},
                         {"op": "with_hypothesis", "add": y3, "ops": probe}] + probe)
        raw["acyclic"] = out
        errs = []
        if out.get("error") or len(out.get("results") or []) != len(allq) + 6:
            errs.append(f"session failed: {str(out.get('error'))[:300]}")
        else:
            res = [unwrap(q, r) for q, r in zip(allq, out["results"])]
            envc = Env(S, X, "duckdb", Y=Y)
            for q, r in zip(allq, res):
                key = K["acyclic"][q["id"]] if q.get("state") == "acyclic" else K["extended"][q["id"]]
                envq = Env(S, X, "duckdb", Y=Y, withhold=tuple((q.get("hypothesis") or {}).get("withhold") or ())) if q.get("hypothesis") else envc
                errs += [f"acyclic {q['id']}: {e}" for e in check_question(q, key, r, envq, today)]
            n = len(allq)
            before, h2, h3, after = out["results"][n:n + 2], out["results"][n + 2], out["results"][n + 3], out["results"][n + 4:]
            errs += [f"Y6 add RY24: {e}" for e in rejected(h2.get("error"), "defeat-cycle", ["RY23", "RY24"], True)]
            errs += [f"Y6 add Y3: {e}" for e in rejected(h3.get("error"), "defeat-cycle", ["RY31", "RY32"], True)]
            if [strip(r) for r in before] != [strip(r) for r in after]:
                errs.append("Y6: Q32/Q43 changed across the rejected hypotheses")
            for q, r in zip((q32, q43), after):
                errs += [f"Y6 after {q['id']}: {e}" for e in check_question(q, K["acyclic"][q["id"]], r, envc, today)]
        got = {q["id"]: answer_fields(q, unwrap(q, r)).get("status") for q, r in zip(QC, (out.get("results") or [])[len(Q):len(Q) + len(QC)])}
        verdict(7, errs, f"({time.time() - t0:.1f}s) " + " ".join(f"{i}={g}" for i, g in got.items()))
    if "8" in a.only:
        import tempfile
        import edn_format as E
        from reference import plain
        man = plain(list(E.loads((ROOT / FIX / "manifest.edn").read_text())))
        errs, notes, raw["fixtures"] = [], [], {}
        with tempfile.TemporaryDirectory() as td:
            for m in man:
                name = m.get("file") or "derived"
                if m.get("derive"):
                    pathlib.Path(td, "slice.edn").write_text(derive_slice((ROOT / SLICE).read_text(), m["derive"]))
                    load_ = [str(pathlib.Path(td, "slice.edn")), EXT]
                else:
                    load_ = [SLICE, EXT, f"{FIX}/{m['file']}"]
                t0 = time.time()
                out = session(load_, [op_for(QC[0])])
                dt = time.time() - t0
                raw["fixtures"][f"{m['ir']} {name}"] = out
                e = rejected(out.get("error"), m["violation"], m["members"], m.get("exact"))
                if not e and (out.get("error") or {}).get("op") != "load":
                    e = [f"error op {(out.get('error') or {}).get('op')}, want load"]
                errs += [f"{m['ir']} {name}: {x}" for x in e]
                notes.append(f"{m['ir']}{'' if not e else '!'}")
            # `add` of the closing rule: rejected, state unchanged
            ry24 = edn_records((ROOT / FIX / "y2-even-loop.edn").read_text(), {"RY24"})
            q43 = next(q for q in QC if q["id"] == "Q43")
            out = session([SLICE, EXT, CYC], [op_for(q43), {"op": "add", "edn": ry24}, op_for(q43)])
            raw["fixtures"]["add RY24"] = out
            rs = out.get("results") or []
            if len(rs) != 3:
                errs.append(f"add RY24: session failed {str(out.get('error'))[:200]}")
            else:
                errs += [f"add RY24: {x}" for x in rejected(rs[1].get("error"), "defeat-cycle", ["RY23", "RY24"], True)]
                if strip(rs[0]) != strip(rs[2]): errs.append("add RY24: state changed by the rejected add")
        verdict(8, errs, f"({len(man)} fixtures + add: {' '.join(notes)})")
    print("GREEN" if green else "NOT GREEN", f"(checks {a.only})")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps({"report": report, "raw": raw}, indent=1, default=str))
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
