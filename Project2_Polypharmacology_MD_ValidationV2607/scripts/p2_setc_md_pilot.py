#!/usr/bin/env python3
"""Bounded, provenance-first pilot design for set-C molecular dynamics.

This script does *not* launch GROMACS and must not be used as evidence that the
four parent-study consensus systems represent set C.  It selects a small,
deterministic subset of the 17 set-C polypharmacology candidates, validates the
available docking provenance, and writes a manifest for a future targeted MD
campaign.  It fails closed when candidate-specific prepared complexes are not
present.

Example:
    python scripts/p2_setc_md_pilot.py --n-candidates 2

The default output is:
    results/pilot/set_c_md_pilot_manifest.json
    results/pilot/set_c_md_pilot_systems.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
SET_C_FILE = RESULTS_DIR / "candidate_selection" / "md_top20_candidates_polypharm.csv"
DOCKING_FILE = RESULTS_DIR / "docking_mutants.csv"
PILOT_DIR = RESULTS_DIR / "pilot"

# These are the already-run parent-study MD systems.  They are deliberately
# recorded as exclusions, not as fallback inputs for set-C pilot systems.
PARENT_MD_SYSTEMS = {
    "201-PfDHFR",
    "438-PfATP4",
    "164-PfClpP",
    "214-PfCRT",
}
TARGET_MUTATIONS = {
    "PfDHFR": ["WT", "N51I", "C59R", "S108N", "I164L"],
    "PfCRT": ["WT", "K76T", "K76A"],
}
# A future preparation workflow must write system_manifest.json with the exact
# set_c_id, target, mutation, and canonical SMILES fields checked below, in
# addition to the executable GROMACS inputs. Until then, the pilot remains
# fail-closed and cannot report READY_FOR_EXPLICIT_REVIEW.
REQUIRED_COMPLEX_FILES = ("complex.gro", "topol.top", "md.mdp", "system_manifest.json")


def validate_system_manifest(path: Path, row: dict) -> str | None:
    """Return an identity error for a prepared system, or ``None`` if valid."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"{path}: invalid JSON ({exc})"
    expected = {
        "set_c_id": row["set_c_id"],
        "target": row["target"],
        "mutation": row["mutation"],
        "smiles": row["smiles"],
    }
    mismatches = [
        f"{key}={payload.get(key)!r} (expected {value!r})"
        for key, value in expected.items()
        if payload.get(key) != value
    ]
    return f"{path}: identity mismatch: {', '.join(mismatches)}" if mismatches else None


def validate_docking_completeness(
    selected: pd.DataFrame, docking: pd.DataFrame, targets: list[str]
) -> None:
    """Require exactly one finite docking row for every selected state."""
    expected_rows = len(selected) * sum(len(TARGET_MUTATIONS[target]) for target in targets)
    observed = docking[
        docking["smiles"].isin(selected["smiles"])
        & docking["target"].isin(targets)
    ].copy()
    if len(observed) != expected_rows:
        raise SystemExit(
            "Selected set-C docking is incomplete or contains duplicates: "
            f"expected {expected_rows} rows, found {len(observed)}"
        )
    if not np.isfinite(pd.to_numeric(observed["vina_score"], errors="coerce")).all():
        raise SystemExit("Selected set-C docking contains non-finite vina_score values")
    duplicates = observed.groupby(["smiles", "target", "mutation"]).size()
    if (duplicates != 1).any():
        raise SystemExit("Selected set-C docking has duplicate candidate/target/mutation rows")
    for target in targets:
        allowed = set(TARGET_MUTATIONS[target])
        observed_mutations = set(observed.loc[observed["target"] == target, "mutation"])
        if observed_mutations != allowed:
            raise SystemExit(
                f"Docking mutation panel mismatch for {target}: "
                f"expected {sorted(allowed)}, found {sorted(observed_mutations)}"
            )
    if set(observed["smiles"]) != set(selected["smiles"]):
        raise SystemExit("Selected set-C docking does not cover exactly the selected candidate SMILES")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n-candidates",
        type=int,
        default=2,
        help="Number of set-C candidates to select (default: 2; maximum: 4).",
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=sorted(TARGET_MUTATIONS),
        default=sorted(TARGET_MUTATIONS),
        help="Target pairs to include in the pilot (default: PfDHFR PfCRT).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PILOT_DIR,
        help="Output directory for the manifest and system table.",
    )
    return parser.parse_args()


def require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise SystemExit(f"{label} is missing required columns: {', '.join(missing)}")


def select_candidates(frame: pd.DataFrame, n: int) -> pd.DataFrame:
    # Rank is the canonical deterministic ordering; composite_score is a
    # secondary key so a malformed/duplicated rank cannot silently reorder a run.
    selected = (
        frame.sort_values(["rank", "composite_score"], ascending=[True, False])
        .drop_duplicates(subset=["smiles"], keep="first")
        .head(n)
        .copy()
    )
    selected.insert(0, "set_c_id", [f"PP-{int(rank):02d}" for rank in selected["rank"]])
    return selected


