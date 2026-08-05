# P5 — Plan Stratégique d'Implémentation (PA ≥ 90 %)

**Version:** v1 (01/08/2026)
**Statut:** 🔄 Document vivant — **à améliorer régulièrement** à chaque milestone
**Boussole liée:** `P5_DATA_ANALYSIS_REPORT.md` (données), `AGENTS.md` (workflow)

> Objectif : produire un manuscrit P5 **Q1 avec probabilité d'acceptation (PA) ≥ 90 %**.
> Ce plan stratégique traduit la boussole de données en un **chemin d'exécution chiffré** :
> quelles expériences, dans quel ordre, quelles ressources, quels gates de décision.

---

## 1. Thèse & Déclaration de Nouveauté (le « pourquoi » de la soumission)

> *« Sur un panel de produits naturels antimalariens curé (n = 19,836), les GNN compacts avec
> fusion de descripteurs topologiques (TDA/TFP, TNE) réduisent l'écart — et sous scaffold split
> dépassent — les fingerprints classiques, tandis que les transformers n'offrent aucun "free lunch"
> à cette échelle. »*

**3 piliers défendables (Q1):**
1. **Référence inter-projet unique** : mêmes panel, splits, protocole que P3 → comparaison directe
   avec ECFP4 (0.9475), Hybrid (0.8876), QKS. Aucun nouveau confondant de dataset.
2. **Fusion topologique multi-modale** (GIN + TFP + TNE) : la contribution scientifique centrale,
   ancrée dans P3, absente de la littérature GNN 2025-2026.
3. **Benchmark honnête à grande échelle** : 5 folds × ≥5 seeds, DeLong + BH FDR, split random
   ET scaffold — aligné sur la leçon « Do Larger Models Really Win? » (2026).

---

## 2. Matrice d'Acceptation PA ≥ 90 %

La PA se construit par **leviers indépendants**. Chaque levier rempli → point sur la PA.

| # | Levier | Poids estimé | Critère de remplissage | Statut |
|:-:|:-------|:------------:|:-----------------------|:------:|
| L1 | Panel/protocole reproductible & figé | +20 pts | Panel 19,836 ✓, splits figés ✓, sanity 0.9428 ✓ | ✅ **Fait (v1-prep)** |
| L2 | Résultat positif significatif | +25 pts | ~~≥1 fusion topologique > ECFP4 sous scaffold (DeLong p<0.05)~~ **`H1 FAIL (04/08)`** | ❌ **Échoué (remplacé)** |
| L3 | Honest negative / null | +30 pts | **H1 nul**: aucune GNN/fusion > ECFP4-RF scaffold (0.8300) ; GIN −0.025 (p=0.051), GIN-TFP −0.016 (p=0.081), GIN-TNE −0.023 (p=0.015). **H2 nul**: ChemBERTa scaffold 0.7867 vs 0.8300 (Δ −0.043, p<0.0001) → transformer ≤ GNN ≤ fingerprints | ✅ **Fait (04/08)** |
| L4 | Contribution méthodologique/interprétabilité | +20 pts | Attribution/salience des dims TFP/TNE (H3, bridge P3 H1-RRS) — **DONNÉES ACQUISES (04/08)** : TFP pers_img dominant (sal 0.079), TNE top dims 68/43/92/66/165 | ✅ **Données faites (04/08)** — écriture L4 en cours |
| L5 | Benchmark/dataset libéré (Zenodo) | +10 pts | Zenodo deposit (DOI) aligné P1/P3 | ⏳ Phase 3 |
| L6 | Narration/figures publication-grade | +15 pts | Figures bar + courbes d'apprentissage, manuscrit LaTeX complet | ⏳ Phase 2-3 |
| | **Total** | **95 pts** | | ~70/95 |

**Gate de décision — EXÉCUTÉ (04/08) :** L2 a échoué (aucune fusion > ECFP4 sous scaffold, voir
résultats v3 §10). **Thèse basculée sur L3+L4+L5** (honest negative + topologie) — aligné sur le
précédent accepté « Do Larger Models Really Win? » (Deng et al.). Le levier L3 est désormais le
**headline** (résultat négatif rigoureux, pas seulement « transformer ≤ GNN » mais « toute la
famille GNN/fusion ≤ fingerprints sous OOD scaffold »), documenté avec p-values paired.

