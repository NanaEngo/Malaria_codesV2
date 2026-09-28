#!/bin/bash
# P2 — Generalized declared repair of the external-docking ligands that failed
# in array 15605. The 10 missing ligands fail for FOUR systematic, distinct
# reasons (not a docking problem):
#
#   (A) Salt/counterion in frozen SMILES -> 2-3 fragments rejected by Meeko:
#       EXT-019 (.Cl), EXT-021 (.2Cl), EXT-032 (.2Cl), EXT-033 (.Cl),
#       EXT-036 (.2Cl), EXT-037 (.oxalate)
#           Repair: largest-fragment free base (heavy-atom argmax).
#   (B) RDKit EmbedMolecule failed at seed 42 on flexible/floppy systems where
#       distance geometry cannot converge:
#       EXT-008 (69 heavy atoms, 52 rotatable bonds), EXT-038
#           Repair: Open Babel --gen3d (already installed), then SDF -> PDBQT
#           via Meeko. OBabel's force-field 3D is far more lenient than RDKit
#           DG for these ring-rich / very flexible export-panel systems.
#   (C) EXT-007 hit the SLURM time-limit at 3/8 (large flexible export panel
#       ligand); prep was fine. Repair: re-run ONLY the 5 missing states.
#   (D) EXT-039 is a DECLARED EMBED_FAILURE: the molecule (folded cyclic ether
#       macrocycle) cannot generate 3D coordinates within reasonable compute
#       under RDKit DG, RDKit random-coords, or OBabel --gen3d. It is excluded
#       by declaration, NOT silently dropped: recorded in the provenance
#       ledger, panel target becomes 312/320 (39 ligands x 8 states).
#
# Every repair is DECLARED and recorded in a provenance ledger; the frozen
# panel CSV is never modified. The aggregate/RRS chain consumes only
# external_panel_id + state, so repaired outputs integrate once the integrity
# audit reaches 312/312 with the declared EXT-039 exclusion.
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
[[ -s "$PANEL" ]] || fail "missing frozen panel"

# frozen SMILES map
declare -A RAW_SMI
while IFS=, read -r id smi; do
  [[ "$id" == "external_panel_id" ]] && continue
  RAW_SMI["$id"]="$smi"
done < <(cut -d, -f1,2 "$PANEL")

EMBED_FAILURE="EXT-039"          # declared, never docked
salt_ids="EXT-019 EXT-021 EXT-032 EXT-033 EXT-036 EXT-037"
obabel_ids="EXT-008 EXT-038"

make_pdbqt_salt() {
  local id="$1"
  local smi_file="$OUT/ligands/$id.smi"
  local out="$OUT/ligands/$id.pdbqt"
  [[ -s "$out" ]] && rm -f "$out"
  printf '%s\n' "${RAW_SMI[$id]}" > "$smi_file"
  "$MEeko_PY" - "$smi_file" "$out" <<'PY'
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy
s = Path(sys.argv[1]).read_text().strip()
m = Chem.MolFromSmiles(s)
if m is None: raise SystemExit('invalid SMILES')
frags = Chem.GetMolFrags(m, asMols=True)
main = max(frags, key=lambda f: f.GetNumHeavyAtoms())
if len(frags) > 1:
    print(f'strip {len(frags)} counterion/fragment(s) -> free base: {Chem.MolToSmiles(main)[:60]}', file=sys.stderr)
m = Chem.AddHs(main)
if AllChem.EmbedMolecule(m, randomSeed=42) < 0:
    raise SystemExit('3D embedding failed (free base)')
AllChem.MMFFOptimizeMolecule(m)
prep = MoleculePreparation()
models = prep.prepare(m)
pdbqt, ok, err = PDBQTWriterLegacy.write_string(models[0])
if not ok: raise SystemExit(err)
Path(sys.argv[2]).write_text(pdbqt)
PY
  [[ -s "$out" ]] || fail "$id ligand PDBQT still empty"
  echo "  $id: prepared (free base) OK"
}

