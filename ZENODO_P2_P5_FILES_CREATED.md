# Zenodo P2 & P5 Upload Documentation — Files Created

**Date**: 2026-09-16  
**Purpose**: Complete list of documentation files created for P2 and P5 Zenodo uploads  
**Model**: Following P3 Zenodo template structure

---

## Overview

This document lists all files created to support the Zenodo upload process for P2 and P5 projects. The structure and content follow the established P3 template.

---

## Master Planning Documents

### 1. ZENODO_P2_P5_UPLOAD_PLAN.md
- **Location**: `/home/vital/Documents/GitHub/Malaria_codesV2/`
- **Purpose**: Comprehensive upload workflow for both P2 and P5
- **Content**:
  - Step-by-step upload process
  - DOI reservation instructions
  - Package verification procedures
  - Post-upload actions
  - Timeline and checklist

### 2. ZENODO_P2_P5_QUICK_REFERENCE.md
- **Location**: `/home/vital/Documents/GitHub/Malaria_codesV2/`
- **Purpose**: Fast-access reference guide
- **Content**:
  - At-a-glance project comparison
  - Quick start workflow
  - Key metadata (keywords, descriptions)
  - Git commands
  - Common issues and solutions
  - Timeline estimates

### 3. ZENODO_P2_P5_FILES_CREATED.md
- **Location**: `/home/vital/Documents/GitHub/Malaria_codesV2/`
- **Purpose**: This document — inventory of all created files
- **Content**:
  - Complete file listing
  - File descriptions
  - Usage instructions
  - Relationships between documents

---

## P2 Project-Specific Documents

### 4. P2 UPLOAD_INSTRUCTIONS.md
- **Location**: `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/`
- **Purpose**: Detailed step-by-step upload guide for P2
- **Content**:
  - Pre-upload checklist
  - DOI reservation process
  - Zenodo web interface instructions
  - Metadata entry (complete descriptions, keywords)
  - File upload options (drag-drop, ZIP)
  - Pre-publish verification
  - Post-publish actions
  - Manuscript update instructions
  - Troubleshooting guide

### 5. P2 UPLOAD_CHECKLIST.md
- **Location**: `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/`
- **Purpose**: Interactive checklist for P2 upload process
- **Content**:
  - 10-phase upload workflow
  - Checkbox lists for each phase
  - Pre-upload preparation
  - DOI reservation
  - Metadata entry
  - File upload
  - Pre-publish verification
  - Publish
  - Post-publish verification
  - Manuscript update
  - Repository updates
  - Final documentation
  - Troubleshooting log
  - Timeline estimates

---

## P5 Project-Specific Documents

### 6. P5 UPLOAD_INSTRUCTIONS.md
- **Location**: `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/`
- **Purpose**: Detailed step-by-step upload guide for P5
- **Content**:
  - Pre-upload checklist
  - DOI reservation process
  - Zenodo web interface instructions
  - Metadata entry (complete descriptions, keywords)
  - File upload options (drag-drop, ZIP, subdirectory ZIPs)
  - Large file handling strategies (2GB package)
  - Pre-publish verification
  - Post-publish actions
  - Manuscript update instructions (when ready)
  - Troubleshooting guide
  - Special notes for large file uploads

### 7. P5 UPLOAD_CHECKLIST.md
- **Location**: `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/`
- **Purpose**: Interactive checklist for P5 upload process
- **Content**:
  - 10-phase upload workflow
  - Checkbox lists for each phase
  - Pre-upload preparation
  - DOI reservation
  - Metadata entry
  - File upload (with large file considerations)
  - Pre-publish verification
  - Publish
  - Post-publish verification
  - Manuscript update (when ready)
  - Repository updates
  - Final documentation
  - Special considerations for P5 (2GB, extended campaign)
  - Troubleshooting log
  - Timeline estimates (3-4 hours)

---

## Document Relationships

### Hierarchy

```
Master Documents (Workspace Root)
├── ZENODO_P2_P5_UPLOAD_PLAN.md          (Comprehensive workflow)
├── ZENODO_P2_P5_QUICK_REFERENCE.md      (Fast reference)
└── ZENODO_P2_P5_FILES_CREATED.md        (This document)
    |
    ├── P2 Documents (Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/)
    │   ├── UPLOAD_INSTRUCTIONS.md        (Detailed guide)
    │   └── UPLOAD_CHECKLIST.md           (Interactive checklist)
    |
    └── P5 Documents (Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/)
        ├── UPLOAD_INSTRUCTIONS.md        (Detailed guide)
        └── UPLOAD_CHECKLIST.md           (Interactive checklist)
```

### Cross-References

- **UPLOAD_PLAN** → References both UPLOAD_INSTRUCTIONS.md files
- **QUICK_REFERENCE** → Summarizes key info from all documents
- **UPLOAD_INSTRUCTIONS** → Referenced by UPLOAD_CHECKLIST
- **UPLOAD_CHECKLIST** → Points to UPLOAD_INSTRUCTIONS for details

---

## Comparison with P3 Template

All documents follow the established P3 template structure:

| Document Type | P3 | P2 | P5 |
|---------------|----|----|-----|
| UPLOAD_INSTRUCTIONS.md | ✅ | ✅ | ✅ |
| UPLOAD_CHECKLIST.md | ✅ | ✅ | ✅ |
| README.md | ✅ | ✅* | ✅* |
| MANIFEST.json | ✅ | ✅* | ✅* |

