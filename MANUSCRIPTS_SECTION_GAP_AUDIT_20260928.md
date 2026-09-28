# Audit des manquements par section — Manuscrits P1 V8 & P2 V2609C (main + SM/SI)

* **Date :** 28 septembre 2026
* **Périmètre :** conformité section par section des deux manuscrits canoniques —
`Project1_Chem_space_antimalarial_V7_CorrectedGrid/submission_ACS_P1V8/` (main 25 p. + SM 17 p.) et
`Project2_Polypharmacology_MD_ValidationV2607/manuscript/V2609C/` (main 26 p. + SM 19 p.).
* **Méthode :** lecture ciblée des sources `.tex` (sections vérifiées par grep/ligne), croisement avec
les DAR (`P1_DATA_ANALYSIS_REPORT.md` V8 ; `P2_DATA_ANALYSIS_REPORT.md` 28-09-2026), les artefacts
résultats et les exigences éditoriales JCIM/ACS. C'est un audit de **rigueur et de complétude
documentaire** — il ne remplace ni la relecture auteur ni la revue indépendante.
**Sévérités :** 🔴 MAJEUR (corriger avant toute resoumission) · 🟠 MOYEN (fortement recommandé) ·
🟡 MINEUR (cosmétique/optionnel) · ✅ CONFORME (aucun manquement détecté).

---

## Verdict global

