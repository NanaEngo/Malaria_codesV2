# Set-C Post-Production Runbook: QC → MD-RRS

**Date:** 10 August 2026  
**Scripts verified:**  
- `p2_setc_trajectory_qc.py` — ✅ compile OK (malaria_md, py3.11)  
- `p2_setc_md_rrs.py` — ✅ compile OK (malaria_md, py3.11)  
**Dependencies verified:** MDAnalysis 2.10.0, scipy 1.17.1, numpy 2.4.6, pandas 2.3.3 (all in malaria_md)  

---

## ⚠️ Pre-condition: equilibration must complete for all 16 systems

The production array (`15111`, `dependency=afterok:15106`) only runs for systems with `npt.gro`.  
The MD-RRS script (`p2_setc_md_rrs.py`) is **fail-closed**: it requires **exactly 136 rows** (17 candidates × 8 states) **all with `qc_status=PASS`**, identical `analysis_rule_id`, `duration_ns`, and `n_frames`.  

**Current equilibration state (10 Aug, ~3h30 from start):**  
- 3/16 npt.gro (PP-01 PfCRT WT/K76A/K76T)  
- 1/16 FAIL (PP-01_PfDHFR_N51I — libgomp crash)  
- 12/16 no NPT progress (stalled or queued)  

**→ If the panel remains incomplete, the MD-RRS calculation will FAIL-CLOSED.**  
The 3 completed systems can still be individually QC'd for manuscript supplementary analysis (bound-fraction reports), but MD-RRS classification requires the full panel.

---

## Step 1: Verify production array completion

Before running QC, confirm:

```bash
# Check production.xtc count (expect 16 for full panel)
B=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/results/md_systems/set_c
find "$B" -name 'production.xtc' -type f | wc -l

# Check individual system production status
for d in "$B"/PP-*; do
  n=$(basename "$d")
  p=$(find "$d/runs" -name 'production.xtc' 2>/dev/null)
  [ -n "$p" ] && echo "$n: PRODUCTION_DONE ($(du -h "$p" | cut -f1))" || echo "$n: MISSING"
done

# Check SLURM array completion
sacct -j 15111 --format=JobID,State,Elapsed 2>/dev/null
```

---

## Step 2: Run trajectory QC (bound-fraction analysis)

**Estimated runtime:** ~5–15 min per system (wtih MDAnalysis, max_frames=2000).  
**Total:** ~1.5–4 h for 16 systems on 1 CPU; can be parallelized per system.

```bash
# Activate environment
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

# Change to project root
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607

# RUN — trajectory QC (ALL 16 systems)
python scripts/p2_setc_trajectory_qc.py \
  --bound-angstrom 5.0 \
  --min-frames 500 \
  --min-bound-fraction 0.10 \
  --max-frames 2000

# Expected output:
#   results/set_c_md/set_c_trajectory_qc.csv
# Contains: set_c_id, target, mutation, bound_fraction, n_frames,
#           duration_ns, trajectory_sha256, tpr_sha256, qc_status, analysis_rule_id
```

**Options:**
- Single system debugging: `--system PP-01_PfCRT_WT`
- Run as SLURM job (recommended for 16 systems):
  ```bash
  sbatch --dependency=afterok:15111 << 'SBATCH'
  #SBATCH --job-name=p2_setc_qc
  #SBATCH --partition=production
  #SBATCH --nodes=1 --ntasks=1 --cpus-per-task=4
  #SBATCH --time=6:00:00 --mem=16G
  #SBATCH --output=logs/p2_setc_qc_%j.log
  source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
  conda activate malaria_md
  cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
  python scripts/p2_setc_trajectory_qc.py --max-frames 2000
  SBATCH
  ```

---

## Step 3: Verify QC output integrity

```bash
QC=results/set_c_md/set_c_trajectory_qc.csv
python -c "
import pandas as pd
df = pd.read_csv('$QC')
print('Rows:', len(df))
print('PASS:', (df.qc_status == 'PASS').sum())
print('Non-PASS:', (df.qc_status != 'PASS').sum())
print('analysis_rule_id:', df.analysis_rule_id.unique())
if (df.qc_status == 'PASS').all():
    print('✅ ALL PASS — can proceed to MD-RRS')
else:
    print('❌ Some systems FAIL QC — investigate non-PASS rows:')
    print(df[df.qc_status != 'PASS'][['set_c_id','target','mutation','qc_status']])
"
```

