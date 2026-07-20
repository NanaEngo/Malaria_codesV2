"""
p1_prior_comparison.py
========================
REVISION-ROADMAP R11b — Quantitative comparison with prior African NP studies.

Uses ANPDB 2025 (data/external/anpdb_clean.csv, 11,448 compounds) as the
unified superset of NANPDB (~4,500) and EANPDB (~1,870). Reports:
  1. Tanimoto overlap between 396 seed NPs and ANPDB (threshold 0.4)
  2. Scaffold diversity: unique Bemis-Murcko scaffolds + diversity fraction
  3. % unique seed scaffolds not present in ANPDB

Outputs (results/):
  p1_prior_comparison.csv          — per-seed-NP max Tanimoto to ANPDB
  p1_prior_comparison_summary.txt  — statistics + suggested Discussion paragraph

Usage:
  python scripts/revision/p1_prior_comparison.py [--threshold 0.4]

Requirements:
  conda activate malaria_md
"""

import argparse
from pathlib import Path

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from rdkit.Chem.Scaffolds import MurckoScaffold

PROJECT = Path(__file__).parent.parent.parent
RESULTS = PROJECT / "results"
DATA    = PROJECT / "data"

ANPDB_PATH = DATA / "external" / "anpdb_clean.csv"
SEED_PATH  = RESULTS / "seed_african_nps_smiles.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def canon(smi: str) -> "str | None":
    mol = Chem.MolFromSmiles(str(smi))
    return Chem.MolToSmiles(mol) if mol else None


def morgan_fp(smi: str, radius: int = 2, n_bits: int = 2048):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)


def murcko_smi(smi: str) -> "str | None":
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    scaf = MurckoScaffold.GetScaffoldForMol(mol)
    if scaf is None or scaf.GetNumAtoms() == 0:
        return None
    return Chem.MolToSmiles(scaf)


def scaffold_diversity(smiles: list) -> dict:
    scaffolds = {}
    for smi in smiles:
        s = murcko_smi(smi)
        if s:
            scaffolds[s] = scaffolds.get(s, 0) + 1
    n = len(smiles)
    return {
        "n_molecules":        n,
        "n_scaffolds":        len(scaffolds),
        "diversity_fraction": len(scaffolds) / n if n else 0.0,
        "scaffold_set":       set(scaffolds.keys()),
    }


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_seeds() -> list:
    df = pd.read_csv(SEED_PATH)
    smiles = [canon(s) for s in df["smiles"].dropna()]
    smiles = [s for s in smiles if s]
    print(f"  Seed NPs loaded: {len(smiles)}")
    return smiles


