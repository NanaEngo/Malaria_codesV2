# P1 V8 Reproducibility Package — JCIM Revision

**DOI**: https://doi.org/10.5281/zenodo.22686176  
**License**: CC BY 4.0  
**Manuscript**: "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis"  
**Journal**: *Journal of Chemical Information and Modeling*  
**Version**: V8 (revision resubmission, 2026-09-10)  
**Original Manuscript ID**: ci-2026-00578g

---

## Purpose

This deposit provides complete reproducibility records for the V8 revision, addressing Reviewer R2.6's request for:
- Maintained repository with license and release tag
- Archival DOI for data availability
- All wild-type denominators and raw docking outputs
- Machine-readable candidate tables
- Complete protocol specifications

All files are sha256-verified. The checksum manifest is in `sha256sums.txt`.

---

## Contents

### 1. `data/` — Core datasets

| File | Description |
|------|-------------|
| `v7_candidate_manifest.csv` | 17-member cohort with SMILES, MPO scores, properties |
| `v7_integrated_candidate_metrics.csv` | RRS profiles, PNS, ACSI, N_fav for all 17 candidates |
| `wt_mutant_scores_complete.csv` | Wild-type and mutant docking scores (68 candidate–target pairs, 6 PfDHFR + 3 PfCRT mutants) |
| `SI_Table_SNEW5_polypharmacology_metrics.csv` | Polypharmacology summary metrics |

### 2. `results/` — Revision analyses

#### `pfcrt_redock_v2grid_20260909/`
Response to R2.3 — PfCRT re-docking with corrected wild-type receptor.
- `manifest.json` — protocol specifications
- `revised_rrs_and_nfav.csv` — updated RRS and N_fav counts
- Output poses and affinity table

#### `retrospective_approved_antimalarials_20260909/`
Response to R1.2 — retrospective honest-negative control using 5 approved antimalarials.
- `rrs_profiles.csv` — RRS values for artemisinin, pyrimethamine, chloroquine, lumefantrine, cipargamin
- `README.md` — interpretation (pipeline does not recover clinical resistance signatures)
- Docking outputs by drug and target

#### `dekois_mtxstripped_20260909/`
Response to R2.4 — DEKOIS 2.0 external validation, two-arm comparison.
- `analysis_summary.json` — ROC-AUC for MTX-retained (0.502) vs MTX-stripped (0.563)
- `dekois_pfdhfr_retained.csv` — MTX-retained active/decoy scores
- `dekois_pfdhfr_stripped.csv` — MTX-stripped active/decoy scores
- `README.md` — interpretation (near-chance, overlapping CIs → no MTX support)

### 3. `scripts/` — Analysis code

| Script | Purpose |
|--------|---------|
| `p1_r12_retrospective.py` | Retrospective control (R1.2) |
| `p1_r23_pfcrt_redock.py` | PfCRT re-docking (R2.3) |
| `p1_r23_rrs_recompute.py` | RRS recalculation after PfCRT correction |
| `p1_r24_dekois_mtxstripped.py` | DEKOIS two-arm benchmark (R2.4) |
| `p1_r24_analyze.py` | ROC analysis for DEKOIS results |
| `launch_r24.sh` | AutoDock Vina launcher for DEKOIS runs |
| `v8_figure2_annotations.py` | Figure 2 mutation profile annotations |
| `p1_statistical_audit.py` | Spearman correlation + multiplicity correction |

All scripts are Python 3.11+ with conda environment `malaria_md` (RDKit 2025.03, numpy, pandas, scipy, matplotlib).

### 4. `documentation/` — Supporting documents

| File | Description |
|------|-------------|
| `P1_DATA_ANALYSIS_REPORT.md` | Complete data provenance and analysis record |
| `SUBMISSION_MANIFEST_V8.md` | V8 submission file inventory |
| `Response_to_Reviewers_V8_Summary.md` | Executive summary of all 18 reviewer responses |
| `LICENSE.txt` | CC BY 4.0 license text |

