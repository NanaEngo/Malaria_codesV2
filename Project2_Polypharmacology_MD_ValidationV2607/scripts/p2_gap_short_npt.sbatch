#!/bin/bash
#SBATCH --job-name=p2_gap_npt
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=logs/p2_gap_npt_%j.log
#SBATCH --error=logs/p2_gap_npt_%j.err

set -euo pipefail
PROJECT_DIR="${SLURM_SUBMIT_DIR:-/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607}"
cd "$PROJECT_DIR"
PY="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
GMX="/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi"
SRC="${P2_GAP_PROGRESSIVE_ROOT:-$PROJECT_DIR/results/md_systems/set_c_progressive_nvt_15223/system}"
OUT="$PROJECT_DIR/results/md_systems/set_c_short_npt_${SLURM_JOB_ID}"
[[ ! -e "$OUT" ]] || { echo "Refusing non-fresh output root: $OUT" >&2; exit 2; }
[[ -f "$SRC/nvt_dt2fs.gro" && -f "$SRC/nvt_dt2fs.cpt" ]] || { echo "Missing progressive NVT endpoint" >&2; exit 3; }
mkdir -p "$OUT"
# Copy only immutable topology/provenance inputs and the validated NVT
# endpoint; include every topology dependency required by topol.top, but do
# not carry stale intermediate NVT witness outputs forward.
cp "$SRC"/topol.top "$SRC"/ligand_openff.itp "$SRC"/nvt_dt2fs.gro "$SRC"/nvt_dt2fs.cpt "$OUT"/
cp "$SRC"/topol_*.itp "$SRC"/posre*.itp "$OUT"/
cp "$SRC"/forcefield_manifest.json "$SRC"/system_manifest.json "$SRC"/pre_equilibration_audit.json "$OUT"/
if [[ -d "$SRC/charmm36-jul2022.ff" ]]; then
  cp -a "$SRC/charmm36-jul2022.ff" "$OUT/"
fi
cd "$OUT"

if ! command -v mpirun >/dev/null 2>&1 || [[ ! -x "$GMX" ]]; then
  echo "Missing MPI/GROMACS executable" >&2
  exit 4
fi

for required in topol_Protein_chain_A.itp topol_Protein_chain_A2.itp topol_Protein_chain_H.itp topol_Protein_chain_L.itp; do
  [[ -f "$OUT/$required" ]] || { echo "Missing topology dependency: $required" >&2; exit 6; }
done

if ! "$PY" - "$SRC" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])/'progressive_nvt_status.json'
if not p.is_file():
    raise SystemExit('missing progressive_nvt_status.json')
d=json.loads(p.read_text())
if d.get('status') != 'PASS' or d.get('stages_completed') != 4 or d.get('downstream_submitted') is not False:
    raise SystemExit(f'invalid upstream progressive status: {d}')
PY
then
  echo "Upstream progressive NVT status is not PASS" >&2
  exit 5
fi

stage="grompp"
write_failure_status() {
  local rc="$1"
  "$PY" -c 'import json,sys; from pathlib import Path; Path(sys.argv[1]).write_text(json.dumps({"status":"FAILED","stage":sys.argv[2],"exit_code":int(sys.argv[3]),"scientific_status":"ISOLATED_DIAGNOSTIC_ONLY","downstream_submitted":False}, indent=2)+"\\n")' "$OUT/short_npt_status.json" "$stage" "$rc"
}
trap 'rc=$?; write_failure_status "$rc"; exit "$rc"' ERR

cat > witness_npt.mdp <<'EOF'
integrator = md
nsteps = 1000
dt = 0.002
nstxout-compressed = 100
nstenergy = 50
nstlog = 50
continuation = yes
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
pcoupl = Parrinello-Rahman
pcoupltype = isotropic
tau_p = 2.0
compressibility = 4.5e-5
ref_p = 1.0
gen_vel = no
EOF

mpirun --bind-to none -np 1 "$GMX" grompp -f witness_npt.mdp -c nvt_dt2fs.gro -r nvt_dt2fs.gro -t nvt_dt2fs.cpt -p topol.top -o witness_npt.tpr -maxwarn 0 >grompp.out 2>grompp.err
stage="mdrun"
mpirun --bind-to none -np 1 "$GMX" mdrun -s witness_npt.tpr -deffnm witness_npt -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off >mdrun.out 2>mdrun.err

stage="status"
"$PY" - <<'PY'
from pathlib import Path
import json, os, re
root=Path('.')
texts=[]
for name in ('witness_npt.log','mdrun.out','mdrun.err','grompp.out','grompp.err'):
    p=root/name
    if p.exists(): texts.append(p.read_text(errors='replace'))
log='\\n'.join(texts)
required=['witness_npt.gro','witness_npt.cpt','witness_npt.edr','witness_npt.log']
missing=[name for name in required if not (root/name).is_file() or (root/name).stat().st_size == 0]
status={
 'status':'PASS', 'job_id':os.environ.get('SLURM_JOB_ID'),
 'scientific_status':'ISOLATED_2PS_STABILITY_DIAGNOSTIC_ONLY',
 'input_nvt_endpoint':'nvt_dt2fs.gro', 'steps':1000, 'dt_ps':0.002,
 'temperature_target_k':310.15, 'pressure_target_bar':1.0,
 'artifacts':[p.name for p in root.glob('witness_npt.*')],
 'error_markers':sorted(set(re.findall(r'(?im)(?:^Fatal error:|^Error:|^\s*NaN\b|^\s*LINCS warning|^\s*Segmentation fault|^Caught signal 11)',log))),
 'missing_artifacts':missing,
 'downstream_submitted':False,
 'interpretation':'2 ps stability witness; not equilibrated pressure/density; not suitable for production MD',
 'status_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
}
if status['error_markers'] or status['missing_artifacts']:
    status['status']='FAILED_MARKERS'
else:
    status['status']='PASS'
(root/'short_npt_status.json').write_text(json.dumps(status,indent=2)+'\n')
PY
printf 'SHORT_NPT_PASS output=%s\n' "$OUT"
