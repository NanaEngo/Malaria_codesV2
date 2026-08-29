# P3 Statistical & Reproducibility Audit — Quantum-Inspired Representations

**Audit scope:** `Project3_Quantum_Inspired_RepresentationsV2607` (TFP / TNE / QKS / hybrid on eos80ch antimalarial library)
**Audit date:** 01 Aug 2026 (canonical P1–P3 record: `BMAD_Q1_DATA_ANALYSIS_REPORT.md`; P4 record: `P4_DATA_ANALYSIS_REPORT.md`)
**Rubric:** `~/.agents/skills/peer-review/references/{statistical_reproducibility,common_issues}.md`
**Mode:** local read-only (no HPC, no manuscript edits). Findings labeled `[Not reported]` vs `[Design/analysis problem]` per rubric.

> ⚠️ **UPDATE 01 Aug 2026 (same day, post-audit) — findings 1 & 2 superseded by M1 leakage discovery.**
> After this audit was drafted, the "completed full-library hybrid rerun" (job 12696, Hybrid 0.8968, Critical 2 / TOP-8 items 2, 5, 8) was **EXCLUDED** because it ran in `--precompute-kernel` mode: UMAP was fitted on ALL data before the train/test split (transductive leakage, ~+0.05 AUC inflation) — BMAD `M1`, lines 1844–1887. The 0.8968 value **must NOT** be written into the manuscript. A canonical no-leakage re-run (per-fold UMAP train-only, winning combo `n_qubits=6, nr=1, nk=30`) is running as **job 12699** (`p3_hybrid_canonical_19849.sbatch`); the QKS re-runs (jobs 12700/12702) use the same canonical panel. Additionally, the audit's two n=19,849 panels (Critical 1) have since been **unified** via `load_canonical_panel()` (TFP-order ∩ activity-dedup ∩ finite-TNE = **n=19,836**) shared by the classical, hybrid, ablation, and QKS benchmarks — the canonical classical re-run (job 12698) gives ECFP4 **0.9475±0.0045** on that shared panel. See §4 below.

---

## 0. Executive summary

The manuscript is unusually honest in its narrative (reproducibility failures are disclosed, the "no quantum advantage" framing is open, the H1–RRS association is openly size-mediated, the hybrid is labeled provisional). **The single biggest risk is not overclaiming — it is that the manuscript text is now stale relative to the completed full-library hybrid rerun (job 12696, finished 01 Aug 06:20 during this audit), and that the two "n=19,849" benchmarks used different molecule panels.** The headline classical-vs-quantum comparison is confounded by panel composition; the provisional-hybrid hedging no longer matches the deposited numbers; and the reported multiplicity control is internally inconsistent (10 vs 9 vs 7 comparisons).

Severity tally: **2 critical, 4 major, 5 minor** (details below).

---

## 1. Findings, severity-ordered

### CRITICAL 1 — QKS n=19,849 and classical n=19,849 benchmarks use *different* molecule panels
- **Question:** Q1 (sample size / precision); Q2 (comparability).
- **Evidence:** `results/p3_qks_summary_n19849.txt` (QK 0.6592±0.0362, RBF 0.8251±0.0022, linear 0.5397) was computed on the **first 19,849 rows of `results/eos80ch_malaria_final_activity.csv`** (`head(19849)`: 14,462 active / 5,387 inactive = **72.9%** active). The corrected classical benchmark (`results/p3_classical_benchmark_19849_summary.txt`, ECFP4 **0.9490±0.0013**) was computed on the **TFP panel** `results/p3_tda_fingerprints.csv` (15,063 active / 4,786 inactive = **75.9%** active), per `scripts/p3_classical_benchmark_19849.py`. SMILES overlap between the two panels: **only 11,720 / 19,849 (~59%)** (n=5,000: only 3,176/5,000 overlap).
- **Why it matters:** The abstract and Results state "ECFP4 AUC 0.949 is the strongest single descriptor" and "the quantum kernel (0.659) falls significantly below RBF (0.825), p=0.0006" — but these numbers come from non-identical molecule sets with different class ratios (75.9% vs 72.9%). The within-QKS comparison (QK vs RBF vs linear) is internally valid; the **cross-benchmark ranking** (quantum/classical) is confounded by panel composition.
- **Fix:** Run the QKS kernels on the identical TFP-panel SMILES, or state explicitly in Methods that the two n=19,849 panels differ and deposit the exact SMILES list per benchmark. Recompute the "no advantage at scale" sentence once panels match.

