#!/usr/bin/env python3
"""Generate Figure S1: MPO sensitivity analysis heatmap."""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401 — registers styles
import matplotlib.colors as mcolors
import numpy as np
import os
from matplotlib.patches import Patch

SCIENCE_STYLE = ['science', 'no-latex', 'grid']

CSV_PATH = os.path.join(os.path.dirname(__file__),
                         "../results/candidate_selection/mpo_sensitivity_analysis.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "../manuscript/Graphics")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    labels = {
        "w_vina": "Vina (35%)",
        "w_diff": "DiffDock (25%)",
        "w_qed": "QED (20%)",
        "w_admet": "ADMET (15%)",
        "w_ro5": "Ro5 (5%)",
    }
    var_labels = {"-0.2": "-20%", "-0.1": "-10%", "0.1": "+10%", "0.2": "+20%"}

    weights = list(labels.keys())
    variations = ["-0.2", "-0.1", "0.1", "0.2"]

    matrix = np.zeros((len(weights), len(variations)))
    for i, w in enumerate(weights):
        for j, v in enumerate(variations):
            row = df[(df["weight"] == w) & (df["variation"] == float(v))]
            if not row.empty:
                matrix[i, j] = row["jaccard_similarity"].values[0]

    # Discrete colormap: red for 0.5, green for 1.0
    cmap = mcolors.ListedColormap(["#D32F2F", "#388E3C"])
    bounds = [0.0, 0.75, 1.01]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    with plt.style.context(SCIENCE_STYLE):
        fig, ax = plt.subplots(figsize=(7, 4))
        im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

        ax.set_xticks(range(len(variations)))
        ax.set_xticklabels([var_labels[v] for v in variations])
        ax.set_yticks(range(len(weights)))
        ax.set_yticklabels([labels[w] for w in weights])

        for i in range(len(weights)):
            for j in range(len(variations)):
                val = matrix[i, j]
                txt = f"{val:.2f}"
                ax.text(j, i, txt, ha="center", va="center",
                        fontsize=12, fontweight="bold", color="white")

        ax.set_xlabel("Weight variation", labelpad=10)
        ax.set_ylabel("MPO component", labelpad=10)

        legend_elements = [
            Patch(facecolor="#388E3C", edgecolor="white",
                  label="Jaccard = 1.00 (stable)"),
            Patch(facecolor="#D32F2F", edgecolor="white",
                  label="Jaccard = 0.50 (unstable)"),
            Patch(facecolor="none", edgecolor="red", linestyle="--",
                  linewidth=1.5, label="Threshold (0.70)"),
        ]
        ax.legend(handles=legend_elements, loc="lower right", fontsize=9,
                  framealpha=0.9, fancybox=False)

        fig.tight_layout()
        out_path = os.path.join(OUT_DIR, "Figure_S1_MPO_sensitivity.pdf")
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        fig.savefig(out_path.replace(".pdf", ".png"), dpi=300, bbox_inches="tight")
        plt.close(fig)

    print(f"Saved: {out_path}")
    print(f"Saved: {out_path.replace('.pdf', '.png')}")


if __name__ == "__main__":
    main()
