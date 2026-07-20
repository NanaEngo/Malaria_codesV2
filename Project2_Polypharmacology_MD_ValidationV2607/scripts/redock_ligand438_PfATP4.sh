#!/bin/bash
# ==============================================================================
# Re-dock Ligand 438 against PfATP4 (9N10)
# 
# Purpose: Resolve the +473 kcal/mol clash by exhaustive re-docking
# Why: Original Vina -5.73 kcal/mol produced a clashing MD pose
# Method: Vina exhaustiveness=128 (vs original 64), 20 output modes
# Rescoring: Gnina CNN (after HPC installation)
#
# Usage:
#   ./redock_ligand438_PfATP4.sh                    # run locally
#   sbatch redock_ligand438_PfATP4.sh               # run on HPC (SLURM)
#   bash redock_ligand438_PfATP4.sh --install-gnina  # install Gnina first
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$PROJECT_DIR/results/redock_438"
mkdir -p "$RESULTS_DIR"

# Check prerequisites
command -v obabel &>/dev/null || { echo "ERROR: obabel required (apt install openbabel or conda install -c conda-forge openbabel)"; exit 1; }
command -v bc &>/dev/null || { echo "ERROR: bc required"; exit 1; }

LIGAND_SMILES="COc1cc(SC)ccc1C(=O)N1CCC(C)(O)CC1"
LIGAND_PDBQT="$RESULTS_DIR/ligand_438.pdbqt"

# ----- PfATP4 (9N10) target -----
TARGET_PDBQT="$PROJECT_DIR/data/proteins/9N10.pdbqt"
CENTER_X=134.84
CENTER_Y=133.10
CENTER_Z=97.63
SIZE_X=25
SIZE_Y=25
SIZE_Z=25

# ----- Detection -----
VINA_BIN=""
for cand in /home/taamangtchu/miniforge3/bin/vina /usr/bin/vina /usr/local/bin/vina vina; do
    if command -v "$cand" &>/dev/null; then
        VINA_BIN="$cand"
        break
    fi
done

if [ -z "$VINA_BIN" ]; then
    echo "ERROR: Vina not found in PATH"
    echo "Install via: conda install -c conda-forge vina"
    exit 1
fi
VINA_VER=$("$VINA_BIN" --version 2>&1 | head -1)
echo "Vina: $VINA_BIN ($VINA_VER)"

# Check Gnina (optional — for CNN rescoring)
GNINA_BIN=""
if command -v gnina &>/dev/null; then
    GNINA_BIN="$(command -v gnina)"
    echo "Gnina: $GNINA_BIN (available for CNN rescoring)"
else
    echo "Gnina: not found (install via HPC script install_gnina_hpc.sh)"
fi

# ----- Step 1: SMILES → PDBQT -----
echo ""
echo "=== Step 1: SMILES → PDBQT ==="
if [ ! -f "$LIGAND_PDBQT" ]; then
    obabel -:"$LIGAND_SMILES" -opdbqt --gen3d -h --log \
        -O "$LIGAND_PDBQT" 2>&1
    echo "  Ligand PDBQT: $LIGAND_PDBQT"
else
    echo "  Ligand PDBQT already exists: $LIGAND_PDBQT"
fi

# Verify the PDBQT
if grep -q "ROOT" "$LIGAND_PDBQT" 2>/dev/null; then
    echo "  PDBQT format: OK"
else
    echo "  WARNING: PDBQT may be malformed"
fi

# ----- Step 2: Vina docking (exhaustiveness=128) -----
echo ""
echo "=== Step 2: Vina Docking (exhaustiveness=128) ==="
VINA_OUT="$RESULTS_DIR/ligand_438_vina_out.pdbqt"
VINA_LOG="$RESULTS_DIR/ligand_438_vina.log"

