#!/bin/bash
#SBATCH --job-name=p2_setc_gpu_wit
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_publication_gpu_v2_20260812/slurm_%j.out
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_publication_gpu_v2_20260812/slurm_%j.err

# Clean GPU restart from equilibrated inputs. This is not a continuation of the
# aborted CPU production trajectory. GPU update/constraints are deliberately
# disabled because the historical UpdateConstrainGpu path was unstable.
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
export OMP_NUM_THREADS=8
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi

PROJ=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
export SCRIPT_DIR="$PROJ/scripts"
source "$SCRIPT_DIR/md_execution_guard.sh"
md_guard_parse --execute
md_guard_require_authorization

SOURCE="$PROJ/results/md_systems/set_c_publication_witness_v8_20260811/PP-01_PfDHFR_WT"
ROOT="$PROJ/results/md_systems/set_c_publication_gpu_v2_20260812"
SYS="$ROOT/PP-01_PfDHFR_WT"
RUN="$SYS/runs/publication_gpu_20260812_v4/replicate_1"
GMX="$P2_GMX_BIN"

mkdir -p "$RUN"
PROV="$RUN/production_provenance.json"
record_failure() {
  local rc=$?
  python - "$PROV" "$rc" "$BASH_COMMAND" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
p=Path(sys.argv[1])
d=json.loads(p.read_text()) if p.is_file() else {}
d.update({'status':'PRODUCTION_FAILED','failed_utc':datetime.now(timezone.utc).isoformat(),'exit_code':int(sys.argv[2]),'failed_command':sys.argv[3],'md_rrs_status':'NOT_COMPUTED'})
p.write_text(json.dumps(d,indent=2)+'\n')
PY
  exit "$rc"
}
trap record_failure ERR
for f in npt.gro npt.cpt topol.top md.mdp forcefield_manifest.json system_manifest.json; do
  test -s "$SOURCE/$f" || { echo "FAIL: missing source input $SOURCE/$f" >&2; exit 2; }
done

for f in npt.gro npt.cpt topol.top md.mdp; do cp -f "$SOURCE/$f" "$RUN/$f"; done
cp -f "$SOURCE/system_manifest.json" "$SYS/system_manifest.json"

python - <<'PY'
import hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
root=Path('/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607')
source=root/'results/md_systems/set_c_publication_witness_v8_20260811/PP-01_PfDHFR_WT'
sys=root/'results/md_systems/set_c_publication_gpu_v2_20260812/PP-01_PfDHFR_WT'
run=sys/'runs/publication_gpu_20260812_v4/replicate_1'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((source/'forcefield_manifest.json').read_text())
system=json.loads((source/'system_manifest.json').read_text())
expected={'cohort_id':'P2_SET_C_POLYPHARM_17','set_c_id':'PP-01','target':'PfDHFR','mutation':'WT','system_name':'PP-01_PfDHFR_WT'}
for key, value in expected.items():
    if system.get(key) != value:
        raise SystemExit(f'FAIL: system manifest {key}={system.get(key)!r}, expected {value!r}')
if manifest.get('cohort_id') != 'P2_SET_C_POLYPHARM_17' or manifest.get('system_name') != 'PP-01_PfDHFR_WT':
    raise SystemExit('FAIL: force-field manifest identity mismatch')
if manifest.get('protein_force_field') != 'CHARMM36m' or manifest.get('ligand_force_field') != 'OpenFF 2.2.0 (AM1-BCC)':
    raise SystemExit('FAIL: force-field policy does not match the approved witness')
if manifest.get('policy_deviation', {}).get('declared') is not True or manifest.get('policy_deviation', {}).get('approved') is not True:
    raise SystemExit('FAIL: approved OpenFF policy deviation is not declared')
for name, field in [('topol.top','topology_sha256'),('npt.gro','coordinates_sha256'),('npt.cpt','checkpoint_sha256')]:
    if sha(source/name) != manifest.get(field):
        raise SystemExit(f'FAIL: source hash mismatch for {name}')

# The parent manifest contains a stale md_mdp_sha256, while the current file
# retains the declared production protocol. Reconcile without mutating the
# parent manifest: the derived run manifest binds the current bytes and records
# the parent-manifest hash plus the exact reason for the reconciliation.
def mdp_value(name):
    for line in (source/'md.mdp').read_text().splitlines():
        line=line.split(';',1)[0].strip()
        if not line or '=' not in line:
            continue
        key, value=(part.strip() for part in line.split('=',1))
        if key == name:
            return value
    return None
