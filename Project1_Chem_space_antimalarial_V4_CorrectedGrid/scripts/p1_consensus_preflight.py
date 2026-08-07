#!/usr/bin/env python3
"""Fail-closed preflight for the independent P1 consensus-decoy benchmark.

This script only inspects files and locally installed tools/packages.  It never
runs Vina, DiffDock, SLURM, or any docking command.  A manifest is written even
when checks fail, so an incomplete benchmark cannot be mistaken for a result.

The intended benchmark is a common, independently labelled panel evaluated by
the same Vina+DiffDock protocol.  The currently available DEKOIS panel is a
PfDHFR Vina-only baseline; it must not be silently treated as a four-target
consensus benchmark.

Exit codes:
  0  all preflight gates pass (execution may be prepared, but is not launched)
  2  fail-closed: one or more required gates are incomplete
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from rdkit import Chem
except ImportError:  # pragma: no cover - reported as a preflight failure
    Chem = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
P1_ROOT = PROJECT_ROOT / "Project1_Chem_space_antimalarial_V4_CorrectedGrid"
P2_ROOT = PROJECT_ROOT / "Project2_Polypharmacology_MD_ValidationV2607"

DEKOIS_ACTIVES = P2_ROOT / "data/from_project1/data/external/DHFR_ligands.smi"
DEKOIS_DECOYS = P2_ROOT / "data/from_project1/data/external/DHFR_decoys.smi"
RECEPTORS = {
    "PfDHFR": P2_ROOT / "data/from_project1/data/proteins/7F3Y.pdbqt",
    "PfCRT": P2_ROOT / "data/from_project1/data/proteins/6UKJ.pdbqt",
    "PfATP4": P2_ROOT / "data/from_project1/data/proteins/9N10.pdbqt",
    "PfClpP": P2_ROOT / "data/from_project1/data/proteins/4GM2.pdbqt",
}
P1_PROVENANCE_FILES = {
    "P1_STONED_MMV_SEEDS": P1_ROOT / "p1_stoned_mmv_seeds.csv",
    "P1_PREDICTED_SYBA_LIBRARY": P1_ROOT / "c6_primary_leads_synthesisable.csv",
}
P1_SET_A_TOP20 = P1_ROOT / "results/p1_set_a_top20.csv"
# This is a summary table, not an independent raw labelled panel.  It is
# deliberately checked and reported as insufficient rather than used as input.
SUMMARY_ENRICHMENT = P1_ROOT / "p1_enrichment_chembl_benchmark.csv"
EXISTING_DIFFDOCK_SUMMARY = (
    P2_ROOT / "data/from_project1/docking/diffdock_summary.csv"
)
EXISTING_COMBINED_SUMMARY = (
    P2_ROOT / "data/from_project1/docking/combined_docking_results.csv"
)
P2_COHORT_FILES = {
    "P2_SET_B_MD_TOP20": P2_ROOT / "results/md_top20_candidates.csv",
    "P2_SET_C_POLYPHARM": P2_ROOT / "results/candidate_selection/md_top20_candidates_polypharm.csv",
}
PARENT_MD_PROVENANCE = P2_ROOT / "results/metrics/parent_md_provenance.json"
DEKOIS_HISTORICAL_RESULT = (
    PROJECT_ROOT / "Project1_Chem_space_antimalarial_V2_CorrectedGrid/results/v2_dekois/dekois_v2_roc_auc.csv"
)
DIFFDOCK_WEIGHTS_ENV = "DIFFDOCK_WEIGHTS"
DIFFDOCK_CONFIDENCE_WEIGHTS_ENV = "DIFFDOCK_CONFIDENCE_WEIGHTS"
DIFFDOCK_HOME_ENV = "DIFFDOCK_HOME"
DIFFDOCK_ENTRYPOINT_ENV = "DIFFDOCK_ENTRYPOINT"
EXPECTED_HISTORICAL_DEKOIS_SHA256 = "53db3e9d309e6a0ea2fcabf30f7c98c9481216ab97220d0b8cf2e02845ec4358"
EXPECTED_HISTORICAL_DEKOIS = {
    "roc_auc": "0.450104",
    "roc_auc_ci_low": "0.366643",
    "roc_auc_ci_high": "0.531372",
    "ef_1pct": "0.000000",
    "ef_5pct": "0.000000",
    "ef_10pct": "0.251829",
    "ef_20pct": "0.877834",
    "n_bootstrap": "1000",
    "bootstrap_seed": "42",
    "n_actives_total": "40",
    "n_actives_valid": "40",
    "n_decoys_total": "1199",
    "n_decoys_valid": "1199",
    "actives_mean": "-7.5438",
    "actives_std": "0.9301",
    "decoys_mean": "-7.7147",
    "decoys_std": "1.0181",
}


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": str(path.relative_to(PROJECT_ROOT))
        if path.is_relative_to(PROJECT_ROOT)
        else str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else None,
        "sha256": sha256(path),
    }
    if path.is_file() and path.suffix.lower() in {".csv", ".smi", ".txt"}:
        try:
            with path.open(encoding="utf-8", errors="replace") as handle:
                record["lines"] = sum(1 for _ in handle)
        except OSError as exc:
            record["read_error"] = str(exc)
    return record


def canonical_smiles(value: str) -> str | None:
    if Chem is None:
        return None
    molecule = Chem.MolFromSmiles(value.strip())
    return Chem.MolToSmiles(molecule, canonical=True) if molecule else None


def read_smi(path: Path) -> tuple[list[str], int]:
    values: list[str] = []
    invalid = 0
    if not path.is_file():
        return values, invalid
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            value = line.strip().split()[0] if line.strip() else ""
            if not value:
                continue
            values.append(value)
            if canonical_smiles(value) is None:
                invalid += 1
    return values, invalid


def read_csv_smiles(path: Path, column_candidates: tuple[str, ...]) -> list[str]:
    if not path.is_file():
        return []
    values: list[str] = []
    with path.open(encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        field = next((candidate for candidate in column_candidates if candidate in (reader.fieldnames or [])), None)
        if field is None:
            return values
        for row in reader:
            value = (row.get(field) or "").strip()
            if value:
                values.append(value)
    return values


def package_status(package: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(package)
    if spec is None:
        return {"available": False, "package": package, "import_error": "module_not_found"}
    try:
        module = __import__(package)
        return {
            "available": True,
            "package": package,
            "version": getattr(module, "__version__", "unknown"),
            "path": getattr(module, "__file__", None),
        }
    except Exception as exc:
        return {
            "available": False,
            "package": package,
            "import_error": f"{type(exc).__name__}: {exc}",
            "path": spec.origin,
        }


def command_status(command: str) -> dict[str, Any]:
    resolved = shutil.which(command)
    return {"available": resolved is not None, "command": command, "path": resolved}


def check(name: str, passed: bool, detail: str, **extra: Any) -> dict[str, Any]:
    result = {"name": name, "status": "PASS" if passed else "BLOCKED", "detail": detail}
    result.update(extra)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=P1_ROOT / "results/p1_consensus_preflight.json",
        help="Manifest path; no docking output is written by this script.",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output

    active_raw, active_invalid = read_smi(DEKOIS_ACTIVES)
    decoy_raw, decoy_invalid = read_smi(DEKOIS_DECOYS)
    active_canonical = {canonical_smiles(value) for value in active_raw} - {None}
    decoy_canonical = {canonical_smiles(value) for value in decoy_raw} - {None}

    cohort_sets: dict[str, set[str]] = {}
    cohort_files = {**P1_PROVENANCE_FILES, **P2_COHORT_FILES}
    cohort_duplicates: dict[str, int] = {}
    for name, path in cohort_files.items():
        if path.suffix.lower() == ".csv":
            raw = read_csv_smiles(path, ("smiles", "SMILES", "input"))
        else:
            raw, _ = read_smi(path)
        canonical_values = [canonical_smiles(value) for value in raw]
        canonical_values = [value for value in canonical_values if value is not None]
        cohort_sets[name] = set(canonical_values)
        cohort_duplicates[name] = len(canonical_values) - len(cohort_sets[name])

    checks: list[dict[str, Any]] = []
    checks.append(check(
        "python_rdkit",
        Chem is not None,
        "RDKit is required for deterministic SMILES canonicalisation.",
    ))
    for package in ("meeko", "torch", "torch_geometric", "e3nn", "spyrmsd"):
        status = package_status(package)
        checks.append(check(
            f"python_{package}",
            status["available"],
            "Required for the prepared Vina/DiffDock execution environment.",
            **status,
        ))
    diffdock_home = Path(os.environ[DIFFDOCK_HOME_ENV]) if os.environ.get(DIFFDOCK_HOME_ENV) else None
    diffdock_entrypoint = Path(os.environ[DIFFDOCK_ENTRYPOINT_ENV]) if os.environ.get(DIFFDOCK_ENTRYPOINT_ENV) else None
    diffdock_weights = Path(os.environ[DIFFDOCK_WEIGHTS_ENV]) if os.environ.get(DIFFDOCK_WEIGHTS_ENV) else None
    diffdock_confidence_weights = Path(os.environ[DIFFDOCK_CONFIDENCE_WEIGHTS_ENV]) if os.environ.get(DIFFDOCK_CONFIDENCE_WEIGHTS_ENV) else None
    diffdock_artifacts_ok = (
        diffdock_home is not None and diffdock_home.is_dir()
        and diffdock_entrypoint is not None and diffdock_entrypoint.is_file()
        and diffdock_weights is not None and diffdock_weights.is_file()
        and diffdock_confidence_weights is not None and diffdock_confidence_weights.is_file()
    )
    checks.append(check(
        "diffdock_artifacts",
        diffdock_artifacts_ok,
        "Pinned DiffDock source, entrypoint, score checkpoint, and confidence checkpoint are present. This is artifact validation only; it is not an inference smoke test.",
        DIFFDOCK_HOME=str(diffdock_home) if diffdock_home else None,
        DIFFDOCK_ENTRYPOINT=str(diffdock_entrypoint) if diffdock_entrypoint else None,
        DIFFDOCK_WEIGHTS=str(diffdock_weights) if diffdock_weights else None,
        DIFFDOCK_CONFIDENCE_WEIGHTS=str(diffdock_confidence_weights) if diffdock_confidence_weights else None,
        entrypoint_sha256=sha256(diffdock_entrypoint) if diffdock_entrypoint else None,
        weights_sha256=sha256(diffdock_weights) if diffdock_weights else None,
        confidence_weights_sha256=sha256(diffdock_confidence_weights) if diffdock_confidence_weights else None,
        confidence_checkpoint="best_model_epoch75.pt",
        inference_smoke_test="NOT_VALIDATED_TIMEOUT",
    ))
    for command in ("vina", "obabel", "sbatch"):
        status = command_status(command)
        checks.append(check(
            f"command_{command}",
            status["available"],
            "Available command required by the planned execution wrapper.",
            **status,
        ))

    checks.append(check(
        "dekois_active_panel",
        DEKOIS_ACTIVES.is_file() and len(active_raw) == 40 and active_invalid == 0,
        "Expected 40 valid DEKOIS PfDHFR actives.",
        count=len(active_raw), invalid_smiles=active_invalid,
        file=file_record(DEKOIS_ACTIVES),
    ))
    checks.append(check(
        "dekois_decoy_panel",
        DEKOIS_DECOYS.is_file() and len(decoy_raw) == 1200 and decoy_invalid == 0,
        "Expected 1,200 valid DEKOIS PfDHFR decoys.",
        count=len(decoy_raw), invalid_smiles=decoy_invalid,
        file=file_record(DEKOIS_DECOYS),
    ))
    checks.append(check(
        "dekois_internal_disjointness",
        len(active_raw) == len(active_canonical) == 40
        and len(decoy_raw) == len(decoy_canonical) == 1200
        and not (active_canonical & decoy_canonical),
        "DEKOIS active and decoy labels must be unique and disjoint after canonicalisation.",
        active_raw=len(active_raw), active_unique=len(active_canonical),
        decoy_raw=len(decoy_raw), decoy_unique=len(decoy_canonical),
        overlap=len(active_canonical & decoy_canonical),
    ))

    for target, receptor in RECEPTORS.items():
        checks.append(check(
            f"receptor_{target}",
            receptor.is_file() and receptor.stat().st_size > 0,
            "Target receptor PDBQT is present and non-empty.",
            file=file_record(receptor),
        ))

    for cohort_name, values in cohort_sets.items():
        overlap_active = len(values & active_canonical)
        overlap_decoy = len(values & decoy_canonical)
        checks.append(check(
            f"independence_{cohort_name}",
            cohort_duplicates[cohort_name] == 0
            and overlap_active == 0 and overlap_decoy == 0,
            "DEKOIS molecules must not overlap canonical P1/P2 cohorts after canonicalisation; duplicate canonical structures are rejected.",
            cohort_size=len(values), duplicates=cohort_duplicates[cohort_name],
            overlap_active=overlap_active, overlap_decoy=overlap_decoy,
            file=file_record(cohort_files[cohort_name]),
        ))

    checks.append(check(
        "parent_md_boundary",
        PARENT_MD_PROVENANCE.is_file(),
        "The four parent-MD leads are tracked as a separate cohort; direct SMILES overlap is not inferred from numeric lead IDs.",
        file=file_record(PARENT_MD_PROVENANCE),
        direct_smiles_overlap_check="NOT_APPLICABLE_WITHOUT_PARENT_SMILES",
    ))

    # A summary CSV cannot replace target-specific raw labels and is not treated
    # as an execution input.  This gate is deliberately explicit.
    summary_exists = SUMMARY_ENRICHMENT.is_file()
    checks.append(check(
        "four_target_independent_labels",
        False,
        "Only the PfDHFR DEKOIS raw panel is present; the existing ChEMBL file is a summary without raw labelled SMILES for all four targets.",
        available_summary=file_record(SUMMARY_ENRICHMENT),
        required_raw_target_panels=["PfDHFR", "PfCRT", "PfATP4", "PfClpP"],
        available_raw_target_panels=["PfDHFR (DEKOIS)"],
    ))
    p2_b = cohort_sets.get("P2_SET_B_MD_TOP20", set())
    p2_c = cohort_sets.get("P2_SET_C_POLYPHARM", set())
    checks.append(check(
        "p2_set_b_set_c_disjointness",
        not (p2_b & p2_c),
        "P2 Set B and Set C must remain pairwise disjoint after canonicalisation.",
        set_b_size=len(p2_b), set_c_size=len(p2_c), overlap=len(p2_b & p2_c),
    ))
    checks.append(check(
        "p1_set_a_provenance",
        P1_SET_A_TOP20.is_file(),
        "The independent benchmark must have a machine-readable P1 Set-A top-20 manifest; the broad predicted-SYBA library is not treated as Set A.",
        file=file_record(P1_SET_A_TOP20),
    ))
    checks.append(check(
        "diffdock_input_provenance",
        False,
        "Existing DiffDock/combined summaries lack a matching input-panel hash, model/weights hash, and reproducible execution manifest; they cannot be reused as consensus results.",
        diffdock_summary=file_record(EXISTING_DIFFDOCK_SUMMARY),
        combined_summary=file_record(EXISTING_COMBINED_SUMMARY),
        required_artifacts=["input_panel_sha256", "model_or_weights_sha256", "execution_manifest", "software_versions"],
    ))
    historical_metrics: dict[str, str] = {}
    if DEKOIS_HISTORICAL_RESULT.is_file():
        with DEKOIS_HISTORICAL_RESULT.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("metric") and row.get("value"):
                    historical_metrics[row["metric"]] = row["value"]
    historical_hash = sha256(DEKOIS_HISTORICAL_RESULT)
    historical_ok = (
        historical_hash is not None
        and historical_hash.startswith(EXPECTED_HISTORICAL_DEKOIS_SHA256)
        and all(historical_metrics.get(key) == value for key, value in EXPECTED_HISTORICAL_DEKOIS.items())
    )
    checks.append(check(
        "historical_dekois_artifact_traceability",
        historical_ok,
        "The reported 0.450 DEKOIS baseline must match the frozen historical V2 artifact hash and expected summary metrics; V4 has no local DEKOIS result file.",
        historical_result=file_record(DEKOIS_HISTORICAL_RESULT),
        expected_sha256=EXPECTED_HISTORICAL_DEKOIS_SHA256,
        expected_metrics=EXPECTED_HISTORICAL_DEKOIS,
        observed_metrics=historical_metrics,
        canonical_v4_result=file_record(P1_ROOT / "results/v2_dekois/dekois_v2_roc_auc.csv"),
    ))

    blockers = [item["name"] for item in checks if item["status"] == "BLOCKED"]
    manifest: dict[str, Any] = {
        "schema": "p1-consensus-preflight/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "canonical_project": "P1 V4",
        "status": "PASS_READY_FOR_EXPLICIT_EXECUTION_REVIEW" if not blockers else "FAIL_CLOSED_MISSING_OR_INVALID_INPUTS",
        "execution_allowed": not blockers,
        "dockings_launched": False,
        "diffdock_launched": False,
        "slurm_submitted": False,
        "benchmark_result": "UNTESTED",
        "benchmark_scope": {
            "intended": "Common independently labelled Vina+DiffDock panel, target-stratified metrics.",
            "currently_available": "DEKOIS PfDHFR raw active/decoy panel for Vina-only baseline; no four-target raw panel.",
            "required_metrics": ["ROC-AUC", "EF1", "EF5", "EF10", "BEDROC", "PR-AUC", "bootstrap 95% CI"],
            "bootstrap_seed": 42,
        },
        "checks": checks,
        "blocking_checks": blockers,
        "input_manifest": {
            "dekois_actives": file_record(DEKOIS_ACTIVES),
            "dekois_decoys": file_record(DEKOIS_DECOYS),
            "receptors": {target: file_record(path) for target, path in RECEPTORS.items()},
            "p1_provenance_panels": {name: file_record(path) for name, path in P1_PROVENANCE_FILES.items()},
            "p1_set_a_top20": file_record(P1_SET_A_TOP20),
            "p2_cohorts": {name: file_record(path) for name, path in P2_COHORT_FILES.items()},
            "parent_md_provenance": file_record(PARENT_MD_PROVENANCE),
            "historical_dekois_result": file_record(DEKOIS_HISTORICAL_RESULT),
        },
        "safe_next_action": (
            "Acquire raw, independently labelled target panels and complete the DiffDock input/model execution manifest; rerun this preflight before any docking."
            if blockers else
            "Obtain explicit review approval, freeze the execution manifest, then run the benchmark wrapper. This preflight itself has launched nothing."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": manifest["status"],
        "execution_allowed": manifest["execution_allowed"],
        "dockings_launched": False,
        "slurm_submitted": False,
        "blocking_checks": blockers,
        "manifest": str(output),
    }, indent=2))
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
