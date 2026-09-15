# External Cross-References Fix — P3 Response Document

**Issue Identified:** 15 September 2026  
**Issue Resolved:** 15 September 2026  
**Status:** ✅ Fixed

---

## Problem

The P3 Response to Reviewers document (`Response_to_Reviewers_P3_V2609.tex`) had external cross-references to the main manuscript and SI that were showing as "undefined" during compilation.

**Symptoms:**
- LaTeX warnings: `Reference 'M-sec:intro' on page X undefined`
- 7+ undefined reference warnings during compilation
- Cross-references appeared as "??" in the compiled PDF

---

## Root Cause

The Response document used `\Cref{M-sec:...}` commands to link to sections in the main manuscript, but the main manuscript (`Paper3_Quantum_InspiredV2609.tex`) **did not have `\label{}` commands** on those sections.

**Comparison with P1:**
- **P1 manuscript:** Every section had explicit labels: `\section{Introduction}\label{sec:intro}`
- **P3 manuscript:** Sections had NO labels: `\section{Introduction}` (no label)

The `\externaldocument[M-]{}` mechanism in the Response document requires the target `.aux` file to contain `\newlabel{sec:...}` entries, which are only generated when `\label{}` commands exist in the source.

---

## Solution

Added `\label{}` commands to all referenced sections in the main manuscript **AND** added missing siunitx unit declarations to the Response document preamble.

### Part 1: Labels Added to `Paper3_Quantum_InspiredV2609.tex`

1. **sec:intro** — Section 1 (Introduction)
2. **sec:methods** — Section 2 (Methods)
3. **sec:methods_dataset** — Subsection 2.1 (Dataset)
4. **sec:results** — Section 3 (Results)
5. **sec:results_benchmark** — Subsection 3.3 (Activity prediction benchmark)
6. **sec:results_transfer** — Subsection 3.6 (Transfer under a ChEMBL label-source shift)
7. **sec:discussion** — Section 4 (Discussion)
8. **sec:disc_limitations** — Subsection 4.5 (Limitations)
9. **sec:conclusion** — Section 5 (Conclusion)

### Part 2: siunitx Unit Declarations Added to Response Preamble

The Response document used siunitx commands like `\SI{10}{\micro\molar}` and `\SI{-7.0}{\kcalmol}`, but the preamble didn't declare these units.

**Added to Response preamble:**
```latex
\DeclareSIUnit\molar{M}
\DeclareSIUnit\kcalmol{kcal\,mol^{-1}}
```

This matches the declarations in the main manuscript's preamble.

### Part 3: Label Corrected in Response Document

- Changed `\Cref{M-sec:methods_library}` → `\Cref{M-sec:methods_dataset}` (the manuscript subsection is called "Dataset", not "Library")

---

## Verification

### Before Fix

**Issue 1: Undefined cross-references**
```bash
cd V2609/
pdflatex Response_to_Reviewers_P3_V2609.tex
# Result: 7 "undefined reference" warnings
```

**Issue 2: Undefined siunitx units**
```bash
pdflatex Response_to_Reviewers_P3_V2609.tex
# Result: 
# ! Undefined control sequence.
# <argument> \micro \molar 
# ! Package siunitx Error: Found prefix part with no unit.
```

### After Fix

```bash
# Step 1: Add siunitx declarations to Response preamble
# Added: \DeclareSIUnit\molar{M} and \DeclareSIUnit\kcalmol{kcal\,mol^{-1}}

# Step 2: Recompile main manuscript to generate updated .aux with new labels
pdflatex Paper3_Quantum_InspiredV2609.tex
# Result: Paper3_Quantum_InspiredV2609.aux now contains all 9 \newlabel{sec:...} entries

# Step 3: Recompile Response document
pdflatex Response_to_Reviewers_P3_V2609.tex
# Result: 0 "undefined reference" warnings ✅
# Result: 0 siunitx errors ✅
```

**Output:**
```
Output written on Response_to_Reviewers_P3_V2609.pdf (10 pages, 234679 bytes).
Exit Code: 0
No undefined references ✅
No undefined control sequences ✅
Only cosmetic "Overfull hbox" warning (text extends 4.7pt into margin) ✅
```

---

## Cross-References Now Working

All external links in the Response document now resolve correctly:

| Response Reference | Resolves To | Target |
|-------------------|-------------|--------|
| `\Cref{M-sec:intro}` | Section 1 | Introduction |
| `\Cref{M-sec:methods_dataset}` | Section 2.1 | Dataset |
| `\Cref{M-sec:results_benchmark}` | Section 3.3 | Activity prediction benchmark |
| `\Cref{M-sec:results_transfer}` | Section 3.6 | Transfer under ChEMBL shift |
| `\Cref{M-sec:disc_limitations}` | Section 4.5 | Limitations |
| `\Cref{M-sec:conclusion}` | Section 5 | Conclusion |

**Note:** The `M-` prefix is added automatically by the `\externaldocument[M-]{...}` command in the Response preamble.

---

## Technical Details

### How External References Work in LaTeX

1. **Main manuscript compilation:**
   ```latex
   \section{Introduction}\label{sec:intro}
   ```
   Creates entry in `.aux` file:
   ```latex
   \newlabel{sec:intro}{{1}{2}{Introduction}{section.1}{}}
   ```

