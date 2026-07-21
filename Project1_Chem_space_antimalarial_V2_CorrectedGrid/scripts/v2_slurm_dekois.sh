#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
# OPTIMISATION 2026-07-20: When submitting, use --array=0-1249%48
# (48 concurrent tasks on 48-CPU penavoraserver) instead of %16.
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/logs/slurm/%x_%a.log

# DEKOIS V2 worker — one array element = one ligand (active or decoy)
# Array size: 0-1249 (0-49 actives, 50-1249 decoys)
# Environment: RECEPTOR, CX, CY, CZ, EXHAUSTIVITY (PfDHFR grid)

# AUDIT FIX 2026-07-17: added set -eo pipefail + input guards + Vina error
# capture. Previously this script had no set -e, masked all Vina stderr with
# 2>/dev/null, and would silently produce empty outputs on failure.
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
# AUDIT FIX 2026-07-17: set -u incompatible with GROMACS GMXRC (unbound
# `shell` and `GMXLDLIB` variables during conda activate malaria_md).
set +u
conda activate malaria_md
set -u

V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
DEKOIS_DIR="${V2DIR}/results/v2_dekois"
mkdir -p "${V2DIR}/logs/slurm"

i=$SLURM_ARRAY_TASK_ID

if [ "$i" -lt 50 ]; then
  # Active compound: files are zero-padded, 1-indexed (active_0001 to active_0040)
  # AUDIT FIX 2026-07-17: was `active_${i}.pdbqt` (non-padded, 0-indexed) —
  # mismatch with zero-padded 1-indexed filenames from run_v2_dekois.sh.
  # SLURM array 0-49 → shift +1 to match 1-indexed files; i=40-49 will exit 2
  # via input guard (only 40 actives exist).
  LIG=$(printf "%s/actives/active_%04d.pdbqt" "$DEKOIS_DIR" "$((i + 1))")
  OUTFILE="${LIG}.docked.pdbqt"
else
  # Decoy compound: files are non-padded, 1-indexed (decoy_1 to decoy_1200)
  # AUDIT FIX 2026-07-17: decoys created by obabel -m are 1-indexed non-padded.
  # d = i - 50 (0-1199); shift +1 to match 1-indexed files.
  d=$((i - 50))
  LIG="${DEKOIS_DIR}/decoys/decoy_$((d + 1)).pdbqt"
  OUTFILE="${LIG}.docked.pdbqt"
fi

# Reuse: skip if already docked AND output contains a Vina REMARK line
if [ -f "$OUTFILE" ] && [ -s "$OUTFILE" ] && grep -q "VINA RESULT" "$OUTFILE" 2>/dev/null; then
  exit 0
fi

# AUDIT FIX: validate input files exist before invoking Vina.
if [ ! -f "$LIG" ]; then
  echo "ERROR: ligand not found: $LIG" >&2
  exit 2
fi
if [ ! -f "$RECEPTOR" ]; then
  echo "ERROR: receptor not found: $RECEPTOR" >&2
  exit 2
fi

# AUDIT FIX 2026-07-17: capture Vina exit code instead of masking stderr.
# Under set -e, naive $? capture aborts before capture. Wrap with || vina_rc=$?.
vina --receptor "$RECEPTOR" --ligand "$LIG" \
  --center_x $CX --center_y $CY --center_z $CZ \
  --size_x 25 --size_y 25 --size_z 25 \
  --exhaustiveness ${EXHAUSTIVITY:-16} --cpu 1 \
  --out "$OUTFILE" || vina_rc=$?
vina_rc=${vina_rc:-0}

if [ $vina_rc -ne 0 ] || ! grep -q "VINA RESULT" "$OUTFILE" 2>/dev/null; then
  echo "ERROR: Vina failed for $LIG (exit=$vina_rc)" >&2
  rm -f "$OUTFILE"
  exit 3
fi
