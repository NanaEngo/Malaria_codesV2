#!/usr/bin/env python3
"""
Generate drug-likeness compliance table for V7 Set-C candidates (PP-01 to PP-17)

Evaluates compliance with:
- Lipinski Rule of 5 (MW≤500, logP≤5, HBD≤5, HBA≤10)
- Veber Rules (RB≤10, TPSA≤140)
- QED threshold (>0.70 for high drug-likeness)
- NPL threshold (>0 for NP-relatedness)

Outputs:
- CSV: results/derived/v7_druglikeness_compliance.csv
- LaTeX: manuscript/tables/sm_table_druglikeness.tex
"""

import pandas as pd
from pathlib import Path

def evaluate_lipinski(row):
    """Evaluate Lipinski Rule of 5 compliance"""
    passes = (
        row['MW'] <= 500 and
        row['logP'] <= 5 and
        row['HBD'] <= 5 and
        row['HBA'] <= 10
    )
    return 'Pass' if passes else 'Fail'

def evaluate_veber(row):
    """Evaluate Veber rules compliance"""
    passes = (
        row['RB'] <= 10 and
        row['TPSA'] <= 140
    )
    return 'Pass' if passes else 'Fail'

def evaluate_qed(row):
    """Evaluate QED threshold (high drug-likeness)"""
    return 'High' if row['QED'] > 0.70 else 'Moderate'

def evaluate_npl(row):
    """Evaluate NP-relatedness"""
    return 'Yes' if row['NPL'] > 0 else 'No'

def generate_latex_table(df, output_path):
    """Generate LaTeX table for supplementary material"""
    latex_lines = []
    
    # Table header
    latex_lines.append(r"\begin{table}[h!]")
    latex_lines.append(r"\centering")
    latex_lines.append(r"\caption{Drug-likeness compliance of Set-C polypharmacology candidates (PP-01 to PP-17). Lipinski: Lipinski Rule of Five (MW $\leq$ 500, logP $\leq$ 5, HBD $\leq$ 5, HBA $\leq$ 10); Veber: Veber rules (RB $\leq$ 10, TPSA $\leq$ 140 \si{\angstrom\squared}); QED: quantitative estimate of drug-likeness (High $>$ 0.70, Moderate $\leq$ 0.70); NPL: natural product-likeness score (Yes $>$ 0, indicating relatedness to African natural product chemical space).}")
    latex_lines.append(r"\label{tab:druglikeness}")
    latex_lines.append(r"\small")
    latex_lines.append(r"\begin{tabular}{lccccccc}")
    latex_lines.append(r"\toprule")
    latex_lines.append(r"Candidate & Lipinski & Veber & QED & QED Value & NPL & NPL Value & Overall \\")
    latex_lines.append(r"\midrule")
    
    # Data rows
    for _, row in df.iterrows():
        cand = row['candidate_id']
        lipinski = row['Lipinski_compliance']
        veber = row['Veber_compliance']
        qed_class = row['QED_classification']
        qed_val = f"{row['QED']:.2f}"
        npl_class = row['NPL_classification']
        npl_val = f"{row['NPL']:.2f}"
        overall = row['Overall_compliance']
        
        # Format pass/fail with check/cross symbols
        lipinski_sym = r"\checkmark" if lipinski == 'Pass' else r"\texttimes"
        veber_sym = r"\checkmark" if veber == 'Pass' else r"\texttimes"
        
        latex_lines.append(f"{cand} & {lipinski_sym} & {veber_sym} & {qed_class} & {qed_val} & {npl_class} & {npl_val} & {overall} \\\\")
    
    # Summary statistics
    latex_lines.append(r"\midrule")
    n_total = len(df)
    n_lipinski = (df['Lipinski_compliance'] == 'Pass').sum()
    n_veber = (df['Veber_compliance'] == 'Pass').sum()
    n_qed_high = (df['QED_classification'] == 'High').sum()
    n_npl_yes = (df['NPL_classification'] == 'Yes').sum()
    n_full = (df['Overall_compliance'] == 'Full').sum()
    
    latex_lines.append(f"Compliant & {n_lipinski}/{n_total} & {n_veber}/{n_total} & {n_qed_high}/{n_total} & --- & {n_npl_yes}/{n_total} & --- & {n_full}/{n_total} \\\\")
    latex_lines.append(f"Percentage & {100*n_lipinski/n_total:.0f}\\% & {100*n_veber/n_total:.0f}\\% & {100*n_qed_high/n_total:.0f}\\% & --- & {100*n_npl_yes/n_total:.0f}\\% & --- & {100*n_full/n_total:.0f}\\% \\\\")
    
    latex_lines.append(r"\bottomrule")
    latex_lines.append(r"\end{tabular}")
    latex_lines.append(r"\end{table}")
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(latex_lines))
    
    print(f"✓ LaTeX table written to: {output_path}")

