"""Generate submission-quality secondary figures from canonical result tables.

This script intentionally performs no refitting. It reads the stored summary tables
produced by the canonical analyses and renders publication figures at 300 dpi.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
GRAPHICS = ROOT / "manuscript" / "LaTeX" / "Graphics"

plt.rcParams.update({
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 120,
    "savefig.dpi": 300,
})


def save(fig: plt.Figure, *paths: Path) -> None:
    fig.tight_layout()
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def tne_regression() -> None:
    src = RESULTS / "p3_physical_validation" / "p3_tne_regression.csv"
    df = pd.read_csv(src)
    targets = list(df["target"].drop_duplicates())
    descriptors = ["TNE (192-dim)", "ECFP4 (2048-bit)"]
    colors = {descriptors[0]: "#2878b5", descriptors[1]: "#d95f02"}

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    x = np.arange(len(targets))
    width = 0.34
    for i, descriptor in enumerate(descriptors):
        vals = [
            float(df.loc[(df["target"] == target) & (df["descriptor"] == descriptor), "R2"].iloc[0])
            for target in targets
        ]
        bars = ax.bar(
            x + (i - 0.5) * width,
            vals,
            width,
            label=descriptor,
            color=colors[descriptor],
            edgecolor="white",
            linewidth=0.5,
        )
        ax.bar_label(bars, labels=[f"{v:.3f}" for v in vals], padding=2, fontsize=7)

    ax.set_xticks(x, [t.replace(" (", "\n(") for t in targets])
    ax.set_ylim(0, 0.68)
    ax.set_ylabel(r"Cross-validated $R^2$ for computational docking score")
    ax.set_title("Information-retention analysis: TNE versus ECFP4")
    ax.grid(axis="y", alpha=0.22, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    fig.text(
        0.01,
        0.01,
        "Random Forest, 5-fold CV; values are read from the canonical regression summary table.",
        ha="left",
        va="bottom",
        fontsize=7,
        color="#444444",
    )
    save(
        fig,
        RESULTS / "p3_physical_validation" / "p3_tne_regression_summary.png",
        GRAPHICS / "p3_tne_regression_summary.png",
    )


def ga_discriminator() -> None:
    src = RESULTS / "p3_ga_discriminator.csv"
    df = pd.read_csv(src).sort_values("n_generated")
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    x = df["n_generated"].to_numpy()
    ax.plot(x, df["auc_ecfp4_tanimoto"], "o-", lw=2, ms=5, label="ECFP4 Tanimoto", color="#d95f02")
    ax.plot(x, df["auc_quantum_kernel"], "o-", lw=2, ms=5, label="Quantum-kernel density", color="#2878b5")
    ax.axhline(0.5, color="#666666", ls="--", lw=1, label="Random performance")
    ax.set_xscale("symlog", linthresh=50)
    ax.set_xticks(x, [str(v) for v in x])
    ax.set_ylim(0.35, 1.05)
    ax.set_xlabel("Number of expanded molecules ($N$)")
    ax.set_ylabel("AUC--ROC")
    ax.set_title("Structural-discrimination benchmark")
    ax.grid(axis="y", alpha=0.22, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right")
    fig.text(
        0.01,
        0.01,
        "200 reference seeds; canonical stored discriminator results; computational structural endpoint.",
        ha="left",
        va="bottom",
        fontsize=7,
        color="#444444",
    )
    save(fig, RESULTS / "p3_ga_discriminator.png", GRAPHICS / "p3_ga_discriminator.png")


if __name__ == "__main__":
    tne_regression()
    ga_discriminator()
    print("Generated 300-dpi submission figures from stored canonical result tables.")
