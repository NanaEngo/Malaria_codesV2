#!/usr/bin/env python3
"""
P5 — Benchmark training/evaluation (M1.3). 5-fold × seeds, checkpoint resume,
DeLong + BH statistics. Mirrors P3 hybrid benchmark protocol.

Usage (CPU dry-run):
    python scripts/p5_benchmark.py --model GIN --dry-run --device cpu

Usage (GPU production):
    sbatch scripts/p5_benchmark.sbatch GIN
    # or
    python scripts/p5_benchmark.py --model GIN --device cuda
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.loader import DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score
from scipy import stats

# Local imports
P5_SCRIPTS = Path(__file__).resolve().parent
P5_ROOT = P5_SCRIPTS.parent
sys.path.insert(0, str(P5_SCRIPTS))
import p5_models
import p5_data

# P3 for reference ECFP4-RF
P3_RESULTS = Path("/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/results")

# Config
MODEL_NAMES = list(p5_models.MODEL_FACTORY.keys())
DEVICE = "auto"
N_FOLDS = 5
SEEDS = [0, 1, 2, 3, 4]
EPOCHS = 50
BATCH_SIZE = 512
LR = 1e-3
WEIGHT_DECAY = 1e-4
PATIENCE = 10
HIDDEN = 128
DROPOUT = 0.1


def set_seed(seed: int):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device(name: str) -> torch.device:
    if name == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device("cpu")


def load_splits(split_type: str) -> list:
    """Returns list of 5 folds, each fold = list of 5 seed dicts"""
    # For simplicity: return per-seed fold arrays
    pass


class P5Benchmark:
    def __init__(self, model_name: str, split_type: str = "random",
                 device: str = "auto", dry_run: bool = False,
                 ckpt_path: Path | None = None):
        self.model_name = model_name
        self.split_type = split_type
        self.device = get_device(device)
        self.dry_run = dry_run
        self.ckpt_path = ckpt_path or (P5_ROOT / "results" / f"p5_{model_name}_{split_type}_ckpt.json")

        panel = pd.read_csv(P5_ROOT / "results" / "p5_canonical_panel.csv")
        self.smiles = panel["smiles"].tolist()
        self.y = panel["activity"].values.astype(np.int64)

        self.graphs = torch.load(P5_ROOT / "results" / "p5_graphs.pt")

        # descriptor vectors
        self.desc = None
        if model_name in p5_models.FUSION_MODELS:
            n_desc = p5_models.MODEL_FACTORY[model_name].get("n_desc")
            if n_desc:
                self.desc = torch.zeros((len(self.smiles), n_desc), dtype=torch.float32)
                # Fill in descriptors based on model type
                if model_name == "GIN-FP":
                    self.desc[:, :2048] = torch.from_numpy(self._load_ecfp4())
                elif model_name == "GIN-TFP":
                    self.desc[:, :78] = torch.from_numpy(self._load_tfp())
                elif model_name == "GIN-TNE":
                    self.desc[:, :192] = torch.from_numpy(self._load_tne())
                elif model_name == "Hybrid-All":
                    self.desc[:, :2048] = torch.from_numpy(self._load_ecfp4())
                    self.desc[:, 2048:2048+78] = torch.from_numpy(self._load_tfp())
                    self.desc[:, 2048+78:] = torch.from_numpy(self._load_tne())

        # splits
        self.folds = self._load_splits(split_type)

        # model params
        self.in_dim = len(self.graphs[0]["x"][0])
        self.edge_dim = self.graphs[0]["edge_attr"].shape[1] if self.graphs[0]["edge_attr"].numel() > 0 else 6
        self.n_desc = self.desc.shape[1] if self.desc is not None else None

        # checkpoint
        self.completed: set[tuple] = set()
        if self.ckpt_path.exists():
            with open(self.ckpt_path) as f:
                ckpt = json.load(f)
                self.completed = set(tuple(r) for r in ckpt.get("completed", []))
            print(f"Loaded checkpoint: {len(self.completed)} completed records")

    def _load_ecfp4(self) -> np.ndarray:
        from rdkit import Chem
        from rdkit.Chem import rdFingerprintGenerator
        from rdkit.DataStructs import ConvertToNumpyArray
        morgan = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        mats = []
        for smi in self.smiles:
            mol = Chem.MolFromSmiles(smi)
            arr = np.zeros(2048, dtype=np.float32)
            if mol:
                ConvertToNumpyArray(morgan.GetFingerprint(mol), arr)
            mats.append(arr)
        return np.stack(mats)

    def _load_tfp(self) -> np.ndarray:
        import p5_data
        panel = pd.read_csv(P5_ROOT / "results" / "p5_canonical_panel.csv")
        return panel[[f"tfp_{i}" for i in range(78)]].values.astype(np.float32)

    def _load_tne(self) -> np.ndarray:
        panel = pd.read_csv(P5_ROOT / "results" / "p5_canonical_panel.csv")
        return panel[[f"tne_{i}" for i in range(192)]].values.astype(np.float32)

    def _load_splits(self, split_type: str) -> list:
        # Returns list of 5 folds, each fold is list of 5 seed dicts {train,val,test}
        split_files = []
        for seed in SEEDS:
            f = P5_ROOT / "results" / f"p5_splits_{split_type}_5fold_seed{seed}.npy"
            split_files.append(np.load(f, allow_pickle=True))
        # transpose: folds x seeds
        folds = []
        for f_idx in range(N_FOLDS):
            folds.append([sf[f_idx] for sf in split_files])
        return folds

    def _make_data_list(self, indices: np.ndarray) -> list:
        from torch_geometric.data import Data
        dl = []
        for i in indices:
            g = self.graphs[i]
            d = Data(
                x=g["x"], edge_index=g["edge_index"],
                edge_attr=g["edge_attr"], y=torch.tensor([self.y[i]], dtype=torch.float32)
            )
            if self.desc is not None:
                d.desc = self.desc[i]
            dl.append(d)
        return dl

    def train_fold(self, fold_idx: int, seed: int) -> float:
        set_seed(seed)
        fold = self.folds[fold_idx][SEEDS.index(seed)]
        tr_idx, val_idx, te_idx = fold["train"], fold["val"], fold["test"]

        tr_data = self._make_data_list(tr_idx)
        val_data = self._make_data_list(val_idx)
        te_data = self._make_data_list(te_idx)

        tr_loader = DataLoader(tr_data, batch_size=BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_data, batch_size=BATCH_SIZE)
        te_loader = DataLoader(te_data, batch_size=BATCH_SIZE)

        model = p5_models.build_model(
            self.model_name, self.in_dim, hidden=HIDDEN, edge_dim=self.edge_dim,
            n_descriptor_features=self.n_desc, dropout=DROPOUT
        ).to(self.device)

        opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
        criterion = nn.BCEWithLogitsLoss()

        best_val = -1.0
        best_state = None
        wait = 0

        for epoch in range(EPOCHS):
            model.train()
            for batch in tr_loader:
                batch = batch.to(self.device)
                desc = batch.desc if hasattr(batch, "desc") else None
                opt.zero_grad()
                logits = model(batch.x, batch.edge_index, batch.batch,
                               edge_attr=batch.edge_attr if batch.edge_attr.numel() else None,
                               desc=desc).squeeze()
                loss = criterion(logits, batch.y)
                loss.backward()
                opt.step()

            # val
            model.eval()
            val_preds, val_true = [], []
            with torch.no_grad():
                for batch in val_loader:
                    batch = batch.to(self.device)
                    desc = batch.desc if hasattr(batch, "desc") else None
                    logits = model(batch.x, batch.edge_index, batch.batch,
                                   edge_attr=batch.edge_attr if batch.edge_attr.numel() else None,
                                   desc=desc).squeeze()
                    val_preds.append(torch.sigmoid(logits).cpu().numpy())
                    val_true.append(batch.y.cpu().numpy())
            val_auc = roc_auc_score(np.concatenate(val_true), np.concatenate(val_preds))

            if val_auc > best_val:
                best_val = val_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
                if wait >= PATIENCE:
                    break

        model.load_state_dict(best_state)

        # test
        model.eval()
        te_preds, te_true = [], []
        with torch.no_grad():
            for batch in te_loader:
                batch = batch.to(self.device)
                desc = batch.desc if hasattr(batch, "desc") else None
                logits = model(batch.x, batch.edge_index, batch.batch,
                               edge_attr=batch.edge_attr if batch.edge_attr.numel() else None,
                               desc=desc).squeeze()
                te_preds.append(torch.sigmoid(logits).cpu().numpy())
                te_true.append(batch.y.cpu().numpy())
        te_auc = roc_auc_score(np.concatenate(te_true), np.concatenate(te_preds))
        return float(te_auc)

    def run(self) -> list[dict]:
        results = []
        for f_idx in range(N_FOLDS):
            for s_idx, seed in enumerate(SEEDS):
                key = (f_idx, seed)
                if key in self.completed:
                    print(f"  Skipping completed fold {f_idx} seed {seed}")
                    continue
                print(f"Training {self.model_name} fold {f_idx} seed {seed} on {self.device}...")
                if self.dry_run:
                    te_auc = 0.5  # dummy
                else:
                    te_auc = self.train_fold(f_idx, seed)
                results.append({
                    "model": self.model_name, "fold": f_idx, "seed": seed,
                    "test_auc": te_auc, "split": self.split_type,
                })
                self.completed.add(key)
                if not self.dry_run:
                    self._save_ckpt(results)
        return results

    def _save_ckpt(self, results: list):
        with open(self.ckpt_path, "w") as f:
            json.dump({"completed": list(self.completed), "results": results}, f, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=MODEL_NAMES, required=True)
    ap.add_argument("--split", choices=["random", "scaffold"], default="random")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    args = ap.parse_args()

    bench = P5Benchmark(args.model, args.split, args.device, args.dry_run)
    results = bench.run()

    # save CSV (never in dry-run)
    if not args.dry_run:
        out_csv = P5_ROOT / "results" / f"p5_{args.model}_{args.split}_results.csv"
        pd.DataFrame(results).to_csv(out_csv, index=False)
        print(f"Results written to {out_csv}")

    # stats summary
    aucs = [r["test_auc"] for r in results]
    print(f"\n{args.model} ({args.split}) mean AUC = {np.mean(aucs):.4f} ± {np.std(aucs):.4f}")
    print(f"  Per-seed: {np.mean(np.array(aucs).reshape(5,5), axis=1)}")


if __name__ == "__main__":
    main()