2. **Response document preamble:**
   ```latex
   \usepackage{xr}
   \externaldocument[M-]{Paper3_Quantum_InspiredV2609}
   ```
   Reads `Paper3_Quantum_InspiredV2609.aux` and prefixes all labels with `M-`

3. **Response document body:**
   ```latex
   \Cref{M-sec:intro}
   ```
   Resolves to "Section 1" with clickable hyperlink

---

## Files Modified

### Main Manuscript
- **File:** `Paper3_Quantum_InspiredV2609.tex`
- **Changes:** Added 9 `\label{}` commands to sections/subsections
- **Lines modified:** ~9 (one label per section)
- **Recompilation required:** Yes (to regenerate `.aux` file)

### Response Document
- **File:** `Response_to_Reviewers_P3_V2609.tex`
- **Changes:** Fixed 1 incorrect label reference (`methods_library` → `methods_dataset`)
- **Lines modified:** 1
- **Recompilation required:** Yes (to pick up new labels from main `.aux`)

### Supporting Information (No Changes)
- **File:** `Paper3_Quantum_Inspired_SM_V2609.tex`
- **Status:** No changes needed (no SM references in current Response version)

---

## Comparison with P1

### P1 Approach (Working Example)

P1's main manuscript has comprehensive labels:

```latex
\section{Introduction}\label{sec:intro}
\section{Materials and Methods}\label{sec:methods}
\subsection{Chemical-space funnel}\label{sec:methods_funnel}
\subsection{Candidate-set identity}\label{sec:methods_cohort}
... (28 total section labels)
```

P1's Response document uses them:

```latex
\externaldocument[M-]{P1_Integrated_Polypharmacology_RRS_Main_V8}
...
We clarified this in \Cref{M-sec:intro}.
The Methods section describes \Cref{M-sec:methods_funnel}.
```

**Result:** All cross-references work perfectly.

### P3 Approach (Now Fixed)

P3's main manuscript originally had NO labels:

```latex
\section{Introduction}          ← No label!
\section{Methods}                ← No label!
\subsection{Dataset}             ← No label!
```

P3's Response tried to use non-existent labels:

```latex
\externaldocument[M-]{Paper3_Quantum_InspiredV2609}
...
\Cref{M-sec:intro}               ← Undefined!
\Cref{M-sec:methods_library}     ← Undefined!
```

**Result:** 7 undefined references, "??" in PDF.

**After fix:** P3 now matches P1's approach with explicit labels everywhere.

---

## Best Practices

### For Future Manuscripts

1. **Always add labels to major sections:**
   ```latex
   \section{Introduction}\label{sec:intro}
   \section{Methods}\label{sec:methods}
   \section{Results}\label{sec:results}
   \section{Discussion}\label{sec:discussion}
   \section{Conclusion}\label{sec:conclusion}
   ```

2. **Add labels to key subsections:**
   ```latex
   \subsection{Dataset}\label{sec:methods_dataset}
   \subsection{Benchmark}\label{sec:results_benchmark}
   ```

3. **Use descriptive label names:**
   - ✅ Good: `sec:methods_dataset`, `sec:results_benchmark`
   - ❌ Bad: `sec:1`, `sec:A`, `sec:test`

4. **Check cross-references compile cleanly:**
   ```bash
   pdflatex manuscript.tex
   grep "undefined" manuscript.log
   # Should return nothing
   ```

---

## Lessons Learned

1. **Template compliance:** The P3 Response was based on the P1 template (which worked), but the P3 *manuscript* lacked the labels that P1's manuscript had.

2. **Cross-document dependencies:** External references create a dependency chain:
   - Response → requires → Main `.aux` → requires → Labels in Main `.tex`
   - If any link breaks, cross-references fail

3. **Compilation order matters:**
   ```bash
   # Correct order:
   1. pdflatex main.tex           # Generate .aux with labels
   2. pdflatex response.tex       # Read .aux for cross-refs
   
   # Wrong order:
   1. pdflatex response.tex       # .aux doesn't exist or is outdated
   2. pdflatex main.tex           # Too late, response already compiled
   ```

4. **Verification is essential:** Always check for "undefined reference" warnings after changes.

---

## Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Main manuscript labels | ✅ Added | 9 labels added to key sections |
| Response cross-references | ✅ Fixed | 1 label corrected, all resolve |
| Compilation | ✅ Clean | 0 undefined references |
| PDF output | ✅ Correct | Cross-references clickable |
| Ready for submission | ✅ Yes | All external links work |

---

## Final Verification Commands

```bash
cd ~/Documents/GitHub/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607_V4/manuscript/LaTeX/V2609

# Verify main manuscript has labels
grep "\\\\label{sec:" Paper3_Quantum_InspiredV2609.tex
# Expected: 9 lines with \label{sec:...}

# Verify .aux file has newlabel entries
grep "newlabel{sec:" Paper3_Quantum_InspiredV2609.aux
# Expected: 9 lines with \newlabel{sec:...}

# Verify Response compiles cleanly
pdflatex Response_to_Reviewers_P3_V2609.tex 2>&1 | grep -i "undefined"
# Expected: No output (no matches)

# Verify PDF generated
ls -lh Response_to_Reviewers_P3_V2609.pdf
# Expected: 10 pages, ~235 KB
```

---

**Issue Resolved:** 15 September 2026  
**Fixed By:** Kiro AI  
**Verification:** Complete ✅

---

**End of Fix Report**
