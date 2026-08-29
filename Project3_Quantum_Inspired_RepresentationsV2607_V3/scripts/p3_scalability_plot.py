#!/usr/bin/env python3
"""P3 — R15: Scalability benchmark for quantum kernel computation.

Measures wall-clock time for the quantum kernel (IQPEmbedding on
lightning.qubit) as a function of number of molecules, then generates
a publication-quality scalability plot with polynomial fit.

Samples n ∈ {50, 100, 200, 500, 1000, 2000} and records:
    - Total kernel matrix time (including closest_PSD)
    - Pairs per second throughput
    - Memory usage (approximate via gc + timing)

Outputs:
    results/p3_scalability_results.csv   — raw timing data
    results/p3_scalability_plot.png       — publication-quality figure
    results/p3_scalability_fit.txt        — best-fit parameters

Usage:
    python scripts/p3_scalability_plot.py
    python scripts/p3_scalability_plot.py --max-mols 4000 --n-samples 8
    python scripts/p3_scalability_plot.py --n-repeats 2 --quick  (faster, fewer samples)
"""

import gc
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", DeprecationWarning)

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
SCRIPTS_DIR = PROJECT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

N_QUBITS = 6  # Phase-2 optimal: bond_dim=6 (BMAD v51 / Appendix K; was 8)
N_REPEATS = 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_quantum_kernel(n_qubits: int, n_repeats: int = 1):
    """Create a PennyLane quantum kernel function (IQPEmbedding)."""
    import pennylane as qml
    dev = qml.device("lightning.qubit", wires=n_qubits)

    @qml.qnode(dev)
    def _kernel(x1, x2):
        qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
        return qml.probs(wires=range(n_qubits))

    def kfn(a, b):
        return float(_kernel(a, b)[0])
    return kfn


def _sample_molecules(n: int) -> np.ndarray:
    """Load n molecules and reduce to 6-D UMAP features."""
    from p3_qks_benchmark import load_dataset, reduce_to_qubits
    X, y, _ = load_dataset(n)
    # Use first 80% as "training" for consistent measurement
    split = int(n * 0.8)
    X_tr, X_te = X[:split], X[split:]
    del X, y
    gc.collect()
    X_q_tr, _ = reduce_to_qubits(X_tr, X_te, n_components=N_QUBITS)
    del X_te, X_tr
    gc.collect()
    return X_q_tr


