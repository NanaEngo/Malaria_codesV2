# P2 — polypharmacology, RRS, and MD validation

**Status checkpoint (12 August 2026):** docking/RRS/ACSI/PNS analysis complete; Set-C candidate-specific MD-RRS pending.
**DAR:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
**Roadmap:** `P1_P5_RRS_POLYPHARMA_ROADMAP.md`

## Scientific design

- Canonical Set-C cohort: **17 polypharmacology-oriented candidates**.
- Docking panel: **136 WT/mutant systems** for PfDHFR and PfCRT.
- Per-target RRS excludes non-binding WT denominators (`|ΔG_WT| < 5.0 kcal mol⁻¹`).
- Canonical RRS classes: **A*:6, B:5, C:5, D:1**.
- ACSI mean: **0.543**; high-ACSI candidates: **2/17**.
- Cross-metric PNS–RRS: ρ=−0.559, p=0.020; not significant after Bonferroni correction.

The four historical parent-lead MD systems are a separate evidence stream, not Set-C validation. Only PfCRT–214 has an interpretable historical MM-GBSA estimate; the 4GM2-labelled system is not structural PfClpP validation because 4GM2 is PfClpR.

## Current Set-C MD status

The bounded pilot contains 16 prepared systems (PP-01/PP-02 × PfDHFR/PfCRT mutation states) using OpenFF 2.2.0 AM1-BCC ligand parameters with CHARMM36m/TIP3P. The policy deviation from CGenFF is explicit and PI-approved in the manifests.

- **15254:** isolated `PP-01_PfDHFR_WT` equilibration witness complete; `npt.gro`/`npt.cpt` hashed.
- **15259:** isolated witness production running toward 10 ns.
- **15260:** witness QC pending with `afterok:15259`.
- **Full-panel MD-RRS:** `NOT_COMPUTED` until complete trajectories pass QC.
- Legacy 15106/15111/15117 jobs are superseded.

## Canonical locations

- Main manuscript: `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex`
- Supporting Information: `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex`
- Docking/RRS/ACSI/PNS data: `results/`
- Set-C preparation and post-production runbooks: `results/set_c_md/`
- Integration plan: `scripts/P2_MD_RRS_INTEGRATION_PLAN.md` (historical plan; do not execute legacy commands)

## Evidence boundary

Docking-RRS is not MD-RRS. No candidate-specific MD claim enters the manuscript until trajectory hashes, PASS QC, the predeclared bound-fraction rule, and complete-panel provenance are available.
