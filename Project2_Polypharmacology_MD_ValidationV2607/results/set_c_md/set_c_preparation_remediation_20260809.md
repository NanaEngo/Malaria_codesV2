# Set-C MD preparation remediation — 9 August 2026

## Current result

The bounded pilot selected `PP-01` and `PP-02` across PfDHFR and PfCRT:

- 16 candidate–target–mutation systems expected;
- 16/16 blocked;
- 136/136 docking rows available and finite;
- 0 candidate-specific MD systems ready;
- 0 GROMACS processes launched;
- `md_rrs_status=NOT_COMPUTED`.

The authoritative machine-readable outputs are:

- `results/pilot/set_c_md_pilot_manifest.json`;
- `results/set_c_md/set_c_md_execution_manifest.json`;
- `results/set_c_md/set_c_md_status.csv`.

## Required preparation contract

For every system directory
`results/md_systems/set_c/PP-{01,02}_{PfDHFR,PfCRT}_{mutation}/`, preparation must produce:

1. `complex.gro` with candidate-specific coordinates;
2. `topol.top` and every recursively included topology/parameter file;
3. `md.mdp` with the declared temperature, timestep, restraints, and output frequency;
4. `npt.gro` and `npt.cpt` from a completed, auditable equilibration;
5. `system_manifest.json` binding candidate ID, target, mutation, canonical SMILES, cohort ID, receptor/ligand hashes, and coordinate frame;
6. `forcefield_manifest.json` declaring and hash-binding:
   - protein force field: `CHARMM36m`;
   - ligand force field: `CGenFF`;
   - water model: `TIP3P`;
   - topology, coordinate, checkpoint, system-manifest, and recursive topology-dependency hashes.

## Prohibited shortcuts

- Do not copy the four parent-study systems into Set-C.
- Do not relabel historical ACPYPE/GAFF2 files as CHARMM36m/CGenFF.
- Do not create manifests around files whose force-field provenance is unknown.
- Do not infer MD-RRS from docking-RRS or from parent-study trajectories.
- Do not launch `grompp` or `mdrun` until the workflow reports `ready_system_count=16` and `blocked_system_count=0`.

## Execution sequence after preparation

1. Generate candidate-specific receptor/ligand systems with a tracked preparation toolchain.
2. Independently verify identities, coordinate frames, topology includes, and hashes.
3. Run the existing `p2_setc_md_workflow.py` in read-only mode.
4. Require `READY_FOR_AUTHORIZED_EXECUTION`.
5. Launch only with `--execute` and `P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND`.
6. Run trajectory QC before any MD-RRS calculation.
7. Keep docking-RRS and MD-RRS in separate columns and separate provenance records.

Until these conditions are met, the scientifically correct statement is: **Set-C MD has not been performed; MD-RRS is not computed.**
