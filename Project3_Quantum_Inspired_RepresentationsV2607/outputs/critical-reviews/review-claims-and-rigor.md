# P3 Critical Review — Pass B: Claims & Rigor

**Manuscript:** *Persistent homology resolves the scaffold paradox in AI-generated African antimalarial candidates* (Paper 3, target Journal of Cheminformatics)
**Lens:** adversarial-general + scientific-critical-thinking
**Model:** Opus 4.8 (claims-and-rigor pass)
**Date:** 2026-07-27
**Scope:** novelty/"first" claims, overclaiming, logical gaps, falsifiability. Review-only — no manuscript/script file was edited.
**CSV cross-checks performed:** `results/p3_h1_rrs_correlation_final.csv`, `p3_h1_rrs_correlation_final.txt`, `p3_rrs_tfp_final.csv`, `results/p3_physical_validation/p3_tda_promiscuity.csv`, `results/p3_tartarus_tne_regression.csv`, `results/p3_qks_benchmark.csv`, `scripts/p3_rrs_tfp_expansion.py`.

---

## GATE VERDICT (one sentence)

**FAILS the rigor gate as written:** the three load-bearing headline claims — the H₁-RRS "biomarker" ρ=0.916, the QKS "task-specific quantum kernel sensitivity," and the H₁-ring-complexity → promiscuity mechanism — are each unsupported or directly contradicted by the project's own result CSVs, and the prior audit's claimed mitigation (canonize ρ=0.312) was never applied to the main manuscript; these must be downgraded from biomarker/advantage claims to hypothesis-generating observations before a Q1 submission can survive.

---

## CRITICAL

### C1 — Headline H₁-RRS correlation ρ=0.916 is unreproducible, inconsistent with the project's own scripts, and collapses at scale
**Locations:** abstract L99; discussion L513; conclusion L532; figure caption L520. SM L104/L639 report ρ=0.947 (pilot, n=14) → 0.361 (n=77). Prior audit §Weakness#2 says canonical value is 0.312 (p=0.006, n=77).
**Verdict: UNSUPPORTED / overclaiming.**
**Evidence from CSVs:**
- `p3_h1_rrs_correlation_final.csv` (the definitive n=77 analysis) gives, for H₁ features: `H1_count ρ=+0.3124 (p=0.0057)`, `H1_entropy ρ=+0.2544 (p=0.026)`, `H1_max_pers ρ=+0.0674 (p=0.561, NOT SIGNIFICANT)`, `H1_mean_pers ρ=+0.0056 (p=0.961, NS)`. There is **no H₁ feature with ρ≈0.916 or 0.947** anywhere in the results.
- `p3_h1_rrs_correlation_final.txt` records the class distribution at n=77 as **Class A=46, B=31, C=0, D=0**. The "resistance-vulnerable" Class D that the entire resilient-vs-vulnerable contrast rests on contains **zero compounds** at scale.
- `scripts/p3_rrs_tfp_expansion.py:5` states the pilot headline is `rho=0.947 (n=14)`, not 0.916. So the main manuscript's 0.916 is a **third value** that matches neither the script (0.947) nor the definitive CSV (max 0.312).
- grep across `results/` confirms 0.916 never appears as an H₁-RRS Spearman ρ (all 0.916 hits are unrelated QKS AUCs / fingerprint bits).

**Fix (one-line each):** Abstract L99 → replace "Spearman ρ = 0.916, p < 0.0001, n=14 … establishing a computationally inexpensive topological predictor" with "Spearman ρ = 0.31, p = 0.006, n=77 (H₁ count); pilot ρ = 0.95 on n=14 did not replicate (Class D absent at n=77), so this is hypothesis-generating only." Discussion L513 / Conclusion L532 / caption L520 → match the n=77 numbers and delete every "p<0.0001" and "biomarker/predictor" framing; reframe as "preliminary, unreplicated." Reconcile 0.916 vs 0.947 vs 0.312 to a single canonical value sourced from the CSV.

