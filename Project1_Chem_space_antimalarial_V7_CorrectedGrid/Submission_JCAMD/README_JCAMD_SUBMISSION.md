# JCAMD Submission Package for Project 1 (P1)

**Manuscript Title:** Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis

**Date Prepared:** September 28, 2026

**Adapted From:** Submission_DD (Digital Discovery version)

---

## Package Contents

This directory contains the complete submission package for the Journal of Computer-Aided Molecular Design (JCAMD):

### Main Files
1. **P1_Integrated_Polypharmacology_RRS_Main_JCAMD.tex** - Main manuscript (LaTeX source)
2. **P1_Integrated_Polypharmacology_RRS_Main_JCAMD.pdf** - Main manuscript (compiled, 16 pages) ⚡ UPDATED
3. **P1_Integrated_Polypharmacology_RRS_SM_JCAMD.tex** - Supporting Information (LaTeX source)
4. **P1_Integrated_Polypharmacology_RRS_SM_JCAMD.pdf** - Supporting Information (compiled, 14 pages)
5. **Cover_Letter_P1_JCAMD.tex** - Cover letter (LaTeX source)
6. **Cover_Letter_P1_JCAMD.pdf** - Cover letter (compiled, 2 pages)

### Supporting Files
- **Sao_Chim_Space.bib** - Bibliography database
- **Data_Availability_Statement.tex** - Data availability statement (if needed separately)
- **Graphics/** - All figure files (PDF and PNG formats)
- **tables/** - All supplementary table files (LaTeX format)

---

## Key Adaptations for JCAMD

### 1. **Cross-Reference Resolution**
The original Submission_DD version used the `xr` package for cross-references between main manuscript and supporting information (e.g., `\Cref{SM-tab:...}`). **Since these don't work on submission platforms**, all cross-references have been replaced with:

#### In Main Manuscript:
- `\Cref{SM-sec:sm_val_dekois}` → "Section S1 of the Supporting Information"
- `\Cref{SM-tab:sm_vina_distributions}` → "Table S1 (per-target medians: PfDHFR -5.92, PfCRT -8.06, PfClpP -6.02, PfATP4 -6.38 kcal mol⁻¹; see Supporting Information)"
- `\Cref{SM-fig:chemical_space_coverage}` → "Figure S1 in the Supporting Information"
- `\Cref{SM-tab:druglikeness}` → "Table S2 in the Supporting Information"
- `\Cref{SM-tab:admet}` → "Table S3 in the Supporting Information"
- `\Cref{SM-sec:sm_val_redock_null}` → "Section S2 of the Supporting Information (pipeline-null control)"
- `\Cref{SM-tab:rrs_classes}` → "Table S4 in the Supporting Information (A*: WT score ≥7 kcal mol⁻¹ and all RRS ≥80%; B: all RRS ≥70%; C: at least one RRS ≥80%; D: no RRS ≥80%)"
- `\Cref{SM-tab:crossmetric}` → "Table S5 in the Supporting Information"
- `\Cref{SM-sec:sm_crossmetric}` → "Section S3 of the Supporting Information"
- `\Cref{SM-tab:sm_retrospective_antimalarials}` → "Table S6 in the Supporting Information"

#### In Supporting Information:
- All `\Cref{M-...}` references to main text replaced with explicit section/table/equation numbers
- Example: `\Cref{M-sec:methods_cohort}` → "Section 2.2 of the main text"

### 2. **Journal-Specific Formatting**
- Cover letter updated for JCAMD editor
- Manuscript maintains JCAMD article class compatibility
- All citations and references preserved
- Figure and table captions maintain full context

### 3. **Content Integrity**
- ✅ All scientific content preserved
- ✅ All validation results intact
- ✅ All figures and tables included
- ✅ Complete bibliography
- ✅ Author ORCID identifiers maintained
- ✅ Data availability statement included

---

## Compilation Instructions

To recompile the documents (if needed):

### Main Manuscript
```bash
cd Submission_JCAMD
pdflatex P1_Integrated_Polypharmacology_RRS_Main_JCAMD.tex
bibtex P1_Integrated_Polypharmacology_RRS_Main_JCAMD
pdflatex P1_Integrated_Polypharmacology_RRS_Main_JCAMD.tex
pdflatex P1_Integrated_Polypharmacology_RRS_Main_JCAMD.tex
```

### Supporting Information
```bash
pdflatex P1_Integrated_Polypharmacology_RRS_SM_JCAMD.tex
bibtex P1_Integrated_Polypharmacology_RRS_SM_JCAMD
pdflatex P1_Integrated_Polypharmacology_RRS_SM_JCAMD.tex
pdflatex P1_Integrated_Polypharmacology_RRS_SM_JCAMD.tex
```

### Cover Letter
```bash
pdflatex Cover_Letter_P1_JCAMD.tex
```

---

## Submission Checklist

- [x] Main manuscript compiled without errors (16 pages) ⚡ UPDATED
- [x] Supporting Information compiled without errors (14 pages)
- [x] Cover letter compiled without errors (2 pages)
- [x] All cross-references resolved inline
- [x] All figures present in Graphics/
- [x] All tables present in tables/
- [x] Bibliography file present (Sao_Chim_Space.bib)
- [x] Author ORCID identifiers included
- [x] Zenodo DOI referenced: https://doi.org/10.5281/zenodo.22696778
- [x] No compilation errors or undefined references
- [x] **Ethics Declaration added** ⚡ NEW
- [x] **Funding statement added** ⚡ NEW

---

## Differences from Digital Discovery Submission

The JCAMD package differs from the original Digital Discovery submission (Submission_DD) in:

1. **Cross-reference handling:** All `xr` package cross-references replaced with inline text
2. **Cover letter:** Updated for JCAMD editor instead of Digital Discovery
3. **Journal scope:** Emphasis on computer-aided molecular design methods rather than data-driven discovery

**Scientific content is identical** - all results, validation, figures, tables, and conclusions are preserved.

---

## Contact Information

**Corresponding Author:**  
Myke Vital Sao Temgoua  
Department of Physics, Faculty of Science  
University of Yaoundé I  
P.O. Box 812, Yaoundé, Cameroon  
Email: myke-vital.sao@facsciences-uy1.cm

---

## Version Control

- **Original Source:** Project1_Chem_space_antimalarial_V7_CorrectedGrid/Submission_DD (V8)
- **JCAMD Adaptation Date:** September 28, 2026
- **Package Status:** Ready for submission
- **Canonical Version:** P1 V8 (enhanced with DEKOIS/MMV/redocking validation)

---

## Notes for Submission

1. Upload all PDF files: Main manuscript, Supporting Information, and Cover Letter
2. Graphics files are embedded in PDFs but also available separately if needed
3. All inline cross-reference text provides sufficient context for standalone reading
4. Supporting Information tables are referenced by number (S1, S2, etc.) consistently
5. Zenodo deposit contains all raw data and code for full reproducibility

**The package is complete and ready for JCAMD submission.**


---

## ⚡ Technical Check Revision (September 28, 2026)

Following the initial submission technical check, the following sections were added to the main manuscript:

### Added Sections (Page 16)

1. **Ethics Declaration**
   ```
   Not applicable. This is a purely computational study using publicly 
   available data and structures. No human participants, animal subjects, 
   or biological materials were involved.
   ```

2. **Funding**
   ```
   This research received no specific grant from any funding agency in 
   the public, commercial, or not-for-profit sectors. All computational 
   resources were provided by the authors' institutions.
   ```

3. **Competing Interests** (separated from previous "Notes" section)
   ```
   The authors declare no competing financial interest. This is a 
   computational, hypothesis-generating study; no experimental potency 
   is claimed.
   ```

### Impact on Document
- **Page count:** 15 → 16 pages
- **Scientific content:** Unchanged
- **Results/validation:** Unchanged
- **Only change:** Addition of required declaration sections

### Resubmission Status
✅ **Both technical check requirements addressed**  
✅ **Manuscript ready for resubmission**

See **REVISION_NOTE_TECHNICAL_CHECK.md** for detailed response to technical check.

---

**Package Status:** Ready for resubmission to JCAMD (Technical Check Revision Complete)
