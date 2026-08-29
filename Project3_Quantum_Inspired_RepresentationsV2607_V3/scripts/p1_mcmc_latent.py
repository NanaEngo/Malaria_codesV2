"""
Paper 1 — Quick Win: MCMC Metropolis-Hastings Latent Space Sampling.

Implements a Markov Chain Monte Carlo random walk in a 2D UMAP-proxy latent
space to generate novel molecules optimised for Multi-Parameter Optimisation
(MPO) score.

Strategy:
  1. Project the existing molecule library (ECFP4 fingerprints → UMAP 2D)
     to create a differentiable proxy latent space.
  2. Fit a Gaussian Mixture Model (GMM) to estimate the data density in
     latent space (serves as the prior p(z)).
  3. Fit a surrogate model (Random Forest) to predict MPO score from latent
     coordinates (serves as the likelihood proxy p(MPO|z)).
  4. Run Metropolis-Hastings MCMC: propose new z' by perturbing current z
     with Gaussian noise, accept/reject based on p(z') × p(MPO|z').
  5. Decode promising latent points back to SMILES via nearest-neighbour
     lookup in the original UMAP space.

Outputs:
    results/p1_mcmc_generated.csv       — generated molecules with MPO scores
    results/p1_mcmc_trajectory.csv       — MCMC trajectory (acceptance, MPO)
    results/p1_mcmc_landscape.png        — latent space + MCMC walk plot
    results/p1_mcmc_summary.txt          — summary statistics

Usage:
    python scripts/p1_mcmc_latent.py
    python scripts/p1_mcmc_latent.py --n-steps 5000 --n-chains 4 --warmup 1000

Requires:
    rdkit, umap-learn, scikit-learn, pandas, numpy, matplotlib
"""

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.metrics import pairwise_distances_argmin_min

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_full_library() -> pd.DataFrame:
    """Load the full synthesisable library with MPO scores.

    Returns DataFrame with columns: smiles, weighted_mpo_score, qed, sa_score.
    """
    path = RESULTS_DIR / "c6_primary_leads_synthesisable.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={"input": "smiles"})

    # Load additional ADMET columns if available
    admet_path = RESULTS_DIR / "eos7kpb_malaria_final_screening.csv"
    if admet_path.exists():
        admet = pd.read_csv(admet_path)
        admet = admet.rename(columns={"input": "smiles"})
        df = df.merge(
            admet[["smiles", "aq_sol", "cyp3a4", "caco_2", "pf_nf54", "hepg2"]],
            on="smiles", how="left"
        )

    return df


def ecfp4_fingerprints(smiles_list: list[str]) -> np.ndarray:
    """Batch compute ECFP4 fingerprints (2048-bit)."""
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


# ---------------------------------------------------------------------------
# Latent space construction (UMAP proxy)
# ---------------------------------------------------------------------------

