# P1 Adversarial Audit, Rejection Root-Cause Analysis & Deep Scientific Refinements
**Project:** `Project1_Chem_space_antimalarial_V7_CorrectedGrid` (Chemical Space Exploration, Polypharmacology & Resistance Resilience)
**Revision:** rev 2.1 — 16 October 2026. rev 2: addendum folded into the body, retracted targets and refuted claims removed, evidence pinning added. rev 2.1: **§7 "wow" factor** (the referee-facing contribution) added; no other section renumbered in meaning, the former §7 (limits) is now §8.

## Audit pin

| Field | Value |
|---|---|
| Repository | `/home/nanaengo/Malaria_codesV2` (canonical single tree, `AGENTS.md` §0) |
| Branch / commit audited | `master` @ `1c9c38f2ec572d92f03073f765b6cd11b9b062a6` (2026-10-16T12:21:31+01:00) |
| Path convention | repo-relative only; no absolute `file://` links |
| Evidence rule | every factual claim carries either a repository path **with sha256** or a DOI/accession. A claim without one is marked `UNVERIFIED` |
| Auditor frameworks | BMAD multi-layer review (`bmad-code-review`), Scientific Critical Thinking, Hypothesis Generation, Experimental Design, Peer Review |
| Rejection context | Refused by *Journal of Chemical Information and Modeling* (JCIM) — initial review and 16 Sept 2026 resubmission refusal |

**Superseded in rev 2 (do not re-assert):** the "retained MTX causes the DEKOIS failure" root cause; the `1J3I` PfDHFR attribution; the `(26.66, 42.19, 39.89)` grid centre and the "0.00 Å" MTX coincidence; the `16.7–19.5 Å` PfCRT residue-76 displacement as current state; the `ρ = +0.515` correlation as the corrected value; the `AUC > 0.75` / `EF@1% > 5.0` rescue targets; the "Gabrani 2024" and "Tang 2025" citations.

**Key literature anchors (verified this revision):**
- Kim, Tan, Wicht et al., *Nature* **576**, 315–320 (2019) — PfCRT; PDB `6UKJ` is annotated `Plasmodium falciparum (isolate 7G8)` (RCSB REST, checked 16 Oct 2026).
- Hany et al., *Drug Des. Devel. Ther.* **19** (2025), DOI 10.2147/DDDT.S537065 — DEKOIS 2.0 on WT and quadruple-mutant PfDHFR with ML rescoring; `EF1% = 28.41` (WT, PLANTS+CNN) and `EF1% = 31.02` (Q, FRED+CNN); ML rescoring moved AutoDock Vina "from worse-than-random to better-than-random" (Europe PMC full text, PMC12363558).
- Gómez-Bombarelli et al., *ACS Cent. Sci.* **4**, 268–276 (2018); Nigam et al., *Chem. Sci.* **12**, 7079–7090 (2021) (STONED/SELFIES).
- Eberhardt et al., *JCIM* **61**, 3891–3898 (2021) — **AutoDock Vina 1.2.0** (not GNINA; GNINA is McNutt et al. 2021).

---

## 1. Executive summary & audit scorecard

Project 1 combines two studies in one manuscript: (1) generative expansion of 396 African Natural Products (ANPs) and 454 synthetic antimalarials into a 65,856-compound library compressed into 484 VAE centroids, and (2) a 17-compound multi-target, mutant-aware Resistance Resilience Score (RRS) docking analysis (Set C).

Re-auditing against the canonical artifacts at the pinned commit changes the scorecard materially: two of the five items originally rated 🔴 CRITICAL describe states that the project has already corrected, and one of them rests on a hypothesis the project has already tested and rejected.

