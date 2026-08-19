#!/usr/bin/env python3
"""
P4 — Generate publication-quality figures for the manuscript.

Generates publication figures from deposited benchmark CSV results:
  1. p4_evidence_overview.png/.pdf — paired benchmark, Pareto front and ablation effects
  2. benchmark_reward_bar.png       — mean best reward ± std per method
  3. benchmark_efficiency.png      — time vs reward with method colours
  4. pareto_front.png              — canonical MPO vs SYBA front with RRS/PNS encoding
  5. scaffold_diversity.png        — 2D MDS projection with method-coloured points

Usage:
  python scripts/p4_generate_figures.py

Output:
  manuscript/LaTeX/Graphics/*.png
"""

import argparse
import csv
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# ── Paths ────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_DIR / "results" / "benchmark_molecules_opt_v12"
GRAPHICS_DIR = PROJECT_DIR / "manuscript" / "LaTeX" / "Graphics"
GRAPHICS_DIR.mkdir(parents=True, exist_ok=True)

# ── Style ────────────────────────────────────────────────────────────
# ACS / JCIM-style publication figures
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.minor.width": 0.4,
    "ytick.minor.width": 0.4,
    "lines.linewidth": 1.2,
    "lines.markersize": 6,
})

# ── Colour palette (colourblind-friendly) ────────────────────────────
COLOURS = {
    "mcts": "#0072B2",      # blue
    "greedy": "#D55E00",    # vermillion
    "ga": "#009E73",        # green
    "random": "#CC79A7",    # pink
}
METHOD_LABELS = {
    "mcts": "MCTS+ScafVAE",
    "greedy": "Greedy",
    "ga": "GA",
    "random": "Random",
}
N_SEEDS = 20  # matches --array=0-19 in p4_benchmark_array.sbatch


def load_benchmark_data():
    """Load benchmark data from the merged CSV (preferred) or per-seed CSVs."""
    data = defaultdict(list)
    merged_path = RESULTS_DIR / "p4_benchmark_merged.csv"

    if merged_path.exists():
        print(f"  Using merged benchmark data: {merged_path}")
        with open(merged_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                method = row["method"].strip().lower()
                data[method].append({
                    "seed": int(row["seed"]),
                    "reward": float(row.get("best_reward", row.get("reward", 0))),
                    "mpo": float(row.get("mpo", 0)),
                    "docking": float(row.get("docking", 0)),
                    "syba": float(row.get("syba", 0)),
                    "sa": float(row.get("sa", 0)),
                    "time_s": float(row.get("time_s", row.get("elapsed_s", 0))),
                })
    else:
        print(f"  WARNING: {merged_path} not found; falling back to per-seed files")
        for seed in range(N_SEEDS):
            csv_path = RESULTS_DIR / f"p4_benchmark_seed_{seed}.csv"
            if not csv_path.exists():
                print(f"  WARNING: {csv_path} not found")
                continue
            with open(csv_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    method = row["method"].strip().lower()
                    data[method].append({
                        "seed": int(row["seed"]),
                        "reward": float(row.get("best_reward", row.get("reward", 0))),
                        "mpo": float(row.get("mpo", 0)),
                        "docking": float(row.get("docking", 0)),
                        "syba": float(row.get("syba", 0)),
                        "sa": float(row.get("sa", 0)),
                        "time_s": float(row.get("time_s", row.get("elapsed_s", 0))),
                    })
    if not data:
        print("  ERROR: No benchmark data loaded! Check results/benchmark/ directory.")
        print(f"  Expected either p4_benchmark_merged.csv or {N_SEEDS} per-seed files")
        sys.exit(1)
    return data


# ── Figure 1: Benchmark reward bar chart ─────────────────────────────
def plot_reward_bar(data):
    """Bar chart of mean best reward ± std for each method."""
    methods = ["random", "mcts", "greedy", "ga"]
    means = []
    stds = []
    colours = []
    labels = []

    for m in methods:
        rewards = [d["reward"] for d in data[m]]
        means.append(np.mean(rewards))
        stds.append(np.std(rewards, ddof=1))
        colours.append(COLOURS[m])
        labels.append(METHOD_LABELS[m])

    fig, ax = plt.subplots(figsize=(4.5, 3.8))
    x = np.arange(len(methods))
    bars = ax.bar(x, means, yerr=stds, capsize=4, color=colours,
                  edgecolor="black", linewidth=0.6, width=0.55,
                  error_kw={"linewidth": 1.0, "ecolor": "dimgrey"})

    # Add value labels on bars
    for i, (bar, mean, std) in enumerate(zip(bars, means, stds)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.008,
                f"{mean:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Mean best reward", fontsize=10)
    ax.set_ylim(0, max(means) + max(stds) + 0.06)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.01))
    n_seeds_actual = max(len(data[m]) for m in methods if m in data)
    ax.set_title(f"Benchmark comparison ({n_seeds_actual} seeds)", fontsize=11, fontweight="bold")

    # Significance brackets (paired tests on the same seed IDs).
    by_seed = {
        m: {int(d["seed"]): d["reward"] for d in data[m]}
        for m in methods
    }
    common_mr = sorted(set(by_seed["mcts"]) & set(by_seed["random"]))
    common_mg = sorted(set(by_seed["mcts"]) & set(by_seed["ga"]))
    p_mr = ttest_rel([by_seed["mcts"][s] for s in common_mr],
                     [by_seed["random"][s] for s in common_mr]).pvalue
    p_mg = ttest_rel([by_seed["mcts"][s] for s in common_mg],
                     [by_seed["ga"][s] for s in common_mg]).pvalue

    def p_label(p):
        return f"p = {p:.6f}" if p >= 1e-4 else "p < 0.0001"

    y_max = max(means) + max(stds) + 0.06
    ax.plot([0, 1], [y_max, y_max], "k-", linewidth=0.6)
    ax.text(0.5, y_max + 0.004, p_label(p_mr), ha="center", fontsize=7,
            fontstyle="italic")
    y2 = max(means) + max(stds) + 0.11
    ax.plot([1, 3], [y2, y2], "k-", linewidth=0.6)
    ax.text(2.0, y2 + 0.004, p_label(p_mg), ha="center", fontsize=7,
            fontstyle="italic")
    ax.set_ylim(0, y2 + 0.06)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    out_path = GRAPHICS_DIR / "benchmark_reward_bar.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"  ✅ {out_path.name}")