### C2 — The ρ=0.916 / "p<0.0001" on n=14 with Class A=3, Class D=1 is statistically meaningless as a biomarker claim
**Locations:** abstract L99; discussion L513; conclusion L532; caption L520; limitations L528.
**Verdict: overclaiming (statistical reason below).**
**Statistical reason a tough reviewer states first:** A Spearman correlation on n=14 where the contrast of interest (resilient vs vulnerable) is carried by only **4 effective points** (Class A n=3, Class D n=1) is not a 14-point test of the resilience hypothesis — it is a 4-point comparison in which one entire class is a singleton. (i) With Class D n=1, the "mean 1.73 Å for Class D" is a single observation with no variance, so the Class-A-vs-D contrast is "3 numbers vs 1 number"; the apparent separation is almost entirely determined by where that one Class-D point sits and by the 10 Class-B/C context points, none of which define the resilience axis. (ii) The headline feature is "H₁ persistence," but the definitive CSV shows H₁ *max persistence* ρ=0.067 (p=0.56) and *mean persistence* ρ=0.006 (p=0.96) — i.e., the persistence feature the manuscript emphasizes has **no correlation at all** at n=77; only H₁ *count* (ρ=0.31) is weakly significant. (iii) "p<0.0001" on n=14 can only come from a permutation/bootstrap test; with the real signal living in 4 of 14 points, such a test is over-powered relative to the effective n and is exquisitely sensitive to a single reclassification — which is exactly why it collapsed to ρ≈0.31 (count) / 0.06 (persistence) at n=77. A reviewer will read "p<0.0001, n=14, one class n=1" as a small-sample artefact, not a biomarker. (iv) The bootstrap 95% CI `[0.799, 1.000]` reported at SM L639 is itself a red flag: a CI whose upper bound is exactly 1.0 and lower bound 0.80 on 4 effective points is too narrow to be trustworthy and signals the resampling is reflecting the degenerate contrast, not a stable effect.
**Fix:** Move the entire H₁-RRS result to "preliminary / hypothesis-generating" in abstract, discussion, conclusion; report n=77 ρ=0.31 (count) as the only replicated value; state explicitly that H₁ *persistence* (the feature hypothesized) did not replicate (ρ=0.067, p=0.56); remove "p<0.0001" everywhere; state the pilot (n=14, A=3/D=1) cannot support any biomarker claim and that Class D=0 at n=77 precludes a resilient-vs-vulnerable test until a cohort with genuine vulnerable compounds is assembled.

### C3 — "Task-specific quantum kernel sensitivity" for polypharmacology is an overclaim and contradicts the manuscript's own "kernels indistinguishable" conclusion
**Locations:** Table 4 footnote L365 ("QKS AUC 0.747 vs RBF 0.737; the consistently positive Δ=+0.010 across 5 folds (σ=0.008) suggests task-specific quantum kernel sensitivity"); results L463 ("demonstrating that the quantum kernel extracts polypharmacologically relevant information beyond classical kernel baselines"); conclusion L532.
**Verdict: overclaiming.**
**Reasoning:** Δ=+0.010 with σ=0.008 gives Δ/σ≈1.25. As a paired comparison across 5 folds, that is a t-statistic of ~1.25 on 4 degrees of freedom → uncorrected two-tailed p≈0.26, i.e., **not significant even before multiple-comparison correction.** The phrase "consistently positive across 5 folds" is the only support offered; "all 5 folds positive" with a mean of +0.010 and σ=0.008 is not the same as significant (a sign test on 5/5 gives p=0.0625 uncorrected, also not significant at α=0.05, and certainly not after correction). No corrected p-value is reported for this claim. Worse, this is **internally contradictory**: in the *same* Table 4 body (L347–361) and again in §4.5 (L499–501) the manuscript concludes Quantum/RBF/Linear are "statistically indistinguishable (p>0.05)" and that the apparent quantum advantage was "an artefact of untuned RBF." The polypharmacology Δ (+0.010) is *smaller* than the binary-task Δ (+0.050, 0.751 vs 0.701) that the manuscript itself labels a non-significant artefact — yet the smaller effect is rebranded as "sensitivity." That is cherry-picking the favourable framing for the weaker result.
**Note:** A dedicated polypharmacology-QKS results CSV with a p-value could not be located in `results/` (the 0.747/0.737 values do not appear together in any results CSV; `p3_qks_benchmark.csv` holds the binary-task per-fold values only) — **[partially UNVERIFIED-needs-conda/HPC job CSV]** the raw polypharm per-fold values should be deposited and the paired test re-run with Bonferroni correction across the kernel/task comparisons.
**Fix:** Replace "suggests task-specific quantum kernel sensitivity" and "extracts polypharmacologically relevant information beyond classical kernel baselines" with "QKS and RBF are statistically indistinguishable on the polypharmacology task (Δ=+0.010, σ=0.008, paired t p≈0.26 uncorrected; not significant)," and fold this into the existing "no quantum advantage" conclusion rather than carving out an exception.

