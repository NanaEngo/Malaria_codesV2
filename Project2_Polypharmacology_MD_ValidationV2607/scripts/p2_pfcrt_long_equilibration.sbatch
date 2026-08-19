#!/bin/bash
#SBATCH --job-name=p2_pfcrt_eq1ns
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=logs/p2_pfcrt_eq1ns_%j.log
#SBATCH --error=logs/p2_pfcrt_eq1ns_%j.err

# Long NPT equilibration (1 ns) of the repaired PfCRT model, resuming from the
# 100 ps canonical witness checkpoint. Technical stability witness only: no
# production, no binding/affinity/RRS claim.
set -eo pipefail
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u
GMX=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi

SRC=results/md_systems/pfcrt_md_witness_20260818
WORK=results/md_systems/pfcrt_eq1ns_20260818
mkdir -p "$WORK"
cd "$WORK"
cp -a ../pfcrt_md_witness_20260818/charmm36-jul2022.ff .
cp ../pfcrt_md_witness_20260818/topol.top .
cp ../pfcrt_md_witness_20260818/npt.cpt .
cp ../pfcrt_md_witness_20260818/npt.gro .

# 1 ns NPT from the 100 ps checkpoint (continuation = yes)
cat > npt1ns.mdp <<'EOF'
integrator = md
nsteps = 500000
dt = 0.002
nstxout-compressed = 5000
nstenergy = 500
nstlog = 500
continuation = yes
constraints = h-bonds
constraint_algorithm = lincs
lincs_iter = 1
lincs_order = 4
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.2
rcoulomb = 1.2
rvdw = 1.2
coulombtype = PME
pme_order = 4
fourierspacing = 0.16
tcoupl = V-rescale
tc-grps = System
tau_t = 0.1
ref_t = 310.15
pcoupl = Parrinello-Rahman
pcoupltype = isotropic
tau_p = 2.0
compressibility = 4.5e-5
ref_p = 1.0
gen_vel = no
EOF

printf '1\n' | "$GMX" grompp -f npt1ns.mdp -c npt.gro -t npt.cpt -r npt.gro -p topol.top -o npt1ns.tpr -maxwarn 2 > grompp.out 2>&1 || { echo "GROMPP FAILED"; tail -10 grompp.out; exit 1; }
"$GMX" mdrun -s npt1ns.tpr -deffnm npt1ns -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off > mdrun.out 2>&1 || { echo "MDRUN FAILED"; tail -10 mdrun.out; exit 1; }

echo "=== LONG EQUILIBRATION COMPLETE ==="
grep "Performance" npt1ns.log | tail -1
grep -cE "Fatal error|LINCS warning|Segmentation" npt1ns.log || true
ls -la npt1ns.gro npt1ns.cpt npt1ns.edr npt1ns.log
