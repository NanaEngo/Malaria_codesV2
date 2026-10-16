# P5 Adversarial Audit, Rejection Root-Cause Analysis & Deep Scientific Refinements
**Project:** `Project5_GNN_Transformer_DrugDiscovery_V2609` (GNN/Transformer Out-of-Distribution Generalization, 1-WL Topological Bottleneck & Conformal Triage)
**Revision:** rev 2.1 — 16 October 2026. rev 2: addendum folded into the body, retracted targets and unlocatable citations removed, evidence pinning added. rev 2.1: **§6 "wow" factor** (the referee-facing contribution) added; the former §6 (limits) is now §7.

## Audit pin

| Field | Value |
|---|---|
| Repository | `/home/nanaengo/Malaria_codesV2` (canonical single tree, `AGENTS.md` §0) |
| Branch / commit audited | `master` @ `1c9c38f2ec572d92f03073f765b6cd11b9b062a6` (2026-10-16T12:21:31+01:00) |
| Path convention | repo-relative only; no absolute `file://` links |
| Evidence rule | every factual claim carries a repository path **with sha256** or a DOI. A claim without one is `UNVERIFIED` |
| Auditor frameworks | BMAD multi-layer review (`bmad-code-review`), Scientific Critical Thinking, Hypothesis Generation, Experimental Design, Peer Review |

**Superseded in rev 2 (do not re-assert):** the citations "Gabrani et al., *JCAMD* 2024" and "Tang et al., *Nature Machine Intelligence* 2025 (fingerprint paradox)" (not locatable); "Alvarsson et al., *JCIM* 2023 — exact 90 % Mondrian coverage on ChEMBL actives" (not locatable as stated); the "Surrogate-Oracle Bias **theorem**" framing (a hypothesis with a measurable index until proven); the target "coverage-by-decile curve **proving** exact 90 % class-conditional coverage under OOD shift"; and the reading of `eos80ch` labels as a single "malaria activity" class.

**Key literature anchors (verification status in §5):**
- Bodnar et al., *NeurIPS* 34, 2625–2640 (2021) — CW networks / cellular message passing. Not re-verified in this revision.
- Tibshirani et al., *NeurIPS* 32, 2530–2540 (2019) — conformal prediction under covariate shift (assumes covariate shift and an estimated density ratio). Not re-verified.
- Tursunbadalov & Tursunbadalov, arXiv:2607.06605 (2026) — marginal conformal prediction under-covers the minority class; class-conditional fix (verified).
- Arvidsson McShane et al., *J. Cheminform.* (2024), DOI 10.1186/s13321-024-00870-9 — CPSign (verified).
- Wee & Jiang, *J. Chem. Inf. Model.* **65**(23), 12691–12706 (2025), DOI 10.1021/acs.jcim.5c02266 — TDA/topological deep learning review (verified).
- van Heerden, Turon, Duran-Frigola, Pillay, Birkholtz, *ACS Omega* **8**(46), 43813–43826 (2023), DOI 10.1021/acsomega.3c05664 — the `eos80ch` model family (verified).

---

## 1. Executive summary & audit scorecard

Project 5 benchmarks `GIN`, topological descriptor fusion (`GIN-TFP`, `GIN-TNE`) and `ChemBERTa` against `ECFP4-RF` on a 19,836-compound antimalarial panel under random, Bemis–Murcko scaffold and Butina splits, plus a transfer test on 22,267 disjoint ChEMBL 34 compounds.