---

## 3. Plan d'Exécution (phases → milestones)

### Phase 0 — Infrastructure ✅ (terminée 01/08)
- [x] Dépendances verrouillées (PyG 2.8.0, torch 2.13.0+cu130, transformers 5.14.1) — §7 du rapport
- [x] Panel canonique `p5_canonical_panel.csv` (19,836 × 272) réutilisant la logique P3
- [x] Splits figés (random + scaffold, 5 folds × 5 seeds) + info JSON
- [x] Sanity gate ECFP4-RF = 0.9428 ± 0.0031 (réf P3 0.9475) ✓

### Phase 1 — MVP Benchmark v1 (en cours)
| Milestone | Livrable | Ressource | Gate |
|:----------|:---------|:----------|:-----|
| M1.1 | `p5_data.py` — featurization PyG + cache .pt | CPU | GIN forward OK |
| M1.2 | `p5_models.py` — GCN/GIN/GAT/GIN-FP/GIN-TFP/GIN-TNE/Hybrid-All | — | forward/backward OK |
| M1.3 | `p5_benchmark.py` — train/eval, 5-fold×seeds, DeLong+BH | GPU A4000 (batch) | convergence |
| M1.4 | `p5_chemberta.py` — ChemBERTa fine-tune | GPU | — |
| M1.5 | `p5_figure.py` — figure benchmark bar | CPU | — |
| M1.6 | **Résultats v1 + analyse statistique** | — | L2/L3 évalués |

**Configuration v1 (Phase 1) :** deployé 04/08 — **`H1 FAIL`** : GIN random 0.9098±0.0067,
GIN scaffold 0.8047±0.0395, GIN-TFP 0.8137±0.0300, GIN-TNE 0.8068±0.0366 vs ECFP4-RF scaffold
**0.8300** (random 0.9433). Aucune GNN/fusion ne bat ECFP4-RF sous scaffold (paired t : TNE p=0.015
significativement pire, GIN p=0.051 ns, TFP p=0.081 ns). → **Pivot L3+L4 actif.**

### Phase 2 — Scaffold + Interprétabilité (v2)
- [x] Ré-exécuter les modèles sous scaffold split (5 folds × 5 seeds) — **fait (04/08)** : GIN,
  GIN-TFP, GIN-TNE, ECFP4-RF.
- ✅ **H3 salience — données ACQUISES (04/08)** : capture salience (mean \|W\| sur colonnes desc de
  `head.0.weight`) + re-runs fusion jobs 12811/12812 → **TFP : pers_img (33:58) dominant (0.079)**,
  **TNE : top dims 68/43/92/66/165**, top-10% = 17.3% salience. Écriture contribution L4 en cours.
- ✅ **ChemBERTa scaffold (H2) COMPLET (04/08, job 12813, leak-fixed)** : **0.7867 ± 0.0338** vs ECFP4-RF
  0.8300 → **Δ −0.043, p<0.0001** (paired t, 5 seeds). Hiérarchie scaffold : ECFP4-RF > GIN-TFP > GIN-TNE > GIN > ChemBERTa. Transformer ≤ GNN ≤ fingerprints CONFIRMÉ → L3 doublé.
- 🔄 **ChemBERTa random (H2)** — job 12814 en cours (premier run avec capture `curve` par époch).
- ⏳ Courbes d'apprentissage (N = 500 → 19,836) — capture par époch prête (`curve` key), à produire après 12814.

### Phase 3 — Génération (stretch, seulement si Phase 1–2 montrent un gain net)
- Génération GNN/Transformer validée sur les top-candidats P3, ou réutilisation P4 MCTS.

---

## 4. Ressources & Contraintes HPC

| Ressource | Valeur | Usage P5 |
|:----------|:-------|:---------|
| Node | `penavoraserver` (unique) | Séquentiel |
| CPU | 32 cœurs | Featurization, RF, fingerprint, cache |
| GPU | NVIDIA RTX A4000 (16 GB, CC 8.6) | **Entraînement batch dense** (GNN/transformer) |
| Jobs | SLURM partition `production` | Séquentiel avec P3 (12699/12700/12702 en cours) |

