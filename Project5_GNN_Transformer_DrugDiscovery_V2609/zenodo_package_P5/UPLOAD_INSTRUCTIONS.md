# Quick Upload Guide — Zenodo P5 Package

**Package location**: `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/`  
**Reserved DOI**: ⚠️ **TO BE RESERVED** → https://doi.org/10.5281/zenodo.XXXXXXX  
**Status**: Ready to upload after DOI reservation

---

## Pre-Upload Checklist

Before you upload, verify locally:

```bash
cd Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5

# 1. Verify all checksums match (after sha256sums.txt is generated)
sha256sum -c sha256sums.txt
# Expected: All OK, no mismatches

# 2. Check package structure
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt data/ results/ scripts/ documentation/
# Expected: All present

# 3. Check total size
du -sh .
# Expected: ~2 GB (extended campaign results are large)
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
   P5 Reproducibility Package — JCAMD Submission: Graph neural networks and transformers for antimalarial drug discovery under distribution shift
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
P5 Reproducibility Package — JCAMD Submission: Graph neural networks and transformers for antimalarial drug discovery under distribution shift
```

**Authors** (in order, with ORCIDs):
1. Sao Temgoua, Myke Vital → ORCID: 0009-0004-5170-2309
2. Tchapet Njafa, Jean-Pierre → ORCID: 0000-0002-1936-8353
3. Samafou, Penabei → (no ORCID)
4. Fon Mbacham, Wilfred → ORCID: 0000-0002-3934-3233
5. Nana Engo, Serge Guy → ORCID: 0000-0002-7484-3508

**Description**:
```
Complete reproducibility records for "Graph neural networks and transformers for antimalarial drug discovery: honest-negative results under distribution shift" submitted to the Journal of Computer-Aided Molecular Design (JCAMD).

This deposit provides:
- Core dataset (19,836 molecules from African natural product-inspired library)
- Benchmark results (5 GNN/Transformer architectures vs ECFP4-RF baseline)
- Random and scaffold split evaluations (5-fold cross-validation, 5 seeds)
- Extended robustness campaign (25 configurations, 625 fold-seed records)
- External validation (22,267 molecule ChEMBL-derived disjoint panel)
- Structural complexity analysis (Fsp3 ≥0.45, rings ≥4 cohorts)
- Topological fusion results (GIN-TFP, GIN-TNE integrating P3 representations)
- ChemBERTa sequence model benchmarks (125/125 configurations complete)
- Distance-aware conformal triage filter (NN-Tanimoto + ECE calibration)
- Analysis scripts (Python 3.11+ with malaria_md environment, PyTorch 2.13.0, PyG 2.8.0)
- Complete documentation (DAR, methods supplements, theoretical framework)

Key findings: 
- ECFP4-RF baseline dominates under scaffold split (0.8300 vs GIN 0.8047, GIN-TFP 0.8138)
- Honest-negative result: GNNs/Transformers do not outperform classical fingerprints at this scale
- 1-WL expressivity bottleneck on complex African NP topologies (Fsp3 ≥0.45, rings ≥4)
- Topological fusion (TFP) provides modest +0.0091 AUC gain under scaffold split
- Distance-aware triage filter boosts OOD screening precision by +14.2%
- Performance ordering invariant across 5 split families and 3 capacity settings

All files are sha256-verified. See README.md for complete usage instructions.
```

**Keywords** (comma-separated):
```
antimalarial, graph neural networks, GNN, transformers, ChemBERTa, drug discovery, distribution shift, scaffold split, African natural products, Plasmodium falciparum, ECFP4, topological data analysis, PyTorch Geometric, molecular machine learning, honest-negative results, conformal prediction, JCAMD
```

**License**:
- Select: **Creative Commons Attribution 4.0 International (CC BY 4.0)**

**Upload type**:
- Select: **Dataset**

**Related identifiers**:
- Add: "is supplement to" → (manuscript DOI when assigned)
- Add: "is related to" → https://doi.org/10.5281/zenodo.19608875 (P3 deposit - provides TFP/TNE features)
- Add: "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1 deposit - upstream library)

**Funding** (optional):
- Leave blank unless you have specific grant numbers

### Step 4: Upload Files

**Option A: Drag-and-drop (if manageable)**
1. In the "Files" section, drag the entire `zenodo_package_P5/` folder
2. Wait for all files to upload (may take 1-2 hours for ~2 GB)
3. Zenodo will automatically compute checksums

**Option B: ZIP and upload (recommended for large packages)**
1. Create a ZIP archive locally:
   ```bash
   cd Project5_GNN_Transformer_DrugDiscovery_V2609
   zip -r zenodo_package_P5.zip zenodo_package_P5/
   ```
2. Upload `zenodo_package_P5.zip` to Zenodo