| Audit layer | Status | Essential finding (evidence) |
|---|:---:|---|
| **1. Construct validity of the label oracle (`eos80ch`)** | 🔴 **OPEN** | Primary labels derive from Ersilia `eos80ch`, whose model family was trained on asexual-blood-stage (126,374) and sexual/gametocyte (93,941) screening data to recognise **stage-specific** activity (van Heerden et al. 2023). Repo documentation declares only "Ersilia eos80ch computational predictions … threshold 0.5" (`Project3_.../V2609/PLACEHOLDER_COMPLETION_GUIDE.md`, `SUBMISSION_READY.md`) without stating the stage semantics. The "malaria activity" construct is therefore under-specified in the manuscripts that use it (P3, P5, P7). |
| **2. "1-WL bottleneck" versus readout-only concatenation** | 🔴 **OPEN** | `GIN-TFP` concatenates a global persistence vector at the MLP readout (`[h_G ‖ TFP]`); message passing stays strictly 1-WL. The experiment therefore does not test higher-order topological message passing, and the `+0.0091` AUC bump (0.8047 → 0.8138) is not evidence for a fixed bottleneck. |
| **3. Heuristic triage routing labelled "conformal"** | 🔴 **OPEN** | The rule (`d_NN < 0.40` / `0.40–0.60` / `ECE > 0.08`) has no non-conformity scores, no prediction sets and no finite-sample `1−α` guarantee, and the thresholds were chosen after inspecting test deciles. Two additional failure modes apply to any repair: importance-weight collapse under scaffold splits, and the fact that covariate-shift validity does **not** cover label shift. |
| **4. Inferential power and subgroup sizes** | 🟠 **OPEN** | Primary paired tests use n = 5 per-seed means. Exact sign-flip tests at n = 5 have a **two-sided floor of 2/2⁵ = 0.0625** (one-sided 1/2⁵ = 0.03125), which fails any FDR control of the sort claimed. The "3D + polycyclic" subgroup contains n = 79 molecules. |
| **5. Literature positioning** | 🟡 **PARTIALLY CLOSED** | The claim that classical fingerprints match or beat standard GNNs/transformers on 20k tabular bioactivity data repeats a well-established consensus. Two of the citations used to support it could not be located and have been removed; the honest-negative scaffold result must stay. |

---

## 2. Diagnosis

### 2.1 The surrogate-oracle confounder, stated precisely
The panel's binary labels derive from a **classical fingerprint model**. Three consequences follow, in increasing order of what they require:

1. **Alignment by construction.** If the teacher is a function of 2D circular fingerprint features, a student whose input space is that same feature space has maximal mutual information with the label by construction; students using other structure (global graph paths, 3D geometry, SMILES syntax) pay an *alignment penalty*.
2. **The penalty must be measured, not asserted.** Sweep fingerprint radius and bit length, and fingerprint family (Morgan radius 1–3, MACCS, RDKit-FP), and report how the ECFP-student advantage moves. If the advantage collapses when the teacher's fingerprint parameters are matched, the alignment explanation is quantitative; if it persists, something else is operating.
3. **A "theorem" is not available.** Until proven, treat this as a **hypothesis** evaluated through a measurable alignment index.

**Label semantics travel with the claim.** The verified lineage of `eos80ch` is stage-specific antimalarial activity (asexual blood stage versus gametocyte), so "active" most likely means "stage-classified active" rather than "antiplasmodial". Confirm which output column and polarity the P5 pipeline binarised at threshold 0.5, and either rewrite the construct definition accordingly or replace the label source.

### 2.2 What the `GIN-TFP` architecture can and cannot show
`GIN-TFP` runs the same 1-WL `GINConv` stack as `GIN` and appends a global persistence vector at the readout. Atoms inside fused polycycles still receive identical 1-WL neighbourhood messages; nothing in the *message-passing hierarchy* changes. A causal test of the bottleneck requires a genuinely higher-order layer (§3.2), and any claimed gain requires a capacity-matched, budget-matched comparison.

### 2.3 Conformal triage: from heuristic to guaranteed
The current router is a post-hoc heuristic. A defensible replacement has to state its assumption and survive two specific failure modes:

- **Importance-weight collapse.** Scaffold splits produce near-disjoint support, so the test-to-calibration density ratio is extreme or undefined. Report the **effective sample size** `ESS = (Σw)²/Σw²`, clip/stabilise weights, and fall back to unweighted split-conformal below a **pre-declared** ESS floor.
- **Mondrian × weighting.** Class-conditional validity under weighting requires per-class weights, and **label shift is not covered** by a covariate-shift guarantee. Choose one assumption and state it: covariate shift (weighted) or class-conditional calibration (Mondrian), or a label-shift construction if the shift is in the class proportions.

**Coverage is marginal, not per-molecule.** Report empirical coverage per scaffold-family bin and per class, and claim only what those bins show.

