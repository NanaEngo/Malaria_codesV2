# P5 — Design relancé : Gaps & Novelty (ancre : revue GenAI 2026)

**Version:** v2 (04/08/2026) — **refonte complète** du design, pilotée par les gaps
de la revue *Karim et al. (2026), "Generative AI in Bioinformatics: A Systematic
Review", Arch. Computat. Methods Eng.* — https://doi.org/10.1007/s11831-026-10743-z
**Boussole données :** `P5_DATA_ANALYSIS_REPORT.md` (panel/splits figés)

> Cette refonte part des **gaps explicites que la revue identifie dans la
> littérature GenAI-bioinfo** et en fait la colonne vertébrale de la thèse P5.
> Le design v1 (PA90) risquait « yet another benchmark » ; le v2 retourne cela :
> P5 est **le benchmark anti-saturation**, fondé sur l'évaluation hors-distribution
> et la fusion topologique multi-modale, dans un espace chimique sous-représenté.

---

## 1. Les gaps de la littérature (revue 2026) → leviers P5

| # | Gap identifié par la revue (KS2026, §RQs) | Citation clé | Levier P5 qui le comble |
|:-:|:------------------------------------------|:-------------|:------------------------|
| G1 | **Saturation des benchmarks** — CAFA3, scGPT convergent (~84 %), « limited practical separation despite architectural differences » (§4.5.4) | §4.5.4 | Benchmark sur panel unique **figé** (comparabilité) + **split scaffold** = séparation mesurable, pas une hiérarchie de AUC saturées |
| G2 | **« Larger is better » remis en cause** — déplacement vers compute-optimal, PEFT (LoRA), modèles compacts (§4.5.10) | « moving away from the assumption that larger models always perform better » | Thèse centrale : **GNN compacts (A4000, respiration) vs transformer lourds** — prédiction chiffrée, pas un dogme |
| G3 | **In-distribution évalue mal l'utilité réelle** — scGPT zéro-shot degrade, BixBench : FMs faibles en tâches multi-étapes malgré bench (§4.5.7) | « out-of-distribution and prospective evaluations remain limited » | Évaluation **scaffold-split OOD** comme ligne principale + courbes d'apprentissage |
| G4 | **Représentation « simple chaîne »** — DNA/RNA/protraités en strings 1D, ignorant structure/contexte (§4.5.6) | « sequence simplicity » | Fusion **graphe + topologie (TFP, degré de simplicité 0) + tenseur (TNE)** = au-delà de la string, multi-modale |
| G5 | **Interprétabilité/incertitude** — « generate interpretable latent features » ; gap vers le clinique (§4.5.8, agenda RQ5) | « transparent GenAI models that generate interpretable latent features » | Attribution/attention : **quelles dims TFP/TNE portent le signal** (pont P3 §H1-RRS) |
| G6 | **Biais de données** — ChEMBL/UniProt sur-représente kinases/CNS et organismes bien étudiés (§4.6) | « underrepresented organisms and compound classes » | Espace **produits-naturels antipaludiques africains** (P1/P3) = classes composés **vraiment sous-représentées**, avec ancrage biologique P2 (RRS/PNS) |
| G7 | **Plausibilité computationnelle ≠ validation expérimentale** (§4.5.9) | « multi-layered validation … in silico, held-out, experimental, prospective » | Ancrer sur les **oracles biologiques P2/P3** (RRS, PNS, docking Tartarus) comme étage de validation |

---

## 2. Thèse (v2, écrite sur les gaps)

> *« Sur un panel antipaludique de produits-naturels africains (n = 19,836, espace
> chimique sous-représenté — G6), les GNN compacts avec fusion de descripteurs
> topologiques (TDA/TFP, TNE) résistent à l'évaluation hors-distribution (split
> scaffold — G3) là où les transformers ne montrent aucun "free lunch" (G2),
> et l'attribution attentionnelle révèle quelles topologies portent le signal (G5).
> Le benchmark est volontairement anti-saturation (G1) : panel figé, splits figés,
> bar classique ECFP4, accordé à la validation biologique inter-projets (G7). »*

