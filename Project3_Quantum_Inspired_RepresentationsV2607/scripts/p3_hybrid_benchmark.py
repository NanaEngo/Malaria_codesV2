"""
Paper 3 — Steps 5–6: Hybrid framework + activity prediction benchmark.

Combines TFP, TNE, and QK (quantum kernel PCA) features into a single
hybrid descriptor and benchmarks against:
    - ECFP4, FCFP4, MACCS, AP, PHCO, BPF baselines
    - TFP alone
    - TNE alone
    - Hybrid (TFP + TNE + QK, each component per-fold to avoid data leakage)

Classifiers: Random Forest (200 trees) + SVM, 5-fold CV
Metrics: AUC-ROC, accuracy, F1
Significance: paired t-tests (hybrid vs each baseline)

QK features are computed WITHIN each CV fold:
  1. UMAP fit on training → transform test (no leakage)
  2. Kernel matrix on training data only
  3. Kernel PCA fit on training → transform test

NOT a grid search over α/β/γ (RF is scale-invariant, and the old ECFP4 proxy
for QK weights was incorrect — 2048-bit vs 10-dim mismatch).

Ablation study: systematically removes one component at a time.

Inputs:
    results/p3_tda_fingerprints.csv
    results/p3_tne_embeddings.csv
    results/eos80ch_malaria_final_activity.csv

Outputs:
    results/p3_hybrid_benchmark.csv
    results/p3_ablation.csv
    results/p3_hybrid_summary.txt

Usage:
    python Papers/Quantum_Inspired_Representations/Scripts/p3_hybrid_benchmark.py
    python Papers/Quantum_Inspired_Representations/Scripts/p3_hybrid_benchmark.py --n-mols 1000
"""

import argparse
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
from rdkit.Chem import MACCSkeys
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem import AllChem
from rdkit.Chem.AtomPairs.Sheridan import GetBPFingerprint
from rdkit.Chem.Pharm2D import Generate, Gobbi_Pharm2D
from rdkit.DataStructs import ConvertToNumpyArray

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
from scipy.stats import ttest_rel
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import pennylane as qml
from pennylane.kernels import kernel_matrix, closest_psd_matrix

N_QUBITS = 8

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

N_FOLDS = 5
ACT_THRESHOLD = 0.5
RF_TREES = 200


# ---------------------------------------------------------------------------
# Data loading
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


