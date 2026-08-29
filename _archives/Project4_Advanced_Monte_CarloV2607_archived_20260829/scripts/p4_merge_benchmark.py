#!/usr/bin/env python3
"""P4 — Merge per-seed benchmark CSVs and generate a summary LaTeX table.

Reads all ``results/benchmark/p4_benchmark_seed_*.csv`` files, writes a merged
CSV, and produces a LaTeX table of mean ± standard deviation reward and
wall-clock time for each method.

Usage:
    python scripts/p4_merge_benchmark.py
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from statistics import mean, stdev


PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results" / "benchmark"

METHOD_ORDER = ["random", "mcts", "ga", "greedy"]
METHOD_LABELS = {
    "random": "Random",
    "mcts": "MCTS+ScafVAE",
    "ga": "GA",
    "greedy": "Greedy",
}


def discover_csvs(results_dir: Path) -> list[Path]:
    """Return all per-seed benchmark CSVs sorted by seed number."""
    csvs = []
    for p in results_dir.glob("p4_benchmark_seed_*.csv"):
        try:
            seed_part = p.stem.split("_")[-1]
            int(seed_part)
            csvs.append(p)
        except ValueError:
            continue
    return sorted(csvs, key=lambda p: int(p.stem.split("_")[-1]))


def load_rows(csv_paths: list[Path]) -> list[dict]:
    rows = []
    for path in csv_paths:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({
                    "method": row["method"].strip().lower(),
                    "seed": int(row["seed"]),
                    "reward": float(row["reward"]),
                    "elapsed_s": float(row["elapsed_s"]),
                })
    return rows


def compute_stats(rows: list[dict]) -> dict:
    """Return {method: {mean_reward, std_reward, min_reward, max_reward, mean_time, std_time, n}}."""
    stats = {}
    for method in METHOD_ORDER:
        method_rows = [r for r in rows if r["method"] == method]
        if not method_rows:
            stats[method] = None
            continue
        rewards = [r["reward"] for r in method_rows]
        times = [r["elapsed_s"] for r in method_rows]
        n = len(method_rows)
        stats[method] = {
            "n": n,
            "mean_reward": mean(rewards),
            "std_reward": stdev(rewards) if n > 1 else 0.0,
            "min_reward": min(rewards),
            "max_reward": max(rewards),
            "mean_time": mean(times),
            "std_time": stdev(times) if n > 1 else 0.0,
        }
    return stats


def write_merged_csv(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "seed", "reward", "elapsed_s"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"  Merged CSV: {output}")


def write_latex_table(stats: dict, output: Path) -> None:
    """Write a LaTeX table summarising mean, std, min, max reward and mean time per method."""
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "% P4 benchmark summary across all seeds (auto-generated)",
        "\\begin{tabular}{l c c c c c}",
        "\\hline",
        "Method & Mean reward & Std & Min & Max & Mean time (s) \\\\",
        "\\hline",
    ]
    for method in METHOD_ORDER:
        s = stats[method]
        if s is None:
            lines.append(f"{METHOD_LABELS[method]} & --- & --- & --- & --- & --- \\\\")
            continue
        mean_r = f"{s['mean_reward']:.4f}"
        std_r = f"{s['std_reward']:.4f}"
        min_r = f"{s['min_reward']:.4f}"
        max_r = f"{s['max_reward']:.4f}"
        time_r = f"{s['mean_time']:.1f}"
        lines.append(
            f"{METHOD_LABELS[method]} & {mean_r} & {std_r} & {min_r} & {max_r} & {time_r} \\\\"
        )
    lines.extend([
        "\\hline",
        "\\end{tabular}",
    ])
    output.write_text("\n".join(lines) + "\n")
    print(f"  LaTeX table: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge P4 benchmark per-seed CSVs and generate a LaTeX summary table."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directory containing p4_benchmark_seed_*.csv files",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=RESULTS_DIR / "p4_benchmark_merged.csv",
    )
    parser.add_argument(
        "--output-tex",
        type=Path,
        default=RESULTS_DIR / "p4_benchmark_table.tex",
    )
    args = parser.parse_args()

    csv_paths = discover_csvs(args.results_dir)
    if not csv_paths:
        print(f"ERROR: No p4_benchmark_seed_*.csv files found in {args.results_dir}", file=sys.stderr)
        return 1

    print(f"Discovered {len(csv_paths)} per-seed CSV files")
    rows = load_rows(csv_paths)
    stats = compute_stats(rows)

    write_merged_csv(rows, args.output_csv)
    write_latex_table(stats, args.output_tex)

    print("\nSummary:")
    for method in METHOD_ORDER:
        s = stats[method]
        if s is None:
            print(f"  {METHOD_LABELS[method]}: no data")
        else:
            print(f"  {METHOD_LABELS[method]}: reward {s['mean_reward']:.4f} ± {s['std_reward']:.4f} "
                  f"[{s['min_reward']:.4f}, {s['max_reward']:.4f}] "
                  f"(time {s['mean_time']:.1f} ± {s['std_time']:.1f} s, n={s['n']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
