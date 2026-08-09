#!/usr/bin/env bash
#SBATCH --job-name=p2_md_diag
#SBATCH --partition=production
#SBATCH --array=0-1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=24G
#SBATCH --time=12:00:00
#SBATCH --output=logs/p2_md_diag_%A_%a.out
#SBATCH --error=logs/p2_md_diag_%A_%a.err

# This is deliberately NOT the publication-grade reconstruction pipeline.
# It continues two historical systems only, without modifying MD_systems/.
# 201_PfDHFR and 214_PfCRT have non-empty NPT inputs and pass grompp smoke;
# 438_PfATP4 lacks NPT inputs; 164/4GM2 is PfClpR, not PfClpP.
set -euo pipefail

# SLURM may execute a copied batch script from /var/lib/slurm/slurmd.
# Never infer the project root from BASH_SOURCE in that context.
PROJECT_DIR="${P2_PROJECT_DIR:-${SLURM_SUBMIT_DIR:-}}"
if [[ -z "$PROJECT_DIR" || ! -d "$PROJECT_DIR/MD_systems" ]]; then
  echo "FAIL-CLOSED: set P2_PROJECT_DIR to the repository P2 directory" >&2
  exit 2
fi
SOURCE_ROOT="${PROJECT_DIR}/MD_systems"
RUN_ROOT="${PROJECT_DIR}/results/diagnostic_md_20260809"
GMX_BIN="${P2_GMX_BIN:-/home/nanaengo/miniforge3/envs/malaria_md/bin.AVX2_256/gmx_mpi}"
TARGET_NS="${P2_MD_TARGET_NS:-10}"
TEMPERATURE_K="310.15"
RUN_STAGE="initialization"

case "${SLURM_ARRAY_TASK_ID:-0}" in
  0) SYSTEM_NAME="201_PfDHFR" ;;
  1) SYSTEM_NAME="214_PfCRT" ;;
  *) echo "Unsupported array task: ${SLURM_ARRAY_TASK_ID:-unset}" >&2; exit 64 ;;
esac

if [[ "${P2_MD_DIAGNOSTIC_CONFIRM:-}" != "I_UNDERSTAND_HISTORICAL_DIAGNOSTIC" ]]; then
  echo "FAIL-CLOSED: set P2_MD_DIAGNOSTIC_CONFIRM=I_UNDERSTAND_HISTORICAL_DIAGNOSTIC" >&2
  exit 2
fi
[[ -x "$GMX_BIN" ]] || { echo "Missing GROMACS binary: $GMX_BIN" >&2; exit 2; }
[[ "$TARGET_NS" =~ ^[0-9]+([.][0-9]+)?$ ]] || { echo "Invalid P2_MD_TARGET_NS" >&2; exit 2; }

SOURCE_DIR="${SOURCE_ROOT}/${SYSTEM_NAME}"
OUT_DIR="${RUN_ROOT}/${SYSTEM_NAME}"
if [[ -e "$OUT_DIR" ]]; then
  echo "Refusing to reuse existing output directory: $OUT_DIR" >&2
  exit 2
fi
mkdir -p "$RUN_ROOT" "$OUT_DIR"
cp -a "${SOURCE_DIR}/." "$OUT_DIR/"

# Record a machine-readable exclusion and failure state even if GROMACS exits.
export P2_DIAG_OUT="$OUT_DIR"
export P2_DIAG_STAGE_FILE="$OUT_DIR/diagnostic_stage.txt"
trap 'rc=$?; if [[ "$rc" -ne 0 && -f "${P2_DIAG_OUT:-}/diagnostic_provenance.json" ]]; then python3 - "$rc" "${RUN_STAGE:-unknown}" <<'PY'
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
p = Path(os.environ["P2_DIAG_OUT"]) / "diagnostic_provenance.json"
try:
    d = json.loads(p.read_text())
    d.update({"status": "FAILED", "failed_utc": datetime.now(timezone.utc).isoformat(), "exit_code": int(sys.argv[1]), "failed_stage": sys.argv[2]})
    p.write_text(json.dumps(d, indent=2) + "\\n")
except Exception as exc:
    (Path(os.environ["P2_DIAG_OUT"]) / "diagnostic_failure.txt").write_text(f"status=FAILED\\nexit_code={sys.argv[1]}\\nstage={sys.argv[2]}\\nprovenance_update_error={exc}\\n")
PY
fi; exit "$rc"' EXIT

for required in npt.gro npt.cpt topol.top; do
  [[ -s "${OUT_DIR}/${required}" ]] || { echo "Missing required ${required}" >&2; exit 2; }
done

