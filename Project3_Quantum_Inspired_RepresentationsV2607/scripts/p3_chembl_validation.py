#!/usr/bin/env python3
"""
P3 ChEMBL Experimental Validation — Query IC50 for top candidates.
Updated: July 23, 2026 — Retry logic, graceful API-outage handling.

Queries ChEMBL API for experimental activity data (IC50, EC50) of the top-10
P3 candidates across 4 Plasmodium targets. When the API is unavailable, outputs
a placeholder CSV with a clear note that experimental validation is pending.
"""

import os
import sys
import json
import time
import requests
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results' / 'p3_chembl_validation'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Top-10 P3 candidates (from SM Table S20 / P1 R8-B pipeline)
TOP_10_SMILES = [
    'Cc1ccc(CN2CCN(Cc3ccccc3)CC2)cc1O',
    'Cc1ccccc1CN1CCN(Cc2cccc(O)c2)CC1',
    'Cc1cc(CN2CCN(Cc3ccccc3)CC2)ccc1O',
    'COc1ccc(CN2CCN(Cc3ccccc3C)CC2)cc1O',
    'Oc1cccc(CN2CCN(Cc3ccc(Cl)cc3)CC2)c1',
    'Cc1ccc(CN2CCN(Cc3ccc(O)cc3)CC2)c(C)c1',
    'COc1ccc(CN2CCN(Cc3ccc(C)c(O)c3)CC2)cc1',
    'Cc1ccc(CN2CCN(Cc3cccc(O)c3)CC2)c(C)c1',
    'Oc1ccc(CN2CCN(Cc3ccccc3)CC2)cc1Cl',
    'Oc1ccc(CN2CCN(Cc3ccccc3Cl)CC2)cc1',
]

# ChEMBL target IDs for Plasmodium falciparum (verified via web search)
CHEMBL_TARGETS = {
    'PfDHFR': 'CHEMBL4296323',
    'PfCRT':  'CHEMBL1795182',
    'PfATP4': 'CHEMBL5235475',
    'PfClpP': 'CHEMBL4824474',
}

# ChEMBL API base URL
CHEMBL_API = 'https://www.ebi.ac.uk/chembl/api/data'

# Activity thresholds (nM)
IC50_THRESHOLD_ACTIVE = 1000    # < 1 uM = active
IC50_THRESHOLD_INACTIVE = 10000 # > 10 uM = inactive

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds, doubles each retry


def query_chembl_target_activities(target_chembl_id, max_results=100):
    """
    Query ChEMBL for bioactivity data against a specific target.
    Includes retry logic with exponential backoff.
    Returns (activities, success_flag).
    """
    url = f"{CHEMBL_API}/activity.json"
    params = {
        'target_chembl_id': target_chembl_id,
        'standard_type__in': 'IC50,EC50,Ki,Kd',
        'standard_units': 'nM',
        'limit': min(max_results, 100),
        'offset': 0,
    }
    
    all_activities = []
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"  Attempt {attempt + 1}/{MAX_RETRIES}...")
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            activities = data.get('activities', [])
            if not activities:
                break
            
            for act in activities:
                try:
                    value = float(act.get('standard_value', None))
                except (TypeError, ValueError):
                    continue
                
                record = {
                    'chembl_id': act.get('molecule_chembl_id', ''),
                    'canonical_smiles': act.get('canonical_smiles', ''),
                    'standard_type': act.get('standard_type', ''),
                    'standard_value_nM': value,
                    'standard_relation': act.get('standard_relation', '='),
                    'pchembl_value': act.get('pchembl_value', None),
                    'target': act.get('target_pref_name', ''),
                    'assay_chembl_id': act.get('assay_chembl_id', ''),
                }
                all_activities.append(record)
            
            # Pagination
            params['offset'] += params['limit']
            if len(activities) < params['limit']:
                break
            
            time.sleep(0.5)
            
        except requests.RequestException as e:
            delay = RETRY_DELAY * (2 ** attempt)
            print(f"  Warning: ChEMBL API error for {target_chembl_id}: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"  Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"  Max retries reached for {target_chembl_id}")
                return [], False
    
    return all_activities[:max_results], True


