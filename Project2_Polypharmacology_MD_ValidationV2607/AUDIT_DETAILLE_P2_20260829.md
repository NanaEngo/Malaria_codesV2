# Audit détaillé — Project2_Polypharmacology_MD_ValidationV2607

**Date** : 29 août 2026
**Cible** : JCIM (manuscrit `Polypharmacology_MD_Validation_V2607.tex` + SM)
**Statut actuel déclaré** : `READING_FINAL_AUTHOR` (28 Aug 2026, DAR §9)
**Méthodologie d'audit** : (1) bonnes pratiques d'ingénierie (Twelve-Factor / Turing Way / FAIR / nf-core) ; (2) bonnes pratiques méthodologiques scientifiques (Turing Way, pré-enregistrement, calibration, cross-validation, validation expérimentale).

> **Légende sévérité** : 🔴 BLOQUANT · 🟠 MAJEUR · 🟡 MINEUR · 🟢 CONFORME

---

## 0. Synthèse exécutive

| Dimension | Verdict | Une ligne |
|---|---|---|
| Reproductibilité logicielle (Twelve-Factor) | 🟢 bon | Pipeline versionné, seed=42, hash sur inputs/outputs, manifestes JSON par étape. |
| Reproductibilité de l'environnement | 🟠 partiel | `environment_md.yml` est référencé depuis `scripts/`, pas depuis `environments/`. |
| Pipeline (Snakemake/nf-core) | 🟡 partiel | `scripts/Snakefile` orchestre C1–C14 mais ne couvre pas la chaîne Set-C. |
| Tests unitaires | 🟢 bon | `pytest tests/` → 19 passed, 1 skipped. |
| FAIR data | 🟠 partiel | Données présentes mais DOI Zenodo = `pending`. |
| Puissance statistique | 🔴 bloquant | n=12 cohorte primary ; tous p ajustés = 1.0 sur H1/H2/H3. |
| Calibration des modèles | 🔴 bloquant | DEKOIS 2.0 PfDHFR AUC = 0.45 (≈ hasard). |
| Cross-FF / cross-validation | 🟠 majeur | Un seul FF sur 16 systèmes pilote. |
| MD-RRS | 🟠 majeur | 10 ns × 16 systèmes, 1 réplicat. |
| Validation expérimentale | 🔴 bloquant | Pas d'assay PfDHFR/PfCRT. |
| Honnêteté éditoriale | 🟢 bon | Limitations étoffées (R1–R10). |
| Compilation LaTeX | 🟢 bon | main 30 p. / SM 16 p., 0 err / 0 undefined. |

**Verdict global** : 🟠 **Révision majeure recommandée**. Pipeline techniquement reproductible, scientifiquement honnête dans ses Limitations, mais ne ferme pas la boucle causale docking → MD → MM-GBSA → assay. Défendable comme papier de méthode de priorisation, pas comme papier d'affinité/résistance.

---

## 1. Question centrale et réponse bornée actuelle

### 1.1 Question centrale posée (DAR §1)

> *Does a resistance-aware, target-level computational workflow (docking-derived RRS + PNS + ACSI + targeted MD) distinguish predicted potency from predicted resilience in a chemically diverse antimalarial library — and what does a targeted MD pilot add beyond docking?*

Cette question a deux volets :
1. **Volet méthodologique** : un pipeline docking + RRS + PNS + ACSI discrimine-t-il puissance et résilience ?
2. **Volet rajout** : la MD ciblée ajoute-t-elle de l'information au-delà du docking ?

### 1.2 Réponse bornée (DAR §1, abstract, Limitations)

> *The workflow supports **computational prioritisation** but does **not** establish biological target engagement, resistance circumvention, or pathway-level mechanism.*