### CRITICAL 2 — Full-library hybrid rerun completed *during this audit* and supersedes every "provisional hybrid" statement in the manuscript
> ⚠️ **SUPERSEDED same day** — this finding is invalidated by the M1 transductive-leakage discovery: job 12696 (0.8968) ran in `--precompute-kernel` mode (UMAP on all data), so 0.8968 is EXCLUDED; a canonical no-leakage re-run (job 12699) is in progress. See §4 and the UPDATE note above. The manuscript's provisional hedging remains correct.
- **Question:** Q1 / reproducibility.
- **Evidence:** `results/p3_hybrid_summary.txt` and `results/p3_hybrid_benchmark.csv` were overwritten at **2026-08-01 06:20:51** by job 12696. New canonical values: **Hybrid RF AUC 0.8968±0.0066 vs ECFP4 0.9490±0.0013, paired t=-16.957, p=0.0001** (5 folds) → hybrid is **significantly below** ECFP4. The manuscript (lines 428–432, 544, 546, 554) still reports "provisional hybrid AUC 0.842, p=0.111; no conclusion until the rerun completes". The SM Table S4 per-fold Hybrid rows (0.800/0.960/0.792/1.000/0.917) are stale and do not match the new run (0.897/0.890/0.908/0.894/0.895); the old fold-4 value AUC=1.000 was itself a red flag from the non-reproducible run.
- **Additional provenance issue:** the n=5,000 hybrid run survives only in `results/p3_hybrid_benchmark_n5000_full.csv`, which has **Hybrid rf folds [2,3,4,5] only (fold 1 missing)** while ECFP4 has 5 folds → the reported `0.8423±0.0076` and its paired t-test were computed on mismatched fold sets.
- **Why it matters:** The paper's central hedge ("hybrid may be a complementary tool if confirmed") is now resolved, and the answer is negative (0.897 < 0.949, p<0.0001). Leaving the provisional wording makes the deposited data contradict the text.
- **Fix:** Update manuscript + SM S4 to the completed rerun; delete the provisional caveats; document the n=5,000 fold-1 drop; re-run the ablation on the same completed run (ablation currently exists only as a partial n≈5,000 CSV, `results/p3_ablation.csv`: Hybrid−TFP 0.8226, Hybrid−TNE 0.8688, Hybrid−QK 0.7308).

### MAJOR 3 — Multiplicity control is inconsistent across the paper and not applied to the headline kernel tests
- **Question:** Q2 (multiplicity).
- **Evidence:** Methods (manuscript line 238) claims "Bonferroni adjustment across 10 pairwise comparisons"; the effect-size table footnote (`results/p3_effect_sizes/p3_effect_sizes_table.tex` line 22) says "0.05/9 = 0.0056"; the generating script `scripts/p3_effect_sizes.py:188` computes `0.05/len(df) = 0.05/7 = 0.0071`. The effect-size table itself contains **7** comparisons. Meanwhile `results/p3_qks_summary_n500.txt / _n5000.txt / _n19849.txt` flag "Significant (p<0.05)" with **no** correction across the 3-kernel × 4-sample-size family (n=500, 5,000, 19,849 + Phase-2 grid), and the H1–RRS headline (ρ=0.312, p=0.0057) is uncorrected across the 12 features in `p3_h1_rrs_correlation_final.txt`.
- **Why it matters:** The paper's strongest quantitative claim — "gamma-tuned RBF significantly outperforms QK (p=0.003)" — is one of ~9–12 unadjusted kernel comparisons; a single raw p<0.003 among a family of that size is much weaker evidence than presented.
- **Fix:** Pre-register one comparison family per analysis; apply Bonferroni-Holm or FDR; report adjusted p; make the divisor consistent across Methods, tables, and scripts (7, not 9, not 10).

### MAJOR 4 — Effect sizes and "power" are computed on the 5 CV folds and are not interpretable as effect metrics
- **Question:** Q6 (effect sizes / uncertainty units).
- **Evidence:** `results/p3_effect_sizes/p3_effect_sizes.csv` — Cohen's d = 6.5–24.1 ("large" for all), CI_95 are confidence intervals on the **fold-mean difference** (n=5), and Power_80pct = 1.0 for all rows (post-hoc power on 5 folds is circular). The SM table's own caption concedes "because the full-library folds are very consistent, the resulting d values are large, so the absolute ΔAUC is the more interpretable effect metric" — i.e., the reported d values are acknowledged to be uninformative. No DeLong or molecule-level CIs exist anywhere in the paper (`grep` for DeLong/95%CI in manuscript + SM returns nothing).
- **Why it matters:** Reviewers will read d≈24 as a huge effect; it is an artifact of n=5 fold-level pseudoreplication. The unit of inference is the molecule, not the fold.
- **Fix:** Replace fold-level d with DeLong 95% CIs on AUC deltas (molecule-level); drop post-hoc power; report ΔAUC as the primary effect metric; keep d only as a fold-precision diagnostic.