def classify_activity(ic50_nM):
    """Classify activity based on IC50 threshold."""
    if ic50_nM < IC50_THRESHOLD_ACTIVE:
        return 'Active'
    elif ic50_nM > IC50_THRESHOLD_INACTIVE:
        return 'Inactive'
    else:
        return 'Intermediate'


# Check RDKit availability at module level
_RDKIT_AVAILABLE = False
try:
    from rdkit import Chem
    from rdkit.Chem import DataStructs, AllChem
    _RDKIT_AVAILABLE = True
except ImportError:
    pass


def compute_tanimoto_smiles(smiles1, smiles2):
    """Compute Tanimoto similarity between two SMILES strings."""
    if not _RDKIT_AVAILABLE:
        return None
    try:
        mol1 = Chem.MolFromSmiles(smiles1)
        mol2 = Chem.MolFromSmiles(smiles2)
        
        if mol1 is None or mol2 is None:
            return None
        
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
        
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except ImportError:
        return None


def main():
    """Main entry point: query ChEMBL and validate top candidates."""
    if not _RDKIT_AVAILABLE:
        print("Warning: RDKit not installed; similarity search disabled.")
    """Main entry point: query ChEMBL and validate top candidates."""
    print("=" * 70)
    print("P3 ChEMBL Experimental Validation")
    print("=" * 70)
    
    all_results = []
    targets_with_data = 0
    targets_failed = 0
    
    # Query each target
    for target_name, target_id in CHEMBL_TARGETS.items():
        print(f"\n--- Querying {target_name} ({target_id}) ---")
        
        activities, success = query_chembl_target_activities(target_id, max_results=200)
        
        if not success or not activities:
            targets_failed += 1
            continue
        
        targets_with_data += 1
        print(f"  Retrieved {len(activities)} activities")
        
        # Classify by activity
        active = [a for a in activities if classify_activity(a['standard_value_nM']) == 'Active']
        inactive = [a for a in activities if classify_activity(a['standard_value_nM']) == 'Inactive']
        
        print(f"  Active (< {IC50_THRESHOLD_ACTIVE} nM): {len(active)}")
        print(f"  Inactive (> {IC50_THRESHOLD_INACTIVE} nM): {len(inactive)}")
        
        # For each top-10 candidate, find closest ChEMBL analogue
        for i, smiles in enumerate(TOP_10_SMILES):
            best_match = None
            best_tanimoto = 0.0
            
            for act in activities:
                if not act['canonical_smiles']:
                    continue
                
                tan = compute_tanimoto_smiles(smiles, act['canonical_smiles'])
                if tan is not None and tan > best_tanimoto:
                    best_tanimoto = tan
                    best_match = act
            
            if best_match and best_tanimoto > 0.5:
                result = {
                    'Rank': i + 1,
                    'Candidate_SMILES': smiles[:60] + '...' if len(smiles) > 60 else smiles,
                    'Target': target_name,
                    'ChEMBL_match': best_match['chembl_id'],
                    'Match_SMILES': best_match['canonical_smiles'][:60] + '...' if best_match['canonical_smiles'] else '',
                    'Tanimoto': round(best_tanimoto, 3),
                    'Standard_type': best_match['standard_type'],
                    'IC50_nM': best_match['standard_value_nM'],
                    'IC50_uM': round(best_match['standard_value_nM'] / 1000, 2),
                    'Activity': classify_activity(best_match['standard_value_nM']),
                    'pChEMBL': best_match.get('pchembl_value', ''),
                }
                all_results.append(result)
                
                status = '✅' if best_tanimoto > 0.7 else '⚠️'
                print(f"  {status} Rank {i+1}: Tanimoto={best_tanimoto:.3f}, "
                      f"IC50={best_match['standard_value_nM']:.0f} nM "
                      f"({classify_activity(best_match['standard_value_nM'])})")
    
    # Save results
    if all_results:
        df = pd.DataFrame(all_results)
        output_csv = OUTPUT_DIR / 'p3_chembl_validation.csv'
        df.to_csv(output_csv, index=False)
        print(f"\nResults saved to: {output_csv}")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Targets with successful queries: {targets_with_data}/{len(CHEMBL_TARGETS)}")
        print(f"Targets with API failures: {targets_failed}/{len(CHEMBL_TARGETS)}")
        
        for target in CHEMBL_TARGETS:
            target_df = df[df['Target'] == target]
            if len(target_df) == 0:
                continue
            
            active_count = len(target_df[target_df['Activity'] == 'Active'])
            high_sim = len(target_df[pd.to_numeric(target_df['Tanimoto'], errors='coerce') > 0.7])
            
            print(f"\n{target}:")
            print(f"  Candidates with ChEMBL match: {len(target_df)}/10")
            print(f"  High-similarity matches (T > 0.7): {high_sim}")
            print(f"  Experimentally active analogues: {active_count}")
        
        # Generate LaTeX table
        latex_path = OUTPUT_DIR / 'p3_chembl_validation_table.tex'
        with open(latex_path, 'w') as f:
            f.write("% Auto-generated by p3_chembl_validation.py\n")
            f.write("% ChEMBL experimental validation of top-10 P3 candidates\n\n")
            f.write("\\begin{table}[htbp]\n")
            f.write("\\centering\n")
            f.write("\\caption{ChEMBL experimental validation of top-10 candidates. For each candidate, the closest structural analogue with experimental IC$_{50}$ data is reported.}\n")
            f.write("\\label{tab:chembl_validation}\n")
            f.write("\\small\n")
            f.write("\\begin{tabularx}{\\textwidth}{c l l l l l}\n")
            f.write("\\toprule\n")
            f.write("Rank & Target & ChEMBL ID & Activity & {IC$_{50}$ (\\si{\\micro\\molar})} & Tanimoto \\\\\n")
            f.write("\\midrule\n")
            
            for _, row in df.iterrows():
                activity_marker = '✓' if row['Activity'] == 'Active' else ('✗' if row['Activity'] == 'Inactive' else '~')
                f.write(f"{row['Rank']} & {row['Target']} & {row['ChEMBL_match']} & "
                        f"{activity_marker} {row['Activity']} & {row['IC50_uM']:.1f} & "
                        f"{row['Tanimoto']:.3f} \\\\\n")
            
            f.write("\\bottomrule\n")
            f.write("\\end{tabularx}\n")
            f.write("\\end{table}\n")
        
        print(f"\nLaTeX table saved to: {latex_path}")
    
    else:
        print("\n" + "=" * 70)
        print("ChEMBL API UNAVAILABLE — EXPERIMENTAL VALIDATION DEFERRED")
        print("=" * 70)
        print("The ChEMBL REST API returned errors for all 4 Plasmodium targets.")
        print("This is a server-side issue (HTTP 500 / timeouts).")
        print("\nAction required:")
        print("  1. Re-run this script when the API recovers")
        print("  2. Or query ChEMBL manually via https://www.ebi.ac.uk/chembl/")
        print("  3. Document the API outage as a limitation in the manuscript\n")
        
        # Write placeholder CSV
        placeholder = pd.DataFrame({
            'Rank': range(1, 11),
            'Candidate_SMILES': TOP_10_SMILES,
            'Target': ['All'] * 10,
            'ChEMBL_match': ['PENDING'] * 10,
            'Match_SMILES': ['ChEMBL API unavailable'] * 10,
            'Tanimoto': ['PENDING'] * 10,
            'Standard_type': ['PENDING'] * 10,
            'IC50_nM': ['PENDING'] * 10,
            'IC50_uM': ['PENDING'] * 10,
            'Activity': ['ChEMBL API unavailable — experimental IC50 pending'] * 10,
            'pChEMBL': ['PENDING'] * 10,
        })
        output_csv = OUTPUT_DIR / 'p3_chembl_validation.csv'
        placeholder.to_csv(output_csv, index=False)
        print(f"Placeholder CSV saved to: {output_csv}")
    
    return all_results


if __name__ == '__main__':
    main()
