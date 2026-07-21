"""
Paper 3 — QJIT Kernel Benchmark.

Compares PennyLane IQPEmbedding kernel execution time:
    — Standard: QNode on lightning.qubit
    — QJIT compiled: same circuit via pennylane.qjit (if catalyst is compatible)

Measures kernel_matrix() wall time for subset sizes [50, 100, 200, 500]
and reports evaluations/second and speedup ratio.

Usage:
    python scripts/benchmark_qjit.py
    python scripts/benchmark_qjit.py --n-mols 500  --no-qjit
"""

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

warnings.filterwarnings("ignore")

try:
    from umap import UMAP
except ImportError:
    UMAP = None

import pennylane as qml
from pennylane.kernels import kernel_matrix

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
N_QUBITS = 8
ACT_THRESHOLD = 0.5
SUBSET_SIZES = [25, 50, 100]


def load_dataset(n_mols: int) -> np.ndarray:
    """Load ECFP4 fingerprints for n_mols molecules."""
    act = pd.read_csv(RESULTS_DIR / "eos80ch_malaria_final_activity.csv")
    act = act[["input", "asexual_blood_stage"]].dropna()
    if n_mols:
        act = act.head(n_mols)

    fps = []
    for smi in act["input"]:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        arr = np.zeros(2048, dtype=np.float32)
        ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        fps.append(arr)
    return np.array(fps, dtype=np.float32)


def reduce_to_qubits(X: np.ndarray) -> np.ndarray:
    """ECFP4 → 8D UMAP (Jaccard) → [-1,1] scaling."""
    if UMAP is not None:
        reducer = UMAP(n_components=N_QUBITS, metric="jaccard",
                       random_state=42, n_neighbors=15, min_dist=0.1)
        X_8d = reducer.fit_transform(X)
    else:
        from sklearn.decomposition import PCA
        X_8d = PCA(n_components=N_QUBITS, random_state=42).fit_transform(X)
    lo, hi = X_8d.min(axis=0), X_8d.max(axis=0)
    rng = np.where(hi - lo > 0, hi - lo, 1.0)
    return np.clip(2.0 * (X_8d - lo) / rng - 1.0, -1.0, 1.0)


# -----------------------------------------------------------------------
# Kernel implementations
# -----------------------------------------------------------------------

def make_kernel_standard(n_qubits: int = N_QUBITS):
    """Standard PennyLane QNode on lightning.qubit."""
    dev = qml.device("lightning.qubit", wires=n_qubits)

    @qml.qnode(dev)
    def _kernel(x1, x2):
        qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=1)
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=1)
        return qml.probs(wires=range(n_qubits))

    def fn(a, b):
        return float(_kernel(a, b)[0])
    return fn


def make_kernel_qjit(n_qubits: int = N_QUBITS):
    """
    QJIT-compiled kernel via pennylane.qjit.
    Falls back to standard if catalyst is incompatible.
    """
    try:
        from pennylane import qjit as _qjit
    except ImportError:
        return None

    try:
        dev = qml.device("lightning.qubit", wires=n_qubits)

        @qml.qnode(dev)
        def _kernel(x1, x2):
            qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=1)
            qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=1)
            return qml.probs(wires=range(n_qubits))

        compiled = _qjit(_kernel)

        def fn(a, b):
            return float(compiled(a, b)[0])

        # Smoke test: one evaluation to confirm it works
        test_vec = np.zeros(n_qubits, dtype=np.float32)
        _ = fn(test_vec, test_vec)
        print("  [QJIT] Smoke test OK")
        return fn
    except Exception as e:
        print(f"  [QJIT] Unavailable: {e}")
        return None


# -----------------------------------------------------------------------
# Benchmark
# -----------------------------------------------------------------------

