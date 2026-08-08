"""
Paper 3 — Generate a better persistence_diagrams figure.

Produces a 2×2 figure:
  Top row: 2D structures of a representative African natural product and a
          synthetic/generated molecule.
  Bottom row: birth–death persistence diagrams (H0, H1, H2) for each molecule.

The figure highlights the topological contrast central to the paper: African
natural products tend to have persistent H1 (ring) features reflecting conserved
scaffolds, whereas synthetic/generated molecules often show more transient
H0/H1 signatures.

Run from the project root (or anywhere) in the malaria_md environment, e.g.:
    conda run -n malaria_md python scripts/p3_generate_persistence_diagrams.py
"""

import argparse
import importlib.metadata
import json
import subprocess
from datetime import datetime, timezone
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw

# Import TDA helpers from the project pipeline
sys.path.insert(0, str(Path(__file__).parent))
from p3_tda_pipeline import (
    _HAS_RIPSER,
    compute_persistence,
    smiles_to_distance_matrix,
)

if not _HAS_RIPSER:
    raise ImportError("ripser is required. Run: pip install ripser")

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
GRAPHICS_DIR = PROJECT_DIR / "manuscript" / "LaTeX" / "Graphics"

# Robust cross-project seed path (P1 is a sibling directory)
SEED_PATH = (
    PROJECT_DIR.parent
    / "Project1_Chem_space_antimalarial_V2_CorrectedGrid"
    / "p1_stoned_mmv_seeds.csv"
)
TDA_PATH = RESULTS_DIR / "p3_tda_fingerprints.csv"

# Colorblind-friendly Okabe-Ito palette + distinct markers
_DIM_STYLE = {
    0: {"color": "#E69F00", "marker": "o", "label": r"H$_0$"},  # components
    1: {"color": "#56B4E9", "marker": "s", "label": r"H$_1$"},  # rings
    2: {"color": "#009E73", "marker": "^", "label": r"H$_2$"},  # voids
}


