#!/usr/bin/env python3
"""Generate two missing P2 Supplementary Material figures:
    1. VAE_latent_space.pdf — top-20 candidates in Paper 1 VAE latent space
    2. rrs_radar_profiles.pdf — per-compound RRS radar plots across 6 mutations

Data sources:
    - P1 MCMC latent coordinates: Project1_Chem_space_antimalarial_V2_CorrectedGrid/p1_mcmc_generated.csv
    - P2 RRS classification: Project2_Polypharmacology_MD_ValidationV2607/results/c_rrs_classification.csv
    - P2 merged metrics: Project2_Polypharmacology_MD_ValidationV2607/results/c_merged_metrics.csv (if available)
"""

from __future__ import annotations

import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
P1_ROOT = PROJECT_ROOT.parent / "Project1_Chem_space_antimalarial_V2_CorrectedGrid"
P2_RESULTS = PROJECT_ROOT / "results"
GRAPHICS_DIR = PROJECT_ROOT / "manuscript" / "Graphics"

# Ensure output directory exists
GRAPHICS_DIR.mkdir(parents=True, exist_ok=True)

# ── Style ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
})


# ============================================================================
# FIGURE 1: VAE Latent Space
# ============================================================================

def generate_vae_latent_space() -> None:
    """Plot P1 VAE latent space with high-MPO regions highlighted.

    Caption: "Position of the top-20 candidates in the Paper 1 VAE latent
    space, coloured by predicted MPO score."
    """
    mcmc_path = P1_ROOT / "p1_mcmc_generated.csv"
    if not mcmc_path.exists():
        print(f"WARNING: {mcmc_path} not found — skipping VAE latent space")
        return

    mcmc = pd.read_csv(mcmc_path)
    print(f"Loaded {len(mcmc)} MCMC-generated molecules with latent coords")

    # Build background: use all molecules as context
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

    # ── Panel (a): All molecules colored by MPO ──
    ax = axes[0]
    sc = ax.scatter(
        mcmc["latent_1"], mcmc["latent_2"],
        c=mcmc["mpo_predicted"], cmap="viridis",
        s=12, alpha=0.6, edgecolors="none",
    )
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8)
    cbar.set_label("Predicted MPO score")

    # Highlight top-20 by MPO
    top20 = mcmc.nlargest(20, "mpo_predicted")
    ax.scatter(
        top20["latent_1"], top20["latent_2"],
        s=60, edgecolors="red", facecolors="none", linewidths=1.5,
        zorder=5, label=f"Top-20 MPO (n={len(top20)})",
    )
    ax.set_xlabel("Latent dimension 1")
    ax.set_ylabel("Latent dimension 2")
    ax.set_title("(a) MCMC-generated molecules\ncoloured by MPO score")
    ax.legend(fontsize=7, loc="lower right")

    # ── Panel (b): Top-20 magnified with nearest-neighbour labels ──
    ax = axes[1]
    # Use all centroids as background
    ax.scatter(
        mcmc["latent_1"], mcmc["latent_2"],
        c="lightgrey", s=8, alpha=0.35, edgecolors="none",
    )
    # Plot top-20 with MPO colour
    sc2 = ax.scatter(
        top20["latent_1"], top20["latent_2"],
        c=top20["mpo_predicted"], cmap="viridis",
        s=80, edgecolors="black", linewidths=0.5, zorder=5,
    )
    for _, row in top20.iterrows():
        ax.annotate(
            f"{row['mpo_predicted']:.3f}",
            (row["latent_1"], row["latent_2"]),
            textcoords="offset points", xytext=(4, 4),
            fontsize=5, alpha=0.8,
        )
    ax.set_xlabel("Latent dimension 1")
    ax.set_title("(b) Top-20 by predicted MPO\n(values are MPO scores)")
    ax.set_xlim(ax.get_xlim())  # freeze view

    fig.suptitle(
        "Position of top-20 candidates in Paper 1 VAE latent space",
        fontsize=11, fontweight="bold", y=1.01,
    )
    fig.tight_layout()

    outpath = GRAPHICS_DIR / "VAE_latent_space.pdf"
    fig.savefig(outpath)
    plt.close(fig)
    print(f"  -> saved {outpath}")


