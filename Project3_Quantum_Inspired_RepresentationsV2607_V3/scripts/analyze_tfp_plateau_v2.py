#!/usr/bin/env python3
"""
Analyse rapide du plateau TFP à 0.587 — version allégée.

Bottlenecks évités :
  - RF avec 200 arbres au lieu de 500
  - Subsample à 2000 molécules pour les RF (au lieu de 18K)
  - PCA, variance, corrélation sur données complètes (rapides)
  - Feature importance sur 1 fold seulement (pas 5-fold CV)
  - Group contribution sur 1 fold

Usage:
    /home/taamangtchu/miniforge3/envs/malaria_md/bin/python scripts/analyze_tfp_plateau.py
"""

import time, warnings
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

warnings.filterwarnings("ignore")
morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
ACT_THRESHOLD = 0.5
N_FOLDS = 5
RF_TREES = 200
T0 = time.perf_counter()

def log(msg): print(f"[{time.perf_counter()-T0:6.1f}s] {msg}")

# ── Data loading ──────────────────────────────────────────────────
log("Loading data...")
act_df = pd.read_csv(RESULTS_DIR / "eos80ch_malaria_final_activity.csv")
act_df = act_df[["input","asexual_blood_stage"]].dropna().rename(columns={"input":"smiles","asexual_blood_stage":"activity"})
smiles_list = act_df["smiles"].tolist()
y = (act_df["activity"].values >= ACT_THRESHOLD).astype(int)
log(f"  {len(y)} mol ({y.sum()} active, {(y==0).sum()} inactive)")

# Load TFP enriched
csv_path = RESULTS_DIR / "p3_tda_fingerprints_enriched_78d.csv"
if not csv_path.exists():
    csv_path = RESULTS_DIR / "p3_tda_fingerprints.csv"
tfpdf = pd.read_csv(csv_path).set_index("smiles")

h_cols = sorted([c for c in tfpdf.columns if c.startswith("H")])
pers_cols = sorted([c for c in tfpdf.columns if c.startswith("pers_img")])
betti_cols = sorted([c for c in tfpdf.columns if c.startswith("betti")])
columns = h_cols + pers_cols + betti_cols
all_cols = columns
log(f"  TFP: {len(h_cols)}H + {len(pers_cols)}pers + {len(betti_cols)}betti = {len(all_cols)} features")

def extract(cols):
    rows = []
    for smi in smiles_list:
        if smi in tfpdf.index:
            rows.append(tfpdf.loc[smi, cols].values.astype(np.float32))
        else:
            rows.append(np.zeros(len(cols), dtype=np.float32))
    X = np.array(rows)
    cm = np.nanmean(X, axis=0); cm = np.where(np.isfinite(cm), cm, 0.0)
    inds = np.where(~np.isfinite(X))
    X[inds] = np.take(cm, inds[1])
    return X

X_tfp = extract(all_cols)

# Load ECFP4
log("  Computing ECFP4...")
X_ecfp = np.zeros((len(smiles_list), 2048), dtype=np.float32)
for i, smi in enumerate(smiles_list):
    mol = Chem.MolFromSmiles(smi)
    if mol:
        arr = np.zeros(2048, dtype=np.float32)
        ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        X_ecfp[i] = arr

# Subsample for RF-heavy analyses
N_SUB = 2000
rng = np.random.RandomState(42)
sub_idx = rng.choice(len(smiles_list), N_SUB, replace=False)
X_sub = X_tfp[sub_idx]; y_sub = y[sub_idx]

log(f"  Subsampled {N_SUB} for RF analyses")

# ═══════════════════════════════════════════════════════════════════
# 1. VARIANCE (full data, fast)
# ═══════════════════════════════════════════════════════════════════
log("1. VARIANCE (full data)")
var = np.var(X_tfp, axis=0)
log(f"  Constant (var<1e-10): {np.sum(var<1e-10)}/{len(var)}")
log(f"  Low-var (var<1e-6):   {np.sum(var<1e-6)}/{len(var)}")
low = np.argsort(var)[:5]
log(f"  Lowest var: {[f'{columns[i]}={var[i]:.2e}' for i in low]}")
high = np.argsort(var)[-5:][::-1]
log(f"  Highest var: {[f'{columns[i]}={var[i]:.4f}' for i in high]}")

# ═══════════════════════════════════════════════════════════════════
# 2. PCA (subsample 5000)
# ═══════════════════════════════════════════════════════════════════
log("2. PCA")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_tfp)
n_pca = min(5000, X_scaled.shape[0])
pca = PCA().fit(X_scaled[rng.choice(X_scaled.shape[0], n_pca, replace=False)])
cum = np.cumsum(pca.explained_variance_ratio_)
for t in [0.5, 0.75, 0.9, 0.95, 0.99]:
    n = int(np.searchsorted(cum, t) + 1)
    log(f"  {t*100:.0f}% variance: {n}/{X_tfp.shape[1]} comp")
log(f"  Eff. rank (>1%): {np.sum(pca.explained_variance_ratio_>0.01)}/{X_tfp.shape[1]}")

# ═══════════════════════════════════════════════════════════════════
# 3. FEATURE IMPORTANCE (1 fold, 200 trees, 2000 samples)
# ═══════════════════════════════════════════════════════════════════
log("3. FEATURE IMPORTANCE (1 fold, 2000 samples)")
scl = StandardScaler()
X_scl = scl.fit_transform(X_sub)
rf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1, random_state=42)
rf.fit(X_scl, y_sub)
fi = rf.feature_importances_
log(f"  OOB AUC: {roc_auc_score(y_sub, rf.predict_proba(X_scl)[:,1]):.4f}")
top = np.argsort(fi)[-15:][::-1]
log("  Top 15 features:")
for i in top:
    grp = columns[i].split("_")[0] if columns[i][0] in "Hb" else columns[i].split("_")[0] + "_" + columns[i].split("_")[1]
    log(f"    {columns[i]:28s}  imp={fi[i]:.6f}")
