# P1 — Canonical data and analysis status (V8)

**Project**: Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes  
**Manuscript target**: *J. Chem. Inf. Model.* (JCIM, ACS)  
**Revision**: V8 (response to reviewers)  
**Last updated**: 2026-09-10  

This file records the canonical numerical state of the P1 analysis after the R1/R2 revisions. All primary results live in the manuscript (`P1_Integrated_Polypharmacology_RRS_Main_V8.tex`) and Supporting Information (`P1_Integrated_Polypharmacology_RRS_SM_V8.tex`); the Zenodo deposit (`zenodo_package_P1/`) holds machine-readable tables, code, and raw docking outputs.

## Canonical numbers (V8, corrected PfCRT channel)

- Library: 65 856 unique molecules → 19 913 prioritised candidates.  
- Cohort: 17-member Set-C polypharmacology-oriented set.  
- Docking: 68/68 candidate–target pairs pass geometric gate; scores −12.01 to −4.63 kcal mol⁻¹.  
- PfCRT: re-docked on 3D7-like LYS-76 receptor, cavity-anchored V2 grid (25 Å); pipeline-null RRS 99.4–100.5 %.  
- RRS classes: 7 A*, 4 B, 6 C, 0 D (range 73.2–115.6 %).  
- Favourability: within-target median (PfDHFR −5.92, PfCRT −8.06, PfClpP −6.02, PfATP4 −6.38 kcal mol⁻¹).  
- Cross-metric (Bonferroni α = 0.017, n = 17):  
  - PNS–RRS ρ = −0.714 (p = 0.0013)  
  - N_fav–RRS ρ = +0.714 (p = 0.0013; permutation p = 0.0019)  
  - RRS–|S_WT| ρ = +0.691 (p = 0.0021)  
  - ACSI–RRS ρ = −0.190 (n.s.)  

## Reviewer-driven controls completed

- R1.1 Structural-evidence gradient stated explicitly.  
- R1.2 Retrospective docking of five approved antimalarials (negative recovery of clinical signatures).  
- R2.1 N_fav–RRS correlation and power limitation reported.  
- R2.2 Within-target median favourability; Table 2 recomputed.  
- R2.3 PfCRT isoform/grid correction and full re-dock.  
- R2.4 Two-arm MTX-retained vs MTX-stripped DEKOIS (negative for blockade).  
- R2.5 Pipeline-null control; class boundaries placed relative to null.  
- R2.6 WT/mutant score table in SI; Zenodo package assembled (DOI pending).  
- R2.7 PNS and ACSI formally defined.  
- R2.8 Redocking/validation tables rebuilt (no contradiction).  
- R2.9 Five-seed sensitivity reported.  
- All minor points addressed.

## Evidence boundary

All results are computational hypotheses. No experimental potency, confirmed multi-target engagement, or resistance-circumvention claims are made. Docking scores are AutoDock Vina scoring-function outputs, not free energies.

## File map

| Item | Location |
|------|----------|
| Main text | `P1_Integrated_Polypharmacology_RRS_Main_V8.tex` |
| Supporting Information | `P1_Integrated_Polypharmacology_RRS_SM_V8.tex` |
| Response to reviewers | `Response_to_Reviewers_P1_V8.tex` |
| Cover letter | `Cover_Letter_P1_V8.tex` |
| Tables (SI) | `tables/sm_table_*.tex` (also root copies) |
| Graphics | `p1_v7_*.pdf` |
| Archival deposit | `zenodo_package_P1/` (external; DOI to insert) |

This status file supersedes earlier V4–V7 snapshots.
