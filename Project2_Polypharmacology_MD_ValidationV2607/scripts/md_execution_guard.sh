#!/usr/bin/env bash
# Shared fail-closed guard for P2 MD execution scripts.
# A script may only launch GROMACS when BOTH conditions hold:
#   1. the caller passes --execute; and
#   2. P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND is exported explicitly.
# Without both conditions, callers must remain in dry-run mode.

md_guard_parse() {
    MD_GUARD_EXECUTE=0
    MD_GUARD_DRY_RUN=1
    MD_GUARD_SAW_EXECUTE=0
    MD_GUARD_SAW_DRY_RUN=0
    MD_GUARD_POSITIONAL=()

    for arg in "$@"; do
        case "$arg" in
            --execute)
                MD_GUARD_EXECUTE=1
                MD_GUARD_DRY_RUN=0
                MD_GUARD_SAW_EXECUTE=1
                ;;
            --dry-run)
                MD_GUARD_EXECUTE=0
                MD_GUARD_DRY_RUN=1
                MD_GUARD_SAW_DRY_RUN=1
                ;;
            --help|-h)
                return 64
                ;;
            --*)
                echo "ERROR: unknown execution flag: $arg" >&2
                return 64
                ;;
            *)
                MD_GUARD_POSITIONAL+=("$arg")
                ;;
        esac
    done

    # Explicitly reject contradictory flags rather than silently choosing one.
    if [[ "$MD_GUARD_SAW_EXECUTE" == "1" && "$MD_GUARD_SAW_DRY_RUN" == "1" ]]; then
        echo "ERROR: --execute and --dry-run cannot be combined." >&2
        return 64
    fi
}

md_guard_check_parent_system() {
    local system_name="$1"
    case "$system_name" in
        201_DHFR|438_ATP4|164_ClpP|214_CRT) return 0 ;;
        *) echo "ERROR: system is not an allowlisted parent-study MD system: $system_name" >&2; return 2 ;;
    esac
}

md_guard_require_authorization() {
    if [[ "${MD_GUARD_EXECUTE:-0}" != "1" ]]; then
        echo "[DRY RUN] GROMACS execution is disabled by default."
        echo "        Pass --execute and export P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND only after reviewing the inputs."
        return 1
    fi
    if [[ "${P2_MD_EXECUTE_CONFIRM:-}" != "I_UNDERSTAND" ]]; then
        echo "ERROR: --execute requires P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND." >&2
        echo "       No GROMACS command was launched." >&2
        return 2
    fi
    local gmx_bin="${P2_GMX_BIN:-gmx}"
    if ! command -v "$gmx_bin" >/dev/null 2>&1 && [[ ! -x "$gmx_bin" ]]; then
        echo "ERROR: configured GROMACS executable is unavailable: $gmx_bin" >&2
        return 2
    fi
    return 0
}

md_guard_validate_forcefield_manifest() {
    local system_dir="$1"
    local manifest="$system_dir/forcefield_manifest.json"
    [[ -d "$system_dir" ]] || {
        echo "ERROR: missing parent-study system directory: $system_dir" >&2
        return 2
    }
    [[ -s "$manifest" ]] || {
        echo "ERROR: missing force-field manifest: $manifest" >&2
        return 2
    }
    python3 "${SCRIPT_DIR}/md_forcefield_manifest.py" "$manifest" --system-dir "$system_dir"
    return $?
}

md_guard_print_plan() {
    local script_name="$1"
    shift
    echo "P2 MD execution guard: $script_name"
    echo "Planned operation: $*"
    echo "GROMACS launched: no"
    echo "Status: FAIL-CLOSED / DRY-RUN"
}
