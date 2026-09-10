# P1 V8 Zenodo Package — Complete Summary

**Date prepared**: 2026-09-10  
**Location**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/zenodo_package_P1/`  
**Reserved DOI**: https://doi.org/10.5281/zenodo.22686176  
**Status**: ✅ **READY TO UPLOAD** (staged, verified, checksummed)

---

## Package Overview

| Metric | Value |
|--------|-------|
| **Total files** | 218 files + 1 checksum manifest |
| **Total size** | 4.4 MB |
| **License** | CC BY 4.0 International |
| **Checksum algorithm** | SHA-256 |
| **Status** | Staged locally, pending Zenodo upload |

---

## Directory Structure

```
zenodo_package_P1/
├── README.md                    # 406-line comprehensive usage guide
├── MANIFEST.json                # Machine-readable package metadata
├── LICENSE.txt                  # CC BY 4.0 full legal text
├── sha256sums.txt               # 218 file checksums
├── UPLOAD_INSTRUCTIONS.md       # Step-by-step Zenodo upload guide
│
├── data/                        # 3 files — Core datasets
│   ├── v7_candidate_manifest.csv
│   ├── v7_integrated_candidate_metrics.csv
│   └── SI_Table_SNEW5_polypharmacology_metrics.csv
│
├── results/                     # 202 files — Revision analyses
│   ├── pfcrt_redock_v2grid_20260909/         (R2.3)
│   ├── retrospective_approved_antimalarials_20260909/  (R1.2)
│   └── dekois_mtxstripped_20260909/          (R2.4)
│
├── scripts/                     # 8 files — Analysis code
│   ├── p1_r12_retrospective.py
│   ├── p1_r23_pfcrt_redock.py
│   ├── p1_r23_rrs_recompute.py
│   ├── p1_r24_dekois_mtxstripped.py
│   ├── p1_r24_analyze.py
│   ├── p1_statistical_audit.py
│   ├── v8_figure2_annotations.py
│   └── launch_r24.sh
│
└── documentation/               # 3 files — Supporting docs
    ├── P1_DATA_ANALYSIS_REPORT.md
    ├── SUBMISSION_MANIFEST_V8.md
    └── Response_to_Reviewers_V8_Summary.md
