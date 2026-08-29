#!/usr/bin/env python
"""S1-S3: TFP definition, ECFP4 complementarity, and scaffold-aware evaluation.

Three questions the manuscript leaves open, answered in one run on the canonical
panel:

S1  Which TFP is actually benchmarked? The Methods define a 12-dimensional vector
    (4 summary statistics x 3 homology dimensions). p3_hybrid_benchmark.py loads
    every column with the "H" prefix (33 features) and, with --tfp-enriched
    (default True), appends persistence images (25) and Betti curves (20) for 78.
    We evaluate all three so the published number can be attributed correctly.

S2  Are the quantum-inspired descriptors complementary to ECFP4? The manuscript
    asserts this repeatedly; the concatenation that tests it was never run. The
    hybrid contains no ECFP4. We evaluate ECFP4 + TFP + TNE against ECFP4 alone
    with a paired test. (QKS is excluded: no precomputed quantum-kernel feature
    matrix exists and recomputing it is O(N^2) on 19,836 molecules.)

S3  Does the ranking survive a scaffold-aware split? The library retains 69.3% of
    seed scaffolds after STONED-SELFIES expansion, so random K-fold splits
    analogue series across train and test. We repeat every descriptor under
    GroupKFold on Bemis-Murcko scaffolds and report the drop.

Output: results/p3_s1s3_benchmark.csv + .txt
"""
from __future__ import annotations

import argparse
from collections import Counter

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold

RDLogger.DisableLog("rdApp.*")

# The 12 features the Methods actually define: 4 statistics x 3 homology dims.
TFP12 = [f"H{d}_{s}" for d in (0, 1, 2)
         for s in ("entropy", "count", "max_pers", "mean_pers")]


def ecfp4_matrix(smiles: list[str], n_bits: int = 2048) -> np.ndarray:
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=n_bits)
    out = np.zeros((len(smiles), n_bits), dtype=np.uint8)
    for i, s in enumerate(smiles):
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            continue
        out[i] = gen.GetFingerprintAsNumPy(mol).astype(np.uint8)
    return out


def scaffold_groups(smiles: list[str]) -> np.ndarray:
    idx: dict[str, int] = {}
    groups = []
    for s in smiles:
        mol = Chem.MolFromSmiles(s)
        core = "" if mol is None else MurckoScaffold.MurckoScaffoldSmiles(mol=mol)
        groups.append(idx.setdefault(core, len(idx)))
    return np.asarray(groups)


