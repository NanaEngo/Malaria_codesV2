# P1 V7 — Pre-Submission Instructions

**Status:** Phase 1 (Document Updates) ✅ COMPLETE  
**Current Phase:** Phase 3 (Pre-Submission Requirements) ⚠️ IN PROGRESS  
**Estimated Time to Submission-Ready:** 2-3 hours

---

## ✅ Completed Actions (Phase 1)

1. ✅ V7 promoted to canonical JCIM submission version
2. ✅ AGENTS.md updated (header + P1 section)
3. ✅ Submission package created (`submission_ACS_P1V7/`)
4. ✅ All documentation created (promotion plan, summary, manifest)
5. ✅ Compilation verified: Main 25 pages + SM 13 pages, 0 errors
6. ✅ Cover letter draft created: `manuscript/Cover_Letter_P1_V7.tex`

---

## ⚠️ Required Pre-Submission Actions

### Action 1: Add ORCID iDs (Priority 1) ⏰ ~15 minutes

**File to Edit:** `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`

**Location:** Lines 22-31 (author block)

**Current Code:**
```latex
\author{Myke Vital Sao Temgoua}
\email{myke-vital.sao@facsciences-uy1.cm}
\affiliation{Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}
\author{Jean-Pierre Tchapet Njafa}
\affiliation{Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}
\author{Penabei Samafou}
\affiliation{Department of Medical Imaging and Radiation Sciences, Faculty of Medicine and Health Sciences, Université de Sherbrooke, Sherbrooke, QC J1H 5N4, Canada}
\author{Wilfred Fon Mbacham}
\affiliation{Department of Biochemistry, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}
\author{Serge Guy Nana Engo}
\affiliation{Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}
```

**Required Code (Add `\orcid{}` after each author):**
```latex
\author{Myke Vital Sao Temgoua}
\orcid{XXXX-XXXX-XXXX-XXXX}  % ← ADD THIS LINE with actual ORCID
\email{myke-vital.sao@facsciences-uy1.cm}
\affiliation{Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}

\author{Jean-Pierre Tchapet Njafa}
\orcid{XXXX-XXXX-XXXX-XXXX}  % ← ADD THIS LINE with actual ORCID
\affiliation{Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}

\author{Penabei Samafou}
\orcid{XXXX-XXXX-XXXX-XXXX}  % ← ADD THIS LINE with actual ORCID
\affiliation{Department of Medical Imaging and Radiation Sciences, Faculty of Medicine and Health Sciences, Université de Sherbrooke, Sherbrooke, QC J1H 5N4, Canada}

\author{Wilfred Fon Mbacham}
\orcid{XXXX-XXXX-XXXX-XXXX}  % ← ADD THIS LINE with actual ORCID
\affiliation{Department of Biochemistry, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}

\author{Serge Guy Nana Engo}
\orcid{XXXX-XXXX-XXXX-XXXX}  % ← ADD THIS LINE with actual ORCID
\affiliation{Department of Physics, Faculty of Science, University of Yaoundé I, P.O. Box 812, Yaoundé, Cameroon}
```

**How to Find ORCID iDs:**
- Go to https://orcid.org/
- Search for each author by name
- Copy their 16-digit ORCID (format: XXXX-XXXX-XXXX-XXXX)
- If an author doesn't have an ORCID, they should register for free at https://orcid.org/register

**After Adding:**
1. Save the file
2. Recompile: `cd manuscript && pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex`
3. Verify 0 errors in compilation log

---

### Action 2: Add Funding Acknowledgment (Priority 1) ⏰ ~5 minutes

**File to Edit:** `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`

**Location:** After the last section (before `\end{document}`)

**Option A — If Funding Was Received:**
```latex
\acknowledgment
This work was supported by [Grant Agency Name] (Grant Number XXXXX to [PI Name]). [Add additional funding sources if applicable, separated by semicolons.]
```

**Option B — If No Funding Was Received:**
```latex
\acknowledgment
No external funding was received for this work.
```

**Placement:**
- Add immediately before the `\end{document}` line
- Typically placed after References section (ACS style handles placement automatically)

**After Adding:**
1. Save the file
2. Recompile: `cd manuscript && pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex`
3. Verify the acknowledgment appears correctly in the PDF

---

### Action 3: Review and Compile Cover Letter (Priority 2) ⏰ ~10 minutes

**File:** `manuscript/Cover_Letter_P1_V7.tex`

**Status:** ✅ Draft created (comprehensive version highlighting V7 enhancements)

