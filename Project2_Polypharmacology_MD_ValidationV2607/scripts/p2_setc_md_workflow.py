#!/usr/bin/env python3
"""Set-C MD + docking-RRS/polypharmacology workflow.

This is the execution entry point for the canonical 17-candidate set-C cohort.
It deliberately does not invent structures or force-field parameters from SMILES
or docking scores. A candidate-target-state may run only when its directory has
been prepared independently with CHARMM36m protein FF and either the canonical CGenFF ligand FF or the documented, PI-approved OpenFF 2.2.0 (AM1-BCC) deviation (declared in each forcefield_manifest.json policy_deviation block), and carries matching manifests.

Default mode is a read-only preflight.  Execution requires both ``--execute``
and ``P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND``.  The authorization is intentionally
kept even for an auto-approved invocation: it prevents an accidental call from
turning a planning command into a multi-system GROMACS campaign.

The workflow writes a status/provenance table that joins future MD status to
*docking-derived* RRS/ACSI/PNS.  It never calls that join an MD-RRS result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
SET_C_FILE = RESULTS_DIR / "candidate_selection" / "md_top20_candidates_polypharm.csv"
DOCKING_FILE = RESULTS_DIR / "docking_mutants.csv"
SYSTEM_ROOT = RESULTS_DIR / "md_systems" / "set_c"
OUTPUT_DIR = RESULTS_DIR / "set_c_md"

TARGET_MUTATIONS = {
    "PfDHFR": ["WT", "N51I", "C59R", "S108N", "I164L"],
    "PfCRT": ["WT", "K76T", "K76A"],
}
PARENT_NAMES = {"201_DHFR", "438_ATP4", "164_ClpP", "214_CRT"}
REQUIRED_INPUTS = ("complex.gro", "topol.top", "md.mdp", "system_manifest.json", "npt.gro", "npt.cpt")
# The historical GPU update/constraint path was unstable (rc=-6,
# UpdateConstrainGpu). CPU mode remains the default and is retained for
# reproducibility; the benchmarked mixed-offload GPU mode keeps bonded/update
# calculations on the CPU.
MDRUN_CPU = ["-nb", "cpu", "-pme", "cpu", "-bonded", "cpu", "-update", "cpu"]
MDRUN_GPU_MIXED = ["-nb", "gpu", "-pme", "gpu", "-bonded", "cpu", "-update", "cpu"]
REQUIRED_FF_FIELDS = {
    "cohort_id", "system_name", "protein_force_field", "ligand_force_field",
    "water_model", "topology_sha256", "coordinates_sha256",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_DIR)) if path.is_relative_to(PROJECT_DIR) else str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-candidates", type=int, default=2, help="Deterministic pilot size (1-4; default 2).")
    parser.add_argument("--targets", nargs="+", choices=sorted(TARGET_MUTATIONS), default=sorted(TARGET_MUTATIONS))
    parser.add_argument("--target-ns", type=float, default=10.0, help="Production duration per system/replicate (default 10 ns).")
    parser.add_argument("--replicates", type=int, default=1, help="Independent production replicates (default 1).")
    parser.add_argument("--execute", action="store_true", help="Run GROMACS after all systems pass validation.")
    parser.add_argument("--auto-approved", action="store_true", help="Non-interactive invocation only; never bypasses the execution authorization guard.")
    parser.add_argument("--gpu-id", default="auto")
    parser.add_argument("--backend", choices=("cpu", "gpu"), default="cpu", help="mdrun backend; GPU uses the benchmarked mixed-offload flags.")
    parser.add_argument("--ntomp", type=int, default=8, help="OpenMP threads for mdrun (default 8; explicit to avoid whole-node grabbing under SLURM arrays).")
    parser.add_argument("--array-index", type=int, default=-1, help="Legacy SLURM array task index. Prefer --system-name for fail-closed ownership.")
    parser.add_argument("--system-name", default=None, help="Exact prepared system name owned by this task; prevents filesystem-order remapping.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise SystemExit(f"{label} is missing required columns: {', '.join(missing)}")


def select_candidates(frame: pd.DataFrame, n: int) -> pd.DataFrame:
    selected = (
        frame.sort_values(["rank", "composite_score"], ascending=[True, False])
        .drop_duplicates("smiles", keep="first")
        .head(n)
        .copy()
    )
    selected.insert(0, "set_c_id", [f"PP-{int(rank):02d}" for rank in selected["rank"]])
    return selected


def validate_docking(selected: pd.DataFrame, docking: pd.DataFrame, targets: list[str]) -> None:
    expected = sum(len(TARGET_MUTATIONS[target]) for target in targets) * len(selected)
    observed = docking[docking["smiles"].isin(selected["smiles"]) & docking["target"].isin(targets)].copy()
    if len(observed) != expected:
        raise SystemExit(f"Selected docking panel incomplete: expected {expected} rows, found {len(observed)}")
    if set(observed["smiles"]) != set(selected["smiles"]):
        raise SystemExit("Selected docking panel does not cover exactly the selected candidate set")
    if not np.isfinite(pd.to_numeric(observed["vina_score"], errors="coerce")).all():
        raise SystemExit("Selected docking panel contains non-finite scores")
    keys = observed.groupby(["smiles", "target", "mutation"]).size()
    if (keys != 1).any():
        raise SystemExit("Selected docking panel contains duplicate candidate/target/mutation rows")
    for target in targets:
        expected_mutations = set(TARGET_MUTATIONS[target])
        actual = set(observed.loc[observed["target"] == target, "mutation"])
        if actual != expected_mutations:
            raise SystemExit(f"Mutation panel mismatch for {target}: expected {sorted(expected_mutations)}, found {sorted(actual)}")


def load_metric_map(name: str, candidate_sha256: str, key: str = "smiles") -> dict:
    """Load only canonical set-C metric rows with matching provenance."""
    path = RESULTS_DIR / name
    if not path.exists():
        raise RuntimeError(f"Required canonical metric output is missing: {path}")
    frame = pd.read_csv(path)
    required = {key, "cohort_id", "candidate_sha256"}
    if not required.issubset(frame.columns):
        raise RuntimeError(f"{name} lacks immutable cohort provenance columns")
    valid = frame[
        (frame["cohort_id"] == "P2_SET_C_POLYPHARM_17")
        & (frame["candidate_sha256"] == candidate_sha256)
    ]
    if len(valid) != len(frame):
        raise RuntimeError(f"{name} contains stale, custom, or mixed-cohort metric rows")
    if valid[key].duplicated().any():
        raise RuntimeError(f"{name} contains duplicate metric rows for candidate SMILES")
    return {row[key]: row for _, row in valid.iterrows()}


def authorize_with_shared_guard(execute: bool, gmx: str) -> str | None:
    """Use the shared shell guard for the exact binary that will execute."""
    if not execute:
        return None
    guard = PROJECT_DIR / "scripts" / "md_execution_guard.sh"
    command = (
        f"source {shlex_quote(str(guard))}; "
        "md_guard_parse --execute && md_guard_require_authorization"
    )
    result = subprocess.run(
        ["bash", "-lc", command],
        text=True,
        capture_output=True,
        env={**os.environ, "P2_GMX_BIN": gmx},
    )
    if result.returncode != 0:
        return (result.stderr or result.stdout).strip() or "shared execution guard rejected request"
    return None


def shlex_quote(value: str) -> str:
    import shlex
    return shlex.quote(value)


def resolve_gmx() -> str:
    configured = os.environ.get("P2_GMX_BIN")
    candidate = configured or shutil.which("gmx_mpi") or shutil.which("gmx")
    if not candidate:
        raise RuntimeError("No GROMACS executable found; set P2_GMX_BIN explicitly")
    if not Path(candidate).is_file() and not shutil.which(candidate):
        raise RuntimeError(f"Configured GROMACS executable is unavailable: {candidate}")
    version = subprocess.run([candidate, "--version"], text=True, capture_output=True)
    if version.returncode != 0:
        raise RuntimeError(f"GROMACS executable failed --version: {candidate}")
    return candidate


def validate_identity(manifest_path: Path, expected: dict) -> list[str]:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid system_manifest.json: {exc}"]
    errors = []
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"system_manifest {key}={payload.get(key)!r}, expected {value!r}")
    return errors


def topology_dependencies(topol: Path) -> dict[str, Path]:
    """Resolve all local topology includes recursively for integrity checking."""
    import re
    resolved: dict[str, Path] = {}
    pending = [topol]
    while pending:
        current = pending.pop()
        if not current.is_file():
            continue
        text = current.read_text(errors="replace")
        for include in re.findall(r'^\\s*#include\\s+["<]([^">]+)[">]', text, flags=re.MULTILINE):
            dependency = (current.parent / include).resolve()
            key = str(dependency.relative_to(topol.parent.resolve())) if dependency.is_relative_to(topol.parent.resolve()) else str(dependency)
            if key not in resolved:
                resolved[key] = dependency
                pending.append(dependency)
    return resolved


def validate_forcefield(system_dir: Path, expected_name: str) -> list[str]:
    path = system_dir / "forcefield_manifest.json"
    if not path.is_file():
        return ["missing forcefield_manifest.json"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid forcefield_manifest.json: {exc}"]
    errors = []
    missing = sorted(REQUIRED_FF_FIELDS - set(payload))
    if missing:
        errors.append(f"forcefield manifest missing fields: {', '.join(missing)}")
    if payload.get("cohort_id") != "P2_SET_C_POLYPHARM_17":
        errors.append("forcefield cohort_id is not P2_SET_C_POLYPHARM_17")
    if payload.get("system_name") != expected_name:
        errors.append(f"forcefield system_name={payload.get('system_name')!r}, expected {expected_name!r}")
    if payload.get("protein_force_field") != "CHARMM36m":
        errors.append("protein force field must be CHARMM36m")
    ligand_ff = payload.get("ligand_force_field")
    deviation = payload.get("policy_deviation") or {}
    if ligand_ff != "CGenFF":
        # Documented, PI-approved deviation (2026-08-09): OpenFF 2.2.0 (AM1-BCC)
        # substitutes for the licensed ParamChem CGenFF binary (not pip/conda
        # installable).  Accepted ONLY when the manifest declares the deviation
        # explicitly and approval is recorded; anything else fails closed.
        deviation_ok = (
            ligand_ff == "OpenFF 2.2.0 (AM1-BCC)"
            and deviation.get("declared") is True
            and deviation.get("field") == "ligand_force_field"
            and deviation.get("canonical_requirement") == "CGenFF"
            and deviation.get("approved") is True
        )
        if not deviation_ok:
            errors.append(
                "ligand force field must be CGenFF, or an approved documented "
                "policy_deviation for OpenFF 2.2.0 (AM1-BCC)"
            )
    if payload.get("water_model") != "TIP3P":
        errors.append("water model must be TIP3P")
    for filename, field in (("topol.top", "topology_sha256"), ("npt.gro", "coordinates_sha256"), ("npt.cpt", "checkpoint_sha256"), ("system_manifest.json", "system_manifest_sha256")):
        path_to_check = system_dir / filename
        if not path_to_check.is_file():
            errors.append(f"missing hash input: {filename}")
            continue
        if not isinstance(payload.get(field), str) or payload[field] != sha256(path_to_check):
            errors.append(f"{field} does not match {filename}")

    # A topology hash is insufficient if an included ligand/toppar file changes.
    # Require every local include, including nested includes, to be declared and hash-matched.
    dependency_hashes = payload.get("topology_dependency_sha256", {})
    topol = system_dir / "topol.top"
    if topol.is_file():
        for include, dependency in topology_dependencies(topol).items():
            if not dependency.is_file():
                errors.append(f"missing topology dependency: {include}")
            elif dependency_hashes.get(include) != sha256(dependency):
                errors.append(f"topology dependency hash missing/mismatched: {include}")
    return errors


def inspect_system(row: dict) -> tuple[dict, list[str]]:
    system_dir = Path(row["prepared_complex_dir"])
    expected_name = f"{row['set_c_id']}_{row['target']}_{row['mutation']}"
    errors: list[str] = []
    if system_dir.name != expected_name:
        errors.append(f"directory name {system_dir.name!r} does not match expected {expected_name!r}")
    if any(parent in system_dir.parts for parent in PARENT_NAMES):
        errors.append("parent-study MD directory detected in set-C path")
    if not system_dir.is_dir():
        errors.append("prepared system directory is missing")
    for filename in REQUIRED_INPUTS:
        path = system_dir / filename
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing/empty {filename}")
    if not errors:
        errors.extend(validate_identity(system_dir / "system_manifest.json", {
            "set_c_id": row["set_c_id"],
            "target": row["target"],
            "mutation": row["mutation"],
            "smiles": row["smiles"],
            "cohort_id": "P2_SET_C_POLYPHARM_17",
        }))
        errors.extend(validate_forcefield(system_dir, expected_name))
    return {**row, "system_name": expected_name, "prepared_complex_dir": str(system_dir), "md_status": "READY" if not errors else "BLOCKED"}, errors


def make_production_mdp(system_dir: Path, target_ns: float, temperature: float = 310.15) -> Path:
    nsteps = int(round(target_ns * 1_000_000 / 0.002))
    path = system_dir / "set_c_production.mdp"
    path.write_text(f"""; Canonical set-C production MD; generated only after manifest validation.
