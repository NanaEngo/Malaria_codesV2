#!/bin/bash
#SBATCH --job-name=p2_md_50ns
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --array=0-7%1
#SBATCH --output=logs/p2_md_50ns_%A_%a.out
#SBATCH --error=logs/p2_md_50ns_%A_%a.err

set -e

# Target 50-ns systems: PP-01 and PP-15 across PfDHFR and PfCRT
SYSTEMS=(
    "PP-01_PfDHFR_WT"
    "PP-01_PfDHFR_N51I"
    "PP-01_PfDHFR_C59R"
    "PP-01_PfCRT_WT"
    "PP-01_PfCRT_K76T"
    "PP-15_PfDHFR_WT"
    "PP-15_PfCRT_WT"
    "PP-02_PfDHFR_N51I"
)

SYSTEM=${SYSTEMS[$SLURM_ARRAY_TASK_ID]}
ROOT_DIR="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607"
SYS_DIR="${ROOT_DIR}/results/md_systems/set_c_preparation_20260812_v1/${SYSTEM}"
RUN_DIR="${SYS_DIR}/runs/ext50_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"

mkdir -p "${RUN_DIR}" "${ROOT_DIR}/logs"
cd "${RUN_DIR}"

source /home/nanaengo/miniforge3/bin/activate malaria_md

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting 50-ns extension production for ${SYSTEM} (Task ${SLURM_ARRAY_TASK_ID})"

# Check input files
GRO="${SYS_DIR}/npt.gro"
CPT="${SYS_DIR}/npt.cpt"
TOP="${SYS_DIR}/topol.top"

if [ ! -f "${GRO}" ] || [ ! -f "${TOP}" ]; then
    echo "ERROR: Missing required input files in ${SYS_DIR}"
    exit 1
fi

# Prepare 50-ns MDP (25,000,000 steps @ 2 fs = 50,000 ps = 50 ns)
cat << 'EOF' > md_50ns.mdp
integrator              = md
dt                      = 0.002
nsteps                  = 25000000
nstlog                  = 25000
nstenergy               = 25000
nstxout-compressed      = 25000
compressed-x-precision  = 1000
continuation            = yes
constraint_algorithm    = lincs
constraints             = h-bonds
lincs_iter              = 1
lincs_order             = 4
cutoff-scheme           = Verlet
ns_type                 = grid
nstlist                 = 20
rlist                   = 1.2
coulombtype             = PME
rcoulomb                = 1.2
vdwtype                 = Cut-off
vdw-modifier            = Force-switch
rvdw-switch             = 1.0
rvdw                    = 1.2
tcoupl                  = Nose-Hoover
tc-grps                 = Protein Non-Protein
tau_t                   = 1.0 1.0
ref_t                   = 310.15 310.15
pcoupl                  = Parrinello-Rahman
pcoupltype              = isotropic
tau_p                   = 5.0
ref_p                   = 1.0
compressibility         = 4.5e-5
pbc                     = xyz
DispCorr                = EnerPres
gen_vel                 = no
EOF

# Grompp
gmx grompp -f md_50ns.mdp -c "${GRO}" -r "${GRO}" -p "${TOP}" -t "${CPT}" -o production_50ns.tpr -maxwarn 2

# Mdrun GPU
gmx mdrun -deffnm production_50ns -ntomp ${SLURM_CPUS_PER_TASK} -pin on -nb gpu -pme gpu -bonded gpu -update gpu

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Completed 50-ns production MD for ${SYSTEM}"
