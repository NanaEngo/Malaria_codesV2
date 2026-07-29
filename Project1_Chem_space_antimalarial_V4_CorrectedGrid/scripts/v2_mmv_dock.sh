#!/bin/bash
# V2 Corrected Grid — MMV Malaria Box re-docking
# Docks 399 MMV compounds against all 4 targets with corrected grids
# Source MMV PDBQTs: Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/pdbqt_ligands_mmv/
# After dock: run v2_mmv_analyze.py

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
# AUDIT FIX 2026-07-17: set -u incompatible with GROMACS GMXRC.
set +u
conda activate malaria_md
set -u

PROJ="/home/nanaengo/Malaria_codesV2"
P2DATA="${PROJ}/Project2_Polypharmacology_MD_ValidationV2607"
MMV_DIR="${P2DATA}/data/from_project1/data/pdbqt_ligands_mmv"
V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
OUT="${V2DIR}/results/v2_mmv"
N_PARALLEL=4
EXHAUSTIVITY=16

mkdir -p "$OUT"

# Re-use Phase 2 re-dock if complete; else run MMV separately
dock_target() {
  local name=$1 receptor=$2 cx=$3 cy=$4 cz=$5
  local outdir="${OUT}/${name}"
  mkdir -p "$outdir"
  echo "[$(date +%H:%M)] Starting MMV ${name}"

  for f in "$MMV_DIR"/*.pdbqt; do
    while (( $(jobs -r | wc -l) >= N_PARALLEL )); do
      sleep 2
    done
    base=$(basename "$f")
    outfile="${outdir}/${base}"
    [ -f "$outfile" ] && continue
    nice -n 10 vina --receptor "$receptor" --ligand "$f" \
      --center_x $cx --center_y $cy --center_z $cz \
      --size_x 25 --size_y 25 --size_z 25 \
      --exhaustiveness $EXHAUSTIVITY --cpu 1 \
      --out "$outfile" > /dev/null 2>&1 &
  done
  wait
  local count=$(ls "$outdir"/*.pdbqt 2>/dev/null | wc -l)
  echo "[$(date +%H:%M)] MMV ${name}: ${count} docked"
}

dock_target "pfDHFR" "${PROJ}/data/proteins/7F3Y_v2.pdbqt" 8.34 -13.9 -41.754
dock_target "pfCRT" "${PROJ}/data/proteins/6UKJ.pdbqt" 152.5 148.0 154.5
dock_target "pfATP4" "${PROJ}/data/proteins/9N10.pdbqt" 129.3 130.9 92.4
dock_target "pfClpP" "${PROJ}/data/proteins/4GM2.pdbqt" 26.19 35.09 24.72

echo "=== MMV V2 dock complete: $(date) ==="
