# Set-C preparation audit — 11 August 2026

## Scope

This note records the forensic audit of the background preparation attempts for the
16-system P2 Set-C pilot. It is an execution/provenance record, not a manuscript
result. No Set-C trajectory, MD-RRS value, or publication claim is promoted here.

## Attempt 15196

`15196` failed before preparation because its Slurm `--wrap` command attempted to
source/activate Conda under a shell that did not provide the expected `source`
function. The resulting Python process lacked OpenFF (`ModuleNotFoundError`). No
system was promoted.

## Attempt 15197

`15197` used the correct absolute `malaria_md` Python and passed package-import
checks, but failed during the first system (`PP-01_PfDHFR_WT`) in the Open Babel
step. The executable resolved through `PATH` to the incompatible Python 3.13
wrapper (`_openbabel.so: undefined symbol ...`). The compatible executable is
`/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel` (Open Babel 3.1.0).
Only a temporary `ligand_heavy_dock.pdb` was left in the isolated output root;
no `complex.gro`, `topol.top`, or preparation manifest was promoted.

## Fail-closed controls added before the next attempt

1. The preparation script pins absolute `malaria_md` executables for GROMACS and
   Open Babel; both are version-checked and Open Babel performs a real temporary
   PDB-to-SDF conversion smoke test before any system directory is created.
2. Required Python modules (OpenFF Toolkit/Interchange, PDBFixer, OpenMM, SciPy,
   and RDKit) are checked in the running interpreter.
3. Preparation uses a hidden per-system work directory and atomically promotes it
   only after completion. Failures leave a machine-readable
   `*.preparation_failed.json` marker and cannot create a partially promoted
   system.
4. A pre-equilibration audit checks topology/coordinate molecule order, ligand
   placement before solvent, atom counts, finite coordinates, all-atom
   sub-0.5-A overlaps, and a final `grompp -maxwarn 0` check.
5. The equilibration worker requires `pre_equilibration_audit.json` with `PASS`,
   verifies its input hashes, requires the absolute `malaria_md` Python, and uses
   `grompp -maxwarn 0` for every stage.

## Subsequent witness chronology

### 15198 — AM1-BCC backend unavailable

The toolchain preflight passed the Python imports but OpenFF could not discover an
AM1-BCC backend. The job failed before system promotion with
`ChargeMethodUnavailableError`. No fallback to Gasteiger or zero charges was
allowed because that would change the declared protocol.

### 15199 — receptor path failure

After the AM1-BCC environment fix, the witness reached protein preparation but
failed before promotion because `pdb2gmx` received a relative path to
`receptor_fixed.pdb` after the working directory changed. The receptor was
written by PDBFixer, but GROMACS looked in the wrong location. The path was made
absolute and existence-checked before `pdb2gmx`.

### 15200 — topology/coordinate order failure

The witness reached GROMACS but failed closed at `grompp` with 17,563 atom-name
mismatch warnings. The cause was insertion of `MOL0` before the protein entries
because the `; Compound #mols` comment in `[ molecules ]` was misread by the
insertion logic. The parser now ignores comments and enforces
`Protein_chain_* → MOL0 → SOL/NA/CL`.

### 15201 — audit path failure

The witness passed preparation steps but the final audit called `grompp` with
paths containing the work-directory prefix while also setting `cwd` to that
work directory. GROMACS therefore searched for duplicated paths and failed with
"file does not exist". The audit now passes local filenames with `cwd=system_dir`
and retains `-maxwarn 0`.

### 15202 — provenance bookkeeping failure

The witness produced a scientifically valid prepared system and passed
`grompp`, but its audit JSON contained literal trailing `\\n` bytes and the
root preparation status remained `IN_PROGRESS`. The artifact was repaired for
inspection, but 15202 was not accepted as the final witness because it preceded
the complete provenance fix.

### 15203 — final witness PASS

`15203` (`PP-01_PfDHFR_WT`) is the first final witness using the complete corrected
worker. Independent read-only verification found:

