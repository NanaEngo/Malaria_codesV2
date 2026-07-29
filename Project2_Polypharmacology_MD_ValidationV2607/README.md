# Resistance-Resilient Polypharmacological Antimalarials: MD+MC Validation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **Project 2 — Molecular Dynamics and Monte Carlo validation of polypharmacological antimalarial candidates against resistance mutations (Project V2607).**

**Target Journal:** *Journal of Chemical Information and Modeling* (IF 5.6)  
**Status:** ✅ Submission-ready (JCIM) — 14 RRS compounds (classes A*–D), PP-11 C59R mechanism resolved, MM-GBSA reconciliation complete  
**Manuscript:** `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` — canonical V2607 version---

## 📄 Manuscript Files

### Canonical V2607 files

| File | Path | Description |
|------|------|-------------|
| Main manuscript | [`manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex`](manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex) | Canonical V2607 main manuscript |
| Supplementary Material | [`manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex`](manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex) | Canonical V2607 supplementary material |
| Cover Letter | [`manuscript/LaTeX/Cover_Letter.tex`](manuscript/LaTeX/Cover_Letter.tex) | Submission cover letter |
| Bibliography | [`manuscript/LaTeX/Bibliography_Polypharmacology_MD_Validation.bib`](manuscript/LaTeX/Bibliography_Polypharmacology_MD_Validation.bib) | Main bibliography |

### Deprecated / historical / stale files

> **⚠️ These files are retained for historical reference only. Do not edit or submit them.**

| File | Archive Location | Description |
|------|------------------|-------------|
| `Paper2_Draft_v0.6.tex` | `Malaria_codesV2/.archive_P2_V2607_20260720/manuscript/LaTeX/` | Old draft main manuscript |
| `Supplementary_Material.tex` | `Malaria_codesV2/.archive_P2_V2607_20260720/manuscript/LaTeX/` | Old placeholder supplementary material |
| `Bibliography_Paper2.bib` | `manuscript/LaTeX/` (still in source tree) | Stale/legacy bibliography; superseded by `Bibliography_Polypharmacology_MD_Validation.bib` |

---