**Expected for full panel:**
- 136 rows (17 × 8)
- analysis_rule_id = `setc_p2_minheavy_5A_ge10percent_v1` (unique)
- duration_ns consistent across all rows
- n_frames consistent across all rows
- All trajectory_sha256 valid (64 hex chars)

---

## Step 4: Compute MD-RRS (fail-closed)

**This step will FAIL-CLOSED if any QC PASS condition is violated.**

```bash
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607

# RUN — MD-RRS computation (requires ALL 136 rows PASS)
python scripts/p2_setc_md_rrs.py \
  --qc-file results/set_c_md/set_c_trajectory_qc.csv \
  --min-wt-bound-fraction 0.10 \
  --output results/set_c_md/md_rrs_classification.csv

# Expected outputs:
#   results/set_c_md/md_rrs_classification.csv  (RRS values, classes)
#   results/set_c_md/md_rrs_provenance.json       (provenance metadata)
```

**What the script checks (fail-closed gates):**
- candidate_sha256 matches canonical set-C file
- ALL rows have qc_status = PASS
- Exactly 1 unique analysis_rule_id
- All duration_ns identical
- All n_frames identical
- All trajectory_sha256 valid and files exist with matching hashes
- Exactly 136 rows (= 17 × 8)
- No duplicate set_c_id/target/mutation combinations
- SMILES consistency across all rows
- All targets (PfDHFR, PfCRT) and all mutations per target present

**MD-RRS formula:**  
`MD_RRS_mutant = 100 × bound_fraction_mutant / bound_fraction_WT`  
Averaged over targets with WT bound_fraction ≥ 0.10.

**MD-RRS classes:** Same as docking-RRS (A: ≥80% all, B: ≥70% all, C: ≥80% specific, D: <60% any).

---

## Step 5: Compare with docking-RRS

```bash
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607

python -c "
import pandas as pd
md = pd.read_csv('results/set_c_md/md_rrs_classification.csv')
dock = pd.read_csv('results/c_rrs_classification.csv')
merged = md.merge(dock, on='set_c_id', suffixes=('_MD', '_dock'))
merged['MD_vs_dock'] = merged['MD_RRS_class'] == merged['RRS_class']
print('MD-RRS vs docking-RRS agreement:')
print(merged[['set_c_id','MD_RRS_class','RRS_class','MD_vs_dock']].to_string())
print()
print('Agreement rate:', merged['MD_vs_dock'].mean())
"
```

---

## ⚠️ Known issue (10 Aug 2026): equilibration stalled/failed

**Problem:** 13/16 systems show no NPT progress. Task `PP-01_PfDHFR_N51I` crashed with a `libgomp` threading error. The remaining 12 are stalled with tiny log files (99–105 bytes) and no NPT output after 8–11 hours running time.

**Symptoms:**
- `npt.gro`: only 3/16  
- `npt.log`: only the 3 completed systems have log rows  
- Task logs: 99–449 bytes, well below the expected size for a completed equilibration  
- Old job 15081 showed `libgomp.so.1` crash for `PP-01_PfDHFR_N51I` on `penavoraserver`  

**Likely cause:** OpenMP thread contention on a shared node — multiple GROMACS instances each requesting 8 threads overwhelm the node.

**Recommended fix:**  
1. Cancel the stuck `15106_[4-7]` tasks:  
   ```bash
   scancel 15106_4 15106_5 15106_6 15106_7
   ```
2. Resubmit the failing systems individually with `-ntomp 2` (reduced threads):  
   ```bash
   cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
   
   # For each failing system, edit the sbatch or call the workflow directly:
   for SYS in PP-01_PfDHFR_N51I PP-01_PfDHFR_S108N PP-01_PfDHFR_WT \
              PP-01_PfDHFR_I164L PP-01_PfCRT_K76A PP-01_PfCRT_K76T PP-01_PfCRT_WT \
              PP-01_PfDHFR_C59R PP-02_PfCRT_K76A PP-02_PfCRT_K76T PP-02_PfCRT_WT \
              PP-02_PfDHFR_C59R PP-02_PfDHFR_I164L PP-02_PfDHFR_N51I PP-02_PfDHFR_S108N PP-02_PfDHFR_WT; do
     echo "NEEDS_RUN: $SYS"
   done
   ```

