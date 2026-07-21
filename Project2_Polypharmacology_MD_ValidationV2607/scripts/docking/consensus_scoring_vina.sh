#!/bin/bash

# --- CONFIGURATION ---
VINA_EXEC="vina" # Assure-toi que 'vina --version' renvoie bien 1.2.7
<<<<<<< Updated upstream
BASE_PATH="/home/vital/Documents/PhD_2021/Malaria_codes/Docking"
LIGAND_DIR="$BASE_PATH/pdbqt_ligands_decoys"

# Identifiant de la cible (à changer manuellement selon la cible : 4GM2/9N10/6UKJ/7F3Y)
TARGET_ID="7F3Y" 
OUT_BASE="$BASE_PATH/Docking_${TARGET_ID}/decoys_results_consensus"
=======
BASE_PATH="/home/myke_vital/Malaria_codes/data/"
LIGAND_DIR="$BASE_PATH/pdbqt_ligands_mmv"

# Identifiant de la cible (à changer manuellement selon la cible : 4GM2/9N10/6UKJ/7F3Y)
TARGET_ID="4GM2" 
OUT_BASE="$BASE_PATH/Docking_${TARGET_ID}/mmv_results_consensus"
>>>>>>> Stashed changes
CONFIG="$BASE_PATH/Docking_${TARGET_ID}/config.txt"

CSV_FILE="$OUT_BASE/summary_consensus_${TARGET_ID}.csv"
REPORT_FILE="$OUT_BASE/progress_report_${TARGET_ID}.txt"

# --- PRÉPARATION ---
# On crée un dossier LOGS pour ne pas encombrer les dossiers de résultats
mkdir -p "$OUT_BASE/EXCELLENT" "$OUT_BASE/GOOD" "$OUT_BASE/OTHERS" "$OUT_BASE/ERRORS" "$OUT_BASE/LOGS"
echo "Ligand,Vina_Score,Vinardo_Score,Best_Score,Category" > "$CSV_FILE"

total_ligands=$(ls "$LIGAND_DIR"/*.pdbqt 2>/dev/null | wc -l)

echo "--------------------------------------------------"
echo "Workflow Consensus Vina 1.2.7 - Cible : $TARGET_ID"
echo "Calcul sur $total_ligands molécules"
echo "--------------------------------------------------"

for ligand_path in "$LIGAND_DIR"/*.pdbqt; do
    [ -e "$ligand_path" ] || continue
    filename=$(basename "$ligand_path")
    name="${filename%.*}"
    
    if [ ! -s "$ligand_path" ]; then
        echo "SAUTÉ : $name (Fichier vide)"
        continue
    fi

    echo -n "Analyse $name... "

    # --- 1. SCORING VINA STANDARD ---
    $VINA_EXEC --config "$CONFIG" --scoring vina --ligand "$ligand_path" \
               --out "$OUT_BASE/LOGS/${name}_vina_out.pdbqt" > "$OUT_BASE/LOGS/${name}_vina.log" 2>&1
    
    raw_v=$(grep -E "^[[:space:]]*1[[:space:]]+" "$OUT_BASE/LOGS/${name}_vina.log" | head -n 1 | awk '{print $2}')
    score_v=$(echo "$raw_v" | tr -d -c '0-9.-')

    # --- 2. SCORING VINARDO ---
    $VINA_EXEC --config "$CONFIG" --scoring vinardo --ligand "$ligand_path" \
               --out "$OUT_BASE/LOGS/${name}_vinardo_out.pdbqt" > "$OUT_BASE/LOGS/${name}_vinardo.log" 2>&1
    
    raw_vn=$(grep -E "^[[:space:]]*1[[:space:]]+" "$OUT_BASE/LOGS/${name}_vinardo.log" | head -n 1 | awk '{print $2}')
    score_vn=$(echo "$raw_vn" | tr -d -c '0-9.-')

    # --- VALIDATION DES SCORES ---
    if [[ -z "$score_v" || -z "$score_vn" ]]; then
        echo "ÉCHEC."
        mv "$ligand_path" "$OUT_BASE/ERRORS/" 2>/dev/null
        continue
    fi

    # Déterminer le meilleur score (le plus petit/négatif) pour le rangement
    best_score=$(echo -e "$score_v\n$score_vn" | sort -n | head -n 1)

    # --- TRI ET RANGEMENT (Basé sur le meilleur des deux scores) ---
    is_excellent=$(echo "$best_score <= -9.0" | bc -l)
    is_good=$(echo "$best_score <= -7.0" | bc -l)

    if [ "$is_excellent" -eq 1 ]; then
        category="EXCELLENT"
        dest_dir="EXCELLENT"
    elif [ "$is_good" -eq 1 ]; then
        category="GOOD"
        dest_dir="GOOD"
    else
        category="OTHERS"
        dest_dir="OTHERS"
    fi

    # On garde la pose Vina par défaut pour le dossier de résultats
    cp "$OUT_BASE/LOGS/${name}_vina_out.pdbqt" "$OUT_BASE/$dest_dir/${name}_out.pdbqt"

    echo "$name,$score_v,$score_vn,$best_score,$category" >> "$CSV_FILE"
    echo "OK (Vina: $score_v | Vinardo: $score_vn)"

    # --- RAPPORT DE PROGRESSION ---
    processed=$(tail -n +2 "$CSV_FILE" | wc -l)
    {
        echo "=== ÉTAT D'AVANCEMENT DOCKING ($TARGET_ID) ==="
        echo "Vina version : 1.2.7 (Consensus Vina/Vinardo)"
        echo "Dernière mise à jour : $(date '+%H:%M:%S')"
        echo "Progression : $processed / $total_ligands"
        echo "Dernier ligand : $name (Best: $best_score kcal/mol)"
    } > "$REPORT_FILE"

done

echo "--------------------------------------------------"
echo "Terminé ! Résultats compilés dans $CSV_FILE"
