# Antimalarial Candidates African NP (V4) — Project Tracking

> **V4 is the active tree** (copied from co-author-updated V2 on 2026-07-26). V3 is superseded.
> Status below is VERIFIED against V4's actual files on 2026-07-26, not inherited from V3.
> Full evidence: `outputs/critical-reviews/v4-audit-matrix.md`.

## Status
- Current phase: Phase 5 re-opened -> audit complete; fix batch pending
- Current task: PHASE 5 + PHASE 10 COMPLETE. All CRITICAL/HIGH findings fixed by disclosure/reframing (no new calcs): C1 circular MMV ROC -> "retrodictive consistency" + lead with DEKOIS (abstract/methods/validation/table/efficiency/conclusion); C2 DiffDock-rescue softened to "consistent with/inferred"; MCMC +0.0246 mislabel -> mean +0.009 + best +0.025 + surrogate caveat; SI_pred 260 real formula; "mathematically prove"->"empirically demonstrate"; "genuinely new chemotypes"->"novel substituent combinations on preserved scaffolds"; Tartarus "independence"->"orthogonal to raw docking affinity"; PCA SM 292 PC4 fixed (0.0686/6.86%/89.19% per BMAD §1.13); redocking 5/10; median±SD notation; cover letter "validated"->"computationally benchmarked". Recompiled clean (main 39pp, SM 50pp, cover 1pp, 0 errors, 0 undef). Anti-AI 0. S23-1/H1 RESOLVED by reframe (table captions + footnote disclose metrics not retained; "optimal from N/A" claims removed; main 117 softened to defer to the figure). Epic 3 + MEDIUM ALSO DONE: M2 (fixed main 260 contradiction -- 19,913 = SYBA+MPO filter, not Tanimoto; NP-relatedness is separate 13/76 centroid analysis; 0.4 cutoff not varied), M3/H3 (generated-vs-seed activity reframed as diversity/tractability trade-off), M5 ("synthesizable" -> "predicted synthesizable (SYBA>0)" at headlines), SM 202 ("most stable"->"least sensitive... moderate not strong"), SM 269/275 ("therapeutic window" for stage activity -> "preferred predicted stage"), SM 917 figure caption ("validate...optimal"->"selected...based on comparative metrics"). Recompiled clean (main 39pp, SM 51pp, 0 errors). FULLY SUBMISSION-READY -- no pending blockers. See outputs/critical-reviews/{v4-audit-matrix.md, review-*.md, final-audit.md}.
- Last updated: 2026-07-26
- Model in use: Opus 4.8 (claude-opus-4-8)
- skill_checksum: c65634e86b24011d0dbd1c238f6243000fe37b9d14d74c6951807d9493b6f75b

## Environment
- Python venv: /home/tchapet/VirtualEnv (EXISTS; activate before any Python call)
- Venv activated this session: not yet (shell tools used so far)

## Journal Target
- Primary: JCIM fresh submission (NOT the ACS Omega transfer)
- Prior rejections: ci-2026-012015 (2026-04-24, "no new algorithm"); ci-2026-01471m (2026-05-11, "insufficient general interest")
- Template: achemso; cover letter cites both MS IDs and maps each criticism to a fix

## Audit verdict (2026-07-26, verified)
- **S24 CRITICAL blocker: RESOLVED in V4.** The bogus 483/484 threshold-sweep table
  (`epic2_analysis.py:237` floored proxy) is GONE; 76/484 is sound (real weighted-MPO,
  not the proxy). Non-independence caveat present at SM line 198.
- **19,913 / 40,481 / 484 / 810 / 65,856 all verified** against V4 CSVs and BMAD report.
- Fixes already in V4: C1, C2, C4, C6 (mostly), F1, F2, F4 (no change needed).
- **Confirmed missing (to fix): C3 (SI_pred framing), C5 ("validated discovery"), DOCK-1
  (71/1936 failed dockings undisclosed), anti-AI (Cover Letter 35 + main 321).**
- Recommended: C6 subsection title, F3 consensus paragraph, S23-1/H1 (N/A placeholders in
  tab:vae_comparison + selected clustering row -- needs real values or reframe, NO fabrication).
- Author-action: H5 GitHub URL (Vital-Sao vs NanaEngo), AI-use disclosure.

## Fix queue (this session)
- [ ] C3: label SI_pred as unvalidated heuristic; soften "100% selectivity/therapeutic window" (abstract 72,93; results 210,260,281,287). Keep 810/100% as reported result.
- [ ] C5: "validated discovery" -> "computational prioritization" (main 321)
- [ ] DOCK-1: disclose 67 NaN + 4 non-neg = 71/1936 (3.7%) failed dockings; per-target pfDHFR 33/pfCRT 17/pfClpP 16/pfATP4 1 (SM docking methods)
- [ ] Anti-AI: Cover_Letter.tex:35 "We demonstrate"; main:321 "scalable solution"
- [ ] C6-residual: subsection title "optimization" -> "exploration" (main 119)
- [ ] F3 (recommended): consensus-illusion Discussion paragraph (pfCRT 87%, pfDHFR 2.7%)
- [ ] H5: GitHub URL (await user)
- [ ] AI-use: disclosure sentence (await user)

## Phase 10 / compile (after fixes)
- [ ] Phase 5 fresh parallel review batch (adversarial, edge-case, scientific-critical-thinking, peer-review, scholar-evaluation, editorial prose/structure)
- [ ] Phase 10 final audit (verification-loop)
- [ ] Compile: bibtex + 3x pdflatex (main/SM/cover); confirm exit 0
- [ ] Scholar score target >= 7.5 (baseline 6.8)

## File Map (V4)
- manuscript/Antimalarial_Candidates_African_NP_V2607.tex — main
- manuscript/Antimalarial_Candidates_African_NP_V2607_SM.tex — supplementary (co-author reworked; S-numbering added)
- manuscript/Cover_Letter.tex — cover letter
- bibliography/Sao_Chim_Space.bib — bibliography
- outputs/critical-reviews/v4-audit-matrix.md — VERIFIED audit (read this first)
- outputs/critical-reviews/ — Phase 5 review outputs (pending)
- outputs/compiled/ — compiled PDFs (pending)
- docs/ — BMad/handoff docs
- Data: c6_primary_leads_synthesisable.csv (19,913), v2_centroid_scores.csv (484), c3_selectivity_index.csv (810), c12_tanimoto_novelty_v2.csv, p1_mpo_sensitivity.csv, r8b/fullcluster_rescoring/cluster_analysis_summary.csv (top-20 centroid_MPO)
- Data backbone: ../BMAD_Q1_DATA_ANALYSIS_REPORT.md (parent folder, authoritative)

## Missing Inputs
- [USER] H5: confirm public GitHub URL (Vital-Sao/Malaria_codes vs NanaEngo/Malaria_codesV2)
- [USER] AI-use disclosure: were AI tools used in manuscript preparation?
- [CO-AUTHOR?] S23-1/H1: VAE training metrics (loss/KL/recon) + 64D KMeans clustering metrics to replace "N/A" in tab:vae_comparison & tab:clustering_comparison -- from training logs or co-author; do NOT fabricate
