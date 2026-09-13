#!/usr/bin/env python3
"""Lightweight ECFP4 logistic-regression baseline for P5.

Uses the official frozen split directory supplied explicitly. Outputs are
written to a robustness directory and never overwrite canonical results.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import DataStructs, rdFingerprintGenerator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
PANEL = ROOT / "results" / "p5_canonical_panel.csv"
SEEDS = [0, 1, 2, 3, 4]
N_FOLDS = 5


def ecfp4_matrix(smiles: list[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    rows = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol is not None:
            DataStructs.ConvertToNumpyArray(gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.asarray(rows, dtype=np.float32)


def run(split: str, split_dir: Path, output_dir: Path, C: float) -> dict:
    panel = pd.read_csv(PANEL)
    X = ecfp4_matrix(panel["smiles"].astype(str).tolist())
    y = panel["activity"].to_numpy(dtype=int)
    rows = []
    seed_auc, seed_ap, seed_f1, seed_bacc = [], [], [], []
    for seed in SEEDS:
        folds = np.load(split_dir / f"p5_splits_{split}_5fold_seed{seed}.npy", allow_pickle=True)
        aucs, aps, f1s, baccs = [], [], [], []
        for fold, rec in enumerate(folds):
            tr, te = np.asarray(rec["train"], dtype=int), np.asarray(rec["test"], dtype=int)
            # Scaling is sparse-safe and makes the regularized linear baseline explicit.
            scaler = StandardScaler(with_mean=False)
            Xtr = scaler.fit_transform(X[tr])
            Xte = scaler.transform(X[te])
            clf = LogisticRegression(C=C, max_iter=1000, solver="liblinear", class_weight=None)
            clf.fit(Xtr, y[tr])
            p = clf.predict_proba(Xte)[:, 1]
            b = (p >= 0.5).astype(int)
            auc = roc_auc_score(y[te], p)
            ap = average_precision_score(y[te], p)
            f1 = f1_score(y[te], b)
            bacc = balanced_accuracy_score(y[te], b)
            aucs.append(auc); aps.append(ap); f1s.append(f1); baccs.append(bacc)
            rows.append({"model": f"Logistic-ECFP4-C{C:g}", "split": split,
                         "fold": fold, "seed": seed, "test_auc": auc,
                         "test_ap": ap, "test_f1": f1, "test_bacc": bacc})
        seed_auc.append(float(np.mean(aucs))); seed_ap.append(float(np.mean(aps)))
        seed_f1.append(float(np.mean(f1s))); seed_bacc.append(float(np.mean(baccs)))
        print(f"{split} seed {seed}: AUC={seed_auc[-1]:.4f} AP={seed_ap[-1]:.4f} "
              f"F1={seed_f1[-1]:.4f} bACC={seed_bacc[-1]:.4f}", flush=True)
    result = {
        "status": "COMPUTED",
        "model": f"Logistic-ECFP4-C{C:g}", "split": split, "C": C,
        "seed_means_auc": seed_auc, "seed_means_ap": seed_ap,
        "seed_means_f1": seed_f1, "seed_means_bacc": seed_bacc,
        "mean_auc": float(np.mean(seed_auc)), "std_auc": float(np.std(seed_auc)),
        "mean_ap": float(np.mean(seed_ap)), "mean_f1": float(np.mean(seed_f1)),
        "mean_bacc": float(np.mean(seed_bacc)), "n_fold_seed": len(rows),
        "protocol": "ECFP4 Morgan radius=2, 2048 bits; sparse scaling; liblinear logistic regression; official frozen splits",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"p5_logistic_ecfp4_C{C:g}_{split}"
    (output_dir / f"{stem}_baseline.json").write_text(json.dumps(result, indent=2))
    pd.DataFrame(rows).to_csv(output_dir / f"{stem}_results.csv", index=False)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["random", "scaffold", "both"], default="both")
    ap.add_argument("--split-dir", required=True)
    ap.add_argument("--output-dir", default=str(ROOT / "results" / "lightweight_robustness"))
    ap.add_argument("--C", type=float, default=1.0)
    args = ap.parse_args()
    t0 = time.perf_counter()
    splits = ["random", "scaffold"] if args.split == "both" else [args.split]
    for split in splits:
        r = run(split, Path(args.split_dir), Path(args.output_dir), args.C)
        print(f"{split}: mean AUC={r['mean_auc']:.4f} +/- {r['std_auc']:.4f}; AP={r['mean_ap']:.4f}")
    print(f"elapsed_seconds={time.perf_counter() - t0:.1f}")


if __name__ == "__main__":
    main()
