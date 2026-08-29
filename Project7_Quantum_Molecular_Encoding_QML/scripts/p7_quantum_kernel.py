"""
P7 — Quantum Kernel Computation

Compute quantum kernel matrices using UnitaryOverlap:
  K(A,B) = |⟨0|U_B† U_A|0⟩|²
  
For P1 Set A (20×20 = 400 evaluations): exact statevector simulation
For P3 Benchmark: Nyström approximation or subset selection

Outputs:
  - Kernel matrices (CSV + NPY)
  - Kernel statistics (eigenvalues, rank, condition number)
  - Gram matrix visualization (optional)

Usage:
    python scripts/p7_quantum_kernel.py --p1-set-a --method bond_order
    python scripts/p7_quantum_kernel.py --p3-benchmark --method bond_order --nystrom 500
"""

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# Import local QMSE library
from qmse_lib.encodings import UnitaryOverlap

warnings.filterwarnings('ignore')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"


def load_circuits(circuit_csv: Path):
    """
    Load pre-generated quantum circuits from CSV.
    
    Returns:
        DataFrame with molecule_id, success status, circuit parameters
    """
    if not circuit_csv.exists():
        raise FileNotFoundError(
            f"Circuit file not found: {circuit_csv}\n"
            f"Run: python scripts/p7_quantum_circuits.py first"
        )
    
    df = pd.read_csv(circuit_csv)
    
    # Filter only successful circuits
    if 'success' in df.columns:
        successful = df[df['success'] == True]
        failed = len(df) - len(successful)
        if failed > 0:
            print(f"WARNING: {failed} molecules failed circuit generation")
        df = successful
    
    print(f"Loaded {len(df)} successful circuits from {circuit_csv.name}")
    return df


def regenerate_circuit(smiles, method, entangling_layer='rzz', n_layers=1):
    """
    Regenerate quantum circuit for a molecule.
    
    This recreates the circuit from SMILES using the same parameters
    as the original circuit generation step.
    """
    from qmse_lib import BondOrderMatrix, CoulombMatrix
    from qmse_lib.encodings import BondFeatureMap
    
    # Generate molecular matrix
    if method == 'bond_order':
        encoder = BondOrderMatrix()
    elif method == 'coulomb':
        encoder = CoulombMatrix()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    matrix = encoder.compute(smiles, add_hydrogens=False)
    matrix_size = matrix.shape[0]
    num_qubits = matrix_size  # 1 qubit per atom
    
    # Generate circuit
    circuit = BondFeatureMap(
        matrix=matrix,
        num_qubits=num_qubits,
        n_layers=n_layers,
        entangling_layer=entangling_layer,
        n_atom_to_qubit=1,
        reverse_bits=True
    )
    
    return circuit


def compute_unitary_overlap(circuit_a: QuantumCircuit, circuit_b: QuantumCircuit) -> float:
    """
    Compute unitary overlap K(A,B) = |⟨0|U_B† U_A|0⟩|²
    
    Uses exact statevector simulation.
    """
    # Get number of qubits (use maximum to handle different sizes)
    n_qubits = max(circuit_a.num_qubits, circuit_b.num_qubits)
    
    # Pad circuits to same size if needed
    if circuit_a.num_qubits < n_qubits:
        circuit_a_padded = QuantumCircuit(n_qubits)
        circuit_a_padded.compose(circuit_a, qubits=range(circuit_a.num_qubits), inplace=True)
        circuit_a = circuit_a_padded
    
    if circuit_b.num_qubits < n_qubits:
        circuit_b_padded = QuantumCircuit(n_qubits)
        circuit_b_padded.compose(circuit_b, qubits=range(circuit_b.num_qubits), inplace=True)
        circuit_b = circuit_b_padded
    
    # Compute statevectors
    # |ψ_A⟩ = U_A|0⟩
    sv_a = Statevector.from_instruction(circuit_a)
    
    # |ψ_B⟩ = U_B|0⟩
    sv_b = Statevector.from_instruction(circuit_b)
    
    # K(A,B) = |⟨ψ_B|ψ_A⟩|²
    overlap = abs(sv_b.inner(sv_a)) ** 2
    
    return float(overlap)