### 2.4 Statistical unit
Two errors co-exist in the current design: testing n = 5 seed means (the wrong unit, and a test whose exact floor is 0.0625 two-sided), and treating 25 fold–seed records as independent (pseudo-replication). The independent biological unit of generalization is the **held-out Bemis–Murcko scaffold cluster**. Because every molecule receives an out-of-fold prediction, inference can be done at that level directly.

### 2.5 Cohort and label independence from the rest of the programme
The 17-molecule cohort shared with P1/P2 (`Project7_.../data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv`, sha256 `b7d7c859…`, `cohort_id = P2_SET_C_POLYPHARM_17`) creates overlap that must be declared. The 22,267-compound ChEMBL panel must be deduplicated against the surrogate panel by stereo-aware InChIKey, with scaffold overlap reported, and its heterogeneous assays/thresholds fixed by a **pre-declared activity rule** before any model score is examined.

---

## 3. Refinements

rev 1 numbering retained for continuity: rev 1 *Novelty 1* (surrogate-oracle / dual-oracle benchmark) → §3.1; *Novelty 2* (`CW-GIN` higher-order ring message passing) → §3.2; *Novelty 3* (rigorous conformal routing) → §3.3; *Novelty 4* (scaffold-clustered inference) → §3.4; honesty constraints → §3.5.

### 3.1 Dual-oracle design with a fixed activity rule
Elevate the surrogate panel (`eos80ch`, n = 19,836) and an experimental panel (ChEMBL 34, n ≈ 22,267) to co-primary arms, model families `ECFP4-RF`, `GIN`, `GIN-TFP`, `CW-GIN`, `ChemBERTa` run on both. The comparison is only interpretable if the experimental arm has: a pre-declared activity rule, InChIKey dedup against the surrogate panel, reported scaffold overlap, and complexity strata (e.g. `Fsp³ ≥ 0.45 ∧ rings ≥ 4`).

### 3.2 True higher-order ring message passing (`CW-GIN`) with a fair ablation
Lift each molecular graph to a 2-dimensional regular cell complex (0-cells = atoms, 1-cells = bonds, 2-cells = chordless rings), pass messages atom↔bond, bond↔ring and ring↔ring (encoding fused/bridged/spiro junctions), and weight 2-cell embeddings by `H₁` persistence lifetime. Then run a **three-arm ablation at identical parameter counts and an identical hyperparameter-search budget**:

1. `1-WL GIN` (atoms and bonds only);
2. `GIN-TFP` (1-WL plus readout concatenation);
3. `CW-GIN` (2-cell message passing).

Add a **matched classical substructure baseline** (larger-radius fingerprint or WL-subtree kernel) and a **stereo-aware fingerprint baseline**, so that any gain can be attributed to topology rather than to extra features — and so that the "ECFP4 is stereo-blind" claim is tested rather than assumed.

### 3.3 Conformal repair with explicit assumptions and diagnostics
1. **Baseline:** class-conditional (Mondrian) CP with per-class non-conformity scores and separate quantiles.
2. **Then:** covariate-shift weighting with ESS reported and a pre-declared floor; fall back to unweighted split-conformal below it.
3. **For triage semantics:** prefer a **false-discovery-rate-controlling conformal selection** construction when the operational question is "which compounds do we route to docking/MD" — that question is about the error rate of *selections*, which prediction sets do not control.
4. **Diagnostics:** coverage by OOD decile and by class; prediction-set size distribution; calibration curve.

### 3.4 Inference at the scaffold-cluster level
Resample **scaffold clusters** (outer) and molecules within clusters (inner) over out-of-fold predictions from a fixed fold structure; use cluster-aware variance for AUROC rather than plain DeLong; cross-check with a mixed-effects logistic regression with scaffold random intercepts. Report the number of clusters and the effective sample size. This replaces — and should not be supplemented by — seed-level hypothesis tests.

### 3.5 Honesty constraints (from `AGENTS.md` §5)
Retain the honest-negative scaffold result; do not claim universal GNN/Transformer inferiority; `CW-GIN` is a hypothesis test whose null result is a publishable outcome; and every "gain" figure must carry its confidence interval from §3.4.

---

## 4. Action plan and gates

