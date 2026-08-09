# Antimalarial Candidates African NP (V4) — Project Tracking

> **V4 is the active tree** (copied from co-author-updated V2 on 2026-07-26). V3 is superseded.
> Status below is VERIFIED against V4's actual files on 2026-07-26, not inherited from V3.
> Full evidence: `outputs/critical-reviews/v4-audit-matrix.md`.

## Status
- Current phase: **author-controlled scientific development; no editorial submission restriction active**; V4 wording audit completed 7 August 2026; structural discrepancy identified during V5 migration on 9 August 2026. Scientific correction/QC work continues; submission restrictions will be reactivated only on explicit author instruction.
- Current task: preserve all historical V4 numbers while replacing the historical 4GM2/PfClpP interpretation. PDB 4GM2 is PfClpR; the existing 484-centroid arm is not PfClpP validation. V5's 17×4 raw Vina runs cannot replace the 484-centroid panel. Full 2F6I revalidation, downstream recomputation, and review documentation remain scientific work in progress; no editorial restriction blocks that work before explicit author reactivation. The current rescue evidence remains incomplete and is not promoted into V4 results. All CRITICAL/HIGH findings fixed by disclosure/reframing (no new calcs): C1 circular MMV ROC -> "retrodictive consistency" + lead with DEKOIS (abstract/methods/validation/table/efficiency/conclusion); C2 DiffDock-rescue softened to "consistent with/inferred"; MCMC +0.0246 mislabel -> mean +0.009 + best +0.025 + surrogate caveat; SI_pred 260 real formula; "mathematically prove"->"empirically demonstrate"; "genuinely new chemotypes"->"novel substituent combinations on preserved scaffolds"; Tartarus "independence"->"orthogonal to raw docking affinity"; PCA SM 292 PC4 fixed (0.0686/6.86%/89.19% per BMAD §1.13); redocking 5/10; median±SD notation; cover letter "validated"->"computationally benchmarked". Recompiled clean (main 39pp, SM 50pp, cover 1pp, 0 errors, 0 undef). Anti-AI 0. S23-1/H1 RESOLVED by reframe (table captions + footnote disclose metrics not retained; "optimal from N/A" claims removed; main 117 softened to defer to the figure). Epic 3 + MEDIUM ALSO DONE: M2 (fixed main 260 contradiction -- 19,913 = SYBA+MPO filter, not Tanimoto; NP-relatedness is separate 13/76 centroid analysis; 0.4 cutoff not varied), M3/H3 (generated-vs-seed activity reframed as diversity/tractability trade-off), M5 ("synthesizable" -> "predicted synthesizable (SYBA>0)" at headlines), SM 202 ("most stable"->"least sensitive... moderate not strong"), SM 269/275 ("therapeutic window" for stage activity -> "preferred predicted stage"), SM 917 figure caption ("validate...optimal"->"selected...based on comparative metrics"). Recompiled clean (main 39pp, SM 51pp, 0 errors). HISTORICAL EDITORIAL STATUS ONLY; the listed review/revalidation items are scientific work-in-progress findings, not an active pre-submission restriction. See outputs/critical-reviews/{v4-audit-matrix.md, review-*.md, final-audit.md}.
- Last updated: 2026-08-09
- **Mapping resolution (09/08/2026):** V4's V5–P2 overlay now uses the V6 source-bound candidate manifest and row-wise RDKit canonical-SMILES checks against the 68-row V5 manifest and P2 Set-C source. The integration artifact is `MOLECULAR_KEY_VERIFIED_ROW_WISE_CANONICAL_SMILES`; V6 audit and validator hashes are recorded in its provenance sidecar. No order-only mapping remains.
- **2F6I uniform revalidation (09/08/2026):** array job `13451` produced all 484 centroid directories. The independent `afterany` audit `13972` returned `FAILED_CLOSED`: 449/484 records independently passed the raw Vina checks and 35 records contain worker failures. Merge `13452` remained blocked by `afterok`; no aggregate replacement panel was promoted. A separate provenance-bound rescue was already executed in `pfclpp_2f6i_484_rescue_seed20260809_v2` with seed `20260809` and exhaustiveness `32`: 3/35 records produced raw Vina results, while 32/35 remained worker failures. A fresh author-controlled retry (job `14976`) reproduced this outcome; its audit-only dependent job `15012` recorded `RESCUE_SENSITIVITY_INCOMPLETE` with 3/35 audited passes, 32/35 failures, and zero unaccounted records. A fresh isolated attempt submitted as `14483_[0-483]` populated `pfclpp_2f6i_484_uniform_seed20260809_run13999` with **450 `result.json` + 34 `failure.json` = 484/484 attempted records**. A record-level check confirms unique centroid IDs 0–483, no result/failure overlap, and no missing IDs; its aggregate directory `pfclpp_2f6i_484_uniform_aggregate_14483` is not populated, so this attempt is not yet an accepted replacement panel. A separate older cross-pass audit covers 17 exclusions, but its scope is not identical: 16 IDs overlap the rescue-v2 set and ID 171 is cross-pass-only; it must not be combined with the 35-ID rescue denominator. The scope reconciliation is recorded in `results/pfclpp_2f6i_audit_reconciliation_20260809.json`. All layers remain sensitivity/audit evidence only, return incomplete or pending status, and make no consensus/RRS/PNS promotion. The current scheduler query has no active entry and does not recover final accounting states for these historical IDs; filesystem artifacts and audit JSONs are the authoritative evidence currently available. The V4 tree contains no distinct signed independent-review register for this 484-centroid panel; the V5/V6 four-target register must not be substituted for it.


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
- **C3, C5, DOCK-1, anti-AI, C6, F3, S23-1/H1, and Epic 3 wording corrections:** resolved by disclosure/reframing; no unsupported values were fabricated.
- **Target identity correction:** 4GM2 is PfClpR, not PfClpP; V4 text now labels the historical 4GM2 analysis as PfClpR-specific. A verified PfClpP structure is required for future PfClpP-specific work.
- **Author-action:** human approval and journal submission remain pending; Zenodo upload remains pending.

## Fix queue (7 August 2026)
- [x] C3: SI_pred is explicitly an unvalidated heuristic; no therapeutic-window claim.
- [x] C5: discovery language reframed as computational prioritization.
- [x] DOCK-1: failed docking records disclosed (71/1936; 3.7%; per-target counts retained).
- [x] Anti-AI, C6, F3, S23-1/H1, and Epic 3 wording mitigated without fabricating metrics.
- [x] Target identity: 4GM2 corrected from PfClpP to PfClpR in the manuscript package; complete 2F6I replacement remains pending.
- [ ] Full 484-centroid PfClpP/2F6I revalidation and independent review.
- [ ] Human author approval and journal submission.
- [ ] Zenodo upload.

## Phase 10 / compile (editorial compile completed 7 August 2026; structural submission gate still open)
- [x] Final adversarial/editorial/scientific review findings resolved or explicitly bounded.
- [x] Full-project temporary-clone compile: main and SM `pdflatex → bibtex → pdflatex → pdflatex` all returned 0; cover LaTeX passes returned 0.
- [x] Canonical V4 submission audit recorded in `outputs/critical-reviews/final-submission-audit-20260807.md`.
- [ ] Full 484-centroid PfClpP/2F6I revalidation and independent review.
- [ ] Human author approval and journal submission.

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