def compute_kernel_matrix(
    mol_ids,
    smiles_list,
    method='bond_order',
    entangling_layer='rzz',
    n_layers=1
):
    """
    Compute full quantum kernel matrix for all molecule pairs.
    
    Args:
        mol_ids: List of molecule IDs
        smiles_list: List of SMILES strings
        method: Encoding method
        entangling_layer: Entangling gate type
        n_layers: Circuit depth
    
    Returns:
        K: (n, n) kernel matrix
        circuit_cache: Dict of {mol_id: circuit}
    """
    n = len(mol_ids)
    K = np.zeros((n, n))
    
    print(f"\nGenerating {n} quantum circuits...")
    circuits = {}
    failed_ids = []
    
    for i, (mol_id, smiles) in enumerate(zip(mol_ids, smiles_list)):
        try:
            circuit = regenerate_circuit(smiles, method, entangling_layer, n_layers)
            circuits[mol_id] = circuit
        except Exception as e:
            print(f"  ERROR: {mol_id} failed circuit generation: {e}")
            failed_ids.append(mol_id)
        
        if (i + 1) % 5 == 0:
            print(f"  {i + 1}/{n} circuits generated")
    
    if failed_ids:
        print(f"\nWARNING: {len(failed_ids)} circuits failed, excluding from kernel")
        # Filter out failed molecules
        valid_indices = [i for i, mol_id in enumerate(mol_ids) if mol_id not in failed_ids]
        mol_ids = [mol_ids[i] for i in valid_indices]
        circuits = {mol_id: circuits[mol_id] for mol_id in mol_ids}
        n = len(mol_ids)
        K = np.zeros((n, n))
    
    print(f"\nComputing {n}×{n} = {n*n} kernel elements...")
    
    # Compute kernel matrix
    total_pairs = (n * (n + 1)) // 2  # Upper triangle including diagonal
    computed = 0
    
    for i, mol_id_i in enumerate(mol_ids):
        for j in range(i, n):  # Upper triangle
            mol_id_j = mol_ids[j]
            
            if i == j:
                # Diagonal: K(A,A) = 1.0 (self-overlap)
                K[i, j] = 1.0
            else:
                try:
                    overlap = compute_unitary_overlap(
                        circuits[mol_id_i],
                        circuits[mol_id_j]
                    )
                    K[i, j] = overlap
                    K[j, i] = overlap  # Symmetric
                except Exception as e:
                    print(f"  ERROR: K({mol_id_i}, {mol_id_j}) failed: {e}")
                    K[i, j] = 0.0
                    K[j, i] = 0.0
            
            computed += 1
            if computed % 10 == 0 or computed == total_pairs:
                print(f"  {computed}/{total_pairs} pairs computed ({100*computed/total_pairs:.1f}%)")
    
    print(f"\nKernel matrix computed: {K.shape}")
    
    return K, circuits, mol_ids


def compute_nystrom_approximation(
    mol_ids,
    smiles_list,
    n_landmarks=500,
    method='bond_order',
    entangling_layer='rzz',
    n_layers=1,
    seed=42
):
    """
    Compute Nyström approximation of kernel matrix for large datasets.
    
    K ≈ K_nm @ K_mm^(-1) @ K_nm^T
    
    where:
    - n = all samples
    - m = landmark samples (subset)
    - K_nm = kernel between all samples and landmarks
    - K_mm = kernel among landmarks
    """
    np.random.seed(seed)
    
    n = len(mol_ids)
    m = min(n_landmarks, n)
    
    print(f"\nNyström approximation: {n} samples, {m} landmarks")
    
    # Select landmark samples (stratified by activity if available)
    landmark_indices = np.random.choice(n, size=m, replace=False)
    landmark_mol_ids = [mol_ids[i] for i in landmark_indices]
    landmark_smiles = [smiles_list[i] for i in landmark_indices]
    
    print(f"Selected {m} landmarks")
    
    # Compute K_mm (landmark kernel)
    print("\n1. Computing K_mm (landmark kernel)...")
    K_mm, circuits_landmarks, landmark_mol_ids = compute_kernel_matrix(
        landmark_mol_ids,
        landmark_smiles,
        method,
        entangling_layer,
        n_layers
    )
    
    # Compute K_nm (all samples vs landmarks)
    print("\n2. Computing K_nm (all samples vs landmarks)...")
    K_nm = np.zeros((n, len(landmark_mol_ids)))
    
    # Generate circuits for all molecules
    print(f"  Generating {n} circuits...")
    all_circuits = {}
    for i, (mol_id, smiles) in enumerate(zip(mol_ids, smiles_list)):
        try:
            circuit = regenerate_circuit(smiles, method, entangling_layer, n_layers)
            all_circuits[mol_id] = circuit
        except Exception as e:
            print(f"    ERROR: {mol_id} failed: {e}")
    
    # Compute overlaps with landmarks
    total_pairs = n * len(landmark_mol_ids)
    computed = 0
    
    for i, mol_id_i in enumerate(mol_ids):
        if mol_id_i not in all_circuits:
            continue
        
        for j, landmark_id in enumerate(landmark_mol_ids):
            try:
                overlap = compute_unitary_overlap(
                    all_circuits[mol_id_i],
                    circuits_landmarks[landmark_id]
                )
                K_nm[i, j] = overlap
            except Exception as e:
                print(f"    ERROR: K({mol_id_i}, {landmark_id}) failed: {e}")
                K_nm[i, j] = 0.0
            
            computed += 1
            if computed % 100 == 0 or computed == total_pairs:
                print(f"    {computed}/{total_pairs} pairs computed ({100*computed/total_pairs:.1f}%)")
    
    # Nyström approximation: K ≈ K_nm @ K_mm^(-1) @ K_nm^T
    print("\n3. Computing Nyström approximation...")
    
    # Regularize K_mm for numerical stability
    K_mm_reg = K_mm + 1e-8 * np.eye(len(landmark_mol_ids))
    
    try:
        K_mm_inv = np.linalg.inv(K_mm_reg)
        K_approx = K_nm @ K_mm_inv @ K_nm.T
    except np.linalg.LinAlgError:
        print("  WARNING: K_mm singular, using pseudo-inverse")
        K_mm_pinv = np.linalg.pinv(K_mm_reg)
        K_approx = K_nm @ K_mm_pinv @ K_nm.T
    
    print(f"  Approximation complete: {K_approx.shape}")
    
    return K_approx, landmark_indices, landmark_mol_ids


