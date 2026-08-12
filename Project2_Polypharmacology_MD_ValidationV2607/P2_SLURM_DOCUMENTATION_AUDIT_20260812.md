# P2 SLURM and documentation audit — 12 August 2026

## Scope and verdict

This audit covers all P2 `*.sbatch` files, the Set-C trajectory-QC/MD-RRS scripts, `AGENTS.md`, and the seven files under `Project2_Polypharmacology_MD_ValidationV2607/docs/`.

**Verdict:** the shell/Python syntax is clean, and the ordinary `python scripts/...` paths resolve correctly after the documented `cd` to the P2 project root. However, the Set-C MD-RRS chain is **not execution-ready** because its dependency metadata and its cohort cardinality are inconsistent with the active pilot design. No job was submitted, cancelled, or modified during this audit.

## Static checks completed

- All P2 SLURM scripts pass `bash -n`.
- All Python scripts in `Project2_Polypharmacology_MD_ValidationV2607/scripts/` pass `py_compile` with `/home/nanaengo/miniforge3/envs/malaria_md/bin/python`.
- Commands such as `python scripts/p2_setc_equilibrate.py` and `python scripts/p2_setc_md_workflow.py` are valid because the scripts `cd` to the P2 project root before invocation.
- `SCRIPTS_DIR="scripts"` in `p2_setc_qc_and_md_rrs.sbatch` is also valid at runtime after that `cd`; a raw-text resolver that does not expand shell variables produces a false missing-path warning.
- The current live queue agrees with the active status boundary: `15259` is running and `15260` is pending on its dependency. These are an isolated `PP-01_PfDHFR_WT` witness, not a cohort MD-RRS result.

## Critical findings

### C1 — Reusable QC/MD-RRS wrapper contains obsolete hard-coded job identity

`p2_setc_qc_and_md_rrs.sbatch` contains:

- `#SBATCH --dependency=afterok:15111`
- provenance fields identifying production `15111` and equilibration `15106`.

The active documentation explicitly marks 15106/15111/15117 as superseded. The wrapper therefore cannot be safely submitted as a current generic post-production job. Its dependency must be supplied at submission time or through a verified chain manifest; job IDs must be recorded from the actual submission, never copied into the script.

### C2 — Pilot cardinality and MD-RRS cardinality are mathematically incompatible

The prepared Set-C pilot has:

- 2 candidates (`PP-01`, `PP-02`);
- 8 target states per candidate (5 PfDHFR + 3 PfCRT);
- **16 systems**, corresponding to 16 QC rows if one trajectory is accepted per state.

`p2_setc_md_rrs.py`, however, hard-codes:

```text
expected_rows = 17 * (5 + 3) = 136
```

and requires all 17 Set-C candidates to be represented. Therefore the current 16-system pilot can never pass the current MD-RRS gate, even with 16 perfect trajectories. This is the main scientific/technical blocker.

Two valid designs exist, but they must not be conflated:

1. **Pilot estimand:** implement an explicitly labelled 16-row, two-candidate MD-RRS analysis and state that the remaining 15 candidates have docking-RRS only; or
2. **Full-cohort estimand:** prepare and run 136 candidate/state systems before computing the 17-candidate MD-RRS.

No code change should select between these designs implicitly.

### C3 — `afterany` resilience is inconsistent with the fail-closed MD-RRS contract

The production script intentionally permits `afterany` so one failed equilibration task does not block independent production tasks. That is defensible for salvageable per-system trajectories, but the comments state that downstream QC “tolerates missing systems.” The MD-RRS script does not: it refuses any non-PASS row and requires a complete panel. The safe interpretation is:

- `afterany` may launch a **QC-only inventory**;
- it must not imply that MD-RRS can be computed on a partial panel;
- a separate completeness gate must stop manuscript-facing MD-RRS integration unless the selected pilot/full-cohort contract is satisfied.

### C4 — QC hashes trajectories but does not enforce the full prepared-system manifest

`p2_setc_trajectory_qc.py` records trajectory and TPR hashes and the candidate-file hash. Its docstring describes validation against expected topology/coordinate provenance, but the implementation does not independently verify every `system_manifest.json` and `forcefield_manifest.json` identity/hash before accepting a row. That check exists in the MD workflow preflight but is not repeated at the QC boundary. For reviewer-grade provenance, QC should consume and verify the system manifest for every accepted trajectory.

### C5 — Array ownership depends on filesystem sorting

