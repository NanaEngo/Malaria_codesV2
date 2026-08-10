# Set-C MD → MD-RRS Execution Runbook (16 systems)

**Cohort:** `P2_SET_C_POLYPHARM_17` — 2 candidates (PP-01, PP-02) × 8 receptor
states (PfDHFR WT/N51I/C59R/S108N/I164L + PfCRT WT/K76T/K76A) = **16 systems**.
**Authorized:** PI-approved OpenFF 2.2.0 (AM1-BCC) ligand FF deviation
(`policy_deviation.approved=true` in each `forcefield_manifest.json`).
**Status (10 Aug 2026):** preparation COMPLETE (16/16, structures regenerated
clean — ROOT CAUSE v3 fix); equilibration job **15106** running; production
MD not yet launched.

---

## Stage 0 — Equilibration (running)

- Job: **15106** (`p2_setc_equilibrate_final.sbatch`, array 0-15 `%4`,
  `-ntomp 8`, EM `emstep=0.0001` no-POSRES → EM2 → NVT → NPT 310.15 K/1 bar).
- Completion criterion per system: `npt.gro` + `npt.cpt` non-empty
  (and no `equilibration_failure.json`).
- ETA: ~8–14 h/system, 4 waves → **~12–16 h total**.

## Stage 1 — Production MD (10 ns × 16, parallel)

```bash
sbatch --dependency=afterok:15106 \
  Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_setc_production.sbatch
```

- Array 0-15 `%4`, `--time 48:00:00`; each task runs exactly one system via
  `p2_setc_md_workflow.py --array-index $SLURM_ARRAY_TASK_ID`
  (single system per task → no run-directory races; per-task
  `set_c_md_status_arrayNN.csv` / `..._manifest_arrayNN.json`).
- mdrun is CPU-only (`-nb cpu -pme cpu -bonded cpu -update cpu`; the A4000
  GPU crashes GROMACS update/constraint routines) and `-ntomp 8`.
- Output per system: `runs/<run_id>/replicate_1/production.{tpr,xtc,edr,gro,log}`.
- ETA: ~9–10 h/system × 4 waves ≈ **~40 h**.

## Stage 2 — Trajectory QC

```bash
python Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_setc_trajectory_qc.py
```

- Computes per system: protein–ligand heavy-atom minimum distance per frame,
  `bound_fraction` (frames < 5.0 Å), `n_frames`, `duration_ns`, trajectory/tpr
  SHA-256, `qc_status` (PASS / FAIL / NO_PRODUCTION_RUN).
- Predeclared analysis rule: `setc_p2_minheavy_5A_ge10percent_v1`
  (≥ 500 frames, ≥ 10 % bound fraction).
- Writes `results/set_c_md/set_c_trajectory_qc.csv` — the exact contract
  consumed by the MD-RRS step.

## Stage 3 — MD-RRS computation

```bash
python Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_setc_md_rrs.py \
  --qc-file results/set_c_md/set_c_trajectory_qc.csv \
  --min-wt-bound-fraction 0.10
```

- Definition (MD-derived, distinct from docking-RRS):
  `MD-RRS_i,m,t = 100 × bound_fraction_mut,t / bound_fraction_WT,t`,
  averaged only over targets whose WT bound fraction ≥ 0.10.
  Classes A*/A/B/C/D by the same operational thresholds as docking-RRS.
- Refuses non-PASS rows (fail-closed). Output:
  `results/set_c_md/md_rrs_classification.csv` + JSON manifest.

## Stage 4 — Manuscript integration

- Compare docking-RRS (per-target, `docking_mutants.csv`) with MD-RRS
  (bound-fraction based): report agreement/divergence per candidate and
  target; treat MD-RRS as the trajectory-derived resilience proxy.
- Update P2 manuscript and BMAD/P4/P5 reports with the 16-system
  trajectory panel (separate provenance column; never merged with
  docking-RRS).

---

## Provenance contract (non-negotiable)

- Every system dir must carry `system_manifest.json` (identity) and
  `forcefield_manifest.json` (FF + hashes) — already present for 16/16.
- Docking-RRS and MD-RRS stay in **separate columns and separate
  provenance records** (`metric_boundary` guard in the workflow manifest).
- No MD-RRS claim without trajectory QC PASS rows.
- All hashes bind candidate SMILES, topology, coordinates, and checkpoint.

## Key files

| Artifact | Path |
|---|---|
| Equilibration array | `scripts/p2_setc_equilibrate_final.sbatch` |
| Equilibration engine | `scripts/p2_setc_equilibrate.py` |
| Preparation (FF/order fix) | `scripts/p2_setc_prepare_openff.py` |
| Production array | `scripts/p2_setc_production.sbatch` |
| Production workflow | `scripts/p2_setc_md_workflow.py` |
| Trajectory QC | `scripts/p2_setc_trajectory_qc.py` |
| MD-RRS | `scripts/p2_setc_md_rrs.py` |
| Remediation/root cause | `results/set_c_md/set_c_preparation_remediation_20260809.md` |
