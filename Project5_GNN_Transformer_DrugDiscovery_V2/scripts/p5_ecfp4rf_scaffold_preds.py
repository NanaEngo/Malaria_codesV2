#!/usr/bin/env python3
"""Archive per-fold ECFP4-RF test predictions on the frozen canonical scaffold split.

Reuses the exact ECFP4-RF recipe from the locked benchmark (see p5_butina_cluster.py):
  - ECFP4 Morgan r=2, 2048 bits
  - StandardScaler(fit on train) -> RandomForestClassifier(500 trees, n_jobs=-1,
    random_state=0, class_weight="balanced_subsample")
  - predict_proba(Xte)[:,1]
Frozen folds come from results/p5_splits_scaffold_5fold_seed{s}.npy (the canonical
scaffold split used everywhere in P5V2). Output per fold-seed:
  results/extended_campaign_20260825/training/canonical_scaffold/ECFP4-RF/pred_seed{s}_fold{k}.csv
  columns index,y,p  (index = panel row index, matching the GNN-native pred files).

Deterministic: RandomForestClassifier(random_state=0) + fixed folds -> reproducible.
"""
import argparse, hashlib, json, sys, time
import numpy as np
import pandas as pd
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import DataStructs
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score

ROOT = Path(__file__).resolve().parent.parent
P5_ROOT = ROOT / "results"
PANEL_PATH = P5_ROOT / "p5_canonical_panel.csv"
# Candidate frozen-split locations: V2 files/symlinks first, then the archived V1
# checkout (moved to _archives on 2026-08-29), which holds the originals.
_CAND_SPLIT_DIRS = [
    P5_ROOT,
    (Path(__file__).resolve().parent.parent.parent
     / "_archives"
     / "Project5_GNN_Transformer_DrugDiscovery_archived_20260829"
     / "results"),
]

def _split_path(seed: int):
    for d in _CAND_SPLIT_DIRS:
        p = d / f"p5_splits_scaffold_5fold_seed{seed}.npy"
        if p.is_file():
            return p
    raise FileNotFoundError(
        f"frozen scaffold split seed{seed} not found in: {_CAND_SPLIT_DIRS}"
    )
# Native-arm prediction dir of the extended campaign (matching GIN etc.)
OUT_DIR = P5_ROOT / "extended_campaign_20260825" / "training" / "canonical_scaffold" / "ECFP4-RF"

N_FOLDS = 5
SEEDS = [0, 1, 2, 3, 4]
ECFP4_RADIUS = 2
ECFP4_BITS = 2048
RF_TREES = 500


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ecfp4_features(smiles):
    gen = GetMorganGenerator(radius=ECFP4_RADIUS, fpSize=ECFP4_BITS)
    out = np.zeros((len(smiles), ECFP4_BITS), dtype=np.uint8)
    for i, s in enumerate(smiles):
        mol = Chem.MolFromSmiles(str(s))
        if mol is None:
            continue
        fp = gen.GetFingerprint(mol)
        arr = np.zeros((ECFP4_BITS,), dtype=np.uint8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        out[i] = arr
    return out


def run_ecfp4rf(X, y, train_idx, test_idx):
    # Canonical P5V2 ECFP4-RF: StandardScaler + RandomForestClassifier(500,
    # random_state=0) with default class_weight=None (see scripts/p5_sanity_ecfp4_rf.py
    # and manuscript Methods). This reproduces the canonical scaffold estimate 0.8300.
    sc = StandardScaler()
    Xtr = sc.fit_transform(X[train_idx].astype(np.float32))
    Xte = sc.transform(X[test_idx].astype(np.float32))
    clf = RandomForestClassifier(
        n_estimators=RF_TREES, n_jobs=8, random_state=0
    )
    clf.fit(Xtr, y[train_idx])
    p = clf.predict_proba(Xte)[:, 1]
    auc = float(roc_auc_score(y[test_idx], p))
    ap = float(average_precision_score(y[test_idx], p))
    bal = float(balanced_accuracy_score(y[test_idx], (p > 0.5).astype(int)))
    return p, auc, ap, bal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    ap.add_argument("--max-warn", action="store_true", help="(accepted for compat)")
    args = ap.parse_args()

    for s in args.seeds:
        _split_path(s)  # fail-closed: raise early if any seed split is unavailable
    panel = pd.read_csv(PANEL_PATH)
    n = len(panel)
    smiles = panel["smiles"].astype(str).tolist()
    y = panel["activity"].astype(int).to_numpy()
    print(f"panel rows: {n}, prevalence={y.mean():.4f}")

    print("computing ECFP4 ...")
    t0 = time.time()
    X = ecfp4_features(smiles)
    print(f"ECFP4 done in {time.time()-t0:.1f}s shape={X.shape}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"panel_n": n, "ecfp4_bits": ECFP4_BITS, "ecfp4_radius": ECFP4_RADIUS,
               "rf_trees": RF_TREES, "seeds": []}
    for s in args.seeds:
        splits = np.load(str(_split_path(s)), allow_pickle=True)
        seed_recs = []
        aucs = []
        for fk in range(N_FOLDS):
            # frozen split record: {"train": [...], "val": [...], "test": [...]}
            rec = splits[fk]
            train_idx = np.asarray(rec["train"])
            test_idx = np.asarray(rec["test"])
            p, auc, aps, bal = run_ecfp4rf(X, y, train_idx, test_idx)
            out_csv = OUT_DIR / f"pred_seed{s}_fold{fk}.csv"
            pd.DataFrame({"index": test_idx, "y": y[test_idx], "p": p}).to_csv(out_csv, index=False)
            aucs.append(auc)
            seed_recs.append({"fold": fk, "status": "OK", "auc": float(f"{auc:.4f}"),
                           "ap": float(f"{aps:.4f}"), "balanced_acc": float(f"{bal:.4f}"),
                           "n_test": int(len(test_idx))})
        summary["seeds"].append({"seed": s, "folds": seed_recs,
                                 "mean_auc": float(f"{np.mean(aucs):.4f}")})
        print(f"seed {s}: mean fold AUC = {np.mean(aucs):.4f}")

    # audit manifest
    first = OUT_DIR / "pred_seed0_fold0.csv"
    summary["out_dir"] = str(OUT_DIR)
    summary["pred_sha256_example"] = sha256(first) if first.exists() else None
    summary["panel_sha256"] = sha256(PANEL_PATH)
    man = OUT_DIR / "audit.json"
    with open(man, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"wrote {man}")
    print("mean seed-fold scaffold AUC =",
          round(np.mean([r["mean_auc"] for r in summary["seeds"]]), 4))


if __name__ == "__main__":
    main()