### C4 — Novelty / "first" claims (N5–N8 in ms; N1–N4 in README) are overstated given the negative results
**Locations:** ms N5–N8 at L120; README N1–N4 at README L28–31 ("First proof…", "First quantum kernel…", "First TDA…"); abstract L99; conclusion L532.
**Verdict per claim:**

| Claim | Location | Verdict | Why |
|-------|----------|---------|-----|
| **N5 / "systematic TDA vs ECFP4 benchmark … 1D PH captures scaffold-level features invisible to classical fingerprints"** | ms L120; cf. README N3 L30 | **Overstated.** TFP standalone AUC=0.587 (Table 1, L310) — *below* the 0.5-equivalent-of-useful bar and far below ECFP4 0.868. "Invisible to ECFP4" is contradicted by TFP+ECFP4 AUC=0.865 (Δ=-0.003 vs ECFP4, p=0.884): adding TFP to ECFP4 adds nothing. The only TDA configuration that matches ECFP4 is PersStats+RF (SM S8, AUC 0.873, Δ=+0.005, **not significant**). So "captures features invisible to ECFP4" is not supported — TFP adds no incremental discriminative signal. |
| **N6 / "application of PH to resolve a chemical space paradox (92.6% vs 69.3%) by decomposing topology into H₀/H₁"** | ms L120; cf. README N4 L31 | **Supported as interpretation, overstated as "resolves."** The H₁/H₀ decomposition is a reasonable *narrative*, but no statistical test links 69.3% scaffold recovery to H₁ preservation or 92.6% Tanimoto to H₀ divergence (see H3). "Resolves" implies a demonstrated mechanism; only a narrative is provided. |
| **N7 / "tensor network descriptor achieving 5.9× real-atom compression while retaining binding-relevant information"** | ms L120; cf. README N1 L28 ("First proof that TNE retains 3D physical binding affinity across 19,913 molecules") | **Overstated (README) / partly supported (ms).** ms uses the defensible 5.9× and Tartarus R²=0.473 for PfDHFR (1 of 3 targets). README N1 says "First proof … retains 3D physical binding affinity across 19,913 molecules" — but TNE *loses* to ECFP4 on 2 of 3 targets (6Y2F: 0.464 vs 0.578; 4LDE: 0.334 vs 0.517, CSV-confirmed), so "retains binding affinity across 19,913 molecules" overclaims a single-target win into a library-wide proof. Also "15.6× compression" in README N1 is the padded upper bound, not the 5.9× real figure the ms uses. |
| **N8 / "applicability domain analysis using quantum kernel density"** | ms L120; cf. README N2 L29 ("First quantum kernel vs SVM RBF benchmark on a hard multi-target antimalarial polypharmacology task") | **Overstated (README N2) / supported-but-negated (ms N8).** The QK-density discriminator is *beaten* by ECFP4 Tanimoto (AUC 0.425–0.511 vs 1.000, Table 5), so as a domain discriminator it is worse than the classical baseline. README N2's "Quantum Advantage on Polypharmacology" is directly negated by C3 (Δ=+0.010, n.s.). The ms N8 itself is a fair description of what was done, but the README's "Quantum Advantage" headline is contradicted by the ms's own "no quantum advantage" conclusion. |

**Cross-cutting fix:** Drop the word "First proof" (README N1) and "Quantum Advantage" (README N2) entirely; reframe all N1–N4/N5–N8 as "first *systematic application/benchmark* of … on African-NP space," and qualify N5 ("invisible to ECFP4") and N7 README ("retains binding affinity across 19,913") with the negative per-target/per-feature results. README must be reconciled to the ms (5.9× not 15.6×; n=77 ρ=0.31 not 0.916; 5-fold not 10-fold — see S7).

---

## HIGH