| Audit layer | Status | Essential finding (evidence) |
|---|:---:|---|
| **1a. DEKOIS null result — causal attribution** | ✅ **REFUTED** | The MTX-blockade hypothesis was **tested and rejected** by the two-arm experiment at `results/dekois_mtxstripped_20260909/` (2026-09-09, `JOB_COMPLETE`, sha256 `f4a908b3…` / `0e668e76…`): retained receptor AUC **0.5023** [0.4225, 0.5862], `EF@1%` **0.00**; MTX-stripped AUC **0.5626** [0.4772, 0.6463], `EF@1%` **0.00**; ΔAUC +0.060 with overlapping bootstrap CIs. `P1_DATA_ANALYSIS_REPORT.md` §R2.4 (sha256 `b5d4745c…`): *"removing MTX does not restore enrichment … the near-chance DEKOIS result is attributable to the single-method Vina scoring function and grid positioning (near the NADPH site), not to steric blockade"*. |
| **1b. PfCRT structural identity & grid** | ✅ **FIXED (R2.3)** | Original defect was real: `6UKJ` is the 7G8 (K76T) isoform, so it cannot serve as the wild-type denominator. Corrected run exists: `results/pfcrt_redock_v2grid_20260909/` (status `COMPUTED`, sha256 `ca1c7cd3…`) uses a *"corrected 3D7-like wild-type (LYS-76), 6UKJ frame"* with a cavity-anchored V2 grid (centre 152.99, 151.042, 159.379; 25 Å) and *"residue 76 CA 11.2 Å from center"*. |
| **2. RRS batch confounding** | 🟠 **PARTLY FIXED** | A self-mutation null control is implemented in the corrected run (`NULL` receptor = WT through the mutation script; `rrs_null_pfcrt` mean 100.0, range [99.4, 100.5]; `max_abs_deviation_mutant_vs_null` K76T 1.2, K76A 0.51). The same null is **not yet** computed for the PfDHFR mutation states. |
| **3. Cohort duplication with P2** | 🔴 **OPEN (editorial)** | The 17-molecule cohort is shared: `Project7_.../data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv` (sha256 `b7d7c859…`) carries `cohort_id = P2_SET_C_POLYPHARM_17`, IDs `PP-01…PP-17`, and a single `p2_source_sha256`. Naming differs across projects ("P1 Set A" = "P2 Set C"). |
| **4. Construct validity of cross-target cutoffs** | 🟠 **PARTLY ADDRESSED** | The corrected run reports per-target medians (`nfav_per_target_medians`: PfDHFR −5.921, PfCRT −8.056, PfClpP −6.016, PfATP4 −6.378) and PfCRT class counts (`A* = 7, B = 4, C = 6`), but the universal −6.0 kcal/mol rule is not yet replaced by a per-target empirical quantile throughout. |
| **5. Generative chemistry & centroid compression** | 🟡 **OPEN** | `Chiral-STONED` stereocontrol, a low-rank DPP compression path, and the active-retention curve `R(K)` remain to be built. Single-seed docking remains a limitation. |

---

## 2. Diagnosis (revised against the canonical artifacts)

### 2.1 The DEKOIS failure: what it is, and what it is not
The honest-negative result stands: on DEKOIS 2.0 for PfDHFR the pipeline is near chance (AUC ≈ 0.45–0.50; `EF@1% = 0.00`). What must not be repeated is the original causal story.

- The retained-receptor arm reproduces the published baseline (0.5023 at exhaustiveness 32 vs the published 0.450 at exhaustiveness 64; DAR §R2.4).
- Stripping MTX raises AUC by 0.060 with overlapping CIs and leaves `EF@1% = 0.00`. The improvement is inside the noise band implied by 40 actives.
- The DAR's own conclusion — single-method Vina scoring plus grid placement near the NADPH site — is therefore the supported explanation, and it is also the explanation that Hany et al. (2025) corroborate from the other direction: on the same targets, **rescoring**, not receptor surgery, moved Vina from worse-than-random to better-than-random.

**Consequence for the manuscript:** the DEKOIS section should be presented as a bounded protocol-sensitivity study (two arms, identical pipeline, one variable), not as a validated benchmark that can be rescued by a receptor fix.

### 2.2 Enrichment metrics at this panel size are noise-dominated
The project's own bootstrap interval quantifies the problem: AUC 0.5023 [0.4225, 0.5862] with 40 actives and 1199 decoys — a half-width of ~0.08. `EF@1%` is computed from the top ~12 of 1240 ranked compounds. At this panel size the sampling variance of any early-enrichment statistic exceeds any effect a docking pipeline could plausibly produce. "40 actives" — not "MTX" — is the binding constraint on this benchmark.

