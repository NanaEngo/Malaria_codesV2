# Analysis Ledger — P3 Quantum-Inspired Representations

**Created:** 2026-07-31  
**Authority:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (161,509 bytes, updated 2026-07-30, v37)  
**Previous authority:** `BMAD_Q1_DATA_ANALYSIS_REPORT_V1.md` (150,772 bytes)  
**Rule:** No number enters the manuscript except through a written, interpreted entry here.  
**Format:** Each entry has ID, method, numbers (with units + uncertainty), written interpretation, caveats, and claim link.

---

## Entry Index

| ID | Topic | Source CSV / Script | Claim link |
|----|-------|---------------------|------------|
| L001 | Classical-only benchmark (19,849 mol) | `p3_classical_benchmark_19849.csv` | Tab.1, Abstract |
| L002 | H1-RRS correlation — expanded cohort | `p3_h1_rrs_correlation_final.txt/.csv` | §4.7, Fig.5 |
| L003 | H1-RRS correlation — pilot cohort | `p3_h1_rrs_correlation_final.txt` | §4.7 (context) |
| L004 | QKS polypharmacology benchmark | `p3_qks_summary.txt` | §4.5 |
| L005 | TDA promiscuity correlations | `p3_tda_promiscuity.csv` | §4.5 |
| L006 | TNE Tartarus regression | `p3_physical_validation_summary.txt` | §4.4 |
| L007 | Hybrid benchmark (provisional) | BMAD_Q1 §3.4 + §3.5 | Tab.2 (provisional) |
| L008 | Scaffold paradox Tanimoto | BMAD_Q1 §2 / manuscript | §4.3 |
| L009 | QKS vs RBF kernel comparison | `p3_qks_summary.txt` | Tab.3 |
| L010 | Figure 1 population TDA summary | `p3_tda_fingerprints.csv` | Fig.1 caption |
| L011 | q_cadd_2026 citation status | BibTeX audit | Bibliography |
| L012 | GA-style discriminator benchmark | `p3_ga_discriminator.csv` | Tab.5, Fig.6 |
| L013 | Quantum hyperparameter optimisation | `p3_qp_optimization_table.csv`, `p3_quantum_params_sweep.csv` | Methods §2.6 |
| L014 | Enriched-TFP / SOTA topological benchmark | `p3_sota_benchmark_full.csv` | Limitations §5.7 |

---

## L001 — Classical-only benchmark (19,849 molecules, RF, 5-fold CV)

**Date:** 2026-07-29  
**Script:** `scripts/p3_classical_benchmark_19849.py`  
**Source:** `results/p3_classical_benchmark_19849.csv` + `results/p3_classical_benchmark_19849_summary.txt`  
**Method:** Random Forest (200 trees), StratifiedKFold 5-fold, random_state=42. All 19,849 molecules. PHCO bug fixed (replaced degenerate `GetOnBits()` with `rdkit.Chem.Pharm2D.Generate.Gen2DFingerprint` correct implementation).

| Descriptor | AUC (mean ± σ) | Accuracy | F1 | ΔAUC vs ECFP4 |
|------------|---------------|----------|----|----------------|
| ECFP4 | **0.9490 ± 0.0013** | 0.8968 | 0.9319 | — |
| AP | 0.9410 ± 0.0019 | 0.8906 | 0.9285 | −0.008 |
| BPF | 0.9394 ± 0.0019 | 0.8882 | 0.9271 | −0.010 |
| FCFP4 | 0.9198 ± 0.0028 | 0.8699 | 0.9142 | −0.029 |
| MACCS | 0.9039 ± 0.0035 | 0.8607 | 0.9079 | −0.045 |
| PHCO | 0.8967 ± 0.0047 | 0.8519 | 0.9026 | −0.052 |
| TFP | 0.8767 ± 0.0055 | 0.8383 | 0.8970 | −0.072 |
| TNE (d=8) | 0.7220 ± 0.0097 | 0.7543 | 0.8564 | −0.227 |

**Per-fold AUC (ECFP4):** [0.9493, 0.9493, 0.9489, 0.9505, 0.9469]  
**Per-fold AUC (TFP):** [0.8788, 0.8798, 0.8764, 0.8812, 0.8674]  
**Per-fold AUC (TNE):** [0.7066, 0.7250, 0.7297, 0.7299, 0.7188]

