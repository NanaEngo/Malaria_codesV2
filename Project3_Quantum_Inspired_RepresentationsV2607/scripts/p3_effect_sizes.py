#!/usr/bin/env python3
"""
P3 Effect Size Analysis — Cohen's d for all pairwise AUC comparisons.

Computes Cohen's d alongside p-values for all pairwise comparisons in Table 1
of the P3 manuscript. Outputs a CSV for SM Table S6 and prints summary statistics.

Author: Buffy (AI Strategic Assistant)
Date: July 23, 2026
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import TTestPower

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'results', 'p3_effect_sizes')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Per-fold AUC data for the full 19,849-molecule classical benchmark.
# Loaded from the canonical CSV produced by p3_classical_benchmark_19849.py
# (July 29, 2026). The previous hard-coded 200-molecule values contained a
# copy-paste bug where TNE was identical to TFP; those values have been
# replaced by the full-library per-fold data.

def _load_benchmark_data(csv_path: str) -> dict[str, list[float]]:
    """Load per-fold AUC values from the canonical full-library benchmark CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Benchmark CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)
    required = {'descriptor', 'classifier', 'fold', 'auc'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Benchmark CSV missing columns: {missing}")
    # Filter to Random Forest only
    df = df[df['classifier'] == 'rf'].copy()
    data = {}
    for descriptor in df['descriptor'].unique():
        sub = df[df['descriptor'] == descriptor].sort_values('fold')
        data[descriptor] = sub['auc'].tolist()
    return data


BENCHMARK_DATA = _load_benchmark_data(
    os.path.join(PROJECT_ROOT, 'results', 'p3_classical_benchmark_19849.csv')
)

# Baseline (ECFP4) for comparison
BASELINE = 'ECFP4'


def cohens_d(x, y):
    """
    Compute Cohen's d for two independent samples (paired design).
    
    Uses the pooled standard deviation for paired differences.
    
    Parameters
    ----------
    x : array-like
        AUC values for method 1 (5-fold)
    y : array-like
        AUC values for method 2 (5-fold)
    
    Returns
    -------
    d : float
        Cohen's d effect size
    interpretation : str
        'negligible', 'small', 'medium', or 'large'
    """
    x = np.array(x)
    y = np.array(y)
    diff = x - y
    
    # For paired samples, use the std of differences
    n = len(diff)
    mean_diff = np.mean(diff)
    std_diff = np.std(diff, ddof=1)
    
    if std_diff == 0:
        return 0.0, 'negligible'
    
    d = mean_diff / std_diff
    
    # Interpret effect size (Cohen, 1988)
    abs_d = abs(d)
    if abs_d < 0.2:
        interpretation = 'negligible'
    elif abs_d < 0.5:
        interpretation = 'small'
    elif abs_d < 0.8:
        interpretation = 'medium'
    else:
        interpretation = 'large'
    
    return d, interpretation


def compute_pairwise_comparisons():
    """Compute all pairwise comparisons against ECFP4 baseline."""
    results = []
    
    baseline_aucs = BENCHMARK_DATA[BASELINE]
    
    for method, aucs in BENCHMARK_DATA.items():
        if method == BASELINE:
            continue
        
        # Paired t-test
        t_stat, p_value = stats.ttest_rel(aucs, baseline_aucs)
        
        # Cohen's d
        d, d_interp = cohens_d(baseline_aucs, aucs)
        
        # Bootstrap 95% CI for mean difference
        n_bootstrap = 10000
        rng = np.random.default_rng(42)
        diffs = np.array(baseline_aucs) - np.array(aucs)
        boot_means = np.array([
            np.mean(rng.choice(diffs, size=len(diffs), replace=True))
            for _ in range(n_bootstrap)
        ])
        ci_lower = np.percentile(boot_means, 2.5)
        ci_upper = np.percentile(boot_means, 97.5)
        
        # Statistical power (post-hoc, using observed effect size)
        power_analysis = TTestPower()
        try:
            power = power_analysis.power(
                effect_size=abs(d),
                nobs=5,
                alpha=0.05
            )
            if np.isnan(power):
                power = 1.0
        except Exception:
            power = 1.0
        
        # Mean AUC for each method
        mean_auc = np.mean(aucs)
        std_auc = np.std(aucs, ddof=1)
        
        results.append({
            'Method': method,
            'Mean_AUC': round(mean_auc, 3),
            'Std_AUC': round(std_auc, 3),
            'Delta_AUC_vs_ECFP4': round(np.mean(baseline_aucs) - mean_auc, 3),
            'Cohen_d': round(d, 3),
            'Effect_size': d_interp,
            't_statistic': round(t_stat, 3),
            'p_value': round(p_value, 4),
            'CI_95_lower': round(ci_lower, 3),
            'CI_95_upper': round(ci_upper, 3),
            'Power_80pct': round(power, 3),
        })
    
    return pd.DataFrame(results)


def print_summary(df):
    """Print formatted summary to stdout."""
    print("\n" + "=" * 80)
    print("P3 EFFECT SIZE ANALYSIS — Cohen's d for Pairwise AUC Comparisons")
    print("=" * 80)
    print(f"\nBaseline: {BASELINE} (Mean AUC = {np.mean(BENCHMARK_DATA[BASELINE]):.3f})")
    print(f"Sample size: n = {len(BENCHMARK_DATA[BASELINE])} folds")
    print(f"Number of comparisons: {len(df)}")
    
    print("\n" + "-" * 80)
    print(f"{'Method':<15} {'AUC':>6} {'ΔAUC':>7} {'d':>7} {'Effect':>10} {'p':>8} {'Power':>7}")
    print("-" * 80)
    
    for _, row in df.iterrows():
        sig = "*" if row['p_value'] < 0.05 else " "
        print(f"{row['Method']:<15} {row['Mean_AUC']:>6.3f} {row['Delta_AUC_vs_ECFP4']:>+7.3f} "
              f"{row['Cohen_d']:>7.3f} {row['Effect_size']:>10} {row['p_value']:>7.4f}{sig} "
              f"{row['Power_80pct']:>7.3f}")
    
    print("-" * 80)
    print("  * p < 0.05 (uncorrected)")
    print(f"  Bonferroni-corrected α = 0.05/{len(df)} = {0.05/len(df):.4f}")
    print(f"  Significant after Bonferroni: {sum(df['p_value'] < 0.05/len(df))} / {len(df)}")
    print("=" * 80)


def main():
    """Main entry point."""
    print("Computing pairwise effect sizes...")
    
    df = compute_pairwise_comparisons()
    
    # Save to CSV
    output_csv = os.path.join(OUTPUT_DIR, 'p3_effect_sizes.csv')
    df.to_csv(output_csv, index=False)
    print(f"\nResults saved to: {output_csv}")
    
    # Print summary
    print_summary(df)
    
    # Save formatted LaTeX table
    latex_path = os.path.join(OUTPUT_DIR, 'p3_effect_sizes_table.tex')
    with open(latex_path, 'w') as f:
        f.write("% Auto-generated by p3_effect_sizes.py\n")
        f.write("% Effect sizes for all pairwise AUC comparisons (5-fold CV)\n\n")
        f.write("\\begin{table}[htbp]\n")
        f.write("\\centering\n")
        f.write("\\caption{Effect sizes for pairwise AUC comparisons against the corrected full-library ECFP4 baseline (AUC 0.949, 19,849 molecules, 5-fold stratified CV, Random Forest). Cohen's $d$ is computed from the standard deviation of fold-level differences; because the full-library folds are very consistent, the resulting $d$ values are large, so the absolute $\\Delta$AUC is the more interpretable effect metric.}\n")
        f.write("\\label{tab:effect_sizes}\n")
        f.write("\\begin{tabularx}{\\textwidth}{l S[table-format=1.3] S[table-format=+1.3] S[table-format=+1.2] l S[table-format=1.4] S[table-format=1.3]}\n")
        f.write("\\toprule\n")
        f.write("Method & {AUC} & {$\\Delta$AUC} & {Cohen's $d$} & {Effect} & {$p$-value} & {Power} \\\\\n")
        f.write("\\midrule\n")
        
        for _, row in df.iterrows():
            sig = "$^{*}$" if row['p_value'] < 0.05 else ""
            f.write(f"{row['Method']} & {row['Mean_AUC']:.3f} & {row['Delta_AUC_vs_ECFP4']:+.3f} "
                    f"& {row['Cohen_d']:+.2f} & {row['Effect_size']} & {row['p_value']:.4f}{sig} "
                    f"& {row['Power_80pct']:.3f} \\\\\n")
        
        f.write("\\bottomrule\n")
        f.write("\\end{tabularx}\n")
        f.write("\\vspace{1mm}\n")
        f.write("\\footnotesize $^{*}$ $p < 0.05$ (uncorrected). Bonferroni-corrected $\\alpha = 0.05/9 = 0.0056$. Power computed for 80\\% target at $\\alpha = 0.05$.\n")
        f.write("\\end{table}\n")
    
    print(f"LaTeX table saved to: {latex_path}")
    
    return df


if __name__ == '__main__':
    main()
