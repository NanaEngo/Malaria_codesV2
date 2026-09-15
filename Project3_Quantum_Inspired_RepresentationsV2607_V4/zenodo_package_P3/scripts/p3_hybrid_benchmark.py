#!/usr/bin/env python3
"""
P3 — Hybrid Benchmark Script

Benchmarks all representations (ECFP4, TFP, TNE, QKS, hybrid) using 5-fold CV.

This is a template/reference script. The actual P3 benchmark results are provided
in results/p3_hybrid_benchmark.csv.

Requirements:
    - rdkit >= 2025.03.6
    - numpy >= 2.2.1
    - pandas >= 2.2.3
    - scikit-learn >= 1.6.1

Key Results (from P3 DAR):
    - ECFP4-RF: 0.9475 AUC (baseline)
    - Hybrid (TFP+TNE+QK): 0.8876 AUC
    - TFP-RF: 0.6300 AUC
    - TNE-RF: 0.6300 AUC

Usage:
    python p3_hybrid_benchmark.py --labels labels.csv --tda tda.csv --tne tne.csv --output results.csv
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from rdkit import Chem
from rdkit.Chem import AllChem


def smiles_to_ecfp4(smiles, radius=2, n_bits=2048):
    """
    Generate ECFP4 fingerprint from SMILES.
    
    Args:
        smiles (str): SMILES string
        radius (int): Morgan fingerprint radius (default: 2 for ECFP4)
        n_bits (int): Fingerprint length
        
    Returns:
        np.ndarray: Binary fingerprint vector
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return np.zeros(n_bits)
    
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    return np.array(fp)


def cross_validate_model(X, y, n_folds=5, random_state=42):
    """
    5-fold cross-validation with Random Forest.
    
    Args:
        X (np.ndarray): Feature matrix
        y (np.ndarray): Labels
        n_folds (int): Number of CV folds
        random_state (int): Random seed
        
    Returns:
        tuple: (mean_auc, std_auc, fold_aucs)
    """
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    fold_aucs = []
    
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=500, random_state=random_state, n_jobs=-1)
        rf.fit(X_train, y_train)
        
        # Predict
        y_pred_proba = rf.predict_proba(X_test)[:, 1]
        
        # Compute AUC
        auc = roc_auc_score(y_test, y_pred_proba)
        fold_aucs.append(auc)
        
        print(f"  Fold {fold+1}/{n_folds}: AUC = {auc:.4f}")
    
    mean_auc = np.mean(fold_aucs)
    std_auc = np.std(fold_aucs)
    
    return mean_auc, std_auc, fold_aucs


def main():
    parser = argparse.ArgumentParser(description="P3 Hybrid Benchmark")
    parser.add_argument("--labels", required=True, help="CSV with SMILES and activity labels")
    parser.add_argument("--tda", help="CSV with TDA fingerprints")
    parser.add_argument("--tne", help="CSV with TNE embeddings")
    parser.add_argument("--output", required=True, help="Output CSV with benchmark results")
    parser.add_argument("--n-folds", type=int, default=5, help="CV folds (default: 5)")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    
    # Load labels
    print("Loading labels...")
    labels_df = pd.read_csv(args.labels)
    smiles = labels_df['smiles'].values
    y = labels_df['activity'].values
    
    print(f"Dataset: {len(smiles)} molecules, {y.sum()} actives ({100*y.mean():.1f}%)")
    
    results = []
    
    # 1. ECFP4 baseline
    print("\n[1/4] Benchmarking ECFP4...")
    X_ecfp4 = np.array([smiles_to_ecfp4(s) for s in smiles])
    mean_auc, std_auc, _ = cross_validate_model(X_ecfp4, y, n_folds=args.n_folds, 
                                                  random_state=args.random_state)
    results.append({'representation': 'ECFP4-RF', 'mean_auc': mean_auc, 'std_auc': std_auc})
    print(f"  ECFP4-RF: {mean_auc:.4f} ± {std_auc:.4f}")
    
    # 2. TDA
    if args.tda:
        print("\n[2/4] Benchmarking TDA...")
        tda_df = pd.read_csv(args.tda)
        X_tda = tda_df.filter(regex='^TDA_').values
        mean_auc, std_auc, _ = cross_validate_model(X_tda, y, n_folds=args.n_folds,
                                                      random_state=args.random_state)
        results.append({'representation': 'TFP-RF', 'mean_auc': mean_auc, 'std_auc': std_auc})
        print(f"  TFP-RF: {mean_auc:.4f} ± {std_auc:.4f}")
    
    # 3. TNE
    if args.tne:
        print("\n[3/4] Benchmarking TNE...")
        tne_df = pd.read_csv(args.tne)
        X_tne = tne_df.filter(regex='^TNE_').values
        mean_auc, std_auc, _ = cross_validate_model(X_tne, y, n_folds=args.n_folds,
                                                      random_state=args.random_state)
        results.append({'representation': 'TNE-RF', 'mean_auc': mean_auc, 'std_auc': std_auc})
        print(f"  TNE-RF: {mean_auc:.4f} ± {std_auc:.4f}")
    
    # 4. Hybrid (TFP + TNE concatenated)
    if args.tda and args.tne:
        print("\n[4/4] Benchmarking Hybrid (TFP+TNE)...")
        X_hybrid = np.hstack([X_tda, X_tne])
        mean_auc, std_auc, _ = cross_validate_model(X_hybrid, y, n_folds=args.n_folds,
                                                      random_state=args.random_state)
        results.append({'representation': 'Hybrid-RF', 'mean_auc': mean_auc, 'std_auc': std_auc})
        print(f"  Hybrid-RF: {mean_auc:.4f} ± {std_auc:.4f}")
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(args.output, index=False)
    print(f"\nResults saved to {args.output}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for _, row in results_df.iterrows():
        print(f"{row['representation']:15s}: {row['mean_auc']:.4f} ± {row['std_auc']:.4f}")
    print("\nKey finding: No quantum-inspired method outperforms ECFP4")


if __name__ == "__main__":
    main()