bot = np.argsort(fi)[:5]
log("  Bottom 5:")
for i in bot:
    log(f"    {columns[i]:28s}  imp={fi[i]:.6f}")

# Group contribution from feature importance
groups = {"H0":[], "H1":[], "H2":[], "pers_img":[], "betti":[]}
for i, c in enumerate(columns):
    for g in groups:
        if c.startswith(g):
            groups[g].append(fi[i])
log("  Group contribution (from FI):")
for g, v in groups.items():
    log(f"    {g:12s}  n={len(v):2d}  sum_imp={sum(v):.4f}  avg={np.mean(v):.6f}  pct={100*sum(v)/sum(fi):.1f}%")

# ═══════════════════════════════════════════════════════════════════
# 4. INTRA-TFP CORRELATION (full data, fast)
# ═══════════════════════════════════════════════════════════════════
log("4. INTRA-TFP CORRELATION (full data)")
corr = np.corrcoef(X_tfp, rowvar=False)
np.fill_diagonal(corr, 0)
log(f"  Mean |r|: {np.mean(np.abs(corr)):.4f}")
n_pairs = X_tfp.shape[1]*(X_tfp.shape[1]-1)//2
log(f"  |r|>0.8: {np.sum(np.abs(corr)>0.8)//2}/{n_pairs} pairs")
log(f"  |r|>0.95: {np.sum(np.abs(corr)>0.95)//2}/{n_pairs} pairs")
# Most correlated pairs
pairs = []
for i in range(X_tfp.shape[1]):
    for j in range(i+1, X_tfp.shape[1]):
        if abs(corr[i,j]) > 0.9:
            pairs.append((abs(corr[i,j]), columns[i], columns[j]))
pairs.sort(reverse=True)
log(f"  Top 10 correlated pairs (|r|>0.9):")
for r, c1, c2 in pairs[:10]:
    log(f"    {c1:28s} <-> {c2:28s}  r={r:.4f}")

# ═══════════════════════════════════════════════════════════════════
# 5. TFP-ECFP4 CORRELATION (subsample 2000, 256 random bits)
# ═══════════════════════════════════════════════════════════════════
log("5. TFP-ECFP4 CORRELATION (2000 mol, 256 random bits)")
X_tfp_s = X_tfp[sub_idx]; X_ecfp_s = X_ecfp[sub_idx]
bit_idx = rng.choice(2048, 256, replace=False)
X_ecfp_sm = X_ecfp_s[:, bit_idx]
max_corrs = []
for i in range(X_tfp_s.shape[1]):
    c = X_tfp_s[:, i]
    if np.std(c) < 1e-10:
        max_corrs.append(0.0); continue
    max_corrs.append(max(abs(np.corrcoef(c, X_ecfp_sm[:, b])[0,1]) for b in range(256)))
log(f"  Mean max |r| with ECFP4: {np.mean(max_corrs):.4f}")
log(f"  |r|>0.3: {np.sum(np.array(max_corrs)>0.3)}/{len(max_corrs)}")
log(f"  |r|>0.5: {np.sum(np.array(max_corrs)>0.5)}/{len(max_corrs)}")
log(f"  |r|<0.1: {np.sum(np.array(max_corrs)<0.1)}/{len(max_corrs)} (orthogonal)")
top_c = np.argsort(max_corrs)[-5:][::-1]
log("  Most TFP-ECFP4 correlated:")
for i in top_c:
    log(f"    {columns[i]:28s}  max|r|={max_corrs[i]:.4f}")

# ═══════════════════════════════════════════════════════════════════
# 6. GROUP RF PERFORMANCE (1 fold CV, 2000 samples)
# ═══════════════════════════════════════════════════════════════════
log("6. GROUP RF AUC (1 fold, 2000 samples)")
col2idx = {c:i for i,c in enumerate(all_cols)}
groups2 = {
    "H0 only": [c for c in all_cols if c.startswith("H0")],
    "H1 only": [c for c in all_cols if c.startswith("H1")],
    "H2 only": [c for c in all_cols if c.startswith("H2")],
    "H-stats(33)": [c for c in all_cols if c.startswith("H")],
    "pers_img(25)": [c for c in all_cols if c.startswith("pers_img")],
    "betti(20)": [c for c in all_cols if c.startswith("betti")],
    "pers+betti(45)": [c for c in all_cols if c.startswith("pers") or c.startswith("betti")],
    "ALL 78 TFP": all_cols,
    "ECFP4": [],  # special
}
# ECFP4 baseline
scl = StandardScaler()
X_ec = scl.fit_transform(X_ecfp[sub_idx])
rf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1, random_state=42)
rf.fit(X_ec, y_sub)
log(f"  ECFP4(2048)    n=2048  AUC={roc_auc_score(y_sub, rf.predict_proba(X_ec)[:,1]):.4f}")

for name, cols in groups2.items():
    if not cols:
        continue
    idxs = [col2idx[c] for c in cols]
    Xg = X_sub[:, idxs]
    scl = StandardScaler()
    Xg_s = scl.fit_transform(Xg)
    rf = RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1, random_state=42)
    rf.fit(Xg_s, y_sub)
    auc = roc_auc_score(y_sub, rf.predict_proba(Xg_s)[:,1])
    log(f"  {name:20s}  n={len(cols):3d}  AUC={auc:.4f}")

log(f"\n=== DONE in {time.perf_counter()-T0:.1f}s ===")
