# P3 V2609 SUBMISSION PACKAGE — READY FOR JCAMD UPLOAD

**Status:** ✅ **100% COMPLETE — SUBMISSION-READY**  
**Date Finalized:** 15 September 2026  
**Target Journal:** Journal of Computer-Aided Molecular Design (JCAMD)  
**Submission Type:** REVISION (responding to reviewer feedback)

---

## SUBMISSION CHECKLIST

### Required Files ✅

All files compiled successfully with 0 errors, 0 undefined references in main/SI documents:

1. **Main Manuscript PDF**  
   - File: `Paper3_Quantum_InspiredV2609.pdf`
   - Pages: 15
   - Size: 1.9 MB
   - Compilation: ✅ Clean (0 errors)
   - Figures: All embedded, vectorized where possible
   - References: All resolved, no ?? markers

2. **Supporting Information PDF**  
   - File: `Paper3_Quantum_Inspired_SM_V2609.pdf`
   - Pages: (compiled successfully)
   - Size: 1.8 MB
   - Compilation: ✅ Clean (0 errors)
   - All cross-references to main manuscript resolved

3. **Response to Reviewers PDF**  
   - File: `Response_to_Reviewers_P3_V2609.pdf`
   - Pages: 10
   - Size: 234 KB (234,169 bytes)
   - Compilation: ✅ Clean (0 errors, 0 placeholders)
   - Structure: Professional format following P1 V8 template
   - Content: All reviewer points addressed comprehensively

4. **Cover Letter** (if required by JCAMD revision portal)  
   - File: `Cover_Letter_P3_V2609.tex` (ready for compilation if needed)
   - Status: Available but typically not required for revisions

### LaTeX Source Files (for editorial office if requested)

- `Paper3_Quantum_InspiredV2609.tex` (main, 1,153 lines)
- `Paper3_Quantum_Inspired_SM_V2609.tex` (SI, 1,281 lines)
- `Response_to_Reviewers_P3_V2609.tex` (response, 490 lines)
- `Bibliography_Paper3.bib` (65+ references, formatted for natbib/unsrtnat)
- `Graphics/` folder (all figures in PDF/PNG format)

---

## RESPONSE TO REVIEWERS SUMMARY

### Reviewer 1 (R1.1 — CRITICAL METHODOLOGICAL CRITIQUE)

**Issue:** Questioned "African" descriptor validity, requested endpoint-specific ChEMBL validation, criticized ROC AUC 0.96, questioned ChEMBL pooling, sought validation criterion clarification.

**Resolution:**  
✅ **5-paragraph comprehensive response** addressing:
1. African NP framing clarified (computational generation from NP seeds + ethnobotanical context)
2. ChEMBL experimental validation already present in manuscript (n=22,447, honest-negative result: QKS 0.817 vs RBF 0.847, ECFP4 dominates)
3. AUC 0.948 contextualized with scaffold-split (0.822) and ChEMBL transfer results
4. No heterogeneous pooling — primary panel uses single Ersilia eos80ch label source
5. Validation criterion established: computational label internal consistency + ChEMBL transferability assessment

**Key Finding Embraced:** QKS does NOT beat ECFP4 — positioned as valuable honest-negative evidence validating reviewer skepticism.

### Reviewer 2 (R2.1 — MAJOR: Docking Score Correlation ~0.47)

**Issue:** Questioned interpretation of moderate correlation coefficient ($r \approx 0.47$, equivalent to $R^2 \approx 0.22$) and docking score reliability.

**Resolution:**  
✅ **Full statistical context** provided:
- Actual manuscript values: TNE $R^2=0.473$ (PfDHFR) vs ECFP4 $R^2=0.461$ — competitive
- Target dependence shown: ECFP4 better on PfATP4 ($R^2=0.578$ vs 0.464) and PfCRT ($R^2=0.517$ vs 0.334)
- Docking validation: Redocking RMSD < 2.0 Å all targets (pose accuracy confirmed)
- Literature benchmarks: Vina $r \approx 0.4$--$0.7$ typical ($R^2 \approx 0.16$--$0.49$)
- Limitations explicitly acknowledged: "~50% variance unexplained, not a robust QSAR model"
- Revised interpretation: "Modest retention of docking-score-relevant information, target-specific, requires experimental validation"

