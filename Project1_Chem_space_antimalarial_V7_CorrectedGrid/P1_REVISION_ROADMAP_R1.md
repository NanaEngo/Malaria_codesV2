# P1 Revision Roadmap — Response to JCIM Reviewers

**Project**: Project 1 — Chem-space antimalarial / polypharmacology-oriented RRS framework  
**Manuscript**: "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis"  
**Journal**: *J. Chem. Inf. Model.* (JCIM)  
**Revision version**: R1 (First revision in response to reviewer comments)  
**Date**: 2026-09-09  
**Author**: Myke Vital Sao Temgoua  
**Status**: ROADMAP_DRAFT — not yet executed

---

## Executive Summary

Both reviewers appreciate the honest, transparent reporting and methodological integrity but identified **critical flaws** that prevent publication in the current form. Both reviewers explicitly encourage resubmission after addressing these issues. This roadmap organizes the required work into **three tiers**:

- **Tier 1 (CRITICAL — manuscript cannot be revised without these)**: 9 major issues requiring new computations, protocol changes, or data reanalysis
- **Tier 2 (REQUIRED — necessary for acceptance)**: 8 minor/moderate issues requiring text clarification, notation fixes, or metadata additions
- **Tier 3 (RECOMMENDED — strengthens manuscript)**: 4 enhancements that would improve impact and credibility

**Estimated timeline**: 6–8 weeks for Tier 1 completion; 2 weeks for Tier 2+3.

**Key strategic decision**: Both reviewers suggest the same solution to multiple problems — **use ligand-free receptors** and **validate with rescoring** (Hany et al. 2025 approach). This single protocol change addresses Major Points 1, 3, and 4 simultaneously.

---

## Reviewer Consensus & Strategic Priorities

### What Both Reviewers Agree On

✅ **Strengths to preserve**:
- Honest reporting with integrity (no score-to-affinity conversion, no cross-target composites, null results reported)
- Separation of evidence layers
- Genuine accessibility case for resource-limited settings
- Sound design instinct (independence of target breadth and mutation resilience)

