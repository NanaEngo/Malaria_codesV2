# Submission Package Manifest
## P4 Pareto-MCTS Manuscript - Journal of Cheminformatics

**Generated:** 2026-08-18 21:08 UTC  
**Manuscript ID:** P4_Pareto_MCTS_JoC  
**Target Journal:** Journal of Cheminformatics (Springer/BMC)  
**Submission Type:** Original Research Article

---

## Package Contents

### 1. Main Manuscript
- **File:** `P4_Pareto_MCTS_JoC_refined.pdf`
- **Pages:** 14
- **Size:** 543 KB
- **Format:** PDF/A (LaTeX-generated)
- **Compile Status:** Clean (0 errors, 0 warnings)
- **Last Modified:** 2026-08-18

### 2. Supplementary Material
- **File:** `P4_Pareto_MCTS_JoC_SM.pdf`
- **Pages:** 4
- **Size:** 308 KB
- **Format:** PDF/A (LaTeX-generated)
- **Contents:**
  - S1: Hyperparameter screening details
  - S2: Diversity metrics (MDS, Tanimoto)
  - S3: Full-vocabulary benchmark
  - S4: Selection ablation
  - S5: Data availability details
  - S6: References
- **Last Modified:** 2026-08-18

### 3. Cover Letter
- **File:** `Cover_Letter_P4_JoC.pdf`
- **Pages:** 2
- **Size:** 84 KB
- **Format:** PDF/A (LaTeX-generated)
- **Contents:**
  - Submission statement
  - Research significance
  - Key findings summary
  - Data availability statement
  - Suggested reviewers
- **Last Modified:** 2026-08-18 (updated with corrected Greedy score)

### 4. LaTeX Source Files
All source files in `manuscript/LaTeX/`:

#### Main Files
- `P4_Pareto_MCTS_JoC_refined.tex` (53 KB) - Main manuscript source
- `P4_Pareto_MCTS_JoC_SM.tex` (15 KB) - Supplementary Material source
- `Cover_Letter_P4_JoC.tex` (3.6 KB) - Cover letter source
- `P4_Bibliography.bib` (15 KB) - Bibliography (36 entries)

#### Graphics (6 PDF figures)
All in `Graphics/` subdirectory:
- `benchmark_reward_bar.pdf` (22 KB) - Figure 1: Scalar benchmark bar plot
- `p4_evidence_overview.pdf` (25 KB) - Figure 2: Evidence overview
- `benchmark_efficiency.pdf` (18 KB) - Figure 3: Efficiency comparison
- `pareto_front.pdf` (22 KB) - Figure 4: Pareto front visualization
- `rrs_pns_profile.pdf` (38 KB) - Figure 5: RRS/PNS profiles
- `scaffold_diversity.pdf` (17 KB) - SM Figure: Diversity MDS

**Total Package Size:** ~1.0 MB (compiled PDFs + sources)

---

## Data Availability

All supporting data available at:
- **Repository:** https://github.com/NanaEngo/Malaria_codesV2
- **License:** MIT
- **Contents:**
  - 20-seed v12 scalar benchmark (`results/benchmark_molecules_opt_v12/`)
  - Pareto fronts and multi-objective comparison (`results/pareto/`)
  - Diversity metrics (`results/diversity/`)
  - Ablation studies (`results/ablation/`)
  - Analysis scripts (`scripts/`)

---

## Key Statistics (Verified against v12 data)

### Scalar Benchmark (Table 2)
| Method | Mean | Std | Status |
|--------|------|-----|--------|
| Random | 0.6724 | 0.0056 | ✓ |
| Greedy | 0.6676 | 0.0000 | ✓ (FIXED) |
| MCTS | 0.6649 | 0.0068 | ✓ |
| GA | 0.6453 | 0.0124 | ✓ |

### Statistical Tests
- MCTS vs Random: Δ = -0.0075, t₁₉ = -4.97, p = 0.000085 ✓
- 95% CI: [-0.0107, -0.0043] ✓

### Pareto Front
- Hypervolume: 1.2366 ✓
- Non-dominated solutions: 4 ✓

### Multi-Objective Comparison (Table 4)
- MCTS HV: 19.10 ✓ (v12 updated)
- C-metric: 0.867 ✓ (v12 updated)

---

## Quality Control Completed

### L1 - Analysis Ledger
- **Date:** 2026-08-18
- **Status:** PASS
- **Entries:** 14 (all traced to sources)
- **File:** `outputs/analysis/analysis-ledger.md`

### L3 - Adversarial Review
- **Date:** 2026-08-18
- **Status:** MINOR REVISION
- **Passes:** 7 independent reviews
- **Findings:** 3 CRITICAL + 5 HIGH + 8 MEDIUM + 4 LOW
- **Files:** `outputs/critical-reviews/review-*-20260818.md`
- **Summary:** `outputs/critical-reviews/L3-SUMMARY-20260818.md`

