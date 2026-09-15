# Propositions to address the JCAMD reviewer comments

## Purpose and evidence boundary

This document proposes revision routes; it does **not** claim that a new endpoint-level analysis has been performed.

The propositions are based on:

- `Reviewer_report.md`
- current V2609 main manuscript, SI, and cover letter
- `V2609_REVIEWER_COMMENT_AUDIT.md`
- P3 canonical analysis record, `P3_DATA_ANALYSIS_REPORT.md`
- existing P3 result artifacts and Zenodo package inventory

No manuscript, data, code, or response letter is modified by this document.

## Current state that constrains every route

1. The primary P3 result is a computational-label benchmark, not an experimental activity benchmark. The canonical conclusion is therefore correctly bounded: non-classical representations did not improve performance beyond ECFP4 under the protocols tested (`P3_DATA_ANALYSIS_REPORT.md:35-52`).
2. The current ChEMBL panel contains 22,447 rows, but it pools *P. falciparum* assay records under a single IC50 threshold. It cannot answer Reviewer 1's request for comparable, single-assay pKi/pIC50 endpoints (`results/p3_external_validation_report.json:2-21`; `Paper3_Quantum_InspiredV2609.tex:304`).
3. There is a provenance conflict requiring resolution before manuscript promotion: the canonical P3 DAR reports Tartarus regression for three targets and polypharmacology classification with n=19,900 (`P3_DATA_ANALYSIS_REPORT.md:94-101`; `results/p3_tartarus_summary.txt:7-20`), while V2609 reports a four-target AutoDock Vina cohort with 17,011 complete profiles (`Paper3_Quantum_InspiredV2609.tex:276`; `Paper3_Quantum_Inspired_SM_V2609.tex:532-540`). The source manifest must determine which statement is valid. Do not settle this by editing prose alone.
4. The corrected package compiles without undefined reference/citation warnings. This solves the reviewer’s visible `??` issues, but it does not validate scientific claims or internal dataset provenance.

## Decision proposition A — scientific response to Reviewer 1

### A1 — Recommended: registered, endpoint-specific ChEMBL benchmark

Create a new, versioned experimental benchmark rather than modifying the pooled ChEMBL transfer panel.

**Protocol contract**

- Unit of analysis: one distinct compound–assay endpoint record after a predeclared duplicate-resolution rule.
- Endpoint definition: one `assay_id`, one biological target/assay context, one measurement family (pIC50 or pKi), one unit/conversion rule, and one activity-label threshold per endpoint.
- Inclusion: only endpoints with prespecified minimum usable sample size and both classes after de-duplication. The exact thresholds must be set before retrieval; `n >= 500` and a minimum of 100 compounds per class are reasonable feasibility screens, not results.
- Exclusion: mixed targets, mixed assay types, non-comparable units, ambiguous relations, compounds without auditable structures, and duplicate measurements handled outside the declared aggregation rule.
- Comparators: ECFP4 must be primary. TFP, TNE, QKS, and any hybrid use the same compound cohort, split objects, preprocessing scope, and hyperparameter-selection rule wherever technically possible.
- Splits: repeated scaffold-grouped cross-validation is primary; random stratified cross-validation may be secondary and must not be called prospective generalisation.
- Outcomes: ROC-AUC with confidence interval or repeat distribution; PR-AUC when class balance is unequal; per-endpoint delta versus ECFP4; endpoint-wise statistical comparison; multiplicity adjustment across endpoints; explicit failure count for TNE/QKS.
- Reporting: one results table per endpoint with assay ID, target, assay type, unit/transformation, n, active/inactive counts, scaffold count, all descriptor results, uncertainty, and multiplicity-adjusted comparison.
- Status: the analysis is exploratory unless a protocol is frozen before execution. It must never overwrite P3 canonical outputs; use a new result root such as `results/p3_chembl_endpoint_benchmark_v1/` with input hashes, source-release date, environment, command lines, and output hashes.

**What it answers.** This is the only route that directly addresses the reviewer’s objections to pooled endpoints, calculated labels, and the descriptor-versus-ECFP test criterion.

**Likely scientific outcomes and acceptable interpretations.**

