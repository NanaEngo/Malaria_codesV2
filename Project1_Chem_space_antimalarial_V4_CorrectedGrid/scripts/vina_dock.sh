#!/bin/bash
# Helper: dock a single ligand with Vina.
# Usage: vina_dock.sh <ligand.pdbqt> <cx> <cy> <cz> [exhaustiveness]
# Env:   RECEPTOR must be set to the receptor .pdbqt path.
# AUDIT FIX 2026-07-17: removed 2>/dev/null masking (was hiding Vina errors);
# added input validation + VINA RESULT check + cleanup on failure.
set -eo pipefail

if [ -z "${RECEPTOR:-}" ]; then
  echo "ERROR: RECEPTOR environment variable not set" >&2
  exit 2
fi
if [ $# -lt 4 ]; then
  echo "ERROR: usage: $0 <ligand.pdbqt> <cx> <cy> <cz> [exhaustiveness]" >&2
  exit 2
fi

LIG="$1"
CX="$2"; CY="$3"; CZ="$4"
EXH="${5:-16}"
OUTFILE="${LIG}.docked.pdbqt"

if [ ! -f "$LIG" ]; then
  echo "ERROR: ligand not found: $LIG" >&2
  exit 2
fi
if [ ! -f "$RECEPTOR" ]; then
  echo "ERROR: receptor not found: $RECEPTOR" >&2
  exit 2
fi

# Reuse: skip if already docked with valid VINA RESULT
if [ -f "$OUTFILE" ] && [ -s "$OUTFILE" ] && grep -q "VINA RESULT" "$OUTFILE" 2>/dev/null; then
  exit 0
fi

nice -n 15 vina --receptor "$RECEPTOR" --ligand "$LIG" \
  --center_x "$CX" --center_y "$CY" --center_z "$CZ" \
  --size_x 25 --size_y 25 --size_z 25 \
  --exhaustiveness "$EXH" --cpu 1 --out "$OUTFILE" || vina_rc=$?
vina_rc=${vina_rc:-0}

if [ $vina_rc -ne 0 ] || ! grep -q "VINA RESULT" "$OUTFILE" 2>/dev/null; then
  echo "ERROR: Vina failed for $LIG (exit=$vina_rc)" >&2
  rm -f "$OUTFILE"
  exit 3
fi
