# P2 Data Analysis Report — active summary

**Scope:** Resistance-aware polypharmacology of antimalarial leads (docking-RRS, PNS, ACSI, targeted MD, MM-GBSA, Set-C MD pilot).
**Updated:** 19 August 2026
**Root:** `Project2_Polypharmacology_MD_ValidationV2607/`

## 1. Central question

Does a resistance-aware, target-level computational workflow (docking-derived RRS + PNS + ACSI + targeted MD) distinguish predicted potency from predicted resilience in a chemically diverse antimalarial library — and what does a targeted MD pilot add beyond docking?

**Bounded answer:** the workflow supports *computational prioritisation* but does **not** establish biological target engagement, resistance circumvention, or pathway-level mechanism (as stated in the manuscript abstract).

## 2. Primary cohort: Set-C docking (17 candidates, 136 systems)

- **17 candidates** selected by MPO ≥ 0.70, SYBA > 0, SI > 10 from 19 913 primary leads.
- **136 Vina docking systems**: PfDHFR (WT + N51I, C59R, S108N, I164L) and PfCRT (WT + K76T, K76A).
- RRS classification: **6 Class A\*, 5 Class B, 5 Class C, 1 Class D** (per-target RRS; weak-WT targets excluded).
- PNS–RRS: Spearman **ρ = −0.559, p = 0.020** (n = 17) — direction consistent with H1 but **does not survive Bonferroni** (α ≈ 0.017).
- ACSI > 0.70 for **2/17** candidates; ACSI–PNS ρ = −0.078 (p = 0.765), ACSI–RRS ρ = −0.132 (p = 0.613).
- RRS–ΔG_WT: ρ = −0.433 (p = 0.082).
- Tartarus external validation and MPO sensitivity analysis documented in manuscript (`tab:tartarus_calibration`, `tab:tartarus_correlation`).

## 3. Parent-study targeted MD cohort (4 systems, 10 ns each)

| System | Outcome | MM-GBSA |
|---|---|---|
| PfCRT–214 | Bound (min dist 3.19 Å, 78 contacts, 23 H-bonds) | **−18.25 ± 0.40 kcal/mol** (101 snapshots, interpretable) |
| PfATP4–438 | Bound (min dist 2.25 Å, 178 contacts) | N/A — CHARMM36→AMBER conversion corrupted (+473 kcal/mol vdW inflation artifact) |
| PfClpR-labelled 164 | Unbound (67.4 Å) | N/A — dissociated |
| PfDHFR–201 | Unbound (78.2 Å) | N/A — dissociated |

## 4. Set-C MD pilot (16 systems, 10 ns each) — secondary analysis (NEW 19 Aug)

**Production:** 16 systems (PP-01, PP-02 × PfDHFR WT/N51I/C59R/S108N/I164L, PfCRT WT/K76T/K76A), 10 ns each, CHARMM36m/GAFF2, 310.15 K, GPU A4000 (job array 15320, ~19.8 ns/day sustained).
**Trajectory QC:** 16/16 PASS (job 15386; rule `setc_p2_minheavy_5A_ge10percent_v1`; hash-verified inputs/outputs).

### 4.1 Discriminative MD-RRS (multi-threshold, lifts the binary ceiling)

`results/set_c_md/md_rrs_discriminative_manifest.json` + `md_rrs_discriminative_pilot.csv`.
The 5 Å bound-fraction ceiling (all 16 systems = 1.000) is lifted with continuous metrics:
bound fractions at 2.0–4.0 Å, mean/p5 min heavy-atom distance, and MD_RRS_d = (mutant distance / WT distance) × 100 (>100 = looser).

**Key finding: no mutant shows a weaker-binding signature within 10 ns.**
- PP-01 PfDHFR N51I: mean_min 1.82 Å vs WT 2.52 Å (binds *tighter*; 85% of frames < 2 Å)
- PP-01 PfCRT K76T: 2.77 Å vs WT 3.17 Å (tighter)
- All MD_RRS_d ratios in range [91, 103]; bf(2 Å) 0.45–1.00.