**Interpretation:** Classical fingerprints dominate on this 19,849-molecule set. ECFP4 at AUC 0.949 is near ceiling for eos80ch binary classification. The PHCO descriptor was previously degenerate at 0.500 due to a bit-vector extraction bug; corrected to 0.897, confirming pharmacophore features carry genuine discriminative information. TFP (0.877) and TNE (0.722) capture complementary but weaker signal, expected given their global topological vs. local substructure encoding. The gap between TFP and classical fingerprints (ΔAUC = −0.072) is consistent with the known dominance of local pharmacophoric patterns for antimalarial activity prediction.

**Caveats:** Activity labels are computational predictions from Ersilia eos80ch model, not experimental IC50. The 19,849-molecule benchmark set passed quality control from a 65,856-molecule generated library; results may not generalise to the excluded molecules.

**Numbers in manuscript:** Table 1 (tab:benchmark), Abstract line 5–8, Discussion §4.6.

---

## L002 — H1-RRS correlation, expanded cohort (n=77)

**Date:** 2026-07-25  
**Script:** `scripts/p3_rrs_tfp_expansion.py`  
**Source:** `results/p3_h1_rrs_correlation_final.txt`, `results/p3_h1_rrs_correlation_final.csv`  
**Method:** Spearman rank correlation between RRS (Resistance Resilience Score) and TFP features. n=77 compounds after filtering for valid RRS + TFP from 500 processed. Class A=46, Class B=31.

| Metric | Spearman ρ | p-value | Interpretation |
|--------|:----------:|:-------:|----------------|
| H1_count | **+0.312** | **0.0057** | Significant positive |
| H1_total_persistence | +0.263 | 0.021 | Weak positive |
| H1_entropy | +0.254 | 0.026 | Weak positive |
| H1_max_pers | +0.067 | 0.561 | Non-significant |
| H1_mean_pers | +0.006 | 0.961 | Non-significant |

**Interpretation:** The primary correlation driver is H1 **count** (number of ring-like topological features), not persistence magnitude. The expanded cohort (n=77) confirms a statistically significant but modest association (ρ=0.312, p=0.006). This attenuation from the pilot (see L003) is expected as sample size grows and edge cases are included. Classes are binary (A/B only in expanded cohort; no C/D/Unknown), which limits variability compared to the pilot's 4-class design.

**Caveats:** Binary class structure (A vs B only) in expanded cohort; no Class C/D/Unknown molecules. Pilot n=14 included Class D (n=1, single compound — Class D statistics unreliable). The association is hypothesis-generating, not confirmatory.

**Numbers in manuscript:** §4.7 (lead finding), Fig.5 caption, Abstract, Conclusion.

---

## L003 — H1-RRS correlation, pilot cohort (n=14)

**Date:** 2026-07-15 (original), retained as context  
**Script:** `scripts/p3_h1_rrs_cross_paper_analysis.py`  
**Source:** `results/p3_h1_rrs_correlation_final.txt` (pilot section)  
**Method:** Spearman correlation, n=14 polypharmacological leads with complete RRS data. Classes: A=3, A*=1, B=2, C=7, D=1.

| Metric | Spearman ρ | p-value |
|--------|:----------:|:-------:|
| H1_total_persistence | **+0.947** | < 0.0001 |
| H1_count | +0.837 | 0.0007 |

**Interpretation:** Very strong association in pilot. Class A (resistance-resilient) mean H1 total persistence = 3.74 ± 0.34 Å vs Class D = 1.73 Å. However, Class D contains a single compound (n=1); the comparison is descriptive only. The pilot result is included in the manuscript as context for the expanded cohort finding but is not the lead claim.

**Caveats:** n=14 is insufficient for reliable Spearman estimation; the result is heavily influenced by the single Class D outlier. Treat as hypothesis-generating only.

**Numbers in manuscript:** §4.7 (context only, after expanded ρ=0.312 lead), Fig.5 caption.

---

## L004 — QKS polypharmacology benchmark

**Date:** 2026-07-XX  
**Script:** `scripts/p3_qks_benchmark.py`  
**Source:** `results/p3_qks_summary.txt`  
**Method:** IQPEmbedding, 8 qubits, PennyLane lightning.qubit. Polypharmacology label: ≥2 Plasmodium targets at ΔG ≤ −7.0 kcal/mol (10.3% prevalence). 5-fold CV.

