# P3 V2609 Manuscript Conversion to Springer Nature Template

## Conversion Summary

**Date:** September 16, 2026  
**Source:** `Paper3_Quantum_InspiredV2609.tex` (372 lines)  
**Target:** `sn-article.tex` (Springer Nature sn-jnl class)  
**Status:** ✅ Successfully completed and compiled

## Conversion Details

### Document Class
- **From:** `\documentclass[11pt,a4paper]{article}`
- **To:** `\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}`
- **Style:** Math and Physical Sciences Numbered Reference Style

### Author Information Conversion
Converted from `authblk` package format to Springer Nature `\author` and `\affil` commands:

```latex
\author*[1]{\fnm{Myke Vital} \sur{Sao Temgoua}}\email{myke-vital.sao@facsciences-uy1.cm}
\author[1]{\fnm{Jean-Pierre} \sur{Tchapet Njafa}}
\author[1]{\fnm{Serge Guy} \sur{Nana Engo}}
\author[2]{\fnm{Penabei} \sur{Samafou}}
\author[3]{\fnm{Fon Wilfred} \sur{Mbacham}}
```

### Content Preserved

#### Complete manuscript structure:
1. ✅ **Title** (full 94-character title preserved)
2. ✅ **Abstract** (370 words with contribution statement and highlights)
3. ✅ **Keywords** (7 keywords)
4. ✅ **Introduction** (Section 1)
5. ✅ **Methods** (Section 2 with 6 subsections)
   - Dataset
   - Classical fingerprint baselines
   - Topological Fingerprint (with subsections)
   - Tensor Network Embedding (with subsections)
   - Quantum Kernel Score
   - Hybrid descriptor
   - Evaluation protocol
   - Software
6. ✅ **Results** (Section 3 with 6 subsections)
   - Scaffold decomposition by persistent homology
   - Binding-relevant information in tensor network compression
   - Activity prediction benchmark
   - Hybrid descriptor and quantum kernel comparison
   - Fusion with a classical fingerprint
   - Transfer under a ChEMBL label-source shift
   - Topological features and multi-target docking profiles
7. ✅ **Discussion** (Section 4 with 5 subsections)
8. ✅ **Conclusion** (Section 5)
9. ✅ **Backmatter**
   - Supplementary information
   - Data Availability
   - List of Abbreviations
   - Acknowledgments
   - Declarations (Funding, Competing interests, Ethics, Consent, Author contributions, Use of AI)

#### Mathematical Content:
- ✅ All 4 numbered equations preserved
- ✅ siunitx package retained for scientific notation
- ✅ Custom SI units (\angstrom, \molar, \kcalmol) declared
- ✅ Mathematical symbols and formatting intact

#### Figures and Tables:
- ✅ Table 1 (Activity-prediction performance) with complex tabularx formatting
- ✅ Figure 1 (scaffold_paradox.pdf) reference
- ✅ Figure 2 (applicability_domain.pdf) reference
- ✅ Figure 3 (p3_extval_internal_vs_external.png) reference
- ✅ Graphics path adjusted: `\graphicspath{{../Graphics/}}`

#### Cross-References:
- ✅ External document reference to SM: `\externaldocument[X-]{../Paper3_Quantum_Inspired_SM_V2609}`
- ✅ All internal cross-references (sections, figures, tables, equations)
- ✅ Citation commands converted from natbib style to work with sn-mathphys-num

#### Bibliography:
- ✅ Bibliography file copied: `Bibliography_Paper3.bib`
- ✅ Bibliography style: `sn-mathphys-num.bst` (copied from bst/ subdirectory)
- ✅ All citations preserved (~40 unique citations)

### Package Adjustments

**Added packages for Springer Nature compatibility:**
```latex
\usepackage{tabularx}%
\usepackage{array}%
\usepackage{longtable}%
```

**Retained specialized packages:**
- siunitx (with all custom unit declarations)
- xr (for external document references to Supporting Information)
- All mathematical packages (amsmath, amssymb, amsfonts, mathtools)
- booktabs (for professional tables)

**Removed packages (handled by sn-jnl class):**
- geometry (page layout)
- fontenc, inputenc, lmodern (font handling)
- hyperref configuration (class handles this)
- natbib (replaced by class bibliography system)
- cleveref (not needed with Springer class)
- caption customization (class provides styling)
- authblk (replaced by class author system)

### File Locations

**Template directory:**
```
/home/vital/Documents/GitHub/Malaria_codesV2/
  Project3_Quantum_Inspired_RepresentationsV2607_V4/
    manuscript/LaTeX/V2609/sn-article-template/
```

**Files:**
- `sn-article.tex` - Main manuscript (converted)
- `sn-article.pdf` - Compiled output (18 pages, 564 KB)
- `Bibliography_Paper3.bib` - Bibliography database (copied)
- `sn-mathphys-num.bst` - Bibliography style (copied from bst/)

**Graphics path:**
- Figures remain in `../Graphics/` relative to template directory
- External document reference: `../Paper3_Quantum_Inspired_SM_V2609`

## Compilation Status

### Successful compilation:
```bash
cd sn-article-template
pdflatex sn-article.tex
bibtex sn-article
pdflatex sn-article.tex
pdflatex sn-article.tex
```

### Output:
- **Pages:** 18
- **File size:** 564 KB
- **Errors:** 0
- **Undefined references:** 0
- **Warnings:** Font size substitutions only (cosmetic)

## Quality Assurance

✅ **All content preserved:** No scientific content was removed or altered  
✅ **Equations intact:** All 4 numbered equations compile correctly  
✅ **Tables formatted:** Complex tabularx table with siunitx columns preserved  
✅ **Figures referenced:** All 3 figure references maintained with correct paths  
✅ **Citations working:** All ~40 citations compile with numbered style  
✅ **Cross-references:** Internal and external references functional  
✅ **Math notation:** All mathematical symbols and formatting preserved  
✅ **SI units:** Custom unit definitions working correctly  
✅ **Author metadata:** All 5 authors with correct affiliations  
✅ **Backmatter:** Complete with all declarations and acknowledgments  

## Template Compliance

The converted manuscript fully complies with Springer Nature requirements:

1. ✅ Uses sn-jnl document class (version 3.1, December 2024)
2. ✅ Uses sn-mathphys-num bibliography style (numbered references)
3. ✅ Author format: `\fnm{}` and `\sur{}` with proper affiliation markers
4. ✅ Affiliations use `\orgdiv`, `\orgname`, `\orgaddress` structure
5. ✅ Abstract is unstructured (as per journal preference)
6. ✅ Keywords provided
7. ✅ Backmatter sections properly formatted
8. ✅ Declarations section complete
9. ✅ Data Availability statement included
10. ✅ Supporting Information referenced

## Next Steps

The manuscript is now ready for:
1. ✅ Compilation testing (completed successfully)
2. ⏭️ Content review by authors
3. ⏭️ Final proofreading
4. ⏭️ Submission to target Springer Nature journal

## Notes

- The graphical abstract line was removed as it's typically not included in the main manuscript body for journal submission
- All technical content, data, results, and conclusions remain exactly as in the original V2609 manuscript
- The Supporting Information cross-reference path `../Paper3_Quantum_Inspired_SM_V2609` may need adjustment depending on SM location during submission
- No changes were made to scientific content, claims, or interpretations
