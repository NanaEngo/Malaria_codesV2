# P6 — Revue finale auteur, reviewer et éditeur associé

**Date :** 31 août 2026  
**Projet canonique :** `Project6_LISH_MoA_Structure_Phenotype`  
**Cible :** *Journal of Computer-Aided Molecular Design*

## Question centrale

Sous une évaluation contrôlée des fuites sur une cohorte LISH-MoA mappée, la structure moléculaire fournit-elle une information prédictive transférable au-delà d’une référence fondée sur le phénotype, et la combinaison des deux sources améliore-t-elle la prédiction hors échantillon ?

Cette question est falsifiable, agnostique quant à une amélioration et ne confond pas prédiction de labels observés avec inférence d’un mécanisme causal.

## Résultats canoniques vérifiés

- 3 289 lignes au niveau médicament et 206 labels.
- 1 722 structures uniques et 794 groupes de collision.
- 25 répétitions seed–fold.
- Référence phénotype : AUROC collision-group 0,63619 ; scaffold 0,64023.
- ECFP4-RF : AUROC collision-group 0,53562 ; scaffold 0,53817.
- Fusion phénotype–ECFP4-RF : AUROC collision-group 0,58323 ; scaffold 0,58774.
- GIN-TFP : meilleure log loss parmi les bras moléculaires, 0,02334 en collision-group et 0,02373 en scaffold, avec AUROC proche du hasard.
- Calibration RF scaffold : structure ECE 0,0012, MCE 0,3893, Brier 0,0034 ; fusion ECE 0,0017, MCE 0,2590, Brier 0,0034.
- QKS borné : structure, ΔF(0,5)=0,0229 et Spearman 0,0361 ; fusion, ΔF(0,5)=0,0329 et Spearman 0,4272.

## Lecture auteur

La prose du manuscrit est scientifique et ne contient pas de journal d’exécution ni de jargon promotionnel notable. Le manuscrit distingue correctement labels MoA observés, prédiction et causalité. Les valeurs RF du scaffold et de la fusion sont alignées avec les sorties canoniques. La cover letter et le manifest ont été harmonisés avec la question centrale et l’état final des calculs.

Point restant : confirmer personnellement auteurs, affiliations, ORCID, financement et conflits d’intérêts avant dépôt.

## Lecture reviewer adversariale

Les risques majeurs examinés étaient la fuite de structures identiques, le mélange RF/logistique, la confusion entre log loss et discrimination, l’interprétation de la fusion, le déséquilibre des labels, l’absence de validation externe et la surinterprétation biologique. Le protocole de collision-group, la sensibilité scaffold, l’unification RF et les limites explicites réduisent ces risques.

La fusion ne doit pas être décrite comme une amélioration confirmée : son accord avec la référence phénotype est descriptif et son AUROC reste inférieur à celui de la référence phénotype.

Les diagnostics de calibration et QKS sont bornés à la cohorte étudiée et ne constituent ni validation biologique ni preuve de causalité.

## Lecture éditeur associé

L’adéquation à JCAMD est bonne : le travail porte sur la modélisation moléculaire, les biais d’évaluation, la généralisation structurale et la reproductibilité. La contribution est méthodologique et négative, mais défendable si elle reste limitée à la cohorte, aux labels et aux modèles évalués.

## Figures et tableaux

Les tableaux principaux portent les résultats quantitatifs essentiels. Aucune figure n’est actuellement incluse dans le manuscrit principal ; cette absence n’est pas bloquante pour un benchmark compact, mais une figure synthétique de performance par split pourrait améliorer la lisibilité si elle est générée depuis les fichiers canoniques.

## Limites

Le travail ne démontre ni mécanisme causal, ni engagement de cible, ni activité biologique, ni supériorité universelle d’une représentation moléculaire. Le split scaffold reste une analyse de sensibilité sur la même cohorte. Les intervalles seed–fold ne sont pas des intervalles populationnels. L’évaluation externe et la validation expérimentale restent hors périmètre.

## État technique

- Prompt d’audit enregistré dans `P6_AUDIT_PROMPT_JCAMD.md`.
- DAR mis à jour avant les documents de soumission.
- Manifest et cover letter alignés.
- Compilation précédemment vérifiée : main 10 pages, cover 1 page, sans erreur ni référence indéfinie.
- Les sorties `NOT_COMPUTED` restent explicitement hors des claims.

## Actions avant dépôt

1. Vérification finale par les auteurs des métadonnées, ORCID, financement et conflits.
2. Vérification visuelle du PDF final et des légendes/tableaux.
3. Vérification des directives JCAMD à la date du dépôt.
4. Création de l’archive de données et vérification de sa complétude.
5. Gel du manifest et du commit de soumission.

## Verdict

**READY AFTER MINOR AUTHOR CHECKS**
