#!/bin/bash
#SBATCH --job-name=p2_setc_wit_md
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00
#SBATCH --mem=16G
#SBATCH --output=logs/p2_setc_wit_md_%j.log
#SBATCH --error=logs/p2_setc_wit_md_%j.err

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
export P2_GMX_BIN=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi
export P2_SETC_NTOMP=8

PROJ=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
cd "$PROJ"
ROOT=results/md_systems/set_c_publication_witness_v8_20260811
SYS=PP-01_PfDHFR_WT
D="$ROOT/$SYS"
RUN_ABS="$PROJ/$ROOT/$SYS/runs/publication_witness_20260811/replicate_1"
GMX="$P2_GMX_BIN"

[ -s "$D/npt.gro" ] || { echo 'FAIL: missing npt.gro after equilibration' >&2; exit 2; }
[ -s "$D/npt.cpt" ] || { echo 'FAIL: missing npt.cpt after equilibration' >&2; exit 2; }
[ -s "$D/md.mdp" ] || { echo 'FAIL: missing finalized md.mdp' >&2; exit 2; }
[ -s "$D/topol.top" ] || { echo 'FAIL: missing topol.top' >&2; exit 2; }

python - <<'PY'
import json
from pathlib import Path
p=Path('results/md_systems/set_c_publication_witness_v8_20260811/PP-01_PfDHFR_WT/forcefield_manifest.json')
d=json.loads(p.read_text())
if d.get('finalized_by_equilibration') is not True:
    raise SystemExit(f"FAIL: forcefield manifest not finalized: {d.get('finalized_by_equilibration')}")
if d.get('protein_force_field') != 'CHARMM36m':
    raise SystemExit('FAIL: unexpected protein force field')
if d.get('ligand_force_field') != 'OpenFF 2.2.0 (AM1-BCC)':
    raise SystemExit('FAIL: unexpected ligand force field')
print('equilibration/force-field manifest gate: PASS')
PY

mkdir -p "$RUN_ABS"
cp "$D/npt.gro" "$D/npt.cpt" "$D/topol.top" "$D/md.mdp" "$RUN_ABS/"
python - <<'PY'
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
D=Path('results/md_systems/set_c_publication_witness_v8_20260811/PP-01_PfDHFR_WT')
R=D/'runs/publication_witness_20260811/replicate_1'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
prov={'schema_version':1,'status':'PRODUCTION_STARTING','created_utc':datetime.now(timezone.utc).isoformat(),'system':D.name,'run_dir':str(R),'equilibration_job':'15250','protocol':'10 ns; dt=0.002 ps; 310.15 K; 1 bar; CHARMM36m protein + OpenFF 2.2.0 AM1-BCC ligand; TIP3P','input_sha256':{n:sha(R/n) for n in ['npt.gro','npt.cpt','topol.top','md.mdp']},'md_rrs_status':'NOT_COMPUTED'}
(R/'production_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
PY

cd "$D"
"$GMX" grompp -f md.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o "$RUN_ABS/production.tpr" -maxwarn 0
"$GMX" mdrun -s "$RUN_ABS/production.tpr" -deffnm "$RUN_ABS/production" -v -ntomp 8 -nb cpu -pme cpu -bonded cpu -update cpu

python - <<'PY'
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
R=Path('/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_publication_witness_v8_20260811/PP-01_PfDHFR_WT/runs/publication_witness_20260811/replicate_1')
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
required=['production.tpr','production.xtc','production.edr','production.log','production.gro']
missing=[n for n in required if not (R/n).is_file() or (R/n).stat().st_size==0]
prov=json.loads((R/'production_provenance.json').read_text())
prov.update({'status':'PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC' if not missing else 'PRODUCTION_INCOMPLETE','completed_utc':datetime.now(timezone.utc).isoformat(),'outputs_sha256':{n:sha(R/n) for n in required if (R/n).is_file()},'missing_outputs':missing})
(R/'production_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
if missing: raise SystemExit(f'missing production outputs: {missing}')
print('production completed; trajectory QC required')
PY
