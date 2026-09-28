# P1 V4 Resource Inventory for V7 Enhancement

**Created:** 2026-01-10  
**Purpose:** Systematic inventory of V4 manuscript resources to identify content for V7 enhancement

---

## EXECUTIVE SUMMARY

V4 represents the comprehensive centroid-based screening manuscript with:
- **484 centroids** across 3 targets (PfDHFR, PfCRT, PfATP4)
- **Extensive MPO framework** with 5 components + polypharmacology bonus
- **19,913 synthesizable leads** from 53 clusters
- **Comprehensive ADMET analysis** and safety profiling
- **Detailed enrichment validation** (MMV Malaria Box + DEKOIS)
- **Scaffold diversity analysis** (20,702 unique scaffolds, 69.3% recovery)

V7 currently focuses on **17-candidate polypharmacology cohort** across **4 targets** (adds PfClpP).

---

## SECTION 1: FIGURES TO ADAPT FOR V7

### Priority 1: Essential Figures

1. **Physicochemical Properties Violin Plot** (`phys_chem.pdf`)
   - **Location:** V4 main, Figure 1
   - **Content:** Violin plots for MW, logP, TPSA, HBD, HBA, RB across NP/SD/Generated subgroups
   - **Adaptation:** Update for Set-C 17-candidate cohort if different distributions
   - **Action:** Copy to V7 Graphics/, verify compatibility with Set-C data

2. **MPO Sensitivity Analysis** (likely in SM)
   - **Content:** Shows weight perturbation effects on top-1000 ranking
   - **Relevance:** V7 may not use MPO, but could use for Discussion context
   - **Action:** Extract if available, include in V7 SM if relevant

3. **VAE Training Curves** (SM)
   - **Content:** Loss convergence for 32D and 64D latent spaces
   - **Relevance:** Background Methods validation
   - **Action:** Check if V7 needs VAE methodology detail

4. **Clustering Quality Comparison** (SM)
   - **Content:** Silhouette/Calinski-Harabasz/Davies-Bouldin indices
   - **Relevance:** Methods validation for centroid selection
   - **Action:** Include in V7 SM if centroid methodology is discussed

### Priority 2: Supplementary Figures

5. **UMAP Latent Space Projection** (SM, likely exists)
   - **Content:** 2D UMAP of 64D latent space colored by cluster
   - **Relevance:** Visual validation of VAE clustering
   - **Action:** Check SM figures, adapt for V7 if needed

6. **Enrichment Curves** (SM, likely exists)
   - **Content:** ROC curves for MMV Malaria Box per target
   - **Relevance:** Benchmarking validation
   - **Action:** Check if relevant for V7 validation section

### Priority 3: Candidate-Specific Figures (CRITICAL FOR V7)

7. **Top-10 Binding Mode Figures** (`SM_Figure_S15_top10_binding_modes.pdf`)
   - **Location:** V4 SM
   - **Content:** 2D interaction diagrams for top-10 MPO candidates
   - **Adaptation:** **V7 NEEDS binding mode figures for PP-01 to PP-17**
   - **Action:** Use V4 template to create V7-specific binding mode figures for 17 candidates

---

## SECTION 2: TABLES TO ADAPT FOR V7

### Priority 1: Essential Tables (Main Text)

1. **Enrichment Validation Table** (Table in main, ~line 400)
   - **Content:** ROC-AUC, EF5%, EF10%, BEDROC per target (PfDHFR/PfCRT/PfATP4)
   - **Adaptation:** V7 adds PfClpP (4th target), update accordingly
   - **Action:** Verify if V7 has enrichment data for all 4 targets

### Priority 2: SM Tables (CRITICAL - Many Applicable to V7)

2. **SM Table: Druglikeness Compliance** (SM-tab:druglikeness)
   - **Content:** Lipinski/Veber/SYBA pass rates for full library + expansion
   - **Relevance:** V7 Set-C cohort may have different rates
   - **Action:** Regenerate for 17-candidate cohort if needed

3. **SM Table: Selectivity Index Distribution** (SM-tab:selectivity)
   - **Content:** SI_pred distribution for 810 screened molecules
   - **Relevance:** V7 needs SI for 17 candidates
   - **Action:** Calculate SI_pred for Set-C cohort

