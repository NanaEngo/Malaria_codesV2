#!/usr/bin/env python3
"""Expand ChEMBL validation to 77 RRS compounds (3 targets, 231 pairs)."""

import sys
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'Project3_Quantum_Inspired_RepresentationsV2607' / 'results'

RRS_INPUT = RESULTS_DIR / 'p3_rrs_tfp_final.csv'
OUTPUT_CSV = RESULTS_DIR / 'p3_chembl_expanded.csv'

CHEMBL_TARGETS = {
    'PfDHFR': 'CHEMBL4296323',
    'PfCRT': 'CHEMBL1795182',
    'PfATP4': 'CHEMBL6066156',
}
CHEMBL_API = 'https://www.ebi.ac.uk/chembl/api/data'

try:
    from rdkit import Chem
    from rdkit.Chem import DataStructs, AllChem
    _HAS_RDKIT = True
except ImportError:
    _HAS_RDKIT = False

def compute_tanimoto(smi1, smi2):
    if not _HAS_RDKIT:
        return None
    try:
        m1 = Chem.MolFromSmiles(smi1)
        m2 = Chem.MolFromSmiles(smi2)
        if m1 is None or m2 is None:
            return None
        fp1 = AllChem.GetMorganFingerprintAsBitVect(m1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(m2, 2, nBits=2048)
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except Exception:
        return None

def query_target(target_id, max_results=200):
    """Query ChEMBL activities for a target (with retries)."""
    url = f"{CHEMBL_API}/activity.json"
    params = {
        'target_chembl_id': target_id,
        'standard_type__in': 'IC50,EC50,Ki,Kd',
        'standard_units': 'nM',
        'limit': min(max_results, 100),
    }
    activities = []
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            for act in data.get('activities', []):
                try:
                    val = float(act.get('standard_value', None))
                except (TypeError, ValueError):
                    continue
                activities.append({
                    'chembl_id': act.get('molecule_chembl_id', ''),
                    'smiles': act.get('canonical_smiles', ''),
                    'type': act.get('standard_type', ''),
                    'value_nM': val,
                    'pchembl': act.get('pchembl_value', None),
                })
            break
        except Exception as e:
            if attempt == 2:
                print(f"  FAILED after 3 attempts: {e}")
            else:
                time.sleep(2 * (2 ** attempt))
    return activities

def main():
    print("=" * 60)
    print("P3 ChEMBL Expanded Validation (77 RRS compounds)")
    print("=" * 60)

    # Load 77 RRS compounds
    df = pd.read_csv(RRS_INPUT)
    valid = df.dropna(subset=['rrs_score'])
    smiles_col = 'smiles' if 'smiles' in valid.columns else ('smile' if 'smile' in valid.columns else None)
    if smiles_col is None:
        print("ERROR: No SMILES column found")
        sys.exit(1)

    smiles_list = valid[smiles_col].tolist()
    print(f"Loaded {len(smiles_list)} compounds with valid RRS")

    # Query each target
    all_activities = {}
    for tname, tid in CHEMBL_TARGETS.items():
        print(f"\nQuerying {tname} ({tid})...")
        acts = query_target(tid)
        all_activities[tname] = acts
        print(f"  Retrieved {len(acts)} activities")

    # For each compound, find closest ChEMBL match per target
    results = []
    for idx, smi in enumerate(smiles_list):
        if idx % 10 == 0:
            print(f"  Processing compound {idx+1}/{len(smiles_list)}...")

        for tname, acts in all_activities.items():
            best_tan = 0.0
            best_act = None
            for act in acts:
                if not act['smiles']:
                    continue
                tan = compute_tanimoto(smi, act['smiles'])
                if tan is not None and tan > best_tan:
                    best_tan = tan
                    best_act = act

            if best_act and best_tan > 0.25:
                results.append({
                    'compound_idx': idx,
                    'target': tname,
                    'chembl_id': best_act['chembl_id'],
                    'tanimoto': round(best_tan, 3),
                    'ic50_nM': best_act['value_nM'],
                    'ic50_uM': round(best_act['value_nM'] / 1000, 2),
                    'activity': 'Active' if best_act['value_nM'] < 1000 else ('Inactive' if best_act['value_nM'] > 10000 else 'Intermediate'),
                })

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False)
    n_matches = len(results_df)
    n_pairs = len(smiles_list) * len(CHEMBL_TARGETS)
    print(f"\nCompleted: {n_matches} matches found out of {n_pairs} candidate-target pairs")

    if n_matches > 0:
        high_tan = len(results_df[results_df['tanimoto'] > 0.3])
        active_matches = len(results_df[results_df['activity'] == 'Active'])
        print(f"  High-similarity (T>0.3): {high_tan}")
        print(f"  Active matches: {active_matches}")
    print(f"\nSaved: {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
