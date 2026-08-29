# Audit détaillé — Project2_Polypharmacology_MD_ValidationV2607

**Date** : 29 août 2026
**Cible** : JCIM — `Polypharmacology_MD_Validation_V2607.tex` et Supporting Information
**Statut après réconciliation DAR** : **HOLD avant édition du manuscrit**

> **Légende** : 🔴 bloquant · 🟠 majeur · 🟡 mineur · 🟢 conforme

## Addendum de gouvernance — 29 août 2026

Le DAR P2 a été mis à jour avant toute nouvelle modification du manuscrit. Cette mise à jour ne change aucun résultat numérique : elle clarifie la provenance et les limites d'interprétation.

- Le niveau de preuve primaire est le classement docking-derived RRS/PNS/ACSI sur la cohorte Set-C.
- MD géométrique, MM-GBSA mono-réplicat, GNINA, P2Rank, ProLIF et les réplications docking sont des diagnostics secondaires ou techniques.
- Aucun de ces diagnostics ne constitue une mesure d'affinité, d'engagement de cible ou de résistance.
- Le multi-seed PP-01 est recevable uniquement comme contrôle borné de sensibilité à la seed. PfDHFR reproduit le score historique ; PfCRT reste affecté par l'absence de la préparation récepteur historique archivée. Les essais utilisant la grille PP-15 ou une préparation Meeko sont exclus de l'inférence.

## 1. Synthèse exécutive corrigée

| Dimension | Verdict | Interprétation éditoriale |
|---|---:|---|
| Traçabilité computationnelle | 🟢 | Manifests, seeds, hashes et tests sont utiles et bien documentés. |
| Reproductibilité environnementale | 🟠 | L'environnement doit avoir un chemin canonique unique et idéalement un conteneur épinglé. |
| Cohorte et puissance | 🔴 | `n=12` pour l'estimand primary ; les tests non significatifs ne démontrent pas l'absence d'association. |
| Calibration docking | 🔴 | DEKOIS PfDHFR AUC `0.45` est compatible avec le hasard ; aucune affirmation de pouvoir prédictif ne doit subsister. |
| MD/MM-GBSA | 🟠 | 10 ns et un réplicat par système permettent un diagnostic local, pas une estimation thermodynamique robuste. |
| Validation indépendante | 🟠 | GNINA, P2Rank et réplication externe restent des validations computationnelles partageant des hypothèses ou des données. |
| Validation biologique | 🔴 | Aucun assay PfDHFR/PfCRT : target engagement et résistance restent non observés. |
| Prose et portée | 🟠 | Le papier doit être recadré explicitement comme workflow de priorisation bornée. |

**Verdict** : **révision majeure avant dépôt**. Le travail peut être défendable dans JCIM comme étude méthodologique de priorisation et de calibration négative ; il n'est pas défendable comme démonstration de puissance, d'affinité ou de résilience biologique.

## 2. Contradictions ou risques à fermer avant soumission

### R1 — Surinterprétation de la reproductibilité
Une faible dispersion entre seeds ne valide ni la grille, ni la préparation du ligand, ni la physique du score. La formulation admissible est : *the mode-1 docking score was stable under the tested seeds for the reproduced protocol*. Éviter *validated*, *accurate* ou *resistance-resilient*.

### R2 — PfCRT PP-01 : provenance incomplète
Le résultat `−9.250` (range `−9.262` à `−9.225`) est proche mais ne contient pas l'historique `−9.300`. L'absence de la préparation récepteur originale interdit de conclure à une reproduction exacte. Cette réserve doit apparaître dans le SM et le DAR, pas seulement dans un log.

### R3 — MD-RRS et MM-GBSA ne sont pas des mesures de résistance
Les ratios >100 ou <100 sur un réplicat de 10 ns ne doivent pas être transformés en effet de mutation. Présenter les résultats comme diagnostics dépendants du protocole, avec incertitude et absence de validation expérimentale.

### R4 — DEKOIS 0.45 invalide toute rhétorique de prédiction
Le manuscrit doit employer *prioritisation*, *ranking hypothesis* ou *computational triage*. Il doit éviter *predicts potency*, *demonstrates binding* et *identifies resistance-proof compounds*.

### R5 — Corrélations post-sélectionnées
Les p-values et bootstrap sont des analyses descriptives sur une cohorte sélectionnée. Elles ne doivent pas être présentées comme confirmation indépendante des hypothèses H1–H3.

### R6 — Réplication externe non indépendante au sens biologique
Les 39 ligands et le pipeline de scoring ne constituent pas une validation expérimentale indépendante. La formulation correcte est *cross-cohort computational transfer/replication*.

## 3. Actions recommandées, par priorité

### Bloquants avant soumission

1. **Rechercher et supprimer toute affirmation d'affinité, d'engagement, de résistance ou de mécanisme biologique** non directement mesurée.
2. **Ajouter une section Methods “Estimands and evidence boundaries”** distinguant primary, secondary, technical et unobserved quantities.
3. **Aligner abstract, title, Results et Conclusion** sur le message : triage computationnel, non validation biologique.
4. **Insérer DEKOIS AUC `0.45 [0.37, 0.53]` dans Results et Discussion**, avec son implication pour la calibration.
5. **Corriger toutes les références au multi-seed PP-01** pour conserver le caveat PfCRT et exclure les runs non canoniques.
6. **Auditer automatiquement claims ↔ fichiers** : chaque valeur publiée doit avoir un fichier, un protocole, un hash et un statut dans le DAR.

### Majeurs, fortement recommandés

7. Ajouter AUPRC, calibration curve/Brier uniquement si les scores probabilistes et les labels sont disponibles ; sinon documenter explicitement pourquoi ils ne sont pas calculables.
8. Présenter les résultats MD avec intervalles inter-réplicats uniquement si de vrais réplicats existent ; ne pas appeler l'écart-type intra-trajectory une incertitude de réplication.
9. Déplacer les détails d'ingénierie, les IDs de jobs et les chemins de fichiers dans le Data Availability/SM ; conserver dans le main les méthodes, estimands et résultats scientifiques.
10. Ajouter un tableau SM “claim–evidence–boundary” et un schéma du DAG docking → filtering → MD diagnostic → prioritisation.
11. Ne pas promettre un gain de puissance statistique par une extension non réalisée ; marquer la cohorte `n=12` comme exploratoire pour les corrélations.

### Après soumission / version ultérieure

12. Cross-force-field sur un panel pilote avec protocole gelé.
13. Réplicats MD d'au moins 100 ns pour les systèmes destinés à une interprétation énergétique.
14. Calibration MM-GBSA sur ligands de référence avec mesures expérimentales.
15. Assays PfDHFR/PfCRT et recalibration prospective du workflow.

## 4. Décision de soumission

- **Soumission immédiate sans correction** : déconseillée.
- **Soumission après recadrage de portée et audit claims↔data** : défendable comme article de méthode/triage.
- **Soumission comme preuve de polypharmacologie ou de résistance** : non recommandée en l'absence d'assays.

## 5. Références canoniques

- DAR : `P2_DATA_ANALYSIS_REPORT.md` — source de vérité et règle DAR-before-manuscript.
- Main : `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex`.
- SM : `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex`.
- Données PP-01 : `results/pp01_docking_20260829/`.
- Données PP-15 : `results/pp15_docking_20260828/`.

*Ce document remplace l'ancienne synthèse uniquement pour le statut de décision ; les résultats primaires restent ceux du DAR.*