4. **SM Table: CYP450 Inhibition** (SM-tab:cyp450)
   - **Content:** Mean/median CYP2C9/2C19/3A4/2D6 inhibition probabilities
   - **Relevance:** Critical ADMET data for V7 candidates
   - **Action:** Extract CYP data for 17 Set-C candidates

5. **SM Table: Stage-Specific Activity** (SM-tab:stage_activity)
   - **Content:** eos80ch predictions for asexual vs sexual stages
   - **Relevance:** Mechanistic profiling for V7 Discussion
   - **Action:** Calculate for 17 candidates if not already done

6. **SM Table: RRS + Polypharmacology** (SM-tab:rrs_polypharm) - **CRITICAL**
   - **Content:** This is the V7 cohort! 17 candidates with RRS/PNS/ACSI
   - **Status:** Should already exist in V7 data
   - **Action:** Verify V7 has this table in SM, cross-check with BMAD

7. **SM Table: Top-10 Retrosynthesis** (SM-tab:sm_s20_retrosynthesis)
   - **Content:** ASKCOS retrosynthetic routes for top-10 MPO candidates
   - **Relevance:** V7 should have retrosynthesis for select candidates
   - **Action:** Generate for top V7 candidates (e.g., PP-06, PP-11, PP-15)

8. **SM Table: Scaffold Diversity** (SM-tab:scaffolds)
   - **Content:** Top-10 Bemis-Murcko scaffolds + counts
   - **Relevance:** Library characterization context
   - **Action:** Check if V7 needs scaffold analysis for 17-candidate cohort

9. **SM Table: Scaffold Recovery** (SM-tab:scaffold_recovery)
   - **Content:** Seed NP scaffold retention rate (69.3%)
   - **Relevance:** Generative model validation
   - **Action:** Background Methods, may not need update for V7

10. **SM Table: NP-Related Summary** (SM-tab:np_related_summary)
    - **Content:** NP-relatedness for optimization candidates (Tanimoto ≥ 0.4)
    - **Relevance:** Check if V7 17-candidates have NP-relatedness profile
    - **Action:** Calculate Tanimoto to seed NPs for Set-C cohort

11. **SM Table: Tanimoto Novelty** (SM-tab:tanimoto_novelty)
    - **Content:** Tanimoto distribution to seed NPs (92.6% < 0.4)
    - **Relevance:** Generative model diversity validation
    - **Action:** Background context, likely not needed for V7 update

12. **SM Table: PCA Variance** (SM-tab:pca)
    - **Content:** Explained variance PC1-4 from physicochemical descriptors
    - **Relevance:** Chemical space dimensionality analysis
    - **Action:** Could include in V7 SM if space permits

13. **SM Table: fsp3 Distribution** (SM-tab:fsp3)
    - **Content:** 3D structural complexity metrics
    - **Relevance:** Drug-likeness characterization
    - **Action:** Calculate for 17-candidate cohort

14. **SM Table: Virtual Screening Hit Rates** (SM-tab:virtual_screening)
    - **Content:** Per-target hit rates for 484 centroids
    - **Relevance:** Centroid-based methodology validation
    - **Action:** V7 may cite for Methods context, not directly applicable

15. **SM Table: Computational Cost Comparison** (SM-tab:computational_comparison)
    - **Content:** CPU-hours centroid vs exhaustive (99.3% reduction)
    - **Relevance:** Efficiency claim for Discussion
    - **Action:** Include in V7 Discussion as context

16. **SM Table: MMV Validation** (SM-tab:mmv_validation)
    - **Content:** Per-target MMV hit rates + ROC-AUC
    - **Relevance:** Benchmarking validation
    - **Action:** Check if V7 has similar validation

17. **SM Table: Redocking Validation** (SM-tab:redocking_validation)
    - **Content:** RMSD < 2.0 Å for co-crystallized ligands
    - **Relevance:** Docking protocol validation
    - **Action:** Verify V7 has redocking validation for all 4 targets

18. **SM Table: Consensus Filtering** (SM-tab:consensus)
    - **Content:** Hit rate reduction from dual-filter consensus
    - **Relevance:** Docking methodology
    - **Action:** Check if V7 uses consensus scoring

