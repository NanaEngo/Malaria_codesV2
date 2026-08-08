# P3 — Analysis Ledger

Re-anchored 2026-08-06 against the post-HPC canonical run. Every number in
`manuscript/LaTeX/Paper3_Quantum_InspiredV2608.tex` must trace to an entry here.

**Manuscript base:** `Paper3_Quantum_InspiredV2608.tex` (2026-08-05), adopted this session
over the superseded `_V2` folder branch (which still carried ECFP4 0.949, Hybrid 0.842,
TFP 0.877 and a `TFP = 0.587` value present in no deposited file).

**Verification environment:** `/home/tchapet/VirtualEnv` (Python 3.12.3), numpy + scipy.
Entries marked *recomputed* were re-derived from the raw per-fold records in this session,
not copied from a summary file.

**Supersession rule:** entries are never overwritten. A corrected value gets a new ID and
the old entry is marked `SUPERSEDED BY Lxxx`.

---

## L101 — Classical descriptor benchmark, canonical panel

- **Method:** 5-fold stratified cross-validation, Random Forest, canonical panel of
  19,836 molecules (the subset of the 19,849-molecule library with complete TNE embeddings).
  Binary activity labels from the eos80ch model.
- **Source:** `results/p3_classical_benchmark_19849.csv` (40 per-fold rows);
  summary `results/p3_classical_benchmark_19849_summary.txt`.
- **Numbers (mean AUC ± SD over 5 folds, *recomputed*):**

  | Descriptor | AUC | SD |
  |---|---|---|
  | ECFP4 | 0.9475 | 0.0045 |
  | AP | 0.9399 | 0.0051 |
  | BPF | 0.9389 | 0.0046 |
  | FCFP4 | 0.9183 | 0.0060 |
  | MACCS | 0.9045 | 0.0054 |
  | PHCO | 0.8959 | 0.0039 |
  | TFP | 0.8759 | 0.0059 |
  | TNE | 0.7219 | 0.0068 |

- **Interpretation:** the classical fingerprints win, and they win on their home ground.
  ECFP4 encodes exactly the local atom environments that drive the eos80ch label, so its
  0.948 is close to a ceiling for this task rather than evidence that topology is useless.
  TFP at 0.876 sits below the four circular/path fingerprints but above the 2D pharmacophore
  descriptor, which is the expected position for a representation that discards atom identity
  and keeps only shape. TNE at 0.722 is the honest cost of 6.1× compression: enough signal
  survives to beat chance by a wide margin, not enough to compete as a standalone predictor.
- **Caveats:** single label source (eos80ch), single classifier family for these rows, seed 42.
  The SD is the across-fold SD, not a bootstrap CI, and 5 folds give df = 4 for any paired test
  built on them — see L106.
- **Claims:** abstract ranking sentence; Table 1; Results §3.1; Conclusion.

## L102 — Canonical hybrid and ablation

- **Method:** same 5-fold protocol and panel as L101. Hybrid = TFP + TNE + kernel-PCA
  quantum features, concatenated after unit normalisation. Ablation removes one component
  and refits. Paired two-sided *t*-test across the 5 folds.
- **Source:** `results/p3_hybrid_canonical_checkpoint.json` (`section: ablation_QK`).
- **Numbers (*recomputed* from per-fold AUC):**

  | Model | AUC | SD | Δ vs Hybrid | t | p |
  |---|---|---|---|---|---|
  | Hybrid (rf) | 0.8876 | 0.0065 | — | — | — |
  | Hybrid − TNE | 0.8990 | 0.0054 | **+0.0114** | +12.92 | 2.07 × 10⁻⁴ |
  | Hybrid − TFP | 0.8736 | 0.0065 | −0.0139 | −11.93 | 2.83 × 10⁻⁴ |
  | Hybrid − QKS | 0.8472 | 0.0058 | −0.0404 | −19.44 | 4.13 × 10⁻⁵ |
  | Hybrid (svm) | 0.8323 | 0.0082 | — | — | — |

- **Hybrid vs ECFP4 (rf, paired, 5 folds):** Δ = −0.0599, t = −29.90, p = 7.45 × 10⁻⁶.
- **Interpretation:** the fusion is carried by the quantum-kernel block. Dropping QKS costs
  0.040 AUC, three times the cost of dropping TFP. TNE is not merely redundant — removing it
  *raises* AUC by 0.011, and the effect is consistent across all five folds. The hybrid is
  therefore best described as a TFP + QKS descriptor that currently carries TNE as ballast.
  The manuscript states this (Table 2 caption, Results §3.4); the Discussion should not
  describe TNE as contributing to hybrid performance, because it does not.
- **Caveats:** df = 4. The *t* statistics are inflated by fold non-independence — the five
  training sets overlap by 60%, so these p-values are optimistic and should be read as
  "consistent in direction across folds", not as calibrated significance. Fusion weights
  (0.10 / 0.10 / 0.80) were tuned outside this run; the tuning set must be named or the
  ablation inherits a leakage question (audit-v3 M6, open).
- **Claims:** abstract hybrid sentence; Table 2 + caption; Results §3.4; Discussion §4.2.

## L103 — Quantum kernel vs tuned RBF and linear baselines

- **Method:** 5-fold CV SVM on precomputed kernel matrices. Circuit: `IQPEmbedding`,
  1 repeat, 6 qubits, noiseless statevector. RBF gamma tuned by grid search.
- **Source:** `results/p3_qks_summary_n19849.txt`, `results/p3_qks_summary_n5000.txt`.
- **Numbers:**

  | n | QK AUC | RBF AUC | linear AUC | QK vs RBF | QK vs linear |
  |---|---|---|---|---|---|
  | 19,849 | 0.8230 ± 0.0081 | 0.8292 ± 0.0066 | 0.5365 ± 0.0729 | t = −2.594, p = 0.0604 | t = 9.733, p = 0.0006 |
  | 5,000 | 0.8199 ± 0.0229 | 0.8260 ± 0.0143 | 0.5173 ± 0.0519 | t = −0.901, p = 0.4186 | t = 12.736, p = 0.0002 |

- **Target alignment:** QK 0.6216 ± 0.0129 vs RBF 0.1454 ± 0.0064 at n = 19,849.
- **Interpretation:** the quantum kernel does not beat a properly tuned RBF at either scale,
  and at the larger sample it trails by 0.006 AUC with p = 0.060 — a borderline result that
  points toward quantum *disadvantage*, not parity. Calling this "indistinguishable" reads the
  non-significance as evidence of equivalence, which a df = 4 test cannot support. The
  alignment gap is the interesting part: the quantum kernel aligns with the labels four times
  better than RBF yet predicts no better, which says the extra alignment lands in directions
  the SVM margin does not use.
- **Caveats:** simulation only, no hardware noise. Non-significance at df = 4 is a
  power statement, not an equivalence claim; a TOST or bootstrap CI would be needed to assert
  equivalence. The two sample sizes are nested, so the two p-values are not independent.
- **Claims:** abstract kernel sentence; Results §3.5; Discussion §4.3; SM Table S-qkernel.

## L104 — Tensor Network Embedding: compression and runtime

- **Method:** Tucker decomposition, bond dimension 8, ranks (8, 8, 3), padded input
  tensor 100 × 10 × 3 = 3000 elements, 192-element core descriptor. 4 CPU workers.
