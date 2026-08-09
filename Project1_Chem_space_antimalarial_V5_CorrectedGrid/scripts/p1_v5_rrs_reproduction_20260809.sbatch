#!/usr/bin/env bash
#SBATCH --job-name=p1v5_rrs_rep
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p1_v5_rrs_rep_%x_%j.log
#SBATCH --error=logs/p1_v5_rrs_rep_%x_%j.err
set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate diffdock

ROOT=/home/nanaengo/Malaria_codesV2
V5=$ROOT/Project1_Chem_space_antimalarial_V5_CorrectedGrid
TARGET=${TARGET:?set TARGET=PfDHFR or PfCRT}
RUN_ROOT=${RUN_ROOT:?set RUN_ROOT to an isolated absolute output directory}
case "$RUN_ROOT" in
  /*) ;;
  *) echo "FAIL-CLOSED: RUN_ROOT must be absolute: $RUN_ROOT" >&2; exit 2 ;;
esac
EXPECTED_ROOT="$V5/results/exploratory/rrs_reproduction_20260809"
EXPECTED_REAL="$(realpath -m "$EXPECTED_ROOT")"
RUN_REAL="$(realpath -m "$RUN_ROOT")"
case "$RUN_REAL" in
  "$EXPECTED_REAL"/*) ;;
  *) echo "FAIL-CLOSED: RUN_ROOT is outside the approved exploratory root: $RUN_ROOT" >&2; exit 2 ;;
esac
# New submissions are target-isolated. mkdir is an atomic per-target lock:
# concurrent reruns for the same target cannot both enter the output tree.
TARGET_ROOT="$RUN_ROOT/$TARGET"
if ! mkdir "$TARGET_ROOT" 2>/dev/null; then
  echo "FAIL-CLOSED: target output lock already exists: $TARGET_ROOT" >&2
  exit 2
fi
mkdir "$TARGET_ROOT/vina_scores"
cd "$V5"

exec python scripts/p1_v5_vina_dock_mutants.py \
  --target "$TARGET" \
  --output-root "$TARGET_ROOT/vina_scores" \
  --out-csv "$TARGET_ROOT/vina_scores/v5_mutant_vina_scores_${TARGET}.csv"
