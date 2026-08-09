# Malaria_codesV2 — Source of Truth

> **Authoritative folder containing the most up-to-date versions of the five projects in the antimalarial discovery pipeline.**

## Projects

| # | Directory | Focus | Status |
|---|-----------|-------|--------|
| **1** | `Project1_Chem_space_antimalarial_V4_CorrectedGrid/` | AI discovery of antimalarials from African chemical space | 🔄 Author-controlled scientific development; PfClpP/2F6I revalidation remains an active QC task, with no editorial block before explicit reactivation |
| **2** | `Project2_Polypharmacology_MD_ValidationV2607/` | MD/MC validation of polypharmacological leads against resistance mutations | ✅ Submission-ready (JCIM) |
| **3** | `Project3_Quantum_Inspired_RepresentationsV2607/` | Quantum-inspired ML for molecular representation | ✅ Submission-ready — canonical benchmarks complete (ECFP4 0.9475, Hybrid 0.8876, QKS 6q parity); manuscript trimmed 26→18 p. (main 18 p. / SM 18 p. / cover letter 1 p., 0 erreur / 0 réf. indéfinie) |
| **4** | `Project4_Advanced_Monte_CarloV2607/` | Pareto MCTS for de novo antimalarial design | ✅ Manuscript ready (JoC) — v11 20-seed benchmark complete (optimal MCTS config, re-run 02/08, reproducible); multi-objective front comparison (HV/IGD/C-metric) |
| **5** | `Project5_GNN_Transformer_DrugDiscovery/` | GNN/transformer benchmark against classical fingerprints on the canonical antimalarial panel | 🔄 Manuscript V2608 drafted — benchmark complete (ECFP4 0.9433 / scaffold 0.8300 > GIN > ChemBERTa); honest-negative + attribution thesis |

## Gaps & Novelty (cross-project)

The programme is anchored on **antimalarial drug resistance mitigation via African natural products (P1–P2)**, then tests whether representational/algorithmic complexity beats simple baselines (**P3–P5**).

| Project | Gap addressed | Novelty / Differentiator |
|---------|---------------|--------------------------|
| **P1** | Docking pipelines evaluated in-distribution only | DEKOIS 2.0 honest-negative (AUC 0.450) + MMV positive control; MPO orthogonal to docking (ρ=0.013) |
| **P2** | Resistance validated by affinity alone, not structure | RRS score (% WT binding retained across mutants, PfDHFR N51I/C59R/S108N/I164L, PfCRT K76T); PP-11 C59R clash mechanism resolved |
| **P3** | "Larger/quantum is better" untested on NP space | First canonical QKS ≈ RBF benchmark at n=19,849 (p=0.060); TNE 6.1× real compression retains binding; TDA H₁ rigidity→promiscuity map; 92.6% ECFP4-unreachable gap resolved |
| **P4** | Scalar rewards collapse objective trade-offs | First Pareto-guided MCTS to fold **RRS (resistance-resilience)** and PNS into the generation objective (front HV 1.2366) — the resistance thread P2→P4 |
| **P5** | Benchmark saturation + "larger is better" dogma (Karim et al. 2026 review, G1–G3) | Anti-saturation benchmark: fixed panel, scaffold-split OOD evaluation, topological fusion (TFP/TNE) attribution — honest-negative "fingerprints hold, attribution is the value", anchored on P2/P3 oracles (G7) |

**Unified thesis:** across kernels, graphs, transformers and generation, complexity does not beat simple baselines on scalar objectives on this programme; its value is qualitative (attribution, diversity). Cf. `P5_DESIGN_GAPS_NOVELTY.md` for the full gap→lever mapping (Karim et al. 2026, 10.1007/s11831-026-10743-z).

## Quick Reference

```
Malaria_codesV2/
├── README.md
├── AGENTS.md                      ← LA BOUSSOLE (workflow, état des projets)
├── BMAD_Q1_DATA_ANALYSIS_REPORT.md    ← Data analysis report P1–P3 (canonique)
├── P4_DATA_ANALYSIS_REPORT.md         ← Data analysis report P4 (canonique)
├── P5_DATA_ANALYSIS_REPORT.md         ← Data analysis report P5 (canonique)
├── P5_DESIGN_GAPS_NOVELTY.md          ← P5 design v2, piloté par les gaps (revue 2026)
├── P5_STRATEGIC_PA90.md               ← Plan stratégique P5 (PA ≥ 90%)
├── Project1_Chem_space_antimalarial_V2_CorrectedGrid/  → 12 scripts, LaTeX, bibliography, results
├── Project2_Polypharmacology_MD_ValidationV2607/        → 48 .py, 15 .sh, LaTeX, data, Tuto
├── Project3_Quantum_Inspired_RepresentationsV2607/      → scripts, LaTeX (V2608), results
├── Project4_Advanced_Monte_CarloV2607/                  → MCTS, Pareto, oracles, LaTeX (JoC)
└── Project5_GNN_Transformer_DrugDiscovery/              → GNN/transformer pipelines, manuscript (V2608)
```

## Repository

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/NanaEngo/Malaria_codesV2 |
| Zenodo | 10.5281/zenodo.19608875 |

**Version:** V2608 (Aug 6, 2026)

## Data Analysis & Provenance

The canonical source of truth for project data, provenance, and analysis decisions:
- **P1–P3:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
- **P4:** `P4_DATA_ANALYSIS_REPORT.md`
- **P5:** `P5_DATA_ANALYSIS_REPORT.md`

Manuscript updates must follow the workflow: **raw data → data-analysis report → manuscript**.

## Results Location Note (2026-07-29)

The canonical results directories for the five projects are:
- **P1:** `/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/results/`
- **P2:** `/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/`
- **P3:** `/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/results/`
- **P4:** `/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607/results/`
- **P5:** `/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery/results/`

See the respective data-analysis reports for the full audit and SLURM correction plans.