```

---

## What This Package Contains

### Core Datasets (`data/`)

1. **`v7_candidate_manifest.csv`** — 17-member cohort
   - SMILES strings (canonical, RDKit-generated)
   - MPO scores, molecular properties
   - Source (African NP-inspired hybrid library)

2. **`v7_integrated_candidate_metrics.csv`** — RRS profiles
   - Per-target RRS values (PfDHFR, PfCRT, PfClpP, PfATP4)
   - RRS_mean classification (A*, B, C)
   - PNS, ACSI, N_fav metrics

3. **`SI_Table_SNEW5_polypharmacology_metrics.csv`** — Polypharmacology summary
   - Target breadth and favorability counts
   - Cross-metric correlations

### Revision Results (`results/`)

#### 1. PfCRT Re-Docking (R2.3)
**Directory**: `pfcrt_redock_v2grid_20260909/`
- **Why**: Original submission used misassigned PfCRT structure
- **What**: Re-docked all 17 candidates on corrected 3D7-like WT (6UKJ)
- **Result**: Updated RRS values, 7 A* / 4 B / 6 C classification unchanged
- **Files**: Corrected receptor PDB, revised scores, updated manifest

#### 2. Retrospective Control (R1.2)
**Directory**: `retrospective_approved_antimalarials_20260909/`
- **Why**: Reviewer requested positive-control validation
- **What**: Ran 5 approved antimalarials (artemisinin, pyrimethamine, chloroquine, lumefantrine, cipargamin) through same pipeline
- **Result**: **Honest-negative** — pipeline does not recover clinical resistance signatures
  - Pyrimethamine: ≈100% RRS on all 4 PfDHFR mutants (clinically resistant)
  - Chloroquine: ≈99% RRS on PfCRT K76T/K76A (clinically resistant)
- **Implication**: Docking-RRS values are prioritization hypotheses, not resistance-circumvention evidence
- **Files**: RRS profiles by drug, docking outputs, interpretation README

#### 3. DEKOIS 2.0 Validation (R2.4)
**Directory**: `dekois_mtxstripped_20260909/`
- **Why**: Reviewer requested external benchmark
- **What**: Two-arm comparison (MTX-retained vs MTX-stripped) on PfDHFR
- **Result**: **Honest-negative** — near-chance discrimination
  - MTX-retained: ROC-AUC 0.502 [0.437, 0.567]
  - MTX-stripped: ROC-AUC 0.563 [0.498, 0.628]
  - Overlapping 95% CIs → no MTX-dependent enrichment
- **Implication**: AutoDock Vina scores are target-specific ranking, not calibrated affinity predictions
- **Files**: Active/decoy scores (retained and stripped), ROC analysis, interpretation README

### Analysis Scripts (`scripts/`)

All scripts are **Python 3.11+** with **conda environment `malaria_md`**:

| Script | Purpose | Reviewer Point |
|--------|---------|----------------|
| `p1_r12_retrospective.py` | Retrospective approved drugs | R1.2 |
| `p1_r23_pfcrt_redock.py` | PfCRT re-docking | R2.3 |
| `p1_r23_rrs_recompute.py` | RRS recalculation | R2.3 |
| `p1_r24_dekois_mtxstripped.py` | DEKOIS two-arm benchmark | R2.4 |
| `p1_r24_analyze.py` | ROC analysis | R2.4 |
| `p1_statistical_audit.py` | Spearman + multiplicity correction | R2.7 |
| `v8_figure2_annotations.py` | Figure 2 mutation annotations | Manuscript |
| `launch_r24.sh` | AutoDock Vina launcher | R2.4 |

### Documentation (`documentation/`)

1. **`P1_DATA_ANALYSIS_REPORT.md`** — Complete provenance record
2. **`SUBMISSION_MANIFEST_V8.md`** — V8 submission file inventory
3. **`Response_to_Reviewers_V8_Summary.md`** — Executive summary of all 18 responses

---

## Reviewer Items Addressed

This package resolves **R2.6** (repository release + archival DOI) and supports all other reviewer responses:

| Point | Requirement | Status |
|-------|-------------|--------|
| **R1.1** | PNS/ACSI definitions | ✅ Added to Methods + SM Table S5 |
| **R1.2** | Retrospective control | ✅ **In this package** (5 approved drugs, honest-negative) |
| **R2.1** | Workflow clarification | ✅ SI Scheme S1 + expanded Methods |
| **R2.2** | Favorability definition | ✅ Defined + boundary sensitivity |
| **R2.3** | PfCRT correction | ✅ **In this package** (re-docking complete) |
| **R2.4** | DEKOIS validation | ✅ **In this package** (two-arm, honest-negative) |
| **R2.5** | MMV interpretation | ✅ Relabelled "retrodictive consistency" |
| **R2.6** | Repository + DOI | ✅ **This entire package** |
| **R2.7** | Multiplicity correction | ✅ Holm-Bonferroni applied, 3/4 significant |
| **R2.8** | Redocking table split | ✅ Full-ligand vs fragment/cofactor |
| **R2.9** | Multi-seed sensitivity | ✅ 5-seed runs, spread <0.06 kcal/mol |
| **R2.10** | C59R claim removed | ✅ Fold-change claim deleted |
| **R2.11** | Grid specifications | ✅ Complete coords in SM Table S1 |
| **R2.12** | 9N10 clarification | ✅ Peptide pose only, no small-molecule |
| **R2.13** | Cost metric caveat | ✅ Efficiency, not retention rate |
| **R2.14** | Physicochemical tables | ✅ 3 new tables (Lipinski, QED, ADMET) |
| **R2.15** | RRS formula consistency | ✅ Unified definition Methods §2.6 |
| **R2.16** | DOI insertion | ✅ Already in Main + SM + Response |

**Total**: 18/18 resolved ✅

---

## Honest-Negative Results

Two major analyses produced **transparent null results**, both included in this package:

### 1. DEKOIS 2.0 External Validation
- **Result**: ROC-AUC ≈ 0.5 (chance-level)
- **Interpretation**: AutoDock Vina on PfDHFR does not generalize to external actives/decoys
- **Implication**: Docking scores are target-specific prioritization, not calibrated activity predictions
- **Why included**: Establishes honest evidence boundaries

### 2. Retrospective Approved Drugs
- **Result**: Pipeline does not recover clinical resistance signatures
  - Pyrimethamine: high RRS on resistant mutants (should be low)
  - Chloroquine: high RRS on resistant mutants (should be low)
- **Interpretation**: Docking-RRS is not resistance-circumvention evidence
- **Implication**: Computational profiles require wet-lab validation
- **Why included**: Prevents overinterpretation of candidate RRS values

**Both results strengthen methodological transparency and are essential for evidence-boundary clarity.**

---

## Software Requirements

To reproduce analyses from this package:

### Conda Environment
```bash
conda create -n malaria_md python=3.11
conda activate malaria_md
conda install -c conda-forge rdkit numpy pandas scipy matplotlib scikit-learn
```

### Key Versions
- Python: 3.11+
- RDKit: 2025.03.6
- NumPy: 2.2.1
- pandas: 2.2.3
- SciPy: 1.15.1
- matplotlib: 3.10.1
- scikit-learn: 1.6.1
- AutoDock Vina: 1.2.5

### External Tools
- **AutoDock Vina 1.2.5**: https://vina.scripps.edu/
- **Open Babel** (optional, for format conversions): http://openbabel.org/

---

## Upload Status

### ✅ Completed Locally

- [x] All files copied to `zenodo_package_P1/`
- [x] SHA-256 checksums generated (`sha256sums.txt`)
- [x] README.md comprehensive guide written (406 lines)
- [x] MANIFEST.json machine-readable metadata created
- [x] LICENSE.txt (CC BY 4.0) included
- [x] UPLOAD_INSTRUCTIONS.md step-by-step guide written
- [x] Documentation complete (DAR, submission manifest, reviewer summary)
- [x] Package verified: 218 files, 4.4 MB, all checksums OK

### ⏳ Pending Actions (Author)

- [ ] Upload package to Zenodo deposit 22686176
- [ ] Verify post-upload file integrity (download + checksum spot-check)
- [ ] Publish Zenodo deposit (makes DOI active)
- [ ] Confirm DOI resolves: https://doi.org/10.5281/zenodo.22686176
- [ ] Make GitHub repository public (after DOI verification)
- [ ] Create GitHub release tag: `v8-jcim-resubmission`

### ✅ Already Done (Manuscript)

- [x] DOI inserted in Main Data Availability section
- [x] DOI inserted in SM Reproducibility section
- [x] DOI referenced in Response to Reviewers R2.6
- [x] No manuscript changes needed after Zenodo upload

---

## Citation

Once published, cite as:

**Dataset**:
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. (2026). P1 V8 Reproducibility Package — JCIM Revision 
[Data set]. Zenodo. https://doi.org/10.5281/zenodo.22686176
```

