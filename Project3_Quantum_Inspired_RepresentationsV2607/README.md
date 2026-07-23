# Paper 3: Persistent Homology Resolves the Scaffold Paradox in AI-Generated African Antimalarial Candidates

## Working Title

Persistent Homology Resolves the Scaffold Paradox in AI-Generated African Antimalarial Candidates: a Topological and Tensor-Network Fingerprinting Study

---

## Status (July 23, 2026)

| Attribute | Details |
|-----------|---------|
| **Version** | v0.8 — Main 20p + SM 6p, 0 undefined references |
| **Target Journal** | *Journal of Cheminformatics* (IF 6.5) |
| **Bibliography style** | natbib (authoryear) |
| **Compilation** | ✅ Main 20 pages, 0 errors; SM 6 pages, 0 errors |
| **Zenodo DOI** | `10.5281/zenodo.19608875` — reserved (pending final deposit of CSVs, scripts, benchmark data) |

### Recent Commits (July 23, 2026)

| Commit | Description |
|--------|-------------|
| `cd901a35` | SM Table S5: remove fabricated n=200 rows, keep authoritative n=1000 only |
| `be9b18dd` | P3 phase2 n=1000 data integration + gitignore CSV/TXT unignore + P3 param_search bugfix |
| `e265c881` | gitignore CSV/TXT unignore + P3 param_search bugfix |
| `a85c7f02` | P3 data pipeline integration + deprecated-ref cleanup (SM §5-7, BMAD §3.10-3.11) |
| `58e2156b` | P3 Q1 polish: 5 remaining items fixed (circular caption, undefined fig ref, PHCO to SM, Table S4, SM label bug) |
| `e189a786` | P3 Q1 prose polish: 17 non-Q1 terms replaced, caption consistency, siunitx fix |

---

## Compilation Status

| File | Pages | Undefined Refs | Errors |
|------|-------|----------------|--------|
| `Paper3_Quantum_InspiredV2607.tex` | 20 | 0 | 0 |
| `Paper3_Quantum_Inspired_SM_V2607.tex` | 6 | 0 | 0 |

---

## Key Results

| Result | Value | Source |
|--------|-------|--------|
| ECFP4 AUC (baseline) | 0.868 | Full benchmark (n=19,849) |
| Hybrid AUC (TFP+TNE+QKS) | 0.842 | Full benchmark (n=19,849) |
| Hybrid p-value vs ECFP4 | 0.111 (ns) | Paired t-test, 5-fold CV |
| QKS AUC (gamma-tuned RBF) | 0.751 | Subsample (n=500) |
| QKS vs RBF p-value | 0.088 (ns) | Subsample (n=500) |
| Optimised Hybrid AUC (n=1000) | 0.828 ± 0.037 | Phase2 re-benchmark (bd=6, nr=1, nk=30) |
| H₁ persistence vs RRS | ρ = 0.947, p < 0.0001, 95% CI [0.799, 1.000] | Cross-paper (n=14) |
| TNE compression | 5.9× real-atom | Full library |
| TDA success rate | 99.93% | 19,836/19,849 valid |

---

## Quantum Parameter Optimisation (Phase 2)

### Grid Search (Job 7962)
- 60 combinations: bond_dim ∈ {4,6,8} × n_repeats ∈ {1,2,3,4,6} × n_kpca ∈ {5,10,20,30}
- 5-fold CV RF on n=200 molecules
- Completed 50/60 combos before termination

### Re-benchmarking (Jobs 11974, July 22)
- Top-3 combinations re-evaluated on n=1000 molecules (750 active, 250 inactive)
- All 3 completed quantum kernel computation but failed at summary stage (UnboundLocalError — fixed July 23)
- Per-fold results saved to raw CSVs

| bond_dim | n_repeats | n_kpca | AUC (n=1000) | Source |
|:--------:|:---------:|:------:|:------------:|:------:|
| **6** | **1** | **30** | **0.8283 ± 0.0371** | `p3_phase2_bd6_nr1_nk30_raw.csv` |
| 6 | 6 | 20 | 0.8047 ± 0.0354 | `p3_phase2_bd6_nr6_nk20_raw.csv` |
| 6 | 6 | 30 | 0.8121 ± 0.0396 | `p3_phase2_bd6_nr6_nk30_raw.csv` |

---

## Manuscript Files

| File | Status |
|------|--------|
| `manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex` | **Canonical main** — 20p, 0 errors |
| `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex` | **Canonical SM** — 6p, 0 errors |
| `manuscript/LaTeX/Paper3_Quantum_InspiredV2607.pdf` | Compiled PDF (main) |
| `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.pdf` | Compiled PDF (SM) |
| `.archive_P3_V2607_20260720/` | Deprecated drafts — do not edit |

### SM Sections

