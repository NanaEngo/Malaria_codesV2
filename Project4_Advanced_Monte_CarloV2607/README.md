# Project 4 — Advanced Monte Carlo Strategies (P4)

**Status:** Active development — MCTS+RL proof-of-concept complete, QMC skeleton in place.

This project implements advanced Monte Carlo methods for antimalarial molecular design:
- **MCTS+RL**: Monte Carlo Tree Search with reinforcement-learning-style oracles for de novo molecular generation.
- **QMC**: Quantum Monte Carlo validation pipeline for high-accuracy electronic-structure validation of top candidates (skeleton).

---

## Repository layout

```
Project4_Advanced_Monte_CarloV2607/
├── P4_MC_Strategies.md          # Long-term strategic roadmap
├── README.md                    # This file
├── scripts/                     # Executable scripts
│   ├── p4_mcts_agent.py         # MCTS agent (UCT selection, expansion, rollout, backprop)
│   ├── p4_mcts_rl_env.py       # Molecular RL environment (fragment attachment)
│   ├── p4_mcts_oracles.py      # Real P1/P2 oracles (MPO, docking, SYBA, SA)
│   ├── p4_mcts_run.py          # CLI runner for a single MCTS search
│   ├── p4_mcts_merge.py        # Merge + rank per-task MCTS outputs
│   ├── p4_mcts_array.sbatch    # SLURM array submission
│   ├── p4_qmc_prepare.py       # QMC input preparation (skeleton)
│   └── p4_qmc_analyze.py       # QMC energy analysis (skeleton)
├── results/                     # Generated MCTS outputs (gitignored)
└── logs/slurm/                  # SLURM logs
```

---

## Quick start

### 1. Single MCTS search (local)

```bash
cd scripts
python p4_mcts_run.py \
  --initial-smiles C \
  --max-steps 3 \
  --n-iterations 5 \
  --seed 0 \
  --output-csv ../results/mcts/p4_mcts_seed_0.csv
```

### 2. SLURM array (HPC)

```bash
sbatch --array=0-9%2 scripts/p4_mcts_array.sbatch
```

The array script sets `MAX_STEPS`, `N_ITERATIONS`, and `INITIAL_SMILES` via `--export`.

### 3. Merge and rank results

```bash
python scripts/p4_mcts_merge.py --rescore --top-n 20
```

Output: `results/mcts/p4_mcts_merged_ranked.csv`

---

## Oracles

`p4_mcts_oracles.py` wires the MCTS reward to real P1/P2 data:

| Component | Source | Fallback |
|-----------|--------|----------|
| MPO | `Project2/results/c6_primary_leads_synthesisable.csv` | RDKit QED |
| Docking | `Project2/results/tartarus_output.csv` | Tanimoto nearest-neighbour proxy |
| SYBA | `c6_primary_leads_synthesisable.csv` | `syba` package |
| SA | `c6_primary_leads_synthesisable.csv` | RDKit `sascorer` |

The oracle caches canonical SMILES to avoid recomputing the same molecule during rollouts.

---

## Current results

A 3-task test array completed successfully (job 10597). Each task ran 5 MCTS iterations from a `C` scaffold with `MAX_STEPS=3`.

| Seed | Best state | Best reward |
|-----:|:-----------|------------:|
| 0 | `CO` | 2.600000 |
| 1 | `CC` | 2.600000 |
| 2 | `Cc1ccccc1` | 2.600000 |

Merged output: `results/mcts/p4_mcts_merged_ranked.csv`

---

## QMC pipeline (skeleton)

The QMC components are placeholders for future work:
- `p4_qmc_prepare.py`: prepare geometries and trial wavefunctions.
- `p4_qmc_analyze.py`: analyze correlation energies and compare with QKS/TDA scores.

See `P4_MC_Strategies.md` for the long-term QMC roadmap.

---

## Dependencies

- `malaria_md` conda environment (rdkit, pandas, numpy)
- Optional: `syba` package for on-the-fly synthetic accessibility
- Optional: RDKit `sascorer` contrib for SA score

---

## Canonical files

| File | Purpose |
|------|---------|
| `scripts/p4_mcts_oracles.py` | Real-score oracle aggregator |
| `scripts/p4_mcts_merge.py` | Post-processing and ranking |
| `scripts/p4_mcts_array.sbatch` | Production SLURM array script |

---

## Notes

- `results/` is gitignored; regenerate outputs by running the scripts.
- The MCTS environment currently uses a small fragment vocabulary. Expand `p4_mcts_rl_env.py` to add medicinal-chemistry-aware fragment actions.
- For production runs, increase `--n-iterations` and `--max-steps` and consider parallelizing oracle calls.
