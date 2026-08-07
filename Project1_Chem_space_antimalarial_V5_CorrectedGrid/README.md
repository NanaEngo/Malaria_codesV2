# P1 V5 — African Antimalarial Chemical Space

## Migration status

**Status: `MIGRATION_IN_PROGRESS` (7 August 2026).**

This directory is the controlled V5 successor of:

```text
Project1_Chem_space_antimalarial_V4_CorrectedGrid/
```

V4 remains unchanged and is the frozen evidence baseline. V5 was created as a full controlled copy, excluding only generated LaTeX caches/logs and Python cache files. Source data, scripts, figures, audit artifacts, and historical PDFs were retained for provenance. Inherited PDFs are quarantined under `manuscript/provenance/inherited_pdfs/` and inherited V4 audit/preflight JSON records are quarantined under `results/provenance/inherited_v4/`; neither is a V5 release artifact.

### V5 scope

The V5 objective is to produce a new canonical Paper 1 package after the V4 audit. The `teamwork/` request proposed:

1. DiffDock rescoring of the **17 P2 Set-C polypharmacology candidates** against 7F3Y, 6UKJ, 4GM2, and 9N10 (68 pairs); this inherited proposal is now superseded because 4GM2 is PfClpR, not PfClpP;
2. empirical Vina+DiffDock consensus integration into P2 RRS/PNS tables;
3. migration of the Paper 1 sources from V2607 to V2608;
4. a new Main + Supplementary Material + Cover Letter package.

The P2 Set-C cohort is not the P1 Set-A MPO top-20 cohort and must remain explicitly separate.

## Evidence boundary

The V5 migration contains an inherited raw DiffDock run for provenance, but the panel is now **superseded and scientifically invalid for the intended four-target claim** because PDB 4GM2 is PfClpR rather than PfClpP. There is no accepted new Vina/consensus biological result. The deterministic 68-row input manifest and raw outputs remain under `results/diffdock_polypharm/` and `results/diffdock_full_68_verified/` as superseded provenance records; they must not be used for Vina, consensus, RRS, PNS, or manuscript claims. See `results/target_identity_audit.json`. An independent audit validates 68/68 rank-1 pose SDFs and 68/68 rank-1 confidence SDFs, while identifying 11 invalid secondary confidence poses among 612. A coordinate audit finds 10/68 poses fully inside the predeclared Vina grids, 14/68 partial, and 44/68 outside. Therefore:

- DiffDock rank-1 files are accepted as hashed raw pose artifacts, not as affinity measurements;
- DiffDock confidence is not converted to kcal/mol and is not combined with Vina;
- Vina score-only rescoring is blocked until the coordinate-frame/pocket mismatch is resolved without post-hoc translation or arbitrary box expansion;
- no four-target consensus, RRS, or PNS table is updated;
- no V5 claim is treated as biologically validated by this run;
- the fixed-center smoke gate **failed closed** in the final deterministic attempt: DiffDock completed with zero internal failures/skips, but rank-1 containment was only `0.7916667` (79.17%) in the declared grid; earlier smoke artifacts are superseded and no smoke run authorizes the 68-pair execution;
- V5 compilation and final adversarial sign-off remain pending.

The inherited V4 MMV, DEKOIS, ChEMBL, chemical-space, docking, selectivity-proxy, and ADMET artifacts remain historical baseline evidence and retain their V4 limitations.

## Canonical V5 manuscript sources

```text
manuscript/Antimalarial_Candidates_African_NP_V2608.tex
manuscript/Antimalarial_Candidates_African_NP_V2608_SM.tex
manuscript/Cover_Letter.tex
```

The V2608 source files were initially copied byte-for-byte from the V4 V2607 sources, then renamed and their internal cross-references updated. They now carry an explicit internal-draft notice because their scientific body remains inherited V4 content. They have not yet been compiled as V5.

## Structural-pocket dossier

`results/structural_pocket_dossier.md` records evidence-bounded, target-specific decisions for 7F3Y, 6UKJ, 4GM2, and 9N10 using authoritative RCSB entry metadata and the local PDB inventory. It deliberately does not promote any target to an accepted docking pocket: MTX/NDP/UMP provide a candidate PfDHFR anchor requiring independent review; Y01 in PfCRT is a membrane-mimetic proxy and is not accepted as an inhibitor anchor; the current 4GM2 entry is PfClpR rather than PfClpP and is therefore a hard target-identity mismatch; PfATP4 has no small-molecule inhibitor anchor in 9N10 and requires a separately supported cavity definition. No arbitrary center, post-hoc translation, or box expansion is allowed.

## Required gates before V5 completion

1. Verify the DiffDock environment, entrypoint, model hashes, configuration, and normalization-array hashes against the recorded input provenance.
2. Preserve the immutable 68-row input manifest and raw execution provenance.
3. Independently audit rank-1 pose and confidence SDF completeness, hashes, candidate identities, and coordinate compatibility.
4. Resolve the pocket/grid coordinate mismatch using a target-specific pocket-aware protocol or formally justified receptor/grid revision; the final deterministic fixed-center smoke failed closed at 79.17% rank-1 containment. Never translate poses after generation.
5. Run isolated Vina score-only rescoring only after the coordinate gate passes, loading scores from empirical files and never from hardcoded score dictionaries.
6. Obtain a genuine WT+mutant Vina panel for all four targets before claiming four-target consensus or RRS.
7. Recompute consensus/RRS/PNS only after gates 1–6 pass.
8. Update V5 manuscript text/tables with only accepted machine-readable outputs.
9. Compile Main, SM, and Cover Letter; scan for errors, undefined citations, stale V2607 references, and unresolved placeholders.

See `results/v5_migration_manifest.json` for the machine-readable migration record.
