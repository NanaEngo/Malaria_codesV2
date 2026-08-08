#!/usr/bin/env python3
"""Diagnose grid-box containment of Vina rank-1 poses for PfClpP/2F6I pairs.

For each pair with a vina_out.pdbqt, report the rank-1 centroid, the number of
atoms outside the declared box, the max outside deviation per axis, and the
pose-to-triad distance. Prints a compact table to decide whether the box or the
containment gate needs adjustment.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
OUT = V5 / "results/vina_dock_2F6I_PfClpP_17"
CENTER = np.asarray([-24.276, 17.28, -2.901], dtype=float)
BOX = np.asarray([25.0, 25.0, 25.0], dtype=float)
LO = CENTER - BOX / 2
HI = CENTER + BOX / 2


def read_pose_model1(path: Path):
    coords = []
    mc = 0
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            mc += 1
            if mc > 1:
                break
            continue
        if line.startswith(("ATOM  ", "HETATM")) and mc == 1:
            try:
                coords.append(np.asarray([float(line[30:38]), float(line[38:46]), float(line[46:54])]))
            except ValueError:
                continue
    return np.asarray(coords)


def main() -> int:
    print(f"center: {CENTER.tolist()}  box: {BOX.tolist()}")
    print(f"{'pair':<20} {'atoms':>5} {'frac':>6} {'n_out':>5} {'max_dev':>8} {'centroid':>24}")
    for pair_dir in sorted(OUT.glob("PP-*_PfClpP")):
        out_pdbqt = pair_dir / "vina_out.pdbqt"
        if not out_pdbqt.is_file():
            print(f"{pair_dir.name:<20} NO OUTPUT")
            continue
        arr = read_pose_model1(out_pdbqt)
        outside_mask = (arr < LO).any(axis=1) | (arr > HI).any(axis=1)
        frac = float(1 - outside_mask.mean())
        n_out = int(outside_mask.sum())
        dev = np.maximum(LO - arr, 0) + np.maximum(arr - HI, 0)
        max_dev = float(dev.max()) if len(dev) else 0.0
        centroid = arr.mean(axis=0)
        print(f"{pair_dir.name:<20} {len(arr):>5} {frac:>6.3f} {n_out:>5} {max_dev:>8.2f} {np.round(centroid,1).tolist()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