protocol_expected={
    'integrator':'md','nsteps':'5000000','dt':'0.002','continuation':'yes',
    'nstxout-compressed':'5000','nstenergy':'1000','nstlog':'1000',
    'constraints':'h-bonds','constraint_algorithm':'lincs','lincs_iter':'1','lincs_order':'4',
    'cutoff-scheme':'Verlet','nstlist':'10','rlist':'1.2','rcoulomb':'1.2','rvdw':'1.2',
    'coulombtype':'PME','pme_order':'4','fourierspacing':'0.16',
    'tcoupl':'V-rescale','tc-grps':'System','tau_t':'0.1','ref_t':'310.15',
    'pcoupl':'Parrinello-Rahman','pcoupltype':'isotropic','tau_p':'2.0',
    'compressibility':'4.5e-5','ref_p':'1.0','gen_vel':'no',
}
for key, expected_value in protocol_expected.items():
    if mdp_value(key) != expected_value:
        raise SystemExit(f'FAIL: md.mdp protocol {key}={mdp_value(key)!r}, expected {expected_value!r}')
current_mdp_sha=sha(source/'md.mdp')
parent_manifest_sha=sha(source/'forcefield_manifest.json')
reconciled=dict(manifest)
reconciled['parent_forcefield_manifest_sha256']=parent_manifest_sha
reconciled['md_mdp_sha256_parent']=manifest.get('md_mdp_sha256')
reconciled['md_mdp_sha256']=current_mdp_sha
reconciled['provenance_reconciliation']={
    'declared': True,
    'reason':'Parent manifest md_mdp_sha256 was stale; current md.mdp was retained only after exact protocol-key validation.',
    'reconciled_utc':datetime.now(timezone.utc).isoformat(),
    'protocol_keys_checked':protocol_expected,
}
(sys/'forcefield_manifest.json').write_text(json.dumps(reconciled,indent=2)+'\n')

# Stage every local topology include declared by the parent manifest, not just
# topol.top. This preserves relative #include paths for grompp and binds the
# copied dependency bytes to the run provenance.
for relative_name in manifest.get('topology_dependency_sha256', {}):
    relative=Path(relative_name)
    if relative.is_absolute() or '..' in relative.parts:
        raise SystemExit(f'FAIL: unsafe topology dependency path: {relative_name}')
    src=source/relative
    dst=run/relative
    expected_hash=manifest.get('topology_dependency_sha256', {}).get(relative_name)
    if not src.is_file():
        raise SystemExit(f'FAIL: missing topology dependency: {src}')
    if sha(src) != expected_hash:
        raise SystemExit(f'FAIL: source topology dependency hash mismatch: {relative_name}')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

prov={
 'schema_version':2,
 'status':'PRODUCTION_STARTING',
 'created_utc':datetime.now(timezone.utc).isoformat(),
 'cohort_id':'P2_SET_C_MD_RRS_PILOT_PP01_PP02',
 'system':'PP-01_PfDHFR_WT',
 'run_dir':str(run),
 'parent_forcefield_manifest_sha256':parent_manifest_sha,
 'md_mdp_sha256_parent':manifest.get('md_mdp_sha256'),
 'md_mdp_sha256_current':current_mdp_sha,
 'source_equilibration_dir':str(source),
 'source_production_cpu_run':'results/md_systems/set_c_publication_witness_v8_20260811/PP-01_PfDHFR_WT/runs/publication_witness_20260811/replicate_1',
 'source_production_cpu_run_canonical':False,
 'protocol':'10 ns; dt=0.002 ps; 310.15 K; 1 bar; CHARMM36m protein + OpenFF 2.2.0 AM1-BCC ligand; TIP3P',
 'execution_backend':'GROMACS 2025.4 CUDA mixed offload',
 'mdrun_flags':['-ntomp','8','-pin','on','-nb','gpu','-pme','gpu','-bonded','cpu','-update','cpu','-gpu_id','0'],
 'input_sha256':{n:sha(run/n) for n in ['npt.gro','npt.cpt','topol.top','md.mdp']},
 'topology_dependency_sha256':{n:sha(run/Path(n)) for n in manifest.get('topology_dependency_sha256', {})},
 'forcefield_manifest_sha256':sha(sys/'forcefield_manifest.json'),
 'system_manifest_sha256':sha(sys/'system_manifest.json'),
 'md_rrs_status':'NOT_COMPUTED',
}
(run/'production_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
PY

cd "$RUN"
"$GMX" grompp -f md.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o production.tpr -maxwarn 0
"$GMX" mdrun -s production.tpr -deffnm production -v -ntomp 8 -pin on -nb gpu -pme gpu -bonded cpu -update cpu -gpu_id 0 -cpt 15

python - <<'PY'
import hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
run=Path('/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_publication_gpu_v2_20260812/PP-01_PfDHFR_WT/runs/publication_gpu_20260812_v4/replicate_1')
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
required=['production.tpr','production.xtc','production.edr','production.log','production.gro','production.cpt']
missing=[n for n in required if not (run/n).is_file() or (run/n).stat().st_size==0]
prov=json.loads((run/'production_provenance.json').read_text())
prov.update({'status':'PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC' if not missing else 'PRODUCTION_INCOMPLETE','completed_utc':datetime.now(timezone.utc).isoformat(),'outputs_sha256':{n:sha(run/n) for n in required if (run/n).is_file()},'missing_outputs':missing})
(run/'production_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
if missing: raise SystemExit(f'missing production outputs: {missing}')
print('GPU production completed; trajectory QC required')
PY
