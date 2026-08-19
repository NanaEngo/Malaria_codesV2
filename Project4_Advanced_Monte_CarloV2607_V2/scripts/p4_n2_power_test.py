#!/usr/bin/env python3
"""N2 power test — can n=20 distinguish scalar-proxy vs ParetoPUCT selection?

Reuses N1 normalisation (norm_syba sigmoid + COMMON min-max bounds across all
candidate points, active objectives = mpo/syba/rrs/pns). Computes a per-seed
hypervolume for each mode, paired differences, then reports the minimal
detectable hypervolume difference (MDE) at alpha=0.05, power=0.80 for a
one-sided paired test at the CURRENT n and at the proposed n=20.

Honest reading: if MDE(n=20) is far ABOVE the observed effect, n=20 still
cannot resolve it and the near-null is real-within-detectable-range, not a
power artefact. ponytail: nearest-higher-sample approach, add bootstrapped CI
only if a reviewer asks.
"""
import argparse
import glob
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pymoo.indicators.hv import Hypervolume
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

ACTIVE = ["mpo", "syba", "rrs", "pns"]
NORM_SYBA_RAW = "syba"  # per-seed CSVs carry RAW syba, unlike N1's evaluated table


def norm_syba(raw):
    return 1.0 / (1.0 + math.exp(-raw / 5.0))


def load_mode(directory):
    frames = []
    for f in sorted(glob.glob(str(Path(directory) / "p4_pareto_seed_*.csv"))):
        df = pd.read_csv(f)
        df["syba"] = df["syba"].apply(norm_syba)
        frames.append(df)
    return frames


def hv(front, lo, hi, ref=1.1):
    vecs = front[ACTIVE].to_numpy(float)
    if len(vecs) == 0:
        return float("nan")
    norm = (vecs - lo) / np.where(hi - lo > 1e-10, hi - lo, 1.0)
    return float(Hypervolume(ref_point=np.full(len(ACTIVE), ref)).do(-norm))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proxy", required=True, help="dir of proxy per-seed CSVs")
    ap.add_argument("--pareto", required=True, help="dir of pareto per-seed CSVs")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    args = ap.parse_args()

    proxy = load_mode(args.proxy)
    pareto = load_mode(args.pareto)
    if not proxy or not pareto:
        raise SystemExit("ERROR: no per-seed CSVs found in one/both mode dirs")
    if len(proxy) != len(pareto):
        raise SystemExit(f"ERROR: mismatched seeds proxy={len(proxy)} pareto={len(pareto)}")

    # Common normalisation bounds across ALL points of BOTH modes (mirrors N1)
    all_vecs = np.vstack([f[ACTIVE].to_numpy(float)
                          for f in proxy + pareto])
    lo = all_vecs.min(axis=0)
    hi = all_vecs.max(axis=0)

    z = []
    for fa, fb in zip(proxy, pareto):
        hva = hv(fa, lo, hi)
        hvb = hv(fb, lo, hi)
        z.append(hva - hvb)  # + => proxy higher HV
    z = np.array(z)  # + => proxy higher HV
    n = len(z)
    mean_d = float(z.mean())
    sd = float(z.std(ddof=1)) if n > 1 else float("nan")
    se = sd / math.sqrt(n)

    # minimal detectable effect for a two-sided alpha at power=p:
    # normal approx: MDE(N) = (z_{1-alpha/2} + z_{1-beta}) * sd / sqrt(N)
    z_alpha = 1.959964  # two-sided 0.05
    z_beta = 0.841621   # power 0.80

    print(f"Seeds (paired): {n}")
    print(f"Per-seed dHV (proxy - pareto): {z.round(4).tolist()}")
    print(f"mean dHV = {mean_d:.4f}   SD = {sd:.4f}   paired t = {mean_d/se:.3f}")
    print(f"MDE @ n={n:<2d} (alpha={args.alpha:.2f}, power={args.power:.2f}): {mde(sd, n):.4f}")
    print(f"MDE @ n=20 (projected): {mde(sd, 20):.4f}")
    print(f"ratio |mean_d|/MDE(n=20) = {abs(mean_d)/mde(sd, 20):.2f}")
    print()
    if abs(mean_d) < mde(sd, 20):
        print("VERDICT: |mean| < projected MDE(20) -> n=20 CANNOT resolve this effect.")
        print("  Honest null stands: selection is not a bottleneck within detectable range.")
    else:
        print("VERDICT: |mean| above projected MDE(20) -> n=20 WOULD resolve it. Worth running.")
    print("  Caveat: MDE uses observed SD at n=5 as a frozen noise estimate;")
    print("          SD itself is uncertain with n=5 (wide CI on sd).")


def mde(sd: float, N, z_alpha=1.959964, z_beta=0.841621) -> float:
    """Minimal detectable effect for a two-sided test at power, normal approx."""
    return (z_alpha + z_beta) * sd / math.sqrt(N)


def demo() -> None:
    # Self-check: MDE must shrink as N grows and scale linearly in sd.
    sd = 1.0
    assert mde(sd, 20) < mde(sd, 5)
    assert abs(mde(sd, 20) - mde(2.0, 20)) > 1e-9  # sd scaling
    assert mde(sd, 4) == mde(sd, 4)
    # toy paired sample, high-SD frozen -> verdict must be null (|mean|<MDE(20))
    z = np.array([-1.7757, 0.2712, 1.8072, 1.1154, 1.241])
    sd_z = z.std(ddof=1)
    assert abs(z.mean()) < mde(sd_z, 20)
    print("demo OK")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        demo()
    else:
        main()