def evaluate(X: np.ndarray, y: np.ndarray, groups: np.ndarray, split: str,
             seed: int = 42, n_splits: int = 5) -> list[float]:
    if split == "random":
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        folds = cv.split(X, y)
    else:
        folds = GroupKFold(n_splits=n_splits).split(X, y, groups)
    aucs = []
    for tr, te in folds:
        clf = RandomForestClassifier(n_estimators=200, random_state=seed, n_jobs=-1)
        clf.fit(X[tr], y[tr])
        aucs.append(roc_auc_score(y[te], clf.predict_proba(X[te])[:, 1]))
    return aucs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tda-csv", default="results/p3_tda_fingerprints.csv")
    ap.add_argument("--tne-csv", default="results/p3_tne_embeddings.csv")
    ap.add_argument("--labels-csv", default="results/p3_labels_production.csv")
    ap.add_argument("--out-csv", default="results/p3_s1s3_benchmark.csv")
    ap.add_argument("--out-txt", default="results/p3_s1s3_benchmark.txt")
    args = ap.parse_args()

    tda = pd.read_csv(args.tda_csv)
    tne = pd.read_csv(args.tne_csv)
    lab = pd.read_csv(args.labels_csv)

    df = lab.merge(tda, on="smiles").merge(tne, on="smiles").dropna()
    smiles = df["smiles"].tolist()
    y = df["activity"].to_numpy(dtype=int)
    print(f"Canonical panel: {len(df)} molecules, "
          f"{y.sum()} active / {len(y) - y.sum()} inactive")

    h_cols = [c for c in tda.columns if c.startswith("H")]
    pi_cols = [c for c in tda.columns if c.startswith("pers_img_")]
    bt_cols = [c for c in tda.columns if c.startswith("betti_")]
    tne_cols = [c for c in tne.columns if c.startswith("tne_")]

    X_tfp12 = df[TFP12].to_numpy(float)
    X_tfp33 = df[h_cols].to_numpy(float)
    X_tfp78 = df[h_cols + pi_cols + bt_cols].to_numpy(float)
    X_tne = df[tne_cols].to_numpy(float)
    print("Building ECFP4...")
    X_ecfp = ecfp4_matrix(smiles)

    descriptors = {
        "ECFP4": X_ecfp,
        "TFP-12 (as defined in Methods)": X_tfp12,
        "TFP-33 (H-prefix, --no-tfp-enriched)": X_tfp33,
        "TFP-78 (enriched, benchmarked)": X_tfp78,
        "TNE": X_tne,
        "ECFP4+TFP78+TNE": np.hstack([X_ecfp, X_tfp78, X_tne]),
    }

    print("Assigning Bemis-Murcko scaffolds...")
    groups = scaffold_groups(smiles)
    n_scaf = len(set(groups.tolist()))
    top = Counter(groups.tolist()).most_common(1)[0][1]
    print(f"  {n_scaf} distinct scaffolds; largest holds {top} molecules "
          f"({100 * top / len(groups):.1f}%)")

    rows = []
    for split in ("random", "scaffold"):
        for name, X in descriptors.items():
            aucs = evaluate(X, y, groups, split)
            for f, a in enumerate(aucs, 1):
                rows.append({"descriptor": name, "split": split, "fold": f,
                             "auc": a, "n_features": X.shape[1]})
            print(f"  [{split:>8}] {name:<38} "
                  f"{np.mean(aucs):.4f} +/- {np.std(aucs, ddof=1):.4f}")

    out = pd.DataFrame(rows)
    out.to_csv(args.out_csv, index=False)

    def get(name: str, split: str) -> np.ndarray:
        s = out[(out.descriptor == name) & (out.split == split)].sort_values("fold")
        return s.auc.to_numpy()

    lines = ["=" * 87, "P3 S1-S3 BENCHMARK", "=" * 87,
             f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
             f"Panel: {len(df)} molecules | scaffolds: {n_scaf} | RF-200, 5-fold, seed 42",
             "",
             f"{'descriptor':<38}{'dim':>5}{'random':>18}{'scaffold':>18}{'drop':>8}",
             "-" * 87]
    for name, X in descriptors.items():
        r, s = get(name, "random"), get(name, "scaffold")
        lines.append(f"{name:<38}{X.shape[1]:>5}"
                     f"{np.mean(r):>11.4f}+{np.std(r, ddof=1):<6.4f}"
                     f"{np.mean(s):>11.4f}+{np.std(s, ddof=1):<6.4f}"
                     f"{np.mean(s) - np.mean(r):>8.4f}")
    lines += ["-" * 87, "",
              "S2 -- complementarity: ECFP4+TFP78+TNE vs ECFP4 (paired t, 5 folds)"]
    for split in ("random", "scaffold"):
        a, b = get("ECFP4+TFP78+TNE", split), get("ECFP4", split)
        t, p = stats.ttest_rel(a, b)
        lines.append(f"  {split:>8}: delta = {np.mean(a) - np.mean(b):+.4f}  "
                     f"t = {t:+.3f}  p = {p:.4g}")
    lines += ["", "S1 -- TFP definition: which vector produces the published 0.876?"]
    for name in ("TFP-12 (as defined in Methods)",
                 "TFP-33 (H-prefix, --no-tfp-enriched)",
                 "TFP-78 (enriched, benchmarked)"):
        lines.append(f"  {name:<38} random AUC = {np.mean(get(name, 'random')):.4f}")
    lines += ["", "S3 -- leakage: mean AUC drop from random to scaffold split"]
    drops = [np.mean(get(n, "scaffold")) - np.mean(get(n, "random")) for n in descriptors]
    lines.append(f"  mean drop across {len(descriptors)} descriptors = {np.mean(drops):+.4f}")
    lines.append("")

    txt = "\n".join(lines)
    with open(args.out_txt, "w") as fh:
        fh.write(txt + "\n")
    print("\n" + txt)


if __name__ == "__main__":
    main()
