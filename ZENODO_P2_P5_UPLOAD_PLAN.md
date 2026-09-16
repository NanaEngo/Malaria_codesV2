# Zenodo Upload Plan — P2 and P5

**Created**: 2026-09-16  
**Purpose**: Prepare and upload reproducibility packages for P2 and P5 to Zenodo  
**Model**: Following P3 structure and workflow

---

## Overview

This document outlines the complete workflow for uploading P2 and P5 Zenodo packages, following the established P3 template.

### Project Status

| Project | Manuscript Status | DOI Status | Package Status |
|---------|------------------|------------|----------------|
| **P2** | V2609C technically submission-ready (JCIM) | ⚠️ **Needs reservation** | ✅ Directory structure exists |
| **P5** | Pre-submission development | ⚠️ **Needs reservation** | ✅ Directory structure exists |

---

## Step 1: Reserve Zenodo DOIs

Both P2 and P5 need DOI reservations.

### Instructions

1. Go to https://zenodo.org (log in)
2. Click **"New upload"**
3. For each project, fill basic information:

#### P2 DOI Reservation

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

**Upload type**: Dataset

4. Click **"Save"** (do NOT upload files yet)
5. Copy the reserved DOI (format: `10.5281/zenodo.XXXXXXX`)

#### P5 DOI Reservation

**Title**:
```
P5 Reproducibility Package — JCAMD Submission: Graph neural networks and transformers for antimalarial drug discovery
```

**Authors** (same as P2):
1. Sao Temgoua, Myke Vital → ORCID: 0009-0004-5170-2309
2. Tchapet Njafa, Jean-Pierre → ORCID: 0000-0002-1936-8353
3. Samafou, Penabei → (no ORCID)
4. Fon Mbacham, Wilfred → ORCID: 0000-0002-3934-3233
5. Nana Engo, Serge Guy → ORCID: 0000-0002-7484-3508

**Upload type**: Dataset

### After Reservation

Update the following files for each project with the reserved DOIs:
- `MANIFEST.json` → `"doi_reserved": "https://doi.org/..."`
- `README.md` → Top section
- `UPLOAD_INSTRUCTIONS.md` → Step 1

---

## Step 2: Verify Package Contents

Check that all necessary files are present in each package directory.

### P2 Package Verification

```bash
cd Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2

# Check structure
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt

# Check subdirectories
ls -d data/ results/ scripts/ documentation/

# Verify checksums (after they're generated)
sha256sum -c sha256sums.txt
```

### P5 Package Verification

```bash
cd Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5

# Check structure
ls -1 README.md MANIFEST.json LICENSE.txt sha256sums.txt

# Check subdirectories
ls -d data/ results/ scripts/ documentation/

# Verify checksums (after they're generated)
sha256sum -c sha256sums.txt
```

---

## Step 3: Upload to Zenodo

For each project, follow the project-specific `UPLOAD_INSTRUCTIONS.md` file.

### Quick Upload Steps (Both Projects)

1. **Access deposit**: Go to reserved DOI URL (e.g., `https://zenodo.org/deposit/XXXXXXX`)

2. **Fill metadata**:
   - Title (see above)
   - Authors with ORCIDs
   - Description (see project-specific instructions)
   - Keywords
   - License: CC BY 4.0
   - Upload type: Dataset

3. **Upload files**:
   - **Option A** (recommended): Drag entire `zenodo_package_PX/` folder
   - **Option B**: Create ZIP and upload

4. **Pre-publish verification**:
   - Download `sha256sums.txt` and spot-check
   - Download 2-3 random files and verify checksums
   - Review all metadata

5. **Publish**:
   - Click "Publish" button
   - ⚠️ **IMPORTANT**: Once published, deposit is immutable
   - DOI becomes active immediately

---

## Step 4: Post-Upload Actions

After both deposits are published:

### 4.1 Update Manuscripts

#### P2 Manuscript (V2609C)

Add to Data Availability section:
```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

Update file: `Project2_Polypharmacology_MD_ValidationV2607/manuscript/V2609C/Polypharmacology_MD_Validation_V2609C.tex`

#### P5 Manuscript

Add to Data Availability section (when manuscript is finalized):
```latex
\section*{Data Availability}
All data and analysis scripts supporting this study are available at Zenodo: 
\url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

