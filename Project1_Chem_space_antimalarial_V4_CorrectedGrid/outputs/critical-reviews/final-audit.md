# Phase 10 Final Pre-Submission Audit — V4 (2026-07-26)

> **SUPERSEDED HISTORICAL AUDIT.** This record documents the 26 July state and is retained for provenance. The authoritative post-correction verdict is `final-submission-audit-20260807.md`, which includes the 4GM2/PfClpR identity correction and the final V4 compilation status.

Run after the Phase 5 critical-review batch fixes were applied + recompiled clean.
Checklist per article-writing skill Phase 10; evidence from V4 files + Phase 5 reviews.

## Compile + language
| Item | Verdict | Evidence |
|---|---|---|
| Main compiles | PASS | 39 pp, 0 errors, 0 undefined refs (bibtex + 3x pdflatex) |
| SM compiles | PASS | 50 pp, 0 errors, 0 undefined refs |
| Cover letter compiles | PASS | 1 pp, 0 errors |
| Anti-AI scan | PASS | 0 banned-pattern hits across all three .tex |
| Terminology consistency | PASS (minor residual) | "optimization-worthy" retained (defined term); "PfDHFR-TS" vs "PfDHFR" used contextually |

## Result-claim consistency + rigor (post-Phase-5 fixes)
| Item | Verdict | Evidence |
|---|---|---|
| S24 (483/76 contradiction) | PASS | 483 table gone; 76/484 sound (real weighted-MPO); caveat at main 206 / SM 198 |
| C1 circular MMV ROC | PASS (reframed) | "retrodictive consistency" + "score-based stratification for 3/4 targets" disclosed (abstract 72/93, methods 126, validation 216, table caption 220, efficiency 265, conclusion 317/319); DEKOIS leads |
| C2 DiffDock-rescue claim | PASS (softened) | "consistent with / inferred across benchmarks rather than demonstrated" (281, 317, 319) |
| MCMC +0.0246 mislabel | PASS (fixed) | Now reports mean +0.009 + best +0.025 + surrogate R2=0.377 + no UQ + not de novo (121, 317) |
| SI_pred framing | PASS | Labeled unvalidated heuristic at 210 + 260 + SM caption 236; real formula, not IC50 ratio |
| C5 "validated discovery" | PASS | -> "computational prioritization" (321) |
| DOCK-1 failure disclosure | PASS | 71/1936 (3.7%) + per-target counts (SM 178) |
| "mathematically prove" | PASS | -> "empirically demonstrate" (91) |
| "genuinely new chemotypes" | PASS | -> "novel substituent combinations on preserved scaffolds" (271) |
| Tartarus "independence of MPO dimensions" | PASS | -> "orthogonal to raw docking affinity" + cross-ref to shared-residual caveat (305) |
| Cover letter "validated" | PASS | -> "computationally benchmarked" (line 35) |
| PCA table SM 292 | PASS | PC4 fixed to 0.0686 / 6.86% / 89.19% (matches BMAD §1.13) |
| Redocking 5/5 | PASS | Now "5/5 alignable; 5/10 overall, 5 excluded for SDF mismatches" (216) |
| Median +/- SD | PASS | -> "median 3.51 (distribution SD 1.45)" (146) |
| Numbers trace to source | PASS | 19,913=c6 CSV rows; 484=v2_centroid_scores; 810/100%=c3_selectivity_index; 65,856/40,481/763.8/53 canonical (BMAD §8) |

## Reporting + availability
| Item | Verdict | Evidence |
|---|---|---|
| Data availability statement | PASS | Zenodo DOI 10.5281/zenodo.19608875; FAIR-compliant (main 341) |
| Code availability | PASS | GitHub github.com/Vital-Sao/Malaria_codes (user-confirmed public URL) |
| AI-use disclosure | PASS | Acknowledgments (user-approved) |
| Ethical declarations | PASS | Author Contributions, Funding (none), Competing Interests (none) |
| Cover letter | PASS (per user) | Short, revision of ci-2026-012015, date 2026-07-26 (user chose this framing) |
| Random seeds / reproducibility | PARTIAL | Seeds stated in Data Availability; per-centroid DiffDock/QED/ADMET not retained (disclosed) |

## Historical remaining blockers / open items (non-blocking, need co-author — NOT fabricated)
| Item | Severity | Action |
|---|---|---|
| S23-1/H1: tab:vae_comparison (SM 851-876) + selected 64D KMeans row (SM 941) are "N/A" | MEDIUM | Needs VAE training logs (loss/KL/recon) + clustering metrics from co-author. Do NOT fabricate. Either restore real values or reframe the table to not claim "optimal/superior" from N/A. |
| Epic 3 (M2 Tanimoto sensitivity curve; M3/H3 generated-vs-seed activity reframe; M5 ASKCOS synthesizability softening) | LOW | Optional for JCIM revision; not started. |
| Phase 5 MEDIUM residuals (MPO "stable" wording at SM 202; "therapeutic window" for stage activity at SM 269/275) | LOW | Optional softening; not blocking. |

## Historical verdict — superseded 9 August 2026
The editorial audit was clean for the historical V4 text, but it does not authorize
submission. The V4 484-centroid numerical panel still contains the historical 4GM2 arm,
which is PfClpR rather than genuine PfClpP. Submission is blocked pending complete
2F6I/PfClpP revalidation, independent review, and downstream recomputation. This
historical audit must not be used as a submission authorization.

The historical recommendation was to obtain VAE training metrics + 64D KMeans clustering
metrics from the co-author or reframe those tables before submission. See the August 7 audit
for the current status after those disclosure/reframing actions.
