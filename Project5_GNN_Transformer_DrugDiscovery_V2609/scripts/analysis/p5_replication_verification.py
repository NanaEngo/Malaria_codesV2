#!/usr/bin/env python3
"""
P5 — Computational replication verification (Action 2, replication evidence).

Re-runs the ECFP4-RF baseline on the FROZEN splits (random and scaffold,
5 folds x 5 seeds each) from scratch and compares the resulting mean AUC
against the committed baseline JSONs within a documented tolerance.

This is an independent computational reproduction: same frozen splits, same
descriptor pipeline (RDKit Morgan r=2, 2048 bits), same RF configuration
(500 trees) as the committed baselines. Outputs a machine-readable verdict.

Usage:
    python scripts/p5_replication_verification.py
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

P5_ROOT = Path(__file__).resolve().parent.parent
SEEDS = [0, 1, 2, 3, 4]
TOL = 0.005  # documented tolerance on the mean over 25 replicates


def ecfp4_matrix(smiles_list: list[str]) -> np.ndarray:
    morgan = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(morgan.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tol", type=float, default=TOL)
    args = ap.parse_args()

    panel = pd.read_csv(P5_ROOT / "results" / "p5_canonical_panel.csv")
    smiles = panel["smiles"].tolist()
    y = panel["activity"].values
    X = ecfp4_matrix(smiles)
    print(f"Panel: {X.shape}, active fraction {y.mean():.3f}")

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=500, n_jobs=8, random_state=0)),
    ])

    verdict_rows = []
    all_pass = True
    for split in ["random", "scaffold"]:
        committed = json.load(open(P5_ROOT / "results" / f"p5_ecfp4rf_{split}_baseline.json"))
        seed_means = []
        for seed in SEEDS:
            folds = np.load(P5_ROOT / "results" / f"p5_splits_{split}_5fold_seed{seed}.npy", allow_pickle=True)
            aucs = []
            for f in folds:
                tr, te = f["train"], f["test"]
                pipe.fit(X[tr], y[tr])
                aucs.append(roc_auc_score(y[te], pipe.predict_proba(X[te])[:, 1]))
            seed_means.append(float(np.mean(aucs)))
        rep_mean = float(np.mean(seed_means))
        committed_mean = float(committed["mean"])
        dev = abs(rep_mean - committed_mean)
        ok = dev <= args.tol
        all_pass &= ok
        verdict_rows.append({
            "split": split, "replication_mean": round(rep_mean, 4),
            "committed_mean": round(committed_mean, 4),
            "deviation": round(dev, 4), "tolerance": args.tol, "pass": ok,
        })
        print(f"{split:8s} replication {rep_mean:.4f} vs committed {committed_mean:.4f} "
              f"(dev {dev:.4f} <= {args.tol}) -> {'PASS' if ok else 'FAIL'}")

    out = P5_ROOT / "results" / "p5_replication_verification.json"
    json.dump({
        "generated": "2026-08-08", "tolerance": args.tol,
        "protocol": "ECFP4-RF (RDKit Morgan r=2, 2048 bits; RF 500 trees; frozen splits; 5 folds x 5 seeds)",
        "verdict": "PASS" if all_pass else "FAIL",
        "rows": verdict_rows,
    }, open(out, "w"), indent=2)
    print(f"\nVERDICT: {'PASS' if all_pass else 'FAIL'} -> {out}")


if __name__ == "__main__":
    main()
