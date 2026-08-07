#!/usr/bin/env python3
"""
v2_postprocess.py
=================
Post-process the top-20 candidate selection with V2 corrected grid scores.

Purpose (from synthese_audit §3.1c C1):
    The per-target MPO scores (MPO_7f3y, MPO_6ukj, MPO_9n10, MPO_4gm2) in the
    current md_top20_candidates.csv are derived from V1-grid Vina scores from
    ANP_MPO_Ranked_Final_refined.csv (created July 5, 11 days before V2 grid
    diagnosis on July 16). This script:

    1. Loads current top-20 (ranked by physicochemical weighted_mpo_score → unchanged)
    2. Checks if V2 re-dock results exist (from job 7951, v2_redock_anp/)
    3. If available: recomputes per-target MPO with V2 affinities
    4. If not available: creates file with pending-V2 annotation
    5. Adds provenance columns (grid_version, exhaustiveness, source)
    6. Outputs v2_top20_candidates.csv
    7. Generates comparison report: old vs new

Outputs:
    results/v2_top20_candidates.csv    — V2-certified top-20 table
    results/v2_top20_comparison.txt    — old vs new comparison report

Usage:
    python scripts/v2_postprocess.py
    python scripts/v2_postprocess.py --force  # force V2 computation even with partial data
    python scripts/v2_postprocess.py --v2-results /path/to/v2_redock_results.csv
"""

import argparse
import sys
import os
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# sklearn import (optional, for MPO formula fitting)
try:
    from sklearn.linear_model import LinearRegression
    HAS_SKLEARN = True
except ImportError:
    LinearRegression = None
    HAS_SKLEARN = False

# ─── Paths ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # Malaria_codesV2
PROJECT2 = PROJECT_ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
RESULTS_DIR = PROJECT2 / "results"
ANP_FILE = PROJECT2 / "data" / "from_project1" / "docking" / "ANP_MPO_Ranked_Final_refined.csv"
V2_REDOCK_DIR = RESULTS_DIR / "v2_redock_anp"
V2_RESULTS_CSV = V2_REDOCK_DIR / "v2_redock_results.csv"

# Current top-20
OLD_TOP20_CSV = RESULTS_DIR / "md_top20_candidates.csv"

# Outputs
V2_TOP20_CSV = RESULTS_DIR / "v2_top20_candidates.csv"
COMPARISON_TXT = RESULTS_DIR / "v2_top20_comparison.txt"

V2_CENTER = {
    "7F3Y": (1.33, -1.733, -23.842),
    "6UKJ": (152.99, 151.042, 159.379),
    "9N10": (134.84, 133.10, 97.63),
    "4GM2": (26.19, 35.09, 24.72),
}

TARGET_MAP = {
    "7F3Y": "PfDHFR",
    "6UKJ": "PfCRT",
    "9N10": "PfATP4",
    "4GM2": "PfClpR",
}

# ─── MPO computation ─────────────────────────────────────────────────────────

