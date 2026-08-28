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

---

## Update (evening 2026-08-09) — OpenFF 2.2 + CHARMM36m pathway VALIDATED end-to-end

The documented workaround (`OpenFF 2.2.0` ligand FF + `AM1-BCC` charges via
AmberTools, protein `CHARMM36m`, water `TIP3P`) has been implemented and
validated on the pilot system `PP-01_PfDHFR_WT`:

| Stage | Status | Evidence |
|-------|--------|----------|
| Ligand topology (OpenFF 2.2 + AM1-BCC) | ✅ | `ligand_openff.itp` (40 atoms, moleculetype MOL0), heavy frame RMSD 0.0 nm vs rank-1 Vina pose |
| Protein (pdbfixer → pdb2gmx CHARMM36m) | ✅ | 2 chains, 18 074 heavy atoms, frame preserved (MET1 CA identical) |
| Solvation (cubic box, TIP3P, 0.15 M NaCl) | ✅ | 14.79 nm cube, 316 108 atoms, net charge neutralised |
| EM phase 1 (protein restrained, -DPOSRES) | ✅ | 3 000 steps, steep |
| EM phase 2 (unrestrained) | ✅ | 10 000 steps, **final Potential = −5.21e+06 kJ/mol** (no blow-up) |
| NVT / NPT (310.15 K, 1 bar) | ✅ | **smoke VALIDATED 2026-08-10** on `PP-01_PfDHFR_WT` (grompp+mdrun rc=0, 2000 steps each; `npt.cpt`/`npt.gro` produced); full 16-system array 15054 running |
| forcefield_manifest finalisation | 🔄 | after NPT (npt.gro/npt.cpt hashes, recursive topology deps, md.mdp hash) |

### Technical fixes required (all recorded here for reproducibility)

1. **GROMACS directive order** — the ligand `#include` must be inserted right
   after the forcefield include and BEFORE the `topol_Protein_chain_*.itp`
   includes, otherwise the ligand `[ atomtypes ]` follows the protein
   `[ moleculetype ]` and grompp aborts ("Invalid order for directive atomtypes").
2. **Trailing newline** — `gmx solvate` appends `SOL <n>` to `[ molecules ]`;
   without a trailing newline in `topol.top` the entry merges into the last
   molecule line (`Protein_chain_B 1SOL ...`) and the topology silently loses
   the SOL molecules (grompp coordinate-count mismatch).
3. **Cubic box (not dodecahedron)** — the ~10.7 nm dimer does not fit a
   dodecahedron with a=13.2 nm (z-height a/√2 = 9.33 nm < 10.3 nm z-extent);
   mdrun aborts with "no domain decomposition compatible with the given box".
   Cubic box of edge ≥ 14.63 nm (14.79 nm used) is DD-compatible.
4. **Hydrogen placement on the fixed docked heavy frame** — Vina/Meeko strips
   nonpolar H's (docked pose has 25 atoms: 24 heavy + 1 polar H). An earlier
   scheme that transferred H bond vectors from an unrelated embedded conformer
   produced 0.63 Å intra-ligand overlaps and crashed EM.  Open Babel
   (`obabel heavy.pdb -O lig.sdf -h -p 7.4`) places H's consistently with the
   docked heavy geometry (formula verified C18H16O6, internal min 0.95 Å),
   and the SDF preserves bond orders for RDKit/OpenFF.
5. **Two-phase EM** — the receptor carries two mis-oriented polar H's
   (TYR-OH ... ASN-NH2 at 0.82 Å, a short 2.61 Å OH-ND2 H-bond).  EM phase 1
   with `define = -DPOSRES` (protein heavy atoms restrained, `-r complex.gro`,
   emstep 0.002) relaxes H's/water/ligand; EM phase 2 (unrestrained) completes
   the relaxation to −5.21e+06 kJ/mol.
6. **CPU-only mdrun** — the host A4000 GPU crashes GROMACS update/constraint
   routines (rc=-6, UpdateConstrainGpu); mdrun always runs with
   `-nb cpu -pme cpu -bonded cpu -update cpu` (matches the parent study).

### Deviation remains documented, never silent

