# P3 Zenodo Setup & Upload Guide

**Package:** zenodo_package_P3/  
**Reserved DOI:** https://doi.org/10.5281/zenodo.19608875  
**Current Status:** ✅ Package prepared, ready for upload  
**Target:** Publish Zenodo deposit for P3 V2609 JCAMD revision

---

## Quick Start (If You're in a Hurry)

```bash
# 1. Verify package integrity
cd ~/Documents/GitHub/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3
sha256sum -c sha256sums.txt
# Expected: All files OK ✅

# 2. Create upload ZIP
cd ..
zip -r zenodo_p3_upload.zip zenodo_package_P3/
# Result: zenodo_p3_upload.zip (~10-50 MB depending on data files)

# 3. Go to Zenodo
# URL: https://zenodo.org/deposit/19608875
# Log in → Upload ZIP → Fill metadata (see below) → Publish
```

**See "Step-by-Step Upload Process" below for detailed instructions.**

---

## Table of Contents

1. [Pre-Upload Checklist](#pre-upload-checklist)
2. [Package Contents Verification](#package-contents-verification)
3. [Step-by-Step Upload Process](#step-by-step-upload-process)
4. [Metadata Template (Copy-Paste Ready)](#metadata-template)
5. [Post-Upload Verification](#post-upload-verification)
6. [Manuscript Integration](#manuscript-integration)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Upload Checklist

### ✅ Verify Package Structure

```bash
cd ~/Documents/GitHub/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3

# Check all required directories exist
ls -d data/ results/ scripts/ documentation/
# Expected: All 4 directories present

# Check all required files exist
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt UPLOAD_INSTRUCTIONS.md
# Expected: All 5 files present
```

### ✅ Verify Checksums

```bash
sha256sum -c sha256sums.txt
```

**Expected output:**
```
data/p3_labels_production.csv: OK
data/p3_tda_fingerprints.csv: OK
data/p3_tne_embeddings.csv: OK
results/p3_hybrid_benchmark.csv: OK
... (all files OK)
```

**If you see mismatches:** Some files may have been modified. Regenerate checksums:
```bash
find . -type f ! -name 'sha256sums.txt' -exec sha256sum {} \; > sha256sums.txt
```

### ✅ Check Package Size

```bash
du -sh .
# Expected: ~10-100 MB (depending on data file sizes)

# If > 50GB: Contact Zenodo for large deposit approval
# If 2-50GB: Upload via web interface (may take time)
# If < 2GB: Upload should be smooth ✅
```

---

## Package Contents Verification

### Current Files in Package

Run this to see what's included:

```bash
tree -L 2 zenodo_package_P3/
```

**Expected structure:**

```
zenodo_package_P3/
├── README.md                    ← Main documentation
├── MANIFEST.json                ← Package metadata
├── LICENSE.txt                  ← CC BY 4.0 license
├── sha256sums.txt              ← Checksums for verification
├── UPLOAD_INSTRUCTIONS.md       ← This guide
├── ZENODO_SETUP_GUIDE.md       ← Comprehensive setup (new)
│
├── data/                        ← Core datasets
│   ├── p3_labels_production.csv    (19,849 molecules with activity labels)
│   ├── p3_tda_fingerprints.csv     (TFP: 84 persistent homology features)
│   └── p3_tne_embeddings.csv       (TNE: 192-dim Tucker embeddings)
│
├── results/                     ← Benchmark results
│   ├── p3_hybrid_benchmark.csv     (5-fold CV for 9 representations)
│   ├── p3_qks_benchmark_v1.csv     (Quantum kernel internal)
│   ├── p3_chembl_expanded.csv      (ChEMBL external validation data)
│   ├── p3_external_validation.csv  (External validation results)
│   └── p3_sota_benchmark.csv       (SOTA comparison)
│
├── scripts/                     ← Analysis code
│   ├── p3_tda_pipeline.py          (Topological fingerprint generation)
│   ├── p3_tne_pipeline.py          (Tensor network embeddings)
│   ├── p3_qks_kernel.py            (Quantum kernel computation)
│   ├── p3_hybrid_benchmark.py      (Main benchmark)
│   ├── environment.yml             (Conda environment)
│   └── README_SCRIPTS.md           (Script usage guide)
│
└── documentation/               ← Supporting docs
    └── P3_DATA_ANALYSIS_REPORT.md  (Complete provenance & analysis)
```

### File Count Check

```bash
find zenodo_package_P3/ -type f | wc -l
# Expected: ~15-25 files total
```

---

## Step-by-Step Upload Process

### Step 1: Access Your Reserved Zenodo Deposit

1. **Go to:** https://zenodo.org/deposit/19608875
2. **Log in** with your Zenodo account credentials
3. **Verify** you see the reserved DOI: `10.5281/zenodo.19608875`

**If you don't see the deposit:**
- Check you're logged into the correct Zenodo account
- The deposit may have been created under a different account
- Contact Zenodo support: info@zenodo.org

### Step 2: Upload Files

**Option A: Upload Individual Files (Recommended)**

1. In the Zenodo deposit interface, click **"Start upload"**
2. **Drag and drop** the entire `zenodo_package_P3/` folder into the upload area
3. Wait for all files to upload (Zenodo shows progress bars)
4. **Verify** all files appear in the file list

**Advantages:**
- Users can download individual files
- Better for large datasets
- Zenodo computes checksums automatically

**Option B: Upload as ZIP Archive**

1. Create ZIP locally:
   ```bash
   cd ~/Documents/GitHub/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607_V4
   zip -r zenodo_p3_upload.zip zenodo_package_P3/
   ```
2. Upload `zenodo_p3_upload.zip` to Zenodo
3. Users will need to unzip after download

**Advantages:**
- Faster upload for slow connections
- Single file to manage

**Recommendation:** Use **Option A** unless you have upload issues.

### Step 3: Fill Metadata (Copy-Paste Ready)

See the **[Metadata Template](#metadata-template)** section below for copy-paste ready content.

**Required fields:**

1. **Upload type:** Dataset
2. **Publication date:** 2026-09-15 (or current date)
3. **Title:** (see template)
4. **Creators:** (see template - 5 authors with ORCIDs)
5. **Description:** (see template)
6. **License:** Creative Commons Attribution 4.0 International
7. **Keywords:** (see template - 14 keywords)

**Optional but recommended:**

8. **Related identifiers:**
   - "is supplement to" → (manuscript DOI when assigned)
   - "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1 deposit)
9. **Contributors:** (leave blank unless you have data curators to acknowledge)
10. **Funding:** (add grant numbers if applicable)

### Step 4: Pre-Publish Verification

**Before clicking "Publish", verify:**

✅ **File integrity:**
```bash
# Download sha256sums.txt from Zenodo preview
# Spot-check 3 random files:
wget https://zenodo.org/api/records/19608875/files/data/p3_labels_production.csv
sha256sum p3_labels_production.csv
# Compare against sha256sums.txt
```

✅ **Metadata accuracy:**
- [ ] All 5 author names correct
- [ ] All ORCIDs correct (check against ORCID.org)
- [ ] Title matches manuscript exactly
- [ ] Description clearly explains content
- [ ] License is CC BY 4.0
- [ ] Keywords cover key concepts

✅ **File list completeness:**
- [ ] All data/ files present (3 files)
- [ ] All results/ files present (~5 files)
- [ ] All scripts/ files present (~6 files)
- [ ] All documentation/ files present (1+ files)
- [ ] Root files present (README, MANIFEST, LICENSE, etc.)

### Step 5: Publish

1. Click the green **"Publish"** button
2. ⚠️ **READ THE WARNING:** Once published, the deposit is **immutable**
   - You can't edit or delete files
   - You can only add new versions (v2, v3, etc.)
3. Click **"Confirm"** to publish

**What happens next:**
- DOI becomes active immediately
- Zenodo generates a landing page
- Files become publicly downloadable
- Citation metadata propagates to DataCite

### Step 6: Verify Publication

**Immediate checks (within 5 minutes):**

✅ **DOI Resolution:**
```bash
curl -L https://doi.org/10.5281/zenodo.19608875
# Should redirect to Zenodo landing page
```

✅ **Landing page loads:**
- Go to: https://zenodo.org/records/19608875
- Verify title, authors, description render correctly
- Check README.md displays properly

✅ **Download test:**
```bash
# Download 3 random files and verify checksums
wget https://zenodo.org/api/records/19608875/files/sha256sums.txt
wget https://zenodo.org/api/records/19608875/files/data/p3_labels_production.csv
sha256sum -c sha256sums.txt
```

**If all checks pass:** ✅ **Zenodo deposit is live and ready!**

---

## Metadata Template

### Copy-Paste Into Zenodo

**Upload type:**
```
Dataset
```

**Publication date:**
```
2026-09-15
```
*(or current date)*

**Title:**
```
P3 Reproducibility Package — JCAMD Submission: Quantum-inspired molecular representations for African antimalarial candidates
```

**Creators (in order, add ORCIDs):**

```
1. Sao Temgoua, Myke Vital
   ORCID: 0009-0004-5170-2309
   Affiliation: University of Yaoundé I, Cameroon

2. Tchapet Njafa, Jean-Pierre
   ORCID: 0000-0002-1936-8353
   Affiliation: University of Yaoundé I, Cameroon

3. Samafou, Penabei
   Affiliation: University of Yaoundé I, Cameroon

4. Fon Mbacham, Wilfred
   ORCID: 0000-0002-3934-3233
   Affiliation: University of Yaoundé I, Cameroon

5. Nana Engo, Serge Guy
   ORCID: 0000-0002-7484-3508
   Affiliation: University of Yaoundé I, Cameroon
```

**Description:**
```
Complete reproducibility package for "Quantum-inspired molecular representations for African antimalarial candidates: topological fingerprints, tensor network embeddings, and kernel methods" submitted to the Journal of Computer-Aided Molecular Design (JCAMD).

This deposit provides:
- Core datasets (19,849 molecules with TFP, TNE, QKS representations)
- Benchmark results (5-fold cross-validation, external ChEMBL validation)
- Analysis scripts (Python 3.11+ with malaria_md conda environment)
- Complete documentation (data analysis report, methods supplement)

Key finding: None of the quantum-inspired representations (Topological Fingerprints, Tensor Network Embeddings, Quantum Kernel Scores) outperforms classical ECFP4 fingerprints under the tested protocols. However, these methods provide valuable diagnostic and interpretive insights into molecular topology and polypharmacology patterns.

Key results:
- ECFP4-RF: AUC 0.948 (random split) / 0.822 (scaffold split)
- Hybrid (TFP+TNE+QK): AUC 0.888
- Quantum kernel vs RBF: 0.751 vs 0.701 (p=0.088, not significant)
- ChEMBL external: Quantum 0.817 < RBF 0.847 (p=0.021, quantum worse)
- TNE docking correlation: R²=0.473 (PfDHFR), competitive with ECFP4

All files are SHA-256 verified. See README.md for complete usage instructions and reproduction protocols.
```

**License:**
```
Creative Commons Attribution 4.0 International (CC BY 4.0)
```

**Keywords (comma-separated):**
```
antimalarial, quantum-inspired, topological data analysis, persistent homology, tensor networks, quantum kernels, molecular representations, machine learning, drug discovery, Plasmodium falciparum, natural products, African plant metabolites, JCAMD, reproducibility
```

**Related identifiers:**

```
Relation: "is supplement to"
Identifier: (manuscript DOI - add after acceptance)
Scheme: DOI

Relation: "is related to"
Identifier: https://doi.org/10.5281/zenodo.22686176
Scheme: DOI
```
*(P1 deposit with docking scores)*

**Funding (optional):**
```
(Leave blank unless you have specific grant numbers to acknowledge)
```

---

## Post-Upload Verification

### Comprehensive Test Suite

After Zenodo publication, run these tests:

#### 1. DOI Resolution Test

```bash
# Test DOI redirects correctly
curl -I https://doi.org/10.5281/zenodo.19608875 | grep Location
# Expected: Location: https://zenodo.org/records/19608875
```

#### 2. File Integrity Test

```bash
# Download package and verify all checksums
mkdir -p /tmp/zenodo_test
cd /tmp/zenodo_test

# Download all files
wget -r -np -nH --cut-dirs=4 https://zenodo.org/api/records/19608875/files/

# Verify checksums
sha256sum -c sha256sums.txt
# Expected: All files OK ✅
```

#### 3. README Rendering Test

Visit: https://zenodo.org/records/19608875

**Check:**
- [ ] README.md renders as formatted markdown (not raw text)
- [ ] Tables display properly
- [ ] Code blocks have syntax highlighting
- [ ] Links are clickable
- [ ] Headings create table of contents

#### 4. Metadata Accuracy Test

**Verify on landing page:**
- [ ] Title matches manuscript
- [ ] All 5 authors listed in correct order
- [ ] All ORCIDs clickable and link to correct profiles
- [ ] Description displays properly (no formatting errors)
- [ ] Keywords appear as tags
- [ ] License badge shows "CC BY 4.0"
- [ ] DOI badge displays correctly

#### 5. Citation Export Test

**On Zenodo landing page:**
- [ ] Click "Cite" button
- [ ] Verify BibTeX export format
- [ ] Verify APA format
- [ ] Check all author names appear correctly

#### 6. Download Performance Test

```bash
# Test download speed for largest file
time wget https://zenodo.org/api/records/19608875/files/data/p3_tne_embeddings.csv
# Should complete in reasonable time (< 5 min for files < 100MB)
```

**If all 6 tests pass:** ✅ **Zenodo deposit is production-ready!**

---

## Manuscript Integration

### Update Data Availability Statement

**For V2609 manuscript, add to Data Availability section:**

```latex
\section*{Data Availability}

All data, analysis scripts, and reproducibility records supporting this study are 
openly available at Zenodo \citep{zenodo_p3}:

\begin{itemize}
\item \textbf{DOI:} \url{https://doi.org/10.5281/zenodo.19608875}
\item \textbf{Contents:} Core datasets (19,849 molecules with TFP, TNE, QKS 
representations), benchmark results (5-fold CV, external validation), analysis 
scripts (Python 3.11+ with malaria\_md environment), complete documentation
\item \textbf{License:} CC BY 4.0 International
\end{itemize}

The Zenodo deposit includes SHA-256 checksums for all files to verify integrity. 
See the deposit README.md for complete usage instructions and reproduction protocols.
```

**Add to Bibliography_Paper3.bib:**

```bibtex
@misc{zenodo_p3,
  author       = {Sao Temgoua, Myke Vital and
                  Tchapet Njafa, Jean-Pierre and
                  Samafou, Penabei and
                  Fon Mbacham, Wilfred and
                  Nana Engo, Serge Guy},
  title        = {{P3 Reproducibility Package — JCAMD Submission: 
                   Quantum-inspired molecular representations for 
                   African antimalarial candidates}},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19608875},
  url          = {https://doi.org/10.5281/zenodo.19608875}
}
```

### Alternative: Shorter Statement

If you prefer brevity:

```latex
\section*{Data Availability}

All data and code are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.19608875} \citep{zenodo_p3}.
```

---

## Troubleshooting

### Upload Fails or Times Out

**Symptoms:** Upload hangs, shows errors, or fails after hours

**Solutions:**
1. **Use ZIP upload** (Option B above) — smaller single file
2. **Split into batches:**
   ```bash
   # Upload data/ folder separately
   # Upload results/ folder separately
   # Upload scripts/ separately
   ```
3. **Check internet connection:** Zenodo requires stable connection
4. **Try different time:** Zenodo may be slower during peak hours (EU daytime)

### Checksums Don't Match After Download

**Symptoms:** `sha256sum -c` shows mismatches

**Possible causes:**
1. **Newline differences:** Windows vs Linux line endings
2. **Download incomplete:** Try re-downloading
3. **File modified during upload:** Check if you edited files after checksums were generated

**Solution:**
```bash
# Regenerate checksums from Zenodo download
cd zenodo_download/
find . -type f ! -name 'sha256sums.txt' -exec sha256sum {} \; > sha256sums_new.txt
diff sha256sums.txt sha256sums_new.txt
# If differences are only in newlines, it's OK
```

### DOI Doesn't Resolve After 30 Minutes

**Symptoms:** https://doi.org/10.5281/zenodo.19608875 shows 404 error

**Possible causes:**
1. **DOI propagation delay:** Can take up to 24 hours (rare)
2. **Zenodo/DataCite sync issue:** Technical problem on their end

**Solutions:**
1. **Wait 24 hours** and test again
2. **Check Zenodo directly:** https://zenodo.org/records/19608875 (bypass DOI)
3. **Contact Zenodo support:** info@zenodo.org with your deposit ID

### README Doesn't Render as Markdown

**Symptoms:** README shows as plain text or with markdown syntax visible

**Possible causes:**
1. **File not named README.md:** Zenodo only renders files named exactly `README.md`
2. **Encoding issue:** File not UTF-8

**Solution:**
```bash
# Verify filename
ls -l README.md  # Must be exact

# Verify encoding
file README.md
# Expected: README.md: UTF-8 Unicode text

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 README.md > README_utf8.md
mv README_utf8.md README.md
```

### Need to Correct a File After Publishing

**Symptoms:** You found an error in an uploaded file after clicking "Publish"

**Important:** ⚠️ You **cannot** edit or delete published files on Zenodo

**Solutions:**
1. **Upload a new version (v2):**
   - Go to your published deposit
   - Click "New version"
   - Upload corrected files
   - DOI remains the same: `10.5281/zenodo.19608875`
   - Version-specific DOI: `10.5281/zenodo.19608876` (v2)

2. **Add erratum file:**
   - If error is minor, upload `ERRATA.txt` to v2 explaining correction
   - Original v1 remains available for transparency

3. **Contact Zenodo to unpublish (extreme cases only):**
   - Only for serious issues (e.g., privacy violation, copyright)
   - Email: info@zenodo.org
   - Unpublished deposits leave a tombstone page

### File Size Exceeds Zenodo Limit

**Symptoms:** Upload rejected because file > 50GB

**Zenodo limits:**
- Default: 50 GB per deposit
- Larger: Contact Zenodo for approval

**Solutions:**
1. **Compress large files:**
   ```bash
   gzip large_file.csv  # Creates large_file.csv.gz
   ```

2. **Split large files:**
   ```bash
   split -b 10G large_file.csv large_file_part_
   # Creates: large_file_part_aa, large_file_part_ab, etc.
   ```

3. **Contact Zenodo for quota increase:**
   - Email: info@zenodo.org
   - Subject: "Request for increased deposit quota"
   - Explain your research and file sizes

---

## Post-Publication Actions

### 1. Update AGENTS.md

Add Zenodo status to AGENTS.md:

```markdown
## P3 Zenodo Status

- **DOI:** https://doi.org/10.5281/zenodo.19608875
- **Status:** ✅ Published (2026-09-15)
- **Citation:** Sao Temgoua et al. (2026). P3 Reproducibility Package [Data set]. Zenodo.
```

### 2. Make GitHub Repository Public (Optional)

**After Zenodo DOI verification:**

```bash
cd ~/Documents/GitHub/Malaria_codesV2

# Create P3 release tag
git tag -a p3-v2609-jcamd -m "P3 V2609 JCAMD revision with Zenodo DOI 10.5281/zenodo.19608875"
git push origin p3-v2609-jcamd

# Then make repository public via GitHub settings
```

**Steps to make public:**
1. Go to: https://github.com/NanaEngo/Malaria_codesV2/settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility" → "Make public"
4. Confirm action

**Benefits:**
- Users can see code development history
- GitHub citation integration
- Community contributions possible

**Wait until:** Zenodo DOI confirmed working before making public

### 3. Announce Deposit (Optional)

**Share on social media / mailing lists:**

```
🎉 New data release! P3 Reproducibility Package for our JCAMD submission on 
quantum-inspired molecular representations for antimalarial drug discovery is 
now openly available at Zenodo: https://doi.org/10.5281/zenodo.19608875

Includes datasets, benchmarks, and analysis scripts for topological fingerprints, 
tensor network embeddings, and quantum kernel methods. CC BY 4.0 licensed.

Key finding: Classical ECFP4 fingerprints outperform quantum-inspired methods 
under tested protocols, but quantum methods provide valuable interpretive insights.

#OpenScience #DrugDiscovery #QuantumML #Malaria
```

---

## Quick Reference Card

### Essential URLs

| Resource | URL |
|----------|-----|
| **Zenodo deposit** | https://zenodo.org/deposit/19608875 |
| **Published DOI** | https://doi.org/10.5281/zenodo.19608875 |
| **Zenodo support** | info@zenodo.org |
| **Package location** | `~/Documents/GitHub/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/` |

### Essential Commands

```bash
# Verify checksums
sha256sum -c sha256sums.txt

# Create upload ZIP
zip -r zenodo_p3_upload.zip zenodo_package_P3/

# Test DOI resolution
curl -I https://doi.org/10.5281/zenodo.19608875

# Download for verification
wget https://zenodo.org/api/records/19608875/files/sha256sums.txt
```

### Key Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation, landing page |
| `MANIFEST.json` | Package metadata, key findings |
| `LICENSE.txt` | CC BY 4.0 license text |
| `sha256sums.txt` | File integrity checksums |
| `UPLOAD_INSTRUCTIONS.md` | Quick upload guide |
| `ZENODO_SETUP_GUIDE.md` | This comprehensive guide |

---

## Success Criteria

Your Zenodo upload is **complete and successful** when:

✅ **All files uploaded** (no missing files)  
✅ **Checksums verified** (sha256sum -c passes)  
✅ **Metadata complete** (all required fields filled)  
✅ **DOI resolves** (https://doi.org/10.5281/zenodo.19608875 works)  
✅ **Downloads work** (test 3 random files)  
✅ **README renders** (markdown displays properly)  
✅ **Citation exports** (BibTeX/APA formats work)  
✅ **Manuscript updated** (Data Availability section has DOI)

**When all criteria met:** 🎉 **Zenodo deposit is production-ready for P3 JCAMD submission!**

---

## Timeline Estimate

| Task | Estimated Time |
|------|----------------|
| Pre-upload verification | 10 minutes |
| Create ZIP archive | 2-5 minutes |
| Upload to Zenodo | 10-60 minutes (depends on file size and connection) |
| Fill metadata | 10 minutes |
| Pre-publish verification | 10 minutes |
| Publish deposit | 1 minute |
| Post-publish verification | 15 minutes |
| Update manuscript | 10 minutes |
| **Total** | **~1-2 hours** |

---

## Support

**Questions or issues?**

1. **Check this guide first** (most common issues covered)
2. **Check Zenodo FAQ:** https://help.zenodo.org
3. **Email Zenodo support:** info@zenodo.org
4. **Check AGENTS.md** for project-specific context

**For manuscript integration questions:**
- Refer to `SUBMISSION_READY.md` in V2609 folder
- Contact corresponding author

---

**Last Updated:** 15 September 2026  
**Prepared By:** Kiro AI  
**Guide Version:** 1.0

---

**End of Setup Guide**
