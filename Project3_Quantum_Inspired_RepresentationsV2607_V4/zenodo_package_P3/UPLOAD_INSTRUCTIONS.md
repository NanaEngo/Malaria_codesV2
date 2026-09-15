# Quick Upload Guide — Zenodo P3 Package

**Package location**: `Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/`  
**Reserved DOI**: https://doi.org/10.5281/zenodo.19608875  
**Status**: ✅ Ready to upload (staged, pending file collection)

---

## Pre-Upload Checklist

Before you upload, verify locally:

```bash
cd Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3

# 1. Verify all checksums match (after sha256sums.txt is generated)
sha256sum -c sha256sums.txt
# Expected: All OK, no mismatches

# 2. Check package structure
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt data/ results/ scripts/ documentation/
# Expected: All present
```

If all checks pass ✅ → proceed to upload.

---

## Upload to Zenodo (Web Interface)

### Step 1: Access Reserved Deposit

1. Go to: https://zenodo.org/deposit/19608875
2. Log in with your Zenodo account
3. You should see the reserved deposit with DOI `10.5281/zenodo.19608875`

### Step 2: Fill Metadata

Copy-paste the following into Zenodo's metadata fields:

**Title**:
```
P3 Reproducibility Package — JCAMD Submission: Quantum-inspired molecular representations for African antimalarial candidates
```

**Authors** (in order, with ORCIDs):
1. Sao Temgoua, Myke Vital → ORCID: 0009-0004-5170-2309
2. Tchapet Njafa, Jean-Pierre → ORCID: 0000-0002-1936-8353
3. Samafou, Penabei → (no ORCID)
4. Fon Mbacham, Wilfred → ORCID: 0000-0002-3934-3233
5. Nana Engo, Serge Guy → ORCID: 0000-0002-7484-3508

**Description**:
```
Complete reproducibility records for "Quantum-inspired molecular representations for African antimalarial candidates: topological fingerprints, tensor network embeddings, and kernel methods" submitted to the Journal of Computer-Aided Molecular Design (JCAMD).

This deposit provides:
- Core datasets (19,849 molecules with TFP, TNE, QKS representations)
- Benchmark results (5-fold CV, external ChEMBL validation)
- Regression analyses (docking score correlations)
- Analysis scripts (Python 3.11+ with malaria_md environment)
- Complete documentation (DAR, methods supplement, results summary)

Key finding: None of the quantum-inspired representations (TFP, TNE, QKS) outperforms classical ECFP4 fingerprints under the tested protocols, though they provide diagnostic and interpretive value.

All files are sha256-verified. See README.md for complete usage instructions.
```

**Keywords** (comma-separated):
```
antimalarial, quantum-inspired, topological data analysis, persistent homology, tensor networks, quantum kernels, molecular representations, machine learning, drug discovery, Plasmodium falciparum, natural products, African plant metabolites, JCAMD
```

**License**:
- Select: **Creative Commons Attribution 4.0 International (CC BY 4.0)**

**Upload type**:
- Select: **Dataset**

**Related identifiers**:
- Add: "is supplement to" → (manuscript DOI when assigned)
- Add: "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1 deposit)

**Funding** (optional):
- Leave blank unless you have specific grant numbers

### Step 3: Upload Files

**Option A: Drag-and-drop (recommended)**
1. In the "Files" section, drag the entire `zenodo_package_P3/` folder
2. Wait for all files to upload
3. Zenodo will automatically compute checksums

**Option B: ZIP and upload**
1. Create a ZIP archive locally:
   ```bash
   cd Project3_Quantum_Inspired_RepresentationsV2607_V4
   zip -r zenodo_package_P3.zip zenodo_package_P3/
   ```
2. Upload `zenodo_package_P3.zip` to Zenodo

**Recommended**: Option A (individual files) for better file-level access.

### Step 4: Pre-Publish Verification

Before clicking "Publish":

1. **Download test**: Download `sha256sums.txt` from Zenodo preview
2. **Spot-check**: Download 2-3 random files and verify checksums
3. **Metadata review**: Double-check all author names, ORCIDs, title, keywords
4. **License check**: Confirm CC BY 4.0 is selected

If all checks pass ✅ → proceed to publish.

### Step 5: Publish

1. Click **"Publish"** button
2. ⚠️ **IMPORTANT**: Once published, the deposit is **immutable**
3. Confirm publication
4. **DOI becomes active immediately**

### Step 6: Post-Publish Verification

After publishing:

1. **Verify DOI resolves**: https://doi.org/10.5281/zenodo.19608875
2. **Download verification**: Test a few files
3. **Test README rendering**: Verify markdown formatting

If all verifications pass ✅ → **Zenodo upload complete!**

---

## Post-Upload: Update Manuscript

Insert the DOI in the manuscript Data Availability section:

```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: \url{https://doi.org/10.5281/zenodo.19608875}.
```

---

## Post-Upload: Make GitHub Repository Public

After Zenodo DOI is confirmed working:

1. Go to: https://github.com/NanaEngo/Malaria_codesV2/settings
2. Scroll to **"Danger Zone"**
3. Click **"Change repository visibility"** → **"Make public"**
4. Create a release tag:
   ```bash
   cd ~/Documents/GitHub/Malaria_codesV2
   git tag -a p3-jcamd-submission -m "P3 JCAMD submission with Zenodo DOI 10.5281/zenodo.19608875"
   git push origin p3-jcamd-submission
   ```

---

## Troubleshooting

### Upload times out or fails
- Use ZIP upload (Option B)
- Split into smaller batches

### Checksums don't match after download
- Try downloading raw files (not ZIP preview)
- Contact Zenodo support: info@zenodo.org

### DOI doesn't resolve after 30 minutes
- Contact Zenodo support

### Need to correct a file after publishing
- Upload a **new version** (v2)
- DOI remains the same

---

## Final Checklist

- [ ] Zenodo DOI resolves: https://doi.org/10.5281/zenodo.19608875
- [ ] Downloaded 3 random files and verified checksums
- [ ] README.md renders correctly on Zenodo
- [ ] Manuscript Data Availability statement updated
- [ ] GitHub repository public (after DOI verification)

---

**Contact for issues**:
- Zenodo support: info@zenodo.org
- Corresponding author: myke-vital.sao@facsciences-uy1.cm

**Last updated**: 2026-09-11  
**Prepared by**: Kiro AI agent
