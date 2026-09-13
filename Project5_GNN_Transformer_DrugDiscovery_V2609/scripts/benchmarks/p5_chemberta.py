#!/usr/bin/env python3
"""
P5 — ChemBERTa fine-tune (arm for Q1/Q4). Mirrors the P5 benchmark protocol.

Usage:
    python scripts/p5_chemberta.py --dry-run --device cpu
    python scripts/p5_chemberta.py --device cuda
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, balanced_accuracy_score

P5_ROOT = Path(__file__).resolve().parent.parent
PANEL = P5_ROOT / "results" / "p5_canonical_panel.csv"

MODEL_NAME = "seyonec/ChemBERTa-zinc-base-v1"  # base; can try ChemBERTa-3 later
MAX_LENGTH = 128
BATCH_SIZE = 32
EPOCHS = 10
LR = 2e-5
WEIGHT_DECAY = 0.01
PATIENCE = 3
SEEDS = [0, 1, 2, 3, 4]
N_FOLDS = 5
DEVICE = "auto"


class SMILESDataset(Dataset):
    def __init__(self, smiles: list[str], labels: np.ndarray, tokenizer, max_length: int):
        self.smiles = smiles
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.smiles)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.smiles[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


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


def load_splits(split_type: str = "random") -> list:
    split_files = []
    for seed in SEEDS:
        f = P5_ROOT / "results" / f"p5_splits_{split_type}_5fold_seed{seed}.npy"
        split_files.append(np.load(f, allow_pickle=True))
    folds = []
    for f_idx in range(5):
        folds.append([sf[f_idx] for sf in split_files])
    return folds


class ChemBERTaTrainer:
    def __init__(self, split_type: str = "random", dry_run: bool = False, device: str = "auto",
                 curves_only: bool = False, tag: str = "", masks_only: bool = False):
        self.split_type = split_type
        self.dry_run = dry_run
        self.device = get_device(device)
        self.curves_only = curves_only
        self.tag = tag
        self.masks_only = masks_only
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME,
            num_labels=2,
        ).to(self.device)
        # Snapshot pretrained weights once; restore before each fold so folds are
        # independent (motorformer is otherwise leak across folds). ponytail: per-fold reset.
        self.pretrained_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
        self.panel = pd.read_csv(PANEL)
        self.smiles = self.panel["smiles"].tolist()
        self.y = self.panel["activity"].values.astype(np.int64)
        self.folds = load_splits(split_type) if not masks_only else []
        self.completed: set[tuple] = set()
        self.ckpt_path = P5_ROOT / "results" / f"p5_chemberta_{split_type}_ckpt{tag}.json"
        if not masks_only and self.ckpt_path.exists():
            with open(self.ckpt_path) as f:
                ckpt = json.load(f)
                self.completed = set(tuple(r) for r in ckpt.get("completed", []))
            print(f"Loaded ChemBERTa checkpoint: {len(self.completed)} completed")

    def _make_loader(self, indices: np.ndarray, shuffle: bool = False) -> DataLoader:
        ds = SMILESDataset([self.smiles[i] for i in indices],
                           self.y[indices], self.tokenizer, MAX_LENGTH)
        return DataLoader(ds, batch_size=BATCH_SIZE, shuffle=shuffle)

    def _train_core(self, tr_idx, val_idx, te_idx, seed, set_index=None) -> tuple:
        """Shared train/validate/test loop used by both canonical fold indices and
        arbitrary index masks (e.g. Butina splits). Returns
        (pred_scores, te_auc, te_ap, te_f1, te_bacc, curve)."""
        set_seed(seed)
        if set_index is not None:
            self.model = set_index(tr_idx, te_idx)
            self.model.load_state_dict(self.pretrained_state)
        else:
            self.model.load_state_dict(self.pretrained_state)  # independent folds (no cross-fold leak)
        tr_loader = self._make_loader(tr_idx, shuffle=True)
        val_loader = self._make_loader(val_idx)
        te_loader = self._make_loader(te_idx)

        opt = torch.optim.AdamW(self.model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
        criterion = nn.CrossEntropyLoss()

        best_val = -1.0
        best_state = None
        wait = 0
        curve = []

        for epoch in range(EPOCHS):
            self.model.train()
            for batch in tr_loader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                opt.zero_grad()
                logits = self.model(**batch).logits
                loss = criterion(logits, batch["labels"])
                loss.backward()
                opt.step()

            # validation
            self.model.eval()
            val_preds, val_true = [], []
            with torch.no_grad():
                for batch in val_loader:
                    batch = {k: v.to(self.device) for k, v in batch.items()}
                    logits = self.model(**batch).logits
                    val_preds.append(torch.softmax(logits, dim=1)[:, 1].cpu().numpy())
                    val_true.append(batch["labels"].cpu().numpy())
            val_auc = roc_auc_score(np.concatenate(val_true), np.concatenate(val_preds))
            curve.append(float(val_auc))

            if val_auc > best_val:
                best_val = val_auc
                best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                wait = 0
            else:
                wait += 1
                if wait >= PATIENCE:
                    break

        self.model.load_state_dict(best_state)

        # test
        self.model.eval()
        te_preds, te_true = [], []
        with torch.no_grad():
            for batch in te_loader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                logits = self.model(**batch).logits
                te_preds.append(torch.softmax(logits, dim=1)[:, 1].cpu().numpy())
                te_true.append(batch["labels"].cpu().numpy())
        p = np.concatenate(te_preds)
        t = np.concatenate(te_true)
        te_auc = roc_auc_score(t, p)
        te_ap = average_precision_score(t, p)
        te_bin = (p >= 0.5).astype(int)
        te_f1 = f1_score(t, te_bin)
        te_bacc = balanced_accuracy_score(t, te_bin)
        return p, float(te_auc), float(te_ap), float(te_f1), float(te_bacc), curve

    def train_fold(self, fold_idx: int, seed: int) -> float:
        set_seed(seed)
        self.model.load_state_dict(self.pretrained_state)  # independent folds (no cross-fold leak)
        fold = self.folds[fold_idx][SEEDS.index(seed)]
        tr_idx, val_idx, te_idx = fold["train"], fold["val"], fold["test"]
        _, te_auc, te_ap, te_f1, te_bacc, curve = self._train_core(
            tr_idx, val_idx, te_idx, seed)
        return te_auc, te_ap, te_f1, te_bacc, curve

    def train_masks(self, train_idx, test_idx, seed: int, val_frac: float = 0.1) -> tuple:
        """Train on an arbitrary index mask (e.g. Butina splits) without relying on
        the canonical fold/seed splits. A validation fold is carved by stratified
        holdout from train_idx so early-stopping does not touch test_idx.
        Returns (pred_scores, auc, ap, f1, bacc)."""
        train_idx = np.asarray(train_idx, dtype=np.int64)
        test_idx = np.asarray(test_idx, dtype=np.int64)
        y_tr = self.y[train_idx]
        # stratified holdout: interleave positives/negatives every 10th row
        rng = np.random.default_rng(seed)
        pos = train_idx[y_tr == 1]
        neg = train_idx[y_tr == 0]
        def _holdout(g):
            g = rng.permutation(g)
            n = max(1, int(np.ceil(len(g) * val_frac)))
            return np.sort(g[:n]), np.sort(g[n:])
        val_pos, tr_pos = _holdout(pos)
        val_neg, tr_neg = _holdout(neg)
        val_idx = np.concatenate([val_pos, val_neg])
        tr_idx2 = np.concatenate([tr_pos, tr_neg])
        p, auc, ap, f1, bacc, _ = self._train_core(tr_idx2, val_idx, test_idx, seed)
        return p, auc, ap, f1, bacc

    def run(self) -> list[dict]:
        results = []
        for f_idx in range(N_FOLDS):
            for s_idx, seed in enumerate(SEEDS):
                key = (f_idx, seed)
                if not self.curves_only and key in self.completed:
                    print(f"  Skipping completed fold {f_idx} seed {seed}")
                    continue
                print(f"Training ChemBERTa fold {f_idx} seed {seed} on {self.device}...")
                if self.dry_run:
                    te_auc, te_ap, te_f1, te_bacc, curve = 0.5, 0.5, 0.5, 0.5, []
                else:
                    te_auc, te_ap, te_f1, te_bacc, curve = self.train_fold(f_idx, seed)
                results.append({
                    "model": "ChemBERTa", "fold": f_idx, "seed": seed,
                    "test_auc": te_auc, "test_ap": te_ap, "test_f1": te_f1,
                    "test_bacc": te_bacc, "split": self.split_type,
                    "curve": curve,
                })
                self.completed.add(key)
                if not self.dry_run and not self.curves_only:
                    self._save_ckpt(results)
        if self.curves_only:
            self._save_curves(results)
        return results

    def _save_curves(self, results: list):
        p = P5_ROOT / "results" / f"p5_chemberta_{self.split_type}_curves.json"
        curves = [{"fold": r["fold"], "seed": r["seed"], "curve": r["curve"]} for r in results]
        json.dump({"model": "ChemBERTa", "split": self.split_type, "curves": curves}, open(p, "w"), indent=2)
        print(f"Curves written to {p} (canonical ckpt/CSV untouched)")

    def _save_ckpt(self, results: list):
        with open(self.ckpt_path, "w") as f:
            json.dump({"completed": list(self.completed), "results": results}, f, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["random", "scaffold"], default="random")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    ap.add_argument("--curves-only", action="store_true")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    trainer = ChemBERTaTrainer(split_type=args.split, dry_run=args.dry_run, device=args.device,
                               curves_only=args.curves_only, tag=args.tag)
    results = trainer.run()

    if not args.dry_run and not args.curves_only:
        out_csv = P5_ROOT / "results" / f"p5_chemberta_{args.split}_results{args.tag}.csv"
        pd.DataFrame(results).to_csv(out_csv, index=False)
        print(f"Results written to {out_csv}")

    aucs = [r["test_auc"] for r in results]
    print(f"\nChemBERTa ({args.split}) mean AUC = {np.mean(aucs):.4f} ± {np.std(aucs):.4f}")


# Module-level lru cache so repeated fold calls (e.g. Butina arms) reuse one
# tokenizer + pretrained model instead of re-downloading per call.
_trainer_cache: dict = {}


def run_chemberta_fold(train_idx, test_idx, y, device):
    """Train ChemBERTa on arbitrary index masks (Butina splits) and return
    (pred_scores, auc, ap, balanced_acc).

    Mirrors the canonical protocol (pretrained-weight reset per fold, AdamW
    lr=2e-5, patience 3, max 10 epochs) with a stratified holdout validation
    carved from train_idx. Reuses a cached trainer (tokenizer + model) so a
    batch of calls does not re-download weights for every fold.
    """
    global _trainer_cache
    # Butina passes a torch.device object and a y vector. get_device() matches on
    # string names, so normalize: accept torch.device / str. The trainer re-loads
    # panel/smiles/y itself (shared source of truth), so the caller's y is
    # intentionally ignored (keeps one canonical label source).
    dev_name = device.type if isinstance(device, torch.device) else str(device)
    key = dev_name  # cache per device so a CPU/GPU mix cannot mismatch
    if key not in _trainer_cache:
        # masks_only=True: train_masks() uses caller-supplied index masks and
        # does not need canonical split .npy files or a ckpt (Butina path).
        _trainer_cache[key] = ChemBERTaTrainer(
            split_type="random", device=dev_name, masks_only=True)
    trainer = _trainer_cache[key]
    # train_masks returns (p, auc, ap, f1, bacc); Butina's interface is a strict
    # 4-tuple (p, auc, ap, bal). Keep bal = bacc to match the other arms.
    p, auc, ap, f1, bacc = trainer.train_masks(
        np.asarray(train_idx, dtype=np.int64),
        np.asarray(test_idx, dtype=np.int64),
        seed=int(os.environ.get("BUTINA_SEED", "0")),
    )
    return p, auc, ap, bacc


if __name__ == "__main__":
    main()