# Set-C MD → MD-RRS execution runbook

**Updated:** 18 August 2026
**Scope:** candidate-specific Set-C trajectories only; parent-study MD systems are excluded.
**Current status:** **Pilot contract COMPLETE (18 Aug 2026).** Production `15320` finished 16/16 (10 ns each, GPU A4000 `%1` throttle). Post-production wrapper `15386` ran trajectory QC → MD-RRS in pilot mode: **16/16 QC PASS** (rule `setc_p2_minheavy_5A_ge10percent_v1`), `md_rrs_status=COMPUTED_WITH_COHORT_CONTRACT`, manifest `post_production_manifest_pilot.json` (schema v3). Outputs: `set_c_trajectory_qc_pilot.csv`, `md_rrs_pilot_PP01_PP02.csv`. MD-RRS = 100.0 (class A) for PP-01 and PP-02 — saturated because `bound_fraction=1.000` for all 16 systems including mutants; the 10-ns window cannot resolve partial affinity loss, so class A is a ceiling, not an affinity-equality proof. Full-cohort (`full` mode, 17 candidates/136 systems) remains `NOT_COMPUTED` by design: that production contract has not been prepared. GPU witness `15270` and benchmark `15262` are stability evidence only. Wrong-root equilibration `15275`, gates `15293`/`15307`, stopped production arrays `15308`/`15313`/`15317`, and failed wrapper attempts `15384`/`15385` are retained as non-canonical provenance.

## Cohort contracts

| Mode | Candidates | Systems / QC rows | QC output | MD-RRS output | Manuscript meaning |
|---|---:|---:|---|---|---|
| `pilot` (default) | PP-01, PP-02 | 16 | `results/set_c_md/set_c_trajectory_qc_pilot.csv` | `results/set_c_md/md_rrs_pilot_PP01_PP02.csv` | Targeted trajectory check only; the other 15 candidates remain docking-RRS only |
| `full` | PP-01–PP-17 | 136 | `results/set_c_md/set_c_trajectory_qc_full.csv` | `results/set_c_md/md_rrs_classification.csv` | Full Set-C MD-RRS claim only after all 17 candidates pass |

The 16-system pilot is 2 candidates × PfDHFR (WT, N51I, C59R, S108N, I164L) and PfCRT (WT, K76T, K76A), with the predeclared 10-ns production protocol. The force-field policy deviation is explicit: OpenFF 2.2.0 AM1-BCC for ligands with CHARMM36m/TIP3P for the protein/solvent; each system must retain `policy_deviation.declared=true` and `policy_deviation.approved=true`.

### GPU stability verdict and serial-cohort plan

The completed GPU benchmark (`15262`) is the evidence used to select the production flags `-nb gpu -pme gpu -bonded cpu -update cpu`; it sustained 19.816 ns/day without fatal or LINCS errors. The live `PP-01_PfDHFR_WT` witness (`15270`) independently checks the equilibrated-input path: `grompp` passed, one A4000 is allocated, and the last audited production checkpoint was free of fatal/LINCS errors. This supports serial GPU production, but neither job authorizes a Set-C MD-RRS claim.

The cohort plan is:

