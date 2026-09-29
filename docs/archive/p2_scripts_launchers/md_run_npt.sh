#!/usr/bin/env bash
# P2 NPT equilibration utility; dry-run by default.
# Usage: bash scripts/md_run_npt.sh [--dry-run|--execute] [complex|all]

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
    md_guard_print_plan "md_run_npt.sh" "NPT equilibration at ${TEMPERATURE_K} K and 1 bar for ${COMPLEXES[*]}"
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
    [[ -s "$system_dir/nvt.gro" && -s "$system_dir/nvt.cpt" && -s "$system_dir/topol.top" ]] || { echo "ERROR: missing NPT inputs in $system_dir" >&2; exit 1; }
    md_guard_validate_forcefield_manifest "$system_dir"
    (
        cd "$system_dir"
        cat > npt.mdp <<EOF
; NPT equilibration at physiological temperature
integrator = md
nsteps = 250000
dt = 0.002
nstxout-compressed = 1000
nstenergy = 1000
nstlog = 1000
continuation = yes
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
pcoupl = Parrinello-Rahman
pcoupltype = isotropic
tau_p = 2.0
compressibility = 4.5e-5
ref_p = 1.0
gen_vel = no
EOF
        "$GMX_BIN" grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
        "$GMX_BIN" mdrun -deffnm npt -v
    )
done
