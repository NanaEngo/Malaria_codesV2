#!/usr/bin/env python
"""S2/S3 refinement: fair-fusion battery and a stabilised scaffold-split estimate.

S2 (P-S2-A). The earlier finding that ECFP4+TFP+TNE underperforms ECFP4 rests on
naive concatenation: 270 dense features appended to 2048 sparse bits changes what
max_features samples at each RF node, so the drop may be dilution rather than an
absence of complementary information. Four fusions are therefore compared against
ECFP4 on identical folds:

  stacked        out-of-fold probabilities from a per-block RF into a logistic
                 meta-learner -- the standard fair test, immune to dilution
  block-weighted each block scaled to equal total variance before concatenation
  top-k          per-block RF-importance selection before concatenation
  ECFP4+TFP      isolates whether TNE drives the drop

S3 (P-S3-A). GroupKFold is deterministic and unstratified; one partition gave
scaffold-split SDs 3-9x the random-split ones, with the largest scaffold (8.4% of
the library) dominating whichever fold held it. We repeat scaffold-grouped splits
10 times with GroupShuffleSplit and report mean with a t-based 95% CI.

Also recomputes the scaffold count with generic (atom-type-stripped) Murcko
scaffolds as a sanity check on the 629 figure. Overlap with the 850 seed scaffolds
is NOT computed: the seed set lives in the companion Paper-1 project, not here.

Output: results/p3_s2s3_refine.csv + .txt
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, StratifiedKFold

RDLogger.DisableLog("rdApp.*")

TFP12 = [f"H{d}_{s}" for d in (0, 1, 2)
         for s in ("entropy", "count", "max_pers", "mean_pers")]
SEED = 42


def ecfp4_matrix(smiles: list[str], n_bits: int = 2048) -> np.ndarray:
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    out = np.zeros((len(smiles), n_bits), dtype=np.uint8)
    for i, s in enumerate(smiles):
        mol = Chem.MolFromSmiles(s)
        if mol is not None:
            out[i] = gen.GetFingerprintAsNumPy(mol).astype(np.uint8)
    return out


def murcko(smiles: list[str], generic: bool = False) -> list[str]:
    cores = []
    for s in smiles:
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            cores.append("")
            continue
        core = MurckoScaffold.GetScaffoldForMol(mol)
        if generic and core.GetNumAtoms():
            try:
                core = MurckoScaffold.MakeScaffoldGeneric(core)
            except Exception:
                pass
        cores.append(Chem.MolToSmiles(core))
    return cores


def rf(seed: int = SEED) -> RandomForestClassifier:
    return RandomForestClassifier(n_estimators=200, random_state=seed, n_jobs=-1)


def stacked_auc(blocks: list[np.ndarray], y: np.ndarray,
                tr: np.ndarray, te: np.ndarray, inner: int = 3) -> float:
    """Out-of-fold stacking: per-block RF -> logistic meta-learner."""
    meta_tr = np.zeros((len(tr), len(blocks)))
    inner_cv = StratifiedKFold(n_splits=inner, shuffle=True, random_state=SEED)
    for b, X in enumerate(blocks):
        for itr, ite in inner_cv.split(X[tr], y[tr]):
            m = rf().fit(X[tr][itr], y[tr][itr])
            meta_tr[ite, b] = m.predict_proba(X[tr][ite])[:, 1]
    meta_te = np.column_stack(
        [rf().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1] for X in blocks])
    meta = LogisticRegression(max_iter=1000).fit(meta_tr, y[tr])
    return roc_auc_score(y[te], meta.predict_proba(meta_te)[:, 1])


def block_weighted(blocks: list[np.ndarray]) -> np.ndarray:
    """Scale each block to unit total variance so no block dominates by width."""
    scaled = []
    for X in blocks:
        Xf = X.astype(float)
        v = Xf.var(axis=0).sum()
        scaled.append(Xf / np.sqrt(v) if v > 0 else Xf)
    return np.hstack(scaled)


def topk_fusion(blocks: list[np.ndarray], y: np.ndarray,
                tr: np.ndarray, k: int = 50) -> np.ndarray:
    """Per-block RF-importance selection, fitted on the training fold only."""
    keep = []
    for X in blocks:
        if X.shape[1] <= k:
            keep.append(X)
            continue
        imp = rf().fit(X[tr], y[tr]).feature_importances_
        keep.append(X[:, np.argsort(imp)[-k:]])
    return np.hstack(keep)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tda-csv", default="results/p3_tda_fingerprints.csv")
    ap.add_argument("--tne-csv", default="results/p3_tne_embeddings.csv")
    ap.add_argument("--labels-csv", default="results/p3_labels_production.csv")
    ap.add_argument("--out-csv", default="results/p3_s2s3_refine.csv")
    ap.add_argument("--out-txt", default="results/p3_s2s3_refine.txt")
    ap.add_argument("--repeats", type=int, default=10)
    args = ap.parse_args()

    tda = pd.read_csv(args.tda_csv)
    tne = pd.read_csv(args.tne_csv)
    lab = pd.read_csv(args.labels_csv)
    df = lab.merge(tda, on="smiles").merge(tne, on="smiles").dropna()
    smiles = df["smiles"].tolist()
    y = df["activity"].to_numpy(dtype=int)

    h = [c for c in tda.columns if c.startswith("H")]
    pi = [c for c in tda.columns if c.startswith("pers_img_")]
    bt = [c for c in tda.columns if c.startswith("betti_")]
    tn = [c for c in tne.columns if c.startswith("tne_")]

    X_ecfp = ecfp4_matrix(smiles)
    X_tfp78 = df[h + pi + bt].to_numpy(float)
    X_tne = df[tn].to_numpy(float)
    blocks = [X_ecfp, X_tfp78, X_tne]
    print(f"Panel {len(df)} | ECFP4 {X_ecfp.shape[1]} | "
          f"TFP78 {X_tfp78.shape[1]} | TNE {X_tne.shape[1]}")

    rows: list[dict] = []

    # ---------- S2: fair-fusion battery, random 5-fold ----------
    print("\nS2 fair-fusion battery (random 5-fold)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    X_bw = block_weighted(blocks)
    X_naive = np.hstack([X_ecfp, X_tfp78, X_tne])
    X_et = np.hstack([X_ecfp, X_tfp78])
    for fold, (tr, te) in enumerate(cv.split(X_ecfp, y), 1):
        variants = {
            "ECFP4": X_ecfp,
            "naive concat": X_naive,
            "block-weighted": X_bw,
            "top-k per block": topk_fusion(blocks, y, tr),
            "ECFP4+TFP only": X_et,
        }
        for name, X in variants.items():
            a = roc_auc_score(y[te], rf().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1])
            rows.append({"analysis": "S2", "descriptor": name, "split": "random",
                         "rep": fold, "auc": a})
        rows.append({"analysis": "S2", "descriptor": "stacked", "split": "random",
                     "rep": fold, "auc": stacked_auc(blocks, y, tr, te)})
        print(f"  fold {fold} done")

    # ---------- S3: repeated scaffold splits ----------
    print("\nS3 repeated scaffold splits...")
    cores = murcko(smiles)
    uniq = {c: i for i, c in enumerate(dict.fromkeys(cores))}
    groups = np.array([uniq[c] for c in cores])
    n_scaf = len(uniq)
    n_gen = len(set(murcko(smiles, generic=True)))
    print(f"  Murcko scaffolds: {n_scaf} | generic: {n_gen}")

    s3 = {"ECFP4": X_ecfp, "TFP-12": df[TFP12].to_numpy(float),
          "TFP-78": X_tfp78, "TNE": X_tne, "ECFP4+TFP78+TNE": X_naive}
    gss = GroupShuffleSplit(n_splits=args.repeats, test_size=0.2, random_state=SEED)
    for rep, (tr, te) in enumerate(gss.split(X_ecfp, y, groups), 1):
        for name, X in s3.items():
            a = roc_auc_score(y[te], rf().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1])
            rows.append({"analysis": "S3", "descriptor": name, "split": "scaffold",
                         "rep": rep, "auc": a})
        print(f"  repeat {rep}/{args.repeats} done")

    out = pd.DataFrame(rows)
    out.to_csv(args.out_csv, index=False)

    def vals(analysis: str, name: str) -> np.ndarray:
        s = out[(out.analysis == analysis) & (out.descriptor == name)].sort_values("rep")
        return s.auc.to_numpy()

    def ci95(a: np.ndarray) -> tuple[float, float]:
        m, sd, n = a.mean(), a.std(ddof=1), len(a)
        hw = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
        return m - hw, m + hw

    L = ["=" * 84, "P3 S2/S3 REFINEMENT", "=" * 84,
         f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
         f"Panel: {len(df)} molecules | RF-200, seed {SEED}", "",
         "S2 -- fair-fusion battery vs ECFP4 (random 5-fold, paired t)", "-" * 84,
         f"{'fusion':<22}{'AUC':>9}{'SD':>9}{'delta':>9}{'t':>9}{'p':>11}"]
    base = vals("S2", "ECFP4")
    L.append(f"{'ECFP4 (baseline)':<22}{base.mean():>9.4f}{base.std(ddof=1):>9.4f}"
             f"{'--':>9}{'--':>9}{'--':>11}")
    for name in ("stacked", "block-weighted", "top-k per block",
                 "ECFP4+TFP only", "naive concat"):
        a = vals("S2", name)
        t, p = stats.ttest_rel(a, base)
        L.append(f"{name:<22}{a.mean():>9.4f}{a.std(ddof=1):>9.4f}"
                 f"{a.mean() - base.mean():>+9.4f}{t:>9.3f}{p:>11.4g}")
    L += ["-" * 84, "",
          f"S3 -- repeated scaffold splits ({args.repeats}x GroupShuffleSplit, 20% held out)",
          f"Murcko scaffolds: {n_scaf} | generic Murcko scaffolds: {n_gen}",
          "Seed-scaffold overlap NOT computed: seed set is in the companion Paper-1 project.",
          "-" * 84,
          f"{'descriptor':<22}{'mean AUC':>10}{'SD':>9}{'95% CI':>22}"]
    for name in s3:
        a = vals("S3", name)
        lo, hi = ci95(a)
        L.append(f"{name:<22}{a.mean():>10.4f}{a.std(ddof=1):>9.4f}"
                 f"{f'[{lo:.4f}, {hi:.4f}]':>22}")
    L += ["-" * 84, ""]

    txt = "\n".join(L)
    with open(args.out_txt, "w") as fh:
        fh.write(txt + "\n")
    print("\n" + txt)


if __name__ == "__main__":
    main()