def _measure_kernel_time(X: np.ndarray, n_repeats: int = 1,
                          use_chunked: bool = False,
                          block_size: int = 200) -> dict:
    """Measure quantum kernel matrix computation time.

    Returns timing breakdown dict.
    """
    import pennylane as qml
    from pennylane.kernels import kernel_matrix, closest_psd_matrix

    n = len(X)
    n_pairs = n * (n + 1) // 2

    kfn = _make_quantum_kernel(N_QUBITS, n_repeats)

    t0 = time.perf_counter()

    if use_chunked:
        # Use chunked kernel from p3_qks_benchmark
        from p3_qks_benchmark import _kernel_matrix_chunked
        K = _kernel_matrix_chunked(X, block_size=block_size, n_jobs=1,
                                    n_qubits=N_QUBITS, n_repeats=n_repeats)
    else:
        K = kernel_matrix(X, X, kernel=kfn)

    t_kernel = time.perf_counter() - t0

    t1 = time.perf_counter()
    K = closest_psd_matrix(K)
    t_psd = time.perf_counter() - t1

    total = time.perf_counter() - t0
    rate = n_pairs / t_kernel if t_kernel > 0 else 0

    # Cleanup
    del K, kfn
    gc.collect()

    return {
        "n": n,
        "pairs": n_pairs,
        "kernel_time_s": round(t_kernel, 2),
        "psd_time_s": round(t_psd, 2),
        "total_time_s": round(total, 2),
        "pairs_per_s": round(rate, 1),
        "use_chunked": use_chunked,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="P3 — Kernel scalability benchmark")
    parser.add_argument("--max-mols", type=int, default=2000,
                        help="Maximum number of molecules (default: 2000)")
    parser.add_argument("--n-samples", type=int, default=6,
                        help="Number of sample points (default: 6)")
    parser.add_argument("--n-repeats", type=int, default=1,
                        help="IQPEmbedding repeats (default: 1)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: fewer samples, smaller max")
    parser.add_argument("--output", type=str, default=None,
                        help="Output plot path (default: results/p3_scalability_plot.png)")
    args = parser.parse_args()

    if args.quick:
        args.max_mols = 500
        args.n_samples = 4

    # Generate sample sizes on log-like scale
    ns = np.unique(np.logspace(
        np.log10(50), np.log10(args.max_mols), args.n_samples
    ).astype(int)).tolist()
    print(f"  Scalability samples: {ns}")
    print(f"  IQPEmbedding repeats: {args.n_repeats}")

    records = []

    for n in ns:
        t_load = time.perf_counter()
        print(f"\n  n={n} — loading molecules...", end=" ", flush=True)

        try:
            X = _sample_molecules(n)
        except Exception as e:
            print(f"Failed: {e}")
            continue

        load_time = time.perf_counter() - t_load
        print(f"loaded in {load_time:.1f}s  ({X.shape})", flush=True)

        # Direct kernel
        print(f"    Direct kernel...", end=" ", flush=True)
        rec = _measure_kernel_time(X, args.n_repeats, use_chunked=False)
        print(f"{rec['kernel_time_s']:.1f}s  ({rec['pairs_per_s']:.0f} pairs/s)", flush=True)
        records.append(rec)

        # Chunked kernel (only if n > 200)
        if n > 200:
            print(f"    Chunked kernel (bs=200)...", end=" ", flush=True)
            rec_chunked = _measure_kernel_time(
                X, args.n_repeats, use_chunked=True, block_size=200
            )
            print(f"{rec_chunked['kernel_time_s']:.1f}s  ({rec_chunked['pairs_per_s']:.0f} pairs/s)",
                  flush=True)
            records.append(rec_chunked)

        del X
        gc.collect()

    if not records:
        print("No data collected — aborting")
        return

    # Save raw data
    df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "p3_scalability_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # ── Generate plot ──────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")  # non-interactive backend
        import matplotlib.pyplot as plt
        from scipy.optimize import curve_fit

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Left panel: time vs n
        colors = {"direct": "#2196F3", "chunked": "#FF9800"}
        markers = {"direct": "o", "chunked": "s"}

        for method, label in [("direct", "Direct"), ("chunked", "Chunked")]:
            sub = df[df["use_chunked"] == (method == "chunked")]
            if len(sub) < 2:
                continue
            x = sub["n"].values
            y = sub["total_time_s"].values
            ax1.plot(x, y, color=colors[method], marker=markers[method],
                     linestyle="-", linewidth=1.5, markersize=6,
                     label=label)

            # Fit quadratic: t = a * n² + b * n + c
            def _quad(n, a, b, c):
                return a * n ** 2 + b * n + c

            try:
                popt, _ = curve_fit(_quad, x, y, p0=[1e-6, 1e-3, 0])
                n_smooth = np.linspace(x.min(), x.max(), 100)
                ax1.plot(n_smooth, _quad(n_smooth, *popt),
                         color=colors[method], linestyle="--",
                         alpha=0.5, linewidth=1,
                         label=f"{label} fit (a={popt[0]:.2e})")
            except Exception:
                pass

        ax1.set_xlabel("Number of molecules (n)", fontsize=12)
        ax1.set_ylabel("Total time (s)", fontsize=12)
        ax1.set_title("Quantum Kernel Scalability", fontsize=13, fontweight="bold")
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Right panel: pairs/s throughput
        for method, label in [("direct", "Direct"), ("chunked", "Chunked")]:
            sub = df[df["use_chunked"] == (method == "chunked")]
            if len(sub) < 2:
                continue
            ax2.plot(sub["n"], sub["pairs_per_s"],
                     color=colors[method], marker=markers[method],
                     linestyle="-", linewidth=1.5, markersize=6,
                     label=label)

        ax2.set_xlabel("Number of molecules (n)", fontsize=12)
        ax2.set_ylabel("Throughput (pairs/s)", fontsize=12)
        ax2.set_title("Kernel Throughput", fontsize=13, fontweight="bold")
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        out_png = Path(args.output) if args.output else RESULTS_DIR / "p3_scalability_plot.png"
        fig.savefig(out_png, dpi=150, bbox_inches="tight")
        print(f"  Saved: {out_png}")
        plt.close(fig)

    except ImportError as e:
        print(f"  Warning: matplotlib not available — skipping plot ({e})")
    except Exception as e:
        print(f"  Warning: plot generation failed — {e}")

    # Save fit summary
    lines = [
        "P3 — Quantum Kernel Scalability Results",
        f"  Device: lightning.qubit | Qubits: {N_QUBITS} | Repeats: {args.n_repeats}",
        f"  Samples: {ns}",
        "",
    ]
    for _, row in df.iterrows():
        method = "chunked" if row["use_chunked"] else "direct"
        lines.append(
            f"  n={int(row['n']):5d}  {method:8s}  "
            f"kernel={row['kernel_time_s']:7.1f}s  "
            f"psd={row['psd_time_s']:6.1f}s  "
            f"total={row['total_time_s']:7.1f}s  "
            f"rate={row['pairs_per_s']:8.0f} pairs/s"
        )

    summary = "\n".join(lines)
    print("\n" + summary)
    (RESULTS_DIR / "p3_scalability_fit.txt").write_text(summary)
    print(f"  Summary saved: {RESULTS_DIR / 'p3_scalability_fit.txt'}")


if __name__ == "__main__":
    main()
