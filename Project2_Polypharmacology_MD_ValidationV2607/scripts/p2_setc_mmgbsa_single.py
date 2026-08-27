#!/usr/bin/env python3
"""Single-system MM-GBSA mirroring scripts/p2_setc_mmgbsa_batch.py protocol verbatim.

Usage: python p2_single_mmgbsa.py <SYSTEM_NAME> <RUN_DIR>
Out: results/set_c_md/single_rerun_20260825/mmgbsa/<SYSTEM>/
"""
import csv
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607")
OUT_ROOT = Path(os.environ.get(
    "P2_MMGBSA_OUT_ROOT",
    str(ROOT / "results" / "set_c_md" / "single_rerun_20260825" / "mmgbsa"),
))
ENV = "malaria_md"

INPUT_TEMPLATE = """&general
  sys_name="{sys_name}"
  startframe=1
  endframe={endframe}
  interval=10
  keep_files=0
/
&gb
  igb=5
  saltcon=0.150
/
"""


def build_index(rep: Path, out_ndx: Path):
    proc = subprocess.run(
        ["mamba", "run", "-n", ENV, "gmx_mpi", "make_ndx", "-f", str(rep / "production.tpr"), "-o", "/dev/null"],
        input="q\n", capture_output=True, text=True, cwd=str(rep),
    )
    groups: dict[int, str] = {}
    atoms: dict[int, int] = {}
    for line in proc.stdout.splitlines():
        m = re.match(r"\s*(\d+)\s+(\S+)\s+:\s*(\d+)\s+atoms", line)
        if m:
            groups[int(m.group(1))] = m.group(2)
            atoms[int(m.group(1))] = int(m.group(3))
    receptor = next((i for i, n in groups.items() if n == "Protein"), None)
    if receptor is None:
        raise RuntimeError(f"no Protein group for {rep}")
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
    cmds = f"{receptor}\nname {receptor} receptor\n{ligand}\nname {ligand} ligand\nq\n"
    subprocess.run(
        ["mamba", "run", "-n", ENV, "gmx_mpi", "make_ndx", "-f", str(rep / "production.tpr"), "-o", str(out_ndx)],
        input=cmds, capture_output=True, text=True, cwd=str(rep), check=True,
    )
    names = re.findall(r"\[ ([^\]]+) \]", out_ndx.read_text())
    return names.index("receptor"), names.index("ligand")


def validate_timeseries(path: Path) -> dict:
    """Reject parser-successful outputs with unphysical bonded energies."""
    sections = {"Complex Energy Terms": "complex", "Receptor Energy Terms": "receptor", "Ligand Energy Terms": "ligand", "Delta Energy Terms": "delta"}
    records: dict[str, list[dict[str, float | int]]] = {name: [] for name in sections.values()}
    section = None
    with path.open(newline="") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            title = row[0].strip()
            if title in sections:
                section = sections[title]
                continue
            if section is None or row[0].strip() == "Frame #" or not row[0].strip().lstrip("-").isdigit():
                continue
            try:
                records[section].append({
                    "frame": int(row[0]),
                    "BOND": float(row[1]),
                    "UB": float(row[4]),
                    "TOTAL": float(row[15]),
                })
            except (IndexError, ValueError):
                records[section].append({"frame": int(row[0]), "BOND": math.inf, "UB": math.inf, "TOTAL": math.inf})

    threshold = 100_000.0
    anomalous = {
        section: [row for row in rows if not all(math.isfinite(float(row[key])) for key in ("BOND", "UB", "TOTAL"))
                  or abs(float(row["BOND"])) > threshold or abs(float(row["UB"])) > threshold]
        for section, rows in records.items()
    }
    checked = {section: len(rows) for section, rows in records.items()}
    failures = {section: {"count": len(rows), "frames": [row["frame"] for row in rows],
                          "max_abs_bond": max((abs(float(row["BOND"])) for row in rows), default=0.0),
                          "max_abs_ub": max((abs(float(row["UB"])) for row in rows), default=0.0)}
                for section, rows in anomalous.items() if rows}
    return {
        "status": "FAILED_NUMERICAL_QC" if failures else "PASS",
        "reportable": not failures,
        "threshold_kcal_mol": threshold,
        "checked_rows": checked,
        "anomalous_sections": failures,
    }