1. Close 15270 and retain its hashes, log, checkpoint, energy output, and terminal status.
2. Preflight all 16 `system_manifest.json` and `forcefield_manifest.json` files; reject any missing, mismatched, or stale hash before production.
3. Run one production at a time on the single A4000: PP-01/PP-02 × PfDHFR (WT, N51I, C59R, S108N, I164L) and PfCRT (WT, K76T, K76A). Use explicit `--system-name` selection and versioned pilot output paths. Enforce serial execution with an array throttle `%1` or an explicit per-system dependency chain; never submit the GPU production array with `%4` on the single A4000. The pre-submission manifest must enumerate all 16 expected system names in deterministic order.
4. Use a controlled `afterany` chain for independent salvage: a failed system must be recorded as `NON-PASS` but must not silently block later systems. The aggregate pilot remains ineligible unless all 16 systems produce valid terminal outputs and pass QC. **Implemented and active:** `scripts/p2_setc_gpu_production.sbatch` provides `#SBATCH --gres=gpu:1`, `#SBATCH --array=0-15%1`, explicit `--system-name "$SYS"`, and the approved mixed-offload flags. Final gate `15319` passed and production `15320` is running serially.
5. Treat 19.816 ns/day as a conservative planning rate: 10 ns is approximately 12.1 h of GPU time per system, or approximately 8 days of raw GPU time for 16 systems, before setup/retry overhead. Replace this planning estimate only after the closed witness supplies a measured terminal rate.
6. Run per-system QC only as diagnostic output until the complete 16-row pilot is present; then run the mode-specific aggregate QC and MD-RRS wrapper.

Production stability acceptance requires non-empty `production.xtc`, `production.tpr`, checkpoint and log files; no fatal error, LINCS failure, NaN, or energy divergence; and matching system/force-field/topology hashes. A failed witness or cohort system revises the GPU verdict to `GPU_PATH_REQUIRES_REMEDIATION` and blocks MD-RRS.

## Active Set-C checkpoint — serial production (13 August 2026)

Preparation job `15274` is retained as terminal provenance; its versioned root `results/md_systems/set_c_preparation_20260812_v1` passed a fresh strict **16/16** inventory (`complex.gro`, `topol.top`, both manifests, and `pre_equilibration_audit.json=PASS`). The scheduler record for 15274 is no longer queryable because accounting storage is disabled.

The first equilibration attempt `15275` used the wrong legacy root and was cancelled; its 69-file hash inventory is retained at `results/set_c_md/noncanonical_eq_root_snapshot_20260812T194605Z.json`. It is non-canonical and must not enter QC or manuscript analysis. Corrected equilibration **15288** completed with explicit `P2_SETC_ROOT=results/md_systems/set_c_preparation_20260812_v1`: all 16 tasks finalized `npt.gro`/`npt.cpt` with `rc=0`.

Gate **15312** passed the exact `16/16` `READY_FOR_AUTHORIZED_EXECUTION` preflight. Production `15313` was stopped after `grompp` passed but GROMACS 2025.4 rejected the unsupported `mdrun -seed` option. The launcher has been corrected; production `15317` was also stopped after a 1000-fold ns-to-step conversion error was detected. The final MDP now requests exactly 5,000,000 steps for 10 ns, and a 10-step GPU smoke test passes. Final gate `15319` passed 16/16 and production `15320` is active with `%1` serialization; task 0 confirms the exact 10-ns protocol and GPU offload without fatal/LINCS errors. `md_rrs_status=NOT_COMPUTED` until all 16 trajectories pass QC. *(Historical 13-Aug status: since superseded — production `15320` finished 16/16, QC 16/16 PASS and pilot MD-RRS `COMPUTED_WITH_COHORT_CONTRACT` on 18 Aug; see Current status above.)*

## Preconditions

1. Candidate-specific `system_manifest.json` and `forcefield_manifest.json` are present and identity/hashes pass in the new versioned root. The historical 0/16 read-only preflight applies only to the incomplete canonical root `results/md_systems/set_c`; the active versioned root contains the completed 16/16 equilibration outputs, while production `15320` remains in progress.
2. The actual equilibration and production SLURM IDs are recorded at submission time; no historical ID is copied into a reusable script.
3. Production trajectories contain non-empty `production.xtc` and `production.tpr` files.
4. The selected contract is declared explicitly through `P2_SETC_COHORT_MODE`.
5. No manuscript claim is updated from an incomplete, witness-only, or failed chain.

## Submission of the post-production chain

After the actual production job has completed, submit the wrapper with its real IDs:

