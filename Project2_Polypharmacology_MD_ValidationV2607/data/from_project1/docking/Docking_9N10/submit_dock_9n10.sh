#!/bin/bash
# === AUDIT FIX 2026-07-17: A4 — strict mode ===
set -euo pipefail

# --- CONFIGURATION ---
BASE_PATH="/home/myke_vital/Docking"
LIGAND_DIR="$BASE_PATH/pdbqt_ligands"
OUT_BASE="$BASE_PATH/Docking_9N10/results"
CONFIG="$BASE_PATH/Docking_9N10/config.txt"
CSV_FILE="$OUT_BASE/summary_results_9n10.csv"
REPORT_FILE="$OUT_BASE/progress_report_9n10.txt"

# --- PRÉPARATION ---
mkdir -p "$OUT_BASE/EXCELLENT" "$OUT_BASE/GOOD" "$OUT_BASE/OTHERS" "$OUT_BASE/ERRORS"
echo "Ligand,Affinity_kcal_mol,Category" > "$CSV_FILE"

total_ligands=$(ls "$LIGAND_DIR"/*.pdbqt 2>/dev/null | wc -l)

echo "--------------------------------------------------"
echo "Lancement workflow Vina 1.2.5 - $total_ligands molécules"
echo "--------------------------------------------------"

for ligand_path in "$LIGAND_DIR"/*.pdbqt; do
    [ -e "$ligand_path" ] || continue
    filename=$(basename "$ligand_path")
    name="${filename%.*}"
    
    if [ ! -s "$ligand_path" ]; then
        echo "SAUTÉ : $name (Fichier vide)"
        continue
    fi

    echo -n "Docking $name... "

    # --- EXECUTION VINA 1.2.5 ---
    # On supprime --log et on redirige la sortie (>) vers le fichier .log
    vina --config "$CONFIG" \
         --ligand "$ligand_path" \
         --out "$OUT_BASE/${name}_out.pdbqt" > "$OUT_BASE/${name}.log" 2>&1
    
    if [ $? -ne 0 ]; then
        echo "ÉCHEC."
        mv "$ligand_path" "$OUT_BASE/ERRORS/" 2>/dev/null
        continue
    fi

    # --- EXTRACTION DU SCORE ---
    # Recherche de la ligne du mode 1 dans le fichier log qu'on vient de créer
    raw_score=$(grep -E "^[[:space:]]*1[[:space:]]+" "$OUT_BASE/${name}.log" | head -n 1 | awk '{print $2}')
    score=$(echo "$raw_score" | tr -d -c '0-9.-')

    if [[ -z "$score" || ! "$score" =~ ^-?[0-9]+(\.[0-9]+)?$ ]]; then
        echo "SCORE INVALIDE."
        continue
    fi

    # --- TRI ET RANGEMENT ---
    is_excellent=$(echo "$score <= -9.0" | bc -l)
    is_good=$(echo "$score <= -7.0" | bc -l)

    if [ "$is_excellent" -eq 1 ]; then
        category="EXCELLENT"
        mv "$OUT_BASE/${name}_out.pdbqt" "$OUT_BASE/EXCELLENT/${name}_out.pdbqt"
    elif [ "$is_good" -eq 1 ]; then
        category="GOOD"
        mv "$OUT_BASE/${name}_out.pdbqt" "$OUT_BASE/GOOD/${name}_out.pdbqt"
    else
        category="OTHERS"
        mv "$OUT_BASE/${name}_out.pdbqt" "$OUT_BASE/OTHERS/${name}_out.pdbqt"
    fi

    echo "$name,$score,$category" >> "$CSV_FILE"
    echo "OK ($score kcal/mol)"

    # --- RAPPORT DE PROGRESSION ---
    processed=$(grep -c "," "$CSV_FILE")
    processed=$((processed - 1))
    {
        echo "=== ÉTAT D'AVANCEMENT DOCKING (4GM2) ==="
        echo "Vina version : 1.2.5"
        echo "Dernière mise à jour : $(date '+%H:%M:%S')"
        echo "Progression : $processed / $total_ligands"
        echo "Dernier ligand : $name ($score kcal/mol)"
    } > "$REPORT_FILE"

done

echo "--------------------------------------------------"
echo "Terminé ! Résultats dans $OUT_BASE"
