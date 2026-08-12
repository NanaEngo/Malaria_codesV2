# V4 MPO and DiffDock Content Analysis for V7 Integration

**Date:** 11 January 2026  
**Purpose:** Compare V4's detailed MPO and DiffDock content against V7 to identify what should be added to V7 manuscript

---

## Executive Summary

**V4 contains extensive MPO and DiffDock mathematical formulations and methodology that are NOT present in V7.**

V7 currently mentions MPO and DiffDock only in passing:
- Abstract: "Multi-parameter optimization combined docking-derived scores, DiffDock confidence, QED, an ADMET composite, and a Lipinski penalty"
- Methods validation subsection: "consensus Vina+DiffDock ROC-AUC 0.924-1.000"
- SM Section S11: MMV enrichment validation using consensus scores

**What V7 is MISSING from V4:**
1. Complete MPO mathematical framework (5 equations + weight rationale)
2. DiffDock confidence transformation formula (logistic sigmoid)
3. Component weight justification (35% Vina, 25% DiffDock, 20% QED, 15% ADMET, 5% Ro5)
4. Polypharmacology bonus equation
5. MPO sensitivity analysis methodology and results
6. Centroid-based screening workflow linked to MPO
7. NP-relatedness filtering methodology
8. Full MPO sensitivity table (SM Table S17)

---

## Detailed Content Comparison

### 1. MPO Mathematical Framework

#### **V4 Main Text (Section "MPO framework and multi-target analysis")**

```latex
A continuous multi-parameter optimization (MPO) framework was applied, integrating five normalized components:
\begin{enumerate}
    \item $S_{\text{vina}}$ (\qty{35}{\percent} weight): Vina binding affinity, min-max scaled.
    \item $S_{\text{diff}}$ (\qty{25}{\percent} weight): DiffDock confidence, transformed via logistic sigmoid.
    \item $S_{\text{qed}}$ (\qty{20}{\percent} weight): Quantitative Estimate of Drug-likeness.
    \item $S_{\text{admet}}$ (\qty{15}{\percent} weight): Composite index aggregating \num{11} parameters.
    \item $P_{\text{Ro5}}$ (\qty{5}{\percent} weight): Penalty term for Lipinski violations.
\end{enumerate}
Sensitivity analysis across \num{25} weight perturbations...
```

**V7 Current Status:** Only mentions "Multi-parameter optimization combined docking-derived scores, DiffDock confidence, QED, an ADMET composite, and a Lipinski penalty" - NO equations, NO component details

---

#### **V4 SM: Complete MPO Section with All Equations**

V4 SM contains a full "Multi-parameter optimization scoring function" section with:

1. **Total MPO equation:**
```latex
\text{MPO}_{\text{total}, i} = \sum_{k=1}^{5} w_k \cdot S_{k,i} + \text{Polypharmacology Bonus}_i
```

2. **Component 1 - Vina (35%):**
```latex
S_{\text{vina}, i} = \frac{\text{Vina}_i - \text{Vina}_{\min}}{\text{Vina}_{\max} - \text{Vina}_{\min}}
```
Plus rationale for linear scaling vs exponential/power-law.

3. **Component 2 - DiffDock (25%):**
```latex
S_{\text{diff}, i} = \frac{1}{1 + e^{-c_i}}
```
Plus rationale for sigmoidal mapping over linear.

4. **Component 3 - QED (20%):**
```latex
S_{\text{qed}, i} = \text{QED}_i
```
Direct use without transformation.

5. **Component 4 - ADMET (15%):**
```latex
S_{\text{admet}, i} = \frac{1}{11} \sum_{m=1}^{11} d_m(\text{ADMET}_{i,m})
```
With list of 11 endpoints (HIA, solubility, Caco-2, BBB, hERG, AMES, DILI, SA, P-gp, CYP, clearance).

6. **Component 5 - Ro5 Penalty (5%):**
```latex
P_{\text{Ro5}, i} = 1 - 0.2 \cdot n_{\text{violations}, i}
```
With explicit penalty scale (0 violations = 1.0, 1 = 0.8, etc.).

7. **Polypharmacology bonus:**
```latex
\text{Polypharmacology Bonus}_i = 0.05 \cdot (n_{\text{targets}, i} - 1) \quad \text{if } n_{\text{targets}, i} \geq 2
```
Capped at +0.10 (3 targets).

**V7 Current Status:** NONE of these equations appear in V7 main or SM.

---

### 2. Weight Selection Rationale

#### **V4 SM Section: "Weight selection rationale"**