*Existing files to be updated with reserved DOIs

---

## Files to Update (Not Created)

These existing files need DOI updates after reservation:

### P2
1. `zenodo_package_P2/README.md` → Add reserved DOI to header
2. `zenodo_package_P2/MANIFEST.json` → Update `"doi_reserved"` field

### P5
1. `zenodo_package_P5/README.md` → Add reserved DOI to header
2. `zenodo_package_P5/MANIFEST.json` → Update `"doi_reserved"` field

### Both Projects
1. `AGENTS.md` → Update Zenodo status after publication

---

## Usage Instructions

### For Initial DOI Reservation

1. Read: `ZENODO_P2_P5_UPLOAD_PLAN.md` (Step 1)
2. Use: Project-specific `UPLOAD_INSTRUCTIONS.md` (Step 1)
3. Update: All package files with reserved DOI

### For Package Verification

1. Read: `ZENODO_P2_P5_QUICK_REFERENCE.md` (Step 3)
2. Follow: Commands in project-specific `UPLOAD_INSTRUCTIONS.md` (Pre-Upload Checklist)

### For Upload Process

1. Use: Project-specific `UPLOAD_CHECKLIST.md` (complete all phases)
2. Reference: Project-specific `UPLOAD_INSTRUCTIONS.md` (detailed steps)
3. Quick lookup: `ZENODO_P2_P5_QUICK_REFERENCE.md` (metadata, keywords)

### For Post-Upload Actions

1. Follow: `UPLOAD_CHECKLIST.md` Phases 7-10
2. Reference: `UPLOAD_INSTRUCTIONS.md` Post-Upload sections
3. Update: Manuscript and AGENTS.md as specified

---

## Key Features

### Consistency Across Projects

All documents maintain consistent:
- Author lists and ORCIDs
- License (CC BY 4.0)
- Upload type (Dataset)
- Section structures
- Phase numbering
- Checklist formats

### Project-Specific Adaptations

#### P2
- ~500 MB package size
- 10-30 minute upload time
- JCIM manuscript (V2609C ready)
- MD validation focus
- Estimand divergence emphasis

#### P5
- ~2 GB package size
- 1-2 hour upload time
- JCAMD manuscript (pre-submission)
- GNN/Transformer focus
- Honest-negative results emphasis
- Special large-file handling instructions

---

## Maintenance Notes

### When to Update

1. **After DOI Reservation**: Update all package files with actual DOI
2. **After Publication**: Update AGENTS.md with published status
3. **If Issues Arise**: Document in Troubleshooting Log sections
4. **If Process Changes**: Update master UPLOAD_PLAN first, then cascade to specific documents

### Version Control

All documents created: 2026-09-16  
Following: P3 template (established 2026-09-11)  
Updates needed: After DOI reservation and publication

---

## Success Metrics

### Document Completeness
✅ Master planning documents created (3)  
✅ P2-specific documents created (2)  
✅ P5-specific documents created (2)  
✅ Cross-references established  
✅ Follows P3 template structure  
✅ Project-specific adaptations included  

### Upload Readiness
- [ ] DOIs reserved (pending action)
- [ ] Package files updated (pending DOI)
- [ ] Checksums verified (existing)
- [ ] Documentation complete ✅

---

## Next Steps

### Immediate (To Reserve DOIs)
1. Follow `ZENODO_P2_P5_UPLOAD_PLAN.md` Step 1
2. Reserve both DOIs on Zenodo
3. Update all package files with reserved DOIs
4. Verify package contents

### After DOI Reservation
1. Complete P2 upload following `UPLOAD_CHECKLIST.md`
2. Complete P5 upload following `UPLOAD_CHECKLIST.md`
3. Update manuscripts with DOIs
4. Create git tags
5. Update AGENTS.md

---

## Related Documentation

### Existing Zenodo Docs (For Reference)
- `ZENODO_QUICK_START.md` — General guide (includes P3, P4, P5)
- `ZENODO_PACKAGES_SUMMARY.md` — Overview of all packages
- `ZENODO_BUILD_REPORT.md` — Build process documentation
- `ZENODO_ACTION_CHECKLIST.md` — Action items
- `ZENODO_STATUS.md` — Status tracking for all projects

### Project Data Analysis Reports
- `Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md`
- `Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md`

### Project Manuscripts
- P2: `Project2_Polypharmacology_MD_ValidationV2607/manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`
- P5: (pre-submission development)

---

## Contact

- **Zenodo Support**: info@zenodo.org
- **Corresponding Author**: myke-vital.sao@facsciences-uy1.cm
- **Repository**: https://github.com/NanaEngo/Malaria_codesV2

---

## Summary

**Total Files Created**: 7

**Master Documents** (3):
- ZENODO_P2_P5_UPLOAD_PLAN.md
- ZENODO_P2_P5_QUICK_REFERENCE.md
- ZENODO_P2_P5_FILES_CREATED.md

**P2 Documents** (2):
- UPLOAD_INSTRUCTIONS.md
- UPLOAD_CHECKLIST.md

**P5 Documents** (2):
- UPLOAD_INSTRUCTIONS.md
- UPLOAD_CHECKLIST.md

**All documents are ready for use immediately after DOI reservation.**

---

**Last updated**: 2026-09-16  
**Prepared by**: Kiro AI agent  
**Template**: Following P3 Zenodo structure
