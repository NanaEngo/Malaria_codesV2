"""
Paper 3 — Step 3: Tensor Network Embedding (TNE).

Builds a 3D molecular tensor T ∈ R^(N × F × 3) per molecule:
    N = up to 100 atoms (padded with zeros)
    F = 10 atom-level features
    3 = x, y, z coordinates (Å, from ETKDGv3 conformer)

Applies Tucker decomposition with bond dimension 8 (default) to compress each tensor,
then flattens the core tensor as the TNE descriptor.

Atom features (F=10):
    0  atomic number (normalised / 100)
    1  degree
    2  formal charge
    3  num Hs
    4  is aromatic
    5  is in ring
    6  hybridisation (SP=1, SP2=2, SP3=3, other=0, normalised /3)
    7  partial charge (Gasteiger, normalised to [-1,1])
    8  van der Waals radius (normalised / 3)
    9  electronegativity proxy (Pauling / 4)

Outputs:
    results/p3_tne_embeddings.csv     — TNE descriptor matrix
    results/p3_tne_summary.txt        — compression stats + wall-time

Usage:
    python scripts/p3_tne_pipeline.py
    python scripts/p3_tne_pipeline.py --pilot
    python scripts/p3_tne_pipeline.py --bond-dim 16
    python scripts/p3_tne_pipeline.py --n-jobs 8            # CPU parallel
    python scripts/p3_tne_pipeline.py --gpu                 # GPU Tucker (requires PyTorch+CUDA)

Optimizations (v2, July 2026):
    - Wall-time benchmarking added (mol/sec, total seconds, ETA)
    - joblib parallel loop FIXED (was wired as arg but never called — bug)
    - Optional GPU Tucker via tensorly.set_backend("pytorch")
"""

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.rdchem import HybridizationType

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

N_ATOMS   = 100   # max atoms per molecule
N_FEATS   = 10    # atom feature dimension
N_COORDS  = 3     # x, y, z

# Pauling electronegativity proxy (most common elements)
_EN = {1: 2.20, 6: 2.55, 7: 3.04, 8: 3.44, 9: 3.98, 15: 2.19,
       16: 2.58, 17: 3.16, 35: 2.96, 53: 2.66}
_VDW = {1: 1.20, 6: 1.70, 7: 1.55, 8: 1.52, 9: 1.47, 15: 1.80,
        16: 1.80, 17: 1.75, 35: 1.85, 53: 1.98}
_HYB = {HybridizationType.SP: 1, HybridizationType.SP2: 2,
        HybridizationType.SP3: 3}


