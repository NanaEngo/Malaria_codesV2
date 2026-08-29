# Review B — Inferential Statistics

**Manuscript:** *Topological and tensor-network representations resolve chemical paradoxes in African antimalarial natural products* (target: Journal of Cheminformatics)
**Files reviewed:** `manuscript/LaTeX/Paper3_Quantum_InspiredV2608.tex` (MAIN, 433 ll.), `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2608.tex` (SM, 731 ll.), deposited outputs in `results/`, generating scripts in `scripts/`.
**Scope:** inferential logic only — test choice, assumptions, effective df, null-result framing, multiplicity, effect sizes/CIs, causal language on correlations, confounder-set fidelity, class imbalance and label provenance. Arithmetic reproduction was not the remit; discrepancies are noted only where they change an inference.
**Reviewer note:** `outputs/analysis/analysis-ledger.md` and `project-tracking.md` were deliberately not read.

Severity key: **CRITICAL** = invalidates a headline claim as stated · **HIGH** = must be fixed before acceptance · **MEDIUM** = weakens rigor, fixable in revision · **LOW** = precision/reporting.

---

## §0. Executive summary

The manuscript is unusually self-aware about its own nulls — MAIN:227 contains an explicit and correct statement that non-significance is not equivalence, and the H₁–RRS confound is disclosed rather than buried. That good instinct is undermined by four structural problems:

1. Every inferential p-value in the paper is a paired *t*-test on 5 cross-validation folds (df = 4) drawn from **overlapping training sets**, so the reported *t* statistics are inflated by an unknown, unmodelled factor and the nominal df overstate the information content. Cohen's *d* values up to **63.8** are the diagnostic symptom, not a finding.
2. The **stated multiplicity correction covers 7 tests; the family actually computed is ≥ 204** (§3).
3. The **MW-only partial correlation (p = 0.85)**, cited five times including in the Abstract, **does not exist in any deposited output or script** (§5.1). The confounder set described in the text is not the confounder set the deposit shows.
4. The polypharmacology/promiscuity claim carries **explicit mechanistic causal language** on a ρ = −0.25 correlation whose strongest predictor (H₀ count) *is* molecular size — the exact confound the authors correctly controlled for elsewhere and did not control for here (§6.1). The deposited table's 95 % CI columns are **empty**, while the figure caption asserts CI error bars.

Bootstrap CIs are promised in MAIN:227 for the two comparisons that matter most and are delivered for neither.

---

## §1. Complete enumeration of hypothesis tests (DONE-CRITERION 1)

**Legend for verdict:** ✅ valid as reported · ⚠️ valid test, over-read or under-specified · ❌ invalid, unsupported, or absent.

### 1A. Tests with a reported p-value, main manuscript

| # | Test | Location | Statistic reported | p | df / n | Verdict |
|---|---|---|---|---|---|---|
| T1 | Hybrid vs ECFP4 AUC, paired *t* | MAIN:100, 251, 315, 345, 353, 380, 388 | t = −29.902 | < 0.0001 | df = 4 (5 CV folds) | ⚠️ Test correct in form; folds non-independent → *t* and df both inflated. Direction is not in doubt (Δ = 0.060 ≫ fold SD 0.0065), conclusion survives; the *statistic* does not. Report Δ + bootstrap CI instead. |
| T2 | Quantum kernel vs gamma-tuned RBF, n = 5000 | MAIN:100, 301, 353, 388; SM:683, 693, 700 | t = −0.901 | 0.4186 | df = 4 | ⚠️ Underpowered null (§4). Correctly hedged in MAIN:227 but upgraded elsewhere. |
| T3 | Quantum vs RBF, n = 19 849 | MAIN:100, 127, 279, 301, 353, 388; SM:683, 693 | t = −2.594 | 0.0604 | df = 4 | ⚠️ Same. Note the point estimate favours **RBF** (0.8292 vs 0.8230); "no significant difference" is a null, not parity. |
| T4 | Quantum vs linear, n = 5000 | MAIN:301, 388; SM:683, 707 | t = 12.736 | 0.0002 | df = 4 | ✅ Direction robust (Δ ≈ 0.30). Multiplicity uncorrected. |
| T5 | Quantum vs linear, n = 19 849 | MAIN:301, 388; SM:683, 707 | t = 9.733 | 0.0006 | df = 4 | ✅ Same. |
| T6 | H₁ count vs RRS, Spearman | MAIN:100, 361, 363, 368, 376, 380; SM:104, 639 | ρ = 0.3124 | 0.005679 | n = 77 (df = 75) | ❌ **Fails the paper's own implicit family correction.** 11 H₁ features were tested against RRS (`results/p3_h1_rrs_correlation_final.txt`); Bonferroni α = 0.05/11 = 0.00455 < 0.005679. The headline "nominally significant" association is **not significant** once the tested feature set is acknowledged. See §3.2. |
| T7 | Pilot H₁ total persistence vs RRS | MAIN:100, 361, 368, 376, 380; SM:104, 639 | ρ = 0.947 | < 0.0001 | n = 14 (df = 12) | ⚠️ Reported repeatedly as context. The 95 % CI on ρ at n = 14 is roughly [0.83, 0.98] — but this is the *selected maximum* of the same 11-feature screen at n = 14, so it is a winner's-curse estimate. Never labelled as such. |
| T8 | H₁ count vs RRS, partial, **MW only** | MAIN:100, 361, 368, 376; SM:104, 639 | ρ_partial ≈ 0 | **0.85** | n = 77 | ❌ **CRITICAL — no such analysis exists.** `scripts/p3_h1_rrs_partial_corr.py:89` hard-codes `confounders = ["MW","n_rings","Fsp3","H0_count"]`; there is no single-covariate branch, no CLI override, and no output file containing p = 0.85. See §5.1. |
| T9 | H₁ count vs RRS, partial, 4 covariates | MAIN:361; SM:639 | ρ_partial = −0.0388 | 0.7447 | n = 77, df = 71 | ✅ Correctly computed and correctly reported as a failure to reject. Good practice. |
| T10 | H₀ count vs # targets bound, Spearman | MAIN:325; SM:575, 580 | ρ = −0.2478 | 2.5 × 10⁻²³⁶ (stated "< 10⁻¹³⁷") | n = 17 011 | ❌ p is real; the **inference is not** (§6.1). H₀ count ≈ heavy-atom count (mean 38.04, SM:192, vs mean 39 atoms/molecule, MAIN:186) → this is a molecular-size correlation dressed as topology. No size adjustment, unlike T9. |
| T11 | H₀ entropy vs # targets bound | MAIN:325; SM:575 | ρ = −0.2428 | 1.2 × 10⁻²²⁶ | n = 17 011 | ❌ Same. |
| T12 | H₁ entropy vs # targets bound | MAIN:325; SM:575 | ρ = −0.1896 | 1.9 × 10⁻¹³⁷ | n = 17 011 | ❌ Same. ρ² = 3.6 % of rank variance carrying a full steric-clash mechanism (§6.1). |
| T13 | Historical 8-qubit QK vs RBF, n = 5000 | MAIN:378; SM:599, 693 | — | 0.003 | df = 4 | ⚠️ Cited as a superseded artefact. Acceptable, but it enters the multiplicity family. |
| T14 | Historical 8-qubit QK vs RBF, n = 19 849 | MAIN:378; SM:599, 693 | — | 0.0006 | df = 4 | ⚠️ Same. |
| T15 | Wilcoxon, H₁ persistence seed vs expanded | MAIN:291 (Fig. 1 caption: "Wilcoxon $p$-value") | **none** | **none** | **none** | ❌ **A test is announced in a figure caption and its value never appears** in main text, SM, or `results/`. No `scaffold_paradox` output file exists (`ls results/` — absent; only `Graphics/scaffold_paradox.pdf`). The scaffold-paradox resolution (contribution N6, MAIN:123) rests on this unreported test. |

### 1B. Tests with a reported p-value, Supplementary Material

