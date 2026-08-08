#!/usr/bin/env python3
"""
P3 Resistance Benchmark: predict RRS Class A from TDA features.

Uses p3_tda_fingerprints.csv (TDA features) merged with Tartarus
docking scores (P2) to benchmark whether topological features predict
resistance resilience better than baseline.
"""

import numpy as np, pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
R = PROJECT_ROOT / "Project3_Quantum_Inspired_RepresentationsV2607" / "results"

# Load TDA features
tda = pd.read_csv(R / "p3_tda_fingerprints.csv")
print(f"TDA features: {len(tda)} compounds, {len(tda.columns)} cols")

# Load Tartarus docking
tart = pd.read_csv(PROJECT_ROOT / "Project2_Polypharmacology_MD_ValidationV2607/results/tartarus_output.csv")
tart = tart[["smile", "score_1syh", "score_6y2f", "score_4lde"]]
tart.columns = ["smiles", "PfDHFR", "PfATP4", "PfCRT"]
for c in ["PfDHFR", "PfATP4", "PfCRT"]:
    tart[c] = tart[c].replace(10000.0, np.nan)

# Merge
df = tda.merge(tart, on="smiles", how="inner")
print(f"Merged: {len(df)} compounds")

# Compute RRS (need >=2 targets bound at <= -7.0 kcal/mol)
def compute_rrs(row):
    scores = [abs(row[c]) for c in ["PfDHFR","PfATP4","PfCRT"]
              if pd.notna(row[c]) and row[c] <= -7.0]
    return np.mean(scores) if len(scores) >= 2 else np.nan

df["RRS"] = df.apply(compute_rrs, axis=1)
df["is_A"] = (df["RRS"] >= 8.0).astype(int)
df = df.dropna(subset=["RRS"])
print(f"Valid RRS: {len(df)} (Class A: {df['is_A'].sum()}, non-A: {(df['is_A']==0).sum()})")

y = df["is_A"].values

# Feature sets
feat_sets = {
    "H1_stats": [c for c in df.columns if c.startswith("H1_")],
    "H0_stats": [c for c in df.columns if c.startswith("H0_")],
    "pers_img": [c for c in df.columns if c.startswith("pers_img_")],
    "betti": [c for c in df.columns if c.startswith("betti_")],
    "H1+H0": [c for c in df.columns if c.startswith("H1_") or c.startswith("H0_")],
}

results = []
skf = StratifiedKFold(5, shuffle=True, random_state=42)
for name, cols in feat_sets.items():
    X = df[cols].values.astype(float)
    if np.isnan(X).any():
        X = np.nan_to_num(X)
    aucs = []
    for tr, te in skf.split(X, y):
        Xs = StandardScaler().fit_transform(X[tr])
        Xte = StandardScaler().fit_transform(X[te])
        clf = RandomForestClassifier(n_estimators=500, class_weight="balanced",
                                     random_state=42, n_jobs=-1)
        clf.fit(Xs, y[tr])
        aucs.append(roc_auc_score(y[te], clf.predict_proba(Xte)[:,1]))
    m, s = np.mean(aucs), np.std(aucs)
    print(f"{name:<15} ({len(cols):4d} feats): AUC = {m:.4f} ± {s:.4f}")
    results.append({"strategy": name, "n_features": len(cols),
                    "auc_mean": m, "auc_std": s, "n_molecules": len(y)})

# Save
pd.DataFrame(results).to_csv(R / "p3_resistance_benchmark.csv", index=False)
with open(R / "p3_resistance_benchmark_summary.txt", "w") as f:
    f.write("P3 Resistance Benchmark\n")
    f.write(f"Compounds: {len(df)} (Class A: {df['is_A'].sum()}, non-A: {(df['is_A']==0).sum()})\n")
    f.write(f"Folds: 5, Classifier: RF(500, balanced)\n\n")
    for r in sorted(results, key=lambda x: -x["auc_mean"]):
        f.write(f"{r['strategy']:<15} AUC {r['auc_mean']:.4f} ± {r['auc_std']:.4f}  ({r['n_features']} feats)\n")

print("\nSaved to p3_resistance_benchmark.csv + _summary.txt")