- If no non-classical descriptor exceeds ECFP4 after multiplicity control: strengthen the bounded honest-negative claim to the declared endpoint collection.
- If a non-classical descriptor is better on one or more endpoint(s): report those endpoints as endpoint-specific findings, retain the overall non-universality conclusion, and test whether the advantage survives scaffold grouping.
- If endpoint construction yields too few usable assays: report that fact, preserve the existing paper’s scope, and do not substitute pooled data as a proxy.

**Why recommended.** It gives the reviewer the design they asked for and converts the paper from a single easy-to-predict, generated-label benchmark into an evidence-bounded comparison across experimental endpoint contexts. It is more work than a wording change, but it is scientifically responsive.

### A2 — Constrained alternative: narrow the manuscript and be fully explicit

Do not add a new experiment. Retain only the primary computational-label analysis, framed as a representation/diagnostic study on a computationally generated natural-product-inspired library. Move the pooled ChEMBL results to a clearly labelled exploratory supplement or remove them.

**Required manuscript changes**

- State that the study does not benchmark homogeneous experimental endpoints.
- Remove any sentence implying that pooled ChEMBL transfer fulfills experimental endpoint validation.
- Do not claim that the reviewer’s requested endpoint benchmark was completed in the response letter.
- Retitle and restructure the contribution around topology, compression, kernel comparison, scaffold leakage, and bounded diagnostics.

**What it answers.** It resolves overclaiming but does not satisfy the reviewer’s central request. Use only if A1 is not feasible before the revision deadline.

### A3 — Staged route: data audit first, then decide whether A1 is feasible

Run a read-only ChEMBL-source audit before selecting a final route. The audit produces counts—not manuscript claims—for candidate assay IDs after applying the A1 contract. It reports target, assay format, standard type/unit, relation, number of unique structures, class balance under predeclared thresholds, and scaffold count.

**Decision rule**

- Proceed to A1 only if the audit identifies a prespecified minimum number of viable endpoints.
- Otherwise select A2 and state the limitation plainly.

**Why this route may be practical.** The current P3 directory has no endpoint-specific dataset or active analysis scripts, but `zenodo_package_P3/scripts/` contains reusable descriptor pipeline scripts and the canonical P3 scripts are recoverable from git history (`P3_DATA_ANALYSIS_REPORT.md:183-214`). The audit prevents an unsupported promise of a large endpoint study.

## Decision proposition B — terminology and study framing

### B1 — Recommended: precise provenance wording, retain the regional context

Keep the scientifically relevant regional/ethnobotanical context while making generated-molecule status explicit at every high-visibility location.

- Preferred title pattern: `Do topological and quantum-inspired molecular representations add value? Evidence from an African-natural-product-inspired antimalarial library`.
- First Introduction definition: “Here, ‘African-natural-product-inspired’ refers to the provenance of seed scaffolds and ethnobotanical context; the analysed library molecules were computationally generated and are not asserted to be naturally occurring or geographically intrinsic.”
- Replace “African antimalarial candidates” with “computationally generated candidates inspired by African natural-product antimalarial seed scaffolds.”
- Make the same replacement in abstract, keywords, cover letter, graphical-abstract caption, and response letter.

**What it answers.** It corrects the reviewer’s valid semantic objection without erasing the actual provenance of the seed collection.

### B2 — Stronger neutralisation

Remove “African” from the title and headline language altogether; retain it only in Methods as a source-dataset descriptor.

**Trade-off.** This is least vulnerable to the reviewer’s criticism but weakens the manuscript’s connection to African natural-product provenance.

## Decision proposition C — docking and TNE claim repair

### C1 — Recommended: provenance reconciliation gate before prose revision

Create a versioned reconciliation table from the actual source artifacts, with one row per dataset statement:

| Claim field | Required verification |
|---|---|
| Dataset identity | source archive, version/hash, and source-release metadata |
| Docking engine | source-defined engine, not a substituted name |
| Targets and structures | exact count, PDB ID, target identity |
| Cohort size | raw row count and complete-case count |
| Task | regression target or docking-defined classification target |
| Metric | R², Spearman rho, AUC, and corresponding n |
| Manuscript/SI locations | every source location to update |