def smiles_to_tensor(smiles: str) -> np.ndarray | None:
    """
    Convert SMILES to tensor T in R^(N_ATOMS x N_FEATS x N_COORDS).
    Returns None if 3D embedding fails.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    mol = Chem.AddHs(mol)
    AllChem.ComputeGasteigerCharges(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    params.useRandomCoords = True
    if AllChem.EmbedMolecule(mol, params) != 0:
        return None
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
    except Exception:
        pass

    conf = mol.GetConformer()
    atoms = list(mol.GetAtoms())[:N_ATOMS]

    T = np.zeros((N_ATOMS, N_FEATS, N_COORDS), dtype=np.float32)

    for i, atom in enumerate(atoms):
        idx = atom.GetIdx()
        pos = conf.GetAtomPosition(idx)
        coords = np.array([pos.x, pos.y, pos.z], dtype=np.float32)

        z = atom.GetAtomicNum()
        gc = float(atom.GetPropsAsDict().get("_GasteigerCharge", 0.0))
        if not np.isfinite(gc):
            gc = 0.0

        feats = np.array([
            z / 100.0,
            atom.GetDegree() / 6.0,
            np.clip(atom.GetFormalCharge() / 2.0, -1.0, 1.0),
            atom.GetTotalNumHs() / 4.0,
            float(atom.GetIsAromatic()),
            float(atom.IsInRing()),
            _HYB.get(atom.GetHybridization(), 0) / 3.0,
            np.clip(gc, -1.0, 1.0),
            _VDW.get(z, 1.70) / 3.0,
            _EN.get(z, 2.55) / 4.0,
        ], dtype=np.float32)

        # Outer product: (N_FEATS,) x (N_COORDS,) -> (N_FEATS, N_COORDS)
        T[i] = np.outer(feats, coords)

    return T


def tucker_compress(T: np.ndarray, bond_dim: int,
                    use_gpu: bool = False) -> np.ndarray:
    """
    Tucker decomposition of T in R^(N x F x C) with rank (bond_dim, bond_dim, C).
    Returns the flattened core tensor as the TNE descriptor.

    Args:
        T:        Input tensor (N_ATOMS, N_FEATS, N_COORDS)
        bond_dim: Tucker rank for first two modes
        use_gpu:  If True, use PyTorch CUDA backend for tensorly
    """
    try:
        import tensorly as tl
        from tensorly.decomposition import tucker
    except ImportError:
        raise ImportError("tensorly not installed. Run: pip install tensorly")

    if use_gpu:
        try:
            import torch
            tl.set_backend("pytorch")
            T_tl = tl.tensor(T, device="cuda", dtype=torch.float32)
        except Exception:
            tl.set_backend("numpy")
            T_tl = T
    else:
        tl.set_backend("numpy")
        T_tl = T

    ranks = (min(bond_dim, T.shape[0]),
             min(bond_dim, T.shape[1]),
             T.shape[2])
    core, _ = tucker(T_tl, rank=ranks, init="svd", tol=1e-4, n_iter_max=100)

    # Always return numpy for downstream usage
    if use_gpu:
        core = tl.to_numpy(core)
        tl.set_backend("numpy")
    return core.flatten()


def reconstruction_error(T: np.ndarray, bond_dim: int,
                          use_gpu: bool = False) -> float:
    """Frobenius norm of (T - T_reconstructed) / ||T||."""
    try:
        import tensorly as tl
        from tensorly.decomposition import tucker

        if use_gpu:
            try:
                import torch
                tl.set_backend("pytorch")
                T_tl = tl.tensor(T, device="cuda", dtype=torch.float32)
            except Exception:
                tl.set_backend("numpy")
                T_tl = T
        else:
            tl.set_backend("numpy")
            T_tl = T

        ranks = (min(bond_dim, T.shape[0]),
                 min(bond_dim, T.shape[1]),
                 T.shape[2])
        core, factors = tucker(T_tl, rank=ranks, init="svd", tol=1e-4,
                               n_iter_max=100)
        T_rec = tl.tucker_to_tensor((core, factors))

        if use_gpu:
            T_np = tl.to_numpy(T_tl)
            T_rec_np = tl.to_numpy(T_rec)
        else:
            T_np, T_rec_np = np.asarray(T_tl), np.asarray(T_rec)

        norm_T = np.linalg.norm(T_np)
        return float(np.linalg.norm(T_np - T_rec_np) / norm_T) if norm_T > 0 else 0.0
    except Exception:
        return float("nan")
    finally:
        try:
            import tensorly as tl
            tl.set_backend("numpy")
        except Exception:
            pass


def load_smiles() -> pd.DataFrame:
    path = RESULTS_DIR / "c6_primary_leads_synthesisable.csv"
    df = pd.read_csv(path).rename(columns={"input": "smiles"})
    return df[["smiles"]].drop_duplicates().reset_index(drop=True)


def _n_real_atoms(smiles: str) -> int:
    """Count actual atoms in a SMILES (including implicit H after AddHs)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return 0
    mol = Chem.AddHs(mol)
    return min(mol.GetNumAtoms(), N_ATOMS)