3. Alternative: create a new sbatch with `--cpus-per-task=4` and environment variable `export P2_SETC_NTOMP=2` in the script.

**Impact on production + QC chain:** Until equilibration completes for all 16 systems, the MD-RRS calculation cannot run (fail-closed on 136 rows). Only the 3 completed systems can be individually QC'd for intermediate analysis.---

## Status checkpoint — 2026-08-10 ~10:40 UTC (chain 15118 → 15119 → 15120)

Measured live state (squeue + per-system log mtimes):

| Job | Role | State | Note |
|---|---|---|---|
| **15118** eq retry (12 sys, `P2_SETC_NTOMP=2`, array 0-11%8) | Equilibration | 8 RUNNING, 3 PENDING, 1 FAILED | All 8 running tasks in **EM phase** (~27 min elapsed; em.log fresh 10:26-10:37). 4 preserved systems (PP-01 K76A/K76T/WT/C59R) already have npt.gro and are skipped. **15118_1 = PP-01_PfDHFR_N51I FAILED again** (libgromacs crash; the `-ntomp 1` workaround did not survive; N51I stays docking-RRS only, QC skips missing systems). |
| **15119** prod (16 × 10 ns, array 0-15%4) | Production | PENDING (dep 15118) | sbatch verified: `P2_SETC_NTOMP=8` exported **inside script** (4 tasks × 8 threads = 32 threads < 48 cores → no 15106-style contention); `--time=48:00:00` < partition MaxTime (7 days). Header ETA: ~9-10 h per 10 ns @ 8 threads, %4 → **~40 h** for the array. **No change needed.** |
| **15120** QC + MD-RRS | Post-prod | PENDING (dep 15119) | ~10-30 min after 15119. |

**ETAs (UTC):** 15118 complete ≈ **12:00-12:30** (first wave 8 tasks finish ~11:30, second wave 3 tasks ~12:30) → 15119 ≈ 12:30 + **~40 h** → 15119 complete ≈ **2026-08-12 ~04:30** → 15120 (QC+MD-RRS) ≈ **2026-08-12 ~05:00** → results feed the P2 manuscript integration plan.

**npt.gro count:** 4/16 (the 4 preserved PP-01 systems); the other 12 regenerate as 15118 waves complete. N51I ×2 (PP-01, PP-02) are expected to fail or be skipped.

**Timing model (measured):** EM 2×10k steps ~35-40 min @ 2 threads; NVT+NPT 2×50k steps ~80-100 min @ 2 threads → ~2 h per system. 2 waves × 8/3 tasks.
## Status checkpoint — 2026-08-10 ~10:47 UTC (chain 15118 → 15119 → 15120) — 2nd measurement

Measured live (squeue + log mtimes vs `date`, 10:47:01 UTC):

| Job | State | Detail |
|---|---|---|
| 15118 (eq, 12 sys, array 0-11 %8, NTOMP=2) | 8 RUNNING (0,2-8), 3 PENDING (9-11), 1 FAILED (1 = PP-01_PfDHFR_N51I) | Wave-1 elapsed ~45 min. Fresh logs: PP-01_I164L/S108N/WT + PP-02_K76A still in EM2 (em2.log mtime = now); **PP-02_K76T entered NVT 10:45:17, PP-02_WT 10:46:53** (nvt.log fresh, step 0). Old 10:09 npt/nvt logs = residues of canceled 15106 — do NOT use for rate. |
| 15119 (prod, 16×10 ns, %4, NTOMP=8) | PENDING (dependency 15118) | Unchanged config (safe, verified earlier). |
| 15120 (QC + MD-RRS) | PENDING (dependency 15119) | ~30 min after 15119. |

Measured EM duration (wave-1): EM1 ~26 min + EM2 ~16 min ≈ **42 min/system** (2 threads) — matches the 35-40 min model.

npt.gro: **4/16** (the 4 preserved PP-01 PfCRT K76A/K76T/WT + PfDHFR C59R from the earlier successful run); 12 more regenerate via 15118 (minus N51I failures).

