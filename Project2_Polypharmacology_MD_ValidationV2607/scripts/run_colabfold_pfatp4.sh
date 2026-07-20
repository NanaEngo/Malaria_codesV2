#!/bin/bash
# ==============================================================================
# ColabFold (AlphaFold2) — Prédiction PfATP4 complet
#
# Cible: PfATP4 (PF3D7_1211900, UniProt Q9U445, 1264 aa)
# But: Modèle SANS template PDB pour comparer de novo avec cryo-EM 9N10
#
# Installation ColabFold sur HPC:
#   cd ~ && git clone https://github.com/YoshitakaMo/localcolabfold.git
#   cd localcolabfold && bash install.sh
#   # Télécharge les poids (~3 Go) et configure l'environnement
#
# Usage (sbatch):
#   scp PfATP4_Q9U445.fasta nanaengo@100.73.21.40:~/colabfold_input/
#   scp run_colabfold_pfatp4.sh nanaengo@100.73.21.40:~/colabfold_input/
#   ssh nanaengo@100.73.21.40
#   sbatch ~/colabfold_input/run_colabfold_pfatp4.sh
#
# Usage (direct — petit test):
#   bash ~/colabfold_input/run_colabfold_pfatp4.sh  (sans GPU, très lent)
# ==============================================================================

#SBATCH --job-name=af2_pfatp4
#SBATCH --output=af2_pfatp4_%j.out
#SBATCH --error=af2_pfatp4_%j.err
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --partition=gpu

set -euo pipefail

# ----- Configuration -----
INPUT_FASTA="$HOME/colabfold_input/PfATP4_Q9U445.fasta"
OUTPUT_DIR="$HOME/colabfold_results/pfatp4_$(date +%Y%m%d)"
COLABFOLD_ENV="$HOME/localcolabfold/colabfold-conda"
COLABFOLD_BATCH="$COLABFOLD_ENV/bin/colabfold_batch"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  ColabFold — PfATP4 (Q9U445, 1264 aa)"
echo "=============================================="
echo "  Input:  $INPUT_FASTA"
echo "  Output: $OUTPUT_DIR"
echo "  Date:   $(date)"
echo ""

# Vérifier l'entrée
if [ ! -f "$INPUT_FASTA" ]; then
    echo "ERROR: FASTA not found: $INPUT_FASTA"
    exit 1
fi

# Détection GPU
echo "--- GPU Detection ---"
if command -v nvidia-smi &>/dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo "  GPU OK"
else
    echo "  WARNING: No GPU detected — ColabFold sera très lent (~heures)"
fi
echo ""

# Activer l'environnement ColabFold
echo "--- Activating ColabFold environment ---"
if [ -f "$COLABFOLD_ENV/bin/activate" ]; then
    source "$COLABFOLD_ENV/bin/activate"
    echo "  Env: $COLABFOLD_ENV"
else
    echo "  ERROR: ColabFold environment not found at $COLABFOLD_ENV"
    echo "  Install: cd ~/localcolabfold && bash install.sh"
    exit 1
fi
echo ""

# Lancer ColabFold
echo "--- Running ColabFold (AlphaFold2) ---"
echo "  Modèle: PfATP4 complet (1264 aa, ~2-4h sur GPU, ~12-24h CPU)"
echo "  Date:   $(date)"
echo ""

# NOTE: 1264 aa avec --num-recycle 3 peut causer OOM sur GPU < 24 Go VRAM.
# Réduire à --num-recycle 1 si échec mémoire.

# Vérifier dispo OpenMM pour --amber
AMBER_FLAG=""
if "$COLABFOLD_ENV/bin/python" -c "import openmm" 2>/dev/null; then
    AMBER_FLAG="--amber"
    echo "  OpenMM OK → relaxation Amber activée"
else
    echo "  WARNING: OpenMM non disponible → pas de relaxation Amber"
    echo "  (peut être installé: conda install -c conda-forge openmm)"
fi

# PAS de --templates : on veut un modèle de novo non biaisé par la cryo-EM 9N10
$COLABFOLD_BATCH \
    "$INPUT_FASTA" \
    "$OUTPUT_DIR" \
    --num-recycle 3 \
    --num-seeds 1 \
    --use-gpu-relax \
    $AMBER_FLAG \
    --rank iptm+ptm \
    2>&1 | tee "$OUTPUT_DIR/colabfold.log"

echo ""
echo "--- ColabFold Complete ---"
echo "  Output: $OUTPUT_DIR/"
echo "  Log:    $OUTPUT_DIR/colabfold.log"
echo ""

# Lister les sorties
echo "--- Output Files ---"
ls -lh "$OUTPUT_DIR/"*.pdb 2>/dev/null || echo "  No PDB files found"
ls -lh "$OUTPUT_DIR/"*.json 2>/dev/null || echo "  No JSON files found"
echo ""

# Résumé des métriques de confiance
echo "--- Confidence Summary ---"
SCORES_JSON=$(ls "$OUTPUT_DIR/"*_scores.json 2>/dev/null | head -1)
if [ -n "$SCORES_JSON" ] && [ -f "$SCORES_JSON" ]; then
    python3 -c "
import json
with open('$SCORES_JSON') as f:
    d = json.load(f)
for k, v in d.items():
    if isinstance(v, (int, float)):
        print(f'  {k}: {v}')
" 2>/dev/null || echo "  (could not parse scores)"
fi
echo ""

echo "=============================================="
echo "  Prochaines étapes:"
echo "  1. rsync -avz nanaengo@100.73.21.40:$OUTPUT_DIR/ ./results/colabfold_pfatp4/"
echo "  2. Comparer AF2 vs cryo-EM 9N10:"
echo "     - RMSD backbone (Aligner AF2→9N10 via PyMOL/USCF Chimera)"
echo "     - pLDDT par domaine (N/C-terminal, TM hélices)"
echo "     - Régions manquantes dans 9N10 comblées par AF2?"
echo "  3. Si AF2 diffère de 9N10 dans le site actif:"
echo "     - Re-docker ligand 438 sur AF2 et comparer les poses"
echo "=============================================="