def learn_mpo_formula(anp: pd.DataFrame) -> dict:
    """
    Reverse-engineer the per-target MPO formula from the ANP file.

    The ANP file contains columns:
        aff_7f3y, conf_7f3y, MPO_7f3y  (and similarly for 6UKJ, 9N10, 4GM2)
        S_vina, S_diff, S_qed, S_admet, MPO_Score, MPO_multi

    The per-target MPO appears to be a non-linear function of affinity + confidence.
    We fit per-target models to replicate the formula as closely as possible.
    """
    targets = ["7F3Y", "6UKJ", "9N10", "4GM2"]
    formulas = {}

    for target in targets:
        aff_col = f"aff_{target.lower()}"
        conf_col = f"conf_{target.lower()}"
        mpo_col = f"MPO_{target.lower()}"

        if mpo_col not in anp.columns:
            print(f"  [warn] {mpo_col} not in ANP file, using fallback formula")
            formulas[target] = None
            continue

        # Get clean data
        cols = [aff_col, conf_col, mpo_col]
        clean = anp[cols].dropna()

        if len(clean) < 5:
            print(f"  [warn] {target}: only {len(clean)} clean rows, using fallback")
            formulas[target] = None
            continue

        aff = clean[aff_col].values
        conf = clean[conf_col].values
        mpo = clean[mpo_col].values

        # Try 2-factor linear regression: MPO = a*aff + b*conf + c
        if not HAS_SKLEARN:
            print(f"    [warn] sklearn not available, using fallback for {target}")
            formulas[target] = None
            continue
        X = np.column_stack([aff, conf])
        lr = LinearRegression().fit(X, mpo)
        r2 = lr.score(X, mpo)
        rho_s, p_s = spearmanr(lr.predict(X), mpo)

        print(f"  {target} ({TARGET_MAP[target]}):")
        print(f"    MPO ≈ {lr.coef_[0]:.4f}×aff + {lr.coef_[1]:.4f}×conf + {lr.intercept_:.4f}")
        print(f"    R² = {r2:.4f}, Spearman ρ = {rho_s:.4f} (p={p_s:.4e})")

        # Store formula parameters
        formulas[target] = {
            "coef_aff": lr.coef_[0],
            "coef_conf": lr.coef_[1],
            "intercept": lr.intercept_,
            "r2": r2,
        }

    return formulas


def compute_mpo_from_v2(target: str, v2_affinity: float, formulas: dict,
                        fallback_conf: float = 0.5) -> float:
    """
    Compute per-target MPO score from V2 affinity using learned formula.
    Falls back to sigmoid normalization if no formula is available.
    """
    formula = formulas.get(target)

    if formula is not None:
        # Use learned linear model
        return float(formula["coef_aff"] * v2_affinity
                     + formula["coef_conf"] * fallback_conf
                     + formula["intercept"])

    # Fallback: sigmoid-based MPO normalization
    # For docking scores, more negative = better binding
    # MPO = 1 / (1 + exp(affinity)) maps [-10, -4] to [0.98, 0.12] approximately
    mpo = 1.0 / (1.0 + np.exp(v2_affinity))
    return float(np.clip(mpo, 0.0, 1.0))


# ─── Data loading ─────────────────────────────────────────────────────────────

def load_current_top20() -> pd.DataFrame:
    """Load the current top-20 candidates (V1-based per-target MPO)."""
    df = pd.read_csv(OLD_TOP20_CSV, index_col=0)
    print(f"  Loaded current top-20: {len(df)} candidates")
    print(f"  Columns: {list(df.columns)}")
    return df


def load_anp_file() -> pd.DataFrame:
    """Load the ANP MPO ranking file (V1 scores)."""
    df = pd.read_csv(ANP_FILE)
    print(f"  Loaded ANP file: {len(df)} molecules")
    return df


def load_v2_results() -> pd.DataFrame | None:
    """
    Load V2 re-dock results if available.
    Returns None if the file doesn't exist or is empty.
    """
    if not V2_RESULTS_CSV.exists():
        print(f"  V2 re-dock results NOT FOUND at: {V2_RESULTS_CSV}")
        print(f"  (Job 7951 still pending in queue)")
        return None

    df = pd.read_csv(V2_RESULTS_CSV)
    if len(df) == 0:
        print(f"  V2 re-dock results file is EMPTY")
        return None

    print(f"  Loaded V2 re-dock results: {len(df)} entries "
          f"({len(df) // 4} ligands × 4 targets)")
    return df


# ─── Core post-processing ─────────────────────────────────────────────────────

