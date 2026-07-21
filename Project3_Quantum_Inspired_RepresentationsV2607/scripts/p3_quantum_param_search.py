#!/usr/bin/env python3
"""
Paper 3 — Quantum Parameter Optimization Search.

Grid search over quantum kernel parameters to find the optimal combination
that maximizes Hybrid descriptor AUC-ROC (RF classifier, 5-fold CV).

Parameters searched:
    - n_repeats:  IQPEmbedding depth        [1, 2, 3, 4, 6]
    - n_kpca:     Kernel PCA components       [5, 10, 20, 30]
    - bond_dim:   Number of qubits (UMAP dim) [4, 6, 8]

Uses the same per-fold QK pipeline as p3_hybrid_benchmark.py but reuses
precomputed fingerprints/embeddings and only evaluates the Hybrid descriptor
(much faster than running the full benchmark for each combination).

Usage:
    python scripts/p3_quantum_param_search.py
    python scripts/p3_quantum_param_search.py --n-mols 500 --n-jobs 1 --block-size 200

Output:
    results/p3_quantum_params_sweep.csv
"""

import argparse
import sys
import time
import warnings
from pathlib import Path

try:
    from tqdm import tqdm
    _HAS_TQDM = True
except ImportError:
    _HAS_TQDM = False

try:
    import jax
    import jax.numpy as jnp
    _HAS_JAX = True
    _JAX_BACKEND = jax.devices()[0].platform  # 'cpu' or 'gpu'
except ImportError:
    _HAS_JAX = False
    _JAX_BACKEND = None

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", DeprecationWarning)

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

import pennylane as qml
from pennylane.kernels import kernel_matrix, closest_psd_matrix

if _HAS_JAX:
    _KERNEL_FN_JAX_CACHE: dict = {}
    def _get_kernel_fn_jax(n_qubits, n_repeats):
        """JIT-compiled kernel function via JAX interface (10-100x faster)."""
        key = (n_qubits, n_repeats)
        if key not in _KERNEL_FN_JAX_CACHE:
            dev_jax = qml.device("lightning.qubit", wires=n_qubits)
            @qml.qnode(dev_jax, interface="jax", diff_method=None)
            def _circuit(x1, x2):
                qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
                qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
                return qml.probs(wires=range(n_qubits))
            # JIT the full matrix computation (vmap over all pairs)
            @jax.jit
            def _mat(X):
                return jax.vmap(
                    lambda x1: jax.vmap(
                        lambda x2: _circuit(x1, x2)[0]
                    )(X)
                )(X)
            _KERNEL_FN_JAX_CACHE[key] = _mat
        return _KERNEL_FN_JAX_CACHE[key]

    def _kernel_matrix_jax(X, n_qubits, n_repeats):
        """Compute full kernel matrix using JAX JIT (10-100x faster than loop)."""
        X_jax = jnp.array(X, dtype=jnp.float32)
        _mat_fn = _get_kernel_fn_jax(n_qubits, n_repeats)
        K_jax = _mat_fn(X_jax)
        return np.array(K_jax, dtype=np.float64)
else:
    def _kernel_matrix_jax(X, n_qubits, n_repeats):  # type: ignore[misc]
        raise RuntimeError("JAX not installed — use _kernel_matrix_with_progress instead")

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

N_FOLDS = 5
ACT_THRESHOLD = 0.5
RF_TREES = 200

# ---------------------------------------------------------------------------
# Data loading (copied from p3_hybrid_benchmark.py for self-containment)
# ---------------------------------------------------------------------------

def load_activity() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_DIR / "eos80ch_malaria_final_activity.csv")
    return df[["input", "asexual_blood_stage"]].dropna().rename(
        columns={"input": "smiles", "asexual_blood_stage": "activity"}
    )


