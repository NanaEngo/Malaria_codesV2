# V2609 forensic audit against `Reviewer_report.md`

## Scope and standard of evidence

This audit reads the revised LaTeX sources and freshly built PDFs for the main manuscript, Supporting Information (SI), and cover letter. It also checks the response letter because it will be submitted with the revision; a response may describe a correction, but it is not proof that the manuscript or underlying data supports it.

For quantitative claims, evidence means a traceable local result artifact, manifest, or rerunnable source—not a Markdown summary or an assertion in the revised prose. The submitted V2608 files were used only as baseline.

## Fresh build verification

A clean rebuild was performed in the dependency order required by the reciprocal `xr` imports:

```text
main -> SI -> main -> cover letter -> response letter
```

All four PDFs were created. The final `.log` files contain no undefined-citation/reference diagnostics or rerun warnings. The main PDF resolves the docking pointer as “Section 16.2.” The response-letter PDF contains ten literal `??` strings only because it quotes the reviewers’ original missing-marker comments; they are not unresolved references.

This verifies compilation and final cross-references. It does not validate the numerical claims.

## Overall verdict

**The revision resolves the original missing-reference/cross-reference defects and improves the framing of generated molecules and high random-split AUCs. It does not implement Reviewer 1’s required homogeneous endpoint-level ChEMBL benchmark. More seriously, the current four-target docking account is contradicted by the local raw data used for the reported 17,011-molecule results, and the response letter contains mutually contradictory statements about endpoint validation. This package should not be submitted as a complete response to the reviews.**

| Status | Reviewer items |
|---|---:|
| Addressed | 9 |
| Partly addressed | 2 |
| Not addressed / unsupported | 4 |

## Reviewer 1

### R1.1a — Meaning of “African” for generated compounds

**Status: Addressed.**

The title uses “African natural-product-inspired antimalarial chemical space” (`Paper3_Quantum_InspiredV2609.tex:64`), while the abstract and Methods explicitly identify a computationally generated candidate library and its African natural-product/synthetic-drug seed provenance (`:90,134`). This addresses the reviewer’s objection without attributing a geographic identity to generated molecules.

### R1.1b — Calculated labels versus experimental bioactivity

**Status: Partly addressed.**

The primary labels are accurately declared as Ersilia eos80ch model outputs (`Paper3_Quantum_InspiredV2609.tex:134,304`), and the manuscript does not present them as direct experimental activity measurements. This is an appropriate correction.

It is not experimental endpoint validation. The 22,447-compound ChEMBL transfer panel remains pooled across assays, and its result artifact points to a Project 5 input path (`results/p3_external_validation_report.json:2`). No P3-local frozen input manifest identifies the assay records, endpoints, units, targets, or de-duplication rule used for those 22,447 rows.

### R1.1c — Unrealistically high random-split AUC

**Status: Addressed.**

The manuscript reports scaffold-grouped performance in the abstract and explains the analogue-series problem in the limitations (`Paper3_Quantum_InspiredV2609.tex:90,308`). It gives the relevant scaffold count and lowers the interpretation of random-split AUCs to interpolation within related scaffolds. This directly answers the reviewer’s concern.

### R1.1d — Heterogeneous ChEMBL assay pooling

**Status: Not addressed.**

The SI correctly acknowledges that the ChEMBL panel pools heterogeneous *P. falciparum* assays under a single IC50 threshold and lacks assay IDs, targets, and protocol-level identity (`Paper3_Quantum_Inspired_SM_V2609.tex:643-645`). Disclosure is not a methodological remedy: the pooled set cannot support the same-endpoint comparisons requested by Reviewer 1.

### R1.1e — Benchmark descriptors against ECFP on comparable same-assay endpoints

**Status: Not addressed.**

No endpoint-specific dataset or results table is present in the V2609 main manuscript or SI. The available P3 ChEMBL novelty artifacts do not fill this gap: `p3_chembl_validation.csv` contains one matched top-10 record and `p3_chembl_expanded.csv` contains seven matched pairs, neither with assay IDs nor descriptor benchmarks. The 22,447-row transfer summary remains a pooled, Project 5-sourced panel.

To satisfy the review, each benchmark row must name one assay ID, one target/context, one measurement type and unit rule, a declared filtering/deduplication procedure, an endpoint-local label or regression target, scaffold-aware evaluation, and uncertainty for ECFP4 versus every proposed representation.

## Reviewer 2 — major issue

### R2.1 — Cautious interpretation of approximately 0.47 docking performance and docking reliability

**Status: Partly addressed.**

The manuscript now calls the quantity R², limits it to docking-score information retention on the derivation panel, states that ECFP4 is stronger for PfATP4 and PfCRT, and rejects inference to biological binding or prospective generalisation (`Paper3_Quantum_InspiredV2609.tex:211,292,304`). This is a substantial improvement.

The supporting evidence is not internally coherent. The current physical-validation regression file contains three targets only—PfDHFR, PfATP4, and PfCRT—and its PfDHFR ECFP4 R² is 0.4508, not the 0.461 printed in the main manuscript. The response letter further asserts four successful redocking tests with RMSD <2 Å (`Response_to_Reviewers_P3_V2609.tex:328-332`), but no corresponding redocking artifact was found in the P3 results tree. That unsupported assertion must be removed or backed by a versioned table and protocol.

