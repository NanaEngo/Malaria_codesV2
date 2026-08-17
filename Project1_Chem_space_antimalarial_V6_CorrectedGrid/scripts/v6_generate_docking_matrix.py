#!/usr/bin/env python3
"""Generate 17×4 docking affinity heatmap for P1 V6 (replaces target-wise means bar)."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
V6 = ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid"
VINA = V5 / "results" / "v5_four_target_vina_affinities.csv"
METRICS = V6 / "results" / "derived" / "v6_integrated_candidate_metrics.csv"
OUT = V6 / "results" / "figures"
MANUSCRIPT = V6 / "manuscript" / "Graphics"

TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]


def main():
    # Load data
    vina = pd.read_csv(VINA)
    metrics = pd.read_csv(METRICS)

    # Order by integrated metrics order
    order = metrics["candidate_id"].tolist()
    vina = vina.set_index("candidate_id").loc[order].reset_index()

    # Build matrix
    aff_cols = [f"aff_{t}" for t in TARGETS]
    matrix = vina[aff_cols].values  # shape (17, 4)
    candidates = vina["candidate_id"].tolist()

    # Class labels from metrics
    class_map = dict(zip(metrics["candidate_id"], metrics["RRS_class"]))
    class_colors = {"A*": "#047857", "A": "#0f766e", "B": "#2563eb", "C": "#d97706", "D": "#dc2626"}

    # Plot
    fig, ax = plt.subplots(figsize=(5.5, 8))

    # Diverging colormap centered at -6 (typical Vina range)
    im = ax.imshow(matrix, cmap="YlOrRd_r", aspect="auto", vmin=-8, vmax=-4)

    # Annotate cells
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            text_color = "white" if val < -6.5 else "black"
            ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                    fontsize=8, color=text_color, fontweight="medium")

    # Axes
    ax.set_xticks(range(len(TARGETS)))
    ax.set_xticklabels(TARGETS, fontsize=10, fontweight="bold")
    ax.set_yticks(range(len(candidates)))
    ylabels = [f"{c} ({class_map[c]})" for c in candidates]
    ax.set_yticklabels(ylabels, fontsize=8.5)

    # Color y-tick labels by RRS class
    for i, c in enumerate(candidates):
        cls = class_map[c]
        ax.get_yticklabels()[i].set_color(class_colors.get(cls, "black"))

    ax.set_xlabel("Target", fontsize=11, fontweight="bold")
    ax.set_ylabel("Candidate (RRS class)", fontsize=11, fontweight="bold")
    ax.set_title("17×4 wild-type docking matrix\n(kcal mol⁻¹, AutoDock Vina)",
                 fontsize=12, fontweight="bold", pad=12)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("Vina score (kcal mol⁻¹)", fontsize=9)

    # Geometric gate note
    ax.text(0.5, -0.07, "All 68 pairs pass geometric pose-quality gate; scores are computational estimates, not experimental binding energies.",
            transform=ax.transAxes, ha="center", fontsize=7.5, style="italic", color="gray")

    fig.tight_layout()

    # Save to all locations
    for out_dir in [OUT, MANUSCRIPT]:
        out_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_dir / "p1_v6_docking_matrix.pdf", bbox_inches="tight")
        fig.savefig(out_dir / "p1_v6_docking_matrix.png", dpi=300, bbox_inches="tight")

    plt.close(fig)
    print("Saved p1_v6_docking_matrix.{pdf,png}")


if __name__ == "__main__":
    main()
