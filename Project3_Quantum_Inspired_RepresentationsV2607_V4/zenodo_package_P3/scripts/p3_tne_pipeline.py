#!/usr/bin/env python3
"""
P3 — Tensor Network Embedding (TNE) Pipeline

Generates tensor network embeddings using Tucker decomposition.
Compresses molecular representations with bond_dim=8, Tucker ranks=(8,8,3).

This is a template/reference script. The actual P3 TNE computation was performed
using the workflow described in the P3_DATA_ANALYSIS_REPORT.md. The output data
(p3_tne_embeddings.csv) is provided in the data/ directory.

Requirements:
    - tensorly >= 0.8.1
    - rdkit >= 2025.03.6
    - numpy >= 2.2.1
    - pandas >= 2.2.3

Key Parameters (from P3 DAR):
    - Bond dimension: 8
    - Tucker ranks: (8, 8, 3)
    - Output dimension: 192
    - Mean compression: 6.1x
    - Reconstruction error: mean=0.113, max=0.220
    - Failures: 13 out of 19,849 molecules

Usage:
    python p3_tne_pipeline.py --input molecules.csv --output p3_tne_embeddings.csv
"""

import argparse
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

try:
    import tensorly as tl
    from tensorly.decomposition import tucker
except ImportError:
    print("Warning: tensorly not installed. Install with: pip install tensorly")
    tl = None


