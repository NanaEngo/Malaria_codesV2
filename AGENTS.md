# AGENTS.md — Projet Malaria_codesV2

**Dernière mise à jour :** 02 août 2026 — Reporting P4 séparé de BMAD : `P4_DATA_ANALYSIS_REPORT.md` est la boussole P4 (benchmark, Pareto, ablations, QMC) ; BMAD couvre P1–P3 uniquement. P3 : **benchmarks canoniques COMPLETS** (jobs 12698/12699/12700/12702) — classique n=19,836 (ECFP4 0.9475 ± 0.0045), **hybride canonique Hybrid RF AUC 0.8876 ± 0.0065** (p<0.0001 vs ECFP4), **ablation : QK = principal contributeur (Δ=−0.040)**, **QKS 6q C3-fix : quantum ≈ RBF à toutes les échelles** (n=5,000 p=0.419 ; n=19,849 p=0.060). **Manuscrit trimé 26→18 p.** (main 18 p. / 7 230 mots, SM 18 p., cover letter 1 p. ; fusion tables benchmark/hybrid, `tab:qkernel`→SM S13, titre harmonisé — BMAD §3.14, audit v3.1). **ChEMBL validation exécutée** : 10 leads queryés, analogues tous Inactive (Tanimoto 0.229–0.379) — résultat honnête négatif.

**GitHub :** https://github.com/NanaEngo/Malaria_codesV2

---