def validate_docking(selected: pd.DataFrame, docking: pd.DataFrame, targets: list[str]) -> list[dict]:
    records: list[dict] = []
    for _, candidate in selected.iterrows():
        for target in targets:
            expected = TARGET_MUTATIONS[target]
            observed = docking[
                (docking["smiles"] == candidate["smiles"])
                & (docking["target"] == target)
            ]
            observed_mutations = sorted(set(observed["mutation"]))
            missing = [mutation for mutation in expected if mutation not in observed_mutations]
            for mutation in expected:
                rows = observed[observed["mutation"] == mutation]
                records.append(
                    {
                        "set_c_id": candidate["set_c_id"],
                        "rank": int(candidate["rank"]),
                        "smiles": candidate["smiles"],
                        "target": target,
                        "mutation": mutation,
                        "docking_rows": int(len(rows)),
                        "docking_input_complete": not missing,
                        "prepared_complex_dir": str(
                            RESULTS_DIR / "md_systems" / "set_c" / f"{candidate['set_c_id']}_{target}_{mutation}"
                        ),
                    }
                )
    return records


def main() -> int:
    args = parse_args()
    if not 1 <= args.n_candidates <= 4:
        raise SystemExit("--n-candidates must be between 1 and 4 for a bounded pilot")

    if not SET_C_FILE.exists():
        raise SystemExit(f"Missing canonical set-C file: {SET_C_FILE}")
    if not DOCKING_FILE.exists():
        raise SystemExit(f"Missing docking provenance file: {DOCKING_FILE}")

    set_c = pd.read_csv(SET_C_FILE)
    docking = pd.read_csv(DOCKING_FILE)
    require_columns(set_c, {"rank", "smiles", "composite_score"}, "set-C candidate file")
    require_columns(docking, {"smiles", "target", "mutation", "vina_score"}, "docking file")

    if len(set_c) != 17:
        raise SystemExit(f"Expected 17 set-C candidates, found {len(set_c)}")
    if set(set_c["smiles"]) & set(docking["smiles"]) != set(set_c["smiles"]):
        raise SystemExit("Set-C candidate/docking SMILES membership mismatch; refusing to select a pilot")

    selected = select_candidates(set_c, args.n_candidates)
    validate_docking_completeness(selected, docking, args.targets)
    systems = validate_docking(selected, docking, args.targets)
    missing_prepared = []
    for row in systems:
        complex_dir = Path(row["prepared_complex_dir"])
        if not complex_dir.is_dir():
            missing_prepared.append(str(complex_dir))
            continue
        missing_files = [
            name for name in REQUIRED_COMPLEX_FILES
            if not (complex_dir / name).is_file() or (complex_dir / name).stat().st_size == 0
        ]
        identity_error = None
        manifest_path = complex_dir / "system_manifest.json"
        if not missing_files and manifest_path.is_file():
            identity_error = validate_system_manifest(manifest_path, row)
        if missing_files or identity_error:
            details = []
            if missing_files:
                details.append(f"missing/empty: {', '.join(missing_files)}")
            if identity_error:
                details.append(identity_error)
            missing_prepared.append(f"{complex_dir} ({'; '.join(details)})")

    # Explicitly prevent accidental reuse of the four parent-system directory
    # names, even if a future output layout is changed.
    for system_name in PARENT_MD_SYSTEMS:
        if any(system_name in path for path in missing_prepared):
            raise SystemExit(f"Parent-study MD system leaked into pilot path: {system_name}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    systems_path = args.output_dir / "set_c_md_pilot_systems.csv"
    with systems_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(systems[0]) if systems else [])
        writer.writeheader()
        writer.writerows(systems)

    manifest = {
        "schema_version": 1,
        "status": "PREFLIGHT_ONLY_MISSING_SET_C_COMPLEXES" if missing_prepared else "READY_FOR_EXPLICIT_REVIEW",
        "execution": {
            "gromacs_launched": False,
            "production_md_run": False,
            "reason": "This script only selects and validates a future set-C pilot; it never launches MD.",
        },
        "cohorts": {
            "set_c": {
                "source": str(SET_C_FILE.relative_to(PROJECT_DIR)),
                "n_candidates_total": int(len(set_c)),
                "selected_ids": selected["set_c_id"].tolist(),
                "purpose": "Targeted future MD pilot; distinct from parent-study MD systems.",
            },
            "parent_md_excluded": sorted(PARENT_MD_SYSTEMS),
        },
        "targets": args.targets,
        "required_mutations": {target: TARGET_MUTATIONS[target] for target in args.targets},
        "provenance": {
            "docking_file": str(DOCKING_FILE.relative_to(PROJECT_DIR)),
            "docking_rows": int(len(docking)),
            "system_table": str(systems_path.relative_to(PROJECT_DIR)),
        },
        "required_complex_files": list(REQUIRED_COMPLEX_FILES),
        "missing_prepared_complex_dirs": sorted(set(missing_prepared)),
        "selection": selected[["set_c_id", "rank", "smiles", "composite_score"]].to_dict(orient="records"),
    }
    manifest_path = args.output_dir / "set_c_md_pilot_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Set-C candidates available: {len(set_c)}")
    print(f"Selected pilot candidates: {', '.join(selected['set_c_id'])}")
    print(f"Target pairs: {', '.join(args.targets)}")
    print(f"Docking provenance rows: {len(docking)}")
    print(f"Prepared set-C complex directories missing: {len(set(missing_prepared))}")
    print(f"GROMACS launched: no")
    print(f"Manifest: {manifest_path}")
    if missing_prepared:
        print("Preflight result: FAIL-CLOSED (set-C-specific prepared complexes are absent)")
        return 2
    print("Preflight result: READY FOR EXPLICIT REVIEW (no simulation launched)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
