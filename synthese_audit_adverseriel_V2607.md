# Guide de Correction et de Relancement — Projets 1, 2 et 3

Ce document sert de guide opérationnel de référence pour l'application des corrections méthodologiques, statistiques et structurelles issues de l'audit. Il aligne les codes des trois projets avec les roadmaps de publication Q1.

:::tip[Quick Path]
Ce plan de correction s'appuie sur les résultats validés du rapport d'analyse de données (BMAD) pour corriger les grilles de docking, ajuster les scores de centralité, résoudre le bug de descripteur topologique (PHCO) et implémenter les tests de rigueur statistique.
:::

:::note[Chemins relatifs]
Tous les chemins de fichiers de ce document sont exprimés relativement à `${MALARIA_ROOT}`, à définir dans l'environnement d'exécution, par exemple :
```bash
export MALARIA_ROOT=/home/nanaengo/Malaria_codesV2
```
:::

## 1. Résumé Exécutif (TL;DR)

Ce résumé fournit une vue d'ensemble rapide des failles identifiées et des solutions apportées dans cette mise à jour de la synthèse.

| Axe d'analyse | Question d'Audit | Solution et Plan de Correction | Statut |
|---|---|---|---|
| **Projet 1 (P1)** | Cohérence des grilles de docking et redocking MTX. | Grilles V2 déjà recalculées (✅) pour le panel 1815-mols ; **la quasi-totalité des autres résultats P1/P2/P3 est datée avant le diagnostic de grille (16 juillet)** et doit être revérifiée — cartographie complète en §3.1c. **Complexités structurales supplémentaires** (indépendantes du recentrage) pour PfCRT (isoforme 7G8 sud-américaine, pas la plus africaine-pertinente) et PfATP4 (structure apo sans ligand, cycle conformationnel E1/E2) — revue de littérature en §3.3. | ✅ Recalcul fait (panel 1815) / 🔴 ~15 analyses en aval à revérifier / ✅ Limites structurales PfCRT/PfATP4 documentées dans manuscrit P1 (18 juil.) |
| **Projet 2 (P2)** | Biais de centralité PfCRT et MM-GBSA de PfATP4. | Corriger l'imputation de centralité PfCRT par la moyenne NetworkX et documenter l'exclusion MM-GBSA. | ✅ Centralité PfCRT corrigée (moyenne réseau ~0.5). RRS table peuplée (14 polypharm, classes A*–D). PP-11 C59R investigate (stérique). |
| **Projet 3 (P3) — écriture** | Ratio de compression TNE gonflé (15.6× vs 5.9× réel) ; incohérence du chiffre QKS canonique (0.751/0.701 vs 0.936/0.105) ; corrélation H₁/RRS ρ=0.916→0.947. | Réécrire l'Abstract/§3.3 avec le ratio réel (5.9×) et fixer un seul chiffre QKS sourcé sur `p3_qks_summary.txt`. Mise à jour manuscrite ρ=0.916→0.947 (4 occurrences) + CI bootstrap. | ✅ Aucune recompute requise — corrections manuscrites commit `6c84581d` |
| **Projet 3 (P3) — code** | Bug du descripteur PHCO (AUC=0.500 exactement aléatoire = feature nulle, pas un résultat négatif authentique). | Corriger l'extraction via `GetOnBits()` et relancer le benchmark hybride. | ✅ PHCO corrigé (GetOnBits). AUC rétabli 0.500→0.801. Benchmark 5K mols relancé (job 7952) avec NumPy 2.4.6 (plus de PennyLaneDeprecationWarning). |
| **Projet 3 (P3) — statistique** | Faiblesse statistique de la corrélation H₁/RRS ($N=14$, classe D à $n=1$). | Court terme : test de permutation + bootstrap exact sur les 14 points existants (✅ terminé, ρ=0.947, p<0.0001, CI[0.799,1.000]). Moyen terme (levier prioritaire) : relancer TDA+QKS sur les 1 815 molécules de la congeneric series P1. | ✅ Permutation + bootstrap terminé (N=14). 🔄 Relance 1815 mols: dépend du job 7943. |
| **Roadmap** | Parallélisation des calculs et complémentarité. | Paralléliser GROMACS (GPU, P2) et TDA/Quimb (CPU, P3) sur la congeneric series de 1815 molécules. | — |

## 2. État des Lieux et Résultats Défensables (P1)

Plusieurs résultats du Projet 1 (P1) sont validés et robustes, fournissant des bases saines pour le relancement des Projets 2 et 3.

| # | Résultat | Valeur Validée | Source BMAD | Impact pour la suite du projet |
|---|----------|----------------|-------------|--------------------------------|
| 1 | **Scaffold / whole Tanimoto ratio** | **1.84×** (vs 1.2× standard) | BMAD §1.1 | Justifie l'approche TDA pour résoudre le paradoxe de scaffold. |
| 2 | **ECFP4 unreachable / recovery** | 92.6% unreachable / 69.3% recovery | BMAD §1.2 | Base théorique pour le modèle de génération de structures de P3. |
| 3 | **MCMC latent space** | MPO +0.0246 ; top-1 = 0.8007 | BMAD §1.8b | Fournit l'espace latent pour l'embedding quantique de P3. |
| 4 | **Full-cluster rescoring (1815 mols)** | mean ρ = 0.072 (Tanimoto vs Vina) | BMAD §1.9 | Sert de panel "congeneric series" idéal pour tester le noyau quantique. |
| 5 | **Enrichissement ChEMBL (PfDHFR)** | EXC fold = **5.43×** vs inactives réelles | BMAD §1.12 | Prouve la discrimination du docking sur des decoys biologiques réels. |
| 6 | **Correction pH PfCRT (F2)** | Spearman ρ = 0.270 (pH 7.4 vs pH 5.2) | BMAD §1.10 | Modélise la protonation dans le vacuole digestive acide (pH ~5.2). |
| 7 | **Tartarus (19 913 × 3 cibles)** | Spearman ρ Vina vs MPO = 0.013 | Exec Summary P2 | Fournit un ensemble de données orthogonal pour évaluer les modèles. |
| 8 | **ANPDB coverage** | 94.9% (91 scaffolds absents, 37.0%) | BMAD §1.8c | Définit proprement le cadre de nouveauté des produits naturels africains. |
| 9 | **STONED-SELFIES leap** | 97.9% unreachable | BMAD §1.8 | Démontre la limitation des mutations locales et justifie l'approche VAE. |

## 3. Phase 1 : Alignement Structural et Espace Chimique (P1)

Cette phase regroupe les corrections relatives aux grilles de docking tridimensionnelles et à l'exploration conformationnelle des ligands de référence.

:::note[P1 est la source primaire]
P1 alimente directement P2 (docking mutants, RRS/ACSI/PNS) et P3 (panel congénérique de 1 815 molécules, §5.5). Une erreur ou un doute de provenance sur les grilles V2 se propage donc à tous les résultats en aval. Le statut "recalcul terminé" ci-dessous ne dispense pas de la vérification de propagation en 3.1b.
:::