### H1 — Causal claim (a) "H₁ rigidity → lower conformational entropy penalty → resistance resilience" is unfalsifiable as stated
**Location:** discussion L515 ("a highly rigid cycle system reduces the conformational entropy penalty upon binding … 'locks' the ligand in its bioactive pose … conferring resilience").
**Verdict: unsupported / not falsifiable as written.**
**What would refute it:** (i) an MD-derived conformational entropy ΔS_conf measurement showing rigid-H₁ compounds actually pay a smaller entropy penalty on binding (the manuscript has MD data from the companion paper but reports **no** entropy calculation — the claim is pure inference); (ii) a demonstration that H₁ persistence predicts resilience *after controlling for* molecular size / binding affinity (the n=14 cohort are all "established high-affinity binders," so the resilience axis is confounded with affinity and with H₀/atom count); (iii) the prediction that artificially rigidifying a scaffold increases resilience — testable via the same MD pipeline, not done. As written, the mechanism is a just-so story: it invokes an unmeasured quantity (ΔS_conf) to explain a correlation (ρ=0.916) that itself does not replicate (C1/C2).
**Fix:** Rewrite as "we *speculate* that H₁ rigidity may reduce the conformational-entropy penalty on binding, a hypothesis testable by ΔS_conf from the companion MD trajectories; we do not measure entropy here." Remove "conferring resilience" / "'locks' the ligand" as established fact.

### H2 — Causal claim (b) "lower topological complexity (H₁/H₀) → promiscuity via conformational adaptability" is contradicted by the promiscuity CSV
**Location:** results L465 ("lower topological complexity in ring structures (H₁) and structural components (H₀) endows candidate molecules with optimal conformational adaptability across multiple malaria targets, reducing steric clash penalties"). Echoed conclusion L532.
**Verdict: overclaiming / partially contradicted.**
**CSV evidence (`p3_tda_promiscuity.csv`, N=17011):** the strongest negative correlations with #targets-bound are `H0_count ρ=-0.248`, `H0_entropy ρ=-0.243` (ms L465 matches CSV ✓). But the **ring-topology features the mechanistic sentence emphasizes are near-zero**: `H1_max_pers ρ=-0.00199 (p=0.795)`, `H1_count ρ=-0.099`, `H1_entropy ρ=-0.190`. H₁ *max persistence* — the feature the manuscript elsewhere (L515) calls "cycle rigidity" and links to resilience — has **essentially zero** correlation with promiscuity (p=0.795). What actually drives the signal is H₀ (connected-component count ≈ atom count ≈ molecular size): bigger molecules bind fewer targets. That is a **molecular-size / specificity** effect, not a "ring-topology conformational-adaptability" insight. The "conformational adaptability" and "steric clash penalty" language is a post-hoc narrative overlaid on a size correlation, and the "ring structures (H₁)" clause is not supported by the H₁ persistence numbers.
**Fix:** Replace the mechanistic sentence with: "Molecular size (H₀ count/entropy, the dominant topological correlate, |ρ|≈0.24) anti-correlates with multi-target binding — a size/specificity effect. H₁ ring-topology features show weak-to-null correlations (H₁ max-persistence ρ=-0.002, p=0.80), so we do not claim a ring-complexity mechanism for promiscuity." Delete "conformational adaptability" / "steric clash penalties" unless supported by a conformational analysis.