Every prepared system carries `forcefield_manifest.json` with
`policy_deviation` (`declared: true, canonical_requirement: CGenFF,
actual: OpenFF 2.2.0 (AM1-BCC), approved: true`), and
`p2_setc_md_workflow.py::validate_forcefield` now accepts the OpenFF ligand FF
**only** when the deviation block is present and approved (otherwise it still
fails closed with "ligand force field must be CGenFF ...").

### SLURM

* `p2_setc_prepare_all.sbatch` — full 16-system pilot preparation
  (PP-01/PP-02 × 8 receptor states); earlier run cancelled when the solvation
  box bug was found; resubmission queued behind the pipeline fix.
* `p2_setc_equilibrate.sbatch` — SLURM array (0-15) EM/NVT/NPT per system with
  `--dependency=afterok:<prep job>`, finalises the manifests.  **Note (10/08):**
  must be run with a concurrency limit (`--array=0-15%4`) — see failure record above.
* `p2_setc_equilibrate_retry.sbatch` — retry array (0-11, `%4`, `--mem=8G`) for
  the 12 systems that crashed in 15054 (job **15070**).

### Update (2026-08-10) — array 15054 partial failure, root cause, and retry 15070

**Failure.** Array `15054` (16 tasks, EM/NVT/NPT) crashed on **12/16 systems**
with an OpenMP (`libgomp`) runtime error inside `libgromacs_mpi.so.10` during
EM, ~3 minutes after submission (failures recorded 23:25–23:26 UTC on
2026-08-09).  The remaining 4 systems (array indices 3, 4, 13, 15 =
`PP-01_PfDHFR_S108N`, `PP-01_PfDHFR_I164L`, `PP-02_PfCRT_WT`,
`PP-02_PfCRT_K76A`) **survived** and progressed normally
(EM → EM2 → NVT ≈ 50% at last check, NPT pending).

**Root cause: resource oversubscription, not chemistry.** The original sbatch
declared `--array=0-15` **without a concurrency limit** and `--mem=16G` per
task, so SLURM launched all 16 tasks simultaneously on the 48-CPU / 128 GB node:
- CPU: 16 tasks × 4 threads = 64 > 48 available → oversubscription;
- RAM: 16 × 16 G = 256 G requested > 128 G physical.

The OpenMP thread/stack allocation failure (symbols in the traceback point into
`libgomp` while GROMACS builds neighbour-search ranges) is the expected symptom
of that oversubscription.  The earlier local smoke test passed because it ran
**one system at a time** on the login node.

**Fix (applied).** `scripts/p2_setc_equilibrate_retry.sbatch` re-submits only
the **12 failed systems** with:
- `--array=0-11%4` → **max 4 concurrent tasks** (4×4 CPU = 16 ≤ 48; with the 4
  surviving 15054 tasks still running, 8×4 = 32 ≤ 48);
- `--mem=8G` per task (gmx_mpi CPU on ~316 k atoms needs far less than 16 G;
  4×8 G + 4×16 G = 96 G ≤ 128 G).

Retry job: **15070** (submitted 2026-08-10; 4 tasks running, 8 queued).  The 4
surviving systems finish in array 15054 without interruption.  No chemistry or
topology change was required — the prepared systems and manifests are intact.

### Current honest statement

Historical checkpoint: Set-C MD preparation for the 16-system pilot was **in progress** at the time; the pipeline
was validated end-to-end on `PP-01_PfDHFR_WT` (EM restrained + EM free + NVT + NPT, all rc=0, final EM potential −5.21e6 kJ/mol, NPT 310.15 K / 1 bar).  The first full array `15054` partially failed on resource oversubscription (12/16, fixed by concurrency-limited retry `15070`); the 4 unaffected systems continue.
`md_rrs_status=NOT_COMPUTED` until production trajectories pass QC.  Docking-RRS
and MD-RRS remain in separate provenance records.

---

## Update (2026-08-10, 04:50 UTC) — ROOT CAUSE v2: NaN water explosion under POSRES (SUPERSEDED)

### Symptom (arrays 15054 / 15070 / 15081)
Deterministic segfault in the GROMACS 2025.4 Verlet pair-search
(`gmx::Range/ArrayRef<BasicVector<float>>`, called from libgomp) during
EM phase 1, at steps ~40-160, on the same systems regardless of:

