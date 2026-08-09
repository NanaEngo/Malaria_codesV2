#!/usr/bin/env python
"""
P4 alternative activity oracle: RF classifier on ECFP4 fingerprints.

Trains on the P5 canonical panel (n=19,836), then predicts activity
probabilities for P4 best-in-seed molecules from the v12 benchmark.
Compares with the current Tanimoto-based activity proxy.
"""
import sys, os, json, warnings
import numpy as np
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")

# ── paths ──
P5_PANEL = Path("/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery/results/p5_canonical_panel.csv")
P4_V12_DIR = Path("/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/results/benchmark_molecules_opt_v12")
P4_MERGED = P4_V12_DIR / "p4_benchmark_merged.csv"
P4_PARETO = Path("/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/results/pareto/merged_pareto_front.csv")
OUT_DIR = Path("/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/results/pareto")
OUT_FILE = OUT_DIR / "p4_activity_rf_oracle.json"

# ── 1. Load P5 panel and train RF on ECFP4 ──
print("Loading P5 canonical panel...")
panel = pd.read_csv(P5_PANEL)
# The panel has smiles, activity, then tfp_* and tne_* columns.
# We need ECFP4 fingerprints, not TFP/TNE. Let's compute them from SMILES.
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

print(f"Panel: {len(panel)} molecules, {panel['activity'].sum()} active")

# Compute ECFP4 fingerprints
def compute_ecfp4(smiles_list, n_bits=2048, radius=2):
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            fps.append(np.zeros(n_bits, dtype=np.float32))
        else:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
            arr = np.zeros(n_bits, dtype=np.float32)
            AllChem.DataStructs.ConvertToNumpyArray(fp, arr)
            fps.append(arr)
    return np.array(fps)

print("Computing ECFP4 fingerprints for P5 panel...")
X = compute_ecfp4(panel["smiles"].tolist())
y = panel["activity"].values.astype(int)

# Train RF
print("Training RF classifier (5-fold CV)...")
rf = RandomForestClassifier(n_estimators=500, random_state=42, n_jobs=-1)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(rf, X, y, cv=cv, scoring="roc_auc")
print(f"  P5 panel ECFP4-RF CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Fit on full panel
rf.fit(X, y)
print("  Full-fit done.")

# ── 2. Load P4 best-in-seed molecules ──
print("\nLoading P4 v12 benchmark molecules...")
all_mols = []
for seed in range(20):
    f = P4_V12_DIR / f"p4_benchmark_molecules_seed_{seed}.csv"
    if f.exists():
        df = pd.read_csv(f)
        # Find the best molecule (highest reward)
        if "reward" in df.columns:
            best = df.loc[df["reward"].idxmax()]
        elif "scalar_reward" in df.columns:
            best = df.loc[df["scalar_reward"].idxmax()]
        else:
            best = df.iloc[0]
        best["_seed"] = seed
        all_mols.append(best)

if not all_mols:
    print("ERROR: No seed files found. Checking merged file...")
    if P4_MERGED.exists():
        merged = pd.read_csv(P4_MERGED)
        print(f"  Merged file columns: {list(merged.columns)}")
        print(f"  Merged file shape: {merged.shape}")
    sys.exit(1)

p4_df = pd.DataFrame(all_mols)
print(f"  Loaded {len(p4_df)} best-in-seed molecules")

# Find SMILES column
smi_col = None
for c in ["smiles", "SMILES", "canonical_smiles", "mol_smiles", "best_smiles"]:
    if c in p4_df.columns:
        smi_col = c
        break
if smi_col is None:
    print(f"  Available columns: {list(p4_df.columns)}")
    print("  Cannot find SMILES column. Exiting.")
    sys.exit(1)

print(f"  SMILES column: {smi_col}")

# ── 3. Compute ECFP4 for P4 molecules and predict ──
p4_smiles = p4_df[smi_col].tolist()
X_p4 = compute_ecfp4(p4_smiles)
p4_probs = rf.predict_proba(X_p4)[:, 1]
p4_preds = rf.predict(X_p4)

p4_df["rf_activity_prob"] = p4_probs
p4_df["rf_activity_pred"] = p4_preds

print(f"\nP4 best-in-seed RF activity probabilities:")
for _, row in p4_df.iterrows():
    seed = int(row["_seed"])
    prob = row["rf_activity_prob"]
    pred = int(row["rf_activity_pred"])
    smi_short = str(row[smi_col])[:50]
    print(f"  seed {seed:2d}: prob={prob:.4f} pred={pred}  {smi_short}...")

# ── 4. Load Pareto front and predict ──
print("\nLoading Pareto front...")
if P4_PARETO.exists():
    pareto = pd.read_csv(P4_PARETO)
    pareto_smi_col = None
    for c in ["smiles", "SMILES", "canonical_smiles"]:
        if c in pareto.columns:
            pareto_smi_col = c
            break
    if pareto_smi_col:
        X_pareto = compute_ecfp4(pareto[pareto_smi_col].tolist())
        pareto_probs = rf.predict_proba(X_pareto)[:, 1]
        pareto["rf_activity_prob"] = pareto_probs
        print(f"  Pareto front ({len(pareto)} points) RF activity probabilities:")
        for _, row in pareto.iterrows():
            prob = row["rf_activity_prob"]
            smi_short = str(row[pareto_smi_col])[:50]
            print(f"    prob={prob:.4f}  {smi_short}...")
    else:
        print(f"  Pareto columns: {list(pareto.columns)}")

# ── 5. Compare with current Tanimoto-based proxy ──
# The current activity oracle uses max Tanimoto to known actives.
# Let's compute that for comparison.
print("\nComputing Tanimoto-based activity proxy (max Tanimoto to P5 actives)...")
active_mask = y == 1
active_fps_rdkit = []
for i, smi in enumerate(panel["smiles"].tolist()):
    if active_mask[i]:
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            active_fps_rdkit.append(AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048))

