#!/bin/bash
# Launcher for the R2.4 DEKOIS MTX-stripped re-run (detached, survives session end)
cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V7_CorrectedGrid || exit 1
mkdir -p results/dekois_mtxstripped_20260909
exec /home/nanaengo/miniforge3/envs/malaria_md/bin/python -u \
  scripts/p1_r24_dekois_mtxstripped.py --workers 24 \
  >> results/dekois_mtxstripped_20260909/run.log 2>&1