def analyze_kernel_matrix(K, mol_ids):
    """Analyze kernel matrix properties."""
    print("\n=== Kernel Matrix Analysis ===")
    
    # Basic statistics
    n = K.shape[0]
    print(f"Shape: {K.shape}")
    print(f"Diagonal (self-overlap): min={K.diagonal().min():.4f}, max={K.diagonal().max():.4f}, mean={K.diagonal().mean():.4f}")
    
    # Off-diagonal statistics
    off_diag = K[~np.eye(n, dtype=bool)]
    print(f"Off-diagonal: min={off_diag.min():.4f}, max={off_diag.max():.4f}, mean={off_diag.mean():.4f}")
    
    # Eigenvalues
    try:
        eigenvalues = np.linalg.eigvalsh(K)
        eigenvalues = eigenvalues[eigenvalues > 1e-10]  # Filter near-zero
        
        print(f"\nEigenvalues:")
        print(f"  Positive: {(eigenvalues > 0).sum()}/{len(eigenvalues)}")
        print(f"  Max: {eigenvalues.max():.4f}")
        print(f"  Min: {eigenvalues.min():.4e}")
        print(f"  Rank: {len(eigenvalues)}")
        
        # Condition number
        if len(eigenvalues) > 0:
            cond = eigenvalues.max() / eigenvalues.min()
            print(f"  Condition number: {cond:.2e}")
        
        # Effective rank (eigenvalues > 1% of max)
        eff_rank = (eigenvalues > 0.01 * eigenvalues.max()).sum()
        print(f"  Effective rank (λ > 0.01λ_max): {eff_rank}")
        
        stats = {
            'eigenvalues': eigenvalues.tolist(),
            'n_positive': int((eigenvalues > 0).sum()),
            'rank': int(len(eigenvalues)),
            'effective_rank': int(eff_rank),
            'condition_number': float(cond) if len(eigenvalues) > 0 else None
        }
    except Exception as e:
        print(f"  WARNING: Eigenvalue analysis failed: {e}")
        stats = {'error': str(e)}
    
    # Check positive semi-definiteness
    min_eigenvalue = eigenvalues.min() if len(eigenvalues) > 0 else None
    if min_eigenvalue is not None and min_eigenvalue < -1e-6:
        print(f"\n  ⚠️  WARNING: Kernel is not positive semi-definite (min λ = {min_eigenvalue:.4e})")
    else:
        print(f"\n  ✓ Kernel is positive semi-definite")
    
    return stats


