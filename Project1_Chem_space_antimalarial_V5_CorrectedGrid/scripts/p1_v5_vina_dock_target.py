#!/usr/bin/env python3
"""Fail-closed Vina grid-restrained docking for P1 V5 target pairs.

Replaces the PfClpP-only runner with a generalized version. For each target, the
declared grid center is bound to an authentic structural anchor:
  - PfDHFR / 7F3Y : MTX co-crystallized inhibitor heavy-atom centroid (defensible).
  - PfClpP / 2F6I : chain A catalytic triad Ser252/His223/Asp219 centroid
    (genuine PfClpP; 4GM2 is PfClpR and must not be used).
  - PfCRT  / 6UKJ : Y01 (cholesterol hemisuccinate) centroid - membrane-mimetic
    PROXY, not an antimalarial inhibitor; docked with an explicit caveat and
    excluded from any primary claim without independent mutational/transport
    evidence (per structural dossier PROXY_NOT_ACCEPTED).
  - PfATP4 / 9N10 : NO co-crystallized small-molecule anchor -> runner refuses
    (CAVITY_EVIDENCE_REQUIRED); PfATP4 cannot be docked defensibly.

Verification gate (composite, biological, per pair):
  (1) rank-1 centroid inside the declared box (search-space control, Vina-guaranteed);
  (2) at least one pose atom within ANCHOR_CONTACT_A of an anchor atom (pocket contact);
  (3) >= MIN_FRACTION of pose atoms inside box + grid-discretization padding.
Affinity is never converted to a binding constant; no GROMACS/consensus/RRS/PNS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
VINA = shutil.which("vina") or "/usr/local/bin/vina"

# Anchor atoms per target (2F6I: chain A triad; 7F3Y: MTX atoms; 6UKJ: Y01 atoms)
ANCHOR_ATOMS = {
    "PfDHFR": {"pdb_id": "7F3Y", "anchor_label": "MTX co-crystallized inhibitor (catalytic-site copy A702)",
               "receptor_pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb",
               "receptor_pdbqt": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/7F3Y.pdbqt",
               "center": None, "anchor_resname": "MTX", "anchor_chain": "A", "anchor_resi": "702",
               "box": (18.0, 18.0, 18.0),
               "box_note": "18 A box centered on the MTX catalytic-site copy (A702) confines the search to the DHFR active site; the global MTX centroid mixes 3 partial copies (A702/A704/B702) and the old V5 center was the receptor centroid (verified 08/08/2026: A702 contacts Phe58/Phe116/Ile14/Ile164/Cys15/Asp54 — the canonical DHFR pocket)."},
    "PfClpP": {"pdb_id": "2F6I", "anchor_label": "chain A catalytic triad Ser252/His223/Asp219",
               "receptor_pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb",
               "receptor_pdbqt": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/2F6I.pdbqt",
               "center": np.asarray([-24.276, 17.28, -2.901], dtype=float),
               "anchor_atoms": np.asarray([[-22.232, 15.984, -2.161], [-26.372, 18.249, -4.879], [-24.225, 17.608, -1.663]], dtype=float),
               "box": (28.0, 28.0, 28.0)},
    "PfCRT": {"pdb_id": "6UKJ", "anchor_label": "Y01 cholesterol hemisuccinate (PROXY, not an inhibitor)",
              "receptor_pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/6UKJ.pdb",
              "receptor_pdbqt": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/6UKJ.pdbqt",
              "center": None, "anchor_resname": "Y01", "box": (28.0, 28.0, 28.0),
              "caveat": "Y01 is a membrane-mimetic stabilizing proxy, not a co-crystallized antimalarial inhibitor (structural dossier PROXY_NOT_ACCEPTED); results are exploratory only."},
    "PfATP4": {"pdb_id": "9N10", "anchor_label": "NONE - no co-crystallized small-molecule anchor",
               "receptor_pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/9N10.pdb",
               "receptor_pdbqt": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/proteins/9N10.pdbqt",
               "center": None, "anchor_resname": None, "box": (28.0, 28.0, 28.0),
               "blocked_reason": "CAVITY_EVIDENCE_REQUIRED: no co-crystallized small-molecule inhibitor (9N10 has PfABP protein partner only); arbitrary coordinates are not accepted."},
}
VERIFY_PADDING = 0.5
ANCHOR_CONTACT_A = 10.0
MIN_FRACTION = 0.90
EXHAUSTIVENESS = 16
NUM_MODES = 9
SEED = 0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"FAIL-CLOSED missing/empty {label}: {path}")


def anchor_centroid_and_atoms(pdb: Path, resname: str, chain: str | None = None,
                              resi: str | None = None):
    """Anchor centroid/atoms for a ligand, optionally restricted to one instance.

    7F3Y contains 3 partial MTX copies (A702 catalytic-site, A704, B702 mirror);
    taking the global MTX centroid mixes sites (same error class as the PfClpP
    barrel channel). The catalytic-site copy must be selected explicitly.
    """
    pts = []
    for line in pdb.read_text(errors="replace").splitlines():
        if not (line.startswith("HETATM") and line[17:20].strip() == resname):
            continue
        if chain is not None and line[21:22].strip() != chain:
            continue
        if resi is not None and line[22:26].strip() != resi:
            continue
        try:
            pts.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
    if not pts:
        raise SystemExit(f"FAIL-CLOSED no {resname} anchor atoms found in {pdb.name} "
                         f"(chain={chain}, resi={resi})")
    return np.mean(np.asarray(pts, dtype=float), axis=0), np.asarray(pts, dtype=float)


def ca_frame_equivalence(pdb: Path, pdbqt: Path) -> dict:
    def read_ca(path: Path):
        out = {}
        for line in path.read_text(errors="replace").splitlines():
            if not line.startswith(("ATOM  ", "HETATM")) or line[12:16].strip() != "CA":
                continue
            try:
                out[(line[21:22].strip(), line[22:26].strip())] = np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
        return out
    a, b = read_ca(pdb), read_ca(pdbqt)
    missing = sorted(set(b) - set(a))
    if missing:
        raise SystemExit(f"FAIL-CLOSED PDBQT CA not present in PDB: {missing[:10]}")
    common = sorted(set(a) & set(b))
    delta = np.asarray([a[k] - b[k] for k in common], dtype=float)
    rmsd = float(np.sqrt(np.mean(delta ** 2)))
    max_norm = float(np.max(np.linalg.norm(delta, axis=1)))
    if rmsd > 1e-6 or max_norm > 1e-6:
        raise SystemExit(f"FAIL-CLOSED PDBQT/PDB CA mismatch: rmsd={rmsd}, max={max_norm}")
    return {"method": "CA subset, identical coordinates", "pdb_ca": len(a), "pdbqt_ca": len(b),
            "common_ca": len(common), "rmsd_A": rmsd, "status": "CA_SUBSET_FRAME_EQUIVALENT"}


def parse_vina_affinity(text: str) -> float:
    matches = re.findall(r"^\s*\d+\s+([-+]?\d+(?:\.\d+)?)\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s*$", text, flags=re.MULTILINE)
    if len(matches) < NUM_MODES:
        raise ValueError(f"expected at least {NUM_MODES} mode rows in Vina table, found {len(matches)}")
    return float(matches[0])


def rank1_gate(pdbqt_path: Path, center: np.ndarray, box: tuple, anchor_atoms: np.ndarray,
               padding: float = VERIFY_PADDING) -> tuple[bool, float, int, float, bool]:
    coords = []
    mc = 0
    for line in pdbqt_path.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            mc += 1
            if mc > 1:
                break
            continue
        if line.startswith(("ATOM  ", "HETATM")) and mc == 1:
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
            except ValueError:
                continue
    if not coords:
        return False, 0.0, 0, float("inf"), False
    arr = np.asarray(coords, dtype=float)
    c = center
    b = np.asarray(box, dtype=float) + 2 * padding
    fraction = float(np.all((arr >= c - b / 2) & (arr <= c + b / 2), axis=1).mean())
    centroid = arr.mean(axis=0)
    centroid_in_box = bool(np.all((centroid >= c - np.asarray(box) / 2) & (centroid <= c + np.asarray(box) / 2)))
    anchor_min = float(min(np.min(np.linalg.norm(arr - t, axis=1)) for t in anchor_atoms))
    return True, fraction, len(arr), anchor_min, centroid_in_box


def prepare_ligand_pdbqt(smiles: str, pair_dir: Path) -> tuple[Path, Path]:
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        from meeko import MoleculePreparation, PDBQTWriterLegacy
    except ImportError as exc:
        raise SystemExit(f"FAIL-CLOSED rdkit/meeko unavailable: {exc}")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise SystemExit(f"FAIL-CLOSED RDKit could not parse SMILES: {smiles[:60]}")
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, randomSeed=SEED, useRandomCoords=True) != 0:
        raise SystemExit(f"FAIL-CLOSED RDKit 3D embedding failed for SMILES: {smiles[:60]}")
    AllChem.ComputeGasteigerCharges(mol)
    charges = [float(atom.GetProp("_GasteigerCharge")) for atom in mol.GetAtoms()]
    if not all(v == v and abs(v) < 1e100 for v in charges):
        raise SystemExit("FAIL-CLOSED non-finite Gasteiger charges")
    preparator = MoleculePreparation(
        merge_these_atom_types=("H",), hydrate=False, flexible_amides=False,
        rigid_macrocycles=False, min_ring_size=7, double_bond_penalty=50,
        charge_model="gasteiger", load_atom_params="ad4_types",
    )
    prepared = preparator.prepare(mol)
    if not prepared:
        raise SystemExit(f"FAIL-CLOSED Meeko no prepared molecule for {smiles[:40]}")
    pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(prepared[0])
    if not is_ok:
        raise SystemExit(f"FAIL-CLOSED PDBQT writer failed: {error_msg}")
    ligand_pdbqt = pair_dir / "ligand.pdbqt"
    ligand_pdbqt.write_text(pdbqt_string, encoding="utf-8")
    conversion_log = pair_dir / "meeko_conversion.log"
    conversion_log.write_text(f"conversion_method=SMILES_EmbedMolecule_seeded_Meeko_API\nembed_seed={SEED}\nstatus=PASS\n", encoding="utf-8")
    return ligand_pdbqt, conversion_log


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, choices=sorted(ANCHOR_ATOMS))
    ap.add_argument("--output-dir", type=Path, default=None)
    ap.add_argument("--limit-pairs", type=int, default=None)
    ap.add_argument("--exhaustiveness", type=int, default=EXHAUSTIVENESS)
    ap.add_argument("--num-modes", type=int, default=NUM_MODES)
    args = ap.parse_args()
    spec = ANCHOR_ATOMS[args.target]
    if spec.get("blocked_reason"):
        raise SystemExit(f"FAIL-CLOSED {args.target} blocked: {spec['blocked_reason']}")
    require_file(Path(VINA), "AutoDock Vina")
    require_file(spec["receptor_pdb"], f"{args.target} receptor PDB")
    require_file(spec["receptor_pdbqt"], f"{args.target} receptor PDBQT")
    require_file(MANIFEST, "V5 manifest")
    version = subprocess.run([VINA, "--version"], text=True, capture_output=True).stdout.strip()
    frame = ca_frame_equivalence(spec["receptor_pdb"], spec["receptor_pdbqt"])
    if spec.get("anchor_resname"):
        center, anchor_atoms = anchor_centroid_and_atoms(
            spec["receptor_pdb"], spec["anchor_resname"],
            chain=spec.get("anchor_chain"), resi=spec.get("anchor_resi"),
        )
    else:
        center, anchor_atoms = spec["center"], spec["anchor_atoms"]
    output = args.output_dir or (V5 / f"results/vina_dock_{spec['pdb_id']}_{args.target}_17")
    if not output.is_absolute():
        output = ROOT / output
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"FAIL-CLOSED output directory exists and is non-empty: {output}")
    output.mkdir(parents=True, exist_ok=False)
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    target_rows = [r for r in rows if r["target"] == args.target]
    if len(target_rows) != 17:
        raise SystemExit(f"FAIL-CLOSED expected 17 {args.target} rows, found {len(target_rows)}")
    if args.target == "PfClpP":
        for r in target_rows:
            if r["pdb_id"] != "2F6I":
                raise SystemExit(f"FAIL-CLOSED PfClpP row does not reference 2F6I: {r['complex_name']}")
    if args.limit_pairs:
        if not (1 <= args.limit_pairs <= 17):
            raise SystemExit("FAIL-CLOSED --limit-pairs must be in [1,17]")
        target_rows = target_rows[:args.limit_pairs]
    started = datetime.now(timezone.utc).isoformat()
    records = []
    for r in target_rows:
        pair_dir = output / r["complex_name"]
        pair_dir.mkdir()
        ligand_pdbqt, conversion_log = prepare_ligand_pdbqt(r["ligand_description"], pair_dir)
        cx, cy, cz = center
        cmd = [VINA, "--receptor", str(spec["receptor_pdbqt"].resolve()),
               "--ligand", str(ligand_pdbqt.resolve()),
               "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
               "--size_x", str(spec["box"][0]), "--size_y", str(spec["box"][1]), "--size_z", str(spec["box"][2]),
               "--exhaustiveness", str(args.exhaustiveness), "--num_modes", str(args.num_modes),
               "--seed", str(SEED), "--out", str((pair_dir / "vina_out.pdbqt").resolve())]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        vina_log = pair_dir / "vina_dock.log"
        vina_log.write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode != 0:
            (output / "RUN_FAILED_NO_ACCEPTED_RESULT").write_text("Incomplete Vina docking.\n", encoding="utf-8")
            raise SystemExit(f"FAIL-CLOSED Vina failed for {r['complex_name']}: see {vina_log}")
        out_pdbqt = pair_dir / "vina_out.pdbqt"
        require_file(out_pdbqt, f"Vina output for {r['complex_name']}")
        affinity = parse_vina_affinity(result.stdout + result.stderr)
        valid, fraction, atoms, anchor_min, centroid_in_box = rank1_gate(out_pdbqt, center, spec["box"], anchor_atoms)
        gate_pass = valid and centroid_in_box and anchor_min <= ANCHOR_CONTACT_A and fraction >= MIN_FRACTION
        if not gate_pass:
            (output / "RUN_FAILED_NO_ACCEPTED_RESULT").write_text("Incomplete Vina docking.\n", encoding="utf-8")
            raise SystemExit(f"FAIL-CLOSED {r['complex_name']} fails gate: valid={valid} centroid_in_box={centroid_in_box} anchor_min={anchor_min:.2f} fraction={fraction:.3f}")
        records.append({
            "complex_name": r["complex_name"], "candidate_id": r["candidate_id"], "target": r["target"],
            "pdb_id": spec["pdb_id"], "vina_affinity_kcal_mol": affinity,
            "rank1_inside_fraction": fraction, "rank1_atom_count": atoms,
            "rank1_anchor_min_A": anchor_min, "rank1_centroid_in_box": centroid_in_box,
            "ligand_pdbqt_sha256": sha256(ligand_pdbqt), "vina_out_pdbqt_sha256": sha256(out_pdbqt),
            "conversion_log_sha256": sha256(conversion_log), "vina_log_sha256": sha256(vina_log),
            "vina_command": cmd,
        })
    out_csv = output / f"vina_dock_{spec['pdb_id']}_{args.target}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0])); w.writeheader(); w.writerows(records)
    provenance = {
        "schema": "p1-v5-vina-grid-dock-target/v1",
        "status": "VINA_GRID_DOCK_RANK1_VERIFIED_IN_GRID",
        "target": args.target, "pdb_id": spec["pdb_id"], "anchor": spec["anchor_label"],
        "caveat": spec.get("caveat"),
        "pairs": len(records), "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "vina_executable": str(Path(VINA).resolve()), "vina_version": version,
        "receptor_pdbqt_sha256": sha256(spec["receptor_pdbqt"]), "receptor_pdb_sha256": sha256(spec["receptor_pdb"]),
        "pdb_pdbqt_frame_equivalence": frame,
        "center": np.round(center, 3).tolist(), "box_A": list(spec["box"]), "verify_padding_A": VERIFY_PADDING,
        "gate": {"centroid_in_box": True, "anchor_contact_A": ANCHOR_CONTACT_A, "min_fraction": MIN_FRACTION},
        "exhaustiveness": args.exhaustiveness, "num_modes": args.num_modes, "seed": SEED,
        "manifest_sha256": sha256(MANIFEST), "output_csv_sha256": sha256(out_csv),
        "all_rank1_pass_gate": True, "consensus_scores_written": False, "rrs_pns_updated": False,
        "accepted_for_full_run": False,
        "next_gate": "independent review of receptor identities and anchors before consensus/RRS/PNS",
    }
    (output / "execution_provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": provenance["status"], "target": args.target, "pairs": len(records), "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
