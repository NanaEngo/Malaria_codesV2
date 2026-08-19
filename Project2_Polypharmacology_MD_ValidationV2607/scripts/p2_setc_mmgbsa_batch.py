#!/usr/bin/env python3
"""Batch MM-GBSA (Tier 0) on the 16 Set-C pilot trajectories.

Protocol matches the canonical P2 manuscript Methods: gmx_MMPBSA v1.5,
OBC2 generalised Born model (igb=5), 0.15 M ionic strength, dielectric
80.0 (solvent) / 1.0 (protein), snapshots every 100 ps across the 10 ns
production trajectories (100 frames). One gmx_MMPBSA run per system is
launched in the background; each uses the default 4 processors.

Only systems whose QC passed (set_c_trajectory_qc_pilot.csv == PASS) and
whose FINAL_RESULTS_MMPBSA.dat is not already present are launched, so the
script is idempotent and safe to re-run.

Outputs: results/set_c_md/mmgbsa_20260819/<SYSTEM>/FINAL_RESULTS_MMPBSA.dat
plus a per-system status JSON.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP = ROOT / "results" / "md_systems" / "set_c_preparation_20260812_v1"
QC_CSV = ROOT / "results" / "set_c_md" / "set_c_trajectory_qc_pilot.csv"
OUT_ROOT = ROOT / "results" / "set_c_md" / "mmgbsa_20260819"
ENV = "malaria_md"

INPUT_TEMPLATE = """&general
  sys_name="{sys_name}"
  startframe=1
  endframe=1000
  interval=10
  keep_files=0
/
&gb
  igb=5
  saltcon=0.150
