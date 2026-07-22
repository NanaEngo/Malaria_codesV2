# Project 4 — Advanced Monte Carlo Strategies (P4)

**Target journal:** *Journal of Chemical Information and Modeling* (JCIM) — ACS
**Status:** Complete architecture — ready for HPC production runs
**Date:** July 2026
**Repository:** https://github.com/NanaEngo/Malaria_codesV2

---

## 1. Project Overview (BMAD-METHOD: Scope & Domain)

P4 implements a **de novo molecular generation framework** combining:
- **MCTS + ScafVAE** — Tree search guided by a chemistry-informed fragment policy (PUCT)
- **Pareto MCTS** — Multi-objective optimization via non-dominated front (HV 0.58)
- **Real P1/P2 oracles** — MPO, docking (Tartarus), SYBA, SA, RRS, PNS
- **4-method benchmark** — MCTS vs Random vs Greedy vs GA (n=5 seeds, statistical significance)
- **QMC validation** — Quantum Monte Carlo pipeline placeholder

**Novelty:** First integration of (1) Pareto-MCTS with ScafVAE-informed fragment policy, (2) multi-method benchmark with scaffold diversity metrics, (3) QMC-based electronic correlation validation for de novo design candidates.

---

## 2. Methodology Applied (scientific-agent-skills)

| Skill | Source | Application in P4 |
|-------|--------|-------------------|
| **medchem** | K-Dense-AI/scientific-agent-skills | Drug-likeness filtering (Lipinski, Veber, PAINS, Brenk) in OracleAggregator |
| **molfeat** (inspired) | K-Dense-AI/scientific-agent-skills | Multi-fingerprint scaffold compatibility (Morgan + MACCS) in ScafVAEPolicy |
| **optimize-for-gpu** | K-Dense-AI/scientific-agent-skills | CuPy batch Tanimoto for GPU-accelerated nearest-neighbour in oracle |
| **experimental-design** | K-Dense-AI/scientific-agent-skills | Stratified seed protocol, independent RNG per replicate, holdout split |

### 2.1 medchem — Drug-Likeness Filters

The `OracleAggregator` now includes drug-likeness filtering via `medchem>=2.0.5`:

```python
# Applied in _medchem_filter():
# - Lipinski Rule-of-Five (MW≤500, logP≤5, HBD≤5, HBA≤10)
# - Veber rules (RotBonds≤10, TPSA≤140)
# - PAINS structural alerts (pan-assay interference)
# - Brenk alerts (undesirable functional groups)
# 
# Falls back to RDKit-only checks when medchem not installed.
```

The `drug_like` flag is included in `score()` output and a small bonus (+0.02) is added in `reward()` for drug-like molecules.

### 2.2 molfeat-Inspired Multi-Fingerprint Policy

The `ScafVAEPolicy` scaffold compatibility score now combines:
- **Morgan fingerprints** (ECFP-like, radius=2, 2048 bits) — weight 0.7
- **MACCS fingerprints** (166 structural keys) — weight 0.3

This provides better chemical space coverage than Morgan alone, as MACCS keys capture functional group presence that Morgan's atomic environment approach may miss.

### 2.3 GPU-Accelerated Batch Tanimoto

The `_batch_tanimoto_gpu()` method uses CuPy (when available) for batch Tanimoto computation:
- Converts RDKit bit-vectors to CuPy dense arrays
- Computes Tanimoto = |A∩B| / (|A| + |B| - |A∩B|) via GPU matrix operations
- Graceful CPU fallback when CuPy is unavailable

### 2.4 Experimental Design

Benchmark protocol:
- 5 independent seeds (n=5 replicates)
- Independent RNG per seed (no seed chaining)
- Odd seeds (1, 3) can serve as holdout/validation split
- Parallel execution via joblib (`--n-jobs`)

---

## 3. File Architecture

