#!/bin/bash
#SBATCH --job-name=p2_pfcrt_wit
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/p2_pfcrt_wit_%j.log
#SBATCH --error=logs/p2_pfcrt_wit_%j.err

# Activate Conda before nounset: the cluster's GROMACS hook references
# optional variables during initialization.
set -eo pipefail
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u

# Fail closed: this witness must use OpenMM CUDA, never a silent CPU fallback.
python - <<'PY'
from openmm import Platform
import os
print('CUDA_VISIBLE_DEVICES=', os.environ.get('CUDA_VISIBLE_DEVICES', 'unset'))
print('OpenMM platforms=', [Platform.getPlatform(i).getName() for i in range(Platform.getNumPlatforms())])
if not any(Platform.getPlatform(i).getName() == 'CUDA' for i in range(Platform.getNumPlatforms())):
    raise SystemExit('FAIL-CLOSED: OpenMM CUDA platform unavailable')
PY

PROJECT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
MODEL=$(find "$PROJECT/results/md_systems/pfcrt_colabfold_gpu_ensemble_20260811" -maxdepth 1 -name '*relaxed_rank_001*.pdb' | sort | head -1)
FASTA="$PROJECT/results/md_systems/pfcrt_sequence_reference_20260811/W7FI62.fasta"
OUT="$PROJECT/results/md_systems/pfcrt_fullmodel_witness_openmm_retry4_20260811"
ENSEMBLE_MANIFEST="$PROJECT/results/md_systems/pfcrt_colabfold_gpu_ensemble_20260811/provenance_ensemble_completed.json"
[[ -n "$MODEL" && -f "$MODEL" ]] || { echo 'Missing complete relaxed model' >&2; exit 2; }
[[ -f "$ENSEMBLE_MANIFEST" ]] || { echo 'Missing ensemble completion manifest' >&2; exit 5; }
[[ -f "$FASTA" ]] || { echo 'Missing W7FI62 FASTA' >&2; exit 3; }
[[ ! -e "$OUT" ]] || { echo "Refusing existing output root: $OUT" >&2; exit 4; }
# The Python witness creates the fresh output directory itself; do not create
# it here because the script uses exist_ok=False as a stale-output guard.

python scripts/p2_pfcrt_fullmodel_witness_openmm.py \
  --model "$MODEL" \
  --reference-fasta "$FASTA" \
  --ensemble-manifest "$ENSEMBLE_MANIFEST" \
  --output-dir "$OUT" \
  --steps 10000 \
  --temperature-k 310.15
