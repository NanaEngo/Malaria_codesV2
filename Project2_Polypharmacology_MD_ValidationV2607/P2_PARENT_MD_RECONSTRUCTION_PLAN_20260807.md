# P2 parent-study MD — reconstruction and execution plan

**Date:** 7 August 2026
**Cohort:** `P2_PARENT_STUDY_MD_4`
**Scope:** 201–PfDHFR, 438–PfATP4, 164–PfClpP (historical label), and 214–PfCRT
**Status:** `FAIL_CLOSED_BLOCKED`; no new GROMACS execution authorized

## 1. Evidence boundary

The four named systems are the parent-study MD cohort. They are **not** the 17 set-C polypharmacology candidates used for docking-derived RRS, ACSI, PNS, and cross-metric analyses. The historical record reports 10 ns per named system (40 ns total), with only PfCRT–214 receiving an interpretable endpoint estimate. That historical record is retained as bounded evidence; this plan does not re-label it as a new run.

The current guarded preflight is the source of truth for any future execution:

```text
scripts/p2_parent_md_preflight.py
status: FAIL_CLOSED_BLOCKED
ready: 0/4
blocked: 4/4
gromacs_launched: false
```

## 2. Current blockers

| System | Historical files present | Current blocker | Consequence |
|---|---:|---|---|
| `201_PfDHFR` | `ions.gro`, `topol.top`, `npt.gro`, `npt.cpt` | Missing `forcefield_manifest.json`; existing ligand artifacts are ACPYPE/GAFF2-derived | Cannot certify CHARMM36m+CGenFF provenance or launch a new stage |
| `438_PfATP4` | `ions.gro`, `topol.top` | Missing/empty `npt.gro` and `npt.cpt`; missing force-field manifest; historical rebuild script contains a pose-shifting workflow | Must be reconstructed from verified inputs; no continuation from absent NPT state |
| `164_PfClpP` | `ions.gro`, `topol.top`, `npt.gro`, `npt.cpt` | **Target identity blocked:** the historical receptor 4GM2 is PfClpR, not PfClpP; force-field manifest also missing | Do not rebuild or report this as PfClpP until a genuine, independently verified PfClpP receptor is supplied |
| `214_PfCRT` | `ions.gro`, `topol.top`, `npt.gro`, `npt.cpt` | Missing force-field manifest; ligand source variants have non-matching hashes | Ligand identity and parameter provenance must be resolved before rebuild |

Adding a manifest around these files would be invalid: it would certify neither the force field actually used nor the identity of the coordinates, and would conceal the missing 438 NPT state. No `forcefield_manifest.json`, `npt.gro`, or `npt.cpt` is created by this mitigation.

## 3. Required reconstruction sequence

### Gate A — Freeze source identity

The historical `164` system is not eligible for a PfClpP reconstruction under the current receptor assignment. It remains a provenance-only diagnostic until a genuine PfClpP structure is independently verified. A future source manifest must therefore record the accepted PDB identity and explicitly fail if a PfClpR/PfClpP mismatch is detected.

The current machine-readable deliverable is the inventory `results/metrics/parent_md_source_inventory.json`; it contains candidate files only and intentionally has no selected source records. A future reviewed `results/metrics/parent_md_source_manifest.json` must contain one record per eligible system and SHA-256 references to the selected receptor, ligand, canonical-SMILES record, docking pose, and preparation inputs. That reviewed source manifest is distinct from the force-field manifest and is not an authorization artifact.

For each lead, record one immutable receptor–ligand input pair with:

- authoritative receptor PDB ID and target identity;
- chain/residue selection and protonation policy;
- ligand canonical SMILES, formal charge, stereochemistry, and source PDB hash;
- docking-pose provenance and coordinate-frame relationship;
- SHA-256 hashes for every source file.

The current inventory is insufficient for immediate acceptance: several ligand PDB variants exist for the same numeric lead and the canonical SMILES are not directly bound to `201`, `438`, `164`, and `214` in one machine-readable record. The source manifest must be completed before any reconstruction; for `164`, it must contain a verified PfClpP receptor or mark the system `IDENTITY_BLOCKED`.


### Gate B — Resolve force-field tooling

The approved future policy is:

- protein: CHARMM36m;
- ligand: CGenFF;
- water: TIP3P;
- temperature: 310.15 K.

