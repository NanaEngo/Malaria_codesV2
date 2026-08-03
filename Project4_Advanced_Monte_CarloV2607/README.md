# Project 4 — Advanced Monte Carlo Strategies (P4)

**Target Journal:** *Journal of Cheminformatics* (JoC) — canonical manuscript: `P4_Pareto_MCTS_JoC_refined.tex`
**Status:** v11 20-seed benchmark complete (optimal MCTS config, job 12725); manuscript ready for submission (Target PA ≥ 85%)
**Date:** August 2026

P4 implements a **de novo molecular generation framework** targeting **African Natural Product (ANP)-inspired antimalarial chemistry**, combining:
- **MCTS + ScafVAE**: Tree search guided by a chemistry-informed fragment policy (PUCT) built on privileged natural product-like antimalarial fragments (chromone, quinoline, indole, terpene derivatives) with medicinal chemistry safety filters (`medchem`: PAINS, Brenk, Veber, Lipinski).
- **Pareto MCTS**: Multi-objective optimization via exact non-dominated front and hypervolume calculation (`pymoo` $WFG$ algorithm, HV ≥ 0.58).
- **Real P1/P2 Oracles**: MPO (≥0.75), docking (Tartarus V2 *P. falciparum* targets), SYBA (>0), SA (<3.5), RRS (selectivity), PNS (polypharmacology), plus GPU-accelerated CuPy batch Tanimoto lookup.
- **4-Method Benchmark**: MCTS+ScafVAE vs. Random vs. Greedy vs. GA across 20 independent seeds with paired t-testing and real best-in-seed molecule sets. The **v11 benchmark** (20 seeds, screened-optimal MCTS config `c_PUCT=5.0, ν=0.01, T=0.8`, job 12725) is the canonical P4 benchmark; the v10 default-config run is retained as sensitivity comparison.
- **QMC Validation**: Two-tiered electronic-structure validation pipeline (Tier 1: wB97X-D DFT; Tier 2: DMC diffusion Monte Carlo gold standard). QMC results were removed from the manuscript pending a reproducible validation run.

---

## 1. Repository Layout

```
Project4_Advanced_Monte_CarloV2607/
├── AGENTS.md                    # Project methodology & skills mapping
├── README.md                    # This file — overview & quick start
├── P4_MC_Strategies.md          # Long-term strategic roadmap
├── scripts/
│   ├── p4_mcts_oracles.py       # OracleAggregator with medchem + CuPy batch Tanimoto
│   ├── p4_mcts_policy.py        # ScafVAEPolicy with Morgan+MACCS fingerprints
│   ├── p4_mcts_agent.py         # MCTS agent (PUCT, Dirichlet noise, rollout fix)
│   ├── p4_mcts_rl_env.py        # Molecular RL environment (datamol graph sanitization)
│   ├── p4_mcts_baselines.py     # Random, Greedy, Genetic Algorithm baselines
│   ├── p4_mcts_benchmark.py     # Unified 4-method benchmark (n=10 seeds, FCD, uniqueness)
│   ├── p4_mcts_run.py           # CLI runner for single MCTS search
│   ├── p4_mcts_pareto.py        # Pareto MCTS multi-objective optimization (pymoo)
│   ├── p4_mcts_merge.py         # Post-processing & ranking
│   ├── p4_mcts_ablation.py      # Full 2^5 factorial design ablation study
│   ├── p4_generate_figures.py   # Publication-quality figures (bar, violin, radar, MDS)
│   └── p4_qmc_*.py              # QMC electronic-structure validation pipeline
├── manuscript/LaTeX/
│   ├── P4_Pareto_MCTS_JoC_refined.tex # Main manuscript (CANONICAL, JoC)
│   ├── P4_Pareto_MCTS_JoC_SM.tex      # Supplementary Material (S1–S3)
│   ├── Cover_Letter_P4_JoC.tex        # Cover letter (JoC)
│   ├── P4_Pareto_MCTS_V2607.tex       # Earlier draft (historical only)
│   └── P4_Bibliography.bib            # References
└── results/                     # Generated MCTS outputs & figures (gitignored)
```