### CRITICAL Fixes Applied
All 3 CRITICAL items resolved via Option A (fix + rerun):
1. ✓ Greedy best-intermediate rule (0.6676 vs old 0.4278)
2. ✓ Fragment priors → heuristic (text corrected)
3. ✓ Multi-objective v12 rerun (Table 4 updated)

### HIGH Fixes Applied
All 5 addressable HIGH items fixed:
1. ✓ Hyperparameter language clarified
2. ✓ Computational-proxy disclosure added
3. ✓ Progressive widening range corrected
4. ✓ Vocabulary confound linked
5. ✓ Environment file reference removed

### L4 - Pre-Submission Audit
- **Date:** 2026-08-18
- **Status:** CLEARED FOR SUBMISSION
- **Gates:** 9/9 PASS
- **File:** `outputs/L4-PRE-SUBMISSION-AUDIT-20260818.md`

---

## Submission Checklist

### Required for Submission ✓
- [x] Main manuscript PDF
- [x] Supplementary Material PDF
- [x] Cover letter PDF
- [x] LaTeX source files
- [x] Bibliography file
- [x] All figure files (6 PDFs)
- [x] Data availability statement
- [x] Ethics declarations
- [x] Author contributions
- [x] Competing interests statement
- [x] Funding statement

### To Add During Online Submission
- [ ] ORCID IDs for all authors
- [ ] Author affiliations and contact details
- [ ] Keywords (5-7 recommended)
- [ ] Line numbers (if required by journal)
- [ ] Graphical abstract (optional for JoC)

### Post-Acceptance Requirements
- [ ] Camera-ready source files
- [ ] High-resolution figures (if requested)
- [ ] Data DOI (Zenodo/Figshare if requested)
- [ ] Copyright transfer agreement

---

## Suggested Keywords

1. Molecular design
2. Monte Carlo tree search
3. Multi-objective optimization
4. Pareto front
5. Antimalarial drug discovery
6. Fragment-based generation
7. Cheminformatics

---

## Suggested Reviewers

1. **Dr. Jan H. Jensen**
   - Expertise: Graph-based genetic algorithms, MCTS for chemical space
   - University of Copenhagen

2. **Prof. Gisbert Schneider**
   - Expertise: Generative molecular design
   - ETH Zurich

3. **Dr. Ola Engkvist**
   - Expertise: De novo design, multi-objective optimization
   - AstraZeneca / University of Gothenburg

---

## File Integrity

All files verified:
- ✓ PDFs compile from source
- ✓ All cross-references resolve
- ✓ All figures embedded correctly
- ✓ Bibliography complete (36 entries)
- ✓ No LaTeX errors or warnings
- ✓ Statistics match source data

**MD5 Checksums:**
```
P4_Pareto_MCTS_JoC_refined.pdf: (generate at submission)
P4_Pareto_MCTS_JoC_SM.pdf: (generate at submission)
Cover_Letter_P4_JoC.pdf: (generate at submission)
```

---

## Submission Instructions

### Journal of Cheminformatics Submission System
1. Visit: https://www.editorialmanager.com/jcheminf/
2. Create account or log in
3. Start new submission
4. Upload files in order:
   - Cover letter PDF
   - Main manuscript PDF
   - Supplementary Material PDF
   - Source files (.tex, .bib, figures) as ZIP
5. Complete metadata forms:
   - Title, abstract, keywords
   - Author details and ORCID IDs
   - Suggested reviewers
   - Ethics and declarations
6. Review and submit

### Expected Timeline
- **Submission:** 2026-08-18
- **Initial decision:** 4-8 weeks
- **Revision (if required):** 2-4 weeks
- **Final decision:** 2-4 weeks after revision
- **Publication:** 2-4 weeks after acceptance
- **Total:** 3-6 months estimated

---

## Contact Information

**Corresponding Author:**
- Name: Myke Vital Sao Temgoua
- Email: myke-vital.sao@facsciences-uy1.cm
- Institution: University of Yaoundé I
- Department: Physics, Faculty of Science

**Alternative Contact:**
(Add if available)

---

## Notes

1. **Greedy Score Update:** Cover letter and manuscript updated with corrected Greedy score (0.6676) after fixing best-intermediate tracking bug (CRITICAL-1).

2. **Multi-Objective Update:** Table 4 updated with v12 canonical data after rerunning multi-objective comparison (CRITICAL-3).

3. **Fragment Priors:** Manuscript corrected to "heuristic scaffold-informed" (CRITICAL-2).

4. **Data Version:** Manuscript uses canonical v12 benchmark data throughout.

5. **QMC Boundary:** Tier 2 DMC remains diagnostic; no publication-grade QMC energy claims made.

---

**Manifest prepared by:** Claude Sonnet 4.5  
**Date:** 2026-08-18  
**Audit status:** L4 CLEARED FOR SUBMISSION

---

END OF MANIFEST
