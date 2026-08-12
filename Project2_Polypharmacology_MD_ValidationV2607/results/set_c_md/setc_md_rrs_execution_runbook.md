# Set-C MD → MD-RRS execution runbook

**Updated:** 12 August 2026
**Scope:** candidate-specific Set-C trajectories only; parent-study MD systems are excluded.
**Current status:** CPU witness chain `15254 → 15259 → 15260` was stopped and is non-canonical. GPU benchmark `15262` passed; clean GPU witness `15270` is running. `md_rrs_status=NOT_COMPUTED` until a complete declared cohort passes trajectory QC.

## Cohort contracts

| Mode | Candidates | Systems / QC rows | QC output | MD-RRS output | Manuscript meaning |
|---|---:|---:|---|---|---|
| `pilot` (default) | PP-01, PP-02 | 16 | `results/set_c_md/set_c_trajectory_qc_pilot.csv` | `results/set_c_md/md_rrs_pilot_PP01_PP02.csv` | Targeted trajectory check only; the other 15 candidates remain docking-RRS only |
| `full` | PP-01–PP-17 | 136 | `results/set_c_md/set_c_trajectory_qc_full.csv` | `results/set_c_md/md_rrs_classification.csv` | Full Set-C MD-RRS claim only after all 17 candidates pass |

The 16-system pilot is 2 candidates × PfDHFR (WT, N51I, C59R, S108N, I164L) and PfCRT (WT, K76T, K76A), with the predeclared 10-ns production protocol. The force-field policy deviation is explicit: OpenFF 2.2.0 AM1-BCC for ligands with CHARMM36m/TIP3P for the protein/solvent; each system must retain `policy_deviation.declared=true` and `policy_deviation.approved=true`.

## Preconditions

1. Candidate-specific `system_manifest.json` and `forcefield_manifest.json` are present and identity/hashes pass.
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
sbatch --dependency=afterok:${PROD_JOB_ID} \
  --export=ALL,P2_PRODUCTION_JOB_ID=${PROD_JOB_ID},P2_EQUILIBRATION_JOB_ID=${EQ_JOB_ID},P2_SETC_COHORT_MODE=pilot \
  scripts/p2_setc_qc_and_md_rrs.sbatch
```

Use `P2_SETC_COHORT_MODE=full` only after the 17-candidate/136-system production contract has been prepared and independently checked. The wrapper writes a mode-specific post-production manifest and refuses missing job IDs.

## Direct QC and MD-RRS commands

The wrapper is preferred because it binds the job IDs and output paths. For a controlled manual run, set the mode-specific paths explicitly:

```bash
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607

export P2_SETC_ROOT="$PWD/results/md_systems/set_c"
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

- SLURM `p2_setc_gpu_witness` RUNNING on penavoraserver, RunTime 07:18, limit 24 h (End 13 Aug 07:55:41 UTC).
- CWD: `results/md_systems/set_c_publication_gpu_v2_20260812/PP-01_PfDHFR_WT/runs/publication_gpu_20260812_v4/replicate_1`.
- GROMACS production active: `mdrun -s production.tpr -nb gpu -pme gpu -bonded cpu -update cpu -gpu_id 0 -ntomp 8`.
- Progress at observation: step 4,284,000 / 5,000,000 (dt = 0.002 ps) = 8.57 ns / 10 ns = **85.7 %**.
- Outputs so far: production.xtc ≈ 1.02 GB, .cpt, .edr, .log present; no NaN/energy divergence in last energy block (Potential −4.34e6 kJ/mol, T = 309.8 K, P ≈ −29 bar).
- ETA (linear): ~1.4 ns remaining at observed throughput ≈ 1.17 ns/h ⇒ **~16:15–16:30 UTC** for this replicate, well inside the SLURM limit.
- This is a single witness replicate (PP-01_PfDHFR_WT). Post-QC chain (`set_c_trajectory_qc.py`, `p2_setc_md_rrs.py`) may start per-system as soon as each replicate finishes, without waiting for the whole array.