### 2.3 PfCRT: the anatomy was right, the state is now corrected
`6UKJ` is the chloroquine-resistant 7G8 isoform carrying T76 (verified against the RCSB entry and its annotated source organism). Using it unchanged as the "wild-type" denominator was a genuine defect. It is now corrected by construction: a 3D7-like LYS-76 receptor derived on the 6UKJ frame, re-docked with K76T, K76A and a `NULL` control under one protocol.

**Residual gap.** The gate is currently stated as *"residue 76 CA 11.2 Å from center"*. In a 25 Å box the half-edge is 12.5 Å, so the CA is inside with ~1.3 Å of margin and the CB sits near the boundary. Report the **maximum distance of any residue-76 atom from the box centre** (and the fraction of the residue inside), not the CA alone. This is a one-line change that closes an obvious reviewer attack.

### 2.4 Uncontrolled preparation batch effects in RRS
The algebra behind the original concern is sound:
$$\Delta G_{\text{mut}} - \Delta G_{\text{WT}} = \underbrace{(\Delta G_{\text{mut}}^{\text{pipe2}} - \Delta G_{\text{WT}}^{\text{pipe2}})}_{\text{true mutation signal}} + \underbrace{(\Delta G_{\text{WT}}^{\text{pipe2}} - \Delta G_{\text{WT}}^{\text{pipe1}})}_{\text{confounding batch offset}}$$
The corrected PfCRT run addresses it empirically: the `NULL` control (WT through the mutant-preparation pipeline) gives `RRS_null ∈ [99.4, 100.5]`, so mutant deviations can be expressed against a measured noise band rather than against an assumed 100 %. Apply the same control to the PfDHFR states before any PfDHFR RRS is interpreted.

### 2.5 Statistical power and the reported correlations
At n = 17 (12 complete two-target candidates) a two-sided Spearman test at Bonferroni α = 0.017 has only ~37 % power to detect |ρ| = 0.50. A non-significant result is therefore **not** evidence of independence; state it as "not detectable at this n" and support independence only with a pre-declared equivalence margin and a TOST/ROPE decision.

The correlation values themselves must be taken from the corrected artifacts, not from the superseded tables: `results/pfcrt_redock_v2grid_20260909/revision_summary.json` (sha256 `14f8197e…`) reports `nfav_rrs_spearman` **ρ = 0.7137, p = 0.0013** (100 000-permutation p = 0.00192). The corrected run also revises the class counts from `A* = 6, B = 5, C = 5, D = 1` to `A* = 7, B = 4, C = 6`, with mean-RRS range 73.2–115.6. Where the manuscript still quotes `ρ = +0.515` or the old class counts, they are stale.

---

## 3. Novelty assessment and refinements

rev 1 numbering is retained for continuity: rev 1 *Novelty 1* (Chiral-STONED) → §3.2; *Novelty 2* (compression + active-retention) → §3.3; *Novelty 3* (receptor standardisation and rescoring) → §3.1 (already implemented) + §3.5 (rescoring, open); *Novelty 4* (null-calibrated RRS and target-relative polypharmacology) → §3.1 and §3.4.

The pipeline as published —
$$\text{seeds} \xrightarrow{\text{STONED-SELFIES}} 65\text{k library} \xrightarrow{\text{VAE} + k\text{-means}} 484\ \text{centroids} \xrightarrow{\text{Vina}} \text{top hits}$$
— remains an incremental application of 2018–2021 tools. Three refinements remain genuinely open; two items previously listed as "novelty" are already implemented and are restated here as *completed infrastructure*.

### 3.1 Already implemented (restate, do not re-propose)
1. **Corrected PfCRT receptor and cavity-anchored grid** (R2.3) — see §2.3. Remaining work: the residue-76 max-atom-distance gate.
2. **Self-mutation null control (`NULL`)** and **per-target score medians** — see §2.4 and the scorecard row 4. Remaining work: extend the null to PfDHFR states; complete the per-target empirical-quantile replacement of the −6.0 kcal/mol rule.

### 3.2 Open novelty 1 — stereochemically and topologically locked generative expansion (`Chiral-STONED`)
**Gap.** ANPs from NANPDB/EANPDB are defined by conserved polycyclic cores and dense stereochemistry; unconstrained STONED-SELFIES mutates the whole SELFIES string and can break bridged/fused rings and stereocentres.

