# Paper 3: Topological and Tensor-Network Representations Resolve Chemical Space Paradoxes

## Working Title

Topological and Tensor-Network Representations Resolve Chemical Space Paradoxes in African Antimalarial Natural Products

---



> **Data-analysis audit (2026-07-18):** Active P3 results are currently located under `Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/results/` and are being consolidated into the canonical top-level directory. Known issues: ✅ PHCO descriptor bug fixed — AUC rose from 0.500 to ~0.83 after replacing `ConvertToNumpyArray` with manual `GetOnBits()` bit-setting; ✅ QKS headline reconciled — canonical result is Quantum AUC 0.751 vs RBF 0.701 (p=0.088, ns) on 500 molecules; the 0.936/0.105 claim was unsupported and has been removed. See `BMAD_Q1_DATA_ANALYSIS_REPORT.md` §2 for the full audit and SLURM correction plan.
>
> **P3 phase2 SLURM job audit & fixes (2026-07-20):** Running jobs audited and four issues fixed in `scripts/p3_quantum_param_search.py` and `scripts/p3_phase2_array.sbatch`: (1) `PicklingError` on PennyLane `StateVectorC128` — removed the `--hpc` auto-detect flag and forced `n_jobs=1`; (2) race condition on shared `p3_quantum_params_sweep.csv` — added `--output-csv` so each array task writes a unique file; (3) OpenMP oversubscription — set `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`; (4) TFP imputation bug — missing SMILES now padded with `NaN` instead of zeros so mean imputation runs. Bash error handling improved with an `err_handler` trap.
>
> **Smoke tests (2026-07-20):** Single-process test (`--n-mols 50`) completed in ~44 s with AUC 0.8697 ± 0.1002 (verification only, not a benchmark result). Parallel two-process test with distinct `--output-csv` files completed successfully, confirming no race condition.
>
> **Current P3 phase2 jobs:**
> - `10594_0` (bd6_nr1_nk30): RUNNING, fixed script
> - `10595_1` (bd6_nr6_nk30): RUNNING, fixed script
> - `10595_2` (bd6_nr6_nk20): RUNNING, fixed script
>
> **Next steps for P3 relaunch:** import P1 full-cluster 1815-mol panel (`Project1_Chem_space_antimalarial_V2_CorrectedGrid/results/r8b/fullcluster_rescoring/docking_results.csv`) into P3, run TDA and QKS benchmarks on this congeneric series, and update §3.3/§4.7 of the manuscript. See `BMAD_Q1_DATA_ANALYSIS_REPORT.md` §4 for the full P3 phase2 SLURM audit and fix details.
## Overview

| Attribute | Details |
|-----------|---------|
| **Status** | v0.7 — TDA/TNE/QKS/GA benchmarks complete; PHCO fixed (GetOnBits, AUC 0.500→0.801); QKS reconciled (0.751 vs 0.701); 5K molecule optimization running (job 7943) |
| **Target Journal** | *Journal of Cheminformatics* (IF 6.5) |
| **Bibliography style** | BMC (`\bibliographystyle{bmc-mathphys}`) |
| **Timeline** | June 2026 – February 2027 |
| **Submission target** | February 2027 |
| **Acceptance probability** | ~75% (pre-results) |

## Novelty Claims

| ID | Claim |
|----|-------|
| **N5** | First systematic TDA vs. ECFP4 benchmark on natural product chemical space |
| **N6** | First use of persistent homology to explain a chemical space paradox (92.6% Tanimoto novelty vs. 69.3% scaffold recovery) |
| **N7** | First tensor network descriptor compression for a drug discovery library (d=8 → 5.9× compression) |
| **N8** | First applicability domain analysis using quantum kernel density for NP compounds |

## Scope

- **Library**: 65,856 molecules from African NP chemical space
- **Methods**: TFP (12-dim persistent homology), TNE (Tucker d=8, 5.9× compression), QKS (8-qubit PennyLane)
- **Benchmark**: 5-fold CV, RF + SVM, Bonferroni-corrected paired t-tests
- **QK subsample**: 10,000 molecules (O(N²) scaling constraint)
- **Scaffold paradox**: H₁ preservation vs. H₀ divergence (Wilcoxon test)
- **VAE baseline**: Silhouette 0.229 (Paper 1); target TNE Silhouette > 0.35

