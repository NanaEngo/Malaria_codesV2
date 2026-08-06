# Project 5 — GNN/Transformer Drug Discovery (P5)

**Objectif :** benchmark contrôlé, anti-saturation et honnête : sur le panel
antipaludique canonique (n = 19,836), les GNN compacts et les transformers
(ChemBERTa) **ne battent pas les fingerprints classiques** (ECFP4) ; la valeur
est qualitative — attribution topologique (salience), pas le ranking.

**Boussole données :** `P5_DATA_ANALYSIS_REPORT.md`
**Plan stratégique :** `P5_STRATEGIC_PA90.md`
**Design v2 (gaps & novelty) :** `P5_DESIGN_GAPS_NOVELTY.md`

---

## 1. Gap & Nouveauté (ancré sur la revue Karim et al. 2026, 10.1007/s11831-026-10743-z)

Le design v2 part des gaps explicites identifiés par la revue systématique GenAI-bioinfo
2026 et en fait la colonne vertébrale de la thèse :

| Gap (revue 2026) | Levier P5 | Statut |
|:-----------------|:----------|:------:|
| **G1** Saturation des benchmarks | Panel unique **figé** + split scaffold = séparation mesurable | ✅ |
| **G2** « Larger is better » remis en cause | GNN compacts (A4000) vs transformer lourds — prédiction chiffrée | ✅ |
| **G3** OOD évalue mal l'utilité réelle | Split **scaffold-split** comme ligne primaire + courbes d'apprentissage | ✅ |
| **G4** Représentation « simple chaîne » | Fusion graphe + topologie (TFP) + tenseur (TNE) — multi-modale | ✅ |
| **G5** Interprétabilité/incertitude | Attribution/salience : quelles dims TFP/TNE portent le signal | ✅ |
| **G6** Biais de données | Espace **produits-naturels antipaludiques africains** (P1/P3) | ✅ |
| **G7** Plausibilité computationnelle ≠ validation | Ancrage **oracles biologiques P2/P3** (RRS, PNS, docking) | ✅ |

**Différenciateur unique :** la combinatoire *GNN-compact + fusion topologique
(TFP/TNE) + évaluation hors-distribution + espace NP antipaludique + ancrage
biologique* — l'articulation n'apparaît dans aucun des 82 articles revus.

---

## 2. Résultats clés (benchmark complet, splits figés)

| Descripteur/modèle | P3 (random, RF) | P5 (random) | P5 (scaffold) |
|:-------------------|:---------------:|:-----------:|:-------------:|
| ECFP4 (RF) | 0.9475 ± 0.0045 | **0.9433 ± 0.0002** | 0.8300 ± 0.0023 |
| GIN | — | 0.9098 ± 0.0067 | 0.8047 ± 0.0395 |
| GIN-TFP (fusion) | — | — | 0.8138 ± 0.0352 |
| GIN-TNE (fusion) | — | — | 0.8090 ± 0.0378 |
| ChemBERTa | — | **0.9121 ± 0.0047** | 0.7867 ± 0.0338 |

**Verdict (honest-negative + attribution) :**
1. **Reproduction ✓** — sanity ECFP4 P5 (0.9433) reproduit P3 (0.9475) à 0.004 près → baselines fiables, comparaison directe valide.
2. **Fingerprints = étalon** — ECFP4 (0.9433 / scaffold 0.8300) > GIN > ChemBERTa (0.7867) : les modèles « plus grands » n'apportent pas de free lunch (G2).
3. **H1/H2 = contrôle honnête de P3** — cohérent avec QKS ≈ RBF (p≥0.06) et « Do Larger Models Really Win? ».
4. **H3 (salience)** — les dims persistent-image de TFP dominent l'attribution → ce sont les mêmes features topologiques dont P3 a montré la contribution (QK/TDA/TNE) → thèse unifiée « topologie utile en attribution, pas en ranking ».

Figures : `results/figures/p5_auc_benchmark.png`, `p5_learning_curves.png`, `p5_salience.png`.

---

## 3. Intégration de la résistance aux antipaludiques

Le panel P5 est un **contrôle prédictif du programme anti-résistance** (P1/P2/P3) :
- L'intro ancre le besoin de **nouveaux scaffolds actifs contre les souches résistantes** (artémisinine-résistantes) et nomme les **mutations de résistance validées par MD** (PfDHFR N51I/C59R/S108N/I164L ; PfCRT K76T) qui définissent la provenance du panel (manuscrit V2608, §Intro et §Discussion).
- La section *Relation to the companion projects* relie explicitement P5 à la thèse transversale honnête-négative : prédiction (P3/P5) et génération (P4) aboutissent au même verdict — la complexité ne bat pas la simplicité sur la métrique scalaire ; sa valeur est qualitative (attribution / diversité Pareto).
- Bridge P4→P5 : la salience H3 fournit des features interprétables corrélables aux oracles RRS/PNS (P2/P4) — cf. H1-RRS P3 étendu (n=77, ρ=0.312).

---

## 4. Structure

```
Project5_GNN_Transformer_DrugDiscovery/
├── README.md                    ← Ce fichier
├── scripts/                     ← Pipeline d'entraînement, modèles, dataloaders (PyG, ChemBERTa)
├── manuscript/
│   ├── P5_manuscript_V2608.tex  ← Manuscrit canonique
│   └── Bibliography_P5.bib
├── results/                     ← Checkpoints, métriques, figures (benchmark complet)
└── docs/                        ← Roadmap et spécifications des modèles
```

---

## 5. Quick Start

```bash
conda activate malaria_md

# Panel + splits figés (déjà générés : results/p5_canonical_panel.csv, p5_splits_*.npy)
python scripts/p5_benchmark.py --model gin --split scaffold

# Figures
python scripts/p5_figures.py
```

---

*Note : toute action doit être documentée dans `P5_DATA_ANALYSIS_REPORT.md` avant exécution.*