### H3 — Causal claim (c) scaffold-paradox mechanism "H₁ preserved / H₀ diverges explains 92.6% vs 69.3%" is unfalsifiable / partly tautological
**Location:** results/scaffold-paradox L330 (caption), L325; discussion L477–479 ("scaffold recovery 69.3% reflects H₁ persistence … 92.6% distinction reflects H₀ features").
**Verdict: interpretation stated as mechanism; not falsifiable as written; partly tautological.**
**Problems:** (i) **Tautology:** Bemis–Murcko scaffolds are *defined* as the ring system after side-chain removal, so "scaffold recovery correlates with H₁ (ring topology)" is close to true-by-definition — scaffolds are rings, H₁ counts rings. Stating that scaffold preservation "reflects H₁ preservation" does not *explain* the paradox, it restates that rings are conserved while substituents vary. (ii) **No statistical link:** the manuscript provides no test mapping the 69.3% number to H₁ or the 92.6% number to H₀ — Figure 3 caption mentions a "Wilcoxon p-value" for seed-vs-generated H₁/H₀ distributions but **no p-value, effect size, or N is reported in the text** for that comparison. (iii) The "1.84× ratio" (scaffold Tanimoto 0.379 vs whole-molecule 0.206, L479) is presented as quantitative confirmation, but it only shows scaffolds are more conserved than whole molecules — expected, and not specific to the H₁/H₀ decomposition. (iv) The phrase "H₁ preservation with H₀ divergence *explains* the paradox" (caption L330) is a causal claim with no causal test.
**What would refute/falsify it:** a regression of scaffold-recovery on H₁-distance controlling for H₀-distance across seed→generated pairs, or a permutation test showing H₁-distance predicts scaffold-recovery better than H₀-distance (or than random). Without that, "resolves/explains" should become "is consistent with."
**Fix:** Soften "explains/resolves" to "is consistent with the interpretation that"; report the actual Wilcoxon p-values and N for seed-vs-generated H₁ and H₀ distributions in the text and caption; add the controlling regression or explicitly state the mapping is interpretive, not statistically demonstrated; acknowledge the partial tautology (scaffolds are rings by definition).

### H4 — "Complementary tools" framing vs the negative results is a goalpost shift
**Location:** conclusion L532/L540 ("position these quantum-inspired representations not as replacements for classical fingerprints, but as complementary diagnostic tools that reveal topological dimensions … inaccessible to conventional cheminformatics"); discussion L491.
**Verdict: overstated framing.** "Complementary" implies each tool contributes *incremental* signal the others lack. The data show the opposite for prediction: TFP+ECFP4 = 0.865 vs ECFP4 = 0.868 (Δ=-0.003, p=0.884, Table 2 L444) — TFP adds **nothing** to ECFP4 for classification; Hybrid minus TFP = 0.837 vs Hybrid = 0.842 (Δ=-0.005) — TFP's incremental contribution to the hybrid is within noise; QKS standalone is beaten by ECFP4 (0.751 vs 0.868) and is statistically indistinguishable from tuned RBF. The genuinely "complementary" result is the **scaffold-paradox interpretation** (H₁/H₀ decomposition as a *diagnostic*, not a predictor) and the **promiscuity size-effect** — both of which are interpretive (H2/H3), not predictive. Calling them "complementary diagnostic tools that reveal dimensions inaccessible to conventional cheminformatics" overstates tools whose incremental predictive value is null and whose diagnostic value is narrative.
**Fix:** Replace "complementary tools … inaccessible to conventional cheminformatics" with "interpretive diagnostics that do not improve predictive performance over ECFP4 (TFP+ECFP4 Δ=-0.003, n.s.) but offer a topological *reading* of library structure (scaffold paradox) and a size-based correlate of multi-target binding."

### H5 — SM promiscuity correlations contradict both the main manuscript and the CSV (seed S5, confirmed)
**Locations:** main L465 (H0_count -0.248, H0_entropy -0.243, H1_entropy -0.190, N=17011) ✓ matches `p3_tda_promiscuity.csv`; SM L579 (H0 max persistence -0.167, H1 entropy -0.161) ✗.
**Verdict: SM values are wrong.** CSV gives `H0_max_pers ρ=-0.152` (not -0.167) and `H1_entropy ρ=-0.190` (not -0.161). The SM cites different features *and* different values than either the main text or the generating CSV.
**Fix:** Replace SM L579 numbers with the CSV values and the same features as the main text (or explicitly state the SM reports a different feature subset with CSV-sourced numbers).

### H6 — SM Tartarus target/PDB labels contradict the main manuscript and the CSV (seed S3, confirmed)
**Locations:** main L459 (`1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT`); SM L573 (`1SYH/PfDHFR, 6Y2F/PfCRT homologue, 4LDE/PfClpP homologue`); ChEMBL enrichment SM L448 (`PfDHFR/7F3Y, PfATP4/9N10, PfCRT/6UKJ` — a separate, legitimate experiment with different PDBs).
**Verdict: SM L573 is wrong; CSV agrees with the main manuscript.** `p3_tartarus_tne_regression.csv` labels rows `PfDHFR (1SYH)`, `PfATP4 (6Y2F)`, `PfCRT (4LDE)` — matching main L459, **not** SM L573 (which swaps 6Y2F→PfCRT and 4LDE→PfClpP). The "homologue" caveat in the SM does not resolve this: the main text and CSV assign 6Y2F to PfATP4 and 4LDE to PfCRT outright. A reviewer cross-checking SM against main will flag a target-identity error, which in a docking paper reads as a possible data-integrity problem.
**Fix:** Make SM L573 read exactly `1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT` to match main L459 and the CSV; if 4LDE is genuinely a PfClpP homologue used as a PfCRT surrogate, state that explicitly and reconcile with the CSV/main label.

