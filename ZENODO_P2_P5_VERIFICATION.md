# Zenodo P2 & P5 Package Verification

**Date**: 2026-09-16  
**Purpose**: Verify that P2 and P5 packages have all necessary files before upload

---

## Files Created Today (2026-09-16)

✅ **8 new documentation files created:**

### Master Documents (Workspace Root)
1. `ZENODO_P2_P5_UPLOAD_PLAN.md`
2. `ZENODO_P2_P5_QUICK_REFERENCE.md`
3. `ZENODO_P2_P5_FILES_CREATED.md`
4. `ZENODO_P2_P5_SUMMARY.md`
5. `ZENODO_P2_P5_VERIFICATION.md` (this file)

### P2 Package Documents
6. `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/UPLOAD_INSTRUCTIONS.md`
7. `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/UPLOAD_CHECKLIST.md`

### P5 Package Documents
8. `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/UPLOAD_INSTRUCTIONS.md`
9. `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/UPLOAD_CHECKLIST.md`

---

## P2 Package Files to Verify

### Core Package Files (Should Exist)
- [ ] `README.md` — Package overview and usage guide
- [ ] `MANIFEST.json` — Structured metadata
- [ ] `LICENSE.txt` — CC BY 4.0 license
- [ ] `sha256sums.txt` — Checksums (or to be generated)

### New Upload Documentation (Created Today)
- [x] `UPLOAD_INSTRUCTIONS.md` — Detailed upload guide
- [x] `UPLOAD_CHECKLIST.md` — Interactive checklist

### Subdirectories (Should Exist)
- [ ] `data/` — Core datasets
- [ ] `results/` — MD-RRS, MM-GBSA, external replication
- [ ] `scripts/` — Analysis pipelines
- [ ] `documentation/` — DAR and methods supplements

---

## P5 Package Files to Verify

### Core Package Files (Should Exist)
- [ ] `README.md` — Package overview and usage guide
- [ ] `MANIFEST.json` — Structured metadata
- [ ] `LICENSE.txt` — CC BY 4.0 license
- [ ] `sha256sums.txt` — Checksums (or to be generated)

### New Upload Documentation (Created Today)
- [x] `UPLOAD_INSTRUCTIONS.md` — Detailed upload guide
- [x] `UPLOAD_CHECKLIST.md` — Interactive checklist

### Subdirectories (Should Exist)
- [ ] `data/` — Core datasets
- [ ] `results/` — Benchmark results, extended campaign
- [ ] `scripts/` — GNN/Transformer pipelines
- [ ] `documentation/` — DAR and methods supplements

---

## Files to Update After DOI Reservation

### P2
- [ ] `zenodo_package_P2/README.md` → Add DOI to header
- [ ] `zenodo_package_P2/MANIFEST.json` → Update `"doi_reserved"` field
- [ ] `zenodo_package_P2/UPLOAD_INSTRUCTIONS.md` → Replace XXXXXXX with actual DOI

### P5
- [ ] `zenodo_package_P5/README.md` → Add DOI to header
- [ ] `zenodo_package_P5/MANIFEST.json` → Update `"doi_reserved"` field
- [ ] `zenodo_package_P5/UPLOAD_INSTRUCTIONS.md` → Replace XXXXXXX with actual DOI

---

## Verification Commands

### Check P2 Package Structure
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2

# List all files
ls -la

# Check subdirectories
ls -d data/ results/ scripts/ documentation/

# Check new upload docs
ls -l UPLOAD_INSTRUCTIONS.md UPLOAD_CHECKLIST.md

# Verify size
du -sh .
```

### Check P5 Package Structure
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5

# List all files
ls -la

# Check subdirectories
ls -d data/ results/ scripts/ documentation/

# Check new upload docs
ls -l UPLOAD_INSTRUCTIONS.md UPLOAD_CHECKLIST.md

# Verify size
du -sh .
```

---

## Next Steps

1. **Verify packages** using commands above
2. **Reserve DOIs** on Zenodo for both projects
3. **Update package files** with reserved DOIs
4. **Generate checksums** if not already present:
   ```bash
   # In each zenodo_package_PX/ directory:
   find . -type f -not -name "sha256sums.txt" -exec sha256sum {} \; > sha256sums.txt
   ```
5. **Follow UPLOAD_CHECKLIST.md** for each project

---

**Status**: Documentation complete, ready for verification and upload  
**Created**: 2026-09-16
