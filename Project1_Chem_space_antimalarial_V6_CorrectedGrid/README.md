# P1 V6 — Integrated Chemical-Space, Polypharmacology, and Resistance-Resilience Study

**Status:** `SCIENTIFIC_MANUSCRIPT_DRAFT — EVIDENCE_INTEGRITY_PASS_PENDING_INDEPENDENT_REVIEW`

**Article sources:** `manuscript/P1_V6_Integrated_Polypharmacology_RRS.tex`, `manuscript/P1_V6_Integrated_Polypharmacology_RRS_SM.tex`, and `manuscript/Cover_Letter_P1_V6.tex`. These are the scientific article files; registers, audits, and HPC tracking remain archival controls and are not manuscript prose. The article package is written as IMRAD-style research prose rather than as a project report.

**Purpose:** V6 is a new, independent publication workspace. It combines the V4 chemical-space/MPO funnel, the corrected V5 target-anchored Vina panel, and the corrected P2 per-target RRS/polypharmacology analysis without overwriting V4 or V5.

## Scientific scope

V6 is a computational, hypothesis-generating study. Its primary claim is the identification and prioritization of African-natural-product-inspired candidates with predicted multi-target profiles and an in-silico resistance-resilience profile. V6 does **not** claim experimental inhibition, measured IC50/EC50, binding kinetics, or demonstrated resistance circumvention.

## Locked evidence boundaries

1. **V4 chemical-space evidence:** library construction, novelty/scaffold analysis, drug-likeness, MPO funnel, and the original 484-centroid reduction. V4 is retained as the upstream chemical-space analysis; its candidate sets are not silently relabelled.
2. **V5 docking evidence:** the locked 17-candidate polypharmacology cohort is evaluated against four targets: PfDHFR (7F3Y), PfCRT (6UKJ), PfClpP (2F6I), and PfATP4 (9N10). The 17×4 Vina table is complete raw, target-anchored evidence (68/68 composite-gate records), but remains pending independent review. Candidate identity is verified row-wise by the V6 source-bound manifest using canonical SMILES against the V5 68-row manifest and P2 source.
3. **RRS evidence:** an exploratory score-ratio statistic is evaluated per target on PfDHFR mutants (N51I, C59R, S108N, I164L) and PfCRT mutants (K76T, K76A). It uses docking-score magnitudes, not free-energy differences. No PfClpP/PfATP4 RRS claim is made without a declared mutant panel.
4. **Polypharmacology:** a four-target docking profile reported target by target; no arithmetic cross-target score is used because Vina scores are not calibrated across unlike pockets. RRS is a two-target mutation analysis. These scopes are complementary, not interchangeable.
5. **Historical MD:** the four parent systems (201, 438, 164, 214) remain a separate parent-study MD cohort. They are not presented as MD validation of the 17-candidate RRS/polypharmacology cohort.

## Target identity and anchor policy

- `2F6I` is the PfClpP structure used for V6. `4GM2` is PfClpR and is excluded from PfClpP claims.
- PfDHFR uses the MTX A702 catalytic-site copy in 7F3Y.
- PfCRT uses the Y01-associated cavity in 6UKJ; Y01 is a membrane/cavity proxy, not an inhibitor claim.
- PfATP4 uses a catalytically motivated P-type ATPase region around D451/DPPR because 9N10 has no co-crystallized small-molecule inhibitor.

## Publication positioning

The V6 manuscript is written as an IMRAD-style computational research article, not as a project report. Its central scientific distinction is between (i) four-target predicted polypharmacology, (ii) per-target mutation-aware RRS, and (iii) experimental activity, which is not measured here. The article reports the corrected null findings and the evidence classes of the PfDHFR, PfCRT, PfClpP, and PfATP4 anchors.

V6 may be submitted as a computational JCIM-style study or to a related computational drug-discovery journal without new wet-lab experiments, provided that the manuscript:

- calls docking scores and RRS values computational estimates, not experimental affinities;
- reports the negative and non-significant findings;
- separates target-specific RRS from four-target polypharmacology;
- distinguishes positive-control/retrodictive analyses from independent decoy validation;
- provides reproducible code, structures, configurations, hashes, and data-access statements;
- never presents the independent-review gate as passed unless a qualified human reviewer signs it.

## V4 484-centroid 2F6I replacement boundary

The historical V4 484-centroid PfClpP arm is a separate panel and is not replaced by the V5 17×4 candidate table. Its uniform 2F6I revalidation is running in the V4 tree under SLURM job `13451`; merge `13452` is `afterok`, and audit `13972` is `afterany`. The uniform array produced all 484 centroid directories, but fail-closed audit `13972` rejected the panel: 449 records independently passed raw Vina checks and 35 records contain explicit worker failures. No aggregate CSV or downstream promotion was produced. The 449 successes are diagnostic only. V6 must not use this panel to replace the V4 evidence until all 35 failures are resolved, the complete panel is independently re-audited, and the structural review is signed.

## Fail-closed review policy

The V6 pipeline has two independent states:

- `EVIDENCE_INTEGRITY_PASS`: automated checks confirm completeness, hashes, identities, cohort consistency, and schema integrity.
- `INDEPENDENT_REVIEW_ACCEPTED`: only a qualified human reviewer may set this state by signing the review dossier through the documented signature protocol.

An automated script may produce the first state but must never create the second. The current candidate mapping satisfies the automated row-wise molecular-key check; this does not constitute independent structural review or biological validation. The exploratory RRS analysis is computed independently from the declared PfDHFR and PfCRT mutant source panel and may be reported with explicit computational and non-acceptance qualifiers. Independent structural review gates acceptance or promotion of the V5 four-target docking panel and any accepted V5--RRS/PNS integration; it does not constitute validation of the RRS mutant panel or experimental validation. Until the register is independently signed, V6 results must therefore remain labeled exploratory/source-panel RRS and raw target-profile evidence, not independently accepted integrated evidence.

## Directory map

- `docs/` — roadmap, claim boundaries, review protocol
- `evidence/` — immutable references/snapshots and hash manifests
- `results/` — V6-derived outputs only
- `scripts/` — deterministic validation and downstream analysis scripts
- `manuscript/` — V6 main, supporting information, and cover letter
- `logs/` — validation and HPC logs
