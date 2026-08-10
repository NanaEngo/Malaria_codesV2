#!/bin/bash
#SBATCH --job-name=p2_setc_eq_2t
#SBATCH --partition=production
#SBATCH --array=0-11%8
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=12:00:00
#SBATCH --mem=8G
#SBATCH --output=logs/p2_setc_eq_2t_%A_%a.log
#SBATCH --error=logs/p2_setc_eq_2t_%A_%a.err

# =============================================================================
# Equilibration retry with P2_SETC_NTOMP=2 (reduced thread count).
#
# Why: The original 15106 used NTOMP=8 with --cpus-per-task=8. On a shared node
# where multiple array tasks run concurrently, 8 threads × N tasks causes severe
# OpenMP contention → tasks stall with logs ~100 B.
#
# Array 0-11 maps to the 12 systems NOT yet equilibrated (indices 0-3 of 15106
# completed 4 PP-01 systems; indices 4-15 are the 12 remaining). 8 concurrent
# × 2 threads = 16 threads max — safe on the 48-core node.
#
# After this array completes, resubmit:
#   PROD=$(sbatch --parsable --dependency=afterany:THIS_JOB scripts/p2_setc_production.sbatch)
#   sbatch --dependency=afterany:$PROD scripts/p2_setc_qc_and_md_rrs.sbatch
# NOTE (10/08): afterany REQUIRED (not afterok) - task 1 (PP-01_PfDHFR_N51I) is a
# documented failure; afterok:JOB_* on an array never satisfies with any FAILED task
# -> guaranteed deadlock of the production job. QC tolerates missing systems.
# NOTE: TimeLimit 08:00:00 is tight at NTOMP=2 (measured NVT ~220 steps/min ->
# ~8.4 h total for PfCRT systems). Running-job TimeLimit updates are BLOCKED by the
# cluster (Access/permission denied); wave-1 PfCRT tasks may time out at 8 h.
# Rescue path: gmx mdrun -s npt.tpr -cpi npt.cpt -deffnm npt -ntomp 2 (checkpoint).
# =============================================================================

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -euo pipefail

export PYTHONUNBUFFERED=1
export P2_SETC_NTOMP=2   # <-- REDUCED THREADS (was 8 in 15106)

cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607

# Map array index to system name (12 systems not yet equilibrated)
SYSTEMS=(
    PP-01_PfDHFR_I164L    # index 0 — STALLED in 15106
    PP-01_PfDHFR_N51I     # index 1 — FAILED libgomp in 15106
    PP-01_PfDHFR_S108N    # index 2 — STALLED in 15106
    PP-01_PfDHFR_WT       # index 3 — STALLED in 15106
    PP-02_PfCRT_K76A      # index 4  — STALLED/PENDING
    PP-02_PfCRT_K76T      # index 5  — PENDING
    PP-02_PfCRT_WT        # index 6  — PENDING
    PP-02_PfDHFR_C59R     # index 7  — PENDING
    PP-02_PfDHFR_I164L    # index 8  — PENDING
    PP-02_PfDHFR_N51I     # index 9  — PENDING
    PP-02_PfDHFR_S108N    # index 10 — PENDING
    PP-02_PfDHFR_WT       # index 11 — PENDING
)

IDX=$SLURM_ARRAY_TASK_ID
SYS="${SYSTEMS[$IDX]}"

echo "=== equilibration retry (NTOMP=2): $SYS (array task $IDX) ==="
echo "P2_SETC_NTOMP: $P2_SETC_NTOMP"
echo "SLURM_JOB_ID: $SLURM_JOB_ID"

python scripts/p2_setc_equilibrate.py --system "$SYS"

echo "=== $SYS finished rc=$? ==="