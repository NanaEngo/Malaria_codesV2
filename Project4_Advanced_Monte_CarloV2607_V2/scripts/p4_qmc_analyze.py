#!/usr/bin/env python3
"""P4 — Analyze Quantum Monte Carlo (QMC) outputs and correlate with descriptors.

This script parses QMC total energies from QMCPACK, CASINO, and PennyLane
output files and correlates them with P3 quantum-inspired descriptors
(QKS, TDA persistence, TNE embeddings).

Features
--------
- Parse QMCPACK .scalar.dat and .stat.h5 output files
- Parse CASINO output files
- Compute PennyLane VQE energies (when PennyLane is available)
- Spearman/Pearson correlation with P3 descriptors
- Permutation test for statistical significance
- Generate publication-quality correlation plots
- HTML report generation

Usage
-----
python p4_qmc_analyze.py --qmc-dir qmc_inputs/mol_* --descriptors p3_descriptors.csv
python p4_qmc_analyze.py --qmc-dir qmc_inputs/ --pennylane --output report.html
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np

logger = logging.getLogger("p4_qmc_analyze")

# ── Optional dependencies ────────────────────────────────────────────
_HAS_PENNYLANE = False
_HAS_MATPLOTLIB = False
_HAS_SEABORN = False
_HAS_SCIPY = False

try:
    import pennylane as qml

    _HAS_PENNYLANE = True
except ImportError:
    pass

try:
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use("Agg")
    _HAS_MATPLOTLIB = True
except ImportError:
    pass

try:
    import seaborn as sns

    _HAS_SEABORN = True
except ImportError:
    pass

try:
    from scipy import stats as scipy_stats

    _HAS_SCIPY = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════
#  1. QMC output parsers
# ═══════════════════════════════════════════════════════════════════════


def parse_qmcpack_energy(output_file: Path) -> Optional[float]:
    """Extract the final QMC total energy from a QMCPACK output file.

    Supports .scalar.dat format and plain .out files.

    Parameters
    ----------
    output_file : Path
        Path to QMCPACK output (.scalar.dat or .out).

    Returns
    -------
    float or None
        Final total energy in Hartree, or None if parsing fails.
    """
    if not output_file.exists():
        return None

    text = output_file.read_text(encoding="utf-8", errors="replace")

    # .scalar.dat format (columnar data)
    if ".scalar" in output_file.suffix:
        try:
            # Format: step  LocalEnergy  LocalEnergy_sigma  ...
            lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
            if len(lines) >= 2:
                # Header line gives column names; data lines start from line 1+?
                for line in reversed(lines):
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            energy = float(parts[1])
                            if -1000 < energy < 0:  # sensible energy range for org. molecules
                                return energy
                        except ValueError:
                            continue
        except Exception:
            pass

    # Free-format .out files
    patterns = [
        r"Total\s+energy\s*=\s*([-+]?\d+\.\d+)",
        r"LocalEnergy\s*=\s*([-+]?\d+\.\d+)",
        r"E\s*=\s*([-+]?\d+\.\d+)",
        r"Final\s+QMC\s+[Ee]nergy\s*:\s*([-+]?\d+\.\d+)",
    ]
    for line in text.splitlines():
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    energy = float(match.group(1))
                    if -1000 < energy < 0:
                        return energy
                except ValueError:
                    continue

    return None


def parse_casino_energy(output_file: Path) -> Optional[float]:
    """Extract the final DMC energy from a CASINO output file.

    Parameters
    ----------
    output_file : Path
        Path to CASINO output file.

    Returns
    -------
    float or None
        Final DMC energy in Hartree, or None if parsing fails.
    """
    if not output_file.exists():
        return None

    text = output_file.read_text(encoding="utf-8", errors="replace")

    patterns = [
        r"DMC\s+energy\s*=\s*([-+]?\d+\.\d+)",
        r"Total\s+[Ee]nergy\s*=\s*([-+]?\d+\.\d+)",
        r"E_DMC\s*=\s*([-+]?\d+\.\d+)",
    ]

    for line in text.splitlines():
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    energy = float(match.group(1))
                    if -1000 < energy < 0:
                        return energy
                except ValueError:
                    continue

    return None


def compute_pennylane_energy(
    smiles: str,
    n_qubits: int = 8,
    n_layers: int = 2,
    n_shots: int = 10000,
) -> Optional[float]:
    """Compute a VQE energy estimate using PennyLane.

    This serves as a lightweight QMC proxy when full QMCPACK/CASINO are
    not available. Uses a Transverse Ising Hamiltonian as a surrogate.

    Parameters
    ----------
    smiles : str
        Input SMILES (hashed to seed the variational parameters).
    n_qubits : int
        Number of qubits.
    n_layers : int
        Number of variational layers.
    n_shots : int
        Number of measurement shots.

    Returns
    -------
    float or None
        Estimated ground-state energy (arbitrary units), or None on failure.
    """
    if not _HAS_PENNYLANE:
        return None

    try:
        # Seed parameters from SMILES hash
        seed = int(hashlib.sha256(smiles.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        params = rng.uniform(-np.pi, np.pi, size=(n_layers, n_qubits))

        # Build device and Hamiltonian
        dev = qml.device("default.qubit", wires=n_qubits, shots=n_shots)

        # Hamiltonian: Transverse Ising model
        coeffs = [1.0] * (n_qubits - 1) + [0.5] * n_qubits
        obs = (
            [qml.Z(i) @ qml.Z(i + 1) for i in range(n_qubits - 1)]
            + [qml.X(i) for i in range(n_qubits)]
        )
        H = qml.Hamiltonian(coeffs, obs)

        @qml.qnode(dev)
        def energy_circuit(params):
            qml.IQPEmbedding(
                features=rng.uniform(-1, 1, size=n_qubits),
                wires=range(n_qubits),
                n_repeats=2,
            )
            qml.BasicEntanglerLayers(
                theta=params,
                wires=range(n_qubits),
                rotation=qml.RY,
            )
            return qml.expval(H)

        energy = energy_circuit(params)
        return float(energy)

    except Exception as exc:
        logger.debug("PennyLane energy computation failed: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════════════════
#  2. Correlation analysis
# ═══════════════════════════════════════════════════════════════════════


def correlation_analysis(
    energies: Sequence[float],
    descriptors: np.ndarray,
    descriptor_names: Optional[list[str]] = None,
    n_permutations: int = 100000,
) -> dict[str, Any]:
    """Compute correlations between QMC energies and descriptor dimensions.

    Parameters
    ----------
    energies : sequence of float
        QMC/VQE energies (one per molecule).
    descriptors : np.ndarray
        Descriptor matrix, shape (n_molecules, n_features).
    descriptor_names : list of str or None
        Optional names for descriptor dimensions.
    n_permutations : int
        Number of permutations for significance testing.

    Returns
    -------
    dict
        Correlation results including Pearson/Spearman coefficients, p-values,
        and permutation test results.
    """
    if not _HAS_SCIPY:
        return {"error": "scipy not available"}

    energies = np.asarray(energies, dtype=float)
    descriptors = np.asarray(descriptors, dtype=float)

    if energies.ndim != 1 or descriptors.ndim != 2:
        return {"error": "Invalid input shapes"}

    n_molecules = len(energies)
    if n_molecules < 3:
        return {"error": f"Need >= 3 molecules, got {n_molecules}"}

    if descriptor_names is None:
        descriptor_names = [f"descriptor_{i}" for i in range(descriptors.shape[1])]

    results: dict[str, Any] = {
        "n_molecules": n_molecules,
        "n_descriptors": descriptors.shape[1],
        "correlations": [],
    }

    for i in range(descriptors.shape[1]):
        d = descriptors[:, i]

        # Skip constant descriptors
        if np.std(d) < 1e-10:
            continue

        # Pearson
        pearson_r, pearson_p = scipy_stats.pearsonr(energies, d)

        # Spearman
        spearman_rho, spearman_p = scipy_stats.spearmanr(energies, d)

        # Permutation test for Pearson
        n_greater = 0
        observed = abs(pearson_r)
        combined = np.column_stack([energies, d])
        for _ in range(min(n_permutations, 10000)):  # cap for speed
            perm = combined.copy()
            np.random.shuffle(perm[:, 0])
            perm_r, _ = scipy_stats.pearsonr(perm[:, 0], perm[:, 1])
            if abs(perm_r) >= observed:
                n_greater += 1
        perm_p = (n_greater + 1) / (min(n_permutations, 10000) + 1)

        results["correlations"].append({
            "descriptor": descriptor_names[i],
            "pearson_r": float(pearson_r),
            "pearson_p": float(pearson_p),
            "spearman_rho": float(spearman_rho),
            "spearman_p": float(spearman_p),
            "permutation_p": float(perm_p),
            "n_permutations": min(n_permutations, 10000),
        })

    # Sort by absolute Pearson coefficient
    results["correlations"].sort(key=lambda x: abs(x["pearson_r"]), reverse=True)

    return results


# ═══════════════════════════════════════════════════════════════════════
#  3. Plotting
# ═══════════════════════════════════════════════════════════════════════


def plot_correlation_matrix(
    results: dict[str, Any],
    output_path: Path,
) -> Optional[Path]:
    """Generate a correlation matrix heatmap between QMC energies and descriptors.

    Parameters
    ----------
    results : dict
        Output from correlation_analysis().
    output_path : Path
        Output PNG path.

    Returns
    -------
    Path or None
        Path to generated plot, or None if matplotlib unavailable.
    """
    if not _HAS_MATPLOTLIB:
        return None

    correlations = results.get("correlations", [])
    if not correlations:
        return None

    # Build matrix
    names = [c["descriptor"] for c in correlations]
    pearson_vals = [c["pearson_r"] for c in correlations]
    spearman_vals = [c["spearman_rho"] for c in correlations]
    p_vals = [c["pearson_p"] for c in correlations]

    fig, axes = plt.subplots(1, 2, figsize=(14, max(6, len(names) * 0.4)))

    # Pearson
    colors_p = ["#d73027" if v < 0 else "#4575b4" for v in pearson_vals]
    alpha_p = [max(0.2, 1.0 - p) for p in p_vals]
    axes[0].barh(names, pearson_vals, color=colors_p, alpha=alpha_p, edgecolor="gray")
    axes[0].axvline(0, color="black", linewidth=0.5)
    axes[0].set_xlabel("Pearson r")
    axes[0].set_title("QMC Energy ~ Descriptor Correlation (Pearson)")

    # Add significance annotations
    for i, (r_val, p_val) in enumerate(zip(pearson_vals, p_vals)):
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
        axes[0].text(r_val + 0.02 if r_val >= 0 else r_val - 0.12, i, sig,
                     va="center", fontsize=8, color="gray")

    # Spearman
    colors_s = ["#d73027" if v < 0 else "#4575b4" for v in spearman_vals]
    axes[1].barh(names, spearman_vals, color=colors_s, alpha=0.8, edgecolor="gray")
    axes[1].axvline(0, color="black", linewidth=0.5)
    axes[1].set_xlabel("Spearman ρ")
    axes[1].set_title("QMC Energy ~ Descriptor Correlation (Spearman)")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Correlation plot saved: %s", output_path)
    return output_path


def plot_energy_landscape(
    energies: Sequence[float],
    molecule_labels: Sequence[str],
    output_path: Path,
    descriptor_values: Optional[Sequence[float]] = None,
    descriptor_name: str = "",
) -> Optional[Path]:
    """Plot the QMC energy landscape across molecules.

    Parameters
    ----------
    energies : sequence of float
        QMC energies.
    molecule_labels : sequence of str
        Labels for each molecule (truncated SMILES).
    output_path : Path
        Output PNG path.
    descriptor_values : sequence of float, optional
        Overlay descriptor values as a color map.
    descriptor_name : str
        Name of the descriptor for the colorbar label.

    Returns
    -------
    Path or None
        Path to generated plot.
    """
    if not _HAS_MATPLOTLIB:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(energies))
    if descriptor_values is not None:
        sc = ax.scatter(x, energies, c=descriptor_values, cmap="viridis",
                        s=80, edgecolor="black", linewidth=0.5, zorder=3)
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label(descriptor_name, rotation=270, labelpad=15)
    else:
        ax.scatter(x, energies, color="#4575b4", s=60, zorder=3)

    ax.plot(x, energies, "k-", alpha=0.3, zorder=1)

    # Labels
    if len(molecule_labels) <= 20:
        ax.set_xticks(x)
        ax.set_xticklabels([s[:12] + "..." if len(s) > 12 else s for s in molecule_labels],
                           rotation=45, ha="right", fontsize=8)
    else:
        ax.set_xlabel("Molecule index")

    ax.set_ylabel("QMC Energy (Hartree / a.u.)")
    ax.set_title("QMC Energy Landscape")
    ax.axhline(np.mean(energies), color="red", linestyle="--", alpha=0.5, label=f"Mean: {np.mean(energies):.4f}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def generate_html_report(
    results: dict[str, Any],
    energies: list[Optional[float]],
    smiles_list: list[str],
    plot_paths: dict[str, Path],
    output_path: Path,
) -> Path:
    """Generate a standalone HTML report of the QMC analysis.

    Parameters
    ----------
    results : dict
        Correlation analysis results.
    energies : list of float or None
        QMC energies per molecule.
    smiles_list : list of str
        Original SMILES strings.
    plot_paths : dict
        Mapping from plot name to Path.
    output_path : Path
        Output HTML file path.

    Returns
    -------
    Path
        Path to generated HTML report.
    """
    n_valid = sum(1 for e in energies if e is not None)
    correlations = results.get("correlations", [])

    # Build HTML
    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="UTF-8">',
        "<title>P4 — QMC Analysis Report</title>",
        "<style>",
        "body { font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 960px; margin: 2em auto; padding: 0 1em; }",
        "h1 { color: #1a1a2e; border-bottom: 2px solid #4575b4; }",
        "h2 { color: #4575b4; margin-top: 2em; }",
        "table { border-collapse: collapse; width: 100%; margin: 1em 0; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "th { background-color: #4575b4; color: white; }",
        "tr:nth-child(even) { background-color: #f5f5f5; }",
        ".sig-*** { font-weight: bold; color: #d73027; }",
        ".sig-** { color: #fc8d59; }",
        ".sig-* { color: #fdcc8a; }",
        ".sig-ns { color: #999; }",
        "img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin: 1em 0; }",
        ".summary { background: #f0f7ff; padding: 1em; border-radius: 4px; border-left: 4px solid #4575b4; }",
        "</style></head><body>",
        "<h1>P4 — Quantum Monte Carlo Analysis Report</h1>",
        f'<div class="summary">',
        f"<p><strong>Molecules analyzed:</strong> {len(smiles_list)}</p>",
        f"<p><strong>Valid QMC energies:</strong> {n_valid}/{len(smiles_list)}</p>",
        f"<p><strong>PennyLane available:</strong> {'YES' if _HAS_PENNYLANE else 'NO'}</p>",
        f"<p><strong>Correlation features:</strong> {len(correlations)}</p>",
        "</div>",
    ]

    # Energy table
    html_parts.append("<h2>QMC Energies</h2>")
    html_parts.append('<table><tr><th>#</th><th>SMILES</th><th>QMC Energy (Hartree)</th></tr>')
    for idx, (smiles, energy) in enumerate(zip(smiles_list, energies)):
        energy_str = f"{energy:.6f}" if energy is not None else "N/A"
        html_parts.append(f"<tr><td>{idx + 1}</td><td><code>{smiles}</code></td><td>{energy_str}</td></tr>")
    html_parts.append("</table>")

    # Correlation table
    if correlations:
        html_parts.append("<h2>Correlation Analysis</h2>")
        html_parts.append(
            '<table><tr><th>Descriptor</th><th>Pearson r</th><th>p-value</th><th>Spearman ρ</th><th>p-value</th><th>Perm. p</th><th>Signif.</th></tr>'
        )
        for c in correlations:
            sig = "***" if c.get("pearson_p", 1) < 0.001 else "**" if c.get("pearson_p", 1) < 0.01 else "*" if c.get("pearson_p", 1) < 0.05 else "ns"
            html_parts.append(
                f"<tr>"
                f"<td>{c['descriptor']}</td>"
                f"<td>{c['pearson_r']:.4f}</td>"
                f"<td>{c['pearson_p']:.4e}</td>"
                f"<td>{c['spearman_rho']:.4f}</td>"
                f"<td>{c['spearman_p']:.4e}</td>"
                f"<td>{c['permutation_p']:.4e}</td>"
                f'<td class="sig-{sig}">{sig}</td>'
                f"</tr>"
            )
        html_parts.append("</table>")

    # Plots
    if plot_paths.get("correlation_matrix") and plot_paths["correlation_matrix"].exists():
        html_parts.append("<h2>Correlation Matrix</h2>")
        html_parts.append(f'<img src="{plot_paths["correlation_matrix"].name}" alt="Correlation matrix"/>')

    if plot_paths.get("energy_landscape") and plot_paths["energy_landscape"].exists():
        html_parts.append("<h2>Energy Landscape</h2>")
        html_parts.append(f'<img src="{plot_paths["energy_landscape"].name}" alt="Energy landscape"/>')

    html_parts.append("</body></html>")

    output_path.write_text("\n".join(html_parts), encoding="utf-8")
    logger.info("HTML report written: %s", output_path)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
#  4. Main entry point
# ═══════════════════════════════════════════════════════════════════════


def analyze_qmc_directory(
    qmc_dir: Path,
    descriptors_csv: Optional[Path] = None,
    use_pennylane: bool = False,
    n_qubits: int = 8,
    n_layers: int = 2,
    output_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Run full QMC analysis on a directory of prepared QMC inputs.

    Parameters
    ----------
    qmc_dir : Path
        Directory containing molecule subdirectories (from p4_qmc_prepare.py).
    descriptors_csv : Path or None
        Path to CSV with P3 descriptor values.
    use_pennylane : bool
        If True, compute PennyLane energies as a QMC proxy.
    n_qubits : int
        Qubits for PennyLane circuit.
    n_layers : int
        Layers for PennyLane circuit.
    output_dir : Path or None
        Output directory for plots and reports.

    Returns
    -------
    dict
        Complete analysis results.
    """
    output_dir = Path(output_dir or qmc_dir / "analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover molecule directories
    mol_dirs = sorted(qmc_dir.glob("mol_*/")) if qmc_dir.is_dir() else [qmc_dir]
    if not mol_dirs or (len(mol_dirs) == 1 and not mol_dirs[0].is_dir()):
        # Try direct subdirectories
        mol_dirs = sorted([d for d in qmc_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])

    if not mol_dirs:
        logger.error("No molecule directories found in %s", qmc_dir)
        return {"error": "No molecule directories found"}

    # Extract SMILES and energies
    smiles_list: list[str] = []
    energies: list[Optional[float]] = []
    energy_sources: list[str] = []

    for mol_dir in mol_dirs:
        # Try to get SMILES from metadata
        meta_file = mol_dir / "circuit_description.txt"
        if meta_file.exists():
            # Extract SMILES from the directory structure or metadata
            pass

        # Read SMILES from the canonical name if possible
        mol_name = mol_dir.name.replace("mol_", "")

        # Parse QMCPACK output
        energy = None
        source = "none"

        qmcpack_out = mol_dir / "qmcp_input.xml"
        if qmcpack_out.exists():
            energy = parse_qmcpack_energy(qmcpack_out)
            if energy is not None:
                source = "qmcp"

        if energy is None:
            casino_out = mol_dir / "casino.input"
            if casino_out.exists():
                energy = parse_casino_energy(casino_out)
                if energy is not None:
                    source = "casino"

        # PennyLane proxy
        if energy is None and use_pennylane and _HAS_PENNYLANE:
            # Use directory name or placeholder
            pl_energy = compute_pennylane_energy(mol_name, n_qubits=n_qubits, n_layers=n_layers)
            if pl_energy is not None:
                energy = pl_energy
                source = "pennylane"

        # Store; if no energy found, None
        energies.append(energy)
        energy_sources.append(source)
        smiles_list.append(mol_name)

    # Load descriptors if provided
    descriptors = None
    descriptor_names = None
    if descriptors_csv and descriptors_csv.exists():
        try:
            import pandas as pd

            df = pd.read_csv(descriptors_csv)
            # Use numeric columns only
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= len(smiles_list):
                descriptors = df[numeric_cols].values[:len(smiles_list)]
                descriptor_names = list(numeric_cols)
            else:
                logger.warning("Not enough rows in descriptors CSV; need >= %d", len(smiles_list))
        except Exception as exc:
            logger.warning("Failed to load descriptors: %s", exc)

    # Correlation analysis on valid energies
    valid_indices = [i for i, e in enumerate(energies) if e is not None]
    valid_energies = [energies[i] for i in valid_indices]
    correlation_results: dict[str, Any] = {
        "n_molecules": len(smiles_list),
        "n_valid_energies": len(valid_energies),
    }

    if descriptors is not None and len(valid_energies) >= 3:
        # Extract descriptors for valid molecules
        desc_valid = descriptors[valid_indices] if len(valid_indices) <= len(descriptors) else descriptors[:len(valid_energies)]
        corr = correlation_analysis(valid_energies, desc_valid, descriptor_names)
        correlation_results.update(corr)

        # Generate plots
        plot_paths: dict[str, Path] = {}

        corr_plot = output_dir / "correlation_matrix.png"
        if plot_correlation_matrix(corr, corr_plot):
            plot_paths["correlation_matrix"] = corr_plot

        energy_plot = output_dir / "energy_landscape.png"
        if plot_energy_landscape(valid_energies, smiles_list[:len(valid_energies)], energy_plot):
            plot_paths["energy_landscape"] = energy_plot

        correlation_results["plots"] = {k: str(v) for k, v in plot_paths.items()}

    # Generate HTML report
    report_path = output_dir / "qmc_analysis_report.html"
    generate_html_report(
        correlation_results,
        energies,
        smiles_list,
        plot_paths if descriptors is not None else {},
        report_path,
    )
    correlation_results["report_path"] = str(report_path)

    # Save JSON summary
    json_path = output_dir / "qmc_analysis_results.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(correlation_results, fh, indent=2, default=str)
    correlation_results["json_path"] = str(json_path)

    return correlation_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze QMC outputs and correlate with P3 descriptors.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--qmc-dir", type=Path, required=True,
                        help="Directory containing QMC input subdirectories")
    parser.add_argument("--descriptors", type=Path, default=None,
                        help="CSV file with P3 descriptor values")
    parser.add_argument("--pennylane", action="store_true",
                        help="Use PennyLane VQE as QMC energy proxy")
    parser.add_argument("--n-qubits", type=int, default=8, help="Qubits for PennyLane circuit")
    parser.add_argument("--n-layers", type=int, default=2, help="Layers for PennyLane circuit")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    logger.info("QMC Analysis — Starting")
    logger.info("  Input:     %s", args.qmc_dir)
    logger.info("  PennyLane: %s", "YES" if args.pennylane and _HAS_PENNYLANE else "NO")
    logger.info("  Descriptors: %s", args.descriptors if args.descriptors else "none")

    results = analyze_qmc_directory(
        qmc_dir=args.qmc_dir,
        descriptors_csv=args.descriptors,
        use_pennylane=args.pennylane,
        n_qubits=args.n_qubits,
        n_layers=args.n_layers,
        output_dir=args.output_dir,
    )

    if "error" in results:
        logger.error("Analysis failed: %s", results["error"])
        sys.exit(1)

    n_corr = len(results.get("correlations", []))
    n_energies = results.get("n_valid_energies", 0)

    print(f"\n{'=' * 60}")
    print(f"  QMC Analysis Complete")
    print(f"  {'=' * 60}")
    print(f"  Molecules found:       {results.get('n_molecules', 0)}")
    print(f"  Valid QMC energies:    {n_energies}")
    print(f"  PennyLane proxy:       {'YES' if args.pennylane and _HAS_PENNYLANE else 'NO'}")
    print(f"  Correlation features:  {n_corr}")
    if n_corr > 0:
        top_corr = results["correlations"][0]
        print(f"  Best Pearson r:        {top_corr['pearson_r']:.4f} "
              f"(p={top_corr['pearson_p']:.4e}, {top_corr['descriptor']})")
    if results.get("report_path"):
        print(f"  Report:                {results['report_path']}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
