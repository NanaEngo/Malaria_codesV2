# Scientific-Critical-Thinking Review — V4 Corrected Grid

**Reviewer lens:** falsifiability, causal vs. correlational language, statistical rigor, overclaiming.
**Files reviewed:** `Antimalarial_Candidates_African_NP_V2607.tex` (main), `Antimalarial_Candidates_African_NP_V2607_SM.tex` (SM).
**Data backbone cross-check:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (parent folder, authoritative).
**Date:** 2026-07-26.
**Scope note:** Items the user marked ALREADY FIXED on 2026-07-26 are NOT re-flagged here: S24 (76 sound), C3 SI_pred-heuristic labeling *at main l.210 and SM Table S-selectivity l.236*, C5 ("validated discovery" in Conclusion), DOCK-1 (71/1936 NaN disclosure at SM l.178), anti-AI, C6 (MCMC surrogate weakness + nearest-neighbour decoding disclosed), F3 (PfCRT-domination/DiffDock-compensation paragraph, present at main l.311), AI-use. This review targets *residual* and *new* scientific-rigor issues not covered by that list.

---

## CRITICAL

### CRIT-1 — Headline "consensus-score ROC-AUC 0.924–1.000" is tautological for 3 of 4 targets (circular label assignment); the only prospective benchmark is near-random (0.450)
**Where:** Abstract main l.72 ("maintaining discriminatory power … ROC-AUC 0.924–1.000"); Methods main l.126, l.216; Table 1 main l.228–231; SM l.1275, l.1336, l.1346–1348.
**Falsifiability / statistical validity:** For PfATP4, PfClpP, and PfCRT the "actives"/"decoys" labels are *assigned by the consensus score being evaluated*: SM l.1336 states verbatim "Actives: top 25% by consensus score. Decoys: bottom 25% by consensus score"; SM l.1346 concedes the AUC=1.000 values come from "score-based classification, demonstrating that consensus scoring effectively distinguishes high-scoring from low-scoring MMV compounds." Ranking compounds by a score and then asking whether that score separates the top from the bottom of its own ranking is circular — AUC→1.0 (or 0.971 for PfCRT, whose 359/40 split is the HIGH-tier vs rest, also score-derived) is true *by construction*, not evidence of discriminative power. The MMV Malaria Box contains only confirmed actives (IC₅₀<10 µM), so there is no experimental inactive set inside it; any "decoy" set is necessarily score-derived (or borrowed from DEKOIS, which is done for PfDHFR only). The sole genuinely prospective, property-matched-decoy benchmark — DEKOIS PfDHFR, Vina-only — gives ROC-AUC 0.450 (95% CI 0.367–0.531), i.e. near-random. The deposited data therefore **cannot falsify the "0.924–1.000 discriminatory power" claim** for 3/4 targets, because the labels are a deterministic function of the score. The audit matrix verified the *numbers* trace to CSVs (sound) but did not assess this methodological circularity.
**Suggested fix:** (a) Disclose explicitly in Table 1 caption and Methods that PfATP4/PfClpP (1.000) and PfCRT (0.971) use score-based labels and are **internal-consistency checks, not external discrimination**; (b) reframe the abstract/headline from "maintaining discriminatory power" to "retrodiction on a positive-control set, with the only prospective benchmark (DEKOIS) at near-random 0.450"; (c) lead the validation narrative with DEKOIS 0.450 as the actual prospective result and present the MMV values as retrodictive consistency only; (d) stop comparing the score-based AUCs to literature single-method benchmarks (see HIGH-3).

