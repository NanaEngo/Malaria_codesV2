#!/usr/bin/env python3
"""
P7 Phase 3A — Quantum Feature Extractor (QFE) Hybrid Model.

Architecture:
    SMILES → ECFP4 (2048-bit)
           → Classical encoder: Linear(2048 → n_qubits)
           → Quantum circuit (n_qubits, RY encoding + variational RZ/RZZ)
           → Measurement: Pauli-Z expectations (n_qubits-dim)
           → Classical decoder: MLP(n_qubits → 32 → 1, Sigmoid)

Quantum circuit (per sample):
    [Encoding]    RY(x_i) on qubit i   (data embedding)
    [Variational] RX(θ_i0), RZ(θ_i1)  (trainable single-qubit)
    [Entangling]  RZZ(θ_ij) on (i, i+1) (trainable two-qubit)
    [Measurement] ⟨Z_i⟩ for each qubit

Gradient norm is logged each epoch to detect barren plateaus.

Usage:
    python scripts/p7_arch1_quantum_feature_extractor.py \\
        --data data/p1_set_a/p1_set_a_17_candidates.csv \\
        --output results/phase1_proof_of_concept/ \\
        --qubits 4 --depth 1 --entangling rzz --cv loo \\
        --backend default.qubit
"""
import argparse
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
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                              recall_score, roc_auc_score)
from sklearn.model_selection import LeaveOneOut

# ── ECFP4 helper ─────────────────────────────────────────────────────────────
def smiles_to_ecfp4(smiles: str, n_bits: int = 2048) -> np.ndarray:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return np.zeros(n_bits, dtype=np.float32)
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    fp  = gen.GetFingerprint(mol)
    arr = np.zeros(n_bits, dtype=np.float32)
    for idx in fp.GetOnBits():
        arr[idx] = 1.0
    return arr


# ── Quantum circuit ───────────────────────────────────────────────────────────
def build_qfe_circuit(n_qubits: int, n_layers: int, entangling: str, backend: str):
    """Returns a PennyLane QNode that encodes `inputs` and applies variational layers."""
    dev = qml.device(backend, wires=n_qubits)

    @qml.qnode(dev, interface='torch', diff_method='backprop')
    def circuit(inputs, theta_sq, theta_ent):
        """
        inputs   : (n_qubits,)  — compressed molecule features
        theta_sq : (n_layers, n_qubits, 2)  — single-qubit params [RX, RZ]
        theta_ent: (n_layers, n_qubits-1)   — two-qubit params [RZZ or CNOT]
        """
        for layer in range(n_layers):
            # ── Encoding ──────────────────────────────────────────────
            for q in range(n_qubits):
                qml.RY(inputs[q], wires=q)

            # ── Single-qubit variational ──────────────────────────────
            for q in range(n_qubits):
                qml.RX(theta_sq[layer, q, 0], wires=q)
                qml.RZ(theta_sq[layer, q, 1], wires=q)

            # ── Entangling ────────────────────────────────────────────
            for q in range(n_qubits - 1):
                if entangling == 'rzz':
                    qml.IsingZZ(theta_ent[layer, q], wires=[q, q + 1])
                elif entangling == 'cnot':
                    qml.CNOT(wires=[q, q + 1])
                elif entangling == 'cz':
                    qml.CZ(wires=[q, q + 1])

        return [qml.expval(qml.PauliZ(q)) for q in range(n_qubits)]

    return circuit


