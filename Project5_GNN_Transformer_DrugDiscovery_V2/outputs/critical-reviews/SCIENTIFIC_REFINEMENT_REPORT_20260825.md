# P5 V2 — Rapport de raffinement scientifique avant soumission

**Date :** 25 août 2026  
**Objet :** renforcer la résistance scientifique du manuscrit face à un reviewer statistique/ML sévère et à un editorial board rigoureux.  
**Statut initial :** manuscrit scientifiquement défendable ; raffinements recommandés avant soumission.

## Verdict scientifique

Le résultat principal est défendable si sa portée reste limitée :

> Dans le panel antipaludique étudié et avec les configurations évaluées, ECFP4-RF conserve la meilleure performance sous séparation par scaffold.

Le résultat ne doit pas être formulé comme une infériorité universelle des GNN ou transformers.

## Priorité 1 — clôture avant soumission

### 1. Unité statistique et pseudoréplication

- Présenter les cinq moyennes par seed comme unité de comparaison computationnelle, et non comme échantillon aléatoire de molécules futures.
- Conserver les 25 résultats fold–seed pour la transparence.
- Rapporter différence moyenne, dispersion entre seeds, intervalles de confiance et distribution fold-level.
- Déclarer explicitement que les incertitudes sont des incertitudes de réplication computationnelle.

### 2. Cohérence code–manuscrit–artefacts

Vérifier et aligner :

- nombre de couches ;
- fonctions d’activation ;
- dropout ;
- learning rate et weight decay ;
- batch size ;
- nombre d’époques et patience ;
- seeds NumPy/Python/PyTorch/CUDA ;
- configuration RF ;
- traitement des molécules invalides dans l’analyse externe.

### 3. Sensibilité au choix de la partition scaffold

La partition scaffold principale est une réalisation unique. Il faut idéalement :

- plusieurs partitions scaffold indépendantes ; ou
- une analyse secondaire sur plusieurs ordres d’assignation ; ou
- au minimum une mesure de sensibilité documentée sur les partitions déjà disponibles.

La question à traiter est : le résultat négatif est-il robuste au choix de la partition ?

### 4. Comparaisons statistiques

La hiérarchie complète des modèles appris est descriptive. Les tests principaux portent sur chaque modèle contre ECFP4-RF. Le manuscrit doit préciser que les différences GIN–TFP, GIN–TNE et GIN ne constituent pas toutes des contrastes inférentiels préspécifiés.

### 5. Formulation de l’effet topologique

Remplacer toute formulation pouvant impliquer un gain confirmé par une formulation indiquant que GIN-TFP présente un déficit numériquement plus faible, sans test inférentiel préspécifié contre GIN.

## Priorité 2 — validité ML

### 6. Budget de capacité et d’optimisation

Documenter séparément les hyperparamètres fixés a priori et ceux optimisés. Le résultat doit être limité aux configurations évaluées si aucun tuning équivalent n’a été réalisé.

### 7. Baseline supplémentaire — COMPUTED

Deux contrôles ECFP4 ont été exécutés sur les splits officiels, sans entraînement profond :

- kNN ECFP4 distance-weighted, k=5 : AUC 0.9166 random ; 0.7110 scaffold ; AUPRC 0.9562 et 0.8467 ;
- régression logistique ECFP4, C=1 : AUC 0.8790 random ; 0.7063 scaffold ; AUPRC 0.9456 et 0.8542.

Ces résultats sont secondaires et versionnés dans `results/lightweight_robustness/`. Ils montrent que le résultat RF ne doit pas être généralisé à tout apprenant ECFP4.

### 8. Déséquilibre de classes

Compléter l’AUC par AUPRC et indiquer la prévalence par fold, surtout pour ChEMBL où la prévalence positive est élevée.

### 9. Déterminisme GPU

Documenter versions CUDA/PyTorch/PyG, GPU, seeds et éventuelles opérations non déterministes. Ne pas prétendre à un déterminisme parfait sans preuve.

## Priorité 3 — difficulté chimique

### 10. Caractérisation des splits — COMPUTED

L’audit des splits officiels a confirmé zéro overlap train--test de scaffold sous le protocole scaffold. La prévalence active des folds test scaffold varie de 0.586 à 0.862. Dans un audit borné (500 molécules train, 100 test par fold), la similarité Tanimoto maximale moyenne varie de 0.292 à 0.388 sous scaffold contre 0.477 à 0.568 sous random. Ces résultats sont descriptifs et versionnés dans `scientific_audit_20260825.json`.