| Kernel | AUC | Target Alignment |
|--------|-----|-----------------|
| Quantum (IQPEmbedding) | **0.7512 ± 0.0334** | **0.5432 ± 0.0177** |
| RBF (gamma-tuned) | 0.7007 ± 0.0672 | 0.3343 ± 0.1162 |
| Linear | 0.7208 ± 0.0281 | — |

Paired t-test QK vs RBF: t=2.248, p=0.0878 (not significant).

**Interpretation:** The quantum kernel achieves AUC 0.747 vs RBF 0.737 on polypharmacology prediction — a numerically higher but statistically non-significant difference (p=0.088). This suggests the quantum kernel extracts polypharmacology-relevant information, but the margin over a properly tuned classical kernel is not decisive at this sample size. The target alignment metric (0.543 vs 0.334) shows stronger separation, indicating the quantum kernel geometry is more aligned with the polypharmacology label structure.

**Caveats:** Subsample evaluation (not full 19,849); statistical power limited. The p=0.088 result does not survive Bonferroni correction.

**Numbers in manuscript:** §4.5 ("AUC 0.747 vs RBF 0.737"), Tab.3 (TA=0.543).

---

## L005 — TDA promiscuity correlations (N=17,011)

**Date:** 2026-07-XX  
**Script:** `scripts/p3_physical_validation.py`  
**Source:** `results/p3_physical_validation/p3_tda_promiscuity.csv`  
**Method:** Spearman and Pearson correlations between TDA features and number of Plasmodium targets bound (ΔG ≤ −7.0 kcal/mol). N=17,011 molecules from Tartarus docking output.

| TDA feature | Spearman ρ | p-value |
|-------------|:----------:|:-------:|
| H0_count | −0.248 | 2.54 × 10⁻²³⁶ |
| H0_entropy | −0.243 | 1.18 × 10⁻²²⁶ |
| H1_entropy | −0.190 | 1.91 × 10⁻¹³⁷ |
| H0_max_pers | −0.152 | 4.05 × 10⁻⁸⁸ |

**Interpretation:** Lower topological complexity (fewer H0 components, lower H0/H1 entropy) correlates with higher multi-target binding. This is mechanistically interpretable: simpler ring systems and fewer disconnected components confer conformational flexibility that reduces steric clash penalties when binding multiple structurally distinct active sites. The correlations are modest in magnitude (|ρ| ≤ 0.25) but highly significant given N=17,011.

**Caveats:** Docking scores (QuickVina) approximate experimental binding affinity. Correlation ≠ causation; confounders (molecular weight, lipophilicity) not controlled.

**Numbers in manuscript:** §4.5, Fig.4 (p3_tda_promiscuity.png).

---

## L006 — TNE Tartarus regression (3 Plasmodium targets)

**Date:** 2026-07-XX  
**Script:** `scripts/p3_physical_validation.py`  
**Source:** `results/p3_physical_validation/p3_physical_validation_summary.txt`  
**Method:** Random Forest regression (`RandomForestRegressor`, `n_estimators=100`, `random_state=42`, 5-fold CV) with TNE (192-dim, d=8) vs ECFP4 (2048-bit) descriptors predicting docking scores.

**CORRECTION 2026-08-02:** this entry previously recorded "Ridge regression". That was wrong. `scripts/p3_physical_validation.py` — the only script that writes `p3_tne_regression.csv` — imports `RandomForestRegressor` (line 65) and instantiates it for both the TNE and the ECFP4 arm (lines 239, 252); the file contains no `Ridge` import. Main-manuscript line 463 ("Random Forest regressors") was therefore correct all along and the ledger was the defective record. Note the tree count differs between analyses: 100 here, 200 in the classical benchmark (L001); neither count is currently stated in the manuscript.

**Open — docking engine.** The manuscript and this entry say QuickVina. The Tartarus platform (Nigam et al., NeurIPS 2023, arXiv:2209.12487) ships both `qvina` and `smina` and its documentation describes scoring with smina. Confirm which binary the docking run invoked before submission.

| Target | TNE R² | TNE ρ | ECFP4 R² | ECFP4 ρ | N |
|--------|--------|-------|----------|---------|---|
| PfDHFR (1SYH) | **0.473** | **0.694** | 0.451 | 0.683 | 11,878 |
| PfATP4 (6Y2F) | 0.464 | 0.654 | **0.570** | **0.762** | 17,075 |
| PfCRT (4LDE) | 0.334 | 0.585 | **0.515** | **0.733** | 17,074 |

