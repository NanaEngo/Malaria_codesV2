#!/usr/bin/env python3
"""
P3 — Topological Data Analysis (TDA) Fingerprint Pipeline

Generates topological fingerprints using persistent homology (Gudhi library).
Computes Vietoris-Rips filtration on molecular graphs to extract H0 and H1 features.

This is a template/reference script. The actual P3 TDA computation was performed
using the workflow described in the P3_DATA_ANALYSIS_REPORT.md. The output data
(p3_tda_fingerprints.csv) is provided in the data/ directory.

Requirements:
    - gudhi >= 3.10.1
    - rdkit >= 2025.03.6
    - numpy >= 2.2.1
    - pandas >= 2.2.3

Usage:
    python p3_tda_pipeline.py --input molecules.csv --output p3_tda_fingerprints.csv

References:
    - Gudhi documentation: https://gudhi.inria.fr/
    - P3 manuscript: Section 2.2 (Topological Fingerprints)
"""

import argparse
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

try:
    import gudhi
except ImportError:
    print("Warning: gudhi not installed. Install with: conda install -c conda-forge gudhi")
    gudhi = None


def smiles_to_distance_matrix(smiles):
    """
    Convert SMILES to distance matrix for TDA.
    
    Args:
        smiles (str): Canonical SMILES string
        
    Returns:
        np.ndarray: Distance matrix (N x N) where N = number of atoms
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    # Get 3D coordinates (or use 2D if 3D fails)
    try:
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.UFFOptimizeMolecule(mol)
        conf = mol.GetConformer()
        coords = np.array([conf.GetAtomPosition(i) for i in range(mol.GetNumAtoms())])
    except:
        # Fallback to 2D coordinates
        AllChem.Compute2DCoords(mol)
        conf = mol.GetConformer()
        coords = np.array([[conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, 0] 
                          for i in range(mol.GetNumAtoms())])
    
    # Compute pairwise distances
    n_atoms = len(coords)
    dist_matrix = np.zeros((n_atoms, n_atoms))
    for i in range(n_atoms):
        for j in range(i+1, n_atoms):
            dist = np.linalg.norm(coords[i] - coords[j])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    
    return dist_matrix


def compute_persistence(distance_matrix, max_dimension=1):
    """
    Compute persistent homology using Vietoris-Rips filtration.
    
    Args:
        distance_matrix (np.ndarray): Distance matrix
        max_dimension (int): Maximum homology dimension (default: 1 for H0 and H1)
        
    Returns:
        list: Persistence diagrams [(birth, death, dimension), ...]
    """
    if gudhi is None:
        raise ImportError("gudhi library required")
    
    # Create Rips complex
    rips_complex = gudhi.RipsComplex(distance_matrix=distance_matrix, max_edge_length=np.inf)
    simplex_tree = rips_complex.create_simplex_tree(max_dimension=max_dimension)
    
    # Compute persistence
    persistence = simplex_tree.persistence()
    
    return persistence


def extract_tda_features(persistence, n_bins=42):
    """
    Extract 84-dimensional TDA fingerprint from persistence diagram.
    
    Features:
        - H0 (connected components): 42 features
        - H1 (loops/cycles): 42 features
    
    Args:
        persistence (list): Persistence pairs from gudhi
        n_bins (int): Number of bins per homology dimension
        
    Returns:
        np.ndarray: 84-dimensional feature vector
    """
    features = np.zeros(2 * n_bins)  # 84 features total
    
    # Separate H0 and H1 persistence pairs
    h0_pairs = [(birth, death) for dim, (birth, death) in persistence if dim == 0 and death != np.inf]
    h1_pairs = [(birth, death) for dim, (birth, death) in persistence if dim == 1 and death != np.inf]
    
    # Compute persistence for each pair (death - birth)
    h0_pers = [death - birth for birth, death in h0_pairs]
    h1_pers = [death - birth for birth, death in h1_pairs]
    
    # Histogram-based features
    if h0_pers:
        features[:n_bins], _ = np.histogram(h0_pers, bins=n_bins, range=(0, max(h0_pers)))
    
    if h1_pers:
        features[n_bins:], _ = np.histogram(h1_pers, bins=n_bins, range=(0, max(h1_pers)))
    
    return features


def process_molecule(smiles):
    """
    Process single molecule: SMILES → Distance matrix → Persistence → Features
    
    Args:
        smiles (str): SMILES string
        
    Returns:
        np.ndarray or None: 84-dimensional TDA fingerprint, or None if failed
    """
    try:
        # Convert to distance matrix
        dist_matrix = smiles_to_distance_matrix(smiles)
        if dist_matrix is None:
            return None
        
        # Compute persistence
        persistence = compute_persistence(dist_matrix, max_dimension=1)
        
        # Extract features
        features = extract_tda_features(persistence)
        
        return features
    
    except Exception as e:
        print(f"Error processing {smiles}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="P3 TDA Fingerprint Pipeline")
    parser.add_argument("--input", required=True, help="Input CSV with SMILES column")
    parser.add_argument("--output", required=True, help="Output CSV with TDA features")
    parser.add_argument("--smiles-col", default="smiles", help="SMILES column name")
    args = parser.parse_args()
    
    if gudhi is None:
        raise ImportError("gudhi library is required. Install with: conda install -c conda-forge gudhi")
    
    # Load data
    print(f"Loading data from {args.input}...")
    df = pd.read_csv(args.input)
    
    if args.smiles_col not in df.columns:
        raise ValueError(f"Column '{args.smiles_col}' not found in input CSV")
    
    # Process molecules
    print(f"Processing {len(df)} molecules...")
    tda_features = []
    failed_indices = []
    
    for idx, smiles in enumerate(df[args.smiles_col]):
        if idx % 100 == 0:
            print(f"  Processed {idx}/{len(df)} molecules...")
        
        features = process_molecule(smiles)
        
        if features is not None:
            tda_features.append(features)
        else:
            tda_features.append(np.full(84, np.nan))  # Mark failures
            failed_indices.append(idx)
    
    # Create output DataFrame
    tda_df = pd.DataFrame(tda_features, columns=[f"TDA_{i}" for i in range(84)])
    tda_df.insert(0, args.smiles_col, df[args.smiles_col])
    
    # Save
    tda_df.to_csv(args.output, index=False)
    print(f"\nSaved TDA fingerprints to {args.output}")
    print(f"Successes: {len(df) - len(failed_indices)}/{len(df)}")
    print(f"Failures: {len(failed_indices)}")
    
    if failed_indices:
        print(f"Failed indices: {failed_indices[:10]}{'...' if len(failed_indices) > 10 else ''}")


if __name__ == "__main__":
    main()
