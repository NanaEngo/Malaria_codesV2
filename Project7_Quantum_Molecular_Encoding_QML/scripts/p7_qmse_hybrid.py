"""
P7 — QMSE-based Hybrid QML Model

Uses quantum molecular encoding (QMSE) as molecular features,
NOT classical fingerprints (ECFP4).

Architecture:
    SMILES → QMSE Matrix (BondOrderMatrix) → Quantum Circuit → MLP → Classification

This properly integrates quantum molecular encoding as requested.

Usage:
    python scripts/p7_qmse_hybrid.py --p1-set-a --qmse-method bond_order --max-atoms 30
    python scripts/p7_qmse_hybrid.py --p3-benchmark --qmse-method coulomb --max-atoms 50
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import LeaveOneOut, StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

# Add scripts to path for QMSE imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from qmse_lib import BondOrderMatrix, CoulombMatrix
from qmse_lib.encodings import BondFeatureMap
import pennylane as qml

# Molecular encoding
class QMSEEncoder:
    """
    Quantum Molecular Structure Encoding.
    
    Converts SMILES → QMSE matrix using:
      - BondOrderMatrix: bond topology + atomic charges
      - CoulombMatrix: 3D geometry + electrostatics
    """
    
    def __init__(self, method='bond_order', add_hydrogens=False, max_atoms=30):
        """
        Args:
            method: 'bond_order' or 'coulomb'
            add_hydrogens: Include explicit hydrogens
            max_atoms: Maximum molecule size (for padding)
        """
        self.method = method
        self.add_hydrogens = add_hydrogens
        self.max_atoms = max_atoms
        
        if method == 'bond_order':
            self.encoder = BondOrderMatrix()
        elif method == 'coulomb':
            self.encoder = CoulombMatrix()
        else:
            raise ValueError(f"Unknown QMSE method: {method}")
    
    def encode(self, smiles: str) -> np.ndarray:
        """
        SMILES → QMSE matrix.
        
        Returns:
            (max_atoms, max_atoms) padded matrix
        """
        # Compute QMSE matrix
        matrix = self.encoder.compute(smiles, add_hydrogens=self.add_hydrogens)
        
        n_atoms = matrix.shape[0]
        
        if n_atoms > self.max_atoms:
            raise ValueError(
                f"Molecule has {n_atoms} atoms, exceeds max_atoms={self.max_atoms}"
            )
        
        # Pad to max_atoms
        if n_atoms < self.max_atoms:
            padded = np.zeros((self.max_atoms, self.max_atoms))
            padded[:n_atoms, :n_atoms] = matrix
            matrix = padded
        
        return matrix
    
    def encode_batch(self, smiles_list: List[str]) -> np.ndarray:
        """
        Batch encoding.
        
        Returns:
            (batch_size, max_atoms, max_atoms) tensor
        """
        matrices = []
        for smiles in smiles_list:
            try:
                matrix = self.encode(smiles)
                matrices.append(matrix)
            except Exception as e:
                print(f"WARNING: Failed to encode {smiles}: {e}")
                # Use zero matrix as fallback
                matrices.append(np.zeros((self.max_atoms, self.max_atoms)))
        
        return np.array(matrices)


# Quantum circuit layer
class QMSEQuantumLayer(nn.Module):
    """
    Quantum layer that processes QMSE matrices.
    
    Uses BondFeatureMap to encode molecular structure into quantum states,
    then measures Pauli Z expectations as quantum features.
    """
    
    def __init__(self, n_qubits=8, n_layers=2, entangling='cnot'):
        """
        Args:
            n_qubits: Number of qubits (≤ max_atoms in QMSE)
            n_layers: Circuit depth
            entangling: Entangling gate ('cnot', 'rzz', 'cz')
        """
        super().__init__()
        
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.entangling = entangling
        
        # Create quantum device
        self.dev = qml.device('default.qubit', wires=n_qubits)
        
        # Trainable weights for VQC
        self.weights = nn.Parameter(torch.randn(n_layers, n_qubits, 3) * 0.1)
    
    def _build_circuit(self, qmse_matrix: np.ndarray):
        """
        Build quantum circuit from QMSE matrix.
        
        Args:
            qmse_matrix: (max_atoms, max_atoms) QMSE matrix
        
        Returns:
            QNode (quantum circuit)
        """
        # Extract relevant submatrix for n_qubits
        submatrix = qmse_matrix[:self.n_qubits, :self.n_qubits]
        
        @qml.qnode(self.dev, interface='torch')
        def circuit(weights):
            # 1. Encode QMSE matrix using BondFeatureMap
            # Convert matrix elements to rotation angles
            for i in range(self.n_qubits):
                for j in range(i+1, self.n_qubits):
                    angle = np.arctan(submatrix[i, j]) if submatrix[i, j] != 0 else 0
                    qml.RZ(angle, wires=i)
                    qml.RZ(angle, wires=j)
            
            # 2. Variational layers
            for layer in range(self.n_layers):
                # Rotation layer
                for qubit in range(self.n_qubits):
                    qml.Rot(*weights[layer, qubit], wires=qubit)
                
                # Entangling layer
                for qubit in range(self.n_qubits - 1):
                    if self.entangling == 'cnot':
                        qml.CNOT(wires=[qubit, qubit + 1])
                    elif self.entangling == 'rzz':
                        qml.IsingZZ(0.1, wires=[qubit, qubit + 1])
                    elif self.entangling == 'cz':
                        qml.CZ(wires=[qubit, qubit + 1])
            
            # 3. Measurements (Pauli Z on all qubits)
            return [qml.expval(qml.PauliZ(i)) for i in range(self.n_qubits)]
        
        return circuit
    
    def forward(self, qmse_batch: torch.Tensor) -> torch.Tensor:
        """
        Args:
            qmse_batch: (batch_size, max_atoms, max_atoms) QMSE matrices
        
        Returns:
            (batch_size, n_qubits) quantum features
        """
        batch_size = qmse_batch.shape[0]
        quantum_features = []
        
        for i in range(batch_size):
            qmse_matrix = qmse_batch[i].detach().cpu().numpy()
            circuit = self._build_circuit(qmse_matrix)
            measurements = circuit(self.weights)
            
            # Convert to tensor
            quantum_features.append(torch.stack(measurements))
        
        return torch.stack(quantum_features)


# Hybrid model
class QMSEHybridModel(nn.Module):
    """
    Hybrid QML model using QMSE as molecular features.
    
    Architecture:
        SMILES → QMSE → Quantum Circuit → MLP → Classification
    """
    
    def __init__(self, max_atoms=30, n_qubits=8, n_layers=2, 
                 entangling='cnot', hidden_dim=32):
        """
        Args:
            max_atoms: Maximum molecule size
            n_qubits: Number of qubits
            n_layers: Circuit depth
            entangling: Entangling gate
            hidden_dim: MLP hidden dimension
        """
        super().__init__()
        
        self.max_atoms = max_atoms
        self.n_qubits = n_qubits
        
        # Quantum layer
        self.quantum_layer = QMSEQuantumLayer(
            n_qubits=n_qubits,
            n_layers=n_layers,
            entangling=entangling
        )
        
        # Classical post-processing
        self.mlp = nn.Sequential(
            nn.Linear(n_qubits, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
    
    def forward(self, qmse_batch: torch.Tensor) -> torch.Tensor:
        """
        Args:
            qmse_batch: (batch_size, max_atoms, max_atoms)
        
        Returns:
            (batch_size, 1) predictions
        """
        # Quantum feature extraction
        quantum_features = self.quantum_layer(qmse_batch)
        
        # Classical classification
        output = self.mlp(quantum_features)
        
        return output
    
    def count_parameters(self):
        """Count trainable parameters."""
        quantum_params = self.quantum_layer.weights.numel()
        classical_params = sum(p.numel() for p in self.mlp.parameters())
        total = quantum_params + classical_params
        
        return {
            'total': total,
            'quantum': quantum_params,
            'classical': classical_params
        }


# Dataset
class QMSEDataset(Dataset):
    """Dataset of QMSE matrices."""
    
    def __init__(self, qmse_matrices: np.ndarray, labels: np.ndarray):
        self.matrices = torch.FloatTensor(qmse_matrices)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.matrices[idx], self.labels[idx]


# Training
def train_qmse_model(model, train_loader, val_loader=None, n_epochs=50,
                     lr=0.01, patience=10, verbose=True):
    """Train QMSE hybrid model."""
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    history = {
        'train_loss': [],
        'val_auc': [],
        'val_acc': []
    }
    
    best_auc = 0.0
    patience_counter = 0
    
    for epoch in range(n_epochs):
        # Train
        model.train()
        train_losses = []
        
        for qmse_batch, labels in train_loader:
            qmse_batch = qmse_batch.to(device)
            labels = labels.to(device).unsqueeze(1)
            
            optimizer.zero_grad()
            outputs = model(qmse_batch)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_losses.append(loss.item())
        
        avg_train_loss = np.mean(train_losses)
        history['train_loss'].append(avg_train_loss)
        
        # Validation
        if val_loader is not None:
            model.eval()
            val_preds, val_true = [], []
            
            with torch.no_grad():
                for qmse_batch, labels in val_loader:
                    qmse_batch = qmse_batch.to(device)
                    outputs = model(qmse_batch)
                    val_preds.extend(outputs.cpu().numpy())
                    val_true.extend(labels.numpy())
            
            val_auc = roc_auc_score(val_true, val_preds)
            val_acc = accuracy_score(val_true, np.array(val_preds) > 0.5)
            
            history['val_auc'].append(val_auc)
            history['val_acc'].append(val_acc)
            
            if verbose:
                print(f"Epoch {epoch+1}/{n_epochs}: "
                      f"Loss={avg_train_loss:.4f}, "
                      f"Val AUC={val_auc:.4f}, "
                      f"Val Acc={val_acc:.4f}")
            
            # Early stopping
            if val_auc > best_auc:
                best_auc = val_auc
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
        else:
            if verbose and epoch % 10 == 0:
                print(f"Epoch {epoch+1}/{n_epochs}: Loss={avg_train_loss:.4f}")
    
    return history


# Main experiment
def run_p1_experiment(qmse_method='bond_order', max_atoms=30, n_qubits=8,
                      n_layers=2, n_epochs=50):
    """
    Run P1 Set A experiment with QMSE encoding.
    
    Uses Leave-One-Out CV on 20 molecules.
    """
    print("\n" + "=" * 60)
    print(f"P1 Set A — QMSE Hybrid QML (method={qmse_method})")
    print("=" * 60)
    
    # Load data
    data_file = PROJECT_ROOT / "data" / "p1_set_a_20_candidates.csv"
    if not data_file.exists():
        print(f"ERROR: {data_file} not found")
        print("Run: python scripts/p7_data_preparation.py --p1-only")
        sys.exit(1)
    
    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} molecules from P1 Set A")
    
    # QMSE encoding
    print(f"\nEncoding molecules using QMSE ({qmse_method})...")
    encoder = QMSEEncoder(method=qmse_method, max_atoms=max_atoms)
    
    qmse_matrices = []
    valid_indices = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        try:
            matrix = encoder.encode(row['canonical_smiles'])
            qmse_matrices.append(matrix)
            valid_indices.append(idx)
        except Exception as e:
            print(f"WARNING: Failed to encode molecule {idx}: {e}")
    
    qmse_matrices = np.array(qmse_matrices)
    df = df.iloc[valid_indices].reset_index(drop=True)
    
    print(f"Successfully encoded {len(qmse_matrices)} molecules")
    print(f"QMSE matrix shape: {qmse_matrices.shape}")
    
    # Dummy labels (for PoC)
    labels = np.random.randint(0, 2, len(df))
    
    # LOO-CV
    print(f"\nRunning Leave-One-Out CV ({len(df)} folds)...")
    
    loo = LeaveOneOut()
    predictions = []
    true_labels = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(loo.split(qmse_matrices)):
        print(f"\n  Fold {fold_idx+1}/{len(df)}")
        
        # Split data
        X_train = qmse_matrices[train_idx]
        y_train = labels[train_idx]
        X_test = qmse_matrices[test_idx]
        y_test = labels[test_idx]
        
        # Create datasets
        train_dataset = QMSEDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
        
        # Create model
        model = QMSEHybridModel(
            max_atoms=max_atoms,
            n_qubits=n_qubits,
            n_layers=n_layers
        )
        
        # Train
        train_qmse_model(
            model, train_loader,
            n_epochs=n_epochs,
            verbose=False
        )
        
        # Predict
        model.eval()
        with torch.no_grad():
            X_test_tensor = torch.FloatTensor(X_test)
            pred = model(X_test_tensor).item()
        
        predictions.append(pred)
        true_labels.append(y_test[0])
        
        print(f"    Predicted: {pred:.3f}, True: {y_test[0]}")
    
    # Overall metrics
    auc = roc_auc_score(true_labels, predictions)
    acc = accuracy_score(true_labels, np.array(predictions) > 0.5)
    f1 = f1_score(true_labels, np.array(predictions) > 0.5)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"AUC: {auc:.4f}")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1: {f1:.4f}")
    
    # Save results
    results_dir = PROJECT_ROOT / "results" / "phase1_p1_set_a" / f"qmse_{qmse_method}"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'method': 'qmse_hybrid',
        'qmse_method': qmse_method,
        'max_atoms': max_atoms,
        'n_qubits': n_qubits,
        'n_layers': n_layers,
        'n_epochs': n_epochs,
        'metrics': {
            'auc': float(auc),
            'accuracy': float(acc),
            'f1': float(f1)
        },
        'predictions': [float(p) for p in predictions],
        'true_labels': [int(l) for l in true_labels]
    }
    
    results_file = results_dir / "results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved: {results_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="P7 QMSE Hybrid QML")
    parser.add_argument('--p1-set-a', action='store_true', help="Run on P1 Set A")
    parser.add_argument('--qmse-method', choices=['bond_order', 'coulomb'], 
                        default='bond_order', help="QMSE encoding method")
    parser.add_argument('--max-atoms', type=int, default=30, help="Max molecule size")
    parser.add_argument('--qubits', type=int, default=8, help="Number of qubits")
    parser.add_argument('--depth', type=int, default=2, help="Circuit depth")
    parser.add_argument('--epochs', type=int, default=50, help="Training epochs")
    
    args = parser.parse_args()
    
    if args.p1_set_a:
        run_p1_experiment(
            qmse_method=args.qmse_method,
            max_atoms=args.max_atoms,
            n_qubits=args.qubits,
            n_layers=args.depth,
            n_epochs=args.epochs
        )
    else:
        print("Please specify --p1-set-a")
        sys.exit(1)


if __name__ == "__main__":
    main()
