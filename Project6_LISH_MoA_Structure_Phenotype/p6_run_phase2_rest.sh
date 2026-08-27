#!/bin/bash
cd ~/Malaria_codesV2/Project6_LISH_MoA_Structure_Phenotype
PY=~/miniforge3/envs/qom/bin/python
# wait for the running kfold phenotype job to finish
while pgrep -f "phase2_benchmark.py --features phenotype --split kfold" > /dev/null; do sleep 60; done
$PY scripts/p6_phase2_benchmark.py --features phenotype --split collision_group > p6_bench_cg.log 2>&1
$PY scripts/p6_phase2_benchmark.py --features phenotype --split scaffold > p6_bench_scaf.log 2>&1
$PY scripts/p6_phase2_benchmark.py --features structure --split collision_group > p6_bench_struct_cg.log 2>&1
echo ALL_DONE > p6_phase2_status.txt