- all five JSON artifacts parse successfully;
- `pre_equilibration_audit.status = PASS`;
- `grompp = PASS` with `grompp_maxwarn = 0`;
- non-null force-field manifest hash;
- `preparation_status = COMPLETED`;
- 316,108 atoms with finite coordinates;
- topology order `Protein_chain_A/B → MOL0 → SOL/NA/CL`;
- minimum pair distance 0.823 Å in the prepared solvated coordinates.

This is a **preparation witness only**. No Set-C scientific result is promoted,
and no equilibration or production job is authorized by this witness alone.

## Promotion rule

No equilibration array, production array, QC, or MD-RRS job may be submitted until
an independent read-only audit reports all 16 systems prepared, all 16
pre-equilibration audits `PASS`, and all required manifests/hashes are present.

The final witness permits submission of the **preparation array only**, provided
that its output root is fresh, each system is independently audited, failures are
quarantined, and the array is not chained to equilibration automatically. The
next gate remains explicit: `16/16 preparation PASS` before any equilibration.

### 15204 — shell wrapper failure (no scientific execution)

The first full preparation submission failed immediately before Python startup:
`sbatch --wrap` used the scheduler's `/bin/sh`, which rejected `set -o pipefail`
(`Illegal option -o pipefail`). No system directory, topology, coordinates,
manifest, or scientific output was promoted. The corrected submission explicitly
invokes `/bin/bash -lc`; this is an execution-wrapper correction only.

### 15205 — preparation-only array launched

Job `15205` was submitted with an explicit `/bin/bash -lc` wrapper after the
non-scientific shell failure of `15204`.

- output root: `results/md_systems/set_c_preparation_20260811_v7`;
- command: corrected `p2_setc_prepare_openff.py --all` with absolute
  `malaria_md` Python, GROMACS, and Open Babel paths;
- SLURM dependency: none;
- preflight: GROMACS, Open Babel, OpenFF modules, AmberTools AM1-BCC, and PDB→SDF
  smoke tests all passed;
- first system observed: `PP-01_PfDHFR_WT`;
- policy: preparation only; no equilibration, production, QC, or MD-RRS is
  chained or authorized.

The promotion gate remains strict: independently verify `16/16` systems with
parseable audits, `grompp = PASS`, `-maxwarn 0`, manifests/hashes, and no
partial system before considering equilibration.

### 15206 — equilibration-only array launched after independent 16/16 gate

The independent preparation gate for `set_c_preparation_20260811_v7` passed:
16/16 systems had parseable audits with `status=PASS`, `grompp=PASS`, and
`grompp_maxwarn=0`; root-level `preparation_status.json` was `COMPLETED` with
16 records; manifests, hashes, coordinates, and molecule ordering were checked.

Job `15206` was then submitted using `scripts/p2_setc_equilibrate_final.sbatch`
with `P2_SETC_ROOT` explicitly set to the fresh preparation root. This is an
 equilibration-only array (`0-15%4`): initially 4 tasks were `RUNNING` and 12
were pending under the array concurrency limit. No production, trajectory QC,
or MD-RRS job was chained or submitted. Production remains blocked until all
16 equilibration outcomes and the expected `npt.gro`/checkpoint/log artifacts
are independently audited.

### 15206 / 15222 — equilibration failure diagnosis (structural/topology gate)

The equilibration-only array `15206` was stopped after the read-only check showed
15 failed tasks, no completed task, and no valid `npt.gro` or `npt.cpt` in the
fresh root `set_c_preparation_20260811_v7`. The failure was initially surfaced
as an Open MPI `MPI_ABORT`; this is only the runtime wrapper symptom.

A single-system diagnostic (`15222`, `PP-01_PfCRT_K76A`) reproduced the failure.
A correct full-input manual `grompp` (all included `.itp` and restraint files,
not the incomplete earlier fixture) identified the primary gate failure:

```
The largest distance between excluded atoms is 2.344 nm between atom 1129 and 1136
Too many warnings (1). If you are sure all warnings are harmless, use the -maxwarn option.
```

