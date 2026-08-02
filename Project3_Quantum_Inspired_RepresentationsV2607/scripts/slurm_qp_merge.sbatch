#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# Merge QP Array Results — runs after slurm_qp_search_array completes
#
# Usage:
#   sbatch --dependency=afterok:<ARRAY_JOBID> /tmp/slurm_qp_merge.sbatch
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p3_qp_merge
#SBATCH --output=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qp_merge_%j.log
#SBATCH --error=/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_qp_merge_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --partition=production

set -euo pipefail

PYTHON="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607"
RESULTS_DIR="${PROJECT_DIR}/results"

echo "═══ Merge QP Array Results ═══"
echo "  Start: $(date -u -Iseconds)"

# ── Combine all per-task CSVs into one ──────────────────────────────
# Each per-task file has the same header. We concatenate header from
# first file, then append all data rows.
PER_TASK_FILES=("${RESULTS_DIR}"/p3_qp_sweep_array_*.csv)
TOTAL_FILES=${#PER_TASK_FILES[@]}

if [ "$TOTAL_FILES" -eq 0 ]; then
  echo "ERROR: No per-task CSV files found in ${RESULTS_DIR}/"
  ls -la "${RESULTS_DIR}/" | grep 'p3_qp' || true
  exit 1
fi

if [ "$TOTAL_FILES" -ne 60 ]; then
  echo "WARNING: Only $TOTAL_FILES/60 tasks completed! Missing combos will be absent from final results." >&2
fi

FIRST=1
for f in "${PER_TASK_FILES[@]}"; do
  if [ ! -f "$f" ]; then continue; fi
  if [ "$FIRST" -eq 1 ]; then
    cat "$f" > "${RESULTS_DIR}/p3_quantum_params_sweep.csv"
    FIRST=0
  else
    tail -n +2 "$f" >> "${RESULTS_DIR}/p3_quantum_params_sweep.csv"
  fi
  rm -f "$f"
done

COUNT=$(tail -n +2 "${RESULTS_DIR}/p3_quantum_params_sweep.csv" | wc -l)
echo "  Merged ${COUNT} results (${TOTAL_FILES}/60 tasks) → p3_quantum_params_sweep.csv"

if [ "$TOTAL_FILES" -lt 60 ]; then
  echo "  ⚠️  Missing tasks: tasks requiring re-submission can be found via:"
  echo "      squeue -j ${SLURM_JOB_ID##*_}  # original array job"
fi

# ── Print summary ───────────────────────────────────────────────────
"${PYTHON}" -c "
import pandas as pd
df = pd.read_csv('${RESULTS_DIR}/p3_quantum_params_sweep.csv')
best = df.loc[df['auc'].idxmax()]
print(f'\n🏆  BEST PARAMETERS:')
print(f'     bond_dim  = {int(best[\"bond_dim\"])}')
print(f'     n_repeats = {int(best[\"n_repeats\"])}')
print(f'     n_kpca    = {int(best[\"n_kpca\"])}')
print(f'     AUC       = {best[\"auc\"]:.4f} ± {best[\"auc_std\"]:.4f}')
print(f'\nTop 5:')
top5 = df.sort_values('auc', ascending=False).head(5)
for i, (_, row) in enumerate(top5.iterrows(), 1):
    print(f'  {i}. bond_dim={int(row[\"bond_dim\"])}, n_repeats={int(row[\"n_repeats\"])}, '
          f'n_kpca={int(row[\"n_kpca\"])} → AUC = {row[\"auc\"]:.4f} ± {row[\"auc_std\"]:.4f}')
"

echo "═══ Merge complete: $(date -u -Iseconds) ═══"