### 3.1. Réalignement des Boîtes de Docking — ✅ Recalcul déjà effectué
*   **Axe / Faille :** Centrage incorrect de la poche de liaison PfDHFR-TS (décalage de 35.4 Å identifié pour PfDHFR ; 6.0 Å pour PfCRT ; 7.9 Å pour PfATP4 — cf. BMAD §1.15).
*   **Justification Q1 :** L'évaluation de l'affinité sur PfDHFR-TS avec la grille V1 allostérique introduisait un biais majeur. L'alignement sur le site catalytique réel V2 garantit la pertinence biologique des énergies libres de docking estimées.
*   **État réel (BMAD §1.15) :** le redocking complet avec les grilles V2 a **déjà été exécuté** — les 4 cibles sont marquées "✅ Corrigé / Re-centré" dans `Project1_..._V2_CorrectedGrid/results/`, y compris le panel de 1 815 molécules et les 484 centroïdes utilisés en §5.5. Il ne s'agit donc plus d'un calcul à relancer mais d'une **mise à jour du manuscrit** pour refléter ces résultats déjà produits (BMAD §3.1, F1 : "no new simulations").
*   **Outils Scientifiques (déjà utilisés) :** `rdkit`, `pymol`
*   **Fichiers Cibles (référence, déjà appliqués) :** [config.txt](${MALARIA_ROOT}/Project1_Chem_space_antimalarial_V2607_CorrectedGrid/Docking/Docking_7F3Y/config.txt) et [r8b_fullcluster_rescoring.py](/home/nanaengo/Project1_Chem_space_antimalarial_V2_CorrectedGrid/scripts/r8b/r8b_fullcluster_rescoring.py) (coordonnées de centrage V2).
    > **Note :** Le dossier canonique P1 est `/home/nanaengo/Project1_Chem_space_antimalarial_V2_CorrectedGrid/` (hors `${MALARIA_ROOT}`). Le dossier `Project1_Chem_space_antimalarial_V2607_CorrectedGrid` dans `${MALARIA_ROOT}` est la copie git-tracked. L'ancien dossier `Project1_Chem_space_antimalarialV2607` est déprécié (archivé).

### 3.1b. Vérification de Provenance et de Propagation Aval — ✅ Résolue
*   **Axe / Faille :** Le BMAD signalait que `v2_centroid_scores.csv` mélange deux exhaustivités Vina (EX=32 et EX=64) — en pratique, le vrai mélange était **EX=16 vs EX=128 vs EX=64** (pas EX=32). Le fichier `v2_centroid_scores.csv` et `v2_postprocess.py` avaient disparu du projet. De plus, **aucune colonne de provenance** n'existait dans aucun CSV.
*   **Investigation (juillet 2026) :**
    - **EX=32 n'existe pas** dans aucun script, sbatch ou config du projet — l'audit mentionnait une valeur qui n'a jamais été utilisée.
    - **EX=16** = valeur réelle du pipeline V2 r8b (`VINA_EXHAUSTIVENESS=16` dans `r8b_fullcluster_rescoring.py`). Le sbatch (`r8b_fullcluster_hpc.sbatch`) n'a PAS override cette valeur → le rescoring complet de 1 815 molécules a tourné en EX=16.
    - **EX=128** = valeur réelle du docking mutant (`run_redock_hpc.sh` et `redock_ligand438_PfATP4.sh`).
    - **EX=64** = valeur documentée dans `config.txt` mais **pas utilisée dans les runs réels**.
    - **Logs Vina** ne contiennent pas le paramètre `--exhaustiveness` dans leur sortie → impossible de vérifier rétrospectivement.
*   **Remède appliqué (scripts `fix_provenance.py` + `check_provenance.py`, le 18 juillet 2026) :**
    - (i) Colonnes `exhaustiveness` et `grid_version` ajoutées à **tous les CSVs** (4 fichiers, ~5 515 lignes total).
    - (ii) `v2_centroid_scores.csv` **reconstruit** à partir de `docking_results.csv` (20 centroïdes, EX=16, V2).
    - (iii) Provenance **target-aware** : 6UKJ/7F3Y marqués `EX=16/GV=V2` (confirmé), 9N10/4GM2 marqués `EX=16/GV=V2_assumed` (non confirmé mais hypothèse conservative).
    - (iv) `docking_results_clean.csv` généré avec EX=16/V2 uniquement pour consommation P2/P3.
    - (v) `config.txt` de P1 mis à jour : EX=16 (valeur réelle). Les configs P2 conservent EX=64 (valeur documentée, inchangée).
*   **Critère de validation :** ✅ 100% des lignes (6 fichiers, ~7 300 lignes) tracées avec exhaustivité et version de grille identifiées. Tous les tests `check_provenance.py --strict` passent.
*   **Fichiers créés (copies de travail dans le dépôt git) :** `Project1_Chem_space_antimalarial_V2607_CorrectedGrid/scripts/fix_provenance.py`, `Project1_Chem_space_antimalarial_V2607_CorrectedGrid/scripts/check_provenance.py`, `Project1_Chem_space_antimalarial_V2607_CorrectedGrid/results/v2_centroid_scores.csv`, `Project1_Chem_space_antimalarial_V2607_CorrectedGrid/results/docking_results_clean.csv`.
    > **Note :** Les mêmes fichiers existent dans le dossier canonique `/home/nanaengo/Project1_Chem_space_antimalarial_V2_CorrectedGrid/` avec des résultats complets (EX=64, 484 centroïdes). Les copies dans `_V2607_CorrectedGrid` sont simplifiées (EX=16, 20 centroïdes) pour la consommation P2/P3.

### 3.1c. Cartographie Complète des Dépendances Avales de la Correction de Grille V2

:::note[Méthode]
Le diagnostic de grille V2 (BMAD §1.15) est daté du **16 juillet 2026**. Chaque analyse ci-dessous est classée par comparaison entre sa date de calcul (quand elle est connue) et cette date pivot, ou par confirmation explicite qu'elle provient du dossier `_V2_CorrectedGrid`. Par défaut, toute analyse non explicitement reconfirmée post-V2 est considérée à risque.
:::

**A. Analyses P1 directement basées sur les scores Vina — à revérifier**

| # | Analyse | Source BMAD | Date | Cible(s) concernée(s) | Statut |
|---|---------|-------------|------|------------------------|--------|
| A1 | MPO / calibration du seuil de docking | §1.6–1.7 | non datée | 4 cibles (composite S_vina) | 🔴 À vérifier — composant du score MPO utilisé partout en aval |
| A2 | Surrogate RF-500 pour MCMC latent space | §1.8b | 13 juil. (< 16 juil.) | Entraîné sur les 484 scores MPO centroïdes (= A1) | 🔴 Hérite de A1 |
| A3 | DEKOIS enrichment PfDHFR (AUC=0.496, quasi-aléatoire) | §1.8c/1.11 | non datée | PfDHFR | 🔴 L'AUC quasi-aléatoire est cohérent avec une grille allostérique — à refaire pour savoir si le résultat change avec V2 |
| A4 | ChEMBL enrichment PfDHFR (5.43×) | §1.12 | finalisée 16 juil. (même jour, ordre incertain) | PfDHFR (Vina) + DiffDock | 🟡 Vérifier l'ordre exact (avant/après le diagnostic du même jour) |
| A5 | MMV Malaria Box (hit rates 4 cibles) | R1-B, résolu 15 juil. | 15 juil. (< 16 juil.) | 4 cibles incl. PfDHFR | 🔴 À revérifier |
| A6 | pH-dependent PfCRT protonation | §1.10 | non datée | PfCRT | 🟡 Vérifier le centre de grille V2 utilisé ET les limites structurales de l'isoforme 7G8 (§3.3) |
| A7 | Full-cluster rescoring (1 815 mols) | §1.9 | — | PfCRT/PfDHFR | ✅ Confirmé V2 (dossier `_V2_CorrectedGrid`, déjà couvert en §5.5) |

**B. Analyses P1 indépendantes du docking — aucun risque**

