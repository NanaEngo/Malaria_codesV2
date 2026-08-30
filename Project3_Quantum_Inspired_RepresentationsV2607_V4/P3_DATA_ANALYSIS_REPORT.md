# P3 — Data Analysis Report (canonical)

**Project**: Project 3 — Quantum-inspired molecular representations (TFP / TNE / QKS) for African antimalarial candidates
**Canonical directory**: `Project3_Quantum_Inspired_RepresentationsV2607_V4/`
**Manuscript target**: *J. Cheminformatics* / *Nat. Comput. Sci.* (TBD)
**Conda environment**: `malaria_md` (Python 3.11, PennyLane 0.45.1, TensorLy 0.9.0, Ripser.py)
**Author**: Myke Vital Sao Temgoua
**Last refreshed**: 2026-08-29
**Status**: V2608 manuscript ready; benchmarks complete; Zenodo DOI reserved (`10.5281/zenodo.19608875`), upload pending

> **Canonical scope rule.** This is the only P3 DAR. The P3 V4 directory is the
> canonical release of P3. The legacy directories `Project3_Quantum_Inspired_RepresentationsV2607/`
> (V1) and `Project3_Quantum_Inspired_RepresentationsV2607_V2/` were moved to
> `_archives/P3_V2607_archived_20260829/` and `_archives/P3_V2607_V2_archived_20260829/`
> on 2026-08-29; their manuscripts are superseded by the V2608 main + SM in
> P3 V4. V1's `manuscript/LaTeX/archive/` is preserved inside the V1 archive
> for historical reference. The P3 V4 ZENODO manifest points its
> `canonical_manifest` to the V1 (now-archived) JSON as the historical source of
> truth; see §11 for a note on the pointer.

---

## 1. Executive summary

P3 benchmarks topological and quantum-inspired molecular representations
against classical fingerprints on \num{19849} African antimalarial candidates
with computationally predicted activity labels. Three non-classical
representations are evaluated:

1. **TFP** — Topological Fingerprint (persistent homology, 84 features
   per molecule).
2. **TNE** — Tensor Network Embedding (Tucker rank (8,8,3) → 192-dim,
   6.1× real-atom compression, reconstruction error 0.113).
3. **QKS** — simulated Quantum Kernel Score (8-qubit IQPEmbedding).

The headline finding is that **none of the three non-classical
representations improves predictive performance beyond ECFP4** under the
tested protocols. They do add diagnostic and interpretive value.

| Comparison | Setup | Result |
|---|---|---|
| Hybrid (TFP+TNE+QK) vs ECFP4 | n=19836, 5-fold CV | Hybrid AUC 0.8876 vs ECFP4 0.9475 (Δ=−0.060) |
| QKS contribution within hybrid | drop QK from hybrid | Δ=−0.040 (QKS principal contributor) |
| Stacking TFP+TNE on ECFP4 | n=19836 | ΔAUC = −0.0002 (p=0.084, n.s.) |
| Quantum vs RBF kernel (internal) | 5-fold CV | Quantum 0.7512 vs RBF 0.7007 (p=0.0878, n.s.) |
| Quantum vs RBF (ChEMBL label-shift) | external | Quantum 0.817 vs RBF 0.847 (p=0.021, *worse*) |
| TNE vs ECFP4 (PfDHFR docking) | n=11878 | R² 0.473 vs 0.461 (TNE competitive) |
| TNE vs ECFP4 (PfATP4, PfCRT) | n=17000 | ECFP4 dominates (0.578/0.517 vs 0.464/0.334) |
| TDA H0/H1 vs #targets bound | n=19900 | weak negative ρ (–0.16 to –0.17, p≪0.001) |

The boundary statement in the abstract is preserved here:
**"These representations add diagnostic and interpretive information under the
tested protocols, but not predictive performance beyond ECFP4."**

---

## 2. Authorisation and provenance

