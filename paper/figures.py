"""Figures for the paper, computed from study2-scaling/results (nothing hard-coded).
  python paper/figures.py   -> paper/fig-accuracy.png, paper/fig-time.png
"""
import csv, json, pathlib
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "study2-scaling/results"
WORLDS = ["S-L2", "M-L2", "L-L2"]
FACTS = {w: json.loads((ROOT / "study2-scaling/worlds" / w / "world.json").read_text())["facts"] for w in WORLDS}

# series -> (label, arms pooled, colour, marker); categorical slots 1,2,3,7 of the reference palette (validated)
SERIES = [("English (read)", ["text"], "#2a78d6", "o"),
          ("Datalog (read)", ["datalog"], "#eb6834", "s"),
          ("OWL+SHACL (read)", ["shacl"], "#1baf7a", "^"),
          ("Engine: Soufflé or pySHACL", ["tool", "shacl-tool"], "#4a3aa7", "D")]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURF, "axes.facecolor": SURF})

score = defaultdict(lambda: [0, 0])  # (model, world, arm) -> [correct, graded]
for l in open(RES / "scaling-pilot-20260918.scored.jsonl"):
    r = json.loads(l)
    s = score[(r["model"], r["world"], r["arm"])]; s[0] += r["exact"]; s[1] += 1
answered = {}
for l in open(RES / "scaling-pilot-20260918.jsonl"):
    r = json.loads(l); answered[(r["model"], r["world"], r["arm"])] = bool(r["answer"])
secs = {(r["model"], r["world"], r["arm"]): (float(r["seconds"]) if r["seconds"] else None)
        for r in csv.DictReader(open(RES / "scaling-pilot-20260918.cost.csv"))}

def style(ax):
    ax.set_xscale("log"); ax.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([FACTS[w] for w in WORLDS]); ax.set_xticklabels([f"{w[0]} ({FACTS[w]:,})" for w in WORLDS])
    ax.set_xlabel("world size (facts, log scale)"); ax.minorticks_off()

NUDGE = [0.24, 0.08, -0.08, -0.24]      # vertical offsets so coincident scores stay visible (fig 1 only)
XOFF = {"datalog": 0.92, "shacl": 1.08}  # horizontal offsets for coincident "no answer" markers

# ---- Figure 1: correct answers out of 9 vs world size ----
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
for ax, model in zip(axes, ["claude-haiku", "claude-sonnet"]):
    for (label, arms, col, mk), dy in zip(SERIES, NUDGE):
        xs, ys, fails = [], [], []
        for w in WORLDS:
            cells = [(model, w, a) for a in arms if (model, w, a) in score]
            if not cells: continue
            if not any(answered[c] for c in cells): fails.append(FACTS[w] * XOFF.get(arms[0], 1)); continue
            xs.append(FACTS[w]); ys.append(sum(score[c][0] for c in cells) / len(cells) + dy)
        ax.plot(xs, ys, color=col, marker=mk, markersize=6, linewidth=2, label=label, markeredgecolor=SURF, markeredgewidth=1)
        for f in fails:
            ax.plot([f], [0], marker="x", color=col, markersize=8, markeredgewidth=2)
    if model == "claude-sonnet":
        ax.annotate("Datalog and SHACL read:\nno answer (output\nbudget exhausted)", (FACTS["L-L2"] * 0.9, 0.3), (FACTS["L-L2"] * 0.2, 2.2),
                    fontsize=7.5, color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.set_title(model.replace("claude-", "Claude ").title(), fontsize=10, color=INK, loc="left")
    ax.set_ylim(-0.5, 9.5); ax.set_yticks(range(0, 10, 3)); style(ax)
axes[0].set_ylabel("correct answers (of 9)")
fig.legend(*axes[1].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(0.5, 0.0))
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(ROOT / "paper/fig-accuracy.png", dpi=300)

# ---- Figure 2: Sonnet wall time per run (log) ----
fig, ax = plt.subplots(figsize=(5.2, 3.6))
for label, arms, col, mk in SERIES:
    xs, ys, lo, hi = [], [], [], []
    for w in WORLDS:
        v = [secs[("claude-sonnet", w, a)] for a in arms if ("claude-sonnet", w, a) in secs]
        v = [x for x in v if x is not None]
        if not v:
            ax.plot([FACTS[w] * XOFF.get(arms[0], 1)], [1500], marker="x", color=col, markersize=8, markeredgewidth=2); continue
        xs.append(FACTS[w]); ys.append(sum(v) / len(v)); lo.append(min(v)); hi.append(max(v))
    ax.errorbar(xs, ys, yerr=[[y - l for y, l in zip(ys, lo)], [h - y for y, h in zip(ys, hi)]], color=col, marker=mk,
                markersize=6, linewidth=2, capsize=3, label=label, markeredgecolor=SURF, markeredgewidth=1)
ax.set_yscale("log"); ax.set_ylim(8, 2500); style(ax)
ax.axhline(1500, color=GRID, linewidth=0.8, linestyle="--")
ax.text(FACTS["S-L2"], 1650, "x = no answer (output budget exhausted)", fontsize=7.5, color=INK2)
ax.set_ylabel("wall time per run (s, log scale)")
ax.set_title("Claude Sonnet, override level 2", fontsize=10, color=INK, loc="left")
ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
fig.tight_layout()
fig.savefig(ROOT / "paper/fig-time.png", dpi=300, bbox_inches="tight")
print("figures written")
