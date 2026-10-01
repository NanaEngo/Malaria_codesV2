# Malaria Journal Adaptation Checklist

**Source:** JCAMD submission (P1 V8 with technical check revisions)  
**Target:** Malaria Journal submission  
**Estimated time:** 2-3 hours

---

## Required Changes

### 1. Abstract → Structured Format ⚡ CRITICAL

**Current:** Unstructured paragraph (250 words)

**Required:** Four subsections:
- **Background:** 2-3 sentences on malaria resistance problem + African NP opportunity
- **Methods:** Chemical-space funnel, target-anchored docking, RRS framework
- **Results:** Key numbers (65,856 molecules, 19,913 leads, 17-member cohort, RRS classes, correlations)
- **Conclusions:** Testable hypotheses, not experimental evidence

**Action:**
```latex
\begin{abstract}
\textbf{Background:} [2-3 sentences from current intro]

\textbf{Methods:} [3-4 sentences from current abstract methods]

\textbf{Results:} [4-5 sentences with key numbers]

\textbf{Conclusions:} [2-3 sentences on implications]
\end{abstract}
```

**Time:** 15 minutes

---

### 2. Add Abbreviations Section ⚡ REQUIRED

**Location:** After Conclusions, before Declarations

**Content:** All acronyms used in manuscript

```latex
\section*{Abbreviations}
\textbf{ACSI:} African-Chemotype Structural Index  
\textbf{ADMET:} Absorption, Distribution, Metabolism, Excretion, Toxicity  
\textbf{AUC:} Area Under the Curve  
\textbf{DEKOIS:} Demanding Evaluation Kits for Objective In Silico Screening  
\textbf{ECFP:} Extended-Connectivity Fingerprint  
\textbf{HBA:} Hydrogen Bond Acceptors  
\textbf{HBD:} Hydrogen Bond Donors  
\textbf{MD:} Molecular Dynamics  
\textbf{MMV:} Medicines for Malaria Venture  
\textbf{MPO:} Multi-Parameter Optimization  
\textbf{PAINS:} Pan-Assay Interference Compounds  
\textbf{PfATP4:} \textit{Plasmodium falciparum} P-type ATPase 4  
\textbf{PfClpP:} \textit{Plasmodium falciparum} Caseinolytic Protease P  
\textbf{PfCRT:} \textit{Plasmodium falciparum} Chloroquine Resistance Transporter  
\textbf{PfDHFR:} \textit{Plasmodium falciparum} Dihydrofolate Reductase  
\textbf{PNS:} Polypharmacology Network Similarity  
\textbf{QED:} Quantitative Estimate of Drug-likeness  
\textbf{RMSD:} Root Mean Square Deviation  
\textbf{ROC:} Receiver Operating Characteristic  
\textbf{RRS:} Resistance-Resilience Score  
\textbf{SMILES:} Simplified Molecular Input Line Entry System
```

**Time:** 10 minutes

---

### 3. Introduction → Background ⚡ SIMPLE

**Change:** Section title only

```latex
\section{Background}  % was \section{Introduction}
```

**Content:** Unchanged

**Time:** 1 minute

---

### 4. Expand Conclusions ⚡ MODERATE

**Current:** 1 paragraph (~100 words)

**Required:** 2-3 paragraphs with explicit implications

**Add:**
- Paragraph 2: Experimental validation pathway
- Paragraph 3: Broader implications for resistance management

**Example addition:**
```latex
The immediate experimental priorities are biochemical potency measurements 
against wild-type and mutant P. falciparum parasites, orthogonal binding 
validation, and molecular-dynamics refinement of the top-priority candidates. 
The workflow's computational efficiency (99.3% cost reduction) makes this 
systematic approach accessible to research groups with limited infrastructure, 
particularly relevant for endemic-region institutions where 94% of malaria 
cases occur.

More broadly, the separation of target breadth from mutation resilience 
provides a reusable template for hypothesis generation in resistance-challenged 
therapeutic areas. The per-target RRS framework, combined with explicit null 
controls and honest-negative reporting, demonstrates how computational 
hypotheses can be generated with transparent uncertainty quantification while 
maintaining clear boundaries between docking estimates and biological activity.
```

