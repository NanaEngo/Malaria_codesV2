#!/usr/bin/env python3
"""P1 V6 evidence-integrity audit.

Checks V5's 17x4 raw Vina evidence, the V5 independent-review register,
and P2's corrected 17-member RRS cohort. The script creates an explicit
candidate manifest by canonical-SMILES matching; it never signs or accepts
the independent-review register and never computes downstream scores.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
V5 = REPO / "Project1_Chem_space_antimalarial_V5_CorrectedGrid"
P2 = REPO / "Project2_Polypharmacology_MD_ValidationV2607"
REGISTER = V5 / "results/structural_pocket_independent_review.json"
V5_TABLE = V5 / "results/v5_four_target_vina_review_table.json"
V5_CSV = V5 / "results/v5_four_target_vina_affinities.csv"
V5_MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
P2_CANDIDATES = P2 / "results/candidate_selection/md_top20_candidates_polypharm.csv"
RRS = P2 / "results/c_rrs_classification.csv"
RAW_RRS = P2 / "results/docking_mutants.csv"
CROSS = P2 / "results/metrics/cross_metric_matrix.csv"
RAW_TARGETS = {
    "PfDHFR": V5 / "results/vina_dock_7F3Y_PfDHFR_17/vina_dock_7F3Y_PfDHFR.csv",
    "PfCRT": V5 / "results/vina_dock_6UKJ_PfCRT_17/vina_dock_6UKJ_PfCRT.csv",
    "PfClpP": V5 / "results/vina_dock_2F6I_PfClpP_17/vina_dock_2F6I_PfClpP.csv",
    "PfATP4": V5 / "results/vina_dock_9N10_PfATP4_17/vina_dock_9N10_PfATP4.csv",
}

TARGETS = ["PfDHFR", "PfCRT", "PfClpP", "PfATP4"]
MUTATIONS = ["RRS_N51I", "RRS_C59R", "RRS_S108N", "RRS_I164L", "RRS_K76T", "RRS_K76A"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def display_path(path: Path) -> str:
    """Use a stable repository-relative label for paths from V4/V5/P2."""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def check_file(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"MISSING:{display_path(path)}")
        return {"path": display_path(path), "exists": False}
    if path.stat().st_size == 0:
        errors.append(f"EMPTY:{display_path(path)}")
    return {
        "path": display_path(path),
        "exists": True,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def canonical_smiles(smiles: str) -> str:
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"unparseable SMILES: {smiles}")
    return Chem.MolToSmiles(mol, canonical=True)


def load_v5_candidate_map(errors: list[str]) -> dict[str, dict[str, str]]:
    """Return candidate_id -> source/canonical SMILES from the V5 manifest."""
    if not V5_MANIFEST.exists():
        errors.append(f"MISSING:{display_path(V5_MANIFEST)}")
        return {}
    with V5_MANIFEST.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        cid = row.get("candidate_id", "").strip()
        smi = row.get("ligand_description", "").strip()
        if not cid or not smi:
            errors.append("V5_MANIFEST_MISSING_CANDIDATE_OR_SMILES")
            continue
        try:
            can = canonical_smiles(smi)
        except (ImportError, ValueError) as exc:
            errors.append(f"V5_MANIFEST_SMILES_ERROR:{cid}:{exc}")
            continue
        previous = mapping.get(cid)
        record = {"candidate_id": cid, "source_smiles": smi, "canonical_smiles": can}
        if previous and previous["canonical_smiles"] != can:
            errors.append(f"V5_MANIFEST_CANDIDATE_ID_HAS_MULTIPLE_SMILES:{cid}")
        mapping[cid] = record
    if len(mapping) != 17:
        errors.append(f"V5_MANIFEST_UNIQUE_CANDIDATES:{len(mapping)} != 17")
    return mapping


def load_p2_source(errors: list[str]) -> list[dict[str, str]]:
    if not P2_CANDIDATES.exists():
        errors.append(f"MISSING:{display_path(P2_CANDIDATES)}")
        return []
    with P2_CANDIDATES.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 17:
        errors.append(f"P2_SOURCE_ROW_COUNT:{len(rows)} != 17")
    for row in rows:
        try:
            row["canonical_smiles"] = canonical_smiles(row.get("smiles", ""))
        except (ImportError, ValueError) as exc:
            errors.append(f"P2_SOURCE_SMILES_ERROR:{exc}")
            row["canonical_smiles"] = ""
    return rows


def verify_raw_vina_outputs(candidate_ids: set[str], errors: list[str]) -> tuple[dict[str, dict], dict[tuple[str, str], dict]]:
    """Verify each target CSV and the raw files whose hashes it declares."""
    summary: dict[str, dict] = {}
    raw_records: dict[tuple[str, str], dict] = {}
    for target, csv_path in RAW_TARGETS.items():
        if not csv_path.exists():
            errors.append(f"MISSING_RAW_VINA_CSV:{target}:{display_path(csv_path)}")
            continue
        with csv_path.open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        ids = {r.get("candidate_id", "") for r in rows}
        if len(rows) != 17:
            errors.append(f"RAW_VINA_ROW_COUNT:{target}:{len(rows)} != 17")
        if ids != candidate_ids:
            errors.append(f"RAW_VINA_CANDIDATE_SET_MISMATCH:{target}")
        for row in rows:
            raw_records[(target, row.get("candidate_id", ""))] = row
            if row.get("target") != target:
                errors.append(f"RAW_VINA_TARGET_MISMATCH:{target}:{row.get('candidate_id')}")
            if not finite(row.get("vina_affinity_kcal_mol")):
                errors.append(f"RAW_VINA_NONFINITE_AFFINITY:{target}:{row.get('candidate_id')}")
            for path_key, hash_key in (("ligand_pdbqt", "ligand_pdbqt_sha256"), ("vina_out_pdbqt", "vina_out_pdbqt_sha256"), ("conversion_log", "conversion_log_sha256"), ("vina_log", "vina_log_sha256")):
                raw_path = row.get(path_key, "")
                expected = row.get(hash_key, "")
                if raw_path and expected:
                    p = Path(raw_path)
                    if not p.exists():
                        errors.append(f"RAW_VINA_REFERENCED_FILE_MISSING:{target}:{row.get('candidate_id')}:{path_key}")
                    elif sha256(p) != expected:
                        errors.append(f"RAW_VINA_HASH_MISMATCH:{target}:{row.get('candidate_id')}:{path_key}")
        prov = csv_path.parent / "execution_provenance.json"
        if not prov.exists():
            errors.append(f"MISSING_RAW_VINA_PROVENANCE:{target}")
        else:
            data = json.loads(prov.read_text())
            if data.get("all_rank1_pass_gate") is not True:
                errors.append(f"RAW_VINA_GATE_NOT_PASS:{target}")
            if data.get("accepted_for_full_run") is not False:
                errors.append(f"RAW_VINA_ACCEPTANCE_FLAG_NOT_FALSE:{target}")
        summary[target] = {"csv": display_path(csv_path), "rows": len(rows), "sha256": sha256(csv_path), "provenance": display_path(prov)}
    return summary, raw_records


def verify_consolidated_vina(raw_records: dict[tuple[str, str], dict], errors: list[str]) -> dict:
    """Compare the consolidated 17x4 table to the four raw target CSVs."""
    if not V5_TABLE.exists():
        return {"checked": False}
    table = json.loads(V5_TABLE.read_text())
    mismatches = 0
    rounding_differences = 0
    checked = 0
    for row in table.get("rows", []):
        cid = row.get("candidate_id", "")
        for target in TARGETS:
            raw = raw_records.get((target, cid))
            if raw is None:
                errors.append(f"CONSOLIDATED_RAW_ROW_MISSING:{target}:{cid}")
                continue
            pairs = [(f"aff_{target}", "vina_affinity_kcal_mol"), (f"gate_{target}_frac", "rank1_inside_fraction")]
            anchor_col = "rank1_triad_min_A" if target == "PfClpP" else "rank1_anchor_min_A"
            pairs.append((f"gate_{target}_anchor_min_A", anchor_col))
            for table_key, raw_key in pairs:
                if not finite(row.get(table_key)) or not finite(raw.get(raw_key)):
                    errors.append(f"CONSOLIDATED_NONFINITE:{target}:{cid}:{table_key}")
                    continue
                diff = abs(float(row[table_key]) - float(raw[raw_key]))
                # The review table is a presentation artifact rounded to two/three
                # decimals; raw CSVs are the authoritative values. Differences up
                # to half a displayed unit are recorded, not treated as corruption.
                if diff > 5.1e-3:
                    errors.append(f"CONSOLIDATED_RAW_VALUE_MISMATCH:{target}:{cid}:{table_key}")
                    mismatches += 1
                elif diff > 0:
                    rounding_differences += 1
                checked += 1
            table_bool = str(row.get(f"gate_{target}_frac", "")) != ""
            if raw.get("rank1_centroid_in_box", "").lower() not in {"true", "false", "1", "0"}:
                errors.append(f"RAW_VINA_BAD_CENTROID_FLAG:{target}:{cid}")
    return {"checked_values": checked, "mismatches": mismatches, "rounding_differences": rounding_differences, "consistent": mismatches == 0}


def classify_rrs(values: list[float], dg_wt_anchor: float) -> str:
    if not values:
        return "D"
    if all(v >= 80 for v in values) and min(values) >= 70:
        return "A*" if abs(dg_wt_anchor) >= 7.0 else "A"
    if all(v >= 70 for v in values):
        return "B"
    if any(v >= 80 for v in values):
        return "C"
    return "D"


def verify_rrs_recomputation(candidate_smiles: set[str], errors: list[str]) -> dict:
    """Recompute corrected per-target RRS and classes from raw mutant docking."""
    if not RAW_RRS.exists() or not RRS.exists():
        return {"recomputed": False}
    with RAW_RRS.open(newline="") as fh:
        raw_rows = list(csv.DictReader(fh))
    with RRS.open(newline="") as fh:
        published = list(csv.DictReader(fh))
    raw_by: dict[str, list[dict[str, str]]] = {}
    for row in raw_rows:
        try:
            can = canonical_smiles(row.get("smiles", ""))
        except (ImportError, ValueError):
            continue
        raw_by.setdefault(can, []).append(row)
    pub_by = {}
    for row in published:
        try:
            pub_by[canonical_smiles(row.get("smiles", ""))] = row
        except (ImportError, ValueError):
            errors.append("RRS_PUBLISHED_UNPARSEABLE_SMILES")
    mismatches = 0
    checked = 0
    for can in candidate_smiles:
        rows = raw_by.get(can, [])
        if not rows or can not in pub_by:
            errors.append(f"RRS_RECOMPUTE_CANDIDATE_MISSING:{can[:24]}")
            continue
        wt_by_target: dict[str, float] = {}
        for target in {"PfDHFR", "PfCRT"}:
            vals = [float(r["vina_score"]) for r in rows if r.get("target") == target and r.get("mutation") == "WT" and finite(r.get("vina_score"))]
            if len(vals) != 1:
                errors.append(f"RRS_RECOMPUTE_WT_COUNT:{target}:{can[:24]}")
            elif abs(vals[0]) >= 5.0:
                wt_by_target[target] = vals[0]
        ratios: dict[str, float] = {}
        for mutation in ["N51I", "C59R", "S108N", "I164L", "K76T", "K76A"]:
            vals = []
            for target, wt in wt_by_target.items():
                mut = [float(r["vina_score"]) for r in rows if r.get("target") == target and r.get("mutation") == mutation and finite(r.get("vina_score"))]
                if len(mut) == 1:
                    vals.append(abs(mut[0]) / abs(wt) * 100.0)
            if vals:
                ratios[mutation] = sum(vals) / len(vals)
        mean = sum(ratios.values()) / len(ratios) if ratios else float("nan")
        anchor = max(wt_by_target.values(), key=abs) if wt_by_target else float("nan")
        expected_class = classify_rrs(list(ratios.values()), anchor)
        pub = pub_by[can]
        if not finite(pub.get("RRS_mean")) or abs(float(pub["RRS_mean"]) - mean) > 1e-6:
            errors.append(f"RRS_MEAN_MISMATCH:{can[:24]}")
            mismatches += 1
        if pub.get("RRS_class") != expected_class:
            errors.append(f"RRS_CLASS_MISMATCH:{can[:24]}:{pub.get('RRS_class')}!={expected_class}")
            mismatches += 1
        for mutation, expected in ratios.items():
            key = f"RRS_{mutation}"
            if not finite(pub.get(key)) or abs(float(pub[key]) - expected) > 1e-6:
                errors.append(f"RRS_VALUE_MISMATCH:{can[:24]}:{mutation}")
                mismatches += 1
            checked += 1
    return {"recomputed": True, "checked_values": checked, "mismatches": mismatches, "consistent": mismatches == 0}


def write_candidate_manifest(v5_map: dict[str, dict[str, str]], p2_rows: list[dict[str, str]], errors: list[str], out: Path) -> dict:
    by_can = {r.get("canonical_smiles"): r for r in p2_rows if r.get("canonical_smiles")}
    rows = []
    for cid, v5 in sorted(v5_map.items()):
        p2 = by_can.get(v5["canonical_smiles"])
        if p2 is None:
            errors.append(f"CANDIDATE_SMILES_NOT_FOUND_IN_P2:{cid}")
            continue
        rows.append({
            "candidate_id": cid,
            "canonical_smiles": v5["canonical_smiles"],
            "v5_source_smiles": v5["source_smiles"],
            "p2_source_rank": p2.get("rank", ""),
            "p2_source_smiles": p2.get("smiles", ""),
            "p2_source_sha256": sha256(P2_CANDIDATES),
            "cohort_id": "P2_SET_C_POLYPHARM_17",
        })
    if len(rows) != 17:
        errors.append(f"V6_CANDIDATE_MANIFEST_ROWS:{len(rows)} != 17")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["candidate_id", "canonical_smiles"])
        writer.writeheader()
        writer.writerows(rows)
    return {"rows": len(rows), "sha256": sha256(out) if out.exists() else None, "path": display_path(out)}


def verify_raw_rrs(candidate_smiles: set[str], errors: list[str]) -> dict:
    """Verify the complete raw WT/mutant panel used for corrected RRS."""
    if not RAW_RRS.exists():
        errors.append(f"MISSING:{display_path(RAW_RRS)}")
        return {"path": display_path(RAW_RRS), "rows": 0, "complete": False}
    with RAW_RRS.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    required = {"smiles", "target", "mutation", "vina_score"}
    if rows:
        missing = required - set(rows[0])
        if missing:
            errors.append(f"RAW_RRS_MISSING_COLUMNS:{sorted(missing)}")
    observed = set()
    for r in rows:
        try:
            observed.add(canonical_smiles(r.get("smiles", "")))
        except (ImportError, ValueError) as exc:
            errors.append(f"RAW_RRS_SMILES_ERROR:{exc}")
    if len(rows) != 136:
        errors.append(f"RAW_RRS_ROW_COUNT:{len(rows)} != 136")
    if observed != candidate_smiles:
        errors.append("RAW_RRS_CANDIDATE_SET_MISMATCH")
    keys = []
    for r in rows:
        try:
            keys.append((canonical_smiles(r.get("smiles", "")), r.get("target"), r.get("mutation")))
        except (ImportError, ValueError):
            keys.append((r.get("smiles"), r.get("target"), r.get("mutation")))
    if len(set(keys)) != len(keys):
        errors.append("RAW_RRS_DUPLICATE_CANDIDATE_TARGET_MUTATION")
    expected = {"PfDHFR": {"WT", "N51I", "C59R", "S108N", "I164L"}, "PfCRT": {"WT", "K76T", "K76A"}}
    for target, mutations in expected.items():
        for smi in candidate_smiles:
            got = set()
            for r in rows:
                try:
                    r_can = canonical_smiles(r.get("smiles", ""))
                except (ImportError, ValueError):
                    continue
                if r_can == smi and r.get("target") == target:
                    got.add(r.get("mutation"))
            if got != mutations:
                errors.append(f"RAW_RRS_PANEL_MISMATCH:{target}")
    return {"path": display_path(RAW_RRS), "rows": len(rows), "sha256": sha256(RAW_RRS), "complete": not any(e.startswith("RAW_RRS_") for e in errors)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=ROOT / "results/validation/v6_integrity_audit.json")
    ap.add_argument("--dossier", type=Path, default=ROOT / "results/validation/v6_review_dossier.md")
    ap.add_argument("--candidate-manifest", type=Path, default=ROOT / "results/v6_candidate_manifest.csv")
    args = ap.parse_args()

    # Never leave a stale candidate manifest after a failed audit.
    args.candidate_manifest.unlink(missing_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    source_paths = [REGISTER, V5_TABLE, V5_CSV, V5_MANIFEST, P2_CANDIDATES, RAW_RRS, RRS, CROSS]
    files = {display_path(p): check_file(p, errors) for p in source_paths}

    register = json.loads(REGISTER.read_text()) if REGISTER.exists() else {}
    if not bool(register.get("accepted_for_full_run", False)):
        warnings.append("INDEPENDENT_REVIEW_PENDING: automated audit cannot authorize downstream claims")
    if register.get("authorization", {}).get("internal_work_authorized") is not False:
        errors.append("V5_REGISTER_AUTHORIZATION_NOT_EXPLICITLY_FALSE")

    candidate_v5: list[str] = []
    if V5_CSV.exists():
        with V5_CSV.open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        required = {"candidate_id", *(f"aff_{t}" for t in TARGETS)}
        missing = required - set(rows[0]) if rows else required
        if missing:
            errors.append(f"V5_CSV_MISSING_COLUMNS:{sorted(missing)}")
        candidate_v5 = [r.get("candidate_id", "") for r in rows]
        if len(rows) != 17:
            errors.append(f"V5_CSV_ROW_COUNT:{len(rows)} != 17")
        if len(set(candidate_v5)) != len(candidate_v5):
            errors.append("V5_CSV_DUPLICATE_CANDIDATES")
        for r in rows:
            for t in TARGETS:
                if not finite(r.get(f"aff_{t}")):
                    errors.append(f"V5_CSV_NONFINITE:{r.get('candidate_id')}:{t}")

    candidate_table: list[str] = []
    if V5_TABLE.exists():
        table = json.loads(V5_TABLE.read_text())
        if table.get("status") != "RAW_DATA_ARTIFACT_FOR_INDEPENDENT_REVIEW":
            warnings.append(f"V5_TABLE_STATUS:{table.get('status')}")
        for t in TARGETS:
            if table.get("completeness", {}).get(t) != "COMPLETE_17":
                errors.append(f"V5_TABLE_INCOMPLETE:{t}")
            if not table.get("targets", {}).get(t, {}).get("pdb"):
                errors.append(f"V5_TABLE_MISSING_PDB:{t}")
        candidate_table = [r.get("candidate_id", "") for r in table.get("rows", [])]
        if len(candidate_table) != 17:
            errors.append(f"V5_TABLE_ROW_COUNT:{len(candidate_table)} != 17")
        for r in table.get("rows", []):
            for t in TARGETS:
                if not finite(r.get(f"aff_{t}")):
                    errors.append(f"V5_TABLE_NONFINITE:{r.get('candidate_id')}:{t}")

    v5_map = load_v5_candidate_map(errors)
    p2_source = load_p2_source(errors)
    manifest_info = write_candidate_manifest(v5_map, p2_source, errors, args.candidate_manifest)
    raw_vina, raw_vina_records = verify_raw_vina_outputs(set(candidate_v5), errors)
    consolidated_vina = verify_consolidated_vina(raw_vina_records, errors)
    raw_rrs = verify_raw_rrs(set(r["canonical_smiles"] for r in p2_source if r.get("canonical_smiles")), errors)
    if candidate_v5 and set(candidate_v5) != set(v5_map):
        errors.append("V5_CSV_MANIFEST_CANDIDATE_SET_MISMATCH")
    if candidate_v5 and candidate_table and set(candidate_v5) != set(candidate_table):
        errors.append("V5_CSV_TABLE_CANDIDATE_SET_MISMATCH")

    candidate_rrs: list[str] = []
    if RRS.exists():
        with RRS.open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        required = {"cohort_id", "candidate_file", "candidate_sha256", "smiles", "RRS_mean", "RRS_class", *MUTATIONS}
        missing = required - set(rows[0]) if rows else required
        if missing:
            errors.append(f"RRS_MISSING_COLUMNS:{sorted(missing)}")
        candidate_rrs = []
        for r in rows:
            try:
                candidate_rrs.append(canonical_smiles(r.get("smiles", "")))
            except (ImportError, ValueError) as exc:
                errors.append(f"RRS_SMILES_ERROR:{exc}")
            if not finite(r.get("RRS_mean")):
                errors.append("RRS_NONFINITE")
            if not r.get("candidate_sha256"):
                errors.append("RRS_MISSING_CANDIDATE_HASH")
        if len(rows) != 17:
            errors.append(f"RRS_ROW_COUNT:{len(rows)} != 17")
        if {r.get("cohort_id") for r in rows} != {"P2_SET_C_POLYPHARM_17"}:
            errors.append("RRS_COHORT_ID_MISMATCH")

    manifest_can = {r["canonical_smiles"] for r in csv.DictReader(args.candidate_manifest.open())} if args.candidate_manifest.exists() else set()
    if manifest_can and set(candidate_rrs) != manifest_can:
        errors.append("P2_RRS_V5_CANONICAL_SMILES_SET_MISMATCH")
    else:
        warnings.append("RRS_V5_JOIN_VERIFIED_BY_CANONICAL_SMILES")
    rrs_recomputation = verify_rrs_recomputation(set(candidate_rrs), errors)

    if CROSS.exists():
        with CROSS.open(newline="") as fh:
            if len(list(csv.reader(fh))) < 5:
                errors.append("CROSS_METRIC_MATRIX_TOO_FEW_ROWS")

    anchors = {}
    for target, entry in register.get("targets", {}).items():
        anchors[target] = {"pdb_id": entry.get("pdb_id"), "decision": entry.get("decision"), "anchor": entry.get("anchor")}
        if target in TARGETS and not entry.get("anchor"):
            errors.append(f"V5_REGISTER_MISSING_ANCHOR:{target}")

    status = "AUDIT_FAIL_REVIEW_BLOCKED" if errors else ("AUDIT_WARN_REVIEW_REQUIRED" if warnings else "AUDIT_PASS_REVIEW_REQUIRED")
    result = {
        "schema": "p1-v6-evidence-integrity-audit/v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "independent_review_required": True,
        "accepted_for_full_run": False,
        "self_authorization_forbidden": True,
        "errors": errors,
        "warnings": warnings,
        "files": files,
        "candidate_manifest": manifest_info,
        "raw_vina_outputs": raw_vina,
        "consolidated_vina": consolidated_vina,
        "raw_rrs": raw_rrs,
        "rrs_recomputation": rrs_recomputation,
        "targets": anchors,
        "candidate_counts": {"v5_affinity_csv": len(candidate_v5), "v5_review_table": len(candidate_table), "v5_manifest": len(v5_map), "p2_source": len(p2_source), "p2_rrs": len(candidate_rrs)},
        "prohibited_actions_until_human_signature": ["final V6 consensus promotion", "integrated RRS/PNS manuscript claims", "editing the register to simulate acceptance"],
    }
    if errors:
        args.candidate_manifest.unlink(missing_ok=True)
        result["candidate_manifest"]["usable"] = False
    else:
        result["candidate_manifest"]["usable"] = True
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    dossier = ["# V6 Evidence-Integrity Review Dossier", "", f"- Automated status: `{status}`", "- Independent review: **REQUIRED; not performed by this script**", "- Independent acceptance: `false`", "", "## Scope", "", "This dossier checks file integrity, schema, counts, target metadata, canonical-SMILES cohort identity, and the hashes declared by the raw per-target Vina outputs. It does not certify biological validity, experimental binding, or independent scientific acceptance.", "", "## Target evidence", ""]
    dossier += [f"- **{t} ({i.get('pdb_id')})** — decision `{i.get('decision')}`; anchor: {i.get('anchor')}" for t, i in anchors.items()]
    dossier += ["", "## Automated findings", ""]
    dossier += [f"- ERROR: `{e}`" for e in errors] or ["- No automated integrity errors detected."]
    dossier += [f"- WARNING: `{w}`" for w in warnings]
    dossier += ["", "## Human reviewer action", "", "Inspect the raw structures, poses, configurations, and hashes independently. Then create the signed artifact specified in `docs/INDEPENDENT_REVIEW_PROTOCOL.md`. This script cannot sign the register or authorize downstream analysis.", ""]
    args.dossier.parent.mkdir(parents=True, exist_ok=True)
    args.dossier.write_text("\n".join(dossier))

    print(json.dumps({"status": status, "errors": len(errors), "warnings": len(warnings), "audit": display_path(args.output), "dossier": display_path(args.dossier), "candidate_manifest": display_path(args.candidate_manifest)}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
