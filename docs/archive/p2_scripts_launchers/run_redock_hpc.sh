#!/bin/bash
# ==============================================================================
# run_redock_hpc.sh — Re-dock Ligand 438 → PfATP4 (9N10) on HPC
#
# Purpose: Resolve +473 kcal/mol clash by exhaustive re-docking
# Method: Vina exhaustiveness=128 (20 modes) → Gnina CNN rescoring
#
# Usage:
#   ssh nanaengo@100.73.21.40
#   source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
#   conda activate malaria_md
#   nohup bash /path/to/run_redock_hpc.sh > ~/redock_438.log 2>&1 &
#
# Or via sbatch:
#   sbatch run_redock_hpc.sh
# ==============================================================================

#SBATCH --job-name=redock_438
#SBATCH --output=redock_438_%j.out
#SBATCH --error=redock_438_%j.err
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=8

set -euo pipefail

# ===== Configuration =====
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607"
RESULTS_DIR="$PROJECT_DIR/results/redock_438"
RECEPTOR="$PROJECT_DIR/data/proteins/9N10.pdbqt"
LIGAND_SMILES="COc1cc(SC)ccc1C(=O)N1CCC(C)(O)CC1"

# Docking box (ATP binding site of PfATP4)
CENTER_X=134.84
CENTER_Y=133.10
CENTER_Z=97.63
SIZE_X=25
SIZE_Y=25
SIZE_Z=25

mkdir -p "$RESULTS_DIR"

# ===== Environment Setup =====
echo "=============================================="
echo "  Re-dock Ligand 438 → PfATP4 (9N10)"
echo "  Date: $(date)"
echo "  Host: $(hostname)"
echo "=============================================="
echo ""

# Source conda (if not already in sbatch context)
if [ -z "${CONDA_DEFAULT_ENV:-}" ] || [ "$CONDA_DEFAULT_ENV" != "malaria_md" ]; then
    if [ -f /home/nanaengo/miniforge3/etc/profile.d/conda.sh ]; then
        source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
        conda activate malaria_md
    fi
fi
echo "  Conda env: ${CONDA_DEFAULT_ENV:-NONE}"
echo "  Python:    $(which python)"
echo ""

# Set LD_LIBRARY_PATH for Gnina (cuDNN in conda lib)
export LD_LIBRARY_PATH="/home/nanaengo/miniforge3/envs/malaria_md/lib:${LD_LIBRARY_PATH:-}"

# ===== Check Tools =====
echo "--- Checking Tools ---"
for tool in obabel vina; do
    if command -v "$tool" &>/dev/null; then
        echo "  ✅ $tool: $(which $tool)"
    else
        echo "  ❌ $tool: NOT FOUND"
        exit 1
    fi
done

GNINA_BIN="$HOME/gnina/gnina"
if [ -f "$GNINA_BIN" ]; then
    echo "  ✅ gnina: $GNINA_BIN ($($GNINA_BIN --version 2>&1))"
else
    echo "  ⚠️  gnina: NOT FOUND — CNN rescoring skipped"
    GNINA_BIN=""
fi

# Check receptor
if [ ! -f "$RECEPTOR" ]; then
    echo "  ❌ Receptor PDBQT not found: $RECEPTOR"
    exit 1
fi
echo "  ✅ Receptor: $RECEPTOR"
echo ""

# ===== Step 1: SMILES → PDBQT =====
echo "=============================================="
echo "  Step 1: SMILES → PDBQT"
echo "=============================================="
LIGAND_PDBQT="$RESULTS_DIR/ligand_438.pdbqt"
if [ ! -f "$LIGAND_PDBQT" ]; then
    echo "  Converting: $LIGAND_SMILES"
    obabel -:"$LIGAND_SMILES" -opdbqt --gen3d -h --log \
        -O "$LIGAND_PDBQT" 2>&1
    echo "  ✅ PDBQT created: $(wc -l < "$LIGAND_PDBQT") lines"
