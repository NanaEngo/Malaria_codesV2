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

## 10. Version History
| Version | Date | Models | Split | Result summary | Files |
|:-------:|:-----|:-------|:------|:---------------|:------|
| v1 | Aug 1, 2026 | (planned) | random 5-fold | pending | — |
| v2 | Aug 4, 2026 | design restart (gaps/novelty) | — | Design relancé sur gaps revue GenAI 2026 (`P5_DESIGN_GAPS_NOVELTY.md`) + fix instrument de mesure | fix `self.folds` (`p5_benchmark.py:114`), dry-run ne pollue plus ckpt/CSV, résultats GIN dummy AUC=0.5 supprimés |

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
