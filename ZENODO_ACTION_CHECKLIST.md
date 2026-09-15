# Zenodo Upload Action Checklist

**Date**: 2026-09-11  
**Status**: ✅ Build complete, ready for upload  
**Priority**: Complete P4 and P5 DOI reservations first

---

## ✅ Completed

- [x] Build P3 package (13 files, 97 MB)
- [x] Build P4 package (117 files, 756 KB)
- [x] Build P5 package (36 files, 8.6 MB)
- [x] Verify all checksums
- [x] Create documentation suite
- [x] Extract scripts from master branch
- [x] Copy data/results from data-results branch

---

## 📋 To Do Before Upload

### P3 — Ready to Upload ✅
- [x] DOI reserved: 10.5281/zenodo.19608875
- [x] README.md complete
- [x] MANIFEST.json complete
- [x] UPLOAD_INSTRUCTIONS.md complete
- [x] All files present
- [x] Checksums verified
- **Action**: Can upload immediately

### P4 — Needs DOI ⚠️
- [ ] **Reserve DOI on Zenodo** (do this first!)
- [x] README.md complete
- [x] MANIFEST.json complete
- [ ] Update MANIFEST.json with DOI
- [ ] Update README.md with DOI
- [ ] Create UPLOAD_INSTRUCTIONS.md (copy from P3, update DOI)
- [x] All files present
- [x] Checksums verified
- **Action**: Reserve DOI, then update docs

### P5 — Needs DOI + Docs ⚠️
- [ ] **Reserve DOI on Zenodo** (do this first!)
- [x] README.md complete
- [ ] Create MANIFEST.json (follow P3/P4 template)
- [ ] Create UPLOAD_INSTRUCTIONS.md (copy from P3, update DOI)
- [ ] Update README.md with DOI
- [x] Most files present
- [x] Checksums verified
- **Action**: Reserve DOI, create MANIFEST + UPLOAD_INSTRUCTIONS

---

## 🔄 Workflow: Reserve DOI on Zenodo

For P4 and P5:

1. Go to https://zenodo.org (log in)
2. Click "New upload"
3. Fill basic info:
   - **P4 Title**: "P4 Reproducibility Package — JCAMD Submission: Pareto-guided Monte Carlo tree search for multi-objective de novo antimalarial drug design"
   - **P5 Title**: "P5 Reproducibility Package — GNN/Transformer antimalarial activity prediction under chemical distribution shift"
4. Add authors (see below)
5. Click "Save" (do NOT upload files yet)
6. Copy the reserved DOI (format: `10.5281/zenodo.XXXXXXX`)
7. Update files with DOI

### Authors (same for all)
1. Sao Temgoua, Myke Vital → ORCID: 0009-0004-5170-2309
2. Tchapet Njafa, Jean-Pierre → ORCID: 0000-0002-1936-8353
3. Samafou, Penabei → (no ORCID)
4. Fon Mbacham, Wilfred → ORCID: 0000-0002-3934-3233
5. Nana Engo, Serge Guy → ORCID: 0000-0002-7484-3508

---

## 📝 P4 Post-DOI Actions

After reserving P4 DOI (example: `10.5281/zenodo.2468123`):

```bash
# 1. Update MANIFEST.json
cd Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4
# Edit MANIFEST.json: "doi_reserved": "https://doi.org/10.5281/zenodo.2468123"

# 2. Update README.md
# Edit README.md: Line 3, update DOI

# 3. Create UPLOAD_INSTRUCTIONS.md
# Copy from P3, update DOI and URLs

# 4. Regenerate checksums
cd ../../
bash scripts/build_zenodo_complete.sh  # Or manually:
cd Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4
find . -type f ! -name "sha256sums.txt" -exec sha256sum {} \; | sort > sha256sums.txt
```

---

## 📝 P5 Post-DOI Actions

After reserving P5 DOI (example: `10.5281/zenodo.2468124`):

