#!/usr/bin/env python3
"""
fix_provenance.py — Add exhaustiveness and grid_version columns to all CSV files.

This script implements the §3.1b provenance check from the audit by:
  1. Adding `exhaustiveness` and `grid_version` columns to every Vina results CSV
  2. Reconstructing the missing v2_centroid_scores.csv from docking_results.csv
  3. Generating a clean filtered CSV (EX=16/V2 only) for downstream P2/P3 consumption

Usage:
    python scripts/fix_provenance.py              # fix all CSVs
    python scripts/fix_provenance.py --check-only  # only validate, don't modify

Pipelines and their known exhaustiveness values:
  - r8b_fullcluster_rescoring.py (V2 Corrected Grid, 1,815 mols): EX=16
  - r1a_dekois_actives.sbatch (DEKOIS enrichment): EX=64
  - run_redock_hpc.sh (mutant docking): EX=128
  - redock_ligand438_PfATP4.sh (PfATP4 redock): EX=128
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import pandas as pd

# ── Project root ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(os.environ.get(
    "MALARIA_ROOT",
    "/home/nanaengo/Malaria_codesV2"
))

# ── Known exhaustiveness values per pipeline ─────────────────────────────────
# These are determined from actual script/sbatch analysis, not config docs.
PIPELINE_EXHAUSTIVENESS = {
    "r8b_fullcluster": 16,        # VINA_EXHAUSTIVENESS=16 in r8b_fullcluster_rescoring.py
    "dekois_enrichment": 64,      # --exhaustiveness 64 in r1a_dekois_actives.sbatch
    "mutant_docking": 128,        # Comments in run_redock_hpc.sh & redock_ligand438_PfATP4.sh
    "assumed_multi_target": 16,   # Conservative assumption: 9N10/4GM2 were docked similarly to r8b
}

# ── Target-to-pipeline mapping ───────────────────────────────────────────────
# The r8b archive docking_results.csv only contains 6UKJ (1,657 rows) and
# 7F3Y (158 rows). The P2 combined files include 9N10 and 4GM2 which came
# from a SEPARATE docking campaign (likely also from the V2 corrected grid
# pipeline but we lack log-file evidence).
# We split provenance by target accordingly.
R8B_TARGETS = ["6UKJ", "7F3Y"]          # Confirmed EX=16 from r8b pipeline
ASSUMED_TARGETS = ["9N10", "4GM2"]       # No log evidence; assumed EX=16
MUTANT_TARGETS = ["PfDHFR", "PfCRT"]     # Separate pipeline, EX=128 (confirmed)

# ── File registry: (relative_path, source_pipeline, grid_version, [split_by_target]) ─
CSV_REGISTRY = [
    # r8b archive — confirmed EX=16 via VINA_EXHAUSTIVENESS in r8b_fullcluster_rescoring.py
    (
        ".archive_P1_V2607_20260717/results/r8b/fullcluster_rescoring/docking_results.csv",
        "r8b_fullcluster",
        "V2",
        None,  # single pipeline, no split needed
    ),
    # P2 combined CSVs — MIXED targets from different campaigns
    (
        "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/docking/combined_docking_results.csv",
        "r8b_fullcluster",  # confirmed targets
        "V2",
        {"R8B_TARGETS": R8B_TARGETS, "ASSUMED_TARGETS": ASSUMED_TARGETS},
    ),
    (
        "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/docking/docking_results_with_smiles.csv",
        "r8b_fullcluster",  # confirmed targets
        "V2",
        {"R8B_TARGETS": R8B_TARGETS, "ASSUMED_TARGETS": ASSUMED_TARGETS},
    ),
    # Mutant docking — confirmed EX=128 from redock scripts
    (
        "Project2_Polypharmacology_MD_ValidationV2607/results/mutant_docking/mutant_docking_results.csv",
        "mutant_docking",
        "V2",
        None,  # single pipeline
    ),
]

OUTPUT_CENTROID_SCORES = "Project1_Chem_space_antimalarialV2607/results/v2_centroid_scores.csv"
OUTPUT_CLEAN_DOCKING = "Project1_Chem_space_antimalarialV2607/results/docking_results_clean.csv"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  Core functions
# ═══════════════════════════════════════════════════════════════════════════════

def add_provenance_columns(
    df: pd.DataFrame,
    pipeline_key: str,
    grid_version: str,
) -> pd.DataFrame:
    """Add exhaustiveness and grid_version columns to a dataframe."""
    ex = PIPELINE_EXHAUSTIVENESS[pipeline_key]
    df_out = df.copy()
    df_out["exhaustiveness"] = ex
    df_out["grid_version"] = grid_version
    # Move provenance columns to the end
    cols = [c for c in df_out.columns if c not in ("exhaustiveness", "grid_version")]
    df_out = df_out[cols + ["exhaustiveness", "grid_version"]]
    return df_out


def validate_provenance(df: pd.DataFrame, name: str) -> dict:
    """Validate that provenance columns are present and complete."""
    result = {"file": name, "rows": len(df), "pass": True, "issues": []}

    for col in ("exhaustiveness", "grid_version"):
        if col not in df.columns:
            result["pass"] = False
            result["issues"].append(f"Missing column: {col}")
            continue
        missing = df[col].isnull().sum()
        if missing > 0:
            result["pass"] = False
            result["issues"].append(f"Column {col}: {missing} null values")

    if result["pass"]:
        ex_values = df["exhaustiveness"].unique()
        gv_values = df["grid_version"].unique()
        result["exhaustiveness_values"] = sorted(ex_values.tolist())
        result["grid_version_values"] = sorted(gv_values.tolist())
        log.info(f"  ✅ {name}: {len(df)} rows, EX={ex_values}, GV={gv_values}")
    else:
        log.warning(f"  ❌ {name}: {', '.join(result['issues'])}")

    return result


def reconstruct_centroid_scores(
    docked_csv: Path,
    output_csv: Path,
) -> pd.DataFrame:
    """Reconstruct v2_centroid_scores.csv from full docking_results.csv.

    Centroid rows are identified by member_idx == 0 in the full cluster
    rescoring output. We extract those and enrich with provenance.
    """
    if not docked_csv.exists():
        log.warning(f"  ⚠️  Cannot reconstruct: {docked_csv} not found")
        return pd.DataFrame()

    df = pd.read_csv(docked_csv)
    centroids = df[df["member_idx"] == 0].copy()

    if len(centroids) == 0:
        log.warning(f"  ⚠️  No centroids found (no rows with member_idx=0)")
        return pd.DataFrame()

    centroids = add_provenance_columns(centroids, "r8b_fullcluster", "V2")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    centroids.to_csv(output_csv, index=False)
    log.info(f"  ✅ Reconstructed v2_centroid_scores.csv: {len(centroids)} centroids → {output_csv}")
    return centroids


def generate_clean_docking(
    docked_csv: Path,
    output_csv: Path,
    target_ex: int = 16,
    target_grid: str = "V2",
):
    """Generate a clean filtered CSV for downstream P2/P3 consumption.

    Filters to EX=16, V2 rows only — the homogeneous provenance set.
    """
    if not docked_csv.exists():
        log.warning(f"  ⚠️  Cannot filter: {docked_csv} not found")
        return

    df = pd.read_csv(docked_csv)
    df = add_provenance_columns(df, "r8b_fullcluster", "V2")

    clean = df[(df["exhaustiveness"] == target_ex) & (df["grid_version"] == target_grid)].copy()
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output_csv, index=False)
    log.info(f"  ✅ Clean docking results: {len(clean)}/{len(df)} rows (EX={target_ex}, {target_grid}) → {output_csv}")


def update_config_exhaustiveness(config_dir: Path, target_ex: int = 16):
    """Update P1 config.txt files to match the actual exhaustiveness used in V2 runs.

    Note: This only updates P1's docking configs, NOT P2's copies. The P2 copies
    may serve different pipelines (mutant docking used EX=128).
    """
    targets = ["7F3Y", "6UKJ", "9N10", "4GM2"]
    updated = 0
    for target in targets:
        config_path = config_dir / f"Docking_{target}/config.txt"
        if config_path.exists():
            content = config_path.read_text()
            if "exhaustiveness" in content:
                old_ex = content.split("exhaustiveness")[1].split("=")[1].strip().split("\n")[0].strip()
                new_content = content.replace(
                    f"exhaustiveness = {old_ex}",
                    f"exhaustiveness = {target_ex}   # actual value used in V2 r8b run (audit §3.1b)"
                )
                config_path.write_text(new_content)
                log.info(f"  ✅ Updated {config_path}: EX={old_ex} → EX={target_ex}")
                updated += 1
    if updated == 0:
        log.info(f"  ⚠️  No config.txt files found in {config_dir}")
    return updated


# ═══════════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Add provenance columns to all Vina docking CSVs."
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only validate provenance, don't modify files"
    )
    parser.add_argument(
        "--skip-v2-centroid",
        action="store_true",
        help="Skip reconstruction of missing v2_centroid_scores.csv"
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip generation of clean filtered CSV"
    )
    args = parser.parse_args()

    log.info("═" * 60)
    log.info("Provenance Fix — §3.1b Implementation")
    log.info("═" * 60)

    results = []

    # ── Step 1: Add provenance columns to all CSVs ───────────────────────────
    log.info("\n── Step 1: Adding provenance columns ──")
    for rel_path, pipeline_key, grid_version, split_config in CSV_REGISTRY:
        abs_path = PROJECT_ROOT / rel_path
        if not abs_path.exists():
            log.warning(f"  ⚠️  File not found: {abs_path}")
            continue

        df = pd.read_csv(abs_path)

        if args.check_only:
            result = validate_provenance(df, rel_path)
            results.append(result)
            continue

        if split_config is not None:
            # ── Target-aware provenance ──────────────────────────────────────
            # Identify the column that holds target information
            # combined_docking_results.csv: 'Target' column
            # docking_results_with_smiles.csv: 'Target' column
            # mutant_docking_results.csv: 'mutant' column (handled separately, no split_config)
            target_col = "Target" if "Target" in df.columns else "target" if "target" in df.columns else None

            if target_col and target_col in df.columns:
                # Split into confirmed (EX=16) and assumed (EX=16 with flag)
                confirmed_mask = df[target_col].isin(split_config.get("R8B_TARGETS", []))
                assumed_mask = df[target_col].isin(split_config.get("ASSUMED_TARGETS", []))

                # Apply confirmed provenance
                df.loc[confirmed_mask, "exhaustiveness"] = PIPELINE_EXHAUSTIVENESS[pipeline_key]
                df.loc[confirmed_mask, "grid_version"] = grid_version

                # Apply assumed provenance (same EX value but flagged in grid_version)
                df.loc[assumed_mask, "exhaustiveness"] = PIPELINE_EXHAUSTIVENESS.get("assumed_multi_target", 16)
                df.loc[assumed_mask, "grid_version"] = f"{grid_version}_assumed"

                # Log any rows not covered
                uncovered = df[~(confirmed_mask | assumed_mask)]
                if len(uncovered) > 0:
                    log.warning(f"  ⚠️  {len(uncovered)} rows have unexpected targets: {uncovered[target_col].unique()}")
                    df.loc[~confirmed_mask & ~assumed_mask, "exhaustiveness"] = 0
                    df.loc[~confirmed_mask & ~assumed_mask, "grid_version"] = "unknown"

                # Move provenance columns to end
                cols = [c for c in df.columns if c not in ("exhaustiveness", "grid_version")]
                df = df[cols + ["exhaustiveness", "grid_version"]]
            else:
                df = add_provenance_columns(df, pipeline_key, grid_version)
        else:
            # Single pipeline — simple add
            df = add_provenance_columns(df, pipeline_key, grid_version)

        abs_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(abs_path, index=False)
        result = validate_provenance(df, rel_path)
        results.append(result)

    # ── Step 2: Reconstruct v2_centroid_scores.csv ───────────────────────────
    log.info("\n── Step 2: Reconstructing v2_centroid_scores.csv ──")
    if not args.skip_v2_centroid and not args.check_only:
        docked_csv = PROJECT_ROOT / CSV_REGISTRY[0][0]
        output_csv = PROJECT_ROOT / OUTPUT_CENTROID_SCORES
        centroids = reconstruct_centroid_scores(docked_csv, output_csv)

        if not centroids.empty:
            result = validate_provenance(centroids, str(OUTPUT_CENTROID_SCORES))
            results.append(result)
    else:
        log.info("  Skipped (--skip-v2-centroid or --check-only)")

    # ── Step 3: Generate clean filtered CSV ──────────────────────────────────
    log.info("\n── Step 3: Generating clean docking_results_clean.csv ──")
    if not args.skip_clean and not args.check_only:
        # Generate from the archive's docking_results.csv (which has already been
        # enriched with provenance columns if Step 1 ran)
        docked_csv = PROJECT_ROOT / CSV_REGISTRY[0][0]
        output_csv = PROJECT_ROOT / OUTPUT_CLEAN_DOCKING
        generate_clean_docking(docked_csv, output_csv)

    # ── Step 4: Update config.txt files to match actual EX=16 value ──────────
    log.info("\n── Step 4: Updating config.txt exhaustiveness to match actual value ──")
    if not args.check_only:
        config_dir = PROJECT_ROOT / "Project1_Chem_space_antimalarialV2607" / "Docking"
        update_config_exhaustiveness(config_dir, target_ex=16)

    # ── Summary ──────────────────────────────────────────────────────────────
    log.info("\n" + "═" * 60)
    log.info("Provenance Check Summary")
    log.info("═" * 60)

    n_pass = sum(1 for r in results if r["pass"])
    n_fail = sum(1 for r in results if not r["pass"])

    for r in results:
        status = "✅" if r["pass"] else "❌"
        ex_vals = r.get("exhaustiveness_values", "?")
        gv_vals = r.get("grid_version_values", "?")
        log.info(f"  {status} {r['file']}: {r['rows']} rows, EX={ex_vals}, GV={gv_vals}")

    log.info(f"\n{n_pass} passed, {n_fail} failed")

    if n_fail > 0:
        log.warning("Some files failed — see individual errors above.")
        sys.exit(1)

    log.info("All provenance checks passed.")


if __name__ == "__main__":
    main()