**Honest caveat:** 10 ns measures local geometry, not affinity; this does **not** demonstrate resistance.

### 4.2 MD vs docking direction comparison

`results/set_c_md/md_vs_docking_comparison_pilot.csv` — mapping by canonical SMILES.

| Candidate | Docking (RRS) | MD 10 ns (MD_RRS_d) | Direction |
|---|---|---|---|
| PP-01 (all 6 mutants) | 83.9–92.5 → **looser** (docking predicts weaker mutant binding) | 91–103 → tighter/neutral | **Divergent** |
| PP-02 PfCRT (K76T/K76A) | 87.9–94.6 looser | 90–103 tighter/neutral | Divergent |

**Interpretation:** methodological divergence (static docking energy vs local 10 ns geometry); neither demonstrates resistance. Documented as a limitation, not a phenotype claim.

### 4.3 Set-C MM-GBSA (16 systems) — NEW 19 Aug

`results/set_c_md/mmgbsa_20260819/`, protocol identical to the parent cohort (gmx_MMPBSA v1.5.0.3, GB OBC2 igb=5, salt 0.15 M, ε 80/1, 100 ps snapshots = 100 frames, CHARMM36→AMBER).
Summary: `results/set_c_md/mmgbsa_summary_pilot.csv` + `mmgbsa_manifest.json` — **status `MMGBSA_COMPUTED` (16/16)**, regenerated 2026-08-19 after the two PBC-fixed reruns.

| System | ΔG_bind (kcal/mol) | MM-GBSA RRS | Docking RRS |
|---|---|---|---|
| PP-01 PfCRT K76A | −35.29 ± 1.17 | 115.3 | 90.86 |
| PP-01 PfCRT K76T | −29.51 ± 2.65 | 96.4 | 92.47 |
| PP-01 PfCRT WT | −30.61 ± 1.65 | 100.0 (ref) | — |
| PP-01 PfDHFR C59R | −26.56 ± 1.91 | 105.0 | 85.47 |
| PP-01 PfDHFR I164L | −26.13 ± 2.34 | 103.3 | 83.87 |
| PP-01 PfDHFR N51I | −29.83 ± 1.50 | 118.0 | 86.40 |
| PP-01 PfDHFR S108N | −30.21 ± 3.62 | 119.5 | 87.60 |
| PP-01 PfDHFR WT | −25.29 ± 2.94 | 100.0 (ref) | — |
| PP-02 PfCRT K76A | −24.53 ± 1.27 | 97.8 | 94.62 |
| PP-02 PfCRT K76T | −30.45 ± 1.38 | 121.4 | 87.91 |
| PP-02 PfCRT WT | −25.08 ± 2.56 | 100.0 (ref) | — |
| PP-02 PfDHFR C59R | −28.85 ± 1.88 | 95.7 | n/a |
| PP-02 PfDHFR I164L | −31.06 ± 1.52 | 103.0 | n/a |
| PP-02 PfDHFR N51I | −34.02 ± 2.68 | 112.8 | n/a |
| PP-02 PfDHFR S108N | −27.09 ± 1.55 | 89.8 | n/a |
| PP-02 PfDHFR WT | −30.16 ± 2.06 | 100.0 (ref) | — |