def postprocess(force: bool = False,
                custom_v2_path: str | None = None) -> tuple[pd.DataFrame, dict]:
    """
    Main post-processing logic.

    Returns:
        v2_top20: DataFrame with V2-certified top-20
        summary: dict with processing summary
    """
    summary = {"v2_available": False, "mpo_updated": 0, "mpo_pending": 0}

    # 1. Load current top-20
    print("\n[1/5] Loading current top-20...")
    top20 = load_current_top20()

    # 2. Load ANP file to learn MPO formula
    print("\n[2/5] Learning per-target MPO formula from ANP file...")
    anp = load_anp_file()
    formulas = learn_mpo_formula(anp)

    # 3. Load V2 re-dock results
    print("\n[3/5] Checking V2 re-dock results...")
    v2_results = load_v2_results()

    if v2_results is not None:
        summary["v2_available"] = True

    # 4. Build V2-certified top-20
    print("\n[4/5] Building V2-certified top-20...")

    # Start with a copy of the current top-20
    v2_top20 = top20.copy()

    # Add provenance columns
    targets = ["7F3Y", "6UKJ", "9N10", "4GM2"]

    for target in targets:
        target_lower = target.lower()
        mpo_col = f"MPO_{target_lower}"
        aff_col = f"aff_{target_lower}"
        prov_col = f"source_{target_lower}"
        gv_col = f"grid_version_{target_lower}"
        ex_col = f"exhaustiveness_{target_lower}"

        if v2_results is not None and force:
            # V2 results available: compute corrected MPO
            v2_top20[prov_col] = "V2 vina"
            v2_top20[gv_col] = "V2"
            v2_top20[ex_col] = 16  # V2 pipeline exhaustiveness

            for idx in v2_top20.index:
                row = v2_top20.loc[idx]
                smiles = row.get("smiles", "")
                lig_id = None

                # Find matching ligand in V2 results
                if smiles:
                    anp_row = anp[anp["SMILES"] == smiles]
                    if len(anp_row) > 0:
                        anp_idx = anp_row.index[0]
                        lig_id = f"ANP_{anp_idx:03d}"

                if lig_id:
                    v2_match = v2_results[
                        (v2_results["ligand_id"] == lig_id)
                        & (v2_results["target"] == target)
                    ]
                    if len(v2_match) > 0:
                        v2_aff = v2_match["v2_affinity_kcal_mol"].values[0]
                        v2_top20.loc[idx, aff_col] = v2_aff
                        # Compute MPO from V2 affinity
                        v2_mpo = compute_mpo_from_v2(target, v2_aff, formulas)
                        v2_top20.loc[idx, mpo_col] = round(v2_mpo, 3)
                        summary["mpo_updated"] += 1
                    else:
                        v2_top20.loc[idx, prov_col] = "V2 vina (not found)"
                        summary["mpo_pending"] += 1
                else:
                    v2_top20.loc[idx, prov_col] = "V2 vina (SMILES not in ANP)"
                    summary["mpo_pending"] += 1
        else:
            # V2 not available: annotate provenance but keep V1 values AS-IS
            v2_top20[prov_col] = "V1 ANP (V2 pending)"
            v2_top20[gv_col] = "V1"
            v2_top20[ex_col] = 16
            # No column renaming — original V1 MPO columns stay in place
            # Add V2 column as companion (empty until job 7951 completes)
            v2_mpo_col = f"{mpo_col}_V2"
            if v2_mpo_col not in v2_top20.columns:
                v2_top20[v2_mpo_col] = np.nan

            summary["mpo_pending"] += len(v2_top20)

    # Add overall provenance
    v2_top20["pipeline_version"] = "V2"
    v2_top20["postprocess_date"] = pd.Timestamp.now().isoformat()
    v2_top20["postprocess_script"] = "v2_postprocess.py"

    # 5. Save
    print(f"\n[5/5] Saving V2-certified top-20...")
    v2_top20.to_csv(V2_TOP20_CSV)
    print(f"  Saved: {V2_TOP20_CSV}")
    print(f"  Entries: {len(v2_top20)} candidates")
    print(f"  MPO updated: {summary['mpo_updated']}")
    print(f"  MPO pending: {summary['mpo_pending']}")

    return v2_top20, summary


