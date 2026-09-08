#!/usr/bin/env python3
"""
P2 — Figure: P2Rank predicted pockets vs Vina grid box centers.

Two-panel figure for the Supporting Information:
  left  : bar chart of distance (Angstrom) between the top-3 P2Rank pocket
          centers and the Vina box center, per receptor with a grid (7F3Y,
          6UKJ, 9N10); 6UKJ highlighted (concordant).
  right : 3D scatter of Vina box center vs top P2Rank pocket centers per
          receptor (same frame pairs only), with the box extent indicated.

Reads: results/p2rank_boxes_20260827/out/*_predictions.csv
        + the grid centers embedded below (from data/from_project1/docking/Docking_*/config.txt).
Writes: results/figures/figure_p2rank_boxes.pdf (+ .png)

Usage: python scripts/p2_figure_p2rank_boxes.py  (malaria_md env)
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

P2_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = P2_ROOT / "results" / "p2rank_boxes_20260827" / "out"
FIG_DIR = P2_ROOT / "results" / "figures"

# Vina grid box centers (config.txt) for receptors with a P2 grid
GRIDS = {
    "7F3Y": {"name": "PfDHFR (7F3Y)", "center": (1.33, -1.733, -23.842), "size": 25},
    "6UKJ": {"name": "PfCRT (6UKJ)", "center": (152.99, 151.042, 159.379), "size": 25},
    "9N10": {"name": "PfATP4 (9N10)", "center": (134.84, 133.10, 97.63), "size": 25},
}


def load_pockets(pdb: str, topn: int = 3) -> list[dict]:
    path = OUT_DIR / f"{pdb}.pdb_predictions.csv"
    if not path.exists():
        return []
    with open(path) as f:
        rows = list(csv.DictReader(f))
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in rows]
    return [
        {"rank": int(r["rank"]), "score": float(r["score"]),
         "prob": float(r["probability"]),
         "center": (float(r["center_x"]), float(r["center_y"]), float(r["center_z"]))}
        for r in rows[:topn]
    ]


def main() -> int:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    pdbs = list(GRIDS.keys())
    pockets = {p: load_pockets(p) for p in pdbs}

    # ---- panel (a): distance bar chart -------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5),
                                   gridspec_kw={"width_ratios": [1.1, 1]})

    labels, dists, colors = [], [], []
    for p in pdbs:
        cx, cy, cz = GRIDS[p]["center"]
        short = GRIDS[p]["name"].split("(")[0].strip()
        for pk in pockets[p][:3]:
            px, py, pz = pk["center"]
            d = math.sqrt((px - cx) ** 2 + (py - cy) ** 2 + (pz - cz) ** 2)
            labels.append(f"{short}\npocket {pk['rank']}")
            dists.append(d)
            colors.append("#2a9d8f" if p == "6UKJ" else "#8ab4f8")
    x = np.arange(len(labels))
    bars = ax1.bar(x, dists, color=colors, edgecolor="black", linewidth=0.4)
    ax1.axhline(12.5, color="red", ls="--", lw=1.2,
                label="box half-edge (12.5 Å)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8, ha="center")
    ax1.set_ylabel("Distance pocket center – Vina box center (Å)", fontsize=9)
    ax1.set_title("(a) P2Rank pocket centres vs Vina box centres", fontsize=10)
    ax1.legend(fontsize=8)
    for b, d in zip(bars, dists):
        ax1.text(b.get_x() + b.get_width() / 2, d + 0.8, f"{d:.1f}",
                 ha="center", va="bottom", fontsize=8)
    ax1.set_ylim(0, max(dists) * 1.15)

    # ---- panel (b): 3D scatter --------------------------------------
    ax2.remove()
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    markers = {"7F3Y": "o", "6UKJ": "s", "9N10": "^"}
    for p in pdbs:
        cx, cy, cz = GRIDS[p]["center"]
        ax2.scatter(*GRIDS[p]["center"], marker="*", s=160, c="red",
                    edgecolors="black", linewidth=0.5, label=f"{GRIDS[p]['name']} Vina box")
        for pk in pockets[p][:3]:
            ax2.scatter(*pk["center"], marker=markers[p], s=55,
                        c="#2a9d8f" if p == "6UKJ" else "#8ab4f8",
                        alpha=0.85, edgecolors="black", linewidth=0.3)
    ax2.set_xlabel("x (Å)"); ax2.set_ylabel("y (Å)"); ax2.set_zlabel("z (Å)")
    ax2.set_title("(b) Vina box centres (*) and top-3 P2Rank pockets\n"
                  "per receptor (same frame pairs)", fontsize=10)
    ax2.legend(fontsize=7, loc="upper left", framealpha=0.9)

    fig.suptitle("")
    fig.tight_layout()

    pdf = FIG_DIR / "figure_p2rank_boxes.pdf"
    png = FIG_DIR / "figure_p2rank_boxes.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=200, bbox_inches="tight")
    print(f"Wrote {pdf} and {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
