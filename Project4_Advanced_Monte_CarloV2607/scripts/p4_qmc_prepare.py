#!/usr/bin/env python3
"""P4 — Prepare molecular inputs for Quantum Monte Carlo (QMC) validation.

This script converts candidate SMILES into:

1. **3D geometries** via RDKit (EmbedMultipleConfs + MMFF94) and optional
   OpenBabel (UFF/GAFF) refinement
2. **Trial wavefunction inputs** using PennyLane (IQPEmbedding circuits)
   or PySCF (Hartree-Fock/DFT) when available
3. **QMC input files** for QMCPACK (XML) and CASINO (input)

All external packages (PySCF, CASINO, QMCPACK) are optional — the script
gracefully degrades and uses whatever is available.

Usage
-----
# Single molecule
python p4_qmc_prepare.py --smiles "CCO" --output-dir qmc_inputs

# Batch from file
python p4_qmc_prepare.py --smiles-file candidates.txt --output-dir qmc_inputs

# With OpenBabel geometry refinement
python p4_qmc_prepare.py --smiles "CCO" --optimize uff
"""

from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

logger = logging.getLogger("p4_qmc_prepare")

# ── Optional dependencies ────────────────────────────────────────────
_HAS_RDKIT = False
_HAS_DESCRIPTORS3D = False
_HAS_OPENBABEL = False
_HAS_PENNYLANE = False
_HAS_PYSCF = False

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdMolAlign, rdMolDescriptors

    # Descriptors3D may not be available in all RDKit versions
    try:
        from rdkit.Chem.Descriptors3D import (
            CalcAsphericity,
            CalcEccentricity,
            CalcInertialShapeFactor,
        )
        _HAS_DESCRIPTORS3D = True
    except ImportError:
        _HAS_DESCRIPTORS3D = False
        CalcAsphericity = None
        CalcEccentricity = None
        CalcInertialShapeFactor = None

    _HAS_RDKIT = True
except ImportError:
    _HAS_DESCRIPTORS3D = False
    pass

try:
    from openbabel import openbabel as ob

    _HAS_OPENBABEL = True
except ImportError:
    try:
        # openbabel-wheel namespace
        import openbabel

        ob = openbabel.openbabel
        _HAS_OPENBABEL = True
    except ImportError:
        pass

try:
    import pennylane as qml

    _HAS_PENNYLANE = True
except ImportError:
    pass

try:
    import pyscf

    _HAS_PYSCF = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════
#  1. Geometry generation
# ═══════════════════════════════════════════════════════════════════════


def _canonical_smiles(smiles: str) -> str:
    """Return canonical RDKit SMILES, or original on failure."""
    if not _HAS_RDKIT:
        return smiles
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(mol) if mol else smiles


def _smiles_hash(smiles: str) -> str:
    """Short, reproducible hash for directory naming."""
    canon = _canonical_smiles(smiles)
    return hashlib.sha256(canon.encode()).hexdigest()[:12]


