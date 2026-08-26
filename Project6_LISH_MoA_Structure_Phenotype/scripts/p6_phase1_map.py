#!/usr/bin/env python3
"""P6 Phase 1 -- drug_id -> perturbagen -> SMILES mapping against LINCS L1000 (GSE92742).

Stages (run in order):
    prepare  Build the Kaggle-side landmark matrix and CMap-side metadata caches.
    match    Max-correlate each Kaggle drug consensus against every individual
             Level5 trt_cp signature; calibrate threshold on permuted controls.
    smiles   Resolve matched pert_id to canonical SMILES via the public
             lincs-cell-painting repurposing TSV (fallback: clue.io API if CLUE_TOKEN set).
    report   Audit summary (coverage, collisions, invalid SMILES) printed as JSON.

Usage (HPC, env qom):
    python p6_phase1_map.py prepare
    python p6_phase1_map.py match [--chunk 20000]
    python p6_phase1_map.py smiles
    python p6_phase1_map.py report
    python p6_phase1_map.py selftest

Inputs are auto-discovered relative to this file:
    ../data/raw/GSE92742_Broad_LINCS_*.txt.gz, Level5_COMPZ.MODZ.gctx(.gz)
    ../../Project5_GNN_Transformer_DrugDiscovery/results/lish_moa/lish_moa_drug_level.csv

Outputs land in ../data/mappings/.
"""
import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "data" / "raw"
MAPS = HERE.parent / "data" / "mappings"
P5_CSV = (HERE.parent.parent / "Project5_GNN_Transformer_DrugDiscovery"
          / "results" / "lish_moa" / "lish_moa_drug_level.csv")

LEVEL5_H5 = RAW / "Level5_COMPZ.MODZ.gctx"
SIG_INFO = RAW / "GSE92742_Broad_LINCS_sig_info.txt.gz"
GENE_INFO = RAW / "GSE92742_Broad_LINCS_gene_info.txt.gz"
REPURPOSING_URL = ("https://s3.amazonaws.com/data.clue.io/repurposing/downloads/"
                   "repurposing_samples_20200324.txt")

KAGGLE_CACHE = MAPS / "kaggle_landmark_matrix.npz"
MATCH_OUT = MAPS / "drugid_to_pert_v1.csv"


def _ensure_dirs() -> None:
    MAPS.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- stage: prepare
def cmd_prepare(_args: argparse.Namespace) -> None:
    """Cache the Kaggle drug-level matrix restricted to landmark genes, and the
    trt_cp signature->perturbagen table from sig_info."""
    _ensure_dirs()

    gene = pd.read_csv(GENE_INFO, sep="\t")
    lm_entrez = set(gene.loc[gene["pr_is_lm"] == 1, "pr_gene_id"].astype(int))

    df = pd.read_csv(P5_CSV)
    gene_cols = [c for c in df.columns if c.startswith("g-")]
    entrez_of_col = {c: int(c.rsplit("_", 1)[1]) for c in gene_cols}
    keep_cols = [c for c in gene_cols if entrez_of_col[c] in lm_entrez]
    print(f"[prepare] kaggle rows={len(df)} gene cols={len(gene_cols)} "
          f"landmark-intersected={len(keep_cols)}")

    M = df[keep_cols].to_numpy(dtype=np.float32)
    col_entrez = np.array([entrez_of_col[c] for c in keep_cols], dtype=int)
    np.savez_compressed(
        KAGGLE_CACHE,
        matrix=M,
        drug_id=df["drug_id"].to_numpy(),
        col_entrez=col_entrez,
        n_observations=(df["n_observations"].to_numpy()
                        if "n_observations" in df else np.zeros(len(df))),
    )
    print(f"[prepare] wrote {KAGGLE_CACHE} shape={M.shape}")

    si = pd.read_csv(SIG_INFO, sep="\t")
    trt = si[si["pert_type"] == "trt_cp"][["sig_id", "pert_id", "pert_iname", "cell_id",
                                           "pert_idose", "pert_itime"]]
    trt.to_csv(MAPS / "cmap_trtcp_siginfo.csv", index=False)
    print(f"[prepare] trt_cp signatures={len(trt)} "
          f"unique perturbagens={trt.pert_id.nunique()}")


