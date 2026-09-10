#!/usr/bin/env python3
"""P1 V8 revision — R2.3/R2.5 PfCRT corrected-receptor re-docking.

Rebuilds the three PfCRT receptors (WT LYS-76, K76T, K76A) plus a
pipeline-processed WT null (side chain stripped, no mutation) from the same
corrected parent (PfCRT_WT.pdb), prepares all four with the project's OpenBabel
Gasteiger protocol, and docks the 17 Set-C ligands on the V2 grid
(center 152.99, 151.042, 159.379; 25 A; exhaustiveness 32; num_modes 10).

Outputs:
  results/pfcrt_redock_v2grid_20260909/
    receptors/  (4 PDBQTs)
    ligands/    (17 PDBQTs, symlinked)
    out/        (per receptor per ligand vina output)
    scores.csv  (candidate, receptor, affinity)
    manifest.json (hashes, config, protocol)
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # P1 project dir
P2 = ROOT.parent / "Project2_Polypharmacology_MD_ValidationV2607"

VINA = "/usr/local/bin/vina"
OBABEL = "/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel"

GRID = {"center": [152.99, 151.042, 159.379], "size": [25.0, 25.0, 25.0]}
EXHAUSTIVENESS = 32
NUM_MODES = 10
ENERGY_RANGE = 5

PARENT_PDB = P2 / "scripts/data/proteins/PfCRT_WT.pdb"  # corrected LYS-76, 6UKJ frame
MUTATE = P2 / "scripts/mutate_pdb.py"
LIGANDS = P2 / "results/docking/ligand_pdbqt"  # rank01..rank17 = PP-01..PP-17
OUT = ROOT / "results/pfcrt_redock_v2grid_20260909"

RECEPTORS = {  # key -> (mutation args or None, label)
    "WT": (None, "corrected LYS-76 wild-type (full side chain)"),
    "K76T": (("K", "T"), "K76T mutant (side chain stripped, per mutate_pdb.py)"),
    "K76A": (("K", "A"), "K76A mutant (side chain stripped, per mutate_pdb.py)"),
    "NULL": (("K", "K"), "pipeline-processed WT null (side chain stripped, no mutation)"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(f"FAILED: {' '.join(cmd[:5])}...\n{r.stderr[-800:]}\n")
        raise SystemExit(1)
    return r


def main() -> None:
    assert Path(VINA).exists() or shutil.which(VINA), "vina not found"
    (OUT / "receptors").mkdir(parents=True, exist_ok=True)
    (OUT / "ligands").mkdir(parents=True, exist_ok=True)
    (OUT / "out").mkdir(parents=True, exist_ok=True)

    # 1. Rebuild receptors from the same corrected parent.
    receptor_hashes: dict[str, str] = {}
    for key, (mut, _label) in RECEPTORS.items():
        if mut is None:
            pdb_in = PARENT_PDB
        else:
            pdb_in = OUT / "receptors" / f"PfCRT_{key}_parent.pdb"
            r = run([sys.executable, str(MUTATE), "--pdb", str(PARENT_PDB),
                     "--chain", "A", "--position", "76",
                     "--from", mut[0], "--to", mut[1],
                     "--output", str(pdb_in)])
            if "WARNING" in r.stdout and "found" in r.stdout:
                sys.stderr.write(r.stdout)
        pdbqt = OUT / "receptors" / f"PfCRT_{key}_receptor.pdbqt"
        run([OBABEL, str(pdb_in), "-opdbqt", "-O", str(pdbqt),
             "--partialcharge", "gasteiger"])
        # Vina rigid receptors must not carry ROOT/BRANCH torsion tags.
        lines = [ln for ln in pdbqt.read_text().splitlines()
                 if not ln.startswith(("ROOT", "BRANCH", "ENDROOT", "TORSDOF"))]
        pdbqt.write_text("\n".join(lines) + "\n")
        receptor_hashes[key] = sha256(pdbqt)
        print(f"  receptor {key}: {pdbqt.name} ok")

    # 2. Symlink the 17 ligands (rank01..rank17 == PP-01..PP-17 by p2_source_rank).
    scores: list[dict] = []
    for i in range(1, 18):
        cand = f"PP-{i:02d}"
        src = LIGANDS / f"rank{i:02d}_ligand.pdbqt"
        assert src.exists(), src
        lig = OUT / "ligands" / f"{cand}_ligand.pdbqt"
        if not lig.exists():
            lig.symlink_to(src)

    # 3. Dock.
    for key in RECEPTORS:
        rec_pdbqt = OUT / "receptors" / f"PfCRT_{key}_receptor.pdbqt"
        for i in range(1, 18):
            cand = f"PP-{i:02d}"
            lig = OUT / "ligands" / f"{cand}_ligand.pdbqt"
            out_pdbqt = OUT / "out" / f"{cand}_{key}_out.pdbqt"
            log = OUT / "out" / f"{cand}_{key}_log.txt"
            conf = OUT / "out" / f"{cand}_{key}_conf.txt"
            conf.write_text(
                f"receptor = {rec_pdbqt}\n"
                f"ligand = {lig}\n"
                f"center_x = {GRID['center'][0]:.3f}\n"
                f"center_y = {GRID['center'][1]:.3f}\n"
                f"center_z = {GRID['center'][2]:.3f}\n"
                f"size_x = {GRID['size'][0]:.1f}\n"
                f"size_y = {GRID['size'][1]:.1f}\n"
                f"size_z = {GRID['size'][2]:.1f}\n"
                f"exhaustiveness = {EXHAUSTIVENESS}\n"
                f"num_modes = {NUM_MODES}\n"
                f"energy_range = {ENERGY_RANGE}\n"
                f"out = {out_pdbqt}\n"
            )
            r = run([VINA, "--config", str(conf)])
            log.write_text(r.stdout)
            aff = None
            for line in r.stdout.splitlines():
                parts = line.split()
                if len(parts) == 4 and parts[0] == "1":
                    try:
                        aff = float(parts[1])
                    except ValueError:
                        pass
                    break
            scores.append({"candidate": cand, "receptor": key, "affinity": aff})
            print(f"  {cand} {key}: {aff}")

    # 4. Emit scores + manifest.
    import csv
    with (OUT / "scores.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["candidate", "receptor", "affinity"])
        w.writeheader()
        w.writerows(scores)

    manifest = {
        "schema": "p1-r23-pfcrt-redock/v1",
        "date_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "purpose": "R2.3 corrected-receptor PfCRT re-dock + R2.5 pipeline-null control",
        "parent_receptor": {"path": str(PARENT_PDB.relative_to(P2.parent)),
                            "sha256": sha256(PARENT_PDB),
                            "note": "corrected 3D7-like wild-type (LYS-76), 6UKJ frame"},
        "mutation_tool": "scripts/mutate_pdb.py (backbone N/CA/C/O + CB retained; side chain removed)",
        "receptor_prep": "OpenBabel -opdbqt --partialcharge gasteiger (project protocol)",
        "grid": {"center": GRID["center"], "size": GRID["size"], "source": "V2-corrected grid; P2Rank top pocket 5.7 A from center; residue 76 CA 11.2 A from center"},
        "ligands": {"path": str(LIGANDS.relative_to(P2.parent)), "mapping": "rankNN = PP-NN by p2_source_rank"},
        "vina": {"version": VINA, "exhaustiveness": EXHAUSTIVENESS, "num_modes": NUM_MODES, "energy_range": ENERGY_RANGE},
        "receptor_sha256": receptor_hashes,
        "scores": str((OUT / "scores.csv").relative_to(ROOT)),
        "status": "COMPUTED",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(OUT), "rows": len(scores)}, indent=2))


if __name__ == "__main__":
    main()