"""Spike v3 data: the v2 procurement world at scale, loaded identically into DuckDB and Postgres.

  python spikes/v3/shared/gen.py                # -> shared/slice.duckdb + Postgres db spike_v3
  python spikes/v3/shared/gen.py --check        # row counts and checksums per table, both backends

Reuses v2 world/domain.py (role limits, vendor periods, amounts, categories, dates) read-only and
v2 world/gen.py's construction (one manager per centre, analysts in leaves, caps around the booked
total, hr/finance assignment divergence after transfers). Scale: ~2,000 cost centres, 20,000
employees, 100,000 requests. Planted requests r000001..r000008 exercise the rule interactions the
questions ask about (see PLANTED). Detail data only: System A never holds these rows.
"""
import argparse, hashlib, json, os, pathlib, random, sys
from datetime import date, timedelta

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from world.domain import ROLE_LIMITS, VENDORS, AMOUNTS, CATEGORIES, TODAY, REQ_FROM  # noqa: E402

SEED = 3
FANOUT = [8, 5, 6, 7]           # children per level: 1 + 8 + 40 + 240 + 1680 = 1969 centres
N_EMP, N_REQ = 20000, 100000
P_VIOLATION, P_EMERGENCY, P_CANCELLED, P_TRANSFER = 0.05, 0.25, 0.10, 0.08
DUCK = HERE / "slice.duckdb"
PG_DSN = os.environ.get("SPIKE_V3_PG", "dbname=spike_v3")

DDL = {
    "cc": "id VARCHAR PRIMARY KEY, parent VARCHAR, level INTEGER NOT NULL, org_unit VARCHAR NOT NULL, booked INTEGER NOT NULL, cap INTEGER NOT NULL",
    "emp": "id VARCHAR PRIMARY KEY, role VARCHAR NOT NULL, cc VARCHAR NOT NULL, manager VARCHAR, violation BOOLEAN NOT NULL",
    "req": "id VARCHAR PRIMARY KEY, requester VARCHAR NOT NULL, amount INTEGER NOT NULL, category VARCHAR NOT NULL, vendor VARCHAR NOT NULL, date DATE NOT NULL, status VARCHAR NOT NULL, emergency BOOLEAN NOT NULL",
    "assignment": "emp VARCHAR NOT NULL, cc VARCHAR NOT NULL, source VARCHAR NOT NULL, effective DATE NOT NULL, PRIMARY KEY (emp, source, effective)",
    "role_limit_version": "role VARCHAR NOT NULL, \"limit\" INTEGER NOT NULL, valid_from DATE NOT NULL, valid_to DATE NOT NULL, PRIMARY KEY (role, valid_from)",
    "vendor_status": "vendor VARCHAR NOT NULL, status VARCHAR NOT NULL, valid_from DATE NOT NULL, valid_to DATE NOT NULL, PRIMARY KEY (vendor, valid_from)",
}
INDEXES = ["CREATE INDEX emp_cc ON emp(cc)", "CREATE INDEX req_requester ON req(requester)", "CREATE INDEX cc_parent ON cc(parent)"]


