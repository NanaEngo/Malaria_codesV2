#!/bin/bash
# P2 — Declared repair of the two failed external-docking ligands.
#
# Array 15605 failed on two ligand preparations (not on docking):
#   EXT-008: RDKit 3D embedding failed at seed 42 (long C12-lysine peptoid chain)
#   EXT-019: SMILES carries a '.Cl' counterion -> 2 fragments rejected by Meeko
#
# Repairs are DECLARED and recorded in a provenance ledger; the frozen panel
# CSV is never modified. The aggregate/RRS chain consumes only
# external_panel_id + state, so repaired outputs integrate cleanly once the
# integrity audit passes 320/320.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
P2ROOT="$ROOT/Project2_Polypharmacology_MD_ValidationV2607"
OUT="$P2ROOT/results/robustness_transfer_20260827/external_docking_run_20260827"
PANEL="$P2ROOT/results/robustness_transfer_20260827/external_docking_panel_candidate_40.csv"
GRID_DHFR="$P2ROOT/data/from_project1/docking/Docking_7F3Y/config.txt"
GRID_CRT="$P2ROOT/data/from_project1/docking/Docking_6UKJ/config.txt"
PREP="$P2ROOT/results/md_systems/set_c_preparation_20260812_v1"
LEDGER="$P2ROOT/results/robustness_transfer_20260827/external_docking_repair_ledger.json"
MEeko_PY="/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
OBABEL="/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel"

fail() { echo "FAIL_CLOSED: $*" >&2; exit 2; }
[[ -x "$MEeko_PY" && -x "$OBABEL" ]] || fail "malaria_md tools unavailable"
command -v vina >/dev/null || fail "vina unavailable"