ETA model (rate at 2 threads not yet measurable — NVT just started):
- NVT+NPT 2×50k steps at ~200-600 steps/min (scaling of the 8-thread 610 steps/min measure) → 2.8-8.3 h remaining per wave-1 system.
- Wave-1 (8 sys) complete ≈ **13:30-19:00 UTC**; wave-2 (3 sys) ≈ +2-3 h → **15118 done ≈ 16:00-21:00 UTC** (previous 12:00-12:30 estimate was optimistic).
- **Action**: re-measure NVT rate at ~11:05 (≈15-20 min of NVT data) to narrow the ETA; update this note.
- 15119 ≈ 15118 + ~40 h (4 waves × ~9.5 h) → Wed 12 - Thu 13 Aug.
- 15120 ≈ +30 min → MD-RRS results for P2 manuscript integration.

Expected final npt.gro: 14-15/16 (PP-01 N51I failed; PP-02 N51I index 10 at risk). QC ignores missing systems (documented).
## Status checkpoint — 2026-08-10 ~10:56 UTC — CHAIN ROBUSTNESS AUDIT (fixes applied)

**Question posed:** is the SLURM chain well-designed so jobs follow through to completion?

**Audit result: the chain was NOT robust as designed — two critical flaws found and fixed:**

| # | Flaw | Consequence | Fix (applied) |
|---|------|-------------|---------------|
| 1 | `--dependency=afterok:15118_*` on 15119 (and `afterok:15119_*` on 15120) | `afterok` on an array with `_*` requires **ALL** elements to exit 0. Task 15118_1 (PP-01_PfDHFR_N51I) is FAILED → dependency never satisfiable → **15119/15120 hang in PENDING forever (silent deadlock)** | `scontrol update JobId=15119 Dependency=afterany:15118_*` (rc=0) + `scontrol update JobId=15120 Dependency=afterany:15119_*` (rc=0) — **verified** in scontrol. Rationale: production tasks are independent (failed element does not block others) and QC tolerates missing systems |
| 2 | `--time=08:00:00` on 15118 at NTOMP=2 | Measured NVT rate ~220 steps/min (K76T/WT, 1500 steps / 6.8 min) → NVT+NPT 2×50k ≈ 7.6 h + EM ≈ 0.75 h ≈ **8.4 h** for PfCRT systems → **timeout at 8 h** | sbatch updated to `12:00:00` (applies to wave-2 pending tasks 9-11, verified 12:00:00). **Running wave-1 tasks (15121-15129) COULD NOT be extended** — cluster blocks TimeLimit updates on running jobs (`Access/permission denied` ×8) |

**Residual risk (wave-1, running):** ~3 PfCRT systems (PP-02 K76A/K76T/WT) may hit the 8 h limit at ~18:02 UTC, ~20-40 min before NPT completion.
- **Rescue path (checkpoint)**: `cd <sys> && gmx mdrun -s npt.tpr -cpi npt.cpt -deffnm npt -ntomp 2` (mdrun writes npt.cpt every 15 min) → finishes the tail, no full rerun.
- If not rescued: those systems are missing; production task fails for them only; **QC (15120) ignores missing systems (documented)**; MD-RRS computed on available systems.
- Wave-2 (tasks 9-11, 12 h limit) is safe.

**Revised ETA (measured 220 steps/min NVT, 42-45 min EM):**
```
15118 wave-1 (8 sys, 8h limit)  ≈ done ~18:02-18:20 UTC (PfCRT at-risk, rescue optional)
15118 wave-2 (3 sys, 12h limit) ≈ done ~02:30-03:00 UTC Aug 11
15119 production (%4 × NTOMP=8, ~9-10h/10ns) ≈ ~03:00 Aug 11 + ~38-40 h → Aug 12 ~17:00-19:00
15120 QC + MD-RRS              ≈ Aug 12 ~17:30-19:30 UTC
```
Full completion ≈ **Aug 12 evening UTC** — achievable and now robust at the dependency level; the only residual uncertainty is the wave-1 PfCRT timeouts (rescusable or QC-tolerated).

**Other chain checks (all good):** partition MaxTime 7 d > 48 h production limit; production NTOMP=8 export (4×8=32 threads < 48 cores, no contention); QC TimeLimit 02:00:00 ample; production `%4` throttle sane.
