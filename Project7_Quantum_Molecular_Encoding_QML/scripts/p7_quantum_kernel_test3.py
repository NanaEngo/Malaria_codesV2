"""
P7 — Quantum Kernel Test (3 molecules)

Quick test to verify quantum kernel computation works on a small subset.
"""

import sys
import json
import warnings
from pathlib import Path
from datetime import datetime
import time

import numpy as np
import pandas as pd
import pennylane as qml

# Add scripts to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from qmse_lib import BondOrderMatrix

warnings.filterwarnings('ignore')

# Paths
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results" / "phase1_p1_set_a" / "quantum_kernel"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("P7 Quantum Kernel — TEST (3 molecules)")
print("=" * 60)

# Load data - take only first 3 molecules
data_file = DATA_DIR / "p1_set_a_20_candidates.csv"
print(f"\nLoading: {data_file}")
df = pd.read_csv(data_file).head(3)  # ONLY 3 MOLECULES FOR TEST
print(f"Molecules: {len(df)} (TEST SUBSET)")

# Extract SMILES and labels
smiles_list = df['canonical_smiles'].tolist()
molecule_ids = df['molecule_id'].tolist()
y_true = df['activity'].values

n_molecules = len(smiles_list)

# Encode all molecules to BondOrderMatrix
print("\n[1/3] Encoding molecules to BondOrderMatrix...")
encoder = BondOrderMatrix()
matrices = []
max_atoms = 0

for i, (mol_id, smiles) in enumerate(zip(molecule_ids, smiles_list)):
    print(f"  {mol_id}: {smiles[:50]}...")
    try:
        matrix = encoder.compute(smiles, add_hydrogens=False)
        matrices.append(matrix)
        max_atoms = max(max_atoms, matrix.shape[0])
        print(f"    → {matrix.shape[0]} atoms, matrix shape {matrix.shape}")
    except Exception as e:
        print(f"    ERROR: {e}")
        matrices.append(None)

print(f"\n  Max atoms: {max_atoms}")

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
    print(f"  Padded to {padded.shape}")

# Generate quantum circuits
print(f"\n[3/3] Computing UnitaryOverlap kernel...")
print(f"  Device: PennyLane default.qubit")
print(f"  Qubits: {max_atoms}")
print(f"  Kernel entries: {n_molecules}×{n_molecules} = {n_molecules**2}")

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
timing = []

for i in range(n_molecules):
    if matrices_padded[i] is None:
        continue
    
    print(f"\n  Row {i+1}/{n_molecules} ({molecule_ids[i]})...")
    circuit_i = create_circuit(matrices_padded[i])
    
    t0 = time.time()
    state_i = circuit_i()
    t1 = time.time()
    print(f"    State computed in {t1-t0:.2f}s")
    
    for j in range(i, n_molecules):
        if matrices_padded[j] is None:
            continue
        
        if i == j:
            # Diagonal: always 1.0
            K[i, j] = 1.0
            print(f"    K[{i},{j}] = 1.0000 (diagonal)")
        else:
            circuit_j = create_circuit(matrices_padded[j])
            state_j = circuit_j()
            
            # UnitaryOverlap: |⟨ψ_i|ψ_j⟩|²
            overlap = np.abs(np.vdot(state_i, state_j))**2
            K[i, j] = overlap
            K[j, i] = overlap  # Symmetric
            print(f"    K[{i},{j}] = {overlap:.4f}")
        
        timing.append(t1-t0)

print(f"\n✓ Kernel computation complete")
print(f"  Shape: {K.shape}")
print(f"  Average time per state: {np.mean(timing):.2f}s")
print(f"  Total time estimate for 17 molecules: {np.mean(timing) * 17 * 17 / 60:.1f} minutes")

# Display kernel
print("\nKernel matrix:")
print(K)

# Save results
print("\n[Saving results...]")

# 1. Kernel matrix (NumPy)
kernel_npy = RESULTS_DIR / "quantum_kernel_bond_order_test3.npy"
np.save(kernel_npy, K)
print(f"  Saved: {kernel_npy}")

# 2. Metadata
metadata = {
    "timestamp": datetime.now().isoformat(),
    "method": "bond_order",
    "n_molecules": n_molecules,
    "n_qubits": max_atoms,
    "kernel_shape": list(K.shape),
    "kernel_matrix": K.tolist(),
    "molecule_ids": molecule_ids,
    "y_true": y_true.tolist(),
    "timing_seconds_per_state": np.mean(timing),
    "note": "TEST SUBSET ONLY - 3 molecules"
}

metadata_json = RESULTS_DIR / "quantum_kernel_bond_order_test3_metadata.json"
with open(metadata_json, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"  Saved: {metadata_json}")

print("\n" + "=" * 60)
print("✅ Quantum kernel test complete (3 molecules)")
print("=" * 60)
print("\nNOTE: This is a proof-of-concept on 3 molecules.")
print("Full 17-molecule kernel requires substantial computation time.")
print("Consider GPU acceleration or true quantum hardware for production runs.")
print()
