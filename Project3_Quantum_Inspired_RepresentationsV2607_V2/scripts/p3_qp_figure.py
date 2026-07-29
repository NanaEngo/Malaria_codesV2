#!/usr/bin/env python3
"""
Generate Figure SX: Quantum Parameter Optimization — AUC Heatmaps

Reads p3_quantum_params_sweep.csv and produces a 3-panel heatmap
(bond_dim=4, 6, 8) with n_repeats × n_kpca, colored by Hybrid AUC.

Output:
    results/figures/p3_qp_optimization_heatmap.png (300 DPI, SM-ready)
    results/figures/p3_qp_optimization_table.csv  (best combos per dim)

Usage:
    python scripts/p3_qp_figure.py
"""

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent.parent
CSV_PATH = PROJECT_DIR / "results" / "p3_quantum_params_sweep.csv"
FIG_DIR = PROJECT_DIR / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────
df = pd.read_csv(CSV_PATH)
BOND_DIMS = sorted(df["bond_dim"].unique())
N_REPEATS = sorted(df["n_repeats"].unique())
N_KPCA = sorted(df["n_kpca"].unique())

# ── Color mapping ──────────────────────────────────────────────────────
# Use a perceptually uniform colormap: viridis
# Range from min AUC to 0.86 (slightly above best observed)
CMAP = "viridis"
VMAX = max(df["auc"].max() + 0.005, 0.86)
VMIN = min(df["auc"].min(), 0.68)

def format_auc(val):
    """Format AUC value for annotation."""
    return f"{val:.4f}"

# ── Create figure ──────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)
fig.suptitle(
    "Quantum Parameter Optimization — Hybrid Descriptor AUC (n=200, 5-fold CV)",
    fontsize=12, fontweight="bold", y=1.02
)

norm = mcolors.Normalize(vmin=VMIN, vmax=VMAX)

for idx, bd in enumerate(BOND_DIMS):
    ax = axes[idx]
    sub = df[df["bond_dim"] == bd].pivot_table(
        index="n_kpca", columns="n_repeats", values="auc"
    )
    # Ensure full grid (fill missing with NaN)
    sub = sub.reindex(index=N_KPCA, columns=N_REPEATS)

    # Heatmap
    im = ax.imshow(sub.values, cmap=CMAP, norm=norm, aspect="auto",
                   interpolation="nearest")

    # Annotate each cell
    for i in range(len(N_KPCA)):
        for j in range(len(N_REPEATS)):
            val = sub.values[i, j]
            if np.isnan(val):
                ax.text(j, i, "⏳", ha="center", va="center",
                        fontsize=9, color="gray", fontweight="bold")
            else:
                txt = f"{val:.4f}"
                # White text on dark cells, black on light
                is_dark = val < (VMIN + VMAX) / 2
                ax.text(j, i, txt, ha="center", va="center",
                        fontsize=9, color="white" if is_dark else "black",
                        fontweight="bold")

    # Highlight best cell
    best = sub[~np.isnan(sub)].max().max()
    if not np.isnan(best):
        best_pos = np.where(sub.values == best)
        if len(best_pos[0]) > 0:
            bi, bj = best_pos[0][0], best_pos[1][0]
            # Draw a prominent golden border around the best cell
            rect = Rectangle(
                (bj - 0.5, bi - 0.5), 1, 1,
                fill=False, edgecolor="gold", linewidth=3, linestyle="-"
            )
            ax.add_patch(rect)
            # Star marker
            ax.text(bj, bi - 0.35, "★", ha="center", va="center",
                    fontsize=16, color="gold", fontweight="bold")

    # Axis labels
    ax.set_xticks(range(len(N_REPEATS)))
    ax.set_xticklabels([str(nr) for nr in N_REPEATS])
    ax.set_yticks(range(len(N_KPCA)))
    ax.set_yticklabels([str(nk) for nk in N_KPCA])

    ax.set_title(f"bond_dim = {bd}", fontsize=11, fontweight="bold")
    ax.set_xlabel("n_repeats (IQP depth)", fontsize=9)
    if idx == 0:
        ax.set_ylabel("n_kpca (components)", fontsize=9)

    # Subtitle with best value
    if not np.isnan(best):
        best_row = sub[sub == best].stack().reset_index().iloc[0]
        ax.text(
            0.5, -0.18, f"Best AUC = {best:.4f} (nr={int(best_row['n_repeats'])}, "
                         f"nk={int(best_row['n_kpca'])})",
            transform=ax.transAxes, ha="center", fontsize=8,
            fontstyle="italic", color="goldenrod"
        )

