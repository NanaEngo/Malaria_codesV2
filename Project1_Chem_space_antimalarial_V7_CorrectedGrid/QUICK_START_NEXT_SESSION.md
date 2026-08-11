# P1 V7 — Quick Start Guide for Next Session

**Goal:** Complete pre-submission requirements and submit to JCIM  
**Time Required:** 2-3 hours  
**Status:** 3 critical actions remaining

---

## ⚡ TL;DR — What You Need to Do

1. **Add 5 ORCID iDs** to the manuscript (~15 min)
2. **Add funding statement** to the manuscript (~5 min)
3. **Review all PDFs** (main 25 p. + SM 13 p. + cover 2 p.) (~2 hours)
4. **Recompile and submit** to Paragon Plus (~30 min)

---

## 📋 Step-by-Step Instructions

### Step 1: Add ORCID iDs (15 minutes)

**Open:** `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`

**Find:** Lines 22-31 (author section)

**Add this line after EACH `\author{}` command:**
```latex
\orcid{XXXX-XXXX-XXXX-XXXX}
```

**Example (for first author):**
```latex
\author{Myke Vital Sao Temgoua}
\orcid{0000-0001-2345-6789}  % ← ADD THIS with real ORCID
\email{myke-vital.sao@facsciences-uy1.cm}
\affiliation{...}
```

**Find ORCIDs:** Go to https://orcid.org/ and search each author's name

**Authors needing ORCIDs:**
1. Myke Vital Sao Temgoua
2. Jean-Pierre Tchapet Njafa
3. Penabei Samafou
4. Wilfred Fon Mbacham
5. Serge Guy Nana Engo

**If author doesn't have ORCID:** Register free at https://orcid.org/register

---

### Step 2: Add Funding Statement (5 minutes)

**Open:** `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`

**Find:** The `\end{document}` line (very end of file)

**Add BEFORE `\end{document}`:**

**Option A — If funding was received:**
```latex
\acknowledgment
This work was supported by [Funding Agency Name] (Grant Number XXXXX to [PI Name]).
```

**Option B — If no funding:**
```latex
\acknowledgment
No external funding was received for this work.
```

---

### Step 3: Recompile Manuscript (5 minutes)

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript

# Compile main manuscript (3 passes + bibtex)
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
bibtex P1_V7_Integrated_Polypharmacology_RRS
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex
pdflatex P1_V7_Integrated_Polypharmacology_RRS.tex

# Check for errors (should show "0 errors")
grep -c "^!" P1_V7_Integrated_Polypharmacology_RRS.log

# Also compile SM for completeness
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
bibtex P1_V7_Integrated_Polypharmacology_RRS_SM
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
pdflatex P1_V7_Integrated_Polypharmacology_RRS_SM.tex
```

**Expected result:** 0 errors, ORCID iDs visible in PDF, acknowledgment section present

---

### Step 4: Review All PDFs (2 hours)

Open these 3 PDFs and read carefully:

1. **Main Manuscript** (25 pages)
   - `manuscript/P1_V7_Integrated_Polypharmacology_RRS.pdf`
   - Focus: Scientific accuracy, evidence boundaries, claims

2. **Supporting Information** (13 pages)
   - `manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.pdf`
   - Focus: All 12 sections present, tables formatted, figures clear

3. **Cover Letter** (2 pages)
   - `manuscript/Cover_Letter_P1_V7.pdf`
   - Focus: V7 enhancements accurately described

**Review Checklist:**

- [ ] ORCIDs appear correctly for all 5 authors
- [ ] Funding/acknowledgment section present
- [ ] Title accurate: "Target breadth and mutation resilience..."
- [ ] Abstract matches manuscript content
- [ ] All Vina scores labeled as kcal/mol (not ΔG)
- [ ] RRS clearly labeled as "docking-score ratios"
- [ ] No claims of "binding affinity" or "experimental activity"
- [ ] All 4 targets appropriately distinguished
- [ ] Validation limitations honestly reported
- [ ] All figures legible at publication size
- [ ] All tables properly formatted
- [ ] All cross-references resolve (no "??" marks)
- [ ] Cover letter claims supported by manuscript

**Full checklist:** See `PRE_SUBMISSION_INSTRUCTIONS.md` (Action 4)

---

### Step 5: Update Submission Package (5 minutes)

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

# Verify package
ls -lh submission_ACS_P1V7/*.pdf
```