# ── Figure 2: Efficiency scatter plot ────────────────────────────────
def plot_efficiency(data):
    """Scatter + errorbar: reward vs time, coloured by method.

    Individual seed results are shown as scatter points; mean ± std
    per method is overlaid as error bars for a clearer comparison.
    """
    methods = ["mcts", "greedy", "ga", "random"]
    markers = {"mcts": "o", "greedy": "s", "ga": "^", "random": "D"}

    fig, ax = plt.subplots(figsize=(4.5, 3.8))

    for m in methods:
        times = np.array([d["time_s"] for d in data[m]])
        rewards = np.array([d["reward"] for d in data[m]])

        # Individual seed points (transparent, show distribution)
        ax.scatter(times, rewards, c=COLOURS[m], label=None,
                   marker=markers[m], s=25, edgecolors="black",
                   linewidth=0.3, alpha=0.4, zorder=2)

        # Mean ± std error bar (bold, principal visual anchor)
        mean_t, mean_r = np.mean(times), np.mean(rewards)
        std_t, std_r = np.std(times, ddof=1), np.std(rewards, ddof=1)
        ax.errorbar(mean_t, mean_r, xerr=std_t, yerr=std_r,
                    fmt=markers[m], c=COLOURS[m], label=METHOD_LABELS[m],
                    markersize=9, markeredgecolor="black",
                    markeredgewidth=0.6, capsize=4, capthick=1.0,
                    elinewidth=1.2, alpha=1.0, zorder=4)

    ax.set_xlabel("Wall-clock time (s)", fontsize=10)
    ax.set_ylabel("Best reward", fontsize=10)
    ax.set_title("Computational efficiency", fontsize=11, fontweight="bold")
    ax.legend(frameon=True, fancybox=False, edgecolor="grey", fontsize=8,
              loc="upper left")

    # Dynamic limits retain every method, including the low-reward greedy arm.
    all_times = np.concatenate([
        np.array([d["time_s"] for d in data[m]]) for m in methods
    ])
    all_rewards = np.concatenate([
        np.array([d["reward"] for d in data[m]]) for m in methods
    ])
    t_min, t_max = float(all_times.min()), float(all_times.max())
    r_min, r_max = float(all_rewards.min()), float(all_rewards.max())
    t_pad = 0.15 * (t_max - t_min) if t_max > t_min else 5.0
    r_pad = 0.15 * (r_max - r_min) if r_max > r_min else 0.01
    ax.set_xlim(max(0.0, t_min - t_pad), t_max + t_pad)
    ax.set_ylim(max(0.0, r_min - r_pad), min(1.0, r_max + r_pad))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.02))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(50))

    out_path = GRAPHICS_DIR / "benchmark_efficiency.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"  ✅ {out_path.name}")


