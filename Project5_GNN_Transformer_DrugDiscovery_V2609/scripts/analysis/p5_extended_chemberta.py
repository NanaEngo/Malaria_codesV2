#!/usr/bin/env python3
"""Versioned ChemBERTa rerun for the P5 extended campaign.

Outputs are written only below results/extended_campaign_20260825/chemberta.
The pretrained snapshot is pinned by revision and its files are hashed before
training. The script fails closed on incomplete or invalid fold outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import average_precision_score, balanced_accuracy_score, f1_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
PANEL = ROOT / "results" / "p5_canonical_panel.csv"
CAMPAIGN = ROOT / "results" / "extended_campaign_20260825"
OUT_ROOT = CAMPAIGN / "chemberta"
SPLIT_ROOT = CAMPAIGN / "splits"
MODEL_ID = "seyonec/ChemBERTa-zinc-base-v1"
MODEL_REVISION = "761d6a18cf99db371e0b43baf3e2d21b3e865a20"
MODEL_SNAPSHOT = Path(os.environ.get("P5_CHEMBERTA_SNAPSHOT", "/home/nanaengo/.cache/huggingface/hub/models--seyonec--ChemBERTa-zinc-base-v1/snapshots/761d6a18cf99db371e0b43baf3e2d21b3e865a20"))
SEEDS = [0, 1, 2, 3, 4]
N_FOLDS = 5
MAX_LENGTH = 128
BATCH_SIZE = 32
NUM_WORKERS = int(os.environ.get("P5_NUM_WORKERS", "2"))
EPOCHS = 10
LR = 2e-5
WEIGHT_DECAY = 0.01
PATIENCE = 3
PARTITIONS = ["canonical_random", "canonical_scaffold", "novel_101", "novel_202", "novel_303"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True))


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class SmileDataset(Dataset):
    def __init__(self, smiles, labels, tokenizer):
        # Tokenize once per fold instead of invoking the tokenizer for every
        # sample access. This preserves the frozen tokenizer and max length.
        enc = tokenizer(list(smiles), truncation=True, padding="max_length",
                        max_length=MAX_LENGTH, return_tensors="pt")
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.labels = torch.as_tensor(np.asarray(labels, dtype=np.int64), dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        return {"input_ids": self.input_ids[i],
                "attention_mask": self.attention_mask[i],
                "labels": self.labels[i]}


def make_loader(dataset, *, shuffle=False):
    kwargs = {"batch_size": BATCH_SIZE, "shuffle": shuffle,
              "num_workers": NUM_WORKERS, "pin_memory": torch.cuda.is_available()}
    if NUM_WORKERS > 0:
        kwargs["persistent_workers"] = True
        kwargs["prefetch_factor"] = 2
    return DataLoader(dataset, **kwargs)


class NullScaler:
    """Small interface-compatible fallback when AMP is unavailable."""
    def scale(self, loss): return loss
    def step(self, optimizer): optimizer.step()
    def update(self): pass
    def unscale_(self, optimizer): pass


def load_partition_folds(partition: str) -> dict[int, list[dict]]:
    if partition in ("canonical_random", "canonical_scaffold"):
        split = "random" if partition == "canonical_random" else "scaffold"
        source = ROOT.parent / "Project5_GNN_Transformer_DrugDiscovery" / "results"
        return {s: [{k: np.asarray(x[k], dtype=int) for k in ("train", "val", "test")} for x in np.load(source / f"p5_splits_{split}_5fold_seed{s}.npy", allow_pickle=True)] for s in SEEDS}
    arr = np.load(SPLIT_ROOT / f"{partition}.npy", allow_pickle=True)
    return {s: [{k: np.asarray(x[k], dtype=int) for k in ("train", "val", "test")} for x in arr[s * 5:(s + 1) * 5]] for s in SEEDS}


def validate_model_snapshot() -> dict:
    required = ["config.json", "pytorch_model.bin", "tokenizer_config.json", "vocab.json", "merges.txt", "special_tokens_map.json"]
    missing = [x for x in required if not (MODEL_SNAPSHOT / x).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing pinned ChemBERTa files: {missing}")
    return {"model_id": MODEL_ID, "revision": MODEL_REVISION, "snapshot": str(MODEL_SNAPSHOT), "files": {x: {"size": (MODEL_SNAPSHOT / x).stat().st_size, "sha256": sha256(MODEL_SNAPSHOT / x)} for x in required}}


def predict(model, loader, device):
    model.eval(); pred, truth = [], []
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
            pred.append(torch.softmax(model(**batch).logits, dim=1)[:, 1].cpu().numpy())
            truth.append(batch["labels"].cpu().numpy())
    return np.concatenate(pred), np.concatenate(truth)


def run_partition(partition: str, device_name: str, max_new_records: int | None = None) -> None:
    panel = pd.read_csv(PANEL)
    folds = load_partition_folds(partition)
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_SNAPSHOT), local_files_only=True)
    base_model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_SNAPSHOT), num_labels=2, local_files_only=True)
    pretrained = {k: v.cpu().clone() for k, v in base_model.state_dict().items()}
    device = torch.device("cuda" if device_name == "cuda" and torch.cuda.is_available() else "cpu")
    out = OUT_ROOT / partition; out.mkdir(parents=True, exist_ok=True)
    write_json(out / "model_provenance.json", validate_model_snapshot())
    csv_path = out / "fold_results.csv"
    rows = pd.read_csv(csv_path).to_dict("records") if csv_path.exists() else []
    done = {(int(r["seed"]), int(r["fold"])) for r in rows}
    new = 0
    for seed in SEEDS:
        for fold, rec in enumerate(folds[seed]):
            if (seed, fold) in done: continue
            set_seed(seed)
            model = AutoModelForSequenceClassification.from_config(base_model.config).to(device)
            model.load_state_dict(pretrained); model.to(device)
            tr = make_loader(SmileDataset(panel.smiles.iloc[rec["train"]], panel.activity.iloc[rec["train"]], tokenizer), shuffle=True)
            va = make_loader(SmileDataset(panel.smiles.iloc[rec["val"]], panel.activity.iloc[rec["val"]], tokenizer))
            te = make_loader(SmileDataset(panel.smiles.iloc[rec["test"]], panel.activity.iloc[rec["test"]], tokenizer))
            opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY); criterion = nn.CrossEntropyLoss()
            amp_enabled = device.type == "cuda"
            scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled) if amp_enabled else NullScaler()
            best, best_state, wait = -1.0, None, 0
            for _epoch in range(EPOCHS):
                model.train()
                for batch in tr:
                    batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
                    opt.zero_grad(set_to_none=True)
                    with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp_enabled):
                        loss = criterion(model(**batch).logits, batch["labels"])
                    scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
                vp, vy = predict(model, va, device); val_auc = roc_auc_score(vy, vp)
                if val_auc > best: best, best_state, wait = val_auc, {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}, 0
                else:
                    wait += 1
                    if wait >= PATIENCE:
                        break
            if best_state is None:
                raise RuntimeError(f"No validation checkpoint produced for {partition} seed={seed} fold={fold}")
            model.load_state_dict(best_state)
            p, y = predict(model, te, device)
            b = (p >= 0.5).astype(int)
            row = {"partition": partition, "model": "ChemBERTa", "seed": seed, "fold": fold, "best_val_auc": best, "test_auc": roc_auc_score(y, p), "test_ap": average_precision_score(y, p), "test_f1": f1_score(y, b), "test_bacc": balanced_accuracy_score(y, b), "n_test": len(y)}
            rows.append(row); done.add((seed, fold)); new += 1
            pd.DataFrame(rows).sort_values(["seed", "fold"]).to_csv(csv_path, index=False)
            pd.DataFrame({"index": rec["test"], "y": y, "p": p}).to_csv(out / f"pred_seed{seed}_fold{fold}.csv", index=False)
            print(f"{partition} ChemBERTa seed={seed} fold={fold} AUC={row['test_auc']:.4f} AP={row['test_ap']:.4f}", flush=True)
            if max_new_records is not None and new >= max_new_records: break
        if max_new_records is not None and new >= max_new_records: break
    complete = len(rows) == 25 and {(int(r["seed"]), int(r["fold"])) for r in rows} == {(s, f) for s in SEEDS for f in range(5)}
    if rows:
        seed_auc = pd.DataFrame(rows).groupby("seed").test_auc.mean()
        seed_ap = pd.DataFrame(rows).groupby("seed").test_ap.mean()
        summary = {"status": "COMPUTED" if complete else "PARTIAL", "partition": partition, "model": "ChemBERTa", "n_records": len(rows), "expected_records": 25, "mean_auc_fold_seed": float(pd.DataFrame(rows).test_auc.mean()), "mean_ap_fold_seed": float(pd.DataFrame(rows).test_ap.mean()), "mean_auc_seed": float(seed_auc.mean()), "mean_ap_seed": float(seed_ap.mean()), "seed_means_auc": {str(k): float(v) for k, v in seed_auc.items()}, "seed_means_ap": {str(k): float(v) for k, v in seed_ap.items()}, "device": str(device), "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    else: summary = {"status": "PARTIAL", "partition": partition, "model": "ChemBERTa", "n_records": 0, "expected_records": 25}
    write_json(out / "summary.json", summary)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--partition", choices=PARTITIONS, required=True); ap.add_argument("--device", choices=["cpu", "cuda"], default="cuda"); ap.add_argument("--max-new-records", type=int, default=None)
    args = ap.parse_args(); run_partition(args.partition, args.device, args.max_new_records)


if __name__ == "__main__": main()