**Time:** 20 minutes

---

### 5. Update Cover Letter ⚡ CRITICAL

**Key elements:**
1. Emphasize malaria relevance
2. **Request APC waiver** (Cameroon eligibility)
3. Explain perfect fit with journal scope
4. Mention African natural products + resistance focus

**Template provided separately**

**Time:** 30 minutes

---

### 6. Check Declarations Section ⚡ VERIFY

**Already have from JCAMD revision:**
- ✅ Ethics Declaration
- ✅ Funding statement
- ✅ Competing Interests
- ✅ Data Availability (Zenodo)

**Add:**
- ⚡ **Authors' Contributions** section

**Example:**
```latex
\section*{Authors' Contributions}
MVST and SGNE designed the integrated study. MVST and J-PTN developed the 
chemical-space and docking analyses. PS and WFM contributed to target biology 
and resistance interpretation. All authors reviewed and approved the manuscript.
```

**Time:** 10 minutes

---

## What Stays Identical ✅

- All Methods content
- All Results content
- All Discussion content
- All figures and tables
- All Supporting Information
- All validation results
- All references (Vancouver format compatible)
- Zenodo data deposit

---

## Files to Create

1. **P1_Malaria_Journal_Main.tex** - Adapted main manuscript
2. **P1_Malaria_Journal_SM.tex** - Supporting Information (minimal changes)
3. **Cover_Letter_Malaria_Journal.tex** - New cover letter with APC waiver request
4. **README_MALARIA_JOURNAL.md** - Package documentation

---

## Pre-Submission Checklist

Before submitting to Malaria Journal, verify:

- [ ] Abstract has four subsections (Background/Methods/Results/Conclusions)
- [ ] Abbreviations section present and complete
- [ ] Introduction renamed to "Background"
- [ ] Conclusions expanded (2-3 paragraphs)
- [ ] Authors' Contributions section added
- [ ] Cover letter requests APC waiver
- [ ] All declarations present (Ethics, Funding, Competing Interests, Data Availability)
- [ ] Zenodo DOI referenced in Data Availability
- [ ] All figures and tables numbered correctly
- [ ] Supporting Information cross-references work
- [ ] Compilation successful (pdfLaTeX)
- [ ] Bibliography formatted (Vancouver/numbered style already correct)

---

## Timeline

| Task | Time | Cumulative |
|------|------|------------|
| Restructure abstract | 15 min | 15 min |
| Add abbreviations | 10 min | 25 min |
| Rename Introduction | 1 min | 26 min |
| Expand Conclusions | 20 min | 46 min |
| Add Authors' Contributions | 10 min | 56 min |
| Compile and verify | 15 min | 71 min |
| Write cover letter | 30 min | 101 min |
| Final checks | 15 min | **116 min (~2 hours)** |

---

## APC Waiver Request

**Key statement for cover letter:**

> "We respectfully request an Article Processing Charge (APC) waiver under 
> BioMed Central's policy for authors from low- and middle-income countries. 
> The corresponding author is affiliated with the University of Yaoundé I, 
> Cameroon, which qualifies for automatic waiver eligibility. All computational 
> work was conducted using institutional resources without external funding."

**Supporting documentation:** None required (automatic for Cameroon-based corresponding author)

---

## Expected Outcome

**Malaria Journal advantages:**
- ✅ Perfect scope match (resistance + African NP)
- ✅ Fast decision (median 9 days)
- ✅ Zero APC cost
- ✅ No method-novelty gate
- ✅ Respected venue (IF 3.7)

**Risk:** Minimal. Work is strong, venue is perfect fit.

**Next step after submission:** Median 9-day first decision (vs 4-6 weeks typical for JCAMD)

---

**Status:** Ready to implement  
**Complexity:** Low (mostly formatting)  
**Scientific changes:** Zero  
**Time investment:** ~2 hours  
**Strategic value:** High (unambiguous scope fit)