---

## MEDIUM

### M1 — "20 high-confidence leads" (L511) vs "n=14" correlation (L513/L520) unexplained (seed S8)
**Verdict: internal inconsistency.** L511 cites 20 leads from the companion MD study; the H₁-RRS correlation uses n=14. The 6-compound gap is never explained (dropout? missing TFP? missing RRS?). Combined with Class A=3/Class D=1 at n=14 and Class D=0 at n=77, the cohort definition is opaque.
**Fix:** State explicitly why 20→14 (e.g., "6 of 20 lacked valid 3D conformers / RRS scores") and report the class breakdown of the 14.

### M2 — TNE regression ECFP4 numbers in main text differ slightly from the CSV (minor, but a numbers-pass issue)
**Location:** main L461 (PfDHFR ECFP4 R²=0.451/ρ=0.683; 6Y2F ECFP4 R²=0.570/ρ=0.762; 4LDE ECFP4 R²=0.515/ρ=0.733). CSV: 0.4606/0.689; 0.5781/0.769; 0.5174/0.734.
**Verdict: small mismatches, directionally consistent.** The TNE numbers match (0.473/0.464/0.334). The ECFP4 baseline numbers are off in the 2nd–3rd decimal — likely a re-run vs an earlier CSV version. Not load-bearing for claims, but a numbers reviewer will flag it.
**Fix:** Re-paste ECFP4 values from the current `p3_tartarus_tne_regression.csv`.

### M3 — Abstract "non-linear ring-topology features … that ECFP4 cannot capture" overclaim (seed S18)
**Location:** abstract L99.
**Verdict: overstated.** The hybrid only *matches* (does not beat) ECFP4 (0.842 vs 0.868, p=0.111), and the ablation shows the hybrid's discriminative power comes from the **QK-PCA** component (γ=0.80), not TFP (removing TFP drops AUC only 0.842→0.837). "Features ECFP4 cannot capture" implies incremental signal, but TFP+ECFP4=0.865 vs ECFP4=0.868 shows TFP captures nothing ECFP4 lacks for prediction.
**Fix:** Change to "while matching ECFP4 discriminative performance (AUC 0.842 vs 0.868, n.s.) and providing an interpretable topological reading of scaffold structure."

### M4 — PHCO AUC reported as 0.500 "exactly random" in main text while SM documents a bug fix yielding 0.801 (seed S4)
**Locations:** main L295, L312, L491 (PHCO AUC 0.500, "exactly random"); SM §PHCO bug L229–232 (bug fix → AUC 0.801).
**Verdict: main text reports the *buggy* value as if it were a real finding.** The SM explicitly says the 0.500 was caused by a `SparseBitVect`/`ConvertToNumpyArray` silent-failure bug and that the corrected AUC is 0.801. Yet the main text uses 0.500 as evidence that "pharmacophore-based bit vectors provide no discriminative information" (L295/L491) — a substantive conclusion drawn from a known software bug. A reviewer reading SM §PHCO will see the main-text claim is refuted by the authors' own correction.
**Fix:** Either (a) report PHCO AUC=0.801 in the main benchmark (and drop the "no discriminative information" claim), or (b) if 0.801 is from the 200-mol dev set only and not re-run on the full 19,849 benchmark, state that explicitly and refrain from the "no discriminative information" conclusion until the corrected PHCO is benchmarked at full scale.

