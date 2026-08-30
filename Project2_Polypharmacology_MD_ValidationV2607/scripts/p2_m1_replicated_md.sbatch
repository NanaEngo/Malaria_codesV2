#!/usr/bin/env bash
#SBATCH --job-name=p2_m1_md
#SBATCH --partition=production
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
# Measured M1 throughput on the pilot node is ~1.2 ns/h (13.9 ns / ~11.5 h on
# the 29 Aug partial run). 100 ns therefore needs ~83 h of wallclock per task,
# so a 2-day window would be killed by the SLURM time limit before completion.
# A 4-day window (96 h) fits 100 ns with margin at the observed rate; concurrency
# is kept at one task (%1) per the declared GPU policy.
#SBATCH --time=4-00:00:00
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

# --- GPU anti-competition guard -------------------------------------------
# The M1 node exposes a SINGLE GPU. Launching a new mdrun while another
# production mdrun is already active would split the GPU across two runs,
# corrupting the new trajectory and slowing the existing production. Fail
# closed before any work is begun if any gmx mdrun process is already running.
if pgrep -f 'gmx.*mdrun' >/dev/null 2>&1; then
  echo "FATAL: another GROMACS mdrun is already active; refusing to share the single GPU (exit 40)." >&2
  pgrep -af 'gmx.*mdrun' >&2 2>/dev/null || true
  exit 40
fi
# ---------------------------------------------------------------------------

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
LOOP_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Copy only the MINIMAL production input closure into this replicate root.
# A full `cp -a` of the source would drag in intermediate trajectories
# (em*.trr, nvt.xtc, npt.xtc, *.edr), the ~2.7 GB historical `runs/` folders,
# and redundant coordinate files for every replicate (12x duplication). That is
# the root cause of the M1 disk overrun (~12 x ~6 GB unused). M1 requires only
# topol.top, its force-field/topology include closure, npt.gro, npt.cpt, the
# ligand ITP (already covered by the closure), and the posre restraint ITPs.
cp "$SRC_RUN/topol.top" "$OUT/topol.top"
cp "$SRC_RUN/npt.gro" "$OUT/npt.gro"
cp "$SRC_RUN/npt.cpt" "$OUT/npt.cpt"
# Force-field and topology includes referenced by topol.top.
while read -r include; do
  include=${include#*\"}; include=${include%\"*}
  [[ -n "$include" ]] || continue
  if [[ -e "$SRC_RUN/$include" ]]; then
    mkdir -p "$OUT/$(dirname "$include" 2>/dev/null || echo .)"
    cp -a "$SRC_RUN/$include" "$OUT/$include"
  else
    mkdir -p "$OUT/$(dirname "$include" 2>/dev/null || echo .)"
    cp -a "$SRC/$include" "$OUT/$include"
  fi
done < <(grep -E '^[[:space:]]*#include[[:space:]]+"[^"]+"' "$SRC_RUN/topol.top" || true)
# posre restraint ITPs are referenced by the topology itps; copy them explicitly.
for f in "$SRC_RUN"/posre_*.itp; do [[ -e "$f" ]] && cp -a "$f" "$OUT/"; done
cp "$SRC/forcefield_manifest.json" "$OUT/forcefield_manifest.json" 2>/dev/null || true
cp "$SRC/system_manifest.json" "$OUT/system_manifest.json" 2>/dev/null || true
cp "$SRC/pre_equilibration_audit.json" "$OUT/pre_equilibration_audit.json" 2>/dev/null || true

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
  -pin on -append -x "$OUT/production.xtc" \
  -c "$OUT/production.gro" -e "$OUT/production.edr" -g "$OUT/production.log"

[[ -s "$OUT/production.xtc" && -s "$OUT/production.tpr" && -s "$OUT/production.gro" ]] || { echo "FATAL: incomplete production output" >&2; exit 43; }
if grep -Eiq 'Fatal error|Segmentation fault|LINCS WARNING|NaN|nan' "$OUT/production.log"; then
  echo "FATAL: runtime integrity marker in production log" >&2
  exit 44
fi

# Prune intermediate numbered checkpoints. They are restart/backup artifacts;
# the final trajectory (production.xtc) and the manifest are the canonical
# products. Keeping only the single most recent checkpoint bounds the disk
# footprint to ~tens of MB per replicate instead of ~2.4 GB of accumulated
# step-*.cpt files across a 100 ns run.
if compgen -G "$OUT"/production_step*.cpt > /dev/null 2>&1; then
  latest=$(ls -1t "$OUT"/production_step*.cpt | head -1)
  for c in "$OUT"/production_step*.cpt; do [[ "$c" != "$latest" ]] && rm -f "$c"; done
  echo "pruned intermediate checkpoints; retained $latest"
fi

# The canonical QC script is an aggregate scanner and requires the exported
# canonical Set-C root; per-replicate QC is performed by the post-production
# gate after all M1 trajectories are complete. Do not invoke it with --input-root.
python - <<PY
import hashlib, json
from pathlib import Path
out = Path("$OUT")
cwd = Path("$PWD")

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

inputs = {}
req = ["topol.top", "npt.cpt", "npt.gro", "production.mdp", "production.tpr"]
for r in req:
    p = out / r
    try:
        inputs[r] = {"sha256": sha256(p), "size_bytes": p.stat().st_size}
    except FileNotFoundError:
        inputs[r] = "MISSING"

manifest = {
  "status": "M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW",
  "system": "$SYS", "replicate": $REP, "seed": $SEED,
  "duration_ns": 100.0, "environment": "malaria_md",
  "gpu_path": "-nb gpu -pme gpu -bonded cpu -update cpu",
  "source_root": "results/md_systems/set_c_preparation_20260812_v1",
  "wallclock_start": "$LOOP_START",
  "wallclock_end": None,
  "first_last_step": None,
  "inputs": inputs,
  "interpretation": "replicated structural robustness analysis; not affinity or resistance validation"
}
(out / "m1_provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("wrote m1_provenance.json")
PY
