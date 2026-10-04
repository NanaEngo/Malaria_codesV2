#!/usr/bin/env python3
"""
P7 Phase 5 — ECFP4-RBF-SVM baseline on External Validation Set (scaffold split).

Scientific rationale
--------------------
Phase 4 used the P3 benchmark (a subset of the eos80ch asexual activity dataset)
with 5-fold stratified CV. Phase 5 tests generalization using the *non-P3* portion
of the same dataset (45,895 molecules not in P3) with a **scaffold split**:

  - Bemis-Murcko scaffolds computed via RDKit
  - Molecules sorted by scaffold frequency (rare scaffolds → test set first)
  - Test set: 20% of the 10K subsample; train set: 80%
  - This mimics the real-world scenario of predicting activity for novel
    chemical series not seen during training.

The 10K subsample is drawn with stratified random sampling (preserving class
ratio) from the 45,895 external-only pool, seeded at 42. SHA-256 of the
subsample is recorded before any model fitting.

Provenance rule (AGENTS.md §4)
-------------------------------
Subsample SHA-256 is computed and written to the summary JSON BEFORE any
training begins. This file is the canonical record for Phase 5 baseline.

Outputs
-------
results/phase3_scaffold/
    ecfp4_rbf_ext10k_scaffold_results.csv      per-molecule predictions
    ecfp4_rbf_ext10k_scaffold_summary.json     summary + provenance

Usage
-----
    python scripts/p7_phase5_ecfp4_baseline_ext.py \\
        --data65k  /path/to/eos80ch_malaria_final_activity.csv \\
        --p3bench  data/p3_benchmark/p3_benchmark_19849.csv \\
        --output   results/phase3_scaffold/ \\
        --n-sample 10000 \\
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
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import (
    accuracy_score, brier_score_loss, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.svm import SVC


# ── Fingerprint helper ────────────────────────────────────────────────────────

def smiles_to_ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray | None:
    """ECFP4 Morgan fingerprint as float32 bit-vector. Returns None on failure."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    fp = gen.GetFingerprint(mol)
    arr = np.zeros(n_bits, dtype=np.float32)
    for idx in fp.GetOnBits():
        arr[idx] = 1.0
    return arr