def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    input_csv = base_dir / "results/derived/v7_physicochemical_properties.csv"
    output_csv = base_dir / "results/derived/v7_druglikeness_compliance.csv"
    output_latex = base_dir / "manuscript/tables/sm_table_druglikeness.tex"
    
    # Create output directories if needed
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_latex.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("V7 Drug-Likeness Compliance Evaluation")
    print("=" * 70)
    
    # Read input data
    print(f"\n[1/4] Reading physicochemical properties: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"      Loaded {len(df)} candidates")
    
    # Evaluate compliance
    print(f"\n[2/4] Evaluating drug-likeness compliance...")
    
    df['Lipinski_compliance'] = df.apply(evaluate_lipinski, axis=1)
    df['Veber_compliance'] = df.apply(evaluate_veber, axis=1)
    df['QED_classification'] = df.apply(evaluate_qed, axis=1)
    df['NPL_classification'] = df.apply(evaluate_npl, axis=1)
    
    # Overall compliance: Pass all criteria
    df['Overall_compliance'] = df.apply(
        lambda row: 'Full' if (
            row['Lipinski_compliance'] == 'Pass' and
            row['Veber_compliance'] == 'Pass' and
            row['QED_classification'] == 'High' and
            row['NPL_classification'] == 'Yes'
        ) else 'Partial',
        axis=1
    )
    
    # Select columns for output
    compliance_df = df[[
        'candidate_id', 'canonical_smiles',
        'MW', 'logP', 'HBD', 'HBA', 'TPSA', 'RB', 'QED', 'NPL',
        'Lipinski_compliance', 'Veber_compliance', 
        'QED_classification', 'NPL_classification',
        'Overall_compliance'
    ]]
    
    # Save CSV
    print(f"\n[3/4] Saving CSV: {output_csv}")
    compliance_df.to_csv(output_csv, index=False)
    print(f"      ✓ Saved {len(compliance_df)} candidate evaluations")
    
    # Generate LaTeX table
    print(f"\n[4/4] Generating LaTeX table: {output_latex}")
    generate_latex_table(compliance_df, output_latex)
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("COMPLIANCE SUMMARY")
    print("=" * 70)
    
    n_total = len(compliance_df)
    
    print(f"\nLipinski Rule of 5:")
    n_pass = (compliance_df['Lipinski_compliance'] == 'Pass').sum()
    print(f"  Pass: {n_pass}/{n_total} ({100*n_pass/n_total:.1f}%)")
    
    print(f"\nVeber Rules:")
    n_pass = (compliance_df['Veber_compliance'] == 'Pass').sum()
    print(f"  Pass: {n_pass}/{n_total} ({100*n_pass/n_total:.1f}%)")
    
    print(f"\nQED (High Drug-Likeness):")
    n_high = (compliance_df['QED_classification'] == 'High').sum()
    print(f"  High (>0.70): {n_high}/{n_total} ({100*n_high/n_total:.1f}%)")
    print(f"  Moderate (≤0.70): {n_total - n_high}/{n_total} ({100*(n_total-n_high)/n_total:.1f}%)")
    
    print(f"\nNatural Product-Likeness:")
    n_yes = (compliance_df['NPL_classification'] == 'Yes').sum()
    print(f"  NP-related (NPL>0): {n_yes}/{n_total} ({100*n_yes/n_total:.1f}%)")
    
    print(f"\nOverall Compliance (All Criteria):")
    n_full = (compliance_df['Overall_compliance'] == 'Full').sum()
    print(f"  Full: {n_full}/{n_total} ({100*n_full/n_total:.1f}%)")
    print(f"  Partial: {n_total - n_full}/{n_total} ({100*(n_total-n_full)/n_total:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  - CSV: {output_csv}")
    print(f"  - LaTeX: {output_latex}")
    print(f"\nNext step: Insert LaTeX table into V7 SM")

if __name__ == "__main__":
    main()