def smiles_to_tensor(smiles, max_atoms=50, bond_dim=8):
    """
    Convert SMILES to tensor representation for TNE.
    
    Args:
        smiles (str): SMILES string
        max_atoms (int): Maximum number of atoms to consider
        bond_dim (int): Bond dimension (default: 8)
        
    Returns:
        np.ndarray: Tensor representation (max_atoms x max_atoms x bond_dim)
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    n_atoms = min(mol.GetNumAtoms(), max_atoms)
    if n_atoms == 0:
        return None
    
    # Initialize tensor
    tensor = np.zeros((max_atoms, max_atoms, bond_dim))
    
    # Encode atoms (one-hot by atomic number)
    for i in range(n_atoms):
        atom = mol.GetAtomWithIdx(i)
        atomic_num = min(atom.GetAtomicNum(), bond_dim-1)
        tensor[i, i, atomic_num] = 1.0
    
    # Encode bonds
    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()
        if i < max_atoms and j < max_atoms:
            bond_type = bond.GetBondTypeAsDouble()
            bond_idx = min(int(bond_type), bond_dim-1)
            tensor[i, j, bond_idx] = 1.0
            tensor[j, i, bond_idx] = 1.0
    
    return tensor


def tucker_decompose(tensor, tucker_ranks=(8, 8, 3)):
    """
    Perform Tucker decomposition on molecular tensor.
    
    Args:
        tensor (np.ndarray): Input tensor (I x J x K)
        tucker_ranks (tuple): Tucker ranks for each mode
        
    Returns:
        tuple: (core_tensor, factors, reconstruction_error)
    """
    if tl is None:
        raise ImportError("tensorly library required")
    
    try:
        # Tucker decomposition
        core, factors = tucker(tensor, rank=tucker_ranks)
        
        # Compute reconstruction
        reconstruction = tl.tucker_to_tensor((core, factors))
        
        # Reconstruction error
        error = np.linalg.norm(tensor - reconstruction) / np.linalg.norm(tensor)
        
        return core, factors, error
    
    except Exception as e:
        return None, None, None


def extract_tne_embedding(core, factors):
    """
    Extract 192-dimensional embedding from Tucker decomposition.
    
    Output dimension: prod(tucker_ranks) = 8*8*3 = 192
    
    Args:
        core (np.ndarray): Core tensor from Tucker decomposition
        factors (list): Factor matrices
        
    Returns:
        np.ndarray: 192-dimensional embedding
    """
    # Flatten core tensor
    embedding = core.flatten()
    
    # Expected dimension: 192
    if len(embedding) != 192:
        # Pad or truncate to 192
        if len(embedding) < 192:
            embedding = np.pad(embedding, (0, 192 - len(embedding)))
        else:
            embedding = embedding[:192]
    
    return embedding


def process_molecule(smiles, bond_dim=8, tucker_ranks=(8, 8, 3)):
    """
    Process single molecule: SMILES → Tensor → Tucker → Embedding
    
    Args:
        smiles (str): SMILES string
        bond_dim (int): Bond dimension
        tucker_ranks (tuple): Tucker ranks
        
    Returns:
        tuple: (embedding, reconstruction_error) or (None, None) if failed
    """
    try:
        # Convert to tensor
        tensor = smiles_to_tensor(smiles, bond_dim=bond_dim)
        if tensor is None:
            return None, None
        
        # Tucker decomposition
        core, factors, error = tucker_decompose(tensor, tucker_ranks=tucker_ranks)
        if core is None:
            return None, None
        
        # Extract embedding
        embedding = extract_tne_embedding(core, factors)
        
        return embedding, error
    
    except Exception as e:
        print(f"Error processing {smiles}: {e}")
        return None, None


def main():
    parser = argparse.ArgumentParser(description="P3 TNE Pipeline")
    parser.add_argument("--input", required=True, help="Input CSV with SMILES column")
    parser.add_argument("--output", required=True, help="Output CSV with TNE embeddings")
    parser.add_argument("--smiles-col", default="smiles", help="SMILES column name")
    parser.add_argument("--bond-dim", type=int, default=8, help="Bond dimension (default: 8)")
    parser.add_argument("--tucker-ranks", nargs=3, type=int, default=[8, 8, 3],
                       help="Tucker ranks (default: 8 8 3)")
    args = parser.parse_args()
    
    if tl is None:
        raise ImportError("tensorly library is required. Install with: pip install tensorly")
    
    tucker_ranks = tuple(args.tucker_ranks)
    
    # Load data
    print(f"Loading data from {args.input}...")
    df = pd.read_csv(args.input)
    
    if args.smiles_col not in df.columns:
        raise ValueError(f"Column '{args.smiles_col}' not found in input CSV")
    
    # Process molecules
    print(f"Processing {len(df)} molecules...")
    print(f"Bond dimension: {args.bond_dim}")
    print(f"Tucker ranks: {tucker_ranks}")
    print(f"Output dimension: {np.prod(tucker_ranks)}")
    
    embeddings = []
    errors = []
    failed_indices = []
    
    for idx, smiles in enumerate(df[args.smiles_col]):
        if idx % 100 == 0:
            print(f"  Processed {idx}/{len(df)} molecules...")
        
        embedding, error = process_molecule(smiles, bond_dim=args.bond_dim, 
                                           tucker_ranks=tucker_ranks)
        
        if embedding is not None:
            embeddings.append(embedding)
            errors.append(error)
        else:
            embeddings.append(np.full(192, np.nan))  # Mark failures
            errors.append(np.nan)
            failed_indices.append(idx)
    
    # Create output DataFrame
    tne_df = pd.DataFrame(embeddings, columns=[f"TNE_{i}" for i in range(192)])
    tne_df.insert(0, args.smiles_col, df[args.smiles_col])
    tne_df['reconstruction_error'] = errors
    
    # Save
    tne_df.to_csv(args.output, index=False)
    print(f"\nSaved TNE embeddings to {args.output}")
    print(f"Successes: {len(df) - len(failed_indices)}/{len(df)}")
    print(f"Failures: {len(failed_indices)}")
    
    if errors:
        valid_errors = [e for e in errors if not np.isnan(e)]
        if valid_errors:
            print(f"Mean reconstruction error: {np.mean(valid_errors):.4f}")
            print(f"Max reconstruction error: {np.max(valid_errors):.4f}")


if __name__ == "__main__":
    main()
