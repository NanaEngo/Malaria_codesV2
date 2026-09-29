# JCAMD Submission Adaptation Summary

**Date:** September 28, 2026  
**Adapted By:** AI Assistant (Kiro) with user oversight  
**Source:** Project1_Chem_space_antimalarial_V7_CorrectedGrid/Submission_DD (P1 V8)

---

## Purpose

Adapt the P1 V8 manuscript from Digital Discovery format to Journal of Computer-Aided Molecular Design (JCAMD) format, with **special attention to resolving cross-references** that do not work on submission platforms.

---

## Major Adaptations

### 1. Cross-Reference Resolution (Primary Issue)

**Problem:** The original manuscript used LaTeX `xr` package for bidirectional cross-references between main text and Supporting Information:
- Main → SI: `\Cref{SM-label}`
- SI → Main: `\Cref{M-label}`

**These cross-references break on journal submission platforms** because:
- The platform compiles files separately
- The `\externaldocument` command cannot access the other file's aux data
- Result: "??" appears in place of references

**Solution:** All cross-references replaced with explicit inline text containing sufficient context.

#### Main Manuscript Cross-Reference Replacements

| Original Cross-Reference | Replacement Text | Context Provided |
|-------------------------|------------------|------------------|
| `\Cref{SM-sec:sm_val_dekois}` | "Section S1 of the Supporting Information" | Explicit section number |
| `\Cref{SM-tab:sm_vina_distributions}` | "Table S1 (per-target medians: PfDHFR -5.92, PfCRT -8.06, PfClpP -6.02, PfATP4 -6.38 kcal mol⁻¹; see Supporting Information)" | **Table number + key data inline** |
| `\Cref{SM-fig:chemical_space_coverage}` | "Figure S1 in the Supporting Information" | Explicit figure number |
| `\Cref{SM-tab:druglikeness}` | "Table S2 in the Supporting Information" | Explicit table number |
| `\Cref{SM-tab:admet}` | "Table S3 in the Supporting Information" | Explicit table number |
| `\Cref{SM-sec:sm_val_redock_null}` | "Section S2 of the Supporting Information (pipeline-null control)" | **Section number + context** |
| `\Cref{SM-tab:rrs_classes}` | "Table S4 in the Supporting Information (A*: WT score ≥7 kcal mol⁻¹ and all RRS ≥80%; B: all RRS ≥70%; C: at least one RRS ≥80%; D: no RRS ≥80%)" | **Table number + complete class definitions inline** |
| `\Cref{SM-tab:crossmetric}` | "Table S5 in the Supporting Information" | Explicit table number |
| `\Cref{SM-sec:sm_crossmetric}` | "Section S3 of the Supporting Information" | Explicit section number |
| `\Cref{SM-tab:sm_retrospective_antimalarials}` | "Table S6 in the Supporting Information" | Explicit table number |

#### Supporting Information Cross-Reference Replacements

| Original Cross-Reference | Replacement Text |
|-------------------------|------------------|
| `\Cref{M-sec:methods_cohort}` | "Section 2.2 of the main text" |
| `\Cref{M-eq:rrs}` | "Eq. 1 of the main text" |
| `\Cref{M-sec:methods_rrs}` | "Section 2.4 of the main text" |
| `\Cref{M-sec:methods_pns}` | "Section 2.5 of the main text" |
| `\Cref{M-sec:methods_docking}` | "Section 2.3 of the main text" |
| `\Cref{M-sec:methods_funnel}` | "Section 2.1 of the main text" |
| `\Cref{M-tab:rrs_main}` | "Table 1 of the main text" |
| `\Cref{M-tab:dual_priority}` | "Table 2 of the main text" |
| `\Cref{M-sec:methods_boundary}` | "Section 2.6 of the main text" |
| `\Cref{M-sec:results_mutation}` | "Section 3.3 of the main text" |
| `\Cref{M-sec:methods_dock_val}` | "Section 2.3.1 of the main text" |

**Key Design Principle:** Where referenced content is critical for interpretation, **inline context was added** (e.g., RRS class definitions, per-target medians) so readers don't need to interrupt their reading flow.

---

### 2. LaTeX Package Cleanup

**Removed from both files:**
```latex
% Cross-references to the Supporting Information
\usepackage{xr}
\externaldocument[SM-]{P1_Integrated_Polypharmacology_RRS_SM_V8_DD}
```

**Replaced with:**
```latex
% Cross-references removed for standalone JCAMD submission
```

This ensures:
- ✅ No dependency on external aux files
- ✅ Clean compilation on submission platforms
- ✅ No unresolved references