Rapporter, idéalement dans un tableau :

- nombre de scaffolds uniques ;
- tailles des folds ;
- prévalence active/inactive ;
- similarité Tanimoto train–test ;
- distributions MW/LogP/TPSA/cycles ;
- proportion de scaffolds rares et singletons.

### 11. Analyse par scaffold

Décrire si l’échec des modèles appris est global ou concentré sur quelques familles chimiques.

### 12. Similarité au-delà du SMILES exact

Vérifier les doublons après standardisation, tautomères, sels, stéréoisomères et analogues très proches entre train et test.

## Priorité 4 — topologie et interprétabilité

### 13. Ablation TFP/TNE

Comparer GIN, GIN+TFP/TNE, suppression de blocs et permutation des colonnes. L’objectif est de séparer utilisation du bloc, information utile et bruit.

### 14. Stabilité de la salience — PARTIELLEMENT COMPUTED

Les vecteurs agrégés sur 25 runs donnent une part de salience top-10% de 17.7% pour TFP et 18.0% pour TNE. La fréquence top-k par run n’est pas calculable car les vecteurs individuels ne sont pas archivés séparément ; elle reste `NOT_COMPUTED_INPUTS_NOT_ARCHIVED`.

### 15. Limites d’interprétation chimique

Les coordonnées persistent-image sont des variables de représentation, non des motifs pharmacophores ou mécanistiques sans analyse inverse dédiée.

## Priorité 5 — validation externe

### 16. Portée de ChEMBL

Utiliser la formulation « molecule-disjoint external transfer panel within the same broad antimalarial domain ».

### 17. Sensibilité aux seuils ChEMBL

Si calculable, tester les seuils pChEMBL et le traitement de la zone 5–6, en évitant toute sélection opportuniste.

## Priorité 6 — LISH-MoA

Le LISH-MoA est une référence phénotypique orthogonale, non une validation structure–MoA. Sa place doit rester secondaire et clairement séparée ; un déplacement vers le Supporting Information est scientifiquement défendable.

## Trois raffinements à rendement élevé

1. alignement strict code–manuscrit–artefacts ;
2. sensibilité au partitionnement scaffold ;
3. ablation/permutation TFP-TNE avec stabilité de salience.

## Mise à jour de clôture — analyses légères exécutées

Après autorisation de l'auteur, les analyses ne nécessitant pas de nouvel entraînement profond ont été exécutées à partir des artefacts gelés officiels : audit des 50 réalisations random/scaffold, contrôle de disjonction des Bemis--Murcko scaffolds, audit Tanimoto borné, kNN ECFP4 et régression logistique ECFP4. Les sorties sont versionnées dans `results/scientific_audit_20260825.json` et `results/lightweight_robustness/`, avec les scripts producteurs et les paramètres consignés.

Les AUPRC sont maintenant disponibles pour ces deux contrôles ECFP4. Elles ne sont pas extrapolées aux modèles neuronaux canoniques, car leurs probabilités de prédiction ne sont pas archivées. Les partitions scaffold supplémentaires avec réentraînement, les ablations/permutations TFP/TNE, la sensibilité des seuils ChEMBL, la standardisation chimique approfondie et la stabilité top-k par run restent explicitement `NOT_COMPUTED`.

## Campagne étendue — clôture du 25 août 2026

La campagne `results/extended_campaign_20260825/` est complète et vérifiée : 25/25 configurations portent le statut `COMPUTED`, chacune avec 25 records, prédictions fold-level et métriques AUC/AUPRC. Les contrastes natif--permuté sont appariés sur cinq moyennes par seed ; les tests exacts de sign-flip ne sont pas significatifs compte tenu de cette petite unité computationnelle. La salience individuelle présente une corrélation de rang modérée à élevée mais un recouvrement top-10% limité, ce qui justifie une interprétation descriptive et non causale. ChemBERTa n’a pas été rerun faute de poids locaux disponibles.

## Limite opérationnelle

Toute analyse future nécessitant de nouveaux calculs doit conserver des sorties versionnées, seeds, hashes, environnement et statut `COMPUTED`/`NOT_COMPUTED` explicites, sans modifier les résultats canoniques.
