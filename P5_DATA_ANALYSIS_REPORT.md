# P5 Data Analysis Report — GNN/Transformer Drug Discovery

**Generated:** August 1, 2026 — **Split from BMAD** August 1, 2026
**Canonical:** ✅ This report is the **single source of truth for all P5 data analysis**. It follows the same split pattern as `P4_DATA_ANALYSIS_REPORT.md` (v47, August 1, 2026). **All future P5 data-analysis decisions are documented HERE, not in BMAD** (which now covers P1–P3 only).
**Environment:** HPC `malaria_md` (rdkit 2025.03.6, torch 2.13.0+cu130 + PyG 2.8.0, deepchem 2.8.0, transformers 5.14.1, scikit-learn 1.9.0) — P5 stack **verrouillé au 01/08/2026**, voir §7
**Coverage:** P5 only — GNN/Transformer benchmark (v1+), multi-modal fusion (TDA/TNE), molecular generation, validation vs P3 baselines

---

## Executive Summary

**P5 (GNN/Transformer Drug Discovery)** applies graph neural networks (GCN, GAT, GIN, GIN-FP) and sequence/attention models (ChemBERTa, Graphormer-style) to the **same curated antimalarial natural-product panel used in P3** (canonical n = 19,836 molecules, 5-fold stratified CV, Random-Forest-free deep pipelines). The goal is a **Q1 publication-ready benchmark (≥ 90 % acceptance probability)** that answers a well-defined, honest question: *do learned graph/sequence representations beat — or complement — classical fingerprints (ECFP4 AUC 0.9475) and the quantum-inspired hybrid (0.8876) already established in P3 on this exact panel?*

**Design principles (learned from P3 + SOTA 2025–2026):**
1. **Same panel, same split, same protocol as P3** → every P5 number is directly comparable to ECFP4 (0.9475), TFP (0.8759), TNE (0.7219), Hybrid (0.8876), QKS. No new dataset = no new confound.
2. **Rigorous baselines first**: Classical ML on fixed representations frequently beats deep models (47.4 % of winning comparisons across 156 in the 2026 "Do Larger Models Really Win?" benchmark). ECFP4/RF is the bar, not a strawman.
3. **Statistical rigor**: 5-fold × repeated seeds, paired tests with multiple-testing control (same standard as P3 audit) — avoid the "single split" trap that led to false GNN superiority claims.
4. **Novel multi-modal angle**: fuse learned GNN embeddings with the P3 topological descriptors (TDA/TFP, TNE) — the genuinely novel contribution that makes a Q1 submission defensible rather than "yet another GNN benchmark."

**Phase 1 (MVP, n = 5,000 → 19,836) delivers:** GCN/GAT/GIN/GIN-FP + ChemBERTa, random & scaffold splits, benchmark bar figure with the SOTA comparisons (per the 2025–2026 literature) — target: rigorous, reproducible, honest.

---

## 1. Project Definition & Objectives

### 1.1 Question
On the P3 canonical antimalarial activity panel (binary activity, n = 19,836):

- **Q1.** Do GNN/Transformer models beat the classical fingerprint baseline (ECFP4/RF, AUC 0.9475)?
- **Q2.** Does multi-modal fusion (GNN embedding + TFP + TNE) beat each modality alone?
- **Q3.** Do learned representations add value under **scaffold split** (harder, publication-relevant) vs random split?
- **Q4.** Can a compact GNN (GIN) reach transformer-level performance at a fraction of compute (MolGraphBench: GCN/GIN optimal for regression; ChemBERTa-3: transformers easier to scale but not universally better)?

### 1.2 Acceptance target (Q1, ≥ 90 % probability)
A defensible Q1 contribution needs at least **three** of:
1. A **positive, reproducible result** (e.g., multi-modal GNN > ECFP4 on scaffold split by a paired-significant margin).
2. An **honest negative or null result** where the field's SOTA over-claims (this is highly valued in 2025–2026, cf. "Do Larger Models Really Win?", MolGraphBench, Heidenreich 62,820-model study).
3. A **methodological/interpretability contribution** (which topological feature carries signal; attention attribution).
4. A **dataset/benchmark contribution** (a clean antimalarial NP activity benchmark with P3 topologies, released on Zenodo — mirrors P1/P3 practice).

The submission thesis: *"On a curated natural-product antimalarial panel, compact GNNs with topological descriptor fusion close the gap with — and under scaffold split exceed — classical fingerprints, while transformers offer no free lunch at this scale."*

---

## 2. SOTA Landscape (2025–2026, from deep web search Aug 1, 2026)

### 2.1 GNN architectures
- **GCN / GIN** — recommended defaults for molecular regression (MolGraphBench, arXiv 2602.20573): GCN RMSE 0.518 (B3DB), GIN-FP RMSE 1.022 (FreeSolv), GIN MAE 63.783 (RT). GNN-FP fusion mostly **non-complementary** (fingerprint pre-fusion redundant).
- **GAT / GraphSAGE** — competitive, higher variance.
- **DumplingGNN** (IJMS 2025) — hybrid MPNN+GAT+GraphSAGE with 3D info: BBBP 96.4 % ROC-AUC, ToxCast 78.2 %, PCBA 88.87 %; 3D dramatically helps (0.734 → 0.915 acc with conformers).
- **HimNet** (Commun. Chem. 2026) — hierarchical interaction message net (atom/motif/molecule/fingerprint layers + attention): BACE 0.890, BBBP 0.954, ClinTox 0.950; **evaluated on malaria activity regression** — directly relevant baseline.
- **MoleculeFormer** (Commun. Biol. 2025) — GCN+Transformer dual-graph, 28 datasets, 3D equivariant.