| # | Test | Location | Statistic | p | df | Verdict |
|---|---|---|---|---|---|---|
| T16 | FCFP4 vs ECFP4 | SM:399 → `results/p3_effect_sizes/p3_effect_sizes_table.tex` | t = −25.956, d = +11.61 | < 0.0001 | 4 | ⚠️ *d* on an invalid scale (§4.2). |
| T17 | MACCS vs ECFP4 | idem | t = −33.220, d = +14.86 | < 0.0001 | 4 | ⚠️ idem |
| T18 | AP vs ECFP4 | idem | t = −10.152, d = +4.54 | 0.0005 | 4 | ⚠️ Passes Bonferroni α = 0.0071 for k = 7 only; fails α = 0.00025 for the true family. |
| T19 | PHCO vs ECFP4 | idem | t = −142.759, **d = +63.84** | < 0.0001 | 4 | ❌ d = 63.8 labelled "large" against Cohen's 0.8 threshold. This is a *d_z* on correlated folds; it is not interpretable on Cohen's scale at all. |
| T20 | BPF vs ECFP4 | idem | t = −12.051, d = +5.39 | 0.0003 | 4 | ⚠️ idem |
| T21 | TFP vs ECFP4 | idem | t = −38.569, d = +17.25 | < 0.0001 | 4 | ⚠️ idem |
| T22 | TNE vs ECFP4 | idem | t = −84.759, d = +37.91 | < 0.0001 | 4 | ⚠️ idem |
| T23 | RBF vs linear, n = 5000 | SM:683 | t = 14.760 | 0.0001 | 4 | ✅ direction robust |
| T24 | RBF vs linear, n = 19 849 | SM:683 | t = 9.788 | 0.0006 | 4 | ✅ direction robust |
| T25 | MC uncertainty vs prediction error, Spearman | SM:361 | ρ = −0.286 | 0.0039 | n = 100 | ❌ Reported as "weak … consistent with the MC uncertainty not reliably flagging misclassifications." It is **significant at p = 0.004** and **negatively** signed, i.e. higher predicted uncertainty ↔ *lower* error — an actively anti-calibrated uncertainty estimate, not a weak one. The sign is never discussed. |
| T26 | PersStats vs ECFP4, SOTA family | SM:520 | **no statistic** | "p > 0.05" | unstated | ❌ A p-value is asserted with no test name, no statistic, no df, and no deposited output (`results/p3_sota_benchmark_full_summary.txt` contains ΔAUC only). |
| T27–T31 | Partial-correlation table, 4 further predictors (H₁ entropy, H₁ total pers. prod., H₁ total pers. sum, H₁ max pers.), total **and** partial | `results/p3_h1_rrs_partial_corr.csv` (deposited, feeds SM:639 claim) | ρ_total 0.254 / 0.263 / 0.361 / 0.067; ρ_partial −0.070 / 0.031 / 0.030 / 0.188 | 0.0256 / 0.0210 / **0.00125** / 0.5606 | n = 77 | ⚠️ **10 tests deposited, 2 reported.** Note H₁_total_pers_sum (p = 0.00125) is the *only* predictor that survives Bonferroni at k = 11 — yet the manuscript headlines H₁ count (p = 0.0057), which does not. Selective reporting of the non-surviving predictor. |
| T32–T35 | TNE vs ECFP4 docking-score Spearman, 3 targets × 2 descriptors | SM:571; `results/p3_physical_validation/p3_tne_regression.csv` | ρ = 0.585–0.762 | all reported as 0.0 | n = 11 878 / 17 075 / 17 074 | ⚠️ p = 0.0 is an underflow artefact, not a p-value. Text quotes ρ without p or CI. |

### 1C. Comparisons asserted with **no test at all** (each is a hypothesis claim in the prose)

| # | Claim | Location | Verdict |
|---|---|---|---|
| T36–T38 | Hybrid ablation: −QKS Δ = −0.040 ("principal positive contributor"), −TFP Δ = −0.014, −TNE Δ = **+0.011** | MAIN:255, 270–275, 315, 345, 353, 380; SM:599 | ❌ Three comparisons carrying a causal attribution ("principal positive contributor") with **no p, no CI, no test**. Per-fold data exist (`results/p3_ablation.csv`) — a paired test and CI are one line of code away. The −TNE result (removing a component *improves* AUC) is reported without acknowledging it contradicts the hybrid rationale. |
| T39–T41 | TNE vs ECFP4 R² per target: PfDHFR 0.473 vs 0.461 "outperforming"; PfATP4 0.464 vs 0.578; PfCRT 0.334 vs 0.517 | MAIN:321, 380; SM:571 | ❌ "Outperforming" on ΔR² = +0.012 with **no test, no CI, no repeated-CV variance**. `p3_physical_validation.py:240–260` uses a single `cross_val_predict(cv=5)` pass → one point estimate per descriptor, zero replicates. Deposited ECFP4 R² is 0.4508 (`p3_tne_regression.csv`), not 0.461 (0.4606 is in the older `p3_tartarus_summary.txt`) — so the headline Δ is either +0.012 or +0.022 depending on which deposit is canonical, and neither is testable as presented. |
| T42–T45 | GA discriminator: Tanimoto AUC = 1.000 vs QK AUC = 0.425/0.481/0.476/0.511 at N = 50/100/200/500 | MAIN:311, 345; SM:608; SM:278–281 | ❌ Four AUC comparisons, no DeLong test, no bootstrap CI, no test against AUC = 0.5 for the QK arm. At N = 50 the SE on an AUC is ≈ 0.05, so "below-random" for N ≤ 200 is not distinguishable from 0.5. The manuscript nonetheless builds a mechanistic story ("the reduced space confounds proximity information rather than enhancing it", MAIN:311). |
| T46–T48 | Clustering: TNE Silhouette 0.350 vs VAE 0.229 vs ECFP4 0.180 | MAIN:223, 303, 341; SM:249–251 | ❌ Three comparisons, single point estimates, no resampling, no CI. MAIN:223 pre-registers a threshold ("TNE Silhouette > 0.35 was set as the target") and the observed value is **0.350** — exactly at the threshold, reported as "substantially exceeding". A threshold met to three decimals with no uncertainty estimate is not evidence. |
| T49–T51 | ChEMBL enrichment: 5.43× / **∞** / 1.46×, verdicts "EXCELLENT/EXCELLENT/–" | SM:419–425 | ❌ An **infinite enrichment** (0/87 inactives recovered) reported as a point estimate with an evaluative verdict and no CI. With 87 inactives the one-sided 95 % bound on the inactive rate is ≈ 3.4 %, so finite enrichment bounds are computable and should be. No test of enrichment vs chance for any target. |
| T52 | MLP vs RF on PersStats, ΔAUC = −0.061 | SM:533, 547 | ❌ No paired test despite 5 matched folds and reported SDs (0.014 / 0.015). Conclusion ("tree-based methods better capture PH feature interactions") is a mechanistic claim from an untested Δ. |
| T53 | TNE reconstruction error, common-ring (0.098) vs atypical (0.137) molecules | MAIN:341; SM:630 | ❌ Two-group comparison, no test, no n per group, no dispersion. |
| T54 | TNE mode-3 factor matrix vs molecular volume, ρ = 0.71 | MAIN:341; SM:630 | ❌ Correlation quoted with **no p, no n, no deposited output**. |
| T55 | H₁ count vs MW, ρ = 0.718 | MAIN:361; SM:639 | ❌ Load-bearing for the entire size-mediation argument, yet **no p, no n, and not present in `p3_h1_rrs_partial_corr.csv/.txt`** (which reports only predictor↔RRS rows). |
| T56 | Polypharmacology QKS vs RBF, partial folds | MAIN:323; SM:573 | ❌ 3 completed folds at n = 500 (0.513/0.658/0.825 vs 0.506/0.642/0.803) plus a 2-fold n = 50 pilot, from which "within noise of the tuned RBF baseline" is asserted. Three paired observations cannot support an equivalence statement (§2, item 8). |
| T57 | TFP-Enriched (32 feat.) vs TFP-12, ΔAUC = −0.0002 | MAIN:376; SM:520 | ❌ Δ = −0.0002 is **1/30th of a single fold SD** (0.0052–0.0065), yet SM:520 concludes "the additional 20 features introduce noise rather than signal" — a mechanistic reading of pure noise. |
| T58–T67 | SOTA table Cohen's *d* for 10 strategies vs ECFP4 | SM:504–517 | ❌ *d* "computed approximately … with σ_pooled = 0.006 (RF) and 0.012 (SVM), approximately estimated from fold-level standard deviations across all strategies" (SM:517). A hand-set pooled SD applied to all rows is not an effect size; d = −12.35 for BettiCurve. Compounded by the RF/SVM sample-size confound the authors themselves flag (SM:520 (ii)). |
| T68 | Phase-1 hyperparameter grid, 50 of 60 combinations × 5-fold CV | SM:300, 320 | ⚠️ A 50-way model selection at n = 200 whose winner (d = 6, n_rep = 1, n_kpca = 30) is then reported at n = 5000 and used for every downstream quantum result. Selection-induced optimism on the winning configuration is never acknowledged and no held-out re-selection is performed. Also: **MAIN:219 truncates mid-sentence** — "a grid search evaluated \num{60} combinations" — the Methods description of this search is literally incomplete. |