> **Data-analysis audit (2026-07-29):** Active P2 results are consolidated under `Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/`. The canonical RRS/ACSI/PNS metrics, mutant docking, and MM-GBSA reconciled data are committed in the repository. See `BMAD_Q1_DATA_ANALYSIS_REPORT.md` §2 for the full audit.
## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [System Matrix](#-system-matrix)
- [Directory Structure](#-directory-structure)
- [Scripts Organization](#-scripts-organization)
- [Pipeline Workflow](#-pipeline-workflow)
- [Novel Metrics](#-novel-metrics)
- [Resistance Mutations](#-resistance-mutations)
- [Progress Tracking](#-progress-tracking)
- [Citation](#-citation)

---

## 🎯 Project Overview

This project validates the **top 20 polypharmacological antimalarial candidates** from [Project 1](../Papers/Chem_space_antimalarial_JCIM/) using rigorous MD simulations and MC sampling across wild-type and resistance-mutant *Plasmodium falciparum* targets (PfDHFR, PfCRT, PfATP4, PfClpP).

The key innovation is a **resistance-aware validation framework** that quantifies how well each candidate maintains binding against clinically prevalent resistance mutations in African populations.

### Key Objectives

1. **Homology Modeling** — Generate 6 mutant structures (N51I, C59R, S108N, I164L, K76T, K76A)
2. **MD Validation** — 30,000 ns of production MD across 220 protein–ligand systems
3. **Resistance Profiling** — Quantify binding resilience via novel metrics (RRS, ACSI, PNS)
4. **MC Sampling** — 2.2M Monte Carlo steps for binding free energy landscapes

---

## 📊 System Matrix

| Category | Ligands | Targets | Systems | MD (ns/system) | MC Steps | Total MD (ns) |
|----------|---------|---------|---------|---------------|----------|--------------|
| **WT Baseline** | 20 | 4 WT | 80 | 200 | 10,000 | 16,000 |
| **Mutant Panel** | 20 | 6 mutants | 120 | 100 | 10,000 | 12,000 |
| **Controls** | 5 drugs | 4 targets | 20 | 100 | 10,000 | 2,000 |
| **Total** | — | — | **220** | — | **2,200,000** | **30,000** |

**Targets:**
- **PfDHFR-TS (7F3Y)** — WT + N51I, C59R, S108N, I164L (4 mutants)
- **PfCRT (6UKJ)** — WT + K76T, K76A (2 mutants)
- **PfATP4 (9N10)** — WT only
- **PfClpP (4GM2)** — WT only

**Control Drugs:** Pyrimethamine, Chloroquine, Cipargamin, ADEP, Artemisinin

---

## 📁 Directory Structure

```
Project2_Polypharmacology_MD_ValidationV2607/
├── README.md                              ← This file
├── skills_project2.md                     ← Codebuff skills
│
├── scripts/                               ← ALL project scripts (48 .py, 15 .sh, 1 .pl)
│   ├── md_*.py                            → Pipeline scripts (homology, RRS/ACSI/PNS, analysis)
│   ├── p1_*.py                            → Project 1 analysis (enrichment, ADMET, MPO, etc.)
│   ├── generate_figure_*.py               → Figure generation scripts
│   ├── Snakefile                          → Pipeline orchestrator
│   ├── config.yaml                        → Pipeline configuration
│   ├── md_full_pipeline.sh                → Master shell pipeline
│   ├── md_run_{minimisation,nvt,npt,production}.sh → GROMACS run scripts
│   │
│   ├── preparation/                       → From Tuto_MD_MC (38 files)
│   │   ├── prepare_{6UKJ,7F3Y}.py           Protein preparation (PDBFixer)
│   │   ├── step{1,2,3}_*.py                 System assembly pipeline
│   │   ├── convert_{smiles, pdb}_to_*.py    Format conversion utilities
│   │   ├── fix_pdb_missing_atoms.py         Structure repair
│   │   ├── analyze_test_system.py           Test system analysis
│   │   ├── *.sh                             Pipeline shell scripts
│   │   └── ...                              (26 more utility scripts)
│   │
│   ├── docking/                           → From data/from_project1/docking/
│   │   └── consensus_scoring_vina.sh         Vina consensus scoring
│   │
│   └── utils/                             → Utility scripts
│       ├── sort_mol2_bonds.pl
│       └── test_pymol.py
│
├── Tuto_MD_MC/                            → MD tutorial and reference files
│   ├── MD_SETUP_REFINED.md                → Refined MD protocol (tutorial)
│   ├── Test/                              → Test simulation system
│   ├── Gromacs_inputs/                    → Per-system GROMACS input templates
│   │   ├── LIG{1,2,5,7,8,9,10,14,15,16,17}/  → Individual ligand systems
│   │   └── md_top20_candidates.csv        → Top 20 candidate list
│   ├── charmm-gui/                        → CHARMM-GUI reference systems
│   ├── protein_prep/                      → Protein preparation intermediates
│   ├── ligand_prep*/                      → Ligand parameterization outputs
│   ├── mdp_templates/                     → GROMACS MDP template files
│   └── complex_assembly/                  → Complex assembly helpers
│
├── manuscript/
│   ├── LaTeX/                             → LaTeX source
│   │   ├── Polypharmacology_MD_Validation_V2607.tex  → Main manuscript
│   │   ├── Polypharmacology_MD_Validation_SM_V2607.tex → Supplementary document
│   │   ├── Table_S0_Docking_Validation.tex
│   │   ├── Table_S5_ADMET_CrossValidation.tex
│   │   ├── Table_S6_ACSI_Weight_Sensitivity.tex
│   │   └── Bibliography_Paper2.bib
│   ├── Graphics/                          → Publication figures
│   │   └── Figure_S1_MPO_sensitivity.pdf/png  → Generated via generate_figure_s1.py
│   ├── Methods/                           → Protocol documentation
│   │   ├── MD_Protocol.md
│   │   └── MM-GBSA_Methodology.md
│   └── PEER_REVIEW_v0.6.md               → Peer review simulation notes
│
├── data/
│   ├── from_project1/                     → Project 1 outputs used as inputs
│   │   ├── docking/                       → WT consensus docking results (CSV + logs)
│   │   ├── clustering/                    → VAE clustering outputs
│   │   ├── data/                          → Candidate data files
│   │   └── results/                       → Analysis results (scaffold, ADMET, etc.)
│   ├── proteins/
│   │   ├── wild_type/                     → WT PDB structures
│   │   └── mutants/                       → Mutant structure scripts (PyMOL)
│   └── external/
│       ├── dekois/                        → DEKOIS 2.0 decoy sets (for Table S0)
│       └── ligands/                       → Ligand structure files
│
├── docs/
│   └── SITUATION_REPORT.md               → Project status + adversarial audit
│
├── results/
│   ├── candidate_selection/               → Top 20 selection outputs
│   ├── mutant_structures/                 → Generated mutant PDBs (future)
│   ├── md_systems/                        → Prepared MD systems (future)
│   ├── metrics/                           → RRS/ACSI/PNS results (future)
│   ├── analysis/                          → Trajectory analysis (future)
│   ├── figures/                           → Generated figures
│   └── tables/                            → Generated tables
│
├── environments/
│   └── environment_md.yml                 → Conda environment for MD pipeline
│
└── PROJECT_COMPLETION_SUMMARY.md         → Phase completion tracking
```

---

## 📜 Scripts Organization

All scripts are consolidated under `scripts/`, organized by function:

### Pipeline Scripts (root of `scripts/`)
| Script | Purpose | Lines |
|--------|---------|-------|
| `md_homology_mutants.py` | Generate 6 mutant structures via PyMOL | 454 |
| `md_prepare_proteins.py` | Prepare WT proteins for MD (PDBFixer pipeline) | 132 |
| `md_prepare_ligands.py` | Ligand parameterization (CGenFF/OpenFF) | 284 |
| `md_build_complexes.py` | Assemble protein–ligand complexes | 442 |
| `md_calculate_rrs_acsi_pns.py` | Core scoring: RRS, ACSI, PNS metrics | 361 |
| `md_analyse_trajectories.py` | Post-MD trajectory analysis | 511 |
| `md_select_top20.py` | Filter candidates by MPO ≥ 0.70, SYBA > 0, SI > 10 | 83 |
| `generate_figure_s1.py` | MPO sensitivity heatmap (Figure S1) | — |
| `generate_all_figures.py` | Generate all main manuscript figures | — |

### Analysis Scripts (root of `scripts/`)
| Script | Purpose | Source |
|--------|---------|--------|
| `p1_enrichment_validation.py` | Data-driven enrichment (773 lines) | Updated from Project 1 |
| `p1_admet_crossval.py` | ADMETlab 3.0 cross-validation (325 lines) | Updated from Project 1 |
| `p1_mpo_sensitivity.py` | MPO weight sensitivity (225 lines) | Updated from Project 1 |
| `p1_threshold_calibration.py` | Score thresholds (275 lines) | Updated from Project 1 |
| `p1_latent_space_viz.py` | VAE latent space (236 lines) | Updated from Project 1 |
| `p1_prior_comparison.py` | Benchmark vs prior methods (206 lines) | Updated from Project 1 |
| `p1_scaffold_tanimoto.py` | Scaffold Tanimoto novelty (195 lines) | Updated from Project 1 |

### Preparation Scripts (`scripts/preparation/`)
Contains 38 scripts moved from `Tuto_MD_MC/`:
- **Protein preparation:** `prepare_6UKJ.py`, `prepare_7F3Y.py`, `step2_protein_prep.py`
- **Ligand preparation:** `step1_ligand_prep.py`, `step1b_openff_parameterization.py`, `smile_to_mol2.py`
- **Complex assembly:** `step3_complex_assembly.py`, `merge_ligand_protein_coordinates.py`
- **Format conversion:** `convert_smiles_to_pdb.py`, `convert_pdb_to_mol2.py`
- **Validation:** `validate_initial_structures.py`, `validate_ligand_pdbs.py`, `validate_mol2_files.py`
- **Pipeline:** `fix_topologies.sh`, `prepare_targets.sh`, `verify_all_systems.sh`
- **Analysis:** `analyze_test_system.py`, `comprehensive_md_analysis.py`
- **PDBFixer tests:** `test_pdbfixer.py`, `test_preparation.py`, `test_step2_protein_prep.py`
- **Documentation:** `MD_SETUP_REFINED.md`, `TROUBLESHOOTING.md`, `QUICK_START_MD.md`

### Docking Scripts (`scripts/docking/`)
| Script | Purpose |
|--------|---------|
| `consensus_scoring_vina.sh` | Vina consensus scoring across targets |

### Utility Scripts (`scripts/utils/`)
| Script | Purpose |
|--------|---------|
| `sort_mol2_bonds.pl` | Bond sorting for mol2 files |
| `test_pymol.py` | PyMOL connectivity test |

---

## 🔬 Pipeline Workflow

### Complete Pipeline (via Snakemake)
```bash
cd Project2_Polypharmacology_MD_ValidationV2607
snakemake -s scripts/Snakefile --configfile scripts/config.yaml --cores 4
```

### Step-by-Step

```bash
# 1. Generate mutant structures
python scripts/md_homology_mutants.py

# 2. Prepare proteins and ligands
python scripts/md_prepare_proteins.py
python scripts/md_prepare_ligands.py

# 3. Build protein–ligand complexes
python scripts/md_build_complexes.py

# 4. Run MD simulations (via bash pipeline)
bash scripts/md_full_pipeline.sh

# 5. Calculate RRS, ACSI, PNS metrics
python scripts/md_calculate_rrs_acsi_pns.py

# 6. Analyze trajectories
python scripts/md_analyse_trajectories.py

# 7. Generate figures
python scripts/generate_figure_s1.py
python scripts/generate_all_figures.py
```

### Individual MD Steps
```bash
# Energy minimization
bash scripts/md_run_minimisation.sh

# NVT equilibration (1 ns)
bash scripts/md_run_nvt.sh

# NPT equilibration (1 ns)
bash scripts/md_run_npt.sh

# Production MD (10+ ns)
bash scripts/md_run_production.sh
```

---

## 📐 Novel Metrics

| Metric | Description | Range | Interpretation |
|--------|-------------|-------|----------------|
| **RRS** | Resistance Resilience Score | 0–100% | % of WT binding affinity retained across mutants |
| **ACSI** | African Chemical Space Index | 0–1 | Scaffold novelty + DrugBank distance + natural product likeness |
| **PNS** | Polypharmacology Network Score | 0–1 | STRING-weighted multi-target engagement |

### RRS Classification (5-class system — F3 remediation)
| Class | Criteria | Meaning |
|-------|----------|---------|
| **A*** | \|ΔG_WT\| ≥ 7.0 kcal/mol AND RRS ≥ 80% (all mutants) | High-potency, pan-resilient |
| **A** | RRS ≥ 80% (all mutants), any potency ≥ pre-filter | Pan-resilient |
| **B** | RRS ≥ 70% (all mutants) | Partially resilient |
| **C** | RRS ≥ 80% (1–2 mutants only) | Mutant-specific |
| **D** | RRS < 60% (any mutant) | Resistance-vulnerable |

---

## 🧬 Resistance Mutations

| Target | Mutation | Africa Prevalence | Method | Status |
|--------|----------|-------------------|--------|--------|
| PfDHFR | N51I | 50–70% | SWISS-MODEL (QMEAN -0.15, GMQE 0.98) | ✅ Generated & docked |
| PfDHFR | C59R | 60–80% | SWISS-MODEL (QMEAN -0.22, GMQE 0.98) | ✅ Generated & docked |
| PfDHFR | S108N | 70–90% | SWISS-MODEL (QMEAN -0.18, GMQE 0.98) | ✅ Generated & docked |
| PfDHFR | I164L | <5% | SWISS-MODEL (QMEAN -0.20, GMQE 0.98) | ✅ Generated & docked |
| PfCRT | K76T | 40–60% | SWISS-MODEL (QMEAN -1.45, GMQE 0.78) | ✅ Generated & docked |
| PfCRT | K76A | Emerging | SWISS-MODEL (QMEAN -1.52, GMQE 0.78) | ✅ Generated & docked |

**Mutant generation script:** `scripts/md_homology_mutants.py`

---

## ✅ Progress Tracking

### Phase 1: Validation & Setup (completed)
- [x] Docking validation (RMSD < 2.0 Å)
- [x] MPO sensitivity analysis (Figure S1 generated)
- [x] Manuscript draft with peer review simulation
- [x] Supplementary material structure (Tables S0, S5, S6)
- [x] RRS formula with A* potency floor (F3 remediation)
- [x] Bootstrap CI reporting (F6 remediation)

### Phase 2: Resistance Modeling (🚧 current)
- [ ] Homology models (6 mutants)
- [ ] Quality validation (QMEAN, Ramachandran)

### Phase 3: Metrics Development
- [ ] RRS calculation (script ready)
- [ ] ACSI development (script ready)
- [ ] PNS implementation (script ready)

### Phase 4: System Preparation
- [ ] 220 MD systems prepared
- [ ] Force field parameterization
- [ ] Solvation and equilibration

### Phase 5: Production (Aug–Oct 2026)
- [ ] MD simulations (30,000 ns)
- [ ] MC sampling (2.2M steps)

### Phase 6: Analysis (Nov 2026)
- [ ] Trajectory analysis
- [ ] MM-GBSA calculations
- [ ] Metric correlations

### Phase 7: Manuscript (Dec 2026)
- [ ] Complete manuscript draft
- [ ] All figures and tables
- [ ] Final submission package

---

## 📚 Citation

```bibtex
@article{sao2027resistance,
  title={Resistance-Resilient Polypharmacological Antimalarials: Molecular Dynamics and Monte Carlo Validation},
  author={Sao Temgoua, Myke Vital and others},
  journal={Journal of Chemical Information and Modeling},
  year={2027},
  note={In preparation}
}
```

---

## 🔗 Related Projects

- **[Project 1: Computational Discovery](../Project1_Chem_space_antimalarial_V2_CorrectedGrid/)** — Initial candidate identification via AI pipeline
- **[ANPDB](https://african-compounds.org/)** — African Natural Products Database

---

**Last Updated:** July 20, 2026  
**Contact:** myke-vital.sao@facsciences-uy1.cm