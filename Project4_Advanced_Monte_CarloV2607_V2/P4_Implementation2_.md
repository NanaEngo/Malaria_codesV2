# Implementation Plan — P4 Completion & HPC Execution

This plan details the implementation of the remaining technical components for **Project 4 (Advanced Monte Carlo Strategies)** to achieve 100% submission readiness for *Journal of Chemical Information and Modeling* (JCIM).

## User Review Required

> [!IMPORTANT]
> - **QMC Execution:** Quantum Monte Carlo (DMC via PySCF/QMCPACK) is computationally intensive (~1000 CPU-hours per candidate). Tier 1 (GFN2-xTB geometry optimization + PBE DFT trial orbitals) will be run first, followed by Tier 2 VMC/DMC pilots on the top-5 Pareto candidates.
> - **Cover Letter:** The JCIM cover letter must strictly evaluate P4 independently without referencing companion papers (P1, P2, P3).

## Proposed Changes

---

### Component 1: Factorial $2^5$ Ablation Study & ANOVA
#### [NEW] [p4_mcts_ablation.py](file:///home/taamangtchu/Documents/Github/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/scripts/p4_mcts_ablation.py)
- Implements a full $2^5 = 32$ run factorial design matrix (factors: ScafVAE policy, Pareto front, $c_{\text{PUCT}}$, Temperature, Fragment vocabulary) with 5 replicates per run (160 total evaluations).
- Evaluates main effects, 2-way interactions, ANOVA $F$-tests, and generates Pareto chart of standardized effects.

#### [NEW] [p4_ablation_factorial.sbatch](file:///home/taamangtchu/Documents/Github/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/scripts/p4_ablation_factorial.sbatch)
- SLURM array script (`--array=0-31%8`) running the 32 factorial design points on the HPC cluster.

---

### Component 2: QMC Tier 1/2 Execution Pipeline
#### [NEW] [p4_qmc_pipeline.py](file:///home/taamangtchu/Documents/Github/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/scripts/p4_qmc_pipeline.py)
- Selects top-5 Pareto candidates from `results/pareto/`.
- Tier 1: GFN2-xTB 3D geometry optimization + PySCF PBE/def2-SVP (with ECP) trial wavefunctions.
- Tier 2: VMC energy evaluation + Slater-Jastrow DMC trial preparation.

#### [NEW] [p4_qmc_array.sbatch](file:///home/taamangtchu/Documents/Github/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/scripts/p4_qmc_array.sbatch)
- SLURM execution script for HPC QMC pipeline (`--array=0-4`).

---

### Component 3: TOC & Publication Figure Generator
#### [NEW] [p4_generate_toc.py](file:///home/taamangtchu/Documents/Github/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/scripts/p4_generate_toc.py)
- Generates publication-ready 300 DPI TOC Graphical Abstract (`Graphics/toc_graphical_abstract.png`) summarizing MCTS + ScafVAE + Pareto Front + QMC validation.

---

### Component 4: JCIM Cover Letter
#### [NEW] [Cover_Letter_JCIM.tex](file:///home/taamangtchu/Documents/Github/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/Cover_Letter_JCIM.tex)
- Formal 1-page JCIM Cover Letter adhering to ACS submission rules (independent evaluation, zero companion paper cross-references).

---

## Verification Plan

### Automated Verification
1. **Factorial Ablation Script:** Test single run locally (`python scripts/p4_mcts_ablation.py --test-run`) before submitting SLURM array.
2. **QMC Pipeline Script:** Verify xTB + PySCF energy evaluation on 1 test SMILES.
3. **TOC Figure:** Verify 300 DPI output image generation in `Graphics/toc_graphical_abstract.png`.
4. **Cover Letter Compilation:** Compile `Cover_Letter_JCIM.tex` using `pdflatex`.

### HPC Deployment
1. Sync all new scripts and files to HPC (`nanaengo@100.73.21.40`).
2. Submit SLURM array jobs (`sbatch scripts/p4_ablation_factorial.sbatch` and `sbatch scripts/p4_qmc_array.sbatch`).
3. Verify output files in `results/ablation/` and `results/qmc/`.
