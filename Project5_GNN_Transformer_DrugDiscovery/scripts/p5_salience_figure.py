#!/usr/bin/env python3
"""
P5 — H3 salience figure: descriptor-dimension salience (mean |W| of fusion head)
for GIN-TFP and GIN-TNE under scaffold split. Bars colored by TFP block
(H0: 0-32, pers_img: 33-57, betti: 58-77). TNE shown as plain bar chart.

Usage:
    python scripts/p5_salience_figure.py [--output results/figures/p5_salience.png]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

P5_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = P5_ROOT / "results"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    out = Path(args.output) if args.output else OUT_DIR / "figures" / "p5_salience.png"

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    tfp = json.load(open(OUT_DIR / "p5_GIN-TFP_scaffold_salience.json"))
    ax = axes[0]
    sal = np.asarray(tfp["salience_mean"])
    colors = np.where(np.arange(78) < 33, "#4c72b0",
              np.where(np.arange(78) < 58, "#dd8452", "#55a868"))
    ax.bar(np.arange(78), sal, color=colors, width=0.8)
    ax.axvspan(32.5, 57.5, color="#dd8452", alpha=0.10)
    ax.axvspan(57.5, 78, color="#55a868", alpha=0.10)
    ax.set_title("GIN-TFP salience (scaffold) — H(0:33) pers_img(33:58) betti(58:78)")
    ax.set_xlabel("TFP dimension")
    ax.set_ylabel("mean |W| (fusion head)")
    ax.set_xlim(-1, 78)

    tne = json.load(open(OUT_DIR / "p5_GIN-TNE_scaffold_salience.json"))
    ax = axes[1]
    sal = np.asarray(tne["salience_mean"])
    order = np.argsort(-sal)
    ax.bar(np.arange(192), sal[order], color="#1f77b4", width=0.8)
    ax.set_title("GIN-TNE salience (scaffold) — dims sorted desc")
    ax.set_xlabel("TNE dimension (rank)")
    ax.set_xlim(-1, 192)

    fig.suptitle("P5 H3: descriptor salience in topological fusion (mean |W|, 25 fold×seed)", fontsize=13)
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
