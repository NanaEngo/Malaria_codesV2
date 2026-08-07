# P1 V5 — Project Tracking

## Status

- **Canonical tree:** `Project1_Chem_space_antimalarial_V5_CorrectedGrid/`
- **Parent baseline:** `Project1_Chem_space_antimalarial_V4_CorrectedGrid/`
- **Current phase:** V4→V5 controlled migration
- **Status:** `MIGRATION_IN_PROGRESS`
- **V4 protection:** V4 is not overwritten by the migration
- **V5 compilation:** pending; inherited PDFs quarantined and not release outputs
- **DiffDock input preflight:** SUPERSEDED/BLOCKED — the inherited 68-row manifest used 4GM2 under the PfClpP label; `results/target_identity_audit.json` records that 4GM2 is PfClpR, not PfClpP. No new manifest may be prepared until a genuine PfClpP structure is supplied.
- **DiffDock 68-pair execution:** inherited raw artifacts are retained for provenance only and are superseded/not accepted because the panel contains the 4GM2/PfClpP identity mismatch; no corrected DiffDock run has been launched.
- **Vina rank-1 gate:** BLOCKED — 10/68 rank-1 poses fully in the predeclared 25 Å grids, 14/68 partial, 44/68 outside; no arbitrary translation or box expansion permitted
- **RRS/PNS integration:** NOT UPDATED; consensus scores and four-target RRS/PNS remain uncomputed
- **Technical DiffDock smoke:** **FAILED CLOSED** in the final deterministic PP-01/PfDHFR fixed-center attempt: DiffDock produced readable outputs with zero internal failures/skips, but rank-1 containment was only 0.7916667 (79.17%) in the declared grid. Earlier smoke artifacts are superseded; no biological validation, Vina score, consensus, RRS, or PNS result is accepted.
- **Structural-pocket preflight:** `REVIEW_REQUIRED_NOT_AUTHORIZED` at `results/structural_pocket_preflight.json`; read-only inventory only, independent review `PENDING`, `accepted_for_full_run=false`. HETATM labels/centroids and historical V2 centers are not accepted as pocket validation. Target-specific evidence is documented in `results/structural_pocket_dossier.md`; PfDHFR is a candidate anchor requiring review, PfCRT Y01 remains a proxy, 4GM2 is confirmed as PfClpR rather than PfClpP (hard target-identity mismatch), and PfATP4 requires an independently supported cavity definition.
- **Reference-ligand preflight:** final rerun6 artifact is provenance-only and is superseded for the four-target panel after the target-identity audit. MTX instances and Y01 were coordinate-preserving inventory artifacts; Y01 remains an ambiguous proxy, MTX requires identity/site review, 4GM2 is PfClpR rather than PfClpP, and 9N10 has no small-molecule inhibitor anchor. No corrected DiffDock/Vina/GROMACS run was launched.
- **Independent structural review register:** `results/structural_pocket_independent_review.json` is `PENDING_INDEPENDENT_REVIEW`; all four target decisions are `PENDING`, `accepted_for_full_run=false`. It is intentionally not a biological acceptance artifact. The full runner requires this register to become explicitly accepted for every target before any future authorization can pass.

## Canonical V5 sources

- `manuscript/Antimalarial_Candidates_African_NP_V2608.tex`
- `manuscript/Antimalarial_Candidates_African_NP_V2608_SM.tex`
- `manuscript/Cover_Letter.tex`

## Cohort boundary

The proposed DiffDock task concerns P2 Set C (17 polypharmacology candidates × 4 targets). It must not be confused with:

- P1 Set A: MPO top-20 candidates;
- P2 Set B: parent-study MD candidates;
- P2 Set C: polypharmacology candidates;
- parent MD leads: 201-PfDHFR, 438-PfATP4, 164-PfClpP, and 214-PfCRT.

## Completed migration actions

- Full controlled copy made from V4 to V5.
- Inherited V4/P1 PDFs moved to `manuscript/provenance/inherited_pdfs/` and inherited V4 audit/preflight JSON moved to `results/provenance/inherited_v4/`; all are labelled as provenance-only.
- Migration-status notices added to the V5 main, SM, and cover-letter sources; no scientific result was changed.
- Generated LaTeX caches/logs and Python cache files excluded.
- Main and SM sources renamed from V2607 to V2608 in V5 only.
- Main/SM external-document references updated to V2608.
- V4 hashes and migration metadata recorded in `results/v5_migration_manifest.json`.

## Completed preparation and raw-output gates

- Canonical Set-C CSV verified: 17 unique valid SMILES.
- Four target PDBs verified non-empty and hashed.
- Local DiffDock environment inspected read-only: CUDA visible, pinned source/checkpoints present.
- Deterministic 68-pair input manifest generated with PP-01–PP-17 IDs.
- Generator, source tree, model/checkpoint, configuration, normalization-array, and sentinel hashes recorded.
- Raw DiffDock execution produced 68/68 rank-1 pose SDFs and 68/68 readable rank-1 confidence SDFs.
- Independent audit `results/diffdock_full_68_verified/independent_rank1_audit.csv` validates all rank-1 records and records 10 IN_GRID, 14 PARTIAL_GRID, and 44 OUTSIDE_GRID poses.
- Secondary confidence audit covers 612 files and derives 11 invalid secondary poses; these are excluded from ensemble claims.
- DiffDock confidence is retained as a pose-quality score, never converted to affinity or combined with Vina.

## Structural dossier decision (7 August 2026)

The target-specific dossier at `results/structural_pocket_dossier.md` records evidence-bounded decisions from RCSB entries 7F3Y, 6UKJ, 4GM2, and 9N10. It is not a biological acceptance or run authorization. No target is promoted automatically from a HETATM centroid or historical grid center. The required sequence is target-specific review → exact receptor-frame check → single-pair exact-config smoke → independent signed review → cryptographically bound authorization. If PfCRT, PfClpP, or PfATP4 cannot be justified, they must be excluded from the primary V5 claim rather than forced into a four-target panel.

## Pending gates

1. Resolve the target-identity and DiffDock/Vina coordinate-frame/pocket-definition mismatches: replace 4GM2 with a verified PfClpP receptor, then use a target-specific pocket-aware rerun or formally justified receptor/grid revision; the final fixed-center smoke failed closed at rank1 inside_fraction=0.7916667. Do not translate poses post hoc. A future full-run authorization must bind the accepted structural preflight hash, the complete sentinel-verified reference-ligand preflight, and an explicitly accepted independent-review register in addition to runner/config/manifest/model/smoke hashes.
2. Re-run the isolated Vina rank-1 score-only gate only after every accepted pose is inside the declared grid and the receptor frame is verified.
3. Obtain a genuine WT+mutant Vina panel for all four targets before claiming four-target consensus or RRS.
4. Recompute consensus/RRS/PNS only after raw outputs, coordinate gate, target panel, and independent verification all pass.
5. Update V5 manuscript claims and tables only from accepted machine-readable outputs.
6. Compile and perform final LaTeX/reference/adversarial audits.

No V5 completion or acceptance guarantee is claimed at this stage. The 68-pair runner is fail-closed and requires an explicit reviewed authorization artifact that does not currently exist.