# ── Figure 3: Pareto front ───────────────────────────────────────────
def load_pareto_data():
    """Load real Pareto-optimal data from p4_pareto_data.csv.

    Contains 5 QMC-validated Pareto-optimal candidates plus the
    20 best-in-seed molecules from the benchmark (4 methods x 5 seeds).
    Returns dict: method -> list of (mpo, syba, sa_inv, label).
    """
    csv_path = RESULTS_DIR / "p4_pareto_data.csv"
    if not csv_path.exists():
        print("  WARNING: p4_pareto_data.csv not found; falling back to benchmark data")
        return None

    data = {
        "pareto_qmc": [], "pareto_additional": [],
        "mcts": [], "greedy": [], "ga": [], "random": [],
    }
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip comment lines (those starting with # are skipped by csv.reader)
            method = row["method"]
            mpo = float(row["mpo"])
            syba = float(row["syba"])
            sa_inv = float(row["sa_inv"])
            label = row["label"]
            if method in data:
                data[method].append((mpo, syba, sa_inv, label))
    return data


def plot_pareto_front(data):
    """Pareto front scatter: MPO vs SYBA, coloured by SA⁻¹.

    Uses real data from p4_pareto_data.csv (5 QMC-validated Pareto-optimal
    candidates + additional best-in-seed benchmark molecules) and computes
    the displayed Pareto frontier directly from the loaded points.
    """
    pareto_data = load_pareto_data()

    markers = {"pareto_qmc": "*", "pareto_additional": "P",
               "mcts": "o", "greedy": "s", "ga": "^", "random": "D"}
    method_labels = {"pareto_qmc": "QMC Pareto (n=5)",
                     "pareto_additional": "Pareto (n=7, non-QMC)",
                     "mcts": METHOD_LABELS["mcts"],
                     "greedy": METHOD_LABELS["greedy"],
                     "ga": METHOD_LABELS["ga"],
                     "random": METHOD_LABELS["random"]}

    fig, ax = plt.subplots(figsize=(5.0, 4.0))

    all_sas_inv = []

    if pareto_data is not None:
        # Iterate in specific order: QMC first (gold stars, prominent),
        # then additional Pareto (diamonds), then benchmark methods
        for method in ["pareto_qmc", "pareto_additional",
                       "mcts", "greedy", "ga", "random"]:
            points = pareto_data.get(method, [])
            if not points:
                continue
            mpos = [p[0] for p in points]
            sybas = [p[1] for p in points]
            sas_inv = [p[2] for p in points]
            labels = [p[3] for p in points]
            all_sas_inv.extend(sas_inv)

            # Different styling for Pareto vs background points
            if method == "pareto_qmc":
                size, alpha, edge_w = 110, 0.95, 0.8
                zorder = 5
            elif method == "pareto_additional":
                size, alpha, edge_w = 70, 0.85, 0.6
                zorder = 4
            else:
                size, alpha, edge_w = 40, 0.50, 0.3
                zorder = 2

            sc = ax.scatter(mpos, sybas, c=sas_inv, cmap="viridis_r",
                            marker=markers[method], s=size,
                            edgecolors="black", linewidth=edge_w,
                            alpha=alpha, vmin=0.4, vmax=1.0,
                            label=method_labels[method], zorder=zorder)

            # Annotate QMC candidates with P1-P5 labels
            if method == "pareto_qmc":
                for i, (x, y, label) in enumerate(zip(mpos, sybas, labels)):
                    ax.annotate(f"  P{i+1}", (x, y), fontsize=7,
                                fontweight="bold", color="black")
            # Annotate additional Pareto with A1-A7 labels
            if method == "pareto_additional":
                for (x, y, label) in zip(mpos, sybas, labels):
                    ax.annotate(f"  {label}", (x, y), fontsize=6,
                                fontstyle="italic", color="dimgrey")
    else:
        # Fallback: use benchmark data only
        for m in ["mcts", "greedy", "ga", "random"]:
            if m not in data:
                continue
            mpos = [d["mpo"] for d in data[m]]
            sybas = [d["syba"] for d in data[m]]
            sas_inv = [(10 - d["sa"]) / 9 for d in data[m]]
            all_sas_inv.extend(sas_inv)
            sc = ax.scatter(mpos, sybas, c=sas_inv, cmap="viridis_r",
                            marker=markers[m], s=45, edgecolors="black",
                            linewidth=0.4, alpha=0.65, vmin=0.4, vmax=1.0,
                            label=method_labels[m], zorder=3)

    # Compute and plot the Pareto frontier from all data points
    if all_sas_inv:
        all_mpos_list = []
        all_sybas_list = []
        # Collect all points for Pareto frontier computation
        if pareto_data is not None:
            for method in pareto_data:
                for p in pareto_data[method]:
                    all_mpos_list.append(p[0])
                    all_sybas_list.append(p[1] * -1)  # negate for minimisation
        else:
            for m in data:
                for d in data[m]:
                    all_mpos_list.append(d["mpo"])
                    all_sybas_list.append(d["syba"] * -1)

        # Compute non-dominated front (2D projection: MPO vs negated SYBA)
        points_2d = np.column_stack([all_mpos_list, all_sybas_list])
        # Sort by MPO and compute Pareto front
        idx = np.argsort(points_2d[:, 0])
        sorted_pts = points_2d[idx]
        pareto_frontier = [sorted_pts[0]]
        for pt in sorted_pts[1:]:
            if pt[1] < pareto_frontier[-1][1]:  # lower = better (negated SYBA)
                pareto_frontier.append(pt)
        pareto_frontier = np.array(pareto_frontier)

        # Plot frontier (convert SYBA back to positive)
        ax.plot(pareto_frontier[:, 0], pareto_frontier[:, 1] * -1,
                "k--", linewidth=0.8, alpha=0.5, label="Pareto frontier",
                zorder=1)

    ax.set_xlabel("MPO score (maximise)", fontsize=10)
    ax.set_ylabel("SYBA score (maximise)", fontsize=10)
    ax.set_title("Pareto front (MPO vs SYBA)", fontsize=11, fontweight="bold")

    # Colour bar for SA (guard against empty data)
    if 'sc' in locals():
        cbar = fig.colorbar(sc, ax=ax, shrink=0.75, pad=0.02)
        cbar.set_label("Accessibility (SA⁻¹)", fontsize=8)
        cbar.ax.tick_params(labelsize=7)

    ax.set_xlim(0.65, 1.00)
    ax.set_ylim(-0.15, 0.90)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.20))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.05))
    ax.legend(frameon=True, fancybox=False, edgecolor="grey",
              fontsize=7, loc="upper left", ncol=1)

    out_path = GRAPHICS_DIR / "pareto_front.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"  ✅ {out_path.name}")


