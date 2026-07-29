# JCIM Manuscript — Organized Structure

## Status

> **Tartarus benchmark:** Full run (19,913 mol × 3 targets) completed Jul 7 2026. Calibration (50 mol) cited in Limitations — full results integrated into P2 correlation analysis. **P1 unblocked.**

**Manuscript V2607:** Finalized — fully compiled (0 errors).
Latest manuscript and scripts synced from `Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid/` on 2026-07-20. This directory remains the canonical P1 location.  

### External Validation Status (Jul 16, 2026)
- **R1-B (MMV Malaria Box):** ✅ COMPLETE — hit rates: PfDHFR 35.1%, PfCRT 90.7%, PfATP4 47.3%, PfClpP 94.0% (composite 69.8%). Table `tab:mmv-validation` in SM.
- **R1-A (DEKOIS 2.0):** ✅ COMPLETE — 1,200 decoys + 40/40 actives docked (1199 decoys valid, uniform Meeko pipeline). Final DEKOIS ROC-AUC is 0.450 (95% CI 0.367–0.531, near-random), honestly reported in manuscript to motivate ML-based DiffDock rescoring.
- **ChEMBL (Part B):** ✅ COMPLETE — integrated into manuscript §1.12 and SM Table S18 (PfDHFR active EXC hit rate = 60.4%, inactive = 11.1%; PfATP4 active GOOD = 53.4%, inactive = 63.2%; PfCRT active EXC = 100%, inactive = 68.4%).
- Main manuscript text now attributes ROC-AUC 0.924–1.000 to the **MMV positive-control benchmark** (not DEKOIS); DEKOIS described as a separate independent external benchmark.

### What is still pending for Project 1:
- [x] **ChEMBL Part B Benchmark:** Completed and integrated.
- [x] **ASKCOS Integration:** Completed (reductive amination identified as primary route).

### R8-B Implementation (Jul 12 2026)
- Scripts implemented — generated outputs in `manuscript/` and `scripts/r8b/`:
- `r8b_pipeline.py` — full workflow: top-10 selection → SM Table S20 → SM Figure S15 → ASKCOS stub
- `SM_Table_S20_top10_retrosynthesis.tex` — LaTeX table with top-10 binding data
- `SM_Figure_S15_top10_binding_modes.pdf` — 2D structure diagrams for top-10
- `SM_Table_S20_top10_retrosynthesis_askcos_stub.tex` — ASKCOS integration framework
- Run: `cd /home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid && python3 scripts/r8b/r8b_pipeline.py --askcos`

**Next:** Ready for submission.

## Directory Structure

```
Papers/Chem_space_antimalarial_JCIM/
├── manuscript/
│   ├── Antimalarial_Candidates_African_NP.tex      # Main manuscript (achemso, jcisd8)
│   ├── Antimalarial_Candidates_African_NP_SM.tex   # Supplementary Material
│   ├── Cover_Letter.tex                             # Cover letter
│   └── achemso.bst                                  # ACS bibliography style
├── bibliography/
│   ├── Sao_Chim_Space.bib                          # Main bibliography (55 cited entries)
│   ├── acs-Antimalarial_Candidates_African_NP.bib  # Auto-generated achemso control
│   └── acs-Antimalarial_Candidates_African_NP_SM.bib
├── output/
│   ├── Antimalarial_Candidates_African_NP.pdf      # Main manuscript (42 pages)
│   ├── Antimalarial_Candidates_African_NP_SM.pdf   # Supplementary (26 pages)
│   └── Cover_Letter.pdf
├── r1b_mmv_results/                                 # MMV benchmark results
├── README.md                                        # This file
├── README_ZENODO.txt                                # Zenodo dataset documentation
├── FIXES_LOG.md                                     # All manuscript fixes (34 items)
├── REVISION-ROADMAP.md                              # Revision tracking (all complete)
├── GATE_10_11_EDITORIAL_SIMULATION.md               # Editorial simulation report
└── REVIEW-JCIM.md                                   # Original review notes
```

```
Papers/Graphics/                                     # All figures
├── flowchart_chemspace.pdf
├── 32_smi_vae_training_history_full.pdf
├── 64_smi_vae_training_history_full.pdf
├── clustering_quality_comparison.pdf
├── phys_chem.pdf
├── intra_inter_cluster_similarity_distributions.pdf
├── admet_prop.pdf
├── ACTIVITY_PRED.pdf
├── redocking_rmsd.pdf / redocking_success_rate.pdf
├── enrichment_roc_curves.pdf / enrichment_factors_comparison.pdf / enrichment_metrics_heatmap.pdf
├── consensus_correlation_analysis.pdf / consensus_hit_rate_comparison.pdf / consensus_overlap_analysis.pdf
├── docking_summary_4panel.pdf
├── vae_training_curves.pdf / vae_accuracy_comparison.pdf
├── interaction_201.png / interaction_214.png / interaction_438.png
├── si_figure_s14_umap_latent_space.png
└── graphical_abstract.png
```

## Compilation (Final Sequence)

From the `manuscript/` directory:

```bash
rm -f *.aux *.bbl *.blg *.log *.out
pdflatex Antimalarial_Candidates_African_NP_SM.tex
pdflatex Antimalarial_Candidates_African_NP.tex
bibtex Antimalarial_Candidates_African_NP
bibtex Antimalarial_Candidates_African_NP_SM
pdflatex Antimalarial_Candidates_African_NP.tex
pdflatex Antimalarial_Candidates_African_NP_SM.tex
pdflatex Antimalarial_Candidates_African_NP_SM.tex
pdflatex Antimalarial_Candidates_African_NP.tex   # final pass
```

## Key Facts

| Item | Value |
|------|-------|
| Main manuscript | 47 pages |
| Supplementary | 41 pages |
| Citations | 55 unique |
| Library size | 65,856 molecules |
| Synthesizable leads | 19,913 (MPO ≥ 0.70, SYBA > 0) |
| Zenodo DOI | 10.5281/zenodo.19608875 |
| GitHub | https://github.com/NanaEngo/Malaria_codesV2 |

## Quality Gates (all passed 2026-04-17)

| Gate | Status |
|------|:------:|
| 10.1 Compilation | ✅ |
| 10.2 Journal Compliance | ✅ |
| 10.3 Style (US English) | ✅ |
| 10.4 Technical (siunitx, cref) | ✅ |
| 10.5 Content | ✅ |
| 10.6 Consistency | ✅ |
| 10.7 Placeholder Audit | ✅ |
| 10.8 Citations (55, all 5 tiers) | ✅ |
| 10.9 Senior Reviewer | ✅ |
| 10.10 Editorial Board + FAIR | ✅ |
| 10.11 Q1 Simulation → Send for review | ✅ |
