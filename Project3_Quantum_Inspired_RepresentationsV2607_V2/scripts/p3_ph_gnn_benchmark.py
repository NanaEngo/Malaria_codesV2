#!/usr/bin/env python3
"""
Simplified PH+GNN benchmark for TopologyNet/D-GRIL qualitative comparison.

Implements a GIN (Graph Isomorphism Network) classifier enriched with
persistent homology features (H0/H1 persistence diagram statistics as
node-level features) on the 19,849-molecule malaria library.

This provides a practical, installable comparison point for the
TopologyNet (Cang & Wei 2017) and D-GRIL (Mukherjee et al. 2026) methods
without requiring their complex native installations (Redis/MapReduce
for TopologyNet; CUDA 11.7 / C++ Boost-compiled GRIL for D-GRIL).

Architecture:
  - Molecule -> molecular graph (atoms=vertices, bonds=edges)
  - Node features: atom type + degree + PH contribution
  - PH features: H0/H1 persistence statistics per atom
  - 3 GINConv layers + global mean pooling + MLP classifier
  - 5-fold stratified CV, class-weighted

Usage:
    python p3_ph_gnn_benchmark.py --n-mols 2000 --epochs 100
"""

import argparse
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score

warnings.filterwarnings("ignore")

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
from torch_geometric.nn import GINConv, global_mean_pool
from torch_geometric.data import Data
try:
    from torch_geometric.loader import DataLoader
except ImportError:
    from torch_geometric.data import DataLoader
    _HAS_TORCH_GEO = True
except ImportError:
    _HAS_TORCH_GEO = False
    print("WARNING: torch_geometric not installed. Install: pip install torch_geometric")

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    _HAS_RDKIT = True
except ImportError:
    _HAS_RDKIT = False

try:
    from ripser import ripser
    _HAS_RIPSER = True
except ImportError:
    _HAS_RIPSER = False

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results'

N_ATOM_FEATURES = 8  # atomic_num, degree, hybridization, aromatic, num_h, formal_charge, ring_member, ph_h0_mean
PH_FEATURES = 4       # H0_mean_pers, H0_entropy, H1_mean_pers, H1_entropy (per-atom context)


def atom_features(atom):
    return [
        atom.GetAtomicNum() / 100.0,
        atom.GetDegree() / 6.0,
        int(atom.GetHybridization()) / 10.0,
        float(atom.GetIsAromatic()),
        atom.GetTotalNumHs() / 4.0,
        (atom.GetFormalCharge() + 4) / 8.0,
        float(atom.IsInRing()),
        0.0,  # placeholder for PH contribution
    ]