else
    echo "  ✅ PDBQT already exists: $LIGAND_PDBQT"
fi

# Verify PDBQT validity
if grep -q "ROOT" "$LIGAND_PDBQT" 2>/dev/null; then
    echo "  ✅ PDBQT format valid (ROOT found)"
else
    echo "  ❌ PDBQT invalid (no ROOT)"
    exit 1
fi

# Count torsions
NUM_TORS=$(grep -c "BRANCH" "$LIGAND_PDBQT" 2>/dev/null || echo 0)
echo "  Torsions: $NUM_TORS active rotatable bonds"
echo ""

# ===== Step 2: Convert receptor to PDBQT? =====
# (9N10.pdbqt should already exist from prior docking)
echo "  Receptor PDBQT size: $(du -h "$RECEPTOR" | cut -f1)"
echo ""

# ===== Step 3: Vina Docking (exhaustiveness=128) =====
echo "=============================================="
echo "  Step 2: Vina Docking (exhaustiveness=128)"
echo "=============================================="
VINA_OUT="$RESULTS_DIR/ligand_438_vina_out.pdbqt"
VINA_LOG="$RESULTS_DIR/ligand_438_vina.log"

if [ ! -f "$VINA_OUT" ]; then
    echo "  Running Vina..."
    echo "  Box: center=[$CENTER_X, $CENTER_Y, $CENTER_Z] size=[$SIZE_X, $SIZE_Y, $SIZE_Z]"
    echo "  CPUs: 8 | Exhaustiveness: 128 | Modes: 20"
    echo "  Started: $(date)"
    
    # Vina 1.2.7 outputs log to stdout (no --log flag)
    vina \
        --receptor "$RECEPTOR" \
        --ligand "$LIGAND_PDBQT" \
        --out "$VINA_OUT" \
        --center_x $CENTER_X --center_y $CENTER_Y --center_z $CENTER_Z \
        --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z \
        --exhaustiveness 128 \
        --num_modes 20 \
        --cpu 8 \
        > "$VINA_LOG" 2>&1
    
    echo "  Finished: $(date)"
    echo "  ✅ Vina docking complete"
else
    echo "  ✅ Vina output already exists: $VINA_OUT"
fi
echo ""

# ===== Step 4: Parse Vina Results =====
echo "=============================================="
echo "  Step 3: Vina Results Analysis"
echo "=============================================="
if [ -f "$VINA_LOG" ]; then
    echo "  Top 10 modes (kcal/mol):"
    grep -E "^[[:space:]]*[0-9]+[[:space:]]+" "$VINA_LOG" | head -10
    echo ""
    
    # Extract best score
    BEST_MODE=$(grep -E "^[[:space:]]*1[[:space:]]+" "$VINA_LOG" | awk '"\$1" == 1 {print}' | head -1)
    BEST_SCORE=$(echo "$BEST_MODE" | awk '{print $2}')
    echo "  Best pose: mode 1 → $BEST_SCORE kcal/mol"
    echo "  Old score (exh=64): -5.73 kcal/mol"
    echo "  Old MM-GBSA: +473.0 kcal/mol (CLASH)"
    
    # Compare with old score
    if [ -n "$BEST_SCORE" ]; then
        IMPROVED=$(echo "$BEST_SCORE < -5.73" | bc -l 2>/dev/null || echo "0")
        if [ "$IMPROVED" = "1" ]; then
            DIFF=$(echo "scale=2; -5.73 - $BEST_SCORE" | bc)
            echo "  ✅ IMPROVED by $DIFF kcal/mol vs old Vina score"
        else
            echo "  ⚠️  NOT improved vs old Vina score (-5.73)"
        fi
        
        GOOD_DOCK=$(echo "$BEST_SCORE < -6.0" | bc -l 2>/dev/null || echo "0")
        if [ "$GOOD_DOCK" = "1" ]; then
            echo "  ✅ Score < -6.0: classified as GOOD binding"
        else
            echo "  ⚠️  Score >= -6.0: still marginal binding"
        fi
    fi