# Colorbar
cbar = fig.colorbar(im, ax=axes, shrink=0.6, pad=0.02)
cbar.set_label("Hybrid AUC (5-fold CV)", fontsize=9)
cbar.ax.tick_params(labelsize=8)

# ── Save ───────────────────────────────────────────────────────────────
output_path = FIG_DIR / "p3_qp_optimization_heatmap.png"
fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
print(f"✅ Figure saved: {output_path}")

# ── Also save best-per-bond_dim table ──────────────────────────────────
print("\n🏆  BEST PARAMETER COMBINATIONS PER BOND DIMENSION:")
print(f"  {'bond_dim':>8} | {'n_repeats':>9} | {'n_kpca':>5} | {'AUC':>6} | {'AUC_std':>7}")
print("  " + "-" * 50)
best_per_dim = []
for bd in BOND_DIMS:
    sub = df[df["bond_dim"] == bd]
    best = sub.loc[sub["auc"].idxmax()]
    best_per_dim.append(best)
    print(f"  {int(best['bond_dim']):>8} | {int(best['n_repeats']):>9} | "
          f"{int(best['n_kpca']):>5} | {best['auc']:.4f} | {best['auc_std']:.4f}")

# Global best
global_best = df.loc[df["auc"].idxmax()]
print(f"\n🏆  GLOBAL BEST:")
print(f"     bond_dim  = {int(global_best['bond_dim'])}")
print(f"     n_repeats = {int(global_best['n_repeats'])}")
print(f"     n_kpca    = {int(global_best['n_kpca'])}")
print(f"     AUC       = {global_best['auc']:.4f} ± {global_best['auc_std']:.4f}")

# Save table
table_path = FIG_DIR / "p3_qp_optimization_table.csv"
best_table = pd.DataFrame(best_per_dim)
best_table.to_csv(table_path, index=False)
print(f"✅ Best-per-dim table saved: {table_path}")

# ── Additional analysis: effect plots ──────────────────────────────────
fig2, axes2 = plt.subplots(1, 3, figsize=(12, 3.5), constrained_layout=True)
fig2.suptitle("Effect of Each Parameter on Hybrid AUC", fontsize=11, fontweight="bold")

# Boxplot by bond_dim
bp_data = [df[df["bond_dim"] == bd]["auc"].dropna().values for bd in BOND_DIMS]
bp1 = axes2[0].boxplot(bp_data, tick_labels=[f"bd={int(bd)}" for bd in BOND_DIMS],
                        patch_artist=True, widths=0.5)
for patch, color in zip(bp1["boxes"], ["#ff9999", "#66b3ff", "#99ff99"]):
    patch.set_facecolor(color)
axes2[0].set_xlabel("Bond Dimension (UMAP dim)")
axes2[0].set_ylabel("AUC")
axes2[0].set_title("Effect of bond_dim", fontsize=10)
axes2[0].grid(axis="y", alpha=0.3)

# Boxplot by n_repeats
nr_unique = sorted(df["n_repeats"].unique())
nr_data = [df[df["n_repeats"] == nr]["auc"].dropna().values for nr in nr_unique]
bp2 = axes2[1].boxplot(nr_data, tick_labels=[str(int(nr)) for nr in nr_unique],
                        patch_artist=True, widths=0.5)
colors_nr = plt.cm.Blues(np.linspace(0.3, 0.8, len(nr_unique)))
for patch, color in zip(bp2["boxes"], colors_nr):
    patch.set_facecolor(color)
axes2[1].set_xlabel("n_repeats (IQP depth)")
axes2[1].set_ylabel("AUC")
axes2[1].set_title("Effect of n_repeats", fontsize=10)
axes2[1].grid(axis="y", alpha=0.3)

# Boxplot by n_kpca
nk_unique = sorted(df["n_kpca"].unique())
nk_data = [df[df["n_kpca"] == nk]["auc"].dropna().values for nk in nk_unique]
bp3 = axes2[2].boxplot(nk_data, tick_labels=[str(int(nk)) for nk in nk_unique],
                        patch_artist=True, widths=0.5)
colors_nk = plt.cm.Greens(np.linspace(0.3, 0.8, len(nk_unique)))
for patch, color in zip(bp3["boxes"], colors_nk):
    patch.set_facecolor(color)
axes2[2].set_xlabel("n_kpca (components)")
axes2[2].set_ylabel("AUC")
axes2[2].set_title("Effect of n_kpca", fontsize=10)
axes2[2].grid(axis="y", alpha=0.3)

output_path2 = FIG_DIR / "p3_qp_parameter_effects.png"
fig2.savefig(output_path2, dpi=300, bbox_inches="tight", facecolor="white")
print(f"✅ Effect plot saved: {output_path2}")

print("\nDone.")
