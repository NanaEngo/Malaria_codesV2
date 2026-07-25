#!/usr/bin/env python3
"""
P3 — NISQ Deployment: 8-qubit IQPEmbedding kernel on IBM Quantum hardware.

Runs the full P3 quantum kernel benchmark from p3_qks_benchmark.py on real
NISQ hardware via PennyLane → Qiskit → IBM Quantum pipeline.

VERSUS SIMULATOR:
    - p3_qks_benchmark.py: lightning.qubit (classical CPU, ideal noiseless)
    - p3_nisq_deploy.py:    qiskit.remote (IBM Quantum, real NISQ hardware)
    - Compare both to quantify hardware noise degradation

USAGE:
    # 1. Set IBM Quantum token:
    export IBM_QUANTUM_TOKEN="your_token_here"

    # 2. Smoke test first (MANDATORY before 8-qubit):
    python scripts/p3_nisq_smoke_test.py

    # 3. Run full NISQ benchmark (10 molecules, 5-fold CV):
    python scripts/p3_nisq_deploy.py --n-mols 10

    # 4. Run with error mitigation:
    python scripts/p3_nisq_deploy.py --n-mols 10 --resilience 1

    # 5. Compare NISQ vs simulator:
    python scripts/p3_qks_benchmark.py --n-mols 10
    python scripts/p3_nisq_deploy.py --n-mols 10
    diff results/p3_qks_benchmark.csv results/p3_nisq_benchmark.csv

COST ESTIMATE (IBM Quantum Open Plan: 10 min/month free):
    - 2-qubit smoke test:    ~5 seconds
    - 8-qubit kernel (10 mol): ~30-60 seconds per fold × 5 folds ≈ 5 min
    - 8-qubit kernel (50 mol): ~3-5 min per fold × 5 folds ≈ 20 min
    - 8-qubit kernel (100 mol): ~10-15 min per fold × 5 folds ≈ 60 min
    → Start with --n-mols 10 to stay within free tier

NISQ CAVEATS:
    - Gate fidelity: ~99.8% (2-qubit), coherence T1/T2 ~100-300 us
    - Queue times: 10-60 min for open-plan jobs
    - Expect 10-30% AUC degradation vs simulator
    - Our P3 result already shows QK ≈ RBF ≈ Linear (p > 0.05)
"""

import argparse
import gc
import json
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC

import pennylane as qml
from pennylane.kernels import kernel_matrix, target_alignment, closest_psd_matrix

# Import P3 data loading utilities
sys.path.insert(0, str(Path(__file__).parent))
from p3_qks_benchmark import (
    load_dataset, reduce_to_qubits, evaluate_fold,
    rbf_kernel, N_QUBITS, N_FOLDS,
)

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"


# ──────────────────────────────────────────────────────────────────────
# IBM Quantum authentication
# ──────────────────────────────────────────────────────────────────────

def _get_ibm_service():
    """Initialize QiskitRuntimeService."""
    token = os.environ.get("IBM_QUANTUM_TOKEN", "")
    if not token:
        token_file = Path.home() / ".ibm_quantum_token"
        if token_file.exists():
            token = token_file.read_text().strip()
    if not token:
        print("ERROR: IBM Quantum token not found.")
        print("  export IBM_QUANTUM_TOKEN='your_token'")
        print("  or: echo 'your_token' > ~/.ibm_quantum_token")
        print("  Get token: https://quantum.ibm.com/ → Account → API token")
        sys.exit(1)

    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService(channel="ibm_quantum", token=token)


# ──────────────────────────────────────────────────────────────────────
# NISQ kernel function (IBM Quantum backend)
# ──────────────────────────────────────────────────────────────────────

def _make_nisq_kernel_fn(n_qubits: int, service, backend: str,
                         resilience: int = 0, shots: int = 1024):
    """
    Build a PennyLane quantum kernel function using IBM Quantum hardware.

    Uses IQPEmbedding on qiskit.remote device with optional error mitigation.

    Args:
        n_qubits: Number of qubits (8 for P3)
        service: QiskitRuntimeService
        backend: IBM backend name (e.g., 'ibm_brisbane')
        resilience: Error mitigation level (0-2)
        shots: Number of measurement shots

    Returns:
        kernel: callable K(x1, x2) → float
    """
    dev = qml.device(
        "qiskit.remote",
        wires=n_qubits,
        backend=backend,
        service=service,
        shots=shots,
        options={"resilience_level": resilience},
    )

    @qml.qnode(dev)
    def _kernel_circuit(x1, x2):
        qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=1)
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=1)
        return qml.probs(wires=range(n_qubits))

    def kernel(a, b):
        """K(x1, x2) = ground-state probability."""
        return float(_kernel_circuit(a, b)[0])

    return kernel