- **Source:** `results/p3_tne_summary.txt`.
- **Numbers:** 19,849 processed → 19,836 valid, 13 failed. Mean atoms/molecule 39.0
  (median 39.0, range 12–70). Real compression ratio 6.1× (range 1.9×–10.9×);
  padded ratio 15.6×. Mean reconstruction error 0.1130 (max 0.2196).
  Wall time 488.0 s = 8.13 min, throughput 40.65 mol/s.
- **Interpretation:** the 13 failures define the canonical panel and are the reason the paper
  evaluates 19,836 rather than 19,849 molecules — a distinction the manuscript must keep
  straight, because the kernel benchmarks use the full 19,849. The 6.1× figure is the honest
  one to quote: the 15.6× padded ratio is an artefact of zero-padding to 100 atoms and would
  inflate with any larger pad. A mean reconstruction error of 0.11 is where the 0.722 standalone
  AUC in L101 comes from.
- **Caveats:** the failure mode of the 13 molecules is not characterised. Runtime is
  hardware-specific and was not repeated, so no uncertainty is attached to 488 s.
- **Claims:** abstract compression figure; Methods §2.4; Results §3.3; Conclusion runtime.

## L105 — TDA feature statistics, full library

- **Method:** Vietoris–Rips persistent homology on single 3D conformers, H₀/H₁/H₂.
- **Source:** `results/p3_tda_summary.txt`.
- **Numbers:** 19,849 processed, 19,849 valid TFPs, 0 failures, 1 conformer/molecule.
  H₀_count mean 38.0417 ± 7.3468 (range 11–69). H₁_count mean 3.6058 ± 1.3429 (range 1–10).
  H₀_max_pers mean 2.7166, min 1.4800. H₂_count mean 0.0304, max 4.0.
- **Interpretation:** ring topology is sparse and tightly bounded — a mean of 3.6 loops per
  molecule with a hard ceiling of 10 — while connectivity varies almost fourfold across the
  library. That asymmetry is the mechanism behind the scaffold-paradox argument (L108): H₁ has
  little room to move under side-chain mutation, H₀ has a great deal.
- **Caveats:** one conformer per molecule, so H₂ in particular is conformer-dependent and its
  mean of 0.03 should not be read as a stable molecular property.
- **⚠ Conflict:** SM Table S2 carries H₀_count 38.0452, H₂_count max 2.0, H₀_max_pers min
  1.9857 — three values that contradict this file (audit-v3 C3, **open**). The main text's
  38.04 and 3.61 agree with this entry; the SM does not.
- **Claims:** Results §3.2; Conclusion; SM Table S2 (**blocked pending C3**).

## L106 — H₁ versus resistance-resilience score, with confounder adjustment

- **Method:** Spearman ρ on 77 compounds with both an RRS class (A/B/C/D) and a TFP.
  Partial correlation = Spearman on ranks followed by partial Pearson on ranks, controlling
  for **molecular weight, ring count, Fsp³, and H₀_count** (listwise, 0 dropped).
- **Source:** `results/p3_h1_rrs_correlation_final.{csv,txt}` (total),
  `results/p3_h1_rrs_partial_corr.{csv,txt}` (partial, run 2026-08-01).
- **Numbers:**

  | Predictor | ρ total | p | ρ partial | p | n |
  |---|---|---|---|---|---|
  | H₁_count | 0.3124 | 0.0057 | −0.0388 | 0.7447 | 77 |
  | H₁_entropy | 0.2544 | 0.0256 | −0.0698 | 0.5576 | 77 |
  | H₁_total_pers_sum | 0.3612 | 0.0013 | 0.0299 | 0.8018 | 77 |
  | H₁_total_pers_prod | 0.2627 | 0.0210 | 0.0305 | 0.7980 | 77 |
  | H₁_max_pers | 0.0674 | 0.5606 | 0.1881 | 0.1110 | 77 |

  Class composition: A = 46, B = 31, C = 0, D = 0, from 500 candidates.
- **Interpretation:** the H₁–resilience association does not survive adjustment. Every
  predictor that was significant on the whole sample collapses to |ρ| < 0.07 once size and
  shape are held fixed. H₁_count is a molecular-size proxy here, and the paper is right to
  say so. This closes the E-2 follow-up that the earlier tracking file listed as open.
- **Caveats:** n = 77, and classes C and D are empty, so this is an A-versus-B contrast
  dressed as a four-level score. Four confounders on 77 observations is a thin design;
  the null partial correlations are consistent with no effect but do not exclude a small one.
- **⚠ Manuscript mismatch:** see **L111** — the text asserts a second, MW-only adjustment
  that this run does not contain. Amended 2026-08-06 after independent review pass B.
- **Claims:** abstract cross-paper sentence; Results §3.6; Discussion limitation paragraph.

## L117 — Fair-fusion battery (S2) — SUPERSEDES L115

*The L115 conclusion ("complementarity refuted") was an artifact of the fusion method.
Corrected 2026-08-06.*

- **Method:** ECFP4 baseline against five fusions on identical random 5-fold splits,
  RF-200, seed 42, canonical panel. Stacking uses out-of-fold probabilities from a
  per-block RF (inner 3-fold) into a logistic meta-learner, so block width cannot
  distort it.
- **Source:** `results/p3_s2s3_refine.{csv,txt}`, `scripts/p3_s2s3_refine.py`.
- **Numbers:**

  | Fusion | AUC | SD | Δ vs ECFP4 | t | p |
  |---|---|---|---|---|---|
  | ECFP4 (baseline) | 0.9505 | 0.0055 | — | — | — |
  | **stacked** | **0.9502** | 0.0053 | **−0.0003** | −1.53 | **0.201 — n.s.** |
  | ECFP4+TFP only | 0.9322 | 0.0064 | −0.0183 | −14.40 | 1.4 × 10⁻⁴ |
  | naive concat | 0.9113 | 0.0085 | −0.0392 | −19.58 | 4.0 × 10⁻⁵ |
  | block-weighted | 0.9107 | 0.0090 | −0.0398 | −19.35 | 4.2 × 10⁻⁵ |
  | top-k per block | 0.9049 | 0.0069 | −0.0456 | −43.01 | 1.7 × 10⁻⁶ |

- **Interpretation:** the result is a clean null, not a negative. Every fusion that puts
  the blocks into one feature matrix loses 0.018–0.046 AUC, and the loss grows with how
  much of ECFP4's 2048 columns get displaced — the signature of feature dilution in a
  random forest, not of harmful information. Stacking, which gives each block its own
  model and combines only predictions, lands on top of the baseline: Δ = −0.0003,
  p = 0.20. TFP and TNE therefore carry **no predictive information beyond ECFP4** on
  this task, and they do not damage it either. The correct claim is "complementarity is
  absent", not "complementarity is refuted", and certainly not "these descriptors are
  complementary".
- **Why L115 was wrong:** it tested only naive concatenation and read the resulting drop
  as evidence about information content. Block-weighting and top-k selection — both
  intended as fairer — drop *further*, which confirms the mechanism is dilution rather
  than interference.
- **Caveats:** QKS still absent (no precomputed kernel matrix, O(N²) to rebuild), so the
  paper's actual TFP+TNE+QK hybrid was not tested against ECFP4. Stacking used a logistic
  meta-learner and 3 inner folds; a richer meta-learner might extract a small gain. df = 4
  on all paired tests, so the null is "no detectable difference", not proven equivalence.