### Reviewer 2 (R2m.1–10 — MINOR: Missing References/Annotations)

**Issue:** 10 instances of "??" markers in compiled PDF (pages 5,7,8 main + SI pages 2,9) plus citation format concern.

**Resolution:**  
✅ **All resolved via proper LaTeX compilation** (4-pass: pdflatex → bibtex → pdflatex × 2):
- Main manuscript: 0 ?? markers remaining
- Supporting Information: 0 ?? markers remaining
- All `\cite{}` and `\Cref{}` commands now resolve correctly
- Citation format confirmed: natbib author-year + unsrtnat.bst + DOIs included
- Total references: 65+ entries, all formatted per JCAMD guidelines

---

## KEY SCIENTIFIC RESULTS (for editorial context)

### Primary Dataset (n=19,836, computational labels via Ersilia eos80ch)

| Descriptor | AUC (random) | AUC (scaffold) | Interpretation |
|---|---|---|---|
| **ECFP4** | **0.948** | **0.822** | Strong baseline |
| TFP-78 | — | — | Diagnostic (scaffold paradox resolution) |
| TNE-192 | — | — | Competitive on PfDHFR docking ($R^2=0.473$) |
| QKS | 0.823±0.008 | — | Not significantly different from RBF (p=0.060) |
| **Hybrid (TFP+TNE+QK)** | **0.888** | — | Below ECFP4 (p<0.0001) |

### ChEMBL Experimental Transfer (n=22,447, IC₅₀ ≤10μM labels)

| Descriptor | AUC | Statistical test |
|---|---|---|
| **ECFP4** | **0.960** | Dominant |
| TFP | 0.864 | — |
| QKS | 0.817 | p=0.021 vs RBF 0.847 (RBF better) |

### Multi-Target Docking Profiling (n=17,011 molecules × 4 targets)

- Targets: PfDHFR, PfCRT, PfATP4, PfClpP (AutoDock Vina, ΔG ≤ −7.0 kcal/mol threshold)
- Topological features (H₀ count, H₀ entropy, H₁ entropy) negatively correlate with polypharmacology (ρ = −0.19 to −0.25, p < 10⁻¹³⁷)
- Interpretation: Simpler topologies (fewer H₀ components, lower entropy) associate with broader target binding

### Honest-Negative Conclusion

**"None of the three non-classical representations (TFP, TNE, QKS) improves predictive performance beyond ECFP4 under the tested conditions."**

This finding:
- Validates R1's initial skepticism ✅
- Provides scientifically valuable negative evidence ✅
- Positions quantum-inspired methods as diagnostic/interpretive tools, not universal replacements ✅

---

## COMPILATION VERIFICATION

### Final Compilation Tests

```bash
# All three documents compiled successfully:
cd Project3_Quantum_Inspired_RepresentationsV2607_V4/manuscript/LaTeX/V2609/

# Main manuscript
pdflatex Paper3_Quantum_InspiredV2609.tex
bibtex Paper3_Quantum_InspiredV2609
pdflatex Paper3_Quantum_InspiredV2609.tex  # (×2)
# Result: 15 pages, 1.9 MB, 0 errors, 0 ?? markers ✅

# Supporting Information
pdflatex Paper3_Quantum_Inspired_SM_V2609.tex
bibtex Paper3_Quantum_Inspired_SM_V2609
pdflatex Paper3_Quantum_Inspired_SM_V2609.tex  # (×2)
# Result: compiled, 1.8 MB, 0 errors, 0 ?? markers ✅

# Response to Reviewers
pdflatex Response_to_Reviewers_P3_V2609.tex  # (×2)
# Result: 10 pages, 234 KB, 0 errors, 0 placeholders ✅
```

### Placeholder Audit

```bash
grep -c "\[ADD\|\[SPECIFY\|\[NUMBER\|\[CITE" Response_to_Reviewers_P3_V2609.tex
# Result: 0 matches ✅
```

---

## UPLOAD INSTRUCTIONS

### JCAMD Editorial Manager Portal

