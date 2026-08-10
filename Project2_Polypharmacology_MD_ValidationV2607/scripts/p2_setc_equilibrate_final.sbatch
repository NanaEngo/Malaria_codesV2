#!/bin/bash
#SBATCH --job-name=p2_setc_eq_final
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=12G
#SBATCH --time=24:00:00
#SBATCH --array=0-15%4
#SBATCH --output=logs/p2_setc_eq_final_%A_%a.log
#SBATCH --error=logs/p2_setc_eq_final_%A_%a.err

# =============================================================================
# FINAL equilibration array for ALL 16 Set-C systems.
#
# ROOT CAUSE v1 (fixed): the equilibration script ran `gmx_mpi mdrun` WITHOUT
#   an explicit -ntomp, so every array task grabbed ALL 48 cores of the node.
#   Array 15054 launched 16 tasks x 48 threads = 768 threads -> OpenMP
#   thread-allocation failure -> segfault.  Retry 15070 (%4) still used
#   4 x 48 = 192 threads -> re-crash.  Fix: -ntomp 8, %4, --cpus-per-task=8.
#
# ROOT CAUSE v2 (fixed in p2_setc_equilibrate.py): the phase-1 EM used
#   `-DPOSRES` + emstep=0.002, freezing the protein while massive initial
#   clashes (docked ligand, mis-oriented polar H's) pushed water coordinates
#   to NaN -> GROMACS Verlet pair-search segfault (deterministic step ~40-160,
#   reproduced even alone with -ntomp 1).  Fix: unrestrained EM phase 1 with
#   emstep=0.0005 (validated on K76A/WT/worst-case PP-02_WT, all rc=0).
#
# 24 h wall time: EM+EM2 (13k steps) + NVT/NPT (2x50k steps) at 8 threads
# needs ~8-14 h per system; 4 batches of 4 -> ~32-56 h total.
# =============================================================================

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md 2>/dev/null || true

export P2_SETC_NTOMP=8
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
export P2_SETC_ROOT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c

cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607

SYSTEMS=(
  PP-01_PfCRT_K76A
  PP-01_PfCRT_K76T
  PP-01_PfCRT_WT
  PP-01_PfDHFR_C59R
  PP-01_PfDHFR_I164L
  PP-01_PfDHFR_N51I
  PP-01_PfDHFR_S108N
  PP-01_PfDHFR_WT
  PP-02_PfCRT_K76A
  PP-02_PfCRT_K76T
  PP-02_PfCRT_WT
  PP-02_PfDHFR_C59R
  PP-02_PfDHFR_I164L
  PP-02_PfDHFR_N51I
  PP-02_PfDHFR_S108N
  PP-02_PfDHFR_WT
)

SYS="${SYSTEMS[$SLURM_ARRAY_TASK_ID]}"
echo "=== equilibration retry (final, ntomp=8): $SYS (array index $SLURM_ARRAY_TASK_ID) ==="

# Skip systems already fully equilibrated (e.g. a concurrent survivor finished)
if [ -f "$P2_SETC_ROOT/$SYS/npt.gro" ] && [ -s "$P2_SETC_ROOT/$SYS/npt.gro" ]; then
  echo "SKIP: $SYS already has npt.gro"
  exit 0
fi

# Remove stale failure marker so a success is not masked
rm -f "$P2_SETC_ROOT/$SYS/equilibration_failure.json"

python scripts/p2_setc_equilibrate.py --system "$SYS"
RC=$?
echo "=== $SYS finished rc=$RC ==="
exit $RC
