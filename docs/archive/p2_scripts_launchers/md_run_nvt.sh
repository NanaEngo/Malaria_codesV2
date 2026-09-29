#!/usr/bin/env bash
# P2 NVT equilibration utility; dry-run by default.
# Usage: bash scripts/md_run_nvt.sh [--dry-run|--execute] [complex|all]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"
# shellcheck source=md_execution_guard.sh
source "${SCRIPT_DIR}/md_execution_guard.sh"
md_guard_parse "$@" || { echo "Usage: $0 [--dry-run|--execute] [complex|all]" >&2; exit 64; }
POSITIONAL=("${MD_GUARD_POSITIONAL[@]}")
COMPLEX="${POSITIONAL[0]:-all}"
TEMPERATURE_K="310.15"
GMX_BIN="${P2_GMX_BIN:-gmx}"

if [[ "$COMPLEX" == "all" ]]; then COMPLEXES=(201_DHFR 438_ATP4 164_ClpP 214_CRT); else COMPLEXES=("$COMPLEX"); fi
if [[ "$MD_GUARD_EXECUTE" != "1" ]]; then
    md_guard_print_plan "md_run_nvt.sh" "NVT equilibration at ${TEMPERATURE_K} K for ${COMPLEXES[*]}"
    exit 0
fi
md_guard_require_authorization || exit $?
md_guard_require_parent_preflight || {
    echo "ERROR: parent MD preflight failed closed; no GROMACS command will run." >&2
    exit 2
}

for complex_name in "${COMPLEXES[@]}"; do
    md_guard_check_parent_system "$complex_name"
    system_dir="$(md_guard_resolve_parent_system_dir "$MD_DIR" "$complex_name")"
    [[ -d "$system_dir" ]] || { echo "ERROR: missing system directory: $system_dir" >&2; exit 1; }
    [[ -s "$system_dir/em.gro" && -s "$system_dir/topol.top" ]] || { echo "ERROR: missing NVT inputs in $system_dir" >&2; exit 1; }
    md_guard_validate_forcefield_manifest "$system_dir"
    (
        cd "$system_dir"
        cat > nvt.mdp <<EOF
; NVT equilibration at physiological temperature
integrator = md
nsteps = 50000
dt = 0.002
nstxout-compressed = 500
nstenergy = 500
nstlog = 500
continuation = no
constraint_algorithm = lincs
constraints = h-bonds
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.2
rcoulomb = 1.2
rvdw = 1.2
coulombtype = PME
tcoupl = V-rescale
tc-grps = System
tau_t = 0.1
ref_t = ${TEMPERATURE_K}
pcoupl = no
gen_vel = yes
gen_temp = ${TEMPERATURE_K}
gen_seed = 12345
define = -DPOSRES
EOF
        "$GMX_BIN" grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
        "$GMX_BIN" mdrun -deffnm nvt -v
    )
done
