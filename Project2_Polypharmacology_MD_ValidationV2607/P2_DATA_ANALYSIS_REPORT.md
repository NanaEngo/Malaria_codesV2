# P2 — Data Analysis Report (canonical)

**Project**: Polypharmacology MD validation (Set-C + parent-study cohort)
**Manuscript**: *J. Chem. Inf. Model.* (JCIM) — V2609 canonical
**Last refreshed**: 2026-08-30

> **Workflow rule:** DAR before manuscript. Any data/result/protocol change is recorded here before manuscript edit. In case of divergence, the DAR prevails.

## 1. Central question

Does a resistance-aware docking workflow (RRS + PNS + ACSI) produce a coherent prioritization signal within a curated antimalarial cohort, and is a short single-replicate MD stress test concordant with that docking-derived signal, or does it reveal non-equivalent quantities?

**Bounded answer:** (i) the docking workflow produces a coherent signal (primary RRS classes A*:1, A:1, B:4, C:5, D:1 on 12 complete two-target candidates; weak PNS–RRS association); (ii) the short MD stress test is **not** concordant — directional disagreement in 7/8 mutant comparisons — and therefore measures a non-equivalent quantity. Neither result establishes biological target engagement or resistance.

## 2. Primary cohort: Set-C docking (17 candidates, 136 systems)

- **17 candidates** (MPO ≥ 0.70, SYBA > 0, SI > 10 from 19,913 primary leads).
- **136 Vina docking systems**: PfDHFR (WT + N51I, C59R, S108N, I164L) and PfCRT (WT + K76T, K76A).
- **Target-balanced primary RRS (12/17):** 1 A*, 1 A, 4 B, 5 C, 1 D.
- **Available-target sensitivity (17/17):** 5 A*, 1 A, 5 B, 5 C, 1 D.
- **Primary PNS–RRS:** ρ = −0.2098, permutation p = 0.5144, Bonferroni-adjusted p = 1.0000, bootstrap 95% [−0.7582, 0.5429] (n = 12).
- **Coverage-sensitive PNS–RRS:** ρ = −0.5588, adjusted p = 0.0667 (n = 17; exploratory).
- **Primary ACSI–RRS:** ρ = −0.4056, adjusted p = 0.5766. RRS–weakest-WT: ρ = −0.1661, adjusted p = 1.0000.
- **ACSI > 0.70** for 2/17 candidates. ACSI weight sensitivity: ρ vs baseline = 0.9167–0.9804.

## 3. Rigorous audit

Canonical re-analysis: `scripts/p2_rigorous_audit.py` (seed 42). Regenerates `c_rrs_classification.csv`, `c_rrs_sensitivity.csv`, `cross_metric_statistical_audit.{csv,json}`, `pns_imputation_sensitivity.{csv,json}`. RRS classes: A*/A require all mutant RRS ≥ 80%; B requires all ≥ 70% but not all ≥ 80%; C requires one ≥ 80% but not all ≥ 70%; D is residual. Cross-metric: 100k permutations + 10k bootstrap. PNS-imputation sensitivity: ρ = 0.9632–1.0000 across zero-to-double PfCRT centrality.

## 4. Parent-study targeted MD (4 systems, 10 ns)

| System | Outcome | MM-GBSA |
|---|---|---|
| PfCRT–214 | Bound (3.19 Å, 78 contacts, 23 H-bonds) | **−18.25 ± 0.40 kcal/mol** (interpretable) |
| PfATP4–438 | Bound (2.25 Å, 178 contacts) | N/A — CHARMM36→AMBER corruption (+473 kcal/mol) |
| PfClpR–164 | Unbound (67.4 Å) | N/A — dissociated |
| PfDHFR–201 | Unbound (78.2 Å) | N/A — dissociated |

## 5. Set-C MD pilot (16 systems, 10 ns)

**Production:** 16 systems (PP-01, PP-02 × 8 mutant states), 10 ns, GPU A4000 (job 15320). CHARMM36m + OpenFF 2.2.0 AM1-BCC (declared policy deviation). **QC:** 16/16 PASS (rule `setc_p2_minheavy_5A_ge10percent_v1`).

### 5.1 Discriminative MD-RRS

No mutant shows a reproducible weaker-binding signature within 10 ns. MD_RRS_d range: 72.2–102.7; two states marginally above 100 (within ±3% of WT — not a reproducible weakening signal).

### 5.2 MD vs docking direction

7/8 systems with both estimates diverge. PP-01 PfCRT K76T is the single concordant case. Methodological divergence dominates; neither method demonstrates resistance.

### 5.3 Set-C MM-GBSA (16/16 computed)

All 16 systems yield finite negative ΔG (range −35.29 to −24.53; mean −29.04 ± 3.00). 8/12 mutants show MM-GBSA RRS > 100 (tighter than WT); 4/12 below 100. **Conclusion:** no mutant shows a reproducible weaker-binding signature, consistent with §5.1.

**PBC fix:** PP-02_PfCRT_K76A and PP-02_PfDHFR_WT re-run on `production_whole.xtc` after BOND/UB overflow.

