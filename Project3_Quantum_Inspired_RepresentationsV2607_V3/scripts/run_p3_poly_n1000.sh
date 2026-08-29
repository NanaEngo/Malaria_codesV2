#!/usr/bin/env bash
# Detached launcher for P3 physical validation QKS polypharm benchmark (n=1000)
source ~/.bashrc 2>/dev/null
eval "$(conda shell.bash hook 2>/dev/null)"
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607
python scripts/p3_physical_validation.py --analysis poly --n-poly 1000 --n-folds 10 --n-repeats 1
