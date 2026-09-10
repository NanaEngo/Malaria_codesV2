#!/usr/bin/env python3
"""P1 Statistical Audit — Adapted from P2 Rigorous Audit

This script computes rigorous statistical analyses for P1 Set A (17 compounds)
using P2's battle-tested statistical framework:
- 100,000-permutation p-values
- 10,000-bootstrap 95% confidence intervals  
- Post-hoc power analysis
- Bonferroni correction for multiple comparisons

Adapts P2's p2_rigorous_audit.py for P1 data structure while keeping all
statistical functions unchanged.

Inputs:
    results/SI_Table_SNEW5_polypharmacology_metrics.csv (ACSI, PNS)
    results/p1_nfav_scores.csv (N_fav, when available)
    results/p1_rrs_classification.csv (RRS, when available)

Outputs:
    results/p1_statistical_audit.csv
    results/p1_statistical_audit.json
    results/p1_statistical_audit_manifest.json

Author: Adapted from P2 (Project2_Polypharmacology_MD_ValidationV2607)
Date: 2026-09-09
Status: READY (awaits P1 docking outputs for full analysis)
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr, norm

SEED = 42
N_PERMUTATIONS = 100_000
N_BOOTSTRAP = 10_000
BONFERRONI_N_HYPOTHESES = 3  # PNS_vs_RRS, ACSI_vs_RRS, ACSI_vs_PNS


def permutation_test(
    x: np.ndarray,
    y: np.ndarray,
    n_perm: int = 100_000,
    seed: int = 42,
) -> dict[str, float]:
    """Two-sided permutation test for Spearman correlation.
    
    Args:
        x: First variable (n,)
        y: Second variable (n,)
        n_perm: Number of permutations
        seed: Random seed
        
    Returns:
        Dictionary with rho, p_two_sided, n_permutations
    """
    rng = np.random.RandomState(seed)
    n = len(x)
    
    # Observed correlation
    rho_obs, _ = spearmanr(x, y)
    
    # Permutation distribution
    rho_perm = np.zeros(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        rho_perm[i], _ = spearmanr(x, y_perm)
    
    # Two-sided p-value
    p_two_sided = np.mean(np.abs(rho_perm) >= np.abs(rho_obs))
    
    return {
        "rho": float(rho_obs),
        "p_two_sided": float(p_two_sided),
        "n_permutations": n_perm,
    }


def bootstrap_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_boot: int = 10_000,
    seed: int = 42,
    alpha: float = 0.05,
) -> dict[str, float]:
    """Bootstrap 95% confidence interval for Spearman correlation.
    
    Args:
        x: First variable (n,)
        y: Second variable (n,)
        n_boot: Number of bootstrap iterations
        seed: Random seed
        alpha: Significance level (0.05 for 95% CI)
        
    Returns:
        Dictionary with ci_low, ci_high, n_bootstrap
    """
    rng = np.random.RandomState(seed)
    n = len(x)
    
    rho_boot = np.zeros(n_boot)
    for i in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        rho_boot[i], _ = spearmanr(x[idx], y[idx])
    
    ci_low = np.percentile(rho_boot, 100 * alpha / 2)
    ci_high = np.percentile(rho_boot, 100 * (1 - alpha / 2))
    
    return {
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n_bootstrap": n_boot,
    }


def compute_power(n: int, rho: float, alpha: float = 0.017) -> float:
    """Post-hoc power for Spearman correlation test.
    
    Uses Fisher Z-transformation approximation.
    
    Args:
        n: Sample size
        rho: Observed or hypothesized correlation
        alpha: Significance level (Bonferroni-corrected)
        
    Returns:
        Statistical power (0 to 1)
    """
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = 0.5 * np.log((1 + rho) / (1 - rho)) * np.sqrt(n - 3)
    power = 1 - norm.cdf(z_alpha - np.abs(z_beta))
    return float(power)


def analyze_correlation(
    data: pd.DataFrame,
    var1: str,
    var2: str,
    analysis_set: str,
    inference_scope: str,
    n_perm: int = N_PERMUTATIONS,
    n_boot: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> dict:
    """Complete correlation analysis: permutation + bootstrap + power.
    
    Args:
        data: DataFrame with both variables
        var1: Name of first variable
        var2: Name of second variable
        analysis_set: Description of cohort (e.g., "available_17")
        inference_scope: Caveat statement
        n_perm: Number of permutations
        n_boot: Number of bootstrap iterations
        seed: Random seed
        
    Returns:
        Dictionary with all statistics
    """
    # Drop missing values
    df_clean = data[[var1, var2]].dropna()
    n = len(df_clean)
    
    if n < 3:
        return {
            "analysis_set": analysis_set,
            "comparison": f"{var1}_vs_{var2}",
            "n": n,
            "error": "insufficient_data",
        }
    
    x = df_clean[var1].values
    y = df_clean[var2].values
    
    # Permutation test
    perm_results = permutation_test(x, y, n_perm=n_perm, seed=seed)
    
    # Bootstrap CI
    boot_results = bootstrap_ci(x, y, n_boot=n_boot, seed=seed)
    
    # Bonferroni correction
    p_bonferroni = min(1.0, perm_results["p_two_sided"] * BONFERRONI_N_HYPOTHESES)
    
    # Power analysis (for observed rho)
    power = compute_power(n, rho=perm_results["rho"], alpha=0.017)
    
    return {
        "analysis_set": analysis_set,
        "comparison": f"{var1}_vs_{var2}",
        "n": n,
        "spearman_rho": perm_results["rho"],
        "permutation_p_two_sided": perm_results["p_two_sided"],
        "bonferroni_p_three_hypotheses": p_bonferroni,
        "bootstrap_ci95_low": boot_results["ci_low"],
        "bootstrap_ci95_high": boot_results["ci_high"],
        "power_at_alpha_0017": power,
        "inference_scope": inference_scope,
    }


def main(args):
    """Run P1 statistical audit."""
    print("=== P1 Statistical Audit (Adapted from P2) ===\n")
    
    # Load P1 data
    print("Loading P1 data...")
    table_path = Path(args.input_table)
    if not table_path.exists():
        raise FileNotFoundError(f"Input table not found: {table_path}")
    
    data = pd.read_csv(table_path)
    print(f"✅ Loaded {len(data)} compounds from {table_path.name}\n")
    
    # Check available variables
    available_vars = set(data.columns)
    print(f"Available variables: {sorted(available_vars)}\n")
    
    # Required variables
    required = {"ACSI", "PNS"}
    missing = required - available_vars
    if missing:
        raise ValueError(f"Missing required variables: {missing}")
    
    # Optional variables (for full analysis)
    optional = {"N_fav", "RRS_class", "RRS_mean"}
    has_nfav = "N_fav" in available_vars and not data["N_fav"].astype(str).str.contains("PENDING").any()
    has_rrs = "RRS_mean" in available_vars or "RRS_class" in available_vars
    
    # Analysis scope
    inference_scope = "exploratory_selected_cohort; not independent validation"
    
    # Run correlation analyses
    results = []
    
    print("Running correlation analyses...")
    print(f"  - {N_PERMUTATIONS:,} permutations per test")
    print(f"  - {N_BOOTSTRAP:,} bootstrap iterations per test")
    print(f"  - Bonferroni correction for {BONFERRONI_N_HYPOTHESES} hypotheses\n")
    
    # 1. ACSI vs PNS (always available)
    print("1. ACSI vs PNS...")
    results.append(analyze_correlation(
        data, "ACSI", "PNS", "available_17", inference_scope,
        n_perm=args.n_permutations, n_boot=args.n_bootstrap, seed=args.seed
    ))
    
    # 2. N_fav vs RRS (if available)
    if has_nfav and has_rrs:
        print("2. N_fav vs RRS...")
        rrs_var = "RRS_mean" if "RRS_mean" in available_vars else "RRS_class"
        results.append(analyze_correlation(
            data, "N_fav", rrs_var, "available_17", inference_scope,
            n_perm=args.n_permutations, n_boot=args.n_bootstrap, seed=args.seed
        ))
    else:
        print("2. N_fav vs RRS... SKIPPED (awaiting P1 docking)")
    
    # 3. ACSI vs RRS (if available)
    if has_rrs:
        print("3. ACSI vs RRS...")
        rrs_var = "RRS_mean" if "RRS_mean" in available_vars else "RRS_class"
        results.append(analyze_correlation(
            data, "ACSI", rrs_var, "available_17", inference_scope,
            n_perm=args.n_permutations, n_boot=args.n_bootstrap, seed=args.seed
        ))
    else:
        print("3. ACSI vs RRS... SKIPPED (awaiting P1 docking)")
    
    # 4. PNS vs RRS (if available)
    if has_rrs:
        print("4. PNS vs RRS...")
        rrs_var = "RRS_mean" if "RRS_mean" in available_vars else "RRS_class"
        results.append(analyze_correlation(
            data, "PNS", rrs_var, "available_17", inference_scope,
            n_perm=args.n_permutations, n_boot=args.n_bootstrap, seed=args.seed
        ))
    else:
        print("4. PNS vs RRS... SKIPPED (awaiting P1 docking)")
    
    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # CSV
    df_results = pd.DataFrame(results)
    csv_path = output_dir / "p1_statistical_audit.csv"
    df_results.to_csv(csv_path, index=False)
    print(f"\n✅ Saved CSV: {csv_path}")
    
    # JSON
    json_path = output_dir / "p1_statistical_audit.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Saved JSON: {json_path}")
    
    # Manifest
    manifest = {
        "script": "p1_statistical_audit.py",
        "date": "2026-09-09",
        "input_table": str(table_path),
        "n_compounds": len(data),
        "n_permutations": args.n_permutations,
        "n_bootstrap": args.n_bootstrap,
        "seed": args.seed,
        "bonferroni_n_hypotheses": BONFERRONI_N_HYPOTHESES,
        "analyses_completed": len(results),
        "has_nfav": has_nfav,
        "has_rrs": has_rrs,
        "adapted_from": "Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_rigorous_audit.py",
    }
    manifest_path = output_dir / "p1_statistical_audit_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"✅ Saved manifest: {manifest_path}")
    
    # Print summary
    print("\n=== Summary ===")
    for result in results:
        if "error" in result:
            print(f"\n{result['comparison']}: ERROR ({result['error']})")
            continue
        
        print(f"\n{result['comparison']}:")
        print(f"  n = {result['n']}")
        print(f"  ρ = {result['spearman_rho']:.3f}")
        print(f"  p = {result['permutation_p_two_sided']:.4f}")
        print(f"  p_Bonf = {result['bonferroni_p_three_hypotheses']:.4f}")
        print(f"  95% CI = [{result['bootstrap_ci95_low']:.3f}, {result['bootstrap_ci95_high']:.3f}]")
        print(f"  Power = {result['power_at_alpha_0017']:.3f}")
    
    print("\n✅ P1 statistical audit complete!")
    print(f"   Completed: {len(results)}/{4} analyses")
    if not has_nfav or not has_rrs:
        print(f"   Remaining: {4 - len(results)} (awaiting P1 docking)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P1 Statistical Audit (adapted from P2)")
    parser.add_argument(
        "--input-table",
        type=str,
        default="results/SI_Table_SNEW5_polypharmacology_metrics.csv",
        help="Input table with ACSI, PNS, N_fav, RRS",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory",
    )
    parser.add_argument(
        "--n-permutations",
        type=int,
        default=N_PERMUTATIONS,
        help=f"Number of permutations (default: {N_PERMUTATIONS:,})",
    )
    parser.add_argument(
        "--n-bootstrap",
        type=int,
        default=N_BOOTSTRAP,
        help=f"Number of bootstrap iterations (default: {N_BOOTSTRAP:,})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Random seed (default: {SEED})",
    )
    
    args = parser.parse_args()
    main(args)
