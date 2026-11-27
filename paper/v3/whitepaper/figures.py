#!/usr/bin/env python3
"""The white paper's three charts, scored from the committed results with bench/score.py (no API calls).

    .venv/bin/python paper/v3/whitepaper/figures.py          # writes fig/*.svg and fig/numbers.json

Scope: family questions, manager answers, N 200, arms G (the document) and T (the engine), every model setting
of the confirmatory runs. fig/numbers.json holds every number drawn, for the text to cite and for review."""
import collections, gzip, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "bench"), str(ROOT / "spikes/v3/shared")]
import score as S                                    # noqa: E402
import run as B                                      # noqa: E402

RUNS = ["b3c", "b3d-glm", "b3e", "b3f", "b3g"]
N, ARMS = 200, {"G": "Rules as a document", "T": "Rules evaluated by the engine"}
INK, INK2, GRID = "#191919", "#666666", "#e6e6e6"
COLOR = {"G": "#f47230", "T": "#257de0"}           # reference palette slots 2 and 1
KBINS = [(1, 1), (2, 3), (4, 5), (6, 99)]


def records():
    for run in RUNS:
        for line in gzip.open(ROOT / f"bench/results/{run}.jsonl.gz", "rt"):
            r = json.loads(line) if line.strip() else None
            if (r and r["kind"] == "manager" and not r["error"] and r["n"] == N and S.arm(r) in ARMS
                    and S.group(r["item"]) == "family"):
                yield dict(r, cost=B.cost_of(r))


NAMES = {"deepseek-v4.1-flash": "DeepSeek v4.1 Flash", "glm-5.3": "GLM 5.3", "gpt-6.2-sol": "GPT-6.2 Sol"}
EFFORT = ["medium", "high", "max"]


def setting(r):
    m = r["model"].split("/")[-1].split("@")[-1]
    e = (r.get("config") or {}).get("reasoning")
    return NAMES.get(m, m) + (f", {e}" if e else "")


def order(s):
    e = s.rsplit(", ", 1)[-1]
    return (s.startswith("GPT"), EFFORT.index(e) if e in EFFORT else -1, s)


def kind(key):
    if "standing" in key:
        return "claim"
    if key["status"] == "CONFLICT":
        return "contested"
    return "absence" if key["qualifier"] is not None else "plain"


def tally():
    t = collections.defaultdict(lambda: collections.Counter())
    for r in records():
        it = B.item(r["item"], r["n"])
        key, s = B.manager_key(it), S.score_manager(r)
        c = t[(setting(r), S.arm(r))]
        k = kind(key)
        c["cells"] += 1; c["correct"] += s["correct"]; c["cost"] += r["cost"] or 0.0
        c[k] += 1
        if k == "plain":
            c["plain_value_ok"] += s["status_ok"] and s["value_ok"]
        if k == "absence":
            c["absence_flagged"] += s["qualifier_ok"]; c["absence_correct"] += s["correct"]
        if k == "contested":
            c["sides_ok"] += s["sides_ok"]
        b = S._bin(it["k"], KBINS)
        c[f"k{b}"] += 1; c[f"k{b}_correct"] += s["correct"]
    return {f"{m} | {a}": dict(c) for (m, a), c in sorted(t.items())}


def style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, labelcolor=INK, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


import matplotlib.ticker  # noqa: E402


