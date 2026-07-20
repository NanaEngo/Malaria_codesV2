"""
p1_latent_space_viz.py
=======================
REVISION-ROADMAP R11 — VAE latent space visualisation.

Loads the saved 64D VAE embeddings, applies UMAP dimensionality reduction,
and generates a scatter plot coloured by compound source (NP, SD, Cheese,
STONED-SELFIES). Saved as SI Figure S14.

Outputs (results/figures/):
  p1_latent_space_umap.pdf   — publication-quality UMAP plot (SI Figure S14)
  p1_latent_space_umap.png   — rasterised version for quick inspection
  p1_latent_space_umap.csv   — UMAP coordinates + source labels

Usage:
  python scripts/p1_latent_space_viz.py [--embeddings PATH] [--n-sample 5000]

Requirements:
  conda activate malaria_md
  pip install umap-learn matplotlib
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

PROJECT = Path(__file__).parent.parent
RESULTS = PROJECT / "results"
FIGURES = RESULTS / "figures"

SOURCE_COLORS = {
    "NP":     "#2ca02c",   # green
    "SD":     "#e377c2",   # pink
    "Cheese": "#8c564b",   # brown
    "STONED": "#1f77b4",   # blue
}
SOURCE_LABELS = {
    "NP":     "African NP",
    "SD":     "Synthetic drug",
    "Cheese": "Cheese analogue",
    "STONED": "STONED-SELFIES",
}


def load_embeddings(embeddings_path: "Path | None") -> "tuple[np.ndarray, list]":
    """
    Load 64D VAE embeddings and source labels.
    Tries several candidate file locations.
    Returns (embeddings array [N, 64], source_labels list[str]).
    """
    candidates = [
        embeddings_path,
        RESULTS / "clustering" / "vae_embeddings_64d.npy",
        RESULTS / "clustering" / "latent_vectors_64d.npy",
        RESULTS / "vae_embeddings_64d.npy",
        RESULTS / "latent_vectors.npy",
    ]
    candidates = [p for p in candidates if p is not None]

    emb_path = next((p for p in candidates if p.exists()), None)
    if emb_path is None:
        raise FileNotFoundError(
            "VAE embeddings not found. Expected one of:\n"
            + "\n".join(str(p) for p in candidates)
            + "\nRun the VAE training pipeline first.")

    print(f"  Loading embeddings from {emb_path}")
    # Use allow_pickle=False for .npy files that contain plain arrays
    with open(emb_path, "rb") as fh:
        embeddings = np.load(fh, allow_pickle=False)
    print(f"  Embeddings shape: {embeddings.shape}")

    # Load source labels from eos80ch library
    lib = pd.read_csv(RESULTS / "eos80ch_malaria_final_activity.csv")
    smiles_col = "input"

    # Determine source from per-source breakdown
    # Build source sets from available metadata files
    seed_smiles   = set()
    sd_smiles     = set()
    stoned_smiles = set()
    cheese_smiles = set()

    seed_file = RESULTS / "seed_african_nps_smiles.csv"
    if seed_file.exists():
        seed_smiles = set(pd.read_csv(seed_file)["smiles"].dropna().tolist())

    # Synthetic drugs: DrugBank-derived file
    for sd_candidate in [RESULTS / "eos57bx_generated_mol2molscaf.csv",
                          RESULTS / "eos9gg2_malaria_final_drugbank_mpo.csv"]:
        if sd_candidate.exists():
            df_sd = pd.read_csv(sd_candidate)
            col = next((c for c in df_sd.columns
                        if c.lower() in ("smiles", "input", "standard_smiles")),
                       df_sd.columns[0])
            sd_smiles = set(df_sd[col].dropna().tolist())
            break

    # STONED-SELFIES: generated molecules file
    for stoned_candidate in [RESULTS / "stoned_selfies_generated.csv",
                              RESULTS / "all_mol_selfies.csv",
                              RESULTS / "5k_all_mol_selfies.csv"]:
        if stoned_candidate.exists():
            df_st = pd.read_csv(stoned_candidate)
            col = next((c for c in df_st.columns
                        if c.lower() in ("smiles", "input")), df_st.columns[0])
            stoned_smiles = set(df_st[col].dropna().tolist())
            break

    # Cheese analogues: CHEESE-generated file
    for cheese_candidate in [RESULTS / "eos2db3_malaria_final_chemdiv_mpo.csv",
                              RESULTS / "eos6ost_np_mol_scaf_smi_filt.csv"]:
        if cheese_candidate.exists():
            df_ch = pd.read_csv(cheese_candidate)
            col = next((c for c in df_ch.columns
                        if c.lower() in ("smiles", "input")), df_ch.columns[0])
            cheese_smiles = set(df_ch[col].dropna().tolist())
            break

    def assign_source(smi):
        if smi in seed_smiles:
            return "NP"
        if smi in sd_smiles:
            return "SD"
        if smi in stoned_smiles:
            return "STONED"
        if smi in cheese_smiles:
            return "Cheese"
        return "Cheese"  # default for unmatched analogues

    labels = [assign_source(s) for s in lib[smiles_col].tolist()]

    # Align embeddings length with library
    n = min(len(embeddings), len(labels))
    return embeddings[:n], labels[:n]


def run_umap(embeddings: np.ndarray, n_sample: int,
             seed: int = 42) -> "tuple[np.ndarray, np.ndarray]":
    """Apply UMAP to embeddings, optionally subsampling."""
    try:
        import umap
    except ImportError:
        raise ImportError("umap-learn not installed. Run: pip install umap-learn")

    n = min(n_sample, len(embeddings))
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(embeddings), n, replace=False)
    sub = embeddings[idx]

    print(f"  Running UMAP on {n} molecules (n_neighbors=15, min_dist=0.1)...")
    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1,
                         metric="euclidean", random_state=seed, verbose=False)
    coords = reducer.fit_transform(sub)
    return coords, idx


def plot_umap(coords: np.ndarray, labels: list[str],
              idx: np.ndarray, out_dir: Path) -> None:
    """Generate and save UMAP scatter plot."""
    fig, ax = plt.subplots(figsize=(7, 6))

    for source, color in SOURCE_COLORS.items():
        mask = np.array([labels[i] == source for i in idx])
        if mask.sum() == 0:
            continue
        ax.scatter(coords[mask, 0], coords[mask, 1],
                   c=color, s=2, alpha=0.4, linewidths=0,
                   label=SOURCE_LABELS[source], rasterized=True)

    # Legend
    handles = [mpatches.Patch(color=c, label=SOURCE_LABELS[s])
               for s, c in SOURCE_COLORS.items()
               if any(labels[i] == s for i in idx)]
    ax.legend(handles=handles, loc="upper right", fontsize=9,
              framealpha=0.8, markerscale=4)

    ax.set_xlabel("UMAP 1", fontsize=11)
    ax.set_ylabel("UMAP 2", fontsize=11)
    ax.set_title("VAE 64D Latent Space — UMAP Projection\n"
                 "(coloured by compound source)", fontsize=11)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        out = out_dir / f"p1_latent_space_umap.{ext}"
        plt.savefig(out, dpi=300 if ext == "png" else None, bbox_inches="tight")
        print(f"  Saved: {out}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="R11: VAE latent space UMAP visualisation")
    parser.add_argument("--embeddings", type=Path, default=None,
                        help="Path to .npy embeddings file (optional)")
    parser.add_argument("--n-sample", type=int, default=5000,
                        help="Number of molecules to plot (default: 5000)")
    args = parser.parse_args()

    print("=" * 60)
    print("R11: VAE Latent Space UMAP Visualisation")
    print("=" * 60)

    embeddings, labels = load_embeddings(args.embeddings)
    coords, idx = run_umap(embeddings, args.n_sample)

    # Save coordinates
    coord_df = pd.DataFrame({
        "umap1":  coords[:, 0],
        "umap2":  coords[:, 1],
        "source": [labels[i] for i in idx],
    })
    out_csv = RESULTS / "p1_latent_space_umap.csv"
    coord_df.to_csv(out_csv, index=False)
    print(f"  Saved: {out_csv}")

    plot_umap(coords, labels, idx, FIGURES)

    # Source distribution summary
    from collections import Counter
    counts = Counter(labels[i] for i in idx)
    print("\n  Source distribution in plot:")
    for src, n in sorted(counts.items()):
        print(f"    {src}: {n} ({n/len(idx)*100:.1f}%)")


if __name__ == "__main__":
    main()
