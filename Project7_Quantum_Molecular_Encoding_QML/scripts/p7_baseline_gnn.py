#!/usr/bin/env python3
"""
P7 Phase 2.2 — GIN Baseline (no PyTorch Geometric required).

Implements Graph Isomorphism Network (GIN, Xu et al. 2019) using
pure PyTorch + RDKit-derived adjacency and node features.

Architecture:
  SMILES → RDKit atom/bond features
         → 3-layer GIN (64-dim hidden)
         → Global mean pooling
         → MLP(64 → 32 → 1, Sigmoid)

Validation: Leave-One-Out CV

Usage:
    python scripts/p7_baseline_gnn.py \\
        --data data/p1_set_a/p1_set_a_17_candidates.csv \\
        --output results/phase1_proof_of_concept/ \\
        --cv loo
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from rdkit import Chem
from rdkit.Chem import Descriptors
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                              recall_score, roc_auc_score)
from sklearn.model_selection import LeaveOneOut

# ── Atom featurisation ────────────────────────────────────────────────────────
ATOM_TYPES   = ['C', 'N', 'O', 'S', 'F', 'Cl', 'Br', 'I', 'P', 'Other']
DEGREE_BINS  = [0, 1, 2, 3, 4, 5]
HYBRID_MAP   = {
    Chem.rdchem.HybridizationType.SP:  0,
    Chem.rdchem.HybridizationType.SP2: 1,
    Chem.rdchem.HybridizationType.SP3: 2,
}
ATOM_FEAT_DIM = len(ATOM_TYPES) + len(DEGREE_BINS) + len(HYBRID_MAP) + 1 + 1  # +aromatic +H_count


def one_hot(val, options, default_last=True):
    vec = [0] * len(options)
    try:
        vec[options.index(val)] = 1
    except ValueError:
        if default_last:
            vec[-1] = 1
    return vec


def atom_features(atom):
    symbol = atom.GetSymbol()
    atype  = one_hot(symbol, ATOM_TYPES)
    degree = one_hot(min(atom.GetDegree(), 5), DEGREE_BINS)
    hyb    = [0] * 3
    hyb[HYBRID_MAP.get(atom.GetHybridization(), 2)] = 1
    arom   = [int(atom.GetIsAromatic())]
    hcnt   = [atom.GetTotalNumHs() / 4.0]
    return atype + degree + hyb + arom + hcnt


def mol_to_graph(smiles):
    """Convert SMILES to (node_feat_matrix, adj_matrix)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, None

    n = mol.GetNumAtoms()
    X = np.zeros((n, ATOM_FEAT_DIM), dtype=np.float32)
    for i, atom in enumerate(mol.GetAtoms()):
        X[i] = atom_features(atom)

    A = np.zeros((n, n), dtype=np.float32)
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        A[i, j] = A[j, i] = 1.0
    # Self-loops for GIN
    A += np.eye(n, dtype=np.float32)

    return torch.FloatTensor(X), torch.FloatTensor(A)


# ── GIN Layer ─────────────────────────────────────────────────────────────────
class GINLayer(nn.Module):
    """GIN: h_v = MLP((1+ε)·h_v + Σ_{u∈N(v)} h_u)"""
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, out_dim),
            nn.BatchNorm1d(out_dim),
            nn.ReLU(),
            nn.Linear(out_dim, out_dim),
        )
        self.eps = nn.Parameter(torch.zeros(1))

    def forward(self, X, A):
        # X: (n, in_dim), A: (n, n) with self-loops
        agg  = A @ X                              # (n, in_dim)
        out  = self.mlp((1 + self.eps) * X + agg)
        return torch.relu(out)


