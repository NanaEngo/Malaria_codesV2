# Quick Upload Guide — Zenodo P2 Package

**Package location**: `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/`  
**Reserved DOI**: ⚠️ **TO BE RESERVED** → https://doi.org/10.5281/zenodo.XXXXXXX  
**Status**: Ready to upload after DOI reservation

---

## Pre-Upload Checklist

Before you upload, verify locally:

```bash
cd Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2

# 1. Verify all checksums match (after sha256sums.txt is generated)
sha256sum -c sha256sums.txt
# Expected: All OK, no mismatches

# 2. Check package structure
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt data/ results/ scripts/ documentation/
# Expected: All present

# 3. Check total size
du -sh .
# Expected: ~500 MB
```

If all checks pass ✅ → proceed to upload.

---

## Upload to Zenodo (Web Interface)

### Step 1: Reserve DOI (If Not Done)

1. Go to: https://zenodo.org
2. Log in with your Zenodo account
3. Click **"New upload"**
4. Fill title:
   ```
   P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads
   ```
5. Add authors (see below)
6. Click **"Save"** (do NOT upload files yet)
7. Copy the reserved DOI (format: `10.5281/zenodo.XXXXXXX`)
8. Update this file, MANIFEST.json, and README.md with the reserved DOI

### Step 2: Access Reserved Deposit

1. Go to: https://zenodo.org/deposit/XXXXXXX (replace with your DOI number)
2. Log in with your Zenodo account
3. You should see the reserved deposit

### Step 3: Fill Metadata

Copy-paste the following into Zenodo's metadata fields:

**Title**:
```
P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads
```

**Authors** (in order, with ORCIDs):
1. Sao Temgoua, Myke Vital → ORCID: 0009-0004-5170-2309
2. Tchapet Njafa, Jean-Pierre → ORCID: 0000-0002-1936-8353
3. Samafou, Penabei → (no ORCID)
4. Fon Mbacham, Wilfred → ORCID: 0000-0002-3934-3233
5. Nana Engo, Serge Guy → ORCID: 0000-0002-7484-3508

**Description**:
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
- Docking-RRS as positive triage filter for prospective experimental validation

All files are sha256-verified. See README.md for complete usage instructions.
```

**Keywords** (comma-separated):
```
antimalarial, drug resistance, polypharmacology, molecular dynamics, docking, PfDHFR, PfCRT, resistance retention score, African natural products, Plasmodium falciparum, MD validation, MM-GBSA, GROMACS, estimand divergence, virtual screening, JCIM
```

**License**:
- Select: **Creative Commons Attribution 4.0 International (CC BY 4.0)**

**Upload type**:
- Select: **Dataset**

**Related identifiers**:
- Add: "is supplement to" → (manuscript DOI when assigned)
- Add: "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1 deposit)
- Add: "is related to" → https://doi.org/10.5281/zenodo.19608875 (P3 deposit)

**Funding** (optional):
- Leave blank unless you have specific grant numbers

### Step 4: Upload Files

**Option A: Drag-and-drop (recommended)**
1. In the "Files" section, drag the entire `zenodo_package_P2/` folder
2. Wait for all files to upload
3. Zenodo will automatically compute checksums

**Option B: ZIP and upload**
1. Create a ZIP archive locally:
   ```bash
   cd Project2_Polypharmacology_MD_ValidationV2607
   zip -r zenodo_package_P2.zip zenodo_package_P2/
   ```
2. Upload `zenodo_package_P2.zip` to Zenodo

**Recommended**: Option A (individual files) for better file-level access.

**Note**: P2 package is ~500 MB. Upload may take 10-30 minutes depending on connection speed.

### Step 5: Pre-Publish Verification

Before clicking "Publish":

1. **Download test**: Download `sha256sums.txt` from Zenodo preview
2. **Spot-check**: Download 2-3 random files and verify checksums:
   ```bash
   # Example verification
   sha256sum -c sha256sums.txt
   ```
3. **Metadata review**: Double-check all author names, ORCIDs, title, keywords
4. **License check**: Confirm CC BY 4.0 is selected

If all checks pass ✅ → proceed to publish.

### Step 6: Publish

1. Click **"Publish"** button
2. ⚠️ **IMPORTANT**: Once published, the deposit is **immutable**
3. Confirm publication
4. **DOI becomes active immediately**

### Step 7: Post-Publish Verification

After publishing:

1. **Verify DOI resolves**: https://doi.org/10.5281/zenodo.XXXXXXX
2. **Download verification**: Test a few files from different subdirectories
3. **Test README rendering**: Verify markdown formatting on Zenodo
4. **Check file structure**: Ensure directory hierarchy is preserved

If all verifications pass ✅ → **Zenodo upload complete!**

---

## Post-Upload: Update Manuscript

Insert the DOI in the manuscript Data Availability section:

**File**: `manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`

```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

