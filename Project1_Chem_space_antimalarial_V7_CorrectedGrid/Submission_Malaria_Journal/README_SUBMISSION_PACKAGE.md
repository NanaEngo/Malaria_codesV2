# Malaria Journal Submission Package — P1 V8 Antimalarial Polypharmacology

**Created:** 28 September 2026  
**Status:** Ready for submission  
**Package directory:** `Submission_Malaria_Journal/`

---

## Package Contents

### Main Files (Ready)
- ✅ `P1_Integrated_Polypharmacology_RRS_Main_MalJ.tex` — Main manuscript (18 pages)
- ✅ `P1_Integrated_Polypharmacology_RRS_Main_MalJ.pdf` — Compiled PDF (1.8 MB)
- ✅ `Cover_Letter_Malaria_Journal.tex` — Cover letter with APC waiver request (3 pages)
- ✅ `Cover_Letter_Malaria_Journal.pdf` — Compiled cover letter
- ✅ `Sao_Chim_Space.bib` — Bibliography file
- ✅ `Graphics/` — All figures (PDF format)
- ✅ `tables/` — All LaTeX table files

### Supporting Information (To Adapt)
- ⏳ `P1_Integrated_Polypharmacology_RRS_SM_JCAMD.tex` → adapt to `*_SM_MalJ.tex`
  - **Note:** Supporting Information does not require structured abstract or Abbreviations section
  - Minor adaptation needed (mainly updating cross-references to main manuscript)

### Documentation
- ✅ `STRATEGIC_RATIONALE.md` — Supervisor's recommendation analysis
- ✅ `ADAPTATION_CHECKLIST.md` — Format requirements checklist
- ✅ `adapt_manuscript_malaria_journal.py` — Automated adaptation script
- ✅ This README

---

## Key Adaptations Applied (Main Manuscript)

### 1. Structured Abstract ✅
Restructured from single-paragraph to four sections:
- **Background** (2 sentences: problem context + African NP opportunity)
- **Methods** (1 paragraph: workflow, 17-member cohort, RRS framework)
- **Results** (1 paragraph: score ranges, RRS classes, correlations, priority candidates)
- **Conclusions** (1 paragraph: hypothesis-generation, validation requirements, recommendations)

### 2. Abbreviations Section ✅
Added comprehensive abbreviations list after Keywords:
- ACSI, ADMET, AUC, CI, DEKOIS, MMV, MPO, MTX, PAINS, PDB, etc.
- All four *Plasmodium* targets (PfDHFR, PfCRT, PfClpP, PfATP4)
- Statistical and computational terms (PNS, QED, RRS, RMSD, ROC, etc.)

### 3. Introduction → Background ✅
Section title changed per Malaria Journal guidelines.
Content unchanged (rationale, African NP context, computational accessibility gap).

### 4. Expanded Conclusions ✅
Expanded from 1 brief paragraph to comprehensive 6-paragraph summary:
1. **Core findings** (target breadth + mutation resilience as complementary properties; 5 priority candidates)
2. **Target-specific design** (heterogeneous evidence quality; null-finding transparency; honest-negative PfCRT result)
3. **Computational efficiency** (99.3% cost reduction; 69.3% scaffold recovery; centroid trade-offs)
4. **Validation requirements** (biochemical assays, mutant panels, orthogonal binding, MD refinement; DEKOIS/retrospective constraints)
5. **African NP contribution** (92.6% novelty; no ACSI-RRS association; PNS correlation exploratory)
6. **Limitations and positioning** (scoring-function caveats; proxy cavities; small cohort; no IC₅₀ data; hypothesis-generation scope)

**Page count:** 18 pages (vs. 16 for JCAMD; increase due to expanded Conclusions)

### 5. Authors' Contributions ✅
Already present in JCAMD version; preserved unchanged.

### 6. Cross-References ✅
All inline manual cross-references preserved from JCAMD adaptation.
No dynamic `\Cref{SM-...}` references (submission-platform compatibility).

---

## Compilation Instructions

### Main Manuscript
```bash
cd Submission_Malaria_Journal/
pdflatex P1_Integrated_Polypharmacology_RRS_Main_MalJ.tex
bibtex P1_Integrated_Polypharmacology_RRS_Main_MalJ
pdflatex P1_Integrated_Polypharmacology_RRS_Main_MalJ.tex
pdflatex P1_Integrated_Polypharmacology_RRS_Main_MalJ.tex
```

**Expected output:** 18-page PDF, 0 errors, 1 overfull hbox (abstract line break, cosmetic)

### Cover Letter
```bash
pdflatex Cover_Letter_Malaria_Journal.tex
pdflatex Cover_Letter_Malaria_Journal.tex
```

**Expected output:** 3-page PDF, 0 errors

### Supporting Information (When Adapted)
```bash
pdflatex P1_Integrated_Polypharmacology_RRS_SM_MalJ.tex
pdflatex P1_Integrated_Polypharmacology_RRS_SM_MalJ.tex
```

---

## Malaria Journal Submission Requirements

