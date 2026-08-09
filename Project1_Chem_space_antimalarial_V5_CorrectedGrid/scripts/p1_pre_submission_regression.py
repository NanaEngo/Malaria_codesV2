#!/usr/bin/env python3
"""Regression checks for the P1 pre-submission execution policy.

This test is intentionally dependency-light and never edits the real phase file
or review registers. It verifies that exploratory work is enabled only in the
pre-submission phase and that the current unsigned V5/V6 registers remain
closed to cryptographic promotion.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    policy = load(
        "p1_policy_regression",
        ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_development_policy.py",
    )
    phase = json.loads((ROOT / "P1_DEVELOPMENT_PHASE.json").read_text(encoding="utf-8"))
    if not policy.is_pre_submission():
        raise AssertionError("current development phase must allow pre-submission work")

    post = dict(phase)
    post["phase"] = "POST_SUBMISSION_REVIEW"
    post["exploratory_internal_work_enabled"] = False
    with tempfile.TemporaryDirectory() as tmp:
        phase_copy = Path(tmp) / "P1_DEVELOPMENT_PHASE.json"
        phase_copy.write_text(json.dumps(post), encoding="utf-8")
        original_phase_file = policy.PHASE_FILE
        policy.PHASE_FILE = phase_copy
        try:
            if policy.is_pre_submission():
                raise AssertionError("post-submission phase unexpectedly enables exploratory work")
            if policy.is_submission_reactivation_active():
                raise AssertionError("post-submission phase without explicit reactivation unexpectedly enabled promotion")

            # Missing explicit authorization must fail closed rather than
            # inheriting permission from an old phase-file schema.
            legacy = dict(phase)
            legacy.pop("development_execution_authorized", None)
            phase_copy.write_text(json.dumps(legacy), encoding="utf-8")
            if policy.is_pre_submission():
                raise AssertionError("phase without explicit development authorization unexpectedly enabled work")
        finally:
            policy.PHASE_FILE = original_phase_file

    # Tamper simulation: even if a pending register is edited to claim
    # acceptance, the cryptographic gate must remain closed. The real register
    # is never modified.
    v5_register = ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/structural_pocket_independent_review.json"
    v6_register = ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/v6_review_register.json"
    with tempfile.TemporaryDirectory() as tmp:
        tampered_v5 = Path(tmp) / "v5.json"
        v5_data = json.loads(v5_register.read_text(encoding="utf-8"))
        v5_data["accepted_for_full_run"] = True
        tampered_v5.write_text(json.dumps(v5_data), encoding="utf-8")
        tampered_v6 = Path(tmp) / "v6.json"
        v6_data = json.loads(v6_register.read_text(encoding="utf-8"))
        v6_data["accepted_for_full_run"] = True
        tampered_v6.write_text(json.dumps(v6_data), encoding="utf-8")

        v5_gate = load(
            "p1_v5_gate_regression",
            ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_consensus_rrs_gate.py",
        )
        v6_gate = load(
            "p1_v6_gate_regression",
            ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid/scripts/v6_review_gate.py",
        )
        v5_ok, v5_message = v5_gate.check_gate(tampered_v5)
        v6_ok, v6_message = v6_gate.check_gate(tampered_v6)
        if v5_ok or v6_ok:
            raise AssertionError("tampered acceptance bit opened a cryptographic gate")

    # Future signature application must stay dormant until explicit author
    # reactivation; this test uses no signature files and never edits registers.
    load(
        "p1_v5_apply_review_signature_regression",
        ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_apply_review_signature.py",
    )
    if not policy.is_pre_submission() or policy.is_submission_reactivation_active():
        raise AssertionError("phase unexpectedly changed before dormant-application test")

    # Use the V5 provenance helper directly to prove that exploratory output
    # cannot mirror a tampered acceptance field.
    figures = load(
        "p1_v5_figures_regression",
        ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_generate_figures.py",
    )
    v6_generator = load(
        "p1_v6_generator_regression",
        ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid/scripts/v6_generate_integrated_data_figures.py",
    )
    tampered = json.loads(v5_register.read_text(encoding="utf-8"))
    tampered["accepted_for_full_run"] = True
    tampered["status"] = "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED"
    provenance = figures.review_gate_provenance(tampered, pre_submission=True)
    if provenance["accepted_for_full_run"] is not False:
        raise AssertionError("exploratory provenance mirrored tampered acceptance")
    v6_provenance = v6_generator.review_gate_provenance(
        {"v5": {"status": "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED", "accepted_for_full_run": True},
         "v6": {"status": "INDEPENDENT_REVIEW_ACCEPTED", "accepted_for_full_run": True}},
        exploratory=True,
    )
    if v6_provenance["v5_accepted_for_full_run"] is not False or v6_provenance["v6_accepted_for_full_run"] is not False or v6_provenance["submission_eligible"] is not False:
        raise AssertionError("V6 exploratory provenance mirrored tampered acceptance")

    v5_gate = load(
        "p1_v5_gate_regression_final",
        ROOT / "Project1_Chem_space_antimalarial_V5_CorrectedGrid/scripts/p1_v5_consensus_rrs_gate.py",
    )
    v6_gate = load(
        "p1_v6_gate_regression",
        ROOT / "Project1_Chem_space_antimalarial_V6_CorrectedGrid/scripts/v6_review_gate.py",
    )
    v5_ok, v5_message = v5_gate.check_gate(v5_register)
    v6_ok, v6_message = v6_gate.check_gate(v6_register)
    if not v5_ok:
        raise AssertionError("pre-submission V5 scientific development unexpectedly blocked: " + v5_message)
    if v6_ok:
        raise AssertionError("unsigned V6 review register unexpectedly opened a promotion gate")
    print("PASS: pre-submission scientific development enabled; V6 promotion gate remains closed; registers remain pending")
    print(v5_message)
    print(v6_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
