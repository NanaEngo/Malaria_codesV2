#!/usr/bin/env python3
"""
P5 — Re-train single fold/seed for GIN-TFP and GIN-TNE to save model weights
for integrated gradients / permutation importance analysis.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.loader import DataLoader

P5_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(P5_ROOT / "scripts"))
import p5_models
import p5_data

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N_FOLDS = 5
SEEDS = [0, 1, 2, 3, 4]
BATCH_SIZE = 512
EPOCHS = 50
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


def load_splits(split_type: str) -> list:
    split_files = [
        P5_ROOT / "results" / f"p5_splits_{split_type}_5fold_seed{seed}.npy"
        for seed in SEEDS
    ]
    per_seed = [np.load(path, allow_pickle=True) for path in split_files]
    folds = []
    for fold_idx in range(N_FOLDS):
        seed_folds = []
        for seed_idx, splits in enumerate(per_seed):
            record = splits[fold_idx]
            train = np.asarray(record["train"], dtype=np.int64)
            val = np.asarray(record["val"], dtype=np.int64)
            test = np.asarray(record["test"], dtype=np.int64)
            seed_folds.append({"train": train, "val": val, "test": test})
        folds.append(seed_folds)
    return folds


def load_graphs():
    cache = P5_ROOT / "results" / "p5_graphs.pt"
    return torch.load(cache, map_location=DEVICE, weights_only=False)


def load_descriptors(desc_name: str):
    panel = pd.read_csv(P5_ROOT / "results" / "p5_canonical_panel.csv")
    if desc_name == "tfp":
        cols = [f"tfp_{i}" for i in range(78)]
    elif desc_name == "tne":
        cols = [f"tne_{i}" for i in range(192)]
    else:
        raise ValueError(f"Unknown descriptor: {desc_name}")
    return panel[cols].values.astype(np.float32)


def train_single_fold(model_name: str, desc_name: str, n_desc: int, fold_idx: int = 0, seed: int = 0):
    """Train a single fold/seed and save model weights."""
    set_seed(seed)
    
    panel = pd.read_csv(P5_ROOT / "results" / "p5_canonical_panel.csv")
    smiles = panel["smiles"].tolist()
    y = panel["activity"].values.astype(np.int64)
    
    graphs = load_graphs()
    desc = torch.tensor(load_descriptors(desc_name), dtype=torch.float32)
    folds = load_splits("scaffold")
    
    fold = folds[fold_idx][SEEDS.index(seed)]
    tr_idx, val_idx, te_idx = fold["train"], fold["val"], fold["test"]
    
    # Create data loaders
    def make_data_list(indices):
        from torch_geometric.data import Data
        dl = []
        for i in indices:
            g = graphs[i]
            d = Data(
                x=g["x"], edge_index=g["edge_index"],
                edge_attr=g["edge_attr"], y=torch.tensor([y[i]], dtype=torch.float32)
            )
            if desc is not None:
                d.desc = desc[i]
            dl.append(d)
        return dl
    
    tr_data = make_data_list(tr_idx)
    val_data = make_data_list(val_idx)
    te_data = make_data_list(te_idx)
    
    tr_loader = DataLoader(tr_data, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=BATCH_SIZE)
    te_loader = DataLoader(te_data, batch_size=BATCH_SIZE)
    
    # Build model
    in_dim = len(graphs[0]["x"][0])
    edge_dim = graphs[0]["edge_attr"].shape[1] if graphs[0]["edge_attr"].numel() > 0 else 6
    
    model = p5_models.build_model(
        model_name, in_dim=in_dim, hidden=HIDDEN, out_dim=1,
        dropout=DROPOUT, edge_dim=edge_dim, n_descriptor_features=n_desc
    ).to(DEVICE)
    
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    criterion = nn.BCEWithLogitsLoss()
    
    best_val_auc = -1
    best_state = None
    patience_counter = 0
    
    for epoch in range(EPOCHS):
        model.train()
        for batch in tr_loader:
            batch = batch.to(DEVICE)
            opt.zero_grad()
            logits = model(batch.x, batch.edge_index, batch.batch, batch.edge_attr, batch.desc).squeeze()
            loss = criterion(logits, batch.y)
            loss.backward()
            opt.step()
        
        # Validation
        model.eval()
        val_logits = []
        val_labels = []
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(DEVICE)
                logits = model(batch.x, batch.edge_index, batch.batch, batch.edge_attr, batch.desc).squeeze()
                val_logits.append(torch.sigmoid(logits).cpu().numpy())
                val_labels.append(batch.y.cpu().numpy())
        
        val_logits = np.concatenate(val_logits)
        val_labels = np.concatenate(val_labels)
        
        try:
            from sklearn.metrics import roc_auc_score
            val_auc = roc_auc_score(val_labels, val_logits)
        except ValueError:
            val_auc = 0.5
        
        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                break
    
    # Load best state
    model.load_state_dict(best_state)
    model.eval()
    
    # Test evaluation
    test_logits = []
    test_labels = []
    with torch.no_grad():
        for batch in te_loader:
            batch = batch.to(DEVICE)
            logits = model(batch.x, batch.edge_index, batch.batch, batch.edge_attr, batch.desc).squeeze()
            test_logits.append(torch.sigmoid(logits).cpu().numpy())
            test_labels.append(batch.y.cpu().numpy())
    
    test_logits = np.concatenate(test_logits)
    test_labels = np.concatenate(test_labels)
    test_auc = roc_auc_score(test_labels, test_logits)
    
    # Save model weights
    weight_path = P5_ROOT / "results" / f"p5_{model_name}_scaffold_fold{fold_idx}_seed{seed}_weights.pt"
    torch.save({
        "model_state_dict": best_state,
        "model_name": model_name,
        "fold": fold_idx,
        "seed": seed,
        "test_auc": float(test_auc),
        "val_auc": float(best_val_auc),
        "in_dim": in_dim,
        "hidden": HIDDEN,
        "n_desc": n_desc,
        "dropout": DROPOUT,
        "edge_dim": edge_dim,
    }, weight_path)
    
    print(f"Saved {model_name} weights to {weight_path} (test_auc={test_auc:.4f})")
    
    return model, test_idx, test_labels, test_logits


if __name__ == "__main__":
    # Train GIN-TFP (fold 0, seed 0)
    print("Training GIN-TFP...")
    train_single_fold("GIN-TFP", "tfp", 78, fold_idx=0, seed=0)
    
    # Train GIN-TNE (fold 0, seed 0)
    print("Training GIN-TNE...")
    train_single_fold("GIN-TNE", "tne", 192, fold_idx=0, seed=0)
    
    print("Done!")