# AGENTS.md — Projet Malaria_codesV2

**Dernière mise à jour :** 21 juillet 2026 - TDA étendu à 19,849 molécules ✅

**GitHub :** https://github.com/NanaEngo/Malaria_codesV2

---

## ⚠️ WORKFLOW STRICT — LA BOUSSOLE

```
┌─────────────────────────────────────────────────────────────┐
│                     WORKFLOW OBLIGATOIRE                     │
│                                                              │
│   Données brutes (HPC)                                        │
│        │                                                      │
│        ▼                                                      │
│   DATA_ANALYSIS_REPORT_V2607.md ←── BOUSSOLE ──┐             │
│        │                                        │             │
│        ▼                                        │             │
│   Manuscrit P1/P2/P3/P4                         │             │
│        │                                        │             │
│        └─── Toute modification doit être         │             │
│             justifiée par le data analysis report│             │
│                                                    │             │
│   RÈGLE : Jamais de "navigation à vue"              │             │
│   Chaque action doit être tracée dans le            │             │
│   data analysis report AVANT d'être exécutée        │             │
└─────────────────────────────────────────────────────────────┘
```

### Règles pour les agents AI

1. **Lire le data analysis report AVANT toute action** — `DATA_ANALYSIS_REPORT_V2607.md` est la boussole
2. **Toute modification de code, de paramètres ou de protocole** doit être documentée dans le data analysis report AVANT exécution
3. **Ne jamais modifier le pipeline de benchmark** sans validation préalable dans le data analysis report
4. **Tout résultat inattendu** (AUC différant de >0.02 de l'attendu) doit être investigué et documenté dans le data analysis report
5. **Phases P3 à suivre strictement :** Phase 1 (n=200) → Phase 2 (n=5,000) → Phase 3 (n=19,849) — jamais de saut de phase
6. **Les fichiers TNE/TFP doivent être présents** pour les benchmarks P3 — sinon le résultat est invalide
7. **Git push après chaque étape validée**

---

## 📊 État des Projets (aligné sur DATA_ANALYSIS_REPORT_V2607.md)

### P1 — Chemical Space & Docking ✅ (Soumission prête)

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| Librairie hybride (65,856 molécules) | ✅ Complété | 92.6% ECFP4-unreachable, 69.3% scaffold recovery |
| Top-20 candidats | ✅ Complété | MPO 0.515–0.550, tous sélectifs (SI > 10) |
| Grilles V2 (4 cibles) | ✅ Déployé | pfDHFR, pfCRT, pfATP4, pfClpP |
| DEKOIS V2 (pfDHFR) | ✅ Terminé | AUC = 0.45 [0.37, 0.53] — Meeko uniforme |
| Redocking | ✅ Validé | RMSD < 2.0 Å toutes cibles |
| Validation Tartarus | ✅ Complété | ρ = 0.013 (p = 0.091), MPO orthogonal au docking |
| **Manuscrit** | ✅ **Prêt soumission** | Dernier audit adverse effectué et mitigé |
| **Cover Letter** | ✅ **Conforme** | 1 page, sans référence aux manuscrits compagnons |

### P2 — Polypharmacology & MD Validation ✅ (Prêt soumission JCIM)

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| RRS — 14 composés | ✅ Complété | Classes A*–D, validation H1 (ρ = 0.947) |
| PP-11 C59R anomaly | ✅ Investigé | Clash stérique Arg59/flavonoïde C-ring |
| PNS | ✅ Complété | PfCRT imputé (network mean) |
| ACSI | ✅ Complété | 23.5% top candidats ACSI > 0.70 |
| MD (4 complexes) | ✅ Complété | PfCRT (214) et PfATP4 (438) ligands liés ; PfClpP/DHFR non-liés |
| MM-GBSA (PfATP4) | ✅ Complété | Parser regex fixé |
| **Manuscrit** | ✅ **Prêt soumission JCIM** | Sections Methods complètes, figures TOC |

### P3 — Quantum-Inspired Representations 🔄 (Phase 2 prête)

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| **Benchmark final (v0.7, n=19,849)** | ✅ Complété | ECFP4=0.868, Hybrid=0.842 |
| **Ablation study** | ✅ Complété | QKS driver principal (p<0.001) |
| **QKS canonical** | ✅ Complété | Quantum 0.751 vs RBF 0.701 |
| **PHCO corrigé** | ✅ Complété | 0.500→0.801 (GetOnBits fix) |
| **Phase 1 — Grid search (n=200)** | ✅ **Complété** | **bd=6, nr=1, nk=30 → AUC 0.8534** |
| Figures SM (heatmap, boxplot, table) | ✅ Générées | `results/figures/p3_qp_*.png` |
| **TNE embeddings (bond_dim=8)** | ✅ **Généré** (job 11872) | 19,836/19,849 valides, 192 dims, 15.6× compression |
| **TDA fingerprints (19,849 mol.)** | ✅ **Généré** (job 11873) | 19,849/19,849 valides, 0 échecs, 78 features |
| **Phase 2 — Benchmark n=5,000** | ✅ **PRÊTE** | TNE + TDA + activité disponibles |
| Phase 3 — Benchmark n=19,849 | ⏳ Après Phase 2 | Meilleur combo sur librairie complète |

#### Fichiers de données P3 — État actuel

| Fichier | Statut | Molécules | Détail |
|:--------|:------:|:---------:|:-------|
| `results/p3_tne_embeddings.csv` | ✅ Généré | 19,836 | bond_dim=8, 192 dims, job 11872 |
| `results/p3_tda_fingerprints.csv` | ✅ Généré | 19,849 | 78 features TFP, job 11873 |
| `results/eos80ch_malaria_final_activity.csv` | ✅ Existant | 65,856 | Activités |
| `results/c6_primary_leads_synthesisable.csv` | ✅ Existant | 19,913 | SMILES + scores MPO |

#### Détail Phase 2 (prochaine action P3)

Exactement comme défini dans `DATA_ANALYSIS_REPORT_V2607.md` §3.4 :

**3 combos à évaluer sur n=5,000 molécules :**

| Combo | bond_dim | n_repeats | n_kpca | AUC (n=200) |
|:-----:|:--------:|:---------:|:------:|:-----------:|
| 1 (meilleur) | 6 | 1 | 30 | **0.8534** |
| 2 | 6 | 6 | 30 | ~0.83 |
| 3 | 6 | 6 | 20 | ~0.82 |

**Note :** Le sbatch actuel (`p3_single_combo.sbatch`) est hardcodé pour bd=6,nr=1,nk=30 uniquement. Pour les 3 combos, il faudra soit créer 3 sbatchs, soit modifier le sbatch pour accepter `--bond-dim`, `--n-repeats`, `--n-kpca` via `--export`.

### P4 — Advanced Monte Carlo 🔄 (Manuscrit en rédaction)

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| MCTS + ScafVAE | ✅ Implémenté | 33 fragments, PUCT, chimie priors |
| Pareto multi-objectif | ✅ Implémenté | MPO + SA + SYBA + RRS + PNS |
| Oracles (RRS, PNS) | ✅ Implémentés | 5 oracles validés |
| Baselines (Random, Greedy, GA) | ✅ Implémentés | Benchmark protocol défini |
| Benchmark protocol | ✅ Défini | 7 metrics, 10 seeds, 1000 oracle calls |
| **Manuscrit — Section Methods** | ✅ **Rédigée** | RRS/PNS intégrés |
| **.bib** | ✅ **Complété** | 30 entrées, toutes citations résolues |
| QMC validation | ✅ Implémenté | Pipeline complet |

---

## 📁 Structure des Répertoires

```
Malaria_codesV2/
├── AGENTS.md                              ← Ce fichier (LA BOUSSOLE)
├── DATA_ANALYSIS_REPORT_V2607.md          ← Data analysis report (SOURCE DE VÉRITÉ)
├── BMAD_Q1_DATA_ANALYSIS_REPORT.md        ← BMAD compliance report
├── synthese_audit_adverseriel_V2607.md    ← Audit adverse (P1)
├── Nouvel audit adversériel.md            ← Audit adverse (tous projets)
├── code_audit_V2607.md                    ← Code audit
├── bilan_corrections_P1_V2607.md          ← Bilan P1
├── Project1_Chem_space_antimalarial_V2_CorrectedGrid/  ← P1 (canonique)
│   ├── manuscript/                        ← Manuscrit + Cover Letter
│   ├── results/                           ← Résultats docking V2
│   └── scripts/                           ← Scripts P1
├── Project2_Polypharmacology_MD_ValidationV2607/       ← P2
│   ├── manuscript/LaTeX/                  ← Manuscrit JCIM
│   └── results/                           ← MD, RRS, PNS
├── Project3_Quantum_Inspired_RepresentationsV2607/     ← P3
│   ├── scripts/                           ← Benchmarks, param search, TNE, TDA
│   ├── results/                           ← CSVs, figures
│   └── logs/slurm/                        ← Logs SLURM
├── Project4_Advanced_Monte_CarloV2607/    ← P4
│   ├── manuscript/LaTeX/                  ← Manuscrit
│   ├── scripts/                           ← MCTS, Pareto, oracles
│   └── P4_MC_Strategies.md               ← Stratégie P4
├── quantum_simulations_framework/         ← Framework quantique (liaison P3)
└── mesohops/                              ← MesoHOPS (liaison P3)
```

---

## ⚙️ Environnement HPC

| Ressource | Valeur |
|:----------|:-------|
| **Hôte** | HPC local (SLURM) |
| **Conda env** | `malaria_md` |
| **Python** | 3.11.15 |
| **PennyLane** | 0.45.1 |
| **RDKit** | 2025.03.6 (conda-forge) |
| **JAX** | 0.10.1 (CUDA) |
| **TensorLy** | 0.9.0 |
| **ripser** | installé |
| **SLURM partition** | production (70% RAM cap = 89.6 GB) |

### Notes sur le GPU et la parallélisation (P2–P4)

#### GPU disponible
| Composant | Statut | Détail |
|:----------|:------:|:-------|
| **GPU** | 🟢 **Disponible** | NVIDIA RTX A4000 (CC 8.6, 16 GB VRAM, driver 580.159) |
| **CUDA 12** | 🟢 Installé | jax-cuda12, cupy-cuda12x, custatevec-cu12 |
| **lightning.gpu** | 🟢 Installé (et désactivé) | Plus lent que CPU pour évaluation paire-par-paire |
| **JAX CUDA** | 🟢 Installé | JAX 0.10.2, GPU détecté (CudaDevice), mais 8× plus lent |

#### Quand utiliser le GPU :

⚠️ **Ne PAS utiliser le GPU** pour le kernel quantique P3 (PennyLane) :
- Le noyau quantique évalue les paires une par une (boucle Python)
- Chaque appel GPU a un overhead qui domine le temps de calcul
- **CPU (lightning.qubit)** : 535 paires/s ✅ **Référence**
- **GPU (lightning.gpu)** : 420 paires/s ❌ 1.3× plus lent
- **JAX JIT GPU** : 81 paires/s ❌ 8× plus lent

✅ **Utiliser la parallélisation CPU** (joblib, n_jobs) quand possible :
- TNE/TDA pipelines : parallélisés via `--n-jobs`
- Benchmark P3 : `_kernel_matrix_chunked` force n_jobs=1 (PicklingError PennyLane)
- P4 MCTS : peut être parallélisé via SLURM array (100 tâches × 24 concurrentes)
- P2 MD : parallélisation OpenMM/Amber sur CPU

#### Quand le GPU sera utile :
- Si le pipeline change pour utiliser **Catalyst** (JIT complet PennyLane → XLA GPU) : `pip install pennylane-catalyst`
- Pour les calculs QMC (P4) : les solveurs électroniques (PySCF, QMCPACK) supportent CUDA
- Pour l'entraînement de réseaux de neurones (PyTorch/TensorFlow) : utilisation GPU native

### Commandes utiles

```bash
# Voir les jobs
squeue -u $USER --format='%.12i %.20j %.2t %.10M'

# Killer un job
scancel <JOB_ID>

# Logs P3
tail -f Project3_Quantum_Inspired_RepresentationsV2607/logs/slurm/p3_single_*.log

# Git push
git add -A && git commit -m "message" && git push origin master
```

---

## 📋 Prochaines Actions Prioritaires

### 1. P3 — Lancer Phase 2 (3 combos, n=5,000)
- ✅ TNE embeddings disponibles (bond_dim=8, 19,836 molécules)
- ✅ TDA fingerprints disponibles (19,849 molécules)
- 🔄 **Lancer le premier combo :** `bd=6, nr=1, nk=30` sur n=5,000
- Puis combos 2 et 3

### 2. P3 — Phase 3 (n=19,849)
- Une fois le meilleur combo confirmé à n=5,000, lancer sur la librairie complète

### 3. P4 — Finaliser manuscrit
- Compléter Introduction et Results (benchmark)
- Compiler et vérifier les références

---

## 🔗 Références Clés

| Document | Rôle |
|:---------|:-----|
| `DATA_ANALYSIS_REPORT_V2607.md` | **BOUSSOLE** — Toute décision doit s'y référer |
| `synthese_audit_adverseriel_V2607.md` | Audit adverse P1 — suggestions traitées ✅ |
| `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | Rapport BMAD (P1–P3 couverts) |
| `Project1_Chem_space_antimalarial_V2_CorrectedGrid/README.md` | Notes P1 |
| `Project4_Advanced_Monte_CarloV2607/P4_MC_Strategies.md` | Stratégie P4 |

---

## ✅ Jobs SLURM de la session

| Job ID | Script | Statut | Résultat |
|:------:|:-------|:------:|:---------|
| 11872 | `p3_tne_generate.sbatch` | ✅ Terminé | TNE bond_dim=8, 19,836 valides |
| 11873 | `p3_tda_extend.sbatch` | ✅ Terminé | TDA 19,849 mol., 0 échec |

## ❌ Leçons apprises (Navigation à vue interdite)

| Erreur | Impact | Leçon |
|:-------|:------:|:------|
| Modification du pipeline kernel (précalculé, JAX, dummy TNE) | AUC 0.785 vs 0.853 attendu → temps perdu | **Suivre le data analysis report** — tout écart doit être documenté AVANT |
| Lancement de jobs ad-hoc (n=500) sans suivre le plan Phase 1→2→3 | 3 jobs ratés, résultats inexploitables | **Respecter les phases** inchangées |
| Optimisation JAX du kernel (plus lent sur CPU) | Temps perdu, code complexifié inutilement | **Benchmarker AVANT de modifier** le pipeline |
| "On verra bien" au lieu de "le data analysis report dit quoi ?" | Dérive de 2 jours | **La boussole ne ment pas** |

---

## License

MIT License — voir fichier LICENSE à la racine.
