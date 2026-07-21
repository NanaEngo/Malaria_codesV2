#!/bin/bash
# Master submission: transition all Vina workloads to SLURM job arrays
# All 5 docking arrays run in parallel (independent targets)
# Post-processing waits for all docking to complete

set -euo pipefail
V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
PROJ="/home/nanaengo/Malaria_codesV2"
WORKER="${V2DIR}/scripts/v2_slurm_vina.sh"
DEKOIS_WORKER="${V2DIR}/scripts/v2_slurm_dekois.sh"
POST_WORKER="${V2DIR}/scripts/v2_slurm_postprocess.sh"
LOGS="${V2DIR}/logs/slurm"
mkdir -p "$LOGS"

DRY_RUN=false
# AUDIT FIX 2026-07-17: under `set -u`, $1 is unbound when invoked with
# no args. Use ${1:-} to default to empty string so dry-run detection
# works whether the script is called by the user, by cron, or by watchdog.
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

submit() {
  if $DRY_RUN; then
    echo "DRY-RUN: sbatch $*"
    echo "000000"
  else
    sbatch --parsable "$@" 2>&1
  fi
}

echo "=== Submitting all Vina workloads to SLURM ==="
echo ""

# ─── Phase 2: 4 targets in parallel, each %8 concurrent ───
echo "--- Phase 2 Re-dock (4 targets in parallel) ---"

submit --array=0-483%8 \
  --job-name=v2_pfdhfr \
  --time=02:00:00 \
  --export=TARGET=pfDHFR,RECEPTOR=${PROJ}/data/proteins/7F3Y_v2.pdbqt,CX=8.34,CY=-13.9,CZ=-41.754,EXHAUSTIVITY=64 \
  --output="$LOGS/v2_pfdhfr_%a.log" \
  "$WORKER" > /tmp/j_pfdhfr.txt
# AUDIT FIX 2026-07-17: under `set -o pipefail`, a transient sbatch output
# (warning line before the job ID, etc.) would let `grep` exit 1, killing
# the master submit mid-flight. Wrap with `|| J="\"\"` so any non-numeric
# token collapses to an empty string and the array is silently skipped.
J1=$(cat /tmp/j_pfdhfr.txt | grep -oE '[0-9]+' | head -1) || J1=""
echo "  PfDHFR: $J1"

submit --array=0-483%8 \
  --job-name=v2_pfcrt \
  --time=02:00:00 \
  --export=TARGET=pfCRT,RECEPTOR=${PROJ}/data/proteins/6UKJ.pdbqt,CX=152.5,CY=148.0,CZ=154.5,EXHAUSTIVITY=64 \
  --output="$LOGS/v2_pfcrt_%a.log" \
  "$WORKER" > /tmp/j_pfcrt.txt
J2=$(cat /tmp/j_pfcrt.txt | grep -oE '[0-9]+' | head -1) || J2=""
echo "  PfCRT:   $J2"

submit --array=0-483%8 \
  --job-name=v2_pfatp4 \
  --time=02:00:00 \
  --export=TARGET=pfATP4,RECEPTOR=${PROJ}/data/proteins/9N10.pdbqt,CX=129.3,CY=130.9,CZ=92.4,EXHAUSTIVITY=64 \
  --output="$LOGS/v2_pfatp4_%a.log" \
  "$WORKER" > /tmp/j_pfatp4.txt
J3=$(cat /tmp/j_pfatp4.txt | grep -oE '[0-9]+' | head -1) || J3=""
echo "  PfATP4:  $J3"

submit --array=0-483%8 \
  --job-name=v2_pfclpp \
  --time=02:00:00 \
  --export=TARGET=pfClpP,RECEPTOR=${PROJ}/data/proteins/4GM2.pdbqt,CX=26.19,CY=35.09,CZ=24.72,EXHAUSTIVITY=64 \
  --output="$LOGS/v2_pfclpp_%a.log" \
  "$WORKER" > /tmp/j_pfclpp.txt
J4=$(cat /tmp/j_pfclpp.txt | grep -oE '[0-9]+' | head -1) || J4=""
echo "  PfClpP:  $J4"

# ─── DEKOIS V2: actives (0-49) + decoys (50-1249) ───
echo "--- DEKOIS V2 ---"

submit --array=0-1249%16 \
  --job-name=v2_dekois \
  --time=04:00:00 \
  --export=RECEPTOR=${PROJ}/data/proteins/7F3Y_v2.pdbqt,CX=8.34,CY=-13.9,CZ=-41.754,EXHAUSTIVITY=16 \
  --output="$LOGS/v2_dekois_%a.log" \
  "$DEKOIS_WORKER" > /tmp/j_dekois.txt
J5=$(cat /tmp/j_dekois.txt | grep -oE '[0-9]+' | head -1) || J5=""
echo "  DEKOIS:  $J5"

# ─── Post-processing (after all docking complete) ───
echo "--- Post-processing (after all docking) ---"

DEPS="afterok"
for j in "$J1" "$J2" "$J3" "$J4" "$J5"; do
  [ -n "$j" ] && [ "$j" != "000000" ] && DEPS="${DEPS}:${j}"
done

submit --job-name=v2_postprocess \
  --dependency=$DEPS \
  --output="$LOGS/v2_postprocess.log" \
  "$POST_WORKER" > /tmp/j_post.txt
J6=$(cat /tmp/j_post.txt | grep -oE '[0-9]+' | head -1) || J6=""
echo "  Post:    $J6"

echo ""
echo "=== Submitted ==="
echo "  Phase 2 PfDHFR:  $J1  (8 conc.)"
echo "  Phase 2 PfCRT:   $J2  (8 conc.)"
echo "  Phase 2 PfATP4:  $J3  (8 conc.)"
echo "  Phase 2 PfClpP:  $J4  (8 conc.)"
echo "  DEKOIS V2:       $J5  (16 conc.)"
echo "  Post-processing: $J6  (after all docking)"
echo ""
echo "Total slots: 4×8 + 16 = 48 (all 48 cores utilized)"
echo "Monitor: squeue -u $USER"
echo "Logs: $LOGS/"
