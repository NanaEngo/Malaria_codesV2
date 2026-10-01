# PhD Thesis Progress Map
**Title:** Quantum Machine Learning Approach for Malaria Drug Discovery  
**Author:** Vital SAO TEMGOUA  
**Target:** 150 pages  
**Current:** 76 pages (50.7% complete) ← **Updated after Chapter 3 results integration (28 Sept 2026)**

> **Chapter rebalance checkpoint (29 Sept 2026):** Chapters equalized at 24 pp each after the introduction restructure (Ch1: 1–24, Ch2: 25–48, Ch3: 49–72; document 96 pp). Additions were genuine content, not padding: Ch2 gained external-data versioning, the Wilson-interval rationale, the PNS formal definition (Eq. 2.x), and a Conclusion section (§2.9) on the Mbokop closing pattern; Ch3 gained the V2609C operational-guidance rules for resistance-aware triage (placed under §3.3 Resistance-aware scoring, where they belong) and a numbered Conclusion (§3.7). One residual "four projects" phrase fixed. Build: 96 pages, 0 errors, 0 undefined references.

> **Introduction structure checkpoint (29 Sept 2026):** Manuscript restructured on the Mbokop thesis model (`ThèseMbokop_V260112/Mbokop_ThesisV2509.tex`). General Introduction now follows the six-section pattern (Background of the study / Statement of the problem / Research questions / Aim and objectives / Significance / Organization of the thesis + Overview of the thesis argument), all in TOC. The previous narrative became the Background section; three new problem statements (representational, evaluative, resistance-aware) and five research questions were authored. Every chapter now opens with a numbered Introduction section with an explicit `\Cref`-based roadmap (1.1, 2.1, 3.1); the previously empty Chapter 1 introduction was written. Five hardcoded "Section X.Y.Z" references replaced with labelled `\Cref` cross-references; seven section labels added to Ch2, five to Ch3. cleveref chapter/section names configured in the preamble. Build: 94 pages, 0 errors, 0 undefined references.

> **Terminology + equalization checkpoint (29 Sept 2026):** (1) All "Project N" / standalone "PN" references removed from the manuscript body (Gen_intro, chap_lit_rev, chap_to_met, chap_res_dis); studies are now referred to descriptively (chemical-space study, resistance-scoring study, representation study, learned-representation study, quantum machine learning programme). (2) Three companion-study ChemRxiv DOIs added to `Bib_thesis_SAO.bib` and cited in Chapter 1: `Temgoua2026Grids` (10.26434/chemrxiv.15006437/v2), `Temgoua2026Topological` (10.26434/chemrxiv.15007167/v1), `Temgoua2026Pareto` (10.26434/chemrxiv.15007306/v1); 12 methodology references also added (Bickerton QED, SYBA, Ertl NPL, DiffDock, SWISS-MODEL, ProLIF, STRING, GROMACS, CHARMM36m, gmx_MMPBSA, MDAnalysis, ETKDG/RDKit). (3) Chapter 2 expanded 13→22 pages with genuinely missing methods content (prioritisation-term declarations, DiffDock consensus estimator, multi-seed + perturbation audits, PfCRT K76 restoration rationale, candidate selection cascade, estimand architecture + reference controls, eligibility-rule rationale, PNS robustness checks, conformer governance, kernel diagnostic hierarchy, MD cohort table, MM-GBSA decomposition + noise floor, ProLIF contact-level complement, label provenance, cohort chemical-space characterisation, compute environment + software table, enrichment-ceiling mechanics, conformal calibration + distance-aware triage rule, power analysis, hyperparameter governance, uncertainty taxonomy + formal test mechanics, claim-ledger convention, docking/MD/RRS-class summary tables). Chapter spans now equalized: Ch1 22 pp (1–22), Ch2 22 pp (24–45), Ch3 23 pp (46–68); total document 90 pp. Build: 0 errors, 0 undefined references, `git diff --check` clean.