## Reviewer 2 — minor issues

### R2m.1 — Two missing references in main-text Section 2.7

**Status: Addressed.**

The final main build has no undefined citation/reference diagnostics.

### R2m.2 — Two missing annotations in main-text Section 3.4

**Status: Addressed.**

The final main build has no undefined-reference diagnostics.

### R2m.3 — One missing annotation in main-text Section 3.6

**Status: Addressed.**

The final main build has no undefined-reference diagnostics.

### R2m.4 — Conclusive source and type of multi-target docking data

**Status: Not addressed / unsupported.**

The prose is more detailed: it names Tartarus, AutoDock Vina, four PDB structures, 19,913 source leads, and 17,011 complete profiles (`Paper3_Quantum_Inspired_SM_V2609.tex:531-543`). But the local raw file underpinning the 17,011-molecule physical-validation results, `results/p3_physical_validation/p3_merged_dataset.csv`, has exactly 17,011 rows and only three score columns: `score_1syh`, `score_6y2f`, and `score_4lde`. It has no `score_2f6i` column. Its regression companion likewise contains only three targets. Therefore the available data do not support the claim that all 17,011 compounds had complete four-target profiles, nor the statement that “PfClpP followed similar patterns” (`Paper3_Quantum_Inspired_SM_V2609.tex:537`).

The current source description is not conclusive until a versioned raw four-target table, with `score_2f6i`, plus a manifest connecting it to the 19,913/17,011 counts is supplied. If no such artifact exists, the prose must revert to the three-target analysis actually evidenced by the raw files.

### R2m.5 — Missing usable SI reference for the docking analysis

**Status: Addressed.**

The SI subsection has a stable label (`Paper3_Quantum_Inspired_SM_V2609.tex:530-531`), and after the required dependency-order build the main text’s `\cref` resolves to “Section 16.2” in the PDF (`Paper3_Quantum_InspiredV2609.tex:276`). Retain the documented build order so this reciprocal external reference remains reproducible.

### R2m.6 — JCAMD citation and reference style

**Status: Not addressed.**

The official current JCAMD submission guidelines specify numbered in-text citations in square brackets and a consecutively numbered reference list. The V2609 main and SI render author-year citations, for example “(World Health Organization, 2024),” and use `natbib` with `unsrtnat` (`Paper3_Quantum_InspiredV2609.tex:36,368-369`; `Paper3_Quantum_Inspired_SM_V2609.tex:34,691-692`).

The response letter incorrectly states that JCAMD requires author-year citations and that `unsrtnat` is the required style (`Response_to_Reviewers_P3_V2609.tex:433-444`). Replace this with the journal’s numbered Springer style and rebuild all four documents. The official source checked for this audit is: https://link.springer.com/journal/10822/submission-guidelines

### R2m.7 — Missing SI annotation in SI Section 2

**Status: Addressed.**

The final SI build has no undefined-reference/citation diagnostics.

### R2m.8 — Two missing SI annotations in SI Section 3

**Status: Addressed.**

The final SI build has no undefined-reference/citation diagnostics.

### R2m.9 — Missing annotation in SI Table S9

**Status: Addressed.**

The final SI build has no undefined-reference/citation diagnostics.

## Additional cross-document integrity blockers

These are not separate reviewer items, but they must be fixed before a credible resubmission.

1. **Response-letter contradiction.** The response correctly says that endpoint-specific ChEMBL validation was not implemented (`Response_to_Reviewers_P3_V2609.tex:216-221`), then later says that the revised manuscript “now includes endpoint-specific ChEMBL validation” (`:267-271`) and that a new endpoint-specific analysis ensures homogeneity (`:481-500`). The latter claims are false on the supplied manuscript/data. The response must consistently state that the pooled transfer analysis is exploratory and does not meet the requested endpoint-specific benchmark.
2. **Unsupported ChEMBL novelty table.** SI Table `tab:chembl_validation_top10` lists ten candidate-level rows (`Paper3_Quantum_Inspired_SM_V2609.tex:437-465`), but the machine-readable `p3_chembl_validation.csv` holds only one record. The project’s own statistical reproducibility audit says the same: one top-10 match and seven expanded pairs. Supply the table-generating input that exactly reproduces all ten rows, or reduce/correct the table and text.
3. **Cross-project provenance.** The 22,447-row transfer-result JSON identifies `/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery/results/p5_public_chembl_malaria.csv` as its source. This must be declared and frozen in P3 if retained; otherwise P3’s data-availability claim cannot independently reproduce the analysis.
4. **Build recipe.** Reciprocal `xr` dependencies require the verified `main -> SI -> main` sequence. Add this exact sequence to the submission build instructions; a one-pass compilation shows temporary unresolved external SI references even though the final dependency build resolves them.

## Pre-resubmission acceptance rule

Do not claim all reviewer comments are addressed until all of the following are true:

1. An endpoint-specific ChEMBL benchmark is present, reproducible, and compared against ECFP under a declared endpoint contract.
2. The docking text, raw table, target count, PDB structures, regression results, and response letter all agree; no unverified PfClpP or redocking claim remains.
3. The response letter consistently describes what was and was not implemented.
4. Citation format is converted to the current JCAMD numbered style.
5. A clean dependency-order build generates all four PDFs with zero final undefined diagnostics.