### Format Compliance ✅
- [x] Structured abstract (Background/Methods/Results/Conclusions)
- [x] Abbreviations section after Keywords
- [x] Introduction renamed to Background
- [x] Expanded Conclusions (2-3 paragraphs → 6 paragraphs)
- [x] Authors' Contributions section
- [x] Ethics Declaration
- [x] Funding statement
- [x] Competing Interests statement
- [x] Data Availability statement with Zenodo DOI
- [x] Acknowledgments (AI tool disclosure)

### Content Requirements ✅
- [x] Original research article scope
- [x] Malaria drug discovery focus
- [x] African research capacity angle
- [x] Mutation resilience / resistance management
- [x] Honest-negative results (DEKOIS, PfCRT null signal)
- [x] Clear hypothesis-generation boundaries
- [x] Reproducibility via Zenodo deposit

### Submission Materials
**Ready:**
- Main manuscript PDF (18 pages)
- Cover letter PDF (3 pages) with APC waiver request
- All figures (Graphics/ directory)
- All tables (tables/ directory)
- Bibliography (.bib file)

**To Prepare:**
- Supporting Information PDF (adapt from JCAMD version)
- Individual figure files (if requested by journal)
- LaTeX source files (if requested)

---

## APC Waiver Request

**Status:** Included in cover letter  
**Eligibility:** Corresponding author in Cameroon (BioMed Central waiver country)  
**Justification:**
- No external funding available
- Institutional computational resources only
- Endemic-region research capacity focus
- Open-access dissemination to malaria-endemic countries

**Expected outcome:** Automatic approval per BioMed Central policy

---

## Strategic Rationale (Supervisor Recommendation)

**Why Malaria Journal after JCAMD/JCIM rejections?**

1. **Scope match:** Antimalarial discovery, resistance, African research capacity (unambiguous fit)
2. **Fast decision:** Median 9 days to first decision (vs. 30–60 days typical)
3. **Impact factor:** 3.7 (respectable, above many specialized computational journals)
4. **APC waiver:** $0 for Cameroon authors (vs. $2000–3000 typical)
5. **No method-novelty gate:** Focus on biological/public-health significance, not computational method innovation
6. **Honest-negative results welcomed:** Journal publishes hypothesis-generation studies with clear limitations

**Positioning:** After two desk rejections from method-focused journals (Digital Discovery, JCIM), Malaria Journal provides appropriate venue for hypothesis-generation study emphasizing **biological utility** over **computational novelty**.

---

## Verification Checklist

### Pre-Submission
- [x] Main manuscript compiles without errors
- [x] Cover letter compiles without errors
- [x] All figures present and referenced correctly
- [x] All tables present and load correctly
- [x] Bibliography resolves all citations
- [x] Zenodo DOI publicly accessible (10.5281/zenodo.22696778)
- [ ] Supporting Information adapted and compiled
- [ ] Final read-through by all authors
- [ ] Corresponding author information correct

### On Submission Platform
- [ ] Upload main manuscript PDF
- [ ] Upload Supporting Information PDF
- [ ] Upload cover letter PDF
- [ ] Upload individual figure files (if required)
- [ ] Select article type: Research
- [ ] Confirm APC waiver request
- [ ] Verify all author ORCID iDs
- [ ] Review and submit

---

## Key Differences from JCAMD Submission

| Feature | JCAMD V8 | Malaria Journal |
|---------|----------|-----------------|
| **Abstract format** | Single paragraph | Structured (B/M/R/C) |
| **Abbreviations** | Not required | Required section |
| **Introduction title** | Introduction | Background |
| **Conclusions length** | 1 paragraph | 6 paragraphs |
| **Page count** | 16 pages | 18 pages |
| **Cross-references** | Manual inline | Manual inline |
| **Target journal** | Comp. chem. methods | Malaria biology/discovery |
| **Method novelty** | Expected | Not required |
| **APC** | ~$2000 | $0 (waiver) |
| **Decision time** | 30–60 days | 9 days (median) |

---

## Contact Information

**Corresponding Author:**  
Myke Vital Sao Temgoua  
Department of Physics, Faculty of Science  
University of Yaoundé I, P.O. Box 812  
Yaoundé, Cameroon  
Email: myke-vital.sao@facsciences-uy1.cm  
ORCID: 0009-0004-5170-2309

---

## Version History

**2026-09-28:** Initial Malaria Journal package created
- Adapted main manuscript from JCAMD V8
- Created cover letter with APC waiver request
- Applied all format requirements (structured abstract, abbreviations, expanded conclusions)
- Verified compilation (18 pages, 0 errors)

---

## Next Actions

1. **Adapt Supporting Information** (minor: update cross-references to main manuscript)
2. **Final author review** (all co-authors read adapted manuscript)
3. **Decision:** Submit immediately OR monitor JCAMD outcome first
4. **If submitting:** Upload package to Malaria Journal submission portal

**Recommendation:** Based on supervisor's strong endorsement and fast decision timeline, consider submitting to Malaria Journal **in parallel** with JCAMD decision monitoring (if journal policies allow).

---

**End of README**
