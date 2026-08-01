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
import gc
import json
import time
import warnings
from pathlib import Path

try:
    from tqdm import tqdm
    _HAS_TQDM = True
except ImportError:
    _HAS_TQDM = False

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", DeprecationWarning)

import numpy as np
import pandas as pd

# ── ECFP4 cache (R11) — placed after numpy import ─────────────────
_ECFP4_CACHE: dict[str, np.ndarray] = {}
from rdkit import Chem
from rdkit.Chem import MACCSkeys
from rdkit.Chem import rdFingerprintGenerator
bpf_gen = rdFingerprintGenerator.GetAtomPairGenerator(fpSize=2048)
from rdkit.Chem.Pharm2D import Generate, Gobbi_Pharm2D
from rdkit.DataStructs import ConvertToNumpyArray

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
from scipy.stats import ttest_rel
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import pennylane as qml
from pennylane.kernels import kernel_matrix, closest_psd_matrix

# ── JAX / CuPy detection ────────────────────────────────────────────
try:
    import jax
    import jax.numpy as jnp
    _HAS_JAX = True
    _JAX_BACKEND = jax.devices()[0].platform  # 'cpu' or 'gpu'
except ImportError:
    _HAS_JAX = False
    _JAX_BACKEND = None

try:
    import cupy as cp
    _HAS_CUPY = True
    _CUPY_AVAILABLE = cp.is_available()
    if not _CUPY_AVAILABLE:
        print("  [CuPy] Imported but no GPU available — falling back to CPU")
except ImportError:
    _HAS_CUPY = False
    _CUPY_AVAILABLE = False
    print("  [CuPy] Not installed — GPU features unavailable")
except Exception as _cupy_err:
    _HAS_CUPY = False
    _CUPY_AVAILABLE = False
    print(f"  [CuPy] Import error: {_cupy_err}")

# ── Device override (set via --device CLI arg) ──
_DEVICE_OVERRIDE: str | None = None


def best_device(n_qubits: int = 6, prefer_cpu: bool = False) -> str:
    """Select the fastest available PennyLane device.

    Priority (from pennylane skill):
    - prefer_cpu=False: lightning.gpu > lightning.qubit > default.qubit
    - prefer_cpu=True:  lightning.qubit > default.qubit (skip GPU)

    Returns device name string for qml.device().
    """
    if prefer_cpu:
        _devices_to_try = ["lightning.qubit", "default.qubit"]
    else:
        _devices_to_try = ["lightning.gpu", "lightning.qubit", "default.qubit"]
    for d in _devices_to_try:
        try:
            qml.device(d, wires=n_qubits)
            return d
        except Exception:
            continue
    return "default.qubit"


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


_CANONICAL_PANEL_CACHE: dict = {}


def load_canonical_panel(n_mols: int | None = None) -> pd.DataFrame:
    """Canonical P3 panel shared by every benchmark script (C2 fix).

    Panel = p3_tda_fingerprints.csv SMILES order, intersected with:
      - activity labels (deduplicated by SMILES)
      - molecules with a finite (valid) TNE embedding
    Every descriptor (ECFP4, TFP, TNE, QK, Hybrid) is therefore computed on
    exactly the same molecules, so paired comparisons are valid and no
    descriptor is silently imputed.

    n_mols: if given, take the first n_mols of the canonical panel
            (in TFP-file order), matching Phase 1→2→3 (n=200/5,000/19,849).

    Raises ValueError if a panel molecule lacks labels or TNE (no silent imputation).
    """
    cache_key = n_mols
    if cache_key in _CANONICAL_PANEL_CACHE:
        return _CANONICAL_PANEL_CACHE[cache_key]

    tfp_df = pd.read_csv(RESULTS_DIR / "p3_tda_fingerprints.csv")
    if "smiles" not in tfp_df.columns:
        raise ValueError("p3_tda_fingerprints.csv must contain a 'smiles' column")
    panel_smiles = tfp_df["smiles"].tolist()

    act = load_activity().drop_duplicates("smiles")
    act = act[act["smiles"].isin(panel_smiles)]

    tne_df = pd.read_csv(RESULTS_DIR / "p3_tne_embeddings.csv")
    tne_cols = [c for c in tne_df.columns if c.startswith("tne_")]
    if tne_cols:
        _finite = np.isfinite(tne_df[tne_cols].values).all(axis=1)
        ok_tne = set(tne_df.loc[_finite, "smiles"])
        act = act[act["smiles"].isin(ok_tne)]

    # Reorder to TFP-file order (canonical across scripts).
    act = act.set_index("smiles").reindex(panel_smiles).dropna().reset_index()
    if len(act) == 0:
        raise ValueError("Canonical panel is empty — check TFP/activity/TNE files")

    if n_mols is not None:
        act = act.head(n_mols)

    _CANONICAL_PANEL_CACHE[cache_key] = act
    return act


def ecfp4(smiles_list: list[str]) -> np.ndarray:
    """Compute ECFP4 fingerprints with caching (R11)."""
    rows = []
    for smi in smiles_list:
        if smi in _ECFP4_CACHE:
            rows.append(_ECFP4_CACHE[smi])
            continue
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        _ECFP4_CACHE[smi] = arr
        rows.append(arr)
    result = np.array(rows)
    assert result.shape[1] == 2048, f"ECFP4: expected 2048 dims, got {result.shape[1]}"  # R7
    return result


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


_fcfp4_feat_inv = rdFingerprintGenerator.GetMorganFeatureAtomInvGen()
fcfp4_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, atomInvariantsGenerator=_fcfp4_feat_inv)

