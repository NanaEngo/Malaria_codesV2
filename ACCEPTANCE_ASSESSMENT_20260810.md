# Point d'Acceptation Global P1–P5 — 10 août 2026

**Version 1.0 — 10 août 2026.** Synthèse des 5 packages de soumission (P1 V6, P2, P3, P4, P5) : état factuel, estimation de probabilité d'acceptation, risques résiduels, actions restantes avant chaque dépôt. Source : roadmap v1.8, manifestes de soumission, registres de revue, jobs SLURM, `FINAL_CROSS_REVIEW_20260810.md`.

---

## 1. Tableau de synthèse

| # | Package | Journal cible | État | Est. acceptation* | Bloquants réels | Actions restantes |
|---|---------|---------------|------|:-----------------:|:----------------|-------------------|
| **P1 V6** | P1 V6 Integrated Polypharmacology+RRS | JCIM (ACS) | ✅ Package ACS complet (20 fichiers), TOC conforme, register levé | **80–85 %** | Aucun bloquant | ORCID + funding dans Paragon Plus, lecture auteur finale |
| **P2** | Polypharmacology MD Validation | JCIM (ACS) | 🔄 Manuscrit prêt (25+3 p.) ; **MD Set-C en cours** (jobs 15106/15111/15117) | **75–80 %** (→ 80–85 % après MD-RRS) | 16 systèmes MD + QC + MD-RRS à produire | ⏳ **Option B retenue** : attendre les jobs MD (15106→15111→15117) puis intégrer les résultats et mettre à jour l'abstract |
| **P3** | Quantum-Inspired Representations | JoC (Springer) | ✅ Benchmarks canoniques + extval complète ; compiles propres | **~82 %** (cible ≥85 %) | Zenodo (upload différé par choix auteur) | Upload Zenodo (DOI réservé), lecture auteur |
| **P4** | Pareto MCTS + oracles | JoC (Springer) | ✅ v12-activity intégré, recompilé RC=0 (11+4 p.) | **~70–75 %** | Aucun (risque scientifique : MCTS ≤ Random) | Checks finaux JoC (TOC/graphical abstract si requis), lecture auteur |
| **P5** | GNN/Transformer Drug Discovery | JoC (Springer) | ✅ Benchmark + validation indépendante 100 % | **~75–80 %** | Aucun (risque : verdict honnête-négatif) | Checks finaux JoC + Zenodo, lecture auteur |

*Estimations basées sur les audits documentés (roadmap v1.8, AGENTS.md) et le contexte éditorial ; à lire comme un intervalle indicatif, pas une garantie.

---

## 2. Détail par package

### P1 V6 — JCIM (ACS) — ✅ PRÊT À DÉPOSER
**Preuves :** audit numérique complet (0 erreur, 1 correction de wording appliquée 10/08) ; register `PENDING_INDEPENDENT_REVIEW` **levé** (décision auteur `INTERNAL_WORK_AUTHORIZED`, commit `c6b9eb720`) ; 5 risques JCIM (R1–R5) **tous résolus** (TOC 3.25×1.75 in conforme, déclaration Use-of-AI, paragraphe validation protocole docking, cover letter datée) ; package `submission_ACS_P1V6/` (20 fichiers : main 19 p. + SM 5 p. + cover 1 p. + TOC PDF/TIFF 300/1200 dpi + figures ≥300 dpi + .bbl + .aux xr) ; revue adverse croisée finale 6 corrections appliquées (DEKOIS 0.450, PfClpR non-évalué, MMV 3 cibles).
**Actions restantes :**
1. **ORCID** du corresponding author (renseigné dans Paragon Plus, étape auteurs — pas dans le .tex, convention ACS)
2. **Funding sources** (si applicable)
3. **Lecture auteur finale** main (19 p.) + SM (5 p.)
4. Renseigner les métadonnées Paragon Plus (keywords L43 ✓, déclarations ✓)

