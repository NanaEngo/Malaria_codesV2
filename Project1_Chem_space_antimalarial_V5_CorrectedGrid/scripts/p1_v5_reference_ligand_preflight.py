#!/usr/bin/env python3
"""Input-read-only, derived-artifact-producing reference-ligand preflight for P1 V5.

The script writes derived provenance artifacts but never modifies source PDBs and
never launches DiffDock, Vina, GROMACS, consensus, RRS, or PNS. Every matching
HETATM instance is inventoried; ambiguous residue names are never silently
collapsed to one ligand. Native coordinates are preserved and checked through a
PDB-to-SDF round trip, but chemical identity and pocket relevance remain subject
to independent review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from rdkit import Chem

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
DEFAULT_OUT_DIR = V5 / "results/reference_ligands"
DEFAULT_OUT_JSON = V5 / "results/reference_ligand_preflight.json"

TARGETS = {
    "PfDHFR": {
        "pdb_id": "7F3Y",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb",
        "residue": "MTX",
        "classification": "CANDIDATE_STRUCTURAL_ANCHOR_REVIEW_REQUIRED",
        "biological_note": "MTX instances are inventoried separately; identity, active-site correspondence, and chain selection require independent review.",
    },
    "PfCRT": {
        "pdb_id": "6UKJ",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/6UKJ.pdb",
        "residue": "Y01",
        "classification": "AMBIGUOUS_PROXY_NOT_ACCEPTED",
        "biological_note": "Y01 is inventoried as a structural proxy only; it is not accepted as an inhibitor-pocket anchor.",
    },
    "PfClpP": {
        "pdb_id": "4GM2",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/4GM2.pdb",
        "residue": None,
        "classification": "TARGET_IDENTITY_MISMATCH_BLOCKED",
        "biological_note": "RCSB 4GM2 is PfClpR, an inactive paralog/subunit, not PfClpP. A genuine PfClpP receptor and target-specific pocket evidence are required.",
    },
    "PfATP4": {
        "pdb_id": "9N10",
        "pdb": ROOT / "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/9N10.pdb",
        "residue": None,
        "classification": "NO_STRUCTURAL_LIGAND_ANCHOR_BLOCKED",
        "biological_note": "No non-water HETATM anchor was found; target-specific membrane-site evidence is required.",
    },
}

WATER_IONS = {"HOH", "WAT", "SOL", "NA", "CL", "K", "CA", "MG", "ZN", "SO4", "PO4"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def residue_groups(pdb: Path, residue: str) -> dict[tuple[str, int, str], list[str]]:
    groups: dict[tuple[str, int, str], list[str]] = {}
    model_count = 0
    for line in pdb.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            model_count += 1
        if not line.startswith("HETATM") or line[17:20].strip() != residue:
            continue
        if line[16].strip():
            raise ValueError(f"alternate-location HETATM is not accepted: {line[16]!r}")
        try:
            occupancy = float(line[54:60])
        except ValueError as exc:
            raise ValueError("malformed HETATM occupancy") from exc
        if occupancy <= 0:
            raise ValueError("non-positive HETATM occupancy is not accepted")
        group = (line[21].strip() or "_", int(line[22:26]), line[26].strip())
        groups.setdefault(group, []).append(line)
    if model_count > 1:
        raise ValueError(f"multiple PDB MODEL records are not accepted: {model_count}")
    return groups


def source_conect_pairs(pdb: Path, atom_serials: set[int]) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for line in pdb.read_text(errors="replace").splitlines():
        if not line.startswith("CONECT"):
            continue
        try:
            serials = [int(line[i:i + 5]) for i in range(6, len(line), 5) if line[i:i + 5].strip()]
        except ValueError:
            continue
        if not serials or serials[0] not in atom_serials:
            continue
        for other in serials[1:]:
            if other in atom_serials and other != serials[0]:
                pairs.add(tuple(sorted((serials[0], other))))
    return pairs


def extract_instance(pdb: Path, source_lines: list[str], output_pdb: Path, output_sdf: Path) -> dict:
    atom_serials = {int(line[6:11]) for line in source_lines}
    atom_names = [line[12:16].strip() for line in source_lines]
    elements = [line[76:78].strip().upper() for line in source_lines]
    if len(atom_serials) != len(source_lines) or len(set(atom_names)) != len(source_lines):
        raise ValueError("duplicate atom serial or atom name in HETATM instance")
    converted = [f"HETATM{line[6:17]}UNL{line[20:]}" for line in source_lines]
    source_conect = source_conect_pairs(pdb, atom_serials)
    conect = []
    for line in pdb.read_text(errors="replace").splitlines():
        if not line.startswith("CONECT"):
            continue
        try:
            serials = [int(line[i:i + 5]) for i in range(6, len(line), 5) if line[i:i + 5].strip()]
        except ValueError:
            continue
        if serials and serials[0] in atom_serials:
            selected = [serials[0]] + [value for value in serials[1:] if value in atom_serials]
            if len(selected) > 1:
                conect.append("CONECT" + "".join(f"{value:5d}" for value in selected))
    output_pdb.parent.mkdir(parents=True, exist_ok=True)
    output_pdb.write_text("\n".join(converted + conect) + "\nEND\n", encoding="utf-8")

    mol = Chem.MolFromPDBFile(str(output_pdb), removeHs=False, sanitize=False)
    if mol is None or mol.GetNumAtoms() != len(source_lines):
        raise ValueError("RDKit PDB parse failed or atom count changed")
    parsed_elements = [atom.GetSymbol().upper() for atom in mol.GetAtoms()]
    if parsed_elements != elements:
        raise ValueError(f"element/order mismatch: source={elements}, parsed={parsed_elements}")
    atom_names = [line[12:16].strip() for line in source_lines]
    atom_serial_list = [int(line[6:11]) for line in source_lines]
    for atom, name, serial in zip(mol.GetAtoms(), atom_names, atom_serial_list):
        atom.SetAtomMapNum(serial)
        atom.SetProp("_V5SourceAtomName", name)
        atom.SetIntProp("_V5SourceAtomSerial", serial)
    # Use PDB molecule atom indices for the source graph. PDB serial numbers
    # are not guaranteed to survive an SDF round trip as AtomMapNum values.
    pdb_bond_orders: dict[tuple[int, int], float] = {}
    for bond in mol.GetBonds():
        pair = tuple(sorted((bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())))
        pdb_bond_orders[pair] = bond.GetBondTypeAsDouble()
    try:
        Chem.SanitizeMol(mol)
    except Exception as exc:
        raise ValueError(f"RDKit sanitization failed: {type(exc).__name__}") from exc
    if mol.GetNumConformers() != 1:
        raise ValueError(f"unexpected conformer count: {mol.GetNumConformers()}")

    writer = Chem.SDWriter(str(output_sdf))
    writer.write(mol)
    writer.close()
    check = Chem.SDMolSupplier(str(output_sdf), removeHs=False, sanitize=True)
    parsed = next((candidate for candidate in check if candidate is not None), None)
    if parsed is None or parsed.GetNumAtoms() != len(source_lines) or parsed.GetNumConformers() != 1:
        raise ValueError("RDKit SDF round-trip validation failed")
    roundtrip_elements = [atom.GetSymbol().upper() for atom in parsed.GetAtoms()]
    if roundtrip_elements != elements:
        raise ValueError("SDF round-trip element/order mismatch")
    source_xyz = [[float(line[30:38]), float(line[38:46]), float(line[46:54])] for line in source_lines]
    roundtrip_xyz = parsed.GetConformer().GetPositions().tolist()
    source_to_sdf: dict[int, int] = {}
    used_sdf: set[int] = set()
    for source_index, (element, xyz) in enumerate(zip(elements, source_xyz)):
        candidates = [
            index for index, (sdf_element, sdf_xyz) in enumerate(zip(roundtrip_elements, roundtrip_xyz))
            if index not in used_sdf and sdf_element == element and sum((xyz[j] - sdf_xyz[j]) ** 2 for j in range(3)) <= 1e-6
        ]
        if len(candidates) != 1:
            raise ValueError(f"atom identity/coordinate mapping is not bijective for source atom {source_index}: {candidates}")
        source_to_sdf[source_index] = candidates[0]
        used_sdf.add(candidates[0])
    serial_to_source_index = {int(line[6:11]): index for index, line in enumerate(source_lines)}
    # Translate SDF bond endpoints back to source-PDB atom indices using the
    # verified element+coordinate bijection; AtomMapNum conventions differ
    # between RDKit PDB and SDF readers and are therefore not used here.
    sdf_to_source = {sdf_index: source_index for source_index, sdf_index in source_to_sdf.items()}
    sdf_bond_orders: dict[tuple[int, int], float] = {}
    for bond in parsed.GetBonds():
        begin = sdf_to_source[bond.GetBeginAtomIdx()]
        end = sdf_to_source[bond.GetEndAtomIdx()]
        sdf_bond_orders[tuple(sorted((begin, end)))] = bond.GetBondTypeAsDouble()
    expected_bond_orders = pdb_bond_orders
    if set(sdf_bond_orders) != set(expected_bond_orders):
        raise ValueError(f"bond connectivity mismatch: source={sorted(expected_bond_orders)}, sdf={sorted(sdf_bond_orders)}")
    for pair, expected_order in expected_bond_orders.items():
        if abs(sdf_bond_orders[pair] - expected_order) > 1e-6:
            raise ValueError(f"bond-order mismatch for {pair}: source={expected_order}, sdf={sdf_bond_orders[pair]}")

    source_xyz = [[float(line[30:38]), float(line[38:46]), float(line[46:54])] for line in source_lines]
    extracted_xyz = parsed.GetConformer().GetPositions().tolist()
    max_abs_delta = max(abs(source_xyz[i][j] - extracted_xyz[i][j]) for i in range(len(source_xyz)) for j in range(3))
    if max_abs_delta > 1e-3:
        raise ValueError(f"native-coordinate mismatch after SDF round trip: max_abs_delta={max_abs_delta}")
    return {
        "atom_count": len(source_lines),
        "element_sequence": elements,
        "native_coordinate_max_abs_delta_A": max_abs_delta,
        "native_coordinate_source_sha256": hashlib.sha256("".join(source_lines).encode()).hexdigest(),
        "source_conect_pair_count": len(source_conect),
        "pdb_inferred_bond_pair_count": len(pdb_bond_orders),
        "sdf_bond_pair_count": len(sdf_bond_orders),
        "pdb_inferred_bond_order_histogram": {str(order): list(pdb_bond_orders.values()).count(order) for order in sorted(set(pdb_bond_orders.values()))},
        "sdf_bond_order_histogram": {str(order): list(sdf_bond_orders.values()).count(float(order)) for order in sorted(set(sdf_bond_orders.values()))},
        "atom_identity_coordinate_mapping": "PASS",
        "bond_connectivity_round_trip": "PASS",
        "bond_order_round_trip": "PASS",
        "rdkit_sdf_round_trip": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUT_JSON)
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_json = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
    if output_json.exists():
        raise SystemExit(f"FAIL-CLOSED preflight JSON already exists; refusing overwrite: {output_json}")
    if output_dir.exists():
        raise SystemExit(f"FAIL-CLOSED reference-ligand output directory already exists; refusing reuse: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)
    records = {}

    for target, spec in TARGETS.items():
        pdb = spec["pdb"]
        if not pdb.is_file() or pdb.stat().st_size == 0:
            raise SystemExit(f"FAIL-CLOSED missing target PDB: {pdb}")
        record = {
            "target": target,
            "pdb_id": spec["pdb_id"],
            "pdb": str(pdb),
            "pdb_sha256": sha256(pdb),
            "declared_residue": spec["residue"],
            "classification": spec["classification"],
            "biological_note": spec["biological_note"],
            "output_immutable": True,
            "diffdock_launched": False,
            "vina_launched": False,
            "gromacs_launched": False,
        }
        if spec["residue"] is None:
            record.update({
                "status": "BLOCKED_NO_DECLARED_REFERENCE_LIGAND",
                "non_water_hetatm_residues_in_pdb": sorted({
                    line[17:20].strip() for line in pdb.read_text(errors="replace").splitlines()
                    if line.startswith("HETATM") and line[17:20].strip() not in WATER_IONS
                }),
            })
            records[target] = record
            continue

        try:
            groups = residue_groups(pdb, spec["residue"])
        except (OSError, ValueError) as exc:
            record.update({"status": "RESIDUE_INVENTORY_FAILED", "error": str(exc)})
            records[target] = record
            continue
        if not groups:
            record.update({"status": "DECLARED_RESIDUE_NOT_FOUND", "instances": []})
            records[target] = record
            continue

        instances = []
        for chain, resseq, icode in sorted(groups):
            tag = f"{chain}_{resseq}{icode or ''}"
            output_pdb = output_dir / f"{target}_{spec['pdb_id']}_{spec['residue']}_{tag}.pdb"
            output_sdf = output_dir / f"{target}_{spec['pdb_id']}_{spec['residue']}_{tag}.sdf"
            if output_pdb.exists() or output_sdf.exists():
                raise SystemExit(f"FAIL-CLOSED reference-ligand output already exists; refusing overwrite: {output_pdb}")
            instance = {
                "chain": chain,
                "resseq": resseq,
                "icode": icode,
                "source_atom_count": len(groups[(chain, resseq, icode)]),
                "status": "EXTRACTION_FAILED",
                "native_coordinates_preserved": False,
                "eligible_for_native_pocket_smoke": False,
            }
            try:
                validation = extract_instance(pdb, groups[(chain, resseq, icode)], output_pdb, output_sdf)
                instance.update({
                    "status": "EXTRACTED_FOR_REVIEW",
                    "isolated_pdb": str(output_pdb),
                    "isolated_pdb_sha256": sha256(output_pdb),
                    "isolated_sdf": str(output_sdf),
                    "isolated_sdf_sha256": sha256(output_sdf),
                    "native_coordinates_preserved": validation["native_coordinate_max_abs_delta_A"] <= 1e-3,
                    "native_coordinate_max_abs_delta_A": validation["native_coordinate_max_abs_delta_A"],
                    "native_coordinate_source_sha256": validation["native_coordinate_source_sha256"],
                    "element_sequence": validation["element_sequence"],
                    "rdkit_parse": validation["rdkit_sdf_round_trip"],
                    "source_conect_pair_count": validation["source_conect_pair_count"],
                    "pdb_inferred_bond_pair_count": validation["pdb_inferred_bond_pair_count"],
                    "sdf_bond_pair_count": validation["sdf_bond_pair_count"],
                    "bond_connectivity_round_trip": validation["bond_connectivity_round_trip"],
                    "bond_order_round_trip": validation["bond_order_round_trip"],
                    "atom_identity_coordinate_mapping": validation["atom_identity_coordinate_mapping"],
                })
            except (OSError, ValueError) as exc:
                instance["error"] = str(exc)
            instances.append(instance)
        record.update({
            "status": "AMBIGUOUS_INSTANCES_INVENTORIED" if len(instances) > 1 else instances[0]["status"],
            "instance_count": len(instances),
            "instances": instances,
            "eligible_for_native_pocket_smoke": False,
        })
        records[target] = record

    extraction_failures = [
        target for target, record in records.items()
        if any(instance.get("status") == "EXTRACTION_FAILED" for instance in record.get("instances", []))
    ]
    result = {
        "schema": "p1-v5-reference-ligand-preflight/v3",
        "script_sha256": sha256(Path(__file__).resolve()),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "REFERENCE_LIGANDS_INVENTORIED_REVIEW_REQUIRED",
        "completion_status": "INCOMPLETE_EXTRACTION_ARTIFACTS" if extraction_failures else "COMPLETE_INVENTORY",
        "extraction_failures": extraction_failures,
        "input_read_only": True,
        "writes_derived_artifacts": True,
        "review_required": True,
        "accepted_for_full_run": False,
        "diffdock_launched": False,
        "vina_launched": False,
        "gromacs_launched": False,
        "consensus_scores_written": False,
        "rrs_pns_updated": False,
        "output_dir": str(output_dir.resolve()),
        "output_json": str(output_json.resolve()),
        "acceptance_rule": "Extraction is provenance-only. Native pocket conditioning requires independently reviewed ligand identity/site correspondence, exact receptor-frame equivalence, and a successful exact-config smoke; no target is eligible from this artifact alone.",
        "targets": records,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if extraction_failures:
        (output_dir / "PREFLIGHT_INCOMPLETE.json").write_text(json.dumps({"schema": "p1-v5-reference-ligand-preflight-incomplete/v1", "result_json_sha256": sha256(output_json), "extraction_failures": extraction_failures}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        (output_dir / "PREFLIGHT_COMPLETE.json").write_text(json.dumps({"schema": "p1-v5-reference-ligand-preflight-complete/v1", "result_json_sha256": sha256(output_json), "artifact_count": len(list(output_dir.iterdir()))}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
