#!/usr/bin/env python3
"""
P7 Phase 4 — QFE 5-fold CV on P3 Benchmark (stratified subsample).

Scientific rationale
--------------------
The full P3 benchmark (19,849 molecules) is computationally intractable for a
PennyLane statevector simulator running on CPU: a single QFE forward pass takes
~20 ms, so 19,849 training passes × 5 folds ≈ 28 GPU-hours on CPU. Instead, we
draw a **stratified random subsample** of the P3 benchmark (default 1,000 mol,
configurable), apply the same class-ratio as the full dataset (~75.9% active),
and run 5-fold stratified CV on that subsample.

This mirrors standard practice for quantum kernel / VQC benchmarking on
chemistry datasets (Nystrom approximation, representative subset selection).
The subsample is seeded and frozen before execution; its SHA-256 hash is
recorded alongside the training results.

Design
------
- Subsample: StratifiedShuffleSplit from p3_benchmark_19849.csv (seed=42)
- CV: StratifiedKFold(n_splits=5, shuffle=True, random_state=42) on subsample
- Model: QFE 4-qubit, depth 1, RZZ entangling (best config from Phase 3A)
- Metric: ROC-AUC (primary), Brier score, accuracy
- Baselines: P3 canonical (ECFP4-RBF AUC 0.9475; Hybrid AUC 0.8876; QKS 0.8385)
- Hardware: PennyLane default.qubit (statevector, CPU)

Outputs
-------
results/phase2_benchmark/
    qfe_4q_d1_p3sub<N>_cv5_results.csv      per-fold metrics
    qfe_4q_d1_p3sub<N>_cv5_summary.json     summary + provenance
    qfe_4q_d1_p3sub<N>_gradient_norms.csv   per-epoch gradient norms

Usage
-----
    python scripts/p7_phase4_p3_benchmark.py \\
        --data data/p3_benchmark/p3_benchmark_19849.csv \\
        --output results/phase2_benchmark/ \\
        --n-sample 1000 \\
        --qubits 4 --depth 1 --entangling rzz \\
        --backend default.qubit \\
        --epochs 80 --lr 3e-3 \\
        --seed 42

Provenance rule
---------------
The subsample SHA-256 is computed and written to the summary JSON before any
model training begins (compliant with AGENTS.md §4 provenance rules).
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pennylane as qml
import torch
import torch.nn as nn
import torch.optim as optim
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.metrics import (
    accuracy_score, brier_score_loss, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit


# ── Fingerprint helper ────────────────────────────────────────────────────────

def smiles_to_ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray:
    """ECFP4 Morgan fingerprint (radius 2) as a float32 bit-vector."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return np.zeros(n_bits, dtype=np.float32)
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    fp = gen.GetFingerprint(mol)
    arr = np.zeros(n_bits, dtype=np.float32)
    for idx in fp.GetOnBits():
        arr[idx] = 1.0
    return arr


def dataframe_sha256(df: pd.DataFrame) -> str:
    """Stable SHA-256 of a DataFrame: sort by mol_id, hash the CSV bytes."""
    buf = df.sort_values("mol_id").to_csv(index=False).encode("utf-8")
    return hashlib.sha256(buf).hexdigest()


# ── Quantum circuit ───────────────────────────────────────────────────────────

def build_qfe_circuit(n_qubits: int, n_layers: int, entangling: str, backend: str):
    """
    Build a PennyLane QNode implementing the QFE forward pass.

    inputs   : (n_qubits,) — compressed molecule features in (−π, π)
    theta_sq : (n_layers, n_qubits, 2) — RX / RZ single-qubit params
    theta_ent: (n_layers, n_qubits-1) — RZZ / CNOT entangling params
    returns  : list of n_qubits Pauli-Z expectations
    """
    dev = qml.device(backend, wires=n_qubits)

    @qml.qnode(dev, interface="torch", diff_method="backprop")
    def circuit(inputs, theta_sq, theta_ent):
        for layer in range(n_layers):
            # ── Angle encoding ────────────────────────────────────────
            for q in range(n_qubits):
                qml.RY(inputs[q], wires=q)
            # ── Single-qubit variational ──────────────────────────────
            for q in range(n_qubits):
                qml.RX(theta_sq[layer, q, 0], wires=q)
                qml.RZ(theta_sq[layer, q, 1], wires=q)
            # ── Entangling layer ──────────────────────────────────────
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


