# Active Markdown status-consistency audit

**Date:** 12 August 2026
**Scope:** active Markdown files outside `docs/archive/`, generated outputs, dependency trees, and version-control metadata.
**Purpose:** prevent obsolete execution records or submission statuses from being mistaken for current scientific evidence.

## Verdict

**PASS for the searched active-Markdown scope — no unlabelled operational contradiction was identified.** This is a document-status audit, not an exhaustive validation of every repository file or scientific result. Historical job identifiers and exploratory states remain only where the document explicitly labels them as superseded, historical, or non-canonical. No scientific numerical result was changed by this audit.

## Current status map

| Area | Current source/status |
|---|---|
| P1 | V6 is the submission-oriented workspace (not a claim of acceptance or of completed optional validation); V4 is the frozen chemical-space baseline and V5 is the target-wise evidence/remediation layer. |
| P2 | Docking-derived RRS/ACSI/PNS are canonical. At the 12 August 2026 audit snapshot, full-panel Set-C MD-RRS remains `NOT_COMPUTED`; the isolated witness chain is `15254 → 15259 → 15260` and must not be promoted to a cohort result. Live job state must be rechecked before execution or manuscript revision. |
| P3 | Canonical benchmark and external-validation claims are controlled by `BMAD_Q1_DATA_ANALYSIS_REPORT.md` and the P3 submission manifest. |
| P4 | The v12-activity benchmark is the scalar benchmark; historical pre-activity/Pareto artifacts remain separately labelled. |
| P5 | The leak-audited benchmark and public external-validation results are controlled by `P5_DATA_ANALYSIS_REPORT.md`. |
| Zenodo | DOI `10.5281/zenodo.19608875` is reserved; upload remains pending. A reserved DOI is not described as a completed public deposit. |

## Historical records retained intentionally

The identifiers `15106`, `15111`, `15117` and related earlier Set-C attempts are retained in runbooks and audit snapshots for reproducibility. They refer to superseded workflows and are explicitly marked **DO NOT EXECUTE** where executable commands remain. The active witness chain is not a replacement for a full-panel MD-RRS result.

Older P1 V4/V5 references are retained only to define evidence provenance and workspace boundaries; they are not presented as the current P1 submission manuscript. The current submission-oriented P1 workspace is V6.

## Scientific boundary preserved

- Docking-RRS is not MD-RRS.
- A single-system witness is not a 16-system Set-C cohort.
- Pending, failed, exploratory, and historical outputs are not silently promoted to validated results.
- Submission-ready package labels refer to document/package readiness, not to completion of optional strengthening experiments.

## Validation performed

The audit searched active Markdown for:

1. superseded P2 job IDs and their surrounding status language;
2. claims that Zenodo was published or fully deposited;
3. stale P1 V4/V5 canonical-submission claims;
4. claims that full-panel MD-RRS was complete;
5. current P2 chain and `NOT_COMPUTED` boundary statements.

Formatting and archive checks completed after the Markdown restructuring:

- `git diff --check` passed;
- `docs/archive/md_full_20260812/SHA256SUMS` verified;
- `docs/archive/readmes_20260812/SHA256SUMS` verified;
- archived documents were not modified.

## Maintenance rule

When a new job finishes, update the appropriate active DAR first with a dated checkpoint containing the job ID, input/output paths, provenance, and status. Then update the roadmap or README only if the status is stable. Historical runbooks must not be repurposed as live launch instructions without removing their superseded-chain warning and recording a new provenance block.