```bash
# 1. Create MANIFEST.json (use P3/P4 as template)
cd Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5
# Create MANIFEST.json with P5-specific content + reserved DOI

# 2. Update README.md
# Edit README.md: Line 3, update DOI

# 3. Create UPLOAD_INSTRUCTIONS.md
# Copy from P3, update DOI and URLs

# 4. Regenerate checksums
cd ../../
bash scripts/build_zenodo_complete.sh  # Or manually:
cd Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5
find . -type f ! -name "sha256sums.txt" -exec sha256sum {} \; | sort > sha256sums.txt
```

---

## 📤 Upload Workflow (Each Package)

### P3 (Ready Now)
```
1. Go to: https://zenodo.org/deposit/19608875
2. Fill metadata (see UPLOAD_INSTRUCTIONS.md)
3. Upload files (drag-and-drop entire package folder)
4. Verify checksums (download and spot-check)
5. Publish
```

### P4 (After DOI Reserved)
```
1. Go to: https://zenodo.org/deposit/XXXXXXX
2. Fill metadata (see UPLOAD_INSTRUCTIONS.md)
3. Upload files
4. Verify checksums
5. Publish
```

### P5 (After DOI Reserved)
```
1. Go to: https://zenodo.org/deposit/XXXXXXX
2. Fill metadata (see UPLOAD_INSTRUCTIONS.md)
3. Upload files
4. Verify checksums
5. Publish
```

---

## 📄 Post-Upload: Update Manuscripts

After each DOI is active and verified:

### P3 Manuscript
```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.19608875}.
```

### P4 Manuscript
```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

### P5 Manuscript
```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

---

## 🏷️ Git Tags (After All Uploads Complete)

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2

# P3
git tag -a p3-jcamd-submission -m "P3 JCAMD submission with Zenodo DOI 10.5281/zenodo.19608875"

# P4 (replace XXXXXXX with actual DOI)
git tag -a p4-jcamd-submission -m "P4 JCAMD submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"

# P5 (replace XXXXXXX with actual DOI)
git tag -a p5-jcamd-submission -m "P5 JCAMD submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"

# Push tags
git push origin p3-jcamd-submission p4-jcamd-submission p5-jcamd-submission
```

---

## 🌐 Make Repository Public (Final Step)

**ONLY after all three DOIs are verified and working:**

```bash
# Go to: https://github.com/NanaEngo/Malaria_codesV2/settings
# Scroll to "Danger Zone"
# Click "Change repository visibility"
# Select "Make public"
# Type repository name to confirm
# Click "I understand, make this repository public"
```

---

## ✅ Final Verification Checklist

Before making repository public, verify:

- [ ] P3 DOI resolves: https://doi.org/10.5281/zenodo.19608875
- [ ] P4 DOI resolves: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] P5 DOI resolves: https://doi.org/10.5281/zenodo.XXXXXXX
- [ ] Downloaded 2-3 files from each deposit and verified checksums
- [ ] README.md renders correctly on Zenodo for each
- [ ] All manuscripts updated with correct DOIs
- [ ] Git tags created and pushed
- [ ] Checked with co-authors before making repository public

---

## 📞 Support Contacts

**Package questions**: myke-vital.sao@facsciences-uy1.cm  
**Zenodo technical**: info@zenodo.org  
**Documentation**: See `ZENODO_BUILD_REPORT.md`, `ZENODO_QUICK_START.md`

---

## ⏱️ Estimated Timeline

- **DOI reservations**: 5 minutes each (P4, P5)
- **Doc updates (P4, P5)**: 15 minutes each
- **Upload P3**: 10 minutes (already complete docs)
- **Upload P4**: 15 minutes (after DOI + docs)
- **Upload P5**: 15 minutes (after DOI + docs)
- **Manuscript updates**: 5 minutes each
- **Git tags**: 2 minutes
- **Make public**: 2 minutes

**Total estimated time**: ~1.5 hours

---

**Created**: 2026-09-11  
**Last updated**: 2026-09-11  
**Status**: Ready for author action  
**Priority**: Reserve DOIs for P4 and P5 first
