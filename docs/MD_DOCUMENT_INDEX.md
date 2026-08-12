# Markdown document index

**Updated:** 12 August 2026
**Purpose:** one short entry point for current scientific status and operational decisions.

## Active sources of truth

| Scope | Active document | Use it for |
|---|---|---|
| P1–P3 data analysis | `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | Validated results, evidence boundaries, and remaining actions |
| P4 data analysis | `P4_DATA_ANALYSIS_REPORT.md` | MCTS/Pareto/QMC results and P4 limitations |
| P5 data analysis | `P5_DATA_ANALYSIS_REPORT.md` | GNN/Transformer benchmark and external validation |
| Cross-project plan | `P1_P5_RRS_POLYPHARMA_ROADMAP.md` | Current milestones and next actions only |
| Operational rules | `AGENTS.md` | Canonical paths, provenance rules, active jobs, and execution policy |
| Submission overview | `README_SUBMISSION.md` | Package status and submission checklists |
| Scientific questions | `CENTRAL_QUESTIONS_PROJECTS.md` | Questions, estimands, and answer-level results |
| Markdown status audit | `MD_STATUS_CONSISTENCY_AUDIT_20260812.md` | Current-vs-historical status boundaries and audit verdict |
| Scientific consistency audit | `SCIENTIFIC_CONSISTENCY_AUDIT_20260812.md` | Final cross-project check of scientific claims, cohorts, denominators, and estimands |
| Historical audit index | `docs/HISTORICAL_AUDIT_INDEX.md` | Single classification map for dated audits, reviews, dossiers, and execution snapshots |

## Secondary documents

- `MD_STATUS_CONSISTENCY_AUDIT_20260812.md` is the concise status-consistency audit; it records the current-vs-historical boundary without replacing any DAR.
- `docs/HISTORICAL_AUDIT_INDEX.md` is the single navigation index for remaining dated audits, reviews, provenance dossiers, and execution checkpoints. It classifies them without promoting them to evidence sources.
- `ACCEPTANCE_ASSESSMENT_20260810.md` and `FINAL_CROSS_REVIEW_20260810.md` are dated assessment snapshots. They are useful for audit history but do not override the active DARs.
- `P5_STRATEGIC_PA90.md` is a planning document; its milestones do not override measured P5 results.
- `Project2_Polypharmacology_MD_ValidationV2607/scripts/P2_MD_RRS_INTEGRATION_PLAN.md` is an integration plan; its old job chain is historical and the live status is in the BMAD DAR.
- `Project2_Polypharmacology_MD_ValidationV2607/P2_SLURM_DOCUMENTATION_AUDIT_20260812.md` records the static SLURM/path audit, the 16-versus-136 MD-RRS cardinality blocker, and the prioritized P2 remediation plan; it does not authorize execution.
- `Project2_Polypharmacology_MD_ValidationV2607/manuscript/LaTeX/SUBMISSION_MANIFEST.md` is a package manifest, not a scientific source of truth.
- `Project2_Polypharmacology_MD_ValidationV2607/results/set_c_md/setc_md_rrs_execution_runbook.md` and `setc_post_production_runbook.md` are execution runbooks. Their job IDs are historical unless a newer checkpoint explicitly supersedes them.
- Project-level `README.md` files are orientation documents; numerical claims must be checked against the active DAR.
- `graphify-out/` reports and dependency `README.md` files are generated/third-party material, not project evidence.

## Current project files

- **P1:** `Project1_Chem_space_antimalarial_V6_CorrectedGrid/` is the submission-oriented workspace; V4/V5 remain evidence and remediation workspaces.
- **P2:** `Project2_Polypharmacology_MD_ValidationV2607/` is the canonical polypharmacology/RRS workspace.
- **P3:** `Project3_Quantum_Inspired_RepresentationsV2607/` is canonical; V2607 manuscript sources are archived inside that project.
- **P4:** `Project4_Advanced_Monte_CarloV2607/` is canonical; v12-activity is the scalar benchmark.
- **P5:** `Project5_GNN_Transformer_DrugDiscovery/` is canonical; V2608 is the manuscript version.

## Archive policy

The long-form versions of the five operational documents were preserved unchanged on 12 August 2026 in:

`docs/archive/md_full_20260812/` (verified by `SHA256SUMS`).

The pre-condensation root/P1–P5, submission, and Zenodo README copies are preserved in `docs/archive/readmes_20260812/` with `SHA256SUMS`; they are not current sources of truth.

The archive contains historical job logs, audit narratives, intermediate decisions, and superseded wording. It is provenance material, **not** the current source of truth. New results must be added first to the appropriate active DAR in a short dated checkpoint, with a source path and status (`VALIDATED`, `EXPLORATORY`, `FAILED`, `PENDING`, or `NOT_COMPUTED`).

## Reading order

1. Read `AGENTS.md` for workflow and provenance rules.
2. Read the relevant DAR.
3. Use the roadmap for next actions, not for replacing numerical evidence.
4. Consult the archive only when reconstructing an earlier decision or job.
