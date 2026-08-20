#!/usr/bin/env python3
"""
P5 — kNN on ECFP4 baseline (random & scaffold). Reviewer-response metric (v5).

Tests the thesis "representation, not model": if a plain k-nearest-neighbours
classifier on ECFP4 matches or beats the GNN/fusion arms under scaffold split,
the ECFP4 advantage is a representation-level effect, not a tree-ensemble
artifact. Same frozen splits, same paired protocol (5 per-seed means, BH-FDR).

Usage:
    python scripts/p5_knn_ecfp4.py
    python scripts/p5_knn_ecfp4.py --split scaffold --k 10
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
from rdkit.Chem import DataStructs
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, balanced_accuracy_score
from scipy import stats

P5_ROOT = Path(__file__).resolve().parent.parent
PANEL = P5_ROOT / "results" / "p5_canonical_panel.csv"
SEEDS = [0, 1, 2, 3, 4]
K_DEFAULT = 5

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


def run_split(split_type: str, k: int) -> dict:
    panel = pd.read_csv(PANEL)
    smiles = panel["smiles"].tolist()
    y = panel["activity"].values
    X = ecfp4_matrix(smiles)
    print(f"ECFP4 matrix ({split_type}): {X.shape}")

    clf = KNeighborsClassifier(n_neighbors=k, n_jobs=-1, weights="distance",
                               metric="jaccard")

    per_seed_means, per_seed_ap, per_seed_f1, per_seed_bacc = [], [], [], []
    all_rows = []
    for seed in SEEDS:
        folds = np.load(P5_ROOT / "results" / f"p5_splits_{split_type}_5fold_seed{seed}.npy", allow_pickle=True)
        aucs, aps, f1s, baccs = [], [], [], []
        for i, f in enumerate(folds):
            tr, te = f["train"], f["test"]
            clf.fit(X[tr], y[tr])
            p = clf.predict_proba(X[te])[:, 1]
            b = (p >= 0.5).astype(int)
            auc = roc_auc_score(y[te], p)
            ap = average_precision_score(y[te], p)
            f1 = f1_score(y[te], b)
            bacc = balanced_accuracy_score(y[te], b)
            aucs.append(auc); aps.append(ap); f1s.append(f1); baccs.append(bacc)
            all_rows.append({"model": f"kNN-ECFP4-k{k}", "fold": i, "seed": seed,
                             "test_auc": auc, "test_ap": ap, "test_f1": f1, "test_bacc": bacc,
                             "split": split_type})
        per_seed_means.append(float(np.mean(aucs)))
        per_seed_ap.append(float(np.mean(aps)))
        per_seed_f1.append(float(np.mean(f1s)))
        per_seed_bacc.append(float(np.mean(baccs)))
        print(f"  seed {seed}: AUC {per_seed_means[-1]:.4f} AP {per_seed_ap[-1]:.4f} "
              f"F1 {per_seed_f1[-1]:.4f} bACC {per_seed_bacc[-1]:.4f}")

    result = {
        "model": f"kNN-ECFP4-k{k}", "split": split_type,
        "seed_means": per_seed_means, "seed_aps": per_seed_ap,
        "seed_f1s": per_seed_f1, "seed_baccs": per_seed_bacc,
        "mean_auc": float(np.mean(per_seed_means)),
        "std_auc": float(np.std(per_seed_means)),
        "mean_ap": float(np.mean(per_seed_ap)),
        "mean_f1": float(np.mean(per_seed_f1)),
        "mean_bacc": float(np.mean(per_seed_bacc)),
        "n": len(all_rows),
    }
    out_json = P5_ROOT / "results" / f"p5_knn_ecfp4_k{k}_{split_type}_baseline.json"
    json.dump(result, open(out_json, "w"), indent=2)
    out_csv = P5_ROOT / "results" / f"p5_knn_ecfp4_k{k}_{split_type}_results.csv"
    pd.DataFrame(all_rows).to_csv(out_csv, index=False)
    print(f"Saved {out_json} and {out_csv}")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["random", "scaffold"], default="scaffold")
    ap.add_argument("--k", type=int, default=K_DEFAULT)
    args = ap.parse_args()

    t0 = time.perf_counter()
    r = run_split(args.split, args.k)
    print(f"\nkNN-ECFP4 k={args.k} {args.split}: mean AUC = {r['mean_auc']:.4f} ± {r['std_auc']:.4f} "
          f"(AP {r['mean_ap']:.4f}, F1 {r['mean_f1']:.4f}, bACC {r['mean_bacc']:.4f})")
    print(f"Elapsed: {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()