> **V2609C figure refresh (29 Sept 2026):** Three P2 thesis figures were stale pre-V2609C versions and have been replaced with the canonical V2609C assets (checksums verified): `p2_rmsd_stability.pdf` ← `Figure3_RMSD_Stability.pdf` (nm axes, canonical R1 labels), `p2_prolif_heatmaps.pdf` ← `Figure4_ProLIF_Heatmaps.pdf` (canonical hotspot panels), `p2_cross_metric_correlation.pdf` ← `cross_metric_correlation.pdf` (declared 4-pair chart, replaces old 8×8 heatmap). RMSD and cross-metric captions rewritten to match; ProLIF caption already canonical.

> **V2609C integration checkpoint (29 Sept 2026):** Chapter 3 P2 section realigned to the canonical P2 manuscript `Project2_.../manuscript/V2609C/`: corrected PP-01 RMSD figure-caption values (backbone/ligand in Å from canonical R1), corrected ProLIF caption (Tyr16 100% occupancy in 5/6 PfCRT systems; Asp54/Leu46/Met55/Ile14 hotspots), added the 16-system Set-C MM-GBSA endpoint table (SD_prop convention) + PP-01 biophysical audit paragraph, added the retrospective ChEMBL genotype–phenotype fold-shift confrontation (28 compounds, ρ −0.13..0.19, direction agreement 28.6–41.7%), added the GNINA near-degenerate-agreement caveat, and added STRING-threshold (400/700/900) and ACSI ±20% weight sensitivity. Chapter 2 methods gained: GNINA/QuickVina cross-scoring subsection, retrospective ChEMBL confrontation protocol, and the MD-RRS_d distance-ratio definition. Chapter 1 lit review updated with estimand-divergence framing. P5 sections verified already claim-calibrated (commit 46926a4bd).

> **Scope note (28 Sept 2026):** The thesis now covers **five projects: P1, P2, P3, P5, P7**.
> P4 (MCTS/Pareto multi-objective optimization) and P6 (LISH-MoA phenotype baseline) have been
> removed from the manuscript — their results already belong to companion publications and must not
> be re-used here. P7 (true QML via QMSE) is in scope with framing only; its methods and results
> sections are yet to be written and its status remains NOT_COMPUTED until canonical runs exist.

## Thesis Structure

