#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/logs/slurm/%x_%a.log
# AUDIT FIX 2026-07-17: default --time raised from 01:00:00 to 02:00:00.
# Previously, the 1h default caused pfATP4 to lose 16 / 484 tasks to TIME LIMIT
# when run unoverridden. v2_submit_all.sh was patched to pass --time=02:00:00
# explicitly, but the worker default also needs to be safe in isolation.

# Generic Vina worker for Phase 2 re-dock (484 centroids)
# Environment: TARGET, RECEPTOR, CX, CY, CZ, EXHAUSTIVITY=64
# Called via: sbatch --array=0-483 --export=TARGET=...,RECEPTOR=...

set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
# AUDIT FIX 2026-07-17: `set -u` is incompatible with GROMACS GMXRC
# scripts sourced during `conda activate malaria_md` (references unbound
# `shell` and `GMXLDLIB` variables, causing silent abort + empty logs).
# Disable -u around activation, re-enable after.
set +u
conda activate malaria_md
set -u

V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
LIG_DIR="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/results/ligands/pdbqt"
OUTDIR="${V2DIR}/results/v2_docking/${TARGET}"
BOX_SIZE=25

mkdir -p "$OUTDIR" "${V2DIR}/logs/slurm"

i=$SLURM_ARRAY_TASK_ID

# Reuse: skip if already docked AND output contains a Vina REMARK line
LIG=$(printf "${LIG_DIR}/ligand_%d.pdbqt" $i)
OUTFILE=$(printf "${OUTDIR}/ligand_%04d_docked.pdbqt" $i)
if [ -f "$OUTFILE" ] && [ -s "$OUTFILE" ] && grep -q "VINA RESULT" "$OUTFILE"; then
  exit 0
fi

# AUDIT FIX: validate input files exist before invoking Vina.
# Previously a missing file would silently produce an empty output and
# downstream postprocess would record None for that ligand.
if [ ! -f "$LIG" ]; then
  echo "ERROR: ligand not found: $LIG" >&2
  exit 2
fi
if [ ! -f "$RECEPTOR" ]; then
  echo "ERROR: receptor not found: $RECEPTOR" >&2
  exit 2
fi

# Dock (capture stderr for debugging on failure).
# AUDIT FIX 2026-07-17: under `set -e`, the naive `vina $?` pattern would
# abort before $? is captured. Wrap with `|| vina_rc=$?` so the script
# survives a Vina failure and reaches the cleanup + exit 3 path.
vina --receptor "$RECEPTOR" --ligand "$LIG" \
  --center_x $CX --center_y $CY --center_z $CZ \
  --size_x $BOX_SIZE --size_y $BOX_SIZE --size_z $BOX_SIZE \
  --exhaustiveness $EXHAUSTIVITY --cpu 1 \
  --out "$OUTFILE" || vina_rc=$?
vina_rc=${vina_rc:-0}

if [ $vina_rc -ne 0 ] || ! grep -q "VINA RESULT" "$OUTFILE" 2>/dev/null; then
  echo "ERROR: Vina failed for $LIG (exit=$vina_rc)" >&2
  rm -f "$OUTFILE"
  exit 3
fi