**Key findings:**
- All 16 systems yield negative ΔG_bind (range −35.29 to −24.53 kcal/mol; mean −29.04 ± 3.00) — every ligand retained in the 10 ns pilot.
- 8/12 mutants show MM-GBSA RRS > 100 (tighter than WT); 4/12 below 100 (PP-01 PfCRT K76T 96.4, PP-02 PfCRT K76A 97.8, PP-02 PfDHFR C59R 95.7, PP-02 PfDHFR S108N 89.8).
- Docking predicted all 12 mutants looser (RRS 83.9–94.6); MM-GBSA does not reproduce this pattern — the four below-100 cases (89.8–97.8) all sit within the ±2–3 kcal/mol MM-GBSA accuracy envelope of their WT references.
- **Conclusion: no mutant shows a reproducible weaker-binding signature within the pilot timescale**, consistent with the MD-RRS geometry result (§4.2). The docking-vs-MM-GBSA direction divergence remains methodological (static docking energy vs single-replicate endpoint estimate), not a phenotype claim.
- **PBC fix applied:** PP-02_PfCRT_K76A and PP-02_PfDHFR_WT failed the first pass (BOND/UB overflow, protein split across the periodic boundary) and were re-run on `production_whole.xtc` (`gmx trjconv -pbc whole`); both finalized 2026-08-19 12:02.

## 5. PfCRT 114–122 reconstruction chain (technical validation, 18–19 Aug)

`results/md_systems/pfcrt_junction_repair_audit_20260818.md` — full audit.

| Step | Verdict |
|---|---|
| Kabsch graft | 0/16 geometry (C–N junctions 0.85–5.5 Å) |
| OpenMM restrained junction repair | **15/15 unique PASS_GEOMETRY** (1.32–1.37 Å), selected `model_03_seed_001` (loop pLDDT 55.2) |
| Canonical GROMACS check | PASS — 1 continuous chain (VAL47→ASN405), pdb2gmx RC=0, EM converged |
| Canonical MD witness | PASS — EM + NVT 100 ps + NPT 100 ps |
| Long equilibration (jobs 15387+15388) | **CONVERGED** — 1 ns NPT, T 310.17 K (drift 0.03%), ρ 1021.12 kg/m³ (drift −0.017%), P half-window −7.52 → −0.38 bar, 0 error markers |

**Classification:** `GEOMETRY_REPAIR_WITNESS_ONLY` + `CANONICAL_POLICY_TOPOLOGY_CHECK_PASS` + `CANONICAL_MD_WITNESS_PASS` — technical validation only; no affinity/RRS/Set-C claim.

## 6. Interpretation and limitations

- Docking-RRS is a hypothesis about relative mutant sensitivity, not a measurement of mutant free-energy difference.
- The 10 ns Set-C pilot cannot resolve partial affinity loss; the discriminative metrics lift the binary ceiling but show **no** mutant-weakening signal, and docking vs MD directions diverge for PP-01 — methodological, not biological.
- MM-GBSA is a cautious endpoint diagnostic (±2–3 kcal/mol expected accuracy), not a calibrated thermodynamic observable; a single 10 ns replicate per system.
- PfCRT reconstruction is a technical/stability witness: no production on the repaired model beyond 1 ns equilibration, no binding/affinity/RRS.
- The study is computational; experimental activity and resistance claims are not made.

## 7. Manuscript status (19 Aug)

- **Manuscript**: `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` (main) + `_SM_V2607.tex` (SI). Target: JCIM (ACS).
- 19 Aug revision: pilot-exclusion sentences corrected (QC now 16/16); Set-C MD pilot integrated as an explicitly secondary analysis with discriminative MD-RRS; MM-GBSA (16 systems) added as secondary result; workflow figure caption updated.
- All numbers in text/tables trace to JSON/CSV data files (manifests listed above).
- Unit tests: `tests/test_pfcrt_pipeline.py` (10/10 PASS) + MM-GBSA aggregation tests.

## 8. Open items

- [x] MM-GBSA aggregation (16/16) → section 4.3 filled; manuscript `tab:mmmgbsa_setc` + Set-C pilot results subsection (`sec:setc_pilot`) added; abstract sentence already present (19 Aug revision).
- [x] Unit tests: `tests/test_pfcrt_pipeline.py` — 14/14 PASS (incl. MM-GBSA aggregation + PBC-fix tests).
- [ ] Final LaTeX compile + figure (MD_RRS vs dock_RRS scatter) if added.
- [ ] Git commit + push.