```
PhD_SAO_V250404.tex (Main File)
│
├── Front Matter (~5 pages)
│   ├── Cover Page ✅
│   ├── Table of Contents ✅
│   ├── List of Figures ✅
│   └── List of Tables ✅
│
├── General Introduction (~3 pages)
│   └── Gen_intro.tex ⏳ To review
│
├── Chapter 1: Literature Review (~30-35 pages) ✅ ENHANCED
│   ├── chap_lit_rev.tex (320 lines, up from 193)
│   │
│   ├── 1. Malaria Drug Discovery Background ✅
│   │   ├── 1.1 Overview of malaria biology
│   │   ├── 1.2 Pharmaceutical drug discovery process
│   │   ├── 1.3 Current treatments
│   │   └── 1.4 Emerging resistance issues
│   │
│   ├── 2. Natural Products in Drug Discovery ✅
│   │   ├── 2.1 Natural products as drugs
│   │   ├── 2.2 Successes of natural products
│   │   └── 2.3 Computational methods for NP analysis
│   │
│   ├── 3. Machine Learning in Drug Discovery ✅
│   │   ├── 3.1 Types of ML techniques
│   │   └── 3.2 Limitations in high-dimensional data
│   │
│   ├── 4. Quantum Computing Fundamentals ✅
│   │   └── 4.1 Quantum computing concepts
│   │
│   ├── 5. Quantum Machine Learning ✅ NEW ENHANCED
│   │   ├── 5.1 Recent QML algorithms
│   │   └── 5.2 Quantum applications for malaria
│   │
│   ├── 6. Computational Drug Discovery Methods ✅ NEW SECTION
│   │   ├── 6.1 Molecular docking (P1/P2 integrated)
│   │   ├── 6.2 Molecular dynamics (P2 integrated)
│   │   ├── 6.3 Chemical space exploration (P1 integrated)
│   │   └── 6.4 Resistance-resilient scoring (P2 integrated)
│   │
│   ├── 7. Molecular Representations for ML ✅ NEW SECTION
│   │   ├── 7.1 Classical fingerprints (P3/P5 baseline)
│   │   ├── 7.2 Graph neural networks (P5 honest-negative)
│   │   └── 7.3 Topological/quantum descriptors (P3 integrated)
│   │
│   ├── 8. Generative Models ✅ NEW SECTION
│   │   ├── 8.1 VAEs and GANs
│   │   └── 8.2 RL and multi-objective optimization
│   │
│   ├── 9. Integration of Workflows ✅ NEW SECTION
│   │   ├── 9.1 Validation cascades
│   │   └── 9.2 Prospective vs retrospective validation
│   │
│   └── 10. Conclusions and Future Perspectives ✅ NEW SECTION
│       └── Comprehensive synthesis of P1–P3, P5, and P7 findings
│
├── Chapter 2: Tools and Methods (~40 pages) ✅ **ENHANCED**
│   ├── chap_to_met.tex (850 lines, comprehensive)
│   │
│   ├── Implemented Sections ✅:
│   │   ├── 2.1 Chemical Space Construction (P1)
│   │   │   ├── Hybrid library construction (JT-VAE)
│   │   │   ├── Target selection (PfDHFR, PfCRT, PfATP4, PfClpP)
│   │   │   └── Physicochemical filtering
│   │   │
│   │   ├── 2.2 Molecular Docking Protocols (P1)
│   │   │   ├── AutoDock Vina methodology
│   │   │   ├── Docking validation (V7)
│   │   │   └── DEKOIS 2.0 benchmark
│   │   │
│   │   ├── 2.3 RRS and Polypharmacology (P2)
│   │   │   ├── Resistance-resilient score computation
│   │   │   ├── Polypharmacology network scoring
│   │   │   └── ACSI chemical space positioning
│   │   │
│   │   ├── 2.4 Molecular Dynamics Methods (P2)
│   │   │   ├── System preparation (OpenFF 2.2.0)
│   │   │   ├── Equilibration protocols (3-stage NPT)
│   │   │   └── MM-GBSA binding free energy
│   │   │
│   │   ├── 2.5 Molecular Descriptors (P3)
│   │   │   ├── ECFP4 baseline
│   │   │   ├── Topological fingerprints (GUDHI)
│   │   │   └── Quantum kernel similarity (Qiskit)
│   │   │
│   │   ├── 2.6 ML/DL Architectures (P3, P5)
│   │   │   ├── Random forest baseline (scikit-learn)
│   │   │   ├── Graph Isomorphism Networks (GIN)
│   │   │   └── Transformer architectures
│   │   │
│   │   └── 2.7 Statistical Validation (All projects)
│   │       ├── Cross-validation protocols
│   │       ├── Performance metrics (ROC-AUC, EF1%)
│   │       └── Multiple hypothesis testing
│   │
│   └── Delivered: 11 pages (comprehensive 8-section methodology)
│
├── Chapter 3: Results and Discussion (~21 pages so far) ✅ **CANONICAL RESULTS INTEGRATED**
│   ├── chap_res_dis.tex
│   │
│   ├── Implemented Sections ✅:
│   │   ├── 3.1 Chemical space construction and target-anchored docking
│   │   │   ├── Scaffold-guided expansion (novelty vs scaffold recovery)
│   │   │   ├── Four-target docking profile + protocol validation
│   │   │   └── Mutation resilience, joint prioritization, cross-metrics
│   │   ├── 3.2 Resistance-aware scoring and the static-to-dynamic estimand
│   │   │   ├── Cohort scope, class counts, threshold sensitivity
│   │   │   ├── Estimand divergence (7/8 matched mutant states)
│   │   │   ├── Parent-study MD stability and MM-GBSA feasibility
│   │   │   └── Interaction-fingerprint hotspots
│   │   ├── 3.3 Quantum-inspired and topological representations
│   │   │   ├── Scaffold-paradox decomposition (H0/H1)
│   │   │   ├── Tensor-network compression and information retention
│   │   │   ├── Activity benchmark + hybrid ablation
│   │   │   ├── Quantum kernel vs tuned RBF
│   │   │   ├── ECFP4-inclusive fusion and ChEMBL transfer
│   │   │   └── Scaffold-grouped re-evaluation + TDA/docking cross-link
│   │   ├── 3.4 Learned representations under chemical distribution shift
│   │   │   ├── Three partition families (random / scaffold / Butina)
│   │   │   ├── Distance-resolved deficit + structural cohorts
│   │   │   └── Topological salience and metric degeneracy
│   │   └── 3.5 Synthesis: the comparison standard for Project 7
│   │
│   └── Target: 50 pages (remaining: expanded discussion, P7 methods/results)
│
├── General Conclusion (~5 pages) ⏳ TO ENHANCE
│   └── Gen_con.tex
│
├── Bibliography (~15 pages) ⏳ TO COMPILE
│   └── Bib_thesis_SAO.bib
│
└── Appendices (~5-10 pages) 📋 OPTIONAL
    ├── Supplementary Tables
    ├── Extended Candidate Lists
    ├── Code Snippets
    └── Additional Figures
```