The mapped atoms are in protein chain A and correspond to the region around
GLY 113 and HIS 123, with residues 114--122 unresolved in the receptor PDB.
The generated protein topology contains the corresponding connected/excluded
backbone graph across this internal structural gap, making the 2.344-nm
excluded-pair distance a topology/structure integrity issue rather than a
benign ligand-geometry warning. The exact topology/PDB evidence is retained in
the diagnostic root and must be rechecked after regeneration.

**Scientific decision:** `-maxwarn 0` remains fail-closed. No `-maxwarn 1`,
warning suppression, production, trajectory QC, or MD-RRS is authorized.
The next valid remediation is either (i) model the unresolved loop with a
validated structure-building protocol, or (ii) explicitly split and cap the
continuous structural segments with a documented biological rationale, then
regenerate the protein topology. A fresh single-system witness must pass
strict `grompp -maxwarn 0`, with complete stdout/stderr, before any array
relaunch.

### Gap-remediation pilot v2 — technical topology PASS, biological policy pending

An isolated pilot was run for `PP-01_PfCRT_K76A` in
`results/md_systems/set_c_gap_pilot_20260811_v2`. It inserted one explicit
`TER` only at the verified unresolved transition `PfCRT chain A:113 -> A:123`
(residues 114--122 absent), regenerated the CHARMM36m protein topology, merged
the existing OpenFF ligand, re-solvated/ionized, and regenerated the system and
force-field manifests rather than reusing stale hashes.

Independent checks passed:

- `pdb2gmx` completed successfully;
- `pre_equilibration_audit.json`: `status=PASS`;
- strict `grompp -maxwarn 0`: `PASS` with zero warnings;
- topology and coordinate hashes agree across the regenerated manifests;
- complex coordinate count: 238251 atoms, internally consistent.

This is explicitly classified as `TECHNICAL_TOPOLOGY_PILOT_ONLY`, with
`biological_validation=PENDING_LOOP_OR_CHAIN_POLICY_REVIEW`. Splitting an
unresolved internal loop creates additional termini and is not yet accepted as
a biologically validated PfCRT model. The canonical 16-system preparation root
is unchanged; no equilibration, production, QC, or MD-RRS is authorized from
this pilot until the structural policy and termini/charge consequences are
reviewed.

### PfCRT gap-split pilot — terminal and short EM witness verdict

The terminal audit confirms that the explicit TER creates an internal `COOH`
terminus at GLY113 and a new `NH2` terminus at HIS123. These charge/patch
changes are not yet biologically validated and must not be treated as a neutral
repair.

The first short witness did not start MD because `-ntmpi 1` was incompatible
with the OpenMPI GROMACS build; that launcher error was corrected without
changing the system. In a fresh temporary copy of the v2 pilot, the corrected
OpenMPI-compatible witness gave `grompp RC=0` and `mdrun RC=0`. The 2,001-step
EM run reached approximately `PE=-3.9494882e6 kJ/mol` with no NaN, LINCS, or
segmentation fault and produced a final EM structure. It did not converge to
the requested force tolerance within the deliberately short witness
(`Fmax` approximately `7.914e3`), so this is only technical topology/runtime
and short-EM evidence, not publication-grade equilibration or biological
validation.

**Gate remains closed:** no NVT/NPT, array relaunch, production, trajectory QC,
or MD-RRS is authorized. A full restrained minimization/terminal-policy review
is required before extending the TER split to the other PfCRT variants.

### PfCRT gap-split pilot — full isolated EM witness

A full isolated EM witness was run on the corrected v2 pilot system in a fresh
`/tmp` directory, using the OpenMPI-compatible `gmx_mpi` launcher (`-np 1`,
CPU-only, `-ntomp 8`). No canonical system or SLURM job was modified.

- `grompp -maxwarn 0`: RC 0;
- `mdrun`: RC 0;
- steepest-descent convergence: 2,916 steps;
- final potential energy: `-3.9795712e6` kJ/mol;
- final maximum force: `9.8936542e2` kJ/(mol nm), below the `1.0e3` target;
- no NaN, LINCS, segmentation-fault, or fatal-error marker;
- final EM structure, energy, trajectory, and log were produced.