integrator = md
nsteps = {nsteps}
dt = 0.002
nstxout-compressed = 5000
nstenergy = 1000
nstlog = 1000
continuation = yes
constraints = h-bonds
constraint_algorithm = lincs
lincs_iter = 1
lincs_order = 4
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.2
rcoulomb = 1.2
rvdw = 1.2
coulombtype = PME
pme_order = 4
fourierspacing = 0.16
tcoupl = V-rescale
tc-grps = System
tau_t = 0.1
ref_t = {temperature}
pcoupl = Parrinello-Rahman
pcoupltype = isotropic
tau_p = 2.0
compressibility = 4.5e-5
ref_p = 1.0
gen_vel = yes
""", encoding="utf-8")
    return path


def prepare_replicate(row: dict, args: argparse.Namespace, run_records: list[dict], gmx: str, run_id: str) -> list[tuple[Path, list[str], list[str]]]:
    """Stage each replicate in a unique run directory and run grompp only."""
    system_dir = Path(row["prepared_complex_dir"])
    mdp = make_production_mdp(system_dir, args.target_ns)
    prepared = []
    for replicate in range(1, args.replicates + 1):
        rep_dir = system_dir / "runs" / run_id / f"replicate_{replicate}"
        if rep_dir.exists():
            raise RuntimeError(f"Refusing to reuse existing run directory: {rep_dir}")
        rep_dir.mkdir(parents=True)
        for filename in ("npt.gro", "npt.cpt", "topol.top"):
            shutil.copy2(system_dir / filename, rep_dir / filename)
        # Preserve every local #include used by topol.top. Copying only topol.top
        # is insufficient for grompp and can silently bind a run to a different
        # working-directory topology. Absolute/out-of-tree includes fail closed.
        dependency_hashes = {}
        for relative_name, dependency in topology_dependencies(system_dir / "topol.top").items():
            relative_path = Path(relative_name)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise RuntimeError(f"unsafe topology dependency path: {relative_name}")
            if not dependency.is_file():
                raise RuntimeError(f"missing topology dependency: {dependency}")
            destination = rep_dir / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dependency, destination)
            dependency_hashes[relative_name] = sha256(destination)
        shutil.copy2(mdp, rep_dir / mdp.name)
        seed = replicate * 12345
        command = [gmx, "grompp", "-f", mdp.name, "-c", "npt.gro", "-r", "npt.gro", "-t", "npt.cpt", "-p", "topol.top", "-o", "production.tpr"]
        record = {
            "system_name": row["system_name"], "replicate": replicate, "seed": seed,
            "run_dir": rel(rep_dir),
            "status": "GROMPP_READY", "mdp_sha256": sha256(rep_dir / mdp.name),
            "topology_sha256": sha256(rep_dir / "topol.top"),
            "coordinates_sha256": sha256(rep_dir / "npt.gro"),
            "checkpoint_sha256": sha256(rep_dir / "npt.cpt"),
            "topology_dependency_sha256": dependency_hashes,
            "backend": args.backend,
            "grompp_command": command,
        }
        run_records.append(record)
        subprocess.run(command, cwd=rep_dir, check=True)
        if not (rep_dir / "production.tpr").is_file() or (rep_dir / "production.tpr").stat().st_size == 0:
            raise RuntimeError(f"grompp produced no production.tpr in {rep_dir}")
        record["production_tpr"] = rel(rep_dir / "production.tpr")
        record["production_tpr_sha256"] = sha256(rep_dir / "production.tpr")
        (rep_dir / "production_provenance.json").write_text(
            json.dumps({
                "schema_version": 1,
                "status": "GROMPP_READY",
                "system_name": row["system_name"],
                "run_dir": rel(rep_dir),
                "md_rrs_status": "NOT_COMPUTED",
                "input_sha256": {
                    "npt.gro": record["coordinates_sha256"],
                    "npt.cpt": record["checkpoint_sha256"],
                    "topol.top": record["topology_sha256"],
                    mdp.name: record["mdp_sha256"],
                },
                "topology_dependency_sha256": dependency_hashes,
                "backend": args.backend,
                "gate_job_id": os.environ.get("P2_GATE_JOB_ID"),
                "equilibration_job_id": os.environ.get("P2_EQUILIBRATION_JOB_ID"),
                "preflight_manifest": os.environ.get("P2_PREFLIGHT_MANIFEST"),
                "preflight_manifest_sha256": (
                    sha256(Path(os.environ["P2_PREFLIGHT_MANIFEST"]))
                    if os.environ.get("P2_PREFLIGHT_MANIFEST")
                    and Path(os.environ["P2_PREFLIGHT_MANIFEST"]).is_file()
                    else None
                ),
                "production_tpr": record["production_tpr"],
                "production_tpr_sha256": record["production_tpr_sha256"],
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        backend_flags = MDRUN_GPU_MIXED if args.backend == "gpu" else MDRUN_CPU
        mdrun = [gmx, "mdrun", "-deffnm", "production", "-seed", str(seed), "-v", "-ntomp", str(args.ntomp), *backend_flags]
        if args.backend == "gpu" and args.gpu_id != "auto":
            mdrun.extend(["-gpu_id", args.gpu_id])
        prepared.append((rep_dir, record, mdrun))
    return prepared


def execute_replicate(prepared: tuple[Path, dict, list[str]], args: argparse.Namespace) -> None:
    rep_dir, record, mdrun = prepared
    record["mdrun_command"] = mdrun
    record["status"] = "RUNNING"
    subprocess.run(mdrun, cwd=rep_dir, check=True)
    required_outputs = ("production.tpr", "production.xtc", "production.edr", "production.log", "production.gro")
    missing = [name for name in required_outputs if not (rep_dir / name).is_file() or (rep_dir / name).stat().st_size == 0]
    if missing:
        raise RuntimeError(f"mdrun completed without required outputs in {rep_dir}: {', '.join(missing)}")
    record.update({
        "status": "COMPLETED",
        "production_tpr": rel(rep_dir / "production.tpr"),
        "production_xtc": rel(rep_dir / "production.xtc"),
        "production_xtc_sha256": sha256(rep_dir / "production.xtc"),
        "production_edr_sha256": sha256(rep_dir / "production.edr"),
        "outputs_sha256": {
            name: sha256(rep_dir / name)
            for name in required_outputs
            if (rep_dir / name).is_file()
        },
    })
    (rep_dir / "production_provenance.json").write_text(
        json.dumps({
            "schema_version": 1,
            "status": "PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC",
            "system_name": record["system_name"],
            "run_dir": record["run_dir"],
            "md_rrs_status": "NOT_COMPUTED",
            "gate_job_id": os.environ.get("P2_GATE_JOB_ID"),
            "equilibration_job_id": os.environ.get("P2_EQUILIBRATION_JOB_ID"),
            "preflight_manifest": os.environ.get("P2_PREFLIGHT_MANIFEST"),
            "preflight_manifest_sha256": (
                sha256(Path(os.environ["P2_PREFLIGHT_MANIFEST"]))
                if os.environ.get("P2_PREFLIGHT_MANIFEST")
                and Path(os.environ["P2_PREFLIGHT_MANIFEST"]).is_file()
                else None
            ),
            "input_sha256": {
                "npt.gro": record["coordinates_sha256"],
                "npt.cpt": record["checkpoint_sha256"],
                "topol.top": record["topology_sha256"],
                "mdp": record["mdp_sha256"],
            },
            "outputs_sha256": record["outputs_sha256"],
            "production_tpr": record["production_tpr"],
            "production_tpr_sha256": record["outputs_sha256"].get("production.tpr"),
        }, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    if not 1 <= args.n_candidates <= 4:
        raise SystemExit("--n-candidates must be between 1 and 4")
    if args.target_ns <= 0 or args.replicates < 1:
        raise SystemExit("--target-ns must be positive and --replicates >= 1")
    if args.execute and os.environ.get("P2_MD_EXECUTE_CONFIRM") != "I_UNDERSTAND":
        raise SystemExit("FAIL-CLOSED: --execute requires P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND")
    if args.execute:
        try:
            gmx = resolve_gmx()
        except RuntimeError as exc:
            raise SystemExit(f"FAIL-CLOSED: {exc}") from exc
        guard_error = authorize_with_shared_guard(True, gmx)
        if guard_error:
            raise SystemExit(f"FAIL-CLOSED: shared MD guard rejected execution: {guard_error}")
    else:
        gmx = None

    set_c = pd.read_csv(SET_C_FILE)
    docking = pd.read_csv(DOCKING_FILE)
    require_columns(set_c, {"rank", "smiles", "composite_score"}, "set-C file")
    require_columns(docking, {"smiles", "target", "mutation", "vina_score"}, "docking file")
    if len(set_c) != 17:
        raise SystemExit(f"Canonical set-C file must contain 17 rows, found {len(set_c)}")
    selected = select_candidates(set_c, args.n_candidates)
    validate_docking(selected, docking, args.targets)
    candidate_hash = sha256(SET_C_FILE)

    rrs = load_metric_map("c_rrs_classification.csv", candidate_hash)
    acsi = load_metric_map("c_acsi_scores.csv", candidate_hash)
    pns = load_metric_map("c_pns_ranking.csv", candidate_hash)
    rows: list[dict] = []
    for _, candidate in selected.iterrows():
        for target in args.targets:
            for mutation in TARGET_MUTATIONS[target]:
                base = {
                    "set_c_id": candidate["set_c_id"], "rank": int(candidate["rank"]), "smiles": candidate["smiles"],
                    "target": target, "mutation": mutation,
                    "prepared_complex_dir": str(SYSTEM_ROOT / f"{candidate['set_c_id']}_{target}_{mutation}"),
                }
                status, errors = inspect_system(base)
                metric = rrs.get(candidate["smiles"], {})
                status.update({
                    "docking_rrs_mean": metric.get("RRS_mean", np.nan),
                    "docking_rrs_class": metric.get("RRS_class", "UNAVAILABLE"),
                    "docking_pns": pns.get(candidate["smiles"], {}).get("PNS", np.nan),
                    "acsi": acsi.get(candidate["smiles"], {}).get("ACSI", np.nan),
                    "blocking_reasons": "; ".join(errors),
                    "md_rrs_status": "NOT_COMPUTED",
                })
                rows.append(status)

    # Array ownership must be explicit.  The old implementation derived the
    # owner from sorted filesystem directories, which could silently remap a
    # task when witness/archive directories were present.  The production
    # wrapper now passes --system-name; the legacy index mode is retained only
    # with a deterministic expected panel order and never consults the filesystem.
    if args.system_name is not None and args.array_index >= 0:
        raise SystemExit("--system-name and --array-index are mutually exclusive")
    expected_array_systems = [
        f"{set_c_id}_{target}_{mutation}"
        for set_c_id in selected["set_c_id"]
        for target in args.targets
        for mutation in TARGET_MUTATIONS[target]
    ]
    array_system = args.system_name
    if args.system_name is not None:
        if args.system_name not in expected_array_systems:
            raise SystemExit(
                f"--system-name {args.system_name!r} is not part of the selected deterministic panel"
            )
        rows = [r for r in rows if r["system_name"] == args.system_name]
        if not rows:
            raise SystemExit(f"No row for explicitly requested system {args.system_name!r}")
    elif args.array_index >= 0:
        if args.array_index >= len(expected_array_systems):
            raise SystemExit(
                f"--array-index {args.array_index} out of range "
                f"({len(expected_array_systems)} systems in the selected panel)"
            )
        array_system = expected_array_systems[args.array_index]
        rows = [r for r in rows if r["system_name"] == array_system]
        if not rows:
            raise SystemExit(f"Array task {args.array_index}: no row for system {array_system!r}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    status_path = args.output_dir / "set_c_md_status.csv"
    manifest_path = args.output_dir / "set_c_md_execution_manifest.json"
    # In array mode each task writes its own manifest/status; skip the shared
    # file to avoid array-task write races.
    if args.array_index >= 0:
        manifest_path = args.output_dir / f"set_c_md_execution_manifest_array{args.array_index:02d}.json"
        status_path = args.output_dir / f"set_c_md_status_array{args.array_index:02d}.csv"
    pd.DataFrame(rows).to_csv(status_path, index=False)
    blocked = [row for row in rows if row["md_status"] != "READY"]
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_id": "P2_SET_C_POLYPHARM_17",
        "array_index": args.array_index,
        "array_system": array_system,
        "selected_ids": selected["set_c_id"].tolist(),
        "targets": args.targets,
        "required_system_count": len(rows),
        "ready_system_count": len(rows) - len(blocked),
        "blocked_system_count": len(blocked),            "target_ns": args.target_ns,
            "replicates": args.replicates,
            "backend": args.backend,
            "gpu_id": args.gpu_id if args.backend == "gpu" else None,
        "execution_requested": bool(args.execute),
        "gromacs_launched": False,
        "md_rrs_status": "NOT_COMPUTED",
        "metric_boundary": "RRS, ACSI, and PNS in the status table are docking/cheminformatics-derived; no MD-RRS is inferred.",
        "status_table": rel(status_path),
        "parent_md_excluded": sorted(PARENT_NAMES),
        "gate_job_id": os.environ.get("P2_GATE_JOB_ID"),
        "equilibration_job_id": os.environ.get("P2_EQUILIBRATION_JOB_ID"),
        "preflight_manifest": os.environ.get("P2_PREFLIGHT_MANIFEST"),
    }
    if blocked:
        manifest["status"] = "FAIL_CLOSED_MISSING_OR_INVALID_SET_C_INPUTS"
        manifest["blocking_examples"] = [row["blocking_reasons"] for row in blocked[:8]]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Set-C systems selected: {len(rows)}")
        print(f"Ready: {len(rows) - len(blocked)}; blocked: {len(blocked)}")
        print("GROMACS launched: no")
        print(f"Status table: {status_path}")
        print("Preflight result: FAIL-CLOSED (candidate-specific CHARMM36m/CGenFF systems are not ready)")
        return 2

    if not args.execute:
        manifest["status"] = "READY_FOR_AUTHORIZED_EXECUTION"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Set-C systems selected: {len(rows)}")
        print("All systems pass identity, force-field, and hash validation.")
        print("GROMACS launched: no (preflight mode)")
        print(f"Status table: {status_path}")
        return 0

    run_records: list[dict] = []
    manifest["gromacs_binary"] = gmx
    manifest["backend"] = args.backend
    manifest["gpu_id"] = args.gpu_id if args.backend == "gpu" else None
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest["run_id"] = run_id
    try:
        prepared_runs = []
        for row in rows:
            prepared_runs.extend(prepare_replicate(row, args, run_records, gmx, run_id))
        manifest["grompp_preflight"] = "PASSED_ALL_REPLICATES"
        for prepared in prepared_runs:
            execute_replicate(prepared, args)
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        manifest["status"] = "PARTIAL_OR_FAILED_EXECUTION_REQUIRES_AUDIT"
        manifest["gromacs_launched"] = True
        manifest["runs_completed_before_failure"] = run_records
        manifest["failure"] = str(exc)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"FAIL-CLOSED: execution stopped after {len(run_records)} completed replicate(s): {exc}", file=sys.stderr)
        print(f"Manifest: {manifest_path}", file=sys.stderr)
        return 3
    manifest["status"] = "PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC"
    manifest["gromacs_launched"] = True
    manifest["runs"] = run_records
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"GROMACS completed for {len(run_records)} replicate(s).")
    print("MD-RRS: not computed; trajectory QC and pre-specified binding-state analysis remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
