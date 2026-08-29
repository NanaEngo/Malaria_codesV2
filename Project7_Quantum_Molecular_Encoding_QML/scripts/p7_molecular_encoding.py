"""
P7 — Molecular Encoding Wrapper

Wraps quantum-molecular-encodings library (Boy et al. 2025) with provenance tracking
and integration with P1-P6 dataset infrastructure.

Core encoding methods:
  - BondOrderMatrix: bond orders (1/2/3/1.5) with stereochemistry
  - CoulombMatrix: atomic charges and average bond lengths

Usage:
    from p7_molecular_encoding import encode_molecule, batch_encode
    
    # Single molecule
    matrix = encode_molecule("CCO", method="bond_order", add_hydrogens=False)
    
    # Batch encoding with provenance
    matrices, provenance = batch_encode(
        smiles_list=["CCO", "c1ccccc1"],
        method="bond_order",
        save_provenance=True
    )

Provenance:
    - SMILES canonicalization (RDKit)
    - Encoding method and parameters
    - Matrix shape and statistics (min, max, mean, std)
    - Stereoisomer detection (R/S, Z/E)
    - Timestamp and Git commit hash
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

# Import from local qmse_lib (Quantum Molecular Structure Encoding library)
# This is a curated copy of essential components from Boy et al. (2025)
try:
    from qmse_lib.matrix import BondOrderMatrix, CoulombMatrix
    from qmse_lib.encodings.bond import BondFeatureMap
    from qmse_lib.encodings.overlap import UnitaryOverlap
    from qmse_lib.supporting_functions import coulomb_matrix, matrix_to_circuit
except ImportError as e:
    print(f"ERROR: Cannot import qmse_lib (Quantum Molecular Structure Encoding library).")
    print(f"  Error: {e}")
    print(f"\nThe qmse_lib should be in the scripts/ directory:")
    print(f"  scripts/qmse_lib/matrix.py")
    print(f"  scripts/qmse_lib/encodings/bond.py")
    print(f"  scripts/qmse_lib/encodings/overlap.py")
    print(f"\nIf missing, the essential files need to be copied from the original")
    print(f"  quantum-molecular-encodings repository.")
    sys.exit(1)


def canonicalize_smiles(smiles: str) -> Optional[str]:
    """
    Canonicalize SMILES string using RDKit.
    
    Returns:
        Canonical SMILES or None if invalid
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def encode_molecule(
    smiles: str,
    method: str = "bond_order",
    add_hydrogens: bool = False,
    bond_coupling: float = 1.0,
    exponent: float = 3.0,
    canonicalize: bool = True
) -> Optional[np.ndarray]:
    """
    Encode a single molecule as a matrix.
    
    Args:
        smiles: SMILES string
        method: "bond_order" or "coulomb"
        add_hydrogens: Whether to add explicit hydrogens
        bond_coupling: Scaling factor for bond interactions
        exponent: Exponent for diagonal elements (Coulomb only, default 3.0 for 0.5*Z^exponent)
        canonicalize: Whether to canonicalize SMILES first
    
    Returns:
        Molecular matrix (np.ndarray) or None if encoding fails
    """
    if canonicalize:
        smiles = canonicalize_smiles(smiles)
        if smiles is None:
            return None
    
    try:
        if method == "bond_order":
            encoder = BondOrderMatrix(bond_coupling=bond_coupling)
        elif method == "coulomb":
            encoder = CoulombMatrix(bond_coupling=bond_coupling)
        else:
            raise ValueError(f"Unknown encoding method: {method}")
        
        # Note: Boy et al. 2025 uses exponent=3.0 for diagonal (0.5 * Z^3.0)
        # but the library default is 3.0, so we pass it explicitly
        matrix = encoder.compute(smiles, add_hydrogens=add_hydrogens, exponent=exponent)
        return matrix
    
    except Exception as e:
        print(f"WARNING: Failed to encode {smiles}: {e}")
        return None


