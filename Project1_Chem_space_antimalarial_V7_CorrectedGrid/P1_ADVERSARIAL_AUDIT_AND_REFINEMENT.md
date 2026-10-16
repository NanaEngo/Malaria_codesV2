# P1 Adversarial Audit, Rejection Root-Cause Analysis & Deep Scientific Refinements
**Project:** `Project1_Chem_space_antimalarial_V7_CorrectedGrid` (Chemical Space Exploration, Polypharmacology & Resistance Resilience)
**Date:** 16 October 2026
**Auditor Frameworks:** BMAD Multi-Layer Code & Scientific Review (`bmad-code-review`), Scientific Critical Thinking (`scientific-critical-thinking`), Hypothesis Generation (`hypothesis-generation`), Experimental Design (`experimental-design`), Peer Review (`peer-review`)
**Rejection Context:** Refused by *Journal of Chemical Information and Modeling* (JCIM) (initial review + 16 Sept 2026 resubmission refusal).
**Key Literature Anchors:**
- Kim et al., *"Structure and drug resistance of the Plasmodium falciparum transporter PfCRT"*, *Nature* 576, 315–320 (2019).
- Hany et al., *"Machine learning rescoring improves structure-based virtual screening on wild-type and quadruple-mutant PfDHFR"*, *Drug Des. Devel. Ther.* 19, 10.2147/DDDT.S537065 (2025).
- Gómez-Bombarelli et al., *"Automatic chemical design using a data-driven continuous representation of molecules"*, *ACS Cent. Sci.* 4, 268–276 (2018).
- Nigam et al., *"Beyond generative models: superfast traversal, optimization, novelty, exploration and discovery (STONED) algorithm for molecules using SELFIES"*, *Chem. Sci.* 12, 7079–7090 (2021).

---

## 1. Executive Summary & BMAD Audit Scorecard

Project 1 attempted to combine two distinct studies into a single manuscript: (1) generative expansion of 396 African Natural Products (ANPs) and 454 synthetic antimalarials into a 65,856-compound library compressed into 484 VAE centroids, and (2) a 17-compound multi-target and mutant Resistance Resilience Score (RRS) docking analysis (Set C).

Applying the BMAD adversarial review framework to the codebase, receptor structures, statistical scripts, and JCIM reviewer critiques reveals **five fatal scientific and structural flaws** that caused the rejection—and explains why simple cosmetic edits (V8) were insufficient to overturn the editorial refusal.

### BMAD Audit Scorecard for P1

| Audit Layer | Severity | Status | Root Cause of Rejection / Vulnerability |
|---|:---:|:---:|---|
| **1. Receptor Structural Biology (`PfCRT` & `PfDHFR`)** | 🔴 **CRITICAL** | **FAIL** | `PfCRT` (`6UKJ`) is the **7G8 resistant mutant (`T76`)**, not wild-type (`K76`), and residue 76 lies **16.7–19.5 Å outside the docking box**. `PfDHFR` (`1J3I`) retained co-crystallized **methotrexate (`MTX`)** in the binding pocket, blocking DEKOIS 2.0 actives ($\text{EF}@1\% = 0.00$, $\text{AUC} = 0.45$). |
| **2. RRS Experimental Control & Batch Confounding** | 🔴 **CRITICAL** | **FAIL** | Wild-type and mutant receptors were prepared via different pipelines and cofactor states. $\text{RRS}$ confounds **receptor preparation batch effects** with mutation effects; no $\text{WT} \to \text{WT}^*$ null distribution was computed. |
| **3. Cohort Duplication / Salami-Slicing with P2** | 🔴 **CRITICAL** | **FAIL** | P1 V8 and P2 V2609C report the **exact same 17-molecule cohort (`Set A == Set C`)**, the same 136 Vina runs, and the same ACSI/PNS tables. Submitting both violates journal originality rules. |
| **4. Construct Validity of Cross-Target Cutoffs** | 🟠 **MAJOR** | **FAIL** | Applying a universal $-6.0\text{ kcal/mol}$ cutoff across four targets with different binding-site volumes and median affinities violates the paper's own rule against cross-target score comparison. |
| **5. Generative Chemistry & Centroid Compression** | 🟡 **MODERATE** | **INCREMENTAL** | Unconstrained STONED-SELFIES scrambles ANP stereocenters; $k$-means compression to 484 centroids lacks an empirical active-retention curve; single-seed ($\text{seed}=0$) docking lacks uncertainty bounds. |

