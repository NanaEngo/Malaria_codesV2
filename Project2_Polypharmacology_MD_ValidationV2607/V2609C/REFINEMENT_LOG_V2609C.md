# P2 V2609C Manuscript Refinement Log (ACS JCIM Submission Audit)

**Date:** 12 September 2026  
**Target Journal:** Journal of Chemical Information and Modeling (JCIM)  
**Main Manuscript:** `Polypharmacology_MD_Validation_V2609C.tex`  
**Supplementary Material:** `Polypharmacology_MD_Validation_SM_V2609C.tex`  
**Bibliography:** `Project2_Polypharmacology_MD_Validation.bib`  

---

## 1. Executive Summary

A comprehensive multi-perspective audit (**Author, Reviewer, Editor**) was conducted on the canonical P2 V2609C manuscript package. All identified critical, major, and minor items were resolved and verified through clean PDF compilation (`pdflatex` + `bibtex`, exit code 0, 0 natbib undefined-citation warnings, 0 undefined reference warnings).

---

## 2. Refinement Table

| ID | Category | Severity | Section | Finding / Audit Criterion | Action Taken & Resolution |
|:---:|:---:|:---:|:---:|:---|:---|
| **F01** | Editor | **CRITICAL** | Title | Original title contained 18 words, exceeding the ACS 15-word limit. | **Applied:** Shortened title to 15 words: *"Estimand Divergence Between Static Docking and Molecular Dynamics as a Triage Filter for Antimalarial Leads"*, applied identically in main `\title{}`, header comment, SM title, and cover letter (corrected 15 Sept; earlier "12 words" was a miscount). |
| **F02** | Author | **CRITICAL** | Intro & BibTeX | 4 missing key references cited in Introduction line 136 (`moyo2023prioritised`, `african_np_underexplored`, `ramirez2018docking`, `ancajas2024np_sar`). | **Applied (12 Sept):** Appended 4 BibTeX entries. **SUPERSEDED 15 Sept (§4 addendum):** all 4 failed independent DOI resolution (false DOIs) — quarantined under INTEGRITY HOLD, DOIs stripped, dependent claims removed. |
| **F03** | Editor | **MINOR** | Data Availability | Data Availability section contained a generic Zenodo placeholder without the reserved DOI. | **Applied:** Explicitly included the reserved Zenodo DOI (`10.5281/zenodo.19608875`) and GitHub repository link. **Corrected 15 Sept:** reworded to reserved/future (prior present-tense "is archived" was inaccurate). |
| **F04** | Reviewer | **MAJOR** | Discussion §4.1 / §4.2 | Literature context needed explicit, quantitative contrast against recent African NP and docking review papers. | **Applied (12 Sept):** Added 2 comparative paragraphs. **REVERTED 15 Sept:** paragraphs depended on HOLD references (unverifiable 134-compound/<5% figures) — removed from manuscript until verified replacements land. |
| **F05** | Reviewer | **MAJOR** | Discussion §4.3 | Needed explicit bridge between P2 (physics-based MD stress testing) and P5 (out-of-distribution machine learning models). | **Applied:** Added the MOOD (Molecular Out-of-Distribution) physics-based relay paragraph, positioning explicit-solvent MD as the first-principles relay when ML model confidence drops on natural products. |
| **F06** | Author | **MAJOR** | Methods §2.1 | Incomplete sentence structure at line 161 due to legacy editing artifact. | **Applied:** Rewrote line 161 into clean, rigorous prose detailing candidate selection criteria (MPO $\ge 0.70$, SYBA $> 0$, SI $> 10$, multi-target coverage). |
| **F07** | Reviewer | **MAJOR** | Conclusion §5 | Defensive, self-canceling boilerplate ("computational record does not support calling RRS a validated prediction..."). | **Applied (12 Sept):** Rewrote Conclusion positive/authoritative. **RE-HEDGED 15 Sept (ADR-0002):** conclusion re-bound to manifest — gate pass for PP-01 only, no evolutionary-barrier claim, 7/8 always with Wilson CI 52.9–97.8% (n=8). |

---

## 3. Verification & Compliance Checklist

