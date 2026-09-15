# V2609 audit against `Reviewer_report.md`

**Scope.** This audit evaluates only the revised LaTeX manuscript files:

- `manuscript/LaTeX/V2609/Paper3_Quantum_InspiredV2609.tex`
- `manuscript/LaTeX/V2609/Paper3_Quantum_Inspired_SM_V2609.tex`
- `manuscript/LaTeX/V2609/Cover_Letter_P3_V2609.tex`

The submitted V2608 LaTeX files were used only as the baseline. The response letter and all Markdown files were not used as evidence that a reviewer request was implemented.

## Verdict

**Not all reviewer comments are fully addressed in the revised manuscript.**

The revision substantially improves the interpretation of the docking-regression result and explicitly limits claims based on model-derived labels, random splits, docking outputs, and non-disjoint ChEMBL transfer. However, the central request from Reviewer 1—benchmarking against ECFP on homogeneous, assay-specific ChEMBL endpoints—is not implemented. The revised ChEMBL set still pools *P. falciparum* assay records. Reviewer 2's request to identify the source and type of the 17,011-molecule multi-target docking data is also incomplete, and the compiled SI retains one unresolved citation.

| Status | Count |
|---|---:|
| Addressed | 4 |
| Partly addressed | 4 |
| Not addressed / unresolved | 3 |

## Reviewer 1

### R1.1a — Geographic terminology for generated molecules

**Status: Partly addressed.**

The revised methods identify the library as computationally generated from 396 African natural-product and 454 synthetic-drug seeds through CHEESE and STONED-SELFIES (`Paper3_Quantum_InspiredV2609.tex:134`). This is a material clarification that the objects being modelled are generated molecules rather than naturally occurring “African molecules.”

However, the title, abstract, keywords, and cover letter retain formulations such as “African antimalarial chemical space,” “African antimalarial candidates,” and “African natural-product-derived antimalarial candidates” (`Paper3_Quantum_InspiredV2609.tex:64,90,95`; `Cover_Letter_P3_V2609.tex:40,42`). The manuscript does not consistently use the more precise “African natural-product-inspired chemical space” wording that would directly answer the reviewer’s terminology objection.

**Required completion:** revise the title-facing and abstract-facing terminology, or add one concise definition early in the Introduction that makes the geographic qualifier apply to seed provenance and ethnobotanical context, not to the generated molecules themselves.

### R1.1b — Calculated labels versus experimental endpoints

**Status: Partly addressed.**

The manuscript now states that the primary labels come from the Ersilia eos80ch model (`Paper3_Quantum_InspiredV2609.tex:134`) and explicitly limits the associated AUCs to prediction of model outputs rather than biological activity (`Paper3_Quantum_InspiredV2609.tex:304`). It also labels the ChEMBL analysis as a label-source-shift transfer analysis rather than an independent molecule-disjoint validation (`Paper3_Quantum_InspiredV2609.tex:134,264,304`; `Paper3_Quantum_Inspired_SM_V2609.tex:638-642`). These are appropriate limitations.

But the experimental transfer panel is not an assay-specific endpoint benchmark. It is assembled from ChEMBL 34 records for *P. falciparum* assays using only a global IC50 threshold (`Paper3_Quantum_Inspired_SM_V2609.tex:638`). The manuscript does not identify a single assay ID, target, stage, assay format, pKi/pIC50 scale, or within-assay active/inactive cohort.

**Required completion:** perform and report the requested homogeneous endpoint-level benchmarking, or explicitly narrow the paper’s contribution and response so that it does not claim to have addressed that request.

### R1.1c — Implausibly high AUC and potential scaffold memorisation

**Status: Addressed.**

The revision reports random-split and Bemis-Murcko scaffold-grouped AUCs in the abstract (`Paper3_Quantum_InspiredV2609.tex:90`) and gives a detailed limitation: 19,836 molecules map to 632 scaffolds, random folds mix analogue series, and ECFP4 declines from 0.9485 to 0.8224 under grouped cross-validation (`Paper3_Quantum_InspiredV2609.tex:308`). It also states that random-split values should not be interpreted as performance on structurally novel chemotypes (`Paper3_Quantum_InspiredV2609.tex:308`).