## Key Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| TFP dimension | 12 (3 dims × 4 statistics) | Roadmap Step 2 |
| Persistence threshold | 0.5 Å (noise filter) | Roadmap Step 2 |
| TNE bond dimension | d=8 (default) | Roadmap Step 3 |
| TNE compression | 5.9× (512 vs 3,000 elements) | Roadmap Step 3 |
| QK qubits | 8 (PennyLane default.qubit) | Roadmap Step 4 |
| QK dim reduction | UMAP (Jaccard metric, not PCA) | Roadmap Step 4 |
| QK subsample | 10,000 molecules | Roadmap Step 4 |
| Hybrid ref set | 500 molecules (MaxMin diversity) | Roadmap Step 5 |
| Default weights | α=0.40 (TFP), β=0.35 (TNE), γ=0.25 (QK) | Roadmap Step 5 |
| KMeans k | 484 (matching Paper 1) | Roadmap Step 2/3 |
| CV folds | 5-fold stratified | Roadmap Step 6 |
| RF trees | 200 | Roadmap Step 6 |

## Files

| File | Description |
|------|-------------|
| [`LaTeX/Paper3_Quantum_InspiredV2607.tex`](LaTeX/Paper3_Quantum_InspiredV2607.tex) | **Canonical manuscript (v0.7)** — all sections written; siunitx/cleveref/booktabs/xr applied; internal version labels and job IDs removed; ready for submission |
| [`LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex`](LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex) | **Supplementary Material** — contains the H$_1$ vs RRS cross-paper violin figure (`fig:h1_rrs`) |
| [`LaTeX/Paper3_Draft_v0.6.tex`](../../.archive_P3_V2607_20260720/manuscript/LaTeX/Paper3_Draft_v0.6.tex) | `Malaria_codesV2/.archive_P3_V2607_20260720/manuscript/LaTeX/Paper3_Draft_v0.6.tex` | Deprecated draft — archived for historical reference only; do not edit |
| [`LaTeX/Bibliography_Paper3.bib`](LaTeX/Bibliography_Paper3.bib) | 50+ references (zero missing citations) |
| Zenodo DOI | [`10.5281/zenodo.19608875`](https://doi.org/10.5281/zenodo.19608875) — archived data, benchmark CSVs, and analysis scripts |

## Scripts

| Script | Purpose | Roadmap Step |
|--------|---------|--------------|
| `Scripts/p3_tda_pipeline.py` | Vietoris-Rips persistence diagrams + TFP extraction | Steps 1–2 |
| `Scripts/p3_tda_pipeline.py --pilot` | Pilot run on 100 molecules (wall-time check) | Step 1 |
| `Scripts/p3_tne_pipeline.py` | Tucker decomposition + TNE embeddings | Step 3 |
| `Scripts/p3_qks_benchmark.py` | 8-qubit quantum kernel vs RBF-SVM benchmark | Step 4 |
| `Scripts/p3_hybrid_benchmark.py` | Hybrid framework + ablation study | Steps 5–6 |

## Quick Start

```bash
# 1. Create and activate Paper 3 environment
conda env create -f environment_paper3.yml
conda activate malaria_paper3

# 2. Pilot run (100 molecules, ~5 min)
python Papers/Quantum_Inspired_Representations/Scripts/p3_tda_pipeline.py --pilot
python Papers/Quantum_Inspired_Representations/Scripts/p3_tne_pipeline.py --pilot

# 3. Full library (65,856 molecules)
python Papers/Quantum_Inspired_Representations/Scripts/p3_tda_pipeline.py --n-jobs 4
python Papers/Quantum_Inspired_Representations/Scripts/p3_tne_pipeline.py --bond-dim 8

# 4. Quantum kernel benchmark (10,000-molecule subsample)
python Papers/Quantum_Inspired_Representations/Scripts/p3_qks_benchmark.py --n-mols 10000

# 5. Hybrid framework + ablation
python Papers/Quantum_Inspired_Representations/Scripts/p3_hybrid_benchmark.py
```

## JCIM Reinforcements Addressed

| Code | JCIM Criticism | Response in Paper 3 |
|------|---------------|---------------------|
| R7 | VAE latent space lacks validation (Silhouette 0.229) | §3.3 TFP vs. VAE comparison (Silhouette, CH, DB indices) |
| R8 | KMeans clustering "methodological decoration" | §3.6 TNE clustering benchmark vs. ECFP4 vs. VAE |
| R9 | African NPs outside applicability domain of Ersilia models? | §3.8 Quantum kernel density applicability domain analysis |
| R10 | Tanimoto/scaffold paradox flagged as data inconsistency | §3.4 Scaffold paradox resolution via H₁/H₀ persistent homology |

## Authors

Myke Vital Sao Temgoua, Jean-Pierre Tchapet Njafa, Serge Guy Nana Engo, Penabei Samafou, Wilfred Fon Mbacham

---

**Roadmap:** [`docs/PAPERS_2_3_ROADMAP.md`](../../docs/PAPERS_2_3_ROADMAP.md) (v2.2)
**Last Updated:** July 20, 2026