Only after this table agrees with a versioned source should the manuscript say whether the Tartarus analysis has three targets/n=19,900 or four targets/n=17,011. The present DAR and V2609 text disagree, so one cannot be promoted on the strength of the other.

**Required final prose boundary.** The result is descriptor information retention against computational docking scores, not validation against binding affinity or biological activity. Report R² and Spearman rho as distinct quantities, preserve target dependence, and avoid calling R²≈0.47 a strong predictive model.

### C2 — Minimal alternative

If the provenance audit cannot be finished quickly, remove the detailed four-target claims and retain only a conservative, source-traceable statement supported by the canonical DAR. This reduces scope but avoids a manuscript-level contradiction.

## Decision proposition D — supplementary navigation and technical completion

### D1 — Recommended: labelled SI citation instead of a manual section number

1. Add a stable SI label to the actual docking-provenance subsection, for example `\label{sec:si_tartarus_docking_provenance}`.
2. Replace “see SI Section 2.3” in the main manuscript with `see Supporting Information, \cref{X-sec:si_tartarus_docking_provenance}`.
3. Add a single table containing the actual docking program, version, receptor/PDB, grid center/size, scoring threshold, source archive, raw n, and complete-profile n.
4. Compile main then SI (or use `latexmk` with external-document aux handling) and test the rendered target reference.

**What it answers.** It closes both Reviewer 2’s request for source/type information and the missing-SI-reference issue in a reader-usable way.

### D2 — Citation/style gate

Before resubmission, run a document-level gate that requires:

- no undefined citations/references;
- no rendered `??` marker in main, SI, cover letter, and response letter;
- no BibTeX warning;
- completion of all mandatory fields in cited records;
- manual confirmation against the current JCAMD author instructions;
- a clean and an annotated manuscript PDF, with annotated changes generated against the submitted V2608 baseline.

The current compilation pass proves marker resolution. It does not by itself prove that the reference style matches JCAMD’s current requirements.

## Decision proposition E — response-letter integrity

The response letter is not evidence that the manuscript is fixed. It must be revised after the scientific route is selected.

- Under A1: describe the exact endpoint protocol, data source, results, and locations only after the outputs have been rerun and independently checked.
- Under A2/A3: say directly that the pooled analysis is exploratory and that endpoint-specific benchmarking was not performed in this revision; do not claim otherwise.
- Never place reviewer-facing language in the article itself. For example, the phrase that an analysis “does not address the methodological requirement for homogeneous endpoint-level analysis” belongs in the response letter, not the published manuscript. In the manuscript, use plain scientific language: “The pooled panel does not support endpoint-specific inference.”

## Recommended combined choice

**Recommendation: A3 → A1 + B1 + C1 + D1 + D2 + E.**

1. Audit whether enough homogeneous ChEMBL endpoints exist under a frozen endpoint contract.
2. If viable, execute the endpoint-specific benchmark as a new versioned analysis; otherwise adopt A2 rather than overstate pooled results.
3. Reconcile Tartarus provenance before finalising docking claims.
4. Apply precise provenance terminology and a labelled SI cross-reference.
5. Rebuild clean and annotated manuscript packages, then write the response letter from verified outputs.

This route addresses every reviewer concern without fabricating an experimental validation result, overwriting canonical P3 results, or rewriting unrelated author prose.

## Acceptance criteria for a future final verification

- Every reported experimental benchmark row maps to one declared assay ID and a reproducible input manifest.
- Endpoint labels, transformations, split objects, and hyperparameter selection are frozen before execution.
- ECFP4 and every comparator use the same endpoint cohort and applicable split definition.
- Multiple-endpoint inference is corrected and effect sizes/uncertainty are reported.
- The Tartarus/docking cohort is consistent across canonical DAR, source artifact, main manuscript, SI, and response letter.
- All “African” terminology declares seed provenance and generated-library status at first use.
- The SI docking pointer resolves to the intended reader-visible section/table.
- Clean and annotated PDFs compile without unresolved marker or bibliography warning.
- The response letter makes no claim beyond the visible, versioned manuscript and results artifacts.