**Actions Required:**
1. **Read the cover letter carefully:**
   ```bash
   cd manuscript
   pdflatex Cover_Letter_P1_V7.tex
   # Opens: Cover_Letter_P1_V7.pdf
   ```

2. **Verify Content:**
   - Title matches manuscript: "Target breadth and mutation resilience..." ✅
   - Journal name: Journal of Chemical Information and Modeling ✅
   - V7 enhancements highlighted:
     - Validation documentation (DEKOIS, MMV, redocking) ✅
     - Physicochemical characterization ✅
     - Methodological rigor (grid specs, efficiency) ✅
   - Evidence boundaries clearly stated ✅
   - Repository URL correct ✅
   - Signatory: Serge Guy Nana Engo ✅

3. **Optional Edits:**
   - Adjust emphasis if desired
   - Add co-author institutional statement if needed
   - Modify signatory if different from Serge Guy Nana Engo

4. **Final Compilation:**
   ```bash
   pdflatex Cover_Letter_P1_V7.tex
   # Verify: Cover_Letter_P1_V7.pdf compiles cleanly
   ```

---

### Action 4: Final Author Review (Priority 3) ⏰ ~2 hours

**Materials to Review:**

1. **Main Manuscript (25 pages)**
   - File: `manuscript/P1_V7_Integrated_Polypharmacology_RRS.pdf`
   - Focus areas:
     - Abstract clarity and accuracy
     - Introduction flow and motivation
     - Methods completeness (grid specs, RRS calculation, validation)
     - Results scientific narrative quality
     - Discussion evidence boundaries and interpretation
     - All figures and tables formatted correctly
     - All cross-references resolve (main ↔ SM)

2. **Supporting Information (13 pages)**
   - File: `manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.pdf`
   - Focus areas:
     - All 12 sections present (S1-S12)
     - All 9 tables formatted correctly
     - Section S11 validation documentation complete
     - All main text cross-references resolve correctly
     - All figure quality adequate (300+ DPI)

3. **Cover Letter (2 pages)**
   - File: `manuscript/Cover_Letter_P1_V7.pdf`
   - Verify all key claims supported by manuscript content

**Review Checklist:**

- [ ] Title and abstract accurately reflect manuscript scope
- [ ] No claims beyond computational evidence boundaries
- [ ] All docking scores labeled as kcal/mol (not ΔG, not free energy)
- [ ] RRS clearly labeled as docking-score ratios, not resistance phenotypes
- [ ] All 4 targets clearly distinguished by evidence type
- [ ] Validation limitations honestly reported
- [ ] All figures legible at publication size
- [ ] All tables properly formatted with captions
- [ ] All equations properly formatted and referenced
- [ ] All cross-references resolve (no "??" marks)
- [ ] Bibliography complete and properly formatted
- [ ] No undefined citations
- [ ] Acknowledgment section present
- [ ] ORCID iDs present for all 5 authors
- [ ] Author affiliations and emails correct

---

## Post-Review: Final Quality Checks

### Step 1: Recompile All Documents

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript

# Main manuscript (3 passes + bibtex)
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
bibtex P1_V7_Integrated_Polypharmacology_RRS
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex

# Supporting Information (3 passes + bibtex)
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
bibtex P1_V7_Integrated_Polypharmacology_RRS_SM
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex

# Cover letter (2 passes)
pdflatex Cover_Letter_P1_V7.tex
pdflatex Cover_Letter_P1_V7.tex
```

### Step 2: Verify Zero Errors

```bash
# Check main manuscript log
grep -i "error\|undefined\|warning" P1_V7_Integrated_Polypharmacology_RRS.log

# Check SM log
grep -i "error\|undefined\|warning" P1_V7_Integrated_Polypharmacology_RRS_SM.log

# Expected output: Only harmless warnings (overfull/underfull boxes), no errors
```

### Step 3: Update Submission Package

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project1_Chem_space_antimalarial_V7_CorrectedGrid

# Copy updated files to submission package
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS.pdf submission_ACS_P1V7/
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.pdf submission_ACS_P1V7/
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS.aux submission_ACS_P1V7/
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS.bbl submission_ACS_P1V7/
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.aux submission_ACS_P1V7/
cp manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.bbl submission_ACS_P1V7/
cp manuscript/Cover_Letter_P1_V7.pdf submission_ACS_P1V7/

# Verify package contents
ls -lh submission_ACS_P1V7/*.pdf
```

### Step 4: Figure Quality Check