| # | Action | Gate |
|---|---|---|
| 1 | Document the label semantics and binarisation of `eos80ch` (stage-specific lineage) in Methods, or replace the label source | Constructor definition matches the oracle's actual task |
| 2 | Quantify the teacher–student alignment index via a fingerprint parameter sweep (radius, size, family) | Index reported with CI; hypothesis labelled as such |
| 3 | Build and run the three-arm `CW-GIN` ablation with matched capacity and search budget, plus classical substructure and stereo-aware baselines | Ablation table complete; no unmatched-budget comparison |
| 4 | Replace the heuristic router with Mondrian CP, then weighted CP with ESS floor | Coverage reported per class **and** per OOD decile; ESS reported |
| 5 | Replace n = 5 seed tests with scaffold-clustered resampling + mixed-effects cross-check | No seed-level p-values anywhere in the manuscript |
| 6 | Deduplicate the ChEMBL panel and report scaffold overlap | Overlap table present; activity rule pre-declared |
| 7 | Replace the removed citations with located sources | Every reference resolves to a DOI/arXiv record |

---

## 5. Verification ledger (claim → evidence)

| Claim | Status | Evidence |
|---|---|---|
| `eos80ch` is a classical fingerprint model | ✅ Verified | Ersilia model-card lineage → van Heerden et al. 2023 |
| `eos80ch` label semantics are stage-specific (ABS vs gametocyte) | ✅ Verified | van Heerden et al., *ACS Omega* 8(46), 43813–43826 (2023), DOI 10.1021/acsomega.3c05664 |
| Label threshold 0.5 and "computational, not experimental" status are documented in-repo | ✅ Verified | `Project3_.../manuscript/LaTeX/V2609/PLACEHOLDER_COMPLETION_GUIDE.md`; `SUBMISSION_READY.md` |
| Tursunbadalov & Tursunbadalov, arXiv:2607.06605 | ✅ Verified | arXiv listing |
| Wee & Jiang, *JCIM* 65(23), 12691–12706 (2025) | ✅ Verified | PubMed 41235667; DOI 10.1021/acs.jcim.5c02266 |
| CPSign = Arvidsson McShane et al. 2024 | ✅ Verified | DOI 10.1186/s13321-024-00870-9 |
| Conformal selection controls FDR over selections | ✅ Verified (rev 2.1) | Jin & Candès, *JMLR* **24**(244), 1–41 (2023) |
| Conformal selection already applied to compound screening | ✅ Verified (rev 2.1) | Bai, Tang, Xu, Svetnik, Yang, Khalili, Yu, Yang, *JCIM* **65**, 13070–13085 (2025), DOI 10.1021/acs.jcim.5c01633 |
| Descriptor-based models outperform deep learning in activity-cliff regimes | ✅ Verified (rev 2.1) | van Tilborg et al., *JCIM* **62**, 5938–5951 (2022), DOI 10.1021/acs.jcim.2c01073 (corrections: *JCIM* **63**, 2266 (2023); **64**, 9643–9648 (2024)) |
| Default fingerprints cannot separate enantiomers; chirality-aware ones can | ✅ Verified (rev 2.1) | `Project7_Quantum_Molecular_Encoding_QML/scripts/p7_chirality_fingerprint_probe.py` (sha256 `565abd0b…`), RDKit 2026.03.4 |
| Exact sign-flip floor at n = 5 | ✅ Corrected here | Two-sided floor 2/2⁵ = 0.0625 (one-sided 0.03125) |
| Shared 17-molecule cohort with P1/P2 | ✅ Verified | `Project7_.../data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv` (sha256 `b7d7c859…`) |
| "Gabrani et al. JCAMD 2024" | 🚫 Not locatable | Two searches; removed |
| "Tang et al. Nature ML 2025" | 🚫 Not locatable | Two searches; removed |
| "Alvarsson et al. JCIM 2023, exact 90 % Mondrian coverage" | 🚫 Not locatable as stated | Removed; replaced by CPSign/2025 review/Tursunbadalov |
| Bodnar et al. 2021; Tibshirani et al. 2019 | ⏸ Not re-checked | Retained as anchors; verify before citing |
| Exact 90 % class-conditional coverage as a *target output* | ⏹ Withdrawn | Coverage is measured, not promised; see §3.3 |

---

## 6. The "wow" factor — what should make a referee or editor say *waouh*