if [ ! -f "$VINA_OUT" ]; then
    echo "  Running Vina with exhaustiveness=128 (this may take 10-30 min)..."
    echo "  Center: [$CENTER_X, $CENTER_Y, $CENTER_Z]  Size: [$SIZE_X, $SIZE_Y, $SIZE_Z]"
    
    $VINA_BIN \
        --receptor "$TARGET_PDBQT" \
        --ligand "$LIGAND_PDBQT" \
        --out "$VINA_OUT" \
        --center_x $CENTER_X --center_y $CENTER_Y --center_z $CENTER_Z \
        --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z \
        --exhaustiveness 128 \
        --num_modes 20 \
        --cpu 8 \
        --log "$VINA_LOG"
    
    echo "  Vina docking complete"
else
    echo "  Vina output already exists: $VINA_OUT"
fi

# ----- Step 3: Parse Vina results -----
echo ""
echo "=== Step 3: Vina Results ==="
if [ -f "$VINA_LOG" ]; then
    echo "  All modes (kcal/mol):"
    grep "^[[:space:]]*[0-9]" "$VINA_LOG" | head -20
    
    BEST_SCORE=$(grep "^[[:space:]]*1" "$VINA_LOG" | awk '{print $2}')
    BEST_SCORE="${BEST_SCORE:-0}"
    echo ""
    echo "  === Best pose: $BEST_SCORE kcal/mol ==="
    echo "  Old score (exhaustiveness=64): -5.73 kcal/mol"
    echo "  Old MM-GBSA: +473.0 ± 1.54 kcal/mol (clash)"
    
    if [ "$(echo "$BEST_SCORE < -6.0" | bc -l 2>/dev/null)" = "1" ]; then
        echo "  ✅ IMPROVED: New pose is better than original (-5.73)"
    elif [ "$(echo "$BEST_SCORE < -5.73" | bc -l 2>/dev/null)" = "1" ]; then
        echo "  🟡 MODEST: Slight improvement over original"
    else
        echo "  ❌ WORSE: New pose is not better than original"
    fi
fi

# ----- Step 4: Gnina CNN rescoring (if available) -----
if [ -n "$GNINA_BIN" ]; then
    echo ""
    echo "=== Step 4: Gnina CNN Rescoring ==="
    GNINA_OUT="$RESULTS_DIR/ligand_438_gnina_out.pdbqt"
    GNINA_LOG="$RESULTS_DIR/ligand_438_gnina.log"
    
    $GNINA_BIN \
        --receptor "$TARGET_PDBQT" \
        --ligand "$VINA_OUT" \
        --out "$GNINA_OUT" \
        --center_x $CENTER_X --center_y $CENTER_Y --center_z $CENTER_Z \
        --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z \
        --exhaustiveness 128 \
        --num_modes 20 \
        --cnn_scoring \
        --log "$GNINA_LOG"
    
    echo "  Gnina rescoring complete"
    echo "  Gnina CNN scores:"
    grep "^[[:space:]]*[0-9]" "$GNINA_LOG" | head -20
else
    echo ""
    echo "=== Step 4: Gnina CNN Rescoring (SKIPPED) ==="
    echo "  Gnina not available locally."
    echo "  To install on HPC, run: bash $SCRIPT_DIR/install_gnina_hpc.sh"
fi

# ----- Summary -----
echo ""
echo "=============================================="
echo "  Redocking Complete"
echo "=============================================="
echo "  Results: $RESULTS_DIR/"
echo "  Best Vina score: $BEST_SCORE kcal/mol"
echo "  Old Vina score:  -5.73 kcal/mol"
echo "  Old MM-GBSA:     +473.0 kcal/mol (CLASH)"
if [ -n "$GNINA_BIN" ]; then
    echo "  Gnina CNN: available"
else
    echo "  Gnina CNN: not available (run install_gnina_hpc.sh)"
fi
echo ""
echo "  Next steps:"
echo "    1. Convert best pose PDBQT → PDB for MD"
echo "    2. Rebuild complex with md_build_complexes.py"
echo "    3. Re-run MM-GBSA to verify clash resolution"
echo "=============================================="