---

## How to Use This Deposit

### Verify Integrity

Before using any data, verify the checksums:

```bash
cd zenodo_package_P1
sha256sum -c sha256sums.txt
```

**Expected output**: All files OK (no mismatches).

### Reproduce Key Results

#### 1. Verify PfCRT RRS recalculation (R2.3)

```bash
cd results/pfcrt_redock_v2grid_20260909
python ../../scripts/p1_r23_rrs_recompute.py revised_rrs_and_nfav.csv
```

**Expected**: 7 A*, 4 B, 6 C profiles (range 73.2–115.6%).

#### 2. Reproduce retrospective control (R1.2)

```bash
cd results/retrospective_approved_antimalarials_20260909
python ../../scripts/p1_r12_retrospective.py rrs_profiles.csv
```

**Expected**: Pyrimethamine ≈100% on all PfDHFR mutants (does not recover clinical resistance).

#### 3. Reproduce DEKOIS ROC-AUC (R2.4)

```bash
cd results/dekois_mtxstripped_20260909
python ../../scripts/p1_r24_analyze.py dekois_pfdhfr_retained.csv dekois_pfdhfr_stripped.csv
```

**Expected**:
- Retained: ROC-AUC 0.502 [0.437, 0.567]
- Stripped: ROC-AUC 0.563 [0.498, 0.628]
- Overlapping 95% CIs → no MTX support

#### 4. Statistical audit

```bash
python scripts/p1_statistical_audit.py data/v7_integrated_candidate_metrics.csv
```

**Expected** (after Holm–Bonferroni correction):
- PNS–RRS: ρ = −0.714, p_adj < 0.05 (significant)
- RRS–WT score: ρ = +0.691, p_adj < 0.05 (significant)
- N_fav–RRS: ρ = +0.714, p_adj < 0.05 (significant)
- ACSI–RRS: ρ = −0.190, p_adj = 0.452 (not significant)

---

## File Formats

### CSV files
- Comma-separated
- UTF-8 encoding
- First row = column headers
- SMILES strings are canonical (RDKit-generated)

### JSON files
- UTF-8 encoding
- Pretty-printed (indent=2)
- Manifest structure: `{protocol, inputs, outputs, checksums}`

### Docking outputs
- PDBQT format (AutoDock standard)
- Mode 1 (best affinity) is used for all analyses
- Exhaustiveness = 32 (except multi-seed validation = 16)

---

## Receptor Structures

All receptor files referenced in `results/*/manifest.json` were sourced from:

| Target | PDB ID | Mutation | Notes |
|--------|--------|----------|-------|
| **PfDHFR** | 1J3I | WT (3D7-like) | Coordinates from Singh et al. 2019 |
| PfDHFR | 1J3K | N51I | Mutant model |
| PfDHFR | 3QGT | C59R | Mutant model |
| PfDHFR | 4DPD | S108N | Mutant model |
| PfDHFR | 1J3J | I164L | Mutant model |
| **PfCRT** | 6UKJ | WT (3D7-like, **corrected R2.3**) | Chain A, cavity-anchored grid |
| PfCRT | — | K76T | Homology model from 6UKJ |
| PfCRT | — | K76A | Homology model from 6UKJ |
| **PfClpP** | 2F6I | WT | Peptide-bound, remediation complete |
| PfATP4 | 6OBE | WT | ADP-bound |

**Note**: PfCRT WT was re-done in R2.3 after detecting a structure misassignment in the original submission. The corrected receptor is in `results/pfcrt_redock_v2grid_20260909/inputs/pfcrt_wt_corrected.pdb`.

---

## Grid Specifications

All grids follow the V2 canonical protocol (centroid-anchored):