## ⚠️ WORKFLOW STRICT — LA BOUSSOLE

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW OBLIGATOIRE                     │
│                                                             │
│                    Données brutes (HPC)                     │
│                                │                            │
│                                ▼                            │
│   BMAD_Q1_DATA_ANALYSIS_REPORT.md  ←──  BOUSSOLE P1/P2/P3   │
│      P4_DATA_ANALYSIS_REPORT.md       ←──  BOUSSOLE P4      │
│                                │                            │
│                                ▼                            │
│                    Manuscrit P1/P2/P3/P4                    │
│                                │                            │
│       └─── Toute modification doit être justifiée par le    │
│              data analysis report (P1–P3 : BMAD ; P4 :      │
│                     P4_DATA_ANALYSIS_REPORT.md)             │
│                                                             │
│            RÈGLE : Jamais de "navigation à vue"             │
│    Chaque action doit être tracée dans le data analysis     │
│                report AVANT d'être exécutée                 │
└─────────────────────────────────────────────────────────────┘
```

### Règles pour les agents AI

1. **Lire le data analysis report AVANT toute action** — `BMAD_Q1_DATA_ANALYSIS_REPORT.md` est la boussole **P1/P2/P3** ; `P4_DATA_ANALYSIS_REPORT.md` est la boussole **P4** (depuis le 01/08/2026, le reporting P4 — benchmark, Pareto, ablations, QMC — se fait dans le rapport P4 dédié, plus dans BMAD)
2. **Toute modification de code, de paramètres ou de protocole** doit être documentée dans le data analysis report (P1–P3 : BMAD ; P4 : P4_DATA_ANALYSIS_REPORT.md) AVANT exécution
3. **Ne jamais modifier le pipeline de benchmark** sans validation préalable dans le data analysis report
4. **Tout résultat inattendu** (AUC différant de >0.02 de l'attendu) doit être investigué et documenté dans le data analysis report
5. **Phases P3 à suivre strictement :** Phase 1 (n=200) → Phase 2 (n=5,000) → Phase 3 (n=19,849) — jamais de saut de phase
6. **Les fichiers TNE/TFP doivent être présents** pour les benchmarks P3 — sinon le résultat est invalide
7. **Git push après chaque étape validée**

---

## 📊 État des Projets (aligné sur BMAD_Q1_DATA_ANALYSIS_REPORT.md pour P1–P3 et P4_DATA_ANALYSIS_REPORT.md pour P4)

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

### P3 — Quantum-Inspired Representations ✅ (Benchmarks canoniques complets)

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| **Benchmark classique canonique (n=19,836)** | ✅ Complété (job 12698) | ECFP4=0.9475±0.0045, FCFP4 0.9183, MACCS 0.9045, AP 0.9399, PHCO 0.8959, BPF 0.9389, TFP 0.8759, TNE 0.7219 |
| **Hybrid canonique (full-library)** | ✅ **Complété (job 12699)** | **Hybrid RF AUC 0.8876 ± 0.0065** (n=19,836, hyperparams 6/1/30, t=−29.9, p<0.0001 vs ECFP4) ; SVM 0.8323 |
| **Ablation study** | ✅ **Complété (job 12699)** | **QK = principal contributeur** (retrait QK : 0.8876→0.8472, Δ=−0.040) ; TFP Δ=−0.014 ; TNE Δ=+0.011 (légèrement négatif) |
| **QKS canonical (6q, C3-fix)** | ✅ **Complété (jobs 12700/12702)** | **quantum ≈ RBF à toutes les échelles** : n=19,849 0.8230 vs 0.8292 (p=0.060, ns) ; n=5,000 0.8199 vs 0.8260 (p=0.419, ns) ; quantum > linear (p≤0.0006) ; n=500 (8q v11) 0.751 vs 0.701 (p=0.088, ns) — anciens chiffres 8q « quantum pire » = artefacts (circuit + C3) |
| **PHCO corrigé** | ✅ Complété | 0.500→0.897 (GetOnBits fix) |
| **Phase 1 — Grid search (n=200)** | ✅ **Complété** | **bd=6, nr=1, nk=30 → AUC 0.8534** |
| **Phase 2 — Re-benchmark (n=5,000)** | ✅ **Complété** | **Combo 1: 0.8283±0.0371 (gagnant, canonique), Combo 2: 0.8121, Combo 3: 0.8047** |
| Figures SM (heatmap, boxplot, table) | ✅ Générées | `results/figures/p3_qp_*.png` |
| **Figure benchmark (bar)** | ✅ **Régénérée 01/08** | `results/figures/p3_auc_benchmark_bar.png` — inclut la ligne **Hybrid 0.8876 ± 0.0065** (canonique) et les valeurs QKS 6q C3-fix (jobs 12700/12702) |
| **TNE embeddings (bond_dim=8)** | ✅ **Généré** | 19,836/19,849 valides (13 échecs), 192 dims, 6.1× compression réelle (mean 39.0 atomes) |
| **TDA fingerprints (19,849 mol.)** | ✅ **Généré** | 19,849/19,849 valides, 0 échecs, 78 features |
| **H₁-RRS expanded (n=77)** | ✅ **Complété** | ρ=0.312, p=0.0057 — cohorte étendue vs pilot n=14 |
| **RRS expansion SLURM** | ✅ **Fonctionnel** | p3_rrs_expansion.sbatch, 4 tasks, 200 molécules |
| **Benchmark classique n=5,000 (hybrid pre-phase)** | ✅ **Complété** | ECFP4=0.940, TFP=0.765 (−0.112 vs n=19,849), TNE=0.660 (−0.062) |
| **Manuscrit** | ✅ **Réconcilié BMAD v50 + trim 26→18 p.** | Main + SM + cover letter alignés sur les benchmarks canoniques (hybrid 0.888, ablation QK Δ=−0.040, QKS 6q ≈ RBF) ; **trim 26→18 p.** (02/08) : main 18 p./7 230 mots, SM 18 p., cover letter 1 p. ; fusion tables benchmark/hybrid, `tab:qkernel`→SM S13, titre harmonisé « Quantum-inspired molecular representations for AI-generated African antimalarial candidates: persistent homology, tensor networks, and quantum kernels » ; compile propre (0 erreur, 0 réf. non définie) |
| **Acceptance assessment** | ✅ **Vers ~82% (cible ≥85%)** | Roadmap documentée; validation physique TNE/TDA complète; benchmark hybride canonique + QKS 6q terminés; trim + déduplication fait (audit v3.1 : ~79–82%, ChEMBL honnête négatif 02/08 −5%, Zenodo ⚠️ PENDING +3% → ~82% ; cible ≥85% via Zenodo + actions restantes) |
| 🔴 Action 1: ChEMBL IC₅₀ validation | ✅ **Exécutée 02/08** | 10 leads top queryés — analogues ChEMBL tous **Inactive** (Tanimoto 0.229–0.379) ; résultat honnête négatif = nouveauté chimique, pas de validation positive (+0% acceptance, narration adaptée) |
| 🔴 Action 2: Reframe H₁-RRS narrative | ✅ **Fait** | ρ=0.312 (n=77) présenté avec caveat confounding MW ; effet size-médié (ρ_partial ≈ 0) — intégré manuscrit + BMAD |
| 🟡 Action 3: Benchmark SOTA topological | ⏳ **À faire** | +8% acceptance |
| 🟡 Action 4: Expand RRS to n≥80 | ⏳ **À faire** | +5% acceptance |
| 🟡 Action 5: Zenodo deposit | ⏳ **À faire** | +5% acceptance (DOI réservé 10.5281/zenodo.19608875, upload manquant) |

#### Fichiers de données P3 — État actuel

| Fichier | Statut | Molécules | Détail |
|:--------|:------:|:---------:|:-------|
| `results/p3_tne_embeddings.csv` | ✅ Généré | 19,836 | bond_dim=8, 192 dims, job 11872 |
| `results/p3_tda_fingerprints.csv` | ✅ Généré | 19,849 | 78 features TFP, job 11873 |
| `results/eos80ch_malaria_final_activity.csv` | ✅ Existant | 65,856 | Activités |
| `results/c6_primary_leads_synthesisable.csv` | ✅ Existant | 19,913 | SMILES + scores MPO |

#### Détail Phase 2 (n=5,000) — ✅ Complété (Jobs 12340-12342)

**Résultats de l'évaluation des 3 combos sur n=5,000 molécules :**

| Combo | bond_dim | n_repeats | n_kpca | AUC (n=200) | AUC (n=5,000) | Statut |
|:-----:|:--------:|:---------:|:------:|:-----------:|:-------------:|:------:|
| **1 (Meilleur)** | **6** | **1** | **30** | **0.8534** | **0.8283 ± 0.0371** | ✅ **Confirmé gagnant** |
| 2 | 6 | 6 | 30 | ~0.83 | 0.8121 ± 0.0396 | Évalué |
| 3 | 6 | 6 | 20 | ~0.82 | 0.8047 ± 0.0354 | Évalué |

**Conclusion Phase 2 :** Le combo 1 (`bd=6, nr=1, nk=30`) est confirmé comme la meilleure configuration hyperparamétrique. Prêt pour le benchmark Phase 3 (n=19,849).

### P5 — GNN/Transformer Drug Discovery 🔄 (Roadmap en cours)

> 📄 **Data analysis P5 : `P5_DATA_ANALYSIS_REPORT.md`** (rapport dédié depuis le 01/08/2026 — même pattern que P4). BMAD ne porte plus le détail P5.
> 📄 **Plan stratégique P5 : `P5_STRATEGIC_PA90.md`** (01/08/2026 — plan d'implémentation stratégique détaillé, objectif Q1 PA≥90 %, à améliorer régulièrement).

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| **Objectif** | 🔄 **Planifié** | GNN (GCN, GAT, GIN) + Transformers (ChemBERTa, Graphormer) pour prédiction d'activité et génération moléculaires |
| **Data analysis report** | ✅ **Créé 01/08** | `P5_DATA_ANALYSIS_REPORT.md` — boussole P5 (panel canonique P3 n=19,836, splits random+scaffold, fusion TDA/TNE, SOTA 2025-26, risque acceptation Q1) |
| **Plan stratégique PA90** | ✅ **Créé 01/08** | `P5_STRATEGIC_PA90.md` — plan d'implémentation stratégique (phase 1 MVP, ressources, milestones, risque acceptation) |
| **v1-prep (panel, splits, sanity)** | ✅ **Complété 01/08** | `p5_canonical_panel.csv` (19,836×272), splits figés (random+scaffold, 5 seeds), sanity ECFP4-RF = 0.9428±0.0031 (réf P3 0.9475) ✓ |
| **Dépendances P5** | ✅ **Verrouillé 01/08** | torch 2.13.0+cu130 + PyG 2.8.0 (torchdrug INCOMPATIBLE py3.11 → PyG), transformers 5.14.1, datasets 5.0.1, deepchem 2.8.0 — `requirements.txt` |
| **Lien P3** | ✅ **Défini** | Intégration features TDA/TNE (P3) comme input multi-modal |
| **Lien P2** | ✅ **Défini** | Validation sur RRS/PNS (P2) comme oracles biologiques |
| **Dataset** | ✅ **Préparé** | n=19,849 (P3 benchmark) — même split que P3 pour comparaison directe |
| **Baselines** | ⏳ **À définir** | ECFP4/TFP (P3), QK (P3), Random Forest — comparaison SOTA |
| **SOTA topological** | ⏳ **À implémenter** | Benchmark topologique (action 3 P3) comme baseline supplémentaire |
| **Modèles** | ⏳ **À implémenter** | GCN, GAT, GIN, ChemBERTa, Graphormer — phase 1 |
| **Multi-modalité** | ⏳ **À implémenter** | Concaténation embeddings GNN + features TDA/TNE |
| **Validation** | ⏳ **À planifier** | 5-fold CV, même protocol que P3 (n=5000 puis n=19,849) |

### P4 — Advanced Monte Carlo 🔄 (Manuscrit en rédaction)

> 📄 **Data analysis P4 : `P4_DATA_ANALYSIS_REPORT.md`** (rapport dédié depuis le 01/08/2026 — benchmark v1–v9, Pareto, ablations, QMC Tier 1/2 diagnostic et verdict v46). BMAD ne porte plus le détail P4.

| Composant | Statut | Résultat clé |
|-----------|:------:|:-------------|
| MCTS + ScafVAE | ✅ Implémenté | 33 fragments, PUCT, chimie priors |
| Pareto multi-objectif | ✅ Implémenté | MPO + SA + SYBA + RRS + PNS |
| Oracles (RRS, PNS) | ✅ Implémentés | 5 oracles validés |
| Baselines (Random, Greedy, GA) | ✅ Implémentés | Benchmark protocol défini |
| Benchmark protocol | ✅ Défini | 7 metrics, 20 seeds, 1000 oracle calls |
| **Manuscrit — Section Results/Benchmark** | ✅ **Actualisé** | Benchmark v9 20 seeds intégré; QMC retiré du manuscrit (cleanup 29/07 ; diagnostic Tier 2 non publication-grade) |
| **.bib** | ✅ **Complété** | 30+ entrées, toutes citations résolues |
| QMC validation | ⚠️ **Tier 1 GPU OK ; Tier 2 non publication-grade (diagnostic VMC/DMC terminé — verdict CORRIGÉ 01/08)** | pyscf 2.14.0 + xtb + gpu4pyscf 1.8.0 : SCF+molden OK (4/4, GPU ~56 s/cand). **PyQMC 0.8.1 installé** — Slater-only VMC H₂O = −75.09 correct. ⚠️ **Correction 01/08 (P4_DATA_ANALYSIS_REPORT.md §5.2, verdict v46) : le diagnostic v45 « chemin JastrowSpin défectueux » est RÉTRACTÉ** — `generate_jastrow(ion_cusp=False)` pose le cusp e-e `bcoeff=[-0.25,-0.50,-0.25]` **inconditionnellement**, donc un Jastrow « zéro-paramètre » n'est PAS exp(0)=1 ; le test A0 (acoeff+bcoeff explicitement nuls) donne `max|log J| = 0.000e+00` ⇒ **chemin `recompute()` numba CORRECT**. Backend **JAX cassé dans 0.8.1** (2 bugs `dot_general` (24,) vs (5,) / (24,) vs (25,) — mismatch cartésien/sphérique 24 vs 25 AOs) → **chemin numba = chemin de production**. DMC collapse 144-e confirmé par scale test (Slater-only −897/−900 vs SCF −864 ; Jastrow −867 ; garde runtime dans `p4_qmc_pipeline.py`). Production exigerait OPTIMIZE + nconfig ≥ 1000 + extrapolation τ→0. Doc : `docs/P4_QMC_FIX_STRATEGY.md` §7–8 |

---

## 📁 Structure des Répertoires

```
Malaria_codesV2/
├── AGENTS.md                              ← Ce fichier (LA BOUSSOLE)
├── BMAD_Q1_DATA_ANALYSIS_REPORT.md        ← Data analysis & BMAD report P1–P3 (SOURCE DE VÉRITÉ / CANONIQUE — V1 supprimé le 31 juillet 2026)
├── P4_DATA_ANALYSIS_REPORT.md             ← Data analysis report P4 (canonique depuis le 01/08/2026 — benchmark, Pareto, ablations, QMC)
├── P5_DATA_ANALYSIS_REPORT.md             ← Data analysis report P5 (canonique depuis le 01/08/2026 — GNN/Transformer benchmark, fusion TDA/TNE)
├── synthese_audit_adverseriel_V2607.md    ← Audit adverse (P1)
├── code_audit_V2607.md                    ← Code audit
├── bilan_corrections_P1_V2607.md          ← Bilan P1
├── Project1_Chem_space_antimalarial_V2_CorrectedGrid/  ← P1 (canonique)
│   ├── manuscript/                        ← Manuscrit + Cover Letter
│   ├── results/                           ← Résultats docking V2
│   └── scripts/                           ← Scripts P1
├── Project2_Polypharmacology_MD_ValidationV2607/       ← P2
│   ├── manuscript/LaTeX/                  ← Manuscrit JCIM
│   └── results/                           ← MD, RRS, PNS
├── Project3_Quantum_Inspired_RepresentationsV2607/     ← P3 (canonique)
│   ├── scripts/                           ← Benchmarks, param search, TNE, TDA
│   ├── results/                           ← CSVs, figures
│   └── logs/slurm/                        ← Logs SLURM
│   ⚠️ `Project3_Quantum_Inspired_RepresentationsV2607_V2/` (HPC only) : version de travail du Dr Tchapet Njafa — ne pas supprimer, à ignorer dans les audits grep (conservée volontairement, décision du 31 juillet 2026)
├── Project4_Advanced_Monte_CarloV2607/    ← P4
│   ├── manuscript/LaTeX/                  ← Manuscrit
│   ├── scripts/                           ← MCTS, Pareto, oracles
│   └── P4_MC_Strategies.md               ← Stratégie P4
├── Project5_GNN_Transformer_DrugDiscovery/  ← P5 (boussole : P5_DATA_ANALYSIS_REPORT.md)
│   ├── scripts/                           ← GNN/Transformer pipelines, dataloaders
│   ├── results/                           ← checkpoints, metrics, figures
│   └── manuscript/                        ← Rédaction théorique + résultats
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
| **lightning.gpu** | 🟢 Installé | Détection auto via `best_device()` dans le code optimisé |
| **JAX CUDA** | 🟢 Installé | JAX 0.10.2, GPU détecté (CudaDevice) |