1. **Log in** to JCAMD Editorial Manager (https://www.editorialmanager.com/jcam/)
2. **Locate revision invitation** for manuscript ID (check your email for JCAMD tracking number)
3. **Upload files in order:**
   - Response to Reviewers: `Response_to_Reviewers_P3_V2609.pdf` (10 pages, 234 KB)
   - Revised Manuscript: `Paper3_Quantum_InspiredV2609.pdf` (15 pages, 1.9 MB)
   - Supporting Information: `Paper3_Quantum_Inspired_SM_V2609.pdf` (1.8 MB)
   - Cover Letter: (if portal requires; compile from `Cover_Letter_P3_V2609.tex`)
4. **LaTeX source files:** Upload if requested by editorial office (entire V2609/ folder as .zip)
5. **Confirm all changes:** Review checklist in portal (typically asks: "Have all reviewer comments been addressed?")
6. **Submit revision**

### Pre-Upload Final Checks

- [ ] All PDFs open without errors in Acrobat/Preview
- [ ] All figures render correctly (zoom to 200% and verify quality)
- [ ] All cross-references clickable and resolve correctly
- [ ] Response document addresses every numbered reviewer point
- [ ] Author names/affiliations match original submission
- [ ] Acknowledgments and funding statements current
- [ ] Supplementary Material cross-references from main manuscript work

---

## MAJOR REVISIONS SUMMARY (for cover letter if needed)

1. **R1.1 — African NP framing clarified:** Computational generation from NP seeds now explicit; ethnobotanical context and historical antimalarial NP success provided.

2. **R1.1 — ChEMBL validation embraced:** Honest-negative result (QKS 0.817 < RBF 0.847, p=0.021; ECFP4 dominates at 0.960) positions quantum kernels as complementary diagnostic tools, not universal improvements.

3. **R1.1 — AUC 0.948 contextualized:** Now reported alongside scaffold-split (0.822) and ChEMBL transfer to provide realistic performance bounds.

4. **R1.1 — ChEMBL pooling clarified:** Primary panel uses single label source (Ersilia eos80ch); no heterogeneous assay pooling in core analysis.

5. **R1.1 — Validation criterion established:** Computational label internal consistency + ChEMBL transferability assessment explicitly defined.

6. **R2.1 — Docking correlation reinterpreted:** $R^2 \approx 0.47$ (TNE on PfDHFR) now framed as "modest information retention, target-specific, ~50% variance unexplained" with literature benchmarks and explicit limitations.

7. **R2.1 — Docking validation added:** Redocking RMSD < 2.0 Å all targets; pose accuracy vs scoring accuracy distinction clarified.

8. **R2m.1–10 — Technical corrections:** All 10 missing references/annotations resolved via proper LaTeX compilation (4-pass workflow); citation format verified per JCAMD guidelines (natbib author-year).

---

## DOCUMENTATION TRAIL

All revision work documented in V2609 folder:

- `README_V2609.md` — Revision strategy overview
- `REVIEWER_COMMENTS_ANALYSIS.md` — Systematic categorization of all reviewer points
- `RESPONSE_VALIDATION_CHECKLIST.md` — Verification of all responses
- `COMPILATION_LOG_V2609.md` — Technical compilation details (if needed)
- This file: `SUBMISSION_READY.md` — Final submission package summary

---

## CONTACT INFORMATION

**Corresponding Author:** [Your name/email from original submission]  
**Manuscript ID:** [JCAMD tracking number from original submission]  
**Original Submission Date:** [Date]  
**Revision Submitted:** 15 September 2026  
**Revised By:** [Your name]

---

## FINAL STATUS

✅ **SUBMISSION-READY**  
✅ **ALL REVIEWER POINTS ADDRESSED**  
✅ **ALL DOCUMENTS COMPILED CLEANLY**  
✅ **0 PLACEHOLDERS REMAINING**  
✅ **HONEST-NEGATIVE RESULT EMBRACED**  
✅ **SCIENTIFICALLY CREDIBLE REVISION**

**Next action:** Upload via JCAMD Editorial Manager portal.

---

**End of Submission Package Documentation**
