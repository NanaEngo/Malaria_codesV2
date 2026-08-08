#!/usr/bin/env python3
"""
P3 — External validation of the Quantum Kernel Score (QKS) on the public
ChEMBL malaria IC50/EC50 dataset (22,447 molecules).

This mirrors EXACTLY the canonical QKS benchmark (jobs 12700/12702:
6-qubit IQPEmbedding, n_repeats=1, state-vector kernel, C3 StandardScaler,
SVM with precomputed kernel vs RBF and linear baselines) but on the SAME
public dataset used by:
  - the descriptor external validation (TFP/TNE vs ECFP4, job 12860), and
  - the P5 GNN external validation:
    Project5_GNN_Transformer_DrugDiscovery/results/p5_public_chembl_malaria.csv

Protocol (identical to p3_qks_benchmark.py run at n=19,849, job 12700):
    - ECFP4 (2048-bit) -> UMAP (Jaccard, n_components=6, random_state=42)
      -> [-1, 1] scaling (canonical reduce_to_qubits)
    - per fold: ONE StandardScaler fit on TRAIN, applied + clipped to [-1,1]
      for train AND test (C3 fix — same Hilbert-space embedding for QK, RBF,
      linear)
    - quantum kernel: 6-qubit IQPEmbedding (1 repeat), state-vector
      formulation (validated numerically identical to pairwise, ~1000x
      faster), closest_psd_matrix, SVM(kernel='precomputed')
    - baselines on the SAME scaled features: RBF (gamma tuned by inner CV)
      and linear SVM
    - 5-fold StratifiedKFold(shuffle, random_state=42); paired t-tests on
      per-fold AUC (df=4) + BH-FDR across kernel comparisons

Outputs:
    results/p3_external_validation_qks_benchmark.csv   — per-fold records
    results/p3_external_validation_qks_summary.txt     — summary + tests
    results/p3_external_validation_qks_report.json     — machine-readable
    results/p3_external_validation_qks_ckpt.json       — fold checkpoint

Usage:
    python scripts/p3_qks_external_validation.py --n-jobs 32 --block-size 200
    python scripts/p3_qks_external_validation.py --limit 150   # smoke test
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", DeprecationWarning)

P3_ROOT = Path(__file__).parent.parent
SCRIPTS = Path(__file__).parent
RESULTS_DIR = P3_ROOT / "results"
sys.path.insert(0, str(SCRIPTS))

from p3_qks_benchmark import (  # noqa: E402  (canonical machinery, pennylane import inside)
    N_QUBITS,
    N_FOLDS,
    run_benchmark,
)

DEFAULT_PUBLIC_CSV = (
    P3_ROOT.parent
    / "Project5_GNN_Transformer_DrugDiscovery"
    / "results"
    / "p5_public_chembl_malaria.csv"
)
ACT_THRESHOLD = 0.5

# Canonical quantum hyperparameters (Phase-2 winning combo, BMAD v51):
#   n_qubits = 6, n_repeats = 1  (C3 fix, jobs 12700/12702)
N_QUBITS = 6
N_REPEATS = 1


def load_public_qks(csv_path: Path, limit: int | None = None):
    """Load the public ChEMBL dataset (same dedup as the descriptor extval).

    Panel = RDKit-parseable molecules with valid ECFP4 (no zero-vector rows).
    Same deterministic dedup + label threshold as p3_external_validation.py.
    """
    from rdkit import Chem
    from rdkit.Chem import rdFingerprintGenerator
    from rdkit.DataStructs import ConvertToNumpyArray

    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["smiles", "activity"])
    df = df.drop_duplicates("smiles").reset_index(drop=True)
    if limit:
        df = df.head(limit)

    _morgan = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps, labels, smiles = [], [], []
    n_fail = 0
    for _, row in df.iterrows():
        mol = Chem.MolFromSmiles(str(row["smiles"]))
        if mol is None:
            n_fail += 1
            continue
        arr = np.zeros(2048, dtype=np.float32)
        ConvertToNumpyArray(_morgan.GetFingerprint(mol), arr)
        fps.append(arr)
        labels.append(int(row["activity"] >= ACT_THRESHOLD))
        smiles.append(str(row["smiles"]))

    X = np.array(fps, dtype=np.float32)
    y = np.array(labels, dtype=int)
    print(f"  Loaded {len(y)} molecules (parse fails {n_fail}, "
          f"active {y.sum()}, inactive {(y == 0).sum()})")
    return X, y, smiles


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR q-values (same as p3_external_validation.py)."""
    pvals = np.asarray(pvals, dtype=float)
    order = np.argsort(pvals)
    m = len(pvals)
    qvals = np.zeros(m)
    for rank, idx in enumerate(order):
        qvals[idx] = min(1.0, pvals[idx] * m / (rank + 1))
    for i in range(m - 2, -1, -1):  # enforce monotonicity
        qvals[order[i]] = min(qvals[order[i]], qvals[order[i + 1]])
    return qvals


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default=str(DEFAULT_PUBLIC_CSV))
    ap.add_argument("--n-jobs", type=int, default=1)
    ap.add_argument("--block-size", type=int, default=None)
    # State-vector kernel is the canonical production path (jobs 12700/12702,
    # validated numerically identical to pairwise, ~1000x faster for n > 500).
    use_state_vector = True
    ap.add_argument("--checkpoint", type=str,
                    default=str(RESULTS_DIR / "p3_external_validation_qks_ckpt.json"))
    ap.add_argument("--limit", type=int, default=None,
                    help="Smoke test on first N molecules")
    args = ap.parse_args()

    t_start = time.perf_counter()
    print("=" * 68)
    print("P3 — QKS external validation on public ChEMBL malaria IC50/EC50")
    print("=" * 68)
    print(f"  Circuit: IQPEmbedding ({N_REPEATS} repeat) | qubits: {N_QUBITS}")
    print(f"  Kernel:  {'state-vector' if use_state_vector else 'pairwise'}")
    print(f"  n_jobs:  {args.n_jobs} | block_size: {args.block_size}")

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: dataset not found: {csv_path}")
        return 1

    X, y, _ = load_public_qks(csv_path, limit=args.limit)

    results = run_benchmark(
        X, y,
        n_repeats=N_REPEATS,
        checkpoint_path=args.checkpoint,
        block_size=args.block_size,
        n_jobs=args.n_jobs,
        state_vector=use_state_vector,
    )

    # ── Save per-fold records ────────────────────────────────────────────
    out_csv = RESULTS_DIR / "p3_external_validation_qks_benchmark.csv"
    results.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # ── Paired stats per model pair + BH-FDR ─────────────────────────────
    models = ["quantum", "rbf", "linear"]
    auc = {m: results.loc[results["model"] == m, "auc"].dropna().values
           for m in models}
    pairs = [("quantum", "rbf"), ("quantum", "linear"), ("rbf", "linear")]
    comps = []
    for m1, m2 in pairs:
        if len(auc[m1]) == len(auc[m2]) and len(auc[m1]) == N_FOLDS:
            t_stat, p_val = stats.ttest_rel(auc[m1], auc[m2])
            comps.append({
                "model_a": m1, "model_b": m2,
                "mean_auc_a": float(auc[m1].mean()),
                "mean_auc_b": float(auc[m2].mean()),
                "paired_t_pvalue": float(p_val),
                "per_fold_a": [round(float(v), 5) for v in auc[m1]],
                "per_fold_b": [round(float(v), 5) for v in auc[m2]],
            })
    if comps:
        qvals = bh_fdr(np.array([c["paired_t_pvalue"] for c in comps]))
        for c, q in zip(comps, qvals):
            c["bh_fdr_qvalue"] = float(q)
            c["significant_at_0.05"] = bool(q < 0.05)

    # ── Cross-reference with the descriptor external validation ──────────
    desc_report = RESULTS_DIR / "p3_external_validation_report.json"
    ecfp4_rf_ext = None
    if desc_report.exists():
        try:
            d = json.loads(desc_report.read_text())
            ecfp4_rf_ext = d.get("descriptor_mean_auc", {}).get("ECFP4")
        except Exception:
            ecfp4_rf_ext = None

    report = {
        "dataset": str(csv_path),
        "n_panel": int(len(y)),
        "n_active": int(y.sum()),
        "n_inactive": int(len(y) - y.sum()),
        "n_qubits": N_QUBITS,
        "n_repeats": N_REPEATS,
        "protocol": "5-fold StratifiedKFold(42), IQPEmbedding state-vector kernel, "
                    "C3 train-only StandardScaler, SVM(precomputed) vs RBF/linear",
        "kernel_mean_auc": {m: float(auc[m].mean()) for m in models},
        "kernel_std_auc": {m: float(auc[m].std()) for m in models},
        "paired_comparisons": comps,
        "ecfp4_rf_external_auc_reference": ecfp4_rf_ext,
        "note": ("ECFP4-RF reference comes from the descriptor external "
                 "validation (RF classifier); QKS arms use SVM — classifier "
                 "differ noted, as in the canonical P3 reporting."),
    }
    out_json = RESULTS_DIR / "p3_external_validation_qks_report.json"
    out_json.write_text(json.dumps(report, indent=2))
    print(f"  Saved: {out_json}")

    # ── Summary text ─────────────────────────────────────────────────────
    lines = [
        "P3 — QKS external validation (public ChEMBL malaria IC50/EC50)",
        f"Circuit: IQPEmbedding ({N_REPEATS} repeats) | {N_QUBITS} qubits | "
        f"{'state-vector' if use_state_vector else 'pairwise'} kernel",
        f"Panel: n={len(y)} (active {y.sum()}, inactive {len(y) - y.sum()})",
        "",
        f"{'Kernel':<10s} {'AUC':>8s} {'±':>7s}",
    ]
    for m in models:
        lines.append(f"{m:<10s} {auc[m].mean():>8.4f} {auc[m].std():>7.4f}")
    lines.append("")
    lines.append("Paired t-test (per-fold, df=4) with BH-FDR:")
    for c in comps:
        lines.append(
            f"  {c['model_a']:<8s} vs {c['model_b']:<8s} "
            f"Δ={c['mean_auc_a'] - c['mean_auc_b']:+.4f} "
            f"p={c['paired_t_pvalue']:.5f} q={c['bh_fdr_qvalue']:.5f} "
            f"{'SIG' if c['significant_at_0.05'] else 'ns'}"
        )
    if ecfp4_rf_ext is not None:
        lines.append("")
        lines.append(f"Reference (descriptor extval, RF): ECFP4 AUC = "
                     f"{ecfp4_rf_ext:.4f} (classifier differs: SVM here)")
    summary = "\n".join(lines)
    print("\n" + summary)
    (RESULTS_DIR / "p3_external_validation_qks_summary.txt").write_text(summary)

    print(f"\nWall time: {time.perf_counter() - t_start:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