---

## 2. Methodology & Skills Integration

| Skill / Library | Ecosystem Source | Application in P4 |
|-----------------|------------------|-------------------|
| **`datamol`** | `scientific-agent-skills` | Fast SMILES standardization (`dm.sanitize_smiles`), Bemis-Murcko scaffold extraction, and molecular graph validation. |
| **`pymoo`** | `scientific-agent-skills` | Exact 2D/3D Hypervolume calculation ($WFG$ algorithm) and non-dominated sorting (`NonDominatedSorting`). |
| **`medchem`** | `scientific-agent-skills` | Structural safety alerts (PAINS A/B/C, Brenk, Veber, Lipinski Ro5) in `OracleAggregator`. |
| **`molfeat`** | `scientific-agent-skills` | Dual Morgan (radius 2, 2048-bit) + MACCS (166-key) multi-fingerprint scaffold compatibility. |
| **`pytdc`** | `scientific-agent-skills` | Benchmark standardization against Therapeutics Data Commons suites. |
| **`optimize-for-gpu`** | `scientific-agent-skills` | CuPy dense matrix Tanimoto operations (`_batch_tanimoto_gpu()`) for 50$\times$ GPU speedup. |
| **`experimental-design`** | `scientific-agent-skills` | Stratified 10-seed execution, full $2^5$ factorial design ($32 \times 5 = 160$ runs), and response surface CCD. |

---

## 3. Quick Start

### Local Single Run / Test Benchmark
```bash
# 1. Activate environment
conda activate malaria_md

# 2. Single MCTS run with Pareto optimization
python scripts/p4_mcts_run.py --pareto --objectives mpo,syba,sa --seed 0

# 3. Small local benchmark test
python scripts/p4_mcts_benchmark.py --n-iterations 200 --n-seeds 3 --n-jobs 3
```

### HPC Production Benchmark (10 Seeds)
```bash
sbatch --array=0-9%5 \
  --export=N_ITERATIONS=2000,GA_POPULATION=100,GA_GENERATIONS=40,MAX_STEPS=10 \
  scripts/p4_benchmark_array.sbatch
```

### Ablation Study ($2^5$ Factorial Design) & Visualization
```bash
python scripts/p4_mcts_ablation.py --n-replicates 5
python scripts/p4_generate_figures.py
```

---

## 4. Oracles & Reward Structure

The `OracleAggregator` links MCTS rewards to real P1/P2 antimalarial data:

| Component | Primary Source | Fallback / Proxy |
|-----------|----------------|------------------|
| **MPO** | `c6_primary_leads_synthesisable.csv` | RDKit QED |
| **Docking** | `tartarus_output.csv` (Tartarus V2) | Tanimoto nearest-neighbour proxy ($R^2=0.88$) |
| **SYBA** | `c6_primary_leads_synthesisable.csv` | `syba` package |
| **SA** | `c6_primary_leads_synthesisable.csv` | RDKit `sascorer` |
| **MedChem Safety** | `medchem>=2.0.5` | PAINS/Brenk/Veber filters |

---

## 5. Submission Checklist & FAIR Compliance

- **Target Journal**: *Journal of Cheminformatics* (JoC)
- **Title**: *"Pareto-guided Monte Carlo tree search explores multi-objective trade-offs missed by scalar antimalarial generation"*
- **Data Availability**: FAIR compliant via Zenodo (DOI: `10.5281/zenodo.19608875`) and GitHub (`https://github.com/NanaEngo/Malaria_codesV2`).
- **Canonical v11 Benchmark**: `results/benchmark_molecules_opt/p4_benchmark_merged.csv` (20 seeds × 4 methods, optimal MCTS config). See `P4_DATA_ANALYSIS_REPORT.md` for the consolidated results.
