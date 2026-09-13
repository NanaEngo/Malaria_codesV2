#!/usr/bin/env python3
"""
P5 — Integrated Gradients & Permutation Importance for Fusion Models
Computes rigorous attribution for TFP (78-dim) and TNE (192-dim) descriptors
on the trained GIN-TFP and GIN-TNE checkpoints.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch_geometric.loader import DataLoader
from sklearn.metrics import roc_auc_score
from scipy import stats

P5_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(P5_ROOT / "scripts"))
import p5_models
import p5_data

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N_FOLDS = 5
SEEDS = [0, 1, 2, 3, 4]
BATCH_SIZE = 512


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


def load_panel():
    panel = pd.read_csv(P5_ROOT / "results" / "p5_canonical_panel.csv")
    return panel


def load_graphs():
    cache = P5_ROOT / "results" / "p5_graphs.pt"
    return torch.load(cache, map_location=DEVICE, weights_only=False)


def load_descriptors_from_panel(desc_name: str):
    """Load TFP or TNE descriptors from canonical panel."""
    panel = load_panel()
    if desc_name == "tfp":
        cols = [f"tfp_{i}" for i in range(78)]
    elif desc_name == "tne":
        cols = [f"tne_{i}" for i in range(192)]
    else:
        raise ValueError(f"Unknown descriptor: {desc_name}")
    missing = [c for c in cols if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns in panel: {missing[:5]}...")
    return panel[cols].values.astype(np.float32)


def build_model_from_ckpt(model_name: str, ckpt_path: Path, n_desc: int):
    panel = load_panel()
    in_dim = 87 + 7 + 1 + 1 + 6 + 1 + 1 + 2
    model = p5_models.build_model(
        model_name, in_dim=in_dim, hidden=128, out_dim=1,
        dropout=0.1, edge_dim=6, n_descriptor_features=n_desc
    )
    ckpt = json.loads(ckpt_path.read_text())
    state_dict = {k: torch.tensor(v) for k, v in ckpt["model_state_dict"].items()}
    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()
    return model


def integrated_gradients(model, graphs, desc, test_idx, target_class=1, n_steps=50):
    """Compute integrated gradients for descriptor features."""
    model.eval()
    ig_attrs = []
    baseline = torch.zeros_like(desc[test_idx]).to(DEVICE)
    
    for i in test_idx:
        g = graphs[i].to(DEVICE)
        d = desc[i:i+1].to(DEVICE).requires_grad_(True)
        b = baseline[i:i+1].to(DEVICE)
        
        # Interpolate between baseline and input
        alphas = torch.linspace(0, 1, n_steps, device=DEVICE)
        grads = []
        
        for alpha in alphas:
            interp = b + alpha * (d - b)
            interp.requires_grad_(True)
            
            with torch.enable_grad():
                logits = model(g.x, g.edge_index, g.batch, g.edge_attr, interp)
                probs = torch.sigmoid(logits)
                target = probs[:, target_class] if probs.shape[1] > 1 else probs.squeeze()
                target.backward()
                grads.append(interp.grad.clone().detach())
                interp.grad.zero_()
        
        # Average gradients and multiply by (input - baseline)
        avg_grad = torch.stack(grads).mean(dim=0)
        attr = (d - b) * avg_grad
        ig_attrs.append(attr.squeeze().cpu().numpy())
    
    return np.stack(ig_attrs)


def permutation_importance(model, graphs, desc, test_idx, test_y, n_perms=10):
    """Compute permutation importance for each descriptor dimension."""
    model.eval()
    loader = DataLoader([graphs[i] for i in test_idx], batch_size=BATCH_SIZE, shuffle=False)
    test_d = desc[test_idx].to(DEVICE)
    test_y_t = torch.tensor(test_y[test_idx], dtype=torch.float32).to(DEVICE)
    
    # Baseline AUC
    with torch.no_grad():
        logits = model(
            torch.cat([g.x for g in loader.dataset]).to(DEVICE),
            torch.cat([g.edge_index for g in loader.dataset], dim=1).to(DEVICE),
            torch.cat([g.batch for g in loader.dataset]).to(DEVICE),
            torch.cat([g.edge_attr for g in loader.dataset], dim=0).to(DEVICE),
            test_d
        ).squeeze()
        baseline_auc = roc_auc_score(test_y, torch.sigmoid(logits).cpu().numpy())
    
    n_desc = desc.shape[1]
    importances = np.zeros((n_perms, n_desc))
    
    for perm in range(n_perms):
        for d in range(n_desc):
            d_perm = test_d.clone()
            perm_idx = torch.randperm(len(test_idx))
            d_perm[:, d] = d_perm[perm_idx, d]
            
            with torch.no_grad():
                logits = model(
                    torch.cat([g.x for g in loader.dataset]).to(DEVICE),
                    torch.cat([g.edge_index for g in loader.dataset], dim=1).to(DEVICE),
                    torch.cat([g.batch for g in loader.dataset]).to(DEVICE),
                    torch.cat([g.edge_attr for g in loader.dataset], dim=0).to(DEVICE),
                    d_perm
                ).squeeze()
                auc = roc_auc_score(test_y, torch.sigmoid(logits).cpu().numpy())
                importances[perm, d] = baseline_auc - auc
    
    return importances.mean(axis=0), importances.std(axis=0)


def compute_all_attributions(model_name: str, desc_name: str, n_desc: int, split_type: str = "scaffold"):
    panel = load_panel()
    graphs = load_graphs()
    desc = torch.tensor(load_descriptors_from_panel(desc_name), dtype=torch.float32)
    folds = load_splits(split_type)
    
    fold_attrs_ig = []
    fold_attrs_perm_mean = []
    fold_attrs_perm_std = []
    
    for fold_idx in range(N_FOLDS):
        for seed_idx, seed in enumerate(SEEDS):
            test_idx = folds[fold_idx][seed_idx]["test"]
            test_y = panel.iloc[test_idx]["activity"].values
            
            ckpt_path = P5_ROOT / "results" / f"p5_{model_name}_{split_type}_ckpt.json"
            if not ckpt_path.exists():
                print(f"Checkpoint not found: {ckpt_path}")
                continue
            
            model = build_model_from_ckpt(model_name, ckpt_path, n_desc)
            
            # Integrated gradients (sample a subset for speed)
            sample_idx = test_idx[:min(200, len(test_idx))]
            ig = integrated_gradients(model, graphs, desc, sample_idx, n_steps=20)
            fold_attrs_ig.append(ig)
            
            # Permutation importance
            perm_mean, perm_std = permutation_importance(
                model, graphs, desc, test_idx, test_y, n_perms=5
            )
            fold_attrs_perm_mean.append(perm_mean)
            fold_attrs_perm_std.append(perm_std)
            
            del model
            torch.cuda.empty_cache()
    
    return {
        "integrated_gradients": np.concatenate(fold_attrs_ig, axis=0) if fold_attrs_ig else None,
        "permutation_importance_mean": np.mean(fold_attrs_perm_mean, axis=0) if fold_attrs_perm_mean else None,
        "permutation_importance_std": np.mean(fold_attrs_perm_std, axis=0) if fold_attrs_perm_std else None,
        "per_importance_per_fold": np.array(fold_attrs_perm_mean) if fold_attrs_perm_mean else None,
    }


if __name__ == "__main__":
    results = {}
    
    # GIN-TFP (78 dims)
    print("Computing attributions for GIN-TFP...")
    tfp_results = compute_all_attributions("GIN-TFP", "tfp", 78, "scaffold")
    results["GIN-TFP"] = {
        k: v.tolist() if v is not None else None 
        for k, v in tfp_results.items()
    }
    
    # GIN-TNE (192 dims)
    print("Computing attributions for GIN-TNE...")
    tne_results = compute_all_attributions("GIN-TNE", "tne", 192, "scaffold")
    results["GIN-TNE"] = {
        k: v.tolist() if v is not None else None 
        for k, v in tne_results.items()
    }
    
    out_path = P5_ROOT / "results" / "p5_attributions_rigorous.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved to {out_path}")
    
    # Summary stats
    for model_name, res in results.items():
        if res["permutation_importance_mean"] is not None:
            imp = np.array(res["permutation_importance_mean"])
            print(f"\n{model_name} Permutation Importance:")
            print(f"  Top-5 dims: {np.argsort(imp)[-5:][::-1]}")
            print(f"  Top-5 values: {imp[np.argsort(imp)[-5:][::-1]]}")
            print(f"  Mean: {imp.mean():.4f}, Std: {imp.std():.4f}")