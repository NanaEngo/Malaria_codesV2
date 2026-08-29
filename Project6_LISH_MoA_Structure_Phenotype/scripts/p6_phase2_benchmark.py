#!/usr/bin/env python
"""Phase 2 leak-audited LISH-MoA benchmark for Project 6.

Reproduces the locked P5 protocol (per-label unweighted logistic regression,
mean column-wise log loss primary) on the exact mapped cohort, adding P6's
stricter leakage gates:

* folds are constructed over **collision groups** (identical canonical SMILES
  never cross train/test) or Murcko **scaffolds** (sensitivity);
* ``--split kfold`` reproduces the original drug-level KFold protocol for
  continuity with the locked phenotype reference (report section 2).

Inputs
------
* ``results/lish_moa/lish_moa_drug_level.csv`` (P5 artifact: drug_id +
  g-/c-/cp_ features + moa_* labels)
* ``data/mappings/drugid_to_smiles_v2_validated.csv`` (this project)

Outputs (under ``results/p6_phase2/``)
--------------------------------------
* ``p6_lish_moa_{features}_{split}_folds.csv``
* ``p6_lish_moa_{features}_{split}_report.json``
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

PROJ = Path(__file__).resolve().parents[1]
DRUG_LEVEL = PROJ / "results" / "lish_moa" / "lish_moa_drug_level.csv"
MAPPING = PROJ / "data" / "mappings" / "drugid_to_smiles_v2_validated.csv"
OUT_DIR = PROJ / "results" / "p6_phase2"
SEEDS = [0, 1, 2, 3, 4]
CLIP_LO, CLIP_HI = 1e-7, 1 - 1e-7


def ecfp4(smiles: list[str]) -> np.ndarray:
    """Compute Morgan radius-2 / 2048-bit fingerprints.

    Args:
        smiles: One canonical SMILES string per row; unparsable entries give
            an all-zero row.

    Returns:
        (n_rows, 2048) float32 fingerprint matrix.
    """
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    out = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(str(smi))
        if mol is not None:
            ConvertToNumpyArray(gen.GetFingerprint(mol), out[i])
    return out


def scaffold_groups(smiles: list[str]) -> np.ndarray:
    """Return the Murcko scaffold SMILES of each molecule.

    Args:
        smiles: Canonical SMILES strings.

    Returns:
        Object array of scaffold strings; unparsable rows get a unique marker.
    """
    from rdkit.Chem.Scaffolds import MurckoScaffold
    groups = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(str(smi))
        groups.append(MurckoScaffold.MurckoScaffoldSmiles(mol=mol) if mol else f"invalid:{smi}")
    return np.asarray(groups, dtype=object)


def group_folds(groups: np.ndarray, seed: int, n_splits: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    """Shuffle unique groups and deal them round-robin into folds.

    Args:
        groups: Group label per row (any hashable).
        seed: RNG seed controlling the group shuffle.
        n_splits: Number of folds.

    Returns:
        List of (train_idx, test_idx) index pairs, disjoint and exhaustive.

    Raises:
        ValueError: If fewer than ``n_splits`` unique groups exist.
    """
    unique = np.unique(groups)
    if len(unique) < n_splits:
        raise ValueError(f"Need >= {n_splits} unique groups; found {len(unique)}")
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    assignment = {g: i % n_splits for i, g in enumerate(unique)}
    fold_id = np.asarray([assignment[g] for g in groups])
    return [(np.where(fold_id != k)[0], np.where(fold_id == k)[0]) for k in range(n_splits)]


def make_folds(split: str, seed: int, n: int,
               cgroups: np.ndarray | None, scaffolds: np.ndarray | None):
    """Dispatch fold construction for the requested split type.

    Args:
        split: One of 'kfold', 'collision_group', 'scaffold'.
        seed: Seed for shuffling.
        n: Number of rows.
        cgroups: Collision-group array (required for collision_group).
        scaffolds: Scaffold array (required for scaffold).

    Returns:
        List of (train_idx, test_idx).

    Raises:
        ValueError: On an unknown split or missing group arrays.
    """
    if split == "kfold":
        kf = KFold(n_splits=5, shuffle=True, random_state=seed)
        return list(kf.split(np.arange(n)))
    if split == "collision_group":
        assert cgroups is not None
        return group_folds(cgroups, seed)
    if split == "scaffold":
        assert scaffolds is not None
        return group_folds(scaffolds, seed)
    raise ValueError(split)


def fit_predict(Xtr: np.ndarray, Ytr: np.ndarray, Xte: np.ndarray,
               model_kind: str = "logistic", seed: int = 42, n_jobs: int = 8) -> np.ndarray:
    """Fit one unweighted logistic regression per label and predict probabilities.

    Ponytail: sequential across labels; 4-core box doesn't gain from multiprocessing
    because RF inner n_jobs already parallelizes within a single label. Reduced
    max_iter=200 (vs 1000) to bound the per-fold wall time on small datasets.

    Args:
        Xtr: Training feature matrix.
        Ytr: Binary label matrix (n_train, n_labels).
        Xte: Test feature matrix.

    Returns:
        Clipped probability matrix (n_test, n_labels); labels absent from the
        training fold fall back to the constant training prevalence.
    """
    pred = np.zeros((len(Xte), Ytr.shape[1]), dtype=np.float64)
    for j in range(Ytr.shape[1]):
        y = Ytr[:, j].astype(int)
        if len(np.unique(y)) < 2:
            pred[:, j] = float(y.mean())
            continue
        if model_kind == "rf":
            model = RandomForestClassifier(n_estimators=300, class_weight=None,
                                           n_jobs=n_jobs, random_state=seed)
        else:
            # ponytail: lbfgs is ~4x faster than liblinear on this small dense dataset
            # (n_train=2630, n_feat<=2054); converges in <50 iter, max_iter=200 is safe.
            model = LogisticRegression(max_iter=200, class_weight=None, solver="lbfgs")
        model.fit(Xtr, y)
        pred[:, j] = model.predict_proba(Xte)[:, 1]
    return np.clip(pred, CLIP_LO, CLIP_HI)


def expected_calibration_error(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> float:
    """Compute ECE over equal-width probability bins.

    Args:
        y: Binary ground truth.
        p: Predicted probabilities.
        n_bins: Number of bins.

    Returns:
        Expected calibration error in [0, 1].
    """
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total, ece = len(y), 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & (p < hi if hi < 1 else p <= hi)
        if mask.any():
            ece += float(mask.mean()) * abs(float(y[mask].mean()) - float(p[mask].mean()))
    return ece


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    """Per-label metric block averaged across labels.

    Args:
        y: Binary label matrix.
        p: Probability matrix.

    Returns:
        Dict with mean_columnwise_log_loss (primary), macro_auprc, macro_auroc,
        mean_brier, mean_ece and n_labels_with_test_variation.
    """
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


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Optional argument vector override.

    Returns:
        Process exit code (0 on success).
    """
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--features", choices=["phenotype", "structure", "both"], default="phenotype",
                    help="Feature block to use (default: phenotype)")
    ap.add_argument("--split", choices=["kfold", "collision_group", "scaffold"], default="kfold",
                    help="Fold construction (kfold reproduces the locked P5 protocol)")
    ap.add_argument("--model", choices=["logistic", "rf"], default="logistic",
                    help="Per-label classifier (default: locked P5 logistic)")
    ap.add_argument("--jobs", type=int, default=8,
                     help="RandomForest n_jobs (default: 8)")
    ap.add_argument("--dump-predictions", action="store_true",
                     help="Write per-drug per-label test predictions under results/p6_phase2/predictions/<stem>/")
    args = ap.parse_args(argv)

    df = pd.read_csv(DRUG_LEVEL)
    mp = pd.read_csv(MAPPING)[["drug_id", "smiles_rdkit", "collision_group"]]
    before = len(df)
    df = df.merge(mp, on="drug_id", how="inner", validate="one_to_one").reset_index(drop=True)
    print(f"[data] merged {len(df)}/{before} drug rows")

    labels = [c for c in df.columns if c.startswith("moa_")]
    if not labels:
        raise ValueError("No moa_* columns found")
    smiles = df["smiles_rdkit"].astype(str).tolist()
    cgroups = df["collision_group"].to_numpy()
    scaffolds = scaffold_groups(smiles)

    pheno_cols = [c for c in df.columns if c.startswith(("g-", "c-", "cp_"))]
    if args.features == "phenotype":
        X = df[pheno_cols].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(np.float32)
    elif args.features == "structure":
        X = ecfp4(smiles)
    else:
        Xp = df[pheno_cols].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(np.float32)
        X = np.hstack([Xp, ecfp4(smiles)])
    Y = df[labels].astype(np.int8).to_numpy()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.model == "logistic" else f"_{args.model}"
    stem = f"p6_lish_moa_{args.features}_{args.split}{suffix}"
    pred_dir = OUT_DIR / "predictions" / stem if args.dump_predictions else None
    if pred_dir is not None:
        pred_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for seed in SEEDS:
        for fold, (tr, te) in enumerate(make_folds(args.split, seed, len(df), cgroups, scaffolds)):
            if args.model == "rf":
                # ponytail: trees are scale-invariant; scaler is logistic-only
                Xtr, Xte = X[tr], X[te]
            else:
                scaler = StandardScaler()
                Xtr = scaler.fit_transform(X[tr])
                Xte = scaler.transform(X[te])
            pred = fit_predict(Xtr, Y[tr], Xte, args.model, seed, args.jobs)
            if pred_dir is not None:
                # ponytail: per-drug per-label dump for calibration/QKS (fail-closed audit needs this)
                # Use dict-of-arrays + pd.concat (axis=1) once instead of 207 single-column inserts
                # which trigger DataFrame fragmentation and dominate wall time.
                cols = {"drug_id": df.iloc[te]["drug_id"].values}
                for j, lbl in enumerate(labels):
                    cols[f"{lbl}_true"] = Y[te, j]
                    cols[f"{lbl}_pred"] = pred[:, j]
                out = pd.DataFrame(cols)
                out.to_csv(pred_dir / f"seed{seed}_fold{fold}.csv", index=False)
            rec = {"features": args.features, "split": args.split, "seed": seed,
                    "fold": fold, "n_train": len(tr), "n_test": len(te)}
            rec.update(metrics(Y[te], pred))
            records.append(rec)
    result = pd.DataFrame(records)
    result.to_csv(OUT_DIR / f"{stem}_folds.csv", index=False)
    summary = {"input": str(DRUG_LEVEL), "mapping": str(MAPPING),
               "features": args.features, "split": args.split,
               "n_drugs": len(df), "n_labels": len(labels),
               "n_collision_groups": int(pd.Series(cgroups).nunique()),
               "mean_metrics": result[["mean_columnwise_log_loss", "macro_auprc", "macro_auroc",
                                       "mean_brier", "mean_ece"]].mean(numeric_only=True).to_dict(),
               "protocol": "5 seeds x 5 folds; drug-level aggregation; unweighted per-label logistic baseline",
               "interpretation": "MoA-associated prediction; not causal target engagement"}
    (OUT_DIR / f"{stem}_report.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
