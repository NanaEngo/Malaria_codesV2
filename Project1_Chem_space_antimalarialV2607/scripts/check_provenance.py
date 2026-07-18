#!/usr/bin/env python3
"""
check_provenance.py — Validate that all Vina docking CSVs have provenance columns.

This is the validation gate (§3.1b criterion): 100% of rows in every
downstream CSV must have exhaustiveness and grid_version traced.

Usage:
    python scripts/check_provenance.py
    python scripts/check_provenance.py --verbose   # show first 3 rows of each file
    python scripts/check_provenance.py --strict    # exit 1 on any failure

Exit codes:
    0 = all pass
    1 = one or more failures (only with --strict)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(os.environ.get(
    "MALARIA_ROOT",
    "/home/nanaengo/Malaria_codesV2"
))

REQUIRED_COLS = ["exhaustiveness", "grid_version"]

FILES_TO_CHECK = [
    # P1 V2 corrected grid results
    ".archive_P1_V2607_20260717/results/r8b/fullcluster_rescoring/docking_results.csv",
    # P2 data files
    "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/docking/combined_docking_results.csv",
    "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/docking/docking_results_with_smiles.csv",
    # P2 mutant results
    "Project2_Polypharmacology_MD_ValidationV2607/results/mutant_docking/mutant_docking_results.csv",
    # Reconstructed centroid scores
    "Project1_Chem_space_antimalarialV2607/results/v2_centroid_scores.csv",
    # Clean filtered output
    "Project1_Chem_space_antimalarialV2607/results/docking_results_clean.csv",
]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def check_file(path: Path, strict: bool = False, verbose: bool = False) -> dict:
    """Check that a single CSV file has provenance columns."""
    result = {
        "file": str(path),
        "exists": path.exists(),
        "pass": False,
        "rows": 0,
        "missing_cols": [],
        "null_rows": 0,
        "exhaustiveness_values": [],
        "grid_version_values": [],
    }

    if not result["exists"]:
        result["pass"] = not strict  # non-strict: missing files are OK
        return result

    df = pd.read_csv(path)
    result["rows"] = len(df)

    # Check required columns exist
    for col in REQUIRED_COLS:
        if col not in df.columns:
            result["missing_cols"].append(col)

    if result["missing_cols"]:
        return result

    # Check for null values in provenance columns
    null_mask = df[REQUIRED_COLS].isnull().any(axis=1)
    result["null_rows"] = null_mask.sum()

    # Get unique values
    result["exhaustiveness_values"] = sorted(df["exhaustiveness"].dropna().unique().tolist())
    result["grid_version_values"] = sorted(df["grid_version"].dropna().unique().tolist())

    # Pass if no missing cols and no null rows
    result["pass"] = (len(result["missing_cols"]) == 0) and (result["null_rows"] == 0)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate provenance columns in all Vina docking CSVs."
    )
    parser.add_argument("--verbose", action="store_true", help="Show first 3 rows of each file")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any failure")
    args = parser.parse_args()

    log.info("═" * 60)
    log.info("Provenance Validation — §3.1b Gate Check")
    log.info("═" * 60)

    all_results = []
    for rel_path in FILES_TO_CHECK:
        abs_path = PROJECT_ROOT / rel_path
        result = check_file(abs_path, strict=args.strict, verbose=args.verbose)
        all_results.append(result)

        # Display
        if not result["exists"]:
            if args.strict:
                log.warning(f"  ⚠️  MISSING {rel_path}")
            else:
                log.info(f"  — Skipped (not found): {rel_path}")
            continue

        status = "✅" if result["pass"] else "❌"
        extras = []
        if result["missing_cols"]:
            extras.append(f"missing: {result['missing_cols']}")
        if result["null_rows"] > 0:
            extras.append(f"null_rows: {result['null_rows']}")
        if result["exhaustiveness_values"]:
            extras.append(f"EX={result['exhaustiveness_values']}")
        if result["grid_version_values"]:
            extras.append(f"GV={result['grid_version_values']}")

        extra_str = " | " + ", ".join(extras) if extras else ""
        log.info(f"  {status} {rel_path}: {result['rows']} rows{extra_str}")

        if args.verbose and result["exists"]:
            df = pd.read_csv(abs_path)
            log.info(f"      First 3 rows:")
            for _, row in df.head(3).iterrows():
                log.info(f"      {row.to_dict()}")

    # Summary
    n_pass = sum(1 for r in all_results if r["pass"])
    n_fail = sum(1 for r in all_results if not r["pass"] and r["exists"])
    n_missing = sum(1 for r in all_results if not r["exists"])

    log.info("\n" + "═" * 60)
    log.info(f"Summary: {n_pass} passed, {n_fail} failed, {n_missing} not found")
    log.info("═" * 60)

    if args.strict and n_fail > 0:
        log.warning("Strict mode: failures found.")
        sys.exit(1)

    log.info("Done.")


if __name__ == "__main__":
    main()