Full paragraph justifying the 35/25/20/15/5 split:
- 35% Vina: "prioritizes the physics-inspired docking signal as the primary filter"
- 25% DiffDock: "complementary computational screening signal" 
- Combined 60% for docking: "reflects the central role of target engagement"
- 20% QED: "substantial weight to ensure compounds satisfy oral bioavailability criteria"
- 15% ADMET: "addresses early-stage toxicity concerns"
- 5% Ro5: "modest weight... Ro5 compliance already captured partially within QED"

**V7 Current Status:** No weight rationale provided anywhere.

---

### 3. MPO Sensitivity Analysis

#### **V4 SM: Full methodology section**

```latex
\subsection*{Framework limitations and sensitivity}
\label{sec:mpo_sensitivity_methods}

\textbf{Sensitivity methodology.} The five MPO component scores comprise S$_{\text{vina}}$...
[Full explanation of back-calculation method, perturbation protocol, etc.]

Formal sensitivity analysis across \num{25} weight perturbations ($\pm \qtyrange{10}{20}{\percent}$ per component) 
yielded mean Spearman rank correlation $\rho = \num{0.792}$ for the top-1,000 compounds and mean Jaccard 
similarity of \num{0.548} for the top-20 hit list, indicating moderate sensitivity to weight choice 
(\cref{tab:sm_s17_mpo_sensitivity}). When both stability criteria (top-1000 $\rho > \num{0.95}$ 
and top-20 Jaccard $\geq \num{0.70}$) are required, only \qty{5}{\percent} of non-baseline perturbations passed...
```

Plus **V4 SM Table S17: MPO weight sensitivity analysis** with 25 perturbations showing:
- Spearman ρ for top-1000
- Jaccard for top-20
- Pass/fail for both criteria

**V7 Current Status:** No sensitivity analysis in main or SM.

---

### 4. Centroid-Based Screening Workflow

#### **V4 SM: "Centroid-based screening and MPO stratification"**

Full 5-step workflow:
1. K-Means clustering → 484 centroids
2. Consensus docking (Vina + DiffDock) → EXCELLENT/GOOD/OTHERS
3. MPO scoring → 93 centroids passed
4. Optimization-worthy threshold (MPO ≥ 0.40) → 76 centroids
5. Scaffold expansion → 53 clusters → 40,481 molecules → 19,913 synthesizable leads

With explicit linkage: "This centroid-based strategy reduced computational cost by \qty{99.3}{\percent} compared to exhaustive library-scale docking"

**V7 Current Status:** Methods mention "Variational autoencoders... identify cluster representatives and synthesize structures," but NO explicit MPO-driven filtering workflow described.

---

### 5. NP-Relatedness Filtering

#### **V4 SM: "Natural product relatedness filtering"**

Full methodology:
- Tanimoto ≥ 0.4 to any of 396 seed African NPs
- Morgan fingerprints (radius 2, 2048 bits)
- Among 76 optimization-worthy centroids: 13 (17.1%) NP-related, 63 (82.9%) structurally distinct
- "This dual population supports two computational lead-optimization strategies..."

Plus **V4 SM Table: "African natural product-related optimization candidates"** showing:
- Secondary Hits (MPO ≥ 0.50): 7 total, 2 NP-related (28.6%), mean Tanimoto 0.52
- Promising Scaffolds (MPO 0.40–0.50): 69 total, 11 NP-related (15.9%), mean Tanimoto 0.48
- **All Optimization Candidates: 76 total, 13 NP-related (17.1%), mean Tanimoto 0.49**

**V7 Current Status:** Main text mentions "scaffold recovery was \qty{69.3}{\percent}" but NO explicit NP-relatedness filter or Tanimoto threshold described.

---

### 6. DiffDock Confidence Transformation

#### **V4 Main Text:**
"DiffDock (\num{40} poses/ligand)"  
"Dual-filter thresholds: EXCELLENT (Vina $\leq \qty{-7.0}{\kilo\calorie\per\mole}$ AND DiffDock $\geq \num{0.0}$), GOOD (Vina $\qtyrange{-7.0}{-5.0}{\kilo\calorie\per\mole}$ AND DiffDock $\geq \num{-1.5}$)"

#### **V4 SM:**
```latex
\subsection*{Component 2: DiffDock confidence ($S_{\text{diff}}$, \qty{25}{\percent})}

The DiffDock confidence score is transformed via a logistic sigmoid function to map structural 
log-odds to probabilistic desirability:
\begin{equation}
S_{\text{diff}, i} = \frac{1}{1 + e^{-c_i}}
\label{eq:diffdock}
\end{equation}
where $c_i$ is the DiffDock confidence score for compound $i$ \cite{Corso2023}. This transformation 
ensures that high-confidence poses ($c > \num{0}$) receive scores approaching \num{1.0}, while 
low-confidence poses ($c < \num{-1.5}$) receive scores approaching \num{0}. The sigmoidal mapping 
was chosen over linear scaling because DiffDock confidence scores follow a non-uniform distribution 
with a sharp transition around $c = \num{0}$...
```