### CRIT-2 — MCMC "+0.0246" headline is internally inconsistent and inflates the true mean-chain gain ~2.8×; no uncertainty quantification against a weak surrogate
**Where:** main l.121 ("mean chain MPO improvement of +0.0246 (library mean 0.742 → chain mean 0.751)"); Conclusion main l.317 ("measurable MPO improvement (+0.0246)"); BMAD §1.8b.
**Statistical rigor:** The parenthetical itself contradicts the headline: 0.751 − 0.742 = **+0.009**, not +0.0246. Cross-check against BMAD §1.8b (Mean MPO chains = 0.7507, Library mean = 0.7420, Best chain final = 0.767, Top candidate = 0.8007): mean-chain − library = **+0.0087**; best-chain − library = **+0.025** ≈ +0.0246. The reported +0.0246 is therefore the **best-chain** gain presented as the **mean-chain** improvement — a ~2.83× inflation (verified arithmetically). On top of the mislabel, the surrogate has validation R² = 0.377 (62% of variance unexplained), decoding is nearest-neighbour lookup (disclosed, C6), and there is **no bootstrap CI, no per-chain variance, and no comparison of +0.009 to the surrogate's prediction uncertainty**. A +0.009 shift on a 0.377-R² surrogate is plausibly within surrogate noise, so "confirms that VAE latent space is not flat w.r.t. the MPO objective" (l.121) is not robustly supported.
**Suggested fix:** Report mean-chain **+0.009** and best-chain **+0.025** separately, each with a bootstrap CI over the 4 chains; state that with R²=0.377 the mean-chain gain is within surrogate prediction uncertainty; soften "confirms … not flat" to "is consistent with, but does not by itself establish, non-flatness given surrogate uncertainty." Correct the parenthetical so the stated means equal the stated improvement.

---

## HIGH

### HIGH-1 — SI_pred heuristic caveat (C3 fix) is contradicted at main l.260, where SI_pred is presented as the experimental SI definition
**Where:** main l.260 ("a predicted selectivity index > 10 (defined as IC₅₀,HepG2 / IC₅₀,Pf3D7)"); cf. correct caveat at main l.210 and SM l.236.
**Causal/validity:** The C3 fix correctly labels SI_pred = score_eos7kpb/(1−DILI) an "unvalidated prioritization heuristic" at l.210 and in the SM table. But l.260 re-introduces the problem by *defining* the quantity as "IC₅₀,HepG2 / IC₅₀,Pf3D7" — the **experimental** selectivity-index definition, which is not what SI_pred computes (an activity probability divided by (1 − a hepatotoxicity probability) is not a potency ratio). A reader at l.260 reasonably concludes 810 compounds have measured HepG2/Pf selectivity ratios > 10. The construct validity is itself weak: an Ersilia activity probability ÷ (1 − DILI probability) has no demonstrated correlation to an experimental SI, and the DILI denominator creates a singularity (max 106,773.8, disclosed).
**Suggested fix:** At l.260 replace "defined as IC₅₀,HepG2 / IC₅₀,Pf3D7" with the actual formula and the same heuristic caveat used at l.210 ("an unvalidated ranking proxy; not an experimental potency ratio; supports ranking only"); strike any implication of a measured selectivity ratio. State once in Methods that SI_pred has no demonstrated correlation to experimental SI.

### HIGH-2 — "Mathematically prove" the VAE accesses unreachable scaffolds via STONED-SELFIES
**Where:** main l.91 ("STONED-SELFIES structural mutation analysis was employed to mathematically prove that our generative model accesses new scaffolds fundamentally unreachable by simple local search").
**Overclaiming / falsifiability:** STONED-SELFIES is an empirical stochastic sampling method; the 97.9% unreachable figure (mean max Tanimoto 0.238) is **empirical evidence**, not a mathematical proof. "Prove" / "fundamentally unreachable" overstates what a finite mutation sample can establish and is not falsifiable as stated (no theorem is given).
**Suggested fix:** Replace "mathematically prove" with "empirically demonstrate"; replace "fundamentally unreachable" with "outside the reach of this local-perturbation sample."