make_pdbqt_obabel() {
  # OBabel --gen3d (force-field 3D) is far more reliable than RDKit distance
  # geometry for these flexible/ring-rich export-panel systems. The SDF is
  # read into RDKit (which preserves coordinates) and handed to Meeko.
  local id="$1"
  local smi_file="$OUT/ligands/$id.smi"
  local sdf="$OUT/ligands/$id.ob3d.sdf"
  local out="$OUT/ligands/$id.pdbqt"
  [[ -s "$out" ]] && rm -f "$out"
  printf '%s\n' "${RAW_SMI[$id]}" > "$smi_file"
  rm -f "$sdf"
  timeout 300 "$OBABEL" "$smi_file" -O "$sdf" --gen3d >/dev/null 2>&1 || fail "OBabel --gen3d failed for $id"
  [[ -s "$sdf" ]] || fail "OBabel SDF empty for $id"
  "$MEeko_PY" - "$sdf" "$out" <<'PY'
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy
sdf = Path(sys.argv[1])
m = Chem.MolFromMolFile(str(sdf), removeHs=False)
if m is None: raise SystemExit('invalid OBabel SDF')
# The OBabel --gen3d SDF already carries 3D coordinates; only embed as a
# last resort if (unexpectedly) no conformer survived the round-trip.
if m.GetNumConformers() == 0:
    if AllChem.EmbedMolecule(m, randomSeed=42) < 0:
        raise SystemExit('no conformer available')
AllChem.MMFFOptimizeMolecule(m)
prep = MoleculePreparation()
models = prep.prepare(m)
pdbqt, ok, err = PDBQTWriterLegacy.write_string(models[0])
if not ok: raise SystemExit(err)
Path(sys.argv[2]).write_text(pdbqt)
PY
  [[ -s "$out" ]] || fail "$id ligand PDBQT still empty"
  echo "  $id: prepared (OBabel --gen3d) OK; n_heavy=$("$MEeko_PY" -c "print(Chem.MolFromSmiles('${RAW_SMI[$id]}').GetNumHeavyAtoms())" 2>/dev/null || echo '?')"
}

echo "=== (A) Salt-strip prep ==="
for id in $salt_ids; do make_pdbqt_salt "$id"; done
echo "=== (B) OBabel --gen3d prep ==="
for id in $obabel_ids; do make_pdbqt_obabel "$id"; done
echo "=== (D) Declared EMBED_FAILURE ==="
echo "  $EMBED_FAILURE: no ligand PDBQT generated; recorded as excluded by declaration."

run_states() {
  local id="$1" pdbqt="$2"
  for spec in PfDHFR_WT:PfDHFR_WT:$GRID_DHFR PfDHFR_N51I:PfDHFR_N51I:$GRID_DHFR \
              PfDHFR_C59R:PfDHFR_C59R:$GRID_DHFR PfDHFR_S108N:PfDHFR_S108N:$GRID_DHFR \
              PfDHFR_I164L:PfDHFR_I164L:$GRID_DHFR PfCRT_WT:PfCRT_WT:$GRID_CRT \
              PfCRT_K76T:PfCRT_K76T:$GRID_CRT PfCRT_K76A:PfCRT_K76A:$GRID_CRT; do
    IFS=: read -r state _ grid <<< "$spec"
    local result="$OUT/${id}_${state}.pdbqt"
    [[ -s "$result" ]] && grep -q 'REMARK VINA RESULT:' "$result" && { echo "  $id/$state: already present, skip"; continue; }
    local rec="$OUT/receptors/$state.pdbqt"
    if [[ ! -s "$rec" ]]; then
      local receptor="$PREP/PP-01_${state}/receptor_fixed.pdb"
      "$OBABEL" "$receptor" -O "$rec" --partialcharge gasteiger >/dev/null 2>&1 || fail "receptor conversion failed $state"
      grep -q '^ROOT$' "$rec" && { "$OBABEL" "$receptor" -O "$rec" -xr >/dev/null 2>&1 || fail "rigid conversion failed $state"; }
      grep -q '^ROOT$' "$rec" && fail "receptor remains flexible $state"
    fi
    vina --receptor "$rec" --ligand "$pdbqt" --config "$grid" --exhaustiveness 64 --cpu 16 --out "$result" > "$OUT/logs/${id}_${state}.log" 2>&1 || fail "Vina failed $id/$state"
    grep -q 'REMARK VINA RESULT:' "$result" || fail "missing Vina result $id/$state"
  done
}

