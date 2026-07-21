#!/bin/bash
# Rerun missing V2 docking jobs + DEKOIS actives
# Created: 2026-07-17 (audit remediation)
#
# This script identifies and redocks:
#   1. Missing V2 centroid docking jobs (67 across 4 targets)
#   2. Missing DEKOIS actives (34 of 40)
#
# It uses the same corrected V2 grid coordinates as v2_submit_all.sh.
# Runs locally with 4 parallel workers (configurable via N_PARALLEL env).
#
# Usage: bash scripts/v2_rerun_missing.sh [--dry-run]
#        N_PARALLEL=8 bash scripts/v2_rerun_missing.sh

set -eo pipefail

# AUDIT FIX 2026-07-17: set -u incompatible with GROMACS GMXRC.
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u

V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
PROJ="/home/nanaengo/Malaria_codesV2"
LIG_DIR="${PROJ}/Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/results/ligands/pdbqt"
DOCKING="${V2DIR}/results/v2_docking"
DEKOIS="${V2DIR}/results/v2_dekois"
N_PARALLEL="${N_PARALLEL:-4}"
BOX_SIZE=25
EXHAUSTIVITY=64
EXH_DEKOIS=64  # actives need high exhaustiveness for reliable ROC

DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

# Target grid coordinates (V2 corrected — matches Docking/*/config.txt)
declare -A RECEPTORS GRID_CX GRID_CY GRID_CZ
RECEPTORS[pfDHFR]="${PROJ}/data/proteins/7F3Y_v2.pdbqt"
GRID_CX[pfDHFR]=8.34;   GRID_CY[pfDHFR]=-13.9;  GRID_CZ[pfDHFR]=-41.754

RECEPTORS[pfCRT]="${PROJ}/data/proteins/6UKJ.pdbqt"
GRID_CX[pfCRT]=152.5;   GRID_CY[pfCRT]=148.0;   GRID_CZ[pfCRT]=154.5

RECEPTORS[pfATP4]="${PROJ}/data/proteins/9N10.pdbqt"
GRID_CX[pfATP4]=129.3;  GRID_CY[pfATP4]=130.9;  GRID_CZ[pfATP4]=92.4

RECEPTORS[pfClpP]="${PROJ}/data/proteins/4GM2.pdbqt"
GRID_CX[pfClpP]=26.19;  GRID_CY[pfClpP]=35.09;  GRID_CZ[pfClpP]=24.72

echo "=== V2 Rerun Missing Jobs: $(date) ==="
echo "Workers: ${N_PARALLEL}, Exhaustiveness: ${EXHAUSTIVITY}"
echo ""

