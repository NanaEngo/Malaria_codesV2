#!/usr/bin/env bash
#SBATCH --job-name=p2_ext_rrs_prod
#SBATCH --partition=production
#SBATCH --array=0-39%8
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH --output=logs/p2_ext_rrs_prod_%A_%a.out
#SBATCH --error=logs/p2_ext_rrs_prod_%A_%a.err

set -euo pipefail

ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
OUT="$ROOT/Project2_Polypharmacology_MD_ValidationV2607/results/robustness_transfer_20260827/external_docking_run_20260827"
PANEL="$ROOT/Project2_Polypharmacology_MD_ValidationV2607/results/robustness_transfer_20260827/external_docking_panel_candidate_40.csv"
GRID_DHFR="$ROOT/Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/docking/Docking_7F3Y/config.txt"
GRID_CRT="$ROOT/Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/docking/Docking_6UKJ/config.txt"
PREP="$ROOT/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c_preparation_20260812_v1"

mkdir -p "$OUT" "$OUT/ligands" "$OUT/receptors" "$OUT/logs"
fail() { echo "FAIL_CLOSED: $*" >&2; exit 2; }
[[ -s "$PANEL" ]] || fail "missing panel"
[[ -s "$GRID_DHFR" && -s "$GRID_CRT" ]] || fail "missing grids"
command -v vina >/dev/null || fail "vina unavailable"
MEeko_PY="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
OBABEL="/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel"
[[ -x "$MEeko_PY" && -x "$OBABEL" ]] || fail "malaria_md molecular tools unavailable"

ID=$(awk -F, -v n="$((SLURM_ARRAY_TASK_ID+2))" 'NR==n {print $1}' "$PANEL")
SMILES=$(awk -F, -v n="$((SLURM_ARRAY_TASK_ID+2))" 'NR==n {print $2}' "$PANEL")
[[ "$ID" == "EXT-$(printf '%03d' "$((SLURM_ARRAY_TASK_ID+1))")" ]] || fail "panel ordering mismatch"
[[ -n "$SMILES" ]] || fail "empty SMILES"
SMI="$OUT/ligands/$ID.smi"; PDB="$OUT/ligands/$ID.pdb"; PDBQT="$OUT/ligands/$ID.pdbqt"
printf '%s\n' "$SMILES" > "$SMI"
printf '%s\t%s\t%s\n' "$ID" "$(awk -F, -v n="$((SLURM_ARRAY_TASK_ID+2))" 'NR==n {print $3}' "$PANEL")" "$(awk -F, -v n="$((SLURM_ARRAY_TASK_ID+2))" 'NR==n {print $4}' "$PANEL")" > "$OUT/ligands/$ID.metadata.tsv"
"$MEeko_PY" - "$SMI" "$PDBQT" <<'PY'
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy
smiles=Path(sys.argv[1]).read_text().strip()
mol=Chem.MolFromSmiles(smiles)
if mol is None: raise SystemExit('invalid SMILES')
mol=Chem.AddHs(mol)
if AllChem.EmbedMolecule(mol, randomSeed=42) < 0: raise SystemExit('3D embedding failed')
AllChem.MMFFOptimizeMolecule(mol)
prep=MoleculePreparation()
models=prep.prepare(mol)
pdbqt, ok, err = PDBQTWriterLegacy.write_string(models[0])
if not ok: raise SystemExit(err)
Path(sys.argv[2]).write_text(pdbqt)
PY
[[ -s "$PDBQT" ]] || fail "empty ligand PDBQT"

run_state() {
  local state="$1" receptor="$2" grid="$3"
  [[ -s "$receptor" ]] || fail "missing receptor $state"
  local rec="$OUT/receptors/$state.pdbqt"
  if [[ ! -s "$rec" ]]; then
    "$OBABEL" "$receptor" -O "$rec" --partialcharge gasteiger >/dev/null 2>&1 || fail "receptor conversion failed for $state"
  fi
  [[ -s "$rec" ]] || fail "empty receptor PDBQT for $state"
  if grep -q '^ROOT$' "$rec"; then
    "$OBABEL" "$receptor" -O "$rec" -xr >/dev/null 2>&1 || fail "rigid receptor conversion failed for $state"
  fi
  grep -q '^ROOT$' "$rec" && fail "receptor remains flexible for $state"
  local result="$OUT/${ID}_${state}.pdbqt"
  vina --receptor "$rec" --ligand "$PDBQT" --config "$grid" --exhaustiveness 64 --cpu "${SLURM_CPUS_PER_TASK:-16}" --out "$result" > "$OUT/logs/${ID}_${state}.log" 2>&1 || fail "Vina failed for $ID/$state"
  grep -q 'REMARK VINA RESULT:' "$result" || fail "missing Vina result for $ID/$state"
}
run_state PfDHFR_WT "$PREP/PP-01_PfDHFR_WT/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_N51I "$PREP/PP-01_PfDHFR_N51I/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_C59R "$PREP/PP-01_PfDHFR_C59R/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_S108N "$PREP/PP-01_PfDHFR_S108N/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfDHFR_I164L "$PREP/PP-01_PfDHFR_I164L/receptor_fixed.pdb" "$GRID_DHFR"
run_state PfCRT_WT "$PREP/PP-01_PfCRT_WT/receptor_fixed.pdb" "$GRID_CRT"
run_state PfCRT_K76T "$PREP/PP-01_PfCRT_K76T/receptor_fixed.pdb" "$GRID_CRT"
run_state PfCRT_K76A "$PREP/PP-01_PfCRT_K76A/receptor_fixed.pdb" "$GRID_CRT"
printf 'COMPLETED %s\n' "$ID"