def build_latent_space(ecfp4: np.ndarray, smiles_list: list[str],
                       mpo_scores: np.ndarray,
                       n_components: int = 2,
                       sample: int = 5000,
                       seed: int = 42) -> dict:
    """Build a 2D proxy latent space via UMAP on ECFP4 fingerprints.

    Returns dict with:
        latent_coords: (N, 2) UMAP coordinates
        samples: (N,) indices of sampled molecules
        smiles_subset: list of SMILES for sampled molecules
        mpo_subset: MPO scores for sampled molecules
        reducer: fitted UMAP object (for transform)
        gmm: fitted Gaussian Mixture Model (prior p(z))
        surrogate: fitted Random Forest (MPO predictor)
    r2_val: validation R² of surrogate
    """
    from umap import UMAP
    from sklearn.mixture import GaussianMixture
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split

    n = min(sample, len(smiles_list))
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(smiles_list), n, replace=False)
    idx.sort()  # maintain ordering

    print(f"  Sub-sampling {n} molecules for latent space...")
    ecfp4_sub = ecfp4[idx]
    smiles_sub = [smiles_list[i] for i in idx]
    mpo_sub = mpo_scores[idx]

    # UMAP projection → 2D latent space
    print(f"  UMAP {ecfp4_sub.shape[1]}D → {n_components}D (Jaccard metric)...")
    reducer = UMAP(n_components=n_components, metric="jaccard",
                   random_state=seed, n_neighbors=15, min_dist=0.1)
    latent = reducer.fit_transform(ecfp4_sub)

    # Prior: Gaussian Mixture Model on latent space (p(z))
    print("  Fitting GMM prior (n_components=5)...")
    gmm = GaussianMixture(n_components=5, random_state=seed, max_iter=200)
    gmm.fit(latent)

    # Surrogate: Random Forest to predict MPO from latent coordinates
    # Split for validation
    lat_train, lat_val, mpo_train, mpo_val = train_test_split(
        latent, mpo_sub, test_size=0.2, random_state=seed
    )
    print(f"  Training MPO surrogate (RF, train={len(lat_train)}, val={len(lat_val)})...")
    surrogate = RandomForestRegressor(n_estimators=200, n_jobs=-1,
                                      random_state=seed)
    surrogate.fit(lat_train, mpo_train)
    r2_val = surrogate.score(lat_val, mpo_val)
    print(f"  MPO surrogate R² (validation): {r2_val:.4f}")

    # Scale MPO to [0, 1] for acceptance probability
    mpo_min, mpo_max = mpo_sub.min(), mpo_sub.max()
    mpo_norm = (mpo_sub - mpo_min) / (mpo_max - mpo_min + 1e-10)

    return {
        "latent_coords": latent,
        "idx": idx,
        "smiles_subset": smiles_sub,
        "mpo_subset": mpo_sub,
        "mpo_norm": mpo_norm,
        "reducer": reducer,
        "gmm": gmm,
        "surrogate": surrogate,
        "r2_val": r2_val,
        "mpo_min": mpo_min,
        "mpo_max": mpo_max,
        "ecfp4_full": ecfp4,
    }


# ---------------------------------------------------------------------------
# MCMC Sampler
# ---------------------------------------------------------------------------

def log_prior(z: np.ndarray, gmm) -> float:
    """Log-prior density p(z) from GMM."""
    return float(gmm.score_samples(z.reshape(1, -1))[0])


def log_likelihood(z: np.ndarray, surrogate, mpo_min: float,
                   mpo_max: float, temperature: float = 1.0) -> float:
    """Log-likelihood: predicted MPO score (scaled) × temperature.

    Higher temperature = flatter acceptance landscape (more exploration).
    """
    mpo_pred = float(surrogate.predict(z.reshape(1, -1))[0])
    mpo_norm = (mpo_pred - mpo_min) / (mpo_max - mpo_min + 1e-10)
    mpo_norm = np.clip(mpo_norm, 0.0, 1.0)
    # log-likelihood ∝ temperature × MPO_norm
    return temperature * np.log(mpo_norm + 1e-10)


def log_posterior(z: np.ndarray, gmm, surrogate,
                  mpo_min: float, mpo_max: float,
                  temperature: float = 1.0,
                  prior_weight: float = 0.3) -> float:
    """Log-posterior: prior_weight × log p(z) + log p(MPO|z).

    prior_weight controls the strength of the data density prior
    relative to the MPO likelihood.
    """
    lp = prior_weight * log_prior(z, gmm)
    ll = log_likelihood(z, surrogate, mpo_min, mpo_max, temperature)
    return lp + ll