19. **SM Table: MPO Sensitivity** (SM-tab:sm_s17_mpo_sensitivity)
    - **Content:** Spearman ρ + Jaccard for 25 weight perturbations
    - **Relevance:** MPO robustness analysis
    - **Action:** V7 may not use MPO, skip unless needed for comparison

20. **SM Table: ADMET Cross-Validation** (SM-tab:sm_s16_admet_crossval)
    - **Content:** ADMET-AI vs RDKit proxy concordance
    - **Relevance:** ADMET prediction validation
    - **Action:** Check if V7 has ADMET data for 17 candidates

21. **SM Table: VAE Comparison** (SM-tab:vae_comparison)
    - **Content:** 32D vs 64D latent space performance
    - **Relevance:** Methods validation
    - **Action:** Background context, likely not needed

22. **SM Table: Clustering Comparison** (SM-tab:clustering_comparison)
    - **Content:** KMeans vs Jarvis-Patrick vs BIRCH
    - **Relevance:** Clustering algorithm selection
    - **Action:** Background Methods, likely not needed

23. **SM Table: ScafVAE Diversity Benchmark** (SM-tab:diversity_comparison)
    - **Content:** ConvVAE-SMILES vs ScafVAE comparison
    - **Relevance:** Generative model benchmarking
    - **Action:** Background context for Introduction/Methods

24. **SM Table: Source Breakdown** (SM-tab:source_breakdown)
    - **Content:** NP/SD/Cheese/STONED counts in 65,856-molecule library
    - **Relevance:** Library composition
    - **Action:** Background context, not needed for V7 update

---

## SECTION 3: METHODS CONTENT TO PORT

### 3.1 MPO Framework Mathematical Formulations (SM Section)

**Location:** V4 SM, Section "Multi-parameter optimization scoring function"

**Content:**
- Complete mathematical formulations for:
  1. S_vina (35% weight, min-max scaling)
  2. S_diff (25% weight, logistic sigmoid)
  3. S_qed (20% weight, direct use)
  4. S_admet (15% weight, 11-endpoint composite)
  5. P_Ro5 (5% weight, penalty term)
  6. Polypharmacology bonus (+0.05 per additional target)

**Relevance:** V7 may not use MPO explicitly, but should reference for comparison
**Action:** Include MPO framework in V7 SM for methodological context if space permits

### 3.2 ADMET Composite Score (11 Endpoints)

**Location:** V4 SM, Component 4 subsection

**Content:** List of 11 ADMET-AI endpoints:
- HIA, logS, Caco-2, BBB, hERG, AMES, DILI, SA, P-gp, CYP450, clearance

**Action:** V7 should report ADMET profiles for 17 candidates in SM

### 3.3 Centroid-Based Screening Workflow (SM)

**Location:** V4 SM, "Centroid-based screening and MPO stratification" subsection

**Content:** 5-step workflow:
1. K-Means clustering (484 centroids, 64D VAE)
2. Consensus docking (Vina + DiffDock)
3. MPO scoring (93 EXCELLENT/GOOD centroids)
4. Optimization-worthy threshold (76 centroids, MPO ≥ 0.40)
5. Scaffold expansion (53 clusters → 40,481 molecules → 19,913 leads)

**Relevance:** Background for V7 Methods (how Set-C cohort relates to parent library)
**Action:** Cite V4 for centroid methodology, focus V7 on polypharmacology analysis

### 3.4 NP-Relatedness Filtering (SM)

**Location:** V4 SM, "Natural product relatedness filtering" subsection

**Content:** Tanimoto ≥ 0.4 to 396 seed NPs (Morgan FP, r=2, 2048 bits)

**Action:** Calculate NP-relatedness for 17 Set-C candidates

### 3.5 Sensitivity Analysis Methodology (SM)

**Location:** V4 SM, "Framework limitations and sensitivity" subsection

**Content:** 25 weight perturbations (±10-20% per component), Spearman ρ + Jaccard metrics

**Relevance:** MPO robustness validation
**Action:** V7 may skip if not using MPO

### 3.6 Docking Protocol Details (Main Methods)

**Location:** V4 main, Section 2.6 "Target selection, molecular docking, and virtual screening"

