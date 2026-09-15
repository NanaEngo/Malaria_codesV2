# Structural Model Clarification Summary

**Date:** 2026-09-15  
**Issue:** Potential confusion between two distinct structure sets used for different purposes

## Problem Statement

P3 manuscript uses two different sets of PDB structures:
1. **Tartarus docking structures:** 1SYH, 6Y2F, 4LDE, 2F6I  
2. **MD/resilience structures (P1/P2):** 7F3Y, 6UKJ, 9N10

These serve **completely different analytical purposes** and must not be conflated.

## Resolution

### Purpose Distinction

| Structure Set | Purpose | Use | Papers |
|--------------|---------|-----|---------|
| **1SYH, 6Y2F, 4LDE, 2F6I** | External chemoinformatic validation oracle | Descriptor stress test via Tartarus docking | P3 only |
| **7F3Y, 6UKJ, 9N10** | Refined structural models | Rigorous MD simulations and resistance-resilience assessment | P1, P2 (companion studies) |

### Clarifications Added

#### 1. Main Manuscript (Paper3_Quantum_InspiredV2609.tex, ~line 211)
**Section 3.3: Binding-relevant information in tensor network compression**

Added after docking results:
> "The docking structures (1SYH, 6Y2F, 4LDE, 2F6I) serve as an external chemoinformatic validation oracle and are distinct from the refined models (7F3Y, 6UKJ, 9N10) used for molecular dynamics in companion studies."

#### 2. Supporting Information (Paper3_Quantum_Inspired_SM_V2609.tex, ~line 532)
**Section 2.3: Comparison with existing tools**

Added prominent note:
> **Note on structural models:** The Tartarus docking structures (1SYH, 6Y2F, 4LDE, 2F6I) serve solely as an external chemoinformatic validation oracle—a descriptor stress test to assess information retention—and are distinct from the refined structural models (PfDHFR/7F3Y, PfCRT/6UKJ, PfATP4/9N10) used for molecular dynamics and resistance-resilience assessments in companion studies [Temgoua2026tb, saognn2026]. The docking analysis here does not inform, and is not informed by, the MD-based binding free energy calculations reported elsewhere.

#### 3. Response to Reviewers (Response_to_Reviewers_P3_V2609.tex, ~line 411)
**R2m.4 Resolution section**

Added structural clarification:
> **Structural model clarification:** The Tartarus docking structures (PfDHFR/1SYH, PfCRT/4LDE, PfATP4/6Y2F, PfClpP/2F6I) serve as an external chemoinformatic validation oracle—a descriptor stress test—and are distinct from the refined structural models (PfDHFR/7F3Y, PfCRT/6UKJ, PfATP4/9N10) used for molecular dynamics and resistance-resilience assessments in companion studies. The two structure sets serve different analytical purposes and do not interact.

## Key Messages

1. **Tartarus structures (1SYH, 6Y2F, 4LDE, 2F6I):**
   - Purpose: External validation oracle for descriptor performance
   - Analysis: AutoDock Vina docking scores to test information retention
   - Scope: P3 manuscript only
   - Interpretation: Stress test for TFP/TNE/QKS representations

2. **MD structures (7F3Y, 6UKJ, 9N10):**
   - Purpose: Rigorous structural models for binding thermodynamics
   - Analysis: Explicit-solvent MD simulations, MM/GBSA, resistance-resilience scoring
   - Scope: P1 and P2 companion papers
   - Interpretation: Biophysical validation of lead candidates

3. **No overlap or interaction:**
   - The two analyses are independent
   - Tartarus docking does not inform MD calculations
   - MD results do not influence descriptor validation
   - Different molecules, different methods, different endpoints

## Files Modified

1. `Paper3_Quantum_InspiredV2609.tex` (main manuscript, line ~211)
2. `Paper3_Quantum_Inspired_SM_V2609.tex` (SI, line ~532)
3. `Response_to_Reviewers_P3_V2609.tex` (R2m.4 resolution, line ~411)

## Additional Fixes

- Fixed BibTeX case mismatch: `\citep{Temgoua2026tb}` → `\citep{temgoua2026tb}` (SI line 688)

## Compilation Status

All documents compile cleanly:
- ✅ Main manuscript: 15 pages, 0 warnings
- ✅ Supporting Information: 15 pages, 0 warnings (case mismatch fixed)
- ✅ Response to Reviewers: 5 pages, 0 warnings
- ✅ Cover Letter: 1 page, 0 warnings

## Rationale

This clarification prevents potential reviewer confusion about:
1. Why different PDB structures are cited in different contexts
2. Whether the docking analysis contradicts or duplicates the MD work
3. How the two validation strategies relate to each other

The additions make explicit that P3 uses Tartarus as a **chemoinformatic benchmark** (can the descriptors predict docking scores?) while P1/P2 use refined structures for **biophysical validation** (do the molecules actually bind?). These are complementary but independent validation strategies.
