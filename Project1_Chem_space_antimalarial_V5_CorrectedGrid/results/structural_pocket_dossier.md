# P1 V5 structural-pocket dossier

**Status:** `REVIEW_REQUIRED_NOT_AUTHORIZED`

**Purpose.** This dossier separates structural evidence from geometric convenience. It is a provenance and review record, not an authorization to run DiffDock, Vina, GROMACS, consensus scoring, RRS, or PNS.

## Global rules

- No historical grid center is accepted as a biological pocket by itself.
- No post-hoc pose translation and no arbitrary box expansion are permitted.
- DiffDock confidence is not an affinity measurement.
- A target may enter a future pilot only after target-specific pocket evidence, exact receptor-frame equivalence, and an independent review.
- The four V5 targets remain individually gated; a weak or proxy-supported target cannot be rescued by evidence from another target.
- The P1 V5 Set-C cohort remains separate from P1 Set A, P2 Set B, and the four parent MD leads (201, 438, 164, 214).

## Evidence register

| Target | Entry | Experimental context | Bound non-water ligand | Pocket evidence | Current decision |
|---|---|---|---|---|---|
| PfDHFR | [RCSB 7F3Y](https://www.rcsb.org/structure/7F3Y) | X-ray, 2.25 Å | MTX, NDP, UMP, GOL | Co-modelled folate/substrate/cofactor ligands provide a defensible active-site reference; exact ligand identity, chain selection, and receptor-frame mapping still require independent review. | `CANDIDATE_ANCHOR_REVIEW_REQUIRED` |
| PfCRT | [RCSB 6UKJ](https://www.rcsb.org/structure/6UKJ) | Cryo-EM, 3.30 Å | Y01 (cholesterol hemisuccinate) | Y01 is a membrane-mimetic/stabilizing proxy, not a co-crystallized antimalarial inhibitor. The central cavity may be considered only with independent mutational/transport evidence and explicit flexibility caveats. | `PROXY_NOT_ACCEPTED` |
| PfClpP | [RCSB 4GM2](https://www.rcsb.org/structure/4GM2) | X-ray, 2.80 Å | None | **Identity mismatch:** RCSB 4GM2 is PfClpR, an inactive paralog/subunit, not PfClpP. It cannot serve as a PfClpP receptor. A genuine PfClpP structure must be supplied before any pocket discussion. | `TARGET_IDENTITY_MISMATCH_BLOCKED` |
| PfATP4 | [RCSB 9N10](https://www.rcsb.org/structure/9N10) | Cryo-EM, 3.80 Å | No small-molecule inhibitor; PfABP is a protein partner | Transmembrane pathway or PfATP4–PfABP interface hypotheses require target-specific pharmacology/mutagenesis and conformational justification; arbitrary coordinates are not accepted. | `CAVITY_EVIDENCE_REQUIRED` |

## What is required before a target-specific pilot

### PfDHFR

1. Independently verify MTX/NDP/UMP identity and chain/instance selection.
2. Define the catalytic/folate/cofactor pocket from the reviewed ligand and residue annotation, not a raw centroid.
3. Verify that the exact DiffDock receptor PDB and Vina PDBQT share the same frame and residue identity.
4. Run one exact-configuration smoke pair only after the review record is accepted.

### PfCRT

1. Do not treat Y01 as inhibitor-pocket evidence.
2. Provide a reviewed cavity definition supported by structural mutation/transport evidence or a drug-bound/validated structural model.
3. If the cavity cannot be defended at the resolution and conformational state of 6UKJ, exclude PfCRT from the primary V5 docking claim rather than force it into the four-target panel.

### PfClpP

1. Replace 4GM2 with a verified PfClpP receptor; 4GM2 is PfClpR and is not acceptable for a PfClpP claim.
2. Document the oligomeric state and the proposed axial pore/chamber residues of the correct PfClpP structure.
3. Support the pocket with biochemical, mutational, ligand-bound, or validated cavity evidence.
4. Do not use an exterior surface cleft selected only by geometry.

### PfATP4

1. Define whether the pilot targets the transmembrane pathway or the PfATP4–PfABP interface.
2. Provide mutation/pharmacology evidence for the chosen site and account for the 3.80 Å cryo-EM resolution and conformational state.
3. Do not claim spiroindolone or other inhibitor binding-site coordinates without direct or independently validated evidence.

## Target-identity hard block

The inherited V5 panel labelled `4GM2` as `PfClpP`. The authoritative RCSB entry identifies 4GM2 as PfClpR, an inactive paralog/subunit, not PfClpP. This is a target-identity failure, not a pocket-quality limitation. The inherited manifest and raw DiffDock artifacts are therefore superseded provenance and cannot support any PfClpP score, consensus, RRS, PNS, or manuscript claim. See `results/target_identity_audit.json`.

## Current machine-readable gate

`results/structural_pocket_preflight.json` records:

- `status = REVIEW_REQUIRED_NOT_AUTHORIZED`;
- `independent_review_status = PENDING`;
- `accepted_for_full_run = false`;
- no accepted DiffDock/Vina/GROMACS launch or consensus/RRS/PNS update;
- non-water HETATM inventory only, with PfCRT Y01 explicitly treated as a proxy and PfClpP/PfATP4 lacking ligand anchors.

The register `results/structural_pocket_independent_review.json` is intentionally pending. It must not be edited to simulate an independent review or a signature.

## Sources

- RCSB PDB 7F3Y: https://www.rcsb.org/structure/7F3Y
- RCSB PDB 6UKJ: https://www.rcsb.org/structure/6UKJ
- RCSB PDB 4GM2: https://www.rcsb.org/structure/4GM2
- RCSB PDB 9N10: https://www.rcsb.org/structure/9N10
- V5 preflight: `results/structural_pocket_preflight.json`
- V5 review protocol: `results/structural_pocket_review_signature_protocol.md`
- V5 tracking: `project-tracking.md`

## Decision

The scientifically defensible sequence remains:

1. submit the corrected V4 package after final compilation and human author approval;
2. resolve structural evidence target by target;
3. run an exact-config pilot per accepted target;
4. obtain independent review and cryptographically bound authorization;
5. only then consider a full V5 run and downstream consensus/RRS/PNS calculations.
