#!/usr/bin/env python3
"""P4 — Prepare molecular inputs for Quantum Monte Carlo (QMC) validation.

This script converts a small set of candidate SMILES into the geometry and
trial wavefunction inputs required by QMC packages such as QMCPACK or CASINO.
All external dependencies are optional; the script runs as a skeleton.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence


def prepare_qmc_inputs(
    smiles_list: Sequence[str],
    output_dir: Path,
    method: str = "dft",
    basis: str = "cc-pVTZ",
) -> list[Path]:
    """Generate QMC input files for a list of candidate molecules.

    Parameters
    ----------
    smiles_list : sequence of str
        Candidate SMILES strings.
    output_dir : Path
        Directory where inputs will be written.
    method : str
        Method used to generate trial wavefunction (e.g., "dft", "hf").
    basis : str
        Basis set for the trial wavefunction.

    Returns
    -------
    list[Path]
        Paths to the generated input directories.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    for idx, smiles in enumerate(smiles_list):
        mol_dir = output_dir / f"qmc_input_{idx:03d}"
        mol_dir.mkdir(parents=True, exist_ok=True)

        # TODO: use RDKit + PySCF/ORCA to generate coordinates and orbitals
        (mol_dir / "geometry.xyz").write_text(f"{smiles}\n0 0 0\n", encoding="utf-8")
        (mol_dir / "trial_wfn.inp").write_text(
            f"# Trial wavefunction for {smiles}\n"
            f"method={method}\nbasis={basis}\n",
            encoding="utf-8",
        )
        generated.append(mol_dir)

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare QMC inputs from SMILES.")
    parser.add_argument("--smiles", nargs="+", default=["CCO"], help="Candidate SMILES")
    parser.add_argument("--output-dir", type=Path, default=Path("qmc_inputs"), help="Output directory")
    parser.add_argument("--method", default="dft", help="Trial wavefunction method")
    parser.add_argument("--basis", default="cc-pVTZ", help="Basis set")
    args = parser.parse_args()

    dirs = prepare_qmc_inputs(args.smiles, args.output_dir, args.method, args.basis)
    print(f"Prepared {len(dirs)} QMC input directories in {args.output_dir}")


if __name__ == "__main__":
    main()
