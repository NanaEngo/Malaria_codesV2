#!/usr/bin/env python3
"""P4 — Analyze Quantum Monte Carlo (QMC) outputs and correlate with descriptors.

This script parses QMC total energies from QMCPACK/CASINO output files and
correlates them with P3 quantum-inspired descriptors (QKS, TDA, TNE).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import numpy as np


def parse_qmc_energy(output_file: Path) -> float | None:
    """Extract the final QMC energy from a package output file.

    Parameters
    ----------
    output_file : Path
        Path to QMCPACK/CASINO output.

    Returns
    -------
    float | None
        Final QMC energy in Hartree, or None if parsing fails.
    """
    # TODO: implement real parser for QMCPACK/CASINO output formats
    text = output_file.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "Final QMC Energy" in line:
            try:
                return float(line.split()[-2])
            except (ValueError, IndexError):
                return None
    return None


def correlate_with_descriptors(
    energies: Sequence[float | None],
    descriptors: Sequence[Sequence[float]],
) -> dict[str, float]:
    """Compute Pearson correlation between QMC energies and descriptors.

    Parameters
    ----------
    energies : sequence of float | None
        QMC energies; None values are skipped.
    descriptors : sequence of sequence of float
        Descriptor vectors (e.g., QKS/TDA/TNE features).

    Returns
    -------
    dict[str, float]
        Correlation coefficients per descriptor dimension.
    """
    valid = [(e, d) for e, d in zip(energies, descriptors) if e is not None]
    if not valid:
        return {}
    e_arr = np.array([e for e, _ in valid])
    d_arr = np.array([d for _, d in valid])
    correlations = {}
    for i in range(d_arr.shape[1]):
        if d_arr[:, i].std() > 0:
            correlations[f"descriptor_{i}"] = float(np.corrcoef(e_arr, d_arr[:, i])[0, 1])
    return correlations


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze QMC outputs.")
    parser.add_argument("--qmc-outputs", nargs="+", type=Path, required=True, help="QMC output files")
    parser.add_argument("--descriptors", type=Path, help="CSV/TSV of descriptor values")
    args = parser.parse_args()

    energies = [parse_qmc_energy(out) for out in args.qmc_outputs]
    print("Parsed QMC energies:", energies)

    if args.descriptors:
        # TODO: load real descriptors from CSV/TSV instead of using random
        # placeholders. The random data below is only for skeleton validation.
        descriptors = np.random.randn(len(energies), 3).tolist()
        correlations = correlate_with_descriptors(energies, descriptors)
        print("Correlations with descriptors:", correlations)


if __name__ == "__main__":
    main()