class GINModel(nn.Module):
    def __init__(self, in_dim, hidden=64, n_layers=3, dropout=0.3):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(GINLayer(in_dim, hidden))
        for _ in range(n_layers - 1):
            self.layers.append(GINLayer(hidden, hidden))

        self.classifier = nn.Sequential(
            nn.Linear(hidden, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, X, A):
        h = X
        for layer in self.layers:
            h = layer(h, A)
        # Global mean pooling
        graph_emb = h.mean(dim=0, keepdim=True)   # (1, hidden)
        return self.classifier(graph_emb)           # (1, 1)


# ── Training ──────────────────────────────────────────────────────────────────
def train_fold(train_graphs, train_labels, val_graphs, val_labels,
               device, epochs=150, lr=5e-4, patience=25):
    in_dim = train_graphs[0][0].shape[1]
    model  = GINModel(in_dim=in_dim).to(device)
    optim_ = optim.Adam(model.parameters(), lr=lr)
    crit   = nn.BCELoss()

    best_loss = float('inf')
    patience_ = 0
    best_state = None

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for (X, A), y in zip(train_graphs, train_labels):
            X, A = X.to(device), A.to(device)
            y_t  = torch.FloatTensor([[y]]).to(device)
            optim_.zero_grad()
            pred = model(X, A)
            loss = crit(pred, y_t)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim_.step()
            total_loss += loss.item()

        # Validation
        model.eval()
        with torch.no_grad():
            val_loss = 0.0
            for (X, A), y in zip(val_graphs, val_labels):
                X, A = X.to(device), A.to(device)
                y_t  = torch.FloatTensor([[y]]).to(device)
                pred = model(X, A)
                val_loss += crit(pred, y_t).item()

        if val_loss < best_loss:
            best_loss  = val_loss
            patience_  = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_ += 1
            if patience_ >= patience:
                break

    if best_state:
        model.load_state_dict(best_state)
    return model


def predict(model, X, A, device):
    model.eval()
    with torch.no_grad():
        X, A = X.to(device), A.to(device)
        return model(X, A).item()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="P7 GIN Baseline (no PyG required)")
    parser.add_argument('--data',   type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--cv',     type=str, default='loo', choices=['loo'])
    parser.add_argument('--device', type=str, default='cpu')
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    device  = args.device if torch.cuda.is_available() or args.device == 'cpu' else 'cpu'

    # ── Load data ─────────────────────────────────────────────────────────
    df = pd.read_csv(args.data)
    print(f"Loaded {len(df)} molecules")
    smiles_list = df['SMILES'].tolist()
    labels      = df['activity_label'].tolist()
    print(f"Active: {sum(labels)}, Inactive: {len(labels) - sum(labels)}")

    # ── Build graphs ──────────────────────────────────────────────────────
    graphs = []
    valid_idx = []
    for i, smi in enumerate(smiles_list):
        X, A = mol_to_graph(smi)
        if X is not None:
            graphs.append((X, A))
            valid_idx.append(i)
        else:
            print(f"  WARNING: could not parse SMILES at index {i}, skipping")

    labels = [labels[i] for i in valid_idx]
    print(f"Valid graphs: {len(graphs)}")

    # ── LOO-CV ────────────────────────────────────────────────────────────
    print("\nRunning LOO Cross-Validation...")
    loo     = LeaveOneOut()
    results = []
    t0      = time.time()

    for fold, (train_idx, val_idx) in enumerate(loo.split(graphs)):
        print(f"  Fold {fold + 1}/{len(graphs)}...", end='', flush=True)
        train_g = [graphs[i] for i in train_idx]
        train_y = [labels[i] for i in train_idx]
        val_g   = [graphs[i] for i in val_idx]
        val_y   = [labels[i] for i in val_idx]

        model = train_fold(train_g, train_y, val_g, val_y, device)
        X, A  = val_g[0]
        pred  = predict(model, X, A, device)

        results.append({
            'fold':   fold,
            'y_true': int(val_y[0]),
            'y_pred': float(pred),
        })
        print(f" pred={pred:.3f}, true={val_y[0]}")

    elapsed = time.time() - t0

    # ── Metrics ───────────────────────────────────────────────────────────
    y_true = np.array([r['y_true'] for r in results])
    y_pred = np.array([r['y_pred'] for r in results])
    y_bin  = (y_pred > 0.5).astype(int)

    metrics = {
        'auc':       float(roc_auc_score(y_true, y_pred)) if len(np.unique(y_true)) > 1 else float('nan'),
        'accuracy':  float(accuracy_score(y_true, y_bin)),
        'f1':        float(f1_score(y_true, y_bin, zero_division=0)),
        'precision': float(precision_score(y_true, y_bin, zero_division=0)),
        'recall':    float(recall_score(y_true, y_bin, zero_division=0)),
    }

    # ── Save ──────────────────────────────────────────────────────────────
    pd.DataFrame(results).to_csv(out_dir / "gnn_loo_results.csv", index=False)

    summary = {
        'method':           'GIN-3layer',
        'cv_strategy':      'loo',
        'n_molecules':      len(graphs),
        'n_active':         sum(labels),
        'training_time_sec': elapsed,
        'metrics':          metrics,
    }
    (out_dir / "gnn_loo_summary.json").write_text(json.dumps(summary, indent=2))

    print(f"\n{'='*60}")
    print("GIN Baseline Summary")
    print(f"{'='*60}")
    print(f"Molecules: {len(graphs)}")
    print(f"Time: {elapsed:.1f}s")
    print(f"\nMetrics:")
    for k, v in metrics.items():
        print(f"  {k.upper():12s}: {v:.4f}")
    print(f"{'='*60}")
    print(f"\n✓ Saved to: {out_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\nERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
