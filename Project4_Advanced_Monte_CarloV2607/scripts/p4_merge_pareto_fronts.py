#!/usr/bin/env python3
"""P4 — Merge per-seed Pareto front CSVs into a single consolidated front.

Usage:
    python3 p4_merge_pareto_fronts.py [--results-dir PATH] [--output-csv PATH]

Merges all p4_pareto_seed_*.csv files from the results/pareto/ directory,
computes the consolidated Pareto front across all seeds, and outputs:
1. A CSV with all unique Pareto-optimal molecules
2. Summary statistics to stdout (front size, hypervolume, seeds count)
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from p4_mcts_pareto import ParetoFront


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge per-seed Pareto front CSVs into a consolidated front."
    )
    parser.add_argument(
        "--results-dir", type=Path, default=None,
        help="Path to pareto results directory (default: ../results/pareto)"
    )
    parser.add_argument(
        "--output-csv", type=Path, default=None,
        help="Output consolidated CSV path (default: ../results/pareto/merged_pareto_front.csv)"
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    results_dir = args.results_dir or (project_dir / "results" / "pareto")
    output_csv = args.output_csv or (results_dir / "merged_pareto_front.csv")

    if not results_dir.exists():
        print(f"ERROR: Results directory not found: {results_dir}", file=sys.stderr)
        sys.exit(1)

    # Define objectives (must match p4_mcts_pareto_run.py)
    objectives = ["mpo", "syba", "sa", "rrs", "pns"]
    maximize = [True, True, False, True, True]

    # Load all per-seed CSVs
    pareto_csvs = sorted(results_dir.glob("p4_pareto_seed_*.csv"))
    if not pareto_csvs:
        print(f"ERROR: No p4_pareto_seed_*.csv files found in {results_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"═══ P4 Pareto Front Merge ═══")
    print(f"  Results dir:    {results_dir}")
    print(f"  Found CSVs:     {len(pareto_csvs)}")
    print(f"  Objectives:     {objectives}")

    # Consolidate all molecules across all seeds
    consolidated = ParetoFront(objectives=objectives, maximize=maximize)

    seeds_found = set()
    total_molecules = 0

    for csv_path in pareto_csvs:
        seed = int(csv_path.stem.replace("p4_pareto_seed_", ""))
        seeds_found.add(seed)

        with open(csv_path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                total_molecules += 1
                smiles = row["smiles"]
                scores = {
                    "mpo": float(row["mpo"]),
                    "syba": float(row["syba"]),
                    "sa": float(row["sa"]),
                    "rrs": float(row["rrs"]),
                    "pns": float(row["pns"]),
                }
                consolidated.update(smiles, scores, {"seed": seed})

    # Compute merged front
    merged_solutions = consolidated.solutions
    merged_hv = consolidated.hypervolume()

    print(f"\n  Seeds found:     {len(seeds_found)} ({sorted(seeds_found)[:5]}...)")
    print(f"  Total molecules: {total_molecules}")
    print(f"  Consolidated front size: {len(merged_solutions)}")
    print(f"  Consolidated hypervolume: {merged_hv:.4f}")

    # Write consolidated CSV
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "smiles", "mpo", "syba", "sa", "rrs", "pns",
            "hypervolume", "seed",
        ])
        for smi, vec, meta in merged_solutions:
            writer.writerow([
                smi,
                f"{vec[0]:.4f}",  # MPO
                f"{vec[1]:.4f}",  # SYBA
                f"{vec[2]:.4f}",  # SA
                f"{vec[3]:.4f}",  # RRS
                f"{vec[4]:.4f}",  # PNS
                f"{merged_hv:.4f}",
                meta.get("seed", "?"),
            ])

    print(f"  Output CSV:      {output_csv}")
    print(f"\n  === Front molecules (sorted by MPO descending) ===")
    sorted_solutions = sorted(merged_solutions, key=lambda x: -x[1][0])
    for smi, vec, meta in sorted_solutions[:10]:
        print(f"  {smi:40s} MPO={vec[0]:.3f} SYBA={vec[1]:.3f} "
              f"SA={vec[2]:.3f} RRS={vec[3]:.3f} PNS={vec[4]:.3f} "
              f"(seed={meta.get('seed', '?')})")
    if len(sorted_solutions) > 10:
        print(f"  ... and {len(sorted_solutions) - 10} more non-dominated solutions")
    print(f"\n═══ Merge complete ═══")


if __name__ == "__main__":
    main()