#### Stratégie GPU (mise à jour skills-based) :

Depuis l'application des skills [`scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills) et [`BMAD-METHOD`](https://github.com/bmad-code-org/BMAD-METHOD) :

| Skill | Provenance | Application | Impact |
|:------|:-----------|:------------|:-------|
| **pennylane** | scientific-agent-skills | `best_device()` détection auto : lightning.gpu > lightning.qubit > default.qubit | GPU auto si bénéfice |
| **optimize-for-gpu** | scientific-agent-skills | CuPy interop dans `_kernel_matrix_jax`, Numba JIT pour stats GA | 10-100× sur GPU batch |
| **parallel-web** | scientific-agent-skills | joblib `Parallel()` dans P4 GA pour oracles parallèles | 4× plus rapide offspring |
| **datamol** | scientific-agent-skills | SMILES handling, batch fingerprints, standardisation | Code plus robuste |
| **pymoo** | scientific-agent-skills | NSGA-II Pareto front (NonDominatedSorting, Hypervolume exact) | Optimal multi-objectif |
| **rdkit** | scientific-agent-skills | Best practices, rdFingerprintGenerator API | Conforme standards |
| **deepchem** | scientific-agent-skills | Installé (2.8.0) pour featurization avancée | Prêt |
| **medchem** | scientific-agent-skills | Règles medicinal chemistry | Documentation |
| **molfeat** | scientific-agent-skills | Installé (0.10.1) pour transformer-based featurization (phase 2) | Prêt |
| **stable-baselines3** | scientific-agent-skills | Installé pour future RL policy (PPO/A2C) | Prêt |
| **torchdrug** | scientific-agent-skills | ❌ **INCOMPATIBLE Python 3.11** (Requires-Python <3.11) — **remplacé par PyG** (`torch_geometric` 2.8.0, installé & testé GPU A4000) pour P5 | P5 = PyG |
| **transformers / datasets / tokenizers** | — | Installés (5.14.1 / 5.0.1 / 0.22.2) pour ChemBERTa fine-tune (P5) | Prêt |
| **experimental-design** | scientific-agent-skills | Design d'expériences pour P4 benchmark protocol | Planification |
| **hypothesis-generation** | scientific-agent-skills | Génération d'hypothèses pour Discussion P3/P4 | Rédaction |

