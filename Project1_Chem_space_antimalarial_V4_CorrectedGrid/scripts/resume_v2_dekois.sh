#!/bin/bash
# Resume DEKOIS V2 — dock remaining actives + decoys, compute ROC-AUC
V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
OUT="$V2DIR/results/v2_dekois"
VINA_DOCK="$V2DIR/scripts/vina_dock.sh"
export RECEPTOR="/home/nanaengo/Malaria_codesV2/data/proteins/7F3Y_v2.pdbqt"

# Remaining actives
ls $OUT/actives/active_*.pdbqt | grep -v '\.docked\.' | while read f; do
  [ ! -f "${f}.docked.pdbqt" ] && echo "$f"
done > /tmp/remain_actives.lst
echo "Remaining actives: $(wc -l < /tmp/remain_actives.lst)"

ls $OUT/decoys/decoy_*.pdbqt | grep -v '\.docked\.' | while read f; do
  [ ! -f "${f}.docked.pdbqt" ] && echo "$f"
done > /tmp/remain_decoys.lst
echo "Remaining decoys: $(wc -l < /tmp/remain_decoys.lst)"

# Dock remaining actives (fast: 34 × ~2 min ÷ 4 = ~17 min)
echo "Docking remaining actives..."
xargs -P 4 -I{} bash "$VINA_DOCK" {} 8.34 -13.9 -41.754 < /tmp/remain_actives.lst
echo "Actives done: $(ls $OUT/actives/*.docked.pdbqt | wc -l)/40"

# Dock remaining decoys (1142 × ~2 min ÷ 4 = ~9.5h)
echo "Docking remaining decoys..."
xargs -P 4 -I{} bash "$VINA_DOCK" {} 8.34 -13.9 -41.754 < /tmp/remain_decoys.lst
echo "Decoys done: $(ls $OUT/decoys/*.docked.pdbqt | wc -l)/1200"

# ROC-AUC
python3 -c "
from sklearn.metrics import roc_auc_score
import glob
def sc(f):
    with open(f) as fh:
        for l in fh:
            if 'VINA RESULT' in l: return float(l.strip().split()[2])
    return None
a = [s for s in [sc(f) for f in glob.glob('$OUT/actives/*.docked.pdbqt')] if s]
d = [s for s in [sc(f) for f in glob.glob('$OUT/decoys/*.docked.pdbqt')] if s]
auc = roc_auc_score([1]*len(a)+[0]*len(d), [-s for s in a+d])
print(f'ROC-AUC: {auc:.4f} ({len(a)} act, {len(d)} dec)')
with open('$OUT/dekois_v2_roc_auc.csv','w') as f: f.write(f'roc_auc,{auc:.4f}\nn_actives,{len(a)}\nn_decoys,{len(d)}\n')
"
echo "=== Resume DEKOIS done: $(date) ==="