# ---------------------------------------------------------------- stage: match
def _open_gctx() -> tuple:
    """Return (h5py.File, row_ids_int_array, col_ids_str_array, data_node_path,
    transposed). transposed=True means the data node stores signatures on axis 0
    and genes on axis 1 (GEO GSE92742 variant); False is standard GCTx."""
    import h5py
    if not LEVEL5_H5.exists():
        raise FileNotFoundError(
            f"decompress first:\n  gunzip -kc {RAW/'Level5_COMPZ.MODZ.gctx.gz'} > {LEVEL5_H5}")
    f = h5py.File(LEVEL5_H5, "r")
    if "/0/MATRIX" in f:
        base = "/0/MATRIX"
        if "DATA" in f[base]:
            node, row_meta, col_meta = f"{base}/DATA", f"{base}/ROW/id", f"{base}/COL/id"
        else:
            node, row_meta, col_meta = f"{base}/0/DATA", f"{base}/0/ROW/id", f"{base}/0/COL/id"
    else:  # GEO GSE92742 layout (e.g. Level5_COMPZ.MODZ.gctx)
        node = "/0/DATA/0/matrix"
        row_meta, col_meta = "/0/META/ROW/id", "/0/META/COL/id"

    def _ids(ds):
        return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in ds[:]])

    row_ids, col_ids = _ids(f[row_meta]).astype(int), _ids(f[col_meta])
    # Standard GCTx: genes x sigs. GEO variant stores the transpose.
    transposed = f[node].shape[0] != len(row_ids)
    return f, row_ids, col_ids, node, transposed


def _cnorm(X: np.ndarray) -> np.ndarray:
    """Center each row and L2-normalize it (float64 copy)."""
    X = X.astype(np.float64)
    X -= X.mean(axis=1, keepdims=True)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def _top2(Kn: np.ndarray, Bn: np.ndarray, lbl: np.ndarray, chunk: int = 4096):
    """Best Pearson r of every query row against signature rows of Bn, plus the
    best r against a *different* label (streaming top-2 with distinct labels).

    Args:
        Kn: (n_drugs, n_genes) centered/normalized query matrix.
        Bn: (n_sigs, n_genes) centered/normalized reference matrix.
        lbl: (n_sigs,) perturbagen label of each reference row.
        chunk: signatures per matmul block.
    Returns:
        (best_r, best_j, second_r): length-n_drugs arrays; best_j indexes Bn.
    """
    n = len(Kn)
    best_r = np.full(n, -2.0)
    best_j = np.full(n, -1, dtype=np.int64)
    best_l = np.full(n, -1, dtype=np.int64)
    sec_r = np.full(n, -2.0)
    sec_l = np.full(n, -1, dtype=np.int64)
    rows = np.arange(n)
    for s in range(0, len(Bn), chunk):
        R = Kn @ Bn[s:s + chunk].T                      # (drugs, block)
        j = np.argmax(R, axis=1)
        v = R[rows, j]
        g = np.int64(s) + j                             # global signature index
        l = lbl[g]
        mA = l == best_l                                # same pert as current best
        best_r[mA] = np.maximum(best_r[mA], v[mA])
        mB = (~mA) & (l == sec_l)                       # same pert as runner-up
        sec_r[mB] = np.maximum(sec_r[mB], v[mB])
        mC = (~mA) & (~mB) & (v > best_r)               # new label beats best
        sec_r[mC], sec_l[mC] = best_r[mC], best_l[mC]
        best_r[mC], best_j[mC], best_l[mC] = v[mC], g[mC], l[mC]
        mD = (~mA) & (~mB) & (~mC) & (v > sec_r)        # new label beats runner-up
        sec_r[mD], sec_l[mD] = v[mD], l[mD]
    return best_r, best_j, sec_r


