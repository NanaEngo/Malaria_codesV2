#!/usr/bin/env python3
"""
P3 H1-RRS Definitive Expansion: Compute TFP for 500+ RRS compounds.

Expands the headline Spearman rho=0.947 (n=14) correlation between H1
topological persistence and Resistance Resilience Scores (RRS) to n>=80
with balanced class representation.

This script:
1. Loads the 501-compound RRS dataset (p3_rrs_expanded_v2.csv)
2. Identifies compounds lacking TFP features
3. Computes 78-D TFP for missing compounds using the TDA pipeline
4. Merges RRS + TFP into a unified dataset
5. Computes the definitive H1-RRS correlation across all classes

Usage:
    python p3_rrs_tfp_expansion.py --start-idx 0 --end-idx 500 --task-id 0
"""

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")

# Ripser import
try:
    from ripser import ripser
    _HAS_RIPSER = True
except ImportError:
    ripser = None
    _HAS_RIPSER = False

# ── Configuration ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # Malaria_codesV2

RRS_INPUT = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results' / 'p3_rrs_expanded_v2.csv'
TFP_EXISTING = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results' / 'p3_rrs_expanded_with_tfp_v2.csv'
OUTPUT_DIR = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results'

# TDA parameters (from p3_tda_pipeline.py)
PERSISTENCE_THRESHOLD = 0.5
MAX_ATOMS = 100
MAX_DIM = 2
N_PERS_IMAGE = 25
N_BETTI = 20

BASE_FEATURES = ["entropy", "count", "max_pers", "mean_pers",
                 "birth_mean", "birth_std", "death_mean", "death_std",
                 "pers_q25", "pers_q50", "pers_q75"]

TFP_COLUMNS = (
    [f"H{d}_{feat}" for d in range(MAX_DIM + 1) for feat in BASE_FEATURES]
    + [f"pers_img_{i}" for i in range(N_PERS_IMAGE)]
    + [f"betti_{i}" for i in range(N_BETTI)]
)


# ── TDA functions (adapted from p3_tda_pipeline.py) ───────────────────────

def _weight_distance_matrix(d, atomic_nums):
    Z_outer = np.outer(atomic_nums, atomic_nums)
    w = d * (1.0 + Z_outer / 100.0)
    np.fill_diagonal(w, 0.0)
    return w


def _distance_matrix_from_conformer(mol, conf_id=0):
    conf = mol.GetConformer(conf_id)
    atoms = list(mol.GetAtoms())[:MAX_ATOMS]
    n = len(atoms)
    if n < 2:
        return None
    coords = np.array([conf.GetAtomPosition(a.GetIdx()) for a in atoms])
    atomic_nums = np.array([a.GetAtomicNum() for a in atoms], dtype=float)
    return coords, atomic_nums


def _distance_matrix_3d(mol):
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    params.useRandomCoords = True
    if AllChem.EmbedMolecule(mol, params) != 0:
        return None
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
    except Exception:
        pass
    result = _distance_matrix_from_conformer(mol)
    if result is None:
        return None
    coords, atomic_nums = result
    diff = coords[:, None, :] - coords[None, :, :]
    d = np.sqrt((diff ** 2).sum(axis=-1))
    return _weight_distance_matrix(d, atomic_nums)


def _distance_matrix_2d(mol):
    atoms = list(mol.GetAtoms())[:MAX_ATOMS]
    n = len(atoms)
    if n < 2:
        return None
    atomic_nums = np.array([a.GetAtomicNum() for a in atoms], dtype=float)
    adj = np.full((n, n), np.inf)
    np.fill_diagonal(adj, 0.0)
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if i < n and j < n:
            order = bond.GetBondTypeAsDouble()
            adj[i, j] = 1.0 / order
            adj[j, i] = 1.0 / order
    dist = adj.copy()
    for k in range(n):
        dist_k = dist[k, :][None, :]
        dist_ik = dist[:, k][:, None]
        candidate = dist_ik + dist_k
        dist = np.minimum(dist, candidate)
    return _weight_distance_matrix(dist, atomic_nums)


