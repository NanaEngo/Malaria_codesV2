#!/usr/bin/env python3
"""Local, non-training scientific audit for P5 V2.

This script consumes frozen panel/split/results artifacts and writes a versioned
report. It never regenerates splits, trains models, downloads data, or overwrites
canonical benchmark outputs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SEEDS = range(5)
SPLIT_DIR = RESULTS
N_FOLDS = 5


def scaffold(smi: str) -> str:
    from rdkit.Chem.Scaffolds import MurckoScaffold
    mol = Chem.MolFromSmiles(str(smi))
    if mol is None:
        return "INVALID"
    out = MurckoScaffold.MurckoScaffoldSmiles(mol=mol)
    return out or str(smi)


def fold_audit(panel: pd.DataFrame, split_type: str) -> list[dict]:
    y = panel["activity"].to_numpy(dtype=int)
    scaffolds = panel["smiles"].map(scaffold).to_numpy()
    rows = []
    for seed in SEEDS:
        folds = np.load(SPLIT_DIR / f"p5_splits_{split_type}_5fold_seed{seed}.npy", allow_pickle=True)
        for fold, rec in enumerate(folds):
            tr, va, te = (np.asarray(rec[k], dtype=int) for k in ("train", "val", "test"))
            rows.append({
                "split": split_type, "seed": seed, "fold": fold,
                "n_train": len(tr), "n_val": len(va), "n_test": len(te),
                "train_prevalence": float(y[tr].mean()),
                "val_prevalence": float(y[va].mean()),
                "test_prevalence": float(y[te].mean()),
                "n_train_scaffolds": int(len(set(scaffolds[tr]))),
                "n_val_scaffolds": int(len(set(scaffolds[va]))),
                "n_test_scaffolds": int(len(set(scaffolds[te]))),
                "train_test_scaffold_overlap": int(len(set(scaffolds[tr]) & set(scaffolds[te]))),
                "val_test_scaffold_overlap": int(len(set(scaffolds[va]) & set(scaffolds[te]))),
                "train_val_scaffold_overlap": int(len(set(scaffolds[tr]) & set(scaffolds[va]))),
            })
    return rows


def max_train_test_tanimoto(panel: pd.DataFrame, split_type: str, train_sample_limit: int = 2000, test_sample_limit: int = 500) -> list[dict]:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = []
    for smi in panel["smiles"].astype(str):
        mol = Chem.MolFromSmiles(smi)
        fps.append(gen.GetFingerprint(mol) if mol is not None else None)
    rows = []
    for seed in SEEDS:
        folds = np.load(SPLIT_DIR / f"p5_splits_{split_type}_5fold_seed{seed}.npy", allow_pickle=True)
        for fold, rec in enumerate(folds):
            tr = np.asarray(rec["train"], dtype=int)
            te = np.asarray(rec["test"], dtype=int)
            # Bounded deterministic audit: sample both sides to keep exact Tanimoto cost finite.
            tr_eval = tr[:train_sample_limit]
            te_eval = te[:test_sample_limit]
            maxima = []
            for i in te_eval:
                if fps[i] is None:
                    continue
                vals = [DataStructs.TanimotoSimilarity(fps[i], fps[j]) for j in tr_eval if fps[j] is not None]
                if vals:
                    maxima.append(max(vals))
            rows.append({
                "split": split_type, "seed": seed, "fold": fold,
                "n_test_evaluated": len(maxima), "n_test_available": len(te), "n_train_sampled": len(tr_eval),
                "mean_max_train_test_tanimoto": float(np.mean(maxima)) if maxima else None,
                "median_max_train_test_tanimoto": float(np.median(maxima)) if maxima else None,
                "p95_max_train_test_tanimoto": float(np.percentile(maxima, 95)) if maxima else None,
                "max_train_test_tanimoto": float(np.max(maxima)) if maxima else None,
                "bounded_sample": len(tr) > train_sample_limit or len(te) > test_sample_limit,
            })
    return rows


def result_fold_summary() -> pd.DataFrame:
    frames = []
    for p in sorted(RESULTS.glob("p5_*_results.csv")):
        try:
            d = pd.read_csv(p)
        except Exception:
            continue
        if {"model", "fold", "seed", "test_auc", "split"}.issubset(d.columns):
            frames.append(d[["model", "fold", "seed", "test_auc", "split"]])
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def salience_stability() -> list[dict]:
    rows = []
    for p in sorted(RESULTS.glob("p5_*_scaffold_salience.json")):
        d = json.loads(p.read_text())
        vals = np.asarray(d.get("salience_mean", []), dtype=float)
        if vals.size == 0:
            continue
        k = max(1, int(np.ceil(vals.size * 0.10)))
        top = np.argsort(vals)[-k:][::-1]
        rows.append({
            "file": p.name, "n_dimensions": int(vals.size), "n_seen": d.get("n_seen"),
            "top10pct_k": k, "top_dimensions": top.tolist(),
            "top10pct_salience_share": float(vals[top].sum() / vals.sum()),
            "mean_salience": float(vals.mean()), "sd_salience": float(vals.std()),
            "coefficient_of_variation": float(vals.std() / vals.mean()) if vals.mean() else None,
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(RESULTS / "scientific_audit_20260825.json"))
    ap.add_argument("--tanimoto-train-sample", type=int, default=2000)
    ap.add_argument("--tanimoto-test-sample", type=int, default=500)
    ap.add_argument("--split-dir", default=None, help="Explicit directory containing the frozen p5_splits_* files")
    args = ap.parse_args()
    global SPLIT_DIR
    if args.split_dir:
        SPLIT_DIR = Path(args.split_dir).resolve()
    panel = pd.read_csv(RESULTS / "p5_canonical_panel.csv")
    split_files = [SPLIT_DIR / f"p5_splits_{s}_5fold_seed{seed}.npy" for s in ("random", "scaffold") for seed in SEEDS]
    splits_available = all(p.exists() for p in split_files)
    report = {
        "status": "COMPUTED_FROM_FROZEN_ARTIFACTS" if splits_available else "PARTIAL_PENDING_SPLIT_INPUTS",
        "training_performed": False,
        "panel_n": int(len(panel)),
        "panel_active_prevalence": float(panel["activity"].mean()),
        "split_inputs_available": splits_available,
        "fold_audit": ({s: fold_audit(panel, s) for s in ("random", "scaffold")} if splits_available else {}),
        "bounded_tanimoto_audit": ({
            s: max_train_test_tanimoto(panel, s, args.tanimoto_train_sample, args.tanimoto_test_sample)
            for s in ("random", "scaffold")
        } if splits_available else {}),
        "result_fold_summary_rows": int(len(result_fold_summary())),
        "result_fold_summary": result_fold_summary().to_dict(orient="records"),
        "salience_stability": salience_stability(),
        "not_computed": ([("frozen split-dependent fold geometry and train-test Tanimoto audit (split files absent from workspace)")]
                         if not splits_available else []) + [
            "multiple independent scaffold partitions with model retraining",
            "new GIN/TFP/TNE ablation or permutation training",
            "AUPRC recalculation for canonical neural models because prediction probabilities are not archived",
            "ChEMBL threshold sensitivity reruns",
            "tautomer/salt/stereoisomer standardization rerun",
            "individual per-run salience top-k stability because only aggregate vectors are archived",
        ],
        "interpretation_boundary": "Descriptive audit of frozen artifacts; no new model performance claim is authorized by this report.",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out}")
    print(f"panel_n={len(panel)}; result_rows={report['result_fold_summary_rows']}; training_performed=False")


if __name__ == "__main__":
    main()
