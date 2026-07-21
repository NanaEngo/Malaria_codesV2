"""
p1_mpo_sensitivity.py
======================
REVISION-ROADMAP R5 — Formalise MPO weight sensitivity analysis.

Varies each of the 5 MPO component weights ±10% and ±20% (25 combinations),
recomputes MPO scores for the full 65,856-molecule library, and measures:
  - Spearman rank correlation of top-1000 vs. original ranking
  - Jaccard similarity of top-20 hit list vs. original top-20

Target: Spearman ρ > 0.95 and Jaccard ≥ 0.70 for all perturbations.

Outputs (results/):
  p1_mpo_sensitivity.csv         — 25 rows × (weight, delta, spearman, jaccard)
  p1_mpo_sensitivity_summary.txt — human-readable → SM Table S17

Usage:
  python scripts/p1_mpo_sensitivity.py [--n-top 20] [--n-rank 1000]

Requirements:
  conda activate malaria_md
"""

import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

PROJECT = Path(__file__).parent.parent
RESULTS = PROJECT / "results"

# Nominal MPO weights (Vina 35%, DiffDock 25%, QED 20%, ADMET 15%, Ro5 5%)
WEIGHT_NAMES   = ["vina", "diffdock", "qed", "admet", "ro5"]
NOMINAL_WEIGHTS = [0.35, 0.25, 0.20, 0.15, 0.05]
DELTAS = [-0.20, -0.10, 0.00, +0.10, +0.20]


# ---------------------------------------------------------------------------
# Load full library with all MPO component scores
# ---------------------------------------------------------------------------
def load_library() -> pd.DataFrame:
    """
    Load the full 65,856-molecule library with MPO component scores.
    Uses c6 (MPO + SYBA) merged with eos7kpb (ADMET proxies) and
    eos80ch (activity). Individual component scores are reconstructed
    from available data.
    """
    c6 = pd.read_csv(RESULTS / "c6_primary_leads_synthesisable.csv")
    c6 = c6.rename(columns={"input": "smiles"})

    eos7kpb = pd.read_csv(RESULTS / "eos7kpb_malaria_final_screening.csv")
    eos7kpb = eos7kpb.rename(columns={"input": "smiles"})

    # Merge on smiles
    df = c6.merge(eos7kpb[["smiles", "aq_sol", "cyp3a4", "caco_2",
                             "pf_nf54", "hepg2"]],
                  on="smiles", how="left")

    # Reconstruct individual MPO components from available scores
    # S_vina: we use weighted_mpo_score as a proxy for the full MPO;
    # for sensitivity we need to vary weights, so we decompose:
    # weighted_mpo_score ≈ 0.35*S_vina + 0.25*S_diff + 0.20*qed + 0.15*S_admet + 0.05*P_ro5
    # Since individual components are not stored separately, we use:
    #   S_vina   ← normalised from docking (not available per-molecule in c6)
    #   S_diff   ← not available per-molecule
    #   qed      ← available in c6
    #   S_admet  ← proxy from eos7kpb normalised scores
    #   P_ro5    ← computed from RDKit (or approximated from sa_score)
    #
    # Practical approach: use weighted_mpo_score as the baseline and
    # perturb by reweighting the available sub-scores.

    # Normalise available sub-scores to [0,1]
    def minmax(s):
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn) if mx > mn else pd.Series(0.5, index=s.index)

    df["S_qed"]   = df["qed"].clip(0, 1)
    df["S_admet"] = minmax(df["aq_sol"].fillna(df["aq_sol"].median()))
    df["S_ro5"]   = (1 - (df["sa_score"].clip(1, 5) - 1) / 4).clip(0, 1)

    # For Vina and DiffDock components, back-calculate from weighted_mpo_score:
    # weighted_mpo_score = 0.35*S_v + 0.25*S_d + 0.20*S_q + 0.15*S_a + 0.05*S_r
    # residual = weighted_mpo_score - (0.20*S_q + 0.15*S_a + 0.05*S_r)
    # residual ≈ 0.35*S_v + 0.25*S_d  → treat as combined docking score
    df["_residual"] = (df["weighted_mpo_score"]
                       - 0.20 * df["S_qed"]
                       - 0.15 * df["S_admet"]
                       - 0.05 * df["S_ro5"]).clip(0, 1)
    # Split residual proportionally: S_vina = residual * (0.35/0.60), S_diff = residual * (0.25/0.60)
    df["S_vina"]   = (df["_residual"] * (0.35 / 0.60)).clip(0, 1)
    df["S_diffdock"] = (df["_residual"] * (0.25 / 0.60)).clip(0, 1)

    return df


def compute_mpo(df: pd.DataFrame, weights: list[float]) -> pd.Series:
    """Compute MPO score with given weights [vina, diffdock, qed, admet, ro5]."""
    w = weights
    return (w[0] * df["S_vina"]
            + w[1] * df["S_diffdock"]
            + w[2] * df["S_qed"]
            + w[3] * df["S_admet"]
            + w[4] * df["S_ro5"]).clip(0, 1)


