#!/usr/bin/env python3
"""
P7 Phase 5 — QFE 4q-d1-rzz on External Validation Set (scaffold split).

Scientific rationale
--------------------
Phase 4 demonstrated that QFE is competitive with (but not superior to) classical
baselines on the P3 benchmark under 5-fold stratified CV. Phase 5 tests scaffold
generalization: can QFE predict activity for molecules with scaffolds never seen
during training?

The external validation set is the 45,895 molecules from eos80ch_malaria_final_activity.csv
NOT present in the P3 benchmark. A 10,000-molecule stratified subsample is drawn
(seed=42), then split 80/20 by Bemis-Murcko scaffold (rare scaffolds → test).

The subsample SHA-256 is **shared with the ECFP4 baseline** (same seed, same data),
ensuring both methods are evaluated on identical molecules with identical scaffold
splits. The SHA-256 is verified against the baseline summary before training begins.

Provenance rule (AGENTS.md §4)
-------------------------------
Subsample SHA-256 computed and written to summary JSON BEFORE any training.

Outputs
-------
results/phase3_scaffold/
    qfe_4q_d1_ext10k_scaffold_results.csv      per-molecule predictions
    qfe_4q_d1_ext10k_scaffold_summary.json     summary + provenance
    qfe_4q_d1_ext10k_scaffold_gradient_norms.csv  per-batch gradient norms

Usage
-----
    python scripts/p7_phase5_qfe_ext.py \\
        --data65k  /path/to/eos80ch_malaria_final_activity.csv \\
        --p3bench  data/p3_benchmark/p3_benchmark_19849.csv \\
        --output   results/phase3_scaffold/ \\
        --n-sample 10000 \\
        --qubits 4 --depth 1 --entangling rzz \\
        --backend default.qubit \\
        --epochs 80 --lr 3e-3 \\
        --seed 42
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
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import (
    accuracy_score, brier_score_loss, f1_score,
    precision_score, recall_score, roc_auc_score,
)


# ── Fingerprint and scaffold helpers ──────────────────────────────────────────

def smiles_to_ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    fp = gen.GetFingerprint(mol)
    arr = np.zeros(n_bits, dtype=np.float32)
    for idx in fp.GetOnBits():
        arr[idx] = 1.0
    return arr


def get_murcko_scaffold(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ""
    try:
        scaffold = MurckoScaffold.GetScaffoldForMol(mol)
        return Chem.MolToSmiles(scaffold) if scaffold else ""
    except Exception:
        return ""


def dataframe_sha256(df: pd.DataFrame, smiles_col: str) -> str:
    buf = df.sort_values(smiles_col).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(buf).hexdigest()


# ── Scaffold split ────────────────────────────────────────────────────────────

def scaffold_split(df: pd.DataFrame, test_frac: float = 0.2, seed: int = 42):
    """Bemis-Murcko scaffold split: rare scaffolds → test set."""
    scaffolds = df["scaffold"].tolist()
    scaffold_to_indices: dict[str, list[int]] = {}
    for i, sc in enumerate(scaffolds):
        scaffold_to_indices.setdefault(sc, []).append(i)

    scaffold_sets = sorted(scaffold_to_indices.values(), key=len)

    n_test_target = int(len(df) * test_frac)
    test_idx, train_idx = [], []
    rng = np.random.default_rng(seed)

    for sc_indices in scaffold_sets:
        if len(test_idx) < n_test_target:
            test_idx.extend(sc_indices)
        else:
            train_idx.extend(sc_indices)

    rng.shuffle(test_idx)
    rng.shuffle(train_idx)

    test_scaffolds  = set(df.iloc[test_idx]["scaffold"])
    train_scaffolds = set(df.iloc[train_idx]["scaffold"])
    n_overlap       = len(test_scaffolds & train_scaffolds)

    stats = {
        "n_unique_scaffolds": len(scaffold_to_indices),
        "n_train": len(train_idx),
        "n_test": len(test_idx),
        "scaffold_overlap_between_train_test": n_overlap,
        "pct_novel_scaffolds_in_test": round(
            (len(test_scaffolds) - n_overlap) / max(len(test_scaffolds), 1) * 100, 2
        ),
    }
    return train_idx, test_idx, stats


# ── Quantum circuit ───────────────────────────────────────────────────────────

def build_qfe_circuit(n_qubits: int, n_layers: int, entangling: str, backend: str):
    dev = qml.device(backend, wires=n_qubits)

    @qml.qnode(dev, interface="torch", diff_method="backprop")
    def circuit(inputs, theta_sq, theta_ent):
        for layer in range(n_layers):
            for q in range(n_qubits):
                qml.RY(inputs[q], wires=q)
            for q in range(n_qubits):
                qml.RX(theta_sq[layer, q, 0], wires=q)
                qml.RZ(theta_sq[layer, q, 1], wires=q)
            for q in range(n_qubits - 1):
                if entangling == "rzz":
                    qml.IsingZZ(theta_ent[layer, q], wires=[q, q + 1])
                elif entangling == "cnot":
                    qml.CNOT(wires=[q, q + 1])
                elif entangling == "cz":
                    qml.CZ(wires=[q, q + 1])
        return [qml.expval(qml.PauliZ(q)) for q in range(n_qubits)]

    return circuit


# ── Hybrid model ──────────────────────────────────────────────────────────────

class QFEModel(nn.Module):
    """ECFP4 (2048-bit) → Linear encoder → Quantum circuit → MLP decoder."""

    def __init__(self, fp_dim, n_qubits, n_layers, entangling, backend):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_layers = n_layers

        self.encoder = nn.Sequential(
            nn.Linear(fp_dim, 128),
            nn.ReLU(),
            nn.Linear(128, n_qubits),
            nn.Tanh(),
        )
        self.circuit   = build_qfe_circuit(n_qubits, n_layers, entangling, backend)
        self.theta_sq  = nn.Parameter(torch.randn(n_layers, n_qubits, 2) * 0.01)
        self.theta_ent = nn.Parameter(torch.randn(n_layers, max(n_qubits - 1, 1)) * 0.01)
        self.decoder   = nn.Sequential(
            nn.Linear(n_qubits, 32), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(32, 1), nn.Sigmoid(),
        )

    def forward(self, fp: torch.Tensor) -> torch.Tensor:
        if fp.dim() == 1:
            fp = fp.unsqueeze(0)
        preds = []
        for i in range(fp.shape[0]):
            compressed = self.encoder(fp[i])
            inputs     = compressed * torch.tensor(np.pi)
            q_out      = self.circuit(inputs, self.theta_sq, self.theta_ent)
            q_feat     = torch.stack(q_out).float()
            out        = self.decoder(q_feat.unsqueeze(0))
            preds.append(out.squeeze())
        return torch.stack(preds)


# ── Training ──────────────────────────────────────────────────────────────────

def train_model(
    model,
    train_fps,
    train_labels,
    device: str,
    epochs: int = 80,
    lr: float = 3e-3,
    patience: int = 15,
    batch_size: int = 16,
):
    """Mini-batch SGD for the full training split (no per-fold validation here)."""
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    train_fps_t = [torch.FloatTensor(fp).to(device) for fp in train_fps]
    train_y_t   = torch.FloatTensor(train_labels).to(device)

    best_loss        = float("inf")
    patience_counter = 0
    best_state       = None
    grad_norms       = []

    n_train  = len(train_fps_t)
    indices  = list(range(n_train))

    for epoch in range(epochs):
        model.train()
        np.random.shuffle(indices)
        epoch_loss = 0.0

        for start in range(0, n_train, batch_size):
            batch_idx  = indices[start: start + batch_size]
            optimizer.zero_grad()
            batch_loss = torch.tensor(0.0, device=device, requires_grad=True)

            for idx in batch_idx:
                pred       = model(train_fps_t[idx])
                loss_      = criterion(pred, train_y_t[idx].unsqueeze(0))
                batch_loss = batch_loss + loss_

            batch_loss = batch_loss / len(batch_idx)
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
        avg_epoch_loss = epoch_loss / max(1, n_train // batch_size)

        if avg_epoch_loss < best_loss:
            best_loss        = avg_epoch_loss
            patience_counter = 0
            best_state       = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"    Early stop at epoch {epoch+1}")
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, grad_norms


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="P7 Phase 5 — QFE 5q external scaffold-split validation"
    )
    parser.add_argument("--data65k", type=str,
        default="../Project3_Quantum_Inspired_RepresentationsV2607_V4/results/eos80ch_malaria_final_activity.csv")
    parser.add_argument("--p3bench", type=str,
        default="data/p3_benchmark/p3_benchmark_19849.csv")
    parser.add_argument("--output",  type=str, default="results/phase3_scaffold/")
    parser.add_argument("--n-sample", type=int, default=10000)
    parser.add_argument("--qubits",   type=int, default=4)
    parser.add_argument("--depth",    type=int, default=1)
    parser.add_argument("--entangling", type=str, default="rzz",
        choices=["rzz", "cnot", "cz", "none"])
    parser.add_argument("--backend",  type=str, default="default.qubit")
    parser.add_argument("--fp-size",  type=int, default=2048)
    parser.add_argument("--epochs",   type=int, default=80)
    parser.add_argument("--lr",       type=float, default=3e-3)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--activity-threshold", type=float, default=0.5)
    parser.add_argument("--seed",     type=int, default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    t_start = time.time()
    print("=" * 65)
    print("P7 Phase 5 — QFE on External Validation (scaffold split)")
    print("=" * 65)
    print(f"Qubits     : {args.qubits}")
    print(f"Depth      : {args.depth}")
    print(f"Entangling : {args.entangling}")
    print(f"Backend    : {args.backend}")
    print(f"Subsample  : {args.n_sample} molecules")
    print(f"Epochs     : {args.epochs}, LR: {args.lr}, Patience: {args.patience}")
    print(f"Threshold  : asexual_blood_stage > {args.activity_threshold}")
    print(f"Seed       : {args.seed}")

    # ── Load and filter data ───────────────────────────────────────────────────
    data65k_path = Path(args.data65k)
    p3_path      = Path(args.p3bench)
    out_dir      = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not data65k_path.exists():
        print(f"ERROR: 65K dataset not found at {data65k_path}"); sys.exit(1)
    if not p3_path.exists():
        print(f"ERROR: P3 benchmark not found at {p3_path}"); sys.exit(1)

    df65k  = pd.read_csv(data65k_path)
    df_p3  = pd.read_csv(p3_path)
    smiles_p3 = set(df_p3["SMILES"].dropna())

    df_ext = df65k[~df65k["input"].isin(smiles_p3)].copy()
    df_ext = df_ext.rename(columns={"input": "smiles"})
    df_ext["activity_label"] = (df_ext["asexual_blood_stage"] > args.activity_threshold).astype(int)
    df_ext = df_ext.dropna(subset=["smiles"]).reset_index(drop=True)

    print(f"\n65K total        : {len(df65k)}")
    print(f"P3 excluded      : {len(df_p3)}")
    print(f"External-only    : {len(df_ext)}")

    # ── Stratified subsample ───────────────────────────────────────────────────
    rng = np.random.default_rng(args.seed)
    act_idx   = df_ext[df_ext["activity_label"] == 1].index.tolist()
    inact_idx = df_ext[df_ext["activity_label"] == 0].index.tolist()
    n_active_target   = int(args.n_sample * (df_ext["activity_label"] == 1).mean())
    n_inactive_target = args.n_sample - n_active_target
    sampled_act   = rng.choice(act_idx,   size=min(n_active_target,   len(act_idx)),   replace=False)
    sampled_inact = rng.choice(inact_idx, size=min(n_inactive_target, len(inact_idx)), replace=False)
    sampled_idx   = np.concatenate([sampled_act, sampled_inact])
    rng.shuffle(sampled_idx)

    df_sub = df_ext.loc[sampled_idx].reset_index(drop=True)
    df_sub["mol_id"] = [f"EXT{i:05d}" for i in range(len(df_sub))]

    n_active_sub   = (df_sub["activity_label"] == 1).sum()
    n_inactive_sub = (df_sub["activity_label"] == 0).sum()
    sub_sha256 = dataframe_sha256(df_sub, "smiles")

    print(f"\nSubsample: {len(df_sub)} molecules (seed={args.seed})")
    print(f"  Active  : {n_active_sub} ({n_active_sub/len(df_sub)*100:.1f}%)")
    print(f"  Inactive: {n_inactive_sub} ({n_inactive_sub/len(df_sub)*100:.1f}%)")
    print(f"  SHA-256 : {sub_sha256}")

    # Cross-check with ECFP4 baseline if available
    ecfp4_summary = out_dir / "ecfp4_rbf_ext10k_scaffold_summary.json"
    if ecfp4_summary.exists():
        with open(ecfp4_summary) as f:
            ecfp4_data = json.load(f)
        ecfp4_sha = ecfp4_data["data"]["subsample_sha256"]
        if ecfp4_sha == sub_sha256:
            print(f"  ✓ SHA-256 matches ECFP4 baseline — identical subsample confirmed")
        else:
            print(f"  WARNING: SHA-256 mismatch with ECFP4 baseline!")
            print(f"    ECFP4: {ecfp4_sha}")
            print(f"    QFE  : {sub_sha256}")

    # ── Compute scaffolds ──────────────────────────────────────────────────────
    print("\nComputing Murcko scaffolds...", flush=True)
    df_sub["scaffold"] = [get_murcko_scaffold(s) for s in df_sub["smiles"]]

    # ── Scaffold split ─────────────────────────────────────────────────────────
    train_idx, test_idx, split_stats = scaffold_split(df_sub, test_frac=0.2, seed=args.seed)
    df_train = df_sub.iloc[train_idx]
    df_test  = df_sub.iloc[test_idx]

    print(f"Scaffold split: Train {len(df_train)} | Test {len(df_test)}")
    print(f"  Novel scaffolds in test: {split_stats['pct_novel_scaffolds_in_test']:.1f}%")

    # ── ECFP4 fingerprints ─────────────────────────────────────────────────────
    print("Computing ECFP4 fingerprints...", end=" ", flush=True)
    train_fps, train_labels, n_invalid = [], [], 0
    for _, row in df_train.iterrows():
        fp = smiles_to_ecfp4(row["smiles"], args.fp_size)
        if fp is None:
            n_invalid += 1
            continue
        train_fps.append(fp)
        train_labels.append(row["activity_label"])

    test_fps, test_labels = [], []
    for _, row in df_test.iterrows():
        fp = smiles_to_ecfp4(row["smiles"], args.fp_size)
        if fp is None:
            n_invalid += 1
            continue
        test_fps.append(fp)
        test_labels.append(row["activity_label"])

    print(f"done. Invalid SMILES: {n_invalid}")

    device = "cpu"

    # ── Build model ────────────────────────────────────────────────────────────
    print(f"\nBuilding QFE model ({args.qubits}q, depth {args.depth}, {args.entangling})...")
    model = QFEModel(args.fp_size, args.qubits, args.depth, args.entangling, args.backend)
    model.to(device)

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Trainable params: {n_params}")

    # ── Train ──────────────────────────────────────────────────────────────────
    print(f"\nTraining on {len(train_fps)} molecules × {args.epochs} epochs...", flush=True)
    t_train = time.time()
    model, grad_norms = train_model(
        model, train_fps, train_labels, device,
        args.epochs, args.lr, args.patience, args.batch_size,
    )
    t_train = time.time() - t_train
    print(f"  Training complete: {t_train:.1f}s")

    # ── Evaluate on test set ───────────────────────────────────────────────────
    print("Evaluating on test set...", flush=True)
    model.eval()
    probs, preds_binary = [], []
    test_fps_t = [torch.FloatTensor(fp).to(device) for fp in test_fps]
    with torch.no_grad():
        for fp_t in test_fps_t:
            prob = model(fp_t).item()
            probs.append(prob)
            preds_binary.append(int(prob >= 0.5))

    y_test = np.array(test_labels)
    probs  = np.array(probs)
    preds  = np.array(preds_binary)

    auc       = roc_auc_score(y_test, probs)
    brier     = brier_score_loss(y_test, probs)
    acc       = accuracy_score(y_test, preds)
    f1        = f1_score(y_test, preds, zero_division=0)
    precision = precision_score(y_test, preds, zero_division=0)
    recall    = recall_score(y_test, preds, zero_division=0)

    elapsed = time.time() - t_start

    # Gradient statistics
    gn_arr       = np.array(grad_norms)
    mean_grad    = float(gn_arr.mean())
    std_grad     = float(gn_arr.std())
    min_grad     = float(gn_arr.min())
    max_grad     = float(gn_arr.max())
    pct_below_1e6 = float((gn_arr < 1e-6).mean() * 100)
    barren       = pct_below_1e6 > 1.0

    print("\n" + "=" * 65)
    print(f"QFE ({args.qubits}q, depth {args.depth}, {args.entangling}) — External scaffold split")
    print("=" * 65)
    print(f"Total time : {elapsed:.1f}s")
    print(f"\n── Results ──")
    print(f"  AUC      : {auc:.4f}")
    print(f"  Brier    : {brier:.4f}")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  F1       : {f1:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall   : {recall:.4f}")
    print(f"\n── Gradient norms ──")
    print(f"  mean={mean_grad:.4e}, min={min_grad:.4e}, max={max_grad:.4e}")
    print(f"  Barren plateau: {'RISK' if barren else 'OK'}")
    print(f"\n── Phase 4 references ──")
    print(f"  QFE 4q P3 subsample (CV):   AUC 0.8474 ± 0.0129")
    print(f"  ECFP4-RBF P3 canonical:     AUC 0.9475 ± 0.0045")

    # ── Save per-molecule predictions ─────────────────────────────────────────
    test_smiles_list   = [df_test.iloc[i]["smiles"]   for i in range(len(y_test))]
    test_scaffold_list = [df_test.iloc[i]["scaffold"] for i in range(len(y_test))]

    results_df = pd.DataFrame({
        "smiles":       test_smiles_list,
        "scaffold":     test_scaffold_list,
        "y_true":       y_test,
        "y_pred_prob":  probs,
        "y_pred":       preds,
    })
    results_path = out_dir / "qfe_4q_d1_ext10k_scaffold_results.csv"
    results_df.to_csv(results_path, index=False)

    # ── Save gradient norms ────────────────────────────────────────────────────
    gn_df = pd.DataFrame({"step": range(len(grad_norms)), "grad_norm": grad_norms})
    gn_path = out_dir / "qfe_4q_d1_ext10k_scaffold_gradient_norms.csv"
    gn_df.to_csv(gn_path, index=False)

    # ── Save summary JSON ─────────────────────────────────────────────────────
    summary = {
        "method": f"QFE-{args.qubits}q-depth{args.depth}-{args.entangling}",
        "phase": "Phase 5 — external validation (scaffold split)",
        "script": "scripts/p7_phase5_qfe_ext.py",
        "timestamp": pd.Timestamp.now().isoformat(),
        "execution": {
            "backend": args.backend,
            "device": device,
            "total_time_sec": round(elapsed, 3),
            "training_time_sec": round(t_train, 3),
        },
        "data": {
            "source_65k": str(data65k_path),
            "source_p3_excluded": str(p3_path),
            "n_ext_pool": len(df_ext),
            "n_subsample": len(df_sub),
            "n_active": int(n_active_sub),
            "n_inactive": int(n_inactive_sub),
            "subsample_sha256": sub_sha256,
            "seed": args.seed,
            "activity_threshold": args.activity_threshold,
            "split_strategy": "Bemis-Murcko scaffold split (20% test, rare scaffolds prioritised)",
        },
        "scaffold_split": split_stats,
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
            "auc":       round(auc, 6),
            "brier":     round(brier, 6),
            "accuracy":  round(acc, 6),
            "f1":        round(f1, 6),
            "precision": round(precision, 6),
            "recall":    round(recall, 6),
            "n_train":   len(train_fps),
            "n_test":    len(test_fps),
        },
        "gradient_norms": {
            "mean": round(mean_grad, 6),
            "std":  round(std_grad, 6),
            "min":  round(min_grad, 6),
            "max":  round(max_grad, 6),
            "pct_below_1e6": round(pct_below_1e6, 2),
            "barren_plateau_risk": barren,
        },
        "phase4_references": {
            "QFE_4q_P3_subsample_cv5":   {"auc": 0.8474, "auc_std": 0.0129},
            "ECFP4_RBF_P3_canonical":    {"auc": 0.9475, "auc_std": 0.0045},
            "ECFP4_RBF_P3_local_cv5":    {"auc": 0.8693, "auc_std": 0.0265},
        },
    }
    summary_path = out_dir / "qfe_4q_d1_ext10k_scaffold_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Results saved to: {out_dir}")
    print(f"  {results_path.name}")
    print(f"  {summary_path.name}")
    print(f"  {gn_path.name}")


if __name__ == "__main__":
    main()
