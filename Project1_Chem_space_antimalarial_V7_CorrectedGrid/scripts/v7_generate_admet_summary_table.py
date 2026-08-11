#!/usr/bin/env python3
"""
Generate ADMET summary table for V7 Set-C candidates (PP-01 to PP-17)

Since candidate-specific ADMET predictions are not available and ADMET-AI
has NumPy 2.x compatibility issues, this script generates a summary table
based on:
1. Library-level statistics from P1 V4 (n=810 with ADMET predictions)
2. Favorable drug-likeness profile (100% Lipinski/Veber compliance)
3. Literature-based safety expectations for natural product-inspired compounds

Outputs:
- LaTeX: manuscript/tables/sm_table_admet_summary.tex
- Note: This is a summary/proxy table, not candidate-specific predictions
"""

from pathlib import Path

def generate_latex_table(output_path):
    """
    Generate LaTeX table with ADMET profile summary
    
    Uses library-level statistics from BMAD:
    - CYP450: CYP2C9 26.1%, CYP2C19 42.4%, CYP3A4 42.6%, CYP2D6 17.0%
    - hERG: mean 11.7%, median 11.8%
    - Selectivity: 100% of 810 molecules have SI > 10
    """
    latex_lines = []
    
    # Table header
    latex_lines.append(r"\begin{table}[h!]")
    latex_lines.append(r"\centering")
    latex_lines.append(r"\caption{ADMET profile summary for Set-C polypharmacology candidates. Since candidate-specific ADMET predictions were not available during manuscript preparation, this table reports population-level statistics from the parent chemical space (n=810 African-natural-product-inspired compounds from P1 library). CYP450 values represent predicted inhibition probabilities; hERG represents cardiotoxicity risk; SI represents selectivity index (antiparasitic activity vs mammalian toxicity). All 17 Set-C candidates exhibit favorable drug-likeness (100\% Lipinski/Veber compliance, mean QED 0.703), suggesting low-to-moderate ADMET risk. Individual candidate profiling via experimental or computational validation is recommended for lead optimization.}")
    latex_lines.append(r"\label{tab:admet}")
    latex_lines.append(r"\small")
    latex_lines.append(r"\begin{tabular}{lcc}")
    latex_lines.append(r"\toprule")
    latex_lines.append(r"ADMET Property & Population Mean & Interpretation \\")
    latex_lines.append(r"\midrule")
    
    # CYP450 inhibition
    latex_lines.append(r"\multicolumn{3}{l}{\textbf{CYP450 Inhibition Probability}} \\")
    latex_lines.append(r"CYP2C9 & 26.1\% & Low-moderate risk \\")
    latex_lines.append(r"CYP2C19 & 42.4\% & Moderate risk \\")
    latex_lines.append(r"CYP3A4 & 42.6\% & Moderate risk \\")
    latex_lines.append(r"CYP2D6 & 17.0\% & Low risk \\")
    latex_lines.append(r"\midrule")
    
    # hERG and safety
    latex_lines.append(r"\multicolumn{3}{l}{\textbf{Cardiotoxicity \& Safety}} \\")
    latex_lines.append(r"hERG inhibition & 11.7\% (mean) & Low risk \\")
    latex_lines.append(r"hERG inhibition & 11.8\% (median) & Low risk \\")
    latex_lines.append(r"\midrule")
    
    # Selectivity
    latex_lines.append(r"\multicolumn{3}{l}{\textbf{Selectivity}} \\")
    latex_lines.append(r"Antiparasitic SI $>$ 10 & 100\% (n=810) & Highly selective \\")
    latex_lines.append(r"\midrule")
    
    # Drug-likeness summary (Set-C specific)
    latex_lines.append(r"\multicolumn{3}{l}{\textbf{Set-C Drug-Likeness (n=17)}} \\")
    latex_lines.append(r"Lipinski compliance & 100\% & Excellent \\")
    latex_lines.append(r"Veber compliance & 100\% & Excellent \\")
    latex_lines.append(r"Mean QED & 0.703 & Good \\")
    latex_lines.append(r"Mean logP & 2.84 & Favorable \\")
    latex_lines.append(r"Mean TPSA & \SI{66.3}{\angstrom\squared} & Good permeability \\")
    
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
    output_latex = base_dir / "manuscript/tables/sm_table_admet_summary.tex"
    
    # Create output directory if needed
    output_latex.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("V7 ADMET Summary Table Generation")
    print("=" * 70)
    
    print("\n[NOTE] Generating population-level ADMET summary")
    print("       Candidate-specific predictions not available")
    print("       Using P1 library statistics (n=810) as proxy")
    
    # Generate LaTeX table
    print(f"\n[1/1] Generating LaTeX table: {output_latex}")
    generate_latex_table(output_latex)
    
    # Summary
    print("\n" + "=" * 70)
    print("ADMET PROFILE SUMMARY")
    print("=" * 70)
    
    print("\n✓ Population-Level Statistics (P1 Library, n=810):")
    print("  - CYP450 inhibition: Low-to-moderate risk")
    print("    • CYP2C9: 26.1%")
    print("    • CYP2C19: 42.4%")
    print("    • CYP3A4: 42.6%")
    print("    • CYP2D6: 17.0%")
    
    print("\n✓ Safety Profile:")
    print("  - hERG cardiotoxicity risk: LOW (mean 11.7%, median 11.8%)")
    print("  - Selectivity index: 100% have SI > 10 (highly selective)")
    
    print("\n✓ Set-C Drug-Likeness (n=17, candidate-specific):")
    print("  - 100% Lipinski/Veber compliance")
    print("  - Mean QED: 0.703 (good drug-likeness)")
    print("  - Favorable physicochemical properties")
    
    print("\n" + "=" * 70)
    print("IMPORTANT NOTES")
    print("=" * 70)
    print("\n⚠️  This is a SUMMARY TABLE using population statistics")
    print("    Individual candidate predictions require:")
    print("    1. ADMET-AI (NumPy 2.x compatibility fix needed), OR")
    print("    2. Alternative ADMET prediction tools, OR")
    print("    3. Experimental ADMET profiling")
    
    print("\n✓ Scientifically defensible because:")
    print("  - Set-C selected from same chemical space as P1 library")
    print("  - All 17 candidates have excellent drug-likeness (100% compliance)")
    print("  - Population statistics provide reasonable proxy")
    print("  - Table clearly states limitations and source")
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE")
    print("=" * 70)
    print(f"\nOutput:")
    print(f"  - LaTeX: {output_latex}")
    print(f"\nNext step: Insert table into V7 SM as Section S6")
    print(f"          (or consider generating scaffold analysis first)")

if __name__ == "__main__":
    main()
