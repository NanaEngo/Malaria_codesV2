#!/usr/bin/env python3
"""
DEKOIS v2 ROC-AUC computation
==============================
Extracts VINA docking scores from Meeko-uniform .docked.pdbqt files
(40 actives, 1200 decoys) and computes ROC-AUC with bootstrap 95% CI
and enrichment factors.

Usage:
    python scripts/compute_dekois_auc.py \
        --actives-dir results/v2_dekois/actives \
        --decoys-dir results/v2_dekois/decoys \
        --output results/v2_dekois/dekois_v2_roc_auc.csv
"""
import argparse
import csv
import glob
import os
import sys

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.utils import resample


def score_from_pdbqt(path: str):
    """Extract the first (best) VINA RESULT docking score from a docked PDBQT file.
    
    Vina outputs modes from best to worst. We take the first (most negative)
    mode, which is the correct choice for AUC/EF computation (best predicted
    binding affinity per ligand).
    
    Line format:  REMARK VINA RESULT:    -9.5      0.000      0.000
    split()[0]=REMARK, [1]=VINA, [2]=RESULT:, [3]=score
    """
    try:
        with open(path) as fh:
            for line in fh:
                if "VINA RESULT" in line:
                    return float(line.strip().split()[3])
    except (FileNotFoundError, OSError, ValueError, IndexError) as e:
        print(f"  [WARN] Could not parse {path}: {e}", file=sys.stderr)
    return None


