# Response to Reviewers V8 — Executive Summary

**Manuscript**: Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis  
**Journal**: *Journal of Chemical Information and Modeling*  
**Original ID**: ci-2026-00578g  
**Date**: 2026-09-09 (revision completed in <48h)

---

## Overview

All **18 reviewer comments** (2 from Reviewer 1, 16 from Reviewer 2) were resolved with manuscript evidence, new analyses, or protocol clarifications.

**Major additions**:
1. External DEKOIS 2.0 validation (two-arm comparison, honest-negative result)
2. Retrospective control using 5 approved antimalarials (honest-negative)
3. PfCRT re-docking with corrected wild-type receptor
4. Complete physicochemical characterization (3 new tables)
5. Formal statistical multiplicity correction
6. Zenodo reproducibility package (this deposit)

---

## Reviewer 1 (2 points)

### R1.1 — PNS and ACSI definitions missing
**Status**: ✅ Resolved  
**Action**: Added formal definitions to Methods and SM Table S5 footnotes.

### R1.2 — Approved drugs as retrospective control
**Status**: ✅ Resolved  
**Action**: Ran 5 approved antimalarials through the same pipeline. **Result**: Pipeline does not recover clinical resistance signatures (honest-negative). Added SM Table S13 and discussion paragraph.

---

## Reviewer 2 (16 points)

### R2.1 — Clarify polypharmacology workflow
**Status**: ✅ Resolved  
**Action**: New SI Scheme S1 (workflow flowchart) + expanded Methods.

### R2.2 — Within-target favorability unclear
**Status**: ✅ Resolved  
**Action**: Defined "within-target median favorability" explicitly + boundary sensitivity analysis.

### R2.3 — PfCRT structure misassignment
**Status**: ✅ Resolved  
**Action**: Re-docked all 17 candidates on corrected 3D7-like PfCRT WT. Updated all affected tables and RRS values.

### R2.4 — DEKOIS validation
**Status**: ✅ Resolved  
**Action**: Two-arm comparison: MTX-retained (0.502) vs MTX-stripped (0.563). Near-chance, honest-negative.

### R2.6 — Repository 404, data unavailable
**Status**: ✅ Resolved  
**Action**: **This Zenodo deposit** (sha256-verified, CC BY 4.0).

### R2.7 — Statistical multiplicity correction
**Status**: ✅ Resolved  
**Action**: Holm-Bonferroni correction. 3/4 correlations remain significant.

### R2.9 — Single seed sensitivity
**Status**: ✅ Resolved  
**Action**: 5-seed runs for PP-15 and PP-01. Maximum spread 0.054 kcal/mol.

### R2.14 — Physicochemical characterization
**Status**: ✅ Resolved  
**Action**: Added 3 new tables (Lipinski/Veber, QED, ADMET).

---

## Honest-Negative Results

Two analyses produced **honest-negative** results, both transparently reported:

1. **DEKOIS 2.0**: Near-chance (ROC-AUC 0.45) → docking scores are prioritization hypotheses, not activity predictions
2. **Retrospective approved drugs**: Pipeline does not recover clinical resistance → computational profiles require wet-lab validation

**Both strengthen methodological transparency.**

---

**Full details**: See Response_to_Reviewers_P1_V8.pdf in manuscript submission