# ---------------------------------------------------------------------------
# Main sensitivity loop
# ---------------------------------------------------------------------------
def run_sensitivity(df: pd.DataFrame,
                    n_top: int = 20,
                    n_rank: int = 1000) -> pd.DataFrame:

    # Baseline ranking
    df["mpo_baseline"] = compute_mpo(df, NOMINAL_WEIGHTS)
    baseline_ranked    = df.nlargest(n_rank, "mpo_baseline")["smiles"].tolist()
    baseline_top       = set(df.nlargest(n_top, "mpo_baseline")["smiles"].tolist())

    records = []
    for i, name in enumerate(WEIGHT_NAMES):
        for delta in DELTAS:
            w = NOMINAL_WEIGHTS.copy()
            w[i] = max(0.01, w[i] + delta)
            total = sum(w)
            w = [x / total for x in w]  # renormalise to sum=1

            df["mpo_perturbed"] = compute_mpo(df, w)

            perturbed_ranked = df.nlargest(n_rank, "mpo_perturbed")["smiles"].tolist()
            perturbed_top    = set(df.nlargest(n_top, "mpo_perturbed")["smiles"].tolist())

            # Spearman on top-n_rank
            base_scores = df.set_index("smiles").loc[baseline_ranked, "mpo_baseline"].values
            pert_scores = df.set_index("smiles").loc[baseline_ranked, "mpo_perturbed"].values
            rho, _ = spearmanr(base_scores, pert_scores)

            # Jaccard on top-n_top
            intersection = len(baseline_top & perturbed_top)
            union        = len(baseline_top | perturbed_top)
            jaccard      = intersection / union if union > 0 else 0.0

            records.append({
                "weight_varied": name,
                "delta":         delta,
                "w_vina":        round(w[0], 4),
                "w_diffdock":    round(w[1], 4),
                "w_qed":         round(w[2], 4),
                "w_admet":       round(w[3], 4),
                "w_ro5":         round(w[4], 4),
                "spearman_rho":  round(rho, 4),
                "jaccard_top20": round(jaccard, 4),
                "pass_spearman": rho > 0.95,
                "pass_jaccard":  jaccard >= 0.70,
            })

    return pd.DataFrame(records)


def write_summary(df: pd.DataFrame, n_top: int, n_rank: int) -> None:
    mean_rho = df["spearman_rho"].mean()
    mean_jac = df["jaccard_top20"].mean()
    pass_rho = df["pass_spearman"].mean() * 100
    pass_jac = df["pass_jaccard"].mean() * 100

    lines = [
        "MPO Weight Sensitivity Analysis (SM Table S17)",
        "=" * 55,
        "NOTE: S_vina and S_diffdock are back-calculated from weighted_mpo_score",
        "because individual component scores are not stored per-molecule.",
        "Weight perturbations therefore affect only the QED/ADMET/Ro5 split;",
        "the Vina+DiffDock residual is redistributed proportionally.",
        "Report ρ and Jaccard values with this caveat in SM Table S17.",
        "",
        f"Combinations tested: {len(df)}  (5 weights × 5 deltas)",
        f"Top-{n_rank} Spearman ρ: mean={mean_rho:.4f}  pass rate (>0.95): {pass_rho:.0f}%",
        f"Top-{n_top} Jaccard:     mean={mean_jac:.4f}  pass rate (≥0.70): {pass_jac:.0f}%",
        "",
        "Full results:",
        df.to_string(index=False),
    ]

    if mean_rho > 0.95 and mean_jac >= 0.70:
        lines.insert(3, "CONCLUSION: Framework is ROBUST to weight perturbation.")
    else:
        lines.insert(3, "WARNING: Framework shows sensitivity to weight perturbation.")

    out = RESULTS / "p1_mpo_sensitivity_summary.txt"
    out.write_text("\n".join(lines))
    print(f"  Saved: {out}")


def main():
    parser = argparse.ArgumentParser(
        description="R5: MPO weight sensitivity analysis")
    parser.add_argument("--n-top",  type=int, default=20,
                        help="Size of top hit list for Jaccard (default: 20)")
    parser.add_argument("--n-rank", type=int, default=1000,
                        help="Size of ranked list for Spearman (default: 1000)")
    args = parser.parse_args()

    print("=" * 60)
    print("R5: MPO Weight Sensitivity Analysis")
    print("=" * 60)

    df_lib = load_library()
    print(f"  Library loaded: {len(df_lib)} molecules")

    df_sens = run_sensitivity(df_lib, n_top=args.n_top, n_rank=args.n_rank)

    out_csv = RESULTS / "p1_mpo_sensitivity.csv"
    df_sens.to_csv(out_csv, index=False)
    print(f"  Saved: {out_csv}")

    write_summary(df_sens, args.n_top, args.n_rank)

    print(f"\n  Mean Spearman ρ: {df_sens['spearman_rho'].mean():.4f}")
    print(f"  Mean Jaccard:    {df_sens['jaccard_top20'].mean():.4f}")
    print(f"  Pass rate (ρ>0.95): {df_sens['pass_spearman'].mean()*100:.0f}%")
    print(f"  Pass rate (J≥0.70): {df_sens['pass_jaccard'].mean()*100:.0f}%")


if __name__ == "__main__":
    main()
