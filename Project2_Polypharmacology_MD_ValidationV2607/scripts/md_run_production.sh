#!/usr/bin/env bash
# P2 targeted parent-lead MD runner.
#
# IMPORTANT: This runner is not the source of the already-completed 10 ns
# parent-study trajectories. It is a guarded future-run utility. It does not
# launch GROMACS unless --execute AND P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND are
# supplied explicitly.
#
# Usage:
#   bash scripts/md_run_production.sh [--dry-run] [--execute] [complex|all] [GPU_ID]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"
# shellcheck source=md_execution_guard.sh
source "${SCRIPT_DIR}/md_execution_guard.sh"

md_guard_parse "$@" || {
    echo "Usage: $0 [--dry-run|--execute] [complex|all] [GPU_ID]" >&2
    exit 64
}
POSITIONAL=("${MD_GUARD_POSITIONAL[@]}")
COMPLEX="${POSITIONAL[0]:-all}"
GPU_ID="${POSITIONAL[1]:-auto}"
GMX_BIN="${P2_GMX_BIN:-gmx}"
TARGET_NS="${P2_MD_TARGET_NS:-10}"
REPLICATES="${P2_MD_REPLICATES:-1}"
TEMPERATURE_K="310.15"

if ! [[ "$TARGET_NS" =~ ^[0-9]+([.][0-9]+)?$ ]] || ! [[ "$REPLICATES" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: P2_MD_TARGET_NS must be numeric and P2_MD_REPLICATES a positive integer." >&2
    exit 2
fi

if [[ "$COMPLEX" == "all" ]]; then
    COMPLEXES=(201_DHFR 438_ATP4 164_ClpP 214_CRT)
else
    COMPLEXES=("$COMPLEX")
fi

if [[ "$MD_GUARD_EXECUTE" != "1" ]]; then
    md_guard_print_plan "md_run_production.sh" \
        "targeted parent-lead production MD (${TARGET_NS} ns, ${REPLICATES} replicate(s), ${TEMPERATURE_K} K) for ${COMPLEXES[*]}"
    exit 0
fi
md_guard_require_authorization || exit $?

# This guarded runner is intentionally strict: a partial multi-system run is
# not a valid four-system comparison and must stop at the first failure.
for complex_name in "${COMPLEXES[@]}"; do
    md_guard_check_parent_system "$complex_name"
    system_dir="${MD_DIR}/${complex_name}"
    [[ -d "$system_dir" ]] || { echo "ERROR: missing system directory: $system_dir" >&2; exit 1; }
    [[ -s "$system_dir/npt.gro" ]] || { echo "ERROR: missing npt.gro: $system_dir" >&2; exit 1; }
    [[ -s "$system_dir/npt.cpt" ]] || { echo "ERROR: missing npt.cpt: $system_dir" >&2; exit 1; }
    [[ -s "$system_dir/topol.top" ]] || { echo "ERROR: missing topol.top: $system_dir" >&2; exit 1; }
    md_guard_validate_forcefield_manifest "$system_dir"
done

export P2_RUN_MANIFEST_DIR="$MD_DIR"
export P2_RUN_COMPLEXES="${COMPLEXES[*]}"
export P2_RUN_TARGET_NS="$TARGET_NS"
export P2_RUN_REPLICATES="$REPLICATES"
export P2_RUN_TEMPERATURE_K="$TEMPERATURE_K"
export P2_RUN_GMX_BIN="$GMX_BIN"
export P2_RUNNER_PATH="${BASH_SOURCE[0]}"
python3 - <<'PY'
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["P2_RUN_MANIFEST_DIR"])
complexes = os.environ["P2_RUN_COMPLEXES"].split()

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

systems = []
for name in complexes:
    system_dir = root / name
    systems.append({
        "system_name": name,
        "topology_sha256": sha256(system_dir / "topol.top"),
        "coordinates_sha256": sha256(system_dir / "npt.gro"),
        "checkpoint_sha256": sha256(system_dir / "npt.cpt"),
    })
manifest = {
    "schema_version": 2,
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "authorization": "P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND",
    "runner": "md_run_production.sh",
    "runner_sha256": sha256(Path(os.environ["P2_RUNNER_PATH"]).resolve()),
    "cohort_id": "P2_PARENT_STUDY_MD_4",
    "temperature_k": float(os.environ["P2_RUN_TEMPERATURE_K"]),
    "duration_ns": float(os.environ["P2_RUN_TARGET_NS"]),
    "replicates": int(os.environ["P2_RUN_REPLICATES"]),
    "gromacs_binary": os.environ["P2_RUN_GMX_BIN"],
    "protein_force_field": "CHARMM36m",
    "ligand_force_field": "CGenFF",
    "water_model": "TIP3P",
    "systems": systems,
    "replicate_seeds": {str(rep): rep * 12345 for rep in range(1, int(os.environ["P2_RUN_REPLICATES"]) + 1)},
    "note": "Written immediately before an explicitly authorized future run; not evidence of a completed trajectory.",
}
(root / "parent_md_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

NSTEPS=$(awk -v ns="$TARGET_NS" 'BEGIN { printf "%.0f", ns*1000000/0.002 }')
for complex_name in "${COMPLEXES[@]}"; do
    md_guard_check_parent_system "$complex_name"
    system_dir="${MD_DIR}/${complex_name}"
    (
        cd "$system_dir"
        cat > production.mdp <<EOF
; Guarded targeted parent-lead MD; not set-C MD.
integrator               = md
nsteps                   = ${NSTEPS}
dt                       = 0.002
nstxout-compressed       = 5000
nstenergy                = 1000
nstlog                   = 1000
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
        for rep in $(seq 1 "$REPLICATES"); do
            rep_dir="replicate_${rep}"
            mkdir -p "$rep_dir"
            cp npt.gro npt.cpt topol.top production.mdp "$rep_dir/"
            sed -i '/^gen_vel[[:space:]]*=/{s/=.*/= yes/;}' "$rep_dir/production.mdp"
            echo "gen_seed                 = $((rep * 12345))" >> "$rep_dir/production.mdp"
            printf '%s\n' "replicate=$rep seed=$((rep * 12345)) command=$GMX_BIN grompp/mdrun" >> "$MD_DIR/parent_md_run_commands.log"
            export P2_REP_MDP="$rep_dir/production.mdp"
            export P2_REP_COMPLEX="$complex_name"
            export P2_REP_NUMBER="$rep"
            export P2_REP_SEED="$((rep * 12345))"
            python3 <<'PY'
import hashlib
import json
import os
from pathlib import Path
path = Path(os.environ["P2_REP_MDP"])
hash_value = hashlib.sha256(path.read_bytes()).hexdigest()
manifest_path = Path(os.environ["P2_RUN_MANIFEST_DIR"]) / "parent_md_run_manifest.json"
payload = json.loads(manifest_path.read_text(encoding="utf-8"))
for system in payload["systems"]:
    if system["system_name"] == os.environ["P2_REP_COMPLEX"]:
        system.setdefault("replicates", []).append({
            "replicate": int(os.environ["P2_REP_NUMBER"]),
            "mdp_sha256": hash_value,
            "seed": int(os.environ["P2_REP_SEED"]),
        })
manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
            (
                cd "$rep_dir"
                "$GMX_BIN" grompp -f production.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o production.tpr
                if [[ "$GPU_ID" == "auto" ]]; then
                    "$GMX_BIN" mdrun -deffnm production -v -gpu_id auto
                else
                    "$GMX_BIN" mdrun -deffnm production -v -gpu_id "$GPU_ID"
                fi
            )
        done
    )
done