| Section | Content |
|---------|---------|
| §1 | Cross-paper H₁ persistence vs RRS (fig:h1_rrs) |
| §2 | Per-fold activity prediction statistics (Table S4) |
| §3 | Topological fingerprint statistics (Table S1, fig:persistence) |
| §4 | PHCO fingerprint extraction bug |
| §5 | Quantum circuit parameter optimisation (Table S5, fig:qp_heatmap, fig:qp_effects) |
| §6 | Monte Carlo uncertainty estimation |
| §7 | Computational scalability |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/p3_tda_pipeline.py` | Vietoris-Rips persistence diagrams + TFP extraction |
| `scripts/p3_tne_pipeline.py` | Tucker decomposition + TNE embeddings |
| `scripts/p3_qks_benchmark.py` | 8-qubit quantum kernel vs RBF-SVM benchmark |
| `scripts/p3_hybrid_benchmark.py` | Hybrid framework + ablation study |
| `scripts/p3_quantum_param_search.py` | Grid search over quantum circuit hyperparameters |
| `scripts/p3_ga_discriminator.py` | GA-style discriminator benchmark |
| `scripts/p3_mc_uncertainty.py` | Monte Carlo dropout uncertainty estimation |
| `scripts/p3_h1_rrs_cross_paper_analysis.py` | Cross-paper H₁ persistence vs RRS |
| `scripts/prepare_panel_1815.py` | 1,815-molecule panel for TDA/QKS relance |

---

## Bug Fixes Applied

| Bug | File | Fix | Date |
|-----|------|-----|------|
| PHCO SparseBitVect → all zeros | `p3_hybrid_benchmark.py` | Use `GetOnBits()` instead of `ConvertToNumpyArray()` | July 2026 |
| QKS untuned RBF baseline | `p3_qks_benchmark.py` | Inner CV gamma optimisation on {0.5,1.0,2.0,5.0} | July 2026 |
| Circular Table 2 caption | `Paper3_Quantum_InspiredV2607.tex` | Removed self-referencing `\cref{tab:qkernel}` | July 23 |
| Undefined fig:joint_h1_rrs | `Paper3_Quantum_InspiredV2607.tex` | Replaced with `SM-fig:h1_rrs` via externaldocument | July 23 |
| SM double-prefix labels | `Paper3_Quantum_Inspired_SM_V2607.tex` | `SM-sec:phco_bug` → `sec:phco_bug` | July 23 |
| UnboundLocalError (results_df) | `p3_quantum_param_search.py` | Moved summary before `del` cleanup | July 23 |
| Hardcoded P1 path | `prepare_panel_1815.py` | Replaced with relative `MALARIA_ROOT` path | July 23 |
| Typo Projet1 → Project1 | `r8b_pipeline.py` | Corrected directory name | July 23 |

---

## Remaining Tasks Before Submission

| Priority | Task | Status |
|----------|------|--------|
| 🔴 High | Final Zenodo deposit (DOI reserved, data upload pending) + update Data Availability | Pending |
| 🔴 High | Resubmit full 60-combo grid search on HPC with fixed script | Pending |
| 🟡 Medium | Update P1/P2 manuscripts with shared Zenodo DOI | Pending |
| 🟡 Medium | Compile P1 and P2 manuscripts to verify clean build | Pending |
| 🟢 Low | Internal review of full manuscript PDF | Pending |

---

## Key Findings

1. **ECFP4 remains the recommended baseline** (AUC 0.868) for primary screening; the hybrid matches it (AUC 0.842, p=0.111) without significantly exceeding it.
2. **Quantum, RBF, and Linear kernels are statistically indistinguishable** (p > 0.05) — the earlier apparent quantum advantage was an artefact of untuned RBF hyperparameters.
3. **H₁ topological persistence predicts resistance tolerance** (Spearman ρ=0.947, p < 0.0001, n=14) — a computationally efficient topological predictor of mutation tolerance.
4. **TFP resolves the scaffold paradox** via H₁/H₀ decomposition: ring topology (H₁) is preserved while peripheral connectivity (H₀) diverges.
5. **TNE achieves 5.9× real-atom compression** with competitive Tartarus regression (R²=0.473 for PfDHFR).

## Scope

- **Library**: 19,849 molecules (full benchmark); 65,856 (activity labels)
- **Methods**: TFP (12-dim persistent homology), TNE (Tucker d=8, 5.9× compression), QKS (8-qubit PennyLane)
- **Benchmark**: 5-fold CV, RF + SVM, Bonferroni-corrected paired t-tests
- **Cross-paper**: H₁ persistence vs RRS (P3 × P2, n=14, Spearman ρ=0.947)

---

## Authors

Myke Vital Sao Temgoua, Jean-Pierre Tchapet Njafa, Serge Guy Nana Engo, Penabei Samafou, Wilfred Fon Mbacham

---

**Roadmap:** [`docs/PAPERS_2_3_ROADMAP.md`](../../docs/PAPERS_2_3_ROADMAP.md) (v2.2)
**Last Updated:** July 23, 2026