### MAJOR 5 — ChEMBL "validation" matches only 1/10 top candidates; coverage is not disclosed as such
- **Question:** Q7 (external validation).
- **Evidence:** `results/p3_chembl_validation/p3_chembl_validation.csv` — only 1 of the top-10 matched (Rank 5, PfCRT CHEMBL4754685, Tanimoto 0.379, IC50 15.6 µM, **Inactive**, pChEMBL 4.81). `results/p3_chembl_expanded.csv` — 7 matched pairs, 6 unique compounds, 2 targets (PfCRT Inactive×4, PfATP4 Active×3); no PfDHFR matches.
- **Why it matters:** The paper lists "ChEMBL IC50 validation" as an acceptance action (+15%). As executed, it is a **candidate-matching exercise (10% coverage), not a validation**, and the single matched top-10 candidate was experimentally inactive.
- **Fix:** Report as matching/novelty screen with 1/10 coverage stated in the main text; separate "matched compounds found" from "activity confirmed"; do not call it validation.

### MINOR 6 — No PR-AUC / average-precision reported despite ≥72–76% class imbalance
- **Question:** Q3 (classification metrics).
- **Evidence:** All summaries report AUC/Accuracy/F1 only (e.g., `p3_classical_benchmark_19849_summary.txt`, `p3_hybrid_summary.txt`); `grep` across scripts and results finds no `average_precision_score`/PR-AUC. (Note: the "AP" row in the classical benchmark is the **Atom-Pairs fingerprint descriptor**, AUC 0.9410 — a naming collision with "average precision" that should be disambiguated in the tables.)
- **Why it matters:** At 76% active prevalence, ROC-AUC overstates real-world ranking ability; PR-AUC is the accepted metric for imbalanced screening.
- **Fix:** Add PR-AUC (and ideally Brier score) at least for the primary 19,849-molecule benchmark table; rename the AP descriptor in table captions.

### MINOR 7 — All "significance" is a paired t-test across 5 CV folds (df=4)
- **Question:** Q4 (paired comparisons); Q1 (precision).
- **Evidence:** Every QKS/hybrid/effect-size comparison uses `stats.ttest_rel` over the 5 folds (e.g., QK vs RBF at n=5,000: t=-6.457, df=4, p=0.0030; at n=19,849: t=-9.709, p=0.0006). Folds are correlated, not independent samples; the effective df is far below what the p-values imply.
- **Why it matters:** p=0.003 from n=5 paired observations is not the same evidence as p=0.003 on molecules; the paper's "sufficient statistical power at n=5,000" claim (line 347/515) rests on this fold-level test, not on a molecule-level test.
- **Fix:** Supplement every headline comparison with a DeLong test or molecule-level bootstrap CI; present fold-level t-tests as a secondary diagnostic.

### MINOR 8 — RBF gamma is tuned on a coarse grid and saturates at the upper edge
- **Question:** Q1 / Q2 (kernel comparison fairness).
- **Evidence:** `results/p3_qks_benchmark_n5000.csv` gamma column: 5, 5, 5, 2, 5 on grid {0.5, 1, 2, 5}; n=19,849 run picks 5.0 for all folds — i.e., the tuned optimum sits at the grid boundary, so "RBF beats QK" is conditional on the grid extent. The SM (line 677) discloses the per-fold gamma — good transparency.
- **Fix:** Extend the gamma grid / use continuous or log-uniform tuning; state that the optimum is at the boundary; consider reporting RBF performance under a range of gamma values.

### MINOR 9 — Effect-size Bonferroni footnote is internally wrong (7 rows, footnote says 0.05/9)
- **Question:** Q2 (consistency).
- **Evidence:** `p3_effect_sizes_table.tex` line 22 hardcodes "0.05/9" while the table has 7 comparisons and the script computes `0.05/len(df)=0.05/7`. Manuscript Methods says "10 comparisons". None of 9, 7, 10 agrees with the others.
- **Fix:** Single source of truth for the comparison count; regenerate the table from the script.

---