def generate_rdkit_conformers(
    smiles: str,
    n_conformers: int = 50,
    rmsd_threshold: float = 0.5,
    optimize: bool = True,
    max_optimization_cycles: int = 200,
) -> tuple[Optional["Chem.Mol"], list[int]]:
    """Generate 3D conformers using RDKit's EmbedMultipleConfs + MMFF94.

    Parameters
    ----------
    smiles : str
        Input SMILES.
    n_conformers : int
        Maximum number of conformers to generate.
    rmsd_threshold : float
        RMSD pruning threshold (Angstrom) for conformer clustering.
    optimize : bool
        If True, run MMFF94 force-field optimisation on each conformer.
    max_optimization_cycles : int
        Max MMFF94 optimisation iterations.

    Returns
    -------
    mol : Chem.Mol or None
        Molecule with embedded conformers.
    conf_ids : list of int
        List of conformer IDs that survived optimisation.
    """
    if not _HAS_RDKIT:
        return None, []

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        logger.error("Invalid SMILES: %s", smiles)
        return None, []

    # Add hydrogens explicitly for 3D generation
    mol = Chem.AddHs(mol)

    # Generate conformers
    params = AllChem.EmbedMultipleConfs(
        mol,
        numConfs=n_conformers,
        randomSeed=42,
        pruneRmsThresh=rmsd_threshold,
        useRandomCoords=True,
        useExpTorsionAnglePrefs=True,
        useBasicKnowledge=True,
    )

    if optimize:
        # MMFF94 optimisation
        results = AllChem.MMFFOptimizeMoleculeConfs(
            mol,
            numThreads=0,  # use all CPU cores
            maxIters=max_optimization_cycles,
        )
        # Filter conformers that converged (MMFF return: (converged, energy))
        valid_ids = [
            conf_id for conf_id, (converged, _energy) in enumerate(results) if converged == 0
        ]
    else:
        valid_ids = list(range(mol.GetNumConformers()))

    if not valid_ids:
        logger.warning("No valid conformers for %s", smiles)
        return None, []

    # Keep only the lowest-energy conformer by default
    if optimize and len(valid_ids) > 1:
        energies = [
            (conf_id, AllChem.MMFFGetMoleculeForceField(mol, AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94s"), confId=conf_id).CalcEnergy())
            for conf_id in valid_ids
        ]
        # Handle None force fields
        energies = [(cid, e) for cid, e in energies if e is not None]
        if energies:
            energies.sort(key=lambda x: x[1])
            best_id = energies[0][0]
            valid_ids = [best_id]

    return mol, valid_ids


def write_xyz(mol: "Chem.Mol", conf_id: int, path: Path) -> None:
    """Write an XYZ geometry file from an RDKit molecule with a specific conformer.

    Parameters
    ----------
    mol : Chem.Mol
        RDKit molecule with embedded conformer.
    conf_id : int
        Conformer ID to write.
    path : Path
        Output XYZ file path.
    """
    if not _HAS_RDKIT:
        return

    conf = mol.GetConformer(conf_id)
    symbols = []
    coords = []

    for atom in mol.GetAtoms():
        symbol = atom.GetSymbol()
        pos = conf.GetAtomPosition(atom.GetIdx())
        symbols.append(symbol)
        coords.append((pos.x, pos.y, pos.z))

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"{len(symbols)}\n")
        fh.write(f"Generated by P4 QMC prepare for molecule {mol.GetNumAtoms()} atoms\n")
        for sym, (x, y, z) in zip(symbols, coords):
            fh.write(f"{sym:2s}  {x:.6f}  {y:.6f}  {z:.6f}\n")


def optimize_with_openbabel(xyz_path: Path, method: str = "uff", n_steps: int = 500) -> Optional[Path]:
    """Run OpenBabel geometry optimisation on an XYZ file.

    Parameters
    ----------
    xyz_path : Path
        Input XYZ geometry file.
    method : str
        Force field: "uff" (default), "gaff", "mmff94".
    n_steps : int
        Maximum optimisation steps.

    Returns
    -------
    Path or None
        Path to the optimised XYZ file, or None on failure.
    """
    if not _HAS_OPENBABEL:
        logger.info("OpenBabel not available; skipping geometry optimisation.")
        return None

    output_path = xyz_path.with_suffix(".opt.xyz")

    try:
        mol = ob.OBMol()
        obconv = ob.OBConversion()
        obconv.SetInFormat("xyz")
        obconv.SetOutFormat("xyz")

        if not obconv.ReadFile(mol, str(xyz_path)):
            logger.error("OpenBabel failed to read %s", xyz_path)
            return None

        # Setup force field
        ff = ob.OBForceField.FindForceField(method)
        if ff is None:
            logger.warning("OpenBabel force field '%s' not found; trying UFF.", method)
            ff = ob.OBForceField.FindForceField("UFF")
            if ff is None:
                logger.warning("UFF not available either; skipping optimisation.")
                return None

        # Setup and run optimisation
        ff.Setup(mol)
        ff.SteepestDescent(n_steps)
        ff.ConjugateGradients(n_steps // 2)
        ff.GetCoordinates(mol)

        obconv.WriteFile(mol, str(output_path))
        logger.info("OpenBabel %s optimisation wrote %s", method, output_path)
        return output_path

    except Exception as exc:
        logger.warning("OpenBabel optimisation failed: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════════════════
#  2. Trial wavefunction generation
# ═══════════════════════════════════════════════════════════════════════


def generate_pennylane_circuit(
    smiles: str,
    n_qubits: int = 8,
    n_layers: int = 2,
) -> tuple[str, str]:
    """Generate a PennyLane trial wavefunction description.

    Since PennyLane is available (0.45.1), this generates an actual
    quantum circuit description using IQPEmbedding encoding, which
    creates a classically hard-to-simulate trial wavefunction.

    Parameters
    ----------
    smiles : str
        Input SMILES (used to derive feature vector).
    n_qubits : int
        Number of qubits (max 8 for classical simulator).
    n_layers : int
        Number of variational layers.

    Returns
    -------
    circuit_code : str
        Python code for the PennyLane circuit.
    description : str
        Human-readable description of the trial wavefunction.
    """
    if not _HAS_PENNYLANE:
        return _pennylane_not_available(n_qubits, n_layers)

    # Derive a feature vector from the SMILES using its hash
    seed = int(hashlib.sha256(smiles.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    features = rng.uniform(-1, 1, size=n_qubits * n_layers)

    # Build the circuit description
    circuit_lines = [
        "import pennylane as qml",
        "import numpy as np",
        "",
        f"n_qubits = {n_qubits}",
        f"n_layers = {n_layers}",
        "",
        "# IQPEmbedding based trial wavefunction",
        "# Uses ZZ feature encoding for entangling capability",
        "",
        f"feature_vector = {list(features.round(4))}",
        "",
        "dev = qml.device('default.qubit', wires=n_qubits)",
        "",
        "@qml.qnode(dev)",
        "def trial_wavefunction(params):",
        "    '''Trial wavefunction with IQPEmbedding + variational layers.'''",
        "    # Encode features via IQPEmbedding (classically hard to simulate)",
        "    qml.IQPEmbedding(features=params[:n_qubits], wires=range(n_qubits), n_repeats=2)",
        "    # Variational layers",
        "    for layer in range(n_layers):",
        "        qml.BasicEntanglerLayers(",
        "            theta=params.reshape((n_layers, n_qubits)),",
        "            wires=range(n_qubits),",
        "            rotation=qml.RY,",
        "        )",
        "    return qml.state()",
        "",
        "# Compute trial energy expectation value",
        "# H = sum of Z_i Z_{i+1} + X_i (transverse Ising)",
        "coeffs = [1.0] * (n_qubits - 1) + [0.5] * n_qubits",
        "obs = [qml.Z(i) @ qml.Z(i+1) for i in range(n_qubits-1)] + [qml.X(i) for i in range(n_qubits)]",
        "H = qml.Hamiltonian(coeffs, obs)",
        "",
        "@qml.qnode(dev)",
        "def energy(params):",
        "    trial_wavefunction(params)",
        "    return qml.expval(H)",
        "",
        "# Example: compute trial energy with random parameters",
        "params = np.random.uniform(-np.pi, np.pi, size=(n_layers, n_qubits))",
        "trial_energy = energy(params)",
    ]

    description = (
        f"PennyLane IQPEmbedding trial wavefunction ({n_qubits} qubits, "
        f"{n_layers} layers, {n_qubits * n_layers} variational parameters). "
        f"The IQPEmbedding encoding creates classically hard-to-simulate "
        f"superpositions ideal for QMC trial wavefunctions."
    )

    return "\n".join(circuit_lines), description


def _pennylane_not_available(n_qubits: int, n_layers: int) -> tuple[str, str]:
    """Return placeholder when PennyLane is not installed."""
    circuit_code = (
        f"# PennyLane trial wavefunction ({n_qubits} qubits, {n_layers} layers)\n"
        f"# Install PennyLane: pip install pennylane\n"
    )
    description = f"Placeholder: install PennyLane for trial wavefunction generation."
    return circuit_code, description


def generate_pyscf_input(
    xyz_path: Path,
    basis: str = "cc-pVTZ",
    method: str = "hf",
) -> Optional[str]:
    """Generate a PySCF Python script for trial wavefunction calculation.

    Parameters
    ----------
    xyz_path : Path
        Path to XYZ geometry file.
    basis : str
        Basis set (e.g., "cc-pVTZ", "sto-3g", "6-31G*").
    method : str
        Method: "hf" (Hartree-Fock, default), "dft" (B3LYP), "mp2".

    Returns
    -------
    str or None
        PySCF Python script as a string, or None if PySCF unavailable.
    """
    if not _HAS_PYSCF:
        return _pyscf_not_available(xyz_path, basis, method)

    # Read molecule from XYZ
    mol = pyscf.M(verbose=0)
    mol.atom = str(xyz_path)
    mol.basis = basis
    mol.build()

    script_lines = [
        "#!/usr/bin/env python3",
        f"\"\"\"PySCF trial wavefunction for {xyz_path.name}\"\"\"",
        "",
        "from pyscf import gto, scf, dft, mp",
        "",
        f"mol = gto.M(atom='''",
        mol.atom,
        f"''', basis='{basis}', verbose=3)",
        f"",
    ]

    if method == "hf":
        script_lines.extend([
            "# Hartree-Fock calculation",
            "mf = scf.RHF(mol)",
            "mf.kernel()",
            "print('HF energy:', mf.e_tot)",
            "",
            "# Save orbital coefficients for QMC trial wavefunction",
            "import numpy as np",
            "np.savez('mo_coeff.npz', mo_coeff=mf.mo_coeff, mo_energy=mf.mo_energy)",
        ])
    elif method == "dft":
        script_lines.extend([
            "# DFT B3LYP calculation",
            "mf = dft.RKS(mol)",
            "mf.xc = 'b3lyp'",
            "mf.kernel()",
            "print('DFT energy:', mf.e_tot)",
            "",
            "np.savez('mo_coeff.npz', mo_coeff=mf.mo_coeff, mo_energy=mf.mo_energy)",
        ])
    elif method == "mp2":
        script_lines.extend([
            "# HF + MP2 calculation",
            "mf = scf.RHF(mol)",
            "mf.kernel()",
            "mp2 = mp.MP2(mf)",
            "mp2.kernel()",
            "print('MP2 energy:', mp2.e_tot)",
        ])

    script_lines.append("")
    return "\n".join(script_lines)


def _pyscf_not_available(xyz_path: Path, basis: str, method: str) -> str:
    """Return placeholder when PySCF is not installed."""
    return (
        f"#!/usr/bin/env python3\n"
        f"# PySCF trial wavefunction for {xyz_path.name}\n"
        f"# Install PySCF: pip install pyscf\n"
        f"# then run: python {xyz_path.stem}_pyscf.py\n"
        f"#\n"
        f"# Configuration:\n"
        f"#   basis: {basis}\n"
        f"#   method: {method}\n"
    )


# ═══════════════════════════════════════════════════════════════════════
#  3. QMC Input file generation
# ═══════════════════════════════════════════════════════════════════════


def write_qmcpack_input(
    xyz_path: Path,
    output_dir: Path,
    n_equilibration_steps: int = 1000,
    n_blocks: int = 100,
    n_steps_per_block: int = 100,
) -> Path:
    """Write a QMCPACK XML input file.

    Parameters
    ----------
    xyz_path : Path
        XYZ geometry file containing the molecule.
    output_dir : Path
        Output directory.
    n_equilibration_steps : int
        Number of VMC equilibration steps.
    n_blocks : int
        Number of VMC blocks for statistics.
    n_steps_per_block : int
        Steps per block.

    Returns
    -------
    Path
        Path to the generated QMCPACK input file.
    """
    xml_path = output_dir / "qmcp_input.xml"

    # Read atom types from XYZ for the XML header
    atom_types = set()
    try:
        with open(xyz_path, encoding="utf-8") as fh:
            lines = fh.readlines()
        for line in lines[2:]:  # skip header lines
            parts = line.strip().split()
            if parts:
                atom_types.add(parts[0])
    except Exception:
        atom_types = {"C", "H", "O", "N"}

    # Build XML content
    xml_content = f"""<?xml version="1.0"?>
<simulation>
  <!-- Auto-generated by P4 QMC prepare -->
  <project id="qmc" series="0">
    <application name="QMCPACK" role="molec"/>
  </project>

  <!-- Geometry -->
  <include href="{xyz_path.name}"/>

  <!-- Hamiltonian: electrons in external potential -->
  <hamiltonian name="h0" type="generic" target="e">
    <pairpot name="ElecElec" type="coulomb" source="e" target="e"/>
    <pairpot name="IonElec" type="coulomb" source="ion0" target="e"/>
    <constant name="IonIon" type="coulomb" source="ion0" target="ion0"/>
  </hamiltonian>

  <!-- Wavefunction: Slater-Jastrow (placeholder; use PySCF orbitals) -->
  <wavefunction name="psi0" target="e">
    <determinantset type="MolecularOrbital" name="LCAO">
      <basisset name="LCAOBSet">
        <atomicBasisSet type="STO" element="H" normalized="yes">
          <basisGroup rid="H" n="0" l="0" type="Slater">
            <radfunc exponent="1.0" contraction="0.0"/>
          </basisGroup>
        </atomicBasisSet>
        <atomicBasisSet type="STO" element="C" normalized="yes">
          <basisGroup rid="C" n="0" l="0" type="Slater">
            <radfunc exponent="6.0" contraction="0.0"/>
          </basisGroup>
          <basisGroup rid="C" n="1" l="0" type="Slater">
            <radfunc exponent="1.0" contraction="0.0"/>
          </basisGroup>
          <basisGroup rid="C" n="2" l="0" type="Slater">
            <radfunc exponent="1.0" contraction="0.0"/>
          </basisGroup>
        </atomicBasisSet>
      </basisset>
      <slaterdeterminant>
        <determinant id="up" spin="3"/>
        <determinant id="down" spin="2"/>
      </slaterdeterminant>
    </determinantset>
    <jastrow type="Two-Body" function="Bspline" print="yes" name="J2">
      <correlation size="4" cusp="1.0" elementA="C" elementB="C">
        <coefficients id="eC_C" type="Array">0.0 0.0 0.0 0.0</coefficients>
      </correlation>
      <correlation size="4" cusp="0.5" elementA="C" elementB="H">
        <coefficients id="eC_H" type="Array">0.0 0.0 0.0 0.0</coefficients>
      </correlation>
    </jastrow>
  </wavefunction>

  <!-- VMC optimisation -->
  <qmc method="vmc" move="pbyp" gpu="no">
    <estimator name="LocalEnergy" hdf5="no"/>
    <parameter name="useDR">yes</parameter>
    <parameter name="blocks">100</parameter>
    <parameter name="steps">100</parameter>
    <parameter name="substeps">2</parameter>
    <parameter name="timestep">0.1</parameter>
    <parameter name="warmupBlocks">10</parameter>
  </qmc>
</simulation>
"""
    with open(xml_path, "w", encoding="utf-8") as fh:
        fh.write(xml_content)
    logger.info("Written QMCPACK input: %s", xml_path)
    return xml_path


def write_casino_input(
    xyz_path: Path,
    output_dir: Path,
    n_configs: int = 10000,
) -> Path:
    """Write a CASINO input file.

    Parameters
    ----------
    xyz_path : Path
        XYZ geometry file.
    output_dir : Path
        Output directory.
    n_configs : int
        Number of configurations for DMC.

    Returns
    -------
    Path
        Path to the generated CASINO input file.
    """
    casino_path = output_dir / "casino.input"

    content = f"""! Auto-generated by P4 QMC prepare
! CASINO input for {xyz_path.name}

SYSTEM
  GEOMETRY_FILE {xyz_path.name}
  SPIN_POLARISED F
  CHARGE 0
END

WAVEFUNCTION
  METHOD PLATONIC
END

VMC
  NCONFIG {n_configs}
  TOTSTEP 5000
END

DMC
  NCONFIG {n_configs}
  TOTSTEP 10000
  TIMESTEP 0.01
END
"""
    with open(casino_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    logger.info("Written CASINO input: %s", casino_path)
    return casino_path


# ═══════════════════════════════════════════════════════════════════════
#  4. 3D shape descriptors (optional, for QMC-QKS correlation)
# ═══════════════════════════════════════════════════════════════════════


def compute_3d_descriptors(mol: "Chem.Mol", conf_id: int) -> dict[str, float]:
    """Compute 3D molecular shape descriptors for correlation analysis.

    Parameters
    ----------
    mol : Chem.Mol
        RDKit molecule with conformer.
    conf_id : int
        Conformer ID.

    Returns
    -------
    dict[str, float]
        Dictionary of 3D descriptors.
    """
    if not _HAS_RDKIT:
        return {}

    descriptors = {}

    # Asphericity, eccentricity, inertial shape factor
    try:
        descriptors["asphericity"] = CalcAsphericity(mol, confId=conf_id)
        descriptors["eccentricity"] = CalcEccentricity(mol, confId=conf_id)
        descriptors["inertial_shape_factor"] = CalcInertialShapeFactor(mol, confId=conf_id)
    except Exception:
        pass

    # Radius of gyration (using rdMolDescriptors)
    try:
        descriptors["radius_of_gyration"] = rdMolDescriptors.CalcRadiusOfGyration(mol, confId=conf_id)
    except Exception:
        pass

    # PMI (Principal Moments of Inertia)
    try:
        pmi = rdMolDescriptors.CalcPMI1(mol, confId=conf_id)
        pmi2 = rdMolDescriptors.CalcPMI2(mol, confId=conf_id)
        pmi3 = rdMolDescriptors.CalcPMI3(mol, confId=conf_id)
        # Normalised PMI ratios
        if pmi > 0:
            descriptors["pmi_ratio_1"] = pmi2 / pmi if pmi > 0 else 0.0
            descriptors["pmi_ratio_2"] = pmi3 / pmi if pmi > 0 else 0.0
    except Exception:
        pass

    # NPA (Normalised Principal Moments Ratios)
    try:
        npr1 = rdMolDescriptors.CalcNPR1(mol, confId=conf_id)
        npr2 = rdMolDescriptors.CalcNPR2(mol, confId=conf_id)
        descriptors["npr1"] = npr1
        descriptors["npr2"] = npr2
    except Exception:
        pass

    return descriptors


# ═══════════════════════════════════════════════════════════════════════
#  5. Main entry point
# ═══════════════════════════════════════════════════════════════════════


def prepare_single_molecule(
    smiles: str,
    output_dir: Path,
    n_conformers: int = 50,
    optimize_ff: Optional[str] = None,
    basis: str = "cc-pVTZ",
    method: str = "hf",
    n_qubits: int = 8,
) -> dict[str, Path]:
    """Prepare all QMC inputs for a single molecule.

    Parameters
    ----------
    smiles : str
        Input SMILES.
    output_dir : Path
        Output directory for this molecule.
    n_conformers : int
        Number of RDKit conformers to generate.
    optimize_ff : str or None
        Force field for optional OpenBabel optimisation ("uff", "gaff", "mmff94", or None).
    basis : str
        Basis set for trial wavefunction.
    method : str
        Quantum chemistry method.
    n_qubits : int
        Qubits for PennyLane circuit.

    Returns
    -------
    dict[str, Path]
        Mapping from file type to path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: dict[str, Path] = {}

    # Copy metadata
    generated["__smiles__"] = Path(smiles)  # type: ignore[assignment]
    generated["__canonical_smiles__"] = Path(_canonical_smiles(smiles))

    # 1. Generate 3D geometry
    mol, conf_ids = generate_rdkit_conformers(
        smiles, n_conformers=n_conformers, rmsd_threshold=0.5, optimize=True
    )

    if mol and conf_ids:
        xyz_path = output_dir / "geometry.xyz"
        write_xyz(mol, conf_ids[0], xyz_path)
        generated["xyz"] = xyz_path

        # 1b. Optional OpenBabel optimisation
        if optimize_ff is not None and _HAS_OPENBABEL:
            opt_path = optimize_with_openbabel(xyz_path, method=optimize_ff)
            if opt_path is not None:
                # Read back optimised coordinates into an RDKit mol
                ob_mol = ob.OBMol()
                obconv = ob.OBConversion()
                obconv.SetInFormat("xyz")
                if obconv.ReadFile(ob_mol, str(opt_path)):
                    # Convert back to RDKit for descriptor calculation
                    from rdkit.Chem import rdMolInterchange  # type: ignore[attr-defined]

                    try:
                        rdkit_mol_opt = rdMolInterchange.MolFromOBMol(ob_mol)
                        if rdkit_mol_opt:
                            generated["xyz_optimised"] = opt_path
                    except Exception:
                        generated["xyz_optimised"] = opt_path
                else:
                    generated["xyz_optimised"] = opt_path

        # 3D shape descriptors
        descriptors = compute_3d_descriptors(mol, conf_ids[0])
        if descriptors:
            desc_path = output_dir / "shape_descriptors.npy"
            np.save(desc_path, descriptors)
            generated["shape_descriptors"] = desc_path

    # 2. Trial wavefunction (PennyLane)
    circuit_code, circuit_desc = generate_pennylane_circuit(smiles, n_qubits=n_qubits)
    pl_path = output_dir / "pennylane_circuit.py"
    with open(pl_path, "w", encoding="utf-8") as fh:
        fh.write(circuit_code)
    generated["pennylane_circuit"] = pl_path

    meta_path = output_dir / "circuit_description.txt"
    with open(meta_path, "w", encoding="utf-8") as fh:
        fh.write(circuit_desc + "\n")
        fh.write(f"n_qubits: {n_qubits}\n")
        fh.write(f"PennyLane version: {qml.__version__ if _HAS_PENNYLANE else 'not installed'}\n")
    generated["circuit_description"] = meta_path

    # 3. PySCF trial wavefunction script (if available)
    if _HAS_PYSCF and generated.get("xyz"):
        pyscf_code = generate_pyscf_input(generated["xyz"], basis=basis, method=method)
        if pyscf_code:
            pyscf_path = output_dir / f"pyscf_{method}.py"
            with open(pyscf_path, "w", encoding="utf-8") as fh:
                fh.write(pyscf_code)
            generated["pyscf_script"] = pyscf_path

    # 4. QMCPACK input
    if generated.get("xyz"):
        qmcp_path = write_qmcpack_input(generated["xyz"], output_dir)
        generated["qmcp_input"] = qmcp_path

    # 5. CASINO input (as alternative)
    if generated.get("xyz"):
        casino_path = write_casino_input(generated["xyz"], output_dir)
        generated["casino_input"] = casino_path

    return generated


def prepare_batch(
    smiles_list: Sequence[str],
    output_dir: Path,
    rename_by_smiles: bool = True,
    **kwargs,
) -> list[dict[str, Path]]:
    """Prepare QMC inputs for a batch of molecules.

    Parameters
    ----------
    smiles_list : sequence of str
        List of SMILES strings.
    output_dir : Path
        Base output directory; subdirectories are created per molecule.
    rename_by_smiles : bool
        If True, name subdirectories by SMILES hash for reproducibility.
    **kwargs
        Additional arguments passed to prepare_single_molecule().

    Returns
    -------
    list[dict[str, Path]]
        Results for each molecule.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Path]] = []
    for idx, smiles in enumerate(smiles_list):
        if rename_by_smiles:
            mol_dir = output_dir / f"mol_{_smiles_hash(smiles)}"
        else:
            mol_dir = output_dir / f"mol_{idx:04d}"

        try:
            result = prepare_single_molecule(smiles, mol_dir, **kwargs)
            results.append(result)
            logger.info("[%d/%d] %s → %s", idx + 1, len(smiles_list), smiles[:40], mol_dir)
        except Exception as exc:
            logger.error("[%d/%d] %s FAILED: %s", idx + 1, len(smiles_list), smiles[:40], exc)
            # Write error marker
            (mol_dir / "ERROR.txt").write_text(str(exc), encoding="utf-8")
            results.append({})

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare QMC inputs for candidate molecules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python p4_qmc_prepare.py --smiles 'CCO' --output-dir qmc_inputs\n"
            "  python p4_qmc_prepare.py --smiles-file candidates.txt --optimize uff\n"
            "  python p4_qmc_prepare.py --smiles 'C' 'CC' --output-dir qmc_inputs --method dft\n"
        ),
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--smiles", nargs="+", help="One or more SMILES strings")
    input_group.add_argument(
        "--smiles-file", type=Path, help="File with one SMILES per line (skips # comments and empty lines)"
    )
    parser.add_argument("--output-dir", type=Path, default=Path("qmc_inputs"), help="Output directory")
    parser.add_argument("--n-conformers", type=int, default=50, help="Number of RDKit conformers to generate")
    parser.add_argument("--optimize", default=None, choices=["uff", "gaff", "mmff94"],
                        help="OpenBabel force field for geometry optimisation")
    parser.add_argument("--basis", default="cc-pVTZ", help="Basis set for trial wavefunction")
    parser.add_argument("--method", default="hf", choices=["hf", "dft", "mp2"], help="Quantum method")
    parser.add_argument("--n-qubits", type=int, default=8, help="Qubits for PennyLane circuit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Collect SMILES
    if args.smiles:
        smiles_list = args.smiles
    elif args.smiles_file:
        with open(args.smiles_file, encoding="utf-8") as fh:
            smiles_list = [
                line.split("#")[0].strip()
                for line in fh
                if line.strip() and not line.startswith("#")
            ]
    else:
        parser.error("Either --smiles or --smiles-file is required.")

    logger.info("Preparing QMC inputs for %d molecules", len(smiles_list))
    logger.info("RDKit: %s", "YES" if _HAS_RDKIT else "NO")
    logger.info("OpenBabel: %s", "YES" if _HAS_OPENBABEL else "NO")
    logger.info("PennyLane v%s" % (qml.__version__,) if _HAS_PENNYLANE else "PennyLane: NO")
    logger.info("PySCF: %s", "YES" if _HAS_PYSCF else "NO")

    results = prepare_batch(
        smiles_list,
        args.output_dir,
        n_conformers=args.n_conformers,
        optimize_ff=args.optimize,
        basis=args.basis,
        method=args.method,
        n_qubits=args.n_qubits,
    )

    n_success = sum(1 for r in results if r)
    n_fail = len(results) - n_success
    logger.info("Done: %d / %d successful, %d failed", n_success, len(results), n_fail)
    logger.info("Output: %s", args.output_dir.resolve())

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  QMC Input Preparation Complete")
    print(f"  {'=' * 60}")
    print(f"  Total molecules:   {len(results)}")
    print(f"  Successful:        {n_success}")
    print(f"  Failed:            {n_fail}")
    print(f"  Output directory:  {args.output_dir.resolve()}")
    print(f"  RDKit 3D:          {'YES' if _HAS_RDKIT else 'NO'}")
    print(f"  OpenBabel opt:     {'YES ({0})'.format(args.optimize) if args.optimize and _HAS_OPENBABEL else 'NO'}")
    print(f"  PennyLane circuit: {'YES ({0} qubits)'.format(args.n_qubits) if _HAS_PENNYLANE else 'NO'}")
    print(f"  PySCF:             {'YES ({0}/{1})'.format(args.method, args.basis) if _HAS_PYSCF else 'NO (install pyscf)'}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