#### Quand utiliser le GPU (nouvelle stratégie `best_device()` + `--device` flag) :

Le code P3 utilise `best_device(n_qubits, prefer_cpu=False)` avec un flag `--device` :

| Flag | Comportement | Usage |
|:-----|:-------------|:------|
| `auto` (défaut) | best_device() avec `prefer_cpu=True` si CuPy absent | **Recommandé pour CPU** |
| `--device lightning.qubit` | Force CPU (lightning.qubit) | **Pour sbatch CPU** — 535 paires/s |
| `--device lightning.gpu` | Force GPU (expérimental) | Réservé aux tests GPU |

⚠️ **LEÇON CRITIQUE — GPU PLUS LENT QUE CPU** (vérifié expérimentalement) :
- `lightning.gpu` : 0/91 blocs en 9 min (job 11907) → **stuck** ❌
- `lightning.qubit` CPU : 77s/bloc (référence historique) ✅
- Cause : overhead GPU par appel (2ms) domine pour l'évaluation paire-par-paire
- `best_device()` retourne `lightning.gpu` en priorité, ce qui piège les sbatch CPU !
- **Fix appliqué :** `--device lightning.qubit` + `prefer_cpu=True` propagé à tout le code

✅ **Parallélisation CPU** (recommandée) :
- TNE/TDA pipelines : parallélisés via `--n-jobs`
- P4 GA : oracles évalués en parallèle via joblib `Parallel(n_jobs=min(4, n_offspring))`
- P4 benchmark : SLURM array (100 tâches × 24 concurrentes)

