# P3 Zenodo Upload Checklist

**DOI:** https://doi.org/10.5281/zenodo.19608875  
**Date:** _______________  
**Uploaded by:** _______________

---

## ☐ PRE-UPLOAD (Before going to Zenodo)

### Package Verification
- [ ] Navigate to package: `cd zenodo_package_P3/`
- [ ] Verify checksums: `sha256sum -c sha256sums.txt` → All OK
- [ ] Check package size: `du -sh .` → Under 50 GB
- [ ] Verify all folders exist: `ls -d data/ results/ scripts/ documentation/`

### Create Upload Package
- [ ] Option A: Will upload individual files (recommended) ✓
- [ ] Option B: Create ZIP: `zip -r ../zenodo_p3_upload.zip .`

---

## ☐ ZENODO ACCESS

- [ ] Go to: https://zenodo.org/deposit/19608875
- [ ] Log in to Zenodo account
- [ ] Verify reserved DOI appears: `10.5281/zenodo.19608875`

---

## ☐ FILE UPLOAD

- [ ] Click "Start upload" or "Upload" button
- [ ] Drag and drop folder OR upload ZIP
- [ ] Wait for upload to complete (watch progress bars)
- [ ] Verify file count matches expected (~15-25 files)

---

## ☐ METADATA (Copy from ZENODO_SETUP_GUIDE.md)

### Required Fields
- [ ] **Upload type:** Dataset
- [ ] **Publication date:** 2026-09-15 (or current date)
- [ ] **Title:** "P3 Reproducibility Package — JCAMD Submission: Quantum-inspired molecular representations for African antimalarial candidates"
- [ ] **Creators:** All 5 authors with ORCIDs entered correctly:
  - [ ] Sao Temgoua, Myke Vital (ORCID: 0009-0004-5170-2309)
  - [ ] Tchapet Njafa, Jean-Pierre (ORCID: 0000-0002-1936-8353)
  - [ ] Samafou, Penabei
  - [ ] Fon Mbacham, Wilfred (ORCID: 0000-0002-3934-3233)
  - [ ] Nana Engo, Serge Guy (ORCID: 0000-0002-7484-3508)
- [ ] **Description:** Copy-pasted from ZENODO_SETUP_GUIDE.md
- [ ] **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- [ ] **Keywords:** antimalarial, quantum-inspired, topological data analysis, persistent homology, tensor networks, quantum kernels, molecular representations, machine learning, drug discovery, Plasmodium falciparum, natural products, African plant metabolites, JCAMD, reproducibility

### Optional Fields (Recommended)
- [ ] **Related identifiers:** 
  - [ ] "is related to" → https://doi.org/10.5281/zenodo.22686176 (P1)
  - [ ] "is supplement to" → (manuscript DOI - add after acceptance)
- [ ] **Funding:** (if applicable)

---

## ☐ PRE-PUBLISH VERIFICATION

- [ ] Metadata review:
  - [ ] All author names spelled correctly
  - [ ] All ORCIDs link to correct profiles
  - [ ] Title matches manuscript exactly
  - [ ] Description has no typos
- [ ] File list review:
  - [ ] README.md present
  - [ ] MANIFEST.json present
  - [ ] LICENSE.txt present
  - [ ] sha256sums.txt present
  - [ ] All data/ files present (3 files)
  - [ ] All results/ files present (~5 files)
  - [ ] All scripts/ files present (~6 files)
  - [ ] All documentation/ files present (1+ files)
- [ ] Download test (optional):
  - [ ] Download sha256sums.txt from preview
  - [ ] Download 1 data file and verify checksum

---

## ☐ PUBLISH

- [ ] Read the immutability warning (files cannot be edited after publish)
- [ ] Click green "Publish" button
- [ ] Confirm publication
- [ ] Wait for confirmation message

---

## ☐ POST-PUBLISH VERIFICATION (Within 5 minutes)

### DOI Resolution
- [ ] Test DOI: `curl -L https://doi.org/10.5281/zenodo.19608875`
- [ ] Should redirect to: https://zenodo.org/records/19608875

### Landing Page
- [ ] Go to: https://zenodo.org/records/19608875
- [ ] Title displays correctly
- [ ] All 5 authors listed
- [ ] Description renders properly
- [ ] README.md renders as formatted markdown (not raw text)
- [ ] License badge shows "CC BY 4.0"

### Download Test
- [ ] Download sha256sums.txt
- [ ] Download 3 random files
- [ ] Verify checksums: `sha256sum -c sha256sums.txt`
- [ ] All downloads OK

### Citation Export
- [ ] Click "Cite" button on landing page
- [ ] BibTeX export works
- [ ] All author names appear correctly

---

## ☐ MANUSCRIPT INTEGRATION

- [ ] Update manuscript Data Availability section with DOI
- [ ] Add `@misc{zenodo_p3,...}` to Bibliography_Paper3.bib
- [ ] Compile manuscript to verify citation works
- [ ] Verify DOI hyperlink is clickable in PDF

---

## ☐ DOCUMENTATION UPDATE

- [ ] Update AGENTS.md with Zenodo publication status
- [ ] Update P3_ZENODO_DEPOSIT_MANIFEST.json status to "published"
- [ ] Create git tag: `git tag -a p3-v2609-zenodo -m "P3 Zenodo published"`
- [ ] Push tag: `git push origin p3-v2609-zenodo`

---

## ☐ OPTIONAL POST-PUBLICATION

- [ ] Make GitHub repository public (after DOI verification)
- [ ] Announce on social media / mailing lists
- [ ] Add Zenodo badge to GitHub README
- [ ] Notify collaborators deposit is live

---

## FINAL VERIFICATION (24 hours later)

- [ ] DOI still resolves correctly
- [ ] Downloads still work
- [ ] No error reports from users
- [ ] Manuscript with DOI submitted to JCAMD

---

## SUCCESS CRITERIA ✅

Upload is **complete and successful** when ALL of these are checked:

- ✅ All files uploaded
- ✅ Checksums verified
- ✅ Metadata complete
- ✅ DOI resolves
- ✅ Downloads work
- ✅ README renders
- ✅ Citation exports
- ✅ Manuscript updated

---

## TROUBLESHOOTING

**If any step fails:**
1. Check ZENODO_SETUP_GUIDE.md "Troubleshooting" section
2. Contact Zenodo support: info@zenodo.org
3. Check AGENTS.md for project context

---

## NOTES

Use this space for any issues encountered or notes:

```
___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________
```

---

**Completion Date:** _______________  
**Verified By:** _______________  
**Status:** ☐ In Progress  |  ☐ Complete  |  ☐ Issues (see notes)

---

**End of Checklist**
