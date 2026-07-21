#!/usr/bin/env python3
"""Standalone MD simulation script converted from the T019 talktorial notebook.

This script downloads a PDB structure, prepares the protein and ligand,
builds an OpenMM system, minimizes it, and runs a short MD trajectory.
"""

import argparse
import copy
import sys
from pathlib import Path

import numpy as np
import requests
from rdkit import Chem
from rdkit.Chem import AllChem
import mdtraj as md
import pdbfixer
import openmm as mm
import openmm.app as app
from openmm import unit
from openff.toolkit.topology import Molecule
from openmmforcefields.generators import GAFFTemplateGenerator


DEFAULT_PDB_ID = "1J3I"
DEFAULT_LIGAND_NAME = "LIG001"
DEFAULT_OUTPUT_DIR = Path("protein_prep")
DEFAULT_LIGAND_SMILES = (
    "COc1cc(C)c([C@H](C)NC(=O)c2ccc(CC[NH3+])cc2)cc1OC"
)


def download_pdb(pdb_id: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    response = requests.get(url)
    response.raise_for_status()
    with open(destination, "wb") as f:
        f.write(response.content)
    return destination


def prepare_protein(
    pdb_file,
    ignore_missing_residues=True,
    ignore_terminal_missing_residues=True,
    ph=7.0,
):
    fixer = pdbfixer.PDBFixer(str(pdb_file))
    fixer.removeHeterogens()
    fixer.findMissingResidues()

    if ignore_terminal_missing_residues:
        chains = list(fixer.topology.chains())
        keys = list(fixer.missingResidues.keys())
        for key in keys:
            chain = chains[key[0]]
            if key[1] == 0 or key[1] == len(list(chain.residues())):
                del fixer.missingResidues[key]

    if ignore_missing_residues:
        fixer.missingResidues = {}

    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(ph)
    return fixer


def prepare_ligand(pdb_file: Path, resname: str, smiles: str, depict: bool = False):
    rdkit_mol = Chem.MolFromPDBFile(str(pdb_file))
    rdkit_mol_split = Chem.rdmolops.SplitMolByPDBResidues(rdkit_mol)
    ligand = rdkit_mol_split[resname]
    ligand = Chem.RemoveHs(ligand)

    reference_mol = Chem.MolFromSmiles(smiles)
    prepared_ligand = AllChem.AssignBondOrdersFromTemplate(reference_mol, ligand)
    prepared_ligand.AddConformer(ligand.GetConformer(0))
    prepared_ligand = Chem.rdmolops.AddHs(prepared_ligand, addCoords=True)
    prepared_ligand = Chem.MolFromMolBlock(Chem.MolToMolBlock(prepared_ligand))

    if depict:
        ligand_2d = copy.deepcopy(ligand)
        prepared_ligand_2d = copy.deepcopy(prepared_ligand)
        AllChem.Compute2DCoords(ligand_2d)
        AllChem.Compute2DCoords(prepared_ligand_2d)
        print("Ligand preparation complete. Depiction is not available in script mode.")

    return prepared_ligand


def rdkit_to_openmm(rdkit_mol, name="LIG"):
    off_mol = Molecule.from_rdkit(rdkit_mol)
    off_mol.name = name

    element_counter = {}
    for off_atom, rdkit_atom in zip(off_mol.atoms, rdkit_mol.GetAtoms()):
        element = rdkit_atom.GetSymbol()
        element_counter[element] = element_counter.get(element, 0) + 1
        off_atom.name = f"{element}{element_counter[element]}"

    off_topology = off_mol.to_topology()
    mol_topology = off_topology.to_openmm()
    mol_positions = off_mol.conformers[0].to("nanometers")
    return app.Modeller(mol_topology, mol_positions)


def merge_protein_and_ligand(protein, ligand):
    md_protein_topology = md.Topology.from_openmm(protein.topology)
    md_ligand_topology = md.Topology.from_openmm(ligand.topology)
    md_complex_topology = md_protein_topology.join(md_ligand_topology)
    complex_topology = md_complex_topology.to_openmm()

    total_atoms = len(protein.positions) + len(ligand.positions)
    complex_positions = unit.Quantity(np.zeros((total_atoms, 3)), unit=unit.nanometers)
    complex_positions[: len(protein.positions)] = protein.positions
    complex_positions[len(protein.positions) :] = ligand.positions

    return complex_topology, complex_positions


def generate_forcefield(rdkit_mol=None, protein_ff="amber14-all.xml", solvent_ff="amber14/tip3pfb.xml"):
    forcefield = app.ForceField(protein_ff, solvent_ff)
    if rdkit_mol is not None:
        gaff = GAFFTemplateGenerator(
            molecules=Molecule.from_rdkit(rdkit_mol, allow_undefined_stereo=True)
        )
        forcefield.registerTemplateGenerator(gaff.generator)
    return forcefield


def build_simulation(
    complex_topology,
    complex_positions,
    forcefield,
    output_dir: Path,
    steps: int,
    write_interval: int,
    log_interval: int,
):
    modeller = app.Modeller(complex_topology, complex_positions)
    modeller.addSolvent(forcefield, padding=1.0 * unit.nanometers, ionicStrength=0.15 * unit.molar)

    system = forcefield.createSystem(modeller.topology, nonbondedMethod=app.PME)
    integrator = mm.LangevinIntegrator(
        300 * unit.kelvin, 1.0 / unit.picoseconds, 2.0 * unit.femtoseconds
    )
    simulation = app.Simulation(modeller.topology, system, integrator)
    simulation.context.setPositions(modeller.positions)

    output_dir.mkdir(parents=True, exist_ok=True)
    # Replace the md.reporters.XTCReporter line with:
    simulation.reporters.append(
        app.DCDReporter(str(output_dir / "trajectory.dcd"), reportInterval=write_interval)
        )
    simulation.reporters.append(
        app.StateDataReporter(
            sys.stdout,
            log_interval,
            step=True,
            potentialEnergy=True,
            temperature=True,
            progress=True,
            remainingTime=True,
            speed=True,
            totalSteps=steps,
            separator="\t",
        )
    )

    return simulation


def main():
    parser = argparse.ArgumentParser(description="Run an OpenMM MD simulation for a protein-ligand complex.")
    parser.add_argument(
        "--pdb-id",
        default=DEFAULT_PDB_ID,
        help="PDB ID to download and simulate. Matches step2_protein_prep.py.",
    )
    parser.add_argument(
        "--ligand-name",
        default=DEFAULT_LIGAND_NAME,
        help="Ligand residue name used by the downstream prep scripts.",
    )
    parser.add_argument(
        "--ligand-smiles",
        default=DEFAULT_LIGAND_SMILES,
        help="Isomeric SMILES string for the ligand. Update this to match step1_ligand_prep.py and step1b_openff_parameterization.py.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for downloaded PDB files, simulation outputs, and snapshots. Matches step2_protein_prep.py.",
    )
    parser.add_argument("--steps", type=int, default=10, help="Number of MD steps to run.")
    parser.add_argument("--write-interval", type=int, default=1, help="Trajectory write interval in steps.")
    parser.add_argument("--log-interval", type=int, default=1, help="Log interval in steps.")
    parser.add_argument("--ph", type=float, default=7.0, help="pH for protein protonation.")
    parser.add_argument("--ignore-missing-residues", action="store_true", help="Ignore missing residues in the PDB structure.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    pdb_path = out_dir / f"{args.pdb_id}.pdb"

    if not pdb_path.exists():
        print(f"Downloading PDB {args.pdb_id} to {pdb_path}")
        download_pdb(args.pdb_id, pdb_path)

    prepared_protein = prepare_protein(
        pdb_path,
        ignore_missing_residues=args.ignore_missing_residues,
        ignore_terminal_missing_residues=not args.ignore_missing_residues,
        ph=args.ph,
    )

    rdkit_ligand = prepare_ligand(pdb_path, args.ligand_name, args.ligand_smiles, depict=False)
    omm_ligand = rdkit_to_openmm(rdkit_ligand, name=args.ligand_name)
    complex_topology, complex_positions = merge_protein_and_ligand(prepared_protein, omm_ligand)

    print("Complex topology has", complex_topology.getNumAtoms(), "atoms.")
    forcefield = generate_forcefield(rdkit_ligand)
    simulation = build_simulation(
        complex_topology,
        complex_positions,
        forcefield,
        out_dir,
        steps=args.steps,
        write_interval=args.write_interval,
        log_interval=args.log_interval,
    )

    print("Minimizing energy...")
    simulation.minimizeEnergy()
    with open(out_dir / "topology.pdb", "w") as pdb_file:
        app.PDBFile.writeFile(
            simulation.topology,
            simulation.context.getState(getPositions=True, enforcePeriodicBox=True).getPositions(),
            file=pdb_file,
            keepIds=True,
        )

    print("Running MD simulation...")
    simulation.context.setVelocitiesToTemperature(300 * unit.kelvin)
    simulation.step(args.steps)

    trajectory_path = out_dir / "trajectory.dcd"
    if trajectory_path.exists() and trajectory_path.stat().st_size > 0:
        print(f"Simulation complete. Trajectory written to {trajectory_path}")
    else:
        raise RuntimeError("Trajectory file was not generated or is empty.")


if __name__ == "__main__":
    main()