def run_mcmc(initial_z: np.ndarray,
             proposal_std: float,
             n_steps: int,
             warmup: int,
             gmm, surrogate,
             mpo_min: float, mpo_max: float,
             temperature: float = 1.0,
             prior_weight: float = 0.3,
             seed: int = 42) -> dict:
    """Metropolis-Hastings MCMC in latent space.

    Args:
        initial_z: starting point in latent space
        proposal_std: std of Gaussian proposal distribution
        n_steps: total MCMC steps
        warmup: steps to discard as burn-in
        gmm: fitted GMM (prior)
        surrogate: fitted RF (MPO predictor)
        temperature: acceptance temperature
        prior_weight: weight of prior vs likelihood
        seed: RNG seed

    Returns:
        dict with: samples, mpo_preds, log_posts, acceptance_rate
    """
    rng = np.random.default_rng(seed)
    z_current = initial_z.copy()
    lp_current = log_posterior(z_current, gmm, surrogate,
                                mpo_min, mpo_max, temperature, prior_weight)

    samples = [z_current.copy()]
    mpo_preds = [float(surrogate.predict(z_current.reshape(1, -1))[0])]
    log_posts = [lp_current]
    n_accepted = 0

    for step in range(n_steps):
        # Propose: z' = z + N(0, σ²I)
        z_proposal = z_current + rng.normal(0, proposal_std, size=z_current.shape)
        lp_proposal = log_posterior(z_proposal, gmm, surrogate,
                                     mpo_min, mpo_max, temperature, prior_weight)

        # Accept/reject
        if lp_proposal > lp_current or rng.uniform() < np.exp(lp_proposal - lp_current):
            z_current = z_proposal
            lp_current = lp_proposal
            n_accepted += 1

        samples.append(z_current.copy())
        mpo_preds.append(float(surrogate.predict(z_current.reshape(1, -1))[0]))
        log_posts.append(lp_current)

        if (step + 1) % 1000 == 0:
            print(f"    Step {step + 1}/{n_steps}  "
                  f"AC rate: {n_accepted / (step + 1):.2%}  "
                  f"MPO: {mpo_preds[-1]:.4f}")

    # Discard warmup
    post_warmup = samples[warmup:]
    post_mpo = mpo_preds[warmup:]
    post_lp = log_posts[warmup:]
    acceptance_rate = n_accepted / n_steps

    return {
        "samples": np.array(post_warmup),
        "all_samples": np.array(samples),
        "mpo_preds": np.array(post_mpo),
        "all_mpo_preds": np.array(mpo_preds),
        "log_posts": np.array(post_lp),
        "acceptance_rate": acceptance_rate,
    }


# ---------------------------------------------------------------------------
# Decoding: latent → SMILES via nearest-neighbour
# ---------------------------------------------------------------------------