### HIGH-3 — Efficiency section misattributes the consensus (Vina+DiffDock ML) ROC gain to the centroid-sampling method, and compares against single-method benchmarks their own single-method result fails
**Where:** main l.265 and l.281 ("This efficiency gain was achieved while maintaining the consensus-score ROC-AUC 0.924–1.000 … exceeding typical single-method virtual screening benchmarks (ROC-AUC 0.7–0.8)").
**Causal misattribution / overclaiming:** Two problems. (i) The 0.924–1.000 is the *consensus* (Vina + DiffDock ML rescoring) figure, not a property of centroid-based sampling; the centroid method's standalone discriminative ability is untested (exhaustive ROC is "Unknown" per SM l.1072–1075). Attribution of the ROC to the efficiency innovation conflates two distinct components. (ii) The comparison to "typical single-method VS benchmarks 0.7–0.8" is apples-to-oranges: their own single-method prospective result (DEKOIS Vina-only) is **0.450 — below** that 0.7–0.8 range. Claiming to "exceed typical single-method benchmarks" while the single-method arm is 0.450 (and 3/4 of the consensus values are tautological, CRIT-1) is misleading.
**Suggested fix:** Separate the two claims: centroid sampling reduces *runs* by 99.3% (defensible, arithmetic sound); the enrichment gain comes from adding DiffDock ML rescoring, not from centroid sampling. Delete "exceeding typical single-method virtual screening benchmarks (0.7–0.8)" or restate as "the consensus protocol's retrodictive AUC on the MMV positive control exceeds the 0.7–0.8 typical of single-method retrospective benchmarks, whereas the prospective single-method DEKOIS result (0.450) does not."

### HIGH-4 — VAE / clustering validation metrics are "N/A" for the *selected* 64D KMeans configuration, yet the text calls it "optimal/superior/best balance"
**Where:** main l.117 ("based on superior cluster separation in this benchmarking"), l.161, l.166 ("best balance of granularity and cohesion"); SM Table (vae_comparison) l.853–876 (Validation/Reconstruction/KL/Silhouette/CH/DB all "N/A"); SM Table (clustering_comparison) l.941 (the selected 64D KMeans row: Sil/CH/DB = "N/A", Quality "Acceptable*").
**Falsifiability / reproducibility:** The entire 484-centroid pipeline rests on the 64D KMeans clustering, but the displayed metrics for the *chosen* configuration are all N/A, so a reviewer cannot evaluate whether the latent space / clustering is any good. "Superior/best" is unsupported by the displayed data (the only populated KMeans row is 32D, Sil=0.182 = "Poor"). This is a known gap (audit matrix E, S23-1: "gutted … do NOT fabricate"), but the scientific-rigor concern is that the *selection claim* currently overstates what the tables show.
**Suggested fix:** Do not fabricate. Either (a) restore the real 64D KMeans Sil/CH/DB and VAE loss/KL from `32/64_smi_vae_training_history_full.pdf` / training logs (needs the numeric source), or (b) reframe l.117/l.166 from "superior/optimal/best" to "selected" and add one sentence that the 64D choice is supported by the clustering-quality *figure* (SM Fig clustering_quality) rather than the table, whose 64D KMeans row is pending population. At minimum, the mismatch between "optimal" prose and "N/A" table cells must be acknowledged.

---

## MEDIUM

### MED-1 — "Genuinely new chemotypes" contradicts the manuscript's own scaffold-preservation finding
**Where:** main l.271 ("the generative model accesses genuinely new chemotypes rather than mere interpolations"); also l.91 "new scaffolds."
**Overclaiming / internal consistency:** The manuscript's central scaffold-paradox result is that ring systems are *preserved* (69.3% scaffold recovery; 1.84× scaffold-to-whole Tanimoto ratio, i.e. scaffold Tanimoto *higher* than whole-molecule). "New chemotypes" implies new scaffold/structural classes, which contradicts scaffold preservation — the novelty is in peripheral substituents on retained scaffolds, not in chemotypes.
**Suggested fix:** Replace "genuinely new chemotypes" with "novel substituent-decorated analogues on preserved scaffolds" (consistent with the 1.84× ratio narrative).

