#!/usr/bin/env python3
"""Set-C equilibration worker (EM/NVT/NPT) + force-field manifest finalisation.

Consumes the prepared system directories produced by ``p2_setc_prepare_openff.py``
(the explicitly exported versioned Set-C root, `set_c_preparation_20260812_v1/PP-XX_<Target>_<Mut>/`).  For each system it:

  1. runs steepest-descent EM (em.mdp, 5000 steps);
  2. runs NVT equilibration (100 ps, V-rescale, 310.15 K);
  3. runs NPT equilibration (100 ps, Parrinello-Rahman, 310.15 K / 1 bar);
  4. finalises ``forcefield_manifest.json`` with the npt.gro/npt.cpt hashes,
     ``md.mdp`` production descriptor hash, the system-manifest hash, and the
     recursive topology-dependency hashes (``finalized_by_equilibration=True``).

The production ``md.mdp`` (10 ns, 310.15 K, 2 fs) is written during finalisation
so that the workflow preflight (`p2_setc_md_workflow.py`) sees every contract
input.  A ``--smoke`` flag shortens every stage for pipeline validation.

Usage:
    python scripts/p2_setc_equilibrate.py --system PP-01_PfDHFR_WT
    python scripts/p2_setc_equilibrate.py --system PP-01_PfDHFR_WT --smoke
    python scripts/p2_setc_equilibrate.py --all            # every prepared dir
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
_root_env = os.environ.get("P2_SETC_ROOT")
if not _root_env:
    raise RuntimeError("P2_SETC_ROOT must be explicitly exported; refusing the legacy Set-C root")
SYSTEM_ROOT = Path(_root_env).expanduser().resolve()
EXPECTED_SYSTEM_ROOT = (PROJECT_DIR / "results" / "md_systems" / "set_c_preparation_20260812_v1").resolve()
if SYSTEM_ROOT != EXPECTED_SYSTEM_ROOT:
    raise RuntimeError(f"P2_SETC_ROOT must equal {EXPECTED_SYSTEM_ROOT}, got {SYSTEM_ROOT}")

GMX = os.environ.get("P2_GMX_BIN", "/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi")
PYTHON_EXPECTED = "/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
TEMP_K = 310.15

# Number of OpenMP threads per mdrun.  MUST be set explicitly: without -ntomp,
# GROMACS detects all 48 cores of the node and every array task tries to use 48
# threads -> 16 tasks x 48 = 768 threads -> OpenMP thread-allocation failure and
# segfault in the Verlet pair-search (observed on array 15054, retry 15070).
# Default 8 threads keeps 4 concurrent tasks within the 48-core node
# (4 x 8 = 32 <= 48).  Override with P2_SETC_NTOMP if needed.
NTOMP = int(os.environ.get("P2_SETC_NTOMP", "8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# GPU-less mdrun: the host A4000 crashes GROMACS GPU update/constraint routines
# (rc=-6, UpdateConstrainGpu); CPU paths are deterministic and match the parent
# study.  Always appended to mdrun calls.  -ntomp is set explicitly to prevent
# the whole-node thread oversubscription that caused deterministic segfaults in
# the Verlet pair-search under SLURM arrays (see NTOMP above).
MDRUN_CPU = ["-nb", "cpu", "-pme", "cpu", "-bonded", "cpu", "-update", "cpu",
             "-ntomp", str(NTOMP)]


def run(cmd: list[str], cwd: Path, label: str) -> None:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"{label} failed (rc={result.returncode}):\n"
            f"$ {' '.join(cmd)}\n{result.stdout[-1500:]}\n{result.stderr[-1500:]}"
        )


def write_mdp(system_dir: Path, name: str, body: str) -> None:
    (system_dir / name).write_text(body, encoding="utf-8")


def em_mdp(nsteps: int = 5000, emtol: float = 1000.0,
           emstep: float = 0.01) -> str:
    return f"""; EM — steepest descent (unrestrained)\nintegrator  = steep