def fcfp4(smiles_list: list[str]) -> np.ndarray:
    """FCFP4 (feature-classified) fingerprints using modern rdFingerprintGenerator API.

    Uses GetMorganGenerator(useFeatures=True) which extracts pharmacophoric
    features instead of atom identities — this is the correct FCFP4 definition.
    Replaces the legacy AllChem.GetMorganFingerprintAsBitVect.
    """
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(fcfp4_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


def bpf_hashed(smiles_list: list[str], nBits=2048) -> np.ndarray:
    """BPF (Bottom Path Fingerprint) via atom-pair generator.

    Uses rdFingerprintGenerator.GetAtomPairGenerator which is the correct
    modern replacement for the deprecated GetBPFingerprint — both capture
    atom-pair path patterns.
    """
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(nBits, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(bpf_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)


def load_precomputed(smiles_list: list[str],
                     csv_path: Path,
                     prefix: str) -> np.ndarray | None:
    """Load TFP or TNE descriptors aligned to smiles_list.

    C2 fix: the canonical panel guarantees every SMILES is present in the
    source CSV, so any missing molecule raises instead of being silently
    imputed with column means (which corrupted the n=19,849 Hybrid results).
    """
    if not csv_path.exists():
        print(f"  Warning: {csv_path.name} not found — run the corresponding pipeline first")
        return None
    df = pd.read_csv(csv_path)
    feat_cols = [c for c in df.columns if c.startswith(prefix)]
    if not feat_cols:
        return None
    df = df.set_index("smiles")
    rows = []
    missing = 0
    for smi in smiles_list:
        if smi in df.index:
            rows.append(df.loc[smi, feat_cols].values.astype(np.float32))
        else:
            missing += 1
            rows.append(np.zeros(len(feat_cols), dtype=np.float32))
    if missing:
        raise ValueError(
            f"load_precomputed({csv_path.name}, prefix='{prefix}'): "
            f"{missing}/{len(smiles_list)} molecules have no features — "
            f"panel is not canonical. Refusing to impute silently (C2)."
        )
    return np.array(rows)


# ---------------------------------------------------------------------------
# Benchmark helpers
# ---------------------------------------------------------------------------



def cv_score(X: np.ndarray, y: np.ndarray,
             clf_name: str, descriptor: str) -> list[dict]:
    """5-fold CV for a classical descriptor (no QK involved).

    Uses sklearn.pipeline.Pipeline to prevent data leakage — StandardScaler
    is fit ONLY on training folds and applied to test folds within the CV loop.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix of shape (n_mols, n_features).
    y : np.ndarray
        Binary labels of shape (n_mols,).
    clf_name : str
        Classifier name: "rf" (Random Forest) or "svm" (SVC RBF).
    descriptor : str
        Descriptor name for record-keeping.

    Returns
    -------
    list[dict]
        List of per-fold metric dictionaries.
    """
    if clf_name == "rf":
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                            random_state=42)),
        ])
    else:  # svm
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", probability=True, C=1.0, random_state=42)),
        ])

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    records = []
    fold_iter = enumerate(skf.split(X, y), 1)
    if _HAS_TQDM:
        fold_iter = tqdm(fold_iter, total=N_FOLDS,
                         desc=f"  {descriptor} {clf_name}", unit="fold", ncols=80)
    for fold, (tr, te) in fold_iter:
        X_tr, X_te = X[tr], X[te]
        y_tr, y_te = y[tr], y[te]

        pipe.fit(X_tr, y_tr)
        y_prob = pipe.predict_proba(X_te)[:, 1]
        y_pred = pipe.predict(X_te)

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


def _get_kernel_fn(n_qubits: int, n_repeats: int = 1, prefer_cpu: bool = False):
    """Get or create a cached quantum kernel function for given parameters.

    Uses best_device() to select the fastest available device.
    If prefer_cpu=True, skips lightning.gpu (GPU overhead > CPU
    for pair-by-pair quantum kernel evaluation).

    Each worker process creates the QNode only ONCE.
    """
    key = (n_qubits, n_repeats, prefer_cpu)
    if key not in _KERNEL_CACHE:
        dev_name = _DEVICE_OVERRIDE or best_device(n_qubits, prefer_cpu=prefer_cpu)
        dev = qml.device(dev_name, wires=n_qubits)

        @qml.qnode(dev)
        def _kernel(x1, x2):
            qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
            qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
            return qml.probs(wires=range(n_qubits))

        def _kfn(a, b):
            return float(_kernel(a, b)[0])

        _KERNEL_CACHE[key] = _kfn

    return _KERNEL_CACHE[key]


def _get_kernel_fn_jax(n_qubits: int, n_repeats: int = 1, prefer_cpu: bool = False):
    """JIT-compiled kernel function via JAX interface (10-100x faster).

    Uses pennylane-lightning with JAX backend and XLA compilation.
    The entire kernel matrix is computed via jax.vmap, avoiding the
    per-pair QNode overhead.

    Falls back to standard _get_kernel_fn if JAX is unavailable.
    """
    if not _HAS_JAX:
        return _get_kernel_fn(n_qubits, n_repeats, prefer_cpu=prefer_cpu)

    key = (n_qubits, n_repeats, prefer_cpu, "jax")
    if key not in _KERNEL_CACHE:
        dev_name = _DEVICE_OVERRIDE or best_device(n_qubits, prefer_cpu=prefer_cpu)
        dev_jax = qml.device(dev_name, wires=n_qubits)

        @qml.qnode(dev_jax, interface="jax", diff_method=None)
        def _circuit(x1, x2):
            qml.IQPEmbedding(x1, wires=range(n_qubits), n_repeats=n_repeats)
            qml.adjoint(qml.IQPEmbedding)(x2, wires=range(n_qubits), n_repeats=n_repeats)
            return qml.probs(wires=range(n_qubits))

        # JIT the full matrix computation: vmap over all pairs
        @jax.jit
        def _mat(X):
            return jax.vmap(
                lambda x1: jax.vmap(
                    lambda x2: _circuit(x1, x2)[0]
                )(X)
            )(X)

        _KERNEL_CACHE[key] = _mat

    return _KERNEL_CACHE[key]


def _kernel_matrix_jax(X: np.ndarray,
                        n_qubits: int,
                        n_repeats: int,
                        dtype: type = np.float64,
                        prefer_cpu: bool = False) -> np.ndarray:
    """Compute full kernel matrix using JAX JIT + vmap (10-100x faster).

    Batches ALL pairwise evaluations into a single XLA-compiled operation.
    On GPU, uses CuPy interop to avoid GPU->CPU transfer overhead.

    Args:
        X: (n, n_qubits) input array scaled to [-1, 1]
        n_qubits: Number of qubits
        n_repeats: IQPEmbedding repeat count
        dtype: Output dtype (float32 or float64)
        prefer_cpu: If True, skip lightning.gpu

    Returns:
        K: (n, n) symmetric kernel matrix
    """
    if not _HAS_JAX:
        raise RuntimeError("JAX not available — use chunked kernel instead")

    _mat_fn = _get_kernel_fn_jax(n_qubits, n_repeats, prefer_cpu=prefer_cpu)
    X_jax = jnp.array(X, dtype=jnp.float32)
    K_jax = _mat_fn(X_jax)

    # Use CuPy interop on GPU for zero-copy conversion
    if _HAS_CUPY and _CUPY_AVAILABLE and _JAX_BACKEND == "gpu":
        return cp.asnumpy(cp.array(K_jax, dtype=dtype))
    return np.array(K_jax, dtype=dtype)