```bash
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
EQ_JOB_ID=<actual-equilibration-job-id>
PROD_JOB_ID=<actual-production-job-id>
# Use afterany so a terminal failed production still writes the fail-closed manifest.
# The wrapper itself must reject missing/non-PASS rows and must not emit MD-RRS.
# PROD_JOB_ID must be the newly validated GPU array, not the CPU launcher or a historical ID.
sbatch --dependency=afterany:${PROD_JOB_ID} \
  --export=ALL,P2_PRODUCTION_JOB_ID=${PROD_JOB_ID},P2_EQUILIBRATION_JOB_ID=${EQ_JOB_ID},P2_SETC_COHORT_MODE=pilot \
  scripts/p2_setc_qc_and_md_rrs.sbatch
```

Use `P2_SETC_COHORT_MODE=full` only after the 17-candidate/136-system production contract has been prepared and independently checked. The wrapper writes a mode-specific post-production manifest and refuses missing job IDs. For the pilot, aggregate QC/MD-RRS must not be launched merely because one production finishes: all 16 declared systems must be represented first. Per-system diagnostic QC may run earlier, but it cannot produce or overwrite `md_rrs_pilot_PP01_PP02.csv`.

## Direct QC and MD-RRS commands

The wrapper is preferred because it binds the job IDs and output paths. For a controlled manual run, set the mode-specific paths explicitly:

```bash
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607

export P2_SETC_ROOT="$PWD/results/md_systems/set_c_preparation_20260812_v1"
export P2_SETC_QC_OUTPUT="$PWD/results/set_c_md/set_c_trajectory_qc_pilot.csv"
python scripts/p2_setc_trajectory_qc.py \
  --bound-angstrom 5.0 --min-frames 500 --min-bound-fraction 0.10 --max-frames 2000

python scripts/p2_setc_md_rrs.py \
  --qc-file results/set_c_md/set_c_trajectory_qc_pilot.csv \
  --cohort-mode pilot \
  --output results/set_c_md/md_rrs_pilot_PP01_PP02.csv
```

The full-mode filenames are `set_c_trajectory_qc_full.csv` and `md_rrs_classification.csv`, with `--cohort-mode full`. Never point pilot mode at the canonical full-cohort output.

## Fail-closed gates

Trajectory QC and MD-RRS must agree on one declared `analysis_rule_id`, one duration, and one frame-count protocol. Every accepted row must have `qc_status=PASS`, valid 64-character SHA-256 hashes, existing trajectory/TPR files, and a candidate-file hash matching the canonical Set-C file.

- Pilot: exactly 16 unique candidate/target/mutation rows and both `PP-01` and `PP-02`.
- Full: exactly 136 unique candidate/target/mutation rows and all 17 Set-C IDs.
- MD-RRS remains separate from docking-RRS. It is a trajectory-derived bound-fraction ratio, not a replacement for the docking metric.
- A failed or incomplete contract produces a terminal failed/pending manifest and no manuscript result.
- The GPU witness and the 15262 benchmark are stability evidence only; they are not substitutes for the 16-system pilot contract.

## Discriminative MD-RRS (multi-threshold) — 18 Aug 2026

`results/set_c_md/md_rrs_discriminative_manifest.json` + `set_c_trajectory_metrics_pilot.csv` + `md_rrs_discriminative_pilot.csv`

Re-analysis of the same 16 production trajectories (no new MD) with a
continuous metric family: per-frame min heavy-atom protein--ligand distance,
bound fractions at 2.0/2.5/3.0/3.5/4.0/5.0 A, mean/p5/median min distance,
and `MD_RRS_d = 100 * mutant / WT` per continuous metric.

Key results:

- The binary 5 A bound fraction still saturates at 1.000 for all 16 systems
  (no dissociation event in 10 ns) - the continuous layer lifts the ceiling.