**The one line.**

> The fingerprint-versus-GNN contest is shown to be **partly a property of the label oracle** — measured, not asserted — and the triage rule is upgraded from post-hoc thresholds to a **selection procedure with the false-discovery-rate guarantee that the operational decision actually needs**.

### 6.1 Why it lands

Benchmark validity is now the live question in molecular ML, and this project is sitting on the evidence for it without having made it the headline:

1. **The oracle confound becomes a measured alignment index.** The panel's labels are produced by a classical fingerprint model (`eos80ch`; van Heerden et al., *ACS Omega* **8**(46), 43813–43826 (2023), DOI 10.1021/acsomega.3c05664). Sweeping the teacher's fingerprint hyper-parameters (radius × bit length × family) and plotting ΔAUROC(student − `ECFP4-RF`) against alignment converts "fingerprints beat GNNs" from a leaderboard into a **quantified teacher–student effect**, with the dual-oracle design (surrogate arm n = 19 836 vs experimental ChEMBL 34 arm n ≈ 22 267) as the control.
2. **The project's own controls already point at the mechanism.** On the scaffold split both classical controls drop to AUC ≈ 0.71 while the random-forest arm holds 0.8300 — i.e. **the random-forest component, not the ECFP4 fingerprint alone, carries the scaffold-split advantage** (DAR §controls; scikit-learn kNN Δ = −0.0267 and logistic regression Δ = −0.0643 on the random split). This is a *stronger and more surprising* statement than "fingerprints win", and it is already in the ledger.
3. **The correct guarantee for the decision.** The operational question is "which compounds do we route to docking/MD", which is about the error rate of **selections**, not of prediction sets. Conformal selection with FDR control is exactly that construction (Jin & Candès, *JMLR* **24**(244), 1–41 (2023)) and has already been applied to compound screening (Bai, Tang, Xu, Svetnik, Yang, Khalili, Yu, Yang, *JCIM* **65**, 13070–13085 (2025), DOI 10.1021/acs.jcim.5c01633). Adding an ESS floor with a pre-declared fallback, Mondrian class-conditional calibration, and coverage reported by class *and* OOD decile makes it a guarantee a referee can check rather than a heuristic they must trust.
4. **The 1-WL claim becomes causal.** `GIN-TFP` concatenates persistence features at the readout, so it cannot test the message-passing bottleneck; the three-arm `CW-GIN` ablation (2-cell complexes, `H₁`-weighted 2-cells) at **matched parameter count and matched hyperparameter-search budget**, with two absorbing classical baselines, does.
5. **The statistical unit is fixed.** Testing n = 5 seed means is replaced by resampling over held-out **Murcko scaffold clusters**, removing the exact two-sided floor of 2/2⁵ = 0.0625 that no FDR procedure can rescue.

### 6.2 Wow at a glance

| Element | Value | Evidence |
|---|---|---|
| Scaffold-split table (canonical) | `ECFP4-RF` **0.8300 ± 0.0023**; `GIN-TFP` 0.8138 ± 0.0107; `GIN-TNE` 0.8090; `GIN` 0.8047 ± 0.0141; `ChemBERTa` 0.7867 ± 0.0054 | `Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md` §2 (sha256 `957836db…`) |
| Random-split table (canonical) | `ECFP4-RF` 0.9433 ± 0.0003; `ChemBERTa` 0.9121; `GIN` 0.9098; `GIN-TFP` 0.9084; `GIN-TNE` 0.8918 | same |
| Control that reframes the result | kNN / logistic regression on the same ECFP4 features fall to ≈ 0.71 on the scaffold split → the RF component, not the fingerprint alone | same, DAR controls paragraph |
| Why the oracle confound is real | labels from `eos80ch`: stage-specific (asexual-blood-stage vs gametocyte) classical fingerprint models | van Heerden et al. 2023, DOI 10.1021/acsomega.3c05664 |
| Guarantee for triage | conformal selection, FDR control | Jin & Candès, *JMLR* **24**(244), 1–41 (2023); Bai et al., *JCIM* **65**, 13070–13085 (2025) |
| Why a stereo-aware baseline is mandatory | default Morgan r = 2 gives Tanimoto **1.0000** for enantiomer pairs; `includeChirality=True` gives **0.7333** (alanine) / **0.5833** (threonine) | `Project7_Quantum_Molecular_Encoding_QML/scripts/p7_chirality_fingerprint_probe.py` (RDKit 2026.03.4) |
| Benchmark-validity anchor | activity-cliff regimes where descriptor-based models outperform deep learning | van Tilborg et al., *JCIM* **62**, 5938–5951 (2022), DOI 10.1021/acs.jcim.2c01073 (corrections: *JCIM* **63**, 2266 (2023); **64**, 9643–9648 (2024)) |

