#!/usr/bin/env python3
"""Molecular-size control for the RRS Class A benchmark (ledger L122, caveat a).

`p3_resistance_benchmark.py` shows that RRS Class A is predictable from TDA
features (H1+H0, AUC 0.875). That number on its own does not establish that
topology carries resilience signal, because ledger L121 shows the continuous
H1-RRS correlation is entirely accounted for by molecular weight. The control
that decides it is a classifier trained on size descriptors alone, on the same
compounds, under the same protocol.

Three arms, identical folds:
  size       -- MW, ring count, heavy atoms, Fsp3
  H1+H0      -- the 22 topological features, reproducing the published arm
  H1+H0+size -- both, to test whether topology adds over size

Two deliberate differences from p3_resistance_benchmark.py:
  1. The scaler is fitted on the training fold and applied to the test fold.
     The original fits a separate scaler on the test fold, which is the same
     train/test scaling mismatch the manuscript reports fixing as C3 in the
     QKS benchmark. Random Forests are scale-invariant so this changes little,
     but the comparison here must not carry the defect it is auditing.
  2. Paths resolve to this project, not to the sibling folder.

Output: results/p3_resistance_size_baseline.{csv,txt}
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

RDLogger.DisableLog("rdApp.*")

PROJECT = Path(__file__).resolve().parent.parent
REPO = PROJECT.parent
RESULTS = PROJECT / "results"
TARTARUS = REPO / "Project2_Polypharmacology_MD_ValidationV2607" / "results" / "tartarus_output.csv"

TARGETS = ["PfDHFR", "PfATP4", "PfCRT"]
BINDING_CUTOFF = -7.0
CLASS_A_CUTOFF = 8.0
SEED = 42
N_FOLDS = 5


def load_cohort() -> pd.DataFrame:
    """Merge TDA fingerprints with Tartarus docking and label RRS Class A.

    Label definition is copied from p3_resistance_benchmark.py so the arms
    remain comparable with the published numbers.
    """
    tda = pd.read_csv(RESULTS / "p3_tda_fingerprints.csv")
    tart = pd.read_csv(TARTARUS)[["smile", "score_1syh", "score_6y2f", "score_4lde"]]
    tart.columns = ["smiles"] + TARGETS
    for col in TARGETS:
        tart[col] = tart[col].replace(10000.0, np.nan)

    df = tda.merge(tart, on="smiles", how="inner")

    def rrs(row: pd.Series) -> float:
        bound = [abs(row[t]) for t in TARGETS
                 if pd.notna(row[t]) and row[t] <= BINDING_CUTOFF]
        return np.mean(bound) if len(bound) >= 2 else np.nan

    df["RRS"] = df.apply(rrs, axis=1)
    df = df.dropna(subset=["RRS"]).copy()
    df["is_A"] = (df["RRS"] >= CLASS_A_CUTOFF).astype(int)
    return df


def size_descriptors(smiles: pd.Series) -> pd.DataFrame:
    """Four plain size/shape descriptors. Unparseable SMILES yield NaN rows."""
    rows = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            rows.append({"MW": np.nan, "n_rings": np.nan,
                         "heavy_atoms": np.nan, "Fsp3": np.nan})
            continue
        rows.append({
            "MW": Descriptors.MolWt(mol),
            "n_rings": Descriptors.RingCount(mol),
            "heavy_atoms": Descriptors.HeavyAtomCount(mol),
            "Fsp3": Descriptors.FractionCSP3(mol),
        })
    return pd.DataFrame(rows, index=smiles.index)


def ecfp4_features(smiles: pd.Series) -> pd.DataFrame:
    """2048-bit ECFP4 (Morgan radius 2), the classical baseline used
    throughout this paper. Unparseable SMILES yield an all-zero row."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    rows = np.zeros((len(smiles), 2048), dtype=np.int8)
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            rows[i] = gen.GetFingerprintAsNumPy(mol).astype(np.int8)
    return pd.DataFrame(rows, index=smiles.index,
                        columns=[f"ecfp4_{i}" for i in range(2048)])


def cv_auc(X: np.ndarray, y: np.ndarray, protocol: str) -> list[float]:
    """Per-fold AUCs. Folds are seed-fixed so arms are paired.

    protocol='published' reproduces p3_resistance_benchmark.py, which fits a
    separate scaler on the test fold. That is a train/test scaling mismatch,
    but every arm must share it for the arms to be comparable with the
    published H1+H0 value of 0.8749.
    protocol='corrected' fits the scaler on the training fold only.
    """
    skf = StratifiedKFold(N_FOLDS, shuffle=True, random_state=SEED)
    aucs = []
    for train_idx, test_idx in skf.split(X, y):
        train_scaler = StandardScaler().fit(X[train_idx])
        if protocol == "published":
            test_X = StandardScaler().fit_transform(X[test_idx])
        else:
            test_X = train_scaler.transform(X[test_idx])
        clf = RandomForestClassifier(n_estimators=500, class_weight="balanced",
                                     random_state=SEED, n_jobs=-1)
        clf.fit(train_scaler.transform(X[train_idx]), y[train_idx])
        aucs.append(float(roc_auc_score(y[test_idx], clf.predict_proba(test_X)[:, 1])))
    return aucs


