#!/usr/bin/env python3
"""
Generate physicochemical properties table for V7 Set-C candidates (PP-01 to PP-17)

Calculates:
- MW (Molecular Weight)
- logP (Lipophilicity)
- HBD (H-Bond Donors)
- HBA (H-Bond Acceptors)
- TPSA (Topological Polar Surface Area)
- RB (Rotatable Bonds)
- QED (Quantitative Estimate of Drug-likeness)
- SA (Synthetic Accessibility)
- Lipinski violations

Outputs:
- CSV: results/derived/v7_physicochemical_properties.csv
- LaTeX: manuscript/tables/sm_table_physicochemical.tex
"""

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, Crippen, QED
from rdkit.Chem import rdMolDescriptors
import sys
from pathlib import Path

# Add path for SAScore if needed
sys.path.append(str(Path(__file__).parent))

def calculate_sa_score(mol):
    """
    Calculate Synthetic Accessibility Score
    Range: 1 (easy) to 10 (difficult)
    """
    try:
        # Try importing SAScore - may need separate installation
        from rdkit.Chem import RDConfig
        import os
        sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
        import sascorer
        return sascorer.calculateScore(mol)
    except:
        # Fallback: use simple complexity metric
        # Not ideal but provides rough estimate
        return None

def calculate_lipinski_violations(mol):
    """
    Calculate number of Lipinski Rule of 5 violations
    Rules:
    - MW <= 500
    - logP <= 5
    - HBD <= 5
    - HBA <= 10
    """
    violations = 0
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    
    if mw > 500:
        violations += 1
    if logp > 5:
        violations += 1
    if hbd > 5:
        violations += 1
    if hba > 10:
        violations += 1
    
    return violations

