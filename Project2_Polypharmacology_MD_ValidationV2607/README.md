# Resistance-Aware Computational Analysis of Antimalarial Leads

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **Project 2 — Set-C polypharmacology docking/RRS analysis plus separate targeted MD of four named parent-study consensus complexes (Project V2607).**

**Target Journal:** *Journal of Chemical Information and Modeling* (IF 5.6)  
**Status:** ✅ Cohort-corrected submission package — 17 set-C candidates for docking/RRS/ACSI/PNS; four separate parent-study MD systems; only 214–PfCRT has interpretable MM-GBSA
**Manuscript:** `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` — canonical V2607 version
**Execution safety:** all future GROMACS wrappers are **dry-run by default**; execution requires `--execute` plus `P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND`. The mitigation workflow itself launched no GROMACS job.

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

This project analyzes the **17 canonical set-C polypharmacology candidates** using docking against wild-type and resistance-mutant PfDHFR/PfCRT structures, followed by RRS, ACSI, PNS, and cross-metric analyses. Separately, production MD was run only for four named parent-study consensus complexes (201–PfDHFR, 438–PfATP4, historical 164–PfClpP cohort label, 214–PfCRT); these four systems are not set-C candidates and do not constitute MD validation of the set-C cohort. The 164 label is not structural PfClpP validation because PDB 4GM2 is PfClpR.

The key innovation is a **resistance-aware validation framework** that quantifies how well each candidate maintains binding against clinically prevalent resistance mutations in African populations.

### Key Objectives

1. **Homology Modeling** — Generate six mutant structures (N51I, C59R, S108N, I164L, K76T, K76A)
2. **Resistance Profiling** — Quantify docking-based binding resilience and chemical/network properties via RRS, ACSI, and PNS
3. **Targeted parent-lead MD** — Analyze four named wild-type complexes, 10 ns each (40 ns total), separately from set C
4. **Bounded set-C pilot** — `scripts/p2_setc_md_workflow.py --auto-approved` selects PP-01/PP-02, validates the 136-row docking panel, and preflights candidate-specific MD systems. Current preflight: **16 systems selected, 0 ready, 16 blocked, 0 GROMACS processes launched**. Any prepared system must include `complex.gro`, `topol.top`, `md.mdp`, `npt.gro`, `npt.cpt`, `system_manifest.json`, and a hash-checked CHARMM36m+CGenFF `forcefield_manifest.json`; otherwise the workflow fails closed without launching GROMACS. The remediation contract is recorded in `results/set_c_md/set_c_preparation_remediation_20260809.md`.

---

## 📊 System Matrix

| Category | Ligands | Targets | Systems | MD (ns/system) | MC Steps | Total MD (ns) |
|----------|---------|---------|---------|---------------|----------|--------------|
| **Set-C docking panel** | 17 | 8 WT/mutant PfDHFR/PfCRT states | 136 | — | — | — |
| **Parent-study MD complexes** | 4 named leads | 4 WT targets | 4 | 10 ns/system | — | **40 ns** |
| **Set-C pilot design** | 2 default candidates | selected PfDHFR/PfCRT states | manifest only | — | — | **0 ns launched** |

**Targets:**
- **PfDHFR-TS (7F3Y)** — WT + N51I, C59R, S108N, I164L (4 mutants)
- **PfCRT (6UKJ)** — WT + K76T, K76A (2 mutants)
- **PfATP4 (9N10)** — WT only
- **PfClpR (4GM2; not PfClpP)** — historical docking record only; not accepted as PfClpP validation

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
│       └── sort_mol2_bonds.pl
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
└── README.md                              → Current project overview and status
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
- **Validation:** `validate_initial_structures.py`, `validate_ligand_pdbs.py`, and `validate_mol2_files.py`
- **Documentation:** `MD_SETUP_REFINED.md`, `TROUBLESHOOTING.md`, `QUICK_START_MD.md`

### Docking Scripts (`scripts/docking/`)
| Script | Purpose |
|--------|---------|
| `consensus_scoring_vina.sh` | Vina consensus scoring across targets |

### Utility Scripts (`scripts/utils/`)
| Script | Purpose |
|--------|---------|
| `sort_mol2_bonds.pl` | Bond sorting for mol2 files |
| `validate_initial_structures.py` | Initial-structure validation |

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

# 4. Inspect the guarded MD plan (does not run GROMACS)
bash scripts/md_full_pipeline.sh --dry-run
# A future run requires explicit authorization after input review:
# P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND bash scripts/md_full_pipeline.sh --execute --yes

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
# All commands below are dry-run unless --execute is explicitly supplied.
bash scripts/md_run_minimisation.sh --dry-run
bash scripts/md_run_nvt.sh --dry-run
bash scripts/md_run_npt.sh --dry-run
bash scripts/md_run_production.sh --dry-run

# Future execution requires BOTH an explicit flag and environment confirmation:
# export P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND
# bash scripts/md_run_production.sh --execute 201_DHFR
```

---

## 🔒 Evidence and execution boundaries

- The canonical set-C cohort contains 17 candidates and 136 docking states; RRS, ACSI, PNS, and cross-metric results are docking/cheminformatics-derived.
- The four parent-study MD systems (201-PfDHFR, 438-PfATP4, historical 164-PfClpP cohort label, 214-PfCRT) are a separate targeted check: 10 ns each, 40 ns total, at 310.15 K. The 164 label is historical and must not be interpreted as PfClpP structural validation from 4GM2, which is PfClpR. They are not set-C MD validation.
- Only 214-PfCRT has an interpretable MM-GBSA estimate (−18.25 ± 0.40 kcal/mol). Dissociated systems and the 438 conversion-corrupted result are reported as non-interpretable.
- `results/metrics/canonical_set_c_provenance.json`, `results/metrics/parent_md_provenance.json`, and `results/metrics/parent_md_execution_policy.json` are the provenance/policy records. The set-C pilot manifest is preflight-only and records `gromacs_launched: false`.
- The reserved Zenodo DOI is not evidence of a completed deposit until the record is publicly populated and independently verifiable.

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

### Phase 4: Cohort-corrected system preparation
- [x] Four parent-study MD systems identified and re-analyzed (10 ns each)
- [ ] Set-C-specific pilot complexes prepared and validated (workflow: `scripts/p2_setc_md_workflow.py`; current preflight is fail-closed)
- [ ] Force-field parameterization, solvation, and equilibration for any future set-C pilot

### Phase 5: Bounded future production
- [x] Pilot selector/preflight manifest generated without launching GROMACS
- [ ] Implement the prepared-system producer that writes the required identity manifest and validates coordinates/topology before any future READY status
- [ ] Explicitly approved set-C MD production
- [ ] Any future MC sampling, with results and convergence diagnostics recorded before manuscript use

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

**Last Updated:** August 7, 2026 — cohort provenance, fail-closed MD wrappers, and evidence boundaries updated
**Contact:** myke-vital.sao@facsciences-uy1.cm