#!/usr/bin/env python3
"""Build an auditable PfCRT SEQRES-to-coordinate residue mapping.

The tool is read-only with respect to PDB inputs: it writes only a JSON mapping
artifact. It does not model residues or launch MD. The mapping uses a global
sequence alignment between the PDB SEQRES sequence and the observed ATOM
residue sequence, preserving PDB residue numbers and explicitly marking missing
coordinates and expression-tag records.
"""
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
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_seqres(path: Path, chain: str) -> list[tuple[int, str, str]]:
    """Return (SEQRES ordinal, 3-letter residue, one-letter residue)."""
    out = []
    ordinal = 0
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("SEQRES") and line[11:12] == chain:
            for token in line[19:].split():
                ordinal += 1
                out.append((ordinal, token, AA3.get(token, "X")))
    if not out:
        raise ValueError(f"No SEQRES records for chain {chain} in {path}")
    return out


def parse_atoms(path: Path, chain: str) -> list[tuple[int, str, str, bool]]:
    """Return unique coordinate residues (PDB number, name, one-letter, finite)."""
    residues = {}
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM") or line[21:22].strip() != chain:
            continue
        try:
            number = int(line[22:26])
            name = line[17:20].strip()
            xyz = tuple(float(line[a:b]) for a, b in ((30, 38), (38, 46), (46, 54)))
        except (ValueError, IndexError):
            continue
        finite = all(math.isfinite(x) for x in xyz)
        key = number
        if key not in residues:
            residues[key] = {"name": name, "one": AA3.get(name, "X"), "finite": finite}
        else:
            residues[key]["finite"] = residues[key]["finite"] and finite
    return [(n, v["name"], v["one"], v["finite"]) for n, v in sorted(residues.items())]


def align(reference: str, observed: str) -> list[tuple[int | None, int | None]]:
    """Needleman-Wunsch alignment returning zero-based index pairs or gaps."""
    match, mismatch, gap = 2, -3, -4
    n, m = len(reference), len(observed)
    score = [[0] * (m + 1) for _ in range(n + 1)]
    trace = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): score[i][0] = score[i - 1][0] + gap; trace[i][0] = "U"
    for j in range(1, m + 1): score[0][j] = score[0][j - 1] + gap; trace[0][j] = "L"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            choices = [(score[i-1][j-1] + (match if reference[i-1] == observed[j-1] else mismatch), "D"), (score[i-1][j] + gap, "U"), (score[i][j-1] + gap, "L")]
            score[i][j], trace[i][j] = max(choices, key=lambda x: x[0])
    pairs = []
    i, j = n, m
    while i or j:
        step = trace[i][j]
        if step == "D": pairs.append((i - 1, j - 1)); i -= 1; j -= 1
        elif step == "U": pairs.append((i - 1, None)); i -= 1
        elif step == "L": pairs.append((None, j - 1)); j -= 1
        else: raise RuntimeError("alignment traceback failed")
    pairs.reverse()
    return pairs


def seqadv(path: Path, chain: str) -> list[dict]:
    out = []
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("SEQADV") or line[12:13] != chain:
            continue
        out.append({"raw": line.rstrip(), "pdb_residue": line[12:16].strip(), "pdb_number": line[18:22].strip(), "note": line[39:].strip()})
    return out


def build(reference: Path, chain: str, loop_start: int, loop_end: int, mapping_note: str) -> dict:
    seq = parse_seqres(reference, chain)
    coords = parse_atoms(reference, chain)
    seq_string = "".join(row[2] for row in seq)
    coord_string = "".join(row[2] for row in coords)
    pairs = align(seq_string, coord_string)
    by_seq = {}
    for si, ci in pairs:
        if si is not None:
            by_seq[si] = ci
    records = []
    for si, three, one in seq:
        ci = by_seq.get(si - 1)
        if ci is None:
            rec = {"seqres_index": si, "seqres_residue": three, "one_letter": one, "coordinate_present": False, "mapping_status": "missing_coordinate"}
        else:
            pdb_num, pdb_three, pdb_one, finite = coords[ci]
            rec = {"seqres_index": si, "seqres_residue": three, "one_letter": one, "pdb_res_num": pdb_num, "pdb_residue": pdb_three, "coordinate_present": True, "finite_coordinates": finite, "mapping_status": "mapped" if one == pdb_one else "sequence_mismatch"}
        if si <= 4 or si > len(seq) - 39:
            rec["construct_annotation"] = "expression_tag_or_construct"
        records.append(rec)
    observed_by_pdb = {r.get("pdb_res_num"): r for r in records if r.get("pdb_res_num") is not None}
    left = observed_by_pdb.get(loop_start - 1)
    right = observed_by_pdb.get(loop_end + 1)
    if left is None or right is None:
        raise ValueError(f"Could not locate PDB gap boundaries {loop_start - 1} and {loop_end + 1}")
    left_seq = left["seqres_index"]
    right_seq = right["seqres_index"]
    for rec in records:
        if left_seq < rec["seqres_index"] < right_seq and not rec["coordinate_present"]:
            rec["mapping_status"] = "missing_loop"
    gap_records = [r for r in records if left_seq < r["seqres_index"] < right_seq]
    return {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "MAPPING_AUDIT_ONLY",
        "scientific_interpretation": "NO_LOOP_RECONSTRUCTION_NO_MD",
        "reference": {"path": str(reference), "sha256": sha256(reference), "chain": chain, "seqres_length": len(seq), "coordinate_residue_count": len(coords), "alignment_score_method": "Needleman-Wunsch match=2 mismatch=-3 gap=-4", "mapping_note": mapping_note, "seqadv": seqadv(reference, chain)},
        "key_checks": {
            "pdb_loop_window": [loop_start, loop_end],
            "pdb_left_boundary": left,
            "pdb_right_boundary": right,
            "missing_loop_seqres_records": gap_records,
            "missing_loop_pdb_numbers": [i for i in range(loop_start, loop_end + 1) if i not in observed_by_pdb],
            "pdb_residue_76_observed": observed_by_pdb.get(76),
            "pdb_residue_76_status": "present_in_coordinates" if 76 in observed_by_pdb else "missing",
            "sequence_ordinal_for_pdb_76": next((r for r in records if r.get("pdb_res_num") == 76), None),
        },
        "records": records,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reference", type=Path, required=True); p.add_argument("--output", type=Path, required=True); p.add_argument("--chain", default="A"); p.add_argument("--loop-start", type=int, default=114, help="First missing PDB residue number"); p.add_argument("--loop-end", type=int, default=122, help="Last missing PDB residue number"); p.add_argument("--mapping-note", required=True)
    a = p.parse_args(); result = build(a.reference, a.chain, a.loop_start, a.loop_end, a.mapping_note); a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); print(json.dumps({"status": result["status"], "seqres_length": result["reference"]["seqres_length"], "coordinates": result["reference"]["coordinate_residue_count"], "pdb76": result["key_checks"]["pdb_residue_76_observed"], "missing_pdb_numbers": result["key_checks"]["missing_loop_pdb_numbers"], "missing_seqres_count": len(result["key_checks"]["missing_loop_seqres_records"]), "output": str(a.output)}, indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())
