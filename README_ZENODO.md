# Zenodo Deposit — Malaria Codes V2607

**DOI:** [10.5281/zenodo.19608875](https://doi.org/10.5281/zenodo.19608875)
**Repository:** [github.com/NanaEngo/Malaria_codesV2](https://github.com/NanaEngo/Malaria_codesV2)
**Licence:** MIT (code), CC-BY 4.0 (data)
**Deposit date:** July 29, 2026

## Scope

This deposit archives all computational results, scripts, and LaTeX source for four complementary projects addressing antimalarial drug discovery through AI-driven chemical space exploration, polypharmacology MD validation, quantum-inspired molecular representations, and advanced Monte Carlo search strategies.

## Project Inventory

### Project 1 — AI-Driven Chemical Space Exploration
~175 files, ~72 MB

**Description:** Generative expansion of African natural product chemical space (65,856 molecules), multi-parameter optimization, consensus docking across four *Plasmodium falciparum* resistance targets, enrichment validation, and full-cluster rescoring.

**Key data files:**
- `results/p1_enrichment_chembl_benchmark.csv` — ChEMBL enrichment (3/4 targets)
- `results/r8b/fullcluster_rescoring/docking_results.csv` — 1,815 fully docked molecules
- `results/p1_mcmc_generated.csv` — MCMC latent space optimization results
- `results/p1_stoned_leap_results.csv` — STONED-SELFIES neighbourhood sampling
- `manuscript/Antimalarial_Candidates_African_NP_V2607.tex` — Main manuscript
- `manuscript/Antimalarial_Candidates_African_NP_V2607_SM.tex` — Supplementary Material

### Project 2 — Polypharmacology MD Validation
~493 files, ~459 MB

**Description:** MD validation of 20 high-confidence polypharmacological leads across four resistance-relevant *P. falciparum* targets (PfDHFR, PfCRT, PfATP4, PfClpP). Includes MM-GBSA binding free energies, resistance resilience scoring, African Chemical Space Index, and cross-metric correlation analysis.

**Key data files:**
- `results/c_rrs_classification.csv` — Resistance Resilience Score classification (14 compounds)
- `results/mutant_docking_results.csv` — Docking across 6 PfDHFR resistance mutants
- `results/c_merged_metrics.csv` — Unified PNS/ACSI/RRS/dG dataset
- `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` — Main manuscript
- `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex` — Supplementary Material

### Project 3 — Quantum-Inspired Molecular Representations
~147 files, ~37 MB

**Description:** Topological Data Analysis (persistent homology), Tensor Network Embedding (Tucker decomposition), and Quantum Kernel Scores on 19,849 African antimalarial candidates. Full benchmark against 8 classical fingerprints, SOTA topological benchmark, ChEMBL experimental validation, and cross-paper H₁-RRS correlation analysis.

**Key data files:**
- `results/p3_hybrid_benchmark.csv` — Full 10-descriptor benchmark (19,849 molecules)
- `results/p3_sota_benchmark.csv` — SOTA topological benchmark (5 descriptor strategies)
- `results/p3_rrs_tfp_final.csv` — Expanded H₁-RRS correlation (500 compounds)
- `results/p3_chembl_validation/p3_chembl_validation.csv` — ChEMBL structural analogues
- `manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex` — Main manuscript
- `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex` — Supplementary Material

### Project 4 — Pareto-Guided MCTS with Quantum Validation
~43 files, ~1.5 MB

**Description:** Pareto multi-objective Monte Carlo Tree Search with ScafVAE-informed fragment policy for *de novo* antimalarial design. Canonical v9 four-method benchmark (MCTS, Random, Greedy, GA) across 20 independent seeds with non-parametric Wilcoxon signed-rank testing, Fréchet ChemNet Distance (FCD), and scaffold uniqueness. QMC validation removed pending a reproducible rerun.

**Key data files:**
- `results/benchmark/p4_benchmark_merged.csv` — Canonical v9 20-seed four-method benchmark
- `results/benchmark/p4_pareto_data.csv` — Pareto front data
- `manuscript/LaTeX/P4_Pareto_MCTS_V2607.tex` — Main manuscript

## File Manifest

A complete file listing with sizes is available in `zenodo_manifest.txt` at the repository root.

## How to Use

1. All Python scripts use conda environment `malaria_md` (rdkit 2025.03.6, pennylane 0.45.1, tensorly 0.9.0, numpy 1.26.4)
2. SLURM scripts target the University of Yaoundé I HPC facility
3. LaTeX manuscripts target *Journal of Cheminformatics* (P1, P3), *Journal of Chemical Information and Modeling* (P4), and *ACS Infectious Diseases* (P2)
4. See individual project README.md files for detailed instructions

## Citation

If you use this dataset, please cite:

> Sao Temgoua, M. V., Tchapet Njafa, J.-P., Nana Engo, S. G., Samafou, P., & Fon Mbacham, W. (2026). Persistent homology decomposes the scaffold paradox in AI-generated African antimalarial candidates [Data set]. Zenodo. https://doi.org/10.5281/zenodo.19608875

## Contact

Corresponding author: myke-vital.sao@facsciences-uy1.cm