---

## Post-Upload: Create Git Tag

After Zenodo DOI is confirmed working:

```bash
cd ~/Documents/GitHub/Malaria_codesV2
git tag -a p2-jcim-submission -m "P2 JCIM V2609C submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"
git push origin p2-jcim-submission
```

---

## Troubleshooting

### Upload times out or fails
- Use ZIP upload (Option B)
- Try uploading subdirectories separately (data/, results/, scripts/, documentation/)
- Check internet connection stability

### Checksums don't match after download
- Try downloading raw files (not ZIP preview)
- Verify you're comparing the same file versions
- Contact Zenodo support: info@zenodo.org

### DOI doesn't resolve after 30 minutes
- Check deposit page directly on Zenodo
- Clear browser cache and try again
- Contact Zenodo support: info@zenodo.org

### Need to correct a file after publishing
- Upload a **new version** (v2)
- DOI remains the same
- Previous versions remain accessible

### File size concerns
- Current package: ~500 MB (well within Zenodo's 50 GB limit)
- If needed, can compress trajectory files further
- Contact Zenodo for larger deposits

---

## Final Checklist

- [ ] Zenodo DOI reserved and URL updated in this file
- [ ] All package files present and checksums verified
- [ ] Metadata complete (title, authors, description, keywords)
- [ ] Files uploaded to Zenodo
- [ ] Pre-publish verification complete
- [ ] Deposit published on Zenodo
- [ ] DOI resolves: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] Downloaded 3 random files and verified checksums
- [ ] README.md renders correctly on Zenodo
- [ ] Manuscript Data Availability statement updated
- [ ] Git tag created and pushed

---

## Key Files in Package

```
zenodo_package_P2/
├── README.md                      # Complete usage guide
├── MANIFEST.json                  # Structured metadata
├── UPLOAD_INSTRUCTIONS.md         # This file
├── UPLOAD_CHECKLIST.md           # Step-by-step checklist
├── LICENSE.txt                    # CC BY 4.0
├── sha256sums.txt                # SHA-256 checksums
├── data/                          # Core datasets
│   ├── c_rrs_classification.csv
│   ├── c_pns_ranking.csv
│   ├── set_c_trajectory_metrics_pilot.csv
│   └── external_docking_scores.csv
├── results/                       # Benchmark outputs
│   ├── md_rrs_discriminative_pilot.csv
│   ├── mmgbsa_summary_pilot.csv
│   ├── md_vs_docking_comparison_pilot.csv
│   └── external_docking_rrs_20260827.csv
├── scripts/                       # Reproduction scripts
│   ├── p2_rigorous_audit.py
│   ├── set_c_trajectory_qc.py
│   ├── p2_setc_md_rrs.py
│   └── environment.yml
└── documentation/                 # Supporting docs
    ├── P2_DATA_ANALYSIS_REPORT.md
    ├── MMGBSA_JUSTIFICATION_ADDENDUM.md
    └── Methods supplements
```

---

**Contact for issues**:
- Zenodo support: info@zenodo.org
- Corresponding author: myke-vital.sao@facsciences-uy1.cm

**Last updated**: 2026-09-16  
**Prepared by**: Kiro AI agent