# ─── Phase 1: V2 centroid docking (67 missing) ───
total_missing=0
for target in pfDHFR pfCRT pfATP4 pfClpP; do
  outdir="${DOCKING}/${target}"
  receptor="${RECEPTORS[$target]}"
  cx="${GRID_CX[$target]}"; cy="${GRID_CY[$target]}"; cz="${GRID_CZ[$target]}"

  # Find missing IDs using Python (robust against sort/padding issues)
  missing_ids=$(python3 -c "
from pathlib import Path
td = Path('${outdir}')
done = set()
if td.exists():
    for f in td.glob('ligand_*_docked.pdbqt'):
        try:
            idx = int(f.stem.replace('ligand_','').replace('_docked',''))
            done.add(idx)
        except ValueError:
            pass
missing = sorted(set(range(484)) - done)
print(' '.join(str(i) for i in missing))
" 2>/dev/null)

  n_missing=$(echo "$missing_ids" | wc -w)
  total_missing=$((total_missing + n_missing))
  echo "  ${target}: ${n_missing} missing centroids"

  if [ "$n_missing" -eq 0 ]; then
    continue
  fi

  # Validate receptor exists
  if [ ! -f "$receptor" ]; then
    echo "    ERROR: receptor not found: $receptor" >&2
    continue
  fi

  if $DRY_RUN; then
    echo "    DRY-RUN: would dock ${n_missing} centroids"
    continue
  fi

  # Dock each missing centroid
  for id in $missing_ids; do
    while [ "$(jobs -r | wc -l)" -ge "$N_PARALLEL" ]; do
      sleep 1
    done
    lig=$(printf "${LIG_DIR}/ligand_%d.pdbqt" "$id")
    out=$(printf "${outdir}/ligand_%04d_docked.pdbqt" "$id")

    if [ ! -f "$lig" ]; then
      echo "    WARN: ligand not found: $lig" >&2
      continue
    fi

    nice -n 10 vina --receptor "$receptor" --ligand "$lig" \
      --center_x "$cx" --center_y "$cy" --center_z "$cz" \
      --size_x "$BOX_SIZE" --size_y "$BOX_SIZE" --size_z "$BOX_SIZE" \
      --exhaustiveness "$EXHAUSTIVITY" --cpu 1 \
      --out "$out" > /dev/null 2>&1 &
  done
  # AUDIT FIX 2026-07-17: `wait` under set -e aborts if ANY background job
  # fails. Use `|| true` to survive individual Vina failures and continue
  # to the next target.
  wait || true
  done_count=$(ls "$outdir"/ligand_*_docked.pdbqt 2>/dev/null | wc -l)
  echo "    → ${done_count}/484 docked total"
done

echo ""
echo "  Total V2 missing: ${total_missing}"
echo ""

# ─── Phase 2: DEKOIS actives (34 missing) ───
echo "--- DEKOIS actives rerun ---"
dekois_receptor="${RECEPTORS[pfDHFR]}"
dekois_cx="${GRID_CX[pfDHFR]}"
dekois_cy="${GRID_CY[pfDHFR]}"
dekois_cz="${GRID_CZ[pfDHFR]}"

if [ ! -f "$dekois_receptor" ]; then
  echo "  ERROR: PfDHFR receptor not found: $dekois_receptor" >&2
else
  # Find missing actives (files without .docked.pdbqt)
  missing_actives=0
  for f in "$DEKOIS"/actives/active_*.pdbqt; do
    [ -f "$f" ] || continue
    [[ "$f" == *.docked.pdbqt ]] && continue
    outfile="${f}.docked.pdbqt"
    if [ ! -f "$outfile" ] || ! grep -q "VINA RESULT" "$outfile" 2>/dev/null; then
      missing_actives=$((missing_actives + 1))
      if $DRY_RUN; then
        echo "  DRY-RUN: would dock $(basename "$f")"
        continue
      fi
      while [ "$(jobs -r | wc -l)" -ge "$N_PARALLEL" ]; do
        sleep 1
      done
      nice -n 10 vina --receptor "$dekois_receptor" --ligand "$f" \
        --center_x "$dekois_cx" --center_y "$dekois_cy" --center_z "$dekois_cz" \
        --size_x "$BOX_SIZE" --size_y "$BOX_SIZE" --size_z "$BOX_SIZE" \
        --exhaustiveness "$EXH_DEKOIS" --cpu 1 \
        --out "$outfile" > /dev/null 2>&1 &
    fi
  done
  # AUDIT FIX 2026-07-17: same wait || true pattern as above.
  wait || true
  if ! $DRY_RUN; then
    docked_actives=$(grep -rl "VINA RESULT" "$DEKOIS"/actives/*.docked.pdbqt 2>/dev/null | wc -l)
    echo "  DEKOIS actives: ${docked_actives}/40 docked (was missing: ${missing_actives})"
  else
    echo "  DEKOIS actives missing: ${missing_actives}"
  fi
fi

echo ""
echo "=== Rerun complete: $(date) ==="
echo "Next step: run v2_postprocess.py to regenerate v2_centroid_scores.csv"
echo "  python3 ${V2DIR}/scripts/v2_postprocess.py"
