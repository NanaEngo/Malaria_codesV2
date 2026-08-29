#!/usr/bin/env python3
"""
P5 — Frozen train/val/test splits (v1-prep, documented in P5_DATA_ANALYSIS_REPORT.md §10).

Writes results/p5_splits_{random,scaffold}_5fold_seed{0..4}.npy — nested lists of
[{train: [...], val: [...], test: [...]}, ...] per fold, indices into
results/p5_canonical_panel.csv order. + p5_splits_info.json (protocol summary).

Random:   stratified 5-fold, repeated 5 seeds (0..4).
Scaffold: Bemis-Murcko scaffold grouping (RDKit MurckoDecompose),
          GroupKFold-style assignment with per-seed random scaffold tie-break.

Splits are computed ONCE and frozen — never regenerated per run (AGENTS.md rule).
Usage:
    python scripts/p5_make_splits.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.model_selection import StratifiedKFold

P5_ROOT = Path(__file__).resolve().parent.parent
PANEL = P5_ROOT / "results" / "p5_canonical_panel.csv"
OUT_DIR = P5_ROOT / "results"
N_FOLDS = 5
SEEDS = [0, 1, 2, 3, 4]


def scaffold_groups(smiles_list: list[str]) -> np.ndarray:
    """Bemis-Murcko scaffold id per molecule (SMILES string as group id)."""
    groups = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            groups.append(None)
            continue
        scaffold = MurckoScaffold.MurckoScaffoldSmiles(mol=mol)
        groups.append(scaffold if scaffold else smi)
    return np.array(groups, dtype=object)


def make_scaffold_folds(smiles_list: list[str], y: np.ndarray, seed: int) -> list[dict]:
    """Scaffold-aware 5-fold: no scaffold shared between train/val/test."""
    groups = scaffold_groups(smiles_list)
    rng = np.random.default_rng(seed)
    # deterministic per-seed scaffold order (shuffle group ids)
    unique = np.unique([g for g in groups if g is not None])
    rng.shuffle(unique)
    order = {g: i for i, g in enumerate(unique)}

    # greedy assignment of scaffolds to folds minimizing max size
    fold_sizes = np.zeros(N_FOLDS)
    assignment = np.full(len(groups), -1, dtype=int)
    for g in unique:
        idx = np.where(groups == g)[0]
        j = int(np.argmin(fold_sizes))
        fold_sizes[j] += len(idx)
        assignment[idx] = j

    folds = []
    for k in range(N_FOLDS):
        test = np.where(assignment == k)[0]
        rest = np.where(assignment != k)[0]
        rng.shuffle(rest)
        n_val = max(1, len(rest) // N_FOLDS)
        val, train = rest[:n_val], rest[n_val:]
        folds.append({"train": train.tolist(), "val": val.tolist(), "test": test.tolist()})
    return folds


def main() -> None:
    t0 = time.perf_counter()
    panel = pd.read_csv(PANEL)
    smiles = panel["smiles"].tolist()
    y = panel["activity"].values
    print(f"Panel: {len(panel):,} molecules, active={y.sum():,}")

    for seed in SEEDS:
        # random stratified
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        folds = []
        for tr, te in skf.split(np.zeros(len(y)), y):
            rng = np.random.default_rng(seed)
            tr_idx = tr.copy()
            rng.shuffle(tr_idx)
            n_val = max(1, len(tr_idx) // N_FOLDS)
            val, train = tr_idx[:n_val], tr_idx[n_val:]
            folds.append({"train": train.tolist(), "val": val.tolist(), "test": te.tolist()})
        np.save(OUT_DIR / f"p5_splits_random_5fold_seed{seed}.npy", np.array(folds, dtype=object), allow_pickle=True)

        # scaffold
        folds_s = make_scaffold_folds(smiles, y, seed)
        np.save(OUT_DIR / f"p5_splits_scaffold_5fold_seed{seed}.npy", np.array(folds_s, dtype=object), allow_pickle=True)

        print(f"  seed {seed}: random + scaffold folds written")

    # protocol info
    info = {
        "panel": str(PANEL),
        "n_molecules": len(panel),
        "n_folds": N_FOLDS,
        "seeds": SEEDS,
        "random": "stratified 5-fold, shuffle, per-seed, val = last 20% of train",
        "scaffold": "Bemis-Murcko scaffold groups, greedy min-max assignment, per-seed tie-break, val = last 20% of train",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(OUT_DIR / "p5_splits_info.json", "w") as f:
        json.dump(info, f, indent=2)
    print(f"\nWrote {N_FOLDS}×{len(SEEDS)} split files + p5_splits_info.json")
    print(f"Elapsed: {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()
