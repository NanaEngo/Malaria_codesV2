# P1 V8 JCIM Resubmission — Final Checklist

**Date prepared**: 2026-09-10  
**Original manuscript ID**: ci-2026-00578g  
**Resubmission type**: Revision (will appear as new submission in system due to transfer-decline workflow)

---

## ✅ Core Submission Documents (all verified 2026-09-10)

| Document | Pages | Status | Notes |
|----------|-------|--------|-------|
| **Main manuscript** | 27 | ✅ Ready | `P1_Integrated_Polypharmacology_RRS_Main_V8.pdf` — 0 errors, 0 undefined refs |
| **Supporting Information** | 21 | ✅ Ready | `P1_Integrated_Polypharmacology_RRS_SM_V8.pdf` — 0 errors, 0 undefined refs |
| **Cover Letter** | 2 | ✅ Ready | `Cover_Letter_P1_V8.pdf` — addresses transfer decline, manuscript ID, 48h turnaround, JCIM commitment |
| **Response to Reviewers** | 7 | ✅ Ready | `Response_to_Reviewers_P1_V8.pdf` — all 18 points addressed, 0 errors |

---

## ✅ Reproducibility Package

**Location**: `zenodo_package_P1/` (staged, not yet uploaded)

**Contents** (verified in Response to Reviewers §R2.6):
- All 17 candidate SMILES and property tables
- Wild-type and mutant receptor PDB files (6 PfDHFR, 3 PfCRT, 2 PfClpP, 3 PfATP4)
- Grid configuration files (`.gpf` or coordinate records)
- Complete docking outputs (68 poses, RMSD < 2 Å except MTX)
- RRS calculation spreadsheet
- DEKOIS 2.0 benchmark results (two arms: MTX-retained, MTX-stripped)
- Retrospective control (5 approved antimalarials)
- Source code for all analysis scripts
- README with sha256 checksums

**DOI**: https://doi.org/10.5281/zenodo.22686176 (reserved, will be finalized after upload)

**License**: CC BY 4.0

**Action required before final submission**:
1. Upload `zenodo_package_P1/` contents to Zenodo
2. Verify DOI resolves correctly
3. Confirm sha256 checksums in README match uploaded files
4. Make repository public (currently staged locally)

---

## ✅ Reviewer Response Summary

| Reviewer | Comments | Status |
|----------|----------|--------|
| **R1** | 2 points | ✅ All addressed |
| **R2** | 16 points (9 major + 7 minor) | ✅ All addressed |

**Total**: 18/18 resolved

**Major additions in response**:
- DEKOIS 2.0 external validation (two-arm comparison, honest-negative result)
- Retrospective control using 5 approved antimalarials (honest-negative)
- PfCRT re-docking with corrected wild-type structure
- Complete physicochemical characterization (3 tables)
- Formal statistical multiplicity correction
- Zenodo reproducibility package with sha256 verification

---

## ✅ Cover Letter Key Points

The revised cover letter explicitly:

1. **References original manuscript ID**: ci-2026-00578g
2. **Declines transfer option**: Chooses to remain with JCIM with three reasons
3. **Emphasizes rapid response**: Completed revision in <48h because work was already in progress
4. **Points to comprehensive response**: All 18 comments resolved with manuscript evidence
5. **Highlights JCIM alignment**: Methodological rigor, cheminformatics readership, resistance/polypharmacology focus
6. **Thanks reviewers**: Acknowledges that feedback improved the manuscript

---

## ✅ Evidence Boundaries (maintained throughout)

The manuscript **does NOT claim**:
- Experimental binding affinities
- Confirmed simultaneous multi-target engagement
- Biological resistance circumvention
- Measured IC₅₀/EC₅₀ values
- Clinical relevance or therapeutic potential

The manuscript **does provide**:
- Four-target docking profiles for hypothesis generation
- Per-target RRS values (mutation-panel docking ratios)
- Exploratory cross-metric correlations
- Transparent validation (DEKOIS, MMV, redocking)
- Complete reproducibility records

---

## 🔄 Actions Required Before Upload

### 1. Zenodo Upload (author action)
- [ ] Upload `zenodo_package_P1/` to Zenodo (https://zenodo.org/deposit/22686176)
- [ ] Verify all checksums match
- [ ] Make repository public
- [ ] Confirm DOI resolves: https://doi.org/10.5281/zenodo.22686176

### 2. TOC Graphic (optional, can be submitted later)
The `Toc-Graphic/` folder contains:
- `TOC_BRIEF_FOR_AI.md` — complete prompt for ChatGPT/Gemini
- `p1_v8_toc_graphic_ACS.tiff` — Python-generated fallback (975×525 px, 300 dpi, RGB)
- `p1_v8_toc_graphic_ACS_1200dpi.tiff` — high-res version (3900×2100 px)
- `generate_toc_v8.py` — script to regenerate or modify

**Decision**: Use AI-generated version OR Python fallback OR submit later during production

### 3. JCIM Submission Portal
When the system asks "Is this a revision?", the answer will effectively be **NO** (new submission) because you declined the transfer. However:
- **Mention manuscript ID ci-2026-00578g in cover letter** ✅ (done)
- **Upload Response to Reviewers** as a separate file
- **Select "Article" as manuscript type**
- **Include all 4 PDFs**: Main, SM, Cover Letter, Response

---

## 📋 Final Verification (pre-upload)

Run this command to verify all files one last time:

```bash
cd Project1_Chem_space_antimalarial_V7_CorrectedGrid/submission_ACS_P1V8
for f in P1_Integrated_Polypharmacology_RRS_Main_V8 P1_Integrated_Polypharmacology_RRS_SM_V8 Cover_Letter_P1_V8 Response_to_Reviewers_P1_V8; do
  echo "=== ${f}.pdf ==="
  pdfinfo ${f}.pdf | grep Pages
  grep -c "Undefined" ${f}.log | xargs echo "Undefined refs:"
done
```

**Expected output**:
```
=== P1_Integrated_Polypharmacology_RRS_Main_V8.pdf ===
Pages:           27
Undefined refs: 0
=== P1_Integrated_Polypharmacology_RRS_SM_V8.pdf ===
Pages:           21
Undefined refs: 0
=== Cover_Letter_P1_V8.pdf ===
Pages:           2
Undefined refs: 0
=== Response_to_Reviewers_P1_V8.pdf ===
Pages:           7
Undefined refs: 0
```

✅ **All verified as of 2026-09-10**

---

## 🎯 Why This Revision Should Succeed

1. **Comprehensive validation**: DEKOIS, MMV, redocking, retrospective controls
2. **Honest reporting**: Two honest-negative results (DEKOIS near-chance, approved drugs don't recover resistance signatures)
3. **Transparent boundaries**: Clear distinction between computational hypotheses and biological claims
4. **Complete reproducibility**: Zenodo package with sha256 verification, CC BY 4.0 license
5. **Reviewer respect**: All 18 comments addressed with manuscript evidence, no deferrals
6. **Methodological rigor**: Statistical corrections, pipeline-null controls, multi-seed sensitivity
7. **JCIM alignment**: Methods-focused, cheminformatics audience, resistance mechanisms

---

## 📞 Contact

**Corresponding author**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**ORCID**: 0009-0004-5170-2309

---

**Document prepared by**: Kiro AI agent  
**Last updated**: 2026-09-10T18:18 UTC+01:00
