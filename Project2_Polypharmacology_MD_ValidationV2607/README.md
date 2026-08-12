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

- **15259/15260:** CPU witness and dependent QC were stopped after a partial 858-ps trajectory; the output is non-canonical.
- **15262:** mixed GPU/CPU benchmark passed at 19.816 ns/day without fatal or LINCS errors.
- **15270:** clean GPU witness is running from equilibrated inputs; `grompp` passed and GPU offload is active.
- **Pilot MD-RRS contract:** `PP-01/PP-02` × 8 states = 16 QC rows; use `--cohort-mode pilot`, which writes `results/set_c_md/md_rrs_pilot_PP01_PP02.csv` and cannot overwrite the full-cohort output.
- **Full-panel MD-RRS:** `NOT_COMPUTED`; the separate full contract requires 17 candidates × 8 states = 136 PASS-QC rows.
- **PlasmoDB annotation:** stable target IDs and mutation context are recorded in `results/plasmodb_target_annotation.csv` and SM Table S7; no pathway enrichment is claimed. PlasmoDB record retrieval is evidenced, but no directly scripted WDK REST client is currently part of the workflow.
- **GitHub tool register:** verified current/available applications, effective-use evidence, licenses, and integration priorities are recorded in `P2_GITHUB_TOOL_REGISTER_20260812.md`.
- **GNINA status:** executable available (`v1.3.2`), but the preserved ligand-438 attempt produced an empty output file (0 bytes); therefore no GNINA score or pose is reportable for P2. The generalized 17 × 4 consensus claim is withdrawn pending a new complete, non-empty manifest.
- Legacy 15106/15111/15117 jobs are superseded.

## Canonical locations

- Main manuscript: `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex`
- Supporting Information: `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex`
- Docking/RRS/ACSI/PNS data: `results/`
- Set-C preparation and post-production runbooks: `results/set_c_md/`
- Integration plan: `scripts/P2_MD_RRS_INTEGRATION_PLAN.md` (historical plan; do not execute legacy commands)

## Evidence boundary

Docking-RRS is not MD-RRS. No candidate-specific MD claim enters the manuscript until trajectory hashes, PASS QC, the predeclared bound-fraction rule, and complete-panel provenance are available.