else
    echo "  ⚠️  Vina log not found"
fi
echo ""

# ===== Step 5: Gnina CNN Rescoring =====
echo "=============================================="
echo "  Step 4: Gnina CNN Rescoring"
echo "=============================================="
if [ -n "$GNINA_BIN" ] && [ -f "$VINA_OUT" ]; then
    GNINA_OUT="$RESULTS_DIR/ligand_438_gnina_out.pdbqt"
    GNINA_LOG="$RESULTS_DIR/ligand_438_gnina.log"
    
    if [ ! -f "$GNINA_OUT" ]; then
        echo "  Running Gnina CNN rescoring..."
        echo "  Started: $(date)"
        
        # Gnina v1.3.2 uses CNN scoring by default (ensemble loaded automatically).
    # No --cnn_scoring flag needed — it's the default scoring mode.
    $GNINA_BIN \
            --receptor "$RECEPTOR" \
            --ligand "$VINA_OUT" \
            --out "$GNINA_OUT" \
            --center_x $CENTER_X --center_y $CENTER_Y --center_z $CENTER_Z \
            --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z \
            --exhaustiveness 128 \
            --num_modes 20 \
            --log "$GNINA_LOG" 2>&1
        
        echo "  Finished: $(date)"
        echo "  ✅ Gnina rescoring complete"
    else
        echo "  ✅ Gnina output already exists: $GNINA_OUT"
    fi
    
    # Parse Gnina results
    echo ""
    echo "--- Gnina CNN Scores ---"
    if [ -f "$GNINA_LOG" ]; then
        # Extract CNN scores (different format from Vina)
        echo "  Raw Gnina log lines:"
        grep -E "(CNN|affinity|score)" "$GNINA_LOG" | head -10 || echo "  (no CNN score lines found)"
        echo ""
        echo "  Full Gnina results:" 
        grep -E "^[[:space:]]*[0-9]+[[:space:]]+" "$GNINA_LOG" | head -10 || echo "  (no mode lines)"
    else
        echo "  ⚠️  Gnina log not found"
    fi
else
    echo "  ⚠️  Gnina not available — rescoring skipped"
fi
echo ""

# ===== Summary =====
echo "=============================================="
echo "  REDOCKING COMPLETE"
echo "=============================================="
echo "  Results: $RESULTS_DIR/"
echo "  Vina best: $BEST_SCORE kcal/mol (OLD: -5.73)"
if [ -f "$GNINA_OUT" ]; then
    echo "  Gnina: ✅ rescoring done"
    echo "  Gnina output: $GNINA_OUT"
fi
echo ""
echo "  Files:"
ls -lh "$RESULTS_DIR/" 2>/dev/null
echo ""
echo "  Next steps (after verifying):"
echo "    1. Extract best pose from $VINA_OUT"
echo "    2. obabel best_pose.pdbqt -O best_pose.pdb"
echo "    3. Rebuild complex: md_build_complexes.py"
echo "    4. Re-run MM-GBSA: run_mmgbsa_438_singchain.sh"
echo "=============================================="

# Save a summary text file
SUMMARY_FILE="$RESULTS_DIR/redock_summary.txt"
{
    echo "Redocking Summary — Ligand 438 → PfATP4 (9N10)"
    echo "Date: $(date)"
    echo "Host: $(hostname)"
    echo ""
    echo "Old score: -5.73 kcal/mol (exhaustiveness=64)"
    echo "Old MM-GBSA: +473.0 ± 1.54 kcal/mol (CLASH)"
    echo ""
    echo "New best Vina score: ${BEST_SCORE:-N/A} kcal/mol (exhaustiveness=128)"
    echo "Gnina rescoring: $([ -f "$GNINA_OUT" ] && echo "Done" || echo "Skipped/N/A")"
} > "$SUMMARY_FILE"
echo "  Summary saved: $SUMMARY_FILE"
echo ""
echo "=============================================="
