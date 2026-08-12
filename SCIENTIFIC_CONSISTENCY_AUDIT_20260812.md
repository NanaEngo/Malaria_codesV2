# Final scientific-consistency audit — active Markdown

**Date:** 12 August 2026
**Scope:** active project Markdown outside `docs/archive/`, generated outputs, dependency trees, and the intentionally ignored P3 V2 work area.
**Purpose:** identify scientific contradictions in cohort definitions, denominators, estimands, validation status, and interpretation; distinguish real contradictions from legitimate protocol-specific results.

## Verdict

**PASS after clarification of two denominator/status boundaries.** No unsupported biological claim was introduced. The audit found one apparent numerical contradiction that was a legitimate subset distinction and one status-risk in a historical P3 audit log. Both are now made explicit.

## Confirmed clarification 1 — P5 external-panel denominators

The values **22,447** and **22,267** refer to different, documented panels:

- **22,447:** broader ChEMBL-derived panel after activity/structure filtering, stored in `Project5_GNN_Transformer_DrugDiscovery/results/p5_public_chembl_malaria.csv` and described by `p5_public_chembl_malaria_provenance.json`.
- **180 compounds:** canonical-SMILES overlap with the P5 panel, recorded in the same provenance artifact.
- **22,267:** molecule-disjoint panel after removing those 180 overlaps, stored in `p5_public_chembl_malaria_disjoint.csv`; this is the panel used for the ECFP4–GIN transfer benchmark.
- **External descriptor sensitivity (P3, not the P5 benchmark):** the broader 22,447-compound panel is the denominator for the 351 TNE failures and 22,096 complete cases. These TNE counts must not be attributed to the P5 ECFP4–GIN evaluation.

The distinction is now stated in `P5_DATA_ANALYSIS_REPORT.md`, `P5_STRATEGIC_PA90.md`, and `CENTRAL_QUESTIONS_PROJECTS.md`.

## Confirmed clarification 2 — P3 historical audit language

`Project3_Quantum_Inspired_RepresentationsV2607/P3_ADVERSARIAL_AUDIT_MITIGATION.md` contained dated mitigation items, including historical acceptance estimates and an old physical-validation tracker. The scientific results themselves were not promoted, but the file could be mistaken for a current source of truth. Its header now explicitly identifies it as a **historical adversarial audit and mitigation log** and defers current claims to the canonical DAR and central-questions document.

The P3 V2 work area and its old roadmap remain outside the canonical scope as specified by project instructions; they were not edited.

## Canonical scientific boundaries rechecked

- P1/P2 docking scores, RRS, PNS, and ACSI are computational prioritisation measures, not IC\(_{50}\)/EC\(_{50}\), target engagement, or experimental resistance measurements.
- Docking-RRS is distinct from MD-RRS; full-panel Set-C MD-RRS remains `NOT_COMPUTED` at the 12 August snapshot.
- The P2 witness chain is not a cohort result.
- P3 QKS is comparable to matched RBF at tested scales; no quantum advantage is claimed.
- P3 H\(_1\)–RRS association is size/confounder-sensitive and is not presented as an independent biological biomarker.
- P4’s v12 scalar benchmark is distinct from the secondary pre-activity Pareto geometry analysis; random search remains the strongest scalar baseline.
- P5 scaffold-split ECFP4–RF remains stronger than the learned arms; GIN–TFP’s improvement over GIN is descriptive unless a corresponding predeclared paired test is reported.
- Zenodo DOI `10.5281/zenodo.19608875` remains reserved with upload pending.

## Checks performed

1. Cross-file search of active Markdown for canonical AUCs, sample sizes, RRS/PNS/ACSI values, MD-RRS status, P4 benchmark values, and P5 external-validation values.
2. Provenance verification of the two P5 external CSV denominators and JSON metadata.
3. Review of P3 historical-audit headers and legacy numerical/status language.
4. `git diff --check` and archive SHA-256 verification.

## Files changed by this audit

- `P5_DATA_ANALYSIS_REPORT.md`
- `P5_STRATEGIC_PA90.md`
- `CENTRAL_QUESTIONS_PROJECTS.md`
- `Project3_Quantum_Inspired_RepresentationsV2607/P3_ADVERSARIAL_AUDIT_MITIGATION.md`
- this report

No manuscript `.tex`, PDF, CSV, or simulation output was modified.