---

### Step 6: Submit to Paragon Plus (30 minutes)

**Portal:** https://paragonplus.acs.org/

**Login:** Use your ACS credentials (or create account)

**Select Journal:** Journal of Chemical Information and Modeling (JCIM)

**Manuscript Type:** Article

**Upload Files (in order):**

1. Main manuscript: `submission_ACS_P1V7/P1_V7_Integrated_Polypharmacology_RRS.pdf`
2. Supporting Information: `submission_ACS_P1V7/P1_V7_Integrated_Polypharmacology_RRS_SM.pdf`
3. Cover letter: `submission_ACS_P1V7/Cover_Letter_P1_V7.pdf`
4. (Optional) TOC graphic: `manuscript/Graphics/p1_v7_toc_graphic.pdf`
5. (Optional) Source files: `submission_ACS_P1V7/Sao_Chim_Space.bib` and .tex files

**Metadata to Enter:**

- **Title:** Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis
- **Running Title:** Polypharmacology and mutation resilience in antimalarials
- **Keywords:** African natural products; antimalarial discovery; polypharmacology; resistance resilience; molecular docking; chemical space; PfDHFR; PfCRT
- **Corresponding Author:** Myke Vital Sao Temgoua
- **Email:** myke-vital.sao@facsciences-uy1.cm
- **ORCIDs:** [Added in Step 1]
- **Funding:** [Added in Step 2]

---

## 📁 All Key Files (Reference)

### To Edit
- `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex` — Add ORCIDs + funding

### To Review
- `manuscript/P1_V7_Integrated_Polypharmacology_RRS.pdf` — Main (25 p.)
- `manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.pdf` — SM (13 p.)
- `manuscript/Cover_Letter_P1_V7.pdf` — Cover letter (2 p.)

### Documentation (Read These!)
- `PRE_SUBMISSION_INSTRUCTIONS.md` — Detailed guide
- `PHASE3_STATUS_SUMMARY.md` — Current status
- `V7_PROMOTION_COMPLETE.md` — What's been done
- `submission_ACS_P1V7/SUBMISSION_MANIFEST_V7.md` — Submission guide

---

## ✅ Success Checklist

When you can check all these boxes, you're ready to submit:

- [ ] All 5 ORCID iDs added to manuscript
- [ ] Funding acknowledgment added to manuscript
- [ ] Manuscript recompiled with 0 errors
- [ ] ORCID iDs appear in compiled PDF
- [ ] Acknowledgment section appears in PDF
- [ ] Main manuscript reviewed (25 pages)
- [ ] SM reviewed (13 pages)
- [ ] Cover letter reviewed (2 pages)
- [ ] All PDFs copied to submission_ACS_P1V7/
- [ ] Ready to upload to Paragon Plus

---

## 🆘 Need Help?

**Questions about:**
- **This guide:** Read `PRE_SUBMISSION_INSTRUCTIONS.md` (more detailed)
- **ORCIDs:** https://orcid.org/help
- **ACS submission:** https://paragonplus.acs.org/help
- **JCIM guidelines:** https://pubs.acs.org/journal/jcisd8

**Technical issues:**
- LaTeX won't compile? Check `.log` file for errors
- Missing citations? Run `bibtex` again
- Cross-references broken? Compile 3 times

---

## ⏱️ Time Budget

| Task | Time | Cumulative |
|------|:----:|:----------:|
| Find 5 ORCIDs | 10 min | 10 min |
| Add ORCID lines | 5 min | 15 min |
| Add funding | 5 min | 20 min |
| Recompile | 5 min | 25 min |
| Review main | 60 min | 1h 25min |
| Review SM | 45 min | 2h 10min |
| Review cover letter | 10 min | 2h 20min |
| Update package | 5 min | 2h 25min |
| Submit to portal | 30 min | **2h 55min** |

**Total:** ~3 hours

---

## 🎯 The Goal

**End State:** Manuscript submitted to JCIM via Paragon Plus

**When:** When all 3 critical actions complete (ORCIDs, funding, review)

**Current Status:** V7 is technically complete and ready — just needs these final touches

---

**You've got this! The hard work is done — now just the admin tasks remain.**

**Good luck with your JCIM submission! 🚀**

---

**Last Updated:** 2026-01-11  
**Version:** 1.0  
**Prepared By:** Kiro AI
