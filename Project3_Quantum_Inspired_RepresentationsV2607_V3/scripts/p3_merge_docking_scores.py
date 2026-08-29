#!/usr/bin/env python3
"""
Merge Tartarus docking scores (P2) into the P3 canonical panel.

Creates: results/p3_docking_scores.csv with columns:
  smiles, PfDHFR, PfATP4, PfCRT, RRS_score, rrs_class
"""

import numpy as np
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Inputs
TARTARUS_CSV = PROJECT_ROOT / 'Project2_Polypharmacology_MD_ValidationV2607' / 'results' / 'tartarus_output.csv'
PANEL_CSV = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results' / 'p3_tda_fingerprints.csv'

# Output
OUT_CSV = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results' / 'p3_docking_scores.csv'

# Configuration
TARGET_MAP = {
    'score_1syh': 'PfDHFR',
    'score_6y2f': 'PfATP4',
    'score_4lde': 'PfCRT',
}

BINDING_THRESHOLD = -7.0
MIN_TARGETS = 2


def compute_rrs(row, target_cols):
    """RRS = mean |docking score| across targets where compound binds."""
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
    print("=" * 60)
    print("P3: Merge Tartarus docking scores into canonical panel")
    print("=" * 60)

    # Load Tartarus
    tart = pd.read_csv(TARTARUS_CSV)
    print(f"Tartarus: {len(tart)} compounds, cols: {list(tart.columns)}")

    # Rename and clean
    tart = tart.rename(columns=TARGET_MAP)
    for col in TARGET_MAP.values():
        if col in tart.columns:
            tart[col] = tart[col].replace(10000.0, np.nan)

    # Keep only relevant columns
    tart = tart[['smile'] + list(TARGET_MAP.values())].copy()

    # Load P3 canonical panel (TDA fingerprints CSV has all 19,849 smiles)
    panel = pd.read_csv(PANEL_CSV)
    print(f"Panel: {len(panel)} compounds, cols: {list(panel.columns)[:10]}...")

    # Normalize smiles column
    if 'smile' in tart.columns and 'smiles' in panel.columns:
        tart = tart.rename(columns={'smile': 'smiles'})

    # Merge
    merged = panel[['smiles']].merge(tart, on='smiles', how='left')
    print(f"Merged: {len(merged)} compounds")

    # Compute RRS
    target_cols = [c for c in TARGET_MAP.values() if c in merged.columns]
    merged['RRS_score'] = merged.apply(lambda r: compute_rrs(r, target_cols), axis=1)
    merged['rrs_class'] = merged['RRS_score'].apply(classify_rrs_class)

    # Summary
    valid = merged.dropna(subset=['RRS_score'])
    print(f"\nRRS valid (>= {MIN_TARGETS} targets bound): {len(valid)}/{len(merged)}")
    if len(valid) > 0:
        print(f"  RRS mean: {valid['RRS_score'].mean():.3f}")
        print(f"  Class distribution:")
        for cls in ['A', 'B', 'C', 'D']:
            count = (valid['rrs_class'] == cls).sum()
            print(f"    Class {cls}: {count}")
    print(f"  Unknown (bind <{MIN_TARGETS}): {merged['rrs_class'].eq('Unknown').sum()}")

    # Save
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_CSV, index=False)
    print(f"\nSaved: {OUT_CSV}")

    # Quick validation
    for col in target_cols:
        n_bound = (merged[col] <= BINDING_THRESHOLD).sum()
        n_docked = merged[col].notna().sum()
        print(f"  {col}: {n_docked} docked, {n_bound} bound (<{BINDING_THRESHOLD})")


if __name__ == '__main__':
    main()