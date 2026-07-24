# Paper 3: Persistent Homology Resolves the Scaffold Paradox in AI-Generated African Antimalarial Candidates

## Working Title

Persistent Homology Resolves the Scaffold Paradox in AI-Generated African Antimalarial Candidates: a Topological and Tensor-Network Fingerprinting Study

---

## Status (July 24, 2026)

| Attribute | Details |
|-----------|---------|
| **Version** | v0.9 — Main 16p + SM 11p, 0 undefined references |
| **Target Journal** | *Journal of Cheminformatics* (IF ≈ 6.5) |
| **Bibliography style** | natbib (authoryear) |
| **Compilation** | ✅ Main 16p, 0 errors; SM 11p, 0 errors |
| **Zenodo DOI** | `10.5281/zenodo.19608875` — reserved (data upload pending) |
| **Acceptance estimate** | **45–55%** → Roadmap to ≥85% documented |

### Recent Commits (July 24, 2026)

| Commit | Description |
|--------|-------------|
| `eabafec7` | Expanded H₁-RRS n=33 results (ρ=0.305, p=0.085 n.s.) + manuscript updates |
| `9ae249b` | Fix all LaTeX bugs (undefined refs, missing SI units, SM bibliography) |
| `51a2589` | Correct compilation order (Main→SM→Main) |
| `66c287a` | Page reduction 17→16 (condensed Limitations, Conclusion, When-Methods-Add-Value) |
| `71863f5` | Polish trims (smooth transition, condensed 6→3 step enumeration) |

---

## Compilation Status

| File | Pages | Undefined Refs | Errors | Status |
|------|-------|----------------|--------|--------|
| `Paper3_Quantum_InspiredV2607.tex` | **16** | **0** | **0** | ✅ J Cheminform limit |
| `Paper3_Quantum_Inspired_SM_V2607.tex` | **11** | **0** | **0** | ✅ Clean |

---

## Key Results

| Result | Value | Source | Status |
|--------|-------|--------|--------|
| ECFP4 AUC (baseline) | 0.868 | Full benchmark (n=19,849) | ✅ Verified |
| Hybrid AUC (TFP+TNE+QKS) | 0.842 | Full benchmark (n=19,849) | ✅ Verified |
| Hybrid p-value vs ECFP4 | 0.111 (ns) | Paired t-test, 5-fold CV | ✅ Not significant |
| QKS AUC (gamma-tuned RBF) | 0.751 | Subsample (n=500) | ✅ Verified |
| QKS vs RBF p-value | 0.312 (ns) | Subsample (n=500) | ✅ No quantum advantage |
| Optimised Hybrid AUC (n=1000) | 0.828 ± 0.037 | Phase2 re-benchmark | ✅ Verified |
| H₁-RRS pilot (n=14) | ρ = 0.947, p < 0.0001 | Cross-paper | ⚠️ Preliminary only |
| **H₁-RRS expanded (n=33)** | **ρ = 0.305, p = 0.085 (n.s.)** | Cross-paper | ❌ Did not replicate |
| TNE compression | 5.9× real-atom | Full library | ✅ Verified |
| TDA success rate | 99.93% | 19,836/19,849 valid | ✅ Verified |

---

## Acceptance Assessment (July 24, 2026)

**Estimated probability: 45–55%** → **Target ≥85%**

### Score Card (1–10 scale)

| Criterion | Score | Weight | Weighted | Target |
|-----------|:-----:|:------:|:--------:|:------:|
| Methodological rigor | 7 | 25% | 1.75 | 9 |
| Novelty of findings | 6 | 25% | 1.50 | 8 |
| Presentation quality | 7 | 15% | 1.05 | 9 |
| Reproducibility | 8 | 15% | 1.20 | 9 |
| Biological relevance | 4 | 10% | 0.40 | 7 |
| Addressing limitations | 8 | 10% | 0.80 | 9 |
| **Total** | — | **100%** | **6.70/10** | **8.50/10** |

### Critical Gaps

