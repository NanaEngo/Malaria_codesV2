# P2 — Final author review and adversarial audit

**Date:** 30 August 2026  
**Target:** *Journal of Chemical Information and Modeling* (JCIM, ACS)  
**Canonical manuscript:** `manuscript/LaTeX/Polypharmacology_MD_Validation_V2609.tex`  
**Canonical SI:** `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2609.tex`  
**Environment:** `malaria_md`  
**Protocol:** `docs/P2_JCIM_AUTHOR_REVIEW_PROTOCOL.md`

## Executive summary

The DAR, canonical source data, manuscript, SI and M1 provenance were cross-checked. The manuscript is scientifically framed as a calibration and computational-triage study, not as biological validation of polypharmacology or resistance. No unsupported affinity, residence-time, target-engagement or resistance claim was found in the canonical V2609 main text or SI.

The audit identified and corrected several DAR inconsistencies, chiefly stale M1 status entries and an unrounded MD-RRS value. The canonical source value for PP-01 PfCRT K76T is 102.7468, reported as 102.7 in the manuscript and DAR. M1 is a single independent structural-stress trajectory of PP-01 PfDHFR WT reaching 25.17 ns with QC PASS; it is reported in the SI as an archival appendix outside the Set-C estimand and is not presented as a multi-replicate campaign.

**Decision:** `READY_FOR_AUTHOR_APPROVAL`  
`READY_FOR_SUBMISSION` is not assigned because Paragon Plus metadata, ORCID confirmation for all authors and the pending data archive require human completion.

## Files audited

- `P2_DATA_ANALYSIS_REPORT.md`
- `manuscript/LaTeX/Polypharmacology_MD_Validation_V2609.tex`
- `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2609.tex`
- `manuscript/LaTeX/Cover_Letter_V2609.tex`
- `manuscript/LaTeX/SUBMISSION_MANIFEST_V2609.md`
- `results/c_rrs_classification.csv`
- `results/set_c_md/md_rrs_discriminative_pilot.csv`
- `results/set_c_md/md_vs_docking_comparison_pilot.csv`
- `results/set_c_md/mmgbsa_summary_pilot.csv`
- `results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1/m1_provenance.json`
- `docs/P2_JCIM_AUTHOR_REVIEW_PROTOCOL.md`

## DAR ↔ source-data audit

| Item | Result | Evidence / resolution |
|---|---|---|
| Set-C cohort and 136 docking systems | PASS | DAR §2 and `c_rrs_classification.csv` |
| Complete two-target cohort, n=12 | PASS | DAR §2–§3; main and SI agree |
| PfCRT-only sensitivity cohort, n=5 | PASS | DAR §2; unequal coverage explicitly bounded |
| Class counts A*/A/B/C/D | PASS | 1/1/4/5/1 on n=12; 5/1/5/5/1 on available-target analysis |
| PNS–RRS correlation | PASS | rho = -0.2098, permutation p = 0.5144, adjusted p = 1.0000 |
| Coverage-sensitive PNS–RRS | PASS | rho = -0.5588, adjusted p = 0.0667; explicitly exploratory |
| DEKOIS | PASS | AUC = 0.450, CI 0.37–0.53; treated as absence of enrichment |
| MD-RRS range | CORRECTED | 72.2–102.7; exact PP-01 PfCRT K76T source = 102.7468 |
| MD/docking direction comparison | PASS | 7/8 divergent; one concordant row, PP-01 PfCRT K76T |
| Set-C MM-GBSA | PASS | 16 rows, 12 mutant + 4 WT; 8/12 mutant ratios >100, 4/12 <100 |
| Parent-study MM-GBSA | PASS | Only PfCRT–214 reportable: -18.25 ± 0.40 kcal/mol |
| PP-15 probe | PASS | Both WT systems completed; no mutant/RRS claim |
| M1 | PASS after reconciliation | 25.17 ns, bound fraction 1.000, mean minimum distance 2.753 Å, QC PASS, USER_DECISION |

## Corrections applied to the DAR

1. Corrected PP-01 PfCRT K76T MD-RRS from 102.8 to 102.7 in the current numerical summary and historical audit note.
2. Reconciled M1 status entries that still described job 15715 as running to 100 ns. The current status now records job 15715 stopped by watcher 15716 at 25.16 ns and QC PASS.
3. Marked older M1 execution descriptions as `SUPERSEDED` rather than deleting the historical records.
4. Updated the current manuscript status to `AUTHOR REVIEW COMPLETE`.
5. Updated the current release page count to main 32 pages / SI 20 pages / cover 1 page.
6. Marked the V2609 title decision as applied.
7. Clarified the difference between the historical lightweight bootstrap and the canonical RRS/polypharmacology bootstrap.
8. Removed the stale inventory description “335+ lines”.

The DAR remains the authoritative record; dated historical checkpoints were preserved and explicitly labelled superseded.

## Claims ↔ evidence audit

| Claim class | Assessment | Residual risk |
|---|---|---|
| RRS is a relative docking-score-retention statistic | PASS | It is protocol-dependent and not biochemical |
| PNS is a network-weighted ranking heuristic | PASS | Centrality depends on network construction and imputation |
| ACSI is a chemical-space descriptor | PASS | Reference-space dependence |
| MD-RRS measures local geometric retention | PASS | Does not estimate affinity or residence time |
| MM-GBSA is an endpoint diagnostic | PASS | Single-trajectory, single-replicate uncertainty remains |
| PP-01 passes the pilot-scope gate | PASS | Gate is exploratory and conditional on target coverage |
| PP-02 is not promoted by the gate | PASS | No biological negative conclusion is drawn |
| External RRS is near 100 | PASS | External panel is docking-derived, not experimental |
| M1 extends the PP-01 WT structural observation | PASS | One system and one independent trajectory only |
| Biological polypharmacology or resistance circumvention | NOT CLAIMED | Experimental validation remains absent |

