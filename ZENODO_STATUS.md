# Zenodo Deposits Status — P1, P3, P4, P5

**Last updated**: 2026-09-11  
**Purpose**: Track Zenodo reproducibility deposits across all projects

---

## Status Overview

| Project | Journal | Manuscript Status | Zenodo DOI | Package Status |
|---------|---------|-------------------|------------|----------------|
| **P1** | JCIM | V8 revision ready (2026-09-09) | [10.5281/zenodo.22686176](https://doi.org/10.5281/zenodo.22686176) | ✅ **Ready for upload** |
| **P3** | JCAMD | Submitted (2026-08-30) | [10.5281/zenodo.19608875](https://doi.org/10.5281/zenodo.19608875) | ✅ **Structured** (2026-09-11) |
| **P4** | JCAMD | Submitted (2026-08-30) | ⚠️ **Needs reservation** | ✅ **Structured** (2026-09-11) |
| **P5** | JCAMD | Pre-submission development | ⚠️ **Needs reservation** | ✅ **Structured** (2026-09-11) |

---

## P1 — Chemical Space & Polypharmacology

**Status**: ✅ V8 package complete, ready for upload  
**Location**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/zenodo_package_P1/`  
**DOI**: https://doi.org/10.5281/zenodo.22686176 (reserved)  
**Files**: 218 files, ~4.4 MB  
**Key result**: 17 candidates with RRS profiles, DEKOIS validation, PfCRT correction

**Next action**: Upload to Zenodo (author decision pending)

---

## P3 — Quantum-Inspired Representations

**Status**: ✅ Package structure created (2026-09-11)  
**Location**: `Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/`  
**DOI**: https://doi.org/10.5281/zenodo.19608875 (reserved)  
**Key result**: No quantum-inspired method outperforms ECFP4 (honest-negative)

### Prepared Files
- ✅ README.md (complete usage guide)
- ✅ MANIFEST.json (structured metadata)
- ✅ UPLOAD_INSTRUCTIONS.md (step-by-step)
- ✅ Package directory structure created

### Files to Collect (via build script)
- [ ] Data: `p3_labels_production.csv`, `p3_tda_fingerprints.csv`, `p3_tne_embeddings.csv`
- [ ] Results: benchmarks, external validation, regression analyses
- [ ] Scripts: TDA, TNE, QKS pipelines
- [ ] Documentation: P3 DAR

**Next action**: Run build script, verify checksums, upload to Zenodo

---

## P4 — Pareto-Guided MCTS

**Status**: ✅ Package structure created (2026-09-11)  
**Location**: `Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4/`  
**DOI**: ⚠️ **Needs Zenodo reservation**  
**Key result**: MCTS does not beat Random (honest-negative), Pareto provides trade-offs

### Prepared Files
- ✅ README.md (complete usage guide)
- ✅ MANIFEST.json (structured metadata)
- ⚠️ UPLOAD_INSTRUCTIONS.md (needs DOI update after reservation)
- ✅ Package directory structure created

### Files to Collect (via build script)
- [ ] Data: Fragment libraries, ScafVAE vocabulary, oracle specs
- [ ] Results: v12 benchmark (20 seeds), Pareto front, ablation study
- [ ] Scripts: MCTS agent, policy, oracles, benchmarks
- [ ] Documentation: P4 DAR

**Next action**: Reserve DOI on Zenodo, update MANIFEST/README, run build script

---

## P5 — GNN/Transformer Benchmark

**Status**: ✅ Package structure created (2026-09-11)  
**Location**: `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/`  
**DOI**: ⚠️ **Needs Zenodo reservation**  
**Key result**: ECFP4-RF outperforms GNN/Transformer under scaffold split (honest-negative)

### Prepared Files
- ✅ README.md (complete usage guide)
- ⚠️ MANIFEST.json (to be created)
- ⚠️ UPLOAD_INSTRUCTIONS.md (to be created)
- ✅ Package directory structure created

### Files to Collect (via build script)
- [ ] Data: 19,836-molecule panel, splits, graph cache
- [ ] Results: Extended campaign (625 records), NN-Tanimoto deciles, Butina split, calibration
- [ ] Scripts: GNN training, ChemBERTa, baselines
- [ ] Documentation: P5 DAR

**Next action**: Reserve DOI, complete MANIFEST/UPLOAD_INSTRUCTIONS, run build script

---

## Build Workflow

### Step 1: Reserve DOIs (P4 & P5)
```bash
# Go to https://zenodo.org
# Create new uploads for P4 and P5
# Reserve DOIs without uploading files
# Copy DOIs to MANIFEST.json and README.md
```

### Step 2: Run Build Script
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2
bash scripts/build_zenodo_packages_batch.sh
```

### Step 3: Verify Packages
```bash
# Check each package
cd Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3
sha256sum -c sha256sums.txt

cd ../../Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4
sha256sum -c sha256sums.txt

cd ../../Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5
sha256sum -c sha256sums.txt
```

### Step 4: Upload to Zenodo
Follow `UPLOAD_INSTRUCTIONS.md` in each package

---

## Honest-Negative Results (Scientific Value)

All three new packages report honest-negative findings that advance the field:

### P3: Quantum-Inspired Methods
- **Finding**: No quantum-inspired representation (TFP, TNE, QKS) outperforms classical ECFP4
- **Value**: Establishes methodological boundaries for quantum-inspired approaches
- **Evidence**: 5-fold CV, external ChEMBL validation, multiple representation tests

### P4: MCTS Optimization
- **Finding**: MCTS does not beat Random exploration in scalar reward (0.6649 vs 0.6724, p<0.001)
- **Value**: Questions MCTS advantage in flat reward landscapes
- **Evidence**: 20-seed benchmark with paired statistical tests

### P5: Deep Learning Models
- **Finding**: ECFP4-RF outperforms GNN/Transformer under scaffold split (0.8300 vs best 0.8138)
- **Value**: Identifies when classical methods remain competitive despite architectural complexity
- **Evidence**: NN-Tanimoto decile analysis shows gap driven by novel molecules

**All three are publication-worthy findings** that provide evidence-based guidance to the research community.

---

## Common Metadata (All Projects)

**Authors** (same order for all):
1. Sao Temgoua, Myke Vital → ORCID: 0009-0004-5170-2309
2. Tchapet Njafa, Jean-Pierre → ORCID: 0000-0002-1936-8353
3. Samafou, Penabei → (no ORCID)
4. Fon Mbacham, Wilfred → ORCID: 0000-0002-3934-3233
5. Nana Engo, Serge Guy → ORCID: 0000-0002-7484-3508

**License**: CC BY 4.0 International  
**Institution**: Department of Physics, Faculty of Science, University of Yaoundé I, Cameroon  
**Corresponding author**: myke-vital.sao@facsciences-uy1.cm

---

## Documentation Created (2026-09-11)

### Build infrastructure
- ✅ `scripts/build_zenodo_packages_batch.sh` — Automated package builder
- ✅ `ZENODO_PACKAGES_SUMMARY.md` — Detailed overview of all three packages
- ✅ `ZENODO_QUICK_START.md` — Quick reference guide
- ✅ `ZENODO_STATUS.md` — This file (status tracker)

### Per-project files
- ✅ P3: README, MANIFEST, UPLOAD_INSTRUCTIONS
- ✅ P4: README, MANIFEST, (UPLOAD_INSTRUCTIONS needs DOI)
- ✅ P5: README, (MANIFEST and UPLOAD_INSTRUCTIONS to be completed)

---

## Timeline

| Date | Action | Status |
|------|--------|--------|
| 2026-08-30 | P3, P4 submitted to JCAMD | ✅ Complete |
| 2026-09-09 | P1 V8 revision completed | ✅ Complete |
| 2026-09-11 | P3, P4, P5 Zenodo packages structured | ✅ Complete |
| **Next** | Reserve DOIs for P4, P5 | ⏳ Pending |
| **Next** | Run build script for all three | ⏳ Pending |
| **Next** | Upload to Zenodo | ⏳ Pending |
| **Next** | Update manuscripts with DOIs | ⏳ Pending |
| **Next** | Make GitHub repository public | ⏳ Pending |

---

## Support Resources

- **Detailed overview**: `ZENODO_PACKAGES_SUMMARY.md`
- **Quick start**: `ZENODO_QUICK_START.md`
- **P1 reference**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/zenodo_package_P1/`
- **Build script**: `scripts/build_zenodo_packages_batch.sh`
- **Zenodo help**: info@zenodo.org

---

**Prepared by**: Kiro AI agent  
**Following**: P1 V8 Zenodo template structure
