#!/usr/bin/env python3
"""
P7 Phase 6 — Optuna Hyperparameter Optimisation for QFE and Quantum Models.

Scientific rationale
--------------------
Phases 4–5 established the canonical QFE 4q-d1-rzz configuration via manual
ablation (qubit count only). Phase 6 performs a systematic, multi-dimensional
HPO over the full QFE design space using Optuna (TPE sampler) to determine
whether a better configuration can close the ~2.5% gap vs. the classical ECFP4
baseline on the P3 subsample benchmark.

The same frozen subsample used in Phase 4 is re-used here (SHA-256:
d781d9c43923e3d5bbbbbb78dd572c6b091cbceea8946110c3e1dc5e980b5f0a).
This guarantees a fair apples-to-apples comparison between the Phase 4
canonical AUC (0.8474) and any HPO-tuned result.

Search space (QFE)
------------------
Circuit:
    n_qubits        : {4, 6, 8}
    n_layers        : {1, 2, 3}
    entangling      : {rzz, cnot, cz, none}

Encoder (ECFP4 → qubit features):
    hidden_dim      : {64, 128, 256}   (ECFP4 → hidden → n_qubits)

Optimiser:
    lr              : log-uniform [1e-4, 1e-2]
    batch_size      : {8, 16, 32}
    epochs          : {60, 80, 100}
    weight_decay    : log-uniform [1e-6, 1e-3]

Regularisation:
    dropout_rate    : uniform [0.0, 0.5]

For the ECFP4-RBF SVM baseline (fast oracle comparison):
    C               : log-uniform [0.01, 100]
    gamma           : {scale, auto}

Strategy
--------
- Sampler   : TPEsample (Optuna default; efficient for mixed integer/continuous spaces)
- Pruner     : MedianPruner (prune unpromising trials at intermediate epochs)
- Direction : maximise ROC-AUC (primary); Brier score logged as secondary
- n_trials  : configurable (default 50 for QFE, 30 for ECFP4 oracle)
- CV         : 3-fold stratified (inner loop only; same P3 subsample)
- Budget     : each trial uses the same frozen subsample (n=1000, seed=42)

Provenance rules (AGENTS.md §4)
--------------------------------
1. Subsample SHA-256 verified against Phase 4 canonical before any trial.
2. Each trial is logged with: trial number, hyperparameters, seed, AUC, Brier,
   gradient norm statistics, runtime.
3. Best trial parameters are written to a frozen JSON artifact BEFORE any
   evaluation on hold-out data.
4. HPO results are EXPLORATORY until re-run with canonical 5-fold CV using the
   best parameters — that re-run produces the CANONICAL result.
5. Optuna study is persisted to SQLite (``results/phase4_hpo/optuna_study.db``)
   for resumability; journal file is also saved.

Outputs
-------
results/phase4_hpo/
    qfe_hpo_study.db                  Optuna SQLite study (resumable)
    qfe_hpo_all_trials.csv            per-trial metrics table
    qfe_hpo_best_params.json          best trial parameters (frozen)
    qfe_hpo_summary.json              run provenance + top-5 trials
    ecfp4_hpo_all_trials.csv          ECFP4 SVM oracle search
    ecfp4_hpo_best_params.json        best ECFP4 SVM parameters
    qfe_hpo_importance.png            hyperparameter importance plot
    qfe_hpo_optimization_history.png  optimisation history plot
    qfe_hpo_parallel_coordinate.png   parallel coordinate plot

Usage
-----
    # Full QFE search (50 trials, 3-fold CV on P3 subsample n=1000):
    python scripts/p7_phase6_qfe_optuna_hpo.py \\
        --data  data/p3_benchmark/p3_benchmark_19849.csv \\
        --output results/phase4_hpo/ \\
        --n-sample 1000 \\
        --n-trials-qfe 50 \\
        --n-trials-ecfp4 30 \\
        --cv-folds 3 \\
        --seed 42

    # Quick smoke-test (5 trials):
    python scripts/p7_phase6_qfe_optuna_hpo.py \\
        --data  data/p3_benchmark/p3_benchmark_19849.csv \\
        --output results/phase4_hpo/ \\
        --n-trials-qfe 5 --n-trials-ecfp4 5 \\
        --cv-folds 2 --seed 42

    # Resume an interrupted study:
    python scripts/p7_phase6_qfe_optuna_hpo.py \\
        --data  data/p3_benchmark/p3_benchmark_19849.csv \\
        --output results/phase4_hpo/ \\
        --resume --n-trials-qfe 50 --seed 42
"""

import argparse
import hashlib
import json
import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Suppress noisy PennyLane / PyTorch deprecation warnings during HPO
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

import torch
import torch.nn as nn
import torch.optim as optim
import pennylane as qml

