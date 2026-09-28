#!/bin/bash
#SBATCH --job-name=p2_setc_rescue
#SBATCH --partition=production
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=04:00:00
#SBATCH --mem=8G
#SBATCH --begin=18:15
#SBATCH --output=logs/p2_setc_rescue_%j.log
#SBATCH --error=logs/p2_setc_rescue_%j.err

# =============================================================================
# Wave-1 checkpoint rescue (10/08/2026) — AUTOMATED.
#
# Context: 15118 wave-1 tasks (indices 0,2-8) started ~10:02 UTC with an 8 h
# TimeLimit that could NOT be extended (cluster blocks updates on running jobs).
# At the measured NVT rate (~220 steps/min, NTOMP=2), PfCRT systems need ~8.4 h
# -> they are killed by the time limit at ~18:02-18:05 UTC, ~20-40 min before NPT
# completion. mdrun writes npt.cpt every 15 min, so the tail is resumable.
#
# This job is scheduled with --begin=18:15 (after the deterministic 8 h kill) and
# resumes, per wave-1 system, any NPT left incomplete by the timeout:
#   gmx_mpi mdrun -deffnm npt -cpi npt.cpt <CPU-only flags, same as workflow>
#
# Skip conditions: npt.gro already present (completed in time) or npt.cpt absent
# (never reached NPT - e.g. EM/NVT failure -> documented, QC tolerates missing).
# NVT-only interruptions (no npt.cpt yet) are logged for a manual follow-up.
#
# Runs independently of wave-2 (different system dirs) and finishes (~18:50) long
# before 15118 terminates (~02:30 Aug 11) -> no conflict with 15119 production.
# =============================================================================

set -uo pipefail
export PYTHONUNBUFFERED=1

GMX=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
BASE=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c

# Wave-1 systems (15118 array tasks 0,2-8) - the 8h-limit cohort
WAVE1=(
    PP-01_PfDHFR_I164L
    PP-01_PfDHFR_S108N
    PP-01_PfDHFR_WT
    PP-02_PfCRT_K76A
    PP-02_PfCRT_K76T
    PP-02_PfCRT_WT
    PP-02_PfDHFR_C59R
    PP-02_PfDHFR_I164L
)

echo "=== p2_setc_rescue start $(date -u) ==="

# Margin: let SLURM register the 8 h timeouts and release file handles.
sleep 120

rescued=0
skipped_done=0
skipped_no_npt=0
manual_nvt=0

for SYS in "${WAVE1[@]}"; do
    D="$BASE/$SYS"
    if [ ! -d "$D" ]; then
        echo "SKIP $SYS: dir missing"
        continue
    fi
    if [ -f "$D/npt.gro" ]; then
        echo "SKIP $SYS: npt.gro present (completed before limit)"
        skipped_done=$((skipped_done + 1))
        continue
    fi
    if [ ! -f "$D/npt.cpt" ]; then
        echo "SKIP $SYS: no npt.cpt (NPT not reached). nvt.cpt? $([ -f "$D/nvt.cpt" ] && echo yes || echo no)"
        if [ -f "$D/nvt.cpt" ]; then
            manual_nvt=$((manual_nvt + 1))
            echo "  MANUAL-NEEDED $SYS: resume NVT first, then grompp NPT:"
            echo "    gmx_mpi mdrun -deffnm nvt -cpi nvt.cpt -ntomp 2 -nb cpu -pme cpu -bonded cpu -update cpu"
            echo "    gmx_mpi grompp -f npt.mdp -c nvt.gro -t nvt.cpt -r nvt.gro -o npt.tpr (flags from workflow)"
            echo "    gmx_mpi mdrun -deffnm npt -ntomp 2 -nb cpu -pme cpu -bonded cpu -update cpu"
        fi
        skipped_no_npt=$((skipped_no_npt + 1))
        continue
    fi
    echo "=== RESCUE $SYS: resuming npt from checkpoint $(date -u) ==="
    if ( cd "$D" && "$GMX" mdrun -deffnm npt -cpi npt.cpt -ntomp 2 \
             -nb cpu -pme cpu -bonded cpu -update cpu ); then
        if [ -f "$D/npt.gro" ]; then
            echo "OK $SYS: npt.gro recreated ($(stat -c%s "$D/npt.gro") bytes)"
            rescued=$((rescued + 1))
        else
            echo "WARN $SYS: mdrun rc=0 but npt.gro missing"
        fi
    else
        echo "FAIL $SYS: rescue mdrun rc=$?"
    fi
done

echo "=== p2_setc_rescue done $(date -u) ==="
echo "SUMMARY: rescued=$rescued completed_ok=$skipped_done no_npt=$skipped_no_npt manual_nvt_needed=$manual_nvt"
exit 0
