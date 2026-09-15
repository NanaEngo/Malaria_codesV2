# P3 Manuscript V2609 — JCAMD Revision

**Date:** 15 September 2026  
**Status:** Revision in progress (responding to reviewer feedback)

## Overview

This folder contains the revised manuscript files for P3 (Quantum-Inspired Molecular Representations) in response to JCAMD reviewer comments received after initial submission.

## Files in This Directory

- `Paper3_Quantum_InspiredV2609.tex` — Main manuscript (revised from V2608)
- `Paper3_Quantum_Inspired_SM_V2609.tex` — Supporting Information (revised from V2608)
- `Bibliography_Paper3.bib` — Bibliography file
- `Cover_Letter_P3_V2609.tex` — Cover letter for revision submission
- `Response_to_Reviewers_P3_V2609.tex` — Point-by-point response to reviewer comments
- `Graphics/` — All figures and graphics

## Reviewer Comments Summary

### Reviewer 1 (Major Critique)
- **Core Issue:** Fundamental methodological critique about descriptor validation strategy
- **Key Points:**
  - Questions the "African" descriptor framing and artificial generation approach
  - Challenges using calculated activity scores instead of real experimental endpoints
  - Critiques ROC AUC 0.96 as unrealistically high for biological data
  - Points out ChEMBL data pooling issues (mixing uncorrelated assays)
  - **Recommendation:** Benchmark against diverse ChEMBL endpoints with real experimental data

### Reviewer 2 (1 Major + 10 Minor Issues)
- **Major Issue:** Correlation coefficients ~0.47 indicate low correlation, limited predictive utility
- **Minor Issues:** 10 missing references/annotations marked with "??" throughout manuscript and SI

## Revision Strategy

1. **Address R1's methodology:** Reframe descriptor validation with ChEMBL endpoint-specific benchmarks
2. **Address R1's "African" framing:** Clarify chemical space definition and generation rationale
3. **Address R1's ROC AUC critique:** Provide context for performance metrics and data heterogeneity
4. **Address R2's correlation interpretation:** Clarify statistical significance and predictive context
5. **Fix all R2 minor issues:** Complete all missing references and annotations

## Version History

- **V2608:** Initial JCAMD submission (August 2026)
- **V2609:** Revision responding to reviewer feedback (September 2026)

## Compilation

```bash
pdflatex Paper3_Quantum_InspiredV2609.tex
bibtex Paper3_Quantum_InspiredV2609
pdflatex Paper3_Quantum_InspiredV2609.tex
pdflatex Paper3_Quantum_InspiredV2609.tex
```

## Status Tracking

- [x] V2609 folder created
- [x] Files migrated from V2608
- [ ] Response to Reviewers document drafted
- [ ] Manuscript revised per reviewer comments
- [ ] Supporting Information revised per reviewer comments
- [ ] Cover letter updated
- [ ] All missing references/annotations completed
- [ ] Manuscript compilation verified
- [ ] Ready for resubmission