from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

import optuna
from optuna.samplers import TPESampler
from optuna.pruners import MedianPruner
import optuna.visualization as ov

# ── Provenance constant (Phase 4 canonical subsample) ─────────────────────────
PHASE4_SUBSAMPLE_SHA256 = "d781d9c43923e3d5bbbbbb78dd572c6b091cbceea8946110c3e1dc5e980b5f0a"
PHASE4_QFE_AUC          = 0.8474   # canonical Phase 4 result (4q-d1-rzz)
PHASE4_ECFP4_AUC        = 0.8693   # local ECFP4 baseline on same subsample
P3_CANONICAL_ECFP4_AUC  = 0.9475   # P3 full-dataset canonical

# Logging
logger = logging.getLogger("p7_phase6_hpo")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# ── Fingerprint helper ─────────────────────────────────────────────────────────

def smiles_to_ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray | None:
    """ECFP4 Morgan fingerprint (radius 2) as float32 bit-vector. Returns None on failure."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    fp  = gen.GetFingerprint(mol)
    arr = np.zeros(n_bits, dtype=np.float32)
    for idx in fp.GetOnBits():
        arr[idx] = 1.0
    return arr


def dataframe_sha256(df: pd.DataFrame, smiles_col: str) -> str:
    """Stable SHA-256 of a DataFrame sorted by SMILES column."""
    buf = df.sort_values(smiles_col).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(buf).hexdigest()


# ── Data loading and subsample preparation ────────────────────────────────────

def load_subsample(
    data_path: Path,
    n_sample: int,
    seed: int,
    fp_size: int = 2048,
) -> tuple[np.ndarray, np.ndarray, str]:
    """
    Load P3 benchmark, draw stratified subsample (identical to Phase 4),
    compute ECFP4 fingerprints, verify SHA-256 against Phase 4 canonical.

    Returns
    -------
    fps    : (n_sample, fp_size) float32 fingerprint matrix
    labels : (n_sample,) int binary labels
    sha256 : subsample SHA-256
    """
    logger.info("Loading P3 benchmark from %s", data_path)
    df = pd.read_csv(data_path)

    # Column detection — P3 benchmark uses 'SMILES' and 'activity_label'
    smiles_col = "SMILES" if "SMILES" in df.columns else "smiles"
    label_col  = "activity_label" if "activity_label" in df.columns else "label"
    df = df.dropna(subset=[smiles_col, label_col]).reset_index(drop=True)

    logger.info("Full benchmark: %d molecules (%d active / %d inactive)",
                len(df),
                (df[label_col] == 1).sum(),
                (df[label_col] == 0).sum())

    # Stratified subsample — must match Phase 4 exactly (same splitter, same seed)
    sss = StratifiedShuffleSplit(n_splits=1, test_size=n_sample, random_state=seed)
    _, sub_idx = next(sss.split(df[smiles_col], df[label_col]))
    df_sub = df.iloc[sub_idx].reset_index(drop=True)
    if "mol_id" not in df_sub.columns:
        df_sub.insert(0, "mol_id", [f"MOL{i:05d}" for i in range(len(df_sub))])

    sha256 = dataframe_sha256(df_sub, smiles_col)
    logger.info("Subsample SHA-256: %s", sha256)

    if sha256 != PHASE4_SUBSAMPLE_SHA256:
        logger.warning(
            "SHA-256 MISMATCH with Phase 4 canonical!\n"
            "  Expected : %s\n"
            "  Got      : %s\n"
            "  Comparison with Phase 4 AUC may not be valid.",
            PHASE4_SUBSAMPLE_SHA256, sha256,
        )
    else:
        logger.info("✓ SHA-256 matches Phase 4 canonical subsample.")

    # ECFP4 fingerprints
    logger.info("Computing ECFP4 fingerprints (fp_size=%d)...", fp_size)
    fps_list, labels_list, n_invalid = [], [], 0
    for _, row in df_sub.iterrows():
        fp = smiles_to_ecfp4(row[smiles_col], fp_size)
        if fp is None:
            n_invalid += 1
            continue
        fps_list.append(fp)
        labels_list.append(int(row[label_col]))

    if n_invalid:
        logger.warning("%d invalid SMILES dropped.", n_invalid)

    fps    = np.stack(fps_list, axis=0)   # (N, fp_size)
    labels = np.array(labels_list, dtype=np.int32)
    logger.info("Fingerprint matrix: %s | Labels: %d active / %d inactive",
                fps.shape, labels.sum(), (labels == 0).sum())

    return fps, labels, sha256


# ── Quantum circuit construction ───────────────────────────────────────────────

def build_qfe_circuit(n_qubits: int, n_layers: int, entangling: str, backend: str):
    """
    Construct a PennyLane QNode for the QFE forward pass.

    Identical architecture to Phase 4/5 scripts.  The returned callable
    accepts (inputs, theta_sq, theta_ent) and returns a list of Pauli-Z
    expectation values.
    """
    dev = qml.device(backend, wires=n_qubits)

    @qml.qnode(dev, interface="torch", diff_method="backprop")
    def circuit(inputs, theta_sq, theta_ent):
        for layer in range(n_layers):
            # Angle encoding
            for q in range(n_qubits):
                qml.RY(inputs[q], wires=q)
            # Single-qubit variational layer
            for q in range(n_qubits):
                qml.RX(theta_sq[layer, q, 0], wires=q)
                qml.RZ(theta_sq[layer, q, 1], wires=q)
            # Entangling layer
            for q in range(n_qubits - 1):
                if entangling == "rzz":
                    qml.IsingZZ(theta_ent[layer, q], wires=[q, q + 1])
                elif entangling == "cnot":
                    qml.CNOT(wires=[q, q + 1])
                elif entangling == "cz":
                    qml.CZ(wires=[q, q + 1])
                # "none" → no entangling gate
        return [qml.expval(qml.PauliZ(q)) for q in range(n_qubits)]

    return circuit


# ── QFE hybrid model ──────────────────────────────────────────────────────────

class QFEModel(nn.Module):
    """
    ECFP4 fingerprint → classical encoder → quantum circuit → classical decoder.

    Architecture (identical to Phase 4/5, extended to support HPO search space):
        encoder  : Linear(fp_dim, hidden_dim) → ReLU → Linear(hidden_dim, n_qubits) → Tanh → ×π
        quantum  : n_layers of (RY encoding + RX/RZ variational + entangling)
        decoder  : Linear(n_qubits, 32) → ReLU → Dropout(p) → Linear(32, 1) → Sigmoid
    """

    def __init__(
        self,
        fp_dim: int,
        n_qubits: int,
        n_layers: int,
        entangling: str,
        backend: str,
        hidden_dim: int = 128,
        dropout_rate: float = 0.2,
    ):
        super().__init__()
        self.n_qubits    = n_qubits
        self.n_layers    = n_layers
        self.hidden_dim  = hidden_dim

        self.encoder = nn.Sequential(
            nn.Linear(fp_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_qubits),
            nn.Tanh(),
        )
        self.circuit   = build_qfe_circuit(n_qubits, n_layers, entangling, backend)
        self.theta_sq  = nn.Parameter(torch.randn(n_layers, n_qubits, 2) * 0.01)
        self.theta_ent = nn.Parameter(torch.randn(n_layers, max(n_qubits - 1, 1)) * 0.01)
        self.decoder   = nn.Sequential(
            nn.Linear(n_qubits, 32),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, fp: torch.Tensor) -> torch.Tensor:
        """Process a single fingerprint vector or a 1D batch."""
        if fp.dim() == 1:
            fp = fp.unsqueeze(0)
        preds = []
        for i in range(fp.shape[0]):
            compressed = self.encoder(fp[i])
            inputs     = compressed * torch.tensor(np.pi, dtype=torch.float32)
            q_out      = self.circuit(inputs, self.theta_sq, self.theta_ent)
            q_feat     = torch.stack(q_out).float()
            out        = self.decoder(q_feat.unsqueeze(0))
            preds.append(out.squeeze())
        return torch.stack(preds)


# ── Training loop ─────────────────────────────────────────────────────────────

def train_qfe(
    model: QFEModel,
    fps: np.ndarray,
    labels: np.ndarray,
    train_idx: np.ndarray,
    *,
    epochs: int,
    lr: float,
    batch_size: int,
    patience: int = 10,
    weight_decay: float = 1e-5,
    seed: int = 42,
    trial: optuna.Trial | None = None,
    fold: int = 0,
) -> tuple[QFEModel, list[float]]:
    """
    Mini-batch Adam training with cosine-annealing LR and early stopping.

    If an Optuna ``trial`` is provided, intermediate AUC values are reported
    for pruning (MedianPruner).
    """
    torch.manual_seed(seed)
    device = "cpu"

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    fps_t    = [torch.FloatTensor(fps[i]).to(device) for i in train_idx]
    labels_t = torch.FloatTensor(labels[train_idx]).to(device)

    best_loss        = float("inf")
    patience_counter = 0
    best_state       = None
    grad_norms: list[float] = []

    n_train  = len(fps_t)
    idx_list = list(range(n_train))
    rng      = np.random.default_rng(seed)

    for epoch in range(epochs):
        model.train()
        rng.shuffle(idx_list)
        epoch_loss = 0.0

        for start in range(0, n_train, batch_size):
            batch_idx = idx_list[start: start + batch_size]
            optimizer.zero_grad()
            batch_loss = torch.tensor(0.0, device=device, requires_grad=True)

            for bi in batch_idx:
                pred       = model(fps_t[bi])
                loss_      = criterion(pred, labels_t[bi].unsqueeze(0))
                batch_loss = batch_loss + loss_

            batch_loss = batch_loss / max(len(batch_idx), 1)
            batch_loss.backward()

            gnorm = sum(
                p.grad.norm().item() ** 2
                for p in model.parameters()
                if p.grad is not None
            ) ** 0.5
            grad_norms.append(gnorm)

            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += batch_loss.item()

        scheduler.step()
        avg_loss = epoch_loss / max(1, n_train // max(batch_size, 1))

        # Early stopping
        if avg_loss < best_loss:
            best_loss        = avg_loss
            patience_counter = 0
            best_state       = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

        # Optuna intermediate reporting for pruning (every 5 epochs)
        if trial is not None and (epoch + 1) % 5 == 0:
            # Report a proxy metric (negative loss) for pruning decisions
            trial.report(-avg_loss, step=fold * epochs + epoch)
            if trial.should_prune():
                raise optuna.TrialPruned()

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, grad_norms


def evaluate_qfe(
    model: QFEModel,
    fps: np.ndarray,
    labels: np.ndarray,
    test_idx: np.ndarray,
) -> dict[str, float]:
    """Return AUC, Brier, and gradient norm stats on test_idx."""
    device = "cpu"
    model.eval()
    probs = []
    with torch.no_grad():
        for i in test_idx:
            fp_t = torch.FloatTensor(fps[i]).to(device)
            prob = model(fp_t).item()
            probs.append(prob)
    y_true = labels[test_idx]
    probs  = np.array(probs)
    auc    = roc_auc_score(y_true, probs)
    brier  = brier_score_loss(y_true, probs)
    return {"auc": auc, "brier": brier}


# ── Gradient norm diagnostics ─────────────────────────────────────────────────

def gradient_diagnostics(grad_norms: list[float]) -> dict[str, float]:
    """Compute barren-plateau diagnostics from a list of gradient norms."""
    arr = np.array(grad_norms)
    if len(arr) == 0:
        return {"mean": 0.0, "min": 0.0, "max": 0.0,
                "pct_below_1e6": 100.0, "barren_plateau": True}
    return {
        "mean":           float(arr.mean()),
        "std":            float(arr.std()),
        "min":            float(arr.min()),
        "max":            float(arr.max()),
        "pct_below_1e6":  float((arr < 1e-6).mean() * 100),
        "barren_plateau": bool((arr < 1e-6).mean() > 0.01),
    }


# ── Optuna objective — QFE ────────────────────────────────────────────────────

def make_qfe_objective(
    fps: np.ndarray,
    labels: np.ndarray,
    cv_folds: int,
    backend: str,
    fp_size: int,
    seed: int,
):
    """
    Return an Optuna objective function for QFE hyperparameter search.

    The objective performs cv_folds-fold stratified CV and returns the mean
    validation AUC as the optimisation target.
    """
    kf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)

    def objective(trial: optuna.Trial) -> float:
        # ── Circuit hyperparameters ────────────────────────────────────────
        n_qubits   = trial.suggest_categorical("n_qubits",   [4, 6, 8])
        n_layers   = trial.suggest_categorical("n_layers",   [1, 2, 3])
        entangling = trial.suggest_categorical("entangling", ["rzz", "cnot", "cz", "none"])

        # ── Encoder hyperparameters ────────────────────────────────────────
        hidden_dim   = trial.suggest_categorical("hidden_dim",   [64, 128, 256])
        dropout_rate = trial.suggest_float("dropout_rate", 0.0, 0.5)

        # ── Optimiser hyperparameters ──────────────────────────────────────
        lr           = trial.suggest_float("lr", 1e-4, 1e-2, log=True)
        batch_size   = trial.suggest_categorical("batch_size",  [8, 16, 32])
        epochs       = trial.suggest_categorical("epochs",      [60, 80, 100])
        weight_decay = trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True)

        fold_aucs: list[float] = []
        all_grad_norms: list[float] = []

        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(fps, labels)):
            model = QFEModel(
                fp_dim=fp_size,
                n_qubits=n_qubits,
                n_layers=n_layers,
                entangling=entangling,
                backend=backend,
                hidden_dim=hidden_dim,
                dropout_rate=dropout_rate,
            )

            model, grad_norms = train_qfe(
                model, fps, labels, train_idx,
                epochs=epochs,
                lr=lr,
                batch_size=batch_size,
                weight_decay=weight_decay,
                seed=seed + fold_idx,
                trial=trial,
                fold=fold_idx,
            )
            metrics = evaluate_qfe(model, fps, labels, val_idx)
            fold_aucs.append(metrics["auc"])
            all_grad_norms.extend(grad_norms)

        mean_auc = float(np.mean(fold_aucs))
        std_auc  = float(np.std(fold_aucs))

        # Store diagnostics as user attributes for post-hoc analysis
        trial.set_user_attr("fold_aucs",   fold_aucs)
        trial.set_user_attr("auc_std",     std_auc)
        diag = gradient_diagnostics(all_grad_norms)
        trial.set_user_attr("grad_mean",         diag["mean"])
        trial.set_user_attr("grad_pct_below_1e6", diag["pct_below_1e6"])
        trial.set_user_attr("barren_plateau",    diag["barren_plateau"])

        return mean_auc

    return objective


# ── Optuna objective — ECFP4 SVM oracle ──────────────────────────────────────

def make_ecfp4_objective(
    fps: np.ndarray,
    labels: np.ndarray,
    cv_folds: int,
    seed: int,
):
    """
    Optuna objective for ECFP4-RBF SVM search (fast oracle comparison).

    This is intentionally lightweight to provide a wall-clock-comparable
    classical reference against the QFE HPO budget.
    """
    kf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)

    def objective(trial: optuna.Trial) -> float:
        C     = trial.suggest_float("C",     0.01, 100.0, log=True)
        gamma = trial.suggest_categorical("gamma", ["scale", "auto"])

        fold_aucs: list[float] = []
        scaler = StandardScaler()

        for train_idx, val_idx in kf.split(fps, labels):
            X_tr = scaler.fit_transform(fps[train_idx].astype(np.float64))
            X_va = scaler.transform(fps[val_idx].astype(np.float64))
            y_tr = labels[train_idx]
            y_va = labels[val_idx]

            svm = SVC(kernel="rbf", C=C, gamma=gamma, probability=True,
                      random_state=seed, max_iter=2000)
            svm.fit(X_tr, y_tr)
            probs = svm.predict_proba(X_va)[:, 1]
            fold_aucs.append(roc_auc_score(y_va, probs))

        mean_auc = float(np.mean(fold_aucs))
        trial.set_user_attr("fold_aucs", fold_aucs)
        trial.set_user_attr("auc_std",   float(np.std(fold_aucs)))
        return mean_auc

    return objective


# ── Visualisation helpers ─────────────────────────────────────────────────────

def save_plots(study: optuna.Study, out_dir: Path, prefix: str) -> None:
    """Save Optuna visualisation plots (requires plotly). Skip silently if unavailable."""
    try:
        import plotly  # noqa: F401 — presence check

        fig = ov.plot_optimization_history(study)
        fig.write_image(str(out_dir / f"{prefix}_optimization_history.png"))

        fig = ov.plot_parallel_coordinate(study)
        fig.write_image(str(out_dir / f"{prefix}_parallel_coordinate.png"))

        try:
            fig = ov.plot_param_importances(study)
            fig.write_image(str(out_dir / f"{prefix}_importance.png"))
        except Exception:
            # fanova is optional; skip if not available
            pass

        logger.info("Optuna plots saved to %s/", out_dir)
    except ImportError:
        logger.warning("plotly not available — visualisation plots skipped.")
    except Exception as e:
        logger.warning("Plot generation failed: %s", e)


# ── Results serialisation ──────────────────────────────────────────────────────

def trials_to_dataframe(study: optuna.Study) -> pd.DataFrame:
    """Export completed trial metrics to a tidy DataFrame."""
    rows = []
    for t in study.trials:
        if t.state != optuna.trial.TrialState.COMPLETE:
            continue
        row = {"trial_number": t.number, "auc_mean": t.value}
        row.update({f"param_{k}": v for k, v in t.params.items()})
        row.update({f"attr_{k}":  v for k, v in t.user_attrs.items()})
        row["duration_sec"] = (
            (t.datetime_complete - t.datetime_start).total_seconds()
            if t.datetime_complete and t.datetime_start else None
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("auc_mean", ascending=False).reset_index(drop=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="P7 Phase 6 — Optuna HPO for QFE and quantum models"
    )
    parser.add_argument("--data",   type=str,
        default="data/p3_benchmark/p3_benchmark_19849.csv",
        help="Path to P3 benchmark CSV (default: data/p3_benchmark/p3_benchmark_19849.csv)")
    parser.add_argument("--output", type=str,
        default="results/phase4_hpo/",
        help="Output directory for HPO results")
    parser.add_argument("--n-sample",     type=int,   default=1000,
        help="Subsample size — must match Phase 4 (default: 1000)")
    parser.add_argument("--n-trials-qfe",  type=int,  default=50,
        help="Number of Optuna trials for QFE search (default: 50)")
    parser.add_argument("--n-trials-ecfp4", type=int, default=30,
        help="Number of Optuna trials for ECFP4-SVM search (default: 30)")
    parser.add_argument("--cv-folds",     type=int,   default=3,
        help="Inner CV folds for each trial (default: 3)")
    parser.add_argument("--fp-size",      type=int,   default=2048,
        help="ECFP4 fingerprint bit length (default: 2048)")
    parser.add_argument("--backend",      type=str,   default="default.qubit",
        help="PennyLane backend (default: default.qubit)")
    parser.add_argument("--seed",         type=int,   default=42,
        help="Global random seed (default: 42)")
    parser.add_argument("--resume",       action="store_true",
        help="Resume an existing Optuna study from the SQLite database")
    parser.add_argument("--skip-ecfp4",   action="store_true",
        help="Skip the ECFP4 SVM oracle search")
    parser.add_argument("--skip-plots",   action="store_true",
        help="Skip Optuna visualisation plots")
    args = parser.parse_args()

    # Silence Optuna info logging (trial-level noise)
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    t_global = time.time()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("P7 Phase 6 — Optuna Hyperparameter Optimisation")
    print("=" * 70)
    print(f"Data       : {args.data}")
    print(f"Subsample  : {args.n_sample} (seed={args.seed})")
    print(f"QFE trials : {args.n_trials_qfe}  |  CV folds: {args.cv_folds}")
    print(f"ECFP4 trials: {args.n_trials_ecfp4}")
    print(f"Backend    : {args.backend}")
    print(f"Output     : {args.output}")
    print(f"Resume     : {args.resume}")
    print("=" * 70)

    # ── 1. Load data ───────────────────────────────────────────────────────────
    fps, labels, sha256 = load_subsample(
        Path(args.data), args.n_sample, args.seed, args.fp_size
    )

    # ── 2. QFE Optuna study ────────────────────────────────────────────────────
    study_name = "p7_qfe_hpo"
    db_path    = out_dir / "qfe_hpo_study.db"
    storage    = f"sqlite:///{db_path}"

    if args.resume and db_path.exists():
        logger.info("Resuming existing study from %s", db_path)
        qfe_study = optuna.load_study(study_name=study_name, storage=storage)
        completed_before = len([
            t for t in qfe_study.trials
            if t.state == optuna.trial.TrialState.COMPLETE
        ])
        logger.info("  Existing completed trials: %d", completed_before)
    else:
        qfe_study = optuna.create_study(
            study_name=study_name,
            storage=storage,
            direction="maximize",
            sampler=TPESampler(seed=args.seed),
            pruner=MedianPruner(n_startup_trials=5, n_warmup_steps=10),
            load_if_exists=args.resume,
        )

    qfe_objective = make_qfe_objective(
        fps, labels,
        cv_folds=args.cv_folds,
        backend=args.backend,
        fp_size=args.fp_size,
        seed=args.seed,
    )

    logger.info("Starting QFE search: %d trials × %d-fold CV...",
                args.n_trials_qfe, args.cv_folds)
    print(f"\n[QFE] Running {args.n_trials_qfe} Optuna trials "
          f"({args.cv_folds}-fold CV each)...")
    t_qfe_start = time.time()

    qfe_study.optimize(
        qfe_objective,
        n_trials=args.n_trials_qfe,
        show_progress_bar=True,
        catch=(Exception,),       # log errors without aborting the study
    )

    t_qfe = time.time() - t_qfe_start
    logger.info("QFE search done in %.1fs", t_qfe)

    # Best QFE trial
    best_qfe = qfe_study.best_trial
    print(f"\n{'─'*60}")
    print(f"[QFE] Best trial #{best_qfe.number}:")
    print(f"  AUC  : {best_qfe.value:.4f}  (Phase 4 canonical: {PHASE4_QFE_AUC})")
    print(f"  Δ vs Phase 4  : {best_qfe.value - PHASE4_QFE_AUC:+.4f}")
    print(f"  Δ vs ECFP4 local: {best_qfe.value - PHASE4_ECFP4_AUC:+.4f}")
    print(f"  Parameters:")
    for k, v in best_qfe.params.items():
        print(f"    {k:20s}: {v}")
    print(f"{'─'*60}")

    # Save all trial results
    qfe_df = trials_to_dataframe(qfe_study)
    qfe_trials_path = out_dir / "qfe_hpo_all_trials.csv"
    qfe_df.to_csv(qfe_trials_path, index=False)
    logger.info("All QFE trials saved: %s", qfe_trials_path)

    # Freeze best params
    best_qfe_params = {
        "trial_number":  best_qfe.number,
        "auc_mean":      best_qfe.value,
        "auc_std":       best_qfe.user_attrs.get("auc_std", None),
        "fold_aucs":     best_qfe.user_attrs.get("fold_aucs", None),
        "params":        best_qfe.params,
        "grad_mean":     best_qfe.user_attrs.get("grad_mean", None),
        "barren_plateau": best_qfe.user_attrs.get("barren_plateau", None),
        "frozen_timestamp": pd.Timestamp.now().isoformat(),
        "status": "EXPLORATORY — requires canonical 5-fold CV re-run to become CANONICAL",
    }
    best_qfe_path = out_dir / "qfe_hpo_best_params.json"
    with open(best_qfe_path, "w") as f:
        json.dump(best_qfe_params, f, indent=2)
    logger.info("Best QFE params frozen: %s", best_qfe_path)

    # ── 3. ECFP4 SVM Optuna study (oracle comparison) ─────────────────────────
    best_ecfp4: optuna.Trial | None = None

    if not args.skip_ecfp4:
        ecfp4_study_name = "p7_ecfp4_hpo"
        ecfp4_study = optuna.create_study(
            study_name=ecfp4_study_name,
            direction="maximize",
            sampler=TPESampler(seed=args.seed + 1),
            load_if_exists=True,
        )
        ecfp4_objective = make_ecfp4_objective(
            fps, labels,
            cv_folds=args.cv_folds,
            seed=args.seed,
        )
        print(f"\n[ECFP4-SVM] Running {args.n_trials_ecfp4} Optuna trials...")
        t_ecfp4_start = time.time()
        ecfp4_study.optimize(
            ecfp4_objective,
            n_trials=args.n_trials_ecfp4,
            show_progress_bar=True,
            catch=(Exception,),
        )
        t_ecfp4 = time.time() - t_ecfp4_start
        logger.info("ECFP4 search done in %.1fs", t_ecfp4)

        best_ecfp4 = ecfp4_study.best_trial
        print(f"\n[ECFP4-SVM] Best trial #{best_ecfp4.number}:")
        print(f"  AUC  : {best_ecfp4.value:.4f}  (Phase 4 local: {PHASE4_ECFP4_AUC})")
        print(f"  Parameters: {best_ecfp4.params}")

        ecfp4_df = trials_to_dataframe(ecfp4_study)
        ecfp4_df.to_csv(out_dir / "ecfp4_hpo_all_trials.csv", index=False)

        best_ecfp4_params = {
            "trial_number": best_ecfp4.number,
            "auc_mean":     best_ecfp4.value,
            "auc_std":      best_ecfp4.user_attrs.get("auc_std", None),
            "fold_aucs":    best_ecfp4.user_attrs.get("fold_aucs", None),
            "params":       best_ecfp4.params,
            "frozen_timestamp": pd.Timestamp.now().isoformat(),
            "status": "EXPLORATORY — requires canonical 5-fold CV re-run to become CANONICAL",
        }
        with open(out_dir / "ecfp4_hpo_best_params.json", "w") as f:
            json.dump(best_ecfp4_params, f, indent=2)
    else:
        logger.info("ECFP4 oracle search skipped (--skip-ecfp4).")

    # ── 4. Visualisation ───────────────────────────────────────────────────────
    if not args.skip_plots:
        save_plots(qfe_study, out_dir, "qfe_hpo")

    # ── 5. Master summary JSON ─────────────────────────────────────────────────
    total_time = time.time() - t_global
    n_completed_qfe  = sum(1 for t in qfe_study.trials if t.state == optuna.trial.TrialState.COMPLETE)
    n_pruned_qfe     = sum(1 for t in qfe_study.trials if t.state == optuna.trial.TrialState.PRUNED)
    n_failed_qfe     = sum(1 for t in qfe_study.trials if t.state == optuna.trial.TrialState.FAIL)

    top5 = (
        qfe_df[["trial_number", "auc_mean",
                *[c for c in qfe_df.columns if c.startswith("param_")]]]
        .head(5)
        .to_dict(orient="records")
    )

    summary = {
        "phase":   "Phase 6 — Optuna HPO",
        "script":  "scripts/p7_phase6_qfe_optuna_hpo.py",
        "timestamp": pd.Timestamp.now().isoformat(),
        "data": {
            "source":           args.data,
            "n_sample":         args.n_sample,
            "subsample_sha256": sha256,
            "sha256_verified":  sha256 == PHASE4_SUBSAMPLE_SHA256,
            "seed":             args.seed,
        },
        "search_config": {
            "backend":          args.backend,
            "cv_folds":         args.cv_folds,
            "n_trials_qfe":     args.n_trials_qfe,
            "n_trials_ecfp4":   args.n_trials_ecfp4,
            "sampler":          "TPESampler",
            "pruner":           "MedianPruner(n_startup=5, n_warmup=10)",
            "direction":        "maximize AUC",
        },
        "qfe_search": {
            "n_completed": n_completed_qfe,
            "n_pruned":    n_pruned_qfe,
            "n_failed":    n_failed_qfe,
            "best_auc":    best_qfe.value,
            "best_params": best_qfe.params,
            "delta_vs_phase4_qfe":   round(best_qfe.value - PHASE4_QFE_AUC, 4),
            "delta_vs_phase4_ecfp4": round(best_qfe.value - PHASE4_ECFP4_AUC, 4),
            "delta_vs_p3_canonical": round(best_qfe.value - P3_CANONICAL_ECFP4_AUC, 4),
            "runtime_sec":     round(t_qfe, 1),
            "top_5_trials":    top5,
            "status": "EXPLORATORY",
        },
        "ecfp4_oracle": (
            {
                "best_auc":    best_ecfp4.value,
                "best_params": best_ecfp4.params,
                "delta_vs_phase4_ecfp4": round(best_ecfp4.value - PHASE4_ECFP4_AUC, 4),
                "runtime_sec": round(t_ecfp4, 1),
                "status": "EXPLORATORY",
            }
            if best_ecfp4 is not None else "SKIPPED"
        ),
        "phase4_references": {
            "QFE_4q_d1_rzz_cv5_AUC":   PHASE4_QFE_AUC,
            "ECFP4_local_cv5_AUC":      PHASE4_ECFP4_AUC,
            "ECFP4_P3_canonical_AUC":   P3_CANONICAL_ECFP4_AUC,
        },
        "next_step": (
            "Re-run best QFE params with canonical 5-fold CV (same subsample, "
            "n_splits=5, seed=42) to produce a CANONICAL result comparable to "
            "Phase 4 AUC 0.8474 ± 0.0129."
        ),
        "total_runtime_sec": round(total_time, 1),
    }

    summary_path = out_dir / "qfe_hpo_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Summary saved: %s", summary_path)

    # ── 6. Terminal summary ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("P7 Phase 6 — HPO Complete")
    print("=" * 70)
    print(f"Total runtime : {total_time:.1f}s")
    print(f"\n── QFE Results ──")
    print(f"  Completed trials  : {n_completed_qfe} / {args.n_trials_qfe}")
    print(f"  Pruned trials     : {n_pruned_qfe}")
    print(f"  Best AUC (HPO)    : {best_qfe.value:.4f}")
    print(f"  Phase 4 canonical : {PHASE4_QFE_AUC}   (4q-d1-rzz, fixed HPs)")
    print(f"  Improvement       : {best_qfe.value - PHASE4_QFE_AUC:+.4f}")
    print(f"\n── Best QFE configuration ──")
    for k, v in best_qfe.params.items():
        marker = " ← changed" if k == "n_qubits" and v != 4 else ""
        marker = marker or (" ← changed" if k == "n_layers"   and v != 1   else "")
        marker = marker or (" ← changed" if k == "entangling" and v != "rzz" else "")
        print(f"  {k:20s}: {v}{marker}")
    print(f"\n── Gap to classical baselines ──")
    print(f"  vs ECFP4 local (Phase 4): {best_qfe.value - PHASE4_ECFP4_AUC:+.4f}")
    print(f"  vs ECFP4 P3 canonical   : {best_qfe.value - P3_CANONICAL_ECFP4_AUC:+.4f}")

    if best_ecfp4 is not None:
        print(f"\n── ECFP4-SVM Oracle ──")
        print(f"  Best AUC (HPO)    : {best_ecfp4.value:.4f}  "
              f"(Phase 4 local: {PHASE4_ECFP4_AUC})")
        print(f"  Best params: {best_ecfp4.params}")

    print(f"\n── Status ──")
    print("  Results are EXPLORATORY until re-run with canonical 5-fold CV.")
    print(f"\n── Outputs ──")
    print(f"  {out_dir}/qfe_hpo_all_trials.csv")
    print(f"  {out_dir}/qfe_hpo_best_params.json   ← frozen best config")
    print(f"  {out_dir}/qfe_hpo_summary.json")
    print(f"  {out_dir}/qfe_hpo_study.db            ← resumable Optuna study")
    if not args.skip_plots:
        print(f"  {out_dir}/qfe_hpo_*.png")

    print("\n⚠  NEXT ACTION: Re-run best params with 5-fold CV to obtain a")
    print("   CANONICAL result comparable to Phase 4 (AUC 0.8474 ± 0.0129).")
    print("=" * 70)


if __name__ == "__main__":
    main()