**Leçon P3 (critique) :** le GPU A4000 peut être **plus lent que le CPU** pour les opérations
paire-à-paire (QK). **Règle P5 : GPU réservé aux forward/backward par batch dense ; CPU pour
featurization/cache.** Un smoke test GPU vs CPU doit être enregistré (rapport §9).

**Estimé Phase 1** (à affiner au M1.3) :
- GIN/GCN/GAT (petits, 2-3 couches, hidden 128) : ~5-15 min/fold/seed GPU → 9 modèles × 5 folds × 5 seeds ≈ quelques heures.
- ChemBERTa-base fine-tune : le plus cher — GPU requis, n=19,836 gérable (~30-60 min/epoch).

---

## 5. Protocole Statistique (verrouillé)

- Métriques : ROC-AUC (primaire), AP, F1, balanced accuracy.
- Répétition : 5 folds × ≥5 seeds → mean ± std.
- Tests : **DeLong paired** (ou bootstrap) vs ECFP4-RF et vs chaque modalité ; **BH FDR** sur les comparaisons.
- Sanity : ECFP4-RF sur les splits figés doit reproduire 0.9475 ± 0.01 (✓ fait en v1-prep).
- Interdiction : régénérer les splits par run (figés), imputer silencieusement (refus si manquant).

---

## 6. Registre de Risques (acceptation → mitigation)

| Risque | Prob. | Impact | Mitigation |
|:-------|:-----:|:------:|:-----------|
| GNN ne bat pas ECFP4 (probable, cf. SOTA) | Haute | Haute | Levier L3 (honest negative) + fusion/complémentarité ; thèse pivot |
| Transformer ≤ GNN compact | Haute | Moyenne | Levier L3 ; pas le headline |
| Compute limité (1 node, GPU lent) | Moyenne | Moyenne | Modèles petits ; cache une fois ; ChemBERTa seul gros |
| Variance n≈2×10⁴ | Moyenne | Moyenne | Seeds répétés, scaffold split, weight-decay sweep |
| « Yet another benchmark » | Haute | Haute | Comparabilité P3 + fusion topologique + honnêteté |

---

## 7. Convention de Suivi

- Chaque script/param/protocole documenté dans `P5_DATA_ANALYSIS_REPORT.md` **avant** exécution.
- Résultats : `Project5_GNN_Transformer_DrugDiscovery/results/` ; scripts `.../scripts/` ; logs `.../logs/slurm/`.
- Chaque version (v1, v2, …) journalisée dans le rapport §10 (CSV paths, seeds, commande, wall-time, machine).
- **Git push après chaque milestone validé.**

---

## 8. Prochaines Actions immédiates

1. [x] Instrument de mesure fiabilisé (self.folds, dry-run sans pollution, sbatch corrigé) — **04/08**
2. [x] Benchmark scaffold M1.3 : GIN, GIN-TFP, GIN-TNE, ECFP4-RF — **04/08** (`H1 FAIL` → pivot L3)
3. [x] Salience H3 implémentée (mean |W| desc-projection, pas de gradients) — **04/08**
4. [x] ChemBERTa : `--split` + dry-run propre + sbatch dédié + **leak fix (per-fold reset)** — **04/08**
5. [x] **H2 ChemBERTa scaffold COMPLET (job 12813)** : 0.7867 vs 0.8300, p<0.0001 → transformer ≤ GNN CONFIRMÉ
6. [x] **H3 re-runs fusion + salience (jobs 12811/12812)** : TFP pers_img dominant, TNE top dims identifiées
7. [x] **`p5_figure.py` écrit → bar figure** bipanel random/scaffold avec CI honnêtes ECFP4 — **04/08**
8. [ ] **H2 ChemBERTa random** (job 12814 en cours) → premier run avec courbes par époch
9. [ ] Courbes d'apprentissage (`p5_learning_curves.py` prêt, à exécuter après 12814)
10. [ ] Manuscrit LaTeX (thèse honest-negative L3 + interprétabilité L4)
11. [ ] Mise à jour régulière de **ce** document à chaque milestone

---

## 9. Pertinence littérature récente (extrait des références partagées)

Les références suivantes confirment et orientent la stratégie P5 :

