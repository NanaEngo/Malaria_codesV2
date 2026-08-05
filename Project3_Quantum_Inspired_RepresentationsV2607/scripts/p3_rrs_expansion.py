#!/usr/bin/env python3
"""
P3 H1-RRS Expansion: Compute RRS for 200+ compounds.

Expands the headline Spearman rho=0.947 (n=14) correlation between H1
topological persistence and Resistance Resilience Scores (RRS) to n>=30
with balanced class representation.

Uses Tartarus full run (19,913 compounds x 3 targets) from P2 results.

Author: Buffy (AI Strategic Assistant)
Date: July 23, 2026
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # Malaria_codesV2

# Tartarus full run: 19,913 compounds x 3 targets
TARTARUS_OUTPUT = (
    PROJECT_ROOT
    / 'Project2_Polypharmacology_MD_ValidationV2607'
    / 'results'
    / 'tartarus_output.csv'
)

# Target name mapping: Tartarus column -> canonical target name
# PDB IDs: 1syh=DHFR, 6y2f=ATP4, 4lde=CRT  (per BMAD_Q1 §3.8.1)
TARGET_MAP = {
    'score_1syh': 'PfDHFR',
    'score_6y2f': 'PfATP4',
    'score_4lde': 'PfCRT',
}

# RRS thresholds
BINDING_THRESHOLD = -7.0  # kcal/mol
MIN_TARGETS = 2  # minimum targets for polypharmacology


def load_tartarus():
    """Load Tartarus full run and rename columns to target names."""
    if not TARTARUS_OUTPUT.exists():
        print(f"ERROR: Tartarus output not found: {TARTARUS_OUTPUT}")
        return None

    df = pd.read_csv(TARTARUS_OUTPUT)
    print(f"Loaded Tartarus output: {len(df)} compounds, {len(df.columns)-1} targets")

    # Rename score columns to target names
    df = df.rename(columns=TARGET_MAP)

    # Replace 10000 (non-docked) with NaN
    for target in TARGET_MAP.values():
        if target in df.columns:
            df[target] = df[target].replace(10000.0, np.nan)
            n_valid = df[target].notna().sum()
            n_bound = (df[target] <= BINDING_THRESHOLD).sum()
            print(f"  {target}: {n_valid} docked, {n_bound} bound (< {BINDING_THRESHOLD})")

    return df


def compute_rrs(row, target_cols):
    """
    Compute Resistance Resilience Score for a compound.

    RRS = mean |docking score| across targets where compound binds.
    Higher RRS = more resistance-resilient.
    """
    scores = []
    for col in target_cols:
        if pd.notna(row[col]):
            score = row[col]
            if score <= BINDING_THRESHOLD:
                scores.append(abs(score))

    if len(scores) >= MIN_TARGETS:
        return np.mean(scores)
    else:
        return np.nan


def classify_rrs_class(rrs_score):
    """Classify compound into RRS classes based on score."""
    if pd.isna(rrs_score):
        return 'Unknown'
    if rrs_score >= 8.0:
        return 'A'
    elif rrs_score >= 7.0:
        return 'B'
    elif rrs_score >= 6.0:
        return 'C'
    else:
        return 'D'


def main():
    parser = argparse.ArgumentParser(description='P3 RRS Expansion')
    parser.add_argument('--start-idx', type=int, default=0)
    parser.add_argument('--end-idx', type=int, default=200)
    parser.add_argument('--output-dir', type=str,
                        default=str(PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607'
                                    / 'results' / 'p3_rrs_expansion'))
    parser.add_argument('--task-id', type=int, default=0)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== P3 RRS Expansion (Task {args.task_id}) ===")
    print(f"Processing indices: {args.start_idx} to {args.end_idx}")

    # Load data
    df = load_tartarus()
    if df is None or len(df) == 0:
        print("ERROR: No docking data available. Exiting.")
        sys.exit(1)

    target_cols = [v for v in TARGET_MAP.values() if v in df.columns]

    # Pre-filter to compounds with >= MIN_TARGETS targets bound.
    # NOTE (Aug 5, 2026): the previous >=1 pre-filter sliced mostly mono-target
    # binders, but compute_rrs requires MIN_TARGETS=2 -> n=77 plateau despite a
    # pool of 2051 polypharmacological compounds. Filter on MIN_TARGETS directly.
    has_binding = df[target_cols].apply(lambda row: (row <= BINDING_THRESHOLD).sum() >= MIN_TARGETS, axis=1)
    df_bound = df[has_binding].reset_index(drop=True)
    print(f"\nCompounds with >= {MIN_TARGETS} targets bound: {len(df_bound)}/{len(df)}")

    # Slice to task range
    end_idx = min(args.end_idx, len(df_bound))
    if args.start_idx >= len(df_bound):
        print(f"WARNING: start_idx {args.start_idx} >= {len(df_bound)} bound compounds. Nothing to process.")
        # Write empty result
        empty_df = pd.DataFrame(columns=['smiles'] + target_cols + ['rrs_score', 'rrs_class'])
        output_file = output_dir / f'p3_rrs_expansion_task{args.task_id}.csv'
        empty_df.to_csv(output_file, index=False)
        return

    task_df = df_bound.iloc[args.start_idx:end_idx].copy()
    print(f"Processing {len(task_df)} compounds (indices {args.start_idx}-{end_idx})")

    # Compute RRS
    task_df['rrs_score'] = task_df.apply(
        lambda row: compute_rrs(row, target_cols), axis=1
    )

    # Classify into RRS classes
    task_df['rrs_class'] = task_df['rrs_score'].apply(classify_rrs_class)

    # Save task results
    output_file = output_dir / f'p3_rrs_expansion_task{args.task_id}.csv'
    task_df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")

    # Summary statistics
    valid = task_df.dropna(subset=['rrs_score'])
    print(f"\nSummary (Task {args.task_id}):")
    print(f"  Valid compounds (>= {MIN_TARGETS} targets bound): "
          f"{len(valid)}/{len(task_df)}")
    if len(valid) > 0:
        print(f"  RRS mean: {valid['rrs_score'].mean():.3f}")
        print(f"  RRS std: {valid['rrs_score'].std():.3f}")

    class_counts = valid['rrs_class'].value_counts()
    print(f"  Class distribution:")
    for cls in ['A', 'B', 'C', 'D']:
        count = class_counts.get(cls, 0)
        print(f"    Class {cls}: {count}")

    print(f"\n=== Task {args.task_id} completed ===")


if __name__ == '__main__':
    main()
