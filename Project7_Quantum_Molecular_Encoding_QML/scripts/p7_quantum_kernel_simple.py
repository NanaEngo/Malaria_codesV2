"""
P7 — Simplified Quantum Kernel Computation

Streamlined computation of quantum kernel matrices for P1 Set A.
Focuses on core functionality without extensive error handling.
"""

import sys
import json
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import pennylane as qml
from tqdm import tqdm

# Add scripts to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from qmse_lib import BondOrderMatrix
from qmse_lib.encodings import BondFeatureMap, UnitaryOverlap

warnings.filterwarnings('ignore')

# Paths
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results" / "phase1_p1_set_a" / "quantum_kernel"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("P7 Quantum Kernel — Simplified Computation")
print("=" * 60)

# Load data
data_file = DATA_DIR / "p1_set_a_20_candidates.csv"
print(f"\nLoading: {data_file}")
df = pd.read_csv(data_file)
print(f"Molecules: {len(df)}")

# Extract SMILES and labels
smiles_list = df['canonical_smiles'].tolist()
molecule_ids = df['molecule_id'].tolist()
y_true = df['activity'].values

n_molecules = len(smiles_list)
print(f"\nComputing {n_molecules}×{n_molecules} = {n_molecules**2} kernel entries...")

# Encode all molecules to BondOrderMatrix
print("\n[1/3] Encoding molecules to BondOrderMatrix...")
encoder = BondOrderMatrix()
matrices = []
max_atoms = 0

for i, smiles in enumerate(tqdm(smiles_list, desc="Encoding")):
    try:
        matrix = encoder.compute(smiles, add_hydrogens=False)
        matrices.append(matrix)
        max_atoms = max(max_atoms, matrix.shape[0])
    except Exception as e:
        print(f"  ERROR encoding molecule {i} ({smiles}): {e}")
        matrices.append(None)

print(f"  Max atoms: {max_atoms}")
print(f"  Successful: {sum(m is not None for m in matrices)}/{n_molecules}")

# Zero-pad matrices to uniform size
print("\n[2/3] Zero-padding to uniform size...")
matrices_padded = []
for matrix in matrices:
    if matrix is None:
        matrices_padded.append(None)
        continue
    
    pad_size = max_atoms - matrix.shape[0]
    if pad_size > 0:
        padded = np.pad(matrix, ((0, pad_size), (0, pad_size)), mode='constant')
    else:
        padded = matrix
    matrices_padded.append(padded)

# Generate quantum circuits
print("\n[3/3] Computing UnitaryOverlap kernel...")
print(f"  Device: PennyLane default.qubit (statevector simulation)")
print(f"  Qubits: {max_atoms}")

# Create quantum device
dev = qml.device('default.qubit', wires=max_atoms)

def create_circuit(matrix):
    """Create PennyLane quantum circuit from BondOrderMatrix."""
    @qml.qnode(dev)
    def circuit():
        # Data encoding: RZ gates with arctan-transformed matrix elements
        for i in range(matrix.shape[0]):
            # Diagonal: atomic number encoding
            angle_diag = np.arctan(matrix[i, i])
            qml.RZ(angle_diag, wires=i)
            
            # Off-diagonal: bond encoding
            for j in range(i+1, matrix.shape[0]):
                if matrix[i, j] != 0:
                    angle_bond = np.arctan(matrix[i, j])
                    qml.RZ(angle_bond, wires=i)
                    qml.RZ(angle_bond, wires=j)
        
        # Entangling layer: linear connectivity
        for i in range(matrix.shape[0] - 1):
            qml.CNOT(wires=[i, i+1])
        
        return qml.state()
    
    return circuit

# Compute kernel matrix
K = np.zeros((n_molecules, n_molecules))

for i in tqdm(range(n_molecules), desc="Kernel rows"):
    if matrices_padded[i] is None:
        continue
    
    circuit_i = create_circuit(matrices_padded[i])
    state_i = circuit_i()
    
    for j in range(i, n_molecules):
        if matrices_padded[j] is None:
            continue
        
        circuit_j = create_circuit(matrices_padded[j])
        state_j = circuit_j()
        
        # UnitaryOverlap: |⟨ψ_i|ψ_j⟩|²
        overlap = np.abs(np.vdot(state_i, state_j))**2
        K[i, j] = overlap
        K[j, i] = overlap  # Symmetric

print(f"\n✓ Kernel computation complete")
print(f"  Shape: {K.shape}")
print(f"  Diagonal: min={K.diagonal().min():.4f}, max={K.diagonal().max():.4f}")
print(f"  Off-diagonal: min={K[np.triu_indices(n_molecules, k=1)].min():.4f}, " +
      f"max={K[np.triu_indices(n_molecules, k=1)].max():.4f}")

# Save results
print("\n[Saving results...]")

# 1. Kernel matrix (NumPy)
kernel_npy = RESULTS_DIR / "quantum_kernel_bond_order.npy"
np.save(kernel_npy, K)
print(f"  Saved: {kernel_npy}")

# 2. Kernel matrix (CSV for inspection)
kernel_csv = RESULTS_DIR / "quantum_kernel_bond_order.csv"
pd.DataFrame(K, index=molecule_ids, columns=molecule_ids).to_csv(kernel_csv)
print(f"  Saved: {kernel_csv}")

# 3. Metadata
metadata = {
    "timestamp": datetime.now().isoformat(),
    "method": "bond_order",
    "n_molecules": n_molecules,
    "n_qubits": max_atoms,
    "kernel_shape": K.shape,
    "diagonal_stats": {
        "min": float(K.diagonal().min()),
        "max": float(K.diagonal().max()),
        "mean": float(K.diagonal().mean()),
        "std": float(K.diagonal().std())
    },
    "off_diagonal_stats": {
        "min": float(K[np.triu_indices(n_molecules, k=1)].min()),
        "max": float(K[np.triu_indices(n_molecules, k=1)].max()),
        "mean": float(K[np.triu_indices(n_molecules, k=1)].mean()),
        "std": float(K[np.triu_indices(n_molecules, k=1)].std())
    },
    "molecule_ids": molecule_ids,
    "y_true": y_true.tolist()
}

metadata_json = RESULTS_DIR / "quantum_kernel_bond_order_metadata.json"
with open(metadata_json, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"  Saved: {metadata_json}")

print("\n" + "=" * 60)
print("✅ Quantum kernel computation complete")
print("=" * 60)
print("\nNext step:")
print("  python scripts/p7_phase1_poc.py --method bond_order")
print()