# ── Figure 4: Scaffold diversity MDS ─────────────────────────────────
def plot_diversity(data):
    """2D metric MDS projection of the deposited best-in-seed molecule sets."""
    import pandas as pd

    mds_path = PROJECT_DIR / "results" / "diversity" / "p4_diversity_mds.csv"
    if not mds_path.exists():
        print(f"  WARNING: {mds_path} not found; skipping diversity figure")
        return
    mds = pd.read_csv(mds_path)

    markers = {"mcts": "o", "greedy": "s", "ga": "^", "random": "D"}

    fig, ax = plt.subplots(figsize=(4.5, 4.0))
    for m in ["mcts", "random", "greedy", "ga"]:
        sub = mds[mds["method"] == m]
        if sub.empty:
            continue
        ax.scatter(sub["mds_x"], sub["mds_y"], c=COLOURS[m],
                   label=METHOD_LABELS[m], marker=markers[m], s=30,
                   edgecolors="black", linewidth=0.3, alpha=0.7, zorder=3)

    ax.set_xlabel("MDS dimension 1", fontsize=10)
    ax.set_ylabel("MDS dimension 2", fontsize=10)
    ax.set_title("Chemical space coverage (metric MDS)", fontsize=11,
                 fontweight="bold")
    ax.legend(frameon=True, fancybox=False, edgecolor="grey", fontsize=8)
    ax.set_aspect("equal")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    out_path = GRAPHICS_DIR / "scaffold_diversity.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"  ✅ {out_path.name}")


