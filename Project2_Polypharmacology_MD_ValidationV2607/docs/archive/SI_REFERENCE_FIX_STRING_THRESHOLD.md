# P2 V2609C: STRING Threshold Sensitivity SI Reference Fix

**Date:** 17 September 2026  
**Status:** ✅ Complete  
**Issue:** Incomplete Supporting Information reference

---

## Problem Identified

**Main manuscript (line 443)** mentioned:
> "STRING threshold sensitivity (confidence cutoffs 400, 700, 900) showed PNS rank stability... — distinct from the PfCRT-centrality imputation sensitivity **(Supporting Information)**."

The reference was **incomplete** — it said "Supporting Information" but didn't cite a specific table/figure.

---

## Root Cause

1. **Data exists**: `results/string_threshold_sensitivity_20260829/` contains the analysis
2. **Table S7** (file `Table_S9_PNS_Imputation_Sensitivity.tex`) only showed **PfCRT centrality imputation** sensitivity
3. **STRING threshold** sensitivity (400/700/900) was **missing** from the SI tables
4. Main text cited the analysis but had no corresponding SI element

---

## Solution Implemented

### 1. **Main Manuscript Fix (Line 443)**

**Changed:**
```latex
(Supporting Information)
```

**To:**
```latex
(\cref{SM-tab:s7_pns_sensitivity})
```

✅ Now properly cross-references Table S7 in SI

---

### 2. **Table S7 Enhancement**

**File:** `Table_S9_PNS_Imputation_Sensitivity.tex`

**Added:**
- Updated caption to mention both sensitivity analyses
- Added **second sub-table** with STRING threshold data (400/700/900)
- Included Spearman ρ values and Top-5 Jaccard indices

**New structure:**
- **First sub-table**: PfCRT centrality imputation (original content, 5 rows)
- **Second sub-table**: STRING threshold sensitivity (3 pairwise comparisons)

**Data source:** `results/string_threshold_sensitivity_20260829/string_threshold_sensitivity_summary.json`

---

## Table S7 Content (Updated)

### PfCRT Centrality Imputation (STRING threshold 700)
| Imputation | C_PfCRT | Spearman ρ | Min PNS | Max PNS | n |
|---|---|---|---|---|---|
| Zero | 0.0000 | 0.9716 | 0.300 | 5.147 | 17 |
| One-half canonical | 0.0755 | 0.9975 | 0.674 | 5.573 | 17 |
| **Canonical network mean** | **0.1510** | **1.0000** | **1.047** | **6.000** | **17** |
| One-and-a-half canonical | 0.2265 | 0.9755 | 1.421 | 6.426 | 17 |
| Twice canonical | 0.3020 | 0.9632 | 1.795 | 6.853 | 17 |

### STRING Confidence Threshold (canonical PfCRT imputation)
| Comparison | n | Spearman ρ | Top-5 Jaccard |
|---|---|---|---|
| 400 vs 700 | 17 | **0.9975** | 1.000 |
| 700 vs 900 | 17 | 0.9681 | 0.667 |
| 400 vs 900 | 17 | 0.9632 | 0.667 |

---

## Verification

✅ **Main manuscript** now cites `\cref{SM-tab:s7_pns_sensitivity}`  
✅ **Table S7** now contains both analyses  
✅ **Data matches** JSON source file exactly  
✅ **Caption updated** to describe both sensitivity dimensions  

---

## Interpretation

**From the data:**

1. **PfCRT imputation sensitivity:** Rank correlation ranges 0.9632–1.0000
   - Most stable at ½× and 1× canonical values (ρ ≥ 0.9975)
   - Shows the PNS ranking depends on this imputed value

2. **STRING threshold sensitivity:** Rank correlation 0.9632–0.9975
   - Very stable between 400 and 700 (ρ = 0.9975, perfect Top-5 agreement)
   - Slightly less stable at 900 threshold
   - **Key finding**: Threshold choice doesn't alter ranking substantively

3. **Comparison**: Both sensitivities show similar ρ ranges (0.96–1.00), but they test different assumptions:
   - **PfCRT imputation**: Sensitivity to a **missing node** (no experimental PfCRT data)
   - **STRING threshold**: Sensitivity to **edge filtering** (network confidence cutoff)

---

## Files Modified

1. `V2609C/Polypharmacology_MD_Validation_V2609C.tex` (main manuscript)
   - Line 443: Added proper SI cross-reference

2. `V2609C/Table_S9_PNS_Imputation_Sensitivity.tex` (Table S7)
   - Updated caption
   - Added STRING threshold sensitivity sub-table
   - Added data source comment in header

---

## Next Steps

1. **Compile** to verify table layout and cross-reference
2. **Visual check**: Ensure two sub-tables are clearly separated
3. **Consistency**: Verify all ρ values match between main text and table
4. **Cross-check** with other SI references to ensure numbering consistency

---

**Author approval recommended** before compilation.
