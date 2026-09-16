# Zenodo P2 & P5 Quick Reference Guide

**Created**: 2026-09-16  
**Purpose**: Fast-access reference for P2 and P5 Zenodo uploads  
**Status**: Both DOIs need reservation

---

## At a Glance

| Item | P2 | P5 |
|------|----|----|
| **DOI Status** | ⚠️ Needs reservation | ⚠️ Needs reservation |
| **Package Size** | ~500 MB | ~2 GB |
| **Upload Time** | 10-30 minutes | 1-2 hours |
| **Manuscript Status** | V2609C ready (JCIM) | Pre-submission |
| **Package Location** | `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/` | `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/` |

---

## Quick Start Workflow

### Step 1: Reserve DOIs (Both Projects)

Go to https://zenodo.org → "New upload" → Save without uploading

#### P2 Title
```
P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads
```

#### P5 Title
```
P5 Reproducibility Package — JCAMD Submission: Graph neural networks and transformers for antimalarial drug discovery under distribution shift
```

**Authors** (both projects):
1. Sao Temgoua, Myke Vital (ORCID: 0009-0004-5170-2309)
2. Tchapet Njafa, Jean-Pierre (ORCID: 0000-0002-1936-8353)
3. Samafou, Penabei
4. Fon Mbacham, Wilfred (ORCID: 0000-0002-3934-3233)
5. Nana Engo, Serge Guy (ORCID: 0000-0002-7484-3508)

---

### Step 2: Update Package Files

After DOI reservation, update in each package:
- `MANIFEST.json` → `"doi_reserved"`
- `README.md` → Header DOI
- `UPLOAD_INSTRUCTIONS.md` → Replace XXXXXXX

---

### Step 3: Verify Packages

#### P2
```bash
cd Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2
sha256sum -c sha256sums.txt
du -sh .  # Should be ~500 MB
```

#### P5
```bash
cd Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5
sha256sum -c sha256sums.txt
du -sh .  # Should be ~2 GB
```

---

### Step 4: Upload to Zenodo

1. Go to deposit URL: `https://zenodo.org/deposit/XXXXXXX`
2. Fill all metadata (see project-specific UPLOAD_INSTRUCTIONS.md)
3. Upload files:
   - **P2**: Drag folder or ZIP (Option A or B)
   - **P5**: ZIP recommended (Option B) due to size
4. Verify uploads
5. Publish (irreversible!)

---

### Step 5: Post-Upload

1. Verify DOI resolves
2. Download and check 3-5 files
3. Update manuscript Data Availability section
4. Create git tag
5. Update AGENTS.md

---

## Key Metadata

### P2 Keywords
```
antimalarial, drug resistance, polypharmacology, molecular dynamics, docking, PfDHFR, PfCRT, resistance retention score, African natural products, Plasmodium falciparum, MD validation, MM-GBSA, GROMACS, estimand divergence, virtual screening, JCIM
```

### P5 Keywords
```
antimalarial, graph neural networks, GNN, transformers, ChemBERTa, drug discovery, distribution shift, scaffold split, African natural products, Plasmodium falciparum, ECFP4, topological data analysis, PyTorch Geometric, molecular machine learning, honest-negative results, conformal prediction, JCAMD
```

### License (Both)
Creative Commons Attribution 4.0 International (CC BY 4.0)

### Upload Type (Both)
Dataset

---

## Related Identifiers

### P2
- "is supplement to" → (manuscript DOI when assigned)
- "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1)
- "is related to" → https://doi.org/10.5281/zenodo.19608875 (P3)

### P5
- "is supplement to" → (manuscript DOI when assigned)
- "is related to" → https://doi.org/10.5281/zenodo.19608875 (P3)
- "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1)

---

## Key Findings Summary

### P2
- 87.5% estimand divergence (static docking vs short MD)
- 39-ligand external replication: 100% Class-A agreement
- African NP: Fsp3=0.22, QED=0.70, MPO=0.728
- No mutant shows reproducible weakening in 10 ns MD
- Docking-RRS as positive triage filter

### P5
- ECFP4-RF dominates: 0.8300 vs GIN 0.8047 (scaffold split)
- Honest-negative: GNNs don't outperform classical fingerprints
- 1-WL bottleneck on complex topologies (Fsp3 ≥0.45, rings ≥4)
- TFP fusion: +0.0091 AUC modest gain
- Distance-aware triage: +14.2% OOD precision
- Performance ordering invariant across splits

---

## File Counts

