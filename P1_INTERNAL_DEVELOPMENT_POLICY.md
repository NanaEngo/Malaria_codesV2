# P1 Internal Development Policy — Author-controlled pre-submission mode

**Decision (09 August 2026):** Until the author explicitly states that the manuscript has been submitted and requests reactivation, **no editorial, submission, or independent-review restriction blocks scientific development**. P1 V4/V5/V6/V7 analyses, reruns, sensitivity analyses, figures, manuscript refinement, consensus calculations, RRS/PNS exploratory analyses, and debugging may proceed while the work remains under development. The machine-readable phase switch records `development_execution_authorized=true`.

This policy does **not** waive scientific quality control. Target identity, receptor/frame integrity, hashes, input completeness, geometric gates, finite scores, provenance, and genuine software failures remain mandatory diagnostics. A failed scientific QC is reported and corrected; it is not treated as an editorial restriction.

The review registers remain truthful: pending review is still recorded as pending, and outputs are not silently relabeled as independently reviewed. `PENDING_INDEPENDENT_REVIEW`, `accepted_for_full_run=false`, `internal_work_authorized=false`, and `*_NOT_SUBMISSION_READY` are provenance labels during development, not commands to stop computation or drafting. `internal_work_authorized=false` means that independent-review acceptance is not being asserted; it does not revoke development execution authorization.

**Reactivation is manual and author-controlled.** Submission does not switch the workflow automatically. Only an explicit author instruction may set `submission_restrictions_reactivation_requested=true` and activate the post-submission review policy. Until that instruction is given, all development routes remain available.

## Active phase

The project is currently in the **author-controlled pre-submission development phase**, recorded in the root phase switch `P1_DEVELOPMENT_PHASE.json`. P2, P3, P4, and P5 inherit this root development authorization for scientific work; their own scientific QC, provenance, and project-specific execution requirements remain applicable.

During this phase, `development_execution_authorized=true`: no independent-review signature is required to execute scientific development. The registers remain pending so that they do not falsely claim review acceptance.

## Scientific QC versus editorial status

- **Always active:** data integrity, target/PDB identity, frame equivalence, hashes, manifests, numerical finiteness, geometric/biological gate checks, provenance, and software error handling.
- **Inactive until explicitly requested:** editorial submission gates, signature prerequisites for development execution, and promotion restrictions that exist solely because a manuscript may later be submitted.
- **Status labels only:** `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY`, `EXPLORATORY_UNVERIFIED_VOID_FOR_SUBMISSION`, and `PENDING_INDEPENDENT_REVIEW` describe provenance. They do not prohibit computation, reruns, figures, or manuscript drafting.
- **Scientific failures remain real:** a failed target-identity, geometry, hash, or runtime check must be fixed or transparently bounded before a result is described as scientifically valid. This is scientific work, not an editorial block.

## Development outputs

The existing scripts may route exploratory outputs to `results/exploratory/` to prevent accidental overwriting of canonical artifacts. This is a provenance safeguard, not a restriction on the work. Exploratory outputs may guide debugging, figures, hypothesis generation, RRS/PNS analysis, and manuscript drafting, provided their status is described accurately.

```bash
# Normal pre-submission development invocation
python scripts/p1_v5_consensus_scoring.py
python scripts/p1_v5_rrs_pilot.py

# Optional explicit quarantine marker; not required in this phase
python scripts/p1_v5_consensus_scoring.py --internal-development
```

## Post-submission policy — dormant until explicitly activated

The post-submission policy is **not activated automatically**. It becomes active only after both conditions are met:

1. the author explicitly confirms that the relevant manuscript has been submitted; and
2. the author explicitly requests reactivation of submission/review restrictions.

At that point, update `P1_DEVELOPMENT_PHASE.json` with the author instruction and use the signed, hash-bound review gates for new submission-facing claims, revisions, or responses to reviewers. Until then, no script should refuse scientific development merely because a review signature is absent.

This policy therefore preserves scientific freedom now while preserving truthful provenance and a clearly documented future submission-control procedure.
