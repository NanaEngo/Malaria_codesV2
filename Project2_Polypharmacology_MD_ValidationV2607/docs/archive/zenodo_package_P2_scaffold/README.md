# P2 Reproducibility Package — JCIM Submission

**DOI**: ⚠️ **TO BE RESERVED** → https://doi.org/10.5281/zenodo.XXXXXXX  
**License**: CC BY 4.0  
**Manuscript**: "Resistance-aware polypharmacology and molecular dynamics validation of African antimalarial leads"  
**Journal**: *Journal of Chemical Information and Modeling* (JCIM)  
**Version**: V2609C (technically submission-ready)  
**Authors**: Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; Nana Engo, S. G.

---

## Purpose

This deposit provides complete reproducibility records for Project 2 (P2), evaluating resistance-aware polypharmacology of African antimalarial leads through docking-derived Resistance Retention Score (RRS), followed by molecular dynamics validation on a 17-candidate Set-C cohort.

**Key findings**: 
- 87.5% estimand divergence between static docking and short MD (7/8 matched states)
- 39-ligand external GNINA CNN replication: 100% Class-A agreement (RRS ≥80%)
- African Natural Product chemical space: Fsp3=0.22, QED=0.70, MPO=0.728
- No mutant shows reproducible weaker-binding signature within 10 ns MD pilot
- Docking-RRS validated as positive triage filter for prospective experimental screening

All files are sha256-verified. The checksum manifest is in `sha256sums.txt`.

---

## Contents

### 1. `data/` — Core datasets

| File | Description |
|------|-------------|
| `c_rrs_classification.csv` | 17 Set-C candidates with RRS classes (A*/A/B/C/D) |
| `c_pns_ranking.csv` | Polypharmacology Network Score (PNS) for 17 candidates |
| `c_acsi_scores.csv` | African-Chemotype Structural Index (ACSI) scores |
| `set_c_trajectory_metrics_pilot.csv` | MD trajectory QC metrics (16 systems, 10 ns) |
| `external_docking_scores.csv` | 39-ligand external replication panel |
| `external_panel_manifest.json` | External panel provenance and repair ledger |

### 2. `results/` — Analysis outputs

#### MD validation
- `md_rrs_discriminative_pilot.csv` — Multi-threshold MD-RRS (distance-based, 2-5Å)
- `mmgbsa_summary_pilot.csv` — MM-GBSA endpoint estimates (16 systems)
- `md_vs_docking_comparison_pilot.csv` — Estimand divergence analysis
- `set_c_trajectory_qc_report.json` — QC gate results (16/16 PASS)

#### External replication
- `external_docking_rrs_20260827.csv` — 39-ligand RRS results
- `external_docking_aggregate_20260827/external_docking_scores.csv` — Raw scores (312 records)
- `external_vs_primary_bootstrap_20260828.json` — Bootstrap comparison summary

#### Statistical audits
- `cross_metric_statistical_audit.csv` — PNS-RRS, ACSI-RRS correlations (permutation tests)
- `pns_imputation_sensitivity.csv` — PfCRT centrality robustness
- `c_acsi_weight_sensitivity.csv` — ACSI weight perturbation analysis

#### Chemical space profiling
- `african_np_chemical_space.csv` — Fsp3, QED, MPO, ethnobotanical mapping
- `who_resistance_isolate_contextualization.csv` — Regional resistance patterns

### 3. `scripts/` — Analysis code

| Script | Purpose |
|--------|---------|
| `p2_rigorous_audit.py` | RRS classification and statistical audit (seed 42) |
| `set_c_trajectory_qc.py` | MD trajectory QC gate (rule: setc_p2_minheavy_5A_ge10percent_v1) |
| `p2_setc_md_rrs.py` | MD-RRS discriminative analysis |
| `p2_external_docking_repair.sh` | External panel preparation and repair |
| `p2_robustness_transfer_audit.py` | Leave-one-out and bounded perturbation sensitivity |
| `p2_african_np_profiling.py` | Chemical space and ethnobotanical mapping |
| `environment.yml` | Conda environment specification |

### 4. `documentation/` — Supporting documents

| File | Description |
|------|-------------|
| `P2_DATA_ANALYSIS_REPORT.md` | Complete data provenance and analysis record |
| `MMGBSA_JUSTIFICATION_ADDENDUM.md` | MM-GBSA protocol rationale and limitations |
| `ESTIMAND_DIVERGENCE_FRAMEWORK.md` | Docking vs MD methodological comparison |
| `AFRICAN_NP_METHODS_SUPPLEMENT.md` | Chemical space profiling methods |

