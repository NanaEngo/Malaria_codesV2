#!/usr/bin/env python3
"""Detailed per-axis geometry of a Vina rank-1 pose vs the declared box.

Usage: p1_v5_vina_pose_detail.py <pair_dir_name>
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
OUT = V5 / "results/vina_dock_2F6I_PfClpP_17"
CENTER = np.asarray([-24.276, 17.28, -2.901], dtype=float)
BOX = np.asarray([28.0, 28.0, 28.0], dtype=float)
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
    name = sys.argv[1] if len(sys.argv) > 1 else "PP-02_PfClpP"
    arr = read_pose_model1(OUT / name / "vina_out.pdbqt")
    print(f"{name}: {len(arr)} atoms")
    print(f"box: lo={LO}  hi={HI}")
    print(f"min: {arr.min(axis=0)}   max: {arr.max(axis=0)}")
    outside = (arr < LO).any(axis=1) | (arr > HI).any(axis=1)
    print(f"outside atoms: {outside.sum()}")
    dev = np.maximum(LO - arr, 0) + np.maximum(arr - HI, 0)
    if outside.any():
        print(f"max deviation per axis: {dev.max(axis=0)}")
        print("outside atom coords:")
        for a in arr[outside]:
            print("  ", np.round(a, 2))
    # distance to chain A triad atoms
    triad = np.asarray([[-22.232, 15.984, -2.161], [-26.372, 18.249, -4.879], [-24.225, 17.608, -1.663]])
    dmin = min(float(np.min(np.linalg.norm(arr - t, axis=1))) for t in triad)
    print(f"pose-min distance to chain A triad atoms: {dmin:.2f} A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
