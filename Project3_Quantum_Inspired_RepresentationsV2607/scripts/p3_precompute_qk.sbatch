#!/bin/bash
#SBATCH --job-name=p3_precompute_qk
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_precompute_qk_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_precompute_qk_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=5G
#SBATCH --time=24:00:00
#SBATCH --partition=production
#SBATCH --export=ALL

set -euo pipefail

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1

PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"

cd "${PROJECT_DIR}"

echo "P3 QKS Precompute (n=5000) — kernel matrix only"
echo "Start: $(date -u -Iseconds)"
echo "CPUs: $(nproc), RAM: $(free -g | awk '/Mem/{print $2}') GB"

"${PYTHON}" -c "
import sys, time, json, pickle
import numpy as np
from pathlib import Path

sys.path.insert(0, '${PROJECT_DIR}/scripts')
from p3_hybrid_benchmark import ecfp4, load_activity, _precompute_qk_all

RESULTS = Path('${PROJECT_DIR}/results')
OUT = RESULTS / 'p3_qk_precomputed_5000.npz'
CKPT = RESULTS / 'p3_qk_precompute_checkpoint.json'

# Load data
print('Loading activity data...')
df = load_activity()
smiles = df['smiles'].tolist()
y = df['activity'].values

# Subsample to 5000
np.random.seed(42)
n = min(5000, len(smiles))
idx = np.random.choice(len(smiles), n, replace=False)
smiles_n = [smiles[i] for i in idx]
y_n = y[idx]

print(f'Subsampled: {n} molecules, {y_n.sum()} active ({y_n.mean():.1%})')

# ECFP4
print('Computing ECFP4...')
X_ecfp = ecfp4(smiles_n)
print(f'  Shape: {X_ecfp.shape}')

# Precompute kernel (the big step)
print('Precomputing QKS kernel matrix...')
t0 = time.perf_counter()
QK_data = _precompute_qk_all(
    X_ecfp,
    n_qubits=6,
    n_repeats=1,
    block_size=200,
    n_jobs=4,
    prefer_cpu=True,
    use_jax=False,
    dtype=np.float64,
)
elapsed = time.perf_counter() - t0
print(f'Total precompute: {elapsed:.1f}s ({elapsed/60:.1f} min)')

# Save kernel matrix
K_psd = QK_data['K_psd']
np.savez_compressed(OUT, K_psd=K_psd, y=y_n, smiles=np.array(smiles_n, dtype=object))
print(f'Saved: {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)')

# Save checkpoint
with open(CKPT, 'w') as f:
    json.dump({
        'n_molecules': n,
        'kernel_shape': list(K_psd.shape),
        'time_s': elapsed,
        'output': str(OUT),
        'status': 'complete',
    }, f, indent=2)
print(f'Checkpoint: {CKPT}')
print('PRECOMPUTE COMPLETE')
"

echo "End: $(date -u -Iseconds)"
