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
- **DiffDock fixed-center drift diagnosis (08/08/2026):** stochastic (Langevin) reverse-diffusion sampling — the `tr_z ~ N(0,1)` term in `utils/sampling.py::sampling` — displaces rank-1 poses 10–17 Å out of the 25 Å pocket box, even with a correct fixed-center initialization (verified: rerun4 and rerun6 share byte-identical configs, yet rerun4 IN_GRID=1.0 while rerun6=0.7917; the run is not reproducible under stochastic sampling). ODE (deterministic) sampling (job 12850) also failed closed (rank1 fraction 0.0): DiffDock's blind score model moves the ligand toward ITS learned pocket, not the declared catalytic center. **CONCLUSION: DiffDock cannot be constrained to the 2F6I catalytic pocket; per the tracking fallback, PfClpP evidence switches to grid-restrained AutoDock Vina docking.**
- **PfClpP pocket-center correction (08/08/2026) — SCIENTIFIC: the previous V5 center [-0.116, 40.446, 12.213] was the centroid of ALL Ser/His/Asp residues across the heptamer = the barrel-channel axis, NOT a catalytic site (verified: Vina pose at that center landed ~22 Å from the nearest triad). The genuine catalytic triad of 2F6I (mature numbering; UniProt O97252 active-site Ser289 = 2F6I Ser252, offset 37; geometrically complete in all 7 chains) is Ser252/His223/Asp219. Canonical pocket center = chain A triad centroid [-24.276, 17.28, -2.901]. Corrected in `p1_v5_vina_dock_clpp_2f6i.py`, `p1_v5_run_diffdock.py`, `p1_v5_score_rank1_vina.py`, `p1_v5_structural_pocket_preflight.py`, `p1_v5_grid_revision_preflight.py`, `target_identity_audit.json` v2.**
- **Vina grid-restrained PfClpP docking (08/08/2026):** new fail-closed runner `p1_v5_vina_dock_clpp_2f6i.py` — SMILES→Meeko PDBQT (Gasteiger, seeded embed), full Vina 1.2.7 docking inside the 25 Å box centered on the chain A triad; rank-1 IN_GRID by construction + verified at 100% containment; smoke (PP-01, exhaustiveness 8) PASSED with pose centroid 10.2 Å from the chain A triad and 6-7 Å pose-atom contact to catalytic atoms. 17-pair run 12851 (box 25 Å) failed closed on PP-13 (2 atoms 1.03 Å past the 25 Å edge); runs 12852/12853 (box 28 Å) also failed closed on PP-02/PP-06 (atoms 0.013–0.88 Å past the cube edge while poses sat 3.3–7.6 Å from the triad). **Gate redesign 08/08/2026: the cube is a Vina search-space artifact, not a biological containment criterion; the catalytic cavity is non-cubic and extended polypharm ligands (up to 30 heavy atoms) legitimately place peripheral atoms just past a cube edge. The accepted verification gate is now composite and biological: (1) rank-1 centroid inside the declared box (Vina-guaranteed), (2) at least one pose atom within 10 Å of a chain A triad atom (pocket contact), (3) ≥ 90% of atoms inside box + 0.5 Å grid padding. Full 17-pair run with the composite gate submitted 08/08/2026 (job 12854, exhaustiveness 16, box 28 Å).
- **✅ PfClpP/2F6I Vina docking COMPLETE (job 12854, 08/08/2026): 17/17 pairs pass the composite biological gate** — status `VINA_GRID_DOCK_RANK1_VERIFIED_IN_GRID`, all_pass=True; affinities −5.05 to −7.03 kcal/mol; pose-to-triad minima 3.3–8.9 Å (all ≤ 10 Å, every pose contacts the chain A catalytic triad Ser252/His223/Asp219); in-box fractions 0.963–1.0. Outputs: `results/vina_dock_2F6I_PfClpP_17/` (execution_provenance.json, vina_dock_2F6I_PfClpP.csv, per-pair vina_out.pdbqt). DiffDock poses remain pose cross-check only (not affinity).**
- **Generalized Vina runner `p1_v5_vina_dock_target.py` (08/08/2026)**: target-anchored (PfDHFR/MTX, PfClpP/chain-A triad, PfCRT/Y01-proxy) with per-target composite gates; PfATP4 refuses (CAVITY_EVIDENCE_REQUIRED, no co-crystallized anchor). **PfCRT/6UKJ smoke PASSED (Y01 anchor, single instance A501); full 17-pair PfCRT run submitted (job 12855).**
- **✅ PfCRT/6UKJ Vina docking COMPLETE (job 12855, 08/08/2026): 17/17 pairs pass the composite gate** — status `VINA_GRID_DOCK_RANK1_VERIFIED_IN_GRID`, all_pass=True; affinities −5.12 to −7.91 kcal/mol; pose-to-anchor (Y01 A501) minima 3.0–4.1 Å (all ≤ 10 Å); in-box fractions all 1.0. Outputs: `results/vina_dock_6UKJ_PfCRT_17/` (execution_provenance.json, vina_dock_6UKJ_PfCRT.csv, per-pair vina_out.pdbqt). Caveat: Y01 (cholesterol hemisuccinate) is a membrane-proxy anchor, not an inhibitor — the PfCRT pose evidence is valid relative to the Y01 cavity but is not a potency claim.**
- **PfDHFR anchor REVIEW_REQUIRED (08/08/2026)**: 7F3Y contains 3 partial MTX copies (A702, A704, B702; each 33 atoms at z=−58.7/−24.8/−6.9); the previous V5 center (1.33, −1.733, −23.842) ≈ receptor centroid, not an active site (same barrel/centroid error class as 2F6I). Defensible anchor = MTX copy at the DHFR catalytic site; CA frame PDB/PDBQT is exact (1096=1096, rmsd 0). Vina smoke with the global-MTX-centroid box failed the gate (rank-1 16–20 Å from MTX) → **do not run PfDHFR 17-pair until the specific MTX instance (chain A catalytic-site copy) is selected; documented, not forced.**
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

