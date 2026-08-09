# P1 V4 structural blocker and V5 backport decision — 9 August 2026

## Decision

P1 V4 is **not submitted**. The existing V4 numerical panel contains the historical `4GM2` arm, while the V5 structural audit established that PDB 4GM2 is PfClpR rather than genuine PfClpP. Correcting the prose alone is insufficient for a submission package that still presents the four-target numerical panel as if it included PfClpP.

The genuine PfClpP structure selected for controlled replacement is PDB `2F6I`. V5's completed 17-by-4 raw Vina runs are not substituted into V4: they are a different cohort and cannot replace the V4 484-centroid panel.

## Safe backport

- 4GM2 is described as PfClpR-specific.
- Historical parent-MD label `164` is not treated as PfClpP structural validation.
- V5 consensus/RRS/PNS outputs remain excluded because the V5 independent-review register is still pending and the bypass-derived consensus is VOID.
- V4 numerical scores are preserved unchanged until a complete replacement exists.
- V4 status documents now state `BLOCKED` pending full 2F6I replacement and independent review.

## Controlled replacement

- Canonical centroid source: `Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/cluster_representatives_smiles.csv` (484 unique rows, zero-based centroid mapping).
- Receptor: `2F6I.pdb` and coordinate-equivalent `2F6I.pdbqt`.
- Anchor: chain-A catalytic triad Ser252/His223/Asp219, derived from the PDB, not hard-coded coordinates.
- Search space: 28 Å cubic Vina box centered on the triad centroid.
- Composite raw gate: centroid in declared box; at least 90% atoms in box plus 0.5 Å padding; nearest pose atom within 10 Å of the catalytic triad.
- Worker: `scripts/p1_v4_revalidate_clpp_2f6i.py`.
- Aggregator: `scripts/p1_v4_aggregate_clpp_2f6i.py`, which independently checks canonical SMILES identity, source/receptor/Vina hashes, raw pose/log presence and hashes, PDB/PDBQT frame equivalence, and recomputed pose gate.

## Execution status

- Centroid-0 smoke attempt 1: failed closed due to a relative-path bug in the worker; no accepted result.
- Centroid-0 smoke attempt 2: passed technical raw Vina gate (`PASS_RAW_VINA`, affinity `-6.627` kcal mol−1); this is not a biological validation claim.
- Full array: SLURM job `12929`, array `0-483`, concurrency `16`, raw outputs only.
- Independent QC: SLURM job `12966`, dependency `afterok:12929`; no downstream scoring.
- Early observed failures: centroid 13 and 40 contain boron and Vina rejects AutoDock atom type `B`; centroid 30 fails deterministic RDKit embedding under three tested strategies. These remain fail-closed and must be resolved by a validated preparation policy or counted as exclusions; no element substitution or SMILES mutation is allowed.

## Promotion rule

Even if all raw records pass QC, the result remains `RAW_ARRAY_COMPLETE_PENDING_INDEPENDENT_REVIEW`. No consensus, MPO, RRS, PNS, manuscript table, acceptance claim, or submission status may be updated until the receptor/pocket evidence and complete raw panel have been independently reviewed and explicitly authorized.