This strengthens the technical topology/EM evidence but does not validate the
biological treatment of the unresolved loop: the TER split still creates an
internal COOH/NH2 pair whose terminal-state and electrostatic consequences
require explicit structural policy review. NVT/NPT, array relaunch, production,
trajectory QC, and MD-RRS remain blocked.

### PfCRT gap-split pilot — NVT stability diagnosis

The first 2-fs NVT witness (`h-bonds`, `dt=0.002 ps`) failed at 0.174 ps with
escalating LINCS deviations and a segmentation fault. A correct global-to-local
mapping showed that the reported pair is a real `TYR184 CB--HB2` bond with an
initial distance of approximately 1.12 Angstrom; it is not evidence by itself
that the TER split created a long bond.

Two isolated controls clarified the immediate protocol sensitivity:

- constrained NVT at `dt=0.0002 ps` (0.2 fs), 1,000 steps: `grompp RC=0`,
  `mdrun RC=0`, initial temperature approximately 310.171 K, no NaN/LINCS/
  segmentation-fault marker;
- unconstrained control at `dt=0.0005 ps`, 1,000 steps: `grompp RC=0`,
  `mdrun RC=0`, no NaN/LINCS/segmentation-fault marker.

These are diagnostic controls, not publication-grade equilibration. The
standard 2-fs constrained NVT has not yet been validated for the gap-split
system, and the artificial internal COOH/NH2 termini remain a biological and
electrostatic policy issue. No global PfCRT extension, NPT, production,
trajectory QC, or MD-RRS is authorized.

### 15223 — progressive NVT diagnostic checkpoint

The isolated progressive NVT witness is running in
`results/md_systems/set_c_progressive_nvt_15223` from the v2 gap-split pilot.
The EM stage completed; the `dt=0.0002 ps` (0.2 fs) NVT stage completed with
`nvt_dt0p2fs.gro/.cpt/.edr/.log` and no NaN, LINCS, segmentation-fault, or fatal
marker. The `dt=0.0005 ps` stage is being preprocessed/started. No NPT,
production, trajectory QC, or MD-RRS job is chained or submitted. This remains
an isolated diagnostic witness only.

### 15224–15226 — isolated short NPT witness

Job `15224` failed before `mdrun` because the fresh output omitted the protein
`.itp` dependencies included by `topol.top`; no scientific calculation ran.
Job `15225` was a non-scientific wrapper failure caused by a malformed `cp`
block (the output directory command was joined to a comment and a stray `/`
line stopped execution). No MD ran in either case.

The corrected isolated witness `15226` copied all topology dependencies and
completed 1,000 NPT steps (2.0 ps) from the validated progressive NVT endpoint:
`grompp RC=0`, `mdrun RC=0`, no true fatal/NaN/LINCS/segmentation marker, and
`witness_npt.gro/.cpt/.edr/.log` were produced. Mean observables were
`T=310.488 K`, `P=-10.7034 bar`, density `1011.01 kg/m^3`, potential energy
`-3.27276e6 kJ/mol`, kinetic energy `621644 kJ/mol`, and total energy
`-2.65111e6 kJ/mol`.

This is an **isolated 2-ps stability witness**, not a pressure/density
 equilibration or publication-grade MD result. No production, QC, or MD-RRS
job was submitted.

### Decision after 15226 — biological gate takes precedence over more compute

The numerical sequence (full EM, progressive constrained NVT at 0.2/0.5/1/2 fs,
and isolated 2-ps NPT at 2 fs) provides limited evidence of short-term numerical
stability but does not validate the biological model. In particular, the
2-ps mean pressure of -10.7 bar is not evidence of pressure equilibration. The internal `TER` split at the unresolved PfCRT region
creates an artificial internal `COOH`/`NH2` terminal pair. A longer isolated NPT
run would test only numerical stability and transient density behavior; it
cannot establish that this terminal treatment represents the native protein.