def cmd_match(args: argparse.Namespace) -> None:
    """Max-correlate each Kaggle drug consensus against every individual Level5
    trt_cp signature. Max-pooling over signatures is used instead of perturbagen
    means because averaging across cell lines/doses dilutes compound signals.
    Threshold calibrated on gene-permuted controls."""
    _ensure_dirs()
    # ponytail: our own cache holds string arrays; allow_pickle is safe here
    cache = np.load(KAGGLE_CACHE, allow_pickle=True)
    M, drug_ids, col_entrez = cache["matrix"], cache["drug_id"], cache["col_entrez"]

    f, row_ids, col_ids, node, transposed = _open_gctx()
    pos_of_entrez = {g: i for i, g in enumerate(row_ids)}
    sel_rows = np.array([pos_of_entrez[int(e)] for e in col_entrez], dtype=int)

    sig = pd.read_csv(MAPS / "cmap_trtcp_siginfo.csv")
    sig_pos = pd.Series(np.arange(len(col_ids)), index=pd.Index(col_ids))
    mask = sig["sig_id"].isin(sig_pos.index)
    if (~mask).sum():
        print(f"[match] warning: {(~mask).sum()} trt_cp sig_ids absent from gctx columns")
    sig = sig[mask]
    colsel = sig_pos.loc[sig["sig_id"]].to_numpy()
    ordc = np.argsort(colsel)  # h5py fancy indexing requires increasing order
    colsel = colsel[ordc]
    sig = sig.iloc[ordc].reset_index(drop=True)

    print(f"[match] gathering {len(colsel)} signatures x {len(sel_rows)} landmark genes")
    B = np.empty((len(colsel), len(sel_rows)), dtype=np.float32)
    data = f[node]
    gene_order = np.argsort(sel_rows)          # ascending positions for the HDF5 read
    restore = np.argsort(gene_order)           # maps sorted back to col_entrez order
    t0 = time.time()
    for start in range(0, len(colsel), args.chunk):
        sl = slice(start, min(start + args.chunk, len(colsel)))
        blk = (data[colsel[sl], :][:, gene_order][:, restore] if transposed
               else data[:, colsel[sl]][gene_order, :][restore, :])
        # both branches yield (n_sigs_chunk, n_genes) once oriented
        B[sl] = blk if transposed else blk.T
        print(f"[match] gathered {sl.stop}/{len(colsel)} "
              f"({sl.stop / (time.time() - t0):.0f} sigs/s)", flush=True)
    f.close()

    uniq_perts, inv = np.unique(sig["pert_id"].to_numpy(), return_inverse=True)
    print(f"[match] scanning {len(uniq_perts)} perturbagens / {len(B)} signatures")

    Kn, Bn = _cnorm(M), _cnorm(B)
    del B
    best_r, best_j, sec_r = _top2(Kn, Bn, inv)

    # negative-control calibration: permute genes within each kaggle vector
    rng = np.random.default_rng(42)
    Mp = np.stack([M[i, rng.permutation(M.shape[1])] for i in range(len(M))])
    null_best, _, _ = _top2(_cnorm(Mp), Bn, inv)
    thresh = float(np.quantile(null_best, 0.9999))

    hit = sig.iloc[best_j]
    out = pd.DataFrame({
        "drug_id": drug_ids,
        "matched_sig_id": hit["sig_id"].to_numpy(),
        "matched_cell_id": hit["cell_id"].to_numpy(),
        "matched_pert_id": hit["pert_id"].to_numpy(),
        "matched_pert_iname": hit["pert_iname"].to_numpy(),
        "match_score": best_r,
        "second_score": sec_r,
        "margin": best_r - sec_r,
        "above_threshold": best_r > thresh,
    })
    out.to_csv(MATCH_OUT, index=False)
    (MAPS / "match_threshold.json").write_text(json.dumps(
        {"threshold_q9999_null": thresh,
         "n_above": int(out.above_threshold.sum()), "n_total": len(out)}, indent=2))
    print(f"[match] threshold(null q=.9999)={thresh:.4f}; "
          f"above={int(out.above_threshold.sum())}/{len(out)} -> {MATCH_OUT}")


