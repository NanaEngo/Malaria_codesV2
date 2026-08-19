#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Dump per-block accumulator arrays from a PyQMC 0.8.1 hdf5 output file.

Usage: python p4_qmc_dump_hdf5.py <file.hdf5>
Prints the shape and per-block values of every accumulator group so we can see
whether energies drift block-to-block (population collapse / walker collapse)
or are stable.
"""

import sys

import h5py
import numpy as np


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: p4_qmc_dump_hdf5.py <file.hdf5>")
    path = sys.argv[1]
    with h5py.File(path, "r") as f:
        print(f"file: {path}")
        print(f"top-level keys: {sorted(f.keys())}")
        for key in sorted(f.keys()):
            obj = f[key]
            if isinstance(obj, h5py.Dataset):
                arr = np.asarray(obj[:])
                print(f"\n[{key}] shape={arr.shape}")
                if arr.ndim == 1:
                    print(f"  values: {arr}")
                elif arr.ndim >= 2:
                    # nblocks is the leading axis for accumulators
                    block_means = arr.mean(axis=tuple(range(1, arr.ndim)))
                    print(f"  block means: {block_means}")
                    # Avoid flooding: only print raw values when the dataset is small
                    nraw = arr.size
                    if nraw <= 1200:
                        print(f"  raw (first 3 blocks): {arr[:3]}")
                    else:
                        # print first-block flat stats for high-dim datasets (e.g.
                        # configs (nblocks, nconf, nelec, 3) or energygrad2)
                        flat = arr.reshape(arr.shape[0], -1)
                        print(f"  per-block min/mean/max: "
                              f"{[round(float(v), 4) for v in flat.min(axis=1)]} / "
                              f"{[round(float(v), 4) for v in flat.mean(axis=1)]} / "
                              f"{[round(float(v), 4) for v in flat.max(axis=1)]}")


if __name__ == "__main__":
    main()
