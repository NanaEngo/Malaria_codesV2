"""
P7 — Quantum Circuit Generation

Generate parameterized quantum circuits from molecular structures using
quantum molecular encoding (QMSE):
  - BondOrderMatrix / CoulombMatrix → molecular matrices
  - BondFeatureMap → parameterized quantum circuits
  - Circuit visualization and validation

Outputs:
  - results/phase1_p1_set_a/quantum_circuits/
  - Circuit parameters, qubit counts, gate counts
  - Visualization (optional, requires matplotlib)

Usage:
    python scripts/p7_quantum_circuits.py --p1-set-a --method bond_order
    python scripts/p7_quantum_circuits.py --p3-benchmark --method coulomb --sample 100
"""

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Import local QMSE library
from qmse_lib import BondOrderMatrix, CoulombMatrix
from qmse_lib.encodings import BondFeatureMap

warnings.filterwarnings('ignore')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"


def encode_molecule_to_circuit(
    smiles: str,
    method='bond_order',
    entangling_layer='rzz',
    n_layers=1,
    n_atom_to_qubit=1,
    add_hydrogens=False
):
    """
    Encode a molecule as a quantum circuit.
    
    Args:
        smiles: SMILES string
        method: 'bond_order' or 'coulomb'
        entangling_layer: 'rxx', 'ryy', or 'rzz'
        n_layers: Circuit depth
        n_atom_to_qubit: Qubits per atom
        add_hydrogens: Add explicit hydrogens
    
    Returns:
        dict with: circuit, matrix, num_qubits, gate_count
    """
    # Generate molecular matrix
    if method == 'bond_order':
        encoder = BondOrderMatrix()
    elif method == 'coulomb':
        encoder = CoulombMatrix()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    try:
        matrix = encoder.compute(smiles, add_hydrogens=add_hydrogens)
    except Exception as e:
        return {'error': str(e), 'smiles': smiles}
    
    # Determine number of qubits
    matrix_size = matrix.shape[0]
    num_qubits = matrix_size * n_atom_to_qubit
    
    # Generate quantum circuit
    try:
        circuit = BondFeatureMap(
            matrix=matrix,
            num_qubits=num_qubits,
            n_layers=n_layers,
            entangling_layer=entangling_layer,
            n_atom_to_qubit=n_atom_to_qubit,
            reverse_bits=True
        )
    except Exception as e:
        return {'error': str(e), 'smiles': smiles, 'matrix': matrix}
    
    # Count gates
    gate_count = {
        'total': len(circuit.data),
        'single_qubit': sum(1 for gate in circuit.data if len(gate.qubits) == 1),
        'two_qubit': sum(1 for gate in circuit.data if len(gate.qubits) == 2),
    }
    
    return {
        'circuit': circuit,
        'matrix': matrix,
        'num_qubits': num_qubits,
        'matrix_size': matrix_size,
        'gate_count': gate_count
    }


def process_dataset(
    csv_file: Path,
    method='bond_order',
    entangling_layer='rzz',
    n_layers=1,
    n_atom_to_qubit=1,
    max_samples=None,
    smiles_col='canonical_smiles'
):
    """
    Process a dataset and generate quantum circuits for all molecules.
    
    Returns:
        results_df: DataFrame with circuit parameters
        circuits: Dict of {molecule_id: circuit_data}
    """
    print(f"\nProcessing: {csv_file}")
    df = pd.read_csv(csv_file)
    
    if max_samples:
        df = df.head(max_samples)
        print(f"Sampling first {max_samples} molecules")
    
    print(f"Total molecules: {len(df)}")
    print(f"Encoding method: {method}")
    print(f"Entangling layer: {entangling_layer}")
    print(f"Circuit depth: {n_layers}")
    
    results = []
    circuits = {}
    failed_count = 0
    
    for idx, row in df.iterrows():
        mol_id = row.get('molecule_id', f'mol_{idx}')
        smiles = row[smiles_col]
        
        result = encode_molecule_to_circuit(
            smiles=smiles,
            method=method,
            entangling_layer=entangling_layer,
            n_layers=n_layers,
            n_atom_to_qubit=n_atom_to_qubit
        )
        
        if 'error' in result:
            failed_count += 1
            results.append({
                'molecule_id': mol_id,
                'smiles': smiles,
                'success': False,
                'error': result['error']
            })
        else:
            circuits[mol_id] = result
            
            results.append({
                'molecule_id': mol_id,
                'smiles': smiles,
                'success': True,
                'num_qubits': result['num_qubits'],
                'matrix_size': result['matrix_size'],
                'total_gates': result['gate_count']['total'],
                'single_qubit_gates': result['gate_count']['single_qubit'],
                'two_qubit_gates': result['gate_count']['two_qubit'],
            })
        
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(df)} molecules (failed: {failed_count})")
    
    print(f"\nTotal: {len(df)} | Success: {len(df) - failed_count} | Failed: {failed_count}")
    
    results_df = pd.DataFrame(results)
    return results_df, circuits


