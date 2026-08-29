#!/usr/bin/env python
"""P6 Phase 2 GNN arms (GIN / GIN-TFP / GIN-TNE) on the mapped LISH-MoA cohort.

Adapts the locked P5 estimator (p5_models.build_model, AdamW 1e-3 / wd 1e-4,
batch 512, <=50 epochs, patience 10, BCEWithLogitsLoss) to P6's multi-label
estimand (206 moa_* labels) under the leakage gates of
``p6_phase2_benchmark.py``:

* folds over collision groups (primary honest split) or Murcko scaffolds;
* validation is carved from TRAIN groups only (groups dealt round-robin into
  six parts; part 0 = val), so no test group leaks into model selection;
* early stopping on mean column-wise log loss (the primary estimand).

Outputs mirror the phase-2 naming: ``results/p6_phase2/p6_lish_moa_{model}_{split}_*``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJ / "scripts"))
from p6_phase2_benchmark import DRUG_LEVEL, MAPPING, OUT_DIR, SEEDS, make_folds, metrics, scaffold_groups

NUM_WORKERS = int(__import__('os').environ.get('P6_NUM_WORKERS', '2'))

P5_SCRIPTS = PROJ.parent / "Project5_GNN_Transformer_DrugDiscovery_V2" / "scripts"
DESC_NPZ = OUT_DIR / "p6_tfp_tne_descriptors.npz"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def train_val_groups(groups: np.ndarray, seed: int, n_parts: int = 6):
    """Deal TRAIN groups round-robin into n_parts; part 0 becomes validation."""
    unique = np.unique(groups)
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    assign = {g: i % n_parts for i, g in enumerate(unique)}
    part = np.asarray([assign[g] for g in groups])
    return np.where(part != 0)[0], np.where(part == 0)[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", choices=["GIN", "GIN-TFP", "GIN-TNE"], required=True)
    ap.add_argument("--split", choices=["collision_group", "scaffold"], default="collision_group")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dump-predictions", action="store_true",
                     help="Write per-drug per-label test predictions under results/p6_phase2/predictions/<stem>/")
    args = ap.parse_args(argv)

    stem = f"p6_lish_moa_{args.model.lower()}_{args.split}"
    pred_dir = OUT_DIR / "predictions" / stem if args.dump_predictions else None
    if pred_dir is not None:
        pred_dir.mkdir(parents=True, exist_ok=True)

    import torch
    from torch_geometric.data import Data
    from torch_geometric.loader import DataLoader
    sys.path.insert(0, str(P5_SCRIPTS))
    import p5_models
    import p5_data
    from rdkit import Chem

    df = pd.read_csv(DRUG_LEVEL)
    mp = pd.read_csv(MAPPING)[["drug_id", "smiles_rdkit", "collision_group"]]
    df = df.merge(mp, on="drug_id", how="inner", validate="one_to_one").reset_index(drop=True)
    labels = [c for c in df.columns if c.startswith("moa_")]
    smiles = df["smiles_rdkit"].astype(str).tolist()
    cgroups = df["collision_group"].to_numpy()
    scaffolds = scaffold_groups(smiles)
    Y = torch.tensor(df[labels].astype(np.float32).to_numpy())

    uniq = sorted(set(smiles))
    uidx = {s: i for i, s in enumerate(uniq)}
    row2u = np.asarray([uidx[s] for s in smiles])
    mols = {s: Chem.MolFromSmiles(s) for s in uniq}
    graphs_u = [p5_data.mol_to_graph(mols[s]) if mols[s] is not None else None for s in uniq]

    desc = None
    if args.model != "GIN":
        z = np.load(DESC_NPZ, allow_pickle=True)
        dmap = {s: i for i, s in enumerate(z["smiles"].tolist())}
        key = {"GIN-TFP": "tfp", "GIN-TNE": "tne"}[args.model]
        desc_u = z[key][[dmap[s] for s in uniq]].astype(np.float32)
        desc = desc_u[row2u]
        bad = ~np.isfinite(desc).all(axis=1)
        desc[bad] = 0.0

    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    # p5_data.mol_to_graph returns a 4-tuple (x, edge_index, edge_attr, num_atoms);
    # unpack rather than dict-index it.
    _x0, _ei0, _ea0, _ = next(g for g in graphs_u if g is not None)
    in_dim = int(_x0.shape[1])
    edge_dim = int(_ea0.shape[1])

    records = []
    for seed in SEEDS:
        for fold, (tr, te) in enumerate(make_folds(args.split, seed, len(df), cgroups, scaffolds)):
            itr, ite = train_val_groups(cgroups[tr], seed)
            tr_i, va_i, te_i = tr[itr], tr[ite], te
            random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)

            def make(idx):
                out = []
                for i in idx:
                    x, edge_index, edge_attr, _ = graphs_u[row2u[i]]
                    d = Data(x=x, edge_index=edge_index, edge_attr=edge_attr,
                             y=Y[i])
                    if desc is not None:
                        d.desc = torch.tensor(desc[i])
                    out.append(d)
                return out

            loader_kwargs = {'num_workers': NUM_WORKERS, 'pin_memory': device.type == 'cuda'}
            if NUM_WORKERS > 0:
                loader_kwargs.update(persistent_workers=True, prefetch_factor=2)
            tr_loader = DataLoader(make(tr_i), batch_size=512, shuffle=True, **loader_kwargs)
            va_loader = DataLoader(make(va_i), batch_size=512, **loader_kwargs)
            te_loader = DataLoader(make(te_i), batch_size=512, **loader_kwargs)

            model = p5_models.build_model(
                args.model, in_dim, hidden=128, out_dim=len(labels),
                dropout=0.1, edge_dim=edge_dim,
                n_descriptor_features=(desc.shape[1] if desc is not None else None),
            ).to(device)
            opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
            criterion = torch.nn.BCEWithLogitsLoss()

            def predict(loader):
                model.eval(); ps, ys = [], []
                with torch.no_grad():
                    for b in loader:
                        b = b.to(device)
                        logits = model(b.x, b.edge_index, b.batch,
                                       edge_attr=b.edge_attr, desc=getattr(b, "desc", None))
                        ps.append(torch.sigmoid(logits).cpu().numpy())
                        # ponytail: fixed 206-label width from the locked cohort
                        ys.append(b.y.cpu().numpy().reshape(b.num_graphs, -1))
                return np.concatenate(ps), np.concatenate(ys)

            best_ll, best_state, wait = float("inf"), None, 0
            for _epoch in range(50):
                model.train()
                for b in tr_loader:
                    if b.num_graphs < 2:
                        continue
                    b = b.to(device, non_blocking=True); opt.zero_grad(set_to_none=True)
                    with torch.autocast(device_type='cuda', dtype=torch.float16, enabled=device.type == 'cuda'):
                        logits = model(b.x, b.edge_index, b.batch,
                                       edge_attr=b.edge_attr, desc=getattr(b, "desc", None))
                        loss = criterion(logits, b.y.view(b.num_graphs, -1))
                    loss.backward(); opt.step()
                vp, vy = predict(va_loader)
                va_ll = float(metrics(vy.astype(int), np.clip(vp, 1e-7, 1 - 1e-7))["mean_columnwise_log_loss"])
                if va_ll < best_ll:
                    best_ll, wait = va_ll, 0
                    best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                else:
                    wait += 1
                    if wait >= 10:
                        break
            model.load_state_dict(best_state)
            pp, yy = predict(te_loader)
            if pred_dir is not None:
                # ponytail: per-drug per-label dump for calibration/QKS (fail-closed audit needs this)
                # Use dict-of-arrays + pd.concat (axis=1) once instead of 207 single-column inserts
                # which trigger DataFrame fragmentation and dominate wall time.
                cols = {"drug_id": df.iloc[te]["drug_id"].values}
                for j, lbl in enumerate(labels):
                    cols[f"{lbl}_true"] = yy[:, j].astype(int)
                    cols[f"{lbl}_pred"] = pp[:, j]
                out = pd.DataFrame(cols)
                out.to_csv(pred_dir / f"seed{seed}_fold{fold}.csv", index=False)
            rec = {"features": args.model.lower(), "split": args.split, "seed": seed,
                   "fold": fold, "n_train": len(tr_i), "n_val": len(va_i), "n_test": len(te_i),
                   "best_val_log_loss": best_ll}
            rec.update(metrics(yy.astype(int), np.clip(pp, 1e-7, 1 - 1e-7)))
            records.append(rec)
            print(f"{args.model} {args.split} seed={seed} fold={fold} "
                  f"logloss={rec['mean_columnwise_log_loss']:.5f}", flush=True)

    result = pd.DataFrame(records)
    stem = f"p6_lish_moa_{args.model.lower()}_{args.split}"
    result.to_csv(OUT_DIR / f"{stem}_folds.csv", index=False)
    summary = {
        "input": str(DRUG_LEVEL), "mapping": str(MAPPING),
        "mapping_sha256": sha256(MAPPING), "descriptors_sha256": sha256(DESC_NPZ),
        "features": args.model, "split": args.split,
        "n_drugs": len(df), "n_labels": len(labels),
        "n_collision_groups": int(pd.Series(cgroups).nunique()),
        "mean_metrics": result[["mean_columnwise_log_loss", "macro_auprc", "macro_auroc",
                                "mean_brier", "mean_ece"]].mean(numeric_only=True).to_dict(),
        "protocol": ("5 seeds x 5 group-disjoint folds; multi-label GIN head (locked P5 "
                     "optimizer/epochs/patience); val carved from train groups only; early stop "
                     "on val mean column-wise log loss; TFP/TNE zero-vector ITT failures"),
        "interpretation": "MoA-associated prediction; not causal target engagement",
    }
    (OUT_DIR / f"{stem}_report.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["mean_metrics"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
