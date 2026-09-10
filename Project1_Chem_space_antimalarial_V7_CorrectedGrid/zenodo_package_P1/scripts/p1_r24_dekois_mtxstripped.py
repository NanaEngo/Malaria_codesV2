#!/usr/bin/env python3
"""P1 V8 revision — R2.4 DEKOIS 2.0 re-run on an MTX-stripped PfDHFR receptor.

Reviewer R2.4: EF@1% = EF@5% = 0.00 in the DEKOIS benchmark suggests the retained
methotrexate (MTX) blocks the antifolate pocket; re-run on a ligand-stripped
receptor.

Design (audited against P2 assets on 2026-09-09):
  * Benchmark set (P2): 40 DEKOIS actives (DHFR_ligands.smi) + 1200 property-matched
    decoys (DHFR_decoys.smi), the set declared in SM Table S10 (40/1200).
  * Two arms, identical protocol except the receptor:
      - arm "retained": P2 data/proteins/7F3Y.pdbqt (retains MTX 126 at., NDP 116,
        UMP 44, GOL 18) — reproduces the original 0.450/0.00 baseline on this pipeline;
      - arm "stripped": MTX-stripped PfDHFR WT receptor built during the R1.2
        retrospective (9075 ATOM, 0 HETATM, same frame as 7F3Y.pdbqt;
        MET A 1 N = 18.905, 23.316, -52.623 in both) — the R2.4 test.
  * Grid: P2 canonical Docking_7F3Y grid, center (1.33, -1.733, -23.842), 25 A box.
    MTX CoM in this frame is (7.44, 0.57, -29.74), ~8.9 A from the grid center, i.e.
    inside the box: retained MTX is geometrically able to block active poses.
  * Protocol: ligands prepared identically in both arms (RDKit ETKDGv3 + MMFF, then
    Open Babel PDBQT, as in the original enrichment script). Exhaustiveness 32, the
    V8 revised-protocol standard (R2.3/R1.2), num_modes 20. Documented deviation from
    the original config's exhaustiveness = 64; both arms use the same value so the
    retained-vs-stripped comparison is internally controlled.
  * Metrics: ROC-AUC (+ bootstrap 95% CI), EF@1/5/10%, BEDROC (alpha=20), PR-AUC,
    per-arm docked counts.

Outputs (results/dekois_mtxstripped_20260909/):
  scores_<arm>.csv        — compound, label, vina_score_kcal_mol (or FAILED)
  metrics_<arm>.csv       — one row per arm with all metrics
  summary.json / .txt     — machine + human readable record
  run.log                 — progress log
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
P2 = ROOT.parent / "Project2_Polypharmacology_MD_ValidationV2607"
OUT = ROOT / "results/dekois_mtxstripped_20260909"

ENV = Path("/home/nanaengo/miniforge3/envs/malaria_md/bin")
OBABEL = ENV / "obabel"
VINA = Path("/usr/local/bin/vina")

ACTIVES = P2 / "data/external/dekois/DHFR_ligands.smi"   # 40
DECOYS = P2 / "data/external/dekois/DHFR_decoys.smi"     # 1200

RECEPTORS = {
    "retained": P2 / "data/proteins/7F3Y.pdbqt",
    "stripped": ROOT / "results/retrospective_approved_antimalarials_20260909"
                      / "receptors/PfDHFR_WT_receptor.pdbqt",
}

GRID = {"center": [1.33, -1.733, -23.842], "size": [25.0, 25.0, 25.0]}
EXHAUSTIVENESS = 32
NUM_MODES = 20
CPU_PER_JOB = 2
SEED = 42


def load_smiles(path: Path) -> list[str]:
    """Load 'SMILES <id>' lines, canonicalise, return (smiles, ids)."""
    smiles, ids = [], []
    for line in path.read_text().splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        mol = Chem.MolFromSmiles(parts[0])
        if mol is None:
            continue
        smiles.append(Chem.MolToSmiles(mol))
        ids.append(parts[1] if len(parts) > 1 else parts[0])
    return smiles, ids


def prepare_ligand(smiles: str, workdir: Path, index: int) -> Path | None:
    """RDKit ETKDGv3 + MMFF, then Open Babel -> PDBQT (original protocol)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, AllChem.ETKDGv3()) != 0:
        return None
    try:
        AllChem.MMFFOptimizeMolecule(mol)
    except Exception:
        pass
    pdb = workdir / f"lig_{index}.pdb"
    pdbqt = workdir / f"lig_{index}.pdbqt"
    Chem.MolToPDBFile(mol, str(pdb))
    ret = subprocess.run(
        [str(OBABEL), str(pdb), "-O", str(pdbqt)],
        capture_output=True,
    )
    if ret.returncode != 0 or not pdbqt.exists():
        return None
    return pdbqt