### 2.2 Graph/sequence Transformers
- **Graphormer-style (SPD/centrality biases)**: CardinalGraphFormer (arXiv 2602.02201) — sparse attention + cardinality-preserving channel + contrastive/masked pretraining; significant gains on 10/11 MoleculeNet/OGB/TDC tasks (BBBP 0.938, hERG 0.898, ClinTox 0.954).
- **DGT — dual graph transformer** (Nat. Commun. 2026): jointly models atom + bond graphs with stereogeometry; "considerably outperforms SOTA."
- **BiScale-GTR** (arXiv 2604.06336): fragment-aware graph transformer, BPE fragment tokens, GIN atom encoder + Transformer; SOTA on MoleculeNet/PharmaBench/LRGB.
- **ChemBERTa-3** (Digital Discovery 2026 / ChemRxiv 2025): open-source training framework (DeepChem-integrated); transformers scale easier than GNNs; MoLFormer-class models on ZINC20/PubChem. **We do NOT retrain foundation models** — we fine-tune released weights.

### 2.3 The honest-benchmark lesson (critical for framing)
- **"Do Larger Models Really Win?"** (2026, 26 endpoints, 156 comparisons): classical ML wins 47.4 %, pretrained sequence models 28.8 %, GNNs 21.8 %. Under scaffold split GNNs/sequence models are competitive; under random split classical ML dominates.
- **Heidenreich systematic study** (62,820 models): RF on RDKit2D/ECFP4 beats MolBERT/GROVER on most MoleculeNet under scaffold split; GROVER+RDKit (fingerprint-concat) improves a lot → **fingerprint fusion is a proven lever** (supports our Q2/Q4).
- **Low-data regime** (ChemRxiv 2026): hybrid GCN+ChemBERTa concatenation fusion (GTCA-Cat) improves low-data; simple concatenation ≥ cross-attention. GPR beats deep models on BACE bioactivity.

**Consequence for P5:** our likely-winning configuration is **GNN + fingerprint/topology fusion** (GIN-FP with TFP/TNE), not a big transformer. Transformers (ChemBERTa fine-tune) serve as the scale/sequence comparison arm.

---

## 3. Dataset & Protocol (locked from P3)

### 3.1 Panel
- **Canonical panel n = 19,836** (TFP-order ∩ dedup-activity ∩ finite-TNE), binary activity label, identical to P3 (BMAD v51). SMILES source: `results/eos80ch_malaria_final_activity.csv` (65,856) → canonical subset.
- P3 feature files to reuse: `p3_tne_embeddings.csv` (19,836, 192-d), `p3_tda_fingerprints.csv` (19,849, 78-d TFP).
- No new activity labels: keeps P5 directly comparable to P3 and avoids dataset-construction criticism.

### 3.2 Splits (both reported)
1. **Stratified random 5-fold** (reproducibility/benchmark arm).
2. **Bemis–Murcko scaffold 5-fold** (harder, publication arm) — exact DeepChem/MoleculeNet-style protocol, indices released.
- **Repeated seeds**: ≥ 5 seeds per model × split (statistical power; matches P3 audit standard).

### 3.3 Metrics
- Classification: ROC-AUC (primary), AP, F1, balanced accuracy.
- Paired **DeLong / bootstrap** tests vs ECFP4-RF and vs each modality; **Benjamini–Hochberg** FDR control across comparisons (avoids the P3 Bonferroni lesson; document correction in §8).
- Report mean ± std across seeds; activity-cliff-aware discussion (learning-curve caveat).

---

## 4. Models & Implementation Plan

### 4.1 Phase 1 — MVP benchmark (v1)
| Model | Type | Input | Notes |
|:------|:-----|:------|:------|
| ECFP4 + RF | classical bar (P3) | ECFP4 2048-bit | **hard baseline, AUC 0.9475** |
| GCN | GNN | 2D graph | MolGraphBench default |
| GIN | GNN | 2D graph | MolGraphBench: optimal regression |
| GAT | GNN | 2D graph | attention arm |
| GIN-FP | GNN+FP | graph + ECFP4 | fingerprint fusion arm |
| GIN-TFP | GNN+topology | graph + TFP(78) | **P3 topology fusion (novel)** |
| GIN-TNE | GNN+topology | graph + TNE(192) | **P3 tensor fusion (novel)** |
| ChemBERTa (fine-tune) | sequence transformer | SMILES | released weights, `seyonec/ChemBERTa-zinc-base-v1` or ChemBERTa-3 |
| Hybrid-All | multi-modal | graph + TFP + TNE + ECFP4 | full fusion (Q2) |

### 4.2 Phase 2 — Scaffold split + interpretability (v2)
- Re-run best 3 models under scaffold split.
- Attention/attribution analysis: which TFP/TNE dims the GNN attends to (bridge to P3 § H1-RRS).
- Learning curves (N = 500 → 19,836) to characterize low-data regime (aligns with 2026 learning-curve literature).

### 4.3 Phase 3 — Generation (optional, stretch)
- GNN/Transformer-based generative validation on the P3 top candidates (or use P4 MCTS) — only if Phase 1–2 show a clear win; do NOT bloat the core paper.

---

## 5. Novelty / Contribution Statement (for Q1 framing)
1. **First GNN/Transformer benchmark on the canonical P3 antimalarial NP panel**, with the same split/protocol as the published-framework quantum/classical comparison → cross-project comparability.
2. **Topological-descriptor fusion**: TFP (persistent homology) + TNE (tensor network) as auxiliary GNN channels — a concrete, mechanistic multi-modal contribution (not blind concatenation).
3. **Honest scaling conclusion** (transformers ≠ free lunch at n ≈ 2×10⁴), consistent with the 2025–2026 scaling-benchmark literature.
4. **Reusable public benchmark** + Zenodo deposit (mirrors P1/P3 practice, strengthens acceptance odds).

---

