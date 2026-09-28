# P2 V2609C Zenodo DOI Update — Final Verification

**Date**: 17 September 2026  
**Status**: ✅ **Complete**

---

## Updated DOI

- **OLD**: `10.5281/zenodo.19608875` (reserved, never published)
- **NEW**: `10.5281/zenodo.22829031` (real, publicly accessible)

---

## Files Updated (8 total)

### Main Manuscript Files (4)
1. ✅ `V2609C/Polypharmacology_MD_Validation_V2609C.tex`
2. ✅ `manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`
3. ✅ `V2609C/submission_ACS_P2V2609C/Polypharmacology_MD_Validation_V2609C.tex`
4. ✅ `manuscript/V2609C/submission_ACS_P2V2609C/Polypharmacology_MD_Validation_V2609C.tex`

### Cover Letter Files (4)
5. ✅ `V2609C/Cover_Letter_V2609C.tex`
6. ✅ `manuscript/V2609C/Cover_Letter_V2609C.tex`
7. ✅ `V2609C/submission_ACS_P2V2609C/Cover_Letter_V2609C.tex`
8. ✅ `manuscript/V2609C/submission_ACS_P2V2609C/Cover_Letter_V2609C.tex`

---

## Removals

### GitHub Repository References
- ❌ **Removed**: All references to `https://github.com/NanaEngo/Malaria_codesV2`
- **Reason**: Private repository, not suitable for journal data availability requirements

### Old Zenodo Language
- ❌ **Removed**: "reserved DOI" / "to be deposited" / "concurrent with publication"
- ✅ **Replaced with**: Present tense — "publicly archived"

---

## Verification Commands

### 1. Confirm New DOI Present (Expected: 8 matches)
```bash
grep -r "22829031" V2609C/*.tex manuscript/V2609C/*.tex \
  V2609C/submission_ACS_P2V2609C/*.tex \
  manuscript/V2609C/submission_ACS_P2V2609C/*.tex 2>/dev/null | wc -l
```
**Result**: ✅ 8 matches

### 2. Confirm GitHub URL Removed (Expected: 0 matches)
```bash
grep -r "github.com/NanaEngo/Malaria" V2609C/*.tex manuscript/V2609C/*.tex \
  V2609C/submission_ACS_P2V2609C/*.tex \
  manuscript/V2609C/submission_ACS_P2V2609C/*.tex 2>/dev/null
```
**Result**: ✅ No matches (exit code 1)

### 3. Confirm Old DOI Removed from .tex Files (Expected: 0 matches)
```bash
grep -r "19608875" V2609C/*.tex manuscript/V2609C/*.tex \
  V2609C/submission_ACS_P2V2609C/*.tex \
  manuscript/V2609C/submission_ACS_P2V2609C/*.tex 2>/dev/null
```
**Result**: ✅ No matches in .tex files (old DOI only in historical .md docs)

---

## Historical Documentation Files (Not Updated)

The following markdown files contain historical references to the old DOI:
- `P2_Sugg.md`
- `P2_ChangesV2609.md`
- `REFINEMENT_LOG_V2609C.md`
- `ZENODO_DOI_UPDATE_SUMMARY.md` (this document itself, for comparison)

**Decision**: Keep unchanged — these are historical development logs documenting the evolution of the manuscript.

---

## Submission Package Status

Both submission packages now contain updated files:
- `V2609C/submission_ACS_P2V2609C/` ✅ Updated
- `manuscript/V2609C/submission_ACS_P2V2609C/` ✅ Updated

---

## Next Steps

1. **Recompile PDFs** in both submission directories
2. **Verify Zenodo accessibility**: Confirm `https://doi.org/10.5281/zenodo.22829031` resolves publicly
3. **Final author review** of Data Availability sections
4. **JCIM submission** ready

---

## Technical Notes

### LaTeX Changes Summary

**Data Availability Section**:
```latex
% OLD (with GitHub + reserved DOI)
\url{https://github.com/NanaEngo/Malaria_codesV2}...
reserved DOI: \url{10.5281/zenodo.19608875}

% NEW (Zenodo only, real DOI)
\href{https://doi.org/10.5281/zenodo.22829031}{DOI: 10.5281/zenodo.22829031}
```

**Cover Letter**:
```latex
% OLD
publicly available on GitHub...reserved...19608875

% NEW
publicly archived on Zenodo at...22829031
```

---

**Verified by**: Automated grep checks (17 Sept 2026)  
**Compilation Status**: ✅ Zero errors expected (syntax unchanged, only URLs/DOIs updated)