| # | Source | URL | Point clé | Implication P5 |
|---|--------|-----|-----------|----------------|
| 1 | **BIB 2024 (Nałęcz‑Charkiewicz & Charkiewicz)** | https://academic.oup.com/bib/article/25/5/bbae391/7733456 | Revue systématique du quantum computing en bioinformatique (mapping) | Contexte NISQ/QC pour P3 (QKS : preuve de concept NISQ) |
| 1b | **MolPROP (J. Cheminformatics 2024)** | https://doi.org/10.1186/s13321-024-00846-9 | Fusion par concaténation GCN + ChemBERTa‑2 (MLM), meilleure sur petits jeux | Confirme le paradigme *GNN + transf‑seq* ; justifie l'arm ChemBERTa pour P5 |
| 2 | **IEEE‑Xplore** | https://ieeexplore.ieee.org/document/10466774 | Contrôle de biais dans les transferts de modèle | Renforce l'utilisation des tests DeLong + BH FDR (§5) |
| 3 | **ACM‑DL** | https://dl.acm.org/doi/fullHtml/10.1145/3575879.3576024 | MorphML : modèle morphologique multi‑graph | Inspire une éventuelle extension phase 2 (topologie + morphologie) |
| 4 | **Kaggle MOA** | https://www.kaggle.com/competitions/lish-moa/discussion/181113 | Méthodes de pooling des votes (RF, GNN, Transformer) | Justifie le script `p5_ensemble.py` (voting classifier hybride) |
| 5‑9 | **Sci‑Direct** | https://www.sciencedirect.com/science/article/pii/S0893608025005350 / https://www.sciencedirect.com/science/article/pii/S0010482522005820 | VAE + fine‑tune ChemBERTa pour réponse pharmacologique | Oriente une éventuelle phase 3 (génération conditionnelle) |
| 10‑12 | **Connected‑Papers** | https://www.connectedpapers.com/main/e7eb02275ea8f1e88bd449bf29eff56e53249297/Variational-Autoencoder-for-Anti%20Cancer-Drug-Response-Prediction/graph | Clusters de graph‑transformers autour de GIN/TNE | Valide le choix des modèles GIN‑TFP/TNE (fusion topologique) |
| 13‑16 | **GitHub** | https://github.com/dptech-corp/ligandexplorer / https://github.com/MonashBioinformaticsPlatform/learning-resource-links / https://github.com/Bayer-Group/FirstML / https://github.com/aspuru-guzik-group | Exemplars de pipelines (ligandexplorer, ML‑drugs) | Modèles de structuration réutilisables pour logs/checkpoints |
| 17 | **DeepChem** | https://deepchem.io/ | Bibliothèque standard pour featurisation + modèles | Intégration progressive de ses descripteurs (voir `p5_data.py`) |
| 18 | **ASPUR‑Guzik** | https://github.com/aspuru-guzik-group | Modèle de génération de ligands via GNN | Confirme la pertinence de la phase 3 (génération) |

## 10. Axes d'expérimentation supplémentaires (à explorer post-v1)

1. **Ensemble hybride** : RF + GNN (meilleur) + ChemBERTa via voting classifier (Kaggle MOA)
2. **Auto-encodeur latent** : VAE sur SMILES/GNN embeddings pour découvrir des représentations latentes discriminantes (Sci‑Direct)
3. **Fine-tune de transformers graphiques** : Graphormer ou DGT sur le panel canonique panel (Connected-Papers)
4. **Optimisation bayésienne des hyperparamètres** : utilisation de `optuna` ou `ray.tune` pour les modèles GNN
5. **Intégration DeepChem** : adopter ses featuriseurs (ECFP4, MACCS, etc.) et modèles de baseline dans `p5_data.py`
6. **Génération conditionnelle** : VAE/GAN conditionnée à l'activité pour proposer de nouveaux candidats (ASPUR‑Guzik)
7. **Analyse de stabilité topologique** : persistence landscapes au lieu de simples Betti curves pour représenter la forme des données
8. **Apprentissage contrastif** : pretraining GNN sur de grandes bases de données (ZINC, ChEMBL) puis fine-tune sur le panel

> Ces axes seront intégrés au fil des milestones, en fonction des résultats de la phase 1 et des ressources disponibles.

---

*Dernière mise à jour : 01/08/2026 — enrichi avec littérature SOTA et axes d'expérimentation.*
