#!/usr/bin/env python3
"""P4 — Merge per-task MCTS results and rank molecules by reward.

Reads all `p4_mcts_seed_*.csv` files produced by `p4_mcts_array.sbatch`,
deduplicates by generated SMILES (keeping the highest reward), and writes a
single ranked CSV.

Optionally re-scores each unique molecule with the full P1/P2 oracle to
include component scores (MPO, docking, SYBA, SA).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


# ── Paths ────────────────────────────────────────────────────────────
def _project_dir() -> Path:
    return Path(__file__).resolve().parent.parent


RESULTS_DIR = _project_dir() / "results" / "mcts"


def _seed_from_path(p: Path) -> int:
    match = re.search(r"p4_mcts_seed_(\d+)\.csv", p.name)
    return int(match.group(1)) if match else -1


def discover_csvs(results_dir: Path) -> list[Path]:
    """Return all per-task MCTS CSV files sorted by seed."""
    if not results_dir.exists():
        return []
    csvs = [p for p in results_dir.glob("p4_mcts_seed_*.csv") if p.is_file()]
    csvs = [p for p in csvs if _seed_from_path(p) >= 0]
    csvs.sort(key=lambda p: _seed_from_path(p))
    return csvs


def merge_results(csv_paths: list[Path], rescore: bool = False) -> pd.DataFrame:
    """Load, concatenate, deduplicate, and rank MCTS results."""
    if not csv_paths:
        return pd.DataFrame(
            columns=[
                "seed",
                "initial_smiles",
                "max_steps",
                "n_iterations",
                "best_state",
                "best_reward",
            ]
        )

    df = pd.concat([pd.read_csv(p) for p in csv_paths], ignore_index=True)

    # Deduplicate by generated SMILES (highest reward first), then rank by reward
    df = df.sort_values("best_reward", ascending=False).drop_duplicates(
        subset=["best_state"], keep="first"
    ).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)

    if rescore:
        from p4_mcts_oracles import OracleAggregator

        oracle = OracleAggregator()
        component_scores = df["best_state"].apply(oracle.score)
        df["mpo"] = component_scores.apply(lambda d: d["mpo"])
        df["docking"] = component_scores.apply(lambda d: d["docking"])
        df["syba"] = component_scores.apply(lambda d: d["syba"])
        df["sa"] = component_scores.apply(lambda d: d["sa"])

    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge per-task P4 MCTS results and rank by reward."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directory containing p4_mcts_seed_*.csv files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "p4_mcts_merged_ranked.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--rescore",
        action="store_true",
        help="Re-score each unique molecule with the full oracle (slower)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=None,
        help="Only keep top-N ranked molecules",
    )
    args = parser.parse_args()

    csv_paths = discover_csvs(args.results_dir)
    print(f"Discovered {len(csv_paths)} per-task CSV files in {args.results_dir}")

    merged = merge_results(csv_paths, rescore=args.rescore)
    print(f"Merged rows: {len(merged)} unique molecules")

    if args.top_n is not None and args.top_n > 0:
        merged = merged.head(args.top_n)
        print(f"Kept top {args.top_n} molecules")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False)
    print(f"Ranked output written to: {args.output}")

    # Print a concise summary
    print("\nTop 5 molecules:")
    print(merged.head(5)[["rank", "best_state", "best_reward"]].to_string(index=False))


if __name__ == "__main__":
    main()