### 5.4 K76A inter-replicate sensitivity

Original canonical: −35.29 ± 1.17 (19 Aug, rep1). Second replicate: −27.54 ± 1.89 (26 Aug, rep2, PBC-whole). Difference 7.75 kcal/mol documented in manuscript Limitations.

## 5.5 Author re-read trace (V2609, 30 Aug 2026)

Values verified against the canonical sources and now recorded here (DAR-before-manuscript rule):

- **Mean target-specific RRS:** PfDHFR = **75.1** (12 complete two-target candidates, mean of `RRS_mean_PfDHFR`), PfCRT = **86.2** (17 PfCRT-eligible, mean of `RRS_mean_PfCRT`); recomputed from `results/c_rrs_classification.csv` and consistent with Result-text. Complete-two-target classes: A*:1, A:1, B:4, C:5, D:1.
- **PP-15 single-ligand feasibility probe** (wild-type only; outside the 16-system pilot): Vina best poses PfDHFR −8.62, PfCRT −7.81 kcal/mol; 10 ns production each, QC pass, bound fraction 1.000 (mean min distances 2.77 Å PfDHFR, 3.20 Å PfCRT); MM-GBSA (GB^OBC2, igb=5, 0.15 M salt, PBC-whole) −29.52 ± 0.33 (PfDHFR, 100 frames) and −27.79 ± 0.49 (PfCRT, 80 frames) kcal/mol. Canonical Vina scores −8.621/−7.810; five-seed dispersion 0.018 (PfDHFR) and 0.030 (PfCRT) kcal/mol (source `results/pp15_docking_20260828/`). Narrated strictly as a feasibility check, not validation of the shortlist.
- **PP-01 PfCRT K76T pilot MD-RRS = 102.7** (§5.1), confirmed against `results/set_c_md/md_rrs_pilot_PP01_PP02.csv` and the SM/table rows; within the ±2 kcal/mol endpoint noise floor and read as retention, not gain.

## 6. Post-production chain

- All 16 production runs complete (job 15320); post-production COMPLETE 2026-08-18T21:29:54Z.
- MD-RRS: `COMPUTED_WITH_COHORT_CONTRACT` (PP-01/PP-02, 8 QC rows).
- MM-GBSA: 16/16 finite endpoints (`mmgbsa_summary_pilot.csv`).
- Full-panel (17×8=136) MD-RRS: `NOT_COMPUTED` by design.

## 7. Lightweight robustness (post-processing, no new MD)

- **MM-GBSA ΔΔG:** 0/12 mutants show significantly weaker binding at 95% CI; max |ΔΔG| = 5.37 kcal/mol. Confirms retention-not-gain.
- **Partial PNS–RRS** (controlling MW + scaffold prevalence): raw ρ = −0.2098 → partial ρ = −0.6154. Association strengthens under controls.
- **Cohort bootstrap (B=10⁴):** class-fraction CI95 — A* [0.118, 0.529], B [0.118, 0.529], C [0.118, 0.529], D [0.000, 0.176].
- **STRING 400/900 sensitivity:** PNS ranking threshold-robust — ρ = 0.9975 (400 vs 700), ρ = 0.9681 (700 vs 900).
- **PP-01/PP-15 multi-seed redocking:** seed noise ±0.03–0.05 kcal/mol; docking prioritization not seed-sensitive (Table S17).
- **GNINA CNN consensus:** 38/38 class A, 0 discordance with Vina; ρ(Vina,CNN) = 0.558 on ligand mean RRS.
- **External docking replication (39×8=312 records):** mean RRS 100.45 [99.59, 101.32]; class-A fraction 0.974 [0.923, 1.000].
- **ProLIF IFP:** 16/16 systems show 4–11 contacts at ≥50% occupancy; corroborates retention-not-gain.
- **MD-filter retention gate (pilot scope):** 7/12 gate rows pass docking RRS ≥ 80 AND MD-RRS < 100; PP-01 polypharma-promoted (2 targets), PP-02 not promoted (1 eligible target).
- **P2Rank pocket audit:** PfCRT top pocket 5.7 Å from Vina box center (independent corroboration).

## 8. Interpretation and limitations

### 8.1 Evidence levels

1. **Primary:** prespecified docking RRS/PNS/ACSI on Set-C.
2. **Secondary:** MD geometry, MM-GBSA, GNINA, P2Rank, ProLIF, robustness, external docking.
3. **Technical:** topology repair, equilibration, hash checks.
4. **Unobserved:** experimental affinity, target engagement, resistance phenotype.

Only levels 1–3 are available. Levels 2–3 must not validate level-1 biological claims.

### 8.2 Key limitations

- Docking-RRS is a hypothesis about relative mutant sensitivity, not a free-energy measurement.
- 10 ns pilot cannot resolve partial affinity loss; 7/8 systems diverge directionally from docking.
- MM-GBSA is a single-replicate endpoint, not a calibrated thermodynamic observable.
- PP-01 multi-seed: PfDHFR canonical −7.500 inside seed spread; PfCRT −9.300 ~0.04 from seed range (original receptor prep not preserved).
- Study is computational; no experimental activity or resistance claims.