def smiles_to_distance_matrix(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    dm = _distance_matrix_3d(mol)
    if dm is not None:
        return dm
    dm = _distance_matrix_2d(mol)
    if dm is not None:
        return dm
    return None


def compute_persistence(dist_matrix):
    if not _HAS_RIPSER:
        raise ImportError("ripser not installed")
    result = ripser(dist_matrix, maxdim=MAX_DIM, distance_matrix=True)
    return result["dgms"]


def persistence_entropy(dgm):
    finite = dgm[np.isfinite(dgm[:, 1])]
    if len(finite) == 0:
        return 0.0
    pers = finite[:, 1] - finite[:, 0]
    pers = pers[pers > 0]
    if len(pers) == 0:
        return 0.0
    total = pers.sum()
    p = pers / total
    return float(-np.sum(p * np.log(p + 1e-12)))


def persistence_image(dgm, n_bins=25, threshold=2.0):
    finite = dgm[np.isfinite(dgm[:, 1])]
    if len(finite) == 0:
        return np.zeros(n_bins, dtype=np.float32)
    pers = finite[:, 1] - finite[:, 0]
    pers = pers[pers > 0]
    if len(pers) == 0 or pers.max() == 0:
        return np.zeros(n_bins, dtype=np.float32)
    pers = np.clip(pers, 0, threshold)
    weights = pers / pers.max()
    bins = np.linspace(0, threshold, n_bins + 1)
    img, _ = np.histogram(pers, bins=bins, weights=weights)
    s = img.sum()
    if s > 0:
        img = img / s
    return img.astype(np.float32)


def betti_curve(dgm, n_points=20, max_scale=5.0):
    finite = dgm[np.isfinite(dgm[:, 1])]
    if len(finite) == 0:
        return np.zeros(n_points, dtype=np.float32)
    births = finite[:, 0]
    deaths = np.clip(finite[:, 1], 0, max_scale)
    scales = np.linspace(0, max_scale, n_points)
    curve = np.zeros(n_points, dtype=np.float32)
    for s_idx, s in enumerate(scales):
        curve[s_idx] = np.sum((births < (s + 1e-6)) & (deaths >= s))
    m = curve.max()
    if m > 0:
        curve = curve / m
    return curve


def extract_tfp(diagrams):
    features = []
    for dim in range(MAX_DIM + 1):
        if dim >= len(diagrams):
            features.extend([0.0] * len(BASE_FEATURES))
            continue
        dgm = diagrams[dim]
        finite = dgm[np.isfinite(dgm[:, 1])]
        pers = (finite[:, 1] - finite[:, 0]) if len(finite) > 0 else np.array([])
        above_noise = pers[pers > PERSISTENCE_THRESHOLD] if len(pers) > 0 else pers
        entropy = persistence_entropy(dgm)
        count = float(np.sum(pers > PERSISTENCE_THRESHOLD))
        max_pers = float(pers.max()) if len(pers) > 0 else 0.0
        mean_pers = float(pers.mean()) if len(pers) > 0 else 0.0
        birth_mean = float(finite[:, 0].mean()) if len(finite) > 0 else 0.0
        birth_std = float(finite[:, 0].std()) if len(finite) > 0 else 0.0
        death_mean = float(finite[:, 1].mean()) if len(finite) > 0 else 0.0
        death_std = float(finite[:, 1].std()) if len(finite) > 0 else 0.0
        pers_q25 = float(np.percentile(above_noise, 25)) if len(above_noise) > 0 else 0.0
        pers_q50 = float(np.percentile(above_noise, 50)) if len(above_noise) > 0 else 0.0
        pers_q75 = float(np.percentile(above_noise, 75)) if len(above_noise) > 0 else 0.0
        features.extend([entropy, count, max_pers, mean_pers,
                         birth_mean, birth_std, death_mean, death_std,
                         pers_q25, pers_q50, pers_q75])
    # Persistence image
    pers_images = []
    for dim in range(MAX_DIM + 1):
        if dim < len(diagrams):
            img = persistence_image(diagrams[dim], n_bins=N_PERS_IMAGE)
            pers_images.append(img * (dim + 1))
        else:
            pers_images.append(np.zeros(N_PERS_IMAGE, dtype=np.float32))
    if pers_images:
        combined_img = np.sum(pers_images, axis=0)
        s = combined_img.sum()
        if s > 0:
            combined_img = combined_img / s
    else:
        combined_img = np.zeros(N_PERS_IMAGE, dtype=np.float32)
    features.extend(combined_img.tolist())
    # Betti curve
    bettis = []
    for dim in range(MAX_DIM + 1):
        if dim < len(diagrams):
            bettis.append(betti_curve(diagrams[dim], n_points=N_BETTI))
        else:
            bettis.append(np.zeros(N_BETTI, dtype=np.float32))
    if bettis:
        combined_betti = np.sum(bettis, axis=0)
        m = combined_betti.max()
        if m > 0:
            combined_betti = combined_betti / m
    else:
        combined_betti = np.zeros(N_BETTI, dtype=np.float32)
    features.extend(combined_betti.tolist())
    return np.array(features, dtype=np.float32)


def compute_tfp_for_smiles(smiles):
    """Compute TFP for a single SMILES string."""
    dist = smiles_to_distance_matrix(smiles)
    if dist is None:
        return None
    try:
        diagrams = compute_persistence(dist)
        return extract_tfp(diagrams)
    except Exception:
        return None


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='P3 RRS-TFP Expansion')
    parser.add_argument('--start-idx', type=int, default=0)
    parser.add_argument('--end-idx', type=int, default=500)
    parser.add_argument('--task-id', type=int, default=0)
    args = parser.parse_args()

    print(f"=== P3 RRS-TFP Expansion (Task {args.task_id}) ===")
    print(f"Processing indices: {args.start_idx} to {args.end_idx}")

    # Load RRS data
    if not RRS_INPUT.exists():
        print(f"ERROR: RRS input not found: {RRS_INPUT}")
        return
    rrs_df = pd.read_csv(RRS_INPUT)
    print(f"Loaded RRS data: {len(rrs_df)} compounds")

    # Load existing TFP data (if any)
    existing_tfp = set()
    if TFP_EXISTING.exists():
        existing_df = pd.read_csv(TFP_EXISTING)
        if 'smiles' in existing_df.columns:
            existing_tfp = set(existing_df['smiles'].tolist())
        print(f"Existing TFP data: {len(existing_tfp)} compounds")

    # Slice to task range
    end_idx = min(args.end_idx, len(rrs_df))
    task_df = rrs_df.iloc[args.start_idx:end_idx].copy()
    print(f"Task range: {args.start_idx} to {end_idx} ({len(task_df)} compounds)")

    # Filter to compounds needing TFP
    need_tfp = []
    for idx, row in task_df.iterrows():
        smiles = row.get('smiles', row.get('input', ''))
        if pd.isna(smiles) or smiles in existing_tfp:
            continue
        need_tfp.append((idx, smiles))

    print(f"Compounds needing TFP: {len(need_tfp)}/{len(task_df)}")

    if len(need_tfp) == 0:
        print("All compounds already have TFP. Nothing to do.")
        return

    # Compute TFP for each compound
    results = []
    for i, (idx, smiles) in enumerate(need_tfp):
        if i % 10 == 0:
            print(f"  Processing {i+1}/{len(need_tfp)}...")
        tfp = compute_tfp_for_smiles(smiles)
        row_data = {'smiles': smiles, 'index': idx}
        if tfp is not None:
            for j, col in enumerate(TFP_COLUMNS):
                row_data[col] = tfp[j]
            row_data['tfp_valid'] = True
        else:
            for col in TFP_COLUMNS:
                row_data[col] = np.nan
            row_data['tfp_valid'] = False
        results.append(row_data)

    # Save task results
    results_df = pd.DataFrame(results)
    output_file = OUTPUT_DIR / f'p3_rrs_tfp_task{args.task_id}.csv'
    results_df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")

    valid_count = results_df['tfp_valid'].sum()
    print(f"\nSummary (Task {args.task_id}):")
    print(f"  Valid TFPs: {valid_count}/{len(need_tfp)}")
    print(f"  Failed: {len(need_tfp) - valid_count}")

    print(f"\n=== Task {args.task_id} completed ===")


if __name__ == '__main__':
    main()