**Proposal.** Decompose each seed into a Bemis–Murcko/`H₁` core with frozen CIP (R/S) stereocentres and mutable peripheral attachment vectors; restrict token mutations to the periphery; gate on CIP invariance and synthetic accessibility.

**Bounded claim.** This is a **library-coverage** intervention. Docking scores are only weakly stereodiscriminating, so any claim that the pipeline discriminates enantiomers requires an explicit enantiomer-pair control; without it, claim coverage, not stereoselectivity.

### 3.3 Open novelty 2 — principled library compression with a measured active-retention curve
**Gap.** A "99.3 % cost reduction" from docking 484 centroids instead of 65,856 molecules says nothing about retained actives.

**Proposal.**
1. Compare (a) VAE k-means, (b) MaxMin Tanimoto sphere exclusion, (c) k-DPP over a joint 2D + 3D kernel.
2. Implement the DPP as a **low-rank/Nyström** or greedy log-determinant selection: an exact DPP over 65,856 molecules implies a dense 65,856² kernel (~35 GB in float64) plus an eigendecomposition, and must be reported with its approximation.
3. Verify kernel PSD-ness when 2D and 3D terms are combined; clip negative eigenvalues if needed.
4. Measure the **active-retention curve** `R(K)` for `K ∈ {100, 250, 484, 1000, 2500}` using spiked validated actives (ChEMBL/MMV), with scaffold-cluster bootstrap CIs.

### 3.4 Open novelty 3 — calibrated RRS and target-relative polypharmacology
1. Extend the `NULL` self-mutation control to PfDHFR; define mutant susceptibility as a **Z-score against the empirical null band** rather than fixed 70 %/80 % cutoffs.
2. Replace the universal −6.0 kcal/mol cutoff with **per-target empirical quantiles** estimated from a common decoy background per target, so cross-target breadth is invariant to pocket size and baseline offset.
3. Enforce cohort separation from P2 by stereo-aware InChIKey **and** Murcko scaffold, and declare any overlap in both manuscripts.

### 3.5 Open novelty 4 — physics/ML rescoring as the actionable lever (restored from rev 1)
**Gap.** The DEKOIS null result is a scoring-function result (§2.1). Hany et al. (2025) show, on the same two PfDHFR targets, that **rescoring** rather than receptor surgery moves AutoDock Vina from worse-than-random to better-than-random, reaching `EF1% = 28.41` (WT) and `31.02` (quadruple mutant).

**Proposal.** Re-run DEKOIS 2.0 on the PfDHFR WT and mutant states across three scoring tiers — (i) AutoDock Vina, (ii) a 3D-CNN rescoring tier (`GNINA` `CNNscore`/`CNNaffinity`; GNINA 1.3 is current), (iii) RF-Score-VS — with all tiers sharing one ligand-preparation and grid protocol, and the Hany et al. range used as a **reference band, not a promise**. Run all docking across M = 5 seeds and report mean ± SD.

**Bound.** The Hany comparison sets expectations, not targets: no enrichment value is pre-claimed (see §4 action 9 and G3).

### 3.6 Statistical and benchmarking discipline (new)
- Pre-register the enrichment metric set: BEDROC(α = 20), `EF@5%` and a bias-corrected enrichment estimator, each with a scaffold-cluster bootstrap CI. Traditional `EF` is known to misestimate true enrichment.
- Run a **panel-size/power simulation before docking** (actives 40 → 400 at fixed decoy ratio) and either size the panel so a pre-declared effect is detectable, or label the benchmark descriptive and underpowered.
- Put primary docking-validity evidence on **pose recovery**: crystallographic redocking RMSD per control ligand (pyrimethamine, cycloguanil, WR99210 on PfDHFR; chloroquine/piperaquine on PfCRT), reported per ligand with poses — not a single "RMSD < 2.0 Å all targets" line.
- Multi-seed docking (M = 5 seeds) with mean ± SD remains appropriate as an uncertainty statement.

---

## 4. Action plan

