#!/bin/bash
# MD Simulation: Complete Pipeline (Setup → Simulate → Analyse)
# Usage: bash scripts/md_full_pipeline.sh [--dry-run] [--yes]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"

DRY_RUN=""
YES_FLAG=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN="yes"
            ;;
        --yes)
            YES_FLAG="yes"
            ;;
    esac
done

echo "============================================================"
echo "MD Simulation: Complete Pipeline"
echo "============================================================"
echo ""
echo "This script will:"
echo "  0a. Select top 20 MD candidates (MPO/SYBA/SI filters)"
echo "  0b. Build resistance mutant structures (SWISS-MODEL / PyMOL)"
echo "  1.  Prepare protein structures"
echo "  2.  Generate ligand topologies (CGenFF / GAFF2 fallback)"
echo "  3.  Build solvated complexes (automated + ion addition)"
echo "  4.  Run energy minimisation"
echo "  5.  Run NVT equilibration (100 ps)"
echo "  6.  Run NPT equilibration (500 ps)"
echo "  7.  Run production MD (100 ns × 3 replicates)"
echo "  8.  Analyse trajectories"
echo "  9.  Calculate RRS / ACSI / PNS (Paper 2 metrics)"
echo ""
echo "Estimated wall time: 3-4 weeks on single GPU"
echo "Disk space required: 50-100 GB"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
MISSING_DEPS=0

if ! command -v gmx &> /dev/null; then
    echo "  ✗ GROMACS not found (gmx command)"
    MISSING_DEPS=1
else
    echo "  ✓ GROMACS found: $(gmx --version 2>&1 | head -1)"
fi

if ! command -v python3 &> /dev/null; then
    echo "  ✗ Python3 not found"
    MISSING_DEPS=1
else
    echo "  ✓ Python3 found: $(python3 --version)"
fi

if ! command -v obabel &> /dev/null; then
    echo "  ✗ Open Babel not found (needed for CGenFF MOL2 conversion)"
    MISSING_DEPS=1
else
    echo "  ✓ Open Babel found: $(obabel --version 2>&1 | head -1)"
fi

if [ "$DRY_RUN" = "yes" ]; then
    echo ""
    echo "[DRY RUN] Showing commands without execution..."
    echo ""
    echo "Step 0a: Select top 20 candidates"
    echo "  python3 scripts/md_select_top20.py"
    echo ""
    echo "Step 0b: Build resistance mutant structures"
    echo "  python3 scripts/md_homology_mutants.py [--method swissmodel|pymol]"
    echo ""
    echo "Step 1: Prepare proteins"
    echo "  python3 scripts/md_prepare_proteins.py"
    echo ""
    echo "Step 2: Prepare ligands (CGenFF / GAFF2 fallback)"
    echo "  python3 scripts/md_prepare_ligands.py"
    echo ""
    echo "Step 3: Build complexes"
    echo "  python3 scripts/md_build_complexes.py"
    echo ""
    echo "Step 4: Minimisation"
    echo "  bash scripts/md_run_minimisation.sh"
    echo ""
    echo "Step 5: NVT equilibration (300 K)"
    echo "  bash scripts/md_run_nvt.sh"
    echo ""
    echo "Step 6: NPT equilibration (300 K)"
    echo "  bash scripts/md_run_npt.sh"
    echo ""
    echo "Step 7: Production MD (100 ns × 3 replicates)"
    echo "  bash scripts/md_run_production.sh"
    echo ""
    echo "Step 8: Trajectory analysis"
    echo "  python3 scripts/md_analyse_trajectories.py"
    echo ""
    echo "Step 9: RRS / ACSI / PNS metrics"
    echo "  python3 scripts/md_calculate_rrs_acsi_pns.py"
    echo ""
    echo "[DRY RUN] Complete!"
    exit 0
fi

if [ "$MISSING_DEPS" -eq 1 ]; then
    echo ""
    echo "ERROR: Missing dependencies. Install the MD environment:"
    echo "  conda env create -f environment_md.yml"
    echo "  conda activate malaria_md"
    exit 1
fi

echo ""

# Confirm before proceeding
if [ "$YES_FLAG" != "yes" ]; then
    read -p "Proceed with MD simulation pipeline? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo ""
echo "Starting MD simulation pipeline..."
echo ""

# Step 0a: Select top 20 candidates
echo "Step 0a: Selecting top 20 MD candidates..."
python3 "${PROJECT_DIR}/scripts/md_select_top20.py" || { echo "Step 0a failed"; exit 1; }

