#!/usr/bin/env python3
"""
P5 — #2: Distance-to-nearest-training-compound (NN-Tanimoto) decile stratification
on the frozen scaffold splits.

Goal: per-fold-seed, compute the ECFP4 nearest-training Tanimoto for every test
molecule; stratify into 10 deciles; report per-decile ROC-AUC for all 5 arms
(ECFP4-RF, GIN, GIN-TFP, GIN-TNE, ChemBERTa) and for both canonical partitions
(random and scaffold).

Inputs (frozen, never overwritten):
  results/p5_canonical_panel.csv
  results/p5_splits_{random,scaffold}_5fold_seed{0..4}.npy
  results/extended_campaign_20260825/training/{random,scaffold}/{model}/pred_seed*_fold*.csv
  results/extended_campaign_20260825/chemberta/{random,scaffold}/pred_seed*_fold*.csv

Outputs (post-hoc, versioned):
  results/nn_tanimoto_deciles_20260829/
    per_molecule_<split>_<model>_seed*_fold*.npz
    decile_auc_<split>_<model>.csv          (10 rows per (model, split))
    decile_summary_<split>.json
    per_decile_means_<split>.csv            (5 arms × 10 deciles)
    audit.json

Protocol (declarative, locked):
  - ECFP4 (Morgan radius=2, 2048 bits) computed from panel SMILES once.
  - For each (split, seed, fold), test molecules are scored against the
    *training* molecules of that fold using scikit-learn NearestNeighbors on
    the binary ECFP4 bit matrix with Tanimoto distance.
  - Test predictions for the GNN-family arms are read from the archived
    per-fold-seed files in extended_campaign_20260825/training/.
  - ECFP4-RF is re-fit per fold with the canonical protocol (500 trees,
    StandardScaler, random_state=0) and predictions are written to per-fold
    files inside this script's output directory.
  - ChemBERTa predictions are read from extended_campaign_20260825/chemberta/.
  - Per-fold-seed: assign each test molecule to a decile by its NN-Tanimoto
    *similarity* (1 - distance) on the *pooled* test set of that fold-seed
    (10 equal-frequency bins by quantile). Per-decile ROC-AUC is computed
    from the per-molecule y/p pairs.
  - Per-model aggregation: 25 fold-seeds → 5 per-seed means; report
    mean ± SD across the 5 per-seed means, separately for the two splits.

No model is retrained except the ECFP4-RF baseline (the canonical ECFP4-RF
result CSVs store fold-level AUCs only, not per-molecule predictions, so a
refit is the only way to obtain per-molecule p for decile stratification).
GNN/Transformer checkpoints are NOT touched.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

P5_ROOT = Path(__file__).resolve().parent.parent
PANEL_CSV = P5_ROOT / "results" / "p5_canonical_panel.csv"
SPLITS_DIR = P5_ROOT / "results"
EXT_CAMPAIGN = P5_ROOT / "results" / "extended_campaign_20260825"
CHEMBERTA_DIR = EXT_CAMPAIGN / "chemberta"
OUT = P5_ROOT / "results" / "nn_tanimoto_deciles_20260829"

SEEDS = [0, 1, 2, 3, 4]
N_DECILES = 10
ARMS = ("ECFP4-RF", "GIN", "GIN-TFP", "GIN-TNE", "ChemBERTa")
SPLITS = ("random", "scaffold")

# Map model -> directory glob pattern for archived per-fold-seed predictions
GNN_PRED_DIR = {
    "random":   EXT_CAMPAIGN / "training" / "canonical_random",
    "scaffold": EXT_CAMPAIGN / "training" / "canonical_scaffold",
}
GNN_PRED_SUBDIR = {
    "GIN":      "GIN_native",
    "GIN-TFP":  "GIN-TFP_native",
    "GIN-TNE":  "GIN-TNE_native",
}
CHEMBERTA_PRED_DIR = {
    "random":   CHEMBERTA_DIR / "canonical_random",
    "scaffold": CHEMBERTA_DIR / "canonical_scaffold",
}


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def ecfp4_matrix(smiles: list[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    rows = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            arr = np.zeros(2048, dtype=np.float32)
            ConvertToNumpyArray(gen.GetFingerprint(mol), arr)
            rows[i] = arr
    return rows


def load_splits(split_type: str, panel_n: int) -> list:
    """Return a list (per seed) of length-5 arrays of dicts with 'train'/'test' indices.

    Scaffold: load the canonical .npy files.
    Random:   the canonical .npy files are not on disk in this checkout; reconstruct
              from the GIN_native archived predictions under extended_campaign_20260825/
              by union-complement (each fold's test set is the union of all other folds'
              training set under a stratified random partition).
    """
    folds: list = []
    for s in SEEDS:
        path = SPLITS_DIR / f"p5_splits_{split_type}_5fold_seed{s}.npy"
        if path.exists():
            folds.append(np.load(path, allow_pickle=True))
            continue
        if split_type != "random":
            raise FileNotFoundError(f"Missing canonical split file: {path}")
        # Reconstruct random split from archived GIN_native test indices
        gnn_dir = GNN_PRED_DIR["random"] / GNN_PRED_SUBDIR["GIN"]
        per_fold_test = []
        for f_idx in range(5):
            df = pd.read_csv(gnn_dir / f"pred_seed{s}_fold{f_idx}.csv")
            per_fold_test.append(np.sort(df["index"].to_numpy(dtype=np.int64)))
        # Sanity: union should cover the panel
        union = np.sort(np.concatenate(per_fold_test))
        if union.size != panel_n:
            raise RuntimeError(
                f"Reconstructed random split union size {union.size} != panel_n {panel_n}; "
                f"cannot reconstruct safely."
            )
        # Folds should be approximately disjoint and approximately equal size
        # (stratified random). The complement of test is train.
        per_seed_folds = []
        for f_idx in range(5):
            test_idx = per_fold_test[f_idx]
            train_idx = np.setdiff1d(union, test_idx, assume_unique=False)
            per_seed_folds.append({"train": train_idx, "test": test_idx})
        _log(f"  reconstructed random split seed={s} from archived GIN_native preds")
        folds.append(per_seed_folds)
    return folds


def fit_ecfp4rf_per_fold(X: np.ndarray, y: np.ndarray, train_idx: np.ndarray) -> np.ndarray:
    """Re-fit the canonical ECFP4-RF (StandardScaler + RF 500 trees, random_state=0)."""
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=0)),
    ])
    pipe.fit(X[train_idx], y[train_idx])
    return pipe.predict_proba(X)[:, 1]


def read_gnn_preds(split_type: str, model: str, seed: int, fold: int) -> Optional[pd.DataFrame]:
    """Read archived per-fold-seed pred_*.csv (schema: index,y,p)."""
    sub = GNN_PRED_SUBDIR[model]
    f = GNN_PRED_DIR[split_type] / sub / f"pred_seed{seed}_fold{fold}.csv"
    if not f.exists():
        return None
    return pd.read_csv(f)


def read_chemberta_preds(split_type: str, seed: int, fold: int) -> Optional[pd.DataFrame]:
    f = CHEMBERTA_PRED_DIR[split_type] / f"pred_seed{seed}_fold{fold}.csv"
    if not f.exists():
        return None
    return pd.read_csv(f)


def per_fold_nn_tanimoto(X: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray) -> np.ndarray:
    """For each test molecule, return its nearest-training Tanimoto similarity (0..1)."""
    if len(train_idx) == 0 or len(test_idx) == 0:
        return np.zeros(len(test_idx), dtype=np.float32)
    # scikit-learn NearestNeighbors on the binary bit matrix with Tanimoto metric.
    # Note: skNearestNeighbors metric='jaccard' is the Tanimoto distance for binary vectors
    # (1 - |A∩B|/|A∪B|). We then convert to similarity 1 - d.
    nn = NearestNeighbors(n_neighbors=1, metric="jaccard", n_jobs=-1)
    nn.fit(X[train_idx])
    d, _ = nn.kneighbors(X[test_idx], n_neighbors=1, return_distance=True)
    sim = 1.0 - d.ravel()
    return sim.astype(np.float32)


def assign_deciles(sim: np.ndarray, n_bins: int = N_DECILES) -> np.ndarray:
    """Assign each value to an equal-frequency decile bin (1..n_bins) by quantile.

    Uses pandas qcut with duplicates='drop' to handle ties; bin labels are 1-indexed.
    """
    if len(sim) == 0:
        return np.array([], dtype=np.int64)
    s = pd.Series(sim)
    bins = pd.qcut(s, q=n_bins, labels=False, duplicates="drop") + 1
    out = bins.to_numpy(dtype=np.int64)
    # If duplicates='drop' reduced the number of bins, relabel to 1..k contiguous
    uniq = np.unique(out)
    remap = {v: i + 1 for i, v in enumerate(uniq)}
    out = np.array([remap[v] for v in out], dtype=np.int64)
    return out


def per_decile_auc(df: pd.DataFrame, decile_col: str = "decile") -> pd.DataFrame:
    """Per-decile ROC-AUC; NaN for deciles with <2 labels in either class."""
    rows = []
    for k in sorted(df[decile_col].unique()):
        sub = df[df[decile_col] == k]
        y = sub["y"].to_numpy()
        p = sub["p"].to_numpy()
        n_pos = int(y.sum())
        n_neg = int(len(y) - n_pos)
        if n_pos < 2 or n_neg < 2 or len(y) < 5:
            auc = float("nan")
        else:
            try:
                auc = float(roc_auc_score(y, p))
            except ValueError:
                auc = float("nan")
        rows.append({
            "decile": int(k),
            "n": int(len(y)),
            "n_pos": n_pos,
            "n_neg": n_neg,
            "auc": auc,
            "mean_sim": float(sub["nn_tanimoto"].mean()) if "nn_tanimoto" in sub.columns else float("nan"),
        })
    return pd.DataFrame(rows)


def process_split(
    split_type: str,
    panel: pd.DataFrame,
    X: np.ndarray,
    y: np.ndarray,
    splits: list,
) -> dict:
    """Return per-arm × per-decile × per-seed aggregated table."""
    per_arm_decile_records: dict[str, list[pd.DataFrame]] = {a: [] for a in ARMS}
    # Per-fold-seed audit metadata
    fold_seed_audit: list[dict] = []

    for s_idx, seed_folds in enumerate(splits):
        for f_idx, fold in enumerate(seed_folds):
            train_idx = np.asarray(fold["train"], dtype=np.int64)
            test_idx = np.asarray(fold["test"], dtype=np.int64)
            n_train, n_test = len(train_idx), len(test_idx)

            # Per-test-molecule NN-Tanimoto (computed once per (seed, fold) — reused for all arms)
            sim = per_fold_nn_tanimoto(X, train_idx, test_idx)
            deciles = assign_deciles(sim, n_bins=N_DECILES)

            fold_seed_audit.append({
                "seed": SEEDS[s_idx],
                "fold": f_idx,
                "n_train": int(n_train),
                "n_test": int(n_test),
                "nn_sim_mean": float(sim.mean()) if len(sim) else float("nan"),
                "nn_sim_p10":  float(np.quantile(sim, 0.10)) if len(sim) else float("nan"),
                "nn_sim_p50":  float(np.quantile(sim, 0.50)) if len(sim) else float("nan"),
                "nn_sim_p90":  float(np.quantile(sim, 0.90)) if len(sim) else float("nan"),
            })

            base = pd.DataFrame({
                "index": test_idx,
                "y": y[test_idx],
                "nn_tanimoto": sim,
                "decile": deciles,
            })

            for arm in ARMS:
                if arm == "ECFP4-RF":
                    p_test = fit_ecfp4rf_per_fold(X, y, train_idx)[test_idx]
                    arm_df = base.copy()
                    arm_df["p"] = p_test
                elif arm == "ChemBERTa":
                    cb = read_chemberta_preds(split_type, SEEDS[s_idx], f_idx)
                    if cb is None:
                        _log(f"WARN missing ChemBERTa pred {split_type} s{SEEDS[s_idx]} f{f_idx}")
                        continue
                    cb = cb.set_index("index")
                    arm_df = base.copy()
                    arm_df["p"] = arm_df["index"].map(cb["p"]).to_numpy()
                else:
                    gnn = read_gnn_preds(split_type, arm, SEEDS[s_idx], f_idx)
                    if gnn is None:
                        _log(f"WARN missing {arm} pred {split_type} s{SEEDS[s_idx]} f{f_idx}")
                        continue
                    gnn = gnn.set_index("index")
                    arm_df = base.copy()
                    arm_df["p"] = arm_df["index"].map(gnn["p"]).to_numpy()

                # Drop any rows with missing p (e.g. molecule not present in the
                # archived predictions — should not happen on the canonical
                # campaign, but be defensive).
                arm_df = arm_df.dropna(subset=["p", "y", "decile", "nn_tanimoto"])
                # 5 models × 10 deciles × 25 fold-seeds
                da = per_decile_auc(arm_df)
                da["seed"] = SEEDS[s_idx]
                da["fold"] = f_idx
                da["arm"] = arm
                da["split"] = split_type
                per_arm_decile_records[arm].append(da)
                # Persist per-molecule for reproducibility (npz is cheap)
                out_dir = OUT / f"per_molecule_{split_type}_{arm.replace(' ', '_').replace('-', '_')}"
                out_dir.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(
                    out_dir / f"seed{SEEDS[s_idx]}_fold{f_idx}.npz",
                    index=arm_df["index"].to_numpy(),
                    y=arm_df["y"].to_numpy(),
                    p=arm_df["p"].to_numpy(),
                    nn_tanimoto=arm_df["nn_tanimoto"].to_numpy(),
                    decile=arm_df["decile"].to_numpy(),
                )
        _log(f"  split={split_type} seed={SEEDS[s_idx]} done")

    # Aggregate to per-decile × per-seed means (5 seeds) and then mean ± SD across seeds
    summary: dict[str, pd.DataFrame] = {}
    for arm, records in per_arm_decile_records.items():
        if not records:
            _log(f"WARN no records for arm {arm} split {split_type}")
            continue
        df = pd.concat(records, ignore_index=True)
        # For each (decile, seed) average the 5 fold values
        per_seed = df.groupby(["decile", "seed"])["auc"].mean().reset_index()
        agg = per_seed.groupby("decile")["auc"].agg(["mean", "std", "count"]).reset_index()
        agg.columns = ["decile", "auc_mean_seed_mean", "auc_sd_seed_mean", "n_seeds"]
        # Also report n molecules per decile (averaged across fold-seeds)
        n_per_decile = df.groupby("decile")["n"].mean().reset_index()
        n_per_decile.columns = ["decile", "n_mean_per_fold_seed"]
        pos_per_decile = df.groupby("decile")["n_pos"].mean().reset_index()
        pos_per_decile.columns = ["decile", "n_pos_mean_per_fold_seed"]
        sim_per_decile = df.groupby("decile")["mean_sim"].mean().reset_index()
        sim_per_decile.columns = ["decile", "nn_tanimoto_mean"]
        out = agg.merge(n_per_decile, on="decile").merge(pos_per_decile, on="decile").merge(sim_per_decile, on="decile")
        out["arm"] = arm
        out["split"] = split_type
        summary[arm] = out
        # Write per-arm CSV
        out_path = OUT / f"decile_auc_{split_type}_{arm.replace(' ', '_').replace('-', '_')}.csv"
        out.to_csv(out_path, index=False)
        _log(f"  arm={arm} wrote {out_path.name}")
    return {
        "summary_per_arm": summary,
        "fold_seed_audit": fold_seed_audit,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", nargs="+", default=list(SPLITS), choices=list(SPLITS))
    ap.add_argument("--arms", nargs="+", default=list(ARMS), choices=list(ARMS))
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    _log(f"Output dir: {OUT}")
    _log(f"Splits: {args.splits}; arms: {args.arms}")

    panel = pd.read_csv(PANEL_CSV)
    smiles = panel["smiles"].tolist()
    y = panel["activity"].to_numpy(dtype=np.int64)
    _log(f"Panel: {len(panel)} molecules, activity positives = {int(y.sum())}")

    _log("Computing ECFP4 (Morgan r=2, 2048 bits) from SMILES ...")
    t0 = time.perf_counter()
    X = ecfp4_matrix(smiles)
    _log(f"  ECFP4 matrix {X.shape}, t = {time.perf_counter()-t0:.1f}s")

    audit = {
        "panel_n": int(len(panel)),
        "panel_pos": int(y.sum()),
        "ecfp4_shape": list(X.shape),
        "deciles": N_DECILES,
        "seeds": SEEDS,
        "splits": {},
        "git": "post-hoc #2 audit; no retraining except ECFP4-RF",
        "notes": (
            "Random split excluded: the canonical random-split .npy files are not on disk "
            "on this HPC checkout. The GIN random-split archived predictions (training/canonical_random/) "
            "store only test indices, not full train/test splits. The manuscript-relevant claim "
            "for #2 is the scaffold split (chemical novelty)."
        ),
    }

    per_decile_means_all: list[pd.DataFrame] = []
    for split_type in args.splits:
        _log(f"=== split = {split_type} ===")
        splits = load_splits(split_type, len(panel))
        out = process_split(split_type, panel, X, y, splits)
        audit["splits"][split_type] = {
            "n_fold_seed_records": len(out["fold_seed_audit"]),
            "fold_seed_audit": out["fold_seed_audit"],
        }
        for arm, df in out["summary_per_arm"].items():
            per_decile_means_all.append(df)

    # Combined per-decile means table (5 arms × 10 deciles × 2 splits)
    combined = pd.concat(per_decile_means_all, ignore_index=True)
    combined = combined[["split", "arm", "decile", "auc_mean_seed_mean",
                         "auc_sd_seed_mean", "n_seeds",
                         "n_mean_per_fold_seed", "n_pos_mean_per_fold_seed",
                         "nn_tanimoto_mean"]]
    combined_path = OUT / "per_decile_means_all.csv"
    combined.to_csv(combined_path, index=False)
    _log(f"Wrote {combined_path.name} with {len(combined)} rows")

    # Per-split summary JSON
    for split_type in args.splits:
        sub = combined[combined["split"] == split_type]
        per_arm_json = {}
        for arm in args.arms:
            a = sub[sub["arm"] == arm].sort_values("decile")
            per_arm_json[arm] = [
                {
                    "decile": int(r["decile"]),
                    "auc_mean": (None if pd.isna(r["auc_mean_seed_mean"])
                                 else float(r["auc_mean_seed_mean"])),
                    "auc_sd":   (None if pd.isna(r["auc_sd_seed_mean"])
                                 else float(r["auc_sd_seed_mean"])),
                    "n_seeds":  int(r["n_seeds"]),
                    "n_mean_per_fold_seed": (None if pd.isna(r["n_mean_per_fold_seed"])
                                            else float(r["n_mean_per_fold_seed"])),
                    "n_pos_mean_per_fold_seed": (None if pd.isna(r["n_pos_mean_per_fold_seed"])
                                                 else float(r["n_pos_mean_per_fold_seed"])),
                    "nn_tanimoto_mean": (None if pd.isna(r["nn_tanimoto_mean"])
                                         else float(r["nn_tanimoto_mean"])),
                }
                for _, r in a.iterrows()
            ]
        sjson = {
            "split": split_type,
            "deciles": N_DECILES,
            "seeds": SEEDS,
            "per_arm": per_arm_json,
        }
        sp = OUT / f"decile_summary_{split_type}.json"
        with open(sp, "w") as f:
            json.dump(sjson, f, indent=2)
        _log(f"Wrote {sp.name}")

    with open(OUT / "audit.json", "w") as f:
        json.dump(audit, f, indent=2)
    _log(f"Wrote audit.json ({len(audit['splits'])} splits)")
    _log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
