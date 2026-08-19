#!/bin/bash
#SBATCH --job-name=p2_setc_wit_qc
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --mem=12G
#SBATCH --output=logs/p2_setc_wit_qc_%j.log
#SBATCH --error=logs/p2_setc_wit_qc_%j.err

set -e
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
ROOT=results/md_systems/set_c_publication_witness_v8_20260811
SYS=PP-01_PfDHFR_WT
D="$ROOT/$SYS"
R="$D/runs/publication_witness_20260811/replicate_1"
export P2_SETC_ROOT="$ROOT"
export P2_SETC_QC_OUTPUT="$ROOT/trajectory_qc.csv"
[ -s "$R/production.xtc" ] || { echo 'FAIL: production.xtc missing' >&2; exit 2; }
[ -s "$R/production.tpr" ] || { echo 'FAIL: production.tpr missing' >&2; exit 2; }
python scripts/p2_setc_trajectory_qc.py \
  --system "$SYS" \
  --bound-angstrom 5.0 \
  --min-frames 500 \
  --min-bound-fraction 0.10 \
  --max-frames 2000 \
  --output "$ROOT/trajectory_qc.csv"
python - <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path
root=Path('results/md_systems/set_c_publication_witness_v8_20260811')
qc=root/'trajectory_qc.csv'
prov=root/'post_qc_provenance.json'
rows=qc.read_text().splitlines() if qc.exists() else []
prov.write_text(json.dumps({'schema_version':1,'status':'TRAJECTORY_QC_COMPLETED','completed_utc':datetime.now(timezone.utc).isoformat(),'system':'PP-01_PfDHFR_WT','qc_rule':'minimum heavy-atom protein-ligand distance <5.0 A; bound fraction threshold 0.10; max sampled frames 2000','qc_output':str(qc),'qc_rows':max(0,len(rows)-1),'md_rrs_status':'NOT_COMPUTED','reason':'single WT system is insufficient for mutant/WT per-target MD-RRS'},indent=2)+'\n')
print(prov.read_text())
PY