| Manuscrit | État | Manquements |
|---|---|---|
| **P1 V8** (main + SM) | Techniquement solide ; **1 incohérence de cohorte à corriger en SM**, quelques écarts mineurs | 1 🔴 · 3 🟠 · 4 🟡 |
| **P2 V2609C** (main + SM) | Le plus abouti des deux ; 1 manquement majeur trouvé et corrigé le 28-09 (légende P2Rank contradictoire avec l'artefact), + bib `Temgoua2026` restaurée | 1 🔴✅ · 2 🟠 (1✅) · 4 🟡 |

Aucun des deux manuscrits ne promet de validation expérimentale ; les cadrages honest-negative
(ADR-0002 côté P2, null-anchoring côté P1) sont correctement appliqués.

---

## 1. P1 V8 — Main (`P1_Integrated_Polypharmacology_RRS_Main_V8.tex`)

| Section (ligne) | Constat | Sévérité | Action |
|---|---|:---:|---|
| Introduction (l.46) | Contexte, gap et question bien posés ; chiffres de fardeau cohérents | ✅ | — |
| Introduction (l.46) | Formulation type « the geographic footprint … is expanding » : à recalibrer sur le tempo épidémiologique lors de l'adaptation à la nouvelle revue | 🟡 | Reformulation douce lors du portage Digital Discovery |
| Materials and Methods (l.55) | Grilles données numériquement ; gate géométrique défini ; validation en 3 niveaux (redocking, MMV, DEKOIS 2 bras) — très complet | ✅ | — |
| Materials and Methods (l.55) | La justification biologique des centres de grille (jobs HPC 12854/12855/12859/12864, ancres vérifiées `p1_v5_pocket_centers_verified.json`) n'est **pas citée** dans le main ni le SM | 🟠 | Ajouter une phrase + référence artefact en SM (§sm_vina_matrix) — utile en réponse aux relecteurs |
| Results (l.86) | Null-anchoring explicite (RRS PfCRT 99.1–100.6 %, pipeline-null 99.4–100.5 %) ; cas PP-11 et PP-15 (112.7–131.8 %) interprétés prudemment | ✅ | — |
| Discussion (l.191) | Limites honnêtes ; pas de claim biologique | ✅ | — |
| Conclusion (l.223) | Mesurée ; appelle la validation expérimentale | ✅ | — |
| Declarations (l.240) | **Use of AI présent** et correctement formulé (l.240) | ✅ | — |
| Declarations (l.240) | Funding / ORCID : statut « en cours » selon `STATUS.md` (Day 1) — à confirmer avant resoumission | 🟠 | Finaliser métadonnées auteur |
| Global | Refus JCIM du 16/09 : le formatage est JCIM/ACS ; la cible candidate (RSC Digital Discovery) exigera un **reformatage** (template RSC, limites de mots, graphique TOC optionnel) | 🟠 | Adapter main+SM+cover DD (`submission_DD_P1V8/Cover_Letter_P1_DD.tex` déjà prêt) |

## 2. P1 V8 — SM/SI (`P1_Integrated_Polypharmacology_RRS_SM_V8.tex`, 22 sections)

| Section (ligne) | Constat | Sévérité | Action |
|---|---|:---:|---|
| S1 Cohort & evidence (l.30) | Caveat « enriched cohort, n_targets_bound=2 » correct | ✅ | — |
| S2–S3 Chemical space / Vina matrix (l.35–43) | 68/68 tracé ; bornes −12.01/−4.63 | ✅ | — |
| S4–S6 Physchem / Drug-likeness / ADMET (l.82–88) | Complets | ✅ | — |
| S7 RRS definition (l.91) | Définition + classes alignées V8 | ✅ | — |
| S8 Exploratory cross-metric (l.121) | **INCOHÉRENCE DE COHORTE** : le tableau donne PNS–RRS ρ = −0.714 (n = 17, cohorte P1) mais le §« sensitivity » (l.141) cite *raw ρ = −0.2098, partial ρ = −0.6154, n = 12* — **ce sont les statistiques P2 (Set-C complete-two-target)**, introduites dans un texte qui décrit la cohorte P1 (n = 17), sans étiquette de provenance | 🔴 | Réécrire l.141 en étiquetant explicitement la sensibilité « contrôles P2 (n = 12) à titre de comparaison inter-études » ou la recalculer sur la cohorte P1 ; sinon un relecteur y verra une contradiction interne |
| S8 (l.130–133) | Le ρ = −0.714 P1 vs le PNS–RRS P2 (−0.2098/−0.5588) : deux estimands légitimes mais jamais réconciliés noir sur blanc | 🟠 | Ajouter 2–3 lignes de réconciliation inter-estimands (cohortes, définitions PNS différentes) |
| S9 Evidence classes (l.147) | Gradients de preuve clairs | ✅ | — |
| S10–S11 MPO framework (l.150–202) | Pondérations justifiées ; portée locale annoncée | ✅ | — |
| S12 Repro & availability (l.207) | Pointe le dépôt Zenodo | ✅ | — |
| S13 Validation (l.210) | Redocking 4/5, DEKOIS 2 bras (0.502 vs 0.563, IC chevauchants), PfCRT LYS-76 + pipeline-null, multi-seed — état de l'art du projet | ✅ | — |
| S13 (l.216) | Le bras MTX-stripped n'est cité qu'une fois (« stripped » ×1) mais la prose §sm_val_dekois couvre les deux bras et les IC — conforme, faible redondance seulement | 🟡 | — |
| S14 Resources (l.248) | DOI public 10.5281/zenodo.22696778 ✓ (vérifié 16/09) | ✅ | — |
| Global | Les trois contrôles de septembre (R1.2/R2.3/R2.4) sont **tous** reflétés main+SM ✓ (c'était le trou du BMAD, corrigé le 28-09 côté BMAD) | ✅ | — |

## 3. P2 V2609C — Main (`Polypharmacology_MD_Validation_V2609C.tex`)

| Section (ligne) | Constat | Sévérité | Action |
|---|---|:---:|---|
| Introduction (l.132–142) | Cadrage Estimand Divergence + règle d'éligibilité WT + panel 39 composés GNINA ; références HOLD retirées proprement (audit 15/09) | ✅ | — |
| M&M Study design (l.150) | Critères de sélection MPO/SYBA/SI/scaffold explicites | ✅ | — |
| M&M Resistance panel (l.181) | PfDHFR/PfCRT mutants ; contexte piperaquine cité | ✅ | — |
| M&M Homology (l.203) | Seuils QMEAN/GMQE/Rama/RMSD énoncés | ✅ | — |
| M&M Docking assessment (l.207–213) | DEKOIS null assumé, MTX redock failure documenté, « GNINA yielded no usable score for this panel » cohérent avec le re-scoring du panel externe (portées différentes, bien séparées) | ✅ | — |
| M&M NP space / ADMET (l.217–223) | Descriptifs, non surinterprétés | ✅ | — |
| M&M RRS definition (l.227) | Règle \|S_WT\| < 5.0 présentée comme appliquée, pas comme nouveauté (ADR-0002 respecté) | ✅ | — |
| M&M MD protocol (l.251) | 10 ns single-replicate annoncé comme stress test | ✅ | — |
| Results (l.265–400) | Reproductibilité, estimands séparés, intersection exploratoire, parent-MD non chevauchant, Estimand Divergence 7/8 (Wilson 52.9–97.8 %), panel externe 100 % class-level — tous conformes au DAR | ✅ | — |
| Discussion (l.408–445) | Robustesse, filtre de triage, positionnement multi-cibles : mesurés | ✅ | — |
| Limitations (l.451) | 7.75 kcal/mol K76A, plancher 2.01 WT, **pH digestif 5.2 déclaré en limite (l.457)**, single-replicate assumé (clause H3 : pilier WT = 2 productions cohérentes, mutants 1 réplicat) | ✅ | — |
| Conclusion (l.464) | Mesurée | ✅ | — |
| Global | L'échec de l'attendu « 3 réplicats » (Soares) et l'abandon ≥ 25 ns sont traités au niveau Limitations/H3 — suffisant ; l'audit pH 5.2 reste PLANNED mais **n'est pas promis** dans le manuscrit (aucune référence prospective) ✓ | ✅ | — |
| Global | La trajectoire 25 ns PP-01_PfDHFR_WT (M1) n'est **pas mentionnée** au main/SM ( observation-only, cohérent avec le cadrage) ; disponible comme munition réponse-relecteurs | 🟡 | Garder en annexe de réponse, pas dans le texte |

## 4. P2 V2609C — SM/SI (`Polypharmacology_MD_Validation_SM_V2609C.tex`)

| Section (ligne) | Constat | Sévérité | Action |
|---|---|:---:|---|
| Tables S0–S19 (`\input` l.67–304) | Contenu : validation docking, homology QC, ADMET, ACSI weights, RRS by target, seuils, imputation PNS, cohort estimands, evidence scope, panel scope, K76A réplicat, P1 context, robustness transfer, multi-seed, margin sensitivity, PP-01 biophysical audit — **couverture alignée DAR** | ✅ | — |
| Ordre des `\input` | L'ordre d'inclusion n'est **pas monotone** (S12 avant S11, S9 avant S8, S16 avant S15, S19 en fin) : la numérotation **rendue** ne correspond plus aux **noms de fichiers** ; les `xr` du main résolvent par label (pas de « ?? »), mais un relecteur qui cherche « Table S15 » par nom de fichier se perdra | 🟠→✅ | **CORRIGÉ 28-09** : trois inversions intra-section réordonnées (S11↔S12, S8→S9 avec Secondary_Analyses après les deux, S15↔S16) ; recompilé 0 erreur / 0 indéfini |
| Légende Figure S4 (P2Rank) | **TROUVÉ 28-09** : la légende affichait prob 0.94/0.88/0.82/0.91 + PDB « 6L9H » + « volumes » — valeurs sans source contredisant l'artefact (`results/p2rank_boxes_20260827/` : 0.972/0.999/0.663/0.299, aucun champ volume dans le CSV) ; pour PfClpP la conclusion était **inversée** | 🔴→✅ | **CORRIGÉ 28-09** : légende réécrite sur les valeurs artefact (concordance PfCRT 5.7 Å, caveat 9N10, pas de grille 2F6I) |
| Bib `Temgoua2026` | **TROUVÉ 28-09** : clé citée ×3 (main ×2 + Table S0) mais absente de la bib (introduite par la session distante) ; le HOLD du 15-09 était un faux négatif — le DOI versionné `10.26434/chemrxiv.15007167/v1` résout (Crossref 200, posté 07-08) | 🟠→✅ | **CORRIGÉ 28-09** : entrée restaurée avec note de vérification ; main 26 p. + SM 22 p., 0 erreur / 0 indéfini |
| PP-15 (l.275–281, `tab:s_pp15`) | Section présente : MM-GBSA −29.52 ± 0.33 / −27.79 ± 0.49, multiseed 0.03 kcal/mol, écart 0.04 du score PfCRT WT expliqué honnêtement | ✅ | — |
| WT replicate consistency (l.250, Table S10) | Offset 2.01 kcal/mol, caveat autocorrélation correct | ✅ | — |
| ProLIF / Figure 4 | Données dans le main (§ l.428, Figure 4) ; le SM n'a **pas** de section ProLIF détaillée (occupances par système) | 🟡 | Optionnel : table d'occupances par système en SM pour la réponse aux relecteurs |
| Réparation PfCRT 114–122 & audit AF3/Boltz (Axis 3) | Présents dans le DAR uniquement ; **absents du SM** (choix assumé witness-only, mais utile en annexe de réponse) | 🟡 | Annexe de réponse aux relecteurs, pas besoin dans le SM soumis |
| Data availability | DOI Zenodo réservé 10.5281/zenodo.19608875, wording « reserved/future » correct — **l'upload reste à faire** avant soumission | 🟠 | Uploader le package `zenodo_package_P2/` puis basculer le wording en présent public |

## 5. Conformité transversale (les deux manuscrits)

| Item | P1 V8 | P2 V2609C |
|---|---|---|
| Chiffres tracés vers DAR/artefacts | ✅ (V8 audit 10/09) | ✅ (cohérence HPC 16/09 + audit 28/09) |
| Zéro claim expérimental / biologique | ✅ | ✅ |
| Zénodo | ✅ public (22696778) | 🟠 réservé (19608875) — upload pending |
| Use of AI | ✅ (l.240) | 🟡 à re-vérifier au format final (non trouvé par grep — possiblement dans les déclarations non couvertes par les mots-clés) |
| Titre ≤ contrainte revue | ✅ V8 | ✅ 15 mots (corrigé 15/09) |
| Package auto-contenu | ✅ `submission_ACS_P1V8/` + DD | ✅ `submission_ACS_P2V2609C/` (diff-vérifié 16/09) |

---

## Plan d'action priorisé (consolidé)

1. 🔴 **P1 SM l.141** — étiqueter/recalculer la sensibilité cross-métrique (cohorte P1 n = 17 vs stats P2 n = 12). *Effort : 30 min.*
2. ~~🟠 **P2 SM** — réaligner l'ordre des `\input`~~ **FAIT 28-09** (3 swaps intra-section, recompile 0 erreur) ; **+ fix 🔴 légende P2Rank S4 sur valeurs artefact ; + bib `Temgoua2026` restaurée (DOI ChemRxiv /v1 résout, Crossref 200 — lève le HOLD du 15-09)**.
3. 🟠 **P2** — upload Zenodo (19608875) + bascule du wording Data Availability. *Effort : 1 h.*
4. 🟠 **P1** — finaliser funding/ORCID ; citer les artefacts d'ancrage de grilles en SM ; préparer le portage Digital Discovery (template RSC).
5. 🟡 Cosmétiques : « footprint expanding » (P1 intro), annexes de réponse (25 ns M1, AF3/Boltz, ProLIF par système), vérification Use-of-AI côté P2 au format final.

