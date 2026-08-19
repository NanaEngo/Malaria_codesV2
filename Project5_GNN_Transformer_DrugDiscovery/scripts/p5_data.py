#!/usr/bin/env python3
"""
P5 — PyG graph featurization + cached Data objects (M1.1).

Builds torch_geometric.data.Data objects from the frozen canonical panel and
caches them to results/p5_graphs.pt (list of Data in panel order). Graphs are
computed ONCE and reused across all models/seeds (never recomputed per run).

Atom features (per-atom, dimension F_ATOM):
    atomic number one-hot (periods 1-6), degree, formal charge, num H,
    hybridization, aromaticity, ring membership, chirality.

Edge features (per-bond, dimension F_EDGE):
    bond type one-hot (single/double/triple/aromatic), conjugation, in-ring.

Additional descriptors (optional, via DeepChem):
    - ECFP4 (2048-bit Morgan)
    - MACCS (167-bit)
    - RDKit 2D descriptors (200+ features)

Usage:
    python scripts/p5_data.py            # build cache
    python scripts/p5_data.py --force    # rebuild cache
    python scripts/p5_data.py --deepchem # also compute DeepChem descriptors
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from rdkit import Chem
from rdkit.Chem import rdchem

try:
    from deepchem.feat import CircularFingerprint, MACCSKeysFingerprint, RDKitDescriptors
    DEEPCHEM_AVAILABLE = True
except Exception as exc:  # noqa: BLE001 - deepchem is optional; any import failure
    # (e.g. jax/numpy incompatibility in the host env) must not block the
    # P5 benchmark, which computes ECFP4 via RDKit directly.
    DEEPCHEM_AVAILABLE = False
    print(f"Warning: DeepChem descriptors disabled (import failed: {exc})")

P5_ROOT = Path(__file__).resolve().parent.parent
PANEL = P5_ROOT / "results" / "p5_canonical_panel.csv"
CACHE = P5_ROOT / "results" / "p5_graphs.pt"
DESC_CACHE = P5_ROOT / "results" / "p5_deepchem_descriptors.npz"

ATOM_LIST = list(range(1, 87))
HYB_LIST = [rdchem.HybridizationType.SP, rdchem.HybridizationType.SP2,
            rdchem.HybridizationType.SP3, rdchem.HybridizationType.SP3D,
            rdchem.HybridizationType.SP3D2, rdchem.HybridizationType.OTHER]
BOND_LIST = [rdchem.BondType.SINGLE, rdchem.BondType.DOUBLE,
             rdchem.BondType.TRIPLE, rdchem.BondType.AROMATIC]
MAX_DEGREE = 6


def one_hot(value, options) -> list[float]:
    return [float(value == o) for o in options]


def atom_features(atom: Chem.Atom) -> np.ndarray:
    f = one_hot(atom.GetAtomicNum(), ATOM_LIST)
    f += one_hot(atom.GetTotalDegree(), list(range(MAX_DEGREE + 1)))
    f += [float(atom.GetFormalCharge())]
    f += [float(atom.GetTotalNumHs())]
    f += one_hot(atom.GetHybridization(), HYB_LIST)
    f += [float(atom.GetIsAromatic())]
    f += [float(atom.IsInRing())]
    f += one_hot(atom.GetChiralTag(), [rdchem.CHI_TETRAHEDRAL_CW, rdchem.CHI_TETRAHEDRAL_CCW])
    return np.array(f, dtype=np.float32)


def edge_features(bond: Chem.Bond) -> np.ndarray:
    f = one_hot(bond.GetBondType(), BOND_LIST)
    f += [float(bond.GetIsConjugated())]
    f += [float(bond.IsInRing())]
    return np.array(f, dtype=np.float32)


def mol_to_graph(mol: Chem.Mol) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    if mol is None:
        raise ValueError("None molecule in canonical panel — must be resolvable")
    x = np.stack([atom_features(a) for a in mol.GetAtoms()])
    rows, cols, ef = [], [], []
    for b in mol.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
        fe = edge_features(b)
        rows += [i, j]
        cols += [j, i]
        ef += [fe, fe]
    edge_index = torch.tensor([rows, cols], dtype=torch.long)
    if ef:
        edge_attr = torch.tensor(np.stack(ef), dtype=torch.float32)
    else:
        edge_attr = torch.empty((0, 6), dtype=torch.float32)
    return torch.tensor(x, dtype=torch.float32), edge_index, edge_attr, torch.tensor([mol.GetNumAtoms()], dtype=torch.long)


def _conv_worker(mol):
    return mol_to_graph(mol)


def build_graphs(smiles_list: list[str], n_jobs: int = 32) -> list:
    from concurrent.futures import ProcessPoolExecutor
    mols = [Chem.MolFromSmiles(s) for s in smiles_list]

    with ProcessPoolExecutor(max_workers=n_jobs) as ex:
        graphs = list(ex.map(_conv_worker, mols, chunksize=64))
    return graphs


def compute_deepchem_descriptors(smiles_list: list[str]) -> dict[str, np.ndarray]:
    """Compute additional descriptors using DeepChem featurizers."""
    if not DEEPCHEM_AVAILABLE:
        return {}

    mols = [Chem.MolFromSmiles(s) for s in smiles_list]
    valid_idx = [i for i, m in enumerate(mols) if m is not None]
    valid_mols = [mols[i] for i in valid_idx]

    descriptors = {}

    # ECFP4 (Morgan radius=2, 2048 bits)
    ecfp = CircularFingerprint(radius=2, size=2048)
    ecfp_features = ecfp.featurize(valid_mols)
    descriptors['ecfp4'] = ecfp_features.astype(np.float32)

    # MACCS keys (167 bits)
    maccs = MACCSKeysFingerprint()
    maccs_features = maccs.featurize(valid_mols)
    descriptors['maccs'] = maccs_features.astype(np.float32)

    # RDKit 2D descriptors (200+)
    rdkit_desc = RDKitDescriptors()
    rdkit_features = rdkit_desc.featurize(valid_mols)
    descriptors['rdkit_2d'] = rdkit_features.astype(np.float32)

    print(f"DeepChem descriptors computed for {len(valid_mols)} molecules:")
    for k, v in descriptors.items():
        print(f"  {k}: shape {v.shape}")

    return descriptors


def save_descriptors_cache(descriptors: dict[str, np.ndarray], smiles_list: list[str]):
    """Save descriptor cache with molecule indices for alignment."""
    np.savez_compressed(DESC_CACHE,
                        **descriptors,
                        smiles=np.array(smiles_list, dtype=object))
    print(f"Saved descriptor cache to {DESC_CACHE}")


def main() -> None:
    import argparse
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--n-jobs", type=int, default=min(32, os.cpu_count() or 1))
    ap.add_argument("--deepchem", action="store_true", help="Compute DeepChem descriptors")
    args = ap.parse_args()

    if CACHE.exists() and not args.force:
        print(f"Cache exists: {CACHE} — use --force to rebuild")
        if args.deepchem:
            print("Also checking DeepChem cache...")
            if DESC_CACHE.exists():
                print(f"DeepChem cache exists: {DESC_CACHE}")
                return
        else:
            return

    t0 = time.perf_counter()
    panel = pd.read_csv(PANEL)
    smiles = panel["smiles"].tolist()
    print(f"Building graphs for {len(smiles):,} molecules (n_jobs={args.n_jobs})...")

    graphs = build_graphs(smiles, n_jobs=args.n_jobs)

    data_list = []
    for (x, ei, ea, n) in graphs:
        data_list.append({
            "x": x, "edge_index": ei, "edge_attr": ea, "num_nodes": n.item(),
        })
    torch.save(data_list, CACHE)
    print(f"Wrote {CACHE} ({len(data_list):,} graphs)")
    print(f"F_ATOM={len(mol_to_graph(Chem.MolFromSmiles('CC'))[0][0])}, F_EDGE={len(edge_features(Chem.MolFromSmiles('CC').GetBondWithIdx(0)))}")

    # Compute DeepChem descriptors if requested
    if args.deepchem and DEEPCHEM_AVAILABLE:
        print("Computing DeepChem descriptors...")
        desc = compute_deepchem_descriptors(smiles)
        if desc:
            save_descriptors_cache(desc, smiles)
        else:
            print("No descriptors computed (DeepChem issue)")
    elif args.deepchem:
        print("DeepChem not available — skipping descriptor computation")

    print(f"Elapsed: {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()