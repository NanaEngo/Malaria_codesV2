# Project 4 — Advanced Monte Carlo Strategies (P4)

**Target journal:** *Journal of Cheminformatics* (JoC) — canonical manuscript: `P4_Pareto_MCTS_JoC_refined.tex`
**Status:** v12-activity 20-seed benchmark complete (optimal MCTS config); canonical JoC manuscript undergoing final editorial validation
**Date:** August 2026
**Repository:** https://github.com/NanaEngo/Malaria_codesV2

---

## 1. Project Overview (BMAD-METHOD: Scope & Domain)

P4 implements a **de novo molecular generation framework** combining:
- **MCTS + ScafVAE** — Tree search guided by a chemistry-informed fragment policy (PUCT) with medchem filters.
- **Pareto MCTS** — Multi-objective optimization via non-dominated front (MPO, SYBA, RRS, PNS; SA is constant and excluded from dominance/HV; HV = 1.2366 under the locked convention).
- **Real P1/P2 oracles** — MPO, docking (Tartarus), SYBA, SA, RRS, PNS.
- **4-method benchmark** — MCTS vs Random vs GA vs Greedy (20 independent seeds, paired t-tests with documented multiplicity).
- **QMC validation** — Two-tiered electronic-structure validation pipeline (wB97X-D DFT + DMC diffusion Monte Carlo).

**Novelty:** First integration of (1) Pareto-MCTS with ScafVAE-informed fragment policy incorporating PAINS/Brenk safety priors, (2) 4-method benchmark with Fréchet ChemNet Distance (FCD) and scaffold diversity metrics, (3) QMC-based electronic correlation validation for de novo design candidates.

---

## 2. Methodology Applied (scientific-agent-skills)

| Skill / Library | Source | Application in P4 |
|-----------------|--------|-------------------|
| **datamol** | K-Dense-AI/scientific-agent-skills | Fast SMILES standardization, scaffold extraction, molecular graph validation |
| **pymoo** | K-Dense-AI/scientific-agent-skills | Exact 2D/3D Hypervolume calculation and non-dominated sorting in Pareto MCTS |
| **medchem** | K-Dense-AI/scientific-agent-skills | Drug-likeness filtering (Lipinski, Veber, PAINS, Brenk) in OracleAggregator |
| **molfeat** (inspired) | K-Dense-AI/scientific-agent-skills | Multi-fingerprint scaffold compatibility (Morgan + MACCS) in ScafVAEPolicy |
| **pytdc** | K-Dense-AI/scientific-agent-skills | Benchmark standardization against Therapeutics Data Commons suites |
| **optimize-for-gpu** | K-Dense-AI/scientific-agent-skills | CuPy batch Tanimoto for GPU-accelerated nearest-neighbour in oracle |
| **experimental-design** | K-Dense-AI/scientific-agent-skills | Stratified 10-seed protocol, full $2^5$ factorial screening, Central Composite Design |

### 2.1 medchem — Drug-Likeness Filters
The `OracleAggregator` includes drug-likeness filtering via `medchem>=2.0.5`:
- Lipinski Rule-of-Five (MW≤500, logP≤5, HBD≤5, HBA≤10)
- Veber rules (RotBonds≤10, TPSA≤140)
- PAINS structural alerts (pan-assay interference)
- Brenk alerts (undesirable functional groups)

### 2.2 molfeat-Inspired Multi-Fingerprint Policy
The `ScafVAEPolicy` scaffold compatibility score combines:
- **Morgan fingerprints** (ECFP-like, radius=2, 2048 bits) — weight 0.7
- **MACCS fingerprints** (166 structural keys) — weight 0.3

### 2.3 GPU-Accelerated Batch Tanimoto
The `_batch_tanimoto_gpu()` method uses CuPy for batch Tanimoto computation, providing up to 50x speedup on NVIDIA GPUs.

### 2.4 Experimental Design (Ablation & Benchmarks)
- **10 independent seeds** per method for statistical power (Wilcoxon signed-rank test).
- **$2^5$ factorial design** (32 runs × 5 replicates) to quantify effects of policy, Pareto, c_puct, temp, and fragment set.
- **Central Composite Design (CCD)** for response-surface optimization of continuous variables.

---

## 3. File Architecture

