# P1–P6 pre-submission workflow notice — 09 August 2026

## Author decision

Until the author explicitly confirms that the relevant manuscript has been submitted **and** explicitly requests reactivation of submission/review restrictions:

> **No editorial, submission, independent-review, signature, or promotion restriction blocks scientific work.**

This applies to ongoing calculations, reruns, sensitivity analyses, debugging, figures, data integration, RRS/PNS/ACSI exploratory analyses, and manuscript refinement across P1–P5. P2–P5 inherit the root phase decision; their project-specific scientific QC and execution requirements remain active. The phase switch explicitly records `development_execution_authorized=true`.

## What remains active

Scientific quality control is not suspended. The following remain mandatory:

- correct target/PDB/isoform identity;
- receptor and ligand frame equivalence;
- input and cohort completeness;
- SHA-256/provenance and reproducibility checks;
- geometric and biological-anchor gates;
- finite and internally consistent numerical results;
- detection and reporting of software, scheduler, or environment failures;
- honest separation of raw, exploratory, reviewed, and experimental evidence.

A failed scientific check is a finding to investigate and fix. It is not an editorial restriction, and it does not authorize silently ignoring the problem.

## Truthful status labels

Registers may remain `PENDING_INDEPENDENT_REVIEW` with `accepted_for_full_run=false` and `internal_work_authorized=false`. Exploratory outputs may remain labeled `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY` or `EXPLORATORY_UNVERIFIED_VOID_FOR_SUBMISSION`. These labels describe evidence provenance; they do not prohibit continued science or manuscript drafting. `internal_work_authorized=false` does not override the phase-level `development_execution_authorized=true`; it only prevents an unreviewed register from being mistaken for independent acceptance.

No script, register, README, roadmap, report, or manuscript note may state that work is automatically blocked before submission. The phrase “submission restrictions” refers only to the dormant post-submission policy described below.

## Explicit reactivation trigger

Submission does **not** automatically activate restrictions. Reactivation requires a later author instruction that explicitly confirms both:

1. the relevant manuscript has been submitted; and
2. submission/review restrictions should now be reactivated.

Until that instruction, the phase remains `PRE_SUBMISSION_DEVELOPMENT`, `editorial_submission_restrictions_active=false`, and `submission_restrictions_reactivation_requested=false`.

When the author gives that instruction, update the phase file and record the date and scope. Only then may signed independent review become a submission-facing promotion requirement.
