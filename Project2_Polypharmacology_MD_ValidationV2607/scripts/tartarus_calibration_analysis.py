"""
Tartarus Docking Calibration — Post-Processing

Computes Spearman ρ between Tartarus QuickVina scores (1SYH, 6Y2F, 4LDE)
and our consensus MPO scores from P1.

Inputs:
    results/tartarus_output.csv              — Tartarus docking scores
    data/from_project1/results/eos9gg2_malaria_final_drugbank_mpo.csv  — MPO scores

Outputs:
    results/tartarus_calibration.csv         — per-molecule Tartarus + MPO scores
    results/tartarus_calibration_summary.txt — Spearman ρ and statistics
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

RESULTS_DIR = Path(__file__).parent.parent / "results"
DATA_DIR = Path(__file__).parent.parent / "data" / "from_project1" / "results"


def main():
    parser = argparse.ArgumentParser(description="Tartarus calibration analysis")
    parser.add_argument("--tartarus-csv", type=Path,
                        default=RESULTS_DIR / "tartarus_output.csv",
                        help="Tartarus Docker output CSV")
    parser.add_argument("--mpo-csv", type=Path,
                        default=DATA_DIR / "eos9gg2_malaria_final_drugbank_mpo.csv",
                        help="MPO scores CSV from P1")
    args = parser.parse_args()

    print("=" * 60)
    print("Tartarus Docking Calibration Analysis")
    print("=" * 60)

    # --- Load Tartarus scores ---
    if not args.tartarus_csv.exists():
        print(f"ERROR: Tartarus output not found: {args.tartarus_csv}")
        print("  Run run_tartarus_docking.sh first.")
        return

    tar_df = pd.read_csv(args.tartarus_csv)
    print(f"\nTartarus scores: {len(tar_df)} molecules")

    # The Tartarus output has columns: smile, score_1syh, score_6y2f, score_4lde
    # Rename 'smile' → 'smiles' for consistency
    if "smile" in tar_df.columns:
        tar_df = tar_df.rename(columns={"smile": "smiles"})

    # Filter out failed docking (score = 10000)
    for col in ["score_1syh", "score_6y2f", "score_4lde"]:
        if col in tar_df.columns:
            n_fail = (tar_df[col] >= 9999).sum()
            print(f"  {col}: {n_fail} failed dockings (score=10000)")
            tar_df[col] = tar_df[col].replace(10000, np.nan)

    # Compute composite Tartarus score (mean of successful targets)
    tar_cols = [c for c in ["score_1syh", "score_6y2f", "score_4lde"] if c in tar_df.columns]
    tar_df["tar_composite"] = tar_df[tar_cols].mean(axis=1)
    n_valid = tar_df["tar_composite"].notna().sum()
    print(f"  Composite score available for {n_valid}/{len(tar_df)} molecules")

    # --- Load MPO scores ---
    if not args.mpo_csv.exists():
        print(f"ERROR: MPO CSV not found: {args.mpo_csv}")
        return

    mpo_df = pd.read_csv(args.mpo_csv)
    print(f"\nMPO scores: {len(mpo_df)} molecules")

    # Find SMILES column
    smiles_col = None
    for c in ["smiles", "input", "SMILES"]:
        if c in mpo_df.columns:
            smiles_col = c
            break
    if smiles_col is None:
        print("ERROR: No SMILES column found in MPO CSV")
        return

    mpo_df = mpo_df.rename(columns={smiles_col: "smiles"})

    # Find MPO score column
    mpo_col = None
    for c in ["weighted_mpo_score", "mpo_score", "MPO"]:
        if c in mpo_df.columns:
            mpo_col = c
            break
    if mpo_col is None:
        print("ERROR: No MPO score column found")
        print(f"  Available columns: {list(mpo_df.columns)}")
        return

    print(f"  Using MPO column: {mpo_col}")

    # --- Merge on SMILES ---
    merged = tar_df.merge(
        mpo_df[["smiles", mpo_col]],
        on="smiles",
        how="inner"
    )
    print(f"\nMerged: {len(merged)} molecules with both Tartarus and MPO scores")

    if len(merged) < 10:
        print("ERROR: Too few overlapping molecules for correlation analysis.")
        print("  Check that SMILES formats match between datasets.")
        return

    # --- Compute correlations ---
    print("\n" + "-" * 50)
    print("Spearman rank correlations (Tartarus vs MPO)")
    print("-" * 50)

    results = []

    # Composite vs MPO
    mask = merged["tar_composite"].notna() & merged[mpo_col].notna()
    if mask.sum() >= 10:
        rho, pval = spearmanr(merged.loc[mask, "tar_composite"],
                              merged.loc[mask, mpo_col])
        r_pearson, p_pearson = pearsonr(merged.loc[mask, "tar_composite"],
                                        merged.loc[mask, mpo_col])
        print(f"\n  Composite (mean 3 targets) vs {mpo_col}:")
        print(f"    Spearman ρ = {rho:.4f}  (p = {pval:.2e})")
        print(f"    Pearson r  = {r_pearson:.4f}  (p = {p_pearson:.2e})")
        print(f"    n = {mask.sum()}")
        results.append({
            "comparison": f"composite_vs_{mpo_col}",
            "spearman_rho": rho,
            "spearman_p": pval,
            "pearson_r": r_pearson,
            "pearson_p": p_pearson,
            "n": int(mask.sum()),
        })

    # Per-target vs MPO
    for col in tar_cols:
        mask = merged[col].notna() & merged[mpo_col].notna()
        if mask.sum() >= 10:
            rho, pval = spearmanr(merged.loc[mask, col],
                                  merged.loc[mask, mpo_col])
            print(f"\n  {col} vs {mpo_col}:")
            print(f"    Spearman ρ = {rho:.4f}  (p = {pval:.2e})")
            print(f"    n = {mask.sum()}")
            results.append({
                "comparison": f"{col}_vs_{mpo_col}",
                "spearman_rho": rho,
                "spearman_p": pval,
                "pearson_r": np.nan,
                "pearson_p": np.nan,
                "n": int(mask.sum()),
            })

    # --- Score distributions ---
    print("\n" + "-" * 50)
    print("Score Distributions")
    print("-" * 50)

    for col in tar_cols + ["tar_composite"]:
        vals = merged[col].dropna()
        if len(vals) > 0:
            print(f"\n  {col}:")
            print(f"    n    = {len(vals)}")
            print(f"    mean = {vals.mean():.3f}")
            print(f"    std  = {vals.std():.3f}")
            print(f"    min  = {vals.min():.3f}")
            print(f"    max  = {vals.max():.3f}")
            print(f"    P25  = {vals.quantile(0.25):.3f}")
            print(f"    P50  = {vals.quantile(0.50):.3f}")
            print(f"    P75  = {vals.quantile(0.75):.3f}")

    # --- Save merged data ---
    out_csv = RESULTS_DIR / "tartarus_calibration.csv"
    merged.to_csv(out_csv, index=False)
    print(f"\nMerged data saved: {out_csv}")

    # --- Save summary ---
    summary_lines = [
        "Tartarus Docking Calibration Summary",
        "=" * 50,
        f"Molecules with Tartarus scores: {len(tar_df)}",
        f"Molecules with MPO scores:      {len(mpo_df)}",
        f"Overlap:                         {len(merged)}",
        "",
    ]

    for r in results:
        summary_lines.append(
            f"{r['comparison']}: Spearman ρ={r['spearman_rho']:.4f} "
            f"(p={r['spearman_p']:.2e}, n={r['n']})"
        )

    summary = "\n".join(summary_lines)
    summary_file = RESULTS_DIR / "tartarus_calibration_summary.txt"
    summary_file.write_text(summary)
    print(f"Summary saved: {summary_file}")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
