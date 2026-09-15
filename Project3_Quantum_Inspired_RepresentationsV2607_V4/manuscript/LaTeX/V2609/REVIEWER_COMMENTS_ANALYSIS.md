# P3 Reviewer Comments Analysis — JCAMD Submission

**Date:** 15 September 2026  
**Document Purpose:** Systematic analysis and categorization of all reviewer feedback

---

## Summary Statistics

| Reviewer | Major Issues | Minor Issues | Total Points |
|----------|-------------|--------------|--------------|
| Reviewer 1 | 1 (comprehensive critique) | 0 | 1 |
| Reviewer 2 | 1 (correlation interpretation) | 10 (missing refs/annotations) | 11 |
| **TOTAL** | **2** | **10** | **12** |

---

## Reviewer 1: Major Methodological Critique

### R1.1 — Fundamental Approach and Validation Strategy (CRITICAL)

**Reviewer's Core Arguments:**

1. **"African" Descriptor Framing:**
   - Questions the validity of "African antimalarial compounds" as a scientific category
   - Points out molecules were artificially generated, not naturally sourced
   - Suggests national/regional origin should not interfere with objective scientific assessment
   - Quote: *"what on Earth is an 'African' molecule anyway? Are the protons in the carbon nuclei 100% African?"*

2. **Validation Methodology:**
   - Current approach (calculated activity scores) is wrong
   - Calculated activity scores are "notoriously easy to predict"
   - ROC AUC 0.96 is "better than real life" — unrealistically high for bioactivity measurements
   - Nothing in malaria bioactivity can achieve such high experimental accuracy

3. **ChEMBL Data Pooling Issues:**
   - ChEMBL malaria data spans diverse battery of tests against different targets
   - Tests at different Plasmodium development stages
   - Pooling "absolutely uncorrelated data together makes no sense"
   - Learning associated chemotypes by heart is not validation

4. **Recommended Validation Strategy:**
   - ChEMBL contains thousands of endpoints (>700 with enough molecules)
   - Endpoints have both actives and inactives with comparable pKi/pIC50 values
   - Data from same assay CAN be compared
   - Some sets feature thousands of compounds
   - **Proper benchmark:** Test new descriptors against ECFP on diverse ChEMBL endpoints
   - Success criterion: If descriptors win on at least ONE target where classical methods fail, then they're "good everywhere, not only in Africa"

**Severity:** CRITICAL — challenges fundamental premise of the study

**Required Actions:**
1. Reframe "African natural product-inspired" chemical space with proper scientific justification
2. Address artificial generation vs. natural sourcing clarification
3. Explain ROC AUC 0.96 in context (may be overfitting, cross-validation issues, or dataset characteristics)
4. Acknowledge ChEMBL data heterogeneity issues
5. Implement or propose endpoint-specific ChEMBL validation
6. Benchmark QKS/hybrid descriptors against ECFP on multiple real experimental endpoints
7. Remove or contextualize claims of universal applicability without proper validation

---

## Reviewer 2: Major Issue

### R2.1 — Correlation Interpretation and Predictive Utility

**Location:** Page 9, Section 4.2

**Reviewer's Concern:**
- Pearson correlation coefficients around 0.47 indicate "low correlation"
- Low correlation has "little predictive use"
- Docking scores for this target may not be reliable enough compared to experimental data
- Recommends formulating section "more carefully"

**Severity:** MAJOR — questions validity of key results

**Required Actions:**
1. Clarify what correlation coefficient of 0.47 means in this context
2. Report statistical significance (p-values, confidence intervals)
3. Provide context for "predictive utility" — what was being predicted?
4. Address docking score reliability
5. Compare to literature benchmarks for similar analyses
6. Reframe interpretation to be more conservative/accurate
7. Consider additional validation if correlation is indeed weak

**Current Text Issues:**
- May be overstating predictive power
- May lack statistical context (significance testing)
- May need validation against experimental data

---

## Reviewer 2: Minor Issues (10 Total)

All issues involve missing references or annotations marked with "??" in the manuscript or supporting information.

### R2m.1 — Page 5, Section 2.7: Two Missing References
**Location:** Main text, page 5, section 2.7  
**Issue:** Two references marked by "??"  
**Action Required:** Identify and complete both missing citations

### R2m.2 — Page 7, Section 3.4: Two Missing Annotations
**Location:** Main text, page 7, section 3.4  
**Issue:** Two annotations marked by "??"  
**Action Required:** Complete both missing annotations (likely figure/table/equation references)

