#!/usr/bin/env bash
#SBATCH --job-name=p2_md_short_rep
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --array=0-15%1
#SBATCH --output=logs/p2_md_short_rep_%A_%a.out
#SBATCH --error=logs/p2_md_short_rep_%A_%a.err

# Short exploratory replicates only. Requires prepared Set-C inputs and the
# explicit execution confirmation. Does not compute MD-RRS or MM-GBSA.
set -euo pipefail
: "${P2_MD_EXECUTE_CONFIRM:?Set P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND after review}"
[[ "$P2_MD_EXECUTE_CONFIRM" == I_UNDERSTAND ]] || { echo 'FAIL-CLOSED: authorization missing' >&2; exit 2; }
PROJECT_DIR="${P2_PROJECT_DIR:-/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607}"
EXPECTED="$PROJECT_DIR/results/md_systems/set_c_preparation_20260812_v1"
[[ -d "$PROJECT_DIR" ]] || { echo "FAIL-CLOSED: project directory unavailable: $PROJECT_DIR" >&2; exit 2; }
# SLURM may not propagate shell-local exports; resolve the only permitted root
# from the checked-out project while still rejecting an explicitly supplied
# alternative root.
P2_SETC_ROOT="${P2_SETC_ROOT:-$EXPECTED}"
[[ "$(realpath -m "$P2_SETC_ROOT")" == "$EXPECTED" ]] || { echo 'FAIL-CLOSED: non-canonical root' >&2; exit 2; }
command -v gmx_mpi >/dev/null || { echo 'FAIL-CLOSED: gmx_mpi unavailable' >&2; exit 3; }

SYSTEMS=(
  PP-01_PfDHFR_WT PP-01_PfDHFR_N51I PP-01_PfDHFR_C59R PP-01_PfDHFR_S108N PP-01_PfDHFR_I164L
  PP-01_PfCRT_WT PP-01_PfCRT_K76T PP-01_PfCRT_K76A
  PP-02_PfDHFR_WT PP-02_PfDHFR_N51I PP-02_PfDHFR_C59R PP-02_PfDHFR_S108N PP-02_PfDHFR_I164L
  PP-02_PfCRT_WT PP-02_PfCRT_K76T PP-02_PfCRT_K76A
)
SYS="${SYSTEMS[$SLURM_ARRAY_TASK_ID]}"
BASE="$P2_SETC_ROOT/$SYS"
[[ -d "$BASE" ]] || { echo "FAIL-CLOSED: missing $BASE" >&2; exit 4; }
for f in topol.top npt.gro npt.cpt forcefield_manifest.json; do [[ -s "$BASE/$f" ]] || { echo "FAIL-CLOSED: missing $f" >&2; exit 4; }; done

RUN="$BASE/runs/short_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
[[ ! -e "$RUN" ]] || { echo "Refusing to reuse $RUN" >&2; exit 5; }
mkdir -p "$RUN"
cp "$BASE/topol.top" "$BASE/npt.gro" "$BASE/npt.cpt" "$RUN/"
# Copy all recursively referenced local topology files while preserving their
# relative paths; fail closed for missing or out-of-tree dependencies.
python - "$BASE" "$RUN" <<'PY'
import re, shutil, sys
from pathlib import Path
base, run = map(Path, sys.argv[1:])
seen = set()
stack = [base / 'topol.top']
root = base.resolve()
while stack:
    current = stack.pop().resolve()
    if current in seen:
        continue
    seen.add(current)
    if not current.is_file():
        raise SystemExit(f'FAIL-CLOSED: missing topology dependency {current}')
    text = current.read_text(errors='replace')
    for name in re.findall(r'^\\s*#include\\s+["<]([^">]+)[">]', text, re.M):
        dep = (current.parent / name).resolve()
        if not dep.is_relative_to(root):
            # The prepared topologies use ./charmm36-jul2022.ff/... relative
            # includes. Stage the exact installed force field into the run
            # directory, and record its source through the copied files.
            if name.startswith('./charmm36-jul2022.ff/') or name.startswith('charmm36-jul2022.ff/'):
                ff_name = name.removeprefix('./')
                source = Path('/usr/share/gromacs/top') / ff_name
                if not source.is_file():
                    raise SystemExit(f'FAIL-CLOSED: standard force-field file unavailable: {source}')
                destination = run / ff_name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                continue
            raise SystemExit(f'FAIL-CLOSED: out-of-tree topology dependency {name}')
        rel = dep.relative_to(root)
        dest = run / rel
        if dep.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            for child in dep.rglob('*'):
                if child.is_file():
                    rel_child = child.relative_to(root)
                    child_dest = run / rel_child
                    child_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(child, child_dest)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dep, dest)
            stack.append(dep)
PY
cat > "$RUN/short.mdp" <<'MDP'
integrator = md
nsteps = 1000000
dt = 0.002
nstxout-compressed = 5000
nstenergy = 1000
nstlog = 1000
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
MDP
SEED=$((12345 + SLURM_ARRAY_TASK_ID * 1000))
printf '%s\n' "system=$SYS" "seed=$SEED" "target_ns=2" "status=STARTED_REQUIRES_QC" > "$RUN/launch_context.txt"
cd "$RUN"
gmx_mpi grompp -f short.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o short.tpr
if [[ "${P2_SHORT_MD_WITNESS_ONLY:-0}" == "1" ]]; then
  printf '%s\n' "status=WITNESS_GROMPP_PASS" "md_rrs_status=NOT_COMPUTED" >> launch_context.txt
  exit 0
fi
gmx_mpi mdrun -deffnm short -ntomp 8 -nb gpu -pme gpu -bonded cpu -update cpu
printf '%s\n' "status=COMPLETED_REQUIRES_TRAJECTORY_QC" "md_rrs_status=NOT_COMPUTED" >> launch_context.txt