def decode_nearest(z: np.ndarray, latent_coords: np.ndarray,
                   smiles_pool: list[str], mpo_pool: np.ndarray,
                   n_neighbours: int = 3) -> tuple[str, float]:
    """Decode a latent point to SMILES by nearest-neighbour search.

    Returns the SMILES of the nearest molecule in latent space along with
    its MPO score.
    """
    idx, dist = pairwise_distances_argmin_min(z.reshape(1, -1), latent_coords)
    i = int(idx[0])
    return smiles_pool[i], float(mpo_pool[i])


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_landscape(latent_coords: np.ndarray,
                   mpo_scores: np.ndarray,
                   mcmc_results: dict,
                   mcmc_idx: int,
                   output_dir: Path,
                   alpha: float = 0.3) -> None:
    """Plot latent space coloured by MPO + MCMC trajectory."""
    fig, ax = plt.subplots(figsize=(8, 7))

    # Background: latent space coloured by MPO
    sc = ax.scatter(latent_coords[:, 0], latent_coords[:, 1],
                    c=mpo_scores, cmap="viridis", s=8, alpha=alpha,
                    edgecolors="none", vmin=0, vmax=1)
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8)
    cbar.set_label("MPO Score", fontsize=10)
    cbar.ax.tick_params(labelsize=8)

    # MCMC trajectory (all samples, fading)
    all_s = mcmc_results["all_samples"]
    ax.plot(all_s[:, 0], all_s[:, 1], "r-", lw=0.5, alpha=0.5)
    ax.scatter(all_s[0, 0], all_s[0, 1], c="blue", s=60, marker="*",
               edgecolors="white", zorder=5, label="Start")
    ax.scatter(all_s[-1, 0], all_s[-1, 1], c="red", s=60, marker="D",
               edgecolors="white", zorder=5, label="End")

    # Post-warmup samples
    post = mcmc_results["samples"]
    ax.scatter(post[:, 0], post[:, 1], c="#d62728", s=3, alpha=0.2)

    ax.set_xlabel("UMAP 1 (latent dimension)", fontsize=11)
    ax.set_ylabel("UMAP 2 (latent dimension)", fontsize=11)
    ax.set_title(f"MCMC Trajectory in Proxy Latent Space\n"
                 f"(AC rate: {mcmc_results['acceptance_rate']:.1%})", fontsize=11)
    ax.legend(fontsize=8, loc="lower right")
    ax.tick_params(labelsize=9)
    plt.tight_layout()

    out_png = output_dir / f"p1_mcmc_landscape_chain{mcmc_idx}.png"
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"  Saved: {out_png}")
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MCMC Metropolis-Hastings Latent Space Sampling"
    )
    parser.add_argument("--n-steps", type=int, default=5000,
                        help="MCMC steps per chain (default: 5000)")
    parser.add_argument("--warmup", type=int, default=1000,
                        help="Burn-in steps to discard (default: 1000)")
    parser.add_argument("--n-chains", type=int, default=4,
                        help="Number of parallel MCMC chains (default: 4)")
    parser.add_argument("--proposal-std", type=float, default=0.15,
                        help="Gaussian proposal std (default: 0.15)")
    parser.add_argument("--temperature", type=float, default=1.0,
                        help="Acceptance temperature (default: 1.0)")
    parser.add_argument("--prior-weight", type=float, default=0.3,
                        help="Prior weight vs likelihood (default: 0.3)")
    parser.add_argument("--n-gen", type=int, default=20,
                        help="Number of molecules to decode and report (default: 20)")
    parser.add_argument("--latent-sample", type=int, default=3000,
                        help="Molecules to build latent space from (default: 3000)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("=" * 60)
    print("Paper 1 — MCMC Metropolis-Hastings Latent Space Sampling")
    print(f"  Steps/chain:    {args.n_steps}")
    print(f"  Chains:         {args.n_chains}")
    print(f"  Warmup:         {args.warmup}")
    print(f"  Proposal σ:     {args.proposal_std}")
    print(f"  Temperature:    {args.temperature}")
    print(f"  Prior weight:   {args.prior_weight}")
    print("=" * 60)

    t0_total = time.perf_counter()

    # Step 1: Load data
    print("\n[1/5] Loading molecule library...")
    df = load_full_library()
    print(f"  Loaded {len(df)} molecules")

    # Use weighted_mpo_score as optimisation target
    if "weighted_mpo_score" in df.columns:
        mpo_scores = df["weighted_mpo_score"].fillna(0).values
    elif "mpo_score" in df.columns:
        mpo_scores = df["mpo_score"].fillna(0).values
    else:
        print("  Warning: no MPO score found; using QED as proxy.")
        mpo_scores = df["qed"].fillna(0).values

    smiles_list = df["smiles"].tolist()
    print(f"  MPO range: [{mpo_scores.min():.4f}, {mpo_scores.max():.4f}]")

    # Step 2: Compute ECFP4 fingerprints
    print("\n[2/5] Computing ECFP4 fingerprints...")
    t0 = time.perf_counter()
    ecfp4 = ecfp4_fingerprints(smiles_list)
    print(f"  Done in {time.perf_counter() - t0:.1f}s — {len(ecfp4)} × {ecfp4.shape[1]}")

    # Step 3: Build latent space (UMAP proxy)
    print("\n[3/5] Building proxy latent space...")
    ls = build_latent_space(ecfp4, smiles_list, mpo_scores,
                            n_components=2,
                            sample=args.latent_sample,
                            seed=args.seed)

    # Step 4: Run MCMC chains
    print("\n[4/5] Running MCMC chains...")
    chains = []
    # Initialise chains from diverse starting points (high-MPO molecules)
    n_high_mpo = min(args.n_chains * 3, len(ls["latent_coords"]))
    high_mpo_idx = np.argsort(ls["mpo_subset"])[-n_high_mpo:]
    initial_indices = high_mpo_idx[np.linspace(0, len(high_mpo_idx) - 1,
                                                args.n_chains, dtype=int)]

    for chain_i in range(args.n_chains):
        print(f"\n  Chain {chain_i + 1}/{args.n_chains}  "
              f"(initial MPO={ls['mpo_subset'][initial_indices[chain_i]]:.4f})")
        z0 = ls["latent_coords"][initial_indices[chain_i]]
        result = run_mcmc(
            z0, args.proposal_std, args.n_steps, args.warmup,
            ls["gmm"], ls["surrogate"],
            ls["mpo_min"], ls["mpo_max"],
            temperature=args.temperature,
            prior_weight=args.prior_weight,
            seed=args.seed + chain_i
        )
        print(f"  Chain {chain_i + 1} done — "
              f"AC rate: {result['acceptance_rate']:.1%}, "
              f"Final MPO: {result['mpo_preds'][-1]:.4f}")
        chains.append(result)

        # Plot landscape for first 2 chains
        if chain_i < 2:
            plot_landscape(ls["latent_coords"], ls["mpo_norm"],
                          result, chain_i, RESULTS_DIR)

    # Step 5: Decode best latent points to SMILES
    print("\n[5/5] Decoding best latent points to SMILES...")

    # Collect all post-warmup samples across chains
    all_samples = np.vstack([c["samples"] for c in chains])
    all_mpo = np.concatenate([c["mpo_preds"] for c in chains])

    # Select best unique molecules
    best_idx = np.argsort(all_mpo)[-args.n_gen * 3:][::-1]  # candidates
    seen_smiles = set()
    generation = []

    for i in best_idx:
        if len(generation) >= args.n_gen:
            break
        z = all_samples[i]
        smi, mpo_nearest = decode_nearest(
            z, ls["latent_coords"], ls["smiles_subset"], ls["mpo_subset"]
        )
        if smi not in seen_smiles:
            seen_smiles.add(smi)
            mpo_pred = all_mpo[i]
            generation.append({
                "smiles": smi,
                "mpo_predicted": round(float(mpo_pred), 4),
                "mpo_nearest": round(float(mpo_nearest), 4),
                "latent_1": round(float(z[0]), 4),
                "latent_2": round(float(z[1]), 4),
            })

    gen_df = pd.DataFrame(generation)
    out_gen = RESULTS_DIR / "p1_mcmc_generated.csv"
    gen_df.to_csv(out_gen, index=False)
    print(f"  Saved: {out_gen}")

    # Trajectory CSV (first chain only for compactness)
    chain0 = chains[0]
    traj_df = pd.DataFrame({
        "step": np.arange(len(chain0["all_mpo_preds"])),
        "mpo_pred": chain0["all_mpo_preds"],
        "log_posterior": np.array(chain0["log_posts"]),
        "latent_1": chain0["all_samples"][:, 0],
        "latent_2": chain0["all_samples"][:, 1],
    })[:args.n_steps + 1]  # trim to exact n_steps + 1

    out_traj = RESULTS_DIR / "p1_mcmc_trajectory.csv"
    traj_df.to_csv(out_traj, index=False)
    print(f"  Saved: {out_traj}")

    # Summary text
    all_ac_rates = [c["acceptance_rate"] for c in chains]
    all_final_mpo = [c["mpo_preds"][-1] for c in chains]
    all_mean_mpo = [c["mpo_preds"].mean() for c in chains]
    mpo_improvement = all_final_mpo[0] - ls["mpo_subset"].mean()

    lines = [
        "MCMC Metropolis-Hastings Latent Space Sampling",
        "=" * 55,
        f"Library molecules:       {len(df)}",
        f"Latent space size:       {args.latent_sample}",
        f"MCMC chains:             {args.n_chains}",
        f"Steps per chain:         {args.n_steps}",
        f"Warmup (discarded):      {args.warmup}",
        f"Proposal std:            {args.proposal_std}",
        f"Temperature:             {args.temperature}",
        f"Prior weight:            {args.prior_weight}",
        "",
        f"MPO surrogate R² (val):  {ls['r2_val']:.4f}",
        f"Mean AC rate:            {np.mean(all_ac_rates):.1%}",
        f"Mean MPO (chains):       {np.mean(all_mean_mpo):.4f}",
        f"Final MPO (chain 0):     {all_final_mpo[0]:.4f}",
        f"Library mean MPO:        {ls['mpo_subset'].mean():.4f}",
        f"MPO improvement:         {mpo_improvement:+.4f}",
        "",
        f"Generated molecules:     {len(generation)}",
        "",
        "Top 5 generated molecules:",
    ]

    for i, row in enumerate(generation[:5]):
        lines.append(f"  {i + 1}. MPO={row['mpo_predicted']:.4f}  "
                     f"{row['smiles'][:80]}")

    lines += [
        "",
        "Interpretation:",
    ]

    if mpo_improvement > 0.02:
        lines.append("  ✓ MCMC successfully discovered higher-MPO regions of latent space.")
    elif mpo_improvement > 0:
        lines.append("  △ Modest MPO improvement — landscape may be flat.")
    else:
        lines.append("  △ MCMC did not improve MPO — surrogate may be inaccurate.")

    summary = "\n".join(lines)
    print("\n" + summary)
    out_txt = RESULTS_DIR / "p1_mcmc_summary.txt"
    out_txt.write_text(summary)
    print(f"  Saved: {out_txt}")
    print(f"\n  Total wall time: {time.perf_counter() - t0_total:.1f}s")


if __name__ == "__main__":
    main()
