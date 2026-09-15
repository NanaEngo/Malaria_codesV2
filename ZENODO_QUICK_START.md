# Zenodo Packages — Quick Start Guide

**Goal**: Create reproducibility deposits for P3, P4, P5 following the P1 template  
**Date**: 2026-09-11

---

## 1. Build All Packages (One Command)

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2
bash scripts/build_zenodo_packages_batch.sh
```

**This will**:
- Create directory structures for P3, P4, P5
- Copy data, results, scripts, documentation
- Generate SHA256 checksums
- Report file counts and sizes

**Expected output**:
```
=== Building Zenodo Packages for P3, P4, P5 ===
[1/3] Building P3 package...
  Copying P3 data files...
  Copying P3 results...
  ✓ P3 package structure created

[2/3] Building P4 package...
  ...
  ✓ P4 package structure created

[3/3] Building P5 package...
  ...
  ✓ P5 package structure created

=== Generating SHA256 checksums ===
  P3: Files: X, Size: Y MB
  P4: Files: X, Size: Y MB
  P5: Files: X, Size: Y MB
```

---

## 2. Verify Packages

Check each package:

```bash
# P3
cd Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3
sha256sum -c sha256sums.txt
ls -lh  # Check total size

# P4
cd ../../Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4
sha256sum -c sha256sums.txt
ls -lh

# P5
cd ../../Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5
sha256sum -c sha256sums.txt
ls -lh
```

---

## 3. Reserve DOIs (If Needed)

**P3**: Already reserved https://doi.org/10.5281/zenodo.19608875 ✅  
**P4**: **Need to reserve** ⚠️  
**P5**: **Need to reserve** ⚠️

### To reserve a DOI:
1. Go to https://zenodo.org (log in)
2. Click **"New upload"**
3. Fill title: "P4 Reproducibility Package — JCAMD Submission"
4. Add authors (see MANIFEST.json for order and ORCIDs)
5. Click **"Save"** (do NOT upload files yet)
6. DOI will be reserved (format: `10.5281/zenodo.XXXXXXX`)
7. Copy DOI and update:
   - `MANIFEST.json` → `"doi_reserved": "https://doi.org/..."`
   - `README.md` → Top section
   - `UPLOAD_INSTRUCTIONS.md` → Step 1

---

## 4. Upload to Zenodo

For each project, follow `UPLOAD_INSTRUCTIONS.md`:

### Quick steps:
1. Go to deposit URL (e.g., https://zenodo.org/deposit/19608875 for P3)
2. Fill metadata:
   - Title, authors (with ORCIDs), description, keywords
   - License: CC BY 4.0
   - Upload type: Dataset
3. Upload files:
   - **Option A**: Drag entire `zenodo_package_PX/` folder
   - **Option B**: Create ZIP and upload
4. Verify checksums (download and spot-check)
5. **Publish** (irreversible!)

---

## 5. Post-Upload Actions

After each Zenodo DOI is active:

### Update manuscript
```latex
\section*{Data Availability}
All data and analysis scripts are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXX}.
```

### Create Git tags
```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2

# P3
git tag -a p3-jcamd-submission -m "P3 JCAMD submission with Zenodo DOI"
git push origin p3-jcamd-submission

# P4
git tag -a p4-jcamd-submission -m "P4 JCAMD submission with Zenodo DOI"
git push origin p4-jcamd-submission

# P5
git tag -a p5-jcamd-submission -m "P5 JCAMD submission with Zenodo DOI"
git push origin p5-jcamd-submission
```

### Make repository public (after all DOIs verified)
1. Go to https://github.com/NanaEngo/Malaria_codesV2/settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility" → "Make public"

---

## Package Locations

| Project | Package Path | README | MANIFEST |
|---------|-------------|--------|----------|
| P3 | `Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/` | ✅ | ✅ |
| P4 | `Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4/` | ✅ | ✅ |
| P5 | `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/` | ✅ | ✅ |

---

## Key Files in Each Package

```
zenodo_package_PX/
├── README.md                # Complete usage guide (detailed)
├── MANIFEST.json            # Structured metadata
├── UPLOAD_INSTRUCTIONS.md   # Step-by-step Zenodo upload
├── LICENSE.txt              # CC BY 4.0
├── sha256sums.txt          # Generated checksums
├── data/                    # Core datasets
├── results/                 # Benchmark outputs
├── scripts/                 # Reproduction scripts
└── documentation/           # DAR and supplements
```

---

## Troubleshooting

### "File not found" during build
- Some files may not exist yet
- Build script continues with warnings
- Check warnings and manually copy missing files

### Large file sizes (especially P5)
- P5 extended campaign may be several GB
- Consider ZIP upload to Zenodo
- Or upload subdirectories separately

### Checksums don't match after download
- Zenodo may re-compress files
- Download raw files (not ZIP preview)
- Contact Zenodo support if persistent

### DOI doesn't resolve
- Wait 10-15 minutes for propagation
- Check deposit page directly
- Contact Zenodo support after 30 minutes

---

## Checklist

**Before upload**:
- [ ] Build script completed without errors
- [ ] All checksums verify locally
- [ ] DOIs reserved (P4 and P5)
- [ ] Metadata reviewed in MANIFEST.json

**Upload**:
- [ ] P3 uploaded and published
- [ ] P4 uploaded and published
- [ ] P5 uploaded and published
- [ ] All DOIs resolve

**Post-upload**:
- [ ] Manuscripts updated with DOIs
- [ ] Git tags created and pushed
- [ ] Repository made public
- [ ] Downloaded and verified 2-3 files per deposit

---

## Support

- **Package questions**: See `ZENODO_PACKAGES_SUMMARY.md`
- **Zenodo technical issues**: info@zenodo.org
- **Manuscript questions**: myke-vital.sao@facsciences-uy1.cm

---

**Created**: 2026-09-11  
**Model**: Following P1 V8 Zenodo structure