### 6.3 The artifact that carries it — one figure

**Figure A ("the oracle curve")**: x-axis = teacher–student alignment (fingerprint family × radius × bit length); y-axis = ΔAUROC(student − `ECFP4-RF`) on the scaffold split, one point per student arm, with scaffold-cluster bootstrap intervals. A single plot in which the reader sees whether the fingerprint's advantage is a property of the labels or of the model class. A second panel overlays the conformal triage operating characteristic (selected fraction vs empirical FDR at the nominal α), i.e. the difference between a claimed and an achieved error rate.

### 6.4 The decisive, cheap experiments

| # | Action | Cost | Gate |
|---|---|---|---|
| W1 | Fingerprint-parameter sweep (Morgan radius 1–3, 1024/2048/4096 bits, MACCS, RDKit-FP) → alignment index for every student arm | CPU-hours; models already trained per arm | ΔAUROC reported with scaffold-cluster CIs; hypothesis labelled as a hypothesis |
| W2 | Dual-oracle comparison with a pre-declared activity rule, InChIKey dedup and reported scaffold overlap | data curation + reuse of the same five model families | Overlap table present **before** any model score is examined |
| W3 | Three-arm `CW-GIN` ablation at matched capacity **and** matched search budget, plus (i) chirality-aware Morgan (`includeChirality=True`), (ii) longer-radius / WL-subtree kernel | one GPU campaign | Ablation table complete; no unmatched-budget comparison |
| W4 | Replace the heuristic router with conformal selection (FDR-controlled) + Mondrian fallback, ESS floor pre-declared | analysis | Coverage by class **and** by OOD decile; ESS reported; nominal-vs-empirical α plot |
| W5 | Scaffold-cluster resampling + mixed-effects logistic regression cross-check | analysis | No seed-level p-values remain anywhere in the manuscript |

### 6.5 The controls that make it credible

The `ECFP4-RF` per-seed mean vectors already archived for the BH-FDR families; the kNN/logistic-regression negative controls that *already* broke the "ECFP4 is enough" reading; the five-fold-independent transformer initialisation protocol; and the honest-negative scaffold result retained as the central finding (`AGENTS.md` §5).

### 6.6 What must not be claimed

- No universal GNN/Transformer inferiority and no universal fingerprint superiority — the controls show the learner matters more than the fingerprint.
- No "surrogate-oracle bias **theorem**": it is a measurable index until proven.
- No exact 90 % coverage as a target output: coverage is measured per class and per OOD decile, and only what those bins show is claimed.
- No retracted prospective figures (the +14.2 % precision claim stays removed) and no unmatched-budget or unmatched-capacity comparisons.

### 6.7 What would falsify it

If ΔAUROC does **not** shrink when the teacher's fingerprint parameters are matched, the oracle-alignment explanation is quantitatively dead and the fingerprint advantage must be attributed elsewhere — a result that is equally publishable and is the reason W1 comes first.

### 6.8 Cover-letter line (for the editor)

> "We quantify how much of the fingerprint-versus-GNN gap is a property of the label oracle rather than of the models, and we give the out-of-distribution triage rule a finite-sample false-discovery-rate guarantee instead of hand-tuned thresholds."

---

## 7. Limits of this audit

- No model was retrained; AUC values, subgroup sizes (n = 79) and split results are quoted from `P5_DATA_ANALYSIS_REPORT.md` and the `V2609` manuscript at the pinned commit and were not re-derived.
- The claim that `GIN-TFP` uses only readout concatenation is taken from the audit's own architectural reading; the current `GIN-TFP` implementation was not re-inspected in this revision.
- "Not locatable" is a reason not to cite, not proof of fabrication.