---

### 3. Cover Letter Update

**Changed from:** Digital Discovery submission  
**Changed to:** JCAMD submission

**Key modifications:**
- Editor address updated to JCAMD Editor-in-Chief (Springer Nature)
- Journal scope emphasis: "computer-aided molecular design" instead of "data-driven discovery"
- Relevance section tailored to JCAMD readership
- Scientific content and validation summary unchanged

---

## Files Created

### New Source Files
1. **P1_Integrated_Polypharmacology_RRS_Main_JCAMD.tex** - Adapted main manuscript
2. **P1_Integrated_Polypharmacology_RRS_SM_JCAMD.tex** - Adapted supporting information
3. **Cover_Letter_P1_JCAMD.tex** - Adapted cover letter

### Compiled PDFs
1. **P1_Integrated_Polypharmacology_RRS_Main_JCAMD.pdf** (15 pages, no errors)
2. **P1_Integrated_Polypharmacology_RRS_SM_JCAMD.pdf** (14 pages, no errors)
3. **Cover_Letter_P1_JCAMD.pdf** (2 pages, no errors)

### Documentation
1. **README_JCAMD_SUBMISSION.md** - Complete submission package documentation
2. **ADAPTATION_SUMMARY.md** - This file

### Supporting Files (Copied)
- Graphics/ directory (all figures)
- tables/ directory (all SI tables)
- Sao_Chim_Space.bib (bibliography)
- Data_Availability_Statement.tex

---

## Content Integrity Verification

### ✅ Scientific Content
- [x] All results preserved
- [x] All validation data intact
- [x] All statistical analyses unchanged
- [x] All figures included
- [x] All tables included
- [x] All citations preserved

### ✅ Formatting
- [x] No undefined references
- [x] No missing citations
- [x] All cross-references resolved
- [x] Equations numbered correctly
- [x] Figures and tables numbered correctly
- [x] Bibliography complete

### ✅ Compilation
- [x] Main manuscript compiles cleanly
- [x] Supporting Information compiles cleanly
- [x] Cover letter compiles cleanly
- [x] No LaTeX errors
- [x] No missing references
- [x] All PDFs generated

---

## Testing Performed

### Compilation Test
```bash
# Main manuscript
pdflatex + bibtex + 2x pdflatex → SUCCESS (15 pages)

# Supporting Information  
pdflatex + bibtex + 2x pdflatex → SUCCESS (14 pages)

# Cover letter
pdflatex → SUCCESS (2 pages)
```

**Result:** All documents compile without errors.

### Cross-Reference Test
- ✅ All inline references readable
- ✅ No "??" markers in compiled PDFs
- ✅ Context sufficient for standalone reading
- ✅ Table/Figure/Section numbers explicit

---

## Advantages of This Approach

### 1. **Platform Independence**
- No dependency on `xr` package
- Works on any LaTeX platform
- No risk of broken cross-references during submission

### 2. **Enhanced Readability**
- Critical data (e.g., RRS class definitions, per-target medians) available inline
- Readers don't need to flip to SI for key information
- Better for print versions

### 3. **Submission Ready**
- Guaranteed to work on journal submission platforms
- No post-submission formatting issues
- Clean, professional presentation

### 4. **Reproducibility**
- All source files self-contained
- Can be compiled anywhere
- No hidden dependencies

---

## What Was NOT Changed

### Scientific Content
- ✅ All numerical results identical
- ✅ All conclusions unchanged
- ✅ All validation results preserved
- ✅ All statistical tests unchanged
- ✅ All figures unchanged
- ✅ All tables unchanged

### Structure
- ✅ Section organization identical
- ✅ Abstract unchanged
- ✅ Keywords unchanged
- ✅ Author list unchanged
- ✅ ORCID identifiers preserved
- ✅ Data availability statement unchanged

---

## Recommendation

**The Submission_JCAMD package is ready for submission to JCAMD.** 

The adaptation successfully resolves the cross-reference issue while:
- Maintaining complete scientific integrity
- Enhancing readability through inline context
- Ensuring platform independence
- Providing clean, error-free compilation

**No further modifications needed** unless journal-specific formatting requirements emerge during submission.

---

## Contact for Questions

For questions about this adaptation, refer to:
- README_JCAMD_SUBMISSION.md for submission instructions
- Original AGENTS.md for project context
- P1_DATA_ANALYSIS_REPORT.md for scientific background

**Corresponding Author:**  
Myke Vital Sao Temgoua  
myke-vital.sao@facsciences-uy1.cm