**Manuscript** (when published):
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. Target breadth and mutation resilience in 
African-natural-product-inspired antimalarial chemotypes: a computational 
analysis. J. Chem. Inf. Model. 2026, XX, XXXX–XXXX. 
DOI: [to be assigned]
```

---

## Quick Start

### Verify Package Integrity

```bash
cd Project1_Chem_space_antimalarial_V7_CorrectedGrid/zenodo_package_P1
sha256sum -c sha256sums.txt
# Expected: All OK
```

### Upload to Zenodo

Follow detailed instructions in `UPLOAD_INSTRUCTIONS.md`.

**Quick summary**:
1. Go to https://zenodo.org/deposit/22686176
2. Fill metadata (title, authors with ORCIDs, keywords, license CC BY 4.0)
3. Upload all files (drag-and-drop or ZIP)
4. Verify upload integrity
5. Publish (makes DOI active)
6. Confirm DOI resolves
7. Make GitHub repository public

---

## Contact

**Corresponding author**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**ORCID**: 0009-0004-5170-2309  
**Institution**: University of Yaoundé I, Cameroon

**For Zenodo upload issues**: info@zenodo.org

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| **This summary** | `ZENODO_PACKAGE_SUMMARY.md` | Overview of complete package |
| **Upload guide** | `zenodo_package_P1/UPLOAD_INSTRUCTIONS.md` | Step-by-step Zenodo instructions |
| **Package README** | `zenodo_package_P1/README.md` | Comprehensive usage guide (for Zenodo users) |
| **Manifest** | `zenodo_package_P1/MANIFEST.json` | Machine-readable metadata |
| **Checksums** | `zenodo_package_P1/sha256sums.txt` | File integrity verification |
| **Cover letter** | `submission_ACS_P1V8/Cover_Letter_P1_V8.pdf` | Mentions DOI + rapid response |
| **Response doc** | `submission_ACS_P1V8/Response_to_Reviewers_P1_V8.pdf` | All 18 points addressed |
| **Submission checklist** | `submission_ACS_P1V8/FINAL_SUBMISSION_CHECKLIST.md` | Pre-JCIM-upload verification |

---

**Last updated**: 2026-09-10T18:48 UTC+01:00  
**Prepared by**: Kiro AI agent (on behalf of MVST)  
**Package status**: ✅ READY TO UPLOAD