## 6. Risk Register (acceptance-risk → mitigation)
| Risk | Likelihood | Impact | Mitigation |
|:-----|:----------:|:------:|:-----------|
| GNN does not beat ECFP4 (likely, cf. SOTA) | High | High | Frame as honest negative + fusion/complementarity result (still Q1-value: "Do Larger Models Really Win?" was accepted; Nature Comm 2023 Deng et al. framed exactly this) |
| Transformer underperforms on small panel | High | Medium | Position transformers as scale/sequence arm; do not make them the headline |
| Compute limits (single node, A4000 GPU, CPU slow) | Medium | Medium | GIN/GCN/GAT small (torchdrug); ChemBERTa-base fine-tune on n=19,836 feasible; cache features once |
| Overfitting / variance at n≈2×10⁴ | Medium | Medium | Repeated seeds, scaffold split, learning curves, dropout/weight-decay sweeps |
| "Yet another benchmark" criticism | High | High | The P3-comparability + topological-fusion + honesty angle is the differentiator |

---

## 7. Dependencies & Environment (LOCKED Aug 1, 2026)
**Stack GNN/Transformer installé et vérifié** dans `malaria_md` (Python 3.11.15, torch CUDA OK sur NVIDIA RTX A4000, CC 8.6) :

| Package | Version | Statut |
|:--------|:--------|:-------|
| torch | 2.13.0+cu130 | ✅ (GPU A4000 OK) |
| torch-geometric (PyG) | 2.8.0.post1 | ✅ GIN forward testé |
| transformers | 5.14.1 | ✅ installé (pour ChemBERTa fine-tune) |
| datasets | 5.0.1 | ✅ installé |
| tokenizers | 0.22.2 | ✅ installé |
| deepchem | 2.8.0 | ✅ installé (featurization) |
| rdkit | 2025.03.6 | ✅ présent |
| scikit-learn / pandas / numpy / scipy / tqdm | 1.9.0 / 2.3.3 / 2.4.6 / 1.17.1 / 4.68.3 | ✅ présents |
| molfeat | 0.10.1 | ✅ présent |
| huggingface-hub | 1.26.0 | ✅ installé |

**Décision clé : `torchdrug` est INCOMPATIBLE avec Python 3.11** (`Requires-Python < 3.11` — aucune version disponible pour 3.11.15). On utilise donc **PyG (`torch_geometric`) comme unique stack GNN** (modern, maintenu, GPU A4000 testé). `dgl` non installé (non requis avec PyG). AGENTS.md doit être corrigé : les lignes « torchdrug/deepchem/transformers installé » sont obsolètes (seul torchdrug manque — deepchem/transformers sont désormais réellement installés).

- Lock : `Project5_GNN_Transformer_DrugDiscovery/requirements.txt` (généré) + snapshot conda env.
- GPU policy: follow P3 lesson — **A4000 GPU can be slower than CPU for pair-wise ops**; use GPU only for dense batch training (GNN/transformer forward/backward), CPU for feature caching. Lock in §7.1 of this report.

---

## 8. Tracking / Logging Convention (mirrors P3/P4)
- Every benchmark version (v1, v2, …) logged here in §10 with CSV paths, seeds, exact command, wall-time, and machine.
- Result files under `Project5_GNN_Transformer_DrugDiscovery/results/`; scripts under `.../scripts/`; logs under `.../logs/slurm/`.
- Every code/parameter/protocol change documented HERE **before** execution (AGENTS.md rule).
- Statistical corrections (Bonferroni/FDR choice) documented at the time of the first multi-comparison.

---

## 9. Checklist before any training run
- [x] Panel exported to `results/p5_canonical_panel.csv` (SMILES, activity, TFP, TNE aligned on canonical indices) — **19,836 rows verified**.
- [x] Splits (random + scaffold 5-fold, ≥5 seeds) computed once and **frozen** as `results/p5_splits_*.npy` — no split regeneration per run.
- [x] ECFP4-RF reproduction of 0.9475 on the frozen panel (sanity gate) — **0.9428 ± 0.0031 PASSED**.
- [x] Requirements locked (`Project5_GNN_Transformer_DrugDiscovery/requirements.txt`).
- [ ] GPU vs CPU smoke test recorded (P3 lesson) — next GNN script must record this.

---

## 9bis. Comparaison inter-projets (P3/P5 et P4/P5) — ajout 04/08

### P5 vs P3 — le même terrain, la même leçon