| # | Action | Resolves | Deliverable | Gate |
|---|---|---|---|---|
| 1 | Rewrite the DEKOIS section around the completed two-arm experiment; cite the DAR §R2.4 conclusion; remove the receptor-fix causal claim | Refuted root cause | Manuscript §2.3.1 / §4.5 + SM §S12.2 | Text contains no causal MTX claim; two-arm table present with CIs |
| 2 | Report the residue-76 max-atom distance (and inside-fraction) for every PfCRT state | Residual receptor gap | Box-coordinate table | Max-atom distance < half-edge for all states, else box re-centred |
| 3 | Replace `EF@1%`-based claims with the pre-registered metric set; run the panel-size simulation | Noise-dominated metric | Metric table + power figure | Pre-registration committed before the docking run |
| 4 | Extend the `NULL` self-mutation control to PfDHFR; restate RRS classes against the measured null band | Batch confounding | Null-calibrated RRS table | Every class assignment reproducible from the null band |
| 5 | Replace the −6.0 kcal/mol rule with per-target empirical quantiles | Construct validity | `eCDF-PNS` definition + table | Breadth metric invariant to per-target score offset |
| 6 | Enforce and declare P1/P2 cohort separation | Salami-slicing risk | Disjointness table (InChIKey + Murcko) | Zero undeclared overlap |
| 7 | Update all correlation and class-count numbers to the corrected run (ρ = 0.7137; `A* = 7, B = 4, C = 6`) | Stale statistics | Revised tables | Values match `revision_summary.json` |
| 8 | Replace the two unlocatable citations with sourced evidence on representation robustness under distribution shift | Citation integrity | Two sourced references | Both resolve to a DOI/arXiv record |
| 9 | Remove the `AUC > 0.75` / `EF@1% > 5.0` targets from all text and response letters | Retracted target | — | No pre-claimed enrichment value anywhere |

---

## 5. Verification ledger (claim → evidence)

| Claim | Status | Evidence |
|---|---|---|
| `6UKJ` = PfCRT 7G8 isoform (T76) | ✅ Verified | RCSB entry + FASTA, checked 16 Oct 2026; Kim et al., *Nature* 576, 315–320 (2019) |
| DEKOIS MTX-blockade explains the null result | ❌ **Refuted** | `zenodo_package_P1/results/dekois_mtxstripped_20260909/summary.txt` (sha256 `f4a908b3…`); DAR §R2.4 (sha256 `b5d4745c…`) |
| Grid centre co-located with MTX (0.00 Å) | ❌ **False as recorded** | Recorded centre (1.33, −1.733, −23.842) vs MTX CoM (7.44, 0.57, −29.74), ≈ 8.9 Å — `scripts/p1_r24_dekois_mtxstripped.py` (sha256 `01f22bbf…`) |
| `1J3I` contains MTX | ❌ **False** | PDBe molecule inventory for `1J3I` = HOH, NDP, UMP, WRA; the retained DEKOIS arm used `7F3Y.pdbqt` |
| Corrected 3D7-like PfCRT WT + cavity grid + NULL control exist | ✅ Verified | `results/pfcrt_redock_v2grid_20260909/manifest.json` (sha256 `ca1c7cd3…`) |
| `ρ(N_fav, RRS)` corrected value | ✅ Verified | `revision_summary.json` (sha256 `14f8197e…`): ρ 0.7137, p 0.0013, permutation p 0.00192 |
| P1/P2/P7 cohort identity | ✅ Verified | `Project7_.../data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv` (sha256 `b7d7c859…`) |
| Hany et al. 2025 rescoring outcome | ✅ Verified | Europe PMC full text PMC12363558 (DOI 10.2147/DDDT.S537065) |
| BEDROC / early-recognition metric critique | ✅ Verified (rev 2.1) | Truchon & Bayly, *JCIM* **47**, 488–508 (2007), DOI 10.1021/ci600426e (Europe PMC 17288412) |
| "Gabrani et al. JCAMD 2024" | 🚫 Not locatable | Two literature searches; removed from this document |
| "Tang et al. Nature ML 2025 (fingerprint paradox)" | 🚫 Not locatable | Two literature searches; removed from this document |
| `AUC > 0.75` / `EF@1% > 5.0` after receptor repair | ⏹ Withdrawn target | No measurement supports it; withdrawn per the pre-registration rule |

---

## 6. Acceptance gates (executable)

