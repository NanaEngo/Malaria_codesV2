#!/usr/bin/env python3
"""
P5 — Sanity gate (v1-prep, documented in P5_DATA_ANALYSIS_REPORT.md §10).

Re-runs ECFP4-RF on the frozen random split (seed 0, fold 0) and asserts
AUC ≈ 0.9475 ± 0.01 (P3 canonical ECFP4-RF value) using the SAME descriptor
and pipeline as P3. This validates the panel + split + pipeline plumbing
before any GNN training.

Usage:
    python scripts/p5_sanity_ecfp4_rf.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem import DataStructs
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

P5_ROOT = Path(__file__).resolve().parent.parent
PANEL = P5_ROOT / "results" / "p5_canonical_panel.csv"
SPLIT = P5_ROOT / "results" / "p5_splits_random_5fold_seed0.npy"

REF_AUC = 0.9475
TOL = 0.01

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


def ecfp4_matrix(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


def main() -> None:
    t0 = time.perf_counter()
    panel = pd.read_csv(PANEL)
    folds = np.load(SPLIT, allow_pickle=True)
    fold = folds[0]

    smiles = panel["smiles"].tolist()
    y = panel["activity"].values

    X = ecfp4_matrix(smiles)
    print(f"ECFP4 matrix: {X.shape}")

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=500, n_jobs=32, random_state=0)),
    ])

    aucs = []
    for i, f in enumerate(folds):
        tr, te = f["train"], f["test"]
        pipe.fit(X[tr], y[tr])
        p = pipe.predict_proba(X[te])[:, 1]
        a = roc_auc_score(y[te], p)
        aucs.append(a)
        print(f"  fold {i}: test AUC = {a:.4f}")

    mean = float(np.mean(aucs))
    std = float(np.std(aucs))
    print(f"\nMean 5-fold AUC = {mean:.4f} ± {std:.4f}")
    print(f"P3 reference ECFP4-RF = {REF_AUC}")
    if abs(mean - REF_AUC) > TOL:
        raise ValueError(
            f"Sanity gate FAILED: AUC {mean:.4f} deviates from P3 {REF_AUC} by "
            f"{abs(mean-REF_AUC):.4f} > {TOL}. Pipeline/panel mismatch — abort P5 training."
        )
    print(f"Sanity gate PASSED ✓ (within {TOL} of P3)")
    print(f"Elapsed: {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()
