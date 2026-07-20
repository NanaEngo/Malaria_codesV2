"""
Paper 3 — Steps 1–2: Topological Data Analysis (TDA) pipeline.

Computes Vietoris-Rips persistent homology (H0, H1, H2) for each molecule
and extracts an enriched Topological Fingerprint (TFP) vector (78-d).

Molecular graph construction (per roadmap):
    G = (V, E, w)  where  w_ij = d_ij × (1 + Z_i × Z_j / 100)
    d_ij = Euclidean distance between atoms i and j (from 3D conformer)
    Z_i  = atomic number of atom i

TFP features (78 total per molecule):
    - 11 base features × 3 dims (H0/H1/H2): entropy, count, max/mean pers,
      birth_mean/std, death_mean/std, pers_q25/50/75
    - 25-D persistence image (persistence-weighted histogram, threshold 2.0)
    - 20-D Betti curve (Betti number evolution, scales 0–5)

The 78-D TFP enables richer signal extraction vs the original 12-D version.

Outputs:
    results/p3_tda_fingerprints.csv   — TFP matrix (n_mols × 78)
    results/p3_tda_summary.txt        — summary statistics

Usage:
    python Papers/Quantum_Inspired_Representations/Scripts/p3_tda_pipeline.py
    python Papers/Quantum_Inspired_Representations/Scripts/p3_tda_pipeline.py --pilot
    python Papers/Quantum_Inspired_Representations/Scripts/p3_tda_pipeline.py --n-jobs 4
"""

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
# Morgan fingerprints not used — TFP uses ripser persistent homology

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).parent.parent  # .../Project3
RESULTS_DIR = PROJECT_DIR / "results"
DATA_DIR    = PROJECT_DIR / "data"

PERSISTENCE_THRESHOLD = 0.5   # Å — features below this are noise
MAX_ATOMS = 100                # truncate/pad to this for consistent graphs
MAX_DIM   = 2                  # compute H0, H1, H2
DEFAULT_N_CONF = 1             # conformers per molecule (1 = original single-conformer)


def load_smiles(input_path: Path = None) -> pd.DataFrame:
    """Load the full 65,856-molecule library or a custom input path."""
    if input_path:
        path = input_path
    else:
        path = RESULTS_DIR / "c6_primary_leads_synthesisable.csv"
    df = pd.read_csv(path)
    col = "input" if "input" in df.columns else ("smiles" if "smiles" in df.columns else df.columns[0])
    df = df.rename(columns={col: "smiles"})
    return df[["smiles"]].drop_duplicates().reset_index(drop=True)


def _weight_distance_matrix(d: np.ndarray, atomic_nums: np.ndarray) -> np.ndarray:
    """Apply atomic-number weighting: w_ij = d_ij × (1 + Z_i × Z_j / 100)."""
    Z_outer = np.outer(atomic_nums, atomic_nums)
    w = d * (1.0 + Z_outer / 100.0)
    np.fill_diagonal(w, 0.0)
    return w


def _distance_matrix_from_conformer(mol, conf_id: int = 0) -> tuple[np.ndarray, np.ndarray] | None:
    """Extract coordinates + atomic numbers from a conformer.

    Returns (coords, atomic_nums) or None if molecule is too small.
    Truncates to MAX_ATOMS.
    """
    conf = mol.GetConformer(conf_id)
    atoms = list(mol.GetAtoms())[:MAX_ATOMS]
    n = len(atoms)
    if n < 2:
        return None
    coords = np.array([conf.GetAtomPosition(a.GetIdx()) for a in atoms])
    atomic_nums = np.array([a.GetAtomicNum() for a in atoms], dtype=float)
    return coords, atomic_nums


def _distance_matrix_3d(mol) -> np.ndarray | None:
    """Generate 3D Euclidean distance matrix with MMFF optimisation."""
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