def maccs(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(167, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(MACCSkeys.GenMACCSKeys(mol), arr)
        rows.append(arr)
    return np.array(rows)


ap_gen = rdFingerprintGenerator.GetAtomPairGenerator(maxDistance=10, fpSize=2048)

def ap(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(ap_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


def phco(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(39972, dtype=np.float32)
        if mol:
            try:
                fp = Generate.Gen2DFingerprint(mol, Gobbi_Pharm2D.factory)
                # ConvertToNumpyArray fails on some Gobbi SparseBitVects. Using GetOnBits() is robust.
                for on_bit in fp.GetOnBits():
                    if on_bit < 39972:
                        arr[on_bit] = 1.0
            except Exception:
                pass
        rows.append(arr)
    return np.array(rows)


def fcfp4(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, useFeatures=True, nBits=2048)
            ConvertToNumpyArray(fp, arr)
        rows.append(arr)
    return np.array(rows)


def bpf_hashed(smiles_list: list[str], nBits=2048) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(nBits, dtype=np.float32)
        if mol:
            try:
                fp = GetBPFingerprint(mol)
                for k, v in fp.GetNonzeroElements().items():
                    arr[k % nBits] += v
            except Exception:
                pass
        rows.append(arr)
    return np.array(rows)


def load_precomputed(smiles_list: list[str],
                     csv_path: Path,
                     prefix: str) -> np.ndarray | None:
    """Load TFP or TNE descriptors aligned to smiles_list."""
    if not csv_path.exists():
        print(f"  Warning: {csv_path.name} not found — run the corresponding pipeline first")
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
            rows.append(np.zeros(len(feat_cols), dtype=np.float32))
    X = np.array(rows)
    # Replace NaN with column means
    col_means = np.nanmean(X, axis=0)
    col_means = np.where(np.isfinite(col_means), col_means, 0.0)
    inds = np.where(~np.isfinite(X))
    X[inds] = np.take(col_means, inds[1])
    return X


# ---------------------------------------------------------------------------
# Benchmark helpers
# ---------------------------------------------------------------------------

def scale(X_tr: np.ndarray, X_te: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    sc = StandardScaler()
    return sc.fit_transform(X_tr), sc.transform(X_te)


def cv_score(X: np.ndarray, y: np.ndarray,
             clf_name: str, descriptor: str) -> list[dict]:
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    records = []
    for fold, (tr, te) in enumerate(skf.split(X, y), 1):
        X_tr, X_te = scale(X[tr], X[te])
        y_tr, y_te = y[tr], y[te]

        if clf_name == "rf":
            clf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                         random_state=42)
            clf.fit(X_tr, y_tr)
            y_prob = clf.predict_proba(X_te)[:, 1]
            y_pred = clf.predict(X_te)
        else:  # svm
            clf = SVC(kernel="rbf", probability=True, C=1.0, random_state=42)
            clf.fit(X_tr, y_tr)
            y_prob = clf.predict_proba(X_te)[:, 1]
            y_pred = clf.predict(X_te)

        records.append({
            "descriptor": descriptor,
            "classifier": clf_name,
            "fold": fold,
            "auc":      roc_auc_score(y_te, y_prob) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy": accuracy_score(y_te, y_pred),
            "f1":       f1_score(y_te, y_pred, zero_division=0),
        })
    return records


# ---------------------------------------------------------------------------
# Chunked kernel matrix (same approach as p3_qks_benchmark)
# ---------------------------------------------------------------------------

# Module-level cache for kernel functions in parallel workers.
# Each loky process imports the module fresh, so this cache is per-process.
_KERNEL_CACHE: dict = {}


def _get_kernel_fn(n_qubits: int, n_repeats: int = 1):
    """Get or create a cached quantum kernel function for given parameters.

    Uses IQPEmbedding on lightning.qubit. Each worker process creates the
    QNode only ONCE (on first block), then reuses it for all subsequent blocks.
    """
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


def _compute_block_task(i0: int, i1: int, j0: int, j1: int,
                         X_chunk: np.ndarray,
                         n_qubits: int, n_repeats: int) -> np.ndarray:
    """
    Compute one block of the kernel matrix (top-level for joblib pickling).

    Uses the module-level cached kernel function (_get_kernel_fn) so each
    worker creates the PennyLane device + QNode only ONCE.
    """
    _kfn = _get_kernel_fn(n_qubits, n_repeats)
    return kernel_matrix(X_chunk[i0:i1], X_chunk[j0:j1], _kfn)


def _kernel_matrix_chunked(X: np.ndarray,
                             block_size: int = 200,
                             n_jobs: int = 1,
                             n_qubits: int = 8,
                             n_repeats: int = 1) -> np.ndarray:
    """
    Compute kernel matrix via block decomposition, optionally parallel.

    Exploits symmetry: only computes blocks i_block <= j_block
    and mirrors K[j,i] = K[i,j].T for the lower triangle.

    Parallel mode uses joblib with loky (process) backend.
    """
    n = len(X)
    n_blocks = (n + block_size - 1) // block_size
    block_ranges = [(i * block_size, min((i + 1) * block_size, n))
                    for i in range(n_blocks)]

    # Build tasks ONLY for upper triangle (i_block <= j_block)
    tasks = []
    task_idx = []
    for ib, (i0, i1) in enumerate(block_ranges):
        for jb, (j0, j1) in enumerate(block_ranges):
            if ib <= jb:
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

    # Assemble full matrix (upper triangle computed, lower mirrored)
    K = np.zeros((n, n), dtype=np.float64)
    for (ib, jb), block in zip(task_idx, results):
        i0, i1 = block_ranges[ib]
        j0, j1 = block_ranges[jb]
        K[i0:i1, j0:j1] = block
        if ib != jb:
            K[j0:j1, i0:i1] = block.T

    return K


# ---------------------------------------------------------------------------
# QK features (per-fold, no data leakage)
# ---------------------------------------------------------------------------

def _qk_features_fold(X_ecfp_tr: np.ndarray, X_ecfp_te: np.ndarray,
                       n_qubits: int = 8,
                       n_kpca: int = 10,
                       n_repeats: int = 1,
                       block_size: int | None = None,
                       n_jobs: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute QK features for one CV fold — NO data leakage (lightning.qubit).

    UMAP is fitted on training data only, then applied to test.
    Kernel matrix is built on training data only, then test points
    are projected via kernel PCA.

    For large n, uses chunked kernel computation with process-level
    parallelism (loky backend) to avoid PennyLane QueuingManager issues.

    Args:
        block_size: Block size for chunked kernel (None = auto, direct)
        n_jobs: Parallel workers for chunked mode

    Returns:
        qk_tr: (n_train, n_kpca) array
        qk_te: (n_test, n_kpca) array
    """
    from umap import UMAP
    from sklearn.decomposition import KernelPCA

    # Step 1: UMAP on training only
    reducer = UMAP(n_components=n_qubits, metric="jaccard",
                   random_state=42, n_neighbors=15, min_dist=0.1)
    X_8d_tr = reducer.fit_transform(X_ecfp_tr)
    X_8d_te = reducer.transform(X_ecfp_te)

    # Step 2: Scale to [-1, 1] using training statistics
    lo, hi = X_8d_tr.min(axis=0), X_8d_tr.max(axis=0)
    rng = np.where(hi - lo > 0, hi - lo, 1.0)
    X_q_tr = 2.0 * (X_8d_tr - lo) / rng - 1.0
    X_q_te = np.clip(2.0 * (X_8d_te - lo) / rng - 1.0, -1.0, 1.0)

    n_train = len(X_q_tr)

    # Step 3-4: Training kernel matrix (chunked if large) + PSD fix
    if block_size is not None and n_train > block_size:
        print(f"        Chunked QK matrix: {n_train}x{n_train}, block_size={block_size}, n_jobs={n_jobs}, n_repeats={n_repeats}")
        K_tr = _kernel_matrix_chunked(X_q_tr,
                                       block_size=block_size,
                                       n_jobs=n_jobs,
                                       n_qubits=n_qubits,
                                       n_repeats=n_repeats)
    else:
        # Direct computation for small matrices
        dev = qml.device("lightning.qubit", wires=n_qubits)

        @qml.qnode(dev)
        def _kernel(x1, x2):
            qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
            qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
            return qml.probs(wires=range(n_qubits))

        def kernel_fn(a, b):
            return float(_kernel(a, b)[0])

        K_tr = kernel_matrix(X_q_tr, X_q_tr, kernel_fn)

    K_tr_psd = closest_psd_matrix(K_tr)

    # Step 5: KPCA on training kernel
    n_kpca_actual = min(n_kpca, len(X_q_tr) - 1)
    kpca = KernelPCA(n_components=n_kpca_actual,
                     kernel="precomputed", copy_X=True,
                     random_state=42)
    qk_tr = kpca.fit_transform(K_tr_psd)

    # Step 6: Transform test via kernel + KPCA projection
    # Test matrix is usually smaller, use direct computation
    dev_te = qml.device("lightning.qubit", wires=n_qubits)

    @qml.qnode(dev_te)
    def _kernel_te(x1, x2):
        qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
        return qml.probs(wires=range(n_qubits))

    def kernel_fn_te(a, b):
        return float(_kernel_te(a, b)[0])

    K_te = kernel_matrix(X_q_te, X_q_tr, kernel_fn_te)
    qk_te = kpca.transform(K_te)

    # Normalise to unit variance (for stable weighting across folds)
    qk_tr = qk_tr / (qk_tr.std(axis=0, keepdims=True) + 1e-10)
    qk_te = qk_te / (qk_te.std(axis=0, keepdims=True) + 1e-10)

    return qk_tr.astype(np.float32), qk_te.astype(np.float32)


# ---------------------------------------------------------------------------
# CV score for hybrid (fold-specific QK features)
# ---------------------------------------------------------------------------

def _cv_score_hybrid(X_ecfp: np.ndarray,
                      X_tfp: np.ndarray | None,
                      X_tne: np.ndarray | None,
                      y: np.ndarray,
                      n_qubits: int = 8,
                      n_kpca: int = 10,
                      n_repeats: int = 1,
                      block_size: int | None = None,
                      n_jobs: int = 1,
                      checkpoint_path: str | None = None,
                      completed_folds: set | None = None) -> list[dict]:
    """
    5-fold CV for hybrid descriptor (lightning.qubit).

    For each fold:
      1. Compute QK features on training only (_qk_features_fold)
         - Uses chunked kernel computation for large n (block_size, n_jobs)
      2. Concatenate [TFP_tr, TNE_tr, QK_tr] → train RF
      3. Evaluate on [TFP_te, TNE_te, QK_te]

    No data leakage: UMAP + kernel matrix + KPCA are fit on training only.

    Supports checkpoint resume: saves fold results to JSON after each fold.
    Pass ``checkpoint_path`` to enable, ``completed_folds`` to skip already-done
    folds on resume.
    """
    if completed_folds is None:
        completed_folds = set()
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    records = []

    for fold, (tr_idx, te_idx) in enumerate(skf.split(X_ecfp, y), start=1):
        if fold in completed_folds:
            print(f"    Hybrid fold {fold}/{N_FOLDS} — skipped (checkpoint)")
            continue

        print(f"    Hybrid fold {fold}/{N_FOLDS}...")

        # Compute QK features within this fold (no leakage)
        qk_tr, qk_te = _qk_features_fold(
            X_ecfp[tr_idx], X_ecfp[te_idx],
            n_qubits=n_qubits,
            n_kpca=n_kpca,
            n_repeats=n_repeats,
            block_size=block_size,
            n_jobs=n_jobs,
        )

        # Build fold-specific feature matrices
        components_tr, components_te = [], []
        if X_tfp is not None:
            components_tr.append(X_tfp[tr_idx])
            components_te.append(X_tfp[te_idx])
        if X_tne is not None:
            components_tr.append(X_tne[tr_idx])
            components_te.append(X_tne[te_idx])
        components_tr.append(qk_tr)
        components_te.append(qk_te)

        X_tr = np.hstack(components_tr)
        X_te = np.hstack(components_te)
        y_tr, y_te = y[tr_idx], y[te_idx]

        # StandardScaler
        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        X_te_s = sc.transform(X_te)

        # RF classifier
        clf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                     random_state=42)
        clf.fit(X_tr_s, y_tr)
        y_prob = clf.predict_proba(X_te_s)[:, 1]
        y_pred = clf.predict(X_te_s)

        records.append({
            "descriptor": "Hybrid",
            "classifier": "rf",
            "fold": fold,
            "auc":      roc_auc_score(y_te, y_prob) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy": accuracy_score(y_te, y_pred),
            "f1":       f1_score(y_te, y_pred, zero_division=0),
        })

        # SVM classifier
        clf_svm = SVC(kernel="rbf", probability=True, C=1.0, random_state=42)
        clf_svm.fit(X_tr_s, y_tr)
        y_prob_svm = clf_svm.predict_proba(X_te_s)[:, 1]
        y_pred_svm = clf_svm.predict(X_te_s)

        records.append({
            "descriptor": "Hybrid",
            "classifier": "svm",
            "fold": fold,
            "auc":      roc_auc_score(y_te, y_prob_svm) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy": accuracy_score(y_te, y_pred_svm),
            "f1":       f1_score(y_te, y_pred_svm, zero_division=0),
        })

        # Save checkpoint after each fold (R4)
        if checkpoint_path:
            with open(checkpoint_path, "w") as _f:
                json.dump({"records": records, "section": "hybrid"}, _f, default=str)
            print(f"      Checkpoint saved: {checkpoint_path}")

    return records


def _cv_score_ablation_hybrid(X_ecfp: np.ndarray,
                               X_tfp: np.ndarray | None,
                               X_tne: np.ndarray | None,
                               y: np.ndarray,
                               remove: str = "QK",
                               n_qubits: int = 8,
                               n_kpca: int = 10,
                               n_repeats: int = 1,
                               block_size: int | None = None,
                               n_jobs: int = 1,
                               checkpoint_path: str | None = None,
                               completed_folds: set | None = None) -> list[dict]:
    """
    5-fold CV ablation: remove one component from the hybrid (lightning.qubit).

    remove ∈ {"TFP", "TNE", "QK"}
    QK is still computed per-fold (no leakage) when it is included.
    Uses chunked kernel for large n (block_size, n_jobs).

    Supports checkpoint resume (same pattern as _cv_score_hybrid).
    """
    if completed_folds is None:
        completed_folds = set()
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    records = []
    desc_name = f"Hybrid-{remove}"

    for fold, (tr_idx, te_idx) in enumerate(skf.split(X_ecfp, y), start=1):
        print(f"    {desc_name} fold {fold}/{N_FOLDS}...")

        # Compute QK within this fold if QK is NOT being removed
        if remove != "QK":
            qk_tr, qk_te = _qk_features_fold(
            X_ecfp[tr_idx], X_ecfp[te_idx],
            n_qubits=n_qubits,
            n_kpca=n_kpca,
            n_repeats=n_repeats,
            block_size=block_size,
            n_jobs=n_jobs,
        )

        # Build components (skip the removed one)
        components_tr, components_te = [], []
        if remove != "TFP" and X_tfp is not None:
            components_tr.append(X_tfp[tr_idx])
            components_te.append(X_tfp[te_idx])
        if remove != "TNE" and X_tne is not None:
            components_tr.append(X_tne[tr_idx])
            components_te.append(X_tne[te_idx])
        if remove != "QK":
            components_tr.append(qk_tr)
            components_te.append(qk_te)

        X_tr = np.hstack(components_tr) if components_tr else np.zeros((len(y[tr_idx]), 1))
        X_te = np.hstack(components_te) if components_te else np.zeros((len(y[te_idx]), 1))
        y_tr, y_te = y[tr_idx], y[te_idx]

        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        X_te_s = sc.transform(X_te)

        clf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                     random_state=42)
        clf.fit(X_tr_s, y_tr)
        y_prob = clf.predict_proba(X_te_s)[:, 1]
        y_pred = clf.predict(X_te_s)

        records.append({
            "descriptor": desc_name,
            "classifier": "rf",
            "fold": fold,
            "auc":      roc_auc_score(y_te, y_prob) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy": accuracy_score(y_te, y_pred),
            "f1":       f1_score(y_te, y_pred, zero_division=0),
        })

        # Save checkpoint after each ablation fold (R4)
        if checkpoint_path:
            with open(checkpoint_path, "w") as _f:
                json.dump({"records": records, "section": f"ablation_{remove}"}, _f, default=str)
            print(f"      Ablation checkpoint saved: {checkpoint_path}")

    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-mols", type=int, default=200,
                        help="Molecules for benchmark (default: 200 for local; set higher for HPC)")
    parser.add_argument("--block-size", type=int, default=None,
                        help="Block size for chunked QK kernel (default: None=auto; HPC: 200)")
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Parallel workers for chunked QK mode (default: 1; HPC: 48)")
    parser.add_argument("--hpc", action="store_true",
                        help="HPC mode: block_size=200, n_jobs=max (requires joblib)")
    parser.add_argument("--n-repeats", type=int, default=1,
                        help="IQPEmbedding repeat count for QK (default: 1; try 2 for richer kernel)")
    parser.add_argument("--n-kpca", type=int, default=10,
                        help="Number of kernel PCA components for QK (default: 10; try 20 for more signal)")
    parser.add_argument("--tfp-enriched", action="store_true", default=True,
                        help="Include persistence image + Betti curves in TFP (default: True; add --no-tfp-enriched to use only base H features)")
    parser.add_argument("--no-tfp-enriched", action="store_false", dest="tfp_enriched",
                        help="Use only base H features for TFP (no pers_img or betti curves)")
    parser.add_argument("--checkpoint", type=str, default=None,
                        help="Path to JSON checkpoint for fold-by-fold resume (default: None)")
    args = parser.parse_args()

    DEVICE = "lightning.qubit"  # system-wide PennyLane device

    # HPC mode: overrides block_size and n_jobs for maximum throughput
    if args.hpc:
        if args.block_size is None:
            args.block_size = 200
        if args.n_jobs == 1:
            try:
                import os
                args.n_jobs = len(os.sched_getaffinity(0))
            except Exception:
                import multiprocessing
                args.n_jobs = multiprocessing.cpu_count()
        print(f"  HPC mode: block_size={args.block_size}, n_jobs={args.n_jobs}")

    print("=" * 60)
    print("Paper 3 — Hybrid Framework + Activity Benchmark  (lightning.qubit)")
    print("=" * 60)

    t0_total = time.perf_counter()

    act_df = load_activity()
    if args.n_mols:
        act_df = act_df.head(args.n_mols)

    smiles_list = act_df["smiles"].tolist()
    y = (act_df["activity"].values >= ACT_THRESHOLD).astype(int)
    print(f"  {len(y)} molecules  (active={y.sum()}, inactive={(y==0).sum()})")

    # Load descriptors
    print("\n  Loading descriptors...")
    X_ecfp = ecfp4(smiles_list)
    X_maccs = maccs(smiles_list)
    X_ap = ap(smiles_list)
    X_phco = phco(smiles_list)
    X_fcfp4 = fcfp4(smiles_list)
    X_bpf = bpf_hashed(smiles_list)
    X_tfp = load_precomputed(smiles_list,
                              RESULTS_DIR / "p3_tda_fingerprints.csv", "H")
    # Optionally add persistence image and Betti curve columns
    if X_tfp is not None and args.tfp_enriched:
        X_tfp_pers = load_precomputed(smiles_list,
                                       RESULTS_DIR / "p3_tda_fingerprints.csv", "pers_img_")
        X_tfp_betti = load_precomputed(smiles_list,
                                        RESULTS_DIR / "p3_tda_fingerprints.csv", "betti_")
        if X_tfp_pers is not None and X_tfp_betti is not None:
            X_tfp = np.hstack([X_tfp, X_tfp_pers, X_tfp_betti])
            print(f"    TFP enriched: {X_tfp.shape[1]} features (H={33}, pers_img={X_tfp_pers.shape[1]}, betti={X_tfp_betti.shape[1]})")
        else:
            print(f"    WARNING: TFP enriched requested but pers_img or betti columns missing — using base H only ({X_tfp.shape[1]} features)")
    elif X_tfp is not None:
        print(f"    TFP base only: {X_tfp.shape[1]} features (H0/H1/H2 base features only)")
    if X_tfp is None:
        print("    WARNING: TFP file not found — run p3_tda_pipeline first. TFP will be excluded from Hybrid.")
    X_tne = load_precomputed(smiles_list,
                              RESULTS_DIR / "p3_tne_embeddings.csv", "tne_")

    # ── Checkpoint resume (R4) ───────────────────────────────────
    completed_hybrid: set[int] = set()
    completed_ablation: set[str] = set()
    # completed_folds used for ablation sub-sections: "TFP", "TNE", "QK"
    ablation_done: dict[str, set[int]] = {r: set() for r in ["TFP", "TNE", "QK"]}
    if args.checkpoint and Path(args.checkpoint).exists():
        with open(args.checkpoint) as _f:
            _ckpt = json.load(_f)
        _saved_records = _ckpt.get("records", [])
        _completed_sections = _ckpt.get("completed_sections", [])
        for _r in _saved_records:
            _desc = _r.get("descriptor", "")
            _fold = _r.get("fold", 0)
            if _desc == "Hybrid":
                completed_hybrid.add(_fold)
            elif _desc and _desc.startswith("Hybrid-"):
                _removed = _desc.replace("Hybrid-", "")
                if _removed in ablation_done:
                    ablation_done[_removed].add(_fold)
        print(f"  Checkpoint loaded: {len(completed_hybrid)} hybrid folds + {sum(len(v) for v in ablation_done.values())} ablation folds completed")

    print(f"\n  Hybrid: QK features computed per-fold (UMAP + kernel PCA on train only).")
    print(f"    n_repeats={args.n_repeats}, n_kpca={args.n_kpca}, no data leakage.")
    print(f"    TFP enriched={args.tfp_enriched}.")

    # Full benchmark
    print("\n  Running benchmark (5-fold CV)...")
    all_records = []
    descriptors = {
        "ECFP4":  X_ecfp,
        "FCFP4":  X_fcfp4,
        "MACCS":  X_maccs,
        "AP":     X_ap,
        "PHCO":   X_phco,
        "BPF":    X_bpf,
    }
    if X_tfp is not None:
        descriptors["TFP"] = X_tfp
    if X_tne is not None:
        descriptors["TNE"] = X_tne

    # Classical descriptors: use existing cv_score (no QK involved)
    for desc_name, X_desc in descriptors.items():
        print(f"    {desc_name}...")
        for clf in ["rf", "svm"]:
            all_records.extend(cv_score(X_desc, y, clf, desc_name))

    # Hybrid descriptor: uses per-fold QK computation (no data leakage)
    print(f"    Hybrid (per-fold QK)...")
    all_records.extend(_cv_score_hybrid(
        X_ecfp, X_tfp, X_tne, y,
        n_qubits=N_QUBITS,
        n_kpca=args.n_kpca,
        n_repeats=args.n_repeats,
        block_size=args.block_size,
        n_jobs=args.n_jobs,
        checkpoint_path=args.checkpoint,
        completed_folds=completed_hybrid,
    ))

    # Save intermediate checkpoint after hybrid benchmark
    if args.checkpoint:
        with open(args.checkpoint, "w") as _f:
            json.dump({
                "records": all_records,
                "completed_sections": ["hybrid"],
                "section": "hybrid_done",
            }, _f, default=str)
        print(f"  Intermediate checkpoint: hybrid benchmark done")

    results_df = pd.DataFrame(all_records)
    out_csv = RESULTS_DIR / "p3_hybrid_benchmark.csv"
    results_df.to_csv(out_csv, index=False)
    t_benchmark = time.perf_counter() - t0_total
    print(f"\n  Saved: {out_csv}  (total wall time: {t_benchmark:.1f}s)")

    # Ablation study (per-fold QK, no data leakage)
    print("\n  Running ablation study...")
    ablation_records = []
    for removed in ["TFP", "TNE", "QK"]:
        ablation_records.extend(_cv_score_ablation_hybrid(
            X_ecfp, X_tfp, X_tne, y,
            remove=removed,
            n_qubits=N_QUBITS,
            n_kpca=args.n_kpca,
            n_repeats=args.n_repeats,
            block_size=args.block_size,
            n_jobs=args.n_jobs,
            checkpoint_path=args.checkpoint,
            completed_folds=ablation_done.get(removed, set()),
        ))

    abl_df = pd.DataFrame(ablation_records)
    abl_out = RESULTS_DIR / "p3_ablation.csv"
    abl_df.to_csv(abl_out, index=False)
    print(f"  Saved: {abl_out}")

    # Summary
    lines = ["Hybrid: per-fold QK (no data leakage); RF is scale-invariant (no weights)", ""]
    for desc in results_df["descriptor"].unique():
        sub = results_df[(results_df["descriptor"] == desc) &
                         (results_df["classifier"] == "rf")]
        auc = sub["auc"].dropna()
        lines.append(f"{desc:<12s} RF  AUC={auc.mean():.4f}±{auc.std():.4f}")

    # Paired t-test: Hybrid vs ECFP4
    h_auc = results_df[(results_df["descriptor"] == "Hybrid") &
                        (results_df["classifier"] == "rf")]["auc"].values
    e_auc = results_df[(results_df["descriptor"] == "ECFP4") &
                        (results_df["classifier"] == "rf")]["auc"].values
    if len(h_auc) == len(e_auc) == N_FOLDS:
        t, p = ttest_rel(h_auc, e_auc)
        lines += ["", f"Paired t-test Hybrid vs ECFP4: t={t:.3f}, p={p:.4f}",
                  "Significant (p<0.05)" if p < 0.05 else "Not significant"]

    summary = "\n".join(lines)
    print("\n" + summary)
    (RESULTS_DIR / "p3_hybrid_summary.txt").write_text(summary)
    print(f"\n  Summary saved: {RESULTS_DIR / 'p3_hybrid_summary.txt'}")


# ---------------------------------------------------------------------------
# PennyLane QK density
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()

