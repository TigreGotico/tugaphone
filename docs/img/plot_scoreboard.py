"""Draw docs/img/scoreboard.svg: rules-only PER and stress accuracy of each dialect with human gold.

Run from the repo root: python docs/img/plot_scoreboard.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import save  # noqa: E402

rows = [{"dialect": r["dialect"], "per": r["per"], "stress_acc": r["stress_acc"]}
        for r in sorted(json.loads((ROOT / "benchmarks" / "results.json").read_text(encoding="utf-8")),
                        key=lambda r: r["per"])
        if r["reference_kind"] == "human"]


def draw(fig, theme, rows):
    per, stress = fig.subplots(1, 2, sharey=True, width_ratios=[3, 2])
    y = range(len(rows))
    per.barh(y, [r["per"] for r in rows], height=0.6, color=theme["series"][0])
    for i, r in zip(y, rows):
        per.text(r["per"] + 0.004, i, f"{r['per']:.3f}", va="center", fontsize=8, color=theme["text"])
    per.set_xlim(0, max(r["per"] for r in rows) * 1.2)
    per.set_title("PER, rules only (lower is better)", fontsize=9)
    per.set_yticks(list(y), [r["dialect"] for r in rows], fontsize=8)
    per.invert_yaxis()
    per.grid(axis="y", visible=False)

    scored = [(i, r["stress_acc"]) for i, r in zip(y, rows) if r["stress_acc"] is not None]
    stress.scatter([a for _, a in scored], [i for i, _ in scored], s=36, color=theme["series"][0], zorder=3)
    for i, a in scored:
        stress.text(a - 0.002, i, f"{a:.3f}", va="center", ha="right", fontsize=8, color=theme["text"])
    stress.set_xlim(0.95, 1.004)
    stress.set_xticks([0.95, 0.96, 0.97, 0.98, 0.99, 1.0])
    stress.set_title("Stress accuracy (higher is better)", fontsize=9)
    stress.grid(axis="y", visible=False)


save(str(ROOT / "docs" / "img" / "scoreboard"), draw, rows, width=8, height=3.4)