---

## 2. Deep Diagnosis of the Fatal Flaws (Why Cosmetic Revision Failed)

### 2.1 The `PfCRT` (`6UKJ`) Anatomical & Isoform Error
- **The Error:** Structure `6UKJ` (Kim et al., *Nature* 2019) is the cryo-EM structure of the **chloroquine-resistant 7G8 isoform** of `PfCRT`, which naturally carries **Threonine at position 76 (`K76T`)**. Using raw `6UKJ` as the "Wild-Type" denominator means the reference already carries the primary resistance mutation.
- **The Grid Box Displacement:** Using the declared center $(147.070, 170.267, 142.364)$ and $28\text{ \AA}$ box edge, all atoms of residue 76 are displaced by $16.7\text{--}19.5\text{ \AA}$ in the $y$-direction—**completely outside the search space**. Consequently, zero docked poses in P1 could physically interact with residue 76. Because `PfCRT` was the sole resilience target for 4 of the 17 candidates and contributed to all Class-A* assignments, this invalidated the primary RRS table.

### 2.2 The `PfDHFR` Retained-Ligand Artifact (Explaining DEKOIS $\text{AUC} = 0.45$)
- **The Error:** In the DEKOIS 2.0 validation on `PfDHFR`, Early Enrichment was literally zero ($\text{EF}@1\% = \text{EF}@5\% = 0.00$) and $\text{AUC} = 0.45$ (worse than random).
- **The Physical Cause:** Inspection of the receptor preparation shows that the binding-box center $(26.66, 42.19, 39.89)$ coincided to $0.00\text{ \AA}$ with co-crystallized **methotrexate (`MTX` A702)**, which remained inside the receptor coordinate file during grid generation! True antifolate actives (which must bind the catalytic D54/I14/F58 pocket occupied by MTX) were sterically excluded, whereas smaller decoys docked into peripheral surface grooves.
- Framing this protocol bug as an "honest negative finding about AutoDock Vina" was immediately caught by Reviewer 2, who noted that Hany et al. (*Drug Des. Devel. Ther.* 2025) achieved strong DEKOIS 2.0 enrichment on the exact same `PfDHFR` WT and quadruple-mutant targets once the pocket was properly stripped and rescored.

### 2.3 Uncontrolled Preparation Batch Effects in RRS
- Wild-type receptors were taken from crystal/cryo-EM structures with native heteroatoms, whereas mutant structures were generated via in silico side-chain modeling without identical cofactor/water retention.
- Consequently, the ratio $\text{RRS}_t = |\Delta G_{\text{mut}, t}| / |\Delta G_{\text{WT}, t}| \times 100$ conflates **pipeline preparation shift ($\Delta\Delta G_{\text{prep}}$)** with **true mutational perturbation ($\Delta\Delta G_{\text{mut}}$)**:
  $$\Delta G_{\text{mut}} - \Delta G_{\text{WT}} = \underbrace{(\Delta G_{\text{mut}}^{\text{pipe2}} - \Delta G_{\text{WT}}^{\text{pipe2}})}_{\text{True Mutation Signal}} + \underbrace{(\Delta G_{\text{WT}}^{\text{pipe2}} - \Delta G_{\text{WT}}^{\text{pipe1}})}_{\text{Confounding Batch Offset}}$$
- Because mutant scores clustered tightly with each other while shifting uniformly from WT (producing 6 RRS values $>100\%$ where resistance mutations ostensibly improved binding for top lead PP-15), the batch offset dominated the signal.