**V7 Current Status:** Only "consensus Vina+DiffDock ROC-AUC 0.924-1.000" mentioned - NO confidence transformation formula, NO dual-filter thresholds explicitly defined.

---

## Recommendation: What to Add to V7

### Option 1: Minimal Integration (Main Text Only)
Add brief MPO framework description to Methods, similar to V4 main text section "MPO framework and multi-target analysis":
- List 5 components with weights
- Mention dual-filter thresholds (EXCELLENT/GOOD)
- Reference full equations in SM

**Estimated addition:** ~1 paragraph in Methods (~150 words)

---

### Option 2: Comprehensive Integration (Main + SM)
**Main Text additions:**
1. Expand chemical-space funnel subsection to include MPO component list
2. Add dual-filter threshold definitions to target-anchored docking subsection

**SM additions (NEW Section):**
3. Full MPO scoring function section with all 7 equations (similar to V4 SM)
4. Weight selection rationale
5. Centroid-based screening workflow linked to MPO
6. MPO sensitivity analysis methodology
7. NP-relatedness filtering methodology
8. New SM Table: MPO sensitivity (25 perturbations)
9. New SM Table: NP-related optimization candidates

**Estimated addition:** 
- Main: ~2 paragraphs (~300 words)
- SM: ~3 pages + 2 tables

---

### Option 3: V7-Specific Hybrid Approach
Given that V7 focuses on the **polypharmacology cohort (Set C)** rather than the full library screening, we could:

1. **Keep V7's streamlined narrative** (it already mentions MPO in abstract/methods)
2. **Add a NEW SM section** that cross-references V4 for the MPO framework details:
   - "The MPO framework used for upstream candidate selection is detailed in the companion manuscript (Temgoua et al., Chemical Space, submitted). Briefly, the framework integrated..."
   - Include only the 5 component equations and weight table
   - Add explicit statement: "Set C candidates were selected from the MPO ≥ 0.40 optimization-worthy tier"

**Estimated addition:** 
- Main: 0 words (already sufficient)
- SM: ~1 page (equations + brief context)

---

## Evidence Boundary Considerations

V7's current approach is **deliberately more cautious** than V4:
- V7: "all \num{68} candidate--target pairs passed the geometrical anchor gate" (emphasis on structural anchors, NOT MPO scores)
- V7: "The resulting Vina values are target-specific scoring-function estimates, not experimental free energies"
- V7: Does NOT use phrases like "secondary hits" or "optimization-worthy"

**If we add V4's MPO content to V7, we should:**
1. Keep V7's cautious framing (computational prioritization, NOT hit quality claims)
2. Use past tense: "Candidates **were selected** from MPO ≥ 0.40 tier" (not "are high-quality hits")
3. Emphasize that MPO was an **upstream filter** for Set C selection, NOT a validation of Set C quality
4. Cross-reference the companion manuscript for full MPO validation

---

## Files Modified (if Option 2 or 3 chosen)

1. `P1_V7_Integrated_Polypharmacology_RRS.tex` (main)
   - Potentially expand Methods subsections

2. `P1_V7_Integrated_Polypharmacology_RRS_SM.tex` (SM)
   - Add new section after current S11 (validation) or before tables
   - Add 1-2 new tables

3. New table files in `manuscript/tables/`:
   - `sm_table_mpo_sensitivity.tex` (if adding sensitivity analysis)
   - `sm_table_np_related_candidates.tex` (if adding NP-relatedness)

---

## Next Steps

**USER DECISION REQUIRED:**

Which integration approach should we pursue?

- **Option 1** (Minimal): ~1 paragraph in main Methods, no SM additions → maintains V7's streamlined focus
- **Option 2** (Comprehensive): Full MPO section in SM + main text expansions → matches V4's detail level
- **Option 3** (Hybrid): Brief SM section cross-referencing V4 + upstream filter statement → balances detail with V7's narrative

**My recommendation:** Option 3 (Hybrid)
- Respects V7's target-anchored focus (not library-scale screening focus)
- Provides transparency about Set C selection methodology
- Avoids duplicating V4 content unnecessarily
- Maintains V7's cautious evidence boundary framing