def _process_one(args_tuple):
    """Top-level worker for joblib pickling."""
    smi, bond_dim, use_gpu = args_tuple
    n_real = _n_real_atoms(smi)
    T = smiles_to_tensor(smi)
    if T is None:
        return smi, None, float("nan"), 0
    try:
        core = tucker_compress(T, bond_dim, use_gpu=use_gpu)
        err  = reconstruction_error(T, bond_dim, use_gpu=use_gpu)
        return smi, core, err, n_real
    except Exception:
        return smi, None, float("nan"), 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true",
                        help="Run on 100 molecules only")
    parser.add_argument("--bond-dim", type=int, default=8,
                        help="Tucker bond dimension (default: 8, per roadmap Step 3)")
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel CPU workers (default: 1; use -1 for all cores)")
    parser.add_argument("--gpu", action="store_true",
                        help="Use GPU Tucker via tensorly PyTorch backend (requires CUDA)")
    args = parser.parse_args()

    print("=" * 60)
    print(f"Paper 3 — Tensor Network Embedding (bond_dim={args.bond_dim})")
    if args.gpu:
        print("  Backend: PyTorch GPU (CUDA)")
    elif args.n_jobs != 1:
        print(f"  Backend: joblib CPU ({args.n_jobs} workers)")
    else:
        print("  Backend: NumPy CPU (serial)")
    print("=" * 60)

    df = load_smiles()
    if args.pilot:
        df = df.head(100)
        print("  [PILOT] Using first 100 molecules")
    print(f"  Loaded {len(df)} molecules")

    # Determine output descriptor dimension from a test molecule
    test_T = smiles_to_tensor("c1ccccc1")
    if test_T is None:
        raise RuntimeError("Test molecule failed — check RDKit installation")
    test_core = tucker_compress(test_T, args.bond_dim, use_gpu=args.gpu)
    desc_dim = len(test_core)
    print(f"  Tensor shape: {test_T.shape}  ->  core dim: {desc_dim}")
    print(f"  Compression ratio: {test_T.size / desc_dim:.1f}x")

    col_names = [f"tne_{i}" for i in range(desc_dim)]
    smiles_list = df["smiles"].tolist()
    n = len(smiles_list)

    # --- Main loop ---
    t0 = time.perf_counter()

    if args.n_jobs != 1 and not args.gpu:
        # Parallel CPU via joblib — FIXED: was present as arg but never wired (bug)
        from joblib import Parallel, delayed
        print(f"  Running parallel with n_jobs={args.n_jobs}...")
        job_args = [(smi, args.bond_dim, False) for smi in smiles_list]
        results_raw = Parallel(n_jobs=args.n_jobs, verbose=5)(
            delayed(_process_one)(a) for a in job_args
        )
    else:
        # Serial (or GPU)
        results_raw = []
        for i, smi in enumerate(smiles_list):
            if i % 500 == 0:
                elapsed = time.perf_counter() - t0
                rate = i / elapsed if elapsed > 0 else 0.0
                eta = (n - i) / rate if rate > 0 else float("inf")
                print(f"    {i}/{n}  ({rate:.1f} mol/s, ETA {eta/60:.1f} min)...")
            results_raw.append(_process_one((smi, args.bond_dim, args.gpu)))

    t_total = time.perf_counter() - t0

    # --- Collect results ---
    rows, errors, failed, real_atoms = [], [], 0, []
    for smi, core, err, n_real in results_raw:
        if core is None:
            failed += 1
            rows.append([smi] + [np.nan] * desc_dim)
            errors.append(np.nan)
        else:
            rows.append([smi] + list(core))
            errors.append(err)
            real_atoms.append(n_real)

    valid_n = n - failed
    mol_per_sec = valid_n / t_total if t_total > 0 else 0.0
    print(f"  Completed: {valid_n}/{n} ({failed} failed)")
    print(f"  Wall time: {t_total:.1f}s  ({mol_per_sec:.2f} mol/s)")

    out_df = pd.DataFrame(rows, columns=["smiles"] + col_names)
    suffix = "_pilot" if args.pilot else ""
    out_csv = RESULTS_DIR / f"p3_tne_embeddings{suffix}.csv"
    out_df.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # Compute both compression ratios
    padded_elements = N_ATOMS * N_FEATS * N_COORDS  # 100 × 10 × 3 = 3000
    padded_ratio = padded_elements / desc_dim

    if real_atoms:
        mean_atoms = np.mean(real_atoms)
        median_atoms = np.median(real_atoms)
        min_atoms = min(real_atoms)
        max_atoms = max(real_atoms)
        # Real ratio: actual (unpadded) tensor size / descriptor dim
        # Real tensor = actual_atoms × N_FEATS × N_COORDS
        real_elements = np.array(real_atoms) * N_FEATS * N_COORDS
        real_ratio_mean = np.mean(real_elements) / desc_dim
        real_ratio_min = (min_atoms * N_FEATS * N_COORDS) / desc_dim
        real_ratio_max = (max_atoms * N_FEATS * N_COORDS) / desc_dim
    else:
        mean_atoms = median_atoms = min_atoms = max_atoms = 0
        real_ratio_mean = real_ratio_min = real_ratio_max = 0.0

    valid_errors = [e for e in errors if np.isfinite(e)]
    summary_lines = [
        f"Molecules processed  : {n}",
        f"Valid embeddings     : {valid_n}",
        f"Failed               : {failed}",
        f"Bond dimension       : {args.bond_dim}",
        f"Tucker ranks         : ({args.bond_dim}, {args.bond_dim}, {N_COORDS})",
        f"Input tensor (padded): {N_ATOMS}×{N_FEATS}×{N_COORDS} = {padded_elements} elements",
        f"Core descriptor dim  : {desc_dim}",
        f"",
        f"--- Compression ratios ---",
        f"Padded ratio (N={N_ATOMS}) : {padded_ratio:.1f}x",
        f"",
        f"--- Real (unpadded) stats  ---",
        f"Mean atoms/molecule   : {mean_atoms:.1f}",
        f"Median atoms/molecule : {median_atoms:.1f}",
        f"Min atoms             : {min_atoms}",
        f"Max atoms             : {max_atoms}",
        f"Real ratio (mean)     : {real_ratio_mean:.1f}x",
        f"Real ratio range      : {real_ratio_min:.1f}x to {real_ratio_max:.1f}x",
        f"",
        f"--- Reconstruction error ---",
        f"Mean recon. error    : {np.mean(valid_errors):.4f}" if valid_errors else "Mean recon. error: N/A",
        f"Max  recon. error    : {np.max(valid_errors):.4f}"  if valid_errors else "Max  recon. error: N/A",
        f"",
        f"--- Performance ---",
        f"Wall time (s)        : {t_total:.1f}",
        f"Throughput (mol/s)   : {mol_per_sec:.2f}",
        f"Backend              : {'GPU (PyTorch/CUDA)' if args.gpu else f'CPU (n_jobs={args.n_jobs})'}",
    ]
    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)

    summary_out = RESULTS_DIR / f"p3_tne_summary{suffix}.txt"
    summary_out.write_text(summary_text)
    print(f"\n  Summary saved: {summary_out}")


if __name__ == "__main__":
    main()