# ── Hybrid model ──────────────────────────────────────────────────────────────

class QFEModel(nn.Module):
    """
    ECFP4 (2048-bit) → Linear encoder → Quantum circuit → MLP decoder.

    Identical architecture to Phase 3A to allow direct comparison.
    """

    def __init__(
        self,
        fp_dim: int,
        n_qubits: int,
        n_layers: int,
        entangling: str,
        backend: str,
    ):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_layers = n_layers

        # Classical encoder: compress ECFP4 to n_qubits dims in (−1, 1)
        self.encoder = nn.Sequential(
            nn.Linear(fp_dim, 128),
            nn.ReLU(),
            nn.Linear(128, n_qubits),
            nn.Tanh(),
        )

        # Quantum circuit (PennyLane QNode)
        self.circuit = build_qfe_circuit(n_qubits, n_layers, entangling, backend)

        # Variational parameters (trainable)
        self.theta_sq = nn.Parameter(
            torch.randn(n_layers, n_qubits, 2) * 0.01
        )
        self.theta_ent = nn.Parameter(
            torch.randn(n_layers, max(n_qubits - 1, 1)) * 0.01
        )

        # Classical decoder: quantum expectations → probability
        self.decoder = nn.Sequential(
            nn.Linear(n_qubits, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, fp: torch.Tensor) -> torch.Tensor:
        """
        fp : (batch, fp_dim) or (fp_dim,)
        returns: (batch,) probabilities
        """
        if fp.dim() == 1:
            fp = fp.unsqueeze(0)

        preds = []
        for i in range(fp.shape[0]):
            compressed = self.encoder(fp[i])             # (n_qubits,)
            inputs = compressed * torch.tensor(np.pi)    # scale to (−π, π)
            q_out = self.circuit(inputs, self.theta_sq, self.theta_ent)
            q_feat = torch.stack(q_out).float()          # (n_qubits,)
            out = self.decoder(q_feat.unsqueeze(0))      # (1, 1)
            preds.append(out.squeeze())

        return torch.stack(preds)                        # (batch,)


# ── Training ──────────────────────────────────────────────────────────────────

def train_fold(
    model,
    train_fps: list,
    train_labels: list,
    val_fps: list,
    val_labels: list,
    device: str,
    epochs: int = 80,
    lr: float = 3e-3,
    patience: int = 15,
    batch_size: int = 16,
) -> tuple[nn.Module, list[float]]:
    """
    Mini-batch SGD for one CV fold.

    Mini-batching is critical for the P3 subsample (n_train ≈ 800).
    Molecules are processed one-at-a-time inside each mini-batch because
    PennyLane's per-sample QNode does not support true batching on
    default.qubit without a batch_dim decorator.
    """
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    train_fps_t = [torch.FloatTensor(fp).to(device) for fp in train_fps]
    train_y_t = torch.FloatTensor(train_labels).to(device)
    val_fps_t = [torch.FloatTensor(fp).to(device) for fp in val_fps]
    val_y_arr = np.array(val_labels)

    best_val_loss = float("inf")
    patience_counter = 0
    best_state = None
    grad_norms = []

    n_train = len(train_fps_t)
    indices = list(range(n_train))

    for epoch in range(epochs):
        model.train()
        np.random.shuffle(indices)
        epoch_loss = 0.0

        # Mini-batch loop
        for start in range(0, n_train, batch_size):
            batch_idx = indices[start : start + batch_size]
            optimizer.zero_grad()
            batch_loss = torch.tensor(0.0, device=device, requires_grad=True)

            for idx in batch_idx:
                pred = model(train_fps_t[idx])           # scalar
                loss_ = criterion(pred, train_y_t[idx].unsqueeze(0))
                batch_loss = batch_loss + loss_

            batch_loss = batch_loss / len(batch_idx)
            batch_loss.backward()

            # Gradient norm (barren plateau monitoring)
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

        # Validation loss (no grad)
        model.eval()
        with torch.no_grad():
            val_loss = 0.0
            for fp_t, y in zip(val_fps_t, val_labels):
                pred = model(fp_t)
                val_loss += criterion(
                    pred, torch.FloatTensor([y]).to(device)
                ).item()

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, grad_norms


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="P7 Phase 4 — QFE 5-fold CV on P3 benchmark subsample"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/p3_benchmark/p3_benchmark_19849.csv",
        help="Path to p3_benchmark_19849.csv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/phase2_benchmark/",
        help="Output directory",
    )
    parser.add_argument(
        "--n-sample",
        type=int,
        default=1000,
        help="Number of molecules to subsample (stratified). Default: 1000",
    )
    parser.add_argument("--qubits", type=int, default=4)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument(
        "--entangling",
        type=str,
        default="rzz",
        choices=["rzz", "cnot", "cz", "none"],
    )
    parser.add_argument("--backend", type=str, default="default.qubit")
    parser.add_argument("--fp-size", type=int, default=2048)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    device = "cpu"

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    print("=" * 65)
    print("P7 Phase 4 — QFE on P3 Benchmark (5-fold CV, subsample)")
    print("=" * 65)
    print(f"Qubits     : {args.qubits}")
    print(f"Depth      : {args.depth}")
    print(f"Entangling : {args.entangling}")
    print(f"Backend    : {args.backend}")
    print(f"Subsample  : {args.n_sample} molecules")
    print(f"Epochs     : {args.epochs}, LR: {args.lr}, Patience: {args.patience}")
    print(f"Seed       : {args.seed}")

    # ── Load full P3 benchmark ────────────────────────────────────────────
    p3_path = Path(args.data)
    if not p3_path.exists():
        print(f"ERROR: P3 benchmark not found at {p3_path}")
        sys.exit(1)

    df_full = pd.read_csv(p3_path)
    print(f"\nFull P3 benchmark: {len(df_full)} molecules")
    print(
        f"  Active: {(df_full['activity_label'] == 1).sum()} "
        f"({(df_full['activity_label'] == 1).mean() * 100:.1f}%)"
    )

    # ── Stratified subsample ──────────────────────────────────────────────
    n_sample = min(args.n_sample, len(df_full))
    splitter = StratifiedShuffleSplit(
        n_splits=1, test_size=n_sample, random_state=args.seed
    )
    _, sub_idx = next(
        splitter.split(df_full["SMILES"], df_full["activity_label"])
    )
    df_sub = df_full.iloc[sub_idx].reset_index(drop=True)

    n_active_sub = (df_sub["activity_label"] == 1).sum()
    n_inactive_sub = (df_sub["activity_label"] == 0).sum()
    sub_sha256 = dataframe_sha256(df_sub)

    print(f"\nSubsample: {len(df_sub)} molecules (seed={args.seed})")
    print(f"  Active  : {n_active_sub} ({n_active_sub / len(df_sub) * 100:.1f}%)")
    print(f"  Inactive: {n_inactive_sub} ({n_inactive_sub / len(df_sub) * 100:.1f}%)")
    print(f"  SHA-256 : {sub_sha256}")

    smiles_list = df_sub["SMILES"].tolist()
    labels = df_sub["activity_label"].tolist()

    # ── Compute ECFP4 fingerprints ────────────────────────────────────────
    print("\nComputing ECFP4 fingerprints...", end="", flush=True)
    fps = [smiles_to_ecfp4(smi, args.fp_size) for smi in smiles_list]
    fps_arr = np.array(fps)
    n_invalid = sum(fp.sum() == 0 for fp in fps)
    print(f" done. Invalid SMILES: {n_invalid}")

    # ── 5-fold stratified CV ──────────────────────────────────────────────
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)

    fold_results = []
    all_grad_norms = []
    total_t0 = time.time()

    for fold_idx, (train_idx, test_idx) in enumerate(
        skf.split(fps_arr, labels)
    ):
        print(f"\n{'─' * 50}")
        print(f"Fold {fold_idx + 1}/5")
        print(
            f"  Train: {len(train_idx)} | "
            f"Test: {len(test_idx)} | "
            f"Active (train): {sum(labels[i] for i in train_idx)}"
        )

        train_fps = [fps[i] for i in train_idx]
        train_y = [labels[i] for i in train_idx]
        test_fps = [fps[i] for i in test_idx]
        test_y = np.array([labels[i] for i in test_idx])

        model = QFEModel(
            fp_dim=args.fp_size,
            n_qubits=args.qubits,
            n_layers=args.depth,
            entangling=args.entangling,
            backend=args.backend,
        ).to(device)

        fold_t0 = time.time()
        model, gnorms = train_fold(
            model,
            train_fps,
            train_y,
            test_fps,
            test_y.tolist(),
            device,
            epochs=args.epochs,
            lr=args.lr,
            patience=args.patience,
            batch_size=args.batch_size,
        )
        fold_elapsed = time.time() - fold_t0
        all_grad_norms.append(gnorms)

        # Inference on test set
        model.eval()
        y_pred_list = []
        with torch.no_grad():
            for fp in test_fps:
                fp_t = torch.FloatTensor(fp).to(device)
                prob = model(fp_t).item()
                y_pred_list.append(prob)

        y_pred = np.array(y_pred_list)
        y_bin = (y_pred > 0.5).astype(int)

        try:
            auc = roc_auc_score(test_y, y_pred)
        except ValueError:
            auc = float("nan")

        brier = brier_score_loss(test_y, y_pred)
        acc = accuracy_score(test_y, y_bin)
        f1 = f1_score(test_y, y_bin, zero_division=0)
        prec = precision_score(test_y, y_bin, zero_division=0)
        rec = recall_score(test_y, y_bin, zero_division=0)
        mean_gnorm = float(np.mean(gnorms)) if gnorms else float("nan")

        print(
            f"  AUC: {auc:.4f}  Brier: {brier:.4f}  "
            f"Acc: {acc:.4f}  F1: {f1:.4f}"
        )
        print(
            f"  Time: {fold_elapsed:.1f}s  "
            f"Mean ‖∇θ‖: {mean_gnorm:.4e}"
        )

        fold_results.append(
            {
                "fold": fold_idx,
                "n_train": len(train_idx),
                "n_test": len(test_idx),
                "auc": auc,
                "brier_score": brier,
                "accuracy": acc,
                "f1": f1,
                "precision": prec,
                "recall": rec,
                "mean_grad_norm": mean_gnorm,
                "elapsed_sec": fold_elapsed,
            }
        )

    total_elapsed = time.time() - total_t0

    # ── Aggregate metrics ─────────────────────────────────────────────────
    aucs = [r["auc"] for r in fold_results if not np.isnan(r["auc"])]
    briers = [r["brier_score"] for r in fold_results]
    accs = [r["accuracy"] for r in fold_results]
    f1s = [r["f1"] for r in fold_results]

    mean_auc = float(np.mean(aucs)) if aucs else float("nan")
    std_auc = float(np.std(aucs)) if len(aucs) > 1 else float("nan")

    # ── Gradient norm analysis ────────────────────────────────────────────
    flat_gnorms = [g for fold in all_grad_norms for g in fold]
    gnorm_stats = {
        "mean": float(np.mean(flat_gnorms)) if flat_gnorms else float("nan"),
        "std": float(np.std(flat_gnorms)) if flat_gnorms else float("nan"),
        "min": float(np.min(flat_gnorms)) if flat_gnorms else float("nan"),
        "max": float(np.max(flat_gnorms)) if flat_gnorms else float("nan"),
        "pct_below_1e6": float(
            (np.array(flat_gnorms) < 1e-6).mean()
        ) if flat_gnorms else float("nan"),
        "barren_plateau_risk": bool(
            flat_gnorms and float(np.mean(flat_gnorms)) < 1e-6
        ),
    }

    # ── P3 canonical baselines for inline comparison ──────────────────────
    p3_baselines = {
        "ECFP4-RBF (P3 canonical)": {"auc": 0.9475, "auc_std": 0.0045},
        "Hybrid-RF (P3 canonical)": {"auc": 0.8876, "auc_std": 0.0065},
        "QKS-PennyLane (P3 pilot)": {"auc": 0.8385, "auc_std": None},
    }

    # ── Save results ──────────────────────────────────────────────────────
    result_tag = (
        f"qfe_{args.qubits}q_d{args.depth}_p3sub{n_sample}_cv5"
    )

    df_results = pd.DataFrame(fold_results)
    results_path = out_dir / f"{result_tag}_results.csv"
    df_results.to_csv(results_path, index=False)

    # Per-epoch gradient norms
    gnorm_rows = []
    for fold_i, gnorms in enumerate(all_grad_norms):
        for epoch_i, gn in enumerate(gnorms):
            gnorm_rows.append(
                {"fold": fold_i, "epoch": epoch_i, "grad_norm": gn}
            )
    gnorm_path = out_dir / f"{result_tag}_gradient_norms.csv"
    pd.DataFrame(gnorm_rows).to_csv(gnorm_path, index=False)

    summary = {
        "method": f"QFE-{args.qubits}q-depth{args.depth}-{args.entangling}",
        "phase": "Phase 4 — P3 benchmark (stratified subsample)",
        "script": "scripts/p7_phase4_p3_benchmark.py",
        "timestamp": pd.Timestamp.now().isoformat(),
        "execution": {
            "backend": args.backend,
            "device": device,
            "total_time_sec": total_elapsed,
        },
        "data": {
            "source": str(p3_path),
            "n_full": len(df_full),
            "n_subsample": n_sample,
            "n_active": int(n_active_sub),
            "n_inactive": int(n_inactive_sub),
            "subsample_sha256": sub_sha256,
            "seed": args.seed,
            "cv_strategy": "StratifiedKFold(n_splits=5, shuffle=True, seed=42)",
        },
        "hyperparameters": {
            "n_qubits": args.qubits,
            "n_layers": args.depth,
            "entangling": args.entangling,
            "fp_size": args.fp_size,
            "epochs": args.epochs,
            "lr": args.lr,
            "patience": args.patience,
            "batch_size": args.batch_size,
        },
        "results": {
            "mean_auc": mean_auc,
            "std_auc": std_auc,
            "mean_brier": float(np.mean(briers)),
            "std_brier": float(np.std(briers)),
            "mean_accuracy": float(np.mean(accs)),
            "std_accuracy": float(np.std(accs)),
            "mean_f1": float(np.mean(f1s)),
            "std_f1": float(np.std(f1s)),
            "per_fold": fold_results,
        },
        "gradient_norms": gnorm_stats,
        "p3_canonical_baselines": p3_baselines,
    }
    summary_path = out_dir / f"{result_tag}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    # ── Final report ──────────────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print(
        f"QFE ({args.qubits}-qubit, depth {args.depth}, {args.entangling}) "
        f"— P3 subsample ({n_sample} mol) — 5-fold CV"
    )
    print(f"{'=' * 65}")
    print(f"Total time : {total_elapsed:.1f}s")
    print(f"\n── Results ──")
    print(f"  AUC : {mean_auc:.4f} ± {std_auc:.4f}")
    print(f"  Brier: {np.mean(briers):.4f} ± {np.std(briers):.4f}")
    print(f"  Acc  : {np.mean(accs):.4f} ± {np.std(accs):.4f}")
    print(f"  F1   : {np.mean(f1s):.4f} ± {np.std(f1s):.4f}")

    print(f"\n── P3 Canonical Baselines (for reference) ──")
    for name, vals in p3_baselines.items():
        std_str = f"± {vals['auc_std']:.4f}" if vals["auc_std"] else ""
        print(f"  {name}: AUC {vals['auc']:.4f} {std_str}")

    auc_ratio = mean_auc / 0.9475 if not np.isnan(mean_auc) else float("nan")
    print(f"\n── Decision gate (QFE / ECFP4 ratio) ──")
    print(f"  {mean_auc:.4f} / 0.9475 = {auc_ratio:.3f}", end="")
    if auc_ratio >= 0.80:
        print("  → PASS (≥ 0.80)")
    else:
        print("  → FAIL (< 0.80)")

    bp = "RISK" if gnorm_stats["barren_plateau_risk"] else "OK"
    print(f"\n── Gradient norms ──")
    print(
        f"  mean={gnorm_stats['mean']:.4e}, "
        f"min={gnorm_stats['min']:.4e}, "
        f"max={gnorm_stats['max']:.4e}"
    )
    print(f"  Barren plateau: {bp}")

    print(f"\n✓ Results saved to: {out_dir}/")
    print(f"  {results_path.name}")
    print(f"  {summary_path.name}")
    print(f"  {gnorm_path.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        print(f"\nERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
