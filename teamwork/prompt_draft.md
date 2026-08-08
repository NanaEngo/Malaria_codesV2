# Teamwork Project Prompt — Draft

> Status: Launched — delegated to teamwork_preview (Auto-Approved Mode)
> Goal: Execute Option B (DiffDock RRS/Polypharm) on HPC and generate Paper 1 V5 manuscript autonomously

Apply DiffDock consensus rescoring (Option B) to P2 Set-C Polypharmacology candidates (17 compounds) across 4 Pf targets (PfDHFR, PfCRT, PfClpP, PfATP4) on HPC GPU to strengthen RRS and Polypharmacology analysis, then create the finalized V5 manuscript for Paper 1 ready for submission.

Working directory: /home/taamangtchu/Documents/Github/Malaria_codesV2

## Requirements

### R1. DiffDock Rescoring Execution on HPC
Execute GPU-accelerated DiffDock inference (`inference.py`) directly on HPC (`nanaengo@100.73.21.40`) for all 17 Set-C polypharmacology candidates across 4 targets (7F3Y, 6UKJ, 4GM2, 9N10). Compute geometric confidence scores and dual Vina+DiffDock consensus scores.

### R2. Polypharmacology & RRS Integration on HPC
Integrate the dual-consensus scores into P2 polypharmacology tables (`c_rrs_classification.csv`, `c_pns_ranking.csv`) directly on HPC, verifying that multi-target binders remain robust without single-docking artifacts.

### R3. Paper 1 V5 Manuscript Finalization on HPC (Target: 95%+ Acceptance Rate)
Update Paper 1 LaTeX files (`Antimalarial_Candidates_African_NP_V2607.tex` → `V2608` / `V5`) on HPC, incorporate the DiffDock consensus polypharmacology context, ensure 100% clean compilation on HPC (0 errors, 0 warnings, 0 missing citations), and produce the submission-ready package (Main + SM + Cover Letter) designed to meet a 95%+ peer-review acceptance probability.

## Acceptance Criteria

### Execution & Integration
- [ ] DiffDock confidence scores calculated for 17 candidates × 4 targets = 68 pairs on HPC GPU without errors.
- [ ] Results saved in `Project2_Polypharmacology_MD_ValidationV2607/results/p2_diffdock_polypharm_scores.csv`.
- [ ] RRS classification and polypharmacology tables updated with dual-consensus metrics.

### Manuscript V5 (95%+ Quality Standard)
- [ ] Paper 1 LaTeX V5 compiled cleanly into PDF (Main + SM + Cover Letter) on HPC.
- [ ] All references, figures, and tables fully resolved with 0 undefined citations or missing metrics.
- [ ] 95%+ peer-review quality bar verified (uncompromising evidence traceability, honest reporting of DEKOIS baseline & MMV consensus, complete S21/ADMET/CYP3A4 audit mitigations).
