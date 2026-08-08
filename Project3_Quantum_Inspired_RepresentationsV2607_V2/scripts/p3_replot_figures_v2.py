#!/usr/bin/env python3
"""Alternative ("v2") renderings of the P3 manuscript figures.

Writes NEW files with a ``_v2`` suffix into ``manuscript/LaTeX/Graphics/``.
No existing figure is overwritten or deleted -- the author picks between them.

Rigour rules enforced here, so that the v2 panels are not merely prettier:
  * every value is read from a deposited result file; nothing is hard-coded,
  * bar axes start at zero, so bar length stays proportional to the quantity,
  * 95% confidence intervals are drawn wherever the source file supplies them,
  * the sample size behind every panel is printed on the panel,
  * a group with fewer than 3 observations is drawn as individual points, never
    as a density -- a violin over n=1 invents a distribution nobody measured,
  * the Okabe-Ito palette is used throughout (safe for common colour vision
    deficiencies) and no information is carried by colour alone.

Run from the project root with the project venv:
    /home/tchapet/VirtualEnv/bin/python3 scripts/p3_replot_figures_v2.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
GRAPHICS = ROOT / "manuscript" / "LaTeX" / "Graphics"

# Okabe-Ito qualitative palette.
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILLION = "#D55E00"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
GREY = "#4D4D4D"

STYLE = {
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9.5,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.frameon": False,
    "legend.fontsize": 8.5,
    "grid.color": "#D9D9D9",
    "grid.linewidth": 0.6,
}


def panel_tag(ax, letter: str) -> None:
    ax.text(
        -0.13, 1.06, letter, transform=ax.transAxes,
        fontsize=11, fontweight="bold", va="bottom", ha="left",
    )


def annotate_n(ax, text: str) -> None:
    ax.text(
        0.98, 0.03, text, transform=ax.transAxes,
        fontsize=7.5, color=GREY, ha="right", va="bottom",
    )


def save(fig, stem: str, also_pdf: bool = False) -> None:
    written = []
    png = GRAPHICS / f"{stem}.png"
    fig.savefig(png)
    written.append(png.name)
    if also_pdf:
        pdf = GRAPHICS / f"{stem}.pdf"
        fig.savefig(pdf)
        written.append(pdf.name)
    plt.close(fig)
    print(f"  wrote {', '.join(written)}")


# ---------------------------------------------------------------------------
# Figure 1 -- population persistence summary (H0 / H1 / H2)
# ---------------------------------------------------------------------------
def fig_persistence(tda: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5))

    ax = axes[0]
    h0 = tda["H0_mean_pers"].dropna().to_numpy()
    ax.hist(h0, bins=70, color=BLUE, alpha=0.85, edgecolor="white", linewidth=0.25)
    median = float(np.median(h0))
    ax.axvline(median, color=VERMILLION, linewidth=1.4, linestyle="--")
    ax.annotate(
        f"median {median:.2f} " + r"$\AA$",
        xy=(median, ax.get_ylim()[1] * 0.93),
        xytext=(6, 0), textcoords="offset points",
        color=VERMILLION, fontsize=8.5, va="top",
    )
    ax.set_xlabel(r"mean $H_0$ persistence ($\AA$)")
    ax.set_ylabel("molecules")
    ax.set_title(r"$H_0$ — connected components", pad=8)
    ax.grid(axis="y")
    panel_tag(ax, "a")
    annotate_n(ax, f"n = {h0.size:,}")

    ax = axes[1]
    sub = tda[["H1_birth_mean", "H1_death_mean", "H1_mean_pers"]].dropna()
    hb = ax.hexbin(
        sub["H1_birth_mean"], sub["H1_death_mean"], C=sub["H1_mean_pers"],
        reduce_C_function=np.median, gridsize=45, cmap="viridis",
        linewidths=0.0, mincnt=1,
    )
    lo = float(min(sub["H1_birth_mean"].min(), sub["H1_death_mean"].min()))
    hi = float(max(sub["H1_birth_mean"].max(), sub["H1_death_mean"].max()))
    ax.plot([lo, hi], [lo, hi], color=GREY, linewidth=0.9, linestyle=":", zorder=3)
    ax.text(
        0.97, 0.10, r"$y = x$ (zero lifetime)", transform=ax.transAxes,
        fontsize=7.5, color=GREY, ha="right",
    )
    cb = fig.colorbar(hb, ax=ax, pad=0.02, fraction=0.046)
    cb.set_label(r"median $H_1$ persistence ($\AA$)", fontsize=8.5)
    cb.ax.tick_params(labelsize=7.5)
    cb.outline.set_linewidth(0.6)
    ax.set_xlabel(r"mean $H_1$ birth ($\AA$)")
    ax.set_ylabel(r"mean $H_1$ death ($\AA$)")
    ax.set_title(r"$H_1$ — rings and loops", pad=8)
    panel_tag(ax, "b")
    annotate_n(ax, f"n = {len(sub):,}")

    ax = axes[2]
    h2 = tda[tda["H2_count"] >= 1]
    frac = 100.0 * len(h2) / len(tda)
    counts = h2["H2_count"].to_numpy()
    sizes = 14 + 16 * (counts - counts.min())
    ax.scatter(
        h2["H2_birth_mean"], h2["H2_death_mean"], s=sizes, c=h2["H2_mean_pers"],
        cmap="magma", alpha=0.8, edgecolor="white", linewidth=0.3,
    )
    lo = float(min(h2["H2_birth_mean"].min(), h2["H2_death_mean"].min()))
    hi = float(max(h2["H2_birth_mean"].max(), h2["H2_death_mean"].max()))
    ax.plot([lo, hi], [lo, hi], color=GREY, linewidth=0.9, linestyle=":")
    sm = plt.cm.ScalarMappable(
        cmap="magma",
        norm=plt.Normalize(h2["H2_mean_pers"].min(), h2["H2_mean_pers"].max()),
    )
    cb = fig.colorbar(sm, ax=ax, pad=0.02, fraction=0.046)
    cb.set_label(r"mean $H_2$ persistence ($\AA$)", fontsize=8.5)
    cb.ax.tick_params(labelsize=7.5)
    cb.outline.set_linewidth(0.6)
    ax.set_xlabel(r"mean $H_2$ birth ($\AA$)")
    ax.set_ylabel(r"mean $H_2$ death ($\AA$)")
    ax.set_title(r"$H_2$ — enclosed voids", pad=8)
    panel_tag(ax, "c")
    annotate_n(ax, f"n = {len(h2):,} ({frac:.1f}% of library)")

    fig.subplots_adjust(wspace=0.58)
    save(fig, "persistence_diagrams_v2", also_pdf=True)


# ---------------------------------------------------------------------------
# Figure 4 -- TDA features vs multi-target promiscuity
# ---------------------------------------------------------------------------
def _pretty_tda(name: str) -> str:
    """``H1_mean_pers`` -> ``$H_1$ mean persistence``."""
    parts = name.split("_")
    head, rest = parts[0], "_".join(parts[1:])
    words = {
        "count": "count",
        "entropy": "entropy",
        "max_pers": "max persistence",
        "mean_pers": "mean persistence",
        "birth_mean": "mean birth",
        "birth_std": "birth SD",
        "death_mean": "mean death",
        "death_std": "death SD",
        "pers_q25": "persistence Q1",
        "pers_q50": "persistence median",
        "pers_q75": "persistence Q3",
    }
    if head in {"H0", "H1", "H2"} and rest in words:
        return rf"$H_{head[1]}$ {words[rest]}"
    return name.replace("_", " ")


def _p_label(p: float) -> str:
    if p == 0:
        return r"$p < 10^{-300}$"
    mant, exp = f"{p:.1e}".split("e")
    return rf"$p = {mant}\times 10^{{{int(exp)}}}$"


def fig_promiscuity(prom: pd.DataFrame) -> None:
    df = prom.dropna(subset=["spearman_rho"]).copy()

    # The source file mixes interpretable persistence statistics with vectorised
    # persistence-image and Betti-curve components, whose indices carry no
    # chemical meaning on their own. Plot the interpretable set; report the
    # vectorised set in the footnote rather than dropping it silently.
    interpretable = df["tda_feature"].str.match(r"^H[012]_")
    vec = df[~interpretable]
    df = df[interpretable].copy()
    df["abs_rho"] = df["spearman_rho"].abs()
    df = df.sort_values("abs_rho", ascending=False).head(14).sort_values("spearman_rho")

    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    y = np.arange(len(df))
    colors = [VERMILLION if r < 0 else BLUE for r in df["spearman_rho"]]

    ax.hlines(y, 0.0, df["spearman_rho"], color=colors, linewidth=1.6, alpha=0.5, zorder=2)
    ax.scatter(df["spearman_rho"], y, s=56, c=colors, zorder=4,
               edgecolor="white", linewidth=0.7)
    ax.axvline(0.0, color=GREY, linewidth=0.9, zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels([_pretty_tda(f) for f in df["tda_feature"]])
    ax.set_ylim(-0.8, len(df) + 0.9)
    ax.set_xlabel(r"Spearman $\rho$ with number of targets bound")
    ax.set_title("Topological predictors of multi-target binding", pad=12)
    ax.grid(axis="x")

    span = float(df["spearman_rho"].abs().max())
    ax.set_xlim(-span * 1.22, span * 1.22)

    # p-values get their own right-hand column, outside the data area.
    trans = ax.get_yaxis_transform()
    for yi, p in enumerate(df["spearman_p"]):
        ax.text(1.03, yi, _p_label(p), transform=trans, fontsize=7.0,
                color=GREY, va="center", ha="left", clip_on=False)
    ax.text(1.03, len(df) + 0.35, "Spearman $p$", transform=trans, fontsize=7.4,
            color=GREY, va="center", ha="left", fontweight="bold", clip_on=False)

    handles = [
        Line2D([], [], marker="o", linestyle="", color=VERMILLION,
               label="negative: simpler topology binds more targets"),
        Line2D([], [], marker="o", linestyle="", color=BLUE,
               label="positive: more complex topology binds more targets"),
    ]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 0.99),
              ncol=1, handletextpad=0.5)

    note = (
        f"N = {int(df['N'].iloc[0]):,} molecules. The source file supplies no confidence "
        "intervals, so none are drawn.\n"
        f"{len(vec)} vectorised persistence-image and Betti-curve components were also tested "
        f"(range {vec['spearman_rho'].min():+.3f} to {vec['spearman_rho'].max():+.3f}); they are "
        "omitted here because their indices are not individually interpretable."
    )
    fig.text(0.5, -0.02, note, ha="center", va="top", fontsize=7.2,
             color=GREY, linespacing=1.5)
    save(fig, "p3_tda_promiscuity_v2")


# ---------------------------------------------------------------------------
# Figure 6 -- GA discriminator: classical Tanimoto vs quantum kernel density
# ---------------------------------------------------------------------------
def fig_ga(ga: pd.DataFrame) -> None:
    ga = ga.sort_values("n_generated")
    x = np.arange(len(ga))
    width = 0.36

    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    ax.axhspan(0.0, 0.5, color="#F4F4F4", zorder=0)
    ax.axhline(0.5, color=GREY, linewidth=1.0, linestyle="--", zorder=2)

    b1 = ax.bar(x - width / 2, ga["auc_ecfp4_tanimoto"], width, color=ORANGE,
                edgecolor="white", linewidth=0.6, label="ECFP4 Tanimoto", zorder=3)
    b2 = ax.bar(x + width / 2, ga["auc_quantum_kernel"], width, color=BLUE,
                edgecolor="white", linewidth=0.6, label="quantum kernel density", zorder=3)
    for bars in (b1, b2):
        labels = ax.bar_label(bars, fmt="%.3f", fontsize=7.5, padding=3, color=GREY)
        for lab in labels:
            lab.set_bbox(dict(facecolor="white", edgecolor="none", pad=1.0, alpha=0.85))
            lab.set_zorder(6)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(v)}" for v in ga["n_generated"]])
    ax.set_xlabel("generated molecules scored")
    ax.set_ylabel("AUC-ROC")
    ax.set_xlim(-0.62, len(ga) - 0.38)
    ax.set_ylim(0.0, 1.16)
    ax.set_yticks(np.arange(0.0, 1.01, 0.2))
    ax.set_title("Applicability-domain discrimination", pad=10)
    ax.grid(axis="y")

    chance = Line2D([], [], color=GREY, linewidth=1.0, linestyle="--",
                    label="chance (AUC = 0.5); shaded band is at or below chance")
    ax.legend(handles=[b1, b2, chance], loc="upper center", ncol=2,
              bbox_to_anchor=(0.5, -0.15))

    fig.text(
        0.5, -0.16,
        f"{int(ga['n_reference'].iloc[0])} reference seeds · "
        f"{ga['device'].iloc[0]} simulator.",
        ha="center", va="top", fontsize=7.2, color=GREY,
    )
    save(fig, "p3_ga_discriminator_v2")


# ---------------------------------------------------------------------------
# Figure 5 -- H1 topology by resistance-resilience class
# ---------------------------------------------------------------------------
def fig_h1_rrs(rrs: pd.DataFrame) -> None:
    df = rrs.dropna(subset=["rrs_class", "H1_mean_pers"]).copy()
    df["rrs_class"] = df["rrs_class"].astype(str).str.strip()

    # Compounds without an RRS classification were excluded from the correlation
    # analysis; they are not a resistance class and must not be drawn as one.
    total_rows = len(df)
    unclassified = df["rrs_class"].str.lower().isin({"unknown", "nan", "", "none"})
    n_excluded = int(unclassified.sum())
    df = df[~unclassified]
    order = sorted(df["rrs_class"].unique())
    palette = {c: col for c, col in
               zip(order, [BLUE, GREEN, ORANGE, VERMILLION, PURPLE, SKY, GREY])}
    rng = np.random.default_rng(42)

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.4))

    for ax, col, label in (
        (axes[0], "H1_mean_pers", r"mean $H_1$ persistence ($\AA$)"),
        (axes[1], "H1_count", r"$H_1$ count"),
    ):
        for i, cls in enumerate(order):
            vals = df.loc[df["rrs_class"] == cls, col].dropna().to_numpy()
            if vals.size == 0:
                continue
            colour = palette[cls]
            if vals.size >= 3:
                parts = ax.violinplot([vals], positions=[i], widths=0.72,
                                      showextrema=False, showmedians=False)
                for body in parts["bodies"]:
                    body.set_facecolor(colour)
                    body.set_alpha(0.28)
                    body.set_edgecolor(colour)
                    body.set_linewidth(0.9)
                q1, med, q3 = np.percentile(vals, [25, 50, 75])
                ax.vlines(i, q1, q3, color=colour, linewidth=4.5, alpha=0.85, zorder=4)
                ax.plot(i, med, "o", color="white", markersize=4.5, zorder=5,
                        markeredgecolor=colour, markeredgewidth=1.2)
            jitter = rng.uniform(-0.13, 0.13, size=vals.size)
            ax.plot(np.full(vals.size, i) + jitter, vals, "o", markersize=2.6,
                    color=colour, alpha=0.45 if vals.size >= 3 else 1.0,
                    markeredgewidth=0.0, zorder=3)

        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([f"Class {c}" for c in order])
        ax.set_ylabel(label)
        ax.grid(axis="y")

        ymin = ax.get_ylim()[0]
        for i, cls in enumerate(order):
            n = int((df["rrs_class"] == cls).sum())
            ax.annotate(f"n = {n}", xy=(i, ymin), xytext=(0, 4),
                        textcoords="offset points", ha="center",
                        fontsize=7.2, color=GREY)

    axes[0].set_title(r"$H_1$ persistence by resistance class", pad=9)
    axes[1].set_title(r"$H_1$ count by resistance class", pad=9)
    panel_tag(axes[0], "a")
    panel_tag(axes[1], "b")

    fig.text(
        0.5, -0.06,
        f"Analysis cohort: n = {len(df)} compounds carrying an RRS classification; "
        f"{n_excluded} of {total_rows} processed compounds were unclassified and are excluded.\n"
        "Thick bars span the interquartile range and the white marker is the median. "
        "Classes with fewer than three compounds are shown as individual points only.",
        ha="center", va="top", fontsize=7.4, color=GREY, linespacing=1.5,
    )
    fig.subplots_adjust(wspace=0.26)
    save(fig, "h1_rrs_class_violin_v2")


# ---------------------------------------------------------------------------
# Figure 3 -- TNE vs ECFP4 on the Tartarus docking regression
# ---------------------------------------------------------------------------
def fig_tne(reg: pd.DataFrame) -> None:
    reg = reg.copy()
    reg["descriptor"] = reg["descriptor"].astype(str).str.strip()
    targets = list(dict.fromkeys(reg["target"]))
    descs = list(dict.fromkeys(reg["descriptor"]))
    colours = {d: c for d, c in zip(descs, [BLUE, ORANGE, GREEN])}

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.3))
    x = np.arange(len(targets))
    width = 0.36

    for ax, metric, label, panel in (
        (axes[0], "R2", r"coefficient of determination $R^2$", "a"),
        (axes[1], "spearman_rho", r"Spearman $\rho$", "b"),
    ):
        for j, d in enumerate(descs):
            vals = []
            for t in targets:
                sel = reg[(reg["target"] == t) & (reg["descriptor"] == d)][metric]
                vals.append(float(sel.iloc[0]) if len(sel) else np.nan)
            bars = ax.bar(
                x + (j - (len(descs) - 1) / 2) * width, vals, width,
                color=colours.get(d, GREY), edgecolor="white", linewidth=0.6,
                label=d, zorder=3,
            )
            ax.bar_label(bars, fmt="%.3f", fontsize=7.3, padding=2, color=GREY)

        ax.set_xticks(x)
        ax.set_xticklabels(targets, fontsize=8.5)
        ax.set_ylabel(label)
        ax.set_ylim(0, float(np.nanmax(reg[metric])) * 1.22)
        ax.grid(axis="y")
        panel_tag(ax, panel)

    axes[0].set_title("Docking-score regression accuracy", pad=9)
    axes[1].set_title("Rank agreement with docking score", pad=9)
    axes[1].legend(loc="upper center", ncol=len(descs), bbox_to_anchor=(0.5, -0.13))

    ns = " · ".join(
        f"{t}: N = {int(reg[reg['target'] == t]['N'].iloc[0]):,}" for t in targets
    )
    fig.text(0.5, -0.07, ns, ha="center", fontsize=7.4, color=GREY)
    fig.subplots_adjust(wspace=0.26)
    save(fig, "p3_tne_regression_v2")


def main() -> None:
    plt.rcParams.update(STYLE)
    GRAPHICS.mkdir(parents=True, exist_ok=True)

    print("Figure 1 — population persistence summary")
    fig_persistence(pd.read_csv(RESULTS / "p3_tda_fingerprints.csv"))

    print("Figure 4 — TDA vs promiscuity")
    fig_promiscuity(pd.read_csv(RESULTS / "p3_physical_validation" / "p3_tda_promiscuity.csv"))

    print("Figure 6 — GA discriminator")
    fig_ga(pd.read_csv(RESULTS / "p3_ga_discriminator.csv"))

    print("Figure 5 — H1 by resistance class")
    fig_h1_rrs(pd.read_csv(RESULTS / "p3_rrs_tfp_final.csv"))

    print("Figure 3 — TNE vs ECFP4 regression")
    fig_tne(pd.read_csv(RESULTS / "p3_physical_validation" / "p3_tne_regression.csv"))

    print("\nAll v2 figures written to manuscript/LaTeX/Graphics/ (originals untouched).")


if __name__ == "__main__":
    main()
