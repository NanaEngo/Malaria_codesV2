# Quick Upload Guide — Zenodo P1 V8 Package

**Package location**: `Project1_Chem_space_antimalarial_V7_CorrectedGrid/zenodo_package_P1/`  
**Reserved DOI**: https://doi.org/10.5281/zenodo.22686176  
**Total files**: 218 files, 4.4 MB  
**Status**: ✅ Ready to upload (staged, verified, checksummed)

---

## Pre-Upload Checklist

Before you upload, verify locally:

```bash
cd Project1_Chem_space_antimalarial_V7_CorrectedGrid/zenodo_package_P1

# 1. Verify all checksums match
sha256sum -c sha256sums.txt
# Expected: All OK, no mismatches

# 2. Count files
find . -type f | wc -l
# Expected: 219 (218 content + 1 sha256sums.txt)

# 3. Check package size
du -sh .
# Expected: ~4.4 MB

# 4. Verify key files exist
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt data/ results/ scripts/ documentation/
# Expected: All present
```

If all checks pass ✅ → proceed to upload.

---

## Upload to Zenodo (Web Interface)

### Step 1: Access Reserved Deposit

1. Go to: https://zenodo.org/deposit/22686176
2. Log in with your Zenodo account
3. You should see the reserved deposit with DOI `10.5281/zenodo.22686176`

### Step 2: Fill Metadata

Copy-paste the following into Zenodo's metadata fields:

**Title**:
```
P1 V8 Reproducibility Package — JCIM Revision: Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes
```

**Authors** (in order, with ORCIDs):
1. Sao Temgoua, Myke Vital → ORCID: 0009-0004-5170-2309
2. Tchapet Njafa, Jean-Pierre → ORCID: 0000-0002-1936-8353
3. Samafou, Penabei → (no ORCID)
4. Fon Mbacham, Wilfred → ORCID: 0000-0002-3934-3233
5. Nana Engo, Serge Guy → ORCID: 0000-0002-7484-3508

**Description**:
```
Complete reproducibility records for the V8 revision of "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis" submitted to the Journal of Chemical Information and Modeling (manuscript ID: ci-2026-00578g).

This deposit provides:
- Core datasets (17-member cohort with SMILES, RRS profiles, polypharmacology metrics)
- Revision analyses (PfCRT re-docking, retrospective control with 5 approved antimalarials, DEKOIS 2.0 two-arm validation)
- Analysis scripts (Python 3.11+ with malaria_md conda environment)
- Complete documentation (DAR, submission manifest, reviewer response summary)

All files are sha256-verified. Addresses Reviewer R2.6 requirement for maintained repository with license and archival DOI. See README.md for complete usage instructions.
```

**Keywords** (comma-separated):
```
antimalarial, polypharmacology, resistance resilience, virtual screening, AutoDock Vina, computational chemistry, Plasmodium falciparum, natural products, African plant metabolites, drug discovery, docking, mutation profiling, JCIM
```

**License**:
- Select: **Creative Commons Attribution 4.0 International (CC BY 4.0)**

**Upload type**:
- Select: **Dataset**

**Related identifiers**:
- Add: "is supplement to" → (leave blank for now, add manuscript DOI when assigned)
- Add: "is derived from" → https://doi.org/10.2210/pdb1J3I/pdb (PfDHFR)
- Add: "is derived from" → https://doi.org/10.2210/pdb6UKJ/pdb (PfCRT)
- Add: "is derived from" → https://doi.org/10.2210/pdb2F6I/pdb (PfClpP)
- Add: "is derived from" → https://doi.org/10.2210/pdb6OBE/pdb (PfATP4)

**Funding** (optional):
- Leave blank unless you have specific grant numbers

### Step 3: Upload Files

**Option A: Drag-and-drop (recommended)**
1. In the "Files" section, drag the entire `zenodo_package_P1/` folder
2. Wait for all 218 files to upload (may take 5-10 minutes depending on connection)
3. Zenodo will automatically compute checksums

**Option B: ZIP and upload**
1. Create a ZIP archive locally:
   ```bash
   cd Project1_Chem_space_antimalarial_V7_CorrectedGrid
   zip -r zenodo_package_P1.zip zenodo_package_P1/
   ```
2. Upload `zenodo_package_P1.zip` to Zenodo
3. Users will download the ZIP and extract locally

**Recommended**: Option A (individual files) for better file-level access and Zenodo's automatic checksumming.