This directly addresses the reviewer’s concern that very high random-CV AUC may not represent realistic prospective performance.

### R1.1d — Heterogeneous ChEMBL assay pooling

**Status: Not addressed.**

The revised text acknowledges that the ChEMBL panel is a different label source and that molecule-level disjointness is unestablished, but it still pools “ChEMBL 34 bioactivity records for *Plasmodium falciparum* assays” into one binary IC50-threshold dataset (`Paper3_Quantum_Inspired_SM_V2609.tex:638`). No assay-specific results table or individual homogeneous endpoint analysis exists in the revised main manuscript, SI, or cover letter.

This is the reviewer’s principal methodological objection. A common threshold does not make values from different targets, stages, assay protocols, or laboratories comparable.

### R1.1e — Benchmark across many ChEMBL endpoints and establish whether any descriptor beats ECFP

**Status: Not addressed.**

The requested benchmark requires multiple separate ChEMBL endpoints with measured pKi/pIC50 values from the same assay and a descriptor-versus-ECFP comparison per endpoint. The V2609 files contain one pooled ChEMBL transfer panel (`Paper3_Quantum_InspiredV2609.tex:264`; `Paper3_Quantum_Inspired_SM_V2609.tex:638-676`), not an endpoint-by-endpoint benchmark.

The current honest-negative conclusion—ECFP4 remains strongest for the pooled transfer panel—is scientifically more careful than the original claim, but it cannot establish that the descriptors are unhelpful across the endpoint space the reviewer specified.

## Reviewer 2

### R2.1 — Interpret the approximately 0.47 docking association cautiously and discuss docking reliability

**Status: Addressed.**

The reported statistic is now explicitly an R² from a regression against docking scores, not an unspecified Pearson correlation. The manuscript states that TNE is competitive only for PfDHFR (R² = 0.473 versus 0.461 for ECFP4), is weaker for PfATP4 and PfCRT, and does not establish prospective generalisation or biological binding prediction (`Paper3_Quantum_InspiredV2609.tex:211,292`). The SI likewise identifies the target structures, QuickVina source, comparator, and target-specific results (`Paper3_Quantum_Inspired_SM_V2609.tex:532-534`) and describes the analysis as information retention rather than generalisation (`Paper3_Quantum_Inspired_SM_V2609.tex:534,629`).

The paper also makes clear that activity labels are computational and that experimental validation remains necessary (`Paper3_Quantum_InspiredV2609.tex:304,322`). This is a materially more cautious formulation.

### R2m.1 — Two missing references in main-text Section 2.7

**Status: Partly addressed.**

After a fresh local LaTeX build, the revised main-manuscript PDF contains no rendered `??`, “Citation undefined,” or “Reference undefined” markers. However, the SI still has one unresolved citation (`temgoua2027md`), so the claimed blanket resolution of all reference defects is not achieved at package level. See “Compilation audit” below.

### R2m.2 — Two missing annotations in main-text Section 3.4

**Status: Addressed.**

The rebuilt main PDF contains no unresolved rendered cross-reference markers. This is the relevant observable requirement for the reported missing annotations.

### R2m.3 — One missing annotation in main-text Section 3.6

**Status: Addressed.**

The rebuilt main PDF contains no unresolved rendered cross-reference markers.

### R2m.4 — Clarify the source and type of “multi-target docking data”

**Status: Not addressed.**

The main text says only that 17,011 molecules have “multi-target docking data” and defines a threshold of at least two targets at ΔG ≤ −7.0 kcal mol⁻¹ (`Paper3_Quantum_InspiredV2609.tex:273-276`). It does **not** identify the targets, docking engine, receptor structures, grid configurations, provenance, or whether this is the same dataset discussed in the SI.

The SI provides separate details for a Tartarus/QuickVina dataset: 19,913 leads and three targets (1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT) (`Paper3_Quantum_Inspired_SM_V2609.tex:532-534`). This does not unambiguously describe the 17,011-molecule multi-target dataset in the main text, and the sample size and target count differ.

