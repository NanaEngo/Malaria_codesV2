"""P4 — Simulation N1: multi-objective benchmark of the four generation methods.

Re-evaluates the deposited per-seed best molecules of the four methods
(random / greedy / GA / MCTS) with the full OracleAggregator (MPO, SYBA, SA,
RRS, PNS) — the same oracle used to produce the canonical Pareto MCTS front —
then builds each method's Pareto front and compares hypervolume / coverage.

This closes the manuscript gap: "scalar baselines were evaluated on scalar
reward only, so a front-level comparison against them is not performed".
It makes the 4-method benchmark multi-objective without re-running anything.

Usage:
    python p4_benchmark_multiobj.py [--out results/pareto/p4_multiobj_benchmark.csv]
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
from pymoo.indicators.hv import Hypervolume
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

PROJECT = Path(__file__).resolve().parents[1]
BENCH = PROJECT / "results" / "benchmark_molecules_opt"
PARETO = PROJECT / "results" / "pareto"
FRONT_CSV = PARETO / "merged_pareto_front.csv"

ACTIVE = ["mpo", "syba", "rrs", "pns"]


def norm_syba(raw: float) -> float:
    """Same sigmoid normalisation as p4_recompute_pareto_syba.py / oracles."""
    return 1.0 / (1.0 + math.exp(-raw / 5.0))


def load_best_molecules() -> pd.DataFrame:
    frames = []
    for f in sorted(BENCH.glob("p4_benchmark_molecules_seed_*.csv")):
        df = pd.read_csv(f)
        if "best_smiles" in df.columns and "method" in df.columns:
            frames.append(df[["method", "seed", "best_smiles"]])
    return pd.concat(frames, ignore_index=True)


def evaluate(oracle, df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, (_, r) in enumerate(df.iterrows()):
        try:
            s = oracle.score(r["best_smiles"])
        except Exception:
            continue
        rows.append({
            "method": r["method"], "seed": int(r["seed"]),
            "smiles": r["best_smiles"],
            "mpo": s.get("mpo", 0.0), "syba": norm_syba(float(s.get("syba", 0.0))),
            "sa": s.get("sa", 0.0), "rrs": s.get("rrs", 0.0),
            "pns": s.get("pns", 0.0),
        })
    out = pd.DataFrame(rows)
    # de-duplicate by method+smiles keeping best per (method, smiles) on mean of active
    out["_mean"] = out[ACTIVE].mean(axis=1)
    out = out.sort_values("_mean", ascending=False).drop_duplicates(["method", "smiles"])
    return out.drop(columns="_mean").reset_index(drop=True)


def front_of(sub: pd.DataFrame) -> pd.DataFrame:
    vecs = sub[ACTIVE].to_numpy(float)
    mask = NonDominatedSorting().do(vecs, only_non_dominated_front=True)
    return sub.iloc[mask].reset_index(drop=True)


def igd(front: pd.DataFrame, ref: np.ndarray) -> float:
    """Inverted generational distance: mean dist from each ref pt to nearest front pt."""
    fv = front[ACTIVE].to_numpy(float)
    return float(np.mean([np.min(np.linalg.norm(fv - r, axis=1)) for r in ref]))


def spread(front: pd.DataFrame, ref: np.ndarray) -> float:
    """Delta-spread: coverage uniformity of front pts relative to ref extremes."""
    fv = front[ACTIVE].to_numpy(float)
    if len(fv) < 2:
        return float("nan")
    d = np.linalg.norm(np.diff(fv, axis=0), axis=1)
    d_bar = d.mean()
    lo = np.min(ref, axis=0)
    hi = np.max(ref, axis=0)
    df = np.min(np.linalg.norm(fv - lo, axis=1)) + np.min(np.linalg.norm(fv - hi, axis=1))
    return float((df + sum(abs(di - d_bar) for di in d)) / (df + len(d) * d_bar))


def hv_normalised(front: pd.DataFrame, lo: np.ndarray, hi: np.ndarray, ref: float = 1.1) -> float:
    """Hypervolume under a COMMON min-max normalisation shared across methods."""
    vecs = front[ACTIVE].to_numpy(float)
    norm = (vecs - lo) / np.where(hi - lo > 1e-10, hi - lo, 1.0)
    neg = -norm  # maximise -> minimise by negation (pymoo convention)
    return float(Hypervolume(ref_point=np.full(len(ACTIVE), ref)).do(neg))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(PARETO / "p4_multiobj_benchmark.csv"))
    args = ap.parse_args()

    from p4_mcts_oracles import OracleAggregator
    oracle = OracleAggregator(use_precomputed=True)

    df = load_best_molecules()
    ev = evaluate(oracle, df)
    ev.to_csv(args.out, index=False)
    canon = pd.read_csv(FRONT_CSV)
    canon = canon[~canon["smiles"].duplicated()]

    # Common normalisation bounds across ALL candidates (baselines + canonical front)
    all_vecs = np.vstack([ev[ACTIVE].to_numpy(float),
                          canon[ACTIVE].to_numpy(float)])
    lo = all_vecs.min(axis=0)
    hi = all_vecs.max(axis=0)

    # Reference set for IGD/spread: non-dominated union of ALL candidates
    allcand = pd.concat([ev[["method"] + ACTIVE], canon[["smiles"] + ACTIVE]], ignore_index=True)
    all_front = front_of(allcand)
    ref = all_front[ACTIVE].to_numpy(float)

    FR = PARETO / "p4_multiobj_fronts"
    FR.mkdir(parents=True, exist_ok=True)
    all_front[ACTIVE].to_csv(FR / "front_union_ref.csv", index=False)

    groups = [("random", ev[ev["method"] == "random"]),
              ("greedy", ev[ev["method"] == "greedy"]),
              ("ga", ev[ev["method"] == "ga"]),
              ("baselines_pooled", ev[ev["method"].isin(["random", "greedy", "ga"])]),
              ("mcts_canon", canon[["smiles"] + ACTIVE])]

    summary = []
    for name, sub in groups:
        fr = front_of(sub)
        fr[ACTIVE].to_csv(FR / f"front_{name}.csv", index=False)
        summary.append({"method": name, "n_unique": len(sub),
                        "front_size": len(fr),
                        "hv": hv_normalised(fr, lo, hi),
                        "igd": igd(fr, ref), "spread": spread(fr, ref)})

    summ = pd.DataFrame(summary)
    print(summ.round(3).to_string(index=False))
    summ.to_csv(PARETO / "p4_multiobj_front_summary.csv", index=False)
    print(f"[N1] summary -> results/pareto/p4_multiobj_front_summary.csv")
    print(f"[N1] per-method fronts -> results/pareto/p4_multiobj_fronts/")


if __name__ == "__main__":
    main()
