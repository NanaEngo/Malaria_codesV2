#!/usr/bin/env python3
"""Re-run MM-GBSA for the two systems whose trajectories split across the
periodic boundary (PBC).

Root cause diagnosed 2026-08-19: for PP-02_PfDHFR_WT (60/1001 frames) and
PP-02_PfCRT_K76A (513/1001 frames) the protein crossed the PBC boundary, so
the cpptraj/AMBER conversion produced a handful of frames with catastrophic
bond/Urey-Bradley energies (UB ~1e7 kcal/mol, RMS ~3e3 Angstrom), and sander
wrote ``*************`` (overflow) which gmx_MMPBSA could not parse.

Fix: ``gmx trjconv -pbc whole`` (already applied, producing
``production_whole.xtc`` in each replicate dir), then re-run gmx_MMPBSA with
``-ct production_whole.xtc``. All other 14 systems have 0 split frames and are
unaffected.

Protocol unchanged: gmx_MMPBSA v1.5, OBC2 (igb=5), 0.15 M, 100 frames
(every 100 ps over 10 ns), receptor/ligand index groups from launch_status.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "results" / "set_c_md" / "mmgbsa_20260819"
ENV = "malaria_md"

FAILED_SYSTEMS = ["PP-02_PfDHFR_WT", "PP-02_PfCRT_K76A"]


def main() -> int:
    launched = []
    for sys_name in FAILED_SYSTEMS:
        out_dir = OUT_ROOT / sys_name
        status = json.loads((out_dir / "launch_status.json").read_text())
        rep = Path(status["replicate"])
        whole = rep / "production_whole.xtc"
        if not whole.is_file():
            print(f"ERROR {sys_name}: {whole} missing; run trjconv -pbc whole first",
                  flush=True)
            continue
        final = out_dir / "FINAL_RESULTS_MMPBSA.dat"
        rec_idx, lig_idx = status["index_groups"]["receptor"], status["index_groups"]["ligand"]
        # remove stale retained intermediates from the failed run
        for stale in rep.glob("_GMXMMPBSA_*"):
            try:
                stale.unlink()
            except OSError:
                pass
        cmd = [
            "mamba", "run", "-n", ENV, "gmx_MMPBSA", "-O",
            "-i", str(out_dir / "mmpbsa.in"),
            "-o", str(final),
            "-cs", str(rep / "production.tpr"),
            "-ct", str(whole),
            "-cp", str(rep / "topol.top"),
            "-ci", str(out_dir / "complex.ndx"),
            "-cg", str(rec_idx), str(lig_idx),
            "-nogui",
        ]
        logf = open(out_dir / "run_pbc_fixed.log", "w")
        proc = subprocess.Popen(cmd, cwd=str(rep), stdout=logf,
                                stderr=subprocess.STDOUT, start_new_session=True)
        status["pbc_fixed"] = True
        status["trajectory"] = str(whole)
        status["rerun_pid"] = proc.pid
        status["rerun_launched_utc"] = datetime.now(timezone.utc).isoformat()
        status["rerun_note"] = ("PBC split (protein across boundary) caused BOND/UB "
                                "overflow in the first pass; re-run on "
                                "production_whole.xtc (gmx trjconv -pbc whole).")
        (out_dir / "launch_status.json").write_text(json.dumps(status, indent=2) + "\n")
        launched.append(sys_name)
        print(f"launched {sys_name} (pid {proc.pid}, -ct {whole.name})", flush=True)
    print(f"\nLaunched {len(launched)} PBC-fixed re-runs in {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