- [x] **Compilation:** `pdflatex` exit code 0; 0 `natbib` undefined citations; 0 LaTeX undefined references.
- [x] **Title Length:** 15 words ($\le 15$ words ACS limit), consistent across main/SM/cover.
- [x] **Abstract:** 102 words ($\le 200$ words JCIM limit).
- [x] **Keywords:** 9 structured keywords present.
- [x] **Graphical Abstract:** `\tocentry{}` present and self-contained with TikZ workflow diagram.
- [x] **CRediT Taxonomy:** All 9 standard CRediT roles explicitly mapped across 5 co-authors.
- [x] **Data Availability:** GitHub URL + Zenodo DOI (`10.5281/zenodo.19608875`) included with reserved/future wording (corrected 15 Sept).
- [x] **Provenance:** Frozen package `submission_ACS_P2V2609C/` refreshed from canonical sources 15 Sept (re-audit §5) and recompiled green. HPC sync status unverified from this workspace.

---

## 4. Addendum — Integrity audit 2026-09-15 (post-refinement findings)

Independent DOI resolution against `Project2_Polypharmacology_MD_Validation.bib`:

- **FAILED (false DOI, quarantined with INTEGRITY HOLD notes, DOIs removed):**
  `moyo2023prioritised`, `african_np_underexplored`, `ramirez2018docking`,
  `ancajas2024np_sar`, `sdmt_trends_parasitology_2026` (404),
  `sdmt2026trends` (DOI resolves to an unrelated paper),
  `temgoua2026chemrxiv` (malformed/unresolving preprint DOI),
  `genheden2015mmpbsa` (DOI 404; work itself is real — correct DOI still to confirm).
- **Verified OK:** `sadybekov2023computational`, `yu2022mutation_mmgbsa`,
  `kittelson2026docking`, `wei2024structure`, `ferreira2023docking`
  (key misnamed — entry is Gentile et al., content correct).
- **Metadata fixed:** `roux2024mmgbsa` pages/number corrected to 128(49):12027–12029.
- **Zenodo wording corrected** (main Data Availability + cover letter):
  reserved DOI, deposit concurrent with publication — prior present-tense
  "is archived" was inaccurate (DOI 404s; deposit pending).
- **Recompiled 2026-09-15** (fresh bibtex + 3 pdflatex passes): main and SM
  both exit 0 with 0 undefined citations/references. The earlier SM
  warnings were a stale `.bbl` + missing pass (build artifact).
- The F02 "100% citations resolved" claim above is **superseded** by this
   addendum for the listed keys. Package status remains
   `SUBMISSION_NOT_AUTHORIZED` — do not submit until each HOLD entry is
   replaced by a verified reference and the frozen
   `submission_ACS_P2V2609C/` copy is refreshed from canonical sources
   (main/SM/cover builds green at 0 undefined as of 15 Sept).

## 5. Addendum — Re-audit findings 4–9 (15 September 2026)

- **Findings 4–5 (title): CONFIRMED and fixed.** Main `\title{}` was 16
  words (not 12); header comment, SM title, and cover letter still
  carried the old 18-word title. New 15-word title
  (*"…Triage Filter for Antimalarial Leads"*) applied in all four
  places; F01 row and checklist corrected above.
- **Finding 6 (affiliation): REJECTED.** V2609C affiliation lines are
  identical to V2609B (`Department of Medical Imaging and Radiation
  Sciences, Université de Sherbrooke, Sherbrooke, QC, Canada`); the
  claimed DAR wording ("Faculty of Medicine and Health Sciences",
  "J1H 5N4") occurs nowhere in the repo or the DAR. No change made.
- **Finding 7 (STRING range): CONFIRMED and fixed.** PNS threshold rhos
  from `results/string_threshold_sensitivity_20260829/` are 0.9975 /
  0.9681 / 0.9632 (range 0.9632–0.9975); the 1.0000 was the centrality
  (not PNS) 700-vs-900 value. Main text now states all three pairs;
  Table S9 imputation range (0.9632–1.0000) verified correct and kept.
- **Finding 8 (DEKOIS CI): CONFIRMED and fixed.** No script computes the
  0.37–0.53 CI (V2609B carryover). CI removed; ROC-AUC 0.450 +
  EF5% = 0.00 kept.
- **Finding 9 + bib integrity: FIXED.** All 8 HOLD keys excised from the
  main text (stand-ins: `ferreira2023docking`,
  `polypharmacology_malaria_2026`, `roux2024mmgbsa`; upstream provenance
  via SM Table S16) and deleted from the `.bib` (removal notes kept as
  comments). Zero live cites remain. Rejected as already-clean: "other
  undefined keys" (0 undefined in main+SM logs, 0 bibtex warnings) and
  "bib filename mismatch" (`\bibliography` arg matches the `.bib`
  filename exactly).
- **Frozen package refreshed** from canonical sources and recompiled
  (main/SM/cover exit 0, 0 undefined). Provenance checklist item above
  is now satisfied for the file copy; HPC sync remains unverified from
  this workspace.