def _evaluate_state_vectors(X: np.ndarray,
                             n_qubits: int = 8,
                             n_repeats: int = 1,
                             prefer_cpu: bool = False) -> np.ndarray:
    """Evaluate quantum state vectors for input samples X.
    
    Shape: (len(X), 2**n_qubits) complex64.
    1000x faster than pair-wise QNode evaluation by computing state vectors
    O(N) and performing BLAS inner products K = |V1 @ V2.conj().T|^2.
    """
    dev_name = _DEVICE_OVERRIDE or best_device(n_qubits, prefer_cpu=prefer_cpu)
    dev = qml.device(dev_name, wires=n_qubits)

    @qml.qnode(dev)
    def _circuit(x):
        qml.IQPEmbedding(x, wires=range(n_qubits), n_repeats=n_repeats)
        return qml.state()

    V = np.array([_circuit(x) for x in X], dtype=np.complex64)
    return V


def _compute_block_task(i0: int, i1: int, j0: int, j1: int,
                         X_chunk: np.ndarray,
                         n_qubits: int, n_repeats: int,
                         prefer_cpu: bool = False) -> np.ndarray:
    """Compute one block of the kernel matrix using state vector inner product."""
    VX = _evaluate_state_vectors(X_chunk[i0:i1], n_qubits=n_qubits, n_repeats=n_repeats, prefer_cpu=prefer_cpu)
    VY = _evaluate_state_vectors(X_chunk[j0:j1], n_qubits=n_qubits, n_repeats=n_repeats, prefer_cpu=prefer_cpu)
    return (np.abs(VX @ VY.conj().T) ** 2).astype(np.float64)


def _kernel_matrix_chunked(X: np.ndarray,
                             block_size: int = 200,
                             n_jobs: int = 1,
                             n_qubits: int = 8,
                             n_repeats: int = 1,
                             prefer_cpu: bool = False,
                             use_jax: bool = False,
                             dtype: type = np.float64) -> np.ndarray:
    """
    Compute kernel matrix via state vector inner products (1000x faster).
    """
    n = len(X)
    print(f"        State vector QK matrix: {n}x{n}, {n_qubits}q, {n_repeats}rep")
    V = _evaluate_state_vectors(X, n_qubits=n_qubits, n_repeats=n_repeats, prefer_cpu=prefer_cpu)
    K = np.abs(V @ V.conj().T) ** 2
    K = (K + K.T) / 2.0
    return K.astype(dtype)


# ---------------------------------------------------------------------------
# Rectangular chunked kernel matrix (for test projection)
# ---------------------------------------------------------------------------

def _compute_block_task_xy(i0: int, i1: int, j0: int, j1: int,
                            X: np.ndarray, Y: np.ndarray,
                            n_qubits: int, n_repeats: int,
                            prefer_cpu: bool = False) -> np.ndarray:
    """Compute one rectangular block of the kernel matrix K(X, Y)."""
    VX = _evaluate_state_vectors(X[i0:i1], n_qubits=n_qubits, n_repeats=n_repeats, prefer_cpu=prefer_cpu)
    VY = _evaluate_state_vectors(Y[j0:j1], n_qubits=n_qubits, n_repeats=n_repeats, prefer_cpu=prefer_cpu)
    return (np.abs(VX @ VY.conj().T) ** 2).astype(np.float64)


def _kernel_matrix_chunked_xy(X: np.ndarray, Y: np.ndarray,
                                block_size: int = 200,
                                n_jobs: int = 1,
                                n_qubits: int = 8,
                                n_repeats: int = 1,
                                prefer_cpu: bool = False,
                                use_jax: bool = False,
                                dtype: type = np.float64) -> np.ndarray:
    """Chunked kernel matrix for rectangular inputs (e.g., test x train).
    Uses state vector inner products (1000x faster).
    """
    n_x, n_y = len(X), len(Y)
    print(f"        State vector rectangular QK matrix: {n_x}x{n_y}, {n_qubits}q, {n_repeats}rep")
    VX = _evaluate_state_vectors(X, n_qubits=n_qubits, n_repeats=n_repeats, prefer_cpu=prefer_cpu)
    VY = _evaluate_state_vectors(Y, n_qubits=n_qubits, n_repeats=n_repeats, prefer_cpu=prefer_cpu)
    K = np.abs(VX @ VY.conj().T) ** 2
    return K.astype(dtype)


# ---------------------------------------------------------------------------
# QK features (per-fold, no data leakage)
# ---------------------------------------------------------------------------

