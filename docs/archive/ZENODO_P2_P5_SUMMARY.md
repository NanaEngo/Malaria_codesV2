# Zenodo P2 & P5 Upload Preparation — Complete Summary

**Date**: 2026-09-16  
**Status**: ✅ Documentation complete, ready for DOI reservation and upload  
**Model**: Following established P3 template

---

## Executive Summary

Complete Zenodo upload documentation has been prepared for **P2** (Polypharmacology MD Validation) and **P5** (GNN/Transformer Drug Discovery) projects. All necessary files are ready following the established P3 template structure.

### What's Ready
✅ **7 new documentation files created**  
✅ **Complete upload workflows documented**  
✅ **Step-by-step checklists prepared**  
✅ **Metadata templates ready**  
✅ **Troubleshooting guides included**  
✅ **Post-upload procedures documented**  

### What's Needed
⚠️ **Reserve Zenodo DOIs** (both projects)  
⚠️ **Update package files with DOIs**  
⚠️ **Execute uploads**  
⚠️ **Update manuscripts and AGENTS.md**  

---

## Files Created

### Master Documents (Workspace Root)

1. **ZENODO_P2_P5_UPLOAD_PLAN.md**
   - Comprehensive workflow for both projects
   - DOI reservation instructions
   - Package verification procedures
   - Post-upload actions
   - Timeline and master checklist

2. **ZENODO_P2_P5_QUICK_REFERENCE.md**
   - Fast-access reference guide
   - Side-by-side project comparison
   - Quick start commands
   - Key metadata ready to copy-paste
   - Common issues and solutions

3. **ZENODO_P2_P5_FILES_CREATED.md**
   - Complete inventory of created files
   - Document relationships
   - Usage instructions
   - Maintenance notes

4. **ZENODO_P2_P5_SUMMARY.md** (this file)
   - Executive summary
   - Quick action guide
   - Key differences highlighted

### P2-Specific Documents

Located in: `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/`

5. **UPLOAD_INSTRUCTIONS.md**
   - Detailed P2 upload guide
   - Zenodo web interface walkthrough
   - Complete metadata templates
   - ~500 MB package handling
   - P2-specific troubleshooting

6. **UPLOAD_CHECKLIST.md**
   - 10-phase interactive checklist
   - Checkbox format for tracking progress
   - Estimated 2-2.5 hour timeline
   - Troubleshooting log section

### P5-Specific Documents

Located in: `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/`

7. **UPLOAD_INSTRUCTIONS.md**
   - Detailed P5 upload guide
   - Large file handling (~2 GB)
   - Multiple upload strategy options
   - P5-specific troubleshooting

8. **UPLOAD_CHECKLIST.md**
   - 10-phase interactive checklist
   - Large file considerations
   - Estimated 3-4 hour timeline
   - Extended campaign notes

---

## Quick Action Guide

### Step 1: Reserve DOIs (Start Here)

```bash
# Go to: https://zenodo.org → "New upload"

# P2 Title:
P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads

# P5 Title:
P5 Reproducibility Package — JCAMD Submission: Graph neural networks and transformers for antimalarial drug discovery under distribution shift

# Authors (both):
1. Sao Temgoua, Myke Vital (ORCID: 0009-0004-5170-2309)
2. Tchapet Njafa, Jean-Pierre (ORCID: 0000-0002-1936-8353)
3. Samafou, Penabei
4. Fon Mbacham, Wilfred (ORCID: 0000-0002-3934-3233)
5. Nana Engo, Serge Guy (ORCID: 0000-0002-7484-3508)

# Click "Save" (don't upload yet), copy DOI
```

### Step 2: Update Package Files

After DOI reservation:
- Update `MANIFEST.json` → `"doi_reserved": "https://doi.org/..."`
- Update `README.md` → Header section
- Update `UPLOAD_INSTRUCTIONS.md` → Replace XXXXXXX throughout

### Step 3: Verify Packages

```bash
# P2
cd Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2
sha256sum -c sha256sums.txt
du -sh .  # ~500 MB

# P5
cd Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5
sha256sum -c sha256sums.txt
du -sh .  # ~2 GB
```

### Step 4: Upload

Follow project-specific `UPLOAD_CHECKLIST.md`:
- **P2**: 2-2.5 hours total (10-30 min upload)
- **P5**: 3-4 hours total (1-2 hour upload)

### Step 5: Post-Upload

1. Verify DOIs resolve
2. Update manuscripts
3. Create git tags
4. Update AGENTS.md

---

## Key Differences: P2 vs P5

| Aspect | P2 | P5 |
|--------|----|----|
| **Package Size** | ~500 MB | ~2 GB |
| **Upload Time** | 10-30 minutes | 1-2 hours |
| **Total Time** | 2-2.5 hours | 3-4 hours |
| **Manuscript** | V2609C ready | Pre-submission |
| **Journal** | JCIM | JCAMD |
| **Focus** | MD validation, RRS | GNN/Transformer benchmark |
| **Key Finding** | Estimand divergence | Honest-negative (ECFP4 wins) |
| **Upload Strategy** | Drag-drop or ZIP | ZIP recommended |
| **Special Notes** | 16 MD systems | Extended campaign (625 configs) |

---

## What the Documents Provide

### For Each Project

1. **Complete Metadata Templates**
   - Ready to copy-paste into Zenodo
   - Title, authors, description, keywords
   - Related identifiers pre-filled

2. **Step-by-Step Instructions**
   - DOI reservation process
   - Zenodo web interface walkthrough
   - File upload options
   - Pre-publish verification
   - Post-publish actions

3. **Interactive Checklists**
   - 10-phase workflow
   - Checkbox format
   - Progress tracking
   - Timeline estimates

4. **Troubleshooting Guides**
   - Common issues
   - Solutions
   - Contact information