def calculate_properties(smiles):
    """
    Calculate all physicochemical properties for a SMILES string
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    props = {
        'MW': Descriptors.MolWt(mol),
        'logP': Crippen.MolLogP(mol),
        'HBD': Descriptors.NumHDonors(mol),
        'HBA': Descriptors.NumHAcceptors(mol),
        'TPSA': Descriptors.TPSA(mol),
        'RB': Descriptors.NumRotatableBonds(mol),
        'QED': QED.qed(mol),
        'SA': calculate_sa_score(mol),
        'Lipinski_violations': calculate_lipinski_violations(mol)
    }
    
    return props

def generate_latex_table(df, output_path):
    """
    Generate LaTeX table for supplementary material
    """
    latex_lines = []
    
    # Table header
    latex_lines.append(r"\begin{table}[h!]")
    latex_lines.append(r"\centering")
    latex_lines.append(r"\caption{Physicochemical properties of Set-C polypharmacology candidates (PP-01 to PP-17). MW: molecular weight (Da); logP: octanol-water partition coefficient; HBD: hydrogen bond donors; HBA: hydrogen bond acceptors; TPSA: topological polar surface area (\si{\angstrom\squared}); RB: rotatable bonds; QED: quantitative estimate of drug-likeness (0-1 scale); SA: synthetic accessibility (1 = easy to synthesize, 10 = difficult); Lipinski: number of Lipinski Rule of Five violations.}")
    latex_lines.append(r"\label{tab:physichem}")
    latex_lines.append(r"\small")
    latex_lines.append(r"\begin{tabular}{lcccccccccc}")
    latex_lines.append(r"\toprule")
    latex_lines.append(r"Candidate & MW & logP & HBD & HBA & TPSA & RB & fsp\textsuperscript{3} & QED & SA & Lipinski \\")
    latex_lines.append(r"\midrule")
    
    # Data rows
    for _, row in df.iterrows():
        cand = row['candidate_id']
        mw = f"{row['MW']:.1f}"
        logp = f"{row['logP']:.2f}"
        hbd = f"{row['HBD']:.0f}"
        hba = f"{row['HBA']:.0f}"
        tpsa = f"{row['TPSA']:.1f}"
        rb = f"{row['RB']:.0f}"
        fsp3 = f"{row['fsp3']:.2f}"
        qed = f"{row['QED']:.2f}"
        sa = f"{row['SA']:.1f}" if pd.notna(row['SA']) else "---"
        lipinski = f"{row['Lipinski_violations']:.0f}"
        
        latex_lines.append(f"{cand} & {mw} & {logp} & {hbd} & {hba} & {tpsa} & {rb} & {fsp3} & {qed} & {sa} & {lipinski} \\\\")
    
    # Summary statistics
    latex_lines.append(r"\midrule")
    mean_row = df[['MW', 'logP', 'HBD', 'HBA', 'TPSA', 'RB', 'fsp3', 'QED', 'SA', 'Lipinski_violations']].mean()
    latex_lines.append(f"Mean & {mean_row['MW']:.1f} & {mean_row['logP']:.2f} & {mean_row['HBD']:.1f} & {mean_row['HBA']:.1f} & {mean_row['TPSA']:.1f} & {mean_row['RB']:.1f} & {mean_row['fsp3']:.2f} & {mean_row['QED']:.2f} & {mean_row['SA']:.1f} & {mean_row['Lipinski_violations']:.1f} \\\\")
    
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
    input_csv = base_dir / "results/derived/v7_integrated_candidate_metrics.csv"
    output_csv = base_dir / "results/derived/v7_physicochemical_properties.csv"
    output_latex = base_dir / "manuscript/tables/sm_table_physicochemical.tex"
    
    # Create output directories if needed
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_latex.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("V7 Physicochemical Properties Generation")
    print("=" * 70)
    
    # Read input data
    print(f"\n[1/4] Reading input data: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"      Loaded {len(df)} candidates (PP-01 to PP-{len(df):02d})")
    
    # Calculate properties
    print(f"\n[2/4] Calculating physicochemical properties...")
    properties_list = []
    
    for idx, row in df.iterrows():
        cand_id = row['candidate_id']
        smiles = row['canonical_smiles']
        
        print(f"      Processing {cand_id}...", end=" ")
        props = calculate_properties(smiles)
        
        if props is None:
            print("ERROR: Invalid SMILES")
            continue
        
        # Add candidate ID and existing data
        props['candidate_id'] = cand_id
        props['canonical_smiles'] = smiles
        props['fsp3'] = row['fsp3']
        props['NPL'] = row['NPL']
        
        properties_list.append(props)
        print("✓")
    
    # Create output dataframe
    props_df = pd.DataFrame(properties_list)
    
    # Reorder columns
    column_order = ['candidate_id', 'canonical_smiles', 'MW', 'logP', 'HBD', 'HBA', 
                   'TPSA', 'RB', 'fsp3', 'NPL', 'QED', 'SA', 'Lipinski_violations']
    props_df = props_df[column_order]
    
    # Save CSV
    print(f"\n[3/4] Saving CSV: {output_csv}")
    props_df.to_csv(output_csv, index=False, float_format='%.4f')
    print(f"      ✓ Saved {len(props_df)} candidate properties")
    
    # Generate LaTeX table
    print(f"\n[4/4] Generating LaTeX table: {output_latex}")
    generate_latex_table(props_df, output_latex)
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"\nMolecular Weight (Da):")
    print(f"  Mean ± SD: {props_df['MW'].mean():.1f} ± {props_df['MW'].std():.1f}")
    print(f"  Range: {props_df['MW'].min():.1f} - {props_df['MW'].max():.1f}")
    
    print(f"\nlogP:")
    print(f"  Mean ± SD: {props_df['logP'].mean():.2f} ± {props_df['logP'].std():.2f}")
    print(f"  Range: {props_df['logP'].min():.2f} - {props_df['logP'].max():.2f}")
    
    print(f"\nTPSA (Ų):")
    print(f"  Mean ± SD: {props_df['TPSA'].mean():.1f} ± {props_df['TPSA'].std():.1f}")
    print(f"  Range: {props_df['TPSA'].min():.1f} - {props_df['TPSA'].max():.1f}")
    
    print(f"\nQED:")
    print(f"  Mean ± SD: {props_df['QED'].mean():.3f} ± {props_df['QED'].std():.3f}")
    print(f"  Range: {props_df['QED'].min():.3f} - {props_df['QED'].max():.3f}")
    
    print(f"\nLipinski Violations:")
    print(f"  Mean: {props_df['Lipinski_violations'].mean():.2f}")
    print(f"  0 violations: {(props_df['Lipinski_violations'] == 0).sum()}/{len(props_df)} candidates ({100*(props_df['Lipinski_violations'] == 0).sum()/len(props_df):.1f}%)")
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  - CSV: {output_csv}")
    print(f"  - LaTeX: {output_latex}")
    print(f"\nNext step: Insert LaTeX table into V7 SM")

if __name__ == "__main__":
    main()