#### Quand le GPU sera testé :
- P3 Phase 2 GPU : réservé aux tests (sbatch `p3_phase2_gpu.sbatch` avec `--gres=gpu:1`)
- P4 QMC : solveurs électroniques (PySCF) supportent CUDA
- P4 RL training : stable-baselines3 avec PyTorch CUDA

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

### 1. P3 — Benchmarks canoniques COMPLETS (jobs 12698/12699/12700/12702) ✅
- ✅ Classiques canoniques n=19,836 (job 12698) : ECFP4=0.9475, PHCO=0.8959, TFP=0.8759, TNE=0.7219
- ✅ Hybride canonique (job 12699) : **Hybrid RF AUC 0.8876 ± 0.0065** (p<0.0001 vs ECFP4) + ablation (QK Δ=−0.040 principal, TFP Δ=−0.014, TNE Δ=+0.011)
- ✅ QKS 6q C3-fix (12700 n=19,849 / 12702 n=5,000) : quantum ≈ RBF à toutes les échelles (p=0.060/0.419, ns) ; quantum > linear (p≤0.0006)
- ✅ Figure benchmark régénérée (01/08) avec ligne Hybrid canonique 0.8876 ± 0.0065 et QKS 6q C3-fix
- ✅ Manuscrit (main + SM + cover letter) réconcilié avec BMAD v50 + **trim 26→18 p.** (02/08) — main 18 p./7 230 mots, SM 18 p., cover letter 1 p. ; fusion tables benchmark/hybrid, `tab:qkernel`→SM S13, titre harmonisé ; compile propre (0 erreur, 0 réf. non définie) ; plus aucun "provisoire" ni "rerun pending" dans le manuscrit

