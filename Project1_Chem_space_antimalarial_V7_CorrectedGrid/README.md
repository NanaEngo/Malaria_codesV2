# P1 V7 — Integrated Chemical-Space, Polypharmacology, and Resistance-Resilience Study

**Status:** `SCIENTIFIC_MANUSCRIPT_DRAFT — EVIDENCE_INTEGRITY_PASS_PENDING_INDEPENDENT_REVIEW`

**Article sources:** `manuscript/P1_V7_Integrated_Polypharmacology_RRS.tex`, `manuscript/P1_V7_Integrated_Polypharmacology_RRS_SM.tex`, and `manuscript/Cover_Letter_P1_V7.tex`. These are the scientific article files; registers, audits, and HPC tracking remain archival controls and are not manuscript prose. The article package is written as IMRAD-style research prose rather than as a project report.

**Purpose:** V7 is a new, independent publication workspace. It combines the V4 chemical-space/MPO funnel, the corrected V5 target-anchored Vina panel, and the corrected P2 per-target RRS/polypharmacology analysis without overwriting V4 or V5.

## Scientific scope

V7 is a computational, hypothesis-generating study. Its primary claim is the identification and prioritization of African-natural-product-inspired candidates with predicted multi-target profiles and an in-silico resistance-resilience profile. V7 does **not** claim experimental inhibition, measured IC50/EC50, binding kinetics, or demonstrated resistance circumvention.

## Locked evidence boundaries

1. **V4 chemical-space evidence:** library construction, novelty/scaffold analysis, drug-likeness, MPO funnel, and the original 484-centroid reduction. V4 is retained as the upstream chemical-space analysis; its candidate sets are not silently relabelled.
2. **V5 docking evidence:** the locked 17-candidate polypharmacology cohort is evaluated against four targets: PfDHFR (7F3Y), PfCRT (6UKJ), PfClpP (2F6I), and PfATP4 (9N10). The 17×4 Vina table is complete raw, target-anchored evidence (68/68 records passed the automated geometric gate); the raw poses remain subject to independent structural review and are not treated as experimental validation. Candidate identity is verified row-wise by the V7 source-bound manifest using canonical SMILES against the V5 68-row manifest and P2 source.
3. **RRS evidence:** an exploratory score-ratio statistic is evaluated per target from the separate `docking_mutants.csv` WT/mutant panel on PfDHFR mutants (N51I, C59R, S108N, I164L) and PfCRT mutants (K76T, K76A). It uses docking-score magnitudes, not free-energy differences, and is not derived from the four-target V5 WT matrix. No PfClpP/PfATP4 RRS claim is made without a declared mutant panel.
4. **Polypharmacology:** a four-target docking profile reported target by target; no arithmetic cross-target score is used because Vina scores are not calibrated across unlike pockets. RRS is a two-target mutation analysis. These scopes are complementary, not interchangeable.
5. **Historical MD:** the four parent systems (201, 438, 164, 214) remain a separate parent-study MD cohort. They are not presented as MD validation of the 17-candidate RRS/polypharmacology cohort.

## Target identity and anchor policy

- `2F6I` is the PfClpP structure used for V7. `4GM2` is PfClpR and is excluded from PfClpP claims.
- PfDHFR uses the MTX A702 catalytic-site copy in 7F3Y.
- PfCRT uses the Y01-associated cavity in 6UKJ; Y01 is a membrane/cavity proxy, not an inhibitor claim.
- PfATP4 uses a catalytically motivated P-type ATPase region around D451/DPPR because 9N10 has no co-crystallized small-molecule inhibitor.

## Publication positioning

The V7 manuscript is written as an IMRAD-style computational research article, not as a project report. Its central scientific distinction is between (i) four-target predicted polypharmacology, (ii) per-target mutation-aware RRS, and (iii) experimental activity, which is not measured here. The article reports the corrected null findings and the evidence classes of the PfDHFR, PfCRT, PfClpP, and PfATP4 anchors. The integrated audit found no file, schema, cohort, or RRS-recomputation errors; independent structural review remains a separate scientific control.

V7 may be submitted as a computational JCIM-style study or to a related computational drug-discovery journal without new wet-lab experiments, provided that the manuscript:

- calls docking scores and RRS values computational estimates, not experimental affinities;
- reports the negative and non-significant findings;
- separates target-specific RRS from four-target polypharmacology;
- distinguishes positive-control/retrodictive analyses from independent decoy validation;
- provides reproducible code, structures, configurations, hashes, and data-access statements;
- never presents the independent-review gate as passed unless a qualified human reviewer signs it.

## V4 484-centroid 2F6I replacement boundary

The historical V4 484-centroid PfClpP arm is a separate panel and is not replaced by the V5 17×4 candidate table. Its uniform 2F6I revalidation (`13451`), rescue (`13478`), and associated merge/audit jobs (`13452`, `13479`, `13972`) have no active scheduler entry in the current query; final accounting states are not recoverable from that query. The uniform array produced all 484 centroid directories, but fail-closed audit `13972` rejected the panel: 449 records independently passed raw Vina checks and 35 records contain explicit worker failures. No aggregate replacement panel was promoted. The 449 successes are diagnostic only. V7 must not use this panel to replace the V4 evidence until the 35 failures are resolved, the complete panel is independently re-audited, and a V4-specific independent-review artifact is completed. The V7 four-target register covers only the V5 17×4 evidence and is not a substitute.

## Evidence integrity and author-controlled workflow

The V7 pipeline distinguishes scientific integrity from editorial status:

- `EVIDENCE_INTEGRITY_PASS`: automated checks confirm completeness, hashes, identities, cohort consistency, and schema integrity.
- `INDEPENDENT_REVIEW_ACCEPTED`: a qualified human reviewer may later create this status through the documented signature protocol.
- `PENDING_INDEPENDENT_REVIEW`: truthful provenance while work is ongoing; it does not block scientific development.

Automated scripts must never fabricate independent acceptance. During the current author-controlled `PRE_SUBMISSION_DEVELOPMENT` phase, exploratory RRS/ACSI/PNS integration, figures, reruns, and manuscript refinement may proceed without a signature. Outputs remain explicitly labeled `NOT_SUBMISSION_READY` or exploratory, so the scientific record is not misrepresented. The candidate mapping, raw target-wise Vina evidence, and RRS source panel retain their existing technical and biological caveats.

Scientific QC remains active at all times: target identity, hashes, frame equivalence, cohort identity, schema integrity, finite scores, and runtime/provenance checks. These are quality controls, not editorial restrictions. Submission does not automatically switch the workflow. Only the author’s explicit confirmation that submission has occurred **and** explicit request to reactivate restrictions may activate the signed-review gate for submission-facing promotion. The detailed policy is recorded in `P1_INTERNAL_DEVELOPMENT_POLICY.md`.

## Directory map

- `docs/` — roadmap, claim boundaries, review protocol
- `evidence/` — immutable references/snapshots and hash manifests
- `results/` — V7-derived outputs only
- `scripts/` — deterministic validation and downstream analysis scripts
- `manuscript/` — V7 main, supporting information, and cover letter
- `logs/` — validation and HPC logs
