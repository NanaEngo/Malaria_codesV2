# P1 V5 — Target-Anchored Computational Prioritization

## Scientific article package

The canonical V5 article is a standalone JCIM-style computational study:

- `manuscript/Antimalarial_Candidates_African_NP_V2608.tex` — main article
- `manuscript/Antimalarial_Candidates_African_NP_V2608_SM.tex` — Supporting Information
- `manuscript/Cover_Letter.tex` — aligned cover letter

The article evaluates a locked 17-member Set-C polypharmacology-oriented cohort against four *Plasmodium falciparum* targets using target-anchored AutoDock Vina docking: PfDHFR (7F3Y), PfCRT (6UKJ), PfClpP (2F6I), and PfATP4 (9N10). The raw matrix contains 68 candidate–target records.

## Scientific contribution

V5 tests whether target-specific pocket definitions provide a reproducible pose-prioritization layer for a chemically diverse cohort. It distinguishes:

- computational Vina score estimates from measured affinity;
- geometric pose admissibility from biological target engagement;
- four-target predicted profiles from RRS and experimental resistance resilience;
- PfClpP (2F6I) from the invalid historical PfClpR assignment (4GM2).

PfCRT is evaluated relative to a Y01-associated membrane/cavity proxy, and PfATP4 relative to conserved catalytic machinery because no co-crystallized small-molecule inhibitor is available in 9N10. These evidence classes are not equivalent and are stated in the article.

## Data and reproducibility

The machine-readable outputs are `results/v5_four_target_vina_affinities.csv` and `results/v5_four_target_vina_review_table.json`. Receptor and ligand files, configurations, raw poses, scripts, and provenance records are retained in the project tree. The independent structural-review register and automated integrity audit remain archival controls; they are not biological validation and are not used as manuscript results.

The historical V4 484-centroid PfClpP arm and the four parent MD systems are separate evidence streams. Neither is presented as validation of the V5 17-member cohort.

## Author-controlled pre-submission development

The project is under active scientific and manuscript development. The root phase switch `P1_DEVELOPMENT_PHASE.json` is `PRE_SUBMISSION_DEVELOPMENT`, with editorial submission restrictions inactive. Consensus, docking-RRS, PNS/ACSI exploratory analyses, sensitivity analyses, figures, and manuscript refinement may proceed without waiting for an independent-review signature. Outputs retain truthful provenance labels such as `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY`; the registers remain `PENDING_INDEPENDENT_REVIEW` and `accepted_for_full_run=false`.

This does not disable scientific QC: target identity, hashes, geometric gates, row counts, finite scores, receptor/frame integrity, and runtime/provenance checks remain active. A scientific failure must be investigated; it is not an editorial restriction. Submission does not switch the workflow automatically. Only the author’s explicit instruction that submission has occurred **and** that restrictions should be reactivated may activate the signed-review policy. See `P1_INTERNAL_DEVELOPMENT_POLICY.md`.