# ============================================================================
# FIGURE 2: RRS Radar Profiles
# ============================================================================

def generate_rrs_radar_profiles() -> None:
    """Radar plots of per-compound RRS across six resistance mutations.

    Missing axes denote an ineligible target under the target-specific
    wild-type docking threshold; they are not imputed as zero.

    Caption: "Per-compound RRS profiles across six resistance mutations for
    the 17 Set-C candidates."
    """
    rrs_path = P2_RESULTS / "c_rrs_classification.csv"
    if not rrs_path.exists():
        print(f"WARNING: {rrs_path} not found — skipping RRS radar")
        return

    rrs = pd.read_csv(rrs_path)
    print(f"Loaded {len(rrs)} compounds with RRS classifications")

    # Six mutant-state columns; WT is a denominator, not a resistance state.
    # Missing values indicate an ineligible target and remain as gaps.
    mut_cols = ["RRS_N51I", "RRS_C59R", "RRS_S108N", "RRS_I164L",
                "RRS_K76T", "RRS_K76A"]
    mut_labels = ["N51I", "C59R", "S108N", "I164L", "K76T", "K76A"]

    # Verify columns exist
    missing = [c for c in mut_cols if c not in rrs.columns]
    if missing:
        print(f"ERROR: Missing RRS columns: {missing}")
        print(f"Available: {list(rrs.columns)}")
        return

    # Group by RRS class
    class_order = ["A*", "A", "B", "C", "D"]
    groups = {cls: rrs[rrs["RRS_class"] == cls] for cls in class_order}
    # Filter empty groups
    groups = {k: v for k, v in groups.items() if len(v) > 0}
    n_groups = len(groups)

    # Colors per class
    class_colors = {
        "A*": "#d62728",   # red
        "A": "#ff7f0e",    # orange
        "B": "#2ca02c",    # green
        "C": "#1f77b4",    # blue
        "D": "#9467bd",    # purple
    }

    n_mutations = len(mut_labels)
    angles = np.linspace(0, 2 * np.pi, n_mutations, endpoint=False).tolist()
    angles += angles[:1]  # close the circle

    fig, axes = plt.subplots(
        1, n_groups, figsize=(4.2 * n_groups, 5.2),
        subplot_kw={"projection": "polar"},
    )
    if n_groups == 1:
        axes = [axes]

    for ax, (cls_name, df) in zip(axes, groups.items()):
        color = class_colors.get(cls_name, "#333333")
        n_compounds = len(df)

        for _, row in df.iterrows():
            values = [row[c] for c in mut_cols]
            values += values[:1]  # close
            ax.plot(angles, values, "o-", linewidth=0.8, markersize=3,
                    color=color, alpha=0.7)

        # Reference rings
        ax.set_ylim(0, 200)
        ax.set_yticks([50, 100, 150])
        ax.set_yticklabels(["50%", "100%", "150%"], fontsize=6)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(mut_labels, fontsize=7)
        ax.set_title(
            f"Class {cls_name}\n(n = {n_compounds})",
            fontsize=9, fontweight="bold", color=color, pad=12,
        )
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        "RRS radar profiles across six resistance mutations\n"
        "(17 Set-C candidates; unavailable targets shown as gaps)",
        fontsize=11, fontweight="bold", y=1.02,
    )

    # Legend: compound details
    legend_text = "\n".join(
        [f"Class {cls}: {len(df)} compounds" for cls, df in groups.items()]
    )
    fig.text(0.02, 0.01, legend_text, fontsize=6, family="monospace",
             va="bottom", ha="left")

    fig.tight_layout()

    outpath = GRAPHICS_DIR / "rrs_radar_profiles.pdf"
    fig.savefig(outpath)
    plt.close(fig)
    print(f"  -> saved {outpath}")


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    print("=" * 60)
    print("Generating P2 Supplementary Material figures")
    print("=" * 60)

    generate_vae_latent_space()
    generate_rrs_radar_profiles()

    print("\nDone. Output directory:", GRAPHICS_DIR)
    print("Files:")
    for f in sorted(GRAPHICS_DIR.glob("*.pdf")):
        print(f"  {f.name}  ({f.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
