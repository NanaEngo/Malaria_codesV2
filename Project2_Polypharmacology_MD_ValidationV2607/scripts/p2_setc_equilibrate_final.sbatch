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
# ROOT CAUSE v3 (FINAL, 10/08 — see set_c_preparation_remediation_20260809.md):
#   p2_setc_prepare_openff.py::add_ligand_to_topol inserted MOL0 as the FIRST
#   [ molecules ] entry while merge_gro wrote protein-first/ligand-last
#   coordinates -> grompp silently mis-assigned atom order -> genion scrambled
#   coordinates -> collapsed aromatic rings (TYR34 CG-CE1 0.68 A, TYR238
#   OH-CD2 1.0 A) and exploded side chains (LYS104 HE1-HE2 65 A) in complex.gro
#   of all 16 systems -> water NaN explosion -> non-deterministic libgomp
#   segfault in the Verlet pair-search.
#   Fix: [ molecules ] order aligned with coordinates (protein first, MOL0
#   second) + ions.gro regenerated from clean solvated.gro; 16/16 verified
#   clean (0 collapsed rings).  Structures were re-prepared before this array.
#
# Also retained from earlier fixes:
#   v1: explicit -ntomp 8 (no whole-node grabbing under arrays);
#   v2: unrestrained EM phase 1, emstep=0.0001 (POSRES froze the protein and
#       amplified residual clashes into NaN explosions).
#
# 24 h wall time: EM+EM2 (13k steps) + NVT/NPT (2x50k steps) at 8 threads
# needs ~8-14 h per system; 4 batches of 4 -> ~32-56 h total.
# =============================================================================

set -e
# Do not rely on shell activation inside Slurm's --wrap environment.  The
# worker itself requires this exact interpreter and fails closed otherwise.
export P2_SETC_PYTHON=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
[ -x "$P2_SETC_PYTHON" ] || { echo "FATAL: missing malaria_md Python" >&2; exit 90; }

export P2_SETC_NTOMP=8
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
export P2_SETC_ROOT=${P2_SETC_ROOT:-/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c}

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

"$P2_SETC_PYTHON" scripts/p2_setc_equilibrate.py --system "$SYS"
RC=$?
echo "=== $SYS finished rc=$RC ==="
exit $RC
