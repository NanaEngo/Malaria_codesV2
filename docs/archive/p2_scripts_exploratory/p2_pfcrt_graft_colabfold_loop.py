#!/usr/bin/env python3
"""Graft ColabFold PfCRT residues 114--122 onto experimental 6UKJ chain A.

This is a technical reconstruction, not experimental validation. The script
never edits canonical PDBs or Set-C directories. It writes one candidate per
ColabFold model and a JSON audit. Selection is based only on predeclared
structural confidence and geometry, never on docking or ligand scores.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from Bio.PDB import PDBIO, PDBParser

EXPECTED = {114: "N", 115: "K", 116: "K", 117: "G", 118: "N", 119: "S", 120: "K", 121: "E", 122: "R"}
THREE_TO_ONE = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
BACKBONE = ("N", "CA", "C", "O")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def residue_map(chain):
    return {res.id[1]: res for res in chain if res.id[0] == " " and res.id[2] == " "}


def model_chain(structure, chain_id="A"):
    for model in structure:
        if chain_id in model.child_dict:
            return model[chain_id]
    raise ValueError(f"chain {chain_id!r} not found")


def one_letter(res):
    return THREE_TO_ONE.get(res.resname.strip(), "?")


def kabsch_transform(source: np.ndarray, target: np.ndarray):
    src_cent = source.mean(axis=0)
    tgt_cent = target.mean(axis=0)
    src0 = source - src_cent
    tgt0 = target - tgt_cent
    cov = src0.T @ tgt0
    v, _, wt = np.linalg.svd(cov)
    d = np.sign(np.linalg.det(v @ wt))
    if d == 0:
        d = 1.0
    # Row-vector convention: source @ rot + trans = target. For
    # H = source.T @ target, the SVD factors U, Vt give U D Vt.
    # This is verified by the repository smoke test for row vectors.
    rot = v @ np.diag([1.0, 1.0, d]) @ wt
    trans = tgt_cent - src_cent @ rot
    return rot, trans


def atom_coord(res, name):
    if name not in res:
        raise ValueError(f"residue {res.id[1]} lacks atom {name}")
    return np.asarray(res[name].coord, dtype=float)


def all_heavy(chain):
    out = []
    for res in chain:
        if res.id[0] != " ":
            continue
        for atom in res:
            element = (atom.element or atom.name[:1]).upper()
            if element != "H":
                out.append((res.id[1], atom.name.strip(), np.asarray(atom.coord, dtype=float)))
    return out


def plddt(loop_residues):
    vals = [float(atom.bfactor) for res in loop_residues for atom in res]
    return float(np.mean(vals)) if vals else float("nan")


def audit_geometry(chain):
    residues = residue_map(chain)
    required = list(range(113, 124))
    if any(n not in residues for n in required):
        return {"pass": False, "reason": "missing_flank_or_loop_residue"}
    coords = [np.asarray(atom.coord, dtype=float) for n in required for atom in residues[n]]
    finite = bool(coords) and bool(np.isfinite(np.asarray(coords)).all())
    peptide = {}
    for left in range(113, 123):
        try:
            peptide[f"{left}-{left+1}"] = float(np.linalg.norm(atom_coord(residues[left], "C") - atom_coord(residues[left + 1], "N")))
        except ValueError:
            peptide[f"{left}-{left+1}"] = float("nan")
    peptide_ok = all(math.isfinite(v) and 1.0 <= v <= 1.8 for v in peptide.values())
    loop_atoms = [(r, a, c) for r in range(114, 123) for rr, a, c in all_heavy(chain) if rr == r]
    # Include the immediate flanks in the non-bonded screen. Exclude only
    # same-residue pairs and directly bonded neighboring residues, whose short
    # distances are chemically required rather than steric clashes.
    core = all_heavy(chain)
    min_dist = float("inf")
    min_pair = None
    for r, a, c in loop_atoms:
        for rr, aa, cc in core:
            if rr in range(114, 123) or abs(r - rr) <= 1:
                continue
            d = float(np.linalg.norm(c - cc))
            if d < min_dist:
                min_dist, min_pair = d, [r, a, rr, aa]
    clash_ok = math.isfinite(min_dist) and min_dist >= 1.6
    seq = "".join(one_letter(residues[n]) for n in range(114, 123))
    return {
        "pass": bool(finite and peptide_ok and clash_ok and seq == "NKKGNSKER"),
        "sequence_114_122": seq,
        "finite_coordinates": finite,
        "peptide_bond_distances_A": peptide,
        "peptide_bonds_plausible": peptide_ok,
        "minimum_loop_to_core_heavy_atom_distance_A": min_dist,
        "minimum_loop_to_core_pair": min_pair,
        "core_clash_screen_pass": clash_ok,
        "loop_plddt_mean": plddt([residues[n] for n in range(114, 123)]),
    }


def validate_provenance(reference_path: Path, prediction_dir: Path, mapping_path: Path):
    """Verify immutable input/output hashes before any coordinates are grafted."""
    preflight_path = prediction_dir / "provenance_preflight.json"
    completion_candidates = (
        prediction_dir / "provenance_colabfold_completed.json",
        prediction_dir / "provenance_ensemble_completed.json",
    )
    completion_path = next((p for p in completion_candidates if p.is_file()), None)
    if not preflight_path.is_file() or completion_path is None:
        raise ValueError("missing ColabFold preflight or completion provenance")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    completion = json.loads(completion_path.read_text(encoding="utf-8"))
    if preflight.get("accession") != "W7FI62" or completion.get("accession") != "W7FI62":
        raise ValueError("ColabFold provenance accession is not W7FI62")
    if completion.get("status") not in {"COLABFOLD_COMPLETED", "COLABFOLD_ENSEMBLE_COMPLETED"}:
        raise ValueError("ColabFold completion manifest is not complete")
    if preflight.get("sequence_sha256") != completion.get("sequence_sha256"):
        raise ValueError("preflight/completion FASTA hashes differ")
    fasta = Path(preflight.get("sequence_path", ""))
    if not fasta.is_file() or sha256(fasta) != preflight.get("sequence_sha256"):
        raise ValueError("ColabFold FASTA hash does not match the current file")
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    declared_pdb_hash = mapping.get("reference", {}).get("pdb_sha256")
    if declared_pdb_hash != sha256(reference_path):
        raise ValueError("mapping PDB hash does not match the 6UKJ reference used for grafting")
    output_hashes = completion.get("outputs", {})
    if not isinstance(output_hashes, dict):
        raise ValueError("completion manifest has no output hash map")
    for relative_name, declared_hash in output_hashes.items():
        output = prediction_dir / relative_name
        if not output.is_file() or sha256(output) != declared_hash:
            raise ValueError(f"completion output hash mismatch: {relative_name}")
    return preflight, completion


def graft(reference_path: Path, model_path: Path, output_path: Path, chain_id: str, mapping_path: Path):
    parser = PDBParser(QUIET=True)
    ref = parser.get_structure("reference", str(reference_path))
    pred = parser.get_structure("prediction", str(model_path))
    ref_chain = model_chain(ref, chain_id)
    pred_chain = model_chain(pred, chain_id)
    ref_res = residue_map(ref_chain)
    pred_res = residue_map(pred_chain)
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    missing = mapping.get("checks", {}).get("missing_gap_numbers")
    if missing != list(range(114, 123)):
        raise ValueError(f"mapping artifact does not certify exact 114--122 gap: {missing}")
    if mapping.get("checks", {}).get("n_mismatches") != 0:
        raise ValueError("mapping artifact reports UniProt/PDB sequence mismatches")
    if mapping.get("checks", {}).get("sequence_residue_76") != "T":
        raise ValueError("mapping artifact does not certify experimental K76/T state")
    if any(n not in ref_res for n in (76, 113, 123)):
        raise ValueError("experimental reference lacks required K76/113/123 anchors")
    if one_letter(ref_res[76]) != "T":
        raise ValueError("experimental reference residue 76 is not THR")
    if 114 in ref_res or 115 in ref_res or 116 in ref_res or 117 in ref_res or 118 in ref_res or 119 in ref_res or 120 in ref_res or 121 in ref_res or 122 in ref_res:
        raise ValueError("reference unexpectedly contains coordinates in the declared 114--122 gap")
    if one_letter(ref_res[113]) != "G" or one_letter(ref_res[123]) != "H":
        raise ValueError("reference flanks are not GLY113/HIS123")
    if any(n not in pred_res for n in list(range(113, 124))):
        raise ValueError("prediction lacks complete 113--123 anchor/loop interval")
    predicted_seq = "".join(one_letter(pred_res[n]) for n in range(113, 124))
    expected_seq = "".join(THREE_TO_ONE.get(ref_res[n].resname.strip(), "?") if n in ref_res else EXPECTED.get(n, "?") for n in range(113, 124))
    if "".join(one_letter(pred_res[n]) for n in range(114, 123)) != "NKKGNSKER":
        raise ValueError(f"prediction loop sequence mismatch: {predicted_seq}")
    anchor_atoms = [(n, atom) for n in (113, 123) for atom in BACKBONE]
    source = np.asarray([atom_coord(pred_res[n], atom) for n, atom in anchor_atoms])
    target = np.asarray([atom_coord(ref_res[n], atom) for n, atom in anchor_atoms])
    rot, trans = kabsch_transform(source, target)
    out = copy.deepcopy(ref)
    out_chain = model_chain(out, chain_id)
    for n in range(114, 123):
        if n in out_chain.child_dict:
            out_chain.detach_child((" ", n, " "))
        residue = copy.deepcopy(pred_res[n])
        for atom in residue:
            atom.coord = np.asarray(atom.coord, dtype=float) @ rot + trans
        out_chain.add(residue)
    out_chain.child_list.sort(key=lambda r: (r.id[1], r.id[2]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    io = PDBIO(); io.set_structure(out); io.save(str(output_path))
    audit = audit_geometry(out_chain)
    audit.update({"reference_sha256": sha256(reference_path), "mapping_sha256": sha256(mapping_path), "prediction_sha256": sha256(model_path), "output_sha256": sha256(output_path), "predicted_anchor_loop_sequence": predicted_seq, "reference_anchor_context": expected_seq, "anchor_fit_rmsd_A": float(np.sqrt(np.mean(np.sum((source @ rot + trans - target) ** 2, axis=1))))})
    return audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--prediction-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--chain", default="A")
    ap.add_argument("--mapping", type=Path, required=True)
    args = ap.parse_args()
    args.reference = args.reference.resolve(); args.prediction_dir = args.prediction_dir.resolve(); args.output_dir = args.output_dir.resolve()
    if args.output_dir == args.reference.parent or "set_c" in args.output_dir.parts:
        raise SystemExit("FAIL-CLOSED: output directory cannot be canonical reference or set_c")
    models = sorted(args.prediction_dir.glob("*.pdb"))
    # ColabFold writes raw ensemble files as `model_<m>_seed_<s>` and
    # post-ranked files as `rank_<r>`. Accept both forms, but never accept an
    # unrelated PDB accidentally placed in the prediction directory.
    model_pattern = re.compile(r"(?:^|_)model_(\d+)_seed_(\d+).*\.pdb$")
    rank_pattern = re.compile(r"(?:^|_)rank_(\d+).*\.pdb$")
    models = [p for p in models if model_pattern.search(p.name) or rank_pattern.search(p.name)]
    if not models:
        raise SystemExit("No model_<n>_seed_<s> or ranked ColabFold PDB models found")

    def model_key(path: Path):
        match = model_pattern.search(path.name)
        if match:
            return (int(match.group(1)), int(match.group(2)), path.name)
        match = rank_pattern.search(path.name)
        return (int(match.group(1)), -1, path.name)

    models.sort(key=model_key)
    provenance_path = args.prediction_dir / "provenance_preflight.json"
    try:
        prediction_provenance, completion_provenance = validate_provenance(args.reference, args.prediction_dir, args.mapping)
    except Exception as exc:
        raise SystemExit(f"FAIL-CLOSED: provenance validation failed: {exc}") from exc
    records = []
    for index, model in enumerate(models, start=1):
        match = model_pattern.search(model.name)
        if match:
            model_number, seed_number = int(match.group(1)), int(match.group(2))
            label = f"model_{model_number:02d}_seed_{seed_number:03d}"
            rank = model_number
        else:
            rank = int(rank_pattern.search(model.name).group(1))
            label = f"rank_{rank:03d}"
        output = args.output_dir / f"candidate_{label}.pdb"
        try:
            audit = graft(args.reference, model, output, args.chain, args.mapping)
            status = "PASS_GEOMETRY" if audit["pass"] else "BLOCKED_GEOMETRY"
            records.append({"model": model.name, "rank": rank, "candidate": output.name, "model_number": model_number if match else None, "seed": seed_number if match else None, "status": status, "audit": audit})
        except Exception as exc:
            records.append({"model": model.name, "rank": rank, "candidate": output.name, "status": "BLOCKED_EXCEPTION", "error": str(exc)})
    passing = [r for r in records if r["status"] == "PASS_GEOMETRY"]
    # Predeclared representative: highest loop pLDDT among geometry-passing models;
    # docking scores and ligand contacts are deliberately not consulted.
    selected = max(passing, key=lambda r: (r["audit"].get("loop_plddt_mean", -1.0), -r["rank"])) if passing else None
    result = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(), "status": "READY_FOR_INDEPENDENT_STRUCTURAL_REVIEW" if len(passing) >= 3 else "BLOCKED_INSUFFICIENT_PASSING_ENSEMBLE", "scientific_interpretation": "TECHNICAL_TOPOLOGY_AND_STABILITY_EVIDENCE_ONLY", "reference": {"path": str(args.reference), "sha256": sha256(args.reference), "chain": args.chain}, "mapping": {"path": str(args.mapping), "sha256": sha256(args.mapping)}, "prediction_dir": str(args.prediction_dir), "prediction_provenance": prediction_provenance, "completion_provenance": completion_provenance, "models_found": len(models), "passing_models": len(passing), "selection_rule": "highest mean loop pLDDT among geometry-passing candidates; no docking/ligand score used", "selected_candidate": selected, "records": records, "boundary": "Candidates are isolated hypotheses. No canonical PDB, mutant, Set-C directory, topology, trajectory, QC, or MD-RRS was modified or authorized."}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "graft_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "models_found": len(models), "passing_models": len(passing), "selected": selected["candidate"] if selected else None, "audit": str(args.output_dir / "graft_audit.json")}, indent=2))
    return 0 if result["status"] == "READY_FOR_INDEPENDENT_STRUCTURAL_REVIEW" else 2

if __name__ == "__main__":
    raise SystemExit(main())
