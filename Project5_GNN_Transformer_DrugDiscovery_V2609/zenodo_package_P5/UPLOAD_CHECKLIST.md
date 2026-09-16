# P5 Zenodo Upload Checklist

**DOI:** ⚠️ **TO BE RESERVED** → https://doi.org/10.5281/zenodo.XXXXXXX  
**Package:** `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/`  
**Status:** Ready for upload after DOI reservation

---

## Phase 1: Pre-Upload Preparation

### Package Verification
- [ ] Navigate to package: `cd zenodo_package_P5/`
- [ ] Verify checksums: `sha256sum -c sha256sums.txt` → All OK
- [ ] Check package size: `du -sh .` → ~2 GB
- [ ] Verify all key files present:
  - [ ] README.md
  - [ ] MANIFEST.json
  - [ ] LICENSE.txt
  - [ ] sha256sums.txt
  - [ ] data/ directory
  - [ ] results/ directory (largest component)
  - [ ] scripts/ directory
  - [ ] documentation/ directory

### Create Upload Package
- [ ] Option A: Will upload individual files (if feasible)
- [ ] Option B: Create ZIP: `zip -r ../zenodo_p5_upload.zip .` ✓ (recommended)
- [ ] Option C: Create separate subdirectory ZIPs (if upload times out)

---

## Phase 2: Zenodo DOI Reservation

### Reserve DOI
- [ ] Go to: https://zenodo.org
- [ ] Click "New upload"
- [ ] Fill title: "P5 Reproducibility Package — JCAMD Submission: Graph neural networks and transformers for antimalarial drug discovery under distribution shift"
- [ ] Add authors with ORCIDs (see UPLOAD_INSTRUCTIONS.md)
- [ ] Click "Save" (do NOT upload yet)
- [ ] Copy reserved DOI: `10.5281/zenodo.XXXXXXX`

### Update Package Files
- [ ] Update MANIFEST.json: `"doi_reserved": "https://doi.org/..."`
- [ ] Update README.md: DOI in header
- [ ] Update UPLOAD_INSTRUCTIONS.md: Replace XXXXXXX with actual DOI
- [ ] Update this checklist: Replace XXXXXXX with actual DOI

---

## Phase 3: Metadata Entry

Access deposit: https://zenodo.org/deposit/XXXXXXX

### Basic Information
- [ ] **Title**: P5 Reproducibility Package — JCAMD Submission: Graph neural networks and transformers for antimalarial drug discovery under distribution shift
- [ ] **Upload type**: Dataset
- [ ] **Publication date**: (today's date)

### Authors (in order)
- [ ] Sao Temgoua, Myke Vital (ORCID: 0009-0004-5170-2309)
- [ ] Tchapet Njafa, Jean-Pierre (ORCID: 0000-0002-1936-8353)
- [ ] Samafou, Penabei (no ORCID)
- [ ] Fon Mbacham, Wilfred (ORCID: 0000-0002-3934-3233)
- [ ] Nana Engo, Serge Guy (ORCID: 0000-0002-7484-3508)

### Description
- [ ] Copy full description from UPLOAD_INSTRUCTIONS.md
- [ ] Verify all key findings listed
- [ ] Verify reference to README.md for usage instructions

### Keywords
- [ ] antimalarial
- [ ] graph neural networks
- [ ] GNN
- [ ] transformers
- [ ] ChemBERTa
- [ ] drug discovery
- [ ] distribution shift
- [ ] scaffold split
- [ ] African natural products
- [ ] Plasmodium falciparum
- [ ] ECFP4
- [ ] topological data analysis
- [ ] PyTorch Geometric
- [ ] molecular machine learning
- [ ] honest-negative results
- [ ] conformal prediction
- [ ] JCAMD

### Additional Metadata
- [ ] **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- [ ] **Related identifiers**:
  - [ ] "is supplement to" → (manuscript DOI when assigned)
  - [ ] "is related to" → https://doi.org/10.5281/zenodo.19608875 (P3)
  - [ ] "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1)

---

## Phase 4: File Upload

### Upload Files
- [ ] Choose upload method (Option B ZIP recommended for 2GB package)
- [ ] Start upload process
- [ ] Monitor upload progress (estimate: 1-2 hours for ~2 GB)
- [ ] Verify upload completed successfully
- [ ] Check that files are accessible in Zenodo preview

### Verify Upload
- [ ] All expected files/directories present
- [ ] Total size ~2 GB
- [ ] No upload errors reported
- [ ] ZIP extraction works (if applicable)

---

## Phase 5: Pre-Publish Verification

### Download Tests
- [ ] Download `sha256sums.txt` from Zenodo preview
- [ ] Download `README.md` and verify it matches local
- [ ] Download 3-5 files from different subdirectories:
  - [ ] `data/p5_canonical_panel.csv`
  - [ ] `results/p5_replication_stats.csv`
  - [ ] `results/extended_campaign_20260825/` sample file
  - [ ] `scripts/p5_benchmark.py`
  - [ ] `documentation/P5_DATA_ANALYSIS_REPORT.md`
- [ ] Verify checksums of downloaded files

### Metadata Review
- [ ] Title correct and complete
- [ ] All 5 authors listed in correct order
- [ ] All ORCIDs entered correctly
- [ ] Description complete with all key points
- [ ] All 17 keywords entered
- [ ] License is CC BY 4.0
- [ ] Upload type is Dataset
- [ ] Related identifiers added

### Content Review
- [ ] README.md renders correctly (markdown formatting)
- [ ] File hierarchy preserved (or ZIP is accessible)
- [ ] No missing files or directories
- [ ] Checksums file accessible

---

## Phase 6: Publish

### Final Checks
- [ ] All above items completed ✓
- [ ] Confident all information correct
- [ ] Understand publication is **irreversible**

### Publish Deposit
- [ ] Click "Publish" button
- [ ] Read and confirm warning
- [ ] Confirm publication
- [ ] Wait for confirmation message (may take longer for large deposit)

---

## Phase 7: Post-Publish Verification

### DOI Verification
- [ ] DOI resolves: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] Landing page loads correctly
- [ ] All metadata displays correctly
- [ ] Files are accessible for download

### Download Verification
- [ ] Download and verify checksums for:
  - [ ] `data/p5_canonical_panel.csv`
  - [ ] `results/p5_ecfp4rf_random_baseline.json`
  - [ ] `results/p5_replication_stats.csv`
  - [ ] `scripts/p5_benchmark.py`
  - [ ] `documentation/P5_DATA_ANALYSIS_REPORT.md`
- [ ] All checksums match `sha256sums.txt`

### Presentation Verification
- [ ] README.md displays correctly
- [ ] MANIFEST.json is readable
- [ ] Directory structure clear (or ZIP extraction straightforward)
- [ ] All documentation accessible

---

## Phase 8: Manuscript Update

### Update Manuscript (When Finalized)
- [ ] Identify manuscript version for submission
- [ ] Open main manuscript .tex file
- [ ] Locate or create Data Availability section
- [ ] Add DOI: `\url{https://doi.org/10.5281/zenodo.XXXXXXX}`
- [ ] Compile manuscript to verify LaTeX compiles
- [ ] Verify DOI hyperlink works in PDF

### Update Bibliography (if needed)
- [ ] Add Zenodo dataset citation to bibliography
- [ ] Format: `@misc{zenodo_p5, author = {...}, title = {...}, year = {2026}, doi = {10.5281/zenodo.XXXXXXX}, url = {...}}`
- [ ] Compile and verify citation renders correctly

---

## Phase 9: Repository Updates

### Update AGENTS.md
- [ ] Update P5 Zenodo status line
- [ ] Change from "reserved / upload pending" to "published"
- [ ] Add actual DOI

### Create Git Tag
- [ ] Navigate to repository root
- [ ] Create tag: `git tag -a p5-jcamd-submission -m "P5 JCAMD submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"`
- [ ] Push tag: `git push origin p5-jcamd-submission`
- [ ] Verify tag visible on GitHub

### Commit Updates
- [ ] Stage manuscript updates (when applicable)
- [ ] Stage AGENTS.md update
- [ ] Commit: `git commit -m "Update P5 documentation with Zenodo DOI"`
- [ ] Push: `git push origin main`

---

## Phase 10: Final Documentation

### Create Completion Record
- [ ] Note completion date
- [ ] Record final DOI
- [ ] Note any issues encountered
- [ ] Document resolution of any problems

### Notify Collaborators
- [ ] Inform co-authors that deposit is live
- [ ] Share DOI: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] Provide direct link to Zenodo landing page

---

## Troubleshooting Log

Use this section to document any issues encountered:

### Issue 1:
- **Problem**: 
- **Solution**: 
- **Date**: 

### Issue 2:
- **Problem**: 
- **Solution**: 
- **Date**: 

---

## Special Considerations for P5

### Large File Size (~2 GB)
- [ ] Allow 1-2 hours for upload
- [ ] Use stable internet connection
- [ ] Consider uploading during off-peak hours
- [ ] Have backup plan if upload times out

### Extended Campaign Results
- [ ] 625 fold-seed records included
- [ ] ChemBERTa 125 configurations included
- [ ] Structural complexity cohort analyses included
- [ ] Verify completeness of results/ directory

### External Validation
- [ ] ChEMBL-derived disjoint panel (22,267 molecules) included
- [ ] Verify overlap exclusion documented
- [ ] Verify provenance chain intact

---

## Timeline

- [ ] **Phase 1-2**: Pre-upload preparation and DOI reservation (30 minutes)
- [ ] **Phase 3**: Metadata entry (20 minutes)
- [ ] **Phase 4**: File upload (1-2 hours for 2GB)
- [ ] **Phase 5**: Pre-publish verification (30 minutes)
- [ ] **Phase 6**: Publish (5 minutes)
- [ ] **Phase 7**: Post-publish verification (20 minutes)
- [ ] **Phase 8**: Manuscript update (15 minutes, when ready)
- [ ] **Phase 9**: Repository updates (10 minutes)
- [ ] **Phase 10**: Final documentation (10 minutes)

**Total estimated time**: 3-4 hours (mainly due to upload time)

---

## Completion

- [ ] **ALL PHASES COMPLETE** ✅
- [ ] **Final DOI**: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] **Completion date**: _______________
- [ ] **Completed by**: _______________

---

**Contact for issues**:
- Zenodo support: info@zenodo.org
- Corresponding author: myke-vital.sao@facsciences-uy1.cm

**Last updated**: 2026-09-16  
**Prepared by**: Kiro AI agent