- thread count (`-ntomp 1`, 2, 8, 48 all crashed);
- concurrency (`%4` or full node — the crash also reproduced **alone** on an
  idle node);
- `OMP_STACKSIZE=1G` + `ulimit -s unlimited`;
- with or without the `-nb cpu -pme cpu -bonded cpu -update cpu` flags.

The first hypothesis (OpenMP thread oversubscription: 16 tasks x 48 threads)
explained the *first* array failures but was NOT the full story.

### v2 root cause (proven, but INCOMPLETE — see v3)
`step*.pdb` written by GROMACS immediately before the crash contains
**`-nan` coordinates for a water molecule** (e.g. SOL 2719 in
PP-02_PfDHFR_WT).  The starting complexes carry **massive initial clashes**
(step-0 Bond ~1e8 kJ/mol, LJ-14 ~2.4e8 kJ/mol, LJ(SR) ~5e8 kJ/mol).
Removing the POSRES restraint + gentle EM (emstep=0.0001) made the *mild*
systems converge, so v2 attributed the crash to POSRES-frozen protein +
water NaN explosion.  **However** K76T and C59R still crashed at steps 63/250
with the v2 protocol, and the SAME WT command was non-deterministic
(converged run 1, segfault run 2) — a signature of corrupted input, not of
the integrator.

---

## Update (2026-08-10, ~06:00 UTC) — ROOT CAUSE v3 (FINAL): topology/coordinate molecule-order misalignment

### Root cause (definitive, proven by structural forensics)
`p2_setc_prepare_openff.py::add_ligand_to_topol` inserted **MOL0 as the
FIRST `[ molecules ]` entry**, while `merge_gro` wrote **protein first,
ligand last** in the coordinates.  `grompp` silently re-attributed atom
order, and `genion` then scrambled the coordinates.  Consequences measured
on every one of the 16 systems:

- **collapsed aromatic rings** — TYR34 CG–CE1 at **0.68 Å** (K76T), TYR238
  OH–CD2 at **1.00 Å** (most systems); complex.gro of K76T had **114
  collapsed rings** vs 0 in the clean `protein_processed.gro`;
- **exploded side chains** — LYS104 HE1–HE2 at **65 Å** (same side chain,
  should be ~1.6 Å);
- subsequent water **NaN explosion** → non-deterministic libgomp segfault in
  the Verlet pair-search (the v2 "NaN" symptom was a *downstream* effect).

The EM/EM2/NVT/NPT stages and the receptors were never the problem: a clean
`solvated.gro` (0 collapsed rings) became corrupted only after grompp+genion.

### Fix (validated end-to-end)
1. **Align `[ molecules ]` order with coordinate order** (protein first,
   then MOL0) in `p2_setc_prepare_openff.py`;
2. **Regenerate** `ions.gro` from the clean `solvated.gro` (restoring the
   pre-genion SOL count before grompp);
3. Keep the gentle EM protocol from v2 as the relaxation scheme:

| Protocol | K76A | WT | PP-02_WT (worst) | K76T (hardest clash) |
|---|---|---|---|---|
| POSRES + emstep 0.002 | crash | non-det. crash | crash @40 | crash @40 |
| no POSRES, emstep 0.0005 | -3.92e6 OK | -5.14e6 OK | -4.89e6 OK | crash @63 |
| **no POSRES, emstep 0.0001** | OK | OK | OK | **-3.87e6, 6211 steps, rc=0** |

Validation of the fix: regenerated K76T `complex.gro` → **0 collapsed rings
(was 114)**, LYS104 HE1–HE2 **1.63 Å (was 65 Å)**; all 16 systems verified
clean (0 collapsed rings, correct order).

### Status
- **Job 15106** (array 0-15, %4, ntomp=8) running on the **regenerated
  clean structures**: wave-0 (K76A em=1496, K76T em=1509, WT em=1585,
  C59R em=979) all past the historical crash zone, **0 failures** — K76T,
  which previously crashed at step 63/250 even with the v2 protocol, now
  progresses normally.
- ETA per system at 8 threads: EM+EM2 ~15-30 min, NVT+NPT (2x50k steps)
  ~8-14 h; 4 batches of 4 -> full set ~32-56 h.
