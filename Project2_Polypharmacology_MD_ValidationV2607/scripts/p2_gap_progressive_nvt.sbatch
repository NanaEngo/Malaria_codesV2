#!/bin/bash
#SBATCH --job-name=p2_gap_nvt_prog
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p2_gap_nvt_prog_%j.log
#SBATCH --error=logs/p2_gap_nvt_prog_%j.err

set -euo pipefail

PROJECT_DIR="${SLURM_SUBMIT_DIR:-/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607}"
cd "$PROJECT_DIR"

PY="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
GMX="/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi"
PILOT="${P2_GAP_PILOT_ROOT:-$PROJECT_DIR/results/md_systems/set_c_gap_pilot_20260811_v2/system}"
OUT="$PROJECT_DIR/results/md_systems/set_c_progressive_nvt_${SLURM_JOB_ID}"

if [[ -e "$OUT" ]]; then
    echo "Refusing non-fresh output root: $OUT" >&2
    exit 2
fi
mkdir -p "$OUT"
cp -a "$PILOT" "$OUT/system"
cd "$OUT/system"

if [[ ! -f complex.gro || ! -f topol.top || ! -f ligand_openff.itp ]]; then
    echo "Missing pilot input files" >&2
    exit 3
fi
if ! command -v mpirun >/dev/null 2>&1; then
    echo "Missing mpirun" >&2
    exit 4
fi
if [[ ! -x "$GMX" ]]; then
    echo "Missing GROMACS executable: $GMX" >&2
    exit 5
fi

stage="initialization"
trap 'rc=$?; printf "{\\n  \\"status\\": \\"FAILED\\",\\n  \\"job_id\\": \\"%s\\",\\n  \\"stage\\": \\"%s\\",\\n  \\"exit_code\\": %d,\\n  \\"scientific_status\\": \\"ISOLATED_DIAGNOSTIC_ONLY\\"\\n}\\n" "$SLURM_JOB_ID" "$stage" "$rc" > progressive_nvt_failure.json; exit "$rc"' ERR

# The validated OpenMPI build must be launched with one MPI rank; do not pass
# -ntmpi to this binary.  All non-MPI CPU flags remain explicit.
gmxrun() {
    mpirun --bind-to none -np 1 "$GMX" "$@"
}

cat > em.mdp <<'EOF'
integrator = steep
nsteps = 10000
emtol = 1000
emstep = 0.0001
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.2
rcoulomb = 1.2
rvdw = 1.2
coulombtype = PME
pme_order = 4
fourierspacing = 0.16
constraints = none
EOF

gmxrun grompp -f em.mdp -c complex.gro -p topol.top -o em.tpr -maxwarn 0 > em.grompp.out 2> em.grompp.err
gmxrun mdrun -s em.tpr -deffnm em -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off > em.mdrun.out 2> em.mdrun.err

cat > make_mdp.py <<'PY'
from pathlib import Path
import sys
name, dt, nsteps, gen_vel = sys.argv[1:]
Path(name).write_text(f"""integrator = md
nsteps = {nsteps}
dt = {dt}
nstxout-compressed = 200
nstenergy = 50
nstlog = 50
continuation = {'no' if gen_vel == 'yes' else 'yes'}
constraints = h-bonds
constraint_algorithm = lincs
lincs_iter = 2
lincs_order = 6
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
gen_vel = {gen_vel}
""")
PY

# Progressive stages: each stage starts from the previous final coordinates.
# A stage failure is recorded and stops the witness; no later stage is run.
prev="em.gro"
idx=0
for spec in "0.0002 nvt_dt0p2fs yes" "0.0005 nvt_dt0p5fs no" "0.001 nvt_dt1fs no" "0.002 nvt_dt2fs no"; do
    read -r dt name gen <<< "$spec"
    stage="$name"
    python_name="${name}.mdp"
    "$PY" make_mdp.py "$python_name" "$dt" 1000 "$gen"
    if grep -Rqs '#ifdef POSRES' topol*.top topol*.itp; then
        echo 'define = -DPOSRES' >> "$python_name"
    fi
    gmxrun grompp -f "$python_name" -c "$prev" -r "$prev" -p topol.top -o "${name}.tpr" -maxwarn 0 > "${name}.grompp.out" 2> "${name}.grompp.err"
    gmxrun mdrun -s "${name}.tpr" -deffnm "$name" -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off > "${name}.mdrun.out" 2> "${name}.mdrun.err"
    cp "${name}.gro" "${name}.final.gro"
    prev="${name}.gro"
    idx=$((idx + 1))
done

cat > progressive_nvt_status.json <<EOF
{
  "status": "PASS",
  "job_id": "${SLURM_JOB_ID}",
  "pilot": "${PILOT}",
  "output_root": "${OUT}",
  "stages_completed": ${idx},
  "dt_ps": [0.0002, 0.0005, 0.001, 0.002],
  "steps_per_stage": 1000,
  "temperature_k": 310.15,
  "downstream_submitted": false,
  "scientific_status": "ISOLATED_DIAGNOSTIC_ONLY"
}
EOF

echo "PROGRESSIVE_NVT_PASS stages=$idx output=$OUT"