### R2m.3 — Page 8, Section 3.6: One Missing Annotation
**Location:** Main text, page 8, section 3.6  
**Issue:** One annotation marked by "??"  
**Action Required:** Complete missing annotation

### R2m.4 — Page 8, Section 3.7: Multi-Target Docking Data Source Unclear
**Location:** Main text, page 8, section 3.7  
**Issue:** Source and type of "multi-target docking data" not clear  
**Context:** Reviewer notes information is "seemingly found in the supporting information page S10"  
**Action Required:** 
1. Add conclusive information about data source in main text
2. Verify SI page S10 reference is correct
3. Ensure cross-reference is clear

### R2m.5 — Page 8, Section 3.7: One Missing SI Reference
**Location:** Main text, page 8, section 3.7  
**Issue:** One reference to supplementary material marked by "??"  
**Action Required:** Complete missing SI reference

### R2m.6 — Citation Format and Style
**Location:** Throughout manuscript  
**Issue:** Format and style of reference citations may need adjustment to JCAMD requirements  
**Action Required:** 
1. Review JCAMD author guidelines for citation format
2. Adjust all citations to match required format
3. Ensure consistency throughout

### R2m.7 — SI Page 2, Section 2: One Missing Annotation
**Location:** Supporting Information, page 2, section 2  
**Issue:** One annotation marked by "??"  
**Action Required:** Complete missing annotation

### R2m.8 — SI Page 2, Section 3: Two Missing Annotations
**Location:** Supporting Information, page 2, section 3  
**Issue:** Two annotations marked by "??"  
**Action Required:** Complete both missing annotations

### R2m.9 — SI Page 9, Table S9: One Missing Annotation
**Location:** Supporting Information, page 9, table S9  
**Issue:** One annotation marked by "??"  
**Action Required:** Complete missing table annotation (likely footnote or reference)

### R2m.10 — General Citation Format Throughout
**Location:** Throughout manuscript and SI  
**Issue:** Ensure all citation formats match JCAMD requirements  
**Action Required:** Systematic review and correction of all citations

---

## Response Strategy Framework

### Tier 1: Critical Issues (Must Address Fully)
1. **R1.1:** Fundamental methodology and "African" framing
2. **R2.1:** Correlation interpretation and predictive utility

### Tier 2: Technical Corrections (Must Complete)
- All 10 R2 minor issues (missing references/annotations)
- Citation format standardization

### Response Tone Guidelines

**For R1 (Challenging/Hostile Tone):**
- Remain professional and respectful
- Acknowledge valid scientific concerns
- Do NOT be defensive about "African" terminology
- Provide clear scientific justification for approach
- Accept limitations where appropriate
- Demonstrate commitment to rigorous validation
- Offer concrete improvements/additions

**For R2 (Constructive/Technical):**
- Thank for careful reading
- Address each point systematically
- Provide specific page/line references for corrections
- Acknowledge oversight on missing references
- Clarify statistical interpretations

### Key Manuscript Revisions Required

1. **Introduction/Methods:** Reframe "African natural product-inspired" chemical space
2. **Results:** Add proper statistical context to correlation analyses
3. **Discussion:** Address ChEMBL endpoint-specific validation
4. **Discussion:** Contextualize ROC AUC 0.96 performance
5. **Throughout:** Complete all missing references/annotations (10 locations)
6. **Throughout:** Standardize citation format to JCAMD requirements

---

## Cross-Reference Checklist

Before finalizing response:
- [ ] Every R1 argument addressed with scientific evidence
- [ ] Every R2 major issue addressed with clarification or additional analysis
- [ ] All 10 minor issues fixed with specific manuscript locations cited
- [ ] All manuscript revisions cross-referenced in response document
- [ ] Tone professional and scientific throughout
- [ ] No defensive language about methodology
- [ ] Proper acknowledgment of limitations
- [ ] Clear plan for additional validation if needed

---

## Files to Modify

1. `Paper3_Quantum_InspiredV2609.tex` — Main manuscript revisions
2. `Paper3_Quantum_Inspired_SM_V2609.tex` — SI revisions
3. `Response_to_Reviewers_P3_V2609.tex` — Point-by-point response (new file)
4. `Cover_Letter_P3_V2609.tex` — Update to reference revision addressing concerns

---

## Notes for Response Document

- R1's tone is challenging but raises valid scientific concerns
- Must not dismiss R1's critique as merely "tone" — the science questions are real
- R2 is helpful and constructive — thank appropriately
- The "??" issues suggest manuscript was submitted with incomplete references (LaTeX compilation issues)
- Need to verify all \ref{} and \cite{} commands compile correctly
- May need to add new ChEMBL benchmark analyses if committing to that validation