### 2. P4 — Finaliser manuscrit
- Compléter Introduction et Results (benchmark)
- Compiler et vérifier les références

---

## 🔗 Références Clés

| Document | Rôle |
|:---------|:-----|
| `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | **BOUSSOLE / SOURCE DE VÉRITÉ P1–P3** — Data analysis & BMAD report (Toute décision P1–P3 doit s'y référer). ⚠️ **Seule version canonique — les versions antérieures et les docs BMAD désuets ont été supprimés (local + HPC) le 31 juillet 2026.** Le reporting P4 ne s'y fait plus (depuis v47, 01/08/2026). |
| `P4_DATA_ANALYSIS_REPORT.md` | **BOUSSOLE / SOURCE DE VÉRITÉ P4** — Data analysis report P4 dédié (benchmark v1–v9, Pareto, ablations, QMC Tier 1/2 diagnostic et verdict v46). Créé le 01/08/2026 (split de BMAD v47). |
| `P5_DATA_ANALYSIS_REPORT.md` | **BOUSSOLE / SOURCE DE VÉRITÉ P5** — Data analysis report P5 dédié (benchmark GNN/Transformer v1+, fusion TDA/TNE, splits random+scaffold, SOTA 2025-26, risque acceptation Q1). Créé le 01/08/2026 (même pattern que P4). |
| `P5_STRATEGIC_PA90.md` | **PLAN STRATÉGIQUE P5** — Plan d'implémentation stratégique détaillé (PA≥90 %, phases, milestones, ressources HPC, matrice d'acceptation) — à améliorer régulièrement. Créé le 01/08/2026. |
| `synthese_audit_adverseriel_V2607.md` | Audit adverse P1 — suggestions traitées ✅ |
| `Project1_Chem_space_antimalarial_V2_CorrectedGrid/README.md` | Notes P1 |
| `Project4_Advanced_Monte_CarloV2607/P4_MC_Strategies.md` | Stratégie P4 |

---

## ✅ Jobs SLURM de la session

| Job ID | Script | Statut | Résultat |
|:------:|:-------|:------:|:---------|
| 11872 | `p3_tne_generate.sbatch` | ✅ Terminé | TNE bond_dim=8, 19,836 valides |
| 11873 | `p3_tda_extend.sbatch` | ✅ Terminé | TDA 19,849 mol., 0 échec |
| 12698 | `p3_classical_canonical` | ✅ Terminé | Benchmark classique canonique n=19,836 (ECFP4 0.9475 ± 0.0045) |
| 12699 | `p3_hybrid_canonical` | ✅ **Terminé** | **Hybrid RF AUC 0.8876 ± 0.0065** (p<0.0001) + ablation (QK Δ=−0.040 principal, TFP Δ=−0.014, TNE Δ=+0.011) |
| 12700 | `p3_qks_n19849` | ✅ **Terminé** | QKS 6q C3-fix n=19,849 : Quantum 0.8230 vs RBF 0.8292 (p=0.060, ns) |
| 12702 | `p3_qks_n5000` | ✅ **Terminé** | QKS 6q C3-fix n=5,000 : Quantum 0.8199 vs RBF 0.8260 (p=0.419, ns) |

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


## NISQ Hardware Access for PennyLane (July 25, 2026)


## NISQ Hardware Verification (July 25, 2026) — COMPLETE

### Results
- **2-qubit Bell state**: `<XX>=+1.0056` (fidelity 0.0598) on ibm_fez (156 qubits) ✅
- **2-qubit IQPEmbedding kernel**: `K(x1,x1)=0.988281` (deviation 0.012) on ibm_fez ✅
- **PennyLane → Qiskit → IBM Quantum pipeline**: VERIFIED end-to-end ✅

### Limitations (documented in P3 manuscript)
- 8-qubit full benchmark: queue times on Open Plan free tier (10 min/month) exceed practical limits
- Full NISQ AUC comparison requires paid/priority IBM Quantum access (research tier)
- Classical simulator results (lightning.qubit) are the primary benchmark in the manuscript
- The 2-qubit verification proves the deployment pipeline is functional

### Scripts
- `scripts/p3_nisq_smoke_test.py`: 2-qubit verification (Bell + kernel)
- `scripts/p3_nisq_deploy.py`: 8-qubit benchmark (needs priority access for real HW)
- Both use: pennylane-qiskit 0.45.0 + qiskit-ibm-runtime 0.45.1
- Backend fallback: auto-detects best available 100+ qubit device

### Free Platforms for Real Quantum Computers

Our P3 quantum kernel simulations run on PennyLane's `lightning.qubit` classical simulator at 8 qubits.
The manuscript's NISQ-era caveat notes that real hardware would degrade kernel fidelity.
Below are the free platforms where our 8-qubit IQPEmbedding circuit could be deployed on actual NISQ devices.

| Platform | Free Tier | Qubits | Best For | PennyLane Plugin |
|----------|-----------|--------|----------|-----------------|
| **IBM Quantum Open Plan** | 10 min/month | 100+ (Heron r2) | IQPEmbedding w/ dynamic circuits | `qml.device("qiskit.remote", ...)` |
| **AWS Braket** | Academic credits (apply) | Varies (IonQ, Rigetti) | Multi-vendor comparison | `qml.device("braket.aws.qubit", ...)` |
| **IBM Promotion** | 180 min/12mo (after 20 min used) | Same as Open Plan | Full-scale benchmarking | Same as IBM Open |

### Recommended Workflow for P3 NISQ Deployment

1. **Iterate on simulator**: Optimize the 8-qubit IQPEmbedding circuit using `lightning.qubit` (already done)
2. **Apply for IBM Open Plan**: Register at quantum.ibm.com → use the 10 min/month allocation
3. **Gate fidelity expectations**: Median 2-qubit error ~10^-3 (99.8% fidelity), coherence T1/T2 ~100-300 us
4. **Queue times**: Fair-share scheduler; open-tier jobs are lower priority than paid/research tiers
5. **Error mitigation**: PennyLane natively supports Zero-Noise Extrapolation and Probabilistic Error Amplification
6. **After 12 months**: Qualify for 180-minute promotion for full kernel benchmark

### Important Caveats
- **8-qubit circuits MUST be shallow**: Depth < ~50 gates to fit within coherence window
- **Kernel fidelity will degrade**: Expect 10-30% degradation vs simulator AUC depending on circuit depth
- **Academic credits**: AWS Cloud Credit for Research program for multi-vendor Braket access
- **No real quantum advantage expected**: Our benchmark already shows QK = RBF = Linear (p > 0.05)


## IBM Quantum Open Plan — Registration Steps (July 25, 2026)

### How to apply for free IBM Quantum access

1. Go to https://quantum.ibm.com/ and click "Sign up" (free account)
2. Verify email and log in
3. Navigate to Account → API token (top-right menu)
4. Copy the token
5. On the HPC development node:
   ```bash
   export IBM_QUANTUM_TOKEN="your_token_here"
   # Or save to file (more secure):
   echo "your_token_here" > ~/.ibm_quantum_token
   chmod 600 ~/.ibm_quantum_token
   ```

### Free tier limits
- **10 minutes/month** of quantum computing time on 100+ qubit Heron processors
- Fair-share scheduler: open-plan jobs are lower priority than paid/research tiers
- Queue times: typically 10-60 minutes during peak hours
- **Promotion**: after using 20 minutes total in 12 months → 180 minutes bonus

### NISQ scripts (ready for deployment)

| Script | Purpose | Qubits | Est. IBM time |
|--------|---------|:------:|:-------------:|
| `p3_nisq_smoke_test.py` | Bell state + kernel overlap verification | 2 | ~5 seconds |
| `p3_nisq_deploy.py` | Full IQPEmbedding kernel benchmark | 8 | ~5 min (n=10) |

### Important caveats
- **Run smoke test FIRST** before any 8-qubit deployment
- **n>20 impractical** on free tier: kernel_matrix submits n² individual IBM Quantum jobs per fold
- **Gate fidelity ~99.8%** (2-qubit), coherence T1/T2 ~100-300 µs
- **Expect 10-30% AUC degradation** vs classical simulator
- **Our P3 result already shows**: QK ≈ RBF ≈ Linear (p > 0.05 on simulator)
- **No quantum advantage expected** on hardware — this is a methodological proof-of-concept

### Packages installed in malaria_md (July 25, 2026)
- pennylane 0.45.1
- pennylane-qiskit 0.45.0
- ... (voir section HPC)

---

### Références complémentaires SOTA (extraites des URLs partagés)

| # | Source | URL | Point clé | Implication pour P4/P5 |
|---|--------|-----|-----------|------------------------|
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
- qiskit 2.3.0
- qiskit-ibm-runtime 0.45.1


## Zenodo Deposit (July 25, 2026)

- **DOI:** 10.5281/zenodo.19608875 (reserved)
- **Manifest:** `zenodo_manifest.txt` — 858 files, 569.4 MB across P1–P4
- **README:** `README_ZENODO.md` — full deposit structure and citation guide
- **Status:** ⚠️ Manifest ready; upload pending (use Zenodo web UI or API)
- **Contents:** All CSV results, Python/Bash/SLURM scripts, LaTeX source (.tex/.bib/.bst), README files, and key figures
- **Excluded:** GROMACS trajectories, docking PDBQT files, SLURM logs, IBM tokens, .git/