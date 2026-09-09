# P2 — polypharmacology, RRS, and MD triage (V2609)

**Status checkpoint (30 August 2026):** docking/RRS/ACSI/PNS analysis complete; Set-C pilot COMPLETE (16/16 trajectories PASS-QC); post-production chain COMPLETE (manifest v3, qc_exit_code=0, md_rrs_exit_code=0); pilot MD-RRS COMPUTED_WITH_COHORT_CONTRACT (PP-01/PP-02 → Class A over PfCRT;PfDHFR); Set-C MM-GBSA computed 16/16. Full-panel (17×8=136-row) MD-RRS remains NOT_COMPUTED by design. The V2609 LaTeX release is maintained separately from the immutable V2607 source files. The current manuscript framing is computational triage and interpretation calibration, not biological validation. See `docs/P2_V2609_IMPLEMENTATION_PLAN.md`, `docs/P2_V2609_NARRATIVE_PIVOT_PLAN.md`, and `docs/P2_V2609_MD_AUDIT_MATRIX.md`.

**Roadmap:** `P1_P5_RRS_POLYPHARMA_ROADMAP.md`

## Scientific design

- Canonical Set-C cohort: **17 polypharmacology-oriented candidates**.
- Docking panel: **136 WT/mutant systems** for PfDHFR and PfCRT.
- Per-target RRS excludes non-binding WT denominators (`|ΔG_WT| < 5.0 kcal mol⁻¹`).
- Canonical target-balanced RRS classes: **A*:1, A:1, B:4, C:5, D:1** (12 complete two-target candidates); available-target sensitivity classes: **A*:5, A:1, B:5, C:5, D:1** (17 candidates).
- ACSI mean: **0.543**; high-ACSI candidates: **2/17**.
- Primary target-balanced PNS–RRS: ρ=−0.2098, permutation p=0.5144, Bonferroni-adjusted p=1.0000 (n=12); the 17-candidate coverage-sensitive estimate is ρ=−0.5588, adjusted p=0.0667.

The four historical parent-lead MD systems are a separate evidence stream, not Set-C validation. Only PfCRT–214 has an interpretable historical MM-GBSA estimate; the 4GM2-labelled system is not structural PfClpP validation because 4GM2 is PfClpR.

## Current Set-C MD status

The bounded pilot contains 16 prepared systems (PP-01/PP-02 × PfDHFR/PfCRT mutation states) using OpenFF 2.2.0 AM1-BCC ligand parameters with CHARMM36m/TIP3P. The policy deviation from CGenFF is explicit and PI-approved in the manifests.

- **15259/15260:** CPU witness and dependent QC were stopped after a partial 858-ps trajectory; the output is non-canonical.
- **15262:** mixed GPU/CPU benchmark passed at 19.816 ns/day without fatal or LINCS errors.
- **15270:** clean GPU witness completed one 10-ns trajectory; it is stability evidence only.
- **15319/15320:** final gate passed 16/16; production `15320` completed all 16 serial runs at exactly 5,000,000 steps / 10 ns with GPU PP/PME offload. The previous failed launchers remain non-canonical; the authoritative post-production chain subsequently passed QC for all 16 trajectories and produced the bounded pilot MD-RRS output.
- **Pilot MD-RRS contract:** `PP-01/PP-02` × 8 states = 16 QC rows; use `--cohort-mode pilot`, which writes `results/set_c_md/md_rrs_pilot_PP01_PP02.csv` and cannot overwrite the full-cohort output. Aggregate QC passed for all 16 terminal trajectories (authority wrapper output 15386; failed attempts p2_setc_qc_rrs_15384/15385 are superseded).
- **Full-panel MD-RRS:** `NOT_COMPUTED`; the separate full contract requires 17 candidates × 8 states = 136 PASS-QC rows.
- **PlasmoDB annotation:** stable target IDs and mutation context are recorded in `results/plasmodb_target_annotation.csv` and SM Table S7; no pathway enrichment is claimed. PlasmoDB record retrieval is evidenced, but no directly scripted WDK REST client is currently part of the workflow.
- **GitHub tool register:** verified current/available applications, effective-use evidence, licenses, and integration priorities are recorded in `P2_GITHUB_TOOL_REGISTER_20260812.md`.
- **GNINA status:** executable available (`v1.3.2`), but the preserved ligand-438 attempt produced an empty output file (0 bytes); therefore no GNINA score or pose is reportable for P2. The generalized 17 × 4 consensus claim is withdrawn pending a new complete, non-empty manifest.
- Legacy 15106/15111/15117 jobs are superseded.
- **Cleanup audit (13 August):** failed run directories, 1,087 autosave/backup files (~13.7 GB), and ten untracked Antechamber/SQM/energy temporary files were removed after reference-safety checks. Exact diagnostic duplicates and the legacy `results/md_systems/set_c` root were retained because historical scripts reference them. Active production and canonical evidence are protected.

## Canonical locations

- Immutable V2607 source manuscript (archived): `_archives/V2607_manuscript/Polypharmacology_MD_Validation_V2607.tex`
- Active V2609 main manuscript: `manuscript/LaTeX/Polypharmacology_MD_Validation_V2609.tex`
- Active V2609 Supporting Information: `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2609.tex`
- Active V2609 cover letter: `manuscript/LaTeX/Cover_Letter_V2609.tex`
- Docking/RRS/ACSI/PNS data: `results/`
- Set-C preparation and post-production runbooks: `results/set_c_md/`
- Implementation plan: `docs/P2_V2609_IMPLEMENTATION_PLAN.md`
- Narrative pivot: `docs/P2_V2609_NARRATIVE_PIVOT_PLAN.md`
- Markdown audit matrix: `docs/P2_V2609_MD_AUDIT_MATRIX.md`

## Evidence boundary

Docking-RRS is not MD-RRS. The bounded PP-01/PP-02 pilot MD-RRS is reportable only within its declared pilot contract because trajectory hashes, PASS QC, the predeclared rule, and cohort provenance are complete. The full 17-candidate MD-RRS remains not computed and is not claimed.