Therefore, no 50--100 ps NPT witness, PfCRT WT/K76A/K76T extension, production
MD, trajectory QC, or MD-RRS is authorized at this stage. The next required
step is a documented biological/structural policy decision: either (i) validate
a loop-reconstruction protocol that removes the internal split, or (ii) provide
an explicit, literature-supported justification for the split and its terminal
patches/charges. If that gate is approved, the subsequent isolated witness
must record complete input hashes, terminal selections, net charge/electrostatic
checks, strict `grompp -maxwarn 0`, temperature/pressure/density/RMSD monitoring,
and zero true LINCS/NaN/fatal markers before any variant extension is considered.

Current scientific classification: `TECHNICAL_TOPOLOGY_AND_STABILITY_EVIDENCE_ONLY`;
`BIOLOGICAL_MODEL_VALIDATION = PENDING`.

## Closing section — 18 Aug 2026: both chains resolved

### Set-C pilot chain (production → QC → MD-RRS) — COMPLETE

- Production `15320` 16/16 (10 ns each, GPU A4000 `%1`); trajectory QC 16/16
  PASS; pilot MD-RRS `COMPUTED_WITH_COHORT_CONTRACT` (job `15386` after two
  fixed failures: 15384 GMXRC `set +u`, 15385 MDAnalysis `timespan`).
- Pilot result: PP-01/PP-02 MD_RRS = 100.0 (class A), saturated because
  `bound_fraction=1.000` for all 16 systems — ceiling, not affinity-equality
  proof. Full-cohort mode (17 candidates/136 systems) remains NOT_COMPUTED by
  design.
- See `setc_post_production_runbook.md` closing section and
  `setc_md_rrs_execution_runbook.md` status.

### PfCRT 114–122 reconstruction — BIOLOGICAL gate now PASSED (technical)

The former internal COOH/NH2 split at the 114–122 gap (the reason for the
`BIOLOGICAL_MODEL_VALIDATION = PENDING` verdict above) has been resolved by a
restrained OpenMM junction-repair protocol, then validated under the canonical
GROMACS policy:

1. `scripts/p2_pfcrt_junction_repair_openmm.py` — rigid Kabsch graft could not
   satisfy both junctions (C(113)-N(114): 0.85–3.26 Å, C(122)-N(123): 3.5–5.5
   Å; 0/16 passing). OpenMM position restraints on the core + harmonic C-N
   restraints at 1.33 Å + L-BFGS + 10 K relaxation → **15/15 unique
   PASS_GEOMETRY** (junction bonds 1.32–1.37 Å, loop sequence NKKGNSKER
   unchanged, no core clash).
2. Selected `candidate_model_03_seed_001` (loop pLDDT 55.2).
3. `scripts/p2_pfcrt_canonical_md_witness.sh` — canonical CHARMM36m/TIP3P
   pdb2gmx: **1 continuous chain** (VAL47 NH2 → ASN405 COOH, no internal
   split), 359 residues; grompp RC=0; solvation + ions; EM + NVT completed
   (see `results/md_systems/pfcrt_md_witness_20260818/`).

Updated scientific classification (18 Aug): `GEOMETRY_REPAIR_WITNESS_ONLY` +
`CANONICAL_POLICY_TOPOLOGY_CHECK_PASS` — the loop is geometrically sound and
processable under the P2 policy. This remains a **technical** validation:
no production MD on the repaired PfCRT, no binding/affinity/RRS, no Set-C
promotion from the reconstruction.

**Long equilibration (19 Aug)**: job `15387` ran 1 ns NPT (Parrinello-Rahman,
310.15 K) from the 100 ps witness checkpoint but hit the 3 h walltime at step
392240 (~784 ps, 6.28 ns/day on 8 CPU threads) and checkpointed cleanly.
Job `15388` resumed from that checkpoint (`mdrun -cpi`) to complete the full
1 ns. Convergence manifest: `results/md_systems/pfcrt_eq1ns_20260818/
equilibration_convergence_manifest.json`. Still a technical stability witness
— no production, no binding/affinity/RRS claim.
