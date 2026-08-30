#!/usr/bin/env bash
# p2_m1_tune_benchmark.sh
# ----------------------------------------------------------------------------
# M1 mdrun calibration. Measures ns/day for a set of -(nb/pme/bonded/update)
# and -ntomp configurations on the PUBLICATION system, so the 11 remaining M1
# replicates use the fastest configuration.
#
# IMPORTANT RESOURCE RULE
#   This project node exposes a single GPU (RTX A4000). Running this script
#   while replicate_1 production is active would COMPETE for that GPU, corrupt
#   the measurement AND slow the running production (~11 h invested). Execute
#   this ONLY when the GPU is free (e.g. at the replicate_1 -> replicate_2
#   transition), never concurrently with an active production mdrun.
#
# Usage:
#   bash scripts/p2_m1_tune_benchmark.sh
#
# Output: prints the xtc-log-derived ns/day for each config and appends a row
#   to $TUNE_DIR/benchmark_summary.tsv. The best config is printed at the end.
# ----------------------------------------------------------------------------
set -euo pipefail

PROJECT="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$PROJECT"

# --- GPU anti-competition guard ---
# Single-GPU node: never benchmark (or run) while another mdrun is active.
if pgrep -f 'gmx.*mdrun' >/dev/null 2>&1; then
  echo "FATAL: another GROMACS mdrun is active; the benchmark must run only when the GPU is free. Refusing to start (exit 40)." >&2
  pgrep -af 'gmx.*mdrun' >&2 2>/dev/null || true
  exit 40
fi
# ---------------------------------

source /home/nanaengo/miniforge3/etc/profile.d/conda.sh || true
set +u; conda activate malaria_md; set -u

TUNE_DIR="results/m1_tune_benchmark_$(date +%Y%m%d)"
mkdir -p "$TUNE_DIR"

# Reference .tpr from the currently-prepared replicate_1 system. Recompute the
# tpr fresh here so the benchmark is independent of the running production's
# checkpoint file.
SRC="results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1"
REF_TPR="$SRC/production.tpr"
[[ -s "$REF_TPR" ]] || { echo "FATAL: no reference tpr: $REF_TPR" >&2; exit 41; }

# Short-run tpr for benchmarking: also acts as a guard that the config runs
# without fatal errors on the real system. nsteps=200000 => 400 ps per run.
# We grompp on the existing topology/inputs to keep the field identical.
TUNE_TPR="$TUNE_DIR/bench.tpr"
if [[ ! -s "$TUNE_TPR" ]]; then
  cat > "$TUNE_DIR/bench.mdp" <<'EOF'
integrator              = md
nsteps                  = 200000
dt                      = 0.002
continuation            = yes
ref-t                   = 310.15
tc-grps                 = System
tau-t                   = 1.0
tcoupl                  = V-rescale
pcoupl                  = Parrinello-Rahman
pcoupltype              = isotropic
tau-p                   = 5.0
compressibility         = 4.5e-5
ref-p                   = 1.0
constraints             = h-bonds
constraint-algorithm    = lincs
lincs-iter              = 2
lincs-order             = 4
cutoff-scheme           = Verlet
rlist                   = 1.2
rvdw                    = 1.2
rcoulomb                = 1.2
coulombtype             = PME
fourierspacing          = 0.16
nstlist                 = 20
nstenergy               = 1000
nstlog                  = 1000
nstxout-compressed      = 0
nstcheckpoint           = 0
EOF
  gmx_mpi grompp -f "$TUNE_DIR/bench.mdp" -c "$SRC/npt.gro" -p "$SRC/topol.top" \
    -t "$SRC/npt.cpt" -o "$TUNE_TPR" -po "$TUNE_DIR/bench_out.mdp" -maxwarn 0
fi

# Candidate configurations. -update gpu is intentionally absent: the system
# cannot use GPU-resident update (update groups unavailable, per production.log).
CONFIGS=(
  "8   gpu gpu cpu cpu"
  "12  gpu gpu cpu cpu"
  "16  gpu gpu cpu cpu"
  "16  gpu gpu gpu cpu"
  "20  gpu gpu cpu cpu"
  "20  gpu gpu gpu cpu"
  "24  gpu gpu cpu cpu"
  "24  gpu gpu gpu cpu"
)

declare -A RESULT
echo -e "ntomp\tnb\tpme\tbonded\tupdate\tns_day" | tee "$TUNE_DIR/benchmark_summary.tsv"

for cfg in "${CONFIGS[@]}"; do
  read -r NTOMP NB PME BONDED UPDATE <<< "$cfg"
  OUT="$TUNE_DIR/t${NTOMP}_${BONDED}"
  mkdir -p "$OUT"
  rm -f "$OUT"/*.{log,cpt,edr,xtc,gro} 2>/dev/null || true
  t0=$(date +%s)
  gmx_mpi mdrun -deffnm "$OUT/bench" -s "$TUNE_TPR" \
    -nb "$NB" -pme "$PME" -bonded "$BONDED" -update "$UPDATE" \
    -ntomp "$NTOMP" -gpu_id 0 -pin on \
    -x "$OUT/bench.xtc" -c "$OUT/bench.gro" -e "$OUT/bench.edr" -g "$OUT/bench.log" \
    >> "$TUNE_DIR/tune.out" 2>&1 || { echo "RUN_FAILED t${NTOMP}_${BONDED}" | tee -a "$TUNE_DIR/benchmark_summary.tsv"; continue; }
  t1=$(date +%s)
  NSDAY=$(grep -iE 'Performance:' "$OUT/bench.log" | tail -1 | grep -oE '[0-9.]+ ns/day' || echo "")
  # fallback: compute from wall time and known length (400 ps) if no perf line
  if [[ -z "$NSDAY" ]]; then
    NSDAY=$(awk -v dt="$((t1-t0))" 'BEGIN{printf "%.2f", 400e-6 / (dt/86400.0)}')
  fi
  RESULT["$NTOMP/$BONDED"]="$NSDAY"
  echo -e "$NTOMP\t$NB\t$PME\t$BONDED\t$UPDATE\t$NSDAY" | tee -a "$TUNE_DIR/benchmark_summary.tsv"
done

best=""
bestv=0
for k in "${!RESULT[@]}"; do
  v=$(echo "${RESULT[$k]}" | grep -oE '^[0-9.]+')
  if awk -v a="$v" -v b="$bestv" 'BEGIN{exit !(a>b)}'; then best="$k"; bestv="$v"; fi
done
echo
echo "BEST CONFIG: -ntomp ${best%/*} -bonded ${best#*/}  (${bestv} ns/day)"
echo "Apply by editing scripts/p2_m1_replicated_md.sbatch: -ntomp and --cpus-per-task to match, and -bonded accordingly."