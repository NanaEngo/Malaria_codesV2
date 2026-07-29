# Malaria_codesV2 — Source of Truth

> **Authoritative folder containing the most up-to-date versions of all four projects in the antimalarial discovery pipeline.**

## Projects

| # | Directory | Focus | Status |
|---|-----------|-------|--------|
| **1** | `Project1_Chem_space_antimalarial_V2_CorrectedGrid/` | AI discovery of antimalarials from African chemical space | ✅ Submission-ready (JCIM) |
| **2** | `Project2_Polypharmacology_MD_ValidationV2607/` | MD/MC validation of polypharmacological leads | ✅ Submission-ready (JCIM) |
| **3** | `Project3_Quantum_Inspired_RepresentationsV2607/` | Quantum-inspired ML for molecular representation | 🔄 Manuscript in revision — corrected classical benchmark complete (ECFP4 AUC 0.949); full hybrid rerun pending |
| **4** | `Project4_Advanced_Monte_CarloV2607/` | Pareto MCTS for de novo antimalarial design | 🔄 Manuscript in preparation — v9 20-seed benchmark complete |

## Quick Reference

```
Malaria_codesV2/
├── README.md
├── Project1_Chem_space_antimalarial_V2_CorrectedGrid/     → 12 scripts, LaTeX, bibliography, results
│   ├── scripts/       (r1a, r1b, p1 analysis)
│   ├── manuscript/    (LaTeX + compiled PDFs)
│   ├── bibliography/  (3 .bib files, 55 entries)
│   └── r1b_mmv_results/
├── Project2_Polypharmacology_MD_ValidationV2607/  → 48 .py, 15 .sh, LaTeX, data, Tuto
│   ├── scripts/       (pipeline + preparation + docking + utils)
│   ├── manuscript/    (Paper2 + Supplementary + Tables S0/S5/S6)
│   ├── Tuto_MD_MC/    (MD protocol, Gromacs_inputs, Test system)
│   ├── data/          (from_project1, proteins, external)
│   └── docs/          (SITUATION_REPORT.md)
└── Project3_Quantum_Inspired_RepresentationsV2607/ → 4 scripts, LaTeX
    ├── scripts/       (TDA, TNE, QK, hybrid benchmarks)
    └── manuscript/LaTeX/ (Paper3 + bibliography)

Project4_Advanced_Monte_CarloV2607/ → Pareto MCTS + QMC validation
    ├── scripts/       (MCTS, Pareto, baselines, QMC)
    └── manuscript/LaTeX/ (P4 manuscript + bibliography)
```

## Repository

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/NanaEngo/Malaria_codesV2 |
| Zenodo | 10.5281/zenodo.19608875 |

**Version:** V2607 (July 29, 2026)

## Data Analysis & Provenance

The canonical source of truth for all project data, provenance, and analysis decisions is `BMAD_Q1_DATA_ANALYSIS_REPORT.md`. Manuscript updates must follow the workflow: **raw data → data-analysis report → manuscript**.

## Results Location Note (2026-07-29)

The canonical results directories for the four projects are:
- **P1:** `/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/results/`
- **P2:** `/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/`
- **P3:** `/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/results/`
- **P4:** `/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/results/`

See `BMAD_Q1_DATA_ANALYSIS_REPORT.md` for the full data-analysis audit and SLURM correction plan.