def build():
    rnd = random.Random(SEED)
    cc, parent, lvl = [], {}, {}
    def mk(p, l):
        c = f"cc{len(cc):04d}"; cc.append(c); lvl[c] = l
        if p: parent[c] = p
        return c
    frontier = [mk(None, 0)]
    for l, k in enumerate(FANOUT, start=1):
        frontier = [mk(p, l) for p in frontier for _ in range(k)]
    depth = len(FANOUT)
    leaves = [c for c in cc if lvl[c] == depth]
    unit = {c: (rnd.choice(["delivery", "support"]) if lvl[c] == depth else "leadership") for c in cc}

    emps, mgr = [], {}
    for c in cc:
        role = "vp" if lvl[c] == 0 else "director" if lvl[c] == 1 else "manager" if lvl[c] == depth else "senior_manager"
        e = f"e{len(emps):03d}"; emps.append([e, role, c]); mgr[c] = e
    while len(emps) < N_EMP:
        e = f"e{len(emps):03d}"; emps.append([e, "analyst", rnd.choice(leaves)])
    manager = {e: (mgr[c] if r == "analyst" else mgr.get(parent.get(c))) for e, r, c in emps}

    # hr records a transfer first; finance later or not yet (v2 world/gen.py)
    analysts = [e for e in emps if e[1] == "analyst"]
    assignment = [[e, c, s, "2026-01-01"] for e, _, c in emps for s in ("hr", "finance")]
    final = {e: c for e, _, c in emps}
    for e, _, c in rnd.sample(analysts, round(len(analysts) * P_TRANSFER)):
        to = rnd.choice([l for l in leaves if l != c])
        d1 = REQ_FROM + timedelta(days=rnd.randrange(10, 80)); d2 = d1 + timedelta(days=rnd.randrange(7, 41))
        assignment.append([e, to, "hr", d1.isoformat()])
        if d2 <= TODAY and rnd.random() > 0.3:
            assignment.append([e, to, "finance", d2.isoformat()]); final[e] = to

    staff = [e for e, r, _ in emps if r != "vp"]
    violation = set(rnd.sample(staff, round(len(staff) * P_VIOLATION)))
    booked = {c: rnd.randrange(40, 141) * 1000 for c in leaves}
    for c in cc:
        if lvl[c] < depth and rnd.random() < 0.3:
            booked[c] = rnd.randrange(5, 40) * 1000
    total = {c: booked.get(c, 0) for c in cc}
    for c in reversed(cc):
        if c in parent: total[parent[c]] += total[c]
    fac = lambda c: [1.2, 1.4] if lvl[c] == 0 else [1.05, 1.15, 1.3, 1.5] if lvl[c] < depth else [0.97, 1.03, 1.1, 1.2, 1.4, 1.6]
    cap = {c: int(total[c] * rnd.choice(fac(c)) // 1000 * 1000) for c in cc}

    def anc(c):
        out = [c]
        while c in parent: c = parent[c]; out.append(c)
        return out
    def roomy(e, amt):     # no cap breach for amt anywhere on the charged path
        return all(total[x] + amt <= cap[x] for x in anc(final[e]))

    span = (TODAY - REQ_FROM).days
    clean = [e for e in analysts if e[0] not in violation and roomy(e[0], 40000)]
    pick = lambda: rnd.choice(clean)[0]
    PLANTED = [   # id, requester, amount, category, vendor, date, status, emergency
        ["r000001", rnd.choice(sorted(violation & {e for e, r, _ in analysts})), 8000, "software", "acme", "2026-08-20", "pending", False],  # R312 vs R314 -> CONFLICT
        ["r000002", pick(), 90000, "capital", "fern", "2026-08-03", "pending", True],    # R306 waiver, defeated by R307 (extension)
        ["r000003", pick(), 12000, "hardware", "fern", "2026-07-22", "pending", True],   # R306 waiver applies
        ["r000004", pick(), 38000, "services", "acme", "2026-07-10", "pending", False],  # R203: limit on request date (manager 25k, not 40k)
        ["r000005", pick(), 3000, "hardware", "acme", "2026-09-01", "pending", False],   # plain approval
        ["r000006", pick(), 12000, "hardware", "fern", "2026-09-02", "pending", False],  # why-not: vendor check fails
        ["r000007", pick(), 20000, "hardware", "bolt", "2026-07-15", "pending", False],  # bolt approved on its date
        ["r000008", pick(), 20000, "hardware", "bolt", "2026-08-15", "pending", False],  # bolt suspended on its date
    ]
    req = [list(p) for p in PLANTED]
    for i in range(len(PLANTED), N_REQ):
        d = (REQ_FROM + timedelta(days=rnd.randrange(span + 1))).isoformat()
        req.append([f"r{i + 1:06d}", rnd.choice(staff), rnd.choice(AMOUNTS), rnd.choice(CATEGORIES), rnd.choice(list(VENDORS)), d,
                    "cancelled" if rnd.random() < P_CANCELLED else "pending", rnd.random() < P_EMERGENCY])
    return {
        "cc": [[c, parent.get(c), lvl[c], unit[c], booked.get(c, 0), cap[c]] for c in cc],
        "emp": [[e, r, final[e], manager[e], e in violation] for e, r, _ in emps],
        "req": req,
        "assignment": sorted(assignment, key=lambda a: (a[0], a[2], a[3])),
        "role_limit_version": [[r, l, f.isoformat(), t.isoformat()] for r, vs in ROLE_LIMITS.items() for l, f, t in vs],
        "vendor_status": [[v, s, f.isoformat(), t.isoformat()] for v, ps in VENDORS.items() for s, f, t in ps],
    }


def load_duck(tables):
    import duckdb
    DUCK.unlink(missing_ok=True)
    con = duckdb.connect(str(DUCK))
    for t, rows in tables.items():
        con.execute(f"CREATE TABLE {t} ({DDL[t]})")
        con.executemany(f"INSERT INTO {t} VALUES ({', '.join('?' * len(rows[0]))})", rows)
    for i in INDEXES: con.execute(i)
    con.close()


def load_pg(tables):
    import psycopg
    with psycopg.connect(PG_DSN) as con, con.cursor() as cur:
        for t, rows in tables.items():
            cur.execute(f"DROP TABLE IF EXISTS {t}")
            cur.execute(f"CREATE TABLE {t} ({DDL[t].replace('VARCHAR', 'TEXT')})")
            with cur.copy(f"COPY {t} FROM STDIN") as cp:
                for r in rows: cp.write_row(r)
        for i in INDEXES: cur.execute(i)
        cur.execute("ANALYZE")


ORDER = {"cc": "id", "emp": "id", "req": "id", "assignment": "emp, source, effective",
         "role_limit_version": "role, valid_from", "vendor_status": "vendor, valid_from"}


def fingerprint(rows):
    h = hashlib.sha256()
    for r in rows:
        h.update(json.dumps([x.isoformat() if hasattr(x, "isoformat") else x for x in r]).encode())
    return h.hexdigest()[:16]


def check():
    import duckdb, psycopg
    d = duckdb.connect(str(DUCK), read_only=True)
    ok = True
    with psycopg.connect(PG_DSN) as p, p.cursor() as cur:
        for t, o in ORDER.items():
            a = d.execute(f"SELECT * FROM {t} ORDER BY {o}").fetchall()
            cur.execute(f"SELECT * FROM {t} ORDER BY {o}"); b = cur.fetchall()
            fa, fb = fingerprint(a), fingerprint(b)
            print(f"{t:20s} duckdb {len(a):7d} {fa}   postgres {len(b):7d} {fb}   {'ok' if (len(a), fa) == (len(b), fb) else 'DIFFER'}")
            ok &= (len(a), fa) == (len(b), fb)
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    if not a.check:
        t = build()
        load_duck(t); load_pg(t)
        print({k: len(v) for k, v in t.items()})
    sys.exit(0 if check() else 1)
