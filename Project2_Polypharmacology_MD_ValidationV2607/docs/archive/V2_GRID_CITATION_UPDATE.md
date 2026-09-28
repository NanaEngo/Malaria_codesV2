# P2 V2609C: V2 Grid Citation Update

**Date:** 17 September 2026  
**Status:** ✅ Complete  
**Target:** P2 V2609C manuscript for JCIM submission

## Issue Identified

The P2 V2609C manuscript mentioned "V2 grids" and "corrected V2 binding-site coordinates" **three times** without:
1. Citing the source (P1/Temgoua2026)
2. Explaining what "V2" means
3. Making the dependency on P1 transparent

This posed risks for:
- **Reproducibility**: Readers couldn't understand V2 origin
- **Transparency**: Critical PfCRT K76→LYS correction not referenced
- **Review**: Undefined terminology would be flagged

## Solution Implemented

Added `\citep{Temgoua2026}` citation at **three strategic locations**:

### 1. Main Manuscript - Docking Protocol Assessment (Line 209)

**Added:**
```latex
against grids centered on the corrected V2 binding-site coordinates~\citep{Temgoua2026}
```

**Plus explanatory sentence:**
```latex
The V2 grid specification represents the post-review refinement from the 
companion study, including the critical PfCRT K76→LYS restoration for 
wild-type reference state and P2Rank-validated binding-site centers.
```

### 2. Main Manuscript - RRS Formula Section (Line 229)

**Added:**
```latex
matching the audited V2 configuration files~\citep{Temgoua2026}.
```

### 3. Table S1 - Docking Validation (Table_S0_Docking_Validation.tex)

**Added:**
```latex
Values are from corrected parent-study benchmarks using V2 grids~\citep{Temgoua2026}.
```

## What V2 Grids Represent

From P1 (Temgoua2026):
- **V2** = post-reviewer-correction grid coordinates (P1 Response to Reviewers R2.3)
- **Critical correction**: PfCRT 6UKJ is 7G8 isoform (K76T); residue 76 restored to **LYS** for 3D7-like wild-type
- **Grid center**: `(152.99, 151.042, 159.379)` with 25 Å dimensions
- **Validation**: P2Rank pocket prediction confirms cavity-anchored placement
- **Provenance**: Complete grid coordinates documented in P1 Methods section

## Citation Key Details

**BibTeX entry:** `Temgoua2026`

```bibtex
@Article{Temgoua2026,
  author    = {Temgoua, Myke Vital Sao and Njafa, Jean-Pierre Tchapet and 
               Samafou, Penabei and Mbacham, Wilfred Fon and Engo, Serge Guy Nana},
  title     = {Target breadth and mutation resilience in African-natural-product-inspired 
               antimalarial chemotypes: a computational analysis},
  year      = {2026},
  month     = Sept,
  doi       = {10.26434/chemrxiv.15006437/v2},
  publisher = {American Chemical Society (ACS)},
}
```

## Files Modified

1. `manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex` (main manuscript)
   - Line ~209: Added citation + explanatory text in "Docking protocol assessment"
   - Line ~229: Added citation in "RRS definition" section

2. `manuscript/V2609C/Table_S0_Docking_Validation.tex` (SI Table S1)
   - Line 10: Added citation in table caption

## Verification

✅ All three V2 grid mentions now cite `Temgoua2026`  
✅ First mention includes explanatory context (PfCRT correction, P2Rank validation)  
✅ Citation key exists in bibliography (`Project2_Polypharmacology_MD_Validation.bib`)  
✅ No compilation errors expected (standard `\citep{}` command)

## Next Steps

1. **Compile manuscript** to verify citation appears correctly in superscript
2. **Check bibliography** to ensure Temgoua2026 appears in references
3. **Cross-check with P1 V8** to ensure grid coordinates match exactly if needed
4. **Update cover letter** if necessary to acknowledge companion study relationship

## Independence Statement

The manuscript already includes:
- Table S16: "Upstream workflow context" documenting shared provenance
- Clear statement: "not an independent validation set"
- Separate emphasis: P2 tests **estimand divergence** (docking vs MD), not P1 validation

The citation makes this transparent to readers without claiming independence.

---

**Author approval required** before next compilation/submission.
