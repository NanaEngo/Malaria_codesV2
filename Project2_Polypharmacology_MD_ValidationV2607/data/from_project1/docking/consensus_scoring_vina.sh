#!/bin/bash
# === AUDIT FIX 2026-07-17: A1 — strict mode + guard LIGAND_DIR ===
set -euo pipefail
: \"${LIGAND_DIR:?FATAL: LIGAND_DIR is unset}\"

# --- CONFIGURATION ---
VINA_EXEC="vina" # Assure-toi que 'vina --version' renvoie bien 1.2.7
BASE_PATH="${PROJECT2_BASE_DIR:-/home/vital/Documents/PhD_2021/Malaria_codes/Docking}"
LIGAND_DIR="$BASE_PATH/pdbqt_ligands_decoys"

# Identifiant de la cible (à changer manuellement selon la cible : 4GM2/9N10/6UKJ/7F3Y)
TARGET_ID="7F3Y" 
OUT_BASE="$BASE_PATH/Docking_${TARGET_ID}/decoys_results_consensus"
