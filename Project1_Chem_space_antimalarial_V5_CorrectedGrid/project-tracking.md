# P1 V5 — Project Tracking

## Status

- **Canonical tree:** `Project1_Chem_space_antimalarial_V5_CorrectedGrid/`
- **Parent baseline:** `Project1_Chem_space_antimalarial_V4_CorrectedGrid/`
- **Current phase:** V4→V5 controlled migration
- **Status:** `MIGRATION_IN_PROGRESS`
- **V4 protection:** V4 is not overwritten by the migration
- **V5 compilation:** pending; inherited PDFs quarantined and not release outputs
- **DiffDock input preflight:** **CORRECTED 08/08/2026** — the inherited 68-row manifest used 4GM2 under the PfClpP label (4GM2 is PfClpR, UniProt Q8IL98). The genuine PfClpP receptor **2F6I** (EC 3.4.21.92, UniProt O97252, "ClpP protease catalytic domain from Plasmodium falciparum", 2.45 Å, El Bakkouri 2010) was downloaded and prepared as receptor PDBQT; the 17 PfClpP manifest rows were corrected to 2F6I (legacy manifest backed up as `diffdock_input_manifest_4GM2_legacy.csv`); scripts `p1_v5_grid_revision_preflight.py`, `p1_v5_score_rank1_vina.py`, `p1_v5_run_diffdock.py`, `p1_v5_structural_pocket_preflight.py` updated to 2F6I with pocket center [-0.116, 40.446, 12.213] (catalytic-residue centroid in the 2F6I frame; the old 4GM2 center is NOT transferable).
- **DiffDock 68-pair execution:** inherited raw artifacts are retained for provenance only and are superseded/not accepted because the panel contains the 4GM2/PfClpP identity mismatch. **Corrected PfClpP re-run submitted 08/08/2026 (job 12849)** via `p1_v5_run_diffdock_clpp_2f6i.py` + `p1_v5_diffdock_2f6i_clpp.sbatch` — 17 PfClpP pairs re-docked against 2F6I with fixed pocket center; CA frame equivalence verified (PDBQT is a coordinate-identical CA subset of the PDB, rmsd=0; 74 incomplete-side-chain residues absent but frame unchanged).
- **Vina rank-1 gate:** BLOCKED — 10/68 rank-1 poses fully in the predeclared 25 Å grids, 14/68 partial, 44/68 outside; no arbitrary translation or box expansion permitted. **PfClpP poses from the old 4GM2 run are unusable (different frame) and will be replaced by the 2F6I re-run (job 12849) before the Vina score-only gate is re-evaluated.**
- **RRS/PNS integration:** NOT UPDATED; consensus scores and four-target RRS/PNS remain uncomputed
- **Technical DiffDock smoke:** **FAILED CLOSED** in the final deterministic PP-01/PfDHFR fixed-center attempt: DiffDock produced readable outputs with zero internal failures/skips, but rank-1 containment was only 0.7916667 (79.17%) in the declared grid. Earlier smoke artifacts are superseded; no biological validation, Vina score, consensus, RRS, or PNS result is accepted.
- **DiffDock fixed-center drift diagnosis (08/08/2026):** stochastic (Langevin) reverse-diffusion sampling — the `tr_z ~ N(0,1)` term in `utils/sampling.py::sampling` — displaces rank-1 poses 10–17 Å out of the 25 Å pocket box, even with a correct fixed-center initialization (verified: rerun4 and rerun6 share byte-identical configs, yet rerun4 IN_GRID=1.0 while rerun6=0.7917; the run is not reproducible under stochastic sampling). **Fix: ODE (deterministic, score-guided) sampling** (`ode: true` → `tr_perturb = 0.5·tr_g²·dt·tr_score`, no stochastic term). Implemented in `p1_v5_run_diffdock_clpp_2f6i.py` as `--no-ode` opt-out (ODE is the default) + `--limit-pairs N` smoke mode; **ODE smoke for PP-01/PfClpP submitted 08/08/2026 (job 12850)**. If ODE containment passes 100%, the 17-pair ODE run is the accepted PfClpP evidence path; if ODE also drifts, PfClpP docking falls back to grid-restrained Vina-only docking (classical, fully controllable) with DiffDock kept as pose cross-check only.
- **Structural-pocket preflight:** `REVIEW_REQUIRED_NOT_AUTHORIZED` at `results/structural_pocket_preflight.json`; read-only inventory only, independent review `PENDING`, `accepted_for_full_run=false`. HETATM labels/centroids and historical V2 centers are not accepted as pocket validation. Target-specific evidence is documented in `results/structural_pocket_dossier.md`; PfDHFR is a candidate anchor requiring review, PfCRT Y01 remains a proxy, **PfClpP receptor corrected to 2F6I (evidence class now CATALYTIC_TRIAD_REVIEW_REQUIRED instead of TARGET_IDENTITY_MISMATCH_BLOCKED; see `results/target_identity_audit.json` v2)**, and PfATP4 requires an independently supported cavity definition.
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
- Inherited, superseded, provenance-only DiffDock artifacts contain 68/68 readable rank-1 pose SDFs and 68/68 readable rank-1 confidence SDFs; these are not accepted V5 evidence.
- Independent audit `results/diffdock_full_68_verified/independent_rank1_audit.csv` validates all rank-1 records and records 10 IN_GRID, 14 PARTIAL_GRID, and 44 OUTSIDE_GRID poses.
- Secondary confidence audit covers 612 files and derives 11 invalid secondary poses; these are excluded from ensemble claims.
- DiffDock confidence is retained as a pose-quality score, never converted to affinity or combined with Vina.