def run_protocol(df: pd.DataFrame, arms: dict[str, list[str]],
                 protocol: str) -> tuple[list[dict], dict[str, list[float]]]:
    """Evaluate every arm under one scaling protocol on shared folds."""
    y = df["is_A"].values
    folds: dict[str, list[float]] = {}
    results = []
    for name, cols in arms.items():
        X = np.nan_to_num(df[cols].values.astype(float))
        aucs = cv_auc(X, y, protocol)
        folds[name] = aucs
        mean, std = float(np.mean(aucs)), float(np.std(aucs))
        print(f"  {name:<12} ({len(cols):5d} feats): AUC = {mean:.4f} +/- {std:.4f}",
              flush=True)
        results.append({"protocol": protocol, "arm": name, "n_features": len(cols),
                        "auc_mean": mean, "auc_std": std, "n_molecules": len(y),
                        "fold_aucs": ";".join(f"{a:.4f}" for a in aucs)})
    return results, folds


def main() -> None:
    df = load_cohort()
    sizes = size_descriptors(df["smiles"])
    df = pd.concat([df, sizes], axis=1).dropna(subset=list(sizes.columns))

    n_a = int(df["is_A"].sum())
    print(f"Cohort: {len(df)} compounds (Class A: {n_a}, non-A: {len(df) - n_a})",
          flush=True)

    print("Computing ECFP4 fingerprints...", flush=True)
    ecfp = ecfp4_features(df["smiles"])
    df = pd.concat([df, ecfp], axis=1)

    size_cols = list(sizes.columns)
    topo_cols = [c for c in df.columns
                 if c.startswith("H1_") or c.startswith("H0_")]
    ecfp_cols = list(ecfp.columns)

    # The four single-family feature sets reproduce the remaining arms of
    # p3_resistance_benchmark.py, which were published under the test-fold
    # scaler and have not otherwise been re-evaluated.
    arms = {
        "size": size_cols,
        "ECFP4": ecfp_cols,
        "H1_stats": [c for c in df.columns if c.startswith("H1_")],
        "H0_stats": [c for c in df.columns if c.startswith("H0_")],
        "pers_img": [c for c in df.columns if c.startswith("pers_img_")],
        "betti": [c for c in df.columns if c.startswith("betti_")],
        "H1+H0": topo_cols,
        "H1+H0+size": topo_cols + size_cols,
    }

    all_results: list[dict] = []
    all_folds: dict[str, dict[str, list[float]]] = {}
    for protocol in ("published", "corrected"):
        print(f"\n[{protocol} protocol]", flush=True)
        res, folds = run_protocol(df, arms, protocol)
        all_results.extend(res)
        all_folds[protocol] = folds

    pd.DataFrame(all_results).to_csv(
        RESULTS / "p3_resistance_size_baseline.csv", index=False)

    def paired(folds: dict[str, list[float]],
               arm_a: str, arm_b: str) -> tuple[float, float, float]:
        """Arms share fold assignments, so pair fold by fold."""
        diff = np.array(folds[arm_a]) - np.array(folds[arm_b])
        t, p = stats.ttest_rel(folds[arm_a], folds[arm_b])
        return float(np.mean(diff)), float(t), float(p)

    comparisons = [("H1+H0", "size"), ("H1+H0+size", "size"),
                   ("ECFP4", "size"), ("H1+H0", "ECFP4"),
                   ("H1_stats", "size"), ("H0_stats", "size"),
                   ("pers_img", "size"), ("betti", "size"),
                   ("pers_img", "H1+H0"), ("betti", "H1+H0")]

    with open(RESULTS / "p3_resistance_size_baseline.txt", "w") as fh:
        fh.write("P3 Resistance Benchmark -- Size and ECFP4 Controls\n")
        fh.write(f"Compounds: {len(df)} (Class A: {n_a}, non-A: {len(df) - n_a})\n")
        fh.write(f"Folds: {N_FOLDS}, Classifier: RF(500, balanced)\n")
        fh.write(f"Size descriptors: {', '.join(size_cols)}\n")
        fh.write("ECFP4: Morgan radius 2, 2048 bits\n")
        fh.write("\nProtocols: 'published' reproduces p3_resistance_benchmark.py "
                 "(separate scaler fitted on the test fold);\n"
                 "'corrected' fits the scaler on training folds only. "
                 "Arms are only comparable within a protocol.\n")
        for protocol in ("published", "corrected"):
            rows = [r for r in all_results if r["protocol"] == protocol]
            fh.write(f"\n=== {protocol} protocol ===\n")
            for r in sorted(rows, key=lambda x: -x["auc_mean"]):
                fh.write(f"{r['arm']:<12} AUC {r['auc_mean']:.4f} +/- "
                         f"{r['auc_std']:.4f}  ({r['n_features']} feats)\n")
            fh.write("Fold-paired t-tests (5 folds, identical splits):\n")
            for arm_a, arm_b in comparisons:
                d, t, p = paired(all_folds[protocol], arm_a, arm_b)
                fh.write(f"  {arm_a:<12} vs {arm_b:<6} dAUC {d:+.4f}  "
                         f"t = {t:+.3f}  p = {p:.4f}\n")

    print("\nSaved p3_resistance_size_baseline.{csv,txt}", flush=True)


if __name__ == "__main__":
    main()