- **No mutant shows a weaker-binding signature**: e.g. PP-02 PfDHFR N51I has
  mean_min = 1.82 A vs WT 2.52 A (MD_RRS_mean_min = 72.2, binds *tighter*);
  PP-02 PfCRT K76T 2.77 A vs WT 3.17 A. Several mutants show slightly
  shorter contact distances than WT within this window.
- Interpretation (mandatory): the discriminative metrics remove the binary
  saturation but do **not** demonstrate resistance. 10 ns single-replicate
  windows measure local geometry, not affinity; no reduced-binding phenotype
  is established for any mutant.

## MD-RRS vs docking-RRS cross-comparison - 18 Aug 2026

`results/set_c_md/md_vs_docking_comparison_pilot.csv` (mapping via canonical
candidate smiles). Conventions: dock_RRS = |dG_mut|/|dG_WT| x 100 (>100 =
mutant binds tighter); MD_RRS_mean_min_dist = mean min-distance ratio (<100 =
mutant closer/tighter).

Key result: **the two metrics disagree in direction for PP-01** - docking
predicts *looser* binding for every PP-01 mutant (RRS 83.9-92.5), while the
10 ns MD shows *tighter* contacts (MD_RRS_dist 91-103). For PP-02 PfCRT both
point tighter (87-95). PP-02 PfDHFR mutants have no docking baseline (NaN).

Interpretation (mandatory): this is a methodological divergence, not a
resolved phenotype. Docking scores static binding energy; the 10 ns
single-replicate MD measures local geometry without dissociation events.
Neither metric alone establishes resistance. The docking RRS<100 for the
known resistance mutations (N51I/C59R/S108N/I164L) is suggestive but would
require experimental or longer-timescale validation.

## Post-QC comparison

Only after the selected contract passes:

```bash
python - <<'PY'
import pandas as pd
md = pd.read_csv('results/set_c_md/md_rrs_pilot_PP01_PP02.csv')
dock = pd.read_csv('results/c_rrs_classification.csv')
merged = md.merge(dock, on='set_c_id', suffixes=('_MD', '_dock'))
print(merged[['set_c_id', 'MD_RRS_class', 'RRS_class']].to_string(index=False))
PY
```

The pilot comparison is descriptive and limited to PP-01/PP-02; it must not be generalized to the remaining 15 candidates. The 10-ns single-replicate design does not establish long-timescale residence, convergence, or thermodynamic affinity.

## Biological annotation boundary

`results/plasmodb_target_annotation.csv` and Supporting Information Table S7 provide stable target identifiers, mutation context, record permalinks, and retrieval date. They do not constitute a GO/pathway-enrichment analysis. No pathway claim may be added without an independently defined gene set, background universe, release-pinned annotations, and multiplicity-corrected statistics.

---

## GPU witness live status — job 15270 (12 August 2026, ~15:05 UTC)

- SLURM job `15270` is terminal; no current P2 job is visible in `squeue`. The witness completed at 16:27:51 UTC on 12 August 2026.
- CWD: `results/md_systems/set_c_publication_gpu_v2_20260812/PP-01_PfDHFR_WT/runs/publication_gpu_20260812_v4/replicate_1`.
- GROMACS production active: `mdrun -s production.tpr -nb gpu -pme gpu -bonded cpu -update cpu -gpu_id 0 -ntomp 8`.
- Terminal progress: step 5,000,000 / 5,000,000 (dt = 0.002 ps) = **10 ns / 10 ns**.
- Terminal outputs: production.xtc ≈ 1.19 GB, production.tpr/.cpt/.edr/.log/.gro present; no fatal, LINCS, NaN, or infinite indicators were found in the terminal log scan.
- Measured terminal performance: **28.169 ns/day** (wall time 30,672.48 s). This replaces the provisional ETA/rate estimate.
- This is a single witness replicate (PP-01_PfDHFR_WT). Per-system diagnostic QC may inspect it when complete, but aggregate QC and `p2_setc_md_rrs.py` remain blocked until all 16 pilot systems are present and pass the declared gates.
