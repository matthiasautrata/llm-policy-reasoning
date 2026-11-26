"""Rule and claim generator for the v3 benchmark (PLAN-v3-bench §2): the curve's x-axis.

  .venv/bin/python bench/gen.py                     # bench/bases/N{025,050,100,200}.{edn,params.json,questions.json}
  .venv/bin/python bench/gen.py --n 50 --seed 7 --density 20 --distractors 0.3 --out DIR

A base is the slice map (spikes/v3/shared/slice.edn) with generated rules, claims, terms and assets
spliced in; it is loaded together with extension.edn, so the slice's 24 rules plus R307 are the N = 25 core.
N counts rules only. Generated families use their own predicates (instance code first), may read slice
predicates and never conclude or attack them, so every slice key holds at every N. Schema and data stay at
slice size.

Families (each documented by its parameters in N*.params.json, which the oracle in reference.py reads;
the oracle never reads the EDN):
  programme   dated limit versions:  [:programme_limit_ok P ?r]  one strict rule per version
  clearance   on a programme:        [:programme_cleared P ?r]   base rule (limit ok and slice vendor check),
              optional exception (defeater on a vendor, superior to the base) and exception to the exception
              (emergency requests from that vendor within the limit, superior to the exception)
  dispute     owner dispute K:       [:capitalised C ?r]  one owner capitalises a category-C request from an amount,
              another expenses it below a higher amount; without superiority the overlap is a CONFLICT. Every
              dispute over C concludes the same literal, so disputes over one category meet (team defeat), and a
              later dispute's rule may be stated to prevail over an earlier one's opposite rule
  chain       sub-programmes U01..Um of P01 (PLAN-v3-bench-full §3b′): [:uNN_cleared ?r], one predicate per level
              (the gate's cycle check is per predicate, so a level cannot read its own predicate). U01 clears what
              P01 clears; U02 what U01 clears and is capitalised (so a contested capitalisation is contested
              downstream); from U03 on, a defeater blocks emergency requests and an exception to it re-admits an
              emergency request cleared under P01 up to an amount (reading P01's clearance directly)

P01 is seeded apart from N (its programme, its chain levels and the disputes over its category, each from its
own seed), so the items on it are the same at every N; N adds levels (m = 1 + log2(N / 25)) and disputes over
its category (round(N / 50)), which is what makes k and the dispute count grow with N.
  distractor  irrelevant to the tasks: [:perk D ?e] by role, [:centre_tag D ?c] by org unit
  claim tree  [:supplier_qualified S v] with required (insurance_valid, quality_audited) and supporting
              (delivery_on_time) sub-claims; optionally a later claim of the same asserter negates one
  claim dispute  two asserters disagree: [:export_licensed X v] ordered by one authority rule
              (legal over compliance), [:data_protection_ok X v] without superiority (contested)

Knobs: N; density = interactions (exceptions, precedence, conflicts) per 100 rules over the whole base
(the core has 4: R306, R307, R313, R314); distractors = share of generated rules that are distractors.
Seeded and reproducible. Every base passes the integrity gate (shared/integrity.py) and its questions pass
the mode check, or the generator stops. Fetches filter on the key only (constants are compared in the body),
so no generated rule adds a fetch shape that flush() would batch as UNION ALL; the report lists every
shape that would (PLAN-v3-bench §0).
"""
import argparse, json, math, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHARED = ROOT / "spikes/v3/shared"
sys.path.insert(0, str(SHARED))
import edn_format as E  # noqa: E402
import integrity  # noqa: E402
import model_check as MC  # noqa: E402
from reference import plain  # noqa: E402

SLICE, EXT = SHARED / "slice.edn", SHARED / "extension.edn"
OUT = ROOT / "bench/bases"
CORE_RULES, CORE_INTERACTIONS = 25, 4          # slice 24 + R307; R306, R307, R313, R314
CLAIM_RATIO = 14 / 25                          # claims per rule in the core
NS = [25, 50, 100, 200]

CATEGORIES = ["software", "hardware", "services", "capital"]
VENDORS = ["acme", "bolt", "cog", "dyne", "edge", "fern"]
ROLES = ["analyst", "manager", "senior_manager", "director", "vp"]
ORG_UNITS = ["delivery", "support", "leadership"]
LIMITS = [8000, 12000, 20000, 30000, 45000, 60000]
SPLITS = ["2026-07-01", "2026-08-01", "2026-09-01"]
OWNERS = ["procurement", "finance", "operations", "it", "facilities", "marketing"]
EXC_OWNERS = ["risk", "compliance", "legal"]
DISPUTE_OWNERS = [("finance", "tax"), ("finance", "audit"), ("controller", "tax"), ("audit", "controller")]
PROGRAMMES = ["cloud tooling", "lab equipment", "field services", "office refit", "fleet renewal", "training",
              "events", "security tooling", "data licences", "consulting", "print and post", "test rigs",
              "site maintenance", "developer laptops", "network upgrade", "translation", "catering",
              "recruiting", "archive digitisation", "warehouse racking"]