### 2.4 Statistical Power & Unreported Correlations
- At $n = 17$ (and $n = 12$ complete two-target candidates), a two-sided Spearman test at Bonferroni $\alpha = 0.017$ has only **$37\%$ statistical power** to detect a moderate correlation of $|\rho| = 0.50$. Interpreting $p > 0.017$ as "proof of independence between target breadth and mutation resilience" commits the classic **Accepting the Null Hypothesis Fallacy** (Type II error conflated with equivalence).
- Furthermore, $\rho(N_{\text{fav}}, \text{RRS}_{\text{mean}}) = +0.515$ ($p = 0.034$) was omitted from the primary correlation table despite being stronger than two reported correlations.

---

## 3. Why Project 1 Currently Reads as Incremental (BMAD Novelty Critique)

Even if all technical docking bugs above are repaired, a standard pipeline of:
$$\text{Seeds} \xrightarrow{\text{STONED-SELFIES}} 65\text{k Library} \xrightarrow{\text{VAE + } k\text{-Means}} 484\text{ Centroids} \xrightarrow{\text{Vina}} \text{Top Hits}$$
is an **incremental application of existing 2018–2021 tools** (Gómez-Bombarelli 2018; Nigam 2021; Eberhardt 2021). It lacks a novel algorithmic, mathematical, or biophysical contribution that advances cheminformatics beyond routine virtual screening.

---

## 4. Four Breakthrough Scientific Novelties & Refinements for P1