**Ce que la réponse bornée dit en creux** :
- Le pipeline **classe** des candidats (c'est un filtre/tri, pas un prédicteur).
- Le pipeline **ne démontre pas** que les composés touchent effectivement leur cible.
- Le pipeline **ne démontre pas** qu'ils résistent à la résistance.
- Le pipeline **ne démontre pas** qu'ils agissent sur un mécanisme pathway-level.

### 1.3 Implications de cette réponse bornée

- **Titre et abstract** doivent refléter "computational prioritisation", pas "engagement biologique".
- **Discussion** ne peut pas affirmer d'affinité mesurée, ni de potentiel thérapeutique.
- **Limitations** doivent être étoffées (ce qui est fait via R1–R10 dans `AUDIT_MITIGATIONS_P2_20260824.md`).
- **Soumission JCIM** est défendable comme **papier de méthode**, pas comme papier de découverte.

### 1.4 Pourquoi la réponse est bornée — diagnostic synthétique

1. **Boucle causale non fermée** : docking → MD → MM-GBSA n'est jamais comparé à Kd/EC50 mesurée.
2. **MD trop courte** : 10 ns × 16 systèmes mesure la géométrie locale, pas l'affinité.
3. **Divergence MD ↔ docking** : 7/8 systèmes divergent (PP-01_PfCRT_K76T seul concordant) — symptôme de modèles incomplets.
4. **Modèle docking non calibré** : DEKOIS PfDHFR AUC = 0.45 ≈ hasard.
5. **Puissance statistique insuffisante** : n=12 → tous p ajustés = 1.0 sur H1/H2/H3.
6. **Pas de pré-enregistrement** des hypothèses/seuils.
7. **Un seul FF** sur 16 systèmes — pas de robustesse inter-FF.

---

## 2. Ce qu'il aurait fallu faire (approche juste ex-ante)

### 2.1 Pré-enregistrement (Turing Way, AsPredicted, OSF)

**Avant toute campagne computationnelle** :
- Définir les hypothèses (H1 : PNS–RRS, H2 : ACSI–RRS, H3 : RRS–worst WT) **a priori**.
- Définir les seuils (RRS ≥80/70, MPO ≥0.70, class A*/A/B/C/D) **a priori**.
- Calculer la taille d'effet minimale détectable (power analysis).
- Définir un critère go/no-go : ex. AUC ≥ 0.7 sur benchmark externe = go.
- Publier le pré-protocole sur OSF ou AsPredicted avec timestamp.

**Pourquoi** : sans pré-enregistrement, les seuils et le pipeline deviennent flexibles a posteriori → risque de HARKing, p-hacking, seuils cherry-picked.

### 2.2 Calibration des modèles AVANT la campagne

**Avant de lancer le screening** :
- **Docking** : valider sur co-crystals PubChem/PDBbind (≥ 30 complexes anti-paludiques). AUC cible ≥ 0.75.
- **MM-GBSA** : benchmarker sur ligands PfDHFR avec Kd/EC50 connue (WR99210, P218, pyrimethamine, proguanil, cycloguanil). RMSE cible ≤ 1.5 kcal/mol.
- **MD** : valider la convergence (RMSD < 3 Å sur 100 ns avec 3 réplicats) avant d'extraire ΔG.
- **Critère d'arrêt** : si AUC < 0.6 ou RMSE > 2.5 → pivoter ou abandonner la voie.

**Pourquoi** : un modèle non calibré produit des résultats non-interprétables, même avec manifests et seeds.

### 2.3 Cross-validation des modèles

- **Cross-FF** sur 2-3 ligands pilotes : CHARMM36m + CGenFF, AMBER ff14SB + GAFF2, OpenFF Sage 2.3.0. Divergence > 1 kcal/mol = résultat suspect.
- **Cross-réplicats MD** : minimum 3 × 100 ns par système pour stabiliser ΔG (ou FEP alchemical avec 10-20 lambda windows).
- **Cross-structures** : WT + mutant en plusieurs conformations (NMR ensemble, MD snapshots).

### 2.4 Boucle expérimentale intégrée

- **Informer la sélection docking avec de l'affinité mesurée** : tester les 17 candidats sur PfDHFR recombinant (WT + N51I/C59R/S108N/I164L) et PfCRT (transport assay).
- **Replier la boucle** : les Kd mesurées re-entrent dans le pipeline (calibrants MM-GBSA / docking).
- **Sans cette boucle**, "polypharmacologie prédite" = spéculation, même avec manifests.

### 2.5 Reproductibilité interne (déjà en place)

- ✅ Manifests JSON par étape, seed=42, runs SLURM horodatés, hash sur inputs/outputs.
- ⚠ Manque : container pinné par SHA, tests d'invariance OS/driver GPU.

### 2.6 Ce que la démarche juste aurait donné (vs ce qu'on a)

| Aspect | Démarche juste | Démarche réelle |
|---|---|---|
| Pré-enregistrement | OSF timestampé | ❌ absent |
| Critère go/no-go | AUC ≥ 0.7 | ❌ AUC = 0.45 → pas d'arrêt |
| Cohorte | n ≥ 50 (calcul de puissance) | 17 → 12 primary |
| Calibration docking | AUC ≥ 0.75 validée | 0.45 (≈ hasard) |
| Cross-FF | 2-3 FF pilotes | 1 seul (CHARMM36m + OpenFF) |
| MD | 3 × 100 ns | 1 × 10 ns |
| MM-GBSA calibré | RMSE ≤ 1.5 kcal/mol | 1 réplicat, non calibré |
| Boucle assay | Kd/EC50 mesurée | ❌ absente |

**Conclusion** : l'approche réelle a produit un pipeline de tri défendable, mais sans les garde-fous méthodologiques qui auraient permis de transformer le tri en prédiction. La réponse bornée est **cohérente avec ce qu'on a fait, pas avec ce qu'il aurait fallu faire**.

---

## 3. Ce que nous avons fait — bilan factuel

### 3.1 Données primaires (COMPUTED)

| Livrable | État | Référence |
|---|---|---|
| 17 candidats Set-C (MPO ≥ 0.70, SYBA > 0, SI > 10) | ✅ | `results/candidate_selection/` |
| 136 systèmes docking Vina 1.2.7 (17 × 8 cibles/états) | ✅ | `results/docking_mutants.csv` |
| Classes RRS target-balanced (A*:1, A:1, B:4, C:5, D:1) | ✅ | `results/c_rrs_classification.csv` |
| Classes RRS available-target (A*:5, A:1, B:5, C:5, D:1) | ✅ | `results/c_rrs_classification.csv` |
| ACSI scores (2/17 > 0.70, mean 0.543) | ✅ | `results/c_acsi_scores.csv` |
| PNS scores (centralité STRING 700 + imputation PfCRT) | ✅ | `results/c_pns_ranking.csv` |
| Audit statistique (Spearman + 100k perm + 10k boot + Bonferroni) | ✅ | `results/cross_metric_statistical_audit.{csv,json}` |
| Sensibilité imputation PfCRT (ρ 0.9632–1.0000) | ✅ | `results/pns_imputation_sensitivity.{csv,json}` |
| 16 trajectoires MD 10 ns (PP-01/PP-02 × 8 états) | ✅ | `results/set_c_md/md_systems/.../runs/` |
| QC 16/16 PASS (`setc_p2_minheavy_5A_ge10percent_v1`) | ✅ | `results/set_c_md/post_production_manifest_pilot.json` v3 |
| MD-RRS discriminatif (16 records, 12 ratios) | ✅ | `results/set_c_md/md_rrs_discriminative_pilot.csv` |
| MM-GBSA 16/16 (range [−35.29, −24.53]) | ✅ | `results/set_c_md/mmgbsa_20260819/` |
| DEKOIS 2.0 PfDHFR (AUC = 0.45 [0.37, 0.53]) | ✅ | P1 V7 (référencé depuis P2) |
| Tartarus calibration (ρ = 0.013, p = 0.091) | ✅ | P1 V7 (référencé) |
| Réplication externe 39 ligands (312/312 finite) | ✅ | `results/external_docking_aggregate_20260827/` |
| GNINA CNN consensus 312/312 (38/38 class A concordant) | ✅ | `results/robustness_transfer_20260827/gnina_consensus_20260828/` |
| P2Rank 2.5.1 (PfCRT top pocket score 162.7) | ✅ | `results/p2rank_boxes_20260827/` |
| ProLIF 2.2.1 IFP 16/16 (descriptif) | ✅ | `results/prolif_ifp_20260827/` |
| STRING 400/700/900 sensitivity (ρ 0.9975 400 vs 700) | ✅ | `results/string_threshold_sensitivity_20260829/` |
| PP-15 + PP-01 multi-seed redocking (±0.03 / ±0.05) | ✅ | `results/pp15_docking_20260828/`, `results/pp01_docking_20260829/` |

### 3.2 Données secondaires (COMPUTED, descriptives)

| Livrable | État | Référence |
|---|---|---|
| LOO + perturbations ±1 kcal/mol + bootstrap | ✅ | `results/lightweight_robustness/` |
| ΔΔG ± SD per mutant (R8) | ✅ | `mmgbsa_ddeltaG_pilot.csv` |
| Corrélation partielle PNS-RRS \| MW + scaffold (R9) | ✅ | `partial_corr_input_table.csv` |
| Bootstrap classes (R3) | ✅ | `lightweight_runs_summary.json` |
| WT réplicat R1 vs R2 (offset 2.01 kcal/mol < 1 SD) | ✅ | `results/set_c_md/single_rerun_20260825/` |
| MD-filter retention gate (7/12 pass) | ✅ | `results/rrs_polypharma_secondary_20260828/` |
| WT replicate consistency (SM Table S10) | ✅ | `manuscript/LaTeX/Table_S10_WT_Replicate_Consistency.tex` |

### 3.3 Données NOT_COMPUTED (par design)

| Livrable | État | Raison |
|---|---|---|
| Full-panel MD-RRS (17 × 8 = 136) | `NOT_COMPUTED` by design | Pilot = PP-01/PP-02 seulement |
| Validation expérimentale (IC50 PfDHFR, transport PfCRT) | `pending` | Pas de labo biochimique partenaire |
| Zenodo DOI | `pending` | Archive non uploader |
| Cross-FF (AMBER, OpenFF 2.3.0) | `pending` | Coût GPU non budgété |
| FEP alchemical | `pending` | Idem |
| FEP/SMD on PP-01/PP-02/PP-15 | `pending` | Idem |

### 3.4 Honneur — l'honnêteté méthodologique (déjà présente)

- ✅ Section Limitations étoffée (R1–R10) — toutes les préoccupations des reviewers sévères anticipées et documentées.
- ✅ Résultats négatifs non enterrés : DEKOIS 0.45, dissociations 164/201, MM-GBSA R1 vs R2 = 2.01, MM-GBSA PfATP4 +473 kcal/mol.
- ✅ "Docking-RRS is not MD-RRS" (DAR §7, README §Evidence boundary).
- ✅ "Docking-score uncertainty" (~±1 kcal/mol > plusieurs marges de classe) — Limitations.
- ✅ "MD as filter" argument pour les dissociations — vend la dissociation comme une force du pipeline.
- ✅ Cross-estimand separation (target-balanced vs coverage-sensitive).

### 3.5 Reproductibilité et FAIR (état actuel)

| Élément | État | Note |
|---|---|---|
| Manifestes JSON par étape | ✅ | 7+ manifestes versionnés |
| Seed 42 sur tous les audits | ✅ | Audits déterministes |
| Hash SHA-256 sur inputs/outputs | ✅ | Vérifiable |
| Tests pytest | ✅ | 19 passed, 1 skipped |
| environment_md.yml | ⚠ | Vivant dans `scripts/`, pas `environments/` |
| Container pinné (Apptainer/Docker) | ❌ | Manquant |
| DOI Zenodo | ❌ | `pending` |
| `git diff --check` | ✅ | Validation post-modif |
| Snakemake pipeline complet | 🟡 | C1–C14 seulement, pas Set-C |

---

## 4. Comment mitiger / rattraper

### 4.1 Court terme (avant soumission JCIM, ~1-2 semaines)

| # | Action | Coût | Bénéfice | Statut |
|---|---|---|---|---|
| M1 | Déplacer `environment_md.yml` → `environments/` + corriger README | 5 min | Cohérence AGENTS | À faire |
| M2 | Uploader package Zenodo + récupérer DOI | 1 h | FAIR complet | À faire |
| M3 | Reformuler question centrale : "le pipeline est-il non-orthogonal au hasard sur benchmarks découplés ?" | 30 min | Honnêteté accrue | À faire |
| M4 | Ajouter Brier + AUPRC (en plus d'AUC DEKOIS) | 1 h | Calibration transparente | À faire |
| M5 | Ajouter phrase Methods justifiant OpenFF 2.2.0 + AM1-BCC vs CGenFF | 15 min | Anticipe R2-style | À faire |
| M6 | `pytest` dans `malaria_md` (env canonique AGENTS) | 30 min | Cohérence tests | À faire |
| M7 | CI GitHub Actions (`pytest`, `ruff`, `pdflatex` smoke) | 2 h | Reproductibilité continue | À faire |
| M8 | Ajouter `LICENSE` au root P2 | 5 min | FAIR | À faire |

### 4.2 Moyen terme (post-soumission ou v2, ~3-6 mois)

| # | Action | Coût | Bénéfice | Statut |
|---|---|---|---|---|
| R1 | Étendre cohorte à 50+ candidats (P1 a 19 913 leads) | 2-3 sem GPU | Puissance statistique (p ajusté < 0.05 atteignable) | À faire |
| R2 | Cross-FF PP-01/PP-02 × 8 (AMBER ff14SB + GAFF2.11) | 2 sem GPU | Robustesse inter-FF | À faire |
| R3 | MD triplée 100 ns PP-01 + PP-02 (WT + 4 mutants PfDHFR, WT + 2 mutants PfCRT) | 1 mois GPU | ΔG avec incertitude réelle | À faire |
| R4 | Calibrer MM-GBSA sur 5 ligands PfDHFR avec IC50 (WR99210, P218, pyrimethamine, proguanil, cycloguanil). Cible RMSE ≤ 1.5 kcal/mol | 1 sem compute | Calibration error bars | À faire |
| R5 | FEP alchemical (10-20 lambda windows) sur top-3 class A* | 3-6 mois GPU | ΔG absolu avec incertitude | À faire |
| R6 | IC50 PfDHFR recombinant (WT + N51I/C59R/S108N/I164L) sur PP-01/PP-02/PP-15 | 6 mois + financement | Ferme la boucle causale | À faire |
| R7 | Transport assay PfCRT (SPR/MST sur protéoliposomes K76T vs WT) | 6 mois + financement | Ferme boucle PfCRT | À faire |
| R8 | Pré-protocole OSF : hypothèses, seuils, go/no-go, taille d'effet, multiplicité | 1 sem | Standard Turing Way | À faire |

### 4.3 Long terme (refonte structurelle, ~6-12 mois)

| # | Action | Bénéfice |
|---|---|---|
| L1 | Refactoriser pipeline Set-C en `nextflow.config` nf-core-style (règles nommées, containers par étape, `params.yaml`) | Reproductibilité DAG ; alignement nf-core |
| L2 | Produire `Dockerfile` / `apptainer.def` pinnant GROMACS 2025.4 + CUDA + cuDNN + OpenFF 2.2.0 + CHARMM36m | Mobilité de compute |
| L3 | Renommer scripts en `rule_*` (convention Snakemake/nf-core) | Convention nf-core |
| L4 | Tests d'intégration : 1 ligand × 1 mutant × 100 ps exécutable en CI en < 10 min | Smoke test bout-en-bout |
| L5 | Technical Note séparé : "PfATP4 CHARMM36→AMBER conversion artifact in gmx_MMPBSA" (+473 kcal/mol) | Visibilité communauté |

---

## 5. Mieux valoriser scientifiquement ce qui a été fait

### 5.1 Reconnaître que la réponse bornée EST le résultat principal

**Pivot narratif** : la "réponse bornée" n'est pas un échec — c'est un **résultat méthodologique fort**. Elle dit :
> *Un pipeline docking+MD+MM-GBSA, appliqué avec toute la rigueur de reproductibilité moderne (manifestes, seeds, hashs, 19 tests pytest), ne peut pas démontrer l'engagement biologique ou la résistance. C'est précisément la valeur du pipeline : il sait ce qu'il ne peut pas dire.*

**À valoriser dans la couverture éditoriale** :
- Abstract : "computational prioritisation, not biological engagement" est **déjà** un acte d'honnêteté.
- Title : ne pas promettre ce que la méthode ne peut pas donner.
- Introduction : citer Turing Way + MLOps sur la calibration des modèles en drug discovery.

### 5.2 Les 7 forces à préserver et mettre en avant

| Force | Comment la valoriser |
|---|---|
| **Honnêteté radicale des Limitations** (R1–R10) | Citer explicitement "we report what the method cannot do" comme une contribution positive au champ. |
| **Séparation estimand primary vs sensitivity** | Section Methods dédiée : "Estimands, primary analysis, sensitivity analysis" — modèle COSORT/STROBE pour in silico. |
| **Multiplicité corrigée** (Bonferroni-Holm sur 3 hyp.) | Mettre en avant comme standard minimal pour in silico screens. |
| **Incertitudes** (bootstrap 10k, permutation 100k) | Tableau de bord d'incertitude dans Results, pas juste un point estimate. |
| **Cross-validation multi-outils** (GNINA + external 39 + Tartarus + P2Rank + ProLIF) | Schéma de cross-validation explicite dans Methods/Results. |
| **Traçabilité manifeste** (JSON par étape) | Section Data Availability avec liens directs aux manifestes. |
| **Code source + tests pytest** | Dépôt GitHub public + DOI Zenodo + badge CI. |

### 5.3 Trois angles de publication alternatifs ou complémentaires

#### Angle A — **Papier de méthode** (chemin actuel, défendable)
*Titre* : "A reproducible, bounded, target-level computational pipeline for polypharmacology candidate prioritisation in antimalarial discovery."
*Cible* : JCIM, J. Cheminform., Bioinformatics.
*Message* : le pipeline trie honnêtement, avec tous les garde-fous modernes, et sait ce qu'il ne peut pas dire.
*Force* : déjà presque prêt (compilation propre, limitations étoffées).
*Faiblesse* : AUC DEKOIS 0.45 doit être prominent dans l'abstract.

#### Angle B — **Étude de calibration négative** (pivot, plus fort scientifiquement)
*Titre* : "Why docking-derived resistance resilience scores are not validated by short MD: a calibration study with 17 polypharmacology candidates."
*Cible* : JCIM, J. Chem. Inf. Model. (sister journal Briefings in Bioinformatics).
*Message* : 7/8 systèmes divergent entre docking et MD 10 ns → la MD est un filtre, pas une validation. La calibration sur benchmarks externes (DEKOIS 0.45) montre la limite du docking.
*Force* : résultat négatif **publiable** (Mlinarič et al. 2018, Open Med Chem J — les études négatives sont rares et précieuses).
*Faiblesse* : il faut accepter de pivoter le narratif actuel.

#### Angle C — **Étude de reproductibilité** (méta-science)
*Titre* : "Reproducibility audit of a polypharmacology MD validation pipeline: manifests, seeds, hashes, and what they buy you."
*Cible* : Nat. Methods, PLOS Comput Biol, JOSS (Journal of Open Source Software).
*Message* : 150+ scripts, 7+ manifestes, 19 tests, seed=42, hashs SHA-256 — voici ce que la reproductibilité permet et ne permet pas de capturer.
*Force* : la rigueur reproductible est un livrable en soi, surtout dans un champ où la plupart des études ne documentent que les résultats.
*Faiblesse* : audience plus restreinte.

#### Recommandation
- **Court terme** : soumettre l'**Angle A** à JCIM (déjà prêt).
- **Moyen terme** : pivoter en **Angle B** si reviewers majeurs, ou publier les deux en parallèle.
- **Long terme** : archive logicielle (JOSS) en **Angle C** comme livrable compagnon.

### 5.4 Valoriser les artefacts déjà produits

| Artefact | Valorisation possible |
|---|---|
| 7+ manifestes JSON par étape | DOI Zenodo, archive ouverte |
| 19 tests pytest | Badge CI, badge coverage |
| P2Rank + ProLIF audits | Supplementary Note "Independent pocket and interaction audits" |
| GNINA consensus (38/38 class A) | Highlighted Result : "CNN scoring reproduces Vina retention-not-gain pattern" |
| External replication 39 ligands | Highlighted Result : "Cross-cohort replication supports the retention pattern" |
| WT R1 vs R2 (2.01 kcal/mol < 1 SD) | Highlighted Result : "Endpoint noise floor established at ~2 kcal/mol" |
| STRING 400/700/900 (ρ 0.9975) | Highlighted Result : "Network-derived score is threshold-robust" |
| PP-15 + PP-01 multi-seed (±0.03, ±0.05) | Highlighted Result : "Docking prioritization is not seed-sensitive" |

### 5.5 Valoriser le négatif

Le résultat le plus important est peut-être **DEKOIS AUC = 0.45** : un paper qui le rapporte honnêtement et en tire les conséquences (pivoter de "prédiction" vers "triage") est plus utile au champ qu'un paper qui le cache ou l'ignore. Mettre cet élément dans :
- L'abstract (1 phrase).
- La section Results (1 paragraphe dédié).
- La section Discussion (1 paragraphe avec implications).
- Le Supplementary Information (Table S0 récapitulant toutes les calibrations).

### 5.6 Le méta-point à défendre en réponse aux reviewers

> *Notre contribution n'est pas un classement de candidats prometteurs — c'est la démonstration qu'un pipeline de priorisation computationnelle, même avec toute la rigueur de reproductibilité moderne (manifestes, seeds, hashs, tests), reste un outil de triage et non un prédicteur d'engagement biologique. Le prochain saut nécessite la calibration sur benchmarks découplés (DEKOIS 0.45) et la boucle expérimentale. Notre honnêteté sur ce point est la contribution méthodologique.*

---

## 6. Verdict final

### Six forces à préserver
1. Honnêteté radicale des Limitations (R1–R10).
2. Séparation estimand primary vs sensitivity (COSORT/STROBE-style).
3. Multiplicité corrigée (Bonferroni-Holm).
4. Estimations d'incertitude (bootstrap 10k, permutation 100k).
5. Cross-validation multi-outils (GNINA + external + Tartarus + P2Rank + ProLIF).
6. Traçabilité manifestes JSON par étape.

### Trois faiblesses à affronter
1. AUC DEKOIS = 0.45 (modèle non-calibré) — **doit figurer dans l'abstract**.
2. n=12 → tous p ajustés = 1.0 — **reformuler la question** (R1 rattrapage via extension cohorte).
3. Pas de validation expérimentale (boucle non fermée) — **engager labo partenaire** (B6/B7).

### Recommandation finale
1. **Court terme** : compléter M1–M8 (1-2 jours), soumettre **Angle A** (papier de méthode) à JCIM.
2. **Moyen terme** : pivoter vers **Angle B** (calibration négative) si reviewers majeurs ; lancer R1 (extension cohorte), R2 (cross-FF), R3 (MD triplée 100 ns), R4 (calibration MM-GBSA).
3. **Long terme** : archive logicielle (Angle C) sur JOSS, R5 (FEP), R6/R7 (boucle expérimentale), R8 (pré-protocole OSF), L1–L5 (refonte nf-core).

---

## 7. Annexes — Pointeurs d'évidence

| Élément | Chemin |
|---|---|
| DAR | `Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md` (455 lignes) |
| Audit adversarial | `docs/PRX_adversarial_review_P2_20260824.md` + `AUDIT_MITIGATIONS_P2_20260824.md` |
| Audit gaps P2/P5 | `docs/P2_P5_SEVERE_REVIEW_GAP_AUDIT_20260828.md` |
| Roadmap | `docs/P1_P5_RRS_POLYPHARMA_ROADMAP.md` |
| Suggestion originelle | `P2_Sugg.md` (5 failles + plan défense) |
| Manifestes | `results/p2_*.json`, `results/set_c_md/*.json` |
| Tests | `tests/test_rigorous_audit.py`, `test_lightweight_robustness.py`, `test_pfcrt_pipeline.py` |
| Env | `scripts/environment_md.yml` (⚠ à déplacer) |
| Pipeline | `scripts/Snakefile` (C1–C14 seulement) |
| Manuscrit | `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` + `_SM_V2607.tex` |
| AGENTS racine | `/home/nanaengo/Malaria_codesV2/AGENTS.md` (règle DAR avant manuscrit) |

---

*Rapport généré le 29 août 2026 — verdict : 🟠 Révision majeure recommandée, 🟢 Honnêteté méthodologique forte, 🔴 Boucle expérimentale manquante. La soumission JCIM est défendable comme **papier de méthode de priorisation** si le cadre "prioritisation, pas engagement" est maintenu et défendu en réponse aux reviewers. La réponse bornée est cohérente avec ce qui a été fait ; elle devient une force si on accepte de pivoter le narratif vers la calibration négative et l'angle méta-scientifique.*