P3 (quantum-inspired kernels, RF) et P5 (GNN/transformer) partagent **le même panel
canonique n=19,836** et les mêmes fingerprints. La comparaison n'est valable que sur le
**split random** (P3 = StratifiedKFold 5-fold random uniquement ; le split scaffold est
l'apport de P5) :

| Descripteur/modèle | P3 (random, RF) | P5 (random) | P5 (scaffold) |
|:-------------------|:---------------:|:-----------:|:-------------:|
| ECFP4 (RF) | 0.9475 ± 0.0045 | **0.9433 ± 0.0002** | 0.8300 ± 0.0023 |
| TFP seul | 0.8759 ± 0.0059 | — | — |
| TNE seul | 0.7219 ± 0.0068 | — | — |
| Hybrid P3 (QK+TFP+TNE, RF) | 0.8876 ± 0.0065 | — | — |
| GIN | — | 0.9098 ± 0.0067 | 0.8047 ± 0.0395 |
| GIN-TFP (fusion) | — | — | 0.8138 ± 0.0352 |
| GIN-TNE (fusion) | — | — | 0.8090 ± 0.0378 |
| ChemBERTa | — | **0.9121 ± 0.0047** | 0.7867 ± 0.0338 |

**Lectures :**
1. **Reproduction ✓ :** le sanity ECFP4 P5 (0.9433) reproduit P3 (0.9475) à 0.004 près
   (même protocole, même panel) → les baselines sont fiables et la comparaison directe est valide.
2. **Le signal topologique n'est pas un game-changer :** TFP/TNE en fusion GNN (P5, scaffold)
   ≈ TFP/TNE seuls en RF (P3, random 0.876/0.722) ; la fusion topologique n'inverse pas le
   classement face aux fingerprints. Cohérent avec l'ablation P3 (TNE Δ=+0.011 marginal).
3. **H1/H2 P5 = contrôle honnête de P3 :** la même plateforme, poussée avec des modèles
   « plus grands » (GNN, transformers), confirme que **les fingerprints restent l'étalon** —
   c'est exactement le message de P3 (kernel quantum ≈ RBF ≈ linéaire, p≥0.06) et de
   « Do Larger Models Really Win? ». P3 reste le win du projet (Hybrid 0.8876, ablation QK Δ=−0.040) ;
   P5 le renforce en honest-negative contrôlé.
4. **H3 (salience) connecte P5 → P3 :** les dims persistent-image de TFP dominent la salience P5
   → ce sont les mêmes features topologiques dont P3 a montré la contribution (QK/TDA/TNE).
   → argument unifié « topologie utile en attribution, pas en ranking ».

### P5 vs P4 — deux honest-negatives qui se complètent

P4 (génération) et P5 (prédiction) ont des protocoles différents (P4 = récompense scalaire
multi-objectif sur 20 seeds, MCTS/GA/Random ; P5 = AUC ROC sous splits random+scaffold) :
**aucun chiffre n'est directement comparable**. Ce qui compte, c'est le **parallèle
structural des conclusions** :

| Axe | P4 (génération, v12 canonical) | P5 (prédiction) |
|:----|:-------------------------------|:----------------|
| Modèles vs baselines | Random 0.7335 > MCTS+ScafVAE 0.7276 > Greedy 0.7211 > GA 0.7027 | ECFP4 0.9433/0.8300 > GIN > ChemBERTa 0.7867 |
| Écart au meilleur simple | MCTS vs Random Δ=0.006 (t=2.41, p=0.026) | GIN vs ECFP4 Δ=−0.025 (p=0.018) |
| Verdict principal | MCTS n'améliore pas la récompense scalaire (random ≤ égal) | Les modèles « plus grands » n'améliorent pas l'AUC (fingerprints ≥) |
| Valeur réelle | **Pareto front divers** (4 solutions non-dominées, HV 1.2366) | **Salience/interprétabilité** (dims pers_img dominantes) |
| Message unifié | « Le scoring simple gagne ; la valeur est dans la diversité du front » | « Les fingerprints gagnent ; la valeur est dans l'attribution » |

**Ce que P5 dit relativement à P4 :**
1. **Cohérence narrative du projet :** les deux projets indépendants (génération et prédiction)
   aboutissent au **même pattern honest-negative** — la complexité (MCTS, GNN, transformer) ne bat
   pas la simplicité (Random, ECFP4) sur la métrique scalaire, mais apporte une contribution
   qualitative (diversité Pareto / interprétabilité topologique). C'est une **thèse transversale
   forte** pour le manuscrit P5 et pour l'ensemble Q1.
2. **Bridge P4 → P5 possible (leverage) :** la salience H3 (dims pers_img de TFP/TNE) fournit des
   **features interprétables à corréler aux oracles P4** (RRS/PNS — cf. H1-RRS P3 étendu, n=77).
   Les candidats du Pareto P4 pourraient être re-scorés par le modèle P5 ECFP4-RF (le meilleur
   prédicteur) — pas par un GNN. → le manuscrit P5 peut se référencer explicitement à P4 comme
   « compagnon de génération ».
3. **P5 ne corrige pas P4, il le corrobore :** pas de fuite/artefact du type benchmark P4
   (drift oracle Tartarus, config par défaut, greedy bug) détecté côté P5 — les deux honest-negatives
   sont indépendamment fiables.

### Figures & tables de perspective (P5/P3, P5/P4) — à produire/déjà produites

| # | Figure/Table | Contenu | Projet | Fichier | Statut |
|:-:|:-------------|:--------|:-------|:--------|:------:|
| **F1** | Bar chart bipanel **random/scaffold** P5 (ECFP4-RF vs GIN/GIN-TFP/GIN-TNE/ChemBERTa, mean ± CI, ligne baseline ECFP4 pointillée) | Figure principale manuscrit (Results) | P5 | `results/figures/p5_auc_benchmark.png` | ✅ **Générée 04/08** |
| **F2** | Bar chart canonique **P3 random** (ECFP4/FCFP4/MACCS/AP/PHCO/BPF/TFP/TNE/Hybrid-QK, RF) | Réf. P3 (compare la plateforme commune) | P3 | `Project3/.../figures/p3_auc_benchmark_bar.png` | ✅ Existe (01/08) |
| **F3** | **Salience dims TFP/TNE** (bar par modèle ; blocs H/pers_img/betti colorés TFP) — top dims 42/43/52/53/54 (TFP), 68/43/92/66/165 (TNE) | Figure H3 (interprétabilité, L4) | P5 | `scripts/p5_salience_figure.py` → `results/figures/p5_salience.png` | ✅ **Générée 05/08** |
| **F4** | **Courbes d'apprentissage** (val AUC/époch, GNN vs ChemBERTa, par split) | Figure Methods/Results (v3-c) | P5 | `scripts/p5_learning_curves.py` → `results/figures/p5_learning_curves.png` | 🔄 **Jobs 12836–12840 (curves-only, 05/08)** — GIN random/scaffold, GIN-TFP/TNE scaffold, ChemBERTa scaffold ; ChemBERTa random déjà capturé |
| **T1** | Tableau comparatif **P5 vs P3** (§9bis ci-dessus) : mêmes panel + fingerprints, split random seul comparable ; sanity ECFP4 0.9433 ≈ 0.9475 | Manuscrit Discussion/Table S | P5/P3 | `P5_DATA_ANALYSIS_REPORT.md` §9bis | ✅ Rédigé 04/08 |
| **T2** | Tableau **P5 vs P4** (parallèle structural honest-negative : modèles vs baselines, verdict, valeur réelle) | Manuscrit Discussion | P5/P4 | `P5_DATA_ANALYSIS_REPORT.md` §9bis | ✅ Rédigé 04/08 |
| **T3** | Tableau **hiérarchie scaffold finale** (ECFP4-RF 0.8300 > GIN-TFP 0.8138 > GIN-TNE 0.8090 > GIN 0.8047 > ChemBERTa 0.7867) + statistiques paired | Manuscrit Results (table principale) | P5 | à rédiger dans manuscrit | ⏳ Manuscrit |
| **T4** | Tableau **références SOTA** : Guo & Ding 2026 (47.4% classiques gagnants, 156 comparaisons), Benchmarking Pretrained Embeddings (25 modèles ≈ ECFP), Boldini 2024 (fingerprints NPs) | Manuscrit Introduction/Discussion (positionnement) | P5 | à rédiger | ⏳ Manuscrit |

**Usage prévu au manuscrit :** F1 = figure principale Results (preuve honnête-négative) ;
F2 + T1 = ancrage P3 (même plateforme, même panel → la comparaison est contrôlée) ;
F3 + F4 = contributions qualitatives (interprétabilité topologique + courbes d'apprentissage) ;
T2 + T4 = cadrage Discussion (parallèle P4 et littérature SOTA 2025-26).

---

## 10. Version History
| Version | Date | Models | Split | Result summary | Files |
|:-------:|:-----|:-------|:------|:---------------|:------|
| v1 | Aug 1, 2026 | (planned) | random 5-fold | pending | — |
| v2 | Aug 4, 2026 | design restart (gaps/novelty) | — | Design relancé sur gaps revue GenAI 2026 (`P5_DESIGN_GAPS_NOVELTY.md`) + fix instrument de mesure | fix `self.folds` (`p5_benchmark.py:114`), dry-run ne pollue plus ckpt/CSV, résultats GIN dummy AUC=0.5 supprimés |
| v3-a | Aug 4, 2026 | chemberta leak fix | scaffold | **ChemBERTa cross-fold leak trouvé+fixé** (model non reset entre folds → folds 1+ héritaient du fine-tune). Ckpts contaminés supprimés, relance. | `p5_chemberta.py` (per-fold reset) ; fold-0/1 scaffold post-fix 0.8247/0.7857 ✓ |
| v3-b | Aug 4, 2026 | **H3 salience (interprétabilité)** | scaffold | Salience capturée (mean \|W\| desc-projection, 25 folds). **TFP : dims persistent-image (33:58) dominantes** (sal 0.079 vs H 0.0485, betti 0.0547 ; top dims 42/43/52/53/54). **TNE : top dims 68/43/92/66/165**, top-10% dims = 17.3% salience. Fusion re-runs : GIN-TFP 0.8138±0.0352, GIN-TNE 0.8090±0.0378. | `p5_{GIN-TFP,GIN-TNE}_scaffold_salience.json` |
| v3-c | Aug 4, 2026 | figures + learning curves | random+scaffold | **Capture val_auc par époch ajoutée aux 2 loops** (GNN `p5_benchmark.py`, ChemBERTa `p5_chemberta.py`) → clé `curves` au ckpt pour les runs FUTURS uniquement (résultats committés intacts). Figure benchmark rénovée `p5_figure.py` (bipanel random/scaffold, CI honnêtes ECFP4 depuis seed_means). | `p5_figure.py`, `p5_learning_curves.py` |
| v3-d | Aug 4, 2026 | **H2 ChemBERTa scaffold (leak-fixed, complet)** | scaffold | **ChemBERTa scaffold = 0.7867 ± 0.0338 (25 fold×seed)** vs **ECFP4-RF 0.8300** → **Δ = −0.0433, p < 0.0001** (paired t, 5 seeds). Transformer < GNN < ECFP4 sous scaffold : **H2 honnête négatif CONFIRMÉ** (aligné "Do Larger Models Really Win"). | `p5_chemberta_scaffold_ckpt.json` (25/25) |
| v3-e | Aug 4, 2026 | **Comparaison inter-projets** | — | **§9bis ajouté** : P5 vs P3 (sanity ECFP4 0.9433 ≈ P3 0.9475 → comparaison valide ; fusion topologique n'inverse pas les fingerprints ; P5 = contrôle honnête de P3) et **P5 vs P4** (même pattern honest-negative génération/prédiction ; H3 salience = bridge vers oracles P4 RRS/PNS ; candidats Pareto P4 re-scorables par ECFP4-RF). | `P5_DATA_ANALYSIS_REPORT.md` §9bis |
| v3-f | Aug 4, 2026 | **Journal cible + gaps/novelty (web)** | — | **Cible : Journal of Cheminformatics** (Springer, axe éditorial "publishing benchmark studies for ML", collection "Evaluating AI/ML in cheminformatics", précédent direct Boldini 2024 fingerprints NPs). Recherche web SOTA : **Guo & Ding 2026 "Do Larger Models Really Win" (arXiv:2604.26498)** — 156 comparaisons, classiques ML gagnent 47.4%, séquence 28.8%, GNN 21.8%, LLM-SAR 1.9% ; **Benchmarking Pretrained Embeddings (arXiv:2508.06199)** — 25 modèles ≈ ECFP, seul CLAMP gagne ; Boldini 2024 (fingerprints NPs). → **P5 = extension directe de ces 3 références sur panel NPs africaines + contribution interprétabilité (H3)**. Figures/tables de perspective listées (§9bis). | §9bis + web 04/08 |
| v3 | Aug 4, 2026 | **GIN prod (M1.3)** | random + scaffold 5-fold × 5 seeds | **GIN random = 0.9098 ± 0.0067**, **GIN scaffold = 0.8047 ± 0.0395**, **GIN-TFP scaffold = 0.8137 ± 0.0300**, **GIN-TNE scaffold = 0.8068 ± 0.0366** (25 fold×seed chacun). Fix sbatch (chemin, `--dry-run`, mem, conda inline) + fix fusion numpy→tensor + fix collate flat desc. | `results/p5_{GIN,GIN-TFP,GIN-TNE}_scaffold_ckpt.json` + CSVs |
| v3-g | Aug 5, 2026 | **H2 ChemBERTa random (leak-fixed, complet)** | random | **ChemBERTa random = 0.9121 ± 0.0047 (25 fold×seed)** — au-dessus du GIN random (0.9098), sous ECFP4-RF (0.9433, Δ=−0.031). Transformer < fingerprints sous random (attendu, cf. "Do Larger Models Really Win"), mais **meilleur que GIN** à variance moindre (std 0.0047 vs 0.0067). Hiérarchie P5 complète : ECFP4 0.9433 > ChemBERTa 0.9121 > GIN 0.9098 (random) ; ECFP4 0.8300 > GIN-TFP 0.8138 > GIN-TNE 0.8090 > GIN 0.8047 > ChemBERTa 0.7867 (scaffold). | `p5_chemberta_random_ckpt.json` + CSV (25/25, job 12815) |

### v3 (Aug 4, 2026) — GIN production run (M1.3) ✅ LOGGED-BEFORE-RUN
- **Instrument fix déjà appliqué** (v2) : `self.folds` l.114, dry-run ne sauvegarde plus ckpt/CSV.
- **Fix sbatch wrapper** (celui-ci était encore pollué) : `p5_benchmark.sbatch` pointait vers `s_products/p5_benchmark.py` (inexistant) et passait **`--dry-run` en dur** → un sbatch naïf aurait re-lancé des dummy AUC=0.5. Corrigé : `scripts/p5_benchmark.py`, suppression du `--dry-run`, virgule manquante dans le JSON `metadata.json` (`batch_size`).
- **Bug `$RUN_CMD` corrigé (3 itérations)** : la chaîne composée `source && conda activate && python` stockée dans une variable puis exécutée non quotée ne re-parse pas `&&` → conda activait mais avalait les args python (ArgumentError) ou `source` silencieux (stdout vide, runtime 0 s). Fix définitif : **activation conda inline dans le corps du script** (`source … ; conda activate …; python …`), testé exit=0 en dry-run. `--mem=0` bloquait aussi (MaxMemPerLimit) → `--mem=80G` (125 GB nœud).
- **GIN random (bar, job 12800) : AUC = 0.9098 ± 0.0067** (25 fold×seed, EPOCHS=50/PATIENCE=10, GPU A4000, ~7 min). En-dessous de ECFP4 0.9475 → attendu/honnête (cf. "Do Larger Models Really Win?", random split classique domine).
- **Gate H1 (barre scaffold + fusion) :** sbatch étendu à `SPLIT=${2:-random}` → lancement GIN-scaffold (barre) + GIN-TFP + GIN-TNE (arms fusion, scaffold = primary line). GIN-TFP/TNE sont les modèles de fusion topologique du design v2.
- **GIN scaffold (job 12801) : AUC = 0.8047 ± 0.0395** (25 fold×seed) — la barre GNN chute de 0.910 (random) à 0.805 (scaffold), comme attendu. La barre de comparaison H1 = ECFP4 sous scaffold.
- **Bug fusion corrigé (jobs 12802/12803)** : `self.desc` (torch.FloatTensor) ← `_load_tfp()/_load_tne()/_load_ecfp4()` retournaient numpy → `TypeError: can't assign numpy to FloatTensor`. Fix : `torch.from_numpy(...)` aux 6 affectations (GIN-FP/TFP/TNE/Hybrid-All). Vérifié init OK (`GIN-TFP desc (19836,78)`, `GIN-TNE (19836,192)`). Relance des 2 jobs fusion.
- **Bug fusion 2 corrigé (jobs 12804/12805)** : PyG collate `desc` (attribut par graphe [n_desc]) en **flat** [N×n_desc] → `RuntimeError: Tensors must have same number of dimensions: got 2 and 1` (`p5_models.py:58`). Fix : reshape dans `_GraphBase.forward` (`if desc.dim()==1: desc = desc.reshape(h.shape[0], self.n_desc)`). Vérifié forward batch OK (`out (2,1)`). Jobs fusion relancés (12806/12807).
- **Résultats fusion scaffold (jobs 12806/12807) :** GIN-TFP = **0.8137 ± 0.0300**, GIN-TNE = **0.8068 ± 0.0366**. Modeste gain TFP vs bar GIN 0.8047 (+0.009) ; TNE ~plateau. **Verdict H1 en attente de la barre ECFP4-RF scaffold** (job 12808).
- **Verdict H1 — FAIL (barre ECFP4-RF scaffold = 0.8300, job 12808) :** aucune arm GNN ne bat ECFP4-RF sous scaffold. ⚠️ **CORRECTION AUDIT 06/08 : les p-values initiales (GIN 0.051, TFP 0.081, TNE 0.015) provenaient d'un appariement fold-means vs seed-means (misaligné).** Avec la méthode documentée (paired t sur les 5 per-seed means, données déposées actuelles), **les 4 arms sont significativement pires** : GIN −0.0253 (p=0.018), GIN-TFP −0.0162 (p=0.025), GIN-TNE −0.0210 (p=0.038), ChemBERTa −0.0433 (p<0.0001) — tous passent BH-FDR (adj ≤ 0.038). → **honest-négatif plus fort : chaque arm est significativement en dessous des fingerprints.** (ECFP4-RF random = 0.9433, sanity v1 confirmé.) → **Pivot au plan v2 prévu : H2 (honnête négatif) + H3 (interprétabilité)** — aligné exactement sur la revue GenAI 2026 (G1 saturation benchmark, "Do Larger Models Really Win" : classique domine 47.4% sous scaffold). Le manuscrit P5 se positionne en **honest-negative + contribution interprétabilité/topologie**, pas en "GNN > fingerprints".
- **Optimisation ressources HPC (leçon requête)** : le job GPU ne consomme que ~2.3 GB RSS et ~1 cœur réel → `--mem` 80G→**16G**, `cpus-per-task` 32→**8**, `time` 24h→**6h**. Réserve 35× adaptée au besoin → moins de blocage de la file production. Lancer les jobs via **`sbatch`** (l'`nohup` derrière un shell qui timeout ne se détache pas proprement → job tué). Baseline RF en CPU-only (pas de `--gpus`, partition production) job 12808.
- **Pivot H2/H3 lancé (post-H1-FAIL) :** ChemBERTa fine-tune (H2, jobs 12809 random / 12810 scaffold) + re-run fusion avec capture salience (H3, jobs 12811/12812).
- **H3 pipeline (salience) implémenté** : `p5_benchmark.py` → `train_fold` retourne la salience du descripteur = **mean |W| sur colonnes desc de `head.0.weight`** (Linear `[128, 128+n_desc]`), agrégée folds×seeds dans `p5_{model}_{split}_salience.json`. Validé fold 0 GIN-TFP : `(78,)` non-négatifs, AUC 0.8171. Pas de gradients — plateau de la première couche du head. Key `head.0.weight` confirmée (`nn.Sequential(Linear,…)`).
- **ChemBERTa fixés** : `--split scaffold` ajouté (était hardcodé random), dry-run ne pollue plus ckpt/CSV, sbatch dédié `p5_chemberta.sbatch` (8 CPU/16 G). ChemBERTa random fold 0 = 0.9326 vs ECFP4 0.9475 (début, cohérent H2).
- **Cadence estimée** : ChemBERTa ~5-6 min/fold (10 épochs) → ~2 h/split ×2, puis 2 re-runs fusion (~10 min chacun). File : 12809 R → 12810 → 12811 → 12812.
- **⚠️ BUG CRITIQUE — fuite inter-folds ChemBERTa (trouvé 04/08) :** `p5_chemberta.py` chargeait `self.model` **une seule fois** dans `__init__` (`from_pretrained`, l.99) et le réutilisait sur les **25 folds** sans reset. `train_fold` ne réinitialisait que `opt`, pas les poids → **les folds 1–4 héritaient du fine-tune des folds précédents** (fuite de validation croisée). Symptôme : fold 0 = 0.826 (honnête, vrai base pretrained) mais folds 1+ s'envolaient à 0.95–0.99. → résultants "ChemBERTa win" (random 0.981 / scaffold 0.96) **ARTEFACT, pas un résultat réel**. **Fix :** snapshot `self.pretrained_state` à l'init + `load_state_dict(self.pretrained_state)` au début de chaque `train_fold` (folds indépendants). **Validé :** folds 0/1 scaffold post-fix = 0.8247 / 0.7857 (vs 0.826 puis 0.95+ avant), cohérents ECFP4/GNN. Ckpts random+scaffold contaminés **supprimés**, jobs 12809/12810 annulés, relance propre (job 12813). H2 "transformers ≤ GNN" rétabli (léger avantage transformer random reste à confirmer sur run complet fixé).
- **H3 — Salience des dims TFP/TNE (données 04/08, 25 folds) :** `salience = mean|W|` sur colonnes desc de `head.0.weight` (projection `[128+n_desc→128]`), agrégé fold×seed. **TFP (78 dims) :** groupe **persistent-image (33:58) porte le signal** — salience moy. 0.0790 vs H(0:33) 0.0485 et betti(58:78) 0.0547 ; top-5 dims 42/43/52/53/54 (sal 0.100–0.119). **TNE (192 dims) :** top dims 68/43/92/66/165 (sal 0.096–0.145) ; top-10% des dims = 17.3% de la salience totale (sparsité modérée). → contribution d'interprétabilité (L4) : la géométrie persistante (pers_img) domine la topologie portée par la fusion, cohérente avec le rôle 3D/géométrique (aligné "Do Larger Models Really Win" + agenda RQ5). Bridge P3 H1-RRS : ces dims topologiques sont les candidats à corréler aux scores RRS/PNS.
- **H2 — ChemBERTa scaffold COMPLET (job 12813, leak-fixed, 25 fold×seed) :** **0.7867 ± 0.0338** (folds 0.724–0.836, pas d'inflation — le fix de fuite tient sur les 25 folds). **Vs ECFP4-RF scaffold 0.8300 : Δ = −0.0433, paired t(4) = −18.35, p < 0.0001** (⚠️ CORRECTION AUDIT 06/08 : t(4)=−18.35 et non −29.96 — la valeur antérieure venait de l'appariement misaligné). Hiérarchie scaffold finale : **ECFP4-RF 0.8300 > GIN-TFP 0.8138 > GIN-TNE 0.8090 > GIN 0.8047 > ChemBERTa 0.7867**. Le transformer pré-entraîné n'apporte RIEN sous scaffold — pas même la fusion topologique ne rattrape les fingerprints classiques. **H2 honnête négatif CONFIRMÉ (transformer ≤ GNN ≤ fingerprints)** → narration L3 intacte, doublement soutenue (GNN H1 + transformer H2). Le manuscrit P5 = honest-negative + interprétabilité (H3) + topologie (pers_img), PAS "GNN/transformer > classique".
- **Logs :** `Project5_GNN_Transformer_DrugDiscovery/logs/p5_GIN/stdout_{random,scaffold}.log`

### v3-g (Aug 5, 2026) — H2 ChemBERTa random COMPLET (leak-fixed, job 12815) ✅
- **ChemBERTa random = 0.9121 ± 0.0047 (25 fold×seed)** — variance très faible (std 0.0047, range 0.902–0.921), pas d'inflation inter-folds (le fix v3-a tient). **Vs GIN random 0.9098 ± 0.0067 : Δ = +0.0023 (ns)** ; **vs ECFP4-RF 0.9433 : Δ = −0.0312**. 
- **Hierarchie random finale : ECFP4-RF 0.9433 > ChemBERTa 0.9121 > GIN 0.9098.** Le transformer fine-tuné surclasse légèrement le GNN compact mais reste sous les fingerprints — **H2 random CONFIRMÉ (honnête négatif)** : « plus grand » ≠ « meilleur » sous random split, cohérent avec "Do Larger Models Really Win" (classique ML gagne 47.4 %).
- **Hiérarchie complète P5 (les 6 lignes finales) :**

| Modèle | Random | Scaffold |
|:-------|:------:|:--------:|
| ECFP4-RF (P5 sanity) | **0.9433 ± 0.0002** | **0.8300 ± 0.0023** |
| ChemBERTa | 0.9121 ± 0.0047 | 0.7867 ± 0.0338 |
| GIN | 0.9098 ± 0.0067 | 0.8047 ± 0.0395 |
| GIN-TFP | — | 0.8138 ± 0.0352 |
| GIN-TNE | — | 0.8090 ± 0.0378 |

- **Verdict global P5 verrouillé :** fingerprints (ECFP4-RF) = étalon sur les 2 splits ; GNN compact ≈ transformer à variance moindre ; fusion topologique (GIN-TFP) = gain modeste sous scaffold. **Honest-negative contrôlé + H3 salience (pers_img) = les contributions de P5.** Benchmarks P5 (v1-prep → v3-g) **terminés** — toutes les barres des figures finales sont remplies (ECFP4, GIN, GIN-TFP, GIN-TNE, ChemBERTa × random/scaffold).
- **Logs :** `Project5_GNN_Transformer_DrugDiscovery/logs/p5_ChemBERTa/stdout_random.log` (job 12815)

### v1-prep (Aug 1, 2026) — Panel export + dependencies ✅ DONE
- **Dependencies installed & locked** (see §7): torch 2.13.0+cu130, PyG 2.8.0 (GIN smoke-tested on A4000), transformers 5.14.1, datasets 5.0.1, deepchem 2.8.0. **torchdrug incompatible with Python 3.11 → PyG chosen.** Lock: `Project5_GNN_Transformer_DrugDiscovery/requirements.txt`.
- **Panel export** ✅ `scripts/p5_export_panel.py` → `results/p5_canonical_panel.csv` (19,836 × 272: smiles, activity, tfp_0..77, tne_0..191) via **reusing P3's `load_canonical_panel`** — byte-identical order/labels to P3. TFP enriched = 78 (H=33 + pers_img=25 + betti=20), matching job 12699's "TFP enriched: 78 features". Active=14,721 (74.2 %).
- **Frozen splits** ✅ `scripts/p5_make_splits.py` → `results/p5_splits_{random,scaffold}_5fold_seed{0..4}.npy` + `p5_splits_info.json`. Random: stratified 5-fold; Scaffold: Bemis–Murcko greedy min-max. Validated: no train/val/test overlap, ~20 % val.
- **Sanity gate** ✅ `scripts/p5_sanity_ecfp4_rf.py` → mean ECFP4-RF AUC = **0.9428 ± 0.0031** (fold-0 test 0.9460) vs P3 0.9475, within 0.01 tolerance → PASSED. Pipeline/panel plumbing validated before any GNN run.

---
## Références & Documents Liés
- `AGENTS.md` — P5 section + P5_DATA_ANALYSIS_REPORT as the P5 boussole
- `BMAD_Q1_DATA_ANALYSIS_REPORT.md` — P1–P3 canonical (v51; P3 canonical panel, hybrid 0.8876, classical 0.9475)
- `P4_DATA_ANALYSIS_REPORT.md` — P4 boussole (same split pattern)
- `Project5_GNN_Transformer_DrugDiscovery/` — code, results, manuscript
- Key SOTA: MolGraphBench (arXiv 2602.20573); CardinalGraphFormer (arXiv 2602.02201); BiScale-GTR (arXiv 2604.06336); HimNet (Commun. Chem. 2026); MoleculeFormer (Commun. Biol. 2025); DGT (Nat. Commun. 2026); ChemBERTa-3 (Digital Discovery 2026); "Do Larger Models Really Win?" (2026); DumplingGNN (IJMS 2025); low-data learning-curve benchmark (ChemRxiv 2026)

### Entrées bib préparées pour le manuscrit P5 (prêtes à copier dans le `.bib`)

> **Contexte d'usage P5 :** ces 3 références servent au cadrage (Introduction/Related work) du futur manuscrit P5 — deux **revues** (quantum computing en bioinformatique / drug discovery) pour le contexte NISQ-QML, et **MolPROP** comme preuve de la fusion multimodale GNN+langage (justifie le paradigme GIN + ChemBERTa / fusion de features). Même jeu de clés que `Bibliography_Paper3.bib` (cohérence cross-manuscript) ; les clés `naleczcharkiewicz2024`/`kumar2024quantumdrug`/`rollins2024molprop` sont déjà résolues dans le main P3 (v51).

```bibtex
@article{naleczcharkiewicz2024,
  author  = {Na{\l}ecz-Charkiewicz, Katarzyna and Charkiewicz, Kamil},
  title   = {Quantum Computing in Bioinformatics: A Systematic Review Mapping},
  journal = {Briefings in Bioinformatics},
  year    = {2024},
  volume  = {25},
  number  = {5},
  pages   = {bbae391},
  doi     = {10.1093/bib/bbae391},
}

@article{kumar2024quantumdrug,
  author  = {Kumar, Gautam and Yadav, Sahil and Mukherjee, Aniruddha and Hassija, Vikas and Guizani, Mohsen},
  title   = {Recent Advances in Quantum Computing for Drug Discovery and Development},
  journal = {IEEE Access},
  year    = {2024},
  volume  = {12},
  pages   = {64491--64509},
  doi     = {10.1109/ACCESS.2024.3376408},
}

@article{rollins2024molprop,
  author  = {Rollins, Zachary A. and Cheng, Alan C. and Metwally, Essam},
  title   = {{MolPROP}: Molecular Property Prediction with Multimodal Language and Graph Fusion},
  journal = {Journal of Cheminformatics},
  year    = {2024},
  volume  = {16},
  number  = {1},
  pages   = {56},
  doi     = {10.1186/s13321-024-00846-9},
}
```