| Gate | Criterion |
|---|---|
| G1 Receptor integrity | No unintended co-crystal ligand in any PDBQT; for every PfCRT state, report the maximum residue-76 atom distance from the box centre and the inside-fraction |
| G2 Prep symmetry | WT and mutants produced by one script/hash; prep-log diff empty apart from the mutation |
| G3 Benchmark | Pre-registered metric set (BEDROC(20), EF@5 %, bias-corrected EF) with scaffold-cluster bootstrap CIs, on a panel whose active count was chosen by a documented power simulation |
| G4 Null | PfCRT **and** PfDHFR mutant deviations reported against the measured `RRS_null` band; inside the band ⇒ reported as indistinguishable from noise |
| G5 Disjointness | P1 ∩ P2 cohorts empty by stereo-aware InChIKey and by Murcko scaffold |
| G6 Citation integrity | Every citation resolves to a DOI/arXiv record fetched and dated in §5 |
| G7 Claim pinning | The manuscript states the commit at which each numerical claim was produced |

---

## 7. The "wow" factor — what should make a referee or editor say *waouh*

**The one line.**

> Every resistance score in this study is quoted in units of a **measured null band**, the breadth axis is defined by per-target empirical quantiles instead of a universal kcal/mol cutoff, and the one benchmark that fails is shipped as a **two-arm, one-variable, hash-pinned experiment** that reproduces the published baseline in its control arm.

### 7.1 Why it lands

Editors remember *measurements*, not adjectives, and referees attack *uncalibrated* numbers. Three properties do the work here, and all three already exist in the tree at the pinned commit:

1. **Calibration.** The corrected PfCRT re-dock ships a `NULL` control (wild type passed through the mutant-preparation script) whose spread *is* the score's noise floor: `rrs_null_pfcrt` mean **100.0**, range **[99.4, 100.5]**, with mutant deviations of 1.2 (K76T) and 0.51 (K76A) percentage points. A resistance score with a measured 0.5 pp noise floor is a different scientific object from the same score without one.
2. **A coupling that survives confounder adjustment.** `N_fav`–`RRS` Spearman ρ = **0.7137** (p = 0.0013; 100 000-permutation p = **0.00192**), and on the n = 12 complete-two-target subset, conditioning on molecular weight and Murcko-scaffold prevalence *strengthens* the association (partial ρ = **−0.6154** vs raw **−0.2098**). Reproducible sentence for the abstract: *resistance resilience is not promiscuity re-labelled.*
3. **A negative result delivered as evidence.** The two-arm DEKOIS experiment (retained vs MTX-stripped receptor, one variable changed) returns ΔAUC +0.060 with overlapping bootstrap CIs and `EF@1 %` = 0.00 **in both arms**, while the retained arm reproduces the published baseline (0.5023 at exhaustiveness 32 vs the published 0.450 at exhaustiveness 64). That is a protocol-sensitivity *result* — most groups would have buried it.

### 7.2 Wow at a glance

| Element | Value | Evidence |
|---|---|---|
| Measured null band (PfCRT) | mean 100.0, range [99.4, 100.5]; max deviation K76T 1.2, K76A 0.51 pp | `zenodo_package_P1/results/pfcrt_redock_v2grid_20260909/revision_summary.json` (sha256 `14f8197e…`) |
| Coupling | ρ = 0.7137, p = 0.0013, permutation p = 0.00192 | same |
| Confounder-adjusted coupling | partial ρ = −0.6154 vs raw −0.2098 (n = 12; MW + Murcko prevalence) | `zenodo_package_P1/P1_DATA_ANALYSIS_REPORT.md` §R2.1 (sha256 `b5d4745c…`) |
| Controlled negative | retained **0.5023** [0.4225, 0.5862] vs stripped **0.5626** [0.4772, 0.6463]; `EF@1 %` 0.00 in both arms | `zenodo_package_P1/results/dekois_mtxstripped_20260909/summary.txt` (sha256 `f4a908b3…`) |
| Internal replication | retained arm at exhaustiveness 32 reproduces the published exhaustiveness-64 baseline 0.450 [0.367, 0.531] | same |
| Chemical-space contrast | 92.6 % of the 65 856-molecule library ECFP4-unreachable; 69.3 % NP Murcko cores retained | DAR §1 (sha256 `b5d4745c…`) |
| Pose recovery | crystallographic redocking RMSD 1.23–1.78 Å across the four targets | `zenodo_package_P1/P1_V8_PACKAGE_AUDIT_20260909.md` §R2.8 (sha256 `65372a20…`) |
| Corrected class structure | `A* = 7`, `B = 4`, `C = 6`; mean-RRS range 73.2–115.6 | `revision_summary.json` (sha256 `14f8197e…`) |

