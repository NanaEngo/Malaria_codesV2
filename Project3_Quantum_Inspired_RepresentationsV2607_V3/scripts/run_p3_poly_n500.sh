#!/usr/bin/env bash
# Detached launcher for P3 physical validation QKS polypharm benchmark (n=500, 5 folds)
set -euo pipefail

# Usage (detached):
#   setsid bash scripts/run_p3_poly_n500.sh > results/p3_physical_validation/p3_polypharm_n500.log 2>&1 &
#
# Override the Python interpreter if needed:
#   Malaria_MD_PYTHON=/path/to/python setsid bash scripts/run_p3_poly_n500.sh ...

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${MALARIA_MD_PYTHON:-/home/nanaengo/miniforge3/envs/malaria_md/bin/python}"

[ -x "$PYTHON" ] || { echo "ERROR: Python interpreter not found or not executable: $PYTHON" >&2; exit 1; }
export PYTHONUNBUFFERED=1

cd "$PROJECT_DIR"

exec "$PYTHON" "$PROJECT_DIR/scripts/p3_physical_validation.py" \
    --analysis poly \
    --n-poly 500 \
    --n-folds 5 \
    --n-repeats 1