### 1D. Tests computed and deposited but never surfaced

| Source | Count | Verdict |
|---|---|---|
| `results/p3_physical_validation/p3_tda_promiscuity.csv` | **78 Spearman + 78 Pearson = 156 tests** over all H₀/H₁/H₂/Betti/persistence-image features vs # targets bound | ❌ Three are reported (T10–T12) as "the strongest signals". The other 153 — including 12 with p > 0.05 — are invisible in main + SM. No correction, no mention of the screen size. |
| `results/p3_h1_rrs_correlation_final.txt` | 11 Spearman tests (H₁ entropy, count, max/mean pers., birth mean/std, death mean/std, pers q25/q50/q75) | ❌ One reported. See T6. |
| `results/p3_h1_rrs_partial_corr.csv` | 10 (5 predictors × total + partial) | ⚠️ Two reported. See T27–T31. |

**Enumeration totals:** 26 distinct tests with an asserted p-value (T1–T26, minus in-text duplicates); 33 comparisons asserted with no test (T36–T68); 177 deposited-but-unreported tests (156 + 11 + 10, net of the 5 already counted). **Distinct hypothesis tests in the family: ≥ 204.**

---

## §2. Every non-significant sentence, quoted verbatim (DONE-CRITERION 3)

> **N1** — MAIN:227: *"Because fold-level AUCs are not independent (overlapping training folds), these $t$-tests have limited power ($df = 4$); we therefore interpret non-significance as ``we could not detect a difference'' rather than equivalence, and we report bootstrap \qty{95}{\percent} confidence intervals on the principal AUC differences (ECFP4 vs. hybrid, quantum vs. RBF) in the Supplementary Material."*
> **Verdict: correct in principle, falsified in practice.** This is exactly the right framing and it is the standard the rest of the paper should be held to. But (a) it is stated once, in Methods, and contradicted by N4/N6/N9 below; (b) **the promised bootstrap CIs are not in the SM.** `grep -i "confidence\|bootstrap"` over the SM returns only the Monte-Carlo bootstrap section (SM:344) — no CI on ECFP4 vs hybrid, none on quantum vs RBF. `results/p3_effect_sizes/p3_effect_sizes.csv` *does* contain `CI_95_lower/CI_95_upper` for the seven classical descriptors (computed at `p3_effect_sizes.py:119–128`), but the generated LaTeX table (`p3_effect_sizes_table.tex`) **drops both CI columns**, and neither of the two promised comparisons is in that table. **HIGH.**

> **N2** — MAIN:100 (Abstract): *"The quantum kernel shows no statistically significant difference from a gamma-tuned RBF baseline at any sample size ($p = \num{0.060}$ at $n = \num{19849}$; $p = \num{0.419}$ at $n = \num{5000}$), while significantly outperforming the linear kernel at scale ($p \leq \num{0.0006}$)."*
> **Verdict: over-reads the null.** "No statistically significant difference **at any sample size**" is a universal-quantifier claim built from two underpowered tests (df = 4). The abstract juxtaposes it with a genuine positive ("significantly outperforming the linear kernel"), so a reader parses the pair as *quantum ≈ RBF, quantum > linear* — i.e. parity. It is not parity: the point estimate favours RBF at both n. **Needs TOST.** See §7 recommendation R1.

> **N3** — MAIN:127: *"although our results show that once the RBF kernel is properly tuned and the circuit optimised to 6 qubits, the single IQPEmbedding quantum kernel shows no statistically significant difference from it ($p = \num{0.060}$ at $n = \num{19849}$, with a borderline trend toward lower QK performance)"*
> **Verdict: acceptable.** The "borderline trend toward lower QK performance" clause is the correct reading. Retain this phrasing and propagate it.

> **N4** — MAIN:301: *"\cref{SM-tab:qkernel} shows that, with the canonical 6-qubit circuit and the C3 fix, the gamma-tuned RBF kernel and the quantum kernel show \textbf{no statistically significant difference} at either scale"*
> **Verdict: bolded null.** Typographic emphasis on a non-rejection converts absence of evidence into a finding. The same sentence bolds "**significantly outperforms**" for the linear comparison, giving the two identical visual weight. **MEDIUM** (presentation), but it is the mechanism by which N2 reads as parity.

> **N5** — MAIN:351 (§5.5 heading): *"Kernel Comparison: No Significant Quantum Advantage or Disadvantage at Scale"*
> **Verdict: over-reads the null.** A section *title* asserting "no … disadvantage" is a two-sided equivalence claim. With df = 4 and observed Δ = −0.006 (SD of fold differences ≈ 0.005), the 95 % CI on the quantum−RBF difference comfortably includes disadvantages large enough to matter. **HIGH** — retitle (§7, R1).

> **N6** — MAIN:388 (Conclusion): *"The kernel benchmark with a properly tuned RBF baseline and the canonical 6-qubit circuit found no statistically significant difference between the quantum kernel and the gamma-tuned RBF kernel at any sample size … QKS is therefore best framed as a methodological framework contribution (a NISQ-era proof of concept) that shows no significant advantage over properly tuned classical kernels."*
> **Verdict: mixed.** The second clause ("no significant advantage") is correct and appropriately one-sided. The first clause repeats the "at any sample size" universal. Fix the first, keep the second.

> **N7** — MAIN:323: *"the partial $n=500$ and 2-fold pilot ($n=50$) results (Supplementary Material) show no quantum advantage over the gamma-tuned RBF baseline."*
> **Verdict: correctly one-sided**, and honest about incompleteness. ✅

> **N8** — SM:573: *"These partial results place QKS within noise of the tuned RBF baseline and do not demonstrate a task-specific quantum advantage for polypharmacology classification"*
> **Verdict: "within noise of" is an equivalence claim** made from **3 completed folds** (per-fold QKS 0.513/0.658/0.825 vs RBF 0.506/0.642/0.803). With 3 paired observations and a fold-to-fold AUC range of 0.31, no equivalence bound is estimable. The second clause is fine. Replace "place QKS within noise of" with "are uninformative about any difference from". **HIGH.**

> **N9** — SM:693 (Table S caption) and SM:700 (table body, "$p = 0.419$ / 0.060, **n.s.**"): *"With the canonical circuit, the gamma-tuned RBF kernel and the quantum kernel show \textbf{no statistically significant difference} at either scale"*
> **Verdict: over-reads the null in the most load-bearing artefact.** The "n.s." annotation in a results-table cell is the canonical way a null becomes a positive finding in downstream citation. The table has no CI column. **HIGH** — add Δ AUC with bootstrap CI as a column (§7, R1).

> **N10** — SM:520: *"though this $\Delta$AUC of $+\num{0.005}$ does not reach statistical significance ($p > \num{0.05}$), so the two methods should be interpreted as performing comparably rather than PersStats being definitively superior"*
> **Verdict: over-reads the null and is untraceable.** "Performing comparably" is an equivalence conclusion drawn from a p-value with no accompanying test, statistic, df, or deposited output (see T26). **HIGH.**