def analyze_circuits(results_df):
    """Analyze circuit statistics."""
    successful = results_df[results_df['success'] == True]
    
    if len(successful) == 0:
        print("\nWARNING: No successful circuits generated")
        return {}
    
    stats = {
        'n_successful': len(successful),
        'n_failed': len(results_df) - len(successful),
        'qubit_stats': {
            'min': int(successful['num_qubits'].min()),
            'max': int(successful['num_qubits'].max()),
            'mean': float(successful['num_qubits'].mean()),
            'median': float(successful['num_qubits'].median()),
        },
        'gate_stats': {
            'total_min': int(successful['total_gates'].min()),
            'total_max': int(successful['total_gates'].max()),
            'total_mean': float(successful['total_gates'].mean()),
            'single_qubit_mean': float(successful['single_qubit_gates'].mean()),
            'two_qubit_mean': float(successful['two_qubit_gates'].mean()),
        },
    }
    
    print("\n=== Circuit Statistics ===")
    print(f"Successful: {stats['n_successful']}")
    print(f"Failed: {stats['n_failed']}")
    print(f"\nQubits: {stats['qubit_stats']['min']} - {stats['qubit_stats']['max']} (mean: {stats['qubit_stats']['mean']:.1f})")
    print(f"Gates (total): {stats['gate_stats']['total_min']} - {stats['gate_stats']['total_max']} (mean: {stats['gate_stats']['total_mean']:.1f})")
    print(f"  Single-qubit: {stats['gate_stats']['single_qubit_mean']:.1f}")
    print(f"  Two-qubit: {stats['gate_stats']['two_qubit_mean']:.1f}")
    
    return stats


def save_results(results_df, stats, output_dir, phase_name, method):
    """Save circuit generation results."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save circuit parameters
    results_file = output_dir / f"quantum_circuits_{method}.csv"
    results_df.to_csv(results_file, index=False)
    print(f"\nSaved circuit parameters: {results_file}")
    
    # Save statistics
    stats_file = output_dir / f"quantum_circuits_{method}_stats.json"
    with open(stats_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'phase': phase_name,
            'method': method,
            'statistics': stats
        }, f, indent=2)
    print(f"Saved statistics: {stats_file}")


def main():
    parser = argparse.ArgumentParser(description="P7 Quantum Circuit Generation")
    parser.add_argument('--p1-set-a', action='store_true', help="Generate circuits for P1 Set A")
    parser.add_argument('--p3-benchmark', action='store_true', help="Generate circuits for P3 benchmark")
    parser.add_argument('--method', choices=['bond_order', 'coulomb'], default='bond_order',
                        help="Encoding method (default: bond_order)")
    parser.add_argument('--entangling', choices=['rxx', 'ryy', 'rzz'], default='rzz',
                        help="Entangling layer (default: rzz)")
    parser.add_argument('--depth', type=int, default=1, help="Circuit depth (default: 1)")
    parser.add_argument('--sample', type=int, default=None,
                        help="Sample N molecules (for testing)")
    
    args = parser.parse_args()
    
    if not any([args.p1_set_a, args.p3_benchmark]):
        print("ERROR: Specify --p1-set-a or --p3-benchmark")
        sys.exit(1)
    
    print("=" * 60)
    print("P7 Quantum Circuit Generation")
    print("=" * 60)
    
    try:
        if args.p1_set_a:
            print("\n### Phase 1: P1 Set A ###")
            
            csv_file = DATA_DIR / "p1_set_a_20_candidates.csv"
            if not csv_file.exists():
                print(f"ERROR: {csv_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p1-only")
                sys.exit(1)
            
            results_df, circuits = process_dataset(
                csv_file=csv_file,
                method=args.method,
                entangling_layer=args.entangling,
                n_layers=args.depth,
                max_samples=args.sample
            )
            
            stats = analyze_circuits(results_df)
            
            save_results(
                results_df,
                stats,
                RESULTS_DIR / "phase1_p1_set_a" / "quantum_circuits",
                "Phase1_P1SetA",
                args.method
            )
        
        if args.p3_benchmark:
            print("\n### Phase 2: P3 Benchmark ###")
            
            csv_file = DATA_DIR / "p3_benchmark_19849.csv"
            if not csv_file.exists():
                print(f"ERROR: {csv_file} not found")
                print("Run: python scripts/p7_data_preparation.py --p3-only")
                sys.exit(1)
            
            results_df, circuits = process_dataset(
                csv_file=csv_file,
                method=args.method,
                entangling_layer=args.entangling,
                n_layers=args.depth,
                max_samples=args.sample
            )
            
            stats = analyze_circuits(results_df)
            
            save_results(
                results_df,
                stats,
                RESULTS_DIR / "phase2_p3_benchmark" / "quantum_circuits",
                "Phase2_P3Benchmark",
                args.method
            )
        
        print("\n" + "=" * 60)
        print("✅ Quantum circuit generation complete")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Review circuit parameters in results/phase*/quantum_circuits/")
        print("  2. Run quantum kernel: python scripts/p7_quantum_kernel.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
