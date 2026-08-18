#!/usr/bin/env python3
"""Junction repair for grafted PfCRT loop candidates via restrained OpenMM relaxation.

The rigid Kabsch graft in ``p2_pfcrt_graft_colabfold_loop.py`` superimposes the
predicted 113--123 anchor/loop interval onto the experimental 6UKJ core, but it
cannot satisfy both peptide junctions simultaneously: the predicted backbone has
its own geometry, so ``C(113)-N(114)`` and ``C(122)-N(123)`` come out of the
1.0--1.8 A range while the loop interior is correct. This script repairs the two
junctions with a physically motivated protocol:

1. Load the grafted PDB as-is (no missing-residue reconstruction, so the loop
   is never re-modeled).
2. Fix the experimental core with strong position restraints on every atom
   outside the 114--122 loop.
3. Apply harmonic distance restraints to the two junction peptide bonds with
   equilibrium 1.33 A.
4. Minimize (L-BFGS), then propagate a short low-temperature Langevin dynamics
   (quasi-static relaxation) to redistribute the backbone geometry.
5. Re-run the *identical* geometry audit used by the graft gate and write a
   fail-closed manifest.

Boundaries: this is a geometry repair witness for the reconstruction-protocol
gate of the PfCRT 114--122 gap. It is not a Set-C system, not a ligand
binding/affinity calculation, not a mutation-resilience study, and not MD-RRS.
Amber14/TIP3P is used as the repair force field; solvation is not required for
restraint-driven local relaxation and is deliberately omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

GRAFT_AUDIT_MODULE = "p2_pfcrt_graft_colabfold_loop.py"
EXPECTED_LOOP = "NKKGNSKER"  # residues 114..122
PEPTIDE_LEN_A = 1.33          # target C-N peptide bond length
RESTRAINT_K = 1000.0          # kJ/mol/nm^2 (strong harmonic)
POSITION_K = 1000.0           # kJ/mol/nm^2 on core heavy atoms
RELAX_TEMPERATURE_K = 10.0    # quasi-static relaxation temperature
RELAX_STEPS = 2000
RELAX_DT_PS = 0.001


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_audit_functions(script_dir: Path):
    """Import audit_geometry and helpers from the graft script (single source of truth)."""
    path = script_dir / GRAFT_AUDIT_MODULE
    if not path.is_file():
        raise SystemExit(f"graft audit module not found: {path}")
    spec = importlib.util.spec_from_file_location("graft_audit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_system(module, grafted_path: Path, reference_path: Path, out: Path):
    """Load the grafted structure as-is and return (system, positions, restraints, context info)."""
    import openmm
    from openmm import app, unit

    grafted = app.PDBFile(str(grafted_path))
    # Reference flanks for anchor identity checks (same rule as the graft gate).
    ref = module.PDBParser(QUIET=True).get_structure("reference", str(reference_path))
    ref_chain = module.model_chain(ref, "A")
    ref_res = module.residue_map(ref_chain)
    if module.one_letter(ref_res[113]) != "G" or module.one_letter(ref_res[123]) != "H":
        raise SystemExit("reference flanks are not GLY113/HIS123")

    forcefield = app.ForceField("amber14-all.xml", "implicit/obc2.xml")
    # Preprocess: keep chain A only, drop HETATM (crystallographic ligand Y01),
    # and append OXT to the C-terminal ASN 405 so OpenMM can apply the terminal
    # patch (the experimental 6UKJ fragment is truncated and lacks OXT).
    prepared = prepare_chain_a_pdb(grafted_path, out / "_chainA_prepared.pdb")
    # PDBFixer completes partial sidechains and adds a consistent hydrogen set
    # (same normalization as the validated full-model witness). The 114--122
    # loop is complete in the grafted input, so findMissingResidues finds no
    # sequence gap and the loop is never re-modeled.
    from pdbfixer import PDBFixer

    fixer = PDBFixer(filename=str(prepared))
    # Detect but NEVER rebuild missing residues: the 114--122 loop is complete
    # in the grafted input and the crystallographic core is kept as-is; only
    # incomplete sidechains of existing residues are completed (same rule as
    # scripts/preparation/fix_pdb_missing_atoms.py).
    fixer.findMissingResidues()
    fixer.missingResidues = {}
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    if fixer.missingAtoms:
        fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    modeller = app.Modeller(fixer.topology, fixer.positions)
    # Defensive: drop any residual non-A chains PDBFixer may have kept.
    to_delete = [c for c in modeller.topology.chains() if c.id not in ("A", "0")]
    if to_delete:
        modeller.delete(to_delete)
    # The crystallographic reference carries antibody chains H/L and a HETATM
    # ligand; only chain A (PfCRT core + grafted loop) is relevant for junction
    # repair and Amber-template matching.
    to_delete = [c for c in modeller.topology.chains() if c.id not in ("A", "0")]
    if to_delete:
        modeller.delete(to_delete)
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=app.NoCutoff,
        constraints=app.HBonds,
    )
    integrator = openmm.LangevinIntegrator(
        RELAX_TEMPERATURE_K * unit.kelvin,
        1.0 / unit.picosecond,
        RELAX_DT_PS * unit.picosecond,
    )

    # ---- junction distance restraints: C(113)-N(114) and C(122)-N(123) ----
    # Resolve atom indices by (residue index in the OpenMM topology, name).
    # The grafted PDB is chain A, residues numbered 1..424 (6UKJ numbering).
    atoms = list(modeller.topology.atoms())
    by_key = {}
    for atom in atoms:
        res = atom.residue
        key = (res.id, atom.name)
        by_key[key] = atom.index
    pairs = []
    for c_res, n_res in ((113, 114), (122, 123)):
        c_key, n_key = (str(c_res), "C"), (str(n_res), "N")
        if c_key not in by_key or n_key not in by_key:
            raise SystemExit(f"junction atoms not found for {c_key} / {n_key}")
        pairs.append((by_key[c_key], by_key[n_key]))
    k = RESTRAINT_K * unit.kilojoule_per_mole / unit.nanometer**2
    for i, j in pairs:
        force = openmm.CustomBondForce("0.5*k*(r-r0)^2")
        force.addPerBondParameter("k")
        force.addPerBondParameter("r0")
        force.addBond(i, j, [k, PEPTIDE_LEN_A * unit.nanometer])
        system.addForce(force)

    # ---- position restraints on core atoms outside the loop (fix the core) ----
    loop_ids = {str(n) for n in range(114, 123)}
    core_atoms = [a.index for a in atoms if a.residue.id not in loop_ids and a.element is not None and a.element.symbol != "H"]
    if not core_atoms:
        raise SystemExit("no core atoms found for position restraints")
    pos_force = openmm.CustomExternalForce("0.5*k*periodicdistance(x,y,z,x0,y0,z0)^2")
    pos_force.addPerParticleParameter("k")
    pos_force.addPerParticleParameter("x0")
    pos_force.addPerParticleParameter("y0")
    pos_force.addPerParticleParameter("z0")
    positions = modeller.positions
    for idx in core_atoms:
        p = positions[idx]
        pos_force.addParticle(
            idx,
            [
                POSITION_K * unit.kilojoule_per_mole / unit.nanometer**2,
                p[0], p[1], p[2],
            ],
        )
    system.addForce(pos_force)

    return {
        "system": system,
        "modeller": modeller,
        "integrator": integrator,
        "junction_pairs": pairs,
        "core_atom_count": len(core_atoms),
        "n_atoms": len(atoms),
    }


def prepare_chain_a_pdb(grafted_path: Path, output_path: Path) -> Path:
    """Extract chain A (standard residues only) and add OXT to the C-terminus.

    The 6UKJ crystallographic reference carries antibody chains H/L and a
    HETATM ligand (Y01) in chain A; the experimental PfCRT fragment is
    truncated at ASN 405 without OXT. OpenMM needs the OXT atom to apply the
    C-terminal patch, so it is placed using the standard peptide geometry
    (OXT is the mirror of O across the CA-C bond, 1.23 A from C).
    """
    import numpy as np

    module = load_audit_functions(Path(__file__).resolve().parent)
    structure = module.PDBParser(QUIET=True).get_structure("grafted", str(grafted_path))
    chain = structure[0]["A"]
    lines = []
    last_resnum = None
    for residue in chain:
        if residue.id[0] != " ":
            continue  # skip HETATM residues (e.g. Y01)
        resnum = residue.id[1]
        for atom in residue:
            coord = atom.coord
            lines.append(
                f"ATOM  {atom.get_serial_number():>5} {atom.name:>4} {residue.resname:>3} A{resnum:>4}    "
                f"{coord[0]:8.3f}{coord[1]:8.3f}{coord[2]:8.3f}{1.0:6.2f}{atom.get_bfactor():6.2f}          "
                f"{atom.element:>2}"
            )
        last_resnum = resnum
    # Append OXT to the last standard residue if missing.
    if last_resnum is not None:
        residues = {r.id[1]: r for r in chain if r.id[0] == " "}
        last = residues[last_resnum]
        if "OXT" not in last:
            c = last["C"].coord
            ca = last["CA"].coord
            o = last["O"].coord
            # Mirror O across the CA-C axis: OXT = C + (CA-C) - (O-C) projected...
            # Standard approach: reflect O through the plane spanned by (CA-C)
            # and the bisector; simplest robust placement used by PDB tools:
            # OXT is O reflected across the C-CA vector.
            vec = c - ca
            vec /= np.linalg.norm(vec)
            o_proj = np.dot(o - c, vec) * vec
            oxt = 2.0 * (c + o_proj) - o
            # enforce ~1.23 A from C
            oxt = c + (oxt - c) / np.linalg.norm(oxt - c) * 1.23
            lines.append(
                f"ATOM  {9999:>5} OXT  {last.resname:>3} A{last_resnum:>4}    "
                f"{oxt[0]:8.3f}{oxt[1]:8.3f}{oxt[2]:8.3f}{1.0:6.2f}{last['C'].get_bfactor():6.2f}          O "
            )
    lines.append("END")
    output_path.write_text("\n".join(lines) + "\n")
    return output_path


def audit_output(module, out_chain, grafted_path: Path, reference_path: Path, model_path: Path):
    """Run the identical graft geometry audit plus provenance fields.

    PDBFile.writeFile drops B-factors, so the loop pLDDT is transferred from the
    grafted input (whose B-factors come from ColabFold) before auditing; the
    pass/fail gate itself never depends on pLDDT.
    """
    grafted_structure = module.PDBParser(QUIET=True).get_structure("grafted", str(grafted_path))
    grafted_chain = module.model_chain(grafted_structure, "A")
    for residue in out_chain:
        src = grafted_chain.child_dict.get(residue.id)
        if src is None:
            continue
        for atom in residue:
            src_atom = src.child_dict.get(atom.id)
            if src_atom is not None:
                atom.set_bfactor(src_atom.get_bfactor())
    audit = module.audit_geometry(out_chain)
    # pLDDT diluted by PDBFixer-added hydrogens (bfactor 0). Report the heavy-
    # atom-only mean for the selection rule ("highest mean loop pLDDT among
    # geometry-passing candidates").
    residues = module.residue_map(out_chain)
    heavy_vals = [
        float(atom.bfactor)
        for n in range(114, 123)
        for atom in residues[n]
        if (atom.element or atom.name[:1]).upper() != "H"
    ]
    audit["loop_plddt_mean_heavy_only"] = float(np.mean(heavy_vals)) if heavy_vals else float("nan")
    audit.update(
        {
            "input_grafted_sha256": sha256(grafted_path),
            "reference_sha256": sha256(reference_path),
            "prediction_sha256": sha256(model_path),
        }
    )
    return audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grafted", type=Path, required=True, help="grafted candidate PDB (graft output)")
    ap.add_argument("--reference", type=Path, required=True, help="experimental 6UKJ reference PDB")
    ap.add_argument("--prediction", type=Path, required=True, help="source ColabFold model PDB (provenance)")
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--mapping", type=Path, required=True, help="sequence mapping artifact (hash check)")
    ap.add_argument("--chain", default="A")
    args = ap.parse_args()
    grafted = args.grafted.resolve()
    reference = args.reference.resolve()
    prediction = args.prediction.resolve()
    out = args.output_dir.resolve()
    mapping = args.mapping.resolve()

    if out == reference.parent or "set_c" in out.parts:
        raise SystemExit("FAIL-CLOSED: output directory cannot be canonical reference or set_c")
    out.mkdir(parents=True, exist_ok=True)

    module = load_audit_functions(Path(__file__).resolve().parent)

    # Provenance: the grafted input must descend from the canonical mapping artifact.
    mapping_data = json.loads(mapping.read_text(encoding="utf-8"))
    if mapping_data.get("checks", {}).get("missing_gap_numbers") != list(range(114, 123)):
        raise SystemExit("FAIL-CLOSED: mapping artifact does not certify exact 114--122 gap")

    import openmm
    from openmm import app, unit

    context = None
    try:
        built = build_system(module, grafted, reference, out)
        system, modeller, integrator = built["system"], built["modeller"], built["integrator"]

        platform_name = os_platform_heuristic()
        context = openmm.Context(system, integrator, openmm.Platform.getPlatformByName(platform_name))

        # 1. L-BFGS minimization
        context.setPositions(modeller.positions)
        state = context.getState(getEnergy=True)
        e0 = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
        openmm.LocalEnergyMinimizer.minimize(context, maxIterations=1000, tolerance=1.0)
        state = context.getState(getEnergy=True)
        e1 = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)

        # 2. Short quasi-static relaxation at 10 K
        state = context.getState(getPositions=True)
        for _ in range(RELAX_STEPS // 100):
            integrator.step(100)
        state = context.getState(getPositions=True, getEnergy=True)
        relaxed = state.getPositions()
        e2 = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)

        repaired_path = out / "repaired.pdb"
        with open(str(repaired_path), "w") as handle:
            # keepIds=True preserves the PDB residue numbering (47..405 + loop),
            # which the geometry audit relies on to locate residues 113--123.
            app.PDBFile.writeFile(modeller.topology, relaxed, handle, keepIds=True)

        # 3. Re-audit with the identical gate
        parser = module.PDBParser(QUIET=True)
        structure = parser.get_structure("repaired", str(repaired_path))
        out_chain = module.model_chain(structure, args.chain)
        audit = audit_output(module, out_chain, grafted, reference, prediction)
        audit.update(
            {
                "energy_before_kj_mol": float(e0),
                "energy_after_minimize_kj_mol": float(e1),
                "energy_after_relax_kj_mol": float(e2),
                "junction_pairs_atom_indices": built["junction_pairs"],
                "core_atom_count": built["core_atom_count"],
                "n_atoms": built["n_atoms"],
                "platform": platform_name,
                "relax_temperature_k": RELAX_TEMPERATURE_K,
                "relax_steps": RELAX_STEPS,
                "relax_dt_ps": RELAX_DT_PS,
            }
        )
        status = "PASS_GEOMETRY" if audit.get("pass") else "BLOCKED_GEOMETRY"
        manifest = {
            "schema_version": 1,
            "status": status,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "scientific_interpretation": "GEOMETRY_REPAIR_WITNESS_ONLY",
            "boundary": "isolated junction repair; no Set-C, no binding/affinity, no RRS, no mutation study",
            "input_grafted": str(grafted),
            "output": str(repaired_path),
            "audit": audit,
        }
        (out / "junction_repair_audit.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"status": status, "output": str(repaired_path), "audit_pass": audit.get("pass"),
                          "peptide_bonds": audit.get("peptide_bond_distances_A"),
                          "loop_plddt_mean": audit.get("loop_plddt_mean"),
                          "anchor_fit_rmsd_A": audit.get("anchor_fit_rmsd_A"),
                          "core_clash_screen_pass": audit.get("core_clash_screen_pass")}, indent=2))
        sys.exit(0 if status == "PASS_GEOMETRY" else 1)
    finally:
        if context is not None:
            try:
                del context
            except Exception:
                pass


def os_platform_heuristic() -> str:
    """Pick CUDA when available (same rule as the OpenMM witness), else CPU."""
    import openmm

    names = [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]
    if "CUDA" in names:
        return "CUDA"
    if "OpenCL" in names:
        return "OpenCL"
    return "CPU"


if __name__ == "__main__":
    main()
