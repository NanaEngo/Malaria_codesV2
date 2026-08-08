#!/usr/bin/env python3
"""
P4 — Generate publication-quality figures for the manuscript.

Generates 4 PNG figures from benchmark CSV results:
  1. benchmark_reward_bar.png   — Bar chart: mean best reward ± std per method
  2. benchmark_efficiency.png   — Scatter: time vs reward with method colours
  3. pareto_front.png           — Scatter: MPO vs SYBA, coloured by SA (inverse)
  4. scaffold_diversity.png     — 2D MDS projection with method-coloured points

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

    # Significance brackets (paired t-test on 20 seeds; v12 canonical data)
    y_max = max(means) + max(stds) + 0.06
    # v12 paired tests: MCTS vs Random and MCTS vs GA.
    ax.plot([0, 1], [y_max, y_max], "k-", linewidth=0.6)
    ax.text(0.5, y_max + 0.004, "p = 0.000085", ha="center", fontsize=7,
            fontstyle="italic")
    y2 = max(means) + max(stds) + 0.11
    ax.plot([1, 3], [y2, y2], "k-", linewidth=0.6)
    ax.text(2.0, y2 + 0.004, "p < 0.0001", ha="center", fontsize=7,
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

    # Annotations for method regions
    ax.annotate("Cheap", xy=(30, 0.706), fontsize=7, fontstyle="italic",
                color="grey", ha="center")
    ax.annotate("Costly", xy=(68, 0.706), fontsize=7, fontstyle="italic",
                color="grey", ha="center")

    ax.set_xlim(0, 100)
    ax.set_ylim(0.69, 0.76)
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


# ── Main ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate P4 manuscript figures")
    parser.add_argument("--figures", nargs="+",
                        choices=["reward_bar", "efficiency", "pareto", "diversity"],
                        default=["reward_bar", "efficiency", "pareto", "diversity"],
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

    if "reward_bar" in args.figures:
        print("  [1/4] Reward bar chart...")
        plot_reward_bar(data)

    if "efficiency" in args.figures:
        print("  [2/4] Efficiency scatter...")
        plot_efficiency(data)

    if "pareto" in args.figures:
        print("  [3/4] Pareto front (delegating to p4_plot_merged_pareto.py)...")
        script_path = Path(__file__).with_name("p4_plot_merged_pareto.py")
        if script_path.exists():
            subprocess.run([sys.executable, str(script_path)], check=True)
        else:
            print(f"  WARNING: {script_path} not found; falling back to legacy plot_pareto_front")
            plot_pareto_front(data)

    if "diversity" in args.figures:
        print("  [4/4] Scaffold diversity MDS...")
        plot_diversity(data)

    print("\n" + "=" * 55)
    print("  All figures generated successfully!")
    print("=" * 55)


if __name__ == "__main__":
    main()