`p2_setc_production.sbatch` uses a hand-written `SYS_DIRS` array, while `p2_setc_md_workflow.py --array-index` derives ownership from `sorted(SYSTEM_ROOT.iterdir())`. This currently agrees for the 16 expected directory names, but an extra directory or a renamed directory would silently map an SLURM task to the wrong system. The canonical system manifest should define the array order, and both layers should validate the same list/hash before production.

### C6 — Controlled failure diagnostics are partly unreachable under `set -e`

`p2_setc_qc_and_md_rrs.sbatch` enables `set -e` and then captures `$?` after the QC and MD-RRS commands. If either command fails, the shell exits before the custom `QC_RC`/`MD_RRS_RC` handling and before a final provenance record is written. This does not create a false PASS, but it weakens failure diagnostics. Use explicit `if command; then ... else ... fi` blocks (or temporarily disable `errexit` around the command) so every failed chain writes a terminal manifest.

## `AGENTS.md` assessment

`AGENTS.md` is substantially improved and is appropriately short: it identifies the canonical DARs, separates P1/P2/P3/P4/P5, preserves the docking-RRS versus MD-RRS boundary, records the OpenFF policy deviation, and prohibits claims from incomplete jobs. Its current P2 live status is consistent with the queue check (`15259` running; `15260` pending).

It is not yet fully optimal because it does not state two operational invariants that the scripts currently violate:

1. **Cohort cardinality must be declared once and match preparation, QC, MD-RRS, and manuscript estimand** (pilot 16 versus full cohort 136).
2. **Reusable SLURM wrappers must not contain literal historical job IDs**; dependencies and provenance IDs must be injected from the actual submission chain.

These rules should be added only after the corresponding script contract is corrected. No other obsolete scientific claim was found in the active `AGENTS.md`; its false-positive “missing paths” are values, labels, or shell/provenance syntax rather than file references.

## `Project2/docs/` assessment

The seven files under `Project2_Polypharmacology_MD_ValidationV2607/docs/` are historical orientation/audit material, not active sources of truth:

- `AUDIT_CRITIQUE_260704.md` and `audit_project_260528.md`: old audit statuses and 20-candidate framing;
- `METHODS.md`: historical 300 K/200 ns and old HPC-run narrative;
- `polypharmacology_investigation_reportV2.md`: July execution narrative and pre-current cohort framing;
- `ROADMAP.md`: May roadmap with “scripts ready/pending” statuses;
- `SITUATION_REPORT.md`: July cross-project status, including obsolete P3 status;
- `README.md`: directory orientation with legacy links/status language.

These files should not be deleted without preserving provenance, but they should either receive a visible `HISTORICAL — DO NOT USE AS SOURCE OF TRUTH` banner or be moved into the project documentation archive. Numerical and operational decisions must continue to come from `BMAD_Q1_DATA_ANALYSIS_REPORT.md`, `P1_P5_RRS_POLYPHARMA_ROADMAP.md`, and the active P2 README/runbook checkpoint.

## Prioritized P2 implementation plan

### P0 — resolve before any full-panel MD-RRS submission

1. Choose and document the estimand: 16-system pilot MD-RRS or 136-system full-cohort MD-RRS.
2. Replace the hard-coded `15106/15111` dependency and provenance fields with actual-chain parameters and a submission manifest.
3. Add a cardinality gate shared by preparation, production, QC, MD-RRS, and manuscript integration.
4. Make the downstream result status explicit: `PILOT_MD_RRS`, `FULL_COHORT_MD_RRS`, or `NOT_COMPUTED`; never infer one from directory count.

### P1 — reproducibility and failure handling

5. Verify system and force-field manifest identity/hashes at trajectory QC, not only at production preflight.
6. Replace filesystem-sort array ownership with a frozen, hashed system-order manifest.
7. Make QC/MD-RRS failure handling write a terminal provenance manifest despite `set -e`.
8. Add a read-only preflight test that creates synthetic 16-row and 136-row contracts and confirms that only the selected design passes.

### P2 — documentation cleanup

9. Add historical banners or archive the seven legacy `Project2/docs/` files; do not use them for current claims.
10. Update `P2_MD_RRS_INTEGRATION_PLAN.md` so its historical commands are not mistaken for an executable current chain.
11. Add the two cardinality/dependency invariants to `AGENTS.md` after the implementation contract is fixed.

## Boundary for manuscript use

Until the selected contract passes trajectory QC with matching hashes and complete provenance, P2 may report the canonical docking-derived RRS/polypharmacology results and the separate historical parent-study MD evidence. It must not report Set-C MD-RRS, extrapolate the 16-system witness to all 17 candidates, or replace docking-RRS with MD-RRS.