**Interpretation:** TNE (5.9× real-atom compression) retains substantial binding-relevant information — it outperforms ECFP4 for PfDHFR, which has the smallest dataset (N=11,878) and may benefit from TNE's 3D structural encoding. For the two larger targets, ECFP4 maintains an advantage, consistent with the primacy of local pharmacophoric features for high-N regression. The 192-element TNE descriptor achieves this with 15.6× compression of the padded representation.

**Caveats:** R² values based on QuickVina docking scores, not experimental Kd/IC50. TNE regression is linear (Ridge); non-linear methods may yield different comparisons.

**Numbers in manuscript:** §4.4 ("R²=0.473 for PfDHFR"), Fig.3 (p3_tne_parity.png).

---

## L007 — Hybrid benchmark (TFP+TNE+QK, PROVISIONAL)

**Date:** Pre-2026-07-29 (original run file missing); status: rerun in progress on HPC (job 12621, n=5000)  
**Authority:** BMAD_Q1_DATA_ANALYSIS_REPORT.md §3.5  
**Status:** ⚠️ PROVISIONAL — original full 19,849-molecule hybrid run not reproducible from current code/data files.

| Method | AUC | ΔAUC vs ECFP4 | p vs ECFP4 |
|--------|-----|----------------|-----------|
| ECFP4 (baseline) | 0.868 | — | — |
| Hybrid (TFP+TNE+QK) | **0.842** | −0.026 | 0.111 (n.s.) |
| Hybrid − QKS | 0.608 | −0.260 | < 0.001 |
| Hybrid − TFP | 0.837 | −0.031 | 0.044 |
| Hybrid − TNE | 0.835 | −0.033 | 0.038 |
| v2 single-scalar QK | 0.691 | −0.177 | 0.003 |

Optimal weights: α=0.10 (TFP), β=0.10 (TNE), γ=0.80 (QK-PCA).

**Interpretation (provisional):** The hybrid with 10 kernel-PCA quantum components (AUC 0.842) substantially outperforms the prior single-scalar QK density approach (AUC 0.691) and is not significantly different from ECFP4 (p=0.111). The ablation confirms QKS is the primary driver (removing it drops AUC by 0.234). These values are pending the HPC rerun (job 12621, n=5000 with `--precompute-kernel`); smoke test at n=500 gave ECFP4=0.819, Hybrid=0.755 (p=0.032, Hybrid significantly lower at small n, likely due to overfitting in high-dimensional TFP/TNE space).

**⚠️ DO NOT DRAW CONCLUSIONS from hybrid vs ECFP4 until rerun completes.**

**Caveats:** Original run file missing. Smoke test (n=500) shows different ordering (Hybrid < ECFP4, p=0.032) suggesting n-dependence. The n=5000 run will clarify. Manuscript reports these values as provisional in Tab.2.

**Numbers in manuscript:** Tab.2 (tab:hybrid) — marked provisional in caption.

---

## L008 — Scaffold paradox Tanimoto analysis

**Date:** 2026-07-XX  
**Method:** Whole-molecule vs scaffold-only Tanimoto similarity between 396 African NP seeds and 5,000 generated molecules (ECFP4, radius=2).

| Metric | Value |
|--------|-------|
| Whole-molecule Tanimoto (mean) | 0.206 |
| Scaffold-only Tanimoto (mean) | 0.379 |
| Ratio | **1.84×** |
| ECFP4-unreachable fraction | 92.6% |
| Scaffold recovery | 69.3% |

**Interpretation:** The 1.84× higher scaffold Tanimoto vs whole-molecule Tanimoto quantifies the scaffold paradox: generated molecules diverge in side-chain chemistry (captured by whole-molecule ECFP4) while retaining core ring architectures (captured by scaffold-only ECFP4). TDA confirms this mechanistically — H1 persistence distributions are similar between seed and generated sets (preserved ring topology) while H0 counts diverge (structural component variation).

**Numbers in manuscript:** §4.3, Abstract ("92.6%… 69.3%").

---

## L009 — QKS vs RBF vs Linear kernel comparison (N=10,000 subsample)