def dock_one(args: tuple) -> dict:
    """Dock one ligand against one receptor; returns a record dict."""
    smiles, label, arm, workdir, index = args
    lig = prepare_ligand(smiles, workdir, index)
    if lig is None:
        return {"smiles": smiles, "label": label, "arm": arm,
                "score": None, "status": "PREP_FAILED"}
    out = workdir / f"out_{index}.pdbqt"
    cmd = [
        str(VINA), "--receptor", str(RECEPTORS[arm]), "--ligand", str(lig),
        "--out", str(out),
        "--center_x", str(GRID["center"][0]),
        "--center_y", str(GRID["center"][1]),
        "--center_z", str(GRID["center"][2]),
        "--size_x", str(GRID["size"][0]),
        "--size_y", str(GRID["size"][1]),
        "--size_z", str(GRID["size"][2]),
        "--exhaustiveness", str(EXHAUSTIVENESS),
        "--num_modes", str(NUM_MODES),
        "--cpu", str(CPU_PER_JOB),
    ]
    ret = subprocess.run(cmd, capture_output=True)
    if ret.returncode != 0 or not out.exists():
        return {"smiles": smiles, "label": label, "arm": arm,
                "score": None, "status": "DOCK_FAILED"}
    text = out.read_text(encoding="utf-8", errors="ignore")
    scores = []
    for line in text.splitlines():
        if line.startswith("REMARK VINA RESULT:"):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    scores.append(float(parts[3]))
                except ValueError:
                    pass
    if not scores:
        return {"smiles": smiles, "label": label, "arm": arm,
                "score": None, "status": "NO_SCORE"}
    return {"smiles": smiles, "label": label, "arm": arm,
            "score": min(scores), "status": "OK"}


def bedroc(y_true: np.ndarray, scores: np.ndarray, alpha: float = 20.0) -> float:
    n = len(y_true)
    n_actives = int(y_true.sum())
    if n_actives == 0 or n_actives == n:
        return float("nan")
    order = np.argsort(-scores)
    y_sorted = y_true[order]
    ra = n_actives / n
    sum_exp = sum(np.exp(-alpha * i / n) for i, label in enumerate(y_sorted) if label == 1)
    bedroc_max = (ra * np.sinh(alpha / 2) / (np.cosh(alpha / 2) - 1)) + \
                 ((1 - ra) / (1 - np.exp(-alpha)))
    return float((sum_exp / n_actives) / bedroc_max)


def enrichment_factor(y_true: np.ndarray, scores: np.ndarray, fraction: float) -> float:
    n = len(y_true)
    n_actives = int(y_true.sum())
    if n_actives == 0:
        return 0.0
    cutoff = max(1, int(np.ceil(fraction * n)))
    order = np.argsort(-scores)
    top_actives = int(y_true[order[:cutoff]].sum())
    return float((top_actives / cutoff) / (n_actives / n))


def bootstrap_auc(y_true: np.ndarray, scores: np.ndarray, n_boot: int = 10000,
                  seed: int = SEED) -> tuple:
    rng = np.random.default_rng(seed)
    aucs = []
    idx = np.arange(len(y_true))
    for _ in range(n_boot):
        samp = rng.choice(idx, size=len(idx), replace=True)
        if len(np.unique(y_true[samp])) < 2:
            continue
        aucs.append(roc_auc_score(y_true[samp], scores[samp]))
    if not aucs:
        return float("nan"), float("nan"), float("nan")
    lo, hi = np.percentile(aucs, [2.5, 97.5])
    return float(np.mean(aucs)), float(lo), float(hi)


def run_arm(arm: str, actives: list, decoys: list, workers: int) -> pd.DataFrame:
    print(f"[{arm}] docking {len(actives)} actives + {len(decoys)} decoys "
          f"(exh {EXHAUSTIVENESS})...", flush=True)
    workdir = OUT / f"work_{arm}"
    workdir.mkdir(parents=True, exist_ok=True)
    tasks = [(a, "active", arm, workdir, i) for i, a in enumerate(actives)]
    tasks += [(d, "decoy", arm, workdir, len(actives) + i)
              for i, d in enumerate(decoys)]
    with mp.Pool(workers) as pool:
        records = []
        for j, rec in enumerate(pool.imap_unordered(dock_one, tasks, chunksize=8)):
            records.append(rec)
            if (j + 1) % 100 == 0:
                ok = sum(1 for r in records if r["status"] == "OK")
                print(f"[{arm}] {j+1}/{len(tasks)} done, {ok} OK", flush=True)
    df = pd.DataFrame(records)
    df.to_csv(OUT / f"scores_{arm}.csv", index=False)
    return df


