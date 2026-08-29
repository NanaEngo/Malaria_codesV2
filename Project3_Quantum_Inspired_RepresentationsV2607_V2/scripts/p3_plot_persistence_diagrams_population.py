"""
P3 — Population-scale persistence diagram figure (3-panel, publication quality).

Produces Figure 1 for Paper3_Quantum_InspiredV2607.tex matching the caption:
  Left  (H0): KDE of H0 mean persistence across all 19,849 molecules.
  Centre (H1): Hexbin density of per-molecule mean (birth, death) on LINEAR axes,
               coloured by median H1 persistence; orange circle = high-persistence
               ANP (top-20%), blue triangle = low-persistence molecule (bottom-10%).
  Right  (H2): Scatter of the N molecules (fraction%) with H2_count >= 1,
               sized by H2_count, coloured by mean H2 persistence.

Source data: results/p3_tda_fingerprints.csv
Output:      manuscript/LaTeX/Graphics/persistence_diagrams.png  (300 DPI)
             manuscript/LaTeX/Graphics/persistence_diagrams.pdf

Run from project root:
    python scripts/p3_plot_persistence_diagrams_population.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
TDA_CSV     = PROJECT_DIR / "results" / "p3_tda_fingerprints.csv"
OUT_PNG     = PROJECT_DIR / "manuscript" / "LaTeX" / "Graphics" / "persistence_diagrams.png"
OUT_PDF     = PROJECT_DIR / "manuscript" / "LaTeX" / "Graphics" / "persistence_diagrams.pdf"

# ── load data ───────────────────────────────────────────────────────────────
print(f"Loading {TDA_CSV} …", flush=True)
df = pd.read_csv(TDA_CSV)
N  = len(df)
print(f"  {N:,} molecules loaded.", flush=True)

# ── Okabe-Ito palette (colorblind-safe) ────────────────────────────────────
C_H0      = "#E69F00"   # warm orange
C_ANP_HI  = "#E69F00"   # high-persistence ANP marker (top-20%)
C_SYN_LO  = "#0072B2"   # low-persistence molecule (bottom-10%)

# ═══════════════════════════════════════════════════════════════════════════
# Figure layout — wider panels, less padding
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
ax0, ax1, ax2 = axes
fig.subplots_adjust(wspace=0.40)

# ═══════════════════════════════════════════════════════════════════════════
# Panel A — H0 KDE of mean persistence
# ═══════════════════════════════════════════════════════════════════════════
h0_mean = df["H0_mean_pers"].dropna().values
kde     = gaussian_kde(h0_mean, bw_method="scott")
x_grid  = np.linspace(h0_mean.min() * 0.97, h0_mean.max() * 1.02, 400)
med_h0  = np.median(h0_mean)

ax0.fill_between(x_grid, kde(x_grid), alpha=0.30, color=C_H0)
ax0.plot(x_grid, kde(x_grid), color=C_H0, lw=2.0)
ax0.axvline(med_h0, color="#555555", ls="--", lw=1.2,
            label=f"median = {med_h0:.2f} Å")
ax0.set_xlabel(r"Mean $H_0$ persistence (Å)", fontsize=10)
ax0.set_ylabel("Kernel density", fontsize=10)
ax0.set_title(r"$\mathbf{H_0}$ connected components", fontsize=11)
ax0.legend(fontsize=9, framealpha=0.7)
ax0.set_xlim(x_grid[0], x_grid[-1])
ax0.set_ylim(bottom=0)
ax0.tick_params(labelsize=9)
ax0.text(0.97, 0.95, "birth ≡ 0\n(by construction)",
         transform=ax0.transAxes, ha="right", va="top",
         fontsize=8, color="#666666",
         bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.8, ec="none"))
ax0.text(0.03, 0.97, f"N = {N:,}", transform=ax0.transAxes,
         va="top", fontsize=8.5, color="#333333")

# ═══════════════════════════════════════════════════════════════════════════
# Panel B — H1 hexbin, LINEAR axes
# ═══════════════════════════════════════════════════════════════════════════
h1_birth = df["H1_birth_mean"].values
h1_death = df["H1_death_mean"].values
h1_pers  = df["H1_mean_pers"].values

# All 19,849 molecules have valid H1; no filtering needed
pct80 = np.percentile(h1_pers, 80)
pct10 = np.percentile(h1_pers, 10)

# Pick representative from each group: molecule closest to group median
anp_mask = h1_pers >= pct80
syn_mask = h1_pers <= pct10
anp_idx  = np.where(anp_mask)[0]
syn_idx  = np.where(syn_mask)[0]
anp_rep  = anp_idx[np.argmin(np.abs(h1_pers[anp_idx] - np.median(h1_pers[anp_idx])))]
syn_rep  = syn_idx[np.argmin(np.abs(h1_pers[syn_idx] - np.median(h1_pers[syn_idx])))]
anp_pbar = h1_pers[anp_rep]
syn_pbar = h1_pers[syn_rep]

hb = ax1.hexbin(h1_birth, h1_death, C=h1_pers,
                gridsize=45, reduce_C_function=np.median,
                cmap="YlOrRd", linewidths=0.15, mincnt=1)

# Diagonal y = x
all_h1 = np.concatenate([h1_birth, h1_death])
h1_lo  = all_h1.min() * 0.97
h1_hi  = all_h1.max() * 1.02
ax1.plot([h1_lo, h1_hi], [h1_lo, h1_hi], "k--", lw=0.9, alpha=0.5)

# Exemplar markers — confirmed above diagonal (death > birth for all)
ax1.plot(h1_birth[anp_rep], h1_death[anp_rep], "o",
         color=C_ANP_HI, ms=9, mew=1.5, mec="black", zorder=5,
         label=fr"High-pers ANP ($\bar p={anp_pbar:.2f}$ Å, top 20%)")
ax1.plot(h1_birth[syn_rep], h1_death[syn_rep], "^",
         color=C_SYN_LO, ms=9, mew=1.5, mec="black", zorder=5,
         label=fr"Low-pers mol ($\bar p={syn_pbar:.2f}$ Å, bot. 10%)")

cb1 = fig.colorbar(hb, ax=ax1, pad=0.02, fraction=0.046)
cb1.set_label("Median $H_1$ persistence (Å)", fontsize=8.5)
cb1.ax.tick_params(labelsize=8)

ax1.set_xlabel(r"Mean $H_1$ birth (Å)", fontsize=10)
ax1.set_ylabel(r"Mean $H_1$ death (Å)", fontsize=10)
ax1.set_title(r"$\mathbf{H_1}$ rings/loops — hexbin density", fontsize=11)
ax1.legend(fontsize=8, framealpha=0.85, loc="upper left")
ax1.set_xlim(h1_lo, h1_hi)
ax1.set_ylim(h1_lo, h1_hi)
ax1.tick_params(labelsize=9)
ax1.text(0.97, 0.03, f"N = {N:,}", transform=ax1.transAxes,
         ha="right", va="bottom", fontsize=8.5, color="#333333")

# ═══════════════════════════════════════════════════════════════════════════
# Panel C — H2 scatter (molecules with at least one H2 feature)
# ═══════════════════════════════════════════════════════════════════════════
h2_mask  = df["H2_count"].fillna(0) >= 1
df_h2    = df[h2_mask].copy()
n_h2     = len(df_h2)
frac_h2  = 100.0 * n_h2 / N

h2_birth = df_h2["H2_birth_mean"].values
h2_death = df_h2["H2_death_mean"].values
h2_count = df_h2["H2_count"].values
h2_mpers = df_h2["H2_mean_pers"].values

# Marker size proportional to H2 count, capped for readability
sizes = np.clip(h2_count, 1, 8) * 14

sc = ax2.scatter(h2_birth, h2_death, c=h2_mpers, s=sizes,
                 cmap="YlOrRd", alpha=0.70, linewidths=0.3, edgecolors="grey")

# Diagonal
all_h2 = np.concatenate([h2_birth, h2_death])
h2_lo  = all_h2.min() * 0.97
h2_hi  = all_h2.max() * 1.02
ax2.plot([h2_lo, h2_hi], [h2_lo, h2_hi], "k--", lw=0.9, alpha=0.5)

cb2 = fig.colorbar(sc, ax=ax2, pad=0.02, fraction=0.046)
cb2.set_label("Mean $H_2$ persistence (Å)", fontsize=8.5)
cb2.ax.tick_params(labelsize=8)

# Size legend
for cnt, label in [(1, "1"), (3, "3"), (6, "≥ 6")]:
    ax2.scatter([], [], c="grey", alpha=0.65, s=np.clip(cnt, 1, 8) * 14,
                label=f"$H_2$ count = {label}", edgecolors="grey", linewidths=0.3)
ax2.legend(fontsize=8, framealpha=0.85, loc="lower right",
           title="$H_2$ count", title_fontsize=8.5)

ax2.set_xlabel(r"Mean $H_2$ birth (Å)", fontsize=10)
ax2.set_ylabel(r"Mean $H_2$ death (Å)", fontsize=10)
ax2.set_title(r"$\mathbf{H_2}$ cavities/voids — scatter", fontsize=11)
ax2.set_xlim(h2_lo, h2_hi)
ax2.set_ylim(h2_lo, h2_hi)
ax2.tick_params(labelsize=9)
ax2.text(0.03, 0.97, f"N = {n_h2:,} ({frac_h2:.1f}%)", transform=ax2.transAxes,
         va="top", fontsize=8.5, color="#333333")

# ═══════════════════════════════════════════════════════════════════════════
# Shared super-title
# ═══════════════════════════════════════════════════════════════════════════
fig.suptitle(
    "Vietoris–Rips persistence diagrams — 19,849-molecule ANP-space library\n"
    r"Points above the diagonal $y = x$ carry positive lifetime; "
    r"vertical distance from diagonal encodes persistence",
    fontsize=10, y=1.02
)

# ── save ────────────────────────────────────────────────────────────────────
for out_path in [OUT_PNG, OUT_PDF]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fmt = out_path.suffix.lstrip(".")
    fig.savefig(out_path, dpi=300, bbox_inches="tight", format=fmt)
    print(f"Saved: {out_path}  ({out_path.stat().st_size / 1024:.0f} KB)", flush=True)

print("Done.", flush=True)