**Différenciateur unique (ce qu'aucun article de la revue ne couvre) :**
la **combinatoire** GNN-compact + fusion topologique(TFP/TNE) + évaluation
hors-distribution + espace NP antipaludique + ancrage biologique. Chaque pierre
seule est banale ; l'articulation n'apparaît dans aucun des 82 articles revus.

---

## 3. Newness sposition vs 82 articles revus (KS2026)

La revue couvre (Table 2/3 des 82 études) : modèles de séquence (DNABERT, ESM,
scGPT), design de protéines (ProtGPT2, RFdiffusion), multi-omics, agents LLM.
**Aucune** des 82 catégories ne traite notre objet :
- predication d'**activité antiplasmodiale** sur un **panel NP africain** (P1),
- par **fusion GNN + persistance homologique (TFP) + réseau de tenseurs (TNE)**,
- évaluée **scaffold-split** contre un bar classique dans le **même protocole que
  le benchmark quantique/classique P3** (comparabilité inter-projets directe).

La revue se clôt sur **trois priorités futures** (§4.5.10) que P5 implémente
explicitement : (i) **architecture modulaire** → fusion de features + chemins
séparables ; (ii) **efficacité compute / « larger n'est pas mieux »** → = notre
thèse ; (iii) **intégration multi-modale de connaissances biologiques** → TFP/TNE
+ oracles biologiques. P5 est donc une **exécution empirique de l'agenda RQ5** de
la revue, dans un domaine (NP antipaludiques) qu'elle ne traite pas.

---

## 4. Question de conception (les vraies hypothèses à trancher)

Pas « quel modèle gagne » (saturable) mais **trois hypothèses testables** alignées
gaps :

- **H1 (G2+G3) :** sous **scaffold split**, un GNN compact + fusion topologique
  maintient son AUC là où ECFP4 s'effondre, et dépasse ECFP4 (DeLong p<0.05, BH).
  → **Le critère de nouveauté centrale.** Random-split seul ne suffit pas.
- **H2 (G2) :** ChemBERTa fine-tuné (transformer) ≤ GNN compact sur ce panel à
  n≈2×10⁴ → honest negative « transformers ≠ free lunch », agendé comme
  conclusion d'échelle, pas un échec.
- **H3 (G5) :** l'attribution attentionnelle isole un sous-ensemble de dims
  TFP/TNE corrélées au signal (pont version P3 H1-RRS) → contribution
  d'interprétabilité, pas un headblind concat.

Gate : si H1 échoue (pas de win scaffold), basculer sur H2+H3 (honest negative +
interprétabilité), thèse toujours soumissible — cf. « Do Larger Models Really
Win? » (Deng et al. 2023), que la revue cite comme precedent accepté.

---

## 5. Design expérimental (reset)

**Panel & splits** (inchangés, figés — v1-prep ✅, réutilise le protocole P3) :
- Panel canonique `p5_canonical_panel.csv` (19,836 × 272), bar ECFP4-RF 0.9428±0.0031 ✓
- Splits figés random + **scaffold** 5-fold × 5 seeds (`p5_splits_*.npy`) ✓

**Modèles (v2, resserrés sur la thèse) :**
| Modèle | Type | Rôle vs gap |
|:-------|:-----|:------------|
| ECFP4-RF | classique | bar (G3) |
| GIN / GCN / GAT | GNN compact | l'égard de G2 (compact, A4000) |
| GIN+TFP / GIN+TNE | GNN + topologie/tensor | **fusion multi-modale (G4) — contribution** |
| GIN+TFP+TNE | fusion complète | ligne principale de H1 |
| ChemBERTa (fine-tune) | transformer | l'égal de H2 (honest negative) |

**Protocole (ligne anti-saturation, G1/G3) :**
1. Split **random** (sanity/reproductibilité P3) — reporté, PAS le headline.
2. Split **scaffold** = ligne primaire de H1 (OOD : G3).
3. 5 folds × ≥5 seeds, DeLong paired + BH FDR vs ECFP4 et vs mutualité.
4. Courbes d'apprentissage N = 500 → 19,836 (régime basse données, G3).
5. Attribution attention : salience dims TFP/TNE (H3, pont P3 H1-RRS).

**Critères de rejet (honnêteté, G7) :** ne survivent au manuscrit que les AUC sur
splits figés, seeds répétées, avec effect-size et test statistique — pas de dry-run
ni de résultat chance (voir §7).

---

## 6. Gaps résiduels assumés (transparence, façon P3)

- Labels d'activité = prédictions Ersilia (eos80ch), pas IC₅₀ expérimentale → ancrage
  biologique via oracles P2/P3 (docking, RRS, PNS), caveat explicite (G7).
- Single-library NP africaine → sous-représentation assumée ET revendiquée comme
  originalité (G6), avec calibration interne (cf. P3).
- A4000 GPU plus lent que CPU pour opérations paires → GPU réservé aux batch denses,
  record GPU-vs-CPU (P3 lesson).

---

## 7. Prérequis bloquant — instrument de mesure (bug critique)

La refonte inclut un correctif de **fiabilité de la mesure**, sans quoi tout le
design est invalide :

- ❌ **Résultats GIN corrompus commités** : `results/p5_GIN_random_{ckpt,results}.csv`
  sont des valeurs **AUC=0.5** = dummy de `--dry-run` (`p5_benchmark.py:266`), 
  marquées « completed » → un vrai run les saiterait. → **supprimer + jamais
  écrire de résultats en dry-run.**
- ❌ **Bug `self.folds`** : `train_fold` lit `self.folds` (`:180`) mais `_load_splits`
  écrit `self.splits` (`:114`) → AttributeError au premier époch réel. → fixer.

Ces deux points sont dans `P5_DATA_ANALYSIS_REPORT.md` §9 (checklist GPU-vs-CPU
encore `[ ]`) et doivent passer en vedette du milestone M1 avant toute AUC publiée.

---

## 8. Définition de la PA (revue 2026 → levier)

| # | Levier (gaps) | Poids | Statut |
|:-:|:--------------|:-----:|:------:|
| L1 | Panel/splits figés + bar (G1) | +20 | ✅ |
| L2 | Win scaffold-split fusion topo (H1, G3/G4) | +30 | ⏳ |
| L3 | Honest negative transformer (H2, G2) | +15 | ⏳ |
| L4 | Interprétabilité / attribution (H3, G5) | +15 | ⏳ |
| L5 | Anchor biologique (G7) + Zenodo | +10 | ⏳ |
| L6 | Narration « agenda RQ5 de la revue » (positionnement) | +5 | 📝 |
| | **Total** | **~95** | |

**Le vrai différentiateur de PA :** la revue 2026 vient de *documenter* G2–G4
comme gaps ouverts. **Soummettre après une revue systématique qui appelle ces
priorités = positionnement opportuniste et légitime.** P5 se présente comme
l'implémentation empirique de l'agenda RQ5, sur un panel que la revue ne couvre pas.

---

*Relancé : 04/08/2026 — ancre littérature : Karim, W., et al. (2026). Generative
AI in Bioinformatics: A Systematic Review of Models, Applications, and
Methodological Advances. Archives of Computational Methods in Engineering.
https://doi.org/10.1007/s11831-026-10743-z*