- **Claims:** abstract; Discussion complementarity sentences; Conclusion.

## L118 — Stabilised scaffold-split estimate (S3) — REFINES L116

- **Method:** 10 × `GroupShuffleSplit` (20% held out), grouped on Bemis–Murcko scaffolds,
  RF-200, seed 42. Replaces the single deterministic `GroupKFold` partition of L116.
- **Source:** `results/p3_s2s3_refine.{csv,txt}`.
- **Scaffold structure:** **632** Bemis–Murcko scaffolds (L116 reported 629; the small
  difference is `GetScaffoldForMol` + canonical SMILES here versus `MurckoScaffoldSmiles`
  there). Generic, atom-type-stripped scaffolds: **324**.
- **Numbers (mean AUC, t-based 95% CI over 10 repeats):**

  | Descriptor | mean | SD | 95% CI |
  |---|---|---|---|
  | ECFP4 | 0.8392 | 0.0527 | [0.8015, 0.8769] |
  | ECFP4+TFP78+TNE | 0.7941 | 0.0835 | [0.7344, 0.8538] |
  | TFP-78 | 0.7437 | 0.0962 | [0.6749, 0.8126] |
  | TFP-12 | 0.6609 | 0.0671 | [0.6128, 0.7089] |
  | TNE | 0.6506 | 0.0713 | [0.5996, 0.7015] |

- **Interpretation:** the single-partition estimate held. ECFP4 falls from 0.9505 under
  random splitting to 0.8392 across scaffolds — a drop of 0.111, and the random-split
  value sits far outside the scaffold-split CI. The 324 generic scaffolds are the
  starker number: stripped of atom identity, ~20,000 molecules occupy only a few hundred
  distinct topological frameworks, so random folds are largely testing on near-duplicates.
  Descriptor ordering is unchanged, so the paper's comparative conclusions survive; every
  absolute AUC in it describes interpolation within analogue series.
