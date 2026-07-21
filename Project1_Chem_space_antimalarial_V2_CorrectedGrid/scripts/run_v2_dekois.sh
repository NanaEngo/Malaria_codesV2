#!/bin/bash
set -eo pipefail
# V2 DEKOIS benchmark: re-dock 40 actives + 1200 decoys with corrected PfDHFR grid
# Runs independently of Phase 2 (independent ligand set)

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
# AUDIT FIX 2026-07-17: set -u incompatible with GROMACS GMXRC.
set +u
conda activate malaria_md
set -u

V2_DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
PROJ="/home/nanaengo/Malaria_codesV2"
RECEPTOR="${PROJ}/data/proteins/7F3Y_v2.pdbqt"
OUT="${V2_DIR}/results/v2_dekois"
ACT_SMI="${PROJ}/Project2_Polypharmacology_MD_ValidationV2607/data/external/dekois/DHFR_ligands.smi"
DEC_SDF="${PROJ}/Project2_Polypharmacology_MD_ValidationV2607/data/external/dekois/DHFR_Celling-v1.12_decoyset.sdf"
mkdir -p "${OUT}"/{actives,decoys}
N=4
VINA_DOCK="$(dirname "$0")/vina_dock.sh"
export RECEPTOR

# obabel C++ binary (Python wrapper broken in Python 3.13 env)
OBABEL="/home/nanaengo/miniforge3/pkgs/openbabel-3.1.1-py311h8b422cb_9/bin/obabel"
export BABEL_LIBDIR="/home/nanaengo/miniforge3/pkgs/openbabel-3.1.1-py311h8b422cb_9/lib/openbabel/3.1.0"
export LD_LIBRARY_PATH="/home/nanaengo/miniforge3/pkgs/openbabel-3.1.1-py311h8b422cb_9/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

echo "=== DEKOIS V2: $(date) ==="

# 40 actives
echo "Docking 40 actives (exh=64)..."
i=0
awk 'NF && !/^#/' "$ACT_SMI" | while IFS= read -r smi; do
  i=$((i+1)); f=$(printf "%s/actives/active_%04d.pdbqt" "$OUT" "$i")
  echo "$smi" | $OBABEL -ismi -opdbqt -O "$f" --gen3d 2>/dev/null
  echo "$f"
done > /tmp/dekois_actives.lst
xargs -P $N -I{} bash "$VINA_DOCK" {} 8.34 -13.9 -41.754 < /tmp/dekois_actives.lst

# 1200 decoys — split SDF → individual PDBQT, dock (exh=16 OK for relative ranking)
echo "Docking decoys (exh=16)..."
$OBABEL "$DEC_SDF" -opdbqt -O "${OUT}/decoys/decoy_.pdbqt" -m 2>/dev/null
ls "${OUT}/decoys"/decoy_*.pdbqt > /tmp/dekois_decoys.lst
xargs -P $N -I{} bash "$VINA_DOCK" {} 8.34 -13.9 -41.754 < /tmp/dekois_decoys.lst

# Extract scores, compute ROC-AUC
python3 -c "
import csv, glob, os
from sklearn.metrics import roc_auc_score

def score_from_pdbqt(f):
    with open(f) as fh:
        for line in fh:
            if 'VINA RESULT' in line:
                return float(line.strip().split()[2])
    return None

act = [score_from_pdbqt(f) for f in glob.glob('${OUT}/actives/*.docked.pdbqt')]
dec = [score_from_pdbqt(f) for f in glob.glob('${OUT}/decoys/*.docked.pdbqt')]
act = [s for s in act if s is not None]
dec = [s for s in dec if s is not None]

y_true = [1]*len(act) + [0]*len(dec)
y_score = [-s for s in act + dec]  # negate: lower Vina = better
auc = roc_auc_score(y_true, y_score)
print(f'Actives: {len(act)}, Decoys: {len(dec)}, ROC-AUC: {auc:.4f}')
with open('${OUT}/dekois_v2_roc_auc.csv', 'w') as f:
    f.write(f'roc_auc,{auc:.4f}\nn_actives,{len(act)}\nn_decoys,{len(dec)}\n')
"

echo "=== DEKOIS V2 done: $(date) ==="
echo "AUC → ${OUT}/dekois_v2_roc_auc.csv"