### Step 4: Pre-Publish Verification

Before clicking "Publish":

1. **Download test**: Download `sha256sums.txt` from Zenodo preview
2. **Spot-check**: Download 2-3 random files and verify their checksums:
   ```bash
   sha256sum data/v7_candidate_manifest.csv
   # Compare to sha256sums.txt
   ```
3. **File count**: Verify Zenodo shows 219 files (or 1 ZIP file)
4. **Metadata review**: Double-check all author names, ORCIDs, title, keywords
5. **License check**: Confirm CC BY 4.0 is selected

If all checks pass ✅ → proceed to publish.

### Step 5: Publish

1. Click **"Publish"** button
2. ⚠️ **IMPORTANT**: Once published, the deposit is **immutable**
   - You cannot delete or modify files
   - You can only add a new version (v2, v3, etc.)
3. Confirm publication
4. **DOI becomes active immediately**

### Step 6: Post-Publish Verification

After publishing:

1. **Verify DOI resolves**:
   - Open: https://doi.org/10.5281/zenodo.22686176
   - Should redirect to Zenodo deposit page
   - If 404 → wait 10-15 minutes for DOI propagation

2. **Download verification**:
   ```bash
   # Download sha256sums.txt from Zenodo
   wget https://zenodo.org/records/22686176/files/sha256sums.txt
   
   # Download a few files and verify checksums
   wget https://zenodo.org/records/22686176/files/data/v7_candidate_manifest.csv
   sha256sum v7_candidate_manifest.csv
   # Compare to sha256sums.txt
   ```

3. **Test README rendering**:
   - Zenodo should render `README.md` automatically
   - Verify formatting is correct

If all verifications pass ✅ → **Zenodo upload complete!**

---

## Post-Upload: Update Manuscript (Already Done!)

The DOI is **already inserted** in these V8 submission files:
- ✅ Main manuscript Data Availability section
- ✅ Supporting Information Reproducibility section
- ✅ Response to Reviewers R2.6

**No changes needed** — just verify the DOI resolves before final JCIM submission.

---

## Post-Upload: Make GitHub Repository Public

After Zenodo DOI is confirmed working:

1. Go to: https://github.com/NanaEngo/Malaria_codesV2/settings
2. Scroll to **"Danger Zone"**
3. Click **"Change repository visibility"** → **"Make public"**
4. Type repository name to confirm
5. Create a release tag:
   ```bash
   cd ~/Documents/GitHub/SAO/Malaria_codesV2
   git tag -a v8-jcim-resubmission -m "P1 V8 JCIM resubmission with Zenodo DOI 10.5281/zenodo.22686176"
   git push origin v8-jcim-resubmission
   ```

---

## Troubleshooting

### Upload times out or fails
- **Solution 1**: Use ZIP upload (Option B above)
- **Solution 2**: Split into smaller batches (upload `data/`, `results/`, etc. separately)
- **Solution 3**: Use Zenodo CLI:
  ```bash
  pip install zenodo-cli
  zenodo upload --deposit-id 22686176 --file zenodo_package_P1.zip
  ```

### Checksums don't match after download
- Zenodo may re-compress files
- Try downloading raw files (not ZIP preview)
- If persistent, contact Zenodo support: info@zenodo.org

### DOI doesn't resolve after 30 minutes
- Check Zenodo deposit page directly (without DOI redirect)
- Contact Zenodo support if DOI redirect fails

### Need to correct a file after publishing
- **Cannot modify published version**
- Upload a **new version** (v2):
  1. Go to published deposit
  2. Click "New version"
  3. Upload corrected file(s)
  4. Publish v2
  5. DOI remains the same, but users see "Version 2"

---

## Final Checklist

Before closing this task, confirm:

- [ ] Zenodo DOI resolves: https://doi.org/10.5281/zenodo.22686176
- [ ] Downloaded 3 random files and verified checksums match
- [ ] README.md renders correctly on Zenodo
- [ ] All 218 files are accessible for download
- [ ] Manuscript Data Availability statement matches DOI (already done)
- [ ] GitHub repository will be made public (after DOI verification)

---

**Contact for issues**:
- Zenodo support: info@zenodo.org
- Manuscript corresponding author: myke-vital.sao@facsciences-uy1.cm

**Last updated**: 2026-09-10  
**Prepared by**: Kiro AI agent