# ──────────────────────────────────────────────────────────────────────
# NISQ benchmark
# ──────────────────────────────────────────────────────────────────────

def run_nisq_benchmark(
    X: np.ndarray,
    y: np.ndarray,
    service,
    backend: str = "ibm_brisbane",
    resilience: int = 0,
    shots: int = 1024,
    n_jobs: int = 1,
) -> pd.DataFrame:
    """
    5-fold CV benchmark: NISQ kernel vs RBF kernel on IBM Quantum.

    Both use the same [-1, 1] scaled UMAP features as p3_qks_benchmark.py.
    """
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    records = []
    t0_total = time.perf_counter()

    for fold, (tr_idx, te_idx) in enumerate(skf.split(X, y), start=1):
        t0_fold = time.perf_counter()
        print(f"\n  Fold {fold}/{N_FOLDS}...")
        X_tr_raw, X_te_raw = X[tr_idx], X[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]

        # UMAP → scaled features
        X_tr_q, X_te_q = reduce_to_qubits(X_tr_raw, X_te_raw)

        # ── NISQ quantum kernel ─────────────────────────────────
        n_train = len(X_tr_q)
        print(f"    Building NISQ kernel ({n_train}x{n_train}, {n_train**2:,} evals)...")
        print(f"    Backend: {backend} | Shots: {shots} | Resilience: {resilience}")
        print(f"    ⚠️  This will consume IBM Quantum compute time (~{n_train**2 * 0.005:.0f}s)")

        t0_qk = time.perf_counter()
        kernel_fn = _make_nisq_kernel_fn(
            N_QUBITS, service, backend, resilience, shots
        )

        # Compute kernel matrices
        K_tr_q = kernel_matrix(X_tr_q, X_tr_q, kernel_fn)
        K_te_q = kernel_matrix(X_te_q, X_tr_q, kernel_fn)

        # Fix non-PSD
        K_tr_q = closest_psd_matrix(K_tr_q)

        # Target alignment
        try:
            ta_val = float(target_alignment(X_tr_q, y_tr, kernel_fn))
        except Exception:
            ta_val = np.nan

        qk_time = time.perf_counter() - t0_qk
        print(f"    NISQ kernel done in {qk_time:.1f}s | TA: {ta_val:.4f}")

        # Evaluate
        rec_q = evaluate_fold(K_tr_q, K_te_q, y_tr, y_te, "nisq_quantum", ta_val)
        rec_q["fold"] = fold
        rec_q["qk_time_s"] = round(qk_time, 1)
        rec_q["backend"] = backend
        rec_q["shots"] = shots
        rec_q["resilience"] = resilience
        records.append(rec_q)

        # ── RBF baseline (same features) ────────────────────────
        print(f"    RBF: tuning gamma...")
        K_tr_rbf, K_te_rbf, best_gamma = rbf_kernel(X_tr_q, X_te_q, y_train=y_tr)
        print(f"    RBF: best gamma = {best_gamma:.4g}")

        def _rbf_fn(a, b, _g=best_gamma):
            sq = np.sum((a - b) ** 2)
            return np.exp(-_g * sq)

        ta_rbf = float(target_alignment(X_tr_q, y_tr, _rbf_fn))
        rec_rbf = evaluate_fold(K_tr_rbf, K_te_rbf, y_tr, y_te, "rbf", ta_val=ta_rbf)
        rec_rbf["fold"] = fold
        rec_rbf["gamma"] = best_gamma
        records.append(rec_rbf)

        # ── Linear SVM ──────────────────────────────────────────
        clf_lin = SVC(kernel="linear", C=1.0, probability=True, random_state=42)
        clf_lin.fit(X_tr_q, y_tr)
        y_prob_lin = clf_lin.predict_proba(X_te_q)[:, 1]
        y_pred_lin = clf_lin.predict(X_te_q)
        rec_lin = {
            "model": "linear",
            "auc": roc_auc_score(y_te, y_prob_lin) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy": accuracy_score(y_te, y_pred_lin),
            "f1": f1_score(y_te, y_pred_lin, zero_division=0),
            "fold": fold,
        }
        records.append(rec_lin)

        fold_time = time.perf_counter() - t0_fold
        elapsed = time.perf_counter() - t0_total
        eta = (elapsed / fold) * (N_FOLDS - fold) if fold > 0 else 0
        print(f"  Fold {fold} done in {fold_time:.1f}s | ETA: {eta/60:.1f} min")

        # Memory cleanup
        del K_tr_q, K_te_q, X_tr_q, X_te_q, K_tr_rbf, K_te_rbf
        gc.collect()

    return pd.DataFrame(records)


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="P3 NISQ Deploy — 8-qubit IQPEmbedding on IBM Quantum"
    )
    parser.add_argument("--n-mols", type=int, default=10,
                        help="Number of molecules (default: 10; keep small for free tier)")
    parser.add_argument("--backend", type=str, default="ibm_brisbane",
                        help="IBM Quantum backend (default: ibm_brisbane)")
    parser.add_argument("--resilience", type=int, default=0, choices=[0, 1, 2],
                        help="Error mitigation level (default: 0)")
    parser.add_argument("--shots", type=int, default=1024,
                        help="Measurement shots per circuit (default: 1024)")
    parser.add_argument("--simulator", action="store_true",
                        help="Use lightning.qubit simulator (no IBM Quantum)")
    args = parser.parse_args()

    print("=" * 60)
    print("P3 NISQ Deployment — 8-qubit IQPEmbedding on IBM Quantum")
    print("=" * 60)
    print(f"  Molecules: {args.n_mols}")
    print(f"  Backend:   {args.backend}")
    print(f"  Shots:     {args.shots}")
    print(f"  Resilience: {args.resilience}")
    print()

    # Load data
    X, y, _ = load_dataset(args.n_mols)

    # Connect to IBM Quantum (or use simulator)
    if args.simulator:
        print("  MODE: lightning.qubit simulator")
        service = None
        backend = "lightning.qubit"
        # Fall back to simulator-based kernel from p3_qks_benchmark
        print("  Using classical simulator for kernel...")
        from p3_qks_benchmark import run_benchmark
        results = run_benchmark(X, y, n_repeats=1, noise_method=None,
                                checkpoint_path=None, block_size=None, n_jobs=1)
    else:
        print("  Connecting to IBM Quantum...")
        service = _get_ibm_service()
        print(f"  Connected to IBM Quantum")

        # Estimate cost
        n_train_per_fold = int(len(X) * 0.8)
        n_evals_per_fold = n_train_per_fold ** 2 + len(X) * 0.2 * n_train_per_fold
        est_seconds = n_evals_per_fold * 5 * 0.005  # ~5ms per eval
        print(f"  Estimated IBM Quantum time: ~{est_seconds/60:.1f} min")
        if est_seconds / 60 > 8:
            print(f"  ⚠️  WARNING: This may exceed the 10 min/month free tier!")
            print(f"     Reduce --n-mols or increase --shots to stay within budget.")
            if input("  Continue? [y/N] ").lower() != 'y':
                return

        results = run_nisq_benchmark(
            X, y, service, args.backend, args.resilience, args.shots
        )

    # Save results
    out_csv = RESULTS_DIR / "p3_nisq_benchmark.csv"
    results.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # Summary
    print(f"\n{'─' * 60}")
    print("NISQ Benchmark Summary")
    print(f"{'─' * 60}")
    for model in ["nisq_quantum", "rbf", "linear"]:
        sub = results[results["model"] == model]
        if len(sub) == 0:
            continue
        print(f"\n  {model.upper()}:")
        for metric in ["auc", "accuracy", "f1"]:
            vals = sub[metric].dropna()
            if len(vals) > 0:
                print(f"    {metric:<12s} {vals.mean():.4f} ± {vals.std():.4f}")

    # Paired t-tests
    for m1, m2 in [("nisq_quantum", "rbf"), ("nisq_quantum", "linear")]:
        auc1 = results[results["model"] == m1]["auc"].values
        auc2 = results[results["model"] == m2]["auc"].values
        if len(auc1) == len(auc2) == N_FOLDS:
            t_stat, p_val = ttest_rel(auc1, auc2)
            sig = "significant (p<0.05)" if p_val < 0.05 else "not significant"
            print(f"\n  Paired t-test {m1} vs {m2}: t={t_stat:.3f}, p={p_val:.4f} ({sig})")

    print(f"\n{'─' * 60}")
    print("Next steps:")
    print("  1. Compare with classical simulator:")
    print("     python scripts/p3_qks_benchmark.py --n-mols 10")
    print("  2. Check IBM Quantum dashboard: https://quantum.ibm.com/")
    print("  3. If NISQ AUC is 10-30% lower than simulator → expected (hardware noise)")
    print("  4. If NISQ AUC ≈ simulator → quantum kernels are noise-robust at 8 qubits")


if __name__ == "__main__":
    main()
