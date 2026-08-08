#!/usr/bin/env bash
# P2 MD pipeline wrapper. Dry-run is the default; --execute requires a second
# explicit environment confirmation. This wrapper never treats set-C metrics as
# MD results and never silently continues after a failed MD stage.
# Usage: bash scripts/md_full_pipeline.sh [--dry-run] [--execute] [--yes]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
# shellcheck source=md_execution_guard.sh
source "${SCRIPT_DIR}/md_execution_guard.sh"

EXECUTE=0
YES=0
for arg in "$@"; do
    case "$arg" in
        --execute) EXECUTE=1 ;;
        --dry-run) EXECUTE=0 ;;
        --yes) YES=1 ;;
        *) echo "ERROR: unknown argument: $arg" >&2; exit 64 ;;
    esac
done

cat <<'EOF'
============================================================
P2 MD pipeline (guarded)
============================================================
Cohorts: four named parent-study complexes only
Temperature: 310.15 K
Default future targeted run: 10 ns, one replicate
Set-C metrics: docking/RRS/ACSI/PNS only; never relabelled as MD
============================================================
EOF

if [[ "$EXECUTE" != "1" ]]; then
    echo "[DRY RUN] No preparation, grompp, mdrun, or GROMACS command will run."
    echo "Planned stages: minimisation -> NVT -> NPT -> targeted production -> analysis."
    echo "To authorize a future run: --execute plus P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND."
    exit 0
fi

if [[ "$YES" != "1" ]]; then
    echo "ERROR: --execute also requires --yes; no GROMACS command was launched." >&2
    exit 2
fi
md_guard_parse --execute || exit $?
md_guard_require_authorization || exit $?

# Exhaustive read-only gate: report every parent-system blocker before any
# stage can invoke GROMACS. It creates no inputs and never bypasses manifests.
python3 "${SCRIPT_DIR}/p2_parent_md_preflight.py" || {
    echo "ERROR: parent-study MD preflight failed closed; no GROMACS stage will run." >&2
    exit 2
}

# No candidate selection or mutant generation is performed here: those steps
# belong to the set-C docking workflow and mixing them into parent-lead MD is
# prohibited.
bash "${SCRIPT_DIR}/md_run_minimisation.sh" --execute
bash "${SCRIPT_DIR}/md_run_nvt.sh" --execute
bash "${SCRIPT_DIR}/md_run_npt.sh" --execute
bash "${SCRIPT_DIR}/md_run_production.sh" --execute
P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND python3 "${SCRIPT_DIR}/md_analyse_trajectories.py" --execute
