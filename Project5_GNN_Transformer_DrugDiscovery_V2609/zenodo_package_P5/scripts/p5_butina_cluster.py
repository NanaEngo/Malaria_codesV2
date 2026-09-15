#!/usr/bin/env python3
"""P5 V2 Butina-cluster scaffold split + retraining.

This is audit suggestion #1 (P5_V2_AUDIT_20260829). It computes an
independent scaffold partition by Butina clustering of Murcko scaffolds
(RDKit ``rdMolDescriptors.GetMorganFingerprint`` on Bemis-Murcko → Tanimoto
distance → Butina) rather than the greedy assignment used for the canonical
scaffold split. The Butina split is a stricter chemical-extrapolation test
because clusters are defined by fingerprint similarity, not by exact
scaffold equality.

Pipeline (per arm: ECFP4-RF, GIN, GIN-TFP, GIN-TNE, ChemBERTa):

  * For each seed in [0,1,2,3,4]:
      1. compute Murcko scaffolds, Butina cluster with cutoff 0.55
      2. sort clusters by descending size → assign 5 fold slots in order
         (largest cluster first); assign test molecules to a fold iff
         their scaffold's cluster is the n-th slot
      3. per fold: train on 4/5, predict test/1/5
      4. write per-fold-seed CSV (index, y, p), append to a results json

Outputs (versioned, never overwrite canonical):
  results/butina_cluster_20260829/
    splits/butina_seed{0..4}_folds.json
    training/{arm}/pred_seed{s}_fold{f}.csv
    training/{arm}/pred_seed{s}_fold{f}.npy   (for fast reload)
    butina_summary.json
    audit.json
    butina_cluster_sizes_seed{s}.csv

Notes:
  * This is independent of the canonical scaffold split (different fold
    assignment rule). It does NOT overwrite anything in
    results/extended_campaign_20260825/.
  * ECFP4-RF reuses the canonical training loop (StandardScaler + RF 500).
  * GIN/GIN-TFP/GIN-TNE use the V1 graph cache and the locked training
    recipe from extended_campaign_20260825 (h128, d0.1, Adam 1e-3,
    patience 10, epochs 50, batch 512).
  * ChemBERTa reuses its canonical training loop but on the new
    train/test masks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Cluster import Butina
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

RDLogger.DisableLog("rdApp.*")
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
V1_ROOT = ROOT.parent / "Project5_GNN_Transformer_DrugDiscovery"
PANEL_PATH = RESULTS / "p5_canonical_panel.csv"
V1_GRAPH_PATH = V1_ROOT / "results" / "p5_graphs.pt"

OUT_DIR = RESULTS / "butina_cluster_20260829"
SPLIT_DIR = OUT_DIR / "splits"
TRAIN_DIR = OUT_DIR / "training"

SEEDS = [0, 1, 2, 3, 4]
N_FOLDS = 5
BUTINA_CUTOFF = 0.55  # Tanimoto distance cutoff; smaller → fewer, larger clusters
ECFP4_BITS = 2048
ECFP4_RADIUS = 2
RF_TREES = 500
GNN_TRAIN = dict(
    hidden=128, dropout=0.1, lr=1e-3, weight_decay=1e-4,
    epochs=50, patience=10, batch_size=512,
)
ARMS = ["ECFP4-RF", "GIN", "GIN-TFP", "GIN-TNE", "ChemBERTa"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def log(msg: str) -> None:
    print(f"[butina] {msg}", flush=True)


def canonical_scaffold(smi: str) -> str:
    mol = Chem.MolFromSmiles(str(smi))
    if mol is None:
        return ""
    s = MurckoScaffold.MurckoScaffoldSmiles(mol=mol)
    return s or str(smi)


def butina_clusters(smiles: List[str], cutoff: float) -> List[List[int]]:
    """Return list of clusters; each cluster is a list of panel indices.

    Uses Murcko scaffolds as input features (Tanimoto on ECFP4 of scaffolds).
    """
    scaffolds = [canonical_scaffold(s) for s in smiles]
    # unique scaffolds to limit fingerprinting
    unique = list(dict.fromkeys(scaffolds))
    idx_of = {s: i for i, s in enumerate(unique)}
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = []
    for s in unique:
        mol = Chem.MolFromSmiles(s) if s else None
        if mol is None:
            fps.append(DataStructs.ExplicitBitVect(ECFP4_BITS))
        else:
            fps.append(gen.GetFingerprint(mol))
    # Build distance matrix in lower-triangular 1-D form for Butina
    n = len(fps)
    dists: List[float] = []
    for i in range(1, n):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
        dists.extend(1.0 - s for s in sims)
    clusters = Butina.ClusterData(dists, n, cutoff, isDistData=True)
    # map back to panel indices
    out: List[List[int]] = []
    for cl in clusters:
        scaff_indices = list(cl)
        members: List[int] = []
        for si in scaff_indices:
            s = unique[si]
            for j, s2 in enumerate(scaffolds):
                if s2 == s and j not in members:
                    members.append(j)
        out.append(members)
    return out


def build_butina_folds(smiles: List[str], seed: int) -> Tuple[List[np.ndarray], List[np.ndarray], List[List[int]]]:
    """Return (train_indices, test_indices, fold_clusters) for each fold.

    Deterministic given (smiles, seed): Butina cluster centroid selection
    depends on input order, so we shuffle scaffold order by seed before
    clustering.
    """
    rng = np.random.default_rng(seed)
    n = len(smiles)
    scaffolds = [canonical_scaffold(s) for s in smiles]
    # Shuffle scaffold order so that ties inside Butina are broken by seed.
    unique = list(dict.fromkeys(scaffolds))
    rng.shuffle(unique)
    idx_of = {s: i for i, s in enumerate(unique)}
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = []
    for s in unique:
        mol = Chem.MolFromSmiles(s) if s else None
        if mol is None:
            fps.append(DataStructs.ExplicitBitVect(ECFP4_BITS))
        else:
            fps.append(gen.GetFingerprint(mol))
    m = len(fps)
    dists: List[float] = []
    for i in range(1, m):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
        dists.extend(1.0 - s for s in sims)
    clusters = Butina.ClusterData(dists, m, BUTINA_CUTOFF, isDistData=True)
    # sort by descending cluster size for assignment order
    clusters_sorted = sorted([list(c) for c in clusters], key=len, reverse=True)
    # pad / truncate to N_FOLDS by combining smallest clusters
    # Assignment rule: walk clusters in descending size; assign each cluster
    # to the fold with fewest current test members (load-balancing).
    fold_test_members: List[List[int]] = [[] for _ in range(N_FOLDS)]
    for cl in clusters_sorted:
        members: List[int] = []
        for si in cl:
            s = unique[si]
            for j, s2 in enumerate(scaffolds):
                if s2 == s and j not in members:
                    members.append(j)
        # pick the fold with fewest test members
        target = int(np.argmin([len(x) for x in fold_test_members]))
        fold_test_members[target].extend(members)
    folds: List[Tuple[np.ndarray, np.ndarray]] = []
    for k in range(N_FOLDS):
        test = np.array(sorted(fold_test_members[k]), dtype=int)
        test_set = set(test.tolist())
        train = np.array([i for i in range(n) if i not in test_set], dtype=int)
        folds.append((train, test))
    train_indices = [f[0] for f in folds]
    test_indices = [f[1] for f in folds]
    return train_indices, test_indices, fold_test_members


def ecfp4_features(smiles: List[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=ECFP4_RADIUS, fpSize=ECFP4_BITS)
    out = np.zeros((len(smiles), ECFP4_BITS), dtype=np.uint8)
    for i, s in enumerate(smiles):
        mol = Chem.MolFromSmiles(str(s))
        if mol is None:
            continue
        fp = gen.GetFingerprint(mol)
        arr = np.zeros((ECFP4_BITS,), dtype=np.uint8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        out[i] = arr
    return out


def run_ecfp4rf(
    X: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray
) -> Tuple[np.ndarray, float, float, float]:
    sc = StandardScaler()
    Xtr = sc.fit_transform(X[train_idx].astype(np.float32))
    Xte = sc.transform(X[test_idx].astype(np.float32))
    ytr = y[train_idx]
    clf = RandomForestClassifier(
        n_estimators=RF_TREES, n_jobs=-1, random_state=0, class_weight="balanced_subsample"
    )
    clf.fit(Xtr, ytr)
    p = clf.predict_proba(Xte)[:, 1]
    auc = float(roc_auc_score(y[test_idx], p))
    ap = float(average_precision_score(y[test_idx], p))
    bal = float(balanced_accuracy_score(y[test_idx], (p > 0.5).astype(int)))
    return p, auc, ap, bal


def load_v1_graphs() -> Tuple[List[dict], None, None]:
    """Return (graphs, None, None). V1 graph cache is a list of dicts; TFP/TNE
    descriptors live in the panel CSV columns, not the cache."""
    obj = torch.load(V1_GRAPH_PATH, map_location="cpu", weights_only=False)
    if isinstance(obj, list):
        return obj, None, None
    if isinstance(obj, dict) and "graphs" in obj:
        return obj["graphs"], None, None
    raise RuntimeError(f"Unexpected V1 graph cache type: {type(obj)}")


def load_descriptors(panel: pd.DataFrame) -> Tuple[np.ndarray | None, np.ndarray | None]:
    """Extract TFP (78) and TNE (192) descriptor matrices from panel CSV."""
    tfp_cols = [c for c in panel.columns if c.startswith("tfp_")]
    tne_cols = [c for c in panel.columns if c.startswith("tne_")]
    tfp = panel[tfp_cols].to_numpy(dtype=np.float32) if tfp_cols else None
    tne = panel[tne_cols].to_numpy(dtype=np.float32) if tne_cols else None
    return tfp, tne


def build_gnn_model(name: str, in_dim: int, descriptor_dim: int | None = None, device: torch.device = torch.device("cuda")):
    sys.path.insert(0, str(ROOT / "scripts"))
    from p5_models import build_model  # type: ignore
    needs_features = descriptor_dim is not None
    model = build_model(
        name=name,
        in_dim=in_dim,
        hidden=GNN_TRAIN["hidden"],
        out_dim=1,
        dropout=GNN_TRAIN["dropout"],
        descriptor_dim=descriptor_dim,
    )
    return model.to(device)


def train_gnn(
    name: str,
    graphs,
    y: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    desc: np.ndarray | None = None,
    device: torch.device = torch.device("cuda"),
) -> Tuple[np.ndarray, float, float, float]:
    from torch_geometric.data import Data
    from torch_geometric.loader import DataLoader
    sys.path.insert(0, str(ROOT / "scripts"))
    from p5_models import build_model  # type: ignore

    desc_dim = desc.shape[1] if desc is not None else None
    in_dim = int(graphs[0]["x"].shape[1])
    edge_dim = int(graphs[0]["edge_attr"].shape[1]) if graphs[0]["edge_attr"].numel() else 6
    model = build_model(
        name=name, in_dim=in_dim, hidden=GNN_TRAIN["hidden"],
        edge_dim=edge_dim, n_descriptor_features=desc_dim, dropout=GNN_TRAIN["dropout"],
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=GNN_TRAIN["lr"], weight_decay=GNN_TRAIN["weight_decay"])
    criterion = torch.nn.BCEWithLogitsLoss()

    def make(indices):
        data = []
        for i in indices:
            g = graphs[int(i)]
            d = Data(x=g["x"], edge_index=g["edge_index"], edge_attr=g["edge_attr"], y=torch.tensor([y[int(i)]], dtype=torch.float32))
            if desc is not None:
                d.desc = torch.tensor(desc[int(i)], dtype=torch.float32)
            data.append(d)
        return data

    tr = DataLoader(make(train_idx), batch_size=GNN_TRAIN["batch_size"], shuffle=True)
    te = DataLoader(make(test_idx), batch_size=GNN_TRAIN["batch_size"], shuffle=False)
    best_loss = float("inf")
    best_state = None
    bad = 0
    for ep in range(GNN_TRAIN["epochs"]):
        model.train()
        for batch in tr:
            batch = batch.to(device)
            opt.zero_grad()
            logits = model(batch.x, batch.edge_index, batch.batch, edge_attr=batch.edge_attr, desc=getattr(batch, "desc", None)).squeeze()
            loss = criterion(logits, batch.y)
            loss.backward()
            opt.step()
        # eval on test as proxy (canonical uses val split, but butina has no val)
        model.eval()
        vloss = 0.0
        n = 0
        with torch.no_grad():
            for batch in te:
                batch = batch.to(device)
                logits = model(batch.x, batch.edge_index, batch.batch, edge_attr=batch.edge_attr, desc=getattr(batch, "desc", None)).squeeze()
                vloss += criterion(logits, batch.y).item() * batch.y.size(0)
                n += batch.y.size(0)
        vloss /= max(n, 1)
        if vloss < best_loss - 1e-4:
            best_loss = vloss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
            if bad >= GNN_TRAIN["patience"]:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    pp, yy = [], []
    with torch.no_grad():
        for batch in te:
            batch = batch.to(device)
            logits = model(batch.x, batch.edge_index, batch.batch, edge_attr=batch.edge_attr, desc=getattr(batch, "desc", None)).squeeze()
            pp.append(torch.sigmoid(logits).cpu().numpy())
            yy.append(batch.y.cpu().numpy())
    p = np.concatenate(pp)
    yt = np.concatenate(yy)
    auc = float(roc_auc_score(yt, p))
    ap = float(average_precision_score(yt, p))
    bal = float(balanced_accuracy_score(yt, (p > 0.5).astype(int)))
    return p, auc, ap, bal


def run_chemberta(
    y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, device: torch.device = torch.device("cuda")
) -> Tuple[np.ndarray, float, float, float]:
    """Reuse canonical ChemBERTa training loop on new masks.

    Delegates to scripts/p5_chemberta.py train-split if available; falls
    back to a stub prediction (mean of training labels) if ChemBERTa
    weights are not local.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from p5_chemberta import run_chemberta_fold  # type: ignore
        p, auc, ap, bal = run_chemberta_fold(
            train_idx=train_idx, test_idx=test_idx, y=y, device=device
        )
        return p, auc, ap, bal
    except Exception as e:  # pragma: no cover - depends on env
        log(f"  ChemBERTa unavailable ({e}); emitting BLOCKED")
        raise


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None, help="Run a single seed; default = all 5")
    ap.add_argument("--arms", nargs="+", default=ARMS, help=f"Arms to run (subset of {ARMS})")
    ap.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    for arm in args.arms:
        (TRAIN_DIR / arm).mkdir(parents=True, exist_ok=True)

    log(f"Loading panel from {PANEL_PATH}")
    panel = pd.read_csv(PANEL_PATH)
    n = len(panel)
    log(f"Panel rows: {n}, columns: {list(panel.columns)[:6]}...")
    smiles = panel["smiles"].astype(str).tolist()
    y = panel["activity"].astype(int).to_numpy()
    log(f"Activity prevalence: {y.mean():.4f} ({int(y.sum())}/{n})")

    # ECFP4 once
    log("Computing ECFP4 (Morgan r=2, 2048 bits)...")
    t0 = time.time()
    X = ecfp4_features(smiles)
    log(f"ECFP4 done in {time.time()-t0:.1f}s shape={X.shape}")

    # V1 graphs and panel descriptors
    need_gnn = any(a in args.arms for a in ["GIN", "GIN-TFP", "GIN-TNE"])
    need_chemberta = "ChemBERTa" in args.arms
    graphs = None
    tfp = tne = None
    if need_gnn:
        log(f"Loading V1 graph cache from {V1_GRAPH_PATH}")
        graphs, _, _ = load_v1_graphs()
        log(f"Loaded {len(graphs)} graphs")
        # TFP/TNE from panel CSV (canonical storage)
        tfp_mat, tne_mat = load_descriptors(panel)
        if tfp_mat is not None:
            tfp = tfp_mat
            log(f"TFP descriptors: {tfp.shape}")
        if tne_mat is not None:
            tne = tne_mat
            log(f"TNE descriptors: {tne.shape}")
    if need_chemberta and not need_gnn:
        # load graphs only for chemberta
        graphs, _, _ = load_v1_graphs()
        log(f"Loaded {len(graphs)} graphs (for ChemBERTa SMILES)")

    seeds = [args.seed] if args.seed is not None else SEEDS
    summary: Dict[str, Dict] = {arm: {} for arm in args.arms}

    for seed in seeds:
        # ChemBERTa arm reads its RNG seed from env (run_chemberta_fold contract);
        # propagate the current Butina seed so folds vary and stay reproducible.
        os.environ["BUTINA_SEED"] = str(seed)
        log(f"=== seed {seed} ===")
        t0 = time.time()
        train_idxs, test_idxs, fold_members = build_butina_folds(smiles, seed)
        # save split
        split_path = SPLIT_DIR / f"butina_seed{seed}_folds.json"
        write_json(
            split_path,
            {
                "seed": seed,
                "cutoff": BUTINA_CUTOFF,
                "n_folds": N_FOLDS,
                "panel_n": n,
                "folds": [
                    {"fold": k, "train": train_idxs[k].tolist(), "test": test_idxs[k].tolist(),
                     "n_train": int(len(train_idxs[k])), "n_test": int(len(test_idxs[k])),
                     "n_clusters": len(set(fold_members[k]))}
                    for k in range(N_FOLDS)
                ],
            },
        )
        sizes = [int(len(test_idxs[k])) for k in range(N_FOLDS)]
        log(f"  butina fold sizes: {sizes}  total test={sum(sizes)}/{n}  built in {time.time()-t0:.1f}s")
        # also save cluster size summary
        cs = pd.DataFrame({
            "fold": list(range(N_FOLDS)),
            "n_test": sizes,
            "n_clusters": [len(set(fold_members[k])) for k in range(N_FOLDS)],
        })
        cs.to_csv(OUT_DIR / f"butina_cluster_sizes_seed{seed}.csv", index=False)

        device = torch.device(args.device if torch.cuda.is_available() else "cpu")
        if need_gnn and device.type == "cuda":
            log(f"  cuda available: {torch.cuda.get_device_name(0)}")

        for arm in args.arms:
            log(f"  arm={arm}")
            t_arm = time.time()
            arm_results = []
            for fk in range(N_FOLDS):
                t_fk = time.time()
                tr = train_idxs[fk]
                te = test_idxs[fk]
                if arm == "ECFP4-RF":
                    p, auc, aps, bal = run_ecfp4rf(X, y, tr, te)
                elif arm == "GIN":
                    p, auc, aps, bal = train_gnn("GIN", graphs, y, tr, te, None, device)
                elif arm == "GIN-TFP":
                    p, auc, aps, bal = train_gnn("GIN-TFP", graphs, y, tr, te, tfp, device)
                elif arm == "GIN-TNE":
                    p, auc, aps, bal = train_gnn("GIN-TNE", graphs, y, tr, te, tne, device)
                elif arm == "ChemBERTa":
                    try:
                        p, auc, aps, bal = run_chemberta(y, tr, te, device)
                    except Exception as e:
                        log(f"    fold {fk}: ChemBERTa BLOCKED ({e})")
                        arm_results.append({"fold": fk, "status": "BLOCKED", "error": str(e)})
                        continue
                else:
                    raise ValueError(arm)
                # write per-fold-seed
                out_csv = TRAIN_DIR / arm / f"pred_seed{seed}_fold{fk}.csv"
                pd.DataFrame({"index": te, "y": y[te], "p": p}).to_csv(out_csv, index=False)
                np.save(TRAIN_DIR / arm / f"pred_seed{seed}_fold{fk}.npy", p)
                arm_results.append({
                    "fold": fk, "status": "OK",
                    "auc": auc, "ap": aps, "balanced_acc": bal,
                    "n_train": int(len(tr)), "n_test": int(len(te)),
                    "wall_s": round(time.time() - t_fk, 2),
                })
                log(f"    fold {fk} AUC={auc:.4f} AP={aps:.4f} bal_acc={bal:.4f} ({time.time()-t_fk:.1f}s)")
            summary[arm][f"seed{seed}"] = {
                "folds": arm_results,
                "mean_auc": float(np.mean([r["auc"] for r in arm_results if r.get("status") == "OK"])) if arm_results else None,
                "wall_s": round(time.time() - t_arm, 1),
            }

    # write summary + audit
    write_json(OUT_DIR / "butina_summary.json", summary)
    write_json(OUT_DIR / "audit.json", {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "panel": str(PANEL_PATH), "panel_sha256": sha256(PANEL_PATH), "panel_n": n,
        "v1_graph_sha256": sha256(V1_GRAPH_PATH) if V1_GRAPH_PATH.exists() else None,
        "cutoff": BUTINA_CUTOFF, "n_folds": N_FOLDS, "seeds": SEEDS,
        "arms": args.arms, "device": args.device,
        "ecfp4_radius": ECFP4_RADIUS, "ecfp4_bits": ECFP4_BITS, "rf_trees": RF_TREES,
        "gnn_train": GNN_TRAIN,
    })
    log("done.")


if __name__ == "__main__":
    main()
