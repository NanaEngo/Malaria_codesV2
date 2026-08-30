#!/usr/bin/env bash
#SBATCH --job-name=p2_m1_cont
#SBATCH --partition=production
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
# Continuation of the interrupted M1 replicate_1 (PP-01_PfDHFR_WT) from the
# latest checkpoint to the full 100 ns encoded in production.tpr
# (nsteps = 50,000,000). The previous job 15711_0 ran under a 48 h inherited
# limit and was stopped at ~23.4 ns (step 11,707,500) by explicit decision
# (DAR P2 §14). The tpr is unchanged, so mdrun -cpi continues to 100 ns total.
#SBATCH --time=4-00:00:00
#SBATCH --array=0-0%1
#SBATCH --output=logs/p2_m1_cont_%A_%a.log
#SBATCH --error=logs/p2_m1_cont_%A_%a.err

set -euo pipefail

set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u

PROJECT=${SLURM_SUBMIT_DIR:?SLURM_SUBMIT_DIR is required}
cd "$PROJECT"

# --- GPU anti-competition guard (same policy as the original M1 launcher) ---
if pgrep -f 'gmx.*mdrun' >/dev/null 2>&1; then
  echo "FATAL: another GROMACS mdrun is already active; refusing to share the single GPU (exit 40)." >&2
  pgrep -af 'gmx.*mdrun' >&2 2>/dev/null || true
  exit 40
fi

OUT="$PROJECT/results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1"
for required in "$OUT"/production.tpr "$OUT"/production.xtc; do
  [[ -s "$required" ]] || { echo "FATAL: missing required input: $required" >&2; exit 41; }
done

# Latest checkpoint = restart point. Refuse if none exists. The selection must
# NOT use a pipe (e.g. `ls | head -1`): under `set -o pipefail` the producer is
# killed by SIGPIPE when head closes early (observed exit 141 on job 15714).
# A numeric loop over the glob is pipe-free and robust to zero-padding.
CHECKPOINT=""
for _cpt in "$OUT"/production_step*.cpt; do
  [[ -f "$_cpt" ]] || continue
  if [[ -z "$CHECKPOINT" ]]; then
    CHECKPOINT="$_cpt"; continue
  fi
  _s1=${_cpt##*_step}; _s1=${_s1%.cpt}
  _s2=${CHECKPOINT##*_step}; _s2=${_s2%.cpt}
  [[ "$_s1" =~ ^[0-9]+$ && "$_s2" =~ ^[0-9]+$ ]] || continue
  (( 10#$_s1 > 10#$_s2 )) && CHECKPOINT="$_cpt"
done
[[ -n "$CHECKPOINT" && -s "$CHECKPOINT" ]] || { echo "FATAL: no checkpoint found under $OUT" >&2; exit 41; }
echo "continuation checkpoint: $CHECKPOINT"

# Refuse accidental reuse: a completed 100 ns run has a final production.gro.
[[ ! -s "$OUT/production.gro" ]] || { echo "FATAL: production.gro already exists (run already complete): $OUT" >&2; exit 42; }

gmx_mpi mdrun -deffnm "$OUT/production" -s "$OUT/production.tpr" \
  -cpi "$CHECKPOINT" \
  -nb gpu -pme gpu -bonded cpu -update cpu \
  -ntomp "$SLURM_CPUS_PER_TASK" -gpu_id 0 \
  -pin on -append -x "$OUT/production.xtc" \
  -c "$OUT/production.gro" -e "$OUT/production.edr" -g "$OUT/production.log"

[[ -s "$OUT/production.xtc" && -s "$OUT/production.tpr" && -s "$OUT/production.gro" ]] || { echo "FATAL: incomplete production output" >&2; exit 43; }
if grep -Eiq 'Fatal error|Segmentation fault|LINCS WARNING' "$OUT/production.log"; then
  echo "FATAL: runtime integrity marker in production log" >&2
  exit 44
fi

# Prune intermediate checkpoints, keep only the most recent (pipe-free
# selection, same SIGPIPE rationale as above).
LATEST=""
for _cpt in "$OUT"/production_step*.cpt; do
  [[ -f "$_cpt" ]] || continue
  if [[ -z "$LATEST" ]]; then
    LATEST="$_cpt"; continue
  fi
  _s1=${_cpt##*_step}; _s1=${_s1%.cpt}
  _s2=${LATEST##*_step}; _s2=${_s2%.cpt}
  [[ "$_s1" =~ ^[0-9]+$ && "$_s2" =~ ^[0-9]+$ ]] || continue
  (( 10#$_s1 > 10#$_s2 )) && LATEST="$_cpt"
done
if [[ -n "$LATEST" ]]; then
  for c in "$OUT"/production_step*.cpt; do [[ "$c" != "$LATEST" ]] && rm -f "$c"; done
  echo "pruned intermediate checkpoints; retained $LATEST"
fi

# Post-completion provenance update: re-run the post-kill QC gate with the 100 ns
# target; it will upgrade the manifest to M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW
# and record the real achieved duration, QC values, and termination cause.
conda activate malaria_md
python "$PROJECT/scripts/p2_m1_postkill_qc.py" \
  --replicate "$OUT" --target-ns 100.0 --bound-angstrom 5.0 \
  --min-bound-fraction 0.10 --max-frames 3000