```
Project4_Advanced_Monte_CarloV2607/
├── AGENTS.md                    # This file — project methodology
├── README.md                    # Quick-start guide
├── P4_MC_Strategies.md          # Long-term strategic roadmap
├── scripts/
│   ├── p4_mcts_oracles.py       # OracleAggregator with medchem + CuPy batch Tanimoto
│   ├── p4_mcts_policy.py        # ScafVAEPolicy with Morgan+MACCS fingerprints
│   ├── p4_mcts_agent.py         # MCTS agent (PUCT, Dirichlet noise, temperature annealing)
│   ├── p4_mcts_rl_env.py        # Molecular RL environment (fragment attachment, datamol)
│   ├── p4_mcts_baselines.py     # Random, Greedy, GA baselines
│   ├── p4_mcts_benchmark.py     # Unified 4-method benchmark (n=10 seeds, FCD, uniqueness)
│   ├── p4_mcts_run.py           # CLI runner for single MCTS search
│   ├── p4_mcts_pareto.py        # Pareto MCTS multi-objective optimization (pymoo)
│   ├── p4_mcts_merge.py         # Post-processing + ranking
│   ├── p4_generate_figures.py   # Publication-quality figures (bar, efficiency, Pareto, diversity)
│   ├── p4_mcts_ablation.py      # $2^5$ factorial design for ablation study
│   └── p4_qmc_*.py              # QMC validation pipeline (Tier 1: wB97X-D, Tier 2: DMC)
├── manuscript/LaTeX/
│   ├── P4_Pareto_MCTS_JoC_refined.tex # Main manuscript (CANONICAL, JoC)
│   ├── P4_Pareto_MCTS_JoC_SM.tex      # Supplementary Material (S1–S6)
│   ├── Cover_Letter_P4_JoC.tex        # Cover letter (JoC)
│   ├── P4_Pareto_MCTS_V2607.tex       # Earlier draft (historical only)
│   └── P4_Bibliography.bib            # References
└── results/                     # Generated outputs (gitignored)
```

---

## 4. Canonical Files (BMAD-METHOD: Critical Path)

| File | Purpose | Last Updated |
|------|---------|-------------|
| `scripts/p4_mcts_oracles.py` | Core oracle with medchem + CuPy | July 2026 |
| `scripts/p4_mcts_policy.py` | ScafVAE policy with multi-fingerprint | July 2026 |
| `scripts/p4_mcts_agent.py` | MCTS agent with trajectory rollout mitigation | July 2026 |
| `scripts/p4_mcts_pareto.py` | Pareto optimization and hypervolume (pymoo) | July 2026 |
| `scripts/p4_mcts_benchmark.py` | 4-method 20-seed benchmark script (v12-activity canonical scalar benchmark) | Aug 2026 |
| `manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex` | **Canonical manuscript (JoC)** | Aug 2026 |
| `manuscript/LaTeX/P4_Pareto_MCTS_JoC_SM.tex` | Supplementary Material (S1–S6) | Aug 2026 |

---

## 5. Workflow (BMAD-METHOD: Structured Process)

### 5.1 Local Development

```bash
# 1. Environment
conda activate malaria_md

# 2. Quick MCTS test
python scripts/p4_mcts_run.py --n-iterations 5 --seed 0

# 3. Quick benchmark (small budget)
python scripts/p4_mcts_benchmark.py \
  --n-iterations 200 \
  --n-seeds 3 \
  --n-jobs 3 \
  --output results/benchmark/p4_benchmark.csv
```

### 5.2 HPC Production

```bash
# 1. Full benchmark (array job)
sbatch --array=0-9%5 \
  --export=N_ITERATIONS=2000,GA_POPULATION=100,GA_GENERATIONS=40,MAX_STEPS=10 \
  scripts/p4_benchmark_array.sbatch

# 2. Merge results
python scripts/p4_mcts_merge.py --rescore --top-n 20
```

### 5.3 Figure Generation

```bash
python scripts/p4_generate_figures.py          # All figures
```

### 5.4 Manuscript Compilation (canonical JoC manuscript)

```bash
cd manuscript/LaTeX
pdflatex P4_Pareto_MCTS_JoC_refined.tex
bibtex P4_Pareto_MCTS_JoC_refined
pdflatex P4_Pareto_MCTS_JoC_refined.tex
pdflatex P4_Pareto_MCTS_JoC_refined.tex
# Supplementary Material
pdflatex P4_Pareto_MCTS_JoC_SM.tex
pdflatex P4_Pareto_MCTS_JoC_SM.tex
```

---

## 6. Skills Integration Summary

| Change | File | Skill Source | Lines |
|--------|------|-------------|-------|
| Drug-likeness filter | `p4_mcts_oracles.py` | scientific-agent-skills: medchem | ~60 |
| GPU batch Tanimoto | `p4_mcts_oracles.py` | scientific-agent-skills: optimize-for-gpu | ~60 |
| Morgan+MACCS policy | `p4_mcts_policy.py` | scientific-agent-skills: molfeat (inspired) | ~40 |
| Pareto front & HV | `p4_mcts_pareto.py` | scientific-agent-skills: pymoo | ~40 |
| 10-seed stratified + 2^5 factorial | `p4_mcts_benchmark.py`, `p4_mcts_ablation.py` | scientific-agent-skills: experimental-design | ~35 |
| Graph standardization | `p4_mcts_rl_env.py` | scientific-agent-skills: datamol | ~20 |
| Structured documentation | `AGENTS.md`, `P4_MC_Strategies.md` | BMAD-METHOD | - |

---

## 7. Known Limitations

- **medchem/datamol**: Optional dependencies; fallbacks to RDKit if not installed.
- **CuPy**: Requires NVIDIA GPU + CUDA toolkit; silent CPU fallback otherwise.
- **QMC pipeline**: VMC/DMC cost limits validation to top-5 candidates.
- **Statistical Significance**: Requires n>=10 seeds for non-parametric tests to achieve robust statistical power.
