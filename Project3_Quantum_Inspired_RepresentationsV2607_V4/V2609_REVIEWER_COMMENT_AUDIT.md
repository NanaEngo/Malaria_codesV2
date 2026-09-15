# V2609 audit against `Reviewer_report.md`

## Scope and evidence

This is a source-and-build audit of the revised LaTeX submission package only:

- `manuscript/LaTeX/V2609/Paper3_Quantum_InspiredV2609.tex`
- `manuscript/LaTeX/V2609/Paper3_Quantum_Inspired_SM_V2609.tex`
- `manuscript/LaTeX/V2609/Cover_Letter_P3_V2609.tex`

The submitted V2608 files were consulted only as baseline. The response letter, prior Markdown audits, and the new propositions document are not treated as evidence that a reviewer request is implemented in the manuscript.

I also checked the project-level provenance material relevant to the revised docking claims: `P3_DATA_ANALYSIS_REPORT.md` and `results/p3_tartarus_summary.txt`. This matters because a complete-looking prose revision is not adequate if its numerical source cannot be reconciled with the archived result artifacts.

## Build verification

A fresh local build completed with strict exits for the main manuscript, SI, and cover letter using:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error <file>.tex
```

All three PDFs were produced. Their `.log` files contain zero matches for undefined-citation/reference diagnostics. This verifies the absence of the reported unresolved LaTeX markers; it does not validate the scientific analyses or JCAMD copy-editing requirements.

## Overall verdict

**The revision resolves the technical LaTeX defects and substantially improves the scientific caution, but it does not yet address Reviewer 1's central endpoint-specific ChEMBL benchmarking request. In addition, the newly expanded docking description has an unresolved provenance and navigation defect. Therefore, the submission is not yet a complete response to all reviewer comments.**

| Status | Reviewer items |
|---|---|
| Addressed | 8 |
| Partly addressed | 4 |
| Not addressed / unresolved | 3 |

## Reviewer 1

### R1.1 — Meaning of “African” for a computationally generated library

**Status: Addressed, with an advisable final tightening.**

The revised title now says “African natural-product-inspired antimalarial chemical space,” and the abstract says the candidates are computationally generated and inspired by African natural-product antimalarials (`Paper3_Quantum_InspiredV2609.tex:64,90`). Methods specifies the actual construction: 65,856 molecules generated from 396 African natural-product and 454 synthetic-drug seeds using CHEESE and STONED-SELFIES (`Paper3_Quantum_InspiredV2609.tex:134`). This makes the provenance of the seed set distinct from the identity of a molecule.

The phrase “African natural products” remains appropriate when it describes the natural-product seed/provenance context (`Paper3_Quantum_InspiredV2609.tex:118`). To eliminate residual ambiguity, use the same `African natural-product-inspired` construction in every title-facing, abstract-facing, and cover-letter reference; do not describe generated candidates themselves as inherently “African.”

### R1.2 — Computed labels are not experimental bioactivity

**Status: Partly addressed.**

The manuscript now explicitly identifies the primary labels as eos80ch model outputs (`Paper3_Quantum_InspiredV2609.tex:134`), states in the highlights that all activity labels are computational predictions (`Paper3_Quantum_InspiredV2609.tex:105`), and limits the AUC claims to model-output prediction rather than experimental biological activity (`Paper3_Quantum_InspiredV2609.tex:304`). These are appropriate corrections.

However, this limitation cannot substitute for the requested experimental endpoint benchmark. The current ChEMBL analysis remains a pooled-label transfer exercise, rather than validation against a homogeneous measured endpoint.

### R1.3 — Implausibly high AUC and analogue/scaffold memorisation

**Status: Addressed.**

The revised manuscript reports both random and Bemis--Murcko scaffold-grouped cross-validation in the abstract (`Paper3_Quantum_InspiredV2609.tex:90`) and explains why random splitting mixes analogue series. It gives the scaffold count (632), reports the ECFP4 decline from 0.9485 to 0.8224, and states that random-split values should not be read as performance on unseen chemotypes (`Paper3_Quantum_InspiredV2609.tex:308`).

This directly addresses the reviewer’s concern that near-perfect random-CV discrimination does not represent realistic experimental prediction.

### R1.4 — Pooling heterogeneous ChEMBL assays

**Status: Not addressed.**

The revised SI explicitly admits that the ChEMBL panel pools heterogeneous *P. falciparum* assays under one IC50 threshold and does not identify assay IDs, targets, or protocols (`Paper3_Quantum_Inspired_SM_V2609.tex:638-644`). The main manuscript repeats this limitation (`Paper3_Quantum_InspiredV2609.tex:304`). Honest disclosure is an improvement, but it does not remedy the methodological defect identified by the reviewer.

A global IC50 cutoff cannot make measurements from different targets, parasite stages, laboratories, or assay formats a homogeneous endpoint.

### R1.5 — Benchmark descriptors against ECFP on many same-assay ChEMBL endpoints

**Status: Not addressed.**

The reviewer asked for endpoint-by-endpoint benchmarks based on comparable reported pKi/pIC50 values from the same assay, including cases where a proposed descriptor may or may not outperform ECFP. V2609 contains one pooled panel of 22,447 compounds (`Paper3_Quantum_InspiredV2609.tex:262-269`; `Paper3_Quantum_Inspired_SM_V2609.tex:638-682`), not separate assay-defined endpoint analyses.

**Completion requirement:** retrieve endpoint-level ChEMBL records; retain assay ID, target, endpoint type, units, transformation, and deduplication rule; use an endpoint-local activity definition or regression target; apply leakage-safe scaffold-aware validation; and report ECFP4, TFP, TNE, QKS, and fusion results per eligible endpoint with uncertainty. Until that analysis is run and verified, the pooled transfer results must remain explicitly exploratory and cannot be presented as satisfying this request.

## Reviewer 2 — major issue

### R2.1 — Interpret the approximately 0.47 docking result cautiously and address docking reliability

**Status: Partly addressed.**

The revised text correctly calls the quantity an R² from regression, not a correlation coefficient, and confines the result to docking-score information retention on the same molecular set (`Paper3_Quantum_InspiredV2609.tex:211,292`). It states that TNE is only competitive for PfDHFR and is inferior to ECFP4 for PfATP4 and PfCRT. It also rejects any inference to experimental binding or prospective generalisation (`Paper3_Quantum_InspiredV2609.tex:211,292,304`). These changes directly improve the interpretation requested by Reviewer 2.

The remaining limitation is provenance: the SI claims a four-target, 19,913-lead Tartarus source cohort and a 17,011-molecule complete-profile subset (`Paper3_Quantum_Inspired_SM_V2609.tex:532-540`), whereas the project’s archived `results/p3_tartarus_summary.txt` documents three regression targets and a 19,900-molecule polypharmacology cohort. The report does not independently verify the 19,913/17,011/four-target numbers. This discrepancy must be reconciled against raw docking tables, run manifests, or a versioned source script before the expanded docking narrative can be considered conclusive.

## Reviewer 2 — minor issues

### R2m.1 — Two missing references in main-text Section 2.7

**Status: Addressed.**

The fresh main-document build has no undefined-citation or undefined-reference diagnostics.

### R2m.2 — Two missing annotations in main-text Section 3.4

**Status: Addressed.**

The fresh main-document build has no undefined-reference diagnostics.

### R2m.3 — One missing annotation in main-text Section 3.6

**Status: Addressed.**

The fresh main-document build has no undefined-reference diagnostics.

### R2m.4 — Clarify source and type of the multi-target docking data

**Status: Partly addressed.**

The main text now names AutoDock Vina, four proteins and PDB structures, the 17,011-molecule complete-profile cohort, the binding rule, and target-specific grids (`Paper3_Quantum_InspiredV2609.tex:276`). The SI adds a stated source cohort, a distinction from companion-study MD structures, and three target-specific TNE-versus-ECFP4 regression results (`Paper3_Quantum_Inspired_SM_V2609.tex:532-540`). This is materially better than the submitted version.

Two requirements remain:

1. The central provenance conflict described under R2.1 must be resolved from the raw artifacts; otherwise the dataset description is not conclusive.
2. “Target-specific grid configurations” and “validation” are asserted but not supplied as a parameter/validation table in the SI. Include receptor preparation, grid centre/size/spacing, docking engine/version, exhaustiveness/poses, score-selection rule, and validation evidence, or cite an accessible frozen source containing those details.

### R2m.5 — Missing usable supplementary-material reference for the docking analysis

**Status: Not addressed / unresolved.**

The source no longer has a rendered `??`, but the replacement locator is wrong: the main text directs the reader to “SI Section 2.3” (`Paper3_Quantum_InspiredV2609.tex:276`), while the relevant SI material begins under “Applicability domain and comparison with existing tools” at `Paper3_Quantum_Inspired_SM_V2609.tex:524` and has no Section 2.3.

**Completion requirement:** assign the SI docking subsection and any new docking-parameter table stable labels, then replace the prose locator with `\cref{...}` references. Verify the compiled PDF resolves the labels after the main/SI cross-reference build order.

### R2m.6 — JCAMD reference format and citation style

**Status: Partly addressed.**

The revision consistently uses `natbib` citations and `unsrtnat` bibliographies in main and SI (`Paper3_Quantum_InspiredV2609.tex:368-369`; `Paper3_Quantum_Inspired_SM_V2609.tex:690-691`). The fresh build shows no undefined-reference/citation diagnostics.

This audit verifies local consistency and compilation only. It does not certify final compliance with the journal’s current reference-style instructions; that requires applying the official JCAMD template or editorial guidance at submission preparation.

### R2m.7 — Missing SI annotation in SI Section 2

**Status: Addressed.**

The fresh SI build has no undefined-reference or undefined-citation diagnostics.

### R2m.8 — Two missing SI annotations in SI Section 3

**Status: Addressed.**

The fresh SI build has no undefined-reference or undefined-citation diagnostics.

### R2m.9 — Missing annotation in SI Table S9

**Status: Addressed.**

The fresh SI build has no undefined-reference or undefined-citation diagnostics.

## Pre-resubmission actions, in required order

1. **Reconcile docking provenance before retaining the 19,913/17,011/four-target narrative.** Locate and audit the raw tables/manifests that yield those values; otherwise revert the prose to the results actually substantiated by the archived artifact and label any additional analysis as pending.
2. **Repair the SI locator and add conclusive docking protocol evidence.** Use labelled `\cref` links and a parameter/validation table or a frozen cited source.
3. **Implement an endpoint-specific ChEMBL benchmark.** This is the substantive response to Reviewer 1 and cannot be satisfied by caveats around the pooled panel.
4. **After verified endpoint results exist, revise only the claims, tables, SI, cover letter, and point-by-point response that depend on them.** Preserve the author’s remaining prose and keep reviewer-facing narration out of the manuscript.
5. **Perform journal-template and bibliography checks at final submission preparation.**

## Acceptance rule

Do not mark all reviewer comments addressed until (a) endpoint-specific ChEMBL benchmarks are present and reproducible, (b) the docking cohort and protocol are traceable to consistent source artifacts, and (c) the main-to-SI docking reference resolves to a real labelled location.