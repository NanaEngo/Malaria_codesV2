#!/usr/bin/env python3
"""
Merge all RRS-TFP task outputs into a unified dataset and compute H1-RRS correlation.

Called after p3_rrs_tfp_expansion.sbatch array completes.
Merges:
  1. p3_rrs_expanded_v2.csv (501 compounds with RRS scores)
  2. p3_rrs_tfp_task*.csv (per-task TFP outputs)
  3. p3_rrs_expanded_with_tfp_v2.csv (78 compounds with existing TFP)

Outputs:
  p3_rrs_tfp_final.csv — unified 500+ compound dataset with RRS + TFP
  p3_h1_rrs_correlation_final.txt — definitive H1-RRS correlation statistics
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, pearsonr

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results'

RRS_BASE = RESULTS_DIR / 'p3_rrs_expanded_v2.csv'
EXISTING_TFP = RESULTS_DIR / 'p3_rrs_expanded_with_tfp_v2.csv'
TASK_GLOB = 'p3_rrs_tfp_task*.csv'

TFP_H1_COLS = [f'H1_{feat}' for feat in
                ['entropy', 'count', 'max_pers', 'mean_pers',
                 'birth_mean', 'birth_std', 'death_mean', 'death_std',
                 'pers_q25', 'pers_q50', 'pers_q75']]


def main():
    print("=" * 70)
    print("P3 H1-RRS Definitive Correlation")
    print("=" * 70)

    # 1. Load base RRS data
    rrs_df = pd.read_csv(RRS_BASE)
    print(f"Loaded RRS data: {len(rrs_df)} compounds")
    if 'smiles' not in rrs_df.columns and 'input' in rrs_df.columns:
        rrs_df = rrs_df.rename(columns={'input': 'smiles'})

    # 2. Load existing TFP data
    existing_tfp = {}
    if EXISTING_TFP.exists():
        exist_df = pd.read_csv(EXISTING_TFP)
        if 'smiles' in exist_df.columns:
            for _, row in exist_df.iterrows():
                existing_tfp[row['smiles']] = row
            print(f"Loaded existing TFP: {len(existing_tfp)} compounds")

    # 3. Load per-task TFP outputs
    task_files = sorted(RESULTS_DIR.glob(TASK_GLOB))
    print(f"Found {len(task_files)} task output files")

    new_tfp = {}
    for tf in task_files:
        task_df = pd.read_csv(tf)
        for _, row in task_df.iterrows():
            smiles = row.get('smiles', '')
            if pd.isna(smiles) or not smiles:
                continue
            if row.get('tfp_valid', False):
                new_tfp[smiles] = row
    print(f"New TFPs from tasks: {len(new_tfp)} compounds")

    # 4. Merge: for each RRS compound, attach TFP if available
    merged_rows = []
    tfp_count = 0
    for _, rrs_row in rrs_df.iterrows():
        smiles = rrs_row.get('smiles', '')
        merged = rrs_row.to_dict()

        # Try existing TFP first, then new TFP
        tfp_source = existing_tfp.get(smiles) or new_tfp.get(smiles)
        if tfp_source is not None:
            for col in TFP_H1_COLS:
                merged[col] = tfp_source.get(col, np.nan)
            merged['tfp_valid'] = True
            tfp_count += 1
        else:
            for col in TFP_H1_COLS:
                merged[col] = np.nan
            merged['tfp_valid'] = False

        merged_rows.append(merged)

    merged_df = pd.DataFrame(merged_rows)
    print(f"\nMerged dataset: {len(merged_df)} compounds")
    print(f"  With TFP: {tfp_count}")
    print(f"  Without TFP: {len(merged_df) - tfp_count}")

    # 5. Save unified dataset
    output_csv = RESULTS_DIR / 'p3_rrs_tfp_final.csv'
    merged_df.to_csv(output_csv, index=False)
    print(f"\nSaved: {output_csv}")

    # 6. Compute H1-RRS correlation
    valid_df = merged_df.dropna(subset=['rrs_score'] + TFP_H1_COLS)
    print(f"\nCompounds with valid RRS + TFP: {len(valid_df)}")

    if len(valid_df) < 10:
        print("ERROR: Insufficient data for correlation analysis")
        return

    # Class distribution
    print("\nClass distribution:")
    for cls in ['A', 'B', 'C', 'D', 'Unknown']:
        count = (valid_df['rrs_class'] == cls).sum()
        if count > 0:
            print(f"  Class {cls}: {count}")

    # Correlations for each H1 feature
    results = []
    for col in TFP_H1_COLS:
        rho, p = spearmanr(valid_df[col], valid_df['rrs_score'])
        results.append({
            'feature': col,
            'spearman_rho': round(rho, 4),
            'p_value': round(p, 6),
            'n': len(valid_df),
        })

    results_df = pd.DataFrame(results)

    # Print key results
    print("\n" + "=" * 70)
    print("H1-RRS CORRELATION RESULTS")
    print("=" * 70)
    print(f"Total compounds with valid RRS + TFP: {len(valid_df)}")
    print(f"Class distribution: A={sum(valid_df['rrs_class']=='A')}, "
          f"B={sum(valid_df['rrs_class']=='B')}, "
          f"C={sum(valid_df['rrs_class']=='C')}, "
          f"D={sum(valid_df['rrs_class']=='D')}, "
          f"Unknown={sum(valid_df['rrs_class']=='Unknown')}")
    print()

    # Key H1 features
    for feat in ['H1_count', 'H1_entropy', 'H1_total_persistence', 'H1_max_pers', 'H1_mean_pers']:
        if feat in valid_df.columns:
            rho, p = spearmanr(valid_df[feat], valid_df['rrs_score'])
            sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'n.s.'))
            print(f"  {feat:<30s}  rho={rho:+.4f}  p={p:.4f}  {sig}")

    # Also try H1_total_persistence (sum of persistence values)
    if 'H1_count' in valid_df.columns and 'H1_mean_pers' in valid_df.columns:
        valid_df = valid_df.copy()
        valid_df['H1_total_persistence'] = valid_df['H1_count'] * valid_df['H1_mean_pers']
        rho, p = spearmanr(valid_df['H1_total_persistence'], valid_df['rrs_score'])
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'n.s.'))
        print(f"  {'H1_total_persistence':<30s}  rho={rho:+.4f}  p={p:.4f}  {sig}")

    # Save summary
    summary_lines = [
        "=" * 70,
        "P3 H1-RRS DEFINITIVE CORRELATION",
        "=" * 70,
        f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total compounds: {len(merged_df)}",
        f"Valid (RRS + TFP): {len(valid_df)}",
        f"Class A: {sum(valid_df['rrs_class']=='A')}",
        f"Class B: {sum(valid_df['rrs_class']=='B')}",
        f"Class C: {sum(valid_df['rrs_class']=='C')}",
        f"Class D: {sum(valid_df['rrs_class']=='D')}",
        f"Unknown: {sum(valid_df['rrs_class']=='Unknown')}",
        "",
        "Key correlations (Spearman):",
    ]
    for feat in ['H1_count', 'H1_entropy', 'H1_max_pers', 'H1_mean_pers']:
        if feat in valid_df.columns:
            rho, p = spearmanr(valid_df[feat], valid_df['rrs_score'])
            summary_lines.append(f"  {feat}: rho={rho:+.4f}, p={p:.6f}")
    if 'H1_total_persistence' in valid_df.columns:
        rho, p = spearmanr(valid_df['H1_total_persistence'], valid_df['rrs_score'])
        summary_lines.append(f"  H1_total_persistence: rho={rho:+.4f}, p={p:.6f}")

    summary_lines.extend(["", "All feature correlations:"])
    for _, row in results_df.iterrows():
        summary_lines.append(f"  {row['feature']}: rho={row['spearman_rho']:+.4f}, p={row['p_value']:.6f}")

    summary_text = "\n".join(summary_lines)
    summary_file = RESULTS_DIR / 'p3_h1_rrs_correlation_final.txt'
    summary_file.write_text(summary_text)
    print(f"\nSaved: {summary_file}")

    # Save correlation table as CSV
    corr_csv = RESULTS_DIR / 'p3_h1_rrs_correlation_final.csv'
    results_df.to_csv(corr_csv, index=False)
    print(f"Saved: {corr_csv}")

    print("\n=== Correlation analysis completed ===")


if __name__ == '__main__':
    main()