def _distance_matrix_2d(mol) -> np.ndarray | None:
    """Generate 2D graph-based distance matrix (shortest path on bonds).

    Fallback when 3D embedding fails. Uses the molecular graph topology:
    each bond contributes distance = 1.0 (or bond order for multiple bonds).
    Shortest path distances are computed via Floyd-Warshall.
    """
    atoms = list(mol.GetAtoms())[:MAX_ATOMS]
    n = len(atoms)
    if n < 2:
        return None

    atomic_nums = np.array([a.GetAtomicNum() for a in atoms], dtype=float)

    # Build adjacency matrix with bond-order-weighted distances
    adj = np.full((n, n), np.inf)
    np.fill_diagonal(adj, 0.0)

    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()
        if i < n and j < n:
            order = bond.GetBondTypeAsDouble()  # 1.0, 1.5, 2.0, 3.0
            adj[i, j] = 1.0 / order  # stronger bonds = shorter distance
            adj[j, i] = 1.0 / order

    # Floyd-Warshall for all-pairs shortest paths
    dist = adj.copy()
    for k in range(n):
        # Vectorised: dist[i,j] = min(dist[i,j], dist[i,k] + dist[k,j])
        dist_k = dist[k, :][None, :]   # (1, n)
        dist_ik = dist[:, k][:, None]  # (n, 1)
        candidate = dist_ik + dist_k
        dist = np.minimum(dist, candidate)

    return _weight_distance_matrix(dist, atomic_nums)


