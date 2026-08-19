"""P4 — Novelty N5: scalar-weight sensitivity (quantifies audit claim C5).

Shows that the high-MPO / low-SYBA front point P3 becomes the argmax of a
fixed-weight scalar aggregation only at a degenerate weight w_MPO ~>= 0.993.
Sweeps w_MPO over the normalized MPO/SYBA plane for all candidates (front +
baseline molecules). Output: fraction of the weight range where each candidate
is the scalar argmax.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
FRONT = PROJECT / "results" / "pareto" / "merged_pareto_front.csv"
BENCH = PROJECT / "results" / "pareto" / "p4_multiobj_benchmark.csv"
OUT = PROJECT / "results" / "pareto" / "p4_scalar_weight_sweep.csv"


def main() -> None:
    front = pd.read_csv(FRONT)[["mpo", "syba"]].to_numpy(float)
    bench = pd.read_csv(BENCH)[["mpo", "syba"]].to_numpy(float)
    cand = np.vstack([front, bench])
    lo = cand.min(axis=0)
    hi = cand.max(axis=0)
    norm = (cand - lo) / np.where(hi - lo > 1e-10, hi - lo, 1.0)

    # Sweep w_MPO from 0 to 1; scalar = w*mpo + (1-w)*syba (both normalised, maximised)
    ws = np.linspace(0.0, 1.0, 100001)
    wins = np.zeros(len(cand), dtype=int)
    scalar = ws[:, None] * norm[:, 0][None, :] + (1 - ws)[:, None] * norm[:, 1][None, :]
    wins = np.argmax(scalar, axis=1)

    rows = []
    for i in range(len(cand)):
        span = np.sum(wins == i) / len(ws)
        if span > 0:
            w_at = ws[wins == i]
            rows.append({"cand_idx": i, "span_frac": span,
                         "w_min": float(w_at.min()), "w_max": float(w_at.max()),
                         "mpo": float(cand[i, 0]), "syba": float(cand[i, 1])})
    res = pd.DataFrame(rows).sort_values("span_frac", ascending=False).reset_index(drop=True)
    print(res.to_string(index=False))
    res.to_csv(OUT, index=False)
    print(f"[N5] -> results/pareto/p4_scalar_weight_sweep.csv")


if __name__ == "__main__":
    main()