### MED-2 — MPO weight-sensitivity framed as "moderate/stable" despite a 28% pass rate and ADMET ρ as low as 0.26; Vina/DiffDock "most stable" is partly an artifact of the shared-residual back-calculation
**Where:** main l.206 ("yielded a Spearman ρ range 0.26–0.97 … mean 0.792"; "ρ ≥ 0.79 for ±10% Vina/DiffDock vs ρ ≤ 0.55 for ADMET"); SM l.202, l.614, l.627, l.634–636.
**Statistical rigor / independence claim:** The non-independence of S_vina/S_diff is honestly disclosed (main l.206; SM l.198 — back-calculated from a shared residual, split 35:25). That disclosure is good and should stay. The *residual* problem is interpretive: (i) the table shows only **7/25 (28%)** configurations pass both ρ>0.95 AND Jaccard≥0.70, and ADMET −20% drops ρ to **0.26** with Jaccard **0.0** — i.e. the top-20 hit list is quite sensitive to weight choice (72% fail), which is framed as "moderate sensitivity." (ii) Presenting Vina/DiffDock as the "most stable" components (ρ ≥ 0.79) overstates robustness: because their perturbations reallocate *within a shared residual* rather than varying independently, their high ρ is partly a construction artifact (the composite barely moves when you shuffle weight between two back-calculated halves of the same residual). Only QED/ADMET/Ro5 sensitivities are independently interpretable.
**Suggested fix:** State that 18/25 perturbations fail both stability criteria and that the top-20 hit list is sensitive to weight choice (especially ADMET); restate Vina/DiffDock stability as "not independently assessable from the shared-residual design — only QED/ADMET/Ro5 perturbations reflect true independent variation." Consider whether the 76-centroid / 19,913-lead selection (which depends on the chosen weights) warrants an explicit caveat that alternative weightings within the disclosed sensitivity range would change the lead set.

### MED-3 — "Therapeutic window" used for predicted stage activity (eos80ch), not an efficacy-vs-toxicity dose range
**Where:** SM Table (stage_activity) caption l.269 ("a pronounced therapeutic window against asexual blood-stage parasites"); row l.275 ("Primary therapeutic window").
**Overclaiming:** A therapeutic window is specifically the dose range between efficacy and toxicity. Here it labels a *predicted stage preference* (eos80ch median 0.567 asexual vs 0.244 sexual) — a model output preference, not a dose range. (The SI_pred table at SM l.236 was correctly fixed to disclaim "therapeutic window"; this table was not.)
**Suggested fix:** Replace "therapeutic window" with "predicted asexual-stage preference" / "asexual-stage predicted activity."

### MED-4 — PCA Table PC4 row is arithmetically impossible and contradicts the authoritative BMAD report
**Where:** SM Table (pca) l.283–296, specifically l.292 (PC4: Variance 0.000, % Explained 1.1%, Cumulative 100.0%).
**Statistical/numerical:** PC1–PC3 cumulative is 82.3%; PC4 cannot simultaneously be 1.1% *and* raise the cumulative from 82.3% to 100.0% (that would require 17.7%). Variance 0.000 with 1.1% is also self-contradictory. BMAD §1.13 gives PC4 = **6.86%**, cumulative **89.19%** — so the SM table is wrong against the data backbone.
**Suggested fix:** Correct PC4 to 6.86% explained (cumulative 89.2%) per BMAD §1.13 / `c8_pca_explained_variance.txt`, or recompute and reconcile the cumulative column.

### MED-5 — Residual "validated/validates/experimental proxy" overclaim (same class as the fixed C5)
**Where:** main l.93 ("This validated enrichment, combined with a synthetic accessibility filter (SYBA > 0), functions as an orthogonal experimental proxy that justifies hit prioritization"); main l.294 ("The 13 NP-related optimization candidates … validate African natural products as a productive source of antimalarial scaffolds").
**Causal/overclaiming:** C5 fixed "validated discovery" in the Conclusion, but two siblings remain. (i) "Validated enrichment … orthogonal experimental proxy": SYBA is an ML synthetic-accessibility score, not experimental; retrodiction on a positive control is not "validation." (ii) "Validate African natural products as a productive source": 13 computationally-identified candidates do not validate a biological source claim.
**Suggested fix:** l.93 → "This retrospective enrichment, combined with a synthetic-accessibility filter (SYBA > 0), provides converging computational evidence that supports hit prioritization …"; l.294 → "support African natural products as a computationally productive source."

---

## LOW

