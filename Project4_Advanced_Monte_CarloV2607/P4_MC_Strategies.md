# Project 4: Advanced Monte Carlo Strategies (P4)

This document outlines the major, long-term Monte Carlo architectural implementations. Due to their complexity and computational requirements, these strategies are designated for a future project iteration (P4), distinct from the rapid "Quick Wins" incorporated into P1 and P3.

## 4. Monte Carlo Tree Search (MCTS) intégré au Générateur (P1)

### Contexte
Le modèle génératif actuel (ScafVAE) échantillonne l'espace latent de manière probabiliste. Bien que cela permette de générer des molécules chimiquement valides, cela ne garantit pas que ces molécules posséderont le profil pharmacologique désiré (ex: polypharmacologie, MPO, synthèse).

### Stratégie (MCTS + RL)
L'intégration du **Monte Carlo Tree Search (MCTS)** vise à transformer le générateur en un agent d'optimisation dirigée. 
Le MCTS explorera l'arbre de décision de la construction moléculaire (ou l'espace latent) en utilisant une boucle d'Apprentissage par Renforcement (Reinforcement Learning - RL). 
- **Sélection et Expansion :** L'algorithme sélectionne les branches prometteuses menant à des échafaudages moléculaires d'intérêt.
- **Simulation (Rollout) :** Une simulation est lancée pour évaluer le potentiel de la branche.
- **Rétropropagation (Backpropagation) :** Les oracles (scores de docking Tartarus, scores MPO, filtres SA) évaluent la molécule générée et mettent à jour la "valeur" du nœud dans l'arbre.

### Architecture technique proposée
| Composant | Rôle | Technologie candidate |
|-----------|------|---------------------|
| **Environnement** | Définit l'état (SMILES/partiel), les actions (ajout de fragment), les transitions | RDKit + OpenAI Gym-compatible |
| **Agent MCTS** | Explore l'arbre de construction moléculaire | UCT (Upper Confidence Bound for Trees) |
| **Politique de base** | Génère des actions probables à partir de l'espace latent du ScafVAE | ScafVAE existant (P1) |
| **Oracles** | Évaluent la qualité d'une molécule complète | Tartarus docking, MPO, SYBA, SA |
| **Récompense** | Scalaire combiné des oracles | `reward = α·MPO + β·docking + γ·SYBA - δ·SA` |

### Fichiers associés (squelettes)
- [`scripts/p4_mcts_rl_env.py`](scripts/p4_mcts_rl_env.py) — Environnement RL moléculaire (squelette)
- [`scripts/p4_mcts_agent.py`](scripts/p4_mcts_agent.py) — Agent MCTS (squelette)
- [`scripts/p4_mcts_oracles.py`](scripts/p4_mcts_oracles.py) — Oracles de scoring (squelette)

### Estimation de l'Effort
- **Développement :** 2 à 3 semaines. Nécessite une refonte architecturale pour l'intégration de la boucle RL et des oracles de scoring en temps réel.
- **Calcul :** Plusieurs jours sur le cluster HPC pour l'entraînement RL.

---

## 5. Quantum Monte Carlo (QMC) pour la validation (P3)

### Contexte
Dans P3, le noyau quantique (QKS) et le TNE s'appuient sur des données géométriques et des approximations de structure électronique (DFT: B3LYP / wB97X-D). Bien que suffisantes pour le criblage, elles restent des approximations.

### Stratégie (QMC)
Le **Quantum Monte Carlo (QMC)** (Diffusion Monte Carlo ou Variational Monte Carlo) offre une solution quasi-exacte à l'équation de Schrödinger à N-corps. 
- L'objectif est d'utiliser le QMC sur un sous-ensemble très restreint de candidats (ex: les 20 meilleurs hits finaux) pour calculer les énergies de corrélation électronique avec une précision inégalée.
- Cela servira de validation "Gold Standard" pour prouver que les descripteurs QKS captent véritablement les effets quantiques complexes (dispersion, corrélation) pertinents pour la liaison au récepteur, au-delà de la limite de la DFT.

### Architecture technique proposée
| Étape | Outil | Entrée | Sortie |
|-------|-------|--------|--------|
| 1. Préparation géométrie | RDKit / xTB | SMILES | Coordonnées 3D optimisées |
| 2. Génération orbitales | PySCF / ORCA | Coordonnées 3D | Orbitales de trial (Hartree-Fock) |
| 3. QMC | QMCPACK / CASINO | Orbitales de trial | Énergie de corrélation électronique |
| 4. Analyse | Scripts maison | Énergies QMC | Corrélation avec scores QKS / TDA |

### Fichiers associés (squelettes)
- [`scripts/p4_qmc_prepare.py`](scripts/p4_qmc_prepare.py) — Préparation des inputs QMC (squelette)
- [`scripts/p4_qmc_analyze.py`](scripts/p4_qmc_analyze.py) — Analyse des énergies QMC (squelette)

### Estimation de l'Effort
- **Développement :** 1 à 2 semaines pour configurer les pipelines d'inputs complexes (ex: CASINO, QMCPACK) à partir des géométries moléculaires.
- **Calcul :** Extrêmement lourd ($O(N^4)$ à $O(N^6)$). Le calcul QMC d'une molécule antipaludique de taille moyenne (40+ atomes) peut requérir des milliers d'heures-cœur sur le HPC.

---

## 6. Feuille de route P4 (Roadmap)

| Phase | Livrable | Priorité | Dépendances |
|-------|----------|----------|-------------|
| 1 | Squelettes MCTS+RL fonctionnels | Haute | P1 ScafVAE, oracles docking/MPO |
| 2 | Preuve de concept MCTS sur 100 molécules | Haute | Phase 1 |
| 3 | Pipeline QMC end-to-end sur 1 molécule | Moyenne | P3 descripteurs, accès HPC QMC |
| 4 | Validation QMC sur 20 hits finaux | Basse | Phase 3, financement HPC |