### P2 — JCIM (ACS) — 🔄 EN ATTENTE D'UN JEU DE RÉSULTATS (optionnel pour soumettre)
**Preuves :** manifeste complet (main 25 p. / SM 3 p. / cover / Table S0 / Table S5) ; R11 **résolu** (Table S5 ADMET complétée avec vraies prédictions ADMET-AI 17/17, bug Set-A→Set-C corrigé, commit `569c41dcb`) ; revue croisée : DEKOIS 0.450 partout, PfClpR non-évalué, MMV 3 cibles, table RRS 17 scaffolds.
**État MD Set-C (jobs en cours) :**
- **15106** (équilibration, 16 systèmes) : 4 en RUNNING (indices 4/6/7/8), 7 en PENDING (9–15), 0 échec — ETA dépend de la file
- **15111** (production 16×10 ns, `--dependency=afterok:15106`) : PENDING — ~40 h après équilibration
- Chaîne post-production validée end-to-end : `p2_setc_trajectory_qc.py` → `p2_setc_md_rrs.py` (md_rrs_status = NOT_COMPUTED jusqu'au QC)
**Actions restantes :**
1. **Option A (soumettre maintenant)** : le manuscrit est soumissible tel quel — l'abstract positionne le MD-RRS en « future work » ; aucune incohérence
2. **Option B (attendre ~2–3 j)** : analyser 15106 → 15111 → QC → MD-RRS ; si les résultats arrivent, remplacer le wording « future work » de l'abstract et enrichir Results (gain estimé +5 %)
3. Dans les deux cas : ORCID, funding, lecture auteur
4. **Recommandation :** soumettre P1 V6 et P2 ensemble (paper compagnons) — la revue croisée a garanti la cohérence des valeurs partagées (DEKOIS 0.450, RRS par-cible, 17 candidats)

### P3 — JoC (Springer) — ✅ PRÊT (Zenodo en attente)
**Preuves :** benchmarks canoniques complets (ECFP4 0.9475, hybrid 0.8876, ablation QK Δ=−0.040, QKS 6q ≈ RBF p=0.060) ; **validation externe complète** (ChEMBL 22 447 mol : ECFP4 0.9601, TFP 0.8645, TNE 0.6448 ; QKS 0.8172 vs RBF 0.8466, p=0.021 corrigé-resamplé) ; audit statistique job 13998 terminé ; **citation compagnon P2 propre** (`temgoua2027md`, main [22] / SM [5], note « submitted for publication » — commit `e2efd1076`) ; dépendance morte P3→P2 retirée ; compiles 13+17 p., 0 erreur.
**Actions restantes :**
1. **Upload Zenodo** — DOI réservé `10.5281/zenodo.19608875`, manifest 858 fichiers / 569.4 MB prêt ; **différé par choix auteur** (gain estimé +3 % → ~85 %)
2. Lecture auteur finale (13 p. main, 17 p. SM)
3. Vérifier si JoC exige un **graphical abstract** (si oui : TOC 3.25×1.75 in à générer comme pour P1 V6)

### P4 — JoC (Springer) — ✅ PRÊT (checks finaux)
**Preuves :** **oracle d'activité public intégré (v12)** dans le Pareto MCTS (6e objectif, poids 0.10, échelle continue type RRS, commit documenté) ; **re-benchmark v12 complet** (job 12865, 20 seeds×4 méthodes) : Random 0.6724 > MCTS 0.6649 > GA 0.6453 > Greedy 0.4278 (t₁₉=−4.97, p=0.0001) ; manuscrit basculé sur v12 (abstract/table/figure/Methods/SM/cover letter), recompilé RC=0 (11 p. main, 4 p. SM) ; QMC retiré du manuscrit (diagnostic non publication-grade, décision documentée).
**Actions restantes :**
1. Checks finaux JoC (mêmes vérifications éditoriales que P3 : graphical abstract si requis, déclarations)
2. **Risque scientifique à assumer :** MCTS ≤ Random — narratif « framework méthodologique » et ablation honnête déjà en place ; l'oracle activité (v12) documente la non-domination
3. Lecture auteur finale

### P5 — JoC (Springer) — ✅ PRÊT (checks finaux + Zenodo)
**Preuves :** benchmark complet (GIN–TFP random 0.9084, GIN–TNE 0.8918 ; scaffold : ECFP4 0.8300 > tous) ; stats re-dérivées (paired-t df=4 + BH-FDR) ; **validation indépendante 100 %** : (1) re-dérivation `p5_replicate_stats.py` exacte, (2a) ECFP4-RF replication Δ=0.0000, (2b) GIN replication PASS (ρ=0.70), (3) **benchmark public ChEMBL 22 267 mol** (ECFP4-RF 0.9547 vs GIN 0.9237, p=0.0001) → verdict honnête-négatif non-artefact ; audit adverse v2 §10 ; pas de SM (pas de références supplémentaires).
**Actions restantes :**
1. Checks finaux JoC (déclarations, graphical abstract si requis)
2. **Zenodo** (manifest P5 inclus dans le dépôt global)
3. Lecture auteur finale (13 p.)

---

## 3. Risques transverses (déjà gérés)

| Risque | Statut |
|--------|--------|
| Incohérences cross-package (DEKOIS 0.509/0.450, PfClpR, MMV 4→3 cibles, register) | ✅ Revue adverse croisée 10/08 — 6 corrections appliquées (`693ac5322`) |
| Recompilation reviewer (xr/`\externaldocument`) | ✅ `.aux` ajoutés aux packages P1 V6/P2/P3/P4 ; dépendance morte P3→P2 retirée (`282fec8df`) |
| Références compagnons | ✅ P3 cite P2 proprement (main [22], SM [5]) ; entrées non-résiduelles dans les 5 bib |
| Résidus de rapport dans les bibliographies | ✅ Note placeholder P3 corrigée (`e2efd1076`) |
| Jobs en cours | ⏳ 15106 (eq Set-C) RUNNING, 15111 (prod) PENDING — ne bloquent que l'option B de P2 |

---

## 4. Ordre de soumission recommandé

1. **P1 V6** (JCIM) — le plus mûr (80–85 %), package ACS complet, aucun bloquant
2. **P2** (JCIM) — en parallèle/juste après (compagnon ; cohérence garantie) ; **Option B retenue** (MD-RRS doit être intégré — chaîne 15106→15111→15117 active, ETA ~40–48 h)
3. **P3** (JoC) — après upload Zenodo (gain ~3 %) si l'auteur le réactive
4. **P5** (JoC) — après checks finaux + Zenodo
5. **P4** (JoC) — en dernier (risque scientifique MCTS ≤ Random à assumer dans la narration)

## 5. Prochaine étape immédiate
- Décision auteur : **soumettre P1 V6 maintenant** (OUI/NON) → si OUI, préparer les métadonnées Paragon Plus (ORCID, funding) ; 
- Décision P2 : **Option B retenue** (MD-RRS doit être intégré — chaîne 15106→15111→15117 active, ETA ~40–48 h) ;
- Réactivation éventuelle de l'**upload Zenodo** (P3/P4/P5) — différé par choix auteur (10/08).
