#!/usr/bin/env python3
"""P1 V5 — docking-RRS pilot: Vina grid-restrained docking on the mutant panel.

Panel (uniform protein-only protocol, results/rrs_pilot/receptors/):
  PfDHFR (7F3Y frame, MTX-A702 anchor, 18 A box):
      PfDHFR_WT, PfDHFR_N51I, PfDHFR_C59R, PfDHFR_S108N, PfDHFR_I164L
  PfCRT (6UKJ frame, Y01-A501 anchor, 28 A box):
      PfCRT_WT_K76 (T76K revertant), PfCRT_K76T (7G8, as-is), PfCRT_K76A

Same composite biological gate as the 17x4 WT runs: (1) rank-1 centroid in
the declared box, (2) >= 1 pose atom within 10 A of the anchor atom set,
(3) >= 90% of pose atoms inside box + 0.5 A padding. Affinity is never
converted to a binding constant; no consensus/RRS/PNS is computed here
(the separate p1_v5_rrs_pilot.py applies the per-target RRS protocol).

Outputs:
  results/rrs_pilot/vina_scores/<RECEPTOR>/<complex>/...
  results/rrs_pilot/vina_scores/v5_mutant_vina_scores_<TARGET>.csv   (per-target)
  results/rrs_pilot/vina_scores/execution_provenance_<TARGET>.json

The per-target CSV avoids clobbering when the PfDHFR and PfCRT panels run as
two parallel SLURM jobs (12892/12893); p1_v5_rrs_merge_scores.py merges them
into v5_mutant_vina_scores.csv for p1_v5_rrs_pilot.py.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
RECEPTORS = V5 / "results/rrs_pilot/receptors"
VINA = shutil.which("vina") or "/usr/local/bin/vina"
ANCHOR_CONTACT_A = 10.0
MIN_FRACTION = 0.90
VERIFY_PADDING = 0.5
EXHAUSTIVENESS = 16
NUM_MODES = 9
SEED = 0

# Receptor label -> (WT PDB for anchor, box)
TARGETS = {
    "PfDHFR": {"wt_pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb",
               "box": (18.0, 18.0, 18.0),
               "anchor": {"resname": "MTX", "chain": "A", "resi": "702"},
               "label": "MTX co-crystallized inhibitor (catalytic-site copy A702)",
               "receptors": ["PfDHFR_WT", "PfDHFR_N51I", "PfDHFR_C59R",
                             "PfDHFR_S108N", "PfDHFR_I164L"]},
    "PfCRT": {"wt_pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/6UKJ.pdb",
              "box": (28.0, 28.0, 28.0),
              "anchor": {"resname": "Y01"},
              "label": "Y01 cholesterol hemisuccinate (membrane-proxy, not an inhibitor)",
              "receptors": ["PfCRT_WT_K76", "PfCRT_K76T", "PfCRT_K76A"]},
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def require_file(p: Path, label: str) -> None:
    if not p.is_file() or p.stat().st_size == 0:
        raise SystemExit(f"FAIL-CLOSED missing/empty {label}: {p}")


def anchor_centroid_and_atoms(pdb: Path, resname: str, chain=None, resi=None):
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
        raise SystemExit(f"FAIL-CLOSED no {resname} anchor atoms in {pdb.name}")
    return np.mean(np.asarray(pts), axis=0), np.asarray(pts)


def rank1_gate(pdbqt_path: Path, center, box, anchor_atoms) -> tuple:
    coords, mc = [], 0
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
    arr = np.asarray(coords)
    c, b = center, np.asarray(box) + 2 * VERIFY_PADDING
    fraction = float(np.all((arr >= c - b / 2) & (arr <= c + b / 2), axis=1).mean())
    centroid = arr.mean(axis=0)
    cib = bool(np.all((centroid >= c - np.asarray(box) / 2) & (centroid <= c + np.asarray(box) / 2)))
    anchor_min = float(min(np.min(np.linalg.norm(arr - t, axis=1)) for t in anchor_atoms))
    return True, fraction, len(arr), anchor_min, cib


def prepare_ligand_pdbqt(smiles: str, pair_dir: Path) -> Path:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from meeko import MoleculePreparation, PDBQTWriterLegacy
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise SystemExit(f"FAIL-CLOSED parse SMILES: {smiles[:60]}")
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, randomSeed=SEED, useRandomCoords=True) != 0:
        raise SystemExit(f"FAIL-CLOSED embedding failed: {smiles[:60]}")
    AllChem.ComputeGasteigerCharges(mol)
    prep = MoleculePreparation(merge_these_atom_types=("H",), hydrate=False,
                               flexible_amides=False, rigid_macrocycles=False,
                               min_ring_size=7, double_bond_penalty=50,
                               charge_model="gasteiger", load_atom_params="ad4_types")
    prepared = prep.prepare(mol)
    if not prepared:
        raise SystemExit(f"FAIL-CLOSED meeko prepare failed: {smiles[:40]}")
    pdbqt_string, ok, err = PDBQTWriterLegacy.write_string(prepared[0])
    if not ok:
        raise SystemExit(f"FAIL-CLOSED PDBQT writer: {err}")
    out = pair_dir / "ligand.pdbqt"
    out.write_text(pdbqt_string)
    return out


def parse_vina_affinity(text: str) -> float:
    m = re.findall(r"^\s*\d+\s+([-+]?\d+(?:\.\d+)?)\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s*$",
                   text, flags=re.MULTILINE)
    if len(m) < 1:
        raise ValueError("no Vina mode rows found")
    return float(m[0])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, choices=sorted(TARGETS))
    ap.add_argument("--receptor", default=None,
                    help="single receptor label (smoke test); default = all")
    ap.add_argument("--limit-pairs", type=int, default=None)
    ap.add_argument("--output-root", type=Path, default=V5 / "results/rrs_pilot/vina_scores")
    ap.add_argument("--out-csv", type=Path, default=None,
                    help="per-target output CSV (default: v5_mutant_vina_scores_<TARGET>.csv "
                         "in --output-root; avoids clobbering across parallel jobs)")
    ap.add_argument("--exhaustiveness", type=int, default=EXHAUSTIVENESS)
    args = ap.parse_args()

    if args.out_csv is None:
        args.out_csv = args.output_root / f"v5_mutant_vina_scores_{args.target}.csv"

    spec = TARGETS[args.target]
    require_file(Path(VINA), "AutoDock Vina")
    require_file(MANIFEST, "V5 manifest")
    center, anchor_atoms = anchor_centroid_and_atoms(
        spec["wt_pdb"], spec["anchor"]["resname"],
        chain=spec["anchor"].get("chain"), resi=spec["anchor"].get("resi"))

    receptors = [args.receptor] if args.receptor else spec["receptors"]
    out_root = args.output_root
    out_root.mkdir(parents=True, exist_ok=True)

    with MANIFEST.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    pairs = [r for r in rows if r["target"] == args.target]
    if len(pairs) != 17:
        raise SystemExit(f"FAIL-CLOSED expected 17 {args.target} rows, got {len(pairs)}")
    if args.limit_pairs:
        pairs = pairs[: args.limit_pairs]

    records = []
    for rlabel in receptors:
        pdbqt = RECEPTORS / f"{rlabel}.pdbqt"
        pdb = RECEPTORS / f"{rlabel}.pdb"
        require_file(pdbqt, f"{rlabel} receptor PDBQT")
        require_file(pdb, f"{rlabel} receptor PDB")
        for r in pairs:
            pair_dir = out_root / rlabel / r["complex_name"]
            pair_dir.mkdir(parents=True, exist_ok=True)
            lig = prepare_ligand_pdbqt(r["ligand_description"], pair_dir)
            cx, cy, cz = center
            cmd = [VINA, "--receptor", str(pdbqt), "--ligand", str(lig),
                   "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
                   "--size_x", str(spec["box"][0]), "--size_y", str(spec["box"][1]),
                   "--size_z", str(spec["box"][2]),
                   "--exhaustiveness", str(args.exhaustiveness),
                   "--num_modes", str(NUM_MODES), "--seed", str(SEED),
                   "--out", str((pair_dir / "vina_out.pdbqt").resolve())]
            res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
            (pair_dir / "vina_dock.log").write_text(res.stdout + res.stderr)
            if res.returncode != 0:
                raise SystemExit(f"FAIL-CLOSED Vina failed {rlabel}/{r['complex_name']}")
            out = pair_dir / "vina_out.pdbqt"
            require_file(out, "vina output")
            aff = parse_vina_affinity(res.stdout + res.stderr)
            ok, frac, n_atoms, amin, cib = rank1_gate(out, center, spec["box"], anchor_atoms)
            gate = ok and cib and amin <= ANCHOR_CONTACT_A and frac >= MIN_FRACTION
            if not gate:
                raise SystemExit(
                    f"FAIL-CLOSED {rlabel}/{r['complex_name']} gate: ok={ok} cib={cib} "
                    f"anchor_min={amin:.2f} frac={frac:.3f}")
            records.append({
                "candidate_id": r["candidate_id"], "target": args.target,
                "receptor": rlabel, "mutation": rlabel.split("_", 1)[1]
                    if rlabel.startswith("PfDHFR") else rlabel.replace("PfCRT_", ""),
                "vina_affinity_kcal_mol": aff, "rank1_inside_fraction": frac,
                "rank1_atom_count": n_atoms, "rank1_anchor_min_A": amin,
                "rank1_centroid_in_box": cib,
                "ligand_pdbqt_sha256": sha256(lig), "vina_out_pdbqt_sha256": sha256(out),
            })
            print(f"{rlabel:16s} {r['complex_name']:10s} aff={aff:7.3f} amin={amin:5.2f} frac={frac:.3f}")

    csv_path = args.out_csv
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)
    prov = {
        "schema": "p1-v5-rrs-pilot-vina/v1",
        "status": "VINA_GRID_DOCK_MUTANT_PANEL_RANK1_VERIFIED",
        "target": args.target, "receptors": receptors, "pairs_per_receptor": len(pairs),
        "n_records": len(records), "center_A": np.round(center, 3).tolist(),
        "box_A": list(spec["box"]), "anchor": spec["label"],
        "protocol": "uniform protein-only receptors (results/rrs_pilot/receptors), "
                    "obabel -xr PDBQT, composite biological gate",
        "gate": {"centroid_in_box": True, "anchor_contact_A": ANCHOR_CONTACT_A,
                 "min_fraction": MIN_FRACTION, "padding_A": VERIFY_PADDING},
        "exhaustiveness": args.exhaustiveness, "num_modes": NUM_MODES, "seed": SEED,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "output_csv_sha256": sha256(csv_path),
        "consensus_scores_written": False, "rrs_pns_updated": False,
        "accepted_for_full_run": False,
        "next_gate": "independent review of receptor identities and anchors; "
                     "then p1_v5_rrs_pilot.py may compute the per-target RRS",
    }
    (out_root / f"execution_provenance_{args.target}.json").write_text(
        json.dumps(prov, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": prov["status"], "target": args.target,
                      "records": len(records), "out": str(csv_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
