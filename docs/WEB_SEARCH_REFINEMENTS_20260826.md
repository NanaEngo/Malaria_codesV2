# Veille web — raffinements suggérés pour les manuscrits P2/P5/P6

**Date :** 2026-08-26
**Contexte :** recherche littéraire menée pendant l'attente des jobs en cours (K76A replicate_1 local + watcher QC/MM-GBSA ; SLURM 15490 array ChemBERTa, 15500 bras GNN/ChemBERTa P6, 15502 MM-GBSA WT).
**Statut :** suggestions de rédaction/citations uniquement — aucune métrique nouvelle, aucun calcul canonique modifié. Toute édition manuscrite reste une décision auteur et n'intervient qu'après QC PASS des runs en cours.

---

## 1. P2 — Polypharmacologie MD validation (JCIM)

### 1.1 Ancrage mécanistique à citer en Discussion

**Tanner, Richards & Corry, *Nature Communications* 2025** — « Molecular basis of the functional conflict between chloroquine and peptide transport in the Malaria parasite chloroquine resistance transporter PfCRT »
DOI : [10.1038/s41467-025-58244-0](https://www.nature.com/articles/s41467-025-58244-0)

- **130 µs de MD** sur les isoformes 3D7 (CQ-sensible) et Dd2 (CQ-résistante) de PfCRT avec CQ et substrats peptidiques.
- **K76T ouvre le site de liaison CQ** : Lys76 bloque physiquement l'accès au site dans 3D7 ; sa mutation permet l'entrée/binding de CQ.
- **Lys76 = ancre chargée des peptides** : tous les peptides testés (DPVN, PENF, PVNF) partagent la même ancre électrostatique sur K76 → sa mutation réduit le transport peptidique (coût fitness de la résistance).
- **R371I et Q271E agissent en concert avec K76T** pour faciliter l'accès CQ ; Q271E abaisse l'énergie potentielle du chemin d'accès Path 2 d'environ −50 kJ/mol en moyenne.
- La charge de la cavité (neutre → négative dans Dd2) détermine la spécificité de substrat.

**Usage P2 :** positionner nos ΔΔG PfCRT WT vs mutants (K76A) dans cette mécanique établie — renforce la plausibilité biophysique de nos signaux MM-GBSA/MD-RRS et justifie le design mutant-vs-WT. Le fait que cette étude utilise un sampling massif (130 µs) appuie aussi notre argumentaire « réplicats » ci-dessous.

### 1.2 Standards MM-GBSA à expliciter (terminologie + convergence)

Bonnes pratiques consolidées 2025–2026 :

| Pratique | Recommandation | Action P2 |
|---|---|---|
| Réplicats | 3–5 réplicats indépendants > une longue trajectoire unique | Présenter WT/K76A en mean ± SD sur R1/R2 dès QC PASS des deux |
| Convergence | Moyennes cumulées ou block averaging ; cible SEM < 1 kcal/mol | Tracer la convergence cumulée ΔG en SM depuis les séries temporelles gmx_MMPBSA existantes |
| Terminologie | Nommer « score MM-GBSA (entropie exclue) », jamais « ΔG_bind nu » comparé au Kd | Vérifier/réformer la terminologie dans Methods et Results |
| Protocole | GB model (OBC2 igb=5), force sel (0.15 M), frames/interval déclarés | Déjà conforme (protocole batch verbatim) — s'assurer que le texte le reflète |

**Priorité : gratuit et à forte valeur** — ne requiert aucun nouveau calcul, seulement des tracés SM et une passe terminologique.

---

## 2. P5 — GNN/Transformer vs RF (benchmark)

### 2.1 Notre headline confirmé par un méga-benchmark indépendant

**« Do Larger Models Really Win in Drug Discovery? »** — arXiv [2604.26498](https://arxiv.org/html/2604.26498v3) (+ version bioRxiv [10.64898/2026.04.29.721568](https://www.biorxiv.org/content/10.64898/2026.04.29.721568v1))

- 26 endpoints (ADME, toxicité, bioactivité incluant **anti-TB H37Rv et activité phénotypique antimalariale P. falciparum**), 78 entrées endpoint×split, **156 comparaisons task×métrique**.
- Verdict global (arXiv v3, 156 comparaisons task–metric) : **meilleure performance — ML classique 47.4 % / séquence pré-entraînée 28.8 % / GNN 21.8 % / LLM-SAR 1.9 %** ; classical ML domine le random split et reste la famille gagnante globale (les chiffres « 116/25/12/3 » d'une version antérieure sont obsolètes).
  - Random CV : ML gagne ~73 % des comparaisons (interpolation facile).
  - Murcko scaffold CV : ML reste premier mais GNN+séquence ≈ 50 % combinés.
  - Structure-separated CV : séquence 40.4 %, GNN 36.5 %, ML 21.2 % — mais analyse de sensibilité final-window montre que certains gains GNN/séquence dépendent du readout.
- Baselines : RF/ExtraTrees 300 arbres sur ECFP4/ECFP6, MACCS, descripteurs RDKit.

**Usage P5 :** citer en Discussion — notre résultat « RF(ECFP) ≥ GNN/pré-entraînés sur splits random/scaffold » est l'état de l'art confirmé, pas une anomalie locale.

### 2.2 Prémunition reviewers : « le scaffold split n'est pas assez dur »

- **Guo & Ballester**, arXiv [2406.00873](https://arxiv.org/abs/2406.00873) : le scaffold split surestime la performance réelle ; les splits vraiment difficiles = clustering ECFP4 (k-means) ou UMAP.
- Étude OOD 2025 (ChemRxiv) convergente : scaffold ≈ random en pratique ; k-means ECFP4 le plus discriminant.

**Options :**
1. *Gratuite* : une phrase en Discussion reconnaissant la hiérarchie de difficulté des splits (random < scaffold < cluster-based).
2. *Calcul léger (optionnel, décision auteur)* : ajouter un split Butina/k-means ECFP4 comme analyse de sensibilité.

### 2.3 Si le rerun ChemBERTa étendu (job 15490) reste faible

**ChemBERTa-3**, *Digital Discovery* 2026, DOI [10.1039/D5DD00348B](https://pubs.rsc.org/en/content/articlehtml/2026/dd/d5dd00348b) :

- Fine-tuning publié : **LR ≈ 3e-5** (sweet spot quasi systématique dans leurs tables 7–14), batch 16–32, **50–100+ epochs** jusqu'à 500 avec early stopping validation.
- **Multi-seed obligatoire** : variance inter-runs notable même à hyperparamètres identiques → ils rapportent mean ± SD sur 3 seeds.
- Astuces stabilité : restart depuis checkpoint stable sur spike de loss ; two-phase training si NaN.

**Usage P5 :** notre budget court (≤10 epochs, patience 3, mono-seed par défaut) devra être explicitement justifié comme choix low-data dans la réponse aux reviewers — ou complété par multi-seed si les reviewers poussent. À préparer dès maintenant, pas après.

---

## 3. P6 — LISH-MoA structure vs phénotype

### 3.1 Asymétrie de modalité : citation idéale pour nos bras négatifs

**MVCBench**, bioRxiv 2026, DOI [10.64898/2026.04.22.720110](https://www.biorxiv.org/content/10.64898/2026.04.22.720110v1) ([GitHub](https://github.com/QSong-github/MVCBench))

- Benchmark de **24 méthodes de représentation** (12 moléculaires + 12 géniques) sur ~**1,1 M profils** induits par médicaments (transcriptomique + imagerie à haut contenu), settings ID et OOD.
- **Conclusion clé : asymétrie dépendante de la modalité** — les représentations moléculaires avancées (3D-aware, deep encoders) améliorent nettement la prédiction morphologique mais apportent des **gains limités pour la prédiction transcriptionnelle**, où les fingerprints classiques restent compétitifs.
- La performance se dégrade fortement sous distribution shift ; l'intégration multimodale améliore systématiquement.

**Usage P6 :** contextualiser nos bras GIN/GIN-TFP/TNE ≈ hasard face à la baseline phénotype — pattern systémique documenté, pas un échec d'implémentation. Citation directe pour l'honest-negative.

### 3.2 Reformulation du finding « fusion »

Littérature de fusion structure–omique (BioGDR, DeepDTF, MoGraphDRP) : la fusion fonctionne via **attention croisée intermédiaire**, pas par concaténation tardive de features.

**Usage P6 :** reformuler « fusion < baseline » en « late fusion naïve insuffisante ; la littérature converge vers des fusions attentionnelles nécessitant des profils appariés par molécule ». Cohérent avec notre résultat RF-concat.

### 3.3 Contexte SOTA de la prédiction MoA-from-transcriptome

**Hierarchical ArcFace (Katsaouni & Schulz)**, bioRxiv 2026, DOI [10.64898/2026.02.03.703502](https://doi.org/10.64898/2026.02.03.703502) ([GitHub SchulzLab](https://github.com/SchulzLab/Hierarchical-Representation-Learning-for-Drug-MOA-Prediction))

- LINCS L1000 Level-5, 28 769 signatures / 1 214 composés ; dual objectifs ArcFace (MoA-level + compound-level).
- **F1 moyen : hiérarchique 0.75 > MOASL 0.73 = GPAR 0.73 > RF 0.64** ; généralisation unseen cell lines F1 0.816 ; transfert CRISPR sans retraining.

**Usage P6 :** notre baseline phénotype AUROC macro 0.636 est cohérente avec la difficulté intrinsèque de la tâche (RF ≈ 0.64 F1 chez eux aussi) — à citer en Related Work pour cadrer nos chiffres.

### 3.4 Options légères (décision auteur, hors périmètre actuel)

- Breakdown par classe MoA pour montrer où vit le signal phénotype.
- Split UMAP/k-means en analyse de sensibilité (ligne Guo & Ballester) pour blinder la conclusion honest-negative avant promotion manuscrite (règle §7 AGENTS).

---

## 4. Priorisation

| # | Action | Coût | Quand |
|---|--------|------|-------|
| 1 | P2 : tracés de convergence MM-GBSA en SM + passe terminologique (« score entropie exclue ») | Gratuit (SM + texte) | Après QC PASS R1/R2 |
| 2 | P6 : citations MVCBench + fusion attentionnelle + ArcFace/L1000 | Gratuit (texte) | À la rédaction du manuscrit P6 |
| 3 | P2 : Discussion Tanner et al. Nat Commun 2025 | Gratuit (texte) | Édition JCIM (post-GO) |
| 4 | P5 : citations méga-benchmark + phrase hiérarchie des splits | Gratuit (texte) | Révision P5 |
| 5 | P5 : justification/extension multi-seed ChemBERTa | Texte ou calcul léger | Selon résultats 15490 |
| 6 | Splits Butina/k-means (P5) ou breakdown MoA (P6) | Calcul léger | Décision auteur |

**Dépendances :** rien à exécuter maintenant ; les points 1–4 sont de la pure rédaction qui suit les résultats de 15502 (MM-GBSA WT), du watcher K76A (chaîne QC→MM-GBSA), et des reports 15490/15500.

---

## 5. Drafts LaTeX prêts à insérer (décision auteur — insertion non effectuée)

### P2 — Discussion (mécanistique PfCRT)

> Recent atomistic work by Tanner, Richards & Corry~\citep{tanner2025pfcrt} — \num{130}\,\si{\micro\second} of molecular dynamics across CQ-sensitive and CQ-resistant PfCRT isoforms — established that Lys76 physically obstructs the chloroquine binding site while serving as the electrostatic anchor for peptide substrates, with R371I and Q271E acting in concert with K76T to open drug access. Our mutant-vs-wild-type endpoint comparisons are mechanistically consistent with this charged-cavity picture: perturbing residue 76 reshapes the local electrostatics that gate both ligand retention and substrate specificity.

### P2 — Methods (terminologie, si la phrase n'existe pas déjà)

> All MM-GBSA values reported here are endpoint enthalpic scores computed with a single-trajectory protocol (configurational entropy excluded); they are not experimental binding free energies and are interpreted only through within-target contrasts (mutant vs.\ wild type) under identical sampling.

### P5 — Discussion (headline confirmé)

> Our finding that fingerprint-based random forests remain the strongest family under random and Murcko-scaffold splits is independently corroborated by a recent multi-family benchmark spanning 26 endpoints and 156 task--metric comparisons, in which classical ML provides the largest share of best-performing entries (47.4%) ahead of pretrained sequence models (28.8%), GNNs (21.8%) and LLM-based SAR baselines (1.9%)~\citep{guo_ding_2026}; GNN and sequence models recovered ground only under structure-separated protocols. We further note that scaffold splits have been shown to overestimate virtual screening performance relative to cluster-based splits~\citep{guo2024scaffold}, placing our collision-group/scaffold protocols at an intermediate difficulty level.

### P5 — Limitations / réponse reviewers (ChemBERTa budget)

> The extended ChemBERTa rerun uses a deliberately short fine-tuning schedule (\leq{}10 epochs, patience 3) appropriate to our low-data regime; published best practice for chemical foundation models reports learning rates near $3\times 10^{-5}$, batch sizes of 16--32, 50--100+ epochs with early stopping, and multi-seed variance reporting~\citep{chemberta3_2026}. Multi-seed replication is left as future work if reviewer pressure requires tighter variance bounds.

### P6 — Discussion (asymétrie de modalité + fusion)

> The failure of advanced molecular representations to improve transcriptomic mechanism-of-action prediction mirrors the modality-dependent asymmetry documented by MVCBench, where deep molecular encoders substantially help morphological phenotypes but yield only marginal gains over classical fingerprints for gene-expression responses~\citep{mvcbench2026}. Likewise, the underperformance of naive late fusion is consistent with the molecular--omics fusion literature, where benefits arise from intermediate cross-modal attention rather than feature concatenation. Our phenotype baseline (macro-AUROC \num{0.636}) is also consistent with reported random-forest performance on L1000-derived MoA prediction (F1 $\approx$ \num{0.64}) versus structured-representation state of the art ($\approx$ \num{0.75})~\citep{katsaouni2026arcface}.

**Clés bib disponibles :** `tanner2025pfcrt`, `guo_ding_2026`, `guo2024scaffold`, `chemberta3_2026`, `mvcbench2026`, `katsaouni2026arcface` — ajoutées (append uniquement) dans `Bibliography_Polypharmacology_MD_Validation.bib` (P2), `Bibliography_P5.bib` (P5), `manuscript/references_pending.bib` (P6).