# ---------------------------------------------------------------- stage: smiles
def cmd_smiles(_args: argparse.Namespace) -> None:
    """Attach canonical SMILES to matched perturbagens."""
    _ensure_dirs()
    m = pd.read_csv(MATCH_OUT)
    rep_path = RAW / "repurposing_samples_20200324.txt"
    if not rep_path.exists():
        import urllib.request
        urllib.request.urlretrieve(REPURPOSING_URL, rep_path)
    # comment lines start with '!'
    rep = pd.read_csv(rep_path, sep="\t", comment="!",
                      usecols=["broad_id", "pert_iname", "smiles"],
                      low_memory=False).dropna(subset=["smiles"])
    rep["pert_iname"] = rep["pert_iname"].str.lower()
    rep["_core"] = rep["broad_id"].astype(str).str[:13]
    smile_by_name = rep.drop_duplicates("pert_iname").set_index("pert_iname")["smiles"]
    smile_by_core = rep.drop_duplicates("_core").set_index("_core")["smiles"]

    m["canonical_smiles"] = (m["matched_pert_iname"].astype(str).str.lower()
                             .map(smile_by_name))
    need = m["canonical_smiles"].isna()
    m.loc[need, "canonical_smiles"] = (m.loc[need, "matched_pert_id"].str[:13]
                                       .map(smile_by_core))
    m["smiles_source"] = np.where(m["canonical_smiles"].notna(), "repurposing_hub", "")

    token = os.environ.get("CLUE_TOKEN")
    if token and m["canonical_smiles"].isna().any():
        import urllib.parse
        import urllib.request
        todo = m.loc[m["canonical_smiles"].isna(), "matched_pert_id"].unique().tolist()
        filt = urllib.parse.quote(json.dumps(
            {"fields": ["pert_id", "pert_iname", "canonical_smiles"],
             "where": {"pert_id": {"inq": todo}}}))
        req = urllib.request.Request(
            f"https://api.clue.io/api/perts?filter={filt}",
            headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req) as r:
            perts = json.loads(r.read())
        by_id = {p["pert_id"]: p.get("canonical_smiles") for p in perts}
        miss = m["canonical_smiles"].isna()
        got = m.loc[miss, "matched_pert_id"].map(by_id)
        m.loc[miss, "canonical_smiles"] = got
        m.loc[miss & m["canonical_smiles"].notna(), "smiles_source"] = "clue_api"
        print(f"[smiles] clue.io fallback resolved {got.notna().sum()}/{len(todo)}")

    out_path = MAPS / "drugid_to_smiles_v1.csv"
    cols = ["drug_id", "matched_pert_id", "matched_pert_iname", "match_score",
            "second_score", "margin", "above_threshold", "canonical_smiles",
            "smiles_source"]
    m[cols].to_csv(out_path, index=False)
    print(f"[smiles] coverage={m.canonical_smiles.notna().mean():.3f} -> {out_path}")


# ---------------------------------------------------------------- stage: report
def cmd_report(_args: argparse.Namespace) -> None:
    """Audit summary required by the P6 data-analysis report §4."""
    m = pd.read_csv(MAPS / "drugid_to_smiles_v1.csv")
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
    canon_dup = (m["canonical_smiles"].dropna()
                 .duplicated().sum())
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


# ---------------------------------------------------------------- selftest
def cmd_selftest(_args: argparse.Namespace) -> None:
    """Tiny synthetic check of _top2 (no files needed): planted pairs are
    recovered across duplicate-label signatures; permutation destroys them."""
    rng = np.random.default_rng(0)
    genes = 50
    protos = rng.normal(size=(5, genes))
    Bn = np.repeat(protos, 3, axis=0)              # 15 sigs, labels [0,0,0,1,1,1,...]
    lbl = np.repeat(np.arange(5), 3)
    K = np.stack([protos[2] + rng.normal(scale=0.05, size=genes),
                  protos[1] + rng.normal(scale=0.05, size=genes)])
    best_r, best_j, sec_r = _top2(_cnorm(K), _cnorm(Bn), lbl)
    assert list(best_j // 3) == [2, 1], best_j
    assert best_r.min() > 0.99 and (sec_r < best_r).all(), (best_r, sec_r)
    # permuted control must lose the signal
    Mp = np.stack([K[i, rng.permutation(genes)] for i in range(len(K))])
    null_best, _, _ = _top2(_cnorm(Mp), _cnorm(Bn), lbl)
    assert null_best.max() < best_r.min(), (null_best, best_r)
    print("[selftest] OK — _top2 recovers planted pairs; permutation destroys them")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").set_defaults(func=cmd_prepare)
    mp = sub.add_parser("match")
    mp.add_argument("--chunk", type=int, default=20000,
                    help="gctx columns read per block (default 20000)")
    mp.set_defaults(func=cmd_match)
    sub.add_parser("smiles").set_defaults(func=cmd_smiles)
    sub.add_parser("report").set_defaults(func=cmd_report)
    sub.add_parser("selftest").set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