nsteps      = {nsteps}
emtol       = {emtol}
emstep      = {emstep}
cutoff-scheme = Verlet
nstlist     = 10
rlist       = 1.2
rcoulomb    = 1.2
rvdw        = 1.2
coulombtype = PME
pme_order   = 4
fourierspacing = 0.16
constraints = none
"""


def nvt_mdp(smoke: bool) -> str:
    nsteps = 2000 if smoke else 50000  # 100 ps at 2 fs
    return f"""; NVT equilibration
integrator  = md
nsteps      = {nsteps}
dt          = 0.002
nstxout-compressed = 1000
nstenergy   = 500
nstlog      = 500
continuation = no
constraints = h-bonds
constraint_algorithm = lincs
lincs_iter  = 1
lincs_order = 4
cutoff-scheme = Verlet
nstlist     = 10
rlist       = 1.2
rcoulomb    = 1.2
rvdw        = 1.2
coulombtype = PME
pme_order   = 4
fourierspacing = 0.16
tcoupl      = V-rescale
tc-grps     = System
tau_t       = 0.1
ref_t       = {TEMP_K}
gen_vel     = yes
gen_temp    = {TEMP_K}
"""


def npt_mdp(smoke: bool) -> str:
    nsteps = 2000 if smoke else 50000  # 100 ps at 2 fs
    return f"""; NPT equilibration
integrator  = md
nsteps      = {nsteps}
dt          = 0.002
nstxout-compressed = 1000
nstenergy   = 500
nstlog      = 500
continuation = yes
constraints = h-bonds
constraint_algorithm = lincs
lincs_iter  = 1
lincs_order = 4
cutoff-scheme = Verlet
nstlist     = 10
rlist       = 1.2
rcoulomb    = 1.2
rvdw        = 1.2
coulombtype = PME
pme_order   = 4
fourierspacing = 0.16
tcoupl      = V-rescale
tc-grps     = System
tau_t       = 0.1
ref_t       = {TEMP_K}
pcoupl      = Parrinello-Rahman
pcoupltype  = isotropic
tau_p       = 2.0
compressibility = 4.5e-5
ref_p       = 1.0
gen_vel     = no
"""


def production_mdp() -> str:
    return f"""; Set-C production MD descriptor (10 ns, 310.15 K, 2 fs)