def ecfp4(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


def load_precomputed(smiles_list: list[str],
                     csv_path: Path,
                     prefix: str) -> np.ndarray | None:
    if not csv_path.exists():
        return None
    df = pd.read_csv(csv_path)
    feat_cols = [c for c in df.columns if c.startswith(prefix)]
    if not feat_cols:
        return None
    df = df.set_index("smiles")
    rows = []
    for smi in smiles_list:
        if smi in df.index:
            rows.append(df.loc[smi, feat_cols].values.astype(np.float32))
        else:
            rows.append(np.full(len(feat_cols), np.nan, dtype=np.float32))
    X = np.array(rows)
    col_means = np.nanmean(X, axis=0)
    col_means = np.where(np.isfinite(col_means), col_means, 0.0)
    inds = np.where(~np.isfinite(X))
    X[inds] = np.take(col_means, inds[1])
    return X


# ---------------------------------------------------------------------------
# Chunked kernel matrix (same as p3_hybrid_benchmark)
# ---------------------------------------------------------------------------

_KERNEL_CACHE: dict = {}

def _get_kernel_fn(n_qubits: int, n_repeats: int = 1):
    key = (n_qubits, n_repeats)
    if key not in _KERNEL_CACHE:
        dev = qml.device("lightning.qubit", wires=n_qubits)

        @qml.qnode(dev)
        def _kernel(x1, x2):
            qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
            qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
            return qml.probs(wires=range(n_qubits))

        def _kfn(a, b):
            return float(_kernel(a, b)[0])

        _KERNEL_CACHE[key] = _kfn
    return _KERNEL_CACHE[key]


def _compute_block_task(i0, i1, j0, j1, X_chunk, n_qubits, n_repeats):
    _kfn = _get_kernel_fn(n_qubits, n_repeats)
    return kernel_matrix(X_chunk[i0:i1], X_chunk[j0:j1], _kfn)


def _kernel_matrix_with_progress(X, kernel_fn, desc="Kernel"):
    """Compute symmetric kernel matrix row-by-row with tqdm progress.

    Only computes the upper triangle (i <= j) and mirrors to lower.
    Uses tqdm for real-time progress (ETA, pairs/s) in both SLURM logs
    and interactive terminals. Updates once per row to minimise overhead.
    """
    n = len(X)
    K = np.zeros((n, n), dtype=np.float64)
    total_pairs = n * (n + 1) // 2

    if _HAS_TQDM:
        pbar = tqdm(total=total_pairs, desc=desc, unit="pair", ncols=80)
    else:
        pbar = None
        print(f"    Computing {total_pairs:,} kernel pairs (0/{n} rows)", flush=True)

    for i in range(n):
        Xi = X[i]
        row_pairs = n - i  # pairs in this row (i,i) .. (i,n-1)
        for j in range(i, n):
            val = kernel_fn(Xi, X[j])
            K[i, j] = val
            if i != j:
                K[j, i] = val
        if pbar is not None:
            pbar.update(row_pairs)
        if pbar is None and (i + 1) % 10 == 0:
            done = (i + 1) * n - (i + 1) * i // 2
            print(f"    Row {i+1}/{n}  ({done:,}/{total_pairs:,} pairs)", flush=True)

    if pbar is not None:
        pbar.close()
    if pbar is None:
        print(f"    Row {n}/{n}  ({total_pairs:,}/{total_pairs:,} pairs) \u2014 done", flush=True)

    return K


def _kernel_matrix_chunked(X: np.ndarray,
                           block_size: int = 200,
                           n_jobs: int = 1,
                           n_qubits: int = 8,
                           n_repeats: int = 1) -> np.ndarray:
    # NOTE: joblib process parallelism (loky backend) causes PicklingError
    # on PennyLane StateVectorC128 objects.  Additionally, lightning.qubit
    # uses OpenMP internally for forward passes — running multiple processes
    # each with OpenMP threads causes oversubscription.  Always run
    # sequentially; the quantum kernel itself is the bottleneck, not the
    # matrix assembly.
    if n_jobs > 1:
        warnings.warn(
            "Quantum kernel matrix is computed sequentially "
            "(to avoid PicklingError and OpenMP oversubscription); ignoring n_jobs=%d" % n_jobs
        )
        n_jobs = 1

    n = len(X)
    n_blocks = (n + block_size - 1) // block_size
    block_ranges = [(i * block_size, min((i + 1) * block_size, n))
                    for i in range(n_blocks)]

    tasks = []
    task_idx = []
    for ib, (i0, i1) in enumerate(block_ranges):
        for jb, (j0, j1) in enumerate(block_ranges):
            if ib <= jb:
                tasks.append((i0, i1, j0, j1))
                task_idx.append((ib, jb))

    n_tasks = len(tasks)
    if _HAS_TQDM:
        iterable = tqdm(tasks, desc=f"  QK matrix ({n_blocks}x{n_blocks} blocks)",
                        unit="block", ncols=80)
        results = [_compute_block_task(i0, i1, j0, j1, X, n_qubits, n_repeats)
                   for i0, i1, j0, j1 in iterable]
    else:
        results = []
        for idx, (i0, i1, j0, j1) in enumerate(tasks, start=1):
            print(f"    QK block {idx:4d}/{n_tasks}  (rows {i0}:{i1}, cols {j0}:{j1})...")
            sys.stdout.flush()
            block_result = _compute_block_task(i0, i1, j0, j1, X, n_qubits, n_repeats)
            results.append(block_result)

    K = np.zeros((n, n), dtype=np.float64)
    for (ib, jb), block in zip(task_idx, results):
        i0, i1 = block_ranges[ib]
        j0, j1 = block_ranges[jb]
        K[i0:i1, j0:j1] = block
        if ib != jb:
            K[j0:j1, i0:i1] = block.T
    return K


# ---------------------------------------------------------------------------
# Optimised QK pipeline — precompute kernel ONCE on all data, then
# extract per-fold submatrices (avoids redundant UMAP + kernel 5x).
# ---------------------------------------------------------------------------

def _qk_features_fold(QK_data: dict,
                      tr_idx: np.ndarray,
                      te_idx: np.ndarray,
                      n_kpca: int = 10):
    """Extract fold QK features from precomputed kernel matrix.

    Parameters
    ----------
    QK_data : dict
        Precomputed pipeline output from _precompute_qk_all().
    """
    from sklearn.decomposition import KernelPCA

    K_all_psd = QK_data["K_psd"]
    n_train = len(tr_idx)
    n_kpca_actual = min(n_kpca, n_train - 1)

    # Extract submatrices from precomputed kernel (no recomputation!)
    K_tr = K_all_psd[np.ix_(tr_idx, tr_idx)]
    K_te = K_all_psd[np.ix_(te_idx, tr_idx)]

    kpca = KernelPCA(n_components=n_kpca_actual,
                     kernel="precomputed", copy_X=True, random_state=42)
    qk_tr = kpca.fit_transform(K_tr)
    qk_te = kpca.transform(K_te)

    qk_tr = qk_tr / (qk_tr.std(axis=0, keepdims=True) + 1e-10)
    qk_te = qk_te / (qk_te.std(axis=0, keepdims=True) + 1e-10)

    return qk_tr.astype(np.float32), qk_te.astype(np.float32)


def _precompute_qk_all(X_ecfp,
                       n_qubits=6,
                       n_repeats=1,
                       block_size=200,
                       n_jobs=1):
    """Precompute UMAP + kernel matrix ONCE on all molecules.

    Returns dict with:
        - 'X_q': scaled UMAP coordinates (N x n_qubits)
        - 'K_psd': closest-PSD kernel matrix (N x N)
        - 'time_s': kernel computation time
        - 'times': dict of detailed timing breakdown
    """
    from umap import UMAP

    times = {}

    # --- UMAP ---
    t0 = time.perf_counter()
    reducer = UMAP(n_components=n_qubits, metric="jaccard",
                   random_state=42, n_neighbors=15, min_dist=0.1)
    X_8d = reducer.fit_transform(X_ecfp)
    lo, hi = X_8d.min(axis=0), X_8d.max(axis=0)
    rng = np.where(hi - lo > 0, hi - lo, 1.0)
    X_q = 2.0 * (X_8d - lo) / rng - 1.0
    times["umap"] = time.perf_counter() - t0
    print(f"    UMAP ({n_qubits}d): {times['umap']:.1f}s", flush=True)

    n = len(X_q)
    n_pairs = n * (n + 1) // 2
    print(f"    Kernel: {n}x{n} matrix ({n_pairs:,} upper-triangle pairs)", flush=True)

    # --- Kernel matrix ---
    t1 = time.perf_counter()
    if block_size is not None and n > max(1200, block_size):
        K = _kernel_matrix_chunked(X_q, block_size=block_size,
                                   n_jobs=n_jobs,
                                   n_qubits=n_qubits,
                                   n_repeats=n_repeats)
    else:
        # NOTE: GPU (lightning.gpu / JAX JIT) is 1.3-8x SLOWER than CPU
        # for pair-by-pair kernel evaluation due to GPU launch overhead.
        # Always use CPU (lightning.qubit + upper-triangle loop) for speed.
        _kfn = _get_kernel_fn(n_qubits, n_repeats)
        desc = f"  Kernel ({n_qubits}q, {n_repeats}rep)"
        K = _kernel_matrix_with_progress(X_q, _kfn, desc=desc)
    times["kernel"] = time.perf_counter() - t1
    rate = n_pairs / times["kernel"] if times["kernel"] > 0 else 0
    print(f"    Kernel matrix: {times['kernel']:.1f}s  ({rate:.0f} pairs/s)", flush=True)

    # --- closest PSD ---
    t2 = time.perf_counter()
    K_psd = closest_psd_matrix(K)
    times["closest_psd"] = time.perf_counter() - t2
    print(f"    closest_PSD: {times['closest_psd']:.1f}s", flush=True)

    elapsed = time.perf_counter() - t0
    print(f"    Total precompute: {elapsed:.1f}s", flush=True)
    return {"X_q": X_q, "K_psd": K_psd, "time_s": elapsed, "times": times}


# ---------------------------------------------------------------------------
# Single Hybrid AUC evaluation for one parameter combination
# ---------------------------------------------------------------------------

def evaluate_hybrid(X_ecfp, X_tfp, X_tne, y,
                    n_qubits=8, n_kpca=10, n_repeats=1,
                    block_size=None, n_jobs=1):
    """Return mean AUC (RF, 5-fold) for the Hybrid descriptor.

    Precomputes UMAP + kernel matrix ONCE on all data, then extracts
    per-fold submatrices — avoids 5x redundant kernel recomputation.
    """
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)

    # --- Handle missing precomputed data ---
    n = len(X_ecfp)
    if X_tne is None:
        X_tne = np.zeros((n, 1), dtype=np.float32)
        print("    TNE: not found — using dummy zeros", flush=True)
    if X_tfp is None:
        X_tfp = np.zeros((n, 1), dtype=np.float32)
        print("    TFP: not found — using dummy zeros", flush=True)

    # --- Precompute kernel ONCE on all data ---
    QK_data = _precompute_qk_all(X_ecfp,
                                 n_qubits=n_qubits,
                                 n_repeats=n_repeats,
                                 block_size=block_size,
                                 n_jobs=n_jobs)

    fold_aucs = []
    for fold, (tr_idx, te_idx) in enumerate(skf.split(X_ecfp, y), start=1):
        tf = time.perf_counter()
        # Extract fold QK from precomputed kernel (seconds, not minutes)
        qk_tr, qk_te = _qk_features_fold(QK_data, tr_idx, te_idx, n_kpca=n_kpca)

        tr_parts = [X_tfp[tr_idx], X_tne[tr_idx], qk_tr]
        te_parts = [X_tfp[te_idx], X_tne[te_idx], qk_te]

        X_tr = np.hstack(tr_parts)
        X_te = np.hstack(te_parts)
        y_tr, y_te = y[tr_idx], y[te_idx]

        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        X_te_s = sc.transform(X_te)

        clf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1, random_state=42)
        clf.fit(X_tr_s, y_tr)
        y_prob = clf.predict_proba(X_te_s)[:, 1]
        auc = roc_auc_score(y_te, y_prob) if len(np.unique(y_te)) > 1 else np.nan
        fold_aucs.append(auc)
        t_fold = time.perf_counter() - tf
        print(f"    Fold {fold}: AUC={auc:.4f}  KPCA+RF: {t_fold:.1f}s", flush=True)

    mean_auc = np.mean(fold_aucs)
    std_auc = np.std(fold_aucs)
    print(f"    => Mean AUC = {mean_auc:.4f} +/- {std_auc:.4f}", flush=True)
    return mean_auc, std_auc


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Quantum parameter optimization — grid search for best Hybrid AUC"
    )
    parser.add_argument("--n-mols", type=int, default=200,
                        help="Number of molecules for the search (default: 200)")
    parser.add_argument("--block-size", type=int, default=200,
                        help="Block size for chunked kernel (default: 200)")
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel workers (default: 1; forced to 1 for quantum kernel)")
    parser.add_argument("--output-csv", type=str, default=None,
                        help="Output CSV path (default: results/p3_quantum_params_sweep.csv)")

    parser.add_argument("--n-repeats", type=str, default="1,2,3,4,6",
                        help="Comma-separated IQP repeat counts to search")
    parser.add_argument("--n-kpca", type=str, default="5,10,20,30",
                        help="Comma-separated KPCA component counts to search")
    parser.add_argument("--bond-dim", type=str, default="4,6,8",
                        help="Comma-separated qubit counts (UMAP dims) to search")
    args = parser.parse_args()

    # Parse grid
    n_repeats_list = [int(x) for x in args.n_repeats.split(",")]
    n_kpca_list = [int(x) for x in args.n_kpca.split(",")]
    bond_dim_list = [int(x) for x in args.bond_dim.split(",")]

    total_combos = len(n_repeats_list) * len(n_kpca_list) * len(bond_dim_list)
    print("=" * 70)
    print(f"  Quantum Parameter Optimization | {total_combos} combos × {N_FOLDS} folds each")
    print(f"  Molecules: {args.n_mols}")
    print(f"  n_repeats = {n_repeats_list}")
    print(f"  n_kpca    = {n_kpca_list}")
    print(f"  bond_dim  = {bond_dim_list}")
    print("=" * 70)

    t0 = time.perf_counter()

    # Load data
    print("\n  Loading activity data...")
    act_df = load_activity()
    act_df = act_df.head(args.n_mols)
    smiles_list = act_df["smiles"].tolist()
    y = (act_df["activity"].values >= ACT_THRESHOLD).astype(int)
    print(f"    {len(y)} molecules  (active={y.sum()}, inactive={(y==0).sum()})")

    print("  Computing ECFP4...")
    X_ecfp = ecfp4(smiles_list)

    print("  Loading TFP (enriched)...")
    X_tfp = load_precomputed(smiles_list, RESULTS_DIR / "p3_tda_fingerprints.csv", "H")
    X_tfp_pers = load_precomputed(smiles_list, RESULTS_DIR / "p3_tda_fingerprints.csv", "pers_img_")
    X_tfp_betti = load_precomputed(smiles_list, RESULTS_DIR / "p3_tda_fingerprints.csv", "betti_")
    if X_tfp is not None and X_tfp_pers is not None and X_tfp_betti is not None:
        X_tfp = np.hstack([X_tfp, X_tfp_pers, X_tfp_betti])
        print(f"    TFP enriched: {X_tfp.shape[1]} features")

    print("  Loading TNE...")
    X_tne = load_precomputed(smiles_list, RESULTS_DIR / "p3_tne_embeddings.csv", "tne_")
    print(f"    TNE: {X_tne.shape[1] if X_tne is not None else 'None'} features")

    # Grid search with incremental checkpointing
    print(f"\n  Starting grid search ({total_combos} combinations)...")
    records = []
    out_csv = Path(args.output_csv) if args.output_csv else RESULTS_DIR / "p3_quantum_params_sweep.csv"
    done_log = out_csv.with_suffix(".done.log") if args.output_csv else RESULTS_DIR / "p3_quantum_params_sweep_done.log"

    # Load previously completed combinations from checkpoint
    if out_csv.exists():
        done_df = pd.read_csv(out_csv)
        records = done_df.to_dict("records")
        print(f"  Found checkpoint: {len(records)}/{total_combos} already completed")
        done_set = set()
        for r in records:
            done_set.add((int(r["bond_dim"]), int(r["n_repeats"]), int(r["n_kpca"])))
    else:
        records = []
        done_set = set()

    combo = 0
    for bd in bond_dim_list:
        for nrep in n_repeats_list:
            for nkpca in n_kpca_list:
                combo += 1
                key = (bd, nrep, nkpca)
                if key in done_set:
                    print(f"  [{combo}/{total_combos}] SKIP bond_dim={bd}, n_repeats={nrep}, n_kpca={nkpca} (already done)")
                    continue

                print(f"\n  [{combo}/{total_combos}] bond_dim={bd}, n_repeats={nrep}, n_kpca={nkpca}...")
                t_start = time.perf_counter()

                auc_mean, auc_std = evaluate_hybrid(
                    X_ecfp, X_tfp, X_tne, y,
                    n_qubits=bd, n_kpca=nkpca, n_repeats=nrep,
                    block_size=args.block_size, n_jobs=args.n_jobs,
                )
                elapsed = time.perf_counter() - t_start

                records.append({
                    "bond_dim": bd,
                    "n_repeats": nrep,
                    "n_kpca": nkpca,
                    "auc": round(auc_mean, 4),
                    "auc_std": round(auc_std, 4),
                    "time_s": round(elapsed, 1),
                })
                print(f"    AUC = {auc_mean:.4f} ± {auc_std:.4f}  ({elapsed:.1f}s)")

                # Incremental checkpoint: save after each combination
                pd.DataFrame(records).to_csv(out_csv, index=False)
                with open(done_log, "a") as f:
                    f.write(f"{combo}/{total_combos}: bd={bd} nr={nrep} nk={nkpca} auc={auc_mean:.4f}\n")

    # Final save
    results_df = pd.DataFrame(records)
    results_df.to_csv(out_csv, index=False)

    # Summary
    best_idx = results_df["auc"].idxmax()
    best = results_df.loc[best_idx]
    total_time = time.perf_counter() - t0

    print("\n" + "=" * 70)
    print(f"  GRID SEARCH COMPLETE ({total_combos} combos, {total_time:.0f}s = {total_time/60:.1f}min)")
    print("=" * 70)
    print(f"\n  🏆  BEST PARAMETERS:")
    print(f"       bond_dim  = {best['bond_dim']}")
    print(f"       n_repeats = {best['n_repeats']}")
    print(f"       n_kpca    = {best['n_kpca']}")
    print(f"       AUC       = {best['auc']} ± {best['auc_std']}")
    print(f"\n  Top 5 configurations:")
    top5 = results_df.sort_values("auc", ascending=False).head(5)
    for i, row in top5.iterrows():
        print(f"       {i+1}. bond_dim={int(row['bond_dim'])}, n_repeats={int(row['n_repeats'])}, "
              f"n_kpca={int(row['n_kpca'])} → AUC = {row['auc']:.4f} ± {row['auc_std']:.4f}")
    print(f"\n  Results saved: {out_csv}")

    # Quick analysis: best per parameter
    print(f"\n  📈  Best AUC per bond_dim:")
    for bd in bond_dim_list:
        sub = results_df[results_df["bond_dim"] == bd]
        best_bd = sub.loc[sub["auc"].idxmax()]
        print(f"       bond_dim={bd}: best AUC = {best_bd['auc']:.4f} "
              f"(n_repeats={int(best_bd['n_repeats'])}, n_kpca={int(best_bd['n_kpca'])})")

    print(f"\n  📈  Best AUC per n_repeats:")
    for nr in n_repeats_list:
        sub = results_df[results_df["n_repeats"] == nr]
        best_nr = sub.loc[sub["auc"].idxmax()]
        print(f"       n_repeats={nr}: best AUC = {best_nr['auc']:.4f} "
              f"(bond_dim={int(best_nr['bond_dim'])}, n_kpca={int(best_nr['n_kpca'])})")

    print(f"\n  📈  Best AUC per n_kpca:")
    for nk in n_kpca_list:
        sub = results_df[results_df["n_kpca"] == nk]
        best_nk = sub.loc[sub["auc"].idxmax()]
        print(f"       n_kpca={nk}: best AUC = {best_nk['auc']:.4f} "
              f"(bond_dim={int(best_nk['bond_dim'])}, n_repeats={int(best_nk['n_repeats'])})")


if __name__ == "__main__":
    main()
