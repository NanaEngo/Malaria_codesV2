#!/bin/bash
#SBATCH --job-name=p2_ligand_annot
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/p2_ligand_annot_%j.log
#SBATCH --error=logs/p2_ligand_annot_%j.err

# Independent structural annotation only; no GROMACS, docking, RRS, or MD-RRS.
set -euo pipefail

PROJECT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
PYTHON=/home/nanaengo/miniforge3/envs/malaria_md/bin/python
cd "$PROJECT"
mkdir -p logs

"$PYTHON" scripts/p2_ligandexplorer_annotation.py \
  --input-dir "$PROJECT/data/proteins" \
  --output-dir "$PROJECT/results/ligandexplorer_annotation_20260812" \
  --binary /home/nanaengo/ligandexplorer/venv/bin/ligandexplorer \
  --backend gnn \
  --device cpu
