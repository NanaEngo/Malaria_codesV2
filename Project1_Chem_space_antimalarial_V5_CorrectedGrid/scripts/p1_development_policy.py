"""Shared P1 development/submission phase policy.

The phase controls whether independent-review signatures block computation. It
never changes the review registers or turns exploratory results into accepted
submission evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PHASE_FILE = REPO / "P1_DEVELOPMENT_PHASE.json"
PRE_SUBMISSION = "PRE_SUBMISSION_DEVELOPMENT"
POST_SUBMISSION = "POST_SUBMISSION_REVIEW"


def read_phase() -> dict:
    try:
        phase = json.loads(PHASE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"development phase file unreadable: {exc}") from exc
    if phase.get("phase") not in {PRE_SUBMISSION, POST_SUBMISSION}:
        raise RuntimeError(f"unsupported development phase: {phase.get('phase')!r}")
    return phase


def is_pre_submission() -> bool:
    """Return whether author-controlled development is currently unrestricted.

    ``development_execution_authorized`` is the explicit operational switch.
    The legacy exploratory flag remains required for backward compatibility;
    both are phase-level permissions, not evidence-acceptance claims.
    """
    phase = read_phase()
    return (
        phase["phase"] == PRE_SUBMISSION
        and phase.get("exploratory_internal_work_enabled") is True
        and phase.get("development_execution_authorized") is True
        and phase.get("scientific_qc_enabled") is True
        and phase.get("editorial_submission_restrictions_active") is False
        and phase.get("submission_restrictions_reactivation_requested") is False
    )


def phase_name() -> str:
    return read_phase()["phase"]


def is_submission_reactivation_active() -> bool:
    """Return true only after the author explicitly activates post-submission controls."""
    phase = read_phase()
    return (
        phase.get("phase") == POST_SUBMISSION
        and phase.get("scientific_qc_enabled") is True
        and phase.get("editorial_submission_restrictions_active") is True
        and phase.get("submission_restrictions_reactivation_requested") is True
        and phase.get("automatic_post_submission_switch") is False
    )
