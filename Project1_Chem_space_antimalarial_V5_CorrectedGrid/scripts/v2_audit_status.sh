#!/bin/bash
# Ponytail + Graphify audit: check what exists before acting
V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"

echo "=== PONYTAIL AUDIT: $(date) ==="
echo ""

echo "--- Phase 2 Re-dock ---"
for t in pfDHFR pfCRT pfATP4 pfClpP; do
    count=$(ls "$V2DIR/results/v2_docking/$t/"*_docked.pdbqt 2>/dev/null | wc -l)
    echo "  $t: $count/484"
done

echo ""
echo "--- DEKOIS V2 ---"
da=$(ls "$V2DIR/results/v2_dekois/actives/"*.docked.pdbqt 2>/dev/null | wc -l)
dd=$(ls "$V2DIR/results/v2_dekois/decoys/"*.docked.pdbqt 2>/dev/null | wc -l)
echo "  Actives: $da/50  Decoys: $dd/1200"

echo ""
echo "--- MMV ---"
mmv_count=$(ls "$V2DIR/results/v2_mmv/"*/ 2>/dev/null | wc -l)
echo "  V2 docked: $mmv_count targets"

echo ""
echo "--- Results CSVs ---"
for f in "$V2DIR/results/"*v2*.csv "$V2DIR/results/"*.csv; do
    [ -f "$f" ] && echo "  $(basename $f): $(wc -l < "$f") rows"
done

echo ""
echo "--- Running processes ---"
ps aux | grep "[v]ina" | wc -l | xargs echo "  Vina processes:"
ps aux | grep -E "(run_v2_redock|dekois)" | grep -v grep | awk '{print "  "$11, $2, strftime("%H:%M", $9)}'

echo ""
echo "=== Audit done ==="
