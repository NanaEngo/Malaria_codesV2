#!/bin/bash
#SBATCH --job-name=p2_pfcrt_eq1ns_r
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/p2_pfcrt_eq1ns_r_%j.log
#SBATCH --error=logs/p2_pfcrt_eq1ns_r_%j.err

# Resume the 1 ns NPT equilibration of the repaired PfCRT model from the
# checkpoint written when job 15387 hit the 3h walltime (step 392240 / ~784 ps).
# mdrun -cpi continues from the checkpoint to the tpr nsteps (500000 = 1 ns).
# Technical stability witness only: no production, no binding/affinity/RRS claim.
set -eo pipefail
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u
GMX=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi

WORK=results/md_systems/pfcrt_eq1ns_20260818
cd "$WORK"

# Resume from the walltime checkpoint; output files are appended/overwritten.
"$GMX" mdrun -s npt1ns.tpr -deffnm npt1ns -cpi npt1ns.cpt -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off > mdrun_resume.out 2>&1 || { echo "MDRUN RESUME FAILED"; tail -10 mdrun_resume.out; exit 1; }

echo "=== LONG EQUILIBRATION RESUME COMPLETE ==="
grep "Performance" npt1ns.log | tail -1
grep -E "^ *Step +Time" -A1 npt1ns.log | tail -2
grep -cE "Fatal error|LINCS warning|Segmentation" npt1ns.log || true
ls -la npt1ns.gro npt1ns.cpt npt1ns.edr npt1ns.log