### 4.2 Create Git Tags

```bash
cd /home/vital/Documents/GitHub/Malaria_codesV2

# P2
git tag -a p2-jcim-submission -m "P2 JCIM V2609C submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"
git push origin p2-jcim-submission

# P5
git tag -a p5-jcamd-submission -m "P5 JCAMD submission with Zenodo DOI 10.5281/zenodo.XXXXXXX"
git push origin p5-jcamd-submission
```

### 4.3 Update AGENTS.md

Update the Zenodo status line in AGENTS.md to reflect published DOIs.

### 4.4 Verify DOIs Resolve

Test that both DOIs resolve correctly:
- P2: https://doi.org/10.5281/zenodo.XXXXXXX
- P5: https://doi.org/10.5281/zenodo.XXXXXXX

Wait 10-15 minutes if they don't resolve immediately.

---

## Package Locations

| Project | Package Path | Size Estimate |
|---------|-------------|---------------|
| P2 | `Project2_Polypharmacology_MD_ValidationV2607/zenodo_package_P2/` | ~500 MB |
| P5 | `Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5/` | ~2 GB |

---

## Key Files to Create/Update

### For P2

- [ ] `zenodo_package_P2/UPLOAD_INSTRUCTIONS.md` — Detailed upload guide
- [ ] `zenodo_package_P2/UPLOAD_CHECKLIST.md` — Step-by-step checklist
- [ ] `zenodo_package_P2/MANIFEST.json` — Update with reserved DOI
- [ ] `zenodo_package_P2/README.md` — Update with reserved DOI
- [ ] `zenodo_package_P2/sha256sums.txt` — Generate checksums

### For P5

- [ ] `zenodo_package_P5/UPLOAD_INSTRUCTIONS.md` — Detailed upload guide
- [ ] `zenodo_package_P5/UPLOAD_CHECKLIST.md` — Step-by-step checklist
- [ ] `zenodo_package_P5/MANIFEST.json` — Update with reserved DOI
- [ ] `zenodo_package_P5/README.md` — Update with reserved DOI
- [ ] `zenodo_package_P5/sha256sums.txt` — Generate checksums

---

## Timeline

1. **Now**: Reserve DOIs for P2 and P5
2. **After DOI reservation**: Update all package metadata files
3. **Verify packages**: Check all files present and checksums valid
4. **Upload P2**: Complete upload and verification
5. **Upload P5**: Complete upload and verification
6. **Post-upload**: Update manuscripts, create tags, verify DOIs

---

## Related Documentation

- **P3 Example**: See `Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3/`
- **General Guide**: See `ZENODO_QUICK_START.md`
- **Build Scripts**: See `scripts/build_zenodo_packages_batch.sh`

---

## Troubleshooting

### Large file sizes (especially P5)
- P5 may be several GB
- Consider ZIP upload to Zenodo
- Or upload subdirectories separately
- Zenodo limit is 50 GB per deposit

### Checksums don't match after download
- Zenodo may re-compress files
- Download raw files (not ZIP preview)
- Contact Zenodo support if persistent

### DOI doesn't resolve
- Wait 10-15 minutes for propagation
- Check deposit page directly
- Contact Zenodo support after 30 minutes: info@zenodo.org

---

## Final Checklist

**Before upload**:
- [ ] Both DOIs reserved
- [ ] All metadata files updated with DOIs
- [ ] All checksums generated and verified locally
- [ ] Package structures complete

**Upload**:
- [ ] P2 uploaded and published
- [ ] P5 uploaded and published
- [ ] Both DOIs resolve

**Post-upload**:
- [ ] P2 manuscript updated with DOI
- [ ] P5 manuscript updated with DOI (when ready)
- [ ] Git tags created and pushed
- [ ] AGENTS.md updated
- [ ] Downloaded and verified 2-3 files per deposit

---

**Contact**:
- Zenodo support: info@zenodo.org
- Corresponding author: myke-vital.sao@facsciences-uy1.cm

**Last updated**: 2026-09-16  
**Prepared by**: Kiro AI agent