### 7.3 The artifact that carries it — one figure

**Figure R**, three panels:

- **A.** The 17 candidates in (null-calibrated RRS Z-score, per-target-empirical-quantile breadth) space, with the measured `NULL` envelope drawn as a shaded band and the corrected classes labelled.
- **B.** The two-arm DEKOIS CIs on a single axis, both `EF@1 %`/`EF@5 %` values annotated, the published baseline marked as a reference point.
- **C.** The three cross-metric correlations with their permutation distributions and the partial-ρ re-estimate.

Caption line: *"Resistance resilience is reported in units of a measured null; the enrichment failure is reported as a one-variable experiment."*

### 7.4 The decisive, cheap experiments

| # | Action | Cost | Gate |
|---|---|---|---|
| W1 | Extend the `NULL` self-mutation control to the five PfDHFR states (WT→WT*, N51I, C59R, S108N, I164L) | ≈ 5 dockings under the existing protocol, no new protocol | `RRS_null` width reported per state; mutants inside the band are reported as **noise**, not as classes |
| W2 | Replace the −6.0 kcal/mol rule with per-target empirical quantiles from a common decoy background | analysis only | Breadth metric invariant to per-target score offset |
| W3 | Pre-register the enrichment metric set: BEDROC(α = 20) and `EF@5 %`, scaffold-cluster bootstrap CIs | analysis only | Pre-registration committed *before* any docking run; `EF@1 %` at 40 actives is a top-12 statistic (Truchon & Bayly, *JCIM* **47**, 488–508 (2007), DOI 10.1021/ci600426e) |
| W4 | Multi-seed docking (M = 5) with mean ± SD | ≈ 5× the docking budget | Every score carries an SD |
| W5 | Verify that `PNS`–`RRS` (ρ = −0.714) and `N_fav`–`RRS` (ρ = +0.714) are not near-complementary **by definition** before both are presented as independent cross-metric associations | 1 hour | Only non-redundant associations are claimed as independent evidence |

### 7.5 The controls that make it credible

The `NULL` self-mutation band; identical pipeline across the two DEKOIS arms; reproduction of a published baseline inside the control arm; per-target quantiles instead of a universal cutoff; and the honest statement that a non-significant correlation at n = 17 is *not detectable*, not *absent* (a pre-declared SESOI with a TOST/ROPE decision).

### 7.6 What must not be claimed

- No pre-claimed enrichment value (`AUC > 0.75`, `EF@1 % > 5.0` are withdrawn — see §2.1).
- No stereoselectivity from docking scores; `Chiral-STONED` claims *library coverage*, not enantiomer discrimination.
- No universal −6.0 kcal/mol cutoff.
- No independence claim from a failed rejection.

### 7.7 What would falsify it

If the PfDHFR `NULL` band turns out wide (say ≥ 5 pp), the per-mutant classification is not resolvable with this protocol and the primary table must be demoted to "within-noise" — which is precisely why W1 is the first experiment, not the last.

### 7.8 Cover-letter line (for the editor)

> "Our resistance-resilience estimates are reported against a measured WT→WT* null band rather than an assumed 100 %, and our one null benchmark is reported as a controlled two-arm experiment in which the control reproduces the published baseline."

---

## 8. Limits of this audit

- No docking run was re-executed. Numbers are read from the artifacts listed in §5 (each with a sha256) at the pinned commit.
- Pose-recovery RMSD, MMV/DEKOIS decoy sets and the 484-centroid library were not re-derived.
- The two structural-identity checks (`6UKJ` source organism, `1J3I` ligand inventory) were performed against RCSB/PDBe on 16 Oct 2026 and are accession-based, not reproducible from the repository alone.
- The claim that "rescoring, not receptor surgery, is the actionable lever" is supported by the project's own two-arm experiment plus Hany et al. (2025); it is a bounded statement about these two targets, not a general claim about docking.