### P2 Package Structure
```
zenodo_package_P2/
├── data/          (RRS, PNS, ACSI, trajectory metrics)
├── results/       (MD-RRS, MM-GBSA, external replication)
├── scripts/       (audit, QC, analysis pipelines)
└── documentation/ (DAR, methods, justifications)
```

### P5 Package Structure
```
zenodo_package_P5/
├── data/          (19,836 panel + ChEMBL disjoint)
├── results/       (canonical benchmarks + extended campaign)
├── scripts/       (GNN, ChemBERTa, fusion pipelines)
└── documentation/ (DAR, methods, ADR strategic pivot)
```

---

## Git Commands

### After Upload Complete

```bash
cd ~/Documents/GitHub/Malaria_codesV2

# P2
git tag -a p2-jcim-submission -m "P2 JCIM V2609C with Zenodo DOI 10.5281/zenodo.XXXXXXX"
git push origin p2-jcim-submission

# P5
git tag -a p5-jcamd-submission -m "P5 JCAMD with Zenodo DOI 10.5281/zenodo.XXXXXXX"
git push origin p5-jcamd-submission
```

---

## Manuscript Updates

### P2 (V2609C)
File: `Project2_Polypharmacology_MD_ValidationV2607/manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`

```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

### P5 (When Finalized)
File: `Project5_GNN_Transformer_DrugDiscovery_V2609/manuscript/[VERSION]/[FILE].tex`

```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

---

## Detailed Documentation

| Document | Location |
|----------|----------|
| **Master Upload Plan** | `ZENODO_P2_P5_UPLOAD_PLAN.md` |
| **P2 Upload Instructions** | `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/UPLOAD_INSTRUCTIONS.md` |
| **P2 Upload Checklist** | `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/UPLOAD_CHECKLIST.md` |
| **P5 Upload Instructions** | `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/UPLOAD_INSTRUCTIONS.md` |
| **P5 Upload Checklist** | `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/UPLOAD_CHECKLIST.md` |
| **P3 Reference** | `Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/UPLOAD_INSTRUCTIONS.md` |

---

## Common Issues & Solutions

### Upload Timeout (Especially P5)
- **Solution**: Use ZIP upload (Option B)
- Upload during off-peak hours
- Check internet connection stability

### Large File Size (P5: 2GB)
- **Solution**: Create ZIP before upload
- Consider uploading subdirectories separately
- Zenodo limit: 50 GB per deposit (plenty of room)

### Checksums Don't Match
- **Solution**: Download raw files, not ZIP preview
- Verify file extraction if uploaded as ZIP
- Re-download and try again

### DOI Doesn't Resolve
- **Solution**: Wait 10-15 minutes for propagation
- Check deposit page directly
- Contact: info@zenodo.org

---

## Contact Information

- **Zenodo Support**: info@zenodo.org
- **Corresponding Author**: myke-vital.sao@facsciences-uy1.cm
- **Repository**: https://github.com/NanaEngo/Malaria_codesV2

---

## Checklist Overview

### Pre-Upload
- [ ] Both DOIs reserved
- [ ] All package metadata updated
- [ ] Checksums verified locally
- [ ] Package structures complete

### Upload
- [ ] P2 uploaded and published
- [ ] P5 uploaded and published
- [ ] Both DOIs resolve

### Post-Upload
- [ ] Manuscripts updated (P2 now, P5 when ready)
- [ ] Git tags created and pushed
- [ ] AGENTS.md updated
- [ ] Verification downloads complete

---

## Timeline Estimates

| Phase | P2 | P5 |
|-------|----|----|
| DOI Reservation | 10 min | 10 min |
| Package Verification | 15 min | 20 min |
| Metadata Entry | 20 min | 20 min |
| Upload | 10-30 min | 1-2 hours |
| Pre-Publish Checks | 20 min | 30 min |
| Publish | 5 min | 5 min |
| Post-Publish | 30 min | 30 min |
| **Total** | **2-2.5 hours** | **3-4 hours** |

---

## Success Criteria

### For Each Project
✅ DOI reserved and recorded  
✅ All metadata complete and accurate  
✅ All files uploaded successfully  
✅ Checksums verified post-upload  
✅ DOI resolves correctly  
✅ README renders properly  
✅ Manuscript updated with DOI  
✅ Git tag created and pushed  
✅ AGENTS.md updated  

---

**Last updated**: 2026-09-16  
**Prepared by**: Kiro AI agent  
**Model**: Following P3 Zenodo template