**Content:**
- Grid box 25 Å³ for 3 targets (PfDHFR, PfCRT, PfATP4)
- Grid centers: 7F3Y (8.340, -13.900, -41.754), 6UKJ (152.990, 151.042, 159.379), 9N10 (134.840, 133.100, 97.630)
- Vina exhaustiveness 64
- DiffDock 40 poses/ligand
- Dual-filter thresholds: EXCELLENT ≤ -7.0 kcal/mol, GOOD -7.0 to -5.0 kcal/mol

**Action:** V7 adds PfClpP/2F6I, verify grid center and thresholds

---

## SECTION 4: DISCUSSION CONTENT TO PORT

### 4.1 Scaffold Paradox Resolution (Main Discussion)

**Location:** V4 main, Discussion paragraph 2

**Content:** Explanation of 92.6% Tanimoto < 0.4 + 69.3% scaffold recovery paradox
- Ring systems preserved, substituents diverge
- 1.84× scaffold-to-whole-molecule Tanimoto ratio
- STONED-SELFIES mechanism (SELFIES mutations preserve ring syntax)

**Relevance:** V7 Discussion context for generative model
**Action:** Include in V7 Discussion if generative expansion is discussed

### 4.2 Topological Data Analysis (Main Discussion)

**Location:** V4 main, Discussion paragraph 3

**Content:** H1 persistence (ring topology) preserved, H0 (atom connectivity) diverges

**Relevance:** Advanced topic for Discussion
**Action:** Include if V7 Discussion covers TDA/topological features

### 4.3 Activity Cliff Risk Assessment (Main Discussion)

**Location:** V4 main, Discussion paragraph 5-6

**Content:**
- Full-cluster rescoring of top-20 MPO clusters (1,815 molecules)
- Per-cluster SD: 0.17-0.38 kcal/mol (below 1.5 kcal/mol flag)
- Mean Spearman ρ = 0.025 (Tanimoto vs Vina)
- Centroid underestimates binding by 0.13-0.66 kcal/mol

**Relevance:** Centroid methodology limitation
**Action:** Include in V7 Discussion Limitations section

### 4.4 Multi-Target vs Single-Target Optimization (Main Discussion)

**Location:** V4 main, Discussion paragraph 7

**Content:** >70 multi-target compounds (MPO ≥ 0.50, ≥2 targets), but top-20 are single-target optimized

**Relevance:** V7 focuses on multi-target, so this is context
**Action:** Contrast V7 polypharmacology approach with V4 single-target dominance

### 4.5 Computational Efficiency Discussion (Main Discussion)

**Location:** V4 main, Discussion final paragraphs

**Content:**
- 99.3% cost reduction (1,452 vs 197,568 docking runs)
- 517-1,291 CPU-hours vs 70,248-175,620 CPU-hours
- Accessible to malaria-endemic research groups

**Relevance:** Key efficiency claim
**Action:** Include in V7 Discussion as context for centroid-based approach

### 4.6 Comparison with Prior Studies (Main Discussion)

**Location:** V4 main, Discussion subsection "Comparison with prior computational studies"

**Content:**
- Expands beyond static library characterization (Ntie-Kang 2018, Simoben 2020)
- 94.9% coverage of ANPDB at Tanimoto ≥ 0.4
- 37.0% unique scaffolds (91/246 frameworks) absent from ANPDB

**Relevance:** Literature positioning
**Action:** Include in V7 Introduction or Discussion for context

### 4.7 Named Lead Analysis (Main Discussion)

**Location:** V4 main, Discussion subsection "Named lead analysis"

**Content:** Ligand 201 (PfDHFR, -8.49 kcal/mol), Ligand 438 (PfATP4, -5.86 kcal/mol)

**Relevance:** V4-specific leads, not applicable to V7 Set-C cohort
**Action:** V7 should have its own named lead analysis for PP-01 to PP-17

---

## SECTION 5: INTRODUCTION CONTENT TO PORT

### 5.1 Malaria Burden Statistics (Main Introduction)

**Location:** V4 main, Introduction paragraph 1

**Content:** "In 2023, WHO estimated approximately 263 million malaria cases and 597,000 deaths"

**Relevance:** V7 uses same statistics (verified in cross-review)
**Action:** Already in V7, no change needed

### 5.2 Target-Based vs Phenotypic Screening (Main Introduction)

