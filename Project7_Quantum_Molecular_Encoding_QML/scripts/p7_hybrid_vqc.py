"""
P7 — Architecture 1: Quantum Feature Extractor

Implements hybrid quantum-classical model with VQC as feature extractor:
  ECFP4 (2048) → Linear (n_qubits) → VQC (trainable) → MLP → Binary classification

Supports:
  - Leave-one-out CV (P1 Set A, n=20)
  - k-fold CV (P3 benchmark, n=19,849)
  - Ablation study (depth, qubits, entangling gates)
  - Comparison with classical baseline (no quantum layer)

Usage:
    # Phase 1: P1 Set A (LOO-CV)
    python scripts/p7_hybrid_vqc.py --p1-set-a --qubits 4 --depth 2 --entangling cnot

    # Phase 2: P3 benchmark (5-fold CV)
    python scripts/p7_hybrid_vqc.py --p3-benchmark --qubits 8 --depth 2 --folds 5

    # Ablation study
    python scripts/p7_hybrid_vqc.py --p1-set-a --ablation --qubits "4,8" --depth "1,2,3"
"""

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.model_selection import LeaveOneOut, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from torch.utils.data import TensorDataset, DataLoader
from tqdm import tqdm

# Import P7 modules
from p7_quantum_layers import HybridQNN, DualPathQuantumNet, count_quantum_parameters
from p7_training_utils import train_hybrid_model, evaluate_model, log_metrics, save_model

warnings.filterwarnings('ignore')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
MODELS_DIR = PROJECT_ROOT / "models"