## Project Integration Map

```
┌─────────────────────────────────────────────────────────────┐
│                    THESIS CHAPTERS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Chapter 1 (Lit Review) ✅                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ P1: Chemical space (65,856 mol, 4 targets)          │   │
│  │ P2: RRS + polypharmacology (17 candidates)          │   │
│  │ P3: Quantum descriptors (QKS ≈ RBF)                 │   │
│  │ P5: GNN < ECFP4 (scaffold split)                    │   │
│  │ P7: True QML via QMSE (framing; NOT_COMPUTED)       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Chapter 2 (Methods) ⏳                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Detailed protocols for P1-P3, P5, P7                 │   │
│  │ Docking/MD/ML/QML methodologies                      │   │
│  │ Statistical frameworks                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Chapter 3 (Results) ⏳                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Comprehensive P1-P3/P5 results + P7 framing          │   │
│  │ Figures, tables, statistical analyses               │   │
│  │ Cross-project comparisons                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Page Count Projection

| Component | Current | Target | Status |
|-----------|---------|--------|--------|
| Front Matter | 5 | 5 | ✅ Complete |
| General Intro | 3 | 5 | ⏳ Review needed |
| **Chapter 1** | **~15** | **30-35** | ⏳ Aligned to canonical values |
| **Chapter 2** | **~15** | **40** | ⏳ Aligned to canonical protocols |
| Chapter 3 | ~21 | 50 | ⏳ **Canonical results integrated; expansion pending** |
| General Conclusion | ~2 | 5 | ⏳ Expand |
| Bibliography | 0 | 15 | ⏳ Compile needed |
| Appendices | 0 | 5-10 | 📋 Optional |
| **TOTAL** | **76** | **150** | **50.7% complete** |

## Enhancement Roadmap to 150 Pages

### ✅ Phase 1: Chapter 1 Enhancement (COMPLETE)
- [x] Integrate P1–P3, P5 findings (P7 framing only)
- [x] Add computational methods sections
- [x] Add molecular representations section  
- [x] Add generative models section
- [x] Add validation workflows section
- [x] Write comprehensive conclusions
- [x] Maintain scientific rigor and honest-negative reporting
- [x] Compile successfully (43 pages)

### ⏳ Phase 2: Chapter 2 Enhancement (NEXT PRIORITY)
**Target:** +35 pages (43 → 78 pages total)

Detailed methodology sections for:
- [ ] P1: Docking protocols (AutoDock Vina, grid parameters, scoring)
- [ ] P1: Chemical space generation (hybrid library construction)
- [ ] P2: MD simulation protocols (force fields, equilibration, production)
- [ ] P2: RRS computation methodology
- [ ] P3: Quantum descriptor calculation (QKS, TFP, TNE)
- [ ] P3: Machine learning protocols (ECFP4, RF, hybrid models)
- [ ] P7: QMSE/BondFeatureMap methods section (to be written; framing only for now)
- [ ] P5: GNN architectures (GIN, ChemBERTa implementation)
- [ ] P5: Training protocols (scaffold splits, cross-validation)
- [ ] Statistical analysis frameworks
- [ ] Validation methodologies

### ✅ Phase 3a: Chapter 3 canonical results integration (COMPLETE, 28 Sept 2026)
- [x] P1 results: expansion statistics, four-target docking validation, RRS classes, cross-metrics
- [x] P2 results: class counts, threshold sensitivity, estimand divergence, MD stability, ProLIF
- [x] P3 results: scaffold paradox, TNE compression/regression, benchmark + ablation, quantum kernel, fusion, transfer, scaffold-grouped re-evaluation, TDA cross-link
- [x] P5 results: three partition families, distance-resolved deficit, structural cohorts, salience
- [x] Cross-project synthesis + Project 7 comparison standard (framing only)
- [x] Figures/tables harvested from canonical project directories (see inventory below)
- [x] Chapter 1 and Chapter 2 realigned to canonical protocols and values

### ⏳ Phase 3b: Chapter 3 expansion (remaining ~29 pages)
- [ ] Full per-mutant and per-target supplementary tables
- [ ] Extended discussion of ensemble retention and label-source limits
- [ ] Project 7 methods and results (NOT_COMPUTED; framing only until canonical runs exist)

## Chapter 3 figure and table inventory (harvested 28 Sept 2026)

All assets were copied from the canonical project directories into `My_PhD_Thesis/Graphics/`.

| Thesis asset | Source | Project |
|---|---|---|
| `p1_v7_chemical_space_coverage.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p1_v7_targetwise_profile_summary.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p1_v7_rrs_mutation_profiles.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p1_v7_exploratory_metric_relationships.pdf` | `.../Submission_JCAMD/Graphics/` | P1 |
| `p2_workflow.pdf` (from `p2_preview-1.pdf`) | `V2609C/Graphics/` | P2 |
| `p2_rmsd_stability.pdf` | `V2609C/Graphics/` | P2 |
| `p2_prolif_heatmaps.pdf` | `V2609C/Graphics/` | P2 |
| `p2_cross_metric_correlation.pdf` | `V2609C/Graphics/` | P2 |
| `p3_scaffold_paradox.pdf` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_persistence_diagrams.pdf` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_tensor_compression.pdf` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_tne_regression_summary.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_qkernel_benchmark.pdf` (from `applicability_domain.pdf`) | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_extval_internal_vs_external.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_tda_promiscuity.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p3_h1_rrs_violin.png` | `manuscript/LaTeX/Graphics/` | P3 |
| `p5_auc_benchmark.png` | `manuscript/V2609/figures/` | P5 |
| `p5_structural_complexity.png` | `manuscript/V2609/figures/` | P5 |
| `p5_salience.png` | `manuscript/V2609/figures/` | P5 |

Tables authored natively in Chapter 3 from the canonical result tables: P1 docking validation,
P1 per-candidate RRS classes, P2 MD stability metrics, P3 activity benchmark and hybrid ablation,
P5 three-partition benchmark, P5 structural-complexity cohorts.

### ⏳ Phase 4: Supporting Components
**Target:** +20 pages (123 → 143 pages total)

- [ ] Expand General Introduction (3 → 5 pages)
- [ ] Expand General Conclusion (2 → 5 pages)
- [ ] Compile bibliography with biber (0 → 15 pages)
- [ ] Add appendices (optional, 5-10 pages):
  - Extended candidate lists
  - Supplementary tables
  - Code snippets/pseudocode
  - Additional validation figures

### ⏳ Phase 5: Final Refinement
**Target:** 150 pages

- [ ] Final LaTeX compilation with bibliography
- [ ] Resolve all cross-references
- [ ] Verify figure/table numbering
- [ ] Proofread all chapters
- [ ] Ensure consistent notation
- [ ] Check page count distribution
- [ ] Final PDF generation

## Key Accomplishments (Chapter 1)

### Scientific Integrity Maintained
- ✅ **Honest-negative reporting:** P3 and P5 null/negative results presented transparently
- ✅ **Provenance boundaries:** Computational predictions clearly distinguished from experimental validation
- ✅ **No fabrication:** All numbers from canonical DARs
- ✅ **No overclaiming:** Quantum advantage not claimed; GNN limitations acknowledged

### Writing Quality Standards
- ✅ **Full paragraphs:** No bullet points in final text
- ✅ **Flowing prose:** Proper transitions and sentence variety
- ✅ **Anti-AI patterns avoided:** No "delve," "elucidate," "underscore," etc.
- ✅ **Citations integrated:** Natural in-text citations, not lists
- ✅ **Scientific tone:** Mechanistically grounded, precise language

### Technical Quality
- ✅ **LaTeX compilation:** 0 fatal errors
- ✅ **Cross-references:** All labels resolved
- ✅ **Figure integration:** References to existing P1–P3/P5 figures
- ✅ **Table references:** Citations to canonical result tables

## Timeline Estimate for Completion

| Phase | Estimated Time | Pages Added | Running Total |
|-------|---------------|-------------|---------------|
| Phase 1 (Ch 1) | ✅ Complete | +5-8 | 43 |
| Phase 2 (Ch 2) | 3-5 days | +35 | 78 |
| Phase 3 (Ch 3) | 5-7 days | +45 | 123 |
| Phase 4 (Support) | 2-3 days | +20 | 143 |
| Phase 5 (Refine) | 1-2 days | +7 | 150 |
| **TOTAL** | **11-17 days** | **+107** | **150** |

## Files Created/Modified

1. **Modified:**
   - `My_PhD_Thesis/Chapters/chap_lit_rev.tex` (193 → 320 lines)

2. **Created:**
   - `My_PhD_Thesis/CHAPTER1_ENHANCEMENT_SUMMARY.md` (this summary)
   - `My_PhD_Thesis/THESIS_PROGRESS_MAP.md` (this roadmap)

3. **Compiled:**
   - `My_PhD_Thesis/PhD_SAO_V250404.pdf` (43 pages)

## Next Immediate Actions

1. **Bibliography compilation:**
   ```bash
   cd My_PhD_Thesis
   pdflatex PhD_SAO_V250404.tex
   biber PhD_SAO_V250404
   pdflatex PhD_SAO_V250404.tex
   pdflatex PhD_SAO_V250404.tex
   ```

2. **Chapter 2:** ✅ aligned to canonical P1/P2/P3/P5 protocols (target IDs, docking parameters, RRS definition and classes, ACSI definition, PNS source, force fields, descriptors, GIN/transformer settings, partition families). Remaining: P7 QML methods section once the protocol is frozen.

3. **Chapter 3:** ✅ canonical P1–P3/P5 figures and tables integrated with the synthesis that sets the Project 7 comparison standard. Remaining: expanded discussion, per-mutant supplementary tables, P7 results section (NOT_COMPUTED — no claims until canonical runs).

4. **Generate figures:** Create schematics for any new sections using the scientific-schematics skill.

---

**Status:** Chapter 3 canonical results integrated (28 Sept 2026). Build clean: 76 pages, 0 LaTeX errors, 0 undefined references/citations. Next priority is Chapter 3 expansion and the Project 7 methods section.