PERKS = ["home-office allowance", "conference budget", "mobile phone", "car allowance", "lounge access",
         "language course", "standing desk", "gym subsidy", "second monitor", "parking space"]
TAGS = ["energy audit", "hot-desk pilot", "quiet floor", "fire drill group", "badge refresh", "plant care"]
YEAR = ("2026-01-01", "2026-12-31")


# ---------------------------------------------------------------------------- EDN writing
class Kw(str): pass


def edn(x):
    if isinstance(x, Kw): return ":" + x
    if isinstance(x, bool): return "true" if x else "false"
    if x is None: return "nil"
    if isinstance(x, int): return str(x)
    if isinstance(x, str):
        return x if x.startswith("?") else json.dumps(x)
    if isinstance(x, tuple) and x[0] == "inst": return f'#inst "{x[1]}"'
    if isinstance(x, dict): return "{" + " ".join(f":{k} {edn(v)}" for k, v in x.items()) + "}"
    if isinstance(x, list): return "[" + " ".join(edn(v) for v in x) + "]"
    raise TypeError(x)


inst = lambda d: ("inst", d)
fetch_req = lambda cols: [Kw("fetch"), Kw("request"), {"id": "?r"}, cols]


def money(a):
    return f"{a:,}"


def day(d):
    y, m, dd = d.split("-")
    return f"{int(dd)} {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(m)-1]} {y}"


def prev_day(d):
    import datetime
    return (datetime.date.fromisoformat(d) - datetime.timedelta(days=1)).isoformat()