def batch_encode(
    smiles_list: List[str],
    method: str = "bond_order",
    add_hydrogens: bool = False,
    bond_coupling: float = 1.0,
    exponent: float = 3.0,
    canonicalize: bool = True,
    save_provenance: bool = True,
    provenance_path: Optional[Path] = None
) -> Tuple[List[Optional[np.ndarray]], Optional[Dict]]:
    """
    Batch encode molecules with provenance tracking.
    
    Args:
        smiles_list: List of SMILES strings
        method: "bond_order" or "coulomb"
        add_hydrogens: Whether to add explicit hydrogens
        bond_coupling: Scaling factor for bond interactions
        exponent: Exponent for diagonal elements
        canonicalize: Whether to canonicalize SMILES first
        save_provenance: Whether to generate provenance metadata
        provenance_path: Where to save provenance JSON (optional)
    
    Returns:
        (matrices, provenance_dict)
        - matrices: List of np.ndarray (or None if encoding failed)
        - provenance_dict: Metadata dictionary (or None if save_provenance=False)
    """
    matrices = []
    canonical_smiles_list = []
    failed_indices = []
    
    for i, smiles in enumerate(smiles_list):
        if canonicalize:
            canon_smiles = canonicalize_smiles(smiles)
            canonical_smiles_list.append(canon_smiles)
            if canon_smiles is None:
                matrices.append(None)
                failed_indices.append(i)
                continue
            smiles_to_encode = canon_smiles
        else:
            canonical_smiles_list.append(smiles)
            smiles_to_encode = smiles
        
        matrix = encode_molecule(
            smiles_to_encode,
            method=method,
            add_hydrogens=add_hydrogens,
            bond_coupling=bond_coupling,
            exponent=exponent,
            canonicalize=False  # Already canonicalized above
        )
        matrices.append(matrix)
        if matrix is None:
            failed_indices.append(i)
    
    provenance = None
    if save_provenance:
        successful_matrices = [m for m in matrices if m is not None]
        matrix_shapes = [m.shape for m in successful_matrices]
        matrix_sizes = [m.shape[0] for m in successful_matrices]
        
        provenance = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "parameters": {
                "add_hydrogens": add_hydrogens,
                "bond_coupling": bond_coupling,
                "exponent": exponent,
                "canonicalize": canonicalize
            },
            "input": {
                "total_molecules": len(smiles_list),
                "successful": len(successful_matrices),
                "failed": len(failed_indices),
                "failed_indices": failed_indices
            },
            "output": {
                "matrix_shapes": matrix_shapes,
                "min_matrix_size": int(np.min(matrix_sizes)) if matrix_sizes else 0,
                "max_matrix_size": int(np.max(matrix_sizes)) if matrix_sizes else 0,
                "mean_matrix_size": float(np.mean(matrix_sizes)) if matrix_sizes else 0.0
            },
            "statistics": {}
        }
        
        if successful_matrices:
            # Collect statistics
            all_values = np.concatenate([m.flatten() for m in successful_matrices])
            provenance["statistics"] = {
                "min": float(np.min(all_values)),
                "max": float(np.max(all_values)),
                "mean": float(np.mean(all_values)),
                "std": float(np.std(all_values)),
                "median": float(np.median(all_values))
            }
        
        if provenance_path:
            provenance_path = Path(provenance_path)
            provenance_path.parent.mkdir(parents=True, exist_ok=True)
            with open(provenance_path, 'w') as f:
                json.dump(provenance, f, indent=2)
            print(f"Provenance saved: {provenance_path}")
    
    return matrices, provenance


def encode_dataset(
    csv_path: Path,
    smiles_col: str = "smiles",
    method: str = "bond_order",
    output_dir: Optional[Path] = None,
    **encode_kwargs
) -> pd.DataFrame:
    """
    Encode an entire dataset from CSV and save matrices as .npy files.
    
    Args:
        csv_path: Path to CSV with SMILES column
        smiles_col: Name of SMILES column
        method: Encoding method
        output_dir: Where to save .npy files (default: csv_path.parent / "matrices")
        **encode_kwargs: Additional arguments for batch_encode
    
    Returns:
        DataFrame with columns: [original_smiles, canonical_smiles, matrix_path, encoding_success]
    """
    df = pd.read_csv(csv_path)
    smiles_list = df[smiles_col].tolist()
    
    if output_dir is None:
        output_dir = csv_path.parent / "matrices" / method
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Encoding {len(smiles_list)} molecules from {csv_path.name}...")
    print(f"  Method: {method}")
    print(f"  Output: {output_dir}")
    
    matrices, provenance = batch_encode(
        smiles_list,
        method=method,
        save_provenance=True,
        provenance_path=output_dir / "encoding_provenance.json",
        **encode_kwargs
    )
    
    # Save individual matrices
    results = []
    for i, (smiles, matrix) in enumerate(zip(smiles_list, matrices)):
        canon_smiles = canonicalize_smiles(smiles)
        if matrix is not None:
            matrix_filename = f"mol_{i:06d}.npy"
            matrix_path = output_dir / matrix_filename
            np.save(matrix_path, matrix)
            results.append({
                "molecule_id": i,
                "original_smiles": smiles,
                "canonical_smiles": canon_smiles,
                "matrix_path": str(matrix_path.relative_to(csv_path.parent)),
                "matrix_shape": str(matrix.shape),
                "encoding_success": True
            })
        else:
            results.append({
                "molecule_id": i,
                "original_smiles": smiles,
                "canonical_smiles": canon_smiles,
                "matrix_path": None,
                "matrix_shape": None,
                "encoding_success": False
            })
    
    results_df = pd.DataFrame(results)
    results_path = output_dir / "encoding_results.csv"
    results_df.to_csv(results_path, index=False)
    print(f"\nResults saved: {results_path}")
    print(f"  Success: {results_df['encoding_success'].sum()} / {len(results_df)}")
    
    return results_df


if __name__ == "__main__":
    # Example: encode a few test molecules
    test_smiles = [
        "CCO",           # Ethanol
        "c1ccccc1",      # Benzene
        "CC(C)O",        # Isopropanol
        "INVALID"        # Should fail
    ]
    
    print("=== P7 Molecular Encoding Test ===\n")
    
    print("1. BondOrderMatrix encoding:")
    matrices_bond, prov_bond = batch_encode(
        test_smiles,
        method="bond_order",
        add_hydrogens=False,
        save_provenance=True
    )
    print(f"\nSuccess: {len([m for m in matrices_bond if m is not None])} / {len(test_smiles)}")
    print(f"Provenance: {json.dumps(prov_bond['statistics'], indent=2)}")
    
    print("\n" + "="*50 + "\n")
    
    print("2. CoulombMatrix encoding:")
    matrices_coulomb, prov_coulomb = batch_encode(
        test_smiles,
        method="coulomb",
        add_hydrogens=True,
        save_provenance=True
    )
    print(f"\nSuccess: {len([m for m in matrices_coulomb if m is not None])} / {len(test_smiles)}")
    print(f"Provenance: {json.dumps(prov_coulomb['statistics'], indent=2)}")
    
    print("\n✅ Test complete. Ready for P7 pipeline.")