def main() -> int:
    sys_name, rep_rel = sys.argv[1], sys.argv[2]
    rep = Path(rep_rel).resolve()
    out_dir = OUT_ROOT / sys_name
    out_dir.mkdir(parents=True, exist_ok=True)
    final = out_dir / "FINAL_RESULTS_MMPBSA.dat"
    endframe = int(os.environ.get("P2_MMGBSA_ENDFRAME", "1000"))
    if endframe < 1:
        raise ValueError("P2_MMGBSA_ENDFRAME must be positive")
    if final.is_file() and final.stat().st_size > 0:
        print(f"skip {sys_name}: already done")
        return 0
    input_text = INPUT_TEMPLATE.format(sys_name=sys_name, endframe=endframe)
    (out_dir / "mmpbsa.in").write_text(input_text)
    ndx = out_dir / "complex.ndx"
    rec_idx, lig_idx = build_index(rep, ndx)
    cmd = [
        "mamba", "run", "-n", ENV, "gmx_MMPBSA", "-O",
        "-i", str(out_dir / "mmpbsa.in"),
        "-o", str(final),
        # additive vs batch protocol: per-frame energy dump for convergence analysis
        # (energetics unchanged; declared deviation recorded in launch_status.json)
        "-eo", str(out_dir / "mmgbsa_timeseries.csv"),
        "-cs", str(rep / "production.tpr"),
        "-ct", str(rep / "production.xtc"),
        "-cp", str(rep / "topol.top"),
        "-ci", str(ndx),
        "-cg", str(rec_idx), str(lig_idx),
        "-nogui",
    ]
    status = {
        "system": sys_name,
        "launched_utc": datetime.now(timezone.utc).isoformat(),
        "out_dir": str(out_dir),
        "replicate": str(rep),
        "index_groups": {"receptor": rec_idx, "ligand": lig_idx},
        "input": input_text,
        "protocol": f"identical to scripts/p2_setc_mmgbsa_batch.py (gmx_MMPBSA v1.5, GB OBC2 igb=5, saltcon 0.15 M, frames 1-{endframe} interval 10); declared additive deviation: -eo per-frame energy CSV for convergence analysis",
    }
    (out_dir / "launch_status.json").write_text(json.dumps(status, indent=2) + "\n")
    logf = open(out_dir / "run.log", "w")
    proc = subprocess.run(cmd, cwd=str(rep), stdout=logf, stderr=subprocess.STDOUT)
    logf.close()
    status["exit_code"] = proc.returncode

    # --- PBC-whole retry on BOND overflow (same issue as PP-02 in batch 15320) ---
    if proc.returncode != 0:
        log_text = (out_dir / "run.log").read_text(errors="replace")
        if "*************" in log_text:
            print(f"{sys_name}: BOND overflow detected — retrying with PBC-whole trajectory")
            pbc_xtc = rep / "production_pbc.xtc"
            subprocess.run(
                ["mamba", "run", "-n", ENV, "gmx_mpi", "trjconv",
                 "-s", str(rep / "production.tpr"),
                 "-f", str(rep / "production.xtc"),
                 "-o", str(pbc_xtc),
                 "-pbc", "whole", "-mol"],
                input="System\n", capture_output=True, text=True,
                cwd=str(rep), check=True,
            )
            cmd_retry = [c if c != str(rep / "production.xtc") else str(pbc_xtc)
                         if cmd[i - 1] == "-ct" else c
                         for i, c in enumerate(cmd)]
            # rebuild cleanly: replace -ct value
            cmd_retry = []
            it = iter(cmd)
            for token in it:
                if token == "-ct":
                    cmd_retry.append("-ct")
                    next(it)  # skip original xtc
                    cmd_retry.append(str(pbc_xtc))
                else:
                    cmd_retry.append(token)
            logf2 = open(out_dir / "run.log", "w")
            proc2 = subprocess.run(cmd_retry, cwd=str(rep), stdout=logf2, stderr=subprocess.STDOUT)
            logf2.close()
            status["pbc_whole_retry"] = True
            status["exit_code"] = proc2.returncode
            proc = proc2

    status["finished_utc"] = datetime.now(timezone.utc).isoformat()
    if proc.returncode == 0 and (out_dir / "mmgbsa_timeseries.csv").is_file():
        status["numerical_qc"] = validate_timeseries(out_dir / "mmgbsa_timeseries.csv")
        if status["numerical_qc"]["status"] != "PASS":
            status["status"] = "FAILED_NUMERICAL_QC"
            status["reportable"] = False
            print(f"{sys_name}: numerical QC failed; output is not reportable", file=sys.stderr)
            proc.returncode = 1
            status["exit_code"] = proc.returncode
    (out_dir / "launch_status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(f"{sys_name}: exit={proc.returncode} final_exists={final.is_file()}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