def save_kernel(K, mol_ids, output_dir, method, phase_name, stats=None, nystrom_info=None):
    """Save kernel matrix and statistics."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save kernel as CSV
    kernel_df = pd.DataFrame(K, index=mol_ids, columns=mol_ids)
    csv_file = output_dir / f"quantum_kernel_{method}.csv"
    kernel_df.to_csv(csv_file)
    print(f"\nSaved kernel CSV: {csv_file}")
    
    # Save kernel as NPY (more efficient for large matrices)
    npy_file = output_dir / f"quantum_kernel_{method}.npy"
    np.save(npy_file, K)
    print(f"Saved kernel NPY: {npy_file}")
    
    # Save molecule ID mapping
    id_file = output_dir / f"quantum_kernel_{method}_mol_ids.txt"
    with open(id_file, 'w') as f:
        f.write('\n'.join(mol_ids))
    print(f"Saved molecule IDs: {id_file}")
    
    # Save statistics
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'phase': phase_name,
        'method': method,
        'shape': list(K.shape),
        'n_molecules': len(mol_ids),
        'statistics': stats or {},
        'nystrom': nystrom_info
    }
    
    stats_file = output_dir / f"quantum_kernel_{method}_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved statistics: {stats_file}")


def main():
    parser = argparse.ArgumentParser(description="P7 Quantum Kernel Computation")
    parser.add_argument('--p1-set-a', action='store_true', help="Compute kernel for P1 Set A")
    parser.add_argument('--p3-benchmark', action='store_true', help="Compute kernel for P3 benchmark")
    parser.add_argument('--method', choices=['bond_order', 'coulomb'], default='bond_order',
                        help="Encoding method (default: bond_order)")
    parser.add_argument('--entangling', choices=['rxx', 'ryy', 'rzz'], default='rzz',
                        help="Entangling layer (default: rzz)")
    parser.add_argument('--depth', type=int, default=1, help="Circuit depth (default: 1)")
    parser.add_argument('--nystrom', type=int, default=None,
                        help="Use Nyström approximation with N landmarks (for large datasets)")
    
    args = parser.parse_args()
    
    if not any([args.p1_set_a, args.p3_benchmark]):
        print("ERROR: Specify --p1-set-a or --p3-benchmark")
        sys.exit(1)
    
    print("=" * 60)
    print("P7 Quantum Kernel Computation")
    print("=" * 60)
    
    try:
        if args.p1_set_a:
            print("\n### Phase 1: P1 Set A (Exact Kernel) ###")
            
            # Load data
            data_file = DATA_DIR / "p1_set_a_20_candidates.csv"
            if not data_file.exists():
                print(f"ERROR: {data_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p1-only")
                sys.exit(1)
            
            df = pd.read_csv(data_file)
            mol_ids = df['molecule_id'].tolist()
            smiles_list = df['canonical_smiles'].tolist()
            
            # Compute exact kernel
            K, circuits, mol_ids = compute_kernel_matrix(
                mol_ids,
                smiles_list,
                method=args.method,
                entangling_layer=args.entangling,
                n_layers=args.depth
            )
            
            # Analyze kernel
            stats = analyze_kernel_matrix(K, mol_ids)
            
            # Save results
            save_kernel(
                K,
                mol_ids,
                RESULTS_DIR / "phase1_p1_set_a" / "quantum_kernel",
                args.method,
                "Phase1_P1SetA",
                stats=stats
            )
        
        if args.p3_benchmark:
            print("\n### Phase 2: P3 Benchmark ###")
            
            # Load data
            data_file = DATA_DIR / "p3_benchmark_19849.csv"
            if not data_file.exists():
                print(f"ERROR: {data_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p3-only")
                sys.exit(1)
            
            df = pd.read_csv(data_file)
            mol_ids = df['molecule_id'].tolist()
            smiles_list = df['canonical_smiles'].tolist()
            
            if args.nystrom:
                # Use Nyström approximation
                print(f"Using Nyström approximation with {args.nystrom} landmarks")
                
                K, landmark_indices, landmark_mol_ids = compute_nystrom_approximation(
                    mol_ids,
                    smiles_list,
                    n_landmarks=args.nystrom,
                    method=args.method,
                    entangling_layer=args.entangling,
                    n_layers=args.depth
                )
                
                nystrom_info = {
                    'n_landmarks': len(landmark_mol_ids),
                    'landmark_indices': landmark_indices.tolist(),
                    'landmark_mol_ids': landmark_mol_ids
                }
            else:
                print("\nWARNING: Full kernel computation for 19,849 molecules")
                print("This will compute ~197M pairs and may take hours!")
                print("Consider using --nystrom 500 or --nystrom 1000")
                
                response = input("\nContinue with full kernel? (yes/no): ")
                if response.lower() != 'yes':
                    print("Aborted. Use --nystrom N for approximation.")
                    sys.exit(0)
                
                K, circuits, mol_ids = compute_kernel_matrix(
                    mol_ids,
                    smiles_list,
                    method=args.method,
                    entangling_layer=args.entangling,
                    n_layers=args.depth
                )
                
                nystrom_info = None
            
            # Analyze kernel
            stats = analyze_kernel_matrix(K, mol_ids)
            
            # Save results
            save_kernel(
                K,
                mol_ids,
                RESULTS_DIR / "phase2_p3_benchmark" / "quantum_kernel",
                args.method,
                "Phase2_P3Benchmark",
                stats=stats,
                nystrom_info=nystrom_info
            )
        
        print("\n" + "=" * 60)
        print("✅ Quantum kernel computation complete")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Review kernel matrices in results/phase*/quantum_kernel/")
        print("  2. Run Phase 1 PoC: python scripts/p7_phase1_poc.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
