#!/usr/bin/env python3
"""
P5 — Sanity gate (v1-prep) + ECFP4-RF baselines (random & scaffold).

Re-runs ECFP4-RF on the frozen split (5 folds × 5 seeds) and asserts
random-split AUC ≈ 0.9475 ± 0.01 (P3 canonical ECFP4-RF value) using the SAME
descriptor and pipeline as P3. Validates the panel + split + pipeline plumbing
before GNN training, and produces the ECFP4-RF bar for both splits (H1 gate).

Usage:
    python scripts/p5_sanity_ecfp4_rf.py
    python scripts/p5_sanity_ecfp4_rf.py --split scaffold
"""

from __future__ import annotations

import argparse
import json
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
SEEDS = [0, 1, 2, 3, 4]

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


def run_split(split_type: str) -> tuple[list[float], list[float]]:
    """Return (per-fold mean AUC, per-fold std AUC) across 5 seeds."""
    panel = pd.read_csv(PANEL)
    smiles = panel["smiles"].tolist()
    y = panel["activity"].values
    X = ecfp4_matrix(smiles)
    print(f"ECFP4 matrix ({split_type}): {X.shape}")

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=500, n_jobs=8, random_state=0)),
    ])

    means, stds = [], []
    for seed in SEEDS:
        folds = np.load(P5_ROOT / "results" / f"p5_splits_{split_type}_5fold_seed{seed}.npy", allow_pickle=True)
        aucs = []
        for i, f in enumerate(folds):
            tr, te = f["train"], f["test"]
            pipe.fit(X[tr], y[tr])
            p = pipe.predict_proba(X[te])[:, 1]
            aucs.append(roc_auc_score(y[te], p))
        means.append(float(np.mean(aucs)))
        stds.append(float(np.std(aucs)))
        print(f"  seed {seed}: mean fold AUC = {means[-1]:.4f} ± {stds[-1]:.4f}")
    return means, stds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["random", "scaffold"], default="random")
    args = ap.parse_args()

    t0 = time.perf_counter()
    means, stds = run_split(args.split)

    overall = float(np.mean(means))
    print(f"\nECFP4-RF {args.split}: mean over 5 seeds = {overall:.4f} ± {np.std(means):.4f}")

    if args.split == "random":
        print(f"P3 reference ECFP4-RF = {REF_AUC}")
        if abs(overall - REF_AUC) > TOL:
            raise ValueError(
                f"Sanity gate FAILED: AUC {overall:.4f} deviates from P3 {REF_AUC} by "
                f"{abs(overall-REF_AUC):.4f} > {TOL}. Pipeline/panel mismatch — abort P5 training."
            )
        print("Sanity gate PASSED ✓ (within 0.01 of P3)")

    out = P5_ROOT / "results" / f"p5_ecfp4rf_{args.split}_baseline.json"
    json.dump({"split": args.split, "seed_means": means, "seed_stds": stds,
               "mean": overall, "std": float(np.std(means))}, open(out, "w"), indent=2)
    print(f"Saved {out}")
    print(f"Elapsed: {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()