## Adversarial review

### Computational methodology

**Concern:** grid and ligand preparation can change docking reproducibility.  
**Mitigation:** PP-01 and PP-15 multi-seed controls; the canonical ligand preparation and grid provenance are explicitly preserved. The historical PP-15-grid/Meeko run is excluded.

**Concern:** mutant homology models are not experimental structures.  
**Mitigation:** QMEAN, GMQE, Ramachandran and RMSD criteria are reported; the manuscript states that model quality is not experimental accuracy.

### Molecular dynamics

**Concern:** 10 ns and one replicate do not establish residence time or convergence.  
**Mitigation:** this is stated in Methods, Results and Limitations; M1 is labelled a single structural-stress trajectory and not a replicate campaign.

**Concern:** MM-GBSA values can be affected by PBC and numerical instability.  
**Mitigation:** PBC-whole reconstruction, numerical QC, exclusion of dissociated and conversion-invalid systems, explicit reporting of the K76A replicate difference and distinction of SEM from SDprop.

### Biology

**Concern:** docking does not demonstrate polypharmacology or resistance resilience.  
**Mitigation:** the abstract, Discussion and Conclusion explicitly restrict the contribution to computational prioritisation and calibration; experimental assays are stated as necessary.

### Statistics

**Concern:** n=12 gives low power and wide intervals.  
**Mitigation:** correlations are labelled descriptive; permutation p-values, Bonferroni adjustment and bootstrap intervals are reported; unequal coverage and post-selection are disclosed.

### Editorial assessment

The study has a coherent JCIM contribution if evaluated as a negative calibration study: docking-derived retention, short-timescale structural retention and endpoint MM-GBSA are not interchangeable estimands. The paper should not be presented as validation of a resistance-resilient lead.

## Prose audit

### Report-style

The canonical main text and SI contain no active job IDs, execution dates, file-copy instructions, pending workflow states, or internal revision commentary in the scientific narrative. Operational provenance remains in the DAR and manifests.

The following are intentionally retained because they are scientific scope labels, not workflow status:

- `secondary structural-stress test`;
- `outside the Set-C estimand`;
- `single-replicate`;
- `not a free-energy or experimental resistance measure`.

### AI-jargon

No promotional AI-style wording was found in the canonical main text or SI. Terms such as `robustness analysis`, `sensitivity analysis` and `endpoint diagnostic` are used in their technical sense. The discussion uses measurable alternatives and does not claim that the workflow is comprehensive, transformative, or biologically validated.

### Scientific register

PASS. The Discussion is explanatory rather than merely descriptive: it explains possible causes of docking/MD divergence, distinguishes estimands, relates PfCRT interpretation to structural context, and states what experiments would constitute validation.

## Figures and tables

- All figures referenced by V2609 were found in `manuscript/LaTeX/Graphics/`.
- The workflow figure separates docking, RRS and MD branches.
- The scatter figure distinguishes docking-RRS from MD-RRS and reports the non-equivalent-estimand interpretation.
- The cross-metric figure states the target-balanced population and the non-independence of PNS and RRS inputs.
- SI tables provide cohort scope, homology QC, RRS sensitivity, MM-GBSA, PP-15, robustness transfer and multi-seed results.
- SEM, SDprop, confidence intervals and missing values are labelled distinctly.
- No table of SLURM status is present in the manuscript or SI.

**Minor remaining visual check:** inspect the final rendered PDF at submission size for line breaks and table density; compilation and text extraction do not replace visual inspection.

## LaTeX audit

- Main uses `siunitx` and `cleveref`.
- SI uses `siunitx`, `cleveref` and `xr` with the `MAIN-` prefix.
- Manual `\ref`/`\autoref` cross-references were not found in the canonical V2609 main source.
- The formerly unresolved forward reference to the unnumbered Set-C section was replaced by explicit text.
- Final PDF check: main 32 pages, SI 20 pages, 0 `??`.

## Validation results

```text
main compilation: PASS (canonical source + matching V2609 .bbl)
SI compilation: PASS (canonical source + matching V2609 .bbl)
cover compilation: PASS (standalone, 1 page)
main pages: 32
SI pages: 20
cover pages: 1
undefined references in final canonical main/SI: 0
unresolved `??`: 0
Python script syntax: PASS
Bash script syntax: PASS
malaria_md tests: 19 passed, 1 skipped
```

A deliberately isolated package-workspace check showed that copying an unrelated
legacy `.bbl` beside the cover can emit stale cover citations; this is a packaging
hazard, not a V2609 main/SI defect. The final package must include only the matching
V2609 `.bbl` files and the standalone cover source/output, or compile the cover in a
clean directory without inherited auxiliary files.

## Remaining author actions

1. Confirm all author names, order, affiliations and ORCID identifiers in Paragon Plus.
2. Confirm funding declaration and sponsor-role statement; do not infer “no funding” from the acknowledgement.
3. Confirm competing-interest declaration.
4. Complete the Zenodo archive and record the final DOI in the data-availability statement if required.
5. Perform the final human visual inspection of all PDF pages and tables.
6. Upload only the canonical V2609 package and the required supporting files.

## Final decision

`READY_FOR_AUTHOR_APPROVAL`

The scientific manuscript is internally coherent and suitable for final author approval. It is not marked `READY_FOR_SUBMISSION` until the human-controlled metadata, declarations, visual inspection and data-archive steps are completed.
