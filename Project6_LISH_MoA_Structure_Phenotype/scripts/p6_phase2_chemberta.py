#!/usr/bin/env python
"""P6 Phase 2 ChemBERTa arm on the mapped LISH-MoA cohort.

Adapts the locked P5 fine-tuning protocol (seyonec/ChemBERTa-zinc-base-v1,
max_length 128, batch 32, AdamW lr 2e-5 / wd 0.01, <=10 epochs, patience 3) to
P6's multi-label estimand: ``problem_type="multi_label_classification"`` with a
206-unit sigmoid head. Leakage gates identical to ``p6_phase2_gnn.py`` (folds
over collision groups / scaffolds; validation carved from train groups only;
early stop on mean column-wise log loss).

Outputs: ``results/p6_phase2/p6_lish_moa_chemberta_{split}_*``.
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

MODEL_NAME = "seyonec/ChemBERTa-zinc-base-v1"
MAX_LENGTH = 128
BATCH_SIZE = 32
EPOCHS = 10
LR = 2e-5
WEIGHT_DECAY = 0.01
PATIENCE = 3


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def train_val_groups(groups: np.ndarray, seed: int, n_parts: int = 6):
    unique = np.unique(groups)
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    assign = {g: i % n_parts for i, g in enumerate(unique)}
    part = np.asarray([assign[g] for g in groups])
    return np.where(part != 0)[0], np.where(part == 0)[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", choices=["collision_group", "scaffold"], default="collision_group")
    ap.add_argument("--dump-predictions", action="store_true",
                     help="Write per-drug per-label test predictions under results/p6_phase2/predictions/<stem>/")
    args = ap.parse_args(argv)

    stem = f"p6_lish_moa_chemberta_{args.split}"
    pred_dir = OUT_DIR / "predictions" / stem if args.dump_predictions else None
    if pred_dir is not None:
        pred_dir.mkdir(parents=True, exist_ok=True)

    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    df = pd.read_csv(DRUG_LEVEL)
    mp = pd.read_csv(MAPPING)[["drug_id", "smiles_rdkit", "collision_group"]]
    df = df.merge(mp, on="drug_id", how="inner", validate="one_to_one").reset_index(drop=True)
    labels = [c for c in df.columns if c.startswith("moa_")]
    cgroups = df["collision_group"].to_numpy()
    scaffolds = scaffold_groups(df["smiles_rdkit"].astype(str).tolist())
    Yall = df[labels].astype(np.float32).to_numpy()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    class SmilesDataset(Dataset):
        def __init__(self, idx):
            self.enc = tokenizer([str(df["smiles_rdkit"].iloc[i]) for i in idx],
                                 truncation=True, max_length=MAX_LENGTH,
                                 padding="max_length", return_tensors="pt")
            self.y = Yall[idx]

        def __len__(self):
            return len(self.y)

        def __getitem__(self, i):
            item = {k: v[i] for k, v in self.enc.items()}
            item["labels"] = torch.tensor(self.y[i])
            return item

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    records = []
    for seed in SEEDS:
        for fold, (tr, te) in enumerate(make_folds(args.split, seed, len(df), cgroups, scaffolds)):
            itr, ite = train_val_groups(cgroups[tr], seed)
            tr_i, va_i, te_i = tr[itr], tr[ite], te
            random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)

            model = AutoModelForSequenceClassification.from_pretrained(
                MODEL_NAME, num_labels=len(labels),
                problem_type="multi_label_classification",
            ).to(device)
            opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
            amp_enabled = device.type == 'cuda'
            scaler = torch.amp.GradScaler('cuda', enabled=amp_enabled)

            def predict(idx):
                loader_kwargs = {'batch_size': BATCH_SIZE, 'num_workers': NUM_WORKERS,
                                 'pin_memory': device.type == 'cuda'}
                if NUM_WORKERS > 0:
                    loader_kwargs.update(persistent_workers=True, prefetch_factor=2)
                loader = DataLoader(SmilesDataset(idx), **loader_kwargs)
                model.eval(); ps, ys = [], []
                with torch.no_grad():
                    for b in loader:
                        b = {k: v.to(device, non_blocking=True) for k, v in b.items()}
                        logits = model(input_ids=b["input_ids"],
                                       attention_mask=b["attention_mask"]).logits
                        ps.append(torch.sigmoid(logits).cpu().numpy())
                        ys.append(b["labels"].cpu().numpy())
                return np.concatenate(ps), np.concatenate(ys)

            best_ll, best_state, wait = float("inf"), None, 0
            train_loader_kwargs = {'batch_size': BATCH_SIZE, 'shuffle': True,
                                   'num_workers': NUM_WORKERS,
                                   'pin_memory': device.type == 'cuda'}
            if NUM_WORKERS > 0:
                train_loader_kwargs.update(persistent_workers=True, prefetch_factor=2)
            tr_loader = DataLoader(SmilesDataset(tr_i), **train_loader_kwargs)
            for _epoch in range(EPOCHS):
                model.train()
                for b in tr_loader:
                    b = {k: v.to(device, non_blocking=True) for k, v in b.items()}
                    opt.zero_grad(set_to_none=True)
                    with torch.autocast(device_type='cuda', dtype=torch.float16, enabled=amp_enabled):
                        out = model(**b)
                    scaler.scale(out.loss).backward()
                    scaler.step(opt)
                    scaler.update()
                vp, vy = predict(va_i)
                va_ll = float(metrics(vy.astype(int), np.clip(vp, 1e-7, 1 - 1e-7))["mean_columnwise_log_loss"])
                if va_ll < best_ll:
                    best_ll, wait = va_ll, 0
                    best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                else:
                    wait += 1
                    if wait >= PATIENCE:
                        break
            model.load_state_dict(best_state)
            pp, yy = predict(te_i)
            if pred_dir is not None:
                # ponytail: per-drug per-label dump for calibration/QKS (fail-closed audit needs this)
                out = pd.DataFrame({"drug_id": df.iloc[te_i]["drug_id"].values})
                for j, lbl in enumerate(labels):
                    out[f"{lbl}_true"] = yy[:, j].astype(int)
                    out[f"{lbl}_pred"] = pp[:, j]
                out.to_csv(pred_dir / f"seed{seed}_fold{fold}.csv", index=False)
            rec = {"features": "chemberta", "split": args.split, "seed": seed,
                   "fold": fold, "n_train": len(tr_i), "n_val": len(va_i), "n_test": len(te_i),
                   "best_val_log_loss": best_ll}
            rec.update(metrics(yy.astype(int), np.clip(pp, 1e-7, 1 - 1e-7)))
            records.append(rec)
            print(f"chemberta {args.split} seed={seed} fold={fold} "
                  f"logloss={rec['mean_columnwise_log_loss']:.5f}", flush=True)
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    result = pd.DataFrame(records)
    stem = f"p6_lish_moa_chemberta_{args.split}"
    result.to_csv(OUT_DIR / f"{stem}_folds.csv", index=False)
    summary = {
        "input": str(DRUG_LEVEL), "mapping": str(MAPPING),
        "mapping_sha256": sha256(MAPPING),
        "model_name": MODEL_NAME, "features": "chemberta", "split": args.split,
        "n_drugs": len(df), "n_labels": len(labels),
        "n_collision_groups": int(pd.Series(cgroups).nunique()),
        "mean_metrics": result[["mean_columnwise_log_loss", "macro_auprc", "macro_auroc",
                                "mean_brier", "mean_ece"]].mean(numeric_only=True).to_dict(),
        "protocol": ("5 seeds x 5 group-disjoint folds; multi-label ChemBERTa head (locked P5 "
                     "fine-tuning constants); val carved from train groups only; early stop on "
                     "val mean column-wise log loss"),
        "interpretation": "MoA-associated prediction; not causal target engagement",
    }
    (OUT_DIR / f"{stem}_report.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["mean_metrics"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