# ── Figure 5: Integrated evidence overview ───────────────────────────
def plot_overview(data):
    """Generate a compact, evidence-linked overview for the manuscript.

    Panel A shows the paired per-seed MCTS-minus-Random differences from the
    canonical v12 scalar benchmark. Panel B shows the four locked pre-activity
    Pareto solutions with RRS colour and PNS marker shape. Panel C shows the
    observed high-minus-low main effects from the factorial ablation summary.
    No values are simulated or re-estimated here; every point is read directly
    from deposited CSV files.
    """
    benchmark_path = RESULTS_DIR / "p4_benchmark_merged.csv"
    pareto_path = PROJECT_DIR / "results" / "pareto" / "merged_pareto_front.csv"
    ablation_path = PROJECT_DIR / "results" / "ablation" / "p4_component_ablation_summary.csv"
    for path in (benchmark_path, pareto_path, ablation_path):
        if not path.exists():
            raise FileNotFoundError(f"Overview input not found: {path}")

    bench = pd.read_csv(benchmark_path)
    pivot = bench.pivot(index="seed", columns="method", values="reward").sort_index()
    delta = pivot["mcts"] - pivot["random"]
    mean_delta = float(delta.mean())
    sem_delta = float(delta.std(ddof=1) / np.sqrt(len(delta)))
    ci = 2.093024 * sem_delta  # t_(0.975, 19), fixed by n=20 protocol

    pareto = pd.read_csv(pareto_path)
    abl = pd.read_csv(ablation_path)
    pairs = [
        ("ScafVAE", "False", "True"),
        ("Pareto", "False", "True"),
        ("c_PUCT", "2.0", "1.0"),
        ("Temperature", "1.5", "0.5"),
        ("Vocab", "Small", "Large"),
    ]
    effects = []
    for factor, low, high in pairs:
        sub = abl[abl["factor"].astype(str) == factor].copy()
        sub["level_str"] = sub["level"].astype(str)
        sub = sub.set_index("level_str")
        if low not in sub.index or high not in sub.index:
            raise ValueError(f"Missing ablation levels for {factor}: {low}/{high}")
        effects.append((factor, float(sub.loc[high, "mean_reward"] - sub.loc[low, "mean_reward"])))
    effects = sorted(effects, key=lambda x: x[1])

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.6),
                             gridspec_kw={"width_ratios": [1.15, 1.0, 1.15]})
    fig.subplots_adjust(wspace=0.42, left=0.06, right=0.98, bottom=0.19, top=0.82)

    # Panel A: paired per-seed difference, with CI and exact zero line.
    ax = axes[0]
    x = np.arange(len(delta))
    colours = np.where(delta >= 0, "#0072B2", "#D55E00")
    ax.axhline(0, color="0.25", linewidth=0.8, zorder=1)
    ax.vlines(x, 0, delta.values, color=colours, linewidth=1.0, alpha=0.65, zorder=2)
    ax.scatter(x, delta.values, c=colours, edgecolors="black", linewidths=0.35,
               s=30, zorder=3)
    ax.axhline(mean_delta, color="#111111", linewidth=1.3, zorder=4)
    ax.axhspan(mean_delta - ci, mean_delta + ci, color="0.2", alpha=0.12, zorder=0)
    ax.set_title("A  Paired scalar comparison", loc="left", fontweight="bold")
    ax.set_xlabel("Seed")
    ax.set_ylabel("MCTS − Random reward")
    ax.set_xticks([0, 5, 10, 15, 19])
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.01))
    ax.text(0.03, 0.96, f"mean = {mean_delta:.4f}\n95% CI = [{mean_delta-ci:.4f}, {mean_delta+ci:.4f}]",
            transform=ax.transAxes, va="top", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="0.75"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel B: locked pre-activity Pareto front.
    ax = axes[1]
    norm = plt.Normalize(pareto["rrs"].min(), pareto["rrs"].max())
    cmap = plt.get_cmap("viridis")
    for pns, marker in [(0, "v"), (1, "o")]:
        sub = pareto[pareto["pns"] == pns]
        if not sub.empty:
            ax.scatter(sub["mpo"], sub["syba"], c=sub["rrs"], cmap=cmap, norm=norm,
                       marker=marker, s=115, edgecolors="black", linewidths=0.6,
                       zorder=3)
    for i, row in pareto.reset_index(drop=True).iterrows():
        ax.annotate(f"P{i+1}", (row["mpo"], row["syba"]), xytext=(0, 0),
                    textcoords="offset points", ha="center", va="center",
                    color="white", fontsize=8, fontweight="bold", zorder=4)
    ordered = pareto.sort_values("mpo")
    ax.plot(ordered["mpo"], ordered["syba"], "k--", linewidth=0.8, alpha=0.55)
    ax.set_title("B  Pre-activity Pareto front", loc="left", fontweight="bold")
    ax.set_xlabel("MPO (maximise)")
    ax.set_ylabel("SYBA (maximise)")
    ax.set_xlim(0.70, 0.97)
    ax.set_ylim(-0.05, 1.08)
    ax.text(0.03, 0.96, "HV = 1.2366\nSA = 3.0 (constant)", transform=ax.transAxes,
            va="top", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="0.75"))
    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                        fraction=0.046, pad=0.04)
    cbar.set_label("RRS", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor="0.55",
                              markeredgecolor="black", label="PNS = 1", markersize=7),
                       Line2D([0], [0], marker="v", color="w", markerfacecolor="0.55",
                              markeredgecolor="black", label="PNS = 0", markersize=7)],
              fontsize=7, frameon=True, loc="lower left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel C: effect-size ranking from the factorial ablation summary.
    ax = axes[2]
    labels = [x[0] for x in effects]
    vals = np.array([x[1] for x in effects])
    y = np.arange(len(vals))
    bars = ax.barh(y, vals, color="#009E73", edgecolor="black", linewidth=0.45)
    ax.axvline(0, color="0.25", linewidth=0.8)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Observed high − low mean reward")
    ax.set_title("C  Factor effects", loc="left", fontweight="bold")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.05))
    for bar, value in zip(bars, vals):
        ax.text(value + 0.003, bar.get_y() + bar.get_height()/2,
                f"{value:+.3f}", va="center", fontsize=8)
    ax.text(0.03, 0.03, "Different ablation oracle;\nrelative effects only",
            transform=ax.transAxes, fontsize=7.5, va="bottom", color="0.25")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    out_path = GRAPHICS_DIR / "p4_evidence_overview.png"
    pdf_path = GRAPHICS_DIR / "p4_evidence_overview.pdf"
    fig.savefig(out_path, dpi=400)
    fig.savefig(pdf_path)
    plt.close(fig)
    print(f"  ✅ {out_path.name}")
    print(f"  ✅ {pdf_path.name}")