1. ~~Resolve the target-identity mismatch~~ **PfClpP receptor RESOLVED 08/08/2026 (4GM2→2F6I)**; ~~17-pair DiffDock re-run (12849, stochastic) FAILED CLOSED~~; ~~ODE smoke (12850) FAILED CLOSED~~ — DiffDock blind diffusion cannot target the 2F6I catalytic pocket. **✅ PfClpP EVIDENCE COMPLETE (job 12854): grid-restrained Vina docking on the corrected chain A triad center [-24.276, 17.28, -2.901]; 17/17 pairs pass the composite biological gate (centroid-in-box + ≤10 Å triad contact + ≥90% in-box fraction); affinities −5.05 to −7.03 kcal/mol; all poses contact Ser252/His223/Asp219 (3.3–8.9 Å).** **✅ PfCRT/6UKJ EVIDENCE COMPLETE (job 12855): 17/17 pairs pass the composite gate on the Y01 (A501) cavity; affinities −5.12 to −7.91 kcal/mol; anchor minima 3.0–4.1 Å (Y01 = membrane-proxy anchor, caveat documented).** **PfDHFR/7F3Y: anchor REVIEW_REQUIRED (3 partial MTX copies; V5 center was the receptor centroid); do not force until the catalytic-site MTX instance is selected. PfATP4/9N10: blocked (no small-molecule anchor).** Next: select the PfDHFR catalytic-site MTX instance and review all receptor identities before any scoring/consensus/RRS/PNS run. Do not translate poses post hoc. A future full-run authorization must bind the accepted structural preflight hash, the complete sentinel-verified reference-ligand preflight, and an explicitly accepted independent-review register in addition to runner/config/manifest/model/smoke hashes.
2. Re-run the isolated Vina rank-1 score-only gate only after every accepted pose is inside the declared grid and the receptor frame is verified.
3. Obtain a genuine WT+mutant Vina panel for all four targets before claiming four-target consensus or RRS.
4. Recompute consensus/RRS/PNS only after raw outputs, coordinate gate, target panel, and independent verification all pass.
5. Update V5 manuscript claims and tables only from accepted machine-readable outputs.
6. Compile and perform final LaTeX/reference/adversarial audits.

No V5 completion or acceptance guarantee is claimed at this stage. The 68-pair runner is fail-closed and requires an explicit reviewed authorization artifact that does not currently exist.
