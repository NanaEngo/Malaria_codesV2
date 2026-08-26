#!/usr/bin/env python3
"""P6 Phase 1 (v2) -- drug_id -> compound -> SMILES via PRISM Repurposing viability.

The Kaggle LISH-MoA c- features ARE PRISM pooled-line viability data (the official
LISHarvard/moa_challenge repo ships the PRISM<->kaggle cell_mapping), so compound
identity is recovered by correlating each drug's kaggle viability profile against
PRISM Repurposing primary-screen profiles. Expression-based matching against
GSE92742 (p6_phase1_map.py) failed: cross-campaign L1000 correlations sit at the
permutation noise floor (max r=0.307 vs null q9999=0.325).

Stages (run in order):
    prepare  Cache the kaggle drug x cell-line viability matrix and the PRISM
             compound x cell-line LFC matrix restricted to shared CCLE lines.
    match    Max-correlate each kaggle drug against every PRISM compound;
             calibrate threshold on cell-line-permuted controls.
    smiles   Merge canonical SMILES/MoA already present in PRISM treatment info.
    report   Audit summary (coverage, collisions, invalid SMILES) printed as JSON.

Inputs (data/raw/prism/, figshare doi:10.6084/m9.figshare.11384241 files
20237709/20237715/20237718) and ~/lish_moa_data/raw_training/.

Usage (HPC, env qom):
    python p6_phase1_prism.py prepare
    python p6_phase1_prism.py match
    python p6_phase1_prism.py smiles
    python p6_phase1_prism.py report
    python p6_phase1_prism.py selftest

Outputs in data/mappings/: drugid_to_pert_v2.csv, drugid_to_smiles_v2.csv,
prism_threshold.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from p6_phase1_map import _cnorm, _top2  # noqa: E402

RAW = HERE.parent / "data" / "raw"
MAPS = HERE.parent / "data" / "mappings"

TRAIN_DIR = Path("~/lish_moa_data/raw_training").expanduser()
PRISM_LFC = RAW / "prism" / "primary-screen-replicate-collapsed-logfold-change.csv"
PRISM_TRT = RAW / "prism" / "primary-screen-replicate-collapsed-treatment-info.csv"
PRISM_CELL = RAW / "prism" / "primary-screen-cell-line-info.csv"

KAGGLE_C_NPZ = MAPS / "kaggle_c_matrix.npz"
PRISM_M_NPY = MAPS / "prism_compound_matrix.npy"
MATCH_OUT = MAPS / "drugid_to_pert_v2.csv"


def _ensure_dirs() -> None:
    MAPS.mkdir(parents=True, exist_ok=True)


def _norm_ccle(name: str) -> str:
    """Uppercase alnum+underscore key used to intersect CCLE line names."""
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(name).upper())


def cmd_prepare(_args: argparse.Namespace) -> None:
    """Build both viability matrices restricted to shared cell lines."""
    _ensure_dirs()
    feats = pd.read_csv(TRAIN_DIR / "train_features.csv")
    drugs = pd.read_csv(TRAIN_DIR / "train_drug.csv")
    ccols = [c for c in feats.columns if c.startswith("c-")]
    mg = feats[["sig_id"] + ccols].merge(drugs, on="sig_id", how="inner")
    kg = mg.groupby("drug_id")[ccols].mean()
    kg.columns = [_norm_ccle(c.split("-", 2)[2]) for c in ccols]  # c-7-KYSE70_OESOPHAGUS
    print(f"[prepare] kaggle drugs={len(kg)} c-lines={kg.shape[1]}")

    trt = pd.read_csv(PRISM_TRT)
    trt = trt.dropna(subset=["broad_id"])
    lfc = pd.read_csv(PRISM_LFC, index_col=0)
    cell = pd.read_csv(PRISM_CELL, index_col="row_name")
    # matrix rows are cell-line row_names; annotate with CCLE keys
    keys = {r: _norm_ccle(cell.loc[r, "ccle_name"]) if r in cell.index else ""
            for r in lfc.index}
    lfc.index = pd.Index([keys.get(r, str(r)) for r in lfc.index], name=None)

    shared = [c for c in kg.columns if c in set(lfc.index)]
    print(f"[prepare] prism compounds={lfc.shape[1]} lines={lfc.shape[0]} "
          f"shared-lines={len(shared)}")

    K = kg[shared]
    # collapse PRISM doses: median LFC per compound over its column_name entries
    comp_of_col = dict(zip(trt["column_name"], trt["broad_id"]))
    lfc_shared = lfc.loc[shared]
    cols = [c for c in lfc_shared.columns if c in comp_of_col]
    P = lfc_shared[cols].T.groupby([comp_of_col[c] for c in cols]).median()
    P = P.loc[:, shared]  # align line order with K
    print(f"[prepare] unique prism compounds={len(P)}")

    np.savez_compressed(KAGGLE_C_NPZ, matrix=K.to_numpy(dtype=np.float32),
                        drug_id=np.array(K.index, dtype=str),
                        cell_lines=np.array(shared, dtype=str))
    np.save(PRISM_M_NPY, P.to_numpy(dtype=np.float32))
    np.save(MAPS / "prism_compound_ids.npy", np.array(P.index, dtype=str))
    print(f"[prepare] wrote {KAGGLE_C_NPZ} shape={K.shape}; "
          f"{PRISM_M_NPY} shape={P.shape}")


def cmd_match(args: argparse.Namespace) -> None:
    """Max-correlate kaggle drug viability vs PRISM compound viability."""
    _ensure_dirs()
    cache = np.load(KAGGLE_C_NPZ, allow_pickle=True)
    K, drug_ids = cache["matrix"], cache["drug_id"]
    P = np.load(PRISM_M_NPY)
    comp_ids = np.load(MAPS / "prism_compound_ids.npy", allow_pickle=True)

    Kn, Bn = _cnorm(K), _cnorm(P)
    # ponytail: centered scale => 0 is neutral for missing cell-line assays;
    # NaN would poison np.argmax inside _top2
    Bn[~np.isfinite(Bn)] = 0.0
    Kn[~np.isfinite(Kn)] = 0.0
    lbl = np.arange(len(comp_ids))          # one distinct label per compound
    best_r, best_j, sec_r = _top2(Kn, Bn, lbl, chunk=args.chunk)

    rng = np.random.default_rng(42)
    Kp = np.stack([K[i, rng.permutation(K.shape[1])] for i in range(len(K))])
    null_best, _, _ = _top2(_cnorm(Kp), Bn, lbl, chunk=args.chunk)
    thresh = float(np.quantile(null_best, args.q))

    trt = pd.read_csv(PRISM_TRT).dropna(subset=["broad_id"])
    first = trt.drop_duplicates("broad_id").set_index("broad_id")
    hit = first.loc[comp_ids[best_j]]
    out = pd.DataFrame({
        "drug_id": drug_ids,
        "matched_broad_id": comp_ids[best_j],
        "matched_pert_iname": hit["name"].to_numpy(),
        "matched_moa": hit["moa"].to_numpy(),
        "match_score": best_r,
        "second_score": sec_r,
        "margin": best_r - sec_r,
        "above_threshold": best_r > thresh,
    })
    out.to_csv(MATCH_OUT, index=False)
    (MAPS / "prism_threshold.json").write_text(json.dumps(
        {"threshold_q_null": thresh, "q": args.q,
         "n_above": int(out.above_threshold.sum()), "n_total": len(out)}, indent=2))
    print(f"[match] threshold(null q={args.q})={thresh:.4f}; "
          f"above={int(out.above_threshold.sum())}/{len(out)}; "
          f"score med={np.median(best_r):.3f} max={best_r.max():.3f} -> {MATCH_OUT}")


def cmd_smiles(_args: argparse.Namespace) -> None:
    """Attach SMILES (already a PRISM treatment-info column) and write final v2."""
    _ensure_dirs()
    m = pd.read_csv(MATCH_OUT)
    trt = pd.read_csv(PRISM_TRT).dropna(subset=["broad_id"])
    sm = trt.drop_duplicates("broad_id").set_index("broad_id")["smiles"]
    m["canonical_smiles"] = m["matched_broad_id"].map(sm)
    m["smiles_source"] = np.where(m["canonical_smiles"].notna(), "prism_treatment_info", "")
    cols = ["drug_id", "matched_broad_id", "matched_pert_iname", "matched_moa",
            "match_score", "second_score", "margin", "above_threshold",
            "canonical_smiles", "smiles_source"]
    m[cols].to_csv(MAPS / "drugid_to_smiles_v2.csv", index=False)
    cov = m["canonical_smiles"].notna().mean()
    print(f"[smiles] coverage={cov:.3f} -> {MAPS / 'drugid_to_smiles_v2.csv'}")


def cmd_report(_args: argparse.Namespace) -> None:
    """Audit summary required by the P6 data-analysis report section 4."""
    m = pd.read_csv(MAPS / "drugid_to_smiles_v2.csv")
    try:
        from rdkit import Chem  # type: ignore

        def ok(s):
            try:
                return Chem.MolFromSmiles(s) is not None
            except Exception:
                return False

        valid = m["canonical_smiles"].dropna().map(ok).mean()
    except ImportError:
        valid = float("nan")
    canon_dup = m["canonical_smiles"].dropna().duplicated().sum()
    audit = {
        "n_rows": int(len(m)),
        "coverage": round(float(m["canonical_smiles"].notna().mean()), 4),
        "valid_smiles_fraction": None if pd.isna(valid) else round(float(valid), 4),
        "canonical_smiles_collisions": int(canon_dup),
        "matches_above_threshold": int(m["above_threshold"].sum()),
        "ambiguous_margin_lt_0.01": int((m["margin"] < 0.01).sum()),
        "median_match_score": round(float(m["match_score"].median()), 4),
    }
    print(json.dumps(audit, indent=2))


def cmd_selftest(_args: argparse.Namespace) -> None:
    """End-to-end tiny check: a planted kaggle vector must find its PRISM twin."""
    rng = np.random.default_rng(0)
    lines = 20
    protos = rng.normal(size=(3, lines))
    Bn = np.vstack([protos, rng.normal(size=(4, lines))])
    K = np.stack([protos[1] + rng.normal(scale=0.05, size=lines)])
    br, bj, sr = _top2(_cnorm(K), _cnorm(Bn), np.arange(len(Bn)))
    assert bj[0] == 1 and br[0] > 0.99 and sr[0] < br[0], (bj, br, sr)
    print("[selftest] OK")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").set_defaults(func=cmd_prepare)
    mp = sub.add_parser("match")
    mp.add_argument("--chunk", type=int, default=2048,
                    help="compounds per matmul block (default 2048)")
    mp.add_argument("--q", type=float, default=0.9999,
                    help="null quantile for the acceptance threshold (default 0.9999)")
    mp.set_defaults(func=cmd_match)
    sub.add_parser("smiles").set_defaults(func=cmd_smiles)
    sub.add_parser("report").set_defaults(func=cmd_report)
    sub.add_parser("selftest").set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
