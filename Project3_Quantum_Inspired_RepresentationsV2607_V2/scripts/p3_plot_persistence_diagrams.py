#!/usr/bin/env python3
"""
p3_plot_persistence_diagrams.py
================================
Plot Figure 1 — Vietoris-Rips persistence diagrams for Paper 3.

Data source: results/p3_tda_fingerprints.csv (19,849 molecules).
Authoritative statistics: BMAD_Q1_DATA_ANALYSIS_REPORT.md §3.1.

Panel layout:
  H0 — KDE of mean persistence (birth ≡ 0 for connected components)
  H1 — Hexbin density on log-log birth-death axes, coloured by log persistence
  H2 — Scatter of the 3 % of molecules that carry H2 features

Outputs:
  manuscript/LaTeX/Graphics/persistence_diagrams.pdf
  results/figures/persistence_diagrams.png
"""

from __future__ import annotations
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_DIR  = Path(__file__).resolve().parent.parent
TFP_CSV      = PROJECT_DIR / "results" / "p3_tda_fingerprints.csv"
FIGURES_DIR  = PROJECT_DIR / "results" / "figures"
GRAPHICS_DIR = PROJECT_DIR / "manuscript" / "LaTeX" / "Graphics"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":         9,
    "axes.titlesize":   10,
    "axes.labelsize":    9,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
    "legend.fontsize":   8,
})

ANP_COLOR = "#D95F02"
SYN_COLOR = "#1B7BC4"
DIAG_KW   = dict(color="#AAAAAA", lw=0.9, ls="--", zorder=1)
QLINE_KW  = dict(lw=0.9, zorder=2)

# ── Load & prepare ─────────────────────────────────────────────────────────────
print("Loading TDA fingerprints …")
df = pd.read_csv(TFP_CSV)
print(f"  {len(df):,} rows")

# H0 — persistence = death (birth ≡ 0)
h0_mp  = df["H0_mean_pers"].dropna().values
h0_max = df["H0_max_pers"].dropna().values

# H1 — keep only rows where death > birth (geometrically required)
h1 = df[["H1_birth_mean", "H1_death_mean", "H1_mean_pers"]].dropna()
h1 = h1[h1["H1_death_mean"] > h1["H1_birth_mean"]].copy()

# Representative points: drawn directly from CSV (same coordinate system)
# Use 80th-percentile for ANP so the point sits near — but visibly above — the cloud
anp_thresh = h1["H1_mean_pers"].quantile(0.80)
syn_thresh = h1["H1_mean_pers"].quantile(0.10)
anp_row = h1[h1["H1_mean_pers"] >= anp_thresh].sort_values("H1_mean_pers").iloc[len(h1[h1["H1_mean_pers"] >= anp_thresh])//2]
syn_row = h1[h1["H1_mean_pers"] <= syn_thresh].sort_values("H1_mean_pers").iloc[0]

# H2 — sparse: only ~3 % of library
h2 = df[df["H2_count"] > 0][["H2_birth_mean","H2_death_mean","H2_mean_pers","H2_count"]].dropna()
h2 = h2[h2["H2_death_mean"] > h2["H2_birth_mean"]].copy()
pct_h2 = 100 * len(h2) / len(df)
print(f"  H2 molecules: {len(h2):,} ({pct_h2:.1f} %)")

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
fig.subplots_adjust(wspace=0.44, left=0.07, right=0.97, top=0.91, bottom=0.13)

# ═══ Panel A — H0 KDE ═════════════════════════════════════════════════════════
ax = axes[0]

x_lo, x_hi = h0_mp.min() * 0.97, h0_mp.max() * 1.03
y_grid = np.linspace(x_lo, x_hi, 500)

kde_mp  = gaussian_kde(h0_mp,  bw_method=0.12)
kde_max = gaussian_kde(h0_max, bw_method=0.12)
dens_mp  = kde_mp(y_grid)
dens_max = kde_max(y_grid)

ax.fill_betweenx(y_grid, dens_mp,  alpha=0.30, color="#4C78A8")
ax.plot(dens_mp,  y_grid, color="#4C78A8", lw=1.6, label="Mean persistence")
ax.plot(dens_max, y_grid, color="#72B7B2", lw=1.2, ls="--", alpha=0.9, label="Max persistence")

# Quartile horizontal lines with inside labels
q_vals = {
    "Q1":  np.quantile(h0_mp, 0.25),
    "Med": np.quantile(h0_mp, 0.50),
    "Q3":  np.quantile(h0_mp, 0.75),
}
q_styles = {"Q1": (":", "#777"), "Med": ("-", "#444"), "Q3": (":", "#777")}
for name, val in q_vals.items():
    ls, col = q_styles[name]
    ax.axhline(val, color=col, lw=0.9, ls=ls, **{"zorder": 2})
    ax.text(1.01, val, f"{name} {val:.2f}",
            transform=ax.get_yaxis_transform(),   # y in data, x in axes fraction
            ha="left", va="center", fontsize=9, color=col)

ax.set_xlabel("Density", labelpad=3)
ax.set_ylabel("Persistence (weighted units)", labelpad=3)
ax.set_title(r"$H_0$ (Connected Components)", pad=6, fontweight="bold")
ax.set_ylim(x_lo, x_hi)
ax.set_xlim(left=0)
ax.xaxis.set_major_locator(mticker.MaxNLocator(5))
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
ax.legend(loc="lower right", framealpha=0.8, edgecolor="#ccc", handlelength=1.8)
ax.text(0.03, 0.97, f"N = {len(h0_mp):,}\nBirth ≡ 0",
        transform=ax.transAxes, va="top", fontsize=7.5,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.85))

