"""
Paper 3 — Step 4: Quantum Kernel Score (QKS) benchmark.

UPGRADED v2 (July 2026):
  - Circuit: IQPEmbedding (classically-hard data encoding with intrinsic CNOT entanglement)
  - Kernel matrix: pennylane.kernels.kernel_matrix (optimised, replaces nested loop)
  - Metrics: target_alignment added (kernel-label agreement independent of SVM)
  - PSD fix: closest_psd_matrix ensures PSD kernel for SVM
  - Noise: mitigate_depolarizing_noise for realistic simulation

8-qubit circuit (IQPEmbedding):
    IQPEmbedding(x1) → adjoint(IQPEmbedding)(x2)
    → ground-state probability as kernel entry

IQPEmbedding interleaves RZ(arccos(x_i²)) encodings with CNOT entangling layers,
so the adjoint does NOT cancel the CNOTs (data rotations sit between them).
This gives a non-trivial kernel that the original manual circuit could not achieve.

Benchmark:
    SVM with quantum kernel vs SVM with RBF kernel
    5-fold CV on activity labels from eos80ch (asexual_blood_stage)
    Metrics: AUC-ROC, target alignment, accuracy, F1
    Significance: paired t-test across folds

Input features: ECFP4 (2048-bit) reduced to 8 dims via UMAP (Jaccard metric)

Outputs:
    results/p3_qks_benchmark.csv    — per-fold metrics (incl. target alignment)
    results/p3_qks_summary.txt      — summary + significance test

Usage:
    python scripts/p3_qks_benchmark.py
    python scripts/p3_qks_benchmark.py --n-mols 500 --noise depolarizing
    python scripts/p3_qks_benchmark.py --n-mols 1000 --n-repeats 2
    python scripts/p3_qks_benchmark.py --n-mols 3000 --block-size 200 --hpc
"""

import argparse
import gc
import json
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", DeprecationWarning)

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
from scipy.stats import ttest_rel
try:
    from umap import UMAP
except ImportError:
    UMAP = None
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import pennylane as qml
from pennylane.kernels import (
    kernel_matrix,
    target_alignment,
    closest_psd_matrix,
    mitigate_depolarizing_noise,
)

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

