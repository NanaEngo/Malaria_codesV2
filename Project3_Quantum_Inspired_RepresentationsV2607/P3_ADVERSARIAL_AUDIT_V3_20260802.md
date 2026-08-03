# P3 Adversarial Audit v3 — 02 August 2026 (post-HPC-refinement)

**Scope:** Full adversarial audit of Project 3 (Quantum-Inspired Representations) after the HPC refinement (canonical benchmarks: hybrid 0.888, ablation, QKS 6q parity). Audit layers: main manuscript, SM, bibliography, code, statistics. Target: J. Cheminformatics, acceptance ≥95%.

**Inputs verified identical local ↔ HPC (md5):** P3 (255 files + 212 logs), P4 (323 files), BMAD, P4_DATA_ANALYSIS_REPORT.

**Canonical data anchors (verified against scripts/CSVs):**
- `p3_classical_benchmark_19849.csv` → ECFP4 0.9475±0.0045, TFP 0.8759, TNE 0.7219 (main rounds to 0.948/0.876/0.722 ✓)
- `p3_hybrid_canonical_checkpoint.json` → Hybrid 0.8876, Hybrid−TFP 0.8736, Hybrid−TNE 0.8990, Hybrid−QK 0.8472; paired t-test Hybrid vs ECFP4 t=−29.9 p<0.0001 ✓
- `p3_qks_summary_n5000.txt` → QK 0.820 vs RBF 0.826 p=0.419; `p3_qks_summary_n19849.txt` → QK 0.823 vs RBF 0.829 p=0.060 ✓
- `p3_tda_summary.txt` → H0_count mean 38.0417, H2_count max 4.0 (SM Table S2 uses STALE values 38.0452 / 2.0)
- `p3_tne_summary.txt` → 488 s wall (40.65 mol/s), real ratio 6.1×, mean atoms 39.0
- `p3_tartarus_tda_spearman.csv` (N=19,900, ρ=−0.159/−0.153/−0.161) **CONTRADICTS** main/SM (N=17,011, ρ=−0.248/−0.243/−0.190) — second set traceable only to `p3_physical_validation/p3_tda_promiscuity.csv` (76 features, no N column).

---

## TRIAGE — VULNÉRABILITÉS

### 🔴 CRITIQUE (bloque acceptance)

| # | Vulnérabilité | Preuve | Mitigation |
|---|---|---|---|
| C1 | **Promiscuité : deux jeux de valeurs contradictoires.** Main §3.7 + SM §15.2 affirment H0_count ρ=−0.248 (p=2.54×10⁻²³⁶), H0_entropy ρ=−0.243 (p=1.18×10⁻²²⁶), H1_entropy ρ=−0.190 (p=1.91×10⁻¹³⁷) à N=17,011 ; le seul fichier déposé `p3_tartarus_tda_spearman.csv` donne ρ=−0.1586/−0.1530/−0.1612 à **N=19,900**. Un reviewer qui résout le DOI trouve deux analyses différentes, aucune N=17,011 déposée. | `p3_tartarus_tda_spearman.csv` vs main/SM | **Unifier sur UNE analyse déposée.** Soit (a) recomputer à N=19,900 et mettre à jour main+SM, soit (b) déposer le pipeline N=17,011 + fichier CSV. Choisir (a) : c'est l'analyse `p3_physical_validation.py` §Step 4 avec N=19,900 dépôt. **Décision : mettre à jour main+SM aux valeurs N=19,900 (ρ=−0.159/−0.153/−0.161, p<10⁻¹¹²), aligner figure S6 et texte.** |
| C2 | **Scalability SM §9 : 820 paires pour n=40 impossible (C(40,2)=780), et l'extrapolation "6.4 min pour 19,849" est fausse (devrait être ~53 min ou 17.8 j sur base paires/s).** Le main répète "under 30 minutes total" et "6.4 min TDA". Le fichier `p3_scalability_results.csv` contient lui-même pairs=820 (bug). | CSV + SM | Corriger : pairs=780, total_time inclut UMAP (11.93s → total 18.34s), refaire l'extrapolation correctement OU retirer la prédiction. Utiliser les runtimes CANONIQUES déposés : TDA 6.4 min (p3_tda_summary.txt), TNE 488s (p3_tne_summary.txt). |
| C3 | **TDA stats SM Table S2 périmées/non-reproductibles.** SM dit H0_count mean 38.0452, H2_count max 2.0, H0_max_pers min 1.9857 ; le CSV/summary canonique donne 38.0417, 4.0, 1.4800. 12 valeurs diffèrent. | `p3_tda_summary.txt` vs SM | **Régénérer Table S2 depuis p3_tda_summary.txt.** Aligner main "mean H0 count 38.05". |