def load_anpdb() -> list:
    df = pd.read_csv(ANPDB_PATH)
    # anpdb_clean.csv has a 'smiles' column
    col = next((c for c in df.columns if c.lower() == "smiles"), df.columns[3])
    smiles = [canon(s) for s in df[col].dropna()]
    smiles = [s for s in smiles if s]
    print(f"  ANPDB loaded: {len(smiles)} valid molecules")
    return smiles


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="R11b: Compare seed African NPs with ANPDB 2025")
    parser.add_argument("--threshold", type=float, default=0.4,
                        help="Tanimoto similarity threshold for overlap (default: 0.4)")
    args = parser.parse_args()

    print("=" * 65)
    print("R11b: Prior African NP Database Comparison (ANPDB 2025)")
    print("=" * 65)

    seeds  = load_seeds()
    anpdb  = load_anpdb()

    # --- Fingerprints ---
    print("\n  Computing fingerprints...")
    seed_fps  = [(s, morgan_fp(s)) for s in seeds]
    seed_fps  = [(s, fp) for s, fp in seed_fps if fp is not None]
    anpdb_fps = [morgan_fp(s) for s in anpdb]
    anpdb_fps = [fp for fp in anpdb_fps if fp is not None]

    # --- Tanimoto overlap ---
    print(f"  Computing pairwise Tanimoto ({len(seed_fps)} seeds × {len(anpdb_fps)} ANPDB)...")
    records = []
    overlap_count = 0
    for smi, fp in seed_fps:
        sims = DataStructs.BulkTanimotoSimilarity(fp, anpdb_fps)
        max_sim = float(max(sims)) if sims else 0.0
        if max_sim >= args.threshold:
            overlap_count += 1
        records.append({"seed_smiles": smi, "max_tanimoto_anpdb": round(max_sim, 4)})

    df_out = pd.DataFrame(records)
    overlap_pct   = overlap_count / len(seed_fps) * 100
    mean_max_tan  = df_out["max_tanimoto_anpdb"].mean()
    median_max_tan = df_out["max_tanimoto_anpdb"].median()

    print(f"  Overlap (Tanimoto ≥ {args.threshold}): "
          f"{overlap_count}/{len(seed_fps)} ({overlap_pct:.1f}%)")
    print(f"  Mean max Tanimoto: {mean_max_tan:.3f}  |  Median: {median_max_tan:.3f}")

    # --- Scaffold diversity ---
    print("\n  Computing scaffold diversity...")
    seed_scaf  = scaffold_diversity(seeds)
    anpdb_scaf = scaffold_diversity(anpdb)

    shared_scaffolds = seed_scaf["scaffold_set"] & anpdb_scaf["scaffold_set"]
    unique_seed_scaf = seed_scaf["scaffold_set"] - anpdb_scaf["scaffold_set"]
    unique_pct = len(unique_seed_scaf) / len(seed_scaf["scaffold_set"]) * 100 \
                 if seed_scaf["scaffold_set"] else 0.0

    print(f"  Seed scaffolds:  {seed_scaf['n_scaffolds']} "
          f"(diversity {seed_scaf['diversity_fraction']:.3f})")
    print(f"  ANPDB scaffolds: {anpdb_scaf['n_scaffolds']} "
          f"(diversity {anpdb_scaf['diversity_fraction']:.3f})")
    print(f"  Shared: {len(shared_scaffolds)}  |  "
          f"Unique to seeds: {len(unique_seed_scaf)} ({unique_pct:.1f}%)")

    # --- Save CSV ---
    out_csv = RESULTS / "p1_prior_comparison.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # --- Summary text ---
    discussion_para = (
        f'The {len(seeds)} African NPs used as seeds overlap {overlap_pct:.1f}% '
        f'with ANPDB 2025 (NtieKang et al., 2018; Simoben et al., 2020; '
        f'11,448 compounds) by Tanimoto similarity (≥{args.threshold}), '
        f'confirming coverage of the major African NP databases while '
        f'incorporating {unique_pct:.1f}% unique scaffolds not present in ANPDB.'
    )

    lines = [
        "R11b: Prior African NP Database Comparison (ANPDB 2025)",
        "=" * 65,
        f"Seed NPs:              {len(seeds)}",
        f"ANPDB molecules:       {len(anpdb)}",
        f"Tanimoto threshold:    {args.threshold}",
        "",
        f"Overlap count:         {overlap_count}/{len(seed_fps)} ({overlap_pct:.1f}%)",
        f"Mean max Tanimoto:     {mean_max_tan:.3f}",
        f"Median max Tanimoto:   {median_max_tan:.3f}",
        "",
        f"Seed unique scaffolds: {seed_scaf['n_scaffolds']} "
        f"(diversity {seed_scaf['diversity_fraction']:.3f})",
        f"ANPDB unique scaffolds:{anpdb_scaf['n_scaffolds']} "
        f"(diversity {anpdb_scaf['diversity_fraction']:.3f})",
        f"Shared scaffolds:      {len(shared_scaffolds)}",
        f"Unique to seeds:       {len(unique_seed_scaf)} ({unique_pct:.1f}%)",
        "",
        "Suggested Discussion paragraph:",
        "-" * 65,
        discussion_para,
    ]

    out_txt = RESULTS / "p1_prior_comparison_summary.txt"
    out_txt.write_text("\n".join(lines))
    print(f"  Saved: {out_txt}")
    print(f"\n  Discussion paragraph:\n  {discussion_para}")


if __name__ == "__main__":
    main()
