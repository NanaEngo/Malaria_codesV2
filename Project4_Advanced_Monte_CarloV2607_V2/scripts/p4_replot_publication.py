#!/usr/bin/env python3
"""Regenerate the P4 manuscript figures at publication quality.

Every figure is rebuilt from the deposited result files; no value is recomputed,
smoothed, filtered or rescaled. The only changes are visual: Okabe-Ito colours
with redundant marker encoding, explicit uncertainty definitions, raw per-seed
observations where they exist, and 600 dpi raster plus vector sidecar output.

The graphical abstract is deliberately NOT regenerated here.

2026-08-17 layout fixes, after inspecting the six figures at final printed size. All
four are rendering-only: no plotted value, axis range, statistic or caption changes.

  * rrs_pns_profile       method names wrapped over two lines in both panels -- at
                          170 mm across two panels the single-line forms printed
                          "MCTS+ScafVAE" and "Genetic algorithm" as one string.
  * scaffold_diversity    legend lifted above the axes in two columns and the
                          provenance footer given an opaque background -- the legend
                          was drawn inside the data region over the markers and the
                          footer overprinted its fourth entry.
  * p4_evidence_overview  the P1 label is offset leftwards and drawn above the
                          markers -- in the narrow panel B it fell behind the P2
                          marker, so P1 was plotted but unlabelled while P2, P3 and
                          P4 were labelled, inconsistent with pareto_front.
  * benchmark_efficiency  explicit decade and half-decade x ticks -- Greedy (1.9 s)
                          and GA (2.0 s) sat left of the first labelled logarithmic
                          tick with no minor-tick labels, so their wall-clock values
                          could not be read off the axis.

Second pass, same day, after inspecting the re-rendered files: lifting the
scaffold_diversity legend left its provenance footer sitting on the lowest MCTS marker,
which the footer's opaque background then masked. A blank band is now reserved below the
point cloud. This widens the y limits into empty space only -- no coordinate is rescaled.

Sources
-------
results/benchmark_molecules_opt_v12/p4_benchmark_merged.csv  method,seed,reward,elapsed_s
results/pareto/merged_pareto_front.csv                       smiles,mpo,syba,sa,rrs,pns,...
results/pareto/p4_multiobj_benchmark.csv                     method,seed,smiles,mpo,syba,sa,rrs,pns
results/diversity/p4_diversity_mds.csv                       method,seed,smiles,mds_x,mds_y
results/diversity/p4_diversity_metrics.csv                   per-method diversity summary
results/ablation/p4_component_ablation_summary.csv           factor,level,mean_reward,std_reward,n

Usage:  python scripts/p4_replot_publication.py
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

P4_ROOT = Path(os.environ.get("P4_ROOT", Path(__file__).resolve().parents[1]))
RESULTS = P4_ROOT / "results"
OUT = P4_ROOT / "manuscript" / "LaTeX" / "Graphics"

MM = 1 / 25.4

# Okabe-Ito, colour-blind safe. Colour is never the only channel: every method
# also carries a distinct marker and, in bar-like panels, a distinct hatch.
C = {
    "random": "#0072B2",   # blue
    "mcts":   "#D55E00",   # vermillion
    "ga":     "#009E73",   # bluish green
    "greedy": "#CC79A7",   # reddish purple
}
MK = {"random": "o", "mcts": "s", "ga": "^", "greedy": "D"}
HATCH = {"random": "", "mcts": "//", "ga": "\\\\", "greedy": ".."}
LABEL = {
    "random": "Random",
    "mcts": "MCTS+ScafVAE",
    "ga": "Genetic algorithm",
    "greedy": "Greedy",
}
ORDER = ["random", "mcts", "ga", "greedy"]

# Two-line method names for the narrow multi-panel axes. At 170 mm across two panels
# the single-line forms of "MCTS+ScafVAE" and "Genetic algorithm" print as one string.
LABEL_WRAP = {
    "random": "Random",
    "mcts": "MCTS+\nScafVAE",
    "ga": "Genetic\nalgorithm",
    "greedy": "Greedy",
}

# Label placement per front candidate. P1 and P2 share SYBA = 1.000 and differ by only
# 0.035 in MPO, so P1's label is pushed leftwards to clear the P2 marker.
LAB_OFFSET = {
    "P1": (-8, -3, "right"),
    "P2": (8, -3, "left"),
    "P3": (8, -3, "left"),
    "P4": (8, -3, "left"),
}

RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "axes.titleweight": "bold",
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "lines.linewidth": 1.0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}


def save(fig, stem: str) -> None:
    """Write 600 dpi PNG (referenced by the manuscript) plus a vector sidecar."""
    OUT.mkdir(parents=True, exist_ok=True)
    # transparent=False keeps an opaque white ground: an alpha channel changes
    # apparent contrast when composited and is rejected by some publishers.
    fig.savefig(OUT / f"{stem}.png", dpi=600, transparent=False,
                facecolor="white", edgecolor="none")
    fig.savefig(OUT / f"{stem}.pdf", transparent=False,
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"  wrote {stem}.png / .pdf")


def _mnum(v: float) -> str:
    """Four-decimal mathtext number whose minus is unary.

    Bare "$-0.0075$" is parsed as a binary operator and printed with the wider
    surrounding space, which reads as "- 0.0075". Bracing the sign makes it ordinary.
    """
    return f"{{-}}{abs(v):.4f}" if v < 0 else f"{v:.4f}"


def load_bench() -> pd.DataFrame:
    return pd.read_csv(RESULTS / "benchmark_molecules_opt_v12" / "p4_benchmark_merged.csv")


def summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("method")["reward"]
    out = pd.DataFrame({"mean": g.mean(), "sd": g.std(ddof=1), "n": g.size()})
    out["time"] = df.groupby("method")["elapsed_s"].mean()
    return out


# ---------------------------------------------------------------- figure 1
def fig_benchmark_bar(df: pd.DataFrame) -> None:
    """Mean reward per method, with all 20 per-seed observations shown."""
    s = summary(df)
    fig, ax = plt.subplots(figsize=(140 * MM, 78 * MM), layout="constrained")
    rng = np.random.default_rng(20260815)

    for i, m in enumerate(ORDER):
        sub = df[df.method == m]["reward"].to_numpy()
        ax.errorbar(i, s.loc[m, "mean"], yerr=s.loc[m, "sd"], fmt=MK[m],
                    color=C[m], markersize=6, capsize=4, elinewidth=1.1,
                    markeredgecolor="black", markeredgewidth=0.5, zorder=3)
        jit = rng.uniform(-0.13, 0.13, sub.size)
        ax.scatter(i + jit, sub, s=7, color=C[m], alpha=0.40,
                   edgecolors="none", zorder=2)

    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels([LABEL[m] for m in ORDER])
    ax.set_ylabel("Best scalar reward per seed")
    ax.set_ylim(0.40, 0.72)
    ax.grid(axis="y", alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)

    # Significance brackets: p-values exactly as reported in the manuscript.
    def bracket(i, j, y, text):
        ax.plot([i, i, j, j], [y, y + 0.006, y + 0.006, y], lw=0.7, c="black")
        ax.text((i + j) / 2, y + 0.008, text, ha="center", va="bottom", fontsize=6.5)

    bracket(0, 1, 0.694, "$p = 0.000085$")
    bracket(1, 2, 0.676, "$p < 0.0001$")

    ax.text(0.985, 0.03, "points: per-seed values ($n = 20$); markers: mean $\\pm$ 1 SD",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color="0.35")
    save(fig, "benchmark_reward_bar")


# ---------------------------------------------------------------- figure 2
def fig_efficiency(df: pd.DataFrame) -> None:
    """Reward against wall-clock cost."""
    s = summary(df)
    fig, ax = plt.subplots(figsize=(120 * MM, 80 * MM), layout="constrained")
    for m in ORDER:
        ax.errorbar(s.loc[m, "time"], s.loc[m, "mean"], yerr=s.loc[m, "sd"],
                    fmt=MK[m], color=C[m], markersize=8, capsize=4,
                    elinewidth=1.1, markeredgecolor="black", markeredgewidth=0.5,
                    label=LABEL[m], zorder=3)
        ax.annotate(LABEL[m], xy=(s.loc[m, "time"], s.loc[m, "mean"]),
                    xytext=(6, 6), textcoords="offset points", fontsize=6.5)
    ax.set_xlabel("Mean wall-clock time per seed (s)")
    ax.set_ylabel("Mean best scalar reward")
    ax.set_xscale("log")
    ax.set_xlim(1.2, 160)
    # Greedy (1.9 s) and GA (2.0 s) fall left of the 10^1 decade tick, so the default
    # LogLocator leaves them with no labelled reference. Label decades and half-decades
    # explicitly and suppress the unlabelled minor ticks.
    ax.set_xticks([2, 5, 10, 20, 50, 100])
    ax.set_xticklabels(["2", "5", "10", "20", "50", "100"])
    ax.set_xticks([], minor=True)
    ax.grid(alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)
    ax.text(0.985, 0.03, "error bars: 1 SD over 20 seeds; $x$ on a log scale",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color="0.35")
    save(fig, "benchmark_efficiency")


# ---------------------------------------------------------------- figure 3
def _pareto_axes(ax, front: pd.DataFrame, legend: bool = True):
    """MPO vs SYBA; colour = RRS proxy, marker shape = PNS proxy."""
    norm = mpl.colors.Normalize(vmin=front.rrs.min(), vmax=front.rrs.max())
    cmap = mpl.colormaps["viridis"]
    labels = ["P1", "P2", "P3", "P4"]
    for (_, r), lab in zip(front.iterrows(), labels):
        mk = "o" if r.pns >= 0.5 else "^"
        ax.scatter(r.mpo, r.syba, s=110, marker=mk, color=cmap(norm(r.rrs)),
                   edgecolors="black", linewidths=0.7, zorder=3)
        dx, dy, ha = LAB_OFFSET[lab]
        ax.annotate(lab, xy=(r.mpo, r.syba), xytext=(dx, dy),
                    textcoords="offset points", fontsize=8, fontweight="bold",
                    ha=ha, zorder=6)
    ax.margins(x=0.10)
    ax.set_xlabel("MPO $\\uparrow$")
    ax.set_ylabel("SYBA $\\uparrow$")
    ax.grid(alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)
    if legend:
        handles = [
            Line2D([], [], marker="o", ls="", mfc="0.75", mec="black", ms=7,
                   label="PNS proxy $= 1.0$"),
            Line2D([], [], marker="^", ls="", mfc="0.75", mec="black", ms=7,
                   label="PNS proxy $= 0.0$"),
        ]
        ax.legend(handles=handles, loc="center left", frameon=False)
    return mpl.cm.ScalarMappable(norm=norm, cmap=cmap)


def fig_pareto(front: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(110 * MM, 82 * MM), layout="constrained")
    sm = _pareto_axes(ax, front)
    cb = fig.colorbar(sm, ax=ax, pad=0.02)
    cb.set_label("RRS-informed proxy", fontsize=7.5)
    cb.ax.tick_params(labelsize=6.5)
    ax.set_ylim(-0.08, 1.12)
    ax.text(0.985, 0.42, "SA constant (3.0), excluded", transform=ax.transAxes,
            ha="right", fontsize=6.5, color="0.35")
    save(fig, "pareto_front")


# ---------------------------------------------------------------- figure 4
def fig_overview(df: pd.DataFrame, front: pd.DataFrame) -> None:
    """Three-panel evidence overview: paired differences, front, ablation."""
    piv = df.pivot_table(index="seed", columns="method", values="reward")
    diff = (piv["mcts"] - piv["random"]).sort_index()
    mean = diff.mean()
    sem = diff.std(ddof=1) / np.sqrt(diff.size)
    ci = 2.093 * sem  # t(0.975, df = 19)

    fig, axes = plt.subplots(1, 3, figsize=(180 * MM, 62 * MM), layout="constrained")

    ax = axes[0]
    colors = ["#D55E00" if d < 0 else "#0072B2" for d in diff]
    ax.bar(diff.index, diff.values, color=colors, width=0.72,
           edgecolor="black", linewidth=0.3, zorder=3)
    ax.axhspan(mean - ci, mean + ci, color="0.55", alpha=0.30, zorder=1)
    ax.axhline(mean, color="black", lw=0.9, ls="--", zorder=2)
    ax.axhline(0, color="black", lw=0.6, zorder=2)
    ax.set_xlabel("Seed")
    ax.set_ylabel("MCTS $-$ random reward")
    ax.set_title("A", loc="left")
    ax.text(0.5, 0.04,
            f"mean $= {_mnum(mean)}$, 95% CI [${_mnum(mean-ci)}$, ${_mnum(mean+ci)}$]",
            transform=ax.transAxes, ha="center", fontsize=6.5)
    ax.grid(axis="y", alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)

    ax = axes[1]
    sm = _pareto_axes(ax, front, legend=False)
    cb = fig.colorbar(sm, ax=ax, pad=0.02)
    cb.set_label("RRS proxy", fontsize=6.5)
    cb.ax.tick_params(labelsize=6)
    ax.set_ylim(-0.08, 1.12)
    ax.set_title("B", loc="left")

    ax = axes[2]
    abl = pd.read_csv(RESULTS / "ablation" / "p4_component_ablation_summary.csv")
    eff = {}
    for factor, sub in abl.groupby("factor"):
        sub = sub.sort_values("mean_reward")
        eff[factor] = sub["mean_reward"].iloc[-1] - sub["mean_reward"].iloc[0]
    ser = pd.Series(eff).sort_values()
    ax.barh(range(len(ser)), ser.values, color="#009E73", edgecolor="black",
            linewidth=0.3, height=0.62, zorder=3)
    ax.set_yticks(range(len(ser)))
    ax.set_yticklabels(ser.index, fontsize=6.5)
    ax.set_xlabel("High $-$ low main effect")
    ax.set_title("C", loc="left")
    for i, v in enumerate(ser.values):
        ax.text(v + 0.004, i, f"{v:+.3f}", va="center", fontsize=6)
    ax.set_xlim(0, max(ser.values) * 1.30)
    ax.grid(axis="x", alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)

    save(fig, "p4_evidence_overview")


# ---------------------------------------------------------------- figure 5
def fig_rrs_pns() -> None:
    """RRS distributions and PNS = 1 fractions over re-scored best-in-seed rows."""
    mo = pd.read_csv(RESULTS / "pareto" / "p4_multiobj_benchmark.csv")
    mo = mo[mo.rrs.notna() & mo.pns.notna()]
    present = [m for m in ORDER if m in set(mo.method)]

    fig, axes = plt.subplots(1, 2, figsize=(170 * MM, 68 * MM), layout="constrained")
    rng = np.random.default_rng(20260815)

    ax = axes[0]
    for i, m in enumerate(present):
        vals = mo[mo.method == m]["rrs"].to_numpy()
        ax.boxplot([vals], positions=[i], widths=0.5, showfliers=False,
                   medianprops=dict(color="black", lw=1.0),
                   boxprops=dict(lw=0.6), whiskerprops=dict(lw=0.6),
                   capprops=dict(lw=0.6))
        ax.scatter(i + rng.uniform(-0.14, 0.14, vals.size), vals, s=9,
                   color=C[m], alpha=0.65, edgecolors="none", zorder=3)
    ax.set_xticks(range(len(present)))
    ax.set_xticklabels([f"{LABEL_WRAP[m]}\n$n$={int((mo.method == m).sum())}"
                        for m in present], fontsize=6.5)
    ax.set_ylabel("RRS-informed proxy")
    ax.set_title("A", loc="left")
    ax.grid(axis="y", alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)

    ax = axes[1]
    for i, m in enumerate(present):
        sub = mo[mo.method == m]["pns"].to_numpy()
        frac = float((sub >= 1.0).sum()) / sub.size
        ax.bar(i, frac, width=0.6, color=C[m], edgecolor="black", linewidth=0.4,
               hatch=HATCH[m], zorder=3)
        ax.text(i, frac + 0.02, f"{int((sub >= 1.0).sum())}/{sub.size}",
                ha="center", fontsize=6.5)
    ax.set_xticks(range(len(present)))
    ax.set_xticklabels([LABEL_WRAP[m] for m in present], fontsize=6.5)
    ax.set_ylabel("Fraction of valid rows with PNS $= 1$")
    ax.set_ylim(0, 1.12)
    ax.set_title("B", loc="left")
    ax.grid(axis="y", alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)

    save(fig, "rrs_pns_profile")


# ---------------------------------------------------------------- figure 6
def fig_diversity() -> None:
    """MDS projection of best-in-seed sets; greedy collapses to one point."""
    mds = pd.read_csv(RESULTS / "diversity" / "p4_diversity_mds.csv")
    met = pd.read_csv(RESULTS / "diversity" / "p4_diversity_metrics.csv").set_index("method")

    fig, ax = plt.subplots(figsize=(115 * MM, 100 * MM), layout="constrained")
    for m in ORDER:
        sub = mds[mds.method == m]
        if sub.empty:
            continue
        d = met.loc[m, "mean_pairwise_tanimoto_dissimilarity"]
        ax.scatter(sub.mds_x, sub.mds_y, s=34, marker=MK[m], color=C[m],
                   alpha=0.80, edgecolors="black", linewidths=0.4,
                   label=f"{LABEL[m]} (mean dissim. {d:.4f})", zorder=3)
    ax.set_xlabel("MDS dimension 1")
    ax.set_ylabel("MDS dimension 2")
    # "best" put the four long entries inside the data region, on top of the markers,
    # and the footer below overprinted the fourth. Lift the legend clear of the axes.
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2,
              frameon=False, fontsize=6.5, handletextpad=0.4, columnspacing=1.2)
    ax.grid(alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)
    # Reserve a blank band below the point cloud for the provenance footer. At the
    # autoscaled limits the lowest MCTS marker sits directly under the footer and is
    # masked by its opaque background. Only whitespace is added; no value is rescaled.
    y0, y1 = ax.get_ylim()
    ax.set_ylim(y0 - 0.14 * (y1 - y0), y1)
    ax.text(0.985, 0.02,
            "metric MDS on ECFP4 Tanimoto dissimilarity; 20 molecules per method",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6, color="0.35",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.85,
                      boxstyle="square,pad=0.25"))
    save(fig, "scaffold_diversity")


def main() -> None:
    with plt.rc_context(RC):
        bench = load_bench()
        front = pd.read_csv(RESULTS / "pareto" / "merged_pareto_front.csv")
        print("regenerating P4 figures ->", OUT)
        fig_benchmark_bar(bench)
        fig_efficiency(bench)
        fig_pareto(front)
        fig_overview(bench, front)
        fig_rrs_pns()
        fig_diversity()

        s = summary(bench)
        print("\nconsistency check against the manuscript:")
        for m in ORDER:
            print(f"  {LABEL[m]:<18} {s.loc[m,'mean']:.4f} +/- {s.loc[m,'sd']:.4f}"
                  f"  t={s.loc[m,'time']:.1f}s")


if __name__ == "__main__":
    main()
