#!/usr/bin/env python3
"""Bounded QKS sensitivity analysis for structure-mapped LISH-MoA.

This is deliberately not a full 206-label production benchmark. It uses the
canonical 6-qubit QKS machinery on a bounded drug cohort and selected labels,
writing all outputs under an isolated directory. The result is a sensitivity
analysis of representation transfer, not an antimalarial or causal MoA claim.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from p3_qks_benchmark import run_benchmark  # noqa: E402

DEFAULT_INPUT = ROOT.parent / "Project5_GNN_Transformer_DrugDiscovery" / "results" / "lish_moa" / "lish_moa_structure_mapped.csv"
DEFAULT_OUT = ROOT / "results" / "lish_moa"


def ecfp4(smiles: list[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    out = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(str(smi))
        if mol is not None:
            ConvertToNumpyArray(gen.GetFingerprint(mol), out[i])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT / "qks_bounded")
    ap.add_argument("--labels", default="top3", help="comma-separated moa_* columns or top3")
    ap.add_argument("--limit-drugs", type=int, default=500)
    ap.add_argument("--n-jobs", type=int, default=8)
    ap.add_argument("--block-size", type=int, default=100)
    args = ap.parse_args()
    df = pd.read_csv(args.input)
    if "smiles" not in df.columns:
        raise ValueError("QKS requires the audited structure-mapped artifact")
    if args.limit_drugs < 100:
        raise ValueError("Use at least 100 drugs for a meaningful bounded QKS sensitivity run")
    labels = [c for c in df.columns if c.startswith("moa_")]
    if args.labels == "top3":
        labels = sorted(labels, key=lambda c: int(df[c].sum()), reverse=True)[:3]
    else:
        labels = [c.strip() for c in args.labels.split(",") if c.strip()]
        missing = [c for c in labels if c not in df.columns]
        if missing:
            raise ValueError("Unknown label(s): " + ", ".join(missing))
    sampling_seed = 20260812
    if len(df) > args.limit_drugs:
        # Do not use head(): CSV order is not a scientific sampling rule.
        # Reserve one positive and one negative example per selected label when
        # possible, then fill the remainder by deterministic random sampling.
        rng = np.random.default_rng(sampling_seed)
        reserved = set()
        for label in labels:
            pos = np.flatnonzero(df[label].to_numpy() == 1)
            neg = np.flatnonzero(df[label].to_numpy() == 0)
            if len(pos): reserved.add(int(pos[0]))
            if len(neg): reserved.add(int(neg[0]))
        remaining = np.array(sorted(set(range(len(df))) - reserved), dtype=int)
        n_extra = max(0, args.limit_drugs - len(reserved))
        chosen = np.r_[sorted(reserved), rng.choice(remaining, size=min(n_extra, len(remaining)), replace=False)]
        df = df.iloc[np.sort(chosen)].reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)
    X = ecfp4(df.smiles.astype(str).tolist())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for label in labels:
        y = df[label].astype(int).to_numpy()
        if len(np.unique(y)) < 2:
            continue
        checkpoint = args.out_dir / f"{label}_checkpoint.json"
        result = run_benchmark(X, y, n_repeats=1, checkpoint_path=str(checkpoint),
                               block_size=args.block_size, n_jobs=args.n_jobs,
                               state_vector=True)
        result["label"] = label
        records.append(result)
        result.to_csv(args.out_dir / f"{label}_folds.csv", index=False)
    if not records:
        raise RuntimeError("No selected label had both positive and negative examples")
    all_results = pd.concat(records, ignore_index=True)
    all_results.to_csv(args.out_dir / "p3_lish_moa_qks_bounded_folds.csv", index=False)
    report = {"input": str(args.input), "n_drugs": len(df), "sampling_seed": sampling_seed,
              "sampling_method": "deterministic random without replacement with per-label sign reservations",
              "labels_requested": labels,
              "labels_evaluated": sorted(all_results.label.unique().tolist()),
              "n_qubits": 6, "n_repeats": 1, "state_vector": True,
              "protocol": "bounded 5-fold QKS/RBF/linear sensitivity; ECFP4→6D QKS features",
              "scope": "external MoA representation sensitivity; not causal target engagement",
              "mean_auc_by_label_model": all_results.groupby(["label", "model"])["auc"].mean().to_dict()}
    (args.out_dir / "p3_lish_moa_qks_bounded_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