**Location:** V4 main, Introduction paragraph 3

**Content:** Target-based (DHFR, CRT, ATP4) vs phenotypic (MMV Malaria Box) paradigms

**Relevance:** Background context
**Action:** V7 Introduction should briefly cover this (check current state)

### 5.3 Hybrid Pharmacophore Rationale (Main Introduction)

**Location:** V4 main, Introduction paragraph 5

**Content:** NP+SD hybrids combine privileged scaffolds with synthetic tunability

**Relevance:** Core motivation for hybrid library
**Action:** V7 should emphasize hybrid approach in Introduction

### 5.4 Computational Accessibility Gap (Main Introduction)

**Location:** V4 main, Introduction paragraph 7

**Content:** "Conventional approaches demand screening of tens of thousands of compounds per target, exceeding 1000 CPU-hours per target. Such computational requirements are prohibitively expensive for research groups in malaria-endemic regions, where 94% of global cases occur."

**Relevance:** Key motivation for centroid-based approach
**Action:** V7 Introduction should include this accessibility argument

### 5.5 Topological Context (Main Introduction)

**Location:** V4 main, Introduction final paragraph before Methods

**Content:** TopologyNet, D-GRIL, Q2SAR, PACTNet context for topological approaches

**Relevance:** Advanced background for TDA/quantum representations
**Action:** V7 may include if P3 topological features are discussed

---

## SECTION 6: GRAPHICS FOLDER INVENTORY

**Location:** `Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Graphics/`

Need to list directory to identify available figures:

### Action Required:
1. List V4 Graphics/ folder to identify all available figures
2. Identify which figures are cited in V4 main/SM
3. Determine which figures should be copied to V7 Graphics/


### Complete V4 Graphics Inventory:

**Core Figures (Main Text):**
1. `phys_chem.pdf` - Physicochemical violin plots (NP/SD/Generated)
2. `flowchart_chemspace.pdf` - Workflow diagram
3. `graphical_abstract.png` - TOC graphic

**Binding Mode Figures:**
4. `interaction_201.png` - Ligand 201 (PfDHFR top hit)
5. `interaction_214.png` - Ligand 214 (PfCRT top hit)
6. `interaction_438.png` - Ligand 438 (PfATP4 top hit)
7. `SM_Figure_S15_top10_binding_modes.pdf` - **CRITICAL: Top-10 binding modes**

**Validation Figures:**
8. `enrichment_roc_curves.pdf` - ROC curves for MMV Malaria Box
9. `enrichment_all_targets_combined.pdf` - Combined enrichment analysis
10. `enrichment_factors_comparison.pdf` - EF5% / EF10% comparison
11. `enrichment_metrics_heatmap.pdf` - Heatmap of enrichment metrics
12. `PfATP4_9N10_enrichment_curves.png` - Target-specific enrichment
13. `redocking_rmsd.pdf` - Redocking validation RMSD
14. `redocking_success_rate.pdf` - Redocking success rate bar chart
15. `chembl_benchmark_comparison.pdf` - ChEMBL threshold calibration

**Consensus Scoring Figures:**
16. `consensus_correlation_analysis.pdf` - Vina vs DiffDock correlation
17. `consensus_hit_rate_comparison.pdf` - Dual-filter hit rate reduction
18. `consensus_overlap_analysis.pdf` - Venn diagram of consensus filters

**VAE/Clustering Figures:**
19. `32_smi_vae_training_history_full.pdf` - 32D VAE training curves
20. `64_smi_vae_training_history_full.pdf` - 64D VAE training curves
21. `vae_training_curves.pdf` - Combined VAE curves
22. `vae_accuracy_comparison.pdf` - VAE accuracy comparison
23. `clustering_quality_comparison.pdf` - Clustering metrics (Silhouette/CH/DB)
24. `si_figure_s14_umap_latent_space.pdf/.png` - UMAP projection of latent space
25. `intra_inter_cluster_similarity_distributions.pdf` - Tanimoto intra vs inter-cluster

**ADMET/Activity Figures:**
26. `admet_prop.pdf` - ADMET property distributions
27. `ACTIVITY_PRED.pdf` - Ersilia activity predictions
28. `mal_dat.pdf` - Malaria dataset statistics