**Option C: Upload subdirectories separately**
1. Create separate ZIPs for large subdirectories:
   ```bash
   cd zenodo_package_P5
   zip -r data.zip data/
   zip -r results.zip results/
   zip -r scripts.zip scripts/
   zip -r documentation.zip documentation/
   ```
2. Upload each ZIP separately with clear naming

**Recommended**: Option B (single ZIP) for simplicity, or Option C if upload times out.

**Note**: P5 package is ~2 GB. Upload may take 1-2 hours depending on connection speed.

### Step 5: Pre-Publish Verification

Before clicking "Publish":

1. **Download test**: Download `sha256sums.txt` from Zenodo preview
2. **Spot-check**: Download 3-5 random files and verify checksums:
   ```bash
   # Example verification
   sha256sum -c sha256sums.txt
   ```
3. **Metadata review**: Double-check all author names, ORCIDs, title, keywords
4. **License check**: Confirm CC BY 4.0 is selected
5. **Size check**: Verify total uploaded size matches local package

If all checks pass ✅ → proceed to publish.

### Step 6: Publish

1. Click **"Publish"** button
2. ⚠️ **IMPORTANT**: Once published, the deposit is **immutable**
3. Confirm publication
4. **DOI becomes active immediately**

### Step 7: Post-Publish Verification

After publishing:

1. **Verify DOI resolves**: https://doi.org/10.5281/zenodo.XXXXXXX
2. **Download verification**: Test files from each subdirectory
3. **Test README rendering**: Verify markdown formatting on Zenodo
4. **Check file structure**: Ensure directory hierarchy is preserved or ZIP is accessible

If all verifications pass ✅ → **Zenodo upload complete!**

---

## Post-Upload: Update Manuscript

Insert the DOI in the manuscript Data Availability section (when manuscript is finalized):

**File**: `manuscript/[VERSION]/GNN_Transformer_DrugDiscovery_[VERSION].tex`

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
git tag -a p5-jcamd-submission -m "P5 JCAMD submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"
git push origin p5-jcamd-submission
```

---

## Troubleshooting

### Upload times out or fails (common for 2GB package)
- Use ZIP upload (Option B)
- Try uploading subdirectories separately (Option C)
- Upload during off-peak hours for better speed
- Check internet connection stability

### Large file handling
- P5 extended campaign results are ~2 GB
- Zenodo supports up to 50 GB per deposit
- If needed, can exclude auxiliary campaign files
- Contact Zenodo for optimization advice

### Checksums don't match after download
- If uploaded as ZIP, download and extract first
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

---

## Final Checklist

- [ ] Zenodo DOI reserved and URL updated in this file
- [ ] All package files present and checksums verified
- [ ] Metadata complete (title, authors, description, keywords)
- [ ] Files uploaded to Zenodo (may take 1-2 hours for 2GB)
- [ ] Pre-publish verification complete
- [ ] Deposit published on Zenodo
- [ ] DOI resolves: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] Downloaded 3-5 random files and verified checksums
- [ ] README.md renders correctly on Zenodo
- [ ] Manuscript Data Availability statement updated (when ready)
- [ ] Git tag created and pushed

---

## Key Files in Package

```
zenodo_package_P5/
├── README.md                      # Complete usage guide
├── MANIFEST.json                  # Structured metadata
├── UPLOAD_INSTRUCTIONS.md         # This file
├── UPLOAD_CHECKLIST.md           # Step-by-step checklist
├── LICENSE.txt                    # CC BY 4.0
├── sha256sums.txt                # SHA-256 checksums
├── data/                          # Core datasets
│   ├── p5_canonical_panel.csv
│   ├── p5_labels_production.csv
│   └── p5_public_chembl_malaria_disjoint.csv
├── results/                       # Benchmark outputs
│   ├── p5_ecfp4rf_random_baseline.json
│   ├── p5_gin_random_results.csv
│   ├── p5_gin_scaffold_results.csv
│   ├── p5_replication_stats.csv
│   ├── extended_campaign_20260825/
│   ├── chemberta_125_configs/
│   └── structural_complexity_cohorts/
├── scripts/                       # Reproduction scripts
│   ├── p5_benchmark.py
│   ├── p5_extended_campaign.py
│   ├── p5_chemberta_pipeline.py
│   └── environment.yml
└── documentation/                 # Supporting docs
    ├── P5_DATA_ANALYSIS_REPORT.md
    ├── P5_METHODS_SUPPLEMENT.md
    └── ADR_P5_STRATEGIC_PIVOT_V2609.md
```

---

**Contact for issues**:
- Zenodo support: info@zenodo.org
- Corresponding author: myke-vital.sao@facsciences-uy1.cm

**Last updated**: 2026-09-16  
**Prepared by**: Kiro AI agent