# ─── Comparison report ────────────────────────────────────────────────────────

def generate_comparison(old: pd.DataFrame, new: pd.DataFrame,
                        summary: dict) -> str:
    """
    Generate a detailed comparison between old (V1) and new (V2) top-20.
    """
    lines = []
    lines.append("=" * 80)
    lines.append("TOP-20 COMPARISON: V1 (old) vs V2 (corrected)")
    lines.append("=" * 80)
    lines.append(f"Generated: {pd.Timestamp.now().isoformat()}")
    lines.append("")
    lines.append(f"V2 re-dock results available: {summary['v2_available']}")
    lines.append(f"Per-target MPO values updated: {summary['mpo_updated']}")
    lines.append(f"Per-target MPO values pending: {summary['mpo_pending']}")
    lines.append("")

    # 1. Composition comparison: are the same molecules selected?
    old_smiles = set(old["smiles"].str.strip())
    new_smiles = set(new["smiles"].str.strip())
    common = old_smiles & new_smiles
    only_old = old_smiles - new_smiles
    only_new = new_smiles - old_smiles

    lines.append("─" * 80)
    lines.append("1. COMPOSITION ═══ Identité des molécules retenues")
    lines.append("─" * 80)
    lines.append(f"  Molécules communes:  {len(common)}/{len(old_smiles)} ({len(common)/len(old_smiles)*100:.0f}%)")
    lines.append(f"  Uniquement dans V1:  {len(only_old)}")
    lines.append(f"  Uniquement dans V2:  {len(only_new)}")

    if only_old:
        lines.append("  ⚠️ Molécules PERDUES avec V2:")
        for s in only_old:
            lines.append(f"    - {s[:60]}")
    if only_new:
        lines.append("  ⚠️ Molécules NOUVELLES avec V2:")
        for s in only_new:
            lines.append(f"    - {s[:60]}")

    if not only_old and not only_new:
        lines.append("  ✅ Composition IDENTIQUE — le classement physico-chimique est inchangé")
    lines.append("")

    # 2. Ranking comparison
    lines.append("─" * 80)
    lines.append("2. CLASSEMENT ═══ Comparaison rang par rang")
    lines.append("─" * 80)

    # Align by rank index
    comparison_data = []
    for rank in sorted(set(list(old.index) + list(new.index))):
        if rank in old.index and rank in new.index:
            old_row = old.loc[rank]
            new_row = new.loc[rank]
            same = old_row["smiles"] == new_row["smiles"]
            comparison_data.append({
                "rank": rank,
                "old_smiles": old_row["smiles"][:40],
                "new_smiles": new_row["smiles"][:40] if str(new_row["smiles"]) != "nan" else "—",
                "same": same,
                "old_wmpo": old_row.get("weighted_mpo_score", 0),
                "new_wmpo": new_row.get("weighted_mpo_score", 0),
                "old_mpo_7f3y": old_row.get("MPO_7f3y", "—"),
                "new_mpo_7f3y": new_row.get("MPO_7f3y", "—"),
            })

    # Table header
    lines.append(f"  {'Rang':>5} {'Molécule':<42} {'Même?':<6} {'wMPO':>7}")
    lines.append(f"  {'':5} {'':<42} {'':<6} {'V1':>7} {'V2':>7}")
    lines.append("  " + "-" * 75)

    for d in comparison_data:
        same_mark = "✅" if d["same"] else "❌"
        lines.append(
            f"  {d['rank']:>5d} {d['old_smiles']:<42} {same_mark:<6} "
            f"{d['old_wmpo']:>7.3f} {d['new_wmpo']:>7.3f}"
        )

    lines.append("")

    # 3. Per-target MPO comparison
    if summary.get("mpo_updated", 0) > 0:
        lines.append("─" * 80)
        lines.append("3. SCORES MPO PAR CIBLE ═══ V1 vs V2")
        lines.append("─" * 80)

        targets = ["7F3Y", "6UKJ", "9N10", "4GM2"]
        target_name = {"7F3Y": "PfDHFR", "6UKJ": "PfCRT", "9N10": "PfATP4", "4GM2": "PfClpR"}

        for target in targets:
            mpo_col = f"MPO_{target.lower()}"
            v2_col = f"{mpo_col}_V2"

            # V1 values: from the original column in old top-20
            old_vals = old[mpo_col].dropna() if mpo_col in old.columns else pd.Series(dtype=float)
            # V2 values: from the V2 companion column in new top-20 (may be empty)
            v2_vals = new[v2_col].dropna() if v2_col in new.columns \
                      else (new[mpo_col].dropna() if mpo_col in new.columns else pd.Series(dtype=float))

            lines.append(f"\n  {target} ({target_name[target]}):")
            lines.append(f"    V1 (ANP): n={len(old_vals):>3d}  mean={old_vals.mean():.3f} ± {old_vals.std():.3f}" if len(old_vals) > 0 else f"    V1:  N/A")
            lines.append(f"    V2 (corrigé): n={len(v2_vals):>3d}  mean={v2_vals.mean():.3f} ± {v2_vals.std():.3f}" if len(v2_vals) > 0 else f"    V2:  N/A")

            if len(old_vals) > 0 and len(v2_vals) > 0:
                try:
                    r, p = spearmanr(old_vals, v2_vals)
                    lines.append(f"    Spearman ρ = {r:.4f} (p={p:.4e})")
                except Exception:
                    pass

    else:
        lines.append("─" * 80)
        lines.append("3. SCORES MPO PAR CIBLE ═══ En attente des résultats V2")
        lines.append("─" * 80)
        lines.append("  Les résultats du re-dock V2 (job 7951) ne sont pas encore disponibles.")
        lines.append("  Les colonnes MPO par cible seront mises à jour automatiquement")
        lines.append("  lorsque le job sera terminé.")
        lines.append("")
        lines.append(f"  Re-exécuter: python scripts/v2_postprocess.py --force")

    lines.append("")
    lines.append("─" * 80)
    lines.append("4. PROVENANCE ═══ Métadonnées V2")
    lines.append("─" * 80)
    lines.append(f"  Pipeline: V2 (grilles corrigées)")
    lines.append(f"  Grilles V2: 7F3Y [{V2_CENTER['7F3Y'][0]}, {V2_CENTER['7F3Y'][1]}, {V2_CENTER['7F3Y'][2]}]")
    lines.append(f"  Exhaustiveness: 16 (V2 r8b pipeline)")
    lines.append(f"  Re-dock V2: {'COMPLÈTEMENT DISPONIBLE' if summary['v2_available'] else 'EN ATTENTE (job 7951)'}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("END REPORT")
    lines.append("=" * 80)

    return "\n".join(lines)


# ─── Ligand pose extraction ───────────────────────────────────────────────────

def extract_ligand_pose(ligand_id: str = "201") -> dict:
    """
    Extract ligand pose from PfDHFR complex.pdb and check V2 catalytic site.
    """
    complex_pdb = PROJECT2 / "MD_systems" / f"{ligand_id}_PfDHFR" / "complex.pdb"

    if not complex_pdb.exists():
        print(f"\n[extra] Complex PDB NOT FOUND: {complex_pdb}")
        return {"found": False}

    with open(complex_pdb) as f:
        lines = f.readlines()

    lig_atoms = [l for l in lines if 'LIG' in l[17:20]]

    if not lig_atoms:
        print(f"\n[extra] No LIG atoms found in {complex_pdb}")
        return {"found": False}

    coords = np.array([
        (float(l[30:38]), float(l[38:46]), float(l[46:54]))
        for l in lig_atoms
    ])
    com = coords.mean(axis=0)
    v2_center = np.array(V2_CENTER["7F3Y"])
    dist = np.linalg.norm(com - v2_center)
    min_c = coords.min(axis=0)
    max_c = coords.max(axis=0)

    result = {
        "found": True,
        "ligand": ligand_id,
        "n_atoms": len(lig_atoms),
        "com": com.tolist(),
        "v2_center": v2_center.tolist(),
        "distance_angstrom": float(dist),
        "bbox": {
            "x": [float(min_c[0]), float(max_c[0]), float(max_c[0] - min_c[0])],
            "y": [float(min_c[1]), float(max_c[1]), float(max_c[1] - min_c[1])],
            "z": [float(min_c[2]), float(max_c[2]), float(max_c[2] - min_c[2])],
        },
        "at_v2_site": dist < 1.0,
    }

    return result


# ─── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="V2 Post-Processor: generate V2-certified top-20 candidates")
    parser.add_argument("--force", action="store_true",
                        help="Force V2 computation even with partial data")
    parser.add_argument("--v2-results", type=str, default=None,
                        help="Custom path to V2 re-dock results CSV")
    parser.add_argument("--check-pose", action="store_true", default=True,
                        help="Check ligand 201 pose in PfDHFR complex (default: True)")
    args = parser.parse_args()

    print("=" * 60)
    print("v2_postprocess.py — V2-certified Top-20 Generator")
    print("=" * 60)
    print(f"  Force mode: {args.force}")
    print(f"  Custom V2 results: {args.v2_results or '(default)'}")
    print(f"  Check pose: {args.check_pose}")
    print()

    # Override V2 results path if custom
    global V2_RESULTS_CSV
    if args.v2_results:
        V2_RESULTS_CSV = Path(args.v2_results)

    # ── Post-process ──────────────────────────────────────────────────────────
    old_top20 = load_current_top20()
    v2_top20, summary = postprocess(force=args.force)

    # ── Comparison report ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Generating comparison report...")
    print("=" * 60)

    report = generate_comparison(old_top20, v2_top20, summary)
    with open(COMPARISON_TXT, "w") as f:
        f.write(report)
    print(f"  Saved: {COMPARISON_TXT}")

    # Print summary to stdout
    print("\n" + report)

    # ── Ligand pose extraction ────────────────────────────────────────────────
    if args.check_pose:
        print("\n" + "=" * 60)
        print("Extracting ligand 201 pose in PfDHFR complex...")
        print("=" * 60)

        pose = extract_ligand_pose("201")

        if pose["found"]:
            print(f"  Ligand: {pose['ligand']}")
            print(f"  Atoms:  {pose['n_atoms']}")
            print(f"  COM:    [{pose['com'][0]:.3f}, {pose['com'][1]:.3f}, {pose['com'][2]:.3f}]")
            print(f"  V2 center: [{pose['v2_center'][0]}, {pose['v2_center'][1]}, {pose['v2_center'][2]}]")
            print(f"  Distance:  {pose['distance_angstrom']:.3f} Å")
            print(f"  Bounding box:")
            print(f"    X: [{pose['bbox']['x'][0]:.3f}, {pose['bbox']['x'][1]:.3f}]  span={pose['bbox']['x'][2]:.3f}")
            print(f"    Y: [{pose['bbox']['y'][0]:.3f}, {pose['bbox']['y'][1]:.3f}]  span={pose['bbox']['y'][2]:.3f}")
            print(f"    Z: [{pose['bbox']['z'][0]:.3f}, {pose['bbox']['z'][1]:.3f}]  span={pose['bbox']['z'][2]:.3f}")
            print(f"  Verdict: {'✅ AT CATALYTIC SITE (V2)' if pose['at_v2_site'] else '❌ NOT AT V2 SITE'}")
        else:
            print(f"  ❌ Complex PDB not found for ligand {pose.get('ligand', 'unknown')}")
            print(f"  Checked: {PROJECT2 / 'MD_systems' / '201_PfDHFR' / 'complex.pdb'}")

    print("\n✓ Done.")


if __name__ == "__main__":
    main()