The `malaria_md` environment has GROMACS 2025.4, OpenMM, OpenFF, RDKit, ACPYPE, Open Babel, and PDBFixer. It does **not** currently provide `cgenff` or `cgenff_charmm2gmx`, and no ParamChem credential is configured. ACPYPE/GAFF2 is not an acceptable silent substitute for this rerun because the historical mixed-force-field limitation is already documented.

A future run therefore requires either:

1. a locally available, version-pinned CGenFF parameterization and conversion tool with its license/credential provenance; or
2. manually supplied CGenFF stream/parameter files whose provenance, penalty information, and hashes are recorded.

No credentials are written to the repository.

### Gate C — Rebuild eligible systems

Rebuild only systems whose receptor and ligand identities have passed Gate A, not from historical `npt.*` files. The historical `164` system remains excluded until a genuine PfClpP receptor replaces 4GM2/PfClpR:

- eligible systems may proceed through reconstruction after source and parameter review;
- `164_PfClpP` remains `IDENTITY_BLOCKED` and cannot contribute a PfClpP result until replacement and independent verification.

For each eligible system:

1. prepare receptor with the pinned CHARMM36m-compatible workflow;
2. parameterize the ligand with CGenFF and document penalties/charge state;
3. assemble the complex without post-hoc ligand translation;
4. define the box, solvate with TIP3P, add ions, and generate `ions.gro`;
5. run EM → NVT → NPT at 310.15 K;
6. write `forcefield_manifest.json` only after all required files exist and their hashes are computed;
7. write the force-field manifest only after recording parameter-source/version, CGenFF stream/penalty provenance, ligand charge/stereochemistry, and source-manifest hash;
8. independently validate the manifest with `md_forcefield_manifest.py`;
9. require the validator and source-manifest audit to pass before treating the system as eligible for execution.

The 438 system requires a complete new NPT sequence; it cannot inherit missing `npt.gro`/`npt.cpt`. The historical `rebuild_438_complex_md.sh` is not the publication-grade pipeline because it contains historical pose-shifting and legacy force-field assumptions; it remains provenance only until rewritten against the gates above.

### Gate D — Preflight and execution

Only when the receptor identity gate is resolved for every intended target, all eligible-system manifests and required files pass, and the target count is explicitly recorded (currently this cannot be 4/4 because the 164/PfClpP receptor is unresolved):

```bash
python3 scripts/p2_parent_md_preflight.py
# required result: READY_FOR_EXPLICIT_REVIEW, ready_system_count=4

export P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND
bash scripts/md_full_pipeline.sh --execute --yes
```

The execution record must include the runner hash, GROMACS binary/version, force-field policy, temperature, replicate seeds, system hashes, parameter-source/version, CGenFF stream/penalty provenance, ligand charge/stereochemistry, source-manifest hash, and explicit authorization. A failed system must stop the campaign rather than being silently omitted.

## 4. Publication interpretation rule

A future successful rerun would be a **new, explicitly labelled reconstruction**, not a replacement of the historical ACPYPE/GAFF2 run. Historical and reconstructed trajectories must be compared only after checking receptor/ligand identity, force-field compatibility, equilibration, ligand retention, replicate consistency, and trajectory quality. MM-GBSA remains interpretable only for bound, non-corrupted systems; it cannot rescue dissociation or parameter-conversion artifacts.

RRS remains a docking-derived resistance-resilience metric unless a pre-registered, target-specific MD/RRS definition is separately implemented and validated. No MD-RRS claim is made by this plan.

## 5. P1 V5 dependency

P1 V5 remains blocked independently of P2 MD. The inherited 4GM2 structure is PfClpR rather than PfClpP; PfATP4 and PfCRT pocket definitions require target-specific evidence and independent review; and the deterministic DiffDock smoke did not satisfy the rank-1 containment gate. No V5 consensus, Vina, RRS, or PNS result is promoted until a genuine PfClpP structure and accepted pocket dossier exist.

## 6. Acceptance-maximizing decision

The scientifically strongest action is to preserve the current honest negative/blocked status and complete source/force-field provenance before running anything. A fast manifest-only workaround or a GAFF2-to-CGenFF relabel would create a reviewer-visible reproducibility defect and would lower, rather than raise, acceptance probability.
