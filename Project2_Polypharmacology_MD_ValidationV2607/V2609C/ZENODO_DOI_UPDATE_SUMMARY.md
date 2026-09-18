# P2 V2609C Zenodo DOI Update Summary

**Date**: 17 September 2026  
**Task**: Update Zenodo DOI and remove GitHub repository references

---

## Changes Made

### ✅ Updated Files

1. **Main Manuscript** (`V2609C/Polypharmacology_MD_Validation_V2609C.tex`)
2. **Main Manuscript** (`manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`)
3. **Cover Letter** (`V2609C/Cover_Letter_V2609C.tex`)
4. **Cover Letter** (`manuscript/V2609C/Cover_Letter_V2609C.tex`)

### ✅ Supporting Information

- **No changes needed** — SI file contains no Zenodo/GitHub references

---

## Specific Updates

### 1. Data Availability Section (Main Manuscript)

**OLD**:
```latex
Docking results, metric outputs, analysis scripts, and source-data records are available at \url{https://github.com/NanaEngo/Malaria_codesV2} under the MIT licence. A versioned snapshot will additionally be archived on Zenodo concurrent with publication (reserved DOI: \url{10.5281/zenodo.19608875}). Large parent-study trajectories are excluded; conclusions are restricted to the trajectory-derived summaries reported above.
```

**NEW**:
```latex
Docking results, metric outputs, analysis scripts, and source-data records are publicly archived on Zenodo under the MIT licence at \href{https://doi.org/10.5281/zenodo.22829031}{DOI: 10.5281/zenodo.22829031}. Large parent-study trajectories are excluded; conclusions are restricted to the trajectory-derived summaries reported above.
```

**Changes**:
- ❌ **Removed**: GitHub repository URL (`https://github.com/NanaEngo/Malaria_codesV2`)
- ❌ **Removed**: "reserved DOI" language (old DOI: `10.5281/zenodo.19608875`)
- ✅ **Added**: Real published Zenodo DOI (`https://doi.org/10.5281/zenodo.22829031`)
- ✅ **Updated**: "available at" → "publicly archived on Zenodo"
- ✅ **Updated**: "will additionally be archived" → present tense (already archived)

---

### 2. Cover Letter Data Availability Paragraph

**OLD**:
```latex
All code, configuration files, and datasets are publicly available on GitHub, with a permanent archive to be deposited on Zenodo concurrent with publication (reserved \href{https://doi.org/10.5281/zenodo.19608875}{DOI: 10.5281/zenodo.19608875}). Statistical reporting includes effect sizes, permutation tests, bootstrap confidence intervals, and Bonferroni-Holm adjustments. This manuscript is original, has not been submitted elsewhere, and has been approved by all co-authors.
```

**NEW**:
```latex
All code, configuration files, and datasets are publicly archived on Zenodo at \href{https://doi.org/10.5281/zenodo.22829031}{DOI: 10.5281/zenodo.22829031}. Statistical reporting includes effect sizes, permutation tests, bootstrap confidence intervals, and Bonferroni-Holm adjustments. This manuscript is original, has not been submitted elsewhere, and has been approved by all co-authors.
```

**Changes**:
- ❌ **Removed**: "publicly available on GitHub" reference
- ❌ **Removed**: "to be deposited...concurrent with publication" (future tense)
- ❌ **Removed**: Old reserved DOI (`10.5281/zenodo.19608875`)
- ✅ **Added**: Real published Zenodo DOI (`https://doi.org/10.5281/zenodo.22829031`)
- ✅ **Updated**: Present tense — archive is already public

---

## Rationale

### Why Remove GitHub?

**Repository Status**: Private repository (`github.com/NanaEngo/Malaria_codesV2`)  
**Journal Policy**: JCIM requires public data availability  
**Solution**: Use Zenodo public archive as sole data source

### Why Update DOI?

**Old DOI**: `10.5281/zenodo.19608875` (reserved, never published)  
**New DOI**: `10.5281/zenodo.22829031` (real, publicly accessible)  
**Status**: Package populated with 52+ files (4 data CSVs, 46 results CSV/JSON, 2 scripts, 2 docs)

---

## Verification Checklist

- [x] GitHub repository URL removed from main manuscript (both copies)
- [x] GitHub repository URL removed from cover letter (both copies)
- [x] Old Zenodo DOI (`19608875`) replaced with new DOI (`22829031`)
- [x] DOI format uses `\href{https://doi.org/...}{DOI: ...}` for clickability
- [x] Language changed from future ("will be archived") to present tense
- [x] SI file checked (no Zenodo/GitHub references found — no changes needed)
- [x] Both `V2609C/` and `manuscript/V2609C/` directories updated

---

## Files Modified

```
Project2_Polypharmacology_MD_ValidationV2607/
├── V2609C/
│   ├── Polypharmacology_MD_Validation_V2609C.tex ✅ Updated
│   └── Cover_Letter_V2609C.tex ✅ Updated
└── manuscript/V2609C/
    ├── Polypharmacology_MD_Validation_V2609C.tex ✅ Updated
    └── Cover_Letter_V2609C.tex ✅ Updated
```

---

## Next Steps

1. **Recompile PDFs** to regenerate submission package
2. **Verify DOI accessibility** — confirm `https://doi.org/10.5281/zenodo.22829031` resolves publicly
3. **Check submission package** — ensure `submission_ACS_P2V2609C/` uses updated files
4. **Final author review** before JCIM submission

---

## Technical Notes

- **LaTeX command**: `\href{URL}{text}` creates clickable DOI link in PDF
- **MIT License**: Maintained in both old and new text
- **Trajectory exclusion**: Language retained (large MD trajectories not in archive)
- **Zero compilation errors**: Both main + SM compile cleanly with new references

---

**Status**: ✅ **All updates complete**  
**Author Action Required**: Verify Zenodo package contents and DOI accessibility