**Date:** 2026-07-XX  
**Source:** `results/p3_qks_summary.txt`  
**Method:** 5-fold CV on 10,000-molecule subsample. RBF gamma optimised by inner CV on grid {0.5, 1.0, 2.0, 5.0}.

| Kernel | AUC | Target Alignment | p vs QK |
|--------|-----|-----------------|---------|
| Quantum (IQPEmbedding, 8q) | 0.751 | **0.543** | — |
| RBF (gamma-tuned) | 0.701 | 0.334 | 0.088 (n.s.) |
| Linear | 0.721 | — | 0.063 (n.s.) |

**Interpretation:** All three kernels are statistically indistinguishable (all p > 0.05). The earlier apparent quantum advantage (QK=0.936 vs RBF=0.105, p=0.0003) was an artefact of untuned RBF gamma producing near-uniform similarity values. With proper inner-CV tuning, the advantage vanishes. This is a key methodological lesson reported in the Discussion.

**Numbers in manuscript:** Tab.3 (tab:qkernel), §4.6 Discussion.

---

## L010 — Figure 1 population TDA summary statistics

**Date:** 2026-07-31 (computed from `p3_tda_fingerprints.csv` for new figure)  
**Script:** `scripts/p3_plot_persistence_diagrams_population.py`  
**Source:** `results/p3_tda_fingerprints.csv` (N=19,849)

| Metric | Value |
|--------|-------|
| Total molecules | 19,849 |
| H1_count > 0 | 19,849 (100%) |
| H0_mean_pers median | 1.60 Å |
| H1_mean_pers range | 0.236 – 1.400 Å |
| H1_birth_mean range | 1.078 – 4.180 Å |
| H1_death_mean range | 1.813 – 4.989 Å |
| H2_count ≥ 1 | 587 (3.0%) |
| High-pers ANP exemplar (top-20%) | p̄ = 0.78 Å |
| Low-pers exemplar (bottom-10%) | p̄ = 0.42 Å |

**Numbers in manuscript:** Fig.1 caption — "587 molecules (3.0%)" and the H₀ median 1.60 Å.

**Update 2026-08-02:** Figure 1 now renders from `persistence_diagrams_v2.pdf`. The high- and low-persistence exemplar annotations (p̄ = 0.78 Å top-20%, p̄ = 0.42 Å bottom-10%) are **no longer drawn and no longer cited in the caption** — the v2 H₁ panel shows the hexbin density without singling out individual molecules. Both values stay recorded here but are currently unused by the manuscript; restore them to the caption only if a version that marks the exemplars is chosen instead.

---

## L011 — q_cadd_2026 citation status

**Date:** 2026-07-31  
**Issue:** BibTeX entry `q_cadd_2026` has `pages = {54321}` — appears to be a placeholder. Scientific Reports 2026 typically uses article numbers, not page numbers. DOI `10.1038/s41598-026-44978-4` could not be resolved via available tools (network restricted).

**Status:** `[PLACEHOLDER — VERIFY]`. Author must confirm whether 54321 is the actual article number or a placeholder. If Scientific Reports uses article numbers (common since 2020), the correct BibTeX field is `article_number = {54321}` or `pages = {54321}` (some styles render either the same way). The DOI format `10.1038/s41598-026-44978-4` appears structurally valid for Sci. Reports 2026 (year encoded in DOI suffix).

**Action required:** Author to verify article number at https://doi.org/10.1038/s41598-026-44978-4 before submission.

---

## L012 — GA-style discriminator benchmark (quantum kernel density vs ECFP4 Tanimoto)

**Date:** entry written 2026-07-31 from the deposited run
**Script:** `scripts/p3_ga_discriminator.py`
**Source:** `results/p3_ga_discriminator.csv`
**Method:** STONED-SELFIES molecules generated by 2 random character mutations from a 200-compound reference pool (105 active, 95 inactive by eos80ch). Task: separate reference molecules (label 1) from generated molecules (label 0). Classical scorer = maximum ECFP4 Tanimoto to any seed. Quantum scorer = mean IQPEmbedding kernel similarity to the reference set, 8 qubits, `lightning.qubit`.

| N generated | AUC Tanimoto | AUC quantum kernel | ΔAUC |
|---|---|---|---|
| 50 | 1.0000 | 0.4252 | −0.5748 |
| 100 | 1.0000 | 0.4811 | −0.5189 |
| 200 | 1.0000 | 0.4755 | −0.5245 |
| 500 | 1.0000 | 0.5114 | −0.4886 |

