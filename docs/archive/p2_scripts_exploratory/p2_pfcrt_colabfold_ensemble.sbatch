#!/bin/bash
#SBATCH --job-name=p2_pfcrt_ens
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --export=ALL
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=24:00:00
#SBATCH --output=logs/p2_pfcrt_ens_%j.log
#SBATCH --error=logs/p2_pfcrt_ens_%j.err

set -euo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate pfcrt_colabfold

# GPU-first, but retain CPU for preprocessing. Never accept CPU-only inference.
export JAX_PLATFORMS=cuda,cpu
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.75

python - <<'PY'
import os
import jax
print('CUDA_VISIBLE_DEVICES=', os.environ.get('CUDA_VISIBLE_DEVICES', 'unset'))
print('JAX devices=', jax.devices())
if not any(getattr(d, 'platform', '') in {'gpu', 'cuda'} for d in jax.devices()):
    raise SystemExit('FAIL-CLOSED: no CUDA JAX device visible; refusing CPU fallback')
PY

PROJECT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
INPUT="$PROJECT/results/md_systems/pfcrt_sequence_reference_20260811/W7FI62.fasta"
OUT="$PROJECT/results/md_systems/pfcrt_colabfold_gpu_ensemble_20260811"
export PROJECT INPUT OUT
rm -rf "$OUT"
mkdir -p "$OUT"

python - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, os, sys

p = Path(os.environ['INPUT']).resolve()
out = Path(os.environ['OUT']).resolve()
manifest = {
    'schema_version': 1,
    'status': 'COLABFOLD_ENSEMBLE_REQUESTED_GPU',
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'method': 'ColabFold AlphaFold2-PTM isolated ensemble; technical reconstruction hypothesis only',
    'accession': 'W7FI62',
    'strain': '7G8',
    'sequence_path': str(p),
    'sequence_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
    'python': sys.executable,
    'slurm_job_id': os.environ.get('SLURM_JOB_ID'),
    'ensemble_policy': {
        'model_type': 'alphafold2_ptm',
        'num_models': 5,
        'num_seeds': 3,
        'num_ensemble': 1,
        'num_relax': 1,
        'max_msa': '512:1024',
    },
    'command': 'colabfold_batch --msa-mode mmseqs2_uniref_env --model-type alphafold2_ptm --num-models 5 --num-ensemble 1 --num-seeds 3 --num-relax 1 --max-msa 512:1024',
    'output_boundary': f'isolated {out}; no canonical PDB, mutant, set_c, topology, trajectory, QC, or MD-RRS authorization',
    'gpu_preflight': 'passed: CUDA JAX device required before inference',
    'jax_platforms': os.environ.get('JAX_PLATFORMS'),
    'xla_mem_fraction': os.environ.get('XLA_PYTHON_CLIENT_MEM_FRACTION'),
}
(out / 'provenance_preflight.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY

set +e
colabfold_batch \
  --msa-mode mmseqs2_uniref_env \
  --model-type alphafold2_ptm \
  --num-models 5 \
  --num-ensemble 1 \
  --num-seeds 3 \
  --num-relax 1 \
  --max-msa 512:1024 \
  "$INPUT" "$OUT"
CF_RC=$?
MODEL_COUNT=$(find "$OUT" -maxdepth 1 -type f \( -name '*.pdb' -o -name '*.cif' \) | wc -l)
SCORE_COUNT=$(find "$OUT" -maxdepth 1 -type f \( -name '*scores*.json' -o -name '*rank*.json' \) | wc -l)
export CF_RC MODEL_COUNT SCORE_COUNT
set -e

if [ "$CF_RC" -ne 0 ] || [ "$MODEL_COUNT" -lt 3 ] || [ "$SCORE_COUNT" -lt 3 ]; then
  python - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import json, os
out = Path(os.environ['OUT']).resolve()
p = out / 'provenance_preflight.json'
d = json.loads(p.read_text())
d.update({
    'status': 'COLABFOLD_ENSEMBLE_FAILED_MINIMUM_OUTPUT_GATE',
    'completed_utc': datetime.now(timezone.utc).isoformat(),
    'colabfold_returncode': int(os.environ.get('CF_RC', '1')),
    'model_count': int(os.environ.get('MODEL_COUNT', '0')),
    'score_count': int(os.environ.get('SCORE_COUNT', '0')),
    'minimum_output_rule': 'at least 3 coordinate files and 3 score/ranking JSON files',
})
(out / 'provenance_ensemble_failed.json').write_text(json.dumps(d, indent=2) + '\n')
PY
  exit 1
fi

python - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, os
out = Path(os.environ['OUT']).resolve()
manifest = json.loads((out / 'provenance_preflight.json').read_text())
files = [p for p in out.iterdir() if p.is_file() and p.name not in {'provenance_preflight.json', 'provenance_ensemble_completed.json', 'provenance_ensemble_failed.json'}]
manifest.update({
    'status': 'COLABFOLD_ENSEMBLE_COMPLETED',
    'completed_utc': datetime.now(timezone.utc).isoformat(),
    'model_count': int(os.environ['MODEL_COUNT']),
    'score_count': int(os.environ['SCORE_COUNT']),
    'outputs': {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
})
(out / 'provenance_ensemble_completed.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY
