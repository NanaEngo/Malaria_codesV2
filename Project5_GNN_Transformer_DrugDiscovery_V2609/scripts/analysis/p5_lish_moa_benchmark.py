#!/usr/bin/env python3
"""Leak-audited multi-label LISH-MoA benchmark for P5.

Input is the drug-level artifact produced by p5_lish_moa_prepare.py. The
benchmark reports mean column-wise log loss as primary, with macro AUPRC and
AUROC as secondary metrics. It intentionally uses per-label logistic models so
labels absent from a training fold are handled as constants instead of causing
silent fold failure.
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "lish_moa" / "lish_moa_drug_level.csv"
SEEDS = [0, 1, 2, 3, 4]


def ecfp4(smiles: list[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    out = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(str(smi))
        if mol is not None:
            ConvertToNumpyArray(gen.GetFingerprint(mol), out[i])
    return out


def scaffold_groups(smiles: list[str]) -> np.ndarray:
    from rdkit.Chem.Scaffolds import MurckoScaffold
    groups = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(str(smi))
        groups.append(MurckoScaffold.MurckoScaffoldSmiles(mol=mol) if mol else f"invalid:{smi}")
    return np.asarray(groups, dtype=object)


def folds(n: int, seed: int, split: str, smiles: list[str] | None) -> list[tuple[np.ndarray, np.ndarray]]:
    if split == "drug_grouped":
        kf = KFold(n_splits=5, shuffle=True, random_state=seed)
        return list(kf.split(np.arange(n)))
    if smiles is None:
        raise ValueError("scaffold split requires smiles")
    groups = scaffold_groups(smiles)
    unique = np.unique(groups)
    if len(unique) < 5:
        raise ValueError(f"Scaffold split requires at least 5 unique scaffolds; found {len(unique)}")
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    assignment = {g: i % 5 for i, g in enumerate(unique)}
    fold_id = np.asarray([assignment[g] for g in groups])
    return [(np.where(fold_id != k)[0], np.where(fold_id == k)[0]) for k in range(5)]


def fit_predict(Xtr: np.ndarray, Ytr: np.ndarray, Xte: np.ndarray) -> np.ndarray:
    pred = np.zeros((len(Xte), Ytr.shape[1]), dtype=np.float64)
    for j in range(Ytr.shape[1]):
        y = Ytr[:, j].astype(int)
        if len(np.unique(y)) < 2:
            pred[:, j] = float(y.mean())
            continue
        # Unweighted probabilities are retained for the primary log-loss and
        # calibration estimand. Class weighting would improve rare-label recall
        # at the cost of distorting probability calibration.
        model = LogisticRegression(max_iter=1000, class_weight=None, solver="liblinear")
        model.fit(Xtr, y)
        pred[:, j] = model.predict_proba(Xte)[:, 1]
    return np.clip(pred, 1e-7, 1 - 1e-7)


def expected_calibration_error(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total, ece = len(y), 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & (p < hi if hi < 1 else p <= hi)
        if mask.any():
            ece += float(mask.mean()) * abs(float(y[mask].mean()) - float(p[mask].mean()))
    return ece


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    losses, aps, aucs, briers, eces = [], [], [], [], []
    for j in range(y.shape[1]):
        losses.append(log_loss(y[:, j], p[:, j], labels=[0, 1]))
        briers.append(brier_score_loss(y[:, j], p[:, j]))
        eces.append(expected_calibration_error(y[:, j], p[:, j]))
        if len(np.unique(y[:, j])) > 1:
            aps.append(average_precision_score(y[:, j], p[:, j]))
            aucs.append(roc_auc_score(y[:, j], p[:, j]))
    return {"mean_columnwise_log_loss": float(np.mean(losses)),
            "macro_auprc": float(np.mean(aps)) if aps else None,
            "macro_auroc": float(np.mean(aucs)) if aucs else None,
            "mean_brier": float(np.mean(briers)),
            "mean_ece": float(np.mean(eces)),
            "n_labels_with_test_variation": len(aucs)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--features", choices=["phenotype", "structure", "both"], default="phenotype")
    ap.add_argument("--split", choices=["drug_grouped", "scaffold"], default="drug_grouped")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out-dir", type=Path, default=ROOT / "results" / "lish_moa")
    ap.add_argument("--exclude-controls", action="store_true",
                    help="Exclude drug rows with cp_type_trt_fraction == 0")
    args = ap.parse_args()
    df = pd.read_csv(args.input)
    if args.exclude_controls and "cp_type_trt_fraction" in df.columns:
        df = df.loc[df["cp_type_trt_fraction"] > 0].reset_index(drop=True)
    if args.limit:
        df = df.head(args.limit).copy()
    labels = [c for c in df.columns if c.startswith("moa_")]
    if not labels:
        raise ValueError("No moa_* columns found")
    smiles = df["smiles"].astype(str).tolist() if "smiles" in df.columns else None
    if args.features in ("structure", "both") and smiles is None:
        raise ValueError("Structure/both mode requires a mapped artifact with smiles")
    phenotype_cols = [c for c in df.columns if c.startswith(("g-", "c-", "cp_"))]
    if args.features == "phenotype":
        X = df[phenotype_cols].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(np.float32)
    elif args.features == "structure":
        X = ecfp4(smiles)
    else:
        Xp = df[phenotype_cols].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(np.float32)
        X = np.hstack([Xp, ecfp4(smiles)])
    Y = df[labels].astype(np.int8).to_numpy()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for seed in SEEDS:
        for fold, (tr, te) in enumerate(folds(len(df), seed, args.split, smiles)):
            scaler = StandardScaler()
            Xtr = scaler.fit_transform(X[tr])
            Xte = scaler.transform(X[te])
            pred = fit_predict(Xtr, Y[tr], Xte)
            rec = {"features": args.features, "split": args.split, "seed": seed,
                   "fold": fold, "n_train": len(tr), "n_test": len(te)}
            rec.update(metrics(Y[te], pred))
            records.append(rec)
    result = pd.DataFrame(records)
    stem = f"p5_lish_moa_{args.features}_{args.split}" + ("_no_controls" if args.exclude_controls else "")
    result.to_csv(args.out_dir / f"{stem}_folds.csv", index=False)
    summary = {"input": str(args.input), "features": args.features, "split": args.split,
               "exclude_controls": bool(args.exclude_controls), "n_drugs": len(df), "n_labels": len(labels),
               "mean_metrics": result[["mean_columnwise_log_loss", "macro_auprc", "macro_auroc", "mean_brier", "mean_ece"]].mean(numeric_only=True).to_dict(),
               "protocol": "5 seeds x 5 folds; drug-level aggregation; unweighted per-label logistic baseline",
               "interpretation": "MoA-associated prediction; not causal target engagement"}
    (args.out_dir / f"{stem}_report.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
