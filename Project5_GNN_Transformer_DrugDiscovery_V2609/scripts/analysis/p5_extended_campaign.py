#!/usr/bin/env python3
"""P5 V2 extended, versioned simulation campaign.

This script never overwrites canonical P5 results. It reads the frozen panel and
V1 graph/split artifacts, writes all new inputs/outputs under
``results/extended_campaign_20260825/``, and records hashes and configuration.

Subcommands:
  prepare   create independent scaffold partitions and chemical audits
  train     train GIN/GIN-TFP/GIN-TNE with AUPRC and per-run salience
  thresholds  run ECFP4-RF sensitivity on alternative ChEMBL thresholds
  all       run prepare, thresholds, and the requested training matrix

The ChemBERTa arm is intentionally separate: it is run only when its pretrained
weights are locally available. Missing local weights are recorded as BLOCKED,
never replaced by a different model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, balanced_accuracy_score, f1_score, roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CAMPAIGN = RESULTS / "extended_campaign_20260825"
SPLITS = CAMPAIGN / "splits"
ROBUST = CAMPAIGN / "robustness"
PANEL_PATH = RESULTS / "p5_canonical_panel.csv"
V1_ROOT = ROOT.parent / "Project5_GNN_Transformer_DrugDiscovery"
V1_GRAPH_PATH = V1_ROOT / "results" / "p5_graphs.pt"
V1_SPLIT_DIR = V1_ROOT / "results"
SEEDS = [0, 1, 2, 3, 4]
N_FOLDS = 5
DEFAULT_PARTITIONS = {"novel_101": 101, "novel_202": 202, "novel_303": 303}
MODELS = {"GIN": None, "GIN-TFP": "tfp", "GIN-TNE": "tne"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def scaffold_ids(smiles: list[str]) -> np.ndarray:
    out = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(str(smi))
        if mol is None:
            out.append("INVALID")
        else:
            out.append(MurckoScaffold.MurckoScaffoldSmiles(mol=mol) or str(smi))
    return np.asarray(out, dtype=object)


def make_scaffold_folds(smiles: list[str], seed: int) -> list[dict]:
    """Independent scaffold partition using the locked greedy assignment rule."""
    groups = scaffold_ids(smiles)
    unique = list(dict.fromkeys(groups.tolist()))
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    sizes = np.zeros(N_FOLDS, dtype=int)
    assignment = np.full(len(groups), -1, dtype=int)
    for group in unique:
        idx = np.flatnonzero(groups == group)
        fold = int(np.argmin(sizes))
        assignment[idx] = fold
        sizes[fold] += len(idx)
    folds = []
    for fold in range(N_FOLDS):
        test = np.flatnonzero(assignment == fold)
        rest = np.flatnonzero(assignment != fold).copy()
        fold_rng = np.random.default_rng(seed * 100 + fold)
        fold_rng.shuffle(rest)
        n_val = max(1, len(rest) // N_FOLDS)
        folds.append({"train": rest[n_val:].astype(int), "val": rest[:n_val].astype(int), "test": test.astype(int)})
    return folds


def load_v1_folds(split: str, seed: int) -> list[dict]:
    arr = np.load(V1_SPLIT_DIR / f"p5_splits_{split}_5fold_seed{seed}.npy", allow_pickle=True)
    return [{k: np.asarray(rec[k], dtype=int) for k in ("train", "val", "test")} for rec in arr]


def save_folds(name: str, folds_by_seed: dict[int, list[dict]]) -> Path:
    path = SPLITS / f"{name}.npy"
    arr = np.asarray([{k: v.tolist() for k, v in rec.items()} for seed in SEEDS for rec in folds_by_seed[seed]], dtype=object)
    np.save(path, arr, allow_pickle=True)
    return path


def chemical_standardization(smiles: list[str]) -> dict:
    """Audit exact, parent-fragment, and tautomer identity without changing labels."""
    try:
        from rdkit.Chem.MolStandardize import rdMolStandardize
    except Exception as exc:
        return {"status": "BLOCKED", "reason": f"rdMolStandardize unavailable: {exc}"}
    parent = rdMolStandardize.FragmentParent
    enumerator = rdMolStandardize.TautomerEnumerator()
    exact, parents, tautomers, invalid = [], [], [], 0
    for smi in smiles:
        mol = Chem.MolFromSmiles(str(smi))
        if mol is None:
            invalid += 1
            exact.append("INVALID"); parents.append("INVALID"); tautomers.append("INVALID")
            continue
        exact.append(Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True))
        try:
            pmol = parent(mol)
            parents.append(Chem.MolToSmiles(pmol, canonical=True, isomericSmiles=True) if pmol else "INVALID")
        except Exception:
            parents.append("ERROR")
        try:
            tmol = enumerator.Canonicalize(mol)
            tautomers.append(Chem.MolToSmiles(tmol, canonical=True, isomericSmiles=True))
        except Exception:
            tautomers.append("ERROR")
    return {
        "status": "COMPUTED", "n": len(smiles), "invalid": invalid,
        "exact_unique": len(set(exact)), "parent_unique": len(set(parents)),
        "tautomer_unique": len(set(tautomers)),
        "exact_duplicate_rows": len(exact) - len(set(exact)),
        "parent_duplicate_rows": len(parents) - len(set(parents)),
        "tautomer_duplicate_rows": len(tautomers) - len(set(tautomers)),
        "exact": exact, "parent": parents, "tautomer": tautomers,
    }


def split_audit(panel: pd.DataFrame, folds_by_seed: dict[int, list[dict]]) -> list[dict]:
    y = panel.activity.to_numpy(dtype=int)
    scaff = scaffold_ids(panel.smiles.astype(str).tolist())
    rows = []
    for seed, folds in folds_by_seed.items():
        for fold, rec in enumerate(folds):
            tr, va, te = rec["train"], rec["val"], rec["test"]
            rows.append({
                "seed": seed, "fold": fold, "n_train": len(tr), "n_val": len(va), "n_test": len(te),
                "train_prevalence": float(y[tr].mean()), "val_prevalence": float(y[va].mean()), "test_prevalence": float(y[te].mean()),
                "train_test_scaffold_overlap": int(len(set(scaff[tr]) & set(scaff[te]))),
                "n_train_scaffolds": int(len(set(scaff[tr]))), "n_test_scaffolds": int(len(set(scaff[te]))),
            })
    return rows


def prepare() -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True); SPLITS.mkdir(exist_ok=True); ROBUST.mkdir(exist_ok=True)
    panel = pd.read_csv(PANEL_PATH)
    smiles = panel.smiles.astype(str).tolist()
    config = {
        "campaign": "P5_extended_campaign_20260825", "panel": str(PANEL_PATH),
        "panel_sha256": sha256(PANEL_PATH), "panel_n": len(panel), "seeds": SEEDS, "n_folds": N_FOLDS,
        "v1_graph_path": str(V1_GRAPH_PATH), "v1_graph_sha256": sha256(V1_GRAPH_PATH),
        "models": list(MODELS), "novel_partitions": DEFAULT_PARTITIONS,
        "training": {"epochs": 50, "patience": 10, "batch_size": 512, "hidden": 128, "dropout": 0.1, "lr": 1e-3, "weight_decay": 1e-4},
        "descriptor_modes": {"GIN": ["native"], "GIN-TFP": ["native", "permuted"], "GIN-TNE": ["native", "permuted"]},
        "policy": "All outputs versioned; canonical results never overwritten; missing dependencies fail closed.",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    write_json(CAMPAIGN / "campaign_config.json", config)
    all_audits = {}
    for name, seed in DEFAULT_PARTITIONS.items():
        by_seed = {s: make_scaffold_folds(smiles, seed + s) for s in SEEDS}
        path = save_folds(name, by_seed)
        all_audits[name] = {"seed": seed, "split_file": str(path), "split_sha256": sha256(path), "records": split_audit(panel, by_seed)}
    canonical = {"split": "canonical_v1_read_only", "records": []}
    for split in ("random", "scaffold"):
        for seed in SEEDS:
            folds = load_v1_folds(split, seed)
            canonical["records"].extend([{**r, "seed": seed, "split": split} for r in split_audit(panel, {seed: folds})])
    chem = chemical_standardization(smiles)
    write_json(ROBUST / "chemical_standardization_audit.json", chem)
    write_json(ROBUST / "split_audit.json", {"novel": all_audits, "canonical": canonical})
    write_json(CAMPAIGN / "prepare_status.json", {"status": "COMPUTED", "partitions": all_audits, "chemical_audit": "robustness/chemical_standardization_audit.json"})
    print(f"Prepared {len(DEFAULT_PARTITIONS)} independent scaffold partitions and chemical audit in {CAMPAIGN}")


def ecfp_matrix(smiles: list[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    out = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(str(smi))
        if mol is not None:
            DataStructs.ConvertToNumpyArray(gen.GetFingerprint(mol), out[i])
    return out


def train_model_partition(partition: str, model_name: str, descriptor_mode: str, device_name: str, max_new_records: int | None = None) -> None:
    import torch
    from torch_geometric.data import Data
    from torch_geometric.loader import DataLoader
    sys.path.insert(0, str(ROOT / "scripts"))
    import p5_models
    panel = pd.read_csv(PANEL_PATH)
    y = panel.activity.to_numpy(dtype=np.int64)
    graphs = torch.load(V1_GRAPH_PATH, map_location="cpu", weights_only=False)
    desc = None
    desc_name = MODELS[model_name]
    if desc_name:
        cols = [f"{desc_name}_{i}" for i in range(78 if desc_name == "tfp" else 192)]
        desc = panel[cols].to_numpy(dtype=np.float32)
        if descriptor_mode == "permuted":
            partition_seed = {"canonical_scaffold": 11, "novel_101": 101, "novel_202": 202, "novel_303": 303}.get(partition, 0)
            mode_seed = 0 if descriptor_mode == "native" else 10000
            rng = np.random.default_rng(20260825 + partition_seed + sum(ord(c) for c in model_name) + mode_seed)
            desc = desc[rng.permutation(len(desc))]
    device = torch.device("cuda" if device_name == "cuda" and torch.cuda.is_available() else "cpu")
    out_dir = CAMPAIGN / "training" / partition / f"{model_name}_{descriptor_mode}"
    out_dir.mkdir(parents=True, exist_ok=True)
    result_csv = out_dir / "fold_results.csv"
    completed = set()
    rows = []
    if result_csv.exists():
        old = pd.read_csv(result_csv); rows = old.to_dict("records"); completed = {(int(r["seed"]), int(r["fold"])) for r in rows}
    canonical_split = {"canonical_random": "random", "canonical_scaffold": "scaffold"}.get(partition)
    fold_map = ({s: load_v1_folds(canonical_split, s) for s in SEEDS} if canonical_split else None)
    if fold_map is None:
        split_path = SPLITS / f"{partition}.npy"
        arr = np.load(split_path, allow_pickle=True)
        fold_map = {seed: [{k: np.asarray(rec[k], dtype=int) for k in ("train", "val", "test")} for rec in arr[seed*5:(seed+1)*5]] for seed in SEEDS}
    in_dim = int(graphs[0]["x"].shape[1]); edge_dim = int(graphs[0]["edge_attr"].shape[1]) if graphs[0]["edge_attr"].numel() else 6
    salience_rows = []
    salience_path = out_dir / "salience_individual.npz"
    if salience_path.exists():
        old_sal = np.load(salience_path, allow_pickle=False)
        salience_rows = [{"seed": int(s), "fold": int(f), "salience": sal.tolist()} for s, f, sal in zip(old_sal["seed"], old_sal["fold"], old_sal["salience"])]
    new_records = 0
    for seed in SEEDS:
        for fold, rec in enumerate(fold_map[seed]):
            if (seed, fold) in completed: continue
            random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
            if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
            def make(indices):
                data = []
                for i in indices:
                    g = graphs[int(i)]
                    d = Data(x=g["x"], edge_index=g["edge_index"], edge_attr=g["edge_attr"], y=torch.tensor([y[int(i)]], dtype=torch.float32))
                    if desc is not None: d.desc = torch.tensor(desc[int(i)], dtype=torch.float32)
                    data.append(d)
                return data
            tr = DataLoader(make(rec["train"]), batch_size=512, shuffle=True)
            va = DataLoader(make(rec["val"]), batch_size=512)
            te = DataLoader(make(rec["test"]), batch_size=512)
            model = p5_models.build_model(model_name, in_dim, hidden=128, edge_dim=edge_dim, n_descriptor_features=(desc.shape[1] if desc is not None else None), dropout=0.1).to(device)
            opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
            criterion = torch.nn.BCEWithLogitsLoss(); best = -1.0; best_state = None; wait = 0
            for epoch in range(50):
                model.train()
                for batch in tr:
                    batch = batch.to(device); opt.zero_grad()
                    logits = model(batch.x, batch.edge_index, batch.batch, edge_attr=batch.edge_attr, desc=getattr(batch, "desc", None)).squeeze()
                    loss = criterion(logits, batch.y); loss.backward(); opt.step()
                model.eval(); vp=[]; vy=[]
                with torch.no_grad():
                    for batch in va:
                        batch=batch.to(device); logits=model(batch.x,batch.edge_index,batch.batch,edge_attr=batch.edge_attr,desc=getattr(batch,"desc",None)).squeeze()
                        vp.append(torch.sigmoid(logits).cpu().numpy()); vy.append(batch.y.cpu().numpy())
                val_auc=roc_auc_score(np.concatenate(vy),np.concatenate(vp))
                if val_auc > best: best=val_auc; best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}; wait=0
                else:
                    wait += 1
                    if wait >= 10: break
            model.load_state_dict(best_state); model.eval(); pp=[]; yy=[]
            with torch.no_grad():
                for batch in te:
                    batch=batch.to(device); logits=model(batch.x,batch.edge_index,batch.batch,edge_attr=batch.edge_attr,desc=getattr(batch,"desc",None)).squeeze()
                    pp.append(torch.sigmoid(logits).cpu().numpy()); yy.append(batch.y.cpu().numpy())
            pred=np.concatenate(pp); truth=np.concatenate(yy); binary=(pred>=0.5).astype(int)
            row={"partition":partition,"model":model_name,"descriptor_mode":descriptor_mode,"seed":seed,"fold":fold,"best_val_auc":best,"test_auc":roc_auc_score(truth,pred),"test_ap":average_precision_score(truth,pred),"test_f1":f1_score(truth,binary),"test_bacc":balanced_accuracy_score(truth,binary),"n_test":len(truth)}
            rows.append(row); new_records += 1; pd.DataFrame(rows).to_csv(result_csv,index=False)
            pd.DataFrame({"index":rec["test"],"y":truth,"p":pred}).to_csv(out_dir/f"pred_seed{seed}_fold{fold}.csv",index=False)
            if desc is not None:
                sal=best_state["head.0.weight"][:,128:].abs().mean(dim=0).numpy(); salience_rows.append({"seed":seed,"fold":fold,"salience":sal.tolist()})
            print(f"{partition} {model_name} {descriptor_mode} seed={seed} fold={fold} AUC={row['test_auc']:.4f} AP={row['test_ap']:.4f}", flush=True)
            if max_new_records is not None and new_records >= max_new_records:
                break
        if max_new_records is not None and new_records >= max_new_records:
            break
    complete = len(rows) == len(SEEDS) * N_FOLDS
    seed_means = {str(s): float(np.mean([r["test_auc"] for r in rows if int(r["seed"]) == s])) for s in SEEDS if any(int(r["seed"]) == s for r in rows)}
    summary={"status":"COMPUTED" if complete else "PARTIAL","partition":partition,"model":model_name,"descriptor_mode":descriptor_mode,"n_records":len(rows),"expected_records":len(SEEDS)*N_FOLDS,"mean_auc":float(np.mean([r["test_auc"] for r in rows])) if rows else None,"mean_ap":float(np.mean([r["test_ap"] for r in rows])) if rows else None,"seed_means_auc":seed_means,"device":str(device)}
    write_json(out_dir/"summary.json",summary)
    if salience_rows:
        unique_sal = {(r["seed"], r["fold"]): r for r in salience_rows}
        ordered_sal = [unique_sal[k] for k in sorted(unique_sal)]
        np.savez_compressed(salience_path,seed=np.asarray([r["seed"] for r in ordered_sal]),fold=np.asarray([r["fold"] for r in ordered_sal]),salience=np.asarray([r["salience"] for r in ordered_sal],dtype=np.float32))
    print(f"Completed {partition} {model_name} {descriptor_mode}: {len(rows)} records")


def thresholds(spec_name: str | None = None, n_estimators: int = 500) -> None:
    src=RESULTS/"p5_public_chembl_malaria.csv"; df=pd.read_csv(src); panel=pd.read_csv(PANEL_PATH)
    overlap=set(panel.smiles.astype(str))
    specs=[("canonical",6.0,5.0),("strict_active",6.5,5.0),("strict_inactive",6.0,5.5),("high_stringency",7.0,5.5)]
    if spec_name:
        specs=[spec for spec in specs if spec[0] == spec_name]
        if not specs:
            raise ValueError(f"Unknown threshold specification: {spec_name}")
    out_path=ROBUST/"chembl_threshold_sensitivity.json"
    existing=json.loads(out_path.read_text()) if out_path.exists() else {"status":"RUNNING_RF_ONLY","source":str(src),"rows":[],"boundary":"Full GIN threshold reruns are not included; this is an ECFP4-RF sensitivity analysis."}
    done={r.get("spec") for r in existing.get("rows",[]) if r.get("status")=="COMPUTED"}
    rows=[r for r in existing.get("rows",[]) if r.get("spec") not in {s[0] for s in specs}]
    for name, amin, imax in specs:
        sub=df[((df.pchembl>=amin)|(df.pchembl<imax))].copy()
        sub=sub[~sub.smiles.astype(str).isin(overlap)].reset_index(drop=True)
        sub["activity"]=(sub.pchembl>=amin).astype(int)
        sub=sub[((sub.pchembl<imax)|(sub.pchembl>=amin))].reset_index(drop=True)
        if len(sub)<100 or sub.activity.nunique()<2: rows.append({"spec":name,"status":"FAILED","n":len(sub)}); continue
        X=ecfp_matrix(sub.smiles.astype(str).tolist()); y=sub.activity.to_numpy(int); scaff=scaffold_ids(sub.smiles.astype(str).tolist())
        aucs=[]
        for seed in SEEDS:
            rng=np.random.default_rng(seed+7000); groups=list(dict.fromkeys(scaff.tolist())); rng.shuffle(groups); sizes=np.zeros(5,int); ass={}
            for g in groups:
                f=int(np.argmin(sizes)); ass[g]=f; sizes[f]+=int(np.sum(scaff==g))
            for fold in range(5):
                te=np.array([i for i,g in enumerate(scaff) if ass[g]==fold]); tr=np.array([i for i,g in enumerate(scaff) if ass[g]!=fold]); rf=RandomForestClassifier(n_estimators=n_estimators,random_state=seed,n_jobs=-1); rf.fit(X[tr],y[tr]); aucs.append(roc_auc_score(y[te],rf.predict_proba(X[te])[:,1]))
        rows.append({"spec":name,"status":"COMPUTED","active_min_pchembl":amin,"inactive_max_pchembl":imax,"n_estimators":n_estimators,"n":len(sub),"n_active":int(sub.activity.sum()),"n_inactive":int((1-sub.activity).sum()),"scaffold_auc_mean":float(np.mean(aucs)),"scaffold_auc_sd_fold_seed":float(np.std(aucs))})
        write_json(out_path,{"status":"RUNNING_RF_ONLY","source":str(src),"n_estimators":n_estimators,"rows":rows,"boundary":"Full GIN threshold reruns are not included; this is an ECFP4-RF sensitivity analysis."})
        print(f"Computed ChEMBL threshold {name}: n={len(sub)} AUC={np.mean(aucs):.4f}", flush=True)
    final_status="COMPUTED_RF_ONLY" if len(rows)==len([s for s in [("canonical",6.0,5.0),("strict_active",6.5,5.0),("strict_inactive",6.0,5.5),("high_stringency",7.0,5.5)]]) else "PARTIAL_RF_ONLY"
    write_json(out_path,{"status":final_status,"source":str(src),"n_estimators":n_estimators,"rows":rows,"boundary":"Full GIN threshold reruns are not included; this is an ECFP4-RF sensitivity analysis."})
    print(f"Wrote ChEMBL threshold sensitivity: {final_status}")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["prepare","thresholds","train","all"]); ap.add_argument("--partition",default="novel_101"); ap.add_argument("--model",choices=list(MODELS),default="GIN-TFP"); ap.add_argument("--descriptor-mode",choices=["native","permuted"],default="native"); ap.add_argument("--device",choices=["cpu","cuda"],default="cuda"); ap.add_argument("--all-training",action="store_true"); ap.add_argument("--threshold-spec",default=None); ap.add_argument("--n-estimators",type=int,default=500); ap.add_argument("--max-new-records",type=int,default=None)
    args=ap.parse_args()
    if args.command in ("prepare","all"): prepare()
    if args.command in ("thresholds","all"): thresholds(args.threshold_spec,args.n_estimators)
    if args.command=="train": train_model_partition(args.partition,args.model,args.descriptor_mode,args.device,args.max_new_records)
    if args.command=="all" and args.all_training:
        parts=["canonical_random","canonical_scaffold",*DEFAULT_PARTITIONS]
        for part in parts:
            for model, modes in (("GIN",["native"]),("GIN-TFP",["native","permuted"]),("GIN-TNE",["native","permuted"])):
                for mode in modes: train_model_partition(part,model,mode,args.device)

if __name__=="__main__": main()