# ---- (C) EXT-007: re-run ONLY the missing 5 states, keep the 3 valid poses ----
echo "=== (C) EXT-007 missing-state completion ==="
if ! [[ -s "$OUT/ligands/EXT-007.pdbqt" ]]; then
  printf '%s\n' "${RAW_SMI[EXT-007]}" > /tmp/ext007.smi
  "$MEeko_PY" - /tmp/ext007.smi "$OUT/ligands/EXT-007.pdbqt" <<'PY'
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy
s = Path(sys.argv[1]).read_text().strip()
m = Chem.MolFromSmiles(s)
if m is None: raise SystemExit('invalid SMILES')
m = Chem.AddHs(m)
if AllChem.EmbedMolecule(m, randomSeed=42) < 0: raise SystemExit('embed fail')
AllChem.MMFFOptimizeMolecule(m)
prep = MoleculePreparation(); models = prep.prepare(m)
pdbqt, ok, err = PDBQTWriterLegacy.write_string(models[0])
if not ok: raise SystemExit(err)
Path(sys.argv[2]).write_text(pdbqt)
PY
  [[ -s "$OUT/ligands/EXT-007.pdbqt" ]] || fail "EXT-007 ligand PDBQT empty"
fi
run_states EXT-007 "$OUT/ligands/EXT-007.pdbqt"

# ---- full 8-state re-dock for salt + obabel ligands ----
echo "=== Re-dock repaired ligands (salt) ==="
for id in $salt_ids; do run_states "$id" "$OUT/ligands/$id.pdbqt"; done
echo "=== Re-dock repaired ligands (OBabel) ==="
for id in $obabel_ids; do run_states "$id" "$OUT/ligands/$id.pdbqt"; done

# ---- Provenance ledger (declared repair, panel untouched) ----
cat > "$LEDGER" <<EOF
{
  "schema_version": 3,
  "status": "DECLARED_REPAIR_COMPLETED_WITH_EMBED_FAILURE_EXCLUSION",
  "declared_on": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "boundary": "Panel CSV frozen and unmodified; repairs and the EXT-039 exclusion recorded. Aggregate/RRS chain integrates repaired outputs only after the integrity audit reaches 312/312 valid with the declared EXT-039 exclusion.",
  "cause_A_salt_strip": {
    "description": "Frozen SMILES carried counterions (.Cl, .2Cl, .oxalate) yielding 2-3 fragments rejected by Meeko; largest-fragment free base taken.",
    "ligands": ["EXT-019", "EXT-021", "EXT-032", "EXT-033", "EXT-036", "EXT-037"]
  },
  "cause_B_obabel_gen3d": {
    "description": "RDKit distance geometry failed at seed 42 on flexible/ring-rich systems; Open Babel --gen3d (force-field 3D) used instead, then SDF -> Meeko PDBQT.",
    "ligands": ["EXT-008", "EXT-038"]
  },
  "cause_C_time_limit_partial": {
    "description": "EXT-007 killed by SLURM time-limit at 3/8; prep was valid. Only the 5 missing states re-docked; existing poses retained.",
    "ligands": ["EXT-007"]
  },
  "cause_D_embed_failure_exclusion": {
    "description": "EXT-039 cannot generate 3D coordinates under RDKit DG, RDKit random-coords, or OBabel --gen3d within reasonable compute (folded cyclic macrocycle). Declared EMBED_FAILURE and excluded; NOT silently dropped. Panel target becomes 39 ligands x 8 states = 312 records.",
    "ligand": "EXT-039",
    "attempts": ["RDKit ETKDGv2 seed42", "RDKit random-coords seeds (42,2026,7,12345)", "OBabel --gen3d (280s timeout)"]
  }
}
EOF
echo "=== Repair ledger written: $LEDGER ==="
echo "=== Repaired COMPLETE: $salt_ids $obabel_ids + EXT-007; EXT-039 declared EMBED_FAILURE ==="