# ---- EXT-019: strip the '.Cl' counterion (largest fragment = free base) ----
smi019_orig=$(awk -F, '$1=="EXT-019" {print $2}' "$PANEL")
smi019_fixed=$(printf '%s\n' "$smi019_orig" | "$MEeko_PY" -c '
import sys
from rdkit import Chem
s = sys.stdin.read().strip()
m = Chem.MolFromSmiles(s)
frags = Chem.GetMolFrags(m, asMols=True)
main = max(frags, key=lambda f: f.GetNumHeavyAtoms())
print(Chem.MolToSmiles(main))

')
echo "EXT-019: original='$smi019_orig' -> repaired='$smi019_fixed'"

# ---- EXT-008: retry embedding with random-coordinate fallback + seeds ----
smi008=$(awk -F, '$1=="EXT-008" {print $2}' "$PANEL")
echo "EXT-008: retrying embedding with random coords / multiple seeds"

# ---- Regenerate both ligand PDBQTs ----
"$MEeko_PY" - "$smi019_fixed" "$OUT/ligands/EXT-019.pdbqt" <<'PY'
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy
smiles = Path(sys.argv[1]).read_text().strip()
mol = Chem.MolFromSmiles(smiles)
if mol is None: raise SystemExit('invalid SMILES')
mol = Chem.AddHs(mol)
if AllChem.EmbedMolecule(mol, randomSeed=42) < 0: raise SystemExit('3D embedding failed')
AllChem.MMFFOptimizeMolecule(mol)
prep = MoleculePreparation()
models = prep.prepare(mol)
pdbqt, ok, err = PDBQTWriterLegacy.write_string(models[0])
if not ok: raise SystemExit(err)
Path(sys.argv[2]).write_text(pdbqt)
PY
[[ -s "$OUT/ligands/EXT-019.pdbqt" ]] || fail "EXT-019 ligand PDBQT still empty"

"$MEeko_PY" - "$smi008" "$OUT/ligands/EXT-008.pdbqt" <<'PY'
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy
smiles = Path(sys.argv[1]).read_text().strip()
mol = Chem.MolFromSmiles(smiles)
if mol is None: raise SystemExit('invalid SMILES')
mol = Chem.AddHs(mol)
ok = False
for seed in (42, 7, 2026, 12345):
    if AllChem.EmbedMolecule(mol, randomSeed=seed, useRandomCoords=True) >= 0:
        ok = True
        print(f'EXT-008: embedding succeeded with seed {seed}')
        break
if not ok: raise SystemExit('3D embedding failed after all fallbacks')
AllChem.MMFFOptimizeMolecule(mol)
prep = MoleculePreparation()
models = prep.prepare(mol)
pdbqt, ok, err = PDBQTWriterLegacy.write_string(models[0])
if not ok: raise SystemExit(err)
Path(sys.argv[2]).write_text(pdbqt)
PY
[[ -s "$OUT/ligands/EXT-008.pdbqt" ]] || fail "EXT-008 ligand PDBQT still empty"

# ---- Re-dock the 8 states for each repaired ligand ----
run_states() {
  local id="$1" pdbqt="$2"
  for spec in PfDHFR_WT:PfDHFR_WT:$GRID_DHFR PfDHFR_N51I:PfDHFR_N51I:$GRID_DHFR \
              PfDHFR_C59R:PfDHFR_C59R:$GRID_DHFR PfDHFR_S108N:PfDHFR_S108N:$GRID_DHFR \
              PfDHFR_I164L:PfDHFR_I164L:$GRID_DHFR PfCRT_WT:PfCRT_WT:$GRID_CRT \
              PfCRT_K76T:PfCRT_K76T:$GRID_CRT PfCRT_K76A:PfCRT_K76A:$GRID_CRT; do
    IFS=: read -r state _ grid <<< "$spec"
    local rec="$OUT/receptors/$state.pdbqt"
    if [[ ! -s "$rec" ]]; then
      local receptor="$PREP/PP-01_${state}/receptor_fixed.pdb"
      "$OBABEL" "$receptor" -O "$rec" --partialcharge gasteiger >/dev/null 2>&1 || fail "receptor conversion failed $state"
      grep -q '^ROOT$' "$rec" && { "$OBABEL" "$receptor" -O "$rec" -xr >/dev/null 2>&1 || fail "rigid conversion failed $state"; }
      grep -q '^ROOT$' "$rec" && fail "receptor remains flexible $state"
    fi
    local result="$OUT/${id}_${state}.pdbqt"
    vina --receptor "$rec" --ligand "$pdbqt" --config "$grid" --exhaustiveness 64 --cpu 16 --out "$result" > "$OUT/logs/${id}_${state}.log" 2>&1 || fail "Vina failed $id/$state"
    grep -q 'REMARK VINA RESULT:' "$result" || fail "missing Vina result $id/$state"
  done
}
run_states EXT-019 "$OUT/ligands/EXT-019.pdbqt"
run_states EXT-008 "$OUT/ligands/EXT-008.pdbqt"

# ---- Provenance ledger (declared repair, panel untouched) ----
cat > "$LEDGER" <<EOF
{
  "schema_version": 1,
  "status": "DECLARED_REPAIR_COMPLETED",
  "declared_on": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "boundary": "Panel CSV frozen and unmodified; repairs recorded; aggregate/RRS chain integrates repaired outputs only after integrity audit reaches 320/320.",
  "EXT-008": {
    "original_smiles": "$smi008",
    "failure": "3D embedding failed at seed 42",
    "repair": "EmbedMolecule with useRandomCoords=True across seeds 42,7,2026,12345",
    "outcome": "ligand PDBQT regenerated; 8 states re-docked"
  },
  "EXT-019": {
    "original_smiles": "$smi019_orig",
    "failure": "SMILES contains '.Cl' counterion (2 fragments, Meeko rejection)",
    "repair": "largest-fragment free base taken",
    "repaired_smiles": "$smi019_fixed",
    "outcome": "ligand PDBQT regenerated; 8 states re-docked"
  }
}
EOF
echo "=== Repair ledger written: $LEDGER ==="
echo "=== Repaired ligands COMPLETE: EXT-008 + EXT-019 (16 states) ==="
