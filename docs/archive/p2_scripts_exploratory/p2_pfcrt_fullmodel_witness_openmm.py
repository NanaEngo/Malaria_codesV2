#!/usr/bin/env python3
"""Isolated technical MD witness for a complete PfCRT prediction.

This is deliberately not a Set-C preparation and does not use the rejected
114--122 graft. It asks only whether the complete predicted chain can be
minimized and propagated briefly in an explicit solvent box with OpenMM.
No ligand, pocket, mutation, RRS, or biological validation is inferred.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser

STANDARD = {
    "ALA":"A", "ARG":"R", "ASN":"N", "ASP":"D", "CYS":"C",
    "GLN":"Q", "GLU":"E", "GLY":"G", "HIS":"H", "ILE":"I",
    "LEU":"L", "LYS":"K", "MET":"M", "PHE":"F", "PRO":"P",
    "SER":"S", "THR":"T", "TRP":"W", "TYR":"Y", "VAL":"V",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sequence_from_pdb(path: Path):
    structure = PDBParser(QUIET=True).get_structure("pfcrt", str(path))
    model = next(iter(structure))
    chains = list(model.get_chains())
    if len(chains) != 1 or chains[0].id != "A":
        raise ValueError(f"expected exactly one chain A, found {[c.id for c in chains]}")
    residues = [r for r in chains[0] if r.id[0] == " " and r.id[2] == " "]
    if len(residues) != 424:
        raise ValueError(f"complete-model gate failed: expected 424 residues, found {len(residues)}")
    numbers = [r.id[1] for r in residues]
    if numbers != list(range(1, 425)):
        raise ValueError("complete-model gate failed: residue numbering is not 1..424")
    seq = "".join(STANDARD.get(r.resname.strip(), "?") for r in residues)
    if "?" in seq:
        raise ValueError("complete-model gate failed: non-standard residue in chain A")
    return seq


def load_expected_fasta(path: Path) -> str:
    lines = [x.strip() for x in path.read_text().splitlines() if x.strip() and not x.startswith(">")]
    seq = "".join(lines).replace(" ", "").upper()
    if len(seq) != 424:
        raise ValueError(f"reference FASTA length is {len(seq)}, expected 424")
    return seq


def write_json(path: Path, payload: dict):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def validate_ensemble_link(model: Path, manifest_path: Path, model_sha: str) -> dict:
    """Prove that the witness input is an output of the completed GPU ensemble."""
    if not manifest_path.is_file():
        raise ValueError(f"missing ensemble completion manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("status") != "COLABFOLD_ENSEMBLE_COMPLETED":
        raise ValueError("ensemble manifest is not COLABFOLD_ENSEMBLE_COMPLETED")
    if manifest.get("accession") != "W7FI62":
        raise ValueError("ensemble manifest accession is not W7FI62")
    try:
        relative = str(model.relative_to(manifest_path.parent))
    except ValueError as exc:
        raise ValueError("witness model is outside the ensemble output root") from exc
    declared = manifest.get("outputs", {}).get(relative)
    if declared is None:
        raise ValueError(f"model is absent from ensemble output hash map: {relative}")
    if declared != model_sha:
        raise ValueError("witness model hash differs from completed ensemble manifest")
    return {
        "path": str(manifest_path),
        "sha256": sha256(manifest_path),
        "relative_model": relative,
        "declared_model_sha256": declared,
        "slurm_job_id": manifest.get("slurm_job_id"),
    }


def parse_witness_log(path: Path):
    """Return conservative QC metrics from StateDataReporter CSV output."""
    if not path.is_file() or path.stat().st_size == 0:
        return {"rows": 0, "finite_rows": False, "error_markers": ["missing_or_empty_md_log"]}
    text = path.read_text(errors="replace")
    markers = sorted(set(re.findall(r"(?i)(?:nan|inf(?:inity)?|cuda error|exception|segmentation fault|fatal error|lincs warning)", text)))
    rows = []
    for raw in text.splitlines():
        fields = [x.strip() for x in raw.split(",")]
        if len(fields) < 5:
            continue
        try:
            step = int(float(fields[0]))
            values = [float(fields[i]) for i in range(1, 5)]
        except (ValueError, TypeError):
            continue
        rows.append({"step": step, "time_ps": values[0], "potential_kj_mol": values[1], "temperature_k": values[2], "volume_nm3": values[3]})
    finite = bool(rows) and bool(np.isfinite([[v for k, v in row.items() if k != "step"] for row in rows]).all())
    return {"rows": len(rows), "finite_rows": finite, "error_markers": markers, "first_step": rows[0]["step"] if rows else None, "last_step": rows[-1]["step"] if rows else None, "temperature_range_k": [min(r["temperature_k"] for r in rows), max(r["temperature_k"] for r in rows)] if rows else None, "volume_range_nm3": [min(r["volume_nm3"] for r in rows), max(r["volume_nm3"] for r in rows)] if rows else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--reference-fasta", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--ensemble-manifest", type=Path, required=True)
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--temperature-k", type=float, default=310.15)
    args = ap.parse_args()
    model = args.model.resolve()
    fasta = args.reference_fasta.resolve()
    out = args.output_dir.resolve()
    ensemble_manifest = args.ensemble_manifest.resolve()
    project_root = Path(__file__).resolve().parents[1]
    protected_roots = (project_root / "results/md_systems/set_c").resolve(), (project_root / "data/proteins/mutants").resolve()
    if any(out == root or root in out.parents for root in protected_roots):
        raise SystemExit("FAIL-CLOSED: output overlaps canonical Set-C/mutant directory")
    if not model.is_file() or not fasta.is_file():
        raise SystemExit("FAIL-CLOSED: model or reference FASTA missing")
    if "grafted" in str(model).lower() or "candidate_" in model.name.lower():
        raise SystemExit("FAIL-CLOSED: rejected graft/candidate model cannot enter full-model witness")

    # Create the fresh isolated root only after all path/input guards pass and
    # before provenance is written. The sbatch wrapper separately refuses a
    # pre-existing root, so this remains a stale-output fail-closed boundary.
    out.mkdir(parents=True, exist_ok=False)
    model_sha = sha256(model)
    fasta_sha = sha256(fasta)
    try:
        ensemble_link = validate_ensemble_link(model, ensemble_manifest, model_sha)
    except Exception as exc:
        raise SystemExit(f"FAIL-CLOSED: ensemble provenance validation failed: {exc}") from exc
    model_seq = sequence_from_pdb(model)
    ref_seq = load_expected_fasta(fasta)
    if model_seq != ref_seq:
        raise SystemExit("FAIL-CLOSED: predicted model sequence does not exactly match W7FI62 FASTA")

    provenance = {
        "schema_version": 1,
        "status": "TECHNICAL_MODEL_STABILITY_REQUESTED",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_model": str(model),
        "input_model_sha256": model_sha,
        "reference_fasta": str(fasta),
        "reference_fasta_sha256": fasta_sha,
        "ensemble_manifest": ensemble_link,
        "accession": "W7FI62",
        "model_semantics": "complete AlphaFold2-PTM prediction; not experimental PfCRT structure",
        "protocol": {
            "engine": "OpenMM",
            "protein_force_field": "amber14-all.xml",
            "water_model": "amber14/tip3p.xml",
            "temperature_k": args.temperature_k,
            "steps": args.steps,
            "timestep_fs": 2.0,
            "solvent_padding_nm": 1.0,
            "ionic_strength_m": 0.15,
            "minimization_max_iterations": 5000,
        },
        "boundary": "isolated technical stability witness only; no ligand, pocket validation, mutant, RRS, Set-C, QC, or production-MD authorization",
    }
    write_json(out / "witness_provenance_requested.json", provenance)

    from pdbfixer import PDBFixer
    from openmm import LangevinMiddleIntegrator, Platform, unit
    from openmm.app import (ForceField, HBonds, Modeller, PME, PDBFile,
                            Simulation, StateDataReporter, DCDReporter)

    fixer = PDBFixer(filename=str(model))
    fixer.findMissingResidues()
    missing_residues = {str(k): v for k, v in fixer.missingResidues.items() if v}
    if missing_residues:
        provenance["missing_residues"] = missing_residues
        provenance["status"] = "BLOCKED_MISSING_RESIDUES"
        write_json(out / "witness_provenance_failed.json", provenance)
        raise SystemExit("FAIL-CLOSED: PDBFixer found missing residues in complete-model input")
    fixer.findNonstandardResidues()
    if fixer.nonstandardResidues:
        provenance["status"] = "BLOCKED_NONSTANDARD_RESIDUES"
        provenance["nonstandard_residues"] = [str(x[0].id) for x in fixer.nonstandardResidues]
        write_json(out / "witness_provenance_failed.json", provenance)
        raise SystemExit("FAIL-CLOSED: nonstandard residues require explicit review")
    fixer.findMissingAtoms()
    if fixer.missingAtoms:
        fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    prepared_model = out / "prepared_model.pdb"
    PDBFile.writeFile(fixer.topology, fixer.positions, str(prepared_model))
    prepared_model_sha = sha256(prepared_model)
    provenance.update({
        "prepared_model": str(prepared_model),
        "prepared_model_sha256": prepared_model_sha,
        "forcefield_policy": {
            "protein": "Amber14-all",
            "water": "TIP3P",
            "status": "ISOLATED_WITNESS_DEVIATION",
            "not_comparable_to": "P2 canonical CHARMM36m + CGenFF/OpenFF policy",
            "reason": "technical stability witness on complete predicted model; not a parent-study or Set-C MD system",
        },
    })

    forcefield = ForceField("amber14-all.xml", "amber14/tip3p.xml")
    modeller = Modeller(fixer.topology, fixer.positions)
    modeller.addSolvent(forcefield, model="tip3p", padding=1.0 * unit.nanometer,
                        ionicStrength=0.15 * unit.molar)
    system = forcefield.createSystem(
        modeller.topology, nonbondedMethod=PME, nonbondedCutoff=1.0 * unit.nanometer,
        constraints=HBonds, rigidWater=True, hydrogenMass=None,
    )
    integrator = LangevinMiddleIntegrator(
        args.temperature_k * unit.kelvin, 1.0 / unit.picosecond, 0.002 * unit.picoseconds
    )
    integrator.setRandomNumberSeed(20260811)
    try:
        platform = Platform.getPlatformByName("CUDA")
        properties = {"Precision": "mixed"}
    except Exception:
        platform = Platform.getPlatformByName("CPU")
        properties = {}
        provenance["platform_fallback"] = "CPU"
    provenance["platform"] = platform.getName()
    if platform.getName() != "CUDA":
        provenance["status"] = "BLOCKED_NO_CUDA_OPENMM"
        write_json(out / "witness_provenance_failed.json", provenance)
        raise SystemExit("FAIL-CLOSED: OpenMM CUDA platform unavailable")

    simulation = Simulation(modeller.topology, system, integrator, platform, properties)
    simulation.context.setPositions(modeller.positions)
    state0 = simulation.context.getState(getEnergy=True, getPositions=True)
    e0 = state0.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    simulation.minimizeEnergy(maxIterations=5000)
    state1 = simulation.context.getState(getEnergy=True, getPositions=True)
    e1 = state1.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    PDBFile.writeFile(simulation.topology, state1.getPositions(), str(out / "minimized.pdb"))
    simulation.reporters.append(StateDataReporter(str(out / "md.log"), 1000, step=True, time=True, potentialEnergy=True, temperature=True, volume=True, speed=True))
    simulation.reporters.append(DCDReporter(str(out / "witness.dcd"), max(1, args.steps // 10)))
    simulation.step(args.steps)
    final = simulation.context.getState(getEnergy=True, getPositions=True)
    ef = final.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    final_positions_nm = final.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    PDBFile.writeFile(simulation.topology, final.getPositions(), str(out / "final.pdb"))
    log_qc = parse_witness_log(out / "md.log")
    finite = bool(np.isfinite([e0, e1, ef]).all()) and bool(np.isfinite(final_positions_nm).all())
    qc_pass = finite and log_qc["rows"] >= 2 and log_qc["finite_rows"] and not log_qc["error_markers"]
    provenance.update({
        "status": "TECHNICAL_MODEL_STABILITY_PASS" if qc_pass else "TECHNICAL_MODEL_STABILITY_FAILED_QC",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "energies_kj_mol": {"initial": float(e0), "minimized": float(e1), "final": float(ef)},
        "final_positions_finite": bool(np.isfinite(final_positions_nm).all()),
        "steps_completed": args.steps,
        "log_qc": log_qc,
        "qc_scope": "StateDataReporter md.log only; Slurm stdout/stderr are operational logs and were not treated as scientific QC",
        "output_files": sorted(p.name for p in out.iterdir()),
        "interpretation": "Short OpenMM CUDA trajectory witness on a complete predicted model only; Amber14/TIP3P deviation, not structural validation, ligand binding evidence, mutation resilience, canonical Set-C MD, or MD-RRS.",
    })
    write_json(out / "witness_provenance_completed.json", provenance)
    print(json.dumps({"status": provenance["status"], "platform": provenance["platform"], "steps": args.steps, "energies_kj_mol": provenance["energies_kj_mol"]}, indent=2))
    return 0 if provenance["status"] == "TECHNICAL_MODEL_STABILITY_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