> **N11** — MAIN:376: *"the enriched TFP (32 features, adding persistence images and Betti curves) showed no improvement over the 12-feature TFP baseline (RF AUC \num{0.867} versus \num{0.867} at $n = \num{19849}$)"*
> **Verdict: the sentence is fine; SM:520's gloss on it is not.** MAIN correctly says "no improvement". SM:520 escalates the same Δ = −0.0002 to *"suggesting the additional 20 features introduce noise rather than signal"* — a directional mechanistic claim from a difference 30× smaller than the fold SD. **MEDIUM.**

> **N12** — SM:361: *"the uncertainty--error correlation is weak (Spearman $\rho = -\num{0.286}$, $p = \num{0.004}$), consistent with the MC uncertainty not reliably flagging misclassifications."*
> **Verdict: mislabels a significant result as a null, and ignores its sign.** p = 0.004 at n = 100 is not "weak or non-significant" (the wording is inherited verbatim from `results/p3_mc_uncertainty_summary.txt`, whose own interpretation block says "△ Weak or non-significant"). More importantly ρ is **negative**: the model is *more* confident where it is *more* wrong. That is anti-calibration, a substantively different and worse finding than "uninformative". **HIGH.**

> **N13** — MAIN:361 / SM:639 / MAIN:100 / MAIN:368 / SM:104: *"controlling for molecular weight alone collapses the correlation to $\rho_{\text{partial}} \approx 0$ ($p = \num{0.85}$)"* (and MAIN:368/SM:104 variant "$p > \num{0.7}$")
> **Verdict: correct in spirit, unsupported in fact.** As a null-reporting sentence it is exemplary — the authors report their own confound honestly. But the analysis behind it does not exist (§5.1). **CRITICAL.**

> **N14** — MAIN:363: *"why does TFP … show a nominally significant correlation with resistance resilience ($\rho = 0.312$)? … However, the partial-correlation analysis shows this signal is confounded by molecular size; the relationship is therefore hypothesis-generating"*
> **Verdict: correct handling.** ✅ This is the standard the promiscuity analysis (§6.1) should have met and did not.

**Summary of N-verdicts:** 14 non-significant sentences located. **3 correctly reported** (N3, N7, N14, plus N6-second-clause and N11-MAIN); **7 over-read the null into equivalence/parity/comparability** (N2, N4, N5, N6-first-clause, N8, N9, N10); **2 mislabel or misattribute** (N12, N13); **1 states the correct standard but is not honoured** (N1).

---

## §3. Multiple comparisons: family size vs correction applied (DONE-CRITERION 2)

### 3.1 What the manuscript states

> MAIN:227: *"Multiple testing correction used Bonferroni adjustment across the pairwise comparisons within each benchmark family (7 classical-benchmark comparisons; kernel comparisons reported with their paired $t$-test $p$-values)."*

> `p3_effect_sizes_table.tex` footnote: *"$^{*}$ $p < 0.05$ (uncorrected). Bonferroni-corrected $\alpha = 0.05/7 = 0.0071$."*

**Correction applied: k = 7.** The kernel comparisons are explicitly exempted. No correction anywhere for the correlational analyses.

### 3.2 What the family actually is

| Block | Tests | Corrected? |
|---|---|---|
| Classical descriptors vs ECFP4 (T16–T22) | 7 | ✅ Bonferroni k = 7 |
| Hybrid vs ECFP4 (T1) | 1 | ❌ not in the k = 7 set |
| Kernel comparisons, canonical (T2–T5, T23–T24) | 6 | ❌ explicitly exempted |
| Kernel comparisons, historical 8-qubit (T13, T14) | 2 | ❌ |
| H₁ vs RRS Spearman screen (`p3_h1_rrs_correlation_final.txt`) | 11 | ❌ |
| H₁ vs RRS partial-correlation screen (`p3_h1_rrs_partial_corr.csv`) | 10 | ❌ |
| TDA vs promiscuity screen (`p3_tda_promiscuity.csv`) | 78 Spearman + 78 Pearson = 156 | ❌ |
| TNE/ECFP4 docking Spearman (T32–T35) | 6 | ❌ |
| MC uncertainty–error (T25) | 1 | ❌ |
| Hybrid ablation (T36–T38) | 3 | ❌ (no p at all) |
| TNE vs ECFP4 R² (T39–T41) | 3 | ❌ (no p at all) |
| GA discriminator (T42–T45) | 4 | ❌ (no p at all) |
| Clustering (T46–T48) | 3 | ❌ (no p at all) |
| ChEMBL enrichment (T49–T51) | 3 | ❌ (no p at all) |
| MLP vs RF, reconstruction error, mode-3 volume, H₁–MW, TFP-enriched, polypharm (T52–T57) | 6 | ❌ |
| SOTA Cohen's *d* (T58–T67) | 10 | ❌ |
| PersStats vs ECFP4 (T26), Wilcoxon (T15) | 2 | ❌ |
| **Total distinct hypothesis tests** | **≥ 204** | **7 corrected (3.4 %)** |
| Additional model-selection comparisons (Phase-1 grid, T68) | 50 | not a hypothesis family but an unacknowledged optimism source |

### 3.3 Consequences that change conclusions

- **Bonferroni over the true family:** α = 0.05/204 = **2.5 × 10⁻⁴**. Survivors: T1, T4, T5, T10–T12, T16, T17, T19, T21, T22, T23, T24 (and T18/T20 marginally fail at 0.0005/0.0003). **T6 (H₁–RRS, p = 0.0057) fails by a factor of 23.** So does T25 (p = 0.0039).
- **Even the most charitable local correction kills T6.** Restricting to the 11-test H₁–RRS screen alone: α = 0.05/11 = 0.00455 < 0.005679. The Abstract (MAIN:100), Results, Discussion (MAIN:361), Limitations (MAIN:376), and both figure captions describe this as a significant association. **It is not significant under any correction the paper's own family structure implies.** This is CRITICAL for the abstract, HIGH elsewhere (the size-confound caveat already blunts the claim, but the word "significant" must go).
- **The 156-test promiscuity screen is presented as a 3-test result.** MAIN:325 and SM:575 name "the strongest signals" without stating that 78 features were screened. A reader cannot assess selection. Even though the top ρ's survive any correction on p, the *ranking* and the choice of which three to narrate are selection-dependent, and the deposited file shows 12 features with p > 0.05 that are never mentioned.
- **Kernel comparisons are the paper's headline and are explicitly uncorrected** by the authors' own statement. Six tests, α = 0.05/6 = 0.0083: T3 (p = 0.0604) remains non-significant — no change to the conclusion, but the exemption should be justified rather than declared.

---

## §4. Effective degrees of freedom, effect sizes, uncertainty

### 4.1 CRITICAL — 5-fold CV folds are treated as 5 independent samples throughout

Every paired *t*-test in the paper (T1–T5, T13–T14, T16–T24) is `scipy.stats.ttest_rel` over 5 fold-level AUCs (`scripts/p3_effect_sizes.py:110`, and the QKS/hybrid summaries). In 5-fold CV any two training sets share 3/4 of their data. The variance of the fold-mean difference is therefore **underestimated**, the *t* statistic inflated, and the nominal df = 4 is an upper bound on the real information content — the Nadeau–Bengio result is that the naive CV *t*-test has a Type-I error rate several times nominal.

MAIN:227 acknowledges *"these $t$-tests have limited power ($df = 4$)"* — but this frames the problem as *too conservative*, which is the opposite of the truth. The naive CV *t*-test is **anti-conservative**; it makes small differences look significant, it does not make real differences look null. The stated caveat therefore points the reader in the wrong direction and is used to excuse the nulls (N2, N5) while the same inflation is silently accepted for the positives (T1: t = −29.9; T19: t = −142.8).

The paper implies df = 4 for all inferential claims. **The effective df is smaller and unquantified.**