# ── Figure 6: Resistance resilience and polypharmacology profile ─────
def plot_resilience_polypharm():
    """Plot the two domain-specific P2 objective profiles.

    The input contains the deposited best-in-seed molecules re-scored with the
    common pre-activity multi-objective oracle. RRS is shown descriptively as
    a distribution; PNS is shown as the fraction of rows with PNS=1 because
    the current oracle is predominantly discrete. No inferential comparison
    is performed, and the unequal valid-row counts are displayed explicitly.
    """
    path = PROJECT_DIR / "results" / "pareto" / "p4_multiobj_benchmark.csv"
    if not path.exists():
        raise FileNotFoundError(f"RRS/PNS input not found: {path}")
    df = pd.read_csv(path)
    required = {"method", "rrs", "pns"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")

    methods = ["mcts", "random", "ga", "greedy"]
    labels = [METHOD_LABELS[m] for m in methods]
    present = [m for m in methods if m in set(df["method"])]
    positions = np.arange(len(present))

    fig, axes = plt.subplots(1, 2, figsize=(8.3, 3.45),
                             gridspec_kw={"width_ratios": [1.25, 1.0]})
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.24, top=0.84, wspace=0.34)

    # RRS distribution: box + jittered observations, with n shown on x labels.
    ax = axes[0]
    rrs_values = [df.loc[df["method"] == m, "rrs"].dropna().to_numpy()
                  for m in present]
    bp = ax.boxplot(rrs_values, positions=positions, widths=0.46,
                    patch_artist=True, showfliers=False,
                    medianprops={"color": "black", "linewidth": 1.2},
                    whiskerprops={"color": "0.35", "linewidth": 0.8},
                    capprops={"color": "0.35", "linewidth": 0.8})
    for patch, m in zip(bp["boxes"], present):
        patch.set_facecolor(COLOURS[m])
        patch.set_alpha(0.35)
        patch.set_edgecolor("black")
    rng = np.random.default_rng(20260808)
    for x, m, vals in zip(positions, present, rrs_values):
        jitter = rng.uniform(-0.11, 0.11, size=len(vals))
        ax.scatter(x + jitter, vals, s=22, color=COLOURS[m],
                   edgecolors="black", linewidths=0.3, alpha=0.72, zorder=3)
        ax.text(x, 0.228, f"n={len(vals)}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(positions, [METHOD_LABELS[m] for m in present], rotation=22, ha="right")
    ax.set_ylabel("RRS (higher = predicted resilience)")
    ax.set_title("A  Resistance resilience", loc="left", fontweight="bold")
    ax.set_ylim(0.05, 0.245)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.05))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # PNS profile: PNS=1 fraction is the interpretable engagement endpoint.
    ax = axes[1]
    fractions = []
    counts = []
    for m in present:
        vals = df.loc[df["method"] == m, "pns"].dropna()
        counts.append(len(vals))
        fractions.append(float((vals >= 0.999).mean()))
    bars = ax.bar(positions, fractions,
                  color=[COLOURS[m] for m in present], edgecolor="black",
                  linewidth=0.55, width=0.55)
    for bar, frac, n in zip(bars, fractions, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, frac + 0.035,
                f"{100 * frac:.1f}%\n(n={n})", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(positions, [METHOD_LABELS[m] for m in present], rotation=22, ha="right")
    ax.set_ylabel("Rows with PNS = 1")
    ax.set_title("B  Polypharmacology engagement", loc="left", fontweight="bold")
    ax.set_ylim(0, 1.28)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.02, 0.02, "PNS=1 denotes the\nmaximum multi-target score;\nintermediate values are retained.",
            transform=ax.transAxes, fontsize=7.2, va="bottom", color="0.25")

    out_png = GRAPHICS_DIR / "rrs_pns_profile.png"
    out_pdf = GRAPHICS_DIR / "rrs_pns_profile.pdf"
    fig.savefig(out_png, dpi=400)
    fig.savefig(out_pdf)
    plt.close(fig)
    print(f"  ✅ {out_png.name}")
    print(f"  ✅ {out_pdf.name}")


