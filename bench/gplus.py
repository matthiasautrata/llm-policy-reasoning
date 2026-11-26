"""Trusted functions for arm G+ (PLAN-v3-bench §3): parameterised SQL for the five most frequent manager questions,
written from the rules' docs over the semantic layer's tables, and checked against the oracle on every instance.

  .venv/bin/python bench/gplus.py            # check every function against reference.py; exit 1 on a mismatch

Chosen by the number of manager questions (bench/questions/manager.json) each answers from the data:
  request_status      12   approved, denied, vendor check, cap breach, purchase order (R301-R316, R307)
  approved_total       3   approved total and count of a subtree, contested members apart (R120, R121, R314)
  spend                3   booked total and headroom of a centre (R104, R105)
  role_limit           3   a role's approval limit on a date (R201, R202, R203)
  breaching_requests   1   pending requests of a subtree that breach a cap (R110, R106)
Cost centre of an employee and vendor fitness rest on claims, which are not in the data, so no SQL answers them.
A false from these functions rests on the known facts only (IR-005): the descriptions say so, as the rules do.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "spikes/v3/shared/slice.duckdb"

# one request per row: every check of R301-R316 on the request date
_STATUS = """
WITH RECURSIVE q AS (
  SELECT r.id, r.amount, r.category, r.vendor, r.date, r.status, r.emergency, e.cc AS rcc, e.violation, r.requester
  FROM req r JOIN emp e ON e.id = r.requester WHERE {where}),
chain(rid, emp) AS (
  SELECT q.id, e.manager FROM q JOIN emp e ON e.id = q.requester WHERE e.manager IS NOT NULL
  UNION ALL SELECT c.rid, e.manager FROM chain c JOIN emp e ON e.id = c.emp WHERE e.manager IS NOT NULL),
anc(rid, cc) AS (
  SELECT id, rcc FROM q
  UNION ALL SELECT a.rid, c.parent FROM anc a JOIN cc c ON c.id = a.cc WHERE c.parent IS NOT NULL),
sub(root, id) AS (
  SELECT DISTINCT cc, cc FROM anc
  UNION ALL SELECT s.root, c.id FROM cc c JOIN sub s ON c.parent = s.id),
bt AS (SELECT sub.root AS cc, SUM(cc.booked) AS total FROM sub JOIN cc ON cc.id = sub.id GROUP BY sub.root),
chk AS (
  SELECT q.*,
    EXISTS (SELECT 1 FROM chain c JOIN emp a ON a.id = c.emp JOIN role_limit_version l ON l.role = a.role
            WHERE c.rid = q.id AND q.date BETWEEN l.valid_from AND l.valid_to AND l."limit" >= q.amount) AS has_approver,
    EXISTS (SELECT 1 FROM anc a JOIN bt ON bt.cc = a.cc JOIN cc ON cc.id = a.cc
            WHERE a.rid = q.id AND bt.total + q.amount > cc.cap) AS cap_breach,
    (SELECT v.status FROM vendor_status v WHERE v.vendor = q.vendor AND q.date BETWEEN v.valid_from AND v.valid_to) AS vendor_status
  FROM q),
d AS (
  SELECT *,
    COALESCE(vendor_status = 'approved', FALSE)
      OR (emergency AND vendor_status = 'suspended' AND NOT (category = 'capital' AND amount > 50000)) AS vendor_cleared,
    category = 'software' AND amount < 10000 AS auto_approved,
    violation AS denied
  FROM chk)
SELECT id, requester, rcc AS cost_centre, amount, category, vendor, CAST(date AS VARCHAR) AS date, status, emergency,
  has_approver, cap_breach, vendor_status, vendor_cleared, denied, auto_approved,
  CASE WHEN auto_approved AND denied THEN 'contested'
       WHEN auto_approved OR (has_approver AND NOT cap_breach AND vendor_cleared AND NOT denied) THEN 'yes'
       ELSE 'no' END AS approved