### LOW-1 — "Selective antiparasitic activity" frames a predicted heuristic ratio as antiparasitic activity
**Where:** main l.287 ("100% of 810 screened seed molecules showing predicted selective antiparasitic activity (SI > 10)"); main l.279 ("consistent with parasite-selective inhibition rather than toxic promiscuity").
**Fix:** "predicted selective prioritization (SI_pred > 10)" — SI_pred is a ranking proxy, not demonstrated antiparasitic activity (no wet-lab). Reserve "antiparasitic activity" for experimentally confirmed inhibition.

### LOW-2 — PfATP4 sample-size inconsistency (184 vs 198)
**Where:** SM l.1044 (MMV table: PfATP4 N=184, "due to the 15-rotatable-bond filter") vs main Table 1 l.229 and SM l.525, l.1268 (PfATP4 N=198, 99 actives/99 decoys).
**Fix:** Reconcile with a footnote — 198 MMV compounds assigned to PfATP4, of which 184 pass the ≤15-rotatable-bond filter used for docking — so the two N's refer to different denominators. Currently they appear contradictory.

### LOW-3 — MCMC subsection title "Latent space optimization" vs body "exploration" (audit C6-residual)
**Where:** main l.119 (subsection title "Latent space exploration by MCMC sampling" — note: title already says "exploration"; the residual flagged in the audit was the older "optimization" wording).
**Status:** The current V4 title at l.119 already reads "exploration," and the body (l.121) is honest ("While modest"). No action needed beyond confirming the title matches the body; if any remaining instance of "optimization" appears in the abstract/conclusion MCMC sentence, align it to "exploration." (Listed only for completeness; appears largely resolved.)

---

## Items checked and found SOUND (no action)

- **Multiple testing:** BH correction (SM Table S22, l.769–809; main l.193) honestly reports 0/24 (or 0/18) significant with rank-biserial r < 0.10, and explicitly flags "excessive statistical power" from large N — methodologically sound and honestly framed.
- **Bootstrap CIs** on enrichment metrics (1000 resamples, 2.5/97.5 percentiles; SM l.1230–1239) — present and correctly described; gap is only their *absence* on the MCMC +0.0246 (CRIT-2).
- **DEKOIS prospective reporting** (0.450, 95% CI 0.367–0.531) — honestly reported across Methods/Validation/Discussion/Limitations/Conclusion; this is the manuscript's strongest falsifiability asset and is well handled.
- **Tartarus orthogonality** (ρ=0.013, p=0.091, n=17,211; main l.305) — traces to BMAD §2.8; honestly reports non-significance and uses it as a design-feature argument, not a performance claim. Sound.
- **pH 5.2 PfCRT re-protonation** (ρ=0.270, +2.2 kcal/mol; main l.311) — traces to BMAD §1.10; p-value given, caveat present. Sound.
- **19,913 leads / 76 centroids / 810 SI / 65,856 library** — trace to source CSVs per audit matrix; numerically sound.
- **99.3% cost reduction** (263,424 → 1,936 = 65,856×4 → 484×4) — arithmetically correct; the objection (HIGH-3) is only to the *ROC attribution*, not the efficiency arithmetic.
- **F3 PfCRT-domination disclosure** — present at main l.311 (87.0% PfCRT / 2.7% PfDHFR; "DiffDock rescoring compensating for per-target weaknesses of Vina"). Good — and it supports, rather than resolves, CRIT-1.

---

## Bottom line
The manuscript's irreproachable numbers (audit-verified) sit on top of two scientific-rigor weak points a number-tracing audit cannot catch: (1) the headline 0.924–1.000 enrichment is tautological for 3/4 targets (score-based labels) with the only prospective benchmark at 0.450, and (2) the MCMC +0.0246 is a best-chain value mislabeled as the mean-chain gain (~2.8× inflated) with no uncertainty on a weak (R²=0.377) surrogate. Both are falsifiability/statistical-rigor issues, both are fixable by disclosure + reframing (no new calculations needed), and neither requires re-running experiments. The remaining HIGH/MEDIUM items are overclaiming and causal-language residuals ("mathematically prove," "genuinely new chemotypes," SI_pred misdefined as an IC₅₀ ratio at l.260, "therapeutic window" for stage preference, sensitivity framed as stable at 28% pass) plus a PCA table error against the BMAD backbone.
