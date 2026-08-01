# Project 5 — GNN/Transformer-based Drug Discovery

**Objectif :** Implémenter des représentations basées sur les graphes (GNN) et les architectures Transformers (ex: ChemBERTa, Graphormer) pour la prédiction d'activité et la génération de molécules, en tirant parti des résultats topologiques (P3) et MD (P2).

**Piliers :**
1. **Graph Representation Learning** : GNNs (GCN, GAT, GIN) pour encoder la connectivité moléculaire.
2. **Transformers** : Modèles basés sur l'attention (ex: conformer) pour capturer les dépendances à longue distance.
3. **Multi-modalité** : Intégration des features TDA/TNE (P3) avec les embeddings GNN.
4. **Validation** : Benchmark sur le dataset n=19,849 (établi en P3) vs ECFP4/TFP.

**Structure :**
- `scripts/` : Pipeline d'entraînement, modèles, dataloaders.
- `manuscript/` : Rédaction théorique et résultats.
- `results/` : Checkpoints, logs d'entraînement, métriques.
- `docs/` : Roadmap et spécifications des modèles.

*Note : Toute action doit être documentée dans `BMAD_Q1_DATA_ANALYSIS_REPORT.md` avant exécution.*
