# P2 SLURM and workflow audit — 12 August 2026

## Scope

This is the active static audit of the P2 `scripts/*.sbatch` launchers, the Set-C MD workflow, trajectory QC, MD-RRS wrapper, and current queue state. Historical job narratives remain in `docs/archive/` and the dated Set-C runbooks; they are not executable instructions.

## Current verdict

**Static configuration: PASS with one critical fix applied.** All 23 P2 SLURM launchers pass `bash -n`; the referenced Set-C Python workflow/QC/RRS scripts pass compilation in `malaria_md`; absolute project paths and the active GPU witness paths resolve. No script was submitted or cancelled during this audit.

The critical fix was array ownership. `p2_setc_production.sbatch` previously selected a system with a Bash list while `p2_setc_md_workflow.py --array-index` selected from sorted filesystem directories. Witness and archive directories could therefore remap an array task silently. The production launcher now passes the exact `--system-name "$SYS"`; the workflow rejects simultaneous `--system-name`/`--array-index` and validates that the requested name belongs to the deterministic selected panel. Legacy index mode remains deterministic and no longer consults filesystem sorting. The QC boundary now independently revalidates system/force-field identity and topology dependency hashes.

## Live jobs and boundaries

- `15270`: completed GPU witness `PP-01_PfDHFR_WT` (10 ns; 28.169 ns/day; no fatal/LINCS/NaN indicators); one-system evidence only.
- `15262`: completed GPU benchmark; mixed offload (`-nb gpu -pme gpu -bonded cpu -update cpu`) was stable.
- `15259/15260`: stopped CPU witness/QC; partial output is explicitly non-canonical.
- `15264/15266/15268`: pre-execution failures; no production trajectory was generated.
- Historical `15106/15111/15117/15118/15119/15120` records are not the active chain and must not be reused as current dependencies.
- Set-C MD-RRS remains `NOT_COMPUTED`; the witness cannot be promoted to a cohort result. The new `p2_setc_gpu_production.sbatch` is static-only until preparation/equilibration preflight passes for all 16 systems.

## Checks performed

### Launchers and resources

- All P2 `*.sbatch` files pass `bash -n`.
- Set-C array launchers use explicit `--ntasks`, `--cpus-per-task`, memory, time, and array limits.
- GPU launchers request `--gres=gpu:1`; the stable production flags keep update/constraints on CPU.
- Log directories are created before submission for the active launchers; output paths are versioned for witness runs.
- Set-C production requires the execution guard and uses explicit per-task output/manifests.

### Dependency semantics

- Reusable post-production QC has no literal dependency directive or historical job ID. Actual production/equilibration IDs must be passed via `--dependency` and exported provenance variables at submission.
- `afterany` is acceptable for independent salvage production tasks, but it does **not** make a partial panel eligible for MD-RRS. QC/RRS remain fail-closed on incomplete or non-PASS rows.
- The current `p2_setc_qc_and_md_rrs.sbatch` uses explicit `if ...; then ... else ... fi` handling, so terminal QC/MD-RRS failure manifests are written despite `set -euo pipefail`.

### Cohort contracts

- Pilot: PP-01/PP-02 × PfDHFR/PfCRT mutation states = 16 systems and 16 QC rows; output ID/path is `P2_SET_C_MD_RRS_PILOT_PP01_PP02` / `md_rrs_pilot_PP01_PP02.csv`.
- Full cohort: 17 candidates × 8 states = 136 systems/QC rows; output is the canonical full-cohort MD-RRS path.
- `p2_setc_md_rrs.py --cohort-mode` enforces the selected cardinality and refuses mixed/stale candidate hashes. Pilot output cannot overwrite the full output.

## Residual safeguards before a new array submission

1. Complete and QC the declared pilot or full cohort; do not mix the estimands.
2. Supply actual job IDs from the new submission in the post-production wrapper; never copy IDs from historical runbooks.
3. Verify that the system-order/candidate manifest used to prepare the panel matches the selected candidate hash.
4. At trajectory QC, the prepared system/force-field manifest and topology dependency hashes are revalidated for every candidate/state before a trajectory can be accepted; a mismatch is emitted as `MANIFEST_INVALID` and remains fail-closed.
5. Preserve versioned outputs and update the active DAR before promoting any MD-derived claim.

## Implementation checkpoint — 12 August 2026

- Added `scripts/p2_setc_gpu_production.sbatch`: serial `%1` GPU array, explicit system ownership, mixed-offload flags, and execution authorization.
- Extended `p2_setc_md_workflow.py` with an explicit `--backend gpu` mode and topology-include copying/hash provenance; CPU remains the default.
- Read-only pilot preflight (`results/set_c_md/preflight_20260812/`) returned **0/16 ready** and **FAIL_CLOSED** because the canonical `results/md_systems/set_c` root lacks complete `complex.gro`, `topol.top`, `forcefield_manifest.json`, and/or equilibrated `npt.gro` inputs. No production job was submitted.
- The next executable step is OpenFF preparation/equilibration for all 16 systems; only after a fresh preflight reports 16/16 ready may the GPU launcher be submitted with the actual equilibration job ID.

## Scientific boundary

Docking-derived RRS/polypharmacology remains the canonical P2 result. MD-RRS is a distinct trajectory-derived estimand and remains unavailable until the declared cohort passes complete QC with matching hashes, a single analysis rule, consistent duration/frame protocol, and terminal provenance.