### 4.2 CRITICAL — Cohen's *d* is on an uninterpretable scale and labelled with Cohen's thresholds

`p3_effect_sizes.py:82–96` computes `d = mean(diff) / std(diff, ddof=1)` — a paired *d_z*, whose denominator is the SD of *fold-to-fold differences*, not the SD of the measured quantity. Because CV folds are near-replicates, that SD is tiny (0.0004–0.006), yielding **d = 4.5 to 63.8**. The script then applies Cohen's (1988) thresholds designed for a between-subject *d*: every row is labelled "large" (`p3_effect_sizes.py:88–96`).

The SM caption (`p3_effect_sizes_table.tex`) partially concedes this — *"because the full-library folds are very consistent, the resulting $d$ values are large, so the absolute $\Delta$AUC is the more interpretable effect metric"* — but the table still prints an "Effect" column reading "large" seven times. A reader who takes d = 63.84 (PHCO) at face value would conclude the PHCO–ECFP4 gap is ~80× the FCFP4–ECFP4 gap; in Δ AUC the ratio is 1.8×.

**The manuscript promises effect sizes (SM §8, "Effect sizes for pairwise AUC comparisons") and delivers a quantity that is not an effect size for this design.**

### 4.3 HIGH — post-hoc "observed power" is circular

`p3_effect_sizes.py:130–142` computes power from the *observed* effect size at n = 5. All seven rows report Power = 1.000, printed in the SM table under a footnote reading *"Power computed for 80\% target at $\alpha = 0.05$"* — which describes neither what was computed (post-hoc power at observed d) nor what it means. Observed power is a monotone function of the p-value and adds no information; reporting it alongside p = 0.0000 is tautological. **Remove the column.**

### 4.4 HIGH — CIs are computed, promised, and then not shown

- Promised at MAIN:227 for ECFP4-vs-hybrid and quantum-vs-RBF: **neither delivered.**
- Computed for the 7 classical comparisons (`p3_effect_sizes.csv` cols `CI_95_lower/upper`, e.g. AP [0.006, 0.009]) but **stripped from the rendered LaTeX table**. These are the CIs the paper should be leading with instead of *d*.
- `p3_tda_promiscuity.csv` has `ci95_lo`/`ci95_hi` columns that are **entirely empty** — the bootstrap at `p3_physical_validation.py:652–659` is wrapped in a bare `except Exception: lo, hi = np.nan, np.nan`, and it evidently fired for all 78 features. Yet the figure title generated at `p3_physical_validation.py:687` and reproduced in SM Fig. S (SM:580) states *"error bars = 95% bootstrap CI"*. **A published figure asserts CI error bars that are NaN in the deposited data.** CRITICAL for the deposit's integrity.
- No CI anywhere on: hybrid ablation deltas, TNE/ECFP4 R², GA discriminator AUCs, silhouette scores, ChEMBL enrichments, ρ = 0.71 / ρ = 0.718.

### 4.5 MEDIUM — the SOTA table's *d* uses a hand-set pooled SD

SM:517: *"Cohen's $d$ is computed approximately as $(\text{AUC}_{\text{strategy}} - \text{AUC}_{\text{ECFP4}}) / \sigma_{\text{pooled}}$ with $\sigma_{\text{pooled}} = 0.006$ (RF) and $0.012$ (SVM), approximately estimated from fold-level standard deviations across all strategies."* A single constant denominator shared across all rows makes *d* a linear rescaling of Δ AUC — it carries no information beyond Δ AUC while wearing the authority of an effect size. Additionally the baseline is the **superseded** ECFP4 = 0.868, so every *d* in that table refers to a benchmark the paper elsewhere disowns.

---

## §5. Confounding and covariate-set fidelity

### 5.1 CRITICAL — the text describes a covariate set the deposit does not contain

**Claim** (five occurrences): MAIN:100 (Abstract, as "$p > 0.7$"), MAIN:361, MAIN:368 (Fig. 3 caption), MAIN:376, SM:104, SM:639 — *"controlling for molecular weight alone collapses the correlation to $\rho_{\text{partial}} \approx 0$ ($p = \num{0.85}$)"*.

**Deposit** (`results/p3_h1_rrs_partial_corr.txt`, `.csv`): one model only, stated in its own header — *"controlling for MW, n_rings, Fsp3, H0_count"* — giving H₁_count ρ_partial = −0.0388, p = 0.7447.

**Code** (`scripts/p3_h1_rrs_partial_corr.py:89`): `confounders = ["MW", "n_rings", "Fsp3", "H0_count"]`, hard-coded, no CLI override, no loop over covariate subsets, no second output.

**There is no MW-only model in the repository, and the value p = 0.85 appears nowhere in `results/`.** Either an undeposited analysis is being cited, or p = 0.85 is a misremembering of the 4-covariate p = 0.7447 that then acquired a spurious "alone". Two of the five occurrences hedge to "$p > 0.7$" (MAIN:100, MAIN:368, SM:104) — consistent with 0.7447 — while three assert "$p = 0.85$" (MAIN:361, MAIN:376, SM:639). **The paper reports two different p-values for the same claimed analysis.**

This matters beyond bookkeeping: "MW alone kills it" is a *stronger and more damning* confound statement than "the full size panel kills it", and it is the version placed in the Abstract. It must be either run and deposited or deleted.

### 5.2 CRITICAL — the confound control applied to H₁–RRS is not applied to the promiscuity analysis

The authors demonstrate they know how to do this: T9 is a clean, correctly-reported partial correlation. The identical confound is then ignored where it is most damaging (§6.1).

### 5.3 HIGH — the H₁–RRS cohort has no Class D compounds, but the figures are built around Class A vs Class D

`results/p3_h1_rrs_correlation_final.txt`: *"Class A: 46 / Class B: 31 / Class C: 0 / Class D: 0"* for the n = 77 analysis cohort.

