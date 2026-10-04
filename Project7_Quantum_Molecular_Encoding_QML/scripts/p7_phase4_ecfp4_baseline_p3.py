#!/usr/bin/env python3
"""
P7 Phase 4 — ECFP4-RBF-SVM baseline on P3 benchmark subsample.

Purpose
-------
Run the same ECFP4-RBF-SVM that is the P3 canonical baseline on the exact same
stratified subsample used by p7_phase4_p3_benchmark.py. This gives a local
within-experiment baseline so any AUC gap between QFE and ECFP4 is measured
on *identical data*, independent of the P3 canonical 0.9475 value (which was
computed on the full 19,849 molecules).

The P3 canonical baseline (AUC 0.9475 ± 0.0045) is the ultimate reference;
this script adds a local matched-subsample reference.

Design
------
- Subsample: same StratifiedShuffleSplit (seed=42, n=1000 by default)
- CV: StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
- Model: SVC(kernel='rbf', C=10.0, gamma='scale', probability=True)
- Hyperparameters: match P3 canonical as closely as possible
- Metric: ROC-AUC (primary), Brier score, accuracy

Outputs
-------
results/phase2_benchmark/
    ecfp4_rbf_p3sub<N>_cv5_results.csv     per-fold metrics
    ecfp4_rbf_p3sub<N>_cv5_summary.json    summary + provenance

Usage
-----
    python scripts/p7_phase4_ecfp4_baseline_p3.py \\
        --data data/p3_benchmark/p3_benchmark_19849.csv \\
        --output results/phase2_benchmark/ \\
        --n-sample 1000 \\
        --C 10.0 --gamma scale \\
        --seed 42
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.metrics import (
    accuracy_score, brier_score_loss, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit
from sklearn.svm import SVC


# ── Fingerprint helper ────────────────────────────────────────────────────────

def smiles_to_ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray:
    """ECFP4 Morgan fingerprint (radius 2) as a float32 bit-vector."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return np.zeros(n_bits, dtype=np.float32)
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    fp = gen.GetFingerprint(mol)
    arr = np.zeros(n_bits, dtype=np.float32)
    for idx in fp.GetOnBits():
        arr[idx] = 1.0
    return arr