**Interpretation:** The classical scorer separates the two sets perfectly at every N, the quantum kernel density does not separate them at all. Two mechanisms produce this, and they point in opposite directions. The Tanimoto result is partly an artefact: two SELFIES-character mutations sometimes return the original string, so a fraction of the "generated" set is seed-identical, and a perfect AUC is then trivially obtainable. The quantum result is not an artefact but a consequence of the pipeline — UMAP compresses 2048-bit fingerprints to 8 dimensions before encoding, and that reduction discards exactly the atom-level resolution the task requires. Below-random AUC at N ≤ 200 indicates the reduced space actively inverts proximity for near-identical pairs rather than merely losing signal. The practical reading is narrow: for applicability-domain work on molecules that sit close to their training seeds, a fingerprint distance is the right tool, and the quantum kernel should be reserved for structurally heterogeneous sets where its non-linear geometry has something to act on.

**Caveats:** the seed-identical contamination is not quantified in the deposited run; the Tanimoto AUC of 1.000 should not be reported as evidence of classical superiority without it. Reference pool fixed at 200 for all four N values, so the two axes are not independent.

**Numbers in manuscript:** Tab.5 (`tab:ga_discriminator`), Fig.6 caption, Discussion L509, Limitations L546.

---

## L013 — Quantum kernel hyperparameter optimisation (two phases)

**Date:** entry written 2026-07-31 from the deposited runs
**Source:** `results/figures/p3_qp_optimization_table.csv` (Phase 1), `results/p3_quantum_params_sweep.csv` (Phase 2)
**Method:** bond dimension d, IQP repetition layers r, and kernel-PCA component count k tuned against mean 5-fold CV AUC. Phase 1 at n = 200 for breadth; Phase 2 re-runs the leading configuration at n = 5000 with 8-core CPU parallelism and the JAX CPU backend (`JAX_PLATFORMS=cpu`), Jobs 12340–12342.

**Phase 1 (n = 200), deposited rows:**

| d | r | k | AUC | σ | wall time (s) |
|---|---|---|-----|---|---------------|
| 4 | 3 | 20 | 0.8195 | 0.0455 | 385.4 |
| **6** | **1** | **30** | **0.8534** | **0.0489** | 307.4 |
| 8 | 1 | 20 | 0.8431 | 0.0541 | 416.5 |

**Phase 2 (n = 5000), deposited row:**

| d | r | k | AUC | σ | wall time (s) |
|---|---|---|-----|---|---------------|
| 6 | 1 | 30 | 0.8283 | 0.0371 | 21,718.9 |

**Interpretation:** The optimum sits at a single repetition layer and the largest tested KPCA basis, which is the configuration that keeps the encoding shallow while retaining the most kernel structure downstream. Adding repetition layers costs AUC rather than gaining it — consistent with deeper IQP encodings driving the kernel matrix toward concentration, where off-diagonal entries collapse and the SVM loses discriminative geometry. Scaling from n = 200 to n = 5000 lowers AUC from 0.853 to 0.828 while cutting the standard deviation by a quarter (0.049 → 0.037); the n = 200 estimate was optimistic and unstable, and the n = 5000 value should be treated as the honest one. Wall time rises by a factor of about 70 for a 25-fold increase in n, tracking the expected O(N²) kernel cost.

**CORRECTION (same day, after reading BMAD_Q1 §3.5):** an earlier draft of this entry recorded the two Phase-2 comparison runs as undeposited. That was wrong — it checked only `p3_quantum_params_sweep.csv`. BMAD_Q1 lines 882–884 name all three runs with their files, and all three are present in `results/`:

| Combo | d | r | k | AUC (n=5,000) | σ | time (s) | Source |
|---|---|---|---|---|---|---|---|
| 1 (best) | 6 | 1 | 30 | 0.8283 | 0.0371 | 21,719 | `p3_phase2_bd6_nr1_nk30_raw.csv` |
| 2 | 6 | 6 | 30 | 0.8121 | 0.0396 | 28,282 | `p3_phase2_bd6_nr6_nk30_raw.csv` |
| 3 | 6 | 6 | 20 | 0.8047 | 0.0354 | 27,914 | `p3_phase2_bd6_nr6_nk20_raw.csv` |

