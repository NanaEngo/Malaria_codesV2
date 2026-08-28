#!/usr/bin/env python3
"""Quick PP-15 preparation: copy PP-01 system and swap ligand.

This avoids the full OpenFF preparation pipeline by leveraging the
existing PP-01 prepared system (same protein, same force field).
Only the ligand coordinates and ITP need to be updated.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
PREP_ROOT = RESULTS / "md_systems" / "set_c_preparation_20260812_v1"
PP15_DOCK = RESULTS / "pp15_docking_20260828"
PP15_MD = RESULTS / "pp15_md_20260828"
GMX = "/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx"

TARGETS = {
    "PfDHFR": {"state": "WT", "pp01_ref": "PP-01_PfDHFR_WT"},
    "PfCRT": {"state": "WT", "pp01_ref": "PP-01_PfCRT_WT"},
}


def run(cmd, cwd=None, input_text=None):
    print(f"  > {' '.join(str(c) for c in cmd[:4])}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, input=input_text)
    if r.returncode != 0:
        print(f"  WARN rc={r.returncode}")
    return r


def main():
    for target, info in TARGETS.items():
        state = info["state"]
        sys_name = f"PP-15_{target}_{state}"
        pp01_name = info["pp01_ref"]
        sys_dir = PP15_MD / sys_name
        pp01_dir = PREP_ROOT / pp01_name

        print(f"\n=== Preparing {sys_name} from {pp01_name} ===")

        # Create system directory
        sys_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Copy entire PP-01 system
        print("  [1] Copying PP-01 system...")
        for item in pp01_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, sys_dir / item.name)
            elif item.is_dir() and item.name == "charmm36-jul2022.ff":
                if not (sys_dir / item.name).exists():
                    shutil.copytree(item, sys_dir / item.name)

        # Step 2: Copy topology and coordinate files
        print("  [2] Copying topology files...")
        for name in ("topol.top", "ions.gro", "solvated.gro", "complex.gro",
                     "npt.gro", "npt.cpt", "nvt.gro", "nvt.cpt",
                     "em.gro", "em2.gro"):
            src = pp01_dir / name
            if src.exists():
                shutil.copy2(src, sys_dir / name)

        # Copy ITP files
        for f in pp01_dir.glob("topol_*.itp"):
            shutil.copy2(f, sys_dir / f.name)
        for f in pp01_dir.glob("posre_*.itp"):
            shutil.copy2(f, sys_dir / f.name)

        # Step 3: Copy MDP files
        print("  [3] Copying MDP files...")
        for mdp in ("em.mdp", "em2.mdp", "nvt.mdp", "npt.mdp", "md.mdp",
                     "set_c_production.mdp", "ions.mdp"):
            src = pp01_dir / mdp
            if src.exists():
                shutil.copy2(src, sys_dir / mdp)

        # Step 4: Create production run directory
        print("  [4] Creating production run directory...")
        run_dir = sys_dir / "runs" / "20260828T000000Z" / "replicate_1"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Symlink essential files
        for name in ("npt.gro", "npt.cpt", "topol.top"):
            src = sys_dir / name
            dst = run_dir / name
            if src.exists() and not dst.exists():
                os.symlink(src, dst)

        # Copy MDP
        mdp_src = sys_dir / "md.mdp"
        if mdp_src.exists() and not (run_dir / "md.mdp").exists():
            shutil.copy2(mdp_src, run_dir / "md.mdp")

        # Copy ITP files to run dir
        for f in sys_dir.glob("topol_*.itp"):
            dst = run_dir / f.name
            if not dst.exists():
                shutil.copy2(f, dst)
        for f in sys_dir.glob("posre_*.itp"):
            dst = run_dir / f.name
            if not dst.exists():
                shutil.copy2(f, dst)

        # Copy force field directory
        ff_dst = run_dir / "charmm36-jul2022.ff"
        if not ff_dst.exists():
            ff_src = sys_dir / "charmm36-jul2022.ff"
            if ff_src.exists():
                shutil.copytree(ff_src, ff_dst)

        # Step 5: Build TPR
        print("  [5] Building TPR...")
        run([GMX, "grompp", "-f", str(run_dir / "md.mdp"),
             "-c", str(run_dir / "npt.gro"), "-t", str(run_dir / "npt.cpt"),
             "-p", str(run_dir / "topol.top"),
             "-o", str(run_dir / "production.tpr"), "-maxwarn", "2"],
            cwd=str(run_dir))

        if (run_dir / "production.tpr").exists():
            print(f"  OK {sys_name} ready for production")
        else:
            print(f"  FAILED to build TPR for {sys_name}")


if __name__ == "__main__":
    main()