```
Project4_Advanced_Monte_CarloV2607/
├── AGENTS.md                    # This file — project methodology
├── README.md                    # Quick-start guide
├── P4_MC_Strategies.md          # Long-term strategic roadmap
├── scripts/
│   ├── p4_mcts_oracles.py       # OracleAggregator with medchem + GPU batch Tanimoto
│   ├── p4_mcts_policy.py        # ScafVAEPolicy with Morgan+MACCS fingerprints
│   ├── p4_mcts_agent.py         # MCTS agent (PUCT, Dirichlet noise, temperature annealing)
│   ├── p4_mcts_rl_env.py        # Molecular RL environment (fragment attachment)
│   ├── p4_mcts_baselines.py     # Random, Greedy, GA baselines (Dirichlet + annealing)
│   ├── p4_mcts_benchmark.py     # Unified 4-method benchmark with stratified seeds
│   ├── p4_mcts_run.py           # CLI runner for single MCTS search
│   ├── p4_mcts_pareto.py        # Pareto MCTS multi-objective optimization
│   ├── p4_mcts_merge.py         # Post-processing + ranking
│   ├── p4_generate_figures.py   # Publication-quality figures (bar, efficiency, Pareto, diversity)
│   └── p4_qmc_*.py              # QMC validation pipeline (skeleton)
├── manuscript/LaTeX/
│   ├── P4_Pareto_MCTS_V2607.tex # Main manuscript (JCIM format)
│   └── P4_Bibliography.bib      # References
└── results/                     # Generated outputs (gitignored)
```

---

## 4. Canonical Files (BMAD-METHOD: Critical Path)

| File | Purpose | Last Updated |
|------|---------|-------------|
| `scripts/p4_mcts_oracles.py` | Core oracle with medchem + CuPy | July 2026 |
| `scripts/p4_mcts_policy.py` | ScafVAE policy with multi-fingerprint | July 2026 |
| `scripts/p4_mcts_agent.py` | MCTS agent with all improvements | July 2026 |
| `scripts/p4_mcts_baselines.py` | GA with Dirichlet noise + annealing | July 2026 |
| `scripts/p4_mcts_benchmark.py` | Unified stratified benchmark | July 2026 |
| `manuscript/P4_Pareto_MCTS_V2607.tex` | Manuscript draft | July 2026 |

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
sbatch --array=0-4%5 scripts/p4_mcts_array.sbatch

# 2. Merge results
python scripts/p4_mcts_merge.py --rescore --top-n 20
```

### 5.3 Figure Generation

```bash
python scripts/p4_generate_figures.py          # All figures
python scripts/p4_generate_figures.py --figures efficiency  # Single figure
```

### 5.4 Manuscript Compilation

```bash
cd manuscript/LaTeX
pdflatex P4_Pareto_MCTS_V2607.tex
bibtex  P4_Pareto_MCTS_V2607
pdflatex P4_Pareto_MCTS_V2607.tex
pdflatex P4_Pareto_MCTS_V2607.tex
```

---

## 6. Skills Integration Summary

| Change | File | Skill Source | Lines |
|--------|------|-------------|-------|
| Drug-likeness filter | `p4_mcts_oracles.py` | scientific-agent-skills: medchem | ~60 |
| GPU batch Tanimoto | `p4_mcts_oracles.py` | scientific-agent-skills: optimize-for-gpu | ~60 |
| Morgan+MACCS policy | `p4_mcts_policy.py` | scientific-agent-skills: molfeat (inspired) | ~40 |
| Stratified seed protocol | `p4_mcts_benchmark.py` | scientific-agent-skills: experimental-design | ~15 |
| Structured documentation | `AGENTS.md` | BMAD-METHOD | This file |

---

## 7. Known Limitations

- **medchem**: Optional dependency; fallback to RDKit-only checks if not installed.
- **CuPy**: Requires NVIDIA GPU + CUDA toolkit; silent CPU fallback otherwise.
- **MACCS fingerprints**: Added to policy only; oracle still uses Morgan for Tanimoto similarity.
- **QMC pipeline**: Skeleton only — needs full implementation for production.
- **Benchmark**: 5 seeds provides basic statistics; 10+ seeds recommended for publication.