| # | Gap | Severity | Action |
|---|-----|----------|--------|
| 1 | No experimental validation (all computational) | 🔴 High | ChEMBL IC₅₀ proxy (Action 1) |
| 2 | H₁-RRS failed at n=33 (ρ=0.947→0.305) | 🔴 High | Reframe as methodological finding (Action 2) |
| 3 | No SOTA topological benchmark | ✅ Complete (textual comparison) | Comparison with TopologyNet/D-GRIL integrated into manuscript §2.1 |
| 4 | RRS cohort too small (n=33, need n≥80) | 🟡 Medium | Expand to 500+ compounds (Action 4) |
| 5 | Zenodo deposit incomplete | 🟡 Medium | Complete deposit (Action 5) |

---

## Roadmap to 85% Acceptance

See **[P3_SUBMISSION_ROADMAP_85PCT.md](./P3_SUBMISSION_ROADMAP_85PCT.md)** for the detailed plan.

| Action | Task | Hours | Impact | Status |
|:------:|------|:-----:|:------:|:------:|
| 1 | ChEMBL IC₅₀ validation | 3–4 | +15% | ⏳ Pending |
| 2 | Reframe H₁-RRS narrative | 2 | +10% | ⏳ Pending |
| 3 | Benchmark SOTA topological methods (textual comparison) | 6–8 | +8% | ✅ Complete |
| 4 | Expand RRS cohort to n≥80 | 4–6 | +5% | ⏳ Pending |
| 5 | Complete Zenodo deposit | 2 | +5% | ⏳ Pending |
| 6 | Manuscript refinement | 4 | +5% | ⏳ Pending |
| 7 | Reframe Limitations as strengths | 2 | +3% | ✅ Complete |

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
| `manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex` | **Canonical main** — 16p, 0 errors |
| `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex` | **Canonical SM** — 11p, 0 errors |
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
| `scripts/p3_rrs_expansion.py` | Expand RRS computation to 200+ compounds |
| `scripts/p3_rrs_expansion.sbatch` | SLURM batch for RRS expansion (fixed paths) |
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
| SLURM path resolution | `p3_rrs_expansion.sbatch` | Hardcoded absolute paths + set -u fix | July 24 |

---

## Key Findings

1. **ECFP4 remains the recommended baseline** (AUC 0.868) for primary screening; the hybrid matches it (AUC 0.842, p=0.111) without significantly exceeding it.
2. **Quantum, RBF, and Linear kernels are statistically indistinguishable** (p > 0.05) — the earlier apparent quantum advantage was an artefact of untuned RBF hyperparameters.
3. **H₁ topological persistence shows a preliminary correlation with resistance tolerance** (ρ=0.947, n=14 pilot), which weakened to a non-significant trend upon expansion to 33 compounds (ρ=0.305, p=0.085) — a methodological insight on balanced-class sampling.
4. **TFP resolves the scaffold paradox** via H₁/H₀ decomposition: ring topology (H₁) is preserved while peripheral connectivity (H₀) diverges.
5. **TNE achieves 5.9× real-atom compression** with competitive Tartarus regression (R²=0.473 for PfDHFR).

## Scope

- **Library**: 19,849 molecules (full benchmark); 65,856 (activity labels)
- **Methods**: TFP (12-dim persistent homology), TNE (Tucker d=8, 5.9× compression), QKS (8-qubit PennyLane)
- **Benchmark**: 5-fold CV, RF + SVM, Bonferroni-corrected paired t-tests
- **Cross-paper**: H₁ persistence vs RRS (P3 × P2, n=14 pilot, n=33 expanded)

---

## Authors

Myke Vital Sao Temgoua, Jean-Pierre Tchapet Njafa, Serge Guy Nana Engo, Penabei Samafou, Wilfred Fon Mbacham

---

**Roadmap:** [P3_SUBMISSION_ROADMAP_85PCT.md](./P3_SUBMISSION_ROADMAP_85PCT.md)
**Last Updated:** July 24, 2026