export P2_DIAG_SYSTEM="$SYSTEM_NAME"
export P2_DIAG_GMX="$GMX_BIN"
export P2_DIAG_SOURCE="$SOURCE_DIR"
export P2_DIAG_PROJECT="$PROJECT_DIR"
export P2_DIAG_LAUNCHER="$PROJECT_DIR/scripts/p2_historical_diagnostic_md.sbatch"
export P2_DIAG_NS="$TARGET_NS"
export P2_DIAG_TEMP="$TEMPERATURE_K"
export P2_DIAG_ARRAY="${SLURM_ARRAY_JOB_ID:-manual}_${SLURM_ARRAY_TASK_ID:-0}"
python3 - <<'PY'
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

out = Path(os.environ["P2_DIAG_OUT"])
def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()
def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

snapshot = {}
for path in sorted(out.rglob("*")):
    if path.is_file() and path.suffix.lower() in {".top", ".itp", ".prm", ".rtp", ".gro", ".cpt"}:
        snapshot[str(path.relative_to(out))] = file_sha(path)
launcher = Path(os.environ["P2_DIAG_LAUNCHER"])
payload = {
    "schema": "p2-historical-md-diagnostic/v2",
    "status": "RUNNING",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "cohort_id": "P2_PARENT_STUDY_MD_4",
    "system_name": os.environ["P2_DIAG_SYSTEM"],
    "source_input_class": "historical_parent_study_input",
    "source_directory": os.environ["P2_DIAG_SOURCE"],
    "source_force_field": "CHARMM36-jul2022 + GAFF2 (AM1-BCC via ACPYPE)",
    "excluded_systems": {
        "438_PfATP4": "NPT state absent; not submitted",
        "164_4GM2": "4GM2 is PfClpR, not PfClpP; not submitted",
    },
    "publication_grade_reconstruction": False,
    "target_identity_caveat": "Historical named parent system; not a new target validation.",
    "temperature_k": float(os.environ["P2_DIAG_TEMP"]),
    "duration_ns": float(os.environ["P2_DIAG_NS"]),
    "gromacs_binary": os.environ["P2_DIAG_GMX"],
    "slurm_array_id": os.environ["P2_DIAG_ARRAY"],
    "execution_confirmation": "P2_MD_DIAGNOSTIC_CONFIRM=I_UNDERSTAND_HISTORICAL_DIAGNOSTIC",
    "input_sha256": {name: sha(out / name) for name in ("npt.gro", "npt.cpt", "topol.top")},
    "topology_related_snapshot_sha256": snapshot,
    "launcher_sha256": file_sha(launcher) if launcher.is_file() else None,
    "gromacs_version": os.popen(f"{os.environ['P2_DIAG_GMX']} --version 2>/dev/null | head -1").read().strip(),
    "md_rrs_computed": False,
    "mmgbsa_computed": False,
    "independent_review": False,
}
(out / "diagnostic_provenance.json").write_text(json.dumps(payload, indent=2) + "\n")
PY

NSTEPS=$(awk -v ns="$TARGET_NS" 'BEGIN { printf "%.0f", ns*1000000/0.002 }')
cat > "${OUT_DIR}/diagnostic_production.mdp" <<EOF
; Historical-input diagnostic continuation; not publication-grade reconstruction.
integrator               = md
nsteps                   = ${NSTEPS}
dt                       = 0.002
nstxout-compressed       = 5000
nstenergy               = 1000
nstlog                  = 1000
continuation             = yes
constraints              = h-bonds
constraint_algorithm     = lincs
lincs_iter               = 1
lincs_order              = 4
cutoff-scheme            = Verlet
nstlist                  = 10
rlist                    = 1.2
rcoulomb                 = 1.2
rvdw                     = 1.2
coulombtype              = PME
pme_order                = 4
fourierspacing           = 0.16
tcoupl                   = V-rescale
tc-grps                  = System
tau_t                    = 0.1
ref_t                    = ${TEMPERATURE_K}
pcoupl                   = Parrinello-Rahman
pcoupltype               = isotropic
tau_p                    = 2.0
compressibility          = 4.5e-5
ref_p                    = 1.0
gen_vel                  = no
EOF

cd "$OUT_DIR"
RUN_STAGE="grompp"
"$GMX_BIN" grompp -f diagnostic_production.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o diagnostic.tpr
RUN_STAGE="mdrun"
"$GMX_BIN" mdrun -deffnm diagnostic -ntmpi 1 -ntomp "${SLURM_CPUS_PER_TASK:-8}" -nb gpu -pme gpu -v

python3 - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
out = Path(os.environ["P2_DIAG_OUT"])
p = out / "diagnostic_provenance.json"
d = json.loads(p.read_text())
d.update({
    "status": "COMPLETED_RAW_TRAJECTORY_REQUIRES_QC",
    "completed_utc": datetime.now(timezone.utc).isoformat(),
    "outputs": {name: (out / name).stat().st_size for name in ("diagnostic.tpr", "diagnostic.xtc", "diagnostic.edr", "diagnostic.log", "diagnostic.gro") if (out / name).is_file()},
})
p.write_text(json.dumps(d, indent=2) + "\n")
PY

echo "Completed diagnostic run for ${SYSTEM_NAME}; outputs: ${OUT_DIR}"