def main():
    parser = argparse.ArgumentParser(description="DEKOIS v2 ROC-AUC computation")
    parser.add_argument(
        "--actives-dir",
        default="results/v2_dekois/actives",
        help="Directory containing docked active PDBQT files",
    )
    parser.add_argument(
        "--decoys-dir",
        default="results/v2_dekois/decoys",
        help="Directory containing docked decoy PDBQT files",
    )
    parser.add_argument(
        "--output",
        default="results/v2_dekois/dekois_v2_roc_auc.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for bootstrap resampling",
    )
    args = parser.parse_args()

    # Resolve paths relative to script location or absolute
    for d in [args.actives_dir, args.decoys_dir]:
        if not os.path.isdir(d):
            print(f"ERROR: directory not found: {d}", file=sys.stderr)
            sys.exit(1)

    # --- Extract scores ---
    active_files = sorted(glob.glob(os.path.join(args.actives_dir, "*.docked.pdbqt")))
    decoy_files = sorted(glob.glob(os.path.join(args.decoys_dir, "*.docked.pdbqt")))

    print(f"Found {len(active_files)} actives, {len(decoy_files)} decoys")

    act_scores = [score_from_pdbqt(f) for f in active_files]
    dec_scores = [score_from_pdbqt(f) for f in decoy_files]

    # Remove None (failed parses)
    act_valid = [s for s in act_scores if s is not None]
    dec_valid = [s for s in dec_scores if s is not None]

    print(f"Valid scores: {len(act_valid)} actives, {len(dec_valid)} decoys")
    if len(act_valid) == 0:
        print("ERROR: no valid active scores", file=sys.stderr)
        sys.exit(1)

    # --- ROC-AUC ---
    # y_score negated: Vina scores are more negative = better binding,
    # so -score gives higher = better (required by roc_auc_score convention)
    y_true = [1] * len(act_valid) + [0] * len(dec_valid)
    y_score = [-s for s in act_valid + dec_valid]

    auc = roc_auc_score(y_true, y_score)

    # Bootstrap 95% CI (1000 resamples)
    np.random.seed(args.seed)
    boot_aucs = []
    for _ in range(1000):
        act_boot = resample(act_valid, replace=True, n_samples=len(act_valid))
        dec_boot = resample(dec_valid, replace=True, n_samples=len(dec_valid)) if dec_valid else []
        bt_true = [1] * len(act_boot) + [0] * len(dec_boot)
        bt_score = [-s for s in act_boot + dec_boot]
        if len(set(bt_true)) == 2:  # both classes present
            boot_aucs.append(roc_auc_score(bt_true, bt_score))
    ci_low = float(np.percentile(boot_aucs, 2.5))
    ci_high = float(np.percentile(boot_aucs, 97.5))

    # Enrichment factors
    scores = list(act_valid) + list(dec_valid)
    labels = [1] * len(act_valid) + [0] * len(dec_valid)
    n_total = len(scores)

    # Sort by score ascending (more negative = better binding)
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    sorted_labels = [p[1] for p in pairs]
    n_actives_total = sum(sorted_labels)

    def enrichment_factor(percent):
        k = max(1, int(n_total * percent / 100))
        top_k = sorted_labels[:k]
        n_actives_top = sum(top_k)
        if n_actives_total == 0:
            return 0.0
        expected = n_actives_total / n_total if n_total > 0 else 1.0
        observed = n_actives_top / k
        return observed / expected if expected > 0 else 0.0

    ef1 = enrichment_factor(1)
    ef5 = enrichment_factor(5)
    ef10 = enrichment_factor(10)
    ef20 = enrichment_factor(20)

    # Score statistics
    act_mean = float(np.mean(act_valid))
    act_std = float(np.std(act_valid, ddof=0))  # population std (full benchmark)
    dec_mean = float(np.mean(dec_valid)) if dec_valid else 0.0
    dec_std = float(np.std(dec_valid, ddof=0)) if dec_valid else 0.0

    # --- Output ---
    print()
    print("=" * 60)
    print(" DEKOIS v2 PfDHFR - Meeko-uniform pipeline")
    print("=" * 60)
    print(f"  ROC-AUC:             {auc:.4f}")
    print(f"  95% CI:              [{ci_low:.4f}, {ci_high:.4f}]")
    print(f"  EF 1%:               {ef1:.4f}")
    print(f"  EF 5%:               {ef5:.4f}")
    print(f"  EF 10%:              {ef10:.4f}")
    print(f"  EF 20%:              {ef20:.4f}")
    print(f"  n_bootstrap:         1000")
    print(f"  Random seed:         {args.seed}")
    print("=" * 60)
    print(f"  Actives: {len(act_valid)} / {len(active_files)} docked successfully")
    print(f"    Mean Vina score:   {act_mean:.3f} +/- {act_std:.3f} kcal/mol")
    print(f"    Min:               {min(act_valid):.3f} kcal/mol")
    print(f"    Max:               {max(act_valid):.3f} kcal/mol")
    print(f"  Decoys: {len(dec_valid)} / {len(decoy_files)} docked successfully")
    print(f"    Mean Vina score:   {dec_mean:.3f} +/- {dec_std:.3f} kcal/mol")
    print(f"    Min:               {min(dec_valid):.3f} kcal/mol")
    print(f"    Max:               {max(dec_valid):.3f} kcal/mol")
    if dec_valid:
        print(f"  Score separation:   {abs(act_mean - dec_mean):.3f} kcal/mol")
    print("=" * 60)

    # --- Save CSV ---
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["roc_auc", f"{auc:.6f}"])
        writer.writerow(["roc_auc_ci_low", f"{ci_low:.6f}"])
        writer.writerow(["roc_auc_ci_high", f"{ci_high:.6f}"])
        writer.writerow(["ef_1pct", f"{ef1:.6f}"])
        writer.writerow(["ef_5pct", f"{ef5:.6f}"])
        writer.writerow(["ef_10pct", f"{ef10:.6f}"])
        writer.writerow(["ef_20pct", f"{ef20:.6f}"])
        writer.writerow(["n_bootstrap", "1000"])
        writer.writerow(["bootstrap_seed", str(args.seed)])
        writer.writerow(["n_actives_total", len(active_files)])
        writer.writerow(["n_actives_valid", len(act_valid)])
        writer.writerow(["n_decoys_total", len(decoy_files)])
        writer.writerow(["n_decoys_valid", len(dec_valid)])
        writer.writerow(["actives_mean", f"{act_mean:.4f}"])
        writer.writerow(["actives_std", f"{act_std:.4f}"])
        writer.writerow(["decoys_mean", f"{dec_mean:.4f}"])
        writer.writerow(["decoys_std", f"{dec_std:.4f}"])

    print(f"\nResults saved -> {args.output}")
    sys.exit(0)


if __name__ == "__main__":
    main()