**Other Figures:**
29. `docking_summary_4panel.pdf` - 4-panel docking summary
30. `figure_3_rmsd_vs_affinity.pdf` - RMSD vs binding affinity scatter
31. `physicochemical_distributions_by_cluster.pdf` - Per-cluster property distributions
32. `threshold_calibration_distribution.pdf` - ChEMBL threshold distribution

---

## SECTION 7: PRIORITY ACTION PLAN FOR V7 ENHANCEMENT

### Phase 1: Critical Figures (Immediate - Day 1)

**Action 1.1: Copy Essential Figures to V7**
```bash
# Copy from V4 Graphics to V7 Graphics
cp Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Graphics/phys_chem.pdf \
   Project1_Chem_space_antimalarial_V7_CorrectedGrid/manuscript/Graphics/
```

**Action 1.2: Generate V7-Specific Binding Mode Figures**
- **Template:** Use `SM_Figure_S15_top10_binding_modes.pdf` as style guide
- **Content:** Create interaction diagrams for PP-01 to PP-17 (all 17 candidates)
- **Format:** 2D ligand-protein interaction diagrams (H-bonds, π-stacking, hydrophobic)
- **Tool:** PyMOL or LigPlot+ (check BMAD for existing visualization scripts)
- **Priority:** CRITICAL - V7 needs these for Results/Discussion

**Action 1.3: Verify V7 Has Enrichment Validation**
- Check if V7 has ROC curves for all 4 targets (adds PfClpP)
- If missing, generate using V4 templates

### Phase 2: Essential Tables (Day 1-2)

**Action 2.1: Generate V7 Set-C Tables**

Create in V7 SM:
1. **Table S1: Set-C Druglikeness** (adapt from V4 SM-tab:druglikeness)
   - Calculate for 17 candidates: Lipinski/Veber/SYBA/NPL/SA/QED compliance
   
2. **Table S2: Set-C ADMET Profile** (new)
   - CYP450 inhibition (CYP2C9/2C19/3A4/2D6) for 17 candidates
   - hERG, DILI, BBB, HIA predictions
   - SI_pred for 17 candidates

3. **Table S3: Set-C Physicochemical Properties** (new)
   - MW, logP, HBD, HBA, TPSA, RB, fsp3 for 17 candidates
   - Compare to V4 library statistics

4. **Table S4: Set-C Scaffold Analysis** (new)
   - Bemis-Murcko scaffolds for 17 candidates
   - Tanimoto to seed NPs (NP-relatedness)

5. **Table S5: Set-C Stage-Specific Activity** (new)
   - eos80ch predictions (asexual vs sexual stages) for 17 candidates

6. **Table S6: Set-C Retrosynthesis** (high priority)
   - ASKCOS routes for top candidates (PP-06, PP-11, PP-15, etc.)
   - Use V4 SM-tab:sm_s20_retrosynthesis as template

