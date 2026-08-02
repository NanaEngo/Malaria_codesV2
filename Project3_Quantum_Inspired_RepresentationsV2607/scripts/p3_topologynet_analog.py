#!/usr/bin/env python3
"""
TopologyNet Analog: MLP classifier on PersStats (22 PH features).

TopologyNet (Cang & Wei 2017) uses PH features + deep CNN for protein-ligand
binding prediction. As a practical, installable analog, we use:
  - PersStats 22 features (same PH statistics as our SOTA benchmark)
  - Multi-Layer Perceptron (MLP) with 3 hidden layers
  - 5-fold stratified CV, class-weighted

This provides a fair neural-network comparison point for the PersStats RF
result (AUC=0.873) — testing whether a neural architecture extracts more
signal from the same 22 topological features.

Usage:
    python p3_topologynet_analog.py --n-mols 5000 --hidden 128 64 32
"""

import argparse
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results'

# PersStats 22 features: H0/H1/H2 (entropy, count, max_pers, mean_pers, birth_mean/std, death_mean/std, pers_q25/50/75)
# Exact feature names from p3_sota_benchmark.py
PERSSTATS_FEATURES = [
    'H0_entropy', 'H0_count', 'H0_max_pers', 'H0_mean_pers',
    'H0_birth_mean', 'H0_birth_std', 'H0_death_mean', 'H0_death_std',
    'H0_pers_q25', 'H0_pers_q50', 'H0_pers_q75',
    'H1_entropy', 'H1_count', 'H1_max_pers', 'H1_mean_pers',
    'H1_birth_mean', 'H1_birth_std', 'H1_death_mean', 'H1_death_std',
    'H1_pers_q25', 'H1_pers_q50', 'H1_pers_q75',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-mols', type=int, default=5000)
    parser.add_argument('--hidden', type=int, nargs='+', default=[128, 64, 32])
    parser.add_argument('--input', type=str, default=None)
    args = parser.parse_args()

    print("=" * 60)
    print(f"TopologyNet Analog: MLP on PersStats ({'+'.join(str(h) for h in args.hidden)})")
    print(f"Dataset: n={args.n_mols}")
    print("=" * 60)

    # Load labeled data
    if args.input:
        data_path = Path(args.input)
    else:
        data_path = RESULTS_DIR / 'p3_labels_production.csv'
        if not data_path.exists():
            data_path = RESULTS_DIR / 'p3_hybrid_benchmark.csv'
    
    df = pd.read_csv(data_path).head(args.n_mols)
    print(f"Loaded: {len(df)} rows")

    # Extract labels
    label_col = 'label' if 'label' in df.columns else ('activity' if 'activity' in df.columns else None)
    if label_col is None:
        print("ERROR: No label/activity column found.")
        raise SystemExit(1)

    y = df[label_col].astype(int).values

    # Extract or compute PersStats features
    # Check if PersStats columns exist in the data
    available_features = [f for f in PERSSTATS_FEATURES if f in df.columns]
    if len(available_features) >= 12:
        print(f"Using {len(available_features)} PersStats features from input data")
        X = df[available_features].fillna(0).values
    else:
        # Fallback: compute from TFP CSV if available
        tfp_path = RESULTS_DIR / 'p3_tda_fingerprints.csv'
        if tfp_path.exists():
            tfp_df = pd.read_csv(tfp_path).head(args.n_mols)
            available_features = [f for f in PERSSTATS_FEATURES if f in tfp_df.columns]
            if len(available_features) >= 12:
                print(f"Using {len(available_features)} PersStats features from TFP data")
                X = tfp_df[available_features].fillna(0).values
            else:
                print("ERROR: Insufficient PersStats features in TFP data")
                raise SystemExit(1)
        else:
            # Last resort: compute TFP on the fly
            print("Computing PersStats features on the fly...")
            from p3_tda_pipeline import process_molecule
            smiles_col = 'smiles' if 'smiles' in df.columns else ('input' if 'input' in df.columns else df.columns[0])
            smiles_list = df[smiles_col].head(args.n_mols).tolist()
            X_rows = []
            for i, smi in enumerate(smiles_list):
                if i % 500 == 0:
                    print(f"  {i}/{len(smiles_list)}...")
                tfp = process_molecule(smi)
                if tfp is not None and len(tfp) >= 33:  # 33 = 11*3 base features
                    X_rows.append(tfp[:len(PERSSTATS_FEATURES)])
                else:
                    X_rows.append([0.0] * len(PERSSTATS_FEATURES))
            X = np.array(X_rows)

    print(f"Feature matrix: {X.shape}")

    # 5-fold CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs, accs, f1s = [], [], []

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # Compute sample_weight to handle class imbalance (MLPClassifier lacks class_weight)
        n_pos = np.sum(y_train == 1)
        n_neg = np.sum(y_train == 0)
        sample_weight = np.ones(len(y_train))
        sample_weight[y_train == 1] = (n_pos + n_neg) / (2 * n_pos) if n_pos > 0 else 1
        sample_weight[y_train == 0] = (n_pos + n_neg) / (2 * n_neg) if n_neg > 0 else 1

        model = MLPClassifier(
            hidden_layer_sizes=tuple(args.hidden),
            activation='relu',
            solver='adam',
            alpha=0.001,
            batch_size=64,
            max_iter=200,
            early_stopping=True,
            validation_fraction=0.1,
            random_state=42,
        )
        model.fit(X_train, y_train, sample_weight=sample_weight)

        y_pred_prob = model.predict_proba(X_test)[:, 1]
        y_pred = (y_pred_prob > 0.5).astype(int)

        auc = roc_auc_score(y_test, y_pred_prob)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        aucs.append(auc)
        accs.append(acc)
        f1s.append(f1)
        print(f"Fold {fold+1}: AUC={auc:.4f}, Acc={acc:.4f}, F1={f1:.4f}")

    print(f"\n5-fold CV Results (MLP {args.hidden}, n={len(y)}, {len(available_features)} features):")
    print(f"  AUC: {np.mean(aucs):.4f} +/- {np.std(aucs):.4f}")
    print(f"  Acc: {np.mean(accs):.4f} +/- {np.std(accs):.4f}")
    print(f"  F1:  {np.mean(f1s):.4f} +/- {np.std(f1s):.4f}")

    # Comparison with RF baseline
    from sklearn.ensemble import RandomForestClassifier
    rf_aucs = []
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        rf = RandomForestClassifier(n_estimators=500, class_weight='balanced', random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_aucs.append(roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1]))

    print(f"\nReference: PersStats RF AUC: {np.mean(rf_aucs):.4f} +/- {np.std(rf_aucs):.4f}")
    print(f"MLP vs RF: {np.mean(aucs) - np.mean(rf_aucs):+.4f}")

    # Save
    results = {
        'method': f'PersStats_MLP_{"+".join(str(h) for h in args.hidden)}',
        'n_mols': X.shape[0],
        'n_features': X.shape[1],
        'auc_mean': round(np.mean(aucs), 4),
        'auc_std': round(np.std(aucs), 4),
        'rf_auc_mean': round(np.mean(rf_aucs), 4),
        'mlp_vs_rf_delta': round(np.mean(aucs) - np.mean(rf_aucs), 4),
    }
    out_csv = RESULTS_DIR / 'p3_topologynet_analog.csv'
    pd.DataFrame([results]).to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}")


if __name__ == '__main__':
    main()
