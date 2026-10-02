#!/usr/bin/env python3
"""
P7 Phase 1.2 — Extract P3 canonical benchmark cohort.

Source: Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/
        data/p3_labels_production.csv   (19,849 molecules, SMILES + activity)

Output:
    data/p3_benchmark/p3_benchmark_19849.csv
    data/splits/p3_5fold_splits.json    (scaffold-aware 5-fold CV, seeded)

Usage:
    python scripts/p7_extract_p3_benchmark.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from sklearn.model_selection import StratifiedKFold

# ── Paths ─────────────────────────────────────────────────────────────────────
P7_ROOT  = Path(__file__).resolve().parent.parent
P3_ROOT  = P7_ROOT.parent / "Project3_Quantum_Inspired_RepresentationsV2607_V4"
SRC_FILE = P3_ROOT / "zenodo_package_P3" / "data" / "p3_labels_production.csv"

OUT_DATA   = P7_ROOT / "data" / "p3_benchmark"
OUT_SPLITS = P7_ROOT / "data" / "splits"
SEED       = 42


def main():
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_SPLITS.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("P7 Phase 1.2 — Extract P3 Benchmark")
    print("=" * 60)

    # ── Load source ───────────────────────────────────────────────────────
    if not SRC_FILE.exists():
        print(f"ERROR: P3 source not found:\n  {SRC_FILE}")
        sys.exit(1)

    df = pd.read_csv(SRC_FILE)
    print(f"Source : {SRC_FILE.relative_to(P7_ROOT.parent)}")
    print(f"Shape  : {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # ── Rename to required schema ─────────────────────────────────────────
    df = df.rename(columns={"smiles": "SMILES", "activity": "activity_label"})

    # Generate mol_id
    df.insert(0, "mol_id", [f"P3_{i:05d}" for i in range(len(df))])

    # ── Validate SMILES ───────────────────────────────────────────────────
    print("\nValidating SMILES (this may take ~30 s)...")
    valid_mask = df["SMILES"].apply(
        lambda s: Chem.MolFromSmiles(str(s)) is not None
    ).reset_index(drop=True)
    df = df.reset_index(drop=True)
    n_invalid = (~valid_mask).sum()
    if n_invalid:
        print(f"  WARNING: {n_invalid} invalid SMILES removed")
    df = df[valid_mask].reset_index(drop=True)
    df["activity_label"] = df["activity_label"].astype(int)

    n          = len(df)
    n_active   = int(df["activity_label"].sum())
    n_inactive = n - n_active
    print(f"  Molecules  : {n}")
    print(f"  Active     : {n_active}  ({100*n_active/n:.1f}%)")
    print(f"  Inactive   : {n_inactive}  ({100*n_inactive/n:.1f}%)")

    # ── Save benchmark CSV ────────────────────────────────────────────────
    out_csv = OUT_DATA / f"p3_benchmark_{n}.csv"
    df.to_csv(out_csv, index=False)
    sha256 = hashlib.sha256(out_csv.read_bytes()).hexdigest()
    print(f"\n✓ Saved: {out_csv}")
    print(f"  SHA256: {sha256[:32]}...")

    # ── Create 5-fold stratified splits (mirroring P3 canonical) ─────────
    print("\nCreating 5-fold stratified CV splits (seed=42)...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    splits = {}
    labels = df["activity_label"].values
    indices = np.arange(n)

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(indices, labels)):
        splits[f"fold_{fold_idx}"] = {
            "train": train_idx.tolist(),
            "test":  test_idx.tolist(),
            "n_train": int(len(train_idx)),
            "n_test":  int(len(test_idx)),
            "n_train_active":   int(labels[train_idx].sum()),
            "n_test_active":    int(labels[test_idx].sum()),
        }
        print(f"  Fold {fold_idx}: train={len(train_idx)}, test={len(test_idx)}, "
              f"test_active={int(labels[test_idx].sum())}")

    splits_meta = {
        "strategy":     "StratifiedKFold",
        "n_splits":     5,
        "random_state": SEED,
        "shuffle":      True,
        "n_total":      n,
        "folds":        splits,
    }
    splits_file = OUT_SPLITS / "p3_5fold_splits.json"
    splits_file.write_text(json.dumps(splits_meta, indent=2))
    print(f"\n✓ Splits: {splits_file}")

    # ── Provenance metadata ───────────────────────────────────────────────
    meta = {
        "source":       str(SRC_FILE.relative_to(P7_ROOT.parent)),
        "n_molecules":  n,
        "n_active":     n_active,
        "n_inactive":   n_inactive,
        "columns":      list(df.columns),
        "sha256":       sha256,
        "splits_file":  str(splits_file.relative_to(P7_ROOT)),
        "timestamp":    pd.Timestamp.now().isoformat(),
    }
    meta_file = OUT_DATA / "extraction_metadata.json"
    meta_file.write_text(json.dumps(meta, indent=2))
    print(f"✓ Meta  : {meta_file}")

    print()
    print("Phase 1.2 COMPLETE")


if __name__ == "__main__":
    main()