def bench_kernel(X: np.ndarray, kernel_fn, label: str) -> dict:
    """Time kernel_matrix() for the given kernel function."""
    n = len(X)
    n_evals = n * n  # kernel_matrix computes full n×n

    t0 = time.perf_counter()
    K = kernel_matrix(X, X, kernel_fn)
    elapsed = time.perf_counter() - t0

    evals_per_sec = n_evals / elapsed if elapsed > 0 else 0.0
    return {
        "method": label,
        "n_mols": n,
        "n_evals": n_evals,
        "wall_time_s": round(elapsed, 4),
        "evals_per_sec": round(evals_per_sec, 1),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-mols", type=int, default=500,
                        help="Max molecules to load (default: 500)")
    parser.add_argument("--no-qjit", action="store_true",
                        help="Skip qjit benchmark (even if available)")
    args = parser.parse_args()

    print("=" * 60)
    print("Paper 3 — QJIT Kernel Benchmark")
    print("=" * 60)

    # Load and prepare data
    print(f"\n  Loading {args.n_mols} molecules...")
    X_efcp = load_dataset(args.n_mols)
    print(f"  ECFP4 matrix: {X_efcp.shape}")

    print("  Reducing to 8D (UMAP + [-1,1] scaling)...")
    X_q = reduce_to_qubits(X_efcp)
    print(f"  QK input: {X_q.shape}")

    # Build kernel functions
    print("\n  Building kernel functions...")
    kernel_std = make_kernel_standard()
    print("  [STANDARD] lightning.qubit QNode ready")

    kernel_qj = None
    if not args.no_qjit:
        kernel_qj = make_kernel_qjit()
    else:
        print("  [QJIT] Skipped (--no-qjit)")

    # Benchmark each subset size
    records = []
    for n_test in SUBSET_SIZES:
        if n_test > len(X_q):
            print(f"\n  Skipping N={n_test} (only {len(X_q)} molecules available)")
            continue

        X_sub = X_q[:n_test]
        print(f"\n  --- N={n_test} ---")

        rec = bench_kernel(X_sub, kernel_std, "standard")
        records.append(rec)
        print(f"  standard: {rec['wall_time_s']:.4f}s  "
              f"({rec['evals_per_sec']:.0f} evals/s)")

        if kernel_qj is not None:
            rec_qj = bench_kernel(X_sub, kernel_qj, "qjit")
            speedup = rec["wall_time_s"] / rec_qj["wall_time_s"]
            rec_qj["speedup_vs_standard"] = round(speedup, 3)
            records.append(rec_qj)
            print(f"  qjit:     {rec_qj['wall_time_s']:.4f}s  "
                  f"({rec_qj['evals_per_sec']:.0f} evals/s)  "
                  f"speedup={speedup:.2f}x")
        else:
            print(f"  qjit:     N/A (catalyst incompatible)")

    # Results table
    df = pd.DataFrame(records)
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for _, row in df.iterrows():
        speedup_str = ""
        if "speedup_vs_standard" in row and not pd.isna(row.get("speedup_vs_standard")):
            speedup_str = f"  speedup={row['speedup_vs_standard']:.2f}x"
        print(f"  {row['method']:<10s}  N={int(row['n_mols']):>3d}  "
              f"{row['wall_time_s']:.4f}s  "
              f"({int(row['evals_per_sec']):>8,d} evals/s){speedup_str}")

    # Summary comparisons
    print("\n  Comparison (standard vs qjit):")
    std_df = df[df["method"] == "standard"].set_index("n_mols")
    if kernel_qj is not None:
        qj_df = df[df["method"] == "qjit"].set_index("n_mols")
        print(f"  {'N':>5s}  {'standard(s)':>12s}  {'qjit(s)':>10s}  {'speedup':>8s}")
        for n in std_df.index:
            if n in qj_df.index:
                s = std_df.loc[n, "wall_time_s"]
                q = qj_df.loc[n, "wall_time_s"]
                print(f"  {int(n):>5d}  {s:>12.4f}  {q:>10.4f}  {s/q:>7.2f}x")
            else:
                print(f"  {int(n):>5d}  {std_df.loc[n, 'wall_time_s']:>12.4f}  {'N/A':>10s}  {'N/A':>8s}")
    else:
        print(f"  qjit baseline not available (catalyst 0.15.0 requires jaxlib==0.7.1, "
              f"installed: jaxlib==0.10.2)")
        print(f"  Standard lightning.qubit baselines established for future comparison.")

    # Save
    out_csv = RESULTS_DIR / "benchmark_qjit.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")


if __name__ == "__main__":
    main()