**Action 2.2: Cross-Check with BMAD**
- Verify all 17-candidate data exists in `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
- Extract missing data from BMAD if tables incomplete

### Phase 3: Methods Enhancement (Day 2-3)

**Action 3.1: Port V4 Docking Protocol Details**
- Add grid box specifications for PfClpP/2F6I to V7 Methods
- Verify V7 has complete docking protocol description for all 4 targets

**Action 3.2: Port V4 Validation Methods**
- Add redocking validation section if missing in V7
- Add enrichment validation methods (ROC-AUC, EF5%, BEDROC)

**Action 3.3: Add Background on Centroid-Based Sampling**
- Brief paragraph in V7 Methods explaining how Set-C relates to parent 65,856-molecule library
- Cite V4 for detailed centroid methodology

### Phase 4: Discussion Enhancement (Day 3-4)

**Action 4.1: Add Computational Efficiency Context**
- Include V4's 99.3% cost reduction claim as background
- Position V7 polypharmacology analysis as extension of efficient screening

**Action 4.2: Add Activity Cliff Discussion**
- Port V4's activity cliff assessment to V7 Limitations
- Acknowledge centroid-based sampling risks

**Action 4.3: Add Literature Positioning**
- Port V4's comparison with NtieKang 2018, Simoben 2020
- Add ANPDB coverage statistics (94.9% at Tanimoto ≥ 0.4)

**Action 4.4: Expand Named Lead Analysis**
- V7 needs detailed mechanistic profiles for top candidates
- Use V4's ligand 201/214/438 format as template
- Focus on PP-06, PP-11, PP-15 (mentioned in Phase 1 completion)

### Phase 5: Introduction Enhancement (Day 4)

**Action 5.1: Add Accessibility Gap Argument**
- Port V4's "1000 CPU-hours per target" accessibility barrier
- Emphasize 94% of malaria cases in endemic regions

**Action 5.2: Add Hybrid Pharmacophore Rationale**
- Strengthen NP+SD hybrid motivation
- Reference V4's scaffold preservation discussion

### Phase 6: Supplementary Material Enhancement (Day 5)

**Action 6.1: Port Key SM Tables**
Priority tables to adapt:
1. Computational cost comparison (V4 SM-tab:computational_comparison)
2. Redocking validation (V4 SM-tab:redocking_validation)
3. MMV validation (V4 SM-tab:mmv_validation) if applicable
4. Consensus filtering (V4 SM-tab:consensus) if V7 uses consensus

**Action 6.2: Port Key SM Figures**
Priority figures to copy:
1. VAE training curves (background validation)
2. UMAP latent space (optional, if space permits)
3. Clustering quality (optional, background validation)

---

## SECTION 8: DATA REQUIREMENTS FROM BMAD

To complete V7 tables, extract from `BMAD_Q1_DATA_ANALYSIS_REPORT.md`:

### 8.1 Set-C Candidate Data (17 molecules: PP-01 to PP-17)

**Required fields per candidate:**
- SMILES (canonical)
- Molecular weight, logP, HBD, HBA, TPSA, RB, fsp3
- Lipinski/Veber violations
- SYBA, NPL, SA, QED scores
- ADMET-AI predictions (11 endpoints)
- CYP450 inhibition (4 isoforms)
- SI_pred
- Ersilia predictions (eos7yti, eos7kpb, eos80ch)
- Vina scores (4 targets: PfDHFR, PfCRT, PfClpP, PfATP4)
- RRS, PNS, ACSI
- Bemis-Murcko scaffold
- Tanimoto to nearest seed NP

**Source:** Should be in BMAD P2 section or P1 V7 data files

### 8.2 Target-Specific Data

**For each of 4 targets (PfDHFR, PfCRT, PfClpP, PfATP4):**
- Grid box specifications (center coordinates, dimensions)
- Anchor residue definitions
- Redocking validation results (if available)
- Enrichment metrics (if available)

---

## SECTION 9: IMMEDIATE NEXT STEPS

### Step 1: Read BMAD to Locate Set-C Data
```
# Search BMAD for Set-C cohort data
grep -n "PP-01\|PP-02\|PP-03" BMAD_Q1_DATA_ANALYSIS_REPORT.md
grep -n "Set-C\|set_c" BMAD_Q1_DATA_ANALYSIS_REPORT.md
```

### Step 2: Check V7 Data Files
```
# List V7 results directory
ls -la Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/
```

### Step 3: Generate Missing Tables
- Use Python scripts to extract Set-C data from BMAD
- Format tables in LaTeX using V4 templates

### Step 4: Create Binding Mode Figures
- Extract docking poses for PP-01 to PP-17
- Generate 2D interaction diagrams using PyMOL/LigPlot+

### Step 5: Update V7 Main and SM
- Insert tables into V7 SM
- Add figures to V7 main Results section
- Enhance Discussion with V4 context

---

## SECTION 10: CRITICAL QUESTIONS TO ANSWER

1. **Does V7 have docking pose files for PP-01 to PP-17?**
   - If yes, generate interaction diagrams
   - If no, need to extract from docking output or BMAD

2. **Does V7 have ADMET data for Set-C cohort?**
   - Check if ADMET-AI was run on 17 candidates
   - If missing, need to generate

3. **Does V7 have enrichment validation for PfClpP?**
   - V4 has 3 targets, V7 adds 4th
   - Need to verify benchmarking

4. **What is V7's SM structure?**
   - How many tables/figures already exist?
   - Where to insert new content?

---

## END OF INVENTORY

**Next Action:** Read BMAD P2 section to locate Set-C cohort data and begin table generation.
