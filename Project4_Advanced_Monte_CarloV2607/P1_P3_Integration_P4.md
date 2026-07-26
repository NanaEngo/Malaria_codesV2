# P1-P3 Unfinished Points — Harmonic Integration into P4

## Résumé

P1 est **prêt pour soumission** (aucun point en suspens). P3 est en cours (phase2 jobs running depuis 08:53 UTC). P2 est en phase active de développement. Voici les points non réalisés qui peuvent être **harmonieusement intégrés** dans P4.

---

## 1. De P1 (Complètement terminé → Aucune intégration nécessaire)

P1 est "Ready for submission" — tous les quality gates passés. **Rien à intégrer de P1 dans P4**, car P4 utilise déjà :
- Les oracles de docking P1 (Tartarus, MPO, SYBA, SA) via `p4_mcts_oracles.py`
- Le vocabulaire de fragments (dérivé de l'analyse de fragments P1)
- Le framework ScafVAE comme politique MCTS
- Les seeds moléculaires validées (hits P1)

---

## 2. De P2 (En cours — 3 intégrations possibles)

### P2-A: RRS (Resistance Resilience Score) comme nouvel oracle

| Item | Statut P2 | Intégration P4 |
|------|-----------|----------------|
| Script RRS | ✅ `md_calculate_rrs_acsi_pns.py` prêt | Ajouter le RRS comme **5e objectif** dans le Pareto MCTS |
| Données mutant | 🚧 Mutants générés mais pas encore exécutés | P4 peut utiliser le RRS comme oracle proxy (Tanimoto aux mutants connus) |

**Implémentation:** `RRSOracle` dans `p4_mcts_oracles.py` — score basé sur la similarité Tanimoto entre la molécule générée et les hits P2 qui conservent l'affinité contre les mutants.

### P2-B: ACSI (African Chemical Space Index) comme métrique de diversité

| Item | Statut P2 | Intégration P4 |
|------|-----------|----------------|
| Script ACSI | ✅ Script prêt | Ajouter l'ACSI comme métrique de **scaffold diversity** dans le benchmark |
| Données DrugBank | 🔧 En attente | P4 peut utiliser un proxy ACSI basé sur la dissimilarité Tanimoto aux DrugBank |

**Implémentation:** `ACSIMetric` dans `p4_mcts_benchmark.py` — récompense les scaffolds éloignés de l'espace DrugBank connu.

### P2-C: PNS (Polypharmacology Network Score) comme objectif multi-cibles

| Item | Statut P2 | Intégration P4 |
|------|-----------|----------------|
| Script PNS | ✅ Script prêt | Ajouter le PNS comme objectif dans le Pareto MCTS |
| Données STRING | 🔧 En attente | P4 peut utiliser un proxy basé sur le docking multi-cibles |

**Implémentation:** `PNSOracle` — score basé sur la somme pondérée des scores de docking sur les 4 cibles (PfDHFR, PfCRT, PfATP4, PfClpP) déjà disponibles dans Tartarus.

---

## 3. De P3 (Phase 2 en cours — 4 intégrations possibles)

### P3-A: TFP (Topological Fingerprint Persistence) comme descripteur de diversité

| Item | Statut P3 | Intégration P4 |
|------|-----------|----------------|
| Pipeline TFP | ✅ Complété (12-dim persistent homology) | Ajouter le TFP comme **métrique de diversité scaffold** dans le benchmark P4 |
| Données | ✅ Sur 65,856 molécules | Utiliser la dissimilarité TFP (plutôt que Tanimoto ECFP4) pour la diversité |

**Implémentation:** `TFPDiversityMetric` — remplace/rivalise avec le Tanimoto pairwise dans l'évaluation de la diversité.

### P3-B: QKS (Quantum Kernel Score) comme oracle de similarité quantique

| Item | Statut P3 | Intégration P4 |
|------|-----------|----------------|
| QKS | 🟡 Phase 2 en cours (jobs 11861-11863) | Ajouter le QKS comme **oracle de nouveauté** dans P4 |
| Résultats | Pas encore disponibles (jobs running depuis 1h) | Attendre les résultats phase2 pour intégration |

**Implémentation:** `QKSNoveltyOracle` — pénalise les molécules trop similaires (dans l'espace du noyau quantique) à la bibliothèque P1 déjà connue.

### P3-C: TNE (Tensor Network Embedding) comme représentation compressée

| Item | Statut P3 | Intégration P4 |
|------|-----------|----------------|
| TNE | ✅ Complété (bond dimension d=8, compression 5.9×) | Utiliser le TNE comme **représentation d'état alternative** dans l'environnement MCTS |
| Descripteurs | ✅ Tucker core descriptors (192 éléments) | Le TNE peut remplacer les fingerprints ECFP4 pour l'évaluation de diversité |

**Implémentation:** `TNEStateEncoder` — encode l'état SMILES en représentation TNE compressée pour une évaluation plus riche.

### P3-D: PHCO (Pharmacophore) comme guide de construction moléculaire

| Item | Statut P3 | Intégration P4 |
|------|-----------|----------------|
| PHCO | ✅ Fixé (AUC 0.500→0.83) | Ajouter la conscience pharmacophorique dans la politique ScafVAE |
| Descripteurs | ✅ GetOnBits() | Le PHCO peut guider la sélection de fragments pour satisfaire les contraintes 3D |

**Implémentation:** `PHCOGuidance` dans `p4_mcts_policy.py` — bonus pour les fragments qui complètent un pharmacophore connu.

---

## 4. Priorité d'intégration

| Priorité | Intégration | Effort | Impact Q1 | Dépendances |
|----------|-------------|--------|-----------|-------------|
| 🔴 **P2-A** | RRS comme oracle multi-objectif | 2 jours | **Très élevé** — ajoute la conscience de la résistance | Données mutants P2 |
| 🔴 **P2-C** | PNS comme objectif Pareto | 2 jours | **Très élevé** — polypharmacologie quantifiée | Scores Tartarus (déjà dispo) |
| 🟡 **P3-A** | TFP diversité metric | 1 jour | Élevé — remplace Tanimoto standard | Matrices TFP P3 |
| 🟡 **P3-C** | TNE state encoding | 3 jours | Élevé — représentation plus riche | Embeddings TNE P3 |
| 🟢 **P3-B** | QKS novelty oracle | 2 jours | Moyen — dépend des résultats phase2 | Résultats phase2 P3 |
| 🟢 **P3-D** | PHCO fragment guidance | 1 jour | Moyen — amélioration incrémentale | Descripteurs PHCO P3 |
| 🟢 **P2-B** | ACSI diversity metric | 1 jour | Moyen — niche africaine | Données DrugBank |

---

## 5. Plan de soumission P4

**Scénario A (soumission sans dépendances P3)**: Intégrer seulement P2-A (RRS) + P2-C (PNS) comme oracles supplémentaires. P4 reste un papier solide avec 6 objectifs Pareto et benchmark 4 méthodes.

**Scénario B (soumission post-P3)**: Intégrer P3-A (TFP) + P3-C (TNE) + P3-B (QKS). P4 devient un papier multi-résolution combinant MCTS moléculaire + descripteurs quantiques.

**Recommandation**: Scénario A d'abord (soumission plus rapide), avec P3 comme extension présentée dans la section Future Work.