## Structural dossier decision (7 August 2026)

The target-specific dossier at `results/structural_pocket_dossier.md` records evidence-bounded decisions from RCSB entries 7F3Y, 6UKJ, 4GM2, and 9N10. It is not a biological acceptance or run authorization. No target is promoted automatically from a HETATM centroid or historical grid center. The required sequence is target-specific review → exact receptor-frame check → single-pair exact-config smoke → independent signed review → cryptographically bound authorization. If PfCRT, PfClpP, or PfATP4 cannot be justified, they must be excluded from the primary V5 claim rather than forced into a four-target panel.

## Pending gates

1. ~~Resolve the target-identity mismatch~~ **PfClpP receptor RESOLVED 08/08/2026 (4GM2→2F6I)**; corrected 17-pair PfClpP DiffDock re-run running (job 12849, stochastic — FAILED CLOSED on PP-01 rank1 outside grid). **ODE deterministic re-run in progress (job 12850 smoke → then 17-pair ODE)**: stochastic Langevin noise drifted poses 10–17 Å out of the pocket; ODE mode removes the stochastic term so the ligand refines in place at the declared catalytic center. After ODE completion, verify rank-1 IN_GRID containment in the 2F6I pocket box (must achieve 100% IN_GRID per pair). Do not translate poses post hoc. A future full-run authorization must bind the accepted structural preflight hash, the complete sentinel-verified reference-ligand preflight, and an explicitly accepted independent-review register in addition to runner/config/manifest/model/smoke hashes.
2. Re-run the isolated Vina rank-1 score-only gate only after every accepted pose is inside the declared grid and the receptor frame is verified.
3. Obtain a genuine WT+mutant Vina panel for all four targets before claiming four-target consensus or RRS.
4. Recompute consensus/RRS/PNS only after raw outputs, coordinate gate, target panel, and independent verification all pass.
5. Update V5 manuscript claims and tables only from accepted machine-readable outputs.
6. Compile and perform final LaTeX/reference/adversarial audits.

No V5 completion or acceptance guarantee is claimed at this stage. The 68-pair runner is fail-closed and requires an explicit reviewed authorization artifact that does not currently exist.