def smiles_to_distance_matrix(smiles: str) -> np.ndarray | None:
    """
    Generate a weighted distance matrix from a SMILES string.

    First tries 3D embedding (ETKDG + MMFF). If that fails,
    falls back to 2D graph shortest-path distances.

    Returns an (N×N) array or None if both methods fail.
    N is capped at MAX_ATOMS.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    mol = Chem.AddHs(mol)

    # Try 3D first
    dm = _distance_matrix_3d(mol)
    if dm is not None:
        return dm

    # Fallback: 2D graph distances
    dm = _distance_matrix_2d(mol)
    if dm is not None:
        return dm

    return None


def compute_persistence(dist_matrix: np.ndarray) -> list[np.ndarray]:
    """
    Compute Vietoris-Rips persistence diagrams up to MAX_DIM.

    Returns list of (birth, death) arrays indexed by dimension [0..MAX_DIM].
    Requires ripser.
    """
    try:
        from ripser import ripser
    except ImportError:
        raise ImportError("ripser not installed. Run: pip install ripser")

    result = ripser(dist_matrix, maxdim=MAX_DIM, distance_matrix=True)
    return result["dgms"]   # list of (n_features, 2) arrays


def persistence_entropy(dgm: np.ndarray) -> float:
    """Compute persistence entropy of a diagram (finite features only)."""
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


def persistence_image(dgm: np.ndarray, n_bins: int = 25,  # default N_PERS_IMAGE
                       threshold: float = 2.0) -> np.ndarray:
    """
    Compute a 1-D persistence image (projection of PD onto persistence axis).

    Drops infinite-death features. The persistence dimension (death - birth)
    is binned into n_bins equally spaced bins from 0 to threshold.
    Features are weighted by their distance from the diagonal.

    Returns (n_bins,) vector.
    """
    finite = dgm[np.isfinite(dgm[:, 1])]
    if len(finite) == 0:
        return np.zeros(n_bins, dtype=np.float32)

    pers = finite[:, 1] - finite[:, 0]
    pers = pers[pers > 0]
    if len(pers) == 0 or pers.max() == 0:  # guard against NaN from 0/0
        return np.zeros(n_bins, dtype=np.float32)

    # Clip to threshold
    pers = np.clip(pers, 0, threshold)

    # Weight: distance from diagonal (how persistent)
    weights = pers / pers.max()

    # Build persistence image
    bins = np.linspace(0, threshold, n_bins + 1)
    img, _ = np.histogram(pers, bins=bins, weights=weights)
    # Normalise to unit sum
    s = img.sum()
    if s > 0:
        img = img / s
    return img.astype(np.float32)


def betti_curve(dgm: np.ndarray, n_points: int = 20,  # default N_BETTI
                max_scale: float = 5.0) -> np.ndarray:
    """
    Compute Betti curve: Betti number as function of filtration parameter.

    Samples n_points equally spaced from 0 to max_scale.
    Drops infinite-death features (which would contribute at all scales).

    Returns (n_points,) vector.
    """
    finite = dgm[np.isfinite(dgm[:, 1])]
    if len(finite) == 0:
        return np.zeros(n_points, dtype=np.float32)

    births = finite[:, 0]
    deaths = np.clip(finite[:, 1], 0, max_scale)
    death_eps = 1e-6

    scales = np.linspace(0, max_scale, n_points)
    curve = np.zeros(n_points, dtype=np.float32)
    for s_idx, s in enumerate(scales):
        # Betti number = count of features with birth < s <= death
        curve[s_idx] = np.sum((births < (s + death_eps)) & (deaths >= s))

    # Normalise by max value for scale-invariance
    m = curve.max()
    if m > 0:
        curve = curve / m
    return curve


def extract_tfp(diagrams: list[np.ndarray]) -> np.ndarray:
    """
    Extract enriched Topological Fingerprint from persistence diagrams.

    Per homology dimension (H0, H1, H2):
        11 base features (entropy, count, max/mean pers, birth/death stats,
                         persistence percentiles)
    Plus:
        25-D persistence image (all dims combined, threshold=2.0, weighted by dim)
        20-D Betti curve (all dims combined)

    Total: 11×3 + 25 + 20 = 78 features
    """
    features = []

    # Per-dimension features
    for dim in range(MAX_DIM + 1):
        if dim >= len(diagrams):
            features.extend([0.0] * len(BASE_FEATURES))
            continue

        dgm = diagrams[dim]
        finite = dgm[np.isfinite(dgm[:, 1])]
        pers = (finite[:, 1] - finite[:, 0]) if len(finite) > 0 else np.array([])
        above_noise = pers[pers > PERSISTENCE_THRESHOLD] if len(pers) > 0 else pers

        entropy   = persistence_entropy(dgm)
        count     = float(np.sum(pers > PERSISTENCE_THRESHOLD))
        max_pers  = float(pers.max()) if len(pers) > 0 else 0.0
        mean_pers = float(pers.mean()) if len(pers) > 0 else 0.0

        birth_mean = float(finite[:, 0].mean()) if len(finite) > 0 else 0.0
        birth_std  = float(finite[:, 0].std()) if len(finite) > 0 else 0.0
        death_mean = float(finite[:, 1].mean()) if len(finite) > 0 else 0.0
        death_std  = float(finite[:, 1].std()) if len(finite) > 0 else 0.0

        pers_q25 = float(np.percentile(above_noise, 25)) if len(above_noise) > 0 else 0.0
        pers_q50 = float(np.percentile(above_noise, 50)) if len(above_noise) > 0 else 0.0
        pers_q75 = float(np.percentile(above_noise, 75)) if len(above_noise) > 0 else 0.0

        features.extend([entropy, count, max_pers, mean_pers,
                         birth_mean, birth_std, death_mean, death_std,
                         pers_q25, pers_q50, pers_q75])

    # Global persistence image (combined across dimensions, weighted by dim+1)
    pers_images = []
    for dim in range(MAX_DIM + 1):
        if dim < len(diagrams):
            img = persistence_image(diagrams[dim], n_bins=N_PERS_IMAGE)
            # Weight: higher dimensions get slightly more weight
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

    # Global Betti curve (combined across dimensions)
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


# New TFP columns: enriched feature set
# Per dimension (H0, H1, H2):
#   - entropy, count, max_pers, mean_pers (original 4)
#   - birth_mean, birth_std, death_mean, death_std (birth/death distributions)
#   - pers_q25, pers_q50, pers_q75 (persistence percentiles)
#   - pers_img_k (25-D persistence image)
#   - betti_k (20-D Betti curve samples)
# Total: (4 + 4 + 3) × 3 dims + 25 + 20 = 78 features

BASE_FEATURES = ["entropy", "count", "max_pers", "mean_pers",
                 "birth_mean", "birth_std", "death_mean", "death_std",
                 "pers_q25", "pers_q50", "pers_q75"]

N_PERS_IMAGE = 25   # resolution of persistence image (25 bins, threshold 2.0)
N_BETTI = 20         # sampling points for Betti curve

TFP_COLUMNS = (
    [f"H{d}_{feat}" for d in range(MAX_DIM + 1) for feat in BASE_FEATURES]
    + [f"pers_img_{i}" for i in range(N_PERS_IMAGE)]
    + [f"betti_{i}" for i in range(N_BETTI)]
)


def process_molecule(smiles: str, n_conf: int = DEFAULT_N_CONF,
                     random_seed: int = 42) -> np.ndarray | None:
    """Full pipeline: SMILES → (N conformer distance matrices) → persistence → TFP.

    If n_conf > 1, generates multiple conformers via ETKDG and averages the TFP
    vectors (Boltzmann-consistent weighted average using MMFF94 energy as proxy).
    This provides conformational robustness for the topological descriptors.
    """
    if n_conf <= 1:
        # Original single-conformer path
        dist = smiles_to_distance_matrix(smiles)
        if dist is None:
            return None
        try:
            diagrams = compute_persistence(dist)
            return extract_tfp(diagrams)
        except Exception:
            return None

    # Multi-conformer path: generate N conformers, compute TFP for each, average
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    mol = Chem.AddHs(mol)

    # Generate diverse conformers via ETKDG
    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed
    params.useRandomCoords = True
    params.pruneRmsThresh = 0.5   # prune redundant conformers (RMSD < 0.5 A)

    n_embedded = AllChem.EmbedMultipleConfs(mol, numConfs=n_conf, params=params)
    if n_embedded == 0:
        # Fallback: 3D embedding failed entirely — use single-conformer path
        # which itself has a 2D graph-distance fallback
        return process_molecule(smiles, n_conf=1, random_seed=random_seed)

    # Optimise each conformer with MMFF94 and collect energies
    conf_energies = []
    conf_tfps = []
    for conf_id in range(mol.GetNumConformers()):
        try:
            ff = AllChem.MMFFGetMoleculeForceField(
                mol, AllChem.MMFFGetMoleculeProperties(mol), confId=conf_id
            )
            if ff is None:
                continue
            ff.Minimize(maxIts=200)
            energy = ff.CalcEnergy()
        except Exception:
            continue

        # Compute distance matrix for this conformer using shared helper
        result = _distance_matrix_from_conformer(mol, conf_id)
        if result is None:
            continue
        coords, atomic_nums = result
        diff = coords[:, None, :] - coords[None, :, :]
        d = np.sqrt((diff ** 2).sum(axis=-1))
        w = _weight_distance_matrix(d, atomic_nums)

        try:
            diagrams = compute_persistence(w)
            tfp = extract_tfp(diagrams)
            conf_tfps.append(tfp)
            conf_energies.append(energy)
        except Exception:
            continue

    if not conf_tfps:
        # All conformers failed — fall back to single-conformer (2D-capable)
        return process_molecule(smiles, n_conf=1, random_seed=random_seed)

    # Boltzmann weighting from MMFF94 energies
    conf_tfps = np.array(conf_tfps)
    conf_energies = np.array(conf_energies)
    # Boltzmann-weighted average at physiological temperature
    # MMFF94 energies in RDKit are in kcal/mol; β = 1/(k_B × 310K) ≈ 1.62.
    # We use β = 0.4 as a conservative (broader) heuristic: it gives
    # more uniform weights across conformers, avoiding over-confidence
    # from a single dominant low-energy conformer.
    e_min = conf_energies.min()
    rel_energies = conf_energies - e_min
    beta = 0.4  # conservative heuristic (physical β ≈ 1.62 at 310K)
    weights = np.exp(-beta * rel_energies)
    weights /= weights.sum()

    # Weighted average TFP
    tfp_avg = np.average(conf_tfps, axis=0, weights=weights)
    return tfp_avg.astype(np.float32)


def run_pipeline(df: pd.DataFrame, n_jobs: int = 1,
                 n_conf: int = DEFAULT_N_CONF) -> pd.DataFrame:
    """Process all molecules, optionally in parallel."""
    smiles_list = df["smiles"].tolist()
    n = len(smiles_list)
    print(f"  Processing {n} molecules (n_jobs={n_jobs}, n_conf={n_conf})...")
    if n_conf > 1:
        print(f"  [MC-TDA] Generating {n_conf} conformers per molecule, "
              f"Boltzmann-weighting via MMFF94 energies...")

    if n_jobs > 1:
        from joblib import Parallel, delayed
        results = Parallel(n_jobs=n_jobs, verbose=5)(
            delayed(process_molecule)(smi, n_conf=n_conf) for smi in smiles_list
        )
    else:
        results = []
        for i, smi in enumerate(smiles_list):
            if i % 500 == 0:
                print(f"    {i}/{n}...")
            results.append(process_molecule(smi, n_conf=n_conf))

    rows = []
    failed = 0
    for smi, tfp in zip(smiles_list, results):
        if tfp is None:
            failed += 1
            rows.append([smi] + [np.nan] * len(TFP_COLUMNS))
        else:
            rows.append([smi] + tfp.tolist())

    print(f"  Completed: {n - failed}/{n} molecules ({failed} failed 3D embedding)")
    return pd.DataFrame(rows, columns=["smiles"] + TFP_COLUMNS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true",
                        help="Run on 100 molecules only (pilot study)")
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel workers (requires joblib)")
    parser.add_argument("--n-conf", type=int, default=DEFAULT_N_CONF,
                        help="Number of conformers per molecule for MC-TDA "
                             "(default: 1 = single-conformer; >1 enables Boltzmann-"
                             "weighted averaging for conformational robustness)")
    parser.add_argument("--input", type=str, default=None,
                        help="Custom input CSV file path")
    args = parser.parse_args()

    print("=" * 60)
    print("Paper 3 — TDA Pipeline")
    print("=" * 60)

    input_path = Path(args.input) if args.input else None
    df = load_smiles(input_path)
    print(f"  Loaded {len(df)} molecules")

    if args.pilot:
        df = df.head(100)
        print("  [PILOT] Using first 100 molecules")

    tfp_df = run_pipeline(df, n_jobs=args.n_jobs, n_conf=args.n_conf)

    suffix = "" if args.n_conf == 1 else f"_conf{args.n_conf}"
    out = RESULTS_DIR / (f"p3_tda_fingerprints_pilot{suffix}.csv" if args.pilot
                         else f"p3_tda_fingerprints{suffix}.csv")
    tfp_df.to_csv(out, index=False)
    print(f"\n  Saved: {out}")

    # Summary statistics
    valid = tfp_df.dropna(subset=TFP_COLUMNS)
    summary_lines = [
        f"Molecules processed : {len(tfp_df)}",
        f"Valid TFPs          : {len(valid)}",
        f"Failed (no 3D)      : {len(tfp_df) - len(valid)}",
        f"Conformers/mol      : {args.n_conf}",
        "",
        "TFP feature statistics (valid molecules):",
    ]
    for col in TFP_COLUMNS:
        vals = valid[col]
        summary_lines.append(
            f"  {col:<20s}  mean={vals.mean():.4f}  std={vals.std():.4f}"
            f"  min={vals.min():.4f}  max={vals.max():.4f}"
        )

    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)

    suffix = "" if args.n_conf == 1 else f"_conf{args.n_conf}"
    summary_out = RESULTS_DIR / (f"p3_tda_summary_pilot{suffix}.txt" if args.pilot
                                  else f"p3_tda_summary{suffix}.txt")
    summary_out.write_text(summary_text)
    print(f"\n  Summary saved: {summary_out}")


if __name__ == "__main__":
    main()
