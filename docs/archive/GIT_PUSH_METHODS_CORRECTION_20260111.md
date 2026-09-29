# Git Push Summary: Methods Data Expansion Correction
**Date:** January 11, 2026, 20:48  
**Commit:** 129d8477d  
**Branch:** master → master

---

## Push Statistics

| Metric | Value |
|--------|-------|
| **Commit Hash** | 129d8477d |
| **Files Changed** | 6 files |
| **Insertions** | 281 lines |
| **Deletions** | 6 lines |
| **Transfer Size** | 124.57 KiB |
| **Transfer Speed** | 6.23 MiB/s |
| **Status** | ✅ Complete |

---

## Changes Pushed

### 1. **Methods Section Correction** (Main Manuscript)
**File:** `Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`

Updated "Chemical-space funnel" subsection with detailed expansion methodology from V4:

#### Cheese API Parameters
- Similarity threshold: Tanimoto 0.7
- Fingerprint: Morgan radius 2, 2048 bits
- Database: ZINC15 in-stock + ENAMINE-REAL
- Analogues: 100 per seed

#### STONED-SELFIES Parameters
- Variants: 100 per seed
- Mutation type: Single-character SELFIES mutations
- Alphabet size: 50

#### Quality Control
- PAINS-filtered
- Validated via RDKit and Open Babel
- Deduplicated by canonical SMILES
- **Result:** 65,856 unique molecules (94.1% Lipinski-compliant)

#### Citation Added
- `\cite{lzicar_cheese_2024}` for Cheese API

#### Bug Fix
- Removed redundant `\cite{Krenn2020}` from SELFIES mention (was causing mciteplus tracking error)

---

### 2. **Updated PDFs**
- `Cover_Letter_P1_V7.pdf` (template format, refined 20:20)
- `P1_V7_Integrated_Polypharmacology_RRS.pdf` (main, 25 pages, Methods corrected 20:46)
- `P1_V7_Integrated_Polypharmacology_RRS_SM.pdf` (17 pages)

---

### 3. **Documentation Added**
- `GIT_PUSH_SUMMARY_20260111.md` (previous push summary)

---

## Compilation Status

| Document | Pages | Errors | Status |
|----------|:-----:|:------:|:------:|
| **Main** | 25 | 0 | ✅ |
| **SM** | 17 | 0 | ✅ |
| **Cover Letter** | 2 | 0 | ✅ |

**Last Compilation:** 20:46 (Methods correction)

---

## Reference Source

**V4 Manuscript:** `Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Antimalarial_Candidates_African_NP_V2607.tex`

Extracted detailed expansion parameters from V4 Methods section to correct abbreviated description in V7.

---

## Commit Message

```
P1 V7: Methods data expansion correction from V4

Updated Methods section 'Chemical-space funnel' with detailed expansion methodology:
- Cheese API parameters: Tanimoto 0.7, Morgan FP r=2 2048 bits, ZINC15/ENAMINE-REAL
- STONED-SELFIES parameters: 100 variants, single-char mutations, alphabet size 50
- Added lzicar_cheese_2024 citation
- Specified: PAINS-filtered, validated, deduplicated → 65,856 unique (94.1% Lipinski)
- Removed redundant Krenn2020 citation (mciteplus tracking error)

Status: Main 25 pages, 0 errors (compiled 20:46)
Reference: Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript
```

---

## Repository

**GitHub:** https://github.com/NanaEngo/Malaria_codesV2

**Branch:** master (up to date with origin)

---

## Previous Pushes (Session)

1. **20:30** - Commit 7e98fc4be: Complete JCIM submission preparation (V7 promotion, validation, MPO/DiffDock, cover letter)
2. **20:48** - Commit 129d8477d: Methods data expansion correction from V4 ← **CURRENT**

---

## Next Steps

V7 manuscript is **READY FOR SUBMISSION** pending:

1. ✅ Main manuscript (25 pages, 0 errors)
2. ✅ SM (17 pages, 0 errors)
3. ✅ Cover letter (2 pages, template format)
4. ✅ Methods data expansion corrected
5. ⏳ ORCID iDs for 4 co-authors (Paragon Plus entry during submission)

---

**Status:** ✅ **ALL CHANGES PUSHED TO GITHUB**