# ---------------------------------------------------------------------------- families
class Gen:
    def __init__(self, n, seed, density, distractors):
        self.n, self.seed, self.density, self.share = n, seed, density, distractors
        self.rnd = random.Random(f"{seed}:{n}:{density}:{distractors}")
        self.rules, self.claims, self.rid, self.cid = [], [], 0, 0
        self.P = dict(seed=seed, n=n, density=density, distractors=distractors,
                      programmes=[], chain=[], disputes=[], distractor_rules=[], claim_trees=[], claim_disputes=[],
                      superiority=None, superior=[])

    def fixed(self, tag):
        """a generator for one P01 item, independent of N"""
        return random.Random(f"P01:{self.seed}:{tag}")

    def next_rule(self):
        self.rid += 1
        return f"G{self.rid:03d}"

    def rule(self, **r):
        rec = dict(id=Kw(r.pop("id")), kind=Kw(r.pop("kind")), owner=Kw(r.pop("owner")), **{"class": Kw(r.pop("cls"))})
        rec["recorded_at"] = inst("2026-09-14")
        rec.update(r)
        self.P["superior"] += [[str(rec["id"]), str(s)] for s in r.get("superior-to", [])]   # "Prevails over" in the docs
        self.rules.append(rec)

    # programme: dated limit versions, optional clearance with exception and counter-exception
    def programme(self, clearance=False, exception=False, counter=False, rnd=None, cat=None):
        k, rnd = len(self.P["programmes"]) + 1, rnd or self.rnd
        code, name = f"P{k:02d}", PROGRAMMES[(k - 1) % len(PROGRAMMES)] + ("" if k <= len(PROGRAMMES) else f" {k}")
        owner, cat = rnd.choice(OWNERS), cat or rnd.choice(CATEGORIES)
        cuts = sorted(rnd.sample(SPLITS, rnd.choice([1, 2])))
        bounds = [YEAR[0]] + cuts
        versions = []
        for i, f in enumerate(bounds):
            t = prev_day(bounds[i + 1]) if i + 1 < len(bounds) else YEAR[1]
            v = dict(id=self.next_rule(), valid_from=f, valid_to=t, limit=rnd.choice(LIMITS))
            versions.append(v)
            self.rule(id=v["id"], kind="strict", owner="procurement", cls="definition",   # IR-002: one owner defines
                      doc=f"Programme {code} ({name}) covers {cat} requests. Version valid from {day(f)} to {day(t)}: "
                          f"a request is within the programme limit if its amount is at most {money(v['limit'])} "
                          f"(the version valid on the request date governs).",
                      head=[Kw("programme_limit_ok"), code, "?r"],
                      body=[fetch_req({"category": "?c", "amount": "?a", "date": "?d"}), [Kw("="), "?c", cat],
                            [Kw("<="), f, "?d"], [Kw("<="), "?d", t], [Kw("<="), "?a", v["limit"]]])
        p = dict(code=code, name=name, owner=owner, category=cat, versions=versions, clearance=None)
        if clearance:
            base = self.next_rule()
            self.rule(id=base, kind="defeasible", owner=owner, cls="material_inference",
                      doc=f"A request is cleared under programme {code} ({name}) if it is within the programme limit "
                          f"and passes the vendor check.",
                      head=[Kw("programme_cleared"), code, "?r"],
                      body=[[Kw("programme_limit_ok"), code, "?r"], [Kw("vendor_cleared"), "?r"]])
            c = dict(base=base, exception=None, counter=None)
            if exception:
                e, eo, ven = self.next_rule(), rnd.choice(EXC_OWNERS), rnd.choice(VENDORS)
                self.rule(id=e, kind="defeater", owner=eo, cls="exception",
                          doc=f"Exception ({eo}): a request from vendor {ven} is not cleared under programme {code}, "
                              f"whatever the vendor check says. Prevails over {base}.",
                          head=[Kw("neg"), [Kw("programme_cleared"), code, "?r"]],
                          body=[fetch_req({"vendor": "?v"}), [Kw("="), "?v", ven]],
                          **{"superior-to": [Kw(base)]})
                c["exception"] = dict(id=e, owner=eo, vendor=ven)
                if counter:
                    x = self.next_rule()
                    self.rule(id=x, kind="defeasible", owner=owner, cls="exception",
                              doc=f"Exception to the exception: an emergency request from vendor {ven} is cleared under "
                                  f"programme {code} if it is within the programme limit, even without the vendor check. "
                                  f"Prevails over {e}.",
                              head=[Kw("programme_cleared"), code, "?r"],
                              body=[fetch_req({"vendor": "?v", "emergency": "?x"}), [Kw("="), "?v", ven],
                                    [Kw("="), "?x", True], [Kw("programme_limit_ok"), code, "?r"]],
                              **{"superior-to": [Kw(e)]})
                    c["counter"] = dict(id=x)
            p["clearance"] = c
        self.P["programmes"].append(p)

    # owner dispute over capitalisation, with or without superiority
    def dispute(self, superior, cat=None, rnd=None, cross=None):
        """cross: "for" or "against", this dispute's rule of that side prevails over the opposite rule of the
        previous dispute over the same category"""
        k, rnd = len(self.P["disputes"]) + 1, rnd or self.rnd
        code, (a, b) = f"K{k:02d}", rnd.choice(DISPUTE_OWNERS)
        cat = cat or rnd.choice([c for c in ["hardware", "capital", "software"] if c != self.cat])
        lo = rnd.choice([8000, 12000, 20000])
        hi = rnd.choice([x for x in [20000, 30000, 45000, 60000] if x > lo])
        s, d = self.next_rule(), self.next_rule()
        prev = next((x for x in reversed(self.P["disputes"]) if x["category"] == cat), None) if cross else None
        over = {"for": [d] if superior == "for" else [], "against": [s] if superior == "against" else []}
        if prev:
            over[cross].append(prev["against" if cross == "for" else "for"]["id"])
        pref = lambda me: f" Prevails over {' and '.join(over[me])}." if over[me] else ""
        sup = lambda me: {"superior-to": [Kw(x) for x in over[me]]} if over[me] else {}
        self.rule(id=s, kind="defeasible", owner=a, cls="material_inference",
                  doc=f"Capitalisation policy {code} ({a}): a {cat} request of at least {money(lo)} is capitalised." + pref("for"),
                  head=[Kw("capitalised"), cat, "?r"],
                  body=[fetch_req({"category": "?c", "amount": "?a"}), [Kw("="), "?c", cat], [Kw(">="), "?a", lo]], **sup("for"))
        self.rule(id=d, kind="defeater", owner=b, cls="exception",
                  doc=f"Capitalisation policy {code} ({b}): a {cat} request under {money(hi)} is expensed, not capitalised." + pref("against"),
                  head=[Kw("neg"), [Kw("capitalised"), cat, "?r"]],
                  body=[fetch_req({"category": "?c", "amount": "?a"}), [Kw("="), "?c", cat], [Kw("<"), "?a", hi]], **sup("against"))
        self.P["disputes"].append(dict(code=code, category=cat, superior=superior, p01=cat == self.cat,
                                       cross=dict(side=cross, over=prev["code"]) if prev else None,
                                       **{"for": dict(id=s, owner=a, min=lo), "against": dict(id=d, owner=b, below=hi)}))

    # a sub-programme level of P01's chain
    def level(self, j):
        rnd, P01 = self.fixed(f"U{j}"), self.P["programmes"][0]
        code, parent = f"U{j:02d}", "P01" if j == 1 else f"U{j - 1:02d}"
        head = lambda c: [Kw("programme_cleared"), "P01", "?r"] if c == "P01" else [Kw(f"u{c[1:]}_cleared"), "?r"]
        TERMS[f"u{j:02d}_cleared"] = (f"sub-programme {code} clearance", "procurement",
                                      f"Clearance under sub-programme {code}, as opposed to clearance under programme P01, "
                                      f"says a request may be charged to {code}, one level below {parent}.")
        owner, b = rnd.choice(OWNERS), self.next_rule()
        cap = j == 2
        self.rule(id=b, kind="defeasible", owner=owner, cls="material_inference",
                  doc=f"Sub-programme {code} of programme P01 ({P01['name']}): a request cleared under {parent} is cleared "
                      f"under {code}" + (" if it is capitalised." if cap else "."),
                  head=head(code),
                  body=[head(parent)] + ([[Kw("capitalised"), self.cat, "?r"]] if cap else []))
        L = dict(code=code, pred=f"u{j:02d}_cleared", parent=parent, base=dict(id=b, owner=owner, capitalised=cap),
                 exception=None, counter=None)
        if j >= 3:
            e, eo, x, mx = self.next_rule(), rnd.choice(EXC_OWNERS), self.next_rule(), rnd.choice([8000, 12000, 20000])
            self.rule(id=e, kind="defeater", owner=eo, cls="exception",
                      doc=f"Exception ({eo}): an emergency request is not cleared under sub-programme {code}, whatever "
                          f"{code}'s other rules say. Prevails over {b}.",
                      head=[Kw("neg"), head(code)],
                      body=[fetch_req({"emergency": "?x"}), [Kw("="), "?x", True]], **{"superior-to": [Kw(b)]})
            self.rule(id=x, kind="defeasible", owner=owner, cls="exception",
                      doc=f"Exception to the exception: an emergency request of at most {money(mx)} that is cleared under "
                          f"programme P01 is cleared under sub-programme {code}, whatever {parent} says. Prevails over {e}.",
                      head=head(code),
                      body=[fetch_req({"emergency": "?x", "amount": "?a"}), [Kw("="), "?x", True], [Kw("<="), "?a", mx],
                            head("P01")], **{"superior-to": [Kw(e)]})
            L["exception"], L["counter"] = dict(id=e, owner=eo), dict(id=x, max=mx)
        self.P["chain"].append(L)

    def distractor(self):
        k = len(self.P["distractor_rules"]) + 1
        code, i = f"D{k:02d}", self.next_rule()
        if self.rnd.random() < 0.6:
            role, perk = self.rnd.choice(ROLES), PERKS[(k - 1) % len(PERKS)]
            self.rule(id=i, kind="strict", owner="hr", cls="definition",
                      doc=f"Perk {code}: every employee in role {role} is entitled to the {perk}.",
                      head=[Kw("perk"), code, "?e"],
                      body=[[Kw("fetch"), Kw("employee"), {"id": "?e"}, {"role": "?ro"}], [Kw("="), "?ro", role]])
            self.P["distractor_rules"].append(dict(code=code, id=i, kind="perk", role=role, name=perk))
        else:
            unit, tag = self.rnd.choice(ORG_UNITS), TAGS[(k - 1) % len(TAGS)]
            self.rule(id=i, kind="strict", owner="facilities", cls="definition",
                      doc=f"Centre tag {code}: every cost centre of org unit {unit} takes part in the {tag}.",
                      head=[Kw("centre_tag"), code, "?c"],
                      body=[[Kw("fetch"), Kw("cost_centre"), {"id": "?c"}, {"org_unit": "?u"}], [Kw("="), "?u", unit]])
            self.P["distractor_rules"].append(dict(code=code, id=i, kind="centre_tag", org_unit=unit, name=tag))

    # claims
    def claim(self, cid, about, assertion, by, at, vf, vt, backing, qualifier, **links):
        rec = dict(id=Kw(cid), about=about, assertion=assertion, asserted_by=Kw(by), asserted_at=inst(at),
                   valid_from=inst(vf), valid_to=inst(vt) if vt else None, recorded_at=inst("2026-09-14"),
                   backing=backing, qualifier=qualifier)
        for k, v in links.items():
            rec[k] = [Kw(m) for m in v]
        self.claims.append(rec)

    def claim_tree(self, later):
        k = len(self.P["claim_trees"]) + 1
        self.cid += 1
        code, ven, h = f"S{k:02d}", self.rnd.choice(VENDORS), f"H{self.cid}"
        about = f"vendor:{ven}"
        at = f"2026-0{self.rnd.choice([2, 3, 4])}-{self.rnd.choice(['05', '12', '20'])}"
        vt = self.rnd.choice(["2026-12-31", "2026-10-31", None])
        subs = [("insurance_valid", "risk", "required", "Insurance certificate"),
                ("quality_audited", "compliance", "required", "Quality audit"),
                ("delivery_on_time", "operations", "supporting", "Delivery scorecard")]
        ids = [f"{h}.{i + 1}" for i in range(3)]
        self.claim(h, about, [Kw("supplier_qualified"), code, ven], "procurement", at, YEAR[0], vt,
                   f"Supplier list {code}: qualification file Q-{100 + k}", "presumably",
                   depends_on=ids[:2], supports=ids[2:])
        for (pred, by, _, back), i in zip(subs, ids):
            self.claim(i, about, [Kw(pred), code, ven], by, prev_day(at), YEAR[0], None, f"{back} {code}-{ven}", "certainly")
        t = dict(code=code, vendor=ven, top=dict(id=h, asserted_at=at, valid_from=YEAR[0], valid_to=vt),
                 members=[dict(id=i, pred=p, asserter=by, role=role, asserted_at=prev_day(at), valid_from=YEAR[0], valid_to=None)
                          for (p, by, role, _), i in zip(subs, ids)], later=None)
        if later:
            j = self.rnd.choice([0, 2])                 # a required or the supporting member
            m, d = t["members"][j], self.rnd.choice(["2026-05-15", "2026-07-01", "2026-08-10"])
            lid = f"{h}.{4}"
            self.claim(lid, about, [Kw("neg"), [Kw(m["pred"]), code, ven]], m["asserter"], d, d, None,
                       f"Update {code}-{ven}: supersedes {m['id']}", "certainly")
            t["later"] = dict(id=lid, target=m["id"], asserted_at=d, valid_from=d)
        self.P["claim_trees"].append(t)

    def claim_dispute(self, with_sup):
        k = len(self.P["claim_disputes"]) + 1
        self.cid += 1
        code, ven, h = f"X{k:02d}", self.rnd.choice(VENDORS), f"H{self.cid}"
        pred = "export_licensed" if with_sup else "data_protection_ok"
        yes, no = self.rnd.sample(["legal", "compliance"], 2)
        self.claim(f"{h}.1", f"vendor:{ven}", [Kw(pred), code, ven], yes, "2026-04-02", YEAR[0], None,
                   f"Review {code}-{ven} ({yes})", "presumably")
        self.claim(f"{h}.2", f"vendor:{ven}", [Kw("neg"), [Kw(pred), code, ven]], no, "2026-04-09", YEAR[0], None,
                   f"Review {code}-{ven} ({no})", "presumably")
        self.P["claim_disputes"].append(dict(code=code, vendor=ven, pred=pred, superiority=with_sup,
                                             yes=dict(id=f"{h}.1", asserter=yes), no=dict(id=f"{h}.2", asserter=no)))

    # composition
    def build(self):
        B = self.n - CORE_RULES
        if B <= 0:
            return self
        # P01, its chain and the disputes over its category: fixed seeds, growing with N (§3b′)
        self.cat = self.fixed("category").choice(["hardware", "capital", "software"])
        self.programme(clearance=True, exception=True, counter=True, rnd=self.fixed("P01"), cat=self.cat)
        for j in range(1, 2 + round(math.log2(self.n / 50)) + 1):
            self.level(j)
        sups = [None, "for", "against"]
        for i in range(round(self.n / 50)):
            r = self.fixed(f"K{i}")
            self.dispute(sups[i % 3], cat=self.cat, rnd=r, cross=r.choice(["for", "against"]) if i else None)
        fixed = (2 + sum(2 for L in self.P["chain"] if L["exception"])
                 + sum(1 + bool(d["cross"]) for d in self.P["disputes"]))
        want = max(0, round(self.density * self.n / 100) - CORE_INTERACTIONS - fixed)
        n_claims = round(B * CLAIM_RATIO)
        n_cd = max(1, n_claims // 8)                    # claim disputes, alternating with / without superiority
        budget = B - round(self.share * B) - len(self.rules)   # non-distractor rules
        if any(i % 2 == 0 for i in range(n_cd)):        # the authority rule for export_licensed
            sid = self.next_rule()
            self.rule(id=sid, kind="superiority", owner="general_counsel", cls="superiority",
                      doc="Where legal and compliance disagree on a vendor's export licence, legal prevails.",
                      pred=Kw("export_licensed"), order=[Kw("legal"), Kw("compliance")])
            self.P["superiority"] = dict(id=sid, pred="export_licensed", order=["legal", "compliance"])
            want, budget = want - 1, budget - 1
        n_disp, n_exc = want // 2, want - want // 2
        sups = [None, "for", "against"]
        for i in range(n_disp):
            if budget < 2: break
            self.dispute(sups[i % 3]); budget -= 2
        i = 0
        while n_exc > 0 and budget >= 4:
            counter = n_exc >= 2 and i % 2 == 0 and budget >= 5
            nv_before = len(self.rules)
            self.programme(clearance=True, exception=True, counter=counter)
            budget -= len(self.rules) - nv_before
            n_exc -= 2 if counter else 1; i += 1
        while budget >= 2:
            nv_before = len(self.rules)
            self.programme(clearance=self.rnd.random() < 0.5 and budget >= 4)
            budget -= len(self.rules) - nv_before
        assert len(self.rules) <= B, "budget overshoot"
        while len(self.rules) < B:
            self.distractor()
        for i in range(n_cd):
            self.claim_dispute(i % 2 == 0)
        while len(self.claims) < n_claims:
            self.claim_tree(later=len(self.P["claim_trees"]) % 2 == 0)
        return self


# ---------------------------------------------------------------------------- base text, terms, assets
TERMS = {
    "programme_limit_ok": ("programme limit", "procurement", "A programme limit, as opposed to a role's approval limit, bounds a single request under one spending programme; dated versions, the one valid on the request date governs."),
    "programme_cleared": ("programme clearance", "procurement", "Programme clearance, as opposed to approval, says a request may be charged to a programme: within its limit and past the vendor check, subject to the programme's exceptions."),
    "capitalised": ("capitalisation", "controller", "Capitalisation, as opposed to expensing, books a request as an asset; owners may disagree per policy."),
    "perk": ("employee perk", "hr", "An employee perk, as opposed to an approval right, is a benefit granted by role."),
    "centre_tag": ("centre tag", "facilities", "A centre tag, as opposed to an org unit, marks cost centres taking part in a facilities initiative."),
    "supplier_qualified": ("qualified supplier", "procurement", "A qualified supplier, as opposed to an approved vendor in the register, is procurement's claim that a vendor may be used under a supplier list, resting on insurance and quality claims."),
    "insurance_valid": ("supplier insurance", "risk", "Supplier insurance is risk's claim that a vendor's insurance is valid."),
    "quality_audited": ("quality audit", "compliance", "A quality audit is compliance's claim that a vendor passed the audit."),
    "delivery_on_time": ("on-time delivery", "operations", "On-time delivery is operations' claim that a vendor delivers on schedule; it supports, but does not decide, qualification."),
    "export_licensed": ("export licence", "legal", "An export licence is the claim that a vendor holds the licence; legal and compliance may disagree, legal prevails."),
    "data_protection_ok": ("data protection review", "legal", "A data protection review is the claim that a vendor meets data protection requirements; no superiority between asserters is stated."),
}


def splice(text, anchor, items, before_close=True):
    """insert the items (EDN texts) at the end of the vector that closes just before `anchor`"""
    i = text.index(anchor)
    j = text.rindex("]", 0, i)
    return text[:j] + "".join("\n  " + x for x in items) + text[j:]


def base_text(g):
    t = SLICE.read_text()
    preds = set()
    for r in g.rules:
        h = r.get("head")
        if h: preds.add(h[1][0] if h[0] == "neg" else h[0])
    for c in g.claims:
        a = c["assertion"]; preds.add(a[1][0] if a[0] == "neg" else a[0])
    terms = [edn(dict(id=f"term:{p}", label=TERMS[p][0], synonyms=[], owner=Kw(TERMS[p][1]), definition=TERMS[p][2]))
             for p in sorted(preds)]
    have = {"vendor:bolt", "vendor:cog"}
    assets = [edn(dict(id=f"vendor:{v}", kind=Kw("vendor"), doc=f"Vendor {v}."))
              for v in sorted({c["about"].split(":")[1] for c in g.claims}) if f"vendor:{v}" not in have]
    head = (f";; GENERATED by bench/gen.py (n={g.n} seed={g.seed} density={g.density} distractors={g.share}); do not edit.\n"
            f";; The slice (spikes/v3/shared/slice.edn) with {len(g.rules)} generated rules and {len(g.claims)} claims spliced in.\n")
    if g.rules or g.claims:
        t = splice(t, "\n\n ;; ------------------------------------------------------------------ physical model", assets)
        t = splice(t, "\n\n :code-lists", terms)
        t = splice(t, "\n\n ;; ------------------------------------------------------------------ claims", [edn(r) for r in g.rules])
        k = t.rindex("}")
        j = t.rindex("]", 0, k)
        t = t[:j] + "".join("\n  " + edn(c) for c in g.claims) + t[j:]
    return head + t


# ---------------------------------------------------------------------------- questions (for keys), from the data
def questions(g, con):
    """A few goals per family instance that exercise its branches; requests and employees picked from the data."""
    rnd = random.Random(f"q:{g.seed}:{g.n}")
    Q, q = [], lambda s, *a: con.execute(s, list(a)).fetchall()
    pick = lambda rows: rnd.choice(rows)[0] if rows else None
    def add(kind, **x):
        Q.append(dict(id=f"B{len(Q) + 1:03d}", kind=kind, **x))
    for p in g.P["programmes"]:
        rs = []
        for v in p["versions"]:
            rs.append(pick(q("SELECT id FROM req WHERE category = ? AND date BETWEEN ? AND ? AND amount <= ? ORDER BY id LIMIT 50",
                             p["category"], v["valid_from"], v["valid_to"], v["limit"])))
            rs.append(pick(q("SELECT id FROM req WHERE category = ? AND date BETWEEN ? AND ? AND amount > ? ORDER BY id LIMIT 50",
                             p["category"], v["valid_from"], v["valid_to"], v["limit"])))
        for r in filter(None, rs):
            add("decide", goal=["programme_limit_ok", p["code"], r])
        c = p["clearance"]
        if c:
            cr = [x for x in rs if x][:2]
            if c["exception"]:
                ven = c["exception"]["vendor"]
                cr.append(pick(q("SELECT id FROM req WHERE category = ? AND vendor = ? AND NOT emergency ORDER BY id LIMIT 50", p["category"], ven)))
                cr.append(pick(q("SELECT id FROM req WHERE category = ? AND vendor = ? AND emergency AND amount <= 12000 ORDER BY id LIMIT 50", p["category"], ven)))
            for r in filter(None, cr):
                add("decide", goal=["programme_cleared", p["code"], r])
    for d in g.P["disputes"]:
        lo, hi = d["for"]["min"], d["against"]["below"]
        for cond in (f"amount < {lo}", f"amount >= {lo} AND amount < {hi}", f"amount >= {hi}"):
            r = pick(q(f"SELECT id FROM req WHERE category = ? AND {cond} ORDER BY id LIMIT 50", d["category"]))
            if r: add("decide", goal=["capitalised", d["category"], r])
    if g.P["chain"]:                                   # P01's chain: probes through every level (§3b′)
        p = g.P["programmes"][0]
        ven, v = p["clearance"]["exception"]["vendor"], max(p["versions"], key=lambda v: v["limit"])
        cuts = sorted({c for d in g.P["disputes"] if d["p01"] for c in (d["for"]["min"], d["against"]["below"])
                       if c < v["limit"]})             # one probe per interval between the capitalisation thresholds
        bands = list(zip([0] + cuts, cuts + [v["limit"] + 1]))
        conds = [f"NOT emergency AND amount >= {lo} AND amount < {hi}" for lo, hi in bands]
        conds += ["emergency AND amount <= 8000", "emergency AND amount > 20000"]
        for cond in conds:
            r = pick(q(f"SELECT id FROM req WHERE category = ? AND vendor <> ? AND date BETWEEN ? AND ? AND amount <= ? "
                       f"AND {cond} ORDER BY id LIMIT 50", p["category"], ven, v["valid_from"], v["valid_to"], v["limit"]))
            if not r: continue
            add("decide", goal=["capitalised", p["category"], r])
            for L in g.P["chain"]:
                add("decide", goal=[L["pred"], r])
    for x in g.P["distractor_rules"][:6]:                # one member and one non-member each
        t, col, val = ("emp", "role", x["role"]) if x["kind"] == "perk" else ("cc", "org_unit", x["org_unit"])
        for op in ("=", "<>"):
            add("decide", goal=[x["kind"], x["code"], pick(q(f"SELECT id FROM {t} WHERE {col} {op} ? ORDER BY id LIMIT 50", val))])
    for t in g.P["claim_trees"]:
        add("claim", asset=f"vendor:{t['vendor']}", claim=t["top"]["id"])
        if t["later"]:
            add("claim", asset=f"vendor:{t['vendor']}", claim=t["top"]["id"], as_of=prev_day(t["later"]["valid_from"]))
    for c in g.P["claim_disputes"]:
        add("claim", asset=f"vendor:{c['vendor']}", claim=c["yes"]["id"])
        add("decide", goal=[c["pred"], c["code"], c["vendor"]])
    once = {json.dumps({k: v for k, v in x.items() if k != "id"}): x for x in reversed(Q)}   # one question per goal
    return [dict(x, id=f"B{i + 1:03d}") for i, x in enumerate(sorted(once.values(), key=lambda x: x["id"]))]


# ---------------------------------------------------------------------------- UNION ALL report (RESULTS residual 6)
def union_all_shapes(rules):
    """Fetch shapes that flush() would batch as UNION ALL: within one predicate's dependency closure, one concept
    fetched with the same filter columns and two or more distinct constant filters (so a set-at-a-time evaluation
    varies more than one filter column). -> [{concept, columns, constants, predicates, generated}]"""
    def is_var(x): return isinstance(x, str) and x.startswith("?")
    heads = {}
    for r in rules:
        h = r.get("head")
        if not h: continue
        h = h[1] if h[0] == "neg" else h
        heads.setdefault(h[0], []).append(r)
    def lits(body):
        for b in body or []:
            if b[0] == "agg": yield from lits(b[3])
            elif b[0] == "not": yield b[1]
            else: yield b
    def closure(p, seen):
        if p in seen: return
        seen.add(p)
        for r in heads.get(p, []):
            for b in lits(r.get("body")):
                if b[0] != "fetch": closure(b[0], seen)
    shapes = {}
    for p in heads:
        cl = set(); closure(p, cl)
        for q in cl:
            for r in heads.get(q, []):
                for b in lits(r.get("body")):
                    if b[0] != "fetch": continue
                    const = ", ".join(f"{k}={v}" for k, v in sorted(b[2].items()) if not is_var(v))
                    if const:
                        shapes.setdefault((b[1], tuple(sorted(b[2]))), {}).setdefault(p, {})[const] = r["id"]
    out = {}
    for (concept, cols), per in sorted(shapes.items()):
        for p, consts in sorted(per.items()):
            if len(consts) > 1:
                key = (concept, cols, tuple(sorted(consts)), tuple(sorted(consts.values())))
                out.setdefault(key, []).append(p)
    return [dict(concept=c, columns=list(cols), constants=list(k), rules=list(ids), predicates=ps,
                 generated=any(i.startswith("G") for i in ids)) for (c, cols, k, ids), ps in out.items()]


# ---------------------------------------------------------------------------- main
def generate(n, seed, density, distractors, out):
    import duckdb
    g = Gen(n, seed, density, distractors).build()
    out.mkdir(parents=True, exist_ok=True)
    stem = out / f"N{n:03d}"
    (stem.with_suffix(".edn")).write_text(base_text(g))
    load = [str(stem.with_suffix(".edn")), str(EXT)]
    v = integrity.gate(load)
    if v:
        raise SystemExit(f"N={n}: generated base rejected by the integrity gate: {json.dumps(v)[:2000]}")
    con = duckdb.connect(str(SHARED / "slice.duckdb"), read_only=True)
    Q = questions(g, con)
    S, rules, claims = integrity.rule_base(load)
    mc = MC.check(S, rules, claims, Q, MC.declared_modes())
    if not mc["ok"]:
        raise SystemExit(f"N={n}: questions fail the mode check: {mc['errors'][:5]}")
    ua = union_all_shapes(rules)
    inter = (sum(1 for p in g.P["programmes"] if p["clearance"] and p["clearance"]["exception"])
             + sum(1 for p in g.P["programmes"] if p["clearance"] and p["clearance"]["counter"])
             + sum(2 for L in g.P["chain"] if L["exception"]) + sum(bool(d["cross"]) for d in g.P["disputes"])
             + len(g.P["disputes"]) + (1 if g.P["superiority"] else 0) + CORE_INTERACTIONS)
    rep = dict(rules=len(rules), claims=len(claims), generated_rules=len(g.rules), generated_claims=len(g.claims),
               interactions=inter, density_per_100=round(100 * inter / len(rules), 1),
               distractor_share=round(len(g.P["distractor_rules"]) / max(1, len(g.rules)), 2),
               questions=len(Q), union_all=ua)
    g.P["report"] = rep
    (stem.with_suffix(".params.json")).write_text(json.dumps(g.P, indent=1) + "\n")
    (stem.with_suffix(".questions.json")).write_text(json.dumps(Q, indent=1) + "\n")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="*", default=NS)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--density", type=float, default=20)
    ap.add_argument("--distractors", type=float, default=0.3)
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    a = ap.parse_args()
    for n in a.n:
        rep = generate(n, a.seed, a.density, a.distractors, a.out)
        ua = rep.pop("union_all")
        print(f"N={n}", rep)
        for u in ua:
            print(f"  UNION ALL shape ({'generated' if u['generated'] else 'slice'}): {u['concept']} on {u['columns']}, "
                  f"constants {u['constants']} ({', '.join(u['rules'])}), reached from {', '.join(u['predicates'])}")


if __name__ == "__main__":
    main()
