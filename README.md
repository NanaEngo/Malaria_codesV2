# Malaria_codesV2 — Source of Truth

> **Authoritative folder containing the most up-to-date versions of all three projects in the antimalarial discovery pipeline.**

## Projects

| # | Directory | Focus | Status |
|---|-----------|-------|--------|
| **1** | `Project1_Chem_space_antimalarial_V2_CorrectedGrid/` | AI discovery of antimalarials from African chemical space | ✅ Submission-ready (JCIM) |
| **2** | `Project2_Polypharmacology_MD_ValidationV2607/` | MD/MC validation of polypharmacological leads | ✅ RRS table populated (14 PP, classes A*–D); PP-11 C59R mechanism resolved; Named docking (7948) pending |
| **3** | `Project3_Quantum_Inspired_RepresentationsV2607/` | Quantum-inspired ML for molecular representation | ✅ PHCO fixed (0.500→0.801); QKS reconciled (0.751 vs 0.701); 5K benchmark running (7943) |

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
```

## Repository

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/NanaEngo/Malaria_codesV2 |
| Zenodo | 10.5281/zenodo.19608875 |

**Version:** V2607 (July 4, 2026)

## Local ASKCOS deployment

A self-administered ASKCOS Docker deployment lives outside this repo at . A symlink at  (repo root) points to it for project-relative path compatibility. See  for the setup recipe.

## Results Location Note (2026-07-18)

The canonical results directories for the three projects are:
- **P1:** `/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/results/`
- **P2:** `/home/nanaengo/Project2_Polypharmacology_MD_ValidationV2607/results/` (currently empty; active results are in `Malaria_codesV2/Project2.../results/` and will be rsynced)
- **P3:** `/home/nanaengo/Project3_Quantum_Inspired_RepresentationsV2607/results/` (currently empty; active results are in `Malaria_codesV2/Project3.../results/` and will be rsynced)

See `BMAD_Q1_DATA_ANALYSIS_REPORT.md` §2 for the full data-analysis audit and SLURM correction plan.
