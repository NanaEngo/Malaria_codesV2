#!/usr/bin/env bash
# P2 energy minimisation utility; dry-run by default.
# Usage: bash scripts/md_run_minimisation.sh [--dry-run|--execute] [complex|all]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"
# shellcheck source=md_execution_guard.sh
source "${SCRIPT_DIR}/md_execution_guard.sh"
md_guard_parse "$@" || { echo "Usage: $0 [--dry-run|--execute] [complex|all]" >&2; exit 64; }
POSITIONAL=("${MD_GUARD_POSITIONAL[@]}")
COMPLEX="${POSITIONAL[0]:-all}"
GMX_BIN="${P2_GMX_BIN:-gmx}"
if [[ "$COMPLEX" == "all" ]]; then COMPLEXES=(201_DHFR 438_ATP4 164_ClpP 214_CRT); else COMPLEXES=("$COMPLEX"); fi
if [[ "$MD_GUARD_EXECUTE" != "1" ]]; then
    md_guard_print_plan "md_run_minimisation.sh" "two-stage energy minimisation for ${COMPLEXES[*]}"
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
    (
        cd "$system_dir"
        input_gro=""
        [[ -s ions.gro ]] && input_gro=ions.gro
        [[ -n "$input_gro" ]] || { echo "ERROR: ions.gro is required; refusing solvated-only execution in $system_dir" >&2; exit 1; }
        [[ -s topol.top ]] || { echo "ERROR: topol.top missing in $system_dir" >&2; exit 1; }
        md_guard_validate_forcefield_manifest "$system_dir"
        cat > minim.mdp <<'EOF'
integrator = steep
emtol = 1000.0
emstep = 0.01
nsteps = 25000
nstlist = 1
cutoff-scheme = Verlet
coulombtype = PME
rcoulomb = 1.0
rvdw = 1.0
constraints = none
EOF
        "$GMX_BIN" grompp -f minim.mdp -c "$input_gro" -p topol.top -o em_steep.tpr
        "$GMX_BIN" mdrun -deffnm em_steep -v
        cat > minim_cg.mdp <<'EOF'
integrator = cg
emtol = 100.0
emstep = 0.01
nsteps = 25000
nstlist = 1
cutoff-scheme = Verlet
coulombtype = PME
rcoulomb = 1.0
rvdw = 1.0
constraints = none
EOF
        "$GMX_BIN" grompp -f minim_cg.mdp -c em_steep.gro -p topol.top -o em.tpr
        "$GMX_BIN" mdrun -deffnm em -v
        rm -f em_steep.tpr em_steep.trr em_steep.edr em_steep.log minim_cg.mdp
    )
done
