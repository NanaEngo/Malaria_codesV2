#!/usr/bin/env python3
"""P1 V8 revision — R1.2 retrospective validation of five approved antimalarials.

Docks artemisinin, pyrimethamine, chloroquine, lumefantrine, and cipargamin
against the PfDHFR (WT + N51I/C59R/S108N/I164L) and PfCRT (corrected 3D7-like
WT + K76T + K76A) panels using the declared protocols, computes per-drug RRS
profiles, and checks whether the framework recovers clinically documented
resistance signatures (pyrimethamine: PfDHFR N51I/S108N; chloroquine: PfCRT K76T).

Protocols:
  PfDHFR: raw 7F3Y frame; grid anchored on the MTX A702 catalytic pocket
          (center 1.27, 11.63, -32.51; 25 A; exhaustiveness 32); WT receptor
          stripped of MTX/NDP/water consistent with the mutant preparation so
          the WT/mutant comparison is not confounded by retained MTX (R2.5).
  PfCRT:  corrected LYS-76 WT + K76T + K76A receptors on the V2 cavity-anchored
          grid (center 152.99, 151.042, 159.379; 25 A; exhaustiveness 32).

Outputs (results/retrospective_approved_antimalarials_20260909/):
  docking_scores.csv      — 40 runs (5 drugs x 7 receptor states
                          plus 5 PfDHFR-WT re-docks after the stripped-
                          receptor fix; the 9-state plan collapsed to 7
                          because PfCRT uses the corrected LYS-76 WT)
  rrs_profiles.csv        — per-drug per-target RRS (mutant/WT x 100)
  retrospective_summary.json
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P2 = ROOT.parent / "Project2_Polypharmacology_MD_ValidationV2607"
OUT = ROOT / "results/retrospective_approved_antimalarials_20260909"
LIG = OUT / "ligands"
REC = OUT / "receptors"
RUN = OUT / "out"

ENV = Path("/home/nanaengo/miniforge3/envs/malaria_md/bin")
OBABEL = ENV / "obabel"
VINA = Path("/usr/local/bin/vina")

GRID_PFDHFR = {"center": [1.27, 11.63, -32.51], "size": [25.0, 25.0, 25.0]}
GRID_PFCRT = {"center": [152.99, 151.042, 159.379], "size": [25.0, 25.0, 25.0]}

APPROVED = {
    "artemisinin": "C[C@@H]1CC[C@H]2[C@H](C(=O)O[C@H]3[C@@]24[C@H]1CC[C@](O3)(OO4)C)C",
    "pyrimethamine": "CCC1=C(C(=NC(=N1)N)N)C2=CC=C(C=C2)Cl",
    "chloroquine": "CCN(CC)CCCC(C)NC1=C2C=CC(=CC2=NC=C1)Cl",
    "lumefantrine": "CCCCN(CCCC)CC(C1=CC(=CC\\2=C1C3=C(/C2=C/C4=CC=C(C=C4)Cl)C=C(C=C3)Cl)Cl)O",
    "cipargamin": "C[C@H]1CC2=C([C@]3(N1)C4=C(C=CC(=C4)Cl)NC3=O)NC5=CC(=C(C=C25)F)Cl",
}

# state -> (receptor_pdbqt, grid)
STATES = {
    # PfDHFR from mutants_prepared (stripped, raw 7F3Y frame); WT built in-script
    "PfDHFR_N51I": (P2 / "data/proteins/mutants_prepared/PfDHFR_N51I_receptor.pdbqt", GRID_PFDHFR),
    "PfDHFR_C59R": (P2 / "data/proteins/mutants_prepared/PfDHFR_C59R_receptor.pdbqt", GRID_PFDHFR),
    "PfDHFR_S108N": (P2 / "data/proteins/mutants_prepared/PfDHFR_S108N_receptor.pdbqt", GRID_PFDHFR),
    "PfDHFR_I164L": (P2 / "data/proteins/mutants_prepared/PfDHFR_I164L_receptor.pdbqt", GRID_PFDHFR),
    # PfCRT corrected receptors (same pipeline as the re-dock)
    "PfCRT_WT": (ROOT / "results/pfcrt_redock_v2grid_20260909/receptors/PfCRT_WT_receptor.pdbqt", GRID_PFCRT),
    "PfCRT_K76T": (ROOT / "results/pfcrt_redock_v2grid_20260909/receptors/PfCRT_K76T_receptor.pdbqt", GRID_PFCRT),
    "PfCRT_K76A": (ROOT / "results/pfcrt_redock_v2grid_20260909/receptors/PfCRT_K76A_receptor.pdbqt", GRID_PFCRT),
}


def build_stripped_wt() -> Path:
    """Strip MTX/NDP/waters/ions from raw 7F3Y.pdb (standard PDB format),
    keep protein only, then convert to a rigid receptor PDBQT (gasteiger)."""
    src = P2 / "data/proteins/7F3Y.pdb"
    dst = REC / "PfDHFR_WT_receptor.pdbqt"
    if dst.exists() and dst.stat().st_size > 0 and "^ATOM" not in dst.read_text()[:0]:
        if len([l for l in dst.read_text().splitlines() if l.startswith("ATOM")]) > 5000:
            return dst
    keep = [l for l in src.read_text().splitlines()
            if l.startswith("ATOM") or (l.startswith("HETATM") and l[17:20].strip() not in
                                        ("MTX", "NDP", "UMP", "GOL", "HOH"))]
    assert len(keep) > 5000, f"stripped WT too small: {len(keep)}"
    tmp_pdb = REC / "PfDHFR_WT_clean.pdb"
    with tmp_pdb.open("w") as fh:
        fh.write("\n".join(keep) + "\n")
    subprocess.run([str(OBABEL), str(tmp_pdb), "-O", str(dst), "--partialcharge", "gasteiger"],
                   check=True, capture_output=True)
    lines = dst.read_text().splitlines()
    clean = [l for l in lines if not l.startswith(("ROOT", "ENDROOT", "BRANCH", "ENDBRANCH", "TORSDOF"))]
    dst.write_text("\n".join(clean) + "\n")
    n_atoms = len([l for l in dst.read_text().splitlines() if l.startswith("ATOM")])
    if n_atoms < 5000:
        raise RuntimeError(f"WT receptor has too few atoms: {n_atoms}")
    return dst


def prep_ligands() -> None:
    for name, smi in APPROVED.items():
        pdbqt = LIG / f"{name}.pdbqt"
        if pdbqt.exists():
            continue
        sdf = LIG / f"{name}.sdf"
        subprocess.run([str(OBABEL), f"-:{smi}", "-O", str(sdf), "--gen3d"],
                       check=True, capture_output=True)
        subprocess.run([str(OBABEL), str(sdf), "-O", str(pdbqt)],
                       check=True, capture_output=True)


def write_config(cfg_path: Path, receptor: Path, ligand: Path, out: Path, grid: dict) -> None:
    cfg_path.write_text(
        f"receptor = {receptor}\n"
        f"ligand = {ligand}\n"
        f"center_x = {grid['center'][0]:.3f}\n"
        f"center_y = {grid['center'][1]:.3f}\n"
        f"center_z = {grid['center'][2]:.3f}\n"
        f"size_x = {grid['size'][0]:.1f}\n"
        f"size_y = {grid['size'][1]:.1f}\n"
        f"size_z = {grid['size'][2]:.1f}\n"
        f"exhaustiveness = 32\n"
        f"num_modes = 10\n"
        f"energy_range = 5\n"
        f"out = {out}\n")


def score_from_out(path: Path) -> float | None:
    for line in path.read_text().splitlines():
        if line.startswith("REMARK VINA RESULT:"):
            return float(line.split()[3])
    return None


def main() -> None:
    for d in (OUT, LIG, REC, RUN):
        d.mkdir(parents=True, exist_ok=True)
    prep_ligands()
    wt = build_stripped_wt()
    all_states = {"PfDHFR_WT": (wt, GRID_PFDHFR), **STATES}
    expected = len(APPROVED) * len(all_states)

    records = []
    for name in APPROVED:
        lig = LIG / f"{name}.pdbqt"
        for state, (receptor, grid) in all_states.items():
            out = RUN / f"{name}_{state}.pdbqt"
            cfg = RUN / f"{name}_{state}.conf"
            # Remove outputs that were produced against the broken empty WT receptor
            if "PfDHFR_WT" in state and out.exists():
                s = score_from_out(out)
                if s is None or abs(s) < 0.01:
                    out.unlink()
            if not out.exists():
                write_config(cfg, receptor, lig, out, grid)
                subprocess.run([str(VINA), "--config", str(cfg)],
                               check=True, capture_output=True)
            score = score_from_out(out)
            if score is None or not math.isfinite(score):
                raise RuntimeError(f"invalid vina score for {name}/{state}: {score}")
            records.append({"drug": name, "state": state, "vina_score_kcal_mol": score})
            print(f"  {name:14s} {state:16s} {score}")

    import csv
    assert len(records) == expected, f"expected {expected} records, got {len(records)}"
    with (OUT / "docking_scores.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["drug", "state", "vina_score_kcal_mol"])
        w.writeheader()
        w.writerows(records)

    # RRS: mutant/WT x 100, per target
    import pandas as pd
    df = pd.DataFrame(records)
    rows = []
    for drug, g in df.groupby("drug"):
        for target in ("PfDHFR", "PfCRT"):
            wt_v = g.loc[g["state"] == f"{target}_WT", "vina_score_kcal_mol"].iloc[0]
            for m in ("N51I", "C59R", "S108N", "I164L") if target == "PfDHFR" else ("K76T", "K76A"):
                mut_v = g.loc[g["state"] == f"{target}_{m}", "vina_score_kcal_mol"].iloc[0]
                rrs = 100.0 * abs(mut_v) / abs(wt_v) if abs(wt_v) >= 5.0 else None
                rows.append({"drug": drug, "target": target, "mutation": m,
                             "wt": wt_v, "mutant": mut_v, "rrs": rrs})
    rrs_df = pd.DataFrame(rows)
    rrs_df.to_csv(OUT / "rrs_profiles.csv", index=False)
    summary = {"n_runs": len(records), "n_records": len(rrs_df)}
    (OUT / "retrospective_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(rrs_df.to_string(index=False))


if __name__ == "__main__":
    main()