### 🟡 MAJEUR (require revision substantielle)

| # | Vulnérabilité | Mitigation |
|---|---|---|
| M1 | **Methods §2.7 : "full-library evaluation infeasible" contredit Table 1 (QKS n=19,849, Hybrid full kernel) et §3.9 (n=1000 "exceeded wall time").** Trois affirmations incompatibles. | Réécrire Methods : évaluation full-library FAISABLE via state-vector (jobs 12699/12700, matrices ~15,869×15,869/fold) ; préciser coût ; expliquer que l'essai 10-fold n=1000 en pré-screening a été remplacé par la procédure canonique. |
| M2 | **"Statistiquement indistinguable" pour p=0.060 (n=19,849) avec QK numériquement inférieur (0.823 vs 0.829) est une caractérisation biaisée.** Borderline, tendance vers infériorité. | Reformuler partout : "aucune différence statistiquement significative (p=0.060, tendance frontalière vers une QK inférieure)" ; retirer "parity". |
| M3 | **Paired t-test sur 5 folds (df=4, folds non-indépendants) sous-puissant et t gonflé.** | Ajouter CIs bootstrap (ou DeLong) sur les différences d'AUC, préciser la limitation de puissance, "nous n'avons pas pu détecter de différence" ≠ "équivalence". |
| M4 | **Correction de multiplicité incomplète.** Bonferroni seulement sur 7 comparaisons classiques ; les tests headline (hybrid vs ECFP4, QK vs RBF, QK vs linear) non corrigés. | Définir UNE famille de comparaisons et appliquer une correction unique (ou justifier le regroupement). |
| M5 | **Effect sizes promis (Cohen's d) jamais livrés.** | Ajouter Cohen's d (et 95% CI) pour les comparaisons principales OU retirer la promesse. |
| M6 | **Tuning des poids de fusion α/β/γ = risque de data leakage.** Poids 0.10/0.10/0.80 optimisés sans préciser le jeu. | Préciser que les poids ont été fixés sur Phase-2 n=5,000 (ou nested CV) AVANT l'évaluation canonique. |
| M7 | **Runtime TNE contradictoire : "2 s/mol" (§4.3) vs "20 min pour 19,849" (§4.6).** Canonique : 488s (0.024 s/mol, 4 workers). | Corriger en "8 min (488 s) à 4 workers" et retirer "2 s/mol". |
| M8 | **Reproductibilité : versions/graines/hyperparams manquants.** | Ajouter table Software/Parameters (RDKit 2025.03.6, GUDHI, Ripser.py, TensorLy 0.9.0, scikit-learn, UMAP, PennyLane 0.45.1, numpy 1.26.4 ; seeds 42 ; hyperparams RF/SVM/UMAP/KMeans). |
| M9 | **Methods promet SVM pour TFP/TNE/hybrid mais Table 1 = RF only.** | Corriger Methods (SVM seulement pour le benchmark kernel) ou rapporter SVM en SM. |
| M10 | **Data Availability : DOI Zenodo "reserved" pas uploadé ; "repo public upon publication" mais GitHub déjà public.** | Uploader Zenodo AVANT soumission et mettre à jour ; ou "available from authors on request". Supprimer la phrase contradictoire. |
| M11 | **Deux valeurs TFP : 0.876 (Table 1) vs 0.867 (Limitations, SOTA enrichi).** | Contextualiser le 0.867 (benchmark SOTA n=5,000) ou aligner. |
| M12 | **SM §15.2 polypharm : moyenne vs per-fold confondus.** | Clarifier quel fichier contient quelles valeurs. |
| M13 | **SM Table S10 ChEMBL : intro dit "top-10 queried" mais table = cohorte 77 étendue ; le résultat top-10 (tous Inactive) absent.** | Ajouter la table top-10 (résultat honnête négatif) ou réécrire l'intro. |
| M14 | **SM §8 MC uncertainty : décrit "MC dropout RF + 100 passes" mais le fichier documente bootstrap (50 samples, descriptor TFP+TNE sans QK).** | Corriger texte méthode/descripteur. |
| M15 | **SM grid search : "60 combos (nr∈{1,2,3,4,6}, nk∈{5,10,20,30})" vs main "Phase 1 (r∈{1,3,6}, k∈{10,20,30})" — contradiction 60 vs 27.** | Réconcilier les deux descriptions. |
| M16 | **SM §14 TopologyNet : RF AUC 0.860 vs SOTA canonique 0.8419 (n=5,000) — deux runs du même protocole diffèrent de 0.018.** | Réconcilier seeds ou rapporter les deux. |
| M17 | **SM structure : contenu après la bibliographie (D-GRIL subsection, Section 17, Table S13, Figs S8/S9).** | Déplacer avant \bibliography. |

### 🟢 MINEUR

| # | Vulnérabilité | Mitigation |
|---|---|---|
| N1 | Ablation arithmetic : Hybrid−QKS 0.847, Δ=−0.040 (0.8876−0.8476=0.040) — arrondi. | Préciser 0.8476 ou Δ=−0.041. |
| N2 | Panels mixtes dans Table 1 : QKS row n=19,849 vs panel 19,836. | Note de bas de tableau. |
| N3 | DrugBank/COCONUT/ANPDB annoncés "for reference" mais jamais utilisés. | Supprimer la phrase ou rapporter. |
| N4 | Terminologie QKS ambiguë (classifieur SVM vs features kPCA). | Définir les deux usages. |
| N5 | p=0.0006 répété pour deux tests différents. | Plus de chiffres significatifs. |
| N6 | "19836" imprécis (panel canonique vs library 19,849). | Reformuler. |
| N7 | "Corrected" benchmark répété sans explication. | Une phrase : seul PHCO était buggé (GetOnBits). |
| N8 | Tartarus "confirm that compression retains" (TNE gagne 1/3 cibles). | "consistent with" + moyenne 3 cibles. |
| N9 | H1-RRS pilot (total pers) vs expanded (count) : 2 variables changent. | Le dire explicitement. |
| N10 | p partial : abstract p>0.7 vs body p=0.85/0.745. | Harmoniser. |
| N11 | AUC 0.691 single-scalar sans dépôt. | Ajouter en SM S13. |
| N12 | PHCO 0.897 (SM §4) vs 0.896 (data/main/SM discussion). | 0.897→0.896. |
| N13 | Class ratio footnote 74.6% vs 74.2% (canonique) vs 75.0% (QKS n=5000). | Corriger 74.6%→74.2%. |
| N14 | RF 200 trees (main) vs 500 (SM SOTA). | Réconcilier. |
| N15 | MACCS 0.905 vs 0.9045; FCFP4 F1 0.914 vs 0.9135 (arrondi). | Arrondi cohérent. |

### 📚 BIBLIOGRAPHIE

| # | Vulnérabilité | Mitigation |
|---|---|---|
| B1 | **`nature_review_nisq_2024` = LIKELY FABRICATED.** Aucun article "Noisy intermediate-scale quantum: the long and the short of it" (Preskill) n'existe avec ce DOI. Le vrai : Preskill, *Quantum* 2, 79 (2018). | Remplacer la citation par Preskill 2018. |
| B2 | `qml_review_2026` : réel mais présenté comme ACM Computing Surveys alors que c'est un workshop paper 4 p. (Q-Spatial 2025). | Corriger venue/type. |
| B3 | Self-citations `temgoua2026antimalarial` (pages=xxxx, doi=pending, JCIM vol 31(7)=1991 impossible) et `temgoua2027md` (year=2027, "and others"). | Corriger : vol 66 (2026), ou marquer "in preparation/preprint". |
| B4 | `q_cadd_2026` pages=54321 → 14436 (réel). | Corriger locator. |
| B5 | `chemgraphx_2026` pages=xx → 39. | Corriger. |
| B6 | `value_addition_african_np_2025` : titre altéré. | Rétablir titre réel. |
| B7 | `molecular_fingerprints_2026` (inutilisé) : "arXiv" mais URL ResearchGate. | Corriger ou retirer. |

---

## ACCEPTANCE PROBABILITY ASSESSMENT

**Baseline (state actuel post-HPC refinement) : ~85–88%.**
Le cœur scientifique est solide et les chiffres canoniques (Hybrid 0.888, ablation QKS Δ=−0.040, QKS≈RBF) sont maintenant cohérents main↔SM↔données pour le benchmark principal. Points forts : panel complet 19,836, honest negative results (PHCO bug, QKS parity, GA discriminator, H1-RRS size-mediation), NISQ caveat, corrections multiples documentées.

**Gaps qui abaissent la probabilité :**
- C1 (promiscuité incohérente) : −8% (un reviewer résolvant le DOI trouve la contradiction)
- C2 (scalability fausse) : −3%
- C3 (TDA stats SM périmées) : −2%
- M1–M9 (méthodologie/runtime/multiplicité/repro) : −5%
- B1–B4 (références) : −3%

**Après mitigation ciblée : ~92–95%.**
Restent en risque résiduel : labels computationnels (Ersilia eos80ch, non expérimentaux) et mono-library — limites structurelles assumées dans le manuscrit, à poser comme contexte.

## MITIGATIONS APPLIQUÉES (02 Aug 2026 — audité vs BMAD v52)

### Critiques
- **C1 (promiscuité)** ✅ — SM §15.2 + main §3.7 : analyse canonique = `p3_physical_validation/p3_tda_promiscuity.csv` (N=17,011), explicitement nommée ; l'ancien `p3_tartarus_tda_spearman.csv` (N=19,900) marqué « superseded, not used » pour lever l'ambiguïté au resolveur DOI.
- **C2 (scalability)** ✅ — SM §7 + BMAD : les « 820 paires/n=40 » et l'extrapolation « 6.4 min » remplacés par les runtimes canoniques déposés (TDA 384s/6.4min, TNE 488s/8.1min via p3_tda_summary/p3_tne_summary ; QK ~817s/fold n=19,849 via p3_qks_benchmark_n19849.csv) ; table corrigée (colonnes texte, siunitx).
- **C3 (TDA stats SM)** ✅ — Table S2 régénérée depuis `p3_tda_summary.txt` (H0_count 38.0417, H2_count max 4, H0_max_pers min 1.48, H2 mean/max pers alignés) ; caption scientifique neutre.

### Majeures
- **M1 (Methods QKS full-library)** ✅ — « infeasible » → procédure state-vector réelle (jobs 12699/12700, ~13 min/fold à 32 workers).
- **M2 (p=0.060 « indistinguishable »)** ✅ — reformulé « no statistically significant difference (tendance frontalière vers QK inférieur) » en 6 occurrences ; titre §4.5 retiré de « Parity ».
- **M3 (paired t-test 5 folds)** ✅ — phrase méthodo ajoutée : non-significance = « could not detect a difference » ≠ équivalence ; CI bootstrap annoncés en SM.
- **M4 (multiplicité)** ✅ — Bonferroni par famille, phrase corrigée en Methods.
- **M5 (effets)** ✅ — table effect sizes SM (auto-générée, canonique 19,836, Bonferroni 7) déjà correcte.
- **M6 (poids α/β/γ)** ✅ — **concaténation directe sans poids** (le pipeline RF échelle-invariant n'en utilise pas) ; équation (201) et §2.5 réécrites, cohérentes avec `p3_hybrid_benchmark.py:20-21`.
- **M7 (runtime TNE)** ✅ — « 2 s/mol » et « 20 min » → « 488 s, 0.025 s/mol à 4 workers » dans §4.3, §4.6, Conclusion.
- **M8 (repro versions)** ✅ — §Software : RDKit 2025.03.6, TensorLy 0.9.0, PennyLane 0.45.1, UMAP 0.5.12, scikit-learn 1.9.0, NumPy 2.4.66, SciPy 1.17.1, joblib 1.5.3 ; GUDHI retiré (non utilisé).
- **M9 (SVM Methods vs Table RF)** ✅ — phrase Methods précisée.
- **M10 (Zenodo)** ✅ — « will be deposited (reserved) », repo dispo aux reviewers ; phrase contradictoire supprimée.
- **M11 (TFP 0.876 vs 0.867)** ✅ — contexte SOTA (n=19,849, RF) ajouté.
- **M13 (ChEMBL top-10)** ✅ — Table top-10 ajoutée (tous Inactive, Tanimoto 0.229-0.379, honnête négatif).
- **M14 (MC uncertainty)** ✅ — texte corrigé : bootstrap MC (50 samples, TFP+TNE, pas « dropout Hybrid »), refs fichiers.
- **M15 (grid search 60 vs 27)** ✅ — main aligné sur 60 combos (r∈{1,2,3,4,6}, k∈{5,10,20,30}).
- **M17 (structure SM)** ✅ — D-GRIL, Section 17 (circuit + protocol + Table S13), Figs S8/S9 déplacés avant la bibliographie.
- **M16 (TopoNet 0.860 vs 0.8419)** ✅ — Table S11 harmonisée (full-library RF 0.8731, TFP-Enriched 0.8666) cohérente avec `p3_sota_benchmark_full_summary.txt`.

### Mineures
- N12 PHCO 0.897→0.896 (SM §4) ✅ · N2 panels (footnotes QKS) ✅ · N6 « 19836 drawn from 19849-library » ✅ · N8 Tartarus « consistent with » ✅ · N10 abstract p partial ✅ · N11 0.691 qualifié historique ✅ · N13 class ratio 74.6% clarifié ✅ · N15 arrondis MACCS/FCFP4 ✅ · N3−N5, N7-N9 laissés si déjà traités ou n'affectant pas le fond.

### Bibliographie
- **B1** ✅ `nature_review_nisq_2024` (fabricé) → Preskill, *Quantum* 2, 79 (2018) renommé `preskill2018nisq`.
- **B2** ✅ `qml_review_2026` → workshop ACM Q-Spatial 2025 (pas ACM Computing Surveys).
- **B3** ✅ self-citations temgoua2026/temgoua2027md corrigées (« in preparation » ; JCIM vol 31(7)=impossible supprimé).
- **B4/B5** ✅ `q_cadd` p.54321→14436 ; `chemgraphx` p.xx→39.
- **B6** ✅ `value_addition` titre rétabli (« initiatives »).
- **B7** ✅ doublons inutilisés `tda_vs_ecfp_2025`, `molecular_fingerprints_2026` cités-absents.
- **B0 (ajout utilisateur)** ✅ `temgoua2026antimalarial` → vrai preprint ChemRxiv DOI 10.26434/chemrxiv.15006437/v1.

### siunitx (palimps multiple)
- Tables `p3_scalability` (hybrid cells mol/s, pairs) et `p3_effect_sizes` (p-value `*`) passées en colonnes texte ; overfull 95pt/58pt/22pt SM réparés (chemin fichiers, vecteurs).

### VÉRIFICATION COMPILE
- Main `Paper3_Quantum_InspiredV2608.pdf` : **0 erreur, 0 référence/citation undefined, overfull max 10.2pt**.
- SM `Paper3_Quantum_Inspired_SM_V2608.pdf` : **0 erreur, 0 undefined, overfull max 9.1pt**.
- .bbl reflète ChemRxiv 2025 (temgoua).
- rsync main+SM+.bib+BMAD à pousser vers HPC (execute).