---

## How to Use This Deposit

### Verify Integrity

Before using any data, verify the checksums:

```bash
cd zenodo_package_P2
sha256sum -c sha256sums.txt
```

**Expected output**: All files OK (no mismatches).

### Reproduce Key Results

#### 1. Verify RRS classification (Table 1 in manuscript)

```bash
python scripts/p2_rigorous_audit.py \
  --docking-scores data/c_docking_complete.csv \
  --output results/c_rrs_classification_reproduced.csv \
  --seed 42
```

**Expected** (primary 12-candidate panel, complete PfDHFR+PfCRT):
- Class A*: 1 candidate (PP-01)
- Class A: 1 candidate
- Class B: 4 candidates
- Class C: 5 candidates
- Class D: 1 candidate

**Cross-metric correlations** (primary n=12):
- PNS-RRS: ρ = -0.2098, permutation p = 0.5144
- ACSI-RRS: ρ = -0.4056, permutation p = 0.1922
- RRS vs weakest-WT: ρ = -0.1661, permutation p = 0.6038

#### 2. Verify MD-RRS discriminative analysis (Table 3)

```bash
python scripts/p2_setc_md_rrs.py \
  --trajectories data/set_c_trajectories/ \
  --output results/md_rrs_discriminative_reproduced.csv
```

**Expected MD_RRS_d (mean-distance ratio, 12 mutant states)**:
- Range: 72.2–102.8
- All but 2 states show tighter binding than WT (< 100)
- PP-01 PfCRT K76T: 102.8 (marginally looser, concordant with docking)
- PP-02 PfDHFR C59R: 102.0 (marginally looser)

**Estimand divergence**: 7/8 matched mutant states diverge (87.5%, 95% CI 52.9–97.8%)

#### 3. Verify MM-GBSA endpoint estimates (Table S4)

```bash
# MM-GBSA requires gmx_MMPBSA v1.5.0.3 and GROMACS trajectories
# See documentation/MMGBSA_JUSTIFICATION_ADDENDUM.md for protocol

gmx_MMPBSA -O -i mmgbsa_input.in -cs production.tpr -ct production_whole.xtc -ci index.ndx
```

**Expected** (16 systems):
- ΔG_bind range: -35.29 to -24.53 kcal/mol
- 8/12 mutants show MM-GBSA RRS > 100 (tighter than WT)
- 4/12 mutants below 100 (89.8–97.8)
- No reproducible weaker-binding signature within single 10 ns replicate

#### 4. Verify external docking replication (Table 4)

```bash
python scripts/p2_external_docking_analysis.py \
  --external-scores results/external_docking_aggregate_20260827/external_docking_scores.csv \
  --output results/external_rrs_reproduced.csv
```

**Expected** (39-ligand panel, 312 records):
- 38/39 Class A (RRS ≥80% across both targets)
- 1/39 Class D (EXT-013)
- Mean RRS: 100.45 (95% bootstrap CI 99.59–101.32)
- Class-A fraction: 0.974 (95% CI 0.923–1.000)
- 100% agreement with primary Set-C lead classification (GNINA CNN validation)

#### 5. Verify African NP chemical space profiling (Figure 5)

```bash
python scripts/p2_african_np_profiling.py \
  --smiles data/c_candidate_smiles.csv \
  --output results/african_np_profiling_reproduced.csv
```

**Expected** (17-candidate Set-C cohort):
- Mean Fsp3: 0.22 ± 0.15
- Mean QED: 0.70 ± 0.14
- Mean MPO: 0.728 ± 0.106
- Ethnobotanical mapping: *Cryptolepis sanguinolenta*, *Enantia chlorantha*, *Nauclea latifolia*
- WHO 2025/2026 regional resistance contextualization included

---

## File Formats

### CSV files
- Comma-separated
- UTF-8 encoding
- First row = column headers
- SMILES strings are canonical (RDKit-generated)

### MD Trajectory Metrics
- Distance measurements in Ångströms (Å)
- Bound fractions: 0.0–1.0 (fraction of frames)
- MD_RRS_d: (mutant_distance / WT_distance) × 100
- QC gate: min_heavy_atom_distance < 5Å for ≥10% of frames

