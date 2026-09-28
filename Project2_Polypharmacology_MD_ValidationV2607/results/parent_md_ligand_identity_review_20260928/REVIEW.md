# Parent-MD Ligand Identity Review
Date: 2026-09-28 | Status: **FAIL_MANUSCRIPT_CONSENSUS_LEAD_CLAIM_NOT_SUPPORTED**

## Question
Do the four parent-study production-MD systems contain the molecules named by
the manuscript claim (main text): "Four additional parent-study consensus
leads (Ligands 201, 214, 438, 164) were evaluated in production-MD wild-type
complexes"?

## Method
- Production ground truth: UNL composition of `complex_boxed.gro`, cross-checked
  against a second per-system ligand artifact (MMPBSA/complex PDB); both must agree.
- Scheme B (seed-library 0-based index of `all_molecules.csv`, 850 rows) formula match.
- Scheme A (docking/consensus cluster-representative numbering,
  `data/pdb_ligands/`) label content compared against production.
- Set-C disjointness by canonical SMILES against the 17 Set-C candidates.
- Receptor correspondence: prepared-receptor CA counts vs chain A of the named PDB.
- All checks asserted; script re-run reproduces this file.

## Results
| System | Dir label | Production content (formula) | Scheme-B identity | Scheme-A label content | Verdict |
|---|---|---|---|---|---|
| 201_PfDHFR | 201 | C42H38O23 | B-201 = [(2R,3R,4S,5R,6S)-3,5-diacetyloxy-2-(ace | A-201 = C22H18N2O2 (differs) | not the named consensus lead |
| 214_PfCRT | 214 | C13H12O4 | B-214 = (5Z)-5-[(2S)-2-hydroxy-3-phenoxy-propyli | A-214 = C20H20N4O3S (differs) | not the named consensus lead |
| 438_PfATP4 | 438 | C16H20O6P2S3 | B-437 = Temefos | A-438 = C15H15ClN4O (differs) | off-by-one; not the named consensus lead |
| 164_PfClpP | 164 | C15H10O7 | B-164 = (5,8-dihydroxy-4,9-dioxobenzo[f][2]benzo | A-164 = C20H20O6 (differs) | not the named consensus lead |

## Numbering universes
- **Scheme A** = `data/pdb_ligands|pdbqt_ligands` (K-Means cluster representatives):
  the universe used by ALL docking runs and by the README "Named Consensus Hits"
  (201/214/87/438/164). Consensus scores in this numbering: 201 7F3Y -8.49 (GOOD).
- **Scheme B** = `data/ligands/pdb` 0-based index of `all_molecules.csv`
  (396 natural products + 454 synthetic). **Production MD content is scheme B.**
- **Scheme C** = `pdb_ligands_mmv` (MMV consensus) - not involved.

## Verdict
1. **NONE of the four production systems contains its named scheme-A
   consensus-lead molecule.** Production molecules are B-201 (pentaacetyl
   glycoside, C42H38O23), B-214 (C13H12O4), **B-437 (Temefos, C16H20O6P2S3)
   inside the 438-labelled directory - off-by-one**, B-164 (aurone acetate,
   C15H10O7).
2. The manuscript consensus-lead claim is therefore **not supported** under
   every consistent reading; scheme-B indices carry no consensus-lead status.
3. Stale preparation files contradict production (do not use for claims):
   201 `complex.pdb`/`ligand_201.mol2` (2026-07-10) contain a different
   molecule (oxindole, scheme-A index 307) vs the 2026-07-06 production box;
   214 `complex.pdb` (07-10) contains a third unidentified molecule;
   438 `ligand/ligand_438.mol2|pdb` contain DSM-265 (B-438) while production
   simulated Temefos (B-437). Production artifacts (box + MMPBSA) are internally
   consistent per system.
4. **Receptor correspondence PASS**: prepared receptors match chain A CA counts
   of 7F3Y (549), 6UKJ (350), 9N10 (985), 4GM2 (183) - supports "the 164
   system represents PfClpR (PDB 4GM2)".
5. Set-C disjointness PASS: none of the four production molecules is among the
   17 Set-C candidates.

## Recommended manuscript fix (author decision pending)
Replace the consensus-lead wording with an honest provenance statement, e.g.
"four parent-study library complexes (upstream indices 201, 214, 437, 164; the
438-labelled system contains index 437) were evaluated in production-MD
wild-type complexes" - or drop the labels entirely and cite the archived
identity review.

## Provenance
- Script: `scripts/p2_parent_md_ligand_identity_review_20260928.py`
  sha256 {summary['script_sha256'][:16]}...
- Outputs: this directory (versioned; nothing overwritten).
- `results/metrics/parent_md_source_inventory.json` remains FAIL_CLOSED
  untouched by this review.