| Target | Center (x, y, z) Å | Box size (Å) | Spacing (Å) |
|--------|-------------------|--------------|-------------|
| PfDHFR | (32.5, 14.2, 18.7) | 22 × 22 × 22 | 0.375 |
| PfCRT  | (47.3, 51.8, 42.1) | 20 × 20 × 20 | 0.375 |
| PfClpP | (11.4, 8.6, 15.3)  | 20 × 20 × 20 | 0.375 |
| PfATP4 | (28.9, 35.2, 41.6) | 22 × 22 × 22 | 0.375 |

**Important**: PfCRT grid was corrected in R2.3 to be cavity-anchored on the 3D7-like WT structure (6UKJ). The original V7 submission used a misassigned structure. All results in this deposit reflect the corrected protocol.

---

## Software Versions

| Software | Version | Purpose |
|----------|---------|---------|
| AutoDock Vina | 1.2.5 | Docking |
| RDKit | 2025.03.6 | SMILES, descriptors, fingerprints |
| Python | 3.11.10 | Analysis scripts |
| NumPy | 2.2.1 | Array operations |
| pandas | 2.2.3 | Tabular data |
| SciPy | 1.15.1 | Statistics |
| matplotlib | 3.10.1 | Figures |
| scikit-learn | 1.6.1 | ROC curves, metrics |

**Environment**: `malaria_md` conda environment (see `../environment.yml` in the GitHub repository for complete package list).

---

## Evidence Boundaries

This deposit provides:
- ✅ Four-target docking profiles
- ✅ Per-target RRS values (mutation-panel docking ratios)
- ✅ Exploratory correlations (PNS–RRS, N_fav–RRS, ACSI–RRS)
- ✅ Validation datasets (DEKOIS, MMV, redocking, retrospective)
- ✅ Complete protocol specifications

This deposit **does NOT provide**:
- ❌ Experimental binding affinities
- ❌ Confirmed multi-target engagement
- ❌ Biological resistance circumvention evidence
- ❌ Measured IC₅₀/EC₅₀ values
- ❌ Clinical relevance claims

**The computational profiles are hypotheses for wet-lab validation, not activity predictions.**

---

## Relation to Manuscript

This deposit corresponds to:
- **Main text**: Tables 1–3, Figures 1–3
- **Supporting Information**: Tables S1–S14, Figures S1–S4
- **Response to Reviewers**: All 18 points (2 R1, 16 R2)

**Manuscript sections directly supported by this deposit**:
- §2 Methods (all protocols)
- §3.1 Hybrid library and prioritization
- §3.2 Four-target docking profiles
- §3.3 Per-target RRS classification
- §3.4 Exploratory cross-metric correlations
- §3.5 Validation (DEKOIS, MMV, redocking, retrospective)

---

## Citation

If you use this dataset, please cite:

**Paper** (when published):
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. Target breadth and mutation resilience in 
African-natural-product-inspired antimalarial chemotypes: a computational analysis. 
J. Chem. Inf. Model. 2026, XX, XXXX–XXXX. DOI: [to be assigned]
```

**Dataset**:
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. (2026). P1 V8 Reproducibility Package — JCIM Revision [Data set]. 
Zenodo. https://doi.org/10.5281/zenodo.22686176
```

---

## Contact

**Corresponding author**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**ORCID**: 0009-0004-5170-2309  
**Institution**: Department of Physics, Faculty of Science, University of Yaoundé I, Cameroon

**Code repository** (to be made public upon publication): https://github.com/NanaEngo/Malaria_codesV2

---

## Acknowledgments

This work was supported by computational resources from the University of Yaoundé I. We thank the reviewers for constructive feedback that substantially improved the validation rigor and methodological transparency of this study.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V8 | 2026-09-10 | Initial Zenodo deposit for JCIM resubmission |

---

## Zenodo Upload Instructions

### Step 1: Create New Upload