P3 is in author-controlled pre-submission development. No administrative or
independent-review status blocks scientific work. The Zenodo DOI
`10.5281/zenodo.19608875` is **reserved**; no archive has been published.
P3's ZENODO manifest at `P3_ZENODO_DEPOSIT_MANIFEST.json` records
`status: reserved_pending_upload`.

The P3 V4 directory lacks a top-level `README.md`, `scripts/`, `tests/`, or
`requirements.txt`. The historical scripts and tests live in
`_archives/P3_V2607_archived_20260829/scripts/` (60+ scripts) and
`_archives/P3_V2607_archived_20260829/tests/`. The V2608 manuscript compiles
without those (results-only canonical). When the V2608 manuscript is
re-compiled the original scripts must be cross-referenced from the archive
(see §0.2 runbook).

---

## 3. Headline numbers

| Metric | Value | Source |
|---|---|---|
| Molecules (hybrid library, computationally predicted) | \num{19849} | `results/p3_labels_production.csv` |
| Valid TFPs | \num{19849} (0 failures) | `results/p3_tda_summary.txt` |
| Valid TNEs | \num{19836} (13 failures) | `results/p3_tne_summary.txt` |
| TNE bond dim × Tucker ranks | 8 × (8, 8, 3) | TNE pipeline |
| TNE core descriptor dim | \num{192} | TNE pipeline |
| TNE real-atom compression (mean) | 6.1× (range 1.9×–10.9×) | `p3_tne_summary.txt` |
| TNE reconstruction error | mean 0.113, max 0.220 | `p3_tne_summary.txt` |
| Quantum kernel (5-fold CV, n=5k) AUC | 0.7512 ± 0.0334 | `p3_qks_summary.txt` |
| RBF-SVM (5-fold CV) AUC | 0.7007 ± 0.0672 | `p3_qks_summary.txt` |
| Quantum vs RBF p (paired t-test) | 0.0878 (n.s.) | `p3_qks_summary.txt` |
| Hybrid RF (ECFP4) AUC (5-fold) | 0.9600 ± 0.0894 | `p3_hybrid_summary.txt` |
| TFP RF AUC (5-fold) | 0.6300 ± 0.1121 | `p3_hybrid_summary.txt` |
| TNE RF AUC (5-fold) | 0.6300 ± 0.1121 | `p3_hybrid_summary.txt` |
| Hybrid vs ECFP4 (paired t) | t=−1.714, p=0.1616 (n.s.) | `p3_hybrid_summary.txt` |
| TDA promiscuity ρ (H0_max_pers vs #targets) | −0.166985 (n=19900) | `p3_tartarus_summary.txt` |
| Tartarus polypharma RBF-SVM AUC | 0.7370 ± 0.0102 (n=19900) | `p3_tartarus_summary.txt` |
| Tartarus polypharma Quantum Kernel AUC | 0.7475 ± 0.0131 | `p3_tartarus_summary.txt` |
| Tartarus polypharma RF (TNE) AUC | **0.8178 ± 0.0060** | `p3_tartarus_summary.txt` |
| SOTA PersStats RF AUC (n=5000) | 0.8419 ± 0.0089 | `p3_sota_benchmark_summary.txt` |
| SOTA TFP-Enriched RF AUC | 0.8381 ± 0.0070 | `p3_sota_benchmark_summary.txt` |
| TNE PfDHFR R² (regression) | 0.4731 (TNE) vs 0.4606 (ECFP4) | `p3_tartarus_summary.txt` |
| TNE PfATP4 R² | 0.4637 (TNE) vs **0.5781 (ECFP4)** | `p3_tartarus_summary.txt` |
| TNE PfCRT R² | 0.3336 (TNE) vs **0.5174 (ECFP4)** | `p3_tartarus_summary.txt` |
| ECFP4 random-split AUC | 0.948 | main abstract |
| ECFP4 scaffold-split AUC (632 scaffolds) | 0.822 | main abstract |
| Hybrid (TFP+TNE+QK) AUC | 0.888 | main abstract |

---

## 4. Canonical directory inventory

```
Project3_Quantum_Inspired_RepresentationsV2607_V4/  ← canonical (this report)
├── P3_ZENODO_DEPOSIT_MANIFEST.json                  (DOI reserved; canonical_manifest pointer to V1 JSON)
├── manuscript/
│   └── LaTeX/
│       ├── Paper3_Quantum_InspiredV2608.tex          (main, 386 lines, 18 p. compiled)
│       ├── Paper3_Quantum_InspiredV2608.{aux,bbl,blg,log,out,pdf}
│       ├── Paper3_Quantum_Inspired_SM_V2608.tex      (SM, 666 lines, 18 p. compiled)
│       ├── Paper3_Quantum_Inspired_SM_V2608.{aux,bbl,blg,log,out,pdf}
│       ├── Cover_Letter_P3.tex                      (1 p.)
│       ├── Bibliography_Paper3.bib
│       └── Graphics/                                (10 figures + PDFs)
│           ├── applicability_domain.pdf
│           ├── graphical_abstract.pdf
│           ├── h1_rrs_class_violin.png
│           ├── p3_extval_internal_vs_external.png
│           ├── p3_ga_discriminator.png
│           ├── p3_qp_optimization_heatmap.png
│           ├── p3_qp_parameter_effects.png
│           ├── p3_tda_promiscuity.png
│           ├── p3_tne_parity.png
│           └── p3_tne_regression_summary.png
└── results/                                          (77 files; see §5)
```

### 4.1 Historical scripts and tests (archived)

Scripts and tests for P3 are **not** in the V4 directory. They live in
`_archives/P3_V2607_archived_20260829/scripts/` (60+ files: `p3_hybrid_benchmark.py`,
`p3_qks_benchmark.py`, `p3_tne_pipeline.py`, `p3_tda_pipeline.py`,
`p3_external_validation.py`, `p3_physical_validation.py`, `p3_quantum_param_search.py`,
etc.) and `_archives/P3_V2607_archived_20260829/tests/`. The V2608 manuscript
does not require re-execution; it consumes the committed `results/` CSVs and
summary texts directly. See §0.2 for the runbook.

---

## 5. Source artifacts (results/ layout)

| Path | Purpose | Status (29 Aug) |
|---|---|---|
| `results/p3_labels_production.csv` | n=19849 activity labels | `COMPUTED` |
| `results/p3_hybrid_benchmark.csv` | 5-fold CV RF AUC for 9 representations | `COMPUTED` |
| `results/p3_hybrid_summary.txt` | text summary | `COMPUTED` |
| `results/p3_qks_benchmark.csv` | QK vs RBF vs Linear 5-fold CV | `COMPUTED` |
| `results/p3_qks_summary.txt` | text summary | `COMPUTED` |
| `results/p3_tda_fingerprints.csv` | TDA fingerprints (n=19849, 84 features) | `COMPUTED` |
| `results/p3_tda_summary.txt` | TFP feature statistics | `COMPUTED` |
| `results/p3_tne_embeddings.csv` | TNE 192-dim embeddings (n=19836) | `COMPUTED` |
| `results/p3_tne_summary.txt` | TNE pipeline stats + recon error | `COMPUTED` |
| `results/p3_sota_benchmark.csv` | 5-fold CV: PersStats / PersImage / BettiCurve / TFP-12 / TFP-Enriched × RF/SVM | `COMPUTED` |
| `results/p3_sota_benchmark_summary.txt` | SOTA summary | `COMPUTED` |
| `results/p3_tartarus_poly_classification.csv` | Tartarus polypharma classification | `COMPUTED` |
| `results/p3_tartarus_tne_regression.csv` | Tartarus TNE regression per target | `COMPUTED` |
| `results/p3_tartarus_tda_spearman.csv` | TDA Spearman ρ vs #targets bound | `COMPUTED` |
| `results/p3_tartarus_summary.txt` | Tartarus cross-validation summary | `COMPUTED` |
| `results/p3_quantum_params_sweep.csv` | quantum parameter search | `COMPUTED` |
| `results/p3_mc_uncertainty.csv` | Monte Carlo uncertainty | `COMPUTED` |
| `results/p3_chembl_expanded.csv` | ChEMBL label-source-shift panel | `COMPUTED` |
| `results/p3_external_validation.csv` | external validation results | `COMPUTED` |
| `results/p3_external_validation_summary.txt` | external validation summary | `COMPUTED` |
| `results/p3_external_validation_qks_*.csv/.json` | QK external audit | `COMPUTED` |
| `results/p3_external_validation_statistical_audit.json` | bootstrap / perm | `COMPUTED` |
| `results/p3_chembl_validation/` | ChEMBL validation set | `COMPUTED` |
| `results/p3_physical_validation/` | physical validation outputs | `COMPUTED` |
| `results/p3_effect_sizes/` | pairwise AUC effect sizes | `COMPUTED` |
| `results/p3_scalability_results.csv` | scalability plot data | `COMPUTED` |
| `results/p3_phase2_bd6_*.csv` | phase 2 raw data | `COMPUTED` |
| `results/p3_rrs_expansion/` | RRS expansion (P1-P3 link) | `COMPUTED` |
| `results/p3_rrs_labels_for_sota.csv` | RRS labels for SOTA | `COMPUTED` |
| `results/panel_1815_*.csv` | 1815-molecule panel | `COMPUTED` |
| `results/STATISTICAL_REPRODUCIBILITY_AUDIT_P3.md` | reproducibility audit (present in archive) | `COMPUTED` |

---

## 6. Reproducibility runbook

P3 V4 has results-only canonical. Re-execution requires the archived scripts.

```bash
# 1. Recover scripts + tests from the V1 archive
ln -s ../../_archives/P3_V2607_archived_20260829/scripts ./scripts_v1
ln -s ../../_archives/P3_V2607_archived_20260829/tests ./tests_v1

# 2. (Optional) re-run the three core pipelines
mamba run -n p3_env python scripts_v1/p3_tda_pipeline.py        # 19849 TFPs
mamba run -n p3_env python scripts_v1/p3_tne_pipeline.py        # 19836 TNE embeddings
mamba run -n p3_env python scripts_v1/p3_hybrid_benchmark.py    # RF per representation
mamba run -n p3_env python scripts_v1/p3_qks_benchmark.py       # QK vs RBF
mamba run -n p3_env python scripts_v1/p3_sota_benchmark.py      # SOTA PersStats / TFP-Enriched / PersImage
mamba run -n p3_env python scripts_v1/p3_tartarus_validation.py # Tartarus cross-validation

# 3. Statistical audit
mamba run -n p3_env python scripts_v1/p3_external_validation_statistical_audit.py
mamba run -n p3_env python scripts_v1/p3_mc_uncertainty.py
mamba run -n p3_env python scripts_v1/p3_quantum_param_search.py

# 4. LaTeX compile
cd manuscript/LaTeX
pdflatex Paper3_Quantum_InspiredV2608.tex
pdflatex Paper3_Quantum_Inspired_SM_V2608.tex
pdflatex Cover_Letter_P3.tex
```

`p3_*.sbatch` files in the V1 archive document the original SLURM execution
plan; the V4 canonical is the post-execution committed CSVs.

---

## 7. Manuscript structure (V2608)

### 7.1 Main manuscript (18 p., `Paper3_Quantum_InspiredV2608.tex`, 386 lines)

- §1 Introduction (L131) — topologically-rich natural product space, claim of diagnostic-not-predictive value
- §2 Methods (L145) — TFP/TNE/QK pipeline, benchmark protocol, external validation, statistical audit
- §3 Results (L211) — TDA, TNE, hybrid, QK benchmark, Tartarus, external validation
- §4 Discussion (L297) — diagnostic vs predictive, scaffold paradox, label-source-shift
- §5 Conclusion (L335) — representations add diagnostic/interpretive value, not predictive
- Data Availability, List of Abbreviations, Acknowledgments, Authors' Contributions, Funding, Ethics, Consent, Competing Interests, Use of AI

### 7.2 Supporting Information (18 p., `Paper3_Quantum_Inspired_SM_V2608.tex`, 666 lines)

19 sections covering: topological persistence & RRS, pharmacophore fingerprint,
per-fold activity estimates, interpretation, TFP statistics, clustering quality,
discriminator benchmark, quantum circuit parameter optimisation, MC uncertainty,
scalability, effect sizes, ChEMBL enrichment, ChEMBL analogue novelty,
topological representation comparison, TopologyNet analog, applicability domain,
extended analysis, quantum kernel circuit algorithm, ChEMBL label-source-shift
transfer.

---

## 8. Validation gates (passed)

| Gate | Status | Evidence |
|---|---|---|
| TDA 19849/19849 (0 failures) | ✅ | `p3_tda_summary.txt` |
| TNE 19836/19849 (13 failures, explicit) | ✅ | `p3_tne_summary.txt` |
| Hybrid 5-fold CV 9 representations | ✅ | `p3_hybrid_benchmark.csv` + `_summary.txt` |
| QK 5-fold CV (Quantum vs RBF vs Linear) | ✅ | `p3_qks_benchmark.csv` + `_summary.txt` |
| SOTA 5-fold CV (5 strategies × 2 classifiers) | ✅ | `p3_sota_benchmark.csv` + `_summary.txt` |
| Tartarus regression (3 targets × TNE vs ECFP4) | ✅ | `p3_tartarus_summary.txt` |
| Tartarus polypharma classification (3 models) | ✅ | `p3_tartarus_summary.txt` |
| TDA promiscuity correlation (n=19900) | ✅ | `p3_tartarus_tda_spearman.csv` |
| External validation (ChEMBL) | ✅ | `p3_external_validation.csv` + `_summary.txt` |
| QK external audit | ✅ | `p3_external_validation_qks_*.csv/.json` |
| MC uncertainty quantification | ✅ | `p3_mc_uncertainty.csv` + `_summary.txt` |
| Quantum parameter sweep | ✅ | `p3_quantum_params_sweep.csv` |
| LaTeX compile (main + SM) | ✅ | `.log` files in `manuscript/LaTeX/` |
| Statistical reproducibility audit | ✅ | `STATISTICAL_REPRODUCIBILITY_AUDIT_P3.md` (in V1 archive) |

---

## 9. Honest-negative / boundary statements

1. **No quantum advantage claimed.** Quantum vs RBF p=0.0878 (n.s.); on the
   ChEMBL label-source-shift panel, QK under-performs RBF (0.817 vs 0.847,
   p=0.021).
2. **No topological advantage claimed.** Hybrid RF AUC 0.8876 vs ECFP4 0.9475
   (Δ=−0.060). Stacking TFP/TNE on ECFP4 changes AUC by −0.0002 (n.s.).
3. **TNE is target-dependent.** Competitive on PfDHFR (R² 0.473 vs 0.461), but
   inferior to ECFP4 on PfATP4 (0.464 vs 0.578) and PfCRT (0.334 vs 0.517).
4. **External validation reports 351 TNE failures** as an explicit
   ITT/complete-case sensitivity issue (not a refutation).
5. **Scaffold-split is harsher than random-split** for ECFP4 (0.822 vs 0.948
   AUC) — the panel spans only 632 Bemis-Murcko scaffolds, so the test is
   out-of-distribution by construction.
6. **QK is the principal hybrid contributor** (dropping it costs Δ=−0.040)
   but the hybrid still trails ECFP4 — the contribution is not enough to flip
   the conclusion.

---

## 10. Cross-references

- **P1 DAR** (`Project1_Chem_space_antimalarial_V7_CorrectedGrid/P1_DATA_ANALYSIS_REPORT.md`) —
  upstream chemical space (the 19,913 Set-A lead set was the source for the
  P3 19,849-molecule panel).
- **P2 DAR** (`Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md`) —
  Set-C 17-candidate cohort; P3 cross-links via
  `p3_polypharm_tfp_rrs.csv` and `p3_rrs_labels_for_sota.csv`.
- **P5 DAR** (`Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md`) —
  downstream polypharmacology modelling; P3 topological/quantum features
  are an input candidate to P5 fusion arms.
- **P4 DAR** (`P4_DATA_ANALYSIS_REPORT.md`) — Monte Carlo scaffold; P3 MC
  uncertainty follows the same coverage conventions.
- **P7 DAR** (`P7_DATA_ANALYSIS_REPORT.md` when present) — quantum molecular
  encoding; P3 is the quantum-inspired predecessor.
- **BMAD** (`BMAD_Q1_DATA_ANALYSIS_REPORT.md`) — Q1 cross-project synthesis;
  the P3 row in §6 cites this DAR for headline numbers.
- **`docs/CENTRAL_QUESTIONS_PROJECTS.md`** — Q3 is the P3 question
  ("Do TFP/TNE/QK add value beyond classical fingerprints?").

---

## 11. Repository hygiene

| Item | Status |
|---|---|
| P3 V1 (full) | archived to `_archives/P3_V2607_archived_20260829/` (118 MB results, 60+ scripts, V1/V2/V3 manuscript archive) on 2026-08-29 |
| P3 V2 (full) | archived to `_archives/P3_V2607_V2_archived_20260829/` (111 MB results, no SM beyond V2607) on 2026-08-29 |
| P3 V4 canonical | `Project3_Quantum_Inspired_RepresentationsV2607_V4/` (111 MB results, V2608 main + SM + cover) |
| P3 V4 missing `scripts/`, `tests/`, `README.md`, `requirements.txt` | historical scripts/tests recovered via symlink to V1 archive (§0.2) |
| P3 V4 ZENODO manifest `canonical_manifest` pointer | points to the now-archived V1 JSON. The pointer is technically still valid (V1 is the historical manifest source of truth); however, the V4 ZENODO JSON does not enumerate P3 V4's own file list. **Author action item:** regenerate `canonical_manifest` to point at the V4 directory contents or back-fill the V4 contents. |

---

## 12. Outstanding work and next actions

1. **Author target-journal decision.** P3 is currently dual-listed as
   *J. Cheminformatics* / *Nat. Comput. Sci.*; the target should be narrowed
   before submission-facing work.
2. **Zenodo deposit.** DOI `10.5281/zenodo.19608875` is reserved; the upload
   remains pending. The P3 V4 ZENODO manifest should be updated to enumerate
   the V4 file inventory.
3. **Restore scripts and tests in P3 V4** as a top-level `scripts/` and
   `tests/` directory (currently symlinked from the V1 archive for
   reproducibility). The V2608 manuscript compiles without re-execution, so
   this is documentation hygiene, not a functional gap.
4. **Tartarus / external validation** — `p3_external_validation_qks_ckpt.json`
   in the V1 archive is the checkpoint; the V4 directory contains only the
   CSV summaries. Re-export the ckpt if a clean re-run is requested.
5. **BMAD update.** The next BMAD refresh should re-pull P3 headline numbers
   from this DAR; the current BMAD §6 P3 row is consistent with this DAR
   (verified 2026-08-29).

---

*End of P3 Data Analysis Report — canonical, exhaustive, 2026-08-29.*
