# L3 Review Pass — P3 Manuscript (2026-07-31)

**Reviewer:** Kiro manuscript assistant (independent checker pass)  
**Date:** 2026-07-31  
**Manuscript:** `Paper3_Quantum_InspiredV2607.tex` (610 lines, post Phase-11 sync)  
**Authority data:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (v37), `p3_classical_benchmark_19849.csv`, `p3_qks_summary.txt`, `p3_h1_rrs_correlation_final.txt`

---

## Verdict

**0 CRITICAL open · 0 HIGH open · 3 MEDIUM noted (author-owned HOLDs)**  
All CRITICAL and HIGH findings were fixed during this review pass. Compile: 24 pages, 0 errors, 0 undefined citations, anti-AI = 0.

---

## Findings Fixed This Pass

### C1 — Algorithm 1: `StronglyEntanglingLayers` → `IQPEmbedding` [FIXED]
- **Location:** Lines 189, 192, 196, 197
- **Issue:** Methods text, algorithm caption, and algorithm body still used `StronglyEntanglingLayers` (old circuit design). V1 had corrected this to `IQPEmbedding`.
- **Evidence:** `p3_qks_summary.txt` confirms `IQPEmbedding`; BMAD_Q1 §3.4 confirms the correction.
- **Fix applied:** All three occurrences replaced with `IQPEmbedding`.

### C2 — Tab:qkernel: TA = 0.684, p = 0.312 [FIXED]
- **Location:** Line 359
- **Issue:** Table showed `target_alignment = 0.684` and `p = 0.312`. Canonical values from `p3_qks_summary.txt`: TA = 0.5432, p = 0.0878.
- **Evidence:** `p3_qks_summary.txt` line: `target_alignment 0.5432 ± 0.0177`; `Paired t-test quantum vs rbf: t=2.248, p=0.0878`.
- **Fix applied:** TA → 0.543, p → 0.088.

### C3 — Figure 1 caption: old 2×2 per-molecule design [FIXED]
- **Location:** Lines 288–293
- **Issue:** Caption described 2D structures (A/B) and individual persistence diagrams (C/D) — the old design. Current figure is a 3-panel population-scale (H0 KDE / H1 hexbin / H2 scatter) for all 19,849 molecules.
- **Fix applied:** Caption updated to describe H0 KDE (median 1.60 Å), H1 hexbin with exemplar markers (p̄=0.78/0.42 Å), H2 scatter (N=587, 3.0%).

### C4 — Results §4.5: QKS polypharmacology placeholder [FIXED]
- **Location:** Line 463
- **Issue:** Text said "A full benchmark using n=1000…is running on the HPC…per-fold results will be inserted once the run completes." This was resolved — canonical result is AUC 0.747 vs RBF 0.737.
- **Evidence:** `p3_qks_summary.txt`; BMAD_Q1 §3.9 polypharmacology section.
- **Fix applied:** Replaced with resolved result (AUC 0.747 vs RBF 0.737, 5-fold CV).

### C5 — Methods §2.6: "65856 molecules" in benchmark evaluation [FIXED]
- **Location:** Line 238
- **Issue:** "5-fold CV on all 65856 molecules" — the benchmark used 19,849 molecules, not 65,856.
- **Fix applied:** → "19849-molecule benchmark set".

### H1 — Discussion: "20 high-confidence polypharmacological leads" [FIXED]
- **Location:** Line 525
- **Issue:** Said "20" — correct value is 17 (polypharmacological leads) with 14 having complete RRS data. The correction was already in the Discussion at line 527 but not at line 525.
- **Fix applied:** → "17 polypharmacological leads…; of these, 14 carried complete RRS classifications".

### H2 — Discussion: Wesołowski bare-text citation [FIXED]
- **Location:** Line ~511
- **Issue:** `(Weso\l{}owski et al., 2025)` — bare text, not a LaTeX citation. The correct entry `\citep{jamali2026spectralanalysismolecularfeatures}` was added to the bib in a prior session.
- **Fix applied:** → `\citep{jamali2026spectralanalysismolecularfeatures}`.

---

## L1 Gate Check Results (19/19 PASS)

| Check | CSV/Source value | Manuscript value | Result |
|-------|-----------------|-----------------|--------|
| L001 ECFP4 AUC | 0.949 | 0.949 | ✅ PASS |
| L001 AP AUC | 0.941 | 0.941 | ✅ PASS |
| L001 BPF AUC | 0.939 | 0.939 | ✅ PASS |
| L001 FCFP4 AUC | 0.920 | 0.920 | ✅ PASS |
| L001 MACCS AUC | 0.904 | 0.904 | ✅ PASS |
| L001 PHCO AUC | 0.897 | 0.897 | ✅ PASS |
| L001 TFP AUC | 0.877 | 0.877 | ✅ PASS |
| L001 TNE AUC | 0.722 | 0.722 | ✅ PASS |
| L002 H1-RRS ρ | 0.3124 | 0.312 | ✅ PASS |
| L002 H1-RRS p | 0.005679 | 0.0057 | ✅ PASS |
| L002 H1-RRS n | 77 | 77 | ✅ PASS |
| L009 QKS TA | 0.5432 | 0.543 | ✅ PASS |
| L009 QKS p | 0.0878 | 0.088 | ✅ PASS |
| OLD 0.916 occurrences | — | 0 | ✅ PASS |
| StronglyEntangling | — | 0 | ✅ PASS |
| Placeholder 'will be inserted' | — | 0 | ✅ PASS |
| QKS poly 0.747 present | — | 3 | ✅ PASS |
| Fig1 3-panel caption | — | present | ✅ PASS |
| Methods 19849 benchmark set | — | present | ✅ PASS |

---

## Remaining HOLDs (author-owned, no code fix possible)

| Hold | Description | Action needed |
|------|-------------|---------------|
| H1 | ΔAUC footnote convention: mean−baseline +0.075 vs matched per-fold −0.017 | Author to choose convention and add footnote to Tables 1/3 |
| H5 | Zenodo DOI `10.5281/zenodo.19608875` still "reserved" | Publish deposit before submission |
| L6 | `q_cadd_2026` pages = 54321 placeholder | Verify at https://doi.org/10.1038/s41598-026-44978-4 |

---

## Compile Status
- Pages: 24
- Errors: 0
- Undefined citations: 0
- Anti-AI patterns: 0
- Figures: 8 (all files present in Graphics/)