from rdkit.DataStructs import BulkTanimotoSimilarity

tanimoto_max = []
for fp in [AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(s), 2, nBits=2048) 
           for s in p4_smiles if Chem.MolFromSmiles(s) is not None]:
    sims = BulkTanimotoSimilarity(fp, active_fps_rdkit)
    tanimoto_max.append(max(sims))

# Add to p4_df (only for valid molecules)
valid_count = sum(1 for s in p4_smiles if Chem.MolFromSmiles(s) is not None)
if valid_count == len(tanimoto_max):
    p4_df["tanimoto_max_activity"] = tanimoto_max
    print(f"  Tanimoto-max activity for {len(tanimoto_max)} P4 molecules:")
    for i, (_, row) in enumerate(p4_df.iterrows()):
        tan = row.get("tanimoto_max_activity", "N/A")
        rf_prob = row["rf_activity_prob"]
        print(f"    seed {int(row['_seed']):2d}: RF={rf_prob:.4f}  Tanimoto-max={tan:.4f}")

# ── 6. Summary statistics ──
print("\n" + "="*60)
print("SUMMARY: RF activity oracle vs Tanimoto-based proxy")
print("="*60)
print(f"  P4 best-in-seed molecules: {len(p4_df)}")
print(f"  RF activity prob (mean ± std): {p4_df['rf_activity_prob'].mean():.4f} ± {p4_df['rf_activity_prob'].std():.4f}")
print(f"  RF activity pred (active): {p4_df['rf_activity_pred'].sum()}/{len(p4_df)}")
if "tanimoto_max_activity" in p4_df.columns:
    print(f"  Tanimoto-max (mean ± std): {p4_df['tanimoto_max_activity'].mean():.4f} ± {p4_df['tanimoto_max_activity'].std():.4f}")
    # Correlation
    corr = p4_df["rf_activity_prob"].corr(p4_df["tanimoto_max_activity"])
    print(f"  Correlation (RF prob vs Tanimoto-max): {corr:.4f}")

# Save results
result = {
    "p5_cv_auc": f"{cv_scores.mean():.4f} ± {cv_scores.std():.4f}",
    "p5_n": len(panel),
    "p5_active": int(y.sum()),
    "p4_n": len(p4_df),
    "p4_rf_mean_prob": f"{p4_df['rf_activity_prob'].mean():.4f}",
    "p4_rf_std_prob": f"{p4_df['rf_activity_prob'].std():.4f}",
    "p4_rf_active_count": int(p4_df["rf_activity_pred"].sum()),
    "per_seed": [],
}

for _, row in p4_df.iterrows():
    entry = {
        "seed": int(row["_seed"]),
        "rf_activity_prob": round(float(row["rf_activity_prob"]), 4),
        "rf_activity_pred": int(row["rf_activity_pred"]),
    }
    if "tanimoto_max_activity" in row:
        entry["tanimoto_max"] = round(float(row["tanimoto_max_activity"]), 4)
    result["per_seed"].append(entry)

OUT_DIR.mkdir(parents=True, exist_ok=True)
with open(OUT_FILE, "w") as f:
    json.dump(result, f, indent=2)
print(f"\nSaved to {OUT_FILE}")
print("Done.")