def dataframe_sha256(df: pd.DataFrame) -> str:
    """Stable SHA-256 of a DataFrame sorted by mol_id."""
    buf = df.sort_values("mol_id").to_csv(index=False).encode("utf-8")
    return hashlib.sha256(buf).hexdigest()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="P7 Phase 4 — ECFP4-RBF-SVM baseline on P3 benchmark subsample"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/p3_benchmark/p3_benchmark_19849.csv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/phase2_benchmark/",
    )
    parser.add_argument("--n-sample", type=int, default=1000)
    parser.add_argument("--fp-size", type=int, default=2048)
    parser.add_argument("--C", type=float, default=10.0)
    parser.add_argument("--gamma", type=str, default="scale")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("P7 Phase 4 — ECFP4-RBF-SVM baseline (P3 subsample)")
    print("=" * 65)
    print(f"Subsample  : {args.n_sample} molecules")
    print(f"C          : {args.C}  gamma: {args.gamma}")
    print(f"Seed       : {args.seed}")

    # ── Load full P3 benchmark ────────────────────────────────────────────
    p3_path = Path(args.data)
    if not p3_path.exists():
        print(f"ERROR: P3 benchmark not found at {p3_path}")
        sys.exit(1)

    df_full = pd.read_csv(p3_path)
    print(f"\nFull P3 benchmark: {len(df_full)} molecules")

    # ── Stratified subsample (identical to p7_phase4_p3_benchmark.py) ─────
    n_sample = min(args.n_sample, len(df_full))
    splitter = StratifiedShuffleSplit(
        n_splits=1, test_size=n_sample, random_state=args.seed
    )
    _, sub_idx = next(
        splitter.split(df_full["SMILES"], df_full["activity_label"])
    )
    df_sub = df_full.iloc[sub_idx].reset_index(drop=True)

    n_active_sub = int((df_sub["activity_label"] == 1).sum())
    n_inactive_sub = int((df_sub["activity_label"] == 0).sum())
    sub_sha256 = dataframe_sha256(df_sub)

    print(f"\nSubsample: {len(df_sub)} molecules (seed={args.seed})")
    print(f"  Active  : {n_active_sub} ({n_active_sub / len(df_sub) * 100:.1f}%)")
    print(f"  Inactive: {n_inactive_sub} ({n_inactive_sub / len(df_sub) * 100:.1f}%)")
    print(f"  SHA-256 : {sub_sha256}")

    smiles_list = df_sub["SMILES"].tolist()
    labels = np.array(df_sub["activity_label"].tolist())

    # ── Compute ECFP4 fingerprints ────────────────────────────────────────
    print("\nComputing ECFP4 fingerprints...", end="", flush=True)
    fps = np.array([smiles_to_ecfp4(smi, args.fp_size) for smi in smiles_list])
    n_invalid = (fps.sum(axis=1) == 0).sum()
    print(f" done. Invalid SMILES: {n_invalid}")

    # ── 5-fold stratified CV ──────────────────────────────────────────────
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)

    fold_results = []
    total_t0 = time.time()

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(fps, labels)):
        print(f"\n── Fold {fold_idx + 1}/5 ──")
        print(
            f"  Train: {len(train_idx)} | Test: {len(test_idx)} | "
            f"Active (train): {labels[train_idx].sum()}"
        )

        X_train, y_train = fps[train_idx], labels[train_idx]
        X_test, y_test = fps[test_idx], labels[test_idx]

        fold_t0 = time.time()
        clf = SVC(
            kernel="rbf",
            C=args.C,
            gamma=args.gamma,
            probability=True,
            random_state=args.seed,
        )
        clf.fit(X_train, y_train)
        fold_elapsed = time.time() - fold_t0

        y_proba = clf.predict_proba(X_test)[:, 1]
        y_bin = (y_proba > 0.5).astype(int)

        try:
            auc = roc_auc_score(y_test, y_proba)
        except ValueError:
            auc = float("nan")

        brier = brier_score_loss(y_test, y_proba)
        acc = accuracy_score(y_test, y_bin)
        f1 = f1_score(y_test, y_bin, zero_division=0)
        prec = precision_score(y_test, y_bin, zero_division=0)
        rec = recall_score(y_test, y_bin, zero_division=0)

        print(
            f"  AUC: {auc:.4f}  Brier: {brier:.4f}  "
            f"Acc: {acc:.4f}  F1: {f1:.4f}  Time: {fold_elapsed:.1f}s"
        )

        fold_results.append(
            {
                "fold": fold_idx,
                "n_train": len(train_idx),
                "n_test": len(test_idx),
                "auc": auc,
                "brier_score": brier,
                "accuracy": acc,
                "f1": f1,
                "precision": prec,
                "recall": rec,
                "elapsed_sec": fold_elapsed,
            }
        )

    total_elapsed = time.time() - total_t0

    # ── Aggregate metrics ─────────────────────────────────────────────────
    aucs = [r["auc"] for r in fold_results if not np.isnan(r["auc"])]
    briers = [r["brier_score"] for r in fold_results]
    accs = [r["accuracy"] for r in fold_results]
    f1s = [r["f1"] for r in fold_results]

    mean_auc = float(np.mean(aucs)) if aucs else float("nan")
    std_auc = float(np.std(aucs)) if len(aucs) > 1 else float("nan")

    # ── P3 canonical baseline for comparison ─────────────────────────────
    p3_canonical = {"auc": 0.9475, "auc_std": 0.0045, "note": "full 19849 molecules"}

    # ── Save ──────────────────────────────────────────────────────────────
    result_tag = f"ecfp4_rbf_p3sub{n_sample}_cv5"

    df_results = pd.DataFrame(fold_results)
    results_path = out_dir / f"{result_tag}_results.csv"
    df_results.to_csv(results_path, index=False)

    summary = {
        "method": f"ECFP4-RBF-SVM (C={args.C}, gamma={args.gamma})",
        "phase": "Phase 4 — P3 benchmark baseline (stratified subsample)",
        "script": "scripts/p7_phase4_ecfp4_baseline_p3.py",
        "timestamp": pd.Timestamp.now().isoformat(),
        "execution": {
            "device": "cpu",
            "total_time_sec": total_elapsed,
        },
        "data": {
            "source": str(p3_path),
            "n_full": len(df_full),
            "n_subsample": n_sample,
            "n_active": n_active_sub,
            "n_inactive": n_inactive_sub,
            "subsample_sha256": sub_sha256,
            "seed": args.seed,
            "cv_strategy": "StratifiedKFold(n_splits=5, shuffle=True, seed=42)",
        },
        "hyperparameters": {
            "kernel": "rbf",
            "C": args.C,
            "gamma": args.gamma,
            "fp_size": args.fp_size,
        },
        "results": {
            "mean_auc": mean_auc,
            "std_auc": std_auc,
            "mean_brier": float(np.mean(briers)),
            "std_brier": float(np.std(briers)),
            "mean_accuracy": float(np.mean(accs)),
            "std_accuracy": float(np.std(accs)),
            "mean_f1": float(np.mean(f1s)),
            "std_f1": float(np.std(f1s)),
            "per_fold": fold_results,
        },
        "p3_canonical_reference": p3_canonical,
    }
    summary_path = out_dir / f"{result_tag}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    # ── Final report ──────────────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print(f"ECFP4-RBF-SVM — P3 subsample ({n_sample} mol) — 5-fold CV")
    print(f"{'=' * 65}")
    print(f"Total time : {total_elapsed:.1f}s")
    print(f"\n── Results (local subsample) ──")
    print(f"  AUC : {mean_auc:.4f} ± {std_auc:.4f}")
    print(f"  Brier: {np.mean(briers):.4f} ± {np.std(briers):.4f}")
    print(f"  Acc  : {np.mean(accs):.4f} ± {np.std(accs):.4f}")
    print(f"  F1   : {np.mean(f1s):.4f} ± {np.std(f1s):.4f}")
    print(
        f"\n── P3 canonical baseline (full 19849 mol): "
        f"AUC {p3_canonical['auc']:.4f} ± {p3_canonical['auc_std']:.4f} ──"
    )
    print(f"\n✓ Results saved to: {out_dir}/")
    print(f"  {results_path.name}")
    print(f"  {summary_path.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        print(f"\nERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