❌ **Critical problems requiring new work**:
- **PfCRT K76 mutation issue** (R2 Major #3): The grid does not contain residue 76; wild-type is already K76T
- **DEKOIS worse-than-random due to retained ligand** (R2 Major #4): MTX blocks the binding site
- **Wild-type/mutant preparation inconsistency undermines RRS** (R2 Major #5): Batch effects dominate signal
- **Missing correlation** (R2 Major #1): N_fav vs RRS_mean correlation not reported (ρ ≈ +0.515, p=0.034)
- **Cross-target threshold problem** (R2 Major #2): −6.0 kcal/mol cutoff violates within-target design principle

### Reviewer-Specific Concerns

**Reviewer 1** emphasizes:
- Uneven structural quality across targets (mentioned but not quantified)
- Need for retrospective validation against known antimalarial scaffolds

**Reviewer 2** provides:
- Specific geometric calculations (K76 is 16.7–19.5 Å displaced from box center)
- Specific citation (Hany et al. 2025 rescoring protocol)
- Power analysis (n=17, power=0.37 to detect ρ=0.5 at α=0.017)
- Concrete recommendations (ligand-free receptors, rescoring, null RRS distribution, within-target favorability)

---

## TIER 1: CRITICAL Issues (Blocking Publication)

These issues require new computations, data regeneration, or fundamental protocol changes. The manuscript cannot be revised without addressing all nine.

---

### **T1.1 — PfCRT Structure & Grid Correction** 
**Reviewer 2, Major #3 | CRITICAL**

#### Problem Statement
1. 6UKJ chain A residue 76 is modeled as **threonine** (K76T mutant, 7G8 isoform), not lysine (3D7 wild-type)
2. Current grid center (147.070, 170.267, 142.364) with 28 Å box places residue 76 at 16.7–19.5 Å displacement in y-direction — **outside the search box**
3. No sampled pose can contact position 76, invalidating all K76T and K76A RRS values
4. This affects **every A* assignment** because PfCRT panel is sole resilience source for PP-02, PP-06, PP-11, PP-13 and contributes to PP-01, PP-15

#### Required Actions

**Action 1.1.1**: Obtain or model genuine 3D7 wild-type PfCRT structure (K76 as lysine)
- **Method**: Either (a) homology model from 6UKJ replacing T76→K, or (b) identify alternative PDB with 3D7-like sequence
- **Validation**: Verify residue 76 identity via `grep "LYS A  76" structure.pdb`
- **Output**: `pfcrt_3d7_wt_model.pdb`

**Action 1.1.2**: Re-anchor grid to central negatively-charged cavity (Kim et al. drug-interaction site)
- **Method**: Calculate cavity centroid from Kim et al. coordinates; verify cavity volume ≥500 Å³
- **Grid parameters**: Increase box edge to ≥38.9 Å to contain residue 76 (verify all atoms within box)
- **Output**: `pfcrt_gridbox_v2.txt` with new center/dimensions

**Action 1.1.3**: Re-dock entire PfCRT panel (17 compounds × 3 alleles: WT/K76T/K76A = 51 poses)
- **Protocol**: Vina 1.2.7, exhaustiveness=32, 5 seeds (0, 42, 123, 456, 789)
- **Output**: `results/pfcrt_panel_corrected/` with pose PDBQT, energy CSV, seed variance
- **QC**: Verify ≥1 pose contacts residue 76 for each compound

**Action 1.1.4**: Recompute PfCRT RRS values using corrected wild-type denominator
- **Input**: New wild-type scores from Action 1.1.3
- **Output**: Updated Table 1 PfCRT column
- **Impact assessment**: Document class changes (A*/B/C/D) for 6 affected compounds

**Estimated effort**: 2–3 weeks (modeling + 51 docking jobs + QC)

---

### **T1.2 — DEKOIS Benchmark Re-run (Ligand-Free PfDHFR)**
**Reviewer 2, Major #4 | CRITICAL**

#### Problem Statement
1. DEKOIS 2.0 benchmark shows **EF@1% = EF@5% = 0.00** (worse than random in specific way)
2. PfDHFR receptor retains methotrexate (MTX A702) at binding site centroid (0.00 Å error)
3. MTX blocks DEKOIS actives (antifolates) but allows decoys to occupy peripheral grooves
4. Hany et al. (Drug Des. Devel. Ther. 2025, DOI 10.2147/DDDT.S537065) showed rescoring with CNN-Score/RF-Score-VS improves DEKOIS from worse-than-random to better-than-random

#### Required Actions

**Action 1.2.1**: Strip MTX from PfDHFR receptor (7F3Y)
- **Method**: `grep -v "A 702" 7F3Y_processed.pdb > 7F3Y_apo.pdb`
- **Validation**: Verify no HETATM records in binding pocket
- **Output**: `pfdhfr_7f3y_apo.pdb`

**Action 1.2.2**: Re-run DEKOIS 2.0 benchmark on apo structure
- **Input**: 78 actives + 1200 decoys (verify count vs SI discrepancy: Table S7 says 1199, S8 says 1200)
- **Protocol**: Vina 1.2.7, exhaustiveness=32, seed=0 (single seed for benchmark comparability)
- **Output**: ROC-AUC, EF@1%, EF@5%, enrichment plot
- **Target**: EF@1% > 0 (eliminates zero-enrichment artifact)

**Action 1.2.3**: Implement rescoring protocol (Hany et al. 2025)
- **Method**: Apply CNN-Score and RF-Score-VS to Vina poses
- **Software**: Install scoring functions per Hany et al. repository
- **Output**: Rescored ROC-AUC comparison table (Vina raw vs CNN vs RF-Score-VS)
- **Target**: Demonstrate improvement from worse-than-random → better-than-random

**Action 1.2.4**: Re-dock Set C on apo PfDHFR (consistency)
- **Rationale**: Main docking and benchmark must use same receptor
- **Protocol**: 17 compounds × 4 PfDHFR alleles × 5 seeds = 340 poses
- **Output**: Updated PfDHFR panel scores, RRS recomputation

**Action 1.2.5**: Update manuscript text
- **SM §S12**: Replace DEKOIS section with new results
- **Main §2.3**: Add protocol detail "ligand-free apo receptor"
- **Discussion**: Cite Hany et al. 2025 explicitly (R2 requirement)

**Estimated effort**: 3–4 weeks (DEKOIS re-run + rescoring implementation + Set C re-docking)

---

### **T1.3 — Wild-Type/Mutant Preparation Consistency & RRS Null Distribution**
**Reviewer 2, Major #5 | CRITICAL**

#### Problem Statement
1. Manuscript states wild-type and mutant receptors prepared by **different routes** with **different heteroatom composition**
2. This creates batch effect that "contributes to RRS alongside the mutation" (effects not separated)
3. Reviewer observation: mutant scores differ less from each other than from wild-type → **batch effect may dominate signal**
4. Six RRS values **exceed 100%** (mutations improve binding) — all 4 PfDHFR mutations for PP-15
5. 80%/70% class boundaries are "finer than the uncertainty"

#### Required Actions

**Action 1.3.1**: Standardize receptor preparation pipeline
- **Method**: Process wild-type through **identical** pipeline as mutants (same protonation, charge assignment, minimization protocol)
- **Software**: Single Maestro/MOE/OpenBabel workflow for all alleles
- **Output**: `preparation_protocol_v2.md` documenting unified pipeline
- **Apply to**: All 4 targets × all alleles (PfDHFR: 5 structures [WT+4mut], PfCRT: 3 [WT+2mut], others: WT only = 11 total)

**Action 1.3.2**: Generate RRS null distribution
- **Method**: Dock Set C (17 compounds) against "pseudo-mutant" wild-type (WT prepared via mutant pipeline but no mutation applied)
- **Output**: 17 null RRS values showing batch-effect-only variation
- **Statistical analysis**: Mean, SD, 95% CI of null distribution

**Action 1.3.3**: Redefine RRS class boundaries outside null distribution
- **Current**: A* ≥80%, B 70–80%, C 60–70%, D <60%
- **Revised**: Place boundaries at null_mean ± 2×SD (or appropriate percentile)
- **Rationale**: Only classify compounds whose RRS deviates from batch-effect noise

**Action 1.3.4**: Re-dock entire mutation panel with standardized receptors
- **Scale**: 17 compounds × 6 PfDHFR alleles (WT + 4mut + pseudo-mut) × 5 seeds = 510 poses (PfDHFR alone)
- **Add**: 17 × 3 PfCRT alleles × 5 seeds = 255 poses
- **Total**: ~800 docking jobs
- **Output**: Recomputed Table 1 with null-corrected RRS

**Action 1.3.5**: Explain RRS > 100% cases
- **Analysis**: For PP-15 (all 4 PfDHFR mutations improve binding), investigate:
  - Pose quality: Are mutant poses in catalytic site?
  - Structural rationale: Do mutations create favorable interactions?
  - Alternative interpretation: Is PP-15 a resistance-enabling scaffold (inverse utility)?
- **Manuscript addition**: Dedicated paragraph in Results/Discussion addressing biological interpretation

**Estimated effort**: 4–5 weeks (pipeline standardization + 800 docking jobs + null analysis)

---

### **T1.4 — Missing Correlation (N_fav vs RRS_mean)**
**Reviewer 2, Major #1 | CRITICAL**

#### Problem Statement
1. Reviewer calculated **ρ(N_fav, RRS_mean) ≈ +0.515, p=0.034** from Tables 1 & 2
2. This correlation is **positive** and **larger in magnitude** than 2 of 3 correlations in Table S6
3. It is **not reported** anywhere in manuscript
4. Although not significant at α=0.017 (Bonferroni), neither is PNS–RRS (p=0.020) which is described as a "trend"
5. This creates **tension** with §2.5 caution against "non-significance = equivalence" and §4.1 claim that null results "demonstrate" independence
6. Power analysis: n=17, power=0.37 to detect ρ=0.5 at α=0.017 — **underpowered**

#### Required Actions

**Action 1.4.1**: Compute N_fav vs RRS_mean correlation
- **Input**: Table 2 N_fav values + Table 1 RRS_mean values (17 compounds)
- **Method**: Spearman correlation with 95% CI (bootstrap or permutation test)
- **Output**: ρ, p-value, confidence interval
- **Verify**: Reproduce reviewer's ρ ≈ +0.515

**Action 1.4.2**: Add to Table S6 (cross-metric correlations)
- **Location**: Insert as first row (most relevant to independence claim)
- **Format**: `N_fav vs RRS_mean | +0.515 [CI] | 0.034 | n.s.†`
- **Footnote**: †Not significant after Bonferroni correction (α=0.017)

**Action 1.4.3**: Revise independence interpretation
- **§4.1 (Discussion)**: Replace "demonstrate independence" with "do not provide strong evidence of association (but power is limited)"
- **Add power analysis**: "With n=17 and α=0.017, power to detect ρ=0.5 is 0.37; larger sample sizes are required to distinguish weak association from independence."
- **Acknowledge**: "The observed positive correlation (ρ=+0.515, p=0.034) suggests target breadth and mutation resilience may covary, though the association does not reach statistical significance after multiplicity correction."

**Action 1.4.4**: Resolve PNS–RRS "trend" inconsistency
- **Current**: p=0.020 described as trend despite α=0.017 threshold
- **Options**: 
  - (a) Reclassify as n.s. with caveat about power
  - (b) Use α=0.05 with notation that multiplicity-adjusted threshold is stricter
  - (c) Report both p-values and explicitly state that trends are exploratory
- **Recommendation**: Option (c) for transparency

**Action 1.4.5**: Add limitation statement
- **§4.4 or new §4.5**: "The study's sample size (n=17) limits statistical power to detect moderate associations. The observed correlations should be interpreted as hypothesis-generating rather than confirmatory."

**Estimated effort**: 1 week (computation + text revision)

---

### **T1.5 — Within-Target Favorability Definition**
**Reviewer 2, Major #2 | CRITICAL**

#### Problem Statement
1. Current −6.0 kcal/mol threshold **effectively performs cross-target comparison** despite paper's design to avoid this
2. Target-specific mid-ranges differ: PfDHFR −5.60, PfCRT −6.51, PfClpP −6.04, PfATP4 −6.10
3. Result: 7/17 compounds pass for PfDHFR but 12/17 for PfCRT and PfATP4 — **biased target breadth**
4. Threshold cannot be "a priori" **and** "mid-range of observed distributions" (contradiction)

#### Required Actions

**Action 1.5.1**: Define within-target favorability by rank/percentile
- **Method**: For each target, rank all 17 compounds by Vina score
- **Favorability threshold**: Top 50% (≥9/17) or top tertile (≥6/17)
- **Alternative**: Use target-specific score thresholds (e.g., median or Q3)
- **Rationale**: Eliminates cross-target comparison; each target contributes equally to N_fav

**Action 1.5.2**: Recompute Table 2 with within-target favorability
- **Input**: 17 × 4 score matrix from Table S3
- **Process**: 
  - Rank compounds within each target
  - Count favorable ranks per compound (N_fav_rank)
  - Recompute Set C class (I/II/III based on N_fav_rank distribution)
- **Output**: Updated Table 2

**Action 1.5.3**: Recompute Set C prioritization
- **Current**: PP-01/PP-02/PP-15 selected based on N_fav + RRS_class
- **Revised**: Verify prioritization unchanged or document shifts
- **Impact**: If top candidates change, assess implications for validation strategy

**Action 1.5.4**: Remove "a priori" language
- **§2.5**: Replace with "Target-specific favorability was defined by within-target rank to avoid cross-target score comparison"
- **Justify**: "This approach acknowledges that Vina scores are not directly comparable across binding sites of different sizes and chemical environments"

**Action 1.5.5**: Add sensitivity analysis
- **Test**: Does N_fav depend on favorability threshold (50th vs 67th percentile)?
- **Output**: Supplementary table showing N_fav under different thresholds
- **Conclusion**: Demonstrate robustness (or acknowledge sensitivity)

**Estimated effort**: 1 week (reanalysis + sensitivity testing)

---

### **T1.6 — Repository Access & Archival DOI**
**Reviewer 2, Major #6 | CRITICAL**

#### Problem Statement
1. Repository URL (https://github.com/NanaEngo/Malaria_codesV2) returns **404 error**
2. SI defers file names, checksums, dependency versions to repository README
3. RRS wild-type denominators do not appear elsewhere → **values in Table 1 and Figure 1 cannot be verified**
4. No software license, release tag, or archival DOI

#### Required Actions

**Action 1.6.1**: Make repository public
- **Method**: GitHub → Settings → Visibility → Change to Public
- **Date**: Before revision submission
- **Verify**: Test URL access from incognito browser

**Action 1.6.2**: Add software license
- **Recommendation**: MIT License (permissive, standard for academic code)
- **File**: `LICENSE` at repository root
- **Reason**: Enables reuse as requested by reviewers

**Action 1.6.3**: Create release tag for revision
- **Tag**: `v1.0-JCIM-R1` (semantic versioning)
- **Contents**: Freeze code state at revision submission
- **Changelog**: Document what changed from submitted version

**Action 1.6.4**: Archive to Zenodo and obtain DOI
- **Steps**:
  1. Link GitHub repository to Zenodo
  2. Create release (Action 1.6.3)
  3. Zenodo auto-archives and issues DOI
  4. Add DOI badge to README
- **Output**: `https://doi.org/10.5281/zenodo.XXXXXXX`

**Action 1.6.5**: Embed critical data in SI
- **Add to SI**: 
  - Table S_NEW1: Wild-type Vina scores for all 17 compounds × 4 targets
  - Table S_NEW2: Mutant Vina scores (full RRS denominator table)
  - Table S_NEW3: SHA-256 checksums for all CSV/PDB/PDBQT files
- **Rationale**: Paper must be verifiable even if repository becomes unavailable

**Action 1.6.6**: Update Data Availability statement
- **Current**: "Data available at GitHub repository"
- **Revised**: "All primary data, scripts, and receptor structures are archived at Zenodo (DOI: 10.5281/zenodo.XXXXXXX) and maintained at https://github.com/NanaEngo/Malaria_codesV2 (release tag v1.0-JCIM-R1). Wild-type and mutant Vina scores are provided in Tables S_NEW1 and S_NEW2."

**Estimated effort**: 1–2 days (mostly administrative)

---

### **T1.7 — Multi-Seed Docking for Top Candidates**
**Reviewer 2, Major #9 | CRITICAL**

#### Problem Statement
1. All docking uses **single seed (seed=0)**
2. PP-15 exceeds −6.0 kcal/mol cutoff by only **0.045 kcal/mol (PfDHFR)** and **0.084 kcal/mol (PfCRT)** → within noise
3. Reviewer requests ≥5 seeds to assess N_fav assignment stability

#### Required Actions

**Action 1.7.1**: Re-dock Set C with 5 seeds
- **Seeds**: 0, 42, 123, 456, 789 (standard diverse set)
- **Scope**: 17 compounds × 4 targets × 5 seeds = 340 poses
- **Protocol**: Vina 1.2.7, exhaustiveness=32
- **Output**: Score matrix with mean, SD, min, max per compound-target pair

**Action 1.7.2**: Compute score dispersion statistics
- **Metrics**: 
  - Mean ± SD for each compound-target pair
  - Max seed-to-seed difference
  - CV (coefficient of variation)
- **Output**: Table S_NEW4: Seed variability analysis

**Action 1.7.3**: Recompute N_fav with seed variability
- **Method**: Use mean score across 5 seeds for favorability assessment
- **Alternative**: Use worst-case (least favorable) seed for conservative N_fav
- **Comparison**: Table showing N_fav (single seed) vs N_fav (multi-seed mean) vs N_fav (conservative)

**Action 1.7.4**: Assess PP-15 classification stability
- **Focus**: Does PP-15 remain in favorable category for PfDHFR and PfCRT?
- **Analysis**: If score mean ± SD crosses −6.0 threshold (or rank-based threshold from T1.5), document as uncertain
- **Manuscript**: Add statement "PP-15 favorability on PfDHFR is marginal (within seed variability); experimental validation is required to confirm target engagement"

**Action 1.7.5**: Update Methods section
- **§2.3.1**: Change "seed=0" to "Five independent seeds (0, 42, 123, 456, 789) were run for each docking, and scores are reported as mean ± SD across seeds"
- **§2.5**: Add "Compounds whose favorability classification depended on seed choice are flagged"

**Estimated effort**: 2 weeks (340 docking jobs + dispersion analysis)

---

### **T1.8 — PNS and ACSI Definitions**
**Reviewer 2, Major #7 | REQUIRED (elevated to CRITICAL due to Abstract/Results usage)**

#### Problem Statement
1. PNS and ACSI appear in **Abstract, Results, Discussion, Figure 2** but are **never defined**
2. Formulas, inputs, and software not provided
3. Cannot reproduce correlations in Table S6

#### Required Actions

**Action 1.8.1**: Add definitions to Methods
- **§2.4 or new §2.4.1**: "Pharmacophore Novelty Score and ADMET Composite Score"
- **PNS formula**: Document exact calculation (e.g., `PNS = 1 - max(Tanimoto(compound, reference_set))`)
- **ACSI formula**: Document weights and normalization (e.g., `ACSI = w1×ADME1 + w2×ADME2 - w3×Toxicity`)
- **Software**: Name tool used (e.g., "calculated using RDKit 2025.03.6")
- **Reference set**: For PNS, specify what compounds are in reference set

**Action 1.8.2**: Add abbreviations to manuscript
- **First use**: "pharmacophore novelty score (PNS)" and "ADMET composite score index (ACSI)"
- **Abbreviations list**: If journal requires, add to front matter

**Action 1.8.3**: Provide values in SI
- **Table S_NEW5**: PNS and ACSI values for all 17 compounds
- **Include**: Intermediate components (e.g., individual ADMET properties for ACSI)

**Action 1.8.4**: Document reproducibility
- **SI §S11**: Add subsection "PNS and ACSI Calculation"
- **Include**: Example code snippet or pseudocode
- **Link**: Point to repository script that performs calculation

**Estimated effort**: 3 days (documentation + table generation)

---

### **T1.9 — Table S8 Contradiction Resolution**
**Reviewer 2, Major #8 | CRITICAL**

#### Problem Statement
1. **Contradiction**: SI §S12.2 states "no pose-reproduction rate is claimed" and "no test possible for PfClpP", but Table S8 lists "1 success" for all 4 targets including PfClpP
2. **PfClpP issue**: Structure 9N10 contains **no small-molecule ligand** to redock
3. **MMV rows circular**: Score-stratified MMV enrichment is "circular by construction" (text acknowledges this)

#### Required Actions

**Action 1.9.1**: Resolve PfClpP redocking claim
- **Options**:
  - (a) Withdraw PfClpP row from Table S8
  - (b) Clarify what "1 success" means (e.g., "binding site identification" not pose reproduction)
  - (c) Find alternative PfClpP structure with ligand for true redocking
- **Recommendation**: Option (a) — withdraw row and state "PfClpP validation limited to cavity identification"

**Action 1.9.2**: Remove or clearly label MMV rows
- **Current**: Table S8 includes MMV score-stratified enrichment
- **Issue**: Text says "circular by construction" because MMV actives were pre-filtered by score
- **Options**:
  - (a) Remove MMV rows entirely
  - (b) Keep with footnote: "†Score-based enrichment for MMV is circular (actives were selected by high docking scores); included for reference only"
- **Recommendation**: Option (b) for transparency

**Action 1.9.3**: Downgrade validation language
- **Current**: Table S8 caption says "establish docking protocol reliability"
- **Revised**: "Docking protocol assessment: redocking RMSD and external benchmark enrichment"
- **Text (§S12)**: Change "validation" to "assessment" throughout

**Action 1.9.4**: Add honest negative framing
- **§S12 Discussion**: "Redocking success on 4/4 liganded structures demonstrates pose-sampling competence but does not guarantee enrichment on prospective virtual screening. The DEKOIS benchmark (see §1.2.2 revision) provides an independent assessment."

**Estimated effort**: 2 days (table revision + text edits)

---

## TIER 2: REQUIRED Issues (Necessary for Acceptance)

These issues do not require new computations but must be addressed for manuscript acceptance.

---

### **T2.1 — Duplicate Paragraph Removal**
**Reviewer 2, Minor #1**

**Problem**: Paragraph duplicated across pp. 17–18 page break with contradictory statements about PP-01 and PP-15 resilience. p. 17 appears correct per Table 1.

**Action**: 
1. Remove duplicate on p. 18
2. Verify p. 17 version matches Table 1 (PP-01 and PP-15 both resilient on PfDHFR and PfCRT panels)
3. Proofread for other duplications

**Estimated effort**: 30 minutes

---

### **T2.2 — Citation Correction (VAE Reference)**
**Reviewer 2, Minor #2**

**Problem**: Ref. 19 (Kingma & Welling) is generic VAE paper; SMILES VAE requires Gómez-Bombarelli et al.

**Action**:
1. Add citation: Gómez-Bombarelli, R.; Wei, J. N.; Duvenaud, D.; Hernández-Lobato, J. M.; Sánchez-Lengeling, B.; Sheberla, D.; Aguilera-Iparraguirre, J.; Hirzel, T. D.; Adams, R. P.; Aspuru-Guzik, A. Automatic Chemical Design Using a Data-Driven Continuous Representation of Molecules. *ACS Cent. Sci.* **2018**, *4*, 268–276. DOI: 10.1021/acscentsci.7b00572
2. Replace or supplement Ref. 19 where SMILES VAE is discussed
3. Verify no other generic-vs-specific citation errors

**Estimated effort**: 30 minutes

---

### **T2.3 — Cost Reduction Framing**
**Reviewer 2, Minor #3**

**Problem**: "99.3% reduction in computational cost" is relative to exhaustive library docking, not to alternative selection methods. Does not address active-compound retention.

**Action**:
1. Revise §4.4: "Compared to exhaustive docking of the full 65,856-compound library, the centroid-clustering approach reduced computational cost by 99.3% (from ~263,000 to ~1,800 docking jobs). However, this metric does not quantify how many active compounds may have been excluded by the selection process."
2. Add limitation: "Future work should assess active-compound retention via retrospective testing on known antimalarial scaffolds"
3. Consider adding retention experiment if feasible (dock full Set B and compare hit rate to clustered subset)

**Estimated effort**: 1 hour (text revision only) or 1 week (if retention experiment added)

---

### **T2.4 — RRS Notation Consistency**
**Reviewer 2, Minor #4**

**Problem**: RRS eligibility written as `|ΔG_WT| < 5.0 kcal/mol` on p. 21 but as `|S_Vina|` elsewhere.

**Action**:
1. Standardize to `|S_Vina,WT| ≥ 5.0 kcal/mol` throughout (manuscript is "rightly careful" about score vs free energy distinction)
2. Find-replace: Search for `ΔG` in RRS context and replace with `S_Vina`
3. Verify Table 1 caption and footnotes use consistent notation

**Estimated effort**: 30 minutes

---

### **T2.5 — SI Section Numbering & Decoy Count**
**Reviewer 2, Minor #5**

**Problem**: 
1. Section S12 numbered twice (pp. S-11 and S-14)
2. Table S7 says 1,199 decoys; Table S8 says 1,200

**Action**:
1. Renumber duplicate §S12 (second instance becomes §S13 or merge sections)
2. Verify DEKOIS decoy count: Check original DEKOIS 2.0 dataset
3. Correct Tables S7 and S8 to match true count
4. Add footnote if discrepancy is due to preprocessing (e.g., "1 decoy excluded due to failed embedding")

**Estimated effort**: 1 hour

---

### **T2.6 — Figure 2 Annotation**
**Reviewer 2, Minor #6**

**Problem**: ρ, p, and n not reported directly in Figure 2 panel.

**Action**:
1. Add text annotation to Figure 2 scatter plot: "ρ = -0.559, p = 0.020, n = 17"
2. Use consistent notation with Table S6
3. Ensure annotation does not obscure data points

**Estimated effort**: 30 minutes (figure regeneration)

---

### **T2.7 — MPO Sensitivity Analysis**
**Reviewer 2, Minor #7**

**Problem**: SI §S10 defers MPO sensitivity analysis and enrichment validation to companion manuscript ("submitted"). Set C selection depends on these analyses; essential results should be in present paper.

**Action**:
1. Add MPO sensitivity summary to §S10: 
   - Test MPO score under varied parameter weights
   - Report how many compounds change rank position (e.g., "Top 10 candidates stable under ±20% weight perturbation")
2. Add enrichment validation summary:
   - Retrospective test on known antimalarials (MMV or literature hits)
   - Report enrichment factor or ROC-AUC
3. Retain companion manuscript reference but make present paper stand-alone

**Estimated effort**: 1 week (if analysis exists) or 3 weeks (if analysis must be performed)

---

### **T2.8 — Target Structural Evidence Quality Documentation**
**Reviewer 1, Major (implicit)**

**Problem**: "Target selection and structural evidence quality are highly uneven. The four targets have vastly different levels of structural validation. These differences would influence the 'target breadth' result."

**Action**:
1. Add Table S_NEW6: Target structural evidence quality
   - Columns: Target | PDB | Resolution (Å) | Ligand co-crystal? | Mutant structures? | Known drug binding? | Evidence class
   - Example rows:
     - PfDHFR | 7F3Y | 1.8 | Yes (MTX) | Yes (4 alleles) | High (validated drug target) | Class A
     - PfCRT | 6UKJ | 3.2 | No | Partial (K76T in 7G8) | Medium (resistance marker) | Class B
     - PfClpP | 2F6I | 2.6 | No | No | Low (hypothetical) | Class C
     - PfATP4 | 9N10 | 3.8 | No | No | Medium (validated) | Class B
2. Discuss in §4.3 (Limitations): "Target structural evidence quality varies (Table S_NEW6). PfDHFR is well-validated with liganded structures, whereas PfClpP and PfATP4 lack co-crystallized inhibitors. Target breadth should be interpreted in light of these evidence tiers."
3. Optionally down-weight low-evidence targets in N_fav calculation (sensitivity analysis)

**Estimated effort**: 2 days (literature review + table creation)

---

## TIER 3: RECOMMENDED Enhancements

These would strengthen the manuscript's impact and credibility but are not strictly required.

---

### **T3.1 — Retrospective Validation Against Known Antimalarials**
**Reviewer 1, Major (implicit)**

**Problem**: "At minimum a retrospective validation against known antimalarial scaffolds would strengthen the workflow's credibility."

**Action**:
1. Assemble validation set: 50–100 known antimalarials (chloroquine, artemisinin, atovaquone, etc.) + inactive structural analogs
2. Dock validation set against 4 targets
3. Compute enrichment metrics: ROC-AUC, EF@1%, EF@5%
4. Compare to DEKOIS results: Does protocol work for antimalarial scaffolds specifically?
5. Add to §S12 as "Retrospective Antimalarial Scaffold Validation"

**Estimated effort**: 3–4 weeks

---

### **T3.2 — Preliminary Experimental Validation Data**
**Reviewer 1, Major (implicit)**

**Problem**: "The proposed validation strategy lists five categories of experiments but provides no preliminary data, no estimated feasibility, and no prioritization beyond naming three candidates."

**Action**:
1. Collaborate with experimental group to obtain:
   - IC50 data for 1–3 top candidates against P. falciparum (3D7 strain minimum)
   - Preliminary binding assay (SPR, ITC, or thermal shift) for 1 candidate on 1 target
2. Add Results subsection: "Preliminary Experimental Validation"
3. Discuss concordance or discordance with computational predictions
4. Update §5 (Conclusion) to reflect experimental support

**Estimated effort**: 3–6 months (depends on collaborator capacity)

**Note**: This may be deferred to follow-up paper if reviewers accept revised manuscript without it.

---

### **T3.3 — Public Benchmark Repository**
**Recommended Best Practice**

**Action**:
1. Create benchmark suite: DEKOIS 2.0 PfDHFR + retrospective antimalarials + Set C
2. Provide standardized scoring protocol (Vina + rescoring)
3. Enable community comparison of alternative methods
4. Publish as data descriptor or software paper alongside main manuscript

**Estimated effort**: 2 weeks (packaging + documentation)

---

### **T3.4 — Cross-Validation with Hany et al. 2025 Protocol**
**Reviewer 2 Recommendation (implicit)**

**Action**:
1. Apply Hany et al. rescoring protocol (CNN-Score, RF-Score-VS) to Set C
2. Compare top-ranked candidates: Do PP-01/PP-02/PP-15 remain top-3?
3. Report rank correlation between Vina and rescored predictions
4. Add to Discussion: "Alternative scoring functions [Hany et al. ref] prioritize similar candidates, supporting robustness of selection"

**Estimated effort**: 2 weeks (software installation + rescoring + analysis)

---

## Implementation Timeline

### Phase 1: Protocol Corrections (Weeks 1–3)
**Critical dependencies first**
- **Week 1**: T1.6 (Repository public + DOI) — enables reviewer verification immediately
- **Week 1**: T1.8 (PNS/ACSI definitions) — enables correlation reproduction
- **Week 2**: T1.1.1–1.1.2 (PfCRT structure correction) — prerequisite for all PfCRT docking
- **Week 3**: T1.2.1 (PfDHFR apo structure) — prerequisite for DEKOIS and PfDHFR docking

### Phase 2: Large-Scale Docking (Weeks 4–6)
**Parallelizable — run concurrently on cluster**
- **Weeks 4–6**: T1.1.3 (PfCRT panel: 51 poses)
- **Weeks 4–6**: T1.2.2 + T1.2.4 (DEKOIS + PfDHFR Set C: ~400 poses)
- **Weeks 4–6**: T1.3.4 (Standardized mutation panel: ~800 poses)
- **Weeks 4–6**: T1.7.1 (Multi-seed Set C: 340 poses)

**Total docking jobs**: ~1,600 (feasible with 50-node cluster in 2–3 weeks)

### Phase 3: Analysis & Recomputation (Weeks 7–8)
- **Week 7**: T1.2.3 (Rescoring implementation)
- **Week 7**: T1.3.2–1.3.3 (RRS null distribution)
- **Week 7**: T1.4 (Correlation reanalysis)
- **Week 7**: T1.5 (Within-target favorability)
- **Week 8**: T1.1.4, T1.3.4, T1.7.3 (Recompute all Tables 1 & 2)

### Phase 4: Manuscript Revision (Weeks 9–10)
- **Week 9**: All Tier 2 items (T2.1–T2.8)
- **Week 9**: T1.9 (Table S8 resolution)
- **Week 9**: Update all Methods/Results/Discussion sections
- **Week 10**: Regenerate all figures and tables
- **Week 10**: Revision letter writing

### Phase 5: Optional Enhancements (Weeks 11–14)
- **Weeks 11–12**: T3.1 (Retrospective validation) — if time permits
- **Weeks 13–14**: T3.4 (Hany et al. cross-validation) — if software accessible

---

## Deliverables Checklist

### Computational Outputs
- [ ] PfCRT 3D7 wild-type model (PDB)
- [ ] PfCRT corrected grid parameters (TXT)
- [ ] PfCRT panel docking results (51 × 5 seeds = 255 PDBQT)
- [ ] PfDHFR apo structure (PDB)
- [ ] DEKOIS re-run results (ROC-AUC, enrichment plots)
- [ ] CNN-Score / RF-Score-VS rescored results
- [ ] RRS null distribution (17 values + statistics)
- [ ] Standardized receptor set (11 PDB files)
- [ ] Multi-seed docking results (340 × 5 = 1,700 PDBQT)

### Tables (New or Revised)
- [ ] Table 1 (revised RRS values)
- [ ] Table 2 (revised N_fav with within-target favorability)
- [ ] Table S6 (add N_fav vs RRS_mean row)
- [ ] Table S_NEW1 (Wild-type Vina scores)
- [ ] Table S_NEW2 (Mutant Vina scores)
- [ ] Table S_NEW3 (SHA-256 checksums)
- [ ] Table S_NEW4 (Seed variability analysis)
- [ ] Table S_NEW5 (PNS and ACSI values)
- [ ] Table S_NEW6 (Target structural evidence quality)
- [ ] Table S7 (correct decoy count)
- [ ] Table S8 (remove PfClpP row, label MMV rows)

### Figures (Revised)
- [ ] Figure 2 (add ρ, p, n annotation)
- [ ] All figures regenerated with corrected data

### Manuscript Sections (Major Revisions)
- [ ] §2.3 Methods (ligand-free receptors, standardized preparation, multi-seed)
- [ ] §2.4 Methods (add PNS/ACSI definitions)
- [ ] §2.5 Methods (within-target favorability)
- [ ] §3 Results (revised N_fav, RRS, correlations)
- [ ] §4.1 Discussion (independence interpretation)
- [ ] §4.4 Discussion (cost reduction framing, power analysis)
- [ ] §4.X Discussion (RRS > 100% interpretation)
- [ ] §S10 SI (MPO sensitivity summary)
- [ ] §S12 SI (DEKOIS revision, cite Hany et al., redocking revision)
- [ ] Data Availability (add Zenodo DOI, embed tables)

### Repository Updates
- [ ] Make repository public
- [ ] Add MIT License
- [ ] Create release tag v1.0-JCIM-R1
- [ ] Archive to Zenodo and obtain DOI
- [ ] Update README with dependency versions and checksums

### Revision Letter
- [ ] Point-by-point response to Reviewer 1
- [ ] Point-by-point response to Reviewer 2
- [ ] Summary of major changes
- [ ] Highlighted text in revised manuscript (track changes or color coding)

---

## Risk Assessment & Contingency Plans

### High-Risk Items

**Risk 1**: PfCRT 3D7 wild-type structure unavailable
- **Likelihood**: Medium
- **Impact**: High (blocks T1.1)
- **Mitigation**: Commission homology modeling service or use PyMOL/MODELLER for T76K mutation
- **Contingency**: If modeling unreliable, withdraw PfCRT from RRS panel and focus on PfDHFR (still publishable)

**Risk 2**: DEKOIS rescoring implementation fails (software dependencies)
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Contact Hany et al. for scripts/support
- **Contingency**: Report DEKOIS improvement without rescoring (apo structure alone may suffice)

**Risk 3**: RRS null distribution overlaps all observed RRS values (no signal)
- **Likelihood**: Low-Medium (reviewer suspects this)
- **Impact**: Critical (undermines entire RRS framework)
- **Mitigation**: Distinguish preparation batch effect from true mutation effect via control experiment
- **Contingency**: Reframe paper as "docking protocol cannot resolve mutation effects with current receptor preparation methods" — honest negative result, still publishable

**Risk 4**: Within-target favorability changes top candidates
- **Likelihood**: Medium
- **Impact**: Medium (affects validation prioritization)
- **Mitigation**: Assess stability via sensitivity analysis (T1.5.5)
- **Contingency**: Expand candidate list from 3 to 5–7 for validation

### Low-Risk Items
- Repository access (T1.6): Administrative only, no scientific dependency
- Citation corrections (T2.2, T2.4, T2.5, T2.6): Editorial only
- Duplicate removal (T2.1): Copy-editing only

---

## Success Criteria

### Minimum Acceptable Revision (All Tier 1 + Tier 2)
1. PfCRT structure corrected, grid verified to contain K76
2. PfDHFR apo structure used, DEKOIS better than random
3. Wild-type/mutant preparation standardized, RRS null distribution reported
4. N_fav correlation reported, independence claim softened
5. Within-target favorability implemented
6. Repository public with DOI
7. Multi-seed docking completed
8. PNS/ACSI defined
9. All Tier 2 editorial fixes applied

**Outcome**: Paper defensible for resubmission

### Strong Revision (Tier 1 + Tier 2 + Select Tier 3)
Add T3.1 (retrospective validation) and/or T3.4 (Hany cross-validation)

**Outcome**: Paper significantly strengthened, likely acceptance

### Ideal Revision (All Tiers)
Add preliminary experimental data (T3.2)

**Outcome**: High-impact publication with experimental support

---

## Reviewer Response Strategy

### Tone & Framing
- **Acknowledge integrity**: "We thank the reviewers for recognizing our commitment to honest reporting and for providing constructive, detailed feedback."
- **Accept major criticisms**: "We agree that the issues identified are critical and have performed substantial new work to address them."
- **Emphasize new computation**: "This revision includes ~1,600 new docking calculations, protocol standardization, and independent validation."
- **Reframe paper if needed**: If RRS null distribution shows no signal, pivot to "honest negative result demonstrating limits of current docking protocols for mutation analysis"

### Specific Responses

**To Reviewer 1** (uneven target evidence):
> "We have added Table S_NEW6 documenting structural evidence quality for each target and explicitly discuss evidence tiers in the revised Discussion (§4.3). We have also performed retrospective validation against known antimalarial scaffolds (new §S12.3) to address the concern about computational-only credibility."

**To Reviewer 2** (PfCRT K76 problem):
> "We thank the reviewer for the detailed geometric analysis. We have obtained a genuine 3D7 wild-type PfCRT structure (K76 as lysine), re-anchored the grid to the Kim et al. drug-interaction cavity with a 40 Å box that contains all residue 76 atoms, and re-docked the entire PfCRT panel (51 poses × 5 seeds = 255 calculations). The revised RRS values are reported in Table 1."

**To Reviewer 2** (DEKOIS worse-than-random):
> "The reviewer is correct that retained methotrexate caused the EF@1% = 0 artifact. We have stripped MTX from 7F3Y, re-run DEKOIS 2.0 on the apo structure, and implemented the Hany et al. (2025) rescoring protocol as recommended. The revised benchmarks are reported in §S12 and demonstrate meaningful enrichment."

**To Reviewer 2** (wild-type/mutant batch effect):
> "We have standardized the receptor preparation pipeline (new §2.3.2) so that wild-type and mutant structures are processed identically. We have computed a RRS null distribution by docking Set C against pseudo-mutant wild-type receptors (new Figure S_NULL and Table S_NULL). The revised RRS class boundaries are placed outside this null distribution, and compounds whose RRS falls within the null range are flagged as indeterminate."

---

## Resource Requirements

### Computational
- **Cluster access**: 50–100 nodes for 3 weeks
- **Storage**: ~500 GB for docking outputs (PDBQT files)
- **Software**: Vina 1.2.7, OpenBabel, RDKit, CNN-Score, RF-Score-VS, PyMOL/MODELLER

### Personnel
- **Computational chemist** (lead): 8 weeks full-time
- **Structural biologist** (homology modeling): 1 week consultation
- **Data scientist** (statistics, power analysis): 3 days consultation
- **Technical writer** (manuscript revision): 1 week

### Budget (Estimated)
- **Cluster time**: $500–1,000 (if not free academic allocation)
- **Zenodo archival**: Free
- **Modeling software licenses**: $0 (academic PyMOL/MODELLER) or $500 (commercial)
- **Total**: $500–1,500

---

## Conclusion

This revision is **substantial but achievable**. Both reviewers explicitly encourage resubmission and provide clear, actionable guidance. The core scientific instinct (target breadth and mutation resilience as independent properties) is sound and should be preserved.

**Key strategic insight**: The ligand-free receptor + standardized preparation + rescoring approach (repeatedly recommended by Reviewer 2) addresses multiple problems simultaneously and aligns with recent best practices (Hany et al. 2025).

**Critical path**: 
1. PfCRT structure correction (blocks PfCRT work)
2. PfDHFR apo structure (blocks DEKOIS and PfDHFR work)
3. Standardized preparation pipeline (blocks all RRS work)
4. Large-scale docking (parallelizable, 3 weeks wall time)
5. Analysis and manuscript writing (serial, 3 weeks)

**Timeline**: 10–12 weeks to submission-ready revised manuscript if Tier 1 + Tier 2 only; 14–16 weeks if Tier 3 enhancements included.

**Recommendation**: Execute all Tier 1 + Tier 2 immediately; evaluate Tier 3 items after Phase 3 analysis (Week 8) based on results quality and remaining time budget.

---

**Prepared by**: Kiro AI Agent (with scientific-critical-thinking, scientific-writing, and article-writing skills activated)  
**Date**: 2026-09-09  
**Status**: DRAFT — awaiting author review and execution authorization