N_QUBITS = 8
N_FOLDS = 5
ACT_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_dataset(n_mols: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Load molecules + binary activity labels."""
    act = pd.read_csv(RESULTS_DIR / "eos80ch_malaria_final_activity.csv")
    act = act[["input", "asexual_blood_stage"]].dropna().rename(
        columns={"input": "smiles", "asexual_blood_stage": "activity"}
    )
    if n_mols:
        act = act.head(n_mols)

    fps, labels, smiles = [], [], []
    for _, row in act.iterrows():
        mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None:
            continue
        arr = np.zeros(2048, dtype=np.float32)
        ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        fps.append(arr)
        labels.append(int(row["activity"] >= ACT_THRESHOLD))
        smiles.append(row["smiles"])

    X = np.array(fps, dtype=np.float32)
    y = np.array(labels, dtype=int)
    print(f"  Loaded {len(y)} molecules  (active: {y.sum()}, inactive: {(y == 0).sum()})")
    return X, y, smiles


def reduce_to_qubits(X_train: np.ndarray, X_test: np.ndarray,
                     n_components: int = N_QUBITS) -> tuple[np.ndarray, np.ndarray]:
    """UMAP (Jaccard metric) + [-1, 1] scaling. Same features for both QK and RBF.

    Returns:
        X_tr_scaled, X_te_scaled: [-1, 1] scaled UMAP features (for QK AND RBF)
    """
    if UMAP is not None:
        reducer = UMAP(n_components=n_components, metric="jaccard",
                       random_state=42, n_neighbors=15, min_dist=0.1)
        X_tr = reducer.fit_transform(X_train)
        X_te = reducer.transform(X_test)
    else:
        print("  Warning: umap-learn not installed; falling back to PCA")
        from sklearn.decomposition import PCA
        pca = PCA(n_components=n_components, random_state=42)
        scaler = StandardScaler()
        X_tr = pca.fit_transform(scaler.fit_transform(X_train))
        X_te = pca.transform(scaler.transform(X_test))

    # Scale to [-1, 1] (same features for QK and RBF)
    lo, hi = X_tr.min(axis=0), X_tr.max(axis=0)
    rng = np.where(hi - lo > 0, hi - lo, 1.0)
    X_tr_scaled = 2.0 * (X_tr - lo) / rng - 1.0
    X_te_scaled = np.clip(2.0 * (X_te - lo) / rng - 1.0, -1.0, 1.0)
    return X_tr_scaled, X_te_scaled


# ---------------------------------------------------------------------------
# Quantum kernel (upgraded with PennyLane built-in features)
# ---------------------------------------------------------------------------




def _make_kernel_fn(n_qubits: int, n_repeats: int = 1):
    """
    Build a PennyLane quantum kernel function using IQPEmbedding
    on lightning.qubit (CPU-optimised simulator).

    Circuit: IQPEmbedding(x1) -> adjoint(IQPEmbedding)(x2) -> |0> prob = kernel

    IQPEmbedding interleaves RZ(arccos(x_i^2)) encodings with CNOT entangling
    layers. The adjoint does NOT cancel the entangling gates because data-
    dependent rotations sit between consecutive CNOT layers, giving a
    non-trivial kernel that captures inter-qubit correlations.

    Kernel value K(x1, x2) = |<phi(x1)|phi(x2)>|^2 = |<0| U(x2)^dag U(x1) |0>|^2
    where U(x) = IQPEmbedding(x).

    Features must be in [-1, 1] for IQPEmbedding (uses arccos(x^2) internally).
    """
    dev = qml.device("lightning.qubit", wires=n_qubits)

    @qml.qnode(dev)
    def _kernel(x1, x2):
        qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
        return qml.probs(wires=range(n_qubits))

    def kernel(a, b):
        """K(x1, x2) = ground-state probability = |<phi(x1)|phi(x2)>|^2."""
        return float(_kernel(a, b)[0])

    return kernel


def _compute_block_task(i0: int, i1: int, j0: int, j1: int,
                         X_chunk: np.ndarray,
                         n_qubits: int, n_repeats: int) -> np.ndarray:
    """
    Compute one block of the kernel matrix (top-level for joblib pickling).

    Creates its own PennyLane device + QNode per call.
    Each joblib loky process imports the module fresh, so this is safe
    despite being called multiple times per worker (device creation is
    cheap compared to kernel evaluation on large blocks).

    Tested: ~39s per 2400×2400 fold with 48 workers and 144 blocks.
    """
    _dev = qml.device("lightning.qubit", wires=n_qubits)

    @qml.qnode(_dev)
    def _kernel(x1, x2):
        qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
        return qml.probs(wires=range(n_qubits))

    def _kfn(a, b):
        return float(_kernel(a, b)[0])

    return kernel_matrix(X_chunk[i0:i1], X_chunk[j0:j1], _kfn)


def _kernel_matrix_chunked(X: np.ndarray,
                             block_size: int = 200,
                             n_jobs: int = 1,
                             n_qubits: int = 8,
                             n_repeats: int = 1) -> np.ndarray:
    """
    Compute kernel matrix via block decomposition, optionally parallel.

    Exploits symmetry: only computes blocks in the upper triangle
    (i_block <= j_block) and mirrors K[j,i] = K[i,j].T for the lower
    triangle — roughly 2× speedup vs. computing all blocks.

    For large n (e.g., 3000+), dividing the matrix into blocks of
    block_size × block_size allows parallel computation across CPUs
    without O(n²) memory pressure.

    Parallel mode uses joblib with loky (process) backend — each worker
    process creates its own PennyLane device + QNode, avoiding PennyLane's
    non-thread-safe global QueuingManager.

    Returns:
        K: (n, n) full kernel matrix
    """
    n = len(X)
    n_blocks = (n + block_size - 1) // block_size
    block_ranges = [(i * block_size, min((i + 1) * block_size, n))
                    for i in range(n_blocks)]

    # Build tasks ONLY for upper triangle (i_block <= j_block)
    # Kernel matrices are symmetric: K[j,i] = K[i,j].T
    # This halves the number of blocks to compute
    tasks = []
    task_idx = []  # (ib, jb) for mapping each result back
    for ib, (i0, i1) in enumerate(block_ranges):
        for jb, (j0, j1) in enumerate(block_ranges):
            if ib <= jb:  # upper triangle incl. diagonal
                tasks.append((i0, i1, j0, j1))
                task_idx.append((ib, jb))

    n_tasks = len(tasks)
    n_all = n_blocks * n_blocks
    print(f"        Blocks: {n_tasks}/{n_all} computed (symmetry saves {n_all - n_tasks}/{n_all} = {(1-n_tasks/n_all)*100:.0f}%)")

    if n_jobs == 1:
        results = [_compute_block_task(i0, i1, j0, j1, X, n_qubits, n_repeats)
                   for i0, i1, j0, j1 in tasks]
    else:
        from joblib import Parallel, delayed
        results = Parallel(n_jobs=n_jobs)(
            delayed(_compute_block_task)(i0, i1, j0, j1, X, n_qubits, n_repeats)
            for i0, i1, j0, j1 in tasks
        )

    # Assemble full matrix (upper triangle computed, lower triangle mirrored)
    K = np.zeros((n, n), dtype=np.float64)
    for (ib, jb), block in zip(task_idx, results):
        i0, i1 = block_ranges[ib]
        j0, j1 = block_ranges[jb]
        K[i0:i1, j0:j1] = block
        if ib != jb:
            # Mirror: K[jb_range, ib_range] = K[ib_range, jb_range].T
            K[j0:j1, i0:i1] = block.T

    return K


def build_quantum_kernel(X: np.ndarray, n_repeats: int = 1,
                         noise_method: str | None = None,
                         block_size: int | None = None,
                         n_jobs: int = 1) -> np.ndarray:
    """
    Compute quantum kernel matrix using PennyLane built-in features.

    For n ≤ 500, uses the built-in kernel_matrix directly (fast).
    For n > 500, uses block decomposition with optional parallelism.

    1. kernel_matrix (full or chunked)
    2. closest_psd_matrix: ensures PSD for SVM
    3. mitigate_depolarizing_noise: optional noise model

    Args:
        X: (n, n_qubits) input array scaled to [-1, 1] for IQPEmbedding
        n_repeats: IQPEmbedding repeat count
        noise_method: None | "global" | "local" for depolarizing noise
        block_size: Block size for chunked computation (None = auto)
        n_jobs: Parallel workers for chunked mode

    Returns:
        K: (n, n) PSD kernel matrix
    """
    kernel_fn = _make_kernel_fn(N_QUBITS, n_repeats)

    # Step 1: Standardize input features (R2: StandardScaler for QK stability)
    # NOTE: IQPEmbedding requires inputs in [-1, 1] (arccos(x^2)).
    # StandardScaler produces values outside this range, so we clip.
    from sklearn.preprocessing import StandardScaler
    _scaler = StandardScaler()
    X_scaled = _scaler.fit_transform(X)
    # Clip back to [-1, 1] for IQPEmbedding compatibility
    X_scaled = np.clip(X_scaled, -1.0, 1.0)
    if not np.all(np.isfinite(X_scaled)):
        print("    WARNING: NaN/Inf in standardized QK features — falling back to raw")
        X_scaled = X

    # Step 2: Compute kernel matrix
    n = len(X_scaled)
    # ── Adaptive block_size (R12) ────────────────────────────────
    _bs = block_size
    if _bs is None and n > 500:
        _target_blocks = max(n_jobs * 2, 4)
        _bs = max(50, min(500, n // _target_blocks))
        print(f"    Adaptive block_size: n={n}, n_jobs={n_jobs} → block_size={_bs}")

    if _bs is None or n <= _bs:
        # Small matrix: direct computation (fast, no parallel overhead)
        K = kernel_matrix(X_scaled, X_scaled, kernel=kernel_fn)
    else:
        # Large matrix: block decomposition for parallelism
        print(f"    Chunked mode: {n}x{n} matrix, block_size={_bs}, n_jobs={n_jobs}")
        K = _kernel_matrix_chunked(X_scaled,
                                    block_size=_bs,
                                    n_jobs=n_jobs,
                                    n_qubits=N_QUBITS,
                                    n_repeats=n_repeats)

    # Step 3: Fix non-PSD matrices for SVM compatibility
    K = closest_psd_matrix(K)

    # Step 4: Verify PSD property (R3: post-fix sanity check)
    assert K.shape == (n, n), f"Kernel shape mismatch: {K.shape} vs ({n},{n})"  # R7
    _eigvals = np.linalg.eigvalsh(K)
    _min_eig = _eigvals.min()
    _max_eig = _eigvals.max()
    if _min_eig < -1e-8:
        print(f"    WARNING: PSD fix residual — min eigenvalue = {_min_eig:.6e}")
    elif _min_eig < 0:
        print(f"    NOTE: Tiny negative eigenvalue (numerical noise) = {_min_eig:.6e}")
    print(f"    Eigenvalue range: [{_min_eig:.6f}, {_max_eig:.6f}] (n={n})")

    # Step 5: Optional noise mitigation
    if noise_method:
        K = mitigate_depolarizing_noise(K, N_QUBITS, method=noise_method)

    # ── Memory cleanup (R13) ──────────────────────────────────────
    del X_scaled, kernel_fn
    gc.collect()

    return K


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

def evaluate_fold(K_train: np.ndarray, K_test: np.ndarray,
                  y_train: np.ndarray, y_test: np.ndarray,
                  label: str, ta_val: float | None = None) -> dict:
    """Evaluate SVM with precomputed kernel + record target alignment."""
    clf = SVC(kernel="precomputed", probability=True, C=1.0)
    clf.fit(K_train, y_train)
    y_prob = clf.predict_proba(K_test)[:, 1]
    y_pred = clf.predict(K_test)
    result = {
        "model":           label,
        "auc":             roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else np.nan,
        "accuracy":        accuracy_score(y_test, y_pred),
        "f1":              f1_score(y_test, y_pred, zero_division=0),
    }
    if ta_val is not None:
        result["target_alignment"] = ta_val
    return result


def _rbf_matrix(A: np.ndarray, B: np.ndarray, gamma: float) -> np.ndarray:
    """Compute RBF kernel matrix K(A, B) with given gamma."""
    sq = np.sum((A[:, None] - B[None]) ** 2, axis=-1)
    return np.exp(-gamma * sq)


def _tune_rbf_gamma(X_train: np.ndarray, y_train: np.ndarray,
                    gammas: list[float] | None = None,
                    n_inner_folds: int = 3) -> float:
    """Grid search for optimal RBF gamma via inner cross-validation.

    Features are already scaled [-1, 1] (same as QK features).
    Extended gamma grid for better coverage in [-1, 1] space.
    Returns the gamma that maximises mean AUC across inner folds.
    """
    if gammas is None:
        # For data in [-1, 1]^8, max squared distance = 32.
        # gamma > 10 gives exp(-10 * 32) = 1e-139 (near-identity kernel)
        # gamma = 0.5: exp(-0.5 * 1) = 0.61 for points at d=1 — reasonable
        # Cap grid at 5.0 to avoid pathological near-identity matrices.
        gammas = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 0.1, 0.5, 1.0, 2.0, 5.0]

    best_gamma, best_auc = gammas[0], -1.0
    skf = StratifiedKFold(n_splits=n_inner_folds, shuffle=True, random_state=42)
    for g in gammas:
        aucs = []
        for ii_tr, ii_te in skf.split(X_train, y_train):
            K_tr = _rbf_matrix(X_train[ii_tr], X_train[ii_tr], g)
            K_te = _rbf_matrix(X_train[ii_te], X_train[ii_tr], g)
            clf = SVC(kernel="precomputed", C=1.0, probability=True)
            clf.fit(K_tr, y_train[ii_tr])
            y_prob = clf.predict_proba(K_te)[:, 1]
            if len(np.unique(y_train[ii_te])) > 1:
                aucs.append(roc_auc_score(y_train[ii_te], y_prob))
        mean_auc = np.mean(aucs) if aucs else 0.5
        if mean_auc > best_auc:
            best_auc = mean_auc
            best_gamma = g
    return best_gamma


def rbf_kernel(X_train: np.ndarray, X_test: np.ndarray,
               y_train: np.ndarray | None = None,
               gamma: float | None = None) -> tuple[np.ndarray, np.ndarray, float]:
    """Precomputed RBF kernel matrices with automatic gamma tuning.

    Uses the same [-1, 1] scaled features as the quantum kernel.
    No extra StandardScaler (features already scaled identically).

    Returns:
        K_train, K_test, best_gamma
    """
    if gamma is None and y_train is not None:
        best_gamma = _tune_rbf_gamma(X_train, y_train)
    else:
        best_gamma = gamma if gamma is not None else 0.01

    K_tr = _rbf_matrix(X_train, X_train, best_gamma)
    K_te = _rbf_matrix(X_test, X_train, best_gamma)
    return K_tr, K_te, best_gamma


def run_benchmark(X: np.ndarray, y: np.ndarray,
                  n_repeats: int = 1,
                  noise_method: str | None = None,
                  checkpoint_path: str | None = None,
                  block_size: int | None = None,
                  n_jobs: int = 1) -> pd.DataFrame:
    """5-fold CV benchmark: quantum kernel vs RBF kernel (lightning.qubit).

    Both RBF and QK use the same [-1, 1] scaled features.
    Supports checkpoint resume: saves fold results to JSON after each fold.
    For large n, uses block decomposition with n_jobs workers.
    """
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    kernel_fn = _make_kernel_fn(N_QUBITS, n_repeats)
    records = []

    # Load checkpoint if provided
    completed_folds = set()
    if checkpoint_path and Path(checkpoint_path).exists():
        with open(checkpoint_path) as f:
            ckpt = json.load(f)
        records = ckpt.get("records", [])
        completed_folds = {r["fold"] for r in records}
        print(f"  Resuming from checkpoint: {len(completed_folds)} folds completed")

    t0_total = time.perf_counter()

    for fold, (tr_idx, te_idx) in enumerate(skf.split(X, y), start=1):
        if fold in completed_folds:
            print(f"  Fold {fold}/{N_FOLDS} — skipped (checkpoint)")
            continue

        t0_fold = time.perf_counter()
        print(f"  Fold {fold}/{N_FOLDS}...")
        X_tr_raw, X_te_raw = X[tr_idx], X[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]

        # UMAP -> scaled features (same for both QK and RBF)
        X_tr_q, X_te_q = reduce_to_qubits(X_tr_raw, X_te_raw)

        # Quantum kernel
        n_train = len(X_tr_q)
        n_evals = n_train * n_train + len(X_te_q) * n_train
        print(f"    Building quantum kernel ({n_train}x{n_train}, ~{n_evals:,} evals)...")
        if block_size:
            print(f"    Block size={block_size}, n_jobs={n_jobs}")
        t0_qk = time.perf_counter()
        K_tr_q = build_quantum_kernel(X_tr_q, n_repeats, noise_method,
                                       block_size=block_size, n_jobs=n_jobs)
        K_te_q = kernel_matrix(X_te_q, X_tr_q, kernel_fn)
        ta_val = float(target_alignment(X_tr_q, y_tr, kernel_fn))
        qk_time = time.perf_counter() - t0_qk
        print(f"    QK done in {qk_time:.1f}s | Target alignment: {ta_val:.4f}")

        rec_q = evaluate_fold(K_tr_q, K_te_q, y_tr, y_te, "quantum", ta_val)
        rec_q["fold"] = fold
        rec_q["qk_time_s"] = round(qk_time, 1)
        records.append(rec_q)

        # RBF baseline (gamma-tuned on SAME scaled features)
        print(f"    RBF: tuning gamma on [-1,1] features (same as QK)...")
        K_tr_rbf, K_te_rbf, best_gamma = rbf_kernel(
            X_tr_q, X_te_q, y_train=y_tr
        )
        print(f"    RBF: best gamma = {best_gamma:.4g}")

        def _rbf_fn(a, b, _g=best_gamma):
            return float(_rbf_matrix(a.reshape(1, -1), b.reshape(1, -1), _g)[0, 0])

        ta_rbf = float(target_alignment(X_tr_q, y_tr, _rbf_fn))

        rec_rbf = evaluate_fold(K_tr_rbf, K_te_rbf, y_tr, y_te, "rbf",
                                ta_val=ta_rbf)
        rec_rbf["fold"] = fold
        rec_rbf["gamma"] = best_gamma
        records.append(rec_rbf)

        # Linear SVM baseline (same [-1,1] features, no kernel hyperparameters)
        print(f"    Linear SVM on same [-1,1] features (honest baseline)...")
        clf_lin = SVC(kernel="linear", C=1.0, probability=True, random_state=42)
        clf_lin.fit(X_tr_q, y_tr)
        y_prob_lin = clf_lin.predict_proba(X_te_q)[:, 1]
        y_pred_lin = clf_lin.predict(X_te_q)
        rec_lin = {
            "model":           "linear",
            "auc":             roc_auc_score(y_te, y_prob_lin) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy":        accuracy_score(y_te, y_pred_lin),
            "f1":              f1_score(y_te, y_pred_lin, zero_division=0),
            "fold":            fold,
        }
        records.append(rec_lin)
        print(f"    Linear: AUC={rec_lin['auc']:.4f}  Acc={rec_lin['accuracy']:.4f}")

        fold_time = time.perf_counter() - t0_fold
        elapsed = time.perf_counter() - t0_total
        folds_done = fold - len(completed_folds)
        eta = (elapsed / folds_done) * (N_FOLDS - fold) if folds_done > 0 else 0
        print(f"  Fold {fold} done in {fold_time:.1f}s | ETA: {eta/60:.1f} min")

        # Save checkpoint after each fold
        if checkpoint_path:
            with open(checkpoint_path, "w") as f:
                json.dump({"records": records}, f, default=str)
            print(f"    Checkpoint saved: {checkpoint_path}")

        # ── Memory cleanup after each fold (R13) ──────────────────
        del K_tr_q, K_te_q, X_tr_q, X_te_q, X_tr_raw, X_te_raw
        del K_tr_rbf, K_te_rbf
        gc.collect()

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--n-mols", type=int, default=3000,
                        help="Molecules for QK benchmark (default: 3,000; 0 = all)")
    parser.add_argument("--n-repeats", type=int, default=1,
                        help="IQPEmbedding repeat count (default: 1; more = deeper circuit)")
    parser.add_argument("--noise", type=str, default=None,
                        choices=[None, "global", "local"],
                        help="Depolarizing noise mitigation method")
    parser.add_argument("--checkpoint", type=str, default=None,
                        help="Path to checkpoint JSON to resume from (skips completed folds)")
    parser.add_argument("--block-size", type=int, default=None,
                        help="Block size for chunked kernel (default: None=auto; HPC: 200)")
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel workers for chunked mode (default: 1)")
    parser.add_argument("--hpc", action="store_true",
                        help="HPC mode: block_size=200, n_jobs=max (requires joblib)")
    args = parser.parse_args()

    DEVICE = "lightning.qubit"  # system-wide PennyLane device

    # HPC mode: overrides block_size and n_jobs for maximum throughput
    if args.hpc:
        if args.block_size is None:
            args.block_size = 200
        if args.n_jobs == 1:  # only override if user didn't set explicitly
            try:
                import os
                args.n_jobs = len(os.sched_getaffinity(0))
            except Exception:
                import multiprocessing
                args.n_jobs = multiprocessing.cpu_count()
        print(f"  HPC mode: block_size={args.block_size}, n_jobs={args.n_jobs}")

    print("=" * 60)
    print("Paper 3 — Quantum Kernel Benchmark  (lightning.qubit)")
    print("=" * 60)
    print(f"  Circuit: IQPEmbedding ({args.n_repeats} repeat(s))")
    print(f"  Qubits:  {N_QUBITS}")
    print(f"  Device:  {DEVICE}")
    print(f"  Noise:   {args.noise or 'none'}")
    print(f"  Block:   {args.block_size or 'full'}")
    print(f"  Jobs:    {args.n_jobs}")
    print()

    X, y, _ = load_dataset(args.n_mols)

    results = run_benchmark(X, y, args.n_repeats, args.noise,
                            checkpoint_path=args.checkpoint,
                            block_size=args.block_size,
                            n_jobs=args.n_jobs)

    # ── gzip-compressed output (R14) ─────────────────────────────
    out_csv = RESULTS_DIR / "p3_qks_benchmark.csv.gz"
    results.to_csv(out_csv, index=False, compression="gzip")
    out_csv_uncomp = RESULTS_DIR / "p3_qks_benchmark.csv"
    results.to_csv(out_csv_uncomp, index=False)
    print(f"\n  Saved: {out_csv} (compressed), {out_csv_uncomp} (plain)")

    # Memory cleanup (R13)
    del X, y, results
    gc.collect()

    # Summary
    lines = [
        "Quantum Kernel vs RBF-SVM  (5-fold CV)",
        f"Circuit: IQPEmbedding ({args.n_repeats} repeats) | Noise: {args.noise or 'none'}",
        "",
    ]
    for model in ["quantum", "rbf", "linear"]:
        sub = results[results["model"] == model]
        lines.append(f"{model.upper()} kernel:")
        for metric in ["auc", "target_alignment", "accuracy", "f1"]:
            if metric in sub.columns:
                vals = sub[metric].dropna()
                if len(vals) > 0:
                    lines.append(f"  {metric:<18s} {vals.mean():.4f} ± {vals.std():.4f}")
        lines.append("")

    # Paired t-tests on AUC (pairwise)
    model_pairs = [("quantum", "rbf"), ("quantum", "linear"), ("rbf", "linear")]
    for m1, m2 in model_pairs:
        auc1 = results[results["model"] == m1]["auc"].values
        auc2 = results[results["model"] == m2]["auc"].values
        if len(auc1) == len(auc2) == N_FOLDS:
            t_stat, p_val = ttest_rel(auc1, auc2)
            sig = "significant (p<0.05)" if p_val < 0.05 else "not significant"
            lines.append(f"Paired t-test {m1} vs {m2}: t={t_stat:.3f}, p={p_val:.4f} ({sig})")

    summary = "\n".join(lines)
    print("\n" + summary)
    (RESULTS_DIR / "p3_qks_summary.txt").write_text(summary)
    print(f"\n  Summary saved: {RESULTS_DIR / 'p3_qks_summary.txt'}")


if __name__ == "__main__":
    main()