def _get_git_info() -> dict:
    """Capture git commit hash and dirty-state for reproducibility."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_DIR, text=True
        ).strip()
        short = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_DIR, text=True
        ).strip()
        # `git status --porcelain` is sensitive to any tracked or untracked
        # modification; empty output means the working tree is clean.
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=PROJECT_DIR, text=True
        ).strip()
        return {"commit": commit, "short": short, "dirty": bool(status)}
    except Exception:  # not a git repo or git unavailable
        return {"commit": None, "short": None, "dirty": None}


def _get_dependency_versions() -> dict:
    """Record key dependency versions that affect the computed diagrams."""
    versions = {}
    for pkg in ("rdkit", "ripser", "numpy", "matplotlib", "pandas"):
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = None
    return versions


def _canonical_set(smiles_series: pd.Series) -> set:
    """Return canonical SMILES set for robust matching across files."""
    canonical = set()
    for s in smiles_series.dropna().unique():
        mol = Chem.MolFromSmiles(s)
        if mol is not None:
            canonical.add(Chem.MolToSmiles(mol))
    return canonical


def _match_seed_mask(tda: pd.DataFrame, seed_smiles: set) -> pd.Series:
    """Return boolean mask of rows whose canonical SMILES is in seed_smiles."""
    mask = []
    for s in tda["smiles"]:
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            mask.append(False)
            continue
        mask.append(Chem.MolToSmiles(mol) in seed_smiles)
    return pd.Series(mask, index=tda.index)


def _select_by_quantiles(df, filter_cols, sort_cols, ascending):
    """Select molecules matching quantile filters, with progressive fallback."""
    candidates = df.copy()
    for col, (q, direction) in filter_cols.items():
        threshold = candidates[col].quantile(q)
        if direction == ">=":
            candidates = candidates[candidates[col] >= threshold]
        elif direction == "<=":
            candidates = candidates[candidates[col] <= threshold]
    if len(candidates) == 0:
        # Fallback: relax filters and just sort
        candidates = df.copy()
    return candidates.sort_values(by=sort_cols, ascending=ascending).head(1)


def select_representative_molecules(tda_path: Path, seed_path: Path):
    """Pick one African NP seed and one non-seed with contrasting TDA."""
    seed_df = pd.read_csv(seed_path)
    seed_smiles = _canonical_set(seed_df["smiles"])

    tda = pd.read_csv(tda_path)
    tda["is_seed"] = _match_seed_mask(tda, seed_smiles)

    # African NP: seed with high H1 count/persistence (rigid scaffold)
    np_candidates = _select_by_quantiles(
        tda[tda["is_seed"]],
        filter_cols={"H1_count": (0.75, ">=")},
        sort_cols=["H1_count", "H1_mean_pers"],
        ascending=[False, False],
    )
    if np_candidates.empty:
        raise RuntimeError("No African NP seed found in TDA data.")
    np_row = np_candidates.iloc[0]

    # Non-seed: low H1 count, high H0 max persistence (flexible chain)
    non_seed = tda[~tda["is_seed"]].copy()
    syn_candidates = _select_by_quantiles(
        non_seed,
        filter_cols={"H1_count": (0.25, "<="), "H0_max_pers": (0.75, ">=")},
        sort_cols=["H0_count", "H0_max_pers"],
        ascending=[False, False],
    )
    if syn_candidates.empty:
        raise RuntimeError("No non-seed candidate found in TDA data.")
    syn_row = syn_candidates.iloc[0]

    return np_row, syn_row


def get_diagrams(smiles: str):
    """Return persistence diagrams [H0, H1, H2] for a SMILES string."""
    dm = smiles_to_distance_matrix(smiles)
    if dm is None:
        raise RuntimeError(f"Could not compute distance matrix for {smiles}")
    return compute_persistence(dm)


def plot_persistence_diagram(ax, dgms, title="", show_legend=True):
    """Plot H0, H1, H2 persistence diagrams on birth–death axes."""
    # Determine axis limits from all finite points
    all_finite = [
        dgm[np.isfinite(dgm[:, 1])]
        for dgm in dgms
        if len(dgm[np.isfinite(dgm[:, 1])]) > 0
    ]
    if all_finite:
        all_pts = np.vstack(all_finite)
        max_val = max(all_pts[:, 1].max(), all_pts[:, 0].max())
    else:
        max_val = 5.0

    max_val *= 1.05

    for dim, dgm in enumerate(dgms):
        finite = dgm[np.isfinite(dgm[:, 1])]
        if len(finite) == 0:
            continue
        style = _DIM_STYLE[dim]
        # H0 (components) can be numerous; down-weight its visual impact so
        # the more informative H1 ring features remain prominent.
        size = 22 if dim == 0 else 45
        alpha = 0.35 if dim == 0 else 0.75
        ax.scatter(
            finite[:, 0],
            finite[:, 1],
            s=size,
            c=style["color"],
            marker=style["marker"],
            label=style["label"],
            alpha=alpha,
            edgecolors="white",
            linewidths=0.5,
        )

    # Diagonal reference (persistence = 0)
    ax.plot([0, max_val], [0, max_val], "k--", linewidth=1.0, alpha=0.5)
    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Birth", fontsize=11)
    ax.set_ylabel("Death", fontsize=11)
    ax.set_title(title, fontsize=12)
    if show_legend:
        ax.legend(loc="upper left", fontsize=9)


def main():
    parser = argparse.ArgumentParser(
        description="Generate the P3 persistence_diagrams figure."
    )
    parser.add_argument(
        "--seed-path",
        type=Path,
        default=SEED_PATH,
        help="Path to P1 seed SMILES CSV (default: cross-project default)",
    )
    parser.add_argument(
        "--tda-path",
        type=Path,
        default=TDA_PATH,
        help="Path to P3 TDA fingerprints CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=GRAPHICS_DIR / "persistence_diagrams.pdf",
        help="Output figure path",
    )
    args = parser.parse_args()

    np_row, syn_row = select_representative_molecules(args.tda_path, args.seed_path)

    np_smiles = np_row["smiles"]
    syn_smiles = syn_row["smiles"]

    np_dgms = get_diagrams(np_smiles)
    syn_dgms = get_diagrams(syn_smiles)

    # Generate 2D depictions with None checks
    np_mol = Chem.MolFromSmiles(np_smiles)
    syn_mol = Chem.MolFromSmiles(syn_smiles)
    if np_mol is None or syn_mol is None:
        raise RuntimeError("RDKit could not parse one of the selected SMILES.")

    np_img = Draw.MolToImage(np_mol, size=(400, 400), kekulize=True)
    syn_img = Draw.MolToImage(syn_mol, size=(400, 400), kekulize=True)

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    # Top row: 2D structures
    axes[0, 0].imshow(np_img)
    axes[0, 0].axis("off")
    axes[0, 0].set_title(
        "A. African natural product (seed)", fontsize=12, fontweight="bold"
    )

    axes[0, 1].imshow(syn_img)
    axes[0, 1].axis("off")
    axes[0, 1].set_title(
        "B. Generated non-seed candidate", fontsize=12, fontweight="bold"
    )

    # Bottom row: persistence diagrams
    plot_persistence_diagram(
        axes[1, 0],
        np_dgms,
        title="C. Persistence diagram (African NP)",
    )
    plot_persistence_diagram(
        axes[1, 1],
        syn_dgms,
        title="D. Persistence diagram (generated non-seed)",
    )

    plt.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.output, format="pdf", dpi=300, bbox_inches="tight")
    print(f"Saved figure to: {args.output}")

    # PNG preview for quick inspection
    png_path = args.output.with_suffix(".png")
    plt.savefig(png_path, format="png", dpi=150, bbox_inches="tight")
    print(f"Saved preview to: {png_path}")

    # Print selected molecules for the caption
    np_idx = int(np_row.name)
    syn_idx = int(syn_row.name)
    print("\nSelected molecules:")
    print(f"  African NP (row {np_idx}): {np_smiles}")
    print(
        f"    H1_count={np_row['H1_count']:.0f}, "
        f"H1_mean_pers={np_row['H1_mean_pers']:.3f}"
    )
    print(f"  Non-seed   (row {syn_idx}): {syn_smiles}")
    print(
        f"    H1_count={syn_row['H1_count']:.0f}, "
        f"H0_max_pers={syn_row['H0_max_pers']:.3f}"
    )

    # Reproducibility sidecar
    sidecar = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
        "git": _get_git_info(),
        "dependencies": _get_dependency_versions(),
        "seed_path": str(args.seed_path.resolve()),
        "tda_path": str(args.tda_path.resolve()),
        "output_pdf": str(args.output.resolve()),
        "selection": {
            "african_np": {
                "row_index": np_idx,
                "smiles": np_smiles,
                "H1_count": int(np_row["H1_count"]),
                "H1_mean_pers": float(np_row["H1_mean_pers"]),
            },
            "generated_non_seed": {
                "row_index": syn_idx,
                "smiles": syn_smiles,
                "H1_count": int(syn_row["H1_count"]),
                "H0_max_pers": float(syn_row["H0_max_pers"]),
            },
        },
    }
    sidecar_path = args.output.with_suffix(".json")
    sidecar_path.write_text(json.dumps(sidecar, indent=2))
    print(f"Saved reproducibility sidecar to: {sidecar_path}")


if __name__ == "__main__":
    main()