def dumbbell(ax, rows, g, t, xmax, title, fmt="{:.0f}", log=False):
    y = range(len(rows))[::-1]
    for yi, a, b in zip(y, g, t):
        ax.plot([a, b], [yi, yi], color=GRID, linewidth=2, zorder=1)
        ax.scatter([a], [yi], s=36, color=COLOR["G"], zorder=2, edgecolor="white", linewidth=1.5)
        ax.scatter([b], [yi], s=36, color=COLOR["T"], zorder=3, edgecolor="white", linewidth=1.5)
    ax.set_yticks(list(y)); ax.set_yticklabels(rows)
    if log:
        ax.set_xscale("log")
    else:
        ax.set_xlim(-0.5, xmax + 0.5)
    ax.set_title(title, loc="left", color=INK, fontsize=8.5, pad=8)
    if not log:
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=4, integer=True))
    style(ax)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "path"})
    W = 6.5                                          # inches: the width of a text column, so figures render at text width
    d = tally()
    (HERE / "fig").mkdir(exist_ok=True)
    (HERE / "fig/numbers.json").write_text(json.dumps(d, indent=1) + "\n")
    settings = sorted({k.split(" | ")[0] for k in d}, key=order)
    get = lambda m, a, f: d.get(f"{m} | {a}", {}).get(f, 0)
    legend = [Line2D([], [], marker="o", linestyle="", markersize=6, color=COLOR[a], label=ARMS[a]) for a in ARMS]

    # 1: values right, missing data flagged, conflict sides named
    fig, axs = plt.subplots(1, 3, figsize=(W, 2.9), sharey=True)
    panels = [("plain", "plain_value_ok", "Value right,\nno dispute"),
              ("absence", "absence_correct", '"No" from missing\ndata, flagged'),
              ("contested", "sides_ok", "Conflict, every\nside named")]
    for ax, (den, num, title) in zip(axs, panels):
        n = max(get(m, a, den) for m in settings for a in ARMS)
        dumbbell(ax, settings, [get(m, "G", num) for m in settings], [get(m, "T", num) for m in settings], n,
                 f"{title}\n(of {n})")
    fig.legend(handles=legend, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(HERE / "fig/reliability.svg", bbox_inches="tight")

    # 2: correct by number of rules an answer depends on, pooled over settings
    fig, ax = plt.subplots(figsize=(W, 2.9))
    bins = [S._bin(lo, KBINS) for lo, _ in KBINS]
    for a in ARMS:
        share = [sum(get(m, a, f"k{b}_correct") for m in settings) / max(1, sum(get(m, a, f"k{b}") for m in settings))
                 for b in bins]
        ax.plot(bins, [100 * s for s in share], color=COLOR[a], linewidth=2, marker="o", markersize=6,
                markeredgecolor="white", markeredgewidth=1.5)
        ax.annotate(ARMS[a], (len(bins) - 1, 100 * share[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", color=INK, fontsize=8)
    ax.set_ylim(0, 105); ax.set_ylabel("answers fully correct (%)", color=INK2)
    ax.set_xlabel("rules and claims the answer depends on", color=INK2)
    ax.set_title("Fully correct answers by rules involved\n200 rules, five model settings pooled", loc="left",
                 color=INK, fontsize=8.5, pad=8)
    style(ax); ax.grid(axis="x", visible=False); ax.grid(axis="y", color=GRID, linewidth=0.8)
    fig.tight_layout()
    fig.savefig(HERE / "fig/growth.svg", bbox_inches="tight")

    # 3: cost per correct answer
    fig, ax = plt.subplots(figsize=(W, 2.6))
    per = lambda m, a: get(m, a, "cost") / max(1, get(m, a, "correct"))
    g, t = [per(m, "G") for m in settings], [per(m, "T") for m in settings]
    dumbbell(ax, settings, g, t, None, "Cost per fully correct answer\nUSD at list price, 200 rules, log scale", log=True)
    ax.set_xticks([0.001, 0.002, 0.005, 0.01, 0.02, 0.05]); ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_xlim(0.001, 0.05)
    for yi, a, b in zip(range(len(settings))[::-1], g, t):
        ax.annotate(f"{100 * (b - a) / a:.0f} %".replace("-", "\u2212"), (max(a, b), yi), xytext=(8, 0), textcoords="offset points",
                    va="center", color=INK2, fontsize=8)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:g}"))
    fig.legend(handles=legend, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(HERE / "fig/cost.svg", bbox_inches="tight")


if __name__ == "__main__":
    main()