## 2. What is handled well (keep)
- **Honest negative results:** "TDA does not outperform ECFP4", "no quantum advantage at scale", "the apparent quantum advantage was an artifact of untuned RBF gamma" are stated plainly (lines 542, 544, 515).
- **H1–RRS is correctly de-confounded:** unadjusted ρ=0.312 (p=0.0057, n=77) → partial (MW, n_rings, Fsp3, H0_count) ρ=−0.039 (p=0.745); the manuscript interprets this as size-mediated (lines 527, 542, 546), matching `p3_h1_rrs_partial_corr.txt` VERDICT. Suggest also stating the n=77 / no-MC caveat in the abstract.
- **Reproducibility failures disclosed:** the non-reproducible full-library run, the PHCO `GetOnBits` bug, the TNE copy-paste error, and the `class_weight`/baseline corrections are all documented.
- **Calibration is addressed:** conformal coverage 0.950 (α=0.05), ECE 0.0037, uncertainty–error ρ=−0.286 (p=0.0039) in `results/p3_mc_uncertainty_summary.txt`.
- **Per-fold data deposited:** per-fold CSVs and gamma columns are present (`p3_qks_benchmark_n*.csv`, `p3_hybrid_benchmark*.csv`), and the SM reports per-fold gamma (5,5,5,2,5).

---

## 3. TOP-8 prioritized statistical improvements

1. **Match the molecule panels** across the n=19,849 QKS and classical benchmarks (Critical 1) and re-state the "no quantum advantage at scale" sentence on identical panels.
2. **Update the manuscript + SM Table S4 to the completed full-library hybrid rerun** (Hybrid 0.8968±0.0066 vs ECFP4 0.9490±0.0013, p=0.0001) and remove all "provisional/pending rerun" wording (Critical 2).
3. **Replace fold-level paired t-tests (df=4) with DeLong/molecule-level bootstrap CIs** for all headline AUC comparisons, and report PR-AUC for the primary benchmark table (Minor 6/7).
4. **Apply and consistently report multiplicity control** (Bonferroni-Holm or FDR) across the kernel family, the effect-size family, and the H1–RRS feature family; reconcile the 10/9/7 comparison-count discrepancy (Major 3, Minor 9).
5. **Recompute the ablation on the completed full-library hybrid** and report it as the definitive hybrid/ablation result (currently partial n≈5,000 only) (Critical 2).
6. **Reframe the ChEMBL analysis as a 1/10-coverage candidate-matching screen**, not a validation; state coverage and the single inactive top-10 match explicitly (Major 5).
7. **Drop fold-level Cohen's d and post-hoc "Power=1.0"**; report ΔAUC with molecule-level CIs as the effect metric (Major 4).
8. **Fix the n=5,000 hybrid provenance**: document the missing fold 1 in `p3_hybrid_benchmark_n5000_full.csv` and archive a versioned copy of the summary before further reruns overwrite it (Critical 2 / reproducibility).

---

## 4. Post-audit update — 01 Aug 2026 (M1 leakage, canonical panel, rerun status)

Superseded / resolved findings since this audit was drafted:

| Finding | Status | Evidence / action |
|---|---|---|
| **Critical 1** — QKS n=19,849 vs classical n=19,849 different panels | ✅ **RESOLVED** | Both now run on the shared canonical panel via `load_canonical_panel()` = TFP-order ∩ activity-dedup ∩ finite-TNE = **n=19,836** (BMAD C2/M3). Classical re-run (job 12698) done: ECFP4 **0.9475±0.0045**, FCFP4 0.9183, AP 0.9399, BPF 0.9389, MACCS 0.9045, PHCO 0.8959, TFP 0.8759, TNE 0.7219. QKS re-runs on the same panel: jobs 12700 (`n=19,849`) and 12702 (`n=5,000`) queued. |
| **Critical 2** — hybrid 0.8968 "new canonical" | ❌ **INVALIDATED** | 0.8968 came from job 12696 in `--precompute-kernel` (TRANSDUCTIVE UMAP fitted on all data) → ~+0.05 leakage inflation (BMAD M1, lines 1844–1887). **Do not report.** Canonical no-leakage re-run = **job 12699** (per-fold UMAP train-only; `n_qubits=6, nr=1, nk=30`; `p3_hybrid_canonical_19849.sbatch`). Manuscript "provisional / rerun in progress" hedge remains CORRECT until 12699 finishes. |
| **TOP-8 #1** (match panels) | ✅ **RESOLVED** | See Critical 1 row above; "no quantum advantage at scale" sentence must be re-stated once jobs 12700/12702 finish on the shared panel. |
| **TOP-8 #5** (ablation on completed full hybrid) | 🔄 **PENDING** | Will run on the canonical hybrid once job 12699 completes (ablation shares its per-fold QK). |
| **TOP-8 #8** (n=5,000 hybrid fold-1 provenance) | 📋 **STILL OPEN** | `p3_hybrid_benchmark_n5000_full.csv` fold-1 gap (2–5 only) still needs a provenance note; n=5,000 numbers are superseded by the canonical n=19,836 re-run regardless. |

