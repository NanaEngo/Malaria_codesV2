#!/usr/bin/env python3
"""P3 external LISH-MoA benchmark: ECFP4, TFP, TNE, and hybrid descriptors.

The input must be the structure-mapped drug-level artifact produced by the P5
LISH-MoA preparation script. This is a separate external experiment; it never
writes canonical P3 benchmark files.
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
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
P5_PREP = ROOT.parent / "Project5_GNN_Transformer_DrugDiscovery" / "scripts"
DEFAULT_INPUT = ROOT.parent / "Project5_GNN_Transformer_DrugDiscovery" / "results" / "lish_moa" / "lish_moa_structure_mapped.csv"
TFP_DIM, TNE_DIM = 78, 192
sys.path.insert(0, str(SCRIPTS))


def ecfp4(smiles: list[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    out = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(str(smi))
        if mol is not None:
            ConvertToNumpyArray(gen.GetFingerprint(mol), out[i])
    return out


def compute_tfp(smiles: list[str], n_jobs: int) -> tuple[np.ndarray, list[int]]:
    from joblib import Parallel, delayed
    from p3_tda_pipeline import process_molecule
    vals = Parallel(n_jobs=n_jobs)(delayed(process_molecule)(s, n_conf=1) for s in smiles)
    fail = [i for i, x in enumerate(vals) if x is None]
    X = np.vstack([np.zeros(TFP_DIM, np.float32) if x is None else x.astype(np.float32) for x in vals])
    return X, fail


def compute_tne(smiles: list[str], n_jobs: int, bond_dim: int = 8) -> tuple[np.ndarray, list[int]]:
    from joblib import Parallel, delayed
    from p3_tne_pipeline import smiles_to_tensor, tucker_compress
    def one(s):
        t = smiles_to_tensor(s)
        if t is None:
            return None
        try:
            return tucker_compress(t, bond_dim, use_gpu=False).astype(np.float32)
        except Exception:
            return None
    vals = Parallel(n_jobs=n_jobs, backend="threading")(delayed(one)(s) for s in smiles)
    fail = [i for i, x in enumerate(vals) if x is None]
    X = np.vstack([np.zeros(TNE_DIM, np.float32) if x is None else x for x in vals])
    return X, fail


def split_pairs(smiles: list[str], seed: int, split: str):
    if split == "drug_grouped":
        return list(KFold(5, shuffle=True, random_state=seed).split(np.arange(len(smiles))))
    groups = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(str(smi))
        groups.append(MurckoScaffold.MurckoScaffoldSmiles(mol=mol) if mol else f"invalid:{smi}")
    unique = np.unique(groups)
    if len(unique) < 5:
        raise ValueError(f"Scaffold split requires at least 5 unique scaffolds; found {len(unique)}")
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    assignment = {g: i % 5 for i, g in enumerate(unique)}
    fold_id = np.asarray([assignment[g] for g in groups])
    return [(np.where(fold_id != k)[0], np.where(fold_id == k)[0]) for k in range(5)]


def fit_predict(Xtr: np.ndarray, Ytr: np.ndarray, Xte: np.ndarray) -> np.ndarray:
    out = np.zeros((len(Xte), Ytr.shape[1]), dtype=float)
    for j in range(Ytr.shape[1]):
        y = Ytr[:, j]
        if len(np.unique(y)) < 2:
            out[:, j] = y.mean()
        else:
            m = LogisticRegression(max_iter=1000, class_weight=None, solver="liblinear")
            m.fit(Xtr, y)
            out[:, j] = m.predict_proba(Xte)[:, 1]
    return np.clip(out, 1e-7, 1 - 1e-7)


def score(y: np.ndarray, p: np.ndarray) -> dict:
    ll, ap, auc = [], [], []
    for j in range(y.shape[1]):
        ll.append(log_loss(y[:, j], p[:, j], labels=[0, 1]))
        if len(np.unique(y[:, j])) > 1:
            ap.append(average_precision_score(y[:, j], p[:, j]))
            auc.append(roc_auc_score(y[:, j], p[:, j]))
    return {"mean_columnwise_log_loss": float(np.mean(ll)),
            "macro_auprc": float(np.mean(ap)) if ap else None,
            "macro_auroc": float(np.mean(auc)) if auc else None,
            "n_variable_labels": len(auc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--n-jobs", type=int, default=8)
    ap.add_argument("--split", choices=["drug_grouped", "scaffold", "both"], default="both")
    ap.add_argument("--limit-drugs", type=int, default=None)
    ap.add_argument("--out-dir", type=Path, default=ROOT / "results" / "lish_moa")
    args = ap.parse_args()
    df = pd.read_csv(args.input)
    if args.limit_drugs:
        df = df.head(args.limit_drugs).copy()
    if "smiles" not in df.columns:
        raise ValueError("Input must contain audited canonical smiles")
    labels = [c for c in df.columns if c.startswith("moa_")]
    smiles = df.smiles.astype(str).tolist()
    Y = df[labels].astype(np.int8).to_numpy()
    t0 = time.perf_counter()
    Xs = {"ECFP4": ecfp4(smiles)}
    Xs["TFP"], tfp_fail = compute_tfp(smiles, args.n_jobs)
    Xs["TNE"], tne_fail = compute_tne(smiles, args.n_jobs)
    Xs["Hybrid"] = np.hstack([Xs["TFP"], Xs["TNE"]])
    args.out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    split_types = ["drug_grouped", "scaffold"] if args.split == "both" else [args.split]
    for split_type in split_types:
        for name, X in Xs.items():
            for seed in range(5):
                for fold, (tr, te) in enumerate(split_pairs(smiles, seed, split_type)):
                    scaler = StandardScaler()
                    pred = fit_predict(scaler.fit_transform(X[tr]), Y[tr], scaler.transform(X[te]))
                    rec = {"descriptor": name, "split": split_type, "seed": seed, "fold": fold,
                           "n_train": len(tr), "n_test": len(te)}
                    rec.update(score(Y[te], pred))
                    records.append(rec)
    result = pd.DataFrame(records)
    result.to_csv(args.out_dir / "p3_lish_moa_descriptor_folds.csv", index=False)
    report = {"input": str(args.input), "n_drugs": len(df), "n_labels": len(labels),
              "split_types": split_types,
              "n_tfp_failures": len(tfp_fail), "n_tne_failures": len(tne_fail),
              "failure_indices": {"TFP": tfp_fail, "TNE": tne_fail},
              "mean_metrics": result.groupby("descriptor").mean(numeric_only=True).to_dict(orient="index"),
              "protocol": "5 seeds x 5 drug-level/scaffold folds; unweighted per-label logistic baseline; zero-vector ITT failures",
              "qks_status": "NOT_COMPUTED_IN_THIS_DESCRIPTOR_RUN; requires a separately bounded kernel experiment",
              "elapsed_seconds": time.perf_counter() - t0}
    (args.out_dir / "p3_lish_moa_descriptor_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