# ── Hybrid model ──────────────────────────────────────────────────────────────
class QFEModel(nn.Module):
    """ECFP4 → Linear encoder → Quantum circuit → MLP decoder"""

    def __init__(self, fp_dim: int, n_qubits: int, n_layers: int,
                 entangling: str, backend: str):
        super().__init__()
        self.n_qubits  = n_qubits
        self.n_layers  = n_layers

        # Classical encoder: compress fingerprint to n_qubits dims in [-π, π]
        self.encoder = nn.Sequential(
            nn.Linear(fp_dim, 128),
            nn.ReLU(),
            nn.Linear(128, n_qubits),
            nn.Tanh(),               # output in (-1, 1)
        )

        # Quantum circuit
        self.circuit = build_qfe_circuit(n_qubits, n_layers, entangling, backend)

        # Variational parameters (trainable)
        self.theta_sq  = nn.Parameter(
            torch.randn(n_layers, n_qubits, 2) * 0.01
        )
        self.theta_ent = nn.Parameter(
            torch.randn(n_layers, max(n_qubits - 1, 1)) * 0.01
        )

        # Classical decoder
        self.decoder = nn.Sequential(
            nn.Linear(n_qubits, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, fp: torch.Tensor) -> torch.Tensor:
        # fp: (batch, fp_dim) or (fp_dim,)
        if fp.dim() == 1:
            fp = fp.unsqueeze(0)

        preds = []
        for i in range(fp.shape[0]):
            compressed = self.encoder(fp[i])          # (n_qubits,)
            # Scale to (-π, π)
            inputs = compressed * np.pi
            # Run quantum circuit → list of n_qubits expectation values
            q_out  = self.circuit(inputs, self.theta_sq, self.theta_ent)
            q_feat = torch.stack(q_out).float()        # (n_qubits,)  cast float64→float32
            out    = self.decoder(q_feat.unsqueeze(0)) # (1, 1)
            preds.append(out.squeeze())

        return torch.stack(preds)                      # (batch,)


# ── Training utilities ────────────────────────────────────────────────────────
def train_fold(model, train_fps, train_labels, val_fps, val_labels,
               device, epochs=100, lr=5e-3, patience=20):
    crit    = nn.BCELoss()
    optim_  = optim.Adam(model.parameters(), lr=lr)
    sched   = optim.lr_scheduler.StepLR(optim_, step_size=30, gamma=0.5)

    best_loss   = float('inf')
    patience_   = 0
    best_state  = None
    grad_norms  = []

    train_fps_t  = [torch.FloatTensor(fp).to(device) for fp in train_fps]
    train_labs_t = torch.FloatTensor(train_labels).to(device)
    val_fps_t    = [torch.FloatTensor(fp).to(device) for fp in val_fps]

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        optim_.zero_grad()

        # Process one molecule at a time (LOO: train set = n-1)
        for fp_t, y in zip(train_fps_t, train_labs_t):
            pred  = model(fp_t)
            loss_ = crit(pred, y.unsqueeze(0))
            loss_.backward()
            total_loss += loss_.item()

        # Gradient norm (barren plateau check)
        gnorm = sum(
            p.grad.norm().item() ** 2
            for p in model.parameters()
            if p.grad is not None
        ) ** 0.5
        grad_norms.append(gnorm)

        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optim_.step()
        sched.step()

        # Validation loss
        model.eval()
        with torch.no_grad():
            val_loss = 0.0
            for fp_t, y in zip(val_fps_t, val_labels):
                pred      = model(fp_t)
                val_loss += crit(pred, torch.FloatTensor([y]).to(device)).item()

        if val_loss < best_loss:
            best_loss  = val_loss
            patience_  = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_ += 1
            if patience_ >= patience:
                break

    if best_state:
        model.load_state_dict(best_state)
    return model, grad_norms


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="P7 QFE Hybrid Model")
    parser.add_argument('--data',       type=str, required=True)
    parser.add_argument('--output',     type=str, required=True)
    parser.add_argument('--qubits',     type=int, default=4)
    parser.add_argument('--depth',      type=int, default=1)
    parser.add_argument('--entangling', type=str, default='rzz',
                        choices=['rzz', 'cnot', 'cz', 'none'])
    parser.add_argument('--cv',         type=str, default='loo', choices=['loo'])
    parser.add_argument('--backend',    type=str, default='default.qubit')
    parser.add_argument('--fp-size',    type=int, default=2048)
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    device  = 'cpu'

    print("=" * 60)
    print("P7 Phase 3A — QFE Hybrid Model")
    print("=" * 60)
    print(f"Qubits   : {args.qubits}")
    print(f"Depth    : {args.depth}")
    print(f"Entangle : {args.entangling}")
    print(f"Backend  : {args.backend}")

    # ── Load data ─────────────────────────────────────────────────────────
    df = pd.read_csv(args.data)
    print(f"\nLoaded {len(df)} molecules")

    smiles_list = df['SMILES'].tolist()
    labels      = df['activity_label'].tolist()
    print(f"Active: {sum(labels)}, Inactive: {len(labels) - sum(labels)}")

    # ── Compute fingerprints ──────────────────────────────────────────────
    fps = [smiles_to_ecfp4(smi, args.fp_size) for smi in smiles_list]

    # ── LOO-CV ────────────────────────────────────────────────────────────
    loo         = LeaveOneOut()
    results     = []
    all_gnorms  = []
    t0          = time.time()

    for fold, (train_idx, val_idx) in enumerate(loo.split(fps)):
        print(f"\n  Fold {fold + 1}/{len(fps)}...", end='', flush=True)

        train_fps = [fps[i] for i in train_idx]
        train_y   = [labels[i] for i in train_idx]
        val_fps   = [fps[i] for i in val_idx]
        val_y     = [labels[i] for i in val_idx]

        model = QFEModel(
            fp_dim      = args.fp_size,
            n_qubits    = args.qubits,
            n_layers    = args.depth,
            entangling  = args.entangling,
            backend     = args.backend,
        ).to(device)

        model, gnorms = train_fold(
            model, train_fps, train_y, val_fps, val_y, device
        )
        all_gnorms.append(gnorms)

        # Predict
        model.eval()
        with torch.no_grad():
            fp_t = torch.FloatTensor(val_fps[0]).to(device)
            pred = model(fp_t).item()

        results.append({
            'fold':   fold,
            'y_true': int(val_y[0]),
            'y_pred': float(pred),
        })
        print(f" pred={pred:.3f}, true={val_y[0]}", flush=True)

    elapsed = time.time() - t0

    # ── Metrics ───────────────────────────────────────────────────────────
    y_true = np.array([r['y_true'] for r in results])
    y_pred = np.array([r['y_pred'] for r in results])
    y_bin  = (y_pred > 0.5).astype(int)

    metrics = {
        'auc':       float(roc_auc_score(y_true, y_pred)) if len(np.unique(y_true)) > 1 else float('nan'),
        'accuracy':  float(accuracy_score(y_true, y_bin)),
        'f1':        float(f1_score(y_true, y_bin, zero_division=0)),
        'precision': float(precision_score(y_true, y_bin, zero_division=0)),
        'recall':    float(recall_score(y_true, y_bin, zero_division=0)),
    }

    # ── Gradient norm analysis ────────────────────────────────────────────
    flat_gnorms = [g for fold in all_gnorms for g in fold]
    gnorm_stats = {
        'mean':     float(np.mean(flat_gnorms)),
        'std':      float(np.std(flat_gnorms)),
        'min':      float(np.min(flat_gnorms)),
        'max':      float(np.max(flat_gnorms)),
        'pct_below_1e6': float((np.array(flat_gnorms) < 1e-6).mean()),
        'barren_plateau_risk': bool(np.mean(flat_gnorms) < 1e-6),
    }

    # ── Save ──────────────────────────────────────────────────────────────
    result_tag = f"qfe_{args.qubits}q_d{args.depth}"

    pd.DataFrame(results).to_csv(
        out_dir / f"{result_tag}_loo_results.csv", index=False
    )

    # Per-fold gradient norms
    gnorm_rows = []
    for fold_idx, gnorms in enumerate(all_gnorms):
        for epoch_idx, gn in enumerate(gnorms):
            gnorm_rows.append({'fold': fold_idx, 'epoch': epoch_idx, 'grad_norm': gn})
    pd.DataFrame(gnorm_rows).to_csv(
        out_dir / f"{result_tag}_gradient_norms.csv", index=False
    )

    summary = {
        'method':            f'QFE-{args.qubits}q-depth{args.depth}-{args.entangling}',
        'n_qubits':          args.qubits,
        'n_layers':          args.depth,
        'entangling':        args.entangling,
        'backend':           args.backend,
        'cv_strategy':       'loo',
        'n_molecules':       len(fps),
        'n_active':          sum(labels),
        'fp_size':           args.fp_size,
        'training_time_sec': elapsed,
        'metrics':           metrics,
        'gradient_norms':    gnorm_stats,
    }
    (out_dir / f"{result_tag}_loo_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    # ── Report ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"QFE ({args.qubits}-qubit, depth {args.depth}, {args.entangling}) Summary")
    print(f"{'='*60}")
    print(f"Molecules : {len(fps)}")
    print(f"Time      : {elapsed:.1f}s")
    print(f"\nMetrics:")
    for k, v in metrics.items():
        print(f"  {k.upper():12s}: {v:.4f}")
    print(f"\nGradient norms:")
    print(f"  mean={gnorm_stats['mean']:.4e}, "
          f"min={gnorm_stats['min']:.4e}, "
          f"max={gnorm_stats['max']:.4e}")
    bp = "RISK" if gnorm_stats['barren_plateau_risk'] else "OK"
    print(f"  Barren plateau: {bp}")
    print(f"{'='*60}")
    print(f"\n✓ Saved to: {out_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\nERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
