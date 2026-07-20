#!/bin/bash
# Dock DEKOIS PfDHFR actives (40) with same protocol as decoys
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
PROJECT_ROOT="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarialV2607"
OUTPUT_DIR="${PROJECT_ROOT}/results/r1a_dekois"
RECEPTOR="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt"
ACTIVES_SMI="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/external/dekois/DHFR_ligands.smi"
ACT_PDBQT="${OUTPUT_DIR}/actives_pdbqt"
SCORES="${OUTPUT_DIR}/dekois_dhfr_actives_scores.csv"
mkdir -p "${ACT_PDBQT}"
echo "=== DEKOIS actives docking started: $(date) ==="
i=0
while IFS= read -r smi; do
  i=$((i+1))
  echo "$smi" > /tmp/active_$$.smi
  obabel -ismi /tmp/active_$$.smi -opdbqt -O "${ACT_PDBQT}/active_$(printf %04d $i).pdbqt" --gen3d 2>/dev/null
done < "${ACTIVES_SMI}"
rm -f /tmp/active_$$.smi
echo "Converted $i actives to PDBQT"
echo "ligand_id,vina_score" > "${SCORES}"
for f in "${ACT_PDBQT}"/active_*.pdbqt; do
  ln=$(basename "$f" .pdbqt)
  out="${OUTPUT_DIR}/individual_results/${ln}_docked.pdbqt"
  vina --receptor "$RECEPTOR" --ligand "$f" \
    --center_x 1.33 --center_y -1.733 --center_z -23.842 \
    --size_x 25 --size_y 25 --size_z 25 \
    --exhaustiveness 64 --num_modes 20 --cpu 32 \
    --out "$out" > /dev/null 2>&1
  sc=$(grep -A2 "REMARK VINA RESULT" "$out" | grep -oE "\-?[0-9]+\.[0-9]+" | head -1)
  echo "$ln,$sc" >> "${SCORES}"
done
echo "=== DEKOIS actives docking done: $(date) ==="
