#!/usr/bin/env bash
# =============================================================================
# Tartarus Docking Calibration — BMAD Phase 2c
# =============================================================================
# Runs Tartarus QuickVina docking on 19,914 primary leads against 3 targets:
#   1SYH (DHFR), 6Y2F (HIV protease), 4LDE (A2a adenosine receptor)
#
# Requirements:
#   - Docker installed and running (user in docker group)
#   - Input CSV: data/from_project1/results/tartarus_input.csv
#
# Usage:
#   bash scripts/run_tartarus_docking.sh [--sample N]
#
#   --sample N   Only dock first N molecules (for testing; default: all)
#
# Output:
#   results/tartarus_output.csv   — columns: smile, score_1syh, score_6y2f, score_4lde
#   results/tartarus_docking.log  — full log
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data/from_project1/results"
RESULTS_DIR="$PROJECT_DIR/results"

DOCKER_IMAGE="johnwilles/tartarus:latest"
INPUT_CSV="$DATA_DIR/tartarus_input.csv"
OUTPUT_CSV="$RESULTS_DIR/tartarus_output.csv"
LOG_FILE="$RESULTS_DIR/tartarus_docking.log"

SAMPLE_N=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --sample)
            SAMPLE_N="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

echo "========================================" | tee -a "$LOG_FILE"
echo "Tartarus Docking Calibration"           | tee -a "$LOG_FILE"
echo "Started: $(date)"                        | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# --- Pre-flight checks ---
if ! command -v docker &>/dev/null; then
    echo "ERROR: docker not found in PATH" | tee -a "$LOG_FILE"
    exit 1
fi

# Check Docker daemon is accessible (may need 'sg docker' or re-login)
if ! docker info &>/dev/null 2>&1; then
    echo "WARNING: docker daemon not accessible directly." | tee -a "$LOG_FILE"
    echo "If permission denied, run via: sg docker -c 'bash $0 $*'" | tee -a "$LOG_FILE"
    echo "Or add yourself to docker group and re-login." | tee -a "$LOG_FILE"
    exit 1
fi

if [[ ! -f "$INPUT_CSV" ]]; then
    echo "ERROR: Input CSV not found: $INPUT_CSV" | tee -a "$LOG_FILE"
    exit 1
fi

# --- Optionally create a sample ---
RUN_DIR=$(mktemp -d)
trap "rm -rf $RUN_DIR" EXIT

if [[ -n "$SAMPLE_N" ]]; then
    echo "Creating sample of $SAMPLE_N molecules..." | tee -a "$LOG_FILE"
    head -1 "$INPUT_CSV" > "$RUN_DIR/input.csv"
    set +o pipefail
    tail -n +2 "$INPUT_CSV" | head -n "$SAMPLE_N" >> "$RUN_DIR/input.csv"
    set -o pipefail
    INPUT_FILE="input.csv"
    N_MOLECULES="$SAMPLE_N"
else
    cp "$INPUT_CSV" "$RUN_DIR/input.csv"
    INPUT_FILE="input.csv"
    N_MOLECULES=$(( $(wc -l < "$INPUT_CSV") - 1 ))
fi

echo "Molecules to dock: $N_MOLECULES" | tee -a "$LOG_FILE"
echo "Targets: 1SYH, 6Y2F, 4LDE (QuickVina)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# --- Pull Docker image (if not cached) ---
echo "Pulling Tartarus Docker image..." | tee -a "$LOG_FILE"
if ! docker image inspect "$DOCKER_IMAGE" &>/dev/null; then
    docker pull "$DOCKER_IMAGE" 2>&1 | tee -a "$LOG_FILE"
else
    echo "  Image already cached." | tee -a "$LOG_FILE"
fi

# --- Run Tartarus benchmark ---
echo "" | tee -a "$LOG_FILE"
echo "Running Tartarus docking (--mode docking --parallel)..." | tee -a "$LOG_FILE"
echo "  This will dock $N_MOLECULES × 3 targets. Estimated time:" | tee -a "$LOG_FILE"
echo "    ~5s/molecule/target × 3 targets = ~15s/molecule" | tee -a "$LOG_FILE"
echo "    Total: ~$(( N_MOLECULES * 15 / 3600 ))h $(( (N_MOLECULES * 15 % 3600) / 60 ))min" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

T_START=$(date +%s)

# SMINA_CPU: limit CPUs per smina call to avoid over-subscription
# With --parallel (multiprocessing.cpu_count() workers), each worker spawns smina
# Default 2 CPUs/job × 48 workers = 96 threads on 48 cores (manageable)
SMINA_CPU="${SMINA_CPU:-2}"

docker run --rm \
    -e "SMINA_CPU=$SMINA_CPU" \
    -v "$RUN_DIR":/data \
    -v "$SCRIPT_DIR/tartarus_docking_patched.py":/benchmark/tartarus/docking.py \
    "$DOCKER_IMAGE" \
    --mode docking \
    --input_filename "$INPUT_FILE" \
    --output_filename output.csv \
    --parallel \
    2>&1 | tee -a "$LOG_FILE"

T_END=$(date +%s)
T_ELAPSED=$(( T_END - T_START ))

echo "" | tee -a "$LOG_FILE"
echo "Docking completed in $(( T_ELAPSED / 3600 ))h $(( (T_ELAPSED % 3600) / 60 ))min $(( T_ELAPSED % 60 ))s" | tee -a "$LOG_FILE"

# --- Collect output ---
if [[ -f "$RUN_DIR/output.csv" ]]; then
    cp "$RUN_DIR/output.csv" "$OUTPUT_CSV"
    N_OUT=$(tail -n +2 "$OUTPUT_CSV" | wc -l)
    echo "Output saved: $OUTPUT_CSV ($N_OUT molecules scored)" | tee -a "$LOG_FILE"
else
    echo "ERROR: output.csv not found in Docker mount. Check log above." | tee -a "$LOG_FILE"
    exit 1
fi

# --- Summary statistics ---
echo "" | tee -a "$LOG_FILE"
echo "--- Score Summary ---" | tee -a "$LOG_FILE"

for COL in score_1syh score_6y2f score_4lde; do
    # Count successful (non-10000) scores
    N_OK=$(awk -F',' -v col="$COL" '
        NR>1 && $0 ~ col { n++ }
        END { print n+0 }
    ' "$OUTPUT_CSV" 2>/dev/null || echo "?")
    
    # Basic stats via awk
    awk -F',' -v col="$COL" '
        NR>1 {
            # Find column index
            for (i=1; i<=NF; i++) {
                gsub(/^[ \t]+|[ \t]+$/, "", $i)
                if ($i == col) { val = $(i+1); break }
            }
            # Alternative: use positional (col is 2nd, 3rd, or 4th)
        }
    ' "$OUTPUT_CSV" 2>/dev/null || true

    echo "  $COL: (see output.csv for details)" | tee -a "$LOG_FILE"
done

echo "" | tee -a "$LOG_FILE"
echo "Finished: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