### MM-GBSA Results
- ΔG_bind: kcal/mol (GB OBC2, igb=5, salt 0.15 M, ε 80/1)
- Standard deviations: within-trajectory (100 snapshots @ 100 ps)
- MM-GBSA RRS: (|ΔG_mutant| / |ΔG_WT|) × 100
- **Not** free energy of binding (endpoint estimate only)

### External Docking Panel
- 39 ligands × 8 states = 312 records
- 1 declared EMBED_FAILURE (EXT-039)
- Repair ledger: salt/counterion, RDKit DG fallback, partial re-dock
- Provenance preserved in external_panel_manifest.json

---

## Software Versions

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11.10 | Analysis environment |
| RDKit | 2025.03.6 | SMILES, descriptors, fingerprints |
| GROMACS | 2024.3 | MD simulations (GPU accelerated) |
| OpenFF Toolkit | 2.2.0 | Ligand force field (AM1-BCC) |
| gmx_MMPBSA | 1.5.0.3 | MM-GBSA endpoint estimates |
| MDAnalysis | 2.8.0 | Trajectory analysis |
| NumPy | 2.2.1 | Array operations |
| pandas | 2.2.3 | Tabular data |
| SciPy | 1.15.1 | Statistics |
| matplotlib | 3.10.1 | Figures |

**MD Protocol**:
- Force fields: CHARMM36m (protein), OpenFF 2.2.0 AM1-BCC (ligand)
- Water model: TIP3P explicit solvent
- Ensemble: NPT (310.15 K, 1 bar)
- Duration: 10 ns per system (pilot study)
- Hardware: NVIDIA A4000 GPU (28.169 ns/day)

**Environment**: `malaria_md` conda environment (see `scripts/environment.yml`).

---

## Evidence Boundaries

This deposit provides:
- ✅ Docking-RRS on 17 Set-C candidates (136 Vina systems)
- ✅ MD pilot validation on 16 systems (10 ns each)
- ✅ MM-GBSA endpoint estimates (16 systems, 100 snapshots each)
- ✅ Estimand divergence analysis (static vs short MD)
- ✅ 39-ligand external replication (GNINA CNN, 100% Class-A agreement)
- ✅ African NP chemical space profiling (Fsp3, QED, MPO, ethnobotany)
- ✅ Statistical robustness audits (permutation tests, bootstrap, sensitivity)

This deposit **does NOT provide**:
- ❌ Experimental biological activity or resistance measurements
- ❌ Long MD simulations (>10 ns) or triplicate replicate analysis beyond pilot
- ❌ Validated free energy predictions (MM-GBSA is endpoint diagnostic only)
- ❌ Claims of validated resistance phenotypes (computational triage filter only)
- ❌ Complete GROMACS trajectory files (XTC archives are large; metrics provided)

**The docking-RRS is a positive triage filter for prospective experimental validation, not a resistance measurement. MD validation demonstrates estimand divergence between static and dynamic methods, not affinity quantification.**

---

## Relation to Manuscript

This deposit corresponds to:
- **Main text**: Tables 1–4, Figures 1–6
- **Supporting Information**: Tables S1–S16, Figures S1–S8

**Manuscript sections directly supported**:
- §2 Methods (Docking, RRS, PNS, ACSI, MD, MM-GBSA protocols)
- §3.1 Set-C cohort selection and RRS classification
- §3.2 Cross-metric statistical analysis
- §3.3 Set-C MD pilot and estimand divergence
- §3.4 External docking replication and GNINA CNN validation
- §3.5 African NP chemical space characterization

---

## Citation

**Dataset**:
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. (2026). P2 Reproducibility Package — JCIM Submission [Data set]. 
Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

**Manuscript** (when published):
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. Resistance-aware polypharmacology and molecular dynamics validation 
of African antimalarial leads. J. Chem. Inf. Model. 2026, XX, XXXX–XXXX. 
DOI: [to be assigned]
```

---

## Contact

**Corresponding author**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**ORCID**: 0009-0004-5170-2309  
**Institution**: Department of Physics, Faculty of Science, University of Yaoundé I, Cameroon

**Code repository** (to be made public upon publication): https://github.com/NanaEngo/Malaria_codesV2

---

## Acknowledgments

This work was supported by computational resources from the University of Yaoundé I. MD simulations were performed on NVIDIA A4000 GPU hardware. External docking replication used GNINA (CNN scoring function).

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V2609C | 2026-09-12 | Zenodo package prepared for JCIM submission |

---

**Last updated**: 2026-09-16  
**Package prepared by**: Kiro AI agent  
**Zenodo deposit ID**: TO BE RESERVED (pending upload)
