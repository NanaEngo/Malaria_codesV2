#!/bin/bash
# P1 V2 Corrected Grid — Parallel re-dock with resume support
# 16 workers × 1 CPU each — 48-core server has headroom
# Skips already-docked ligands; run idempotently

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
# AUDIT FIX 2026-07-17: set -u incompatible with GROMACS GMXRC.
set +u
conda activate malaria_md
set -u

PROJ="/home/nanaengo/Malaria_codesV2"
V2_DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
LIG_DIR="${PROJ}/Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/results/ligands/pdbqt"
RESULTS="${V2_DIR}/results/v2_docking"
N_CENTROIDS=484
N_PARALLEL=16
VINA_CPUS=1
EXHAUSTIVITY=64
BOX_SIZE=25

mkdir -p "${RESULTS}"

echo "=== P1 V2 Re-dock started: $(date) ===" | tee "${RESULTS}/pipeline.log"
echo "Workers: ${N_PARALLEL}, CPUs/Vina: ${VINA_CPUS}" | tee -a "${RESULTS}/pipeline.log"

dock_target() {
  local name=$1 receptor=$2 cx=$3 cy=$4 cz=$5
  local outdir="${RESULTS}/${name}"
  mkdir -p "$outdir"
  local todo=()
  local docked=0

  for i in $(seq 0 $((N_CENTROIDS - 1))); do
    local outfile=$(printf "${outdir}/ligand_%04d_docked.pdbqt" $i)
    if [ -f "$outfile" ] && [ -s "$outfile" ]; then
      docked=$((docked + 1))
    else
      todo+=($i)
    fi
  done

  echo "[$(date +%H:%M)] ${name}: ${docked} already docked, ${#todo[@]} remaining" | tee -a "${RESULTS}/pipeline.log"

  for i in "${todo[@]}"; do
    while (( $(jobs -r | wc -l) >= N_PARALLEL )); do
      sleep 2
    done
    LIG=$(printf "${LIG_DIR}/ligand_%d.pdbqt" $i)
    OUT=$(printf "${outdir}/ligand_%04d_docked.pdbqt" $i)
    nice -n 10 vina --receptor "$receptor" --ligand "$LIG" \
      --center_x $cx --center_y $cy --center_z $cz \
      --size_x $BOX_SIZE --size_y $BOX_SIZE --size_z $BOX_SIZE \
      --exhaustiveness $EXHAUSTIVITY --cpu $VINA_CPUS \
      --out "$OUT" > /dev/null 2>&1 &
  done
  wait
  local count=$(ls "$outdir"/*.pdbqt 2>/dev/null | wc -l)
  echo "[$(date +%H:%M)] ${name}: ${count} docked total" | tee -a "${RESULTS}/pipeline.log"
}

dock_target "pfDHFR" "${PROJ}/data/proteins/7F3Y_v2.pdbqt" 8.34 -13.9 -41.754
dock_target "pfCRT" "${PROJ}/data/proteins/6UKJ.pdbqt" 152.5 148.0 154.5
dock_target "pfATP4" "${PROJ}/data/proteins/9N10.pdbqt" 129.3 130.9 92.4
dock_target "pfClpP" "${PROJ}/data/proteins/4GM2.pdbqt" 26.19 35.09 24.72

echo "=== V2 Re-dock complete: $(date) ===" | tee -a "${RESULTS}/pipeline.log"
for target in pfDHFR pfCRT pfATP4 pfClpP; do
  COUNT=$(ls "${RESULTS}/${target}"/*.pdbqt 2>/dev/null | wc -l)
  echo "  ${target}: ${COUNT} / ${N_CENTROIDS}" | tee -a "${RESULTS}/pipeline.log"
done
