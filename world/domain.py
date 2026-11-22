"""Domain constants of the procurement world (entities, sizes, dated versions).

The rule logic lives in rules/rules.yaml; this file only fixes what the generator draws from.
Dates are datetime.date here, ISO strings in world.json, integers YYYYMMDD in facts.pl.
"""
from datetime import date

# size -> (depth, branching, analysts per leaf)
SIZES = {"S": (2, 2, 2), "M": (3, 3, 3), "L": (4, 3, 2)}
SEEDS = (1, 2, 3)

TODAY = date(2026, 9, 15)
YEAR_START, YEAR_END = date(2026, 1, 1), date(2026, 12, 31)
REQ_FROM = date(2026, 6, 1)          # requests are raised between REQ_FROM and TODAY

# role -> [(limit, valid_from, valid_to)]; the manager limit rises on 1 August (fork c2 bites on 25k-40k requests)
ROLE_LIMITS = {
    "analyst": [(5000, YEAR_START, YEAR_END)],
    "manager": [(25000, YEAR_START, date(2026, 7, 31)), (40000, date(2026, 8, 1), YEAR_END)],
    "senior_manager": [(50000, YEAR_START, YEAR_END)],
    "director": [(100000, YEAR_START, YEAR_END)],
    "vp": [(500000, YEAR_START, YEAR_END)],
}
# vendor -> [(status, valid_from, valid_to)]
VENDORS = {
    "acme": [("approved", YEAR_START, YEAR_END)],
    "bolt": [("approved", YEAR_START, date(2026, 7, 31)), ("suspended", date(2026, 8, 1), YEAR_END)],
    "cog": [("approved", YEAR_START, YEAR_END)],
    "dyne": [("suspended", YEAR_START, date(2026, 6, 30)), ("approved", date(2026, 7, 1), YEAR_END)],
    "edge": [("approved", YEAR_START, YEAR_END)],
    "fern": [("suspended", YEAR_START, YEAR_END)],
}
# exemption id -> (category, granted, withdrawn or None)
EXEMPTIONS = {"capex": ("capital", date(2026, 1, 1), date(2026, 8, 10))}

AMOUNTS = [3000, 8000, 12000, 20000, 30000, 38000, 45000, 60000, 90000, 120000]
CATEGORIES = ["software", "hardware", "services", "capital"]
REQ_RATIO = 0.8          # requests per employee (at least 8)
P_CANCELLED = 0.10
P_EMERGENCY = 0.25
P_VIOLATION = 0.10       # share of non-vp staff
P_TRANSFER = 0.08        # share of analysts moved between leaves (at least 2)
LEAF_UNITS = ["delivery", "support"]
INTERNAL_UNIT = "leadership"


def as_of(versions, d):
    """The value of the version (value, from, to) that is valid on d, or None."""
    return next((v for v, f, t in versions if f <= d <= t), None)