5. **Post-Upload Procedures**
   - Manuscript updates
   - Git tag creation
   - AGENTS.md updates
   - Verification steps

---

## Document Usage Map

### When Starting Upload Process
→ Read: `ZENODO_P2_P5_UPLOAD_PLAN.md`  
→ Use: Project-specific `UPLOAD_CHECKLIST.md`

### When Filling Zenodo Metadata
→ Reference: Project-specific `UPLOAD_INSTRUCTIONS.md`  
→ Quick lookup: `ZENODO_P2_P5_QUICK_REFERENCE.md`

### When Troubleshooting
→ Check: Project-specific `UPLOAD_INSTRUCTIONS.md` (Troubleshooting section)  
→ Log: Project-specific `UPLOAD_CHECKLIST.md` (Troubleshooting Log)

### For Quick Reference
→ Use: `ZENODO_P2_P5_QUICK_REFERENCE.md`

---

## Metadata Ready to Use

### P2 Description (Ready to Paste)
Complete reproducibility records for "Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads" submitted to JCIM. Includes: 17 Set-C candidates, docking-RRS, MD trajectories (16 systems, 10 ns), MM-GBSA, estimand divergence analysis, 39-ligand external replication, African NP chemical space profiling. Key findings: 87.5% estimand divergence, 100% Class-A external agreement, no reproducible mutant weakening in 10 ns MD.

### P5 Description (Ready to Paste)
Complete reproducibility records for "Graph neural networks and transformers for antimalarial drug discovery" submitted to JCAMD. Includes: 19,836 molecule panel, 5 GNN/Transformer architectures, random/scaffold splits, extended campaign (625 configs), external validation (22,267 ChEMBL), structural complexity analysis, topological fusion, distance-aware triage filter. Key findings: ECFP4-RF dominates (0.8300 vs GIN 0.8047), honest-negative result, 1-WL bottleneck on complex topologies, +14.2% OOD precision gain.

---

## Timeline Breakdown

### P2 Upload Timeline
- **DOI Reservation**: 10 minutes
- **Package Verification**: 15 minutes
- **Metadata Entry**: 20 minutes
- **Upload**: 10-30 minutes (~500 MB)
- **Pre-Publish Verification**: 20 minutes
- **Publish**: 5 minutes
- **Post-Publish**: 30 minutes
- **Total**: 2-2.5 hours

### P5 Upload Timeline
- **DOI Reservation**: 10 minutes
- **Package Verification**: 20 minutes
- **Metadata Entry**: 20 minutes
- **Upload**: 1-2 hours (~2 GB)
- **Pre-Publish Verification**: 30 minutes
- **Publish**: 5 minutes
- **Post-Publish**: 30 minutes
- **Total**: 3-4 hours

---

## Success Checklist

### Documentation Preparation ✅
- [x] Master planning documents created
- [x] Project-specific instructions created
- [x] Interactive checklists prepared
- [x] Quick reference guide ready
- [x] Metadata templates complete
- [x] Troubleshooting guides included

### Next Actions ⚠️
- [ ] Reserve P2 DOI on Zenodo
- [ ] Reserve P5 DOI on Zenodo
- [ ] Update P2 package files with DOI
- [ ] Update P5 package files with DOI
- [ ] Verify P2 package checksums
- [ ] Verify P5 package checksums
- [ ] Execute P2 upload
- [ ] Execute P5 upload
- [ ] Update manuscripts with DOIs
- [ ] Create git tags
- [ ] Update AGENTS.md

---

## Related Documentation

### Existing Zenodo Docs
- `ZENODO_QUICK_START.md` — General guide
- `ZENODO_PACKAGES_SUMMARY.md` — All packages overview
- `ZENODO_STATUS.md` — Status tracking

### P3 Reference (Template Used)
- `Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/`
- DOI: https://doi.org/10.5281/zenodo.19608875 (reserved)

### Project Documentation
- P2 DAR: `Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md`
- P5 DAR: `Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md`
- P2 Manuscript: V2609C (JCIM submission-ready)
- P5 Manuscript: Pre-submission development

---

## Key Contacts

- **Zenodo Support**: info@zenodo.org
- **Corresponding Author**: myke-vital.sao@facsciences-uy1.cm
- **Repository**: https://github.com/NanaEngo/Malaria_codesV2

---

## Implementation Notes

### Consistency with P3
All documentation follows the P3 template established on 2026-09-11:
- Same section structures
- Same metadata formats
- Same checklist phases
- Same upload procedures
- Adapted for project-specific content

### Project-Specific Adaptations

**P2 Adaptations:**
- MD validation focus
- Estimand divergence emphasis
- Set-C pilot systems
- ~500 MB package size
- JCIM journal specifics

**P5 Adaptations:**
- GNN/Transformer benchmark focus
- Honest-negative results emphasis
- Large file handling (~2 GB)
- Extended campaign documentation
- JCAMD journal specifics

---

## Final Notes

### Documentation is Complete
All necessary documentation for P2 and P5 Zenodo uploads has been prepared following the established P3 template. The documents are comprehensive, consistent, and ready to use immediately after DOI reservation.

### Ready for Action
The only remaining steps are:
1. Reserve DOIs on Zenodo (both projects)
2. Update package files with reserved DOIs
3. Follow the checklists to complete uploads
4. Update manuscripts and repository

### Estimated Effort
- **P2 Upload**: 2-2.5 hours (shorter due to smaller package)
- **P5 Upload**: 3-4 hours (longer due to 2 GB package)
- **Both Projects**: Can be done sequentially over 1-2 days

---

**Status**: ✅ Documentation complete and ready for use  
**Next Step**: Reserve DOIs on Zenodo  
**Created**: 2026-09-16  
**Prepared by**: Kiro AI agent
