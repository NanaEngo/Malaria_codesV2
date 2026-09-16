# P2 Zenodo Setup & Upload Guide

**Package:** zenodo_package_P2/  
**Reserved DOI:** ⚠️ **TO BE RESERVED** → https://doi.org/10.5281/zenodo.XXXXXXX  
**Current Status:** Ready for upload after DOI reservation  
**Target:** Publish Zenodo deposit for P2 V2609C JCIM submission

---

## Quick Start (If You're in a Hurry)

```bash
# 0. Reserve DOI first (see Step 0 below)

# 1. Verify package integrity
cd ~/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2
sha256sum -c sha256sums.txt
# Expected: All files OK ✅

# 2. Check package size
du -sh .
# Expected: ~500 MB

# 3. Create upload ZIP (recommended for ~500 MB package)
cd ..
zip -r zenodo_p2_upload.zip zenodo_package_P2/
# Result: zenodo_p2_upload.zip (~500 MB)

# 4. Go to Zenodo
# URL: https://zenodo.org/deposit/XXXXXXX (your reserved DOI)
# Log in → Upload ZIP → Fill metadata (see below) → Publish
```

**See "Step-by-Step Upload Process" below for detailed instructions.**

---

## Table of Contents

1. [Step 0: Reserve DOI (FIRST!)](#step-0-reserve-doi)
2. [Pre-Upload Checklist](#pre-upload-checklist)
3. [Package Contents Verification](#package-contents-verification)
4. [Step-by-Step Upload Process](#step-by-step-upload-process)
5. [Metadata Template (Copy-Paste Ready)](#metadata-template)
6. [Post-Upload Verification](#post-upload-verification)
7. [Manuscript Integration](#manuscript-integration)
8. [Troubleshooting](#troubleshooting)

---

## Step 0: Reserve DOI

**⚠️ DO THIS FIRST before uploading files!**

### Reserve Your DOI on Zenodo

1. Go to: https://zenodo.org
2. Log in with your Zenodo account
3. Click green **"New upload"** button
4. Fill **basic information only**:

   **Title:**
   ```
   P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads
   ```

   **Authors** (in order):
   - Sao Temgoua, Myke Vital (ORCID: 0009-0004-5170-2309)
   - Tchapet Njafa, Jean-Pierre (ORCID: 0000-0002-1936-8353)
   - Samafou, Penabei
   - Fon Mbacham, Wilfred (ORCID: 0000-0002-3934-3233)
   - Nana Engo, Serge Guy (ORCID: 0000-0002-7484-3508)

   **Upload type:** Dataset

5. Click **"Save"** (do NOT upload files yet!)
6. Copy your reserved DOI (format: `10.5281/zenodo.XXXXXXX`)

### Update Package Files with Reserved DOI

After reservation, update these files:

```bash
# 1. Update MANIFEST.json
# Change: "doi_reserved": "TO_BE_RESERVED"
# To:     "doi_reserved": "https://doi.org/10.5281/zenodo.XXXXXXX"

# 2. Update README.md header
# Change: **DOI**: ⚠️ **TO BE RESERVED**
# To:     **DOI**: https://doi.org/10.5281/zenodo.XXXXXXX

# 3. Update UPLOAD_INSTRUCTIONS.md
# Replace all XXXXXXX with your actual DOI number
```

---

## Pre-Upload Checklist

### ✅ Verify Package Structure

```bash
cd ~/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2

# Check all required directories exist
ls -d data/ results/ scripts/ documentation/
# Expected: All 4 directories present

# Check all required files exist
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt
# Expected: All files present
```

### ✅ Verify Checksums

```bash
sha256sum -c sha256sums.txt
```

**Expected output:**
```
data/c_rrs_classification.csv: OK
data/c_pns_ranking.csv: OK
results/md_rrs_discriminative_pilot.csv: OK
... (all files OK)
```

**If checksums need to be generated:**
```bash
find . -type f ! -name 'sha256sums.txt' -exec sha256sum {} \; > sha256sums.txt
```

### ✅ Check Package Size

```bash
du -sh .
# Expected: ~500 MB

# Size guide:
# < 2GB: Upload should be smooth ✅
# 2-10GB: May take 30-60 minutes
# > 10GB: Contact Zenodo for guidance
```

---

## Package Contents Verification

### Current Files in Package

Run this to see what's included:

```bash
tree -L 2 zenodo_package_P2/
```

**Expected structure:**

```
zenodo_package_P2/
├── README.md                    ← Main documentation
├── MANIFEST.json                ← Package metadata
├── LICENSE.txt                  ← CC BY 4.0 license
├── sha256sums.txt              ← Checksums for verification
├── UPLOAD_INSTRUCTIONS.md       ← Detailed upload guide
├── UPLOAD_CHECKLIST.md         ← Interactive checklist
├── QUICK_START.txt             ← Quick reference card
├── ZENODO_SETUP_GUIDE.md       ← This guide
│
├── data/                        ← Core datasets
│   ├── c_rrs_classification.csv         (17 candidates, RRS classes)
│   ├── c_pns_ranking.csv                (Polypharmacology scores)
│   ├── c_acsi_scores.csv                (African-Chemotype index)
│   ├── set_c_trajectory_metrics_pilot.csv (MD metrics, 16 systems)
│   └── external_docking_scores.csv      (39-ligand panel, 312 records)
│
├── results/                     ← Analysis outputs
│   ├── md_rrs_discriminative_pilot.csv  (Multi-threshold MD-RRS)
│   ├── mmgbsa_summary_pilot.csv         (MM-GBSA endpoints)
│   ├── md_vs_docking_comparison_pilot.csv (Estimand divergence)
│   ├── external_docking_rrs_20260827.csv (External RRS)
│   └── cross_metric_statistical_audit.csv (Correlations)
│
├── scripts/                     ← Analysis code
│   ├── p2_rigorous_audit.py             (RRS classification, seed 42)
│   ├── set_c_trajectory_qc.py           (MD QC gate)
│   ├── p2_setc_md_rrs.py                (MD-RRS analysis)
│   ├── p2_external_docking_repair.sh    (External panel prep)
│   └── environment.yml                  (Conda environment)
│
└── documentation/               ← Supporting docs
    ├── P2_DATA_ANALYSIS_REPORT.md       (Complete provenance)
    ├── MMGBSA_JUSTIFICATION_ADDENDUM.md (MM-GBSA rationale)
    └── ESTIMAND_DIVERGENCE_FRAMEWORK.md (Methodology)
```

---

## Step-by-Step Upload Process

### Step 1: Access Your Reserved Zenodo Deposit

1. Go to: `https://zenodo.org/deposit/XXXXXXX` (replace XXXXXXX with your DOI number)
2. Log in with your Zenodo account
3. You should see your draft deposit with reserved DOI

### Step 2: Upload Files

**Option A: Drag entire folder (if manageable)**
1. Open file explorer, navigate to `zenodo_package_P2/`
2. Drag entire folder to Zenodo's "Files" section
3. Wait for upload (10-30 minutes for ~500 MB)

**Option B: Upload ZIP (recommended for ~500 MB)**
1. Create ZIP: `zip -r zenodo_p2_upload.zip zenodo_package_P2/`
2. Upload `zenodo_p2_upload.zip` to Zenodo
3. Wait for upload to complete

**Option C: Upload subdirectories separately**
1. Create ZIPs for each subdirectory:
   ```bash
   cd zenodo_package_P2
   zip -r data.zip data/
   zip -r results.zip results/
   zip -r scripts.zip scripts/
   zip -r documentation.zip documentation/
   ```
2. Upload each ZIP with clear naming

### Step 3: Fill Metadata

See [Metadata Template](#metadata-template) section below for copy-paste ready text.

**Required fields:**
- ✅ Upload type: Dataset
- ✅ Title
- ✅ Creators (all 5 authors with ORCIDs)
- ✅ Description
- ✅ Keywords
- ✅ License: CC BY 4.0
- ✅ Access right: Open Access

**Optional but recommended:**
- Related identifiers (P1, P3 DOIs)
- Funding information (if applicable)

### Step 4: Pre-Publish Verification

Before clicking "Publish", verify:

- [ ] All files uploaded successfully
- [ ] File size ~500 MB total
- [ ] All 5 author names correct
- [ ] All ORCIDs correct
- [ ] Title matches manuscript
- [ ] Description complete
- [ ] All keywords entered
- [ ] License is CC BY 4.0

**Download test:**
- Download `sha256sums.txt` from Zenodo preview
- Download 2-3 random files
- Verify checksums match

### Step 5: Publish

1. Click green **"Publish"** button
2. Read warning: **Deposit is immutable after publish!**
3. Confirm publication

**DOI becomes active immediately after publish.**

---

## Metadata Template

### Copy-Paste Ready Metadata for Zenodo

#### Title
```
P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads
```

#### Creators (in order)
```
1. Sao Temgoua, Myke Vital
   ORCID: 0009-0004-5170-2309

2. Tchapet Njafa, Jean-Pierre
   ORCID: 0000-0002-1936-8353

3. Samafou, Penabei
   (no ORCID)

4. Fon Mbacham, Wilfred
   ORCID: 0000-0002-3934-3233

5. Nana Engo, Serge Guy
   ORCID: 0000-0002-7484-3508
```

#### Description
```
Complete reproducibility records for "Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads" submitted to the Journal of Chemical Information and Modeling (JCIM).

This deposit provides:
- Core datasets (17 Set-C candidates with docking-RRS, PNS, ACSI, and MD trajectories)
- Docking results (136 Vina systems across PfDHFR and PfCRT WT and mutant panels)
- MD simulation outputs (16 Set-C pilot systems, 10 ns each, GROMACS trajectories)
- MM-GBSA results (16 systems with gmx_MMPBSA endpoint estimates)
- Estimand Divergence analysis (static docking vs short MD pose retention)
- 39-ligand external docking replication (GNINA CNN validation)
- African Natural Product chemical space profiling (Fsp3, QED, MPO distributions)
- Analysis scripts (Python 3.11+ with malaria_md environment)
- Complete documentation (DAR, methods supplements, protocol justifications)

Key findings: 
- 87.5% estimand divergence between static docking and short MD (7/8 matched mutant states)
- 39-ligand external replication: 100% Class-A agreement (RRS ≥80%)
- African NP chemical space: Fsp3=0.22, QED=0.70, MPO=0.728
- No mutant shows reproducible weaker-binding signature within 10 ns MD pilot
- Docking-RRS validated as positive triage filter for prospective experimental validation

All files are sha256-verified. See README.md for complete usage instructions.
```

#### Keywords (comma-separated)
```
antimalarial, drug resistance, polypharmacology, molecular dynamics, docking, PfDHFR, PfCRT, resistance retention score, African natural products, Plasmodium falciparum, MD validation, MM-GBSA, GROMACS, estimand divergence, virtual screening, JCIM
```

#### License
```
Creative Commons Attribution 4.0 International (CC BY 4.0)
```

#### Upload Type
```
Dataset
```

#### Related Identifiers
```
is supplement to: (manuscript DOI when assigned)
is related to: https://doi.org/10.5281/zenodo.22686176 (P1 deposit)
is related to: https://doi.org/10.5281/zenodo.19608875 (P3 deposit)
```

---

## Post-Upload Verification

### Verify DOI Resolves

```bash
curl -I https://doi.org/10.5281/zenodo.XXXXXXX
# Expected: HTTP 200 OK
```

### Check Landing Page

Visit: `https://zenodo.org/records/XXXXXXX`

Verify:
- [ ] Title correct
- [ ] All 5 authors listed
- [ ] All ORCIDs correct
- [ ] Description displays correctly
- [ ] README.md renders as markdown
- [ ] Files are downloadable

### Download Verification

```bash
# Download a few files and verify checksums
cd /tmp
wget https://zenodo.org/records/XXXXXXX/files/sha256sums.txt
wget https://zenodo.org/records/XXXXXXX/files/data/c_rrs_classification.csv
wget https://zenodo.org/records/XXXXXXX/files/README.md

# Verify checksums
sha256sum -c sha256sums.txt
```

---

## Manuscript Integration

### Update V2609C Manuscript

File: `manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`

Add to Data Availability section:

```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

### Add to Bibliography (Optional)

File: `manuscript/V2609C/references.bib`

```bibtex
@misc{zenodo_p2,
  author = {Sao Temgoua, Myke Vital and 
            Tchapet Njafa, Jean-Pierre and 
            Samafou, Penabei and 
            Fon Mbacham, Wilfred and 
            Nana Engo, Serge Guy},
  title = {P2 Reproducibility Package — JCIM Submission},
  year = {2026},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://doi.org/10.5281/zenodo.XXXXXXX},
  publisher = {Zenodo}
}
```

### Create Git Tag

```bash
cd ~/Documents/GitHub/Malaria_codesV2
git tag -a p2-jcim-submission -m "P2 JCIM V2609C submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"
git push origin p2-jcim-submission
```

### Update AGENTS.md

Change Zenodo status from "reserved" to "published" with actual DOI.

---

## Troubleshooting

### Upload Times Out

**Problem:** Upload fails or times out (common for ~500 MB)

**Solutions:**
1. Use ZIP upload (Option B above)
2. Upload during off-peak hours (evenings/weekends)
3. Try uploading subdirectories separately (Option C)
4. Check internet connection stability

### Checksums Don't Match

**Problem:** Downloaded files don't match checksums

**Solutions:**
1. If uploaded as ZIP, extract and verify individual files
2. Download raw files (not ZIP preview)
3. Verify you're comparing same file versions
4. Contact Zenodo support: info@zenodo.org

### DOI Doesn't Resolve

**Problem:** DOI URL returns 404 after publishing

**Solutions:**
1. Wait 10-15 minutes for propagation
2. Clear browser cache and try again
3. Check deposit page directly on Zenodo
4. Contact Zenodo support if persists > 30 minutes

### Need to Correct a File After Publishing

**Problem:** Found error in uploaded file

**Solution:**
- Upload a **new version** (v2) of the deposit
- DOI remains the same, version number increments
- Previous versions remain accessible
- Go to deposit page → "New version" button

### File Size Too Large

**Problem:** Package > 50 GB

**Solution:**
- Contact Zenodo before upload: info@zenodo.org
- They can approve larger deposits
- Consider excluding large auxiliary files

---

## Success Checklist

After completion, verify:

- [ ] DOI reserved and published
- [ ] All files uploaded successfully
- [ ] Checksums verified
- [ ] Metadata complete and accurate
- [ ] DOI resolves correctly
- [ ] README renders properly
- [ ] Downloads work
- [ ] Manuscript updated with DOI
- [ ] Git tag created and pushed
- [ ] AGENTS.md updated

---

## Contact

**Zenodo Support:** info@zenodo.org  
**Zenodo Help:** https://help.zenodo.org  
**Corresponding Author:** myke-vital.sao@facsciences-uy1.cm

---

**Last updated:** 2026-09-16  
**Prepared by:** Kiro AI agent  
**Status:** Ready for upload after DOI reservation
