#!/usr/bin/env python3
"""Map UniProt PfCRT numbering to 6UKJ PDB coordinates; no modeling or MD."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

AA3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fasta_sequence(path: Path) -> str:
    return "".join(
        line.strip() for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith(">")
    )


def flatfile_sequence_and_accession(path: Path) -> tuple[str, str | None]:
    accession = None
    sequence_lines = []
    in_sequence = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("AC") and accession is None:
            accession = line[5:].split(";")[0].strip()
        if line.startswith("SQ"):
            in_sequence = True
            continue
        if in_sequence:
            if line.startswith("//"):
                break
            sequence_lines.append("".join(line.split()))
    return "".join(sequence_lines).upper(), accession


def parse_pdb_id(path: Path) -> str:
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("HEADER") and len(line) >= 66:
            return line[62:66].strip()
    raise ValueError(f"No PDB ID in HEADER for {path}")


def parse_dbref(path: Path, chain: str, accession: str, sequence_length: int) -> dict:
    for line in path.read_text(errors="replace").splitlines():
        fields = line.split()
        if not (len(fields) >= 10 and fields[0] == "DBREF" and fields[2] == chain
                and fields[5] == "UNP" and fields[6] == accession):
            continue
        dbref = {
            "pdb_start": int(fields[3]), "pdb_end": int(fields[4]),
            "database": fields[5], "accession": fields[6],
            "uniprot_start": int(fields[8]), "uniprot_end": int(fields[9]),
            "raw": line.rstrip(),
        }
        if not (1 <= dbref["uniprot_start"] <= dbref["uniprot_end"] <= sequence_length):
            raise ValueError(f"DBREF UniProt interval is outside FASTA bounds: {dbref}")
        if dbref["pdb_end"] < dbref["pdb_start"]:
            raise ValueError(f"DBREF PDB interval is invalid: {dbref}")
        return dbref
    raise ValueError(f"No DBREF UNP {accession} record for chain {chain} in {path}")


def structure_ambiguities(path: Path, chain: str) -> dict[str, object]:
    lines = path.read_text(errors="replace").splitlines()
    model_records = sum(line.startswith("MODEL") for line in lines)
    altlocs = sorted({line[16:17].strip() for line in lines
                      if line.startswith("ATOM") and line[21:22].strip() == chain
                      and line[16:17].strip()})
    insertion_codes = sorted({line[26:27].strip() for line in lines
                              if line.startswith("ATOM") and line[21:22].strip() == chain
                              and line[26:27].strip()})
    return {
        "model_records": model_records,
        "alternate_location_codes": altlocs,
        "insertion_codes": insertion_codes,
        "ambiguous": bool(model_records > 1 or altlocs or insertion_codes),
    }


def parse_missing_numbers(path: Path, chain: str) -> list[int]:
    values = []
    pattern = re.compile(rf"\s+[A-Z]{{3}}\s+{re.escape(chain)}\s+(-?\d+)")
    for line in path.read_text(errors="replace").splitlines():
        if "REMARK 465" in line:
            match = pattern.search(line)
            if match:
                values.append(int(match.group(1)))
    return values


def pdb_residues(path: Path, chain: str) -> dict[int, dict[str, object]]:
    residues: dict[int, dict[str, object]] = {}
    seen_atoms: set[tuple[int, str]] = set()
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM") or line[21:22].strip() != chain:
            continue
        try:
            number = int(line[22:26])
            name = line[17:20].strip()
            xyz = tuple(float(line[a:b]) for a, b in ((30, 38), (38, 46), (46, 54)))
        except (ValueError, IndexError):
            continue
        atom_key = (number, line[12:16].strip())
        if atom_key in seen_atoms:
            raise ValueError(f"Duplicate atom record at chain {chain} residue {number} atom {atom_key[1]}")
        seen_atoms.add(atom_key)
        if number in residues and residues[number]["name"] != name:
            raise ValueError(f"Conflicting residue names at PDB {number}: {residues[number]['name']} vs {name}")
        item = residues.setdefault(number, {"name": name, "one": AA3.get(name, "X"), "finite": True})
        item["finite"] = bool(item["finite"]) and all(math.isfinite(value) for value in xyz)
    return residues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fasta", type=Path, required=True)
    parser.add_argument("--pdb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chain", default="A")
    parser.add_argument("--accession", default="W7FI62")
    parser.add_argument("--gap-start", type=int, default=114)
    parser.add_argument("--gap-end", type=int, default=122)
    parser.add_argument("--mutation-residue", type=int, default=76)
    args = parser.parse_args()

    sequence = fasta_sequence(args.fasta)
    flat_path = args.fasta.with_suffix(".txt")
    if not sequence or len(sequence) < args.mutation_residue:
        raise ValueError("FASTA is empty or shorter than the requested mutation residue")
    if not flat_path.is_file():
        raise ValueError(f"Expected UniProt flat-file alongside FASTA: {flat_path}")
    flat_sequence, flat_accession = flatfile_sequence_and_accession(flat_path)
    if flat_accession != args.accession or flat_sequence != sequence:
        raise ValueError("UniProt flat-file accession/sequence does not match FASTA")
    pdb_id = parse_pdb_id(args.pdb)
    if pdb_id != "6UKJ":
        raise ValueError(f"Expected PDB 6UKJ, found {pdb_id}")
    dbref = parse_dbref(args.pdb, args.chain, args.accession, len(sequence))
    ambiguities = structure_ambiguities(args.pdb, args.chain)
    if ambiguities["ambiguous"]:
        raise ValueError(f"Ambiguous PDB representation; refusing to map: {ambiguities}")

    residues = pdb_residues(args.pdb, args.chain)
    missing_remark = parse_missing_numbers(args.pdb, args.chain)
    expected_gap = list(range(args.gap_start, args.gap_end + 1))
    if not all(number in missing_remark for number in expected_gap):
        raise ValueError(f"REMARK 465 does not document complete gap {expected_gap}")

    offset = dbref["uniprot_start"] - dbref["pdb_start"]
    records = []
    mismatches = []
    for pdb_number in range(dbref["pdb_start"], dbref["pdb_end"] + 1):
        uni_number = pdb_number + offset
        expected = sequence[uni_number - 1] if 1 <= uni_number <= len(sequence) else None
        observed = residues.get(pdb_number)
        status = (
            "mapped" if observed and observed.get("one") == expected
            else "missing_coordinate" if observed is None else "sequence_mismatch"
        )
        record = {
            "pdb_res_num": pdb_number, "uniprot_accession": args.accession,
            "uniprot_res_num": uni_number, "uniprot_residue": expected,
            "coordinate_present": observed is not None,
            "pdb_residue": observed.get("name") if observed else None,
            "pdb_one_letter": observed.get("one") if observed else None,
            "finite_coordinates": observed.get("finite") if observed else None,
            "mapping_status": status,
        }
        records.append(record)
        if status == "sequence_mismatch":
            mismatches.append(record)

    gap = [record for record in records if args.gap_start <= record["pdb_res_num"] <= args.gap_end]
    k76 = next(record for record in records if record["pdb_res_num"] == args.mutation_residue)
    pdb_hash, fasta_hash = sha256(args.pdb), sha256(args.fasta)
    result = {
        "schema_version": 3,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "INDEPENDENT_UNIPROT_MAPPING_AUDIT",
        "scientific_interpretation": "NO_LOOP_RECONSTRUCTION_NO_MD",
        "provenance": {
            "python": sys.executable, "python_version": sys.version,
            "pdb": str(args.pdb), "pdb_sha256": pdb_hash,
            "fasta": str(args.fasta), "fasta_sha256": fasta_hash,
            "structure_ambiguities": ambiguities,
        },
        "reference": {
            "pdb_id": pdb_id, "uniprot_accession": args.accession,
            "fasta": str(args.fasta), "fasta_sha256": fasta_hash,
            "sequence_length": len(sequence), "pdb": str(args.pdb),
            "pdb_sha256": pdb_hash, "chain": args.chain,
            "declared_dbref": dbref, "remark_465_missing_numbers": missing_remark,
        },
        "checks": {
            "sequence_residue_76": sequence[args.mutation_residue - 1],
            "pdb_residue_76": k76, "gap_window_pdb_114_122": gap,
            "missing_gap_numbers": [r["pdb_res_num"] for r in gap if not r["coordinate_present"]],
            "remark_465_gap_complete": all(x in missing_remark for x in expected_gap),
            "n_mismatches": len(mismatches), "mismatch_examples": mismatches[:20],
            "coordinate_residue_count": len(residues),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "dbref": dbref,
        "sequence_76": sequence[args.mutation_residue - 1], "pdb76": k76,
        "missing_gap_numbers": result["checks"]["missing_gap_numbers"],
        "remark_465_complete": result["checks"]["remark_465_gap_complete"],
        "n_mismatches": len(mismatches), "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