```bash
# Check all figure resolutions
cd manuscript/Graphics

# For PNG files (should be 300+ DPI)
file p1_v7_toc_graphic.pdf  # Check if it's actually PDF or needs conversion
identify -verbose *.png 2>/dev/null | grep -i resolution

# All figures should be:
# - PDF format: vector (resolution-independent) OR
# - PNG/TIFF format: ≥300 DPI
```

---

## Submission Procedure

### When All Pre-Submission Actions Complete:

**Submission Portal:** https://paragonplus.acs.org/

**Journal:** Journal of Chemical Information and Modeling (JCIM)

**Manuscript Type:** Article

### Upload Order:

1. **Main Manuscript PDF** (`P1_V7_Integrated_Polypharmacology_RRS.pdf` — 25 pages)
2. **Supporting Information PDF** (`P1_V7_Integrated_Polypharmacology_RRS_SM.pdf` — 13 pages)
3. **Cover Letter PDF** (`Cover_Letter_P1_V7.pdf` — 2 pages)
4. **TOC Graphic** (if required separately: `Graphics/p1_v7_toc_graphic.pdf`)
5. **Source Files** (optional but recommended):
   - `Sao_Chim_Space.bib` (bibliography)
   - LaTeX source files (`.tex`, `.bbl`, `.aux`)

### Metadata Entry:

- **Title:** Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis
- **Running Title:** Polypharmacology and mutation resilience in antimalarials
- **Keywords:** African natural products; antimalarial discovery; polypharmacology; resistance resilience; molecular docking; chemical space; PfDHFR; PfCRT
- **Corresponding Author:** Myke Vital Sao Temgoua (myke-vital.sao@facsciences-uy1.cm)
- **ORCID iDs:** [Added in Action 1]
- **Funding:** [Added in Action 2]

---

## Success Criteria — Submission Readiness

| Criterion | Target | Status |
|-----------|:------:|:------:|
| V7 promoted to canonical | Yes | ✅ |
| AGENTS.md updated | Yes | ✅ |
| Submission package created | Yes | ✅ |
| Main text compiles cleanly | 0 errors | ✅ |
| SM compiles cleanly | 0 errors | ✅ |
| All cross-refs resolve | Yes | ✅ |
| Documentation complete | Yes | ✅ |
| Cover letter created | Yes | ✅ |
| **ORCIDs added** | **Yes** | **⚠️ TODO** |
| **Funding added** | **Yes** | **⚠️ TODO** |
| **Cover letter compiled** | **Yes** | **⚠️ TODO** |
| **Final author review** | **Yes** | **⚠️ TODO** |

**Current Status:** ⚠️ **4 pre-submission actions remaining** (estimated 2-3 hours)

---

## Quick Start — Next Session

```bash
# 1. Navigate to manuscript directory
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript

# 2. Open main manuscript in text editor
# Add ORCID iDs after each \author{} line (see Action 1 above)
# Add \acknowledgment section before \end{document} (see Action 2 above)

# 3. Compile main manuscript
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
bibtex P1_V7_Integrated_Polypharmacology_RRS
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex

# 4. Compile cover letter
pdflatex Cover_Letter_P1_V7.tex

# 5. Review all PDFs
# Open P1_V7_Integrated_Polypharmacology_RRS.pdf (main)
# Open P1_V7_Integrated_Polypharmacology_RRS_SM.pdf (SM)
# Open Cover_Letter_P1_V7.pdf (cover letter)

# 6. When satisfied, update submission package
cd ..
cp manuscript/*.pdf submission_ACS_P1V7/
cp manuscript/*.aux submission_ACS_P1V7/
cp manuscript/*.bbl submission_ACS_P1V7/
```

---

## Contact and Support

**Manuscript Prepared By:** Kiro AI (Enhancement Passes 1 & 2, Promotion, January 11, 2026)

**Version History:**
- Enhancement Pass 1 (V4 integration): `P1_V7_FINAL_COMPLETION.md`
- Enhancement Pass 2 (V5 integration): `P1_V7_V5_INTEGRATION_COMPLETED.md`
- Promotion (V6 → V7): `P1_V7_PROMOTION_COMPLETE.md`

**Project Tracking:** `project-tracking.md`

**Data Authority:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (P1-P3)

**Repository:** https://github.com/NanaEngo/Malaria_codesV2

---

**Document Status:** ✅ Complete and ready for user action  
**Last Updated:** 2026-01-11  
**Version:** 1.0
