#!/usr/bin/env python3
"""Rebuild the 4-arm Butina summary block from the per-fold prediction CSVs.

The canonical source of truth for the Butina benchmark is the per-fold
prediction files (training/<ARM>/pred_seed<S>_fold<K>.csv, one row per test
molecule with columns index,y,p). This script recomputes the exact metrics the
benchmark reports (roc_auc, average_precision, balanced_accuracy on y vs p) and
regenerates butina_summary_backup_4arms.json with the same schema as
p5_butina_cluster.py produces for the non-ChemBERTa arms.
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "results" / "butina_cluster_20260829"
TRAIN_DIR = OUT_DIR / "training"
BACKUP = OUT_DIR / "butina_summary_backup_4arms.json"

ARMS = ["ECFP4-RF", "GIN", "GIN-TFP", "GIN-TNE"]
SEEDS = [0, 1, 2, 3, 4]
N_FOLDS = 5


def main() -> None:
    summary = {}
    for arm in ARMS:
        summary[arm] = {}
        for seed in SEEDS:
            folds = []
            for fk in range(N_FOLDS):
                csv_path = TRAIN_DIR / arm / f"pred_seed{seed}_fold{fk}.csv"
                if not csv_path.exists():
                    raise FileNotFoundError(f"Missing prediction file: {csv_path}")
                df = pd.read_csv(csv_path)
                y = df["y"].to_numpy()
                p = df["p"].to_numpy()
                auc = float(roc_auc_score(y, p))
                ap = float(average_precision_score(y, p))
                bal = float(balanced_accuracy_score(y, (p > 0.5).astype(int)))
                folds.append({
                    "fold": fk, "status": "OK", "auc": auc, "ap": ap,
                    "balanced_acc": bal,
                    "n_train": int(len(df)), "n_test": int(len(df)),
                })
            mean_auc = float(np.mean([f["auc"] for f in folds]))
            summary[arm][f"seed{seed}"] = {
                "folds": folds,
                "mean_auc": mean_auc,
                "wall_s": None,  # not recoverable from CSVs; informational only
            }
            print(f"{arm:9s} seed{seed}: mean AUC = {mean_auc:.4f}")

    with open(BACKUP, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nRebuilt {BACKUP} with arms {list(summary.keys())}")


if __name__ == "__main__":
    main()