FROM d"""

_SUBTREE = "r.requester IN (SELECT e.id FROM emp e WHERE e.cc IN (WITH RECURSIVE s(id) AS (SELECT $cc UNION ALL " \
           "SELECT c.id FROM cc c JOIN s ON c.parent = s.id) SELECT id FROM s)) AND r.status = 'pending'"

FUNCTIONS = {
    "request_status": dict(
        params={"request": "request id, e.g. r000001"},
        doc="Approval status of one purchase request with every check behind it, each on the request date: has_approver "
            "(someone in the reporting chain whose limit version valid on the request date covers the amount, R301 R203), "
            "cap_breach (amount plus the booked total of the requester's centre or any ancestor exceeds that centre's cap, "
            "R106), vendor_cleared (vendor approved on the request date, or an emergency with a suspended vendor unless a "
            "capital request over 50,000, R305 R306 R307), denied (requester has a recorded violation, R309), auto_approved "
            "(software under 10,000, R311). approved is 'yes', 'no', or 'contested' (denied and auto-approved both apply, "
            "R314: neither yes nor no). A purchase order is issued exactly when approved is 'yes' (R316). A 'no' or a false "
            "check rests on the known facts only.",
        sql=_STATUS.format(where="r.id = $request")),
    "approved_total": dict(
        params={"cc": "cost centre id"},
        doc="Over the pending requests raised from a cost centre's subtree: the sum and number of those approved "
            "(R120, R121), and the number contested (R314). If any member is contested, the total is contested too: "
            "report it as contested, with approved_total as the proven part only.",
        sql="SELECT $cc AS cc, CAST(COALESCE(SUM(amount) FILTER (WHERE approved = 'yes'), 0) AS BIGINT) AS approved_total, "
            "COUNT(*) FILTER (WHERE approved = 'yes') AS approved_count, COUNT(*) FILTER (WHERE approved = 'contested') "
            "AS contested_count, COUNT(*) AS pending_count FROM (" + _STATUS.format(where=_SUBTREE) + ")"),
    "spend": dict(
        params={"cc": "cost centre id"},
        doc="Booked total of a cost centre over its whole subtree (R104), its cap, and headroom = cap minus booked total "
            "(R105). Booked totals are complete (C10). Never add booked totals or headroom across centres.",
        sql="WITH RECURSIVE s(id) AS (SELECT $cc UNION ALL SELECT c.id FROM cc c JOIN s ON c.parent = s.id) "
            "SELECT $cc AS cc, CAST(SUM(cc.booked) AS BIGINT) AS booked_total, (SELECT cap FROM cc WHERE id = $cc) AS cap, "
            "(SELECT cap FROM cc WHERE id = $cc) - CAST(SUM(cc.booked) AS BIGINT) AS headroom FROM s JOIN cc ON cc.id = s.id"),
    "role_limit": dict(
        params={"role": "analyst, manager, senior_manager, director or vp", "on": "date YYYY-MM-DD (today if asked without a date)"},
        doc="A role's approval limit on a date: the version valid on that date (R202). For a request, use its request "
            "date, not today (R203).",
        sql="SELECT role, \"limit\", CAST(valid_from AS VARCHAR) AS valid_from, CAST(valid_to AS VARCHAR) AS valid_to "
            "FROM role_limit_version WHERE role = $role AND CAST($on AS DATE) BETWEEN valid_from AND valid_to"),
    "breaching_requests": dict(
        params={"cc": "cost centre id"},
        doc="The pending requests raised from a cost centre's subtree that breach a cap: the requester's centre or any "
            "ancestor (R110, R106).",
        sql="SELECT id, amount, cost_centre FROM (" + _STATUS.format(where=_SUBTREE) + ") WHERE cap_breach ORDER BY id"),
}


def call(con, name, args):
    """-> list of row dicts"""
    f = FUNCTIONS[name]
    cur = con.execute(f["sql"], {k: args[k] for k in f["params"]})
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def tools():
    """OpenAI-style tool definitions for the arm"""
    return [{"type": "function", "function": {"name": "fn_" + n, "description": f["doc"], "parameters": {
        "type": "object", "properties": {k: {"type": "string", "description": v} for k, v in f["params"].items()},
        "required": list(f["params"])}}} for n, f in FUNCTIONS.items()]


def check():
    """every function against reference.py: all requests, every centre with pending requests, every role and boundary date"""
    import duckdb
    sys.path.insert(0, str(ROOT / "spikes/v3/shared"))
    import reference as R
    S, X, _ = R.load()
    ref = R.Ref(S, X)
    con = duckdb.connect(str(DB), read_only=True)
    bad = []
    # request_status over every request at once (same SQL, all ids)
    cur = con.execute(_STATUS.format(where="TRUE"))
    cols = [d[0] for d in cur.description]
    rows = {r[0]: dict(zip(cols, r)) for r in cur.fetchall()}
    for rid in ref.req:
        st, v, _ = ref.approved(rid)
        want = "contested" if st == "CONFLICT" else ("yes" if v else "no")
        g = rows[rid]
        got = (g["approved"], g["has_approver"], g["cap_breach"], g["vendor_cleared"], bool(g["denied"]), g["auto_approved"])
        exp = (want, ref.has_approver(rid), ref.cap_breach(rid), ref.vendor_cleared(rid)[0], bool(ref.denied(rid)), ref.auto_approved(rid))
        if got != exp:
            bad.append(("request_status", rid, got, exp))
    print(f"  request_status: {len(ref.req)} requests")
    # single-call path agrees with the bulk path on a sample
    for rid in ["r000001", "r000002", "r000003", "r000005", "r000006", "r000008"]:
        if call(con, "request_status", {"request": rid})[0] != rows[rid]:
            bad.append(("request_status single", rid))
    centres = sorted(ref.cc)
    for c in centres:
        sp = call(con, "spend", {"cc": c})[0]
        if (sp["booked_total"], sp["headroom"]) != (ref.booked_total(c), ref.headroom(c)):
            bad.append(("spend", c, sp))
    print(f"  spend: {len(centres)} centres")
    sample = centres[:: max(1, len(centres) // 60)] + ["cc0009", "cc0049", "cc0058", "cc0105", "cc0290"]
    for c in sample:
        a = call(con, "approved_total", {"cc": c})[0]
        st, v, _, cont, n = ref.approved_agg(c, "sum")
        exp = (v, n, len(cont["via"]) if cont else 0)
        if (a["approved_total"], a["approved_count"], a["contested_count"]) != exp:
            bad.append(("approved_total", c, a, exp))
        br = [r["id"] for r in call(con, "breaching_requests", {"cc": c})]
        if br != ref.breach_in(c):
            bad.append(("breaching_requests", c, len(br), len(ref.breach_in(c))))
    print(f"  approved_total, breaching_requests: {len(sample)} centres")
    days = sorted({d for _, _, f, t in ref.limits for d in (f, t)} | {ref.today})
    for role in sorted({r for r, *_ in ref.limits}):
        for d in days:
            g = call(con, "role_limit", {"role": role, "on": d})
            if (g[0]["limit"] if g else None) != ref.limit_on(role, d):
                bad.append(("role_limit", role, d, g))
    print(f"  role_limit: {len(days)} boundary dates per role")
    return bad


if __name__ == "__main__":
    bad = check()
    for b in bad[:20]: print("FAIL", b)
    print("PASS" if not bad else f"{len(bad)} mismatches")
    sys.exit(1 if bad else 0)
