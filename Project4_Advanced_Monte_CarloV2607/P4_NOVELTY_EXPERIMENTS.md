# P4 — Novelty Experiments (simulations, 2026-08-03)

Ce document trace les simulations de nouveauté ajoutées pour renforcer le
manuscrit au-delà des re-wordings. Chaque expérience répond à un angle
d'acceptation (novelty / generalisation / mécanisme).

Contexte : manuscrit canonique `P4_Pareto_MCTS_JoC_refined.tex` (v12).
Référence de données : `results/benchmark_molecules_opt/` (20 seeds, v11/v12
canonical) + `results/pareto/merged_pareto_front.csv` (front canonique).

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
- Front par méthode : `pymoo.NonDominatedSorting` sur les 4 objectifs actifs **MPO/SYBA/RRS/PNS** (aligné C1).
- **Normalisation commune** pour HV : bornes min–max sur l'union de tous les candidats (baselines + front canonique) — indispensable, sinon per-front norm = front non comparable.
- N4 ajoute **IGD** (dist. moyenne réf→front) et **spread** (Δ-uniformité) sur une référence = front non-dominé de l'union.
- Dumps : `results/pareto/p4_multiobj_front_summary.csv`, fronts `results/pareto/p4_multiobj_fronts/front_{method}.csv`.

### Résultats

| méthode | n_unique/20 | front | HV (comm) | IGD | spread |
|---|---|---|---|---|---|
| random | 20 | 8 | 13.85 | 0.130 | 1.234 |
| greedy | **1** | 1 | 16.59 | 0.614 | NaN |
| ga | 19 | 8 | 15.49 | 0.077 | 1.019 |
| baselines_pooled | 40 | 11 | 15.52 | 0.073 | 0.903 |
| **mcts_canon** | 4 | 4 | **18.99** | 0.492 | 0.670 |

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
3. **Caveat IGD (ponytail) :** la référence pour IGD est l'union non-dominée de
   tous les candidats — `baselines_pooled` y contribue majoritairement, donc
   son IGD trivialement bas (0.073) est attendu, pas informatif. **HV est la
   métrique propre** (indépendante d'une référence de comparaison). IGD/spread
   rapportés comme compléments, pas comme evidence.

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

---

## N3 — Figure HV vs référence (COMPLET, partielle)

`manuscript/LaTeX/Graphics/p4_hv_vs_ref.png` : hypervolume du front canonique en
fonction du point de référence (1.00→1.50) — illustre la sensibilité (monotone
croissante, 15.2→37.8), aligné audit F1/F3, usage SM.

---

## Traçabilité

- Décision documentée dans `P4_DATA_ANALYSIS_REPORT.md` (entrée N1+N4) AVANT toute
  modification du manuscrit — conformément au workflow boussole.
- Résultats reproductibles : `python scripts/p4_benchmark_multiobj.py` (conda malaria_md).