Still-valid findings (unchanged by the M1/canonical-panel work):

- **Major 3 / Minor 9** — multiplicity control inconsistent (10 vs 9 vs 7) across Methods, effect-size table, and `p3_effect_sizes.py`. Script uses `0.05/len(df)=0.05/7`; effect-size table footnote hardcodes "0.05/9"; Methods says "10 comparisons". Need a single source of truth.
- **Major 4** — fold-level Cohen's d (6.5–24.1) and post-hoc Power=1.0 are artifacts of n=5 folds; recommend DeLong/molecule-level CIs on ΔAUC as the primary effect metric.
- **Major 5** — ChEMBL "validation" is a 1/10-coverage candidate-matching exercise; must be reframed as matching/novelty screen with coverage stated.
- **Minor 6** — PR-AUC never reported despite 76% active prevalence; AP descriptor name collides with "average precision" in tables.
- **Minor 7** — all headline significance is paired t-test across 5 folds (df=4); add DeLong or molecule-level bootstrap as primary.
- **Minor 8** — RBF gamma grid {0.5,1,2,5} saturates at upper edge (5.0 for all folds at n=19,849); state boundary effect / extend grid.

---

## Appendix — Verified numbers (recomputed in this audit)

| Item | Value | Source |
|---|---|---|
| head(200) class split | 105 active (52.5%) / 95 inactive | `eos80ch_malaria_final_activity.csv` |
| head(500) | 307 act (61.4%) / 193 inact | same |
| head(5,000) | 3,732 act (74.6%) / 1,268 inact | same |
| head(19,849) | 14,462 act (72.9%) / 5,387 inact | same |
| TFP panel (19,849) | 15,063 act (75.9%) / 4,786 inact | `p3_tda_fingerprints.csv` + `p3_labels_production.csv` |
| Panel overlap | 11,720/19,849 (~59%); n=5,000: 3,176/5,000 | SMILES canonicalized |
| Classical 19,849 (RF) | ECFP4 0.9490±0.0013, FCFP4 0.9198, MACCS 0.9039, AP 0.9410, PHCO 0.8967, BPF 0.9394, TFP 0.8767, TNE 0.7220 | `p3_classical_benchmark_19849_summary.txt` |
| QKS n=5,000 | QK 0.7524±0.0235, RBF 0.8404±0.0087, linear 0.7431; QK–RBF t=−6.457 p=0.0030; QK–lin t=0.596 p=0.5835; RBF–lin t=10.098 p=0.0005 | `p3_qks_summary_n5000.txt` |
| QKS n=19,849 | QK 0.6592±0.0362, RBF 0.8251±0.0022, linear 0.5397; QK–RBF t=−9.709 p=0.0006; QK–lin t=5.259 p=0.0063 | `p3_qks_summary_n19849.txt` |
| Hybrid full-library (NEW) | Hybrid RF 0.8968±0.0066 vs ECFP4 0.9490±0.0013, t=−16.957, p=0.0001 (5 folds) | `p3_hybrid_summary.txt` (overwritten 01 Aug 06:20) |
| Hybrid n=5,000 (archived) | 0.8423±0.0076, but folds 2–5 only (fold 1 absent) | `p3_hybrid_benchmark_n5000_full.csv` |
| H1–RRS (n=77) | Spearman ρ=0.3124 p=0.0057; partial (4 covariates) ρ=−0.0388 p=0.7447 | `p3_h1_rrs_correlation_final.txt`, `p3_h1_rrs_partial_corr.txt` |
| ChEMBL | 1/10 top matched (Inactive, IC50 15.6 µM); expanded 7 pairs/6 cmpd/2 targets | `p3_chembl_validation*.csv`, `p3_chembl_expanded.csv` |
| Ablation (partial n≈5,000) | Hybrid−TFP 0.8226, Hybrid−TNE 0.8688, Hybrid−QK 0.7308 | `p3_ablation.csv` |
| Calibration | conformal coverage 0.950, ECE 0.0037, ρ=−0.286 p=0.0039 | `p3_mc_uncertainty_summary.txt` |

*Prepared as a local audit deliverable; no files under `manuscript/` were modified.*
