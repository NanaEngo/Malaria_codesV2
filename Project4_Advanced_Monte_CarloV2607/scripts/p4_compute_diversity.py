#!/usr/bin/env python3
"""P4 — Real diversity metrics for the four-method benchmark (P0-2).

Computes, from the deposited molecule sets (best SMILES per method per seed,
results/benchmark_molecules/p4_benchmark_molecules_seed_*.csv):

  * mean pairwise Tanimoto dissimilarity (1 - similarity) over ECFP4
    (Morgan radius 2, 2048 bits) for each method's 20 molecules;
  * number and fraction of unique Bemis-Murcko scaffolds;
  * 2D MDS coordinates (metric MDS on the Tanimoto dissimilarity matrix)
    for visualisation in the Supplementary Material.

Outputs:
  results/diversity/p4_diversity_metrics.csv
  results/diversity/p4_diversity_mds.csv
  (also prints a compact table for the SM)

Usage:
    python scripts/p4_compute_diversity.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit import DataStructs

RDLogger.DisableLog("rdApp.*")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
MOL_DIR = PROJECT_DIR / "results" / "benchmark_molecules_opt"
OUT_DIR = PROJECT_DIR / "results" / "diversity"

METHOD_ORDER = ["mcts", "random", "greedy", "ga"]
METHOD_LABELS = {"mcts": "MCTS+ScafVAE", "random": "Random", "greedy": "Greedy", "ga": "GA"}

RADIUS = 2
NBITS = 2048


def load_molecules() -> dict[str, list[tuple[str, int]]]:
    """Return {method: [(smiles, seed), ...]} from deposited molecule CSVs."""
    mols: dict[str, list[tuple[str, int]]] = {m: [] for m in METHOD_ORDER}
    if not MOL_DIR.exists():
        sys.exit(f"ERROR: {MOL_DIR} not found — run the molecule benchmark array first.")
    for path in sorted(MOL_DIR.glob("p4_benchmark_molecules_seed_*.csv")):
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                method = row["method"].strip().lower()
                if method in mols:
                    mols[method].append((row["best_smiles"], int(row["seed"])))
    return mols


def fingerprint(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, RADIUS, nBits=NBITS)
    return fp


def mean_pairwise_dissimilarity(fps: list) -> float:
    """Mean 1 - Tanimoto over all unique pairs."""
    n = len(fps)
    if n < 2:
        return float("nan")
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += 1.0 - DataStructs.TanimotoSimilarity(fps[i], fps[j])
            count += 1
    return total / count


def unique_murcko_scaffolds(smiles_list: list[str]) -> tuple[set[str], int]:
    scaffolds = set()
    n_valid = 0
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        n_valid += 1
        scaf = MurckoScaffold.MurckoScaffoldSmiles(mol=mol)
        scaffolds.add(scaf if scaf else smi)
    return scaffolds, n_valid


def mds_coords(dissim: np.ndarray, seed: int = 0) -> np.ndarray:
    """Metric MDS (2D) via classical scaling on -0.5*d^2 with a small ridge."""
    n = dissim.shape[0]
    if n < 3:
        return np.zeros((n, 2))
    # Constant (all-identical) dissimilarity matrix, e.g. deterministic greedy:
    # MDS would divide by a zero sum of squared distances; return zeros directly.
    if np.allclose(dissim, dissim[0, 0]):
        return np.zeros((n, 2))
    from sklearn.manifold import MDS

    mds = MDS(n_components=2, metric=True, dissimilarity="precomputed",
              random_state=seed, normalized_stress="auto")
    return mds.fit_transform(dissim)


def main() -> int:
    mols = load_molecules()
    out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics_rows = []
    all_mds: list[dict] = []
    print(f"{'Method':<16}{'n':>4}{'meanTanimotoDis':>17}{'uniqueScaf':>12}"
          f"{'scafFrac':>10}")
    print("-" * 60)

    for method in METHOD_ORDER:
        items = sorted(mols[method], key=lambda x: x[1])
        smiles = [s for s, _ in items]
        seeds = [sd for _, sd in items]
        n = len(smiles)

        fps = [fingerprint(s) for s in smiles]
        valid = [f for f in fps if f is not None]
        mean_dis = mean_pairwise_dissimilarity(valid) if len(valid) >= 2 else float("nan")

        scaffolds, n_valid = unique_murcko_scaffolds(smiles)
        scaf_frac = len(scaffolds) / n_valid if n_valid else float("nan")

        metrics_rows.append({
            "method": method,
            "n_molecules": n,
            "n_valid_smiles": n_valid,
            "mean_pairwise_tanimoto_dissimilarity": round(mean_dis, 4),
            "n_unique_bm_scaffolds": len(scaffolds),
            "unique_scaffold_fraction": round(scaf_frac, 4),
        })
        print(f"{METHOD_LABELS[method]:<16}{n:>4}{mean_dis:>17.4f}"
              f"{len(scaffolds):>12}{scaf_frac:>10.4f}")

        # MDS on the pairwise dissimilarity matrix (all unique pairs)
        if len(valid) >= 3:
            nv = len(valid)
            dmat = np.zeros((nv, nv))
            for i in range(nv):
                for j in range(i + 1, nv):
                    d = 1.0 - DataStructs.TanimotoSimilarity(valid[i], valid[j])
                    dmat[i, j] = dmat[j, i] = d
            coords = mds_coords(dmat, seed=42)
            for k, (smi, sd) in enumerate(items):
                if fps[k] is None:
                    continue
                all_mds.append({
                    "method": method, "seed": sd, "smiles": smi,
                    "mds_x": round(float(coords[k, 0]), 5),
                    "mds_y": round(float(coords[k, 1]), 5),
                })

    # ── Write outputs ───────────────────────────────────────────────────
    with open(out_dir / "p4_diversity_metrics.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(metrics_rows[0].keys()))
        writer.writeheader()
        writer.writerows(metrics_rows)
    print(f"\nMetrics CSV: {out_dir / 'p4_diversity_metrics.csv'}")

    if all_mds:
        with open(out_dir / "p4_diversity_mds.csv", "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(all_mds[0].keys()))
            writer.writeheader()
            writer.writerows(all_mds)
        print(f"MDS CSV:      {out_dir / 'p4_diversity_mds.csv'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