# ── Main ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate P4 manuscript figures")
    parser.add_argument("--figures", nargs="+",
                        choices=["overview", "reward_bar", "efficiency", "pareto", "diversity", "rrs_pns"],
                        default=["overview", "reward_bar", "efficiency", "pareto", "diversity", "rrs_pns"],
                        help="Figures to generate")
    args = parser.parse_args()

    print("=" * 55)
    print("  P4 — Figure generation")
    print("=" * 55)

    print("\n  Loading benchmark data...")
    data = load_benchmark_data()
    methods_found = list(data.keys())
    print(f"  Methods loaded: {methods_found}")
    for m in methods_found:
        print(f"    {METHOD_LABELS.get(m, m)}: {len(data[m])} entries")

    print(f"\n  Output: {GRAPHICS_DIR}/")
    print()

    if "overview" in args.figures:
        print("  [0/5] Integrated evidence overview...")
        plot_overview(data)

    if "reward_bar" in args.figures:
        print("  [1/5] Reward bar chart...")
        plot_reward_bar(data)

    if "efficiency" in args.figures:
        print("  [2/5] Efficiency scatter...")
        plot_efficiency(data)

    if "pareto" in args.figures:
        print("  [3/5] Pareto front (delegating to p4_plot_merged_pareto.py)...")
        script_path = Path(__file__).with_name("p4_plot_merged_pareto.py")
        if script_path.exists():
            subprocess.run([sys.executable, str(script_path)], check=True)
        else:
            print(f"  WARNING: {script_path} not found; falling back to legacy plot_pareto_front")
            plot_pareto_front(data)

    if "diversity" in args.figures:
        print("  [4/6] Scaffold diversity MDS...")
        plot_diversity(data)

    if "rrs_pns" in args.figures:
        print("  [5/6] RRS/PNS domain-objective profile...")
        plot_resilience_polypharm()

    print("\n" + "=" * 55)
    print("  All figures generated successfully!")
    print("=" * 55)


if __name__ == "__main__":
    main()
