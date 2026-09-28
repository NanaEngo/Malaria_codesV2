#!/usr/bin/env bash
#SBATCH --job-name=p2_ext_rrs
#SBATCH --array=0-39%8
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH --output=logs/p2_ext_rrs_%A_%a.out
#SBATCH --error=logs/p2_ext_rrs_%A_%a.err

set -euo pipefail

ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
OUT="$ROOT/results/robustness_transfer_20260827/external_docking_run_20260827"
PANEL="$ROOT/results/robustness_transfer_20260827/external_docking_panel_candidate_40.csv"
GRID_DHFR="$ROOT/data/from_project1/docking/Docking_7F3Y/config.txt"
GRID_CRT="$ROOT/data/from_project1/docking/Docking_6UKJ/config.txt"
PREP="$ROOT/results/md_systems/set_c_preparation_20260812_v1"

mkdir -p "$OUT" "$OUT/ligands" "$OUT/receptors" "$OUT/logs"

fail() { echo "FAIL_CLOSED: $*" >&2; exit 2; }
[[ -f "$PANEL" ]] || fail "missing panel"
[[ -f "$GRID_DHFR" && -f "$GRID_CRT" ]] || fail "missing grid config"
command -v vina >/dev/null || fail "vina unavailable"
command -v obabel >/dev/null || fail "obabel unavailable"

python3 - "$PANEL" "$SLURM_ARRAY_TASK_ID" "$OUT" <<'PY'
import csv, pathlib, sys
panel=pathlib.Path(sys.argv[1]); idx=int(sys.argv[2]); out=pathlib.Path(sys.argv[3])
with panel.open(newline='') as f: rows=list(csv.DictReader(f))
if not 0 <= idx < len(rows): raise SystemExit('array index outside frozen panel')
r=rows[idx]
if r['external_panel_id'] != f'EXT-{idx+1:03d}': raise SystemExit('panel ordering mismatch')
if not r['smiles'].strip(): raise SystemExit('empty SMILES')
(out/'ligands'/f"{r['external_panel_id']}.smi").write_text(r['smiles']+'\n')
(out/'ligands'/f"{r['external_panel_id']}.metadata.tsv").write_text('\t'.join([r['external_panel_id'],r['activity'],r['pchembl']])+'\n')
PY

ID=$(awk -F, -v n="$((SLURM_ARRAY_TASK_ID+2))" 'NR==n {print $1}' "$PANEL")
SMI="$OUT/ligands/$ID.smi"
PDB="$OUT/ligands/$ID.pdb"
PDBQT="$OUT/ligands/$ID.pdbqt"
[[ -s "$SMI" ]] || fail "missing ligand SMILES for $ID"

obabel "$SMI" -O "$PDB" --gen3d >/dev/null 2>&1 || fail "Open Babel 3D preparation failed for $ID"
obabel "$PDB" -O "$PDBQT" >/dev/null 2>&1 || fail "PDBQT preparation failed for $ID"
[[ -s "$PDBQT" ]] || fail "empty ligand PDBQT for $ID"

run_state() {
  local state="$1" receptor="$2" grid="$3"
  [[ -s "$receptor" ]] || fail "missing receptor $state"
  local rec="$OUT/receptors/$state.pdbqt"
  if [[ ! -s "$rec" ]]; then
    obabel "$receptor" -O "$rec" >/dev/null 2>&1 || fail "receptor PDBQT conversion failed for $state"
  fi
  [[ -s "$rec" ]] || fail "empty receptor PDBQT for $state"
  local state_out="$OUT/${ID}_${state}.pdbqt"
  local state_log="$OUT/logs/${ID}_${state}.log"
  vina --receptor "$rec" --ligand "$PDBQT" \
    --config "$grid" --exhaustiveness 64 --cpu "$SLURM_CPUS_PER_TASK" \
    --out "$state_out" >"$state_log" 2>&1 || fail "Vina failed for $ID/$state"
  grep -q 'REMARK VINA RESULT:' "$state_out" || fail "no Vina result for $ID/$state"
}

run_state PfDHFR_WT "$PREP/PP-01_PfDHFR_WT/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_N51I "$PREP/PP-01_PfDHFR_N51I/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_C59R "$PREP/PP-01_PfDHFR_C59R/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_S108N "$PREP/PP-01_PfDHFR_S108N/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_I164L "$PREP/PP-01_PfDHFR_I164L/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfCRT_WT "$PREP/PP-01_PfCRT_WT/receptor_fixed.pdb" "$GRID_CRT"
run_state PfCRT_K76T "$PREP/PP-01_PfCRT_K76T/receptor_fixed.pdb" "$GRID_CRT"
run_state PfCRT_K76A "$PREP/PP-01_PfCRT_K76A/receptor_fixed.pdb" "$GRID_CRT"

echo "COMPLETED $ID"
