#!/usr/bin/env python3
"""P4 — Fragment vocabulary ablation analysis (real data)

Aggregates the real fragment-set ablation outputs from
results/ablation/p4_ablation_{all,medium,aromatic_only,minimal}_seed_*.csv,
computes summary statistics, runs one-way ANOVA and Tukey HSD on the best
rewards, and writes a summary CSV plus a bar plot with error bars.

Usage:
    python scripts/p4_mcts_ablation.py
    python scripts/p4_mcts_ablation.py --output-dir results/ablation
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "ablation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P4 fragment vocabulary ablation analysis")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR,
                        help="Directory containing ablation CSV files")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR,
                        help="Directory for output CSVs/figures")
    parser.add_argument("--no-plot", action="store_true", default=False,
                        help="Skip generation of the ablation bar plot")
    return parser.parse_args()


def find_ablation_files(results_dir: Path) -> list[Path]:
    """Find real fragment-set ablation CSVs."""
    if not results_dir.exists():
        raise FileNotFoundError(f"Ablation results directory not found: {results_dir}")
    files = sorted(results_dir.glob("p4_ablation_*_seed_*.csv"))
    return files


def _fragment_set_from_path(path: Path) -> str:
    """Infer fragment set from filename, e.g. p4_ablation_all_seed_0.csv -> all."""
    parts = path.stem.split("_")
    # stems look like: p4_ablation_all_seed_0
    if len(parts) >= 4 and parts[-2] == "seed":
        return parts[2]
    return "unknown"


def load_ablation_data(files: list[Path]) -> pd.DataFrame:
    """Load all ablation CSVs into a single DataFrame with fragment_set and seed."""
    rows = []
    for path in files:
        df = pd.read_csv(path)
        if df.empty:
            continue
        # Use fragment_set column if present; otherwise infer from filename
        if "fragment_set" not in df.columns:
            df["fragment_set"] = _fragment_set_from_path(path)
        # Ensure best_reward exists; fall back to best_score if needed
        if "best_reward" not in df.columns:
            if "best_score" in df.columns:
                df["best_reward"] = df["best_score"]
            else:
                raise ValueError(f"{path} has neither 'best_reward' nor 'best_score' column")
        rows.append(df[["fragment_set", "seed", "best_reward"]].copy())
    if not rows:
        raise ValueError("No ablation data loaded.")
    return pd.concat(rows, ignore_index=True)


def aggregate_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Mean / std / sem / n per fragment set."""
    summary = (
        df.groupby("fragment_set")["best_reward"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    summary["sem"] = summary["std"] / np.sqrt(summary["count"])
    summary = summary.rename(columns={"count": "n", "mean": "mean_reward",
                                    "std": "std_reward"})
    return summary


def run_anova(df: pd.DataFrame) -> dict:
    """One-way ANOVA of best_reward across fragment sets."""
    groups = [group["best_reward"].values for _, group in df.groupby("fragment_set")]
    # Guard: ANOVA requires at least two groups with >= 2 observations each
    if len(groups) < 2 or any(len(g) < 2 for g in groups):
        raise ValueError("ANOVA requires at least two groups with at least 2 observations each")
    f_stat, p_value = stats.f_oneway(*groups)
    return {"f_statistic": f_stat, "p_value": p_value, "df_between": len(groups) - 1,
            "df_within": len(df) - len(groups)}


def tukey_hsd(df: pd.DataFrame) -> pd.DataFrame:
    """Tukey HSD pairwise comparisons (requires statsmodels)."""
    try:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
    except ImportError as exc:
        raise ImportError("statsmodels is required for Tukey HSD") from exc

    group_counts = df.groupby("fragment_set").size()
    if any(group_counts < 2):
        raise ValueError("Tukey HSD requires at least 2 observations per group")
    res = pairwise_tukeyhsd(df["best_reward"], df["fragment_set"], alpha=0.05)
    summary = res.summary()
    return pd.DataFrame(summary.data[1:], columns=summary.data[0])


def plot_ablation(summary: pd.DataFrame, output_path: Path) -> None:
    """Bar plot of mean best reward ± standard error per fragment set."""
    # Order fragment sets from most to least permissive
    order = ["all", "medium", "aromatic_only", "minimal"]
    order = [o for o in order if o in summary["fragment_set"].values]
    plot_df = summary.set_index("fragment_set").loc[order].reset_index()

    fig, ax = plt.subplots(figsize=(6, 4.5))
    x = np.arange(len(plot_df))
    bars = ax.bar(x, plot_df["mean_reward"], yerr=plot_df["sem"],
                  capsize=5, color="steelblue", edgecolor="black",
                  linewidth=0.6, alpha=0.85)

    for bar, mean in zip(bars, plot_df["mean_reward"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{mean:.3f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["fragment_set"], rotation=30, ha="right")
    ax.set_ylabel("Mean best reward", fontsize=11)
    ax.set_xlabel("Fragment vocabulary", fontsize=11)
    ax.set_title("Fragment vocabulary ablation: mean reward ± SEM", fontsize=12, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, plot_df["mean_reward"].max() * 1.2)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    files = find_ablation_files(args.results_dir)
    if not files:
        print(f"ERROR: no ablation CSVs found in {args.results_dir}", file=sys.stderr)
        sys.exit(1)

    df = load_ablation_data(files)
    print(f"Loaded {len(df)} ablation records from {len(files)} files")
    print("Fragment sets:", sorted(df["fragment_set"].unique()))

    # Summary statistics
    summary = aggregate_stats(df)
    summary_path = args.output_dir / "p4_ablation_summary.csv"
    summary.to_csv(summary_path, index=False)
    print("\nSummary:")
    print(summary.to_string(index=False))

    # ANOVA
    anova = run_anova(df)
    anova_path = args.output_dir / "p4_ablation_anova.csv"
    pd.DataFrame([anova]).to_csv(anova_path, index=False)
    print(f"\nANOVA: F={anova['f_statistic']:.4f}, p={anova['p_value']:.4g}")

    # Tukey HSD
    try:
        tukey = tukey_hsd(df)
        tukey_path = args.output_dir / "p4_ablation_tukey.csv"
        tukey.to_csv(tukey_path, index=False)
        print("\nTukey HSD:")
        print(tukey.to_string(index=False))
    except ImportError as exc:
        print(f"\nSkipping Tukey HSD: {exc}", file=sys.stderr)

    # Plot
    if not args.no_plot:
        plot_path = args.output_dir / "p4_ablation_bar.png"
        plot_ablation(summary, plot_path)
        print(f"\nPlot saved to {plot_path}")


if __name__ == "__main__":
    main()