## 8.3 Adversarial review mitigation (V2609, 30 Aug 2026)

Adversarial re-read as a strict JCIM reviewer identified 5 major and 6 minor risks. Each is traced here before the manuscript is edited (DAR-before-manuscript rule).

| # | Risk | Decision / mitigation | Manuscrit change |
|---|---|---|---|
| M1 | DEKOIS null (ROC-AUC 0.450, EF 0.00) is cited but not treated; reviewer may argue the RRS classes lack discriminative meaning if the protocol fails to recover known actives | Reframe as a **boundary, not an unhandled failure**: external *recovery* (DEKOIS) is a distinct estimand from *relative mutant/WT contrast* (RRS within a fixed panel); failure to recover known actives does not by itself invalidate a within-panel ratio. Add explicit Discussion subsection | Discussion: external enrichment as an analysis boundary; why RRS is still interpretable as within-panel *contrast* |
| M2 | 7/8 mutual disconcordance built as THE result rests on n=7 comparisons, 1 replicate, no bound/interval | Bound the claim: 7/8 is descriptive over linked comparisons (2 ligands); add exact concordant case (PP-01 PfCRT K76T); no inference beyond the tested systems | Results/Discussion: replace implied test with explicit descriptive framing + exact concordant row |
| M3 | "Triage signal" is stronger than the evidence (no positive external validation) | Narrow scope: use "hypothesis-generation" (or "prioritization hypothesis") instead of "triage" to avoid implying validated filtering | Abstract, Conclusion, Discussion |
| M4 | Class thresholds (70/80%, WT≥7.0/5.0 kcal/mol) are post-hoc on the panel | Add explicit Limitations note: thresholds are post-hoc, no prospective calibration curve exists | Limitations |
| M5 | No dock→MD MM-GBSA contrast shared on the same mutants (only PfCRT-214 interpretable) | Add conceptual paragraph on *why* a static relative score vs dynamic local geometry should diverge, without over-claiming | Discussion: expand the non-equivalence logic |
| m1 | Overbuilt machinery for a negative result (RRS+PNS+ACSI+GNINA+P2Rank+ProLIF+2 MD sets+DEKOIS) | Keep the methods (they evidence the "each layer = different estimand" message) but tighten the narrative thread; no new computation | Minor tightening |
| m2 | GNINA 38/38 class-A + ρ=0.558 presented as "consensus" risks reading as inflation under a saturated classification | Reframe as “concordance expected under a saturated (near-uniform class-A) ranking” | Discussion wording |
| m3 | p-adj=1.0000 (Bonferroni, n=12) read as a true absence | State explicitly that n=12 is underpowered to detect an association; adjusted p is an artefact of low power, not strong evidence of independence | Cross-metric section |
| m4 | "not additive / non-equivalent" repeated 6× | Keep the phrase where it adds information; ensure it is not circular justification | Prose pass |
| m5 | Figures/citations order, contextual legends | Verify figure order and self-contained legends in the compiled PDF | Compilation check |
| m6 | Soares multi-replicate non-compliance | Already explicit in Methods/Limitations; keep; confirm cover-letter alignment | Verified |

All mitigations are narrative/scope changes supported by the existing evidence; no new simulation required. **Implemented 30 Aug 2026:** M1 → Discussion subsubsection "External enrichment as an analysis boundary" (recovery vs relative-contrast); M2 → seven-of-eight framed as descriptive over 8 linked comparisons (2 ligands) + concordant state named (PP-01 PfCRT K76T); M3 → "triage signal" replaced by "hypothesis-generating prioritization"; M4 → post-hoc threshold note added to Limitations; M5 → mechanistic paragraph (static minimized pose vs thermal ensemble; saturated MD observables); m2 → GNINA 38/38 reframed under saturated classification; m3 → p-adj=1.0000 made explicit as underpowered (n=12).

## 9. Manuscript status

**V2609 = canonical submission release.** V2607 = used-as-source (archived). Compile (fresh, 30 Aug 2026): main **35 p.** / SM **20 p.** / cover 1 p., 0 LaTeX error, 0 undefined refs/citations. M1 (25 ns PP-01 PfDHFR WT) integrated into SM as archival stress-test appendix (outside Set-C estimand).

**Open items:**

| # | Item | Status |
|---|---|---|
| 1 | Full-panel MD-RRS (17×8=136) | `NOT_COMPUTED` by design |
| 2 | Zenodo deposit | `pending` (DOI reserved) |

## 10. Canonical locations

- Active manuscript: `manuscript/LaTeX/Polypharmacology_MD_Validation_V2609.tex` + `_SM_V2609.tex` + `Cover_Letter_V2609.tex`
- Archived V2607: `_archives/V2607_manuscript/`
- Results: `results/`
- Implementation plan: `docs/P2_V2609_IMPLEMENTATION_PLAN.md`
- Narrative pivot: `docs/P2_V2609_NARRATIVE_PIVOT_PLAN.md`
- Operational log (full execution history): `docs/P2_DAR_OPERATIONAL_LOG.md`
