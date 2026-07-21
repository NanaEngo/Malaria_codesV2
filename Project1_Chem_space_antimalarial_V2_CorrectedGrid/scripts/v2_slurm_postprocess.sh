#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/logs/slurm/v2_postprocess.log

# Post-processing: parse all docked PDBQTs → consolidated CSV

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
python3 "$V2DIR/scripts/v2_postprocess.py"

# Update graphify after results are generated
if command -v graphify &>/dev/null; then
  graphify "$V2DIR/scripts" --code-only 2>&1 | grep -E "(wrote|error|found)"
fi

echo "Post-processing complete: $(date)"
