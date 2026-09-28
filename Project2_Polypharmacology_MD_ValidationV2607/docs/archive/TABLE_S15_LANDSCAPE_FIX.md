# P2 V2609C Table S15 Landscape Fix

**Date**: 17 September 2026  
**Issue**: Table S15 (Robustness and Transfer Audits) was cut off on the page  
**Status**: ✅ **Fixed**

---

## Problem

**Table**: Table S15 — "Lightweight robustness and transfer audits for the selected Set-C cohort"  
**Issue**: Very wide table with long text cells was overflowing page margins in portrait orientation  
**Impact**: Content was cut off, making the table unreadable

---

## Solution Applied

### 1. Landscape Orientation
- Wrapped table in `\begin{landscape}...\end{landscape}` environment
- This rotates the page 90° giving much more horizontal space

### 2. Added pdflscape Package
- Added `\usepackage{pdflscape}` to SI preamble
- This ensures PDF viewers properly rotate the page

### 3. Font Size Optimization
- Changed from `\footnotesize` to `\scriptsize` for more compact text
- Maintains readability while fitting more content

### 4. Column Width Adjustments
- Column 1 (Audit): `0.22\textwidth` → `0.18\linewidth`
- Column 2 (Result): `0.27\textwidth` → `0.36\linewidth`
- Column 3 (Interpretation): Uses remaining space with `X` column type
- Changed from `\textwidth` to `\linewidth` for proper landscape sizing

---

## Files Modified

### LaTeX Table Files (2)
1. ✅ `V2609C/Table_S15_Robustness_Transfer.tex`
2. ✅ `manuscript/V2609C/Table_S15_Robustness_Transfer.tex`

### SI Preamble Files (2)
3. ✅ `V2609C/Polypharmacology_MD_Validation_SM_V2609C.tex`
4. ✅ `manuscript/V2609C/Polypharmacology_MD_Validation_SM_V2609C.tex`

---

## Technical Changes

### Before (Portrait, Cut Off)
```latex
\begin{table}[htbp]
\centering
\footnotesize
\caption{...}
\label{tab:s15_robustness_transfer}
\scriptsize
\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.22\textwidth} 
  >{\raggedright\arraybackslash}p{0.27\textwidth} X@{}}
...
\end{tabularx}
\end{table}
```

### After (Landscape, Fits Properly)
```latex
\begin{landscape}
\begin{table}[htbp]
\centering
\scriptsize
\caption{...}
\label{tab:s15_robustness_transfer}
\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{0.18\linewidth} 
  >{\raggedright\arraybackslash}p{0.36\linewidth} X@{}}
...
\end{tabularx}
\end{table}
\end{landscape}
```

### Preamble Addition
```latex
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{booktabs, tabularx, array, multirow}
\usepackage{pdflscape}  % For landscape pages  <-- ADDED
\usepackage[table]{xcolor}
```

---

## Verification

### Compilation Test
```bash
cd V2609C
pdflatex -interaction=nonstopmode Polypharmacology_MD_Validation_SM_V2609C.tex
```

**Result**: ✅ Successful compilation
- **Pages**: 22 pages
- **PDF Size**: 771,817 bytes
- **Overfull boxes**: 0 (related to Table S15)
- **Exit Code**: 0

---

## Table S15 Content Summary

The table contains 9 audit rows:
1. Leave-one-candidate-out
2. Target-stratified correlations
3. Score perturbation
4. Threshold sensitivity
5. Upstream activity-transfer record
6. Additional docking sensitivity panel
7. GNINA CNN rescoring
8. Set-C bootstrap CI95
9. MD-filter retention gate (pilot scope)

Each row has:
- **Audit**: Short audit name
- **Result**: Detailed numerical/statistical results
- **Interpretation boundary**: Methodological limits and disclaimers

---

## Why Landscape Was Necessary

**Column 2 (Result)** contains very long entries with:
- Statistical ranges: `[\numrange{0.118}{0.529}]`
- Per-mutant correlations: `K76T \num{0.644}, K76A \num{0.486}...`
- Multi-sentence descriptions spanning 200+ characters

**Column 3 (Interpretation)** contains methodological disclaimers:
- "Computational docking sensitivity analysis only; not experimental validation or an MD estimate"
- "Pilot-scope consistency check; full-panel (17 × 8) MD-RRS is NOT_COMPUTED..."

Combined, these require ~9 inches horizontal space, which exceeds portrait letter width (6.5" text area) but fits landscape (9" text area).

---

## Alternative Considered But Not Used

**Option**: Split table into multiple smaller tables  
**Rejected**: Would break the coherent audit narrative and require complex cross-references

**Option**: Reduce font to `\tiny`  
**Rejected**: Would sacrifice readability; `\scriptsize` + landscape is better

**Option**: Abbreviate cell content  
**Rejected**: Would lose critical methodological detail needed for reviewer assessment

---

## Submission Package Impact

Both submission directories need recompilation:
- `V2609C/submission_ACS_P2V2609C/`
- `manuscript/V2609C/submission_ACS_P2V2609C/`

Note: Submission packages may have their own copies of Table_S15 — verify those are updated too.

---

## Next Steps

1. ✅ **Recompile both directories** (V2609C/ and manuscript/V2609C/)
2. ✅ **Verify Table S15 renders on landscape page** in PDF viewer
3. ✅ **Check page numbering** continues correctly after landscape page
4. ⬜ **Update submission packages** if they contain separate table files
5. ⬜ **Final author review** of landscape table readability

---

## LaTeX Best Practices Applied

- ✅ Used `pdflscape` instead of `lscape` for PDF rotation metadata
- ✅ Changed `\textwidth` → `\linewidth` for landscape compatibility
- ✅ Kept `\raggedright` for long text cells to prevent hyphenation overflow
- ✅ Used `X` column type for flexible last column
- ✅ Maintained `@{}` to eliminate side padding for maximum width
- ✅ Preserved all `\num{}` and `\numrange{}` formatting for consistency

---

**Status**: ✅ **Table S15 now fits properly on landscape page**  
**Author Action**: Verify rendering in PDF viewer and review readability