All three Phase-2 values are BACKED. Jobs 12340–12342, SLURM array, 8 CPU cores per task.

**Caveat that does survive — the Phase-1 grid is misdescribed in the manuscript.** Methods L228 states d ∈ {4, 6, 8} × r ∈ {1, 3, 6} × k ∈ {10, 20, 30} = 27 combinations. BMAD_Q1 line 856 records the actual search: **3 × 5 × 4 = 60 combinations**, with r ∈ {1, 2, 3, 4, 6} and k ∈ {5, 10, 20, 30}, Job 7962, **terminated after 50 of 60**. Both parameter sets, the total, and the truncation are stated incorrectly or not at all. See claims-evidence-matrix H3b.

**Numbers in manuscript:** Methods §2.6 L228.

---

## L014 — Enriched-TFP / SOTA topological benchmark (n = 19,849)

**Date:** entry written 2026-07-31 from the deposited run
**Source:** `results/p3_sota_benchmark_full.csv`
**Method:** five topological feature sets compared under identical conditions — Random Forest at n = 19,849 and SVM at n = 5,000, both 5-fold CV.

| Strategy | features | RF AUC ± σ | RF accuracy | RF F1 | SVM AUC (n=5000) |
|---|---:|---|---|---|---|
| PersStats | 22 | **0.87308 ± 0.00672** | 0.8332 | 0.8906 | 0.8042 |
| TFP-12 | 12 | 0.86681 ± 0.00650 | 0.8275 | 0.8858 | 0.7857 |
| TFP-Enriched | 32 | 0.86656 ± 0.00518 | 0.8308 | 0.8887 | 0.7891 |
| PersImage | 25 | 0.85955 ± 0.00534 | 0.8265 | 0.8856 | 0.7912 |
| BettiCurve | 20 | 0.81098 ± 0.00435 | 0.7837 | 0.8557 | 0.7198 |

**Interpretation:** Enriching the 12-statistic fingerprint to 32 features by adding persistence images and Betti curves changes nothing measurable: ΔAUC = −0.0002, well inside one standard deviation. The finer-grained descriptors are not adding information the four summary statistics per homology dimension had already captured — which is a real negative result worth reporting, since it says the compression from a full persistence diagram to its summary moments is nearly lossless for this classification task. Betti curves alone are the weakest of the five (0.811), consistent with discarding persistence magnitude and keeping only feature counts across the filtration. PersStats edges out TFP-12 by 0.006, again inside noise.

**Two files, two sample sizes — do not mix them.** `p3_sota_benchmark.csv` carries `n_molecules = 5000` (Job 12061 smoke test); `p3_sota_benchmark_full.csv` carries `n_molecules = 19849` for the RF rows. The table above is the full-library file. BMAD_Q1 line 1785 confirms the split and names 0.8419 as the n=5,000 PersStats value against 0.8731 at n=19,849.

**BMAD_Q1's own E.1 table (line 1755–1766) mixes the two.** Its PersStats AUC cell holds the n=19,849 value (0.8731) while its TFP-Enriched (0.8381), PersImage (0.8370), TFP-12 (0.8303) and BettiCurve (0.7717) cells hold n=5,000 values, and every accuracy/F1 cell in that table is from the n=5,000 file. When quoting the enriched-vs-baseline comparison, take both members of the pair from the same file. At n=19,849 the pair is 0.86681 vs 0.86656 (Δ = −0.0002); at n=5,000 it is 0.8303 vs 0.8381 (Δ = +0.0078). BMAD_Q1 finding #3 (line 1771, "ΔAUC < 0.01") holds either way.

**Caveats — this entry contradicts two statements in the current manuscript.** Line 546 attributes 78 features to the enriched TFP; both the deposited runs and BMAD_Q1 lines 1758/1771 say 32. Lines 533 and 546 give the 12-feature TFP baseline as AUC 0.587; that value is in no result file and in no BMAD_Q1 table. **The authoritative TFP figure is 0.877 ± 0.006** (BMAD_Q1 §3.4 line 841, `p3_classical_benchmark_19849.csv`), which is what Table 1 already prints.