def get_murcko_scaffold(smiles: str) -> str:
    """Return the Bemis-Murcko generic scaffold SMILES. Empty string on failure."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ""
    try:
        scaffold = MurckoScaffold.GetScaffoldForMol(mol)
        return Chem.MolToSmiles(scaffold) if scaffold else ""
    except Exception:
        return ""


def dataframe_sha256(df: pd.DataFrame, smiles_col: str) -> str:
    """Stable SHA-256 of the subsample (sorted by mol_id or index)."""
    buf = df.sort_values(smiles_col).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(buf).hexdigest()


# ── Scaffold split ────────────────────────────────────────────────────────────

def scaffold_split(df: pd.DataFrame, test_frac: float = 0.2, seed: int = 42):
    """
    Bemis-Murcko scaffold split.

    Molecules are grouped by scaffold. Scaffolds are sorted by frequency
    (ascending) and assigned to the test set first (rarest scaffolds go to
    test), until the test fraction is reached. This ensures the test set
    contains more novel scaffolds than the training set.

    Returns
    -------
    train_idx, test_idx : lists of integer positions in df
    scaffold_stats      : dict with diagnostics
    """
    scaffolds = df["scaffold"].tolist()
    scaffold_to_indices: dict[str, list[int]] = {}
    for i, sc in enumerate(scaffolds):
        scaffold_to_indices.setdefault(sc, []).append(i)

    # Sort scaffolds by size ascending so small (rare) scaffolds go to test
    scaffold_sets = sorted(scaffold_to_indices.values(), key=len)

    n_test_target = int(len(df) * test_frac)
    test_idx, train_idx = [], []
    rng = np.random.default_rng(seed)

    for sc_indices in scaffold_sets:
        if len(test_idx) < n_test_target:
            test_idx.extend(sc_indices)
        else:
            train_idx.extend(sc_indices)

    # Shuffle within each split for reproducibility
    rng.shuffle(test_idx)
    rng.shuffle(train_idx)

    n_unique = len(scaffold_to_indices)
    test_scaffolds = set(df.iloc[test_idx]["scaffold"])
    train_scaffolds = set(df.iloc[train_idx]["scaffold"])
    n_scaffold_overlap = len(test_scaffolds & train_scaffolds)

    stats = {
        "n_unique_scaffolds": n_unique,
        "n_train": len(train_idx),
        "n_test": len(test_idx),
        "scaffold_overlap_between_train_test": n_scaffold_overlap,
        "pct_novel_scaffolds_in_test": round(
            (len(test_scaffolds) - n_scaffold_overlap) / max(len(test_scaffolds), 1) * 100, 2
        ),
    }
    return train_idx, test_idx, stats


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="P7 Phase 5 — ECFP4-RBF-SVM baseline on external scaffold split"
    )
    parser.add_argument(
        "--data65k",
        type=str,
        default=(
            "../Project3_Quantum_Inspired_RepresentationsV2607_V4/"
            "results/eos80ch_malaria_final_activity.csv"
        ),
        help="Path to eos80ch_malaria_final_activity.csv (65,856 rows)",
    )
    parser.add_argument(
        "--p3bench",
        type=str,
        default="data/p3_benchmark/p3_benchmark_19849.csv",
        help="Path to p3_benchmark_19849.csv (P3 overlap to exclude)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/phase3_scaffold/",
        help="Output directory",
    )
    parser.add_argument("--n-sample", type=int, default=10000, help="Subsample size (default 10000)")
    parser.add_argument("--C", type=float, default=10.0)
    parser.add_argument("--gamma", type=str, default="scale")
    parser.add_argument("--activity-threshold", type=float, default=0.5,
                        help="Threshold for binarizing asexual_blood_stage score")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    t_start = time.time()
    print("=" * 65)
    print("P7 Phase 5 — ECFP4-RBF-SVM baseline (external scaffold split)")
    print("=" * 65)
    print(f"Subsample  : {args.n_sample} molecules")
    print(f"C          : {args.C}  gamma: {args.gamma}")
    print(f"Threshold  : asexual_blood_stage > {args.activity_threshold}")
    print(f"Seed       : {args.seed}")

    # ── Load data ──────────────────────────────────────────────────────────────
    data65k_path = Path(args.data65k)
    p3_path      = Path(args.p3bench)
    out_dir      = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not data65k_path.exists():
        print(f"ERROR: 65K dataset not found at {data65k_path}")
        sys.exit(1)
    if not p3_path.exists():
        print(f"ERROR: P3 benchmark not found at {p3_path}")
        sys.exit(1)

    df65k = pd.read_csv(data65k_path)
    df_p3 = pd.read_csv(p3_path)

    print(f"\n65K dataset  : {len(df65k)} molecules")
    print(f"P3 benchmark : {len(df_p3)} molecules (to exclude)")

    # ── Exclude P3 molecules ───────────────────────────────────────────────────
    smiles_p3 = set(df_p3["SMILES"].dropna())
    df_ext = df65k[~df65k["input"].isin(smiles_p3)].copy()
    df_ext = df_ext.rename(columns={"input": "smiles"})
    df_ext["activity_label"] = (df_ext["asexual_blood_stage"] > args.activity_threshold).astype(int)
    df_ext = df_ext.dropna(subset=["smiles"]).reset_index(drop=True)

    print(f"External-only: {len(df_ext)} molecules (after P3 exclusion)")
    print(f"  Active  : {(df_ext['activity_label']==1).sum()} ({(df_ext['activity_label']==1).mean()*100:.1f}%)")
    print(f"  Inactive: {(df_ext['activity_label']==0).sum()} ({(df_ext['activity_label']==0).mean()*100:.1f}%)")

    # ── Stratified subsample ───────────────────────────────────────────────────
    rng = np.random.default_rng(args.seed)
    act_idx = df_ext[df_ext["activity_label"] == 1].index.tolist()
    inact_idx = df_ext[df_ext["activity_label"] == 0].index.tolist()

    n_active_target = int(args.n_sample * (df_ext["activity_label"] == 1).mean())
    n_inactive_target = args.n_sample - n_active_target

    sampled_act   = rng.choice(act_idx, size=min(n_active_target, len(act_idx)), replace=False)
    sampled_inact = rng.choice(inact_idx, size=min(n_inactive_target, len(inact_idx)), replace=False)
    sampled_idx   = np.concatenate([sampled_act, sampled_inact])
    rng.shuffle(sampled_idx)

    df_sub = df_ext.loc[sampled_idx].reset_index(drop=True)
    df_sub["mol_id"] = [f"EXT{i:05d}" for i in range(len(df_sub))]

    n_active_sub   = (df_sub["activity_label"] == 1).sum()
    n_inactive_sub = (df_sub["activity_label"] == 0).sum()
    sub_sha256 = dataframe_sha256(df_sub, "smiles")

    print(f"\nSubsample: {len(df_sub)} molecules (seed={args.seed})")
    print(f"  Active  : {n_active_sub} ({n_active_sub/len(df_sub)*100:.1f}%)")
    print(f"  Inactive: {n_inactive_sub} ({n_inactive_sub/len(df_sub)*100:.1f}%)")
    print(f"  SHA-256 : {sub_sha256}")

    # ── Compute Murcko scaffolds ───────────────────────────────────────────────
    print("\nComputing Murcko scaffolds...", flush=True)
    df_sub["scaffold"] = [get_murcko_scaffold(s) for s in df_sub["smiles"]]
    n_unique_scaffolds = df_sub["scaffold"].nunique()
    print(f"  Unique scaffolds: {n_unique_scaffolds}")

    # ── Scaffold split ─────────────────────────────────────────────────────────
    train_idx, test_idx, split_stats = scaffold_split(df_sub, test_frac=0.2, seed=args.seed)
    df_train = df_sub.iloc[train_idx]
    df_test  = df_sub.iloc[test_idx]

    print(f"\nScaffold split (80/20):")
    print(f"  Train: {len(df_train)} | Test: {len(df_test)}")
    print(f"  Unique scaffolds total : {split_stats['n_unique_scaffolds']}")
    print(f"  Scaffold overlap (train∩test): {split_stats['scaffold_overlap_between_train_test']}")
    print(f"  Novel scaffolds in test: {split_stats['pct_novel_scaffolds_in_test']:.1f}%")

    # ── ECFP4 fingerprints ─────────────────────────────────────────────────────
    print("\nComputing ECFP4 fingerprints...", end=" ", flush=True)
    train_fps, train_labels, train_invalid = [], [], 0
    for _, row in df_train.iterrows():
        fp = smiles_to_ecfp4(row["smiles"])
        if fp is None:
            train_invalid += 1
            continue
        train_fps.append(fp)
        train_labels.append(row["activity_label"])

    test_fps, test_labels, test_invalid = [], [], 0
    for _, row in df_test.iterrows():
        fp = smiles_to_ecfp4(row["smiles"])
        if fp is None:
            test_invalid += 1
            continue
        test_fps.append(fp)
        test_labels.append(row["activity_label"])

    X_train = np.array(train_fps)
    y_train = np.array(train_labels)
    X_test  = np.array(test_fps)
    y_test  = np.array(test_labels)
    print(f"done. Invalid SMILES: {train_invalid + test_invalid}")

    # ── Train SVM ──────────────────────────────────────────────────────────────
    print(f"\nTraining ECFP4-RBF-SVM (C={args.C}, gamma={args.gamma})...", end=" ", flush=True)
    t_fit = time.time()
    svm = SVC(kernel="rbf", C=args.C, gamma=args.gamma, probability=True, random_state=args.seed)
    svm.fit(X_train, y_train)
    t_fit = time.time() - t_fit
    print(f"done ({t_fit:.1f}s)")

    # ── Evaluate ───────────────────────────────────────────────────────────────
    probs = svm.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    auc       = roc_auc_score(y_test, probs)
    brier     = brier_score_loss(y_test, probs)
    acc       = accuracy_score(y_test, preds)
    f1        = f1_score(y_test, preds, zero_division=0)
    precision = precision_score(y_test, preds, zero_division=0)
    recall    = recall_score(y_test, preds, zero_division=0)

    elapsed = time.time() - t_start

    print("\n" + "=" * 65)
    print("ECFP4-RBF-SVM — External validation (scaffold split)")
    print("=" * 65)
    print(f"Total time : {elapsed:.1f}s")
    print(f"\n── Results ──")
    print(f"  AUC      : {auc:.4f}")
    print(f"  Brier    : {brier:.4f}")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  F1       : {f1:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall   : {recall:.4f}")

    # ── P4 canonical reference ─────────────────────────────────────────────────
    print(f"\n── P4 local ECFP4 baseline (5-fold CV, n=1000, P3): AUC 0.8693 ± 0.0265 ──")
    print(f"── P3 canonical ECFP4-RBF (full 19849 mol):         AUC 0.9475 ± 0.0045 ──")

    # ── Save per-molecule predictions ─────────────────────────────────────────
    test_smiles = [df_test.iloc[i]["smiles"] for i in range(len(y_test))]
    test_scaffolds = [df_test.iloc[i]["scaffold"] for i in range(len(y_test))]
    results_df = pd.DataFrame({
        "smiles": test_smiles,
        "scaffold": test_scaffolds,
        "y_true": y_test,
        "y_pred_prob": probs,
        "y_pred": preds,
    })
    results_path = out_dir / "ecfp4_rbf_ext10k_scaffold_results.csv"
    results_df.to_csv(results_path, index=False)

    # ── Save summary JSON ─────────────────────────────────────────────────────
    summary = {
        "method": f"ECFP4-RBF-SVM (C={args.C}, gamma={args.gamma})",
        "phase": "Phase 5 — external validation (scaffold split)",
        "script": "scripts/p7_phase5_ecfp4_baseline_ext.py",
        "timestamp": pd.Timestamp.now().isoformat(),
        "execution": {
            "device": "cpu",
            "total_time_sec": round(elapsed, 3),
        },
        "data": {
            "source_65k": str(data65k_path),
            "source_p3_excluded": str(p3_path),
            "n_ext_pool": len(df_ext),
            "n_subsample": len(df_sub),
            "n_active": int(n_active_sub),
            "n_inactive": int(n_inactive_sub),
            "subsample_sha256": sub_sha256,
            "seed": args.seed,
            "activity_threshold": args.activity_threshold,
            "split_strategy": "Bemis-Murcko scaffold split (20% test, rare scaffolds prioritised)",
        },
        "scaffold_split": split_stats,
        "hyperparameters": {
            "kernel": "rbf",
            "C": args.C,
            "gamma": args.gamma,
            "fp_size": 2048,
        },
        "results": {
            "auc": round(auc, 6),
            "brier_score": round(brier, 6),
            "accuracy": round(acc, 6),
            "f1": round(f1, 6),
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "n_train": len(X_train),
            "n_test": len(X_test),
        },
        "p4_phase_references": {
            "ECFP4-RBF local P3 subsample n1000 cv5": {"auc": 0.8693, "auc_std": 0.0265},
            "ECFP4-RBF P3 canonical full 19849": {"auc": 0.9475, "auc_std": 0.0045},
            "QFE 4q-d1-rzz P3 subsample n1000 cv5": {"auc": 0.8474, "auc_std": 0.0129},
        },
    }
    summary_path = out_dir / "ecfp4_rbf_ext10k_scaffold_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Results saved to: {out_dir}")
    print(f"  {results_path.name}")
    print(f"  {summary_path.name}")


if __name__ == "__main__":
    main()