### M5 — "p<0.0001" appears in the abstract/conclusion for the H₁-RRS result with no test specified
**Location:** abstract L99; conclusion L532; caption L520.
**Verdict: unsupported.** The definitive CSV's only H₁ p-values are 0.006 (count), 0.026 (entropy), 0.56/0.96 (persistence). "p<0.0001" can only come from the n=14 permutation/bootstrap (SM L639) which does not replicate (C1/C2). No test name is attached to "p<0.0001" in the main text.
**Fix:** Remove "p<0.0001"; report the n=77 paired/permutation p for the *count* feature (0.006) and state persistence features are non-significant.

---

## Reviewer-likely objections ranked by rejection risk (done-criteria #5)

**#1 (highest risk) — Computational (eos80ch) labels, not experimental; the "resistance biomarker" and "promiscuity mechanism" are built on ML-predicted labels and an unreplicated n=14 pilot.**
Pre-emptive in text: Limitations "Second" point (L528) does state labels are computational and "All claims … should be understood as predictions within a computational framework." **Required fix:** the abstract/discussion/conclusion do not honour this caveat — they call ρ=0.916 a "predictor/biomarker" and the promiscuity correlation a "mechanism." Downgrade per C1/C2/H2. The ChEMBL proxy (3 active PfATP4 analogues, SM Table S10) is too thin (3/231) to rescue a biomarker claim.

**#2 — The headline H₁-RRS ρ=0.916 does not replicate (0.31 at n=77) and the vulnerable class vanishes (Class D=0 at n=77).** A reviewer who reads the SM (which admits 0.947→0.361) alongside the abstract (which headlines 0.916) sees three incompatible numbers and a result that collapses under expansion. **Required fix:** C1+C2 — single canonical number, hypothesis-generating framing, honest "did not replicate" statement. This is the single most likely trigger for a "major revision"/reject because it is an overclaim on the paper's most-emphasised finding.

**#3 — "Quantum advantage/sensitivity" claimed where Δ/σ≈1.25 (n.s.) and the manuscript simultaneously says kernels are indistinguishable.** A Q1 cheminformatics/ML reviewer will compute the t-statistic from the reported Δ and σ and find p≈0.26, then read the internal contradiction (C3). **Pre-emptive in text:** the "no quantum advantage" cautionary tale (L499–501) is genuinely strong — but the polypharmacology footnote (L365) carves out an unjustified exception. **Required fix:** C3 — delete the "task-specific sensitivity" exception and fold polypharmacology into the "no advantage" conclusion.

**#4 — Single library + QKS only on a 10k subsample (O(N²)); generalizability and scalability of the quantum claims unproven.** Pre-emptive in text: Limitations "Sixth" (library bias, L528) and the O(N²) discussion (L489, L507) are present and honest. **Required fix:** minor — explicitly state the polypharmacology QKS is also on the 10k subsample (not stated at L463) and that no external-library replication exists; this lowers the ceiling on any QKS claim and is consistent with C3.

**#5 — TFP/TNE negative result (AUC 0.587/0.606) vs "complementary tools / features ECFP4 cannot capture" framing.** Pre-emptive in text: the negative results are reported (Table 1) and the discussion (L493–495) gives a mechanistic explanation. **Required fix:** H4 + M3 — the "complementary / cannot capture" framing in abstract/conclusion overstates tools whose incremental predictive value is null (TFP+ECFP4 Δ=-0.003); reframe as interpretive diagnostics, not complementary predictors.

---

## Notes on verification status
- All CSV-cited numbers in C1, C2, H2, H5, H6, M2 were read directly from the result files (paths above); no fabrication.
- **[UNVERIFIED-needs-conda/HPC]**: the per-fold polypharmacology QKS values behind Δ=+0.010/σ=0.008 (C3) — no dedicated results CSV found in `results/`; the paired p≈0.26 is computed from the reported Δ and σ (5 folds, 4 df) as the correct test of the claim, but the raw per-fold file should be deposited and the test re-run with Bonferroni correction. The n=14 pilot raw data behind 0.916/0.947 was also not located as a standalone CSV (the 0.947 is referenced in `scripts/p3_rrs_tfp_expansion.py:5`); its reproducibility cannot be confirmed from the deposited artefacts.
- The real ρ cross-check requested in done-criteria #2: **computed from CSV** — definitive n=77 max H₁ ρ = 0.312 (count); H₁ *persistence* (the manuscript's emphasised feature) ρ = 0.067 (p=0.56, NS). The manuscript's 0.916 is not reproducible from any deposited CSV.
