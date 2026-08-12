# P2 Set-C implementation checkpoint — 12 August 2026

## Implemented

- `scripts/p2_setc_md_workflow.py` now supports an explicit `--backend gpu` mode using the benchmarked mixed-offload flags:
  `-nb gpu -pme gpu -bonded cpu -update cpu`.
- Production staging copies local topology `#include` dependencies into each unique run directory and records their SHA-256 values. Missing, unsafe, or unstated dependencies fail closed.
- `scripts/p2_setc_gpu_production.sbatch` is a serial GPU array (`0-15%1`) for the predeclared pilot: PP-01/PP-02 × PfDHFR/PfCRT mutation states (16 systems). Each task owns an explicit system name and a task-specific output/provenance directory.
- CPU mode remains the default and is unchanged for reproducibility.

## Active SLURM chain — 12 August 2026

- **15274 (`p2_setc_prep_all`)** was submitted at 17:05 UTC on `penavoraserver` and is running in the `production` partition (10-hour limit).
- Output root: `results/md_systems/set_c_preparation_20260812_v1`.
- At the 17:10 UTC checkpoint, `PP-01_PfDHFR_WT` was complete (non-empty `complex.gro`, `topol.top`, `system_manifest.json`, and `forcefield_manifest.json`); `PP-02_PfDHFR_WT` was actively being built in a temporary work directory. The job is sequential by design (`--all`), not parallel.
- The only stderr output was the non-fatal `pkg_resources` deprecation warning from `openff.amber_ff_ports`; OpenFF/AmberTools AM1-BCC and Open Babel smoke tests passed, with no traceback or fatal marker.
- Based on the observed cadence, the remaining 15 systems are estimated at approximately 75–100 minutes, subject to molecular size and AM1-BCC cost. This is an operational estimate, not a scientific result.
- This versioned root is deliberately separate from the incomplete canonical `results/md_systems/set_c`; no existing system directory is overwritten.
- Equilibration `15275` has been submitted with `afterok:15274` and remains pending until preparation succeeds.
- Initial gate `15276` was cancelled before execution after review identified a candidate-panel/provenance ambiguity. Corrected gate `15277` has been submitted with `afterok:15275`; it asserts the fixed `PP-01`/`PP-02` panel, runs the aggregate preflight against this versioned root, and submits GPU production only for an exact `16/16` `READY_FOR_AUTHORIZED_EXECUTION` result. GPU production itself has not been submitted.

## Validation performed

- All P2 SLURM launchers pass `bash -n`.
- `p2_setc_md_workflow.py`, `p2_setc_trajectory_qc.py`, and `p2_setc_md_rrs.py` pass `py_compile` in `malaria_md`.
- Read-only pilot preflight (GPU backend, 12 August 2026) produced:
  `results/set_c_md/preflight_gpu_20260812/set_c_md_execution_manifest.json`.
- Preflight result: **FAIL_CLOSED**, **0/16 ready**. The canonical `results/md_systems/set_c` directories have candidate manifests, but the complete prepared topology/equilibration inputs are not present (`complex.gro`, `topol.top`, `forcefield_manifest.json`, and/or `npt.gro`/`npt.cpt`). No GROMACS production job was submitted.

## Witness boundary

Job `15270` completed one isolated `PP-01_PfDHFR_WT` 10-ns GPU witness at **28.169 ns/day** (5,000,000 steps; wall time 30,672.48 s), with no fatal/LINCS/NaN/infinite indicators in the terminal log scan. It validates the GPU execution path only. It is not a 16-system pilot result and does not produce MD-RRS.

## Next executable gate

1. Run the OpenFF 2.2.0 AM1-BCC preparation for all 16 systems into a new versioned root (for example `results/md_systems/set_c_preparation_20260812_v1`), with the approved deviation documented in every force-field manifest; do not overwrite the incomplete canonical root.
2. Run the 16-system equilibration array against that versioned root and record its actual SLURM job ID.
3. Re-run the read-only workflow preflight; require **16/16 ready**.
4. Submit `p2_setc_gpu_production.sbatch` with `--dependency=afterany:<actual-equilibration-job-id>` and the actual job ID recorded in the checkpoint.
5. After all terminal production artifacts exist, run mode-specific trajectory QC and then the pilot MD-RRS wrapper. Any missing or failed row keeps MD-RRS `NOT_COMPUTED`.

The canonical P2 manuscript remains docking-RRS/polypharmacology based. No MD-RRS claim is promoted from the witness or from an incomplete pilot.
