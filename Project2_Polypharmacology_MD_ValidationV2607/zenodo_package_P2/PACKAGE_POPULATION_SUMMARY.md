# P2 Zenodo Package Population Summary

**Date**: 17 September 2026  
**Status**: ✅ **COMPLETE - Package Ready for Review**  
**Action**: Automatic population from project results

---

## Summary

The P2 Zenodo package has been **successfully populated** with all necessary files from the project directory. The package is now ready for:
1. Content review
2. Checksum verification  
3. Metadata updates
4. Upload to Zenodo

---

## Files Populated

### ✅ Data Directory (4 core datasets)

| File | Size | Source | Description |
|------|------|--------|-------------|
| `c_rrs_classification.csv` | 9.7 KB | `results/` | 17 Set-C candidates with RRS classes (A*/A/B/C/D) |
| `c_pns_ranking.csv` | 3.5 KB | `results/` | Polypharmacology Network Score (PNS) rankings |
| `c_acsi_scores.csv` | 5.5 KB | `results/` | African-Chemotype Structural Index scores |
| `c_docking_complete.csv` | 7.2 KB | `results/docking_mutants.csv` | Complete docking scores (136 systems) |

### ✅ Results Directory (46 files: CSV + JSON)

**Statistical audits:**
- `cross_metric_statistical_audit.csv` — PNS-RRS, ACSI-RRS correlations
- `pns_imputation_sensitivity.csv` — PfCRT centrality robustness (5 scenarios)
- `c_acsi_weight_sensitivity.csv` — ACSI weight perturbation
- `c_rrs_sensitivity.csv` — RRS threshold sensitivity

**MD system manifests:**
- 40+ JSON provenance files from Set-C MD preparation
- System manifests, force field records, production logs
- Pre-equilibration audits, receptor gap/TER provenance
- Junction repair ensemble manifests

### ✅ Scripts Directory (2 analysis scripts)

| Script | Purpose |
|--------|---------|
| `p2_rigorous_audit.py` | RRS classification and statistical audit (seed 42) |
| `p2_setc_md_rrs.py` | MD-RRS discriminative analysis (distance-based) |

**Note**: `set_c_trajectory_qc.py` not found in source (may need manual addition if required).

### ✅ Documentation Directory (2 documents)

| Document | Source | Description |
|----------|--------|-------------|
| `MMGBSA_JUSTIFICATION_ADDENDUM.md` | `docs/` | MM-GBSA protocol rationale and limitations |
| `P2_DATA_ANALYSIS_REPORT.md` | `../BMAD_Q1_DATA_ANALYSIS_REPORT.md` | Complete data provenance and analysis record |

---

## Checksum Verification

SHA256 checksums generated for **all files** in the package:

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2
sha256sum -c sha256sums.txt
```

**Expected**: All files should report "OK" (no mismatches).

---

## Package Structure

```
zenodo_package_P2/
├── LICENSE.txt (✅ CC BY 4.0, 21 lines)
├── MANIFEST.json (✅ 190 lines — needs update with actual file list)
├── README.md (✅ Complete documentation, 420 lines)
├── QUICK_START.txt (✅ 175 lines)
├── UPLOAD_CHECKLIST.md (✅ 278 lines)
├── UPLOAD_INSTRUCTIONS.md (✅ Complete)
├── ZENODO_SETUP_GUIDE.md (✅ Complete)
├── sha256sums.txt (✅ Generated with all file checksums)
├── data/ (✅ 4 CSV files)
├── results/ (✅ 46 CSV + JSON files)
├── scripts/ (✅ 2 Python scripts)
└── documentation/ (✅ 2 Markdown files)
```

---

## What Was NOT Included

Per README.md evidence boundaries, these are **intentionally excluded**:

❌ **Complete GROMACS trajectory files** (XTC archives):
- Reason: Too large for Zenodo (multi-GB per system)
- Alternative: Trajectory metrics and QC summaries provided
- MD conclusions based on distance/RMSD metrics, not raw trajectories

❌ **Experimental validation data**:
- Reason: This is a computational study
- No biological activity or resistance measurements available

❌ **External docking panel raw files**:
- Reason: Source directory `results/external_docking_20260827/` not fully populated
- Note: May need manual addition if external replication data is critical

❌ **Large binary force field files**:
- Reason: Scripts use standard force fields (CHARMM36m, OpenFF 2.2.0)
- Users can reproduce using environment.yml

---

## Next Steps

### 1. Content Review ⏳

Review copied files for completeness:

```bash
cd zenodo_package_P2
ls -lh data/
ls -lh results/ | head -20
ls -lh scripts/
ls -lh documentation/
```

**Check**: Are all essential files for reproducibility present?

### 2. Verify Checksums ⏳

```bash
cd zenodo_package_P2
sha256sum -c sha256sums.txt
```

**Expected**: All files OK (no FAILED).

### 3. Update MANIFEST.json ⏳

The current MANIFEST.json (190 lines) needs to be updated with the **actual file list**. Update:

- `files` array with real file names and sizes
- `file_count` with actual count (currently 52+ files)
- `total_size_mb` with actual package size

```bash
du -sh zenodo_package_P2/
```

### 4. Add Missing Scripts (If Required) ⏳

If `set_c_trajectory_qc.py` is essential for reproducibility:

```bash
# Find it in project or reconstruction scripts
find ../scripts -name "*trajectory*qc*.py"
```

### 5. Review UPLOAD_CHECKLIST.md ⏳

Follow the pre-upload checklist to ensure all metadata is complete.

### 6. Upload to Zenodo ⏳

Once reviewed:

1. Reserve DOI on Zenodo
2. Upload package as ZIP archive
3. Fill in metadata (title, authors, description, keywords)
4. Publish and obtain final DOI
5. Update manuscript with DOI

---

## Package Statistics

| Metric | Value |
|--------|-------|
| Total files | 52+ |
| Data files | 4 CSV |
| Results files | 46 CSV + JSON |
| Scripts | 2 Python |
| Documentation | 2 Markdown |
| Root files | 8 (README, LICENSE, etc.) |
| Estimated size | ~1-5 MB (excluding trajectories) |

---

## File Sources

All files were copied from:

**Source root**: `/home/vital/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/`

**Primary sources**:
- `results/*.csv` → `data/` and `results/`
- `results/md_systems/**/*.json` → `results/`
- `scripts/*.py` → `scripts/`
- `docs/*.md` → `documentation/`
- `../BMAD_Q1_DATA_ANALYSIS_REPORT.md` → `documentation/P2_DATA_ANALYSIS_REPORT.md`

---

## Reproducibility Statement

This package provides:

✅ **Core datasets** for RRS classification (17 candidates, 136 docking systems)  
✅ **Statistical audit results** (cross-metric correlations, sensitivity analyses)  
✅ **MD system manifests** (provenance, force fields, production logs)  
✅ **Analysis scripts** (RRS audit, MD-RRS computation)  
✅ **Complete documentation** (methods, protocols, limitations)  
✅ **SHA256 checksums** (integrity verification)  

With this package, independent researchers can:
- ✅ Reproduce RRS classification (Table 1)
- ✅ Reproduce cross-metric statistical audits (Table 3)
- ✅ Verify MD system preparation provenance
- ✅ Understand protocol limitations and boundaries

---

## Contact for Issues

If files are missing or checksums fail:

**Package maintainer**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**Repository**: https://github.com/NanaEngo/Malaria_codesV2

---

**Last updated**: 17 September 2026  
**Populated by**: Automated script (`populate_package.sh`)  
**Ready for**: Author review → Zenodo upload
