#!/usr/bin/env python3
"""Merge uniform + fix results into a complete 484-centroid dataset."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P2 = ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
SMILES_FILE = P2 / "data/from_project1/data/cluster_representatives_smiles.csv"

UNIFORM_DIR = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_uniform_seed20260809"
FIX_DIR = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_fix_seed20260809"
MERGED_DIR = ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid/results/pfclpp_2f6i_484_merged_seed20260809"

# Unfixable centroids (embed failures + tiny molecules that can't reach triad)
UNFIXABLE = {30, 43, 70, 99, 136, 145, 167, 170, 194, 195, 228, 340, 361, 390, 416}


def main():
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read SMILES
    with SMILES_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    smiles = [r["SMILES"].strip() for r in rows]
    
    passed = 0
    failed_unfixable = 0
    failed_other = 0
    
    for i in range(484):
        merged_out = MERGED_DIR / f"centroid_{i:04d}"
        
        # Check if already merged
        if (merged_out / "result.json").exists():
            passed += 1
            continue
        
        # Priority: fix results > uniform results
        fix_result = FIX_DIR / f"centroid_{i:04d}" / "result.json"
        uniform_result = UNIFORM_DIR / f"centroid_{i:04d}" / "result.json"
        
        merged_out.mkdir(parents=True, exist_ok=True)
        
        if fix_result.exists():
            # Use fix result
            shutil.copytree(FIX_DIR / f"centroid_{i:04d}", merged_out, dirs_exist_ok=True)
            passed += 1
        elif uniform_result.exists():
            # Use uniform result
            shutil.copytree(UNIFORM_DIR / f"centroid_{i:04d}", merged_out, dirs_exist_ok=True)
            passed += 1
        elif i in UNFIXABLE:
            # Known unfixable
            merged_out.mkdir(parents=True, exist_ok=True)
            failed_unfixable += 1
            (merged_out / "failure.json").write_text(json.dumps({
                "schema": "p1-v4-clpp-2f6i-merged/v1",
                "status": "UNFIXABLE",
                "message": f"Centroid {i} is unfixable (exotic structure or too small for triad contact)",
                "centroid_id": i,
                "smiles": smiles[i],
            }, indent=2) + "\n")
        else:
            # Unexpected failure
            merged_out.mkdir(parents=True, exist_ok=True)
            failed_other += 1
            (merged_out / "failure.json").write_text(json.dumps({
                "schema": "p1-v4-clpp-2f6i-merged/v1",
                "status": "UNEXPECTED_FAILURE",
                "message": f"Centroid {i} has no valid result",
                "centroid_id": i,
                "smiles": smiles[i],
            }, indent=2) + "\n")
    
    print(f"=== Merge complete ===")
    print(f"Total centroids: 484")
    print(f"Passed: {passed}")
    print(f"Unfixable (exotic/tiny): {failed_unfixable}")
    print(f"Other failures: {failed_other}")
    print(f"Pass rate: {passed}/484 ({100*passed/484:.1f}%)")


if __name__ == "__main__":
    main()
