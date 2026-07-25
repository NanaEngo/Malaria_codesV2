#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  P4 — Fragment vocabulary ablation study
#  Re-runs the ablation with the 108-fragment (expanded) vocabulary to
#  verify/replace the "108→10 degrades reward by 0.14" claim inherited
#  from the old 33-fragment ablation.
#
#  Usage:
#    sbatch --array=0-29%8 p4_ablation_fragments.sbatch
#
#  Array mapping (30 tasks = 3 fragment_sets × 10 seeds):
#    Tasks  0–9:  fragment_set="all"           (108 fragments, baseline)
#    Tasks 10–19: fragment_set="aromatic_only" (8 fragments)
#    Tasks 20–29: fragment_set="minimal"       (5 fragments)
#
#  Expected runtime: ~6 h for full 30-task array (8 concurrent).
# ═══════════════════════════════════════════════════════════════════════
#SBATCH --job-name=p4_ablation
#SBATCH --output=logs/slurm/p4_ablation_%a_%j.log
#SBATCH --error=logs/slurm/p4_ablation_%a_%j.log
#SBATCH --time=08:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --partition=production

set -euo pipefail

# ── Load environment ──────────────────────────────────────────────────
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate malaria_md

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# ── Map task ID to fragment_set + seed ────────────────────────────────
TASK_ID="${SLURM_ARRAY_TASK_ID:-0}"

if   (( TASK_ID < 10 )); then
    FRAGMENT_SET="all"
    SEED="$TASK_ID"
elif (( TASK_ID < 20 )); then
    FRAGMENT_SET="aromatic_only"
    SEED=$(( TASK_ID - 10 ))
else
    FRAGMENT_SET="minimal"
    SEED=$(( TASK_ID - 20 ))
fi

# ── Fixed parameters (match main benchmark) ───────────────────────────
INITIAL_SMILES="C"
MAX_STEPS=8
N_ITERATIONS=1000
C_PUCT=5.0

OUTPUT_CSV="results/ablation/p4_ablation_${FRAGMENT_SET}_seed_${SEED}.csv"
mkdir -p "$(dirname "$OUTPUT_CSV")"

echo "═══ P4 Fragment Ablation — $(date -u -Iseconds) ═══"
echo "  Task ID:         ${TASK_ID}"
echo "  Fragment set:    ${FRAGMENT_SET}"
echo "  Seed:            ${SEED}"
echo "  Initial SMILES:  ${INITIAL_SMILES}"
echo "  Max steps:       ${MAX_STEPS}"
echo "  Iterations:      ${N_ITERATIONS}"
echo "  PUCT c:          ${C_PUCT}"
echo "  Output:          ${OUTPUT_CSV}"
echo "  Host:            $(hostname)"
echo "════════════════════════════════════════════════════"

python3 scripts/p4_mcts_run.py \
    --initial-smiles "${INITIAL_SMILES}" \
    --max-steps "${MAX_STEPS}" \
    --n-iterations "${N_ITERATIONS}" \
    --fragment-set "${FRAGMENT_SET}" \
    --c-puct "${C_PUCT}" \
    --seed "${SEED}" \
    --output-csv "${OUTPUT_CSV}" \
    2>&1

echo "═══ Task ${TASK_ID} complete: $(date -u -Iseconds) ═══"