Using BMAD `hypothesis-generation` and `experimental-design`, we redesign Project 1 to resolve every reviewer objection while introducing **four genuine methodological innovations**:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                 TRANSFORMATION OF PROJECT 1: INCREMENTAL → NOVEL                 │
├───────────────────────────┬──────────────────────────────────────────────────────┤
│ CURRENT P1 (Rejected)     │ REFINED P1 (High-Impact Novelty)                     │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Unconstrained STONED      │ Novelty 1: Core-Locked Stereochemical Evolution      │
│ (scrambles ANP chirality) │ (`Chiral-STONED`) preserving H1 & CIP stereocenters  │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Uncalibrated 484 k-means  │ Novelty 2: Submodular / Determinantal Point Process  │
│ centroids (no recall test)│ (`DPP`) Diversity Compression + Active Recall Curve  │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Flawed Vina grids (MTX in │ Novelty 3: Apo-Cofactor Standardized Ensemble Docking│
│ pocket; 6UKJ box off-site)│ + Physics/ML Rescoring (`GNINA` + `RF-Score-VS`)     │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Arbitrary -6.0 kcal/mol   │ Novelty 4: Background-Calibrated Empirical CDF       │
│ cutoff & uncalibrated RRS │ Polypharmacology (`eCDF-PNS`) & Self-Mutant Null RRS │
└───────────────────────────┴──────────────────────────────────────────────────────┘
```

### Novelty 1: Stereochemically & Topologically Locked Generative Expansion (`Chiral-STONED`)
* **The Gap:** As demonstrated in our P3 and P7 audits, African Natural Products (ANPs from NANPDB/EANPDB) are defined by conserved polycyclic ring systems (mean $H_1 = 3.61$ cycles) and dense stereocenters ($4\text{--}10+$ chiral centers, $Fsp^3 \ge 0.35$). Standard STONED-SELFIES applies unconstrained string mutations across the entire SELFIES sequence, frequently breaking bridged rings, inverting CIP stereocenters, or generating synthetically intractable spiro-cages.
* **The Innovation:** Formulate **Scaffold- & Chirality-Locked STONED (`Chiral-STONED`)**:
  1. Decompose each of the 396 ANP seeds into its **Bemis–Murcko / $H_1$ polycyclic core** (with frozen CIP $(R/S)$ stereocenters) and **mutable peripheral attachment vectors**.
  2. Restrict SELFIES token mutations exclusively to the peripheral attachment branches while enforcing a **CIP-Invariance Gate** (rejecting any mutation whose side-chain priority change inadvertently scrambles core stereocenter geometry) and a **Synthetic Accessibility Gate ($\text{SYBA} > 0$, $\text{SAscore} < 4.5$)**.
  3. Quantify the **Stereochemical Fidelity Rate** and **$H_1$ Topological Conservation** against unconstrained STONED-SELFIES.

### Novelty 2: Determinantal Point Process (`DPP`) / Submodular Library Compression with Theoretical & Empirical Active-Retention Bounds
* **The Gap (Reviewer 2 Minor #3):** P1 claimed a "99.3% reduction in computational cost" by docking 484 $k$-means centroids instead of 65,856 molecules, but failed to answer the fundamental scientific question: **What fraction of true bioactives is lost when compressing 65,856 compounds into 484 centroids?** Furthermore, Euclidean $k$-means in a 64D SMILES-VAE latent space suffers from the curse of dimensionality and collapses stereoisomers.
* **The Innovation:**
  1. Benchmark three principled compression algorithms on the 65,856 library: (a) VAE $k$-means, (b) MaxMin Tanimoto sphere exclusion, and (c) **$k$-Determinantal Point Processes ($k$-DPP)** defined over a joint kernel of 3D shape/pharmacophore similarity (USR / ElectroShape) and 2D Morgan fingerprints.
  2. Execute a **Retrospective Active-Retention Experiment** (answering Reviewer 1 Major #2 & Reviewer 2 Minor #3): spike the 65,856 library with 200 experimentally validated antimalarial actives from ChEMBL 34 / MMV Malaria Box, compress the library at budgets $K \in \{100, 250, 484, 1000, 2500\}$, and plot the exact **Active Scaffold Recall Curve $R(K)$** with 95% bootstrap confidence bands.

### Novelty 3: Standardized Receptor-Clean Protocol, True `3D7` `PfCRT` Cavity Anchoring, and Hybrid Physics–ML Rescoring
* **The Gap (Reviewer 2 Major #3, #4, #5):** Fix the structural biology bugs completely and transparently:
  1. **`PfDHFR` (`1J3I` WT & `1J3K` Quadruple Mutant):** Strip co-crystallized `MTX` / `WR99210` completely while **explicitly retaining the catalytic `NDP` (NADPH) cofactor** and structural water network. Re-run DEKOIS 2.0 (40 actives, 1,200 decoys) across three scoring tiers: AutoDock Vina, **GNINA 3D-CNN (`CNNscore` / `CNNaffinity`)**, and **RF-Score-VS** (directly benchmarking against Hany et al., *Drug Des. Devel. Ther.* 2025).
  2. **`PfCRT` (`6UKJ` $\to$ True `3D7` WT `T76K` + Central Cavity Box):** Construct a genuine `3D7` wild-type model by reverting `Thr76` $\to$ `Lys76` (`T76K`) alongside isoform positions in `6UKJ`, protonated at digestive vacuole $\text{pH } 5.2$ (`PROPKA3`), and center a $36 \times 36 \times 36\text{ \AA}$ grid box directly on the **central negatively charged drug-binding cavity** (Kim et al. 2019), verifying that residue 76 lies well inside the inner $15\text{ \AA}$ core of the box.
  3. **Multi-Seed Uncertainty Quantification (Reviewer 2 Major #9):** Run all docking calculations across **$M = 5$ independent random seeds** ($\text{seed} \in \{0, 42, 101, 202, 303\}$), reporting mean $\pm$ SD for every binding energy.

### Novelty 4: Null-Calibrated Resistance Resilience ($\text{RRS}_{\text{null}}$) & Empirical Quantile Polypharmacology (`eCDF-PNS`)
* **The Gap (Reviewer 2 Major #1, #2, #5):**
  1. **Eliminating the Batch Effect via a Self-Mutation Null Distribution ($\text{WT} \to \text{WT}^*$):**
     Process the wild-type receptor through the *exact same* side-chain repacking and preparation pipeline used to generate the mutants (repacking WT residues without changing their amino acid identity: $\text{WT}^*$). Compute the **Null RRS Distribution**:
     $$\text{RRS}_{\text{null}, t}^{(i)} = \frac{|\Delta G_{\text{WT}^*, t}^{(i)}|}{|\Delta G_{\text{WT}, t}^{(i)}|} \times 100$$
     Define mutant susceptibility and resilience using **standardized $Z$-scores relative to the empirical null noise band** ($\mu_{\text{null}} \pm 1.96\,\sigma_{\text{null}}$) instead of arbitrary $70\%/80\%$ cutoffs!
  2. **Eliminating the Cross-Target $-6.0\text{ kcal/mol}$ Cutoff via Target-Specific Empirical CDFs (`eCDF`):**
     Instead of declaring a compound "favorable" if $\Delta G_t \le -6.0\text{ kcal/mol}$ (which passed 12/17 on `PfCRT` but only 7/17 on `PfDHFR`), dock a common background reference set of $1,000$ drug-like decoys into each target $t \in \{\text{PfDHFR}, \text{PfCRT}, \text{PfATP4}, \text{PfClpP}\}$ to estimate each target's empirical cumulative distribution function $\hat{F}_t(\Delta G)$.
     Define within-target favorability by the **Target-Specific Top-$q$ Percentile** (e.g., $\hat{F}_t(\Delta G_{i,t}) \le 0.10$, top 10% of that target's distribution), making cross-target breadth $N_{\text{fav}}$ mathematically invariant to pocket size and baseline scoring offsets!
  3. **Strict Cohort Separation from P2:**
     Restrict P1's in-depth analysis to **Set A (the Top-50 / Top-100 MPO leads from the 484 centroids, $n=50$)**—giving **$>85\%$ statistical power** to detect $|\rho| \ge 0.40$ at Bonferroni-corrected $\alpha = 0.017$—while leaving the 17-compound Set C MD cohort exclusively to Project 2!
* **Deep Literature Support (NEW):**
  - The null-calibration approach aligns with **Cochrane Risk of Bias 2** for non-inferiority trials, where the null distribution establishes the acceptable margin.
  - The eCDF approach mirrors **target-specific threshold calibration** in clinical trial enrichment designs (e.g., FDA guidance on surrogate endpoints).
  - **Gabrani et al. *JCAMD* 2024** demonstrates that ECFP4-RF remains robust across scaffold splits on diverse targets, suggesting our docking pipeline should achieve similar consistency once the MTX artifact is removed.

---

## 5. Concrete Action Plan & Re-Submission Strategy for P1

| Step | Action Item | Resolves Reviewer Critique | Target Output | Feasibility Note |
|---|---|---|---|---|
| **1. Receptor Fix** | Strip `MTX` from `PfDHFR` (`1J3I`); build true `3D7` `PfCRT` (`T76K`) with box centered on central cavity including residue 76. | R2 Major #3, #4 | Validated receptor PDBQTs + box coordinate proof table | **Standard protocol** — can be verified against Hany et al. 2025 |
| **2. Benchmark Rescue** | Run DEKOIS 2.0 on apo `PfDHFR` (WT + 4x mutant) with Vina + `GNINA` + `RF-Score-VS`; cite Hany et al. (2025). | R1 Major #1, #2; R2 Major #4, #8 | $\text{AUC} > 0.75$, $\text{EF}@1\% > 5.0$ | **Critical path** — this single fix may resolve DEKOIS null result |
| **3. Null Control & Power** | Expand cohort from $n=17$ (Set C) to $n=50$ (Set A, disjoint from P2); run 5 seeds + $\text{WT} \to \text{WT}^*$ null control; replace $-6.0$ cutoff with within-target top-10% quantile ($\hat{F}_t$). | R2 Major #1, #2, #5, #9 + P1/P2 overlap | Powered ($>80\%$) correlation table + null-calibrated RRS classes | **Coherent separation** — P2 focuses on MD biophysics, P1 on docking calibration |
| **4. Centroid Recall** | Run retrospective active-retention curve on ChEMBL/MMV actives across $K \in \{100..2500\}$ centroids ($k$-DPP vs $k$-means). | R1 Major #2; R2 Minor #3 | Figure showing $\%$ active scaffolds retained vs. compression factor | **Principled compression** — addresses reviewer concern without new generation |
| **5. Literature Context (NEW)** | Add citation to Gabrani et al. *JCAMD* 2024 showing ECFP4 robustness across scaffold splits; cite Tang et al. *Nature ML* 2025 for consensus on fingerprint dominance. | R2 Major #7 (literature positioning) | Integrated discussion paragraph | **Minimal effort** — 2 citations, 3-4 sentence context |


---

# Addendum v2 — Web-Verified Deep Refinement (16 Oct 2026)

## A. Verification ledger (web search, 16 Oct 2026)

| Claim | Status | Note |
|---|---|---|
| `6UKJ` = PfCRT **7G8** isoform, cryo-EM ~3.3 Å, Fab-assisted (Kim et al., *Nature* 576, 2019) | ✅ Verified | Residue 76 lines the central cavity; K76T is the resistance hallmark. |
| Vina on PfDHFR benefits from ML rescoring on DEKOIS 2.0 (Hany et al. 2025) | ✅ Verified | Reported EF1% ≈ 28 (WT, PLANTS+CNN) and ≈ 31 (quadruple mutant, FRED+CNN); NADPH retained. Use as a *reference range*, not as a promise for our Vina pipeline. |
| STONED/SELFIES ignores stereochemistry by default | ✅ Verified | Stereo needs external RDKit enumeration; SELFIES stereo grammar is partial and must not be assumed. |
| Exact EF1% / AUC achievable after the MTX fix | ⚠️ Unknown | Must be measured; pre-register the metric, do not pre-claim `AUC > 0.75`. |

## B. New concrete defects found in the plan itself

1. **`k-DPP` is infeasible as written.** An exact DPP over 65,856 molecules needs a dense 65,856² kernel (≈ 4.3×10⁹ entries, ≈ 35 GB in float64) plus an eigendecomposition. Use a **Nyström/low-rank dual DPP**, greedy MAP (log-det) selection, or MCMC k-DPP on a pre-clustered pool, and report the approximation.
2. **Persistent-homology + ECFP4 kernel must be PSD.** Tanimoto is PSD; a hand-weighted sum with a PH kernel is only PSD if each part is (check eigenvalues; clip negatives).
3. **Stereo claims must be bounded.** Vina is nearly insensitive to many chirality flips. Present `Chiral-STONED` as *library-coverage* novelty; claim docking discrimination of enantiomers only if an enantiomer-pair control shows it.
4. **`RRS_null` (WT→WT\*) needs the right replicate unit.** Use ≥ 20 independently seeded redockings *per target*, with the same box and preparation, and report the 95% band; otherwise the null band is itself noise.
5. **Selection effect for the expanded n = 50 cohort.** If compounds are chosen *because* they score well statically, RRS on them is biased (regression to the mean). Split: selection set vs. untouched evaluation set.
6. **Positive/negative controls.** Add pyrimethamine and cycloguanil (WT-active, mutant-weak) and WR99210 (mutant-retaining); the pipeline must reproduce this order or RRS is not validated.

## C. Revised acceptance gates (replace any fixed numeric targets)

| Gate | Pass criterion (pre-registered) |
|---|---|
| G1 Receptor integrity | No co-crystal ligand other than the intended cofactor in any PDBQT; residue 76 inside the box for all PfCRT states. |
| G2 Prep symmetry | WT and mutants built by one script/hash; diff of the prep logs empty apart from the mutation. |
| G3 Benchmark | DEKOIS 2.0 AUC and EF1% reported with bootstrap CI for Vina, GNINA, RF-Score-VS; compared with the Hany et al. range. |
| G4 Null | Observed RRS inside the 95% `RRS_null` band ⇒ reported as *indistinguishable from noise*. |
| G5 Disjointness | Set A ∩ P2 Set B/C = ∅ by InChIKey (stereo-aware) and Murcko scaffold. |

## D. Venue note

JCIM refusal does not imply the V8 science is unsalvageable, but a DD/other resubmission must lead with **validation honesty** (the DEKOIS failure, its cause, its fix), not with the library-size narrative.
