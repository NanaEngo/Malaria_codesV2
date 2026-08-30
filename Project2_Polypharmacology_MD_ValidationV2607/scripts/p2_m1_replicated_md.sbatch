#!/usr/bin/env bash
#SBATCH --job-name=p2_m1_md
#SBATCH --partition=production
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=2-00:00:00
#SBATCH --array=0-11%1
#SBATCH --output=logs/p2_m1_md_%A_%a.log
#SBATCH --error=logs/p2_m1_md_%A_%a.err

set -euo pipefail

# GMXRC uses optional shell variables under nounset; source it before enabling
# strict undefined-variable handling. The conda activation is the canonical P2
# environment and is intentionally explicit.
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u

PROJECT=${SLURM_SUBMIT_DIR:?SLURM_SUBMIT_DIR is required}
cd "$PROJECT"

# M1 is intentionally limited to the PP-01 pillar systems. It must not be
# interpreted as a replacement for the canonical Set-C pilot or full-panel MD.
SYSTEMS=(
  PP-01_PfDHFR_WT
  PP-01_PfCRT_WT
  PP-01_PfDHFR_N51I
  PP-01_PfCRT_K76T
)
REPLICATES=(1 2 3)
SYS=${SYSTEMS[$((SLURM_ARRAY_TASK_ID / 3))]}
REP=${REPLICATES[$((SLURM_ARRAY_TASK_ID % 3))]}

# M1 inputs are the canonical prepared systems, while the completed pilot
# trajectories live under results/set_c_md/md_systems. Never infer a source root.
SRC_ROOT="$PROJECT/results/md_systems/set_c_preparation_20260812_v1"
SRC="$SRC_ROOT/$SYS"
# Use the canonical completed-equilibration checkpoint as the starting point,
# and copy its complete topology include closure into the new replicate root.
SRC_RUN="$SRC"
# The canonical equilibrated coordinates/checkpoint are at the system root;
# the root topol.top is the matching topology. Existing production run folders
# are not used as M1 input because their topology closure is incomplete.
OUT="$PROJECT/results/m1_replicated_md_20260829/$SYS/replicate_${REP}"
mkdir -p "$OUT" "$PROJECT/logs"

for required in "$SRC_RUN"/topol.top "$SRC_RUN"/npt.gro "$SRC_RUN"/npt.cpt; do
  [[ -s "$required" ]] || { echo "FATAL: missing required input: $required" >&2; exit 41; }
done
for include in $(grep -oE '^[[:space:]]*#include[[:space:]]+"[^"]+"' "$SRC_RUN/topol.top" | sed -E 's/.*"([^"]+)"/\1/' || true); do
  [[ -s "$SRC_RUN/$include" || -s "$SRC/$include" ]] || { echo "FATAL: missing topology include: $SRC_RUN/$include" >&2; exit 41; }
done

# Refuse accidental reuse of an existing output. This prevents silent mixing of
# seeds or trajectories across reruns.
[[ ! -e "$OUT/production.xtc" ]] || { echo "FATAL: output exists: $OUT" >&2; exit 42; }

SEED=$((26082900 + SLURM_ARRAY_TASK_ID + 1))
cp -a "$SRC_RUN"/* "$OUT/"
# Preserve the canonical include closure referenced by topol.top.
while read -r include; do
  include=${include#*\"}; include=${include%\"*}
  [[ -n "$include" ]] && { [ -e "$SRC_RUN/$include" ] && cp -a "$SRC_RUN/$include" "$OUT/$include" || cp -a "$SRC/$include" "$OUT/$include"; }
done < <(grep -E '^[[:space:]]*#include[[:space:]]+"[^"]+"' "$SRC_RUN/topol.top" || true)
cp "$SRC/forcefield_manifest.json" "$OUT/forcefield_manifest.json" 2>/dev/null || true

cat > "$OUT/production.mdp" <<EOF
integrator              = md
nsteps                  = 50000000
dt                      = 0.002
; 100 ns production; independent velocity seed per replicate
continuation            = yes
ref-t                  = 310.15
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
pme-order               = 4
fourierspacing          = 0.16
nstlist                 = 20
nstenergy               = 1000
nstlog                  = 1000
nstxout-compressed      = 5000
compressed-x-grps       = System
nstcheckpoint           = 50000
refcoord-scaling        = com
EOF

gmx_mpi grompp -f "$OUT/production.mdp" -c "$OUT/npt.gro" -p "$OUT/topol.top" -t "$OUT/npt.cpt" -o "$OUT/production.tpr" -po "$OUT/production.mdpout" -maxwarn 0

gmx_mpi mdrun -deffnm "$OUT/production" -s "$OUT/production.tpr" \
  -nb gpu -pme gpu -bonded cpu -update cpu \
  -ntomp "$SLURM_CPUS_PER_TASK" -gpu_id 0 \
  -pin on -cpt 15 -cpnum -append -x "$OUT/production.xtc" \
  -c "$OUT/production.gro" -e "$OUT/production.edr" -g "$OUT/production.log"

[[ -s "$OUT/production.xtc" && -s "$OUT/production.tpr" && -s "$OUT/production.gro" ]] || { echo "FATAL: incomplete production output" >&2; exit 43; }
if grep -Eiq 'Fatal error|Segmentation fault|LINCS WARNING|NaN|nan' "$OUT/production.log"; then
  echo "FATAL: runtime integrity marker in production log" >&2
  exit 44
fi

# The canonical QC script is an aggregate scanner and requires the exported
# canonical Set-C root; per-replicate QC is performed by the post-production
# gate after all M1 trajectories are complete. Do not invoke it with --input-root.
python - <<PY
import json
from pathlib import Path
out = Path("$OUT")
manifest = {
  "status": "M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW",
  "system": "$SYS", "replicate": $REP, "seed": $SEED,
  "duration_ns": 100.0, "environment": "malaria_md",
  "gpu_path": "-nb gpu -pme gpu -bonded cpu -update cpu",
  "interpretation": "replicated structural robustness analysis; not affinity or resistance validation"
}
(out / "m1_provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY
