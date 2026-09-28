# P2 Zenodo Upload Checklist

**DOI:** ⚠️ **TO BE RESERVED** → https://doi.org/10.5281/zenodo.XXXXXXX  
**Package:** `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/`  
**Status:** Ready for upload after DOI reservation

---

## Phase 1: Pre-Upload Preparation

### Package Verification
- [ ] Navigate to package: `cd zenodo_package_P2/`
- [ ] Verify checksums: `sha256sum -c sha256sums.txt` → All OK
- [ ] Check package size: `du -sh .` → ~500 MB
- [ ] Verify all key files present:
  - [ ] README.md
  - [ ] MANIFEST.json
  - [ ] LICENSE.txt
  - [ ] sha256sums.txt
  - [ ] data/ directory
  - [ ] results/ directory
  - [ ] scripts/ directory
  - [ ] documentation/ directory

### Create Upload Package
- [ ] Option A: Will upload individual files (recommended) ✓
- [ ] Option B: Create ZIP: `zip -r ../zenodo_p2_upload.zip .`

---

## Phase 2: Zenodo DOI Reservation

### Reserve DOI
- [ ] Go to: https://zenodo.org
- [ ] Click "New upload"
- [ ] Fill title: "P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads"
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
- [ ] **Title**: P2 Reproducibility Package — JCIM Submission: Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads
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
- [ ] drug resistance
- [ ] polypharmacology
- [ ] molecular dynamics
- [ ] docking
- [ ] PfDHFR
- [ ] PfCRT
- [ ] resistance retention score
- [ ] African natural products
- [ ] Plasmodium falciparum
- [ ] MD validation
- [ ] MM-GBSA
- [ ] GROMACS
- [ ] estimand divergence
- [ ] virtual screening
- [ ] JCIM

### Additional Metadata
- [ ] **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- [ ] **Related identifiers**:
  - [ ] "is supplement to" → (manuscript DOI when assigned)
  - [ ] "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1)
  - [ ] "is related to" → https://doi.org/10.5281/zenodo.19608875 (P3)

---

## Phase 4: File Upload

### Upload Files
- [ ] Choose upload method (Option A recommended)
- [ ] Start upload process
- [ ] Monitor upload progress (estimate: 10-30 minutes for ~500 MB)
- [ ] Verify all files uploaded successfully
- [ ] Check that directory structure preserved

### Verify Upload
- [ ] All subdirectories present (data/, results/, scripts/, documentation/)
- [ ] File count matches local package
- [ ] Total size ~500 MB
- [ ] No upload errors reported

---

## Phase 5: Pre-Publish Verification

### Download Tests
- [ ] Download `sha256sums.txt` from Zenodo preview
- [ ] Download `README.md` and verify it matches local
- [ ] Download 2-3 files from data/ directory
- [ ] Download 2-3 files from results/ directory
- [ ] Verify checksums of downloaded files

### Metadata Review
- [ ] Title correct and complete
- [ ] All 5 authors listed in correct order
- [ ] All ORCIDs entered correctly
- [ ] Description complete with all key points
- [ ] All 16 keywords entered
- [ ] License is CC BY 4.0
- [ ] Upload type is Dataset
- [ ] Related identifiers added

### Content Review
- [ ] README.md renders correctly (markdown formatting)
- [ ] File hierarchy preserved
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
- [ ] Wait for confirmation message

---

## Phase 7: Post-Publish Verification

### DOI Verification
- [ ] DOI resolves: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] Landing page loads correctly
- [ ] All metadata displays correctly
- [ ] Files are accessible for download

### Download Verification
- [ ] Download and verify checksums for:
  - [ ] `data/c_rrs_classification.csv`
  - [ ] `results/md_rrs_discriminative_pilot.csv`
  - [ ] `scripts/p2_rigorous_audit.py`
  - [ ] `documentation/P2_DATA_ANALYSIS_REPORT.md`
- [ ] All checksums match `sha256sums.txt`

### Presentation Verification
- [ ] README.md displays correctly
- [ ] MANIFEST.json is readable
- [ ] Directory structure clear
- [ ] All documentation accessible

---

## Phase 8: Manuscript Update

### Update V2609C Manuscript
- [ ] Open: `manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`
- [ ] Locate Data Availability section
- [ ] Add DOI: `\url{https://doi.org/10.5281/zenodo.XXXXXXX}`
- [ ] Compile manuscript to verify LaTeX compiles
- [ ] Verify DOI hyperlink works in PDF

### Update Bibliography (if needed)
- [ ] Add Zenodo dataset citation to bibliography
- [ ] Format: `@misc{zenodo_p2, author = {...}, title = {...}, year = {2026}, doi = {10.5281/zenodo.XXXXXXX}, url = {...}}`
- [ ] Compile and verify citation renders correctly

---

## Phase 9: Repository Updates

### Update AGENTS.md
- [ ] Update P2 Zenodo status line
- [ ] Change from "reserved / upload pending" to "published"
- [ ] Add actual DOI

### Create Git Tag
- [ ] Navigate to repository root
- [ ] Create tag: `git tag -a p2-jcim-submission -m "P2 JCIM V2609C submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"`
- [ ] Push tag: `git push origin p2-jcim-submission`
- [ ] Verify tag visible on GitHub

### Commit Updates
- [ ] Stage manuscript updates
- [ ] Stage AGENTS.md update
- [ ] Commit: `git commit -m "Update P2 manuscript and documentation with Zenodo DOI"`
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

## Timeline

- [ ] **Phase 1-2**: Pre-upload preparation and DOI reservation (30 minutes)
- [ ] **Phase 3**: Metadata entry (20 minutes)
- [ ] **Phase 4**: File upload (10-30 minutes, depending on connection)
- [ ] **Phase 5**: Pre-publish verification (20 minutes)
- [ ] **Phase 6**: Publish (5 minutes)
- [ ] **Phase 7**: Post-publish verification (15 minutes)
- [ ] **Phase 8**: Manuscript update (15 minutes)
- [ ] **Phase 9**: Repository updates (10 minutes)
- [ ] **Phase 10**: Final documentation (10 minutes)

**Total estimated time**: 2-3 hours

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