- **Caveats:** CIs are wide (half-widths 0.024–0.069) because scaffold groups are very
  uneven — quote intervals, not point estimates. `GroupShuffleSplit` does not stratify, so
  class balance varies between repeats. Seed-scaffold overlap (the paper's 69.3% claim)
  could not be checked: the 850 seeds live in the companion Paper-1 project, not here.
  `[ADD: recompute 69.3% scaffold recovery against the seed set]`
- **Claims:** abstract split sentence; Results "Scaffold-aware evaluation"; Limitations.

## L114 — Which TFP is benchmarked (S1)

- **Method:** RF-200, 5-fold stratified CV, canonical panel (19,836 molecules,
  15,052 active / 4,784 inactive), seed 42. Three TFP variants evaluated side by side.
- **Source:** `results/p3_s1s3_benchmark.{csv,txt}`, `scripts/p3_s1s3_benchmark.py`, 2026-08-06.
- **Numbers (random split):**

  | Variant | dim | AUC | SD |
  |---|---|---|---|
  | TFP-12 — as the Methods define it | 12 | 0.8510 | 0.0104 |
  | TFP-33 — `H`-prefix, i.e. `--no-tfp-enriched` | 33 | 0.8710 | 0.0067 |
  | TFP-78 — enriched, the default and what was benchmarked | 78 | 0.8815 | 0.0066 |

- **Interpretation:** the published TFP number is not produced by the descriptor the Methods
  define. The Methods specify four summary statistics across three homology dimensions — 12
  features. The deposited code loads every `H`-prefixed column (33) and, because
  `--tfp-enriched` defaults to `True`, appends 25 persistence-image and 20 Betti-curve columns
  for 78. The gap between the defined and the benchmarked descriptor is ≈ 0.03 AUC. A reader
  implementing the Methods as written lands ~0.03 below the published value and cannot
  reproduce the paper.
- **Caveats:** this run is a replication, not a bit-exact reproduction — my ECFP4 gives 0.9505
  against the deposited 0.9475, so pipeline details differ (fold assignment, RDKit generator
  settings). Absolute values are therefore not directly comparable to L101; the *ordering* and
  the ~0.03 gap are the robust findings, and independent review pass C reached the same
  conclusion from a separate implementation (12-dim → 0.8473, 78-dim → 0.8759).
- **Consequence:** the Limitations sentence claiming the enriched TFP "showed no improvement
  over the 12-feature TFP baseline … consistent with the canonical full-library TFP AUC of
  0.876" is false on this panel in two ways — enrichment improves by ~0.03, and the canonical
  0.876 *is* the enriched number, not the 12-feature one.
- **Claims:** Methods §2.3.3 (main:159); Table 1 TFP row; Limitations (main:376).

## L115 — Complementarity with ECFP4 (S2) — REFUTED

- **Method:** as L114. Naive feature-level concatenation ECFP4 (2048) + TFP-78 + TNE (192)
  = 2318 features, against ECFP4 alone. Paired *t*-test across the 5 folds.
- **Source:** `results/p3_s1s3_benchmark.{csv,txt}`.
- **Numbers:**

  | Split | ECFP4 | ECFP4+TFP78+TNE | Δ | t | p |
  |---|---|---|---|---|---|
  | random | 0.9505 | 0.9113 | **−0.0392** | −19.58 | 4.0 × 10⁻⁵ |
  | scaffold | 0.8420 | 0.8092 | −0.0327 | −1.94 | 0.125 |

- **Interpretation:** the experiment the manuscript never ran does not support the manuscript.
  Adding the quantum-inspired descriptors to ECFP4 does not improve it — it makes it
  significantly worse under the random split, by roughly the margin the paper elsewhere treats
  as meaningful. The complementarity claim, repeated five times as the paper's fallback
  position, is refuted in the only direction that was testable here.
- **Caveats — and they matter:** this is *naive concatenation* into a random forest. Appending
  270 dense continuous features to 2048 sparse binary ones changes what `max_features` samples
  at each split, so part of the drop is dilution rather than absent information. A weighted
  fusion, a stacked ensemble, or per-block feature selection was **not** tested and could
  behave differently. The honest claim is therefore "naive concatenation does not help and
  measurably hurts", not "these descriptors carry no complementary information". Under the
  scaffold split the difference is not significant (p = 0.125), so the negative result is
  clearest exactly where leakage is largest.
- **Not tested:** QKS could not be included — no precomputed quantum-kernel feature matrix
  exists and recomputing it is O(N²) on 19,836 molecules. `[ADD: HPC run of ECFP4+TFP+TNE+QK]`
- **Claims:** abstract "effective complementary tools" (main:100, 388); Discussion (main:345,
  380); SM:595, 597 — **all blocked**.

## L116 — Scaffold-aware evaluation (S3)

- **Method:** as L114, repeated under `GroupKFold` on Bemis–Murcko scaffolds.
- **Source:** `results/p3_s1s3_benchmark.{csv,txt}`.
- **Scaffold structure:** 19,836 molecules collapse to **629 distinct Bemis–Murcko scaffolds**;
  the largest single scaffold holds 1,661 molecules (8.4% of the library), ~31 molecules per
  scaffold on average.
- **Numbers (random → scaffold):**

  | Descriptor | random | scaffold | drop |
  |---|---|---|---|
  | ECFP4 | 0.9505 | 0.8420 | −0.1085 |
  | TFP-78 | 0.8815 | 0.7465 | −0.1350 |
  | TFP-33 | 0.8710 | 0.7367 | −0.1343 |
  | TFP-12 | 0.8510 | 0.6740 | −0.1770 |
  | TNE | 0.7218 | 0.6301 | −0.0917 |
  | ECFP4+TFP78+TNE | 0.9113 | 0.8092 | −0.1021 |

  Mean drop across the six descriptors: **−0.1248**.
- **Interpretation:** every headline number in the paper is inflated by analogue leakage. With
  629 scaffolds behind 19,836 molecules, random 5-fold splitting places near-identical
  analogues on both sides of every fold — exactly what the paper's own 69.3% scaffold-recovery
  statistic predicts. The ECFP4 headline falls from 0.95 to 0.84. The descriptor *ranking* is
  preserved, so the paper's central comparative conclusion survives; its absolute performance
  claims do not. The topological descriptors degrade more than ECFP4 (TFP-12 worst at −0.177),
  which is the opposite of the paper's suggestion that TFP captures scaffold-level features
  that generalise beyond atom-level similarity.
- **Caveats:** `GroupKFold` does not stratify, so class balance varies across folds and the
  scaffold-split SDs are 3–9× larger than the random-split ones. The single largest scaffold
  group (8.4%) dominates whichever fold holds it. These are honest properties of the split,
  not defects, but they widen the uncertainty on every scaffold-split number.
- **Claims:** every AUC in the abstract, Table 1, Table 2 and Conclusion needs either a
  scaffold-split companion value or an explicit statement that the numbers are random-split.

## L113 — Phase-2 hyperparameter re-benchmark

- **Method:** the three leading Phase-1 configurations re-benchmarked at n = 5,000 under the
  canonical 5-fold protocol.
- **Source:** `results/p3_phase2_bd6_nr1_nk30_raw.csv`, `..._nr6_nk30_raw.csv`,
  `..._nr6_nk20_raw.csv` (one row each: `bond_dim,n_repeats,n_kpca,auc,auc_std,time_s`).
- **Numbers (read directly from the deposited rows):**

  | d | r | k | AUC | SD |
  |---|---|---|---|---|
  | 6 | 1 | 30 | **0.8283** | 0.0371 |
  | 6 | 6 | 30 | 0.8121 | 0.0396 |
  | 6 | 6 | 20 | 0.8047 | 0.0354 |

- **Interpretation:** the selected configuration wins by 0.016 AUC over the runner-up, and the
  ordering is driven by the repeat count — one IQPEmbedding repeat beats six at both KPCA
  widths. More circuit repetition buys nothing here, which is consistent with L103's finding
  that the quantum kernel's extra label alignment does not convert into predictive gain.
- **Caveats:** one row per configuration, so the reported SD is the across-fold SD of a single
  run and the three configurations were not compared by a paired test. Only three of the
  Phase-1 grid's configurations were carried forward, and the selection that produced them is
  not deposited — see below.
- **⚠ Phase-1 gap:** the manuscript describes a 60-combination Phase-1 grid at n = 200. No
  deposited file contains it: `p3_quantum_params_sweep.csv` holds a single row (d=6, r=1, k=30,
  AUC 0.8283 — a copy of the Phase-2 winner, not a Phase-1 sweep). The previously printed
  Phase-1 value 0.8534 ± 0.0490 traces only to a comment in
  `scripts/p3_phase2_array.sbatch:9`, and the ± 0.0490 to nothing at all. Both were therefore
  **removed** from the manuscript on 2026-08-06 and replaced with an `[ADD]` placeholder; the
  grid is now described as protocol only, with no undeposited AUC quoted.
- **Claims:** Methods §2.6 (main:219, restored 2026-08-06).

## L112 — MW-only partial correlation — REPRODUCED, now deposited

*Supersedes L111, which was wrong. 2026-08-06.*

- **Method:** identical loading path, inputs and rank-based partial-correlation implementation
  as L106, with the covariate set reduced to molecular weight alone. New script
  `scripts/p3_h1_rrs_mw_only.py`, written this session because no script in the repository
  computed a covariate subset (`p3_h1_rrs_partial_corr.py:91` hard-codes all four).
- **Source:** `results/p3_h1_rrs_mw_only.{txt,csv}`, generated 2026-08-06, n = 77.
- **Numbers:**

  | Predictor | ρ total | p | ρ partial (MW only) | p | n |
  |---|---|---|---|---|---|
  | H₁_count | 0.3124 | 0.0057 | −0.0219 | **0.8507** | 77 |
  | H₁_entropy | 0.2544 | 0.0256 | −0.1064 | 0.3603 | 77 |
  | H₁_total_pers_prod | 0.2627 | 0.0210 | 0.0697 | 0.5495 | 77 |
  | H₁_total_pers_sum | 0.3612 | 0.0013 | 0.0533 | 0.6477 | 77 |
  | H₁_max_pers | 0.0674 | 0.5606 | 0.2021 | 0.0801 | 77 |

  Ancillary: Spearman H₁_count vs molecular weight **ρ = 0.7183**, p = 1.92 × 10⁻¹³, n = 77.
- **Verdict on the manuscript's claim:** **correct.** The text's "p = 0.85" matches 0.8507 and
  "ρ = 0.718" matches 0.7183. The defect was provenance, not accuracy — the analysis had been
  run at some point but its output was never deposited and no repository script reproduced it.
  That is now fixed: script and outputs exist.
- **Interpretation:** molecular weight alone accounts for the whole H₁_count–resilience
  association. Adding ring count, Fsp³ and H₀_count (L106) changes the partial correlation
  only from −0.022 to −0.039, so the three extra covariates add nothing once size is held
  fixed. The manuscript is entitled to state the MW-only result as the cleaner claim, and the
  four-covariate model as a robustness check.
- **Caveats:** n = 77 with RRS classes C and D empty (L106). ρ = 0.718 between H₁_count and MW
  is high enough that the two are near-collinear in this cohort, which is itself the finding.
- **Correction to the record:** independent review pass B reported this as a statistic from an
  analysis that was never run, and L111 accepted that. Reproduction falsified it. Pass B was
  right that nothing in the repository produced the number, and wrong that the number was
  unsupported.
- **Claims:** abstract; Results §3.6 (main:361); Limitations (main:376); SM:639 — all **cleared**.

## L111 — The MW-only partial correlation (p = 0.85) — SUPERSEDED BY L112

> **This entry was wrong.** It concluded the analysis had never been run. L112 reproduces
> the claimed values exactly. Retained unedited below as a record of the error; read L112.

### L111 (superseded) — original text

*Raised by independent review pass B, 2026-08-06; verified here before acceptance.*

- **Claimed in manuscript:** "controlling for molecular weight alone collapses the
  correlation to ρ_partial ≈ 0 (p = 0.85)" — main lines 361 and 376, plus the SM, five
  occurrences in total.
- **What the code does:** `scripts/p3_h1_rrs_partial_corr.py:91` hard-codes
  `confounders = ["MW", "n_rings", "Fsp3", "H0_count"]`. One model, four covariates, no
  MW-only branch, no loop over covariate subsets.
- **What the outputs contain:** `grep '0\.85'` across `results/p3_h1_rrs_partial_corr.*`
  returns nothing. The only deposited partial correlation for H₁_count is
  ρ = −0.0388, p = 0.7447 (L106).
- **Status:** **CRITICAL, open.** This is not an imprecise description of an analysis that
  was run — it is a reported statistic from an analysis that was not run. Under hard rule 3
  it cannot stay in the manuscript in any form.
- **Note on internal inconsistency:** main line 361 reports *both* the phantom MW-only
  result (p = 0.85) *and* the real four-covariate result (p = 0.745), presenting them as two
  analyses. Line 376 (Limitations) and the abstract quote only the phantom one. So the
  Limitations paragraph — the section a reviewer reads for the paper's honesty — rests
  entirely on the number that does not exist.
- **Resolution, either:** (a) delete every MW-only claim and quote only the deposited
  four-covariate result; or (b) actually run the MW-only model, deposit it, and quote the
  value it returns. (a) is cheaper and loses nothing: the four-covariate result already
  supports the conclusion the paper draws.
- **Also unverified in the same sentence:** "H₁ count correlates strongly with molecular
  weight (ρ = 0.718)" — `[CITATION NEEDED — deposited file]`, not found in this session.
- **Claims:** abstract (**blocked**); Results §3.6 (**blocked**); Limitations (**blocked**).

## L107 — Pilot H₁–RRS correlation (n = 14) — UNTRACED

- **Claimed in manuscript:** "pilot n = 14: ρ = 0.947, p < 0.0001" (abstract, V2608 line 100).
- **Source:** **none found.** `grep '0\.947'` across `results/` returns only ECFP4 AUC
  0.9475 rows. `p3_h1_rrs_correlation_final.txt` documents the n = 77 analysis and does not
  mention a 14-compound pilot. No pilot RRS file exists (`*_pilot*` files are TDA/TNE only).
- **Status:** `[CITATION NEEDED — deposited file or script]`. The number cannot enter the
  manuscript under hard rule 3 until a file reproduces it.
- **Note:** the superseded `_V2` V2607 text qualified this as "on H₁ total persistence";
  V2608 dropped the qualifier, so the two versions describe different quantities. Whichever
  is correct, one of them was wrong in print.
- **Claims:** abstract (**blocked**).

## L119 — Provenance of 92.6% / 69.3% — RESOLVED, and MISATTRIBUTED in the manuscript

*Supersedes the "source unknown" status of L108. Traced in `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
v51 (repo parent, the authoritative values file), 2026-08-06.*

- **92.6%** — BMAD_Q1 §exec-summary line 25 and §1.2: the **ECFP4-unreachable fraction**
  (whole-molecule Tanimoto < 0.4) measured on **5,000 generated molecules + 396 seeds**.
- **69.3%** — BMAD_Q1 §1.3 line 110, verbatim: *"Scaffold recovery rate: 69.3%
  (70/101 seed scaffolds recovered in the library of 20,702)."* It is the fraction of
  **seed scaffolds that reappear**, over 101 seed scaffolds, in a **20,702**-molecule library.
- **Both are P1 quantities**, from the companion chemical-space study, computed on datasets
  that are not the P3 panel. BMAD_Q1's own Bemis–Murcko table is for the **65,856**-molecule
  P1 library.
- **The misattribution:** the P3 manuscript presented these two figures as properties of its
  own **19,836**-molecule panel, and used them to motivate the scaffold-paradox framing. Four
  different denominators are in play — 5,396 / 20,702 / 65,856 / 19,836 — and none of the
  first three is the panel being benchmarked. Corrected 2026-08-06: the scaffold-redundancy
  argument now rests on a measurement made **on the P3 panel itself** (632 Murcko / 324
  generic scaffolds, L118), and the P1 figures are cited as companion results rather than
  restated as local ones.
- **Independent cross-check that did hold:** BMAD_Q1 §1.3 gives benzene as the top scaffold at
  **8.41%** of 65,856. My measurement on the P3 panel gives the largest scaffold at
  **8.4%** of 19,836 (1,661 molecules). The two agree, which supports the panel being a
  representative subset of the parent library.
- **Note for future audits:** in v51 the manuscript-ready claims live in **§5.3**, not §4.3.
- **Claims:** abstract opening; Introduction N6; Results scaffold paragraph; Limitations.

## L120 — ECFP4-augmented hybrid: NOT in the authoritative record

- **Checked:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` v51 for any fusion of ECFP4 with the
  quantum-inspired descriptors.
- **Result:** none. Every hybrid in the authoritative record is TFP+TNE+QK **without** ECFP4
  — canonical full-library `Hybrid RF AUC 0.8876 ± 0.0065` (job 12699, n = 19,836) and the
  n = 5,000 pre-phase `0.8423 ± 0.0076` (jobs 12651→12660). No ECFP4-augmented row exists at
  any sample size.
- **Consequence:** the S2 gap is real and remains open. The stacking null (L117) covers
  ECFP4 + TFP + TNE; the paper's actual three-component hybrid including QKS has never been
  tested against ECFP4, here or in the authoritative record.
  `[ADD: HPC run of ECFP4 + TFP + TNE + QK vs ECFP4]`
- **Also confirmed absent from v51:** any scaffold-split or `GroupKFold` analysis. The
  report's "leakage" entries (M1, ~line 1891) concern transductive **UMAP** leakage in
  `p3_hybrid_benchmark.py:820-824`, which inflated job 12696 by ~+0.05 (that 0.8968 result is
  excluded). Different problem — L116/L118 do not duplicate it.
- **Claims:** none directly; bounds what S2 can assert.

## L108 — Scaffold paradox: 92.6% / 69.3% — SUPERSEDED BY L119

- **Claimed in manuscript:** 92.6% Tanimoto distinction versus 69.3% Bemis–Murcko scaffold
  recovery; scaffold-only Tanimoto 0.379 = 1.84× whole-molecule 0.206.
- **Source:** not produced by this project. These are companion-paper quantities
  (`temgoua2026antimalarial`). No file under `results/` computes them; substring matches on
  `0.926` / `0.693` are coincidental hits inside unrelated float columns.
- **Status:** admissible **only** as a cited external result. Requires a page/table pointer
  into the companion paper, not a bare citation, since the whole framing of the paper rests
  on this pair of numbers.
- **Claims:** abstract opening; Introduction N6; Results §3.7; Figure 3 caption; Conclusion.

## L109 — TDA versus multi-target promiscuity — CONTRADICTED

- **Claimed in manuscript (V2608 line 325):** N = 17,011; H₀_count ρ = −0.248,
  H₀_entropy ρ = −0.243, H₁_entropy ρ = −0.190, all p < 10⁻¹³⁷.
- **Deposited file:** `results/p3_tartarus_tda_spearman.csv` gives **N = 19,900** and
  H₀_max_pers −0.1670, H₁_entropy −0.16115, H₀_count −0.15864, H₀_entropy −0.15302
  (p between 10⁻¹²⁴ and 10⁻¹⁰⁴).
- **Status:** **CRITICAL, open.** Two different analyses, and only the one the manuscript
  does *not* cite is deposited. The magnitudes differ by ~0.09 in ρ and the sample sizes by
  2,889 molecules. A reviewer who resolves the Zenodo DOI finds the contradiction immediately.
- **Interpretation (of the deposited analysis):** the sign is stable and the effect is real
  but small — |ρ| ≈ 0.16 on ~20,000 molecules is a highly significant, weakly predictive
  association. The manuscript's "highly significant correlations" is defensible; the
  mechanistic story it hangs on them ("optimal conformational adaptability") is not supported
  by a correlation of this size and should be softened regardless of which N wins.
- **Resolution required:** either recompute at N = 19,900 and update main + SM + Figure S6,
  or deposit the N = 17,011 pipeline and its CSV. Audit-v3 recommends the former.
- **Claims:** Results §3.7 (**blocked**); SM §15.2 (**blocked**).

## L110 — Scalability extrapolation — DEFECTIVE SOURCE

- **Source:** `results/p3_scalability_results.csv`, single row:
  `n=40, pairs=820, load_time_s=0.14, umap_time_s=11.93, kernel_time_s=6.41,
  psd_time_s=0.0, total_time_s=6.41, pairs_per_s=128.0`.
- **Defects:** (a) C(40,2) = **780**, not 820 — the pair count is wrong, which makes
  `pairs_per_s` wrong; (b) `total_time_s` = 6.41 excludes the 11.93 s UMAP step, so the
  true total is 18.34 s and any throughput extrapolation built on 6.41 s understates cost
  by ~3×.
- **Status:** **CRITICAL, open** (audit-v3 C2). The main text's runtime claims
  ("under 15 minutes", 6.4 min TDA, 8.1 min TNE) are sourced from L104/L105 and are *not*
  affected. The SM's O(N²) extrapolation is.
- **Resolution:** fix the script's pair count and total, rerun, or drop the extrapolation and
  quote only the measured canonical runtimes from L104/L105.
- **Claims:** SM §9 (**blocked**); main §4.4 runtime sentence (**clear**, sourced from L104/L105).

---

## L121 — H₁ versus resistance-resilience, n = 494 cohort — SUPERSEDES L106 AND L112

*Written 2026-08-08. Both L106 and L112 document the **n = 77** cohort. The manuscript
reports **n = 494**. The n = 494 outputs existed only in the sibling folder
`Project3_Quantum_Inspired_RepresentationsV2607` and had never been pulled into this
worktree, so this project could not reproduce its own headline correlation. Fixed here.*

- **Why the cohort changed:** `scripts/p3_rrs_expansion.py` pre-filtered on ≥1 bound target
  (`has_binding`) and then took the first 500, but the RRS calculation requires ≥2 targets
  (`MIN_TARGETS=2`), so most of those 500 were mono-target and only 77 survived. The n = 77
  ceiling was a sampling artefact, not a library constraint: the Tartarus pool holds **2051**
  compounds with ≥2 targets at ΔG ≤ −7.0 kcal/mol. The 2026-08-05 fix pre-filters on ≥2
  targets and samples from those 2051 (BMAD_Q1 §3.9 correction note, line 1770).
- **Method:** Spearman ρ on the compounds carrying both an RRS class and a TFP. Partial
  correlation = Spearman on ranks followed by partial Pearson on ranks. Two covariate sets:
  molecular weight alone, and the four-confounder set (MW, ring count, Fsp³, H₀_count).
  Listwise, 0 dropped.
- **Source:** `results/p3_h1_rrs_correlation_final.{csv,txt}` (run 2026-08-05, jobs 12816 +
  TFP 12826), `results/p3_h1_rrs_partial_corr.{csv,txt}` (2026-08-05),
  `results/p3_h1_rrs_mw_only.{csv,txt}` (**regenerated 2026-08-08 on this cohort** — the
  MW-only model had never been deposited at n = 494). Authoritative cross-check:
  `BMAD_Q1_DATA_ANALYSIS_REPORT.md:1770`. The superseded n = 77 files are preserved under
  `results/superseded_n77/`.
- **Numbers (n = 494; Class A = 295, B = 199; C and D empty):**

  | Predictor | ρ total | p | ρ partial, MW only | p | ρ partial, 4 covariates | p |
  |---|---|---|---|---|---|---|
  | H₁_count | 0.2399 | 6.76 × 10⁻⁸ | **−0.0180** | **0.6903** | **+0.0329** | 0.4668 |
  | H₁_entropy | 0.2338 | 1.46 × 10⁻⁷ | −0.0707 | 0.1170 | −0.0020 | 0.9642 |
  | H₁_total_pers_sum | 0.2361 | 1.09 × 10⁻⁷ | −0.0312 | 0.4891 | +0.0164 | 0.7168 |
  | H₁_total_pers_prod | 0.1638 | 2.56 × 10⁻⁴ | −0.0084 | 0.8521 | +0.0046 | 0.9194 |
  | H₁_max_pers | −0.0173 | 0.7009 | +0.0005 | 0.9906 | +0.0016 | 0.9715 |

  Ancillary: Spearman H₁_count vs molecular weight **ρ = 0.5042**, p = 3.23 × 10⁻³³, n = 494.
- **Interpretation:** the association is real on the whole sample and vanishes under
  adjustment, exactly as at n = 77, so the six-fold larger cohort does not rescue it.
  Controlling for molecular weight alone is sufficient to collapse it; adding ring count,
  Fsp³ and H₀_count moves the partial correlation from −0.018 to +0.033, which is noise
  around zero. H₁_count is a molecular-size proxy in this cohort and the manuscript is
  correct to say so. Two quantities weaken relative to n = 77 and the text must not imply
  otherwise: the whole-sample ρ falls 0.312 → 0.240, and the H₁_count–MW collinearity falls
  0.718 → 0.504, so size explains the association less tightly here while still explaining
  it away.
- **Verdict on the manuscript:** the six sites quoting ρ_partial = −0.018, p = 0.69 (main
  l.100, l.363, l.370, l.378; SM l.104, l.639) are **correct and now sourced**. Reproduction
  on 2026-08-08 returned −0.0180 / 0.6903 and 0.5042, matching the text to its printed
  precision. The defect was provenance, not accuracy — the same failure mode as L112, one
  cohort later.
- **Caveats:** Classes C and D remain empty at n = 494, so this is still an A-versus-B
  contrast presented as a four-level score; that limitation is unchanged by the larger n and
  is a library property, not a sampling artefact. Null partial correlations at n = 494
  exclude effects down to roughly |ρ| ≈ 0.13 at 80 % power, which is tighter than n = 77
  allowed but still not proof of exact zero.
- **Claims:** abstract cross-paper sentence; Results §3.6; Discussion limitation paragraph;
  SM §3.9 companion text.

---

## L122 — RRS Class A discriminability from TDA features — NEW

*Co-author result, produced 2026-08-05, pulled into this worktree 2026-08-08. Not previously
in the ledger and not yet in the manuscript.*

- **Method:** binary classification of RRS Class A (resistance-resilient, RRS ≥ 8.0) versus
  non-A from topological features. Random Forest, 500 trees, `class_weight='balanced'`,
  5-fold cross-validation.
- **Scope:** 2051 compounds with ≥2 targets bound at ΔG ≤ −7.0 kcal/mol; 961 Class A,
  1090 non-A.
- **Source:** `scripts/p3_resistance_benchmark.py`,
  `results/p3_resistance_benchmark.csv`, `results/p3_resistance_benchmark_summary.txt`.
  Cross-check: `BMAD_Q1_DATA_ANALYSIS_REPORT.md`, Appendix I (Resistance Benchmark).
- **Numbers:**

  | Feature set | Features | AUC ± std |
  |---|---|---|
  | H₁+H₀ | 22 | **0.8749 ± 0.0134** |
  | Persistence images | 25 | 0.8648 ± 0.0080 |
  | H₀ statistics | 11 | 0.8492 ± 0.0200 |
  | H₁ statistics | 11 | 0.8366 ± 0.0118 |
  | Betti curves | 20 | 0.8195 ± 0.0123 |

- **Interpretation:** the qualitative Class A/non-A split is well predicted by topology
  (AUC 0.82–0.87) in the same compound pool where the continuous H₁–RRS correlation is
  entirely explained by molecular size (L121). The two results are not in tension, and the
  asymmetry is the point: a size confound can flatten a rank correlation while leaving a
  class boundary learnable, because the classifier is free to use 22 features non-linearly
  rather than one feature monotonically. The ordering across feature sets is also
  informative — combining H₁ and H₀ beats either alone (+0.026 over H₁ statistics, +0.038
  over H₀ statistics), and Betti curves trail persistence statistics by 0.055, matching the
  same ranking seen in the activity benchmark (L105, SM Table S12).
- **Caveats, and they are load-bearing:** (a) no molecular-size baseline was run, so the
  headline claim this result *appears* to support — that topology carries resilience signal
  beyond size — is **not yet established**; a Random Forest on MW alone, or on MW plus ring
  count, is the control that decides it, and it does not exist. Given L121, that control is
  mandatory before any manuscript sentence contrasts this AUC with the collapsed
  correlation. (b) The Class A threshold RRS ≥ 8.0 is not derived in any deposited document;
  it needs a stated justification or the split reads as chosen. (c) No comparison against an
  ECFP4 baseline on the same 2051 compounds, so "topology predicts resilience" cannot be
  weighed against "any descriptor predicts resilience". (d) 5-fold CV is random, not
  scaffold-split, so the estimate is optimistic relative to the scaffold-aware protocol used
  elsewhere in this paper (L116, L118) — a like-for-like number would be lower.
- **Status:** **admissible as a deposited result; NOT admissible for the interpretive claim**
  until the size baseline (a) exists. Drafting the Discussion sentence BMAD proposes
  ("distinct qualitative discriminative signal") requires (a) at minimum.
- **Claims:** none yet. Candidate: Discussion, resilience paragraph; SM new table.

---

## L123 — Molecular-size control for RRS Class A — DISCHARGES L122 CAVEAT (a), AND CORRECTS L122's AUC

*Run 2026-08-08. L122 recorded a co-author result but blocked its interpretation: without a
size baseline, an AUC of 0.875 could not be distinguished from "molecular weight predicts
docking affinity", which is what L121 shows the continuous correlation reduces to.*

- **Method:** same cohort, same label, same classifier and fold seed as L122
  (RF 500 trees, `class_weight='balanced'`, stratified 5-fold, `random_state=42`).
  Three arms over identical folds, so the arms are fold-paired: **size** (MW, ring count,
  heavy-atom count, Fsp³), **H1+H0** (the 22 topological features), **H1+H0+size**.
  Significance by paired t-test across the 5 shared folds.
- **One protocol change from L122, and it matters:** the scaler is fitted on the training
  fold and applied to the test fold. `p3_resistance_benchmark.py:65-66` fits a *separate*
  `StandardScaler` on the test fold, which is the same train/test scaling mismatch the
  manuscript reports having fixed as C3 in the QKS benchmark (L103).
- **Source:** `scripts/p3_resistance_size_baseline.py`,
  `results/p3_resistance_size_baseline.{csv,txt}` (per-fold AUCs deposited in the CSV).
- **Numbers (n = 2051; Class A = 961, non-A = 1090):**

  | Arm | Features | AUC ± std | vs size (ΔAUC) | paired t | p |
  |---|---|---|---|---|---|
  | H1+H0+size | 26 | **0.8989 ± 0.0104** | +0.0313 | 6.445 | 0.0030 |
  | H1+H0 | 22 | **0.8937 ± 0.0119** | +0.0260 | 6.429 | 0.0030 |
  | size | 4 | 0.8677 ± 0.0184 | — | — | — |

- **Correction to L122:** the published H1+H0 figure of **0.8749** is an artefact of the
  test-fold scaler. Re-run with the scaler fitted on train folds only, the same features on
  the same folds give **0.8937**, i.e. the mismatch was *costing* 0.019 AUC rather than
  inflating it. The deposited 0.8749 is therefore pessimistic, not optimistic, but it is
  still wrong and must not be quoted. Use 0.8937 (L123). The four other feature sets in L122
  (`pers_img`, `H0_stats`, `H1_stats`, `betti`) carry the same defect and have **not** been
  re-run; none of them may be quoted until they are.
- **Interpretation:** four plain size descriptors already reach AUC 0.868, so most of what
  looked like a topological result is molecular size — consistent with L121, and the reason
  the control was mandatory. Topology nonetheless adds a real increment: +0.026 AUC over
  size alone, consistent in sign across all five folds (paired p = 0.0030). Adding size on
  top of topology buys only a further +0.005, so the topological features already encode
  nearly all the size information and then a little more. The honest statement is that
  topology contributes a small but reproducible discriminative signal beyond molecular
  size — not that resilience is a topological phenomenon.
- **Contrast with L121, stated carefully:** the continuous H₁–RRS correlation collapses
  entirely under MW adjustment while this class boundary retains signal after a size
  baseline. That asymmetry is defensible because a 22-feature non-linear classifier and a
  single-feature rank correlation are not the same test, and it is the strongest form in
  which the resilience result can be put. It is not evidence that the correlation was real.
- **Caveats:** (a) the paired t-test uses 5 CV folds, which share training data and are not
  independent, so p = 0.0030 overstates confidence — it establishes consistency of sign, not
  a population-level effect; a repeated-CV or scaffold-split design would be the honest
  significance test. (b) Folds are random, not scaffold-split, so all three arms are
  optimistic relative to L116/L118 protocol; the *comparison* between arms is fair since the
  bias applies equally. (c) The Class A threshold RRS ≥ 8.0 remains underived (L122 caveat b),
  and RRS is itself a function of the docking scores, so this predicts computed affinity,
  not measured resistance — the same limitation the manuscript already states for activity
  labels. (d) No ECFP4 arm (L122 caveat c) — still open, so "topology beats size" is
  established but "topology is the right descriptor here" is not.
- **Status:** **admissible.** L122 caveat (a) discharged; caveats (b), (c), (d) stand.
- **Claims:** Discussion resilience paragraph; SM resistance-benchmark table.

---

## L124 — ECFP4 arm and protocol reconciliation — SUPERSEDES L123 FOR ALL QUOTED VALUES

*Run 2026-08-08 on author instruction: quote the co-author's published value, and add the
ECFP4 baseline only if BMAD_Q1 lacked it. BMAD_Q1 Appendix I reports the five TDA feature
sets and no classical arm, so ECFP4 was computed.*

- **Method:** as L123, with two additions. (i) A **2048-bit ECFP4** arm (Morgan radius 2).
  (ii) Every arm evaluated under **both** scaling protocols: `published`, which reproduces
  `p3_resistance_benchmark.py` by standardising the test fold with its own statistics, and
  `corrected`, which fits the scaler on training folds only. Arms are only comparable within
  a protocol; shared fold assignment (`random_state=42`) makes them fold-paired.
- **Source:** `scripts/p3_resistance_size_baseline.py`,
  `results/p3_resistance_size_baseline.{csv,txt}` (both protocols, per-fold AUCs in the CSV).
- **Numbers:**

  | Arm | Features | AUC (published) | AUC (corrected) |
  |---|---|---|---|
  | ECFP4 | 2048 | **0.9186 ± 0.0123** | 0.9188 ± 0.0121 |
  | H₁+H₀ + size | 26 | 0.8858 ± 0.0148 | 0.8989 ± 0.0104 |
  | H₁+H₀ | 22 | **0.8755 ± 0.0157** | 0.8937 ± 0.0119 |
  | size | 4 | 0.8436 ± 0.0224 | 0.8677 ± 0.0184 |

  Fold-paired tests, published protocol: H₁+H₀ vs size ΔAUC **+0.0319** (t = 5.595,
  p = 0.0050); H₁+H₀+size vs size +0.0422 (t = 8.395, p = 0.0011); ECFP4 vs size +0.0751
  (t = 7.946, p = 0.0014); **H₁+H₀ vs ECFP4 −0.0432** (t = −6.423, p = 0.0030).
- **Protocol identification confirmed:** under `published`, H₁+H₀ returns **0.8755** against
  the co-author's deposited **0.8749** — agreement to 0.0006, which is fold-level rounding.
  This settles L123's open question: the 0.019 gap was entirely the test-fold scaler, and the
  published protocol is now reproducible from a script in this repository.
- **Decision on which values the manuscript quotes:** the **published** protocol, per author
  instruction, so the manuscript is consistent with the co-author's deposited number. L123's
  `corrected` figures are retained here as the sensitivity analysis and are reported in one
  SM sentence. **L123's numbers must no longer be quoted as headline values.**
- **Interpretation:** the ECFP4 arm changes the claim materially, and in the paper's favour
  as an honest negative. Topology beats plain size by +0.032 (p = 0.0050), so persistent
  homology does encode resilience-relevant structure beyond molecular bulk — L122 caveat (a)
  stays discharged. But ECFP4 beats topology by 0.043 (p = 0.0030), so topology is *not* the
  preferable representation here. This reproduces the ordering of the activity benchmark
  (L101: ECFP4 0.948, TFP 0.876) on an independent task and endpoint, which strengthens the
  paper's central honest-negative rather than weakening it. The size arm being weakest
  (0.844) also rules out the reading that the whole benchmark is a molecular-weight proxy.
- **Caveats:** all four L123 caveats stand — non-independent folds, random rather than
  scaffold splits, an underived RRS ≥ 8.0 threshold, and RRS being a function of the docking
  scores rather than measured resistance. L122 caveat (c) is now **discharged** by the ECFP4
  arm. The conclusions are protocol-insensitive: switching to `corrected` raises all four
  arms and preserves the ordering and every significant comparison.
- **Claims:** Discussion resilience paragraph (main); SM §Resistance-resilience
  classification, `SM-tab:resistance_benchmark`.

---

## L125 — Decomposition of the topological block; BMAD Appendix I reproduced

*Run 2026-08-08. Closes the last item left open by L123/L124: the four single-family feature
sets in `p3_resistance_benchmark.py` had been published under the test-fold scaler and never
re-evaluated, so they were unquotable.*

- **Method:** as L124 — same 2051-compound cohort, same label, same folds
  (`random_state=42`), both scaling protocols — with the four single-family arms added:
  H₁ statistics (11), H₀ statistics (11), persistence images (25), Betti curves (20).
- **Source:** `scripts/p3_resistance_size_baseline.py`,
  `results/p3_resistance_size_baseline.{csv,txt}` (8 arms × 2 protocols, per-fold AUCs in CSV).
- **Reproduction of BMAD_Q1 Appendix I** (published protocol):

  | Set | BMAD Appendix I | This run | Δ |
  |---|---|---|---|
  | H₁+H₀ | 0.8749 | 0.8755 | 0.0006 |
  | pers_img | 0.8648 | 0.8655 | 0.0007 |
  | H0_stats | 0.8492 | 0.8488 | 0.0004 |
  | H1_stats | 0.8366 | 0.8367 | 0.0001 |
  | betti | 0.8195 | 0.8183 | 0.0012 |

  All five agree to ≤ 0.0012. Appendix I is now reproducible from a repository script, and
  the L122 restriction ("none of them may be quoted until re-run") is **lifted**.
- **Numbers vs the size baseline (published protocol, fold-paired):**

  | Arm | AUC | ΔAUC vs size | t | p |
  |---|---|---|---|---|
  | Persistence images | 0.8655 ± 0.0071 | +0.0219 | +2.516 | 0.0656 |
  | H₀ statistics | 0.8488 ± 0.0186 | +0.0052 | +0.879 | 0.4292 |
  | *size baseline* | 0.8436 ± 0.0224 | — | — | — |
  | H₁ statistics | 0.8367 ± 0.0117 | −0.0068 | −0.789 | 0.4741 |
  | Betti curves | 0.8183 ± 0.0142 | −0.0253 | −1.736 | 0.1576 |

  Also: Betti curves vs H₁+H₀ ΔAUC = −0.0572 (t = −6.129, p = 0.0036); persistence images
  vs H₁+H₀ −0.0100 (p = 0.1733).
- **Interpretation:** none of the four single-family sets beats four plain size descriptors
  at the 0.05 level, and two sit numerically below them. Only the joint H₁+H₀ block clears
  the size baseline (L124, +0.032, p = 0.0050). The resilience signal therefore belongs to
  the *combination* of connected-component and cycle statistics, not to persistence images,
  Betti curves, or either homology dimension alone. This is a decomposition result, not a
  new positive one, and it is reported as such: it constrains the attribution of the L124
  claim and pre-empts the obvious reviewer question about which features carry the effect.
  The ordering also matches what these descriptors show for activity prediction (L105,
  `SM-tab:sota`), so the two tasks agree.
- **Protocol-dependent result, flagged in the SM:** H₀ statistics is the only arm whose
  verdict flips — +0.0052 (p = 0.4292) published, +0.0179 (p = 0.0262) corrected. Its status
  is unresolved and it is claimed in neither direction. Every other arm keeps its verdict
  across protocols.
- **Caveats:** all L124 caveats stand unchanged (non-independent folds, random rather than
  scaffold splits, underived RRS ≥ 8.0 threshold, RRS a function of the docking scores).
- **Claims:** SM §Resistance-resilience classification — decomposition paragraph and the four
  added rows of `SM-tab:resistance_benchmark`. **No main-text claim**; the main-text statement
  (topology > size, ECFP4 > topology) is unaffected.

---

## Gate status (L1)

| Gate | Result |
|---|---|
| Ledger currency (all entries dated ≥ manuscript base) | PASS |
| Missing-interpretation check | PASS — 10/10 entries interpreted |
| Unlinked-claim check | FAIL — L107, L108 unsourced; L109, L110 contradicted |
| Every matrix row names an entry ID | pending `claims-evidence-matrix.md` rebuild |

**L1 gate: FAIL.** Four blockers: L107 (untraced pilot), L108 (external, needs precise
citation), L109 (contradicted, CRITICAL), L110 (defective source, CRITICAL).