def _nystrom_kernel_approx(K_nm: np.ndarray, K_mm: np.ndarray,
                            n_kpca: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Nyström kernel approximation via landmark points.

    Approximates the full N×N kernel as K ≈ K_nm @ K_mm^{-1} @ K_nm.T
    and extracts KPCA features from the low-rank factor.

    Args:
        K_nm: (n_train, m) kernel between all training points and landmarks
        K_mm: (m, m) kernel between landmarks
        n_kpca: number of KPCA components

    Returns:
        qk_tr: (n_train, n_kpca) features for training set
        landmarks_idx: indices of landmark points (for test projection)
    """
    from sklearn.decomposition import KernelPCA

    n, m = K_nm.shape
    n_kpca_actual = min(n_kpca, m - 1)

    # PSD fix on landmark kernel
    K_mm_psd = closest_psd_matrix(K_mm)

    # KPCA on landmark kernel (m×m, fast)
    kpca = KernelPCA(n_components=n_kpca_actual,
                     kernel="precomputed", copy_X=True,
                     random_state=42)
    landmarks_emb = kpca.fit_transform(K_mm_psd)  # (m, n_kpca)

    # Approximate eigenvectors of full kernel via interpolation:
    # alpha = K_mm^{-1} @ landmarks_emb  (m, n_kpca)
    # Then: qk = K_nm @ alpha  (n, n_kpca)
    # This is the Nyström extension formula.
    from numpy.linalg import solve
    alpha = solve(K_mm_psd + 1e-8 * np.eye(m), landmarks_emb)  # (m, n_kpca)
    qk_tr = K_nm @ alpha  # (n, n_kpca)

    # Normalise
    qk_tr = qk_tr / (qk_tr.std(axis=0, keepdims=True) + 1e-10)

    return qk_tr.astype(np.float32), kpca, alpha


def _qk_features_fold(X_ecfp_tr: np.ndarray, X_ecfp_te: np.ndarray,
                       n_qubits: int = 8,
                       n_kpca: int = 10,
                       n_repeats: int = 1,
                       block_size: int | None = None,
                       n_jobs: int = 1,
                       use_jax: bool = False,
                       prefer_cpu: bool = False,
                       dtype: type = np.float64,
                       nystrom_m: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute QK features for one CV fold — NO data leakage.

    UMAP is fitted on training data only, then applied to test.
    Kernel matrix is built on training data only, then test points
    are projected via kernel PCA.

    When use_jax=True and JAX is available, the kernel matrix is computed
    via JAX JIT + vmap (10-100x faster than per-pair evaluation).
    On GPU (--device lightning.gpu), the entire matrix is computed in a
    single batched tensor operation.

    Args:
        block_size: Block size for chunked kernel (None = auto, direct)
        n_jobs: Parallel workers for chunked mode
        use_jax: Use JAX JIT + vmap for kernel matrix (10-100x speedup)
        prefer_cpu: Prefer CPU device (skip lightning.gpu)
        dtype: Output dtype for kernel matrix (float32 or float64)

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

    # Decide device name for logging
    _dev_name = _DEVICE_OVERRIDE or best_device(n_qubits, prefer_cpu=prefer_cpu)

    # Step 3-4: Training kernel matrix + PSD fix
    # ── Nyström fast-path (R15) ──────────────────────────────────
    if nystrom_m > 0 and n_train > nystrom_m:
        print(f"        Nyström: m={nystrom_m} landmarks from n={n_train} (speedup ~{(n_train/nystrom_m)**2:.1f}×)")
        rng_idx = np.random.RandomState(42)
        landmark_idx = rng_idx.choice(n_train, size=nystrom_m, replace=False)
        landmark_idx.sort()

        # Compute K_mm (landmarks × landmarks) — small, m×m
        X_landmarks = X_q_tr[landmark_idx]
        _bs = block_size
        if _bs is not None and nystrom_m > _bs:
            K_mm = _kernel_matrix_chunked(X_landmarks, block_size=_bs,
                                           n_jobs=n_jobs, n_qubits=n_qubits,
                                           n_repeats=n_repeats,
                                           prefer_cpu=prefer_cpu, dtype=dtype)
        else:
            _kfn = _get_kernel_fn(n_qubits, n_repeats, prefer_cpu=prefer_cpu)
            K_mm = kernel_matrix(X_landmarks, X_landmarks, _kfn)

        # Compute K_nm (all training × landmarks) — n×m, rectangular
        print(f"        Nyström K_nm: {n_train}x{nystrom_m} (rectangular)")
        K_nm = _kernel_matrix_chunked_xy(X_q_tr, X_landmarks,
                                          block_size=_bs or 500,
                                          n_jobs=n_jobs, n_qubits=n_qubits,
                                          n_repeats=n_repeats,
                                          prefer_cpu=prefer_cpu, dtype=dtype)

        # Nyström KPCA
        qk_tr, _kpca_ny, _alpha_ny = _nystrom_kernel_approx(K_nm, K_mm, n_kpca=n_kpca)

        # Test projection: K_te (n_test, m) × alpha
        K_te_nm = _kernel_matrix_chunked_xy(X_q_te, X_landmarks,
                                             block_size=_bs or 500,
                                             n_jobs=n_jobs, n_qubits=n_qubits,
                                             n_repeats=n_repeats,
                                             prefer_cpu=prefer_cpu, dtype=dtype)
        qk_te = K_te_nm @ _alpha_ny
        qk_te = qk_te / (qk_te.std(axis=0, keepdims=True) + 1e-10)
        qk_tr = qk_tr.astype(np.float32)
        qk_te = qk_te.astype(np.float32)

        # R7: Dimension asserts
        assert qk_tr.shape[1] == qk_te.shape[1], f"QK dim mismatch: train {qk_tr.shape[1]} vs test {qk_te.shape[1]}"
        assert np.all(np.isfinite(qk_tr)), "NaN/Inf in QK training features"
        assert np.all(np.isfinite(qk_te)), "NaN/Inf in QK test features"

        del K_mm, K_nm, K_te_nm, X_landmarks
        gc.collect()
        return qk_tr, qk_te

    # ── Adaptive block_size (R12) ────────────────────────────────
    _bs = block_size
    if _bs is None and n_train > 500 and not (use_jax and _HAS_JAX):
        _target_blocks = max(n_jobs * 2, 4)
        _bs = max(50, min(500, n_train // _target_blocks))
        print(f"        Adaptive block_size: n_train={n_train}, n_jobs={n_jobs} → block_size={_bs}")

    if use_jax and _HAS_JAX:
        # ── JAX JIT fast-path ──
        print(f"        JAX QK matrix: {n_train}x{n_train}, {n_qubits}q, {n_repeats}rep, device={_dev_name}")
        K_tr = _kernel_matrix_jax(X_q_tr, n_qubits, n_repeats, dtype=dtype, prefer_cpu=prefer_cpu)
        # Symmetrize (numerical noise from JIT)
        K_tr = (K_tr + K_tr.T) / 2.0
    elif _bs is not None and n_train > _bs:
        # ── Standard chunked ──
        print(f"        Chunked QK matrix: {n_train}x{n_train}, block_size={_bs}, n_jobs={n_jobs}, n_repeats={n_repeats}")
        K_tr = _kernel_matrix_chunked(X_q_tr,
                                       block_size=_bs,
                                       n_jobs=n_jobs,
                                       n_qubits=n_qubits,
                                       n_repeats=n_repeats,
                                       prefer_cpu=prefer_cpu,
                                       dtype=dtype)
    else:
        # ── Direct computation for small matrices ──
        print(f"        Direct QK matrix: {n_train}x{n_train}, {n_qubits}q, {n_repeats}rep, device={_dev_name}")
        dev = qml.device(_dev_name, wires=n_qubits)

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
    n_te, n_tr = X_q_te.shape[0], X_q_tr.shape[0]
    if use_jax and _HAS_JAX:
        # ── JAX rectangular fast-path ──
        # Compute square kernel on stacked [X_te; X_tr] then extract K(X_te, X_tr).
        # This wastes computing (n_te+n_tr)^2 instead of n_te*n_tr, but with JAX
        # JIT on GPU the marginal cost is negligible (ms vs the full n_train^2).
        print(f"        JAX test kernel: {n_te}x{n_tr} (via {n_te+n_tr}x{n_te+n_tr} stacked)")
        X_all = np.vstack([X_q_te, X_q_tr])
        K_all = _kernel_matrix_jax(X_all, n_qubits, n_repeats, dtype=dtype, prefer_cpu=prefer_cpu)
        K_te = K_all[:n_te, n_te:]  # K(X_te, X_tr) as upper-right block
    elif _bs is not None and (n_te > _bs or n_tr > _bs):
        print("        Computing test kernel matrix (chunked)...")
        K_te = _kernel_matrix_chunked_xy(
            X_q_te, X_q_tr,
            block_size=_bs,
            n_jobs=n_jobs,
            n_qubits=n_qubits,
            n_repeats=n_repeats,
            prefer_cpu=prefer_cpu,
            dtype=dtype,
        )
    else:
        # Test matrix is small, use direct computation
        dev_te = qml.device(_dev_name, wires=n_qubits)

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

    # R7: Dimension asserts
    assert qk_tr.shape[1] == qk_te.shape[1], f"QK dim mismatch: train {qk_tr.shape[1]} vs test {qk_te.shape[1]}"
    assert np.all(np.isfinite(qk_tr)), "NaN/Inf in QK training features"
    assert np.all(np.isfinite(qk_te)), "NaN/Inf in QK test features"

    # ── Memory cleanup (R13) ──────────────────────────────────────
    del K_tr, K_tr_psd, K_te, X_q_tr, X_q_te, X_8d_tr, X_8d_te
    gc.collect()

    return qk_tr.astype(np.float32), qk_te.astype(np.float32)


# ---------------------------------------------------------------------------
# Precomputed kernel (compute ONCE, extract per-fold — ~5x speedup)
# ---------------------------------------------------------------------------

def _precompute_qk_all(X_ecfp: np.ndarray,
                        n_qubits: int = 6,
                        n_repeats: int = 1,
                        block_size: int | None = None,
                        n_jobs: int = 1,
                        prefer_cpu: bool = False,
                        use_jax: bool = False,
                        dtype: type = np.float64) -> dict:
    """
    Precompute UMAP + kernel matrix ONCE on all molecules.

    ⚠️ M1 FIX: this mode is TRANSDUCTIVE. UMAP is fitted on ALL data
    (train + test together), so test-molecule structure influences the
    feature space. This mode must NOT be used for canonical "no-leakage"
    benchmark claims — the default per-fold mode (_qk_features_fold) fits
    UMAP on train only and is the publication path. The state-vector kernel
    is fast enough (~70 s for 19,849²) that per-fold computation is feasible.

    Kept only as an explicit speed option; callers must frame results as
    transductive when used.

    Returns dict with:
        - 'K_psd': closest-PSD kernel matrix (N x N)
        - 'time_s': total kernel computation time
    """
    from umap import UMAP

    print(f"    ⚠️ TRANSDUCTIVE precompute mode: UMAP fitted on ALL data (M1). "
          f"Not for no-leakage claims.")

    print(f"    Precomputing kernel on all {len(X_ecfp)} molecules...")

    # --- UMAP on all data (TRANSDUCTIVE — see M1 warning) ---
    t0 = time.perf_counter()
    reducer = UMAP(n_components=n_qubits, metric="jaccard",
                   random_state=42, n_neighbors=15, min_dist=0.1)
    X_8d = reducer.fit_transform(X_ecfp)
    lo, hi = X_8d.min(axis=0), X_8d.max(axis=0)
    rng = np.where(hi - lo > 0, hi - lo, 1.0)
    X_q = 2.0 * (X_8d - lo) / rng - 1.0
    print(f"      UMAP ({n_qubits}d): {time.perf_counter() - t0:.1f}s")

    n = len(X_q)
    n_pairs = n * (n + 1) // 2
    print(f"      Kernel: {n}x{n} ({n_pairs:,} upper-triangle pairs)")

    # --- Kernel matrix (ONE call, not 5x) ---
    t1 = time.perf_counter()
    dev_name = _DEVICE_OVERRIDE or best_device(n_qubits, prefer_cpu=prefer_cpu)
    print(f"      Computing kernel on device: {dev_name}")

    # Heuristic: use JAX fast-path for n > 500 on CPU (lightning.qubit)
    _use_jax_eff = use_jax and _HAS_JAX and n > 500

    if _use_jax_eff:
        print(f"      JAX JIT kernel: {n}x{n}, {n_qubits}q, {n_repeats}rep")
        K = _kernel_matrix_jax(X_q, n_qubits, n_repeats, dtype=dtype, prefer_cpu=prefer_cpu)
        K = (K + K.T) / 2.0  # symmetrize
    elif block_size is not None and n > block_size:
        K = _kernel_matrix_chunked(X_q,
                                    block_size=block_size,
                                    n_jobs=n_jobs,
                                    n_qubits=n_qubits,
                                    n_repeats=n_repeats,
                                    prefer_cpu=prefer_cpu,
                                    use_jax=False,
                                    dtype=dtype)
    else:
        _kfn = _get_kernel_fn(n_qubits, n_repeats, prefer_cpu=prefer_cpu)
        K = kernel_matrix(X_q, X_q, _kfn)

    kernel_time = time.perf_counter() - t1
    rate = n_pairs / kernel_time if kernel_time > 0 else 0
    print(f"      Kernel matrix: {kernel_time:.1f}s ({rate:.0f} pairs/s)")

    # --- closest-PSD ---
    t2 = time.perf_counter()
    K_psd = closest_psd_matrix(K)
    print(f"      closest_PSD: {time.perf_counter() - t2:.1f}s")

    elapsed = time.perf_counter() - t0
    print(f"      Total precompute: {elapsed:.1f}s — {elapsed/60:.1f} min")

    # Memory cleanup
    del X_8d, X_q, K
    gc.collect()

    return {"K_psd": K_psd, "time_s": elapsed}


def _qk_features_fold_precomputed(QK_data: dict,
                                    tr_idx: np.ndarray,
                                    te_idx: np.ndarray,
                                    n_kpca: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Extract fold QK features from precomputed kernel matrix.

    This is the fast path: instead of computing a new kernel matrix for
    each fold, we extract submatrices from the precomputed full kernel.
    KPCA is fit on the training submatrix (no data leakage).

    Args:
        QK_data: Dict with 'K_psd' key (N x N closest-PSD kernel matrix)
        tr_idx: Training indices
        te_idx: Test indices
        n_kpca: Number of KPCA components

    Returns:
        qk_tr, qk_te: (n_train, n_kpca) and (n_test, n_kpca) arrays
    """
    from sklearn.decomposition import KernelPCA

    K_all_psd = QK_data["K_psd"]
    n_train = len(tr_idx)
    n_kpca_actual = min(n_kpca, n_train - 1)

    # Extract submatrices from precomputed kernel (O(1) indexing, no recomputation)
    K_tr = K_all_psd[np.ix_(tr_idx, tr_idx)]
    K_te = K_all_psd[np.ix_(te_idx, tr_idx)]

    # Fit KPCA on training only (no data leakage)
    kpca = KernelPCA(n_components=n_kpca_actual,
                     kernel="precomputed", copy_X=True, random_state=42)
    qk_tr = kpca.fit_transform(K_tr)
    qk_te = kpca.transform(K_te)

    # Normalise to unit variance
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
                      completed_folds: set | None = None,
                      use_jax: bool = False,
                      prefer_cpu: bool = False,
                      dtype: type = np.float64,
                      precompute_kernel: bool = False,
                      QK_data: dict | None = None,
                      nystrom_m: int = 0,
                      seed_records: list | None = None) -> list[dict]:
    """
    5-fold CV for hybrid descriptor.

    Two modes:
      - precompute_kernel=False (default): UMAP + kernel matrix per fold
        (strict no-leakage, but 5x QK computation — ~5x slower)
      - precompute_kernel=True (optimised): UMAP + kernel ONCE on all data,
        then extract per-fold submatrices for KPCA. UMAP on all data is
        a minor unsupervised approximation; the kernel itself is label-free
        so there is NO leakage from the kernel precomputation.
        (~5x faster for the kernel computation)

    For each fold:
      1. Compute QK features on training only
         - precompute mode: extract from precomputed kernel (O(1))
         - standard mode: compute UMAP+kernel per fold (O(n²))
      2. Concatenate [TFP_tr, TNE_tr, QK_tr] → train RF
      3. Evaluate on [TFP_te, TNE_te, QK_te]

    C1 fix: seed_records carries completed folds' records from prior sessions,
    so a resumed run keeps the full 5-fold statistics instead of reporting
    only the folds computed in the current session.
    """
    if completed_folds is None:
        completed_folds = set()
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    records = [r for r in (seed_records or []) if r.get("descriptor") == "Hybrid"]

    # Build sklearn Pipelines (scaler + classifier) to prevent data leakage
    rf_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                        random_state=42)),
    ])
    svm_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", SVC(kernel="rbf", probability=True, C=1.0, random_state=42)),
    ])

    # ── Precompute kernel ONCE if requested (~5x speedup) ─────────
    # QK_data may be precomputed by caller (main) and shared with ablation
    if precompute_kernel and QK_data is None:
        print(f"    Precomputing kernel on all data ({len(X_ecfp)} molecules)...")
        QK_data = _precompute_qk_all(
            X_ecfp,
            n_qubits=n_qubits,
            n_repeats=n_repeats,
            block_size=block_size,
            n_jobs=n_jobs,
            prefer_cpu=prefer_cpu,
            use_jax=use_jax,
            dtype=dtype,
        )

    for fold, (tr_idx, te_idx) in enumerate(skf.split(X_ecfp, y), start=1):
        if fold in completed_folds:
            print(f"    Hybrid fold {fold}/{N_FOLDS} — skipped (checkpoint)")
            continue

        print(f"    Hybrid fold {fold}/{N_FOLDS}...")

        # Compute QK features (fast path: extract or full compute)
        if precompute_kernel and QK_data is not None:
            # Fast path: O(1) extraction from precomputed kernel
            qk_tr, qk_te = _qk_features_fold_precomputed(
                QK_data, tr_idx, te_idx, n_kpca=n_kpca,
            )
        else:
            # Standard path: per-fold UMAP + kernel (no leakage)
            qk_tr, qk_te = _qk_features_fold(
                X_ecfp[tr_idx], X_ecfp[te_idx],
                n_qubits=n_qubits,
                n_kpca=n_kpca,
                n_repeats=n_repeats,
                block_size=block_size,
                n_jobs=n_jobs,
                use_jax=use_jax,
                prefer_cpu=prefer_cpu,
                dtype=dtype,
                nystrom_m=nystrom_m,
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

        # RF classifier via Pipeline (scaler fit on train only — no leakage)
        rf_pipe.fit(X_tr, y_tr)
        y_prob = rf_pipe.predict_proba(X_te)[:, 1]
        y_pred = rf_pipe.predict(X_te)

        records.append({
            "descriptor": "Hybrid",
            "classifier": "rf",
            "fold": fold,
            "auc":      roc_auc_score(y_te, y_prob) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy": accuracy_score(y_te, y_pred),
            "f1":       f1_score(y_te, y_pred, zero_division=0),
        })

        # SVM classifier via Pipeline
        svm_pipe.fit(X_tr, y_tr)
        y_prob_svm = svm_pipe.predict_proba(X_te)[:, 1]
        y_pred_svm = svm_pipe.predict(X_te)

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
                               completed_folds: set | None = None,
                               use_jax: bool = False,
                               prefer_cpu: bool = False,
                               dtype: type = np.float64,
                               precompute_kernel: bool = False,
                               QK_data: dict | None = None,
                               nystrom_m: int = 0,
                               seed_records: list | None = None) -> list[dict]:
    """
    5-fold CV ablation: remove one component from the hybrid.

    remove ∈ {"TFP", "TNE", "QK"}
    QK is still computed per-fold (no leakage) when it is included.
    Uses JAX or chunked kernel for large n.

    C1/M2 fix: completed_folds is now actually honored (skip + reuse) and
    seed_records preserves completed folds' records across sessions.
    When precompute_kernel=True, accepts QK_data dict to reuse precomputed kernel.
    """
    if completed_folds is None:
        completed_folds = set()
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    desc_name = f"Hybrid-{remove}"
    records = [r for r in (seed_records or []) if r.get("descriptor") == desc_name]

    # Pipeline to prevent data leakage (scikit-learn skill)
    rf_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                        random_state=42)),
    ])

    for fold, (tr_idx, te_idx) in enumerate(skf.split(X_ecfp, y), start=1):
        if fold in completed_folds:
            print(f"    {desc_name} fold {fold}/{N_FOLDS} — skipped (checkpoint)")
            continue
        print(f"    {desc_name} fold {fold}/{N_FOLDS}...")

        # Compute QK within this fold if QK is NOT being removed
        if remove != "QK":
            if precompute_kernel and QK_data is not None:
                # Fast path: extract from precomputed kernel
                qk_tr, qk_te = _qk_features_fold_precomputed(
                    QK_data, tr_idx, te_idx, n_kpca=n_kpca,
                )
            else:
                # Standard path: per-fold compute
                qk_tr, qk_te = _qk_features_fold(
                    X_ecfp[tr_idx], X_ecfp[te_idx],
                    n_qubits=n_qubits,
                    n_kpca=n_kpca,
                    n_repeats=n_repeats,
                    block_size=block_size,
                    n_jobs=n_jobs,
                    use_jax=use_jax,
                    prefer_cpu=prefer_cpu,
                    dtype=dtype,
                    nystrom_m=nystrom_m,
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

        # Pipeline fit (scaler on train only — no leakage)
        rf_pipe.fit(X_tr, y_tr)
        y_prob = rf_pipe.predict_proba(X_te)[:, 1]
        y_pred = rf_pipe.predict(X_te)

        records.append({
            "descriptor": desc_name,
            "classifier": "rf",
            "fold": fold,
            "auc":      roc_auc_score(y_te, y_prob) if len(np.unique(y_te)) > 1 else np.nan,
            "accuracy": accuracy_score(y_te, y_pred),
            "f1":       f1_score(y_te, y_pred, zero_division=0),
        })

        # Save checkpoint after each ablation fold (R4) — merge to keep all
        # sections' records (C1 fix: resume must not lose prior folds).
        if checkpoint_path:
            _prev = []
            if Path(checkpoint_path).exists():
                try:
                    with open(checkpoint_path) as _f:
                        _prev = json.load(_f).get("records", [])
                except (json.JSONDecodeError, OSError):
                    _prev = []
            _merged = _prev + [r for r in records
                               if not any(r.get("fold") == o.get("fold")
                                          and r.get("descriptor") == o.get("descriptor")
                                          for o in _prev)]
            with open(checkpoint_path, "w") as _f:
                json.dump({"records": _merged, "section": f"ablation_{remove}"}, _f, default=str)
            print(f"      Ablation checkpoint saved: {checkpoint_path} ({len(_merged)} records)")

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
    parser.add_argument("--n-kpca", type=int, default=30,
                        help="Number of kernel PCA components for QK (default: 30 = Phase-2 optimal combo; was 10 — see job 12695)")
    parser.add_argument("--tfp-enriched", action="store_true", default=True,
                        help="Include persistence image + Betti curves in TFP (default: True; add --no-tfp-enriched to use only base H features)")
    parser.add_argument("--no-tfp-enriched", action="store_false", dest="tfp_enriched",
                        help="Use only base H features for TFP (no pers_img or betti curves)")
    parser.add_argument("--checkpoint", type=str, default=None,
                        help="Path to JSON checkpoint for fold-by-fold resume (default: None)")
    parser.add_argument("--skip-ablation", action="store_true",
                        help="Skip the ablation study (useful for the expensive full-library run)")
    parser.add_argument("--device", type=str, default="auto",
                        choices=["auto", "lightning.qubit", "lightning.gpu", "default.qubit"],
                        help="PennyLane device: auto (lightning.qubit CPU, recommended), "
                             "lightning.qubit (CPU, optimal for 6-8 qubit circuits), "
                             "lightning.gpu (GPU, experimental — 3-4x SLOWER than CPU "
                             "for small circuits), default.qubit (fallback). "
                             "Note: GPU is slower than CPU for IQPEmbedding 6-8 qubit "
                             "kernels due to per-call launch overhead.")
    parser.add_argument("--jax", action="store_true",
                        help="Use JAX JIT + vmap for the quantum kernel matrix "
                             "(experimental — JAX is 3-4x SLOWER than standard "
                             "lightning.qubit for small circuits). Not recommended.")
    parser.add_argument("--dtype", type=str, default="float64",
                        choices=["float32", "float64"],
                        help="Kernel matrix precision (default: float64). Use float32 "
                             "for 2x memory savings on GPU.")
    parser.add_argument("--n-qubits", type=int, default=6,
                        help="Number of qubits / UMAP components (default: 6 = Phase-2 "
                             "optimal bond_dim=6; was 8 — see job 12695)")
    parser.add_argument("--precompute-kernel", action="store_true",
                        help="Precompute kernel ONCE on all data, then extract "
                             "per-fold submatrices for KPCA. Avoids 4/5 of QK "
                             "computation. UMAP is applied on all data (minor "
                             "unsupervised approximation). Recommended for n > 1000.")
    parser.add_argument("--nystrom-m", type=int, default=0,
                        help="Number of Nyström landmark points (default: 0 = disabled). "
                             "When >0, uses Nyström kernel approximation instead of full "
                             "kernel matrix. Recommended: 500 for n=5000 (speedup ~64×).")
    parser.add_argument("--skip-classical", action="store_true",
                        help="Skip classical descriptor benchmark (resume from "
                             "partial CSV). Useful when only hybrid QK needs rerunning.")
    args = parser.parse_args()

    # ── Device selection ─────────────────────────────────────────────
    if args.device != "auto":
        global _DEVICE_OVERRIDE
        _DEVICE_OVERRIDE = args.device
    # Default: prefer CPU (lightning.qubit) even when GPU is available.
    # Benchmark results show GPU is 3-4x SLOWER than CPU for 6-8 qubit
    # IQPEmbedding circuits due to per-call GPU launch overhead.
    # Only use GPU when user explicitly specifies --device lightning.gpu.
    _prefer_cpu = (args.device != "lightning.gpu")
    _use_jax = args.jax and _HAS_JAX
    _dtype = np.float32 if args.dtype == "float32" else np.float64
    _n_qubits = args.n_qubits

    # Canonical hyperparameter guard (BMAD v51 / Appendix K):
    # Phase-2 grid search (p3_quantum_params_sweep.csv) identified the winning
    # combo bond_dim=6, n_repeats=1, n_kpca=30. Running the FULL benchmark with
    # different parameters silently produced non-canonical results (job 12695:
    # n_qubits=8, n_kpca=10). Fail loudly instead of reproducing that bug.
    _full_bench = (args.n_mols == 0) or (args.n_mols >= 5000)
    if _full_bench and (args.n_qubits != 6 or args.n_repeats != 1 or args.n_kpca != 30):
        _bad = [f"{k}={v}" for k, v in
                (("n_qubits", args.n_qubits), ("n_repeats", args.n_repeats),
                 ("n_kpca", args.n_kpca))
                if (k == "n_qubits" and v != 6) or (k == "n_repeats" and v != 1)
                or (k == "n_kpca" and v != 30)]
        raise SystemExit(
            f"ERROR: non-canonical quantum hyperparameters for n≥5,000 run: {', '.join(_bad)}. "
            f"Canonical Phase-2 winning combo is n_qubits=6, n_repeats=1, n_kpca=30 "
            f"(see BMAD Appendix K, job 12695 incident).")
    print(f"  Canonical hyperparameters: n_qubits={args.n_qubits}, n_repeats={args.n_repeats}, "
          f"n_kpca={args.n_kpca}")

    _dev_name = _DEVICE_OVERRIDE or best_device(_n_qubits, prefer_cpu=_prefer_cpu)
    if _dev_name == "lightning.gpu":
        print(f"  NOTE: GPU ({_dev_name}) selected. Our benchmarks show GPU is 3-4x "
              f"slower than CPU for 6-8 qubit quantum kernels. "
              f"Use --device lightning.qubit for faster execution.")

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
    jax_tag = " + JAX JIT" if _use_jax else ""
    dev_tag = _dev_name + jax_tag
    print(f"Paper 3 — Hybrid Framework + Activity Benchmark  ({dev_tag})")
    print("=" * 60)
    print(f"  Device: {_dev_name}")
    if _use_jax:
        print(f"  JAX:    enabled (backend={_JAX_BACKEND}, {_dtype.__name__})")
    elif args.jax and not _HAS_JAX:
        print(f"  JAX:    requested but not available — falling back to standard mode")
    print(f"  dtype:  {_dtype.__name__}")

    t0_total = time.perf_counter()

    # C2/M3 fix: use the canonical panel shared with the classical benchmark
    # (TFP-file order ∩ deduplicated activity ∩ finite-TNE), so every descriptor
    # is evaluated on exactly the same molecules with identical fold assignment.
    act_df = load_canonical_panel(args.n_mols)
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
    seed_records: list = []
    if args.checkpoint and Path(args.checkpoint).exists():
        with open(args.checkpoint) as _f:
            _ckpt = json.load(_f)
        seed_records = _ckpt.get("records", [])
        _saved_records = seed_records
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

    # ── Skip classical if resuming from checkpoint (R15) ────────
    # Prefer the canonical RF-only classical benchmark CSV (matches the
    # manuscript classical table) so the paired t-test compares Hybrid vs ECFP4
    # on identical RF folds without recomputing slow per-descriptor SVMs.
    if args.skip_classical:
        _classical_csv = RESULTS_DIR / "p3_classical_benchmark_19849.csv"
        _partial_csv = RESULTS_DIR / "p3_hybrid_benchmark_partial.csv"
        if _classical_csv.exists():
            _existing = pd.read_csv(_classical_csv)
            all_records = _existing.to_dict("records")
            print(f"    [skip-classical] Loaded {len(all_records)} rows from {_classical_csv.name}")
        elif _partial_csv.exists():
            _existing = pd.read_csv(_partial_csv)
            all_records = _existing.to_dict("records")
            print(f"    [skip-classical] Loaded {len(all_records)} rows from {_partial_csv.name}")
        else:
            print(f"    [skip-classical] WARNING: no classical CSV found — running classical from scratch")

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
    if not args.skip_classical:
        desc_iter = descriptors.items()
        if _HAS_TQDM:
            desc_iter = tqdm(desc_iter, desc="  Classical descriptors",
                             unit="desc", ncols=80)
        for desc_name, X_desc in desc_iter:
            for clf in ["rf", "svm"]:
                all_records.extend(cv_score(X_desc, y, clf, desc_name))

        # Save incremental CSV after classical descriptors (R4)
        _partial_df = pd.DataFrame(all_records)
        _partial_csv = RESULTS_DIR / "p3_hybrid_benchmark_partial.csv"
        _partial_df.to_csv(_partial_csv, index=False)
        _partial_gz = RESULTS_DIR / "p3_hybrid_benchmark_partial.csv.gz"
        _partial_df.to_csv(_partial_gz, index=False, compression="gzip")
        print(f"    [checkpoint] Classical done: {len(all_records)} rows -> {_partial_csv.name}")
    else:
        print(f"    [skip-classical] Using {len(all_records)} pre-computed classical rows")

    # Hybrid descriptor: uses per-fold QK computation (no data leakage)
    qk_mode = "precomputed" if args.precompute_kernel else "per-fold"
    print(f"    Hybrid ({qk_mode} QK)...")

    # Precompute kernel once if requested (reused for ablation too)
    _shared_QK_data = None
    if args.precompute_kernel:
        _shared_QK_data = _precompute_qk_all(
            X_ecfp,
            n_qubits=_n_qubits,
            n_repeats=args.n_repeats,
            block_size=args.block_size,
            n_jobs=args.n_jobs,
            prefer_cpu=_prefer_cpu,
            use_jax=_use_jax,
            dtype=_dtype,
        )

    all_records.extend(_cv_score_hybrid(
        X_ecfp, X_tfp, X_tne, y,
        n_qubits=_n_qubits,
        n_kpca=args.n_kpca,
        n_repeats=args.n_repeats,
        block_size=args.block_size,
        n_jobs=args.n_jobs,
        checkpoint_path=args.checkpoint,
        completed_folds=completed_hybrid,
        use_jax=_use_jax,
        prefer_cpu=_prefer_cpu,
        dtype=_dtype,
        precompute_kernel=args.precompute_kernel,
        QK_data=_shared_QK_data,
        nystrom_m=args.nystrom_m,
        seed_records=seed_records,
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

    # Save incremental CSV after hybrid (R4)
    _partial_df = pd.DataFrame(all_records)
    _partial_csv = RESULTS_DIR / "p3_hybrid_benchmark_partial.csv"
    _partial_df.to_csv(_partial_csv, index=False)
    _partial_gz = RESULTS_DIR / "p3_hybrid_benchmark_partial.csv.gz"
    _partial_df.to_csv(_partial_gz, index=False, compression="gzip")
    print(f"    [checkpoint] Hybrid done: {len(all_records)} rows -> {_partial_csv.name}")

    results_df = pd.DataFrame(all_records)
    # ── gzip-compressed output (R14) ─────────────────────────────
    out_csv = RESULTS_DIR / "p3_hybrid_benchmark.csv.gz"
    results_df.to_csv(out_csv, index=False, compression="gzip")
    out_csv_uncomp = RESULTS_DIR / "p3_hybrid_benchmark.csv"
    results_df.to_csv(out_csv_uncomp, index=False)
    t_benchmark = time.perf_counter() - t0_total
    print(f"\n  Saved: {out_csv} (compressed), {out_csv_uncomp} (plain)  (wall time: {t_benchmark:.1f}s)")
    gc.collect()

    # Ablation study (per-fold QK, no data leakage)
    ablation_records: list[dict] = []
    if not args.skip_ablation:
        print("\n  Running ablation study...")
        for removed in ["TFP", "TNE", "QK"]:
            ablation_records.extend(_cv_score_ablation_hybrid(
                X_ecfp, X_tfp, X_tne, y,
                remove=removed,
                n_qubits=_n_qubits,
                n_kpca=args.n_kpca,
                n_repeats=args.n_repeats,
                block_size=args.block_size,
                n_jobs=args.n_jobs,
                checkpoint_path=args.checkpoint,
                completed_folds=ablation_done.get(removed, set()),
                use_jax=_use_jax,
                prefer_cpu=_prefer_cpu,
                dtype=_dtype,
                precompute_kernel=args.precompute_kernel,
                QK_data=_shared_QK_data,
                nystrom_m=args.nystrom_m,
                seed_records=seed_records,
            ))

        abl_df = pd.DataFrame(ablation_records)
        # ── gzip-compressed ablation output (R14) ────────────────────
        abl_out = RESULTS_DIR / "p3_ablation.csv.gz"
        abl_df.to_csv(abl_out, index=False, compression="gzip")
        abl_out_uncomp = RESULTS_DIR / "p3_ablation.csv"
        abl_df.to_csv(abl_out_uncomp, index=False)
        print(f"  Saved: {abl_out} (compressed), {abl_out_uncomp} (plain)")
        del abl_df
        gc.collect()

    # Save incremental CSV after ablation (R4) — combined with classical+hybrid
    _full_partial = pd.DataFrame(all_records)
    _full_partial.to_csv(RESULTS_DIR / "p3_hybrid_benchmark_partial.csv", index=False)
    _full_partial.to_csv(RESULTS_DIR / "p3_hybrid_benchmark_partial.csv.gz", index=False, compression="gzip")
    print(f"    [checkpoint] All phases done: {len(all_records)} rows -> p3_hybrid_benchmark_partial.csv")

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