# ═══ Panel B — H1 hexbin ══════════════════════════════════════════════════════
ax = axes[1]

b = h1["H1_birth_mean"].values
d = h1["H1_death_mean"].values
p = h1["H1_mean_pers"].values

hb = ax.hexbin(
    b, d,
    C=np.log10(p),
    reduce_C_function=np.median,
    gridsize=36,
    xscale="log", yscale="log",
    cmap="viridis",
    mincnt=1,
    linewidths=0.12,
    vmin=np.log10(p.min()),
    vmax=np.log10(p.max()),
)

# Diagonal — extend axis limits generously to avoid tick crowding
lim_lo = min(b.min(), d.min()) * 0.75
lim_hi = max(b.max(), d.max()) * 1.35
diag_v = np.logspace(np.log10(lim_lo), np.log10(lim_hi), 300)
ax.plot(diag_v, diag_v, **DIAG_KW)
ax.set_xlim(lim_lo, lim_hi)
ax.set_ylim(lim_lo, lim_hi)

# Representative points — both verified above diagonal
ax.scatter(anp_row.H1_birth_mean, anp_row.H1_death_mean,
           color=ANP_COLOR, s=70, marker="o", zorder=6,
           edgecolors="white", lw=0.7,
           label=f"High-H₁ ANP  (pers={anp_row.H1_mean_pers:.2f})")
ax.scatter(syn_row.H1_birth_mean, syn_row.H1_death_mean,
           color=SYN_COLOR, s=70, marker="^", zorder=6,
           edgecolors="white", lw=0.7,
           label=f"Low-H₁ synthetic-like  (pers={syn_row.H1_mean_pers:.2f})")

ax.set_xlabel("Birth (weighted units, log scale)", labelpad=3)
ax.set_ylabel("Death (weighted units, log scale)", labelpad=3)
ax.set_title(r"$H_1$ (Rings / Loops)", pad=6, fontweight="bold")
ax.tick_params(which="both", direction="in", top=True, right=True)
# Explicit clean tick positions within the 0.75–7 range to avoid crowding
clean_ticks = [1, 2, 3, 5]
ax.set_xticks(clean_ticks)
ax.set_yticks(clean_ticks)
ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
ax.xaxis.set_minor_locator(mticker.NullLocator())
ax.yaxis.set_minor_locator(mticker.NullLocator())
ax.legend(loc="upper left", framealpha=0.85, edgecolor="#ccc",
          handletextpad=0.4, borderpad=0.5)

div1 = make_axes_locatable(ax)
cax1 = div1.append_axes("right", size="4%", pad=0.06)
cb1  = fig.colorbar(hb, cax=cax1)
cb1.set_label("log₁₀(median pers.)", fontsize=7, labelpad=4)
cb1.ax.tick_params(labelsize=6)

ax.text(0.97, 0.03, f"N = {len(h1):,}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.85))

# ═══ Panel C — H2 scatter ═════════════════════════════════════════════════════
ax = axes[2]

sc = ax.scatter(
    h2["H2_birth_mean"], h2["H2_death_mean"],
    c=h2["H2_mean_pers"], cmap="plasma",
    s=np.clip(h2["H2_count"] * 14, 10, 70),
    alpha=0.55, linewidths=0.2, edgecolors="white", zorder=3,
)

b2 = h2["H2_birth_mean"].values
d2 = h2["H2_death_mean"].values
lo2 = min(b2.min(), d2.min()) * 0.88
hi2 = max(b2.max(), d2.max()) * 1.12
ax.plot([lo2, hi2], [lo2, hi2], **DIAG_KW)
ax.set_xlim(lo2, hi2)
ax.set_ylim(lo2, hi2)

ax.set_xlabel("Birth (weighted units)", labelpad=3)
ax.set_ylabel("Death (weighted units)", labelpad=3)
ax.set_title(r"$H_2$ (Cavities / Voids)", pad=6, fontweight="bold")
ax.tick_params(which="both", direction="in", top=True, right=True)

div2 = make_axes_locatable(ax)
cax2 = div2.append_axes("right", size="4%", pad=0.06)
cb2  = fig.colorbar(sc, cax=cax2)
cb2.set_label("Mean H₂ persistence", fontsize=7, labelpad=4)
cb2.ax.tick_params(labelsize=6)

# Size legend — separate from count annotation
for cnt, lab in [(1, "1"), (2, "2"), (4, "≥ 4")]:
    ax.scatter([], [], s=np.clip(cnt*14, 10, 70), color="#888",
               alpha=0.6, label=lab, edgecolors="white", lw=0.2)
ax.legend(title="H₂ count", title_fontsize=7.5, fontsize=7,
          loc="upper left", framealpha=0.85, edgecolor="#ccc")

ax.text(0.97, 0.03,
        f"N = {len(h2):,} / {len(df):,}  ({pct_h2:.1f} %)",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.85))

# ── Save ───────────────────────────────────────────────────────────────────────
out_pdf = GRAPHICS_DIR / "persistence_diagrams.pdf"
out_png = FIGURES_DIR  / "persistence_diagrams.png"
fig.savefig(out_pdf, dpi=300, bbox_inches="tight")
fig.savefig(out_png, dpi=300, bbox_inches="tight")
print(f"Saved → {out_pdf}")
print(f"Saved → {out_png}")
plt.close(fig)
print("Done.")