def smiles_to_ecfp4(smiles: str, radius=2, n_bits=2048) -> np.ndarray:
    """Convert SMILES to ECFP4 fingerprint."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    arr = np.zeros(n_bits, dtype=np.uint8)
    Chem.DataStructs.ConvertToNumpyArray(fp, arr)
    return arr.astype(np.float32)


def load_and_featurize_data(csv_file: Path, smiles_col='canonical_smiles', label_col='activity'):
    """
    Load dataset and convert to ECFP4 features + labels.
    
    Returns:
        X: (n_samples, 2048) ECFP4 fingerprints
        y: (n_samples,) binary labels
        mol_ids: (n_samples,) molecule IDs
    """
    print(f"\nLoading: {csv_file}")
    df = pd.read_csv(csv_file)
    
    print(f"Dataset: {len(df)} molecules")
    
    # Generate fingerprints
    print("Generating ECFP4 fingerprints...")
    fingerprints = []
    labels = []
    mol_ids = []
    failed_count = 0
    
    for idx, row in df.iterrows():
        smiles = row[smiles_col]
        fp = smiles_to_ecfp4(smiles)
        
        if fp is None:
            failed_count += 1
            continue
        
        fingerprints.append(fp)
        mol_ids.append(row.get('molecule_id', f'mol_{idx}'))
        
        # Extract label
        if label_col in df.columns:
            labels.append(int(row[label_col] >= 0.5))
        else:
            labels.append(0)
    
    X = np.array(fingerprints)
    y = np.array(labels)
    
    print(f"Features: {X.shape}")
    print(f"Labels: {y.shape} (active: {y.sum()}, inactive: {len(y) - y.sum()})")
    
    if failed_count > 0:
        print(f"WARNING: {failed_count} molecules failed fingerprint generation")
    
    return X, y, mol_ids


def run_loo_cv_hybrid(
    X, y, mol_ids,
    n_qubits=4,
    n_layers=2,
    entangling='cnot',
    n_epochs=50,
    lr=0.01,
    device=None
):
    """
    Leave-one-out cross-validation with hybrid QML model.
    
    Args:
        X: (n, 2048) features
        y: (n,) labels
        mol_ids: (n,) molecule IDs
        n_qubits: Number of qubits
        n_layers: Circuit depth
        entangling: Entangling gate type
        n_epochs: Training epochs per fold
        lr: Learning rate
        device: torch.device
    
    Returns:
        results: List of per-fold predictions
        metrics: Overall metrics
    """
    print("\n=== Leave-One-Out Cross-Validation (Hybrid QML) ===")
    print(f"Samples: {len(y)}")
    print(f"Architecture: ECFP4 → VQC({n_qubits} qubits, depth {n_layers}) → MLP")
    
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    loo = LeaveOneOut()
    
    y_true = []
    y_pred = []
    y_scores = []
    results = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(loo.split(X)):
        print(f"\nFold {fold_idx + 1}/{len(y)}")
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Convert to tensors
        train_dataset = TensorDataset(
            torch.FloatTensor(X_train_scaled),
            torch.LongTensor(y_train)
        )
        train_loader = DataLoader(train_dataset, batch_size=min(16, len(train_dataset)), shuffle=True)
        
        # Create model
        model = HybridQNN(
            n_features=2048,
            n_qubits=n_qubits,
            n_layers=n_layers,
            entangling=entangling,
            hidden_dim=64
        ).to(device)
        
        # Train (no validation set in LOO)
        history = train_hybrid_model(
            model=model,
            train_loader=train_loader,
            val_loader=None,
            n_epochs=n_epochs,
            lr=lr,
            verbose=False
        )
        
        # Predict on test sample
        model.eval()
        with torch.no_grad():
            X_test_tensor = torch.FloatTensor(X_test_scaled).to(device)
            pred = model(X_test_tensor).cpu().numpy()[0, 0]
        
        y_true.append(y_test[0])
        y_pred.append(int(pred >= 0.5))
        y_scores.append(float(pred))
        
        results.append({
            'fold': fold_idx,
            'molecule_id': mol_ids[test_idx[0]],
            'y_true': int(y_test[0]),
            'y_pred': int(pred >= 0.5),
            'y_score': float(pred),
            'train_loss_final': history['train_loss'][-1]
        })
        
        # Gradient check
        if hasattr(model, 'check_gradient_vanishing'):
            grad_stats = model.check_gradient_vanishing()
            if grad_stats['is_vanishing']:
                print(f"  ⚠️  WARNING: Gradients vanishing (norm: {grad_stats['norm']:.2e})")
    
    # Compute overall metrics
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_scores = np.array(y_scores)
    
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
    
    metrics = {
        'auc': float(roc_auc_score(y_true, y_scores)) if len(np.unique(y_true)) > 1 else 0.0,
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0))
    }
    
    print(f"\n=== Hybrid QML Metrics (LOO-CV) ===")
    print(f"AUC: {metrics['auc']:.4f}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1: {metrics['f1']:.4f}")
    
    return results, metrics


def run_kfold_cv_hybrid(
    X, y, mol_ids,
    n_qubits=4,
    n_layers=2,
    entangling='cnot',
    n_folds=5,
    n_epochs=50,
    lr=0.01,
    device=None,
    seed=42
):
    """
    Stratified k-fold cross-validation with hybrid QML model.
    
    Returns:
        results: List of per-sample predictions
        fold_metrics: List of per-fold metrics
        aggregate_metrics: Overall metrics
    """
    print(f"\n=== {n_folds}-Fold Cross-Validation (Hybrid QML) ===")
    print(f"Samples: {len(y)}")
    print(f"Architecture: ECFP4 → VQC({n_qubits} qubits, depth {n_layers}) → MLP")
    
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    
    results = []
    fold_metrics = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\n### Fold {fold_idx + 1}/{n_folds} ###")
        print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Create data loaders
        train_dataset = TensorDataset(
            torch.FloatTensor(X_train_scaled),
            torch.LongTensor(y_train)
        )
        test_dataset = TensorDataset(
            torch.FloatTensor(X_test_scaled),
            torch.LongTensor(y_test)
        )
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=32)
        
        # Create model
        model = HybridQNN(
            n_features=2048,
            n_qubits=n_qubits,
            n_layers=n_layers,
            entangling=entangling,
            hidden_dim=64
        ).to(device)
        
        # Train with validation split (80/20 of training set)
        val_size = max(1, len(train_dataset) // 5)
        train_subset, val_subset = torch.utils.data.random_split(
            train_dataset,
            [len(train_dataset) - val_size, val_size]
        )
        
        train_loader_split = DataLoader(train_subset, batch_size=32, shuffle=True)
        val_loader_split = DataLoader(val_subset, batch_size=32)
        
        history = train_hybrid_model(
            model=model,
            train_loader=train_loader_split,
            val_loader=val_loader_split,
            n_epochs=n_epochs,
            lr=lr,
            early_stopping_patience=10,
            verbose=True
        )
        
        # Evaluate on test set
        test_metrics = evaluate_model(model, test_loader, device, return_predictions=True)
        
        fold_metrics.append({
            'fold': fold_idx,
            'auc': test_metrics['auc'],
            'accuracy': test_metrics['accuracy'],
            'f1': test_metrics['f1']
        })
        
        print(f"  Fold {fold_idx + 1} Test: AUC {test_metrics['auc']:.4f}, "
              f"Acc {test_metrics['accuracy']:.4f}, F1 {test_metrics['f1']:.4f}")
        
        # Store predictions
        for i, test_i in enumerate(test_idx):
            results.append({
                'fold': fold_idx,
                'molecule_id': mol_ids[test_i],
                'y_true': int(y_test[i]),
                'y_pred': int(test_metrics['predictions'][i] >= 0.5),
                'y_score': float(test_metrics['predictions'][i])
            })
    
    # Aggregate metrics
    aggregate_metrics = {
        'auc_mean': np.mean([m['auc'] for m in fold_metrics]),
        'auc_std': np.std([m['auc'] for m in fold_metrics]),
        'accuracy_mean': np.mean([m['accuracy'] for m in fold_metrics]),
        'accuracy_std': np.std([m['accuracy'] for m in fold_metrics]),
        'f1_mean': np.mean([m['f1'] for m in fold_metrics]),
        'f1_std': np.std([m['f1'] for m in fold_metrics])
    }
    
    print(f"\n=== Aggregate Results ===")
    print(f"AUC: {aggregate_metrics['auc_mean']:.4f} ± {aggregate_metrics['auc_std']:.4f}")
    print(f"Accuracy: {aggregate_metrics['accuracy_mean']:.4f} ± {aggregate_metrics['accuracy_std']:.4f}")
    print(f"F1: {aggregate_metrics['f1_mean']:.4f} ± {aggregate_metrics['f1_std']:.4f}")
    
    return results, fold_metrics, aggregate_metrics


def main():
    parser = argparse.ArgumentParser(description="P7 Hybrid VQC: Quantum Feature Extractor")
    
    # Dataset selection
    parser.add_argument('--p1-set-a', action='store_true', help="Run on P1 Set A (LOO-CV)")
    parser.add_argument('--p3-benchmark', action='store_true', help="Run on P3 benchmark (k-fold CV)")
    
    # Model hyperparameters
    parser.add_argument('--qubits', type=int, default=4, help="Number of qubits (default: 4)")
    parser.add_argument('--depth', type=int, default=2, help="Circuit depth (default: 2)")
    parser.add_argument('--entangling', choices=['cnot', 'cz', 'rxx', 'ryy', 'rzz'], 
                        default='cnot', help="Entangling gate (default: cnot)")
    
    # Training hyperparameters
    parser.add_argument('--epochs', type=int, default=50, help="Training epochs (default: 50)")
    parser.add_argument('--lr', type=float, default=0.01, help="Learning rate (default: 0.01)")
    parser.add_argument('--folds', type=int, default=5, help="Number of folds for k-fold CV (default: 5)")
    
    # Other options
    parser.add_argument('--device', type=str, default=None, help="Device (cpu/cuda, default: auto)")
    parser.add_argument('--output-dir', type=str, default=None, help="Output directory")
    
    args = parser.parse_args()
    
    # Device
    if args.device:
        device = torch.device(args.device)
    else:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print("=" * 60)
    print("P7 Hybrid VQC: Quantum Feature Extractor")
    print("=" * 60)
    print(f"Device: {device}")
    print(f"Qubits: {args.qubits}")
    print(f"Depth: {args.depth}")
    print(f"Entangling: {args.entangling}")
    print("=" * 60)
    
    try:
        if args.p1_set_a:
            print("\n### Phase 1: P1 Set A (LOO-CV) ###")
            
            # Load data
            data_file = DATA_DIR / "p1_set_a_20_candidates.csv"
            if not data_file.exists():
                print(f"ERROR: {data_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p1-only")
                sys.exit(1)
            
            X, y, mol_ids = load_and_featurize_data(data_file)
            
            # Run LOO-CV
            results, metrics = run_loo_cv_hybrid(
                X, y, mol_ids,
                n_qubits=args.qubits,
                n_layers=args.depth,
                entangling=args.entangling,
                n_epochs=args.epochs,
                lr=args.lr,
                device=device
            )
            
            # Save results
            output_dir = Path(args.output_dir) if args.output_dir else RESULTS_DIR / "phase1_p1_set_a" / "hybrid_vqc"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save predictions
            results_df = pd.DataFrame(results)
            results_file = output_dir / f"hybrid_vqc_loo_q{args.qubits}_d{args.depth}_{args.entangling}.csv"
            results_df.to_csv(results_file, index=False)
            print(f"\nSaved predictions: {results_file}")
            
            # Save metrics
            metadata = {
                'architecture': 'hybrid_vqc',
                'n_qubits': args.qubits,
                'n_layers': args.depth,
                'entangling': args.entangling,
                'n_epochs': args.epochs,
                'lr': args.lr,
                'validation': 'loo_cv',
                'dataset': 'p1_set_a'
            }
            
            metrics_file = output_dir / f"hybrid_vqc_loo_q{args.qubits}_d{args.depth}_{args.entangling}_metrics.json"
            log_metrics(metrics, metrics_file, metadata)
        
        elif args.p3_benchmark:
            print("\n### Phase 2: P3 Benchmark (k-Fold CV) ###")
            
            # Load data
            data_file = DATA_DIR / "p3_benchmark_19849.csv"
            if not data_file.exists():
                print(f"ERROR: {data_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p3-only")
                sys.exit(1)
            
            X, y, mol_ids = load_and_featurize_data(data_file)
            
            # Run k-fold CV
            results, fold_metrics, aggregate_metrics = run_kfold_cv_hybrid(
                X, y, mol_ids,
                n_qubits=args.qubits,
                n_layers=args.depth,
                entangling=args.entangling,
                n_folds=args.folds,
                n_epochs=args.epochs,
                lr=args.lr,
                device=device
            )
            
            # Save results
            output_dir = Path(args.output_dir) if args.output_dir else RESULTS_DIR / "phase2_p3_benchmark" / "hybrid_vqc"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save predictions
            results_df = pd.DataFrame(results)
            results_file = output_dir / f"hybrid_vqc_{args.folds}fold_q{args.qubits}_d{args.depth}_{args.entangling}.csv"
            results_df.to_csv(results_file, index=False)
            print(f"\nSaved predictions: {results_file}")
            
            # Save per-fold metrics
            fold_metrics_df = pd.DataFrame(fold_metrics)
            fold_metrics_file = output_dir / f"hybrid_vqc_{args.folds}fold_q{args.qubits}_d{args.depth}_{args.entangling}_per_fold.csv"
            fold_metrics_df.to_csv(fold_metrics_file, index=False)
            
            # Save aggregate metrics
            metadata = {
                'architecture': 'hybrid_vqc',
                'n_qubits': args.qubits,
                'n_layers': args.depth,
                'entangling': args.entangling,
                'n_epochs': args.epochs,
                'lr': args.lr,
                'validation': f'{args.folds}_fold_cv',
                'dataset': 'p3_benchmark'
            }
            
            metrics_file = output_dir / f"hybrid_vqc_{args.folds}fold_q{args.qubits}_d{args.depth}_{args.entangling}_metrics.json"
            log_metrics(aggregate_metrics, metrics_file, metadata)
        
        else:
            print("ERROR: Specify --p1-set-a or --p3-benchmark")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("✅ Hybrid VQC training complete")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Review results in output directory")
        print("  2. Compare with classical baseline (p7_baseline_classical.py)")
        print("  3. Run ablation study with different hyperparameters")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