**Required completion:** add a main-text sentence specifying dataset provenance, docking program/version, four (or actual) targets and structures, grid/source, and the selection/threshold rule; point to the exact SI section/table containing complete parameters.

### R2m.5 — Missing supplementary-material reference in main-text Section 3.7

**Status: Partly addressed.**

The main PDF has no rendered unresolved cross-reference marker, but the referenced SI material is not unambiguously tied to the 17,011-molecule dataset. The technical marker is gone; the substantive navigational request remains incomplete for the reason documented under R2m.4.

### R2m.6 — Citation format and JCAMD style

**Status: Partly addressed.**

The revision uses a consistent `natbib` author–year citation mechanism and `unsrtnat` bibliography style (`Paper3_Quantum_InspiredV2609.tex:36,368-369`; `Paper3_Quantum_Inspired_SM_V2609.tex:34,684-685`). However, the local BibTeX build reports incomplete bibliography records: `Nigam2021`, `temgoua2026tb`, and `saognn2026` have missing year and/or journal fields. An incomplete record cannot be considered fully formatted for submission.

This audit did not independently certify current JCAMD house style because the publisher-guideline lookup was unavailable. The actionable, locally verified finding is that bibliography metadata must be completed before any style claim is accepted.

### R2m.7 — One missing SI annotation in SI Section 2

**Status: Addressed.**

After rebuilding the SI after the main manuscript aux file was available, the imported main-text references resolved. The remaining SI error is an unrelated unresolved citation, not an annotation marker.

### R2m.8 — Two missing SI annotations in SI Section 3

**Status: Addressed.**

The rebuilt SI has no rendered `??` or unresolved reference markers. The caveat about the separate unresolved citation still applies.

### R2m.9 — One missing annotation in SI Table S9

**Status: Partly addressed.**

No rendered `??` remains in the rebuilt SI. Nevertheless, a final SI build still reports one undefined citation, so this document is not technically clean enough to certify all of Reviewer 2’s technical corrections as completed.

## Compilation audit

A fresh local build was run with `latexmk -pdf -interaction=nonstopmode -halt-on-error` in `manuscript/LaTeX/V2609`, compiling the SI, main manuscript, then the SI again (to import the main `.aux` labels), and the cover letter.

| Artifact | Result | Verified issue |
|---|---|---|
| Main manuscript | PDF built, 15 pages | No rendered unresolved `??`/undefined citation/reference marker. Bibliography warnings remain for three incomplete records. |
| Supporting Information | PDF built, 15 pages | `temgoua2027md` remains undefined in the final log and rendered bibliography/citation output. |
| Cover letter | PDF built, 1 page | No unresolved-marker issue. It repeats the pooled ChEMBL-transfer framing (`Cover_Letter_P3_V2609.tex:42,62`), so it should be revised if the manuscript is corrected to endpoint-specific analysis. |

## Priority actions before resubmission

1. **Implement the central Reviewer 1 request:** create an assay-specific ChEMBL benchmark table and analysis. Each endpoint should retain target, assay ID/type, unit/transformation, activity threshold, molecule count, split protocol, and ECFP4/TFP/TNE/QKS results.
2. **Replace or consistently limit the pooled ChEMBL analysis.** It may remain explicitly exploratory, but it cannot be presented as the requested experimental endpoint validation.
3. **Repair the multi-target docking description.** Make the main-text 17,011-molecule dataset traceable and reconcile it with the distinct 19,913-lead/three-target Tartarus analysis in the SI.
4. **Fix compilation and bibliography defects:** add the missing `temgoua2027md` BibTeX entry and complete required `year`/`journal` fields for `Nigam2021`, `temgoua2026tb`, and `saognn2026`; then rebuild main and SI until the logs have no undefined citation/reference warnings.
5. **Tighten the geographic framing** so “African” clearly refers to provenance of seed natural products and study context, not an intrinsic property of generated compounds.
