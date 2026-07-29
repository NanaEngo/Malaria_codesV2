#!/bin/bash
#SBATCH --job-name=p1_dekois_v2
#SBATCH --array=0-1239%48
# OPTIMISATION 2026-07-20: %48 = max 48 concurrent tasks (1 per CPU on
# penavoraserver, which has 48 CPUs). Previous %16 underutilised the node
# by 67%. Vina --cpu 1 ensures no CPU oversubscription.
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500M
#SBATCH --time=00:30:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/logs/slurm/%x_%a.log

# ============================================================
# DEKOIS V2 — Fixed version (2026-07-19)
# ============================================================
# FIX 1: RECEPTOR, CX, CY, CZ hardcoded in script
# FIX 2: Array 0-39 = actives, 40-1239 = decoys (no wasted indices)
# FIX 3: Exhaustiveness=64 (V2 standard)
# FIX 4: Active PDBQTs regenerated via regen_dekois_pdbqt.py (RDKit)
#         -> fixes Vina tree.h(101) internal error
# FIX 5: Decoys will skip already-completed outputs (reuse logic)
# ============================================================

# --- Vina receptor (PfDHFR 7F3Y V2) ---
RECEPTOR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/data/proteins/7F3Y_v2.pdbqt"

# --- Grid center (PfDHFR active site) ---
CX=1.33
CY=-1.733
CZ=-23.842

# --- Grid parameters ---
SIZE_X=25
SIZE_Y=25
SIZE_Z=25
EXHAUSTIVITY=64

# ============================================================
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
set +u
conda activate malaria_md
set -u

V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
DEKOIS_DIR="${V2DIR}/results/v2_dekois"
mkdir -p "${V2DIR}/logs/slurm"

i=$SLURM_ARRAY_TASK_ID

if [ "$i" -lt 40 ]; then
  # --- ACTIVE (indices 0-39 → active_0001 to active_0040) ---
  LIG=$(printf "%s/actives/active_%04d.pdbqt" "$DEKOIS_DIR" "$((i + 1))")
else
  # --- DECOY (indices 40-1239 → decoy_1 to decoy_1200) ---
  d=$((i - 40))
  LIG="${DEKOIS_DIR}/decoys/decoy_$((d + 1)).pdbqt"
fi

OUTFILE="${LIG}.docked.pdbqt"

# Reuse: skip if already docked with valid Vina output
if [ -f "$OUTFILE" ] && [ -s "$OUTFILE" ] && grep -q "VINA RESULT" "$OUTFILE" 2>/dev/null; then
  exit 0
fi

# Validate inputs
if [ ! -f "$LIG" ]; then
  echo "ERROR: ligand not found: $LIG" >&2
  exit 2
fi
if [ ! -f "$RECEPTOR" ]; then
  echo "ERROR: receptor not found: $RECEPTOR" >&2
  exit 2
fi

echo "Docking: $(basename $LIG) → $(basename $OUTFILE)"
echo "Receptor: $RECEPTOR"
echo "Grid: center=($CX, $CY, $CZ) size=($SIZE_X, $SIZE_Y, $SIZE_Z) EX=$EXHAUSTIVITY"

# Run Vina
vina --receptor "$RECEPTOR" --ligand "$LIG" \
  --center_x $CX --center_y $CY --center_z $CZ \
  --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z \
  --exhaustiveness $EXHAUSTIVITY --cpu 1 \
  --out "$OUTFILE" || vina_rc=$?
vina_rc=${vina_rc:-0}

# Validate output
if [ $vina_rc -ne 0 ] || ! grep -q "VINA RESULT" "$OUTFILE" 2>/dev/null; then
  echo "ERROR: Vina failed for $(basename $LIG) (exit=$vina_rc)" >&2
  rm -f "$OUTFILE"
  exit 3
fi

echo "SUCCESS: $(basename $LIG) docked → score=$(grep 'VINA RESULT' $OUTFILE | head -1 | awk '{print $4}')"