# Step 0a-ii: MPO sensitivity analysis (roadmap Step 2 / R2)
echo "Step 0a-ii: MPO weight sensitivity analysis..."
python3 "${PROJECT_DIR}/scripts/md_select_top20.py" --sensitivity || {
    echo "  Warning: MPO sensitivity analysis failed — continuing"
}
echo ""

# Step 0b: Homology modelling of resistance mutants
echo "Step 0b: Building resistance mutant structures..."
python3 "${PROJECT_DIR}/scripts/md_homology_mutants.py" || {
    echo "  Warning: Homology modelling incomplete — check data/proteins/mutants/"
    echo "  Continuing pipeline with available structures..."
}
echo ""

# Step 1: Prepare proteins
echo "Step 1/9: Preparing protein structures..."
python3 "${PROJECT_DIR}/scripts/md_prepare_proteins.py" || { echo "Step 1 failed"; exit 1; }
echo ""

# Step 2: Prepare ligands
echo "Step 2/9: Generating ligand topologies (CGenFF / GAFF2 fallback)..."
python3 "${PROJECT_DIR}/scripts/md_prepare_ligands.py" || { echo "Step 2 failed"; exit 1; }
echo ""

# Step 3: Build complexes (fully automated with ion addition)
echo "Step 3/9: Building complexes..."
python3 "${PROJECT_DIR}/scripts/md_build_complexes.py" --ligand-dir "${PROJECT_DIR}/MD_systems" || { echo "Step 3 failed"; exit 1; }
echo ""

# Discover complexes dynamically from MD_systems/ rather than hardcoding
COMPLEXES=()
for d in "${MD_DIR}"/*/; do
    [ -d "$d" ] && COMPLEXES+=("$(basename "$d")")
done

echo ""

# Verify solvated files exist for all discovered complexes
MISSING_SOLVATED=0
for complex in "${COMPLEXES[@]}"; do
    if [ ! -f "${MD_DIR}/${complex}/ions.gro" ] && \
       [ ! -f "${MD_DIR}/${complex}/solvated.gro" ]; then
        echo "  ERROR: Missing solvated/ions file for ${complex}"
        MISSING_SOLVATED=1
    fi
done

if [ "$MISSING_SOLVATED" -eq 1 ]; then
    echo ""
    echo "ERROR: Some complexes are missing solvated systems."
    echo "Please complete the ion addition step before proceeding."
    exit 1
fi

# Step 4: Minimisation
echo "Step 4/9: Running energy minimisation..."
bash "${PROJECT_DIR}/scripts/md_run_minimisation.sh" || { echo "Step 4 failed"; exit 1; }
echo ""

# Step 5: NVT equilibration
echo "Step 5/9: Running NVT equilibration (300 K)..."
bash "${PROJECT_DIR}/scripts/md_run_nvt.sh" || { echo "Step 5 failed"; exit 1; }
echo ""

# Step 6: NPT equilibration
echo "Step 6/9: Running NPT equilibration (300 K)..."
bash "${PROJECT_DIR}/scripts/md_run_npt.sh" || { echo "Step 6 failed"; exit 1; }
echo ""

# Step 7: Production MD
echo "Step 7/9: Running production MD (100 ns × 3 replicates)..."
echo "  This will take 3-4 weeks. Progress logged to MD_systems/*/replicate_*/production.log"
bash "${PROJECT_DIR}/scripts/md_run_production.sh" || { echo "Step 7 failed"; exit 1; }
echo ""

# Step 8: Trajectory analysis
echo "Step 8/9: Analysing trajectories..."
python3 "${PROJECT_DIR}/scripts/md_analyse_trajectories.py" || { echo "Step 8 failed"; exit 1; }
echo ""

# Step 9: Paper 2 metrics
echo "Step 9/9: Calculating RRS / ACSI / PNS..."
python3 "${PROJECT_DIR}/scripts/md_calculate_rrs_acsi_pns.py" || {
    echo "  Warning: Metrics calculation incomplete (docking_mutants.csv may not exist yet)"
    echo "  Re-run after completing mutant docking: python3 scripts/md_calculate_rrs_acsi_pns.py"
}
echo ""

echo "============================================================"
echo "MD Simulation Pipeline Complete!"
echo "============================================================"
echo ""
echo "Results saved to: ${PROJECT_DIR}/results/md_results/"
echo "Paper 2 metrics : ${PROJECT_DIR}/results/c_rrs_classification.csv"
echo "                  ${PROJECT_DIR}/results/c_acsi_scores.csv"
echo "                  ${PROJECT_DIR}/results/c_pns_ranking.csv"
echo "============================================================"
