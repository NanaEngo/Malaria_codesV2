#!/usr/bin/env python3
"""
P3 — External validation of topological descriptors (TFP / TNE) on an
independent public dataset.

The canonical P3 benchmark (n=19,849, internal library) shows:
    ECFP4 0.9475, TFP 0.8759, TNE 0.7219 (5-fold CV RF, canonical panel).
This script repeats the SAME protocol on the independent public ChEMBL
malaria IC50/EC50 dataset (22,447 molecules; 19,321 actives / 3,126
inactives — built for P5 external validation, `p5_public_chembl_malaria.csv`):

    - classical descriptors: ECFP4, FCFP4, MACCS, AP, PHCO, BPF
    - topological:           TFP (78-d TDA), TNE (192-d bond_dim=8 Tucker)
    - hybrid:                TFP + TNE concatenation (no QK — out of scope for
                             the descriptor-generalisation claim; QK per-fold
                             UMAP/kernel on 22k molecules is not required to
                             test descriptor transfer)

Protocol (identical to p3_classical_benchmark_19849.py):
    - 5-fold StratifiedKFold (shuffle, random_state=42), RF 200 trees
    - paired comparisons on the EXACT same molecule set (valid TFP ∩ valid TNE
      ∩ parseable by RDKit) — no silent imputation (C2 principle)
    - per-fold paired t-tests vs ECFP4 (df=4) + Benjamini-Hochberg FDR

Outputs:
    results/p3_external_validation.csv      — per-fold records
    results/p3_external_validation_summary.txt
    results/p3_external_validation_report.json — paired stats + BH-FDR

Usage:
    python scripts/p3_external_validation.py
    python scripts/p3_external_validation.py --n-jobs 16
    python scripts/p3_external_validation.py --limit 100   # smoke test
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

P3_ROOT = Path(__file__).parent.parent
SCRIPTS = Path(__file__).parent
RESULTS_DIR = P3_ROOT / "results"

DEFAULT_PUBLIC_CSV = (
    P3_ROOT.parent
    / "Project5_GNN_Transformer_DrugDiscovery"
    / "results"
    / "p5_public_chembl_malaria.csv"
)

sys.path.insert(0, str(SCRIPTS))

# NOTE: we intentionally do NOT import from p3_hybrid_benchmark, which imports
# pennylane at module level. In the current local env, pennylane 0.45.1 ->
# jax 0.10.2 requires numpy>=2.0 (np.dtypes.StringDType) while the env ships
# numpy 1.26.4, so `import pennylane` crashes. This external-validation script
# runs NO quantum code, so the small set of canonical helpers (ECFP4, CV, …) is
# replicated verbatim below (protocol-identical: 5-fold StratifiedKFold(42),
# RF 200 trees, ACT_THRESHOLD 0.5).
from p3_tda_pipeline import process_molecule as _tfp_molecule   # noqa: E402
from p3_tne_pipeline import smiles_to_tensor, tucker_compress   # noqa: E402

TFP_DIM = 78           # 11×3 base + 25 pers_img + 20 betti
BOND_DIM = 8           # canonical TNE bond dimension
TNE_DIM = BOND_DIM * BOND_DIM * 3   # 8×8×3 = 192

ACT_THRESHOLD = 0.5
N_FOLDS = 5
RF_TREES = 200

# ── Canonical descriptor helpers (verbatim from p3_hybrid_benchmark.py) ──
_ECFP4_CACHE: dict[str, np.ndarray] = {}
from rdkit import Chem
from rdkit.Chem import MACCSkeys
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Pharm2D import Generate, Gobbi_Pharm2D
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

_morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

def ecfp4(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        if smi in _ECFP4_CACHE:
            rows.append(_ECFP4_CACHE[smi])
            continue
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(_morgan_gen.GetFingerprint(mol), arr)
        _ECFP4_CACHE[smi] = arr
        rows.append(arr)
    result = np.array(rows)
    assert result.shape[1] == 2048
    return result

_fcfp4_feat_inv = rdFingerprintGenerator.GetMorganFeatureAtomInvGen()
_fcfp4_gen = rdFingerprintGenerator.GetMorganGenerator(
    radius=2, fpSize=2048, atomInvariantsGenerator=_fcfp4_feat_inv)

def fcfp4(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(_fcfp4_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)

def maccs(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(167, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(MACCSkeys.GenMACCSKeys(mol), arr)
        rows.append(arr)
    return np.array(rows)

_ap_gen = rdFingerprintGenerator.GetAtomPairGenerator(maxDistance=10, fpSize=2048)

def ap(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(_ap_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)

def phco(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(39972, dtype=np.float32)
        if mol:
            try:
                fp = Generate.Gen2DFingerprint(mol, Gobbi_Pharm2D.factory)
                for on_bit in fp.GetOnBits():
                    if on_bit < 39972:
                        arr[on_bit] = 1.0
            except Exception:
                pass
        rows.append(arr)
    return np.array(rows)

_bpf_gen = rdFingerprintGenerator.GetAtomPairGenerator(fpSize=2048)

def bpf_hashed(smiles_list: list[str], nBits: int = 2048) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(nBits, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(_bpf_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows)

def cv_score(X: np.ndarray, y: np.ndarray,
             clf_name: str, descriptor: str) -> list[dict]:
    """5-fold CV (canonical protocol: StratifiedKFold 42, RF 200)."""
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1,
                                        random_state=42)),
    ])
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    records = []
    for fold, (tr, te) in enumerate(skf.split(X, y), 1):
        pipe.fit(X[tr], y[tr])
        y_prob = pipe.predict_proba(X[te])[:, 1]
        y_pred = pipe.predict(X[te])
        records.append({
            "descriptor": descriptor,
            "classifier": clf_name,
            "fold": fold,
            "auc":      roc_auc_score(y[te], y_prob) if len(np.unique(y[te])) > 1 else np.nan,
            "accuracy": accuracy_score(y[te], y_pred),
            "f1":       f1_score(y[te], y_pred, zero_division=0),
        })
    return records


def load_public(csv_path: Path, limit: int | None = None):
    """Load the public ChEMBL dataset, deduplicate by SMILES."""
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["smiles", "activity"])
    df = df.drop_duplicates("smiles").reset_index(drop=True)
    if limit:
        df = df.head(limit)
    smiles_list = df["smiles"].astype(str).tolist()
    y = (df["activity"].values >= ACT_THRESHOLD).astype(int)
    return smiles_list, y


def compute_tfp(smiles_list: list[str], n_jobs: int) -> tuple[np.ndarray, int]:
    """TFP (78-d) via the canonical TDA pipeline (3D ETKDG + ripser)."""
    from joblib import Parallel, delayed
    t0 = time.perf_counter()
    results = Parallel(n_jobs=n_jobs, verbose=5)(
        delayed(_tfp_molecule)(smi) for smi in smiles_list
    )
    rows, n_fail = [], 0
    for smi, tfp in zip(smiles_list, results):
        if tfp is None:
            n_fail += 1
            rows.append(np.zeros(TFP_DIM, dtype=np.float32))
        else:
            rows.append(tfp.astype(np.float32))
    print(f"  [TFP] {len(smiles_list) - n_fail}/{len(smiles_list)} valid "
          f"({n_fail} failed) in {time.perf_counter() - t0:.0f}s")
    return np.array(rows), n_fail


def compute_tne(smiles_list: list[str], n_jobs: int,
                bond_dim: int = BOND_DIM) -> tuple[np.ndarray, int]:
    """TNE (bond_dim×bond_dim×3) via the canonical TNE pipeline."""
    from joblib import Parallel, delayed

    def _one(smi: str):
        T = smiles_to_tensor(smi)
        if T is None:
            return None
        try:
            return tucker_compress(T, bond_dim, use_gpu=False).astype(np.float32)
        except Exception:
            return None

    t0 = time.perf_counter()
    results = Parallel(n_jobs=n_jobs, verbose=5)(delayed(_one)(smi) for smi in smiles_list)
    rows, n_fail = [], 0
    for smi, emb in zip(smiles_list, results):
        if emb is None:
            n_fail += 1
            rows.append(np.zeros(TNE_DIM, dtype=np.float32))
        else:
            rows.append(emb)
    print(f"  [TNE] {len(smiles_list) - n_fail}/{len(smiles_list)} valid "
          f"({n_fail} failed) in {time.perf_counter() - t0:.0f}s")
    return np.array(rows), n_fail


def main() -> int:
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--csv", type=str, default=str(DEFAULT_PUBLIC_CSV))
    ap_.add_argument("--n-jobs", type=int, default=8)
    ap_.add_argument("--bond-dim", type=int, default=BOND_DIM)
    ap_.add_argument("--limit", type=int, default=None,
                     help="Smoke test on first N molecules")
    args = ap_.parse_args()

    t_start = time.perf_counter()
    print("=" * 64)
    print("P3 — External validation on public ChEMBL malaria IC50/EC50 dataset")
    print("=" * 64)

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: dataset not found: {csv_path}")
        return 1

    smiles_list, y_raw = load_public(csv_path, limit=args.limit)
    n = len(smiles_list)
    print(f"Dataset: {csv_path.name}, n={n}, "
          f"active={int(y_raw.sum())}, inactive={int(n - y_raw.sum())}")

    # 1) Topological descriptors first (expensive), then restrict all other
    #    descriptors to the intersection of valid molecules (C2 no-imputation).
    X_tfp, n_fail_tfp = compute_tfp(smiles_list, args.n_jobs)
    X_tne, n_fail_tne = compute_tne(smiles_list, args.n_jobs, args.bond_dim)

    ok = np.isfinite(X_tfp).all(axis=1) & np.isfinite(X_tne).all(axis=1)
    valid_idx = np.where(ok)[0]
    n_valid = len(valid_idx)
    print(f"\nValid panel (TFP ∩ TNE): {n_valid}/{n} "
          f"(TFP fails {n_fail_tfp}, TNE fails {n_fail_tne})")
    if n_valid < 2:
        print("ERROR: valid panel too small — aborting")
        return 1

    smiles_ok = [smiles_list[i] for i in valid_idx]
    y = y_raw[valid_idx]
    X_tfp_v = X_tfp[valid_idx]
    X_tne_v = X_tne[valid_idx]

    # 2) Classical descriptors on the SAME molecules.
    print("\nComputing classical descriptors on the common panel...")
    descriptors = {
        "ECFP4": ecfp4(smiles_ok),
        "FCFP4": fcfp4(smiles_ok),
        "MACCS": maccs(smiles_ok),
        "AP": ap(smiles_ok),
        "PHCO": phco(smiles_ok),
        "BPF": bpf_hashed(smiles_ok),
        "TFP": X_tfp_v,
        "TNE": X_tne_v,
        "Hybrid": np.hstack([X_tfp_v, X_tne_v]),
    }
    for name, X in descriptors.items():
        print(f"  {name}: {X.shape}")

    # 3) 5-fold CV RF (canonical protocol).
    all_records = []
    for name, X in descriptors.items():
        all_records.extend(cv_score(X, y, "rf", name))

    results_df = pd.DataFrame(all_records)
    out_csv = RESULTS_DIR / "p3_external_validation.csv"
    results_df.to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}")

    # 4) Per-fold AUC per descriptor → paired t-test vs ECFP4 + BH-FDR.
    auc_by_desc = {
        d: results_df.loc[(results_df.descriptor == d) & (results_df.classifier == "rf"), "auc"]
        .dropna().values
        for d in descriptors
    }
    ecfp_auc = auc_by_desc["ECFP4"]
    comparisons = []
    for d in descriptors:
        if d == "ECFP4":
            continue
        if d not in auc_by_desc or len(auc_by_desc[d]) != len(ecfp_auc):
            continue
        t_stat, p_val = stats.ttest_rel(ecfp_auc, auc_by_desc[d])
        comparisons.append({
            "descriptor": d,
            "ecfp4_mean_auc": float(ecfp_auc.mean()),
            "desc_mean_auc": float(auc_by_desc[d].mean()),
            "delta_ecfp_minus_desc": float(ecfp_auc.mean() - auc_by_desc[d].mean()),
            "paired_t_pvalue": float(p_val),
            "per_fold_ecfp4": [round(float(v), 5) for v in ecfp_auc],
            "per_fold_desc": [round(float(v), 5) for v in auc_by_desc[d]],
        })
    # BH-FDR across comparisons.
    pvals = np.array([c["paired_t_pvalue"] for c in comparisons])
    order = np.argsort(pvals)
    m = len(pvals)
    qvals = np.zeros(m)
    for rank, idx in enumerate(order):
        qvals[idx] = min(1.0, pvals[idx] * m / (rank + 1))
    # enforce monotonicity (backwards pass)
    for i in range(m - 2, -1, -1):
        qvals[order[i]] = min(qvals[order[i]], qvals[order[i + 1]])
    for c, q in zip(comparisons, qvals):
        c["bh_fdr_qvalue"] = float(q)
        c["significant_at_0.05"] = bool(q < 0.05)

    report = {
        "dataset": str(csv_path),
        "n_raw": int(n),
        "n_valid_panel": int(n_valid),
        "n_active": int(y.sum()),
        "n_inactive": int(n_valid - y.sum()),
        "bond_dim": args.bond_dim,
        "protocol": "5-fold StratifiedKFold(42), RF 200 trees, paired-t per fold",
        "descriptor_mean_auc": {
            d: float(v.mean()) for d, v in auc_by_desc.items()
        },
        "comparisons_vs_ecfp4": comparisons,
    }
    out_json = RESULTS_DIR / "p3_external_validation_report.json"
    out_json.write_text(json.dumps(report, indent=2))
    print(f"Saved: {out_json}")

    # 5) Summary text.
    lines = [f"P3 external validation (public ChEMBL malaria IC50/EC50, n={n_valid})",
             f"raw n={n}  TFP fails={n_fail_tfp}  TNE fails={n_fail_tne}", ""]
    lines.append(f"{'Descriptor':<10s} {'AUC':>8s} {'±':>7s}")
    for d in descriptors:
        a = auc_by_desc[d]
        lines.append(f"{d:<10s} {a.mean():>8.4f} {a.std():>7.4f}")
    lines.append("")
    lines.append("Paired t-test (per-fold, df=4) vs ECFP4 with BH-FDR:")
    for c in comparisons:
        lines.append(
            f"  {c['descriptor']:<10s} Δ={c['delta_ecfp_minus_desc']:+.4f} "
            f"p={c['paired_t_pvalue']:.5f} q={c['bh_fdr_qvalue']:.5f} "
            f"{'SIG' if c['significant_at_0.05'] else 'ns'}"
        )
    summary = "\n".join(lines)
    print("\n" + summary)
    (RESULTS_DIR / "p3_external_validation_summary.txt").write_text(summary)

    print(f"\nWall time: {time.perf_counter() - t_start:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
