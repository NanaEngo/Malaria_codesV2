"""
P7 — Baseline Classical Method (ECFP4-RBF SVM)

Implement classical baseline for comparison with quantum molecular encoding:
  - ECFP4 (Morgan) fingerprints (radius=2, 2048 bits)
  - RBF kernel SVM
  - Leave-one-out cross-validation (P1 Set A, n=20)
  - 5-fold stratified cross-validation (P3 benchmark, n=19,849)

Outputs:
  - results/phase1_p1_set_a/baseline_ecfp4_loo.csv
  - results/phase2_p3_benchmark/baseline_ecfp4_5fold.csv
  - Metrics: AUC-ROC, accuracy, F1, precision, recall

Usage:
    python scripts/p7_baseline_classical.py --p1-set-a
    python scripts/p7_baseline_classical.py --p3-benchmark
    python scripts/p7_baseline_classical.py --all
"""

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.svm import SVC
from sklearn.model_selection import LeaveOneOut, StratifiedKFold
from sklearn.metrics import (
    roc_auc_score, accuracy_score, f1_score,
    precision_score, recall_score, confusion_matrix
)
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"


def smiles_to_ecfp4(smiles: str, radius=2, n_bits=2048) -> np.ndarray:
    """
    Convert SMILES to ECFP4 (Morgan) fingerprint.
    
    Args:
        smiles: SMILES string
        radius: Morgan fingerprint radius (default: 2 for ECFP4)
        n_bits: Fingerprint length (default: 2048)
    
    Returns:
        NumPy array of fingerprint bits, or None if failed
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    arr = np.zeros(n_bits, dtype=np.uint8)
    Chem.DataStructs.ConvertToNumpyArray(fp, arr)
    return arr.astype(np.float32)


def prepare_features_labels(csv_file: Path, smiles_col='canonical_smiles', label_col='activity'):
    """
    Load dataset and convert to ECFP4 features + labels.
    
    Returns:
        X: (n_samples, 2048) ECFP4 fingerprints
        y: (n_samples,) binary labels
        mol_ids: (n_samples,) molecule IDs
        failed_indices: List of indices that failed fingerprint generation
    """
    print(f"\nLoading: {csv_file}")
    df = pd.read_csv(csv_file)
    
    print(f"Dataset: {len(df)} molecules")
    print(f"Columns: {list(df.columns)}")
    
    # Validate columns
    if smiles_col not in df.columns:
        raise ValueError(f"SMILES column '{smiles_col}' not found. Available: {list(df.columns)}")
    
    # Generate fingerprints
    print("Generating ECFP4 fingerprints...")
    fingerprints = []
    labels = []
    mol_ids = []
    failed_indices = []
    
    for idx, row in df.iterrows():
        smiles = row[smiles_col]
        fp = smiles_to_ecfp4(smiles)
        
        if fp is None:
            failed_indices.append(idx)
            continue
        
        fingerprints.append(fp)
        mol_ids.append(row.get('molecule_id', f'mol_{idx}'))
        
        # Extract label
        if label_col in df.columns:
            labels.append(int(row[label_col] >= 0.5))  # Threshold at 0.5
        else:
            labels.append(0)  # Default label if not present
    
    X = np.array(fingerprints)
    y = np.array(labels)
    
    print(f"Features: {X.shape}")
    print(f"Labels: {y.shape} (active: {y.sum()}, inactive: {len(y) - y.sum()})")
    
    if failed_indices:
        print(f"WARNING: {len(failed_indices)} molecules failed fingerprint generation")
    
    return X, y, mol_ids, failed_indices


def run_loo_cv(X, y, mol_ids):
    """
    Leave-one-out cross-validation with RBF-SVM.
    
    Suitable for small datasets (n=20).
    """
    print("\n=== Leave-One-Out Cross-Validation ===")
    print(f"Samples: {len(y)}")
    
    loo = LeaveOneOut()
    
    y_true = []
    y_pred = []
    y_scores = []
    results = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(loo.split(X)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train SVM with RBF kernel
        svm = SVC(kernel='rbf', gamma='scale', C=1.0, probability=True, random_state=42)
        svm.fit(X_train_scaled, y_train)
        
        # Predict
        pred = svm.predict(X_test_scaled)[0]
        score = svm.predict_proba(X_test_scaled)[0, 1]
        
        y_true.append(y_test[0])
        y_pred.append(pred)
        y_scores.append(score)
        
        results.append({
            'fold': fold_idx,
            'molecule_id': mol_ids[test_idx[0]],
            'y_true': int(y_test[0]),
            'y_pred': int(pred),
            'y_score': float(score)
        })
        
        if (fold_idx + 1) % 5 == 0:
            print(f"  Fold {fold_idx + 1}/{len(y)} complete")
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_scores = np.array(y_scores)
    
    # Compute metrics
    metrics = compute_metrics(y_true, y_pred, y_scores)
    
    return results, metrics


def run_kfold_cv(X, y, mol_ids, n_folds=5, seed=42):
    """
    Stratified k-fold cross-validation with RBF-SVM.
    
    Suitable for large datasets (n=19,849).
    """
    print(f"\n=== {n_folds}-Fold Stratified Cross-Validation ===")
    print(f"Samples: {len(y)}")
    
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    
    fold_results = []
    fold_metrics = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\nFold {fold_idx + 1}/{n_folds}")
        print(f"  Train: {len(train_idx)}, Test: {len(test_idx)}")
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train SVM with RBF kernel
        svm = SVC(kernel='rbf', gamma='scale', C=1.0, probability=True, random_state=42)
        svm.fit(X_train_scaled, y_train)
        
        # Predict
        y_pred = svm.predict(X_test_scaled)
        y_scores = svm.predict_proba(X_test_scaled)[:, 1]
        
        # Compute fold metrics
        metrics = compute_metrics(y_test, y_pred, y_scores)
        metrics['fold'] = fold_idx
        fold_metrics.append(metrics)
        
        print(f"  AUC: {metrics['auc']:.4f}, Acc: {metrics['accuracy']:.4f}, F1: {metrics['f1']:.4f}")
        
        # Store predictions
        for i, test_i in enumerate(test_idx):
            fold_results.append({
                'fold': fold_idx,
                'molecule_id': mol_ids[test_i],
                'y_true': int(y_test[i]),
                'y_pred': int(y_pred[i]),
                'y_score': float(y_scores[i])
            })
    
    # Aggregate metrics across folds
    aggregate_metrics = {
        'auc_mean': np.mean([m['auc'] for m in fold_metrics]),
        'auc_std': np.std([m['auc'] for m in fold_metrics]),
        'accuracy_mean': np.mean([m['accuracy'] for m in fold_metrics]),
        'accuracy_std': np.std([m['accuracy'] for m in fold_metrics]),
        'f1_mean': np.mean([m['f1'] for m in fold_metrics]),
        'f1_std': np.std([m['f1'] for m in fold_metrics]),
    }
    
    print(f"\n=== Aggregate Results ===")
    print(f"AUC: {aggregate_metrics['auc_mean']:.4f} ± {aggregate_metrics['auc_std']:.4f}")
    print(f"Accuracy: {aggregate_metrics['accuracy_mean']:.4f} ± {aggregate_metrics['accuracy_std']:.4f}")
    print(f"F1: {aggregate_metrics['f1_mean']:.4f} ± {aggregate_metrics['f1_std']:.4f}")
    
    return fold_results, fold_metrics, aggregate_metrics


def compute_metrics(y_true, y_pred, y_scores):
    """Compute classification metrics."""
    metrics = {
        'auc': float(roc_auc_score(y_true, y_scores)) if len(np.unique(y_true)) > 1 else 0.0,
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
    }
    
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        metrics['tn'] = int(cm[0, 0])
        metrics['fp'] = int(cm[0, 1])
        metrics['fn'] = int(cm[1, 0])
        metrics['tp'] = int(cm[1, 1])
    
    return metrics


def save_results(results_df, metrics, output_file, phase_name):
    """Save results and metrics to CSV and JSON."""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save predictions
    results_df.to_csv(output_file, index=False)
    print(f"\nSaved predictions: {output_file}")
    
    # Save metrics
    metrics_file = output_file.parent / f"{output_file.stem}_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'phase': phase_name,
            'method': 'ECFP4-RBF-SVM',
            'metrics': metrics
        }, f, indent=2)
    print(f"Saved metrics: {metrics_file}")


def main():
    parser = argparse.ArgumentParser(description="P7 Baseline: ECFP4-RBF SVM")
    parser.add_argument('--p1-set-a', action='store_true', help="Run on P1 Set A (LOO-CV)")
    parser.add_argument('--p3-benchmark', action='store_true', help="Run on P3 benchmark (5-fold CV)")
    parser.add_argument('--all', action='store_true', help="Run on both datasets")
    
    args = parser.parse_args()
    
    # Default to --all if no specific option
    if not any([args.all, args.p1_set_a, args.p3_benchmark]):
        args.all = True
    
    print("=" * 60)
    print("P7 Baseline: ECFP4-RBF SVM")
    print("=" * 60)
    
    try:
        if args.all or args.p1_set_a:
            print("\n### Phase 1: P1 Set A (LOO-CV) ###")
            
            csv_file = DATA_DIR / "p1_set_a_20_candidates.csv"
            if not csv_file.exists():
                print(f"ERROR: {csv_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p1-only")
                sys.exit(1)
            
            X, y, mol_ids, failed = prepare_features_labels(csv_file)
            results, metrics = run_loo_cv(X, y, mol_ids)
            
            results_df = pd.DataFrame(results)
            save_results(
                results_df,
                metrics,
                RESULTS_DIR / "phase1_p1_set_a" / "baseline_ecfp4_loo.csv",
                "Phase1_P1SetA_LOO"
            )
        
        if args.all or args.p3_benchmark:
            print("\n### Phase 2: P3 Benchmark (5-Fold CV) ###")
            
            csv_file = DATA_DIR / "p3_benchmark_19849.csv"
            if not csv_file.exists():
                print(f"ERROR: {csv_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p3-only")
                sys.exit(1)
            
            X, y, mol_ids, failed = prepare_features_labels(csv_file)
            results, fold_metrics, aggregate_metrics = run_kfold_cv(X, y, mol_ids, n_folds=5)
            
            results_df = pd.DataFrame(results)
            metrics_df = pd.DataFrame(fold_metrics)
            
            # Save predictions
            output_file = RESULTS_DIR / "phase2_p3_benchmark" / "baseline_ecfp4_5fold.csv"
            save_results(results_df, aggregate_metrics, output_file, "Phase2_P3Benchmark_5Fold")
            
            # Save per-fold metrics
            fold_metrics_file = output_file.parent / "baseline_ecfp4_5fold_per_fold_metrics.csv"
            metrics_df.to_csv(fold_metrics_file, index=False)
            print(f"Saved per-fold metrics: {fold_metrics_file}")
        
        print("\n" + "=" * 60)
        print("✅ Baseline complete")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Review results in results/phase*/ directories")
        print("  2. Run quantum encoding: python scripts/p7_quantum_circuits.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
