#!/usr/bin/env python3
"""Generate PP-15 ligand ITP for GROMACS from SMILES using OpenFF."""
import sys
from pathlib import Path

smiles = "COc1c(O)cc2c(c1O)C(=O)C([C@H](O)c1ccccc1)CO2"
output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/pp15_ligand.itp")

from openff.toolkit import Molecule
from openff.toolkit.typing.engines.smirnoff import ForceField
from openff.units import unit
import openmm

mol = Molecule.from_smiles(smiles, allow_undefined_stereo=True)
mol.generate_conformers(n_conformers=1)
mol.assign_partial_charges(partial_charge_method="am1bcc")

ff = ForceField("openff-2.2.0.offxml")
omm_system = ff.create_openmm_system(mol.to_topology())

charges = mol.partial_charges.to(unit.elementary_charge).magnitude

with open(output, "w") as f:
    f.write("; PP-15 ligand ITP (OpenFF 2.2.0 AM1-BCC)\n")
    f.write("[ moleculetype ]\nUNL     3\n\n")
    f.write("[ atoms ]\n")
    for i, atom in enumerate(mol.atoms):
        elem = atom.symbol
        chg = float(charges[i])
        mass = atom.mass.to(unit.amu).magnitude
        f.write(f"  {i+1:5d}  {elem:>4s}  1  UNL  {elem:>4s}  {i+1:5d}  {chg:10.6f}  {mass:8.4f}\n")

    f.write("\n[ bonds ]\n")
    for force in omm_system.getForces():
        if isinstance(force, openmm.HarmonicBondForce):
            for j in range(force.getNumBonds()):
                # getBondParameters returns (p1, p2, length, k)
                p1, p2, r0, k_par = force.getBondParameters(j)
                r0_nm = r0.value_in_unit(openmm.unit.nanometer)
                k_val = k_par.value_in_unit(openmm.unit.kilojoule_per_mole / openmm.unit.nanometer**2)
                f.write(f"  {int(p1)+1:5d}  {int(p2)+1:5d}  1  {r0_nm:10.6f}  {k_val:10.4f}\n")

    f.write("\n[ angles ]\n")
    for force in omm_system.getForces():
        if isinstance(force, openmm.HarmonicAngleForce):
            for j in range(force.getNumAngles()):
                # getAngleParameters returns (p1, p2, p3, theta, k)
                p1, p2, p3, theta, k_par = force.getAngleParameters(j)
                th_rad = theta.value_in_unit(openmm.unit.radian)
                k_val = k_par.value_in_unit(openmm.unit.kilojoule_per_mole / openmm.unit.radian**2)
                f.write(f"  {int(p1)+1:5d}  {int(p2)+1:5d}  {int(p3)+1:5d}  1  {th_rad:10.6f}  {k_val:10.4f}\n")

    f.write("\n[ dihedrals ]\n")
    for force in omm_system.getForces():
        if isinstance(force, openmm.PeriodicTorsionForce):
            for j in range(force.getNumTorsions()):
                # getTorsionParameters returns (p1, p2, p3, p4, periodicity, phase, k)
                p1, p2, p3, p4, per, phase, k_par = force.getTorsionParameters(j)
                ph_rad = phase.value_in_unit(openmm.unit.radian)
                k_val = k_par.value_in_unit(openmm.unit.kilojoule_per_mole)
                f.write(f"  {int(p1)+1:5d}  {int(p2)+1:5d}  {int(p3)+1:5d}  {int(p4)+1:5d}  1  {int(per)}  {ph_rad:10.6f}  {k_val:10.4f}\n")

print(f"Written {mol.n_atoms} atoms to {output}")
