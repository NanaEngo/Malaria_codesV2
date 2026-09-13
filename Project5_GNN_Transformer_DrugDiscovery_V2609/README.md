# Project 5 (P5 V2609) — Deconstructing Out-of-Distribution Extrapolation in Molecular Deep Learning

**Status:** Framework and manuscript V2609 complete; submission-ready package for JCAMD / JCIM.
**Active DAR:** `P5_DATA_ANALYSIS_REPORT.md`
**Master Strategy Plan:** `P5_RestrV2609.md`
**ADR Record:** `docs/ADR_P5_STRATEGIC_PIVOT_V2609.md`
**Manuscript Package:** `manuscript/V2609/`

---

## 1. Central Research Question

> *Under chemical-distribution shift, how do structural complexity and representation topology dictate the out-of-distribution extrapolation limits of molecular neural networks versus sparse bit-ensembles, and can distance-aware uncertainty triage dynamically optimize virtual screening performance?*

---

## 2. Core Framework Pillars & Resolved Literature Gaps

```
+---------------------------------------------------------------------------------------------------+
| LITERATURE GAP                                   | P5 NOVELTY & SOLUTION                          |
+--------------------------------------------------+------------------------------------------------+
| 1. GNN failure attributed vaguely to atom count  | Fsp3 x Ring Count Structural Complexity Matrix |
|    or poor hyperparameter tuning                 | (Proves 1-WL over-smoothing; GIN-TFP +0.047)   |
|                                                  |                                                |
| 2. Benchmark papers lack actionable utility      | Executable ConformalTriageFilter Protocol      |
|    for medicinal/computational chemists          | (+14.2% virtual screening precision boost)     |
|                                                  |                                                |
| 3. Unclear if GNN drop is split-dependent        | Multi-Split Invariance & Capacity Sensitivity  |
|    or capacity-bound                             | (5 split families, Butina 0.55, h=64-256 grid) |
|                                                  |                                                |
| 4. Transformer benchmarks suffer from cross-fold | Normative Leakage-Free Transformer Protocol    |
|    weight leakage during cross-validation        | (Fold-independent weight restoration standard) |
|                                                  |                                                |
| 5. Ambiguity between direct target binding and   | Explicit Phenotype vs Structure Boundary       |
|    cellular multi-label phenotype profiles       | (Decoupled molecular P5 from cellular LISH/P6) |
+--------------------------------------------------+------------------------------------------------+
```

---

## 3. Key Findings

1. **Distance-Resolved Stratification (NN-Tanimoto D1–D10):** ECFP4-RF dominance is strictly confined to the structural extrapolation tail ($D_{\text{NN}} < 0.40$, deciles D1–D4). In mid-range interpolation regimes (D5–D8), deep learning models achieve statistical parity ($\Delta \in [0.001, 0.007]$).
2. **Topological Rescue Mechanism (GIN-TFP):** On complex 3D polycyclic natural products ($Fsp^3 \ge 0.45$, rings $\ge 4$), standard GIN drops to 0.768 due to 1-WL over-smoothing, whereas persistent-homology topological feature projections (GIN-TFP) restore performance to 0.815 (+0.047 gain), recovering 36% of the raw GNN deficit.
3. **Actionable Conformal Triage Filter:** A distance- and calibration-aware decision rule ($D_{\text{NN}} < 0.40 \to$ ECFP4-RF; $0.40 \le D_{\text{NN}} \le 0.60 \to$ GIN-TFP; $\mathrm{ECE} > 0.08$ confidence barrier) increases virtual screening precision by **+14.2%** on the 22,267 compound ChEMBL transfer panel.
4. **Leakage-Free Transformer Protocol:** Enforcing per-fold pretrained weight restoration eliminates artificial cross-fold information leakage during cross-validation.

---

## 4. Canonical Benchmark Summary

| Model | Random AUC | Scaffold AUC | Butina AUC (0.55) | Complex 3D ($Fsp^3 \ge 0.45$) |
|---|---:|---:|---:|---:|
| **ECFP4-RF** | **0.9433 ± 0.0003** | **0.8300 ± 0.0023** | **0.8331** | **0.825** |
| GIN-TFP (Topological) | 0.9084 ± 0.0012 | 0.8138 ± 0.0107 | 0.8232 | 0.811 (+0.038 gain vs GIN) |
| GIN-TNE (Tensor) | 0.8918 ± 0.0018 | 0.8090 ± 0.0149 | 0.8191 | 0.805 |
| GIN (Base) | 0.9098 ± 0.0022 | 0.8047 ± 0.0141 | 0.8202 | 0.773 (1-WL drop) |
| ChemBERTa | 0.9121 ± 0.0012 | 0.7867 ± 0.0054 | 0.7776 | 0.765 |

---

## 5. Canonical Directory Layout

```
Project5_GNN_Transformer_DrugDiscovery_V2609/
├── README.md                          # Master Project README
├── P5_DATA_ANALYSIS_REPORT.md         # Canonical Ground Truth Data Analysis Report
├── P5_RestrV2609.md                   # Canonical Master Strategic Plan V2609
├── P5_ZENODO_DEPOSIT_MANIFEST.txt     # Zenodo Deposit Inventory
├── project-tracking.md                # Project Tracking & Milestones
├── requirements.txt                   # Conda / Python dependencies
├── _archives/                         # Consolidated Project Archives
│   ├── docs/                          # Superseded strategy drafts and notes
│   ├── manuscript_V2608/              # Legacy V2608 manuscript files
│   └── scripts/                       # Legacy one-off scripts
├── docs/                              # Project Documentation & ADRs
│   └── ADR_P5_STRATEGIC_PIVOT_V2609.md
├── manuscript/                        # Publication Artifacts
│   ├── V2609/                         # Canonical JCAMD Manuscript Package
│   │   ├── Project5_GNN_Transformer_Antimalarial_main_V2609.tex
│   │   ├── Project5_GNN_Transformer_Antimalarial_main_V2609.pdf
│   │   ├── Project5_GNN_Transformer_Antimalarial_SM_V2609.tex
│   │   ├── Project5_GNN_Transformer_Antimalarial_SM_V2609.pdf
│   │   └── Project5_GNN_Transformer_Antimalarial_V2609.bib
│   ├── Cover_Letter_P5_JCAMD.tex       # Official Cover Letter
│   └── Cover_Letter_P5_JCAMD.pdf
├── results/                           # Benchmark & Replication Data
│   ├── canonical_panel/               # Primary 19,836 molecule dataset
│   ├── public_chembl/                 # External 22,267 molecule transfer panel
│   ├── figures/                       # Publication vector figures
│   ├── butina_cluster_20260829/
│   ├── calibration_20260827/
│   ├── extended_campaign_20260825/
│   ├── lightweight_robustness/
│   ├── lish_moa/
│   ├── nn_tanimoto_deciles_20260829/
│   └── replication_records/           # Raw 125 model fold-seed checkpoint logs
├── scripts/                           # Production Pipelines
│   ├── benchmarks/                    # Training and model evaluation scripts
│   ├── analysis/                      # Post-hoc statistical & decile analysis
│   └── hpc_sbatch/                    # SLURM cluster launcher scripts
└── outputs/                           # Generated Artifacts & Reviews
    ├── analysis/
    ├── critical-reviews/
    └── graphical_abstract/
```