def metrics_for(df: pd.DataFrame, arm: str) -> dict:
    docked = df[df["status"] == "OK"].copy()
    y = np.array(docked["label"] == "active", dtype=int)
    s = np.array(-docked["score"].values)  # negate: higher = better
    if len(np.unique(y)) < 2:
        return {"arm": arm, "n_docked": len(docked), "ROC_AUC": "nan",
                "note": "insufficient classes"}
    auc = roc_auc_score(y, s)
    auc_mean, auc_lo, auc_hi = bootstrap_auc(y, s)
    return {
        "arm": arm,
        "n_actives_requested": int((df["label"] == "active").sum()),
        "n_decoys_requested": int((df["label"] == "decoy").sum()),
        "n_docked": int(len(docked)),
        "n_actives_docked": int((y == 1).sum()),
        "n_decoys_docked": int((y == 0).sum()),
        "n_prep_failed": int((df["status"] == "PREP_FAILED").sum()),
        "n_dock_failed": int((df["status"] == "DOCK_FAILED").sum()),
        "ROC_AUC": round(float(auc), 4),
        "ROC_AUC_mean_boot": round(auc_mean, 4),
        "ROC_AUC_95CI_lo": round(auc_lo, 4),
        "ROC_AUC_95CI_hi": round(auc_hi, 4),
        "EF1pct": round(enrichment_factor(y, s, 0.01), 3),
        "EF5pct": round(enrichment_factor(y, s, 0.05), 3),
        "EF10pct": round(enrichment_factor(y, s, 0.10), 3),
        "BEDROC": round(bedroc(y, s, 20.0), 4),
        "PR_AUC": round(float(average_precision_score(y, s)), 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=min(24, max(1, mp.cpu_count() // 2)))
    ap.add_argument("--arms", default="both", choices=["both", "retained", "stripped"])
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    actives, _ = load_smiles(ACTIVES)
    decoys, _ = load_smiles(DECOYS)
    print(f"Loaded {len(actives)} actives, {len(decoys)} decoys", flush=True)
    if len(actives) != 40 or len(decoys) != 1200:
        print(f"WARNING: expected 40/1200, got {len(actives)}/{len(decoys)}", flush=True)

    arms = ["retained", "stripped"] if args.arms == "both" else [args.arms]
    rows = []
    for arm in arms:
        rec = RECEPTORS[arm]
        if not rec.exists():
            print(f"ERROR: receptor missing for {arm}: {rec}", flush=True)
            sys.exit(1)
        print(f"[{arm}] receptor: {rec}", flush=True)
        t0 = time.time()
        df = run_arm(arm, actives, decoys, args.workers)
        m = metrics_for(df, arm)
        m["wall_min"] = round((time.time() - t0) / 60, 1)
        rows.append(m)
        print(f"[{arm}] metrics: {json.dumps(m, indent=2)}", flush=True)

    mdf = pd.DataFrame(rows)
    mdf.to_csv(OUT / "metrics.csv", index=False)
    record = {
        "protocol": {
            "grid_center": GRID["center"], "grid_size": GRID["size"],
            "exhaustiveness": EXHAUSTIVENESS, "num_modes": NUM_MODES,
            "cpu_per_job": CPU_PER_JOB,
            "ligand_prep": "RDKit ETKDGv3 + MMFF, Open Babel PDBQT (original protocol)",
            "note": "exhaustiveness 32 = V8 revised-protocol standard; retained arm "
                    "reproduces the declared baseline under an identical pipeline",
        },
        "receptors": {a: str(RECEPTORS[a]) for a in RECEPTORS},
        "arms": rows,
    }
    (OUT / "summary.json").write_text(json.dumps(record, indent=2))
    txt = [
        "R2.4 DEKOIS 2.0 re-run — MTX-stripped PfDHFR receptor",
        "=" * 60,
        json.dumps(record, indent=2),
    ]
    (OUT / "summary.txt").write_text("\n".join(txt))
    print("Done. Results in", OUT, flush=True)


if __name__ == "__main__":
    main()