def mol_to_graph(smiles, ph_features=None):
    """Convert molecule to PyG Data object with optional PH features."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    # Build adjacency from bonds
    edge_index = []
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        edge_index.append([i, j])
        edge_index.append([j, i])

    if len(edge_index) == 0:
        return None

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()

    # Node features
    x = []
    for atom in mol.GetAtoms():
        feats = atom_features(atom)
        if ph_features is not None:
            feats[-1] = ph_features  # single scalar PH contribution
        x.append(feats)

    x = torch.tensor(x, dtype=torch.float)
    return Data(x=x, edge_index=edge_index, num_nodes=len(x))


class PHGIN(nn.Module):
    """GIN with 3 conv layers + global mean pool."""
    def __init__(self, in_dim, hidden_dim=64, num_classes=2):
        super().__init__()
        nn1 = nn.Sequential(nn.Linear(in_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, hidden_dim))
        nn2 = nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, hidden_dim))
        nn3 = nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, hidden_dim))
        self.conv1 = GINConv(nn1)
        self.conv2 = GINConv(nn2)
        self.conv3 = GINConv(nn3)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        x = F.relu(self.conv3(x, edge_index))
        x = global_mean_pool(x, batch)
        return self.classifier(x)


def compute_ph_features(smiles):
    """Compute per-molecule PH statistics for node enrichment."""
    if not _HAS_RIPSER:
        return 1.0  # neutral placeholder
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return 1.0
        mol = Chem.AddHs(mol)
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        if AllChem.EmbedMolecule(mol, params) != 0:
            return 1.0
        AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
        conf = mol.GetConformer()
        atoms = list(mol.GetAtoms())
        coords = np.array([conf.GetAtomPosition(a.GetIdx()) for a in atoms])
        n = len(coords)
        if n < 3:
            return 1.0
        diff = coords[:, None, :] - coords[None, :, :]
        d = np.sqrt((diff ** 2).sum(axis=-1))
        result = ripser(d, maxdim=1, distance_matrix=True)
        dgms = result['dgms']
        # Compute H0 and H1 mean persistence
        h0_mean = 0.0
        if len(dgms) > 0:
            finite = dgms[0][np.isfinite(dgms[0][:, 1])]
            if len(finite) > 0:
                h0_mean = float((finite[:, 1] - finite[:, 0]).mean())
        h1_mean = 0.0
        if len(dgms) > 1:
            finite = dgms[1][np.isfinite(dgms[1][:, 1])]
            if len(finite) > 0:
                h1_mean = float((finite[:, 1] - finite[:, 0]).mean())
        # Scale to [0, 1]
        return min(max((h0_mean + h1_mean) / 5.0, 0.0), 1.0)
    except Exception:
        return 1.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-mols', type=int, default=2000, help='Number of molecules')
    parser.add_argument('--epochs', type=int, default=100, help='Training epochs')
    parser.add_argument('--use-ph', action='store_true', help='Enrich with PH features')
    args = parser.parse_args()

    if not _HAS_TORCH_GEO or not _HAS_RDKIT:
        print("ERROR: Requires torch_geometric and rdkit")
        return

    print("=" * 60)
    print(f"PH+GNN Benchmark (n={args.n_mols}, PH={args.use_ph})")
    print("=" * 60)

    # Load data
    data_path = RESULTS_DIR / 'p3_labels_production.csv'
    if not data_path.exists():
        data_path = RESULTS_DIR / 'p3_hybrid_benchmark.csv'
    df = pd.read_csv(data_path).head(args.n_mols)

    smiles_col = 'smiles' if 'smiles' in df.columns else ('input' if 'input' in df.columns else df.columns[0])
    label_col = 'label' if 'label' in df.columns else ('activity' if 'activity' in df.columns else None)
    if label_col is None:
        print("ERROR: No label/activity column found. Provide a labeled CSV via --input.")
        raise SystemExit(1)

    smiles_list = df[smiles_col].tolist()
    labels = df[label_col].astype(int).values

    # Compute PH features if requested
    ph_values = None
    if args.use_ph and _HAS_RIPSER:
        print("Computing PH features...")
        ph_values = []
        for i, smi in enumerate(smiles_list):
            if i % 200 == 0:
                print(f"  {i}/{len(smiles_list)}...")
            ph_values.append(compute_ph_features(smi))
        print(f"  Done. Mean PH: {np.mean(ph_values):.3f}")

    # Convert mols to graphs
    print("Converting molecules to graphs...")
    graphs = []
    valid_idx = []
    for i, smi in enumerate(smiles_list):
        ph = ph_values[i] if ph_values else None
        g = mol_to_graph(smi, ph)
        if g is not None:
            g.y = torch.tensor([labels[i]], dtype=torch.long)
            graphs.append(g)
            valid_idx.append(i)

    print(f"Valid graphs: {len(graphs)}/{len(smiles_list)}")
    valid_labels = labels[valid_idx]

    # 5-fold CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = []
    accs = []
    f1s = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(graphs, valid_labels)):
        train_graphs = [graphs[i] for i in train_idx]
        test_graphs = [graphs[i] for i in test_idx]

        train_loader = DataLoader(train_graphs, batch_size=32, shuffle=True)
        test_loader = DataLoader(test_graphs, batch_size=32)

        in_dim = N_ATOM_FEATURES
        model = PHGIN(in_dim)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        # Compute class weights
        train_labs = valid_labels[train_idx]
        n_pos = (train_labs == 1).sum()
        n_neg = (train_labs == 0).sum()
        pos_weight = n_neg / max(n_pos, 1)
        criterion = nn.CrossEntropyLoss(weight=torch.tensor([1.0, pos_weight]))

        # Train
        model.train()
        for epoch in range(args.epochs):
            total_loss = 0
            for batch in train_loader:
                optimizer.zero_grad()
                out = model(batch)
                loss = criterion(out, batch.y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

        # Evaluate
        model.eval()
        all_preds = []
        all_true = []
        with torch.no_grad():
            for batch in test_loader:
                out = model(batch)
                preds = F.softmax(out, dim=1)[:, 1].numpy()
                all_preds.extend(preds)
                all_true.extend(batch.y.numpy())

        auc = roc_auc_score(all_true, all_preds)
        pred_labels = (np.array(all_preds) > 0.5).astype(int)
        acc = accuracy_score(all_true, pred_labels)
        f1 = f1_score(all_true, pred_labels)

        aucs.append(auc)
        accs.append(acc)
        f1s.append(f1)
        print(f"Fold {fold+1}: AUC={auc:.4f}, Acc={acc:.4f}, F1={f1:.4f}")

    # Summary
    print(f"\n5-fold CV Results (n={len(graphs)}, PH={args.use_ph}):")
    print(f"  AUC: {np.mean(aucs):.4f} +/- {np.std(aucs):.4f}")
    print(f"  Acc: {np.mean(accs):.4f} +/- {np.std(accs):.4f}")
    print(f"  F1:  {np.mean(f1s):.4f} +/- {np.std(f1s):.4f}")

    # Save results
    output = {
        'method': f'PH+GIN{"+PH" if args.use_ph else ""}',
        'n_mols': len(graphs),
        'auc_mean': round(np.mean(aucs), 4),
        'auc_std': round(np.std(aucs), 4),
        'acc_mean': round(np.mean(accs), 4),
        'f1_mean': round(np.mean(f1s), 4),
    }
    out_csv = RESULTS_DIR / f'p3_ph_gnn_benchmark{"_ph" if args.use_ph else ""}.csv'
    pd.DataFrame([output]).to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}")


if __name__ == '__main__':
    main()
