#!/bin/bash
#SBATCH --job-name=p2_pfcrt_cf
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --export=ALL
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=24:00:00
#SBATCH --output=logs/p2_pfcrt_cf_%j.log
#SBATCH --error=logs/p2_pfcrt_cf_%j.err

set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate pfcrt_colabfold
# Keep both backends available: ColabFold uses CUDA for inference but may
# request CPU for preprocessing/output. The previous cuda-only setting caused
# `Unknown backend cpu`; this remains GPU-first and the preflight rejects a
# machine with no CUDA device.
export JAX_PLATFORMS=cuda,cpu
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.75

# Fail closed: never silently run a nominal GPU job on CPU.
python - <<'PY'
import jax
import os
print('CUDA_VISIBLE_DEVICES=', os.environ.get('CUDA_VISIBLE_DEVICES', 'unset'))
print('JAX devices=', jax.devices())
if not any(getattr(d, 'platform', '') in {'gpu', 'cuda'} for d in jax.devices()):
    raise SystemExit('FAIL-CLOSED: no CUDA JAX device visible; refusing CPU fallback')
PY

PROJECT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
INPUT="$PROJECT/results/md_systems/pfcrt_sequence_reference_20260811/W7FI62.fasta"
OUT="$PROJECT/results/md_systems/pfcrt_colabfold_gpu_retry_20260811"
export INPUT OUT PROJECT
rm -rf "$OUT"
mkdir -p "$OUT"

python - <<'PY'
from pathlib import Path
import hashlib, json, os, sys
from datetime import datetime, timezone
p=Path(os.environ['INPUT']).resolve()
out=Path(os.environ['OUT']).resolve()
h=hashlib.sha256(p.read_bytes()).hexdigest()
manifest={
 'schema_version':1,
 'created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'COLABFOLD_REQUESTED_GPU',
 'method':'ColabFold full-length sequence prediction; not experimental loop validation',
 'accession':'W7FI62','strain':'7G8','sequence_path':str(p),
 'sequence_sha256':h,'python':sys.executable,
 'slurm_job_id':os.environ.get('SLURM_JOB_ID'),
 'command':'colabfold_batch --msa-mode mmseqs2_uniref_env --model-type alphafold2_ptm --num-models 1 --num-recycle 1 --num-seeds 1 --num-relax 0',
 'output_boundary':f'isolated {out}; no canonical PDB or set_c modification; no MD authorization',
 'gpu_preflight':'passed: CUDA JAX device required before inference',
 'jax_platforms':os.environ.get('JAX_PLATFORMS'),
 'xla_mem_fraction':os.environ.get('XLA_PYTHON_CLIENT_MEM_FRACTION')
}
(out/'provenance_preflight.json').write_text(json.dumps(manifest,indent=2)+'\n')
PY

set +e
colabfold_batch \
  --msa-mode mmseqs2_uniref_env \
  --model-type alphafold2_ptm \
  --num-models 1 \
  --num-recycle 1 \
  --num-seeds 1 \
  --num-relax 0 \
  "$INPUT" "$OUT"
CF_RC=$?
MODEL_COUNT=$(find "$OUT" -maxdepth 1 -type f \( -name '*.pdb' -o -name '*.cif' \) | wc -l)
SCORE_COUNT=$(find "$OUT" -maxdepth 1 -type f \( -name '*scores*.json' -o -name '*rank*.json' \) | wc -l)
export CF_RC MODEL_COUNT SCORE_COUNT
set -e

# ColabFold 1.6.2 can return zero after a per-query failure. Never mark the
# run complete unless at least one coordinate file and one score/ranking JSON
# exist; this prevents a false-positive provenance record.
if [ "$CF_RC" -ne 0 ] || [ "$MODEL_COUNT" -lt 1 ] || [ "$SCORE_COUNT" -lt 1 ]; then
  python - <<'PY'
from pathlib import Path
import json, os
from datetime import datetime, timezone
out=Path(os.environ['OUT']).resolve()
p=out/'provenance_preflight.json'
d=json.loads(p.read_text())
d.update({'status':'COLABFOLD_FAILED_NO_VALID_MODEL','completed_utc':datetime.now(timezone.utc).isoformat(),'colabfold_returncode':int(os.environ.get('CF_RC','1')),'model_count':int(os.environ.get('MODEL_COUNT','0')),'score_count':int(os.environ.get('SCORE_COUNT','0'))})
(out/'provenance_colabfold_failed.json').write_text(json.dumps(d,indent=2)+'\n')
PY
  exit 1
fi

python - <<'PY'
from pathlib import Path
import hashlib,json,os
from datetime import datetime,timezone
out=Path(os.environ['OUT']).resolve()
files=[p for p in out.iterdir() if p.is_file() and p.name not in {'provenance_colabfold_completed.json','provenance_colabfold_failed.json'}]
manifest=json.loads((out/'provenance_preflight.json').read_text())
manifest.update({'status':'COLABFOLD_COMPLETED','completed_utc':datetime.now(timezone.utc).isoformat(),'outputs':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
(out/'provenance_colabfold_completed.json').write_text(json.dumps(manifest,indent=2)+'\n')
PY