Yet MAIN:368 and SM:104 caption the figure as *"H$_1$ persistence distributions for Class~A (resistance-resilient, blue) versus Class~D (resistance-vulnerable, red) compounds, with Class~B (green) and Class~C (orange) shown for context"* — that is the **pilot n = 14**, in which (by the captions' own admission) *"the Class~D subset contains only one compound"*.

SM:639 then draws inference from it: *"Class~A compounds in the pilot cohort also exhibited higher H$_1$ topological features than Class~D across all four metrics (count, total persistence, mean lifetime; max lifetime marginal)"*. **A four-metric group comparison against a single observation, described as concordant evidence.** With n = 1 in one arm no test is possible and "across all four metrics" has ~1/16 probability under pure noise for a random single compound. The caveat sentence that follows does not neutralise the preceding claim. The word "marginal" applied to the fourth metric implies a p-value that cannot exist.

### 5.4 MEDIUM — the size confound is asymmetrically disclosed

MAIN:376 (Limitations) correctly states H₁ count *"should be interpreted as a proxy for molecular size"*. MAIN:372 then says *"H$_1$ count could therefore serve as a computationally inexpensive, size-mediated surrogate for prioritising resistance-resilient candidates"* — but if H₁ count is a size proxy and the partial correlation is null, then **molecular weight itself is the cheaper surrogate**, and the topological framing adds nothing. The paper never states this obvious corollary, which would cost it contribution (iii) (MAIN:380).

---

## §6. Causal / mechanistic language on correlations

### 6.1 CRITICAL — a steric-clash mechanism asserted from ρ = −0.25 on an unadjusted size proxy

**MAIN:325** (verbatim): *"This provides a clear topological mechanism: lower topological complexity in ring structures (H$_1$) and structural components (H$_0$) endows candidate molecules with optimal conformational adaptability across multiple malaria targets, reducing steric clash penalties."*

**SM:575** (verbatim): *"indicating that molecules with lower topological complexity in their ring systems and structural components are conformationally flexible enough to engage multiple targets --- a topological signature of polypharmacology."*

Four independent problems:

1. **The effect size does not support the story.** ρ = −0.248 → ρ² = 6.1 % of rank variance for the strongest feature; H₁ entropy gives 3.6 %. "A clear topological mechanism" and "endows" are causal verbs on a 6 % rank-variance association.
2. **H₀ count *is* molecular size.** SM:192 gives mean H₀ count = 38.04, SD 7.35, range 11–69; MAIN:186 gives mean 39 atoms/molecule. In a Vietoris–Rips filtration on the atom point cloud, the H₀ generator count at birth is the atom count. So the top result reads: *smaller molecules bind more targets at ΔG ≤ −7 kcal/mol*. Docking scores are well known to be size-correlated, and the direction here (smaller → more promiscuous) is the classic ligand-efficiency artefact of a fixed ΔG threshold. It is not a topological finding.
3. **No adjustment, despite the authors having the tool.** The exact partial-correlation machinery used at T9 (MW, n_rings, Fsp3, H₀ count) is never applied here. Had it been, H₀ count would be a *covariate*, not a predictor.
4. **The dependent variable in the text does not match the deposit.** MAIN:325 states *"(label: $\geq 2$ targets at $\Delta G \leq -\SI{7.0}{\kcalmol}$)"* — a binary at 12.0 % prevalence. But `p3_physical_validation.py:645` correlates each feature against `n_bound = bound.sum(axis=1)`, a **0–3 count**, not the binary. SM:575 says "the number of targets bound" in prose and then re-states the binary label in the same sentence. The reported analysis is against a different variable than the one the manuscript names.

Additionally, the underlying label is itself a computational proxy (QuickVina ΔG on 3 targets), so the chain is: docking score → thresholded count → rank correlation with an atom-count proxy → "steric clash penalties". Each link is defensible; the concatenation asserted as mechanism is not.

### 6.2 HIGH — mechanistic reading of the discriminator collapse

MAIN:311 / MAIN:345 / SM:608: *"the quantum kernel operates on an 8-dimensional UMAP-reduced space that discards the atomic-level resolution needed to detect near-identical matches---the reduced space confounds proximity information rather than enhancing it"* and MAIN:376 *"represents an inherent resolution bottleneck of the UMAP dimensionality reduction"*.

This causal attribution (UMAP is the bottleneck) is never tested. The obvious control — run the same density discriminator on an 8-dimensional **classical** UMAP embedding, or on the raw 6-D features — is not performed. Without it, the QK arm's near-random AUC is equally consistent with the IQPEmbedding kernel, the density statistic (mean rather than max similarity, unlike the Tanimoto arm which uses **maximum** similarity — SM:606), or the reduction. **The two arms use different aggregation functions (max vs mean), which alone could produce the entire gap.** That confound is not mentioned.

### 6.3 MEDIUM — scaffold-paradox mechanism rests on an unreported test

MAIN:286: *"variations captured quantitatively by the substantial divergence in H$_0$ persistent homology between the seed and expanded sets … which manifests mathematically as the preservation of the H$_1$ topology distributions. Consequently, topological data analysis establishes that the computational expansion protocol achieves peripheral functional distinction without destroying the core target-recognition topologies."*

"Establishes" is doing heavy work. The only statistical support offered is the Wilcoxon test named in the Fig. 1 caption (MAIN:291) whose value is never reported (T15), and no distributional summary of seed vs expanded H₀/H₁ appears in main or SM. **A contribution claim (N6, MAIN:123) with zero reported inferential support.**

### 6.4 MEDIUM — "principal positive contributor" from an untested ablation

MAIN:217, 251, 255, 315, 345, 353, 380 and SM:599 repeatedly designate QKS "the principal positive contributor (ablation Δ = −0.040)". Ablation deltas are point estimates with no CI (T36–T38). Δ(−QKS) = −0.040 vs Δ(−TFP) = −0.014 — per-fold data in `results/p3_ablation.csv` would let these be compared properly and would likely support the ordering, but as presented it is a ranking of three unreplicated numbers. Also unaddressed: Δ(−TNE) = **+0.011** means the hybrid is beaten by a two-component variant, so "TFP+TNE+QK" is not the best model the authors fit and the headline AUC 0.888 is not their best hybrid (0.899 is).

---

## §7. Class imbalance and label provenance

### 7.1 HIGH — accuracy and F1 for the weak descriptors are at the trivial-classifier baseline

Canonical panel prevalence: 74.2 % active (MAIN:137; SM:681 gives 14 721/5 115). The always-predict-active classifier therefore achieves **accuracy 0.742** and **F1 0.852**.

From MAIN Table 1 (MAIN:268) and `p3_hybrid_summary.txt`:

| Method | Accuracy | vs 0.742 | F1 | vs 0.852 |
|---|---|---|---|---|
| TNE (d = 8) | 0.756 | **+0.014** | 0.857 | **+0.005** |
| QKS | 0.819 | +0.077 | 0.886 | +0.034 |
| TFP | 0.838 | +0.096 | 0.897 | +0.045 |

**TNE's accuracy and F1 are essentially indistinguishable from predicting "active" for every molecule.** The manuscript reports them in a table alongside ECFP4's 0.896/0.931 with no baseline row and no comment; MAIN:251 says TNE "captures meaningful but lower signal". Its AUC (0.722) does carry signal; its accuracy and F1 do not, and printing them without the majority-class reference invites over-reading. **Add a majority-class baseline row to Table 1 and to SM Table S (per-fold).**

### 7.2 HIGH — inconsistent imbalance handling between benchmarks that are compared to each other

- **Canonical benchmark** (`scripts/p3_hybrid_benchmark.py:365, 1033, 1175`): `RandomForestClassifier(n_estimators=RF_TREES, n_jobs=-1, random_state=42)` — **no `class_weight`**. Likewise `SVC(kernel="rbf", probability=True, C=1.0)` — no `class_weight`.
- **SOTA benchmark** (SM:494, SM:517): *"All evaluations use 5-fold stratified cross-validation with class-weighted classifiers"* / *"All classifiers used \texttt{class\_weight=balanced}"*.
- **Polypharmacology benchmark** (`p3_physical_validation.py:337 comment`): *"the SVM already uses class_weight='balanced'"*.

SM:520 and SM:498 nonetheless compare SOTA-table AUCs directly to the canonical ECFP4 baseline (via Cohen's *d*, T58–T67). **Class-weighted and unweighted models are compared as if interchangeable.** The caption's caveat covers the ECFP4 *value* being superseded but not the weighting difference.

### 7.3 HIGH — at least three distinct label sets are in circulation and the main text describes only one

MAIN:137 states a single provenance: *"Binary activity labels were obtained from Ersilia model eos80ch … using the model's standard classification threshold of \num{0.5}"*, with panel split 74.2 %/25.8 %.

Deposited reality:

| Label set | Split | Used by | Disclosed? |
|---|---|---|---|
| Canonical eos80ch, n = 19 836 | 14 721/5 115 = 74.2 %/25.8 % | classical + hybrid benchmarks | ✅ MAIN:137 |
| `results/p3_labels_production.csv`, n = 19 849 | **15 063/4 786 = 75.9 %/24.1 %** | SOTA benchmark, TopologyNet analog (`p3_sota_benchmark_full_summary.txt`: *"Labels: 15063 active, 4786 inactive"*) | ⚠️ only in SM:517 fine print, described as *"preliminary MPO-derived labels"* — a **different labelling method**, not a different threshold |
| QKS n = 5000 subsample | 3 750/1 250 = 75.0 %/25.0 % (SM:681) | kernel benchmark | ✅ SM:681 |
| Phase-2 n = 5000 subsample | 3 732/1 268 = 74.6 %/25.4 % (SM:320) | hyperparameter selection | ✅ SM:320 |
| GA discriminator seed pool | 105 active/95 inactive, *"balanced by eos80ch activity score"* (SM:606) | discriminator | ✅ |

Two issues: (a) the main text's single-provenance statement is incomplete — an "MPO-derived" label set is materially different from an eos80ch-threshold label set, and the entire SM §SOTA and §TopologyNet sections run on it; (b) SM Table S-sota's Cohen's *d* column compares MPO-labelled TDA strategies against an eos80ch-labelled ECFP4 baseline. **Cross-label-set effect sizes are not interpretable.**

### 7.4 MEDIUM — n = 19 849 vs n = 19 836 used interchangeably for the same benchmark

SM:681 defines the large kernel benchmark as *"the full canonical panel of \num{19836} molecules (\num{14721} active, \num{5115} inactive)"*, but the table (SM:698), its caption, the file names (`p3_qks_benchmark_n19849.csv`), and every main-text citation (MAIN:100, 127, 279, 301, 353, 388) label it **n = 19 849**. Table 1's QKS footnote (MAIN:279) says *"the standalone 6-qubit kernel benchmark at $n = \num{19849}$"*. A reader cannot tell which panel the p = 0.060 refers to. Low inferential impact, high referee irritation.

### 7.5 MEDIUM — the QKS row in Table 1 is not commensurable with the rest of the table

MAIN Table 1 (MAIN:255) is captioned *"canonical panel \num{19836} molecules, 5-fold stratified cross-validation, **Random Forest**"* and carries a "ΔAUC vs. ECFP4" column. The QKS row (MAIN:269, Δ = −0.125) comes from an **SVM with a precomputed kernel at n = 19 849** (MAIN:279 footnote). A Δ column implies a paired comparison; none was performed for that row, and the classifier differs. Same issue, smaller, for the Hybrid row's provenance ("canonical full-library rerun").

### 7.6 LOW — no external / scaffold-split validation

All 5-fold CV is random stratified (`StratifiedKFold(shuffle=True, random_state=42)`). For a library generated by STONED-SELFIES expansion from 396+454 seeds — i.e. containing large families of near-duplicates — random splits place analogues of the same seed in train and test. Every AUC in the paper, including ECFP4 = 0.948, is therefore an optimistic within-analogue-family estimate. The paper's own scaffold-paradox result (69.3 % scaffold recovery, MAIN:286) is direct evidence that this is happening. A scaffold-split (Bemis–Murcko) replicate is the standard control and is absent. Note the companion P5 study reportedly does run scaffold splits, making the omission here conspicuous.

---

## §8. Additional inferential findings

| Sev | Finding | Evidence |
|---|---|---|
| HIGH | **MAIN:219 ends mid-sentence.** *"Hyperparameter optimisation followed a two-phase protocol. In Phase~1 ($n = \num{200}$), a grid search evaluated \num{60} combinations"* — then §2.7 begins. The Methods description of the 50-way model selection that fixes every quantum result is truncated; the reader is sent to SM:300 without being told. | MAIN:219–221 |
| HIGH | **Selection at n = 200 is reported at n = 5000 without a selection-effect caveat.** SM:302 quotes the winner's n = 200 AUC (0.853 ± 0.049); SM:308 quotes 0.8283 ± 0.0371 at n = 5000 for the same config. The drop is consistent with selection optimism at n = 200 over ~50 configurations, but is presented as a neutral "re-benchmark". Only the top-3 were carried forward (SM:320), so no unbiased estimate of the selection penalty exists. | SM:300–320 |
| HIGH | **Silhouette threshold met to the third decimal and called "substantially exceeding".** MAIN:223 pre-sets *"A TNE Silhouette $>$ \num{0.35} was set as the target"*; SM:249 reports **0.350**; MAIN:303 reports it as *"substantially exceeding the VAE latent space (0.229)"*. The target is not strictly met (0.350 is not > 0.35), and no dispersion is given for any of the three descriptors. Silhouette also depends on dimensionality (192 vs 64 vs 2048 D) — a known bias favouring lower-dimensional embeddings that is never mentioned. | MAIN:223, 303; SM:241–254 |
| MEDIUM | **"∞" enrichment reported with an evaluative verdict.** SM:420: PfATP4 enrichment "$\infty$", verdict "EXCELLENT", footnote *"0/87 inactives recovered"*. No CI, no exact test. A one-sided Clopper–Pearson bound on 0/87 is trivially computable and would give a finite, defensible enrichment floor. | SM:411–426 |
| MEDIUM | **Calibration claimed on a near-random model.** SM:361: *"The model is well-calibrated (ECE $< \num{0.05}$)"* for a classifier whose bootstrap MC AUC is **0.5443** (SM:354). At AUC ≈ 0.54 on a 74/26 panel, predicting the base rate for everything yields near-perfect ECE; the calibration statement is vacuous without a baseline-ECE comparison. Also note this section evaluates TFP+TNE on **100 test molecules**, while the same descriptors reach AUC 0.876/0.722 on the full panel — the discrepancy (0.544 vs ≥ 0.722) is never explained. | SM:344–362; `results/p3_mc_uncertainty_summary.txt` |
| MEDIUM | **Conformal "coverage 95.0 % = target 95.0 %" reported as validation.** Marginal coverage at the nominal level is guaranteed by construction for split conformal; it is not evidence the method works. The informative quantity — mean set size 1.820 out of a maximum 2.0, i.e. 82 % of predictions are "both classes" — *is* reported (SM:357) but framed as a caveat rather than as the headline. | SM:346–362 |
| MEDIUM | **Two promised comparative analyses are never reported.** MAIN:231: *"TFP features were compared with ChemGraphX topological descriptors … by computing Spearman correlations between corresponding entropy-based measures across the \num{65856}-molecule library. Fingerprint diversity was assessed using the Universal Molecular Fingerprint Highlighter (UMFH) framework…"* — `grep -rli "chemgraphx\|umfh" results/ scripts/` returns **nothing**, and no result appears in main or SM. A Methods subsection describing analyses that produced no results. | MAIN:229–231 |
| LOW | **p = 0.0 printed as a p-value** in `p3_tne_regression.csv` (6 rows) and `p3_tartarus_summary.txt`. Underflow; should be "< 10⁻³⁰⁰" or reported as ρ with CI. | `results/p3_physical_validation/p3_tne_regression.csv` |
| LOW | **Deposited vs quoted R² mismatch.** ECFP4 PfDHFR R² = 0.4508 (`p3_tne_regression.csv`) vs 0.4606 (`p3_tartarus_summary.txt`) vs 0.461 quoted (MAIN:321, SM:571). PfATP4 0.5701 vs 0.578 quoted; PfCRT 0.5154 vs 0.517 quoted. Two deposits disagree and the manuscript follows the older one. Flagged here only because the "TNE outperforms ECFP4" inference (Δ = +0.012 or +0.022) is sensitive to which is canonical. | MAIN:321; SM:571 |
| LOW | **`H1_max_pers` sign flip between analyses.** ρ = +0.067 vs RRS (`p3_h1_rrs_correlation_final.txt`) but ρ = −0.002 vs promiscuity and ρ_partial = +0.188 after adjustment — the only predictor whose partial exceeds its total. Not discussed; worth a sentence given the size-mediation narrative. | `p3_h1_rrs_partial_corr.csv` |

---

## §9. Actionable recommendations (DONE-CRITERION 4)

Each item names the specific statistic to add and the file that already holds the inputs.

**R1 — Replace the quantum-vs-RBF null with a TOST equivalence test, and retitle §5.5.** *(addresses N2, N4, N5, N6, N9)*
Run two one-sided *t*-tests on the 5 paired fold differences in `results/p3_qks_benchmark_n19849.csv` and `..._n5000.csv` with an a-priori equivalence margin — Δ AUC = ±0.01 is defensible (it is ~1.5 fold SDs and below the smallest classical gap in Table 1). Report `Δ AUC [90 % CI]` per sample size alongside the TOST p. With Δ = −0.0062 and fold-difference SD ≈ 0.005 at n = 19 849 the TOST will almost certainly **fail** at δ = 0.01, which is the honest result: *the study cannot establish equivalence either*. Then retitle §5.5 to *"Kernel comparison: no detectable quantum advantage; equivalence not established"* and add a `Δ AUC [95 % CI]` column to SM Table S-qkernel (SM:696), replacing the "n.s." annotation. Same treatment for the polypharmacology claim at SM:573 — with 3 folds, state explicitly that no equivalence margin is estimable.

**R2 — Run and deposit the MW-only partial correlation, or delete every "p = 0.85".** *(addresses N13, §5.1)*
Add a `--confounders` argument to `scripts/p3_h1_rrs_partial_corr.py` (the covariate list at line 89 is the only change needed) and emit a nested table: unadjusted → +MW → +MW,n_rings → +MW,n_rings,Fsp3 → +all four, with ρ_partial, p, and 95 % bootstrap CI at each step. Re-deposit `results/p3_h1_rrs_partial_corr.{txt,csv}`. Until that file exists, MAIN:100, MAIN:361, MAIN:368, MAIN:376, SM:104 and SM:639 must quote only the deposited 4-covariate result (ρ_partial = −0.039, p = 0.745).

**R3 — Replace Cohen's *d* with Δ AUC + bootstrap CI in SM §8, and add the correction table.** *(addresses §4.2, §4.3, §4.4, §3)*
`scripts/p3_effect_sizes.py` already computes `CI_95_lower/CI_95_upper` (lines 119–128) and already writes them to `p3_effect_sizes.csv`. Change the LaTeX writer to emit columns `Δ AUC | 95 % CI | p (raw) | p (Holm–Bonferroni, k = K)` and drop the `Cohen's d`, `Effect`, and `Power` columns entirely. Set K from an explicit family declaration listed in the SM (see R5). Use **Holm–Bonferroni**, not Bonferroni: with 204 tests, Holm preserves power on the strong effects while still killing p = 0.0057.

**R4 — Apply the §T9 partial-correlation machinery to the promiscuity analysis, and fix its dependent variable.** *(addresses §6.1)*
In `analysis_tda_promiscuity` (`p3_physical_validation.py:623`): (a) correlate against the variable the manuscript names — either switch to the binary `y_all` (≥ 2 targets) or change MAIN:325/SM:575 to say "number of targets bound (0–3)"; (b) add a partial-Spearman column controlling for MW and heavy-atom count, reusing `partial_pearson` from `p3_h1_rrs_partial_corr.py:28`; (c) drop H₀ count from the predictor list or relabel it "atom count (H₀ generators)" so readers can see what it is; (d) fix the bare `except Exception` at line 657 so the bootstrap CI actually populates `ci95_lo/ci95_hi` — the figure caption currently promises error bars the deposit does not contain; (e) add a Benjamini–Hochberg `q` column across all 78 features and report how many survive. Then rewrite MAIN:325 from *"This provides a clear topological mechanism … endows … reducing steric clash penalties"* to a size-adjusted statement of the residual association, or delete the mechanistic sentence.

**R5 — Add an SM section "Multiple comparisons: declared test family".** *(addresses §3)*
A single table listing every test block (the 17 rows of §3.2), its k, and the correction applied to it, with the running total. State plainly that the H₁–RRS association (p = 0.0057) does not survive correction over the 11-feature screen it came from, and downgrade "nominally significant" to "not significant after correction for the 11 topological features screened" in MAIN:100, 361, 368, 376, 380 and SM:104, 639.

**R6 — Report the Wilcoxon test that Figure 1 promises, or remove the promise.** *(addresses T15, §6.3)*
MAIN:291 announces a Wilcoxon *p*-value for seed vs expanded H₀/H₁ persistence; no value and no output file exist. Deposit a `results/p3_scaffold_paradox.csv` with n_seed, n_expanded, median H₀ and H₁ persistence per group, Wilcoxon rank-sum *W*, *p*, and a Cliff's δ effect size, and quote *W*, *p*, and δ in the caption. Without it, contribution N6 (MAIN:123) has no inferential support.

**R7 — Add a majority-class baseline row to Table 1 and per-fold Table S.** *(addresses §7.1)*
Insert `Always-active (majority class) | AUC 0.500 | Acc 0.742 | F1 0.852` as the first row of MAIN Table 1 (MAIN:261). This single row makes TNE's 0.756/0.857 self-evidently uninformative on accuracy/F1 and prevents a referee from concluding the authors did not notice.

**R8 — Test the hybrid ablation.** *(addresses T36–T38, §6.4)*
`results/p3_ablation.csv` holds all 5 folds for each of the three leave-one-out variants and `p3_hybrid_benchmark.csv` holds the full hybrid. Report each Δ with a paired bootstrap 95 % CI over folds and a Holm-corrected p across the 3 comparisons. Then state explicitly that Hybrid−TNE (0.899) outperforms the full hybrid (0.888) and either adopt TFP+QK as the reported hybrid or justify keeping TNE.

**R9 — Add a scaffold-split (Bemis–Murcko) replicate of the canonical benchmark.** *(addresses §7.6)*
`StratifiedKFold` at `p3_hybrid_benchmark.py:374` → `GroupKFold` on Bemis–Murcko scaffold. Report both random-split and scaffold-split AUCs side by side in Table 1. On a STONED-expanded library with 69.3 % scaffold recovery this is the single most consequential missing control, and the resulting drop is itself a publishable observation.

**R10 — Fix the anti-calibration reading.** *(addresses N12)*
SM:361 should read that the uncertainty–error Spearman is **significant and negative** (ρ = −0.286, p = 0.004, n = 100), i.e. the MC uncertainty is *inversely* related to error, and either investigate or state that the uncertainty estimate should not be used for triage. Add a bootstrap CI on ρ. Remove the "well-calibrated" claim or benchmark ECE against a base-rate-predicting reference.

---

## §10. Verdict

The paper's core empirical conclusion — *classical ECFP4 outperforms all quantum-inspired descriptors, and the simulated quantum kernel confers no detectable advantage over a properly tuned RBF* — is very likely correct and is argued with commendable candour about failed hypotheses. That conclusion survives every criticism above, because it rests on Δ AUC gaps (0.060–0.226) that dwarf any plausible correction to the inference machinery.

What does **not** survive as stated: (i) the H₁–RRS "nominally significant" association, which fails correction over its own 11-feature screen; (ii) the MW-only confound analysis, which does not exist; (iii) the topological mechanism for polypharmacology, which is an unadjusted molecular-size correlation with an empty CI column and a mis-stated dependent variable; (iv) any statement of parity or equivalence between the quantum and RBF kernels, none of which is supported by a TOST or a CI; (v) the scaffold-paradox resolution, whose only announced test is never reported. The reported effect sizes are on an uninterpretable scale, the promised confidence intervals are absent, and the declared multiplicity correction covers 7 of ≥ 204 tests.

**Recommendation: major revision.** None of R1–R10 requires new computation beyond what is already deposited, except R6 and R9.

---

### Done-criteria

1. **Complete enumerated list of every hypothesis test in main + SM, each with stated p, df, and validity verdict** — §1, tables 1A (T1–T15, main), 1B (T16–T35, SM), 1C (T36–T68, comparisons asserted without a test), 1D (deposited-but-unreported screens). 68 numbered entries covering ≥ 204 distinct tests, each with location, statistic, p, df/n, and a ✅/⚠️/❌ verdict.
2. **Explicit count of total test family vs correction applied** — §3.2 table: **≥ 204 distinct hypothesis tests; correction applied to 7 (3.4 %)**; plus 50 uncorrected model-selection comparisons. §3.3 gives the two conclusions that change (T6 and T25 fail correction).
3. **Every non-significant-result sentence quoted verbatim with an over-read verdict** — §2, N1–N14: 3 correct, 7 over-read into equivalence/parity/comparability, 2 mislabelled, 1 stated-but-not-honoured. TOST/CI requirements named per instance and consolidated in R1.
4. **At least one concretely actionable recommendation** — §9, R1–R10, each naming the specific statistic (TOST at δ = 0.01; Holm–Bonferroni over a declared family; partial Spearman on MW + heavy-atom count; Benjamini–Hochberg q over 78 features; Cliff's δ + Wilcoxon W for the scaffold paradox; paired bootstrap CI on ablation deltas; majority-class baseline row; GroupKFold on Bemis–Murcko scaffolds) and the file/line that already holds the inputs.
