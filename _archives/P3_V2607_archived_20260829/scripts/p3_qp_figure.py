#!/usr/bin/env python3
"""
Generate Figure SX: Quantum Parameter Optimization — canonical combo.

Reads results/p3_quantum_params_sweep.csv (+ phase-2 raw CSVs) and produces:
  - If a full grid is available (multiple bond_dim / n_repeats / n_kpca):
    3-panel heatmap (as before).
  - Otherwise (consolidated winner + phase-2 combos, current state):
    a focused bar chart of AUC by (bond_dim, n_repeats, n_kpca), highlighting
    the canonical winning combo (6, 1, 30) from BMAD v51 / Appendix K.

Outputs:
    results/figures/p3_qp_optimization_heatmap.png  (or combo bar chart)
    results/figures/p3_qp_optimization_table.csv    (best combos per dim)

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
FIG_DIR = PROJECT_DIR / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data (sweep CSV + any phase-2 raw combos) ─────────────────────
CSV_PATH = PROJECT_DIR / "results" / "p3_quantum_params_sweep.csv"
frames = []
if CSV_PATH.exists():
    frames.append(pd.read_csv(CSV_PATH))
for raw in sorted(PROJECT_DIR.glob("results/p3_phase2_*_raw.csv")):
    frames.append(pd.read_csv(raw))
df = pd.concat(frames, ignore_index=True)
df = df.drop_duplicates(subset=["bond_dim", "n_repeats", "n_kpca"])
df = df.sort_values("auc", ascending=False).reset_index(drop=True)

if df.empty:
    raise SystemExit("No quantum parameter sweep data found.")

CANONICAL = {"bond_dim": 6, "n_repeats": 1, "n_kpca": 30}

is_grid = (df["bond_dim"].nunique() > 1 and
           df["n_repeats"].nunique() > 1 and
           df["n_kpca"].nunique() > 1)

# ── Color mapping for grid mode ─────────────────────────────────────────
CMAP = "viridis"

if is_grid:
    BOND_DIMS = sorted(df["bond_dim"].unique())
    N_REPEATS = sorted(df["n_repeats"].unique())
    N_KPCA = sorted(df["n_kpca"].unique())
    VMAX = max(df["auc"].max() + 0.005, 0.86)
    VMIN = min(df["auc"].min(), 0.68)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)
    fig.suptitle(
        "Quantum Parameter Optimization — Hybrid Descriptor AUC (n=200, 5-fold CV)",
        fontsize=12, fontweight="bold", y=1.02
    )
    norm = mcolors.Normalize(vmin=VMIN, vmax=VMAX)

    for idx, bd in enumerate(BOND_DIMS):
        ax = axes[idx]
        sub = df[df["bond_dim"] == bd].pivot_table(
            index="n_kpca", columns="n_repeats", values="auc")
        sub = sub.reindex(index=N_KPCA, columns=N_REPEATS)
        im = ax.imshow(sub.values, cmap=CMAP, norm=norm, aspect="auto",
                       interpolation="nearest")
        for i in range(len(N_KPCA)):
            for j in range(len(N_REPEATS)):
                val = sub.values[i, j]
                if np.isnan(val):
                    ax.text(j, i, "⏳", ha="center", va="center",
                            fontsize=9, color="gray", fontweight="bold")
                else:
                    is_dark = val < (VMIN + VMAX) / 2
                    ax.text(j, i, f"{val:.4f}", ha="center", va="center",
                            fontsize=9, color="white" if is_dark else "black",
                            fontweight="bold")
        best = sub[~np.isnan(sub)].max().max()
        if not np.isnan(best):
            bi, bj = np.where(sub.values == best)[0][0], np.where(sub.values == best)[1][0]
            ax.add_patch(Rectangle((bj - 0.5, bi - 0.5), 1, 1, fill=False,
                                   edgecolor="gold", linewidth=3))
            ax.text(bj, bi - 0.35, "★", ha="center", va="center",
                    fontsize=16, color="gold", fontweight="bold")
        ax.set_xticks(range(len(N_REPEATS)))
        ax.set_xticklabels([str(nr) for nr in N_REPEATS])
        ax.set_yticks(range(len(N_KPCA)))
        ax.set_yticklabels([str(nk) for nk in N_KPCA])
        ax.set_title(f"bond_dim = {bd}", fontsize=11, fontweight="bold")
        ax.set_xlabel("n_repeats (IQP depth)", fontsize=9)
        if idx == 0:
            ax.set_ylabel("n_kpca (components)", fontsize=9)

    cbar = fig.colorbar(im, ax=axes, shrink=0.6, pad=0.02)
    cbar.set_label("Hybrid AUC (5-fold CV)", fontsize=9)
    output_path = FIG_DIR / "p3_qp_optimization_heatmap.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Saved (grid heatmap): {output_path}")

else:
    # Focused combo bar chart (current consolidated data)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    n = len(df)
    x = np.arange(n)
    aucs = df["auc"].values
    stds = df["auc_std"].fillna(0).values if "auc_std" in df.columns else np.zeros(n)

    # Highlight canonical winning combo (6, 1, 30)
    colors = []
    for _, row in df.iterrows():
        if (int(row["bond_dim"]) == CANONICAL["bond_dim"] and
                int(row["n_repeats"]) == CANONICAL["n_repeats"] and
                int(row["n_kpca"]) == CANONICAL["n_kpca"]):
            colors.append("#6A1B9A")
        else:
            colors.append("#B0BEC5")
    bars = ax.bar(x, aucs, 0.6, yerr=stds, color=colors, edgecolor="black",
                  linewidth=0.8, capsize=4)

    labels = [f"bd={int(r['bond_dim'])}/nr={int(r['n_repeats'])}/nk={int(r['n_kpca'])}"
              for _, r in df.iterrows()]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, rotation=20, ha="right")
    for bar, auc, std in zip(bars, aucs, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, auc + std + 0.005,
                f"{auc:.4f}±{std:.4f}", ha="center", va="bottom",
                fontsize=8, fontweight="bold")
    ax.axhline(y=0.5, color="red", linestyle="--", linewidth=0.8, alpha=0.6,
               label="Random (AUC=0.5)")
    ax.set_ylabel("Hybrid AUC (5-fold CV)", fontsize=11, fontweight="bold")
    ax.set_title("Quantum Parameter Optimization — Hybrid AUC\n"
                 "Canonical winning combo bd=6 / nr=1 / nk=30 highlighted "
                 "(BMAD v51)", fontsize=11, fontweight="bold", pad=10)
    ax.set_ylim(0.6, aucs.max() + 0.06)
    ax.legend(fontsize=9, loc="lower right", framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    plt.tight_layout()
    output_path = FIG_DIR / "p3_qp_optimization_heatmap.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Saved (combo bar): {output_path}")

# ── Save best-per-bond_dim table ────────────────────────────────────────
print("\nBEST PARAMETER COMBINATIONS PER BOND DIMENSION:")
best_per_dim = []
for bd in sorted(df["bond_dim"].unique()):
    sub = df[df["bond_dim"] == bd]
    best = sub.loc[sub["auc"].idxmax()]
    best_per_dim.append(best)
    print(f"  bd={int(best['bond_dim'])} | nr={int(best['n_repeats'])} | "
          f"nk={int(best['n_kpca'])} | AUC={best['auc']:.4f}")

table_path = FIG_DIR / "p3_qp_optimization_table.csv"
pd.DataFrame(best_per_dim).to_csv(table_path, index=False)
print(f"Saved table: {table_path}")

# ── Parameter effect plots (only meaningful with grid data) ─────────────
if df["n_repeats"].nunique() > 1 or df["n_kpca"].nunique() > 1:
    fig2, axes2 = plt.subplots(1, 3, figsize=(12, 3.5), constrained_layout=True)
    fig2.suptitle("Effect of Each Parameter on Hybrid AUC", fontsize=11,
                  fontweight="bold")
    for ai, (key, cmap) in enumerate([("bond_dim", "Reds"), ("n_repeats", "Blues"),
                                      ("n_kpca", "Greens")]):
        vals = sorted(df[key].unique())
        data = [df[df[key] == v]["auc"].dropna().values for v in vals]
        bp = axes2[ai].boxplot(data, tick_labels=[str(int(v)) for v in vals],
                               patch_artist=True, widths=0.5)
        for patch, c in zip(bp["boxes"], plt.cm.get_cmap(cmap)(np.linspace(0.3, 0.8, len(vals)))):
            patch.set_facecolor(c)
        axes2[ai].set_xlabel(key.replace("_", " "))
        axes2[ai].set_ylabel("AUC")
        axes2[ai].set_title(f"Effect of {key}", fontsize=10)
        axes2[ai].grid(axis="y", alpha=0.3)
    output_path2 = FIG_DIR / "p3_qp_parameter_effects.png"
    fig2.savefig(output_path2, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Saved effect plot: {output_path2}")

print("\nDone.")
