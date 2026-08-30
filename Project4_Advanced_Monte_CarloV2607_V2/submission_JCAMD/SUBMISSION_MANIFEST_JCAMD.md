# P4 JCAMD Submission Manifest

**Journal:** Journal of Computer-Aided Molecular Design (JCAMD)  
**Publisher:** Springer Nature  
**Submission Model:** Traditional subscription (NO APC)  
**Manuscript Directory:** `Project4_Advanced_Monte_CarloV2607_V2/manuscript/LaTeX/`  
**Status:** Ready for final author review  
**Date:** 2026-08-23

---

## Required Files

### Core Submission Package
- [x] **Main manuscript:** `P4_Pareto_MCTS_JCAMD.tex`
- [x] **Supporting Information:** `P4_Pareto_MCTS_JCAMD_SM.tex`
- [x] **Cover Letter:** `Cover_Letter_P4_JCAMD.tex` ✅ **COMPILED (149 KB, 1 page)**
- [x] **Bibliography:** `P4_Bibliography.bib`
- [x] **Figures:** `Graphics/` directory

### Supporting Materials
- [x] **Code repository:** https://github.com/NanaEngo/Malaria_codesV2
- [x] **Data deposit:** `Project4_Advanced_Monte_CarloV2607/results/benchmark_molecules_opt_v12/`
- [x] **Pareto artifacts:** `Project4_Advanced_Monte_CarloV2607/results/pareto/`
- [x] **Data Analysis Report:** `P4_DATA_ANALYSIS_REPORT.md`

---

## Cover Letter Status

✅ **Cover Letter Complete**
- Format: P1 V7 style (9pt, compact geometry, flushleft)
- Content: Enhanced JCAMD version with dual evaluation framework
- Compilation: Successful (149 KB PDF, 1 page)
- Key features:
  * Honest-negative scalar benchmark reporting
  * Dual evaluation framework (scalar + Pareto)
  * Clear evidence boundaries
  * Four suggested reviewers
  * Traditional subscription model statement

---

## Key Scientific Findings

### Scalar Benchmark (Honest-Negative)
- **Random:** 0.6724 ± 0.0056 (best)
- **MCTS:** 0.6649 ± 0.0068 (t₁₉ = -4.97, p = 0.000085)
- **GA:** 0.6453 ± 0.0124
- **Greedy:** 0.4278

### Pareto Analysis
- **Four non-dominated profiles**
- **Hypervolume:** 1.2366
- Trade-offs across potency, accessibility, resistance-informed similarity, polypharmacology

### Ablation Effects (2⁵ factorial)
- **ScafVAE:** +0.148
- **Pareto front:** +0.108
- **Large vocabulary:** +0.079

---

## Evidence Boundaries

**What is claimed:**
- Computational framework for multi-objective candidate analysis
- Transparent scalar optimization benchmark
- Pareto front geometry for decision support
- Chemistry-informed search policies

**What is NOT claimed:**
- Experimental IC₅₀/EC₅₀ values
- Confirmed biological resistance circumvention
- Measured polypharmacology activity
- Direct biological measurements

---

## Suggested Reviewers

1. **Dr. Jan H. Jensen** (University of Copenhagen)  
   Expertise: Graph-based genetic algorithms, Monte Carlo methods for chemical space

2. **Prof. Gisbert Schneider** (ETH Zurich)  
   Expertise: Generative molecular design, de novo drug discovery

3. **Dr. Ola Engkvist** (AstraZeneca / Chalmers University)  
   Expertise: Multi-objective optimization, AI-driven molecular design

4. **Prof. Artem Cherkasov** (University of British Columbia)  
   Expertise: Computer-aided drug design for neglected tropical diseases

---

## Pre-Submission Checklist

### Manuscript Files
- [ ] Rename main tex file to JCAMD-appropriate title
- [ ] Rename SM tex file to JCAMD-appropriate title
- [ ] Update manuscript formatting to JCAMD guidelines
- [ ] Verify all figures compile correctly
- [ ] Check all cross-references resolve
- [ ] Verify bibliography formatting

### Cover Letter
- [x] Created with P1 V7 formatting style
- [x] Compiled successfully to PDF
- [x] Honest-negative results clearly stated
- [x] Evidence boundaries explicit
- [x] Traditional subscription model stated
- [x] Four reviewers suggested

### Metadata
- [ ] Author affiliations verified
- [ ] Corresponding author email confirmed
- [ ] ORCID IDs collected
- [ ] Conflict of interest statement verified
- [ ] Funding acknowledgments checked

### Supplementary Materials
- [ ] Code repository URL verified live
- [ ] Data deposit location documented
- [ ] README files complete
- [ ] License files included (MIT)

### Final Checks
- [ ] All co-authors approved submission
- [ ] Institutional approval obtained (if required)
- [ ] Originality confirmed (not under review elsewhere)
- [ ] Reproducibility materials complete

---

## Next Actions

1. **Author review:** Final read-through of cover letter content
2. **Manuscript preparation:** Format main + SM files to JCAMD style
3. **Final compilation:** Generate submission-ready PDFs
4. **Metadata verification:** Confirm all author details
5. **Repository check:** Verify GitHub materials are public and complete
6. **Submission:** Upload via JCAMD editorial system

---

## Notes

- **NO APC:** JCAMD traditional subscription model saves ~$2,390 compared to JoC
- **Honest-negative emphasis:** Scalar benchmark shows MCTS < Random, reported transparently
- **Complementary value:** Pareto analysis provides decision-support despite scalar cost
- **Provenance:** Complete computational reproducibility via GitHub repository
- **V12 canonical:** Only the v12-activity benchmark is used in manuscript prose
