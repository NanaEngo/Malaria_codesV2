#!/usr/bin/env python3
"""Fail-closed audit of PfCRT gap candidates; no repair and no MD."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rooted_path(raw: str | Path) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


AA3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def seqres(path: Path, chain: str) -> str:
    sequence = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("SEQRES") and line[11:12] == chain:
            sequence.extend(AA3.get(token, "X") for token in line[19:].split())
    if not sequence:
        raise ValueError(f"No SEQRES sequence for chain {chain} in {path}")
    return "".join(sequence)


def atoms(path: Path, chain: str) -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    seen_atoms: set[tuple[int, str]] = set()
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM") or line[21:22].strip() != chain:
            continue
        try:
            residue = int(line[22:26])
            atom = line[12:16].strip()
            xyz = tuple(float(line[a:b]) for a, b in ((30, 38), (38, 46), (46, 54)))
        except (ValueError, IndexError):
            continue
        atom_key = (residue, atom)
        if atom_key in seen_atoms:
            raise ValueError(f"Duplicate atom record at chain {chain} residue {residue} atom {atom}")
        seen_atoms.add(atom_key)
        item = out.setdefault(residue, {"name": line[17:20].strip(), "atoms": {}})
        if item["name"] != line[17:20].strip():
            raise ValueError(f"Conflicting residue names at chain {chain} residue {residue}")
        item["atoms"][atom] = xyz  # type: ignore[index]
    return out


def distance(a, b) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def expected_state(path: Path) -> str | None:
    # Filename labels are hypotheses used to select the expected gate; they are
    # never treated as independent mutation evidence.
    match = re.search(r"PfCRT_K76([AT])", path.name)
    return match.group(1) if match else None


def structure_ambiguities(path: Path, chain: str) -> dict[str, object]:
    lines = path.read_text(errors="replace").splitlines()
    model_records = sum(line.startswith("MODEL") for line in lines)
    altlocs = sorted({line[16:17].strip() for line in lines
                      if line.startswith("ATOM") and line[21:22].strip() == chain
                      and line[16:17].strip()})
    insertion_codes = sorted({line[26:27].strip() for line in lines
                              if line.startswith("ATOM") and line[21:22].strip() == chain
                              and line[26:27].strip()})
    return {"model_records": model_records, "alternate_location_codes": altlocs,
            "insertion_codes": insertion_codes,
            "ambiguous": bool(model_records > 1 or altlocs or insertion_codes)}


def aa_set(one_letter: str) -> set[str]:
    return {one_letter, {"A":"ALA", "T":"THR", "K":"LYS"}[one_letter]}


def audit(reference: Path, candidates: list[Path], mapping_path: Path, uniprot_mapping_path: Path, provenance_path: Path, chain: str, start: int, end: int,
          pdb_mutation_residue: int, reference_state: str, alignment_source: str,
          script_path: Path) -> dict:
    reference = reference.resolve()
    mapping_path = mapping_path.resolve()
    uniprot_mapping_path = uniprot_mapping_path.resolve()
    provenance_path = provenance_path.resolve()
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    uniprot_mapping = json.loads(uniprot_mapping_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if uniprot_mapping.get("status") != "INDEPENDENT_UNIPROT_MAPPING_AUDIT":
        raise ValueError(f"UniProt mapping artifact is not independent: {uniprot_mapping.get('status')}")
    if provenance.get("status") != "FETCHED_AUTHORITATIVE_SEQUENCE" or provenance.get("accession") != "W7FI62":
        raise ValueError("UniProt provenance manifest is not the expected W7FI62 archive")
    if uniprot_mapping.get("reference", {}).get("pdb_id") != "6UKJ":
        raise ValueError("UniProt mapping does not identify PDB 6UKJ")
    if uniprot_mapping.get("reference", {}).get("uniprot_accession") != "W7FI62":
        raise ValueError("UniProt mapping does not identify W7FI62")
    if uniprot_mapping.get("checks", {}).get("n_mismatches") != 0:
        raise ValueError("UniProt/PDB mapping contains sequence mismatches")
    if uniprot_mapping.get("checks", {}).get("sequence_residue_76") != "T":
        raise ValueError("Independent sequence does not verify 7G8 K76T")
    if uniprot_mapping.get("checks", {}).get("pdb_residue_76", {}).get("pdb_one_letter") != "T":
        raise ValueError("PDB 6UKJ residue 76 is not verified as THR")
    if not uniprot_mapping.get("checks", {}).get("remark_465_gap_complete"):
        raise ValueError("REMARK 465 does not verify the complete 114-122 gap")
    if uniprot_mapping.get("checks", {}).get("missing_gap_numbers") != list(range(114, 123)):
        raise ValueError("UniProt mapping does not verify PDB gap 114-122")
    # Recompute the provenance chain from the raw files; do not trust hashes or
    # critical claims copied into an intermediate JSON artifact.
    mapping_reference = mapping.get("reference", {})
    if not mapping_reference.get("path") or rooted_path(mapping_reference["path"]) != reference:
        raise ValueError("Local mapping reference path does not match audit reference")
    if mapping_reference.get("sha256") != sha256(reference):
        raise ValueError("Local mapping PDB hash does not match audit reference")
    independent_reference = uniprot_mapping.get("reference", {})
    uniprot_fasta = rooted_path(independent_reference.get("fasta", ""))
    manifest_fasta = rooted_path(provenance.get("fasta", {}).get("path", ""))
    if manifest_fasta != uniprot_fasta or not uniprot_fasta.is_file():
        raise ValueError("Independent mapping FASTA does not match the archived provenance manifest")
    if independent_reference.get("fasta_sha256") != sha256(uniprot_fasta) or provenance.get("fasta", {}).get("sha256") != sha256(uniprot_fasta):
        raise ValueError("Independent mapping FASTA or provenance-manifest hash mismatch")
    flatfile = rooted_path(provenance.get("flatfile", {}).get("path", ""))
    if not flatfile.is_file():
        raise ValueError("Archived UniProt flat-file is missing")
    if provenance.get("flatfile", {}).get("sha256") != sha256(flatfile):
        raise ValueError("Archived UniProt flat-file hash mismatch")
    if independent_reference.get("pdb_sha256") != sha256(reference):
        raise ValueError("Independent mapping PDB hash does not match audit reference")
    if independent_reference.get("sequence_length") != len("".join(line.strip() for line in uniprot_fasta.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith(">"))):
        raise ValueError("Independent mapping sequence length is inconsistent with FASTA")
    sequence_ordinal_record = mapping.get("key_checks", {}).get("sequence_ordinal_for_pdb_76", {})
    key_seqres_index = sequence_ordinal_record.get("seqres_index")
    if key_seqres_index is None or sequence_ordinal_record.get("pdb_res_num") != pdb_mutation_residue:
        raise ValueError("Mapping artifact does not provide a verified SEQRES ordinal for the declared PDB mutation residue")
    if mapping.get("key_checks", {}).get("pdb_residue_76_observed", {}).get("one_letter") != "T":
        raise ValueError("Local mapping does not independently record PDB residue 76 as THR")
    if uniprot_mapping.get("checks", {}).get("sequence_residue_76") != "T":
        raise ValueError("Independent mapping does not record UniProt residue 76 as T")
    if mapping.get("status") != "MAPPING_AUDIT_ONLY":
        raise ValueError(f"mapping artifact is not an audit artifact: {mapping.get('status')}")
    key = mapping.get("key_checks", {})
    if not mapping.get("reference", {}).get("path") or rooted_path(mapping["reference"]["path"]) != reference:
        raise ValueError("mapping artifact reference path does not match audit reference")
    if uniprot_mapping.get("reference", {}).get("pdb_sha256") != sha256(reference):
        raise ValueError("UniProt mapping PDB hash does not match audit reference")
    expected_missing = list(range(114, 123))
    if key.get("missing_loop_pdb_numbers") != expected_missing:
        raise ValueError(f"mapping artifact does not verify PDB gap 114-122: {key.get('missing_loop_pdb_numbers')}")
    reference_seq = seqres(reference, chain)
    reference_atoms = atoms(reference, chain)
    reference_ambiguities = structure_ambiguities(reference, chain)
    if reference_ambiguities["ambiguous"]:
        raise ValueError(f"Reference PDB representation is ambiguous: {reference_ambiguities}")
    missing = [i for i in range(start, end + 1) if i not in reference_atoms]
    reference_coordinate_window = {str(i): reference_atoms[i]["name"] if i in reference_atoms else None for i in range(start, end + 1)}
    reference_pdb_name = reference_atoms.get(pdb_mutation_residue, {}).get("name")
    reference_state_mismatch = reference_pdb_name not in aa_set(reference_state)
    results = []

    for path in candidates:
        lines = path.read_text(errors="replace").splitlines()
        candidate_seq = seqres(path, chain) if any(line.startswith("SEQRES") for line in lines) else ""
        candidate_atoms = atoms(path, chain)
        candidate_ambiguities = structure_ambiguities(path, chain)
        state = expected_state(path)
        sequence_mismatches = [i for i in range(1, min(len(reference_seq), len(candidate_seq)) + 1)
                               if reference_seq[i - 1] != candidate_seq[i - 1]]
        if len(reference_seq) != len(candidate_seq):
            sequence_mismatches.append(f"length:{len(reference_seq)}!={len(candidate_seq)}")
        candidate_seqres_residue = candidate_seq[key_seqres_index - 1] if candidate_seq and key_seqres_index <= len(candidate_seq) else None
        reference_seqres_residue = reference_seq[key_seqres_index - 1] if key_seqres_index <= len(reference_seq) else None
        candidate_pdb_name = candidate_atoms.get(pdb_mutation_residue, {}).get("name")
        candidate_mapping_unresolved = not bool(candidate_seq)
        candidate_ambiguity = bool(candidate_ambiguities["ambiguous"])
        candidate_seqres_mutation_mismatch = state is not None and candidate_seqres_residue != state
        candidate_pdb_mutation_mismatch = state is not None and candidate_pdb_name not in aa_set(state)

        missing_backbone, nonfinite = [], []
        for residue in range(start, end + 1):
            item = candidate_atoms.get(residue)
            if item is None:
                missing_backbone.append(str(residue))
                continue
            for atom in ("N", "CA", "C", "O"):
                if atom not in item["atoms"]:
                    missing_backbone.append(f"{residue}:{atom}")
                elif not all(math.isfinite(value) for value in item["atoms"][atom]):
                    nonfinite.append(f"{residue}:{atom}")

        peptide, ca_steps = {}, {}
        for residue in range(start, end):
            left = candidate_atoms.get(residue, {}).get("atoms", {})
            right = candidate_atoms.get(residue + 1, {}).get("atoms", {})
            if "C" in left and "N" in right:
                peptide[str(residue)] = round(distance(left["C"], right["N"]), 3)
            if "CA" in left and "CA" in right:
                ca_steps[str(residue)] = round(distance(left["CA"], right["CA"]), 3)
        geometry_flags = [f"C{i}-N{i+1}={value}A" for i, value in peptide.items() if not 1.15 <= value <= 1.45]
        geometry_flags += [f"CA{i}-CA{i+1}={value}A" for i, value in ca_steps.items() if not 2.5 <= value <= 4.8]
        preliminary_eligible = not any((sequence_mismatches, missing_backbone, nonfinite, geometry_flags, reference_state_mismatch, candidate_seqres_mutation_mismatch, candidate_pdb_mutation_mismatch, candidate_mapping_unresolved, candidate_ambiguity))
        results.append({
            "path": str(path), "sha256": sha256(path), "structure_ambiguities": candidate_ambiguities,
            "candidate_sequence_length": len(candidate_seq),
            "sequence_mismatches_vs_6UKJ_SEQRES": sequence_mismatches,
            "candidate_seqres_window": candidate_seq[start - 1:end] if len(candidate_seq) >= end else None,
            "coordinate_window": {str(i): candidate_atoms[i]["name"] if i in candidate_atoms else None for i in range(start, end + 1)},
            "expected_state_from_filename": state,
            "seqres_mutation_index": key_seqres_index,
            "reference_seqres_residue_at_index": reference_seqres_residue,
            "candidate_seqres_residue_at_index": candidate_seqres_residue,
            "pdb_mutation_residue": pdb_mutation_residue,
            "reference_pdb_residue_name": reference_pdb_name,
            "candidate_pdb_residue_name": candidate_pdb_name,
            "candidate_mutation_mapping_unresolved": candidate_mapping_unresolved,
            "candidate_seqres_mutation_mismatch": candidate_seqres_mutation_mismatch,
            "candidate_pdb_mutation_mismatch": candidate_pdb_mutation_mismatch,
            "missing_backbone_atoms": missing_backbone, "nonfinite_coordinates": nonfinite,
            "peptide_C_N_A": peptide, "CA_step_A": ca_steps, "geometry_flags": geometry_flags,
            "preliminary_review_eligible": preliminary_eligible,
            "promotion_status": "ELIGIBLE_FOR_REVIEW_ONLY" if preliminary_eligible else "BLOCKED_NUMBERING_SEQUENCE_OR_GEOMETRY",
        })

    versions = {}
    for name in ("openmm", "pdbfixer", "biopython"):
        try:
            versions[name] = {"status": "installed", "version": metadata.version(name)}
        except metadata.PackageNotFoundError:
            versions[name] = {"status": "missing", "version": None}
    top_status = "PRELIMINARY_SCREEN_COMPLETE" if any(item["preliminary_review_eligible"] for item in results) else "BLOCKED_NO_PRELIMINARY_ELIGIBLE_CANDIDATE"
    return {
        "schema_version": 3, "created_utc": datetime.now(timezone.utc).isoformat(), "status": top_status,
        "scientific_interpretation": "PRELIMINARY_PROVENANCE_SCREEN_ONLY_NO_LOOP_RECONSTRUCTION_NO_MD",
        "audit_provenance": {"script": str(script_path), "script_sha256": sha256(script_path), "python": sys.executable, "python_version": sys.version, "package_versions": versions, "alignment_source": alignment_source, "mapping_artifact": str(mapping_path), "mapping_artifact_sha256": sha256(mapping_path), "uniprot_mapping_artifact": str(uniprot_mapping_path), "uniprot_mapping_artifact_sha256": sha256(uniprot_mapping_path), "uniprot_provenance_manifest": str(provenance_path), "uniprot_provenance_manifest_sha256": sha256(provenance_path), "seqres_to_pdb_mapping_status": "CONSUMED_LOCAL_AND_INDEPENDENT_UNIPROT_MAPPING"},
        "reference": {"path": str(reference), "sha256": sha256(reference), "chain": chain, "seqres_length": len(reference_seq), "seqres_window": reference_seq[start - 1:end], "coordinate_window": reference_coordinate_window, "missing_coordinate_residues": missing, "pdb_mutation_residue": pdb_mutation_residue, "pdb_residue_name_at_mutation": reference_pdb_name, "reference_state": reference_state, "reference_pdb_state_mismatch": reference_state_mismatch, "mapping_key_checks": key},
        "candidates": results,
        "promotion_rule": "No candidate may enter MD until complete-sequence alignment, mature/PDB numbering reconciliation, mutation identity, loop geometry/ensemble, charge/terminal audit, and independent structural review pass.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chain", default="A")
    parser.add_argument("--start", type=int, default=100)
    parser.add_argument("--end", type=int, default=135)
    parser.add_argument("--mapping-artifact", type=Path, required=True, help="Output of p2_pfcrt_build_sequence_mapping.py")
    parser.add_argument("--uniprot-mapping-artifact", type=Path, required=True, help="Output of p2_pfcrt_map_uniprot_to_pdb.py")
    parser.add_argument("--pdb-mutation-residue", type=int, default=76)
    parser.add_argument("--reference-state", choices=["A", "T", "K"], default="T")
    parser.add_argument("--alignment-source", required=True)
    parser.add_argument("--uniprot-provenance", type=Path, required=True, help="Raw UniProt archive manifest")
    args = parser.parse_args()
    result = audit(args.reference, args.candidate, args.mapping_artifact, args.uniprot_mapping_artifact, args.uniprot_provenance, args.chain, args.start, args.end, args.pdb_mutation_residue, args.reference_state, args.alignment_source, Path(__file__).resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "reference_pdb_residue": result["reference"]["pdb_residue_name_at_mutation"], "candidates": [{"path": item["path"], "promotion_status": item["promotion_status"], "sequence_mismatches": len(item["sequence_mismatches_vs_6UKJ_SEQRES"]), "candidate_mapping_unresolved": item["candidate_mutation_mapping_unresolved"], "candidate_pdb_mutation_mismatch": item["candidate_pdb_mutation_mismatch"]} for item in result["candidates"]], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
