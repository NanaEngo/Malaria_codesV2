# PASS1 — Audit adversarial P5-V2 (25 août 2026)
Cible : Project5_GNN_Transformer_DrugDiscovery_V2609/manuscript/P5_manuscript_V2608.tex (ligne avancée, couche de traçabilité LED-001-R1…LED-014). Prompt : docs/PROMPT_AUDIT_ADVERSARIAL_P5_20260825.md (JCAMD).

## Verdict : MINOR REVISION → GO après corrections appliquées

## Positifs vérifiés sur pièces
- **F1 Intégrité benchmark** : numériques re-vérifiés contre les JSON bruts — ECFP4-RF random mean 0.9433 ✓ ; scaffold 0.83 ✓ ; ChemBERTa scaffold AUCs 0.74–0.85, mean ≈0.787 ✓ (manuscrit 0.7867).
- **F2 Parité de tuning** : honnêteté exemplaire (L179) — hyperparamètres fixes (hidden=128, 50 epochs, patience=10), pas d'optimisation par tâche, caveat 3D-equivariant (rollins2024molprop), salience = corrélation ≠ causalité (L146).
- **F3 Hygiène de fuite** : reset indépendant des poids pré-entraînés par fold documenté ×2 (L161/L209) ; split scaffold comme proxy de nouveauté cité ; LISH-MoA cadré référence orthogonale phénotypique uniquement (L85/L157/L169) — jamais présenté comme validation des représentations.
- **F4 Validation externe** : ChEMBL CHEMBL364 réelle (manifeste L5/L31 + artefacts results/public_chembl). NB : la mention « external MoleculeNet validation » relevée sur l'ancien manifeste canonical n'existe PAS dans le manifeste V2 — C-P5-01 classée non-applicable à cette ligne.

## Critiques et mitigations (appliquées ce jour)
- **C-P5-02 (MINOR)** ambiguïté du ± : ± affichés = SD de population des moyennes par graine ; dispersions par fold plus larges (jusqu'à 0.0458) archivées dans p5_replication_stats.csv. → phrase clarificatrice ajoutée après eq:hierarchy.
- **C-P5-03 (MINOR)** Overfull 29.59 pt sur l'équation hiérarchique (~L124) → bloc passé en \small ; recompile err=0 / overfull=0 / undef=0.

## Sortie finale
Claims↔evidence : tous les chiffres LED-traçés retrouvés dans les artefacts ; top-blockers : aucun bloquant restant ; phrases interdites absentes (pas de « proves/validates ») ; décision par flux F1–F4 = PASS ; garde anti-hallucination UNVERIFIED : rien d'inventé.
