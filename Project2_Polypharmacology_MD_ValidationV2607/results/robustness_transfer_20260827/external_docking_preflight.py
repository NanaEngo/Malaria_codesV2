#!/usr/bin/env python3
"""Fail-closed preflight for the conditional external P2 docking replication.

This command performs no docking and never edits canonical P2 outputs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from rdkit import Chem

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "robustness_transfer_20260827"
PANEL = OUT / "external_docking_panel_candidate_40.csv"
P2 = ROOT / "results" / "candidate_selection" / "md_top20_candidates_polypharm.csv"
PREP = ROOT / "results" / "md_systems" / "set_c_preparation_20260812_v1"
GRID_ROOT = ROOT / "data" / "from_project1" / "docking"

STATES = {
    "PfDHFR_WT": PREP / "PP-01_PfDHFR_WT" / "receptor_fixed.pdb",
    "PfDHFR_N51I": PREP / "PP-01_PfDHFR_N51I" / "receptor_fixed.pdb",
    "PfDHFR_C59R": PREP / "PP-01_PfDHFR_C59R" / "receptor_fixed.pdb",
    "PfDHFR_S108N": PREP / "PP-01_PfDHFR_S108N" / "receptor_fixed.pdb",
    "PfDHFR_I164L": PREP / "PP-01_PfDHFR_I164L" / "receptor_fixed.pdb",
    "PfCRT_WT": PREP / "PP-01_PfCRT_WT" / "receptor_fixed.pdb",
    "PfCRT_K76T": PREP / "PP-01_PfCRT_K76T" / "receptor_fixed.pdb",
    "PfCRT_K76A": PREP / "PP-01_PfCRT_K76A" / "receptor_fixed.pdb",
}
GRIDS = {
    "PfDHFR": GRID_ROOT / "Docking_7F3Y" / "config.txt",
    "PfCRT": GRID_ROOT / "Docking_6UKJ" / "config.txt",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    blockers: list[str] = []
    checks: dict[str, object] = {}
    if not PANEL.exists(): blockers.append("missing candidate panel")
    if not P2.exists(): blockers.append("missing P2 candidate reference")
    if not blockers:
        panel = pd.read_csv(PANEL); p2 = pd.read_csv(P2)
        required = {"external_panel_id", "smiles", "activity", "pchembl"}
        missing = sorted(required - set(panel.columns))
        if missing: blockers.append(f"panel missing columns: {missing}")
        mols = [Chem.MolFromSmiles(str(s)) for s in panel.smiles]
        invalid = sum(m is None for m in mols)
        canonical = [Chem.MolToSmiles(m, canonical=True) if m else None for m in mols]
        p2_canonical = {Chem.MolToSmiles(m, canonical=True) for m in (Chem.MolFromSmiles(str(s)) for s in p2.smiles) if m}
        overlap = set(canonical) & p2_canonical
        if invalid: blockers.append(f"invalid SMILES: {invalid}")
        if overlap: blockers.append(f"standardized P2 overlap: {len(overlap)}")
        if len(panel) < 20: blockers.append("fewer than 20 eligible ligands")
        checks = {"panel_rows": len(panel), "panel_unique_raw_smiles": int(panel.smiles.nunique()), "panel_unique_canonical_smiles": len(set(canonical)), "invalid_smiles": invalid, "standardized_p2_overlap": len(overlap), "activity_counts": {str(k): int(v) for k,v in panel.activity.value_counts().to_dict().items()}}
    receptor_records = {}
    for state, path in STATES.items():
        exists = path.is_file(); rec = {"path": str(path.relative_to(ROOT)), "exists": exists}
        if exists: rec["sha256"] = sha(path)
        else: blockers.append(f"missing prepared receptor: {state}")
        receptor_records[state] = rec
    grid_records = {}
    for target, path in GRIDS.items():
        exists=path.is_file(); rec={"path":str(path.relative_to(ROOT)),"exists":exists}
        if exists:
            rec["sha256"]=sha(path); rec["content"]=path.read_text()
        else: blockers.append(f"missing grid config: {target}")
        grid_records[target]=rec
    manifest = {
        "schema_version": 2,
        "status": "BLOCKED_PENDING_PARAMETER_RECONCILIATION" if blockers else "PASS_PREPARATION_ONLY_NOT_AUTHORIZED_TO_DOCK",
        "purpose": "Preflight only; no docking executed",
        "checks": checks,
        "receptor_state_artifacts": receptor_records,
        "grid_artifacts": grid_records,
        "protocol_frozen_for_external_replication": {"software":"AutoDock Vina 1.2.7", "exhaustiveness":64, "box_size_angstrom":[25,25,25], "rrs_wt_floor_kcal_mol":5.0, "basis":"audited V2 configuration files and DAR execution record"},
        "historical_parameter_conflict": "An outdated Set-C Methods sentence stated 20 Å; the DAR and audited V2 grid files establish 25 Å with exhaustiveness=64. The sentence has been corrected before any external docking execution.",
        "blockers": blockers,
        "boundary": "No receptor preparation, PDBQT generation, docking, RRS calculation, or canonical-output modification was performed."
    }
    path=OUT/"external_docking_preflight_manifest.json"; path.write_text(json.dumps(manifest,indent=2)+"\n"); print(json.dumps(manifest,indent=2))
    return 0 if not blockers else 2

if __name__ == "__main__": raise SystemExit(main())