integrator  = md
nsteps      = 5000000
dt          = 0.002
nstxout-compressed = 5000
nstenergy   = 1000
nstlog      = 1000
continuation = yes
constraints = h-bonds
constraint_algorithm = lincs
lincs_iter  = 1
lincs_order = 4
cutoff-scheme = Verlet
nstlist     = 10
rlist       = 1.2
rcoulomb    = 1.2
rvdw        = 1.2
coulombtype = PME
pme_order   = 4
fourierspacing = 0.16
tcoupl      = V-rescale
tc-grps     = System
tau_t       = 0.1
ref_t       = {TEMP_K}
pcoupl      = Parrinello-Rahman
pcoupltype  = isotropic
tau_p       = 2.0
compressibility = 4.5e-5
ref_p       = 1.0
gen_vel     = yes
gen_temp    = {TEMP_K}
"""


def topology_dependencies(topol: Path) -> dict[str, str]:
    """All recursively included topology files -> sha256 (keyed relative to topol)."""
    resolved: dict[str, Path] = {}
    pending = [topol]
    while pending:
        current = pending.pop()
        if not current.is_file():
            continue
        text = current.read_text(errors="replace")
        for include in re.findall(r'^\s*#include\s+["<]([^">]+)[">]', text, flags=re.MULTILINE):
            dependency = (current.parent / include).resolve()
            if dependency.is_relative_to(topol.parent.resolve()):
                key = str(dependency.relative_to(topol.parent.resolve()))
            else:
                key = str(dependency)
            if key not in resolved:
                resolved[key] = dependency
                pending.append(dependency)
    return {key: sha256(path) for key, path in resolved.items()}


def validate_equilibration_environment() -> None:
    if sys.executable != PYTHON_EXPECTED:
        raise RuntimeError(
            f"wrong Python interpreter for equilibration: {sys.executable}; "
            f"expected {PYTHON_EXPECTED}"
        )
    if not Path(GMX).is_file() or not os.access(GMX, os.X_OK):
        raise RuntimeError(f"missing GROMACS executable: {GMX}")
    version = subprocess.run([GMX, "--version"], capture_output=True, text=True)
    if version.returncode != 0 or "GROMACS" not in (version.stdout + version.stderr):
        raise RuntimeError(f"GROMACS smoke check failed: {GMX}")


def equilibrate(system_dir: Path, smoke: bool) -> dict:
    required = [
        "complex.gro", "topol.top", "system_manifest.json", "forcefield_manifest.json",
        "pre_equilibration_audit.json",
    ]
    missing = [name for name in required if not (system_dir / name).is_file()]
    if missing:
        return {"system": system_dir.name, "status": "BLOCKED_MISSING_INPUTS", "missing": missing}
    audit = json.loads((system_dir / "pre_equilibration_audit.json").read_text(encoding="utf-8"))
    if audit.get("status") != "PASS" or audit.get("grompp_maxwarn") != 0:
        return {
            "system": system_dir.name,
            "status": "BLOCKED_PREPARATION_AUDIT",
            "audit_status": audit.get("status"),
            "grompp_maxwarn": audit.get("grompp_maxwarn"),
        }

    # Bind the audit certificate to the exact current inputs; a stale PASS may
    # never authorize a changed topology or coordinate file.
    expected_hashes = audit.get("input_sha256", {})
    for filename, expected in expected_hashes.items():
        path = system_dir / filename
        if expected and (not path.is_file() or sha256(path) != expected):
            return {"system": system_dir.name, "status": "BLOCKED_STALE_AUDIT", "file": filename}

    # EM phase 1: GENTLE unrestrained steepest descent (tiny emstep, no
    # -DPOSRES).  Root-cause fix 2026-08-10: the original phase-1 used
    # `-DPOSRES` + emstep=0.002, which froze the protein while the massive
    # initial clashes (docked ligand + two mis-oriented polar H's, ~0.8 A
    # apart; step-0 Bond ~1e8 kJ/mol, LJ ~3e8 kJ/mol) pushed water
    # coordinates to NaN -> GROMACS 2025.4 Verlet pair-search segfault
    # (arrays 15054/15070/15081, deterministic crash step ~40-160).
    # Unrestrained EM resolves the clashes smoothly.  emstep=0.0005 converged
    # for K76A/WT/worst-case PP-02_WT but K76T (hardest clash) still crashed
    # at step 63; emstep=0.0001 converged ALL tested systems (K76T -> -3.87e6,
    # 6211 steps, rc=0) — this is the universal, crash-free protocol.
    write_mdp(system_dir, "em.mdp", em_mdp(nsteps=10000, emtol=1000, emstep=0.0001))
    write_mdp(system_dir, "em2.mdp", em_mdp(nsteps=10000, emtol=200, emstep=0.002))
    write_mdp(system_dir, "nvt.mdp", nvt_mdp(smoke))
    write_mdp(system_dir, "npt.mdp", npt_mdp(smoke))

    run([GMX, "grompp", "-f", "em.mdp", "-c", "complex.gro", "-r", "complex.gro",
         "-p", "topol.top", "-o", "em.tpr", "-maxwarn", "0"], system_dir, "grompp-em")
    run([GMX, "mdrun", "-deffnm", "em", *MDRUN_CPU], system_dir, "mdrun-em")
    run([GMX, "grompp", "-f", "em2.mdp", "-c", "em.gro", "-p", "topol.top",
         "-o", "em2.tpr", "-maxwarn", "0"], system_dir, "grompp-em2")
    run([GMX, "mdrun", "-deffnm", "em2", *MDRUN_CPU], system_dir, "mdrun-em2")
    # sanity: final EM2 potential must be finite and negative (a blow-up here would
    # waste the NVT/NPT stages and indicate unresolved clashes)
    em2_log = (system_dir / "em2.log").read_text(errors="replace")
    import re as _re
    m = _re.findall(r"Potential Energy\s*=\s*([-+0-9.eE]+)", em2_log)
    if not m:
        raise RuntimeError("em2.log has no final Potential Energy")
    final_pot = float(m[-1])
    if not (final_pot < 0 and abs(final_pot) < 1e12):
        raise RuntimeError(f"em2 final potential not sane: {final_pot:.3e} kJ/mol")

    # NVT (from em2)
    run([GMX, "grompp", "-f", "nvt.mdp", "-c", "em2.gro", "-r", "em2.gro", "-p", "topol.top",
         "-o", "nvt.tpr", "-maxwarn", "0"], system_dir, "grompp-nvt")
    run([GMX, "mdrun", "-deffnm", "nvt", *MDRUN_CPU], system_dir, "mdrun-nvt")

    # NPT
    run([GMX, "grompp", "-f", "npt.mdp", "-c", "nvt.gro", "-t", "nvt.cpt", "-r", "nvt.gro",
         "-p", "topol.top", "-o", "npt.tpr", "-maxwarn", "0"], system_dir, "grompp-npt")
    run([GMX, "mdrun", "-deffnm", "npt", *MDRUN_CPU], system_dir, "mdrun-npt")

    for name in ("npt.gro", "npt.cpt"):
        path = system_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            return {"system": system_dir.name, "status": "BLOCKED_NO_NPT_OUTPUT",
                    "missing": name}

    # finalise force-field manifest
    write_mdp(system_dir, "md.mdp", production_mdp())
    ff_path = system_dir / "forcefield_manifest.json"
    ff = json.loads(ff_path.read_text(encoding="utf-8"))
    ff["topology_sha256"] = sha256(system_dir / "topol.top")
    ff["coordinates_sha256"] = sha256(system_dir / "npt.gro")
    ff["checkpoint_sha256"] = sha256(system_dir / "npt.cpt")
    ff["system_manifest_sha256"] = sha256(system_dir / "system_manifest.json")
    ff["md_mdp_sha256"] = sha256(system_dir / "md.mdp")
    ff["topology_dependency_sha256"] = topology_dependencies(system_dir / "topol.top")
    ff["finalized_by_equilibration"] = True
    ff["equilibration"] = {
        "temperature_K": TEMP_K,
        "em_steps": 13000,
        "nvt_ps": 0.2 if smoke else 100.0,
        "npt_ps": 0.2 if smoke else 100.0,
        "production_md_mdp": "md.mdp (10 ns, 310.15 K, 2 fs)",
        "gromacs": GMX,
        "finalized_utc": datetime.now(timezone.utc).isoformat(),
        "smoke": smoke,
    }
    ff_path.write_text(json.dumps(ff, indent=2) + "\n", encoding="utf-8")
    return {
        "system": system_dir.name,
        "status": "EQUILIBRATED_MANIFEST_FINALIZED",
        "npt_gro_sha256": ff["coordinates_sha256"],
        "npt_cpt_sha256": ff["checkpoint_sha256"],
        "n_topology_dependencies": len(ff["topology_dependency_sha256"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", help="Single system dir name, e.g. PP-01_PfDHFR_WT")
    parser.add_argument("--all", action="store_true", help="Equilibrate every prepared dir")
    parser.add_argument("--smoke", action="store_true", help="Short stages (pipeline validation only)")
    args = parser.parse_args()

    validate_equilibration_environment()
    if args.system:
        dirs = [SYSTEM_ROOT / args.system]
    elif args.all:
        dirs = sorted(d for d in SYSTEM_ROOT.iterdir()
                      if d.is_dir() and (d / "complex.gro").is_file())
    else:
        parser.error("provide --system NAME or --all")

    records = []
    for d in dirs:
        print(f"[eq] {d.name}", flush=True)
        try:
            records.append(equilibrate(d, args.smoke))
        except Exception as exc:
            rec = {"system": d.name, "status": "FAILED", "error": str(exc)[-500:]}
            records.append(rec)
            fail_path = d / "equilibration_failure.json"
            import json as _json
            fail_path.write_text(_json.dumps(rec, indent=2) + "\n")
            print(f"[eq] {d.name} FAILED: {str(exc)[-200:]}", flush=True)
    for r in records:
        print(json.dumps(r))
    bad = [r for r in records if not r["status"].startswith("EQUILIBRATED")]
    print(f"[eq] equilibrated {len(records) - len(bad)}/{len(records)} systems")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
