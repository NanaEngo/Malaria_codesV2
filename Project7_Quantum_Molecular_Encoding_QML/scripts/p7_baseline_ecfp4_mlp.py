#!/usr/bin/env python3
"""
P7 Classical Baseline - ECFP4 + MLP

Classical baseline for comparison with quantum models.

Usage:
    python scripts/p7_baseline_ecfp4_mlp.py \\
        --data data/p1_set_a/p1_set_a_20_candidates.csv \\
        --output results/phase1_proof_of_concept/ \\
        --cv loo
"""
import argparse
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np
import json

# Machine learning
from sklearn.model_selection import LeaveOneOut, StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score

# Deep learning
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Chemistry
from rdkit import Chem
from rdkit.Chem import AllChem

class MoleculeDataset(Dataset):
    """PyTorch dataset for molecules"""
    
    def __init__(self, smiles_list, labels, fp_size=2048):
        self.smiles = smiles_list
        self.labels = labels
        self.fp_size = fp_size
        
        # Precompute fingerprints
        self.fingerprints = []
        for smi in smiles_list:
            fp = self.smiles_to_fp(smi)
            self.fingerprints.append(fp)
    
    def smiles_to_fp(self, smiles):
        """Convert SMILES to ECFP4 fingerprint"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return np.zeros(self.fp_size, dtype=np.float32)
        
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=self.fp_size)
        arr = np.zeros(self.fp_size, dtype=np.float32)
        AllChem.DataStructs.ConvertToNumpyArray(fp, arr)
        
        return arr
    
    def __len__(self):
        return len(self.smiles)
    
    def __getitem__(self, idx):
        fp = torch.FloatTensor(self.fingerprints[idx])
        label = torch.FloatTensor([self.labels[idx]])
        return fp, label

class ECFP4_MLP(nn.Module):
    """Classical MLP baseline"""
    
    def __init__(self, input_dim=2048, hidden_dims=[128, 64, 32]):
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)

def train_model(model, train_loader, val_loader, epochs=100, lr=0.001, device='cpu'):
    """Train the model"""
    
    model = model.to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    best_val_loss = float('inf')
    patience = 20
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        
        for fp, labels in train_loader:
            fp, labels = fp.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(fp)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for fp, labels in val_loader:
                fp, labels = fp.to(device), labels.to(device)
                outputs = model(fp)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break
    
    return model

def evaluate_model(model, data_loader, device='cpu'):
    """Evaluate model and return predictions"""
    
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for fp, labels in data_loader:
            fp = fp.to(device)
            outputs = model(fp)
            all_preds.extend(outputs.cpu().numpy().flatten())
            all_labels.extend(labels.numpy().flatten())
    
    return np.array(all_labels), np.array(all_preds)

def run_loo_cv(smiles, labels, output_dir, fp_size=2048, device='cpu'):
    """Run Leave-One-Out Cross-Validation"""
    
    print("\nRunning LOO Cross-Validation...")
    
    loo = LeaveOneOut()
    results = []
    
    for fold_idx, (train_idx, val_idx) in enumerate(loo.split(smiles)):
        print(f"  Fold {fold_idx + 1}/{len(smiles)}...", end='', flush=True)
        
        # Split data
        train_smiles = [smiles[i] for i in train_idx]
        train_labels = [labels[i] for i in train_idx]
        val_smiles = [smiles[i] for i in val_idx]
        val_labels = [labels[i] for i in val_idx]
        
        # Create datasets
        train_dataset = MoleculeDataset(train_smiles, train_labels, fp_size)
        val_dataset = MoleculeDataset(val_smiles, val_labels, fp_size)
        
        train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False)
        
        # Train model
        model = ECFP4_MLP(input_dim=fp_size)
        model = train_model(model, train_loader, val_loader, epochs=100, device=device)
        
        # Evaluate
        y_true, y_pred = evaluate_model(model, val_loader, device)
        
        results.append({
            'fold': fold_idx,
            'y_true': int(y_true[0]),
            'y_pred': float(y_pred[0])
        })
        
        print(f" pred={y_pred[0]:.3f}, true={y_true[0]}")
    
    # Compute overall metrics
    y_true = np.array([r['y_true'] for r in results])
    y_pred = np.array([r['y_pred'] for r in results])
    y_pred_binary = (y_pred > 0.5).astype(int)
    
    metrics = {
        'auc': float(roc_auc_score(y_true, y_pred)) if len(np.unique(y_true)) > 1 else np.nan,
        'accuracy': float(accuracy_score(y_true, y_pred_binary)),
        'f1': float(f1_score(y_true, y_pred_binary, zero_division=0)),
        'precision': float(precision_score(y_true, y_pred_binary, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred_binary, zero_division=0))
    }
    
    # Save results
    df_results = pd.DataFrame(results)
    results_file = output_dir / "ecfp4_mlp_loo_results.csv"
    df_results.to_csv(results_file, index=False)
    print(f"\n✓ Results saved to: {results_file}")
    
    return metrics, results

def main():
    parser = argparse.ArgumentParser(description="P7 ECFP4-MLP Baseline")
    parser.add_argument('--data', type=str, required=True, help='Input CSV file')
    parser.add_argument('--output', type=str, required=True, help='Output directory')
    parser.add_argument('--cv', type=str, default='loo', choices=['loo', '5fold'], help='CV strategy')
    parser.add_argument('--fp-size', type=int, default=2048, help='Fingerprint size')
    parser.add_argument('--device', type=str, default='cpu', choices=['cpu', 'cuda'], help='Device')
    
    args = parser.parse_args()
    
    # Setup
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    device = args.device if torch.cuda.is_available() or args.device == 'cpu' else 'cpu'
    print(f"Using device: {device}")
    
    # Load data
    print(f"\nLoading data from: {args.data}")
    df = pd.read_csv(args.data)
    print(f"Loaded {len(df)} molecules")
    
    smiles = df['SMILES'].tolist()
    labels = df['activity_label'].tolist()
    
    print(f"Active: {sum(labels)}, Inactive: {len(labels) - sum(labels)}")
    
    # Run CV
    start_time = time.time()
    
    if args.cv == 'loo':
        metrics, results = run_loo_cv(smiles, labels, output_dir, args.fp_size, device)
    else:
        raise NotImplementedError("5-fold CV not yet implemented")
    
    elapsed_time = time.time() - start_time
    
    # Summary
    summary = {
        'method': 'ECFP4-MLP',
        'cv_strategy': args.cv,
        'n_molecules': len(smiles),
        'n_active': sum(labels),
        'fp_size': args.fp_size,
        'device': device,
        'training_time_sec': elapsed_time,
        'metrics': metrics
    }
    
    summary_file = output_dir / "ecfp4_mlp_loo_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n" + "=" * 60)
    print("ECFP4-MLP Baseline Summary")
    print("=" * 60)
    print(f"Method: ECFP4-MLP")
    print(f"CV: {args.cv.upper()}")
    print(f"Molecules: {len(smiles)}")
    print(f"Training time: {elapsed_time:.1f}s")
    print(f"\nMetrics:")
    for key, value in metrics.items():
        print(f"  {key.upper()}: {value:.4f}")
    print("=" * 60)
    print(f"\n✓ Summary saved to: {summary_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