/
"""


def find_replicate(system_name: str) -> Path:
    """Return the replicate_1 dir containing production.tpr/xtc/topol.top."""
    sys_dir = PREP / system_name
    for run_dir in sorted(sys_dir.glob("runs/*/replicate_1")):
        if (run_dir / "production.tpr").is_file() and (
            run_dir / "production.xtc"
        ).is_file() and (run_dir / "topol.top").is_file():
            return run_dir
    raise FileNotFoundError(f"no replicate_1 with production files for {system_name}")


def build_index(rep: Path, out_ndx: Path) -> tuple[int, int]:
    """Create an index with receptor (Protein) and ligand groups.

    The ligand is detected dynamically from the make_ndx group listing: the
    smallest non-protein, non-water, non-ion group (typically MOL0). Returns
    the (receptor, ligand) group numbers in the written index.
    """
    proc = subprocess.run(
        ["mamba", "run", "-n", ENV, "gmx_mpi", "make_ndx", "-f", str(rep / "production.tpr"), "-o", "/dev/null"],
        input="q\n",
        capture_output=True,
        text=True,
        cwd=str(rep),
    )
    listing = proc.stdout
    # Parse "  N Name : X atoms" lines
    groups: dict[int, str] = {}
    atoms: dict[int, int] = {}
    for line in listing.splitlines():
        m = re.match(r"\s*(\d+)\s+(\S+)\s+:\s*(\d+)\s+atoms", line)
        if m:
            groups[int(m.group(1))] = m.group(2)
            atoms[int(m.group(1))] = int(m.group(3))
    # receptor = Protein
    receptor = next((i for i, n in groups.items() if n == "Protein"), None)
    if receptor is None:
        raise RuntimeError(f"no Protein group for {rep}")
    # ligand = prefer MOL0/UNL/LIG, else smallest non-protein/water/ion group
    skip = {"Protein", "Protein-H", "C-alpha", "Backbone", "MainChain", "MainChain+Cb",
            "MainChain+H", "SideChain", "SideChain-H", "Prot-Masses", "non-Protein",
            "Other", "NA", "CL", "Water", "SOL", "non-Water", "Ion", "Water_and_ions",
            "System"}
    preferred = next((i for i, n in groups.items() if n in ("MOL0", "UNL", "LIG")), None)
    if preferred is not None:
        ligand = preferred
    else:
        ligand = None
        for i, name in sorted(groups.items()):
            if name in skip:
                continue
            if ligand is None or atoms[i] < atoms[ligand]:
                ligand = i
    if ligand is None:
        raise RuntimeError(f"no ligand group detected for {rep}")
    # Build a clean two-group index via make_ndx commands
    cmds = f"{receptor}\nname {receptor} receptor\n{ligand}\nname {ligand} ligand\nq\n"
    proc2 = subprocess.run(
        ["mamba", "run", "-n", ENV, "gmx_mpi", "make_ndx", "-f", str(rep / "production.tpr"), "-o", str(out_ndx)],
        input=cmds,
        capture_output=True,
        text=True,
        cwd=str(rep),
    )
    # Determine the group numbers of receptor/ligand in the written ndx
    text = out_ndx.read_text()
    names = re.findall(r"\[ ([^\]]+) \]", text)
    rec_idx = names.index("receptor")
    lig_idx = names.index("ligand")
    return rec_idx, lig_idx


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(QC_CSV)))
    targets = [r for r in rows if r["qc_status"] == "PASS"]
    if not targets:
        print("No PASS systems found in QC CSV", file=sys.stderr)
        return 1
    launched = []
    for r in targets:
        sys_name = f"{r['set_c_id']}_{r['target']}_{r['mutation']}"
        out_dir = OUT_ROOT / sys_name
        out_dir.mkdir(parents=True, exist_ok=True)
        final = out_dir / "FINAL_RESULTS_MMPBSA.dat"
        if final.is_file() and final.stat().st_size > 0:
            print(f"skip {sys_name}: already done")
            continue
        # skip if a run is already active for this system (launch_status pid alive)
        status_json = out_dir / "launch_status.json"
        if status_json.is_file():
            try:
                st = json.loads(status_json.read_text())
                pid = int(st.get("pid", -1))
                if pid > 0 and Path(f"/proc/{pid}").exists():
                    print(f"skip {sys_name}: already running (pid {pid})")
                    continue
            except (ValueError, OSError, json.JSONDecodeError):
                pass
        try:
            rep = find_replicate(sys_name)
        except FileNotFoundError as e:
            print(f"ERROR {sys_name}: {e}", file=sys.stderr)
            continue
        # input file
        (out_dir / "mmpbsa.in").write_text(INPUT_TEMPLATE.format(sys_name=sys_name))
        # index
        ndx = out_dir / "complex.ndx"
        if not ndx.is_file():
            try:
                rec_idx, lig_idx = build_index(rep, ndx)
            except RuntimeError as e:
                print(f"ERROR {sys_name}: index: {e}", file=sys.stderr)
                continue
        else:
            names = re.findall(r"\[ ([^\]]+) \]", ndx.read_text())
            rec_idx, lig_idx = names.index("receptor"), names.index("ligand")
        # launch
        cmd = [
            "mamba", "run", "-n", ENV, "gmx_MMPBSA", "-O",
            "-i", str(out_dir / "mmpbsa.in"),
            "-o", str(final),
            "-cs", str(rep / "production.tpr"),
            "-ct", str(rep / "production.xtc"),
            "-cp", str(rep / "topol.top"),
            "-ci", str(ndx),
            "-cg", str(rec_idx), str(lig_idx),
            "-nogui",
        ]
        logf = open(out_dir / "run.log", "w")
        proc = subprocess.Popen(cmd, cwd=str(rep), stdout=logf, stderr=subprocess.STDOUT,
                                start_new_session=True)
        status = {
            "system": sys_name,
            "pid": proc.pid,
            "launched_utc": datetime.now(timezone.utc).isoformat(),
            "out_dir": str(out_dir),
            "replicate": str(rep),
            "index_groups": {"receptor": rec_idx, "ligand": lig_idx},
            "input": INPUT_TEMPLATE.format(sys_name=sys_name),
        }
        (out_dir / "launch_status.json").write_text(json.dumps(status, indent=2) + "\n")
        launched.append(sys_name)
        print(f"launched {sys_name} (pid {proc.pid}, groups {rec_idx}/{lig_idx})")
    summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "n_launched": len(launched),
        "systems": launched,
    }
    (OUT_ROOT / "batch_launch_manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nLaunched {len(launched)} systems. See {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
