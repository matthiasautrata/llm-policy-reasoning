"""Shared helpers for the projections: which relations a layer shows, and value formatting."""
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = yaml.safe_load((ROOT / "world/schema.yaml").read_text())["relations"]


def relations(k):
    """Schema records of the relations shown at layer k (layers are cumulative)."""
    return [r for r in SCHEMA if r["layer"] <= k]


def date_int(s):
    return int(s.replace("-", ""))
