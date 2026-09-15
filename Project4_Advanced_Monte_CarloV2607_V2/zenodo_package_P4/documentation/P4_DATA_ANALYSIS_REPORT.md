# P4 Data Analysis Report — active summary

**Scope:** Pareto-guided MCTS, multi-objective candidate generation, and QMC diagnostics.
**Updated:** 30 August 2026
**Status:** **Submitted to JCAMD (Springer Nature Editorial Manager) on 2026-08-30** — main `P4_Pareto_MCTS_JCAMD.tex` + SM `P4_Pareto_MCTS_JCAMD_SM.tex` + cover letter + Graphics package; awaiting acknowledgement.

> **Règle de workflow (permanente) : DAR avant manuscrit.** Toute modification de données, de résultats, de paramètres ou de protocole est tracée dans ce rapport AVANT toute édition du manuscrit ou du SM. Le manuscrit ne cite que des valeurs/statuts déjà reportés ici (source de vérité). En cas de divergence, le DAR fait foi et le manuscrit est corrigé ensuite. Cette règle s'applique à tous les projets (P1–P7) via leurs DAR respectifs et AGENTS.md.
**Long-form history:** `docs/archive/md_full_20260812/P4_DATA_ANALYSIS_REPORT.md`

## 1. Central question

Does Pareto-guided MCTS generate a more useful set of antimalarial candidates than scalar or unguided baselines when chemical accessibility, resistance-informed similarity, and polypharmacology-informed proxies are considered jointly?

The answer is bounded: MCTS did **not** win the scalar reward benchmark, but the Pareto analysis provides an auditable candidate-set geometry that a single scalar score cannot express.

## 2. Canonical scalar benchmark

**Canonical deposit:** `Project4_Advanced_Monte_CarloV2607/results/benchmark_molecules_opt_v12/` (job 12865; 20 independent seeds; medium fragment set; public-activity proximity included). The post-activity Pareto audit is under `Project4_Advanced_Monte_CarloV2607/results/pareto/`.

| Method | Mean reward ± SD |
|---|---:|
| Random | 0.6724 ± 0.0056 |
| MCTS + ScafVAE | 0.6649 ± 0.0068 |
| GA | 0.6453 ± 0.0124 |
| Greedy | 0.4278 ± 0.0000 |

MCTS versus Random: paired t₁₉=−4.97, p=0.000085. MCTS versus GA: t₁₉=6.95, p<0.0001. The scalar result is an honest negative: MCTS is not superior to broad Random exploration under this reward and budget.

## 3. Pareto result and ablation

The separately locked **pre-activity Pareto artifact** contains four non-dominated solutions with hypervolume **1.2366**. Its SYBA values were constant during the historical search and were recomputed post hoc before the front was re-derived; therefore the front is not presented as an informative historical four-way optimisation result.

Main ablation effects (2⁵ factorial, 160 runs):

- ScafVAE: **+0.148**
- Pareto front: **+0.108**
- Large vocabulary: **+0.079**

RRS and PNS terms are P2-informed computational proxies, not direct biological measurements or MD-RRS labels.

## 4. QMC boundary

Tier 1 SCF/PBE/def2-SVP infrastructure is functional and GPU-accelerated. Tier 2 PyQMC diagnostics identified a real DMC population-collapse problem at candidate scale. Candidate-level QMC energies are therefore **not publication-grade** without wavefunction optimisation, larger configurations, and τ→0 extrapolation. QMC claims were removed from the manuscript; the diagnostics remain in the archive.

## 5. Interpretation and limitations

- MCTS concentrates oracle calls on fewer unique molecules; Random explores more broadly in a relatively flat reward landscape.
- The Pareto front is useful for transparent trade-offs, not proof of superior scalar optimisation.
- SYBA post-hoc recomputation, PNS discreteness, and RRS-informed similarity proxies limit causal interpretation.
- The study is computational; experimental activity and resistance claims are not made.

## 6. Current manuscript status

The canonical P4 manuscript, Supporting Information, figures, and cover letter use the v12 scalar benchmark and explicitly separate it from the historical pre-activity Pareto front. Compilation and numerical consistency checks are complete.

## 7. Next actions

1. Keep v12-activity as the only scalar benchmark in active prose.
2. Retain the pre-activity Pareto front as a clearly labelled sensitivity/provenance artifact.
3. Do not reopen Tier 2 QMC for publication claims without a complete protocol and resource estimate.
4. Prepare the versioned data deposit and final author review.