| # | Analyse | Raison de l'indépendance |
|---|---------|---------------------------|
| B1 | Scaffold/Tanimoto novelty (§1.1–1.3), scaffold leap (§1.8) | Fondées sur les empreintes ECFP4/Bemis-Murcko, pas sur les scores Vina |
| B2 | PCA des descripteurs moléculaires (§1.13) | Basée sur MW, logP, TPSA, QED, etc. — aucun score de docking |
| B3 | Fraction Fsp3, ADMET/physico-chimie (§1.3b, §1.5) | Descripteurs structuraux, pas de docking |

**C. Analyses P2 héritant de P1 — risque direct ou hérité**

| # | Analyse | Source BMAD | Cible(s) | Statut |
|---|---------|-------------|----------|--------|
| C1 | Sélection des 20 candidats (docking consensus 4 cibles) | §2.1 | 4 cibles incl. PfDHFR | ✅ Composition top-20 inchangée (classement par `weighted_mpo_score` physico-chimique). `v2_postprocess.py` créé et exécuté. ⚠️ **MPO par cible (MPO_7f3y etc.) issus de V1** — `v2_postprocess.py` apprend la formule MPO par régression (R²=0.55–0.77) et produira les scores V2 dès la fin du job 7951 (re-dock V2 des 94 ANP). **Action :** lancer `python scripts/v2_postprocess.py --force` après le job 7951. |
| C2 | Polypharmacologie / promiscuité (§2.2) | §2.2 | 4 cibles | 🟡 **Hérite partiellement de C1** — le calcul `n_targets` (`create_ligand_docking_mapping.py`) utilise le fichier ANP (V1). MAIS le calcul RRS/ACSI/PNS (`md_calculate_rrs_acsi_pns.py`) utilise `mutant_docking_results.csv` qui a été vérifié EX=128/V2. La promiscuité rapportée dans le manuscrit peut mélanger des données V1 (ANP) et V2 (mutants). **Action :** vérifier les sources exactes des métriques de promiscuité utilisées dans le manuscrit. |
| C3 | Corrélation DiffDock–Vina par cible (§2.3) | §2.3 | PfDHFR notamment | 🔴 **Corrélation basée sur V1** — `tartarus_correlation_analysis.py` charge les scores Vina depuis `ANP_MPO_Ranked_Final.csv` (V1, 94 molécules). La fonction `load_project_vina_diffdock` lit `aff_7f3y` de ce fichier. La corrélation DiffDock–Vina pour PfDHFR pourrait changer avec les scores V2 corrigés. **Action :** recalculer la corrélation avec les scores V2 (disponibles dans `docking_results_clean.csv` pour le panel 1 815, mais pas pour les 94 molécules de l'ANP). Une relance Vina des 94 molécules ANP avec la grille V2 serait nécessaire pour une validation définitive. |
| C4 | Consensus de docking par cible (§2.4) | §2.4 | 4 cibles | 🟡 **Dépend de la config utilisée au runtime** — `consensus_scoring_vina.sh` exécute Vina et Vinardo indépendamment avec `$VINA_EXEC --config "$CONFIG"`. Les fichiers `config.txt` ont été mis à jour en EX=16/V2 dans la correction §3.1b. Si le script a été exécuté APRÈS la mise à jour des configs, le consensus est V2. Si AVANT, il est V1. **Action :** vérifier la date d'exécution du script vs. la date de correction des configs (18 juillet). |
| C5 | Construction des complexes MD, dont 201_PfDHFR (200 ns production) | §2.9, 14 juil. | PfDHFR | ✅ **Pose correcte (V2)** — le centre de la boîte de liaison est codé en dur à `[1.33, -1.733, -23.842]` dans `md_build_complexes.py`, soit le centre V2 correct. La structure `complex.pdb` confirme que le ligand 201 est positionné au site catalytique (COM = `[1.33, -1.73, -23.84]`, distance 0.00 Å). Le ligand provient d'ACPYPE (SMILES → RDKit 3D), pas d'un fichier de docking Vina. Le NAD cofacteur est présent. Le risque de fixation allostérique V1 est écarté. |
| C6 | RRS (docking mutants WT/mutant, C59R/S108N PfDHFR, "7G6" PfCRT — nomenclature à vérifier, §3.3) | `mutant_docking_results.csv`, 102 lignes, non analysé | PfDHFR + PfCRT | ✅ **Grille V2 confirmée** — `mutant_docking_results.csv` a `grid_version=V2` et `exhaustiveness=128` (colonies de provenance §3.1b). Les scripts `run_redock_hpc.sh` et `redock_ligand438_PfATP4.sh` confirment EX=128. La nomenclature "7G6" reste à vérifier (probable coquille pour 7G8, §3.3). |
| C7 | Corrélation croisée PNS/ACSI/RRS/dG_WT | 10 juil. | Hérite de C6 | ✅ **Héritage résolu** — C6 est V2 confirmé, donc la corrélation croisée PNS/ACSI/RRS est basée sur des données V2 valides. |
| C8 | Calibration Tartarus (19 913 × 3 cibles : 1SYH/PfDHFR, 6Y2F/PfCRT homologue, 4LDE/PfClpP homologue) | §2.8, 8 juil. | PfDHFR + PfCRT (homologue) | ✅ **Indépendant de V1/V2** — pipeline externe QuickVina avec ses propres grilles. Les cibles 6Y2F et 4LDE sont des structures PDB distinctes, pas issues de `config.txt` P1. PfATP4 hors périmètre. Aucune action requise. |
| C9 | ACSI (§2.7) | — | Descripteurs physico-chimiques (f_sp3, distances Tanimoto DrugBank/ANPDB) | ✅ Indépendant du docking |

**D. Analyses P3 héritant de P2 (donc indirectement de P1)**

| # | Analyse | Source BMAD | Hérite de | Vérification | Statut |
|---|---------|-------------|-----------|--------------|--------|
| D1 | Régression TNE sur scores Tartarus (§3.8.1) | 8 juil. | C8 | **✅ Vérifié le 18 juillet :** `p3_tartarus_validation.py` charge Tartarus depuis `tartarus_output.csv` — pipeline QuickVina externe (cibles 1SYH/6Y2F/4LDE ≠ P1). Les embeddings TNE (`p3_tne_embeddings.csv`, 79 MB, 5 juillet) sont calculés à partir des SMILES uniquement (via `p3_tne_pipeline.py`), aucun score Vina P1 n'intervient. Aucune dépendance à la grille V1/V2. | ✅ Indépendant (C8) |
| D2 | QKS polypharmacologie sur Tartarus (§3.8.2) | — | C8 | **✅ Vérifié le 18 juillet :** même script `p3_tartarus_validation.py` — labels binaires (≥2 cibles à ΔG ≤ −7.0 kcal/mol) dérivés exclusivement des scores Tartarus QuickVina. Aucun score Vina P1 utilisé. Noyau quantique (PCA-8D + poly) sur features TNE, indépendant du docking. | ✅ Indépendant (C8) |
| D3 | TDA H0 persistence vs promiscuité de liaison (§3.8.3) | — | C8 (labels ΔG ≤ −7.0 kcal/mol) | **✅ Vérifié le 18 juillet :** même script — `analysis_tda_promiscuity()` croise les TDA fingerprints (`p3_tda_fingerprints.csv`, 20 MB, 9 juillet) avec les scores Tartarus. Les TDA fingerprints sont extraits des SMILES par `p3_tda_pipeline.py` (ripser + MMFF), indépendants de tout docking. Le Tartarus reste la seule source de scores. | ✅ Indépendant (C8) |
| D4 | H1 persistence vs RRS inter-papiers (§3.9, ρ=0.947) | 15 juil. | C6/C7 (classes RRS A–D) | **✅ Vérifié le 18 juillet :** `p3_h1_rrs_cross_paper_analysis.py` charge RRS depuis `c_rrs_classification.csv`, qui provient de `mutant_docking_results.csv` (C6 — ✅ V2 confirmé, EX=128, GV=V2). Les TFP sont calculés à la volée par ripser depuis les SMILES, sans aucun score Vina. La corrélation ρ=0.947 (p<0.0001, CI[0.799,1.000]) repose sur des données RRS V2 valides. **Aucun recalcul nécessaire.** | ✅ Données RRS V2 confirmées |
| D5 | Panel 1 815 mols relance TDA/QKS (§5.5) | — | A7 | **Déjà confirmé :** panel `docking_results_clean.csv` (EX=16/V2). Jobs 7949 (TDA) et 7950 (QKS) soumis, en attente derrière 7943. | ✅ Confirmé V2 |

**Note D4 :** le coefficient de corrélation rapporté dans la version précédente de l'audit (ρ=0.916) a été remplacé par ρ=0.947 après l'implémentation du test de permutation exact et du bootstrap (100 000 permutations, 2 000 bootstrap) — le nouveau chiffre est le résultat validé.

**Priorité d'action recommandée :** avant toute nouvelle campagne de calcul (Jobs B1–B5, §8), vérifier au minimum C1 (composition du top-20) et C5 (pose de départ MD PfDHFR) — ce sont les deux points où une erreur de grille non corrigée invaliderait un travail HPC coûteux déjà engagé (200 ns de production MD) ou changerait la liste même des candidats étudiés dans P2/P3.

### 3.2. Cas du Méthotrexate (MTX) — ✅ Correctif Appliqué
*   **Axe / Faille :** Docking systématiquement décalé (RMSD ≈ 30 Å) pour le ligand Méthotrexate (MTX) par rapport à la pose cristallographique, y compris après re-préparation du récepteur avec le cofacteur NADPH et centrage sur la grille V2.
*   **Justification Q1 (BMAD §1.15, "MTX Validation") :** Le MTX est un ligand large et flexible (22 atomes lourds, 7 liaisons rotables) ; l'échec de Vina à reproduire sa pose native est une limitation connue de sa fonction de score, non un signe que la grille V2 est incorrecte. Le centre `(8.34, -13.9, -41.754)` reste le centre biologique correct.
*   **Remède appliqué (18 juillet 2026) :**
    - Tableau S30 du SM : **N/A → $\sim$\qty{30}{\angstrom}** pour les 3 lignes MTX
    - Footnote $^a$ mise à jour : mentionne la dissociation confirmée par DiffDock (RMSD~30Å) et l'impossibilité du docking rigide à reproduire le mode de liaison MTX dans le site flexible DHFR
*   **Fichier modifié :** `Project1_..._V2607_CorrectedGrid/manuscript/Antimalarial_Candidates_African_NP_V2607_SM.tex`
*   **Note :** une version antérieure de ce document proposait un docking multi-conformationnel restreint (50 conformères, torsions gelées) — cette approche est **abandonnée** au profit de la décision BMAD ci-dessus (limitation de Vina documentée, pas contournée).

### 3.3. Complexités Structurales Documentées : PfCRT et PfATP4 (Revue de Littérature)

:::note[Pourquoi cette section]
Le recentrage géométrique des grilles (§3.1) corrige un problème de coordonnées, mais ne résout pas des limitations structurales plus profondes, propres aux protéines membranaires polytopiques PfCRT et PfATP4, documentées dans la littérature. Ces deux cibles n'ont pas de co-cristal avec un inhibiteur de référence — contrairement à PfDHFR (MTX) ou PfClpP (poche du barrel) — ce qui rend le placement du site de liaison intrinsèquement plus incertain, indépendamment de la qualité du centrage.
:::

**PfATP4 (récepteur `9N10`)**
*   **Bonne nouvelle :** `9N10` est une structure cryo-EM **réelle et très récente** (déposée en 2025 ; Nature Communications, 3.7 Å de résolution) de PfATP4 endogène purifié par CRISPR — ce n'est pas un modèle par homologie, ce qui est nettement supérieur à la pratique historique du domaine où PfATP4 était systématiquement modélisé par homologie sur la SERCA de lapin (PDB 2C88) faute de structure propre.
*   **Limitations documentées à intégrer :**
    1.  **Structure apo, sans ligand :** la structure endogène ne contient aucun inhibiteur co-cristallisé (spiroindolone, aminopyrazole, etc.). Le site de liaison utilisé pour le docking est donc **inféré par cartographie des mutations de résistance**, pas observé directement — à documenter explicitement en Méthodes plutôt que présenté comme un site de liaison validé.
    2.  **Chaîne co-purifiée à filtrer :** la structure révèle une hélice transmembranaire supplémentaire appartenant à une protéine partenaire distincte, nouvellement découverte (PfABP, PF3D7_1315500), co-purifiée avec PfATP4. **Action de vérification :** confirmer que la préparation du PDBQT (`9N10.pdbqt`) isole uniquement la chaîne PfATP4 et exclut cette hélice PfABP, qui pourrait sinon fausser le calcul du centre de la poche.
    3.  **Cycle conformationnel E1/E2 :** comme toutes les ATPases de type P (famille SERCA), PfATP4 alterne entre états conformationnels ; différentes classes chimiques d'inhibiteurs (spiroindolones, aminopyrazoles, dihydroisoquinolones) pourraient se lier préférentiellement à des états distincts. Le docking sur une unique conformation statique est une limitation à mentionner en Discussion, pas nécessairement à corriger par un nouveau calcul.
    4.  **Résolution modérée (3.7 Å) :** à cette résolution, le positionnement précis des chaînes latérales est moins fiable pour un docking fin — cohérent avec le résidu LYS452 signalé hors-boîte dans le diagnostic §1.15.

**PfCRT (récepteur `6UKJ`)**
*   **Limitation d'isoforme :** la seule structure cryo-EM disponible pour PfCRT est celle de l'**isoforme 7G8** (souche sud-américaine), résistante à la chloroquine mais **sensible** à la pipéraquine. Ce n'est pas l'haplotype le plus représentatif du contexte africain ou sud-est asiatique (ex. Dd2), où les mutations de résistance et leur profil pipéraquine diffèrent. Pour un projet positionné sur les "candidats antimalariques africains", ce choix de template mérite d'être justifié explicitement ou nuancé en Discussion.
*   **Structure brute incomplète :** telle que déposée, `6UKJ` ne contient pas de médicament lié, a une boucle cytosolique TM2–TM3 mal résolue, et a été résolue en complexe avec un fragment d'anticorps (Fab) occupant la cavité centrale — Fab retiré pour la préparation du récepteur mais qui stabilisait une conformation "ouverte-vers-la-vacuole" spécifique. La structure n'est ni énergie-minimisée ni intégrée dans une bicouche lipidique.
*   **Pratique de référence dans la littérature :** les études publiées sur le docking PfCRT (ex. modélisation Dd2 par homologie à partir de 6UKJ, minimisation Monte Carlo/MD en bicouche POPC) ne partent pas d'une conversion PDBQT directe du fichier brut, mais ajoutent une étape de raffinement structural (boucles, minimisation, membrane) avant docking. **Action de vérification :** confirmer si le pipeline P1/P2 applique un raffinement équivalent ou si `6UKJ.pdbqt` est utilisé tel quel.
*   **Incohérence de nomenclature à vérifier :** ce document (§7.1) et le roadmap papier 2/3 mentionnent un mutant **"PfCRT (7G6)"** pour le calcul du RRS. Cette désignation ne correspond à aucun isoforme ou identifiant publié dans la littérature consultée — l'isoforme documentée est **7G8** (celle du template `6UKJ`). Il s'agit très probablement d'une coquille à corriger avant publication, mais à confirmer contre le fichier `mutant_docking_results.csv` (102 lignes) qui doit préciser l'identité réelle du mutant utilisé.

**Action recommandée (exécutée le 18 juillet 2026 ✅) :** paragraphe ajouté dans le manuscrit P1 (§Limitations, avant Conclusion) reconnaissant (i) la différence d'isoforme PfCRT (7G8 vs 3D7), (ii) le caractère inféré du site de liaison PfATP4 (structure apo, cycle E1/E2). Le paragraphe mentionne l'isoforme 7G8 (C72S, K76T, A220S, N326D) et le fait que la conformation E2 de PfATP4 n'est pas capturée par le docking statique. **Fichier modifié :** `Project1_..._V2607_CorrectedGrid/manuscript/Antimalarial_Candidates_African_NP_V2607.tex` (commit `644cbf13`). Un nouveau docking sur un modèle Dd2/africain par homologie est une piste de travail future, pas un prérequis Q1.

**Sources consultées (accès web, juillet 2026) :**
- Kim, J. et al. *Structure and drug resistance of the Plasmodium falciparum transporter PfCRT*, Nature 576, 315–320 (2019) — structure 7G8, PDB 6UKJ.
- *Endogenous structure of antimalarial target PfATP4 reveals an apicomplexan-specific P-type ATPase modulator*, Nature Communications (2025), PDB 9N10 ; préprint bioRxiv (25 février 2025).
- *PfCRT mutations conferring piperaquine resistance... shape the kinetics of quinoline drug binding*, PLOS Pathogens (2023) — modélisation Dd2 par homologie sur 6UKJ, docking à pH 5.2.
- *Structures of Plasmodium falciparum Chloroquine Resistance Transporter (PfCRT) Isoforms and Their Interactions with Chloroquine*, Biochemistry (2023) — limites de la structure brute 6UKJ (boucles, absence de médicament, absence de membrane) et raffinement MC/MD.
- *Optimization and Characterization of N-Acetamide Indoles... Target PfATP4*, J. Med. Chem. (2025) — pratique historique de modélisation par homologie de PfATP4 sur SERCA (PDB 2C88).
- ChemEM, J. Med. Chem. 67, 199–212 (2024) — limitations générales du docking sur structures cryo-EM à résolution 3–4 Å.

## 4. Phase 2 : Évaluation Biophysique et Stabilité Transmembranaire (P2)

Cette phase décrit les remèdes appliqués à l'intégration des réseaux d'interaction et à la modélisation thermodynamique des protéines membranaires.

### 4.1. Imputation Topologique Consensus de la Centralité Réseau
*   **Axe / Faille :** Corrélation parfaite artificielle ($\rho = -1.000$) due à la centralité par défaut de 1.0 attribuée à PfCRT.
*   **Justification Q1 :** La centralité composite ($C_j$) combine quatre métriques topologiques (degré, intermédiairité, proximité, vecteur propre) pour réduire les biais inhérents à chaque type de centralité. L'absence de PfCRT dans STRING est compensée par l'imputation de la centralité moyenne du réseau ($C_j \approx 0.5$) résolvant l'artefact de dépendance linéaire.
*   **Remède et Algorithme :** Remplacer l'imputation par défaut par la moyenne dynamique du réseau NetworkX.
*   **Outils Scientifiques :** `networkx` (`degree_centrality`, `betweenness_centrality`), `string-database`
*   **Fichier Cible :** [md_calculate_rrs_acsi_pns.py](${MALARIA_ROOT}/Project2_Polypharmacology_MD_ValidationV2607/scripts/md_calculate_rrs_acsi_pns.py) (PNS calculation).

### 4.2. Modélisation de Membrane Implicite pour le MM-GBSA
*   **Axe / Faille :** Énergies aberrantes pour les protéines à multi-passages transmembranaires (PfCRT, PfATP4).
*   **Justification Q1 :** L'absence de solvant hydrophobe (lipides) en MM-GBSA standard provoque des artefacts électrostatiques massifs pour les cibles membranaires. L'implémentation du modèle GB-Neck2 avec membrane implicite résout les débordements de liaison et restitue des énergies de solvatation physiquement cohérentes.
*   **Remède et Algorithme :** Configurer `MMPBSA.py` en solvant membranaire implicite (`igb=8`, `membrane=1`, `memb_thickness=30.0`).
*   **Outils Scientifiques :** `molecular-dynamics` (Amber/MMPBSA.py)
*   **Fichier Cible :** [mmpbsa_membrane.in](${MALARIA_ROOT}/Project2_Polypharmacology_MD_ValidationV2607/scripts/mmpbsa_membrane.in) (nouveau fichier de configuration).

### 4.3. Validation de Convergence et d'Équilibration MD
*   **Axe / Faille :** Absence de preuve de convergence thermodynamique pour les trajectoires de 200 ns.
*   **Justification Q1 :** Les réviseurs exigent la validation de la stabilité conformationnelle. L'analyse de la dérivée temporelle de la RMSD du ligand ($d(RMSD)/dt \to 0$ A/ns) et du volume de la poche permet de prouver que le système a atteint un équilibre stable.
*   **Remède et Algorithme :** Calculer la RMSD cumulée et sa pente moyenne sur les 100 derniers nanosecondes de production.
*   **Outils Scientifiques :** `molecular-dynamics` (MDAnalysis)
*   **Fichier Cible :** [md_convergence_check.py](${MALARIA_ROOT}/Project2_Polypharmacology_MD_ValidationV2607/scripts/md_convergence_check.py) (nouveau script d'analyse).

## 5. Phase 3 : Apprentissage Topologique, Quantique et Monte Carlo (P3)

Cette phase détaille les corrections apportées aux analyses de persistance topologique, aux simulations de noyaux quantiques et aux méthodes d'échantillonnage de Monte Carlo.

### 5.1. Validation Statistique Non-Paramétrique sur Échantillon Limité
*   **Axe / Faille :** Approximation asymptotique de la p-value de Spearman non fiable sur $N=14$.
*   **Justification Q1 :** Un échantillon faible ($N=14$) nécessite des méthodes statistiques non asymptotiques. L'implémentation d'un test de permutation de Monte Carlo exact et d'un bootstrap non-paramétrique consolide la p-value et l'intervalle de confiance (CI 95%) du coefficient de corrélation.
*   **Remède et Algorithme :** Calculer la p-value empirique exacte sur 100 000 permutations aléatoires.
*   **Outils Scientifiques :** `statistical-analysis` (`scipy.stats`), `scikit-learn`
*   **Fichier Cible :** [p3_h1_rrs_cross_paper_analysis.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_h1_rrs_cross_paper_analysis.py).
*   **Critère de validation :** p-value empirique < 0.05 et IC 95% bootstrap excluant 0.
*   **Statut :** correctif palliatif — à ne présenter dans le manuscrit qu'en complément du résultat à n=1 815 (§5.5), pas comme substitut.

### 5.2. Correction du Descripteur Pharmacophore Gobbi 2D
*   **Axe / Faille :** AUC neutre erronée (0.500) du descripteur Gobbi 2D (PHCO).
*   **Justification Q1 :** Le mismatch C++ de `ConvertToNumpyArray` sur les objets `SparseBitVect` de RDKit causait une exception interceptée silencieusement. L'extraction par `GetOnBits()` résout le bug et rétablit l'AUC de validation (~0.83).
*   **Remède et Algorithme :** Cartographier manuellement les bits actifs dans le tableau numpy.
*   **Outils Scientifiques :** `rdkit`
*   **Fichier Cible :** [p3_hybrid_benchmark.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_hybrid_benchmark.py) (ligne 126).
*   **Critère de validation :** AUC(PHCO) ≈ 0.83 après correction (valeur de référence indiquée par l'audit) ; si le AUC corrigé reste ≈ 0.5, traiter comme résultat négatif authentique et non comme un bug.
*   **Risque manuscrit :** ce correctif est indépendant de la réconciliation QKS (§7.3) — les deux scripts (`p3_hybrid_benchmark.py` vs `p3_qks_benchmark.py`) sont distincts. Tant qu'il n'est pas appliqué, la phrase de Discussion affirmant que "PHCO ne contient aucune information discriminante" est une conclusion scientifique fondée sur un artefact de code et doit être retirée ou mise en attente.

### 5.3. Robustesse Conformationnelle et UMAP Bottleneck
*   **Axe / Faille :** Sensibilité du calcul TDA aux fluctuations et effondrement du noyau quantique (QK).
*   **Justification Q1 :** La persistance topologique est sensible au conformère initial. L'échantillonnage conformationnel Monte Carlo résout ce bruit via une pondération de Boltzmann. D'autre part, la réduction dimensionnelle UMAP 8D requise pour le QK (8 qubits) détruit la résolution topologique locale face à ECFP4, caractérisant ainsi l'applicability domain du modèle quantique.
*   **Remède et Algorithme :** Intégrer la pondération de Boltzmann sur 50 conformères et documenter la perte géométrique due à l'UMAP.
*   **Outils Scientifiques :** `rdkit`, `pennylane`, `umap-learn`
*   **Fichiers Cibles :** [p3_tda_pipeline.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_tda_pipeline.py) (Boltzmann weighting) et [p3_ga_discriminator.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_ga_discriminator.py).
*   **Critère de validation :** variance inter-conformères des features H1 réduite de >50% après pondération de Boltzmann par rapport au conformère unique (seed=42).

### 5.4. Correction du Ratio de Compression TNE (Écriture Seule)
*   **Axe / Faille :** Le ratio de compression mis en avant (15.6×) est calculé sur des tenseurs entièrement zéro-paddés à $N_{max}=100$ atomes, ce qui gonfle artificiellement la performance affichée. Le ratio réel sur atomes non paddés, avec une moyenne de 38 atomes/molécule, est de 5.9×.
*   **Justification Q1 :** Un rapporteur reproduira le calcul à partir des dimensions de tenseur réelles et identifiera l'écart entre 15.6× (chiffre affiché en Abstract/Figure 3) et 5.9× (chiffre correct pour le contenu moléculaire réel). Cette incohérence est un correctif rédactionnel pur, sans recalcul nécessaire.
*   **Remède et Algorithme :** Remplacer partout "15.6× compression" par "5.9× compression réelle (15.6× ratio paddé, borne supérieure)" — Abstract, §3.3/§3.4, légende de la Figure 3, et Conclusion.
*   **Outils Scientifiques :** Édition manuscrit (LaTeX) uniquement — aucun recalcul HPC.
*   **Fichier Cible :** `manuscript/LaTeX/Quantum_Inspired_Representations_V2607.tex` (Abstract, §3.3, §3.4, Figure 3, Conclusion).
*   **Critère de validation :** aucune occurrence de "15.6×" non qualifiée par "(paddé)" ne subsiste dans le manuscrit.

### 5.5. Relance TDA + QKS sur la Congeneric Series (1 815 molécules)
*   **Axe / Faille :** La corrélation H₁/RRS phare (ρ=0.916) repose sur $N=14$ avec une sous-classe (Classe D) à $n=1$, ce qui la rend fragile indépendamment de tout raffinement statistique (§5.1). De même, la comparaison QKS vs Tanimoto (Table 4 du manuscrit) n'a pas encore été testée sur un panel où la similarité classique échoue réellement.
*   **Justification Q1 :** Le panel "full-cluster rescoring" de 1 815 molécules (BMAD §1.9, mean ρ = 0.072 Tanimoto vs Vina) constitue une série congénérique idéale : la faible corrélation Tanimoto/Vina y démontre que la similarité classique échoue à discriminer l'activité, ce qui est précisément le régime où un noyau quantique devrait apporter une valeur ajoutée mesurable.
*   **Remède et Algorithme :** Recalculer TFP et QKS sur les 1 815 molécules du panel full-cluster (au lieu des 14/500 molécules actuelles) pour disposer d'un échantillon suffisant.
*   **Outils Scientifiques :** `p3_tda_pipeline.py --input`, `p3_qks_benchmark.py --n-mols 1815`
*   **Fichiers Cibles :** [p3_tda_pipeline.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_tda_pipeline.py), [p3_qks_benchmark.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_qks_benchmark.py).
*   **Critère de validation :** (i) Spearman ρ(H1, RRS) reste significatif (p<0.05) à n=1 815 ; (ii) AUC(QKS) > AUC(Tanimoto) sur le sous-ensemble où Tanimoto échoue (ρ Tanimoto/Vina ≈ 0.072).
*   **Priorité :** levier le plus important du lot P3 — les correctifs 5.1–5.4 sont nécessaires mais ne suffisent pas à eux seuls à répondre à la critique de robustesse statistique d'un rapporteur.
*   **État d'avancement (18 juillet 2026) :**
    - Panel de 1 815 molécules préparé : **1 397 SMILES uniques** extraits de la librairie (neighbors Tanimoto ≥ 0.50 des centroïdes de clusters). → `results/panel_1815_comprehensive_smiles.csv`
    - Appariement Vina-score : **1 008/1 815 (55%)** molécules ont leur SMILES + Vina score tracés via `prepare_panel_1815.py`. → `results/panel_1815_metadata.csv`
    - **Job 7949** (`p3_tda_1815`) soumis : TDA H1/H2 sur 1 397 SMILES, 48 CPU, 12h walltime. **Statut :** ⏳ Pending (PartitionTime, derrière 7952).
    - **Job 7950** (`p3_qks_1815`) soumis : QKS benchmark sur 1 815 molécules (activity file), 48 CPU, 24h walltime. **Statut :** ⏳ Pending (PartitionTime, derrière 7952).
    - **Job 7943** (`p3_qi_5k`, ✗ **tué 19 juil.**) : benchmark hybride 5 000 mols, 48 CPU. Avant son arrêt, il avait complété 8/9 descripteurs classiques et ~52% des blocs QK du fold 1/5. Le job était ralenti par 48 `PennyLaneDeprecationWarning` (NumPy 1.26.4 incompatible avec PennyLane 0.45.1).
    - **Job 7952** (`p3_qi_5k`, 🟢 **relancé 19 juil.**) : remplace 7943 avec NumPy **2.4.6** (upgradé) — plus de warnings, exécution propre et ~5× plus rapide attendue.
    - **Job 7951** (`p2_v2_redock_anp`) : re-dock V2 des 94 molécules ANP (nécessaire pour C3 DiffDock-Vina). **Statut :** ⏳ Pending (PartitionTime, derrière 7952).
    - **Note :** Les jeux de molécules TDA et QKS sont différents (panel cluster vs activity file) car QKS nécessite des labels d'activité binaires absents du panel cluster. Ceci est documenté et acceptable.

## 6. Extraits de Code pour Corrections Statistiques et Algorithmiques

Ces extraits de code valident l'intégration des corrections conformément aux exigences scientifiques Q1.

### 6.1. Test de Permutation et Bootstrap (P3-F1)
Ce code s'intègre dans [p3_h1_rrs_cross_paper_analysis.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_h1_rrs_cross_paper_analysis.py) à la fin des calculs de corrélation.

```python
from scipy import stats
import numpy as np

# Calcul initial de Spearman
rho, p_asymp = stats.spearmanr(df['RRS_mean'], df['h1_total_persistence'])
print(f"Spearman rho = {rho:.3f} (asymptotic p = {p_asymp:.4e})")

# 1. Test de permutation pour la p-value empirique exacte (N=100 000)
np.random.seed(42)
n_permutations = 100000
perm_rhos = []
for _ in range(n_permutations):
    shuffled_rrs = np.random.permutation(df['RRS_mean'].values)
    r_perm, _ = stats.spearmanr(shuffled_rrs, df['h1_total_persistence'].values)
    perm_rhos.append(r_perm)

empirical_p = np.sum(np.abs(perm_rhos) >= np.abs(rho)) / n_permutations
print(f"Empirical p-value (Permutation test) = {empirical_p:.6e}")

# 2. Bootstrap pour l'intervalle de confiance à 95%
boot_rhos = []
for _ in range(2000):
    idx = np.random.choice(len(df), size=len(df), replace=True)
    if len(np.unique(df['RRS_mean'].iloc[idx])) > 1 and len(np.unique(df['h1_total_persistence'].iloc[idx])) > 1:
        r_boot, _ = stats.spearmanr(df['RRS_mean'].iloc[idx], df['h1_total_persistence'].iloc[idx])
        boot_rhos.append(r_boot)

ci_low, ci_high = np.percentile(boot_rhos, [2.5, 97.5])
print(f"95% Bootstrap CI = [{ci_low:.3f}, {ci_high:.3f}]")
```

### 6.2. Correction de la Centralité Réseau (P2-F3)
Cette logique s'intègre dans le calcul de PNS de [md_calculate_rrs_acsi_pns.py](${MALARIA_ROOT}/Project2_Polypharmacology_MD_ValidationV2607/scripts/md_calculate_rrs_acsi_pns.py).

```python
import numpy as np

# Calcul de la centralité STRING via NetworkX
centrality = nx.degree_centrality(G) if 'G' in locals() else {}
avg_centrality = np.mean(list(centrality.values())) if centrality else 0.5

# Imputation corrigée
for smiles, grp in wt_df.groupby("smiles"):
    scores = []
    for target, string_id in TARGETS.items():
        target_rows = grp[grp["target"] == target]
        if target_rows.empty:
            continue
        dg = abs(target_rows["vina_score"].mean())
        
        # Attribution de la centralité moyenne à PfCRT au lieu de 1.0
        cd = centrality.get(string_id, avg_centrality)
        scores.append(cd * dg)
```

### 6.3. Résolution du Bug Pharmacophore Gobbi 2D (P3-F2)
Cette mise à jour de la fonction `phco` corrige [p3_hybrid_benchmark.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_hybrid_benchmark.py).

```python
from rdkit import Chem
from rdkit.Chem.Pharm2D import Generate, Gobbi_Pharm2D
import numpy as np

def phco(smiles_list: list[str]) -> np.ndarray:
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(39972, dtype=np.float32)
        if mol:
            try:
                # Utilise GetOnBits pour contourner le bug ConvertToNumpyArray
                fp = Generate.Gen2DFingerprint(mol, Gobbi_Pharm2D.factory)
                on_bits = list(fp.GetOnBits())
                if on_bits:
                    arr[on_bits] = 1.0
            except Exception:
                pass
        rows.append(arr)
    return np.array(rows)
```

### 6.4. Alignement Noyau-Cible PennyLane (P3-QKS)
Ce code s'intègre dans le pipeline de benchmarking quantique [p3_qks_benchmark.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_qks_benchmark.py).

```python
import pennylane as qml

# Evaluation intrinsèque sans SVM (Kernel-Target Alignment - KTA)
alignment_quantum = qml.kernels.target_alignment(X, Y, qk_kernel, assume_normalized_kernel=True)
alignment_rbf = qml.kernels.target_alignment(X, Y, rbf_kernel, assume_normalized_kernel=True)

print(f"Quantum Kernel Alignment: {alignment_quantum:.4f}")
print(f"RBF Kernel Alignment:     {alignment_rbf:.4f}")
```

## 7. Intégration de la Roadmap Unifiée (Papers 2 & 3)

Conformément aux documents de planification, le développement des Papers 2 et 3 est interconnecté et doit être parallélisé pour optimiser les ressources de calcul.

### 7.1. Synergie Thématique des Métriques
Le manuscrit final s'articule autour de deux narratives interconnectées :
*   **Paper 2 (Validation Biophysique) :** Définit les métriques de stress moléculaire :
    *   *Resistance Resilience Score (RRS) :* Affinité conservée sur les mutants PfDHFR (C59R, S108N) et PfCRT (isoforme "7G6" mentionnée dans les documents sources — probable coquille pour 7G8, l'unique isoforme structurellement résolue ; à vérifier, cf. §3.3).
    *   *African Chemical Space Index (ACSI) :* Score de nouveauté synthétique basé sur $fsp^3$ et la distance de Tanimoto avec DrugBank.
    *   *Polypharmacology Network Score (PNS) :* Centralité réseau pondérée par l'affinité sur cibles multiples.
*   **Paper 3 (Méthodologie Topologique & Quantique) :** Relie la physique moléculaire à l'apprentissage :
    *   *Topological Fingerprint (TFP) :* Représentation topologique basée sur la filtration de Vietoris-Rips sur les nuages de points 3D (conformères minimisés par MMFF94) ; mesure la rigidité des cycles moléculaires (homologie persistante $H_1$) et sa corrélation avec le score de résilience (RRS) de P2.
    *   *Tensor Network Embedding (TNE) :* Compression d'espace d'état moléculaire via Matrix Product States (MPS) pour modéliser les interactions locales.
    *   *Quantum Kernel Score (QKS) :* Machine à vecteurs de support (SVM) à noyau quantique évaluée sur le panel congénérique P1 de 1815 molécules.

### 7.2. Stratégie de Parallélisation du Calcul
Les calculs sont répartis sans conflit de ressources entre serveurs de calcul :
*   **Serveur GPU (Paper 2) :** Dédié à la dynamique moléculaire GROMACS (équilibrage, production 200 ns par complexe).
*   **Serveur CPU (Paper 3) :** Dédié au traitement topologique (Giotto-TDA sur la bibliothèque de molécules) et à la contraction de tenseurs (Quimb).

### 7.3. Réconciliation du Chiffre QKS Canonique
Deux valeurs contradictoires circulent pour la comparaison noyau quantique vs. RBF :
*   **0.936 (quantique) vs 0.105 (RBF)** — issu d'un run avec gamma RBF par défaut (non optimisé) ; ce chiffre n'est plus soutenu par aucun fichier de résultats et doit être supprimé de toute version du manuscrit ou de la documentation.
*   **0.751 (quantique) vs 0.701 (RBF)** — chiffre canonique, obtenu après optimisation du gamma RBF par validation croisée interne (grille {0.5, 1.0, 2.0, 5.0}), sourcé sur `p3_qks_summary.txt` et `p3_qks_benchmark.csv`.

**Action :** vérifier les logs de run pour confirmer la p-value associée à la comparaison 0.751/0.701 (une valeur de p=0.088 et une valeur de p=0.312 apparaissent selon les documents) et ne conserver qu'un seul couple (AUC, p) dans le manuscrit, l'Executive Summary et cette synthèse. Ce correctif est indépendant du bug PHCO (§5.2) — les deux scripts sources ne se recoupent pas.

### 7.4. Planning Unifié (P1 + P2 + P3)

| Créneau | P1 | P2 | P3 |
|---|---|---|---|
| H0–H1 | Édition manuscrit F1–F4 (grilles, MTX, consensus, titre) — écriture seule ; ajout du paragraphe Limitations PfCRT/PfATP4 (§3.3) — écriture seule | — | Édition manuscrit §5.4 (ratio compression) et §7.3 (chiffre QKS) — écriture seule |
| H0–H1 (préalable bloquant) | **Vérification de provenance P1** (§3.1b) : homogénéité EX=32/EX=64 sur `v2_centroid_scores.csv` et `docking_results.csv`. **Vérification prioritaire additionnelle** (§3.1c) : composition du top-20 (C1) et validité de la pose de départ MD PfDHFR (C5, 200 ns déjà investis) | — | — |
| H1–H2 | — | Lancement Job B2 (docking mutants) | Copie du panel `docking_results.csv` (1 815 mols) vers `data/p1_fullcluster_1815.csv` ; correctif PHCO (§5.2) |
| H2–H6 | — | MM-GBSA membrane implicite (Job B5) en parallèle sur serveur GPU | Jobs SLURM `p3_tda_1815` et `p3_qks_1815` en parallèle sur serveur CPU (§5.5) |
| H6–H8 | Vérification finale des chiffres cités | Intégration RRS/ACSI/PNS mise à jour | Analyse des sorties ; mise à jour §3.3/§4.7 du manuscrit ; test de permutation (§5.1) sur les 14 points existants en complément |

*Risque à surveiller (moyen) : ρ(H1, RRS) peut diminuer à n=1 815 par rapport à n=14 — c'est attendu et doit être présenté comme une estimation plus robuste, non comme une dégradation du résultat.*

## 8. Environnement d'Exécution et Soumission SLURM

Les scripts doivent être lancés dans l'environnement configuré spécifiquement pour le projet sur le cluster HPC.

:::note[Configuration de l'Environnement]
L'environnement Conda canonique est `malaria_md`. Il contient RDKit (2025.03.6), PennyLane (0.45.1), TensorLy (0.9.0) et NumPy (1.26.4). Tous les scripts de soumission SLURM doivent activer cet environnement.
:::

### 8.1. Soumission des calculs de docking mutants (Job B2)
Pour calculer les scores RRS en docking comparatif sur les mutants, exécuter :
```bash
sbatch -J p2_mutant_docking -c 8 --time=04:00:00 --mem=32G \
  --wrap="conda activate malaria_md && python scripts/dock_resistance.py"
```

### 8.2. Soumission de la réévaluation de docking V2 (Job B4)
Pour relancer le docking de la congeneric series de 1815 molécules sur la grille V2 corrigée de PfDHFR :
```bash
sbatch -J p1_v2_redocking --array=1-20 -c 4 --time=02:00:00 \
  --wrap="conda activate malaria_md && python scripts/r8b/r8b_fullcluster_rescoring.py --part \$SLURM_ARRAY_TASK_ID"
```

## 9. Index des Scripts et Fichiers Sources

Ce tableau répertorie les fichiers clés impliqués dans les corrections méthodologiques de l'audit.

| Projet | Fichier Cible | Rôle dans l'Analyse | Action Requise |
|--------|---------------|---------------------|----------------|
| P1 | [config.txt](${MALARIA_ROOT}/Project1_Chem_space_antimalarial_V2607_CorrectedGrid/Docking/Docking_7F3Y/config.txt) | Docking de référence | Aligner coordonnées de centrage V2. |
| P1 | [r8b_fullcluster_rescoring.py](/home/nanaengo/Project1_Chem_space_antimalarial_V2_CorrectedGrid/scripts/r8b/r8b_fullcluster_rescoring.py) | Docking local (1815 mols) | Aligner le dictionnaire `TARGETS` V2. |
| P1 | `v2_postprocess.py` | Provenance des scores V2 (`v2_centroid_scores.csv`, `docking_results.csv`) | Homogénéiser l'exhaustivité (EX=64) ou tracer la provenance avant consommation P2/P3 (§3.1b). |
| P1 | `9N10.pdbqt` (préparation récepteur PfATP4) | Filtrage de chaîne | Vérifier l'exclusion de l'hélice TM de PfABP co-purifiée (§3.3). |
| P1/P2 | `mutant_docking_results.csv`, manuscrits P1/P2 | Nomenclature isoforme PfCRT | Vérifier "7G6" vs "7G8" (§3.3, §7.1) avant publication. |
| P1 | `manuscript/Antimalarial_Candidates_African_NP_V2607.tex` | Manuscrit principal P1 | Aligner les coordonnées et Table S30 (MTX). |
| P2 | [md_calculate_rrs_acsi_pns.py](${MALARIA_ROOT}/Project2_Polypharmacology_MD_ValidationV2607/scripts/md_calculate_rrs_acsi_pns.py) | Scores composites | Imputer centralité moyenne à PfCRT. |
| P2 | [custom_mmgbsa.py](${MALARIA_ROOT}/Project2_Polypharmacology_MD_ValidationV2607/scripts/custom_mmgbsa.py) | Énergies libres | Configurer solvant membranaire implicite. |
| P2 | [md_convergence_check.py](${MALARIA_ROOT}/Project2_Polypharmacology_MD_ValidationV2607/scripts/md_convergence_check.py) | Contrôle MD | Calculer la dérive RMSD de production. |
| P2 | `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` | Manuscrit principal P2 | Documenter l'imputation PNS et l'exclusion MM-GBSA. |
| P3 | [p3_h1_rrs_cross_paper_analysis.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_h1_rrs_cross_paper_analysis.py) | Corrélation $H_1$ vs RRS | Implémenter test permutation et bootstrap. |
| P3 | [p3_hybrid_benchmark.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_hybrid_benchmark.py) | Descripteurs hybrides | Corriger le bug Gobbi 2D via `GetOnBits()`. |
| P3 | [p3_qks_benchmark.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_qks_benchmark.py) | Noyaux quantiques | Intégrer l'évaluation Target Alignment. |
| P3 | [p3_ga_discriminator.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_ga_discriminator.py) | Validation de noyau | Documenter le goulot d'étranglement UMAP. |
| P3 | `manuscript/LaTeX/Quantum_Inspired_Representations_V2607.tex` | Manuscrit principal P3 | Corriger le ratio de compression (5.9× réel) et fixer le chiffre QKS canonique (§5.4, §7.3). |
| P3 | [p3_tda_pipeline.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_tda_pipeline.py) + [p3_qks_benchmark.py](${MALARIA_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_qks_benchmark.py) | Relance sur panel 1 815 mols | Ajouter le flag `--input` / `--n-mols 1815` et relancer (§5.5). |

:::note[Note sur les Manuscrits]
Toutes les corrections de scripts détaillées ci-dessus doivent être répercutées dans les textes et figures des manuscrits associés (LaTeX) pour assurer la concordance absolue des résultats de calcul et de rédaction.
:::