The 0.877-vs-0.867 gap is explained, not a defect: the SOTA benchmark runs `class_weight='balanced'` against a 75.9 %/24.1 % imbalance (BMAD_Q1 lines 1773, 1777) while the classical benchmark does not. Different weighting, same data. Quote 0.877 for the headline descriptor comparison and 0.867 only inside the class-weighted topological comparison, never interchangeably. See claims-evidence-matrix C1 and H1.

**Numbers in manuscript:** Limitations L546 (currently with the wrong feature count and the wrong AUC).

---

## HOLDs status (as of 2026-07-31)

| Hold | Description | Status |
|------|-------------|--------|
| H1 | ΔAUC footnote: mean−baseline (+0.075) vs matched per-fold (−0.017) convention | OPEN — author decision needed |
| H5 | Zenodo DOI `10.5281/zenodo.19608875` — reserved, not yet published | OPEN — publish before submission |
| L6 | `q_cadd_2026` pages=54321 placeholder | OPEN — see L011 above |
| **C1** | TFP AUC 0.587 (L533, L546). **Authority BMAD_Q1 §3.4 L841 = 0.877 ± 0.006**; 0.587 is in no result file and no BMAD table | **OPEN — CRITICAL.** Rewrite both sentences to 0.877; the "poor activity prediction" premise of the paradox argument at L533 does not survive |
| **H1b** | "enriched TFP (78 features)" — authority BMAD_Q1 L1758/L1771 and both deposited runs say 32 | OPEN — correct to 32 |
| **H2b** | Silhouette 0.350 / 0.229 / 0.180 (Tab.4) — no source file, no script, **and absent from all 2,018 lines of BMAD_Q1** | OPEN — deposit or remove. CH and DB indices promised in Methods L234 are never reported |
| ~~H3b (old)~~ | ~~Phase-2 configs undeposited~~ | **RETRACTED 2026-07-31** — all three raw CSVs exist; BMAD_Q1 L882–884. Finding was based on checking one file only |
| **H3b (new)** | Phase-1 grid misdescribed: manuscript L228 says 27 combos, r∈{1,3,6}, k∈{10,20,30}. BMAD_Q1 L856 says **60 combos**, r∈{1,2,3,4,6}, k∈{5,10,20,30}, **truncated at 50/60** (Job 7962) | OPEN — correct the grid spec and disclose the truncation |
| **H4b** | `tab:qkernel` Linear p = 0.198 labelled "vs RBF"; L009 has 0.063 vs QK | OPEN — fix header or cite the right test |
| **H5b** | ΔAUC column retained in Tab.1/Tab.2 for rows whose comparisons Tab.2's caption withdraws | OPEN — drop the column for provisional rows |
| **H6b** | **QKS subsample size.** Manuscript says 10,000 in 5 places (Tab.1 fn L323, Tab.2 fn L457, Tab.3 caption L357, §4.5 L351, Methods). BMAD_Q1 §3.3 L815/L823 and summary L20 say the run was **500 molecules**, with 10,000 as the design target. BMAD_Q1's own inventory L1741 still says 10,000 | **OPEN — HIGH.** Author must state the actual n; a 20× overstatement of the evaluation set is a reproducibility failure |
| **H7b** | **Target alignment.** Authority BMAD_Q1 §3.3 L820 = **0.684 ± 0.021**; manuscript Tab.3 and L004/L009 carry 0.543 from `p3_qks_summary.txt`. PHASE10-FIX changed 0.684 → 0.543 on the CSV's authority, against the rule that BMAD_Q1 outranks intermediate CSVs | **OPEN — HIGH.** Author ruling needed on which is canonical |
| **H8b** | **Circuit name.** BMAD_Q1 §3.3 L817 labels the QKS column "Quantum Kernel (StronglyEntanglingLayers)". Phase 12 unified the manuscript on `IQPEmbedding` citing "§3.4", but §3.4 is the classical benchmark section and names no circuit | OPEN — reconcile with the author |
| **M4b** | TNE recon error 0.098 vs 0.137; mode-3 vs molecular volume ρ = 0.71 (L503) — no source, absent from BMAD_Q1 | OPEN — deposit or remove |
| ~~M9, M10~~ | ~~TNE 19,836 valid / 13 failed / 15.6× / 0.113 / 20 min; H₀ mean 38 SD 7~~ | **CLOSED 2026-07-31** — BMAD_Q1 §3.2 L804–811 and §3.1 L796 confirm all of them |
