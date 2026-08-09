# V5 isolated docking-RRS reproduction — launch provenance

- Date: 2026-08-09
- Phase: `PRE_SUBMISSION_DEVELOPMENT`
- Output root: `results/exploratory/rrs_reproduction_20260809/`
- PfDHFR job: `15013`
- PfCRT job: `15014`
- Post-processing job: `15015`
- Dependency: post-processing uses `afterok:15013:15014`.
- Worker: `scripts/p1_v5_rrs_reproduction_20260809.sbatch`
- Post-processor: `scripts/p1_v5_rrs_reproduction_post_20260809.sbatch`
- Panel: 17 candidates, uniform protein-only receptor protocol, target-specific fixed anchors, rank-1 geometric gate; this is an isolated V5-protocol reproduction, not a common-protocol replication of canonical P2.
- Isolation: no writes to `results/rrs_pilot/`, P2 canonical RRS files, or V6 canonical derived files.
- Promotion boundary: exploratory only; no V5/P2 class, correlation, consensus, or manuscript claim is changed automatically.
- Failure policy: any worker failure prevents post-processing through the `afterok` dependency; partial outputs remain diagnostic and are not aggregated.

## Completion record

- **Status: COMPLETED (9 August 2026)** — both workers finished successfully and post-processing ran through the `afterok` dependency.
- Vina raw scores: **136/136** rows (85 PfDHFR + 51 PfCRT), **0 failure.json**.
- Per-target status: `VINA_GRID_DOCK_MUTANT_PANEL_RANK1_VERIFIED` (seed 0, exhaustiveness 16, num_modes 9).
- RRS recomputed: **34 rows (17 per target)**, distribution **A*: 12, A: 5 per target — identical to the archived pilot** (internal V5-protocol reproducibility confirmed).
- Provenance JSON confirms `canonical_outputs_modified=false` and `canonical_p2_rrs_overwritten=false`.
- Interpretation boundary unchanged: exploratory, `PRE_SUBMISSION_DEVELOPMENT_NOT_SUBMISSION_READY`; not comparable to canonical P2 without protocol reconciliation.