1. Go to https://zenodo.org/deposit/22686176 (reserved DOI)
2. Click "New upload" or "Edit" if draft exists
3. Fill in metadata:
   - **Title**: "P1 V8 Reproducibility Package — JCIM Revision: Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes"
   - **Authors**: 
     - Sao Temgoua, Myke Vital (ORCID: 0009-0004-5170-2309)
     - Tchapet Njafa, Jean-Pierre (ORCID: 0000-0002-1936-8353)
     - Samafou, Penabei
     - Fon Mbacham, Wilfred (ORCID: 0000-0002-3934-3233)
     - Nana Engo, Serge Guy (ORCID: 0000-0002-7484-3508)
   - **Description**: Paste the "Purpose" section from this README
   - **Keywords**: antimalarial, polypharmacology, resistance resilience, virtual screening, AutoDock Vina, computational chemistry, Plasmodium falciparum, natural products, African plant metabolites
   - **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
   - **Upload type**: Dataset
   - **Related identifiers**: 
     - "is supplement to" → [manuscript DOI when assigned]
     - "is derived from" → PDB: 1J3I, 1J3K, 3QGT, 4DPD, 1J3J, 6UKJ, 2F6I, 6OBE

### Step 2: Upload Files

**Option A: Web interface (recommended for initial upload)**
1. Drag and drop the entire `zenodo_package_P1/` folder
2. OR upload files individually (may take longer)
3. Zenodo will compute checksums automatically

**Option B: Zenodo CLI (for updates)**
```bash
# Install Zenodo CLI
pip install zenodo-cli

# Upload
zenodo upload --deposit-id 22686176 --file zenodo_package_P1.zip
```

### Step 3: Verify Upload

After upload completes:
1. Download `sha256sums.txt` from Zenodo
2. Download a few random files and verify checksums:
   ```bash
   sha256sum data/v7_candidate_manifest.csv
   # Compare to sha256sums.txt
   ```
3. If checksums match → proceed to publish
4. If checksums don't match → re-upload affected files

### Step 4: Publish

1. Click "Publish" on Zenodo
2. **DOI will become active immediately**
3. Confirm DOI resolves: https://doi.org/10.5281/zenodo.22686176
4. **IMPORTANT**: Zenodo deposits are versioned — you cannot delete after publishing, but you can upload a new version if corrections are needed

### Step 5: Update Manuscript

Once DOI is active and resolves correctly:
1. Verify Data Availability statement in Main manuscript (already inserted):
   ```latex
   \url{https://doi.org/10.5281/zenodo.22686176}
   ```
2. Verify SM Reproducibility section (already inserted)
3. Verify Response to Reviewers R2.6 (already mentioned)
4. **No changes needed if DOI matches** — you're ready to submit!

### Step 6: Make GitHub Repository Public

After Zenodo DOI is confirmed working:
1. Go to https://github.com/NanaEngo/Malaria_codesV2/settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility" → "Make public"
4. Create a release tag:
   ```bash
   git tag -a v8-jcim-resubmission -m "P1 V8 JCIM resubmission with Zenodo DOI"
   git push origin v8-jcim-resubmission
   ```

---

## Troubleshooting

### Checksums don't match after download
- Zenodo may re-compress files during upload
- Re-download and verify again
- If persistent, contact Zenodo support

### Upload times out
- Split large files into smaller archives
- Use Zenodo CLI for large uploads (more reliable)
- Check internet connection

### DOI doesn't resolve immediately
- Wait 10–15 minutes for Zenodo's DOI registration to propagate
- Check https://doi.org/10.5281/zenodo.22686176 directly
- If > 30 min, contact Zenodo support

### Need to correct a file after publishing
- Upload a new version on Zenodo (preserves original DOI, adds version suffix)
- Update manuscript to reference "v2" if needed
- Original version remains accessible

---

**Last updated**: 2026-09-10  
**Package prepared by**: Kiro AI agent (on behalf of MVST)  
**Zenodo deposit ID**: 22686176 (reserved, pending upload)
